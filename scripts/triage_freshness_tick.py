#!/usr/bin/env python3
"""C-28-40 residue — the per-release rollup hook and the standing cadence tick.

WHAT THIS CLOSES
----------------
`GOAL-INBOX-MANAGED`'s loop, quoted rather than paraphrased (`v328-prelock:R15`,
as amended by `v328-shipday:R63` — this is a Goal loop, a normative surface):

    trigger=per-release + a standing N-day cadence tick (not only release windows)
    consequence=if any issue exceeds the triage-freshness SLO (N days untriaged)
                OR the cadence was missed, escalate to a dedicated triage session
                + flag in the release retrospective

`check_triage_freshness.py` answers "what is the distribution right now?". It cannot
answer either half of that consequence clause, because **both halves are about time
between runs** and the instrument keeps no record of having run. A rollup that leaves
no trace cannot detect its own absence — which is the L1191 shape the instrument's own
docstring was written against, one layer up: there, the *input* signal died unnoticed;
here, the *cadence* can lapse unnoticed.

So this module persists each rollup and reads back the gap.

WHY `scan()` MAKES NO NETWORK CALL
----------------------------------
It runs at wake-up, every session. `check_triage_freshness.py` costs several
`search/issues` calls against a 30/min budget shared with an unidentified concurrent
consumer (`v328-shipday:R55`). A surfacer that spends contended quota on every wake
would be a control that degrades the thing it monitors. `scan()` therefore reads only
the local ledger; `record` is the only mode that touches the API, and it fires on the
release hook or on demand.

THE SECOND VERB (added 2026-07-26)
---------------------------------
The loop's review clause has two verbs -- "run a triage pass (classify new/stale,
dedup, route) **+** emit a rollup" -- and the first version instrumented only the
second. A rollup faithfully recorded every fortnight, with no triage ever performed,
would have reported green forever. That is the same decorative-control shape (L671)
this module was built to remove, reintroduced one level in.

It is detectable without new data: **two consecutive rollups bracket an interval, and
a triage pass that happened has to show up as movement in that interval.** If untriaged
did not fall between two rollups, the queue was measured and not worked. Reported as
ROLLUP-WITHOUT-TRIAGE rather than inferred silently, because there is one honest
alternative reading -- inflow matched outflow -- and the tick cannot tell them apart.
It says so.

WHAT THIS STILL DOES *NOT* CLOSE (stated, not hidden)
-----------------------------------------------------
- Movement is evidence of *activity*, not of *quality*. A pass that mislabels 40 issues
  moves the number and satisfies this check.
- With inflow > outflow, a real triage pass can still leave untriaged flat or rising.
  The flag is a prompt to look, never a verdict.
- N is **not ratified** (`v328-shipday:R47`: the SLO is set after the drain, on real
  data). Both windows below are reporting defaults and say so in every output.

Exit 0 = cadence met and SLO not breached | 1 = cadence missed or SLO breached
       | 2 = never recorded / cannot read
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / ".aget" / "logs" / "triage_rollup.jsonl"
DRAIN_LEDGER = ROOT / ".aget" / "logs" / "issue_drain_ledger.jsonl"

# Reporting defaults. NEITHER is ratified — v328-shipday:R47 defers ratification
# until the post-drain arrival rate is measurable. Kept separate on purpose: the
# SLO window is "how long may an issue sit untriaged", the cadence window is "how
# long may the agent go without looking". Collapsing them would hide a lapse.
DEFAULT_CADENCE_DAYS = 14
SLO_UNRATIFIED_NOTE = "unratified (v328-shipday:R47 — ratify post-drain, on real data)"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _read_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a malformed row must not blind the tick
    return rows


def _drain_has_run() -> bool:
    """True once the C-28-41 baseline drain has written anything.

    This is the `v328-shipday:R47` ratification trigger, made structural: the Batch-12
    owed surface records that "no artifact says who re-opens the SLO question
    post-drain, or when". The answer is now: this tick does, on the first wake after
    the drain writes its first ledger row.
    """
    if not DRAIN_LEDGER.exists():
        return False
    return any(l.strip() for l in DRAIN_LEDGER.read_text().splitlines())


def record(slo_days: int = DEFAULT_CADENCE_DAYS, trigger: str = "manual") -> dict:
    """Run the instrument and append a rollup row. The only mode that spends quota."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_triage_freshness.py"),
         "--json", "--slo-days", str(slo_days)],
        capture_output=True, text=True,
    )
    if proc.returncode == 2 or not proc.stdout.strip():
        raise RuntimeError(f"instrument could not measure: {proc.stderr.strip()[:200]}")
    data = json.loads(proc.stdout)
    row = {
        "recorded_at": _now().isoformat(),
        "trigger": trigger,
        "open_total": data.get("open_total"),
        "untriaged": data.get("untriaged"),
        "breaching": data.get("breaching"),
        "slo_days": data.get("slo_days"),
        "slo_is_ratified": data.get("slo_is_ratified", False),
        "signal_alive": data.get("signal_alive"),
        "distribution": data.get("distribution"),
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def scan(cadence_days: int = DEFAULT_CADENCE_DAYS) -> dict:
    """Local-only read. Returns the tick's state; never calls the network."""
    rows = _read_ledger()
    ratification_due = _drain_has_run() and not (rows and rows[-1].get("slo_is_ratified"))
    if not rows:
        return {"state": "never-recorded", "cadence_days": cadence_days,
                "days_since": None, "cadence_missed": True, "slo_breached": None,
                "last": None, "ratification_due": ratification_due}
    last = rows[-1]
    try:
        when = datetime.fromisoformat(last["recorded_at"])
    except (KeyError, ValueError):
        return {"state": "unreadable", "cadence_days": cadence_days,
                "days_since": None, "cadence_missed": True, "slo_breached": None,
                "last": last, "ratification_due": ratification_due}
    days = (_now() - when).total_seconds() / 86400.0
    breaching = last.get("breaching")

    # Second verb. Two rollups bracket an interval; a triage pass that happened has
    # to show as movement in it. None = insufficient history, which is NOT a pass.
    pass_evidenced: bool | None = None
    delta = None
    if len(rows) >= 2:
        prev_u, last_u = rows[-2].get("untriaged"), last.get("untriaged")
        if isinstance(prev_u, int) and isinstance(last_u, int):
            delta = last_u - prev_u
            pass_evidenced = delta < 0

    return {
        "state": "ok",
        "cadence_days": cadence_days,
        "days_since": round(days, 1),
        "cadence_missed": days > cadence_days,
        "slo_breached": bool(breaching) if breaching is not None else None,
        "pass_evidenced": pass_evidenced,
        "untriaged_delta": delta,
        "last": last,
        "ratification_due": ratification_due,
    }


def format_line(st: dict) -> str:
    """One principal-facing line for wake-up. Empty string when nothing is owed."""
    if st["state"] == "never-recorded":
        return ("⚠ Triage-freshness rollup: NEVER RECORDED — GOAL-INBOX-MANAGED's "
                "cadence tick has no baseline (`python3 scripts/triage_freshness_tick.py record`)")
    if st["state"] == "unreadable":
        return "⚠ Triage-freshness rollup: ledger unreadable — cadence cannot be evidenced"

    last, bits = st["last"], []
    if st["cadence_missed"]:
        bits.append(f"CADENCE MISSED ({st['days_since']}d > {st['cadence_days']}d)")
    if st["slo_breached"]:
        bits.append(f"SLO BREACHED ({last.get('breaching')} issues)")
    if last.get("signal_alive") is False:
        bits.append("TRIAGE SIGNAL DEAD")
    if st["ratification_due"]:
        bits.append("SLO RATIFICATION DUE (drain has written; R47 trigger fired)")
    if st.get("pass_evidenced") is False:
        bits.append(f"ROLLUP WITHOUT TRIAGE (untriaged {st['untriaged_delta']:+d} since "
                    f"last rollup — measured, not worked; or inflow matched outflow)")
    if not bits:
        return ""
    return (f"⚠ Triage freshness [{'; '.join(bits)}] — untriaged "
            f"{last.get('untriaged')}/{last.get('open_total')}, "
            f"N={last.get('slo_days')} {SLO_UNRATIFIED_NOTE}. "
            f"Consequence per GOAL-INBOX-MANAGED: dedicated triage session + "
            f"flag in the release retrospective")


def _self_test() -> int:
    """Falsifiers. Each asserts the check FAILS when it should, not only that it passes."""
    import tempfile, unittest.mock as mock
    ok = fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        if cond:
            ok += 1
            print(f"  PASS  {name}")
        else:
            fail += 1
            print(f"  FAIL  {name}")

    with tempfile.TemporaryDirectory() as td:
        led, drain = Path(td) / "r.jsonl", Path(td) / "d.jsonl"
        with mock.patch.object(sys.modules[__name__], "LEDGER", led), \
             mock.patch.object(sys.modules[__name__], "DRAIN_LEDGER", drain):

            chk("empty ledger -> never-recorded + cadence_missed",
                scan()["state"] == "never-recorded" and scan()["cadence_missed"])
            chk("never-recorded surfaces a line", format_line(scan()) != "")

            fresh = (_now() - timedelta(days=1)).isoformat()
            led.write_text(json.dumps({"recorded_at": fresh, "breaching": 0,
                                       "untriaged": 402, "open_total": 1781,
                                       "slo_days": 14, "signal_alive": True}) + "\n")
            chk("fresh clean row -> cadence met", scan()["cadence_missed"] is False)
            chk("fresh clean row -> SILENT at wake-up", format_line(scan()) == "")

            # FALSIFIER 1: age the row past the window; the check must flip.
            old = (_now() - timedelta(days=30)).isoformat()
            led.write_text(json.dumps({"recorded_at": old, "breaching": 0,
                                       "untriaged": 402, "open_total": 1781,
                                       "slo_days": 14, "signal_alive": True}) + "\n")
            chk("FALSIFIER stale row -> cadence_missed", scan()["cadence_missed"] is True)
            chk("FALSIFIER stale row -> line names CADENCE MISSED",
                "CADENCE MISSED" in format_line(scan()))

            # FALSIFIER 2: breach with a fresh cadence — the two must be independent.
            led.write_text(json.dumps({"recorded_at": fresh, "breaching": 7,
                                       "untriaged": 402, "open_total": 1781,
                                       "slo_days": 14, "signal_alive": True}) + "\n")
            s = scan()
            chk("FALSIFIER breach+fresh -> SLO flagged, cadence NOT",
                s["slo_breached"] is True and s["cadence_missed"] is False)

            # FALSIFIER 3: dead input signal must surface even when all else is green.
            led.write_text(json.dumps({"recorded_at": fresh, "breaching": 0,
                                       "untriaged": 402, "open_total": 1781,
                                       "slo_days": 14, "signal_alive": False}) + "\n")
            chk("FALSIFIER dead signal -> surfaced (L1191)",
                "TRIAGE SIGNAL DEAD" in format_line(scan()))

            # FALSIFIER 4: R47 ratification trigger fires only once the drain writes.
            led.write_text(json.dumps({"recorded_at": fresh, "breaching": 0,
                                       "untriaged": 402, "open_total": 1781, "slo_days": 14,
                                       "slo_is_ratified": False, "signal_alive": True}) + "\n")
            chk("no drain rows -> ratification NOT due", scan()["ratification_due"] is False)
            drain.write_text(json.dumps({"issue": 123, "row": 9}) + "\n")
            chk("FALSIFIER drain wrote -> ratification DUE", scan()["ratification_due"] is True)
            chk("FALSIFIER ratification surfaces at wake-up",
                "RATIFICATION DUE" in format_line(scan()))

            # FALSIFIER 6: the second verb. One row cannot evidence a pass; two flat
            # rows must flag; two falling rows must not.
            # Drain ledger cleared first: FALSIFIER 4 above wrote to it, and a leaked
            # ratification_due would make the silence assertion below fail for an
            # unrelated reason. Order-dependence between assertions is a test defect.
            drain.write_text("")

            def _two(u_prev, u_last):
                led.write_text("\n".join(json.dumps(
                    {"recorded_at": fresh, "breaching": 0, "untriaged": u,
                     "open_total": 1781, "slo_days": 14, "signal_alive": True})
                    for u in (u_prev, u_last)) + "\n")

            led.write_text(json.dumps({"recorded_at": fresh, "breaching": 0,
                                       "untriaged": 402, "open_total": 1781,
                                       "slo_days": 14, "signal_alive": True}) + "\n")
            chk("single row -> pass NOT evidenced (absence, not success)",
                scan()["pass_evidenced"] is None)
            _two(402, 402)
            chk("FALSIFIER two flat rows -> ROLLUP WITHOUT TRIAGE",
                scan()["pass_evidenced"] is False
                and "ROLLUP WITHOUT TRIAGE" in format_line(scan()))
            _two(402, 430)
            chk("FALSIFIER untriaged ROSE -> still flagged", scan()["pass_evidenced"] is False)
            _two(402, 350)
            chk("two falling rows -> pass evidenced, silent",
                scan()["pass_evidenced"] is True and format_line(scan()) == "")

            # FALSIFIER 5: a malformed row must not blind the tick.
            led.write_text("{not json\n" + json.dumps(
                {"recorded_at": fresh, "breaching": 0, "untriaged": 1,
                 "open_total": 2, "slo_days": 14, "signal_alive": True}) + "\n")
            chk("FALSIFIER malformed row skipped, not fatal", scan()["state"] == "ok")

    print(f"\n{ok} passed, {fail} failed")
    return 0 if fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", nargs="?", default="check",
                    choices=["check", "record", "self-test"])
    ap.add_argument("--cadence-days", type=int, default=DEFAULT_CADENCE_DAYS)
    ap.add_argument("--slo-days", type=int, default=DEFAULT_CADENCE_DAYS)
    ap.add_argument("--trigger", default="manual",
                    help="what fired this rollup (e.g. 'release', 'cadence')")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.mode == "self-test":
        return _self_test()

    if a.mode == "record":
        try:
            row = record(slo_days=a.slo_days, trigger=a.trigger)
        except Exception as exc:  # network/quota/instrument failure
            print(f"❌ rollup NOT recorded: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(row, indent=2) if a.json else
              f"✅ rollup recorded ({a.trigger}): untriaged {row['untriaged']}/"
              f"{row['open_total']}, breaching {row['breaching']}, "
              f"N={row['slo_days']} {SLO_UNRATIFIED_NOTE}")
        return 0

    st = scan(cadence_days=a.cadence_days)
    if a.json:
        print(json.dumps(st, indent=2, default=str))
    else:
        line = format_line(st)
        print(line if line else
              f"✅ triage-freshness cadence met ({st['days_since']}d ≤ "
              f"{st['cadence_days']}d), SLO not breached")
    if st["state"] in ("never-recorded", "unreadable"):
        return 2
    return 1 if (st["cadence_missed"] or st["slo_breached"] or st["ratification_due"]) else 0


if __name__ == "__main__":
    sys.exit(main())
