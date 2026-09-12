"""Arming checks for the surviving semantic mutation classes."""
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
def source(path):return (REPO/path).read_text()
def test_voice_containment_and_partial_read_guards_are_load_bearing():
 s=source("scripts/check_voice_consumer_binding.py")
 assert "relative_to(root)" in s and "ec2=(counts[BOUND]>0 and not counts[DANGLING]) if full else None" in s
 assert "files.setdefault" in s and "unsupported markdown entry type" in s
def test_audit_gates_absence_limbs_and_supports_qualified_imports():
 s=source("scripts/audit_instrument_verdict_contract.py")
 assert '"instruments":instruments if full else None' in s
 assert "qualified=" in s and "unwired_instruments" in s
def test_runtime_partial_read_is_not_silent():
 s=source("scripts/check_runtime_support_evidence.py")
 assert '"fully_read": not failures' in s and "unsupported receipt entry type" in s
def test_forecast_checks_containment_and_permission():
 s=source("scripts/forecast_value_gate.py")
 assert "target.relative_to(root)" in s and "target.stat().st_mode & 0o400" in s
