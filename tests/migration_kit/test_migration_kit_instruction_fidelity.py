"""Gate 3 of the v3.36.0 kit design pass (v336-release:R28): R3, instruction fidelity, and design read 2's D-3 and D-4.

Each behavioural test fails on 34353311 for the defect it names and passes after the change; R3-T6 (relabel) and
R3-T9 (classification order) test the new module itself and say so. Nothing outside tmp_path is touched.
"""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PL = load("prepare_launch")

AUTHORED = {"path": "scripts/a.py", "op": "hold", "kind": "authored", "authored_lines": 2, "staged": "/stage/a.py",
            "sha256": "a" * 64, "pre": "1" * 64, "authored_ids": ["2" * 64, "3" * 64]}
ZERO = {"path": "scripts/z.py", "op": "hold", "kind": "unattributed", "authored_lines": 0, "staged": "/stage/z.py",
        "sha256": "b" * 64, "pre": "4" * 64}
NO_SOURCE = {"path": "scripts/n.py", "op": "hold", "kind": "no-source", "authored_lines": None, "pre": "5" * 64}
R = {"aget": "example-x-aget", "template": "template-x-aget", "head": "a" * 40, "items": [AUTHORED, ZERO, NO_SOURCE],
     "pins": {"core": "c" * 40, "template-x-aget": "t" * 40}, "pre_dirty": [], "untracked_protected": [],
     "commit_protected": []}


def test_round2_extra_step_is_rendered_verbatim_without_file_staging_suffix():
    """M-8: a suite-only instruction carries no invented file write or staging instruction."""
    step = "For pytest, run only the declared step-5 suite command; do not run targeted test commands."
    prompt = PL.prompt({**R, "extra_steps": [step]}, "att-1", [])
    assert next(line for line in prompt.splitlines() if line.startswith("4c.")) == "4c. " + step


@pytest.mark.parametrize("spec", ["misspelled=instruction", "member= ", "member"])
def test_round2_extra_step_unknown_member_or_empty_instruction_is_refused(tmp_path, monkeypatch, capsys, spec):
    """M-8: malformed extra steps refuse before making a packet or reading the apply list."""
    import sys
    out = tmp_path / "packet.json"
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--out", str(out), "--protected-list",
                                     str(tmp_path / "absent.json"), "--extra-step", spec, "--", "member"])
    with pytest.raises(SystemExit) as exc:
        PL.main()
    assert exc.value.code == 2 and "--extra-step" in capsys.readouterr().err
    assert not out.exists() and not (tmp_path / PL.R.SLUG).exists()


def test_r3_t1_a_zero_line_hold_is_told_to_keep_its_copy():
    """R3-T1, J-1 (S-234, S-235). A hold with 0 authored lines renders KEEP ("keep your copy", "do not take the
    release bytes"), never "Take the release changes"; an authored hold still renders MERGE; a no-source hold never
    says "from None". At 34353311 every hold renders `MERGE … Take the release changes from <staged>`."""
    p = PL.prompt(R, "att-1", [])
    zero_line = [ln for ln in p.splitlines() if "scripts/z.py" in ln][0]
    assert "KEEP scripts/z.py" in zero_line and "Keep your copy" in zero_line
    assert "do not take the release bytes" in zero_line and "Take the release changes" not in zero_line
    assert "MERGE scripts/a.py" in p and "2 line(s) of your own" in p
    no_src = [ln for ln in p.splitlines() if "scripts/n.py" in ln][0]
    assert "KEEP scripts/n.py" in no_src and "None" not in no_src


def test_r3_t2_a_zero_line_hold_gets_no_edit_rule_and_no_write_set_entry():
    """R3-T2 (S-230, S-231, S-261). At 34353311 every hold gets Edit(<path>) and a write-set entry (:275, :285)."""
    rules, ws = PL.allowlist(R), PL.write_set(R)
    for keep in ("scripts/z.py", "scripts/n.py"):
        assert f"Edit({keep})" not in rules and keep not in ws
    assert "Edit(scripts/a.py)" in rules and "scripts/a.py" in ws                     # control: the merge


def test_r3_t4_an_unknown_label_is_refused_by_every_consumer(tmp_path, monkeypatch):
    """R3-T4 (S-221, S-234, S-256). An item with op 'bogus' carrying source, pre and post: the apply plan refuses it
    (34353311 writes any label that is not hold, :119); the prompt raises (34353311 is silent); the B4 approval check
    refuses it (D-4, below). The after-run half is in test_migration_kit_after_run_check.py."""
    A = load("apply_protected")
    loc = tmp_path / "m"
    loc.mkdir()
    subprocess.run(["git", "init", "-q", str(loc)], check=True)
    monkeypatch.setattr(A, "release_bytes", lambda src: b"release\n")
    entry = {"aget": "m", "location": str(loc), "head": "(unborn)", "ops": [
        {"path": "f.txt", "op": "bogus", "pre": "absent", "post": hashlib.sha256(b"release\n").hexdigest(),
         "source": "x@v:f.txt", "source_sha256": hashlib.sha256(b"release\n").hexdigest()}]}
    ok, why, actions = A.plan_aget(entry)
    assert not ok and not actions and "bogus" in why
    with pytest.raises(Exception):
        PL.prompt({**R, "items": [{"path": "f.txt", "op": "bogus"}]}, "att-1", [])


def test_r3_t5_a_refused_path_is_unsafe_and_cannot_be_relabelled_to_write():
    """R3-T5, B131 (S-212, S-245). A list op `unsafe` cannot become `write` by --resolved-file. At 34353311
    apply_resolved overwrites any label with write."""
    PW = load("prepare_write_list")
    doc = {"agets": [{"aget": "f", "location": "/nowhere", "ops": [
        {"path": ".claude/skills/x/SKILL.md", "op": "unsafe", "why": "unsafe path: a link"}]}]}
    with pytest.raises(ValueError):
        PW.apply_resolved(doc, {"f": {".claude/skills/x/SKILL.md": "f@r:x"}}, read=lambda s: b"bytes\n")
    held = {"agets": [{"aget": "f", "location": "/nowhere", "ops": [
        {"path": "scripts/m.py", "op": "hold", "kind": "authored", "authored_lines": 1}]}]}
    PW.apply_resolved(held, {"f": {"scripts/m.py": "f@r:m"}}, read=lambda s: b"mine\n")     # control: hold -> write
    assert held["agets"][0]["ops"][0]["op"] == "write"


def test_r3_t6_relabels_are_listed_and_rederive_the_placing_fields():
    """R3-T6 (S-233, S-242), unit level (new module): a hold relabelled to write keeps no release `cp` command; an
    unsafe item cannot be relabelled. The prepare_launch.main site uses this function."""
    IM = load("item_meaning")
    out = IM.relabel({**ZERO, "command": "cp -f /stage/z.py scripts/z.py", "mkdir": "mkdir -p scripts"}, "write",
                     staged=None, placed_by="the write list (receiver-authored bytes)")
    assert "command" not in out and "mkdir" not in out and out["op"] == "write"
    with pytest.raises(IM.UnknownClassification):
        IM.relabel({"path": "p", "op": "unsafe", "why": "link"}, "write")


def test_r3_t7_a_phase_one_zero_line_hold_is_kept_not_merged(tmp_path, monkeypatch):
    """R3-T7 (S-229, S-237, S-241). In a repair packet, a phase-1 hold with 0 authored lines is `kept` (judged by its
    digest), an authored one `merged`. At 34353311 every phase-1 hold becomes `merged`."""
    monkeypatch.setattr(PL.L, "resolve_template", lambda loc, name: ("template-x-aget", "test"))
    monkeypatch.setattr(PL.L, "payload_expectations", lambda tpl: {"scripts/z.py": "present", "scripts/a.py": "present"})
    monkeypatch.setattr(PL.L.W.V, "framework_root", lambda: str(tmp_path))
    monkeypatch.setattr(PL, "closure", lambda payload, tpl, core: {})
    monkeypatch.setattr(PL, "pin", lambda repo: "p" * 40)
    monkeypatch.setattr(PL, "source_repo", lambda path, tpl, core: tmp_path)
    items = {"scripts/z.py": dict(ZERO), "scripts/a.py": dict(AUTHORED)}
    monkeypatch.setattr(PL, "classify_path", lambda loc, path, src, tpl, why=None: dict(items[path]))
    loc = tmp_path / "m"
    loc.mkdir()
    subprocess.run(["git", "init", "-q", str(loc)], check=True)
    plan = PL.plan_receiver("m", str(loc), repair=True, merged={"scripts/z.py", "scripts/a.py"})
    ops = {i["path"]: i["op"] for i in plan["items"]}
    assert ops == {"scripts/z.py": "kept", "scripts/a.py": "merged"}


@pytest.mark.parametrize("source,lines,kind", [(False, 0, "no-source"), (False, None, "no-source"),
                                               (True, 0, "unattributed"), (True, 2, "authored"), (True, None, None)])
def test_r3_t9_the_classification_order_is_total_and_disjoint(source, lines, kind):
    """R3-T9 (S-226, S-235; design read 1 D-11), unit level: no source is no-source whatever the count; source with 0
    is unattributed; source with a missing count has no kind and meaning() refuses it."""
    IM = load("item_meaning")
    assert IM.classify_kind("hold", source, lines) == kind
    if kind is None:
        with pytest.raises(IM.UnknownClassification):
            IM.meaning({"path": "p", "op": "hold", "kind": kind, "staged": "s"})


# --- design read 2, D-3 and D-4 ------------------------------------------------------------------------------------

def test_d3_s283_an_unknown_payload_expectation_is_a_finding(monkeypatch, tmp_path):
    """D-3 (S-283, fleet_ledger.py:349). A template expectation label outside {present, absent} is a finding, never
    judged as `present`. At 34353311 any label other than `absent` is judged as present, so a matching blob passes."""
    L = load("fleet_ledger")
    monkeypatch.setattr(L, "blob", lambda *a: "b" * 40)
    monkeypatch.setattr(L.W.V, "framework_root", lambda: str(tmp_path))
    findings = L.payload_findings(tmp_path, "", "s" * 40, "template-x-aget", {"scripts/q.py": "optional"}, {})
    assert any("unknown payload expectation" in f for f in findings), findings
    assert L.payload_findings(tmp_path, "", "s" * 40, "template-x-aget", {"scripts/q.py": "present"}, {}) == []


def test_d3_s288_capture_states_are_already_closed():
    """D-3 (S-288), the reasoned exclusion's evidence: verify_extension_survival refuses any capture state outside
    {present, absent}. It is a record validator, not a payload classification, so R3's table does not apply. This
    passes at 34353311 too; it is a control for the exclusion, not a failing-first test."""
    V = load("verify_extension_survival")
    import inspect
    src = inspect.getsource(V)
    assert "state not in ('present', 'absent')" in src and "capture record with unknown state" in src


def test_d4_the_approval_check_refuses_an_unknown_classification(tmp_path):
    """D-4 (S-253, check_list_approvable.py:83). With every other approval input passing (V3.6 PASS with an empty
    blind-spot report, V3.7 PASS, both current and naming this list), a list op with no meaning row is refused. At
    34353311 a label not in (noop, hold) counts as written and the list is approvable."""
    CA, RBND = load("check_list_approvable"), load("result_binding")
    lst = tmp_path / "LIST.json"
    lst.write_text(json.dumps({"agets": [{"aget": "a", "location": str(tmp_path), "ops": [
        {"path": "scripts/w.py", "op": "write"}, {"path": "scripts/q.py", "op": "bogus"}]}]}))
    sha = hashlib.sha256(lst.read_bytes()).hexdigest()

    def produced(step, out, doc):
        RBND.write_result(step, out, doc, RBND.start_run(step, out))
    v36, v37 = tmp_path / "V36.json", tmp_path / "V37.json"
    produced("rehearse_batch2", v36, {"list_sha256": sha,
                                      "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}]})
    produced("rehearse_v37", v37, {"verdict": "PASS", "list_sha256": sha, "members": {"a": {"verdict": "PASS"}}})
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 1
    doc = json.loads(lst.read_text())
    doc["agets"][0]["ops"] = doc["agets"][0]["ops"][:1]                          # control: only the write
    lst.write_text(json.dumps(doc))
    sha = hashlib.sha256(lst.read_bytes()).hexdigest()
    produced("rehearse_batch2", v36, {"list_sha256": sha,
                                      "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}]})
    produced("rehearse_v37", v37, {"verdict": "PASS", "list_sha256": sha, "members": {"a": {"verdict": "PASS"}}})
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 0


# --- REVW3's B148 read, finding 2: every consumer validates (op, kind) before it filters by op -----------------

def _git_member(loc):
    loc.mkdir(parents=True)
    (loc / "a.txt").write_text("x\n")
    subprocess.run(["git", "init", "-q", str(loc)], check=True)
    subprocess.run(["git", "-C", str(loc), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"],
                   check=True)
    return subprocess.run(["git", "-C", str(loc), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def test_b148_2_the_apply_does_not_silently_hold_an_unknown_kind(tmp_path):
    """B148 finding 2 (REVW3's falsifier). A protected-write entry `(hold, bogus)` is refused at the plan. On stage F2
    the apply closed only the op set and skipped every `hold` before reading its kind: `(True, '', [])`."""
    A = load("apply_protected")
    m = tmp_path / "m"
    head = _git_member(m)
    item = {"path": "a.txt", "op": "hold", "kind": "bogus", "authored_lines": 0, "pre": "x"}
    ok, why, actions = A.plan_aget({"aget": "m", "location": str(m), "head": head, "ops": [item]})
    assert not ok and "CLASSIFICATION" in why and actions == [], (ok, why)


@pytest.mark.parametrize("consumer", ["write_set", "allowlist", "repair_prompt", "placing_commands",
                                      "launch_refusals"])
def test_b148_2_an_unknown_item_is_refused_by_repair_and_launch_consumers(tmp_path, consumer):
    """B148 finding 2 (REVW3's falsifiers). An item with op `bogus` is refused by the repair write set and allowlist,
    the repair prompt, the placing commands (an exception) and the launch's pre-session refusals (an UNKNOWN
    CLASSIFICATION reason: that function returns its reasons). On stage F2 each omitted it silently."""
    LB = load("launch_batch")
    r = {"aget": "a", "location": str(tmp_path), "head": "a" * 40, "template": "t",
         "pins": {"core": "a" * 40, "t": "b" * 40},
         "items": [{"path": "q.py", "op": "bogus", "staged": "/unused", "pre": "absent"}],
         "pre_dirty": [], "untracked_protected": [], "commit_protected": [], "allowlist": [], "write_set": []}
    fns = {"write_set": lambda: PL.write_set(r, repair=True), "allowlist": lambda: PL.allowlist(r, repair=True),
           "repair_prompt": lambda: PL.repair_prompt(r, "a", "b"),
           "placing_commands": lambda: PL.placing_commands(r["items"][0], str(tmp_path)),
           "launch_refusals": lambda: LB.launch_refusals(r)}
    try:
        got = fns[consumer]()
    except ValueError as e:                  # UnknownClassification is a ValueError
        assert "q.py" in str(e) and "bogus" in str(e), e
        return
    assert consumer == "launch_refusals" and any("UNKNOWN CLASSIFICATION" in w and "q.py" in w for w in got), got


def test_b148_4_a_duplicate_path_cannot_erase_an_unlisted_relabel(tmp_path):
    """B148 finding 4 (REVW3's falsifier). A `hold` row followed by an `unsafe` row for the same path: the receiver's
    resolution must not turn both into one `write` (`unsafe -> write` is not in RELABELS). On stage F2 only the first
    row was checked and every row for the path was replaced: the list held one `write`."""
    PW = load("prepare_write_list")
    doc = {"agets": [{"aget": "a", "location": str(tmp_path), "ops": [
        {"path": "q.py", "op": "hold", "kind": "authored", "authored_lines": 1},
        {"path": "q.py", "op": "unsafe", "why": "link"}]}]}
    try:
        got = PW.apply_resolved(doc, {"a": {"q.py": "repo@r:q.py"}}, lambda s: b"release\n")
    except ValueError as e:
        assert "q.py" in str(e), e
        return
    pytest.fail(f"the duplicate rows became {[o['op'] for o in got['agets'][0]['ops']]}")


# --- REVW4's B151 read of stage E2c ------------------------------------------------------------------------------

@pytest.mark.parametrize("consumer", ["module_relabel", "resolved_write", "track_push"])
def test_b151_4_unknown_old_classification_cannot_be_erased_or_skipped(tmp_path, consumer):
    """B151 finding 4 (REVW4's falsifier). An unknown old row `(hold, bogus)` is refused before a relabel, before the
    receiver's resolution replaces it with `write`, and by the push gate's track-skills branch. On stage E2c all
    three returned normally: a valid `merged/authored` item, one `write` row, and the item omitted."""
    IM = load("item_meaning")
    item = {"path": "q.py", "op": "hold", "kind": "bogus", "authored_lines": 1, "staged": "source"}
    if consumer == "module_relabel":
        fn = lambda: IM.relabel(item, "merged")
    elif consumer == "resolved_write":
        PW = load("prepare_write_list")
        doc = {"agets": [{"aget": "a", "location": str(tmp_path), "ops": [dict(item)]}]}
        fn = lambda: PW.apply_resolved(doc, {"a": {"q.py": "repo@r:q.py"}}, lambda x: b"bytes\n")
    else:
        PB = load("push_batch")
        m = tmp_path / "m"
        head = _git_member(m)
        fn = lambda: PB.untracked_writes({"location": str(m), "mode": "track-skills", "items": [item]}, head)
    with pytest.raises(ValueError, match="bogus"):
        fn()


@pytest.mark.parametrize("lines", [True, 1.0])
def test_b151_5_meaning_uses_the_same_integer_predicate_as_the_classifier(lines):
    """B151 finding 5 (REVW4's falsifier, and the float case of its "numeric-equality weakness"). `meaning` applies the
    classifier's predicate: `authored_lines: true` (a bool) or `1.0` (a float) is not an authored count, so a stored
    `authored` kind is refused. On stage E2c `True` returned a writable MERGE row while the classifier gave no kind."""
    IM = load("item_meaning")
    assert IM.classify_kind("hold", True, lines) is None
    with pytest.raises(IM.UnknownClassification):
        IM.meaning({"path": "x", "op": "hold", "kind": "authored", "authored_lines": lines, "staged": "source"})
    with pytest.raises(IM.UnknownClassification):
        IM.meaning({"path": "x", "op": "hold", "kind": "unattributed", "authored_lines": False, "staged": "source"})
    assert IM.meaning({"path": "x", "op": "hold", "kind": "authored", "authored_lines": 1, "staged": "s"})
    assert IM.meaning({"path": "x", "op": "hold", "kind": "unattributed", "authored_lines": 0, "staged": "s"})


def test_d2_r3_the_prompt_names_protected_holds_with_their_row():
    """D2 (R3, DESIGN: "The prompt names protected holds from the protected-write list with their KEEP or LEAVE row.
    Today it names only the protected paths that are written"): a protected file the principal's apply held was never
    named, so the session had no instruction for it. Each is now named with its own meaning row's line; a held line
    reads LEAVE. Control: a receiver with no protected holds gets no such line."""
    holds = [{"path": ".claude/skills/p/SKILL.md", "op": "hold", "kind": "no-source", "pre": "6" * 64},
             {"path": ".claude/hooks/h.sh", "op": "hold-line", "kind": None, "pre": "7" * 64}]
    p = PL.prompt({**R, "protected_holds": holds}, "att-1", [])
    assert "KEEP .claude/skills/p/SKILL.md" in p, p
    assert "LEAVE .claude/hooks/h.sh" in p, p
    assert ".claude/skills/p/SKILL.md" not in PL.prompt(R, "att-1", [])
