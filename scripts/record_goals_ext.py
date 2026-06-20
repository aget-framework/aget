#!/usr/bin/env python3
"""
record_goals_ext.py — structural close of /aget-propose-goals C2 (E1).

C2 ("session-file recording is mandatory") shipped as *advisory* agent-discipline:
SKILL.md says "record the scored set", but nothing made the recording checkable, so
the skill's own anti-decorative guard was itself decorative-until-compliance
(L605/L671 — recording without consequence). This helper makes the recording a
*structural* surface:

  - record_goals()    appends a machine-parseable PROPOSE-GOALS-RECORD block to the
                      current session file (one block per scored candidate set).
  - verify_recorded() is the NEGATIVE CONTROL: given a session file in which a goal
                      set was presented, it returns recorded=False when no block
                      exists — i.e. the check BITES. A session-protocol verifier (or
                      a retrospective) can now fail on a rubric-free / record-free
                      pivot instead of merely trusting the prose.

Instance_Artifact (scripts/*_ext.py, R-TAS-001-05). Best-effort, like
record_invocation.py: a recording failure exits 1 with a warning and MUST NOT abort
the calling skill (the skill still presented the scored set to the principal).

Coordination: shares the "recording≠enforcing" family with
PROJECT_PLAN_self_oversight_structural_enforcement (D71-routing guard). Distinct
trigger (goal-set recording, not governed-route bypass) — no duplication.

See: SKILL-055 (aget-propose-goals) C2/C-PG-002; L1090 (SOP↔skill fold); L605/L671.

Usage:
    # record a scored set into a session file
    python3 scripts/record_goals_ext.py --record --session sessions/session_X.md \
        --focus "v3.23 prep" --table-file /tmp/scored.md

    # verify a session file carries a goal record (negative control; exit 1 if absent)
    python3 scripts/record_goals_ext.py --verify --session sessions/session_X.md

    # self-test (round-trips record→verify + proves the negative control bites)
    python3 scripts/record_goals_ext.py --self-test
"""

import argparse
import sys
from pathlib import Path

START_MARKER = "<!-- PROPOSE-GOALS-RECORD:start -->"
END_MARKER = "<!-- PROPOSE-GOALS-RECORD:end -->"


def render_block(focus: str, scored_table: str) -> str:
    """Render a machine-parseable goal-record block. `scored_table` is the rendered
    markdown table (the SKILL.md Output Format table, including the Commit column)."""
    focus = (focus or "").strip() or "(unspecified)"
    scored_table = (scored_table or "").strip()
    return (
        f"\n{START_MARKER}\n"
        f"### propose-goals scored candidate set\n"
        f"**Focus**: {focus}\n\n"
        f"{scored_table}\n"
        f"{END_MARKER}\n"
    )


def record_goals(session_file, focus: str, scored_table: str) -> bool:
    """Append a goal-record block to the session file. Returns True on success.
    Best-effort: returns False (does not raise) on IO failure."""
    p = Path(session_file)
    try:
        block = render_block(focus, scored_table)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(block)
        return True
    except OSError as exc:  # best-effort, must not abort the calling skill
        sys.stderr.write(f"warning: record_goals append failed: {exc}\n")
        return False


def verify_recorded(text: str) -> dict:
    """NEGATIVE CONTROL. Given session-file text, report whether a well-formed
    goal-record block is present. recorded=False is the structural bite: a session
    that presented a goal set but did not record it fails this check."""
    has_start = START_MARKER in text
    has_end = END_MARKER in text
    # well-formed = start precedes end (a lone marker is not a valid record)
    well_formed = has_start and has_end and text.index(START_MARKER) < text.index(END_MARKER)
    return {
        "recorded": well_formed,
        "has_start_marker": has_start,
        "has_end_marker": has_end,
        "well_formed": well_formed,
    }


def verify_session_file(session_file) -> dict:
    p = Path(session_file)
    if not p.exists():
        return {"recorded": False, "error": f"session file not found: {session_file}"}
    return verify_recorded(p.read_text(encoding="utf-8"))


def self_test() -> int:
    """Round-trip + negative-control proof. Returns 0 on success, 1 on failure."""
    sample_table = (
        "| # | Goal (thrust) | Tag | Commit | D1 | D2 | D3 | D4 | D5 | Score | Dominant Dim |\n"
        "|---|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|\n"
        "| 1 | demo | principal | committed | 3 | 2 | 2 | 3 | 2 | 12 | D1 |\n"
    )

    # 1. negative control BITES: bare session text is not recorded
    bare = "# Session\n## Notes\n(no goals recorded)\n"
    neg = verify_recorded(bare)
    if neg["recorded"]:
        print("FAIL: negative control did not bite (bare text reported recorded)")
        return 1

    # 2. a lone start marker is NOT a valid record (well-formedness bites)
    lone = bare + START_MARKER + "\n"
    if verify_recorded(lone)["recorded"]:
        print("FAIL: lone start marker accepted as a record")
        return 1

    # 3. round-trip: render → verify reports recorded
    recorded_text = bare + render_block("self-test focus", sample_table)
    pos = verify_recorded(recorded_text)
    if not pos["recorded"]:
        print("FAIL: round-tripped block not detected as recorded")
        return 1

    print("PASS: record_goals_ext self-test (negative control bites; round-trip records)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Structural goal-set recording (E1, C2).")
    ap.add_argument("--record", action="store_true", help="append a goal-record block")
    ap.add_argument("--verify", action="store_true", help="verify a session file carries a record")
    ap.add_argument("--self-test", action="store_true", help="round-trip + negative-control proof")
    ap.add_argument("--session", help="path to the session file")
    ap.add_argument("--focus", default="", help="session focus restatement")
    ap.add_argument("--table-file", help="path to a file holding the rendered scored table")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.record:
        if not args.session:
            ap.error("--record requires --session")
        table = ""
        if args.table_file:
            table = Path(args.table_file).read_text(encoding="utf-8")
        ok = record_goals(args.session, args.focus, table)
        return 0 if ok else 1

    if args.verify:
        if not args.session:
            ap.error("--verify requires --session")
        result = verify_session_file(args.session)
        print(f"recorded={result['recorded']} {result}")
        return 0 if result.get("recorded") else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
