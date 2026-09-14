#!/usr/bin/env python3
"""Validate bindings from local vocabulary to named external standards.

WHY THIS EXISTS
---------------
Local concepts cite external standards in prose `source:` fields. Prose citation cannot carry
the one thing a binding must carry: **how strong the correspondence is**. "Receipt" appears in
ISO/IEC 13888-1, in RFC 4998, in IETF SCITT, and in this framework -- and they are not the same
object. SCITT's Receipt is *a signature over verifiable data structure proofs*. A local Receipt
is *a durable, dated record*. Both are receipts; only one is cryptographic.

Asserting equivalence where only similarity holds is how a framework comes to believe its own
log entries are attestations. **A local record is not thereby a cryptographic receipt.**

WHAT A BINDING MUST CARRY
-------------------------
  predicate   one of exactMatch | closeMatch | relatedMatch | broadMatch | narrowMatch.
              SKOS semantics: exactMatch asserts interchangeability across applications;
              closeMatch asserts similarity that may not survive every application.
  scope       what the correspondence DOES cover and what it explicitly does NOT.
              A binding without a stated non-coverage is an equivalence claim in disguise.
  source      a consumer-resolvable identifier -- a standard number, RFC, or URI a third
              party can look up WITHOUT access to this repository. A local file path is not
              a consumer-resolvable source.

THE STRENGTH RULE
-----------------
`exactMatch` is refused unless the binding also carries `equivalence_justification` naming the
definitional property that makes the two interchangeable. This is deliberately hard to satisfy:
the failure mode is not under-claiming.

A binding whose local concept is NOT cryptographic may not `exactMatch` a standard flagged
`cryptographic: true`. That pairing is the specific overclaim this checker exists to refuse.

Read-only.

USAGE
  check_standard_bindings.py --bindings ontology/EXTERNAL_STANDARD_BINDINGS.yaml
  check_standard_bindings.py --bindings B --json

EXIT CODES
  0  every binding is well-formed and no overclaim
  1  at least one overclaim or malformed binding
  2  a binding could not be evaluated  (UNAVAILABLE, never a pass)
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

OK, OVERCLAIM, MALFORMED, UNAVAILABLE = "OK", "OVERCLAIM", "MALFORMED", "UNAVAILABLE"

PREDICATES = {"exactMatch", "closeMatch", "relatedMatch", "broadMatch", "narrowMatch"}
# A source a third party can resolve without this repository.
RESOLVABLE = re.compile(
    r"^(ISO/IEC\s+\d|ISO\s+\d|IETF\s|RFC\s?\d|NIST\s|IEEE\s|W3C\s|https?://|urn:|doi:|draft-)",
    re.I)


class InputError(Exception):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"bindings unreadable: {exc}") from exc
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        pass
    else:
        if not isinstance(doc, dict):
            raise InputError("bindings must parse to a mapping")
        return doc
    try:
        import yaml
    except ImportError as exc:
        raise InputError("bindings are not JSON and PyYAML is unavailable") from exc
    try:
        doc = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001
        raise InputError(f"bindings not parseable: {exc}") from exc
    if not isinstance(doc, dict):
        raise InputError("bindings must parse to a mapping")
    return doc


def check_one(b: dict[str, Any]) -> dict[str, Any]:
    concept = b.get("concept", "<unnamed>")
    problems: list[str] = []

    pred = b.get("predicate")
    if pred not in PREDICATES:
        problems.append(f"predicate {pred!r} is not one of {sorted(PREDICATES)}")

    source = str(b.get("source", "")).strip()
    if not source:
        problems.append("no source")
    elif not RESOLVABLE.match(source):
        problems.append(
            f"source {source!r} is not consumer-resolvable: a third party must be able to look "
            f"it up without access to this repository (standard number, RFC, draft, or URI)")

    scope = b.get("scope") or {}
    covers = str(scope.get("covers", "")).strip() if isinstance(scope, dict) else ""
    excludes = str(scope.get("does_not_cover", "")).strip() if isinstance(scope, dict) else ""
    if not covers:
        problems.append("scope.covers is empty")
    if not excludes:
        problems.append(
            "scope.does_not_cover is empty. A binding that states only what it covers is an "
            "equivalence claim in disguise; name what the correspondence does NOT carry")

    if problems:
        return {"concept": concept, "state": MALFORMED, "problems": problems}

    # --- strength ------------------------------------------------------------
    if pred == "exactMatch":
        if not str(b.get("equivalence_justification", "")).strip():
            return {"concept": concept, "state": OVERCLAIM,
                    "problems": ["exactMatch asserts interchangeability across applications and "
                                 "carries no equivalence_justification naming the definitional "
                                 "property that makes the two interchangeable"]}
        if b.get("external_is_cryptographic") is True and b.get("local_is_cryptographic") is not True:
            return {"concept": concept, "state": OVERCLAIM,
                    "problems": ["exactMatch from a non-cryptographic local concept to a "
                                 "cryptographic external standard. A local record is not thereby "
                                 "a cryptographic receipt; closeMatch or relatedMatch is the "
                                 "warranted strength"]}
    return {"concept": concept, "state": OK, "problems": []}


def assess(doc: dict[str, Any]) -> dict[str, Any]:
    bindings = doc.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise InputError("no 'bindings' list")
    rows = [check_one(b) for b in bindings if isinstance(b, dict)]
    if len(rows) != len(bindings):
        raise InputError("every binding must be a mapping")
    counts = {k: sum(1 for r in rows if r["state"] == k) for k in (OK, OVERCLAIM, MALFORMED)}
    overall = OK if counts[OVERCLAIM] == 0 and counts[MALFORMED] == 0 else OVERCLAIM
    return {"bindings": rows, "counts": counts, "overall": overall}


def render(res: dict[str, Any]) -> str:
    out = [f"external standard bindings: {res['overall']}", ""]
    for r in res["bindings"]:
        out.append(f"  {r['state']:<10} {r['concept']}")
        for p in r["problems"]:
            out.append(f"             -- {p}")
    c = res["counts"]
    out += ["", f"  ok={c[OK]}  overclaim={c[OVERCLAIM]}  malformed={c[MALFORMED]}",
            "  exactMatch asserts interchangeability. Similarity is closeMatch. A local record "
            "is not thereby a cryptographic receipt."]
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    return 0 if res["overall"] == OK else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate external-standard bindings.")
    ap.add_argument("--bindings", type=Path, required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        res = assess(load(args.bindings))
    except InputError as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
