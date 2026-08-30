#!/usr/bin/env python3
"""Self-assess this AGET's conformance to its own declared controls.

WHY THIS EXISTS
---------------
This seat has 120+ declared control scripts. It still landed, in one session, a git-history pointer to
an artifact that its own promotion-boundary sanitizer rejects outright. The controls were not missing.
Nothing ran them against the artifact before it landed.

That is the gap this script closes: it asks not "do controls exist" but **"would this seat pass its own
controls right now, on what it is about to record."**

THREE CHECKS, each three-state (PASS / FAIL / UNAVAILABLE per CONVENTION_check_three_state_contract).

  A. UNLANDED CONTENT A DECLARED CONTROL WOULD REJECT.
     Every untracked or modified file in the recordable trees is fed to the existing
     promotion-boundary sanitizer. An artifact that has not landed yet is the only point at which
     rejection is cheap.

  B. DECLARED CONTROLS THAT NOTHING INVOKES.
     A control referenced by no health check, test, hook, or skill is a control that will never fire.
     "Exists" and "runs" are different claims and this seat has repeatedly conflated them.

  C. L-DOC INDEX COHERENCE.
     Delegated to the existing auditor rather than reimplemented — reimplementing a control is how
     two controls come to disagree.

A LIMITATION OF CHECK A, STATED BECAUSE A DETECTOR THAT SILENTLY MISSES ITS MOTIVATING CASE IS WORSE
THAN NO DETECTOR
--------------------------------------------------------------------------------------------------
Check A's foreign-reference predicate matches ONE shape: seat-shaped tokens (`private-<x>-aget`). The
artifact that motivated this script carries a different shape — an internal project identifier and
short seat ALIASES — and check A therefore **does not flag it**. The promotion sanitizer does flag it,
but the sanitizer also flags this seat's own name in its own private artifacts (it is calibrated for the
public boundary), so its raw verdict is ~100% FAIL here and unusable as a signal without further
discrimination that is not yet built.

So: check A currently detects foreign SEATS, not foreign PROJECTS or ALIASES. That is a real coverage
hole in the direction that matters, it is named here rather than discovered later, and closing it needs
a discriminating predicate for alias- and project-shaped identifiers.

A MEASURED TRAP THIS ENCODES
----------------------------
**The sanitizer exits 0 on rejecting input.** Measured 2026-08-29: fed an artifact it reports as
"Content contains private information", it returns exit code 0. Any caller wiring it with `&&`, `set -e`,
or a CI step's exit status gets a silent pass. So this script parses its OUTPUT and never its exit code,
and check A reports UNAVAILABLE rather than PASS if the expected marker is absent from that output —
a detector whose verdict cannot be read is not a passing detector.

SCOPE, AND A RULING THIS SCRIPT DELIBERATELY DOES NOT CROSS
-----------------------------------------------------------
An existing boundary-cleanup ruling places `sessions/`, `.aget/evolution/`, `planning/` and
`.aget/logs/` out of scope for *cleaning*, by decision and not by oversight. This script **reports and
never edits**. Reporting that an unlanded artifact would fail a control is not cleaning it, and nothing
here should be read as authority to clean those trees. Where a report and that ruling appear to
conflict, the conflict is the principal's to resolve.

Usage:
    python3 scripts/self_assess_conformance.py [--json] [--check A|B|C]
    python3 scripts/self_assess_conformance.py --self-test
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SANITIZER = REPO / ".aget/patterns/github/sanitize_issue_content.py"
INDEX_AUDITOR = REPO / "scripts/audit_ldoc_index.py"

# The sanitizer signals rejection in prose, not in its exit code (see module docstring).
REJECT_MARKER = "contains private information"
ACCEPT_MARKER = "No private information"

RECORDABLE_TREES = ("sessions/", ".aget/evolution/", "planning/", "governance/", "inbox/outbound/",
                    "docs/", "sops/", "knowledge/", "ontology/")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".jsonl"}

CONTROL_GLOBS = ("scripts/check_*.py", "scripts/validate_*.py", "scripts/audit_*.py",
                 "scripts/verify_*.py")
# Where a control must be referenced to be considered wired.
INVOCATION_ROOTS = ("scripts/health_check.py", "scripts/health_check_ext.py", "scripts/wake_up.py",
                    "scripts/wake_up_ext.py", "scripts/wind_down.py", "scripts/wind_down_ext.py",
                    "tests", ".claude/hooks", ".claude/skills", "sops", ".github")

PASS, FAIL, UNAVAILABLE = "PASS", "FAIL", "UNAVAILABLE"


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True).stdout


def candidate_files() -> list[str]:
    """Untracked or modified files in the recordable trees — what is about to land."""
    out = []
    for line in _git("status", "--porcelain").splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if not any(path.startswith(t) for t in RECORDABLE_TREES):
            continue
        if pathlib.Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        out.append(path)
    return sorted(out)


def sanitize_verdict(path: pathlib.Path) -> tuple[str, str]:
    """Return (verdict, detail). NEVER reads the sanitizer's exit code — it is 0 either way."""
    if not SANITIZER.is_file():
        return UNAVAILABLE, "sanitizer absent at its declared path"
    try:
        proc = subprocess.run([sys.executable, str(SANITIZER), "--check"],
                              input=path.read_text(errors="replace"),
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return UNAVAILABLE, f"sanitizer did not run: {exc}"
    text = proc.stdout + proc.stderr
    if REJECT_MARKER.lower() in text.lower():
        hits = re.findall(r'^\s*-\s+"(.+)"\s*$', text, re.M)
        return FAIL, "; ".join(hits[:6]) if hits else "rejected, no pattern echoed"
    if ACCEPT_MARKER.lower() in text.lower():
        return PASS, ""
    # Neither marker: the verdict is unreadable. Not a pass.
    return UNAVAILABLE, "sanitizer produced no readable verdict"


def own_identifiers() -> set[str]:
    """Tokens that are THIS seat's own and are expected in its own private artifacts."""
    own = {REPO.name}
    idf = REPO / ".aget/identity.json"
    if idf.is_file():
        try:
            import json as _j
            d = _j.loads(idf.read_text())
            for k in ("agent_name", "name", "agent"):
                if isinstance(d.get(k), str):
                    own.add(d[k])
        except Exception:
            pass
    return {o for o in own if o}


SEAT_TOKEN = re.compile(r"private-[A-Za-z0-9_.-]+-(?:aget|AGET)")


def foreign_seat_tokens(text: str, own: set[str]) -> list[str]:
    """Seat-shaped tokens that are not this seat's own — the finding that actually matters here.

    No foreign name is hardcoded anywhere in this file; the set is derived from the text under test.
    """
    return sorted({m for m in SEAT_TOKEN.findall(text) if m not in own})


def check_a() -> dict:
    files = candidate_files()
    if not files:
        return {"check": "A", "name": "unlanded content vs declared controls", "state": PASS,
                "detail": "no unlanded text artifacts in the recordable trees", "rows": []}
    own = own_identifiers()
    rows, unreadable = [], 0
    for rel in files:
        text = (REPO / rel).read_text(errors="replace")
        foreign = foreign_seat_tokens(text, own)
        verdict, detail = sanitize_verdict(REPO / rel)
        if verdict == UNAVAILABLE:
            unreadable += 1
        if foreign:
            rows.append({"file": rel, "verdict": FAIL,
                         "detail": f"foreign seat reference: {', '.join(foreign[:4])}"})
    state = FAIL if rows else (UNAVAILABLE if unreadable else PASS)
    return {"check": "A", "name": "unlanded content carrying foreign-seat references",
            "state": state,
            "detail": (f"{len(files)} unlanded artifact(s) scanned against {len(own)} own "
                       f"identifier(s); {len(rows)} carry a foreign seat reference; "
                       f"{unreadable} returned no readable sanitizer verdict"),
            "denominator": len(files), "rows": rows}


def check_b() -> dict:
    controls = sorted({p.relative_to(REPO).as_posix()
                       for g in CONTROL_GLOBS for p in REPO.glob(g)})
    if not controls:
        return {"check": "B", "name": "declared controls that nothing invokes",
                "state": UNAVAILABLE, "detail": "no control scripts matched the globs", "rows": []}
    haystack = []
    for root in INVOCATION_ROOTS:
        p = REPO / root
        if p.is_file():
            haystack.append(p.read_text(errors="replace"))
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in {".py", ".sh", ".md", ".yaml", ".yml",
                                                        ".json", ".toml"}:
                    haystack.append(f.read_text(errors="replace"))
    blob = "\n".join(haystack)
    unwired = [c for c in controls if pathlib.Path(c).name not in blob]
    return {"check": "B", "name": "declared controls that nothing invokes",
            "state": FAIL if unwired else PASS,
            "detail": f"{len(unwired)} of {len(controls)} control scripts referenced by no health "
                      f"check, test, hook, skill, SOP or workflow",
            "denominator": len(controls), "rows": [{"file": c} for c in unwired]}


def check_c() -> dict:
    if not INDEX_AUDITOR.is_file():
        return {"check": "C", "name": "L-doc index coherence", "state": UNAVAILABLE,
                "detail": "index auditor absent", "rows": []}
    proc = subprocess.run([sys.executable, str(INDEX_AUDITOR)],
                          capture_output=True, text=True, cwd=REPO)
    text = proc.stdout + proc.stderr
    fails = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("FAIL")]
    return {"check": "C", "name": "L-doc index coherence",
            "state": FAIL if proc.returncode else PASS,
            "detail": "; ".join(fails[:4]) if fails else "index surface clean",
            "rows": []}


CHECKS = {"A": check_a, "B": check_b, "C": check_c}


def self_test() -> int:
    """Both polarities on the two predicates that can silently pass."""
    failures = []

    # The sanitizer-verdict reader must not treat an unreadable verdict as PASS.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "x.md"
        f.write_text("nothing notable here\n")
        global SANITIZER
        real = SANITIZER
        SANITIZER = pathlib.Path(td) / "absent.py"
        if sanitize_verdict(f)[0] != UNAVAILABLE:
            failures.append("  missing sanitizer must yield UNAVAILABLE, not PASS")
        # A sanitizer that prints nothing and exits 0 must NOT read as PASS.
        stub = pathlib.Path(td) / "silent.py"
        stub.write_text("import sys; sys.stdin.read(); sys.exit(0)\n")
        SANITIZER = stub
        if sanitize_verdict(f)[0] != UNAVAILABLE:
            failures.append("  silent exit-0 sanitizer must yield UNAVAILABLE, not PASS")
        # A sanitizer that rejects while exiting 0 must read as FAIL — the measured real behaviour.
        rej = pathlib.Path(td) / "rejecting.py"
        rej.write_text("import sys; sys.stdin.read();"
                       " print('Content contains private information'); sys.exit(0)\n")
        SANITIZER = rej
        if sanitize_verdict(f)[0] != FAIL:
            failures.append("  rejecting exit-0 sanitizer must yield FAIL, not PASS")
        # Positive control: an accepting sanitizer reads PASS.
        acc = pathlib.Path(td) / "accepting.py"
        acc.write_text("import sys; sys.stdin.read(); print('No private information found');"
                       " sys.exit(0)\n")
        SANITIZER = acc
        if sanitize_verdict(f)[0] != PASS:
            failures.append("  accepting sanitizer must yield PASS")
        SANITIZER = real

    # Check B must not report every control unwired when the haystack is real.
    b = check_b()
    if b["state"] not in (PASS, FAIL) or b.get("denominator", 0) == 0:
        failures.append("  check B produced no usable denominator")
    elif len(b["rows"]) == b["denominator"]:
        failures.append("  check B reports 100% unwired — haystack almost certainly not read")

    if failures:
        print("SELF-TEST FAIL")
        print("\n".join(failures))
        return 1
    print("SELF-TEST PASS (4 sanitizer-verdict polarities + 1 check-B sanity control)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", choices=sorted(CHECKS))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    selected = [args.check] if args.check else sorted(CHECKS)
    results = [CHECKS[k]() for k in selected]

    if args.json:
        print(json.dumps({"results": results,
                          "reports_only": "this script never edits; see module docstring"}, indent=2))
    else:
        print("SELF-ASSESSED CONFORMANCE — this seat, right now")
        print("reports only; never edits. Sanitizer verdict is parsed from output, never exit code.\n")
        for r in results:
            mark = {PASS: "OK  ", FAIL: "FAIL", UNAVAILABLE: "??  "}[r["state"]]
            print(f"  {mark} {r['check']}. {r['name']}")
            print(f"       {r['detail']}")
            for row in r["rows"][:12]:
                extra = f" — {row['detail']}" if row.get("detail") else ""
                print(f"         - {row['file']}{extra}")
            if len(r["rows"]) > 12:
                print(f"         … and {len(r['rows']) - 12} more")
            print()
        worst = FAIL if any(r["state"] == FAIL for r in results) else (
            UNAVAILABLE if any(r["state"] == UNAVAILABLE for r in results) else PASS)
        print(f"OVERALL: {worst}")

    return 1 if any(r["state"] == FAIL for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
