#!/usr/bin/env python3
"""Archetype register parity check — four populations, one role identifier.

The archetype identifier is written in four places and arbitrated in none:

  1. REGISTER   ../aget/specs/ARCHETYPE_SKILLS_INDEX.yaml -> archetypes:
                the authoritative enumeration (AUDIT_archetype_registry_resolution_2026-08-07 §1)
  2. CONSUMER   ../aget/verification/validate_archetype_skills.py -> ARCHETYPE_EXTRAS
                the mapping that actually RUNS in template validation
  3. TEMPLATES  ../template-*/ directory names
                what validate_archetype_skills.py derives a role from (archetype_of(dir))
  4. DECLARED   fleet seats' .aget/version.json | .aget/identity.json "archetype"
                resolved through the fleet register's location: fields, NEVER a path glob

Divergence between (1) and (2) means the register that DECIDES and the instrument that
RUNS hold different populations. Nothing detected that until this check existed.

Recommendation 3 of AUDIT_archetype_registry_resolution_2026-08-07, carried unexecuted
in docs/HANDOFF_saturday_window_2026-08-15.md (A-1) for 22 days.

Scope: this instrument reports the four populations it can reach and emits UNAVAILABLE
for any it cannot (L1342 — an absence claim carries its search contract). It does NOT
repair; registering an archetype is a canonical specs/ write (/aget-enhance-spec, L644)
under the L735 window.

Usage:
    python3 scripts/check_archetype_register_parity.py
    python3 scripts/check_archetype_register_parity.py --json
    python3 scripts/check_archetype_register_parity.py --self-test

Exit codes: 0 parity (or all-UNAVAILABLE with nothing to compare), 1 divergence, 2 error.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("ERROR: PyYAML required", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
CANONICAL = REPO.parent / "aget"

REGISTER_PATH = CANONICAL / "specs" / "ARCHETYPE_SKILLS_INDEX.yaml"
CONSUMER_PATH = CANONICAL / "verification" / "validate_archetype_skills.py"
TEMPLATE_GLOB = "template-*"
# Fleet register location is operator-specific and is NOT hardcoded here.
# Set AGET_FLEET_REGISTER to the authoritative FLEET_STATE.yaml for your fleet.
# Absent or unset, population 4 reports UNAVAILABLE rather than guessing -- a path
# glob is not an acceptable substitute (see read_declared).
_FLEET_REGISTER_ENV = "AGET_FLEET_REGISTER"
FLEET_REGISTER = (
    Path(os.path.expanduser(os.environ[_FLEET_REGISTER_ENV]))
    if os.environ.get(_FLEET_REGISTER_ENV)
    else None
)

UNAVAILABLE = "UNAVAILABLE"


def _norm(value):
    """Normalize a role identifier for comparison: case and separator folded.

    Case and separator variation is reported separately as a distinct finding --
    it is a vocabulary-control defect, not a population divergence.
    """
    return value.strip().lower().replace("_", "-")


def read_register(path=REGISTER_PATH):
    """Population 1: the authoritative archetypes: block."""
    if not path.exists():
        return UNAVAILABLE, f"register not found at {path}"
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception as exc:
        return UNAVAILABLE, f"register unparseable: {exc}"
    block = (doc or {}).get("archetypes")
    if not isinstance(block, dict):
        return UNAVAILABLE, "register has no archetypes: mapping"
    return sorted(block.keys()), None


def read_consumer(path=CONSUMER_PATH):
    """Population 2: ARCHETYPE_EXTRAS, the mapping the validator actually runs."""
    if not path.exists():
        return UNAVAILABLE, f"consumer not found at {path}"
    src = path.read_text()
    match = re.search(r"ARCHETYPE_EXTRAS\s*=\s*\{(.*?)\n\}", src, re.S)
    if not match:
        return UNAVAILABLE, "ARCHETYPE_EXTRAS literal not found"
    keys = re.findall(r'["\']([A-Za-z0-9_\-]+)["\']\s*:', match.group(1))
    if not keys:
        return UNAVAILABLE, "ARCHETYPE_EXTRAS parsed but empty"
    return sorted(set(keys)), None


def read_templates(root=None):
    """Population 3: template directory names, the role source archetype_of() uses."""
    root = root or CANONICAL.parent
    if not root.exists():
        return UNAVAILABLE, f"template root not found at {root}"
    names = []
    for entry in sorted(root.glob(TEMPLATE_GLOB)):
        if not entry.is_dir():
            continue
        name = entry.name[len("template-"):]
        for suffix in ("-aget", "-AGET"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
        names.append(name)
    if not names:
        return UNAVAILABLE, f"no {TEMPLATE_GLOB} directories under {root}"
    return sorted(set(names)), None


def read_declared(register=FLEET_REGISTER):
    """Population 4: archetypes declared by live seats.

    Seats are resolved through the fleet register's location: fields. A path glob is
    NOT an acceptable substitute -- it is blind to portfolio-nested seats and reaches
    templates and non-seat directories (checklist point 11).
    """
    if register is None:
        return UNAVAILABLE, (
            f"no fleet register configured; set {_FLEET_REGISTER_ENV} to your "
            "FLEET_STATE.yaml to enable population 4"
        ), []
    if not register.exists():
        return UNAVAILABLE, "fleet register not found at the configured path", []
    try:
        doc = yaml.safe_load(register.read_text())
    except Exception as exc:
        return UNAVAILABLE, f"fleet register unparseable: {exc}", []
    fleet = (doc or {}).get("fleet")
    if not isinstance(fleet, dict):
        return UNAVAILABLE, "fleet register has no fleet: mapping", []

    values, undeclared = [], []
    for portfolio in fleet.values():
        for agent in (portfolio or {}).get("agents") or []:
            if agent.get("lifecycle_signal") == "archived":
                continue
            location = os.path.expanduser(agent.get("location") or "")
            if not location or not os.path.isdir(location):
                undeclared.append((agent.get("agent_name"), "location unreachable"))
                continue
            found = None
            for rel in (".aget/version.json", ".aget/identity.json"):
                candidate = Path(location) / rel
                if not candidate.exists():
                    continue
                try:
                    value = json.loads(candidate.read_text()).get("archetype")
                except Exception:
                    continue
                if value:
                    found = value
                    break
            if found:
                values.append(found)
            else:
                undeclared.append((agent.get("agent_name"), "no archetype declared"))
    if not values:
        return UNAVAILABLE, "no seat resolved an archetype", undeclared
    return sorted(values), None, undeclared


def compare(register, consumer, templates, declared):
    """Build the finding set. Only populations that are lists participate."""
    findings = []
    available = {
        name: pop
        for name, pop in (
            ("register", register),
            ("consumer", consumer),
            ("templates", templates),
            ("declared", declared),
        )
        if pop != UNAVAILABLE
    }

    if "register" not in available:
        return findings, available  # nothing to arbitrate against

    reg = {_norm(v) for v in available["register"]}

    for name in ("consumer", "templates", "declared"):
        if name not in available:
            continue
        other = {_norm(v) for v in available[name]}
        extra = sorted(other - reg)
        missing = sorted(reg - other)
        if extra:
            findings.append(
                {
                    "kind": "unregistered",
                    "population": name,
                    "values": extra,
                    "detail": f"{name} holds {len(extra)} role(s) absent from the register",
                }
            )
        if missing and name == "consumer":
            # Only the consumer is expected to cover the register; templates and
            # declared seats are legitimately sparse subsets.
            findings.append(
                {
                    "kind": "unimplemented",
                    "population": name,
                    "values": missing,
                    "detail": f"register holds {len(missing)} role(s) the consumer does not map",
                }
            )

    # Vocabulary control: same role, different spelling, within any one population.
    for name, pop in available.items():
        buckets = {}
        for value in pop:
            buckets.setdefault(_norm(value), set()).add(value)
        collisions = {k: sorted(v) for k, v in buckets.items() if len(v) > 1}
        if collisions:
            findings.append(
                {
                    "kind": "case_collision",
                    "population": name,
                    "values": collisions,
                    "detail": f"{name} spells {len(collisions)} role(s) more than one way",
                }
            )
    return findings, available


def run(as_json=False):
    register, reg_err = read_register()
    consumer, con_err = read_consumer()
    templates, tpl_err = read_templates()
    declared, dec_err, undeclared = read_declared()

    findings, available = compare(register, consumer, templates, declared)
    unavailable = {
        name: err
        for name, err in (
            ("register", reg_err),
            ("consumer", con_err),
            ("templates", tpl_err),
            ("declared", dec_err),
        )
        if err
    }

    status = "DIVERGENT" if findings else ("PARITY" if available else "UNAVAILABLE")
    result = {
        "status": status,
        "populations": {
            name: (pop if pop != UNAVAILABLE else UNAVAILABLE)
            for name, pop in (
                ("register", register),
                ("consumer", consumer),
                ("templates", templates),
                ("declared", declared),
            )
        },
        "counts": {
            name: (len(pop) if pop != UNAVAILABLE else UNAVAILABLE)
            for name, pop in (
                ("register", register),
                ("consumer", consumer),
                ("templates", templates),
                ("declared", declared),
            )
        },
        "findings": findings,
        "unavailable": unavailable,
        "seats_without_archetype": undeclared,
        "authority": str(REGISTER_PATH),
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Archetype Register Parity ===")
        print(f"authority: {REGISTER_PATH}")
        for name in ("register", "consumer", "templates", "declared"):
            count = result["counts"][name]
            print(f"  {name:<10} {count}")
        for name, err in unavailable.items():
            print(f"  ! {name}: UNAVAILABLE — {err}")
        if not findings:
            print("\nPARITY — no divergence across the reachable populations.")
        else:
            print(f"\nDIVERGENT — {len(findings)} finding(s):")
            for f in findings:
                print(f"  [{f['kind']}] {f['detail']}")
                print(f"      {f['values']}")
        if undeclared:
            print(f"\nseats declaring no archetype ({len(undeclared)}):")
            for name, why in undeclared:
                print(f"  {name}: {why}")
        print(
            "\nNote: this instrument reports only. Registering an archetype is a "
            "canonical specs/ write (/aget-enhance-spec, L644) under the L735 window."
        )
    return 1 if findings else 0


def self_test():
    """Two-polarity falsifiers: a divergence MUST flag, and parity MUST NOT.

    A check that only ever fires on real data is untested in the direction that
    matters (L1439 — falsify the FAIL path, and the PASS path, or it isn't tested).
    """
    cases = []

    # Polarity 1 (positive control): consumer holds a role the register does not.
    f, _ = compare(["worker", "advisor"], ["worker", "advisor", "ghost"], UNAVAILABLE, UNAVAILABLE)
    cases.append(("divergence flags", any(x["kind"] == "unregistered" for x in f)))

    # Polarity 2 (negative control): aligned populations must NOT flag.
    f, _ = compare(["worker", "advisor"], ["worker", "advisor"], UNAVAILABLE, UNAVAILABLE)
    cases.append(("parity is silent", f == []))

    # Register holds a role the consumer does not implement.
    f, _ = compare(["worker", "advisor"], ["worker"], UNAVAILABLE, UNAVAILABLE)
    cases.append(("unimplemented flags", any(x["kind"] == "unimplemented" for x in f)))

    # Case collision is detected as its own finding, not as a divergence.
    f, _ = compare(["worker"], UNAVAILABLE, UNAVAILABLE, ["worker", "Worker"])
    cases.append(("case collision flags", any(x["kind"] == "case_collision" for x in f)))

    # A sparse declared population must NOT be reported as unimplemented.
    f, _ = compare(["worker", "advisor", "analyst"], UNAVAILABLE, UNAVAILABLE, ["worker"])
    cases.append(("sparse declared is not a defect", f == []))

    # Separator variants fold: research_engineer == research-engineer.
    f, _ = compare(["research-engineer"], ["research_engineer"], UNAVAILABLE, UNAVAILABLE)
    cases.append(("separator folds", f == []))

    # UNAVAILABLE register yields no findings rather than a false parity claim.
    f, avail = compare(UNAVAILABLE, ["worker"], UNAVAILABLE, UNAVAILABLE)
    cases.append(("no register = no arbitration", f == [] and "register" not in avail))

    failed = [name for name, ok in cases if not ok]
    for name, ok in cases:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if failed:
        print(f"\nSELF-TEST FAILED: {failed}")
        return 1
    print(f"\nSELF-TEST PASS ({len(cases)}/{len(cases)}) — both polarities exercised.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--self-test", action="store_true", help="run two-polarity falsifiers")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    return run(as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
