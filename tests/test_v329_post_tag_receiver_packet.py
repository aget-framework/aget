import re
from pathlib import Path

import pytest

from scripts.check_agents_instruction_reach import REQUIRED_ROOT_MARKERS, check_repo


ROOT = Path(__file__).resolve().parents[1]
POSITION = ROOT / "docs" / "POSITION_agents_instruction_reach_and_self_amendment.md"
CORRECTIONS = ROOT / "handoffs" / "CORRECTIONS_v3.29.0.md"


def _write_candidate(tmp_path: Path, position_text: str) -> None:
    (tmp_path / "AGENTS.md").write_text("# Minimal governed root\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / POSITION.name).write_text(position_text, encoding="utf-8")


def test_position_candidate_is_marker_sufficient_for_the_canonical_checker(tmp_path: Path):
    """R-TEST-001-02: the correction satisfies all four textual marker predicates."""
    _write_candidate(tmp_path, POSITION.read_text(encoding="utf-8"))
    result = check_repo(tmp_path)
    assert result["state"] == "PASS"
    assert result["markers"] == {name: True for name in REQUIRED_ROOT_MARKERS}


@pytest.mark.parametrize(
    ("marker", "phrases"),
    [
        ("session_or_client_bootstrap", ("## Session Protocol", "Wake Up Protocol")),
        ("write_boundary", ("## Write Scope", "read-only", "scoped write permissions")),
        (
            "gate_discipline",
            ("## Gate Execution Discipline", "Gate without plan update", "Structural Skill Routing"),
        ),
        (
            "self_amendment_control",
            ("`AGENTS.md` is the governance instruction surface itself.",),
        ),
    ],
)
def test_each_position_marker_is_independently_load_bearing(
    tmp_path: Path, marker: str, phrases: tuple[str, ...]
):
    """R-TEST-001-02: removing one named control fails that control rather than a generic check."""
    text = POSITION.read_text(encoding="utf-8")
    for phrase in phrases:
        text = text.replace(phrase, "")
    _write_candidate(tmp_path, text)
    result = check_repo(tmp_path)
    assert result["state"] == "FAIL"
    assert result["markers"][marker] is False
    assert f"missing root marker: {marker}" in result["errors"]


def test_correction_record_keeps_textual_acceptance_separate_from_delivery():
    """R-REL-019: a public regex fix must not read as received or behavioral evidence."""
    text = CORRECTIONS.read_text(encoding="utf-8")
    assert "adds the file and exact hash" in text
    assert re.search(r"Regex acceptance is not received-state", text, re.I)
