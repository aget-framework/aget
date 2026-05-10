#!/usr/bin/env python3
"""
post_release_changelog_validator.py — CAP-REL-030 Post-Release CHANGELOG Validator (R-REL-026)

Verifies CHANGELOG.md compliance after release tag-cut + push for every
released repo (aget/ + 13 templates).

Requirements implemented (per AGET_RELEASE_SPEC.md §CAP-REL-030):
  R-REL-030-01: every released repo has a `## [X.Y.Z]` entry in CHANGELOG.md
  R-REL-030-02: each entry includes version header, date, and non-empty
                summary section (≥3 non-blank content lines under heading)
  R-REL-030-03: IF release is breaking (BREAKING_CHANGES_v{V}.md present)
                THEN entry SHALL include "Breaking Changes" subsection +
                ≥1 BC-NNN reference
  R-REL-030-04: sanitization — entries SHALL NOT contain private agent
                names (private-*-aget), private repo paths (gmelli/*),
                or fleet-size disclosures
  R-REL-030-05: per-repo PASS/FAIL emitted to
                sessions/post_release_changelog_audit_{VERSION}_{DATE}.md

Sibling to scripts/post_release_tag_validator.py (CAP-REL-031, v3.17 G1.T1.2).
v3.16 G1.6 SPEC-LANDED → v3.17 G1.T1.1 IMPLEMENTATION LANDED.

Closes L900/L909 sanitization-gap class (#1149/#1151 root cause) — sanitization
gate at write time + this contract as audit backstop.

Repo enumeration discipline (per F-V317-G1-CRITIC-013): explicit RELEASE_REPOS
default list + `--repos` CLI override. Hardcoded enumeration is a drift-vector
(see SOP_release_process.md v1.45 changelog); this script's explicit list is
provisional pending v3.18 REQ-REL-fleet-registry contract.

Usage:
  python3 scripts/post_release_changelog_validator.py --version 3.16.0
  python3 scripts/post_release_changelog_validator.py --version 3.17.0 --cwd /path/to/aget-framework
  python3 scripts/post_release_changelog_validator.py --version 3.17.0 --repos aget,template-advisor-aget

Exit codes:
  0 = all required checks PASS
  1 = one or more required checks FAIL
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path
from typing import Optional


# Default 14-repo list (aget + 13 templates including uppercase document-processor).
# Per F-V317-G1-CRITIC-007 lesson: case-sensitive glob `template-*-aget` silently
# skips template-document-processor-AGET; explicit list avoids the drift.
RELEASE_REPOS_DEFAULT = [
    "aget",
    "template-advisor-aget",
    "template-analyst-aget",
    "template-architect-aget",
    "template-consultant-aget",
    "template-developer-aget",
    "template-executive-aget",
    "template-operator-aget",
    "template-researcher-aget",
    "template-reviewer-aget",
    "template-spec-engineer-aget",
    "template-supervisor-aget",
    "template-worker-aget",
    "template-document-processor-AGET",
]

# Sanitization patterns per R-REL-030-04.
# Sanitization regexes per R-REL-030-04. Middle-segment charclass is case-flexible
# to mirror the trailing `(?:aget|AGET)` flexibility — closes F-V317-G1-CRITIC-014
# (mixed-case middle segment escape; e.g., `private-Impact-aget`).
PRIVATE_AGENT_RE = re.compile(r"\bprivate-[A-Za-z0-9_-]+-(?:aget|AGET)\b")
PRIVATE_REPO_RE = re.compile(r"\bgmelli/[a-zA-Z0-9_-]+\b")
FLEET_SIZE_RE = re.compile(r"\b\d{2,}\s*agents?\s*in\s*(?:the\s*)?fleet\b", re.IGNORECASE)


def extract_changelog_block(content: str, version: str) -> Optional[str]:
    """Extract the `## [X.Y.Z]` heading + body, ending at next `## [` or EOF."""
    pattern = rf"^## \[{re.escape(version)}\].*?(?=^## \[|\Z)"
    m = re.search(pattern, content, re.M | re.S)
    return m.group(0) if m else None


def check_changelog_present(repo_root: Path, version: str) -> tuple[bool, str]:
    """R-REL-030-01: CHANGELOG.md has `## [X.Y.Z]` entry."""
    cl_path = repo_root / "CHANGELOG.md"
    if not cl_path.exists():
        return False, f"{cl_path} missing"
    block = extract_changelog_block(cl_path.read_text(), version)
    if block is None:
        return False, f"no `## [{version}]` heading in CHANGELOG.md"
    return True, f"`## [{version}]` heading found"


def check_entry_complete(repo_root: Path, version: str) -> tuple[bool, str]:
    """R-REL-030-02: entry includes version header, date, and ≥3 content lines."""
    cl_path = repo_root / "CHANGELOG.md"
    if not cl_path.exists():
        return False, f"{cl_path} missing"
    block = extract_changelog_block(cl_path.read_text(), version)
    if block is None:
        return False, f"no `## [{version}]` block to inspect"
    heading = block.splitlines()[0]
    # Date pattern: `## [X.Y.Z] - YYYY-MM-DD` (or with surrounding whitespace)
    if not re.search(r"\[\d+\.\d+\.\d+\]\s*-\s*\d{4}-\d{2}-\d{2}", heading):
        return False, f"heading lacks YYYY-MM-DD date: {heading!r}"
    body_lines = [l for l in block.splitlines()[1:] if l.strip()]
    if len(body_lines) < 3:
        return False, f"only {len(body_lines)} non-blank content lines under heading; require ≥3"
    return True, f"heading dated; {len(body_lines)} content lines"


def check_breaking_consistency(repo_root: Path, version: str) -> tuple[Optional[bool], str]:
    """R-REL-030-03: IF release IS breaking THEN entry has Breaking Changes + BC-NNN.

    "Release IS breaking" detection signals (closes F-V317-G1-CRITIC-015):
      (1) BREAKING_CHANGES_v{V}.md present (versioned file at docs/ or repo root)
      (2) BREAKING_CHANGES.md present (unsuffixed file at docs/ or repo root)
      (3) `## [X.Y.Z]` block contains a "Breaking Changes" subsection
    Any of (1)/(2)/(3) → release is breaking → require BC-NNN reference.
    """
    # Signal (1): versioned BREAKING_CHANGES_v{V}.md
    versioned_paths = [
        repo_root / "docs" / f"BREAKING_CHANGES_v{version}.md",
        repo_root / f"BREAKING_CHANGES_v{version}.md",
    ]
    # Signal (2): unsuffixed BREAKING_CHANGES.md (catches releases that don't
    # follow the versioned-file convention — F-015 closure)
    unsuffixed_paths = [
        repo_root / "docs" / "BREAKING_CHANGES.md",
        repo_root / "BREAKING_CHANGES.md",
    ]
    bc_file_present = any(p.exists() for p in versioned_paths + unsuffixed_paths)

    cl_path = repo_root / "CHANGELOG.md"
    block = None
    if cl_path.exists():
        block = extract_changelog_block(cl_path.read_text(), version)

    # Signal (3): Breaking Changes subsection in changelog block itself
    bc_in_changelog = bool(
        block
        and re.search(r"###\s*Breaking Changes\b|^\s*\*?\*?Breaking Changes\*?\*?", block, re.M)
    )

    is_breaking = bc_file_present or bc_in_changelog
    if not is_breaking:
        return None, f"no breaking-change signal detected (N/A — non-breaking release)"
    if not cl_path.exists():
        return False, "CHANGELOG.md missing while breaking-change signal present"
    if block is None:
        return False, f"breaking release but no `## [{version}]` block"
    if not re.search(r"###\s*Breaking Changes\b|^\s*\*?\*?Breaking Changes\*?\*?", block, re.M):
        return False, "breaking release: CHANGELOG entry lacks 'Breaking Changes' subsection"
    if not re.search(r"\bBC-\d+\b", block):
        return False, "breaking release: CHANGELOG entry missing BC-NNN reference"
    return True, "breaking release: 'Breaking Changes' subsection + BC-NNN present"


def check_sanitization(repo_root: Path, version: str) -> tuple[bool, str]:
    """R-REL-030-04: entry SHALL NOT contain private patterns."""
    cl_path = repo_root / "CHANGELOG.md"
    if not cl_path.exists():
        return False, f"{cl_path} missing"
    block = extract_changelog_block(cl_path.read_text(), version)
    if block is None:
        return False, f"no `## [{version}]` block to inspect"
    findings = []
    for label, pattern in [
        ("private agent name", PRIVATE_AGENT_RE),
        ("private repo path", PRIVATE_REPO_RE),
        ("fleet-size disclosure", FLEET_SIZE_RE),
    ]:
        matches = pattern.findall(block)
        if matches:
            for m in matches:
                # Find line number for diagnostic
                for lineno, line in enumerate(block.splitlines(), start=1):
                    if m in line:
                        findings.append(f"{label} '{m}' at line +{lineno}")
                        break
    if findings:
        return False, "sanitization violations: " + "; ".join(findings[:5])
    return True, "no private-pattern leaks detected"


def emit_audit(
    version: str,
    per_repo: dict[str, dict[str, tuple[Optional[bool], str]]],
    audit_path: Path,
) -> None:
    """R-REL-030-05: per-repo PASS/FAIL audit emission."""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Post-Release CHANGELOG Audit — v{version}",
        "",
        f"**Date**: {datetime.date.today().isoformat()}",
        f"**Validator**: scripts/post_release_changelog_validator.py (CAP-REL-030)",
        f"**Spec**: AGET_RELEASE_SPEC.md §CAP-REL-030 (R-REL-026)",
        "",
        "## Per-Repo Results",
        "",
        "| Repo | R-REL-030-01 | R-REL-030-02 | R-REL-030-03 | R-REL-030-04 | Overall |",
        "|------|:------------:|:------------:|:------------:|:------------:|:-------:|",
    ]
    for repo, checks in per_repo.items():
        cells = []
        any_fail = False
        for cid in ("R-REL-030-01", "R-REL-030-02", "R-REL-030-03", "R-REL-030-04"):
            status, _ = checks.get(cid, (False, "missing"))
            if status is True:
                cells.append("PASS")
            elif status is False:
                cells.append("FAIL")
                any_fail = True
            else:
                cells.append("N/A")
        overall = "FAIL" if any_fail else "PASS"
        lines.append(f"| {repo} | " + " | ".join(cells) + f" | {overall} |")
    lines.append("")
    lines.append("## Failure Details")
    lines.append("")
    any_failures = False
    for repo, checks in per_repo.items():
        repo_failures = [(cid, detail) for cid, (status, detail) in checks.items() if status is False]
        if repo_failures:
            any_failures = True
            lines.append(f"### {repo}")
            lines.append("")
            for cid, detail in repo_failures:
                lines.append(f"- **{cid}**: {detail}")
            lines.append("")
    if not any_failures:
        lines.append("None — all checks passed across all repos.")
        lines.append("")
    audit_path.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Post-Release CHANGELOG Validator (CAP-REL-030, R-REL-026)",
    )
    ap.add_argument("--version", required=True, help="Released version, e.g. 3.16.0")
    ap.add_argument(
        "--cwd",
        default=None,
        help="aget-framework root directory (default: current dir; expects sibling repos at this level)",
    )
    ap.add_argument(
        "--repos",
        default=None,
        help="Comma-separated repo list (default: 14-repo RELEASE_REPOS_DEFAULT). Provided to allow per-release override pending v3.18 FLEET_REGISTRY contract.",
    )
    ap.add_argument(
        "--sessions-dir",
        default="sessions",
        help="Directory for R-REL-030-05 audit emission (default: sessions/)",
    )
    ap.add_argument("--quiet", action="store_true", help="Suppress per-check stdout")
    args = ap.parse_args()

    version = args.version.lstrip("v")
    framework_root = Path(args.cwd) if args.cwd else Path.cwd()
    repos = (
        [r.strip() for r in args.repos.split(",") if r.strip()]
        if args.repos
        else list(RELEASE_REPOS_DEFAULT)
    )

    per_repo: dict[str, dict[str, tuple[Optional[bool], str]]] = {}
    failed_overall = False

    for repo in repos:
        repo_root = framework_root / repo
        if not repo_root.exists():
            per_repo[repo] = {
                "R-REL-030-01": (False, f"repo dir not found: {repo_root}"),
                "R-REL-030-02": (False, "skipped (repo dir missing)"),
                "R-REL-030-03": (False, "skipped (repo dir missing)"),
                "R-REL-030-04": (False, "skipped (repo dir missing)"),
            }
            failed_overall = True
            continue
        per_repo[repo] = {
            "R-REL-030-01": check_changelog_present(repo_root, version),
            "R-REL-030-02": check_entry_complete(repo_root, version),
            "R-REL-030-03": check_breaking_consistency(repo_root, version),
            "R-REL-030-04": check_sanitization(repo_root, version),
        }
        if any(s is False for s, _ in per_repo[repo].values()):
            failed_overall = True

    # Audit emission path resolution. Closes F-V317-G1-B3-CRITIC-001 (sessions/
    # pollution at framework-root): when --cwd points to a directory without
    # .aget/ marker, require explicit --sessions-dir.
    cwd_has_aget = (framework_root / ".aget").exists()
    sessions_dir_path = Path(args.sessions_dir)
    if sessions_dir_path.is_absolute():
        sessions_dir = sessions_dir_path
    elif cwd_has_aget:
        sessions_dir = framework_root / sessions_dir_path
    elif args.sessions_dir != "sessions":
        sessions_dir = framework_root / sessions_dir_path
    else:
        print(
            "ERROR: --cwd points to a path without .aget/ (framework-root level) "
            "and --sessions-dir defaulted to 'sessions'. This would create "
            f"'{framework_root}/sessions/' which is outside any agent's session tree. "
            "Specify --sessions-dir explicitly (absolute path OR a path you intend "
            "to live under framework_root).",
            file=sys.stderr,
        )
        return 2
    audit_path = sessions_dir / f"post_release_changelog_audit_{version}_{datetime.date.today().isoformat()}.md"
    emit_audit(version, per_repo, audit_path)

    if not args.quiet:
        for repo, checks in per_repo.items():
            for cid, (status, detail) in checks.items():
                if status is True:
                    print(f"PASS {repo}/{cid}: {detail}")
                elif status is False:
                    print(f"FAIL {repo}/{cid}: {detail}")
                else:
                    print(f"N/A  {repo}/{cid}: {detail}")
        print(f"\nAudit emitted: {audit_path}")

    return 1 if failed_overall else 0


if __name__ == "__main__":
    sys.exit(main())
