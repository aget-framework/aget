from pathlib import Path

from scripts.validate_codex_skill_discovery import REQUIRED, validate


def _skill(root: Path, name: str, text: str = "# skill\n"):
    path = root / ".agents" / "skills" / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(text)


def test_native_bundle_and_recovery_pass(tmp_path):
    """R-TEST-001-02: native bundle includes a recovery contract."""
    for name in REQUIRED:
        _skill(tmp_path, name, "# skill\ncheckpoint and resume recovery\n")
    result = validate(tmp_path)
    assert result["state"] == "PASS"
    assert result["recovery"] is True


def test_explicit_source_fallback_is_not_native(tmp_path):
    """R-TEST-001-02: explicit fallback is not native discovery."""
    for name in REQUIRED:
        path = tmp_path / ".claude" / "skills" / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text("recovery")
    result = validate(tmp_path)
    assert result["state"] == "FAIL"
    assert len(result["errors"]) == len(REQUIRED)


def test_missing_recovery_contract_fails(tmp_path):
    """R-TEST-001-02: native exposure without recovery fails."""
    for name in REQUIRED:
        _skill(tmp_path, name, "# skill\n")
    result = validate(tmp_path)
    assert result["state"] == "FAIL"
    assert "aget-save-state lacks recovery/resume contract" in result["errors"]
