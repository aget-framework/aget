"""Arming checks for the surviving semantic mutation classes."""

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def source(path):
    return (REPO / path).read_text()


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_voice_containment_and_partial_read_guards_are_load_bearing(tmp_path):
    voice = load("check_voice_consumer_binding")
    root = tmp_path / "subject"
    root.mkdir()
    scaffold = root / "knowledge/voice/README.md"
    scaffold.parent.mkdir(parents=True)
    scaffold.write_text("Voice scaffold")
    consumer = root / "consumer.md"
    consumer.write_text("knowledge/voice/README.md Specification Evidence Bank Enforcement")
    control = voice.assess(root, [".", "."])
    assert control["ec2_satisfied"] is True
    assert control["counts"][voice.BOUND] == 1
    outside = tmp_path / "VOICE.md"
    outside.write_text("Outside subject")
    consumer.write_text("../VOICE.md Specification Evidence Bank Enforcement")
    escaped = voice.assess(root, [])
    assert escaped["overall"] == voice.DANGLING
    assert escaped["ec2_satisfied"] is False
    consumer.write_text("knowledge/voice/README.md Specification Evidence Bank Enforcement")
    incomplete = voice.assess(root, ["consumer.md", "missing"])
    assert incomplete["ec2_satisfied"] is None
    assert incomplete["overall"] == voice.UNAVAILABLE
    assert voice.exit_code(incomplete) == 3


def test_audit_gates_absence_limbs_and_supports_qualified_imports(tmp_path):
    audit = load("audit_instrument_verdict_contract")
    (tmp_path / "check_wired.py").write_text(
        "import warranted_verdict as w\ndef check(): return w.Verdict.yes(warrant='observed')\n"
    )
    control = audit.assess(tmp_path)
    assert control["instruments"][0]["checked_constructor_calls"] == 1
    (tmp_path / "check_unreadable.py").write_bytes(b"\xff\xfe")
    incomplete = audit.assess(tmp_path)
    assert incomplete["instruments"] is None
    assert incomplete["unwired_instruments"] is None
    assert audit.exit_code(incomplete) == 3


def test_runtime_partial_read_is_not_silent():
    s = source("scripts/check_runtime_support_evidence.py")
    assert '"fully_read": not failures' in s and "unsupported receipt entry type" in s


def test_forecast_checks_containment_and_permission():
    s = source("scripts/forecast_value_gate.py")
    assert "target.relative_to(root)" in s and "target.stat().st_mode & 0o400" in s
