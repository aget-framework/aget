#!/usr/bin/env python3
"""G2.1 -- CI census across the fleet. Never measured at any seat before 2026-08-02.

Two questions, kept separate because conflating them is how the wiring pilot broke CI:

  STRUCTURE  does the seat have .github/workflows/, and what does each workflow
             actually need on the runner (pytest? a `python -m` module? make?)
  STATE      what is the most recent run's conclusion, per `gh run list`

STATE requires network + a GitHub remote. Three-state per
CONVENTION_check_three_state_contract: a seat whose CI cannot be queried is
UNREACHABLE, never "green". The pilot's failure mode -- a job verified on the
authoring seat, dispatched to a runner without pytest -- is a STRUCTURE fact
that no amount of STATE polling would have surfaced.

STRUCTURE IS READ AT THE REPOSITORY ROOT, NOT THE SEAT'S FOLDER (2026-09-27). GitHub runs
only the workflows at a repository's root. This census used to look in each seat's own
folder, so a seat nested in a shared repository read "no CI" when the root had a workflow,
and a workflow file in a seat's subfolder, which never runs, read as CI. That reading was
retired in the v3.35 plan on 2026-09-26 (wave_membership_table.py applies the root rule),
but this census kept it and a peer quoted its count of Agets without CI as a correction; in
that census, the root-based count was lower. A seat sharing a root is marked SHARED: the root's workflow may or may not
cover that seat, and this census does not claim either.

Read-only. Never writes to a managed repository (R-CLI-004).
"""
import argparse
import json
import os
import re
import subprocess

import yaml

FS = ".aget/fleet/FLEET_STATE.yaml"
# What a workflow needs on the runner. Presence of the left-hand token in a
# workflow means the right-hand capability must exist wherever it runs.
NEEDS = {
    "pytest": r"\bpytest\b",
    "make": r"^\s*run:.*\bmake\b",
    "pip-install": r"pip install",
    "python": r"\bpython3?\b",
}


def seats():
    """Yield (name, location) for every member of the fleet register that has both."""
    d = yaml.safe_load(open(FS))
    for pf in (d.get("fleet") or {}).values():
        if not isinstance(pf, dict):
            continue
        for a in pf.get("agents", []) or []:
            n, loc = a.get("agent_name"), a.get("location")
            if n and loc:
                yield n, os.path.expanduser(loc)


def structure(path):
    """Return workflow filenames and capabilities detected by the configured text patterns."""
    wf_dir = os.path.join(path, ".github", "workflows")
    if not os.path.isdir(wf_dir):
        return {"workflows": 0, "needs": [], "files": []}
    files, needs = [], set()
    for f in sorted(os.listdir(wf_dir)):
        if not f.endswith((".yml", ".yaml")):
            continue
        files.append(f)
        try:
            text = open(os.path.join(wf_dir, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for cap, pat in NEEDS.items():
            if re.search(pat, text, re.M):
                needs.add(cap)
    return {"workflows": len(files), "needs": sorted(needs), "files": files}


def state(path, online):
    """The seat's CI state -- and WHICH COMMIT it is a state OF.

    THE NEWEST RUN IS NOT A VERDICT ON THE SEAT'S HEAD, and this function used to
    report it as one. It asked for one run, never asked which commit that run was
    for, and returned the conclusion as the seat's CI state. A seat dormant for
    months then reads as SUCCESS or FAILURE on a year-old run, and a seat whose
    work is committed but unpushed reads as green on the last thing that WAS
    pushed.

    This is not a new finding here. The identical defect was found and repaired in
    this seat's health check months ago -- that one now compares headSha against
    HEAD and reports staleness explicitly. THE REPAIR NEVER REACHED THIS SIBLING.
    Found 2026-09-06 by sweeping this seat's own instruments for narrowings after
    a peer named the pattern; a fix that lands in one instrument and not in its
    twin is the propagation half of the same problem.

    So: ask for headSha too, compare it to the seat's actual HEAD, and never
    return a bare conclusion. STALE- is a prefix, not a footnote, because a
    reader scanning a column of states will not read a footnote.
    """
    if not online:
        return "NOT-QUERIED"
    r = subprocess.run(["gh", "run", "list", "--limit", "1",
                        "--json", "conclusion,status,workflowName,headSha"],
                       cwd=path, capture_output=True, text=True)
    if r.returncode != 0:
        return "UNREACHABLE"
    try:
        runs = json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return "UNREACHABLE"
    if not runs:
        return "NO-RUNS"

    verdict = (runs[0].get("conclusion") or runs[0].get("status") or "?").upper()

    head = subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "rev-parse", "HEAD"], cwd=path,
                          capture_output=True, text=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"})  # B166 finding 2: a read that leaves the git folder as it was
    if head.returncode != 0:
        # Cannot establish the subject, so cannot claim the verdict is about it.
        return f"{verdict}-SUBJECT-UNKNOWN"
    ran_on = (runs[0].get("headSha") or "").strip()
    if not ran_on:
        return f"{verdict}-SUBJECT-UNKNOWN"
    return verdict if ran_on == head.stdout.strip() else f"STALE-{verdict}"


def repo_root(path):
    """The resolved repository root containing `path`, or None if it is not in a git repository."""
    r = subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "-C", path, "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"})  # B166 finding 2: a read that leaves the git folder as it was
    top = r.stdout.strip()
    return os.path.realpath(top) if r.returncode == 0 and top else None


def census(seat_list, online=False):
    """One row per seat: (name, structure AT THE ROOT, state, scope, inert subfolder workflow count).

    scope is OWN-ROOT, SHARED(n) when n seats share the root, or NO-REPO when the seat is not
    in a git repository (no workflow of its own can run; nothing is claimed about it).
    """
    seat_list = list(seat_list)
    roots = {n: repo_root(p) for n, p in seat_list}
    sharing = {}
    for root in roots.values():
        if root:
            sharing[root] = sharing.get(root, 0) + 1
    rows = []
    for n, p in seat_list:
        root = roots[n]
        if root is None:
            rows.append((n, {"workflows": 0, "needs": [], "files": []}, "N/A-no-repo", "NO-REPO", 0))
            continue
        st = structure(root)
        nested = os.path.realpath(p) != root
        inert = structure(p)["workflows"] if nested else 0
        scope = f"SHARED({sharing[root]})" if sharing[root] > 1 else "OWN-ROOT"
        s = state(root, online) if st["workflows"] else "N/A-no-workflows"
        rows.append((n, st, s, scope, inert))
    return rows


def main():
    """Command-line entry point: print the CI census across the fleet; --online also queries recent runs."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--online", action="store_true",
                    help="query `gh run list` per seat (network; slow)")
    args = ap.parse_args()

    rows = census(seats(), args.online)
    with_wf = [r for r in rows if r[1]["workflows"]]
    shared = [r for r in with_wf if r[3].startswith("SHARED")]
    print(f"{'seat':44s} {'wf':>3s}  {'state':14s} {'scope':10s} needs")
    for n, st, s, scope, _ in sorted(rows, key=lambda r: (-r[1]["workflows"], r[0])):
        if st["workflows"]:
            print(f"{n:44s} {st['workflows']:3d}  {s:14s} {scope:10s} {','.join(st['needs']) or '—'}")
    print(f"\nseats with a workflow at their repository root: {len(with_wf)}/{len(rows)}"
          + (f" (of which {len(shared)} share a root; coverage of each is UNRESOLVED)" if shared else ""))
    print(f"seats with NO workflow at their repository root: {len(rows) - len(with_wf)}/{len(rows)}")
    inert = [(n, k) for n, _, _, _, k in rows if k]
    if inert:
        print("workflow files in a seat's own subfolder (GitHub never runs these): "
              + ", ".join(f"{n} ({k})" for n, k in inert))
    no_repo = [n for n, _, _, scope, _ in rows if scope == "NO-REPO"]
    if no_repo:
        print("not in a git repository (nothing claimed): " + ", ".join(no_repo))
    if args.online:
        from collections import Counter
        c = Counter(r[2] for r in with_wf)
        print("state: " + " · ".join(f"{k}={v}" for k, v in sorted(c.items())))
    else:
        print("state: NOT-QUERIED for all (run with --online)")
    need_pytest = [r[0] for r in with_wf if "pytest" in r[1]["needs"]]
    print(f"\nworkflows requiring pytest on the runner: {len(need_pytest)}")
    print("  " + ", ".join(need_pytest) if need_pytest else "  (none)")
    print("\nOperationalization: 'has CI' = .github/workflows/ contains >=1 .yml|.yaml at the REPOSITORY "
          "ROOT of the seat's FLEET_STATE location (the only workflows GitHub runs). 'needs' is a STRING "
          "SCAN of workflow bodies, so it is a FLOOR, not a complete dependency set -- a workflow calling a "
          "script that imports pytest is not counted.")


if __name__ == "__main__":
    main()
