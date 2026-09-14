#!/usr/bin/env python3
"""Inventory check-class emission sites and wiring without claiming behavioral compliance.

Source inspection establishes syntax, not the subject reach or discriminating
power of a runtime predicate. Unmeasured per-site conformance remains UNAVAILABLE;
one checked constructor elsewhere in a file never certifies its other paths.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

INSTRUMENT, NOT_INSTRUMENT, UNAVAILABLE = "INSTRUMENT", "NOT-INSTRUMENT", "UNAVAILABLE"
CHECKED = {"yes", "no", "passed", "failed", "unknown", "unavailable", "inert"}


def _walk(root):
    files = {}
    failures = []
    visited = set()

    def visit(p):
        rel = str(p.relative_to(root))
        try:
            s = p.lstat()
        except OSError as exc:
            failures.append(f"{rel}: lstat failed: {exc}")
            return
        if stat.S_ISLNK(s.st_mode):
            try:
                q = p.resolve(strict=True)
                q.relative_to(root)
            except (OSError, ValueError):
                failures.append(f"{rel}: symlink escapes population or is dangling")
                return
            failures.append(f"{rel}: symlink entry is not followed")
            return
        if stat.S_ISDIR(s.st_mode):
            key = (s.st_dev, s.st_ino)
            if key in visited:
                return
            visited.add(key)
            if s.st_mode & 0o500 != 0o500:
                failures.append(f"{rel or '.'}: directory lacks owner read/traverse permission")
                return
            try:
                with os.scandir(p) as it:
                    children = sorted((Path(e.path) for e in it), key=lambda x: x.name)
            except OSError as exc:
                failures.append(f"{rel or '.'}: enumeration failed: {exc}")
                return
            for c in children:
                visit(c)
        elif stat.S_ISREG(s.st_mode):
            if p.name.startswith("check_") and p.suffix == ".py":
                files.setdefault((s.st_dev, s.st_ino), p)
        elif p.name.startswith("check_") and p.suffix == ".py":
            failures.append(f"{rel}: unsupported instrument entry type")

    visit(root)
    return sorted(files.values(), key=lambda p: str(p.relative_to(root))), sorted(set(failures))


def _analyse(path, root):
    rel = str(path.relative_to(root))
    try:
        if not path.stat().st_mode & 0o400:
            raise PermissionError("owner-read bit is not set")
        text = path.read_text()
        tree = ast.parse(text)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return None, f"{rel}: unreadable/unparseable: {exc}"
    imports = False
    aliases = set()
    modules = set()
    calls = 0
    bare = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.endswith("warranted_verdict"):
            imports = True
            aliases.update(x.asname or x.name for x in n.names if x.name == "Verdict")
        elif isinstance(n, ast.Import):
            for x in n.names:
                if x.name == "warranted_verdict":
                    imports = True
                    modules.add(x.asname or x.name)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            b = n.func.value
            direct = isinstance(b, ast.Name) and b.id in aliases
            qualified = (
                isinstance(b, ast.Attribute)
                and isinstance(b.value, ast.Name)
                and b.value.id in modules
                and b.attr == "Verdict"
            )
            if (direct or qualified) and n.func.attr in CHECKED:
                calls += 1
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if (
                    isinstance(k, ast.Constant)
                    and k.value == "verdict"
                    and isinstance(v, ast.Constant)
                    and v.value in {"YES", "NO", "PASS", "FAIL"}
                ):
                    bare += 1
    # The declared population is check_*.py, regardless of comments or labels.
    # Return sites and output calls are candidates, not proof that a governed
    # proposition is emitted: wrappers and intermediate data need review too.
    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and node.value is not None:
            sites.append({"line": node.lineno, "kind": "return",
                          "expression": ast.unparse(node.value)})
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            sites.append({"line": node.lineno, "kind": "print",
                          "expression": ast.unparse(node)})
    sites.sort(key=lambda site: (site["line"], site["kind"]))
    problems = []
    if not imports:
        problems.append("does not import warranted_verdict")
    if not calls:
        problems.append("uses no checked Verdict constructor")
    if bare:
        problems.append(f"has {bare} bare definite verdict literal(s)")
    return {
        "path": rel,
        "classification": INSTRUMENT,
        "uses_checked_constructor": not problems,
        "checked_constructor_calls": calls,
        "problems": problems,
        "wiring_scope": "syntactic observations only; missing helper use is not an R1 violation",
        "candidate_emission_sites": sites,
        "conformance": "UNMEASURED",
        "analysis_limit": "source syntax does not establish per-site subject binding, reach, "
                          "affirming evidence and a discriminating predicate",
    }, None


def assess(scripts: Path) -> dict[str, Any]:
    scripts = scripts.resolve(strict=True)
    if not scripts.is_dir():
        raise NotADirectoryError(scripts)
    paths, failures = _walk(scripts)
    rows = []
    for p in paths:
        row, err = _analyse(p, scripts)
        if err:
            failures.append(err)
        elif row:
            rows.append(row)
    failures = sorted(set(failures))
    full = not failures
    instruments = [r for r in rows if r["classification"] == INSTRUMENT]
    unwired = [r["path"] for r in instruments if not r["uses_checked_constructor"]]
    overall = UNAVAILABLE
    limit = None if full else f"could not fully read subject {scripts}: " + "; ".join(failures)
    return {
        "population_root": str(scripts),
        "population_reached": full,
        "fully_read": full,
        "limit": limit,
        "unreached_subjects": failures,
        "classified_states": rows if full else None,
        "instruments": instruments if full else None,
        "observed_instruments": instruments,
        "unwired_instruments": unwired if full else None,
        "observed_unwired_instruments": unwired,
        "overall": overall,
        "discovery": "COMPLETE" if full else "INCOMPLETE",
        "conformance": "UNMEASURED",
        "analysis_limit": "per-site behavioral classification requires source-bound review; "
                          "constructor presence and file readability alone do not establish it",
        "classification": {
            "subject_bound": True,
            "subject_reached": full,
            "affirming_evidence": [r["path"] for r in instruments],
            "predicate_discriminating": None,
            "definite": False,
        },
    }


def exit_code(r):
    return 3 if not r["fully_read"] or r["conformance"] == "UNMEASURED" else 0


def render(r):
    out = [f"instrument verdict contract: {r['overall']}", f"population: {r['population_root']}"]
    out.append(f"discovery: {r['discovery']}; conformance: {r['conformance']}")
    out.append(f"ANALYSIS LIMIT: {r['analysis_limit']}")
    if r["limit"]:
        out += [f"LIMIT: {r['limit']}"] + [f"UNREACHED: {x}" for x in r["unreached_subjects"]]
    for x in r["observed_instruments"]:
        out.append(f"{'WIRED' if x['uses_checked_constructor'] else 'UNWIRED'} {x['path']}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts", type=Path, default=Path("scripts"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = assess(a.scripts)
    except (OSError, NotADirectoryError) as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(r, indent=1) if a.json else render(r))
    return exit_code(r)


if __name__ == "__main__":
    sys.exit(main())
