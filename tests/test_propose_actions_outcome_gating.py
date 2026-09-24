"""Red fixtures for /aget-propose-actions outcome gating (gh#2703; proposed REQ-PA-022 / V-PA-022).

Written at Gate 0 of planning/PROJECT_PLAN_v3.35.0_value_row_propose_actions_repairs_v1.0.md,
BEFORE the implementation existed: every test ran red (strict xfail) on 2026-09-24 at 09:40, and
went green at Gate 1 when check_outcome_gating and close_summary landed and the markers were removed.

Contract (gh#2703):
  1. When the batch's focus is an OUTCOME, every action declares whether it moves the outcome or
     only moves measurement.
  2. An outcome-moving step that is gated (principal push approval, a cross-Aget write, a
     ruling) must be listed under "Decisions needed" at proposal time. It may not be dropped.
  3. An outcome-focused batch with no outcome-moving action and no listed gated decision cannot
     move its outcome; that must be said, not closed as done.
  4. The close report splits outcome from measurement and names any gated act still owed.

Reference implementation site: scripts/propose_actions_classify.py (`check_outcome_gating`,
`close_summary`), next to the Step 2.7 pairing check.
"""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "propose_actions_classify.py"


def _load():
    spec = importlib.util.spec_from_file_location("propose_actions_classify_og", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "check_outcome_gating"):
        pytest.fail("not implemented: check_outcome_gating")
    return mod


CI_FIX = {"text": "fix the health instrument so unreadable CI no longer counts as passing",
          "moves": "measurement"}
PUSH = {"text": "push the CI fixes to origin", "moves": "outcome", "gated": True,
        "gate": "principal push approval"}


def test_gated_outcome_step_must_be_listed_as_a_decision():
    """Satisfies: REQ-PA-022 -- gated outcome step must be listed as a decision."""
    m = _load()
    batch = {"focus_kind": "outcome", "focus": "remediate CI",
             "actions": [CI_FIX, dict(PUSH, decision_listed=False)]}
    r = m.check_outcome_gating(batch)
    assert r["status"] == "UNMET", r
    assert "push the CI fixes" in " ".join(r["reasons"]), r


def test_gated_outcome_step_listed_passes():
    """Satisfies: REQ-PA-022 -- gated outcome step listed passes."""
    m = _load()
    batch = {"focus_kind": "outcome", "focus": "remediate CI",
             "actions": [CI_FIX, dict(PUSH, decision_listed=True)]}
    assert m.check_outcome_gating(batch)["status"] == "PASS"


def test_outcome_focus_with_only_measurement_actions_is_unmet():
    """Satisfies: REQ-PA-022 -- outcome focus with only measurement actions is unmet."""
    m = _load()
    batch = {"focus_kind": "outcome", "focus": "remediate CI", "actions": [CI_FIX]}
    r = m.check_outcome_gating(batch)
    assert r["status"] == "UNMET", r
    assert any("cannot move" in x for x in r["reasons"]), r


def test_missing_moves_tag_under_outcome_focus_is_unmet():
    """Satisfies: REQ-PA-022 -- missing moves tag under outcome focus is unmet."""
    m = _load()
    batch = {"focus_kind": "outcome", "focus": "remediate CI",
             "actions": [{"text": "do something"}, dict(PUSH, decision_listed=True)]}
    r = m.check_outcome_gating(batch)
    assert r["status"] == "UNMET" and any("moves" in x for x in r["reasons"]), r


def test_measurement_focus_needs_no_outcome_mover():
    """Satisfies: REQ-PA-022 -- measurement focus needs no outcome mover."""
    m = _load()
    batch = {"focus_kind": "measurement", "focus": "improve the health instrument",
             "actions": [CI_FIX]}
    assert m.check_outcome_gating(batch)["status"] == "PASS"


def test_malformed_batch_is_refused_not_passed():
    """Satisfies: REQ-PA-022 -- a batch without a declared focus kind is refused, not passed (gh#2703)."""
    m = _load()
    r = m.check_outcome_gating({"actions": [CI_FIX]})  # no focus_kind
    assert r["status"] == "UNAVAILABLE", r


def test_close_summary_splits_outcome_from_measurement():
    """Satisfies: REQ-PA-022 -- the close report splits outcome from measurement and names the gated act owed (gh#2703)."""
    m = _load()
    s = m.close_summary(outcome_changed=False, measurement_changed=True,
                        gated_owed=["push the CI fixes (principal push approval)"])
    assert "outcome unchanged" in s and "measurement improved" in s, s
    assert "gated act owed: push the CI fixes" in s, s


# ---- independent review round 1: regression cases ---------------------------------

def test_non_object_action_is_unavailable_not_a_crash():
    """Satisfies: REQ-PA-022 -- a malformed action list is UNAVAILABLE, never an exception (R1-05)."""
    m = _load()
    assert m.check_outcome_gating({"focus_kind": "outcome", "actions": ["x"]})["status"] == "UNAVAILABLE"


def test_string_boolean_is_unavailable_not_truthy():
    """Satisfies: REQ-PA-022 -- decision_listed "false" is not a boolean and cannot pass by truthiness (R1-05)."""
    m = _load()
    batch = {"focus_kind": "outcome", "actions": [CI_FIX, dict(PUSH, decision_listed="false")]}
    assert m.check_outcome_gating(batch)["status"] == "UNAVAILABLE"


def test_gated_outcome_step_without_a_gate_is_unavailable():
    """Satisfies: REQ-PA-022 -- a gated step naming no gate has no exact change ready to approve (R1-05)."""
    m = _load()
    step = {"text": "push", "moves": "outcome", "gated": True, "decision_listed": True}
    assert m.check_outcome_gating({"focus_kind": "outcome", "actions": [step]})["status"] == "UNAVAILABLE"


def test_saying_the_batch_cannot_move_its_outcome_passes_that_leg():
    """Satisfies: REQ-PA-022 -- the requirement is to say so; an explicit acknowledgement passes (R1-06)."""
    m = _load()
    batch = {"focus_kind": "outcome", "acknowledges_no_outcome_mover": True, "actions": [CI_FIX]}
    r = m.check_outcome_gating(batch)
    assert r["status"] == "PASS" and r["notes"], r
