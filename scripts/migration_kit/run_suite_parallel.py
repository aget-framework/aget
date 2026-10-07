#!/usr/bin/env python3
"""A receiver's whole test suite, one pytest process per test file, in parallel, printed as ONE pytest-style summary.

Why (principal ruling `framework suite-command parallel-runner, CI deselection disclosed`, 2026-09-28): the framework
Aget's suite is serial by default (about 49 min), which no step of the batch route can wait for (V3.6 limits a run to
1,500 s; a headless session's single command is capped at 600 s). This mirrors that Aget's own pre-push engine
(`run_files_parallel` in its scripts/pre_push_suite_gate_ext.py): `tests/**/test_*.py` discovery, one
`python3 -m pytest <file> -q -rfE -p no:cacheprovider` per file, longest-known first, up to 12 workers.

Deselection is DISCLOSED, never silent: with --deselect-file, each listed node id is passed as `--deselect` to its
file's process, and the output names every deselected id before the summary. A test file whose pytest exits with an
error code (2, 3 or 4) is reported as an ERROR line, so it can never read as green.

Output: a `short test summary info` header, the FAILED/ERROR lines of every file's own short test summary as the kit's
one reader reads them (result_binding; B180, B182 finding 1), an `IDS-UNKNOWN` line for a file whose failing ids it
cannot read or whose pytest did not finish (never an id: the kit's reader then reads the run's ids as not all known),
then one summary line such as
`1 failed, 2061 passed, 4 skipped, 4 deselected in 371.2s`, so the kit's one failing-id reader
(result_binding.failing_ids) reads it as it reads pytest. Exit 0 if nothing failed or errored, else 1.

Under the kit (C2a7, B185 finding 1), each file's pytest loads the kit's report plugin through the environment it
inherits, and this runner appends one `runner` record to the same report: how many test files it started and, for
each, the one invocation that file's output names. A file whose output names none, or more than one, leaves the run
not complete. It then prints `aget-kit-report: runner <run>`, so the kit reads the run's failing ids from the report
(result_binding.report_failures), never from the lines above.

Usage (from the receiver's root): python3 <path>/run_suite_parallel.py [--deselect-file tests/ci_known_failures.txt]
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

COUNT = re.compile(r"(\d+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed|warnings?|subtests passed)")
ORDER = ["failed", "passed", "skipped", "deselected", "xfailed", "xpassed", "error", "warning", "subtests passed"]


def discover(root):
    """Return sorted relative paths matching test_*.py under the root's tests folder."""
    return sorted(str(p.relative_to(root)) for p in (root / "tests").rglob("test_*.py"))


def deselected(root, path):
    """Return the test ids listed in the deselect file; empty when no file is named."""
    if not path:
        return []
    f = root / path
    if not f.is_file():
        raise SystemExit(f"run_suite_parallel: --deselect-file {path} not found")
    return [ln.strip() for ln in f.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#")]


def last_summary(text):
    """Return the last pytest summary line in the text, or an empty string when there is none."""
    for ln in reversed(text.splitlines()):
        if " in " in ln and COUNT.search(ln):
            return ln
    return ""


sys.path.insert(0, str(Path(__file__).resolve().parent))
import result_binding as RBND  # noqa: E402  (B182 finding 1: the kit's one failing-id reader, applied per file)


def run_one(root, f, nodes):
    """Run pytest on one test file with its deselections; return (file, exit code, output)."""
    des = [a for n in nodes if n.startswith(f + "::") for a in ("--deselect", n)]
    p = subprocess.run([sys.executable, "-m", "pytest", f, "-q", "-rfE", "-p", "no:cacheprovider", *des], cwd=root,
                       capture_output=True, text=True)
    return f, p.returncode, p.stdout + p.stderr


def main(argv=None):
    """Command-line entry point: run the suite one process per test file and print a single summary."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--deselect-file")
    ap.add_argument("--workers", type=int, default=max(2, min(12, (os.cpu_count() or 4) - 2)))
    a = ap.parse_args(argv)
    root = a.root.resolve()
    nodes = deselected(root, a.deselect_file)
    files = discover(root)
    t0 = time.time()
    totals, lines, errors, unknown, children = {}, [], [], [], []
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for f, rc, out in ex.map(lambda f: run_one(root, f, nodes), files):
            marks = [ln.strip() for ln in out.splitlines() if ln.strip().startswith(RBND.REPORT_MARK)]
            m = RBND._MARK_LINE.fullmatch(marks[0]) if len(marks) == 1 else None
            children.append(m.group(2) if m and m.group(1) == "pytest" else None)   # C2a7: this file's invocation
            # B182 finding 1: each file's output is read by the kit's one reader (one count line, one summary,
            # ids with a unique end, FAILED/ERROR accounted); a file it cannot read is marked, never turned into an id
            found, _, _, why = RBND.summary_section(out)
            ids, why = RBND.failing_ids(out) if not why else ([], why)
            if why and rc in (0, 1):
                unknown.append(f"{RBND.IDS_UNKNOWN}{f}: {why}")
            elif not why:
                lines += found
            counted = {}
            for n, word in COUNT.findall(last_summary(out)):
                key = {"errors": "error", "warnings": "warning"}.get(word, word)
                totals[key] = totals.get(key, 0) + int(n)
                counted[key] = counted.get(key, 0) + int(n)
            if rc not in (0, 1, 5):   # 0 pass, 1 test failures, 5 nothing collected; 2-4 = interrupted/internal/usage
                # B182 finding 1: a line the runner makes is marked as not an id (it held the run's time, and a
                # stable one would exempt a different failure in the same file)
                errors.append(f"{RBND.IDS_UNKNOWN}{f} (pytest exit {rc}: {(out.strip().splitlines() or [''])[-1][:160]})")
            elif rc == 1 and not (counted.get("failed") or counted.get("error")):
                # FALSE GREEN (the framework Aget's review, 2026-09-29): pytest exited 1 with no failed/error count,
                # e.g. a session-level failure that prints "N passed" and then exits 1. It read green here.
                errors.append(f"{RBND.IDS_UNKNOWN}{f} (pytest exit 1 with no failed or error counted: "
                              f"{(out.strip().splitlines() or [''])[-1][:160]})")
    if lines or errors or unknown:               # one line per failure or error, so the counts account for them
        print("=" * 27 + " short test summary info " + "=" * 28)
    for ln in sorted(lines) + errors + unknown:
        print(ln)
    for n in nodes:
        print(f"DESELECTED (disclosed, --deselect-file {a.deselect_file}): {n}")
    if errors:
        totals["error"] = totals.get("error", 0) + len(errors)
    parts = [f"{totals[k]} {k if k != 'error' or totals[k] == 1 else 'errors'}" for k in ORDER if totals.get(k)]
    print(f"{', '.join(parts) or 'no tests ran'} in {time.time() - t0:.1f}s")
    report, token = os.environ.get("AGET_KIT_REPORT"), os.environ.get("AGET_KIT_REPORT_TOKEN")
    if report and token:                  # C2a7: the run's record in the kit's report, and the line that names it
        run = uuid.uuid4().hex
        ok = all(children) and len(set(children)) == len(children)
        try:
            RBND.append_runner_record(report, token, run, len(files), [c for c in children if c], ok)
            print(f"{RBND.REPORT_MARK}runner {run}")
        except OSError as e:
            print(f"(run_suite_parallel: the kit's report could not be appended: {e})")
    print(f"(run_suite_parallel: {len(files)} test files, {a.workers} workers)")
    return 1 if totals.get("failed") or totals.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
