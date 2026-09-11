#!/usr/bin/env python3
"""The routing consumer: build the skill index a harness routes on, from an agent tree.

C-34-01 / gh#2445, acceptance clause P-2 — "Verify actual routing description at a
consumer."

WHY THIS EXISTS. Before this file there was no consumer in canonical that routed on
`description`. Every existing check audited PRESENCE: validate_archetype_skills counted
skills and looked for SKILL.md; check_skill_route_contract resolves /aget-* references;
validate_codex_skill_discovery checks three named skills exist. None of them routes. So
the C-34-01 clause could not be verified at a consumer, because there was no consumer --
and a check that re-parses frontmatter the same way the validator does is not one, it is
the validator wearing a different hat.

WHAT IT MODELS. A harness discovers skills by reading each SKILL.md's YAML frontmatter
and indexing `name` -> `description`, then selects a skill by matching the user's phrasing
against those descriptions. That is the whole contract this file implements. A skill whose
frontmatter is absent or unparseable never enters the index, so it cannot be selected: it
is installed, visible on disk, and unreachable. That is the defect C-34-01 names.

LIMITS, STATED. This is a faithful model of description-based routing, not the harness
itself. It uses lexical overlap where a harness uses a model. It therefore proves
REACHABILITY -- that a repaired skill enters the index and can be selected by its
description, and that a defective one cannot -- and it does NOT prove that any particular
harness would choose the same skill for the same sentence. Reachability is what the clause
asks for; ranking quality is not claimed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is",
    "it", "its", "of", "on", "or", "that", "the", "this", "to", "when", "with", "use",
    "used", "user", "using", "you", "your",
}


def _tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP and len(w) > 2}


def build_index(agent_path: Path) -> dict:
    """Index every ROUTABLE skill under <agent_path>/.claude/skills.

    Returns {"routable": {name: description}, "unroutable": [{"skill":…, "reason":…}]}.
    A skill is routable iff its frontmatter parses AND yields a non-empty description --
    exactly the condition the scaffold gate now enforces.
    """
    routable, unroutable = {}, []
    skills_dir = agent_path / ".claude" / "skills"
    if not skills_dir.is_dir():
        return {"routable": routable, "unroutable": unroutable, "state": "UNREACHABLE"}

    for skill in sorted(q for q in skills_dir.iterdir() if q.is_dir()):
        f = skill / "SKILL.md"
        if not f.is_file():
            unroutable.append({"skill": skill.name, "reason": "no SKILL.md"})
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            unroutable.append({"skill": skill.name, "reason": "frontmatter-absent"})
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            unroutable.append({"skill": skill.name, "reason": "frontmatter-unterminated"})
            continue
        try:
            import yaml
            meta = yaml.safe_load(parts[1])
        except Exception:
            unroutable.append({"skill": skill.name, "reason": "frontmatter-unparseable"})
            continue
        if not isinstance(meta, dict):
            unroutable.append({"skill": skill.name, "reason": "frontmatter-not-a-mapping"})
            continue
        # Same `str(...)` coercion hole the scaffold gate carried: a YAML null would have
        # been indexed as the routable string "None". A non-string description is not
        # routable text, so it is unroutable here for the same reason it is a defect there.
        desc = meta.get("description")
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            unroutable.append({"skill": skill.name, "reason": "description-empty-or-absent"})
            continue
        if not isinstance(desc, str):
            unroutable.append({"skill": skill.name, "reason": "description-not-a-string"})
            continue
        desc = desc.strip()
        routable[str(meta.get("name") or skill.name)] = desc

    return {"routable": routable, "unroutable": unroutable, "state": "OK"}


def route(index: dict, query: str):
    """Select the best-matching skill by DESCRIPTION overlap. None if nothing matches.

    Deliberately scores the description only -- never the skill name. Scoring the name
    would let a skill route correctly while its description was broken, which is the exact
    failure this consumer exists to detect.
    """
    q = _tokens(query)
    if not q:
        return None
    best, best_score = None, 0
    for name, desc in index.get("routable", {}).items():
        score = len(q & _tokens(desc))
        if score > best_score:
            best, best_score = name, score
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("agent_path", type=Path)
    ap.add_argument("--route", help="A query to route against the built index")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    index = build_index(args.agent_path.resolve())
    if args.route:
        index["query"] = args.route
        index["routed_to"] = route(index, args.route)
    if args.json:
        print(json.dumps(index, indent=2))
    else:
        print(f"routable: {len(index['routable'])}  unroutable: {len(index['unroutable'])}")
        for u in index["unroutable"]:
            print(f"  UNROUTABLE [{u['reason']}] {u['skill']}")
        if args.route:
            print(f"  route({args.route!r}) -> {index.get('routed_to')}")
    if index["state"] == "UNREACHABLE":
        return 2
    return 0 if not index["unroutable"] else 1


if __name__ == "__main__":
    sys.exit(main())
