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
