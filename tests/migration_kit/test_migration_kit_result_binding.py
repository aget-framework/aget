"""Gate 3 of the v3.36.0 kit design pass (v336-release:R28): R2, result binding.

Each behavioural test fails on 34353311 for the defect it names and passes after the change; the receipt-grammar
table tests a module that does not exist at 34353311 (its behavioural counterparts are the ledger and push tests).
Everything runs on tmp_path fixtures; nothing is launched or pushed.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(loc, *a):
    return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          check=True, capture_output=True, text=True).stdout.strip()


ATTEMPT = "att-1"


def receipt(terminal, attempt=ATTEMPT, extra=""):
    return f"# Receipt\n\n## Attempt {attempt}\n\nsteps done\n{extra}\nTerminal: {terminal}\n"


# --- the ledger (wrapper r7 F-1) ---------------------------------------------------------------------------------

BASE_OBS = {"remote_version": "3.35.0", "local_version": "3.35.0", "template": "template-x-aget",
            "payload_findings": [], "receipt_on_revision": True, "root_workflows": ["ci.yml"], "shared_root": False,
            "checks_compared": True, "checks_changed": False, "ci": ("PASS", "1 run(s)")}


@pytest.mark.parametrize("terminal", ["REJECTED", "CANNOT-RUN", "UNKNOWN", "accepted"])
@pytest.mark.parametrize("route", ["ci", "no-ci"])
def test_r2_t1_ledger_counts_only_a_success_terminal(terminal, route):
    """R2-T1 (S-147, S-149; wrapper r7 F-1). A REJECTED, CANNOT-RUN, UNKNOWN or lower-case terminal must not reach
    VERIFIED or PUBLISHED-NO-CI. At 34353311 fleet_ledger.py:434 tests only truthiness, so each counts."""
    L = load("fleet_ledger")
    o = {**BASE_OBS, "receipt_terminal": terminal}
    if route == "no-ci":
        o["root_workflows"] = []
    state, why = L.classify(o)
    assert state == "RECEIPT-NOT-SUCCESS", (state, why)
    assert L.classify({**o, "receipt_terminal": "ACCEPTED"})[0] in ("VERIFIED", "PUBLISHED-NO-CI")   # control


def ledger_member(tmp_path, text):
    m = tmp_path / "m"
    m.mkdir(parents=True)
    git(m, "init", "-q")
    (m / "docs").mkdir()
    (m / "docs" / "R.md").write_text(text)
    git(m, "add", "-A")
    git(m, "commit", "-q", "-m", "receipt")
    return m, git(m, "rev-parse", "HEAD")


def test_r2_t2_t19_the_ledger_rereads_the_recorded_receipt(tmp_path):
    """R2-T2 and R2-T19 (S-148). records.json says ACCEPTED for attempt att-1, and the receipt at that revision ends
    `Terminal: REJECTED` in that section: RECEIPT-NOT-SUCCESS. An entry without `attempt` or `receipt_path` is unmet.
    A section holding `Terminal: ACCEPTED` and a second `Terminal: UNKNOWN` is unmet. (New API: at 34353311 the
    ledger never re-reads the file; its behavioural counterpart there is R2-T1.)"""
    L = load("fleet_ledger")
    m, rev = ledger_member(tmp_path, receipt("REJECTED"))
    ing = {"terminal": "ACCEPTED", "receipt_revisions": [rev], "attempt": ATTEMPT, "receipt_path": "docs/R.md",
           "route": "records"}
    assert "holds 'REJECTED'" in L.reread_receipt(m, "", ing)
    assert L.classify({**BASE_OBS, "receipt_terminal": "ACCEPTED",
                       "receipt_read_error": L.reread_receipt(m, "", ing)})[0] == "RECEIPT-NOT-SUCCESS"
    assert "no attempt or receipt_path" in L.reread_receipt(m, "", {**ing, "attempt": None})
    m2, rev2 = ledger_member(tmp_path / "two", receipt("ACCEPTED", extra="Terminal: UNKNOWN\n"))
    assert "terminal-shaped" in L.reread_receipt(m2, "", {**ing, "receipt_revisions": [rev2]})
    m3, rev3 = ledger_member(tmp_path / "three", receipt("ACCEPTED"))
    assert L.reread_receipt(m3, "", {**ing, "receipt_revisions": [rev3]}) is None                     # control


# --- the receipt grammar (R2-T18, design read 1 D-5) -------------------------------------------------------------

GOOD = "## Attempt X\n\nbody\n\nTerminal: ACCEPTED\n"


@pytest.mark.parametrize("text,want", [
    (GOOD, "ACCEPTED"),                                                                        # (a)
    ("## Attempt W\n\nTerminal: REJECTED\n\n## Attempt X\nTerminal: BEHAVIOUR_VERIFIED\n", "BEHAVIOUR_VERIFIED"),  # (g)
    ("**Terminal: REJECTED**\n\n" + GOOD, "ACCEPTED"),                                         # (l) history ignored
    ("## Attempt X (repair)\nTerminal: CANNOT-RUN\n", "CANNOT-RUN"),                          # valid, not a success
    ("## Attempt X\nTerminal: ACCEPTED\nTerminal: UNKNOWN\n", None),                          # (b)
    ("## Attempt X\nTerminal: UNKNOWN\n", None),                                              # (c)
    ("## Attempt X\nTerminal: accepted\n", None),                                             # (d)
    ("## Attempt X\nTerminal: ACCEPTED\nTerminal: ACCEPTED\n", None),                         # (e)
    ("## Attempt X\n**Terminal:** ACCEPTED\n", None),                                         # (f)
    (GOOD + "## Attempt Y\nTerminal: ACCEPTED\n", None),                                      # (h)
    (GOOD + GOOD, None),                                                                      # (i)
    ("## Attempt W\nTerminal: ACCEPTED\n", None),                                             # (j)
    ("## Attempt X\nTerminal: ACCEPTED\nmore text\n", None),                                  # (k)
    ("## Attempt X\nBEHAVIOUR_VERIFIED\nTerminal: REJECTED\n", None),                         # (m)
    ("# attempt X\nTerminal: ACCEPTED\n", None),                                              # (n)
    (b"## Attempt X\n\xff\nTerminal: ACCEPTED\n", None),                                      # not UTF-8
])
def test_r2_t18_receipt_terminal_grammar(text, want):
    """R2-T18: the parser's table. Valid parses return the value; every other case is unmet with a reason."""
    RBND = load("result_binding")
    value, why = RBND.receipt_terminal(text, "X")
    assert value == want and (why is None) == (want is not None), (value, why)


# --- the push gate (R2-T4, R2-T5, D-5) ---------------------------------------------------------------------------

def produce(path, step, doc):
    """Write `doc` at `path` as its producer now does (R2-T16 (c), R2-T17): a run recorded first, then the result bound
    to it. A record written by hand names no run and is not read."""
    RB = load("result_binding")
    rid = RB.start_run(step, path, aget=doc.get("aget"), recorded_by="invoker")
    RB.write_result(step, path, doc, rid, binding={"aget": doc.get("aget"), "subject": doc.get("head") or doc.get("sha")})


def gate_world(tmp_path, terminal="ACCEPTED"):
    """A member pushed at `base`, then a migration commit carrying the receiver's receipt; the B8a record; the
    receiver record of the packet."""
    remote, loc = tmp_path / "remote.git", tmp_path / "aget"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(loc)], check=True)
    (loc / "a.txt").write_text("old\n")
    git(loc, "add", "-A")
    git(loc, "commit", "-q", "-m", "base")
    git(loc, "remote", "add", "origin", str(remote))
    git(loc, "push", "-q", "origin", "main")
    base = git(loc, "rev-parse", "HEAD")
    (loc / "docs").mkdir()
    (loc / "docs" / "V335_RECEIVER_RECEIPT_a.md").write_text(receipt(terminal))
    (loc / "a.txt").write_text("new\n")
    git(loc, "add", "-A")
    git(loc, "commit", "-q", "-m", "migration")
    head = git(loc, "rev-parse", "HEAD")
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    produce(ev / "suite_at_commit.json", "suite_at_commit", {"sha": head, "verdict": "PASS", "aget": "a",
                                                            "tree_check": "enforced"})
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [], "attempt": ATTEMPT,
         "items": [{"path": "a.txt", "op": "write"}], "push_url": [str(remote)]}
    return r, ev, head


def launch_trace(ev, head, session="S-1", aget="a"):
    """What launch_batch.run_one does before the session (the invoker records the check's run) and what
    after_run_check then writes with --run-id/--session-id."""
    RBND = load("result_binding")
    out = ev / "after_run_check.json"
    run_id = RBND.start_run("after_run_check", out, aget=aget, recorded_by="invoker")
    (ev / "launch_record.json").write_text(json.dumps({"head_after": head, "session_id": session,
                                                       "check_run_id": run_id}))
    RBND.write_result("after_run_check", out, {"verdict": "PASS"}, run_id,
                      binding={"aget": aget, "session_id": session, "subject": head})
    return run_id


def rejudge_trace(ev, head, session="S-1", verdict="PASS", aget="a", finish=True):
    """What after_run_check does when run by hand with --session-id and no --run-id: it records its own run first."""
    RBND = load("result_binding")
    out = ev / "after_run_check.json"
    run_id, _ = RBND.producer_start("after_run_check", out, {"verdict": "INCONCLUSIVE"})
    if finish:
        RBND.write_result("after_run_check", out, {"verdict": verdict}, run_id,
                          binding={"aget": aget, "session_id": session, "subject": head})
    return run_id


def test_r2_t4_the_push_gate_refuses_a_verdict_from_another_session(tmp_path):
    """R2-T4 (S-159, S-166). A PASS verdict file from session X beside a launch record for session Y. At 34353311
    gate() reads only `verdict` and returns push facts."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head, session="X")
    (ev / "launch_record.json").write_text(json.dumps({"head_after": head, "session_id": "Y", "check_exit": 1}))
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "session" in why, why


@pytest.mark.parametrize("terminal", ["REJECTED", "CANNOT-RUN"])
def test_r2_t5_the_push_gate_refuses_a_non_success_receipt(tmp_path, terminal):
    """R2-T5 (S-160; wrapper r7 F-1 at B10). The receipt at HEAD ends `Terminal: REJECTED` in the packet's attempt
    section. At 34353311 the gate never reads the receipt: WOULD PUSH."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path, terminal)
    launch_trace(ev, head)
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and terminal in why, why


@pytest.mark.parametrize("case", ["b8a_recorded_only", "b8a_other_aget", "baseline_other_member",
                                  "baseline_other_head", "baseline_not_the_sealed_one", "snapshot_not_the_launchs"])
def test_r2_t10_the_push_gate_reads_only_evidence_bound_to_this_member_and_launch(tmp_path, monkeypatch, case):
    """R2-T10 (S-161, S-162, S-330). Each case meets every other gate condition, so the gate pushes on the stage
    before C2b; on C2b it refuses naming the record:
    - a B8a record whose tree check was only recorded (the packet rehearsal's reference run), or one for another Aget;
    - under the ruled B8a FAIL route (the ruling's typed-line check stubbed to hold; it is tested elsewhere), a baseline
      record for another member, for another pre-migration HEAD, or not the baseline the launch sealed;
    - a launch snapshot that is not the one the launch record names, listing a dirty path that would be allowed."""
    PB = load("push_batch")
    import batch_authority
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    sac = {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"}
    launch = json.loads((ev / "launch_record.json").read_text())
    if case == "b8a_recorded_only":
        sac["tree_check"] = "recorded only"
    elif case == "b8a_other_aget":
        sac["aget"] = "b"
    elif case.startswith("baseline"):
        fails = ["tests/t.py::x"]
        sac.update(verdict="FAIL", failures=fails)
        base = {"aget": "a", "head": r["head"], "verdict": "RECORDED", "failures": fails, "sha256": "s" * 64}
        launch["baseline_sha256"] = "s" * 64
        if case == "baseline_other_member":
            base["aget"] = "b"
        elif case == "baseline_other_head":
            base["head"] = head
        else:
            launch["baseline_sha256"] = "t" * 64
        produce(ev / "baseline_record.json", "baseline", base)
        (ev / "baseline_equal_ruling.json").write_text(json.dumps({"sha": head, "line": "GO x", "session": "S-1"}))
        monkeypatch.setattr(batch_authority, "verify_ruling", lambda ruling, h, d=None: (True, "stubbed"))
    else:
        (Path(r["location"]) / "late.txt").write_text("written after the launch\n")
        (ev / "settings_snapshot_pre.json").write_text(json.dumps({"dirty": {}}))
        launch["snapshot_sha256"] = hashlib.sha256((ev / "settings_snapshot_pre.json").read_bytes()).hexdigest()
        (ev / "settings_snapshot_pre.json").write_text(json.dumps({"dirty": {"late.txt": "x"}}))   # replaced later
    (ev / "launch_record.json").write_text(json.dumps(launch))
    produce(ev / "suite_at_commit.json", "suite_at_commit", sac)
    ok, why = PB.gate(r, tmp_path / "ev", [])
    expect = {"b8a_recorded_only": "tree check", "b8a_other_aget": "B8a record is for",
              "baseline_other_member": "baseline record is for", "baseline_other_head": "pre-migration HEAD",
              "baseline_not_the_sealed_one": "the launch sealed", "snapshot_not_the_launchs": "launch snapshot"}[case]
    assert ok is None and expect in why, (ok, why)


def test_r2_t10_positive_control_bound_evidence_still_pushes(tmp_path, monkeypatch):
    """R2-T10 positive control: the launch's own snapshot with its digest allows its dirty path; a bound baseline under
    the ruled FAIL route passes."""
    PB = load("push_batch")
    import batch_authority
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    launch = json.loads((ev / "launch_record.json").read_text())
    (Path(r["location"]) / "early.txt").write_text("dirty at launch\n")
    (ev / "settings_snapshot_pre.json").write_text(json.dumps({"dirty": {"early.txt": "x"}}))
    launch["snapshot_sha256"] = hashlib.sha256((ev / "settings_snapshot_pre.json").read_bytes()).hexdigest()
    fails = ["tests/t.py::x"]
    launch["baseline_sha256"] = "s" * 64
    produce(ev / "baseline_record.json", "baseline", ({"aget": "a", "head": r["head"], "verdict": "RECORDED",
                                                         "failures": fails, "sha256": "s" * 64}))
    (ev / "baseline_equal_ruling.json").write_text(json.dumps({"sha": head, "line": "GO x", "session": "S-1"}))
    monkeypatch.setattr(batch_authority, "verify_ruling", lambda ruling, h, d=None: (True, "stubbed"))
    (ev / "launch_record.json").write_text(json.dumps(launch))
    # B179 finding 3 (changed at the C2b port onto E2i14, labelled): the B8a list's ids are all read whole;
    # C2c (R2-T16 (c)): the record is the current run of B8a
    produce(ev / "suite_at_commit.json", "suite_at_commit", {"sha": head, "verdict": "FAIL", "failures": fails,
                                                            "failures_complete": True, "aget": "a",
                                                            "tree_check": "enforced"})
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok and ok["head"] == head, why


def test_d5_one_run_identity_contract(tmp_path):
    """Design read 2, D-5: one identity contract at every consumer of an after-run verdict. Current run for the
    verdict file, this member, the launch record's session. Traces: (1) an ordinary launch passes; (2) a hand
    re-judge of the same session, with its own run id, passes and supersedes the launch's check; (3) a re-judge
    naming another session is refused; (4) after a later run started and did not finish, the earlier PASS is
    refused; (5) a verdict for another member is refused. At 34353311 the gate reads only `verdict`, so (3) to (5)
    pass through."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head, session="S-1")
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok and not why                                                             # (1)
    rejudge_trace(ev, head, session="S-1")
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok and not why                                                             # (2)
    rejudge_trace(ev, head, session="S-2")
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "session" in why                                            # (3)
    rejudge_trace(ev, head, session="S-1")
    rejudge_trace(ev, head, session="S-1", finish=False)
    (ev / "after_run_check.json").write_text(json.dumps({"verdict": "PASS",
                                                         "binding": {"aget": "a", "session_id": "S-1"}}))
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "not the current run" in why                                # (4)
    rejudge_trace(ev, head, session="S-1", aget="b")
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "member" in why                                             # (5)


# --- the rehearsal results and the B4 approval (R2-T8, R2-T16, D-2) ---------------------------------------------

def produced(RBND, step, out, doc):
    run_id = RBND.start_run(step, out)
    RBND.write_result(step, out, doc, run_id)


@pytest.mark.parametrize("tool,step,args", [
    ("rehearse_batch2", "rehearse_batch2", ["--packet", "p", "--list", "l", "--scratch", "s", "--bogus"]),
    ("rehearse_repair", "rehearse_repair", ["--packet", "p", "--previous-packet", "q", "--scratch", "s", "--bogus"]),
    ("rehearse_v37", "rehearse_v37", ["--batch", "9", "--scratch", "s", "--bogus", "m-aget"])])
def test_r2_t8_a_usage_error_invalidates_the_earlier_result(tmp_path, tool, step, args):
    """R2-T8 (S-194), closing design read 2 D-2 for the case the kit can see. --out X holds an earlier PASS; a run
    with the same --out and a bad argument must leave X unmet. At 34353311 NOT_FINISHED is written only after
    argparse, so X still reads PASS."""
    T, RBND = load(tool), load("result_binding")
    out = tmp_path / "RESULT.json"
    produced(RBND, step, out, {"verdict": "PASS", "results": [{"aget": "a", "verdict": "PASS"}]})
    assert RBND.read_current(step, out)[1] is None
    with pytest.raises(SystemExit):
        T.main(args + ["--out", str(out)])
    doc = json.loads(out.read_text())
    assert doc.get("verdict") != "PASS" or RBND.read_current(step, out)[1]


def test_r2_t16b_a_pass_copied_from_another_folder_is_refused(tmp_path):
    """R2-T16 (b) (S-183, S-184), design read 1 D-4: a V3.7 PASS copied from another folder, naming the same list
    digest, is not the current run there. At 34353311 the approval step binds the list digest only and accepts it."""
    CA, RBND = load("check_list_approvable"), load("result_binding")
    lst = tmp_path / "LIST.json"
    lst.write_text(json.dumps({"agets": [{"aget": "a"}]}))
    sha = hashlib.sha256(lst.read_bytes()).hexdigest()
    v36, v37 = tmp_path / "V36.json", tmp_path / "V37.json"
    produced(RBND, "rehearse_batch2", v36, {"list_sha256": sha,
                                            "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}]})
    other = tmp_path / "other"
    other.mkdir()
    produced(RBND, "rehearse_v37", other / "V37.json", {"verdict": "PASS", "list_sha256": sha,
                                                         "members": {"a": {"verdict": "PASS"}}})
    v37.write_bytes((other / "V37.json").read_bytes())                    # copied, byte for byte
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 1
    produced(RBND, "rehearse_v37", v37, json.loads(v37.read_text()))     # control: produced here
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 0


def test_r2_t9_the_v37_digest_is_the_recorded_field_only(tmp_path):
    """R2-T9 (S-184 hex fallback). A V3.7 result naming the list only inside free text is not bound. At 34353311
    check_list_approvable.py:95 accepts the first 64-hex run in `list`."""
    CA = load("check_list_approvable")
    sha = "a" * 64
    assert CA.v37_digest({"list": f"WRITE_LIST sha256 {sha} (location rewritten)"}) is None
    assert CA.v37_digest({"list_sha256": sha}) == sha


def test_r2_run_log_contract_unit(tmp_path):
    """The run log itself (R2 clause 1): current only when last started, finished, and the bytes match; a line that
    does not parse makes every key unmet; a key is per output path."""
    RBND = load("result_binding")
    out = tmp_path / "r.json"
    a = RBND.start_run("s", out)
    data = RBND.write_result("s", out, {"v": 1}, a)
    assert RBND.current("s", out, a, data) is None
    assert RBND.current("s", out, a, data + b" ")                                 # other bytes
    b = RBND.start_run("s", out)
    assert RBND.current("s", out, a, data)                                        # superseded by b
    assert RBND.current("s", out, b, data)                                        # b did not finish
    RBND.write_result("s", tmp_path / "other.json", {"v": 2}, RBND.start_run("s", tmp_path / "other.json"))
    assert RBND.current("s", out, b, data)                                        # another key does not help
    with RBND.log_of(out).open("a") as fh:
        fh.write("{not json\n")
    assert "does not parse" in RBND.current("s", out, b, data)


# --- BILD6's finding at E2c (same class as B148 finding 3 and B151 finding 6) ------------------------------------

@pytest.mark.parametrize("bad", ["branch_missing", "aget_int", "items_not_list"])
def test_push_batch_checks_every_receiver_before_the_first_push(tmp_path, monkeypatch, bad):
    """The push loop pushes receiver by receiver. A malformed later receiver must stop the run before ANY push (exit
    2), not end in a traceback after an earlier receiver was pushed. On stage E2c the first receiver's push session
    ran (here a stand-in that writes a marker) and the second raised KeyError/TypeError. Nothing leaves tmp_path."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    second = {**r, "aget": "b"}
    if bad == "branch_missing":
        second.pop("branch")
    elif bad == "aget_int":
        second["aget"] = 7
    else:
        second["items"] = "a.txt"
    r["settings"] = second["settings"] = {"path": str(tmp_path / "settings.json"), "sha256": "0" * 64}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r, second]}))
    rc = tmp_path / "receipt.json"
    produce(rc, "apply_protected", {"agets": [{"aget": "a", "files": []}, {"aget": "b", "files": []}]})   # R2-T17: written by its run
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"),   # R2-T12
                        raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    try:
        got = PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    except Exception as e:   # noqa: BLE001
        got = e
    assert got == 2 and not marker.exists(), (got, marker.read_text() if marker.exists() else None)


def test_push_batch_still_pushes_a_wellformed_packet(tmp_path, monkeypatch):
    """Control for the test above: the same world with a well-formed packet reaches the push (the stand-in runs)."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    r["settings"] = {"path": str(tmp_path / "settings.json"), "sha256": "0" * 64}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r]}))
    rc = tmp_path / "receipt.json"
    produce(rc, "apply_protected", {"mode": "apply", "batch": "99", "agets": [{"aget": "a", "result": "APPLIED", "files": [],
                                                                              "location": r["location"]}]})   # R2-T17: written by its run; C2d (labelled): batch and location
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"),   # R2-T12
                        raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    assert marker.read_text() == "push\n"


# --- REVW5's B152 read of stage E2d ------------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [42, [{"path": []}]], ids=["files_int", "path_list"])
def test_b152_3_push_receipt_shapes_are_checked_before_any_push(tmp_path, monkeypatch, bad):
    """B152 finding 3 (REVW5's falsifier). The apply receipt's later rows are checked before the first push: exit 2,
    no push. On stage E2d a second row with `files: 42` raised TypeError after the first receiver's push stand-in ran,
    and `files: [{"path": []}]` followed that push before the later gate refused."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    second = {**r, "aget": "b"}
    r["settings"] = second["settings"] = {"path": str(tmp_path / "s.json")}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r, second]}))
    rc = tmp_path / "receipt.json"
    produce(rc, "apply_protected", {"agets": [{"aget": "a", "files": []}, {"aget": "b", "files": bad}]})   # R2-T17: written by its run
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"),   # R2-T12
                        raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    try:
        got = PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    except Exception as e:   # noqa: BLE001
        got = e
    assert got == 2 and not marker.exists(), (got, marker.read_text() if marker.exists() else None)


# --- C2a: R2-T6, the apply receipt's entry must be bound ---------------------------------------------------------

GOOD_RECEIPT = {"mode": "apply", "batch": "1", "list_sha256": "l" * 64,   # C2d (labelled): the batch prepare_launch builds
                "agets": [{"aget": "a", "result": "APPLIED", "files": [{"path": "x.md", "post": "p" * 64, "ok": True}]}]}
UNBOUND = {
    "no_result": lambda d: d["agets"][0].pop("result"),
    "dry_run": lambda d: d.update(mode="dry-run"),
    "no_mode": lambda d: d.pop("mode"),
    "file_not_ok": lambda d: d["agets"][0]["files"][0].update(ok=False),
    "two_entries": lambda d: d["agets"].append(dict(d["agets"][0])),
}


def _receipt(case):
    d = json.loads(json.dumps(GOOD_RECEIPT))
    if case:
        UNBOUND[case](d)
    return d


@pytest.mark.parametrize("case", sorted(UNBOUND))
def test_r2_t6_an_unbound_apply_entry_is_refused(case):
    """R2-T6 (S-164, S-171, S-187, S-321, S-329), the unit: an entry with no result, a trial-run receipt (or one with
    no mode), a file the apply did not write, and a duplicate entry are each refused with a reason; a receipt naming
    another list is refused when the caller knows the list's digest. Before C2a no such validator existed."""
    RBND = load("result_binding")
    entry, why = RBND.apply_entry(_receipt(case), "a")
    assert entry is None and why, (case, why)
    assert RBND.apply_entry(_receipt(None), "a", list_sha256="m" * 64)[1]
    assert RBND.apply_entry(_receipt(None), "a", list_sha256="l" * 64) == (GOOD_RECEIPT["agets"][0], None)


@pytest.mark.parametrize("case", ["no_result", "dry_run", "file_not_ok"])
def test_r2_t6_the_push_gate_takes_no_files_from_an_unbound_entry(tmp_path, monkeypatch, case, capsys):
    """R2-T6 at the push gate: with an unbound apply entry for the receiver, nothing is pushed and the reason is
    printed. Before C2a the files were taken from the entry and the push went ahead."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    r["settings"] = {"path": str(tmp_path / "settings.json"), "sha256": "0" * 64}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r]}))
    rc = tmp_path / "receipt.json"
    d = {"mode": "apply", "batch": "99", "agets": [{"aget": "a", "result": "APPLIED", "files": [],
                                                    "location": r["location"]}]}   # C2d (labelled): batch and location
    {"no_result": lambda: d["agets"][0].pop("result"), "dry_run": lambda: d.update(mode="dry-run"),
     "file_not_ok": lambda: d["agets"][0].update(files=[{"path": "x.md", "post": "p" * 64, "ok": False}])}[case]()
    produce(rc, "apply_protected", d)   # R2-T17: written by its run
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"),   # R2-T12
                        raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    assert not marker.exists() and "NOT PUSHED" in capsys.readouterr().out


@pytest.mark.parametrize("case", ["dry_run", "no_mode"])
def test_r2_t6_prepare_launch_refuses_an_unbound_receipt_before_anything_is_made(tmp_path, monkeypatch, capsys, case):
    """R2-T6 at launch preparation: `--receipt` from a trial run, or with no mode, stops at argument checking (exit
    2, naming the mode) before any packet folder is made. Before C2a the receipt was read after staging and its
    files were taken whatever its mode."""
    PL = load("prepare_launch")
    monkeypatch.setenv("AGET_MIGRATION_FROM", "3.35.0")
    monkeypatch.setenv("AGET_MIGRATION_TO", "3.36.0")
    rc = tmp_path / "receipt.json"
    produce(rc, "apply_protected", _receipt(case))   # R2-T17: written by its run
    out = tmp_path / "pk" / "packet.json"
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--out", str(out), "--receipt", str(rc), "a"])
    with pytest.raises(SystemExit) as e:
        PL.main()
    assert e.value.code == 2 and "not 'apply'" in capsys.readouterr().err
    assert not (tmp_path / "pk").exists()


# --- REVW9's B179 read of stage C2a: every requested member needs its own bound entry ------------------------------

@pytest.mark.parametrize("receipt_agets", ["empty", "unrelated"])
def test_b179_2_prepare_launch_refuses_a_member_the_receipt_does_not_name(tmp_path, monkeypatch, capsys, receipt_agets):
    """B179 finding 2 (REVW9's falsifier). The receipt is an applying run's, but it holds no entry for the requested
    member (no entries at all, or only another member's bound entry). Preparation stops at argument checking (exit 2,
    naming the member) before any packet folder is made. On stage C2a only listed members were checked, so an absent
    member got a packet with no applied files."""
    PL = load("prepare_launch")
    monkeypatch.setenv("AGET_MIGRATION_FROM", "3.35.0")
    monkeypatch.setenv("AGET_MIGRATION_TO", "3.36.0")
    d = json.loads(json.dumps(GOOD_RECEIPT))
    d["agets"] = [] if receipt_agets == "empty" else d["agets"]           # GOOD_RECEIPT's entry is for "a"
    rc = tmp_path / "receipt.json"
    # changed at C2d (R2-T17, labelled): the receipt is written as the apply run writes it, bound to its run
    rid = PL.RBND.start_run("apply_protected", rc)
    PL.RBND.write_result("apply_protected", rc, d, rid)
    out = tmp_path / "pk" / "packet.json"
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--out", str(out), "--receipt", str(rc), "b"])
    with pytest.raises(SystemExit) as e:
        PL.main()
    assert e.value.code == 2 and "b: the apply receipt has no entry for this Aget" in capsys.readouterr().err
    assert not (tmp_path / "pk").exists()


# --- REVW9's B180 read of stage C2a2: only pytest's own short summary is read, each id with a unique end ----------

def _pytest_output(tmp_path, body):
    """Actual pytest output (-q -rfE, as the baseline command runs it) for a synthetic test file."""
    (tmp_path / "test_s.py").write_text(body)
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider", "test_s.py"],
                       cwd=tmp_path, capture_output=True, text=True)
    return p.stdout + p.stderr


def test_b180_1_a_balanced_shorter_prefix_is_not_an_id(tmp_path):
    """B180 finding 1 (REVW9's balanced-prefix falsifier). A parameter `same] - alpha[tail` gives the id
    `test_p[same] - alpha[tail]`, whose shorter prefix `test_p[same]` also has balanced brackets and is followed by
    ` - `. The end is not unique, so the ids are not all known. On stage C2a2 the shorter prefix was read as the id."""
    RB = load("result_binding")
    out = _pytest_output(tmp_path, 'import pytest\n@pytest.mark.parametrize("v", ["same] - alpha[tail"])\n'
                                   'def test_p(v):\n    assert v == "x"\n')
    ids, why = RB.failing_ids(out)
    assert why and "end is not unique" in why, (ids, why, out[-400:])
    assert "test_s.py::test_p[same]" not in ids


def test_b180_1_a_failed_line_a_test_prints_is_not_read(tmp_path):
    """B180 finding 1 (REVW9's captured-line falsifier). A failing test prints `FAILED …[new] - …` into its captured
    output; pytest's summary lists only the real failure, and only that id is read. On stage C2a2 the printed id was
    read too, as a baseline failure."""
    RB = load("result_binding")
    out = _pytest_output(tmp_path, 'import pytest\n@pytest.mark.parametrize("v", ["baseline", "new"])\n'
                                   'def test_p(v):\n    print("FAILED test_s.py::test_p[new] - printed")\n'
                                   '    assert v == "new"\n')
    assert "FAILED test_s.py::test_p[new] - printed" in out          # the printed line is in the output
    assert RB.failing_ids(out) == (["test_s.py::test_p[baseline]"], None), out[-600:]


@pytest.mark.parametrize("lines,counts", [
    ("FAILED t.py::a\nFAILED t.py::b", "1 failed, 1 error"),        # a FAILED line standing in for an ERROR id
    ("FAILED t.py::a", "2 failed"),                                  # a failure with no line (advisory A)
    ("FAILED t.py::a\nERROR t.py::b\nERROR t.py::c", "1 failed, 1 error")])
def test_b180_1_failed_and_error_lines_account_for_their_own_counts(lines, counts):
    """B180 finding 1 (advisory (a), REVW9's pooled-count falsifier). FAILED lines must equal the failed count and
    ERROR lines the error count, each separately. On stage C2a2 the two were pooled (and F checked no count)."""
    RB = load("result_binding")
    ids, why = RB.failing_ids(f"=== short test summary info ===\n{lines}\n{counts}, 3 passed in 0.1s")
    assert why and "line(s) for" in why, (ids, why)


def test_b180_1_failures_with_no_summary_section_are_not_known():
    """B180 finding 1: failures reported with no `short test summary info` section cannot be told from printed lines,
    so the ids are not all known; with no failure reported, no line is read at all."""
    RB = load("result_binding")
    assert RB.failing_ids("FAILED t.py::a\n1 failed, 3 passed in 0.1s")[1]
    assert RB.failing_ids("FAILED t.py::a - printed\n3 passed in 0.1s") == ([], None)


def test_b180_1_ordinary_ids_with_spaces_and_dashes_are_read_whole(tmp_path):
    """B180 finding 1, control (REVW9's ordinary case): `alpha - tail` in a parameter, a plain test and a setup error
    are each read whole, and the counts account for them."""
    RB = load("result_binding")
    out = _pytest_output(tmp_path, 'import pytest\n@pytest.fixture\ndef boom():\n    raise RuntimeError("x")\n'
                                   '@pytest.mark.parametrize("v", ["alpha tail"])\ndef test_p(v):\n    assert 0\n'
                                   'def test_q():\n    assert 0\ndef test_e(boom):\n    pass\n')
    # changed at C2a5 (B182 finding 1, labelled): the parameter is `alpha tail`; one holding ` - ` now reads not all
    # known (its end is not unique from text), an admission cost
    assert RB.failing_ids(out) == (["test_s.py::test_e", "test_s.py::test_p[alpha tail]", "test_s.py::test_q"],
                                   None), out[-600:]


def test_b180_1_every_failing_id_reader_is_the_one_reader():
    """B180 finding 1, by population (census): no kit module reads `FAILED`/`ERROR` lines with its own pattern; the
    baseline producer, F, the confirmation run, B8a and the repair rehearsal call result_binding.failing_ids, and the
    parallel runner passes on only each file's own summary lines (run_suite_parallel.summary_lines). On stage C2a2
    rehearse_repair read ids with `\\S+` and the runner took every line starting `FAILED `."""
    import re
    pattern = re.compile(r"\(\?:FAILED\|ERROR\)|\(FAILED\|ERROR\)|startswith\(\(\"FAILED")
    owners = {"result_binding.py", "run_suite_parallel.py"}
    hits = {p.name for p in BATCH.glob("*.py") if p.name not in owners and pattern.search(p.read_text())}
    assert hits == set(), hits
    # changed at C2a7 (B185 finding 1, labelled): the five consumers read the kit's report (report_failures; census in
    # test_migration_kit_result_source.py); the display reader stays the runner's, for its own summary lines
    users = {p.name for p in BATCH.glob("*.py") if "RBND.report_failures(" in p.read_text()}
    assert {"launch_batch.py", "after_run_check.py", "suite_at_commit.py", "rehearse_repair.py"} <= users, users
    runner = (BATCH / "run_suite_parallel.py").read_text()
    # changed at C2a5 (B182 finding 1, labelled): the runner applies the one reader to each file's output
    assert "RBND.summary_section(out)" in runner and "RBND.failing_ids(out)" in runner
    assert 'startswith(("FAILED ", "ERROR "))' not in runner


# --- REVW9's B182 read of stage C2a3: one summary and one count line; an id end unique from the line ---------------

ATEXIT = ('import atexit, pytest\n'
          'atexit.register(lambda: print("=== short test summary info ===\\n1 passed in 0.01s"))\n'
          '@pytest.mark.parametrize("v", ["before", "ok"])\ndef test_p(v):\n    assert v == "ok"\n')


def test_b182_1_a_summary_printed_after_pytests_own_reads_not_all_known(tmp_path):
    """B182 finding 1 (REVW9's falsifier, direct form). An `atexit` callback prints a summary-shaped block after
    pytest's own summary; the output then holds two summaries and two count lines, so the ids are not all known. On
    stage C2a3 the last section was read: no ids, no reason, and the real failure was dropped."""
    RB = load("result_binding")
    out = _pytest_output(tmp_path, ATEXIT)
    assert "FAILED test_s.py::test_p[before]" in out and out.rstrip().endswith("1 passed in 0.01s"), out[-300:]
    ids, why = RB.failing_ids(out)
    assert why and "count lines" in why, (ids, why)


def test_b182_1_the_parallel_runner_marks_a_file_it_cannot_read(tmp_path):
    """B182 finding 1 (REVW9's falsifier, parallel form). The same test file under the kit's runner: the file's output
    cannot be read, so the runner prints an IDS-UNKNOWN line (never an id) and the kit's reader reads the run as not
    all known. On stage C2a3 the runner took the trailing block and its synthetic error line was recorded as an id."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(ATEXIT)
    p = subprocess.run([sys.executable, str(BATCH / "run_suite_parallel.py")], cwd=tmp_path, capture_output=True,
                       text=True)
    RB = load("result_binding")
    assert "IDS-UNKNOWN tests/test_a.py" in p.stdout, p.stdout
    ids, why = RB.failing_ids(p.stdout)
    assert ids == [] and why, (ids, why, p.stdout)


def test_b182_1_a_plain_name_holding_a_dash_separator_is_not_cut(tmp_path):
    """B182 finding 1 (REVW9's whole-id falsifier). A test exposed as `globals()['test_synthetic - alpha']` fails with
    a message; the line holds two ` - `, so its end is not unique and the ids are not all known. On stage C2a3 the
    first word was read as the id, shared with a later `… - beta`."""
    RB = load("result_binding")
    out = _pytest_output(tmp_path, 'def _t():\n    assert 0\nglobals()["test_synthetic - alpha"] = _t\n'
                                   'def test_ok():\n    pass\n')
    assert "test_s.py::test_synthetic - alpha" in out, out[-400:]
    ids, why = RB.failing_ids(out)
    assert why and "end is not unique" in why, (ids, why)


@pytest.mark.parametrize("text", [
    "=== short test summary info ===\nFAILED t.py::test_p[same] - new] - E\n1 failed in 0.1s",       # advisory (1)
    "FAILED t.py::a - printed\n1 passed in 0.1s\n1 failed, 1 passed in 0.2s",                         # advisory (2)
    "=== short test summary info ===\nERROR  - RuntimeError: session\n1 error in 0.1s",               # advisory (11)
    "=== short test summary info ===\nFAILED t.py::a - x\n=== short test summary info ===\n1 failed in 0.1s"])
def test_b182_1_an_unreadable_summary_is_a_reason(text):
    """B182 finding 1 with FWK-OVSR5's C2a3 advisory: an unbalanced `] - ` in a parameter, a captured count line with
    the summary off, an empty session-level id, and two summary headers each read not all known."""
    RB = load("result_binding")
    ids, why = RB.failing_ids(text)
    assert why, (ids, why)


def test_b182_1_the_parallel_runner_keeps_lines_whose_message_looks_like_a_count(tmp_path):
    """FWK-OVSR5's C2a3 advisory (9): a failure message `expected 0 passed in 1.0s` is not a count line, so both
    FAILED lines are kept and read."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        'def test_one():\n    assert 0, "expected 0 passed in 1.0s"\n'
        'def test_two():\n    assert 0, "expected 0 passed in 1.0s"\n')
    p = subprocess.run([sys.executable, str(BATCH / "run_suite_parallel.py")], cwd=tmp_path, capture_output=True,
                       text=True)
    RB = load("result_binding")
    assert RB.failing_ids(p.stdout) == (["tests/test_a.py::test_one", "tests/test_a.py::test_two"], None), p.stdout


# --- C2c: the B8a record and the baseline are bound to their current runs (R2-T16 (c), R2-T17; D-4) -------------

def _sac_main(tmp_path, monkeypatch, r, ev_root, raise_it):
    """suite_at_commit.main for member `a` at its HEAD, with the suite run stubbed: PASS, or raising after start."""
    SAC = load("suite_at_commit")
    pk = tmp_path / "sac_packet.json"
    pk.write_text(json.dumps({"receivers": [{**r, "suite_cmd": "true"}]}))

    def run(location, aget, sha, *a, **k):
        if raise_it:
            raise RuntimeError("the suite run failed before producing a result")
        return {"schema": "v335_suite_at_commit/1", "aget": aget, "sha": sha, "verdict": "PASS",
                "tree_check": "enforced", "hook": "ran", "tree_allowed": [], "summary": "1 passed"}
    monkeypatch.setattr(SAC, "run", run)
    try:
        return SAC.main(["--packet", str(pk), "--aget", "a", "--evidence", str(ev_root)])
    except RuntimeError:
        return "raised"


def test_r2_t16c_a_later_b8a_run_that_fails_leaves_no_earlier_pass_standing(tmp_path, monkeypatch):
    """R2-T16 (c) (D-4, S-161). suite_at_commit writes a PASS for the commit; a re-run for the same commit raises
    before producing a result. The push gate refuses: the earlier PASS is not the current run. Before C2c the record
    was written only at the end, so the earlier PASS stood and the gate pushed."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    (ev / "suite_at_commit.json").unlink()
    assert _sac_main(tmp_path, monkeypatch, r, tmp_path / "ev", False) == 0
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok, why                                                          # control: the current PASS pushes
    assert _sac_main(tmp_path, monkeypatch, r, tmp_path / "ev", True) == "raised"
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "B8a" in why, (ok, why)


def test_r2_t16c_a_b8a_pass_copied_from_another_folder_is_refused(tmp_path, monkeypatch):
    """R2-T16 (c) (D-4). A PASS B8a record for the same member and commit, copied from another evidence folder, is
    refused: its run is not recorded beside it. Before C2b the gate read the file's fields only."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    (ev / "suite_at_commit.json").unlink()
    other = tmp_path / "other_ev"
    assert _sac_main(tmp_path, monkeypatch, r, other, False) == 0
    (ev / "suite_at_commit.json").write_bytes((other / "a" / "suite_at_commit.json").read_bytes())
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "B8a" in why, (ok, why)


def test_r2_t17_a_baseline_copied_from_another_folder_is_not_read_by_the_ruled_route(tmp_path, monkeypatch):
    """R2-T17 (S-162). Under the ruled B8a FAIL route, a baseline record for this member and pre-migration HEAD, with
    the sealed slot's digest, but copied from another folder (no run recorded beside it), is refused. Control: the
    same record written by its run passes. Before C2c the gate read the record as a plain file."""
    PB = load("push_batch")
    import batch_authority
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    launch = json.loads((ev / "launch_record.json").read_text())
    launch["baseline_sha256"] = "s" * 64
    (ev / "launch_record.json").write_text(json.dumps(launch))
    fails = ["tests/t.py::x"]
    # B179 finding 3 (changed at the C2c port onto C2a10, labelled): the B8a list's ids are all read whole
    produce(ev / "suite_at_commit.json", "suite_at_commit", {"sha": head, "verdict": "FAIL", "failures": fails,
                                                            "failures_complete": True, "aget": "a",
                                                            "tree_check": "enforced"})
    (ev / "baseline_equal_ruling.json").write_text(json.dumps({"sha": head, "line": "GO x", "session": "S-1"}))
    monkeypatch.setattr(batch_authority, "verify_ruling", lambda ruling, h, d=None: (True, "stubbed"))
    base = {"aget": "a", "head": r["head"], "verdict": "RECORDED", "failures": fails, "sha256": "s" * 64}
    other = tmp_path / "other"
    other.mkdir()
    produce(other / "baseline_record.json", "baseline", base)
    (ev / "baseline_record.json").write_bytes((other / "baseline_record.json").read_bytes())
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "baseline" in why, (ok, why)
    produce(ev / "baseline_record.json", "baseline", base)
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok and ok["head"] == head, why


# --- C2d: the apply receipt is bound to its current run (R2-T17; D-4) --------------------------------------------

@pytest.mark.parametrize("case", ["never_finished", "copied", "current"])
def test_r2_t17_the_push_gate_reads_only_a_finished_current_apply_receipt(tmp_path, monkeypatch, case, capsys):
    """R2-T17 (S-164). The receipt's entry for the receiver is bound (APPLIED, files ok), but the receipt is from an
    apply run that never finished (a killed run's IN-PROGRESS write: no FINISHED row), or a copy of a finished
    receipt from another folder. Nothing is pushed. Control: the current run's receipt pushes. Before C2d the push
    gate read the receipt as a plain file and pushed in all three cases."""
    PB = load("push_batch")
    RB = load("result_binding")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    r["settings"] = {"path": str(tmp_path / "settings.json"), "sha256": "0" * 64}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r]}))
    rc = tmp_path / "receipt.json"
    d = {"mode": "apply", "batch": "99", "list_sha256": "l" * 64,
         "agets": [{"aget": "a", "result": "APPLIED", "files": [], "location": r["location"]}]}   # C2d (labelled)
    if case == "never_finished":
        RB.start_run("apply_protected", rc)
        RB.atomic_write(rc, (json.dumps(d) + "\n").encode())
    elif case == "copied":
        (tmp_path / "other").mkdir()
        produce(tmp_path / "other" / "receipt.json", "apply_protected", d)
        rc.write_bytes((tmp_path / "other" / "receipt.json").read_bytes())
    else:
        produce(rc, "apply_protected", d)
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"), raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    out = capsys.readouterr().out
    if case == "current":
        assert marker.exists(), out
    else:
        assert not marker.exists() and "not the current run" in out, out


# --- FWK-OVSR8's C2d pre-read (reproduced on a real filesystem, 19:20) -------------------------------------------

@pytest.mark.parametrize("case", ["other_batch", "other_location", "no_location"])
def test_c2d_preread_1_an_apply_receipt_of_another_batch_or_member_location_is_not_pushed(tmp_path, monkeypatch, case):
    """FWK-OVSR8's C2d pre-read 1 (HIGH candidate, reproduced): an apply receipt from another batch, or applied at
    another member location, was accepted by the push gate (and by prepare_launch and after-run A), while the release
    note says each is "checked for this member and this launch". The receipt now binds its batch and each entry its
    location. Control: test_push_batch_still_pushes_a_wellformed_packet (the same world, matching both)."""
    PB = load("push_batch")
    r, ev, head = gate_world(tmp_path)
    launch_trace(ev, head)
    r["settings"] = {"path": str(tmp_path / "settings.json"), "sha256": "0" * 64}
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "x", "receivers": [r]}))
    entry = {"aget": "a", "result": "APPLIED", "files": [], "location": r["location"]}
    d = {"mode": "apply", "batch": "99", "agets": [entry]}
    if case == "other_batch":
        d["batch"] = "98"
    elif case == "other_location":
        (tmp_path / "elsewhere").mkdir()
        entry["location"] = str(tmp_path / "elsewhere")
    else:
        entry.pop("location")
    rc = tmp_path / "receipt.json"
    produce(rc, "apply_protected", d)
    import batch_authority
    monkeypatch.setattr(batch_authority, "check", lambda batch, act=None: (True, "stub"))
    monkeypatch.setattr(batch_authority, "push_authority", lambda batch, *a, **k: (True, "stub"), raising=False)
    marker = tmp_path / "pushed.txt"
    monkeypatch.setattr(PB, "push_command", lambda *a: [sys.executable, "-c",
                                                         f"open({str(marker)!r}, 'a').write('push\\n')"])
    PB.main(["--packet", str(pk), "--push", "--evidence", str(tmp_path / "ev"), "--apply-receipt", str(rc)])
    assert not marker.exists(), case


def test_c2d_preread_3_a_superseded_run_never_replaces_the_newer_runs_result(tmp_path):
    """FWK-OVSR8's C2d pre-read 3 (MEDIUM, reproduced): start A, start B, B writes its result, then A's write
    replaced it (evidence loss). Only the latest started run writes. Control: B's result stays current."""
    RB = load("result_binding")
    out = tmp_path / "ev" / "receipt.json"
    a = RB.start_run("apply_protected", out)
    b = RB.start_run("apply_protected", out)
    RB.write_result("apply_protected", out, {"mode": "apply", "who": "B"}, b)
    try:
        RB.write_result("apply_protected", out, {"mode": "apply", "who": "A"}, a)
    except RB.RunLogError:
        pass
    doc, why = RB.read_current("apply_protected", out)
    assert why is None and doc["who"] == "B", (doc, why)


@pytest.mark.parametrize("bad", ["list", "str", "int", "log"])
def test_c2d_preread_4_a_malformed_binding_or_run_log_is_unavailable_not_a_crash(tmp_path, bad):
    """FWK-OVSR8's C2d pre-read 4 (MEDIUM, reproduced): a binding that is a list or a string, a run id that is an
    integer, or a run log that is not UTF-8 raised AttributeError, TypeError or UnicodeDecodeError out of every reader.
    Each reads unavailable with a reason."""
    RB = load("result_binding")
    out = tmp_path / "ev" / "receipt.json"
    rid = RB.start_run("apply_protected", out)
    RB.write_result("apply_protected", out, {"mode": "apply"}, rid)
    doc = json.loads(out.read_text())
    if bad == "log":
        RB.log_of(out).write_bytes(b"\xff\n")
    else:
        doc["binding"] = {"list": ["x"], "str": "x", "int": {"run_id": 123}}[bad]
        out.write_text(json.dumps(doc))
    got, why = RB.read_current("apply_protected", out)
    assert got is None and why, (got, why)


def test_c2d_preread_5_receipt_with_protected_list_is_refused_not_named_unread(tmp_path, monkeypatch, capsys):
    """FWK-OVSR8's C2d pre-read 5 (MEDIUM, read in the code): with both --receipt and --protected-list, preparation
    skipped reading the receipt, yet the packet named it. The combination is refused before anything is made."""
    PL = load("prepare_launch")
    monkeypatch.setenv("AGET_MIGRATION_FROM", "3.35.0")
    monkeypatch.setenv("AGET_MIGRATION_TO", "3.36.0")
    rc = tmp_path / "receipt.json"
    rid = PL.RBND.start_run("apply_protected", rc)
    PL.RBND.write_result("apply_protected", rc, json.loads(json.dumps(GOOD_RECEIPT)), rid)
    pl = tmp_path / "protected.json"
    pl.write_text("{}")
    out = tmp_path / "pk" / "packet.json"
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--out", str(out), "--receipt", str(rc),
                                      "--protected-list", str(pl), "a"])
    with pytest.raises(SystemExit) as e:
        PL.main()
    assert e.value.code == 2 and "--receipt and --protected-list together" in capsys.readouterr().err
    assert not (tmp_path / "pk").exists()
