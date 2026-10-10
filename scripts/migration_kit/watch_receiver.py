#!/usr/bin/env python3
"""watch_receiver.py — wait on a receiver without polling by hand (R-F16, rehearsal 2026-09-30).

The procedure tells a supervisor to watch a receiver's last turn as well as its HEAD. Without a tool for it, the
rehearsal's supervisor ended its own turn on a receiver act and then waited on nothing. This tool reads a receiver
and exits on the FIRST of:

  turn-ended    the receiver's session finished a turn (its transcript gained an assistant entry that ends the turn;
                a tool call does not count)
  head-moved    the receiver's HEAD changed
  remote-moved  the receiver's remote branch changed

It is read-only: `git rev-parse`, `git log` and `git ls-remote` on the receiver, and reads of its transcripts. It
writes nothing to the receiver and needs no typed line.

Several sessions in one receiver folder. A turn end belongs to a session; HEAD and the remote belong to the checkout.
Every turn-ended event names its session (the transcript's name), and `--session <id or its first characters>`
watches one session's turns only. A head-moved event prints the new commit's subject, because in a shared checkout
another session's commit moves HEAD too and git cannot say which session made it. The procedure's membership step
asks for no other live session in a receiver's folder; this tool does not assume it.

Usage:
    python3 scripts/migration_kit/watch_receiver.py <receiver repository> [--session ID] [--ref refs/heads/main]
        [--interval 5] [--remote-interval 30] [--timeout 3600] [--projects-dir DIR]

Exit codes: 0 an event was seen (printed as `EVENT <kind>: <before> -> <after>`); 2 a probe failed (printed as
`PROBE-FAILED ...`; never read as "no change"); 3 the timeout passed with no event.

Rule (SOP_fleet_migration): a supervisor never ends its turn on a receiver act without this watcher armed.
"""
from __future__ import annotations

import argparse
import json
import re
import os
import subprocess
import sys
import time
from pathlib import Path

END_OF_TURN = "end_turn"


class ProbeFailed(Exception):
    pass


def projects_dir_for(repo: Path) -> Path:
    """Where Claude Code keeps a repository's transcripts: its path with every non-alphanumeric character as "-"."""
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path(repo).resolve()))


def _git(repo, *args) -> str:
    try:
        r = subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "-C", str(repo), *args], capture_output=True,
                           text=True, timeout=25, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"})  # B166 finding 2: a read that leaves the git folder as it was
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeFailed(f"git {args[0]}: {type(exc).__name__}") from exc
    if r.returncode != 0:
        raise ProbeFailed(f"git {args[0]} exit {r.returncode}: {r.stderr.strip()[:120]}")
    return r.stdout.strip()


def head(repo) -> str:
    """Return the repository's current HEAD commit."""
    return _git(repo, "rev-parse", "HEAD")


def remote(repo, ref) -> str:
    """The remote's commit for the ref; an empty answer (no such ref yet) is a value, not a failure."""
    return _git(repo, "ls-remote", "origin", ref).split("\t")[0]


_COUNTS: dict = {}   # transcript path -> ((size, mtime_ns), turn ends); re-read a file only when it changed


def subject(repo, rev) -> str:
    """Return the subject line of the given revision's commit."""
    return _git(repo, "log", "-1", "--format=%s", rev)


def turn_ends(projects: Path, session=None):
    """{session: turn ends} for a receiver's transcripts (one transcript per session, named by its file), or None
    when there is nothing to read: no transcript folder, or no transcript whose name starts with `session`."""
    if not projects.is_dir():
        return None
    out = {}
    for f in sorted(projects.glob("*.jsonl")):
        if session and not f.stem.startswith(session):
            continue
        st = f.stat()
        key = (st.st_size, st.st_mtime_ns)
        cached = _COUNTS.get(str(f))
        if cached and cached[0] == key:
            out[f.stem] = cached[1]
            continue
        n = 0
        with f.open() as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                m = r.get("message")
                if r.get("type") == "assistant" and isinstance(m, dict) and m.get("stop_reason") == END_OF_TURN:
                    n += 1
        _COUNTS[str(f)] = (key, n)
        out[f.stem] = n
    return out or (None if session else out)


def _short(v):
    return v[:8] if isinstance(v, str) and len(v) >= 8 else v


def watch(repo, ref, projects, *, interval=5, remote_interval=30, timeout=3600, say=print, sleep=time.sleep,
          clock=time.time, session=None) -> int:
    """Wait until the receiver ends a turn or its HEAD or remote moves; return 0 on an event, 2 if a probe fails, 3 on timeout."""
    repo, projects = Path(repo), Path(projects)
    try:
        base = {"head": head(repo), "remote": remote(repo, ref)}
    except ProbeFailed as exc:
        say(f"PROBE-FAILED at arming: {exc}")
        return 2
    base["turns"] = turn_ends(projects, session)
    watching = "n/a" if base["turns"] is None else (
        f"session {session}" if session else f"{len(base['turns'])} session transcripts")
    say(f"armed: {repo.resolve().name} HEAD {_short(base['head'])}, remote {_short(base['remote']) or '(none)'}, "
        f"turn ends watched: {watching}")
    if base["turns"] is None:
        what = f"no transcript named {session}* at {projects}" if session else f"no transcripts at {projects}"
        say(f"turn-end UNAVAILABLE: {what}; watching HEAD and remote only")
    start = last_remote = clock()
    while True:
        sleep(interval)
        now = clock()
        try:
            h = head(repo)
            if h != base["head"]:
                say(f"EVENT head-moved: {_short(base['head'])} -> {_short(h)} \"{subject(repo, h)[:80]}\"")
                return 0
            if now - last_remote >= remote_interval:
                last_remote = now
                rm = remote(repo, ref)
                if rm != base["remote"]:
                    say(f"EVENT remote-moved: {_short(base['remote']) or '(none)'} -> {_short(rm) or '(none)'}")
                    return 0
        except ProbeFailed as exc:
            say(f"PROBE-FAILED: {exc}")
            return 2
        t = turn_ends(projects, session)
        if t is not None and base["turns"] is not None:
            ended = [(sid, base["turns"].get(sid, 0), n) for sid, n in sorted(t.items()) if n > base["turns"].get(sid, 0)]
            if ended:
                for sid, was, n in ended:
                    say(f"EVENT turn-ended: session {sid} ({was} -> {n})")
                return 0
        if base["turns"] is None and t is not None:   # the watched transcript appeared after arming
            base["turns"] = {sid: 0 for sid in t}
        if now - start >= timeout:
            say(f"TIMEOUT after {int(now - start)}s with no event")
            return 3


def main(argv=None) -> int:
    """Command-line entry point: wait on a receiver's turn end, HEAD move or remote move."""
    ap = argparse.ArgumentParser(description="Exit on a receiver's turn end, HEAD move or remote move (read-only).")
    ap.add_argument("repo", help="the receiver's repository")
    ap.add_argument("--ref", default="refs/heads/main")
    ap.add_argument("--interval", type=float, default=5)
    ap.add_argument("--remote-interval", type=float, default=30)
    ap.add_argument("--timeout", type=float, default=3600)
    ap.add_argument("--projects-dir", help="the receiver's transcript folder (default: derived from its path)")
    ap.add_argument("--session", help="watch this session's turns only (its id, or the id's first characters)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).expanduser()
    projects = Path(a.projects_dir).expanduser() if a.projects_dir else projects_dir_for(repo)

    def say(msg):
        print(time.strftime("%H:%M:%S"), msg, flush=True)

    return watch(repo, a.ref, projects, interval=a.interval, remote_interval=a.remote_interval, timeout=a.timeout,
                 say=say, session=a.session)


if __name__ == "__main__":
    sys.exit(main())
