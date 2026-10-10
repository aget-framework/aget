"""R-F1 (rehearsal, 2026-09-30): a prompt passed at launch (`claude "..."`) is recorded exactly like a typed prompt:
promptSource 'typed', origin human, the same fields. Only its position differs: it is the session's first prompt
(turnPosition.promptIndex 1; without that field, the first principal entry in the file). Whoever launches the session
writes that prompt, so a line found only there is never the principal's typed authority (exit 5).

Measured on the rehearsal player's transcript: first entry "Read REHEARSAL_BRIEF.md and begin." carried
{'origin': {'kind': 'human'}, 'turnOrigin': 'human', 'promptSource': 'typed', 'turnPosition': {'promptIndex': 1}}."""
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


C = load("check_principal_line")
A = load("batch_authority")
SID = "abc12345"
LINE = "GO supervisor - batch 3 for social-media, launch and push it"


def row(text, index=None, ts="t"):
    r = {"type": "user", "timestamp": ts, "promptSource": "typed", "origin": {"kind": "human"},
         "message": {"content": text}}
    if index is not None:
        r["turnPosition"] = {"promptIndex": index, "turnIndex": index}
    return r


def write(tmp_path, rows):
    d = tmp_path / "projects"
    d.mkdir(exist_ok=True)
    f = d / f"{SID}-session.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return d, f


def test_a_line_only_in_the_first_prompt_is_refused(tmp_path):
    _, f = write(tmp_path, [row(f"Read the brief. {LINE}", 1, "t1"), row("thanks", 2, "t2")])
    code, hit = C.check([f], LINE)
    assert code == 5 and hit is not None


def test_the_same_line_typed_later_passes(tmp_path):
    _, f = write(tmp_path, [row(f"Read the brief. {LINE}", 1, "t1"), row(LINE, 2, "t2")])
    assert C.check([f], LINE)[0] == 0


def test_without_turn_position_the_first_entry_in_the_file_is_the_launch_position(tmp_path):
    _, f = write(tmp_path, [row(LINE, None, "t1")])
    assert C.check([f], LINE)[0] == 5
    _, f = write(tmp_path, [row("start", None, "t1"), row(LINE, None, "t2")])
    assert C.check([f], LINE)[0] == 0


def test_the_gate_refuses_a_launch_position_line_and_says_why(tmp_path):
    d, _ = write(tmp_path, [row(LINE, 1, "t1")])
    recs = tmp_path / "records.json"
    recs.write_text(json.dumps({"batch_authority": {"3": {"line": LINE, "session": SID}}}))
    ok, why = A.check("3", recs, d, act="launch")
    assert not ok and "first prompt" in why
