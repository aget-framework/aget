#!/usr/bin/env python3
"""
deploy_skill.py — Governed surgical skill deployer (C-22-01 / E1, v3.22).

Closes the universal-skills rollout stall (#1120/#1286: "one batched rollout
that stopped" — 15 universal skills uniformly absent from 10 of 13 templates).
The deploy half of the propagate-and-verify pair (paired with the C-22-04
freshness gate, Gate 3): propagation SHALL carry point-of-use verify.

Design (per VERSION_SCOPE C-22-01): per-skill filter · companion artifacts ·
dry-run · audit log · independent verify. Plus two governance properties the
stall taught us to encode IN the tool, not in a doc:

  - **Live gap re-derivation** (not the stale #1120 table): conformance is
    recomputed from the live template trees at run time (L1046 grep-before-assert;
    advisor template has since gained skills the #1120 snapshot lists as missing).
  - **L735 push-window guard**: `--apply` writes to public aget-framework
    template working trees; it REFUSES on Mon–Fri (weekend-only per L735/L983),
    so the deployer cannot be the vector that bypasses the window.

Usage:
  python3 scripts/deploy_skill.py --gap-report                 # live gap (read-only)
  python3 scripts/deploy_skill.py --skill aget-propose-actions # dry-run plan (default)
  python3 scripts/deploy_skill.py --skill X --target template-advisor-aget
  python3 scripts/deploy_skill.py --skill X --apply            # real deploy (L735-gated)
  python3 scripts/deploy_skill.py --self-test

Exit codes: 0 ok / 1 verify-failure or refused / 2 usage-or-env error.
"""

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLEET_ROOT = REPO_ROOT.parent  # siblings: template-*-aget live here
DEFAULT_SOURCE = FLEET_ROOT / "template-worker-aget" / ".claude" / "skills"  # conformant reference
AUDIT_LOG = REPO_ROOT / "workspace" / "skill_deploy_audit.jsonl"

# The 15 universal skills uniformly absent in the stalled rollout (#1120).
UNIVERSAL_SKILLS = [
    "aget-analyze-ontology", "aget-check-facts", "aget-check-initiative",
    "aget-close-session", "aget-create-briefing", "aget-create-rubric",
    "aget-describe-session", "aget-expand-ontology", "aget-open-session",
    "aget-process-observation", "aget-promote-issue", "aget-propose-actions",
    "aget-release-audit-specs", "aget-release-build", "aget-release-critique",
]


def template_dirs(root: Path):
    return sorted(d for d in root.glob("template-*") if (d / ".claude").exists() or d.is_dir())


def has_skill(template: Path, skill: str) -> bool:
    return (template / ".claude" / "skills" / skill / "SKILL.md").exists()


def gap_report(root: Path, universal=UNIVERSAL_SKILLS) -> dict:
    """Live re-derivation of per-template missing universal skills."""
    out = {}
    for t in template_dirs(root):
        if not (t / ".claude").exists():
            out[t.name] = {"structurally_absent": True, "missing": universal}
            continue
        missing = [s for s in universal if not has_skill(t, s)]
        out[t.name] = {"structurally_absent": False, "missing": missing}
    return out


def is_weekend(today: datetime.date) -> bool:
    return today.weekday() >= 5  # 5=Sat, 6=Sun


def plan(skill: str, source: Path, target: Path) -> dict:
    src = source / skill
    dst = target / ".claude" / "skills" / skill
    companions = sorted(p.name for p in src.glob("*")) if src.exists() else []
    return {
        "skill": skill, "source": str(src), "target": str(dst),
        "source_exists": src.exists(), "already_present": dst.exists(),
        "companion_artifacts": companions,
    }


def verify(target: Path, skill: str) -> bool:
    """Independent post-deploy verify: skill dir + SKILL.md present at target."""
    return (target / ".claude" / "skills" / skill / "SKILL.md").exists()


def audit(entry: dict):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def deploy(skill: str, source: Path, target: Path, apply: bool, today: datetime.date) -> dict:
    p = plan(skill, source, target)
    if not p["source_exists"]:
        return {**p, "action": "ERROR", "reason": "source skill not found"}
    if not apply:
        return {**p, "action": "DRY-RUN", "reason": "no write (default); pass --apply to deploy"}
    # --apply path: public aget-framework write → L735 push-window gate
    if not is_weekend(today):
        return {**p, "action": "REFUSED", "reason": f"L735: public template write is weekend-only (today={today:%A})"}
    dst = target / ".claude" / "skills" / skill
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / skill, dst, dirs_exist_ok=True)
    ok = verify(target, skill)  # independent verify
    entry = {"ts": today.isoformat(), "skill": skill, "source": p["source"],
             "target": p["target"], "verified": ok}
    audit(entry)
    return {**p, "action": "DEPLOYED" if ok else "VERIFY-FAILED", "verified": ok}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--gap-report", action="store_true", help="Live per-template missing-skill report (read-only)")
    ap.add_argument("--skill", default=None, help="Skill to deploy (per-skill filter)")
    ap.add_argument("--target", default=None, help="Single template dir name (default: all with the gap)")
    ap.add_argument("--source", default=str(DEFAULT_SOURCE), help="Source skills dir (conformant reference)")
    ap.add_argument("--apply", action="store_true", help="Actually deploy (L735 weekend-gated); default is dry-run")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    source = Path(args.source)
    today = datetime.date.today()

    if args.gap_report:
        rep = gap_report(FLEET_ROOT)
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            conformant = [t for t, v in rep.items() if not v["structurally_absent"] and not v["missing"]]
            print(f"=== universal-skill gap (live re-derivation, {today:%Y-%m-%d}) — {len(rep)} templates ===")
            print(f"Conformant: {len(conformant)}/{len(rep)}")
            for t, v in rep.items():
                if v["structurally_absent"]:
                    print(f"  {t}: STRUCTURALLY ABSENT (no .claude/)")
                elif v["missing"]:
                    print(f"  {t}: missing {len(v['missing'])} — {', '.join(v['missing'])}")
        return 0

    if not args.skill:
        print("ERROR: pass --gap-report or --skill <name>", file=sys.stderr)
        return 2
    if args.skill not in UNIVERSAL_SKILLS:
        print(f"WARN: {args.skill} is not in the universal-skill set (proceeding anyway)", file=sys.stderr)

    rep = gap_report(FLEET_ROOT)
    if args.target:
        targets = [FLEET_ROOT / args.target]
    else:
        targets = [FLEET_ROOT / t for t, v in rep.items()
                   if not v["structurally_absent"] and args.skill in v["missing"]]
    if not targets:
        print(f"No templates need {args.skill} (already universal, or only structurally-absent ones lack it).")
        return 0

    results = [deploy(args.skill, source, t, args.apply, today) for t in targets]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['action']}] {args.skill} -> {Path(r['target']).parent.parent.parent.name}"
                  f"  ({r.get('reason', 'verified=' + str(r.get('verified')))})")
    return 0 if all(r["action"] in ("DRY-RUN", "DEPLOYED") for r in results) else 1


def _self_test() -> int:
    """Deterministic dry-run + L735 guard + verify, in a temp fleet."""
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "template-worker-aget" / ".claude" / "skills" / "aget-propose-actions"
        src.mkdir(parents=True)
        (src / "SKILL.md").write_text("x")
        tgt = root / "template-advisor-aget"
        (tgt / ".claude" / "skills").mkdir(parents=True)
        source = root / "template-worker-aget" / ".claude" / "skills"

        # dry-run never writes
        r = deploy("aget-propose-actions", source, tgt, apply=False, today=datetime.date(2026, 6, 13))
        if r["action"] != "DRY-RUN" or verify(tgt, "aget-propose-actions"):
            fails.append(f"dry-run wrote or mislabelled: {r}")
        # weekday --apply is refused (L735)
        r = deploy("aget-propose-actions", source, tgt, apply=True, today=datetime.date(2026, 6, 12))  # Friday
        if r["action"] != "REFUSED":
            fails.append(f"weekday apply not refused (L735): {r}")
        # weekend --apply deploys + verifies
        global AUDIT_LOG
        saved = AUDIT_LOG
        AUDIT_LOG = root / "audit.jsonl"
        try:
            r = deploy("aget-propose-actions", source, tgt, apply=True, today=datetime.date(2026, 6, 13))  # Saturday
        finally:
            AUDIT_LOG = saved
        if r["action"] != "DEPLOYED" or not verify(tgt, "aget-propose-actions"):
            fails.append(f"weekend apply did not deploy+verify: {r}")
    if fails:
        print("SELF-TEST FAIL:\n  " + "\n  ".join(fails))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
