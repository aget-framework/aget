"""C-34-03 — a producer-side lint ratchet, and a merge-semantics check that is not a lint check.

gh#2464: the payload was lint-dirty for the THIRD release running (gh#832 v3.12.0,
gh#2041 v3.28.0, this one v3.33.1), and the reporter named why a point fix fails:

    "The instance is not the finding. The recurrence is. A corrected v3.33.2 tag closes this
     occurrence and leaves the producing mechanism exactly as it is."

Two mechanisms, tested here: a ratchet that cannot be satisfied by getting worse, and a
retention check that sees what byte-hashes and lint both pass through.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ret = load("ccr", "scripts/check_capability_retention.py")
lint = load("cpl", "scripts/check_payload_lint.py")


def tree(base: Path, name: str, files: dict[str, str]) -> Path:
    d = base / name
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


MOD = """
API_VERSION = "1"

def public_entry(x):
    return x

def _helper():
    pass

class Thing:
    pass

def build(p):
    p.add_argument("--repo")
    p.add_argument("--mode", choices=["fast", "slow"])
"""


def test_guarded_public_definitions_and_reexports_are_retained(tmp_path):
    module = (
        "if enabled:\n    def guarded(): pass\n"
        "try:\n    from provider import Public as Exported\n"
        "except ImportError:\n    class Exported: pass\n"
        "def outer():\n    def local_only(): pass\n"
    )
    before = tree(tmp_path, "before", {"api.py": module})
    after = tree(tmp_path, "after", {"api.py": module})
    assert ret.assess(before, after, set())["state"] == "RETAINED"
    (after / "api.py").write_text("def outer(): pass\n")
    result = ret.assess(before, after, set())
    assert result["state"] == "REMOVED"
    assert set(result["removed"]["api.py"]) == {
        "def:guarded", "reexport:Exported", "class:Exported"
    }


def test_partial_or_unsupported_retention_population_is_unavailable(tmp_path):
    before = tree(tmp_path, "before", {"api.py": "def public(): pass\n"})
    after = tree(tmp_path, "after", {"api.py": "def public(): pass\n"})
    note = tmp_path / "note.md"
    note.write_text("Documentation outside the Python export population")
    (after / "note.md").symlink_to(note)
    assert ret.assess(before, after, set())["state"] == "RETAINED"
    hidden = after / "hidden"
    hidden.mkdir()
    hidden.chmod(0)
    try:
        assert ret.assess(before, after, set())["state"] == "UNAVAILABLE"
    finally:
        hidden.chmod(0o700)
    (hidden / "external").symlink_to(before, target_is_directory=True)
    assert ret.assess(before, after, set())["state"] == "UNAVAILABLE"
    (hidden / "external").unlink()
    (after / "api.py").write_text("from provider import *\n")
    assert ret.assess(before, after, set())["state"] == "UNAVAILABLE"


def test_unparseable_present_module_is_not_reported_removed(tmp_path):
    before = tree(tmp_path, "before", {"api.py": "def public(): pass\ndef _private(): pass\n"})
    after = tree(tmp_path, "after", {"api.py": "def broken(\n"})
    result = ret.assess(before, after, set())
    assert result["state"] == "UNAVAILABLE"
    assert result["removed"] == {}
    assert result["private_removed"] == {}
    assert result["counts_complete"] is False
    assert "REMOVED  api.py" not in ret.render(result)
    assert ret.assess(after, before, set())["added"] == {}


# ---------------- retention: what hashes and lint pass through ----------------


def test_an_unchanged_payload_retains_everything(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD})
    res = ret.assess(b, a, set())
    assert res["state"] == "RETAINED" and ret.exit_code(res) == 0


def test_a_removed_function_is_caught_though_the_file_lints_clean(tmp_path):
    """The overwritten file is perfectly clean code; the capability is gone."""
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD.replace("def public_entry(x):\n    return x\n", "")})
    res = ret.assess(b, a, set())
    assert res["state"] == "REMOVED"
    assert "def:public_entry" in res["removed"]["m.py"]
    assert ret.exit_code(res) == 1


def test_a_removed_cli_flag_is_a_capability_loss(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD.replace('    p.add_argument("--repo")\n', "")})
    assert "flag:--repo" in ret.assess(b, a, set())["removed"]["m.py"]


def test_a_removed_subcommand_choice_is_a_capability_loss(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD.replace('["fast", "slow"]', '["fast"]')})
    assert "choice:slow" in ret.assess(b, a, set())["removed"]["m.py"]


def test_a_removed_class_and_constant_are_capability_losses(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(
        tmp_path,
        "a",
        {"m.py": MOD.replace("class Thing:\n    pass\n", "").replace('API_VERSION = "1"\n', "")},
    )
    gone = ret.assess(b, a, set())["removed"]["m.py"]
    assert "class:Thing" in gone and "const:API_VERSION" in gone


def test_a_whole_module_removed_is_the_loudest_case(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD, "gone.py": "def f():\n    pass\n"})
    a = tree(tmp_path, "a", {"m.py": MOD})
    res = ret.assess(b, a, set())
    assert res["removed"]["gone.py"][0] == "<module removed>"


def test_a_private_name_removal_is_reported_and_does_not_fail(tmp_path):
    """Consumers were never entitled to it."""
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD.replace("def _helper():\n    pass\n", "")})
    res = ret.assess(b, a, set())
    assert res["state"] == "RETAINED"
    assert "def:_helper" in res["private_removed"]["m.py"]


def test_additions_never_fail_retention(tmp_path):
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD + "\ndef brand_new():\n    pass\n"})
    res = ret.assess(b, a, set())
    assert res["state"] == "RETAINED" and "def:brand_new" in res["added"]["m.py"]


def test_a_deliberate_removal_can_be_allow_listed(tmp_path):
    """A deprecation record, not a silent deletion."""
    b = tree(tmp_path, "b", {"m.py": MOD})
    a = tree(tmp_path, "a", {"m.py": MOD.replace("def public_entry(x):\n    return x\n", "")})
    assert ret.assess(b, a, {"def:public_entry"})["state"] == "RETAINED"


def test_an_unparseable_file_is_UNAVAILABLE_not_retained(tmp_path):
    """Retention across a file we could not read is UNKNOWN, never confirmed."""
    b = tree(tmp_path, "b", {"m.py": MOD, "broken.py": "def (:\n"})
    a = tree(tmp_path, "a", {"m.py": MOD, "broken.py": "def (:\n"})
    res = ret.assess(b, a, set())
    assert res["state"] == "UNAVAILABLE" and ret.exit_code(res) == 2


def test_the_checker_parses_and_never_executes_the_payload():
    """Running a candidate payload to learn what it exports is the state-changing act a
    producer gate must not take."""
    src = (REPO / "scripts" / "check_capability_retention.py").read_text()
    assert "ast.parse" in src
    for forbidden in ("subprocess", "exec(", "eval(", "importlib"):
        assert forbidden not in src, f"{forbidden} in a parse-only checker"


# ---------------- the lint ratchet ----------------


def test_the_shipped_repository_declares_a_ruff_config():
    """Canonical carried NO config, so producer and receiver measured different payloads."""
    assert (REPO / "ruff.toml").exists()
    text = (REPO / "ruff.toml").read_text()
    for rule in ("E4", "E7", "E9", "F", "I", "W", "B008"):
        assert f'"{rule}"' in text, f"{rule} missing from the declared select"


def test_a_missing_baseline_is_UNAVAILABLE_not_a_clean_payload(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/payload.py").write_text("value = 1\n")
    res = lint.assess(tmp_path, tmp_path / "nope.json", ["scripts"])
    assert res["state"] == "UNAVAILABLE"
    assert "not a clean payload" in res["why"]
    assert lint.exit_code(res) == 2


def test_a_repository_with_no_ruff_config_is_UNAVAILABLE(tmp_path):
    (tmp_path / "scripts").mkdir()
    res = lint.assess(tmp_path, tmp_path / "b.json", ["scripts"])
    assert res["state"] == "UNAVAILABLE" and "declares no ruff configuration" in res["why"]


def test_missing_or_empty_target_cannot_pass_or_replace_baseline(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    payload = scripts / "payload.py"
    payload.write_text("value = 1\n")
    baseline = tmp_path / "baseline.json"
    args = ["--repo", str(tmp_path), "--baseline", str(baseline), "--path", "scripts"]
    assert lint.main(args + ["--update"]) == 0
    saved = baseline.read_bytes()
    assert lint.assess(tmp_path, baseline, ["scripts"])["state"] == "PASS"
    payload.unlink()
    assert lint.assess(tmp_path, baseline, ["scripts"])["state"] == "UNAVAILABLE"
    assert lint.main(args + ["--update"]) == 2
    assert baseline.read_bytes() == saved
    assert lint.assess(tmp_path, baseline, ["absent"])["state"] == "UNAVAILABLE"
    payload.write_text("value = 1\n")
    assert lint.assess(tmp_path, baseline, ["scripts", "absent"])["state"] == "UNAVAILABLE"


def test_a_new_dirty_file_fails_even_when_the_total_is_unchanged(tmp_path):
    """A backlog is inherited, never extended."""
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    s = tmp_path / "scripts"
    s.mkdir()
    (s / "old.py").write_text("import os\n")  # F401
    base = tmp_path / "b.json"
    assert (
        lint.main(
            ["--repo", str(tmp_path), "--baseline", str(base), "--path", "scripts", "--update"]
        )
        == 0
    )
    (s / "old.py").write_text("x = 1\n")  # fixed: -1
    (s / "new.py").write_text("import sys\n")  # new dirty: +1, total unchanged
    res = lint.assess(tmp_path, base, ["scripts"])
    assert res["state"] == "FAIL"
    assert "newly added file" in res["why"] and res["total_now"] == res["total_baseline"]


def test_an_existing_file_getting_worse_fails(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    s = tmp_path / "scripts"
    s.mkdir()
    (s / "m.py").write_text("import os\n")
    base = tmp_path / "b.json"
    lint.main(["--repo", str(tmp_path), "--baseline", str(base), "--path", "scripts", "--update"])
    (s / "m.py").write_text("import os\nimport sys\n")
    res = lint.assess(tmp_path, base, ["scripts"])
    assert res["state"] == "FAIL" and "got worse" in res["why"]


def test_improvement_passes_and_is_reported(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    s = tmp_path / "scripts"
    s.mkdir()
    (s / "m.py").write_text("import os\nimport sys\n")
    base = tmp_path / "b.json"
    lint.main(["--repo", str(tmp_path), "--baseline", str(base), "--path", "scripts", "--update"])
    (s / "m.py").write_text("x = 1\n")
    res = lint.assess(tmp_path, base, ["scripts"])
    assert res["state"] == "PASS" and res["improved"]


def test_a_ruff_version_change_is_surfaced_not_absorbed(tmp_path):
    """gh#2007: a vendor rule expansion changes the count without the code changing."""
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n')
    s = tmp_path / "scripts"
    s.mkdir()
    (s / "m.py").write_text("x = 1\n")
    base = tmp_path / "b.json"
    lint.main(["--repo", str(tmp_path), "--baseline", str(base), "--path", "scripts", "--update"])
    doc = json.loads(base.read_text())
    doc["ruff_version"] = "ruff 0.0.1"
    base.write_text(json.dumps(doc))
    res = lint.assess(tmp_path, base, ["scripts"])
    assert res["version_changed"] is True
    assert "e-baseline deliberately" in lint.render(res)
