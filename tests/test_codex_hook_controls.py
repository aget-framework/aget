import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_cross_client_hook_controls import matrix

ROOT = Path(__file__).resolve().parents[1]
POC = ROOT / "poc" / "codex-hook-controls" / "codex_pretool_guard.py"


def _run(event):
    return subprocess.run([sys.executable, str(POC)], input=json.dumps(event), text=True,
                          capture_output=True, cwd=ROOT)


def test_supported_client_set_is_exact_and_green(tmp_path):
    """R-TEST-001-02: exact supported-client matrix passes all dimensions."""
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({
        "permissions": {"defaultMode": "default"},
        "hooks": {"PreToolUse": [{"hooks": [
            {"type": "command", "command": "python3 scripts/policy_enforcement.py"}
        ]}]},
    }))
    result = matrix(tmp_path)
    assert result["supported_clients"] == ["Claude Code", "Codex CLI"]
    assert result["state"] == "PASS"
    assert all(all(c["dimensions"].values()) for c in result["clients"])


def test_claude_applicability_does_not_depend_on_guard_filename(tmp_path):
    """H-29-012: registration structure, not the token 'guard', establishes applicability."""
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({
        "hooks": {"PreToolUse": [{"hooks": [
            {"type": "command", "command": "python3 scripts/permission_enforcement.py"}
        ]}]},
    }))
    claude = matrix(tmp_path)["clients"][0]
    assert claude["dimensions"]["applicability"] is True
    assert claude["state"] == "PASS"


def test_claude_applicability_rejects_keyword_only_non_command_entry(tmp_path):
    """H-29-012 falsifier: prose containing 'guard' is not an installed command hook."""
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({
        "hooks": {"PreToolUse": [{"hooks": [
            {"type": "prompt", "prompt": "Ask the guard before continuing"}
        ]}]},
    }))
    claude = matrix(tmp_path)["clients"][0]
    assert claude["dimensions"]["applicability"] is False
    assert claude["state"] == "FAIL"


def test_public_checkout_uses_sanitized_claude_fixture(tmp_path):
    """R-TEST-001-02: public checkout has portable Claude acceptance evidence."""
    result = matrix(tmp_path)
    claude = result["clients"][0]
    assert claude["state"] == "PASS"
    assert claude["evidence_kind"] == "sanitized-portable-fixture"


def test_codex_positive_block_and_no_side_effect(tmp_path):
    """R-TEST-001-02: denied Codex operation has no side effect."""
    sentinel = tmp_path / "untouched"
    sentinel.write_text("original")
    result = _run({"trusted": True, "command": f"write AGENTS.md then {sentinel}"})
    assert result.returncode == 2
    assert json.loads(result.stdout)["decision"] == "block"
    assert sentinel.read_text() == "original"


def test_codex_negative_control_allows_ordinary_operation():
    """R-TEST-001-02: ordinary Codex operation remains allowed."""
    result = _run({"trusted": True, "path": "docs/guide.md"})
    assert result.returncode == 0
    assert json.loads(result.stdout)["decision"] == "allow"


def test_codex_trust_boundary_is_not_overclaimed():
    """R-TEST-001-02: untrusted hook state is unavailable, not PASS."""
    result = _run({"trusted": False, "path": "AGENTS.md"})
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "decision": "unavailable", "reason": "project-untrusted-hooks-not-loaded"
    }


def test_individual_affirmation_is_precise_not_standing():
    """R-TEST-001-02: individual affirmation is precise."""
    result = _run({"trusted": True, "path": ".codex/config.toml", "affirmed": True})
    assert result.returncode == 0
    assert json.loads(result.stdout)["reason"] == "individually-affirmed"
