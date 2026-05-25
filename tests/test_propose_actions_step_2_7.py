"""
V-PA-013 — /aget-propose-actions Step 2.7 audit-after-synthesis pairing (L980 / gh#1476).

Replays the 2026-05-21 session arc that produced L980 (first in-flight self-catch of a
false synthesis-layer count claim on planning/initiatives/INDEX.md) and verifies the
Step 2.7 pre-flight catches the synthesis-without-audit pattern structurally.

Cases:
  - positive:        full L980 arc (2 synthesis + 1 audit on same artifact) -> PASS
  - negative:        L980 arc minus the audit Action                        -> UNMET (friction)
  - false-positive:  2 synthesis Actions on DISTINCT artifacts              -> PASS (no fire)
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from propose_actions_classify import classify, check_pairing, normalize_path  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "l980_session_2026_05_21_action_batch.json"


@pytest.fixture
def l980_arc():
    return json.loads(FIXTURE.read_text())


def test_fixture_loads_three_actions(l980_arc):
    assert len(l980_arc) == 3
    assert all("text" in a and "artifact" in a for a in l980_arc)


def test_per_action_classification_matches_expected(l980_arc):
    # Actions 1+2 = synthesis, Action 3 = audit (the L980 ground truth)
    for a in l980_arc:
        assert classify(a["text"]) == a["class_expected"], a["text"]


def test_positive_pairing_satisfied(l980_arc):
    # G2.2: full arc -> same-artifact group detected + audit-class present -> PASS
    rep = check_pairing(l980_arc)
    assert rep["pairing_status"] == "PASS"
    art = normalize_path("planning/initiatives/INDEX.md")
    assert art in rep["same_artifact_groups"]
    assert rep["same_artifact_groups"][art]["has_audit"] is True
    assert rep["same_artifact_groups"][art]["action_indices"] == [0, 1, 2]


def test_negative_unmet_surfaces_friction(l980_arc):
    # G2.3: remove the audit Action -> synthesis-only same-artifact group -> UNMET
    synthesis_only = [a for a in l980_arc if a["class_expected"] == "synthesis"]
    rep = check_pairing(synthesis_only)
    assert rep["pairing_status"] == "UNMET"
    assert normalize_path("planning/initiatives/INDEX.md") in rep["unpaired_artifacts"]


def test_false_positive_avoidance_distinct_artifacts():
    # G2.4: two synthesis Actions on DIFFERENT artifacts -> no same-artifact group -> PASS
    batch = [
        {"text": "Write Tier-1 placement rows", "artifact": "planning/VERSION_SCOPE_v3.19.0.md"},
        {"text": "Update the ACTIVE roster table", "artifact": "planning/initiatives/INDEX.md"},
    ]
    rep = check_pairing(batch)
    assert rep["pairing_status"] == "PASS"
    assert rep["same_artifact_groups"] == {}


def test_synthesis_cannot_masquerade_as_audit():
    # CAP-PA-013-04 fail-safe: an Action with BOTH verb-sets classifies synthesis,
    # so it cannot satisfy the pairing on its own.
    batch = [
        {"text": "Fold the initiative row", "artifact": "planning/initiatives/INDEX.md"},
        {"text": "Re-count then write the updated summary row", "artifact": "planning/initiatives/INDEX.md"},
    ]
    rep = check_pairing(batch)
    assert rep["pairing_status"] == "UNMET"  # both classify synthesis -> no audit -> friction


def test_non_governed_artifact_not_grouped():
    # Actions on a non-governed path (e.g. workspace/) are out of scope -> no friction
    batch = [
        {"text": "Write scratch notes", "artifact": "workspace/scratch.md"},
        {"text": "Update scratch notes", "artifact": "workspace/scratch.md"},
    ]
    rep = check_pairing(batch)
    assert rep["pairing_status"] == "PASS"
    assert rep["same_artifact_groups"] == {}
