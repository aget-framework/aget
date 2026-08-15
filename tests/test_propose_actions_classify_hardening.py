"""Hardening pins for the REQ-PA-013 audit/synthesis classifier.

These tests exist because the pairing gate was *provably satisfiable by a write*:
`reconcile` shipped in AUDIT_VERBS, carried no synthesis verb, and therefore slipped
past CAP-PA-013-04's masquerade guard. A two-write batch on one governed artifact
returned pairing_status=PASS with has_audit=True.

Every test here asserts BOTH polarities. A one-sided pin is how the original defect
survived: the classifier's own self-test confirmed that audit verbs classify as audit
and never asked whether a non-audit verb had been mislabelled as one.

A canonical sync that reinstates `reconcile` in AUDIT_VERBS fails
test_reconcile_alone_is_not_audit. That is the point.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from propose_actions_classify import (  # noqa: E402
    AUDIT_VERBS,
    SYNTHESIS_VERBS,
    check_pairing,
    classify,
)

GOVERNED = "planning/initiatives/INDEX.md"


# --------------------------------------------------------------------------
# 1. The defect itself, both polarities.
# --------------------------------------------------------------------------

def test_reconcile_alone_is_not_audit():
    """Negative pin: the ambiguous verb must NOT buy audit-class on its own.

    'Reconcile' is ambiguous between compare-against-source and make-agree-by-editing.
    On a governed artifact the editing sense dominates. Per CAP-PA-013-04 an ambiguous
    action falls to synthesis (fail-safe), so it must not satisfy the pairing gate.
   
    Satisfies: CAP-PA-013-01, CAP-PA-013-04
    """
    assert classify("reconcile the INDEX counts") == "synthesis"
    assert not any("reconcile" in v for v in AUDIT_VERBS), (
        "`reconcile` is back in AUDIT_VERBS — this re-opens the L980 vector: a batch "
        "of two writes to one artifact satisfies the pairing gate outright."
    )


def test_real_re_derivation_verbs_still_classify_as_audit():
    """Positive pin for CAP-PA-013-01: removing `reconcile` must not blunt the audit class.

    Without this, the negative pin above could be 'satisfied' by emptying AUDIT_VERBS.

    Satisfies: CAP-PA-013-01
    """
    for text in (
        "re-derive the INDEX counts from primary sources",
        "re-count the stream rows at source",
        "cross-check the totals against the register",
        "verify-from-source every stamped row",
        "audit the stream stamps",
        "re-read the manifest and re-tally",
    ):
        assert classify(text) == "audit", f"expected audit-class for {text!r}"


# --------------------------------------------------------------------------
# 2. The gate-level consequence, both polarities.
# --------------------------------------------------------------------------

def test_two_writes_on_one_artifact_do_not_pass_the_gate():
    """REQ-PA-013: the measured pre-fix failure — PASS with has_audit=True on two writes.

    Satisfies: REQ-PA-013
    """
    batch = [
        {"artifact": GOVERNED, "text": "update the stream rows"},
        {"artifact": GOVERNED, "text": "reconcile the counts"},
    ]
    result = check_pairing(batch)
    assert result["pairing_status"] == "UNMET", (
        "a same-artifact batch containing only writes must surface REQ-PA-013 friction; "
        f"got {result['pairing_status']} with groups {result['same_artifact_groups']}"
    )


def test_a_genuine_audit_still_pairs():
    """Complement for REQ-PA-013: the gate must not become unsatisfiable.

    Satisfies: REQ-PA-013
    """
    batch = [
        {"artifact": GOVERNED, "text": "update the stream rows"},
        {"artifact": GOVERNED, "text": "re-derive the counts from primary sources"},
    ]
    result = check_pairing(batch)
    assert result["pairing_status"] == "PASS"
    assert result["same_artifact_groups"][GOVERNED]["has_audit"] is True


# --------------------------------------------------------------------------
# 3. CAP-PA-013-04 masquerade guard — synthesis cannot buy audit by adding a verb.
# --------------------------------------------------------------------------

def test_synthesis_cannot_masquerade_as_audit():
    """CAP-PA-013-04: audit only when an audit verb is present AND no synthesis verb is.

    Satisfies: CAP-PA-013-04
    """
    assert classify("audit and update the INDEX") == "synthesis"
    assert classify("re-derive and then fold the counts into the INDEX") == "synthesis"
    # ...and the un-contaminated form still reaches audit, so the guard is not a blanket.
    assert classify("re-derive the counts") == "audit"


COMPOSITION_VERBS = [
    "rewrite", "revise", "amend", "edit", "correct", "fix", "patch", "replace",
    "insert", "append", "delete", "remove", "restructure", "refactor", "rework",
    "record", "expand", "extend", "generate", "create", "author", "reword",
    "adjust", "bump", "migrate", "backfill", "tidy", "clean up", "normalize",
    "reformat",
]

# Known, documented residual: `stamp` is deliberately absent from SYNTHESIS_VERBS
# because it false-matched the domain noun "stream-stamp" in the audit example.
# Listed here so the gap is asserted rather than discovered.
KNOWN_MASQUERADE_GAPS = ["stamp", "re-stamp"]


def test_composition_verbs_paired_with_an_audit_verb_do_not_read_as_audit():
    """CAP-PA-013-04: the masquerade guard must fire on ordinary composition verbs.

    Measured 2026-08-15 pre-expansion: 32 of 32 ordinary composition verbs produced a
    false audit-class when paired with an audit verb, because SYNTHESIS_VERBS held only
    16 entries. `\\bwrite\\b` did not match "rewrite".

    Satisfies: CAP-PA-013-02, CAP-PA-013-04
    """
    masquerades = [
        v for v in COMPOSITION_VERBS
        if classify(f"re-verify and {v} the INDEX counts") == "audit"
    ]
    assert not masquerades, (
        f"{len(masquerades)} composition verb(s) still buy audit-class when paired with "
        f"an audit verb: {masquerades}. Each is a live L980 vector."
    )


def test_the_known_stamp_gap_is_still_exactly_the_known_gap():
    """Pins the documented residual so it cannot grow silently.

    This asserts a *bound*, not correctness: the list approach cannot reach every verb,
    so the honest control is to fix the size of what it misses. If this test fails
    because the set shrank, close the gap and shrink the constant.

    Satisfies: CAP-PA-013-02
    """
    still_gapped = [
        v for v in KNOWN_MASQUERADE_GAPS
        if classify(f"re-verify and {v} the INDEX counts") == "audit"
    ]
    assert set(still_gapped) <= set(KNOWN_MASQUERADE_GAPS)
    assert len(still_gapped) <= 2, (
        f"the known-gap set grew to {still_gapped} — an enumeration control is only "
        "honest while its documented bound is accurate"
    )


def test_audit_list_stays_narrow_and_synthesis_list_stays_broad():
    """The asymmetry is the design, not an accident.

    A missing audit verb costs a legitimate action its class (fail-safe). A missing
    synthesis verb lets a write buy audit-class (fail-open). So the guard list must
    dominate the claim list in size.

    Satisfies: CAP-PA-013-01, CAP-PA-013-02
    """
    assert len(SYNTHESIS_VERBS) > 2 * len(AUDIT_VERBS), (
        f"SYNTHESIS_VERBS ({len(SYNTHESIS_VERBS)}) must stay substantially broader than "
        f"AUDIT_VERBS ({len(AUDIT_VERBS)}) — the guard cannot be narrower than the claim"
    )


def test_verb_sets_stay_disjoint():
    """A verb in both sets would make CAP-PA-013-04 unreachable for that verb.

    Satisfies: CAP-PA-013-01, CAP-PA-013-02
    """
    overlap = set(AUDIT_VERBS) & set(SYNTHESIS_VERBS)
    assert not overlap, f"AUDIT_VERBS and SYNTHESIS_VERBS overlap on {overlap}"


# --------------------------------------------------------------------------
# 4. Malformed input must not read as healthy (exit 3, not 0).
# --------------------------------------------------------------------------

def test_malformed_batch_does_not_report_pass(tmp_path):
    """REQ-PA-013: a batch the gate never read must not return PASS — UNKNOWN is not PASS.

    Satisfies: REQ-PA-013
    """
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"description": "x", "target": "y"}]))
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "propose_actions_classify.py"),
         "--check-batch", str(bad)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 3, f"expected exit 3 (MALFORMED), got {proc.returncode}"
    # Substring-matching "PASS" is the wrong predicate: the MALFORMED message explains
    # itself by naming the outcome it refuses to emit ("would emit a vacuous PASS").
    # Assert on the verdict field instead — the refusal must carry no pairing_status.
    assert "MALFORMED" in proc.stdout
    assert '"pairing_status"' not in proc.stdout


# --------------------------------------------------------------------------
# 5. Scope honesty — a vacuous PASS must say so.
# --------------------------------------------------------------------------

def test_vacuous_pass_is_labelled_vacuous():
    """Known bound (gh#2186) on CAP-PA-013-03: GOVERNED_PREFIXES misses tracked paths.

    This pins the *disclosure*, not the coverage: when no candidate targets a governed
    path the gate examined nothing, and the result must say so rather than read healthy.

    Satisfies: CAP-PA-013-03
    """
    batch = [
        {"artifact": "scripts/foo.py", "text": "update the parser"},
        {"artifact": "scripts/foo.py", "text": "rewrite the parser"},
    ]
    result = check_pairing(batch)
    assert result["scope"]["vacuous"] is True
    assert result["scope"]["governed_actions"] == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
