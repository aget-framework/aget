"""V-tests for scripts/check_skill_coherence.py — release-time skill↔tree gate (#1614 / C-22-29)."""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / "scripts" / "check_skill_coherence.py"

_spec = importlib.util.spec_from_file_location("check_skill_coherence", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _check_with_roots(body, roots):
    saved = _mod.SEARCH_ROOTS
    _mod.SEARCH_ROOTS = roots
    try:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "SKILL.md"
            f.parent  # skill dir name = td basename
            f.write_text(body)
            return _mod.check_skill(f)
    finally:
        _mod.SEARCH_ROOTS = saved


def test_self_test_passes():
    r = subprocess.run([sys.executable, str(_SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_absent_governing_spec_flagged(tmp_path):
    body = "**Governing Spec**: AGET_NOPE_SPEC.md — canonical\n"
    r = _check_with_roots(body, [tmp_path])  # empty root → artifact absent
    assert any(m["artifact"] == "AGET_NOPE_SPEC.md" for m in r["missing_governing"])


def test_stale_future_for_shipped_spec_flagged(tmp_path):
    (tmp_path / "AGET_SHIPS_SPEC.md").write_text("x")
    body = "Implements SOP_x.md + future AGET_SHIPS_SPEC.\n"
    r = _check_with_roots(body, [tmp_path])
    assert any(s["artifact"] == "AGET_SHIPS_SPEC.md" for s in r["stale_future"])


def test_no_false_positive_on_trailing_future_modifier(tmp_path):
    """'SOP_x (...) + future AGET_Y' must flag Y, NOT the nearer-preceding SOP_x (#1605 class)."""
    (tmp_path / "AGET_Y_SPEC.md").write_text("x")
    (tmp_path / "SOP_x.md").write_text("x")
    body = "Implements SOP_x.md (graduated procedure) + future AGET_Y_SPEC.\n"
    r = _check_with_roots(body, [tmp_path])
    flagged = {s["artifact"] for s in r["stale_future"]}
    assert "AGET_Y_SPEC.md" in flagged
    assert "SOP_x.md" not in flagged, "trailing 'future' modifies Y, not SOP_x"


def test_coherent_skill_zero_defects(tmp_path):
    (tmp_path / "AGET_SHIPS_SPEC.md").write_text("x")
    body = "**Governing Spec**: AGET_SHIPS_SPEC.md — Active\n"
    r = _check_with_roots(body, [tmp_path])
    assert r["defects"] == 0
