#!/usr/bin/env python3
"""Isolated Codex PreToolUse outcome POC for v3.29.

Input is one JSON object on stdin. The POC is intentionally pure: it returns a
decision and never executes the proposed command. Exit 2 means block.
"""
from __future__ import annotations

import json
import re
import sys

SENSITIVE = re.compile(
    r"(?:^|[/\s])(?:AGENTS\.md|CLAUDE\.md|\.codex/(?:config\.toml|hooks(?:\.json)?|skills)|"
    r"\.agents/skills|\.claude/(?:settings(?:\.local)?\.json|hooks|skills))(?:$|/|\s)", re.I
)


def decide(event: dict) -> dict:
    trusted = bool(event.get("trusted", False))
    target = str(event.get("path") or event.get("command") or "")
    affirmed = bool(event.get("affirmed", False))
    if not trusted:
        return {"decision": "unavailable", "reason": "project-untrusted-hooks-not-loaded"}
    if SENSITIVE.search(target) and not affirmed:
        return {"decision": "block", "reason": "individual-affirmation-required"}
    return {"decision": "allow", "reason": "ordinary-operation" if not SENSITIVE.search(target)
            else "individually-affirmed"}


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
