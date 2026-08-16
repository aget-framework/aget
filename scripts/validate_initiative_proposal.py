#!/usr/bin/env python3
"""
validate_initiative_proposal.py

Mechanical verification runner for initiative proposals
(PROPOSAL_init_*.md files at planning/project-proposals/).

Implements V-INIT-PROP-001..014 from AGET_INITIATIVE_SPEC v1.0.1 §7.

Usage:
    python3 scripts/validate_initiative_proposal.py --file <path>
    python3 scripts/validate_initiative_proposal.py --file <path> --json

Exit codes:
    0 — all 14 V-tests pass
    1 — at least one V-test fails
    2 — usage error or file not readable

Governing spec: ../aget/specs/AGET_INITIATIVE_SPEC.md v1.0.1
Implementing skill: .claude/skills/aget-propose-initiative/SKILL.md v1.0.0
PROJECT_PLAN: planning/PROJECT_PLAN_aget_propose_initiative_v1.0.md Gate 2
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

INITIATIVES_DIR = REPO_ROOT / "planning" / "initiatives"
PROPOSALS_DIR = REPO_ROOT / "planning" / "project-proposals"
INDEX_PATH = PROPOSALS_DIR / "INDEX.md"
VERSION_JSON = REPO_ROOT / ".aget" / "version.json"


@dataclass
class VResult:
    """Single V-test result."""
    v_id: str
    cap_ids: list[str]
    passed: bool
    detail: str


def _section_body(text: str, heading: str) -> str:
    """Return the body of a `## {heading}` section up to the next `## ` heading."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}.*?$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def _table_rows(body: str) -> list[str]:
    """Return non-separator table rows in a section body (lines starting with `|`)."""
    rows = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", s):
            rows.append(s)
    return rows


# ---------------------------------------------------------------------------
# V-test implementations (one per V-INIT-PROP-### in spec §7)
# ---------------------------------------------------------------------------

def verify_v_init_prop_001(file_path: Path, _text: str) -> VResult:
    """V-INIT-PROP-001: Filename + path conformance.

    Verifies: CAP-INIT-PROP-001-01 (file at planning/project-proposals/),
              CAP-INIT-PROP-001-04 (PROPOSAL_init_ prefix, snake_case).
    """
    name = file_path.name
    ok_name = bool(re.match(r"^PROPOSAL_init_[a-z0-9_]+\.md$", name))
    try:
        ok_dir = file_path.resolve().parent.samefile(PROPOSALS_DIR.resolve())
    except FileNotFoundError:
        ok_dir = False
    passed = ok_name and ok_dir
    detail = (
        f"filename={'OK' if ok_name else 'BAD'} "
        f"dir={'OK' if ok_dir else 'NOT planning/project-proposals/'}"
    )
    return VResult("V-INIT-PROP-001", ["CAP-INIT-PROP-001-01", "CAP-INIT-PROP-001-04"], passed, detail)


REQUIRED_SECTIONS = [
    "## Problem",
    "## Evidence",
    "## Proposed Scope",
    "## Channels",
    "## Contributors",
    "## Cross-Initiative Overlap",
    "## Streams Sketch",
    "## Size Estimate",
    "## Dependencies",
    "## ADR-008 Readiness",
    "## Decision",
    "## Traceability",
]


def verify_v_init_prop_002(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-002: Required sections present.

    Verifies: CAP-INIT-PROP-001-03 (12 mandatory sections in order).
    """
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    passed = not missing
    detail = "all 12 sections present" if passed else f"MISSING: {missing}"
    return VResult("V-INIT-PROP-002", ["CAP-INIT-PROP-001-03"], passed, detail)


def verify_v_init_prop_003(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-003: PP-### unique + monotonic (split-mode per spec v1.1.1).

    Verifies: CAP-INIT-PROP-002-01 (PP-### assigned by incrementing INDEX max).

    Per spec v1.1.1, this V-test has two modes:
      - creation-mode: PP > max(INDEX others) OR PP == max+1 — for new proposals
      - revalidation-mode: PP exists in INDEX exactly once — for existing proposals

    Runners try creation-mode first; fall through to revalidation-mode on failure.
    A proposal that passes either mode satisfies CAP-INIT-PROP-002-01.
    """
    m = re.search(r"^\*\*Proposal ID\*\*:\s*PP-(\d+)", text, re.MULTILINE)
    if not m:
        return VResult("V-INIT-PROP-003", ["CAP-INIT-PROP-002-01"], False,
                       "no '**Proposal ID**: PP-NNN' header")
    pp = int(m.group(1))
    if not INDEX_PATH.exists():
        return VResult("V-INIT-PROP-003", ["CAP-INIT-PROP-002-01"], False,
                       f"INDEX missing at {INDEX_PATH}")
    index_text = INDEX_PATH.read_text()

    # Creation-mode
    others = [int(x) for x in re.findall(r"PP-(\d+)", index_text) if int(x) != pp]
    last_other = max(others) if others else 0
    creation_pass = pp > last_other or pp == last_other + 1

    # Revalidation-mode
    pp_padded_matches = re.findall(rf"PP-0*{pp}\b", index_text)
    revalidation_pass = len(pp_padded_matches) == 1

    passed = creation_pass or revalidation_pass
    mode = "creation" if creation_pass else ("revalidation" if revalidation_pass else "neither")
    detail = (
        f"PP={pp} mode={mode} "
        f"creation:max_others={last_other} "
        f"revalidation:index_count={len(pp_padded_matches)}"
    )
    return VResult("V-INIT-PROP-003", ["CAP-INIT-PROP-002-01"], passed, detail)


def verify_v_init_prop_004(file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-004: Proposed INIT-ID uniqueness.

    Verifies: CAP-INIT-PROP-002-03 (INIT-ID format + no collision).
    """
    m = re.search(r"INIT-[A-Z][A-Z0-9-]+", text)
    if not m:
        return VResult("V-INIT-PROP-004", ["CAP-INIT-PROP-002-03"], False, "no INIT-{UPPER-KEBAB} reference found")
    init_id = m.group(0)
    manifest_path = INITIATIVES_DIR / f"{init_id}.md"
    manifest_exists = manifest_path.exists()
    other_proposals = []
    if PROPOSALS_DIR.exists():
        for p in PROPOSALS_DIR.glob("PROPOSAL_init_*.md"):
            if p.resolve() == file_path.resolve():
                continue
            if init_id in p.read_text():
                other_proposals.append(p.name)
    passed = (not manifest_exists) and (not other_proposals)
    detail = (
        f"init_id={init_id} manifest_exists={manifest_exists} "
        f"other_proposals_referencing={other_proposals}"
    )
    return VResult("V-INIT-PROP-004", ["CAP-INIT-PROP-002-03"], passed, detail)


def verify_v_init_prop_005(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-005: Evidence row count >= 3.

    Verifies: CAP-INIT-PROP-007-01 (>=3 evidence rows).
    """
    body = _section_body(text, "Evidence")
    rows = _table_rows(body)
    data_rows = rows[1:] if rows else []
    passed = len(data_rows) >= 3
    detail = f"evidence_data_rows={len(data_rows)} (need >=3)"
    return VResult("V-INIT-PROP-005", ["CAP-INIT-PROP-007-01"], passed, detail)


TYPED_CITATION_RE = re.compile(
    r"L\d+|gh#\d+|session_|aget/|\.aget/|planning/|sops/|governance/|docs/|#\d+",
    re.IGNORECASE,
)


def verify_v_init_prop_006(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-006: Evidence Source citations are typed.

    Verifies: CAP-INIT-PROP-007-02 (each Source is L-doc/gh#/session/path/issue).
    """
    body = _section_body(text, "Evidence")
    rows = _table_rows(body)
    data_rows = rows[1:] if rows else []
    untyped = []
    for row in data_rows:
        parts = [p.strip() for p in row.strip("|").split("|")]
        # Columns: Observation | Source | Impact
        if len(parts) >= 2:
            source = parts[1]
            if not TYPED_CITATION_RE.search(source):
                untyped.append(source[:60])
    passed = not untyped
    detail = "all Sources typed" if passed else f"UNTYPED: {untyped}"
    return VResult("V-INIT-PROP-006", ["CAP-INIT-PROP-007-02"], passed, detail)


def verify_v_init_prop_007(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-007: Channels section non-empty.

    Verifies: CAP-INIT-PROP-005-01, 005-02 (>=1 data row, KB-only allowed).
    """
    body = _section_body(text, "Channels")
    rows = _table_rows(body)
    data_rows = rows[1:] if rows else []
    passed = len(data_rows) >= 1
    detail = f"channels_data_rows={len(data_rows)} (need >=1)"
    return VResult("V-INIT-PROP-007", ["CAP-INIT-PROP-005-01", "CAP-INIT-PROP-005-02"], passed, detail)


def verify_v_init_prop_008(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-008: Contributors section includes Principal.

    Verifies: CAP-INIT-PROP-006-03 (Principal row present by default).
    """
    body = _section_body(text, "Contributors")
    passed = "Principal" in body
    detail = "Principal row present" if passed else "Principal row MISSING"
    return VResult("V-INIT-PROP-008", ["CAP-INIT-PROP-006-03"], passed, detail)


def verify_v_init_prop_009(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-009: Cross-Initiative Overlap classifies every existing initiative.

    Verifies: CAP-INIT-PROP-004-01 (each existing INIT-* covered).
    """
    expected = []
    if INITIATIVES_DIR.exists():
        expected = sorted(p.stem for p in INITIATIVES_DIR.glob("INIT-*.md"))
    body = _section_body(text, "Cross-Initiative Overlap")
    found = set()
    for row in _table_rows(body):
        m = re.search(r"INIT-[A-Z][A-Z0-9-]+", row)
        if m:
            found.add(m.group(0))
    missing = [e for e in expected if e not in found]
    passed = not missing
    detail = (
        f"existing={len(expected)} covered={len(found & set(expected))}"
        + (f" MISSING={missing}" if missing else "")
    )
    return VResult("V-INIT-PROP-009", ["CAP-INIT-PROP-004-01"], passed, detail)


DECISION_OPTIONS = ["Principal reviewed", "Approved", "Deferred", "Rejected", "Fold into"]


def verify_v_init_prop_010(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-010: Decision section has all 5 options.

    Verifies: CAP-INIT-PROP-008-01, 008-02 (5 options including Fold).
    """
    body = _section_body(text, "Decision")
    missing = [opt for opt in DECISION_OPTIONS if opt not in body]
    passed = not missing
    detail = "all 5 options present" if passed else f"MISSING: {missing}"
    return VResult("V-INIT-PROP-010", ["CAP-INIT-PROP-008-01", "CAP-INIT-PROP-008-02"], passed, detail)


def verify_v_init_prop_011(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-011: Status is PROPOSED at creation.

    Verifies: CAP-INIT-PROP-010-01 (Status=PROPOSED).
    """
    passed = bool(re.search(r"^\*\*Status\*\*:\s*PROPOSED", text, re.MULTILINE))
    detail = "Status: PROPOSED found" if passed else "Status field missing or != PROPOSED"
    return VResult("V-INIT-PROP-011", ["CAP-INIT-PROP-010-01"], passed, detail)


def verify_v_init_prop_012(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-012: INDEX has a matching row.

    Verifies: CAP-INIT-PROP-009-01 (INDEX appended with PP-### row).
    """
    m = re.search(r"PP-(\d+)", text)
    if not m:
        return VResult("V-INIT-PROP-012", ["CAP-INIT-PROP-009-01"], False, "no PP-### in proposal")
    pp_id = m.group(0)
    if not INDEX_PATH.exists():
        return VResult("V-INIT-PROP-012", ["CAP-INIT-PROP-009-01"], False, f"INDEX missing at {INDEX_PATH}")
    passed = pp_id in INDEX_PATH.read_text()
    detail = f"{pp_id} {'present' if passed else 'NOT FOUND'} in INDEX"
    return VResult("V-INIT-PROP-012", ["CAP-INIT-PROP-009-01"], passed, detail)


def verify_v_init_prop_013(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-013: No INIT-*.md authored by skill (separation of concerns).

    Verifies: CAP-INIT-PROP-011-01 (propose skill MUST NOT create INIT-*.md manifest).
    Interpretation: the proposed INIT-ID has no corresponding INIT-{ID}.md file
    in planning/initiatives/. (The skill produces a proposal; the manifest is
    /aget-create-initiative's responsibility.)
    """
    m = re.search(r"INIT-[A-Z][A-Z0-9-]+", text)
    if not m:
        return VResult("V-INIT-PROP-013", ["CAP-INIT-PROP-011-01"], True,
                       "no INIT-ID referenced (vacuously passes)")
    init_id = m.group(0)
    manifest_path = INITIATIVES_DIR / f"{init_id}.md"
    passed = not manifest_path.exists()
    detail = f"manifest {init_id}.md {'absent (OK)' if passed else 'PRESENT (separation violated)'}"
    return VResult("V-INIT-PROP-013", ["CAP-INIT-PROP-011-01"], passed, detail)


def verify_v_init_prop_014(_file_path: Path, text: str) -> VResult:
    """V-INIT-PROP-014: Target Versions not past-start.

    Verifies: CAP-INIT-PROP-012-02, 012-03 (start version > current aget_version).
    """
    m = re.search(r"\*\*Target Versions\*\*:\s*v(\d+)\.(\d+)", text)
    if not m:
        return VResult("V-INIT-PROP-014", ["CAP-INIT-PROP-012-02", "CAP-INIT-PROP-012-03"],
                       False, "no '**Target Versions**: vX.Y' header")
    start = (int(m.group(1)), int(m.group(2)))
    if not VERSION_JSON.exists():
        return VResult("V-INIT-PROP-014", ["CAP-INIT-PROP-012-02", "CAP-INIT-PROP-012-03"],
                       False, f"version.json missing at {VERSION_JSON}")
    current_str = json.loads(VERSION_JSON.read_text())["aget_version"]
    cm = re.match(r"^(\d+)\.(\d+)", current_str)
    current = (int(cm.group(1)), int(cm.group(2))) if cm else (0, 0)
    passed = start > current
    detail = f"start=v{start[0]}.{start[1]} current=v{current[0]}.{current[1]}"
    return VResult("V-INIT-PROP-014", ["CAP-INIT-PROP-012-02", "CAP-INIT-PROP-012-03"], passed, detail)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

V_TESTS = [
    verify_v_init_prop_001,
    verify_v_init_prop_002,
    verify_v_init_prop_003,
    verify_v_init_prop_004,
    verify_v_init_prop_005,
    verify_v_init_prop_006,
    verify_v_init_prop_007,
    verify_v_init_prop_008,
    verify_v_init_prop_009,
    verify_v_init_prop_010,
    verify_v_init_prop_011,
    verify_v_init_prop_012,
    verify_v_init_prop_013,
    verify_v_init_prop_014,
]


def run_all(file_path: Path) -> list[VResult]:
    text = file_path.read_text()
    return [fn(file_path, text) for fn in V_TESTS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an initiative proposal against AGET_INITIATIVE_SPEC v1.0.1 §7"
    )
    parser.add_argument("--file", "-f", required=True, type=Path, help="Path to PROPOSAL_init_*.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-test detail (summary only)")
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 2

    results = run_all(args.file)
    n_pass = sum(1 for r in results if r.passed)
    n_total = len(results)
    all_pass = n_pass == n_total

    if args.json:
        out = {
            "file": str(args.file),
            "spec": "AGET_INITIATIVE_SPEC v1.0.1 §7",
            "n_pass": n_pass,
            "n_total": n_total,
            "all_pass": all_pass,
            "results": [asdict(r) for r in results],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"=== Validating {args.file} against AGET_INITIATIVE_SPEC v1.0.1 §7 ===")
        if not args.quiet:
            for r in results:
                marker = "PASS" if r.passed else "FAIL"
                print(f"  [{marker}] {r.v_id} ({', '.join(r.cap_ids)}): {r.detail}")
        print(f"\n{n_pass}/{n_total} V-tests passed " + ("(ALL PASS)" if all_pass else "(FAILURES)"))

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
