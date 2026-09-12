"""C-34-17 — the value gate gains a forecast mode.

Armed both polarities. The negatives are the point: this command exists because the
validator ABORTS where a forecast must REPORT, and because a present source field is not
accepted evidence. Each test below fails if either property regresses.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CMD = REPO / "scripts" / "forecast_value_gate.py"

PASS, FAIL, INERT, UNAVAILABLE = "PASS", "FAIL", "INERT", "UNAVAILABLE"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "src.md").write_text("the pattern is here")
    return tmp_path


def row(rid, su, v1, cls, *, path="src.md", pat="the pattern is here"):
    return {"id": rid, "disposition": "SELECT", "tier": "T1", "su": su,
            "predicted_v1": v1, "class": cls, "source": {"path": path, "pattern": pat}}


def packet(rows, **kw):
    base = {"cap_su": 10, "pool_allows_two_l3": True, "candidates": rows}
    base.update(kw)
    return base


def run(root: Path, pkt: dict, *extra: str):
    p = root / "packet.json"
    p.write_text(json.dumps(pkt))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(p), "--repo-root", str(root), "--json", *extra],
        capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return proc.returncode, payload


def fc(root, pkt, *extra):
    code, payload = run(root, pkt, *extra)
    return code, payload["forecast"]


# --- positive -------------------------------------------------------------------

def test_a_clean_slate_passes_every_limb_and_exits_zero(root):
    code, res = fc(root, packet([row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")]))
    assert code == 0
    assert res["overall"] == PASS
    assert {v["verdict"] for v in res["limbs"].values()} <= {PASS, INERT}


def test_every_limb_is_reported_not_just_the_failing_one(root):
    _, res = fc(root, packet([row("A", 4, "L3", "capability")]))
    for limb in ("CON-FLOOR-1", "CON-FLOOR-2", "CON-CAPABILITY-SHARE", "CON-AMBITION-1",
                 "CON-AMBITION-2", "CON-AMBITION", "CAP-CEILING", "CON-EVIDENCE"):
        assert limb in res["limbs"], f"{limb} missing from the forecast"
        assert set(res["limbs"][limb]["contract"]) >= {
            "subject_bound", "subject_reached", "affirming_evidence",
            "predicate_discriminating", "definite"}


def test_unavailable_and_inert_limbs_are_indefinite_and_name_their_limit(root):
    pkt = packet([row("A", 4, "L3", "capability")])
    del pkt["cap_su"]
    _, res = fc(root, pkt)
    for name in ("CON-AMBITION-1", "CAP-CEILING"):
        assert not res["limbs"][name]["contract"]["definite"]
        assert res["limbs"][name]["limit"]


# --- negative: it must not abort at the first failure ---------------------------

def test_it_reports_every_failing_limb_rather_than_aborting_at_the_first(root):
    """Named limbs, not a count. `len(failing) >= 3` let any single limb be permanently green."""
    code, res = fc(root, packet(
        [row("A", 4, "L1", "governance"), row("B", 3, "L1", "governance")], cap_su=100))
    for limb in ("CON-FLOOR-1", "CON-FLOOR-2", "CON-CAPABILITY-SHARE", "CON-AMBITION-1"):
        assert res["limbs"][limb]["verdict"] == FAIL, f"{limb} must FAIL on an all-bad packet"
    assert code == 1


# --- per-limb isolation: each limb driven to FAIL with the others satisfied ---------
# Added after mutation testing measured 6 of 8 injected regressions SURVIVING the old
# count-based net -- including zeroing all three rubric thresholds.

@pytest.mark.parametrize("limb,rows,cap", [
    ("CON-FLOOR-1", [("A", 4, "L2", "capability"), ("B", 3, "L2", "capability")], 10),
    ("CON-FLOOR-2", [("A", 2, "L3", "capability"), ("B", 5, "L1", "capability")], 10),
    ("CON-CAPABILITY-SHARE", [("A", 4, "L3", "governance"), ("B", 3, "L3", "governance")], 10),
    ("CON-AMBITION-1", [("A", 4, "L3", "capability"), ("B", 3, "L3", "capability")], 1000),
    ("CAP-CEILING", [("A", 4, "L3", "capability"), ("B", 3, "L3", "capability")], 5),
])
def test_each_limb_fails_in_isolation(root, limb, rows, cap):
    code, res = fc(root, packet([row(*r) for r in rows], cap_su=cap))
    assert res["limbs"][limb]["verdict"] == FAIL, f"{limb} did not fail when it should"
    assert code == 1


def test_zeroing_a_threshold_would_be_caught(root):
    """Guards the mutation that survived: the floors must actually bind."""
    _, res = fc(root, packet([row("A", 2, "L3", "capability"), row("B", 5, "L1", "capability")]))
    assert res["limbs"]["CON-FLOOR-2"]["functional_share_pct"] < res["limbs"]["CON-FLOOR-2"]["floor_pct"]
    assert res["limbs"]["CON-FLOOR-2"]["verdict"] == FAIL


def test_the_functional_floor_matches_the_validators_literal(root):
    """M2: the validator uses a literal 0.33 for CON-FLOOR, not 1/3.

    At exactly 33.0% the gate PASSes; a 1/3 floor would FAIL and the forecast would be wrong
    in the band it exists to predict.
    """
    _, res = fc(root, packet([row("A", 33, "L3", "capability"), row("B", 67, "L1", "capability")],
                             cap_su=1000))
    assert res["limbs"]["CON-FLOOR-2"]["functional_share_pct"] == 33.0
    assert res["limbs"]["CON-FLOOR-2"]["verdict"] == PASS, "must mirror the validator's 0.33"


def test_the_disposition_and_tier_filters_are_load_bearing(root):
    """Dropping either filter survived mutation testing. A DEFER row must not be scored."""
    # The two filters MASK each other: a row that is both DEFER and tier=DEFER is excluded
    # by either one alone, so dropping the disposition filter survived. Each row below can be
    # excluded by exactly ONE filter.
    pkt = packet([row("A", 4, "L3", "capability")])
    pkt["candidates"].append({**row("B", 96, "L1", "governance"),
                              "disposition": "DEFER"})          # tier stays T1
    _, res = fc(root, pkt)
    assert res["selected_su"] == 4, "a DEFER row must not enter the scored scope"
    pkt2 = packet([row("A", 4, "L3", "capability")])
    pkt2["candidates"].append({**row("C", 96, "L1", "governance"), "tier": "T2"})
    _, res2 = fc(root, pkt2)
    assert res2["selected_su"] == 4, "a non-T1 row must not enter the scored scope"


# --- negative: evidence semantics, the crux of the acceptance -------------------

def test_a_present_but_unresolvable_source_is_UNAVAILABLE_not_PASS(root):
    """Equating source PRESENCE with evidence ACCEPTANCE is the defect this row fixes."""
    code, res = fc(root, packet([row("A", 7, "L3", "capability", path="does-not-exist.md")]))
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] == UNAVAILABLE
    assert code == 2, "an unscoreable limb must never exit 0"


def test_a_readable_source_whose_pattern_is_absent_FAILS(root):
    """Distinct from UNAVAILABLE: here the evidence was checkable and did not check out."""
    _, res = fc(root, packet([row("A", 7, "L3", "capability", pat="not in the file")]))
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] == FAIL


def test_blank_locators_do_not_buy_a_pass(root):
    _, res = fc(root, packet([row("A", 7, "L3", "capability", path="", pat="")]))
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] != PASS


def test_the_three_evidence_states_are_distinguished(root):
    _, res = fc(root, packet([
        row("ok", 3, "L3", "capability"),
        row("unresolved", 2, "L3", "capability", pat="absent"),
        row("unavailable", 2, "L3", "capability", path="gone.md"),
    ]))
    ev = res["limbs"]["CON-EVIDENCE"]
    assert ev["resolved"] == ["ok"]
    assert ev["unresolved"] == ["unresolved"]
    assert ev["unavailable"] == ["unavailable"]


# --- negative: the validator's other abort points become reports ----------------

def test_an_absent_cap_makes_only_the_cap_limbs_unavailable(root):
    """The validator raises 'cap_su must be positive'. The forecast still scores the rest."""
    pkt = packet([row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")])
    del pkt["cap_su"]
    code, res = fc(root, pkt)
    assert res["limbs"]["CON-AMBITION-1"]["verdict"] == UNAVAILABLE
    assert res["limbs"]["CAP-CEILING"]["verdict"] == UNAVAILABLE
    assert res["limbs"]["CON-FLOOR-1"]["verdict"] == PASS
    assert code == 2


def test_cap_can_be_supplied_on_the_command_line(root):
    pkt = packet([row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")])
    del pkt["cap_su"]
    _, res = fc(root, pkt, "--cap", "10")
    assert res["limbs"]["CON-AMBITION-1"]["verdict"] == PASS


def test_exceeding_the_cap_is_reported_not_raised(root):
    """The validator raises 'selected scope exceeds capacity'."""
    _, res = fc(root, packet([row("A", 40, "L3", "capability"), row("B", 30, "L3", "capability")]))
    assert res["limbs"]["CAP-CEILING"]["verdict"] == FAIL


def test_pool_flag_disagreement_is_surfaced_not_raised(root):
    """The validator raises when pool_allows_two_l3 disagrees with the packet."""
    _, res = fc(root, packet(
        [row("A", 4, "L3", "capability"), row("B", 3, "L2", "capability")], pool_allows_two_l3=True))
    assert res["notes"], "the disagreement must be surfaced"
    assert "validator would refuse" in " ".join(res["notes"])


# --- non-firing is not passing ---------------------------------------------------

def test_limb_two_is_inert_when_the_pool_cannot_fire_it_and_does_not_read_as_pass(root):
    _, res = fc(root, packet(
        [row("A", 4, "L3", "capability"), row("B", 3, "L2", "capability")], pool_allows_two_l3=False))
    assert res["limbs"]["CON-AMBITION-2"]["verdict"] == INERT
    assert res["limbs"]["CON-AMBITION"]["verdict"] == PASS


def test_unclassed_rows_make_capability_share_unavailable_not_zero(root):
    """A missing class is not a 0% share; it is a thing not known."""
    r = row("A", 7, "L3", "capability")
    del r["class"]
    _, res = fc(root, packet([r]))
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE


# --- forecast vs actual ----------------------------------------------------------

def test_forecast_is_compared_against_the_actual_locked_selection(root):
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")])))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 4, "L1", "governance")], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root), "--json"], capture_output=True, text=True)
    cmp_ = json.loads(proc.stdout)["comparison"]
    assert cmp_["forecast_was_accurate"] is False
    assert cmp_["limbs_disagreeing"]
    assert cmp_["su_delta"] == -3
    assert cmp_["l3_dropped"] == ["A", "B"]


# --- hygiene ---------------------------------------------------------------------

def test_a_malformed_packet_exits_three_and_never_reports_a_pass(root):
    bad = root / "bad.json"
    bad.write_text("{not json")
    proc = subprocess.run([sys.executable, str(CMD), "--packet", str(bad), "--repo-root", str(root)],
                          capture_output=True, text=True)
    assert proc.returncode == 3
    assert PASS not in proc.stdout

def test_the_command_is_non_mutating(root):
    before = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    run(root, packet([row("A", 7, "L3", "capability")]))
    after = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    # the packet we wrote is ours; every pre-existing file must be untouched
    for p, mt in before.items():
        assert after.get(p) == mt, f"{p} was mutated"


def test_self_test_passes(root):
    proc = subprocess.run([sys.executable, str(CMD), "--self-test"], capture_output=True, text=True)
    assert proc.returncode == 0 and "self-test: PASS" in proc.stdout


# ===================================================================================
# Regressions from the independent review of 2026-09-09. Each reproduces a defect that
# a green 17-test suite did not detect.
# ===================================================================================

def validator_shaped_row(rid, su, v1, initiative_path):
    """A row in the validator's ACTUAL schema: initiative_path, and NO `class` field."""
    return {"id": rid, "disposition": "SELECT", "tier": "T1", "su": su, "predicted_v1": v1,
            "owner": "x", "initiative_path": initiative_path, "dependency_state": "PROCEED",
            "principal_ruling": "none", "source": {"path": "src.md", "pattern": "the pattern is here"}}


def test_B1_a_validator_shaped_packet_scores_capability_share(root):
    """B1: the validator's CANDIDATE_KEYS has no `class`; class comes from initiative_path.

    Reading only inline/top-level class made this limb UNAVAILABLE on EVERY real packet, so the
    command could never return 0 on the artifact it claims to read.
    """
    (root / "planning" / "initiatives").mkdir(parents=True)
    (root / "planning" / "initiatives" / "INIT-CAP.md").write_text(
        "**Class**: capability\n**Status**: ACTIVE\n")
    (root / "planning" / "initiatives" / "INIT-GOV.md").write_text(
        "**Class**: governance\n**Status**: ACTIVE\n")
    pkt = {"cap_su": 10, "pool_allows_two_l3": True, "candidates": [
        validator_shaped_row("A", 4, "L3", "planning/initiatives/INIT-CAP.md"),
        validator_shaped_row("B", 3, "L3", "planning/initiatives/INIT-GOV.md")]}
    code, res = fc(root, pkt)
    share = res["limbs"]["CON-CAPABILITY-SHARE"]
    assert share["verdict"] != UNAVAILABLE, "class must resolve from initiative_path"
    assert share["capability_share_pct"] == pytest.approx(57.1, abs=0.1)
    assert code == 0


def test_B3_a_duplicate_id_is_rejected_and_never_folds_unavailable_into_pass(root):
    """B3: duplicates double-counted SigmaSU, counted one L3 twice, and let a later row's
    resolvable evidence overwrite an earlier row's UNAVAILABLE -> PASS, exit 0."""
    pkt = packet([row("A", 4, "L3", "capability", path="MISSING.md"),
                  row("A", 4, "L3", "capability")])
    code, payload = run(root, pkt)
    assert code == 3, "a duplicate id must be rejected outright, not scored"
    assert payload.get("overall") != PASS


def test_B4_a_divergent_comparison_cannot_exit_zero(root):
    """B4: the comparison rendered a divergence and the process still exited 0."""
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                      row("B", 3, "L3", "capability")])))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 4, "L1", "governance")], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root)], capture_output=True, text=True)
    assert proc.returncode != 0, "a forecast that disagreed with the lock must not exit 0"


def test_M1_malformed_rows_exit_three_rather_than_crashing(root):
    """M1: KeyError/TypeError tracebacks exited 1 -- indistinguishable from a failing gate."""
    for bad in ({"id": "A", "disposition": "SELECT", "tier": "T1", "predicted_v1": "L3"},
                {"id": "A", "disposition": "SELECT", "tier": "T1", "su": "4", "predicted_v1": "L3"},
                {"disposition": "SELECT", "tier": "T1", "su": 4, "predicted_v1": "L3"},
                {"id": "A", "disposition": "SELECT", "tier": "T1", "su": 4, "predicted_v1": "L9"}):
        code, _ = run(root, {"cap_su": 10, "pool_allows_two_l3": True, "candidates": [bad]})
        assert code == 3, f"malformed row {bad} should exit 3, got {code}"


def test_M1_an_unreadable_packet_exits_three(root):
    binary = root / "b.json"
    binary.write_bytes(b"\x00\xff\xfe binary")
    proc = subprocess.run([sys.executable, str(CMD), "--packet", str(binary),
                           "--repo-root", str(root)], capture_output=True, text=True)
    assert proc.returncode == 3
    proc2 = subprocess.run([sys.executable, str(CMD), "--packet", str(root),
                            "--repo-root", str(root)], capture_output=True, text=True)
    assert proc2.returncode == 3, "a directory as --packet must exit 3, not 1"


def test_M3_a_source_path_escaping_the_root_is_unavailable(root):
    """M3: an absolute source.path discarded repo_root -- /etc/hosts scored PASS."""
    _, res = fc(root, packet([row("A", 7, "L3", "capability",
                                  path="/etc/hosts", pat="localhost")]))
    ev = res["limbs"]["CON-EVIDENCE"]
    assert ev["verdict"] == UNAVAILABLE
    assert "does not resolve within the supplied root" in json.dumps(ev["detail"])


def test_M3_a_traversal_path_is_unavailable(root):
    _, res = fc(root, packet([row("A", 7, "L3", "capability",
                                  path="../../../../etc/hosts", pat="localhost")]))
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] == UNAVAILABLE


# ===================================================================================
# Round-two review, 2026-09-09. BLOCKING-1 is the same escape hole the first round's M3
# repair closed on source.path, reintroduced on the field that repair added.
# ===================================================================================

def init_file(root: Path, rel: str, cls: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"**Class**: {cls}\n**Status**: ACTIVE\n")
    return p


def vrow(rid, su, v1, initiative_path):
    return {"id": rid, "disposition": "SELECT", "tier": "T1", "su": su, "predicted_v1": v1,
            "owner": "x", "initiative_path": initiative_path, "dependency_state": "PROCEED",
            "principal_ruling": "none",
            "source": {"path": "src.md", "pattern": "the pattern is here"}}


def test_BLOCKING1_an_initiative_path_outside_the_root_is_unavailable(root):
    """`outside` must be genuinely outside: the first version of this test put it under
    tmp_path, which IS the root, so it proved nothing."""
    import tempfile
    outside = Path(tempfile.mkdtemp())
    assert not str(outside).startswith(str(root)), "fixture must be outside the root"
    (outside / "EVIL.md").write_text("**Class**: capability\n**Status**: ACTIVE\n")
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [vrow("A", 4, "L3", str(outside / "EVIL.md")),
                          vrow("B", 3, "L3", str(outside / "EVIL.md"))]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE


def test_BLOCKING1_a_traversal_initiative_path_is_unavailable(root):
    (root.parent / "EVIL.md").write_text("**Class**: capability\n**Status**: ACTIVE\n")
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [vrow("A", 7, "L3", "../EVIL.md")]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE


def test_MAJOR2_the_class_pattern_is_the_validators_non_whitespace_form(root):
    """`\\w+` truncated 'capability-adjacent' to 'capability' -- toward the favourable answer."""
    init_file(root, "planning/initiatives/INIT-X.md", "capability-adjacent")
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [vrow("A", 7, "L3", "planning/initiatives/INIT-X.md")]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE, \
        "a hyphenated class must not be truncated into 'capability'"


def test_MAJOR3_an_unresolvable_initiative_path_does_not_fall_back_to_an_inline_class(root):
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [{**vrow("A", 7, "L3", "planning/initiatives/TYPO.md"),
                           "class": "capability"}]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE
    assert any("does not resolve" in n for n in res["notes"]), "the broken pointer must surface"


def test_MAJOR7_a_wholly_different_selection_is_not_an_accurate_forecast(root):
    """Both slates passed the same limbs, so limb-agreement alone called it accurate."""
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                      row("B", 3, "L3", "capability")], cap_su=10)))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("X", 40, "L3", "capability"),
                                       row("Y", 30, "L3", "capability")], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root), "--json"], capture_output=True, text=True)
    cmp_ = json.loads(proc.stdout)["comparison"]
    assert cmp_["limbs_agree"] is True
    assert cmp_["selection_agrees"] is False
    assert cmp_["forecast_was_accurate"] is False
    assert proc.returncode != 0


def test_MINOR8_divergence_exits_one_even_when_a_limb_is_unavailable(root):
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 7, "L3", "capability", path="GONE.md")])))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 7, "L1", "governance")], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root)], capture_output=True, text=True)
    assert proc.returncode == 1, "a definite divergence outranks 'cannot certify'"


# --- the five mutants that survived round two -------------------------------------

def test_capability_share_passes_at_exactly_one_third(root):
    _, res = fc(root, packet([row("A", 1, "L3", "capability"),
                              row("B", 2, "L2", "governance")]))
    s = res["limbs"]["CON-CAPABILITY-SHARE"]
    assert s["capability_share_pct"] == pytest.approx(33.3, abs=0.1)
    assert s["verdict"] == PASS, "the floor is >=, not >"


def test_a_non_positive_su_is_rejected(root):
    for bad in (0, -1):
        code, _ = run(root, packet([{**row("A", 1, "L3", "capability"), "su": bad}]))
        assert code == 3, f"su={bad} must be rejected"


def test_a_blank_source_pattern_is_unavailable_not_a_pass(root):
    """Isolated from the path check: the path resolves, only the pattern is blank."""
    _, res = fc(root, packet([row("A", 7, "L3", "capability", pat="")]))
    ev = res["limbs"]["CON-EVIDENCE"]
    assert ev["verdict"] == UNAVAILABLE
    assert "pattern" in json.dumps(ev["detail"])


def test_a_non_dict_candidate_is_rejected(root):
    code, _ = run(root, {"cap_su": 10, "pool_allows_two_l3": True,
                         "candidates": ["not-an-object"]})
    assert code == 3


def test_the_inline_class_is_case_insensitive(root):
    _, res = fc(root, packet([{**row("A", 7, "L3", "capability"), "class": "Capability"}]))
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == PASS


# --- round three ---------------------------------------------------------------------

def test_MAJORC_an_initiative_without_Status_is_refused_like_the_validator_does(root):
    """The validator's initiative_metadata requires BOTH Class and Status."""
    d = root / "planning" / "initiatives"
    d.mkdir(parents=True)
    (d / "INIT-X.md").write_text("**Class**: capability\n")          # no Status
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [vrow("A", 7, "L3", "planning/initiatives/INIT-X.md")]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE
    assert any("Status" in n for n in res["notes"])


def test_MAJORC_a_yaml_class_fallback_is_not_accepted(root):
    """The validator has no `class:` route; accepting one passed packets it refuses."""
    d = root / "planning" / "initiatives"
    d.mkdir(parents=True)
    (d / "INIT-Y.md").write_text("---\nclass: capability\n---\n")
    pkt = {"cap_su": 10, "pool_allows_two_l3": True,
           "candidates": [vrow("A", 7, "L3", "planning/initiatives/INIT-Y.md")]}
    _, res = fc(root, pkt)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] == UNAVAILABLE
    assert any("would refuse" in n for n in res["notes"])


def test_MAJORE_a_different_selection_with_the_same_L3_set_is_not_accurate(root):
    """selection_agrees compared SigmaSU and the L3 set only, so {A,B} and {A,ZZZ} matched."""
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                      row("B", 3, "L2", "capability")])))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                       row("ZZZ", 3, "L2", "capability")])))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root), "--json"], capture_output=True, text=True)
    cmp_ = json.loads(proc.stdout)["comparison"]
    assert cmp_["selection_agrees"] is False
    assert cmp_["rows_added"] == ["ZZZ"] and cmp_["rows_dropped"] == ["B"]
    assert proc.returncode != 0


@pytest.mark.parametrize("break_clause,pre_rows,post_rows", [
    ("su only", [("A", 4, "L3", "capability")], [("A", 40, "L3", "capability")]),
    ("ids only", [("A", 4, "L3", "capability")], [("Z", 4, "L3", "capability")]),
])
def test_MAJORE_each_selection_clause_fails_alone(root, break_clause, pre_rows, post_rows):
    """Both clauses survived mutation because one fixture broke them together."""
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row(*r) for r in pre_rows], cap_su=100)))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row(*r) for r in post_rows], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root), "--json"], capture_output=True, text=True)
    assert json.loads(proc.stdout)["comparison"]["selection_agrees"] is False, break_clause


def test_MAJORD_a_note_on_the_locked_packet_reaches_the_output_and_the_exit_code(root):
    """compare() dropped the locked packet's notes, so a packet the validator would refuse
    was reported as an accurate forecast, exit 0."""
    pre = root / "pre.json"
    pre.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                      row("B", 3, "L2", "capability")],
                                     pool_allows_two_l3=False)))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                       row("B", 3, "L2", "capability")],
                                      pool_allows_two_l3=True)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root)], capture_output=True, text=True)
    assert "LOCKED-PACKET NOTE" in proc.stdout
    assert "would refuse" in proc.stdout
    assert proc.returncode != 0


def test_MINORL_the_no_rows_result_has_the_same_shape_as_a_normal_one(root):
    _, empty = fc(root, {"cap_su": 10, "pool_allows_two_l3": True,
                         "candidates": [{**row("A", 4, "L3", "capability"),
                                         "disposition": "DEFER"}]})
    _, normal = fc(root, packet([row("A", 7, "L3", "capability")]))
    assert set(empty) == set(normal), f"two result shapes: {set(empty) ^ set(normal)}"


# --- round four ------------------------------------------------------------------------

def test_F7_overall_is_UNAVAILABLE_when_any_limb_is(root):
    """The docstring's load-bearing sentence is 'UNAVAILABLE never folds into PASS', and
    `overall` -- the published headline field -- had no test asserting it."""
    _, res = fc(root, packet([row("A", 7, "L3", "capability", path="GONE.md")]))
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] == UNAVAILABLE
    assert res["overall"] == UNAVAILABLE, "overall must not fold UNAVAILABLE into PASS"


def test_F7_the_functional_share_counts_L2_as_well_as_L3(root):
    """The validator's functional set is {L2, L3}; counting L3 only survived mutation."""
    _, res = fc(root, packet([row("A", 5, "L3", "capability"),
                              row("B", 5, "L2", "capability")]))
    assert res["functional_su"] == 10, "an L2 row is functional"
    assert res["limbs"]["CON-FLOOR-2"]["functional_share_pct"] == 100.0


def test_F4_cap_override_does_not_rewrite_the_locked_packets_cap(root):
    """--cap applied to the lock scored PASS on a lock the gate refuses, exit 0."""
    pre = root / "pre.json"
    pkt = packet([row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")])
    del pkt["cap_su"]
    pre.write_text(json.dumps(pkt))
    post = root / "post.json"
    post.write_text(json.dumps(packet([row("A", 4, "L3", "capability"),
                                       row("B", 3, "L3", "capability")], cap_su=100)))
    proc = subprocess.run(
        [sys.executable, str(CMD), "--packet", str(pre), "--compare-locked", str(post),
         "--repo-root", str(root), "--cap", "10", "--json"], capture_output=True, text=True)
    payload = json.loads(proc.stdout)
    assert payload["comparison"]["forecast_was_accurate"] is False, \
        "the lock fails CON-AMBITION-1 at its own cap of 100; the override must not hide it"
    assert proc.returncode != 0


def test_F5_a_hypothetical_slate_route_is_noted(root):
    """Both retained class routes score packets the validator refuses; say so, as the
    pool-flag disagreement already does."""
    _, res = fc(root, packet([row("A", 7, "L3", "capability")]))
    assert any("would refuse this packet" in n for n in res["notes"])
