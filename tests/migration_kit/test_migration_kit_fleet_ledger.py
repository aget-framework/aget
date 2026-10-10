"""Tests for the v3.35 Gate 3 ledger (G3.1, the fleet migration outcome). Hermetic: local git fixtures, no network.

Failure paths are tested before the ledger classifies anything (plan Gate 3, G3.1): an observation
marked unavailable is INCONCLUSIVE; an exclusion for time or difficulty does not count; a shared
root without a coverage finding is unmet; changed checks without a ruling are unmet; workflow checks
that were not compared (pre-migration revision not found, or a workflow tree unreadable) are INCONCLUSIVE
unless a check-change ruling is recorded for the member.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "v335_fleet_ledger", ROOT / "scripts/migration_kit/fleet_ledger.py")
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def sh(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def commit(repo, files, msg, tag=None):
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            p.unlink()
        else:
            p.write_text(text)
    sh(repo, "add", "-A")
    sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
    if tag:
        sh(repo, "tag", tag)
    return sh(repo, "rev-parse", "HEAD")


def init(path):
    path.mkdir(parents=True)
    sh(path, "init", "-q", "-b", "main")
    return path


def version(v):
    return json.dumps({"aget_version": v})


# ------------------------------------------------------------------ classify: every state

BASE = {"remote_version": "3.35.0", "local_version": "3.35.0", "template": "template-x-aget",
        "payload_findings": [], "receipt_terminal": "BEHAVIOUR_VERIFIED", "receipt_on_revision": True,
        "root_workflows": 1, "shared_root": False, "checks_compared": True, "checks_changed": False,
        "ci": ("PASS", "3 run(s)")}


def state(**over):
    return L.classify({**BASE, **over})[0]


def test_all_conditions_met_is_verified():
    assert state() == "VERIFIED"


def test_no_root_workflow_is_published_no_ci():
    assert state(root_workflows=0) == "PUBLISHED-NO-CI"


def test_unreadable_evidence_is_inconclusive_not_a_pass():
    """Covers an observation marked `unavailable` only. A workflow comparison that was not made is a separate
    branch of classify(), tested by the "uncompared workflow checks" tests below."""
    assert state(unavailable="ls-remote failed") == "INCONCLUSIVE"


def test_version_field_alone_does_not_suffice():
    assert state(payload_findings=["scripts/x.py: differs from every release source"]) == "PAYLOAD-NONCONFORMING"


def test_unresolved_template_is_inconclusive():
    assert state(template=None, template_reason="no usable template") == "INCONCLUSIVE"


def test_not_on_remote_but_local_is_unpublished():
    assert state(remote_version="3.34.0") == "UNPUBLISHED"


def test_neither_is_not_migrated():
    assert state(remote_version="3.34.0", local_version="3.34.0") == "NOT-MIGRATED"


def test_missing_receipt_is_unmet():
    assert state(receipt_terminal=None) == "NO-RECEIPT"
    assert state(receipt_on_revision=False) == "RECEIPT-NOT-ON-REVISION"


def test_shared_root_without_coverage_finding_is_unmet():
    assert state(shared_root=True, coverage=None) == "SHARED-ROOT-UNRESOLVED"


def test_shared_root_recorded_as_not_covering_is_no_ci():
    assert state(shared_root=True, coverage=False) == "PUBLISHED-NO-CI"


def test_shared_root_recorded_as_covering_needs_ci():
    assert state(shared_root=True, coverage=True) == "VERIFIED"


def test_loosened_checks_without_a_ruling_are_unmet():
    assert state(checks_changed=True) == "CHECKS-CHANGED"
    assert state(checks_changed=True, check_change_ruling={"workflows-changed": {"ruling_quote": "q"}}) == "VERIFIED"


def test_a_tightening_review_counts_only_for_the_tree_it_was_bound_to():
    review = {"classification": "tightening", "evidence": "diff adds a blocking step",
              "workflows_tree_sha256": "t1"}
    assert state(checks_changed=True, check_change_review=review, workflows_tree_sha256="t1") == "VERIFIED"
    assert state(checks_changed=True, check_change_review=review, workflows_tree_sha256="t2") == "CHECKS-CHANGED"
    loosening = {**review, "classification": "loosening"}
    assert state(checks_changed=True, check_change_review=loosening, workflows_tree_sha256="t1") == "CHECKS-CHANGED"
    no_evidence = {**review, "evidence": ""}
    assert state(checks_changed=True, check_change_review=no_evidence, workflows_tree_sha256="t1") == "CHECKS-CHANGED"


# F-7 (review r4): a comparison that was not made is not "checks unchanged"

# record_authority.py's shape; C2a (R2-T15, S-154): keyed by the comparison it passes, one fixed name per route
RULING = {name: {"change": "c", "line": "l", "source": "principal, typed"}
          for name in ("workflows-not-compared", "workflows-changed")}


def test_uncompared_workflow_checks_are_inconclusive_not_verified():
    st, reason = L.classify({**BASE, "checks_compared": False,
                             "checks_not_compared": "pre-migration revision not found"})
    assert st == "INCONCLUSIVE"
    assert "not compared" in reason and "pre-migration revision not found" in reason
    assert state(checks_compared=False, ci=("FAIL", "CI")) == "INCONCLUSIVE"
    missing = {k: v for k, v in BASE.items() if k != "checks_compared"}
    st, reason = L.classify(missing)  # an observation set without the key was not compared either
    assert st == "INCONCLUSIVE" and "not compared" in reason


def test_uncompared_workflow_checks_with_a_recorded_ruling_classify_as_before():
    assert state(checks_compared=False, check_change_ruling=RULING) == "VERIFIED"
    assert state(checks_compared=False, check_change_ruling=RULING, ci=("FAIL", "CI")) == "PUBLISHED-NOT-VERIFIED"
    assert state(checks_compared=False, check_change_ruling=RULING, ci=("NOT-QUERIED", "")) == "CI-NOT-QUERIED"
    assert state(checks_compared=False, check_change_ruling={}) == "INCONCLUSIVE"  # an empty record is no ruling


def test_only_a_ruling_in_the_recorders_shape_counts_as_a_ruling():
    """Second review leg, 2026-10-02: any value recorded for the member passed an unmade comparison, the bare word
    "pending" included. What record_authority.py writes is a mapping of check names to entries with a change and the
    principal's line; anything else is read as no ruling."""
    good = {"lint": {"change": "removed", "line": "GO supervisor - lint check removed for seat", "source": "s"}}
    assert L.recorded_ruling(good) == good
    for bad in ("pending", "", None, {}, [], {"lint": "pending"}, {"lint": {"change": "removed"}},
                {"lint": {"change": "removed", "line": "  "}}, {"lint": good["lint"], "ci": {"line": "x"}},
                {"lint": {"change": True, "line": True}}, {"lint": {"change": 1, "line": 2}},
                {"lint": {"change": ["pending"], "line": {"pending": True}}}):        # reviewer session, B111
        assert L.recorded_ruling(bad) is None, bad


def test_a_tightening_review_does_not_stand_in_for_a_comparison():
    review = {"classification": "tightening", "evidence": "e", "workflows_tree_sha256": "t1"}
    assert state(checks_compared=False, check_change_review=review, workflows_tree_sha256="t1") == "INCONCLUSIVE"


def test_uncompared_workflow_checks_leave_published_no_ci_unaffected():
    assert state(root_workflows=0, checks_compared=False) == "PUBLISHED-NO-CI"
    assert state(shared_root=True, coverage=False, checks_compared=False) == "PUBLISHED-NO-CI"
    assert state(shared_root=True, coverage=None, checks_compared=False) == "SHARED-ROOT-UNRESOLVED"


def test_uncompared_workflow_checks_do_not_mask_an_earlier_condition():
    assert state(checks_compared=False, receipt_terminal=None) == "NO-RECEIPT"
    assert state(checks_compared=False, remote_version="3.34.0") == "UNPUBLISHED"


def test_compared_workflow_checks_classify_as_before():
    assert state(checks_compared=True, checks_changed=False) == "VERIFIED"
    assert state(checks_compared=True, checks_changed=True) == "CHECKS-CHANGED"
    assert state(checks_compared=True, checks_changed=True, check_change_ruling=RULING) == "VERIFIED"


def test_the_row_shows_the_reason_and_whether_the_comparison_was_made(monkeypatch):
    seen = {**BASE, "checks_compared": False, "checks_not_compared": "pre-migration revision not found"}
    monkeypatch.setattr(L, "members", lambda: [("a", "/x/a")])
    monkeypatch.setattr(L, "PINNED_MEMBERS", 1)
    monkeypatch.setattr(L, "load_json", lambda path, default: default)
    monkeypatch.setattr(L.census, "repo_root", lambda loc: loc)
    monkeypatch.setattr(L, "observe", lambda *args: seen)
    (row,) = L.build()
    assert row["state"] == "INCONCLUSIVE" and row["terminal"] is False and row["checks_compared"] is False
    assert "not compared" in row["reason"] and "pre-migration revision not found" in row["reason"]
    json.dumps(row)


def test_ci_outcomes():
    assert state(ci=("FAIL", "CI")) == "PUBLISHED-NOT-VERIFIED"
    assert state(ci=("NOT-QUERIED", "")) == "CI-NOT-QUERIED"
    assert state(ci=("PENDING", "")) == "CI-PENDING"
    assert state(ci=("NO-RUN", "")) == "CI-NO-RUN"
    assert state(ci=("QUERY-FAILED", "x")) == "INCONCLUSIVE"
    assert state(ci=("UNREACHABLE", "")) == "INCONCLUSIVE"


class FakeGh:
    """Scripted `gh` replies: each call pops the next (returncode, stdout) for its command kind."""
    def __init__(self, lists, api):
        self.lists, self.api, self.calls = list(lists), list(api), []

    def __call__(self, cmd, **kw):
        self.calls.append(cmd[1])
        rc, out = (self.lists if cmd[1] == "run" else self.api).pop(0)
        return subprocess.CompletedProcess(cmd, rc, stdout=out, stderr="")


RUN_OK = (0, json.dumps([{"status": "completed", "conclusion": "success", "workflowName": "CI"}]))


@pytest.mark.parametrize("lists,api,want", [
    # 2026-09-28 09:57:58: an empty list once was read as no run; the run had succeeded
    ([(0, "[]"), RUN_OK], [(0, "1")], "PASS"),                 # the retry sees the run
    ([(0, "[]"), (0, "[]")], [(0, "1")], "QUERY-FAILED"),      # the two routes disagree
    ([(0, "[]"), (0, "[]")], [(1, "")], "QUERY-FAILED"),       # the confirming query failed
    ([(0, "[]"), (1, "")], [(0, "0")], "QUERY-FAILED"),        # the retry failed
    ([(1, "")], [], "QUERY-FAILED"),                           # the first query failed
    ([(0, "not json")], [], "QUERY-FAILED"),
    ([(0, "[]"), (0, "[]")], [(0, "0")], "NO-RUN"),            # absence shown twice, by two routes
    ([RUN_OK], [], "PASS"),
])
def test_a_failed_or_unconfirmed_ci_query_is_never_no_run(monkeypatch, lists, api, want):
    fake = FakeGh(lists, api)
    monkeypatch.setattr(L.subprocess, "run", fake)
    assert L.ci_result("/r", "abc", True, retry_delay=0)[0] == want


@pytest.mark.parametrize("reason", ["time", "difficulty", None])
def test_exclusion_for_time_or_difficulty_does_not_count(reason):
    ex = {"ruling_quote": "exclude it", "source": "packet", "reason_class": reason}
    assert L.classify({"exclusion": ex})[0] == "EXCLUSION-INVALID"


def test_exclusion_needs_a_quoted_ruling_and_source():
    assert L.classify({"exclusion": {"reason_class": "decommissioned"}})[0] == "INCONCLUSIVE"
    ex = {"ruling_quote": "exclude it", "source": "packet", "reason_class": "decommissioned"}
    assert L.classify({"exclusion": ex})[0] == "EXCLUDED"


def test_only_three_states_are_terminal():
    assert L.TERMINAL == ("VERIFIED", "PUBLISHED-NO-CI", "EXCLUDED")


# ------------------------------------------------------------------ observations on git fixtures

@pytest.fixture
def aget(tmp_path):
    """An Aget with an origin, migrated 3.34.0 -> 3.35.0, workflows unchanged."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    repo = init(tmp_path / "aget")
    sh(repo, "remote", "add", "origin", str(origin))
    commit(repo, {".aget/version.json": version("3.34.0"), ".github/workflows/ci.yml": "on: push\n",
                  "scripts/a.py": "a = 1\n"}, "base")
    pre = sh(repo, "rev-parse", "HEAD")
    mig = commit(repo, {".aget/version.json": version("3.35.0"), "scripts/a.py": "a = 2\n"}, "migrate")
    sh(repo, "push", "-q", "origin", "main")
    return repo, pre, mig


def test_remote_head_reads_branch_and_sha(aget):
    repo, _, mig = aget
    assert L.remote_head(repo) == ("main", mig)


def test_no_origin_is_unavailable(tmp_path):
    repo = init(tmp_path / "lonely")
    commit(repo, {"x": "1\n"}, "x")
    with pytest.raises(L.Unavailable):
        L.remote_head(repo)


def test_version_and_pre_migration_revision(aget):
    repo, pre, mig = aget
    assert L.version_at(repo, "", mig) == "3.35.0"
    assert L.pre_migration_revision(repo, "", mig) == pre


def test_workflow_change_since_pre_migration_is_seen(aget):
    repo, pre, mig = aget
    assert L.workflows_tree(repo, pre) == L.workflows_tree(repo, mig)
    loosened = commit(repo, {".github/workflows/ci.yml": "on: push\ncontinue-on-error: true\n"}, "loosen")
    assert L.workflows_tree(repo, pre) != L.workflows_tree(repo, loosened)


def observed(repo):
    """observe() on one fixture member: no records, no receipts, own root, CI not queried."""
    return L.observe("a", str(repo), {}, {}, {}, False)


def loosening_of(o):
    return {k: o[k] for k in ("checks_compared", "checks_changed", "checks_not_compared") if k in o}


def test_observe_records_a_comparison_that_was_made(aget, framework):
    repo, _, _ = aget
    o = observed(repo)
    assert "unavailable" not in o
    assert o["checks_compared"] is True and o["checks_changed"] is False and "checks_not_compared" not in o
    assert L.classify({**BASE, **loosening_of(o)})[0] == "VERIFIED"
    commit(repo, {".github/workflows/ci.yml": "on: push\ncontinue-on-error: true\n"}, "loosen")
    sh(repo, "push", "-q", "origin", "main")
    o = observed(repo)
    assert o["checks_compared"] is True and o["checks_changed"] is True
    assert L.classify({**BASE, **loosening_of(o)})[0] == "CHECKS-CHANGED"


def test_observe_without_a_pre_migration_revision_is_not_compared(tmp_path, framework):
    """The version file enters at the target in a root commit: there is no parent revision to compare with."""
    origin = tmp_path / "born.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    repo = init(tmp_path / "born")
    sh(repo, "remote", "add", "origin", str(origin))
    sha = commit(repo, {".aget/version.json": version("3.35.0"), ".github/workflows/ci.yml": "on: push\n"}, "born")
    sh(repo, "push", "-q", "origin", "main")
    assert L.pre_migration_revision(repo, "", sha) is None
    o = observed(repo)
    assert "unavailable" not in o
    assert o["checks_compared"] is False and o["checks_changed"] is False
    assert o["checks_not_compared"] == "pre-migration revision not found"
    st, reason = L.classify({**BASE, **loosening_of(o)})
    assert st == "INCONCLUSIVE" and "pre-migration revision not found" in reason


@pytest.mark.parametrize("unreadable", ["pre", "published", "both"])
def test_observe_with_an_unreadable_workflow_tree_is_not_compared(aget, framework, monkeypatch, unreadable):
    repo, pre, mig = aget
    real = L.workflows_tree
    lost = {"pre": {pre}, "published": {mig}, "both": {pre, mig}}[unreadable]
    monkeypatch.setattr(L, "workflows_tree", lambda root, rev: None if rev in lost else real(root, rev))
    o = observed(repo)
    assert "unavailable" not in o
    assert o["checks_compared"] is False and o["checks_changed"] is False
    assert "unreadable" in o["checks_not_compared"]
    st, reason = L.classify({**BASE, **loosening_of(o)})
    assert st == "INCONCLUSIVE" and "unreadable" in reason


def test_nested_prefix_is_read(tmp_path):
    root = init(tmp_path / "shared")
    commit(root, {"seat/.aget/version.json": version("3.35.0")}, "nested")
    assert L.version_at(root, "seat/", "HEAD") == "3.35.0"


@pytest.fixture
def framework(tmp_path, monkeypatch):
    fw = tmp_path / "fw"
    tpl = init(fw / "template-x-aget")
    commit(tpl, {"scripts/a.py": "a = 1\n", "scripts/gone.py": "g\n"}, "t334", tag="v3.34.0")
    commit(tpl, {"scripts/a.py": "a = 2\n", "scripts/gone.py": None, "scripts/new.py": "n\n"}, "t335",
           tag="v3.35.0")
    core = init(fw / "aget")
    commit(core, {"scripts/core_only.py": "c\n"}, "c335", tag="v3.35.0")
    monkeypatch.setenv("AGET_FRAMEWORK_ROOT", str(fw))
    monkeypatch.setattr(L.W, "SPEC_PATHS", ["scripts/core_only.py"])
    monkeypatch.setattr(L.W, "CORRECTION_ROW_4", [])
    return fw


def test_payload_expectations_from_the_template_diff(framework):
    exp = L.payload_expectations("template-x-aget")
    assert exp == {"scripts/a.py": "present", "scripts/gone.py": "absent", "scripts/new.py": "present",
                   "scripts/core_only.py": "present"}


def test_payload_conforming_revision_has_no_findings(framework, tmp_path):
    repo = init(tmp_path / "ok")
    commit(repo, {"scripts/a.py": "a = 2\n", "scripts/new.py": "n\n", "scripts/core_only.py": "c\n"}, "m")
    exp = L.payload_expectations("template-x-aget")
    assert L.payload_findings(repo, "", "HEAD", "template-x-aget", exp, {}) == []


def test_payload_differences_are_findings_unless_recorded(framework, tmp_path):
    repo = init(tmp_path / "bad")
    commit(repo, {"scripts/a.py": "a = 99\n", "scripts/gone.py": "g\n", "scripts/core_only.py": "c\n"}, "m")
    exp = L.payload_expectations("template-x-aget")
    found = L.payload_findings(repo, "", "HEAD", "template-x-aget", exp, {})
    assert found == ["scripts/a.py: differs from every release source",
                     "scripts/gone.py: present, release removes it",
                     "scripts/new.py: absent at the revision"]
    a_blob = sh(repo, "rev-parse", "HEAD:scripts/a.py")
    recorded = {"scripts/a.py": {"reason": "receiver-authored", "source": "receipt", "blob": a_blob}}
    assert len(L.payload_findings(repo, "", "HEAD", "template-x-aget", exp, recorded)) == 2
    recorded_absent = {"scripts/new.py": {"reason": "not taken", "source": "receipt", "blob": "absent"}}
    assert "scripts/new.py: absent at the revision" not in L.payload_findings(
        repo, "", "HEAD", "template-x-aget", exp, recorded_absent)


def test_a_recorded_deviation_covers_only_the_blob_it_names(framework, tmp_path):
    repo = init(tmp_path / "rec")
    commit(repo, {"scripts/a.py": "a = 99\n", "scripts/new.py": "n\n", "scripts/core_only.py": "c\n"}, "m")
    exp = L.payload_expectations("template-x-aget")
    old = sh(repo, "rev-parse", "HEAD:scripts/a.py")
    commit(repo, {"scripts/a.py": "a = 100\n"}, "later change")
    recorded = {"scripts/a.py": {"reason": "r", "source": "s", "blob": old}}
    found = L.payload_findings(repo, "", "HEAD", "template-x-aget", exp, recorded)
    assert len(found) == 1 and found[0].startswith("scripts/a.py: recorded for blob")
    unbound = {"scripts/a.py": {"reason": "r", "source": "s"}}
    assert L.payload_findings(repo, "", "HEAD", "template-x-aget", exp, unbound) == [
        "scripts/a.py: recorded without a blob binding"]


def test_missing_template_repository_falls_through_to_archetype(framework, tmp_path):
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "agent", "archetype": "x"}))
    assert L.resolve_template(loc) == ("template-x-aget", "INFERRED from archetype 'x'")


def test_disagreeing_template_sources_are_a_conflict_not_a_choice(framework, tmp_path):
    other = init(framework / "template-y-aget")
    commit(other, {"z": "1\n"}, "t334", tag="v3.34.0")
    commit(other, {"z": "2\n"}, "t335", tag="v3.35.0")
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "agent", "archetype": "x"}))
    (loc / "manifest.yaml").write_text("base_template: template-y-aget\n")
    t, reason = L.resolve_template(loc)
    assert t is None
    assert "disagree" in reason


def test_a_recorded_principal_ruling_resolves_a_conflict(framework, tmp_path):
    other = init(framework / "template-y-aget")
    commit(other, {"z": "1\n"}, "t334", tag="v3.34.0")
    commit(other, {"z": "2\n"}, "t335", tag="v3.35.0")
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "x"}))
    (loc / "manifest.yaml").write_text("base_template: template-y-aget\n")
    assert L.resolve_template(loc, "seat", {})[0] is None  # conflict without a ruling
    ruled = {"templates": {"seat": {"template": "template-x-aget", "source": "principal, test"}}}
    assert L.resolve_template(loc, "seat", ruled) == ("template-x-aget", "principal ruling (principal, test)")
    unsourced = {"templates": {"seat": {"template": "template-x-aget"}}}
    assert L.resolve_template(loc, "seat", unsourced)[0] is None


def test_manifest_template_origin_is_a_source(framework, tmp_path):
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"archetype": "research_engineer"}))
    (loc / "manifest.yaml").write_text("template_origin: template-x-aget\n")
    assert L.resolve_template(loc) == ("template-x-aget", "manifest.yaml template_origin")


def test_manifest_key_one_block_down_is_a_source(framework, tmp_path):
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "agent"}))
    (loc / "manifest.yaml").write_text("composition:\n  base_template: template-x-aget\n")
    assert L.resolve_template(loc) == ("template-x-aget", "manifest.yaml composition.base_template")


def test_pinned_membership_reads_the_pinned_blob(tmp_path):
    repo = init(tmp_path / "reg")
    reg = {"fleet": {"main": {"agents": [{"agent_name": "a", "location": "/x/a"},
                                         {"agent_name": "b"}]}}}
    pin = commit(repo, {L.REGISTER: json.dumps(reg)}, "reg")
    commit(repo, {L.REGISTER: json.dumps({"fleet": {}})}, "later edit")
    assert L.members(repo, pin) == [("a", "/x/a")]


def test_unreadable_pin_is_unavailable(tmp_path):
    repo = init(tmp_path / "reg")
    commit(repo, {"x": "1\n"}, "x")
    with pytest.raises(L.Unavailable):
        L.members(repo, "0" * 40)


def test_recorded_receipt_needs_terminal_revision_and_source(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "OPSTATE", tmp_path / "absent.json")
    records = {"receipts": {
        "ok": {"terminal": "BEHAVIOUR_VERIFIED", "receipt_revision": "abc", "source": "receipt @ abc"},
        "no-source": {"terminal": "BEHAVIOUR_VERIFIED", "receipt_revision": "abc"},
        "no-revision": {"terminal": "BEHAVIOUR_VERIFIED", "source": "s"}}}
    idx = L.ingestion_index(records)
    assert idx == {"ok": {"terminal": "BEHAVIOUR_VERIFIED", "receipt_revisions": ["abc"], "route": "records"}}


def test_totals_come_from_rows():
    rows = [{"state": "VERIFIED"}, {"state": "NOT-MIGRATED"}, {"state": "NOT-MIGRATED"}]
    assert L.totals(rows) == {"NOT-MIGRATED": 2, "VERIFIED": 1}


# --- REVW6's B159 read of stage E2e7 (finding 1) -----------------------------------------------------------------

def _g(root, *args):
    import os as _os
    p = subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                       capture_output=True)
    assert p.returncode == 0, (args, p.stderr)
    return _os.fsdecode(p.stdout).strip()


@pytest.mark.parametrize("character", ["\r", "\t", "\n", ""], ids=["cr", "tab", "lf", "plain"])
def test_b159_1_a_template_deletion_is_judged_on_the_real_member_path(tmp_path, monkeypatch, character):
    """B159 finding 1 (REVW6's falsifier; `plain` is its control). The template deletes `retired_<c>.txt` between the
    release tags and the member still has it: the payload check must report it ("release removes it"), and readiness
    coverage must name the real path. On stage E2e7 the template diff was read in git's quoted newline form, the
    expectation went to a spelling no member holds, and there was no finding for CR, tab or LF."""
    fw = tmp_path / "framework"
    fw.mkdir()
    template = "template-synthetic-aget"
    fixed = set(L.W.SPEC_PATHS + L.W.CORRECTION_ROW_4)
    rel_name = "retired_" + character + ".txt"
    for name in ["aget", template]:
        root = fw / name
        root.mkdir()
        _g(root, "init", "-q")
        for p in sorted(fixed | {rel_name}):
            f = root / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("release\n")
        _g(root, "add", "-A")
        _g(root, "commit", "-qm", "before")
        _g(root, "tag", L.R.FROM_TAG)
        _g(root, "rm", "--", rel_name)
        _g(root, "commit", "-qm", "remove")
        _g(root, "tag", L.R.TO_TAG)
    member = tmp_path / "member"
    member.mkdir()
    _g(member, "init", "-q")
    for p in sorted(fixed | {rel_name}):
        f = member / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("release\n")
    _g(member, "add", "-A")
    _g(member, "commit", "-qm", "member keeps the retired file")
    head = _g(member, "rev-parse", "HEAD")
    monkeypatch.setattr(L.W.V, "framework_root", lambda: str(fw))   # the framework location only
    expected = L.payload_expectations(template)
    findings = L.payload_findings(str(member), "", head, template, expected, {})
    assert expected.get(rel_name) == "absent", sorted(expected)
    assert any("release removes it" in x for x in findings), findings
    assert rel_name in L.W.coverage_paths(str(member), template)


# --- C2a: R2-T15 (a ruling names its comparison; coverage needs its source) and R2-T3 (every workflow ran) ---------

@pytest.mark.parametrize("route", ["not_compared", "changed"])
def test_r2_t15_a_ruling_naming_another_check_does_not_pass_the_comparison(route):
    """R2-T15 (S-154, H-7). A check-change ruling recorded under an unrelated check name does not pass the unmade or
    the changed workflow comparison; the member stays INCONCLUSIVE or CHECKS-CHANGED. Before C2a any ruling in the
    recorded shape passed both."""
    other = {"pytest-timeout": {"change": "c", "line": "l", "source": "principal, typed"}}
    if route == "not_compared":
        assert state(checks_compared=False, check_change_ruling=other) == "INCONCLUSIVE"
    else:
        assert state(checks_compared=True, checks_changed=True, check_change_ruling=other) == "CHECKS-CHANGED"


def test_r2_t15_shared_root_coverage_false_needs_its_source_and_line():
    """R2-T15 (S-152). `covered: false` for a shared-root member counts (PUBLISHED-NO-CI) only with a source and the
    principal's typed line; a bare `false` reads as not recorded. Before C2a the bare value sufficed."""
    assert L.recorded_coverage({"covered": False}) is None
    assert L.recorded_coverage({"covered": False, "line": "GO x", "source": "principal, typed"}) is False
    assert L.recorded_coverage({"covered": True}) is True


def test_r2_t3_one_success_from_another_workflow_does_not_stand_for_a_committed_one(tmp_path, monkeypatch):
    """R2-T3 (S-151, S-157, S-332). Two workflows are committed at the SHA (one of them deleted in the working tree
    but not committed); the only run on the SHA is a success of the first. CI reads INCOMPLETE, naming the second, so
    the member is not VERIFIED. Before C2a one success read PASS, and the working tree's workflows were counted."""
    import subprocess
    root = tmp_path / "m"
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "a.yml").write_text("name: Suite\non: push\n")
    (root / ".github" / "workflows" / "b.yaml").write_text("on: push\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"],
                   check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    (root / ".github" / "workflows" / "b.yaml").unlink()              # deleted in the working tree only
    wfs = L.committed_workflows(root, sha)
    assert wfs == [(".github/workflows/a.yml", "Suite"), (".github/workflows/b.yaml", ".github/workflows/b.yaml")]
    # changed at C2a4 (B181 finding 3, labelled): each run carries the workflow path it ran, as coverage now needs
    monkeypatch.setattr(L, "_run_list", lambda r, s: [{"status": "completed", "conclusion": "success",
                                                       "workflowName": "Suite", "path": ".github/workflows/a.yml"}])
    ci = L.ci_result(root, sha, True, workflows=wfs)
    assert ci[0] == "INCOMPLETE" and ".github/workflows/b.yaml" in ci[1], ci
    assert state(ci=ci) not in ("VERIFIED", "PUBLISHED-NOT-VERIFIED")
    monkeypatch.setattr(L, "_run_list", lambda r, s: [{"status": "completed", "conclusion": "success",
                                                       "workflowName": n, "path": w} for w, n in wfs])
    assert L.ci_result(root, sha, True, workflows=wfs)[0] == "PASS"     # every committed workflow ran: PASS


# --- REVW9's B179 read of stage C2a: coverage cannot rest on a shared display name -------------------------------

def test_b179_1_two_committed_workflows_sharing_a_name_are_not_covered_by_one_success(tmp_path, monkeypatch):
    """B179 finding 1 (REVW9's falsifier). Two workflows committed at the SHA share the display name `Shared`; the only
    run is one success named `Shared`. CI reads INCOMPLETE (a run cannot be matched to each), so the member is not
    VERIFIED. On stage C2a coverage was a set of names, and one success covered both. Control: distinct names, one
    success, still INCOMPLETE naming the other (as before)."""
    import subprocess
    root = tmp_path / "m"
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "a.yml").write_text("name: Shared\non: push\n")
    (root / ".github" / "workflows" / "b.yml").write_text("name: Shared\non: push\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"],
                   check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    wfs = L.committed_workflows(root, sha)
    assert [n for _, n in wfs] == ["Shared", "Shared"], wfs
    # changed at C2a4 (B181 finding 3, labelled): the run carries the workflow path it ran
    monkeypatch.setattr(L, "_run_list", lambda r, s: [{"status": "completed", "conclusion": "success",
                                                       "workflowName": "Shared", "path": ".github/workflows/a.yml"}])
    ci = L.ci_result(root, sha, True, workflows=wfs)
    assert ci[0] == "INCOMPLETE" and "Shared" in ci[1], ci
    assert state(ci=ci) not in ("VERIFIED", "PUBLISHED-NOT-VERIFIED")


# --- REVW9's B181 read of stage E2i9: a run covers the committed workflow whose path it ran ------------------------

def _one_workflow(tmp_path, name="Shared", file="current.yml"):
    import subprocess
    root = tmp_path / "m"
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / file).write_text(f"name: {name}\non: push\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"],
                   check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return root, sha, L.committed_workflows(root, sha)


@pytest.mark.parametrize("path,want", [(".github/workflows/former.yml", "INCOMPLETE"),
                                       (".github/workflows/current.yml", "PASS")])
def test_b181_3_a_run_of_another_workflow_path_does_not_cover(tmp_path, monkeypatch, path, want):
    """B181 finding 3 (REVW9's falsifier). The only committed workflow is `current.yml`, named `Shared`; the only run
    is a success named `Shared` whose workflow path is `former.yml`. CI reads INCOMPLETE, so the member is not
    VERIFIED. On stage E2i9 the display name matched and CI read PASS. Control: the matching path reads PASS."""
    root, sha, wfs = _one_workflow(tmp_path)
    monkeypatch.setattr(L, "_run_list", lambda r, s: [{"status": "completed", "conclusion": "success",
                                                       "workflowName": "Shared", "path": path}])
    ci = L.ci_result(root, sha, True, workflows=wfs)
    assert ci[0] == want, ci
    if want != "PASS":
        assert state(ci=ci) not in ("VERIFIED", "PUBLISHED-NOT-VERIFIED")


@pytest.mark.parametrize("paths,want", [({7: ".github/workflows/current.yml"}, "PASS"),
                                        ({7: ".github/workflows/former.yml"}, "INCOMPLETE"),
                                        ({}, "INCOMPLETE"),
                                        (None, "QUERY-FAILED")])
def test_b181_3_a_listed_run_is_bound_to_its_path_by_workflow_id(tmp_path, monkeypatch, paths, want):
    """B181 finding 3: `gh run list` gives no path, so a run's path is its workflow id's path in the workflow list. An
    id the list does not name covers nothing; a list that cannot be read is QUERY-FAILED, never a match by name."""
    root, sha, wfs = _one_workflow(tmp_path)
    monkeypatch.setattr(L, "_run_list", lambda r, s: [{"status": "completed", "conclusion": "success",
                                                       "workflowName": "Shared", "workflowDatabaseId": 7}])
    monkeypatch.setattr(L, "_workflow_paths", lambda r: paths)
    assert L.ci_result(root, sha, True, workflows=wfs)[0] == want


# --- REVW9's B184 read of stage C2a4: a run list at its limit is not the whole population -------------------------

@pytest.mark.parametrize("rows,count,want", [(49, 49, "PASS"), (50, 51, "QUERY-FAILED"), (50, None, "QUERY-FAILED"),
                                             (50, 50, "PASS")])
def test_b184_1_a_run_list_at_its_limit_counts_only_when_the_rest_count_matches(tmp_path, monkeypatch, rows, count,
                                                                                 want):
    """B184 finding 1 (REVW9's falsifier, DESIGN.md:300). The run list returns 50 successes (its `--limit`) while the
    REST count names 51 runs on the SHA: QUERY-FAILED, so not VERIFIED. On stage C2a4 it read PASS, 50 run(s). A full
    list counts when the REST count names exactly as many runs; below the limit the list stands as before."""
    root, sha, wfs = _one_workflow(tmp_path)
    run = {"status": "completed", "conclusion": "success", "workflowName": "Shared", "path": wfs[0][0]}
    monkeypatch.setattr(L, "_run_list", lambda r, s: [dict(run) for _ in range(rows)])
    monkeypatch.setattr(L, "_api_run_count", lambda r, s: count)
    ci = L.ci_result(root, sha, True, workflows=wfs)
    assert ci[0] == want, ci
    if want != "PASS":
        assert state(ci=ci) != "VERIFIED"


@pytest.mark.parametrize("stdout", ["", "{}", "[null]", "true", '[{"status": "completed"}, 3]'])
def test_b184_1_run_list_output_that_is_not_a_list_of_runs_is_query_failed(monkeypatch, stdout):
    """FWK-OVSR5's C2a4 advisory (5), same class: output that is not a list of run objects is unreadable, so CI reads
    QUERY-FAILED, never an empty list (NO-RUN) or a traceback."""
    monkeypatch.setattr(L.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout, ""))
    assert L._run_list("/r", "abc") is None
    assert L.ci_result("/r", "abc", True, retry_delay=0)[0] == "QUERY-FAILED"


def test_b184_1_a_failed_workflow_folder_probe_is_unavailable_not_no_workflows(tmp_path, monkeypatch):
    """FWK-OVSR5's C2a4 advisory (2), same class: whether the commit has a workflow folder is read from a listing that
    succeeded; a failed listing raises Unavailable, never "no workflows" (which would let a member without CI pass)."""
    root, sha, wfs = _one_workflow(tmp_path)
    real = L.git

    def failing(cwd, *args, **kw):
        if args[:1] == ("ls-tree",) and "--" in args:
            return subprocess.CompletedProcess(args, 128, "", "fatal: synthetic failure")
        return real(cwd, *args, **kw)
    monkeypatch.setattr(L, "git", failing)
    with pytest.raises(L.Unavailable):
        L.committed_workflows(root, sha)


# --- C2e: the D-8 appendix rule applications (DESIGN.md "Rule applications for rows that deferred to another rule";
# named d8_* because the kit's R2-T16..T19 labels already name other tests) ----------------------------------------

def test_c2e_d8_s331_an_operational_state_source_outside_the_inventory_folder_is_named(monkeypatch, tmp_path):
    """D-8, S-331 (DESIGN's R2-T16 (a)): an OPERATIONAL_STATE source whose path resolves outside the inventory folder
    supplied the receipt revision, and the member reached the CI route. The claim is now unmet and the source is named
    (RECEIPT-NOT-ON-REVISION). Control: a source inside the folder supplies its revision."""
    inv = tmp_path / "inv"
    inv.mkdir()
    monkeypatch.setattr(L, "REPO", tmp_path)
    monkeypatch.setattr(L, "OPSTATE", inv / "OPERATIONAL_STATE.json")
    (tmp_path / "outside.json").write_text(json.dumps({"receipt_revision": "abc"}))
    (inv / "inside.json").write_text(json.dumps({"receipt_revision": "abc"}))
    claim = {"effective": "BEHAVIOUR_VERIFIED", "binding": "MATCH", "sources": ["s1"]}
    for path, unconfined in (("inv/../outside.json", True), ("inv/inside.json", False)):
        (inv / "OPERATIONAL_STATE.json").write_text(json.dumps(
            {"agents": [{"agent": "m", "claims": {"receiver_terminal": claim}}], "sources": {"s1": {"path": path}}}))
        idx = L.ingestion_index({})["m"]
        if unconfined:
            assert idx["receipt_revisions"] == [] and idx.get("unconfined") == [path], idx
        else:
            assert idx["receipt_revisions"] == ["abc"] and not idx.get("unconfined"), idx
    st, why = L.classify({**BASE, "receipt_unconfined": ["inv/../outside.json"]})
    assert st == "RECEIPT-NOT-ON-REVISION" and "inv/../outside.json" in why, (st, why)


def test_c2e_d8_s333_a_template_ruling_naming_a_link_out_of_the_framework_root_is_unusable(framework, tmp_path):
    """D-8, S-333 (DESIGN's R2-T16 (b)): a records.json ruling named `template-z-aget`, a symbolic link in the framework
    root to a repository outside it carrying both tags, and the payload was judged against it. It is now unusable, so
    the payload is INCONCLUSIVE. Control: a ruling naming the real template in the root resolves."""
    out = init(tmp_path / "outside" / "repo")
    commit(out, {"z": "1\n"}, "t334", tag="v3.34.0")
    commit(out, {"z": "2\n"}, "t335", tag="v3.35.0")
    (framework / "template-z-aget").symlink_to(out)
    loc = tmp_path / "seat"
    (loc / ".aget").mkdir(parents=True)
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "x"}))
    linked = {"templates": {"seat": {"template": "template-z-aget", "source": "principal, test"}}}
    t, reason = L.resolve_template(loc, "seat", linked)
    assert t is None and "unusable" in reason, (t, reason)
    assert L.classify({**BASE, "template": None, "template_reason": reason})[0] == "INCONCLUSIVE"
    real = {"templates": {"seat": {"template": "template-x-aget", "source": "principal, test"}}}
    assert L.resolve_template(loc, "seat", real)[0] == "template-x-aget"


def _load_kit(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/migration_kit" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(ROOT / "scripts/migration_kit"))
    spec.loader.exec_module(mod)
    return mod


def test_c2e_d8_s216_s277_s350_a_template_only_inferred_from_the_archetype_is_unmet(framework, tmp_path):
    """D-8, S-216/S-277/S-350 (DESIGN's R2-T18): a member whose only usable source is its archetype had its list entry
    written, its launch planned and its payload judged. The list now blocks it, the launch refuses it and the ledger
    reads its payload INCONCLUSIVE. Control: the same member with a recorded template ruling proceeds."""
    PB, PL = _load_kit("prepare_batch"), _load_kit("prepare_launch")
    loc = init(tmp_path / "seat")
    (loc / ".aget").mkdir()
    (loc / ".aget" / "version.json").write_text(json.dumps({"template": "agent", "archetype": "x"}))
    commit(loc, {"README.md": "r\n"}, "seat")
    entry = PB.prepare("seat", str(loc))
    assert "inferred route is unmet" in str(entry.get("blocked")), entry
    with pytest.raises(Exception) as e:
        PL.plan_receiver("seat", str(loc))
    assert "inferred route is unmet" in str(e.value), e.value
    t, reason = L.usable_template(loc, "seat", {})
    assert t is None and L.classify({**BASE, "template": t, "template_reason": reason})[0] == "INCONCLUSIVE"
    ruled = {"templates": {"seat": {"template": "template-x-aget", "source": "principal, test"}}}
    assert L.usable_template(loc, "seat", ruled) == ("template-x-aget", "principal ruling (principal, test)")
