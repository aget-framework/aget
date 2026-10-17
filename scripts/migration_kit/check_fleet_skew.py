#!/usr/bin/env python3
"""check_fleet_skew.py — how far behind are this supervisor's members, against the limit this supervisor declared?

WHY THIS EXISTS
    The producer blocks its own next release cycle when its furthest-behind receiver is three published minor
    releases behind, and flags two behind. A remote supervisor had nothing of the kind for its own fleet. This tool is
    the receiver's version: it reads the supervisor's own register and each member's version file, and compares the
    floor with a reference version. The shape follows the Kubernetes version skew policy: the coordinator does not move
    further ahead while members are already too far behind it.

REFERENCE VERSION (first found wins)
    --reference VERSION; else the migration target (AGET_MIGRATION_TO or "to" in .aget/migration_target.json); else
    this supervisor's own .aget/version.json. Before Wave 0 the target is the release about to be adopted, so a
    BLOCKED verdict means: bring the floor members up before the supervisor upgrades.

LIMITS
    From adoption_policy.py: skew.blocked_at (default 3) and skew.flagged_at (default 2), each reported with its source
    (env / file / default). A supervisor that declared nothing is told the defaults were applied.

RULES THIS TOOL KEEPS
    1. Members come from the register (.aget/fleet/FLEET_STATE.yaml), never from a directory glob. A register entry
       without a name or a location is reported as malformed and makes the verdict UNAVAILABLE; it is never dropped.
    2. A member's version is read from <location>/.aget/version.json directly, so a member nested inside a larger
       repository reads correctly. A relative location resolves against the supervisor's repository root.
    3. Distance counts PUBLISHED minor releases, from the framework clone's tag list (the clone needs its tags:
       `git fetch --tags`). A member below the ladder is OFF-LADDER, which blocks: it is worse than any finite distance.
    4. A member whose version cannot be read is reported, never scored as current. If any member is unreadable and no
       readable member is already over the limit, the verdict is UNAVAILABLE, not WITHIN-BOUND.
    5. Members whose register status is not "active" are listed as excluded, never silently dropped. The supervisor
       itself (its own path or its own agent name) is the reference, not a member, and is reported as skipped.
    6. A member ahead of the reference is listed as AHEAD; it is not counted as converged.
    7. Every member at the floor is named.

Usage
-----
    python3 scripts/migration_kit/check_fleet_skew.py [--json] [--register PATH] [--reference VERSION] [--framework PATH]

Exit codes: 0 WITHIN-BOUND, 1 BLOCKED, 2 UNAVAILABLE.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTER = ROOT / ".aget" / "fleet" / "FLEET_STATE.yaml"
_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def _load(name, path):
    # By path, not by name, as elsewhere in the kit.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AP = _load("kit_adoption_policy", HERE / "adoption_policy.py")
try:
    R = _load("kit_release_target", HERE / "release_target.py")
    R_ERROR = None
except Exception as exc:  # noqa: BLE001 — a bad migration_target.json must give UNAVAILABLE, not a traceback
    R, R_ERROR = None, f"release target unreadable ({type(exc).__name__}: {exc})"


def _path(p) -> Path:
    return Path(os.path.expanduser(str(p)))


def _same(a: Path, b: Path) -> bool:
    try:
        return os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve()))
    except OSError:
        return False


def parse_minor(version: str | None) -> tuple[int, int] | None:
    """(major, minor) of a strict X.Y.Z version; None for anything else (a malformed version is unreadable)."""
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", (version or "").strip()) if isinstance(version, str) else None
    return (int(m.group(1)), int(m.group(2))) if m else None


def published_minors(framework: Path) -> tuple[list[tuple[int, int]] | None, str | None]:
    """(ordered distinct (major, minor) pairs from the framework clone's tags, reason when unavailable)."""
    if shutil.which("git") is None:
        return None, "git is not installed or not on PATH"
    try:
        out = subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "-C", str(framework), "tag", "--list"],
                             capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"git could not run at {framework} ({type(exc).__name__})"
    if out.returncode != 0:
        return None, f"{framework} is not a readable git clone of the framework"
    seen = {(int(m.group(1)), int(m.group(2))) for m in (_TAG.match(t.strip()) for t in out.stdout.splitlines()) if m}
    if not seen:
        return None, f"no release tags at {framework} (fetch them: git -C {framework} fetch --tags)"
    return sorted(seen), None


def _version_file(location: Path) -> dict | None:
    try:
        data = json.loads((location / ".aget" / "version.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def read_version(location: Path) -> str | None:
    d = _version_file(location)
    v = d.get("aget_version") if d else None
    return v if isinstance(v, str) else None


def register_members(register: Path, root: Path) -> tuple[list[dict] | None, list[str], str | None]:
    """(members [{name, location, status}], malformed entry descriptions, reason when unreadable)."""
    try:
        import yaml
    except ImportError:
        return None, [], "PyYAML is not installed (python3 -m pip install -r scripts/migration_kit/requirements.txt)"
    try:
        data = yaml.safe_load(register.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return None, [], f"register unreadable at {register} ({type(exc).__name__})"
    fleet = data.get("fleet") if isinstance(data, dict) else None
    if not isinstance(fleet, dict) or not fleet:
        return None, [], f"register at {register} has no 'fleet' section"
    out, bad = [], []
    for pname, pf in fleet.items():
        if not isinstance(pf, dict):
            bad.append(f"portfolio {pname}: not a mapping")
            continue
        agents = pf.get("agents")
        if agents is None:                             # a portfolio with no agents (for example an archived one)
            continue
        entries = (list(agents.items()) if isinstance(agents, dict)
                   else [(None, a) for a in agents] if isinstance(agents, list) else None)
        if entries is None:
            bad.append(f"{pname}: 'agents' is neither a list nor a mapping")
            continue
        for key, a in entries:
            if not isinstance(a, dict):
                bad.append(f"{pname}: entry {key or a!r} is not a mapping")
                continue
            name = a.get("agent_name") or key
            loc = a.get("location")
            if not name or not loc:
                bad.append(f"{pname}: entry {name or '(no name)'} has no {'location' if name else 'agent_name'}")
                continue
            p = _path(loc)
            out.append({"name": str(name), "location": str(p if p.is_absolute() else (root / p)),
                        "status": str(a.get("status") or "active").strip().lower()})
    return out, bad, None


def evaluate(register: Path = REGISTER, reference: str | None = None, framework: Path | None = None,
             root: Path = ROOT, env: dict | None = None) -> dict:
    root = _path(root)
    rep: dict = {"verdict": "UNAVAILABLE", "register": str(register), "members": [], "excluded": [], "unreadable": [],
                 "malformed": [], "ahead": [], "skipped_self": [], "floor": None, "flagged": []}
    try:
        pol = AP.load(root, env=env)
    except AP.PolicyError as exc:
        rep["unavailable_reason"] = f"adoption policy invalid: {exc}"
        return rep
    blocked_at = pol["policy"]["skew"]["blocked_at"]
    flagged_at = pol["policy"]["skew"]["flagged_at"]
    rep["limits"] = {"blocked_at": blocked_at, "flagged_at": flagged_at,
                     "source": {"blocked_at": pol["sources"]["skew.blocked_at"],
                                "flagged_at": pol["sources"]["skew.flagged_at"]}}
    rep["defaults_applied"] = [k for k in ("skew.blocked_at", "skew.flagged_at") if pol["sources"][k] == "default"]
    if R is None and (framework is None or reference is None):
        rep["unavailable_reason"] = R_ERROR
        return rep

    framework = _path(framework) if framework else (R.framework_root() / "aget")
    ladder, why = published_minors(framework)
    if not ladder:
        rep["unavailable_reason"] = why
        return rep
    rep["published_minors"] = [f"{a}.{b}" for a, b in ladder]

    if reference is None:
        if R.TO != R.UNSET:
            reference, rep["reference_source"] = R.TO, "migration target"
        else:
            reference, rep["reference_source"] = read_version(root), "this supervisor's own version"
    else:
        rep["reference_source"] = "--reference"
    rep["reference"] = reference
    ref_minor = parse_minor(reference)
    if ref_minor is None or ref_minor not in ladder:
        rep["unavailable_reason"] = f"reference version {reference!r} is not a published release"
        return rep

    members, bad, why = register_members(_path(register), root)
    if members is None:
        rep["unavailable_reason"] = why
        return rep
    rep["malformed"] = bad
    own = _version_file(root) or {}
    own_name = own.get("agent_name")
    for m in members:
        loc = Path(m["location"])
        if _same(loc, root) or (own_name and m["name"] == own_name):
            rep["skipped_self"].append(m["name"])     # the supervisor itself is the reference, not a member
            continue
        if m["status"] != "active":
            rep["excluded"].append({"name": m["name"], "status": m["status"]})
            continue
        ver = read_version(loc)
        minor = parse_minor(ver)
        row = {"name": m["name"], "version": ver, "behind": None, "off_ladder": False, "ahead": False}
        if ver is None or minor is None:
            rep["unreadable"].append(m["name"])
        elif minor not in ladder:
            row["off_ladder"] = True
        else:
            d = ladder.index(ref_minor) - ladder.index(minor)
            row["behind"] = max(0, d)
            if d < 0:
                row["ahead"] = True
                rep["ahead"].append(m["name"])
        rep["members"].append(row)

    rated = [r for r in rep["members"] if r["behind"] is not None]
    off = [r for r in rep["members"] if r["off_ladder"]]
    rep["flagged"] = sorted(r["name"] for r in rated if r["behind"] >= flagged_at) + sorted(r["name"] for r in off)
    incomplete = rep["unreadable"] or rep["malformed"]
    if off:
        rep["floor"] = {"behind": "OFF-LADDER", "names": sorted(r["name"] for r in off)}
        rep["verdict"] = "BLOCKED"
    elif rated:
        worst = max(r["behind"] for r in rated)
        rep["floor"] = {"behind": worst, "names": sorted(r["name"] for r in rated if r["behind"] == worst)}
        if worst >= blocked_at:
            rep["verdict"] = "BLOCKED"
        elif incomplete:
            rep["unavailable_reason"] = ("within the limit for readable members, but "
                                         + ("some members could not be read" if rep["unreadable"]
                                            else "the register has malformed entries"))
        else:
            rep["verdict"] = "WITHIN-BOUND"
    else:
        rep["unavailable_reason"] = ("no active member found in the register" if not rep["members"]
                                     else "no member declared a readable version")
    rep["converged"] = sum(1 for r in rated if r["behind"] == 0 and not r["ahead"])
    rep["in_fleet"] = len(rep["members"])
    return rep


def render(rep: dict) -> None:
    lim = rep.get("limits", {})
    print(f"fleet skew — register {rep['register']}")
    if lim:
        print(f"  limits   : blocked at {lim['blocked_at']} ({lim['source']['blocked_at']}), "
              f"flagged at {lim['flagged_at']} ({lim['source']['flagged_at']})")
        if rep.get("defaults_applied"):
            print("             no declared limit found; the producer defaults were applied")
    if rep.get("reference"):
        print(f"  reference: {rep['reference']} ({rep.get('reference_source')})")
    if rep.get("in_fleet") is not None:
        print(f"  converged: {rep.get('converged', 0)}/{rep['in_fleet']}")
    if rep.get("floor"):
        print(f"  floor    : {rep['floor']['behind']} behind — {', '.join(rep['floor']['names'])}")
    for key, label in (("flagged", "flagged"), ("ahead", "ahead of the reference"),
                       ("unreadable", "unreadable (not counted as current)"), ("malformed", "malformed register entries"),
                       ("skipped_self", "skipped (this supervisor)")):
        if rep.get(key):
            print(f"  {label}: {', '.join(rep[key])}")
    if rep.get("excluded"):
        print("  excluded : " + ", ".join(f"{e['name']} ({e['status']})" for e in rep["excluded"]))
    print(f"  VERDICT  : {rep['verdict']}" + (f" — {rep['unavailable_reason']}" if rep.get("unavailable_reason") else ""))
    if rep["verdict"] == "BLOCKED":
        print("  Do not start the next release's supervisor upgrade until the floor members are within the limit.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fleet version skew against the supervisor's declared limit.")
    ap.add_argument("--register", default=str(REGISTER))
    ap.add_argument("--reference", help="compare against this version instead of the target or own version")
    ap.add_argument("--framework", help="framework clone holding the release tags (default: framework root/aget)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rep = evaluate(_path(a.register), a.reference, _path(a.framework) if a.framework else None)
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        render(rep)
    return {"WITHIN-BOUND": 0, "BLOCKED": 1}.get(rep["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
