"""V-tests for scripts/validate_spec_binding.py — spec→ontology binding validator (C-22-14)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / "scripts" / "validate_spec_binding.py"

_spec = importlib.util.spec_from_file_location("validate_spec_binding", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_self_test_passes():
    r = subprocess.run([sys.executable, str(_SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_resolved_ref_not_phantom(tmp_path):
    names = {"NormativeConceptBinding"}
    f = tmp_path / "S.md"
    f.write_text("aget:concept/NormativeConceptBinding\n")
    r = _mod.scan_spec(f, names)
    assert r["bound"] is True
    assert r["phantom_refs"] == []


def test_unresolved_ref_is_phantom(tmp_path):
    names = {"NormativeConceptBinding"}
    f = tmp_path / "S.md"
    f.write_text("aget:concept/MadeUpConcept42\n")
    r = _mod.scan_spec(f, names)
    assert "MadeUpConcept42" in r["phantom_refs"]


def test_unbound_spec_zero_refs(tmp_path):
    f = tmp_path / "S.md"
    f.write_text("No bindings here at all.\n")
    r = _mod.scan_spec(f, set())
    assert r["bound"] is False
    assert r["ref_count"] == 0
