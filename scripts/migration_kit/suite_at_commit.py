#!/usr/bin/env python3
"""SOP step B8a (plan G3.6 row 13 (a); supervisor:L844 and its refinement 740ba68a): a full run of an Aget's
declared suite on an EXACT commit, in a clean clone with its declared sibling folders, with the CI exclusions it finds
applied and disclosed, plus its own pre-push hook where one exists. Writes a record the push gate requires (push_batch.py
refuses unless suite_at_commit.json names the exact commit to be pushed with verdict PASS, or FAIL under a baseline-equal
ruling; it reads that file as found and does not verify what wrote it). Batch 8: the receiver's own gate caught the
regression that four supervisor checks missed; of the 10 unfinished Agets only one has such a gate, so this is the
default stand-in. It reads the receiver's Git state and clones it into a fresh run folder under the work root
~/.cache/aget-suite-at-commit/ (one per run, never cleared, never inside a repository; R1 clause 5), where the
declared suite and the receiver's pre-push hook, placed as a regular file in the clone, run; a hook reached through
a symbolic link that leads outside the receiver is not run, and the record reads INCONCLUSIVE (R1 clause 6(b)). Run
folders are kept; removing old ones is the operator's. It writes its record under --evidence.
Keep --evidence outside the receiver's repository (operator rule, not enforced by the tool).

Never PASS after the suite or the hook changed the clone (review finding F-6): the tool reads the clone's HEAD and
`git status --porcelain` before the suite, after it and after the hook, and with each status line the content of the
paths it names (a file's bytes and permission bits, a link's target, and for a folder git lists as one entry the
same of the files under it). The command-line tool also takes, at each of the three readings, a snapshot of the
clone's working tree: every file, link and folder that git does not ignore, tracked or not, with its kind, its
permission bits and, for a file, its bytes (snapshot()). A moved HEAD, or outside the paths --allow-path names a new
status line, a line that is gone (second review, 2026-10-02: a listed untracked file the suite deleted), a line that
stays the same while that content differs (same review: a file of a sibling folder copied inside the clone was
listed `??` before and after the suite that rewrote it), or a path whose snapshot differs although no status line
shows it (same review: a tracked file's read and write bits, a folder's permission bits), makes the verdict
INCONCLUSIVE, and the record keeps the lines read; among the blocking and allowed lines a line whose content differs
is kept with ` (content changed)` after it, a line that is gone with ` (no longer listed)`, and a snapshot
difference as `changed PATH`, `added PATH` or `removed PATH`. Not read as a change:
a file git ignored before the suite ran (a change to the ignore rules themselves, in `.gitignore`,
`.git/info/exclude` or the `core.excludesFile` setting, is read), an untracked file under a `__pycache__` or
`.pytest_cache` folder, a change made and undone between two readings, a write by a process that outlives the suite
or the hook and is not in its process group, a folder added or removed with no file that git lists in it (an empty
folder), times and owners, any other change inside a `.git` folder, a push to an explicit URL or path,
and anything written outside the clone and its copied siblings' remotes. Nor a ref moved while HEAD and the status lines stay
as they were (a stash, a new branch). This is the command-line tool's rule: run() called without `allow_paths` (the
reference run below) records the readings and judges only HEAD.

Also the reference run for V3.6's blind-spot report (row 13 (b)): `run()` is imported by rehearse_batch2.py.

Usage: python3 scripts/migration_kit/suite_at_commit.py --packet P --aget A --evidence batchN/evidence [--sha SHA]
           [--allow-path PATH ...]
Exit 0 PASS, 1 FAIL, 3 INCONCLUSIVE.
"""
import argparse
import fnmatch
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import release_target as R  # noqa: E402  (the framework root a work root must not overlap)
import result_binding as RBND  # noqa: E402  (R2-T16 (c): the B8a record is bound to its run)
import place_file as PF  # noqa: E402  (E2i15: the one no-follow working-tree reader)
# Under ~/.cache, as the framework Aget's own gate measured (2026-09-23): not the system temp root (its sandbox
# test treats that specially) and not ~/tmp (its allowlist test aims a trap there).
WORK = Path.home() / ".cache" / "aget-suite-at-commit"
NO_PUSH_URL = "no-push://disabled-by-suite-at-commit"
DONE = re.compile(r"\b\d+ (passed|failed)\b")
DEFAULT_SUITE = f"{sys.executable} -m pytest -q -rfE -p no:cacheprovider"   # as V3.6's S0 (rehearse_repair.suite)
TREE_KEPT = 40   # status lines the record keeps per reading (each reading also records its full count)
TREE_WHY = 5     # status lines a refusal's reason names
CACHE_DIRS = ("__pycache__", ".pytest_cache")   # caches: an untracked file under one is not read as a change


def git(d, *a, env=None):
    """Run git in the given folder and return the completed process. It reads the live member as well as the clone,
    so it takes no optional lock and fetches no missing object (copy_isolation.READ_FLAGS; B166 finding 2)."""
    return subprocess.run(["git", *CI.READ_FLAGS, "-C", str(d), *a], capture_output=True, text=True, env=env)


def kit_git_env(d):
    """R1 ENV for a git act this tool makes in a copy: no transport, no copied hook (R1-T15), bounded by d's parent."""
    return CI.contained_env(Path(d).parent, d, CI.NO_TRANSPORT)


def ci_exclusions(location, suite_cmd, rev=None):
    """The Aget's CI exclusions: literal `--deselect ID` (only an ID containing `::`) / `--ignore PATH` in its root
    workflows, and the non-blank lines not starting with `#` of each existing file whose path appears in those workflows
    as `tests/...known....txt` or is the non-space text after the first `--deselect-file` followed by whitespace in the
    declared suite (a deselect file named any other way, `--deselect-file=PATH` included, is not read). Returns (extra_args, excluded_ids, sources).
    `location` is the CLEAN CLONE at the commit under test, so the files read are that commit's (review minor); with
    `rev` (R2-T13, S-181: the packet's head, the commit before the migration) they are read at that revision in the
    clone instead, so a migration commit cannot add an exclusion for its own new failure."""
    loc = Path(location)

    def read(path):
        # B191 finding 1: an exclusion source is a regular file or nothing; a link (in the tree or committed, mode
        # 120000), a folder or an unreadable entry raises InspectionFailed (B8a: INCONCLUSIVE), never text or absence
        if rev is None:      # E2i15 (FWK-OVSR6's E2i14 pre-read 2, agy P6): no link followed anywhere on the path
            try:
                kind, b = PF.read_entry(loc, path)
            except (PF.Refused, OSError, ValueError) as e:
                raise CI.InspectionFailed(f"{path} in the working tree cannot be read without a link: {e}") from None
            if kind not in ("file", "absent"):
                raise CI.InspectionFailed(f"{path} in the working tree is not a regular file")
            return b.decode(errors="replace") if kind == "file" else None
        b = CI.git_blob_at(loc, rev, path)
        return None if b is None else b.decode(errors="replace")
    if rev is None:
        flows = [p.relative_to(loc).as_posix() for p in sorted((loc / ".github" / "workflows").glob("*.y*ml"))]
    else:
        q = git(loc, "ls-tree", "-z", "--name-only", f"{rev}:.github/workflows")
        flows = sorted(f".github/workflows/{n}" for n in (q.stdout.split("\0") if q.returncode == 0 else [])
                       if n and fnmatch.fnmatch(n, "*.y*ml"))
    text = "\n".join(read(f) or "" for f in flows)
    extra, ids, sources = [], [], []
    for flag, val in re.findall(r"(--deselect|--ignore)[ =]([^\s$\"'|]+)", text):
        if "::" in val or flag == "--ignore":
            extra += [flag, val]
            ids.append(val)
            sources.append(f"workflow {flag}")
    files = set(re.findall(r"(tests/[\w./-]*known[\w./-]*\.txt)", text))
    m = re.search(r"--deselect-file\s+(\S+)", suite_cmd or "")
    declared = {m.group(1)} if m else set()
    for f in sorted(files | declared):
        body = read(f)
        if body is not None:
            listed = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.startswith("#")]
            ids += listed
            sources.append(f"{f} ({len(listed)})")
            if f not in declared:
                extra += [a for i in listed for a in ("--deselect", i)]
    return extra, sorted(set(ids)), sources


def clean_clone(location, aget, sha, siblings, work):
    """Clone the Aget at the exact commit with pushing disabled and its sibling folders copied; return (clone, sibling refs), or (None, reason).
    R1 clause 5 (E2g): `work` is a work root W, refused inside any git repository or overlapping the member, a sibling
    source or the framework root; the clone goes into a fresh run folder `mkdtemp(dir=W)` (copy_isolation.run_folder),
    so no earlier clone is removed and two runs never share a folder."""
    why = CI.name_refusal(aget)                        # B162 finding 1: a name, never a path
    if why:
        return None, why
    sources = CI.sibling_sources(location, siblings)
    try:
        run = CI.run_folder(work, [location, *sources, R.framework_root()], prefix=f"{aget}-")
    except CI.ContainmentRefused as e:
        return None, str(e)
    base = run / f"{aget}.root"
    why = CI.run_child_refusal(run, base, "the clone folder") or CI.place_refusal(
        base, location, "the clone folder", sources=sources)
    if why:
        return None, why
    dest = base / aget
    base.mkdir()
    c = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--no-checkout", str(location), str(dest)], capture_output=True,
                       text=True)
    if c.returncode:
        return None, f"could not clone {sha[:8]}"
    # The clone is made with --no-checkout, so nothing is checked out (and no checkout hook can run) before this test:
    # the clone must be its own working tree with its own git folder, and each of its remotes gets the push URL that
    # cannot resolve, read back from git. Only then is the commit checked out.
    why = CI.isolate(dest, "no-push", url=NO_PUSH_URL, member=True)
    if why:
        return None, f"the clone is not usable, nothing was run in it: {why}"
    try:
        kenv = kit_git_env(dest)
    except CI.ContainmentRefused as e:                  # B160 finding 1: checked under the environment it gives
        return None, f"the clone is not usable, nothing was run in it: {e}"
    if (git(dest, "checkout", "-q", sha, env=kenv).returncode
            or git(dest, "rev-parse", "HEAD").stdout.strip() != sha):
        return None, f"could not clone {sha[:8]}"
    # R1 LINKS: the checkout made the commit's symbolic links; none may lead outside this run's folder. The push
    # routes are read again too (B154 finding 1: a checkout can change branch-dependent configuration).
    why = CI.checked_out_refusal(dest, base, NO_PUSH_URL)
    if why:
        return None, f"the clone is not usable, nothing was run in it: {why}"
    # The clone's origin is the Aget's REAL repository. A suite whose own wind-down commits and pushes (one receiver's
    # aget_session_protocol.py, 2026-09-29 17:48) then pushes from here into it. isolate() above gave every remote of
    # the clone a push URL that cannot resolve, so a push to a named remote fails inside the clone (the principal's
    # typed line 00:56:15Z); a push to an explicit URL or path stays open. Each copied sibling gets the same below.
    # (tuple: dest, sibling refs; or None, reason)
    refs = []
    for rel in siblings:
        src, target = (Path(location) / rel).resolve(), (dest / rel).resolve()
        if not src.is_dir() or base.resolve() not in target.parents:
            return None, f"sibling {rel!r} unavailable"
        shutil.copytree(src, target, symlinks=True)
        # A copied sibling brings its git metadata and its remotes. Before the checkout and clean below, and before
        # the suite and the hook, it must be its own working tree with its own git folder, and its remotes get the
        # push URL that cannot resolve. A sibling with no .git entry is a plain folder and is left as copied.
        why = CI.isolate(target, "no-push", url=NO_PUSH_URL, run=base)
        if why:
            return None, f"sibling {rel!r}: its copy is not usable, nothing was run: {why}"
        try:
            state = sibling_like_ci(target)
        except CI.ContainmentRefused as e:              # B160 finding 1
            return None, f"sibling {rel!r}: its copy is not usable, nothing was run: {e}"
        why = CI.checked_out_refusal(target, base, NO_PUSH_URL)   # LINKS and push routes again (B154 finding 1)
        if why:
            return None, f"sibling {rel!r}: its copy is not usable, nothing was run: {why}"
        refs.append(f"{rel}: {state}")
    return dest, refs


def sibling_like_ci(clone):
    """The framework Aget's review (2026-09-29): check the copied sibling out at its remote default branch, as CI
    does (no pinned ref), not the live checkout's branch or its uncommitted changes. Mirrors its
    pre_push_suite_gate_ext.checkout_siblings_like_ci: origin/HEAD, falling back to origin/main. A sibling with no
    .git entry, or for which neither checkout succeeds, is left as copied from the live folder."""
    if not (clone / ".git").exists():
        return "not a git repository: copied as is"
    for ref in ("origin/HEAD", "origin/main"):
        if git(clone, "checkout", "-q", "--force", "--detach", ref, env=kit_git_env(clone)).returncode == 0:
            git(clone, "clean", "-fdq", env=kit_git_env(clone))
            return f"{ref} {git(clone, 'rev-parse', '--short', 'HEAD').stdout.strip()}"
    return "left as copied (no origin/HEAD or origin/main)"


def suite_env(dest):
    """The framework Aget's review (fullguard M3): tests that read CLAUDE_PROJECT_DIR must see the clone, never the
    caller's live folder; the push-window guard's AGET_TWG_* settings are the caller's and are dropped. Variables whose
    names end in API_KEY are dropped, to keep a suite from making paid calls with them; no other token or secret is
    removed (carriage row 70; the tool does it, so no `env -u` prefix is needed on the command line)."""
    # R1 ENV (R1-T16): git bounded by the folder holding the clone, no operator configuration, CLAUDE_PROJECT_DIR the
    # clone, no copied hook in the suite's own git acts; transports as they are (the suite's local tests run here)
    env = CI.contained_env(Path(dest).parent, dest, check=False)   # run() checks it immediately before use
    return {k: v for k, v in env.items() if not k.startswith("AGET_TWG_") and not k.endswith("API_KEY")}


class Bounded:
    """The result of run_bounded, shaped like subprocess.CompletedProcess."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def run_bounded(cmd, cwd, timeout, env, input=None):
    """Run cmd in its OWN process group and kill the whole group afterwards, on timeout or not. A bare
    subprocess.run timeout kills only the direct child: on 2026-09-29 (17:51) one receiver's wind-down re-ran its suite
    from inside the suite and left orphaned `pytest -q` processes that nothing could reach. Raises TimeoutExpired."""
    # Files, not pipes: a background child inheriting a pipe would hold the wait open until the timeout. Wait for the
    # MAIN process, kill the group (one SIGKILL to that group, a refused kill being ignored; a descendant
    # that started its own session or process group is not reached), then read.
    import tempfile
    with tempfile.TemporaryFile("w+") as fo, tempfile.TemporaryFile("w+") as fe:
        p = subprocess.Popen(cmd, cwd=cwd, env=env, text=True, start_new_session=True, stdout=fo, stderr=fe,
                             stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL)
        timed_out = False
        try:                      # B153 finding 2: from the group's start, the stdin write and the wait included
            if input is not None:
                p.stdin.write(input)
                p.stdin.close()
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:                  # any other exception, an interrupt or a broken pipe included, still kills the group
            kill_group(p.pid)
            p.wait()
        fo.seek(0)
        fe.seek(0)
        out, err = fo.read(), fe.read()
    if timed_out:
        raise subprocess.TimeoutExpired(cmd, timeout, output=out, stderr=err)
    return Bounded(p.returncode, out, err)


def kill_group(pgid):
    """Kill the process group, ignoring one that is already gone or not ours to kill."""
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def parse_porcelain(text):
    """Entries of `git status --porcelain -z` output as (line, paths): line is `XY path`, or `XY path (from orig)` for
    a rename or copy, whose paths are both names. An untracked entry under a CACHE_DIRS folder is left out."""
    out, parts, i = [], text.split("\0"), 0
    while i < len(parts):
        entry, i = parts[i], i + 1
        if len(entry) < 4:
            continue
        xy, paths = entry[:2], [entry[3:]]
        if ("R" in xy or "C" in xy) and i < len(parts):
            paths.append(parts[i])
            i += 1
        if xy == "??" and any(d in paths[0].split("/")[:-1] for d in CACHE_DIRS):
            continue
        out.append((f"{xy} {paths[0]}" + (f" (from {paths[1]})" if len(paths) == 2 else ""), paths))
    return out


def content_print(path):
    """What a listed path holds now, as one short text: a link's target, the SHA-256 of a file's bytes with its
    permission bits, for a folder the SHA-256 over the names and such texts of the files and links under it (folders
    named `.git` or as in CACHE_DIRS left out), `absent`, or `unreadable`."""
    p = Path(path)

    def refuse(e):
        raise e
    try:
        if p.is_symlink():
            return "link:" + os.readlink(p)
        if p.is_file():
            return f"{hashlib.sha256(p.read_bytes()).hexdigest()}:{p.stat().st_mode & 0o7777:o}"
        if p.is_dir():
            h = hashlib.sha256()
            for folder, dirs, files in os.walk(p, onerror=refuse):   # C2a10 (pre-read 7): an unlistable folder
                dirs[:] = sorted(d for d in dirs if d != ".git" and d not in CACHE_DIRS)
                for d in sorted(dirs):        # C2a11 (LOW): a link to a folder is an entry, not nothing
                    if (Path(folder) / d).is_symlink():
                        h.update(f"{(Path(folder) / d).relative_to(p)}\0link:{os.readlink(Path(folder) / d)}\n".encode())
                for name in sorted(files):
                    f = Path(folder) / name
                    c = content_print(f)
                    if CI.non_reading(c):    # C2a10 (E2i16 pre-read 1): never fold an error text into a digest
                        return f"unreadable: {f.relative_to(p)}"
                    h.update(f"{f.relative_to(p)}\0{c}\n".encode())
            return "folder:" + h.hexdigest()
        if os.path.lexists(p):     # C2a10 (FWK-OVSR6's C2a10 pre-read 7): a FIFO or device is there, not absent
            return f"not a regular file (mode {stat.S_IFMT(os.lstat(p).st_mode):o})"
        return "absent"
    except OSError:
        return "unreadable"


def tree_changes(dest, full=False):
    """A Reading: the entries of `git status --porcelain -z --untracked-files=all` in the clone as
    (line, paths, content), or None when git fails: parse_porcelain's entries, each with content_print() of the paths
    it names, read now. With `full`, the Reading's `.snapshot` is snapshot(dest), taken after the status.
    Git does not list the files it ignores, so a write to an ignored path is not seen."""
    p = git(dest, "status", "--porcelain", "-z", "--untracked-files=all")
    if p.returncode:
        return None
    reading = Reading((line, paths, "|".join(content_print(Path(dest) / x) for x in paths))
                      for line, paths in parse_porcelain(p.stdout))
    if full:
        reading.snapshot = snapshot(dest)
    return reading


def allowed(path, allow_paths):
    """True when path equals an entry, or starts with an entry ending in "/" (plain text: no glob, no normalising)."""
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allow_paths)


class Reading(list):
    """One reading of the clone: the status entries, with the working tree's snapshot (or None) as `.snapshot`."""
    snapshot = None


def _walk_snapshot(dest, ignored, out, onerror):
    """snapshot()'s walk, kept lazy so the in-place pruning of `dirs` applies (C2a11: a list() of the walk lost it)."""
    for folder, dirs, files in os.walk(dest, onerror=onerror):
        rel = Path(folder).relative_to(dest).as_posix()
        prefix = "" if rel == "." else rel + "/"
        keep = []
        for d in sorted(dirs):
            if (Path(folder) / d).is_symlink():
                files.append(d)
            elif d != ".git" and d not in CACHE_DIRS and prefix + d + "/" not in ignored:
                keep.append(d)
        dirs[:] = keep
        try:
            out[prefix or "./"] = f"folder:{Path(folder).stat().st_mode & 0o7777:o}"
        except OSError:
            out[prefix or "./"] = "unreadable"
        for name in sorted(files):
            if prefix + name not in ignored and name != ".git":
                out[prefix + name] = content_print(Path(folder) / name)


def snapshot(dest):
    """Every path of the clone's working tree that git does not ignore, as {path: text}: a file's SHA-256 with its
    permission bits, a link's target, a folder's permission bits (folder paths end in `/`; the clone's own folder is
    `./`). Left out: `.git` folders, folders named as in CACHE_DIRS, and the files and folders
    `git ls-files --others --ignored --exclude-standard --directory` lists. Two entries stand for the ignore rules
    kept outside the working tree: `.git/info/exclude` (its bytes) and the `core.excludesFile` setting (its value);
    a `.gitignore` file is in the tree and is read like any other file. None when that git command fails."""
    dest = Path(dest)
    p = git(dest, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--directory")
    if p.returncode:
        return None
    ignored = {x for x in p.stdout.split("\0") if x}
    out = {}

    def unlistable(e):                 # C2a11 (FWK-OVSR6's C2a10r pre-read): a folder that cannot be listed is not empty
        raise e
    try:
        _walk_snapshot(dest, ignored, out, unlistable)
    except OSError:
        return None
    # What git ignores is decided by rules a suite can change. The rules kept outside the working tree are part of
    # the snapshot, so a suite that adds an ignore rule and then writes files the rule hides is read as a change.
    out[".git/info/exclude"] = content_print(dest / ".git" / "info" / "exclude")
    out["(git config) core.excludesFile"] = git(dest, "config", "--get", "core.excludesFile").stdout.strip() or "unset"
    return out


def snapshot_changes(now, before, named):
    """The paths whose snapshot text differs between two snapshots, as (line, [path]) with the line `changed PATH`,
    `added PATH` or `removed PATH`. Left out: a path in `named` or under a folder path in it (the status lines
    already report those), and a folder that is in only one of the two snapshots (its files report it)."""
    out = []
    for path in sorted(set(now) | set(before)):
        if now.get(path) == before.get(path):
            continue
        if path in named or any(n.endswith("/") and path.startswith(n) for n in named):
            continue
        if path.endswith("/") and (path not in now or path not in before):
            continue
        word = "added" if path not in before else "removed" if path not in now else "changed"
        out.append((f"{word} {path}", [path]))
    return out


def split_changes(now, before, allow_paths):
    """The entries of `now` that `before` does not hold with the same line and the same content, and the entries of
    `before` whose line `now` no longer holds, as (blocking lines, allowed lines): an entry is allowed when every
    path it names is. An entry whose line is in both readings and whose content differs is given as its line followed
    by ` (content changed)`; one whose line is gone, as its line followed by ` (no longer listed)`. Entries are
    (line, paths) or (line, paths, content); without the content only the lines are compared."""
    content = lambda e: e[2] if len(e) > 2 else None
    old, old_lines, now_lines = {(e[0], content(e)) for e in before}, {e[0] for e in before}, {e[0] for e in now}
    new = [(e[0] + (" (content changed)" if e[0] in old_lines else ""), e[1])
           for e in now if (e[0], content(e)) not in old]
    new += [(e[0] + " (no longer listed)", e[1]) for e in before if e[0] not in now_lines]
    snap_now, snap_before = getattr(now, "snapshot", None), getattr(before, "snapshot", None)
    if snap_now is not None and snap_before is not None:
        new += snapshot_changes(snap_now, snap_before, {p for _, paths in new for p in paths})
    ok = [line for line, paths in new if all(allowed(p, allow_paths) for p in paths)]
    return [line for line, _ in new if line not in ok], ok


def kept(entries):
    """A reading as the record keeps it: its full count and its first TREE_KEPT lines; None for an unreadable one."""
    return None if entries is None else {"count": len(entries), "lines": [e[0] for e in entries[:TREE_KEPT]]}


def tree_refusal(rec, who, now, before, allow_paths):
    """Judge one reading against the one before it: add its allowed lines to rec["tree_allowed"] and return None, or
    put its blocking lines in rec["tree_unallowed"] and return the reason. An unreadable reading is a reason too."""
    if now is None or before is None:
        return f"`git status --porcelain` could not be read in the clone, so what {who} changed there is unknown"
    if getattr(now, "snapshot", {}) is None or getattr(before, "snapshot", {}) is None:
        return f"the clone's working tree could not be listed, so what {who} changed there is unknown"
    # C2a10 (FWK-OVSR6's E2i16 pre-read 1, reproduced): a path whose content could not be read, before or after,
    # equals nothing: unreadable twice is not "unchanged", and unreadable then readable is not an allowed change
    unread = sorted({e[1][0] if e[1] else e[0] for r in (now, before) for e in r if len(e) > 2 and CI.non_reading(e[2])}
                    | {k for r in (now, before) for k, v in (getattr(r, "snapshot", None) or {}).items()
                       if CI.non_reading(v)})
    if unread:
        return f"what {who} changed in the clone is unknown: {len(unread)} path(s) could not be read, e.g. {unread[0]}"
    blocking, ok = split_changes(now, before, allow_paths)
    rec["tree_allowed"] = (rec["tree_allowed"] + [x for x in ok if x not in rec["tree_allowed"]])[:TREE_KEPT]
    if not blocking:
        return None
    rec["tree_unallowed"] = blocking[:TREE_KEPT]
    return (f"{who} left {len(blocking)} change(s) in the clone outside --allow-path "
            f"(first {min(len(blocking), TREE_WHY)}: {blocking[:TREE_WHY]})")


def run(location, aget, sha, suite_cmd=None, siblings=(), work=WORK, timeout=2400, hook=True, allow_paths=None,
        exclusions_at=None):
    """The record: verdict PASS only when the suite, run with the exclusions ci_exclusions found, completed with
    no failure, the hook (if run) exited 0, neither moved the clone's HEAD and, when `allow_paths` is a list (main
    always passes one), neither left outside it a new `git status --porcelain` line, removed one, changed the content
    or file mode of a path a line already named, or changed a path of the working-tree snapshot. With the default None the status
    readings are recorded but not judged: rehearse_batch2.py's reference run, which asks only which tests fail."""
    judged = allow_paths is not None
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    rec = {"schema": "v335_suite_at_commit/1", "aget": aget, "sha": sha, "started": started,
           "suite_cmd": suite_cmd or DEFAULT_SUITE, "sibling_reads": list(siblings), "failures": [], "hook": None,
           "tree_check": "enforced" if judged else "recorded only", "allow_paths": list(allow_paths or ()),
           "tree_lines_kept": TREE_KEPT, "tree_allowed": []}
    dest, refs = clean_clone(location, aget, sha, siblings, work)
    if dest is None:
        return {**rec, "verdict": "INCONCLUSIVE", "why": refs}
    rec["sibling_refs"] = refs
    if exclusions_at is not None:                       # R2-T13: the exclusions in force before the migration
        if git(dest, "cat-file", "-e", f"{exclusions_at}^{{commit}}").returncode:
            return {**rec, "verdict": "INCONCLUSIVE",
                    "why": f"the exclusions' revision {str(exclusions_at)[:12]} is not in the clone"}
        rec["exclusions_at"] = exclusions_at
        m = re.search(r"--deselect-file\s+(\S+)", suite_cmd or "")
        if m:                                          # pytest reads the declared file from the tested commit itself
            try:                                       # B191 finding 1: regular-file bytes or absence, at both
                at = [CI.git_blob_at(dest, c, m.group(1)) for c in (exclusions_at, sha)]
            except CI.InspectionFailed as e:
                return {**rec, "verdict": "INCONCLUSIVE", "why": f"the declared deselect file: {e}"}
            if at[0] != at[1]:
                return {**rec, "verdict": "INCONCLUSIVE",
                        "why": f"the declared deselect file {m.group(1)} differs between the packet's head "
                               f"{str(exclusions_at)[:8]} and the tested commit {sha[:8]}; the migration changed what "
                               "the suite excludes"}
    try:
        extra, ids, sources = (ci_exclusions(dest, suite_cmd) if exclusions_at is None
                               else ci_exclusions(dest, suite_cmd, exclusions_at))
    except CI.InspectionFailed as e:                   # B191 finding 1: an exclusion source that is not a file
        return {**rec, "verdict": "INCONCLUSIVE", "why": f"the CI exclusions cannot be read: {e}"}
    rec.update(excluded=ids, exclusion_sources=sources)
    cmd = shlex.split(rec["suite_cmd"]) + extra
    tree0 = tree_changes(dest, judged)   # normally empty; a sibling copied inside the clone shows here
    try:
        senv = suite_env(dest)
        why = CI.env_route_refusal(Path(os.path.abspath(dest)), senv, Path(os.path.abspath(dest)).parent)
        if why:
            raise CI.ContainmentRefused(f"under the contained environment: {why}")
    except CI.ContainmentRefused as e:                  # B160 finding 1: the suite does not run
        return {**rec, "verdict": "INCONCLUSIVE", "why": f"the suite was not run: {e}"}
    # B185 finding 1 (C2a7): the suite's failing ids come from a fresh kit report in the clone's run folder (outside
    # the clone); the pre-push hook below runs under the plain environment and writes no report
    report = Path(dest).parent.parent / "b8a_pytest_report.jsonl"
    try:
        token = RBND.new_report(report)
    except OSError as e:
        return {**rec, "verdict": "INCONCLUSIVE", "why": f"the suite was not run: its report cannot be made ({e})"}
    renv = RBND.report_env(senv, report, token)
    rec["result_source"] = {"report": str(report)}
    ign = lambda: CI.ignore_state(dest, also=[("suite environment", renv)])   # R1 clause 8 (IGN, R1-T9): the env the
    ign0 = ign()                         # tree checks read git under and the suite's own, immediately before the suite
    try:
        p = run_bounded(cmd, dest, timeout, renv)
    except subprocess.TimeoutExpired:
        return {**rec, "verdict": "INCONCLUSIVE", "why": f"suite timed out after {timeout} s (process group killed)"}
    head_after = git(dest, "rev-parse", "HEAD").stdout.strip()
    if head_after != sha:
        # The suite committed inside the clone (a wind-down writer in the suite): the commit that passed is no
        # longer the commit that was tested, and the suite has side effects the push would not show.
        return {**rec, "verdict": "INCONCLUSIVE", "head_after": head_after,
                "why": f"the suite moved the clone's HEAD {sha[:8]} -> {head_after[:8]} (it commits during its run)"}
    out = p.stdout + p.stderr
    rec["summary"] = (DONE.search(out) and out[DONE.search(out).start():].splitlines()[0]) or out.strip()[-200:]
    rec["failures"], unknown, rec["failure_events"] = RBND.report_failures(report, token, out,   # B185 finding 1
                                                                           exit_code=p.returncode)   # C2a10, B192 #1
    rec["failures_complete"] = not unknown
    if unknown:
        rec["failures_unknown"] = unknown
    tree1 = tree_changes(dest, judged)
    rec.update(tree_before_suite=kept(tree0), tree_after_suite=kept(tree1))
    ign1 = ign()
    # F-6: an uncommitted write is the same side effect as a commit; the HEAD test above could not see it. IGN is
    # judged whether or not the tree is (the reference run's result counts too), and its reason names the element.
    why = "; ".join(x for x in (judged and tree_refusal(rec, "the suite", tree1, tree0, rec["allow_paths"]),
                                CI.ignore_refusal(ign0, ign1, "the suite")) if x)
    if why:
        return {**rec, "verdict": "INCONCLUSIVE", "why": why}
    if not DONE.search(out):
        return {**rec, "verdict": "INCONCLUSIVE", "why": "the suite did not report a completed result"}
    # R1 clause 6(b) (R1-T2 (d)): the hook that runs is a regular file in the clone, chosen by what the member's entry
    # is; a link leading outside the member is not run and the result is INCONCLUSIVE, never PASS without the hook
    hook_file, why = CI.materialize_hook(location, dest) if hook else (None, None)
    if why:
        return {**rec, "hook": {"present": True, "run": False, "why": why}, "verdict": "INCONCLUSIVE",
                "why": f"the pre-push hook: {why}"}
    if hook_file:
        remote = git(location, "rev-parse", "@{upstream}").stdout.strip() or "0" * 40
        branch = git(location, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "main"
        try:   # F3 (reason map class 12): the hook's timeout reads INCONCLUSIVE, as the suite's does, not a traceback
            h = run_bounded([str(hook_file), "origin", "local"], dest, timeout, senv,
                            input=f"refs/heads/{branch} {sha} refs/heads/{branch} {remote}\n")
        except subprocess.TimeoutExpired:
            return {**rec, "hook": {"present": True, "run": True, "exit": None}, "verdict": "INCONCLUSIVE",
                    "why": f"the pre-push hook timed out after {timeout} s (process group killed)"}
        rec["hook"] = {"present": True, "exit": h.returncode, "tail": (h.stdout + h.stderr)[-600:]}
        head2, tree2 = git(dest, "rev-parse", "HEAD").stdout.strip(), tree_changes(dest, judged)
        rec.update(head_after_hook=head2, tree_after_hook=kept(tree2))
        if head2 != sha:   # judged or not, as for the suite
            why = (f"the pre-push hook moved the clone's HEAD from {sha[:8]} to {head2[:8] or 'unreadable'} "
                   "(it commits when run)")
            return {**rec, "verdict": "INCONCLUSIVE", "why": why}
        ign2 = ign()                                     # IGN after the hook
        why = "; ".join(x for x in (judged and tree_refusal(rec, "the pre-push hook", tree2, tree1, rec["allow_paths"]),
                                    CI.ignore_refusal(ign1, ign2, "the pre-push hook")) if x)
        if why:
            return {**rec, "verdict": "INCONCLUSIVE", "why": why}
    else:
        rec["hook"] = {"present": False}
    ok = p.returncode == 0 and not rec["failures"] and (not rec["hook"]["present"] or rec["hook"]["exit"] == 0)
    if ok and rec["failures_complete"] is not True:   # C2a7 (FWK-OVSR5's C2a5 advisory (2)): PASS reads completeness
        return {**rec, "verdict": "INCONCLUSIVE",
                "why": f"the suite exited 0 but its result is not complete: {rec.get('failures_unknown')}"}
    rec["verdict"] = "PASS" if ok else "FAIL"
    rec["ended"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    return rec


STEP = "suite_at_commit"
NOT_FINISHED = {"state": "started, not finished", "verdict": "INCONCLUSIVE"}


def main(argv=None):
    """Command-line entry point: run an Aget's declared suite on an exact commit and write the record.
    R2-T16 (c), D-4: the record is a result bound to its run. Its first act, before argument parsing, is to record a run
    for `<evidence>/<aget>/suite_at_commit.json` and write the record there as not finished, so a later run for the
    same member that fails, even with a usage error, leaves no earlier PASS standing; the finished record carries the
    run id, and the push gate reads it only as the current run (result_binding.read_current). A path-shaped --aget is
    refused first, before anything is written."""
    argv = sys.argv[1:] if argv is None else list(argv)
    ev_arg, aget_arg = RBND.prescan(argv, "--evidence"), RBND.prescan(argv, "--aget")
    run_id = None
    if ev_arg is not None and aget_arg is not None:  # D2 (C2e pre-read 2): an empty value is a value (argparse takes `--x=`), never absent
        why = CI.name_refusal(aget_arg, "--aget")      # B162 finding 1: before the evidence folder is touched
        if why:
            print(f"REFUSED: {why}")
            return 2
        run_id, early = RBND.producer_start(STEP, Path(ev_arg) / aget_arg / "suite_at_commit.json", NOT_FINISHED)
        if early:
            print(early)
            return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--aget", required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--sha", help="the exact commit to be pushed (default: the Aget's HEAD)")
    ap.add_argument("--allow-path", action="append", default=[], metavar="PATH",
                    help="repeatable: a repository-relative path, or a folder prefix ending in /, that the member's "
                         "suite or hook is known to write; a change confined to these paths does not block PASS")
    a = ap.parse_args(argv)
    why = CI.name_refusal(a.aget, "--aget")            # B162 finding 1: before the evidence folder or any clone
    if why:
        print(f"REFUSED: {why}")
        return 2
    r = next(x for x in json.loads(a.packet.read_text())["receivers"] if x["aget"] == a.aget)
    sha = a.sha or git(r["location"], "rev-parse", "HEAD").stdout.strip()
    sha = git(r["location"], "rev-parse", sha).stdout.strip()
    if not r.get("head"):                               # R2-T13: the exclusions are read at the packet's head
        print(f"REFUSED: the packet names no head for {a.aget}; the exclusions in force before the migration are "
              "unknown")
        return 2
    rec = run(r["location"], a.aget, sha, r.get("suite_cmd"), r.get("sibling_reads") or [],
              allow_paths=a.allow_path, exclusions_at=r["head"])
    ev = a.evidence / a.aget
    ev.mkdir(parents=True, exist_ok=True)
    code = {"PASS": 0, "FAIL": 1}.get(rec["verdict"], 3)
    RBND.write_result(STEP, ev / "suite_at_commit.json", rec, run_id, code,   # R2-T16 (c): bound to this run
                      binding={"aget": a.aget, "subject": sha})
    said = " | ".join(x for x in (rec.get("summary"), rec.get("why")) if x)   # the reason is printed, summary or not
    print(f"{a.aget:34s} {rec['verdict']} at {sha[:8]}: {said}"
          f" | excluded {len(rec.get('excluded', []))} | hook {rec['hook']}"
          f" | allowed changes {len(rec['tree_allowed'])}")
    return code


if __name__ == "__main__":
    sys.exit(main())
