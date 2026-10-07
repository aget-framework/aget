#!/usr/bin/env python3
"""open_receiver.py — open an Aget's OWN session with the principal's line as its first message.

Kit version of the supervisor's decision-sheet opener (v3.35 migration, 2026-09-29). Three guards, each from a failure:

1. **Typed line or named pre-authorization** (principal ruling `outside-filers:R9` / `namedpreauth`, 2026-09-29): on
   2026-09-29 the supervisor opened two receiver windows with no typed line from the principal (read-backs refused,
   nothing sent). A window opens only if (a) a person types `OPEN <key>` at a real terminal now, or (b) a
   pre-authorization record names exactly this receiver key AND this batch, says it is the principal's (`authorized_by`), has
   a non-empty `typed_line` field and has not expired. Anything else is refused. The record is a plain file: its origin is
   not checked, the `typed_line` value is not compared with anything, and no session record is read.
2. **The Aget has not moved** since its line was checked (the framework Aget's review, L1722): "push your own N commits"
   checked against one HEAD must not authorize whatever is there later.
3. **Never from inside a Claude Code session** (it would nest).

Receivers are DATA, not code: `--receivers <file.json>` maps key -> {folder, line, facts, expect: {head, ahead}}.
The v3.35 per-Aget lines stay with the supervisor that wrote them; the kit carries the mechanism.

Usage:
  open_receiver.py --receivers R.json                              # list keys
  open_receiver.py --receivers R.json <key>                        # typed confirmation at a terminal
  open_receiver.py --receivers R.json <key> --batch B --preauth P.json   # named pre-authorization
Exit: 0 exec'd · 2 usage/environment · 3 moved since checked · 4 not authorized
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

LINES: dict = {}   # key -> (folder, line, facts, expect); filled from --receivers (kept as a dict for tests)


def load_receivers(path: Path) -> dict:
    """Read the receivers file and return, per key, the folder, line, facts and expected text."""
    data = json.loads(Path(path).read_text())
    return {k: (v["folder"], v["line"], v.get("facts", ""), v["expect"]) for k, v in data.items()}


def state(folder):
    """(HEAD, commits above its upstream) as the folder reads now."""
    g = lambda *a: subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "-C", folder, *a],   # B166 #2
                                  capture_output=True, text=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}).stdout.strip()
    ahead = g("rev-list", "--count", "@{upstream}..HEAD")
    return g("rev-parse", "HEAD"), int(ahead) if ahead.isdigit() else None


def preauthorized(preauth: Path | None, key: str, batch: str | None, now: dt.datetime) -> tuple[bool, str]:
    """A pre-authorization counts only if it names this key AND this batch, says `authorized_by: principal`, has a
    non-empty `typed_line` field and is unexpired. The file's origin is not checked."""
    if preauth is None:
        return False, "no pre-authorization given"
    if not batch:
        return False, "a pre-authorization must be used with --batch (it names a window AND a batch)"
    try:
        entries = json.loads(Path(preauth).read_text()).get("entries", [])
    except (OSError, ValueError) as e:
        return False, f"pre-authorization unreadable: {e}"
    for e in entries:
        if e.get("key") != key or e.get("batch") != batch:
            continue
        if e.get("authorized_by") != "principal" or not str(e.get("typed_line", "")).strip():
            return False, f"entry for {key}/{batch} is not a principal's typed authorization"
        try:
            expires = dt.datetime.fromisoformat(e["expires"])
        except (KeyError, ValueError):
            return False, f"entry for {key}/{batch} has no valid expiry"
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=dt.timezone.utc)
        if now > expires:
            return False, f"entry for {key}/{batch} expired {e['expires']}"
        return True, f"pre-authorized by the principal: {e['typed_line']!r}"
    return False, f"no pre-authorization names key {key!r} with batch {batch!r}"


def typed_now(key: str, stdin=None) -> tuple[bool, str]:
    """A typed line at a real terminal, now: the person types OPEN <key>."""
    stdin = stdin or sys.stdin
    if not stdin.isatty():
        return False, "not a terminal: a typed line needs a person at a terminal (or use --preauth with --batch)"
    try:
        got = input(f"Type  OPEN {key}  to open this Aget's session: ").strip()
    except EOFError:
        return False, "no input"
    return (got == f"OPEN {key}"), ("typed" if got == f"OPEN {key}" else f"typed {got!r}, expected 'OPEN {key}'")


def main(argv, now=None, stdin=None):
    """Command-line entry point: open one Aget's own session with the principal's line as its first message."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("key", nargs="?")
    ap.add_argument("--receivers", type=Path)
    ap.add_argument("--batch")
    ap.add_argument("--preauth", type=Path)
    a = ap.parse_args(argv)
    if a.receivers:
        LINES.clear()
        LINES.update(load_receivers(a.receivers))
    if not a.key or a.key not in LINES:
        print("keys:", ", ".join(sorted(LINES)) or "(none: pass --receivers)")
        return 2
    folder, line, facts, expect = LINES[a.key]
    if os.environ.get("CLAUDECODE"):
        print("run this from a plain terminal, not from inside a Claude Code session (it would nest)")
        return 2
    if not os.path.isdir(folder) or not shutil.which("claude"):
        print(f"cannot open: folder {folder} or the claude command is missing")
        return 2
    head, ahead = state(folder)
    if head != expect["head"] or ahead != expect["ahead"]:
        print(f"REFUSED: {a.key} moved since its line was checked. Expected HEAD {expect['head'][:8]} with "
              f"{expect['ahead']} above upstream; now HEAD {head[:8]} with {ahead}. Ask the supervisor to re-check.")
        return 3
    now = now or dt.datetime.now(dt.timezone.utc)
    if a.preauth is not None:
        ok, why = preauthorized(a.preauth, a.key, a.batch, now)
    else:
        ok, why = typed_now(a.key, stdin)
    if not ok:
        print(f"NOT AUTHORIZED: {why}. Opening another Aget's window needs the principal's typed line or a "
              f"pre-authorization naming the window and the batch (outside-filers:R9).")
        return 4
    print(f"Opening {folder} ({why})\nFirst message:\n  {line}\nFacts behind it: {facts}\n")
    os.chdir(folder)
    os.execvp("claude", ["claude", line])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
