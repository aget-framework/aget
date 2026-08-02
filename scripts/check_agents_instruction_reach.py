#!/usr/bin/env python3
"""Verify that AGENTS.md decomposition preserves root governance reach.

The check is deliberately content-based: a smaller file is not a success if the
load-bearing controls disappear, and a nested file may add local instructions but
may not claim to replace or disable the root contract.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_ROOT_MARKERS = {
    "session_or_client_bootstrap": r"## Session Protocol|## Agent Compatibility|Wake Up Protocol",
    "write_boundary": r"## Write Scope|read-only|scoped write permissions",
    "gate_discipline": r"Gate Execution Discipline|Gate without plan update|Structural Skill Routing",
    "self_amendment_control": r"AGENTS\.md.*governance instruction surface|governance instruction surface itself",
}
FORBIDDEN_NESTED = (
    r"ignore (?:the )?(?:root|parent) AGENTS\.md",
    r"override (?:the )?(?:root|parent) AGENTS\.md",
    r"root AGENTS\.md does not apply",
)


def check_repo(root: Path, max_bytes: int = 40_000) -> dict:
    root = root.resolve()
    agent_file = root / "AGENTS.md"
    errors: list[str] = []
    if not agent_file.is_file():
        return {"state": "FAIL", "root": str(root), "errors": ["root AGENTS.md absent"]}

    text = agent_file.read_text(encoding="utf-8", errors="replace")
    position = root / "docs" / "POSITION_agents_instruction_reach_and_self_amendment.md"
    contract_text = text + ("\n" + position.read_text(encoding="utf-8", errors="replace")
                            if position.is_file() else "")
    size = agent_file.stat().st_size
    if size > max_bytes:
        errors.append(f"root AGENTS.md is {size} bytes; limit is {max_bytes}")
    markers = {name: bool(re.search(pattern, contract_text, re.I | re.S))
               for name, pattern in REQUIRED_ROOT_MARKERS.items()}
    errors.extend(f"missing root marker: {name}" for name, present in markers.items() if not present)

    nested = []
    for path in sorted(root.rglob("AGENTS.md")):
        if path == agent_file or ".git" in path.parts:
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        violations = [pattern for pattern in FORBIDDEN_NESTED if re.search(pattern, body, re.I)]
        if violations:
            errors.append(f"{path.relative_to(root)} weakens root reach")
        nested.append({"path": str(path.relative_to(root)), "violations": len(violations)})

    return {
        "state": "PASS" if not errors else "FAIL",
        "root": str(root),
        "root_bytes": size,
        "max_bytes": max_bytes,
        "markers": markers,
        "nested": nested,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="*", type=Path, default=[Path.cwd()])
    parser.add_argument("--max-bytes", type=int, default=40_000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = [check_repo(root, args.max_bytes) for root in args.roots]
    payload = {"state": "PASS" if all(r["state"] == "PASS" for r in results) else "FAIL",
               "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"agents-instruction-reach: {payload['state']}")
        for result in results:
            print(f"  {result['root']}: {result['state']} ({result.get('root_bytes', 0)} bytes)")
            for error in result.get("errors", []):
                print(f"    - {error}")
    return 0 if payload["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
