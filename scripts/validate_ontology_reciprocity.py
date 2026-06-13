#!/usr/bin/env python3
"""
validate_ontology_reciprocity.py — Multi-lane SKOS reciprocity validator for AGET ontology.

Closes the gap surfaced by AUDIT_skosify_pilot_2026-05-07.md:
- Lane 1: skos:related ↔ skos:related (symmetric pair)
- Lane 2: skos:broader → skos:narrower (inverse pair, forward)
- Lane 3: skos:narrower → skos:broader (inverse pair, reverse)
- URI uniqueness (catches LifeDomain-class duplicates per gmelli/aget-aget#1253)
- prefLabel uniqueness (across distinct URIs)
- Dangling URI references

Implements the bug-fixed list/string coercion (today's spec+verify-first catch:
single-string broader/narrower fields were iterating character-by-character,
producing 12× false-positive over-counts).

Reference: AUDIT_skosify_pilot_2026-05-07.md, L929 (Cross-Fleet Binding-Gap
Triangulation), L930 (L-Doc Renumbering Race Condition), Skosify EKAW 2012
baseline (Suominen & Hyvönen — n=24, 100% defective).

Usage:
    python3 scripts/validate_ontology_reciprocity.py
    python3 scripts/validate_ontology_reciprocity.py --cluster C548-C562
    python3 scripts/validate_ontology_reciprocity.py --json
    python3 scripts/validate_ontology_reciprocity.py --ontology path/to/file.yaml
"""
import argparse
import json
import sys
import re
from pathlib import Path

DEFAULT_ONTOLOGY = "ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml"


def as_list(v):
    """Coerce single-URI string OR list-of-URIs into list. Skip None.

    The spec+verify-first catch: YAML allows `broader: <single-uri>` or
    `broader: [<uri1>, <uri2>]`. Iterating a single string iterates characters,
    not as one URI. This helper unifies both shapes.
    """
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return v
    return []


def parse_cluster_range(spec):
    """Parse a cluster range like 'C548-C562' into a (lo, hi) tuple."""
    m = re.match(r"C(\d+)-C(\d+)", spec)
    if not m:
        raise ValueError(f"invalid cluster spec: {spec!r}; expected 'C<lo>-C<hi>'")
    return int(m.group(1)), int(m.group(2))


def filter_concepts(concepts, cluster_range):
    """Filter concepts by C-id range, or return all if no range given."""
    if cluster_range is None:
        return concepts
    lo, hi = cluster_range
    out = []
    for c in concepts:
        cid = c.get("id", "")
        if cid.startswith("C") and cid[1:].isdigit():
            n = int(cid[1:])
            if lo <= n <= hi:
                out.append(c)
    return out


def validate(concepts, all_concepts=None):
    """Run all reciprocity + uniqueness checks. Returns dict of findings.

    Scope separation (#1579 / C-22-18, L1030):
    - **Reciprocity** (lanes 1-3) is CLUSTER-LOCAL — enforced only for links
      whose source AND target are both within the audited (scoped) set.
    - **Dangling** detection is WHOLE-VOCAB — a target is dangling only if it
      resolves nowhere in `all_concepts` (the full ontology).
    - **Cross-cluster refs** — targets that resolve in the full vocab but
      outside the scoped set — are reported on a distinct NON-DEFECT line and
      EXCLUDED from TOTAL DEFECTS (they are legitimate, not dangling).

    When `all_concepts` is None (whole-ontology run), scoped == universe, so
    cross_cluster is always empty and behaviour is identical to pre-#1579.
    """
    universe = all_concepts if all_concepts is not None else concepts
    by_uri = {}
    by_label = {}
    for c in concepts:
        uri = c.get("uri", "")
        lbl = c.get("prefLabel", "")
        if uri:
            by_uri.setdefault(uri, []).append(c)
        if lbl:
            by_label.setdefault(lbl, []).append(uri)

    scoped_uris = {u for u in by_uri}
    all_uris = {c.get("uri") for c in universe if c.get("uri")}
    by_uri_first = {}
    for c in universe:
        u = c.get("uri")
        if u and u not in by_uri_first:
            by_uri_first[u] = c

    related_def, broader_def, narrower_def = [], [], []
    dangling, cross_cluster = [], []

    def classify(sid, field, target):
        """'dangling' (nowhere) | 'cross' (out-of-scope but exists) | 'local'."""
        if target not in all_uris:
            dangling.append({"src": sid, "field": field, "target": target})
            return "dangling"
        if target not in scoped_uris:
            cross_cluster.append({"src": sid, "field": field, "target": target})
            return "cross"
        return "local"

    for c in concepts:
        src = c.get("uri")
        sid = c.get("id")
        for rel in as_list(c.get("related")):
            if classify(sid, "related", rel) != "local":
                continue
            tgt = by_uri_first.get(rel)
            if tgt and src not in as_list(tgt.get("related")):
                related_def.append({"src": sid, "field": "related", "target": rel})
        for b in as_list(c.get("broader")):
            if classify(sid, "broader", b) != "local":
                continue
            tgt = by_uri_first.get(b)
            if tgt and src not in as_list(tgt.get("narrower")):
                broader_def.append({"src": sid, "field": "broader→narrower", "target": b})
        for n in as_list(c.get("narrower")):
            if classify(sid, "narrower", n) != "local":
                continue
            tgt = by_uri_first.get(n)
            if tgt and src not in as_list(tgt.get("broader")):
                narrower_def.append({"src": sid, "field": "narrower→broader", "target": n})

    dup_uris = {u: [c.get("id") for c in cs] for u, cs in by_uri.items() if len(cs) > 1}
    dup_labels = {l: us for l, us in by_label.items() if len(set(us)) > 1}

    return {
        "concepts_audited": len(concepts),
        "lane1_related_defects": related_def,
        "lane2_broader_narrower_defects": broader_def,
        "lane3_narrower_broader_defects": narrower_def,
        "dangling_uri_refs": dangling,
        "cross_cluster_refs": cross_cluster,
        "duplicate_uris": dup_uris,
        "duplicate_prefLabels": dup_labels,
        "totals": {
            "lane1": len(related_def),
            "lane2": len(broader_def),
            "lane3": len(narrower_def),
            "dangling": len(dangling),
            "cross_cluster": len(cross_cluster),
            "duplicate_uris": len(dup_uris),
            "duplicate_prefLabels": len(dup_labels),
            "total_defects": (
                len(related_def) + len(broader_def) + len(narrower_def)
                + len(dangling) + len(dup_uris) + len(dup_labels)
            ),
        },
    }


def render_human(findings, cluster_spec=None):
    t = findings["totals"]
    out = []
    label = f"cluster {cluster_spec}" if cluster_spec else "whole ontology"
    out.append(f"=== SKOS reciprocity validation — {label} ===")
    out.append(f"Concepts audited: {findings['concepts_audited']}")
    out.append(f"Lane 1 (related):           {t['lane1']:>4}")
    out.append(f"Lane 2 (broader→narrower):  {t['lane2']:>4}")
    out.append(f"Lane 3 (narrower→broader):  {t['lane3']:>4}")
    out.append(f"Dangling URI references:    {t['dangling']:>4}")
    out.append(f"Cross-cluster refs (OK):    {t['cross_cluster']:>4}   (resolve out-of-scope; NOT defects — #1579)")
    out.append(f"Duplicate URIs:             {t['duplicate_uris']:>4}")
    out.append(f"Duplicate prefLabels:       {t['duplicate_prefLabels']:>4}")
    out.append(f"TOTAL DEFECTS:              {t['total_defects']:>4}")
    if findings["duplicate_uris"]:
        out.append("")
        out.append("Duplicate URIs (data-integrity violations — primary key collision):")
        for u, ids in findings["duplicate_uris"].items():
            out.append(f"  {u}  →  concepts: {ids}")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ontology", default=DEFAULT_ONTOLOGY,
                   help=f"Path to ontology YAML (default: {DEFAULT_ONTOLOGY})")
    p.add_argument("--cluster", default=None,
                   help="Cluster range like 'C548-C562' (default: whole ontology)")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON instead of human-readable summary")
    args = p.parse_args()

    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
        return 2

    path = Path(args.ontology)
    if not path.exists():
        print(f"ERROR: ontology file not found: {path}", file=sys.stderr)
        return 2

    data = yaml.safe_load(path.read_text())
    concepts = data.get("concepts", [])
    cluster_range = parse_cluster_range(args.cluster) if args.cluster else None
    scoped = filter_concepts(concepts, cluster_range)
    # Dangling resolves against the WHOLE vocab; reciprocity stays cluster-local (#1579).
    findings = validate(scoped, all_concepts=concepts)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(render_human(findings, args.cluster))

    return 0 if findings["totals"]["total_defects"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
