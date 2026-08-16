#!/usr/bin/env python3
"""check_deprecation_removals.py — the actuator R-DEP-011/R-DEP-021 never had.

WHY THIS EXISTS (2026-08-13). `POLICY_deprecation.md` carries a Deprecation Registry
whose rows each declare a **removal version**. Nothing compared that field against the
current version. Measured at the moment of writing: `DEP-PRETAG-SH-001` — POL-DEP-001's
own **first full rehearsal**, chosen as the exemplar — scheduled removal at **v3.28.0**,
the seat is at **v3.30.0**, the row still reads *"Active — grace window open"*, the script
is still on disk, and `SOP_release_process.md` Phase 3.0 still calls it **"Preferred."**

The rehearsal proved *deprecate* and *carry*. It never proved *remove*, because removal is
the only step in the sequence with no instrument behind it. A populated removal-version
field with nothing reading it is L671 decorative metadata inside the policy that exists to
prevent decorative metadata.

HOW IT WAS FOUND, which is the argument for building it rather than fixing one row: not by
a deprecation check. It surfaced as a side effect of widening `check_actuator_census.py`'s
corpus to `.sh`. One instance found by accident is a reason to build the general detector.

SCOPE NOTE (verified against the 2026-08-13 standing ruling, not assumed): the ruling
*"the concept register is a working instrument — focus on making it work rather than
pruning it; do NOT prioritise retirement/deprecation work"* is scoped to the **ontology
concept register**, a different register from this one. Its stated lever is *"building
consumers"* — which is exactly what this script is for POLICY_deprecation.md's registry.

THREE-STATE per CONVENTION_check_three_state_contract: PASS / FAIL / UNAVAILABLE. A row
whose removal version cannot be parsed is reported UNAVAILABLE, never silently skipped —
an unparseable row must not read as a clean one (the zero-denominator family, gh#2045).

Exit codes:
    0 — PASS (no row is past its removal version while un-removed), or advisory mode
    1 — FAIL (>=1 row overdue)
    2 — UNAVAILABLE (registry or version.json unreadable)


Usage:
    python3 scripts/check_deprecation_removals.py [--json] [--advisory]

Exit codes:
    0  every registered deprecation is inside its grace window, or --advisory
    1  at least one removal is overdue
    2  registry unreadable or absent (UNAVAILABLE, never a silent pass)
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance" / "POLICY_deprecation.md"
VERSION_JSON = ROOT / ".aget" / "version.json"

# A registry row, split on "|", yields fixed positions:
#   [1] **DEP-ID**: subject   [2] deprecated-in   [3] replacement   [4] removal   [5] status
ROW = re.compile(r"^\|\s*\*\*(DEP-[A-Z0-9-]+)\*\*")
SEMVER = re.compile(r"v?(\d+)\.(\d+)\.(\d+)")
I_DEPRECATED, I_REMOVAL, I_STATUS = 2, 4, 5

# Terminal-state vocabulary. BOTH VERBS ARE LOAD-BEARING (measured 2026-08-13): the first
# version of this file matched only `removed`, and `DEP-REQ-HOM-F-006` — whose status reads
# **"Retired in v3.18.0"** — was reported FAIL. A discharged row read as an overdue one
# because the predicate could not detect its own subject's vocabulary.
TERMINAL = re.compile(r"\b(removed|retired|withdrawn)\b", re.I)


def parse_semver(text):
    """First semver in the text, as a comparable tuple. None when absent."""
    m = SEMVER.search(text or "")
    return tuple(int(g) for g in m.groups()) if m else None


def current_version():
    try:
        return parse_semver(json.loads(VERSION_JSON.read_text())["aget_version"])
    except Exception:
        return None


def rows():
    """Registry rows, de-duplicated by id — the id appears in both the registry table
    and the narrative section below it, and counting both would double the denominator."""
    if not REGISTRY.exists():
        return None
    seen, out = set(), []
    for line in REGISTRY.read_text(errors="ignore").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        dep_id = m.group(1)
        if dep_id in seen:
            continue
        seen.add(dep_id)
        # Split the WHOLE line, not the post-id remainder. The first version split the
        # remainder, which shifted every index by one and made cells[-1] the empty cell
        # after the trailing pipe -- so `status` was always '' and the terminal test could
        # never fire. It printed status='' next to a FAIL verdict and did not treat that
        # as the contradiction it was.
        cells = [c.strip() for c in line.split("|")]
        out.append({"id": dep_id, "cells": cells, "raw": line})
    return out


def classify(row, cur):
    """(state, detail), read from FIXED cell positions, not from scanning.

    An earlier version took "the last cell carrying a semver" as the removal version and
    "the final cell" as status. Both heuristics were wrong on real rows and each produced a
    false positive, so the positions are pinned and a short row is UNAVAILABLE rather than
    silently reinterpreted."""
    cells = row["cells"]
    if len(cells) <= I_STATUS:
        return "UNAVAILABLE", f"row has {len(cells)} cells, need > {I_STATUS}"
    status = cells[I_STATUS]
    # Test the STATUS cell ONLY. Searching the whole row would match the word "removed"
    # inside the removal cell's own grace-period prose ("marked v3.26 -> carried v3.27 ->
    # removed v3.28") and silently discharge the one genuinely overdue row.
    if TERMINAL.search(status):
        return "PASS", f"terminal ({status[:44]})"
    removal = parse_semver(cells[I_REMOVAL])
    if removal is None:
        return "UNAVAILABLE", f"removal cell carries no semver: {cells[I_REMOVAL][:60]!r}"
    if cur is None:
        return "UNAVAILABLE", "current version unreadable"
    if cur >= removal:
        return "FAIL", (
            f"removal scheduled v{'.'.join(map(str, removal))}, "
            f"current v{'.'.join(map(str, cur))}, status={status[:48]!r}"
        )
    return "PASS", f"grace open until v{'.'.join(map(str, removal))}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--advisory", action="store_true",
                    help="report but always exit 0 (battery advisory slot)")
    args = ap.parse_args()

    reg = rows()
    if reg is None:
        print(f"UNAVAILABLE: registry not found at {REGISTRY.relative_to(ROOT)}", file=sys.stderr)
        return 2

    cur = current_version()
    results = [dict(id=r["id"], **dict(zip(("state", "detail"), classify(r, cur)))) for r in reg]
    fails = [r for r in results if r["state"] == "FAIL"]
    unavail = [r for r in results if r["state"] == "UNAVAILABLE"]

    if args.json:
        print(json.dumps({
            "current_version": ".".join(map(str, cur)) if cur else None,
            "denominator": len(results),   # always reported — never a bare count (gh#2045)
            "pass": len(results) - len(fails) - len(unavail),
            "fail": len(fails), "unavailable": len(unavail), "rows": results,
        }, indent=2))
    else:
        print("=" * 62)
        print("DEPRECATION REMOVAL CHECK — registry removal-version vs current")
        print("=" * 62)
        print(f"\n  current version : {'.'.join(map(str, cur)) if cur else 'UNREADABLE'}")
        print(f"  registry rows   : {len(results)}")
        print(f"  PASS {len(results)-len(fails)-len(unavail)}  FAIL {len(fails)}  UNAVAILABLE {len(unavail)}\n")
        for r in results:
            mark = {"PASS": "✅", "FAIL": "❌", "UNAVAILABLE": "⚠️ "}[r["state"]]
            print(f"  {mark} {r['id']:<28} {r['detail']}")
        if fails:
            print("\n  A removal version that has passed with the row still open is not a\n"
                  "  schedule slip — it is an unactuated rule. Remove the artifact and mark\n"
                  "  the row Removed, or re-baseline the version with a stated reason.")
    if args.advisory:
        return 0
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
