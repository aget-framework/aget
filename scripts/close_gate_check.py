#!/usr/bin/env python3
"""
close_gate_check.py — Close-Gate Conformance Guard (v3.20 Tier-1 item C-P1).

Blocks marking a PROJECT_PLAN (or session file) COMPLETE while it still carries
unchecked conformance signals: Pending/In-Progress gate status, PENDING V-test
rows, or unchecked Closure/Finalization checklist items.

Structural sibling of SOP_verify_with_consumer (C-P4, Advisory): C-P4 is the
discipline ("verify with the consumer's check"); this is the structural guard
that makes "all V-tests checked" a precondition of COMPLETE.

Invoked by /aget-close-project and /aget-close-session before a status->COMPLETE
transition. Advisory (ADR-008): reports violations + nonzero exit; the principal
may override with reason (L178).

Exit codes:
  0 = clean (no blocking unchecked conformance signals)
  2 = violations found (block COMPLETE)
  3 = usage / file error

Owning initiative: INIT-PRINCIPLED-EXECUTION (Healthy Friction).
"""
import argparse
import re
import sys
from pathlib import Path

# Closure/Finalization checklist section headers whose unchecked items block COMPLETE.
_CLOSURE_SECTION_RE = re.compile(
    r'^#{1,4}\s*(Closure Checklist|Finalization Checklist)\b', re.IGNORECASE)
_ANY_SECTION_RE = re.compile(r'^#{1,4}\s+\S')
_UNCHECKED_RE = re.compile(r'^\s*[-*]\s*\[\s*\]\s+(.*)$')
_GATE_STATUS_PENDING_RE = re.compile(
    r'\*\*Gate_Status:?\*\*:?\s*(Pending|In Progress)\b', re.IGNORECASE)
# A V-test mapping row marked PENDING (table row containing the token).
_VTEST_PENDING_RE = re.compile(r'\|\s*Gate[^|]*\|[^|]*\|\s*PENDING\s*\|', re.IGNORECASE)

# Substance check (#1568, v3.25 C-25-06): a closure-class section whose boxes are
# all [x] but whose prose is placeholder text is a false-clean — detect the
# placeholders, not just the checkbox state (L671: report-without-block is decorative).
_SUBSTANCE_SECTION_RE = re.compile(
    r'^#{1,4}\s*(Retrospective|What Worked|What Didn\'t Work|Closure Checklist|'
    r'Finalization Checklist|Velocity Analysis)\b', re.IGNORECASE)
_PLACEHOLDER_RE = re.compile(
    r'^\s*(?:\d+\.\s*)?(?:[-*]\s*)?(\{TBD\}|TBD|_\(pending\)_|\(pending\)|\.\.\.|N/A — fill later)\s*$',
    re.IGNORECASE)


def scan(text: str):
    """Return a list of (kind, detail) conformance violations."""
    violations = []
    in_closure = False
    in_substance = False
    for raw in text.splitlines():
        line = raw.rstrip('\n')

        # Track whether we're inside a Closure/Finalization checklist section.
        if _ANY_SECTION_RE.match(line):
            in_closure = bool(_CLOSURE_SECTION_RE.match(line))

        if in_closure:
            m = _UNCHECKED_RE.match(line)
            if m:
                violations.append(('unchecked_closure_item', m.group(1).strip()[:100]))

        if _GATE_STATUS_PENDING_RE.search(line):
            violations.append(('gate_status_pending', line.strip()[:100]))

        if _VTEST_PENDING_RE.search(line):
            violations.append(('vtest_pending', line.strip()[:100]))

        if _ANY_SECTION_RE.match(line):
            in_substance = bool(_SUBSTANCE_SECTION_RE.match(line))
        if in_substance and _PLACEHOLDER_RE.match(line):
            violations.append(('placeholder_substance', line.strip()[:100]))

    return violations


def main(argv=None):
    p = argparse.ArgumentParser(description="Close-gate conformance guard (C-P1).")
    p.add_argument('path', help="PROJECT_PLAN or session markdown file being closed")
    p.add_argument('--quiet', '-q', action='store_true', help="Only print the verdict line")
    args = p.parse_args(argv)

    fp = Path(args.path)
    if not fp.is_file():
        print(f"close-gate: ERROR — file not found: {fp}", file=sys.stderr)
        return 3

    violations = scan(fp.read_text(encoding='utf-8', errors='replace'))

    # Release-class BLOCKING guard (#1554, v3.25 C-25-06): when the instance
    # carries scripts/release_close_guard.py and the plan is release-class,
    # the guard's verdict joins the violation set (exit 2 => BLOCK). Absence
    # of the guard is expected pre-adoption (L601) — no penalty.
    guard = Path('scripts/release_close_guard.py')
    if guard.is_file() and re.search(r'release', fp.name, re.IGNORECASE):
        import subprocess
        try:
            r = subprocess.run([sys.executable, str(guard), str(fp)],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 2:
                tail = (r.stdout or r.stderr).strip().splitlines()
                violations.append(('release_close_guard_block',
                                   tail[-1][:100] if tail else 'guard BLOCK (exit 2)'))
        except Exception as e:
            violations.append(('release_close_guard_error', str(e)[:100]))

    if not violations:
        print(f"close-gate: PASS — no unchecked conformance signals in {fp.name}")
        return 0

    print(f"close-gate: BLOCK — {len(violations)} unchecked conformance signal(s) in {fp.name} "
          f"(L178 override available with reason):")
    if not args.quiet:
        kinds = {'gate_status_pending': 'Gate still Pending/In-Progress',
                 'vtest_pending': 'V-test row PENDING',
                 'unchecked_closure_item': 'Unchecked closure/finalization item',
                 'placeholder_substance': 'Closure-section placeholder prose (substance, #1568)',
                 'release_close_guard_block': 'Release-completion guard BLOCK (#1554)',
                 'release_close_guard_error': 'Release-completion guard error'}
        for kind, detail in violations[:30]:
            print(f"  - [{kinds.get(kind, kind)}] {detail}")
    return 2


if __name__ == '__main__':
    sys.exit(main())
