#!/usr/bin/env python3
"""Validate the minimal Codex-native AGET support bundle and recovery path."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED = ("aget-wake-up", "aget-study-topic", "aget-save-state")


def validate(root: Path) -> dict:
    roots = [root / ".agents" / "skills", root / ".codex" / "skills"]
    found = {}
    for name in REQUIRED:
        candidates = [base / name / "SKILL.md" for base in roots]
        path = next((candidate for candidate in candidates if candidate.is_file()), None)
        found[name] = str(path.relative_to(root)) if path else None
    errors = [f"native skill absent: {name}" for name, path in found.items() if not path]
    save_path = next((base / "aget-save-state" / "SKILL.md" for base in roots
                      if (base / "aget-save-state" / "SKILL.md").is_file()), None)
    if save_path:
        text = save_path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"recover|resume|checkpoint", text, re.I):
            errors.append("aget-save-state lacks recovery/resume contract")
    return {"state": "PASS" if not errors else "FAIL", "skills": found,
            "recovery": not any("recovery" in error for error in errors), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.root.resolve())
    print(json.dumps(result, indent=2) if args.json else f"codex-skill-discovery: {result['state']}")
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
