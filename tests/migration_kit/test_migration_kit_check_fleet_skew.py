"""check_fleet_skew.py: both verdicts, the declared limit, the default stated, nested and unreadable members."""
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[2] / "scripts" / "migration_kit"
spec = importlib.util.spec_from_file_location("t_check_fleet_skew", KIT / "check_fleet_skew.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}


def _framework(tmp, tags):
    fw = tmp / "framework"
    fw.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=fw, check=True, env=GIT_ENV)
    (fw / "f").write_text("x")
    subprocess.run(["git", "add", "f"], cwd=fw, check=True, env=GIT_ENV)
    subprocess.run(["git", "commit", "-qm", "c"], cwd=fw, check=True, env=GIT_ENV)
    for t in tags:
        subprocess.run(["git", "tag", t], cwd=fw, check=True, env=GIT_ENV)
    return fw


def _member(path, version):
    (path / ".aget").mkdir(parents=True, exist_ok=True)
    if version is not None:
        (path / ".aget" / "version.json").write_text(json.dumps({"aget_version": version}))
    return path


def _fleet(tmp, members, root=None):
    root = root or tmp / "supervisor"
    (root / ".aget" / "fleet").mkdir(parents=True, exist_ok=True)
    agents = [{"agent_name": n, "location": str(p), "status": st} for n, p, st in members]
    agents.append({"agent_name": "supervisor", "location": str(root), "status": "active"})
    reg = root / ".aget" / "fleet" / "FLEET_STATE.yaml"
    reg.write_text(yaml.safe_dump({"fleet": {"main": {"agents": agents}}}))
    return root, reg


TAGS = ["v1.1.0", "v1.2.0", "v1.3.0", "v1.4.0", "v1.5.0", "v1.5.1"]


@pytest.fixture
def fw(tmp_path):
    return _framework(tmp_path, TAGS)


def test_within_bound_and_flagged(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    b = _member(tmp_path / "b", "1.3.0")              # 2 behind 1.5 -> flagged, not blocked
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("b", b, "active")])
    rep = S.evaluate(reg, reference="1.5.1", framework=fw, root=root, env={})
    assert rep["verdict"] == "WITHIN-BOUND"
    assert rep["flagged"] == ["b"] and rep["floor"] == {"behind": 2, "names": ["b"]}
    assert rep["defaults_applied"] == ["skew.blocked_at", "skew.flagged_at"]


def test_blocked_names_every_floor_member(tmp_path, fw):
    a = _member(tmp_path / "a", "1.2.0")
    b = _member(tmp_path / "b", "1.2.3")
    c = _member(tmp_path / "c", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("b", b, "active"), ("c", c, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "BLOCKED" and rep["floor"] == {"behind": 3, "names": ["a", "b"]}


def test_declared_limit_overrides_default(tmp_path, fw):
    a = _member(tmp_path / "a", "1.2.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    (root / ".aget" / "adoption_policy.json").write_text(json.dumps({"skew": {"blocked_at": 4, "flagged_at": 3}}))
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "WITHIN-BOUND" and rep["limits"]["source"]["blocked_at"] == "file"
    assert rep["defaults_applied"] == []


def test_nested_member_reads_its_own_version(tmp_path, fw):
    parent = tmp_path / "shared"
    parent.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=parent, check=True, env=GIT_ENV)
    nested = _member(parent / "nested-aget", "1.5.0")
    (parent / ".aget").mkdir()
    (parent / ".aget" / "version.json").write_text(json.dumps({"aget_version": "1.1.0"}))   # the parent is older
    root, reg = _fleet(tmp_path, [("nested", nested, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["members"][0]["version"] == "1.5.0" and rep["verdict"] == "WITHIN-BOUND"


def test_unreadable_member_makes_within_unavailable(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    b = _member(tmp_path / "b", None)
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("b", b, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and rep["unreadable"] == ["b"]


def test_unreadable_member_does_not_hide_a_block(tmp_path, fw):
    a = _member(tmp_path / "a", "1.1.0")
    b = _member(tmp_path / "b", None)
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("b", b, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "BLOCKED"


def test_off_ladder_member_blocks(tmp_path, fw):
    a = _member(tmp_path / "a", "0.9.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "BLOCKED" and rep["floor"]["behind"] == "OFF-LADDER"


def test_inactive_members_are_listed_not_dropped(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    r = _member(tmp_path / "r", "1.1.0")
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("r", r, "retired")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "WITHIN-BOUND" and rep["excluded"] == [{"name": "r", "status": "retired"}]


def test_unpublished_reference_and_missing_register_are_unavailable(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    assert S.evaluate(reg, reference="1.9.0", framework=fw, root=root, env={})["verdict"] == "UNAVAILABLE"
    assert S.evaluate(tmp_path / "nope.yaml", reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "UNAVAILABLE"


def test_reference_defaults_to_the_migration_target(tmp_path):
    fw = _framework(tmp_path, ["v3.34.0", "v3.35.0"])
    a = _member(tmp_path / "a", "3.34.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    rep = S.evaluate(reg, framework=fw, root=root, env={})
    assert rep["reference_source"] == "migration target" and rep["reference"] == S.R.TO
    assert rep["verdict"] == "WITHIN-BOUND" and rep["floor"]["behind"] == 1


def test_malformed_register_entry_makes_within_unavailable(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    d = yaml.safe_load(reg.read_text())
    d["fleet"]["main"]["agents"].append({"agent_name": "no-location"})
    reg.write_text(yaml.safe_dump(d))
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and rep["malformed"]


def test_status_with_whitespace_is_still_active(tmp_path, fw):
    a = _member(tmp_path / "a", "1.1.0")
    root, reg = _fleet(tmp_path, [("a", a, " Active ")])
    assert S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "BLOCKED"


def test_member_ahead_is_listed_and_not_converged(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    b = _member(tmp_path / "b", "1.3.0")
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("b", b, "active")])
    rep = S.evaluate(reg, reference="1.3.0", framework=fw, root=root, env={})
    assert rep["ahead"] == ["a"] and rep["converged"] == 1


def test_relative_location_resolves_against_the_supervisor_root(tmp_path, fw, monkeypatch):
    root = tmp_path / "supervisor"
    _member(root / "members" / "a", "1.1.0")
    (root / ".aget" / "fleet").mkdir(parents=True)
    reg = root / ".aget" / "fleet" / "FLEET_STATE.yaml"
    reg.write_text(yaml.safe_dump({"fleet": {"main": {"agents": [
        {"agent_name": "a", "location": "members/a", "status": "active"}]}}}))
    monkeypatch.chdir(tmp_path)
    assert S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "BLOCKED"


def test_agents_as_a_mapping_are_read(tmp_path, fw):
    a = _member(tmp_path / "a", "1.1.0")
    root = tmp_path / "supervisor"
    (root / ".aget" / "fleet").mkdir(parents=True)
    reg = root / ".aget" / "fleet" / "FLEET_STATE.yaml"
    reg.write_text(yaml.safe_dump({"fleet": {"main": {"agents": {"a": {"location": str(a)}}}}}))
    assert S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "BLOCKED"


def test_register_without_fleet_section_is_unavailable(tmp_path, fw):
    root = tmp_path / "supervisor"
    (root / ".aget" / "fleet").mkdir(parents=True)
    reg = root / ".aget" / "fleet" / "FLEET_STATE.yaml"
    reg.write_text(yaml.safe_dump({"agents": []}))
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and "fleet" in rep["unavailable_reason"]


def test_supervisor_listed_by_name_under_another_path_is_skipped(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active"), ("sup", tmp_path / "elsewhere", "active")])
    (root / ".aget" / "version.json").write_text(json.dumps({"agent_name": "sup", "aget_version": "1.5.0"}))
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert "sup" in rep["skipped_self"] and rep["verdict"] == "WITHIN-BOUND"


def test_framework_without_tags_says_to_fetch_them(tmp_path):
    fw = _framework(tmp_path, [])
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and "fetch --tags" in rep["unavailable_reason"]


def test_malformed_portfolio_is_not_silently_dropped(tmp_path, fw):
    # Review finding 2: a portfolio written as a list must make the check unavailable, not hide a stale member.
    a = _member(tmp_path / "a", "1.5.0")
    stale = _member(tmp_path / "stale", "1.1.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    d = yaml.safe_load(reg.read_text())
    d["fleet"]["broken"] = [{"agent_name": "stale", "location": str(stale)}]
    reg.write_text(yaml.safe_dump(d))
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and rep["malformed"]


def test_portfolio_without_agents_is_allowed(tmp_path, fw):
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    d = yaml.safe_load(reg.read_text())
    d["fleet"]["archived"] = {"portfolio_id": "old", "status": "archived"}
    reg.write_text(yaml.safe_dump(d))
    assert S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "WITHIN-BOUND"


@pytest.mark.parametrize("bad", ["1.5.NOT_A_VERSION", "1.5", "1.5.0garbage", 150])
def test_malformed_member_version_is_unreadable(tmp_path, fw, bad):
    a = tmp_path / "a"
    (a / ".aget").mkdir(parents=True)
    (a / ".aget" / "version.json").write_text(json.dumps({"aget_version": bad}))
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and rep["unreadable"] == ["a"]


def test_unreadable_release_target_is_unavailable(tmp_path, fw, monkeypatch):
    # Review finding 8: a bad migration_target.json made the tool crash; it must give UNAVAILABLE.
    a = _member(tmp_path / "a", "1.5.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    monkeypatch.setattr(S, "R", None)
    monkeypatch.setattr(S, "R_ERROR", "release target unreadable (ValueError: bad)")
    rep = S.evaluate(reg, framework=fw, root=root, env={})
    assert rep["verdict"] == "UNAVAILABLE" and "release target" in rep["unavailable_reason"]
    assert S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})["verdict"] == "WITHIN-BOUND"


def test_member_on_an_unpublished_newer_minor_is_off_ladder(tmp_path, fw):
    a = _member(tmp_path / "a", "1.6.0")
    root, reg = _fleet(tmp_path, [("a", a, "active")])
    rep = S.evaluate(reg, reference="1.5.0", framework=fw, root=root, env={})
    assert rep["verdict"] == "BLOCKED" and rep["floor"]["behind"] == "OFF-LADDER"
