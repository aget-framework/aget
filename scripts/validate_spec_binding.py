#!/usr/bin/env python3
"""
validate_spec_binding.py — Spec→Ontology binding validator (detect/enforce half).

Stream 3 of INIT-ONTOLOGY-SPEC-BINDING (C-22-14, v3.22). The DETECT/ENFORCE
counterpart to scripts/ground_artifact.py (the GENERATE half that *suggests*
bindings). Where check_skill_grounding.py validates the skill surface, this
validates the spec surface:

  - **Phantom URI refs** (R-SPEC-BIND-002): every inline `aget:concept/X` in a
    spec MUST resolve to a concept in the current ontology. An unresolved ref is
    a PhantomConceptReference (C672) — a confabulation seed.
  - **Binding coverage** (R-SPEC-BIND-001, Advisory metric): how many specs
    carry ≥1 inline binding (the Success-Metric tracked by the initiative).

ADR-008 progression: Advisory (read-only report, exit 0) → Strict (`--strict`
exits 1 on any phantom ref, foldable into the release-gate battery).

Reuses scripts/ground_artifact.py: load_ontology(), ONTOLOGY_CANDIDATES,
URI_REF_RE (DRY — single ontology parser).

Usage:
  python3 scripts/validate_spec_binding.py
  python3 scripts/validate_spec_binding.py --json
  python3 scripts/validate_spec_binding.py --strict        # CI gate: exit 1 on phantom refs
  python3 scripts/validate_spec_binding.py --spec AGET_RELEASE_SPEC.md
  python3 scripts/validate_spec_binding.py --self-test

Exit codes:
  0  No phantom refs (or Advisory/read-only/self-test pass)
  1  --strict AND ≥1 phantom ref (release-blocking)
  2  Usage / environment error
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ground_artifact as _ga  # noqa: E402  (load_ontology, ONTOLOGY_CANDIDATES, URI_REF_RE)

# Canonical specs live at ../aget/specs; the local aget/specs holds drafts.
SPEC_ROOTS = [REPO_ROOT.parent / "aget" / "specs", REPO_ROOT / "aget" / "specs"]


def valid_uris():
    """Set of concept URIs (and their bare names) in the current ontology."""
    for cand in _ga.ONTOLOGY_CANDIDATES:
        if cand.exists():
            concepts = _ga.load_ontology(cand)
            names = {c["uri"].split("/")[-1] for c in concepts if c.get("uri")}
            return names, str(cand)
    return set(), None


def scan_spec(path: Path, names: set) -> dict:
    """Return binding findings for one spec file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    refs = _ga.URI_REF_RE.findall(text)  # bare concept names (capture group)
    phantom = sorted({r for r in refs if r not in names})
    return {
        "spec": path.name,
        "ref_count": len(refs),
        "bound": len(refs) > 0,
        "phantom_refs": phantom,
    }


def collect(names: set, only: str | None):
    results = []
    for root in SPEC_ROOTS:
        if not root.exists():
            continue
        for f in sorted(root.glob("*.md")):
            if only and f.name != only:
                continue
            results.append(scan_spec(f, names))
    return results


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="Exit 1 on any phantom ref (CI gate)")
    p.add_argument("--spec", default=None, help="Validate a single spec by filename")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        return _self_test()

    names, onto_path = valid_uris()
    if not names:
        print("ERROR: ontology not found / empty (looked in ground_artifact.ONTOLOGY_CANDIDATES)", file=sys.stderr)
        return 2

    results = collect(names, args.spec)
    if not results:
        print(f"ERROR: no specs found under {[str(r) for r in SPEC_ROOTS]}", file=sys.stderr)
        return 2

    total = len(results)
    bound = sum(1 for r in results if r["bound"])
    phantom_specs = [r for r in results if r["phantom_refs"]]
    phantom_total = sum(len(r["phantom_refs"]) for r in phantom_specs)

    if args.json:
        print(json.dumps({
            "ontology": onto_path, "specs": total, "bound": bound,
            "coverage_pct": round(100 * bound / total, 1),
            "phantom_refs": phantom_total,
            "phantom_specs": [{"spec": r["spec"], "refs": r["phantom_refs"]} for r in phantom_specs],
        }, indent=2))
    else:
        print(f"=== spec→ontology binding validator (C-22-14) — {total} specs, ontology {Path(onto_path).name} ===")
        print(f"Binding coverage (R-SPEC-BIND-001): {bound}/{total} specs carry ≥1 inline aget:concept/X ({round(100*bound/total,1)}%)")
        print(f"Phantom refs (R-SPEC-BIND-002):     {phantom_total}" + ("" if not phantom_total else "  — UNRESOLVED:"))
        for r in phantom_specs:
            print(f"  {r['spec']}: {', '.join(r['phantom_refs'])}")

    if args.strict and phantom_total:
        return 1
    return 0


def _self_test() -> int:
    """Deterministic: a known-good ref resolves; a fabricated ref is phantom."""
    names = {"NormativeConceptBinding", "InlineUriReference"}
    failures = []
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "GOOD.md"
        good.write_text("Bound to aget:concept/NormativeConceptBinding here.\n")
        bad = Path(td) / "BAD.md"
        bad.write_text("Refers to aget:concept/TotallyMadeUpConcept999.\n")
        rg = scan_spec(good, names)
        rb = scan_spec(bad, names)
        if rg["phantom_refs"]:
            failures.append(f"resolved ref flagged phantom: {rg}")
        if not rg["bound"]:
            failures.append("bound spec not counted as bound")
        if "TotallyMadeUpConcept999" not in rb["phantom_refs"]:
            failures.append(f"phantom ref not detected: {rb}")
    if failures:
        print("SELF-TEST FAIL:\n  " + "\n  ".join(failures))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
