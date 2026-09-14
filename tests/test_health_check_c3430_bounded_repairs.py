"""C-34-30 / gh#2502 — three defects in canonical health_check.py.

D1 L-doc numeric IDs must normalize so L99 and L099 collide.
D2 the governance message must report a MEASURED enumeration, not a constant.
D3 the inert --fix flag must be REFUSED, and its stale guidance removed.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "health_check.py"
sys.path.insert(0, str(REPO / "scripts"))
import health_check as hc  # noqa: E402


def _agent(tmp_path, ldocs=(), gov=()):
    root = tmp_path / "agent"
    (root / ".aget" / "evolution").mkdir(parents=True)
    (root / "governance").mkdir(parents=True)
    for name in ldocs:
        (root / ".aget" / "evolution" / name).write_text("# x\n")
    for name in gov:
        (root / "governance" / name).write_text("# x\n")
    return root


# ------------------------------------------------------------------- D1 identity
def test_padded_and_unpadded_ids_collide(tmp_path):
    """THE DEFECT: L99 and L099 are the same L-doc and must report as duplicate."""
    root = _agent(tmp_path, ldocs=("L99_alpha.md", "L099_beta.md"))
    r = hc.check_duplicate_ldoc_ids(root)
    assert not r.passed, f"expected duplicate, got: {r.message}"
    assert "L99" in r.message


def test_genuinely_distinct_ids_do_not_collide(tmp_path):
    """Rejection case: normalization must not manufacture false duplicates."""
    root = _agent(tmp_path, ldocs=("L99_alpha.md", "L100_beta.md", "L0100_gamma.md"))
    r = hc.check_duplicate_ldoc_ids(root)
    # L100 and L0100 DO collide; L99 must not be dragged in with them
    assert "L99" not in r.message.replace("L990", "").replace("L991", "")


def test_same_literal_id_twice_still_detected(tmp_path):
    """Compatibility: what the old check caught, it must still catch."""
    root = _agent(tmp_path, ldocs=("L42_a.md", "L42_b.md"))
    r = hc.check_duplicate_ldoc_ids(root)
    assert not r.passed


def test_no_duplicates_passes(tmp_path):
    root = _agent(tmp_path, ldocs=("L1_a.md", "L2_b.md"))
    assert hc.check_duplicate_ldoc_ids(root).passed


# ---------------------------------------------------------------- D2 measurement
def test_governance_message_reports_a_measured_enumeration(tmp_path):
    root = _agent(tmp_path, gov=("CHARTER.md", "MISSION.md", "SCOPE_BOUNDARIES.md", "EXTRA.md"))
    r = hc.check_governance_directory(root)
    assert r.passed
    assert "enumerated" in r.message, r.message
    assert "4" in r.message, f"must count the 4 files actually present: {r.message}"


def test_governance_message_is_not_a_bare_constant(tmp_path):
    """The regression: '3 files present' printed regardless of what was there."""
    few = hc.check_governance_directory(
        _agent(tmp_path / "a", gov=("CHARTER.md", "MISSION.md", "SCOPE_BOUNDARIES.md")))
    many = hc.check_governance_directory(
        _agent(tmp_path / "b", gov=("CHARTER.md", "MISSION.md", "SCOPE_BOUNDARIES.md",
                                     "X.md", "Y.md")))
    assert few.message != many.message, "the message must vary with what is measured"


# --------------------------------------------------------------------- D3 --fix
def test_fix_flag_is_refused_with_nonzero_exit():
    r = subprocess.run([sys.executable, str(SCRIPT), "--fix"], capture_output=True, text=True)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "REFUSED" in (r.stdout + r.stderr)


def test_normal_run_is_unaffected_by_the_refusal():
    """Compatibility: the refusal must not break the ordinary path."""
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode != 2 or "REFUSED" not in (r.stdout + r.stderr)


def test_stale_run_with_fix_guidance_is_gone():
    src = SCRIPT.read_text()
    assert "(run with --fix)" not in src, "stale guidance points at a refused flag"
