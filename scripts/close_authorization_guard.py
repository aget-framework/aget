#!/usr/bin/env python3
"""
Close Authorization Guard  (Q3:A / L1102 structural hardening)

Prevents the v3.23 defect: a PROJECT_PLAN closed to a terminal status with a
PRINCIPAL-ATTRIBUTED reason ("principal-ruled ...") that had NO linked authorizing
event, AND whose irreversible identity-level consequence (burning the v3.23.0 public
version number / "private milestone" / "fold to v3.24") was never made legible at
decision time.

Two checks on a terminal close:
  (A) Authorization-event pointer — if the close reason ATTRIBUTES the decision to
      the principal, it MUST link the authorizing EVENT (a GO, an AskUserQuestion
      selection, a /aget-go id, an Authorization-log entry, a dated principal quote).
      Free-text "(principal-ruled)" alone = FAIL.  [L1102 root]
  (B) Consequence legibility — if the close carries an IRREVERSIBLE / identity-level
      consequence marker (private milestone, skip/burn a public version, fold to a
      later version, abandon a public release), that consequence MUST be made legible
      (an explicit acknowledgement) — not buried under a mechanism label.  [Q3:A]

Agent-autonomous closes (no principal attribution — e.g. an L-doc, a dogfood COMPLETE)
are allowed: many closes are legitimately autonomous per the Decision Authority Matrix.
The guard only bites when the close LEANS ON principal authority or ships an
irreversible consequence.

Exit: 0 = PASS, 1 = FAIL, 2 = usage/error.
"""
import argparse
import re
import sys

# --- terminal status (a close) vs reopened/void ------------------------------
TERMINAL = re.compile(r"\b(CLOSED|COMPLETE|ABANDONED|SUPERSEDED)\b", re.I)
NOT_A_CLOSE = re.compile(r"\b(REOPENED|IN PROGRESS|VOID|DRAFT|ACTIVE)\b", re.I)

# --- principal attribution: the close leans on principal authority ------------
PRINCIPAL_ATTRIB = re.compile(
    r"principal[-\s]?(ruled|rule|approved|authoriz|decision|decided|chose|selected|elected|directed)"
    r"|per\s+principal|principal'?s\s+(call|ruling|decision|selection|directive)"
    r"|(ruled|approved|authoriz\w*|decided|directed|selected|chosen?)\s+by\s+(the\s+)?principal",  # passive
    re.I,
)

# --- an authorization EVENT pointer (what makes attribution checkable) ---------
EVENT_POINTER = re.compile(
    r"/aget-go"                       # recorded GO skill
    r"|aget-go\b"
    r"|Authorization log"             # the in-plan authorization-event table
    r"|AskUserQuestion"
    r"|\bQ\d+\s*:\s*[A-D]\b"          # an /aget-ask selection (Q1:A)
    r"|\bGO\b[^.\n]{0,40}\b20\d\d-\d\d-\d\d"   # "GO ... 2026-06-21"
    r"|20\d\d-\d\d-\d\d[^.\n]{0,40}\bGO\b"
    r"|principal[-\s]?typed"
    r"|principal (chose|selected|typed)[^.\n]{0,60}[\"'`]"  # quotes the selection
    r"|gh#\d+[^.\n]{0,30}approv",
    re.I,
)

# --- irreversible / identity-level consequence markers ------------------------
IRREVERSIBLE = re.compile(
    r"private milestone"
    r"|fold(ed)?\s+to\s+v?\d"
    r"|skip(p?ing|ped)?\s+(a\s+)?(public\s+)?version"
    r"|dead\s+version"
    r"|burn(ing|t|ed)?\s+(the\s+)?(public\s+)?version"
    r"|abandon(ed|ing)?\s+(the\s+)?(public\s+)?release"
    r"|never\s+public"
    r"|no\s+public\s+(push|release)",
    re.I,
)

# --- consequence made legible (an explicit acknowledgement of the effect) -----
LEGIBLE = re.compile(
    r"consequence\s*:"
    r"|irreversible"
    r"|identity[-\s]level"
    r"|made legible"
    r"|skips?\s+(the\s+)?public\s+version\s+number"
    r"|leaves?\s+a\s+(permanent\s+)?gap"
    r"|standing requirement",
    re.I,
)


def status_declaration(text):
    """The STATUS VALUE only (first ~120 chars after Plan_Status/Status) — so terminal
    vs reopened/draft is decided by the declared status, not by words like 'draft'
    appearing elsewhere in the reason paragraph (dogfood bug: 'landed draft')."""
    m = re.search(r"\*\*Plan_Status\*\*\s*:\s*(.{0,120})", text, re.I)
    if not m:
        m = re.search(r"\*\*Status\*\*\s*:\s*(.{0,120})", text, re.I)
    return m.group(1) if m else text[:120]


def evaluate(text):
    """Return (verdict, issues) for a close-block of text. verdict in PASS/FAIL."""
    issues = []

    decl = status_declaration(text)
    is_terminal = bool(TERMINAL.search(decl)) and not NOT_A_CLOSE.search(decl)
    if not is_terminal:
        return "PASS", ["not a terminal close (reopened/void/active) — guard N/A"]

    attributed = bool(PRINCIPAL_ATTRIB.search(text))
    has_pointer = bool(EVENT_POINTER.search(text))
    irreversible = bool(IRREVERSIBLE.search(text))
    legible = bool(LEGIBLE.search(text))

    # Check A — principal-attributed close needs a linked authorization event
    if attributed and not has_pointer:
        issues.append(
            "CHECK-A FAIL: close is principal-ATTRIBUTED but has no authorization-EVENT "
            "pointer (a GO / AskUserQuestion selection / /aget-go / Authorization log / "
            "dated principal quote). Free-text '(principal-ruled)' is not provenance. [L1102]"
        )

    # Check B — irreversible consequence must be made legible
    if irreversible and not legible:
        issues.append(
            "CHECK-B FAIL: close carries an IRREVERSIBLE/identity-level consequence "
            "(version skip / private milestone / fold) that is NOT made legible. Surface "
            "the irreversible effect explicitly; do not bury it under a mechanism label. [Q3:A]"
        )

    verdict = "FAIL" if issues else "PASS"
    if verdict == "PASS":
        ok = []
        if attributed:
            ok.append("principal-attributed + event-pointer present")
        if irreversible:
            ok.append("irreversible consequence made legible")
        if not attributed and not irreversible:
            ok.append("agent-autonomous close, no irreversible consequence — allowed")
        issues = ok
    return verdict, issues


def extract_close_block(path):
    """Heuristic: the Plan_Status line + its paragraph carry the close record."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    block = []
    for i, ln in enumerate(lines):
        if re.search(r"\*\*Plan_Status\*\*|\*\*Status\*\*\s*:", ln):
            block = lines[i : i + 12]
            break
    return "".join(block) if block else "".join(lines[:30])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Close Authorization Guard (Q3:A / L1102)")
    ap.add_argument("path", nargs="?", help="PROJECT_PLAN file to check")
    ap.add_argument("--text", help="evaluate a literal close-block string (for tests)")
    args = ap.parse_args(argv)

    if args.text is not None:
        text = args.text
    elif args.path:
        try:
            text = extract_close_block(args.path)
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    else:
        ap.print_usage()
        return 2

    verdict, issues = evaluate(text)
    print(f"CLOSE-AUTH-GUARD: {verdict}")
    for it in issues:
        print(f"  - {it}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
