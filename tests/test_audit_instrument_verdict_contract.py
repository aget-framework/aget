from __future__ import annotations

import importlib.util
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "aivc", REPO / "scripts/audit_instrument_verdict_contract.py"
)
aivc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aivc)

WIRED = "from warranted_verdict import Verdict\ndef f(): return Verdict.yes(warrant='observed')\n"


def test_complete_population_reports_positive_and_negative(tmp_path):
    (tmp_path / "check_wired.py").write_text(WIRED)
    (tmp_path / "check_bare.py").write_text("def f(): return {'verdict':'YES'}\n")
    r = aivc.assess(tmp_path)
    assert r["fully_read"] and r["overall"] == "UNAVAILABLE"
    assert r["unwired_instruments"] == ["check_bare.py"]
    assert any(x["uses_checked_constructor"] for x in r["instruments"])


def test_comments_do_not_determine_population_or_certify_behavior(tmp_path):
    path = tmp_path / "check_state.py"
    path.write_text("def check(): return {'state': 'READY'}\n")
    before = aivc.assess(tmp_path)
    assert before["instruments"][0]["candidate_emission_sites"]
    path.write_text("# verdict\n" + path.read_text())
    after = aivc.assess(tmp_path)
    assert len(before["instruments"]) == len(after["instruments"]) == 1
    assert before["conformance"] == after["conformance"] == "UNMEASURED"
    assert before["classification"]["definite"] is False


def test_checked_call_does_not_certify_an_unchecked_path(tmp_path):
    (tmp_path / "check_mixed.py").write_text(
        WIRED + "def unchecked(): return {'state': 'READY'}\n"
    )
    result = aivc.assess(tmp_path)
    row = result["instruments"][0]
    assert row["checked_constructor_calls"] == 1
    assert len(row["candidate_emission_sites"]) == 2
    assert row["conformance"] == "UNMEASURED"
    assert aivc.exit_code(result) == 3


def test_permission_limit_gates_absence_counts_and_exit(tmp_path):
    (tmp_path / "check_good.py").write_text(WIRED)
    d = tmp_path / "hidden"
    d.mkdir()
    (d / "check_bad.py").write_text("x=1")
    d.chmod(0o400)
    try:
        r = aivc.assess(tmp_path)
        assert not r["fully_read"] and r["overall"] == "UNAVAILABLE"
        assert r["instruments"] is None and r["unwired_instruments"] is None
        assert str(tmp_path) in r["limit"] and aivc.exit_code(r) == 3
    finally:
        d.chmod(0o700)


def test_utf16_instrument_and_fifo_are_accounted_for(tmp_path):
    (tmp_path / "check_utf.py").write_bytes(WIRED.encode("utf-16"))
    fifo = tmp_path / "check_pipe.py"
    os.mkfifo(fifo)
    r = aivc.assess(tmp_path)
    assert not r["fully_read"]
    assert "utf" in r["limit"] and "unsupported" in r["limit"]


def test_symlink_entries_are_limits_and_terminate(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "check_ok.py").write_text(WIRED)
    (d / "loop").symlink_to(tmp_path, target_is_directory=True)
    (tmp_path / "check_link.py").symlink_to(d / "check_ok.py")
    r = aivc.assess(tmp_path)
    assert not r["fully_read"] and aivc.exit_code(r) == 3


def test_import_forms_are_recognised(tmp_path):
    (tmp_path / "check_a.py").write_text(
        "import warranted_verdict as w\ndef f(): return w.Verdict.no(warrant='observed')\n"
    )
    r = aivc.assess(tmp_path)
    assert r["instruments"][0]["uses_checked_constructor"]
