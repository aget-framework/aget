#!/usr/bin/env python3
"""
check_initiatives.py — Portfolio-level rollup across planning/initiatives/INIT-*.md.

The structural firing surface for INIT-INITIATIVE-MATURATION Stream 3. The
framework has aggregate-portfolio rollup engines for nearly every artifact class
(L-docs -> check_evolution; KB -> check_kb; ontology -> analyse_ontology; config
-> check_config) except initiatives. Without this engine the "how many
initiatives do we have?" question forces manual grep aggregation across 20+
INIT-*.md files — the failure mode that triggered PROPOSAL_aget-check-initiatives
on 2026-05-20.

Read-only. Companion engine to the /aget-check-initiatives skill (SKILL.md owns
the trigger phrases + report prose; this script owns the computation).

Usage:
  python3 scripts/check_initiatives.py            # human-readable rollup
  python3 scripts/check_initiatives.py --json      # machine-readable
  python3 scripts/check_initiatives.py --quiet      # counts only
  python3 scripts/check_initiatives.py --past-target # Loading Dock instances only
  python3 scripts/check_initiatives.py --cohort      # sibling-arc clusters only
  python3 scripts/check_initiatives.py --strict      # exit 1 on any anomaly

Exit codes:
  0  Clean report (or read-only mode without --strict)
  1  At least one pipeline anomaly AND --strict

Requirements implemented (SKILL.md §Requirements):
  CIS-001 enumerate INIT-*.md + inventory grouped by Status
  CIS-002 0-COMPLETE anomaly (COMPLETE+CLOSED==0 AND ACTIVE>0)
  CIS-003 past-target flag via .aget/version.json comparison
  CIS-004 approved-but-unscaffolded PROPOSAL_init_*.md flag
  CIS-005 staleness flag (>=30 days, git-log-based)
  CIS-006 same-arc cohort cluster detection (<=7-day scaffold + naming family)
  CAP-INIT-007 / V-INIT-007 recursion check (own-row present in output)

Reference: gh#1469 (INIT-INITIATIVE-MATURATION Stream 3); VERSION_SCOPE_v3.21.0
Tier-1 C-21-02; PROPOSAL_aget-check-initiatives APPROVED 2026-05-21.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INIT_DIR = REPO / "planning" / "initiatives"
PROPOSAL_DIR = REPO / "planning" / "project-proposals"
VERSION_JSON = REPO / ".aget" / "version.json"

# FOLDED = an initiative merged into another (terminal disposition; the work
# continues under the host initiative). Recognized so it is never silently
# dropped from the rollup — silent-drop defeats the audit (the engine's whole
# purpose is "don't miss an initiative"). CIS-002 names only COMPLETE/CLOSED;
# FOLDED is a spec gap recorded as a Finding (L742 — fix the spec, not just code).
STATUS_ORDER = ["ACTIVE", "NASCENT", "PROPOSED", "COMPLETE", "CLOSED", "FOLDED", "DORMANT"]
TERMINAL_STATUSES = {"COMPLETE", "CLOSED", "FOLDED"}
KNOWN_STATUSES = set(STATUS_ORDER)
STALE_DAYS = 30
COHORT_WINDOW_DAYS = 7
OWN_INITIATIVE = "INIT-INITIATIVE-MATURATION"

# **Status**: ACTIVE (trailing parenthetical/prose allowed) -> first bare token.
STATUS_RE = re.compile(r"^\*\*Status\*\*:\s*([A-Za-z]+)", re.MULTILINE)
TARGET_RE = re.compile(r"^\*\*Target Versions?\*\*:\s*(.+)$", re.MULTILINE)
CREATED_RE = re.compile(r"^\*\*Created\*\*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
# Version tokens like v3.21 or v4.0.1 (the leading 'v' is optional in the field).
VERSION_TOKEN_RE = re.compile(r"v?(\d+)\.(\d+)(?:\.(\d+))?")
# A version token followed by '+' (e.g. "v3.20+") declares an OPEN-ENDED upper
# bound — "this version and onward". Such a window is never past-target, even
# once the agent version passes the bare token. Without this the '+' is dropped
# and the token mis-reads as a closed ceiling (false-positive Loading Dock).
OPEN_ENDED_RE = re.compile(r"v?\d+\.\d+(?:\.\d+)?\s*\+")


def parse_version(text):
    """Return the highest (major, minor, patch) tuple found in text, or None."""
    best = None
    for m in VERSION_TOKEN_RE.finditer(text):
        tup = (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))
        if best is None or tup > best:
            best = tup
    return best


def current_version():
    try:
        data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return parse_version(data.get("aget_version", ""))


def last_commit_dt(path):
    """ISO datetime of the last commit touching path, or None if untracked/error."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(path)],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    stamp = out.stdout.strip()
    if not stamp:
        return None
    try:
        return datetime.fromisoformat(stamp)
    except ValueError:
        return None


def proposal_to_init_name(proposal_path):
    """PROPOSAL_init_always_on_host.md -> INIT-ALWAYS-ON-HOST (amendment-stripped)."""
    slug = proposal_path.stem[len("PROPOSAL_init_"):]
    if slug.endswith("_amendment"):
        slug = slug[: -len("_amendment")]
    return "INIT-" + slug.upper().replace("_", "-")


def gather(now=None):
    now = now or datetime.now(timezone.utc)
    cur = current_version()
    initiatives = []
    for path in sorted(INIT_DIR.glob("INIT-*.md")):
        text = path.read_text(encoding="utf-8")
        sm = STATUS_RE.search(text)
        status = sm.group(1).upper() if sm else "UNKNOWN"
        tm = TARGET_RE.search(text)
        target_field = tm.group(1) if tm else ""
        target = parse_version(target_field) if tm else None
        open_ended = bool(OPEN_ENDED_RE.search(target_field))
        cm = CREATED_RE.search(text)
        commit_dt = last_commit_dt(path)
        age_days = None
        if commit_dt is not None:
            age_days = (now - commit_dt.astimezone(timezone.utc)).days
        terminal = status in TERMINAL_STATUSES
        past_target = bool(
            cur and target and target < cur and not terminal and not open_ended
        )
        initiatives.append({
            "id": path.stem,
            "status": status,
            "target": target,
            "target_str": ".".join(map(str, target)) if target else None,
            "created": cm.group(1) if cm else None,
            "age_days": age_days,
            "stale": age_days is not None and age_days >= STALE_DAYS and not terminal,
            "past_target": past_target,
        })
    return initiatives, cur


def detect_unscaffolded():
    """APPROVED PROPOSAL_init_*.md with no matching INIT-*.md (initiative Loading Dock)."""
    flagged = []
    existing = {p.stem for p in INIT_DIR.glob("INIT-*.md")}
    for prop in sorted(PROPOSAL_DIR.glob("PROPOSAL_init_*.md")):
        try:
            text = prop.read_text(encoding="utf-8")
        except OSError:
            continue
        if not re.search(r"Status.{0,4}:\s*\**APPROVED", text):
            continue
        init_name = proposal_to_init_name(prop)
        if init_name not in existing:
            flagged.append({"proposal": prop.name, "expected_init": init_name})
    return flagged


def detect_cohorts(initiatives):
    """Same-arc clusters: shared trailing naming family AND created within 7 days."""
    families = {}
    for it in initiatives:
        parts = it["id"].split("-")
        family = parts[-1] if len(parts) > 1 else it["id"]
        families.setdefault(family, []).append(it)
    cohorts = []
    for family, members in families.items():
        dated = [m for m in members if m["created"]]
        if len(dated) < 2:
            continue
        dated.sort(key=lambda m: m["created"])
        span = (datetime.fromisoformat(dated[-1]["created"])
                - datetime.fromisoformat(dated[0]["created"])).days
        if span <= COHORT_WINDOW_DAYS:
            cohorts.append({
                "family": family,
                "members": [m["id"] for m in dated],
                "span_days": span,
            })
    return cohorts


def build_report(now=None):
    initiatives, cur = gather(now=now)
    inventory = {s: [] for s in STATUS_ORDER}
    for it in initiatives:
        inventory.setdefault(it["status"], []).append(it["id"])

    n_active = len(inventory.get("ACTIVE", []))
    n_complete_closed = len(inventory.get("COMPLETE", [])) + len(inventory.get("CLOSED", []))
    n_folded = len(inventory.get("FOLDED", []))
    n_terminal = n_complete_closed + n_folded

    anomalies = {
        # CIS-002 (literal) is COMPLETE+CLOSED==0; widened to include FOLDED
        # since a fold IS a walked close-loop (resolution by merger). The
        # COMPLETE/CLOSED=0-while-FOLDED>0 nuance is surfaced in the report.
        "zero_complete": n_terminal == 0 and n_active > 0,
        "complete_closed": n_complete_closed,
        "folded": n_folded,
        "past_target": [it["id"] for it in initiatives if it["past_target"]],
        "unscaffolded": detect_unscaffolded(),
        "stale": [
            {"id": it["id"], "age_days": it["age_days"]}
            for it in initiatives if it["stale"]
        ],
    }
    cohorts = detect_cohorts(initiatives)
    own = next((it for it in initiatives if it["id"] == OWN_INITIATIVE), None)
    recursion = {
        "own_present": own is not None,
        "own_status": own["status"] if own else None,
        "v_init_007": "PASS" if own is not None else "FAIL",
    }
    return {
        "current_version": ".".join(map(str, cur)) if cur else None,
        "total": len(initiatives),
        "inventory": {s: inventory.get(s, []) for s in STATUS_ORDER},
        "wip": n_active,
        "anomalies": anomalies,
        "cohorts": cohorts,
        "recursion": recursion,
        "initiatives": initiatives,
    }


def has_anomaly(report):
    a = report["anomalies"]
    return bool(
        a["zero_complete"] or a["past_target"] or a["unscaffolded"]
        or a["stale"] or report["recursion"]["v_init_007"] == "FAIL"
    )


def render_human(report):
    lines = ["=== /aget-check-initiatives ===", ""]
    lines.append(f"Inventory ({report['total']} total; agent v{report['current_version']}):")
    for s in STATUS_ORDER:
        ids = report["inventory"][s]
        if ids:
            shown = ", ".join(ids)
            lines.append(f"  {s + ':':10} {len(ids)} ({shown})")
        else:
            lines.append(f"  {s + ':':10} 0")
    lines.append("")
    a = report["anomalies"]
    lines.append("Pipeline anomalies:")
    if a["zero_complete"]:
        lines.append("  - 0 terminal dispositions ever AND ACTIVE>0 (close-loop not walked)")
    elif a["complete_closed"] == 0 and a["folded"] > 0:
        lines.append(f"  - 0 COMPLETE/CLOSED, but {a['folded']} FOLDED (close-loop walked via merger, not completion)")
    if a["past_target"]:
        lines.append(f"  - {len(a['past_target'])} past-target (Loading Dock): {', '.join(a['past_target'])}")
    if a["unscaffolded"]:
        names = ", ".join(u["proposal"] for u in a["unscaffolded"])
        lines.append(f"  - {len(a['unscaffolded'])} approved-but-unscaffolded: {names}")
    if a["stale"]:
        items = ", ".join(f"{s['id']} ({s['age_days']}d)" for s in a["stale"])
        lines.append(f"  - {len(a['stale'])} stale (>={STALE_DAYS}d no commit): {items}")
    if not (a["zero_complete"] or a["past_target"] or a["unscaffolded"] or a["stale"]):
        lines.append("  - none")
    lines.append("")
    lines.append("Cohort detection:")
    if report["cohorts"]:
        for c in report["cohorts"]:
            lines.append(f"  - {c['family']} family ({c['span_days']}d span): {', '.join(c['members'])}")
    else:
        lines.append("  - none")
    lines.append("")
    lines.append(f"Capacity:\n  - WIP: {report['wip']} ACTIVE initiatives")
    lines.append("")
    r = report["recursion"]
    lines.append(f"Recursion check:\n  - {OWN_INITIATIVE} own-status: {r['own_status']} [V-INIT-007 {r['v_init_007']}]")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Portfolio rollup over planning/initiatives/INIT-*.md")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", action="store_true", help="counts only")
    ap.add_argument("--past-target", action="store_true", help="Loading Dock instances only")
    ap.add_argument("--cohort", action="store_true", help="sibling-arc clusters only")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any anomaly")
    args = ap.parse_args(argv)

    report = build_report()

    if args.past_target:
        out = report["anomalies"]["past_target"]
        print(json.dumps(out) if args.json else ("\n".join(out) or "(none past-target)"))
    elif args.cohort:
        out = report["cohorts"]
        print(json.dumps(out, indent=2) if args.json else
              ("\n".join(f"{c['family']}: {', '.join(c['members'])}" for c in out) or "(no cohorts)"))
    elif args.json:
        print(json.dumps(report, indent=2))
    elif args.quiet:
        inv = report["inventory"]
        print(" ".join(f"{s}={len(inv[s])}" for s in STATUS_ORDER) + f" WIP={report['wip']}")
    else:
        print(render_human(report))

    return 1 if (args.strict and has_anomaly(report)) else 0


if __name__ == "__main__":
    sys.exit(main())
