#!/usr/bin/env python3
"""
Both-polarity contract tests for V-CAP-REL-006-02 (AGET_RELEASE_SPEC v1.18.0).

Every requirement is asserted in BOTH directions: a conformant fixture must PASS and a
targeted-defect fixture must FAIL *for the intended reason*. A test that only ever asserts
the green path cannot detect a check that stopped firing (L671).
"""

import importlib.util
import pathlib
import sys

import pytest

_VALIDATOR = pathlib.Path(__file__).resolve().parents[1] / "verification" / "validate_release_body.py"
_spec = importlib.util.spec_from_file_location("validate_release_body", _VALIDATOR)
vrb = importlib.util.module_from_spec(_spec)
sys.modules["validate_release_body"] = vrb
_spec.loader.exec_module(vrb)


def never_resolves(_url):
    return False


def always_resolves(_url):
    return True


def run(body, title="v3.31.0 — Ship What Was Already Built", resolver=always_resolves):
    return vrb.validate_body("aget-framework/aget", "3.31.0", body, title=title,
                             link_resolver=resolver)


def check(result, sub):
    """Return the single check value whose key carries this sub-requirement number."""
    matches = [v for k, v in result["checks"].items() if k.startswith(f"CAP-REL-006-02-{sub}")]
    assert len(matches) == 1, f"expected exactly one check for -{sub}, got {matches}"
    return matches[0]


CHANGELOG = "https://github.com/aget-framework/aget/blob/main/CHANGELOG.md"

BULLET_BODY = f"""**Theme**: Ship What Was Already Built

## What's New

- First delivered capability landed this cycle.
- Second delivered capability landed this cycle.
- Third delivered capability landed this cycle.
- Fourth delivered capability landed this cycle.
- Fifth delivered capability landed this cycle.

## Compatibility

No breaking changes. See [CHANGELOG]({CHANGELOG}) for full detail.
Downstream agents upgrade in place with no migration step required.
Existing configuration files are read unchanged by this release.
Skill definitions carried forward without edit across the upgrade.
"""

BOLD_LEAD_BODY = f"""**Theme**: Ship What Was Already Built

## What's New

**Contract alignment** — the release-body contract now matches its corpus.

**Validator coverage** — every live sub-requirement emits a keyed result.

**Title validation** — release titles are checked, not merely specified.

**Registered vocabulary** — section names come from a closed registry.

**Scannable grammar** — bullets and bold leads are both conformant.

## Compatibility

No breaking changes. See [CHANGELOG]({CHANGELOG}) for full detail.
Downstream agents upgrade in place with no migration step required.
Existing configuration files are read unchanged by this release.
Skill definitions carried forward without edit across the upgrade.
"""


# --- SC-2: both renderings are conformant -----------------------------------------------

def test_bullet_form_passes():
    assert check(run(BULLET_BODY), "02").startswith("PASS")


def test_bold_lead_form_passes():
    """The v3.28.0 regression: 16 bounded bold-lead items failed a bullet-only check (L1264)."""
    assert check(run(BOLD_LEAD_BODY), "02").startswith("PASS")


def test_mixed_rendering_passes():
    mixed = BULLET_BODY.replace(
        "- Fifth delivered capability landed this cycle.",
        "**Fifth capability** — landed this cycle.",
    )
    assert check(run(mixed), "02").startswith("PASS")


def test_prose_paragraph_is_not_a_scannable_item():
    prose = BULLET_BODY.replace(
        "- First delivered capability landed this cycle.",
        "This release delivers a capability, described here in prose without a bold lead.",
    )
    assert check(run(prose), "02").startswith("FAIL")


@pytest.mark.parametrize("count,expect", [(4, "FAIL"), (5, "PASS"), (10, "PASS"), (11, "FAIL")])
def test_item_count_bounds_both_polarities(count, expect):
    items = "\n".join(f"- Delivered capability number {i}." for i in range(count))
    body = f"""**Theme**: Bounds

## What's New

{items}

## Compatibility

No breaking changes. See [CHANGELOG]({CHANGELOG}).
Downstream agents upgrade in place with no migration step.
Existing configuration files are read unchanged.
Skill definitions carry forward without edit.
"""
    assert check(run(body), "02").startswith(expect)


def test_overlong_item_fails():
    body = BULLET_BODY.replace(
        "- First delivered capability landed this cycle.",
        "- First capability\n  continued onto a second line\n  and then a third line.",
    )
    assert check(run(body), "02").startswith("FAIL")


# --- SC-3: core pair required, no fixed total-section count -----------------------------

def test_core_pair_present_passes():
    assert check(run(BULLET_BODY), "08").startswith("PASS")


def test_two_sections_passes_no_fixed_count():
    """The old rule demanded exactly 3 H2s; 2 is conformant when both are core (v3.26.0)."""
    result = run(BULLET_BODY)
    assert check(result, "08").startswith("PASS")


def test_four_sections_passes_no_fixed_count():
    body = BULLET_BODY + "\n## Migration\n\nFollow the upgrade note.\n\n## Known gaps\n\nOne gap remains.\n"
    assert check(run(body), "08").startswith("PASS")


def test_missing_whats_new_fails():
    body = BULLET_BODY.replace("## What's New", "## Overview")
    assert "what's new" in check(run(body), "08").lower()
    assert check(run(body), "08").startswith("FAIL")


def test_missing_compatibility_fails():
    body = BULLET_BODY.replace("## Compatibility", "## Notes").replace("No breaking changes. ", "")
    assert check(run(body), "08").startswith("FAIL")


# --- -04: registered vocabulary ---------------------------------------------------------

def test_registered_disclosure_passes():
    body = BULLET_BODY + "\n## Known gaps\n\nOne limitation ships with this release.\n"
    assert check(run(body), "04").startswith("PASS")


def test_registered_alternate_label_passes():
    body = BULLET_BODY + "\n## Disclosed limitations\n\nOne limitation ships.\n"
    assert check(run(body), "04").startswith("PASS")


def test_unregistered_section_name_fails():
    """'(or equivalent)' was withdrawn in v1.18.0 — an unlisted name is a FAIL, not a variant."""
    body = BULLET_BODY + "\n## Honest disclosure\n\nSomething undisclosed.\n"
    assert check(run(body), "04").startswith("FAIL")


def test_sleeping_caps_mentioned_without_section_fails():
    body = BULLET_BODY.replace(
        "- First delivered capability landed this cycle.",
        "- One SPEC-LANDED-IMPL-DEFERRED capability ships asleep.",
    )
    assert check(run(body), "04").startswith("FAIL")


def test_migration_is_structural_not_disclosure():
    """v3.28.0-v3.30.0 carry ## Migration; a disclosure-only registry would fail all three."""
    body = BULLET_BODY + "\n## Migration\n\nFollow the upgrade note.\n"
    assert check(run(body), "04").startswith("PASS")
    assert check(run(body), "08").startswith("PASS")


# --- -09: title, both polarities --------------------------------------------------------

def test_title_conformant_passes():
    assert check(run(BULLET_BODY, title="v3.31.0 — Ship What Was Already Built"), "09").startswith("PASS")


def test_title_hyphen_form_passes():
    assert check(run(BULLET_BODY, title="v3.31.0 - Ship What Was Already Built"), "09").startswith("PASS")


def test_title_duplicated_version_fails():
    """The v3.17 anomaly: 'v3.17.0 - v3.17.0 — Theme C3...'."""
    assert check(run(BULLET_BODY, title="v3.31.0 - v3.31.0 — Ship It"), "09").startswith("FAIL")


def test_title_missing_version_fails():
    assert check(run(BULLET_BODY, title="Ship What Was Already Built"), "09").startswith("FAIL")


# --- SC-1: coverage — the check that would have caught the -09 stub ----------------------

def test_all_eight_live_subrequirements_emit_a_result():
    """
    The shipped validator emitted seven checks and silently omitted -09, so a reader counting
    green checks saw PASS with no signal a requirement went unevaluated (L671).
    """
    result = run(BULLET_BODY)
    emitted = {k.split("_")[0].rsplit("-", 1)[1] for k in result["checks"]}
    assert emitted == set(vrb.LIVE_SUBREQUIREMENTS), f"missing: {set(vrb.LIVE_SUBREQUIREMENTS) - emitted}"
    assert len(result["checks"]) == 8


def test_withdrawn_06_is_not_emitted():
    assert not any("-06" in k for k in run(BULLET_BODY)["checks"])


def test_absent_title_emits_unavailable_not_omission():
    """An unevaluable check must announce itself rather than vanish."""
    result = run(BULLET_BODY, title=None)
    assert check(result, "09").startswith("UNAVAILABLE")
    assert len(result["checks"]) == 8
    assert result["overall"] == "UNAVAILABLE"


# --- -05 link resolution, both polarities -----------------------------------------------

def test_link_resolves_passes():
    assert check(run(BULLET_BODY, resolver=always_resolves), "05").startswith("PASS")


def test_link_unresolvable_fails():
    assert check(run(BULLET_BODY, resolver=never_resolves), "05").startswith("FAIL")


def test_no_link_fails():
    body = BULLET_BODY.replace(f"[CHANGELOG]({CHANGELOG})", "the changelog")
    assert check(run(body), "05").startswith("FAIL")


# --- -01 / -07 --------------------------------------------------------------------------

def test_theme_present_passes():
    assert check(run(BULLET_BODY), "01").startswith("PASS")


def test_theme_absent_fails():
    assert check(run(BULLET_BODY.replace("**Theme**: Ship What Was Already Built", "Ship it")), "01").startswith("FAIL")


@pytest.mark.parametrize("filler,expect", [(0, "FAIL"), (8, "PASS")])
def test_length_bounds_both_polarities(filler, expect):
    body = f"""**Theme**: Bounds

## What's New

- One.
- Two.
- Three.
- Four.
- Five.

## Compatibility

No breaking changes. See [CHANGELOG]({CHANGELOG}).
""" + "".join(f"Additional compatibility note number {i}.\n" for i in range(filler))
    assert check(run(body), "07").startswith(expect)
