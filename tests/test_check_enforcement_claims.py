"""Gate-2 falsifiers for the spec-enforcement truthfulness checker."""

import datetime as dt
import json
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import check_enforcement_claims as cec  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = ROOT
SCRIPT = ROOT / "scripts" / "check_enforcement_claims.py"
GOLD = ROOT / "tests" / "fixtures" / "enforcement_claims" / "gold_cases.json"


def _materialize(tmp_path: pathlib.Path, case: dict) -> pathlib.Path:
    specs = tmp_path / "specs"
    specs.mkdir(parents=True)
    (specs / "CASE.md").write_text(case["body"])
    for rel, body in case.get("files", {}).items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    return tmp_path


@pytest.mark.parametrize("case", json.loads(GOLD.read_text()), ids=lambda case: case["id"])
def test_vset13_labeled_gold_corpus(case, tmp_path):
    """Every supported form has an explicit identity and expected classification."""
    result = cec.scan(_materialize(tmp_path, case), r"specs/.*\.md$", today=dt.date(2026, 8, 17))
    assert [row["classification"] for row in result["claims"]] == case["expected"]


def test_active_and_disclosed_polarities_have_different_consequences(tmp_path):
    root = tmp_path
    specs = root / "specs"
    specs.mkdir()
    (specs / "CASE.md").write_text(
        "## Enforcement\n\n"
        "| R1 | missing.py | Active |\n"
        "| R2 | future.py | Planned (build-or-remove: 2099-01-01) |\n"
    )
    result = cec.scan(root, r"specs/.*\.md$", today=dt.date(2026, 8, 17))
    by_name = {row["instrument"]: row for row in result["claims"]}
    assert by_name["missing.py"]["failing"] is True
    assert by_name["future.py"]["failing"] is False
    assert result["status"] == "FAIL"


def test_python_docstring_is_not_a_caller(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "CASE.md").write_text("## Enforcement\n\n| R | scripts/tool.py | Active |\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("# validator\n")
    (tmp_path / "narration.py").write_text('"""Run python3 scripts/tool.py in CI."""\n')
    result = cec.scan(tmp_path, r"specs/.*\.md$")
    assert result["claims"][0]["classification"] == "OVERCLAIM_UNCALLED"


def test_predicate_text_is_generated_from_live_regexes():
    text = cec.predicate_text()
    assert cec.ENFORCEMENT_HEADING.pattern in text
    assert cec.ACTIVE_CLAIM.pattern in text
    assert cec.DISCLOSED_GAP.pattern in text
    assert "exact declared path" in text
    assert "NOT a fleet claim" in text


@pytest.mark.skipif(not CANONICAL.exists(), reason="canonical tree not present")
def test_live_corpus_known_claim_identities_are_reached():
    """Known prior misses are identities, not an aggregate tolerance."""
    result = cec.scan(CANONICAL, r"specs/.*\.md$")
    identities = {
        (row["spec"], row["instrument"], row["source_kind"])
        for row in result["claims"]
    }
    expected = {
        ("specs/AGET_CONTENT_INTEGRITY_SPEC.md", "tests/test_version_enforcement.py", "markdown_field"),
        ("specs/AGET_RELEASE_SPEC.md", "scripts/validate_release_gate.py", "wired_declaration"),
        ("specs/AGET_PROJECT_PLAN_SPEC.md", "close_gate_check.py", "disclosed_declaration"),
    }
    assert expected <= identities, f"missing known claim identities: {sorted(expected - identities)}"
    assert not any(row["instrument"] == "scripts/goal_link_check.py" for row in result["claims"]), (
        "ACTIVE initiative prose outside an enforcement declaration became a false positive"
    )


def test_vset14_self_check_requires_an_operational_caller():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), "--self-check", "--json"],
        capture_output=True,
        text=True,
    )
    result = json.loads(proc.stdout)
    assert result["exists"]
    assert result["operational_callers"], "unit-test imports alone do not install the checker"
    assert result["status"] == "PASS"
