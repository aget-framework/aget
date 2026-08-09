"""
Regression guard: the spec tier must SURVIVE scoring, not merely be found.

WHY THIS FILE EXISTS, stated precisely because the failure repeated.

`find_specs` was added to close gh#1580 — a surface CLAIMED in the printed
banner while no finder populated it, so every study reported "0 specs" and a
reader trusting the banner read that as "no spec exists". The function's own
docstring names this "manufactured absence" and says it is closed.

It was not closed. The finder was restored and the SCORING path re-zeroed it.
Measured 2026-08-05: `find_specs('proposal')` returned 62 results while the
rendered report printed `| Specs | 0 | - |`, because main() re-scores every item
through composite_score() and find_specs emitted two fields no other finder
emitted:

  1. `matches` instead of `match_count` — composite_score reads `match_count`
     and defaults it to 1, collapsing the log-damped count term.
  2. `keyword_coverage` defaulting to 0.0 instead of 1.0 — and
     search_file_for_topic OMITS that key for single-token topics, so the
     default IS the value. composite_score multiplies by it, so every spec
     scored exactly 0.0 and fell below RELEVANCE_FLOOR_DEFAULT.

Consequence measured the same day at a peer seat: asked for the formal
definition of "proposal", it reported no formal definition had ever been
written, while AGET_CHANGE_PROPOSAL_SPEC v1.2.0 (CAP-CP-001..005, 12 V-tests)
sat in canonical. The instrument supplied false evidence of non-existence.

THE LESSON THIS FILE ENCODES: a finder test is not a tier test. Asserting that
find_specs() returns rows proves nothing about what the reader sees, because the
defect lived entirely downstream of the finder. Every assertion below therefore
runs the FULL pipeline and reads the RENDERED output — the surface a human
actually trusts.

Both polarities are asserted. A test that only proves specs appear would pass if
the floor were deleted outright, which would reintroduce the noise the floor
exists to suppress. See feedback: "a check whose predicate cannot detect its
subject" and "assert both polarities".
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "study_topic.py"

# A topic guaranteed to hit the spec tier: AGET_CHANGE_PROPOSAL_SPEC and
# AGET_INITIATIVE_SPEC both carry it heavily.
HIT_TOPIC = "proposal"
# A token chosen to exist nowhere in the corpus.
MISS_TOPIC = "zzzznonexistenttoken"


def run_study(topic, *extra):
    """Run the full pipeline exactly as a session would, and return stdout."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--topic", topic, *extra],
        cwd=str(REPO), capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, f"study_topic.py failed: {proc.stderr[-800:]}"
    return proc.stdout


def specs_count_from_summary(report):
    """Parse the Summary table's Specs row — the number the reader sees."""
    for line in report.splitlines():
        if line.startswith("| Specs "):
            return int(line.split("|")[2].strip())
    pytest.fail("Summary table has no Specs row at all — the tier vanished "
                "from the report rather than reporting zero")


class TestSpecsTierSurvivesScoring:
    """The regression that the finder-level fix did not catch."""

    def test_specs_survive_the_default_relevance_floor(self):
        """Verifies CAP-SESSION-007-06 (gh#1580 manufactured-absence). POSITIVE POLARITY — the defect's direct falsifier.

        This is the assertion that was false on 2026-08-05 while find_specs()
        itself worked. It must run WITHOUT --no-floor: the bug was invisible to
        any test that escaped the floor, which is how it shipped.
        """
        count = specs_count_from_summary(run_study(HIT_TOPIC))
        assert count > 0, (
            "Specs tier is zero on a topic with dozens of spec hits. The finder "
            "may still work — check composite_score() inputs in find_specs(): "
            "it must emit `match_count` (not only `matches`) and must default "
            "`keyword_coverage` to 1.0, matching every other finder. A 0 here "
            "is manufactured absence, the gh#1580 failure mode."
        )

    def test_the_definitional_spec_is_actually_reachable(self):
        """Verifies CAP-SESSION-007-06 (gh#1580 manufactured-absence). Counting rows is not the same as surfacing the right row.

        A tier could pass the count assertion while ranking the one spec a
        reader needs below the render cutoff. This pins the specific artifact
        whose absence produced the wrong peer answer.
        """
        report = run_study(HIT_TOPIC)
        assert "AGET_CHANGE_PROPOSAL_SPEC" in report, (
            "AGET_CHANGE_PROPOSAL_SPEC is the only formal definition of a "
            "proposal class in the framework. If a study on 'proposal' cannot "
            "surface it, the study will report that no formal definition exists."
        )

    def test_specs_are_rendered_not_merely_counted(self):
        """Verifies CAP-SESSION-007-07 (gh#1580 manufactured-absence). The Summary count and the rendered section must agree.

        generate_report() renders the specs section from a separate loop over
        findings['specs']. A count without a section is a tier that is tallied
        and then dropped before the reader.
        """
        report = run_study(HIT_TOPIC)
        assert "### Related Specifications" in report, (
            "Summary counts specs but no '### Related Specifications' section "
            "was rendered — the tier is tallied and dropped."
        )

    def test_absent_topic_still_yields_zero(self):
        """Verifies CAP-SESSION-007-06 (gh#1580 manufactured-absence). NEGATIVE POLARITY — the fix must not manufacture presence.

        Without this, deleting the relevance floor entirely would pass every
        assertion above. Manufactured presence is the mirror defect of
        manufactured absence and is equally a false claim about the corpus.
        """
        count = specs_count_from_summary(run_study(MISS_TOPIC))
        assert count == 0, (
            f"A token absent from the corpus returned {count} specs. The fix "
            "has over-corrected: coverage/score inputs must not float every "
            "spec above the floor regardless of relevance."
        )

    def test_floor_still_discriminates_within_the_specs_tier(self):
        """Verifies CAP-SESSION-007-07 (gh#1580 manufactured-absence). The floor must do real work on specs, not be bypassed for them.

        Before the fix, --no-floor was the ONLY way to see specs (0 vs 62).
        After a correct fix the floor should suppress SOME specs but not all —
        if floored == unfloored, the tier has been exempted from scoring rather
        than scored correctly, which trades one silent behaviour for another.
        """
        floored = specs_count_from_summary(run_study(HIT_TOPIC))
        unfloored = specs_count_from_summary(run_study(HIT_TOPIC, "--no-floor"))
        assert 0 < floored <= unfloored, (
            f"floored={floored} unfloored={unfloored} — expected the floor to "
            "retain a nonzero subset."
        )
        assert floored < unfloored, (
            "The relevance floor suppresses no specs at all. Either the corpus "
            "has no low-relevance specs (unlikely) or the specs tier is being "
            "exempted from the floor instead of scored by it."
        )


class TestFindSpecsEmissionContract:
    """Field-shape contract — the proximate cause, pinned directly.

    The tier-level tests above would catch a regression, but only by symptom.
    These name the two fields, so a future edit that reintroduces either one
    fails with a message that says which.
    """

    @pytest.fixture(scope="class")
    def specs(self):
        sys.path.insert(0, str(REPO / "scripts"))
        import study_topic as st
        rows = st.find_specs(HIT_TOPIC)
        assert rows, "find_specs returned nothing — precondition for this class"
        return rows

    def test_emits_match_count_like_every_other_finder(self, specs):
        missing = [r for r in specs if "match_count" not in r]
        assert not missing, (
            f"{len(missing)}/{len(specs)} spec rows lack `match_count`. "
            "composite_score() reads that key and defaults it to 1, so the "
            "log-damped count term silently collapses for the whole tier."
        )

    def test_coverage_default_matches_the_other_finders(self, specs):
        """Verifies CAP-SESSION-007-06 (gh#1580 manufactured-absence). search_file_for_topic omits keyword_coverage for single-token topics,
        so the DEFAULT is the operative value — 0.0 zeroes the product."""
        zeroed = [r for r in specs if r.get("keyword_coverage") == 0.0]
        assert not zeroed, (
            f"{len(zeroed)}/{len(specs)} spec rows carry keyword_coverage=0.0. "
            "composite_score() multiplies by this, so those rows score exactly "
            "0.0 and are suppressed by any positive floor. Default must be 1.0, "
            "matching find_ldocs/find_governance/find_knowledge."
        )

    def test_scores_clear_the_configured_floor(self, specs):
        sys.path.insert(0, str(REPO / "scripts"))
        import study_topic as st
        scored = [st.composite_score(r) for r in specs]
        floor = st.RELEVANCE_FLOOR_DEFAULT
        assert max(scored) >= floor, (
            f"Top spec composite score {max(scored):.3f} is below the floor "
            f"{floor}. The entire tier will be suppressed and the report will "
            "print a confident zero."
        )
