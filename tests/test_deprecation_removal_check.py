"""Both-polarity guard for check_deprecation_removals.py.

Asserting only that an overdue row FAILs is insufficient — the first version of this
checker did that correctly and still shipped two false positives, because its terminal
test could not fire (wrong cell index) and its vocabulary was too narrow (`Removed` only,
missing the `Retired` a real row uses). A one-sided test would have passed on that build.

So both directions are asserted, and the `Retired` case is its own test because it is the
one a `removed`-only predicate silently converts into an overdue row.
"""
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cdr", ROOT / "scripts" / "check_deprecation_removals.py"
)
cdr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cdr)

CUR = (3, 30, 0)


def row(*cells):
    """Build a registry row in the real 7-cell shape: '' | id | dep | repl | removal | status | ''."""
    return {"cells": ["", *cells, ""]}


def test_overdue_open_row_fails():
    r = row("**DEP-X-001**: thing", "v3.26.0", "replacement",
            "**v3.28.0** (2-minor grace)", "**Active — grace window open**")
    state, detail = cdr.classify(r, CUR)
    assert state == "FAIL", detail
    assert "v3.28.0" in detail and "v3.30.0" in detail


def test_row_still_in_grace_passes():
    r = row("**DEP-X-002**: thing", "v3.29.0", "replacement",
            "**v3.31.0** (grace)", "**Active — grace window open**")
    assert cdr.classify(r, CUR)[0] == "PASS"


def test_removed_row_passes():
    r = row("**DEP-X-003**: thing", "v3.15.0", "replacement",
            "v3.15.0 (immediate)", "**Removed in v3.15.0**")
    assert cdr.classify(r, CUR)[0] == "PASS"


def test_retired_counts_as_terminal():
    """The regression that shipped: status 'Retired in v3.18.0' with removal v3.20.0
    already past. A `removed`-only predicate reports this discharged row as overdue."""
    r = row("**DEP-X-004**: thing", "v3.18.0", "replacement",
            "v3.20.0 (2-minor grace)", "**Retired in v3.18.0** (T1.12 Gate 2)")
    state, detail = cdr.classify(r, CUR)
    assert state == "PASS", f"'Retired' must discharge the row, got {state}: {detail}"


def test_grace_prose_in_removal_cell_does_not_discharge_the_row():
    """The removal cell legitimately contains the word 'removed' inside its grace
    narration ('marked v3.26 -> carried v3.27 -> removed v3.28'). Testing the whole row
    for terminal vocabulary would discharge the one genuinely overdue entry."""
    r = row("**DEP-X-005**: thing", "v3.26.0", "replacement",
            "**v3.28.0** (marked v3.26 → carried v3.27 → removed v3.28)",
            "**Active — grace window open**")
    assert cdr.classify(r, CUR)[0] == "FAIL"


def test_short_row_is_unavailable_not_pass():
    """A malformed row must never read as clean (gh#2045 zero-denominator family)."""
    assert cdr.classify({"cells": ["", "**DEP-X-006**: thing", "v3.26.0"]}, CUR)[0] == "UNAVAILABLE"


def test_live_registry_parses_and_reports_a_denominator():
    """The real registry must yield rows; a parser that silently matches nothing would
    report 'no overdue deprecations' over an empty set.

    Portability: a consumer repo need not carry this seat's deprecation policy, so an
    ABSENT registry skips. A registry that is PRESENT but unparseable still fails --
    that is the defect this test exists for.
    """
    if not cdr.REGISTRY.exists():
        pytest.skip(f"live-corpus test: no registry at {cdr.REGISTRY}; nothing to assert")
    live = cdr.rows()
    assert live is not None, "registry present but parser matched nothing"
    assert len(live) >= 3, f"parsed only {len(live)} rows — predicate likely drifted from the table format"


@pytest.mark.parametrize("verb", ["Removed", "Retired", "Withdrawn"])
def test_terminal_vocabulary_is_closed_over_the_verbs_the_registry_uses(verb):
    assert cdr.TERMINAL.search(f"**{verb} in v3.18.0**")
