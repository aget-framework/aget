"""Falsifiers for scripts/check_archetype_register_parity.py.

Bound tests exist because gh#2355 recorded two instruments shipping with zero of
them. Both polarities are exercised on every finding class: a defect MUST flag,
and a clean population set MUST stay silent. A check that only ever fires on live
data is untested in the direction that matters (L1439).

The reader functions are exercised against real fixture files, not only the pure
comparison logic -- a parser that silently returns an empty population would make
every divergence invisible while compare() stayed correct.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "check_archetype_register_parity.py"

sys.path.insert(0, str(REPO / "scripts"))
import check_archetype_register_parity as parity  # noqa: E402

UNAVAILABLE = parity.UNAVAILABLE


# --------------------------------------------------------------------------
# compare(): both polarities on every finding class
# --------------------------------------------------------------------------

def _kinds(findings):
    return {f["kind"] for f in findings}


def test_unregistered_role_flags():
    """Satisfies: R-BND-001-05 — divergence from the declared register is detectable."""
    findings, _ = parity.compare(["worker"], ["worker", "ghost"], UNAVAILABLE, UNAVAILABLE)
    assert "unregistered" in _kinds(findings)
    assert findings[0]["values"] == ["ghost"]


def test_aligned_populations_are_silent():
    """Negative control. If this ever fails, the check cries wolf and gets muted."""
    findings, _ = parity.compare(["worker", "advisor"], ["worker", "advisor"], UNAVAILABLE, UNAVAILABLE)
    assert findings == []


def test_unimplemented_role_flags():
    findings, _ = parity.compare(["worker", "advisor"], ["worker"], UNAVAILABLE, UNAVAILABLE)
    assert "unimplemented" in _kinds(findings)


def test_sparse_declared_population_is_not_unimplemented():
    """Only the consumer is expected to cover the register.

    Live seats are legitimately a subset -- reporting that as a defect would make
    the check fire permanently and therefore be ignored.
    """
    findings, _ = parity.compare(["worker", "advisor", "analyst"], UNAVAILABLE, UNAVAILABLE, ["worker"])
    assert findings == []


def test_case_collision_flags_and_is_not_a_divergence():
    findings, _ = parity.compare(["worker"], UNAVAILABLE, UNAVAILABLE, ["worker", "Worker"])
    assert _kinds(findings) == {"case_collision"}


def test_separator_variants_fold():
    """research_engineer and research-engineer are one role, not two."""
    findings, _ = parity.compare(["research-engineer"], ["research_engineer"], UNAVAILABLE, UNAVAILABLE)
    assert findings == []


def test_missing_register_yields_no_arbitration_not_false_parity():
    """No authority reachable must not be reported as agreement."""
    findings, available = parity.compare(UNAVAILABLE, ["worker"], UNAVAILABLE, UNAVAILABLE)
    assert findings == []
    assert "register" not in available


# --------------------------------------------------------------------------
# readers: exercised against fixtures, including the mutation the check exists for
# --------------------------------------------------------------------------

def test_read_register_parses_a_fixture(tmp_path):
    fixture = tmp_path / "ARCHETYPE_SKILLS_INDEX.yaml"
    fixture.write_text("archetypes:\n  worker:\n    skill_count: 2\n  advisor:\n    skill_count: 1\n")
    values, err = parity.read_register(fixture)
    assert err is None
    assert values == ["advisor", "worker"]


def test_read_register_reports_unavailable_not_empty(tmp_path):
    """An unreachable register must be UNAVAILABLE, never an empty population.

    An empty population compares equal to nothing and would silently suppress
    every finding -- the failure mode this distinction exists to prevent.
    """
    values, err = parity.read_register(tmp_path / "absent.yaml")
    assert values == UNAVAILABLE
    assert err


def test_read_register_on_malformed_block_is_unavailable(tmp_path):
    fixture = tmp_path / "bad.yaml"
    fixture.write_text("archetypes: not-a-mapping\n")
    values, err = parity.read_register(fixture)
    assert values == UNAVAILABLE


def test_read_consumer_parses_the_literal(tmp_path):
    fixture = tmp_path / "validator.py"
    fixture.write_text(
        'EXTRA = ["x"]\n'
        "ARCHETYPE_EXTRAS = {\n"
        '    "worker": ["a"] + EXTRA,\n'
        '    "advisor": [],\n'
        "}\n"
    )
    values, err = parity.read_consumer(fixture)
    assert err is None
    assert values == ["advisor", "worker"]


def test_read_consumer_missing_literal_is_unavailable(tmp_path):
    fixture = tmp_path / "validator.py"
    fixture.write_text("NOTHING_HERE = 1\n")
    values, _ = parity.read_consumer(fixture)
    assert values == UNAVAILABLE


def test_mutation_injected_register_drop_is_detected(tmp_path):
    """Positive control on real shape: drop one register entry, the check must see it.

    A sweep that returns a clean result without ever being shown a defect it can
    detect proves nothing (the 356-register null result, gh#2363).
    """
    full = tmp_path / "full.yaml"
    full.write_text("archetypes:\n  worker:\n    skill_count: 1\n  advisor:\n    skill_count: 1\n")
    mutated = tmp_path / "mutated.yaml"
    mutated.write_text("archetypes:\n  worker:\n    skill_count: 1\n")

    consumer = ["worker", "advisor"]

    clean, _ = parity.compare(parity.read_register(full)[0], consumer, UNAVAILABLE, UNAVAILABLE)
    assert clean == [], "negative control: unmutated fixture must be silent"

    dirty, _ = parity.compare(parity.read_register(mutated)[0], consumer, UNAVAILABLE, UNAVAILABLE)
    assert "unregistered" in _kinds(dirty), "positive control: the check is blind to its own subject"


# --------------------------------------------------------------------------
# CLI contract
# --------------------------------------------------------------------------

def test_self_test_exits_zero():
    r = subprocess.run([sys.executable, str(SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_json_output_is_parseable_and_carries_authority():
    r = subprocess.run([sys.executable, str(SCRIPT), "--json"], capture_output=True, text=True)
    assert r.returncode in (0, 1), r.stderr
    payload = json.loads(r.stdout)
    assert payload["status"] in {"PARITY", "DIVERGENT", "UNAVAILABLE"}
    assert payload["authority"].endswith("ARCHETYPE_SKILLS_INDEX.yaml")
    assert set(payload["populations"]) == {"register", "consumer", "templates", "declared"}


def test_divergence_exits_nonzero_when_findings_present():
    """The exit code must carry the verdict -- a printed FAIL with exit 0 is not a gate."""
    r = subprocess.run([sys.executable, str(SCRIPT), "--json"], capture_output=True, text=True)
    payload = json.loads(r.stdout)
    expected = 1 if payload["findings"] else 0
    assert r.returncode == expected
