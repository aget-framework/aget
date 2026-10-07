"""push_batch.baseline_equal_ruled: a B8a FAIL passes only under a ruling for THIS commit and an exactly equal failure
set to the member's B6 baseline (one receiver, the principal's typed ruling 2026-09-30T01:00:16Z).

K1 (second rehearsal, 2026-10-01): the ruling was a file the supervisor wrote by hand, and the push tool checked only
that it named the commit and carried a line. Nothing bound the line to the principal. Now the ruling's line must be
found typed in the session's transcript and must name the commit; and record_authority.py writes
the file, so no hand step is needed. F-3 (independent review, 2026-10-02): the ruling line must have one fixed form
(the prefix, then `the failures at SHA are baseline-equal`), and the typed prompt must be the line and nothing more
(both tested below). Not tested, because the check does not have it: the member's name in the line. A hand-written ruling file whose
line was typed still passes (tested below)."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
sys.path.insert(0, str(KIT))


def load(name):
    spec = importlib.util.spec_from_file_location(name, KIT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pb = load("push_batch")
REC = load("record_authority")
SHA = "b" * 40
SID = "abc12345"
FAILS = ["tests/test_a.py::t1", "tests/test_b.py::t2"]
LINE = "GO supervisor - the failures at bbbbbbbb are baseline-equal"
SESSION_START = {"type": "user", "timestamp": "0", "promptSource": "typed", "message": {"content": "session start"}}


def transcript(tmp_path, *lines, first=None):
    d = tmp_path / "projects"
    d.mkdir(exist_ok=True)
    rows = [first or SESSION_START] + [
        {"type": "user", "timestamp": f"t{i}", "promptSource": "typed", "message": {"content": x}}
        for i, x in enumerate(lines)]
    (d / f"{SID}-session.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return d


def evidence(tmp_path, ruling_sha=SHA, base_fails=FAILS, base_verdict="RECORDED", ruling=True, line=LINE):
    ev = tmp_path / "ev"
    ev.mkdir(exist_ok=True)
    # changed at C2c (FWK-OVSR7's C2c pre-read M3, labelled): the record is written as its producer writes it, a run
    # recorded first and the record bound to it; the default read is read_current's
    rid = pb.RBND.start_run("baseline", ev / "baseline_record.json", recorded_by="invoker")
    pb.RBND.write_result("baseline", ev / "baseline_record.json", {"verdict": base_verdict, "failures": base_fails}, rid)
    if ruling:
        (ev / "baseline_equal_ruling.json").write_text(
            json.dumps({"sha": ruling_sha, "line": line, "session": SID}))
    return ev


def sac(fails=FAILS, verdict="FAIL", complete=True):
    # B179 finding 3: suite_at_commit records whether every failing id was read whole
    return {"sha": SHA, "verdict": verdict, "failures": fails, "failures_complete": complete}


def ruled(tmp_path, typed=(LINE,), s=None, **kw):
    return pb.baseline_equal_ruled(evidence(tmp_path, **kw), s or sac(), SHA, projects_dir=transcript(tmp_path, *typed))


def test_equal_failures_under_a_typed_ruling_for_this_commit_pass(tmp_path):
    assert ruled(tmp_path)[0]


def test_no_ruling_refuses(tmp_path):
    assert not ruled(tmp_path, ruling=False)[0]


def test_a_ruling_for_another_commit_refuses(tmp_path):
    assert not ruled(tmp_path, ruling_sha="c" * 40)[0]


def test_a_new_failure_refuses(tmp_path):
    ok, why = ruled(tmp_path, s=sac(FAILS + ["tests/test_c.py::new"]))
    assert not ok and "tests/test_c.py::new" in why


def test_a_missing_failure_refuses(tmp_path):
    assert not ruled(tmp_path, s=sac(FAILS[:1]))[0]


def test_an_inconclusive_run_or_baseline_never_qualifies(tmp_path):
    assert not ruled(tmp_path, s=sac(verdict="INCONCLUSIVE"))[0]
    assert not ruled(tmp_path, base_verdict="INCONCLUSIVE")[0]


def test_an_empty_failure_set_is_not_a_baseline_match(tmp_path):
    assert not ruled(tmp_path, base_fails=[], s=sac([]))[0]


# --- K1: the ruling is bound to a typed line ---------------------------------------------------------------------

def test_a_hand_written_ruling_whose_line_was_never_typed_refuses(tmp_path):
    """FALSIFIER: the file alone must not waive a failing suite."""
    ok, why = ruled(tmp_path, typed=("GO supervisor - something else entirely, typed today",))
    assert not ok and "typed" in why


def test_a_ruling_line_that_names_another_commit_refuses(tmp_path):
    line = "GO supervisor - the failures at ccccccc are baseline-equal"
    ok, why = ruled(tmp_path, typed=(line,), line=line)
    assert not ok and "does not name the commit bbbbbbbb" in why


def test_a_ruling_line_that_is_not_in_the_ruling_form_refuses(tmp_path):
    for line in ("GO supervisor - push batch 1; the two failures ruled baseline-equal",
                 "GO supervisor - push batch 1 at bbbbbbbb whatever the suite says",
                 "GO supervisor - push batch 1 at bbbbbbbb; the two failures ruled baseline-equal"):
        ok, why = ruled(tmp_path, typed=(line,), line=line)
        assert not ok and "the ruling line is not in the one accepted form" in why


def test_a_ruling_line_found_only_in_the_sessions_first_prompt_refuses(tmp_path):
    first = {"type": "user", "timestamp": "0", "promptSource": "typed", "message": {"content": LINE}}
    ev = evidence(tmp_path)
    assert not pb.baseline_equal_ruled(ev, sac(), SHA, projects_dir=transcript(tmp_path, first=first))[0]


def test_the_rehearsals_hand_written_shape_still_reads_when_its_line_was_typed(tmp_path):
    """The second rehearsal's file named its session only inside `source`; that shape stays readable."""
    ev = evidence(tmp_path, ruling=False)
    (ev / "baseline_equal_ruling.json").write_text(json.dumps(
        {"sha": SHA, "line": LINE, "source": f"supervisor session {SID}, typed (written by hand)"}))
    assert pb.baseline_equal_ruled(ev, sac(), SHA, projects_dir=transcript(tmp_path, LINE))[0]


def test_a_typed_ruling_line_that_withholds_the_ruling_refuses(tmp_path):
    """F-3 FALSIFIER: a typed, prefixed line naming the commit and saying baseline must not waive the suite when it
    says no, in any wording (the reviewer's lines of the second review are the last two)."""
    for line in ("GO supervisor - do not treat bbbbbbbb as baseline-equal",
                 "GO supervisor - bbbbbbbb baseline ruling remains unapproved",
                 "GO supervisor - bbbbbbbb baseline ruling is prohibited"):
        ok, why = ruled(tmp_path, typed=(line,), line=line)
        assert not ok and "the ruling line is not in the one accepted form" in why


def test_a_ruling_line_typed_inside_a_longer_prompt_refuses(tmp_path):
    """F-3: the recorded ruling line is clean, the typed prompt went on with a condition."""
    ok, why = ruled(tmp_path, typed=(LINE + " provided CI agrees",))
    assert not ok and "not exactly the ruling line" in why


# --- K1: the recorder writes the file, so no hand step is needed (a hand-written file still passes) ---------------

def recorder_world(tmp_path, typed=(LINE,), sac_sha=SHA):
    proj = transcript(tmp_path, *typed)
    ev_root = tmp_path / "evidence"
    (ev_root / "some-aget").mkdir(parents=True)
    (ev_root / "some-aget" / "suite_at_commit.json").write_text(json.dumps({"sha": sac_sha, "verdict": "FAIL"}))
    rec = tmp_path / "records.json"
    rec.write_text("{}")
    return proj, ev_root, rec


def test_the_recorder_writes_a_ruling_bound_to_the_typed_line_and_the_full_commit(tmp_path):
    proj, ev_root, rec = recorder_world(tmp_path)
    code = REC.main(["--session", SID, "--baseline-equal", "some-aget=bbbbbbbb", "--ruling-line", LINE,
                     "--evidence", str(ev_root)], records=rec, projects_dir=proj)
    assert code == 0
    ruling = json.loads((ev_root / "some-aget" / "baseline_equal_ruling.json").read_text())
    assert ruling["sha"] == SHA and ruling["line"] == LINE and ruling["session"] == SID
    assert "record_authority.py" in ruling["source"]
    assert rec.read_text() == "{}"                      # a ruling alone does not rewrite the records file


def test_the_recorder_refuses_an_untyped_ruling_line_and_writes_nothing(tmp_path):
    proj, ev_root, rec = recorder_world(tmp_path, typed=("GO supervisor - a different line typed in this session",))
    code = REC.main(["--session", SID, "--baseline-equal", "some-aget=bbbbbbbb", "--ruling-line", LINE,
                     "--evidence", str(ev_root)], records=rec, projects_dir=proj)
    assert code == 1 and not (ev_root / "some-aget" / "baseline_equal_ruling.json").exists()


def test_the_recorder_refuses_a_commit_the_suite_record_does_not_name(tmp_path):
    proj, ev_root, rec = recorder_world(tmp_path, sac_sha="c" * 40)
    code = REC.main(["--session", SID, "--baseline-equal", "some-aget=bbbbbbbb", "--ruling-line", LINE,
                     "--evidence", str(ev_root)], records=rec, projects_dir=proj)
    assert code == 1 and not (ev_root / "some-aget" / "baseline_equal_ruling.json").exists()


def test_the_recorder_does_not_overwrite_an_existing_ruling(tmp_path):
    proj, ev_root, rec = recorder_world(tmp_path)
    (ev_root / "some-aget" / "baseline_equal_ruling.json").write_text("{}")
    code = REC.main(["--session", SID, "--baseline-equal", "some-aget=bbbbbbbb", "--ruling-line", LINE,
                     "--evidence", str(ev_root)], records=rec, projects_dir=proj)
    assert code == 1 and (ev_root / "some-aget" / "baseline_equal_ruling.json").read_text() == "{}"


def test_b179_3_a_b8a_failure_list_with_a_cut_id_is_not_baseline_equal(tmp_path):
    """B179 finding 3, at the ruled route: a B8a FAIL whose failing ids were not all read whole (`failures_complete`
    false) is not compared with the baseline, under a typed ruling and equal-looking sets. On stage C2a the cut ids
    were compared."""
    ok, why = ruled(tmp_path, s=sac(complete=False))
    assert not ok and "complete" in why, why


def test_c2a12_c2b_preread_2_the_fail_route_judges_the_baseline_record_it_bound(tmp_path):
    """FWK-OVSR6's C2b pre-read 2 (MEDIUM, reproduced): the FAIL route bound the baseline record (baseline_bound) and
    then compared failures from a second read, so a record rewritten in between was compared unbound. The gate now
    reads it once and passes it to both. Here the file on disk differs from the bound record: the bound one decides."""
    ev = evidence(tmp_path, base_fails=["tests/test_other.py::t9"])       # what a second read would see
    bound = {"verdict": "RECORDED", "failures": FAILS}
    d = transcript(tmp_path, LINE)
    assert pb.baseline_equal_ruled(ev, sac(), SHA, projects_dir=d, base=bound) == (True, "")
    assert pb.baseline_equal_ruled(ev, sac(), SHA, projects_dir=d)[0] is False             # control: disk record
    r = {"aget": "m", "head": SHA}
    assert pb.baseline_bound(ev, r, {}, base=None) == "no readable baseline record"
    src = (KIT / "push_batch.py").read_text()
    # changed at C2c (labelled): the one read is read_current's (R2-T17), its reason passed with the record
    assert "baseline_bound(ev, r, launch, base=base, why=bwhy)" in src and "baseline_equal_ruled(ev, sac, head, base=base)" in src


# --- weekly-train:R17 (F3): record_authority --policy records an approval of one member's narrowed selection -------

def _policy_world(tmp_path, selection):
    RA, AR, RBD = load("record_authority"), load("after_run_check"), load("result_binding")
    ev = tmp_path / "ev"
    (ev / "m1").mkdir(parents=True)
    (ev / "m1" / "baseline_record.json").write_text(json.dumps({"aget": "m1", "selection": selection}))
    records = tmp_path / "records.json"
    records.write_text("{}")
    return RA, AR, RBD.selection_digest(selection), ev, records


def test_f3_r17_a_typed_approval_of_the_baselines_selection_is_recorded_and_read_back(tmp_path):
    """weekly-train:R17: the approval line has one fixed form, names the member and the baseline's selection digest
    (8 or more hex), and is typed as a whole prompt; the recorder writes `policy_approvals[aget][digest]`, and F reads
    it back (each entry's line checked again). Refused: a line naming another member, another selection, or never
    typed; a member with no baseline selection."""
    RA, AR, dg, ev, records = _policy_world(tmp_path, {"roots": ["tests"], "ignored": ["templates"]})
    good = f"GO supervisor - the narrowed suite of m1 at selection {dg[:12]} is approved"
    pd = transcript(tmp_path, good)
    base = ["--session", SID, "--evidence", str(ev)]
    assert RA.main(base + ["--policy", f"m1={dg[:12]}", "--policy-line", good.replace("m1 ", "m2 ")],
                   records=records, projects_dir=pd) == 1
    assert RA.main(base + ["--policy", "m1=deadbeefdead", "--policy-line", good], records=records, projects_dir=pd) == 1
    never = f"GO supervisor - the narrowed suite of m1 at selection {dg[:10]} is approved"
    assert RA.main(base + ["--policy", f"m1={dg[:10]}", "--policy-line", never], records=records, projects_dir=pd) == 1
    assert json.loads(records.read_text()) == {}
    assert RA.main(base + ["--policy", f"m1={dg[:12]}", "--policy-line", good], records=records, projects_dir=pd) == 0
    assert dg in json.loads(records.read_text())["policy_approvals"]["m1"]
    import batch_authority as BA_mod
    real = BA_mod.verify_policy
    BA_mod.verify_policy = lambda e, a, d, p=None: real(e, a, d, pd)
    try:
        assert AR.policy_approvals("m1", records) == {dg} and AR.policy_approvals("m2", records) == set()
    finally:
        BA_mod.verify_policy = real
