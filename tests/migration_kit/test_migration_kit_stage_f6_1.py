"""Stage F6.1 (weekly-train:R35, text only): Gate 3 exit (a) asks each accepted limit to stand in the release text and
in the SOP. REVW12's B206 reply (`0999c7347`) found two that stood only in the release text and stated what the SOP
must say. Each row fails on F6's SOP and passes after; its control is the release-note sentence it mirrors."""
from test_migration_kit_release_text import NOTES, row


def test_f6_1_d2_the_sop_states_that_a_run_dying_before_its_first_act_leaves_the_earlier_result_current():
    """D-2: B3, where the SOP states the first-act rule, also states its limit."""
    assert "A run that dies before its first act (the interpreter or an import fails), or" in NOTES
    b3 = row("B3")
    assert "A run that dies before its first act (the interpreter or an import fails), or that cannot append to its " \
           "run log, leaves no run record, and the earlier result for that output stays current." in b3


def test_f6_1_d13_the_sop_states_that_no_kit_step_verifies_extension_survival_after_a_migration():
    """D-13 / S-204: B8, the after-run check, states what it does not read back."""
    assert "No kit step runs `verify_extension_survival.py --verify` after a migration" in NOTES
    b8 = row("B8")
    assert "No kit step runs `verify_extension_survival.py --verify` after a migration" in b8
    assert "only for payload items (KEEP unchanged, every line of a MERGE surviving)" in b8
