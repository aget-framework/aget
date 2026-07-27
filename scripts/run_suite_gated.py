#!/usr/bin/env python3
"""run_suite_gated.py — run a test suite under the TWO-CLAUSE behavioural gate.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH
========================================
`sops/SOP_fleet_migration.md` §Dispatch Safety item 1 and `handoffs/CORRECTIONS_v3.28.0.md`
row 9 both state, in bold, that a contract suite run during migration can mutate the
repository, and that you must assert BOTH clauses across the run:

    git rev-list --count HEAD     # unchanged
    git status --porcelain        # unchanged

Row 9 additionally warns, explicitly, not to diagnose the mutation by grepping for
suspect call sites.

That prose was read, cited, and planned around by a consuming supervisor seat on
2026-07-27 — which then reached for grep first anyway. Its own retrospective:

    "Grep scored 0-for-2 on its hits and 0-for-3 on the real igniters — the upstream
     correction warned about precisely that and the warning didn't stop me; the gate did."

Three igniters were found by per-file bisection with the gate as oracle. Two of them had
nothing to do with the vendored package row 9 names, so "no vendored package" does not
imply "suite is clean."

A warning that its most careful reader cites and then does not follow is decorative
(L671). This file is that warning with an exit code.

WHAT IT DOES
============
  1. Records (commit-count, porcelain) before the run.
  2. Runs the suite.
  3. Re-records. If EITHER clause changed, the run is a GATE VIOLATION regardless of
     whether the tests passed.
  4. `--bisect` then finds which test file mutates, one file at a time, gate between runs.

The count clause alone is insufficient: a clean count passed a run that wrote 18
untracked files (row 9). Both clauses, always.

EXIT CODES
    0  suite ran, gate held
    1  suite failed, gate held          (an ordinary test failure)
    2  GATE VIOLATED — the run mutated the repository
    3  usage / environment error

Reporting rule (§Dispatch Safety item 1): if you deselect an igniter to get a green run,
report the probe **PARTIAL naming the deselection** — never as a clean pass.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def snapshot(repo):
    """The two clauses. Both, or the gate is not the gate."""
    return {
        "commits": _git(repo, "rev-list", "--count", "HEAD"),
        "porcelain": _git(repo, "status", "--porcelain"),
    }


def _path_of(porcelain_line):
    """Strip the 2-char XY status prefix; handle rename arrows."""
    p = porcelain_line[3:] if len(porcelain_line) > 3 else porcelain_line
    return p.split(" -> ")[-1].strip().strip('"')


def diff_snapshots(before, after, allow_paths=()):
    """Return (violations, exempted).

    `allow_paths` are prefixes whose mutation is DECLARED benign — append-only logs and
    the like. Exempted paths are still reported, never suppressed: an exemption a reader
    cannot see is indistinguishable from a gate that did not look. The commit-count
    clause is NEVER exemptible — a commit is never benign during a migration.
    """
    out, exempted = [], []
    if before["commits"] != after["commits"]:
        n = int(after["commits"]) - int(before["commits"])
        out.append(f"COMMIT-COUNT clause: {before['commits']} -> {after['commits']} ({n:+d} commits created)")
    if before["porcelain"] != after["porcelain"]:
        b = set(before["porcelain"].splitlines())
        a = set(after["porcelain"].splitlines())
        changed = sorted((a - b) | (b - a))
        real = []
        for line in changed:
            path = _path_of(line)
            if any(path.startswith(pfx) for pfx in allow_paths):
                exempted.append(line)
            else:
                real.append(line)
        if real:
            out.append(f"PORCELAIN clause: {len(real)} undeclared path change(s)")
            for line in real[:12]:
                out.append(f"    {line}")
    return out, exempted


def run_suite(repo, pytest_args, timeout):
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header",
           "-p", "no:cacheprovider", *pytest_args]
    try:
        return subprocess.run(cmd, cwd=str(repo), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def gated_run(repo, pytest_args, timeout, quiet=False, allow_paths=()):
    """Run once under the gate. Returns (violations, exempted, process_or_None)."""
    before = snapshot(repo)
    proc = run_suite(repo, pytest_args, timeout)
    after = snapshot(repo)
    violations, exempted = diff_snapshots(before, after, allow_paths)
    if not quiet and proc is not None:
        tail = (proc.stdout or "").strip().splitlines()[-6:]
        for line in tail:
            print(f"  {line}")
    return violations, exempted, proc


def bisect(repo, timeout, allow_paths=()):
    """Find every test file that mutates the repo, one file at a time.

    Per-file, not halving: row 9's incident had THREE independent igniters, and a
    halving bisect reports one and stops. Cost is linear in test files; the incident
    it prevents is 527 commits and a 305 MB .git.
    """
    tests = sorted(p for p in (repo / "tests").glob("test_*.py")) if (repo / "tests").is_dir() else []
    if not tests:
        print(f"no tests/test_*.py under {repo}", file=sys.stderr)
        return []
    print(f"bisecting {len(tests)} test file(s) at {repo.name} — gate between every run\n")
    igniters = []
    for t in tests:
        rel = t.relative_to(repo)
        violations, _ex, _p = gated_run(repo, [str(rel)], timeout, quiet=True,
                                        allow_paths=allow_paths)
        if violations:
            igniters.append((str(rel), violations))
            print(f"  *** IGNITER: {rel}")
            for v in violations:
                print(f"        {v}")
            # Restore so the next file is measured from a clean baseline, not a
            # cumulative one — otherwise every later file inherits this one's mutation
            # and the whole tail reads as an igniter.
            _git(repo, "checkout", "--", ".")
    return igniters


def self_test():
    """V-tests for the gate logic. `diff_snapshots` carries every decision, so it is
    the honest unit to test — the first smoke run of this script 'passed' only because
    a prior run had already left the tree dirty, which is exactly the non-discriminating
    check this suite exists to replace.
    """
    S = lambda c, p: {"commits": c, "porcelain": p}
    cases = []

    def check(name, cond):
        cases.append((name, bool(cond)))

    # 1. clean run -> gate holds
    v, e = diff_snapshots(S("10", ""), S("10", ""))
    check("clean run holds", not v and not e)

    # 2. new commit -> violation
    v, e = diff_snapshots(S("10", ""), S("13", ""))
    check("commit clause fires", any("COMMIT-COUNT" in x for x in v))
    check("commit delta reported", any("+3 commits" in x for x in v))

    # 3. untracked file, count clean -> violation (row 9's 18-files case)
    v, e = diff_snapshots(S("10", ""), S("10", "?? SESSION_NOTES/x.md"))
    check("porcelain clause fires on clean count", any("PORCELAIN" in x for x in v))

    # 4. declared-benign path -> exempted, NOT a violation, still reported
    v, e = diff_snapshots(S("10", ""), S("10", " M .aget/logs/gate_log.jsonl"),
                          allow_paths=(".aget/logs/",))
    check("allow-path exempts", not v)
    check("exemption is still reported", len(e) == 1)

    # 5. mixed: one declared, one not -> violation naming only the undeclared
    v, e = diff_snapshots(S("10", ""),
                          S("10", " M .aget/logs/gate_log.jsonl\n?? junk.txt"),
                          allow_paths=(".aget/logs/",))
    check("mixed: violation raised", bool(v))
    check("mixed: only undeclared named", any("junk.txt" in x for x in v)
          and not any("gate_log" in x for x in v))
    check("mixed: declared still reported", len(e) == 1)

    # 6. the commit clause is NEVER exemptible, whatever is allowed
    v, e = diff_snapshots(S("10", ""), S("11", " M .aget/logs/x.jsonl"),
                          allow_paths=(".aget/logs/", ""))
    check("commit clause not exemptible by allow-path", any("COMMIT-COUNT" in x for x in v))

    # 7. prefix matching must not fire on a lookalike sibling
    v, e = diff_snapshots(S("10", ""), S("10", "?? .aget/logs-backup/x"),
                          allow_paths=(".aget/logs/",))
    check("sibling prefix not exempted", bool(v))

    # 8. renames report the destination path
    check("rename path extracted", _path_of("R  old.py -> new.py") == "new.py")

    failed = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}")
    print(f"\nself-test: {len(cases) - len(failed)}/{len(cases)}")
    return 0 if not failed else 1


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()
    ap = argparse.ArgumentParser(
        description="Run a test suite under the two-clause behavioural gate "
                    "(SOP_fleet_migration §Dispatch Safety item 1).")
    ap.add_argument("repo", help="repository root to run the suite in")
    ap.add_argument("--bisect", action="store_true",
                    help="find every test file that mutates the repo, one at a time")
    ap.add_argument("--timeout", type=int, default=900,
                    help="per-run timeout in seconds (default 900; size it against the "
                         "CONTENDED case, not an idle machine — CORRECTIONS row 10)")
    ap.add_argument("pytest_args", nargs="*",
                    help="extra args passed through to pytest (e.g. --deselect ...)")
    ap.add_argument("--allow-path", action="append", default=[], metavar="PREFIX",
                    help="path prefix whose mutation is DECLARED benign (append-only logs). "
                         "Repeatable. Exemptions are always reported. The commit-count "
                         "clause is never exemptible.")
    args = ap.parse_args(argv)
    allow = tuple(args.allow_path)

    repo = Path(args.repo).expanduser().resolve()
    if not (repo / ".git").exists():
        print(f"not a git repository: {repo}", file=sys.stderr)
        return 3

    if args.bisect:
        igniters = bisect(repo, args.timeout, allow)
        print()
        if not igniters:
            print("GATE HELD for every test file individually.")
            return 0
        print(f"{len(igniters)} IGNITER(S) — deselect these, then report the probe "
              f"PARTIAL naming the deselection:")
        for rel, _ in igniters:
            print(f"  --deselect {rel}   (or --ignore {rel})")
        return 2

    print(f"SEAT: {repo.name}")
    violations, exempted, proc = gated_run(repo, args.pytest_args, args.timeout,
                                           allow_paths=allow)
    if exempted:
        print(f"\n  {len(exempted)} DECLARED-BENIGN path change(s) — exempted by --allow-path,")
        print("  reported because an unseen exemption is indistinguishable from no check:")
        for line in exempted[:12]:
            print(f"    ~ {line}")
    print()
    if violations:
        print("*** GATE VIOLATED — the suite mutated the repository ***")
        for v in violations:
            print(f"  {v}")
        print("\nDo NOT report this run as a pass, whatever the test result was.")
        print("Next: re-run with --bisect. Do not grep for the writer — row 9's warning")
        print("was measured ineffective on a careful reader; the gate is what works.")
        return 2

    print("gate HELD — commit count and porcelain both unchanged across the run")
    if proc is None:
        print("(suite TIMED OUT — a timed-out dispatch can leave a seat version-pinned")
        print(" with no payload; inspect the tree before re-dispatching)")
        return 1
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
