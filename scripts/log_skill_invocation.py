#!/usr/bin/env python3
"""
Skill Invocation Logger — Telemetry for AGET Skills

Appends a structured record to skill_invocations.jsonl each time a skill
completes. Provides data for RUBRIC_skill_invocation_value scoring and
skill lifecycle management.

Implements: Skill Telemetry Infrastructure (G1.4, v3.13.0)
Related: RUBRIC_skill_invocation_value v1.2.0, L819 (skill count governance)

Usage (from skill execution):
    python3 scripts/log_skill_invocation.py \\
        --skill aget-release-build \\
        --version 0.2.0 \\
        --outcome success \\
        --duration-seconds 45 \\
        --notes "G1 Builder perspective, 4/4 deliverables"

    python3 scripts/log_skill_invocation.py \\
        --skill aget-expand-ontology \\
        --version 2.1.0 \\
        --outcome partial \\
        --duration-seconds 120 \\
        --notes "Counter-perspective ratio below threshold"

Exit Codes:
    0 - Record appended successfully
    1 - Error (missing args, write failure)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def find_agent_root() -> Path:
    """Find the agent root directory."""
    current = Path(__file__).resolve().parent.parent
    if (current / '.aget').is_dir():
        return current
    for parent in current.parents:
        if (parent / '.aget').is_dir():
            return parent
    return current


def main():
    parser = argparse.ArgumentParser(
        description="Log a skill invocation for telemetry"
    )
    parser.add_argument("--skill", required=True, help="Skill name (e.g., aget-release-build)")
    parser.add_argument("--version", required=True, help="Skill version (e.g., 0.2.0)")
    parser.add_argument(
        "--outcome", required=True,
        choices=["success", "partial", "failed", "skipped"],
        help="Invocation outcome",
    )
    parser.add_argument("--duration-seconds", type=int, default=0, help="Duration in seconds")
    parser.add_argument("--notes", default="", help="Brief notes about the invocation")
    parser.add_argument("--session", default="", help="Session identifier")
    parser.add_argument("--gate", default="", help="Gate context (e.g., G1)")
    args = parser.parse_args()

    agent_root = find_agent_root()
    log_dir = agent_root / ".aget" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "skill_invocations.jsonl"

    record = {
        "timestamp": datetime.now().isoformat(),
        "skill": args.skill,
        "version": args.version,
        "outcome": args.outcome,
        "duration_seconds": args.duration_seconds,
        "notes": args.notes,
    }
    if args.session:
        record["session"] = args.session
    if args.gate:
        record["gate"] = args.gate

    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(f"Logged: {args.skill} v{args.version} [{args.outcome}]")
        sys.exit(0)
    except Exception as e:
        print(f"Error logging invocation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
