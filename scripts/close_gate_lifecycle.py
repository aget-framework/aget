#!/usr/bin/env python3
"""Framework-owned CAP-PP-013-14..22 lifecycle contract for close_gate_check.

This module is part of the canonical close-gate package.  It deliberately does
not use the ``*_ext.py`` suffix: that suffix denotes instance-owned state which
upgrade procedures preserve rather than overwrite.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SPEC = Path(os.environ.get(
    "AGET_PROJECT_PLAN_SPEC",
    Path(__file__).resolve().parent.parent / "specs" / "AGET_PROJECT_PLAN_SPEC.md"))
LIFECYCLE_CLASSES = frozenset({"creator-scaffolded", "pre-close-verifiable", "closer-authored"})
TERMINAL_DISPOSITIONS = (
    "Complete", "Closed", "Closed (Partial)", "Abandoned", "Superseded",
)
REASONED_DISPOSITIONS = frozenset(TERMINAL_DISPOSITIONS[1:])
ROW_DISPOSITIONS = frozenset({"deferred", "obsolete", "accepted-incomplete"})

RAW_SOURCE_REQUIREMENT = {
    "gate_status_pending": "CAP-PP-013-06",
    "vtest_pending": "CAP-PP-013-02",
    "status_row_nonterminal": "CAP-PP-013-06",
    "gate_heading_nonterminal": "CAP-PP-013-06",
    "unchecked_closure_item": "CAP-PP-013-02",
    "placeholder_substance": "CAP-PP-013-03",
    "dual_status_mask": "CAP-PP-013-11",
    "supersession_not_explicit": "CAP-PP-013-10",
    "release_close_guard_block": "CAP-PP-013-12",
    "release_close_guard_error": "CAP-PP-013-12",
}


class LifecycleContractError(ValueError):
    """Malformed invocation, schema, or close document (exit class ERROR)."""


@dataclass(frozen=True)
class Finding:
    reason_key: str
    affected_subject: str
    evidence_location: str
    source_requirement: str
    lifecycle_class: str
    semantic_class: str
    emission_index: int
    detail: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class AccountingRow:
    reason_key: str
    affected_subject: str
    disposition: str
    note: str
    row_index: int = 0


def _table_rows_after(text: str, heading: str):
    start = text.find(heading)
    if start < 0:
        raise LifecycleContractError(f"schema heading absent: {heading}")
    rows = []
    for line in text[start:].splitlines()[1:]:
        if line.startswith("### "):
            break
        if re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", line):
            continue
        if line.startswith("|"):
            rows.append([c.strip().strip("`") for c in line.strip().strip("|").split("|")])
        elif rows:
            break
    return rows


def load_schema(spec_path: Path = SPEC):
    """Derive lifecycle classes, semantic classes and dispositions from the spec."""
    text = spec_path.read_text(encoding="utf-8")
    lifecycle = {}
    for row in _table_rows_after(text, "### CAP-PP-013-14: Lifecycle-class attribute (ETVX)"):
        if row and row[0] == "Requirement":
            continue
        for i in (0, 2):
            if len(row) > i + 1 and re.fullmatch(r"CAP-PP-013-\d{2}", row[i]):
                req, cls = row[i], row[i + 1]
                if cls not in LIFECYCLE_CLASSES or req in lifecycle:
                    raise LifecycleContractError(f"invalid/duplicate lifecycle row: {req}={cls}")
                lifecycle[req] = cls
    expected = {f"CAP-PP-013-{n:02d}" for n in range(1, 23)}
    if set(lifecycle) != expected:
        raise LifecycleContractError(
            f"lifecycle coverage mismatch: missing={sorted(expected-set(lifecycle))} "
            f"extra={sorted(set(lifecycle)-expected)}")

    semantic = {}
    for row in _table_rows_after(text, "### CAP-PP-013-16: Finding occurrence identity and semantic class"):
        if not row or row[0] == "Semantic class" or len(row) < 2:
            continue
        cls = row[0]
        if cls not in {"substantive_work", "closure_record", "integrity"}:
            continue
        for raw_key in ",".join(row[1:]).split(","):
            key = raw_key.strip().strip("`")
            if not key:
                continue
            if key in semantic:
                raise LifecycleContractError(f"raw finding key classified twice: {key}")
            semantic[key] = cls
    if set(semantic) != set(RAW_SOURCE_REQUIREMENT):
        raise LifecycleContractError(
            f"raw-key coverage mismatch: missing={sorted(set(RAW_SOURCE_REQUIREMENT)-set(semantic))} "
            f"extra={sorted(set(semantic)-set(RAW_SOURCE_REQUIREMENT))}")

    enum_match = re.search(
        r"\| CAP-PP-003-01 \|[^\n]*?\|\s*([^|]+?)\s*\| Header \|", text)
    if not enum_match:
        raise LifecycleContractError("CAP-PP-003-01 enum row absent")
    states = tuple(v.strip() for v in enum_match.group(1).split(","))
    if not set(TERMINAL_DISPOSITIONS).issubset(states):
        raise LifecycleContractError("terminal disposition missing from CAP-PP-003-01")
    transitions = {}
    for row in _table_rows_after(text, "### CAP-PP-013-19: Lawful lifecycle transitions"):
        if not row or row[0] == "Source state" or len(row) < 2:
            continue
        source = row[0]
        targets = tuple(v.strip().strip("`") for v in row[1].split(","))
        if source in transitions or source not in states or not set(targets).issubset(TERMINAL_DISPOSITIONS):
            raise LifecycleContractError(f"invalid/duplicate transition row: {source}={targets}")
        transitions[source] = targets
    expected_sources = {"Draft", "In Progress", "Staged",
                        "Implemented-Awaiting-Deployment-Evidence", "Piloted"}
    if set(transitions) != expected_sources:
        raise LifecycleContractError("transition source coverage mismatch")
    return {"lifecycle": lifecycle, "semantic": semantic, "states": states,
            "transitions": transitions}


def canonical_disposition(token: str | None, schema=None):
    if token is None:
        raise LifecycleContractError("E-DISP-MISSING: --disposition is required; no default exists")
    schema = schema or load_schema()
    normalized = re.sub(r"\s+", " ", token.strip()).casefold()
    if normalized == "closed-partial":
        normalized = "closed (partial)"
    hits = [d for d in TERMINAL_DISPOSITIONS if d in schema["states"] and d.casefold() == normalized]
    if len(hits) != 1:
        raise LifecycleContractError(f"E-DISP-UNKNOWN: {token!r}")
    return hits[0]


_SUFFIX = re.compile(
    r"^(?:(completed|closed|closed-partial|abandoned|superseded)\s+)?"
    r"(\d{4}-\d{2}-\d{2})(?:\s+(gh#\d+|https://\S+))*$", re.I)
_VERBS = {
    "Complete": {"completed", "closed"}, "Closed": {"closed"},
    "Closed (Partial)": {"closed-partial"}, "Abandoned": {"abandoned"},
    "Superseded": {"superseded"},
}


def parse_status(value: str, *, legacy: bool, schema=None):
    """Return (canonical state or None, migration warning or None).

    Canonical carriers admit only exact enum values. Legacy carriers may use the
    bounded CAP-PP-013-13 suffix; descriptive/negating prose never establishes
    terminality.  There is intentionally no synonym/equivalence list.
    """
    schema = schema or load_schema()
    clean = re.sub(r"\*+", "", value).strip()
    clean = "".join(c for c in clean if not unicodedata.category(c).startswith("So"))
    clean = re.sub(r"\s+", " ", clean).strip()
    exact = [s for s in schema["states"] if s.casefold() == clean.casefold()]
    if exact:
        return exact[0], None
    if not legacy:
        return None, "canonical Plan_Status must contain exactly one CAP-PP-003 value"
    for state in sorted(schema["states"], key=len, reverse=True):
        if state not in TERMINAL_DISPOSITIONS:
            continue
        m = re.match(rf"^{re.escape(state)}\s*[—–-]\s*(.+)$", clean, re.I)
        if not m:
            continue
        suffix = m.group(1)
        sm = _SUFFIX.fullmatch(suffix)
        if not sm:
            return None, "legacy suffix is ambiguous or meaning-changing"
        verb = sm.group(1)
        if verb and verb.casefold() not in _VERBS[state]:
            return None, "legacy terminal verb disagrees with disposition"
        return state, "legacy annotated status parsed; migrate provenance to Plan_Status_Annotation"
    return None, "status does not resolve to the closed CAP-PP-003 vocabulary"


def enrich_findings(raw: Iterable[tuple[str, str]], evidence_path: str, schema=None):
    schema = schema or load_schema()
    findings = []
    for idx, (key, detail) in enumerate(raw):
        if key not in RAW_SOURCE_REQUIREMENT or key not in schema["semantic"]:
            raise LifecycleContractError(f"uncovered raw finding key: {key}")
        req = RAW_SOURCE_REQUIREMENT[key]
        if req not in schema["lifecycle"]:
            raise LifecycleContractError(f"source requirement absent from lifecycle schema: {req}")
        subject = re.sub(r"\s+", " ", detail).strip() or "<unspecified>"
        findings.append(Finding(
            reason_key=key,
            affected_subject=subject,
            evidence_location=f"{evidence_path}:finding:{idx + 1}",
            source_requirement=req,
            lifecycle_class=schema["lifecycle"][req],
            semantic_class=schema["semantic"][key],
            emission_index=idx,
            detail=detail,
        ))
    return findings


def entry_partition(findings: Iterable[Finding], disposition: str):
    """Return (blocking, carried), derived from lifecycle and semantic attributes."""
    blocking, carried = [], []
    for f in findings:
        if f.lifecycle_class == "closer-authored":
            continue
        if f.semantic_class == "integrity" or f.reason_key == "status_row_nonterminal":
            blocking.append(f)
        elif f.semantic_class == "substantive_work":
            (blocking if disposition == "Complete" else carried).append(f)
        else:
            blocking.append(f)
    return blocking, carried


def _split_escaped_row(line: str):
    if not line.startswith("|") or not line.endswith("|"):
        raise LifecycleContractError("E-GRAMMAR: row lacks outer pipes")
    cells, buf, escaped = [], [], False
    for ch in line[1:-1]:
        if escaped:
            if ch != "|":
                raise LifecycleContractError("E-GRAMMAR: only \\| is a valid escape")
            buf.append("|")
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == "|":
            cells.append("".join(buf).strip()); buf = []
        else:
            buf.append(ch)
    if escaped:
        raise LifecycleContractError("E-GRAMMAR: trailing escape")
    cells.append("".join(buf).strip())
    return cells


def _validate_note(row_disp: str, note: str):
    pairs = {}
    for part in note.split(";"):
        if "=" not in part:
            raise LifecycleContractError("E-GRAMMAR: note must use key=value pairs")
        key, value = (x.strip() for x in part.split("=", 1))
        if not re.fullmatch(r"[a-z]+", key) or not value or key in pairs:
            raise LifecycleContractError("E-GRAMMAR: invalid/duplicate note key")
        pairs[key] = value
    required = {
        "deferred": {"vehicle", "reason"}, "obsolete": {"reason"},
        "accepted-incomplete": {"authority", "receipt", "reason"},
    }[row_disp]
    if set(pairs) != required:
        raise LifecycleContractError(f"E-GRAMMAR: {row_disp} note keys must be {sorted(required)}")
    if row_disp == "deferred" and not re.fullmatch(
            r"(?:planning/PROJECT_PLAN_[^\s]+\.md|INIT-[A-Z0-9-]+|gh#\d+|https://\S+)",
            pairs["vehicle"]):
        raise LifecycleContractError("E-GRAMMAR: deferred vehicle is not governed")
    if row_disp == "accepted-incomplete" and pairs["authority"] not in {
            "principal", "supervisor", "owner"}:
        raise LifecycleContractError("E-GRAMMAR: invalid accepted-incomplete authority")


def parse_unfinished(text: str):
    heading = "## Unfinished at Close"
    starts = [m.start() for m in re.finditer(r"(?m)^## Unfinished at Close\s*$", text)]
    if len(starts) > 1:
        raise LifecycleContractError("E-SECTION-DUPLICATE")
    if not starts:
        return []
    section = text[starts[0]:]
    nxt = re.search(r"(?m)^## (?!Unfinished at Close\s*$).+", section[len(heading):])
    if nxt:
        section = section[:len(heading) + nxt.start()]
    lines = [line for line in section.splitlines() if line.strip()]
    if len(lines) < 4:
        raise LifecycleContractError("E-SECTION-EMPTY")
    if lines[1].strip() != "| reason_key | affected_subject | disposition | note |":
        raise LifecycleContractError("E-GRAMMAR: exact table header required")
    if re.sub(r"\s+", "", lines[2]) != "|---|---|---|---|":
        raise LifecycleContractError("E-GRAMMAR: exact four-column delimiter required")
    rows = []
    for i, line in enumerate(lines[3:], 1):
        cells = _split_escaped_row(line)
        if len(cells) != 4 or any(not c for c in cells):
            raise LifecycleContractError("E-GRAMMAR: accounting row needs four non-empty fields")
        if cells[2] not in ROW_DISPOSITIONS:
            raise LifecycleContractError(f"E-ROW-DISP: {cells[2]!r}")
        _validate_note(cells[2], cells[3])
        rows.append(AccountingRow(*cells, row_index=i))
    if not rows:
        raise LifecycleContractError("E-SECTION-EMPTY")
    return rows


def without_unfinished_section(text: str):
    """Remove the accounting section from detector input; it describes findings."""
    match = re.search(r"(?m)^## Unfinished at Close\s*$", text)
    if not match:
        return text
    tail = text[match.end():]
    nxt = re.search(r"(?m)^## (?!Unfinished at Close\s*$).+", tail)
    end = match.end() + nxt.start() if nxt else len(text)
    return text[:match.start()] + text[end:]


def reconcile(findings: Iterable[Finding], rows: Iterable[AccountingRow]):
    """One-to-one multiset reconciliation; occurrence multiplicity is preserved."""
    fs = list(findings); rs = list(rows)
    nonwaivable = [r for r in rs if any(
        f.reason_key == r.reason_key and f.affected_subject == r.affected_subject
        and f.semantic_class in {"closure_record", "integrity"} for f in fs)]
    f_count = Counter((f.reason_key, f.affected_subject) for f in fs
                      if f.semantic_class == "substantive_work")
    r_count = Counter((r.reason_key, r.affected_subject) for r in rs)
    unaccounted, orphan = [], []
    for key in sorted(set(f_count) | set(r_count)):
        if f_count[key] > r_count[key]:
            unaccounted.extend([key] * (f_count[key] - r_count[key]))
        if r_count[key] > f_count[key]:
            orphan.extend([key] * (r_count[key] - f_count[key]))
    return {"unaccounted": unaccounted, "orphan": orphan, "nonwaivable": nonwaivable}


def escape_field(value: str):
    if "\n" in value or "\r" in value or "\\" in value:
        raise LifecycleContractError("E-GRAMMAR: writer field contains newline/backslash")
    value = value.strip()
    if not value:
        raise LifecycleContractError("E-GRAMMAR: writer field empty")
    return value.replace("|", "\\|")


def load_unfinished_rows(rows_json: Path):
    """Parse and validate a proposed accounting-row payload without mutation."""
    try:
        payload = json.loads(rows_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleContractError(f"E-WRITE-PAYLOAD: {exc}") from exc
    if not isinstance(payload, list) or not payload:
        raise LifecycleContractError("E-WRITE-PAYLOAD: expected a non-empty JSON row list")
    try:
        rows = [AccountingRow(r["reason_key"], r["affected_subject"],
                              r["disposition"], r["note"], i)
                for i, r in enumerate(payload, 1)]
    except (KeyError, TypeError) as exc:
        raise LifecycleContractError(f"E-WRITE-PAYLOAD: malformed row: {exc}") from exc
    for row in rows:
        if row.disposition not in ROW_DISPOSITIONS:
            raise LifecycleContractError(f"E-ROW-DISP: {row.disposition!r}")
        _validate_note(row.disposition, row.note)
    return rows


def render_unfinished(text: str, rows: Iterable[AccountingRow]):
    """Return candidate document bytes; validate their round-trip before any write."""
    rows = list(rows)
    if re.search(r"(?m)^## Unfinished at Close\s*$", text):
        raise LifecycleContractError("E-SECTION-DUPLICATE: writer will not overwrite an existing section")
    rendered = ["## Unfinished at Close", "", "| reason_key | affected_subject | disposition | note |",
                "|---|---|---|---|"]
    rendered.extend("| " + " | ".join(escape_field(v) for v in (
        r.reason_key, r.affected_subject, r.disposition, r.note)) + " |" for r in rows)
    candidate = text.rstrip() + "\n\n" + "\n".join(rendered) + "\n"
    parsed = parse_unfinished(candidate)
    if len(parsed) != len(rows):
        raise LifecycleContractError("E-GRAMMAR: candidate section did not roundtrip")
    return candidate


def commit_unfinished(path: Path, candidate: str, expected_rows: int):
    """Atomically persist a previously validated candidate and verify received bytes."""
    mode = path.stat().st_mode
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(candidate)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        temporary = None
        parsed = parse_unfinished(path.read_text(encoding="utf-8"))
        if len(parsed) != expected_rows:
            raise LifecycleContractError("E-GRAMMAR: persisted section did not roundtrip")
        return parsed
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def is_release_completion_plan(text: str):
    """Derive release class from the document identity, never the filename."""
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return bool(re.fullmatch(
        r"# PROJECT_PLAN:\s+v\d+\.\d+\.\d+\s+(?:Parallel\s+)?Release(?:\s+Train)?",
        first, re.I))


def generated_coverage(schema=None, raw_keys=None, dispositions=None):
    """Generate the mode × phase × disposition × raw-key decision product."""
    schema = schema or load_schema()
    raw_keys = tuple(raw_keys or schema["semantic"])
    dispositions = tuple(dispositions or TERMINAL_DISPOSITIONS)
    if set(raw_keys) != set(schema["semantic"]):
        raise LifecycleContractError("coverage raw-key surface differs from normative schema")
    if set(dispositions) != set(TERMINAL_DISPOSITIONS):
        raise LifecycleContractError("coverage disposition surface differs from normative contract")
    cells = []
    for mode in ("closure", "audit"):
        for phase in ("entry", "exit"):
            for disposition in dispositions:
                for key in raw_keys:
                    semantic = schema["semantic"][key]
                    lifecycle = schema["lifecycle"][RAW_SOURCE_REQUIREMENT[key]]
                    if phase == "entry" and lifecycle == "closer-authored":
                        outcome = "CLEAN"
                    elif semantic in {"closure_record", "integrity"}:
                        outcome = "BLOCK"
                    elif key == "status_row_nonterminal":
                        outcome = "BLOCK"
                    elif phase == "entry":
                        outcome = "BLOCK" if disposition == "Complete" else "CARRY"
                    elif disposition == "Complete":
                        outcome = "BLOCK"
                    elif mode == "audit" and key in {
                            "gate_status_pending", "vtest_pending", "gate_heading_nonterminal"}:
                        outcome = "HYGIENE-IF-LEGITIMATELY-TERMINAL"
                    else:
                        outcome = "ACCOUNT"
                    cells.append((mode, phase, disposition, key, outcome))
    expected = 2 * 2 * len(dispositions) * len(raw_keys)
    if len(cells) != expected or any(not c[-1] for c in cells):
        raise LifecycleContractError("generated coverage has a gap or conflict")
    return cells
