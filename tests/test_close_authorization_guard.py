"""
Firing-falsifier tests for the Close Authorization Guard (Q3:A / L1102).

Each test asserts a verdict that would FLIP if the guard's logic were wrong — no
tautologies. The anchor case is the real v3.23 voided close: the guard MUST FAIL it.
"""
import importlib.util
import pathlib

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "close_authorization_guard",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "close_authorization_guard.py",
)
guard = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(guard)


# --- the real v3.23 defect: this is what actually got committed (cc4b8bd) ------
V323_VOIDED_CLOSE = (
    "**Plan_Status**: **CLOSED — PRIVATE MILESTONE (2026-06-20T07:36:36Z)** via "
    "`/aget-close-project` (D71). Terminated-with-deferral. **Reason** (principal-ruled): "
    "G-a (REQ-9 cut) + G-d Path-2 (public version-bump folded to v3.24); v3.23 finalized "
    "as a private milestone. **Closing agent**: private-aget-framework-AGET."
)

# --- the corrected/authorized form: attribution WITH a real event pointer ------
GOOD_AUTHORIZED_CLOSE = (
    "**Plan_Status**: **CLOSED — COMPLETE (2026-06-21)** via `/aget-close-project`. "
    "Reason: principal GO recorded in the Authorization log (Gate 7 close GO, principal "
    "selection Q1:A 2026-06-21). All public-ship gates passed."
)

# --- a legitimately autonomous close (no principal attribution) ----------------
AUTONOMOUS_CLOSE = (
    "**Plan_Status**: **COMPLETE (2026-06-20)** — dogfood plan; all 11 V-tests pass, "
    "deliverables landed. Agent-autonomous per Decision Authority Matrix (L-doc tier)."
)

# --- irreversible consequence, but made legible --------------------------------
IRREVERSIBLE_BUT_LEGIBLE = (
    "**Plan_Status**: **CLOSED — SUPERSEDED (2026-06-20)**. Principal GO 2026-06-20 "
    "(Authorization log). Consequence: this irreversible-ly skips the public version "
    "number and leaves a permanent gap — surfaced and authorized explicitly."
)


def verdict(text):
    return guard.evaluate(text)[0]


# 1. ANCHOR — the guard must catch the exact v3.23 defect
def test_v323_voided_close_fails():
    v, issues = guard.evaluate(V323_VOIDED_CLOSE)
    assert v == "FAIL"
    # both defects present: no event pointer AND illegible irreversible consequence
    joined = " ".join(issues)
    assert "CHECK-A" in joined  # principal-ruled without event pointer
    assert "CHECK-B" in joined  # private-milestone/fold consequence not made legible


# 2. Same attribution, but WITH an authorization-event pointer -> PASS
def test_authorized_close_with_event_pointer_passes():
    assert verdict(GOOD_AUTHORIZED_CLOSE) == "PASS"


# 3. Falsifier for CHECK-A: strip the pointer from the good close -> must FAIL
def test_check_a_fires_when_pointer_removed():
    stripped = GOOD_AUTHORIZED_CLOSE.replace(
        "recorded in the Authorization log (Gate 7 close GO, principal "
        "selection Q1:A 2026-06-21)",
        "ruled by the principal",
    )
    assert verdict(stripped) == "FAIL"


# 4. Agent-autonomous close (no principal attribution) -> PASS (guard N/A)
def test_autonomous_close_passes():
    assert verdict(AUTONOMOUS_CLOSE) == "PASS"


# 5. Irreversible consequence made legible -> PASS
def test_irreversible_but_legible_passes():
    assert verdict(IRREVERSIBLE_BUT_LEGIBLE) == "PASS"


# 6. Falsifier for CHECK-B: same as #5 but remove the legibility -> must FAIL
def test_check_b_fires_when_legibility_removed():
    illegible = IRREVERSIBLE_BUT_LEGIBLE.replace(
        "Consequence: this irreversible-ly skips the public version "
        "number and leaves a permanent gap — surfaced and authorized explicitly.",
        "Finalized as a private milestone.",
    )
    assert verdict(illegible) == "FAIL"


# 7. A reopened/void plan is NOT a terminal close -> PASS (guard N/A)
def test_reopened_is_not_a_close():
    reopened = (
        "**Plan_Status**: **IN PROGRESS — REOPENED**. The prior CLOSED private-milestone "
        "close is VOID (unauthorized). v3.23.0 reclaimed."
    )
    assert verdict(reopened) == "PASS"


# 8. Empty / non-status text -> guard does not false-positive
def test_non_status_text_passes():
    assert verdict("Some prose with no Plan_Status and no close.") == "PASS"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))


# --- 2026-09-19: a principal-GO close must classify as attributed, not autonomous ----------
NODE1_CLOSE_2026_09_19 = """**Plan_Status**: Complete

> Closure authority: principal GO 2026-09-19 (stub, CAP-PP-018).

| 2026-09-19 ~19:50 | closure | **Ceremony performed under principal GO.** Entry gate:
`lawful-transition` BLOCK under every disposition -> L178 override, state unchanged. |
"""


def test_principal_go_close_is_attributed_with_pointer():
    """Regression: the guard PASSED this text on 2026-09-19 as 'agent-autonomous close'
    although the banner says principal GO. It must PASS as attributed-with-pointer."""
    verdict, issues = guard.evaluate(NODE1_CLOSE_2026_09_19)
    assert verdict == "PASS"
    assert any("principal-attributed + event-pointer present" in i for i in issues), issues
    assert not any("agent-autonomous" in i for i in issues), issues


def test_principal_go_without_pointer_fails_check_a():
    """Negative control: 'principal GO' with no dated/linked event is attribution without
    provenance -- CHECK-A must FAIL, which it could not before the GO branch existed."""
    text = "**Plan_Status**: Complete\n\nClosed under principal GO, no further record.\n"
    verdict, issues = guard.evaluate(text)
    assert verdict == "FAIL"
    assert any("CHECK-A FAIL" in i for i in issues), issues
