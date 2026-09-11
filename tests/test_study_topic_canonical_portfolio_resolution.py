"""C-34-04 / gh#2451 — the canonical resolver must reach beyond immediate siblings.

Both polarities and the compatibility case. The prior body scanned only
`agent_root.parent.iterdir()`, so a portfolio layout returned a clean empty list
that could not be distinguished from a genuine absence.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import study_topic as st  # noqa: E402


def _canonical(base: Path, nested: bool = False) -> Path:
    """Create a canonical checkout carrying the marker file."""
    specs = (base / "aget" / "specs") if nested else (base / "specs")
    specs.mkdir(parents=True)
    (specs / "AGET_SESSION_SPEC.md").write_text("# marker\n")
    (specs.parent / "docs" / "patterns").mkdir(parents=True)
    return specs


# ---------------------------------------------------------------- compatibility
def test_immediate_sibling_layout_still_resolves(tmp_path, monkeypatch):
    """UNCHANGED behaviour: a seat resolving today must resolve identically."""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    portfolio = tmp_path / "github"
    agent = portfolio / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(portfolio / "aget")
    assert st.find_canonical_spec_roots(agent) == [specs]


def test_immediate_sibling_nested_layout_still_resolves(tmp_path, monkeypatch):
    """The second historical layout (checkout CONTAINS aget/) also unchanged."""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    portfolio = tmp_path / "github"
    agent = portfolio / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(portfolio / "checkout", nested=True)
    assert st.find_canonical_spec_roots(agent) == [specs]


# ---------------------------------------------------------------------- success
def test_portfolio_parent_layout_resolves(tmp_path, monkeypatch):
    """THE DEFECT: canonical one directory outside the sibling scan."""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    root = tmp_path / "github"
    agent = root / "GM-CCB" / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(root / "aget-framework" / "aget")
    assert st.find_canonical_spec_roots(agent) == [specs]


def test_env_route_resolves_and_takes_precedence(tmp_path, monkeypatch):
    agent = tmp_path / "github" / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(tmp_path / "elsewhere" / "aget")
    monkeypatch.setenv(st.CANONICAL_ROOT_ENV, str(specs.parent))
    roots = st.find_canonical_spec_roots(agent)
    assert roots and roots[0] == specs


def test_config_route_resolves(tmp_path, monkeypatch):
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    agent = tmp_path / "github" / "private-x-aget"
    (agent / ".aget").mkdir(parents=True)
    specs = _canonical(tmp_path / "elsewhere" / "aget")
    (agent / ".aget" / "config.json").write_text(json.dumps({"canonical_root": str(specs.parent)}))
    assert st.find_canonical_spec_roots(agent) == [specs]


def test_patterns_reach_the_same_canonical_source_as_specs(tmp_path, monkeypatch):
    """Acceptance: 'Both specs and patterns must reach the same canonical source.'"""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    root = tmp_path / "github"
    agent = root / "GM-CCB" / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(root / "aget-framework" / "aget")
    spec_roots = st.find_canonical_spec_roots(agent)
    pattern_roots = st.find_canonical_pattern_roots(agent)
    assert spec_roots == [specs]
    assert pattern_roots == [specs.parent / "docs" / "patterns"]
    assert pattern_roots[0].parent.parent == spec_roots[0].parent


# -------------------------------------------------------------------- rejection
def test_absent_canonical_returns_empty_and_names_the_search_scope(tmp_path, monkeypatch):
    """An honest miss: empty result AND a stated scope, not a bare zero."""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    agent = tmp_path / "github" / "GM-CCB" / "private-x-aget"
    agent.mkdir(parents=True)
    (tmp_path / "github" / "other-portfolio" / "unrelated").mkdir(parents=True)
    assert st.find_canonical_spec_roots(agent) == []
    scope = st.canonical_search_scope()
    assert scope, "an unresolved search must still state where it looked"
    assert any("immediate siblings" in s for s in scope)
    assert any("portfolio siblings" in s for s in scope)


def test_directory_without_marker_file_is_refused(tmp_path, monkeypatch):
    """A specs/ dir lacking AGET_SESSION_SPEC.md is not canonical."""
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    portfolio = tmp_path / "github"
    agent = portfolio / "private-x-aget"
    agent.mkdir(parents=True)
    (portfolio / "impostor" / "specs").mkdir(parents=True)
    assert st.find_canonical_spec_roots(agent) == []


def test_env_route_pointing_at_nothing_is_refused_not_crashed(tmp_path, monkeypatch):
    agent = tmp_path / "github" / "private-x-aget"
    agent.mkdir(parents=True)
    monkeypatch.setenv(st.CANONICAL_ROOT_ENV, str(tmp_path / "does-not-exist"))
    assert st.find_canonical_spec_roots(agent) == []
    assert any("AGET_CANONICAL_ROOT" in s for s in st.canonical_search_scope())


def test_unreadable_config_is_recorded_not_silently_skipped(tmp_path, monkeypatch):
    monkeypatch.delenv(st.CANONICAL_ROOT_ENV, raising=False)
    agent = tmp_path / "github" / "private-x-aget"
    (agent / ".aget").mkdir(parents=True)
    (agent / ".aget" / "config.json").write_text("{not json")
    st.find_canonical_spec_roots(agent)
    assert any("unreadable" in s for s in st.canonical_search_scope())


def test_no_duplicate_roots_when_routes_overlap(tmp_path, monkeypatch):
    """Env route and sibling scan finding the same checkout yields ONE root."""
    portfolio = tmp_path / "github"
    agent = portfolio / "private-x-aget"
    agent.mkdir(parents=True)
    specs = _canonical(portfolio / "aget")
    monkeypatch.setenv(st.CANONICAL_ROOT_ENV, str(specs.parent))
    assert st.find_canonical_spec_roots(agent) == [specs]
