"""Operational-caller guards for canonical spec-enforcement truthfulness."""

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "canonical_health_check", ROOT / "scripts" / "health_check.py"
)
health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(health)


def _applicable_root(tmp_path: Path) -> Path:
    (tmp_path / "specs").mkdir()
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "check_enforcement_claims.py").write_text("# test marker\n")
    return tmp_path


def test_absent_corpus_is_an_explicit_not_applicable_pass(tmp_path):
    result = health.check_spec_enforcement_truthfulness(tmp_path)
    assert result.passed is True
    assert result.severity == "info"
    assert "not applicable" in result.message


def test_failing_corpus_is_warning_only(monkeypatch, tmp_path):
    root = _applicable_root(tmp_path)
    fake = types.SimpleNamespace(scan=lambda path, spec_glob: {
        "status": "FAIL",
        "specs_scanned": 66,
        "claims_checked": 178,
        "findings": [{}] * 165,
    })
    monkeypatch.setitem(sys.modules, "check_enforcement_claims", fake)

    result = health.check_spec_enforcement_truthfulness(root)
    assert result.passed is False
    assert result.severity == "warning"
    assert "165 finding(s)" in result.message


def test_clean_corpus_passes(monkeypatch, tmp_path):
    root = _applicable_root(tmp_path)
    fake = types.SimpleNamespace(scan=lambda path, spec_glob: {
        "status": "PASS",
        "specs_scanned": 1,
        "claims_checked": 1,
        "findings": [],
    })
    monkeypatch.setitem(sys.modules, "check_enforcement_claims", fake)

    result = health.check_spec_enforcement_truthfulness(root)
    assert result.passed is True
    assert result.severity == "info"
    assert "PASS" in result.message
