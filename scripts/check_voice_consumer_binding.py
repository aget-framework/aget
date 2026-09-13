#!/usr/bin/env python3
"""Audit subject-bound consumption of the voice scaffold."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

BOUND, PARTIAL, DANGLING, ABSENT, UNAVAILABLE = (
    "BOUND",
    "PARTIAL",
    "DANGLING",
    "ABSENT",
    "UNAVAILABLE",
)
CITATION = re.compile(r"(?:^|[\s`(\[])((?:[\w./-]*)(?:VOICE\.md|knowledge/voice/[\w./-]*))", re.M)
COMPOSITION_TOKENS = (
    "Specification",
    "Evidence Bank",
    "Enforcement",
    "Calibration Memory",
    "Ontology",
)


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, ValueError):
        return False


def _scaffold(rel: Path) -> bool:
    return len(rel.parts) >= 3 and rel.parts[-3:-1] == ("knowledge", "voice")


def _walk(root: Path, starts: list[Path]) -> tuple[list[Path], list[str]]:
    files: dict[tuple[int, int], Path] = {}
    failures: list[str] = []
    visited = set()

    def visit(path: Path) -> None:
        try:
            s = path.lstat()
        except OSError as exc:
            failures.append(f"{path}: lstat failed: {exc}")
            return
        rel = str(path.relative_to(root))
        if stat.S_ISLNK(s.st_mode):
            try:
                target = path.resolve(strict=True)
                target.relative_to(root)
            except (OSError, ValueError):
                failures.append(f"{rel}: symlink escapes subject or is dangling")
                return
            kind = (
                "directory"
                if target.is_dir()
                else "file"
                if target.is_file()
                else "unsupported entry"
            )
            failures.append(f"{rel}: symlink-to-{kind} is not traversed")
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
                with os.scandir(path) as it:
                    children = sorted((Path(e.path) for e in it), key=lambda p: p.name)
            except OSError as exc:
                failures.append(f"{rel or '.'}: enumeration failed: {exc}")
                return
            for child in children:
                visit(child)
        elif stat.S_ISREG(s.st_mode):
            if path.suffix.lower() == ".md":
                files.setdefault((s.st_dev, s.st_ino), path)
        elif path.suffix.lower() == ".md":
            failures.append(f"{rel}: unsupported markdown entry type")

    for start in starts:
        if not _inside(root, start):
            failures.append(f"{start}: scan root escapes subject")
        elif not start.exists() and not start.is_symlink():
            failures.append(f"{start.relative_to(root)}: scan root absent")
        else:
            visit(start)
    return sorted(files.values(), key=lambda p: str(p.relative_to(root))), sorted(set(failures))


def resolves(root: Path, cited: str) -> bool:
    raw = Path(cited)
    candidates = [root / raw]
    if len(raw.parts) == 1:
        candidates.append(root / "knowledge" / "voice" / raw)
    for p in candidates:
        try:
            q = p.resolve(strict=True)
            q.relative_to(root)
            if q.is_file():
                if not q.stat().st_mode & 0o400:
                    raise PermissionError(f"cited target is unreadable: {cited}")
                with q.open("rb") as target:
                    target.read(1)
                return True
        except (FileNotFoundError, ValueError):
            pass
    return False


def scan_consumer(path: Path, root: Path) -> dict[str, Any] | None:
    rel = path.relative_to(root)
    if _scaffold(rel):
        return None
    try:
        if not path.stat().st_mode & 0o400:
            raise PermissionError("owner-read bit is not set")
        text = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "consumer": str(rel),
            "outcome": UNAVAILABLE,
            "cites": [],
            "unresolved": [],
            "why": f"consumer unreadable: {exc}",
        }
    cites = sorted({m.group(1) for m in CITATION.finditer(text) if not m.group(1).endswith("/")})
    if not cites:
        return None
    unresolved, read_failures = [], []
    for cited in cites:
        try:
            if not resolves(root, cited):
                unresolved.append(cited)
        except OSError as exc:
            read_failures.append(f"{cited}: {exc}")
    ordered = sum(t in text for t in COMPOSITION_TOKENS) >= 3
    outcome, why = (
        (DANGLING, f"observed unresolved citations {unresolved}")
        if unresolved
        else (UNAVAILABLE, "cited targets could not be read") if read_failures
        else ((BOUND, None) if ordered else (PARTIAL, "citation lacks composition order"))
    )
    return {
        "consumer": str(rel),
        "outcome": outcome,
        "cites": cites,
        "unresolved": unresolved,
        "read_failures": read_failures,
        "why": why,
    }


def assess(root: Path, subdirs: list[str]) -> dict[str, Any]:
    try:
        root = root.resolve(strict=True)
        mode = root.stat().st_mode
    except OSError as exc:
        raise NotADirectoryError(root) from exc
    if not stat.S_ISDIR(mode):
        raise NotADirectoryError(root)
    paths, failures = _walk(root, [root / s for s in subdirs] if subdirs else [root])
    seen = []
    for p in paths:
        got = scan_consumer(p, root)
        if got:
            failures.extend(f"{got['consumer']}: {failure}"
                            for failure in got.get("read_failures", []))
        if got and got["outcome"] == UNAVAILABLE:
            failures.append(f"{got['consumer']}: {got['why']}")
        elif got:
            seen.append(got)
    failures = sorted(set(failures))
    full = not failures
    counts = {k: sum(x["outcome"] == k for x in seen) for k in (BOUND, PARTIAL, DANGLING)}
    overall = (
        DANGLING
        if counts[DANGLING]
        else (UNAVAILABLE if not full else (BOUND if counts[BOUND] else ABSENT))
    )
    ec2 = (counts[BOUND] > 0 and not counts[DANGLING]) if full else None
    limit = None if full else f"could not fully read subject {root}: " + "; ".join(failures)
    evidence = [x["consumer"] for x in seen if x["outcome"] in (BOUND, DANGLING)]
    return {
        "population_root": str(root),
        "population_reached": full,
        "fully_read": full,
        "unreached_subjects": failures,
        "limit": limit,
        "consumers": seen,
        "counts": counts,
        "overall": overall,
        "ec2_satisfied": ec2,
        "classification": {
            "subject_bound": True,
            "subject_reached": full,
            "affirming_evidence": evidence,
            "predicate_discriminating": full or bool(evidence),
            "definite": overall != UNAVAILABLE,
        },
    }


def render(r):
    out = [f"voice consumer binding (INIT-VOICE-FRAMEWORK EC-2): {r['overall']}", ""]
    for c in r["consumers"]:
        out += [
            f"  {c['outcome']:<9} {c['consumer']}",
            f"            cites: {', '.join(c['cites'])}",
        ]
        if c.get("why"):
            out.append(f"            -- {c['why']}")
    n = r["counts"]
    out += [
        "",
        f"  bound={n[BOUND]}  partial={n[PARTIAL]}  dangling={n[DANGLING]}",
        f"  EC-2 satisfied: {r['ec2_satisfied']}",
    ]
    if r["limit"]:
        out += [f"  LIMIT: {r['limit']}"] + [f"  UNREACHED: {x}" for x in r["unreached_subjects"]]
    return "\n".join(out)


def exit_code(r):
    return (
        3
        if not r["fully_read"]
        else (1 if r["counts"][DANGLING] else (0 if r["counts"][BOUND] else 2))
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--consumer", action="append", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = assess(a.root, a.consumer or [])
    except (OSError, NotADirectoryError) as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(r, indent=1) if a.json else render(r))
    return exit_code(r)


if __name__ == "__main__":
    sys.exit(main())
