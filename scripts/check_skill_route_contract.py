#!/usr/bin/env python3
"""Route-contract check: does every /aget-* route a skill points at exist?

Ruling **D-IG-12** (2026-08-04). Measured that day: four routes were named by
live skills and absent from disk --

    /aget-enhance-initiative   <- referenced by aget-close-initiative
    /aget-enhance-config       <- referenced by aget-check-config AND aget-enhance-health
    /aget-enhance-ci           <- referenced by aget-enhance-health
    /aget-enhance-coherence    <- referenced by aget-enhance-health

`aget-check-config` advertises itself as "detect-only -- pair with
/aget-enhance-config for remediation". That partner did not exist. A reader
following the instruction lands nowhere.

Why the existing controls missed it: the Skill Reliance Manifest checks
*declared-vs-on-disk for this seat's own skill list* and reported PASS 52/52 the
same morning. It cannot see a route one skill promises on another's behalf --
the predicate does not cover the subject. This check covers exactly that gap.

**It does not adjudicate.** A dangling route may be genuinely owed (a real
obligation with a tracker) or merely aspirational prose. This check reports the
referring skill and the quoting line so the classification is made on evidence
rather than on assumption -- which is what D-IG-12 asked for.

Usage:
    python3 scripts/check_skill_route_contract.py [--json]

Three-state per CONVENTION_check_three_state_contract:
    PASS         every referenced route resolves
    FAIL         >=1 referenced route does not resolve
    UNREACHABLE  the skills directory itself is absent (cannot look)

Exit codes: 0 = PASS or UNREACHABLE (a missing surface degrades, it does not
gate -- contract rule 2) · 1 = FAIL, >=1 unhedged route promised and absent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / ".claude" / "skills"

# A route mention: /aget-<something>, NOT preceded by a word character or slash.
# The negative lookbehind is load-bearing: without it an ORG/REPO path ending in
# `/aget-<name>` (common in issue-tracker references across many skills) reads as
# a route named /aget-<name>. The first draft of this check reported exactly that,
# which is the failure this whole check exists to catch -- a mention is not a claim.
ROUTE_RE = re.compile(r"(?<![\w/])/(aget-[a-z0-9]+(?:-[a-z0-9]+)*)")

# Bare (slash-less) skill names. Measured 2026-08-10: `aget-analyze-ontology`
# disclosed at :199 that `/aget-analyze-kb` does not exist -- and still named
# `aget-analyze-kb` at :157, INSIDE its `## Output Format` template, as an
# existing consuming skill. ROUTE_RE saw :199 (slash, hedged -> aspirational,
# cleared) and could not see :157 (no slash). The check reached the line that
# CONFESSES the defect and not the line that PERFORMS it, so adding hedge prose
# at :199 silenced the gate while the false claim shipped.
#
# Deliberately NOT applied to general prose. Every SKILL.md names sibling skills
# in tables, changelogs and Related sections; matching those would be the
# "too broad" failure warned about below, and a noisy check is one readers skip.
# The narrow surface where a bare name is a CLAIM rather than a mention is the
# output template: text the skill asserts it will emit. That is the only region
# scanned.
BARE_ROUTE_RE = re.compile(r"(?<![\w/`-])(aget-[a-z0-9]+(?:-[a-z0-9]+)*)")

# Headings whose fenced blocks are output templates (what the skill will print).
OUTPUT_HEADING_RE = re.compile(r"^#{1,6}\s.*output\s*format", re.I)

# Mentions that name the class of routes rather than one route.
NON_ROUTE_TOKENS = {
    "aget-enhance", "aget-check", "aget-close", "aget-create", "aget-propose",
}

# A line carrying any of these is talking ABOUT a route -- naming history, a
# grammar counter-example, a deferred candidate -- not directing a reader to
# use one. These are reported as `aspirational` and do NOT gate.
#
# Getting this wrong in either direction is costly. Too narrow and the check
# cries wolf on prose, and a noisy check is one readers learn to skip (the same
# dynamic D-IG-10 named about the ceiling alarm). Too broad and a real broken
# promise hides behind an incidental word. Hence: both polarities are tested.
HEDGE_MARKERS = (
    "future", "candidate", "planned", "scheduled", "reserved", "when available",
    "deferred", "renamed", "absorbed", "superseded", "deprecated", "sketch",
    "invalid", "out of scope", "not yet", "proposed", "would be", "may detect",
    "numbering collision", "not built", "never existed", "hypothetical",
    "does not exist", "no such route",
)


def installed_routes(base: Path) -> set[str]:
    if not base.is_dir():
        return set()
    return {p.name for p in base.iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file()}


def is_hedged(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in HEDGE_MARKERS)


def scan() -> dict:
    """Collect every referenced route with its referrers and quoting lines.

    Two surfaces, deliberately asymmetric:
      * anywhere      -- slash-prefixed `/aget-x` (ROUTE_RE)
      * output blocks -- bare `aget-x` (BARE_ROUTE_RE), where the skill is
                         asserting what it will print, so a name is a claim
    """
    refs: dict[str, list[dict]] = {}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        referrer = skill_md.parent.name
        in_fence = False
        under_output_heading = False
        for lineno, line in enumerate(skill_md.read_text().splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
            elif not in_fence and line.startswith("#"):
                under_output_heading = bool(OUTPUT_HEADING_RE.match(line))

            def add(route: str, surface: str) -> None:
                if route in NON_ROUTE_TOKENS:
                    return
                # Self-reference is never a broken promise. Scoped to the new
                # surface only: excluding it from the route surface too would
                # silently shift this check's established counts.
                if surface == "output-template" and route == referrer:
                    return
                refs.setdefault(route, []).append({
                    "referrer": referrer,
                    "line": lineno,
                    "context": line.strip()[:160],
                    "hedged": is_hedged(line),
                    "surface": surface,
                })

            for m in ROUTE_RE.finditer(line):
                add(m.group(1), "route")
            if in_fence and under_output_heading and not stripped.startswith("```"):
                for m in BARE_ROUTE_RE.finditer(line):
                    add(m.group(1), "output-template")
    return refs


def run(as_json: bool = False) -> int:
    if not SKILLS_DIR.is_dir():
        out = {"state": "UNREACHABLE",
               "reason": f"skills directory not found at {SKILLS_DIR}",
               "routes_referenced": 0, "dangling": []}
        print(json.dumps(out, indent=2) if as_json
              else f"UNREACHABLE — {out['reason']}")
        return 0  # UNREACHABLE does not gate (contract rule 2)

    installed = installed_routes(SKILLS_DIR)
    canonical = installed_routes(REPO.parent / "aget" / ".claude" / "skills")
    refs = scan()
    unresolved = {r: v for r, v in refs.items() if r not in installed}

    owed, aspirational, canonical_only = [], [], []
    for route, mentions in sorted(unresolved.items()):
        entry = {
            "route": route,
            "referrers": sorted({m["referrer"] for m in mentions}),
            "mentions": mentions,
        }
        if route in canonical:
            # Exists upstream but not on this seat. Not a broken promise --
            # a propagation gap, which is a different owner and a different fix.
            canonical_only.append(entry)
        elif all(m["hedged"] for m in mentions):
            aspirational.append(entry)
        else:
            entry["unhedged_mentions"] = [m for m in mentions if not m["hedged"]]
            owed.append(entry)

    state = "FAIL" if owed else "PASS"
    report = {
        "state": state,
        "skills_scanned": len(installed),
        "routes_referenced": len(refs),
        "routes_resolved": len(refs) - len(unresolved),
        "owed": owed,                    # gates
        "aspirational": aspirational,    # reported, does not gate
        "canonical_only": canonical_only,  # propagation gap, does not gate
    }

    if as_json:
        print(json.dumps(report, indent=2))
        return 1 if state == "FAIL" else 0

    print("=== skill route-contract check (D-IG-12) ===\n")
    print(f"Skills scanned:     {report['skills_scanned']}")
    print(f"Routes referenced:  {report['routes_referenced']}")
    print(f"Routes resolved:    {report['routes_resolved']}")
    print(f"  owed (gating):    {len(owed)}")
    print(f"  aspirational:     {len(aspirational)}  (hedged prose — does not gate)")
    print(f"  canonical-only:   {len(canonical_only)}  (propagation gap — does not gate)")

    if owed:
        print(f"\nFAIL — {len(owed)} route(s) promised without hedge and absent:\n")
        for d in owed:
            print(f"  /{d['route']}")
            print(f"    referenced by: {', '.join(d['referrers'])}")
            for m in d["unhedged_mentions"][:2]:
                print(f"      {m['referrer']}/SKILL.md:{m['line']}: {m['context']}")
            print()
    else:
        print("\nPASS — every unhedged route reference resolves.")

    if aspirational:
        print("Aspirational (every mention hedged — future/renamed/reserved):")
        for d in aspirational:
            print(f"  /{d['route']}  ({', '.join(d['referrers'])})")
        print()
    if canonical_only:
        print("Canonical-only (exists upstream, absent on this seat):")
        for d in canonical_only:
            print(f"  /{d['route']}  ({', '.join(d['referrers'])})")
        print()
    return 1 if owed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    return run(as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
