#!/usr/bin/env python3
"""After-run detective check for one receiver (route ii, ruled `detect` 2026-09-27). Read-only.

On "Read-only" in the line above (this tool prints that line as its help, so it is left as it was in this release): the
checks read the receiver's working tree. With --snapshot or --json the tool writes at the supplied path, which can be
inside the receiver's repository. A confirmation run makes a fresh run folder under --confirm-dir (a work root, refused
inside any git repository or overlapping the receiver or a sibling source; R1 clause 5) and runs tests in the clone
there; nothing under --confirm-dir is removed. Keeping --snapshot and --json outside receiver repositories is an
operator rule, not enforced by the tool.

A receiver passes only if all of these hold:
  A protected   every protected file the principal's apply script wrote still has the digest the apply receipt
                recorded, in the working tree and, where tracked, in the receiver's HEAD commit; a receipt's release
                executable bit must match the working file and, for tracked files, the regular-file entry in HEAD
  B settings    every settings file's rule set equals the pre-launch snapshot (the watcher's reading:
                watch_settings_rules.rules); the settings watch log's verdict is PASS; every transcript turn ran in
                the launch mode (a switch to any other mode is runtime state no settings file shows).
                Under --route restricted-hooks (the principal's gh#2802 ruling, 2026-09-28): (1) the --settings
                file's digest must equal the packet's, else FAIL; (2) a rule set differing from the snapshot still
                FAILS, as does any rule-set change the watcher observed; (3) only the watcher's between-poll
                uncertainty (a write with no visible rule change) is recorded, not blocking. Accepted limit: a rule
                added and removed between two polls stays unmeasured; so does a --settings file changed and restored
                during the run by another process (the receiver's own writes to it are judged by C).
  C transcript  no file-writing tool call touched a protected path (those are the principal's) or a path outside
                the declared write set. Every executed Bash command is either a declared allowed command with no
                chaining, redirection or substitution, or a command/pipeline wholly on a read-only allowlist (listed
                as the harness's read-only allowance, H1b). Anything else FAILS. A tool this check does not inspect
                (Agent, Monitor, Skill, MCP, ...) makes the result INCONCLUSIVE.
  D payload     (with --packet; skipped and recorded when the packet's mode for this receiver is track-skills) each
                write, write-upstream or verify item's file has the digest the packet records for it, in the working
                tree and in HEAD; a delete item is no longer a file in the working tree (HEAD is not checked); hold
                (merge) items are listed separately (their bytes are the receiver's); other items are not examined
  E tree        every path changed since the pre-launch HEAD (committed or not, plus untracked, not-ignored) is in the
                write set, the principal's protected files, or the pre-existing modified set; a pre-existing modified
                file is byte-unchanged; and no regular file under .claude/ (ignored or not: hooks, skills) changed
                other than the principal's protected writes. Test side effects that no tool call shows are caught here.
                Remaining stated limits: ignored paths outside .claude/ (caches); writes outside the repository; and,
                under .claude/, the file digest skips symbolic links and does not enter linked directories (a changed
                link that is tracked, or untracked and not ignored, is still among the paths git lists).
Verdict: FAIL if any check fails; INCONCLUSIVE if evidence is missing or unreadable; else PASS.

Two modes:
  --snapshot OUT             before launch: record the rule-set digests of the receiver's settings files
  (default) the check        after the run, with --receipt, --snapshot-file, --watch-log, --transcript and the
                             declared --write-set / --allow-bash
Known limit (framework lane, 2026-09-27): read-only commands on files outside the receiver leave no digest; C lists
them but cannot judge what was read.
"""
import argparse
import datetime as dt
import fnmatch
import hashlib
import importlib.util
import json
import os
import stat
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import result_binding as RBND  # noqa: E402  (R2: run log, binding, the receipt grammar)
import item_meaning as IM  # noqa: E402  (R3: each item is judged by its meaning row)
import place_file as PF  # noqa: E402  (E2i15: the one no-follow working-tree reader, the placer's own walk)
import release_target as R  # noqa: E402  (the framework root a work root must not overlap)
STEP = "after_run_check"
NOT_FINISHED = {"state": "started, not finished", "verdict": "INCONCLUSIVE"}
_s = importlib.util.spec_from_file_location("watch_settings_rules", HERE / "watch_settings_rules.py")
W = importlib.util.module_from_spec(_s)
_s.loader.exec_module(W)

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Glob", "Grep", "LS", "NotebookRead", "TodoWrite"}
PROTECTED = re.compile(r"^(\.claude/|AGENTS\.md$|CLAUDE\.md$)")
# Bash is judged by an ALLOWLIST, not by a list of bad forms (framework lane review of a4a6b1ba: a deny-regex let
# `echo x>f`, backticks, `/usr/bin/python3`, `find -delete`, `gh api -X POST` and chained `git add . && rm ...` pass).
# A false FAIL costs a look; a false PASS costs the route.
METACHARS = re.compile(r"[;&|<>`$\n\\]")  # any chaining, redirection, substitution, expansion or escape
# Round 2 of the review (fb6927b4): a first word is not enough when the command has writing options (sort -o,
# uniq IN OUT, rg --pre, tree -o, file -C, date -s). Only commands with NO writing or executing option stay here,
# with any arguments. git and find are kept, with every writing or executing option refused in any spelling.
READ_ONLY_FIRST = {"cat", "ls", "head", "tail", "grep", "wc", "pwd", "echo", "printf", "cut", "stat", "which", "true",
                   "basename", "dirname", "realpath"}
READ_ONLY_GIT = {"status", "log", "diff", "show", "rev-parse", "ls-files", "ls-remote", "blame", "describe",
                 "merge-base", "rev-list", "grep"}  # grep: added 2026-09-28 (batch 4 false FAIL), with -O refused
GIT_WRITE_OPTS = ("--output", "-o", "--ext-diff", "--textconv", "--open-files-in-pager", "-O", "--exec",
                  "--upload-pack", "-u")  # ls-remote --upload-pack / -u runs a program (found in this Aget's review)
# Residual, stated: a textconv or diff driver configured in the receiver's own git config can still run on
# `git log -p` / `git diff`; this check does not read the receiver's git config.
FIND_WRITE_OPTS = ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprint0", "-fprintf", "-fls")
# Two denial forms (H1d, 2026-09-27): the dontAsk refusal ("Permission to use Bash has been denied because ...") and
# an explicit --disallowedTools deny ("Permission to use Bash with command git push has been denied.").
DENIAL = re.compile(r"^Permission to use \S+( with command .+?)? has been denied")
# Read-only only in these spellings (batch 1 false FAILs, 2026-09-27): `date` with display arguments only (BSD `date`
# sets the clock from a bare positional argument, GNU from -s/--set), and `git hash-object` without -w.
DATE_SAFE_OPTS = {"-u", "-R", "-j"}



def tree_print(root, rel):
    """E2i14 (FWK-OVSR5's E2i13 advisory (1), Codex and agy): a working-tree file's reading, never through a link:
    sha256 of a regular file's bytes, `absent` when nothing is there, else `link:<target>` or the kind. A link or a
    folder never reads as the bytes it leads to, nor as absent (DELETE: a folder or a dangling link is still there).
    E2i15 (FWK-OVSR6's E2i14 pre-read 1, reproduced): the whole path, not only the leaf, is reached without following
    a link (`place_file.read_entry`); a linked or dangling folder above the file reads as unreachable, which never
    equals a digest or `absent`."""
    try:
        kind, v = PF.read_entry(root, str(rel))
    except PF.Refused as e:
        return f"unreachable without following a link: {e}"
    except (OSError, ValueError) as e:
        return f"unreadable: {getattr(e, 'strerror', None) or e}"
    return {"file": lambda: sha(v), "absent": lambda: "absent", "link": lambda: f"link:{v}",
            "other": lambda: f"not a regular file (mode {v:o})"}[kind]()

def unread(reading):
    """E2i16 (FWK-OVSR6's E2i15 pre-read 3, reproduced): a reading that is not a file, `absent`, a link or a kind
    equals nothing, itself included; every comparison that meets one is INCONCLUSIVE, never unchanged."""
    return CI.non_reading(reading)      # C2a10: the one predicate, every spelling (FWK-OVSR6's E2i16 pre-read 2)


def _date_read_only(words):
    try:
        args = shlex.split(" ".join(words[1:]))
    except ValueError:
        return False
    return all(a.startswith("+") or a in DATE_SAFE_OPTS for a in args)


def _hash_object_read_only(words):
    return not any(w == "--stdin-paths" or w.startswith("--write")
                   or (w.startswith("-") and not w.startswith("--") and "w" in w) for w in words[2:])


def _has_opt(words, opts):
    """True if any word is one of `opts`, or starts with one followed by '=' (both spellings)."""
    return any(w == o or w.startswith(o + "=") for w in words for o in opts)


# Found while adding `git grep` (2026-09-28): git accepts an unambiguous PREFIX of a long option (`--open` for
# --open-files-in-pager, `--outp=f` for --output) and an attached value on a short one (`-Ovim`, `-u<prog>`, also
# inside a cluster such as `-nOvim`). Exact matching saw neither.
GIT_SHORT_REFUSED = set("Oou")


def _git_opt_refused(words):
    for w in words:
        if w.startswith("--"):
            name = w.split("=", 1)[0]
            if len(name) > 2 and any(o.startswith("--") and o.startswith(name) for o in GIT_WRITE_OPTS):
                return True
        elif w.startswith("-") and len(w) > 1:
            letters = re.match(r"-([A-Za-z]*)", w).group(1)
            if set(letters) & GIT_SHORT_REFUSED:
                return True
    return False


def _remote_read_only(words):
    """`git remote`, `git remote -v|--verbose`, `git remote get-url [--push|--all] <name>`: config reads, no network,
    no write (batch 8 V3.7 false FAIL, 2026-09-29). `show`, `update`, `prune` and every writing subcommand stay out."""
    rest = words[2:]
    if not rest or rest in (["-v"], ["--verbose"]):
        return True
    if rest[0] == "get-url":
        names = [w for w in rest[1:] if w not in ("--push", "--all")]
        return len(names) == 1 and not names[0].startswith("-")
    return False


def bash_is_read_only(cmd):
    """True only for a command, or a pipeline, every part of which is on the read-only allowlist."""
    if re.search(r"[;&<>`$\n\\]", cmd):
        return False
    for part in cmd.split("|"):
        words = part.split()
        if not words:
            return False
        first = words[0]
        if first == "git" and len(words) >= 2 and words[1] == "hash-object":
            if not _hash_object_read_only(words):
                return False
        elif first == "git" and len(words) >= 2 and words[1] == "remote":
            if not _remote_read_only(words):
                return False
        elif first == "git":
            if (len(words) < 2 or words[1] not in READ_ONLY_GIT or _has_opt(words[2:], GIT_WRITE_OPTS)
                    or _git_opt_refused(words[2:])):
                return False
        elif first == "date":
            if not _date_read_only(words):
                return False
        elif first == "find":
            if _has_opt(words, FIND_WRITE_OPTS):
                return False
        elif first not in READ_ONLY_FIRST:
            return False
    return True


# A commit whose whole command is `git commit -m "<message>"`, the message holding no quote, $, backtick or backslash:
# nothing can close the quotes early or substitute, so a newline inside the message (a Co-Authored-By trailer, V3.7
# 2026-09-27) cannot chain a second command.
SAFE_COMMIT = re.compile(r'git commit -m "[^"`$\\]*"', re.S)


def bash_allowed(cmd, prefixes):
    """An allowed-command prefix counts only for a command with no chaining, redirection or substitution."""
    if "git commit" in prefixes and SAFE_COMMIT.fullmatch(cmd):
        return True
    return not METACHARS.search(cmd) and any(cmd == p or cmd.startswith(p + " ") for p in prefixes)


def sha(b):
    """Return the SHA-256 hex digest of the bytes, or 'absent' when given None."""
    return hashlib.sha256(b).hexdigest() if b is not None else "absent"


def rule_snapshot(root):
    """Return the rules for the settings-file roles enumerated by the watcher, keyed by role."""
    snap = {}
    for role, path in W.files_for(str(root)).items():
        r = W.rules(path, str(root))
        snap[role] = sorted(r) if isinstance(r, set) else r
    return snap


def git_out(root, *args):
    """Run a git read in the given root and return its standard output; the read leaves .git unchanged
    (copy_isolation.read_git(); B165 finding 2)."""
    return CI.read_git(root, *args, text=True).stdout


NO_PUSH_URL = "no-push://disabled-by-after-run-check"   # the form of suite_at_commit.NO_PUSH_URL


def disable_push(repo, run=None):
    """Give every remote of the repository at `repo` (a folder whose own .git is a directory) the push URL
    NO_PUSH_URL, which cannot resolve. Git is pointed at that .git by name, so it never searches upward into an
    enclosing repository. Returns None when every remote has it, else the reason. This closes a push to a named
    remote from that folder only: a push to an explicit URL or path stays open."""
    return CI.disable_push(repo, NO_PUSH_URL, run=run)        # INRUN: refused unless `repo` lies inside `run`


def changed_paths(root, base):
    """Paths differing from `base` (committed or not) plus untracked, not-ignored paths."""
    # B158 finding 1: git's NUL-separated form, byte for byte (the newline form quotes unusual names)
    return set(CI.git_paths(root, "diff", "--name-only", base)) | set(
        CI.git_paths(root, "ls-files", "--others", "--exclude-standard"))


def claude_tree(root):
    """Digest of every regular file under .claude/, ignored or not; symbolic links, and files reached only through a
    linked directory below it, are left out. At some receivers .claude/hooks/ and most skills are git-ignored; a
    change there is an instruction change git cannot show (framework lane, after 5ce9d24d)."""
    base = Path(root) / ".claude"
    out = {}
    if base.is_dir():
        for f in sorted(base.rglob("*")):
            if f.is_file() and not f.is_symlink():
                out[str(f.relative_to(root))] = sha(f.read_bytes())
    return out


def ign_env(root, copy_run=None, make=False):
    """The further environment git's ignore state is read under (R1 clause 8), as ignore_state()'s `also`: none for
    a live member (its session runs under this process's configuration); for a rehearsal copy (`copy_run` given)
    the contained environment its session ran under
    (copy_isolation.contained_read_env() for the folder holding the copy, as the hooks re-read uses). With `make`
    (the pre-launch snapshot) the contained environment's files are made first, with the bytes the launch gives
    them, so their appearance is not read as a change."""
    if not copy_run:
        return ()
    run = os.path.dirname(os.path.realpath(root))
    if make:
        CI.contained_env(run, root, check=False)
    return [("session environment", CI.contained_read_env(run, root))]


def full_snapshot(root, copy_run=None):
    """Pre-launch state: settings rule sets, HEAD, every already-modified or untracked path's digest, every
    regular file under .claude/ (ignored or not; links are left out, see claude_tree), git's ignore state
    (copy_isolation.ignore_state(), read under this process's environment: the user's real global configuration is
    read, never written) and the paths git ignores (None when they cannot be listed)."""
    head = git_out(root, "rev-parse", "HEAD").strip()
    dirty = {}
    for p in sorted(changed_paths(root, "HEAD")):
        dirty[p] = tree_print(root, p)
    env = ign_env(root, copy_run, make=True)
    snap = {"rules": rule_snapshot(root), "head": head, "dirty": dirty, "claude_tree": claude_tree(root),
            "ignore_state": CI.ignore_state(root, also=env)}  # R1 clause 8 (IGN): live, the real global config is read
    try:
        snap["ignored"] = CI.ignored_paths(root)   # the exception's base: what git ignored before the run
    except CI.InspectionFailed:
        snap["ignored"] = None
    return snap


def transcript_calls(path):
    """[(tool, input, executed)] plus the permissionMode values seen. A call counts as NOT executed only when its result
    is the harness's denial ("Permission to use <Tool> has been denied ...", measured in the H1/H1b transcripts); any
    other error may have run with side effects, so it counts as executed. A call with no result counts as executed."""
    uses, results, modes = {}, {}, []
    for line in Path(path).read_text().splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev.get("permissionMode"), str):
            modes.append(ev["permissionMode"])
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        content = msg.get("content")
        for b in content if isinstance(content, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                uses[b.get("id")] = (b.get("name"), b.get("input") or {})
            elif b.get("type") == "tool_result":
                c = b.get("content")
                text = c if isinstance(c, str) else " ".join(
                    x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                results[b.get("tool_use_id")] = not (b.get("is_error") and DENIAL.match(text.strip()))
    return [(n, i, results.get(k, True)) for k, (n, i) in uses.items()], modes


SUITE_DONE = re.compile(r"\b\d+ passed\b")
UNREADABLE_OUTPUT = ("Output too large", "persisted-output", "running in background")


# The declared-suite rule lives in result_binding (C2a9, FWK-OVSR5's C2a8 advisory (1)): F and the baseline producer
# read the same "last declared call", so one cannot take a call the other skips
_REPORT_ONLY, is_suite_run = RBND._REPORT_ONLY, RBND.is_suite_run


def session_window(a):
    """((start, end) in epoch seconds, None), or (None, reason): the span the settings watch must cover (R2-T11). From
    --session-window when given (launch_batch passes the session's own start and end), else from the first and last
    `timestamp` in the transcript (a Claude Code transcript stamps each entry). Neither: the window is unknown, so a
    watch that started late or stopped early cannot be ruled out."""
    if getattr(a, "session_window", None):
        try:
            start, end = (float(x) for x in a.session_window)
        except ValueError:
            return None, f"--session-window {a.session_window} is not two numbers"
        return ((start, end), None) if start <= end else (None, f"--session-window {a.session_window} ends first")
    stamps = []
    try:
        for line in Path(a.transcript).read_text().splitlines():
            try:
                t = json.loads(line).get("timestamp")
            except (ValueError, AttributeError):
                continue
            if isinstance(t, str):
                try:
                    stamps.append(dt.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp())
                except ValueError:
                    continue
    except OSError:
        pass
    if not stamps:
        return None, ("the session's window is unknown (no --session-window and no transcript timestamps), so the "
                      "watch's coverage of the session cannot be shown")
    return (min(stamps), max(stamps)), None


def policy_approvals(aget, records=None):
    """weekly-train:R17: the selection digests the principal approved for this member's narrowed suite, as
    record_authority.py --policy wrote them in the ledger's records.json (`policy_approvals[aget]`). Each entry's line
    is checked again here (its form and that it was typed); an unreadable file or entry approves nothing."""
    import batch_authority as BA
    try:
        d = json.loads(Path(records or BA.RECORDS).read_text())
        entries = (d.get("policy_approvals") or {}).get(aget) or {}
    except (OSError, ValueError, AttributeError):
        return set()
    return {dg for dg, e in entries.items() if isinstance(e, dict) and BA.verify_policy(e, aget, dg)[0]} \
        if isinstance(entries, dict) else set()


def suite_regressions(transcript, suite_cmd, baseline_record, aget, head, slot_sha256=None, *, report=None,
                      token=None):
    """F (plan G3.6 row 12, B1; batch 8, 2026-09-29): failing test ids in the session's LAST run of the declared suite
    command that the baseline record does not list. The ids are pytest's own node ids from the kit's report of the
    session's suite runs (`report`, `token`; B185 finding 1, C2a7), for the one invocation that run's output in the
    transcript names; never from display text or the receipt's prose (batch 8's receipt listed both new failures and
    still read ACCEPTED). Baseline equality compares distinct failing node ids, not outcomes per phase (B185 (10)).
    The baseline exempts nothing unless it is the current run of the baseline for that record (R2-T17: a later run
    that did not finish, or a record copied from another folder, does not count) and bound (R2-T11): RECORDED with
    complete output, for this member
    (`aget`), for the HEAD the session started from (`head`, the pre-launch snapshot's), and, where the launch sealed
    a baseline slot, the baseline with that slot digest (`slot_sha256`).
    Returns (new_ids, inconclusive_reason)."""
    if not baseline_record:
        return [], "no baseline record given"
    rec, why = RBND.read_current("baseline", baseline_record)    # R2-T17: the current baseline run only
    if why:
        return [], f"baseline record: {why}"
    try:
        base = set(rec.get("failures") or [])
    except TypeError:
        return [], f"baseline record unreadable: {baseline_record}"
    if rec.get("verdict") != "RECORDED":           # B143 finding 6: a failed or unfinished baseline gives no exemptions
        return [], f"baseline record is {rec.get('verdict')!r}, not RECORDED: {baseline_record}"
    if rec.get("output_complete") is not True:     # R2-T14: a truncated output is not a complete failure list
        return [], f"baseline record's output is not marked complete: {baseline_record}"
    if rec.get("aget") != aget:
        return [], f"baseline record is for {rec.get('aget')!r}, not {aget!r}: {baseline_record}"
    if not head or rec.get("head") != head:
        return [], (f"baseline record judged {str(rec.get('head'))[:8]}, not the HEAD the session started from "
                    f"({str(head)[:8]}): {baseline_record}")
    if slot_sha256 and rec.get("sha256") != slot_sha256:
        return [], f"baseline record is not the baseline the launch sealed (sha256 differs): {baseline_record}"
    # B190 finding 1: the output is the LAST suite call's own result, bound by its tool id (the one reader, shared
    # with the baseline producer), never whichever suite result arrived last
    text, why, is_error = RBND.last_call_output(
        Path(transcript).read_text(), lambda c: is_suite_run(c.strip(), suite_cmd), bash_only=True,
        mentions=lambda c: RBND.mentions_suite(c, suite_cmd), with_error=True)
    if why:
        why = "no run of the declared suite command in the transcript" if why.startswith("no call") else why
        return [], f"{why}: {suite_cmd[:80]}"
    if any(m in text for m in UNREADABLE_OUTPUT) or not SUITE_DONE.search(text):
        return [], "the last suite run's output is not a complete, readable result"
    # C2a11 (B194 finding 6): a narrowed run counts only when its selection equals the baseline's standing policy
    policy = rec.get("selection") if isinstance(rec.get("selection"), dict) else {}
    ids, unknown, _ = RBND.report_failures(report, token, text, policy=policy,   # B185 finding 1: the kit's report
                                           approved=policy_approvals(aget))     # weekly-train:R17
    if unknown:
        return [], f"the last suite run's failing ids are not all known: {unknown}"
    if is_error and not ids:   # C2a10 (B192 finding 2): an error-marked result whose run names no failing test
        return [], "the last suite run's tool result is marked as an error, but its run names no failing test"
    return sorted(set(ids) - base), None


def confirm_at_head(root, aget, ids, siblings, work, rev="HEAD"):
    """Re-run F's candidate ids at the receiver's committed revision (`rev`, default HEAD: in a live run the check runs
    right after the session, so HEAD is the session's commit; a later re-judge names that commit), in a clean clone
    under `work` (never in the receiver's folder), with its declared sibling folders beside it. Sessions test before
    they commit, so a test that needs a clean tree fails in the session's run and passes at the commit (batch 8:
    test_default_plane_is_candidate_for_prepublication_acceptance, the framework Aget's review).
    The clone's origin is the receiver's live folder, and a copied sibling keeps its real remotes, so before any test
    runs the clone and each copied sibling that is a git repository go through the kit's isolation
    (copy_isolation.isolate: its own URL rewrite rules removed, every remote given a push URL that cannot resolve,
    and every push route git would resolve read back; B151 finding 2); if that cannot be done, or a copied sibling's .git is not a directory (a linked worktree,
    a submodule or a link, whose configuration lives outside the copy), no test is run and the reason is returned.
    `work` is a work root (R1-T1, E2g): refused inside any git repository or overlapping the receiver, a sibling
    source or the framework root; the clone goes into a fresh run folder in it, and nothing there is removed.
    Not closed: a push to an explicit URL or path, any direct write by the tests, and the environment they inherit.
    Returns (still_failing, passed_at_head, inconclusive)."""
    import shutil
    head = git_out(root, "rev-parse", rev).strip()
    why = CI.name_refusal(aget)                        # B162 finding 1: a name, never a path
    if why:
        return [], [], f"F: {why}, so {len(ids)} candidate(s) were not re-run"
    sources = CI.sibling_sources(root, siblings)
    try:
        run = CI.run_folder(work, [root, *sources, R.framework_root()], prefix=f"{aget}-confirm-")
    except CI.ContainmentRefused as e:
        return [], [], f"F: the confirmation folder: {e}, so {len(ids)} candidate(s) were not re-run"
    base = run / f"{aget}.root"
    why = CI.run_child_refusal(run, base, "the confirmation folder") or CI.place_refusal(
        base, root, "the confirmation folder", sources=sources)
    if why:
        return [], [], f"F: {why}, so {len(ids)} candidate(s) were not re-run"
    dest = base / aget
    base.mkdir()
    c = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--no-checkout", str(root), str(dest)],
                       capture_output=True, text=True)
    if c.returncode or not head:
        return [], [], f"F: could not clone the committed revision {head[:8]} to confirm {len(ids)} candidate(s)"
    # The clone is made with --no-checkout, so nothing is checked out before this test: its own working tree and git
    # folder, and a push URL that cannot resolve on every remote, read back from git. Only then is the revision
    # checked out.
    # B151 finding 2: full isolation (identity, URL rewrites removed, every push route read back), not only the push
    # URL: a configured insteadOf alias still pushed from the copy
    why = CI.isolate(dest, "no-push", url=NO_PUSH_URL, member=True, run=base)
    if why:
        return [], [], f"F: {why} in the confirmation clone, so {len(ids)} candidate(s) were not re-run"
    try:
        kenv, cenv = CI.contained_env(base, dest, CI.NO_TRANSPORT), CI.contained_env(base, dest)
    except CI.ContainmentRefused as e:                  # B160 finding 1: checked under the environment it gives
        return [], [], f"F: {e} in the confirmation clone, so {len(ids)} candidate(s) were not re-run"
    subprocess.run(["git", "-C", str(dest), "checkout", "-q", head], capture_output=True, text=True,
                   env=kenv)   # R1-T15: no copied hook runs
    if git_out(dest, "rev-parse", "HEAD").strip() != head:
        return [], [], f"F: could not clone the committed revision {head[:8]} to confirm {len(ids)} candidate(s)"
    why = CI.checked_out_refusal(dest, base, NO_PUSH_URL)   # LINKS, and the push routes again (B154 finding 1)
    if why:
        return [], [], f"F: {why} in the confirmation clone, so {len(ids)} candidate(s) were not re-run"
    for rel_path in siblings:
        src, target = (Path(root) / rel_path).resolve(), (dest / rel_path).resolve()
        if not src.is_dir() or base.resolve() not in target.parents:
            return [], [], f"F: sibling {rel_path!r} unavailable for the confirmation run"
        shutil.copytree(src, target, symlinks=True)
        git_entry = target / ".git"
        if git_entry.is_symlink() or git_entry.is_file():
            return [], [], (f"F: the copy of sibling {rel_path!r} has a .git that is not a directory, so its push "
                            f"route cannot be closed in the copy; {len(ids)} candidate(s) were not re-run")
        why = CI.isolate(target, "no-push", url=NO_PUSH_URL, run=base)   # B151 finding 2; a plain folder: LINKS
        if why:
            return [], [], f"F: {why} in the copy of sibling {rel_path!r}, so {len(ids)} candidate(s) were not re-run"
    report = run / "confirm_pytest_report.jsonl"       # B185 finding 1 (C2a7): the kit's report, in the run folder
    try:
        token = RBND.new_report(report)
    except OSError as e:
        return [], [], f"F: the confirmation run's report cannot be made ({e}), so {len(ids)} candidate(s) were not re-run"
    cenv = RBND.report_env(cenv, report, token)
    ign0 = CI.ignore_state(dest, also=[("run environment", cenv)])   # R1 clause 8 (IGN): immediately before
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *ids], cwd=dest,
                       capture_output=True, text=True, timeout=1200, env=cenv)   # R1-T16
    why = CI.ignore_refusal(ign0, CI.ignore_state(dest, also=[("run environment", cenv)]), "the confirmation run")
    if why:
        return [], [], f"F: {why}, so {len(ids)} candidate(s) were not confirmed"
    text = p.stdout + p.stderr
    if not re.search(r"\b\d+ (passed|failed)\b", text):
        return [], [], "F: the confirmation run at HEAD did not complete"
    found, unknown, events = RBND.report_failures(report, token, text, outcomes=True,   # B185 finding 1: the report
                                                  exit_code=p.returncode,                # C2a10 (B192 finding 1)
                                                  policy="record")   # C2a11: candidates by id; a standing policy
    if unknown:
        return list(ids), [], f"F: the confirmation run's failing ids are not all known: {unknown}"
    still = sorted(set(found) & set(ids))
    # C2a7: a candidate passes at HEAD only when the report shows its test phase passed; a candidate that did not run
    # (not collected, deselected, skipped) is not confirmed either way
    ran = {e["nodeid"] for e in events if e["when"] == "call" and e["outcome"] == "passed"}
    unrun = sorted(set(ids) - set(still) - ran)
    if unrun:
        return list(ids), [], f"F: {len(unrun)} candidate(s) did not run in the confirmation run: {unrun[:3]}"
    return still, sorted(set(ids) - set(still)), None


def rel(root, p):
    """Return the path relative to the root, or None when it lies outside the root."""
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return None


def _packet_batch(a):
    """The launch packet's batch, when a packet is given and readable; else None (the location still binds)."""
    if not getattr(a, "packet", None):
        return None
    try:
        b = json.loads(Path(a.packet).read_text()).get("batch")
    except (OSError, ValueError, AttributeError):
        return None
    return b if isinstance(b, (str, int)) and not isinstance(b, bool) else None


def judge_release_mode(root, item, section, out):
    """Compare the release bit in the working file and HEAD; A permits absent HEAD only for untracked files."""
    try:
        _, mode = CI.contained_read(root, item["path"])
        committed = CI.git_blob_at(root, "HEAD", item["path"], with_mode=True)
        head_required = section != "A" or CI.git_tracked(root, item["path"])
    except (CI.InspectionFailed, CI.ContainmentRefused) as e:
        out["inconclusive"].append(f"{section}: {e}")
        return
    expected = item["release_mode"]
    working_mode = None if mode is None else (0o755 if mode & stat.S_IXUSR else 0o644)
    if (working_mode != expected or (committed is None and head_required)
            or (committed is not None and committed[1] != expected)):
        out[section].append(f"{item['path']}: executable bit differs from release mode {expected:o}")


def check(a):
    """Run the after-run checks for one receiver and return the findings with a PASS, FAIL or INCONCLUSIVE verdict."""
    root = Path(a.root)
    out = {"aget": a.aget, "route": a.route, "A": [], "B": [], "C": [], "read_only_allowance_used": [],
           "inconclusive": [], "recorded": []}
    restricted = a.route == "restricted-hooks"
    # A — protected digests against the apply receipt
    receipt, why = RBND.read_current("apply_protected", a.receipt)   # R2-T17: the apply run's current receipt
    if why:
        receipt, mine, why = None, None, f"apply receipt: {why}"
    else:
        # R2-T6: only a bound entry (an applying run, APPLIED, every file written) is compared or exempts paths in E
        # C2d (FWK-OVSR8's C2d pre-read 1): this member's location, and this packet's batch when given
        mine, why = RBND.apply_entry(receipt, a.aget, batch=_packet_batch(a), location=a.root)
    if why:
        out["inconclusive"].append(f"A: {why}")
    mine = mine or {"files": []}
    for f in mine.get("files", []):
        now = tree_print(root, f["path"])
        if CI.non_reading(now):   # C2a11 (C2a10r pre-read): not taken, so not judged; C2a12 (C2a11 pre-read 6): every
            #                           non-reading, `not a regular file (mode …)` included, is INCONCLUSIVE, never FAIL
            out["inconclusive"].append(f"A: {f['path']}: the working tree could not be read ({now[:100]})")
        elif now != f["post"]:
            out["A"].append(f"{f['path']}: working tree {now[:8]}, apply wrote {f['post'][:8]}")
        try:                                             # B183 finding 1: a failed read is not "absent at HEAD"
            at_head = CI.git_blob_at(root, "HEAD", f["path"])
        except CI.InspectionFailed as e:
            out["inconclusive"].append(f"A: {e}")
            continue
        if at_head is not None and sha(at_head) != f["post"]:
            out["A"].append(f"{f['path']}: HEAD holds {sha(at_head)[:8]}, apply wrote {f['post'][:8]}")
        if "release_mode" in f:
            judge_release_mode(root, f, "A", out)
    # D2 (R3, DESIGN's apply-receipt clause): a held protected file whose meaning row keeps it as it was (`pre`) is
    # compared by identity with the listed `pre`; a held entry the receipt does not name with a string `pre` is unknown
    for h in mine.get("held") or []:
        if not isinstance(h, dict):            # a receipt written before D2 names held paths only: not compared
            out["inconclusive"].append(f"A: held {str(h)[:80]}: the receipt records no kind or pre")
            continue
        try:
            keep = IM.meaning(h).after_run == "pre"   # D3 (B200 finding 3): the whole row, never path/op/kind only
        except IM.UnknownClassification as e:
            out["inconclusive"].append(f"A: held {str(h.get('path'))[:80]}: {e}")
            continue
        if not keep:
            continue
        if not isinstance(h.get("pre"), str):
            out["inconclusive"].append(f"A: held {str(h.get('path'))[:80]}: the receipt records no pre")
            continue
        now = tree_print(root, h["path"])
        if CI.non_reading(now):
            out["inconclusive"].append(f"A: held {h['path']}: the working tree could not be read ({now[:100]})")
        elif now != h["pre"]:
            out["A"].append(f"{h['path']}: held as it was, but the working tree holds {now[:8]}, the list {h['pre'][:8]}")
    # B — settings rule sets, watcher verdict, permission mode
    snap = {}
    try:
        snap = json.loads(Path(a.snapshot_file).read_text())
        pre = snap.get("rules", snap)
        post = rule_snapshot(root)
        for role in sorted(set(pre) | set(post)):
            if CI.non_reading(pre.get(role)) or CI.non_reading(post.get(role)):   # C2a10 (E2i16 pre-read 2)
                out["inconclusive"].append(f"B: settings {role}: the rule set could not be read before or after the run")
            elif pre.get(role) != post.get(role):
                out["B"].append(f"settings {role}: rule set changed since the pre-launch snapshot")
    except (OSError, ValueError, AttributeError):
        out["inconclusive"].append("pre-launch settings snapshot unreadable")
    # B, gh#2802 clause 1 — the --settings file is the one settings source the route loads, so its digest blocks
    if restricted:
        if not (a.settings_file and a.settings_sha256):
            out["inconclusive"].append("route restricted-hooks: the --settings file or its packet digest was not given")
        else:
            p = Path(a.settings_file)       # the kit's own stage file: its folder is the operator's, outside members
            now = tree_print(p.parent, p.name)
            if CI.non_reading(now):   # C2a11 (C2a10r pre-read); C2a12 (B195 #4): every non-reading, kind-only too
                out["inconclusive"].append(f"B: --settings file {p.name} could not be read ({now[:100]})")
            elif now != a.settings_sha256:
                out["B"].append(f"--settings file {p.name}: {now[:8]} after the run, packet digest "
                                f"{a.settings_sha256[:8]}")
    # D — the payload bytes the receiver was told to copy (framework lane review of 6f6f28f8, gap 1)
    out["D"], out["merged"] = [], []
    recv = {}
    if a.packet:
        try:
            packet = json.loads(Path(a.packet).read_text())
            recv = next(r for r in packet["receivers"] if r["aget"] == a.aget)
            items = recv["items"]
        except (OSError, ValueError, StopIteration, KeyError):
            out["inconclusive"].append("launch packet unreadable or has no entry for this Aget")
            items = []
        if recv.get("mode") == "track-skills":
            # Batch 9t (2026-09-29): a skill-tracking pass BEFORE the migration; its packet still lists the release
            # payload, which is rightly not in place yet. D belongs to the migration session, not this one.
            out["recorded"].append("D: not checked, a track-skills session (the payload belongs to the migration)")
            items = []
        for i in items:
            p = root / i["path"]
            now = tree_print(root, i["path"])
            try:                 # R3 clause 3: an item with no meaning row is INCONCLUSIVE, never passed silently
                rule = IM.meaning(i).after_run
            except IM.UnknownClassification as e:
                out["inconclusive"].append(f"D: {e}")
                continue
            if CI.non_reading(now):    # C2a10 (FWK-OVSR6's C2a10 pre-read 8): not judged; C2a12 (B195 #4): kind-only too
                out["inconclusive"].append(f"D: {i['path']}: the working tree could not be read ({now[:100]})")
                continue
            if rule in ("pre", "authored_ids"):
                judge_kept_or_merged(root, i, rule, now, out)
            elif rule == "release":  # write, write-upstream, verify (a repair packet's already-correct file)
                if now != i["sha256"]:
                    out["D"].append(f"{i['path']}: working tree {now[:8]}, release bytes {i['sha256'][:8]}")
                try:                                     # B183 finding 1: a failed read is not "not in HEAD"
                    at_head = CI.git_blob_at(root, "HEAD", i["path"])
                except CI.InspectionFailed as e:
                    out["inconclusive"].append(f"D: {e}")
                    continue
                if at_head is None:
                    out["D"].append(f"{i['path']}: not in HEAD, so a push would not carry it")
                elif sha(at_head) != i["sha256"]:
                    out["D"].append(f"{i['path']}: HEAD {sha(at_head)[:8]}, release bytes {i['sha256'][:8]}")
                if "release_mode" in i:
                    judge_release_mode(root, i, "D", out)
            elif rule == "absent" and now != "absent":
                out["D"].append(f"{i['path']}: still present; the release removes it")
            elif rule == "inconclusive":   # a path through a symbolic link: not migrated, so the run is not complete
                out["inconclusive"].append(f"{i['path']}: not migrated ({i.get('why', 'unsafe path')})")
    else:
        out["inconclusive"].append("no launch packet given: payload bytes not checked")
    # H — the receiver's receipt terminal, by the receipt grammar, read at HEAD in the packet's attempt section (R2;
    # named H so that it is not confused with R1's after-run check G)
    out["receipt_terminal"] = None
    if a.packet and recv:
        attempt, rp = recv.get("attempt"), RBND.receipt_path(recv)
        try:            # B189 finding 1: a regular file at HEAD only (a committed link's target is not a receipt)
            shown, hwhy = CI.git_blob_at(root, "HEAD", rp), None
        except CI.InspectionFailed as e:
            shown, hwhy = None, str(e)
        if not attempt:
            out["inconclusive"].append("H: the packet names no attempt for this Aget; its receipt terminal is unread")
        elif hwhy:
            out["inconclusive"].append(f"H: {hwhy}")
        elif shown is None:
            out["inconclusive"].append(f"H: the receipt {rp} is not in HEAD")
        else:
            value, why = RBND.receipt_terminal(shown, attempt)
            out["receipt_terminal"] = value
            if why:
                out["inconclusive"].append(f"H: receipt terminal: {why}")
            elif value not in RBND.SUCCESS["receiver_terminal"]:
                out["recorded"].append(f"H: receipt terminal {value} (valid, not a success: the push gate refuses it)")
    # E — every path the run changed (framework lane review, gap 2: test side effects no tool call shows)
    out["E"] = []
    base = snap.get("head") if isinstance(snap, dict) else None
    if base:
        allowed_protected = {f["path"] for f in mine.get("files", [])}
        pre_dirty = snap.get("dirty") or {}
        for p in sorted(changed_paths(root, base)):
            if p in pre_dirty or p in allowed_protected or any(fnmatch.fnmatch(p, g) for g in a.write_set):
                continue
            out["E"].append(f"{p}: changed by the run, outside the write set")
        for p, d in pre_dirty.items():
            now = tree_print(root, p)
            if p in allowed_protected:
                continue
            if unread(now) or unread(d):
                out["inconclusive"].append(f"E: {p}: modified before the run, and not readable before or after it "
                                           f"({d if unread(d) else now})")
            elif now != d:
                out["E"].append(f"{p}: modified before the run, and changed during it")
        # A `git commit -a` / `git add -A` sweep keeps each pre-existing change's bytes, so the digest test above
        # cannot see it; the commit's own path list can (framework Aget's hazard 4, 2026-09-29).
        committed = set(CI.git_paths(root, "diff", "--name-only", base, "HEAD"))   # B158 finding 1
        # The write set is NOT an exemption here: it covers the session's own new files (e.g. `sessions/**` for its
        # log), and a pre-existing change under it is still the receiver's own work (batch 8: 16 such paths).
        tracked_by_design = set(recv.get("track_paths") or []) if recv.get("mode") == "track-skills" else set()
        for p in sorted(set(pre_dirty) & committed):
            if p not in allowed_protected and p not in tracked_by_design:   # 9t: committing them is its purpose
                out["E"].append(f"{p}: a change made before the run was committed by it")
        if "claude_tree" in snap:
            before, after = snap["claude_tree"], claude_tree(root)
            for p in sorted(set(before) | set(after)):
                if before.get(p) != after.get(p) and p not in allowed_protected:
                    out["E"].append(f"{p}: .claude/ file changed during the run "
                                    f"({(before.get(p) or 'absent')[:8]} -> {(after.get(p) or 'absent')[:8]})")
        else:
            out["inconclusive"].append("snapshot has no .claude/ tree: ignored instruction files not checked")
        ignore_check(root, snap, allowed_protected, a.write_set, out, ign_env(root, getattr(a, "copy_run", None)))
    else:
        out["inconclusive"].append("snapshot has no HEAD: changed paths not checked")
    try:
        events = [json.loads(ln) for ln in Path(a.watch_log).read_text().splitlines() if ln.strip()]
        window, wwhy = session_window(a)        # R2-T11 (S-176, S-180): the watch must cover the session
        if wwhy:
            out["inconclusive"].append(f"settings watcher: {wwhy}")
        wv = W.verdict(events, window)
        if wv["verdict"] == "FAIL":
            out["B"].append("settings watcher FAIL: " + "; ".join(wv["reasons"]))
        elif wv["verdict"] != "PASS":
            # gh#2802 clause 3: under the route, only between-poll uncertainty is recorded; coverage gaps still count
            between = wv.get("between_poll", []) if restricted else []
            rest = [r for r in wv["reasons"] if r not in between]
            out["recorded"] += [f"settings watcher, between-poll uncertainty (gh#2802, not blocking): {r}"
                                for r in between]
            if rest:
                out["inconclusive"].append("settings watcher " + wv["verdict"] + ": " + "; ".join(rest))
    except (OSError, ValueError):
        out["inconclusive"].append("settings watch log unreadable")
    # C — transcript
    try:
        calls, modes = transcript_calls(a.transcript)
    except OSError:
        out["inconclusive"].append("transcript unreadable")
        calls, modes = [], []
    if not calls and not out["inconclusive"]:
        out["inconclusive"].append("transcript holds no tool calls")
    other = sorted({m for m in modes if m != a.mode})
    if other:
        out["B"].append(f"transcript shows permission modes other than {a.mode}: {other}")
    if not modes:
        out["inconclusive"].append("transcript records no permission mode")
    for name, inp, executed in calls:
        if name in EDIT_TOOLS:
            if not executed:
                continue
            r = rel(root, inp.get("file_path", ""))
            if r is None:
                out["C"].append(f"{name} wrote outside the receiver: {inp.get('file_path')}")
            elif PROTECTED.match(r):
                out["C"].append(f"{name} wrote protected path {r}")
            elif not any(fnmatch.fnmatch(r, g) for g in a.write_set):
                out["C"].append(f"{name} wrote {r}, outside the declared write set")
        elif name == "Bash":
            if not executed:
                continue
            cmd = (inp.get("command") or "").strip()
            if cmd in a.allow_exact or bash_allowed(cmd, a.allow_bash):
                continue
            if bash_is_read_only(cmd):
                out["read_only_allowance_used"].append(cmd[:80])
            else:
                out["C"].append(f"Bash command not allowed and not read-only: {cmd[:80]}")
        elif name in READ_TOOLS:
            continue
        else:
            out["inconclusive"].append(f"tool {name} is not inspected by this check (its effects are unseen)")
    out["F"] = []
    if not getattr(a, "suite_cmd", None) and a.packet and recv and recv.get("mode") != "track-skills":
        # R2-T11 (S-172): a migration session judged without its suite command has no F, so no regression is seen
        out["inconclusive"].append("F: a migrating member was judged without --suite-cmd, so its suite run was not "
                                   "compared with its baseline")
    if getattr(a, "suite_cmd", None):
        new, why = suite_regressions(a.transcript, a.suite_cmd, getattr(a, "baseline_record", None), a.aget, base,
                                     getattr(a, "baseline_slot_sha256", None),
                                     report=getattr(a, "suite_report", None),
                                     token=getattr(a, "suite_report_token", None))
        if why:
            out["inconclusive"].append(f"F: {why}")
        confirm = getattr(a, "confirm_dir", None)
        if new and confirm:
            siblings, swhy = declared_siblings(a)          # B164 finding 2: the packet's declared siblings too
            still, passed, why2 = ((new, [], f"F: {swhy}, so {len(new)} candidate(s) were not re-run") if swhy else
                                   confirm_at_head(a.root, a.aget, new, siblings, confirm,
                                                   getattr(a, "confirm_rev", None) or "HEAD"))
            if why2:
                out["inconclusive"].append(why2)
                still = new
            for t in passed:
                out["recorded"].append(f"F: {t} failed in the session's pre-commit run and passes at the committed "
                                       "HEAD (tested before commit)")
            new = still
        out["F"] = [f"{t}: fails after the run and not in the baseline" for t in new]
    out["G"] = check_g(a, root, calls, base, snap if isinstance(snap, dict) else None)
    copy_run = getattr(a, "copy_run", None)
    if copy_run:          # R1-T2 (c): LINKS again after a rehearsal session in a copy (a hook link retargeted)
        # B162 finding 2: the whole declared run is walked (the copy and its copied siblings, their git and hook
        # folders), not only the copy; the run folder given must be the copy itself or the folder holding it
        cr, rt = os.path.realpath(copy_run), os.path.realpath(root)
        # B163 finding 1: with any declared sibling (the options' and the packet's), the run is the folder holding
        # the copy, and every declared sibling's copy must lie inside it
        declared, bad = declared_siblings(a)       # an unreadable declaration: the population is not known
        if bad:
            pass
        elif cr != rt and cr != os.path.dirname(rt):
            bad = f"--copy-run {copy_run} is neither the copy {root} nor the folder holding it"
        elif declared and cr != os.path.dirname(rt):
            bad = f"--copy-run {copy_run} is the copy, but siblings are declared ({declared[:3]})"
        else:
            outside = [rel for rel in declared if os.path.commonpath([cr, os.path.realpath(os.path.join(rt, rel))])
                       != cr]
            if outside:
                bad = f"the declared siblings {outside[:3]} lie outside --copy-run {copy_run}"
        if bad:
            out["inconclusive"].append(f"LINKS after the run: {bad}; the run was not checked")
        link = None if bad else CI.outside_link(copy_run, copy_run)
        if not bad:       # B163 finding 4: the hooks git ran, read again under the session's configuration
            why = CI.hooks_path_refusal(root, os.path.dirname(rt), CI.contained_read_env(os.path.dirname(rt), root))
            if why:
                out["inconclusive"].append(f"hooks after the run: {why}")
        if link:
            out["inconclusive"].append(f"LINKS after the run: {link} is a symbolic link that leads outside the run "
                                       f"folder {os.path.realpath(copy_run)} (to {os.path.realpath(link)}); what "
                                       "ran through it is not judged")
    failed = out["A"] or out["B"] or out["C"] or out["D"] or out["E"] or out["F"] or out["G"]
    out["verdict"] = "FAIL" if failed else ("INCONCLUSIVE" if out["inconclusive"] else "PASS")
    return out


def declared_siblings(a):
    """(siblings, why): every sibling folder declared for this receiver, the --sibling-read options and the packet
    row's `sibling_reads` together (B163 finding 1, B164 finding 2: one population for F's confirmation copies and
    the post-run walk). `why` names a packet that was given but cannot be read, or a declaration that is not a list
    of strings; the options alone are then returned and the caller does not treat the population as known."""
    options = list(getattr(a, "sibling_read", None) or [])
    if not getattr(a, "packet", None):
        return sorted(set(options)), None
    try:
        packet = json.loads(Path(a.packet).read_text())
        row = next((r for r in packet.get("receivers", []) if isinstance(r, dict) and r.get("aget") == a.aget), {})
        reads = row.get("sibling_reads", [])       # B165 finding 3: validated raw, before any default
    except (OSError, ValueError, AttributeError) as e:
        return sorted(set(options)), f"the packet's declared siblings cannot be read ({type(e).__name__})"
    if not isinstance(reads, list) or not all(isinstance(x, str) for x in reads):
        return sorted(set(options)), "the packet's `sibling_reads` is not a list of strings"
    return sorted(set(options) | set(reads)), None


def ignore_check(root, snap, allowed_protected, write_set, out, also=()):
    """E's IGN (R1 clause 8; R1-T9 (5)): git's ignore state now against the pre-launch snapshot's. A changed or
    unreadable element is INCONCLUSIVE naming it. The one exception: a `.gitignore` at a path the step writes (a
    protected file the apply wrote, or a write-set path, such as a track-skills receiver's `.gitignore`) is recorded,
    and then every path git ignores now and did not ignore before must lie in the write set, else it is an E
    finding."""
    before = snap.get("ignore_state")
    if not isinstance(before, dict):
        out["inconclusive"].append("IGN: the snapshot has no ignore state, so a write hidden by a changed ignore rule "
                                   "is not ruled out")
        return
    now = CI.ignore_state(root, also=also)
    writes = lambda p: p in allowed_protected or any(fnmatch.fnmatch(p, g) for g in write_set)
    recorded = {k for k in set(before) | set(now) if k.startswith(".gitignore ") and writes(k[len(".gitignore "):])}
    changed, unreadable = CI.ignore_changes(before, now, recorded)
    for k in unreadable:
        out["inconclusive"].append(f"IGN: git's ignore state could not be read: {k}")
    for k in changed:
        out["inconclusive"].append(f"IGN: git's ignore state changed during the run: {k}")
    moved = sorted(k for k in recorded if before.get(k) != now.get(k))
    if not moved:
        return
    out["recorded"].append(f"IGN: {moved} changed during the run (paths the step writes)")
    try:
        grown = sorted(set(CI.ignored_paths(root)) - set(snap.get("ignored") or []))
    except CI.InspectionFailed as e:
        out["inconclusive"].append(f"IGN: the paths git ignores could not be listed after the run ({e})")
        return
    if snap.get("ignored") is None:
        out["inconclusive"].append("IGN: the snapshot did not list the paths git ignored before the run")
        return
    for p in grown:
        if not writes(p) and not writes(p.rstrip("/") + "/"):
            out["E"].append(f"{p}: ignored after the run's change to {moved}, and outside the write set")


def link_or_shape(root, path):
    """Why `path` under `root` is not a plain write target now (R1-S (iii)): a component on the way is a symbolic link
    or not a folder, or the leaf exists and is not a regular file with one name. None when it is fine or absent."""
    p = Path(root)
    parts = Path(path).parts
    for i, part in enumerate(parts):
        p = p / part
        if not os.path.lexists(p):
            return None
        st = os.lstat(p)
        if stat.S_ISLNK(st.st_mode):
            return f"{p.relative_to(root)} is a symbolic link"
        if i < len(parts) - 1 and not stat.S_ISDIR(st.st_mode):
            return f"{p.relative_to(root)} is not a folder"
    if not stat.S_ISREG(st.st_mode):
        return "not a regular file"
    if st.st_nlink != 1:
        return f"has {st.st_nlink} names (a hard link)"
    return None


def check_g(a, root, calls, base, snap=None):
    """G (R1-S (iii); D-1 of design read 2: detection, not prevention). Every path the transcript shows written,
    every path changed since the launch HEAD, and every path E reads from the snapshot (a pre-existing change, and a
    .claude/ file whose digest changed, ignored by git or not; B148 finding 5) must have no link component and be a regular file with one name (or be
    absent); nothing under sessions/ may be a link; the packet's sealed stage must still equal its manifest; the
    receiver's sealed baseline must still have the digest recorded at launch and still be sealed. G cannot undo a
    write that went through a link, and it does not see a link made, written through and removed inside the
    session: that is a stated limit."""
    found, paths = [], set()
    for name, inp, executed in calls:
        if name in EDIT_TOOLS and executed:
            r = rel(root, inp.get("file_path", ""))
            if r:
                paths.add(r)
    if base:
        paths |= set(changed_paths(root, base))
    if snap:                                 # the same population E reads (B148 finding 5)
        paths |= set(snap.get("dirty") or {})
        if "claude_tree" in snap:
            before, after = snap["claude_tree"], claude_tree(root)
            paths |= {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
    for p in sorted(paths):
        why = link_or_shape(root, p)
        if why:
            found.append(f"{p}: {why}")
    sess = Path(root) / "sessions"
    if sess.is_symlink():
        found.append("sessions is a symbolic link")
    elif sess.is_dir():
        for folder, dirs, files in os.walk(sess):
            for n in dirs + files:
                if os.path.islink(os.path.join(folder, n)):
                    found.append(f"{os.path.relpath(os.path.join(folder, n), root)} is a symbolic link")
    if a.packet:
        try:
            packet = json.loads(Path(a.packet).read_text())
        except (OSError, ValueError):
            packet = {}
        pr = packet.get("packet_root")
        if pr and isinstance(packet.get("stage_manifest"), dict):
            why = CI.sealed_refusal(Path(pr) / "stage", packet["stage_manifest"])
            if why:
                found.append(f"the packet's sealed stage: {why}")
        want = getattr(a, "baseline_slot_sha256", None)
        if pr and want:
            f = Path(pr) / "baselines" / a.aget / "baseline.json"
            got = sha(f.read_bytes()) if f.is_file() and not f.is_symlink() else "absent"
            if got != want:
                found.append(f"the sealed baseline {f} is {got[:8]}; the launch recorded {want[:8]}")
            elif os.stat(f).st_mode & 0o222:
                found.append(f"the sealed baseline {f} is writable again; the seal is broken")
    return found


def judge_kept_or_merged(root, i, rule, now, out):
    """R3 after-run judgement for a KEEP or MERGE item. "pre": the file is unchanged from the item's `pre`, in the
    working tree and at HEAD (a kept file must not take the release bytes). "authored_ids": every authored line's
    identity (sha256 of the stripped line) survives in the working tree and at HEAD (M4: by identity, not by count);
    the merge itself is listed for review."""
    try:                                                 # B183 finding 1: a failed read is not "absent"
        blob = CI.git_blob_at(root, "HEAD", i["path"])
    except CI.InspectionFailed as e:
        out["inconclusive"].append(f"D: {e}")
        return
    at_head = sha(blob) if blob is not None else "absent"
    if rule == "pre":
        for where, got in (("working tree", now), ("HEAD", at_head)):
            if got != i.get("pre"):
                out["D"].append(f"{i['path']}: kept, but the {where} holds {got[:8]}, not its own bytes "
                                f"{str(i.get('pre'))[:8]}")
        return
    want = i.get("authored_ids") or []
    try:        # E2i15 (FWK-OVSR6's E2i14 pre-read 3, reproduced): a merge is a regular file, read with no link followed
        kind, wt = PF.read_entry(root, i["path"])
    except (PF.Refused, OSError, ValueError) as e:   # C2a10: a ValueError/UnicodeError is a non-reading, not a crash
        kind, wt = "unreachable", str(e)
    if kind not in ("file", "absent"):
        out["D"].append(f"{i['path']}: merged, but the working tree holds a {kind}, not a regular file")
    for where, data in (("working tree", wt if kind == "file" else b""),
                        ("HEAD", blob if blob is not None else b"")):
        have = {hashlib.sha256(ln.strip().encode()).hexdigest()
                for ln in data.decode("utf-8", "replace").splitlines() if ln.strip()}
        lost = [x for x in want if x not in have]
        if lost:
            out["D"].append(f"{i['path']}: merged, but {len(lost)} of your own line(s) are gone from the {where}")
    if not want:
        out["inconclusive"].append(f"D: {i['path']}: a merge with no recorded authored-line identities")
    out["merged"].append(f"{i['path']}: {now[:8]} (merge; compare with the receipt)")


def main(argv=None):
    """Command-line entry point: take the pre-launch settings snapshot, or run the after-run check for one receiver.
    With --json the verdict is an R2 result: with --run-id the invoker recorded the run before this process started
    (launch_batch.run_one), and the id must be the last one started for that output; without it this run records
    itself as its first act, before argument parsing (a hand re-judge). The verdict's binding names the member, the
    session judged (--session-id) and the HEAD judged, and the FINISHED row names the bytes written."""
    argv = sys.argv[1:] if argv is None else list(argv)
    out_path, given = RBND.prescan(argv, "--json"), RBND.prescan(argv, "--run-id")
    run_id = None
    if out_path is not None and RBND.prescan(argv, "--snapshot") is None:  # D2 (C2e pre-read 2): an empty value is a value (argparse takes `--x=`), never absent
        if given:
            try:
                last = RBND.last_started(STEP, out_path)
            except RBND.RunLogError as e:
                last = f"unreadable: {e}"
            if last != given:
                print(f"REFUSED: --run-id {given[:8]} is not the run last started for {out_path} ({str(last)[:8]})")
                return 2
            run_id = given
        else:
            run_id, early = RBND.producer_start(STEP, out_path, NOT_FINISHED)
            if early:
                print(early)
                return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aget", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--snapshot", type=Path, help="before launch: write the settings rule snapshot here and exit")
    ap.add_argument("--receipt")
    ap.add_argument("--snapshot-file")
    ap.add_argument("--watch-log")
    ap.add_argument("--transcript")
    ap.add_argument("--packet", help="launch packet: its WRITE items' release digests are checked (D)")
    ap.add_argument("--mode", default="dontAsk")
    ap.add_argument("--write-set", nargs="*", default=[], help="glob patterns the receiver may write")
    ap.add_argument("--allow-bash", nargs="*", default=[], help="allowed command prefixes, e.g. 'git add'")
    ap.add_argument("--allow-exact", nargs="*", default=[],
                    help="commands allowed only verbatim, e.g. a declared 'cp <staged> <path>' (a prefix would let "
                         "'cp A B C' copy into C)")
    ap.add_argument("--route", choices=["restricted-hooks"], default=None,
                    help="route-b-restricted-hooks: applies the gh#2802 ruling (clauses 1-3, see B)")
    ap.add_argument("--settings-file", help="with --route restricted-hooks: the --settings file the launch used")
    ap.add_argument("--settings-sha256", help="with --route restricted-hooks: that file's digest in the packet")
    ap.add_argument("--suite-cmd", help="F: the session's declared suite command; its last run is compared with "
                                        "--baseline-record (a migration session; not a track-skills one)")
    ap.add_argument("--baseline-record", help="F: the B6 baseline record (its `failures` list)")
    ap.add_argument("--suite-report", help="F: the kit's pytest report of the session's suite runs (the launch "
                                           "record's suite_report); without it F reads no ids and is inconclusive")
    ap.add_argument("--suite-report-token", help="F: that report's token (the launch record's suite_report_token)")
    ap.add_argument("--confirm-dir", help="F: a scratch folder (outside every receiver) where each new failure is "
                                          "re-run at the committed HEAD in a clean clone; without it F fails on any "
                                          "new failure in the session's run")
    ap.add_argument("--sibling-read", nargs="*", default=[], help="F: folders outside the Aget its tests read")
    ap.add_argument("--confirm-rev", help="F: the session's commit, when re-judging after HEAD has moved on")
    ap.add_argument("--copy-run", help="a rehearsal copy's run folder (the copy, or the folder holding it and its "
                                       "declared siblings): every symbolic link under it must still resolve inside "
                                       "it after the session (R1 LINKS), else INCONCLUSIVE")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--run-id", help="R2: the run the invoker recorded for --json before starting this process")
    ap.add_argument("--session-id", help="R2: the session this verdict judges (the launch record's session_id)")
    ap.add_argument("--baseline-slot-sha256", help="G: the digest of the receiver's sealed baseline at launch")
    ap.add_argument("--session-window", nargs=2, metavar=("START", "END"),
                    help="B: the session's start and end (epoch seconds) the settings watch must cover (R2-T11); "
                         "without it, the transcript's first and last timestamps")
    a = ap.parse_args(argv)
    if a.snapshot:
        snap = full_snapshot(a.root, a.copy_run) if a.copy_run else full_snapshot(a.root)
        a.snapshot.write_text(json.dumps(snap, indent=2) + "\n")
        print(f"snapshot written: {a.snapshot}")
        return 0
    missing = [k for k in ("receipt", "snapshot_file", "watch_log", "transcript") if not getattr(a, k)]
    if missing:
        print("INCONCLUSIVE: missing " + ", ".join("--" + m.replace("_", "-") for m in missing))
        return 3
    try:
        out = check(a)
    except CI.InspectionFailed as e:      # B158 finding 1: a git listing that cannot be read is never "no paths"
        # B159 finding 3: the full result shape, so the record and the printer read it like any other result
        out = {"aget": a.aget, "route": a.route, **{k: [] for k in "ABCDEFG"}, "read_only_allowance_used": [],
               "inconclusive": [f"a git listing could not be read: {e}"], "recorded": [], "verdict": "INCONCLUSIVE",
               "why": f"a git listing could not be read: {e}"}
    code = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 3}[out["verdict"]]
    if a.json:
        head = CI.read_git(a.root, "rev-parse", "HEAD", text=True)   # B166 finding 2
        RBND.write_result(STEP, a.json, out, run_id, code,
                          binding={"aget": a.aget, "session_id": a.session_id, "subject": head.stdout.strip()})
    print(f"{a.aget}: {out['verdict']}")
    for k in ("A", "B", "C", "D", "E", "F", "G", "inconclusive", "recorded"):
        for x in out[k]:
            print(f"  {k}: {x}")
    if out["read_only_allowance_used"]:
        print(f"  read-only allowance used by {len(out['read_only_allowance_used'])} command(s)")
    return code


if __name__ == "__main__":
    sys.exit(main())
