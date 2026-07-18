#!/usr/bin/env python3
"""
fleet_scope.py — resolve fleet scope from the authoritative registry, never from a path glob.

Why this exists
---------------
2026-07-16: multiple seats made fleet-scope claims about one artifact by globbing
directory paths — and every glob undercounted silently, each in the shape of its
own vantage point. A glob keyed to a path convention returns a plausible number,
not an error; agents living outside that convention are simply invisible to it.

The authoritative registry (the supervising seat's FLEET_STATE.yaml) was readable
the whole time. Nothing routed anyone to it for *reading*: its only citation was a
registration (write) step. This script is that missing read-route.

Usage
-----
    python3 scripts/fleet_scope.py --list
    python3 scripts/fleet_scope.py --has sops/SOP_permission_cleanup.md
    python3 scripts/fleet_scope.py --lacks scripts/permission_cleanup.py
    python3 scripts/fleet_scope.py --resolves scripts/health_check.py:SOP_permission_cleanup:sops/SOP_permission_cleanup.md
    python3 scripts/fleet_scope.py --diverge scripts/record_invocation.py
    python3 scripts/fleet_scope.py --has sops/SOP_permission_cleanup.md --json

Refs: gh#1813 (meta-invariant family), FLEET_STATE_SPEC v1.0 (supervising seat).
"""

import argparse
import hashlib
import json
import os
import pathlib
import sys

def _find_registry() -> pathlib.Path:
    """Resolve FLEET_STATE.yaml: env override, else discover under ~/github.

    (Globbing to LOCATE the one registry file is not the anti-pattern this
    script exists to kill — globbing to ENUMERATE AGENTS is.)
    """
    env = os.environ.get("AGET_FLEET_STATE")
    if env:
        return pathlib.Path(os.path.expanduser(env))
    hits = sorted(pathlib.Path(os.path.expanduser("~/github")).glob("*/.aget/fleet/FLEET_STATE.yaml"))
    if hits:
        return hits[0]
    return pathlib.Path(os.path.expanduser("~/github/FLEET_STATE.yaml"))


REGISTRY = _find_registry()


def load_agents(registry: pathlib.Path):
    """Return [(name, path)] for every agent with a resolvable location in the registry."""
    try:
        import yaml
    except ImportError:
        sys.exit("fleet_scope: PyYAML required (pip install pyyaml)")
    if not registry.is_file():
        sys.exit(
            f"fleet_scope: registry not found at {registry}\n"
            "  This script's whole premise is that the registry is authoritative.\n"
            "  Do NOT fall back to a path glob — that is the defect this exists to prevent.\n"
            "  Locate the registry and pass --registry, or fix the path here."
        )
    data = yaml.safe_load(registry.read_text())

    found = []

    def walk(node):
        if isinstance(node, dict):
            if "location" in node or "path" in node:
                found.append(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)

    agents = []
    for rec in found:
        loc = str(rec.get("location") or rec.get("path"))
        p = pathlib.Path(os.path.expanduser(loc.replace("~", "~")))
        p = pathlib.Path(os.path.expanduser(loc))
        agents.append((rec.get("name") or p.name, p))
    return agents


def md5(p: pathlib.Path):
    return hashlib.md5(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=pathlib.Path, default=REGISTRY)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="list every agent + location")
    g.add_argument("--has", metavar="REL", help="seats holding REL")
    g.add_argument("--lacks", metavar="REL", help="seats lacking REL")
    g.add_argument("--diverge", metavar="REL", help="seats holding REL, grouped by md5 (shadow-channel detector)")
    g.add_argument(
        "--resolves",
        metavar="FILE:NEEDLE:REFERENT",
        help="L211 invariant: seats where FILE contains NEEDLE but REFERENT is absent",
    )
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    agents = load_agents(a.registry)
    absent = [(n, p) for n, p in agents if not p.exists()]
    live = [(n, p) for n, p in agents if p.exists()]
    out = {"registry": str(a.registry), "agents": len(agents), "resolvable": len(live), "unresolvable": len(absent)}

    if a.list:
        rows = [{"name": n, "path": str(p), "exists": p.exists()} for n, p in agents]
        out["seats"] = rows
        if not a.json:
            print(f"FLEET_STATE: {len(agents)} agents ({len(live)} resolvable, {len(absent)} not)")
            for r in rows:
                print(f"  {'ok ' if r['exists'] else 'MISS'}  {r['name']:<36} {r['path']}")
            return
    elif a.has or a.lacks:
        rel = a.has or a.lacks
        hit = [n for n, p in live if (p / rel).exists()]
        miss = [n for n, p in live if not (p / rel).exists()]
        want_hit = bool(a.has)
        sel = hit if want_hit else miss
        out.update({"artifact": rel, "holding": len(hit), "lacking": len(miss), "selected": sel})
        if not a.json:
            print(f"artifact: {rel}")
            print(f"  holding: {len(hit)}/{len(live)}   lacking: {len(miss)}/{len(live)}")
            for n in sel:
                print(f"    {'HAS ' if want_hit else 'LACKS'}  {n}")
            return
    elif a.diverge:
        rel = a.diverge
        groups = {}
        for n, p in live:
            f = p / rel
            if f.is_file():
                groups.setdefault(md5(f), []).append(n)
        out.update({"artifact": rel, "holding": sum(len(v) for v in groups.values()), "distinct_versions": len(groups)})
        out["groups"] = [{"md5": k[:8], "seats": v} for k, v in groups.items()]
        if not a.json:
            tot = sum(len(v) for v in groups.values())
            print(f"artifact: {rel}")
            print(f"  held by {tot}/{len(live)} seats in {len(groups)} distinct version(s)")
            if len(groups) > 1:
                print(f"  ** DIVERGENT ** {len(groups)} versions across {tot} seats — shadow-channel signature")
            for k, v in sorted(groups.items(), key=lambda x: -len(x[1])):
                print(f"    {k[:8]}  x{len(v):<3} {', '.join(v)}")
            return
    elif a.resolves:
        try:
            fname, needle, referent = a.resolves.split(":", 2)
        except ValueError:
            sys.exit("--resolves expects FILE:NEEDLE:REFERENT")
        emits, dangling = [], []
        for n, p in live:
            f = p / fname
            if f.is_file() and needle in f.read_text(errors="ignore"):
                emits.append(n)
                if not (p / referent).exists():
                    dangling.append(n)
        out.update(
            {
                "control": fname,
                "needle": needle,
                "referent": referent,
                "emitting": len(emits),
                "dangling": len(dangling),
                "dangling_seats": dangling,
            }
        )
        if not a.json:
            print(f"L211 invariant: {fname} emits '{needle}' => {referent} must resolve")
            print(f"  emitting: {len(emits)}/{len(live)}   DANGLING: {len(dangling)}")
            for n in dangling:
                print(f"    DANGLING  {n}")
            return

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
