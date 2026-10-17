"""adoption_policy.py: the receiver declares its policy; defaults apply and say so when it declares nothing."""
import datetime as dt
import importlib.util
import json
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[2] / "scripts" / "migration_kit"
spec = importlib.util.spec_from_file_location("t_adoption_policy", KIT / "adoption_policy.py")
AP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AP)


def _write(root, cfg):
    (root / ".aget").mkdir(parents=True, exist_ok=True)
    (root / ".aget" / "adoption_policy.json").write_text(json.dumps(cfg))


def test_no_declaration_applies_defaults_and_says_so(tmp_path):
    res = AP.load(tmp_path, env={})
    assert res["config_present"] is False
    assert res["policy"]["skew"] == {"blocked_at": 3, "flagged_at": 2}
    assert set(res["sources"].values()) == {"default"}
    assert res["policy"]["halt"]["allowed_change_patterns"] == ["^@aget-version: \\d+\\.\\d+\\.\\d+$", "^@aget-canonical-specs: https://github\\.com/aget-framework/aget/tree/v\\d+\\.\\d+\\.\\d+/specs(?: — reliance-only conformance(?: \\(D-1, 2026-07-04\\): this template runs the version's features; specs are canonical-referenced, not copied locally)?)?$"]
    assert res["sources"]["halt.allowed_change_patterns"] == "default"
    assert "skew.blocked_at" in res["defaults_ruled"] and "min_release_age_days" in res["defaults_proposed"]


def test_file_declaration_overrides_default_per_key(tmp_path):
    _write(tmp_path, {"skew": {"blocked_at": 5}, "min_release_age_days": 0})
    res = AP.load(tmp_path, env={})
    assert res["policy"]["skew"]["blocked_at"] == 5 and res["sources"]["skew.blocked_at"] == "file"
    assert res["policy"]["skew"]["flagged_at"] == 2 and res["sources"]["skew.flagged_at"] == "default"
    assert res["policy"]["min_release_age_days"] == 0


def test_environment_wins_over_file(tmp_path):
    _write(tmp_path, {"skew": {"blocked_at": 5, "flagged_at": 4}})
    res = AP.load(tmp_path, env={"AGET_ADOPTION_SKEW_BLOCKED_AT": "4"})
    assert res["policy"]["skew"]["blocked_at"] == 4 and res["sources"]["skew.blocked_at"] == "env"


def test_allowed_change_patterns_are_file_only_and_report_their_source(tmp_path):
    env = {"AGET_ADOPTION_HALT_ALLOWED_CHANGE_PATTERNS": '[".*"]'}
    assert AP.load(tmp_path, env=env)["sources"]["halt.allowed_change_patterns"] == "default"
    patterns = AP.DEFAULTS["halt"]["allowed_change_patterns"] + [
        r"^aof-AGET - Always-On Fleet program seat - v\d+\.\d+\.\d+$"]
    _write(tmp_path, {"halt": {"allowed_change_patterns": patterns}})
    res = AP.load(tmp_path, env=env)
    assert res["policy"]["halt"]["allowed_change_patterns"] == patterns
    assert res["sources"]["halt.allowed_change_patterns"] == "file"


@pytest.mark.parametrize("patterns", [[], ["("], [""], [1], "^@aget-version:", None])
def test_invalid_allowed_change_patterns_are_refused(tmp_path, patterns):
    _write(tmp_path, {"halt": {"allowed_change_patterns": patterns}})
    with pytest.raises(AP.PolicyError, match=r"halt\.allowed_change_patterns"):
        AP.load(tmp_path, env={})


@pytest.mark.parametrize("cfg", [
    {"skew": {"blocked_at": 2, "flagged_at": 3}},          # flagged above blocked
    {"skew": {"blocked_at": 0}},                           # never blocks
    {"min_release_age_days": -1},
    {"patch_policy": "sometimes"},
    {"halt": {"identity_patterns": []}},
    {"halt": {"identity_patterns": ["("]}},
])
def test_invalid_declarations_are_refused(tmp_path, cfg):
    _write(tmp_path, cfg)
    with pytest.raises(AP.PolicyError):
        AP.load(tmp_path, env={})


def test_unparseable_file_is_refused_not_ignored(tmp_path):
    (tmp_path / ".aget").mkdir()
    (tmp_path / ".aget" / "adoption_policy.json").write_text("{not json")
    with pytest.raises(AP.PolicyError):
        AP.load(tmp_path, env={})


def test_check_age_both_ways():
    d = dt.date(2026, 10, 10)
    assert AP.check_age(d, dt.date(2026, 10, 17), 7) == (True, 7)
    assert AP.check_age(d, dt.date(2026, 10, 16), 7) == (False, 6)
    assert AP.check_age(d, dt.date(2026, 10, 9), 0) == (False, -1)     # published in the future


def test_cli_check_age_exit_codes(tmp_path):
    assert AP.main(["--root", str(tmp_path), "--check-age", "--published", "2026-10-01", "--today", "2026-10-15"]) == 0
    assert AP.main(["--root", str(tmp_path), "--check-age", "--published", "2026-10-14", "--today", "2026-10-15"]) == 1
    assert AP.main(["--root", str(tmp_path), "--check-age"]) == 2


@pytest.mark.parametrize("cfg", [
    {"skew": [3, 2]}, {"wave1_soak": 24}, {"halt": 10},              # sections that are not objects
    {"min_release_age": 3},                                         # misspelled key must not fall back silently
    {"skew": {"blocked": 3}},
])
def test_malformed_shapes_and_unknown_keys_are_refused(tmp_path, cfg):
    _write(tmp_path, cfg)
    with pytest.raises(AP.PolicyError):
        AP.load(tmp_path, env={})


def test_future_release_is_never_old_enough_even_with_zero_minimum():
    assert AP.check_age(dt.date(2026, 10, 16), dt.date(2026, 10, 15), 0)[0] is False
    assert AP.check_age(dt.date(2026, 10, 15), dt.date(2026, 10, 15), 0)[0] is True


@pytest.mark.parametrize("release,policy,fixes,ok", [
    ("3.4.0", "never-alone", False, True),       # not a patch
    ("3.4.1", "always", False, True),
    ("3.4.1", "never-alone", True, False),
    ("3.4.1", "adopt-if-fixes-me", False, False),
    ("3.4.1", "adopt-if-fixes-me", True, True),
])
def test_patch_rule(release, policy, fixes, ok):
    assert AP.patch_decision(release, policy, fixes)[0] is ok


def test_check_age_applies_the_patch_rule(tmp_path):
    base = ["--root", str(tmp_path), "--check-age", "--published", "2026-10-01", "--today", "2026-10-15"]
    assert AP.main(base + ["--release", "3.4.1"]) == 1                 # old enough, but the default patch rule says wait
    assert AP.main(base + ["--release", "3.4.1", "--fixes-me"]) == 0
    assert AP.main(base + ["--release", "3.4.0"]) == 0
    assert AP.main(base + ["--release", "three"]) == 2


def test_tilde_root_is_expanded(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    _write(tmp_path, {"skew": {"blocked_at": 5}})
    assert AP.load("~", env={})["sources"]["skew.blocked_at"] == "file"


@pytest.mark.parametrize("cfg", [{"min_release_age_days": None}, {"halt": {"identity_patterns": None}},
                                 {"skew": {"blocked_at": None}}])
def test_declared_null_is_refused_not_defaulted(tmp_path, cfg):
    _write(tmp_path, cfg)
    with pytest.raises(AP.PolicyError):
        AP.load(tmp_path, env={})


def test_policy_path_that_is_a_folder_is_refused(tmp_path):
    (tmp_path / ".aget" / "adoption_policy.json").mkdir(parents=True)
    with pytest.raises(AP.PolicyError):
        AP.load(tmp_path, env={})


@pytest.mark.parametrize("release", ["1.5.0garbage", "1.5", "v1.5.0"])
def test_release_must_be_strict(release):
    with pytest.raises(AP.PolicyError):
        AP.patch_decision(release, "always", False)


@pytest.mark.parametrize("pattern", [".*", "|", "^", "x?", r"(?:x|# Agent Instructions|.+)"],
                         ids=["dot-star", "empty-alternative", "start-anchor", "optional-x", "arbitrary-probes"])
def test_c8_match_all_allowlist_is_refused(tmp_path, pattern):
    _write(tmp_path, {"halt": {"allowed_change_patterns": [pattern]}})
    with pytest.raises(AP.PolicyError, match="overly broad"):
        AP.load(tmp_path, env={})


@pytest.mark.parametrize("key", ["allowed_change_patterns", "identity_patterns"])
def test_c8_oversized_patterns_are_refused(tmp_path, key):
    _write(tmp_path, {"halt": {key: ["^" + "a" * 256 + "$"]}})
    with pytest.raises(AP.PolicyError, match="256"):
        AP.load(tmp_path, env={})
