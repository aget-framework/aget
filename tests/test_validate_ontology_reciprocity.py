"""V-tests for scripts/validate_ontology_reciprocity.py scope separation (#1579 / C-22-18).

Pins the L1030 fix: dangling-detection is whole-vocab, reciprocity is cluster-local,
cross-cluster references are a non-defect line excluded from TOTAL DEFECTS.
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "validate_ontology_reciprocity",
    Path(__file__).resolve().parent.parent / "scripts" / "validate_ontology_reciprocity.py",
)
_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_mod)
validate = _mod.validate


def _concept(cid, uri, related=None, broader=None, narrower=None):
    c = {"id": cid, "uri": uri, "prefLabel": cid}
    if related:
        c["related"] = related
    if broader:
        c["broader"] = broader
    if narrower:
        c["narrower"] = narrower
    return c


def test_cross_cluster_ref_is_not_dangling():
    """A scoped concept referencing an existing out-of-scope concept → 0 dangling, 1 cross-cluster (#1579 evidence)."""
    full = [
        _concept("C841", "aget:concept/A", related=["aget:concept/Z"]),  # scoped, points out-of-scope
        _concept("C900", "aget:concept/Z"),                              # exists, out-of-scope
    ]
    scoped = [full[0]]
    findings = validate(scoped, all_concepts=full)
    assert findings["totals"]["dangling"] == 0, "existing cross-cluster target must NOT be dangling"
    assert findings["totals"]["cross_cluster"] == 1
    assert findings["totals"]["total_defects"] == 0, "cross-cluster refs are excluded from TOTAL DEFECTS"


def test_true_dangling_is_detected():
    """A reference resolving nowhere in the full vocab IS dangling."""
    full = [_concept("C841", "aget:concept/A", related=["aget:concept/NOWHERE"])]
    findings = validate(full, all_concepts=full)
    assert findings["totals"]["dangling"] == 1
    assert findings["totals"]["cross_cluster"] == 0


def test_whole_ontology_backward_compat():
    """No all_concepts (whole run) → scoped == universe → cross_cluster always 0."""
    full = [
        _concept("C1", "aget:concept/A", related=["aget:concept/B"]),
        _concept("C2", "aget:concept/B", related=["aget:concept/A"]),  # reciprocal
    ]
    findings = validate(full)
    assert findings["totals"]["cross_cluster"] == 0
    assert findings["totals"]["dangling"] == 0
    assert findings["totals"]["lane1"] == 0, "reciprocal related links → no lane-1 defect"


def test_reciprocity_stays_cluster_local():
    """Reciprocity is NOT enforced across the scope boundary (can't edit out-of-scope concepts)."""
    full = [
        _concept("C841", "aget:concept/A", related=["aget:concept/Z"]),  # scoped, no reciprocal from Z
        _concept("C900", "aget:concept/Z"),                              # out-of-scope, does not point back
    ]
    scoped = [full[0]]
    findings = validate(scoped, all_concepts=full)
    assert findings["totals"]["lane1"] == 0, "cross-boundary asymmetry is not a cluster-local defect"
    assert findings["totals"]["cross_cluster"] == 1
