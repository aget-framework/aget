"""V-tests for scripts/deploy_skill.py — governed surgical skill deployer (C-22-01)."""
import datetime
import importlib.util
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / "scripts" / "deploy_skill.py"
_spec = importlib.util.spec_from_file_location("deploy_skill", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _fleet(tmp_path):
    src = tmp_path / "template-worker-aget" / ".claude" / "skills" / "aget-release-build"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("x")
    (src / "helper.py").write_text("y")  # companion artifact
    tgt = tmp_path / "template-advisor-aget"
    (tgt / ".claude" / "skills").mkdir(parents=True)
    return tmp_path / "template-worker-aget" / ".claude" / "skills", tgt


def test_self_test_passes():
    r = subprocess.run([sys.executable, str(_SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_dry_run_never_writes(tmp_path):
    source, tgt = _fleet(tmp_path)
    r = _mod.deploy("aget-release-build", source, tgt, apply=False, today=datetime.date(2026, 6, 13))
    assert r["action"] == "DRY-RUN"
    assert not _mod.verify(tgt, "aget-release-build")


def test_weekday_apply_refused_l735(tmp_path):
    source, tgt = _fleet(tmp_path)
    r = _mod.deploy("aget-release-build", source, tgt, apply=True, today=datetime.date(2026, 6, 12))  # Friday
    assert r["action"] == "REFUSED"
    assert "L735" in r["reason"]
    assert not _mod.verify(tgt, "aget-release-build")


def test_weekend_apply_deploys_with_companions_and_verifies(tmp_path, monkeypatch):
    source, tgt = _fleet(tmp_path)
    monkeypatch.setattr(_mod, "AUDIT_LOG", tmp_path / "audit.jsonl")
    r = _mod.deploy("aget-release-build", source, tgt, apply=True, today=datetime.date(2026, 6, 13))  # Saturday
    assert r["action"] == "DEPLOYED" and r["verified"] is True
    assert _mod.verify(tgt, "aget-release-build")
    # companion artifact came along
    assert (tgt / ".claude" / "skills" / "aget-release-build" / "helper.py").exists()
    assert (tmp_path / "audit.jsonl").exists()


def test_gap_report_detects_missing(tmp_path):
    source, tgt = _fleet(tmp_path)  # advisor lacks the skill
    rep = _mod.gap_report(tmp_path, universal=["aget-release-build"])
    assert "aget-release-build" in rep["template-advisor-aget"]["missing"]
    assert rep["template-worker-aget"]["missing"] == []  # source has it
