#!/usr/bin/env python3
"""create_goal.py — testable engine for /aget-create-goal (SKILL-057).

Implements the verifiable core of AGET_GOAL_SPEC v0.2.0:
- CAP-GOAL-002 conflation guard (outcome-not-workstream)
- CAP-GOAL-003 typing {Achieve, Maintain, Soft}
- CAP-GOAL-004 ≥1 bound loop required at creation
- CAP-GOAL-006 two-tier storage (committed=section in governance/GOALS.md; aspirational=.aget/goals/aspirational.jsonl)
- CAP-GOAL-008 provenance field (enables D71-Strict bypass detection)
- CAP-GOAL-011 lifecycle + type-differentiated terminal (Maintain has no `achieved`)

The SKILL.md orchestrates; this module is the falsifiable engine (ADR-007).
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

GOAL_TYPES = {"Achieve", "Maintain", "Soft"}
STATUSES = {"active", "achieved", "abandoned", "superseded"}
# CAP-GOAL-002: a definition that enumerates workstreams/tasks rather than naming an outcome.
_WORKSTREAM_MARKERS = re.compile(
    r"\b(stream|workstream|task|tasks|step\s*\d|phase\s*\d|then\s+do|todo|backlog|sprint)\b",
    re.IGNORECASE,
)
_OUTCOME_HINT = re.compile(
    r"\b(is|are|reaches?|achieves?|maintains?|stays?|remains?|<=|>=|%|reduced?|increased?|zero|no\s+more)\b",
    re.IGNORECASE,
)


class GoalError(ValueError):
    """Raised when a candidate Goal violates AGET_GOAL_SPEC."""


def validate_outcome(outcome: str) -> None:
    """CAP-GOAL-002: reject a 'goal' defined by workstreams not an outcome."""
    if not outcome or not outcome.strip():
        raise GoalError("CAP-GOAL-002: outcome is empty")
    has_streams = bool(_WORKSTREAM_MARKERS.search(outcome))
    has_outcome = bool(_OUTCOME_HINT.search(outcome))
    # Conflation = enumerates streams AND names no measurable end-state.
    if has_streams and not has_outcome:
        raise GoalError(
            "CAP-GOAL-002 conflation (C930): outcome enumerates workstreams/tasks but names "
            "no measurable end-state. A Goal is an outcome, not a task list."
        )


def validate_type(goal_type: str) -> None:
    if goal_type not in GOAL_TYPES:
        raise GoalError(f"CAP-GOAL-003: type must be one of {sorted(GOAL_TYPES)}, got {goal_type!r}")


def validate_loops(loops: list[dict]) -> None:
    """CAP-GOAL-004: ≥1 loop, each a full 5-tuple."""
    if not loops:
        raise GoalError("CAP-GOAL-004: a Goal requires ≥1 bound loop at creation (MP#12)")
    required = {"owner", "trigger", "review_action", "consequence", "cadence"}
    for i, loop in enumerate(loops):
        missing = required - set(loop)
        if missing:
            raise GoalError(f"CAP-GOAL-004: loop[{i}] missing tuple fields {sorted(missing)}")


def validate_transition(goal_type: str, new_status: str) -> None:
    """CAP-GOAL-011: type-differentiated terminal — a Maintain Goal has no `achieved`."""
    if new_status not in STATUSES:
        raise GoalError(f"CAP-GOAL-011: status must be one of {sorted(STATUSES)}, got {new_status!r}")
    if goal_type == "Maintain" and new_status == "achieved":
        raise GoalError(
            "CAP-GOAL-011: a Maintain Goal cannot transition to `achieved` (it persists under its "
            "loop; terminate via abandoned/superseded). An 'achieved' Maintain Goal is a category error."
        )


def build_committed_section(goal: dict, provenance: str) -> str:
    """CAP-GOAL-006a: structured section-per-goal for governance/GOALS.md."""
    validate_outcome(goal["outcome"])
    validate_type(goal["type"])
    validate_loops(goal["loops"])
    validate_transition(goal["type"], goal.get("status", "active"))
    lines = [
        f"### {goal['id']} — {goal['outcome']}",
        "",
        f"- **type**: {goal['type']}",
        f"- **status**: {goal.get('status', 'active')}",
        "- **commitment**: committed",
        f"- **parent**: {goal.get('parent', '(none)')}",
        f"- **provenance**: {provenance}",
        "- **loops**:",
    ]
    for lp in goal["loops"]:
        lines.append(
            f"  - ⟨owner={lp['owner']}, trigger={lp['trigger']}, "
            f"review={lp['review_action']}, consequence={lp['consequence']}, cadence={lp['cadence']}⟩"
        )
    lines.append("")
    return "\n".join(lines)


def commit_goal(goal: dict, goals_md: Path, provenance: str) -> str:
    """Write a committed Goal section to governance/GOALS.md (idempotent on id)."""
    section = build_committed_section(goal, provenance)
    goals_md.parent.mkdir(parents=True, exist_ok=True)
    existing = goals_md.read_text() if goals_md.exists() else "# GOALS — Committed Goal Registry\n\n"
    if f"### {goal['id']} " in existing:
        raise GoalError(f"Goal id {goal['id']} already committed (idempotency guard)")
    goals_md.write_text(existing.rstrip() + "\n\n" + section)
    return section


def append_aspirational(goal: dict, store: Path) -> None:
    """CAP-GOAL-006b: aspirational goals go agent-internal, NOT to governance/GOALS.md."""
    store.parent.mkdir(parents=True, exist_ok=True)
    rec = {**goal, "commitment": "aspirational"}
    with store.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: create_goal.py <goal.json> [--aspirational]", file=sys.stderr)
        return 2
    goal = json.loads(Path(argv[1]).read_text())
    if "--aspirational" in argv:
        append_aspirational(goal, Path(".aget/goals/aspirational.jsonl"))
        print(f"aspirational goal recorded: {goal.get('id', '(unnamed)')}")
        return 0
    section = commit_goal(goal, Path("governance/GOALS.md"), provenance="create_goal.py CLI")
    print(section)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
