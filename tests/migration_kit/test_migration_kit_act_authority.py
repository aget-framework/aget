"""R-F12 (rehearsal, 2026-09-30): authority is tested per ACT, not only per batch. A B4 launch line ending "no push"
authorized `push_batch.py --push`, because the gate asked only whether a typed line named the batch. Now (the push
and ruling rules are F-3, independent review 2026-10-02):

- a launch reads the batch's line; it is refused when a negation word comes before the word launch, at most 30
  characters earlier in the same clause ("do not launch"), and it need not name the launch;
- a push reads only a per-act entry keyed with the batch key and `:push`; the batch's line is never push authority;
- a push line must have the one fixed form (the prefix, `push the commits of batch N`, optionally more batches and
  ` with commit SHA`), and must be the WHOLE typed prompt, not a part of one;
- a baseline-equal ruling line must have its one fixed form (the prefix, `the failures at SHA are baseline-equal`)
  and gets the same whole-prompt test;
- an act-specific entry is ignored for the other act;
- the recorder refuses to record, for an act, a line the gate refuses for it.

A list of refused words would accept a withholding worded outside it; the reviewer's lines of that kind ("the push
remains unapproved", "the push is prohibited", "the push is held") are tested below. Not tested, because the tool does not read it: a later prompt that withdraws the push without repeating the
line, and a condition that exists only inside a block pasted beside the line.

Hermetic fixtures only, as in test_migration_kit_batch_authority.py."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
sys.path.insert(0, str(KIT))


def load(name):
    spec = importlib.util.spec_from_file_location(name, KIT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = load("batch_authority")
REC = load("record_authority")
SID = "abc12345"
LAUNCH_NO_PUSH = "GO supervisor - batch 2 for social-media, launch it, no push"
PUSH_LINE = "GO supervisor - push the commits of batch 2"
PLAIN = "GO supervisor - batch 2 for social-media as planned"
NOT_THE_FORM = "the push line is not in the one accepted form"
RULING_NOT_THE_FORM = "the ruling line is not in the one accepted form"


# R-F1: a session's first prompt is the launch position and never counts as typed authority, so every fixture
# session starts with a neutral prompt, as a real session does before any principal line.
SESSION_START = {"type": "user", "timestamp": "0", "promptSource": "typed", "message": {"content": "session start"}}

def transcript(tmp_path, *lines):
    d = tmp_path / "projects"
    d.mkdir(exist_ok=True)
    rows = [SESSION_START] + [{"type": "user", "timestamp": f"t{i}", "promptSource": "typed", "message": {"content": x}}
                              for i, x in enumerate(lines)]
    (d / f"{SID}-session.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return d


def records(tmp_path, auth):
    f = tmp_path / "records.json"
    f.write_text(json.dumps({"batch_authority": auth}))
    return f


def e(line):
    return {"line": line, "session": SID}


def test_a_launch_line_that_says_no_push_does_not_authorize_the_push(tmp_path):
    """F-3: the batch's line is never push authority, so with no `2:push` entry the push refuses whatever the launch
    line says. Recorded AS the push line, the same line refuses: it is not in the push form."""
    d = transcript(tmp_path, LAUNCH_NO_PUSH)
    recs = records(tmp_path, {"2": e(LAUNCH_NO_PUSH)})
    assert A.check("2", recs, d, act="launch")[0]
    ok, why = A.check("2", recs, d, act="push")
    assert not ok and "needs its own recorded push line" in why
    ok, why = A.check("2", records(tmp_path, {"2:push": e(LAUNCH_NO_PUSH)}), d, act="push")
    assert not ok and NOT_THE_FORM in why


def test_a_push_needs_a_line_in_the_push_form(tmp_path):
    d = transcript(tmp_path, PLAIN)
    recs = records(tmp_path, {"2": e(PLAIN), "2:push": e(PLAIN)})
    assert A.check("2", recs, d, act="launch")[0]
    ok, why = A.check("2", recs, d, act="push")
    assert not ok and NOT_THE_FORM in why


def test_a_second_per_act_line_authorizes_the_push(tmp_path):
    d = transcript(tmp_path, LAUNCH_NO_PUSH, PUSH_LINE)
    recs = records(tmp_path, {"2": e(LAUNCH_NO_PUSH), "2:push": e(PUSH_LINE)})
    ok, why = A.check("2", recs, d, act="push")
    assert ok and "2:push" in why
    assert A.check("2", recs, d, act="launch")[0]          # the launch still reads the batch's line


def test_an_act_entry_is_ignored_for_the_other_act(tmp_path):
    d = transcript(tmp_path, PUSH_LINE)
    recs = records(tmp_path, {"2:push": e(PUSH_LINE)})
    ok, why = A.check("2", recs, d, act="launch")
    assert not ok and "no batch_authority entry" in why


@pytest.mark.parametrize("line,act,excluded", [
    ("GO supervisor - batch 2, launch only, do not push yet", "push", True),
    ("GO supervisor - batch 2, without pushing anything", "push", True),
    ("GO supervisor - batch 2: no problem, push it", "push", False),       # the exclusion stops at the clause
    ("GO supervisor - batch 2, push it, no launch needed", "launch", True),
    ("GO supervisor - batch 2, launch and push", "push", False),
])
def test_exclusion_is_read_within_one_clause(line, act, excluded):
    """Five lines, each with the negation BEFORE the act word or with none: excludes() as a pure function. The gate
    asks excludes() for the launch only (F-3); for a push the fixed form decides, so "no problem, push it", which
    excludes() does not read as excluding, is refused as a push line all the same."""
    assert A.excludes(line, act) is excluded
    assert NOT_THE_FORM in A.act_shape("GO supervisor - batch 2: no problem, push it", "push")


def rec(tmp_path, d, *args):
    f = tmp_path / "records.json"
    if not f.exists():
        records(tmp_path, {})
    return REC.main(["--session", SID, *args], records=f, projects_dir=d), f


def test_the_recorder_refuses_a_push_entry_from_a_line_that_excludes_it(tmp_path):
    """A line that is not in the push form is not recorded as a push line; other such lines are covered at the gate
    by test_a_push_line_in_any_other_wording_refuses, and the recorder calls the same test."""
    d = transcript(tmp_path, LAUNCH_NO_PUSH)
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", LAUNCH_NO_PUSH)
    assert code == 1 and json.loads(f.read_text())["batch_authority"] == {}


def test_the_recorder_writes_a_per_act_entry_beside_the_batch_line(tmp_path):
    d = transcript(tmp_path, LAUNCH_NO_PUSH, PUSH_LINE)
    assert rec(tmp_path, d, "--key", "2", "--line", LAUNCH_NO_PUSH)[0] == 0
    pk = tmp_path / "packet.json"                      # R2-T12: a push line is recorded for one packet
    pk.write_text(json.dumps({"batch": "2", "receivers": []}))
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE, "--packet", str(pk))
    assert code == 0 and set(json.loads(f.read_text())["batch_authority"]) == {"2", "2:push"}


# ---------- F-3 (independent review, 2026-10-02): negative, conditional and truncated push authority ----------

PUSH1 = "GO supervisor - push the commits of batch 1"
RULING = "GO supervisor - the failures at bbbbbbbb are baseline-equal"
RULED_SHA = "b" * 40


def push_check(tmp_path, recorded, *typed):
    """check() for a push of batch 1: `recorded` is the `1:push` entry, `typed` the prompts (default: the line)."""
    d = transcript(tmp_path, *(typed or (recorded,)))
    return A.check("1", records(tmp_path, {"1:push": e(recorded)}), d, act="push")


@pytest.mark.parametrize("line", [
    "GO supervisor - batch 1, the push remains unapproved",          # the reviewer's three lines, second review:
    "GO supervisor - batch 1, the push is prohibited",               # no negation word, no "hold", no "wait"
    "GO supervisor - batch 1, the push is held",
    "GO supervisor - batch 1, push tomorrow",
    "GO supervisor - batch 1, the push is not approved yet",         # the reviewer's three lines, first review
    "GO supervisor - batch 1, hold the push until I review",
    "GO supervisor - batch 1, pushing is forbidden",
    "GO supervisor - batch 1, wait for me before any push",
    "GO supervisor - batch 1, push if the suite is green",           # conditional
    "GO supervisor - batch 1, push it unless I say otherwise",
    "GO supervisor - batch 1, don't push anything",
    "GO supervisor - batch 1, launch and push nothing",
    "GO supervisor - batch 1, I will decide on the push later",
    "GO supervisor - push the commits of batch 1 tomorrow",          # the form, with a word after it
    "GO supervisor - push the commits of batch 1 once CI is green",
    "GO supervisor - do not push the commits of batch 1",            # the form, with words before it
    "GO supervisor - push the commits of batch 1 with commit nothing",   # the commit place takes hexadecimal only
    "GO supervisor - push the commits of batch 1 with commit abc123",    # six characters: too short for a commit id
    "GO supervisor - push the commits of batch 1.",                  # one more character
    "GO supervisor - batch 1, push the verified commits",            # affirmative, worded another way
    "GO supervisor - batch 1: no problem, push it",
    "go supervisor - push the commits of batch 1",                   # the prefix keeps its letter case
])
def test_a_push_line_in_any_other_wording_refuses(tmp_path, line):
    """Each line is typed exactly as recorded, as a whole prompt; it refuses on its form alone. Two are
    affirmative, and the last has the prefix in another letter case: false refusals the rule accepts (the principal
    types the form)."""
    ok, why = push_check(tmp_path, line)
    assert not ok and (NOT_THE_FORM in why or "must start 'GO supervisor - '" in why)


@pytest.mark.parametrize("line,batch", [
    ("GO supervisor - push the commits of batch 1", "1"),
    ("GO supervisor - PUSH the commits of Batch 1", "1"),                                     # letter case
    ("GO supervisor - push the commits of batches 10t and 10", "10t"),
    ("GO supervisor - push the commits of batches 10t, 10 and 11", "11"),
    ("GO supervisor - push the commits of batch 12 with commit abc1234", "12"),
    ("GO supervisor - push the commits of batch 12 with commits abc1234, def56789 and " + "b" * 40, "12"),
])
def test_a_push_line_in_the_fixed_form_typed_alone_is_accepted(tmp_path, line, batch):
    """CONTROL for the refusals above: the form, with each of its optional parts, is accepted for a batch it names."""
    d = transcript(tmp_path, line)
    ok, why = A.check(batch, records(tmp_path, {f"{batch}:push": e(line)}), d, act="push")
    assert ok and f"{batch}:push" in why and "for push typed" in why


def test_a_push_line_naming_another_batch_refuses(tmp_path):
    """The form is not enough: the typed prompt's batch list must name the batch pushed."""
    ok, why = push_check(tmp_path, "GO supervisor - push the commits of batch 2")
    assert not ok and "names batch(es) ['2'], not '1'" in why


def test_the_push_form_follows_the_configured_prefix(tmp_path, monkeypatch):
    monkeypatch.setenv("AGET_MIGRATION_LINE_PREFIX", "GO overseer - ")
    assert push_check(tmp_path, "GO overseer - push the commits of batch 1")[0]
    ok, why = push_check(tmp_path, PUSH1)
    assert not ok and "must start 'GO overseer - '" in why


def test_a_push_line_typed_with_other_spacing_is_accepted(tmp_path):
    ok, why = push_check(tmp_path, PUSH1)
    assert ok and "1:push" in why and "for push typed" in why
    spaced = "  GO supervisor -  push the\ncommits of   batch 1 "                # differs in whitespace only
    assert push_check(tmp_path, PUSH1, spaced)[0]
    assert push_check(tmp_path, spaced)[0]                                       # recorded with that spacing too


def test_a_push_line_must_be_the_whole_typed_prompt(tmp_path):
    """Truncation on either side refuses: the recorded line is clean, the words typed around it are what withhold."""
    for typed in (PUSH1 + " but nothing until I say so",                           # words cut off after the line
                  "I have NOT decided. Draft only, do not act: " + PUSH1,          # words cut off before the line
                  "note: " + PUSH1 + " tomorrow"):                                 # both sides
        ok, why = push_check(tmp_path, PUSH1, typed)
        assert not ok and "not exactly the recorded push line" in why


def test_a_later_longer_prompt_holding_the_push_line_refuses(tmp_path):
    """The newest prompt that holds the line is the one compared: the line typed alone, then quoted inside a longer
    prompt, refuses."""
    assert not push_check(tmp_path, PUSH1, PUSH1, "cancel what I typed, which was: " + PUSH1)[0]


def test_a_pasted_block_beside_the_push_line_is_left_out_of_the_comparison(tmp_path):
    """check_principal_line.own_text removes a paste that sits among other words (it is a quote), so the line plus a
    pasted block equals the line. A prompt that is ONLY a paste is compared whole."""
    paste = '<pasted_content id="x">a report the principal attached</pasted_content id="x">'
    assert push_check(tmp_path, PUSH1, PUSH1 + " " + paste)[0]
    only = f'<pasted_content id="x">{PUSH1} tomorrow</pasted_content id="x">'
    assert not push_check(tmp_path, PUSH1, only)[0]
    assert push_check(tmp_path, PUSH1, f'<pasted_content id="x">{PUSH1}</pasted_content id="x">')[0]


def test_the_batchs_line_never_authorizes_a_push_even_when_it_names_the_push(tmp_path):
    line = "GO supervisor - batch 2 for social-media, launch and push"
    d = transcript(tmp_path, line, PUSH_LINE)
    recs = records(tmp_path, {"2": e(line)})
    assert A.check("2", recs, d, act="launch")[0]
    assert A.entry_for("2", recs, "push") == (None, None)
    ok, why = A.check("2", recs, d, act="push")
    assert not ok and "needs its own recorded push line" in why
    # even a batch line in the push form is not read for a push; recorded as the push entry, it is
    recs = records(tmp_path, {"2": e(PUSH_LINE)})
    assert not A.check("2", recs, d, act="push")[0]
    assert A.check("2", records(tmp_path, {"2:push": e(PUSH_LINE)}), d, act="push")[0]


def test_a_launch_line_is_still_matched_inside_a_longer_prompt(tmp_path):
    """The launch act keeps its behaviour: the batch's line, as a substring, with the clause-bound exclusion only."""
    d = transcript(tmp_path, PLAIN + ", and wait for my word before anything else")
    assert A.check("2", records(tmp_path, {"2": e(PLAIN)}), d, act="launch")[0]
    assert A.act_shape("GO supervisor - batch 2, launch it, hold the report until later", "launch") is None


def test_the_recorder_refuses_a_push_line_typed_inside_a_longer_prompt(tmp_path):
    d = transcript(tmp_path, PUSH_LINE + " once I have read the report")
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE)
    assert code == 1 and json.loads(f.read_text())["batch_authority"] == {}


def ruling(line):
    return {"line": line, "session": SID}


@pytest.mark.parametrize("line", [
    "GO supervisor - bbbbbbbb baseline ruling remains unapproved",       # the reviewer's two lines, second review
    "GO supervisor - bbbbbbbb baseline ruling is prohibited",
    "GO supervisor - do not treat bbbbbbbb as baseline-equal",
    "GO supervisor - bbbbbbbb baseline waiver refused",
    "GO supervisor - bbbbbbbb is baseline-equal unless CI says otherwise",
    "GO supervisor - the failures at bbbbbbbb are baseline-equal unless CI says otherwise",   # the form, then a condition
    "GO supervisor - I doubt the failures at bbbbbbbb are baseline-equal",                    # words before the form
    "GO supervisor - the failures at bbbbbbbb are not baseline-equal",                        # a word inside the form
    "GO supervisor - bbbbbbbb failures ruled baseline-equal",            # affirmative, worded another way
    "GO supervisor - push batch 1 at bbbbbbbb; the two failures ruled baseline-equal",
])
def test_a_baseline_ruling_line_in_any_other_wording_refuses(tmp_path, line):
    """Each line is typed exactly, has the prefix, names the commit and says baseline; it refuses on its form alone.
    The last two are affirmative: false refusals the rule accepts (the principal types the form)."""
    ok, why = A.verify_ruling(ruling(line), RULED_SHA, transcript(tmp_path, line))
    assert not ok and RULING_NOT_THE_FORM in why


def test_a_baseline_ruling_line_in_the_fixed_form_is_accepted_only_for_the_commit_it_names(tmp_path):
    """CONTROL for the refusals above, and the commit binding: 7 or more characters the commit id starts with."""
    for line in (RULING, "GO supervisor - The failures at BBBBBBB are baseline-equal",
                 f"GO supervisor - the failures at {RULED_SHA} are baseline-equal"):
        assert A.verify_ruling(ruling(line), RULED_SHA, transcript(tmp_path, line))[0]
    ok, why = A.verify_ruling(ruling(RULING), "c" * 40, transcript(tmp_path, RULING))
    assert not ok and "does not name the commit cccccccc" in why


def test_a_baseline_ruling_line_must_be_the_whole_typed_prompt(tmp_path):
    for typed in (RULING + " provided CI agrees", "I have NOT decided, this is a draft: " + RULING):
        ok, why = A.verify_ruling(ruling(RULING), RULED_SHA, transcript(tmp_path, typed))
        assert not ok and "not exactly the ruling line" in why
    assert A.verify_ruling(ruling(RULING), RULED_SHA, transcript(tmp_path, RULING))[0]


def test_the_tools_ask_for_their_own_act(tmp_path, monkeypatch):
    """Covers `--push` and `--launch` without `--copy-root`. A `--copy-root` launch asks for no act; not tested."""
    seen = []
    monkeypatch.setattr(A, "check", lambda batch, *a, act=None, **k: (seen.append(act), (False, "x"))[1])
    sys.modules["batch_authority"] = A
    p = tmp_path / "packet.json"
    p.write_text(json.dumps({"batch": "99", "receivers": [], "claude_version": "x"}))
    assert load("push_batch").main(["--packet", str(p), "--push"]) == 6
    assert load("launch_batch").main(["--packet", str(p), "--launch"]) == 6
    assert seen == ["push", "launch"]


# ---------- R2-T12 (C2b): push authority bound to the packet and to the extra commit ----------

def _push_main(tmp_path, monkeypatch, recs, d, packet, *extra):
    """push_batch.main --push on `packet` (no receivers, so nothing is pushed), with the authority read from `recs`
    and the transcripts in `d`: returns the exit code (6 = no typed authority; 0 = authority accepted)."""
    import hashlib  # noqa: F401
    monkeypatch.setitem(sys.modules, "batch_authority", A)
    monkeypatch.setattr(A.check, "__defaults__", (recs, d, None))
    if hasattr(A, "push_authority"):
        monkeypatch.setattr(A.push_authority, "__defaults__", (None, recs, d))
    return load("push_batch").main(["--packet", str(packet), "--push", *extra])


def _packet(tmp_path, name, note):
    p = tmp_path / name
    p.write_text(json.dumps({"batch": "2", "receivers": [], "claude_version": "x", "note": note}))
    return p


def test_r2_t12_a_push_line_recorded_for_one_packet_does_not_authorize_another_with_the_same_batch(tmp_path,
                                                                                                    monkeypatch):
    """R2-T12 (S-163, S-186). The push line for batch 2 is recorded with packet A; a push from packet B, also batch 2,
    is refused (exit 6). Control: packet A is accepted. Before C2b the authority was looked up by batch number only,
    so packet B was accepted."""
    d = transcript(tmp_path, PUSH_LINE)
    a, b = _packet(tmp_path, "a.json", "A"), _packet(tmp_path, "b.json", "B")
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE, "--packet", str(a))
    assert code == 0
    assert _push_main(tmp_path, monkeypatch, f, d, b) == 6
    assert _push_main(tmp_path, monkeypatch, f, d, a) == 0


def test_r2_t12_an_extra_commit_the_push_line_does_not_name_is_refused(tmp_path, monkeypatch):
    """R2-T12 (S-200). --extra-commit names a commit the recorded push line does not (`with commit SHA`): refused
    (exit 6). Control: a line naming that commit is accepted. Before C2b the extra commit was compared with no line."""
    a = _packet(tmp_path, "a.json", "A")
    extra = ["--extra-commit", "abcdef1234", "--extra-paths", "x", "--only", "m"]
    d = transcript(tmp_path, PUSH_LINE)
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE, "--packet", str(a))
    assert code == 0 and _push_main(tmp_path, monkeypatch, f, d, a, *extra) == 6
    named = PUSH_LINE + " with commit abcdef12"
    d2 = transcript(tmp_path / "n", named) if (tmp_path / "n").mkdir() is None else None
    code, f2 = rec(tmp_path / "n", d2, "--key", "2", "--act", "push", "--line", named, "--packet", str(a))
    assert code == 0 and _push_main(tmp_path, monkeypatch, f2, d2, a, *extra) == 0


def test_r2_t12_the_recorder_refuses_a_push_line_without_its_packet(tmp_path):
    """R2-T12: record_authority.py --act push without --packet writes nothing (the line could not be bound)."""
    d = transcript(tmp_path, PUSH_LINE)
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE)
    assert code == 1 and json.loads(f.read_text())["batch_authority"] == {}


# ---------- C2a12: FWK-OVSR6's C2b pre-read 1 (reproduced): HEAD is bound to the id the push line names ----------

def test_c2a12_c2b_preread_1_a_full_id_named_in_the_push_line_binds_head_not_the_cli_prefix(tmp_path, monkeypatch):
    """The push line names a full 40-character commit; --extra-commit gives its first 8. The gate compared HEAD with
    the 8 characters only, so a different commit sharing them would be pushed. The gate now receives the named id.
    Control: a line naming only 8 characters binds those 8."""
    full = "abcdef12" + "3" * 32
    seen = []
    for named_id, want in ((full, full), ("abcdef12", "abcdef12")):
        base = tmp_path / named_id[:12] / ("n" if named_id == full else "s")
        base.mkdir(parents=True)
        p = base / "a.json"
        p.write_text(json.dumps({"batch": "2", "claude_version": "x", "receivers": [
            {"aget": "m", "location": str(base), "head": "f" * 40, "branch": "main"}]}))
        line = PUSH_LINE + f" with commit {named_id}"
        d = transcript(base, line)
        code, f = rec(base, d, "--key", "2", "--act", "push", "--line", line, "--packet", str(p))
        assert code == 0
        monkeypatch.setitem(sys.modules, "batch_authority", A)
        monkeypatch.setattr(A.check, "__defaults__", (f, d, None))
        monkeypatch.setattr(A.push_authority, "__defaults__", (None, f, d))
        PB = load("push_batch")
        monkeypatch.setattr(PB, "packet_refusal", lambda *a, **k: None)
        monkeypatch.setattr(PB, "gate", lambda r, ev, files, extra, allow: (seen.append(extra), (None, "stop"))[1])
        PB.main(["--packet", str(p), "--push", "--extra-commit", "abcdef12", "--extra-paths", "x", "--only", "m"])
        assert seen and seen[-1][0] == want, seen


def test_c2a12_c2b_preread_2_the_packet_and_the_records_are_each_read_once_on_a_push(tmp_path, monkeypatch):
    """FWK-OVSR6's C2b pre-read 2 (MEDIUM, reproduced): the packet was parsed from one read and hashed from another,
    and the push records were read by the typed-line check and again for the entry used, so a concurrent writer could
    pair one file's line or digest with another's contents. Each is now read once, the bytes it checks the bytes it
    uses."""
    import pathlib
    a = _packet(tmp_path, "a.json", "A")
    d = transcript(tmp_path, PUSH_LINE)
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", PUSH_LINE, "--packet", str(a))
    assert code == 0
    reads = []
    for name in ("read_text", "read_bytes"):
        real = getattr(pathlib.Path, name)
        monkeypatch.setattr(pathlib.Path, name, lambda self, *x, _r=real, **k: (reads.append(str(self)), _r(self, *x, **k))[1])
    assert _push_main(tmp_path, monkeypatch, f, d, a) == 0
    assert reads.count(str(a)) == 1 and reads.count(str(f)) == 1, [r for r in reads if r in (str(a), str(f))]


def test_c2a12_preread_a_push_line_naming_a_commit_needs_its_extra_commit(tmp_path, monkeypatch):
    """FWK-OVSR6's C2a12 pre-read (LOW): a push line naming a commit, with --extra-commit omitted, pushed only the
    checked HEAD, silently. It now refuses (exit 6). Control: the same line with --extra-commit is accepted."""
    a = _packet(tmp_path, "a.json", "A")
    named = PUSH_LINE + " with commit abcdef12"
    d = transcript(tmp_path, named)
    code, f = rec(tmp_path, d, "--key", "2", "--act", "push", "--line", named, "--packet", str(a))
    assert code == 0 and _push_main(tmp_path, monkeypatch, f, d, a) == 6
    assert _push_main(tmp_path, monkeypatch, f, d, a, "--extra-commit", "abcdef12", "--extra-paths", "x",
                      "--only", "m") == 0
