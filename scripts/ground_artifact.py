#!/usr/bin/env python3
"""
ground_artifact.py — Ontology binding GENERATOR (the "connect with ontology" feature).

The generate/suggest counterpart to the detect-only scripts/check_skill_grounding.py.
Where check_skill_grounding.py COUNTS existing inline aget:concept/X references and
flags 0-binding files, this script CONNECTS an artifact to the ontology: it scans a
target file for ontology prefLabels appearing as noun phrases and emits ranked,
copy-pasteable inline-binding suggestions the author can insert.

This closes the missing half of INIT-ONTOLOGY-SPEC-BINDING Stream 3 ("graduate to
Strict + auto-suggest", v3.19 success metric) and remediates the L924 binding gap:
classification without consequence stays decorative until something proposes the
binding, not merely measures its absence.

Concepts (this script binds to the ontology it operationalizes):
  - aget:concept/NormativeConceptBinding (C641) — the binding this script proposes
  - aget:concept/InlineUriReference       (C642) — the pattern it emits
  - aget:concept/SpecificationToOntologyBinding (C644) — the spec-layer target
  - aget:concept/BackwardLinking          (C649) — reciprocal-link reminder it prints
  - aget:concept/VocabularyDecorationFailure (C646) — the counter it remediates
  - aget:concept/BindOnceDecayOften       (C650) — the decay it helps re-bind

Usage:
  python3 scripts/ground_artifact.py --file <path>
  python3 scripts/ground_artifact.py --file aget/specs/SOME_SPEC.md --top 20
  python3 scripts/ground_artifact.py --file <path> --json
  python3 scripts/ground_artifact.py --self-test

Exit codes:
  0  Ran successfully (suggestions printed, or none needed)
  1  No suggestions AND file already has >=1 binding (already grounded)
  2  Target file or ontology not found
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ONTOLOGY_CANDIDATES = [
    REPO / "ontology" / "ONTOLOGY_personal_ai_systems_v1.0.yaml",
    REPO.parent / "aget" / "ontology" / "ONTOLOGY_personal_ai_systems_v1.0.yaml",
]

# A prefLabel is suggestion-worthy only if it is specific enough to avoid noise:
# multi-word, OR a single word of >= MIN_SINGLE_LEN characters.
MIN_SINGLE_LEN = 6
URI_REF_RE = re.compile(r"aget:concept/([A-Za-z][A-Za-z0-9_]+)")


def load_ontology(path: Path):
    """Parse concept blocks (id / uri / prefLabel) by line scan — no yaml dep,
    cheap on the 1.4MB vocabulary file. Returns list of dicts."""
    concepts = []
    cur = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m_id = re.match(r"\s*-\s+id:\s*(C\d+)\s*$", line)
        if m_id:
            if cur.get("id") and cur.get("prefLabel"):
                concepts.append(cur)
            cur = {"id": m_id.group(1)}
            continue
        m_uri = re.match(r"\s+uri:\s*(aget:concept/\S+)\s*$", line)
        if m_uri and cur:
            cur["uri"] = m_uri.group(1)
            continue
        m_pref = re.match(r"\s+prefLabel:\s*(.+?)\s*$", line)
        if m_pref and cur and "prefLabel" not in cur:
            cur["prefLabel"] = m_pref.group(1).strip().strip('"').strip("'")
            continue
    if cur.get("id") and cur.get("prefLabel"):
        concepts.append(cur)
    return concepts


def is_specific(label: str) -> bool:
    if " " in label:
        return True
    return len(label) >= MIN_SINGLE_LEN


def specificity(label: str) -> tuple:
    """Rank: more words first, then longer label."""
    return (len(label.split()), len(label))


def scan(file_path: Path, concepts):
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # concepts already bound in the file (by URI suffix) — skip suggesting these
    already_bound = set(URI_REF_RE.findall(text))
    existing_ref_count = len(URI_REF_RE.findall(text))

    suggestions = []
    seen = set()
    for c in concepts:
        label = c.get("prefLabel", "")
        uri = c.get("uri", "")
        suffix = uri.split("/")[-1] if uri else ""
        if not label or not uri or not is_specific(label):
            continue
        if suffix in already_bound or suffix in seen:
            continue
        # whole-phrase, word-boundary match (case-sensitive — prefLabels are TitleCase nouns)
        pat = re.compile(r"(?<![\w-])" + re.escape(label) + r"(?![\w-])")
        for i, line in enumerate(lines, 1):
            # don't suggest where this exact URI already sits on the line
            if pat.search(line):
                suggestions.append(
                    {
                        "line": i,
                        "phrase": label,
                        "concept_id": c["id"],
                        "uri": uri,
                        "specificity": specificity(label),
                        "context": line.strip()[:100],
                    }
                )
                seen.add(suffix)
                break  # one suggestion per concept (first occurrence)

    suggestions.sort(key=lambda s: s["specificity"], reverse=True)
    return existing_ref_count, suggestions


def main():
    ap = argparse.ArgumentParser(description="Suggest ontology bindings for an artifact.")
    ap.add_argument("--file", help="target artifact to ground")
    ap.add_argument("--top", type=int, default=15, help="max suggestions (default 15)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    onto = next((p for p in ONTOLOGY_CANDIDATES if p.exists()), None)
    if onto is None:
        print("ERROR: ontology YAML not found in known locations.", file=sys.stderr)
        return 2
    concepts = load_ontology(onto)

    if args.self_test:
        assert len(concepts) > 100, f"expected >100 concepts, parsed {len(concepts)}"
        sample = next((c for c in concepts if c["id"] == "C001"), None)
        assert sample and sample["prefLabel"] == "Principal", f"C001 parse failed: {sample}"
        # synthetic artifact mentioning two specific multi-word prefLabels
        ml = [c["prefLabel"] for c in concepts if " " in c["prefLabel"]][:2]
        tmp = REPO / "scripts" / ".ground_selftest.tmp"
        tmp.write_text(f"The {ml[0]} relates to the {ml[1]} in this artifact.\n")
        cnt, sugg = scan(tmp, concepts)
        tmp.unlink()
        assert cnt == 0, "self-test artifact should have 0 existing bindings"
        assert len(sugg) >= 2, f"expected >=2 suggestions, got {len(sugg)}"
        print(f"SELF-TEST PASS: {len(concepts)} concepts parsed; "
              f"{len(sugg)} suggestions on synthetic artifact.")
        return 0

    if not args.file:
        ap.error("--file is required (or use --self-test)")
    target = Path(args.file)
    if not target.is_absolute():
        target = REPO / target
    if not target.exists():
        print(f"ERROR: target file not found: {target}", file=sys.stderr)
        return 2

    existing, suggestions = scan(target, concepts)
    top = suggestions[: args.top]

    if args.json:
        print(json.dumps(
            {
                "file": str(target.relative_to(REPO)) if str(target).startswith(str(REPO)) else str(target),
                "existing_bindings": existing,
                "ontology_concepts": len(concepts),
                "suggested": top,
                "suggested_total": len(suggestions),
            },
            indent=2,
        ))
    else:
        rel = target.relative_to(REPO) if str(target).startswith(str(REPO)) else target
        print(f"=== ground-artifact: {rel} ===")
        print(f"Ontology: {len(concepts)} concepts | Existing inline bindings: {existing}")
        if not top:
            print("No un-bound specific prefLabels found — artifact is grounded or vocabulary-light.")
        else:
            print(f"Suggested bindings ({len(top)} of {len(suggestions)}, ranked by specificity):\n")
            for s in top:
                print(f"  L{s['line']:>4}  \"{s['phrase']}\"  →  {s['uri']} ({s['concept_id']})")
                print(f"        ctx: {s['context']}")
            print("\nInsert as inline normative reference, e.g.:")
            ex = top[0]
            print(f"  ... {ex['phrase']} (`{ex['uri']}`, {ex['concept_id']}) ...")
            print("Reciprocal reminder (C649 BackwardLinking): if a binding declares "
                  "skos:related, back-edit the target concept.")

    # exit 1 = nothing to suggest but already grounded; 0 otherwise
    return 1 if (not suggestions and existing > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
