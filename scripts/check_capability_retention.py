#!/usr/bin/env python3
"""Detect capability DELETION across a payload update. Not a lint check.

WHY THIS IS NOT A LINT CHECK
----------------------------
gh#2464 ask 3, verbatim: *"MERGE-as-overwrite plus a lint-only gate means capability deletion is
invisible at every layer."*

Each existing layer misses it for its own reason:

  byte-hash equality   compares the payload to the TAG it came from, so a deletion that shipped
                       is byte-identical to itself and passes.
  lint                 an overwritten file with a function removed is perfectly clean code.
  the test suite       only catches deletion of things the suite happens to exercise.

Nothing was asking the one question that matters on a MERGE-as-overwrite: *did this update
remove something a consumer could already call?* This does.

WHAT COUNTS AS A CAPABILITY
---------------------------
Surfaces a downstream consumer can bind to and would break on losing:

  * module-level `def` / `class` names (a caller imports them)
  * CLI flags declared via `add_argument("--flag")` (a script or CI job passes them)
  * subcommand/choice literals in `choices=[...]`
  * module-level assignments that read as constants (UPPER_SNAKE)

A name that was public and is gone is a REMOVAL. A name that was private (`_leading`) is
reported separately and does not fail: consumers were never entitled to it.

Read-only, and it never executes the payload -- it parses. Running a candidate payload to
find out what it exports is exactly the state-changing act a producer gate must not take.

USAGE
  check_capability_retention.py --before OLD_DIR --after NEW_DIR
  check_capability_retention.py --before OLD --after NEW --allow-removed removed.json
  check_capability_retention.py --before OLD --after NEW --json

EXIT CODES
  0  no public capability was removed
  1  a public capability was removed and is not in the allow-list
  2  a file could not be parsed on one side  (UNAVAILABLE, never a pass)
  3  inputs unusable
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


class InputError(Exception):
    pass


def capabilities_of(source: str) -> tuple[set[str], set[str]]:
    """(public, private) capability names in one module. Parsed, never executed."""
    tree = ast.parse(source)
    pub: set[str] = set()
    priv: set[str] = set()

    def record(name: str, kind: str) -> None:
        (priv if name.startswith("_") else pub).add(f"{kind}:{name}")

    # Module guards do not create a Python scope. Definitions/imported bindings
    # inside if/try/with still become consumer-visible module attributes.
    pending = list(tree.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            record(node.name, "def")
        elif isinstance(node, ast.ClassDef):
            record(node.name, "class")
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            for alias in node.names:
                if alias.name == "*":
                    raise ValueError("wildcard exports require provider resolution")
                record(alias.asname or alias.name, "reexport")
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id.isupper():
                    record(tgt.id, "const")
        else:
            pending.extend(child for child in ast.iter_child_nodes(node)
                           if isinstance(child, (ast.stmt, ast.ExceptHandler, ast.match_case)))
    # CLI surfaces, wherever they are declared in the module
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr == "add_argument":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    pub.add(f"flag:{arg.value}")
            for kw in node.keywords:
                if kw.arg == "choices" and isinstance(kw.value, (ast.List, ast.Tuple)):
                    for el in kw.value.elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            pub.add(f"choice:{el.value}")
    return pub, priv


def scan(root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]], list[str]]:
    pub: dict[str, set[str]] = {}
    priv: dict[str, set[str]] = {}
    unparsed: list[str] = []
    paths = []

    def visit(path):
        rel = str(path.relative_to(root))
        try:
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                if path.suffix == ".py" or path.is_dir():
                    unparsed.append(f"{rel}: symlink population is not traversed")
            elif stat.S_ISDIR(mode):
                if mode & 0o500 != 0o500:
                    raise PermissionError("directory lacks read/traverse permission")
                with os.scandir(path) as entries:
                    children = sorted(Path(entry.path) for entry in entries)
                for child in children:
                    visit(child)
            elif path.suffix == ".py":
                if not stat.S_ISREG(mode) or not mode & 0o400:
                    raise PermissionError("Python entry is not a readable regular file")
                paths.append(path)
        except OSError as exc:
            unparsed.append(f"{rel}: {exc}")

    visit(root)
    if not paths:
        unparsed.append("no readable Python files in declared population")
    for p in paths:
        rel = str(p.relative_to(root))
        try:
            a, b = capabilities_of(p.read_text())
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
            unparsed.append(f"{rel}: {exc}")
            continue
        pub[rel], priv[rel] = a, b
    return pub, priv, unparsed


def assess(before: Path, after: Path, allowed: set[str]) -> dict[str, Any]:
    if not before.is_dir() or not after.is_dir():
        raise InputError("both --before and --after must be directories")
    pub_b, priv_b, unparsed_b = scan(before)
    pub_a, priv_a, unparsed_a = scan(after)

    def absent(path):
        try:
            path.lstat()
        except FileNotFoundError:
            return True
        except OSError:
            return False
        return False

    removed: dict[str, sorted] = {}
    for rel, names in pub_b.items():
        if rel not in pub_a:
            if not absent(after / rel):
                # Present but unreadable/unparseable is not a removed module.
                continue
            # A whole module gone is the loudest form of the defect.
            gone = sorted(names)
            if gone:
                removed[rel] = ["<module removed>"] + gone
            continue
        gone = sorted(n for n in names - pub_a[rel] if f"{rel}::{n}" not in allowed
                      and n not in allowed)
        if gone:
            removed[rel] = gone
    private_removed = {rel: sorted(names - priv_a.get(rel, set()))
                       for rel, names in priv_b.items()
                       if (rel in priv_a or absent(after / rel))
                       and names - priv_a.get(rel, set())}
    added = {rel: sorted(names - pub_b.get(rel, set()))
             for rel, names in pub_a.items()
             if (rel in pub_b or absent(before / rel)) and names - pub_b.get(rel, set())}

    if unparsed_b or unparsed_a:
        state = "UNAVAILABLE"
        why = (f"{len(unparsed_b) + len(unparsed_a)} file(s) could not be parsed, so retention "
               f"across them is UNKNOWN, not confirmed: "
               f"{(unparsed_b + unparsed_a)[:5]}")
    elif removed:
        state = "REMOVED"
        why = (f"{sum(len(v) for v in removed.values())} public capability(ies) removed across "
               f"{len(removed)} file(s). A MERGE-as-overwrite deletes silently: the bytes match "
               f"the tag, the file lints clean, and a consumer's call is simply gone")
    else:
        state = "RETAINED"
        why = None
    return {"state": state, "why": why, "removed": removed, "added": added,
            "private_removed": private_removed,
            "unparsed": unparsed_b + unparsed_a,
            "counts_complete": not unparsed_b and not unparsed_a,
            "counts": {"before": sum(len(v) for v in pub_b.values()),
                       "after": sum(len(v) for v in pub_a.values())}}


def render(res: dict[str, Any]) -> str:
    out = [f"capability retention: {res['state']}"]
    if res.get("why"):
        out.append(f"  -- {res['why']}")
    for rel, names in list(res["removed"].items())[:12]:
        out.append(f"  REMOVED  {rel}")
        for n in names[:8]:
            out.append(f"             {n}")
    if res["private_removed"]:
        out.append(f"  {sum(len(v) for v in res['private_removed'].values())} private name(s) "
                   f"removed -- reported, not failed: consumers were never entitled to them")
    c = res["counts"]
    qualifier = "" if res.get("counts_complete", True) else "observed only; incomplete population: "
    out.append(f"  {qualifier}public capabilities {c['before']} -> {c['after']}")
    out.append("  Byte-hash equality and lint both pass through a deletion. This does not.")
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    return {"RETAINED": 0, "REMOVED": 1}.get(res["state"], 2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Detect capability deletion across a payload update.")
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--allow-removed", type=Path, default=None,
                    help="JSON list of deliberately removed names (a deprecation record)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    allowed: set[str] = set()
    if args.allow_removed:
        try:
            allowed = set(json.loads(args.allow_removed.read_text()))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            print(f"UNAVAILABLE: allow-list unreadable: {exc}", file=sys.stderr)
            return 3
    try:
        res = assess(args.before, args.after, allowed)
    except InputError as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1, default=list) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
