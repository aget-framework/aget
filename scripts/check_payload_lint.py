#!/usr/bin/env python3
"""Producer-side payload lint gate — a ratchet, not a one-off clean.

WHY A RATCHET
-------------
Three consecutive releases shipped a lint-dirty payload: v3.12.0 (gh#832), v3.28.0 (gh#2041),
v3.33.1 (gh#2464). All three are the same defect and the first two are still open. The reporter
named the reason a point fix does not work:

    "The instance is not the finding. The recurrence is. A corrected v3.33.2 tag closes this
     occurrence and leaves the producing mechanism exactly as it is, so the next release
     re-opens it."

So this gate does not demand a clean tree on the day it lands. It demands that the payload
**never get worse**, and that **every newly added file be clean**. A backlog shrinks or holds;
it cannot grow. That is a mechanism, where a `--fix` sweep is an instance.

WHY A DECLARED CONFIG IS THE ROOT FIX
-------------------------------------
Canonical carried no ruff config. A finding count with no config is not a fact about the code:
the same binary returns a wholly different number with and without one. Producer and receiver
were running different gates and comparing the results. `ruff.toml` now ships WITH the payload,
so the receiver's count and the producer's count are the same measurement.

The ruff VERSION is recorded alongside the baseline for the same reason — a vendor rule
expansion changes the count without the code changing (gh#2007). A version change is reported,
never silently absorbed.

USAGE
  check_payload_lint.py --repo DIR --baseline .aget/lint_baseline.json
  check_payload_lint.py --repo DIR --baseline B --update      # record a NEW baseline
  check_payload_lint.py --repo DIR --baseline B --json

EXIT CODES
  0  the payload did not get worse and every new file is clean
  1  findings increased, or a newly added file is dirty
  2  the gate could not run  (ruff absent, unreadable baseline) -- never a pass
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_PATHS = ("scripts", "tests", "verification")


def ruff_version() -> str | None:
    if not shutil.which("ruff"):
        return None
    try:
        p = subprocess.run(["ruff", "--version"], capture_output=True, text=True, timeout=30)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def run_ruff(repo: Path, paths: list[str]) -> dict[str, int] | None:
    """Per-file finding counts under the repo's OWN ruff.toml. Returns None if ruff cannot run."""
    repo = repo.resolve()
    targets = [str(repo / p) for p in paths]
    if not targets or any(not Path(p).exists() for p in targets):
        return None
    try:
        population = subprocess.run(["ruff", "check", "--show-files", *targets],
                                    cwd=repo, capture_output=True, text=True, timeout=300)
        if population.returncode != 0 or not population.stdout.strip():
            return None
        p = subprocess.run(["ruff", "check", "--output-format", "json", *targets],
                           cwd=repo, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode not in (0, 1):
        return None
    try:
        rows = json.loads(p.stdout or "[]")
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return None
    counts: dict[str, int] = {}
    for r in rows:
        try:
            rel = str(Path(r["filename"]).resolve().relative_to(repo.resolve()))
        except (ValueError, KeyError):
            rel = str(r.get("filename", "?"))
        counts[rel] = counts.get(rel, 0) + 1
    return counts


def assess(repo: Path, baseline_path: Path, paths: list[str]) -> dict[str, Any]:
    if not (repo / "ruff.toml").exists() and not (repo / "pyproject.toml").exists():
        return {"state": "UNAVAILABLE", "why":
                "the repository declares no ruff configuration; a finding count without a "
                "declared config is not portable and this gate will not produce one"}
    version = ruff_version()
    if version is None:
        return {"state": "UNAVAILABLE",
                "why": "ruff is not available; the gate did not run and is NOT a pass"}
    current = run_ruff(repo, paths)
    if current is None:
        return {"state": "UNAVAILABLE", "why": "ruff did not produce readable output"}

    try:
        base = json.loads(baseline_path.read_text())
    except FileNotFoundError:
        return {"state": "UNAVAILABLE", "current": current, "ruff_version": version,
                "why": f"no baseline at {baseline_path}; record one with --update. An absent "
                       f"baseline is not a clean payload"}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"state": "UNAVAILABLE", "why": f"baseline unreadable: {exc}"}

    if not isinstance(base, dict) or not isinstance(base.get("files"), dict):
        return {"state": "UNAVAILABLE", "why": "baseline must contain a files mapping"}
    base_counts = base["files"]
    if any(not isinstance(k, str) or type(v) is not int or v < 0
           for k, v in base_counts.items()):
        return {"state": "UNAVAILABLE", "why": "baseline counts must be nonnegative integers"}
    base_version = base.get("ruff_version")
    regressions = {f: (base_counts.get(f, 0), n) for f, n in current.items()
                   if n > base_counts.get(f, 0)}
    # A file absent from the baseline is NEW. New files must be clean; a backlog is inherited,
    # never extended.
    new_dirty = sorted(f for f in current if f not in base_counts)
    improved = {f: (base_counts[f], current.get(f, 0)) for f in base_counts
                if current.get(f, 0) < base_counts[f]}
    total_now, total_base = sum(current.values()), sum(base_counts.values())

    state = "PASS"
    why = None
    if new_dirty:
        state = "FAIL"
        why = (f"{len(new_dirty)} newly added file(s) are lint-dirty: {new_dirty[:6]}. A backlog "
               f"is inherited, not extended")
    elif regressions:
        state = "FAIL"
        why = f"{len(regressions)} file(s) got worse: {list(regressions)[:6]}"
    return {"state": state, "why": why, "ruff_version": version,
            "baseline_ruff_version": base_version,
            "version_changed": bool(base_version and base_version != version),
            "total_now": total_now, "total_baseline": total_base,
            "regressions": regressions, "new_dirty_files": new_dirty,
            "improved": improved, "current": current}


def render(res: dict[str, Any]) -> str:
    out = [f"payload lint gate: {res['state']}"]
    if res.get("why"):
        out.append(f"  -- {res['why']}")
    if "total_now" in res:
        d = res["total_now"] - res["total_baseline"]
        out.append(f"  findings {res['total_now']} vs baseline {res['total_baseline']} "
                   f"({d:+d})")
    if res.get("version_changed"):
        out.append(f"  ⚠ ruff version moved {res['baseline_ruff_version']} -> "
                   f"{res['ruff_version']}: a vendor rule expansion changes the count without "
                   f"the code changing. Re-baseline deliberately, do not absorb it silently")
    if res.get("improved"):
        out.append(f"  {len(res['improved'])} file(s) improved")
    out.append("  The gate demands the payload never gets WORSE and that new files are clean.")
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    return {"PASS": 0, "FAIL": 1}.get(res["state"], 2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Producer-side payload lint ratchet.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--path", action="append", default=None)
    ap.add_argument("--update", action="store_true", help="record a new baseline")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    paths = args.path or list(DEFAULT_PATHS)

    if args.update:
        version = ruff_version()
        counts = run_ruff(args.repo, paths) if version else None
        if counts is None:
            print("UNAVAILABLE: ruff did not run; refusing to record an empty baseline",
                  file=sys.stderr)
            return 2
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(json.dumps(
            {"ruff_version": version, "paths": paths, "total": sum(counts.values()),
             "files": counts}, indent=1, sort_keys=True) + "\n")
        print(f"baseline recorded: {sum(counts.values())} findings across {len(counts)} file(s), "
              f"{version}")
        return 0

    res = assess(args.repo, args.baseline, paths)
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
