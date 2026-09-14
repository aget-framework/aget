"""C-34-24 — host-layout conformance, conforming AND defective layouts.

The third outcome carries the requirement. CAP-HFL-006 says an ungoverned region's disorder
is NOT a violation, so OUTSIDE-CONTRACT must never be counted as DRIFT and must never fail the
run. Tests below fail if that distinction collapses in either direction.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "chlc", REPO / "scripts" / "check_host_layout_conformance.py")
chlc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chlc)

DRIFT, MISSING, OUTSIDE, OK = chlc.DRIFT, chlc.MISSING, chlc.OUTSIDE, chlc.OK


def write(root: Path, rel: str, text: str = "x"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def manifest(tmp: Path, paths: list[dict]) -> Path:
    p = tmp / "layout_manifest.json"
    p.write_text(json.dumps({"paths": paths}))
    return p


def outcomes(res, prefix):
    return {f["subject"]: f["outcome"] for f in res["findings"] if f["subject"].startswith(prefix)}


# --- conforming layout ------------------------------------------------------------

def test_a_conforming_layout_passes(tmp_path):
    root = tmp_path / "repo"
    write(root, "data/node1/config/app.toml")
    m = manifest(tmp_path, [{"pattern": "data/node1/config/*.toml", "class": "config",
                             "tier": "record"}])
    res = chlc.assess(m, root, None, ["/github/"])
    assert outcomes(res, "manifest:")["manifest:data/node1/config/*.toml"] == OK
    # no roster supplied -> MISSING, so overall is MISSING and exit 2, never 0
    assert chlc.exit_code(res) == 2


def test_a_fully_conforming_layout_with_roster_exits_zero(tmp_path):
    root = tmp_path / "repo"
    write(root, "data/node1/config/app.toml")
    m = manifest(tmp_path, [{"pattern": "data/node1/config/*.toml", "class": "config",
                             "tier": "record"}])
    r = tmp_path / "roster.json"
    r.write_text(json.dumps({"daemons": [{"name": "beat", "exec_path": "/Users/username/.local/bin/beat"}]}))
    res = chlc.assess(m, root, r, ["/github/"])
    assert res["overall"] == OK and chlc.exit_code(res) == 0


# --- CAP-HFL-006: the outcome this row exists for ---------------------------------

def test_an_ungoverned_region_is_OUTSIDE_CONTRACT_not_DRIFT(tmp_path):
    """CAP-HFL-006: 'IF a region has no governing layout rule, THEN the SYSTEM shall NOT
    grade its disorder as a violation (absence != drift).'"""
    root = tmp_path / "repo"
    write(root, "data/node1/config/app.toml")
    write(root, "scratch/whatever.tmp")          # governed by nothing
    write(root, "scratch/deeply/nested/mess.txt")
    m = manifest(tmp_path, [{"pattern": "data/node1/config/*.toml", "class": "config",
                             "tier": "record"}])
    res = chlc.assess(m, root, None, ["/github/"])
    ungoverned = outcomes(res, "observed:")
    assert set(ungoverned.values()) == {OUTSIDE}
    assert res["counts"][DRIFT] == 0, "ungoverned disorder must not be graded as drift"


def test_outside_contract_alone_never_fails_the_run(tmp_path):
    root = tmp_path / "repo"
    write(root, "data/node1/config/app.toml")
    for i in range(5):
        write(root, f"junk/f{i}.tmp")
    m = manifest(tmp_path, [{"pattern": "data/node1/config/*.toml", "class": "config",
                             "tier": "record"}])
    r = tmp_path / "roster.json"
    r.write_text(json.dumps({"daemons": []}))
    res = chlc.assess(m, root, r, ["/github/"])
    assert res["counts"][OUTSIDE] == 5
    assert chlc.exit_code(res) == 0, "an ungoverned region must not fail conformance"


# --- defective layouts ------------------------------------------------------------

def test_an_unknown_lifecycle_class_is_DRIFT(tmp_path):
    root = tmp_path / "repo"
    m = manifest(tmp_path, [{"pattern": "x/*.txt", "class": "not-a-class", "tier": "record"}])
    res = chlc.assess(m, root, None, ["/github/"])
    assert outcomes(res, "manifest:")["manifest:x/*.txt"] == DRIFT


def test_an_invalid_tier_is_DRIFT(tmp_path):
    root = tmp_path / "repo"
    m = manifest(tmp_path, [{"pattern": "x/*.txt", "class": "data", "tier": "durable"}])
    res = chlc.assess(m, root, None, ["/github/"])
    assert outcomes(res, "manifest:")["manifest:x/*.txt"] == DRIFT


def test_a_declared_path_with_no_artifact_is_MISSING_not_DRIFT(tmp_path):
    """A rule exists but nothing was observed. Conformance is unknown, not violated."""
    root = tmp_path / "repo"
    root.mkdir()
    m = manifest(tmp_path, [{"pattern": "data/node1/*.json", "class": "data", "tier": "record"}])
    res = chlc.assess(m, root, None, ["/github/"])
    assert outcomes(res, "manifest:")["manifest:data/node1/*.json"] == MISSING


def test_a_host_anchored_path_is_MISSING_from_a_repo_root(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    m = manifest(tmp_path, [{"pattern": "~/aof/state/heartbeat.jsonl", "class": "state",
                             "tier": "exhaust"}])
    res = chlc.assess(m, root, None, ["/github/"])
    f = [x for x in res["findings"] if x["subject"].startswith("manifest:~")][0]
    assert f["outcome"] == MISSING and "not observable" in f["why"]


# --- CAP-HFL-007 roster ------------------------------------------------------------

def test_a_daemon_running_from_a_repo_checkout_is_DRIFT(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    m = manifest(tmp_path, [{"pattern": "x/*.txt", "class": "data", "tier": "record"}])
    r = tmp_path / "roster.json"
    r.write_text(json.dumps({"daemons": [
        {"name": "from-repo", "exec_path": "/Users/username/github/some-aget/scripts/d.py"},
        {"name": "deployed", "exec_path": "/Users/username/.local/bin/d"},
    ]}))
    res = chlc.assess(m, root, r, ["/github/"])
    o = outcomes(res, "daemon:")
    assert o["daemon:from-repo"] == DRIFT
    assert o["daemon:deployed"] == OK


def test_an_absent_roster_is_MISSING_not_conformant(tmp_path):
    """Absence of a roster is not evidence that no daemon runs from a repo."""
    root = tmp_path / "repo"
    root.mkdir()
    m = manifest(tmp_path, [{"pattern": "x/*.txt", "class": "data", "tier": "record"}])
    res = chlc.assess(m, root, None, ["/github/"])
    f = [x for x in res["findings"] if x["subject"] == "roster"][0]
    assert f["outcome"] == MISSING and "not evidence of conformance" in f["why"]


# --- CAP-HFL-005 envelope / per-row predicate --------------------------------------

def test_rows_missing_the_record_predicate_field_are_DRIFT(tmp_path):
    root = tmp_path / "repo"
    write(root, "logs/audit.jsonl",
          '{"envelope_disposition": "acted"}\n{"other": 1}\n')
    m = manifest(tmp_path, [{"pattern": "logs/*.jsonl", "class": "logs", "tier": "record",
                             "record_predicate": {"field": "envelope_disposition"}}])
    res = chlc.assess(m, root, None, ["/github/"])
    f = [x for x in res["findings"] if x["subject"].startswith("envelope:")][0]
    assert f["outcome"] == DRIFT and "undecidable" in f["why"]


def test_a_well_formed_envelope_is_conformant(tmp_path):
    root = tmp_path / "repo"
    write(root, "logs/audit.jsonl",
          '{"envelope_disposition": "acted"}\n{"envelope_disposition": "n/a (no action)"}\n')
    m = manifest(tmp_path, [{"pattern": "logs/*.jsonl", "class": "logs", "tier": "record",
                             "record_predicate": {"field": "envelope_disposition"}}])
    res = chlc.assess(m, root, None, ["/github/"])
    f = [x for x in res["findings"] if x["subject"].startswith("envelope:")][0]
    assert f["outcome"] == OK and f["rows"] == 2


# --- input hygiene ------------------------------------------------------------------

@pytest.mark.parametrize("value", [[], None, 1, "layout"])
def test_json_non_mapping_is_controlled_unavailable(tmp_path, capsys, value):
    source = tmp_path / "layout.json"
    source.write_text(json.dumps(value))
    assert chlc.main(["--manifest", str(source), "--root", str(tmp_path), "--json"]) == 3
    assert "UNAVAILABLE" in capsys.readouterr().err


@pytest.mark.parametrize("cls,tier", [("cache", "exhaust"), ("data", "exhaust"),
                                     ("config", "record"), ("runtime", "exhaust"),
                                     ("state", "exhaust"), ("logs", "exhaust")])
def test_observed_artifact_must_match_class_location(tmp_path, cls, tier):
    root = tmp_path / "repo"
    write(root, "data/node/object.json")
    control = [{"pattern": "data/node/object.json", "class": "data", "tier": "record"}]
    assert chlc.check_manifest(control, root)[0]["outcome"] == OK
    misplaced = [{"pattern": "data/node/object.json", "class": cls, "tier": tier}]
    result = chlc.check_manifest(misplaced, root)[0]
    assert result["outcome"] == DRIFT
    assert result["misplaced"] == ["data/node/object.json"]


def test_record_telemetry_summary_uses_record_location(tmp_path):
    write(tmp_path, "data/node/digest.json")
    rules = [{"pattern": "data/node/digest.json", "class": "telemetry", "tier": "record"}]
    assert chlc.check_manifest(rules, tmp_path)[0]["outcome"] == OK

def test_an_unparseable_manifest_is_an_input_error_never_a_pass(tmp_path):
    bad = tmp_path / "m.json"
    bad.write_text("{[not valid")
    with pytest.raises(chlc.InputError):
        chlc.assess(bad, tmp_path, None, ["/github/"])


def test_a_manifest_without_paths_is_rejected(tmp_path):
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"nope": []}))
    with pytest.raises(chlc.InputError):
        chlc.assess(m, tmp_path, None, ["/github/"])


def test_yaml_manifests_are_accepted(tmp_path):
    pytest.importorskip("yaml")
    root = tmp_path / "repo"
    write(root, "data/n/config/a.toml")
    m = tmp_path / "layout_manifest.yaml"
    m.write_text('paths:\n  - pattern: "data/n/config/*.toml"\n    class: config\n    tier: record\n')
    res = chlc.assess(m, root, None, ["/github/"])
    assert outcomes(res, "manifest:")["manifest:data/n/config/*.toml"] == OK
