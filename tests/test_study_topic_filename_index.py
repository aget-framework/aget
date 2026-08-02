"""Regression test for the study_topic filename-index gap.

`search_file_for_topic` was content-only: a topic equal to an artifact's
filename slug found 0 matches in that artifact unless the body echoed the slug,
so `find_project_plans` systematically missed plans queried by filename.
Confirmed at source 2026-06-26: `find_project_plans` globs PROJECT_PLAN*.md but
gates inclusion solely on the content match returned by `search_file_for_topic`,
which never inspected `file_path.name`. The fix appends filename tokens (raw +
slug-normalized) to the searchable text. Empirical trigger: a /aget-study-topic
on "PROJECT_PLAN_release_integrity_recurrence_guard" returned 1 tangential L-doc
and missed the plan of that exact name in planning/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import study_topic as st  # noqa: E402

SLUG = "PROJECT_PLAN_release_integrity_recurrence_guard"
FNAME = SLUG + "_v1.0.md"
# body deliberately uses the hyphenated/spaced title, NOT the underscored slug
BODY = "# Release-Integrity Recurrence-Guard\n\nAbstract: installs a guard.\n"


def test_filename_slug_matches_when_body_lacks_it(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "get_agent_root", lambda: tmp_path)
    plan = tmp_path / FNAME
    plan.write_text(BODY)
    match = st.search_file_for_topic(plan, SLUG)
    assert match is not None, "filename-slug topic must surface its own artifact"
    assert match["match_count"] >= 1


def test_normalized_filename_words_match(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "get_agent_root", lambda: tmp_path)
    plan = tmp_path / FNAME
    plan.write_text("# unrelated title only\n")
    match = st.search_file_for_topic(plan, "release integrity guard")
    assert match is not None
    # all three keywords resolvable via the normalized filename stem
    assert match.get("keyword_coverage", 1.0) >= 0.99


def test_unrelated_topic_still_returns_none(tmp_path, monkeypatch):
    # filename matching must not manufacture false positives
    monkeypatch.setattr(st, "get_agent_root", lambda: tmp_path)
    plan = tmp_path / FNAME
    plan.write_text("# unrelated title only\n")
    assert st.search_file_for_topic(plan, "kubernetes helm chart") is None


def test_body_line_numbers_unaffected_by_appended_filename(tmp_path, monkeypatch):
    # appended (not prepended) tokens must leave body context line numbers intact
    monkeypatch.setattr(st, "get_agent_root", lambda: tmp_path)
    plan = tmp_path / FNAME
    plan.write_text("line one\nUNIQUEMARKER here\nline three\n")
    match = st.search_file_for_topic(plan, "UNIQUEMARKER")
    assert match is not None
    assert match["contexts"][0]["line"] == 2
