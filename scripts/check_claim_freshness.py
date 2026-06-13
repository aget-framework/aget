#!/usr/bin/env python3
"""
check_claim_freshness.py — Citation/claim freshness gate (C-22-04 / E4, v3.22).

Mechanizes the verify-before-assert discipline (L1046 grep-before-assert; L908
memory-claim verification) at the artifact-citation layer. A governed artifact
that pairs an issue identifier with a state assertion — `#1461 CLOSED`,
`#1120 OPEN` — is making a CLAIM UNDER TEST, not stating a premise. This gate
re-derives each such claim at the point of use and flags drift.

Governing principle (Theme B, paired with C-22-01 the deployer):
  **"Propagation SHALL carry paired point-of-use verify"** — distributing a
  claim (citing it) without a verify path lets staleness compound silently.
  (Demonstrated live this cycle: #1120's "10 templates × 15 missing skills"
  was 3.4× stale vs the real gap.) INIT-PRINCIPLED-EXECUTION Stream 2.

Modes:
  - offline (default): inventory the machine-checkable claims (count, locations).
  - --online: re-derive each issue's state via `gh issue view` and report drift.
  - --strict: exit 1 when --online finds ≥1 drifted claim (CI / release gate).

Usage:
  python3 scripts/check_claim_freshness.py planning/ docs/
  python3 scripts/check_claim_freshness.py --online --strict planning/VERSION_SCOPE_v3.22.0.md
  python3 scripts/check_claim_freshness.py --self-test

Exit codes: 0 ok / 1 (--strict) drift found / 2 usage-or-env error.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# "#1461 CLOSED", "gh#1120 OPEN", "#1626 MERGED"
CLAIM_RE = re.compile(r"(?:gh)?#(\d{3,5})\s+(OPEN|CLOSED|MERGED)\b")
# For issues, MERGED is not a state — treat an asserted MERGED as CLOSED-equivalent.
ASSERTED_TO_ACTUAL = {"OPEN": "OPEN", "CLOSED": "CLOSED", "MERGED": "CLOSED"}


def extract_claims(text: str):
    """Yield (issue:int, asserted_state:str, lineno:int) for each checkable claim."""
    for i, line in enumerate(text.splitlines(), 1):
        for m in CLAIM_RE.finditer(line):
            yield int(m.group(1)), m.group(2).upper(), i


def iter_files(paths):
    for p in paths:
        path = Path(p)
        if path.is_dir():
            yield from sorted(path.rglob("*.md"))
        elif path.is_file():
            yield path


def gh_state(issue: int) -> str | None:
    """Actual issue state via gh ('OPEN'/'CLOSED'), or None if unavailable."""
    try:
        r = subprocess.run(
            ["gh", "issue", "view", str(issue), "--repo", "gmelli/aget-aget", "--json", "state",
             "-q", ".state"],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0:
            return None
        return r.stdout.strip().upper() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check(paths, online: bool, state_fn=gh_state):
    """Return (claims, drifts). drifts populated only when online."""
    claims, drifts = [], []
    # de-dupe (issue, asserted) so we hit gh once per distinct claim
    seen_pairs = {}
    for f in iter_files(paths):
        rel = str(f.relative_to(REPO_ROOT)) if str(f).startswith(str(REPO_ROOT)) else str(f)
        for issue, asserted, lineno in extract_claims(f.read_text(encoding="utf-8", errors="replace")):
            claims.append({"issue": issue, "asserted": asserted, "file": rel, "line": lineno})
            seen_pairs.setdefault((issue, asserted), []).append(f"{rel}:{lineno}")

    if online:
        actual_cache = {}
        for (issue, asserted), locs in seen_pairs.items():
            if issue not in actual_cache:
                actual_cache[issue] = state_fn(issue)
            actual = actual_cache[issue]
            if actual is None:
                continue  # unresolvable — not a drift, just unchecked
            if ASSERTED_TO_ACTUAL[asserted] != actual:
                drifts.append({"issue": issue, "asserted": asserted, "actual": actual, "locations": locs})
    return claims, drifts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", default=["planning", "docs"], help="Files/dirs to scan")
    ap.add_argument("--online", action="store_true", help="Re-derive each claim via gh")
    ap.add_argument("--strict", action="store_true", help="Exit 1 on drift (CI gate)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    paths = args.paths or ["planning", "docs"]
    claims, drifts = check(paths, args.online)

    if args.json:
        print(json.dumps({"claims": len(claims), "online": args.online,
                          "drifts": drifts}, indent=2))
    else:
        print(f"=== claim-freshness gate (C-22-04) — {len(claims)} checkable #issue+state claims ===")
        if not args.online:
            print("offline: inventory only. Pass --online to re-derive states via gh.")
        else:
            if not drifts:
                print(f"All resolvable claims fresh (0 drift).")
            for d in drifts:
                print(f"  DRIFT #{d['issue']}: asserted {d['asserted']} but actually {d['actual']}")
                for loc in d["locations"]:
                    print(f"        {loc}")

    return 1 if (args.strict and drifts) else 0


def _self_test() -> int:
    import tempfile
    fails = []
    fake = {101: "OPEN", 102: "CLOSED", 103: "CLOSED"}  # 3+ digits, per CLAIM_RE
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.md"
        f.write_text("#101 OPEN ok\n#102 OPEN stale\n#103 MERGED (ok, merged==closed)\n#101 CLOSED also-stale\n")
        claims, drifts = check([str(f)], online=True, state_fn=lambda i: fake.get(i))
        if len(claims) != 4:
            fails.append(f"expected 4 claims, got {len(claims)}")
        drifted = {(d["issue"], d["asserted"]) for d in drifts}
        if (102, "OPEN") not in drifted:
            fails.append("missed drift: #102 asserted OPEN, actually CLOSED")
        if (101, "CLOSED") not in drifted:
            fails.append("missed drift: #101 asserted CLOSED, actually OPEN")
        if (103, "MERGED") in drifted:
            fails.append("false drift: #103 MERGED should equal actual CLOSED")
        if (101, "OPEN") in drifted:
            fails.append("false drift: #101 OPEN matches actual OPEN")
    if fails:
        print("SELF-TEST FAIL:\n  " + "\n  ".join(fails))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
