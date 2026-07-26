#!/usr/bin/env python3
"""Reference resolution — does every path a governed artifact NAMES actually exist?

THE EDGE THIS CHECKS
--------------------
`resolves-to`. The second edge type, after `invoked-by` (check_actuator_census.py).

WHY (L1260)
-----------
A governed artifact can name a destination that has never existed, and stay wrong
indefinitely, because nothing compares the two halves. Both halves look correct
alone: the policy is well-formed prose, and the absent file is absent silently.

Two instances found 2026-07-26, both months old, both in `governance/`:

  1. `POLICY_issue_disposition.md:129` named `BACKLOG.md` §B as the MANDATORY
     salvage destination for `v328-shipday:R64`. The file did not exist, so the
     rule was unexecutable as specified — discovered at first execution, not by
     review.

  2. `POLICY_deprecation.md` states "Both names supported indefinitely" for four
     session-script aliases. ALL FOUR ARE ABSENT. Worse, the reclassification from
     deprecation to permanent-alias rested on that false half: its rationale was
     "both names work; no agent failure attributable to filename choice". There
     was no failure because there was no USER — absence of failure was evidence of
     disuse, not of support.

The second is the sharper case: a governance policy asserting a fact about the
filesystem, false since it was written, load-bearing for a decision.

WHAT IS AND IS NOT A FINDING
----------------------------
Backticked path-shaped strings in `governance/` and `sops/`. Deliberately narrow:

  - template/placeholder forms (`X.Y.Z`, `YYYY`, `NNN`, `{...}`, `<...>`, `*`) are
    NOT findings — they are patterns, not references.
  - a basename that exists ANYWHERE in either tree resolves. A doc naming
    `version.json` means the concept, not one path.
  - both trees are searched: the instance repo AND canonical `../aget/`. Checking
    only the instance manufactures false positives for canonical artifacts — the
    first version of this script did exactly that (`Path('.').parent` is `Path('.')`,
    so the canonical check silently never ran) and reported 135 where the true
    figure is 29. An instrument for finding false absence, producing false absence.

Exit 0 = all resolve | 1 = unresolved found | 2 = usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT.parent / "aget"

SCAN_DIRS = ("governance", "sops")
PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|sh|json|yaml|yml|jsonl|cff))`")
PLACEHOLDER_RE = re.compile(r"X\.Y\.Z|YYYY|NNN|vPRIOR|\{|<|\*")


def _basenames() -> set[str]:
    names = set()
    for base in (ROOT, CANON):
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                names.add(p.name)
    return names


def scan() -> dict[str, list[str]]:
    known = _basenames()
    findings: dict[str, list[str]] = {}
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in sorted(base.glob("*.md")):
            bad = []
            for ref in sorted(set(PATH_RE.findall(f.read_text(errors="ignore")))):
                if PLACEHOLDER_RE.search(ref):
                    continue
                if any((b / ref).exists() for b in (ROOT, CANON)):
                    continue
                if Path(ref).name in known:
                    continue
                bad.append(ref)
            if bad:
                findings[f"{d}/{f.name}"] = bad
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    findings = scan()
    total = sum(len(v) for v in findings.values())

    if args.json:
        print(json.dumps({"edge": "resolves-to", "unresolved": total,
                          "files": findings}, indent=2))
        return 1 if total else 0

    print("=" * 62)
    print("REFERENCE RESOLUTION — edge: `resolves-to`")
    print("=" * 62)
    print(f"\n  scanned      : {', '.join(SCAN_DIRS)}")
    print(f"  unresolved   : {total} across {len(findings)} file(s)\n")

    for f, refs in sorted(findings.items(), key=lambda kv: -len(kv[1])):
        print(f"  {f}  ({len(refs)})")
        for r in refs:
            print(f"      ✗ {r}")

    if total:
        print("\n  A governed artifact naming a path that does not exist is a rule")
        print("  nobody can follow, or a claim about the world that is false. Fix")
        print("  the reference, or create what it names — but do not create an")
        print("  artifact merely so a document becomes true.")
        return 1

    print("  ✅ every named path resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
