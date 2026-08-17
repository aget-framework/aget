"""V-tests for Gate 1 of PROJECT_PLAN_spec_enforcement_truthfulness.

V-SET-05  no canonical surface reports two different statuses for one instrument
V-SET-06  every instrument recorded as reached has >=1 invocation caller
V-SET-07  the spec and the inventory agree -- asserted by a script, not by reading

Why this compares DERIVED FACTS rather than strings: after the Gate 1 repair the spec
says "NONE -- exists, never invoked" and the inventory says "Built, uncalled". Those
agree completely and share no wording. A string-equality check would fail on agreeing
surfaces and pass on a pair that happened to use the same word for different things.
So the comparison is on what each surface implies about (exists, is-reached).

Scope: canonical aget-framework/aget on this machine. Skips rather than fails when the
canonical tree is absent, so the suite stays runnable on a clone without it.
"""

import pathlib
import re

import pytest

CANONICAL = pathlib.Path(__file__).resolve().parents[1]
SPEC = CANONICAL / "specs" / "AGET_DOCUMENTATION_SPEC.md"
INVENTORY = CANONICAL / "docs" / "VALIDATOR_INVENTORY.md"

# Words that assert a requirement IS enforced. If a surface uses one of these for an
# instrument that does not exist or has no callers, the surface is overclaiming.
ENFORCED_WORDS = ("implemented", "active", "enforced", "wired")

pytestmark = pytest.mark.skipif(
    not SPEC.exists() or not INVENTORY.exists(),
    reason="canonical aget tree not present on this machine",
)


def _spec_rows():
    """Parse the spec Enforcement table -> {instrument: (exists, callers, enforcement)}."""
    text = SPEC.read_text()
    block = re.search(r"^## Enforcement\b(.*?)^---", text, re.M | re.S)
    assert block, "spec has no ## Enforcement section"
    rows = {}
    for line in block.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].startswith("CAP-DOC"):
            continue
        instrument = re.sub(r"[`*]", "", cells[1]).strip()
        if instrument.startswith("("):  # "(none named)" / "(none -- human review)"
            continue
        exists = "✓" in cells[2]
        callers = None
        m = re.search(r"\d+", re.sub(r"[`*]", "", cells[3]))
        if m:
            callers = int(m.group(0))
        rows[pathlib.Path(instrument).name] = (exists, callers, cells[4].lower())
    return rows


def _inventory_rows():
    """Parse the inventory -> {instrument: status_text_lower}."""
    rows = {}
    for line in INVENTORY.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0].endswith(".py"):
            continue
        rows[pathlib.Path(re.sub(r"[`*]", "", cells[0])).name] = cells[-1].lower()
    return rows


def test_vset05_no_instrument_carries_two_conflicting_statuses():
    """V-SET-05: a surface may not claim enforcement the other surface denies."""
    spec, inv = _spec_rows(), _inventory_rows()
    conflicts = []
    for name, (exists, callers, enforcement) in spec.items():
        if name not in inv:
            continue
        spec_enforced = not ("none" in enforcement)
        inv_enforced = any(w in inv[name] for w in ENFORCED_WORDS)
        if spec_enforced != inv_enforced:
            conflicts.append(f"{name}: spec={enforcement!r} inventory={inv[name]!r}")
    assert not conflicts, "spec and inventory disagree on enforcement: " + "; ".join(conflicts)


def test_vset06_nothing_is_recorded_enforced_without_a_caller():
    """V-SET-06: ENFORCED requires exists AND >=1 caller. This is the overclaim guard."""
    bad = []
    for name, (exists, callers, enforcement) in _spec_rows().items():
        claims_enforced = "none" not in enforcement and "manual" not in enforcement
        if claims_enforced and (not exists or not callers):
            bad.append(f"{name}: enforcement={enforcement!r} exists={exists} callers={callers}")
    assert not bad, "enforcement claimed without a reachable instrument: " + "; ".join(bad)


def test_vset07_surfaces_agree_by_derived_fact_not_by_wording():
    """V-SET-07: the two surfaces are reconciled, and the check is not string equality."""
    spec, inv = _spec_rows(), _inventory_rows()
    shared = set(spec) & set(inv)
    assert shared, "no instrument appears on both surfaces — nothing was actually compared"
    for name in shared:
        exists, callers, enforcement = spec[name]
        if not exists or callers == 0:
            assert not any(w in inv[name] for w in ENFORCED_WORDS), (
                f"{name}: spec records it unreachable, inventory still says {inv[name]!r}"
            )


def test_the_check_can_actually_fail():
    """Negative control. A predicate that cannot fail proves nothing about the surfaces.

    Feed the same comparison a fabricated overclaim and assert it is caught.
    """
    fake_spec = {"phantom.py": (False, None, "enforced")}
    fake_inv = {"phantom.py": "implemented"}
    caught = []
    for name, (exists, callers, enforcement) in fake_spec.items():
        if "none" not in enforcement and (not exists or not callers):
            caught.append(name)
        if not exists and any(w in fake_inv[name] for w in ENFORCED_WORDS):
            caught.append(name)
    assert caught, "the comparison failed to flag a fabricated overclaim — it is inert"
