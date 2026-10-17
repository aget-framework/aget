"""Carriage row 62: `push_batch.py --push` and `launch_batch.py --launch` (tested here WITHOUT `--copy-root`, which
skips the check) check the principal's typed line themselves, and the authority recorder applies its transcript checks
before writing. One test per refusal path (lesson: an allow rule that removes an outside check must move that check
into the tool, bound to evidence the actor cannot write). Hermetic fixtures only."""
import importlib.util
import json
import re
import subprocess
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
LINE12 = "GO supervisor - batch 12 as batch 10 with the held note commits"


def prompt(ts, source, text):
    return {"type": "user", "timestamp": ts, "promptSource": source, "message": {"content": text}}


def queued(ts, text):
    return {"type": "attachment", "timestamp": ts,
            "attachment": {"type": "queued_command", "prompt": text, "origin": {"kind": "human"}, "timestamp": ts}}


# R-F1: a session's first prompt is the launch position and never counts as typed authority, so every fixture
# session starts with a neutral prompt, as a real session does before any principal line.
SESSION_START = {"type": "user", "timestamp": "0", "promptSource": "typed", "message": {"content": "session start"}}

def transcript(tmp_path, rows):
    d = tmp_path / "projects"
    d.mkdir(exist_ok=True)
    (d / f"{SID}-session.jsonl").write_text("\n".join(json.dumps(r) for r in [SESSION_START, *rows]) + "\n")
    return d


def records(tmp_path, auth=None):
    f = tmp_path / "records.json"
    f.write_text(json.dumps({"batch_authority": auth or {}}))
    return f


def entry(line=LINE12):
    return {"line": line, "session": SID}


def anchor_ledger(f):
    """Import synthetic scope history through the recorder before exercising the read-only gate."""
    doc = json.loads(f.read_text())
    if isinstance(doc.get("scope_overrides"), dict):
        assert REC.main(["--archive-ledger", str(f)], records=f) == 0


def handwritten_launch(f, key, line, session=SID):
    """The gate must independently refuse even a recorder-bypassing entry."""
    doc = json.loads(f.read_text())
    doc["batch_authority"][f"{key}:launch"] = {"line": line, "session": session}
    f.write_text(json.dumps(doc))


# ---------- the gate: accepts ----------

def test_a_typed_line_naming_the_batch_passes(tmp_path):
    d = transcript(tmp_path, [prompt("2026-09-30T08:40:00Z", "typed", LINE12)])
    ok, why = A.check("12", records(tmp_path, {"12": entry()}), d)
    assert ok and "typed" in why and "['12']" in why


def test_a_mid_turn_human_entry_passes_and_is_disclosed(tmp_path):
    d = transcript(tmp_path, [queued("2026-09-30T08:40:00Z", LINE12)])
    ok, why = A.check("12", records(tmp_path, {"12": entry()}), d)
    assert ok and "mid-turn" in why


def test_a_joined_key_serves_each_batch_the_prompt_names(tmp_path):
    line = "GO supervisor - batches 10t and 10 as batch 7, same terms as before"
    d = transcript(tmp_path, [prompt("t", "typed", line)])
    recs = records(tmp_path, {"10t+10": entry(line)})
    assert A.check("10t", recs, d)[0] and A.check("10", recs, d)[0]


# ---------- the gate: refusals ----------

def test_no_entry_for_the_batch_refuses(tmp_path):
    ok, why = A.check("12", records(tmp_path, {"11": entry()}), tmp_path)
    assert not ok and "no batch_authority entry" in why


def test_unreadable_records_refuse(tmp_path):
    ok, why = A.check("12", tmp_path / "absent.json", tmp_path)
    assert not ok and "records unreadable" in why


@pytest.mark.parametrize("line", ["GO - yes", "GO supervisor - batch 12", "go supervisor - batch 12 as batch 10 please"])
def test_a_short_or_wrongly_prefixed_line_refuses(tmp_path, line):
    d = transcript(tmp_path, [prompt("t", "typed", line)])
    ok, why = A.check("12", records(tmp_path, {"12": entry(line)}), d)
    assert not ok and "at least 30 characters" in why


def test_an_accepted_suggestion_refuses(tmp_path):
    d = transcript(tmp_path, [prompt("t", "suggestion_accepted", LINE12)])
    ok, why = A.check("12", records(tmp_path, {"12": entry()}), d)
    assert not ok and "not typed" in why


def test_a_line_in_no_prompt_refuses(tmp_path):
    d = transcript(tmp_path, [prompt("t", "typed", "proceed with recommendations")])
    ok, why = A.check("12", records(tmp_path, {"12": entry()}), d)
    assert not ok and "in no principal prompt" in why


def test_a_pasted_quote_of_the_line_is_not_the_principals_line(tmp_path):
    quoted = f"look at this <pasted_content id=\"x\">{LINE12}</pasted_content id=\"x\">"
    d = transcript(tmp_path, [prompt("t", "typed", quoted)])
    ok, _ = A.check("12", records(tmp_path, {"12": entry()}), d)
    assert not ok


def test_an_entry_quoting_another_batchs_line_refuses(tmp_path):
    """The records file is written by the supervisor; the batch must come from the typed prompt itself."""
    d = transcript(tmp_path, [prompt("t", "typed", LINE12)])
    ok, why = A.check("13", records(tmp_path, {"13": entry()}), d)
    assert not ok and "names batch(es) ['12'], not '13'" in why


def test_the_prefix_follows_the_supervisors_name(tmp_path, monkeypatch):
    line = "GO overseer - batch 4 as batch 3, same terms and checks"
    d = transcript(tmp_path, [prompt("t", "typed", line)])
    recs = records(tmp_path, {"4": entry(line)})
    assert not A.check("4", recs, d)[0]
    monkeypatch.setenv("AGET_MIGRATION_LINE_PREFIX", "GO overseer - ")
    assert A.check("4", recs, d)[0]


def test_first_batch_list_parsing():
    assert A.named_batches("batch 12 as batch 10 with held") == ["12"]
    assert A.named_batches("batches 10t and 10 as batch 7") == ["10t", "10"]
    assert A.named_batches("no batch here") == []


def test_the_transcript_folder_is_derived_from_the_repository_not_one_laptop():
    C = load("check_principal_line")
    assert C.DEFAULT_DIR.name == re.sub(r"[^A-Za-z0-9]", "-", str(C.KIT_ROOT))
    assert C.DEFAULT_DIR.name.startswith("-") and "/" not in C.DEFAULT_DIR.name


# ---------- the recorder ----------

def rec(tmp_path, d, *args):
    f = tmp_path / "records.json"
    if not f.exists():
        records(tmp_path)
    return REC.main(["--session", SID, *args], records=f, projects_dir=d), f


def test_the_recorder_writes_a_typed_line_once(tmp_path):
    d = transcript(tmp_path, [prompt("t", "typed", LINE12)])
    code, f = rec(tmp_path, d, "--key", "12", "--line", LINE12)
    assert code == 0 and "typed" in json.loads(f.read_text())["batch_authority"]["12"]["source"]
    assert rec(tmp_path, d, "--key", "12", "--line", LINE12)[0] == 1          # never replaced


def test_the_recorder_refuses_what_the_gate_refuses_and_writes_nothing(tmp_path):
    d = transcript(tmp_path, [prompt("t", "suggestion_accepted", LINE12)])
    code, f = rec(tmp_path, d, "--key", "12", "--line", LINE12)
    assert code == 1 and json.loads(f.read_text())["batch_authority"] == {}


def test_the_recorder_dry_run_writes_nothing(tmp_path):
    d = transcript(tmp_path, [prompt("t", "typed", LINE12)])
    code, f = rec(tmp_path, d, "--key", "12", "--line", LINE12, "--dry-run")
    assert code == 0 and json.loads(f.read_text())["batch_authority"] == {}


def packet(tmp_path, aget, location):
    p = tmp_path / "packet.json"
    p.write_text(json.dumps({"receivers": [{"aget": aget, "location": str(location)}]}))
    return p


def test_a_scope_override_needs_a_receiver_the_prompt_names(tmp_path):
    line = "GO supervisor - batch 12 for example-core with its wider scope"
    d = transcript(tmp_path, [prompt("t", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p),
               "--scope-override", "example-note-aget=all")[0] == 1       # not a receiver
    p2 = tmp_path / "p2.json"
    p2.write_text(json.dumps({"receivers": [{"aget": "example-note-aget", "location": str(tmp_path)}]}))
    assert rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p2),
               "--scope-override", "example-note-aget=all")[0] == 1       # a receiver the prompt never names
    code, f = rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    ov = json.loads(f.read_text())["scope_overrides"]["example-core-aget"]
    assert code == 0 and ov["batches"] == ["12"] and ov["history"][0]["line"] == line


def test_a_check_change_needs_its_own_typed_line_naming_both(tmp_path):
    check = "GO supervisor - loosen check F for example-core to warn"
    d = transcript(tmp_path, [prompt("t", "typed", check)])
    assert rec(tmp_path, d, "--check-change", "example-core-aget:F=warn")[0] == 1   # no --check-line
    assert rec(tmp_path, d, "--check-line", check,
               "--check-change", "example-core-aget:G=warn")[0] == 1               # line names F, not G
    code, f = rec(tmp_path, d, "--check-line", check, "--check-change", "example-core-aget:F=warn")
    assert code == 0 and "F" in json.loads(f.read_text())["check_change_rulings"]["example-core-aget"]


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout.strip()


def test_held_commits_must_equal_what_the_receiver_actually_holds(tmp_path):
    bare, work = tmp_path / "remote.git", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "clone", "-q", str(bare), str(work)], check=True, capture_output=True)
    for cfg in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
        git(work, "config", *cfg)
    git(work, "commit", "-q", "--allow-empty", "-m", "base")
    git(work, "push", "-q", "-u", "origin", "HEAD")
    git(work, "commit", "-q", "--allow-empty", "-m", "session note")
    held = git(work, "rev-parse", "HEAD")[:7]
    line = "GO supervisor - batch 12 for example-note, push its held note"
    d = transcript(tmp_path, [prompt("t", "typed", line)])
    p = packet(tmp_path, "example-note-aget", work)
    assert rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p),
               "--held", "example-note-aget=deadbee")[0] == 1                   # not what the receiver holds
    code, f = rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p),
                  "--held", f"example-note-aget={held}")
    assert code == 0 and json.loads(f.read_text())["batch_authority"]["12"]["held_commits"] == {
        "example-note-aget": [held]}


# ---------- the tools refuse before doing anything (launch: without --copy-root only) ----------

@pytest.mark.parametrize("tool,flag,word", [("launch_batch", "--launch", "STOPPED"), ("push_batch", "--push", "NOT PUSHED")])
def test_a_live_launch_or_push_without_typed_authority_exits_6(tmp_path, capsys, tool, flag, word):
    """Covers `--push`, and `--launch` without `--copy-root`. `--launch --copy-root` runs no authority check; not tested."""
    p = tmp_path / "packet.json"
    p.write_text(json.dumps({"batch": "99", "receivers": [], "claude_version": "x"}))
    assert load(tool).main(["--packet", str(p), flag]) == 6
    assert f"{word}: no typed authority for batch 99" in capsys.readouterr().out


def test_names_are_matched_as_whole_words():
    assert REC.names("F", "loosen check F for example-core")
    assert not REC.names("G", "GO supervisor - loosen check F")
    assert not REC.names("cli", "GO supervisor - batch 12 for the client repo")
    assert REC.names("example-core", "batch 12 for example-core, held")


# gh#2968 (carry C32; the first v3.36.0 receiver's F-20): `--scope-override` is recorded only with the batch line,
# into batch_authority[N]; check(act="launch") took that line as launch authority when no `N:launch` entry exists, so
# a line that widened a member's write scope also authorized the launch. A scope-override line must never be launch
# authority: the launch needs its own `--act launch` line, as the push already does.
OVERRIDE12 = "GO supervisor - batch 12 scope override for example-core with its wider scope"
LAUNCH12 = "GO supervisor - launch batch 12 for example-core as prepared"


def test_a_scope_override_line_is_not_launch_authority(tmp_path):
    d = transcript(tmp_path, [prompt("t1", "typed", OVERRIDE12)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12", "--line", OVERRIDE12, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert not ok and "launch" in why, why


def test_a_launch_line_after_a_scope_override_authorizes_the_launch(tmp_path):
    d = transcript(tmp_path, [prompt("t1", "typed", OVERRIDE12), prompt("t2", "typed", LAUNCH12)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", OVERRIDE12, "--packet", str(p),
               "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "12", "--act", "launch", "--line", LAUNCH12)
    assert code == 0
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert ok, why


def test_a_plain_batch_line_still_authorizes_the_launch(tmp_path):
    # unchanged behaviour: a batch line recorded without scope overrides is still launch authority
    f = records(tmp_path, {"12": entry()})
    d = transcript(tmp_path, [prompt("t", "typed", LINE12)])
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("key,batches,line", [
    ("12", ["12"], OVERRIDE12),
    ("12+13", ["12", "13"], OVERRIDE12.replace("batch 12", "batches 12 and 13")),
])
@pytest.mark.parametrize("quote", ["identical", "shortened", "whitespace"])
def test_c32_scope_evidence_rerecorded_for_launch_is_refused(tmp_path, key, batches, line, quote):
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", key, "--line", line, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    launch_quote = line.split(" with ")[0] if quote == "shortened" else line
    if quote == "whitespace":
        launch_quote = "  \n".join(line.split())
    code, f = rec(tmp_path, d, "--key", key, "--act", "launch", "--line", launch_quote)
    assert code == 1  # the recorder and the gate must agree
    handwritten_launch(f, key, launch_quote)
    for batch in batches:
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert not ok and "scope" in why, why


def test_c32_two_short_quotes_from_one_scope_prompt_are_not_independent_authority(tmp_path):
    line = OVERRIDE12 + "; " + LAUNCH12
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", OVERRIDE12, "--packet", str(p),
               "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "12", "--act", "launch", "--line", LAUNCH12)
    assert code == 1
    handwritten_launch(f, "12", LAUNCH12)
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why


@pytest.mark.parametrize("history", [None, [], "broken", [None], [{"scope": "all"}]])
def test_c32_incomplete_scope_history_cannot_authorize_launch(tmp_path, history):
    d = transcript(tmp_path, [prompt("t1", "typed", LINE12)])
    f = records(tmp_path, {"12:launch": entry()})
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": {"batches": ["12"], "history": history}}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why


@pytest.mark.parametrize("contents", ["{", None])
def test_c32_unreadable_scope_history_refuses_even_with_a_preloaded_entry(tmp_path, contents):
    d = transcript(tmp_path, [prompt("t1", "typed", LINE12)])
    f = tmp_path / "records.json"
    if contents is not None:
        f.write_text(contents)
    ok, why = A.check("12", records=f, projects_dir=d, act="launch", entry=("12:launch", entry()))
    assert not ok, why


def test_c32_an_unrelated_scope_override_does_not_block_a_plain_batch_line(tmp_path):
    d = transcript(tmp_path, [prompt("t1", "typed", OVERRIDE12), prompt("t2", "typed", LINE12.replace("12", "14"))])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", OVERRIDE12, "--packet", str(p),
               "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "14", "--line", LINE12.replace("12", "14"))
    assert code == 0
    ok, why = A.check("14", records=f, projects_dir=d, act="launch")
    assert ok, why


# v337prep:R1 final fix round: scope evidence belongs to a prompt, never to the supervisor's storage key.
@pytest.mark.parametrize("scope_key,launch_key,batch_list", [
    ("12", "13", "batches 12 and 13"),               # second review, case 1
    ("99", "12", "batches 12 and 99"),               # second review, case 2
    ("12T", "12t", "batch 12t"),                    # second review, case 3
    ("12t", "12T", "batch 12T"),                    # opposite letter case
    ("12T", "12t+13T", "batches 12t and 13T"),       # joined launch storage key
])
@pytest.mark.parametrize("launch_first", [False, True])
@pytest.mark.parametrize("wording", ["scope override with its wider scope", "reviewed terms"])
def test_c32_scope_prompt_cannot_launch_under_another_key(tmp_path, scope_key, launch_key, batch_list,
                                                        launch_first, wording):
    # The neutral wording proves recorded scope evidence is checked even without scope keywords.
    line = f"GO supervisor - {batch_list} for example-core: {wording}"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    scope_args = ["--key", scope_key, "--line", line, "--packet", str(p),
                  "--scope-override", "example-core-aget=all"]
    launch_args = ["--key", launch_key, "--act", "launch", "--line", line]
    for args in ([launch_args, scope_args] if launch_first else [scope_args, launch_args]):
        code, f = rec(tmp_path, d, *args)
        expected = 1 if args is launch_args and (not launch_first or wording != "reviewed terms") else 0
        assert code == expected
    handwritten_launch(f, launch_key, line)
    for batch in launch_key.split("+"):
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert not ok and "scope-override evidence" in why, why


@pytest.mark.parametrize("wording", ["scope override", "scope-override", "wider scope", "override the write scope"])
@pytest.mark.parametrize("short_quote", [False, True])
def test_c32_scope_wording_in_the_prompt_refuses_without_a_scope_record(tmp_path, wording, short_quote):
    quote = "GO supervisor - batches 12 and 13 for example-core"
    line = quote + ": " + wording
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    code, f = rec(tmp_path, d, "--key", "13", "--act", "launch", "--line", quote if short_quote else line)
    assert code == 1
    handwritten_launch(f, "13", quote if short_quote else line)
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope-override evidence" in why, why


def test_c32_disjoint_quotes_from_a_scope_prompt_cannot_launch_another_batch(tmp_path):
    scope_quote = "GO supervisor - batches 12 and 13 for example-core, reviewed terms"
    launch_quote = "GO supervisor - launch batch 13 for example-core as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", scope_quote + "; " + launch_quote)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", scope_quote, "--packet", str(p),
               "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "13", "--act", "launch", "--line", launch_quote)
    assert code == 1
    handwritten_launch(f, "13", launch_quote)
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope-override evidence" in why, why
    # An existing record without the new prompt binding must also be checked against the transcript.
    doc = json.loads(f.read_text())
    h = doc["scope_overrides"]["example-core-aget"]["history"][0]
    h.pop("prompt", None)
    h.pop("session", None)
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope-override evidence" in why, why


@pytest.mark.parametrize("new_session", [False, True])
def test_c32_scope_prompt_identity_does_not_taint_a_separate_typed_launch_prompt(tmp_path, new_session):
    # A separate prompt with its own launch text, in the same or another session.
    line = "GO supervisor - batches 12 and 13 for example-core, reviewed terms"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12", "--line", line, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    launch = "GO supervisor - launch batches 12 and 13 for example-core as prepared"
    sid = "def67890" if new_session else SID
    if new_session:
        (d / f"{sid}-session.jsonl").write_text("\n".join(map(json.dumps, [SESSION_START,
            prompt("t2", "typed", launch)])) + "\n")
    else:
        transcript(tmp_path, [prompt("t1", "typed", line), prompt("t2", "typed", launch)])
    assert REC.main(["--session", sid, "--key", "12+13", "--act", "launch", "--line", launch],
                    records=f, projects_dir=d) == 0
    for batch in ("12", "13"):
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert ok, why


@pytest.mark.parametrize("key,batches", [("12T", ["12t", "12T"]), ("12T+13t", ["12t", "13T"])])
def test_c32_genuine_launch_keys_are_case_insensitive(tmp_path, key, batches):
    line = "GO supervisor - launch batches 12t and 13T for example-core as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    code, f = rec(tmp_path, d, "--key", key, "--act", "launch", "--line", line)
    assert code == 0
    for batch in batches:
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert ok, why
    # Case changes cannot bypass the recorder's no-replacement rule, including for legacy mixed-case keys.
    assert rec(tmp_path, d, "--key", key.swapcase(), "--act", "launch", "--line", line)[0] == 1


def test_c32_scope_batch_ids_are_normalized_without_widening_the_granted_scope(tmp_path):
    line = "GO supervisor - batches 12T and 13t for example-core, reviewed terms"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12T", "--line", line, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    ov = json.loads(f.read_text())["scope_overrides"]["example-core-aget"]
    assert ov["batches"] == ["12t"]  # naming 13t is evidence, not a scope grant for 13t
    assert ov["history"][0]["batches_added"] == ["12t"]


# v337prep:R4: a principal act stays the same act across resumed/forked copies.
NEUTRAL_SCOPE = "GO supervisor - batches 12 and 13 for example-core: reviewed terms, docs may be written"


def write_session(d, sid, rows):
    f = d / f"{sid}-session.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in [SESSION_START, *rows]) + "\n")
    return f


@pytest.mark.parametrize("fork", ["0fork000", "def67890"])
@pytest.mark.parametrize("pin", ["new", "old", "legacy"])
@pytest.mark.parametrize("launch_session", [False, True])
def test_c32_copied_prompt_is_scope_evidence_regardless_of_filename_order(tmp_path, fork, pin, launch_session):
    d = transcript(tmp_path, [prompt("t1", "typed", NEUTRAL_SCOPE)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12", "--line", NEUTRAL_SCOPE, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    write_session(d, fork, [prompt("t1", "typed", NEUTRAL_SCOPE.replace(" ", "\u00a0"))])
    doc = json.loads(f.read_text())
    h = doc["scope_overrides"]["example-core-aget"]["history"][0]
    if pin == "legacy":
        h.pop("prompt", None)
    elif pin == "old":
        h["prompt"] = {"transcript": f"{SID}-session.jsonl", "timestamp": "t1", "text": NEUTRAL_SCOPE}
    doc["batch_authority"]["13:launch"] = {"line": NEUTRAL_SCOPE, **({"session": fork} if launch_session else {})}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why


def test_c32_prompt_identity_uses_timestamp_and_normalized_text_only():
    import check_principal_line as C
    one = ("t1", "typed", NEUTRAL_SCOPE)
    copy = ("t1", "typed", NEUTRAL_SCOPE.replace(" ", "  \n"))
    assert C.prompt_identity(Path("a.jsonl"), one) == C.prompt_identity(Path("z.jsonl"), copy)
    assert "transcript" not in C.prompt_identity(Path("a.jsonl"), one)
    assert C.prompt_identity(Path("a.jsonl"), one) != C.prompt_identity(Path("a.jsonl"), ("t2", *one[1:]))


@pytest.mark.parametrize("legacy", [False, True])
def test_c32_scope_binding_survives_original_transcript_removed_when_copy_remains(tmp_path, legacy):
    d = transcript(tmp_path, [prompt("t1", "typed", NEUTRAL_SCOPE)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12", "--line", NEUTRAL_SCOPE, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    doc = json.loads(f.read_text())
    h = doc["scope_overrides"]["example-core-aget"]["history"][0]
    if legacy:
        h.pop("prompt", None)
    else:
        h["prompt"]["transcript"] = f"{SID}-session.jsonl"
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    write_session(d, "def67890", [prompt("t1", "typed", NEUTRAL_SCOPE), prompt("t3", "typed", LAUNCH12)])
    (d / f"{SID}-session.jsonl").unlink()
    assert REC.main(["--session", "def67890", "--key", "12", "--act", "launch", "--line", LAUNCH12],
                    records=f, projects_dir=d) == 0
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]
    handwritten_launch(f, "13", NEUTRAL_SCOPE, "def67890")
    assert not A.check("13", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("launch_first", [False, True])
@pytest.mark.parametrize("other_session", [False, True])
@pytest.mark.parametrize("candidate_time", ["t1", "t3"])
def test_c32_every_scope_quote_match_is_tainted_even_beyond_the_pin(tmp_path, launch_first,
                                                                   other_session, candidate_time):
    quote = "GO supervisor - batches 12 and 13 for example-core"
    later = quote + ": what is the status? do not launch yet"
    rows = [prompt("t2", "typed", later)]
    if not other_session and candidate_time == "t1":
        rows.insert(0, prompt(candidate_time, "typed", NEUTRAL_SCOPE))
    d = transcript(tmp_path, rows)
    sid = "def67890" if other_session else SID
    if other_session and candidate_time == "t1":
        write_session(d, sid, [prompt(candidate_time, "typed", NEUTRAL_SCOPE)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    f = records(tmp_path)
    if launch_first:
        handwritten_launch(f, "13", NEUTRAL_SCOPE, sid)
    assert REC.main(["--session", SID, "--key", "12", "--line", quote, "--packet", str(p),
                     "--scope-override", "example-core-aget=all"], records=f, projects_dir=d) == 0
    if candidate_time == "t3":  # a later repetition must not escape taint either
        write_session(d, sid, [*rows, prompt(candidate_time, "typed", NEUTRAL_SCOPE)])
    if not launch_first:
        handwritten_launch(f, "13", NEUTRAL_SCOPE, sid)
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why


@pytest.mark.parametrize("kind", ["missing-transcript", "invalid-pin"])
@pytest.mark.parametrize("generic", [False, True])
def test_c32_unverifiable_unrelated_scope_does_not_block_first_launch(tmp_path, kind, generic):
    line = "GO supervisor - launch batch 14 for example-core as prepared"
    d = transcript(tmp_path, [prompt("t3", "typed", line)])
    h = {"line": "GO supervisor - batch 5 scope override for other-aget to write docs/", "session": "aaaa1111",
         "batches_added": ["5"]}
    ov = {"batches": ["5"], "history": [h]}
    if kind == "invalid-pin":
        h["prompt"] = "invalid"
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-other-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    args = [] if generic else ["--act", "launch"]
    code, f = rec(tmp_path, d, "--key", "14", "--line", line, *args)
    assert code == 0
    ok, why = A.check("14", records=f, projects_dir=d, act="launch")
    assert ok, why
    # The same unverifiable entry must still fail closed for the batch it governs, and identify the history.
    doc = json.loads(f.read_text())
    doc["scope_overrides"]["example-other-aget"]["batches"] = ["14"]
    doc["scope_overrides"]["example-other-aget"]["history"][0]["batches_added"] = ["14"]
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check("14", records=f, projects_dir=d, act="launch")
    assert not ok and "example-other-aget" in why, why


@pytest.mark.parametrize("wording", [
    "scope overrides", "scope exceptions", "scope overridden", "scope‑override", "scоpe override",
    "over-ride the scope", "broader write scope", "expanded scope", "outside its write scope",
    "extend the write scope", "scope exception", "broaden the scope", "expand the write scope",
    "SCOPE  OVERRIDE", "scope\u00a0override", "scope override",
    "no scope override needed but expand the write scope",
])
def test_c32_common_scope_wording_refuses_in_recorder_and_gate(tmp_path, wording):
    line = f"GO supervisor - batches 12 and 13 for example-core: {wording}"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    f = records(tmp_path)
    handwritten_launch(f, "13", line)
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why
    f = records(tmp_path)
    assert REC.main(["--session", SID, "--key", "13", "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert json.loads(f.read_text())["batch_authority"] == {}


@pytest.mark.parametrize("wording", [
    "no scope override needed", "no wider scope", "do not override its write scope", "scope overrides none",
    "the override for batch 12 does not change this scope", "within the approved scope",
    "no scope exceptions", "without expanding the scope",
])
def test_c32_genuine_launch_can_mention_scope_in_passing(tmp_path, wording):
    line = f"GO supervisor - launch batch 13 for example-core as prepared; {wording}"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    code, f = rec(tmp_path, d, "--key", "13", "--act", "launch", "--line", line)
    assert code == 0
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert ok, why


@pytest.mark.parametrize("neutral", [False, True])
def test_c32_refused_launch_record_leaves_a_route_for_separate_authority(tmp_path, neutral):
    bad = NEUTRAL_SCOPE if neutral else OVERRIDE12.replace("batch 12", "batches 12 and 13")
    good = "GO supervisor - launch batch 13 for example-core as prepared, go ahead"
    d = transcript(tmp_path, [prompt("t1", "typed", bad), prompt("t2", "typed", good)])
    if neutral:
        p = packet(tmp_path, "example-core-aget", tmp_path)
        assert rec(tmp_path, d, "--key", "12", "--line", bad, "--packet", str(p),
                   "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "13", "--act", "launch", "--line", bad)
    assert code == 1
    assert "13:launch" not in json.loads(f.read_text())["batch_authority"]
    assert rec(tmp_path, d, "--key", "13", "--act", "launch", "--line", good)[0] == 0
    assert A.check("13", records=f, projects_dir=d, act="launch")[0]


def test_c32_distinct_launch_survives_scope_transcript_growth(tmp_path):
    d = transcript(tmp_path, [prompt("t1", "typed", NEUTRAL_SCOPE), prompt("t2", "typed", LAUNCH12)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert rec(tmp_path, d, "--key", "12", "--line", NEUTRAL_SCOPE, "--packet", str(p),
               "--scope-override", "example-core-aget=all")[0] == 0
    code, f = rec(tmp_path, d, "--key", "12", "--act", "launch", "--line", LAUNCH12)
    assert code == 0
    transcript(tmp_path, [prompt("t1", "typed", NEUTRAL_SCOPE), prompt("t2", "typed", LAUNCH12),
                          prompt("t3", "typed", NEUTRAL_SCOPE)])
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]


# v337prep:R6 / C19: legacy ledgers carry the principal quote in descriptive fields.
@pytest.mark.parametrize("field", ["source", "source_7t", "reason"])
@pytest.mark.parametrize("quotes", [('"', '"'), ('“', '”')])
@pytest.mark.parametrize("shape", ["no-history", "history-no-line", "mixed-history"])
def test_c32_legacy_source_quotes_taint_every_batch(tmp_path, field, quotes, shape):
    line = NEUTRAL_SCOPE
    d = transcript(tmp_path, [prompt("t1", "typed", line), prompt("t2", "typed", LAUNCH12)])
    source = f"principal, typed, session {SID}: {quotes[0]}{line}{quotes[1]}"
    ov = {"batches": ["12"], field: source}
    if shape != "no-history":
        ov = {"batches": ["12"], "history": [{"batches": ["12"], field: source}]}
        if shape == "mixed-history":
            ov["history"].insert(0, {"line": "GO supervisor - batch 12 docs may be written"})
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", "13", "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert f.read_bytes() == before
    # A short recorded launch line must not hide the rest of the matched prompt.
    handwritten_launch(f, "13", "GO supervisor - batches 12 and 13 for example-core", session="")
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "scope" in why, why


@pytest.mark.parametrize("field", ["source", "source_7t", "reason"])
def test_c32_old_format_quotes_require_removal_before_a_separate_launch(tmp_path, field):
    first = "GO supervisor - batch 12 for example-core: docs may be written"
    second = NEUTRAL_SCOPE
    d = transcript(tmp_path, [prompt("t1", "typed", first), prompt("t2", "typed", second),
                              prompt("t3", "typed", LAUNCH12)])
    ov = {"batches": ["12"], field:
          f'principal, typed, session {SID}: "{first}"; principal, typed, session {SID}: “{second}”'}
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    handwritten_launch(f, "13", second)
    assert not A.check("13", records=f, projects_dir=d, act="launch")[0]
    assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", LAUNCH12],
                    records=f, projects_dir=d) == 1
    handwritten_launch(f, "12", LAUNCH12)
    assert not A.check("12", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("field", ["source", "source_7t", "reason"])
@pytest.mark.parametrize("in_history", [False, True])
def test_c32_unquoted_old_format_free_text_blocks_even_separate_prompts(tmp_path, field, in_history):
    note = "example-core docs may be written under reviewed terms"
    line = f"GO supervisor - launch batch 13; {note.replace(' ', '  ')}"
    separate = "GO supervisor - launch batches 12 and 13 for example-core as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", line), prompt("t2", "typed", separate)])
    ov = {"batches": ["12"], field: note}
    if in_history:
        ov = {"batches": ["12"], "history": [{field: note}]}
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", "13", "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert f.read_bytes() == before
    handwritten_launch(f, "13", line)
    ok, why = A.check("13", records=f, projects_dir=d, act="launch")
    assert not ok and "ask the principal to confirm" in why, why
    handwritten_launch(f, "13", separate)
    assert not A.check("13", records=f, projects_dir=d, act="launch")[0]
    handwritten_launch(f, "12", separate)
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert not ok and "ask the principal to confirm" in why, why


def test_c32_current_scope_quote_uses_word_boundaries(tmp_path):
    quote = "GO supervisor - example-core writes docs/ too, batch 1"
    launch = quote + "2, launch as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", quote), prompt("t2", "typed", launch)])
    ov = {"batches": ["1"], "history": [{"line": quote, "batches_added": ["1"]}]}
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", launch],
                    records=f, projects_dir=d) == 0
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("wording", [
    "expand the write scopes", "extend its write scopes", "widen the scope", "scope expansion",
    "scope is extended", "override write_scope", "beyond its write scope", "expand example-core write scope",
    "scope extension", "widened scope", "scope widened", "exception to the write scope",
    "add docs/ to its write scope", "expanded write-scopes",
    "no need for a scope override, but widen the scope", "scope overrides: none; scope is extended",
    "the scope exception from batch 12 does not apply, grant a scope override",
])
def test_c32_review_scope_grants_refuse_in_recorder_and_gate(tmp_path, wording):
    test_c32_common_scope_wording_refuses_in_recorder_and_gate(tmp_path, wording)


@pytest.mark.parametrize("wording", [
    "the docs bug is outside the scope of this batch", "scope overrides: none", "no need for a scope override",
    "I do not need a scope override", "not granting any scope override", "do not write outside the scope",
    "the scope override from batch 12 does not apply", "the scope exception from batch 12 does not apply",
    "scope override: none", "scope overrides: not needed", "launch with zero scope overrides",
    "the wider scope for batch 12 stays closed", "we discussed the write scope earlier",
    "approve batch 13 list abc12345 and launch it, scope as packet", "launch within the write scope",
])
def test_c32_review_incidental_scope_mentions_pass_in_recorder_and_gate(tmp_path, wording):
    test_c32_genuine_launch_can_mention_scope_in_passing(tmp_path, wording)


@pytest.mark.parametrize("bad_position", ["before", "between", "after"])
def test_c32_invalid_utf8_refuses_with_reason_but_keeps_other_lines(tmp_path, bad_position, capsys):
    import check_principal_line as C
    d = transcript(tmp_path, [prompt("t1", "typed", LAUNCH12), prompt("t2", "typed", NEUTRAL_SCOPE)])
    path = d / f"{SID}-session.jsonl"
    rows = path.read_bytes().splitlines(keepends=True)
    rows.insert({"before": 0, "between": 2, "after": len(rows)}[bad_position], b"\xff\n")
    path.write_bytes(b"".join(rows))
    # The scope scan must retain the valid prompts on both sides of the damaged row.
    assert [p[2] for p in C.prompts(path)][-2:] == [LAUNCH12, NEUTRAL_SCOPE]
    f = records(tmp_path, {"12:launch": entry(LAUNCH12)})
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert not ok and "UTF-8" in why and "line" in why, why
    f = records(tmp_path)
    assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", LAUNCH12],
                    records=f, projects_dir=d) == 1
    assert "UTF-8" in capsys.readouterr().out
    assert json.loads(f.read_text())["batch_authority"] == {}


def test_c32_legacy_quotes_in_all_fields_and_levels_are_independent_evidence(tmp_path):
    lines = [NEUTRAL_SCOPE + f", terms {i}" for i in range(6)]
    d = transcript(tmp_path, [prompt(f"t{i}", "typed", line) for i, line in enumerate(lines)])
    ov = {"batches": ["12"], "history": [{}]}
    for i, (row, field) in enumerate((row, field) for row in (ov, ov["history"][0])
                                    for field in ("source", "source_7t", "reason")):
        row[field] = f'principal, typed, session {SID} (recorded by record_authority.py): "{lines[i]}"'
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": ov}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    for line in lines:
        handwritten_launch(f, "13", line)
        ok, why = A.check("13", records=f, projects_dir=d, act="launch")
        assert not ok and "scope" in why, why


def test_c32_recovered_scope_pin_survives_invalid_utf8_in_another_session(tmp_path):
    d = transcript(tmp_path, [prompt("t1", "typed", NEUTRAL_SCOPE)])
    p = packet(tmp_path, "example-core-aget", tmp_path)
    code, f = rec(tmp_path, d, "--key", "12", "--line", NEUTRAL_SCOPE, "--packet", str(p),
                  "--scope-override", "example-core-aget=all")
    assert code == 0
    path = d / f"{SID}-session.jsonl"
    rows = path.read_bytes().splitlines(keepends=True)
    path.write_bytes(rows[0] + b"\xff\n" + b"".join(rows[1:]))
    write_session(d, "def67890", [prompt("t2", "typed", LAUNCH12)])
    assert REC.main(["--session", "def67890", "--key", "12", "--act", "launch", "--line", LAUNCH12],
                    records=f, projects_dir=d) == 0
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("quote,text,expected", [
    ("batch 1", "batch 12", False), ("batch 1", "batch 1t", False),
    ("batch 1", "batch 1, launch", True), ("docs may", "Docs may", False),
    ("docs may", "docs  \n may be written", True), ("docs may", "docs maybe", False),
    ("docs may", "xdocs may", False), ("docs may", "docs", False), ("", "anything", False),
    ('docs "may" be written', 'reviewed: docs "may" be written', True),
])
def test_c32_current_quote_matching_rule(quote, text, expected):
    assert A.contains_scope_text(quote, text) == expected
