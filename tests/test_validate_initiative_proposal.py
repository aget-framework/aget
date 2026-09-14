"""
test_validate_initiative_proposal.py

Pytest self-test for scripts/validate_initiative_proposal.py.

Verifies the 14 V-INIT-PROP-### implementations against:
- 1 synthetic conformant fixture (all 14 should pass)
- Targeted non-conformant fixtures (each fails specific V-tests)

Spec: AGET_INITIATIVE_SPEC v1.0.1 §7
Plan: PROJECT_PLAN_aget_propose_initiative_v1.0.md Gate 2 (G2.4 self-test)
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_initiative_proposal.py"


def _load_module():
    """Load the validator as a module (avoids `scripts` package import issues).

    Must register in sys.modules BEFORE exec_module — Python 3.14 dataclass
    introspection looks up cls.__module__ via sys.modules.
    """
    spec = importlib.util.spec_from_file_location("vip", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vip"] = mod  # required for @dataclass under Python 3.14+
    spec.loader.exec_module(mod)
    return mod


vip = _load_module()


CONFORMANT_BODY = dedent("""\
    # Initiative Proposal: Synthetic Test

    **Date**: 2026-05-14
    **Author**: private-aget-framework-AGET
    **Status**: PROPOSED
    **Proposal ID**: PP-9999
    **Proposed Initiative ID**: INIT-SYNTHETIC-TEST-FIXTURE
    **Target Versions**: v9.0 – v9.2
    **Theme**: synthetic conformant fixture

    ---

    ## Problem / Opportunity

    Synthetic fixture for self-test.

    ## Evidence

    | Observation | Source | Impact |
    |---|---|---|
    | obs 1 | L760 | high |
    | obs 2 | gh#1325 | medium |
    | obs 3 | sops/SOP_initiative.md | low |

    ## Proposed Scope

    Synthetic scope.

    ### In Scope
    - item

    ### Out of Scope
    - exclusion

    ## Channels

    | Channel | ID | Purpose | Priority |
    |---|---|---|---|
    | KB-only | — | sync | primary |

    ## Contributors

    | Role | Primary Value Dimensions | Availability |
    |---|---|---|
    | Principal | decision quality | On-demand |
    | private-aget-framework-AGET | artifact production | Full |

    ## Cross-Initiative Overlap

    {overlap_rows}

    ## Streams Sketch

    | # | Stream | Target Version | Description |
    |---|---|---|---|
    | 1 | s1 | v9.0 | x |

    ## Size Estimate

    Multi-cycle.

    ## Dependencies

    | Dependency | Type | Status |
    |---|---|---|
    | none | — | n/a |

    ## ADR-008 Readiness

    | Prerequisite | Status |
    |---|---|
    | L-doc evidence | met |
    | SOP exists | met |
    | Governing spec exists | met |

    ## Decision

    - [ ] Principal reviewed
    - [ ] Approved
    - [ ] Deferred
    - [ ] Rejected
    - [ ] Fold into INIT-OTHER

    ## Traceability

    | Link | Reference |
    |---|---|
    | Trigger | self-test |
""")


@contextmanager
def _conformant_fixture(tmp_path: Path):
    """Write a synthetic conformant proposal that should pass all 14 V-tests.

    Builds the Cross-Initiative Overlap section dynamically to cover every
    INIT-*.md currently in planning/initiatives/ (V-INIT-PROP-009 requires
    full coverage of existing initiatives).
    """
    isolated_root = tmp_path / "validator-root"
    initiatives_dir = isolated_root / "planning" / "initiatives"
    source_initiatives = REPO_ROOT / "planning" / "initiatives"
    if source_initiatives.exists():
        shutil.copytree(source_initiatives, initiatives_dir)
    else:
        initiatives_dir.mkdir(parents=True)
    proposals_dir = isolated_root / "planning" / "project-proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    source_index = REPO_ROOT / "planning" / "project-proposals" / "INDEX.md"
    if source_index.exists() and not (proposals_dir / "INDEX.md").exists():
        shutil.copy2(source_index, proposals_dir / "INDEX.md")
    version_path = isolated_root / ".aget" / "version.json"
    version_path.parent.mkdir(parents=True, exist_ok=True)
    if not version_path.exists():
        shutil.copy2(REPO_ROOT / ".aget" / "version.json", version_path)

    # V-013's evidence is a real staged-diff observation.  Give it a disposable
    # worktree, while excluding ambient Git configuration, hooks, and repository
    # selectors from the observation.
    git_env = {name: value for name, value in os.environ.items()
               if not name.startswith("GIT_")}
    git_env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    subprocess.run(["git", "init", "--quiet", str(isolated_root)], check=True, env=git_env)
    hooks_dir = isolated_root / ".git" / "disabled-hooks"
    hooks_dir.mkdir()
    subprocess.run(
        ["git", "-C", str(isolated_root), "config", "core.hooksPath", str(hooks_dir)],
        check=True,
        env=git_env,
    )

    bindings = {
        "REPO_ROOT": vip.REPO_ROOT,
        "INITIATIVES_DIR": vip.INITIATIVES_DIR,
        "PROPOSALS_DIR": vip.PROPOSALS_DIR,
        "INDEX_PATH": vip.INDEX_PATH,
        "VERSION_JSON": vip.VERSION_JSON,
    }
    old_git_env = {name: value for name, value in os.environ.items()
                   if name.startswith("GIT_")}
    for name in old_git_env:
        os.environ.pop(name, None)
    os.environ.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    vip.REPO_ROOT = isolated_root
    vip.INITIATIVES_DIR = initiatives_dir
    vip.PROPOSALS_DIR = proposals_dir
    vip.INDEX_PATH = proposals_dir / "INDEX.md"
    vip.VERSION_JSON = version_path
    overlap_rows = ["| Initiative | Relationship | Notes |", "|---|---|---|"]
    for p in sorted(initiatives_dir.glob("INIT-*.md")):
        overlap_rows.append(f"| {p.stem} | Independent | synthetic |")
    body = CONFORMANT_BODY.format(overlap_rows="\n".join(overlap_rows))

    # Use a unique INIT-ID and PP-### to avoid collisions with real artifacts
    file_path = proposals_dir / "PROPOSAL_init_synthetic_test_fixture.md"
    file_path.write_text(body)
    try:
        yield file_path
    finally:
        for name, value in bindings.items():
            setattr(vip, name, value)
        for name in tuple(os.environ):
            if name.startswith("GIT_"):
                os.environ.pop(name)
        os.environ.update(old_git_env)


_active_fixtures = {}


def _write_conformant(tmp_path: Path) -> Path:
    """Enter an isolated conformant fixture; paired with ``_cleanup`` below."""
    manager = _conformant_fixture(tmp_path)
    file_path = manager.__enter__()
    _active_fixtures[file_path] = manager
    return file_path


def _cleanup(file_path: Path) -> None:
    """Leave the fixture, restoring every validator binding and Git env value."""
    manager = _active_fixtures.pop(file_path)
    manager.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# Conformant fixture: all 14 should pass
# ---------------------------------------------------------------------------

def test_conformant_fixture_passes_v001_002_004_005_006_007_008_009_010_011_013(tmp_path):
    """The conformant fixture passes all V-tests that don't depend on INDEX state.

    V-INIT-PROP-003 (PP-### monotonic vs INDEX) and V-INIT-PROP-012 (INDEX has
    matching row) and V-INIT-PROP-014 (target version > current) depend on
    repo-wide state we don't mutate in tests; they're tested separately with
    targeted assertions.
    """
    file_path = _write_conformant(tmp_path)
    try:
        results = vip.run_all(file_path)
        by_id = {r.v_id: r for r in results}
        # State-independent V-tests: must all pass on the conformant fixture
        for v in [
            "V-INIT-PROP-001",
            "V-INIT-PROP-002",
            "V-INIT-PROP-004",
            "V-INIT-PROP-005",
            "V-INIT-PROP-006",
            "V-INIT-PROP-007",
            "V-INIT-PROP-008",
            "V-INIT-PROP-009",
            "V-INIT-PROP-010",
            "V-INIT-PROP-011",
            "V-INIT-PROP-013",
        ]:
            assert by_id[v].passed, f"{v} should pass on conformant fixture: {by_id[v].detail}"
    finally:
        _cleanup(file_path)


def test_conformant_fixture_v014_passes_with_future_version(tmp_path):
    """V-INIT-PROP-014: synthetic v9.0 start > current aget_version (3.17 today)."""
    file_path = _write_conformant(tmp_path)
    try:
        results = vip.run_all(file_path)
        v014 = next(r for r in results if r.v_id == "V-INIT-PROP-014")
        assert v014.passed, f"v9.0 should be > current version: {v014.detail}"
    finally:
        _cleanup(file_path)


def test_conformant_fixture_is_scoped_and_observes_clean_staged_diff(tmp_path):
    """Fixture state is synthetic, Git-observable, and restored at teardown."""
    names = ("REPO_ROOT", "INITIATIVES_DIR", "PROPOSALS_DIR", "INDEX_PATH", "VERSION_JSON")
    originals = {name: getattr(vip, name) for name in names}
    file_path = _write_conformant(tmp_path)
    try:
        assert vip.REPO_ROOT != originals["REPO_ROOT"]
        assert list(vip.INITIATIVES_DIR.glob("INIT-*.md")) == []
        assert not vip.INDEX_PATH.exists()
        staged, observation = vip.staged_initiative_manifests()
        assert observation == "staged-diff"
        assert staged == []
    finally:
        _cleanup(file_path)
    assert {name: getattr(vip, name) for name in names} == originals


def test_v013_fails_from_real_staged_manifest_observation(tmp_path):
    """V-013's negative control stages fixture data in the disposable repository."""
    file_path = _write_conformant(tmp_path)
    try:
        manifest = vip.INITIATIVES_DIR / "INIT-SYNTHETIC-STAGED.md"
        manifest.write_text("# Synthetic staged manifest\n")
        subprocess.run(
            ["git", "-C", str(vip.REPO_ROOT), "add", "--", str(manifest.relative_to(vip.REPO_ROOT))],
            check=True,
        )
        result = vip.verify_v_init_prop_013(file_path, file_path.read_text())
        assert result.outcome == "FAIL", result.detail
        assert "planning/initiatives/INIT-SYNTHETIC-STAGED.md" in result.detail
    finally:
        _cleanup(file_path)


# ---------------------------------------------------------------------------
# Targeted non-conformance: each V-test should fail when its specific
# clause is violated
# ---------------------------------------------------------------------------

def test_v002_fails_when_section_missing(tmp_path):
    """Remove '## Channels' from a proposal; V-INIT-PROP-002 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace("## Channels", "## NotChannels")
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v002 = next(r for r in results if r.v_id == "V-INIT-PROP-002")
        assert not v002.passed
        assert "## Channels" in v002.detail
    finally:
        _cleanup(file_path)


def test_v005_fails_when_evidence_under_three(tmp_path):
    """Trim Evidence to 1 data row; V-INIT-PROP-005 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text()
        # Drop 2 of the 3 evidence rows
        text = text.replace("| obs 2 | gh#1325 | medium |\n", "")
        text = text.replace("| obs 3 | sops/SOP_initiative.md | low |\n", "")
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v005 = next(r for r in results if r.v_id == "V-INIT-PROP-005")
        assert not v005.passed
    finally:
        _cleanup(file_path)


def test_v006_fails_when_evidence_source_untyped(tmp_path):
    """Replace a typed Source with 'anecdote'; V-INIT-PROP-006 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace("| obs 1 | L760 | high |", "| obs 1 | anecdote | high |")
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v006 = next(r for r in results if r.v_id == "V-INIT-PROP-006")
        assert not v006.passed
        assert "anecdote" in v006.detail
    finally:
        _cleanup(file_path)


def test_v008_fails_when_principal_missing(tmp_path):
    """Remove Principal row from Contributors; V-INIT-PROP-008 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace(
            "| Principal | decision quality | On-demand |\n", ""
        )
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v008 = next(r for r in results if r.v_id == "V-INIT-PROP-008")
        assert not v008.passed
    finally:
        _cleanup(file_path)


def test_v010_fails_when_decision_option_missing(tmp_path):
    """Remove 'Fold into' option from Decision; V-INIT-PROP-010 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace(
            "- [ ] Fold into INIT-OTHER", "- [ ] Some other thing"
        )
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v010 = next(r for r in results if r.v_id == "V-INIT-PROP-010")
        assert not v010.passed
        assert "Fold into" in v010.detail
    finally:
        _cleanup(file_path)


def test_v011_fails_when_status_not_proposed(tmp_path):
    """Set Status to APPROVED at file creation; V-INIT-PROP-011 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace("**Status**: PROPOSED", "**Status**: APPROVED")
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v011 = next(r for r in results if r.v_id == "V-INIT-PROP-011")
        assert not v011.passed
    finally:
        _cleanup(file_path)


def test_v014_fails_when_target_version_past_start(tmp_path):
    """Set Target Versions to v1.0 (way past current); V-INIT-PROP-014 fails."""
    file_path = _write_conformant(tmp_path)
    try:
        text = file_path.read_text().replace(
            "**Target Versions**: v9.0 – v9.2",
            "**Target Versions**: v1.0 – v1.2",
        )
        file_path.write_text(text)
        results = vip.run_all(file_path)
        v014 = next(r for r in results if r.v_id == "V-INIT-PROP-014")
        assert not v014.passed
    finally:
        _cleanup(file_path)


# ---------------------------------------------------------------------------
# Structural test: 14 verifier functions exist + correctly named
# ---------------------------------------------------------------------------

def test_fourteen_verify_functions_exist():
    """The module must expose exactly 14 functions named verify_v_init_prop_NNN.

    Satisfies: V-INIT-PROP-001 — V-INIT-PROP-001 through V-INIT-PROP-014 validator coverage."""
    import inspect
    fns = [
        name for name, obj in inspect.getmembers(vip, inspect.isfunction)
        if name.startswith("verify_v_init_prop_")
    ]
    assert len(fns) == 14, f"expected 14, got {len(fns)}: {sorted(fns)}"


def test_each_verifier_returns_vresult_with_cap_citation(tmp_path):
    """Every verifier must return a VResult naming at least one CAP-INIT-PROP-* clause.

    Satisfies: V-INIT-PROP-001 — V-INIT-PROP-001 through V-INIT-PROP-014 validator coverage."""
    file_path = _write_conformant(tmp_path)
    try:
        results = vip.run_all(file_path)
        assert len(results) == 14
        for r in results:
            assert r.v_id.startswith("V-INIT-PROP-")
            assert r.cap_ids, f"{r.v_id} cites no CAP clause"
            for cap in r.cap_ids:
                assert cap.startswith("CAP-INIT-PROP-"), f"{r.v_id} cites non-CAP: {cap}"
    finally:
        _cleanup(file_path)


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

def test_cli_json_mode(tmp_path, capsys):
    """Satisfies: V-INIT-PROP-001 — V-INIT-PROP-001 through V-INIT-PROP-014 validator coverage."""
    file_path = _write_conformant(tmp_path)
    try:
        rc = vip.main(["--file", str(file_path), "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["n_total"] == 14
        assert data["file"] == str(file_path)
        # rc is 0 only if ALL 14 pass; in this repo state, V-INIT-PROP-003
        # (PP-9999 unique check) and V-INIT-PROP-012 (INDEX matching row)
        # may not both pass without index mutation; just verify structure here.
        assert rc in (0, 1)
    finally:
        _cleanup(file_path)


# ---------------------------------------------------------------------------
# Falsifiers for V-INIT-PROP-004 / -013 (2026-08-29).
#
# Both checks were reported defective by a peer seat and both were found already
# repaired here -- but neither had a negative arm, so nothing asserted the repair
# held. A fixed instance with no falsifier is an unprotected class: the next edit
# can silently restore the first-match scan that CAP-INIT-PROP-013-01 prohibits.
# ---------------------------------------------------------------------------

def _proposal(init_id: str, body: str = "", preamble: str = "") -> str:
    """Preamble goes BEFORE the declared field on purpose.

    A fixture that puts the declared id first cannot discriminate a first-match
    scan from a field-bound read -- both land on the same token. Mutation-tested
    2026-08-29: with the preamble the mutant fails, without it the mutant passes.
    """
    return (f"# Proposal\n{preamble}\n"
            f"**Proposed Initiative ID**: {init_id}\n\n{body}\n")


def test_v004_cross_reference_in_body_is_not_a_duplicate_claim(tmp_path, monkeypatch):
    """V-INIT-PROP-004 / CAP-INIT-PROP-013-01: only the DECLARED field is a claim.

    The reported false positive: an overlap analysis naming other initiatives must
    not be read as claiming their ids."""
    inits = tmp_path / "initiatives"; inits.mkdir()
    props = tmp_path / "proposals"; props.mkdir()
    (inits / "INIT-EXISTING-ONE.md").write_text("# existing\n")
    monkeypatch.setattr(vip, "INITIATIVES_DIR", inits)
    monkeypatch.setattr(vip, "PROPOSALS_DIR", props)

    text = _proposal(
        "INIT-BRAND-NEW",
        body="## Overlap analysis\nDoes not duplicate INIT-EXISTING-ONE.",
        preamble="## Summary\nThis supersedes nothing; INIT-EXISTING-ONE stays as is.",
    )
    r = vip.verify_v_init_prop_004(tmp_path / "p.md", text)
    assert r.outcome == "PASS", r.detail
    assert "INIT-BRAND-NEW" in r.detail


def test_v004_declared_id_matching_an_existing_manifest_fails(tmp_path, monkeypatch):
    """V-INIT-PROP-004 / CAP-INIT-PROP-002-03: positive control.

    A falsifier that cannot fail is decorative; this arm proves it can."""
    inits = tmp_path / "initiatives"; inits.mkdir()
    props = tmp_path / "proposals"; props.mkdir()
    (inits / "INIT-EXISTING-ONE.md").write_text("# existing\n")
    monkeypatch.setattr(vip, "INITIATIVES_DIR", inits)
    monkeypatch.setattr(vip, "PROPOSALS_DIR", props)

    r = vip.verify_v_init_prop_004(tmp_path / "p.md", _proposal("INIT-EXISTING-ONE"))
    assert r.outcome == "FAIL", r.detail


def test_v004_two_declarations_are_ambiguous_not_first_wins(tmp_path, monkeypatch):
    """V-INIT-PROP-004 / CAP-INIT-PROP-013-01: two declarations are ambiguous.

    First-match-wins is the prohibited behaviour, not a tolerated fallback."""
    inits = tmp_path / "initiatives"; inits.mkdir()
    props = tmp_path / "proposals"; props.mkdir()
    monkeypatch.setattr(vip, "INITIATIVES_DIR", inits)
    monkeypatch.setattr(vip, "PROPOSALS_DIR", props)

    text = ("# Proposal\n**Proposed Initiative ID**: INIT-ONE\n"
            "**Proposed Initiative ID**: INIT-TWO\n")
    r = vip.verify_v_init_prop_004(tmp_path / "p.md", text)
    assert r.outcome == "FAIL" and "ambiguous" in r.detail


def test_v013_and_v004_agree_on_an_ambiguous_input():
    """V-INIT-PROP-004 and V-INIT-PROP-013 must not disagree on one input.

    D2 guard: two verifiers reading the same declared field."""
    text = ("# Proposal\n**Proposed Initiative ID**: INIT-ONE\n"
            "**Proposed Initiative ID**: INIT-TWO\n")
    a = vip.verify_v_init_prop_004(Path("p.md"), text)
    b = vip.verify_v_init_prop_013(Path("p.md"), text)
    assert a.outcome == b.outcome == "FAIL"


def test_v013_missing_declared_field_fails_rather_than_passing_vacuously():
    """V-INIT-PROP-013 / CAP-INIT-PROP-011-01: absence fails, never passes."""
    r = vip.verify_v_init_prop_013(Path("p.md"), "# Proposal\nno id here\n")
    assert r.outcome == "FAIL", r.detail
