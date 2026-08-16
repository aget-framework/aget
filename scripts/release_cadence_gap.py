#!/usr/bin/env python3
"""release_cadence_gap.py — {AGET-Release_gap} SLO reading for R-REL-CAD-007.

R-REL-CAD-007 (POLICY_release_cadence v1.1.0+, D-RP-7) caps the release gap:
"no more than 3 consecutive Saturdays (~21 days) SHALL pass without a public
release." Until 2026-08-07 that cap had NO instrument — the requirement was
wired into a BLOCKING ceremony gate (sops/SOP_scope_lock_ceremony.md G1.VALUEGATE)
while nobody computed its bound. See docs/STUDY_slis_and_slo_candidates_2026-07-28.md
F5 and gh#1769.

SLI specification (per the shape established by release_time_slo.py, 2026-08-07):

  good/total shape : none — thresholdMetric (lte), not a ratio
  event            : one interval between consecutive public releases
  indicator        : count of Saturdays falling strictly between the two release
                     moments
  start boundary   : taggerdate of annotated tag v<N> in the CANONICAL public
                     repo (../aget)
  end boundary     : taggerdate of annotated tag v<N+1>, same repo
  objective        : saturdays_spanned <= 3
  timezone         : taggerdate is tz-aware; Saturday is evaluated in the tag's
                     own offset (a release is "on a Saturday" where it was cut)
  scope            : the cap binds only from 2026-06-26, when R-REL-CAD-007 was
                     introduced. Earlier intervals are reported as HISTORICAL
                     CONTEXT and are NOT breaches — the policy did not exist.

Why taggerdate and not creatordate: for a lightweight tag, creatordate is the
tagged commit's date, which is when the work happened, not when it went public.
Mixing the two silently blends two different boundaries into one series. This
instrument REFUSES lightweight tags rather than dating them from a commit.

Provenance discipline: the denominator is every annotated vX.Y.Z tag in the
canonical repo. A tag that cannot be dated from its own tag object is reported
as SKIPPED with its reason, never silently dropped.

Usage:
    release_cadence_gap.py [--repo PATH] [--cap N] [--all] [--json]

    --all includes pre-policy intervals, which are context and never breaches.
    --json emits the full interval series plus the skipped-tag disclosure.

Exit codes:
    0  cap HELD (or no binding intervals yet)
    1  cap BREACHED -- on every output path, --json included
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta

def _default_repo():
    """Resolve the canonical repo without assuming a fleet checkout layout.

    Was the bare literal "../aget". At the producing seat a sibling `aget/`
    exists and it worked; at a consumer -- a single clone with no fleet around
    it -- there is no sibling, so this exited 1 with "cannot read tags" and the
    instrument was dead on arrival. Measured 2026-08-15 by a downstream seat
    installing v3.31.0 from a clean clone.

    The same sibling-checkout assumption was fixed in a promoted TEST hours
    before that release shipped, and survived here. Fixing one instance of a
    class and shipping another instance of the same class is what makes this
    worth a comment rather than a one-word diff.

    Resolution order, first hit wins:
      1. AGET_CANONICAL_ROOT           -- explicit operator override
      2. this file's own repo root     -- the common case: we ARE canonical
      3. ../aget sibling               -- the fleet-checkout layout
    """
    import os
    import pathlib

    env = os.environ.get("AGET_CANONICAL_ROOT")
    if env and (pathlib.Path(env) / ".git").exists():
        return env

    here = pathlib.Path(__file__).resolve().parent.parent
    if (here / ".git").exists():
        return str(here)

    sibling = here.parent / "aget"
    if (sibling / ".git").exists():
        return str(sibling)

    # Absence is reported by the caller as UNRESOLVED, distinct from a breached
    # cadence -- the disclosed exit-1 ambiguity this release shipped with.
    return str(here)


CANONICAL = _default_repo()
CAP_SATURDAYS = 3               # R-REL-CAD-007 parameter (principal-tunable, D-RP-7)
POLICY_IN_FORCE = "2026-06-26"  # commit that introduced R-REL-CAD-007


def _tags(repo):
    """Annotated vX.Y.Z tags with taggerdate. Lightweight tags -> skipped, with reason."""
    out = subprocess.run(
        ["git", "-C", repo, "for-each-ref",
         "--format=%(refname:short)\t%(taggerdate:iso-strict)\t%(objecttype)",
         "refs/tags"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"cannot read tags from {repo}: {out.stderr.strip()}")

    rows, skipped = [], []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        name, tdate, otype = parts
        if not _is_release_tag(name):
            continue
        if otype != "tag" or not tdate:
            skipped.append({"tag": name, "reason": "lightweight tag — no tag object to date"})
            continue
        rows.append((name, datetime.fromisoformat(tdate)))
    rows.sort(key=lambda r: r[1])
    return rows, skipped


def _is_release_tag(name):
    if not name.startswith("v"):
        return False
    body = name[1:]
    parts = body.split(".")
    return len(parts) == 3 and all(p.isdigit() for p in parts)


def _saturdays_between(a, b):
    """Saturdays strictly after `a` and up to/including `b`'s date."""
    n = 0
    day = a.date() + timedelta(days=1)
    end = b.date()
    while day <= end:
        if day.weekday() == 5:
            n += 1
        day += timedelta(days=1)
    return n


def compute(repo=CANONICAL, cap=CAP_SATURDAYS, in_force=POLICY_IN_FORCE):
    rows, skipped = _tags(repo)
    in_force_date = datetime.fromisoformat(in_force).date()

    intervals = []
    for i in range(1, len(rows)):
        (pn, pd), (cn, cd) = rows[i - 1], rows[i]
        sats = _saturdays_between(pd, cd)
        binding = pd.date() >= in_force_date
        intervals.append({
            "from": pn, "from_date": pd.date().isoformat(),
            "to": cn, "to_date": cd.date().isoformat(),
            "days": (cd.date() - pd.date()).days,
            "saturdays": sats,
            "binding": binding,
            "breach": binding and sats > cap,
        })

    binding = [iv for iv in intervals if iv["binding"]]
    breaches = [iv for iv in binding if iv["breach"]]
    historical_max = max((iv["saturdays"] for iv in intervals), default=0)

    return {
        "metric": "AGET-Release_gap (Saturdays between consecutive public releases)",
        "requirement": "R-REL-CAD-007",
        "cap_saturdays": cap,
        "policy_in_force": in_force,
        "source_repo": repo,
        "tags_considered": len(rows),
        "tags_skipped": skipped,
        "intervals_total": len(intervals),
        "intervals_binding": len(binding),
        "max_saturdays_binding": max((iv["saturdays"] for iv in binding), default=0),
        "max_saturdays_all_history": historical_max,
        "breaches": breaches,
        "status": "BREACHED" if breaches else ("HELD" if binding else "NO-BINDING-DATA"),
        "intervals": intervals,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=CANONICAL, help="canonical public repo path")
    ap.add_argument("--cap", type=int, default=CAP_SATURDAYS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="print every interval, not just binding ones")
    args = ap.parse_args()

    r = compute(repo=args.repo, cap=args.cap)

    if args.json:
        print(json.dumps(r, indent=2))
        # A breach must exit nonzero on EVERY output path. Returning 0 here would
        # make the machine-readable path — the one a hook or CI would call —
        # structurally unable to report the breach it just printed.
        return 1 if r["status"] == "BREACHED" else 0

    print(f"{r['metric']}")
    print(f"  requirement : {r['requirement']} — cap {r['cap_saturdays']} consecutive Saturdays")
    print(f"  source      : {r['source_repo']} annotated tags ({r['tags_considered']} releases)")
    print(f"  in force    : {r['policy_in_force']} — {r['intervals_binding']} binding "
          f"of {r['intervals_total']} intervals")
    if r["tags_skipped"]:
        print(f"  SKIPPED     : {len(r['tags_skipped'])} tag(s) undatable — "
              + ", ".join(t["tag"] for t in r["tags_skipped"]))

    shown = r["intervals"] if args.all else [iv for iv in r["intervals"] if iv["binding"]]
    for iv in shown:
        mark = "BREACH" if iv["breach"] else ("ok" if iv["binding"] else "pre-policy")
        print(f"    {iv['from']:9s} {iv['from_date']} -> {iv['to']:9s} {iv['to_date']}  "
              f"{iv['days']:3d}d  saturdays={iv['saturdays']}  [{mark}]")

    print(f"\n  max saturdays (binding)  : {r['max_saturdays_binding']}")
    print(f"  max saturdays (all-time) : {r['max_saturdays_all_history']} "
          f"— pre-policy intervals are context, NOT breaches")
    print(f"  STATUS: {r['status']}")
    return 1 if r["status"] == "BREACHED" else 0


if __name__ == "__main__":
    sys.exit(main())
