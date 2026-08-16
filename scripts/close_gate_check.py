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

Usage:
  python3 scripts/close_gate_check.py <PROJECT_PLAN or session .md>
  python3 scripts/close_gate_check.py --quiet <path>

Exit codes:
  0 = clean (no blocking unchecked conformance signals)
  2 = violations found (block COMPLETE)
  3 = usage / file error

Owning initiative: INIT-PRINCIPLED-EXECUTION (Healthy Friction).
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

# Closure/Finalization checklist section headers whose unchecked items block COMPLETE.
#
# gh#2223 blind spot 1 (re-derived 2026-08-13): this pattern formerly matched ONLY the
# two literal headings "Closure Checklist" / "Finalization Checklist". A plan whose
# closure section is headed "## Closure", "## Exit Conditions", or "## Gate 4 Closure"
# had every unchecked box under it invisible to the guard. Falsifier held both
# polarities: "## Closure Checklist" + one unchecked box -> exit 2; "## Closure" +
# the same box -> exit 0. Widened to the closure-class alias set.
_CLOSURE_SECTION_RE = re.compile(
    r'^#{1,4}\s*(Closure Checklist|Finalization Checklist|Closure|Finalization'
    r'|Exit Conditions|Exit Criteria|Completion Checklist|Gate Closure)\b', re.IGNORECASE)
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


_CHECKED_RE = re.compile(r'^\s*[-*]\s*\[[xX]\]\s+(.*)$')
# Claims that require INDEPENDENT (non-producer) evidence to be true (L1047).
_INDEP_CLAIM_RE = re.compile(
    r'(deploy[\s-]?verif'
    r'|downstream\s+deploy'
    r'|\bdownstream\b[^.]*\bdeploy'
    r'|[≥>]?=?\s*1\s+downstream'
    r'|supervisor[\s-]?notif'
    r'|second[\s-]?agent'
    r'|independent[\s-]?downstream'
    r'|cross[\s-]?fleet\s+notif'
    r'|fleet[\s-]?confirm'
    r'|consumer[\s-]?confirm)',
    re.IGNORECASE)
# Markers that show the item already attests its evidence is producer-only /
# carried — suppress the WARN (the attestation the WARN asks for is present).
_ATTESTED_RE = re.compile(
    r'(producer[\s-]?pilot'
    r'|\bcarr(y|ies|ied)\b'
    r'|supervisor[\s-]?lane'
    r'|\bOPEN\b'
    r'|independent[\s-]?downstream[^.]*\bOPEN'
    r'|not\b[^.]*self[\s-]?satisf)',
    re.IGNORECASE)


# gh#2223 blind spots 2 and 3 (re-derived 2026-08-13). Two independent literalisms
# let a non-terminal STATUS TABLE pass:
#
#   2. Gate status was read only from the bold prose form `**Gate_Status**: Pending`.
#      A gate carried as a TABLE ROW -- the form every fleet-migration plan actually
#      uses -- was never read. Falsifier both polarities: the bold form -> exit 2, the
#      equivalent table row -> exit 0.
#   3. The V-test row pattern required the literal token PENDING *and* a first cell
#      beginning "Gate". A row reading `Open`/`Blocked`/`Incomplete`/⏳, or one keyed
#      `V3R.1` instead of `Gate 1`, was invisible. Falsifier both polarities: `| Gate 1
#      | x | PENDING |` -> exit 2; the same row with `Open`, and the same PENDING row
#      keyed `V3R.1`, -> exit 0.
#
# Scoped deliberately: fires only inside a markdown table whose HEADER row carries a
# status column alongside a gate/V-test/deliverable column, so prose tables and
# unrelated matrices cannot trip it.
_TABLE_ROW_RE = re.compile(r'^\s*\|(?P<cells>.+)\|\s*$')
_TABLE_SEP_RE = re.compile(r'^\s*\|[\s:|-]+\|\s*$')
_STATUS_HEADER_RE = re.compile(r'\bstatus\b|\bverdict\b|\bstate\b', re.IGNORECASE)
_SUBJECT_HEADER_RE = re.compile(r'\bgate\b|\bv-?test\b|\bdeliverable\b|\bexit\b', re.IGNORECASE)
_NONTERMINAL_STATUS_RE = re.compile(
    r'^(?:\W*)(PENDING|IN[\s-]?PROGRESS|OPEN|INCOMPLETE|BLOCKED|TODO|TO[\s-]DO'
    r'|NOT[\s-]STARTED|DEFERRED|PARTIAL|DRAFT|STOPPED|OWED|UNMET|FAIL(?:ED)?)\b',
    re.IGNORECASE)
_HOURGLASS_RE = re.compile(r'[⏳⏸🚧]')
# Blind spot 4, found only by running the rule against the REAL corpus (2026-08-13):
# the synthetic fixtures used word statuses, but this fleet's plans carry gate status
# as a CHECKBOX CELL -- `| -1.1 | ... | [x] | ... |`. An unchecked `[ ]` in a Status
# column sits outside any closure-named section, so `_UNCHECKED_RE` (which requires a
# `- [ ]` list item) never sees it and neither did the word-token rule above. This is
# the form the guard is most likely to meet on a plan being marked COMPLETE.
_UNCHECKED_CELL_RE = re.compile(r'^\[\s*\]$')


def _split_row(line: str):
    m = _TABLE_ROW_RE.match(line)
    if not m:
        return None
    return [c.strip() for c in m.group('cells').split('|')]


# gh#2223 blind spot 5 (2026-08-16) -- the THIRD gate-status encoding, and the one
# this seat's own plans use. Gate status carried as a bold `**Status**:` line inside a
# `## Gate N` heading section was read by neither existing rule: not the
# `**Gate_Status:**` prose form, not a table row. Measured: a fixture with two open
# heading-encoded gates returned `close-gate: PASS`, exit 0.
#
# The v3.31 release plan is exactly this shape, so the guard that decides whether it may
# close could not see a single one of its gates. Same root as L1404, where
# `loading_dock_surfacer` read the same plan as having zero gates and recommended closing
# it -- two instruments, one encoding assumption, both failing toward "close it".
#
# Scoped to gate sections deliberately: a bare `**Status**:` at document top is the plan's
# own header, not a gate, and matching it would fire on every in-progress plan regardless
# of gate state.
# A gate heading is `Gate <id>:` / `Join <id> —`, NOT any heading beginning with
# the word "Gate". Tightened 2026-08-16 after a cross-engine review measured the
# false positive this rule's first draft introduced: at the supervisor seat,
#   `## GATE 4 REOPEN & REPAIR RECORD — 2026-08-…`  →  fired as a live gate
# That is a repair RECORD, and blocking a close on it is a false-block — the exact
# second polarity V4.0 requires a guard to be free of. The first draft traded the
# tag copy's false-clean for a false-block, so NEITHER copy satisfied V4.0.
#
# Structural, not a word denylist: a real gate heading puts a delimiter directly
# after the gate id (`Gate 2:`, `Gate 3R:`, `Join 0J:`), while a record heading
# continues with prose (`GATE 4 REOPEN …`). Verified against both corpora — a
# denylist of RECORD/REOPEN/LOG would miss the next synonym and would also strike
# legitimate titles like `Gate 3R: Historical Verification-Payload`.
# `[\w.-]+` not `[\w.]+`: NEGATIVE gate ids are real and common in this fleet
# (`## Gate -1: Scope, Authority, and Lane Contract` is in this seat's own v3.31
# plan). The first tightening excluded them, trading the false-block it fixed for
# a fresh FALSE-CLEAN -- found by the clean Class A specimen minted at d23a9af3,
# not by me. Non-gate headings stay excluded: `Gate 0 Results` has no delimiter
# after the id, and `GATE 4 REOPEN ...` continues with prose.
_GATE_HEADING_RE = re.compile(r'^#{1,4}\s*(?:Gate|Join)\s+[\w.-]+\s*[:—–-]', re.IGNORECASE)
_BOLD_STATUS_LINE_RE = re.compile(r'^\*\*Status\*\*:?\s*(.+)$')


def scan_gate_heading_sections(text: str, exempt=frozenset()):
    """Return violations for non-terminal `**Status**:` lines under `## Gate` headings.

    One signal per gate section: a gate is non-terminal or it is not, and repeating the
    same finding for every restatement inside the section buries the others.

    `exempt` carries the gate ids that `resolve_supersession` proved validly
    superseded. Consulting it here is what makes CAP-PP-013-10's "a valid
    reference exempts the declaring gate" true of the VERDICT, not merely of one
    scan's private bookkeeping.
    """
    violations = []
    in_gate = False
    heading = ''
    gid = None
    for raw in text.splitlines():
        if _ANY_SECTION_RE.match(raw):
            in_gate = bool(_GATE_HEADING_RE.match(raw))
            heading = raw.strip().lstrip('#').strip()[:40]
            gid = _gate_id(raw)
            continue
        if not in_gate:
            continue
        m = _BOLD_STATUS_LINE_RE.match(raw.strip())
        if not m:
            continue
        status = m.group(1).strip().lstrip('*').strip()
        if _NONTERMINAL_STATUS_RE.match(status) or _HOURGLASS_RE.search(status):
            if gid is not None and gid in exempt:
                in_gate = False       # validly superseded; not a live gate
                continue
            violations.append(('gate_heading_nonterminal',
                               f"{heading} -> {status[:40]}"))
            in_gate = False          # counted; stop scanning this section
    return violations


def scan_status_table_rows(text: str, exempt=frozenset()):
    """Return (kind, detail) violations for non-terminal rows in gate/V-test status tables.

    Closes gh#2223 blind spots 2 and 3: the guard previously read gate status only from
    the bold prose form and V-test status only from a PENDING-token row keyed "Gate".

    Also honours `exempt` (CAP-PP-013-10). Gate status is carried in a TABLE by
    most fleet-migration plans, so a supersession rule that only understood the
    heading form would exempt a gate in one encoding and block the identical gate
    in the other — the same encoding-blindness gh#2223 was raised for.
    """
    violations = []
    header = None
    status_idx = None
    for raw in text.splitlines():
        line = raw.rstrip('\n')
        cells = _split_row(line)
        if cells is None:
            header, status_idx = None, None
            continue
        if _TABLE_SEP_RE.match(line):
            continue
        if header is None:
            # Candidate header row: needs both a status-ish and a subject-ish column.
            joined = ' '.join(cells)
            if _STATUS_HEADER_RE.search(joined) and _SUBJECT_HEADER_RE.search(joined):
                header = cells
                for i, c in enumerate(cells):
                    if _STATUS_HEADER_RE.search(c):
                        status_idx = i
                        break
            continue
        if status_idx is None or status_idx >= len(cells):
            continue
        status = cells[status_idx]
        if (_NONTERMINAL_STATUS_RE.match(status) or _HOURGLASS_RE.search(status)
                or _UNCHECKED_CELL_RE.match(status)):
            subject = cells[0][:40] if cells else ''
            if _gate_id(subject) is not None and _gate_id(subject) in exempt:
                continue
            violations.append(('status_row_nonterminal',
                               f"{subject} -> {status[:40]}"))
    return violations


# --------------------------------------------------------------------------
# CAP-PP-013-05..13 (AGET_PROJECT_PLAN_SPEC v1.4.0, published 2026-08-16).
# Implemented here at gh#2250 step 2. Each function names the requirement it
# discharges so a reader can check the implementation against the spec text
# rather than against this file's own prose.
# --------------------------------------------------------------------------

#: CAP-PP-003-01 status enum. Closed and normative -- CAP-PP-013-13(e) resolves
#: against THIS and nothing else. Adding a synonym here violates -13 sentence 2.
_PP003_ENUM = ("Draft", "In Progress", "Complete", "Abandoned")

#: -13(d): the first narrative delimiter terminating the leading clause.
_CLAUSE_DELIM_RE = re.compile(r"\s*[—–\-(\[.;,:/]|\s+see\s+", re.IGNORECASE)


def normalize_status(value: str) -> str:
    """CAP-PP-013-13 — normalize a status value for comparison.

    Steps (a)-(e) in the order the requirement specifies. Measured before it was
    written: (a)-(c) alone read 25 of 30 live dual-carriers as contradictory by
    flagging prose tails such as `COMPLETE (2026-07-12)` against `COMPLETE`;
    with (d)-(e) that is 5 of 30, all genuine.
    """
    v = value.strip()
    v = re.sub(r"\*+", "", v)                                     # (a) emphasis
    v = "".join(c for c in v if not unicodedata.category(c).startswith("So"))  # (a) symbols
    v = v.casefold()                                              # (b)
    v = re.sub(r"\s+", " ", v).strip(" \t*_-–—:•")                # (c)
    v = _CLAUSE_DELIM_RE.split(v, 1)[0].strip()                   # (d)
    for e in sorted(_PP003_ENUM, key=len, reverse=True):          # (e) longest first
        if v.startswith(e.casefold()):
            return e.casefold()
    return v                                                      # unresolved -> literal


_STATUS_FIELD_RE = re.compile(r"^\*\*Status\*\*:\s*(.+)$", re.M)
_PLAN_STATUS_FIELD_RE = re.compile(r"^\*\*Plan_Status\*\*:\s*(.+)$", re.M)


def _header_block(text: str) -> str:
    """Everything before the first `## ` section heading.

    CAP-PP-013-11 is about two PLAN-LEVEL header fields. Searching the whole
    document matches a GATE's `**Status**:` line and compares it against the
    plan's `Plan_Status` — which is not a contradiction, it is two different
    subjects. The pre-existing whole-document search only surfaced this when
    terminal-ness happened to disagree; exact-state comparison fires far more
    often, so the latent defect had to be closed with it rather than after it.

    No line cap: real headers carry long prose blocks and a cap silently
    under-reads them.
    """
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)

#: Terminal members of the CAP-PP-003 enum, plus the terminal values real plans
#: use that the enum does not carry. Kept separate from _PP003_ENUM on purpose:
#: -13(e) must resolve ONLY against the enum, while terminality is a different
#: question asked of an already-normalized value.
_TERMINAL_NORMALIZED = ("complete", "abandoned", "closed", "superseded")


def resolve_authoritative_status(text: str):
    """CAP-PP-013-11 — return (normalized_value, source_field, warning_or_None).

    `Plan_Status` is canonical; `**Status**` is a recognized legacy alias whose
    migration warning SHALL NOT alter the verdict. Returns (None, None, None)
    when the plan carries neither field.
    """
    head = _header_block(text)
    s = _STATUS_FIELD_RE.search(head)
    ps = _PLAN_STATUS_FIELD_RE.search(head)
    if ps:
        return normalize_status(ps.group(1)), "Plan_Status", None
    if s:
        return (normalize_status(s.group(1)), "Status",
                "plan uses legacy **Status**; `Plan_Status` is canonical (CAP-PP-013-11)")
    return None, None, None


def scan_dual_status_mask(text: str):
    """CAP-PP-013-11 — contradictory plan state, by EXACT normalized state.

    Supersedes the gh#1791 class comparison this function used to perform.
    Class comparison ('are both terminal?') is a lossy projection that discards
    the disagreement the predicate exists to detect: `Complete` vs `Abandoned`
    are BOTH terminal and are the paradigm contradiction. Precedence does not
    mask -- authority decides which value governs, never whether a conflict
    exists -- so this fires irrespective of which field is authoritative.
    """
    head = _header_block(text)
    s = _STATUS_FIELD_RE.search(head)
    ps = _PLAN_STATUS_FIELD_RE.search(head)
    if not (s and ps):
        return []
    if normalize_status(s.group(1)) == normalize_status(ps.group(1)):
        return []
    return [('dual_status_mask',
             f"Status={s.group(1)[:40]!r} vs Plan_Status={ps.group(1)[:40]!r} — "
             f"normalized states differ (CAP-PP-013-11); reconcile to Plan_Status, "
             f"delete legacy field")]


#: -09: supersession is EXPLICIT metadata. The evaluator SHALL NOT infer it from
#: heading text, ordering, position, or dates.
_SUPERSEDED_BY_RE = re.compile(
    r"^\s*(?:[-*]\s*)?\**superseded_by\**\s*[:=]\s*(.+?)\s*$", re.M | re.IGNORECASE)

#: A heading that REFERENCES a gate id, whether or not it is a well-formed gate
#: heading. Deliberately broader than _GATE_HEADING_RE: -09 forbids treating a
#: record-shaped heading as self-exempting, so a second section naming the same
#: gate must be visible to the duplicate check below.
#
# The id class MUST include `-`. Found by running this rule against the real
# corpus, not by a fixture: `### Gate R-1:`, `R-2:` and `R-3:` each truncated to
# the id `r`, so three distinct gates collapsed into one and their differing
# statuses tripped this rule as a false supersession finding. Hyphenated gate
# ids are ordinary in this fleet (`R-1`, and negative ids like `-1`).
_GATE_ID_IN_HEADING_RE = re.compile(
    r"^#{1,4}\s*(?:Gate|Join)\s+(-?[\w.-]+?)\s*(?=[:—–]|\s|$)", re.IGNORECASE)


#: A `Superseded_By` COLUMN in a status table — the second declaration site.
#: Gate status lives in a table in most fleet-migration plans, so a rule that
#: understood only the heading form would exempt a gate in one encoding and block
#: the identical gate in the other.
_SUPERSEDED_BY_HEADER_RE = re.compile(r'\bsupersed(?:ed|es)[\s_-]?by\b', re.IGNORECASE)


def _gate_id(raw: str):
    """Normalize a heading line or a table subject cell to a comparable gate id.

    Deliberately STRICT: `Gate 5` and `G5` do NOT unify. Exemption is the unsafe
    direction — a missed exemption leaves a gate blocking (annoying, visible,
    correctable), while a spurious one lets a live gate through a close (silent,
    and the whole point of the guard). Where the two directions are not
    symmetric, the loose match belongs on the blocking side, not this one.
    """
    s = re.sub(r'^#{1,4}\s*', '', raw.strip()).strip('`*|').strip()
    m = re.match(r'^(?:Gate|Join)\s+(-?[\w.-]+?)\s*(?=[:—–]|\s|$)', s, re.IGNORECASE)
    if m:
        return m.group(1).casefold()
    m = re.fullmatch(r'(-?[\w.-]+)', s)
    if m and re.search(r'\d', m.group(1)):
        return m.group(1).casefold()
    return None


def _iter_tables(text: str):
    """Yield (header_cells, [data_rows]) for SEPARATOR-CONFIRMED markdown tables.

    A header row is one immediately followed by a `|---|---|` separator. Nothing
    else counts.

    This strictness is not cosmetic. The first implementation treated any table
    row whose text merely CONTAINED "superseded by" as a header, then read the
    matching column of every following row as a reference. Measured against the
    real corpus: 14 findings across 2 plans, all false, all reading prose cells
    like "PASS at `00a13f6d`; evidence baseline superseded by gate 0r" as gate
    references. Prose that discusses supersession is not a declaration of it.
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        cells = _split_row(lines[i].rstrip('\n'))
        if cells is None or not _TABLE_SEP_RE.match(lines[i + 1]):
            i += 1
            continue
        header, rows, j = cells, [], i + 2
        while j < len(lines):
            rc = _split_row(lines[j].rstrip('\n'))
            if rc is None:
                break
            if not _TABLE_SEP_RE.match(lines[j]):
                rows.append(rc)
            j += 1
        yield header, rows
        i = j


def _superseded_by_column(header):
    """Index of a `Superseded_By` column, or None. The CELL must match — not the
    joined header text, which is what let a prose row masquerade as a header."""
    for i, c in enumerate(header):
        if _SUPERSEDED_BY_HEADER_RE.fullmatch(c.strip().strip('*` ')):
            return i
    return None


def _declared_gate_ids(text: str):
    """Every gate id this plan declares — the resolution set for -10(a)/(b).

    Reads BOTH encodings. A heading-only resolution set makes -10(b) ("same
    plan") false for any table-encoded plan: the successor is declared by a table
    row, the reference to it reads as dangling, and the declaring gate is then
    held live for naming a gate that is in fact right there. Measured on a table
    fixture before this was widened.
    """
    ids = []
    for raw in text.splitlines():
        if _GATE_ID_IN_HEADING_RE.match(raw):
            gid = _gate_id(raw)
            if gid is not None:
                ids.append(gid)
    for header, rows in _iter_tables(text):
        joined = ' '.join(header)
        if not (_SUBJECT_HEADER_RE.search(joined)
                and (_STATUS_HEADER_RE.search(joined)
                     or _superseded_by_column(header) is not None)):
            continue
        for cells in rows:
            gid = _gate_id(cells[0]) if cells else None
            if gid is not None:
                ids.append(gid)
    return ids


def _collect_declarations(text: str):
    """Return {declaring_gate_id: target_id} from BOTH declaration sites.

    Site 1 — a `superseded_by:` line inside a gate section.
    Site 2 — a `Superseded_By` COLUMN of a separator-confirmed table.
    """
    out, current = {}, None
    for raw in text.splitlines():
        if _GATE_ID_IN_HEADING_RE.match(raw):
            current = _gate_id(raw)
            continue
        if _ANY_SECTION_RE.match(raw):
            current = None
            continue
        sm = _SUPERSEDED_BY_RE.match(raw)
        if sm and current:
            out[current] = re.sub(r'^(?:gate|join)\s+', '',
                                  sm.group(1).strip().strip('`*').casefold()).strip()

    for header, rows in _iter_tables(text):
        sup_idx = _superseded_by_column(header)
        if sup_idx is None:
            continue
        for cells in rows:
            if sup_idx >= len(cells):
                continue
            decl = _gate_id(cells[0]) if cells else None
            val = cells[sup_idx].strip().strip('`*')
            if decl is None or not val or val.lower() in {'-', '—', '–', 'n/a', 'none', ''}:
                continue
            out[decl] = re.sub(r'^(?:gate|join)\s+', '', val.casefold()).strip()
    return out


def resolve_supersession(text: str):
    """CAP-PP-013-09/10 — the SINGLE resolution pass, run BEFORE any verdict.

    Returns `(exempt_ids, violations)`.

    Centralized deliberately. Resolution used to live inside one scan, so
    `scan_gate_heading_sections` and `scan_status_table_rows` never consulted it:
    a validly superseded gate was reported as live by both, in both encodings,
    while the supersession scan privately considered it resolved. The guard's
    VERDICT therefore contradicted CAP-PP-013-10 even though a function in the
    file implemented it correctly. Resolving once, ahead of verdict generation,
    is what makes the exemption real rather than book-kept.

    A valid reference exempts ONLY the declaring gate; the successor is returned
    to the caller unexempted and is evaluated on its own status like any other.
    """
    declared = _declared_gate_ids(text)
    decls = _collect_declarations(text)

    status = {}                      # gid -> (target, valid, reason)
    for gid, target in decls.items():
        hits = [d for d in declared if d == target]
        if target == gid:
            status[gid] = (target, False, "self-reference")
        elif len(hits) == 0:
            status[gid] = (target, False, "dangling — resolves to no gate in this plan")
        elif len(hits) > 1:
            status[gid] = (target, False, f"ambiguous — resolves to {len(hits)} gates")
        else:
            status[gid] = (target, True, "")

    # (d) acyclic. Walk each chain; every node on a cycle is invalidated, and the
    # walk is bounded by the number of declarations so a cycle cannot spin here.
    for start in list(status):
        path, node = [], start
        while node in status and status[node][1]:
            if node in path:
                for n in path[path.index(node):]:
                    t, _, _ = status[n]
                    status[n] = (t, False, "cyclic supersession chain")
                break
            path.append(node)
            node = status[node][0]

    exempt = frozenset(g for g, (_, valid, _) in status.items() if valid)

    violations = []
    for gid, (target, valid, reason) in sorted(status.items()):
        if not valid:
            violations.append((
                'supersession_not_explicit',
                f"Gate {gid} declares superseded_by={target!r} — {reason}; "
                f"treated as LIVE (CAP-PP-013-10)"))

    # -09: a gate id carried in more than one section with DISAGREEING states, and
    # no explicit declaration at all, is unresolved. Nothing is inferred from
    # heading wording here — only from the same id carrying two different states.
    sections, current = {}, None
    for raw in text.splitlines():
        hm = _GATE_ID_IN_HEADING_RE.match(raw)
        if hm:
            current = _gate_id(raw)
            sections.setdefault(current, [])
            continue
        if _ANY_SECTION_RE.match(raw):
            current = None
            continue
        if current is None:
            continue
        m = _BOLD_STATUS_LINE_RE.match(raw.strip())
        if m:
            sections[current].append(m.group(1).strip().lstrip('*').strip())

    for gid, stamps in sorted(sections.items()):
        if len(stamps) < 2 or gid in decls:
            continue                     # single section, or already adjudicated above
        states = {normalize_status(s) for s in stamps}
        if len(states) < 2:
            continue                     # all sections agree; nothing to resolve
        violations.append((
            'supersession_not_explicit',
            f"Gate {gid} declared in {len(stamps)} sections with disagreeing states "
            f"{sorted(states)} — no `superseded_by` declared (CAP-PP-013-09)"))

    return exempt, violations


def legitimately_terminal(text: str, closure_violations):
    """CAP-PP-013-07 — (bool, reason). All three conditions, each falsifiable.

    (a) authoritative status resolves to exactly one terminal enum value;
    (b) no second status-bearing field declares a different normalized exact state;
    (c) closure-checklist items are checked and V-tests recorded.
    """
    value, source, _ = resolve_authoritative_status(text)
    if value is None:
        return False, "(a) no status-bearing field"
    if value not in _TERMINAL_NORMALIZED:
        return False, f"(a) authoritative {source} normalizes to {value!r}, not terminal"
    if scan_dual_status_mask(text):
        return False, "(b) a second status-bearing field declares a different state"
    blocking_c = {'unchecked_closure_item', 'placeholder_substance', 'vtest_pending'}
    hit = [k for k, _ in closure_violations if k in blocking_c]
    if hit:
        return False, f"(c) closure content incomplete: {sorted(set(hit))}"
    return True, ""


#: -08: findings that describe a STALE STAMP under an otherwise legitimately
#: terminal plan. In audit mode these become HYGIENE. Everything else -- a
#: contradictory plan state, an unresolved supersession, missing closure content
#: -- blocks in both modes.
_STALE_STAMP_KINDS = frozenset({
    'gate_status_pending', 'vtest_pending', 'status_row_nonterminal',
    'gate_heading_nonterminal',
})


def scan_independence_warnings(text: str):
    """Return a list of (kind, detail) independence-WARNs (L1047, non-blocking).

    Restored at v3.26 C-26-06 (F-REL326-G1-2): the v3.25 canonical sync
    overwrote instance copies and DROPPED this half — canonical never had it.
    A WARN fires on a checked `[x]` item whose text asserts an independence-
    requiring claim (deploy-verify / supervisor-notify / second-agent / etc.)
    and does NOT already carry an attestation marker (producer-pilot / carry /
    supervisor-lane / OPEN). The gate can confirm the box is checked; it cannot
    confirm the evidence is independent vs producer-self — so it surfaces the
    item for attestation rather than passing silently. Never blocks.
    """
    warnings = []
    for raw in text.splitlines():
        cm = _CHECKED_RE.match(raw.rstrip('\n'))
        if not cm:
            continue
        body = cm.group(1)
        # Match the CLAIM only in the item's subject window (text before the
        # first " — "/" - " dash-clause, capped at 80 chars), so an incidental
        # later mention does not false-positive. Attestation may appear anywhere.
        subject = re.split(r'\s[—-]\s', body, maxsplit=1)[0][:80]
        if _INDEP_CLAIM_RE.search(subject) and not _ATTESTED_RE.search(body):
            warnings.append(('independence_unattested', body.strip()[:100]))
    return warnings


def main(argv=None):
    p = argparse.ArgumentParser(description="Close-gate conformance guard (C-P1).")
    p.add_argument('path', help="PROJECT_PLAN or session markdown file being closed")
    p.add_argument('--quiet', '-q', action='store_true', help="Only print the verdict line")
    # CAP-PP-013-05: mode is an EVALUATOR INVOCATION INPUT, never plan metadata.
    # A plan carrying its own mode could set itself to `audit` and escape closure
    # blocking; mode is a property of the question, not of the thing questioned.
    p.add_argument('--mode', choices=('closure', 'audit'), default='closure',
                   help="closure (default, CAP-PP-013-05/06) blocks any live non-terminal "
                        "gate or contradictory state; audit (CAP-PP-013-08) reports stale "
                        "stamps under a legitimately-terminal plan as HYGIENE")
    args = p.parse_args(argv)

    fp = Path(args.path)
    if not fp.is_file():
        print(f"close-gate: ERROR — file not found: {fp}", file=sys.stderr)
        return 3

    content = fp.read_text(encoding='utf-8', errors='replace')

    # CAP-PP-013-09/10 — resolve supersession ONCE, BEFORE any verdict is
    # generated, and hand the exempt set to every gate-oriented scan. Order is
    # the requirement here, not a style choice: a scan that runs before
    # resolution cannot honour an exemption, which is precisely how a validly
    # superseded gate came to be reported as live in both encodings.
    exempt, supersession_violations = resolve_supersession(content)

    violations = scan(content)
    violations.extend(scan_status_table_rows(content, exempt))
    violations.extend(scan_gate_heading_sections(content, exempt))
    violations.extend(scan_dual_status_mask(content))
    violations.extend(supersession_violations)
    warnings = scan_independence_warnings(content)

    # CAP-PP-013-11: the legacy-alias migration warning accompanies the verdict
    # and SHALL NOT alter it.
    _, _, _status_migration_warn = resolve_authoritative_status(content)

    # CAP-PP-013-08: audit mode downgrades STALE STAMPS to HYGIENE -- but only
    # WHERE the plan is legitimately-terminal. Otherwise audit falls back to
    # closure behaviour, which is what makes a contradictory plan block in BOTH
    # modes without needing a separate rule.
    hygiene = []
    if args.mode == 'audit':
        ok, why = legitimately_terminal(content, violations)
        if ok:
            hygiene = [v for v in violations if v[0] in _STALE_STAMP_KINDS]
            violations = [v for v in violations if v[0] not in _STALE_STAMP_KINDS]
        else:
            print(f"close-gate: audit → closure fallback — plan is not legitimately-terminal: {why} "
                  f"(CAP-PP-013-08)")

    def _print_independence_warn():
        # Surface independence-WARNs (L1047) — non-silent PASS. Never blocks.
        if not warnings:
            return
        print(f"close-gate: ⚠ INDEPENDENCE-WARN — {len(warnings)} checked item(s) in "
              f"{fp.name} assert independence-requiring claims without attestation "
              f"(non-blocking; attest producer-pilot/carry/supervisor-lane/OPEN or verify independently):")
        if not args.quiet:
            for _, detail in warnings:
                print(f"  - {detail}")

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

    kinds = {'gate_status_pending': 'Gate still Pending/In-Progress',
             'vtest_pending': 'V-test row PENDING',
             'status_row_nonterminal': 'Gate/V-test table row non-terminal (gh#2223)',
             'gate_heading_nonterminal': 'Gate heading section non-terminal (gh#2223 bs5)',
             'unchecked_closure_item': 'Unchecked closure/finalization item',
             'placeholder_substance': 'Closure-section placeholder prose (substance, #1568)',
             'dual_status_mask': 'Contradictory plan state (CAP-PP-013-11)',
             'supersession_not_explicit': 'Supersession not explicit (CAP-PP-013-09)',
             'release_close_guard_block': 'Release-completion guard BLOCK (#1554)',
             'release_close_guard_error': 'Release-completion guard error'}

    def _print_hygiene():
        # CAP-PP-013-12(b)+(c): HYGIENE is labelled DISTINCTLY from blocking and
        # SHALL NOT alter the exit status. Distinguishability comes from the
        # rendering; the exit code answers a different question.
        if not hygiene:
            return
        print(f"close-gate: ◷ HYGIENE — {len(hygiene)} stale gate stamp(s) in {fp.name} under a "
              f"legitimately-terminal plan (audit mode; non-blocking, CAP-PP-013-08):")
        if not args.quiet:
            for kind, detail in hygiene:
                print(f"  ◷ [{kinds.get(kind, kind)}] {detail}")

    if _status_migration_warn:
        print(f"close-gate: ⚠ MIGRATION — {_status_migration_warn} (verdict unaffected)")

    if not violations:
        # CAP-PP-013-12(a) contrapositive: no blocking finding => exit 0, and a
        # hygiene-only run stays here.
        print(f"close-gate: PASS — no unchecked conformance signals in {fp.name} "
              f"[mode={args.mode}]")
        _print_hygiene()
        _print_independence_warn()
        return 0

    # CAP-PP-013-12(a): a blocking finding SHALL return a nonzero exit status.
    print(f"close-gate: BLOCK — {len(violations)} unchecked conformance signal(s) in {fp.name} "
          f"[mode={args.mode}] (L178 override available with reason):")
    if not args.quiet:
        for kind, detail in violations[:30]:
            print(f"  - [{kinds.get(kind, kind)}] {detail}")
    _print_hygiene()
    _print_independence_warn()
    return 2


if __name__ == '__main__':
    sys.exit(main())
