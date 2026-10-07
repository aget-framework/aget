#!/usr/bin/env python3
"""Was a principal line TYPED? (the principal's `typedonly` ruling, 2026-09-29 00:04:34 PDT). READ-ONLY.

Claude Code records each user prompt with a `promptSource`: 'typed' (typed or pasted) or 'suggestion_accepted' (a
prefilled suggestion the principal accepted). On 2026-09-28 four ruling lines in one session were accepted suggestions
while the plan recorded them as typed. Under `typedonly`, an approval, launch or push line, or a ruling that batch 8
relies on, counts only when typed. This reads the session transcript and reports the source of the newest prompt it
reads (see prompts()) that contains the given text.

Exit 0: the newest match is typed. Exit 1: not typed (e.g. an accepted suggestion). Exit 2: no match or no transcript.
Exit 4: a human-origin mid-turn entry, whose promptSource this tool does not read (accept only with that disclosed).
Exit 5: the newest match is the session's FIRST prompt (R-F1, rehearsal 2026-09-30). A prompt passed at launch
(`claude "..."`) is recorded exactly like a typed one; only its position differs (turnPosition.promptIndex 1, or the
first user prompt read from the file when that field is absent). Whoever launches the session writes it, so it is never
the principal's typed authority: the principal types the line again once the session is running.

Usage: python3 scripts/migration_kit/check_principal_line.py --session <id or prefix>
           --contains "approve list batch-8 c69fe0cf" [--projects-dir DIR]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import os

# The supervisor running the kit is the repository the kit sits in (<root>/scripts/migration_kit/). Claude Code keeps
# that repository's transcripts under ~/.claude/projects/<its path, every non-alphanumeric character as "-">. The
# staged copy named one laptop's supervisor here; a remote supervisor has another path (carriage row 62, 2026-09-30).
# AGET_MIGRATION_PROJECTS_DIR overrides it.
KIT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = Path(os.environ.get("AGET_MIGRATION_PROJECTS_DIR") or
                   Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(KIT_ROOT)))


PASTED = re.compile(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", re.S)
QUEUED_HUMAN = "queued-human"   # a mid-turn entry: origin.kind human, no promptSource recorded (2026-09-29)
LAUNCH_POSITION = "launch-position"   # R-F1: the session's first prompt, which a launch argument also produces


def prompts(path):
    """(timestamp, source, text) for each principal entry that is read: non-meta user records whose content is a plain
    string (source = promptSource, or LAUNCH_POSITION for a typed first prompt; a record whose content is not a string
    is skipped) and mid-turn queued commands whose origin is human and whose prompt is a string (source =
    QUEUED_HUMAN). Text inside a <pasted_content> block is removed when the entry has other text (see own_text):
    a paste that QUOTES a proposed line (batch 8: the framework Aget's suggested ruling, pasted for review at 10:07) is
    not the principal's line (a false TYPED, 2026-09-29)."""
    out = []
    seen_user = False
    for line in path.open():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "user" and not r.get("isMeta"):
            c = r.get("message", {}).get("content")
            if isinstance(c, str):
                index = (r.get("turnPosition") or {}).get("promptIndex")
                first = index == 1 if index is not None else not seen_user
                seen_user = True
                source = LAUNCH_POSITION if first and r.get("promptSource") == "typed" else r.get("promptSource")
                out.append((r.get("timestamp", ""), source, own_text(c)))
        elif r.get("type") == "attachment" and isinstance(r.get("attachment"), dict):
            at = r["attachment"]
            if (at.get("type") == "queued_command" and (at.get("origin") or {}).get("kind") == "human"
                    and isinstance(at.get("prompt"), str)):
                out.append((at.get("timestamp") or r.get("timestamp", ""), QUEUED_HUMAN, own_text(at["prompt"])))
    return out


def own_text(s):
    """The principal's own words in an entry. A paste inside other words is a quote and is removed (2026-09-29 10:07:
    "write G1 more formally" + a pasted peer message quoting a proposed ruling). An entry that is ONLY a paste is the
    principal's line (2026-09-29 13:06, the batch 9t approval pasted alone; 2026-09-28, 701024bd's approval)."""
    rest = PASTED.sub("", s)
    if rest.strip():
        return rest
    return re.sub(r"</?pasted_content[^>]*>", "", s)


def normalize(s):
    """Collapse every run of whitespace in the string to a single space."""
    return " ".join(s.split())


def check(files, needle):
    """Return (code, hit) for the newest matching prompt: 0 verified typed, 2 no match, other codes lack verified typed provenance."""
    hits = [p for f in files for p in prompts(f) if normalize(needle) in normalize(p[2])]
    if not hits:
        return 2, None
    newest = max(hits, key=lambda p: p[0])
    return {"typed": 0, QUEUED_HUMAN: 4, LAUNCH_POSITION: 5}.get(newest[1], 1), newest


def main(argv=None):
    """Command-line entry point: report whether a principal line in one session's transcript was typed."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="the session id, or a unique prefix of it")
    ap.add_argument("--contains", required=True, help="exact text the principal's line must contain")
    ap.add_argument("--projects-dir", type=Path, default=DEFAULT_DIR)
    a = ap.parse_args(argv)
    files = sorted(a.projects_dir.glob(f"{a.session}*.jsonl"))
    if len(files) != 1:
        print(f"NO TRANSCRIPT: {len(files)} file(s) match {a.session!r} in {a.projects_dir}")
        return 2
    code, hit = check(files, a.contains)
    if hit is None:
        print(f"NO MATCH: no principal prompt contains {a.contains!r}")
    else:
        verdict = {0: "TYPED", 4: "HUMAN (MID-TURN; SOURCE NOT RECORDED)",
                   5: "FIRST PROMPT (MAY BE A LAUNCH ARGUMENT; TYPE IT AGAIN)"}.get(code, "NOT TYPED")
        source = "promptSource='typed' at the session's first prompt" if code == 5 else f"promptSource={hit[1]!r}"
        print(f"{verdict}: {hit[0]} {source} | {hit[2][:160]!r}")
    return code


if __name__ == "__main__":
    sys.exit(main())
