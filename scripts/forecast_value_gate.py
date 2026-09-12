#!/usr/bin/env python3
"""Forecast the scope-lock value gate without running it.

WHY THIS EXISTS
---------------
`validate_scope_lock_controls.py` is a VALIDATOR, not a forecaster. It:

*(That script and the readiness study behind this note live in the private framework-manager seat and
do not ship here. The properties below are therefore stated so a reader can check them against
whatever validator their own seat runs, rather than taken on a citation they cannot follow.)*

  * has no dry-run/forecast flag;
  * raises `ValidationError` before ever reaching the value constraints -- on cap, ceiling,
    pool-flag or unresolved evidence -- so a packet with any of those never gets scored at all.
    (It does NOT abort at the first *value* constraint: it computes all four and raises once
    with the complete list. An earlier version of this docstring said otherwise and was wrong.)
  * raises when `cap_su` is absent or non-positive;
  * raises when selected SU exceeds `cap_su`;
  * raises when `pool_allows_two_l3` disagrees with the packet's own L3 count;
  * resolves CON-EVIDENCE against the filesystem, so a hypothetical slate cannot be scored.

Consequence, recorded at source: every forecast the scope-lock SOP asks for had to be
HAND-DERIVED from the validator's published predicates, and R9's forecast therefore covered
two of the four binding constraints. This command is the supported route that was missing.

WHAT IT DOES
------------
Reads the validator's own selection packet -- including its candidate schema, in which a row
carries `initiative_path` and NOT a `class` field, and the packet carries no `initiative` block.
Class is resolved the way the validator resolves it: from the initiative file named by
`initiative_path`. An inline `class`, or a top-level `initiative` map, is accepted as a
convenience for hypothetical slates that have no initiative files yet.

Reports EVERY limb with a typed outcome, never aborting at the first failure:

  PASS         the limb fired and is satisfied
  FAIL         the limb fired and is not satisfied
  INERT        the limb did not fire (its firing precondition is absent)
  UNAVAILABLE  the limb's input is absent or unresolvable, so it CANNOT be scored

UNAVAILABLE is the load-bearing state. An unscoreable limb reported as PASS is the exact
failure this rubric exists to prevent, so UNAVAILABLE never folds into PASS and never folds
into FAIL either -- it is reported as its own outcome and it blocks certification (exit 2).

EVIDENCE SEMANTICS
------------------
CON-EVIDENCE checks whether evidence RESOLVES, not whether a source field is present.
Per row, three distinct states:

  RESOLVED     source.path is readable AND source.pattern occurs in its text
  UNRESOLVED   source.path is readable AND source.pattern does NOT occur  -> FAIL
  UNAVAILABLE  no source locators, or source.path is missing/unreadable   -> UNAVAILABLE

Equating "a source string is present" with "evidence is accepted" is the specific defect this
implementation exists to avoid: a hypothetical slate has locators that do not resolve yet, and
that is a thing not-yet-knowable, not a thing satisfied.

NON-MUTATING
------------
Read-only by construction: no writes, no network, no subprocess. Safe to run against a
candidate pool at any point before the ceremony.

USAGE
-----
  # forecast one packet
  python3 scripts/forecast_value_gate.py --packet selection.json

  # supply or override the cap when the packet has none
  python3 scripts/forecast_value_gate.py --packet selection.json --cap 68

  # resolve evidence against a repository other than the cwd
  python3 scripts/forecast_value_gate.py --packet selection.json --repo-root /path/to/repo

  # compare a pre-lock forecast against the actual locked selection
  python3 scripts/forecast_value_gate.py --packet prelock.json --compare-locked locked.json

  # machine-readable
  python3 scripts/forecast_value_gate.py --packet selection.json --json

EXIT CODES
----------
  0  every firing limb PASS, nothing UNAVAILABLE, and -- when --compare-locked is supplied --
     the forecast agreed with the actual locked selection on every limb
  1  at least one firing limb FAIL, or the forecast DISAGREED with the locked selection
  2  no FAIL, but at least one limb UNAVAILABLE -- forecast cannot certify
  3  the packet itself could not be read or is malformed

Version-independent: no cycle, cap, or version string is hardcoded. The cap comes from the
packet or `--cap`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Mirrors validate_scope_lock_controls.py:1025-1026 EXACTLY, including its asymmetry:
# CON-FLOOR compares against a literal 0.33, CON-CAPABILITY-SHARE against 1/3. Using 1/3 for
# both made this forecast disagree with the gate in [33.00%, 33.33%) -- wrong in precisely the
# band it exists to predict. If the validator's asymmetry is itself a defect, it is fixed there
# and mirrored here, never diverged from silently.
# Thresholds are RUBRIC_release_value_cost's, restated here because that rubric is a private
# seat artifact and does not ship with this script. Stated explicitly so a public reader can see
# the numbers rather than chase a citation that resolves nowhere in this tree.
FLOOR_FUNCTIONAL = 0.33     # CON-FLOOR functional share
FLOOR_CAPABILITY = 1 / 3    # CON-CAPABILITY-SHARE
AMBITION_FILL = 0.60

PASS, FAIL, INERT, UNAVAILABLE = "PASS", "FAIL", "INERT", "UNAVAILABLE"


class PacketError(Exception):
    """The packet could not be read or is structurally unusable."""


def bind_emission_contract(limbs: dict[str, dict[str, Any]], subject: str) -> None:
    """Attach the ruled four limbs to each independently emitted proposition."""
    for name, limb in limbs.items():
        state = limb["verdict"]
        indefinite = state in {UNAVAILABLE, INERT}
        why = limb.get("why")
        evidence = {k: v for k, v in limb.items() if k not in {"verdict", "why", "contract", "limit"}}
        limb["contract"] = {
            "subject": f"{subject}:{name}",
            "subject_bound": True,
            "subject_reached": not indefinite,
            "affirming_evidence": evidence if not indefinite else None,
            "predicate_discriminating": not indefinite,
            "definite": not indefinite,
        }
        if indefinite:
            limb["limit"] = why or f"predicate for {name} did not fire"


def _pct(num: float, den: float) -> float:
    return 0.0 if den == 0 else num / den * 100.0


def load_packet(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise PacketError(f"packet not found: {path}") from exc
    except IsADirectoryError as exc:
        raise PacketError(f"packet is a directory: {path}") from exc
    except UnicodeDecodeError as exc:
        raise PacketError(f"packet is not readable text: {path}") from exc
    except OSError as exc:
        raise PacketError(f"packet cannot be read: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PacketError(f"packet is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PacketError("packet must be a JSON object")
    if not isinstance(data.get("candidates"), list) or not data["candidates"]:
        raise PacketError("packet has no candidates list")
    # A duplicate id SILENTLY DOUBLE-COUNTED SigmaSU and capability share, counted one L3 row
    # twice, and let a later row's resolvable evidence overwrite an earlier row's UNAVAILABLE --
    # producing CON-EVIDENCE PASS and exit 0 on a packet whose evidence does not resolve.
    # evaluate_scope_selection_ext.py carries this guard ("Found by independent audit") and the
    # validator rejects duplicates too; this reimplementation dropped it and is restoring it.
    seen: set[str] = set()
    for i, row in enumerate(data["candidates"]):
        if not isinstance(row, dict):
            raise PacketError(f"candidates[{i}] is not an object")
        rid = row.get("id")
        if not isinstance(rid, str) or not rid.strip():
            raise PacketError(f"candidates[{i}] has a blank or non-string id")
        if rid in seen:
            raise PacketError(f"candidates[{i}] repeats id {rid!r}; ids must be unique")
        seen.add(rid)
        su = row.get("su")
        if isinstance(su, bool) or not isinstance(su, (int, float)) or su <= 0:
            raise PacketError(f"candidate {rid}: su must be a positive number, got {su!r}")
        v1 = row.get("predicted_v1")
        if v1 not in {"L0", "L1", "L2", "L3"}:
            raise PacketError(f"candidate {rid}: predicted_v1 must be L0..L3, got {v1!r}")
    return data


def selected_tier1(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Rows the gate would score: disposition SELECT, tier T1 (tier defaults to T1)."""
    out = []
    for row in data["candidates"]:
        if not isinstance(row, dict):
            continue
        if row.get("disposition") != "SELECT":
            continue
        if row.get("tier", "T1") != "T1":
            continue
        out.append(row)
    return out


def read_within_root(root: Path, rel: str) -> str | None:
    """Read a repo-relative file, refusing anything that escapes the root.

    ONE implementation, used by BOTH the evidence check and the class resolver. The first
    round of this repair guarded `source.path` and then introduced the identical hole on
    `initiative_path` -- the field the same commit added. A guard that has to be remembered
    at each call site is a guard that will be missed at one of them.
    """
    try:
        root = root.resolve(strict=True)
        target = (root / rel).resolve(strict=True)
        target.relative_to(root)
        if not target.is_file() or not target.stat().st_mode & 0o400:
            return None
        return target.read_text()
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _initiative_class(root: Path, rel: str) -> str | None:
    r"""Read `class` from the initiative file, as validate_scope_lock_controls.py does.

    The value pattern is the validator's `(\S+)`, not `(\w+)`: on `**Class**: capability-adjacent`
    a `\w+` read yields "capability" and scores the row as capability-facing, while the validator
    reads the whole token and scores it as neither. Truncating toward the favourable answer is
    worse than not reading the file at all.
    """
    text = read_within_root(root, rel)
    if text is None:
        return None, "path does not resolve within the root"
    cls = re.search(r"^\*\*Class\*\*:\s*(\S+)", text, re.M)
    status = re.search(r"^\*\*Status\*\*:\s*(\S+)", text, re.M)
    if not cls:
        # The YAML `class:` fallback this once carried is REMOVED. The validator has no such
        # route (initiative_metadata reads **Field**: only), so accepting it made the forecast
        # PASS packets the validator refuses -- silently, with no note.
        return None, "initiative lacks **Class** metadata; the validator would refuse this packet"
    if not status:
        return None, "initiative lacks **Status** metadata; the validator requires both and " \
                     "would refuse this packet"
    return cls.group(1).strip().lower(), None


def classes_of(data: dict[str, Any], root: Path) -> tuple[dict[str, str | None], list[str]]:
    """Row-id -> class.

    PRIMARY route is the validator's: the initiative file named by `initiative_path`. The
    validator's CANDIDATE_KEYS has no `class` and its TOP_KEYS has no `initiative`, and both
    are enforced by exact_keys(), so a packet it accepts carries NEITHER. Reading only those
    two made this command return CON-CAPABILITY-SHARE UNAVAILABLE on every real packet.

    The inline and top-level forms are kept as a convenience for hypothetical slates whose
    initiative files do not exist yet -- the case the validator cannot score at all.
    """
    out: dict[str, str | None] = {}
    notes: list[str] = []
    initiative = data.get("initiative")
    top = initiative if isinstance(initiative, dict) else {}
    for row in data["candidates"]:
        rid = row["id"]
        cls = None
        rel = row.get("initiative_path")
        if isinstance(rel, str) and rel.strip():
            cls, why = _initiative_class(root, rel)
            if cls is None:
                # A row that NAMES an initiative file and does not resolve it is a typo or an
                # escape, not a hypothetical slate. Falling back to an inline class here made a
                # broken pointer read as a confident answer. The validator raises; we surface.
                notes.append(f"{rid}: initiative_path {rel!r} -- {why}. Class is UNAVAILABLE "
                             f"and no inline value is substituted.")
                out[rid] = None
                continue
        if cls is None and isinstance(top.get(rid), dict):
            cls = top[rid].get("class")
            notes.append(f"{rid}: class taken from the packet's top-level 'initiative' map. "
                         f"The validator's TOP_KEYS has no 'initiative' and exact_keys() would "
                         f"refuse this packet; scored here as a hypothetical slate.")
        if cls is None and "class" in row:
            cls = row.get("class")
            notes.append(f"{rid}: class taken from an inline 'class' field. The validator's "
                         f"CANDIDATE_KEYS has no 'class' and exact_keys() would refuse this "
                         f"packet; scored here as a hypothetical slate.")
        out[rid] = cls.lower() if isinstance(cls, str) else cls
    return out, notes


def evidence_states(rows: list[dict[str, Any]], repo_root: Path) -> dict[str, dict[str, Any]]:
    """Per-row CON-EVIDENCE state. Presence of a source field is NOT acceptance."""
    states: dict[str, dict[str, Any]] = {}
    for row in rows:
        rid = row.get("id", "<no id>")
        source = row.get("source")
        if not isinstance(source, dict):
            states[rid] = {"state": UNAVAILABLE, "why": "row carries no source locators"}
            continue
        raw_path, pattern = source.get("path"), source.get("pattern")
        if not isinstance(raw_path, str) or not raw_path.strip():
            states[rid] = {"state": UNAVAILABLE, "why": "source.path absent or blank"}
            continue
        if not isinstance(pattern, str) or not pattern:
            states[rid] = {"state": UNAVAILABLE, "why": "source.pattern absent or blank"}
            continue
        # The validator's repo_path() refuses a path that escapes the repository. Without the
        # same guard an absolute source.path discards repo_root entirely, so `/etc/hosts` with
        # pattern "localhost" scored CON-EVIDENCE PASS against a root containing no such evidence.
        text = read_within_root(repo_root, raw_path)
        if text is None:
            states[rid] = {"state": UNAVAILABLE,
                           "why": f"source.path does not resolve within the supplied root: "
                                  f"{raw_path}"}
            continue
        if pattern in text:
            states[rid] = {"state": "RESOLVED", "why": None}
        else:
            states[rid] = {"state": "UNRESOLVED", "why": f"pattern not found in {raw_path}"}
    return states


def forecast(data: dict[str, Any], cap_override: float | None, repo_root: Path) -> dict[str, Any]:
    rows = selected_tier1(data)
    classes, class_notes = classes_of(data, repo_root)
    limbs: dict[str, dict[str, Any]] = {}
    notes: list[str] = list(class_notes)

    if not rows:
        for key in ("CON-FLOOR-1", "CON-FLOOR-2", "CON-CAPABILITY-SHARE",
                    "CON-AMBITION-1", "CON-AMBITION-2", "CON-AMBITION", "CAP-CEILING", "CON-EVIDENCE"):
            limbs[key] = {"verdict": UNAVAILABLE, "why": "packet selects no Tier-1 rows"}
        bind_emission_contract(limbs, "selected Tier-1 packet")
        return {"selected_count": 0, "selected_su": 0, "functional_su": 0, "l3_selected": [],
                "selected_ids": [], "limbs": limbs, "notes": notes, "overall": UNAVAILABLE}

    su = sum(r["su"] for r in rows if isinstance(r.get("su"), (int, float)) and not isinstance(r.get("su"), bool))
    func_su = sum(r["su"] for r in rows if r.get("predicted_v1") in {"L2", "L3"})
    l3_sel = [r["id"] for r in rows if r.get("predicted_v1") == "L3"]

    # --- CON-FLOOR, two limbs reported separately -----------------------------
    limbs["CON-FLOOR-1"] = {
        "verdict": PASS if l3_sel else FAIL,
        "l3_selected": l3_sel,
        "why": None if l3_sel else "no selected row carries predicted_v1 L3",
    }
    limbs["CON-FLOOR-2"] = {
        "verdict": PASS if _pct(func_su, su) >= FLOOR_FUNCTIONAL * 100 else FAIL,
        "functional_share_pct": round(_pct(func_su, su), 1),
        "floor_pct": round(FLOOR_FUNCTIONAL * 100, 1),
    }

    # --- CON-CAPABILITY-SHARE -------------------------------------------------
    unclassed = [r["id"] for r in rows if classes.get(r["id"]) not in {"capability", "governance"}]
    if unclassed:
        limbs["CON-CAPABILITY-SHARE"] = {
            "verdict": UNAVAILABLE,
            "why": f"{len(unclassed)} selected row(s) have no capability|governance class",
            "unclassed": sorted(unclassed),
        }
    else:
        cap_su_sum = sum(r["su"] for r in rows if classes.get(r["id"]) == "capability")
        limbs["CON-CAPABILITY-SHARE"] = {
            "verdict": PASS if _pct(cap_su_sum, su) >= FLOOR_CAPABILITY * 100 else FAIL,
            "capability_share_pct": round(_pct(cap_su_sum, su), 1),
            "floor_pct": round(FLOOR_CAPABILITY * 100, 1),
        }

    # --- cap-dependent limbs. The validator RAISES on a bad cap; we report. ----
    cap = cap_override if cap_override is not None else data.get("cap_su")
    cap_usable = (
        isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
    )
    if not cap_usable:
        why = "cap_su absent or not a positive number, and no --cap supplied"
        limbs["CON-AMBITION-1"] = {"verdict": UNAVAILABLE, "why": why}
        limbs["CAP-CEILING"] = {"verdict": UNAVAILABLE, "why": why}
    else:
        limbs["CON-AMBITION-1"] = {
            "verdict": PASS if su >= AMBITION_FILL * cap else FAIL,
            "selected_su": su, "floor_su": round(AMBITION_FILL * cap, 1), "cap": cap,
        }
        # The cap is a CEILING at Gate-1 close as well as an ambition floor.
        limbs["CAP-CEILING"] = {
            "verdict": PASS if su <= cap else FAIL,
            "selected_su": su, "cap": cap,
        }

    # --- CON-AMBITION-2: fires only when the POOL can supply two L3 -----------
    pool = [r for r in data["candidates"] if isinstance(r, dict)]
    pool_l3 = [r["id"] for r in pool if r.get("predicted_v1") == "L3"]
    declared = data.get("pool_allows_two_l3")
    derived = len(pool_l3) >= 2
    if isinstance(declared, bool) and declared is not derived:
        # The validator RAISES here. Forecasting must survive the disagreement and
        # surface it, because a speculative slate is exactly where it shows up.
        notes.append(
            f"pool_allows_two_l3 declared {declared} but the pool holds {len(pool_l3)} L3 candidate(s); "
            f"forecasting from the DERIVED value {derived}. The validator would refuse this packet."
        )
    fires = derived
    if not fires:
        limbs["CON-AMBITION-2"] = {
            "verdict": INERT, "l3_in_pool": len(pool_l3), "l3_selected": len(l3_sel),
            "why": "pool holds <2 L3 candidates; limb does not fire",
        }
    else:
        limbs["CON-AMBITION-2"] = {
            "verdict": PASS if len(l3_sel) >= 2 else FAIL,
            "l3_in_pool": len(pool_l3), "l3_selected": len(l3_sel),
        }

    # --- composed CON-AMBITION, as the validator actually computes it ---------
    a1, a2 = limbs["CON-AMBITION-1"]["verdict"], limbs["CON-AMBITION-2"]["verdict"]
    if a1 == UNAVAILABLE:
        limbs["CON-AMBITION"] = {"verdict": UNAVAILABLE, "why": "limb 1 unavailable"}
    elif FAIL in (a1, a2):
        limbs["CON-AMBITION"] = {"verdict": FAIL, "why": "composed as the validator does: limb1 AND limb2"}
    else:
        limbs["CON-AMBITION"] = {"verdict": PASS, "why": "composed as the validator does: limb1 AND limb2"}

    # --- CON-EVIDENCE: resolution, not presence -------------------------------
    ev = evidence_states(rows, repo_root)
    unresolved = sorted(k for k, v in ev.items() if v["state"] == "UNRESOLVED")
    unavailable = sorted(k for k, v in ev.items() if v["state"] == UNAVAILABLE)
    if unresolved:
        verdict, why = FAIL, f"{len(unresolved)} row(s) cite a readable source whose pattern does not occur"
    elif unavailable:
        verdict, why = UNAVAILABLE, f"{len(unavailable)} row(s) have no resolvable source locators"
    else:
        verdict, why = PASS, None
    limbs["CON-EVIDENCE"] = {
        "verdict": verdict, "why": why,
        "resolved": sorted(k for k, v in ev.items() if v["state"] == "RESOLVED"),
        "unresolved": unresolved, "unavailable": unavailable,
        "detail": {k: v for k, v in ev.items() if v["state"] != "RESOLVED"},
    }

    bind_emission_contract(limbs, "selected Tier-1 packet")
    verdicts = [v["verdict"] for v in limbs.values()]
    overall = FAIL if FAIL in verdicts else (UNAVAILABLE if UNAVAILABLE in verdicts else PASS)
    return {
        "selected_count": len(rows), "selected_su": su, "functional_su": func_su,
        "l3_selected": l3_sel, "selected_ids": [r["id"] for r in rows],
        "limbs": limbs, "notes": notes, "overall": overall,
    }


def compare(pre: dict[str, Any], post: dict[str, Any]) -> dict[str, Any]:
    """Compare a pre-lock forecast against the actual locked selection."""
    rows = []
    for key in sorted(set(pre["limbs"]) | set(post["limbs"])):
        f = pre["limbs"].get(key, {}).get("verdict", "—")
        a = post["limbs"].get(key, {}).get("verdict", "—")
        rows.append({"limb": key, "forecast": f, "actual": a, "agrees": f == a})
    pre_ids, post_ids = set(pre.get("l3_selected", [])), set(post.get("l3_selected", []))
    pre_sel, post_sel = set(pre.get("selected_ids", [])), set(post.get("selected_ids", []))
    # MAJOR-7. `forecast_was_accurate` was limb-verdict agreement ONLY, so a slate in which
    # every selected row changed and SigmaSU moved 7 -> 70 reported "accurate" and exited 0,
    # because both slates happened to pass the same limbs. A forecast of a DIFFERENT selection
    # is not an accurate forecast of this one.
    limbs_agree = not [r for r in rows if not r["agrees"]]
    su_agrees = pre["selected_su"] == post["selected_su"]
    # MAJOR-E: comparing only the L3 set called {A,B} and {A,ZZZ} the same selection.
    rows_agree = pre_ids == post_ids and pre_sel == post_sel
    return {
        "limbs": rows,
        "limbs_disagreeing": [r["limb"] for r in rows if not r["agrees"]],
        "su_forecast": pre["selected_su"], "su_actual": post["selected_su"],
        "su_delta": post["selected_su"] - pre["selected_su"],
        "l3_added": sorted(post_ids - pre_ids), "l3_dropped": sorted(pre_ids - post_ids),
        "rows_added": sorted(post_sel - pre_sel), "rows_dropped": sorted(pre_sel - post_sel),
        "overall_forecast": pre["overall"], "overall_actual": post["overall"],
        # MAJOR-D: compare() kept only limb verdicts, SigmaSU and ids, so a LOCKED packet the
        # validator would refuse outright ("pool_allows_two_l3 declared True but ...") was
        # reported as an accurate forecast, exit 0, with the note unreachable in any output.
        "locked_notes": list(post.get("notes", [])),
        "limbs_agree": limbs_agree,
        "selection_agrees": su_agrees and rows_agree,
        "forecast_was_accurate": limbs_agree and su_agrees and rows_agree,
    }


def render(res: dict[str, Any], title: str) -> str:
    out = [f"{title}: {res['overall']}  ({res['selected_count']} Tier-1 rows, SigmaSU {res['selected_su']})"]
    for key, v in res["limbs"].items():
        bits = []
        for k in ("functional_share_pct", "capability_share_pct", "selected_su", "floor_su",
                  "floor_pct", "cap", "l3_in_pool", "l3_selected"):
            if k in v:
                bits.append(f"{k}={v[k]}")
        extra = ("  " + " ".join(bits)) if bits else ""
        why = f"  -- {v['why']}" if v.get("why") else ""
        out.append(f"  {v['verdict']:<12} {key}{extra}{why}")
    for n in res.get("notes", []):
        out.append(f"  NOTE: {n}")
    return "\n".join(out)


def render_compare(cmp_: dict[str, Any]) -> str:
    out = ["", "--- forecast vs actual locked selection ---",
           f"  SigmaSU forecast={cmp_['su_forecast']} actual={cmp_['su_actual']} delta={cmp_['su_delta']:+}"]
    for r in cmp_["limbs"]:
        mark = "  " if r["agrees"] else "!!"
        out.append(f"  {mark} {r['limb']:<22} forecast={r['forecast']:<12} actual={r['actual']}")
    if cmp_["l3_added"]:
        out.append(f"  L3 added since forecast:   {', '.join(cmp_['l3_added'])}")
    if cmp_["l3_dropped"]:
        out.append(f"  L3 dropped since forecast: {', '.join(cmp_['l3_dropped'])}")
    if cmp_.get("rows_added"):
        out.append(f"  rows added since forecast:   {', '.join(cmp_['rows_added'])}")
    if cmp_.get("rows_dropped"):
        out.append(f"  rows dropped since forecast: {', '.join(cmp_['rows_dropped'])}")
    for n in cmp_.get("locked_notes", []):
        out.append(f"  LOCKED-PACKET NOTE: {n}")
    out.append(f"  limbs agree: {cmp_['limbs_agree']}  selection agrees: {cmp_['selection_agrees']}")
    out.append(f"  forecast was accurate: {cmp_['forecast_was_accurate']}")
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    verdicts = [v["verdict"] for v in res["limbs"].values()]
    if FAIL in verdicts:
        return 1
    if UNAVAILABLE in verdicts:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Non-mutating forecast of the scope-lock value gate. Reports every limb.")
    ap.add_argument("--packet", type=Path, help="selection packet (same shape the validator reads)")
    ap.add_argument("--cap", type=float, default=None,
                    help="cycle cap in SU for the --packet forecast when it declares none. "
                         "NOT applied to --compare-locked: the lock carries its own cap and "
                         "overriding it hides a cap change between forecast and lock")
    ap.add_argument("--repo-root", type=Path, default=Path("."), help="root for resolving source.path")
    ap.add_argument("--compare-locked", type=Path, default=None,
                    help="a second packet holding the ACTUAL locked selection")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.packet:
        ap.error("--packet is required (or use --self-test)")

    try:
        res = forecast(load_packet(args.packet), args.cap, args.repo_root)
        cmp_ = None
        if args.compare_locked:
            # F4: --cap is documented as supplying a cap the PRE-lock packet lacks. Applying
            # it to the locked packet rewrote the lock's own cap_su, so a locked selection the
            # gate would refuse (CON-AMBITION-1 FAIL at its real cap) scored PASS at the
            # override and exited 0 -- MAJOR-D's outcome through a different door.
            post = forecast(load_packet(args.compare_locked), None, args.repo_root)
            cmp_ = compare(res, post)
    except PacketError as exc:
        payload = {"error": str(exc), "overall": UNAVAILABLE}
        print(json.dumps(payload, indent=1) if args.json else f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps({"forecast": res, "comparison": cmp_}, indent=1))
    else:
        print(render(res, "FORECAST"))
        if cmp_:
            print(render_compare(cmp_))
    code = exit_code(res)
    # A comparison that renders a divergence and then exits 0 publishes a clean machine
    # contract over a printed disagreement. The acceptance clause asks the forecast to be
    # COMPARED against the locked selection; a comparison nothing acts on is decoration.
    # A note on the LOCKED packet is a statement about the artifact being shipped; it must
    # reach the exit code even when the two forecasts happen to agree.
    if cmp_ and cmp_.get("locked_notes"):
        code = 1
    if cmp_ and not cmp_["forecast_was_accurate"]:
        # Divergence is a DEFINITE disagreement, so it takes precedence over "cannot certify".
        # Leaving exit 2 in place made a consumer keying on `exit == 1` miss the divergence.
        code = 1
    return code


def self_test() -> int:
    """Both polarities on the states that matter. No fixtures on disk."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "src.md").write_text("the pattern is here")

        def row(rid, su, v1, cls, path="src.md", pat="the pattern is here"):
            return {"id": rid, "disposition": "SELECT", "tier": "T1", "su": su,
                    "predicted_v1": v1, "source": {"path": path, "pattern": pat}, "class": cls}

        # a slate that passes everything
        good = {"cap_su": 10, "pool_allows_two_l3": True,
                "candidates": [row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")]}
        r = forecast(good, None, root)
        if r["overall"] != PASS or exit_code(r) != 0:
            print(f"FAIL self-test: clean slate should PASS, got {r['overall']}"); ok = False

        # evidence UNRESOLVED (path readable, pattern absent) -> FAIL, not UNAVAILABLE
        bad_pat = {"cap_su": 10, "pool_allows_two_l3": True,
                   "candidates": [row("A", 4, "L3", "capability", pat="absent"),
                                  row("B", 3, "L3", "capability")]}
        r = forecast(bad_pat, None, root)
        if r["limbs"]["CON-EVIDENCE"]["verdict"] != FAIL:
            print("FAIL self-test: unresolved pattern must FAIL"); ok = False

        # evidence UNAVAILABLE (path missing) -> UNAVAILABLE, and NOT PASS
        missing = {"cap_su": 10, "pool_allows_two_l3": True,
                   "candidates": [row("A", 4, "L3", "capability", path="nope.md"),
                                  row("B", 3, "L3", "capability")]}
        r = forecast(missing, None, root)
        if r["limbs"]["CON-EVIDENCE"]["verdict"] != UNAVAILABLE:
            print("FAIL self-test: unresolvable source must be UNAVAILABLE"); ok = False
        if exit_code(r) != 2:
            print("FAIL self-test: UNAVAILABLE must exit 2, never 0"); ok = False

        # a source field that is merely PRESENT must not buy a PASS
        present_only = {"cap_su": 10, "pool_allows_two_l3": True,
                        "candidates": [{"id": "A", "disposition": "SELECT", "tier": "T1", "su": 7,
                                        "predicted_v1": "L3", "class": "capability",
                                        "source": {"path": "", "pattern": ""}}]}
        r = forecast(present_only, None, root)
        if r["limbs"]["CON-EVIDENCE"]["verdict"] == PASS:
            print("FAIL self-test: blank locators must not PASS"); ok = False

        # missing cap -> the cap limbs UNAVAILABLE, the others still scored
        nocap = {"pool_allows_two_l3": True,
                 "candidates": [row("A", 4, "L3", "capability"), row("B", 3, "L3", "capability")]}
        r = forecast(nocap, None, root)
        if r["limbs"]["CON-AMBITION-1"]["verdict"] != UNAVAILABLE:
            print("FAIL self-test: absent cap must make CON-AMBITION-1 UNAVAILABLE"); ok = False
        if r["limbs"]["CON-FLOOR-1"]["verdict"] != PASS:
            print("FAIL self-test: an absent cap must not stop the other limbs scoring"); ok = False

        # inert limb 2: pool holds <2 L3
        inert = {"cap_su": 10, "pool_allows_two_l3": False,
                 "candidates": [row("A", 4, "L3", "capability"), row("B", 3, "L2", "capability")]}
        r = forecast(inert, None, root)
        if r["limbs"]["CON-AMBITION-2"]["verdict"] != INERT:
            print("FAIL self-test: limb 2 must be INERT when the pool cannot fire it"); ok = False
        if r["limbs"]["CON-AMBITION"]["verdict"] != PASS:
            print("FAIL self-test: INERT limb 2 must not drag the composed verdict to FAIL"); ok = False

        # PER-LIMB ISOLATION. This block previously asserted `len(failing) >= 3` against a
        # packet failing five, so ANY ONE limb could be permanently green and it still passed.
        # Measured: 6 of 8 injected regressions survived that net, including zeroing all three
        # rubric thresholds. evaluate_scope_selection_ext.py carries an isolation control for
        # exactly this reason ("relaxing the functional floor to zero left the self-test green
        # -- limb 1 was masking it"); this reimplementation dropped it. Each limb below is
        # driven to FAIL with every OTHER limb satisfied, so nothing can mask anything.
        isolation = [
            # (name, packet, the limb that must FAIL)
            ("CON-FLOOR-1", {"cap_su": 10, "pool_allows_two_l3": False,
                             "candidates": [row("A", 4, "L2", "capability"),
                                            row("B", 3, "L2", "capability")]}, "CON-FLOOR-1"),
            ("CON-FLOOR-2", {"cap_su": 10, "pool_allows_two_l3": True,
                             "candidates": [row("A", 2, "L3", "capability"),
                                            row("B", 5, "L1", "capability")]}, "CON-FLOOR-2"),
            ("CON-CAPABILITY-SHARE", {"cap_su": 10, "pool_allows_two_l3": True,
                                      "candidates": [row("A", 4, "L3", "governance"),
                                                     row("B", 3, "L3", "governance")]},
             "CON-CAPABILITY-SHARE"),
            ("CON-AMBITION-1", {"cap_su": 1000, "pool_allows_two_l3": True,
                                "candidates": [row("A", 4, "L3", "capability"),
                                               row("B", 3, "L3", "capability")]},
             "CON-AMBITION-1"),
            ("CAP-CEILING", {"cap_su": 5, "pool_allows_two_l3": True,
                             "candidates": [row("A", 4, "L3", "capability"),
                                            row("B", 3, "L3", "capability")]}, "CAP-CEILING"),
            ("CON-AMBITION-2", {"cap_su": 10, "pool_allows_two_l3": True,
                                "candidates": [row("A", 4, "L3", "capability"),
                                               row("B", 3, "L2", "capability"),
                                               {**row("C", 1, "L3", "capability"),
                                                "disposition": "DEFER", "tier": "DEFER"}]},
             "CON-AMBITION-2"),
        ]
        for name, pkt, must_fail in isolation:
            r = forecast(pkt, None, root)
            if r["limbs"][must_fail]["verdict"] != FAIL:
                print(f"FAIL self-test: {name} isolation -- {must_fail} should FAIL, got "
                      f"{r['limbs'][must_fail]['verdict']}"); ok = False

        # and it must still report several failures together rather than aborting
        multi = {"cap_su": 100, "pool_allows_two_l3": True,
                 "candidates": [row("A", 4, "L1", "governance"), row("B", 3, "L1", "governance")]}
        r = forecast(multi, None, root)
        for limb in ("CON-FLOOR-1", "CON-FLOOR-2", "CON-CAPABILITY-SHARE", "CON-AMBITION-1"):
            if r["limbs"][limb]["verdict"] != FAIL:
                print(f"FAIL self-test: {limb} must FAIL on the all-bad packet"); ok = False

        # declared/derived disagreement is surfaced, not raised
        disagree = {"cap_su": 10, "pool_allows_two_l3": True,
                    "candidates": [row("A", 4, "L3", "capability"), row("B", 3, "L2", "capability")]}
        r = forecast(disagree, None, root)
        if not r["notes"]:
            print("FAIL self-test: pool_allows_two_l3 disagreement must be surfaced"); ok = False

        # forecast vs actual comparison
        c = compare(forecast(good, None, root), forecast(multi, None, root))
        if c["forecast_was_accurate"] or not c["limbs_disagreeing"]:
            print("FAIL self-test: comparison must detect divergence"); ok = False

    print("self-test: PASS" if ok else "self-test: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
