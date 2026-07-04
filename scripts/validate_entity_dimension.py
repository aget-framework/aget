#!/usr/bin/env python3
"""
validate_entity_dimension.py — AGET_ENTITY_DIMENSION_SPEC conformance validator.

Stream 3 of INIT-ONTOLOGY-SPEC-BINDING, validator-half of C-25-01 (v3.25).
Implements the V-ENTDIM-001..016 binding-layer conformance contract from
specs/AGET_ENTITY_DIMENSION_SPEC.md against a target spec file:

  - 12 executable checks (V-002..V-010, V-012..V-016 minus qualitative rows)
  - 2 warn-only SHOULD checks: V-004 (Interrelationship), V-009 (Provenance)
  - 2 qualitative checks reported as MANUAL (V-001 noun-phrase coverage,
    V-011 two-tier bar consistency) — never PASS/FAIL mechanically

Scope honesty (spec §Verification): presence checks verify BINDING, not
coverage DEPTH. Depth stays a qualitative-reviewer concern.

ADR-008 progression: Advisory (report, exit 0) → Strict (`--strict` exits 1
on any SHALL-check failure; SHOULD failures stay warnings in both modes).

Reuses scripts/ground_artifact.py: load_ontology(), ONTOLOGY_CANDIDATES (DRY —
single ontology parser).

Usage:
  python3 scripts/validate_entity_dimension.py --spec specs/AGET_ENTITY_DIMENSION_SPEC.md
  python3 scripts/validate_entity_dimension.py --spec <file> --strict
  python3 scripts/validate_entity_dimension.py --spec <file> --json
  python3 scripts/validate_entity_dimension.py --self-test

Exit codes:
  0  All SHALL checks pass (or Advisory mode / self-test pass)
  1  --strict AND >= 1 SHALL-check failure
  2  Usage / environment error
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from ground_artifact import ONTOLOGY_CANDIDATES, load_ontology  # noqa: E402

URI_RE = re.compile(r"aget:concept/([A-Za-z][A-Za-z0-9_]+)")

# (id, kind, description, check). kind: SHALL | SHOULD | MANUAL
# check: substring/regex the spec text must contain (None for MANUAL/composite).
CHECKS = [
    ("V-ENTDIM-001", "MANUAL", "Every normative domain noun phrase carries a binding (reviewer)", None),
    ("V-ENTDIM-002", "SHALL", "Full-form binding sentence present",
     re.compile(r"SHALL be interpreted in terms of aget:concept/[A-Za-z]")),
    ("V-ENTDIM-003", "SHALL", "EntityDefinitionDimension bound", "aget:concept/EntityDefinitionDimension"),
    ("V-ENTDIM-004", "SHOULD", "EntityInterrelationshipDimension bound (warn-only)", "aget:concept/EntityInterrelationshipDimension"),
    ("V-ENTDIM-005", "SHALL", "EntityActionDimension bound", "aget:concept/EntityActionDimension"),
    ("V-ENTDIM-006", "SHALL", "EntityLifecycleDimension bound", "aget:concept/EntityLifecycleDimension"),
    ("V-ENTDIM-007", "SHALL", "EntityPersistenceDimension bound", "aget:concept/EntityPersistenceDimension"),
    ("V-ENTDIM-008", "SHALL", "EntityGovernanceDimension bound", "aget:concept/EntityGovernanceDimension"),
    ("V-ENTDIM-009", "SHOULD", "EntityProvenanceDimension bound (warn-only)", "aget:concept/EntityProvenanceDimension"),
    ("V-ENTDIM-010", "SHALL", "DimensionalFormalizationMaturity declared", "aget:concept/DimensionalFormalizationMaturity"),
    ("V-ENTDIM-011", "MANUAL", "Two-tier bar stated and consistent (reviewer)", None),
    ("V-ENTDIM-012", "SHALL", "MetaSpecificationGap anti-pattern named", "aget:concept/MetaSpecificationGap"),
    ("V-ENTDIM-013", "SHALL", "VocabularyFirstNamingDiscipline cited", "aget:concept/VocabularyFirstNamingDiscipline"),
    ("V-ENTDIM-014", "SHALL", "All aget:concept/ URIs resolve in ontology", "URI_RESOLUTION"),
    ("V-ENTDIM-015", "SHALL", "Mention!=binding counter-form present", "aget:concept/SpecificationToOntologyBinding"),
    ("V-ENTDIM-016", "SHALL", "Binds-Against declares ontology name AND version",
     re.compile(r"Binds-Against.*ONTOLOGY_personal_ai_systems.*version.*1\.0")),
]


ONTOLOGY_OVERRIDE = None  # set from --ontology


def find_ontology():
    if ONTOLOGY_OVERRIDE and ONTOLOGY_OVERRIDE.exists():
        return ONTOLOGY_OVERRIDE
    for cand in ONTOLOGY_CANDIDATES:
        if cand.exists():
            return cand
    return None


def run_checks(spec_path: Path):
    text = spec_path.read_text(encoding="utf-8")
    results = []
    for vid, kind, desc, probe in CHECKS:
        if kind == "MANUAL":
            results.append({"id": vid, "kind": kind, "desc": desc, "status": "MANUAL"})
            continue
        if probe == "URI_RESOLUTION":
            onto_path = find_ontology()
            if onto_path is None:
                results.append({"id": vid, "kind": kind, "desc": desc,
                                "status": "ERROR", "detail": "ontology file not found"})
                continue
            known = {c.get("uri", "").split("/")[-1] for c in load_ontology(onto_path)}
            # prefLabel-derived URIs: also accept CamelCase of prefLabel (generator convention)
            for c in load_ontology(onto_path):
                label = c.get("prefLabel", "")
                known.add(re.sub(r"[^A-Za-z0-9]", "", label))
            refs = sorted(set(URI_RE.findall(text)))
            unresolved = [r for r in refs if r not in known]
            status = "PASS" if not unresolved else "FAIL"
            results.append({"id": vid, "kind": kind, "desc": desc, "status": status,
                            "detail": f"{len(refs)} refs, unresolved: {unresolved or 'none'}"})
            continue
        hit = bool(probe.search(text)) if hasattr(probe, "search") else (probe in text)
        if hit:
            status = "PASS"
        else:
            status = "WARN" if kind == "SHOULD" else "FAIL"
        results.append({"id": vid, "kind": kind, "desc": desc, "status": status})
    return results


def self_test() -> int:
    """Green fixture = the spec itself (self-demonstrating); red fixture = synthetic."""
    spec = SCRIPT_DIR.parent / "specs" / "AGET_ENTITY_DIMENSION_SPEC.md"
    if not spec.exists():
        print("self-test: SKIP (spec not found)")
        return 2
    green = run_checks(spec)
    green_fail = [r for r in green if r["status"] == "FAIL"]
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("# Fixture spec with no bindings\naget:concept/PhantomNeverInOntologyXyz\n")
        red_path = Path(f.name)
    red = run_checks(red_path)
    red_path.unlink()
    red_fail = [r for r in red if r["status"] == "FAIL"]
    ok = not green_fail and len(red_fail) >= 8
    print(f"self-test: {'PASS' if ok else 'FAIL'} "
          f"(green FAILs={len(green_fail)} expect 0; red FAILs={len(red_fail)} expect >=8)")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--spec", help="spec file to validate")
    p.add_argument("--strict", action="store_true", help="exit 1 on any SHALL failure")
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--ontology", help="explicit path to the ontology yaml "
                   "(instances carry it at ontology/; canonical does not)")
    args = p.parse_args()

    global ONTOLOGY_OVERRIDE
    if args.ontology:
        ONTOLOGY_OVERRIDE = Path(args.ontology)

    if args.self_test:
        return self_test()
    if not args.spec:
        p.print_help()
        return 2
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}", file=sys.stderr)
        return 2

    results = run_checks(spec_path)
    shall_fails = [r for r in results if r["status"] == "FAIL"]
    if args.as_json:
        print(json.dumps({"spec": str(spec_path), "results": results,
                          "shall_failures": len(shall_fails)}, indent=2))
    else:
        print(f"=== validate_entity_dimension: {spec_path.name} ===")
        for r in results:
            detail = f"  [{r.get('detail')}]" if r.get("detail") else ""
            print(f"  {r['status']:6s} {r['id']} ({r['kind']}) — {r['desc']}{detail}")
        print(f"SHALL failures: {len(shall_fails)}"
              + ("" if args.strict else " (Advisory mode — exit 0)"))
    return 1 if (args.strict and shall_fails) else 0


if __name__ == "__main__":
    sys.exit(main())
