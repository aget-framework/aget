"""CANONICAL COPY (2026-09-19): the two corpus tests that glob the instance seat's
governance/RULING*_*.md register (author-naming floor of 50) are omitted here -- they
measure one seat's corpus, not the pattern. They live at private-aget-framework-AGET.
Everything below is pure pattern behaviour and runs at any seat.
"""

"""Both-polarity guard on principal-attribution detection.

Defect fixed 2026-08-28. The pattern listed `ruled|rule` but not the plain GERUND,
and its possessive branch required the `s` (`principal'?s`). So "principal's ruling"
matched and "principal ruling" did not.

Impact measured at repair time: 123 files under governance/, planning/, docs/ and
sops/ contained genuine principal attribution that this pattern could not see --
including three files whose entire purpose is recording principal rulings. The guard
that reads this pattern decides whether a close is authorised.

The negative cases matter as much as the positive ones: widening a pattern until it
matches everything is not a fix, it is a disabled check.
"""
import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _pattern():
    spec = importlib.util.spec_from_file_location(
        "cag", REPO / "scripts" / "close_authorization_guard.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.PRINCIPAL_ATTRIB


@pytest.mark.parametrize("text", [
    "principal ruling",          # THE regression case
    "principal-ruling",
    "Principal Ruling",
    "principal's ruling",
    "principal ruled",
    "principal rule",
    "per principal",
    "ruled by the principal",
    "authorised by principal",
    "principal decision",
    "principal selected",
    "principal directive",
])
def test_attribution_forms_are_matched(text):
    """Satisfies: R-DEC-001-01 — a decision record names whoever decided; the
    principal branch is one of the two author branches. (Was R-BND-001-01, which governs
    cross-boundary reliance contracts, not decision records — see the corpus test below.)"""
    assert _pattern().search(text), f"blind to {text!r}"


@pytest.mark.parametrize("text", [
    "the principal is asleep",
    "municipal ruling",
    "principle ruling",          # different word entirely
    "ruling by committee",
    "principals meeting",
    "a ruling was issued",
])
def test_non_attribution_is_rejected(text):
    """POSITIVE control on the negative. A pattern that matches everything
    attributes everything, which is worse than a blind spot."""
    assert not _pattern().search(text), f"false positive on {text!r}"


@pytest.mark.parametrize("text", [
    "principal GO",                                   # THE 2026-09-19 regression case (node-1)
    "Ceremony performed under principal GO.",
    "principal GO 2026-09-19",
    "principal's GO",
    "principal-typed GO",
    "principal typed `--go`",
    "GO from the principal",
    "GO by the principal",
])
def test_go_attribution_forms_are_matched(text):
    """A principal GO is the fleet's most common authorization act. The guard read
    'under principal GO' as agent-autonomous on 2026-09-19 at node-1 and PASSED the close
    on the wrong ground."""
    assert _pattern().search(text), f"blind to {text!r}"


@pytest.mark.parametrize("text", [
    "let the principal go",
    "the principal goes home",
    "principal go-live gate",
    "principal government",
    "the principal is going",
    "gone by the principal",
])
def test_go_is_case_sensitive_and_bounded(text):
    """The GO token is uppercase-only and word-bounded. Widening it to 'go' would
    attribute every sentence in which the principal leaves the room."""
    assert not _pattern().search(text), f"false positive on {text!r}"


def test_the_specific_regression_case_is_pinned():
    """Named separately so a future widening cannot quietly drop it."""
    p = _pattern()
    assert p.search("principal ruling")
    assert p.search("This was settled by principal ruling on 2026-08-28.")


AGENT_ATTRIB = re.compile(
    r"\*\*(decided|ruled|authored)\s+by\*\*\s*:|\bI am ruling\b|\bthis agent seat\b",
    re.IGNORECASE,
)

# The corpus floor. 50 records carried an author on 2026-09-17, the day the predicate below
# changed from "names the principal" to "names an author". The floor exists because the
# CHEAPEST way to clear an authorship failure is to rename the offending record out of the
# family -- which is exactly what happened that day, correctly, on a principal ruling, and
# which treats the instance while leaving the premise. A rename-to-green now drops the count
# and reds this test. Raising the floor is a deliberate act; lowering it is the escape.
CORPUS_FLOOR = 50


def _names_an_author(text: str) -> bool:
    """Does this record name WHO DECIDED -- principal or agent -- rather than nobody?"""
    return bool(_pattern().search(text) or AGENT_ATTRIB.search(text))


def test_an_agent_authored_record_satisfies_the_check():
    """The case that produced the 2026-09-17 CI red: a record naming an AGENT as decider."""
    assert _names_an_author("**Decided by**: this agent seat, within its own authority.")
    assert _names_an_author("Split. The part that is mine, I am ruling now.")


def test_a_record_naming_nobody_still_fails():
    """POSITIVE CONTROL. A predicate widened until everything passes attributes nothing."""
    assert not _names_an_author("# A record\n\nNothing here names who decided.")
    assert not _names_an_author("a ruling was issued by the committee")


@pytest.mark.parametrize("text", [
    "**Ruled by**: principal",        # THE 2026-09-06 regression case, verbatim header form
    "**Ruled by**: the principal",
    "Decided by: principal",
    '"authorized_by":"principal"',   # JSON record form, 2 in corpus
])
def test_markdown_header_attribution_is_matched(text):
    """Satisfies: R-DEC-001-01 — the passive branch must survive markdown emphasis.
    (Was R-BND-001-01; re-pointed with the rest of this module.)

    Every separator here was DERIVED FROM THE CORPUS, not invented: a dash form was drafted,
    grepped for, found zero times, and dropped rather than widening the pattern for it.
    Both rulings files in governance/ write attribution as `**Ruled by**: principal`. A bare
    `\\s+by\\s+principal` cannot span the `**` and `:`, so the canonical header form read as
    UNATTRIBUTED. One file passed anyway, on unrelated body prose — which is worse than failing,
    because it made the blind spot look like a one-file problem.
    """
    assert _pattern().search(text), f"blind to the header form {text!r}"


@pytest.mark.parametrize("text", [
    "a ruling was issued by the committee",
    "approved by the board",
    "selected by a principal component analysis",
])
def test_widening_the_separator_did_not_disable_the_check(text):
    """POSITIVE control on the 2026-09-06 widening (R-DEC-001-03; was R-BND-001-01).

    The separator class is punctuation-and-space only. If it ever becomes `.*`, these pass and
    the guard attributes everything — which the module docstring already names as the failure
    mode worse than a blind spot.
    """
    assert not _pattern().search(text), f"false positive on {text!r}"
