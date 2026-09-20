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
# Repaired 2026-08-28. The first branch listed `ruled|rule` but not the plain
# GERUND, and the second branch required a possessive (`principal'?s` -- the `s`
# is mandatory). So "principal's ruling" matched and "principal ruling" did not.
# Measured at repair time: 47 occurrences of the plain form in `governance/`
# alone, every one of them reading as unattributed to this guard.
#
# The fix is `rul(?:e|ed|ing)` on the first branch plus an optional possessive on
# the second, not a new branch -- a fourth spelling of the same idea is how this
# pattern acquired a blind spot in the first place.
#
# Second blind spot, found the same hour by the both-polarity test written to pin
# the first: `authoriz` did not match the British `-ise` spelling. 27 occurrences
# in governed text here, 4 of them in the passive form this pattern's third branch
# exists to catch. Same class as the gerund gap -- an unenumerated spelling variant
# -- so it is fixed the same way, by widening the character class rather than
# adding an alternation.
# Third blind spot, found at a receiver 2026-09-19 (node-1, aof1). The pattern had no
# branch for the fleet's most common authorization word: "GO". "Ceremony performed
# under principal GO." matched nothing here, while EVENT_POINTER matched the dated GO,
# so the guard reported a principal-authorized close as agent-autonomous and PASSED it
# on the wrong ground. Fixed as a scoped case-SENSITIVE token `(?-i:GO)\b` on the
# active, possessive and passive branches -- uppercase only, so "let the principal go"
# and "principal go-live" stay unmatched (pinned in the negative cases).
#
# Divergence notice (RULINGS_2026-09-06b R2 `declare`): this local copy carries the
# 2026-08-28 repair and this one; the v3.34.0 tag ships neither. Canonical repaired
# 2026-09-19 from this file; ships at the next tag.
PRINCIPAL_ATTRIB = re.compile(
    r"principal[-\s]?(rul(?:e|ed|ing)|approved|authori[sz]|decision|decided|chose|selected|elected|directed|typed|(?-i:GO)\b)"
    r"|per\s+principal|principal(?:'?s)?\s+(call|ruling|decision|selection|directive|(?-i:GO)\b)"
    # Passive. The separator class is `[\s*_:.\-]` and NOT `.*`: both rulings files write the
    # header as `**Ruled by**: principal`, where markdown emphasis and a colon sit between "by"
    # and "principal", and a bare `\s+` could not span them. Measured 2026-09-06 — the v3.34
    # preparation ruling read as UNATTRIBUTED while carrying a textbook attribution header, and
    # its sibling passed only because unrelated body prose happened to say "principal ruling".
    # Separator set derived from the corpus, not invented: `**:` (2 files), `_` and `:`
    # (`ruled_by: principal`), and `":"` (2 JSON authorization records). Nothing wider would match
    # "a ruling was issued by the committee's principal architect", which the negative cases forbid.
    r"|(ruled|approved|authori[sz]\w*|decided|directed|selected|chosen?|(?-i:GO)\b)[\s*_:.\"\-]+(by|from)[\s*_:.\"\-]+(the[\s*_:.\"\-]+)?principal",  # passive; GO from/by the principal
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
