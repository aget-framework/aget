#!/usr/bin/env python3
"""What the kit requires of every copy or clone it makes of a member or of a sibling folder. One place, used by the
five tools that make one: rehearse_batch2.py and rehearse_repair.py (packet and repair rehearsal), rehearse_v37.py and
launch_batch.py --copy-root (session rehearsal), suite_at_commit.py (the suite at the exact commit) and
after_run_check.py (the confirmation run).

Why (independent review of the v3.36.0 candidate, 2026-10-02): a copy made with its git metadata is a separate folder
and can still act on the live repository. Git follows the copied settings: a `.git` that is a file or a link, a
`commondir` file, or a `core.worktree` setting make `git checkout`, `git clean`, `git commit` and `git remote remove`,
run in the copy, change the member's own files or repository; and a copied sibling keeps its remotes, so a test that
pushes from it reaches the real remote. The tests were first added to the session rehearsal alone; the packet
rehearsal, which runs before it, and the suite check's siblings were left without them.

The routine, in the order a tool applies it:
- place_refusal(): before anything is removed, copied or cloned, the environment must hold none of
  GIT_LOCATION_VARS (git obeys them in every command the tool then runs, the clone's first checkout included), and
  the folder to be cleared and filled must not be the live folder, hold it or lie inside it (the two tools that
  clone, not copy, accept a work folder inside the live tree);
- isolate(): after the copy or the clone and before any other git command in it (the two tools that clone do so
  with --no-checkout and check the commit out only afterwards), git
  run in it must name it as its working tree and its own `.git` folder as its git folder and common folder, and no
  entry under that `.git` folder may be a symbolic link that leads outside the copy, such as a linked `config`
  (git_identity_refusal()); no symbolic link anywhere in the copy may lead outside the run's folder (link_refusal(),
  LINKS; asked of plain sibling folders too, and again after a clone's checkout and before each launch); then the
  remotes defined by files under `.git/remotes/` and `.git/branches/` (an older form that `git remote` does not list, and that git still pushes to) are deleted, and the other remotes are removed
  (`remove`) or each gets a push URL that cannot resolve (`no-push`), and the result is read back from git: no remote
  left, or every push URL git would use equal to the one set (a `url.<base>.insteadOf` rule, wherever it is
  configured, can rewrite the URL that was stored). A copy of a MEMBER (`member=True`) with no `.git` entry of its
  own is refused: git run in it would act on whatever repository encloses the copy folder (a member that is a
  folder inside a shared repository has no `.git` of its own). A copy of a sibling folder with no `.git` entry is a
  plain folder: only LINKS is asked of it, nothing is changed, and git run in it acts on any repository that
  encloses it.

NOT read or closed: the object store's `alternates` file, `core.hooksPath`, a push to an explicit URL or path by
code run outside a batch session (sessions get an empty GIT_ALLOW_PROTOCOL), any direct write by code that runs in
the copy, a link that code makes after LINKS was asked, and anything that code does to git's settings after it
starts.
"""
import hashlib
import os
import re
import secrets
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

NO_PUSH_URL = "no-push://disabled-by-the-migration-kit"
# Environment variables that tell git where a repository's parts are, whatever folder git is run in.
GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                     "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")


def same_folder(a, b):
    """Whether both paths name one existing file-system entry (os.path.samefile); when that cannot be read, whether
    the two paths are equal."""
    try:
        return os.path.samefile(a, b)
    except OSError:
        return a == b


def folders_overlap(a, b):
    """Whether resolved folder `a` is folder `b`, contains it or lies inside it."""
    a, b = Path(a).resolve(), Path(b).resolve()
    return (same_folder(a, b) or any(same_folder(p, b) for p in a.parents)
            or any(same_folder(p, a) for p in b.parents))


def env_refusal(env=None):
    """Why git may not be run with this environment (default: this process's), or None: it holds one of
    GIT_LOCATION_VARS, which git obeys whatever folder it is run in."""
    env = os.environ if env is None else env
    held = sorted(k for k in GIT_LOCATION_VARS if k in env)
    if held:
        return (f"the environment holds {', '.join(held)}, which tells git where a repository is whatever folder it "
                "runs in; unset it first")
    return None


KIT_ENV_DIR = ".kit-env"            # under a run folder: the contained environment's own files
NO_TRANSPORT = ""                   # git's protocol allow-list with nothing on it (launch_batch.SESSION_ALLOW_PROTOCOL)


def contained_env(run, copy=None, allow_protocol=None, hooks="off", base=None, check=True):
    """The environment for git and code the kit runs in a copy (R1 ENV; B152/B153 bind it to the closures already
    built). Starting from `base` (default: this process's environment):
    - drops every git location variable (GIT_LOCATION_VARS) and every inherited GIT_CONFIG_* entry, and a
      GIT_ALLOW_PROTOCOL naming the dead scheme;
    - sets GIT_CEILING_DIRECTORIES to `run`, so git run in a plain copied folder never finds a repository that holds the
      run folder (R1-T3); GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL to a file in `run` holding only a user name and
      e-mail, and XDG_CONFIG_HOME inside `run`, so no operator configuration (and no include in it) is read;
      GIT_OPTIONAL_LOCKS=0; and CLAUDE_PROJECT_DIR to `copy` when given (R1-T16);
    - `allow_protocol`: None leaves transports as they are (member code: a suite's own local clone, fetch or push
      tests run, as the release text says for B8a; the copy's dead scheme stays closed by its own config); a string
      sets GIT_ALLOW_PROTOCOL to it (the kit's own git acts in a copy pass NO_TRANSPORT, the empty list);
    - `hooks="off"` sets core.hooksPath to an empty folder in `run` through GIT_CONFIG_*, which outranks the copy's
      own setting, so no copied hook runs in a kit git act (R1-T15); `hooks="copy"` leaves the copy's hooks in force.
    The files it names are made in `run` (`.kit-env/`) by the contained writer. With `check` (the default), when
    `copy` is a repository its push routes are read under the environment just built (env_route_refusal(), B160
    finding 1); a builder with `check=False` leaves that to its caller, immediately before use. Raises
    ContainmentRefused when the files cannot be made or the check fails."""
    if hooks not in ("off", "copy"):
        raise ValueError(f"hooks must be 'off' or 'copy', not {hooks!r}")
    # B160 finding 3: absolute paths (links not resolved), so a child started in the copy names the same files
    run = Path(os.path.abspath(run))
    copy = Path(os.path.abspath(copy)) if copy is not None else None
    env = contained_read_env(run, copy, base)     # the same variables the after-run re-read uses (B163 finding 4)
    if DEAD_SCHEME in env.get("GIT_ALLOW_PROTOCOL", "").split(":"):
        env.pop("GIT_ALLOW_PROTOCOL")
    contained_mkdir(run, f"{KIT_ENV_DIR}/nohooks")
    contained_mkdir(run, f"{KIT_ENV_DIR}/xdg")
    held = os.listdir(run / KIT_ENV_DIR / "nohooks")          # B160 finding 2: empty at every use
    if held and hooks == "off":
        raise ContainmentRefused(f"{run / KIT_ENV_DIR / 'nohooks'} is not empty ({sorted(held)[:3]}); git would run "
                                 "those files as hooks")
    contained_write(run, f"{KIT_ENV_DIR}/gitconfig", b"[user]\n\tname = aget-migration-kit\n"
                                                      b"\temail = kit@invalid\n")
    if allow_protocol is not None:
        env["GIT_ALLOW_PROTOCOL"] = allow_protocol
    if hooks == "off":
        env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath",
                    "GIT_CONFIG_VALUE_0": str(run / KIT_ENV_DIR / "nohooks")})
    if check and copy is not None and os.path.isdir(copy / ".git") and not os.path.islink(copy / ".git"):
        why = env_route_refusal(copy, env, run)             # B160 finding 1: checked under the very environment
        if why:
            raise ContainmentRefused(f"under the contained environment: {why}")
    return env


def hooks_path_refusal(copy, run, env):
    """Why the hooks git would run in `copy` under `env` lie outside `run`, or None (R1 clause 6(c), launch half;
    B162 finding 2's class): when `core.hooksPath` is set (read under `env`), the folder it names (relative to the
    copy's working tree) must resolve inside `run`, and no entry in it may be a link leading outside `run`. Asked at
    the launch and again after the session (after_run_check --copy-run). A failed read is a refusal."""
    # B163 finding 2: the value is read NUL-delimited as bytes, with git's own path expansion (`--type=path`), and only
    # the delimiter is removed; no file name character is trimmed
    p = subprocess.run(["git", *READ_FLAGS, "-C", str(copy), "config", "-z", "--type=path", "--get", "core.hooksPath"],
                       capture_output=True, env=env)
    if p.returncode == 1 and not p.stderr.strip():
        return None                                     # unset: the copy's own .git/hooks, walked by LINKS
    if p.returncode or not p.stdout.endswith(b"\0"):
        last = (os.fsdecode(p.stderr).strip() or "no output").splitlines()[-1][:120]
        return f"core.hooksPath in {copy} cannot be read (git exit {p.returncode}: {last}); not read as unset"
    value = os.fsdecode(p.stdout[:-1])
    if not value:
        return f"core.hooksPath in {copy} is set but empty; the hooks git would run cannot be named"
    if not os.path.isabs(value):
        # B164 finding 1: a relative value is resolved by git against the working tree it acts on; under `env` that
        # must still be the copy itself (the isolation identity test, asked again), else the hooks cannot be judged
        why = git_identity_refusal(copy, env)
        if why:
            return f"the hooks core.hooksPath names ({value!r}) cannot be judged: {why}"
    folder = Path(value) if os.path.isabs(value) else Path(copy) / value
    real, bound = os.path.realpath(folder), os.path.realpath(run)
    if real != bound and os.path.commonpath([bound, real]) != bound:
        return (f"core.hooksPath in {copy} names {value!r} ({real!r}), outside the run folder {bound}; its hooks "
                "would run")
    link = outside_link(folder, run) if os.path.isdir(folder) else None   # its entries too (B163 finding 4)
    if link:
        return f"{link} in the hooks folder core.hooksPath names leads outside the run folder {bound}"
    return None


def contained_read_env(run, copy=None, base=None):
    """The configuration a contained environment (contained_env() for `run`) gives git, without making or rewriting
    any of its files: for reading what a session's git saw, after the session (B163 finding 4). It names the same
    global configuration file, XDG folder, ceiling and project folder, and reads no system configuration."""
    run = Path(os.path.abspath(run))
    env = {k: v for k, v in (os.environ if base is None else base).items()
           if k not in GIT_LOCATION_VARS and not k.startswith("GIT_CONFIG")}
    env.update({"GIT_CEILING_DIRECTORIES": str(run.resolve()), "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": str(run / KIT_ENV_DIR / "gitconfig"),
                "XDG_CONFIG_HOME": str(run / KIT_ENV_DIR / "xdg"), "GIT_OPTIONAL_LOCKS": "0"})
    if copy is not None:
        env["CLAUDE_PROJECT_DIR"] = os.path.abspath(copy)
    return env


def env_route_refusal(copy, env, run=None):
    """Why the isolated copy, read under `env` (the environment its code or a kit act will run with), could push
    somewhere: the dead scheme must read `never`, no include may be able to change later (include_refusal()), and every
    push route git resolves must use the dead scheme, closed in the copy (B160 finding 1: ENV dropped a caller-global
    rewrite, and a route isolation had read as dead resolved to a real path). None when none can."""
    try:
        used = _query(copy, env, "config", "--get", f"protocol.{DEAD_SCHEME}.allow").strip()
        why = include_refusal(copy, env)
        # B165 finding 1: the route probe needs the run; a contained environment names it (its ceiling)
        routes = push_routes(copy, env, run if run is not None else env.get("GIT_CEILING_DIRECTORIES"))
    except InspectionFailed as e:
        return str(e)
    if why:
        return why
    if used != "never":
        return f"protocol.{DEAD_SCHEME}.allow in {copy} reads {used or 'unset'}, not never"
    bad = {n: u for n, u in routes.items() if any(not x.startswith(f"{DEAD_SCHEME}://") for x in u)}
    if bad:
        return (f"git could push from {copy} by {sorted(bad)} (resolved to "
                f"{sorted({x for v in bad.values() for x in v})[:3]})")
    return None


def place_refusal(target, live, what="the copy folder", inside_ok=False, env=None, sources=()):
    """Why `target` may not be cleared and filled as a copy or clone of `live`, or None: the environment holds a git
    location variable (env_refusal()); or the folder is the live folder, holds it or lies inside it; or it is, holds
    or lies inside one of `sources`, the live sibling folders the copy is made from (R1-T1: a scratch inside a declared
    sibling source was cleared and filled there). With `inside_ok` a folder inside the live folder is accepted (a
    clone made under a work folder that sits in the live tree clears only itself); the live folder itself and a folder
    holding it are still refused. Asked before anything is removed, copied or cloned, and so before the first git
    command."""
    why = env_refusal(env)
    if why:
        return f"{why}; nothing was removed or copied"
    t, lv = Path(target).resolve(), Path(live).resolve()
    inside = any(same_folder(p, lv) for p in t.parents)
    if folders_overlap(t, lv) and not (inside_ok and inside and not same_folder(t, lv)):
        return (f"{what} {t} is, contains or lies inside the live folder {lv}; nothing was removed or copied")
    for src in sources:
        if folders_overlap(t, src):
            return (f"{what} {t} is, contains or lies inside the live sibling folder {Path(src).resolve()}; nothing "
                    "was removed or copied")
    return None


def sibling_sources(location, rels):
    """The live folders a member's declared siblings (`rels`, relative to `location`, e.g. `../aget`) are copied
    from, resolved."""
    return [(Path(location) / rel).resolve() for rel in rels]


def git_identity_refusal(folder, env=None):
    """Why git, run in this folder, would act on a repository or working tree other than the folder's own, or None.
    Refused when the environment git gets (`env`, default this process's) holds one of GIT_LOCATION_VARS; when
    <folder>/.git is a symbolic link or not a folder (a `gitdir:` file, as a linked worktree or a submodule has); and
    when `git rev-parse --show-toplevel --absolute-git-dir --git-common-dir`, run in the folder with that environment,
    fails or names a working tree other than the folder, or a git folder or common git folder other than
    <folder>/.git. So a `core.worktree` setting in the copy's config, a `commondir` file and a bare repository refuse.
    The test is git's own answer, not a reading of the config file's text. Refused too when an entry under
    <folder>/.git is a symbolic link that leads outside the copy folder (outside_link(); R1 LINKS, J-2/H-4: the
    boundary is the copy, not its .git, so a hook linked into the member's own tree, such as
    `.git/hooks/pre-commit -> ../../scripts/pre-commit`, is admitted): git's answers stay the copy's own while a
    command that writes `config`, a ref or an object through the link changes the live repository. Refused as well
    when a regular file reachable under <folder>/.git, object store included, has a second name (shared_git_file(); B166
    finding 1): git appends a reflog in place, so the file behind the other name would change."""
    cr = Path(folder).resolve()
    env = dict(os.environ) if env is None else env
    why = env_refusal(env)
    if why:
        return why
    dot = cr / ".git"
    if dot.is_symlink() or not dot.is_dir():
        return f"{dot} is not a folder of its own (absent, a symbolic link or a gitdir file); a copy has its own"
    link = outside_link(dot, cr)
    if link:
        return (f"{link} is a symbolic link that leads outside {cr}; git writing through it would change another "
                "repository; a copy has its own files")
    shared = shared_git_file(dot)
    if shared:                                          # B166-B168 finding 1: git appends a reflog in place
        return f"{shared[0]} {shared[1]}; a copy has its own files"
    p = subprocess.run(["git", *READ_FLAGS, "-C", str(cr), "rev-parse", "--show-toplevel", "--absolute-git-dir", "--git-common-dir"],
                       capture_output=True, text=True, env=env)
    lines = p.stdout.splitlines()
    if p.returncode or len(lines) != 3:
        return (f"git cannot name a working tree and git folder for {cr} "
                f"({(p.stderr.strip() or 'no output').splitlines()[-1][:160]})")
    top, git_dir, common = lines[0], lines[1], cr / lines[2]
    if not same_folder(top, cr):
        return (f"git run in {cr} acts on the working tree {top} (core.worktree or another redirection); "
                "a copy is its own working tree")
    if not same_folder(git_dir, dot) or not same_folder(common, dot):
        return (f"git run in {cr} uses the git folder {git_dir} (common folder {common.resolve()}), not {dot}; "
                "a copy has its own")
    return None


def shared_git_file(git_dir):
    """The first regular file reachable under `git_dir` that has more than one name (`st_nlink > 1`), as a path, else
    None (B166, B167 and B168 finding 1). Git writes some of its files in place (a reflog is appended, FETCH_HEAD and
    COMMIT_EDITMSG are rewritten), so a second name would change with them. There is no exemption: the object store
    is checked too (B168 finding 1: each exemption so far had a route around it), so a repository that shares object
    files by hard link, as a plain local `git clone` makes, is refused; every copy the kit makes has its own files
    (clones with `--no-hardlinks`, `copytree`, `cp -a`). A symbolic link is followed (one that leads outside the copy
    is refused before this, by outside_link()): a file alias is judged by the regular file it resolves to, and a
    folder alias is walked as the folder it resolves to, wherever that lies. Each resolved folder is walked once, so a
    cycle of aliases ends. Opens no file. Also returned (B169 findings 1-2): anything that is neither a regular file
    nor a folder (a FIFO, socket or device), whatever its link count, and any entry or folder whose inspection fails.
    Only a dangling link (its target does not exist) is skipped: it names nothing to append to. Returns
    (path, reason) or None."""
    walked, stack = set(), [Path(git_dir)]
    while stack:
        folder = stack.pop()
        real = os.path.realpath(folder)
        if real in walked:
            continue
        walked.add(real)
        try:
            entries = sorted(os.scandir(folder), key=lambda e: e.name)
        except OSError as exc:
            return folder, f"cannot be listed ({type(exc).__name__}), so what git may write in it is unknown"
        for e in entries:
            path = Path(folder) / e.name
            try:
                st = os.lstat(path)
            except OSError as exc:                      # B169 finding 2: a failed inspection is never harmless
                return path, f"cannot be inspected ({type(exc).__name__}), so whether git may write it is unknown"
            if stat.S_ISLNK(st.st_mode):
                try:
                    st = os.stat(path)
                except FileNotFoundError:
                    continue                            # dangling: it names nothing to append to
                except OSError as exc:
                    return path, f"is a link that cannot be resolved ({type(exc).__name__})"
            if stat.S_ISDIR(st.st_mode):
                stack.append(path)
            elif not stat.S_ISREG(st.st_mode):          # B169 finding 1: a FIFO, socket or device, whatever its names
                return path, (f"is not a regular file or folder (mode {stat.S_IFMT(st.st_mode):o}); git writing it "
                              "in place would reach whatever reads or owns it")
            elif st.st_nlink > 1:
                return path, ("has more than one name (a hard link); git writing it in place (a reflog append) would "
                              "change the file behind its other name")
    return None


def outside_link(folder, boundary=None):
    """The first entry under `folder` that is a symbolic link resolving outside `boundary` (default: `folder`
    itself), as a path, else None. The walk never follows a link, and a link's target is resolved as git or a test
    would reach it (os.path.realpath, every link on the way followed; a dangling link is judged by where it points).
    A link that stays inside the boundary (an old-style HEAD, a hook linked into the member's tree) is accepted."""
    root = Path(os.path.realpath(boundary if boundary is not None else folder))
    for parent, dirs, files in os.walk(folder, followlinks=False):
        for name in sorted(dirs) + sorted(files):
            entry = Path(parent) / name
            if entry.is_symlink():
                target = Path(os.path.realpath(entry))
                if target != root and root not in target.parents:
                    return entry
    return None


def link_refusal(folder, run=None):
    """LINKS (R1 clause 4; J-2, H-4, H-5): why the copy `folder` may not be used, or None. Refused when any symbolic
    link under it, in the working tree or in .git, resolves outside `run` (the run's folder: the copy itself, or the
    folder that holds the copy and its copied siblings). Asked after the copy is made or checked out, before any git
    act, test, hook or launch in it, and again before each launch. A link made later, by code that runs in the copy,
    is not seen by this check: after-run check G reports a written path that is a link."""
    boundary = Path(run) if run is not None else Path(folder)
    link = outside_link(folder, boundary)
    if link:
        try:
            to = os.readlink(link)
        except OSError:
            to = "?"
        return (f"{link} is a symbolic link that leads outside {Path(os.path.realpath(boundary))} (to {to}); a "
                "write, a test or a hook reaching it would act outside the copy; nothing was run in the copy")
    return None


LEGACY_REMOTE_DIRS = ("remotes", "branches")


def legacy_remote_files(git_dir):
    """The entries under <git_dir>/remotes and <git_dir>/branches: remote definitions in git's older form, which
    `git remote` does not list and `git push <name>` still uses."""
    found = []
    for d in LEGACY_REMOTE_DIRS:
        folder = Path(git_dir) / d
        if folder.is_dir() and not folder.is_symlink():
            found += sorted(folder.iterdir())
        elif os.path.lexists(folder) and not folder.is_dir():
            found.append(folder)
        elif folder.is_symlink():
            found.append(folder)
    return found


def act_refusal(copy, env, run):
    """Why the kit may not make its next git act (checkout, add, rm, commit) in the copy, or None (B165 finding 1):
    git, asked under the act's environment, must still name the copy as its own working tree with its own git
    folder, no `.git` entry linking outside it (git_identity_refusal()), and no symbolic link under the copy may
    lead outside `run` (LINKS). Asked immediately before each such act made after member code ran in the copy."""
    return git_identity_refusal(copy, env) or link_refusal(copy, run)


def register_location(aget, register):
    """The location the fleet register file `register` (FLEET_STATE.yaml) records for `aget`, with `~` expanded, as
    (location, None); (None, reason) when the register cannot be read or does not list the Aget."""
    try:
        import yaml
        doc = yaml.safe_load(Path(register).read_text())
        found = [a.get("location") for sub in (doc.get("fleet") or {}).values() for a in (sub.get("agents") or [])
                 if isinstance(a, dict) and a.get("agent_name") == aget]
    except Exception as e:                                # noqa: BLE001 — any failure is a refusal, never a pass
        return None, f"the fleet register {register} cannot be read ({type(e).__name__}: {e})"
    if len(found) != 1 or not isinstance(found[0], str) or not found[0]:
        return None, f"the fleet register {register} lists {len(found)} location(s) for {aget!r}, not one"
    return os.path.expanduser(found[0]), None


def member_refusal(aget, folder, run=None, register=None):
    """BIND (R1 clause 1, running code; R1-T7): why the kit may not act on `folder` as `aget`, or None. The folder,
    taken as given (no `~` expansion: the kit acts on the path it is given), must be the location the fleet register
    records for that Aget (the same folder, links resolved), or lie inside this run's folder `run` (a rehearsal copy).
    A register that cannot be read, or that lists the Aget other than once, refuses unless the folder is in `run`; a
    `run` that holds the Aget's register location is refused (it would admit the live member as a copy)."""
    real = os.path.realpath(folder)
    if run is not None:
        r = os.path.realpath(run)
        if real == r or os.path.commonpath([r, real]) == r:
            # a copy, unless the run folder holds the Aget's live location (a `--run` naming the member, or a folder
            # above it, would otherwise admit the live member as a copy)
            loc = register_location(aget, register)[0] if register is not None else None
            live = os.path.realpath(loc) if loc else None
            if live and (live == r or os.path.commonpath([r, live]) == r):
                return f"the run folder {run} holds {aget}'s location in the fleet register ({loc}); it is not a copy"
            return None
    if register is None:
        return (f"{folder} is not inside a run folder, and no fleet register was named to show it is {aget}'s "
                "location")
    loc, why = register_location(aget, register)
    if why:
        return f"{folder} is not inside a run folder, and {why}"
    if os.path.realpath(loc) != real:
        return (f"{folder} is not {aget}'s location in the fleet register ({loc})"
                + (f" and does not lie inside the run folder {run}" if run is not None else ""))
    return None


def inrun_refusal(repo, run, env=None):
    """INRUN (R1 clause 2, the git-act row: config and remote writes; R1-T5): why the kit may not change `repo`'s
    remotes or configuration, or None. Asked by each function that does so, itself, so its safety does not depend on
    the order its callers call it in: a run folder must be named, `repo` must be it or lie inside it, and git, asked
    under `env`, must name `repo` as its own working tree with its own git folder (git_identity_refusal())."""
    if run is None:
        return (f"no run folder was named for {repo}; the kit changes a repository's remotes or configuration only "
                "in a copy inside this run's folder")
    r, p = os.path.realpath(run), os.path.realpath(repo)
    if p != r and os.path.commonpath([r, p]) != r:
        return f"{repo} does not lie inside the run folder {run}; its remotes and configuration are not changed"
    return git_identity_refusal(repo, env)


def remove_legacy_remotes(repo, run=None, env=None):
    """Delete every remote definition under <repo>/.git/remotes and <repo>/.git/branches (legacy_remote_files()),
    after INRUN (inrun_refusal()). Returns None when none is left, else the reason."""
    why = inrun_refusal(repo, run, env)
    if why:
        return why
    dot = Path(repo) / ".git"
    for entry in legacy_remote_files(dot):
        try:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except OSError as e:
            return f"could not delete the remote definition {entry} ({e})"
    left = legacy_remote_files(dot)
    if left:
        return f"remote definitions are still present after deletion: {[str(p) for p in left]}"
    return None


def disable_push(repo, url=NO_PUSH_URL, env=None, run=None):
    """Give every remote of the repository at `repo` (a folder whose own .git is a directory) the push URL `url`,
    which cannot resolve, and read back from git the push URLs it would use (`git remote get-url --push --all`):
    each must equal `url`. A stored URL can be rewritten by a `url.<base>.insteadOf` or `pushInsteadOf` rule in any
    configuration git reads, and a rewritten one is a reason, not a success. Git is pointed at that .git by name, so
    it never searches upward into an enclosing repository. Remotes defined by files under `.git/remotes/` or
    `.git/branches/` are deleted first (remove_legacy_remotes()). Returns None when every remote pushes only to
    `url`, else the reason. This closes a push to a named remote from that folder only: a push to an explicit URL or
    path stays open. INRUN first (inrun_refusal(), through remove_legacy_remotes())."""
    why = remove_legacy_remotes(repo, run, env)
    if why:
        return why
    git = ["git", "--git-dir", str(Path(repo) / ".git")]
    listed = subprocess.run([*git, "remote"], capture_output=True, text=True, env=env)
    if listed.returncode:
        return "could not list the remotes"
    for remote in listed.stdout.split():
        if subprocess.run([*git, "remote", "set-url", "--push", remote, url],
                          capture_output=True, text=True, env=env).returncode:
            return f"could not disable push for remote {remote!r}"
        used = subprocess.run([*git, "remote", "get-url", "--push", "--all", remote], capture_output=True, text=True, env=env)
        urls = used.stdout.split()
        if used.returncode or not urls or any(u != url for u in urls):
            return (f"the push URL git would use for remote {remote!r} is {urls or 'unreadable'}, not {url!r} "
                    "(a URL rewrite rule, or a second push URL)")
    return None


def remove_remotes(repo, env=None, run=None):
    """Remove every remote of the repository at `repo` (a folder whose own .git is a directory), git pointed at that
    .git by name, after deleting the remote definitions under `.git/remotes/` and `.git/branches/`
    (remove_legacy_remotes(), which asks INRUN first). Returns None when none is left, else the reason."""
    why = remove_legacy_remotes(repo, run, env)
    if why:
        return why
    git = ["git", "--git-dir", str(Path(repo) / ".git")]
    listed = subprocess.run([*git, "remote"], capture_output=True, text=True, env=env)
    if listed.returncode:
        return "could not list the remotes"
    for remote in listed.stdout.split():
        if subprocess.run([*git, "remote", "remove", remote], capture_output=True, text=True, env=env).returncode:
            return f"could not remove remote {remote!r}"
    left = subprocess.run([*git, "remote"], capture_output=True, text=True, env=env)
    if left.returncode or left.stdout.split():
        return f"remotes are still listed after removal: {left.stdout.split() or 'unreadable'}"
    return None


DEST_OPS = ("write", "mkdir", "delete")


def destination_refusal(root, rel, op="write"):
    """Why the kit may not perform `op` (write, mkdir or delete) on `rel` inside the folder `root` (a member, or a
    copy of one), or None. This is R1 clause 2's test for that operation, as a check only (DEST): the act itself is
    performed by the contained writer (contained_write() and the others below), which repeats it at the act.
    Common part: refused when `rel` is absolute, empty, or has a `..`, `.` or empty component; when `root` itself, or
    any folder between it and the target that exists, is a symbolic link or not a folder; and when the resolved path
    does not lie inside the resolved `root`. Per operation, judged on the last component without following it:
    - write: absent, or a regular file with one name (`st_nlink == 1`): writing a file that has a second name (a hard
      link) changes the other name's bytes too, wherever it is (J-5);
    - mkdir: absent, or a folder;
    - delete: a regular file, with any number of names (unlinking one name writes no bytes).
    Asked when the plan is made and at launch; a check alone does not close the window before the act."""
    if op not in DEST_OPS:
        raise ValueError(f"op must be one of {DEST_OPS}, not {op!r}")
    why = _rel_refusal(rel)
    if why:
        return why
    rel_path = Path(rel)
    base = Path(root)
    if base.is_symlink():
        return f"{base} is a symbolic link"
    p = base
    parts = rel_path.parts
    for i, part in enumerate(parts):
        p = p / part
        if p.is_symlink():
            return f"{p} is a symbolic link; a write through it lands wherever it points"
        if not os.path.lexists(p):
            break
        if i < len(parts) - 1 and not p.is_dir():
            return f"{p} is not a folder"
    target, top = (base / rel_path).resolve(), base.resolve()
    if top not in target.parents:
        return f"{base / rel_path} resolves to {target}, outside {top}"
    leaf = base / rel_path
    if os.path.lexists(leaf):
        st = os.lstat(leaf)
        if op == "write":
            if not stat.S_ISREG(st.st_mode):
                return f"{leaf} is not a regular file"
            if st.st_nlink != 1:
                return (f"{leaf} has {st.st_nlink} names (a hard link); writing it would change the other names' "
                        "bytes too")
        elif op == "mkdir" and not stat.S_ISDIR(st.st_mode):
            return f"{leaf} exists and is not a folder"
        elif op == "delete" and not stat.S_ISREG(st.st_mode):
            return f"{leaf} is not a regular file; only a regular file is deleted"
    elif op == "delete":
        return f"{leaf} does not exist"
    return None


def _rel_refusal(rel):
    """Why `rel` is not a plain relative path with no `..`, `.` or empty component, or None."""
    s = str(rel)
    if not s or os.path.isabs(s):
        return f"{rel} is not a path inside the folder"
    comps = s.split("/")
    if any(c in ("", ".", "..") for c in comps):
        return f"{rel} is not a path inside the folder (an empty, `.` or `..` component)"
    return None


# --- R1 clause 2, enforced at the act: the contained writer (CW) --------------------------------------------------

class ContainmentRefused(Exception):
    """The contained writer refused an act; the message names why. Nothing was written by the refused act."""


def host_refusal():
    """Why this host cannot run the contained writer, or None. It needs dir_fd support for open, rename, mkdir,
    unlink, rmdir and stat, `O_NOFOLLOW` and `O_DIRECTORY`, and an fd-based rmtree. Without them the act is refused,
    never performed unprotected."""
    missing = [n for n in ("O_NOFOLLOW", "O_DIRECTORY") if not hasattr(os, n)]
    for fn in (os.open, os.rename, os.mkdir, os.unlink, os.rmdir, os.stat):
        if fn not in os.supports_dir_fd:
            missing.append(f"dir_fd for os.{fn.__name__}")
    if not getattr(shutil.rmtree, "avoids_symlink_attacks", False):
        missing.append("fd-based shutil.rmtree")
    return f"this host lacks {', '.join(missing)}; the kit will not write without them" if missing else None


def member_root(root):
    """B194 finding 1 (the contract `place_file._root` applies to the placer, for the contained writer's whole family):
    the member folder named so that O_NOFOLLOW applies to the member itself. A NUL, or a `.` or `..` name (`<link>/./`,
    `<link>/sub/..` open through the link) refuses; trailing slashes are dropped (`<link>/` opens the target). Folders
    above the member are the operator's and are not walked."""
    r = os.fspath(root)
    r = os.fsdecode(r) if isinstance(r, bytes) else r
    if "\0" in r:
        raise ContainmentRefused("the member's path holds a NUL byte")
    r = r.rstrip("/") or "/"
    if any(c in (".", "..") for c in r.split("/")):
        raise ContainmentRefused(f"{r}: a member folder named with `.` or `..`")
    return r


def root_identity(root):
    """(st_dev, st_ino) of the folder `root`, read without following a link at its last component."""
    st = os.lstat(member_root(root))
    if not stat.S_ISDIR(st.st_mode):
        raise ContainmentRefused(f"{root} is not a folder (or is a symbolic link)")
    return (st.st_dev, st.st_ino)


def _open_root(root, root_id=None):
    try:
        fd = os.open(member_root(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        raise ContainmentRefused(f"{root} cannot be opened as a folder without following a link ({e})") from None
    st = os.fstat(fd)
    if root_id is not None and (st.st_dev, st.st_ino) != tuple(root_id):
        os.close(fd)
        raise ContainmentRefused(f"{root} is no longer the folder recorded when the act was allowed")
    return fd


def _open_child_dir(fd, name, where):
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
    except OSError as e:
        raise ContainmentRefused(f"{where} is a symbolic link or not a folder ({e.strerror})") from None


def _walk(root, comps, root_id=None, create=False, created=None):
    """An fd for the folder root/comps..., opened component by component with O_NOFOLLOW. With `create`, a missing
    component is made with mkdirat at its parent's fd and its path is appended to `created`."""
    fd = _open_root(root, root_id)
    where = Path(root)
    done = []
    try:
        for c in comps:
            where = where / c
            try:
                st = os.stat(c, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                if not create:
                    raise ContainmentRefused(f"{where} does not exist") from None
                _same_place(root, done, fd, root_id)          # B143 finding 1: the mkdir is an act too
                try:
                    os.mkdir(c, 0o777, dir_fd=fd)
                except FileExistsError:
                    # Parallel members can create the shared .kit-env after our stat. The no-follow directory
                    # open below still refuses a link or a non-directory; only our own mkdir is rollback-owned.
                    pass
                else:
                    if created is not None:
                        created.append(where)
                st = None
            if st is not None and not stat.S_ISDIR(st.st_mode):
                raise ContainmentRefused(f"{where} is a symbolic link or not a folder")
            nfd = _open_child_dir(fd, c, where)
            os.close(fd)
            fd = nfd
            done.append(c)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _same_place(root, parents, pfd, root_id=None):
    """Refuse unless a fresh O_NOFOLLOW walk from `root` to `parents` reaches the very folder `pfd` holds. A folder the
    kit opened can be renamed out of the root by another process after the walk; the fd still names it there. This
    re-check runs immediately before each act (mkdir, temp-file creation, rename, unlink, rmdir) and narrows that
    window; it cannot close it. Stated limit: the contained writer's guarantees hold only under EXCLUSIVE MUTATION of
    the root's folder tree for the operation, meaning no other process (not only no second kit run) writes, renames or
    moves anything in it; a move after the last re-walk is not seen."""
    fd = _walk(root, parents, root_id)
    try:
        a, b = os.fstat(fd), os.fstat(pfd)
        if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
            raise ContainmentRefused(f"{Path(root).joinpath(*parents)} is no longer the folder the kit opened (it was "
                                     "moved or replaced); nothing was written there")
    finally:
        os.close(fd)


def _split(rel):
    why = _rel_refusal(rel)
    if why:
        raise ContainmentRefused(why)
    comps = str(rel).split("/")
    return comps[:-1], comps[-1]


def _replace_at(pfd, tmp, leaf):
    """renameat(tmp, leaf) inside one folder fd. A seam for tests (a failing or killed write)."""
    os.rename(tmp, leaf, src_dir_fd=pfd, dst_dir_fd=pfd)


def contained_read(root, rel, root_id=None):
    """(bytes, mode) of the regular file root/rel, read without following any link, or (None, None) when absent.
    Refuses a link or a non-regular entry."""
    parents, leaf = _split(rel)
    try:
        pfd = _walk(root, parents, root_id)
    except ContainmentRefused as e:
        if "does not exist" in str(e):
            return None, None
        raise
    try:
        try:
            st = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
        except FileNotFoundError:
            return None, None
        if not stat.S_ISREG(st.st_mode):
            raise ContainmentRefused(f"{Path(root) / rel} is not a regular file")
        fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=pfd)
        with os.fdopen(fd, "rb") as fh:
            return fh.read(), stat.S_IMODE(st.st_mode)
    finally:
        os.close(pfd)


def contained_write(root, rel, data, mode=None, root_id=None, created=None):
    """Write `data` to root/rel at the act (R1 clause 2, file-write row): the parent is reached by an fd walk with
    O_NOFOLLOW (missing folders are made with mkdirat and appended to `created`), the target must be absent or a
    regular file with one name, a temp file is made with O_CREAT|O_EXCL|O_NOFOLLOW in that folder, written, read
    back, given `mode` (else the target's mode, else the umask default) and renamed onto the name. Never an in-place
    truncation; a link on the way is refused, never followed. Raises ContainmentRefused."""
    why = host_refusal()
    if why:
        raise ContainmentRefused(why)
    parents, leaf = _split(rel)
    pfd = _walk(root, parents, root_id, create=True, created=created)
    tmp = None
    try:
        try:
            st = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
        except FileNotFoundError:
            st = None
        if st is not None:
            if not stat.S_ISREG(st.st_mode):
                raise ContainmentRefused(f"{Path(root) / rel} is not a regular file")
            if st.st_nlink != 1:
                raise ContainmentRefused(f"{Path(root) / rel} has {st.st_nlink} names (a hard link)")
            if mode is None:
                mode = stat.S_IMODE(st.st_mode)
        _same_place(root, parents, pfd, root_id)
        tmp = f".{leaf}.kit-{os.getpid()}-{secrets.token_hex(4)}.tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o666, dir_fd=pfd)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            if mode is not None:
                os.fchmod(fh.fileno(), mode)
        rfd = os.open(tmp, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=pfd)
        with os.fdopen(rfd, "rb") as fh:
            if fh.read() != data:
                raise ContainmentRefused(f"the temp file for {rel} did not read back")
        _same_place(root, parents, pfd, root_id)
        _replace_at(pfd, tmp, leaf)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp, dir_fd=pfd)
            except OSError:
                pass
        os.close(pfd)


def contained_mkdir(root, rel, root_id=None, created=None):
    """Make the folder root/rel and any missing folder on the way, each with mkdirat at its parent's fd; an existing
    component must be a folder, never a link (R1 clause 2, mkdir row). Never Path.mkdir(parents=True)."""
    why = host_refusal()
    if why:
        raise ContainmentRefused(why)
    parents, leaf = _split(rel)
    os.close(_walk(root, parents + [leaf], root_id, create=True, created=created))


def contained_unlink(root, rel, root_id=None):
    """Delete the regular file root/rel with unlinkat at its parent's fd (R1 clause 2, file-delete row); a link or a
    folder is refused. Absent is not an error (nothing to delete)."""
    parents, leaf = _split(rel)
    pfd = _walk(root, parents, root_id)
    try:
        try:
            st = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if not stat.S_ISREG(st.st_mode):
            raise ContainmentRefused(f"{Path(root) / rel} is not a regular file; it is not deleted")
        _same_place(root, parents, pfd, root_id)
        os.unlink(leaf, dir_fd=pfd)
    finally:
        os.close(pfd)


def contained_seal(root, folder_rel, leaf=None, root_id=None):
    """Clear the write bits (a-w) of root/folder_rel/leaf, when it is present, and then of the folder itself, each
    at an fd reached by the O_NOFOLLOW walk (B148 finding 1: a mode change is an act too, so R1 clause 2's walk and
    file identity apply). The folder must be reached without a link; the file must be a regular file with one name
    (a second name is another file the chmod would change). Everything is checked before any mode changes. Returns
    the file's sha256, or None when it is absent. Raises ContainmentRefused, with no mode changed, otherwise."""
    why = host_refusal() or _rel_refusal(folder_rel) or (_rel_refusal(leaf) if leaf else None)
    if why:
        raise ContainmentRefused(why)
    comps = str(folder_rel).split("/")
    fd = _walk(root, comps, root_id)
    ffd, digest = None, None
    try:
        if leaf:
            try:
                st = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                st = None
            if st is not None:
                where = Path(root) / folder_rel / leaf
                if not stat.S_ISREG(st.st_mode):
                    raise ContainmentRefused(f"{where} is not a regular file; nothing was sealed")
                ffd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
                fst = os.fstat(ffd)
                if (fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino) or fst.st_nlink != 1:
                    raise ContainmentRefused(f"{where} has {fst.st_nlink} names (a hard link) or was replaced; "
                                             "nothing was sealed")
                with os.fdopen(os.dup(ffd), "rb") as fh:
                    digest = hashlib.sha256(fh.read()).hexdigest()
        _same_place(root, comps, fd, root_id)
        if ffd is not None:
            os.fchmod(ffd, stat.S_IMODE(os.fstat(ffd).st_mode) & ~0o222)
        os.fchmod(fd, stat.S_IMODE(os.fstat(fd).st_mode) & ~0o222)
        return digest
    finally:
        if ffd is not None:
            os.close(ffd)
        os.close(fd)


def contained_rmdir(root, rel, root_id=None):
    """Remove the empty folder root/rel at its parent's fd. Raises OSError when it is not empty."""
    parents, leaf = _split(rel)
    pfd = _walk(root, parents, root_id)
    try:
        _same_place(root, parents, pfd, root_id)
        os.rmdir(leaf, dir_fd=pfd)
    finally:
        os.close(pfd)


def contained_rmtree(path, created_ids):
    """Delete the folder tree `path` only when its identity is one this run recorded at creation (`created_ids`, a
    set of (st_dev, st_ino)) and the host's rmtree is fd-based (removes a link entry, never its target). R1 clause 2,
    folder-tree delete row."""
    if not getattr(shutil.rmtree, "avoids_symlink_attacks", False):
        raise ContainmentRefused("this host's rmtree is not fd-based; the tree is not deleted")
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode) or (st.st_dev, st.st_ino) not in set(map(tuple, created_ids)):
        raise ContainmentRefused(f"{path} is not a folder this run created; it is not deleted")
    shutil.rmtree(path)


# --- R4: one shared precondition sweep and one shared all-or-nothing writer -------------------------------------

def head_of(repo):
    """The commit `repo` names as HEAD, read with GIT_OPTIONAL_LOCKS=0: a sha, `(unborn)` for a repository with no
    commit, or None when `repo` is not the top of a repository of its own."""
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    top = subprocess.run(["git", *READ_FLAGS, "-C", str(repo), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         env=env)
    if top.returncode or not same_folder(top.stdout.strip(), repo):
        return None
    h = subprocess.run(["git", *READ_FLAGS, "-C", str(repo), "rev-parse", "--verify", "-q", "HEAD"], capture_output=True,
                       text=True, env=env)
    return h.stdout.strip() if h.returncode == 0 else "(unborn)"


def write_refusals(root, writes, head=None):
    """Every reason, not only the first, why the writes `[(rel, expect_pre)]` may not begin in `root` (R4 pre_ok):
    (a) destination_refusal(root, rel, "write"); (b) the target is a regular file, or it is absent and `expect_pre`
    is `absent`; (d) when `head` is given, head_of(root) equals it. (c), the byte preconditions, is the caller's,
    which holds the list."""
    out = []
    for rel, expect_pre in writes:
        why = destination_refusal(root, rel, "write")
        if why:
            out.append(f"UNSAFE PATH: {why}")
            continue
        f = Path(root) / rel
        if not os.path.lexists(f) and expect_pre not in (None, "absent"):
            out.append(f"STALE: {rel} is absent, the list recorded {str(expect_pre)[:8]}")
    if head is not None:
        got = head_of(root)
        if got != head:
            out.append(f"HEAD MOVED: {root} is at {got or 'no repository of its own'}, the list names {head}")
    return out


class WriteResult:
    """What write_all did. `category` is C3 (every write rolled back and read back) or C4 (rollback incomplete), or
    None when every write landed and read back. `begun` says whether any mutation was attempted. `interrupted` holds
    the KeyboardInterrupt that stopped the writes (the caller records C5 for the batch)."""

    def __init__(self):
        self.category, self.why, self.begun, self.interrupted = None, "", False, None
        self.written, self.rolled_back, self.restored, self.not_restored = [], [], [], []

    def ok(self):
        """Every write landed and read back (an empty action list included: nothing to write is a success)."""
        return self.category is None and self.interrupted is None


def write_all(root, actions, root_id=None, expect_pre=None, modes=None):
    """Write every `(rel, data, post)` in `actions` into `root`, or none of them (R4 clause 2, C3/C4). Each target's
    prior bytes and mode (or absence) are recorded first. Each write re-runs destination_refusal (the per-write
    re-check), goes through contained_write (R1 at the act) and is read back against `post`. A refusal, a mismatch,
    any exception and KeyboardInterrupt all reach rollback: targets are restored in reverse order (or unlinked if they
    were absent), folders this call made are removed deepest first with rmdir only, and every target is read back
    against its record. All match: C3. Otherwise C4, naming what was and was not restored. A KeyboardInterrupt is
    never re-raised: it is returned in `interrupted`, after the rollback record is complete. A precondition refusal
    raised before the first write leaves `begun` False and the member unchanged. With `expect_pre` ({rel: sha256 or
    "absent"}), each target's recorded bytes must match it before the first write, else C2 with nothing written: the
    bytes the plan was made from are the bytes about to be replaced (B141 finding 1). `modes` optionally supplies
    release modes by path; these are written and read back too, while rollback always restores the prior mode."""
    res = WriteResult()
    snap = {}
    created = []
    attempted = []
    try:
        root_id = root_id or root_identity(root)
        for rel, _, _ in actions:
            snap[rel] = contained_read(root, rel, root_id)
        for rel, want in (expect_pre or {}).items():
            if rel in snap:
                got = "absent" if snap[rel][0] is None else hashlib.sha256(snap[rel][0]).hexdigest()
                if got != want:
                    raise ContainmentRefused(f"STALE: {rel} is {got[:8]} now, the plan was made from {str(want)[:8]}")
        for rel, data, post in actions:
            why = destination_refusal(root, rel, "write")
            if why:
                raise ContainmentRefused(f"UNSAFE PATH: {why}")
            res.begun = True
            attempted.append(rel)
            mode = (modes or {}).get(rel, snap[rel][1])
            contained_write(root, rel, data, mode=mode, root_id=root_id, created=created)
            got, got_mode = contained_read(root, rel, root_id)
            if got is None or hashlib.sha256(got).hexdigest() != post:
                raise ContainmentRefused(f"{rel} did not read back as its listed post bytes")
            if mode is not None and got_mode != mode:
                raise ContainmentRefused(f"{rel} did not read back as its listed post mode")
            res.written.append(rel)
        return res
    except BaseException as e:   # noqa: BLE001 — R4: every failure after the first write reaches rollback
        if isinstance(e, KeyboardInterrupt):
            res.interrupted = e
            res.why = "interrupted"
        else:
            res.why = str(e) if isinstance(e, ContainmentRefused) else f"{type(e).__name__}: {e}"
        if not res.begun:
            res.category = "C2"
            return res
        _rollback(root, root_id, snap, attempted, created, res)
        return res


def _note_interrupt(res, e):
    """An interrupt that arrives during the rollback is still C5 for the batch (B141 finding 3): it is recorded, the
    rollback carries on, and the caller stops the batch after this member."""
    if isinstance(e, KeyboardInterrupt) and res.interrupted is None:
        res.interrupted = e


def _rollback(root, root_id, snap, attempted, created, res):
    changed = set()
    for rel in reversed(attempted):
        prior, mode = snap[rel]
        try:
            if contained_read(root, rel, root_id) == snap[rel]:
                continue                                      # the in-flight write never landed: nothing to undo
        except BaseException as e:   # noqa: BLE001
            _note_interrupt(res, e)
        changed.add(rel)
        try:
            if prior is None:
                contained_unlink(root, rel, root_id)
            else:
                contained_write(root, rel, prior, mode=mode, root_id=root_id)
        except BaseException as e:   # noqa: BLE001
            _note_interrupt(res, e)
            res.not_restored.append({"path": rel, "why": f"{type(e).__name__}: {e}"})
    top = Path(root)
    for d in sorted(created, key=lambda p: len(p.parts), reverse=True):
        try:
            contained_rmdir(root, str(d.relative_to(top)), root_id)
        except BaseException as e:   # noqa: BLE001
            _note_interrupt(res, e)
            res.not_restored.append({"path": str(d.relative_to(top)) + "/", "why": f"folder not removed ({e})"})
    bad = {x["path"] for x in res.not_restored}
    for rel in attempted:
        if rel in bad:
            continue
        try:
            now = contained_read(root, rel, root_id)
        except BaseException as e:   # noqa: BLE001
            _note_interrupt(res, e)
            now = (f"unreadable: {e}", None)
        if now == snap[rel]:
            res.restored.append(rel)
        else:
            res.not_restored.append({"path": rel, "why": "read-back differs from the bytes and mode before"})
    res.rolled_back = [rel for rel in res.restored if rel in changed]
    res.category = "C4" if res.not_restored else "C3"


def isolate(copy, remotes, env=None, url=NO_PUSH_URL, member=False, run=None):
    """Make a fresh copy safe to run git and tests in, or say why it is not: None when done, else the reason, with
    nothing changed in the copy. `remotes` is `remove` (the copy loses its remotes) or `no-push` (each remote gets a
    push URL that cannot resolve). A copy of a member (`member=True`) with no `.git` entry of its own is refused: git
    run in it would act on the repository that encloses the copy folder. A copy of a sibling folder with no `.git`
    entry is a plain folder: only LINKS is asked of it. Every copy, plain folders included, is refused when a
    symbolic link under it resolves outside `run` (default: the copy itself; link_refusal()). Call it after the copy
    is made and before any other git command, checkout, apply, hook or test in it. A clone made with
    --no-checkout has no working tree yet: ask link_refusal() again after its checkout."""
    if remotes not in ("remove", "no-push"):
        raise ValueError(f"remotes must be 'remove' or 'no-push', not {remotes!r}")
    copy = Path(copy)
    if not os.path.lexists(copy / ".git"):
        if member:
            return (f"{copy} has no .git of its own (a member that is a folder inside another repository?); git run "
                    "in it would act on the repository that encloses the copy folder; a member copy must be a "
                    "repository of its own")
        return link_refusal(copy, run)
    why = link_refusal(copy, run) or git_identity_refusal(copy, env)
    if why:
        return why
    run = run if run is not None else copy          # INRUN: every remote and config write names this run
    why = remove_url_rewrites(copy, env, run)       # J-3: an insteadOf alias keyed to a removed remote still pushes
    if why:
        return why
    why = remove_remotes(copy, env, run) if remotes == "remove" else disable_push(copy, url, env, run)
    if why:
        return why
    why = dead_scheme_refusal(copy, env, run)   # B152 finding 1: the dead URL must start no helper either
    if why:
        return why
    # R1 clause 4: no push route git itself would resolve may remain except the kit's own dead URL (B151 finding 3:
    # an unused inherited rewrite to exactly that URL refused a member copy on the remove route)
    return push_route_refusal(copy, env, allowed=(url,), run=run)


# --- R1 clause 1(d)/(e) and clause 5: the per-packet root, its sealed stage, and where work roots may be ----------

NOT_A_REPOSITORY = "fatal: not a git repository (or any of the parent directories): .git\n"   # git, LC_ALL=C


def work_refusal(folder, avoid=()):
    """Why `folder` may not be a work root or packet base (W or PB), or None (R1 clause 5): it must lie outside every
    git repository (git, asked in it with GIT_CEILING_DIRECTORIES unset, names no top level) and must not be, hold or
    lie inside any folder in `avoid` (register members, sibling sources, framework roots)."""
    folder = Path(folder)
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATION_VARS and k != "GIT_CEILING_DIRECTORIES"}
    env.update(LC_ALL="C", LANGUAGE="")           # git's "not a git repository" is read in one language
    probe = folder
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    p = subprocess.run(["git", *READ_FLAGS, "-C", str(probe), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                       env=env)
    if p.returncode == 0:
        return f"{folder} lies inside the git repository {p.stdout.strip()}; a work root must be outside every one"
    # B162 finding 3, B163 finding 3: only git's own complete answer (exit 128 and exactly NOT_A_REPOSITORY on stderr)
    # means outside; any other failure (a malformed configuration, even one whose file name holds those words, an
    # invalid GIT_CONFIG_COUNT, a probe that is not a folder, a stop at a filesystem boundary) leaves it unanswered
    if p.returncode != 128 or p.stderr != NOT_A_REPOSITORY:
        last = (p.stderr.strip() or "no output").splitlines()[-1][:160]
        return (f"whether {folder} lies inside a git repository cannot be read (git exit {p.returncode}: {last}); a "
                "work root is accepted only when git answers that it is in none")
    for a in avoid:
        if folders_overlap(folder, a):
            return f"{folder} is, holds or lies inside {a}"
    return None


def run_folder(work, avoid=(), prefix="run-"):
    """RUN (R1 clause 1(b) and 5): a fresh folder for one run, `mkdtemp(dir=work)`, after work_refusal(work, avoid)
    (the work root lies outside every git repository and does not overlap a member, a sibling source or a framework
    root), and after env_refusal(): nothing is made while the environment holds a git location variable. Each run gets its own, so nothing a run makes is ever cleared to make room for another, and no folder
    outside the run's own is removed. A run's folder is kept after the run (its copies and clones stay readable);
    removing old ones is the operator's. Returns the folder as an absolute path; raises ContainmentRefused when the
    work root is refused or cannot be made."""
    why = env_refusal()                       # before anything is made (git would act on another repository)
    if why:
        raise ContainmentRefused(f"{why}; nothing was removed or copied")
    prefix = re.sub(r"[^\w.-]", "_", str(prefix))   # B162 finding 1: a display prefix, never a path
    work = Path(os.path.abspath(work))
    why = work_refusal(work, avoid)
    if why:
        raise ContainmentRefused(f"work root refused: {why}; nothing was made")
    try:
        work.mkdir(parents=True, exist_ok=True)
        why = work_refusal(work, avoid)           # asked again of the folder as made (a link resolves now)
        if why:
            raise ContainmentRefused(f"work root refused: {why}; nothing was made in it")
        made = Path(tempfile.mkdtemp(dir=work, prefix=prefix))
        if made.parent != work:                   # B162 finding 1: the run folder is a child of W, checked
            raise ContainmentRefused(f"the run folder {made} is not a child of the work root {work}")
        return made
    except OSError as e:
        raise ContainmentRefused(f"work root {work} cannot be used: {e}") from None


def name_refusal(name, what="the receiver name"):
    """Why `name` may not name a folder the kit makes (B162 finding 1), or None: it must be one non-empty folder name,
    not `.` or `..` and with no `/` (or NUL), so a join under a run folder stays in it. Asked before any evidence,
    copy or run folder is made for that name."""
    if not isinstance(name, str) or not name:
        return f"{what} {name!r} is not a non-empty string; nothing was made for it"
    if (name in (".", "..") or "/" in name or "\0" in name or (os.altsep and os.altsep in name)
            or Path(name).name != name):
        return f"{what} {name!r} is not a single folder name (a path, `.` or `..`); nothing was made for it"
    return None


def run_child_refusal(run, path, what="the folder"):
    """Why `path` may not be made as a part of the run folder `run`, or None (B162 finding 1): its absolute form
    must lie strictly inside `run`'s. A lexical test, asked before the folder is made; the folders it names are made
    by this run in a fresh folder."""
    r, p = os.path.abspath(run), os.path.abspath(path)
    if p == r or os.path.commonpath([r, p]) != r:
        return f"{what} {p} does not lie inside this run's folder {r}; nothing was made"
    return None


HOOK_NOT_RUN = "hook present, not run"


def materialize_hook(member, clone, name="pre-push"):
    """R1 clause 6(b) (R1-T2 (d)): the member's hook `name`, as a regular file with one name in the clone's
    `.git/hooks/`, so the hook the kit runs is a file inside the run, never one reached through a link. The entry is
    read (a read, never followed to write) at the member's common git folder; its bytes are chosen by what it is:
    - a regular file: its bytes;
    - a symbolic link whose target lies in the member's git folder: the bytes read there;
    - a symbolic link whose target lies in the member's working tree: the bytes of the same relative path in the clone
      (inside the run, at the tested commit), which must be a regular file there;
    - anything else (a link leading outside the member, a target absent from the clone, a folder): not run.
    Returns (path, None) when the hook was placed, (None, None) when the member has no such hook, and
    (None, why) when it has one that is not run; `why` begins with HOOK_NOT_RUN. The write goes through the contained
    writer, mode 0755."""
    member, clone = Path(member), Path(clone)
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATION_VARS}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    # B162 finding 6: git's answer is read byte for byte; only its line terminator is removed (no newline
    # translation, no trimming), so a folder name with a CR or trailing white space names that folder
    p = subprocess.run(["git", *READ_FLAGS, "-C", str(member), "rev-parse", "--git-common-dir"], capture_output=True, env=env)
    out = p.stdout[:-1] if p.stdout.endswith(b"\n") else p.stdout
    if p.returncode or not out:
        return None, f"{HOOK_NOT_RUN}: the member's git folder cannot be named"
    common = Path(os.fsdecode(out))
    common = common if common.is_absolute() else member / common
    entry = common / "hooks" / name
    if not os.path.lexists(entry):
        return None, None
    # B162 finding 5: the source is classified by where the entry resolves with EVERY link on the way followed (the
    # hooks folder itself may be a link), not only by whether its last component is one
    target = Path(os.path.realpath(entry))
    top, git_dir = Path(os.path.realpath(member)), Path(os.path.realpath(common))
    if target == git_dir or git_dir in target.parents:
        src = target
    elif top in target.parents:
        rel = target.relative_to(top)
        src = clone / rel
        if os.path.realpath(src) != os.path.join(os.path.realpath(clone), str(rel)):
            return None, (f"{HOOK_NOT_RUN}: {entry} leads to {rel}, which in the clone is "
                          "reached through a symbolic link")
    else:
        return None, f"{HOOK_NOT_RUN}: {entry} resolves outside the member (to {target})"
    try:
        sst = os.lstat(src)
    except OSError:
        return None, f"{HOOK_NOT_RUN}: {entry} leads to {src}, which does not exist"
    if not stat.S_ISREG(sst.st_mode):
        return None, f"{HOOK_NOT_RUN}: {entry} leads to {src}, which is not a regular file"
    try:
        contained_mkdir(clone, ".git/hooks")
        contained_write(clone, f".git/hooks/{name}", Path(src).read_bytes(), mode=0o755)
    except (OSError, ContainmentRefused) as e:
        return None, f"{HOOK_NOT_RUN}: it could not be placed in the clone: {e}"
    return clone / ".git" / "hooks" / name, None


def seal_tree(root, rel=None, root_id=None):
    """Seal the folder tree root (or root/rel, reached by the O_NOFOLLOW walk): every file and folder made not
    writable (a-w) and its manifest returned, {relative path: sha256} for files and {relative path + "/": "folder"}
    for folders. Two passes over fds opened at their parent's fd with O_NOFOLLOW (B151 finding 7: a mode change is an
    act, as for contained_seal): the first checks everything and changes nothing, refusing (ContainmentRefused) a
    symbolic link, anything but files and folders, and a file with more than one name (a hard link: the chmod would
    change the other file too); the second clears the write bits by fchmod, deepest first, each entry checked to be
    the one the first pass read. The seal is a mode bit: the same OS user can undo it; the manifest re-checked at
    every launch and after each run is the detection. Under the exclusive-mutation limit (_same_place)."""
    why = host_refusal() or (_rel_refusal(rel) if rel else None)
    if why:
        raise ContainmentRefused(why)
    where = Path(root) / rel if rel else Path(root)
    top = _walk(root, str(rel).split("/"), root_id) if rel else _open_root(root, root_id)
    manifest, ids = {}, {}
    try:
        _seal_scan(top, "", where, manifest, ids)
        _seal_apply(top, "", where, ids)
        os.fchmod(top, stat.S_IMODE(os.fstat(top).st_mode) & ~0o222)
    finally:
        os.close(top)
    return manifest


def _seal_entry(dfd, name, p, ids=None, key=None):
    """(lstat, fd) for the entry `name` at the folder fd `dfd`, opened with O_NOFOLLOW and checked to be the entry
    stat read (and, with `ids`, the one recorded at `key`); a link, a special file or a second name is refused."""
    st = os.stat(name, dir_fd=dfd, follow_symlinks=False)
    if stat.S_ISLNK(st.st_mode):
        raise ContainmentRefused(f"{p} is a symbolic link; the stage holds none")
    if stat.S_ISDIR(st.st_mode):
        fd = _open_child_dir(dfd, name, p)
    elif stat.S_ISREG(st.st_mode):
        if st.st_nlink != 1:
            raise ContainmentRefused(f"{p} has {st.st_nlink} names (a hard link); nothing was sealed")
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dfd)
    else:
        raise ContainmentRefused(f"{p} is neither a file nor a folder")
    fst = os.fstat(fd)
    if ((fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino) or (stat.S_ISREG(st.st_mode) and fst.st_nlink != 1)
            or (ids is not None and ids.get(key) != (st.st_dev, st.st_ino))):
        os.close(fd)
        raise ContainmentRefused(f"{p} changed while the stage was being sealed")
    return st, fd


def _seal_scan(dfd, prefix, where, manifest, ids):
    for name in sorted(os.listdir(dfd)):
        rel = prefix + name
        st, fd = _seal_entry(dfd, name, where / rel)
        try:
            if stat.S_ISDIR(st.st_mode):
                manifest[rel + "/"], ids[rel + "/"] = "folder", (st.st_dev, st.st_ino)
                _seal_scan(fd, rel + "/", where, manifest, ids)
            else:
                with os.fdopen(os.dup(fd), "rb") as fh:
                    manifest[rel] = hashlib.sha256(fh.read()).hexdigest()
                ids[rel] = (st.st_dev, st.st_ino)
        finally:
            os.close(fd)


def _seal_apply(dfd, prefix, where, ids):
    for name in sorted(os.listdir(dfd)):
        rel = prefix + name
        st0 = os.stat(name, dir_fd=dfd, follow_symlinks=False)
        key = rel + "/" if stat.S_ISDIR(st0.st_mode) else rel
        st, fd = _seal_entry(dfd, name, where / rel, ids, key)
        try:
            if stat.S_ISDIR(st.st_mode):
                _seal_apply(fd, key, where, ids)
            os.fchmod(fd, stat.S_IMODE(os.fstat(fd).st_mode) & ~0o222)
        finally:
            os.close(fd)


def seal_folder(root, rel=None, root_id=None):
    """Clear the write bits of the one folder root (or root/rel), at an fd reached by the O_NOFOLLOW walk. `rel` is
    checked first (B152 finding 4: `../outside` walked out of root)."""
    why = host_refusal() or (_rel_refusal(rel) if rel else None)
    if why:
        raise ContainmentRefused(why)
    fd = _walk(root, str(rel).split("/"), root_id) if rel else _open_root(root, root_id)
    try:
        os.fchmod(fd, stat.S_IMODE(os.fstat(fd).st_mode) & ~0o222)
    finally:
        os.close(fd)


def sealed_refusal(root, manifest):
    """Why the sealed tree `root` no longer matches `manifest`, or None: the same entry set, every entry not
    writable, no symbolic link, every file's digest equal."""
    root, seen = Path(root), {}
    if not root.is_dir() or root.is_symlink():
        return f"{root} is not the sealed folder"
    if os.lstat(root).st_mode & 0o222:
        return f"{root} is writable; the seal is broken"
    for folder, dirs, files in os.walk(root, followlinks=False):
        for n in dirs + files:
            p = Path(folder) / n
            st = os.lstat(p)
            rel = str(p.relative_to(root))
            if stat.S_ISLNK(st.st_mode):
                return f"{p} is a symbolic link"
            if st.st_mode & 0o222:
                return f"{p} is writable; the seal is broken"
            seen[rel + "/" if stat.S_ISDIR(st.st_mode) else rel] = (
                "folder" if stat.S_ISDIR(st.st_mode) else hashlib.sha256(p.read_bytes()).hexdigest())
    if set(seen) != set(manifest or {}):
        extra, gone = sorted(set(seen) - set(manifest or {})), sorted(set(manifest or {}) - set(seen))
        return f"the sealed entries changed: added {extra[:3]}, removed {gone[:3]}"
    bad = [rel for rel, d in seen.items() if d != manifest[rel]]
    return f"sealed files changed: {bad[:3]}" if bad else None


# --- R1 clause 4: push routes, resolved by git itself (J-3) -----------------------------------------------------

def _git(repo, env, *args):
    # B157 finding 1: bytes decoded with the file-system decoding, not text mode, whose newline translation turned a
    # carriage return in a file name into a line feed
    p = subprocess.run(["git", "--git-dir", str(Path(repo) / ".git"), *args], capture_output=True, env=env)
    return subprocess.CompletedProcess(p.args, p.returncode, os.fsdecode(p.stdout), os.fsdecode(p.stderr))


class InspectionFailed(ContainmentRefused):
    """A configuration query the isolation depends on did not run (B154 finding 2): never read as an empty answer."""


# B166 finding 2: the options and environment that keep a git read from writing the repository it reads (no optional
# lock, no lazy fetch); read_git() adds a private index. Tools that do not import this module repeat them inline.
READ_FLAGS = ("--no-optional-locks", "--no-lazy-fetch")
READ_ENV = {"GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}


# B183 finding 1: git's answer that discovery found no repository, as the WHOLE of its diagnostic (read from git
# 2.50.1: from a folder outside every repository, and when GIT_CEILING_DIRECTORIES or a filesystem boundary stops the
# search). Any other exit-128 diagnostic (a bad config file, whatever its name; a GIT_DIR or `gitdir:` naming nothing; a
# translated message) is a failed query, so the reading is unavailable, never a plain folder.
NO_REPOSITORY = re.compile(rb"fatal: not a git repository \(or any (?:of the parent directories\): \.git|parent up to "
                           rb"mount point [^\n]*\)\nStopping at filesystem boundary \(GIT_DISCOVERY_ACROSS_FILESYSTEM "
                           rb"not set\)\.)\n")


def _read_failed(args, why, text):
    """A failed read_git() result (exit 128, as git's own failures): `why` on stderr, nothing on stdout."""
    return subprocess.CompletedProcess(args, 128, "" if text else b"", why if text else os.fsencode(why))


def read_git(folder, *args, env=None, text=False, timeout=None):
    """A git read of `folder` that leaves its git folder as it was (R1-T12; B165 finding 2): no optional lock
    (`--no-optional-locks`), no lazy fetch of a missing object from a promisor remote (`--no-lazy-fetch`), and the
    index git is given is a private copy (GIT_INDEX_FILE in a temporary folder outside the repository), so a stat
    refresh git makes while reading (as `git diff` does) is written to the copy, never to the member's index.
    The copy is of the index git selects under `env` (B179 finding 4): `rev-parse --git-path index` is asked with the
    caller's GIT_INDEX_FILE still set, so a caller-selected index is the one read, not the repository's default.
    Returns the CompletedProcess (stdout bytes unless `text`). Every kit git read of a live member goes through
    this function or, in a tool that does not import this module, repeats READ_FLAGS and READ_ENV (B166 finding 2).
    `timeout` is passed to subprocess.run (TimeoutExpired propagates)."""
    run_env = dict(os.environ if env is None else env)
    run_env.update(READ_ENV)
    with tempfile.TemporaryDirectory(prefix="kit-read-") as tmp:
        # asked before the private copy replaces GIT_INDEX_FILE: git names the index it would read (B179 finding 4)
        p = subprocess.run(["git", *READ_FLAGS, "-C", str(folder), "rev-parse", "--git-path", "index"],
                           capture_output=True, env=run_env)
        if p.returncode != 0 or not p.stdout.endswith(b"\n") or len(p.stdout) < 2:
            return _read_failed(p.args, f"git did not name the index it reads in {folder} (exit {p.returncode}): "
                                f"{os.fsdecode(p.stderr).strip()[-160:]}", text)
        private = os.path.join(tmp, "index")
        real = os.fsdecode(p.stdout[:-1])            # only git's final line feed is removed (B173 finding 1)
        real = real if os.path.isabs(real) else os.path.join(str(folder), real)
        # B181 finding 2: only an ABSENT index reads as empty, as in git; one present but not a regular file, or one
        # that cannot be read, makes the read fail as git's would, never an empty successful read
        try:
            st = os.stat(real)
        except FileNotFoundError:
            st = None
        except OSError as e:
            return _read_failed(p.args, f"the index git reads, {real}, cannot be inspected: {e}", text)
        if st is not None:
            if not stat.S_ISREG(st.st_mode):
                return _read_failed(p.args, f"the index git reads, {real}, is not a regular file", text)
            try:
                shutil.copyfile(real, private)
            except OSError as e:
                return _read_failed(p.args, f"the index git reads, {real}, cannot be read: {e}", text)
        run_env["GIT_INDEX_FILE"] = private   # absent when the member has no index: git reads it as empty, as there
        return subprocess.run(["git", *READ_FLAGS, "-C", str(folder), *args],
                              capture_output=True, text=text, env=run_env, timeout=timeout)


def git_tracked(folder, path, env=None):
    """Whether git tracks `path` in the index it reads for `folder` (B183 finding 1, with FWK-OVSR5's E2i10 advisory
    (7)): True or False from a listing that succeeded (`ls-files -z -- <path>`: an entry, or none), and
    InspectionFailed when the listing failed, never "untracked". `--error-unmatch` is not used: its exit status does
    not tell an untracked path from a failed read.
    E2i12 (FWK-OVSR5's E2i11 advisory (1)): the path is literal (`--literal-pathspecs`: `:(glob)*` is a name, not a
    pattern), and only an index entry for exactly that path counts: a tracked folder lists the files under it, which
    is not an entry for the folder itself, so it reads False."""
    # C2a9 (FWK-OVSR5's E2i12 advisory (2)): a caller's glob/icase pathspec mode conflicts with --literal-pathspecs
    p = read_git(folder, "--literal-pathspecs", "ls-files", "-z", "--", path, env=_literal_env(env))
    if p.returncode:
        err = os.fsdecode(p.stderr).strip() or "no output"
        raise InspectionFailed(f"whether git tracks {path!r} in {folder} cannot be read (exit {p.returncode}: "
                               f"{err.splitlines()[-1][:120]})")
    want = os.path.normpath(os.fsdecode(path) if isinstance(path, bytes) else str(path))
    return any(os.fsdecode(e) == want for e in p.stdout.split(b"\0") if e)


REGULAR_FILE_MODES = (b"100644", b"100755")


def _literal_env(env):
    """`env` (default: this process's) without the four pathspec-mode variables, for the kit's own literal queries."""
    return {k: v for k, v in (os.environ if env is None else env).items() if k not in PATHSPEC_MODES}


def git_blob_at(folder, rev, path, env=None, with_mode=False):
    """The bytes of `path` at `rev` in `folder`, None when git lists no such entry there (absent), or InspectionFailed
    when it cannot be read (B183 finding 1, with FWK-OVSR5's E2i10 advisory (5)): `git show <rev>:<path>` fails the
    same way for an absent path and a failed read, so absence is read from `ls-tree`, which succeeds with no entry.
    With `with_mode`, return (bytes, 0755 or 0644) from the same regular-file entry, or None when absent."""
    # C2a9 (FWK-OVSR5's E2i12 advisory (1)-(2)): names relative to `folder`, as `path` is (a folder nested in its
    # repository listed top-relative names and every lookup refused); no caller pathspec mode
    try:      # C2a10 (FWK-OVSR6's E2i16 pre-read, both tools): a NUL or unencodable path is refused, never a crash
        os.fsencode(path) if not isinstance(path, bytes) else None
        if "\0" in os.fsdecode(path):
            raise ValueError("a NUL byte")
    except (ValueError, UnicodeError) as e:
        raise InspectionFailed(f"{path!r} at {rev} in {folder} is not a path git can be asked for ({e})") from None
    t = read_git(folder, "--literal-pathspecs", "ls-tree", "-z", rev, "--", path, env=_literal_env(env))
    if t.returncode:
        err = os.fsdecode(t.stderr).strip() or "no output"
        raise InspectionFailed(f"{path!r} at {rev} in {folder} cannot be listed (exit {t.returncode}: "
                               f"{err.splitlines()[-1][:120]})")
    # E2i12 (FWK-OVSR5's E2i11 advisory (2)): only a `blob` entry for exactly this path is file content; a tree
    # (`git show` prints a listing for one) or a submodule entry is not, and reads as a failed inspection
    want = os.path.normpath(os.fsdecode(path) if isinstance(path, bytes) else str(path))
    entries = []
    for e in t.stdout.split(b"\0"):
        if e:
            meta, _, name = e.partition(b"\t")
            entries.append((meta.split(b" "), os.fsdecode(name)))
    mine = [m for m, name in entries if name == want]
    if not mine:
        if entries:
            raise InspectionFailed(f"git lists {len(entries)} entr(ies) for {path!r} at {rev} in {folder}, none of "
                                   "them that path")
        return None
    # B189 finding 1: a symbolic link is stored as a blob too (mode 120000, its target as the bytes); only the two
    # regular-file modes are file content, so a committed link, tree, submodule or unknown entry is refused
    if len(mine) != 1 or len(mine[0]) != 3 or mine[0][1] != b"blob" or mine[0][0] not in REGULAR_FILE_MODES:
        kind = (f"{os.fsdecode(mine[0][1])} (mode {os.fsdecode(mine[0][0])})" if len(mine[0]) == 3 else "unknown entry")
        raise InspectionFailed(f"{path!r} at {rev} in {folder} is a {kind}, not a regular file")
    b = read_git(folder, "cat-file", "blob", os.fsdecode(mine[0][2]), env=_literal_env(env))
    if b.returncode:
        raise InspectionFailed(f"{path!r} at {rev} in {folder} is listed but cannot be read (exit {b.returncode})")
    return (b.stdout, 0o755 if mine[0][0] == b"100755" else 0o644) if with_mode else b.stdout


def git_paths(folder, *args, env=None):
    """The paths a git listing in the working tree `folder` names, read in git's NUL-separated form and decoded byte
    for byte (B158 finding 1: the newline form quotes and escapes a name holding CR, tab, LF, a quote or a backslash,
    and a reader then judged a path that does not exist). `args` is the listing (`diff --name-only …`, `ls-files …`,
    `ls-tree --name-only …`, `diff-tree --name-only …`); `-z` is added. A failed listing raises InspectionFailed,
    never reads as no paths. For `status --porcelain` use git_status_paths()."""
    p = read_git(folder, *args, "-z", env=env)        # B165 finding 2: the read leaves .git unchanged
    if p.returncode:
        err = os.fsdecode(p.stderr).strip() or "no output"
        raise InspectionFailed(f"`git {' '.join(args[:3])}` failed in {folder} (exit {p.returncode}: "
                               f"{err.splitlines()[-1][:120]}); not read as no paths")
    return [os.fsdecode(x) for x in p.stdout.split(b"\0") if x]


def git_name_status(folder, *args, env=None):
    """[(status, [paths])] from `git diff --name-status <args>`, read NUL-separated and byte for byte (B159 finding 1:
    the template-diff readers parsed the quoted newline form, so a template file named with CR, tab or LF was judged
    under a spelling no member holds). A rename or copy (status R or C) carries its old and new path; every other
    status one path. Raises InspectionFailed on a failed or unparseable listing."""
    p = subprocess.run(["git", *READ_FLAGS, "-C", str(folder), "diff", "--name-status", "-z", *args], capture_output=True, env=env)
    if p.returncode:
        raise InspectionFailed(f"`git diff --name-status` failed in {folder} (exit {p.returncode})")
    recs = [os.fsdecode(x) for x in p.stdout.split(b"\0")]
    if recs and recs[-1] == "":
        recs.pop()
    out, i = [], 0
    while i < len(recs):
        status = recs[i]
        n = 2 if status[:1] in ("R", "C") else 1
        paths = recs[i + 1:i + 1 + n]
        if not status or len(paths) != n or not all(paths):
            raise InspectionFailed(f"unparseable name-status record in {folder}: {recs[i:i + 3]!r}")
        out.append((status, paths))
        i += 1 + n
    return out


def git_status_paths(folder, env=None):
    """The paths `git status --porcelain` names (changed or untracked), from its NUL-separated form: each record is
    `XY <path>`, and a rename or copy (X or Y in R/C) is followed by a record holding the source path, which is
    named too (B158 finding 1). Untracked files are listed one by one (`--untracked-files=all`), never as their
    folder, so B1's `pre_dirty` and every path-by-path consumer read one population (B159 finding 2). Raises
    InspectionFailed on a failed or unparseable listing."""
    p = read_git(folder, "status", "--porcelain", "-z", "--untracked-files=all", env=env)   # R1-T12, B165 #2
    if p.returncode:
        raise InspectionFailed(f"`git status --porcelain` failed in {folder} (exit {p.returncode})")
    recs = [os.fsdecode(x) for x in p.stdout.split(b"\0")]
    if recs and recs[-1] == "":
        recs.pop()
    out, i = [], 0
    while i < len(recs):
        r = recs[i]
        if len(r) < 4 or r[2] != " ":
            raise InspectionFailed(f"unparseable status record in {folder}: {r!r}")
        out.append(r[3:])
        if "R" in r[:2] or "C" in r[:2]:
            i += 1
            if i >= len(recs):
                raise InspectionFailed(f"a rename record in {folder} has no source path")
            out.append(recs[i])
        i += 1
    return out


def _query(repo, env, *args, nomatch=True):
    """stdout of a mandatory git query, or InspectionFailed. With `nomatch`, exit 1 is git's "no such key / no match"
    for `config --get` and `--get-regexp` (an empty answer); any other non-zero exit is a failure."""
    p = _git(repo, env, *args)
    if p.returncode == 0 or (nomatch and p.returncode == 1 and not p.stderr.strip()):
        return p.stdout if p.returncode == 0 else ""
    raise InspectionFailed(f"`git {' '.join(args[:4])}` failed in {repo} (exit {p.returncode}: "
                           f"{(p.stderr.strip() or 'no output').splitlines()[-1][:120]}); not read as an empty answer")


def remove_url_rewrites(repo, env=None, run=None):
    """Delete every `url.<base>` section from the copy's own config (insteadOf / pushInsteadOf rules copied from the
    member), after INRUN (inrun_refusal()). Returns None, or the reason one could not be removed."""
    env = dict(os.environ) if env is None else env
    why = inrun_refusal(repo, run, env)
    if why:
        return why
    try:
        out = _query(repo, env, "config", "--local", "--name-only", "--get-regexp", r"^url\.")
    except InspectionFailed as e:
        return str(e)
    for name in sorted({ln.rsplit(".", 1)[0] for ln in out.splitlines() if ln.strip()}):
        if _git(repo, env, "config", "--local", "--remove-section", name).returncode:
            return f"could not remove the URL rewrite section {name!r}"
    return None


def push_routes(repo, env=None, run=None):
    """{candidate: [resolved push URLs]} for every name git could push to from `repo` under `env`: each remote, each
    legacy remote file, every value of a `url.*.insteadOf` / `pushInsteadOf` rule (local or inherited), and
    `remote.pushDefault`. Each is resolved by git as a push destination: a remote with `remote get-url --push --all`,
    any other candidate through a short-lived probe remote (_push_urls_of(); B156 finding 1)."""
    env = dict(os.environ) if env is None else env
    remotes = set(_query(repo, env, "remote", nomatch=False).split())   # B154 finding 2: a failed query raises
    names = set(remotes) | {p.name for p in legacy_remote_files(Path(repo) / ".git")}
    rules = _query(repo, env, "config", "--get-regexp", r"^url\..*\.(insteadof|pushinsteadof)$")
    names |= {ln.split(None, 1)[1].strip() for ln in rules.splitlines() if len(ln.split(None, 1)) == 2}
    pd = _query(repo, env, "config", "--get", "remote.pushdefault").strip()
    if pd:
        names.add(pd)
    out = {}
    for n in sorted(names):
        # B155 finding 2: a failed or empty resolution raises (InspectionFailed); it is never replaced by the raw
        # candidate, which could equal the allowed dead URL while a rewrite redirects it
        if n in remotes:
            urls = _query(repo, env, "remote", "get-url", "--push", "--all", n, nomatch=False).split()
        else:
            urls = _push_urls_of(repo, env, n, run)   # B156 finding 1: as a push destination, not a fetch URL
        if not all(urls) or not urls:
            raise InspectionFailed(f"git resolved no push URL for {n!r} in {repo}; not read as the name itself")
        out[n] = urls
    return out


STATE_CONDITIONS = ("onbranch:", "hasconfig:")   # includeIf conditions whose truth can change after isolation


def include_refusal(repo, env=None):
    """Why configuration git reads for `repo` holds an include that could become active, or change what it says,
    after isolation; None otherwise (B154 finding 1: a dormant `includeIf "onbranch:…"` carried a URL rewrite that a
    checkout activated, redirecting `origin`). Git's includeIf conditions are gitdir, gitdir/i, onbranch and
    hasconfig:remote.*.url; gitdir is fixed for a copy that does not move, while onbranch follows HEAD and hasconfig
    follows configuration. Refused, at any scope: (a) an includeIf with an onbranch or hasconfig condition; (b) an
    include whose target file lies inside the copy (a checkout can change it); (c) any include in configuration git
    reads after the copy's own file (worktree, environment, command line: B153 finding 1). Admitted: unconditional
    and gitdir includes outside the copy, at system, global or local scope; they are active now, so the route check
    sees what they say. Raises InspectionFailed when the query cannot run."""
    env = dict(os.environ) if env is None else env
    # B156 finding 3: the NUL-separated form (`-z`) gives the origin's file name unquoted; the display form quotes and
    # escapes unusual names. Records: scope NUL origin NUL key LF value NUL.
    out = _query(repo, env, "config", "-z", "--show-scope", "--show-origin", "--get-regexp", r"^include(if)?\.")
    copy = Path(repo).resolve()
    fields = out.split("\0")   # B157 finding 1: _git decodes bytes faithfully, so file names come through intact
    if fields and fields[-1] == "":
        fields.pop()
    if len(fields) % 3:
        raise InspectionFailed(f"unreadable include listing in {repo} ({len(fields)} fields)")
    for i in range(0, len(fields), 3):
        scope, origin, entry = fields[i], fields[i + 1], fields[i + 2]
        key, sep, value = entry.partition("\n")
        if not sep:
            raise InspectionFailed(f"unreadable include entry in {repo}: {entry!r}")
        where = f"{scope} configuration ({origin.removeprefix('file:')}): `{key} = {value}`"
        cond = key[len("includeif."):].rsplit(".", 1)[0] if key.startswith("includeif.") else ""
        if scope in ("worktree", "command"):
            return (f"{where} is read after {repo}'s own config and includes another file, which could reopen the "
                    f"{DEAD_SCHEME} scheme or redirect a remote; remove it from that configuration for the run")
        if cond.startswith(STATE_CONDITIONS):
            return (f"{where} is a conditional include whose condition can change after isolation (a checkout or a "
                    "configuration change), so what it says could redirect a remote later; the kit refuses such "
                    "includes at any scope. Move the include out of that file for the run, or use a `gitdir:` "
                    "condition instead")
        # B155 finding 1, B156 finding 2: `~` is expanded as git does it, with the HOME in `env` (an empty HOME gives
        # "/…"); with no HOME in `env` git cannot expand it, so it is refused rather than guessed
        if value == "~" or value.startswith("~/"):
            if "HOME" not in env:
                return f"{where} uses `~` but git runs with no HOME, so the file it names cannot be resolved"
            target = Path(env["HOME"] + value[1:])
        else:
            target = Path(os.path.expanduser(value) if value.startswith("~") else value)   # ~user: that user's home
        if not target.is_absolute():
            if not origin.startswith("file:"):
                return f"{where} is a relative include with no file of origin, so the file it names cannot be resolved"
            target = Path(origin.removeprefix("file:")).parent / target
        target = target.resolve()
        if target == copy or copy in target.parents:
            return (f"{where} includes a file inside the copy ({target}); a checkout can change what it says. "
                    "Move the included file outside the repository")
    return None


DEAD_SCHEME = "no-push"   # the scheme of every dead push URL the kit sets (this module's, after_run_check's, suite_at_commit's)


def dead_scheme_refusal(repo, env=None, run=None):
    """Make the dead URL's scheme unusable from `repo`, or say why it cannot be (B152 finding 1: with a
    `git-remote-no-push` on PATH, a push to a remote whose push URL is `no-push://…` started that helper and exited 0).
    Writes `protocol.no-push.allow = never` into the copy's own config and reads the value git will use back under
    `env`: a command-line or environment config entry that overrides it is a refusal, and so is a `GIT_ALLOW_PROTOCOL`
    in `env` that names the scheme (git ignores protocol.<name>.allow when that variable is set). The entry is the last
    one in the local file, and an include in configuration read after that file is a refusal (B153 finding 1).
    Includes whose truth or content can change later are include_refusal()'s; the routes are read again after each
    kit checkout (checked_out_refusal()). Stated limit (point in time): a change to HEAD or configuration that code
    running in the copy makes afterwards, and a change another process makes to an included file outside the copy,
    are not closed. Only this scheme is
    closed: transports to other destinations are left as they were (the suite check at the commit runs a member's
    local clone, fetch and push tests outside the sessions); routes resolving elsewhere are push_route_refusal()'s."""
    env = dict(os.environ) if env is None else env
    why = inrun_refusal(repo, run, env)               # INRUN: a config write, in a copy inside this run only
    if why:
        return why
    key = f"protocol.{DEAD_SCHEME}.allow"
    # B153 finding 1: the entry is written LAST in the copy's own config. Setting an existing entry in place left it
    # before a dormant `includeIf "onbranch:…"`, which a later checkout activated. Every earlier section is removed and
    # a new one appended, so anything the local file includes before it is overridden.
    for _ in range(64):
        if _git(repo, env, "config", "--local", "--remove-section", f"protocol.{DEAD_SCHEME}").returncode:
            break
    if _git(repo, env, "config", "--local", key, "never").returncode:
        return f"could not close the {DEAD_SCHEME} scheme in {repo}'s own config"
    try:
        listed = _query(repo, env, "config", "--local", "--no-includes", "--list", nomatch=False).splitlines()
        if not listed or listed[-1] != f"{key}=never" or sum(ln.startswith(key + "=") for ln in listed) != 1:
            return f"{key} = never is not the one and last entry of {repo}'s own config"
        why = include_refusal(repo, env)   # B154 finding 1 (and B153's later-scope refusal, folded in)
        if why:
            return why
        used = _query(repo, env, "config", "--get", key).strip()
    except InspectionFailed as e:          # B154 finding 2
        return str(e)
    if used != "never":
        return (f"protocol.{DEAD_SCHEME}.allow as git would use it in {repo} is {used or 'unset'}, "
                "not never (overridden by configuration from the environment or the command line)")
    allow = env.get("GIT_ALLOW_PROTOCOL")
    if allow is not None and DEAD_SCHEME in allow.split(":"):
        return f"GIT_ALLOW_PROTOCOL in the environment names {DEAD_SCHEME!r}, which overrides the copy's config"
    return None


def checked_out_refusal(copy, run=None, url=NO_PUSH_URL, env=None):
    """After a checkout the kit makes in an isolated copy: LINKS again, and the push routes and the dead scheme read
    back again (B154 finding 1 (c): the checkout is when a branch-dependent configuration would change). None when
    nothing changed, else the reason."""
    why = link_refusal(copy, run)
    if why:
        return why
    if not os.path.lexists(Path(copy) / ".git"):
        return None
    env = dict(os.environ) if env is None else env
    try:
        used = _query(copy, env, "config", "--get", f"protocol.{DEAD_SCHEME}.allow").strip()
        why = include_refusal(copy, env)
    except InspectionFailed as e:
        return str(e)
    if why:
        return why
    if used != "never":
        return f"after the checkout, protocol.{DEAD_SCHEME}.allow in {copy} reads {used or 'unset'}, not never"
    return push_route_refusal(copy, env, allowed=(url,), run=run if run is not None else copy)


def _push_urls_of(repo, env, candidate, run=None):
    """The push URLs git would use for `candidate` (a URL or alias that is not a remote's name), by git's own push
    resolution: a short-lived remote holding it is added to the copy's own config, read with `remote get-url --push
    --all` (so `pushInsteadOf`, then `insteadOf`, apply as for a push), and removed (B156 finding 1: `ls-remote
    --get-url` resolves the fetch URL and missed a push-only rewrite of the dead URL). A remote defined on the command
    line is not one git will read here, hence the copy's file. Raises InspectionFailed when any step fails; a probe
    that cannot be removed is a failure too."""
    # B165 finding 1: the probe writes the copy's own config, so it asks INRUN first (a run folder holding the
    # repository, and git's current identity, which refuses a .git entry linked outside the copy): never a write
    # through a link that member code made after isolation
    why = inrun_refusal(repo, run, env)
    if why:
        raise InspectionFailed(f"the route probe was not added: {why}")
    # B157 finding 2: the name must be vacant at every scope, the section the probe reads must hold only its url, and
    # only a section the probe created is removed
    for _ in range(16):
        name = f"kit-route-probe-{secrets.token_hex(4)}"
        if not _query(repo, env, "config", "--get-regexp", rf"^remote\.{name}\."):
            break
    else:
        raise InspectionFailed(f"no vacant route-probe remote name in {repo}; nothing was added")
    if _git(repo, env, "config", "--local", f"remote.{name}.url", candidate).returncode:
        raise InspectionFailed(f"could not resolve {candidate!r} as a push destination in {repo}")
    try:
        held = _query(repo, env, "config", "--get-regexp", rf"^remote\.{name}\.").splitlines()
        if held != [f"remote.{name}.url {candidate}"]:
            raise InspectionFailed(f"the route probe {name!r} in {repo} holds more than its url ({held[:3]})")
        return _query(repo, env, "remote", "get-url", "--push", "--all", name, nomatch=False).split()
    finally:
        if _git(repo, env, "config", "--local", "--remove-section", f"remote.{name}").returncode:
            raise InspectionFailed(f"could not remove the route probe {name!r} from {repo}'s own config")


def push_route_refusal(repo, env=None, allowed=(), run=None):
    """Why git could push from `repo` somewhere other than `allowed`, or None (R1 clause 4: a copy's routes, on
    either isolation route, may resolve only to the unresolvable push URL)."""
    try:
        routes = push_routes(repo, env, run)
    except InspectionFailed as e:
        return str(e)
    bad = {n: urls for n, urls in routes.items() if any(u not in allowed for u in urls)}
    if bad:
        return f"git can still push from {repo} by {sorted(bad)} (resolved to {sorted({u for v in bad.values() for u in v})[:3]})"
    return None


# --- IGN: git's ignore state (R1 clause 8; H-3, R1-T9; E2i) ---------------------------------------------------------
# The tree reads IGN makes: no fsmonitor hook and no untracked cache, so git answers from the files themselves.
IGN_GIT = ("-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false")
PATHSPEC_MODES = ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS")
UNREADABLE = "unreadable"
# C2a10 (FWK-OVSR6's E2i16 pre-read 1-2, reproduced): every spelling the kit's readers give for a reading that was not
# taken. A non-reading equals nothing, itself included: any comparison that meets one is INCONCLUSIVE, never unchanged
NON_READINGS = ("unreachable", "unreadable", "unread", "not a regular file")


def non_reading(v):
    """Whether a reading (a string any kit reader returned) is a reading that was not taken."""
    return isinstance(v, str) and v.lower().startswith(NON_READINGS)


def _ign_git(repo, env, *args):
    """A git read for IGN in `repo` under `env` (READ_FLAGS: no optional lock, no lazy fetch; no fsmonitor, no
    untracked cache); bytes out. B177 finding 1: without GIT_CONFIG, which only `git config` honours (it makes that
    command read another file), so IGN's configuration queries describe the scope ordinary git commands read."""
    run_env = dict(env)
    run_env.pop("GIT_CONFIG", None)
    run_env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(["git", *READ_FLAGS, "-C", str(repo), *IGN_GIT, *args], capture_output=True,
                          env=run_env)


def _file_print(path):
    """A file's IGN reading: sha256 of its bytes, `absent`, `link:<target>` for a symbolic link that is itself the
    element (a `.gitignore`), the kind for anything that is not a regular file (never opened: a FIFO would block),
    or `unreadable`."""
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return "absent"
    except OSError:
        return UNREADABLE
    if not stat.S_ISREG(st.st_mode):
        return f"not a regular file (mode {stat.S_IFMT(st.st_mode):o})"
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return UNREADABLE


def _git_name(repo, env, *args):
    """The one name a git query prints, byte for byte (B173 finding 1): git ends it with a single line feed, and only
    that line feed is removed, so a name holding a line feed, carriage return, tab or space keeps it. None when the
    query fails or prints no name. One query per name: a newline-delimited list of several names cannot be split back
    into names that may themselves hold a line feed."""
    p = _ign_git(repo, env, *args)
    if p.returncode != 0 or len(p.stdout) < 2 or not p.stdout.endswith(b"\n"):
        return None
    return os.fsdecode(p.stdout[:-1])


def _include_target(repo, env, includer, value):
    """The file an include directive `value`, found in the configuration file `includer`, names, as git resolves it
    (B175 finding 1): its `~`, `~user` and `%(prefix)` forms expanded by git itself (`config --type=path` on the value),
    and a relative result joined to the folder of the including file (itself anchored as git reads it). None when git
    cannot expand it, or when a relative value has no including file (process configuration, B176: git refuses a
    relative include there)."""
    expanded = _git_name(repo, env, "-c", f"aget.ign-include={value}", "config", "--type=path", "--get",
                         "aget.ign-include")
    if not expanded:
        return None
    if os.path.isabs(expanded):
        return expanded
    if includer is None:
        return None
    return os.path.join(os.path.dirname(_as_git_reads(includer, repo)), expanded)


def _as_git_reads(path, repo):
    """`path` as git reads it when run with `-C repo`: a relative name (from a relative HOME or XDG_CONFIG_HOME, or one
    `git rev-parse --git-path`, `git var`, `git config --type=path` or `--show-origin` returns) is relative to `repo`,
    not to this process's working folder (B172 finding 1). None stays None."""
    return path if path is None or os.path.isabs(path) else os.path.join(str(repo), path)


def _git_file_print(name, repo):
    """The one reader for every file IGN reads by a name git uses (elements (ii)-(v)): `name` is anchored as git reads
    it (_as_git_reads) and then read (_file_print). Returns (anchored path, reading). No IGN file is read by any other
    route, so no producer of a name can skip the anchoring (B172 finding 1, by class)."""
    path = _as_git_reads(name, repo)
    return path, _file_print(path)


def _named_file_reading(named, repo):
    """The reading of a file a setting names, with its path as git reads it: `<path>: <reading>`, except that an
    unreadable file reads `unreadable: <path>`, so the marker stays at the front and ignore_changes() reports it
    (B171 finding 2)."""
    path, v = _git_file_print(named, repo)
    return f"{UNREADABLE}: {path} ({v})" if non_reading(v) else f"{path}: {v}"   # C2a11: every non-reading


def ignore_state(repo, env=None, also=()):
    """IGN (R1 clause 8; H-3, R1-T9): git's ignore state for the working tree `repo`, as {element: reading}, read
    under `env` (default: this process's environment, the one the kit's own tree checks run git under) and under each
    further (label, environment) pair in `also` (the environment the suite, hook, auditor or session ran under). An
    element that reads differently under a further environment is kept again with ` (<label>)` after its name; the
    `core.excludesFile` elements always are. See ignore_state_one() for the five elements."""
    out = ignore_state_one(repo, env)
    for label, e in also:
        for k, v in ignore_state_one(repo, e).items():
            if k.startswith("core.excludesFile") or (k in out and out[k] != v):
                out[f"{k} ({label})"] = v
            else:
                out.setdefault(k, v)
    return out


def ignore_state_one(repo, env=None):
    """git's ignore state for the working tree `repo` as git reads it under one environment `env` (default: this
    process's), as {element: reading}. Five elements:
    (i) every `.gitignore` in the working tree git uses (B179 finding 5: the one `rev-parse --show-toplevel` names
    under `env`, so a GIT_WORK_TREE or core.worktree that selects another tree is the tree walked, and the selection
    is itself an element), tracked, untracked or itself ignored, found by a walk that does not consult git beyond that
    question, does not enter `.git` and does not follow links (a `.gitignore` that is a link reads as its target);
    (ii) the bytes of `<git folder>/info/exclude`; (iii) `core.excludesFile`'s values with their origins, and the bytes
    of the file the last names, or, unset, of `$XDG_CONFIG_HOME/git/ignore` (`$HOME/.config/git/ignore` when
    XDG_CONFIG_HOME is unset); (iv) the bytes of every configuration file git reads under `env`: the repository's
    `config` and `config.worktree`, the global files and the system file as `git var` names them (or git's answer
    that it reads none), and every file `git config --list --show-origin` names (includes among them), so a
    `core.excludesFile`, `core.fsmonitor`, `core.untrackedCache` or `status.showUntrackedFiles` set during a run is
    seen; (v) the index flags (`git ls-files -v`: the paths marked assume-unchanged or skip-worktree) and the bytes of
    `<git folder>/info/sparse-checkout`. A reading that cannot be made is `unreadable`, never left out. A folder git
    names no repository for under `env` has element (i) and `repository: none` only (B181 finding 1: git's answer,
    not a local `.git` entry; GIT_DIR and discovery in an ancestor count); no answer reads `repository: unreadable`.
    A file reads as sha256, `absent`, a kind, or `unreadable`; ignore_changes() compares two states."""
    repo = Path(os.path.abspath(repo))
    env = dict(os.environ if env is None else env)
    out, walk_errors = {}, []
    # (i) B179 finding 5: the working tree walked is the one git uses, asked of git under `env`; a folder with no
    # `.git` entry has no git to ask and is its own tree
    # B181 finding 1: whether `repo` is a repository, and which, is git's answer under `env` (GIT_DIR, discovery in an
    # ancestor), never the presence of a local `.git` entry; a question git cannot answer is unavailable
    q = _ign_git(repo, env, "rev-parse", "--absolute-git-dir")
    if q.returncode == 0 and len(q.stdout) > 1 and q.stdout.endswith(b"\n"):
        is_repo = True
    elif q.returncode == 128 and NO_REPOSITORY.fullmatch(q.stderr):
        is_repo = False                 # B183 finding 1: git's whole answer is its discovery message, nothing else
    else:
        is_repo = None
        out["repository"] = (f"{UNREADABLE}: git did not say whether {repo} is a repository "
                             f"(exit {q.returncode})")
    tree = repo if is_repo is not None else None
    if is_repo:
        top = _git_name(repo, env, "rev-parse", "--show-toplevel")
        if top is None:
            tree = None
            out[".gitignore (working tree)"] = f"{UNREADABLE}: git did not name the working tree it uses"
        elif not same_folder(_as_git_reads(top, repo), repo):
            tree = Path(_as_git_reads(top, repo))
            out[".gitignore (working tree)"] = f"selected by git: {tree}"
    for parent, dirs, files in (os.walk(tree, followlinks=False, onerror=walk_errors.append) if tree else ()):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        rel = Path(parent).relative_to(tree).as_posix()
        p = Path(parent) / ".gitignore"
        if os.path.lexists(p):
            key = f".gitignore {'' if rel == '.' else rel + '/'}.gitignore"
            out[key] = f"link:{os.readlink(p)}" if p.is_symlink() else _file_print(p)
    if walk_errors:
        out[".gitignore (walk)"] = f"{UNREADABLE}: {walk_errors[0]}"
    if not is_repo:
        # a plain folder (a copied sibling with no .git), as git answers: no git rule applies to it; a repository made
        # or selected by the run changes this element, so it is still seen
        if is_repo is False:
            out["repository"] = "none: git names no repository"
        return out
    # (ii), (iv) repository files, (v) sparse-checkout: the paths git uses for this repository
    # B173 finding 1: one query per name, read byte for byte (never one newline-split listing of four)
    lines = [_git_name(repo, env, "rev-parse", "--git-path", x)
             for x in ("info/exclude", "info/sparse-checkout", "config", "config.worktree")]
    if all(lines):
        exclude, sparse, cfg, wcfg = lines        # as git returned them; read through _git_file_print only
        out["info/exclude"] = _git_file_print(exclude, repo)[1]
        out["info/sparse-checkout"] = _git_file_print(sparse, repo)[1]
        files = {cfg, wcfg}
    else:
        out["info/exclude"] = out["info/sparse-checkout"] = UNREADABLE
        files = set()
        out["config file (repository)"] = UNREADABLE
    # (iii)
    p = _ign_git(repo, env, "config", "--show-origin", "-z", "--get-all", "core.excludesFile")
    if p.returncode == 0:
        parts = [os.fsdecode(x) for x in p.stdout.split(b"\0")][:-1]
        out["core.excludesFile"] = "|".join(parts)
        # B171 finding 1: the file is the one git resolves (`~/`, `~user/`, `%(prefix)/` and the rest), asked of git
        # itself under this environment, never a reading of the value's spelling here
        q = _ign_git(repo, env, "config", "--type=path", "-z", "--get", "core.excludesFile")
        named = os.fsdecode(q.stdout).split("\0")[0] if q.returncode == 0 and q.stdout else None
        # B186 finding 1: git opens a relative name from the top of the working tree it selected (it moves there
        # before reading ignore rules), not from a nested folder the caller named; with no tree named, unavailable
        out["core.excludesFile file"] = (_named_file_reading(named, tree) if named and (tree or os.path.isabs(named))
                                         else UNREADABLE)
    elif p.returncode == 1 and not p.stdout:            # unset: git reads its default ignore file
        out["core.excludesFile"] = "unset"
        xdg, home = env.get("XDG_CONFIG_HOME"), env.get("HOME")
        named = (os.path.join(xdg, "git", "ignore") if xdg else
                 os.path.join(home, ".config", "git", "ignore") if home else None)
        # B186 finding 1: a relative default (a relative XDG_CONFIG_HOME or HOME) is read from the selected tree's top
        out["core.excludesFile file"] = (("no default (no HOME)" if not named else
                                          _named_file_reading(named, tree) if tree or os.path.isabs(named)
                                          else UNREADABLE))
    else:
        out["core.excludesFile"] = out["core.excludesFile file"] = UNREADABLE
    # (iv) the global and system files, and every file the configuration listing names
    # B174 finding 1: whether git reads a global or system file is git's answer, never the kit's reading of git's
    # environment (GIT_CONFIG_NOSYSTEM is a git boolean: `0`, `false`, `no`, `off` still read the system file). `git
    # var` is always asked; it exits 1 with no output when git reads no such file (read from git 2.50.1:
    # GIT_CONFIG_NOSYSTEM=1, or GIT_CONFIG_GLOBAL empty), and that answer is itself an element, so a run that changes it
    # is seen. B173 finding 1: names recovered byte for byte, or the element reads unavailable.
    for scope in ("global", "system"):
        p = _ign_git(repo, env, "var", f"GIT_CONFIG_{scope.upper()}")
        if p.returncode == 1 and not p.stdout:
            out[f"config file ({scope})"] = "none: git reads no such file"
        elif p.returncode != 0 or len(p.stdout) < 2 or not p.stdout.endswith(b"\n"):
            out[f"config file ({scope})"] = UNREADABLE
        elif scope == "system" or "GIT_CONFIG_GLOBAL" in env:
            # one file: the system file, or the one GIT_CONFIG_GLOBAL names; only git's final line feed is removed
            files.add(os.fsdecode(p.stdout[:-1]))
        elif any("\n" in env.get(k, "") for k in ("HOME", "XDG_CONFIG_HOME")):
            # unset GIT_CONFIG_GLOBAL: git lists the XDG (or HOME) file and HOME's, one per line; split back into names
            # only when neither variable, their only source, holds a line feed
            out["config file (global)"] = (f"{UNREADABLE}: HOME or XDG_CONFIG_HOME holds a line feed, so the names "
                                           "git lists one per line cannot be told apart")
        else:
            files |= {x for x in os.fsdecode(p.stdout).split("\n") if x}
    p = _ign_git(repo, env, "config", "--list", "--show-origin", "-z")
    if p.returncode == 0:
        tokens = p.stdout.split(b"\0")
        # B176 finding 1, by construction: no entry is passed over. A `file:` origin is read; an include directive's
        # target is read whatever its origin (B175: a file an include names is read by git even when it emits no
        # setting, and then has no origin of its own); an origin of any other kind cannot be fingerprinted and reads
        # unavailable
        for origin, entry in zip(tokens[0:-1:2], tokens[1::2]):
            o = os.fsdecode(origin)
            includer = o[len("file:"):] if o.startswith("file:") else None
            if includer is not None:
                files.add(includer)
            elif o != "command line:":
                out[f"config origin {o!r}"] = f"{UNREADABLE}: an origin IGN cannot read"
            key, _, value = os.fsdecode(entry).partition("\n")
            k = key.lower()
            if k == "include.path" or (k.startswith("includeif.") and k.endswith(".path")):
                target = _include_target(repo, env, includer, value)
                if target:
                    files.add(target)
                else:
                    out[f"config include {value!r} from {includer or o}"] = UNREADABLE
    else:
        out["config file (listing)"] = UNREADABLE
    for path, v in sorted(_git_file_print(f, repo) for f in files):
        out[f"config file {path}"] = v
    # (v) index flags, read from the index git selects (read_git). B181 finding 2 by construction: the index file git
    # names is itself an element (git's answer, never a reading of GIT_INDEX_FILE here), so a switch of index between
    # readings is seen even when the two hold the same flags; read_git fails, never reads empty, for an index that is
    # present but not a regular readable file
    named = _git_name(repo, env, "rev-parse", "--git-path", "index")
    out["index file"] = _as_git_reads(named, repo) if named else UNREADABLE
    # B186 finding 2: the whole working tree git selected, so a flag outside a nested supplied folder is in the
    # population (`ls-files` run in a subfolder lists only that subfolder): git's own `:(top)` pathspec, names in full.
    # The query runs in `repo` (a tree selected by GIT_WORK_TREE or core.worktree holds no repository to discover),
    # and without the caller's pathspec-mode variables, which would make `:(top)` a literal name and list nothing
    fenv = {k: v for k, v in env.items() if k not in PATHSPEC_MODES}
    p = read_git(repo, *IGN_GIT, "ls-files", "-v", "-z", "--full-name", "--", ":(top)", env=fenv)
    if p.returncode == 0:
        flagged = sorted(os.fsdecode(e) for e in p.stdout.split(b"\0") if e and (e[:1] == b"S" or e[:1].islower()))
        out["index flags"] = f"{len(flagged)}: " + hashlib.sha256("\0".join(flagged).encode()).hexdigest()
    else:
        out["index flags"] = UNREADABLE
    return out


IGN_CACHE_DIRS = ("__pycache__", ".pytest_cache")   # caches, as suite_at_commit.CACHE_DIRS


def ignored_paths(repo, env=None):
    """The paths git ignores in the working tree `repo` (`ls-files --others --ignored --exclude-standard
    --directory`, NUL-separated, read without writing .git), less those under a cache folder (IGN_CACHE_DIRS): R1
    clause 8's ignored-path set. Raises InspectionFailed when git cannot list them."""
    paths = git_paths(repo, *IGN_GIT, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory",
                      env=env)
    return sorted(p for p in paths if not set(p.rstrip("/").split("/")) & set(IGN_CACHE_DIRS))


def ignore_changes(before, after, recorded=()):
    """The IGN elements to report between two ignore_state() readings, as (changed, unreadable): an element added,
    removed or read differently, and one unreadable in either reading. An element named in `recorded` (a path the
    step's write set names, R1 clause 8's one exception) is left out of `changed`; its caller judges the ignored
    paths instead."""
    unreadable = sorted(k for k in set(before) | set(after)
                        if non_reading(str(before.get(k, ""))) or non_reading(str(after.get(k, ""))))   # pre-read 6
    changed = sorted(k for k in set(before) | set(after)
                     if before.get(k) != after.get(k) and k not in unreadable and k not in recorded)
    return changed, unreadable


def ignore_refusal(before, after, who):
    """Why a result from `who` (a suite, hook or auditor run) cannot count, or None (R1 clause 8): the ignore state
    read immediately before it differs from the one read immediately after it, or an element could not be read.
    The reason names the elements. Either reading None (not taken) is a reason too."""
    if before is None or after is None:
        return f"git's ignore state was not read around {who}, so a write it hid cannot be ruled out"
    changed, unreadable = ignore_changes(before, after)
    if not changed and not unreadable:
        return None
    parts = []
    if changed:
        parts.append(f"{who} changed git's ignore state: {changed[:5]}")
    if unreadable:
        parts.append(f"git's ignore state could not be read around {who}: {unreadable[:5]}")
    return "; ".join(parts) + " (a write an ignore rule hides would not be seen)"
