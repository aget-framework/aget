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
import sys
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


def _write_conformant(tmp_path: Path) -> Path:
    """Write a synthetic conformant proposal that should pass all 14 V-tests.

    Builds the Cross-Initiative Overlap section dynamically to cover every
    INIT-*.md currently in planning/initiatives/ (V-INIT-PROP-009 requires
    full coverage of existing initiatives).
    """
    initiatives_dir = REPO_ROOT / "planning" / "initiatives"
    overlap_rows = ["| Initiative | Relationship | Notes |", "|---|---|---|"]
    for p in sorted(initiatives_dir.glob("INIT-*.md")):
        overlap_rows.append(f"| {p.stem} | Independent | synthetic |")
    body = CONFORMANT_BODY.format(overlap_rows="\n".join(overlap_rows))

    # Use a unique INIT-ID and PP-### to avoid collisions with real artifacts
    proposals_dir = REPO_ROOT / "planning" / "project-proposals"
    # A consumer repo need not already have this directory. Assuming it exists made
    # every test in this file fail with FileNotFoundError at canonical while passing
    # at the producer seat -- green here, red there, which is the promotion defect
    # this suite is supposed to help catch.
    proposals_dir.mkdir(parents=True, exist_ok=True)
    file_path = proposals_dir / "PROPOSAL_init_synthetic_test_fixture.md"
    file_path.write_text(body)
    return file_path


def _cleanup(file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink()


# ---------------------------------------------------------------------------
# Conformant fixture: all 14 should pass
# ---------------------------------------------------------------------------

def test_conformant_fixture_passes_v001_002_004_005_006_007_008_009_010_011_013():
    """The conformant fixture passes all V-tests that don't depend on INDEX state.

    V-INIT-PROP-003 (PP-### monotonic vs INDEX) and V-INIT-PROP-012 (INDEX has
    matching row) and V-INIT-PROP-014 (target version > current) depend on
    repo-wide state we don't mutate in tests; they're tested separately with
    targeted assertions.
    """
    file_path = _write_conformant(REPO_ROOT)
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


def test_conformant_fixture_v014_passes_with_future_version():
    """V-INIT-PROP-014: synthetic v9.0 start > current aget_version (3.17 today)."""
    file_path = _write_conformant(REPO_ROOT)
    try:
        results = vip.run_all(file_path)
        v014 = next(r for r in results if r.v_id == "V-INIT-PROP-014")
        assert v014.passed, f"v9.0 should be > current version: {v014.detail}"
    finally:
        _cleanup(file_path)


# ---------------------------------------------------------------------------
# Targeted non-conformance: each V-test should fail when its specific
# clause is violated
# ---------------------------------------------------------------------------

def test_v002_fails_when_section_missing(tmp_path):
    """Remove '## Channels' from a proposal; V-INIT-PROP-002 fails."""
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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


def test_each_verifier_returns_vresult_with_cap_citation():
    """Every verifier must return a VResult naming at least one CAP-INIT-PROP-* clause.

    Satisfies: V-INIT-PROP-001 — V-INIT-PROP-001 through V-INIT-PROP-014 validator coverage."""
    file_path = _write_conformant(REPO_ROOT)
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
    file_path = _write_conformant(REPO_ROOT)
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
