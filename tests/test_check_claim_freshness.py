"""V-tests for scripts/check_claim_freshness.py — citation freshness gate (C-22-04)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / "scripts" / "check_claim_freshness.py"
_spec = importlib.util.spec_from_file_location("check_claim_freshness", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_self_test_passes():
    r = subprocess.run([sys.executable, str(_SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_extracts_only_real_issue_numbers():
    claims = list(_mod.extract_claims("#5 OPEN (too short)\n#1461 CLOSED yes\nfoo #1120 OPEN bar\n"))
    issues = {c[0] for c in claims}
    assert issues == {1461, 1120}  # #5 ignored (CLAIM_RE requires 3-5 digits)


def test_online_detects_state_drift(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("#1461 OPEN (stale)\n#1120 OPEN (fresh)\n")
    fake = {1461: "CLOSED", 1120: "OPEN"}
    claims, drifts = _mod.check([str(f)], online=True, state_fn=lambda i: fake.get(i))
    drifted = {d["issue"] for d in drifts}
    assert 1461 in drifted   # asserted OPEN, actually CLOSED
    assert 1120 not in drifted


def test_merged_equals_closed(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("#1626 MERGED\n")
    _, drifts = _mod.check([str(f)], online=True, state_fn=lambda i: "CLOSED")
    assert drifts == []  # MERGED assertion satisfied by actual CLOSED


def test_unresolvable_is_not_drift(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("#9999 OPEN\n")
    _, drifts = _mod.check([str(f)], online=True, state_fn=lambda i: None)  # gh unavailable
    assert drifts == []  # unchecked != drifted
