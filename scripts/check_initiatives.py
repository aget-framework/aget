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
  CIS-007 proposal<->manifest status-mismatch detection (header lags disposition —
          the gap recorded 2026-06-07 in PROPOSAL_init_lesson_first_issue_filing
          and reproduced 2026-06-12 by 4 stale headers; closed per E2)
  CIS-008 ACTIVE-ceiling check vs the machine-readable declaration in
          planning/initiatives/INDEX.md (L178 overrides are recorded there in prose)
          + capability-ratio floor (>=1/3 capability-class among **Achieve-typed
          ACTIVE only** — D-27-A denominator re-spec, principal-ruled 2026-07-18
          at v3.27 lock; Maintain stewards excluded, reported for visibility;
          v3.22 D-2 floor retained; gh#1655 + C-27-12). Three-state per
          CONVENTION_check_three_state_contract: PASS / FAIL / UNKNOWN
          (UNKNOWN while any Achieve ACTIVE lacks Class OR any ACTIVE is untyped).
  CIS-009 typed-lifecycle block presence (D-IG-1/4 + gh#1884): ACTIVE untyped ->
          WARN; ACTIVE Achieve without '## Exit Conditions' -> WARN; ACTIVE
          Maintain without '## Health Contract' -> WARN. No silent defaults
          (anti-L671). Design: docs/DESIGN_initiative_typing_v1.0.md
  CAP-INIT-007 / V-INIT-007 recursion check (own-row present in output)

  Typed-detector scoping (D-IG-4, 2-class): CIS-002 0-COMPLETE and CIS-003
  past-target fire for Achieve-typed (and, conservatively, untyped) manifests
  only; Maintain is health-metered, not completion-metered. Maintain spine size
  is reported against the D-IG-1 target band. Achieve manifests additionally
  report age-in-portfolio (aging-WIP practice) for grooming verdicts (D-IG-3).

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
STATUS_ORDER = ["ACTIVE", "NASCENT", "PROPOSED", "COMPLETE", "CLOSED", "FOLDED",
                "GRADUATED", "DORMANT"]
TERMINAL_STATUSES = {"COMPLETE", "CLOSED", "FOLDED", "GRADUATED"}
KNOWN_STATUSES = set(STATUS_ORDER)
STALE_DAYS = 30
COHORT_WINDOW_DAYS = 7
OWN_INITIATIVE = "INIT-INITIATIVE-MATURATION"
# D-IG-4: 2-class terminal-behavior axis. Anything else parsed as-is and warned
# (unknown-type is worse than untyped — it looks typed but binds no detector).
KNOWN_TYPES = {"ACHIEVE", "MAINTAIN"}
# v3.22 D-2 governing control: >=1/3 of ACTIVE must be capability-class.
CAPABILITY_FLOOR = 1.0 / 3.0
# D-IG-1 target shape: ~6-8 Maintain stewards as the stable spine (report-only).
MAINTAIN_SPINE_BAND = (6, 8)

# **Status**: ACTIVE (trailing parenthetical/prose allowed) -> first bare token.
# Optional \** before the token: bold-wrapped statuses (`**Status**: **ACTIVE** (...)`)
# parsed as UNKNOWN and silently vanished from the report inventory (found via
# test_v_cis_001 on INIT-ALWAYS-ON-HOST, 2026-06-12 — the silent-drop the header
# comment warns about, enacted by the parser itself).
STATUS_RE = re.compile(r"^\*\*Status\*\*:\s*\**\s*([A-Za-z]+)", re.MULTILINE)
# Typing fields (DESIGN_initiative_typing_v1.0 §1) — same bold-tolerant shape as
# STATUS_RE (the 2026-06-12 bold-token lesson applied at authoring time).
TYPE_RE = re.compile(r"^\*\*Type\*\*:\s*\**\s*([A-Za-z]+)", re.MULTILINE)
CLASS_RE = re.compile(r"^\*\*Class\*\*:\s*\**\s*([A-Za-z]+)", re.MULTILINE)
INTIMACY_RE = re.compile(r"^\*\*Intimacy\*\*:\s*\**\s*([A-Za-z:_-]+)", re.MULTILINE)
EXIT_BLOCK_RE = re.compile(r"^##\s+Exit Conditions\b", re.MULTILINE)
HEALTH_BLOCK_RE = re.compile(r"^##\s+Health Contract\b", re.MULTILINE)
TARGET_RE = re.compile(r"^\*\*Target Versions?\*\*:\s*(.+)$", re.MULTILINE)
CREATED_RE = re.compile(r"^\*\*Created\*\*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
# Version tokens like v3.21 or v4.0.1 (the leading 'v' is optional in the field).
VERSION_TOKEN_RE = re.compile(r"v?(\d+)\.(\d+)(?:\.(\d+))?")
# A version token followed by '+' (e.g. "v3.20+") declares an OPEN-ENDED upper
# bound — "this version and onward". Such a window is never past-target, even
# once the agent version passes the bare token. Without this the '+' is dropped
# and the token mis-reads as a closed ceiling (false-positive Loading Dock).
OPEN_ENDED_RE = re.compile(r"v?\d+\.\d+(?:\.\d+)?\s*\+")
INDEX_MD = INIT_DIR / "INDEX.md"
CEILING_RE = re.compile(r"^\*\*ACTIVE-ceiling \(machine-readable\)\*\*:\s*(\d+)", re.MULTILINE)
# A proposal whose Status line leads with a terminal disposition is closed at the
# proposal layer regardless of an earlier APPROVED in its history — FOLDED ones
# especially must not flag as "approved-but-unscaffolded" (scaffolding a folded
# proposal would be the error). SCAFFOLDED = approved AND manifest exists.
PROPOSAL_TERMINAL_RE = re.compile(
    r"^\*\*Status\*\*:\s*\**\s*(?:FOLDED|REJECTED|WITHDRAWN|SUPERSEDED)", re.MULTILINE)
PROPOSAL_STATUS_LINE_RE = re.compile(r"^\*\*Status\*\*:\s*(.+)$", re.MULTILINE)
# Body-level fold disposition (e.g. "> **DISPOSITION — FOLDED 2026-06-10**" or a
# checked "- [x] **Fold into ...**") — catches a Decision section the header lags.
BODY_FOLD_RE = re.compile(r"DISPOSITION\s*[—-]+\s*FOLDED|^\s*-\s*\[x\]\s*\**Fold\b",
                          re.MULTILINE | re.IGNORECASE)


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
        # A target field leading with "suspended" declares its window historical
        # (E5 Loading-Dock convention, 2026-06-12): version tokens that remain in
        # the field are provenance, not a live delivery commitment. Keyed off the
        # field, not Status — a DORMANT manifest with an unannotated live target
        # SHOULD still flag (pressure to annotate or re-target).
        suspended = target_field.lstrip().lower().startswith("suspended")
        # Typing axis (D-IG-4). Untyped = None (never defaulted, anti-L671);
        # detectors treat untyped conservatively as Achieve-like so coverage
        # never regresses pre-backfill.
        ty = TYPE_RE.search(text)
        itype = ty.group(1).upper() if ty else None
        cl = CLASS_RE.search(text)
        iclass = cl.group(1).lower() if cl else None
        im = INTIMACY_RE.search(text)
        intimacy = im.group(1).lower() if im else None
        # D-IG-4 detector scoping: Maintain is health-metered — a version window
        # is provenance for it, never a live delivery commitment (CIS-003 exempt).
        past_target = bool(
            cur and target and target < cur
            and not terminal and not open_ended and not suspended
            and itype != "MAINTAIN"
        )
        created = cm.group(1) if cm else None
        created_age_days = None
        if created:
            try:
                created_age_days = (now - datetime.fromisoformat(created)
                                    .replace(tzinfo=timezone.utc)).days
            except ValueError:
                pass
        initiatives.append({
            "id": path.stem,
            "status": status,
            "type": itype,
            "class": iclass,
            "intimacy": intimacy,
            "has_exit_conditions": bool(EXIT_BLOCK_RE.search(text)),
            "ec_ticks": _ec_tick_counts(text),
            "has_health_contract": bool(HEALTH_BLOCK_RE.search(text)),
            "target": target,
            "target_str": ".".join(map(str, target)) if target else None,
            "created": created,
            "created_age_days": created_age_days,
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
        if PROPOSAL_TERMINAL_RE.search(text):  # CIS-007 companion: folded != pending-scaffold
            continue
        if not re.search(r"Status.{0,4}:\s*\**APPROVED", text):
            continue
        init_name = proposal_to_init_name(prop)
        if init_name not in existing:
            flagged.append({"proposal": prop.name, "expected_init": init_name})
    return flagged


def detect_status_mismatches():
    """CIS-007: proposal headers that lag their actual disposition.

    Two cheap, high-precision signals (each reproduced live on 2026-06-12):
      - header leads PROPOSED while the mapped INIT-*.md manifest exists
        (PP-014/PP-033 class — approval+scaffold happened, header never updated)
      - header leads PROPOSED while the body carries a fold disposition
        (PP-051 class — Decision section ruled FOLDED, header never updated)
    Name-mapping is heuristic (proposal slug -> INIT id), so a renamed initiative
    can evade the first signal — false negatives accepted, zero-noise preferred.
    """
    flagged = []
    existing = {p.stem for p in INIT_DIR.glob("INIT-*.md")}
    for prop in sorted(PROPOSAL_DIR.glob("PROPOSAL_init_*.md")):
        try:
            text = prop.read_text(encoding="utf-8")
        except OSError:
            continue
        sl = PROPOSAL_STATUS_LINE_RE.search(text)
        if not sl or not re.match(r"\**\s*PROPOSED\b", sl.group(1)):
            continue
        init_name = proposal_to_init_name(prop)
        if init_name in existing:
            flagged.append({"proposal": prop.name, "lag": f"manifest {init_name} exists"})
        elif BODY_FOLD_RE.search(text):
            flagged.append({"proposal": prop.name, "lag": "body carries fold disposition"})
    return flagged


def declared_ceiling():
    """CIS-008: the machine-readable ACTIVE-ceiling declared in INDEX.md, or None."""
    try:
        m = CEILING_RE.search(INDEX_MD.read_text(encoding="utf-8"))
    except OSError:
        return None
    return int(m.group(1)) if m else None


EC_SECTION_RE = re.compile(r"^##\s+Exit Conditions\b(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
EC_ITEM_RE = re.compile(r"^\s*-\s*\[( |x|X)\]", re.MULTILINE)


def _ec_tick_counts(text):
    """(ticked, total) checkbox counts inside the '## Exit Conditions' section, or None."""
    m = EC_SECTION_RE.search(text)
    if not m:
        return None
    boxes = EC_ITEM_RE.findall(m.group(1))
    if not boxes:
        return None
    ticked = sum(1 for b in boxes if b in "xX")
    return {"ticked": ticked, "total": len(boxes)}


def detect_cis010(initiatives):
    """CIS-010 (C-27-11, v3.27 G1.3): EC tick-state as a MAINTAINED signal.

    F-2026-07-16-A: 0/38 exit conditions ticked across the Achieve portfolio while
    >=4 verified MET at source — a decorative EC layer is the mechanism behind a
    0-COMPLETE portfolio (L1189). This detector makes tick-state a maintained,
    surfaced reading: per-ACTIVE-Achieve ticked/total + the portfolio aggregate.
    Detector-before-backfill (L1167): it REPORTS; ticking remains an owner act
    with verify-evidence (INIT-INITIATIVE-MATURATION S3/S4).
    Aggregate WARN when ACTIVE Achieve ECs exist and ZERO are ticked portfolio-wide.
    """
    rows, total_t, total_n = [], 0, 0
    for it in initiatives:
        if it["status"] == "ACTIVE" and (it.get("type") or "").upper() == "ACHIEVE" \
                and it.get("ec_ticks"):
            ec = it["ec_ticks"]
            rows.append({"id": it["id"], "ticked": ec["ticked"], "total": ec["total"]})
            total_t += ec["ticked"]; total_n += ec["total"]
    return {"rows": rows, "ticked": total_t, "total": total_n,
            "state": ("WARN" if (total_n and total_t == 0) else ("PASS" if total_n else "N/A"))}


def detect_cis009(initiatives):
    """CIS-009: typed-lifecycle block presence on ACTIVE manifests (gh#1884).

    WARN classes (each names the missing consumer-facing artifact, anti-L671):
      untyped                  ACTIVE manifest with no **Type** field
      unknown-type             **Type** value outside {Achieve, Maintain}
      missing-exit-conditions  Achieve without a '## Exit Conditions' block
      missing-health-contract  Maintain without a '## Health Contract' block
    """
    warns = []
    for it in initiatives:
        if it["status"] != "ACTIVE":
            continue
        if it["type"] is None:
            warns.append({"id": it["id"], "warn": "untyped"})
        elif it["type"] not in KNOWN_TYPES:
            warns.append({"id": it["id"], "warn": f"unknown-type:{it['type']}"})
        elif it["type"] == "ACHIEVE" and not it["has_exit_conditions"]:
            warns.append({"id": it["id"], "warn": "missing-exit-conditions"})
        elif it["type"] == "MAINTAIN" and not it["has_health_contract"]:
            warns.append({"id": it["id"], "warn": "missing-health-contract"})
    return warns


def capability_ratio(initiatives):
    """CIS-008 ratio half (gh#1655), **Achieve-only denominator** (D-27-A, 2026-07-18).

    Principal ruling D-27-A (v3.27 lock, VERSION_SCOPE_v3.27.0 §Rulings Record):
    capability share is measured among Achieve-typed ACTIVE only — permanent
    Maintain stewards are governance-by-nature and dilute the ratio in a way no
    action can fix, and the all-ACTIVE form punished finishing capability work.
    First computation under this form: 2/9 = 22.2% FAIL (2026-07-18, release plan
    G(-1).2 — red accepted by principal, consumer = next grooming pass).

    Three-state (CONVENTION_check_three_state_contract): UNKNOWN while any
    Achieve-typed ACTIVE manifest lacks a Class tag — an unprobed portfolio must
    not report PASS (#1553). Maintain/untyped ACTIVE are reported for visibility
    but excluded from the denominator; an untyped ACTIVE row also forces UNKNOWN
    (it cannot be excluded-or-included honestly until typed — C-27-13 lane).
    """
    active = [it for it in initiatives if it["status"] == "ACTIVE"]
    if not active:
        return {"state": "PASS", "capability": 0, "governance": 0, "untagged": 0,
                "denominator": "achieve-only (D-27-A)", "achieve": 0, "maintain_excluded": 0,
                "untyped": 0, "ratio": None, "floor": round(CAPABILITY_FLOOR, 4)}
    achieve = [it for it in active if (it.get("type") or "").upper() == "ACHIEVE"]
    maintain = [it for it in active if (it.get("type") or "").upper() == "MAINTAIN"]
    untyped_rows = [it for it in active if (it.get("type") or "").upper() not in KNOWN_TYPES]
    cap = sum(1 for it in achieve if it["class"] == "capability")
    gov = sum(1 for it in achieve if it["class"] == "governance")
    untagged = len(achieve) - cap - gov
    ratio = (cap / len(achieve)) if achieve else None
    if untagged or untyped_rows:
        state = "UNKNOWN"
    elif ratio is None:
        state = "PASS"
    else:
        state = "PASS" if ratio >= CAPABILITY_FLOOR else "FAIL"
    return {"state": state, "capability": cap, "governance": gov,
            "untagged": untagged, "denominator": "achieve-only (D-27-A)",
            "achieve": len(achieve), "maintain_excluded": len(maintain),
            "untyped": len(untyped_rows),
            "ratio": round(ratio, 4) if ratio is not None else None,
            "floor": round(CAPABILITY_FLOOR, 4)}


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

    # D-IG-4 scoping: completion metrics judge Achieve-typed (and, conservatively,
    # untyped) initiatives only; Maintain is the health-metered spine (D-IG-1).
    active_achieve_like = [it for it in initiatives
                           if it["status"] == "ACTIVE" and it["type"] != "MAINTAIN"]
    maintain_spine = [it for it in initiatives
                      if it["status"] == "ACTIVE" and it["type"] == "MAINTAIN"]
    anomalies = {
        # CIS-002 (literal) is COMPLETE+CLOSED==0; widened to include FOLDED
        # since a fold IS a walked close-loop (resolution by merger). The
        # COMPLETE/CLOSED=0-while-FOLDED>0 nuance is surfaced in the report.
        # Typed scoping: fires only while Achieve-like ACTIVE work exists.
        "zero_complete": n_terminal == 0 and len(active_achieve_like) > 0,
        "complete_closed": n_complete_closed,
        "folded": n_folded,
        "past_target": [it["id"] for it in initiatives if it["past_target"]],
        "unscaffolded": detect_unscaffolded(),
        "status_mismatches": detect_status_mismatches(),
        "stale": [
            {"id": it["id"], "age_days": it["age_days"]}
            for it in initiatives if it["stale"]
        ],
        "cis009": detect_cis009(initiatives),
    }
    ceiling = declared_ceiling()
    anomalies["ceiling"] = ceiling
    anomalies["over_ceiling"] = (n_active - ceiling) if (ceiling is not None and n_active > ceiling) else 0
    anomalies["capability_ratio"] = capability_ratio(initiatives)
    anomalies["ec_tick_state"] = detect_cis010(initiatives)
    # Report-only shape signals (grooming inputs, D-IG-1/3 — not strict-anomalies)
    spine_lo, spine_hi = MAINTAIN_SPINE_BAND
    shape = {
        "maintain_spine": len(maintain_spine),
        "maintain_spine_band": list(MAINTAIN_SPINE_BAND),
        "maintain_spine_in_band": spine_lo <= len(maintain_spine) <= spine_hi,
        "achieve_aging": sorted(
            ({"id": it["id"], "created_age_days": it["created_age_days"]}
             for it in active_achieve_like if it["created_age_days"] is not None),
            key=lambda x: -x["created_age_days"]),
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
        # Include non-standard buckets (e.g. UNKNOWN) — filtering to STATUS_ORDER
        # silently dropped unparseable statuses from the returned inventory.
        "inventory": {s: inventory.get(s, [])
                      for s in (STATUS_ORDER
                                + sorted(set(inventory) - set(STATUS_ORDER)))},
        "wip": n_active,
        "anomalies": anomalies,
        "shape": shape,
        "cohorts": cohorts,
        "recursion": recursion,
        "initiatives": initiatives,
    }


def has_anomaly(report):
    a = report["anomalies"]
    return bool(
        a["zero_complete"] or a["past_target"] or a["unscaffolded"]
        or a["status_mismatches"] or a["over_ceiling"]
        or a["stale"] or a["cis009"]
        or a["capability_ratio"]["state"] == "FAIL"
        or report["recursion"]["v_init_007"] == "FAIL"
    )


def render_human(report):
    lines = ["=== /aget-check-initiatives ===", ""]
    lines.append(f"Inventory ({report['total']} total; agent v{report['current_version']}):")
    for s in report["inventory"]:
        ids = report["inventory"][s]
        if ids:
            shown = ", ".join(ids)
            lines.append(f"  {s + ':':10} {len(ids)} ({shown})")
        else:
            lines.append(f"  {s + ':':10} 0")
    lines.append("")
    a = report["anomalies"]
    lines.append("Pipeline anomalies:")
    anomaly_mark = len(lines)
    if a["zero_complete"]:
        lines.append("  - 0 terminal dispositions ever AND ACTIVE>0 (close-loop not walked)")
    elif a["complete_closed"] == 0 and a["folded"] > 0:
        lines.append(f"  - 0 COMPLETE/CLOSED, but {a['folded']} FOLDED (close-loop walked via merger, not completion)")
    if a["past_target"]:
        lines.append(f"  - {len(a['past_target'])} past-target (Loading Dock): {', '.join(a['past_target'])}")
    if a["unscaffolded"]:
        names = ", ".join(u["proposal"] for u in a["unscaffolded"])
        lines.append(f"  - {len(a['unscaffolded'])} approved-but-unscaffolded: {names}")
    if a["status_mismatches"]:
        items = "; ".join(f"{m['proposal']} ({m['lag']})" for m in a["status_mismatches"])
        lines.append(f"  - {len(a['status_mismatches'])} proposal-header lags (CIS-007): {items}")
    if a["stale"]:
        items = ", ".join(f"{s['id']} ({s['age_days']}d)" for s in a["stale"])
        lines.append(f"  - {len(a['stale'])} stale (>={STALE_DAYS}d no commit): {items}")
    if a["cis009"]:
        by_warn = {}
        for w in a["cis009"]:
            by_warn.setdefault(w["warn"], []).append(w["id"])
        for warn, ids in by_warn.items():
            lines.append(f"  - CIS-009 {warn}: {len(ids)} ({', '.join(ids)})")
    if len(lines) == anomaly_mark:  # nothing emitted above (incl. the folded nuance)
        lines.append("  - none")
    lines.append("")
    sh = report["shape"]
    lo, hi = sh["maintain_spine_band"]
    band_note = "in band" if sh["maintain_spine_in_band"] else f"outside D-IG-1 band {lo}-{hi}"
    lines.append(f"Portfolio shape (D-IG-1, report-only):")
    lines.append(f"  - Maintain spine: {sh['maintain_spine']} ACTIVE ({band_note})")
    if sh["achieve_aging"]:
        top = ", ".join(f"{x['id']} ({x['created_age_days']}d)" for x in sh["achieve_aging"][:5])
        lines.append(f"  - Achieve/untyped age-in-portfolio (grooming input, oldest first): {top}"
                     + (" …" if len(sh["achieve_aging"]) > 5 else ""))
    lines.append("")
    lines.append("Cohort detection:")
    if report["cohorts"]:
        for c in report["cohorts"]:
            lines.append(f"  - {c['family']} family ({c['span_days']}d span): {', '.join(c['members'])}")
    else:
        lines.append("  - none")
    lines.append("")
    if a.get("ceiling") is not None:
        over = a["over_ceiling"]
        cap_note = (f" — OVER declared ceiling {a['ceiling']} by {over} "
                    f"(CIS-008; L178 overrides recorded in INDEX.md prose; "
                    f"split re-baseline owed at grooming)" if over
                    else f" (within declared ceiling {a['ceiling']})")
    else:
        cap_note = " (no machine-readable ceiling declared in INDEX.md)"
    lines.append(f"Capacity:\n  - WIP: {report['wip']} ACTIVE initiatives{cap_note}")
    cr = a["capability_ratio"]
    if cr["state"] == "UNKNOWN":
        ratio_note = (f"UNKNOWN — {cr['untagged']} ACTIVE untagged "
                      f"(tagged: {cr['capability']} capability / {cr['governance']} governance); "
                      f"floor unverifiable until Class backfill")
    else:
        pct = f"{cr['ratio']:.0%}" if cr["ratio"] is not None else "n/a"
        ratio_note = (f"{cr['state']} — {cr['capability']}/{cr.get('achieve', report['wip'])} capability ({pct}) "
                      f"among Achieve-typed ACTIVE (D-27-A denominator; "
                      f"{cr.get('maintain_excluded', 0)} Maintain stewards excluded) "
                      f"vs >=1/3 floor (v3.22 D-2, gh#1655; re-spec 2026-07-18)")
    lines.append(f"  - Capability ratio (governing control): {ratio_note}")
    ec = report["anomalies"].get("ec_tick_state") or {}
    if ec.get("total"):
        worst = " ".join(f"{r['id'].replace('INIT-','')}:{r['ticked']}/{r['total']}" for r in ec.get("rows", [])[:6])
        lines.append(f"  - EC tick-state (CIS-010, maintained signal): {ec['state']} — "
                     f"{ec['ticked']}/{ec['total']} ticked across {len(ec.get('rows', []))} ACTIVE Achieve "
                     f"({worst}{' …' if len(ec.get('rows', []))>6 else ''})"
                     + (" — decorative-EC-layer warning, L1189/C-27-11" if ec["state"]=="WARN" else ""))
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
