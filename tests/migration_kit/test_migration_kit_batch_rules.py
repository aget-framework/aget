"""Carriage row 72: batch sessions get their allow rules for one session only (claude --settings). Each rule names one
kit tool and covers it with ANY arguments. These tests assert that each ruled tool's source contains a call to the
typed-authority check (row 62); they do not show that the call runs on every path, and `launch_batch.py --launch
--copy-root` skips it. Row 70: the tools drop variables whose names end in API_KEY, so no command prefix is needed.
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
RULE = re.compile(r"^Bash\(python3 scripts/migration_kit/([a-z_]+)\.py:\*\)$")


def rules():
    return json.loads((KIT / "batch_rules.json").read_text())["permissions"]["allow"]


def test_the_rules_file_is_settings_shaped_and_grants_only_allow_rules():
    doc = json.loads((KIT / "batch_rules.json").read_text())
    assert set(doc) == {"permissions"} and set(doc["permissions"]) == {"allow"}


def test_every_rule_is_narrow_and_names_a_kit_tool():
    """'Narrow' means one kit tool per rule. Each rule ends `:*`, so it covers that tool with any arguments."""
    for r in rules():
        m = RULE.match(r)
        assert m, f"not a narrow kit-tool rule: {r}"
        assert (KIT / f"{m.group(1)}.py").is_file()


def test_every_ruled_tool_checks_typed_authority_itself():
    """An allow rule for a tool without its own authority check would be standing self-authorization. This asserts
    only that the text `batch_authority.check(`, `batch_authority.verify(` or `batch_authority.push_authority(` (which
    calls check(); R2-T12) appears in each ruled tool's source. It
    does not run the tools, and cannot see a path that skips the call (`launch_batch.py --launch --copy-root`)."""
    for r in rules():
        src = (KIT / f"{RULE.match(r).group(1)}.py").read_text()
        assert any(f"batch_authority.{f}(" in src for f in ("check", "verify", "push_authority")), r


def test_the_rules_name_exactly_the_gated_batch_tools():
    """'Gated' means the tool's source calls the authority check; launch_batch.py skips it when --copy-root is given."""
    assert sorted(RULE.match(r).group(1) for r in rules()) == ["launch_batch", "push_batch", "record_authority"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, KIT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_tools_drop_api_keys_but_keep_login(monkeypatch, tmp_path):
    """Covers variables whose names end in API_KEY only (push_batch.py by its source text); other tokens are kept."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("OPENAI_API_KEY", "y")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "z")
    env = load("launch_batch").session_env()
    assert "ANTHROPIC_API_KEY" not in env and "OPENAI_API_KEY" not in env and env["CLAUDE_CODE_OAUTH_TOKEN"] == "z"
    env = load("suite_at_commit").suite_env(tmp_path)
    assert "OPENAI_API_KEY" not in env and env["CLAUDE_CODE_OAUTH_TOKEN"] == "z"
    assert 'not k.endswith("API_KEY")' in (KIT / "push_batch.py").read_text()


def test_the_guide_gives_the_launch_command():
    assert "claude --settings scripts/migration_kit/batch_rules.json" in (KIT / "BATCH_SESSION.md").read_text()
