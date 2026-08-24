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

THE EXIT CODE CARRIES THAT STATE — it did not until 2026-08-21 (v3.32 Gate 1). `classify()`
had returned UNAVAILABLE correctly and `main()` had counted it correctly, and then ended
`return 1 if fails else 0`, which reads only the FAIL bucket. So a registry that was READ
but not MEASURED exited 0: an active row whose removal cell carries no semver, an
unreadable `.aget/version.json` making every active row unclassifiable, or a readable file
that parsed zero rows. The missing-registry UNAVAILABLE was never masked; the row-level one
always was. Same defect shape as the rows it detects — a state reported in the body and
dropped from the verdict.

PRECEDENCE: UNAVAILABLE dominates FAIL. A population only partly measured cannot certify a
whole-registry verdict, so the exit code names the weaker claim; the FAIL rows are still
printed, still counted, and the code is still non-zero, so nothing that blocked before
stops blocking. `--advisory` downgrades FAIL to a report and NEVER downgrades UNAVAILABLE —
"I did not read the subject" is not a finding that an advisory slot may absorb.

INJECTABLE SUBJECT (v3.32 AC-2, DR-3 — 2026-08-21). Until this repair, ROOT/REGISTRY were
module constants derived from `__file__` and `--help` offered only `--json`/`--advisory`.
The instrument could not be pointed at any registry but the one beside it, and its output
never named the registry it read, so a reader could not tell which subject a verdict was
about. Measured on shipped blob 50e29046b8b779b8d17a195d339549e0ddf3014a (identical at
v3.31.0, v3.31.1 and the private working copy).

Precedence — first hit wins, and the winner is ALWAYS disclosed:
    1. --registry PATH                explicit, this exact file
    2. --root DIR                     explicit, DIR/<default registry relpath>
    3. AGET_DEPRECATION_REGISTRY      explicit, environment
    4. this file's own repo root      discovery — the prior sole behaviour

Both flags may be given together: --registry names the registry, --root names the tree
whose `.aget/version.json` it is compared against. Neither silently overrides the other.

An EXPLICIT input that does not resolve is UNAVAILABLE (exit 2). It is NEVER replaced by a
fallback — that substitution is the sibling defect (AC-3/DR-1), where an instrument silently
measured a different subject and exited 0.

COHERENT SUBJECT. The registry and the version it is compared against must come from ONE
tree. When only --registry is given, the root is derived FROM that registry (its
`governance/` parent, else its own directory) — never from discovery. An earlier draft of
this repair left VERSION_JSON resolving from the discovered root, so the registry came from
one seat and the comparison version from another, silently, producing a clean PASS.

EXIT 2 IS A SHARED NAMESPACE (L1432). `argparse` also exits 2 on a usage error, so exit
status alone cannot distinguish UNAVAILABLE from "unrecognized arguments". Every genuine
UNAVAILABLE therefore prints a second discriminator on stderr: a line beginning
`UNAVAILABLE:` that names the subject and the strategy that chose it.

Exit codes:
    0 — PASS (every row was classified and none is past its removal version while
        un-removed), or advisory mode over a FAIL
    1 — FAIL (>=1 row overdue, and every row was classifiable)
    2 — UNAVAILABLE, in any of four shapes, never masked by --advisory:
          a. the declared registry could not be read;
          b. the registry was read but parsed ZERO rows;
          c. >=1 row could not be classified (short row, or no semver in its removal cell);
          d. the current version could not be read, leaving active rows unclassifiable.

Usage:
    python3 scripts/check_deprecation_removals.py [--json] [--advisory]
                                                  [--registry PATH] [--root DIR]
"""
import argparse
import json
import os
import pathlib
import re
import sys

# Default discovery, in order. First existing candidate wins and the winner is disclosed.
# Two names because one script serves two populations: this seat's governance registry
# (`POLICY_deprecation.md`) and the consumer-facing public registry (`DEPRECATIONS.md`).
# Discovery order is documented, disclosed in output, and applies ONLY when no explicit
# input was given — it is a default, never a substitution for a rejected explicit subject.
DEFAULT_REGISTRY_RELPATHS = (
    "governance/POLICY_deprecation.md",
    "governance/DEPRECATIONS.md",
)


def _discover(root):
    """(registry_path, strategy) for a root with no explicit registry named."""
    for rel in DEFAULT_REGISTRY_RELPATHS:
        if (root / rel).is_file():
            return root / rel, rel
    # Nothing found: return the FIRST candidate so the UNAVAILABLE message names a real
    # path rather than nothing, and disclose that discovery came up empty.
    return root / DEFAULT_REGISTRY_RELPATHS[0], "none-of[" + ",".join(DEFAULT_REGISTRY_RELPATHS) + "]"


def _root_for_registry(reg):
    """The tree a registry belongs to, derived from the registry itself.

    `<root>/governance/<name>.md` -> `<root>`; anything else -> the registry's own
    directory. Never the discovered own-repo root: borrowing this file's repo version to
    judge somebody else's registry is the split-subject defect, not a convenience.
    """
    return reg.parent.parent if reg.parent.name == "governance" else reg.parent


def resolve_subject(registry=None, root=None, env=None, home=None):
    """Resolve the subject this run measures.

    Returns (registry_path, root_path, strategy, explicit) — `explicit` is True when an
    operator named the subject, which is what makes a resolution failure UNAVAILABLE
    rather than a fallback.
    """
    home = pathlib.Path(home) if home else pathlib.Path(__file__).resolve().parents[1]

    if registry or root:
        parts = []
        if registry:
            reg = pathlib.Path(registry)
            parts.append(f"--registry={registry}")
        if root:
            rt = pathlib.Path(root)
            parts.append(f"--root={root}")
            if not registry:
                reg, disc = _discover(rt)
                parts.append(f"discovered={disc}")
        else:
            rt = _root_for_registry(reg)
        return reg, rt, "explicit:" + " ".join(parts), True

    if env:
        reg = pathlib.Path(env)
        return reg, _root_for_registry(reg), f"explicit:AGET_DEPRECATION_REGISTRY={env}", True

    reg, disc = _discover(home)
    return reg, home, f"discovered:own-repo-root+{disc}", False


# Module-level defaults are DISCOVERY ONLY — no argv is parsed at import time. Importers
# (the unit half of tests/test_deprecation_removal_check.py) get the historical behaviour;
# main() rebinds these from the parsed arguments.
ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY, _, SUBJECT_STRATEGY, _ = resolve_subject()
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


def current_version(version_json=None):
    vj = VERSION_JSON if version_json is None else pathlib.Path(version_json)
    try:
        return parse_semver(json.loads(vj.read_text())["aget_version"])
    except Exception:
        return None


def rows(registry=None):
    """Registry rows, de-duplicated by id — the id appears in both the registry table
    and the narrative section below it, and counting both would double the denominator.

    None means UNAVAILABLE: absent, a directory, or unreadable. An OSError here used to
    escape as a traceback and exit 1, collapsing UNAVAILABLE into FAIL.
    """
    reg = REGISTRY if registry is None else pathlib.Path(registry)
    if not reg.is_file():
        return None
    try:
        text = reg.read_text(errors="ignore")
    except OSError:
        return None
    seen, out = set(), []
    for line in text.splitlines():
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
                    help="downgrade FAIL to exit 0 (battery advisory slot); UNAVAILABLE is "
                         "never downgraded")
    ap.add_argument("--registry", metavar="PATH",
                    help="explicit path to the deprecation registry (explicit: never falls back)")
    ap.add_argument("--root", metavar="DIR",
                    help="explicit tree root; registry discovered under DIR, version read "
                         "from DIR/.aget/version.json")
    args = ap.parse_args()

    registry, root, strategy, explicit = resolve_subject(
        args.registry, args.root, os.environ.get("AGET_DEPRECATION_REGISTRY"))
    version_json = root / ".aget" / "version.json"

    reg = rows(registry)
    if reg is None:
        # Exit 2 is shared with argparse's usage error (L1432), so the `UNAVAILABLE:`
        # token on stderr is the discriminator a caller can actually test.
        print(f"UNAVAILABLE: registry not readable at {registry}", file=sys.stderr)
        print(f"UNAVAILABLE: subject chosen by {strategy}", file=sys.stderr)
        if explicit:
            print("UNAVAILABLE: the explicit input was rejected and NOT replaced by a "
                  "fallback; no other subject was measured.", file=sys.stderr)
        return 2

    cur = current_version(version_json)
    results = [dict(id=r["id"], **dict(zip(("state", "detail"), classify(r, cur)))) for r in reg]
    fails = [r for r in results if r["state"] == "FAIL"]
    unavail = [r for r in results if r["state"] == "UNAVAILABLE"]

    if args.json:
        print(json.dumps({
            # Source disclosure is not decoration: a verdict whose subject is unnamed
            # cannot be checked by its reader (v3.32 path-resolution contract, rule 2).
            "registry": str(registry),
            "registry_source": strategy,
            "version_source": str(version_json),
            "current_version": ".".join(map(str, cur)) if cur else None,
            "denominator": len(results),   # always reported — never a bare count (gh#2045)
            "pass": len(results) - len(fails) - len(unavail),
            "fail": len(fails), "unavailable": len(unavail), "rows": results,
        }, indent=2))
    else:
        print("=" * 62)
        print("DEPRECATION REMOVAL CHECK — registry removal-version vs current")
        print("=" * 62)
        print(f"\n  registry        : {registry}")
        print(f"  registry source : {strategy}")
        print(f"  version source  : {version_json}")
        print(f"  current version : {'.'.join(map(str, cur)) if cur else 'UNREADABLE'}")
        print(f"  registry rows   : {len(results)}")
        print(f"  PASS {len(results)-len(fails)-len(unavail)}  FAIL {len(fails)}  UNAVAILABLE {len(unavail)}\n")
        for r in results:
            mark = {"PASS": "✅", "FAIL": "❌", "UNAVAILABLE": "⚠️ "}[r["state"]]
            print(f"  {mark} {r['id']:<28} {r['detail']}")
        if fails:
            print("\n  A removal version that has passed with the row still open is not a\n"
                  "  schedule slip — it is an unactuated rule. Remove the artifact and mark\n"
                  "  the row Removed, or re-baseline the version with a stated reason.")
        if unavail or not results:
            print("\n  This run did not measure its whole population, so it certifies\n"
                  "  nothing about the rows it could not classify. Exit 2, not 0.")

    # UNAVAILABLE first, and BEFORE --advisory. The registry was reachable, so the earlier
    # exit is not the one that fires here; what is unavailable is the measurement of one or
    # more rows. Reported on stderr with the `UNAVAILABLE:` discriminator because exit 2 is
    # shared with argparse's usage error (L1432) and the code alone cannot be tested on.
    if not results:
        print(f"UNAVAILABLE: registry readable but 0 rows parsed at {registry}",
              file=sys.stderr)
        print("UNAVAILABLE: an empty denominator is not a clean population (gh#2045); "
              "the row predicate may have drifted from the table format.", file=sys.stderr)
        print(f"UNAVAILABLE: subject chosen by {strategy}", file=sys.stderr)
        return 2
    if unavail:
        print(f"UNAVAILABLE: {len(unavail)} of {len(results)} registry rows could not be "
              f"classified at {registry}", file=sys.stderr)
        for r in unavail:
            print(f"UNAVAILABLE: {r['id']} — {r['detail']}", file=sys.stderr)
        if fails:
            print(f"UNAVAILABLE: {len(fails)} row(s) also FAIL and are reported above; "
                  "UNAVAILABLE takes the exit code because the population is "
                  "only partly measured.", file=sys.stderr)
        print(f"UNAVAILABLE: subject chosen by {strategy}", file=sys.stderr)
        return 2

    if args.advisory:
        return 0
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
