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


# --- schema gate: an optional check must not default to healthy (2026-07-29) ---


def test_malformed_batch_fails_closed_instead_of_vacuous_pass():
    """A batch with the wrong keys used to return pairing_status=PASS over zero groups.

    Every artifact read as "", so nothing was governed, so no group had >=2 members, so
    nothing could be unpaired. The L980 Layer-5 gate reported healthy on a batch it had
    never looked at. Caught live while proposing an action batch on 2026-07-29.
    """
    import pytest

    wrong_keys = [
        {"desc": "audit the counts", "path": "governance/GOALS.md"},
        {"desc": "write the summary", "path": "governance/GOALS.md"},
    ]
    with pytest.raises(ValueError, match="vacuous PASS"):
        check_pairing(wrong_keys)


def test_partial_schema_is_accepted():
    """Only one known key is required — 'text' alone is a legitimate (ungoverned) action."""
    rep = check_pairing([{"text": "measure something"}])
    assert rep["pairing_status"] == "PASS"
    assert rep["scope"]["governed_actions"] == 0


def test_scope_block_marks_a_vacuous_pass_as_vacuous():
    """vg2:R3 — a PASS must carry what it actually covered."""
    rep = check_pairing([{"text": "audit x", "artifact": "workspace/scratch.md"}])
    assert rep["pairing_status"] == "PASS"
    assert rep["scope"]["vacuous"] is True

    paired = check_pairing(
        [
            {"text": "re-derive the counts", "artifact": "governance/GOALS.md"},
            {"text": "write the rollup", "artifact": "governance/GOALS.md"},
        ]
    )
    assert paired["pairing_status"] == "PASS"
    assert paired["scope"]["vacuous"] is False
    assert paired["scope"]["governed_actions"] == 2


def test_a_declared_subject_cannot_split_a_same_artifact_group():
    """Satisfies: REQ-PA-013 -- two writes to one artifact stay one group whatever subjects they declare (R1-04)."""
    batch = [
        {"text": "write the summary", "artifact": "planning/X.md", "subject_id": "x"},
        {"text": "update the table", "artifact": "planning/X.md", "subject_id": "y"},
    ]
    rep = check_pairing(batch)
    assert rep["pairing_status"] == "UNMET", rep
