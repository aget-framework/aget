"""Falsifying tests for gh#2223 — close_gate_check.py returned exit 0 on a plan
carrying unchecked closure boxes and non-terminal gate rows.

Re-derived at source 2026-08-13 rather than imported: the AOF-1 session's repair
candidate `c36c204f89b889211595368df73ce44ea6e51611` is not reachable in this
repository (`git cat-file` -> no such object), so the defect was reproduced from a
fresh fixture and each blind spot isolated with a matched control.

Every test asserts BOTH polarities. A guard that blocks everything is as useless as
one that blocks nothing, and the original defect survived precisely because the
literal forms fired while their realistic variants did not -- so a test that only
checks the failing side would have passed against the broken guard too.

Blind spots closed:
  1. closure-section heading literalism  ("## Closure" vs "## Closure Checklist")
  2. gate status read only from the bold prose form, never from a table row
  3. V-test row required the literal token PENDING and a first cell beginning "Gate"
  4. status carried as a checkbox CELL `| [ ] |` -- the form this fleet's plans
     actually use, found only by running the rule against the real corpus
"""
import importlib.util
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_GUARD = _REPO / "scripts" / "close_gate_check.py"


def _load():
    spec = importlib.util.spec_from_file_location("close_gate_check", _GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cgc = _load()


def _rows(text):
    return cgc.scan_status_table_rows(text)


def _closure(text):
    return [v for v in cgc.scan(text) if v[0] == "unchecked_closure_item"]


# --- Blind spot 1: closure-section heading literalism -------------------------

@pytest.mark.parametrize("heading", [
    "Closure", "Finalization", "Exit Conditions", "Exit Criteria",
    "Completion Checklist", "Gate Closure", "Closure Checklist",
])
def test_closure_alias_headings_are_read(heading):
    text = f"# P\n\n## {heading}\n\n- [ ] residents accepted\n"
    assert _closure(text), f"unchecked box under '## {heading}' went unread"


def test_non_closure_heading_is_not_read():
    """Control: the widening must not make every unchecked box a closure signal."""
    text = "# P\n\n## Open Questions\n\n- [ ] should we rename the wave\n"
    assert not _closure(text), "unchecked box under an unrelated heading was read as closure"


# --- Blind spots 2+3: gate/V-test status tables ------------------------------

_HDR = "| Gate | Deliverable | Status |\n|---|---|---|\n"
_VHDR = "| V-test | Deliverable | Status |\n|---|---|---|\n"


@pytest.mark.parametrize("status", [
    "PENDING", "In Progress", "Open", "Incomplete", "Blocked",
    "TODO", "Deferred", "Partial", "STOPPED", "UNMET", "FAILED", "⏳",
])
def test_nonterminal_table_status_blocks(status):
    assert _rows(f"# P\n\n{_HDR}| G1 | dispatch | {status} |\n"), \
        f"non-terminal status {status!r} in a gate table went unread"


@pytest.mark.parametrize("status", [
    "COMPLETE", "ACCEPTED", "DONE", "PASS", "CLOSED", "✅", "N/A", "WAIVED",
])
def test_terminal_table_status_passes(status):
    assert not _rows(f"# P\n\n{_HDR}| G1 | dispatch | {status} |\n"), \
        f"terminal status {status!r} was wrongly flagged"


def test_vtest_keyed_row_is_read_not_only_gate_keyed():
    """Blind spot 3b: the old pattern required the first cell to begin 'Gate'."""
    assert _rows(f"# P\n\n{_VHDR}| V3R.1 | refresh | PENDING |\n"), \
        "V-test-keyed row went unread because its first cell was not 'Gate ...'"


def test_table_without_status_header_is_not_scanned():
    """Control: bounds the rule to genuine status tables, not every matrix."""
    text = "# P\n\n| Term | Definition |\n|---|---|\n| Open | not yet closed |\n"
    assert not _rows(text), "a glossary table was scanned as a gate status table"


# --- Blind spot 4: checkbox status CELLS -------------------------------------

def test_unchecked_status_cell_blocks():
    text = "# P\n\n| # | Deliverable | Status |\n|---:|---|---|\n| -1.1 | verify specs | [ ] |\n"
    assert _rows(text), "unchecked `[ ]` status cell went unread (the real-corpus form)"


def test_checked_status_cell_passes():
    text = "# P\n\n| # | Deliverable | Status |\n|---:|---|---|\n| -1.1 | verify specs | [x] |\n"
    assert not _rows(text), "checked `[x]` status cell was wrongly flagged"


# --- The gh#2223 scenario end to end -----------------------------------------

_FIXTURE = """# PROJECT_PLAN: Remote Fleet v3.30 Migration

**Plan_Status**: COMPLETE

| Gate | Deliverable | Status | V-test |
|---|---|---|---|
| G1 | Preflight | In Progress | V1 |
| G2 | Dispatch wave | Blocked | V2 |
| G3 | Collect receipts | ⏳ | V3 |
| G4 | Reconcile | Open | V4 |
| G5 | Close | Incomplete | V5 |

## Closure

- [ ] All residents accepted
- [ ] Receipts immutable
- [ ] Live parity verified
- [ ] CI disposition recorded
- [ ] Retrospective written
- [ ] Successor handoff created
"""


def test_gh2223_scenario_blocks_with_all_eleven_signals():
    """The issue's exact shape: 6 unchecked closure boxes + 5 unchecked gate rows."""
    assert len(_closure(_FIXTURE)) == 6
    assert len(_rows(_FIXTURE)) == 5


def test_clean_plan_of_the_same_shape_still_passes():
    """Control: the same plan, genuinely finished, must not block."""
    clean = (_FIXTURE
             .replace("In Progress", "COMPLETE").replace("Blocked", "ACCEPTED")
             .replace("⏳", "PASS").replace("Open", "COMPLETE")
             .replace("Incomplete", "COMPLETE").replace("- [ ]", "- [x]"))
    assert not _closure(clean)
    assert not _rows(clean)


# --- Corpus polarity: the rule must be live on real plans, not merely quiet ---

def _plans():
    return sorted((_REPO / "planning").glob("PROJECT_PLAN*.md"))


_TERMINAL = re.compile(
    r"^\*\*Plan_Status\*\*:\s*(COMPLETE|CLOSED|ABANDONED|SUPERSEDED)", re.M | re.I)


@pytest.mark.skipif(not (_REPO / "planning").is_dir(), reason="no planning/ corpus")
def test_rule_fires_on_real_nonterminal_plans():
    """A rule that never fires on real data is inert, however green its fixtures.

    Measured 2026-08-13: 13 of 53 non-terminal plans. The first draft of this rule
    scored 0 here -- the fixtures passed and the rule was useless, which is what
    sent the derivation back to the corpus and produced blind spot 4.
    """
    live = sum(1 for p in _plans()
               if not _TERMINAL.search(p.read_text(errors="replace"))
               and _rows(p.read_text(errors="replace")))
    assert live > 0, "rule is inert on the real non-terminal corpus"


@pytest.mark.skipif(not (_REPO / "planning").is_dir(), reason="no planning/ corpus")
def test_rule_is_silent_on_already_closed_plans():
    """Control on the same corpus: measured 0 of 22 terminal plans."""
    noisy = [p.name for p in _plans()
             if _TERMINAL.search(p.read_text(errors="replace"))
             and _rows(p.read_text(errors="replace"))]
    assert not noisy, f"false positives on closed plans: {noisy}"
