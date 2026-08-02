"""Tests for the #1560 relevance-floor in study_topic.generate_report.

Gate 2 (re-opened), PROJECT_PLAN_research_capability_first_rung_v1.0. Build V-tests (L625).
The floor buckets the Recommendation on the RELEVANT count (keyword_coverage >=
0.5), not raw total, so token-noise over-matches don't read as "good coverage".
keyword_coverage is now propagated through every finder (the F-G2-A fix).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import study_topic as st  # noqa: E402


def _ldocs(coverages):
    """Build a findings dict using the REAL ldoc finding schema (key 'ldoc')."""
    return {
        "ldocs": [
            {"ldoc": f"L{i}", "title": f"Title {i}", "file": f"L{i}.md",
             "match_count": 3, "keyword_coverage": c, "domain_boost": 1.0}
            for i, c in enumerate(coverages)
        ],
        "patterns": [], "project_plans": [], "sops": [], "governance": [],
    }


def _recommendation(report):
    return report.split("### Recommendation", 1)[1]


def test_noise_input_not_good_coverage():
    """R-TEST-001-02: low-coverage noise must not read as good coverage."""
    rec = _recommendation(st.generate_report("test app as an aget", _ldocs([0.1] * 50)))
    assert "Good coverage" not in rec
    assert "novel topic" in rec
    assert "50 raw hits" in rec


def test_genuine_hits_reported_as_relevant_count():
    """R-TEST-001-02: several high-coverage hits report the relevant count — WITHOUT a quality
    adjective. Updated 2026-07-10 (v3.26 C-26-11, audit C1 ruling): 'Good
    coverage' was the defect's carrier — a quality claim the tool cannot
    demonstrate — so the contract-derived line replaced it. The substance this
    test guards (relevant count surfaces; noise never inflates it) is unchanged."""
    rec = _recommendation(st.generate_report("codex native app", _ldocs([0.8, 0.9, 1.0, 0.7])))
    assert "4 relevant" in rec
    assert "Good coverage" not in rec


def test_mixed_reports_relevant_and_noise():
    """R-TEST-001-02: a mix separates relevant hits from filtered noise."""
    rec = _recommendation(st.generate_report("x", _ldocs([0.9, 0.6, 0.2, 0.1, 0.1])))  # 2 relevant
    assert "2 relevant" in rec
    assert "3 additional raw hits" in rec


def test_single_keyword_topics_unaffected():
    """R-TEST-001-02: single-keyword findings remain relevant."""
    f = {"ldocs": [{"ldoc": "L1", "title": "T1", "file": "L1.md", "match_count": 5}],
         "patterns": [], "project_plans": [], "sops": [], "governance": []}
    rec = _recommendation(st.generate_report("release", f))
    assert "1 relevant artifact" in rec


def test_zero_total_still_novel():
    """R-TEST-001-02: zero findings retain the novel-topic result."""
    f = {"ldocs": [], "patterns": [], "project_plans": [], "sops": [], "governance": []}
    rec = _recommendation(st.generate_report("brand new", f))
    assert "novel topic" in rec


def test_coverage_propagated_through_finder():
    """R-TEST-001-02: finders propagate the keyword-coverage signal."""
    import inspect
    assert "keyword_coverage" in inspect.getsource(st.find_ldocs)
    assert "keyword_coverage" in inspect.getsource(st.find_governance)
