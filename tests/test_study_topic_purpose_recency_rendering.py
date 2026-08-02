import importlib.util
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_SCRIPT = ROOT / "scripts" / "study_topic.py"
CANONICAL_SCRIPT = ROOT.parent / "aget" / "scripts" / "study_topic.py"
SCRIPT = Path(os.environ.get("AGET_STUDY_TOPIC_SCRIPT",
                             CANONICAL_SCRIPT if CANONICAL_SCRIPT.is_file() else LOCAL_SCRIPT))


def _run(root: Path, *args):
    env = {**os.environ, "AGET_STUDY_ROOT": str(root)}
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                          capture_output=True, env=env, timeout=30)


def _base(root: Path):
    (root / ".aget").mkdir(parents=True)
    (root / ".aget" / "config.json").write_text(json.dumps({
        "study_topic": {"priority_areas": {"pre-release": ["planning/**"]}}
    }))
    (root / "planning").mkdir()
    (root / "governance").mkdir()


def test_cli_purpose_changes_ranking(tmp_path):
    """R-TEST-001-02: purpose weighting changes CLI ranking."""
    _base(tmp_path)
    (tmp_path / "planning" / "PROJECT_PLAN_release.md").write_text("quasar release\n")
    (tmp_path / "governance" / "POLICY.md").write_text("quasar release\n")
    result = _run(tmp_path, "--topic", "quasar release", "--purpose", "pre-release",
                  "--no-floor", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    plan = payload["findings"]["project_plans"][0]
    policy = payload["findings"]["governance"][0]
    assert plan["purpose_boost"] == 2.0
    assert policy["purpose_boost"] == 1.0
    assert plan["score"] > policy["score"]


def test_session_recency_is_bounded_and_disclosed(tmp_path):
    """R-TEST-001-02: session recency is bounded and rendered."""
    _base(tmp_path)
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    (sessions / f"session_{date.today().isoformat()}_topic.md").write_text("quasar\n")
    (sessions / "session_2020-01-01_topic.md").write_text("quasar\n")
    result = _run(tmp_path, "--topic", "quasar", "--include-sessions",
                  "--session-days", "7", "--no-floor", "--json")
    payload = json.loads(result.stdout)
    assert len(payload["findings"]["sessions"]) == 1
    assert payload["search_contract"]["sessions"] == {
        "included": True, "recency_days": 7,
        "date_basis": "filename date; undated files included"
    }


def test_instrument_surface_is_opt_in_and_human_rendered(tmp_path):
    """R-TEST-001-02: executable instruments are opt-in and rendered."""
    _base(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "quasar_check.py").write_text("# quasar\n")
    default = json.loads(_run(tmp_path, "--topic", "quasar", "--no-floor", "--json").stdout)
    assert "instruments" not in default["findings"]
    rendered = _run(tmp_path, "--topic", "quasar", "--include-instruments", "--no-floor")
    assert rendered.returncode == 0
    assert "### Related Instruments" in rendered.stdout
    assert "quasar_check.py" in rendered.stdout


def test_omission_banner_bounds_repo_internal_scope(tmp_path):
    """R-TEST-001-02: external omissions bound the internal search."""
    _base(tmp_path)
    payload = json.loads(_run(tmp_path, "--topic", "quasar", "--json").stdout)
    excluded = payload["search_contract"]["surfaces_out_of_universe"]
    assert "WORK REPO" in excluded
    assert "WEB / external prior art" in excluded
