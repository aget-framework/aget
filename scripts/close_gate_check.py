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


def scan(text: str):
    """Return a list of (kind, detail) conformance violations."""
    violations = []
    in_closure = False
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

    if not violations:
        print(f"close-gate: PASS — no unchecked conformance signals in {fp.name}")
        return 0

    print(f"close-gate: BLOCK — {len(violations)} unchecked conformance signal(s) in {fp.name} "
          f"(L178 override available with reason):")
    if not args.quiet:
        kinds = {'gate_status_pending': 'Gate still Pending/In-Progress',
                 'vtest_pending': 'V-test row PENDING',
                 'unchecked_closure_item': 'Unchecked closure/finalization item'}
        for kind, detail in violations[:30]:
            print(f"  - [{kinds.get(kind, kind)}] {detail}")
    return 2


if __name__ == '__main__':
    sys.exit(main())
