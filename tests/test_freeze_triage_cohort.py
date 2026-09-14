"""C-34-26 — the triage-cohort instrument, promoted cohort-independent.

The old verify() asserted one cycle's counts: 192 members, 19 surfaced, 7 clusters. It
therefore passed for exactly one population and failed for every other, for a reason that has
nothing to do with custody. These tests exercise cohorts of OTHER sizes -- each of which the
old implementation would have rejected -- and then tamper with custody to prove verification
still bites.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ftc", REPO / "scripts" / "freeze_triage_cohort.py")
ftc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ftc)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def build(tmp: Path, numbers: list[int], surfaced: list[int], clusters: int = 1):
    """Mint a self-consistent snapshot / clusters / result triple of arbitrary size."""
    items = [{"number": n, "title": f"t{n}", "url": "u", "created_at": "c",
              "updated_at": "u", "labels": [], "body_sha256": sha(f"body{n}")} for n in numbers]
    member_digest = sha("\n".join(str(n) for n in numbers))
    snap = {"schema": "triage-cohort-review-input/1.0", "repo": "octo/handbook",
            "frozen_at": "2026-01-01T00:00:00+00:00",
            "population_predicate": "open issue with no live classification label",
            "classification_labels": ["type:bug"], "query": "q", "count": len(numbers),
            "member_number_sha256": member_digest,
            "body_custody": "bodies omitted; each item carries a source digest",
            "items": items}
    buckets = [[] for _ in range(clusters)]
    for i, n in enumerate(surfaced):
        buckets[i % clusters].append(n)
    cl = {"clusters": [{"issues": b, "proposed_owner": "o", "next_action": "a",
                        "principal_effect": "e"} for b in buckets if b]}
    res_items = [{"number": n, "body_sha256": sha(f"body{n}"),
                  "independent_verdict": "SURFACE" if n in surfaced else "NOT_SURFACE",
                  "final_verdict": "SURFACE" if n in surfaced else "NOT_SURFACE",
                  "rationale": "r", "proposed_owner": "o", "next_action": "a"}
                 for n in numbers]
    counts = {v: sum(i["final_verdict"] == v for i in res_items)
              for v in ("SURFACE", "VERIFY", "NOT_SURFACE")}
    res = {"schema": "triage-cohort-review-result/1.0",
           "source_member_number_sha256": member_digest, "source_count": len(numbers),
           "reviewed_count": len(res_items), "final_counts": counts,
           "surfaced_cluster_count": len(cl["clusters"]),
           "surfaced_issue_count": len(surfaced), "clusters": cl["clusters"],
           "items": res_items}
    ps, pc, pr = tmp / "s.json", tmp / "c.json", tmp / "r.json"
    ps.write_text(json.dumps(snap)); pc.write_text(json.dumps(cl)); pr.write_text(json.dumps(res))
    return ps, pc, pr


# --- cohort independence: the point of the promotion ------------------------------

@pytest.mark.parametrize("size,surf,cl", [(3, [1], 1), (10, [2, 4, 6], 2), (250, [7], 1)])
def test_verify_passes_for_cohorts_of_any_size(tmp_path, size, surf, cl, capsys):
    """Each of these would have FAILED the old `== 192` / `== 19` / `== 7` literals."""
    ps, pc, pr = build(tmp_path, list(range(1, size + 1)), surf, cl)
    assert ftc.verify(ps, pc, pr) == 0
    assert "PASS" in capsys.readouterr().out


def test_a_single_member_cohort_verifies(tmp_path):
    ps, pc, pr = build(tmp_path, [42], [42], 1)
    assert ftc.verify(ps, pc, pr) == 0


# --- custody still bites -----------------------------------------------------------

def test_a_tampered_member_digest_fails(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    snap = json.loads(ps.read_text())
    snap["member_number_sha256"] = sha("tampered")
    ps.write_text(json.dumps(snap))
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


def test_a_member_added_underneath_the_review_fails(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    snap = json.loads(ps.read_text())
    snap["items"].append({"number": 99, "title": "t", "url": "u", "created_at": "c",
                          "updated_at": "u", "labels": [], "body_sha256": sha("body99")})
    snap["count"] = 4
    ps.write_text(json.dumps(snap))
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


def test_an_edited_body_fails_body_hash_custody(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    res = json.loads(pr.read_text())
    res["items"][0]["body_sha256"] = sha("edited underneath")
    pr.write_text(json.dumps(res))
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


def test_a_surfaced_issue_outside_any_cluster_fails(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    cl = json.loads(pc.read_text())
    cl["clusters"][0]["issues"] = [2]      # cluster no longer matches the SURFACE verdict
    pc.write_text(json.dumps(cl))
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


def test_a_cluster_missing_its_actionable_fields_fails(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    cl = json.loads(pc.read_text())
    cl["clusters"][0]["next_action"] = "  "
    pc.write_text(json.dumps(cl))
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


def test_a_duplicated_member_fails_uniqueness(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 2], [1], 1)
    with pytest.raises(RuntimeError, match="verification failed"):
        ftc.verify(ps, pc, pr)


# --- reconcile ----------------------------------------------------------------------

def test_reconcile_rejects_a_review_that_does_not_cover_the_frozen_cohort(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2, 3], [1], 1)
    rev = tmp_path / "rev.json"
    rev.write_text(json.dumps([{"number": 1, "verdict": "SURFACE", "rationale": "r",
                                "proposed_owner": "o", "next_action": "a"}]))
    with pytest.raises(RuntimeError, match="do not match the frozen member register"):
        ftc.reconcile(ps, [rev], pc, tmp_path / "out.json")


def test_reconcile_rejects_cluster_rows_outside_the_frozen_input(tmp_path):
    ps, pc, pr = build(tmp_path, [1, 2], [1], 1)
    rev = tmp_path / "rev.json"
    rev.write_text(json.dumps([
        {"number": n, "verdict": "NOT_SURFACE", "rationale": "r", "proposed_owner": "o",
         "next_action": "a"} for n in (1, 2)]))
    pc.write_text(json.dumps({"clusters": [{"issues": [999], "proposed_owner": "o",
                                            "next_action": "a", "principal_effect": "e"}]}))
    with pytest.raises(RuntimeError, match="outside the frozen input"):
        ftc.reconcile(ps, [rev], pc, tmp_path / "out.json")


# --- version independence / no private identifiers ------------------------------------

def test_no_cycle_scoped_schema_identifier_survives(tmp_path):
    ps, _, pr = build(tmp_path, [1], [1], 1)
    assert "v332" not in json.loads(ps.read_text())["schema"]
    assert "v332" not in json.loads(pr.read_text())["schema"]


def test_the_source_carries_no_private_tracker_identifier():
    """A private TRACKER/seat identifier, not the word 'private'.

    The first version of this test asserted `"private-" not in src` and failed on
    `--private-body-output` -- a legitimate flag naming the private body FILE. A predicate
    broad enough to match its own tooling cannot tell a leak from a flag name, so it is
    scoped to org/seat identifiers.
    """
    src = (REPO / "scripts" / "freeze_triage_cohort.py").read_text()
    for token in ("gmelli", "aget-aget", "private-aget", "private-supervisor", "-AGET/"):
        assert token not in src, f"private identifier {token!r} survived promotion"
    # and no module-level repository default of any shape
    assert "freeze mode requires --repo" in src


def test_cohort_literals_survive_only_as_prose_never_as_code(tmp_path):
    """The removed literals are documented. Documentation must not become behaviour."""
    src = (REPO / "scripts" / "freeze_triage_cohort.py").read_text()
    body = src.split('"""', 2)[2]          # past the module docstring
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    for literal in ("192", "== 19", "== 7"):
        assert literal not in code, f"cohort literal {literal!r} is live in code"


def test_freeze_mode_still_requires_an_explicit_repo():
    """No default tracker: substituting an unnamed subject is the defect --repo prevents."""
    src = (REPO / "scripts" / "freeze_triage_cohort.py").read_text()
    assert "freeze mode requires --repo OWNER/NAME" in src
