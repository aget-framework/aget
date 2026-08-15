#!/usr/bin/env python3
"""Actuator census — does every control have something that RUNS it?

THE EDGE THIS CHECKS
--------------------
`invoked-by`. Not "does the script exist" (it does), not "does it work" (it may),
but: **is anything in this repository going to run it without a human choosing to?**

WHY THIS EXISTS (root-cause analysis, 2026-07-26)
-------------------------------------------------
A single session surfaced 60+ defects. Every one was a missing EDGE, not a missing
node:

    orphaned script          -> no `invoked-by`
    dangling path reference  -> no `resolves-to`
    gate ordering fault      -> no `depends-on`
    control shipped unwired  -> no `actuated-by`
    issue done but still open-> no `closed-by`
    threshold never met      -> no `has-ever-passed`

Every artifact existed, was well-formed, was committed, and looked like progress.
What was missing was the relationship that made it real.

The proof is the counter-example. This repo models exactly ONE artifact
relationship and wires its check — the Skill Reliance Manifest (`declared` <->
`on disk`, validated at CI + wake-up). Its standing result is **52/52, 0 errors,
0 warnings**. Where the edge is modelled and actuated it is perfect; where it is
not, we found 29 orphaned scripts out of 104.

This script is the second edge, generalising the first.

THE CASE THAT FORCED IT
-----------------------
`check_requirements_ledger.py` (C-28-31) shipped as a BUILT, tested, Tier-1 row of
the release themed *"Make the gates fire"* — referenced only by its own test, the
plan, an L-doc, a session file and an audit brief. No hook. No battery. No wake-up.
It fired only if someone chose to run it. The cycle reproduced the root cause it
was created to fix, and nothing detected the difference between that row and the
two rows that were wired correctly.

WHAT COUNTS AS AN ACTUATOR
--------------------------
Something that runs the control WITHOUT an agent electing to:
  - a registered hook in `.claude/settings.json` (the only true actuator: the
    harness runs it regardless of intent)
  - a slot in `scripts/release_gate_battery.sh` (runs when the battery runs)
  - `wake_up.py` / `wind_down.py` (runs every session)
  - a test (runs in CI / the suite)

A mention in an SOP or a SKILL.md is NOT an actuator. It is an instruction to a
model, and compliance is a behaviour rather than a mechanism — which is the whole
finding.

Exit 0 = every control actuated | 1 = orphans found | 2 = usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Scripts whose NAME marks them as a control. A control asserts something about
# the world; an orphaned control asserts it to nobody.
#
# DEMOTED FROM GATE TO HINT, 2026-08-08. This tuple was the corpus predicate:
# `if not p.name.startswith(CONTROL_PREFIXES): continue`. Anything named otherwise
# never entered the census at all.
#
# Measured at the moment of demotion: scripts/*.py = 151, prefix-matched = 72,
# EXCLUDED = 79 — of which **50 assert a verdict** (`exit 1` / `FAIL` / `assert`).
# The excluded set included `close_authorization_guard.py`, `codex_git_guard.py`,
# `close_gate_check.py`, `capture_friction.py`, `deployment_monitor.py`. Two have
# "guard" in the name. They are controls by any behavioural test and were invisible
# to this census by construction.
#
# WHY THIS IS WORSE THAN A MISS, and why the fix is a removed predicate rather than
# a widened one. An excluded item is not a false negative. A false negative occupies
# a slot in the denominator and can be audited. An excluded item occupies no slot —
# not numerator, not denominator, not the orphan backlog — so it is strictly less
# visible than the failure this census exists to detect. (vp_of_ai, 2026-08-08.)
#
# A naming convention also drifts GENERATIVELY: it misses every future control whose
# author names it after its subject rather than its category. The gap grew without
# anyone acting.
#
# Error direction is chosen deliberately. Behavioural detection over-includes, and
# over-inclusion is this instrument's documented failure mode. That is the correct
# trade anyway: false positives occupy slots and can be adjudicated DOWN via
# NOT_A_CONTROL; exclusions cannot be adjudicated UP, because nobody sees them.
CONTROL_PREFIXES = ("check_", "validate_", "audit_", "verify_", "d71_", "goal_link_")

# Behavioural corpus predicate: does the script ASSERT a verdict about the world?
# This is the gate now; the name is only a hint that raises confidence.
_ASSERTS = re.compile(
    r"sys\.exit\(1\)|(?<![\w.])exit\(1\)|\breturn 1\b|[\"']FAIL[\"']|\bassert\s",
)

# Shell twin of _ASSERTS. A shell control asserts with `exit 1`, a `[FAIL]` marker,
# or `return 1` — `assert` is not shell, and `sys.exit` never appears.
_ASSERTS_SH = re.compile(
    r"\bexit\s+1\b|\breturn\s+1\b|\[FAIL\]|[\"']FAIL[\"']",
)


def _corpus():
    """Every file that could BE a control — `.py` and `.sh`, scripts/ and hooks/.

    EXTENSION PREDICATE REMOVED, 2026-08-13. The line was
    `sorted((ROOT / "scripts").glob("*.py"))`, and it is the 2026-08-08 lesson above
    surviving on a second axis: that fix removed the *name* predicate and left the
    *extension* predicate untouched, so an entire file class stayed excluded — and
    the argument for why that is worse than a miss is unchanged, word for word. An
    excluded item occupies no slot: not numerator, not denominator, not the orphan
    backlog.

    ASYMMETRY THIS CLOSES: `.sh` files were already read as ACTUATORS (see
    `_actuator_blob` / `_wired_commands`, which parse `release_gate_battery.sh` and
    `.claude/hooks/*.sh`) but never as SUBJECTS. A shell script could wire other
    controls and could never itself be found unwired.

    Measured at the moment of removal: scripts/*.py = 167, scripts/*.sh = 6,
    .claude/hooks/*.sh = 8. The `.sh` set contained TWO zero-caller controls
    (`check_template_conformance.sh`, `prepare_impact_aget_migration.sh`), one of
    which had been reporting `templates=13 failures=13` to nobody since its rename.
    The other known instance of this class, `.claude/hooks/delegated_mutation_guard.sh`
    (gh#2117), had to be found by hand — this census could not have surfaced it.
    """
    files = sorted((ROOT / "scripts").glob("*.py"))
    files += sorted((ROOT / "scripts").glob("*.sh"))
    files += sorted((ROOT / ".claude" / "hooks").glob("*.sh"))
    return files


# Adjudicated NON-controls: behaviourally assertive, deliberately NOT censused,
# WITH A STATED REASON. This is the residue the behavioural pass over-includes.
# An entry here is a claim under test, exactly like ORPHAN_EXEMPTIONS below.
NOT_A_CONTROL = {
    "aget_init.py": "scaffolder; its exit 1 is a setup failure, not a verdict about repo state",
    "deploy_skill.py": "deployer; exit 1 reports a failed copy, not a governance assertion",
}

# Deliberately unwired, WITH A STATED REASON. This exists so the census can tell
# "nobody thought about this" apart from "we thought about it and here is why" —
# silent absence and considered absence look identical otherwise, and treating
# them the same is what let 15 controls sit orphaned.
#
# An entry here is a claim under test: if the reason stops being true, the
# exemption is a lie the census now tells on your behalf. Re-read them.
ORPHAN_EXEMPTIONS = {
    "audit_citation_syntax.py":
        "28.6s fleet-wide census over 31 seats — 20x the next-slowest control. "
        "Wired into the per-release battery 2026-07-26 and REMOVED the same hour: "
        "it pushed the battery past 120s, and a battery too slow to run is a "
        "battery nobody runs — which is Root 1 exactly, recreated by the fix for "
        "Root 1. It is a periodic FLEET audit, not a release gate. Owed: a "
        "periodic-audit surface to host it. Until that exists, unwired ON PURPOSE.",
    "audit_voice_inherit.py":
        "Belongs to a live parallel session's voice-remediation arc (L1252: two "
        "sessions, one tree). Not this session's to wire.",
}

# Surfaces that actually cause execution, in descending strength.
ACTUATORS = {
    "hook": [".claude/settings.json"],
    # The battery, AND the validator registry the battery delegates to. Omitting
    # the second produced three false orphans on this census's own first run
    # (validate_changelogs / validate_content_sync / validate_project_plan are
    # all entries in validate_release_gate.py's VALIDATORS list). An actuator
    # census that cannot see one level of indirection manufactures orphans —
    # the same false-absence defect it exists to find, in itself, immediately.
    "battery": ["scripts/release_gate_battery.sh",
                "scripts/validate_release_gate.py",
                "scripts/check_release_completion.sh"],
    "session": ["scripts/wake_up.py", "scripts/wake_up_ext.py",
                "scripts/wind_down.py", "scripts/wind_down_ext.py"],
    "test": None,  # any file under tests/
}


def _actuator_blob() -> dict[str, str]:
    blob = {}
    for kind, paths in ACTUATORS.items():
        if kind == "test":
            texts = []
            for f in sorted((ROOT / "tests").glob("*.py")):
                try:
                    texts.append(f.read_text(errors="ignore"))
                except OSError:
                    pass
            blob[kind] = "\n".join(texts)
            continue
        texts = []
        for rel in paths:
            p = ROOT / rel
            if p.exists():
                try:
                    texts.append(p.read_text(errors="ignore"))
                except OSError:
                    pass
        blob[kind] = "\n".join(texts)
    # hooks referenced FROM settings.json also count — read their bodies
    hook_bodies = []
    for f in sorted((ROOT / ".claude" / "hooks").glob("*.sh")):
        try:
            hook_bodies.append(f.read_text(errors="ignore"))
        except OSError:
            pass
    blob["hook"] += "\n" + "\n".join(hook_bodies)
    return blob


def _wired_commands() -> dict[str, str]:
    """Extract HOW each control is actually invoked, not merely THAT it is named.

    Added 2026-07-26 after this census reported 45/45 actuated while
    `check_plan_sop_vtest_binding.py` was wired with NO ARGUMENTS and exited 2
    (usage error) on every battery run. It counted as actuated because its
    FILENAME appeared in an actuator surface. That is a documentary check on an
    execution property -- L1258's shape, inside the tool written to fix L1260.
    """
    cmds: dict[str, str] = {}
    battery = ROOT / "scripts" / "release_gate_battery.sh"
    if battery.exists():
        text = battery.read_text(errors="ignore")
        text = re.sub(r"\\\n\s*", " ", text)          # join line-continuations FIRST
        for m in re.finditer(r"^run_gate\s+\"[^\"]*\"\s+[01]\s+(.+)$", text, re.M):
            cmd = m.group(1).strip()
            f = re.search(r"scripts/([A-Za-z0-9_]+\.(?:py|sh))", cmd)
            if f:
                cmds[f.group(1)] = cmd
    return cmds


def _bears_load(name: str, cmd: str) -> tuple[bool, str]:
    """Invoke as wired and reject a USAGE error. A control that cannot parse its
    own arguments cannot fire, however well it is named.

    Short timeout on purpose: argparse failures are INSTANT. A timeout means the
    control got PAST argument parsing, which is all this checks.

    3s, not 12s. At 12s x 46 controls this census took minutes and hit the
    'too slow to run' trap -- the same one that made the contract suite
    structurally unpassable this morning. A check nobody runs protects nothing,
    so the cost of the check is part of whether it works.
    """
    import subprocess
    run = cmd.replace("$VER", "3.28.0").replace("${VER}", "3.28.0")
    try:
        r = subprocess.run(run, shell=True, capture_output=True, text=True,
                           cwd=str(ROOT), timeout=3)
    except subprocess.TimeoutExpired:
        return True, "runs (timed out past arg-parsing)"
    out = (r.stdout or "") + (r.stderr or "")
    if re.search(r"^usage:|error: the following arguments|error: provide|unrecognized arguments",
                 out, re.M):
        first = next((l for l in out.splitlines() if l.strip()), "")
        return False, f"USAGE ERROR as wired: {first[:70]}"
    return True, f"runs (exit {r.returncode})"


def census() -> tuple[list, list]:
    blob = _actuator_blob()
    wired = _wired_commands()
    controls, orphans = [], []
    unadjudicated = []
    for p in _corpus():
        # Corpus predicate: name-hint OR behavioural assertion. The name alone no
        # longer gates entry (see CONTROL_PREFIXES note).
        by_name = p.name.startswith(CONTROL_PREFIXES)
        asserts = _ASSERTS_SH if p.suffix == ".sh" else _ASSERTS
        try:
            by_behaviour = bool(asserts.search(p.read_text(errors="ignore")))
        except OSError:
            by_behaviour = False
        if not (by_name or by_behaviour):
            continue
        if p.name in NOT_A_CONTROL:
            continue
        # A behaviour-only candidate with no adjudication is the residue this fix
        # exists to surface. It FAILS rather than silently joining or leaving the
        # corpus — "the system reports until someone decides", not "someone must
        # remember to look".
        if by_behaviour and not by_name and p.name not in ORPHAN_EXEMPTIONS:
            unadjudicated.append(p.name)
        found = [k for k, text in blob.items() if p.name in text]
        # LOAD-BEARING TEST: named is not wired. If we know the exact invocation,
        # run it; a usage error demotes the control to orphaned regardless of how
        # many surfaces mention it.
        if found and p.name in wired:
            ok, why = _bears_load(p.name, wired[p.name])
            if not ok:
                controls.append((p.name, [f"NAMED-NOT-LOAD-BEARING: {why}"]))
                orphans.append(p.name)
                continue
        if not found and p.name in ORPHAN_EXEMPTIONS:
            controls.append((p.name, ["exempt"]))
            continue
        controls.append((p.name, found))
        if not found:
            orphans.append(p.name)
    return controls, orphans, unadjudicated


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="census every scripts/*.py, not just control-named ones")
    args = ap.parse_args()

    if args.all:
        global CONTROL_PREFIXES
        CONTROL_PREFIXES = ("",)

    controls, orphans, unadjudicated = census()
    total = len(controls)
    wired = total - len(orphans)

    if args.json:
        print(json.dumps({
            "total_controls": total, "actuated": wired, "orphans": orphans,
            "unadjudicated": unadjudicated,
            "edge": "invoked-by",
        }, indent=2))
        return 1 if (orphans or unadjudicated) else 0

    print("=" * 62)
    print("ACTUATOR CENSUS — edge: `invoked-by`")
    print("=" * 62)
    print(f"\n  controls found : {total}")
    print(f"  actuated       : {wired}")
    print(f"  ORPHANED       : {len(orphans)}")
    print(f"  UNADJUDICATED  : {len(unadjudicated)}  (behaviourally a control, not yet classified)\n")
    if unadjudicated:
        print("  These assert a verdict but carry no control-name and no adjudication.")
        print("  Classify each: wire it, add to ORPHAN_EXEMPTIONS, or add to NOT_A_CONTROL.")
        for n in unadjudicated:
            print(f"    ? {n}")
        print()

    for name, found in controls:
        if found:
            print(f"  ✅ {name:<44} {'+'.join(sorted(found))}")
    if orphans:
        print()
        for name in orphans:
            print(f"  ❌ {name:<44} NOTHING RUNS THIS")
        print("\n  An orphaned control asserts something to nobody. Wire it into")
        print("  the battery, a hook, wake-up, or a test — or delete it, because")
        print("  a control that never runs is documentation with a shebang.")
        return 1

    print("\n  ✅ every control has an actuator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
