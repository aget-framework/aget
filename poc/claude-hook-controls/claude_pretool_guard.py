#!/usr/bin/env python3
"""Isolated Claude Code PreToolUse outcome POC for the v3.29 client matrix.

The input is one JSON tool event on stdin. The POC is pure: it returns a
decision and never executes the proposed operation. Exit 2 means block.
"""
from __future__ import annotations

import json
import re
import sys


SENSITIVE = re.compile(
    r"(?:^|[/\s])(?:AGENTS\.md|CLAUDE\.md|\.claude/(?:settings(?:\.local)?\.json|hooks|skills))"
    r"(?:$|/|\s)",
    re.I,
)


def decide(event: dict) -> dict:
    target = str(event.get("path") or event.get("command") or "")
    affirmed = bool(event.get("affirmed", False))
    if SENSITIVE.search(target) and not affirmed:
        return {"decision": "block", "reason": "individual-affirmation-required"}
    return {
        "decision": "allow",
        "reason": "individually-affirmed" if SENSITIVE.search(target) else "ordinary-operation",
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"decision": "block", "reason": f"invalid-event:{exc}"}))
        return 2
    result = decide(event)
    print(json.dumps(result, sort_keys=True))
    return 2 if result["decision"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
