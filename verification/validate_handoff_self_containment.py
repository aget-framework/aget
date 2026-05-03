#!/usr/bin/env python3
"""
Validate RELEASE_HANDOFF self-containment.

Implements: AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v0.1 (REVIEWED 2026-05-03)
Traces to: H-RHSC-001 G2 (PROJECT_PLAN_release_handoff_self_containment_spec_v1.0.md)

Validates RELEASE_HANDOFF_v{X.Y.Z}.md against 8 CAPs (CAP-RHSC-001..008) and
11 sub-requirements (V-RHSC-001..011), emitting per-V-test PASS/FAIL/UNKNOWN
with file:line evidence.

Usage:
    python3 validate_handoff_self_containment.py --handoff <path>
    python3 validate_handoff_self_containment.py --handoff <path> \\
        --release-manifest <path> --prior-version v3.16.0
    python3 validate_handoff_self_containment.py --handoff <path> --json

Exit codes:
    0: All V-tests PASS (UNKNOWN tolerated unless --strict)
    1: Any V-test FAIL (or any UNKNOWN if --strict)
    2: Validator error (file not found, git unavailable, etc.)

JSON schema (when --json):
    {
      "version": "0.1.0",
      "handoff": "<path>",
      "results": [
        {"cap": "CAP-RHSC-NNN", "v_test": "V-RHSC-NNN",
         "status": "PASS|FAIL|UNKNOWN", "evidence": "<file:line or descriptive>"}
      ],
      "summary": {"pass": N, "fail": N, "unknown": N, "exit_code": N}
    }

Implementation notes (Auditor findings, AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC
v0.1 audit trail 2026-05-03):

    - CAP-RHSC-003 ("publication time" semantics): this validator compares cited
      SOP versions against canonical SOPs at validator RUN TIME. Drift (cited !=
      current canonical) is treated as FAIL regardless of cause (stale handoff
      vs post-publication SOP bump). Operator should re-run after canonical bumps.

    - V-RHSC-008 (dual-pass): accepts EITHER per-archetype enumeration OR an
      explicit "no per-archetype variation" disclaimer. Absence of both = FAIL.

    - V-RHSC-010 (substrate-modification): requires --prior-version to detect
      modifications via `git diff <prior>..HEAD -- verification/`. Without
      --prior-version, V-RHSC-010 returns UNKNOWN (FAIL only in --strict mode).
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


SCHEMA_VERSION = "0.1.0"


@dataclass
class CheckResult:
    cap: str
    v_test: str
    status: str  # PASS | FAIL | UNKNOWN
    evidence: str

    def to_dict(self):
        return asdict(self)


# CAP-RHSC-001: Dialog Reference Prohibition
DIALOG_PATTERNS = [
    r"consult framework manager",
    r"ask aget-framework",
    r"ask the framework",
    r"see private-[\w-]+-aget",
    r"reach out to",
    r"contact <agent>",
]


def check_cap_001_dialog_references(handoff_path: Path, lines: List[str]) -> CheckResult:
    pattern = re.compile("|".join(DIALOG_PATTERNS), re.IGNORECASE)
    matches = [f"{handoff_path}:{i}" for i, line in enumerate(lines, start=1) if pattern.search(line)]
    if matches:
        return CheckResult(
            "CAP-RHSC-001", "V-RHSC-001", "FAIL",
            f"{len(matches)} dialog-reference matches: {matches[:3]}{'...' if len(matches) > 3 else ''}",
        )
    return CheckResult(
        "CAP-RHSC-001", "V-RHSC-001", "PASS",
        f"{handoff_path}: 0 matches across {len(DIALOG_PATTERNS)} dialog-reference patterns",
    )


# CAP-RHSC-002: Sanitization Invariants (4 sub-requirements)
SANITIZATION_PATTERNS = [
    ("V-RHSC-002", "R-RHSC-002-01", r"private-[\w-]+-(?:aget|AGET)", "private agent name"),
    ("V-RHSC-003", "R-RHSC-002-02", r"(?:gmelli/[\w-]+|~/github/private-)", "private repo path"),
    ("V-RHSC-004", "R-RHSC-002-03", r"(?:\d+\s+agents?\s+in\s+fleet|fleet\s+of\s+\d+)", "fleet size disclosure"),
    ("V-RHSC-005", "R-RHSC-002-04", r"(?:SESSION_\d{4}-\d{2}-\d{2}|FLEET-[\w]+-\d+)", "internal session/project ID"),
]


def check_cap_002_sanitization(handoff_path: Path, lines: List[str]) -> List[CheckResult]:
    results = []
    for v_test, r_id, pattern, label in SANITIZATION_PATTERNS:
        regex = re.compile(pattern)
        matches = [f"{handoff_path}:{i}" for i, line in enumerate(lines, start=1) if regex.search(line)]
        if matches:
            results.append(CheckResult(
                "CAP-RHSC-002", v_test, "FAIL",
                f"{r_id}: {len(matches)} {label} matches: {matches[:3]}",
            ))
        else:
            results.append(CheckResult(
                "CAP-RHSC-002", v_test, "PASS",
                f"{r_id}: 0 {label} matches",
            ))
    return results


# CAP-RHSC-003: SOP Version Parity (closes L910)
SOP_REFERENCE_RE = re.compile(r"(SOP_[\w]+\.md)\s+v(\d+\.\d+)")
VERSION_HEADER_RE = re.compile(r"\*\*Version\*\*:?\s*v?(\d+\.\d+)")


def check_cap_003_sop_version_parity(handoff_path: Path, lines: List[str], canonical_root: Path) -> CheckResult:
    references = []
    for i, line in enumerate(lines, start=1):
        for m in SOP_REFERENCE_RE.finditer(line):
            references.append((m.group(1), m.group(2), i))

    if not references:
        return CheckResult(
            "CAP-RHSC-003", "V-RHSC-006", "PASS",
            "No SOP version references in handoff (vacuously satisfied)",
        )

    mismatches = []
    for sop_name, cited_version, line_no in references:
        canonical_sop = canonical_root / "sops" / sop_name
        if not canonical_sop.exists():
            mismatches.append(f"{handoff_path}:{line_no}: {sop_name} v{cited_version} cited but canonical not found at {canonical_sop}")
            continue
        try:
            sop_lines = canonical_sop.read_text().splitlines()[:30]
        except OSError as e:
            mismatches.append(f"{handoff_path}:{line_no}: {sop_name} read error: {e}")
            continue
        canonical_version = None
        for sop_line in sop_lines:
            vm = VERSION_HEADER_RE.search(sop_line)
            if vm:
                canonical_version = vm.group(1)
                break
        if canonical_version is None:
            mismatches.append(f"{handoff_path}:{line_no}: {sop_name} canonical has no parseable Version header")
        elif canonical_version != cited_version:
            mismatches.append(f"{handoff_path}:{line_no}: {sop_name} cited v{cited_version}, canonical v{canonical_version}")

    if mismatches:
        return CheckResult(
            "CAP-RHSC-003", "V-RHSC-006", "FAIL",
            f"{len(mismatches)} parity violations: {mismatches[:3]}",
        )
    return CheckResult(
        "CAP-RHSC-003", "V-RHSC-006", "PASS",
        f"{len(references)} SOP version references, all match canonical",
    )


# CAP-RHSC-004: Breaking Change Detection Commands
BC_PATTERN = re.compile(r"BC-\d{3,}")
CODE_FENCE_RE = re.compile(r"^```")


def check_cap_004_breaking_change_commands(handoff_path: Path, lines: List[str]) -> CheckResult:
    bc_lines = [(i, line) for i, line in enumerate(lines, start=1) if BC_PATTERN.search(line)]
    if not bc_lines:
        return CheckResult(
            "CAP-RHSC-004", "V-RHSC-007", "PASS",
            "No BC-NNN references in handoff (vacuously satisfied)",
        )
    fence_lines = [i for i, line in enumerate(lines, start=1) if CODE_FENCE_RE.match(line)]

    missing = []
    for bc_line_no, _ in bc_lines:
        nearby = [f for f in fence_lines if abs(f - bc_line_no) <= 20]
        if not nearby:
            missing.append(f"{handoff_path}:{bc_line_no}: BC reference without code fence within +/-20 lines")

    if missing:
        return CheckResult(
            "CAP-RHSC-004", "V-RHSC-007", "FAIL",
            f"{len(missing)} BC references missing code fences: {missing[:3]}",
        )
    return CheckResult(
        "CAP-RHSC-004", "V-RHSC-007", "PASS",
        f"{len(bc_lines)} BC references, all have code fence within +/-20 lines",
    )


# CAP-RHSC-005: Per-Archetype Branch Explicitness
ARCHETYPES = [
    "worker", "supervisor", "advisor", "analyst", "architect",
    "consultant", "developer", "executive", "operator",
    "researcher", "reviewer", "spec-engineer", "document-processor",
]
ARCHETYPE_RE = re.compile(r"\bFor\s+(" + "|".join(ARCHETYPES) + r")\b", re.IGNORECASE)
NO_VARIATION_RE = re.compile(r"no\s+per[- ]archetype\s+variation", re.IGNORECASE)


def check_cap_005_archetype_explicitness(handoff_path: Path, full_text: str) -> CheckResult:
    enumerations = ARCHETYPE_RE.findall(full_text)
    has_disclaimer = bool(NO_VARIATION_RE.search(full_text))

    if enumerations:
        unique_archetypes = sorted(set(e.lower() for e in enumerations))
        return CheckResult(
            "CAP-RHSC-005", "V-RHSC-008", "PASS",
            f"{len(enumerations)} archetype enumerations covering {len(unique_archetypes)} archetypes: {unique_archetypes[:5]}",
        )
    if has_disclaimer:
        return CheckResult(
            "CAP-RHSC-005", "V-RHSC-008", "PASS",
            '"no per-archetype variation" disclaimer present',
        )
    return CheckResult(
        "CAP-RHSC-005", "V-RHSC-008", "FAIL",
        "Neither per-archetype enumeration nor variation-disclaimer found",
    )


# CAP-RHSC-006: Sleeping Requirements Disclosure (closes L916)
SLEEPING_HEADER_RE = re.compile(r"^#+\s*Sleeping\s+Requirements?\s+Disclosure", re.IGNORECASE | re.MULTILINE)


def check_cap_006_sleeping_requirements(handoff_path: Path, full_text: str, release_manifest: Optional[Path]) -> CheckResult:
    if release_manifest is None:
        return CheckResult(
            "CAP-RHSC-006", "V-RHSC-009", "UNKNOWN",
            "No --release-manifest provided; cannot detect SPEC-LANDED CAPs",
        )
    if not release_manifest.exists():
        return CheckResult(
            "CAP-RHSC-006", "V-RHSC-009", "FAIL",
            f"--release-manifest not found: {release_manifest}",
        )

    manifest_text = release_manifest.read_text()
    has_spec_landed = "SPEC-LANDED" in manifest_text or "spec-landed" in manifest_text

    if not has_spec_landed:
        return CheckResult(
            "CAP-RHSC-006", "V-RHSC-009", "PASS",
            "Release manifest has no SPEC-LANDED CAPs; disclosure not required",
        )

    if not SLEEPING_HEADER_RE.search(full_text):
        return CheckResult(
            "CAP-RHSC-006", "V-RHSC-009", "FAIL",
            "Release ships SPEC-LANDED CAPs but handoff has no Sleeping Requirements Disclosure section",
        )
    return CheckResult(
        "CAP-RHSC-006", "V-RHSC-009", "PASS",
        "Sleeping Requirements Disclosure section present (SPEC-LANDED CAPs detected in manifest)",
    )


# CAP-RHSC-007: Measurement-Substrate Caveat
SUBSTRATE_SCRIPTS = {
    "health_check.py", "validate_archetype_skills.py",
    "verify_deployment.py", "validate_capability_spec.py",
    "validate_file_naming.py",
}
KR_RE = re.compile(r"(KR\d+|Key\s+Result\s+\d+).{0,200}?(PASS|FAIL)", re.IGNORECASE | re.DOTALL)
AS_MEASURED_RE = re.compile(r"as\s+measured\s+by", re.IGNORECASE)


def check_cap_007_substrate_caveat(handoff_path: Path, full_text: str, prior_version: Optional[str], canonical_root: Path) -> CheckResult:
    if prior_version is None:
        return CheckResult(
            "CAP-RHSC-007", "V-RHSC-010", "UNKNOWN",
            "No --prior-version provided; cannot detect substrate-script modifications",
        )

    try:
        result = subprocess.run(
            ["git", "-C", str(canonical_root), "diff", "--name-only", f"{prior_version}..HEAD", "--", "verification/"],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if result.returncode != 0:
            return CheckResult(
                "CAP-RHSC-007", "V-RHSC-010", "UNKNOWN",
                f"git diff returncode={result.returncode}: {result.stderr.strip()[:200]}",
            )
        modified_files = result.stdout.strip().splitlines()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return CheckResult(
            "CAP-RHSC-007", "V-RHSC-010", "UNKNOWN",
            f"git diff failed: {e}",
        )

    modified_substrate = [f for f in modified_files if Path(f).name in SUBSTRATE_SCRIPTS]

    if not modified_substrate:
        return CheckResult(
            "CAP-RHSC-007", "V-RHSC-010", "PASS",
            f"No measurement substrate scripts modified between {prior_version}..HEAD",
        )

    kr_claims = KR_RE.findall(full_text)
    if not kr_claims:
        return CheckResult(
            "CAP-RHSC-007", "V-RHSC-010", "PASS",
            f"Substrate scripts modified ({modified_substrate}) but no KR PASS/FAIL claims in handoff (vacuously satisfied)",
        )

    if not AS_MEASURED_RE.search(full_text):
        return CheckResult(
            "CAP-RHSC-007", "V-RHSC-010", "FAIL",
            f"Substrate scripts modified ({modified_substrate}) and {len(kr_claims)} KR claims present, but no 'as measured by' caveat",
        )
    return CheckResult(
        "CAP-RHSC-007", "V-RHSC-010", "PASS",
        f"{len(kr_claims)} KR claims with 'as measured by' caveat (modified substrate: {modified_substrate})",
    )


# CAP-RHSC-008: Deprecation Replacement Naming
DEPRECATIONS_HEADER_RE = re.compile(r"^#+\s*Deprecations?\b", re.IGNORECASE | re.MULTILINE)
ARROW_RE = re.compile(r"->|→")
NO_REPLACEMENT_RE = re.compile(r"no\s+replacement[;,)]?\s*behavior\s+removed", re.IGNORECASE)
TABLE_DIVIDER_RE = re.compile(r"\|\s*-+\s*\|")


def check_cap_008_deprecation_replacement(handoff_path: Path, full_text: str) -> CheckResult:
    section_match = DEPRECATIONS_HEADER_RE.search(full_text)
    if not section_match:
        return CheckResult(
            "CAP-RHSC-008", "V-RHSC-011", "PASS",
            "No Deprecations section in handoff (vacuously satisfied)",
        )

    start = section_match.end()
    next_section = re.search(r"^#+\s+\w", full_text[start:], re.MULTILINE)
    section_text = full_text[start:start + next_section.start()] if next_section else full_text[start:]

    table_rows = [l for l in section_text.splitlines()
                  if l.strip().startswith("|") and not TABLE_DIVIDER_RE.match(l.strip())]
    data_rows = table_rows[1:] if len(table_rows) > 1 else []

    if not data_rows:
        return CheckResult(
            "CAP-RHSC-008", "V-RHSC-011", "PASS",
            "Deprecations section present but no table data rows (vacuously satisfied)",
        )

    violations = [row.strip()[:80] for row in data_rows
                  if not (ARROW_RE.search(row) or NO_REPLACEMENT_RE.search(row))]

    if violations:
        return CheckResult(
            "CAP-RHSC-008", "V-RHSC-011", "FAIL",
            f"{len(violations)} deprecation rows missing arrow or no-replacement disclosure: {violations[:2]}",
        )
    return CheckResult(
        "CAP-RHSC-008", "V-RHSC-011", "PASS",
        f"{len(data_rows)} deprecation rows, all have replacement arrow or no-replacement disclosure",
    )


def run_all_checks(handoff_path: Path, canonical_root: Path,
                   release_manifest: Optional[Path], prior_version: Optional[str]) -> List[CheckResult]:
    text = handoff_path.read_text()
    lines = text.splitlines()

    results: List[CheckResult] = []
    results.append(check_cap_001_dialog_references(handoff_path, lines))
    results.extend(check_cap_002_sanitization(handoff_path, lines))
    results.append(check_cap_003_sop_version_parity(handoff_path, lines, canonical_root))
    results.append(check_cap_004_breaking_change_commands(handoff_path, lines))
    results.append(check_cap_005_archetype_explicitness(handoff_path, text))
    results.append(check_cap_006_sleeping_requirements(handoff_path, text, release_manifest))
    results.append(check_cap_007_substrate_caveat(handoff_path, text, prior_version, canonical_root))
    results.append(check_cap_008_deprecation_replacement(handoff_path, text))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RELEASE_HANDOFF self-containment per AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v0.1",
    )
    parser.add_argument("--handoff", required=True, type=Path,
                        help="Path to RELEASE_HANDOFF_v{X.Y.Z}.md")
    parser.add_argument("--canonical-root", type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help="Root of canonical aget/ directory (default: this script's parent.parent)")
    parser.add_argument("--release-manifest", type=Path, default=None,
                        help="Optional release manifest YAML for CAP-RHSC-006 SPEC-LANDED detection")
    parser.add_argument("--prior-version", type=str, default=None,
                        help="Prior release tag for CAP-RHSC-007 substrate-modification git diff (e.g., v3.16.0)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--strict", action="store_true", help="Treat UNKNOWN as FAIL")
    args = parser.parse_args()

    if not args.handoff.exists():
        print(f"Error: handoff not found: {args.handoff}", file=sys.stderr)
        return 2

    results = run_all_checks(args.handoff, args.canonical_root, args.release_manifest, args.prior_version)

    has_fail = any(r.status == "FAIL" for r in results)
    has_unknown = any(r.status == "UNKNOWN" for r in results)
    exit_code = 1 if has_fail or (args.strict and has_unknown) else 0

    if args.json:
        output = {
            "version": SCHEMA_VERSION,
            "handoff": str(args.handoff),
            "results": [r.to_dict() for r in results],
            "summary": {
                "pass": sum(1 for r in results if r.status == "PASS"),
                "fail": sum(1 for r in results if r.status == "FAIL"),
                "unknown": sum(1 for r in results if r.status == "UNKNOWN"),
                "exit_code": exit_code,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 70)
        print("RELEASE_HANDOFF Self-Containment Validation")
        print(f"Spec: AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v{SCHEMA_VERSION}")
        print(f"Handoff: {args.handoff}")
        print("=" * 70)
        for r in results:
            marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "UNKNOWN": "[UNK ]"}[r.status]
            print(f"  {marker} {r.v_test} ({r.cap})")
            print(f"         {r.evidence}")
        print("=" * 70)
        passes = sum(1 for r in results if r.status == "PASS")
        fails = sum(1 for r in results if r.status == "FAIL")
        unknowns = sum(1 for r in results if r.status == "UNKNOWN")
        print(f"Summary: {passes} PASS, {fails} FAIL, {unknowns} UNKNOWN (strict={args.strict})")
        print(f"Exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
