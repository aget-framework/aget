"""Red fixtures for the /aget-propose-actions deferral scan (REQ-PA-012; gh#2676, gh#2426).

Written at Gate 0 of planning/PROJECT_PLAN_v3.35.0_value_row_propose_actions_repairs_v1.0.md,
BEFORE the implementation existed: each behavioural test ran red (strict xfail) on 2026-09-24
at 09:40, and went green at Gate 1 when scripts/propose_actions_handoff_scan.py landed and the
markers were removed. The two
`test_prescribed_*` tests characterise the defects in the selectors the skill prescribes today;
they pass now and keep passing, because they test the old selectors, not the new scan.

Population contract (gh#2676): deferral markers are DOCUMENTS ON DISK, not commits, and never
filesystem mtime. Candidates = committed handoffs whose last author date is inside the window,
plus untracked or locally modified handoffs (no authored date to filter on, so in-window).
Location contract (gh#2426): locations are configurable; the release-class `handoffs/` directory
is excluded by default. Three-state contract: "no candidates", "none matched" and "could not look"
must never render identically.
"""

import importlib.util
import os
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "propose_actions_handoff_scan.py"


def _load():
    if not SCRIPT.exists():
        pytest.fail(f"not implemented: {SCRIPT.name} does not exist")
    spec = importlib.util.spec_from_file_location("propose_actions_handoff_scan", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo, *args, env=None):
    e = dict(os.environ)
    e.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
              "GIT_COMMITTER_EMAIL": "t@t"})
    if env:
        e.update(env)
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, env=e)


def _repo(tmp_path):
    repo = tmp_path / "seat"
    repo.mkdir()
    _git(repo, "init", "-q")
    return repo


def _commit_file(repo, rel, text, days_ago):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    _git(repo, "add", rel)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - days_ago * 86400))
    _git(repo, "commit", "-q", "-m", f"add {rel}",
         env={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
    os.utime(p, None)  # a fresh clone rewrites mtime to "now"; the scan must not care
    return p


# ---- characterisation of today's prescribed selectors (pass now, keep passing) ----------------

def test_prescribed_mtime_selector_overcounts_after_fresh_clone(tmp_path):
    """Satisfies: REQ-PA-012 -- characterises the prescribed -mtime selector's fail-closed defect (gh#2676)."""
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_old.md", "deferred: subject-x\n", days_ago=40)
    out = subprocess.run(["find", str(repo / "docs"), "-name", "HANDOFF_*.md", "-mtime", "-14"],
                         capture_output=True, text=True, check=True).stdout
    assert "HANDOFF_old.md" in out, "the -mtime selector treats a 40-day-old handoff as recent"


def test_prescribed_commit_history_selector_misses_untracked(tmp_path):
    """Satisfies: REQ-PA-012 -- characterises the commit-history selector's fail-open defect (gh#2676)."""
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_seed.md", "seed\n", days_ago=1)
    (repo / "docs" / "HANDOFF_new.md").write_text("deferred: subject-y\n")
    out = _git(repo, "log", "--since=14 days ago", "--name-only", "--format=",
               "--", "docs/HANDOFF_*.md").stdout
    assert "HANDOFF_new.md" not in out, "the commit-history selector cannot see an untracked handoff"


# ---- required behaviour of the new scan (red now) --------------------------------------------

def test_old_committed_handoff_is_outside_window_even_after_fresh_clone(tmp_path):
    """Satisfies: REQ-PA-012 -- old committed handoff is outside window even after fresh clone."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_old.md", "deferred: subject-x\n", days_ago=40)
    r = m.scan(repo, subjects=["subject-x"], days=14)
    assert r["verdict"] == "NO-CANDIDATES", r


def test_recent_committed_handoff_matches(tmp_path):
    """Satisfies: REQ-PA-012 -- recent committed handoff matches."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_recent.md", "parked: subject-x\n", days_ago=3)
    r = m.scan(repo, subjects=["subject-x"], days=14)
    assert r["verdict"] == "MATCHED" and r["matches"][0]["subject"] == "subject-x", r


def test_untracked_handoff_is_a_candidate_and_matches(tmp_path):
    """Satisfies: REQ-PA-012 -- untracked handoff is a candidate and matches."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/README.md", "x\n", days_ago=1)
    (repo / "docs" / "HANDOFF_new.md").write_text("deferred: subject-y\n")
    r = m.scan(repo, subjects=["subject-y"], days=14)
    assert r["verdict"] == "MATCHED", r
    assert r["matches"][0]["tracked"] is False, r


def test_old_but_locally_modified_handoff_is_a_candidate(tmp_path):
    """Satisfies: REQ-PA-012 -- old but locally modified handoff is a candidate."""
    m = _load()
    repo = _repo(tmp_path)
    p = _commit_file(repo, "docs/HANDOFF_old.md", "old\n", days_ago=40)
    p.write_text("old\nre-parked today: subject-z\n")
    r = m.scan(repo, subjects=["subject-z"], days=14)
    assert r["verdict"] == "MATCHED", r


def test_handoffs_outside_docs_are_scanned_by_default(tmp_path):
    """Satisfies: REQ-PA-012 -- handoffs outside docs are scanned by default."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "planning/HANDOFF_a.md", "deferred: alpha\n", days_ago=2)
    _commit_file(repo, "inbox/outbound/HANDOFF_b.md", "deferred: beta\n", days_ago=2)
    r = m.scan(repo, subjects=["alpha", "beta"], days=14)
    assert r["verdict"] == "MATCHED", r
    assert {x["subject"] for x in r["matches"]} == {"alpha", "beta"}, r


def test_release_class_handoffs_are_excluded_by_default(tmp_path):
    """Satisfies: REQ-PA-012 -- release class handoffs are excluded by default."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/README.md", "x\n", days_ago=1)
    _commit_file(repo, "handoffs/RELEASE_HANDOFF_v9.md", "mentions subject-r\n", days_ago=1)
    r = m.scan(repo, subjects=["subject-r"], days=14)
    assert r["verdict"] != "MATCHED", r


def test_locations_are_configurable(tmp_path):
    """Satisfies: REQ-PA-012 -- handoff locations are configurable per Aget (gh#2426)."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "notes/HANDOFF_c.md", "deferred: gamma\n", days_ago=2)
    assert m.scan(repo, subjects=["gamma"], days=14)["verdict"] != "MATCHED"
    r = m.scan(repo, subjects=["gamma"], days=14, locations=["notes"])
    assert r["verdict"] == "MATCHED", r


def test_three_states_are_distinct(tmp_path):
    """Satisfies: REQ-PA-012 -- no candidates, none matched and could-not-look render differently (gh#2426)."""
    m = _load()
    repo = _repo(tmp_path)
    # no configured location exists: the guard could not look anywhere
    r_none = m.scan(repo, subjects=["s"], days=14)
    assert r_none["verdict"] == "UNAVAILABLE" and r_none["reason"], r_none
    # a location exists, but holds no candidate in the window
    _commit_file(repo, "docs/README.md", "x\n", days_ago=1)
    r_empty = m.scan(repo, subjects=["s"], days=14)
    assert r_empty["verdict"] == "NO-CANDIDATES", r_empty
    # candidates exist, none matches
    _commit_file(repo, "docs/HANDOFF_d.md", "unrelated\n", days_ago=1)
    r_miss = m.scan(repo, subjects=["s-absent"], days=14)
    assert r_miss["verdict"] == "NONE-MATCHED" and r_miss["candidates"] == 1, r_miss
    assert len({r_none["verdict"], r_empty["verdict"], r_miss["verdict"]}) == 3


def test_not_a_git_repository_is_unavailable_not_clean(tmp_path):
    """Satisfies: REQ-PA-012 -- an unenumerable population is UNAVAILABLE, never a clean scan (gh#2426)."""
    m = _load()
    plain = tmp_path / "plain"
    (plain / "docs").mkdir(parents=True)
    (plain / "docs" / "HANDOFF_e.md").write_text("deferred: s\n")
    r = m.scan(plain, subjects=["s"], days=14)
    assert r["verdict"] == "UNAVAILABLE" and "git" in r["reason"].lower(), r


def test_result_names_what_was_searched(tmp_path):
    """Satisfies: REQ-PA-012 -- result names what was searched."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_f.md", "x\n", days_ago=1)
    r = m.scan(repo, subjects=["s"], days=14)
    assert r["window_days"] == 14 and r["selector"] and r["locations"], r
    assert any(loc["path"] == "docs" and loc["status"] == "present" for loc in r["locations"]), r


# ---- independent review round 1: regression cases ---------------------------------

def test_untracked_filename_with_spaces_is_found(tmp_path):
    """Satisfies: REQ-PA-012 -- a path containing spaces is read exactly (R1-01: porcelain quoting hid it)."""
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/README.md", "x\n", days_ago=1)
    (repo / "docs" / "HANDOFF_has space.md").write_text("deferred: spaced-subject\n")
    r = m.scan(repo, subjects=["spaced-subject"], days=14)
    assert r["verdict"] == "MATCHED", r


def test_old_modified_filename_with_spaces_is_found(tmp_path):
    """Satisfies: REQ-PA-012 -- a locally modified old handoff with spaces is a candidate (R1-01)."""
    m = _load()
    repo = _repo(tmp_path)
    p = _commit_file(repo, "docs/HANDOFF_old one.md", "old\n", days_ago=40)
    p.write_text("old\nre-parked: spaced-old\n")
    r = m.scan(repo, subjects=["spaced-old"], days=14)
    assert r["verdict"] == "MATCHED", r


def test_staged_rename_counts_the_new_path_only(tmp_path):
    """Satisfies: REQ-PA-012 -- a rename record's original path is not read as a second candidate.

    Guard, not reproduction: the pre-fix parser also passed this; it pins the -z parser's rename skip (R1-01).
    """
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/HANDOFF_a.md", "deferred: renamed-subject\n", days_ago=40)
    _git(repo, "mv", "docs/HANDOFF_a.md", "docs/HANDOFF_b.md")
    r = m.scan(repo, subjects=["renamed-subject"], days=14)
    assert r["verdict"] == "MATCHED" and r["candidate_paths"] == ["docs/HANDOFF_b.md"], r


def test_git_that_cannot_run_is_unavailable_exit_2(tmp_path):
    """Satisfies: REQ-PA-012 -- a missing git is UNAVAILABLE (exit 2), never a crash that exits 1 (R1-02)."""
    import sys as _sys
    repo = _repo(tmp_path)
    out = subprocess.run([_sys.executable, str(SCRIPT), "--repo", str(repo), "--subject", "x"],
                         capture_output=True, text=True, env={"PATH": ""})
    assert out.returncode == 2 and out.stdout.startswith("UNAVAILABLE"), (out.returncode, out.stdout, out.stderr)


def test_one_unreadable_candidate_forbids_a_clean_result(tmp_path):
    """Satisfies: REQ-PA-012 -- a candidate that cannot be read may hide the subject, so no clean verdict (R1-03)."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can read a mode-000 file")
    m = _load()
    repo = _repo(tmp_path)
    _commit_file(repo, "docs/README.md", "x\n", days_ago=1)
    (repo / "docs" / "HANDOFF_ok.md").write_text("unrelated\n")
    locked = repo / "docs" / "HANDOFF_locked.md"
    locked.write_text("deferred: hidden-subject\n")
    locked.chmod(0)
    try:
        r = m.scan(repo, subjects=["hidden-subject"], days=14)
    finally:
        locked.chmod(0o644)
    assert r["verdict"] == "UNAVAILABLE" and r["unreadable"], r
