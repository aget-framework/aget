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

    REPAIRED 2026-08-21 (v3.32 AC-3). The ladder above was correct; its FAILURE
    MODE was not. An explicit AGET_CANONICAL_ROOT that does not resolve fell
    silently through to rule 2 and the tool measured a DIFFERENT repository,
    reported it as the canonical public repo, and exited 0.

    Measured on the shipped blob 4ac6b576268b31d4ea580ea12293d7a8bbc95d1e:
      AGET_CANONICAL_ROOT=/nonexistent ... --json  ->  exit 0
      "source_repo": "<whatever repo the script happened to live in>"
      disclosure of the rejected input: none

    An operator who names a subject and is silently given another subject gets a
    confident answer about the wrong thing. That is worse than an error.

    Two rules, and they are different in kind:
      - An explicit input that does not resolve is UNAVAILABLE (exit 2). It is
        never silently replaced, and never conflated with FAIL (exit 1), which
        means "the subject was read and the cadence is breached."
      - Discovery (rules 2 and 3) applies only when NO explicit input was given.

    Returns (repo, strategy). The strategy is disclosed in output so a reader can
    always tell which rule won -- source disclosure, not just source selection.
    """
    import os
    import pathlib

    env = os.environ.get("AGET_CANONICAL_ROOT")
    if env is not None and env != "":
        if (pathlib.Path(env) / ".git").exists():
            return env, "explicit:AGET_CANONICAL_ROOT"
        # Explicit and unresolvable. Do NOT fall through: the operator named a
        # subject, and substituting another one is the defect being repaired.
        return None, f"UNAVAILABLE:explicit AGET_CANONICAL_ROOT={env!r} is not a git repository (rejected, no fallback applied)"

    here = pathlib.Path(__file__).resolve().parent.parent
    if (here / ".git").exists():
        return str(here), "discovered:own-repo-root"

    sibling = here.parent / "aget"
    if (sibling / ".git").exists():
        return str(sibling), "discovered:sibling-aget"

    return None, "UNAVAILABLE:no canonical repo found by explicit input, own repo root, or sibling aget/"


def resolve_source(cli_repo=None):
    """Resolve the subject across EVERY input channel, with one rule.

    Precedence: explicit --repo > explicit AGET_CANONICAL_ROOT > discovery.

    v3.32 Phase-3 review repair. The prior version gated only the environment
    variable. `--repo` defaulted to the module-level CANONICAL computed at IMPORT
    time, so an explicit `--repo` never reached this gate at all:

      * an unresolvable --repo fell through to _tags(), which raised and exited 1
        with EMPTY stdout -- indistinguishable from BREACHED, which is the exact
        conflation this module exists to end (findings 1, 2);
      * discovery had already run at import regardless of --repo (finding 3);
      * and source_strategy reported how DISCOVERY resolved even when --repo chose
        the subject, so the tool measured one repository and disclosed a different
        strategy for choosing it (finding 4) -- a false headline claim, since this
        module promises source DISCLOSURE, not merely source selection.

    Fixing only --repo would repeat the original error one channel over, so every
    channel now returns through this one function.
    """
    import os
    import pathlib as _pl

    if cli_repo is not None and cli_repo != "":
        if (_pl.Path(cli_repo) / ".git").exists():
            return str(cli_repo), "explicit:--repo"
        return None, (f"UNAVAILABLE:explicit --repo={cli_repo!r} is not a git repository "
                      "(rejected, no fallback applied)")

    env = os.environ.get("AGET_CANONICAL_ROOT")
    if env is not None and env != "":
        if (_pl.Path(env) / ".git").exists():
            return env, "explicit:AGET_CANONICAL_ROOT"
        return None, (f"UNAVAILABLE:explicit AGET_CANONICAL_ROOT={env!r} is not a git repository "
                      "(rejected, no fallback applied)")

    here = _pl.Path(__file__).resolve().parent.parent
    if (here / ".git").exists():
        return str(here), "discovered:own-repo-root"
    sibling = here.parent / "aget"
    if (sibling / ".git").exists():
        return str(sibling), "discovered:sibling-aget"
    return None, "UNAVAILABLE:no canonical repo found by explicit input, own repo root, or sibling aget/"


CANONICAL, CANONICAL_STRATEGY = _default_repo()
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
        rows.append((name, _parse_tagger_date(tdate)))
    rows.sort(key=lambda r: r[1])
    return rows, skipped



def _parse_tagger_date(value):
    """Parse a git taggerdate across Python versions.

    Python 3.11 accepts a terminal `Z` and colon-less UTC offsets; 3.10 does not
    and raises ValueError. git emits either form depending on log.date / config,
    so the shipped script parsed fine on 3.11+ and died on 3.10 -- exiting 1 with
    empty stdout, which the caller could not distinguish from a real BREACHED
    result. Normalizing here keeps the version difference out of every call site.
    """
    s = (value or "").strip()
    if not s:
        raise ValueError("empty taggerdate")
    if s.endswith(("Z", "z")):
        s = s[:-1] + "+00:00"
    # colon-less offset: "+0000" / "-0730" -> "+00:00" / "-07:30"
    if len(s) >= 5 and s[-5] in "+-" and s[-3] != ":":
        s = s[:-2] + ":" + s[-2:]
    return datetime.fromisoformat(s)


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


def compute(repo=CANONICAL, cap=CAP_SATURDAYS, in_force=POLICY_IN_FORCE, strategy=None):
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
        "source_strategy": strategy if strategy is not None else CANONICAL_STRATEGY,
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
    ap.add_argument("--repo", default=None,
                    help="canonical public repo path (explicit; rejected loudly if not a git repo)")
    ap.add_argument("--cap", type=int, default=CAP_SATURDAYS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="print every interval, not just binding ones")
    args = ap.parse_args()

    # Every channel resolves here, after parsing. Resolving at import time is what
    # let --repo bypass the gate entirely.
    repo, strategy = resolve_source(args.repo)

    # UNAVAILABLE gate (v3.32 AC-3). Fires BEFORE any measurement, because a
    # measurement of a substituted subject is worse than no measurement.
    # Exit 2 is deliberately distinct from exit 1: 1 means "read the subject,
    # cadence is BREACHED"; 2 means "never read the declared subject at all".
    # Collapsing them to "nonzero" is the conflation this repair exists to end.
    if repo is None:
        msg = strategy.split("UNAVAILABLE:", 1)[-1]
        if args.json:
            print(json.dumps({
                "metric": "AGET-Release_gap (Saturdays between consecutive public releases)",
                "status": "UNAVAILABLE",
                "source_repo": None,
                "source_strategy": strategy,
                "reason": msg,
            }, indent=2))
        else:
            print(f"UNAVAILABLE: {msg}", file=sys.stderr)
        return 2

    r = compute(repo=repo, cap=args.cap, strategy=strategy)

    if args.json:
        print(json.dumps(r, indent=2))
        # A breach must exit nonzero on EVERY output path. Returning 0 here would
        # make the machine-readable path — the one a hook or CI would call —
        # structurally unable to report the breach it just printed.
        return 1 if r["status"] == "BREACHED" else 0

    print(f"{r['metric']}")
    print(f"  requirement : {r['requirement']} — cap {r['cap_saturdays']} consecutive Saturdays")
    print(f"  source      : {r['source_repo']} annotated tags ({r['tags_considered']} releases)")
    # Source SELECTION without source STRATEGY is the half-disclosure this module's
    # own docstring forbids: "a reader can always tell which rule won". Both --json
    # paths carried source_strategy from the start; this path, the one an operator
    # actually reads, printed only the path. An explicitly-named subject and a
    # discovered one rendered identically, which is precisely the distinction the
    # 2026-08-21 repair exists to make visible. Found by rehearsing the shipped
    # instrument end to end, 2026-08-23.
    print(f"  resolved by : {r['source_strategy']}")
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
