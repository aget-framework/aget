"""Tests for check_principal_line.py (the principal's `typedonly` ruling, 2026-09-29). Hermetic fixtures only."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_principal_line", ROOT / "scripts/migration_kit/check_principal_line.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


# R-F1: a session's first prompt is the launch position and never counts as typed authority, so every fixture
# session starts with a neutral prompt, as a real session does before any principal line.
SESSION_START = {"type": "user", "timestamp": "0", "promptSource": "typed", "message": {"content": "session start"}}

def write(tmp_path, rows):
    f = tmp_path / "abc123-session.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in [SESSION_START, *rows]) + "\n")
    return tmp_path


def prompt(ts, source, text, **extra):
    return {"type": "user", "timestamp": ts, "promptSource": source, "message": {"content": text}, **extra}


def run(d, needle):
    return C.main(["--session", "abc123", "--contains", needle, "--projects-dir", str(d)])


def test_a_typed_line_passes_and_an_accepted_suggestion_does_not(tmp_path):
    d = write(tmp_path, [prompt("2026-09-29T07:04:34Z", "typed", "proceed with recommendations"),
                         prompt("2026-09-29T06:48:13Z", "suggestion_accepted", "yes, fix the approval check first")])
    assert run(d, "proceed with recommendations") == 0
    assert run(d, "fix the approval check") == 1          # the 2026-09-28 finding: accepted suggestions read as rulings


def test_the_newest_matching_line_decides(tmp_path):
    """A suggestion accepted after a typed line is what the principal last did with that text."""
    d = write(tmp_path, [prompt("2026-09-29T01:00:00Z", "typed", "approve push batch-8"),
                         prompt("2026-09-29T02:00:00Z", "suggestion_accepted", "approve push batch-8")])
    assert run(d, "approve push batch-8") == 1


def test_no_match_meta_rows_and_missing_source_are_not_typed(tmp_path):
    d = write(tmp_path, [prompt("t1", "typed", "approve list batch-8 c69fe0cf", isMeta=True),
                         prompt("t2", None, "confirm batch-8-launch"),
                         {"type": "assistant", "message": {"content": "approve push batch-8"}}])
    assert run(d, "approve list batch-8 c69fe0cf") == 2       # only a meta row carries it
    assert run(d, "confirm batch-8-launch") == 1              # no promptSource recorded: not typed
    assert run(d, "approve push batch-8") == 2                # the assistant's own text is never a principal line


def test_an_ambiguous_or_missing_session_is_refused(tmp_path):
    assert run(tmp_path, "x") == 2
    (tmp_path / "abc123-a.jsonl").write_text("")
    (tmp_path / "abc123-b.jsonl").write_text("")
    assert run(tmp_path, "x") == 2


def queued(ts, text, kind="human"):
    return {"type": "attachment", "timestamp": ts,
            "attachment": {"type": "queued_command", "prompt": text, "origin": {"kind": kind}, "timestamp": ts}}


def test_a_pasted_quote_of_a_proposed_line_is_not_the_line(tmp_path):
    """2026-09-29: the principal pasted the framework Aget's message, which QUOTED a suggested ruling, for review; the
    checker read it as the typed ruling. Text inside <pasted_content> no longer matches."""
    paste = ('write G1 more formally. <pasted_content id="p1">Type these: predicatefix; approve push batch-8'
             '</pasted_content id="p1">')
    d = write(tmp_path, [prompt("2026-09-29T17:07:11Z", "typed", paste)])
    assert run(d, "predicatefix; approve push batch-8") == 2
    assert run(d, "write G1 more formally") == 0                  # the principal's own words around it still count


def test_an_entry_that_is_only_a_paste_is_the_principals_line(tmp_path):
    """2026-09-29 13:06: the batch 9t approval arrived as a paste and nothing else; stripping it (the quote rule) made
    the principal's own line unreadable. A paste alone is the line; a paste inside other words stays a quote."""
    alone = '<pasted_content id="p">\n  approve list batch-9t ec14c17f305a; approve push batch-9t\n</pasted_content id="p">'
    d = write(tmp_path, [queued("2026-09-29T20:06:00Z", alone),
                         prompt("2026-09-29T17:07:11Z", "typed",
                                'write G1 <pasted_content id="q">predicatefix; approve push</pasted_content id="q">')])
    assert run(d, "approve list batch-9t ec14c17f305a") == 4          # found, as a mid-turn human entry
    assert run(d, "predicatefix; approve push") == 2                   # still a quote


def test_a_mid_turn_human_entry_is_found_and_reported_distinctly(tmp_path):
    """A line sent while the agent works is recorded as a queued command (origin human, no promptSource): found, with
    wrapped whitespace normalised, and reported as exit 4 rather than typed. A non-human origin is never a line."""
    d = write(tmp_path, [queued("2026-09-29T17:13:04Z", "predicatefix; approve push batch-8 of 76f19247\n     plus x"),
                         queued("2026-09-29T17:14:00Z", "approve list batch-9 abc", kind="task-notification")])
    assert run(d, "predicatefix; approve push batch-8 of 76f19247 plus x") == 4
    assert run(d, "approve list batch-9 abc") == 2
