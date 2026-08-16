"""Two-polarity contract for scripts/release_cadence_gap.py (R-REL-CAD-007 instrument).

The point of both polarities: a guard that only ever fires, or only ever passes, is
not evidence. These tests assert that a breaching series FLAGS and a compliant series
does NOT — over real git tag objects, not mocked dates.

Anchors: gh#1769 (R-REL-CAD-007 has no instrument);
docs/STUDY_slis_and_slo_candidates_2026-07-28.md F5.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "release_cadence_gap.py"


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True, env=env)


def _fixture_repo(tmp, tags):
    """Build a repo whose annotated tags land on the given ISO dates.

    tags: list of (tagname, 'YYYY-MM-DD', annotated: bool)
    """
    import os
    repo = Path(tmp) / "canon"
    repo.mkdir()
    _git(repo.parent, "init", "-q", "canon")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    for name, date, annotated in tags:
        stamp = f"{date}T12:00:00-07:00"
        (repo / "f.txt").write_text(name)
        _git(repo, "add", "f.txt")
        env = dict(os.environ,
                   GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp,
                   GIT_AUTHOR_EMAIL="t@example.com", GIT_AUTHOR_NAME="t",
                   GIT_COMMITTER_EMAIL="t@example.com", GIT_COMMITTER_NAME="t")
        _git(repo, "commit", "-q", "-m", name, env=env)
        if annotated:
            _git(repo, "tag", "-a", name, "-m", name, env=env)
        else:
            _git(repo, "tag", name, env=env)
    return repo


def _run(repo):
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--json"],
        capture_output=True, text=True)
    return json.loads(out.stdout), out.returncode


# --- polarity 1: a series that exceeds the cap MUST flag -------------------

def test_breaching_series_flags():
    """Five Saturdays with no release between two tags -> BREACHED.

    Satisfies: R-REL-CAD-007 (max-gap cap) — positive polarity.
    """
    with tempfile.TemporaryDirectory() as tmp:
        # 2026-06-27 (Sat) then 2026-08-01 (Sat): Saturdays strictly between are
        # 07-04, 07-11, 07-18, 07-25, 08-01 = 5 > cap 3
        repo = _fixture_repo(tmp, [
            ("v1.0.0", "2026-06-27", True),
            ("v1.1.0", "2026-08-01", True),
        ])
        r, rc = _run(repo)
        assert r["status"] == "BREACHED", r
        assert len(r["breaches"]) == 1
        assert r["breaches"][0]["saturdays"] == 5
        assert rc == 1, "a breach must be a nonzero exit, not a printed note"


# --- polarity 2: a compliant series MUST NOT flag --------------------------

def test_compliant_series_does_not_flag():
    """Weekly Saturday releases -> HELD, and no false breach.

    Satisfies: R-REL-CAD-007 (max-gap cap) — negative polarity.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fixture_repo(tmp, [
            ("v1.0.0", "2026-06-27", True),
            ("v1.1.0", "2026-07-04", True),
            ("v1.2.0", "2026-07-11", True),
            ("v1.3.0", "2026-07-18", True),
        ])
        r, rc = _run(repo)
        assert r["status"] == "HELD", r
        assert r["breaches"] == []
        assert r["max_saturdays_binding"] == 1
        assert rc == 0


# --- the scope clause is part of the result (L1220 / filtered-zero) --------

def test_pre_policy_gap_is_context_not_breach():
    """A 5-Saturday gap BEFORE the policy date must not be reported as a breach.

    Satisfies: R-REL-CAD-007 scope clause — the requirement binds from 2026-06-26.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fixture_repo(tmp, [
            ("v1.0.0", "2026-01-03", True),
            ("v1.1.0", "2026-02-07", True),   # 5 Saturdays, but pre-2026-06-26
            ("v1.2.0", "2026-02-14", True),
        ])
        r, rc = _run(repo)
        assert r["status"] != "BREACHED", "pre-policy interval must not breach"
        assert r["max_saturdays_all_history"] == 5, "…but it must still be REPORTED"
        assert r["max_saturdays_binding"] == 0
        assert rc == 0


# --- an undatable tag is disclosed, never silently dropped ----------------

def test_lightweight_tag_is_skipped_with_reason():
    """A lightweight tag has no tag object; dating it from the commit would blend
    two different boundaries. It must appear in tags_skipped, not vanish.

    Satisfies: R-REL-CAD-007 provenance discipline — an undatable tag is disclosed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fixture_repo(tmp, [
            ("v1.0.0", "2026-06-27", True),
            ("v1.1.0", "2026-07-04", False),   # lightweight
            ("v1.2.0", "2026-07-11", True),
        ])
        r, _ = _run(repo)
        skipped = [t["tag"] for t in r["tags_skipped"]]
        assert "v1.1.0" in skipped, r["tags_skipped"]
        assert r["tags_considered"] == 2


# --- the live reading is a real reading -----------------------------------

def test_live_canonical_reading_is_wellformed():
    """The live reading against canonical is a real reading, not a fixture.

    Satisfies: R-REL-CAD-007 — the instrument reports against the real corpus.
    """
    canon = REPO.parent / "aget"
    if not (canon / ".git").exists():
        pytest.skip("canonical ../aget not present")
    r, rc = _run(canon)
    assert r["requirement"] == "R-REL-CAD-007"
    assert r["cap_saturdays"] == 3
    assert r["status"] in {"HELD", "BREACHED", "NO-BINDING-DATA"}
    assert r["intervals_binding"] >= 1, "policy has been in force since 2026-06-26"
    assert rc in (0, 1)
