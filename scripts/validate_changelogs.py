#!/usr/bin/env python3
"""Validate CHANGELOG entries exist across all repos for a target version.

Per R-SYNC-002, checks all template repos and core aget/ for a CHANGELOG.md
entry matching the target version.

Usage:
    python3 scripts/validate_changelogs.py --version 3.10.0

Exit codes:
    0 - All repos have CHANGELOG entry for target version
    1 - One or more repos missing CHANGELOG entry
    2 - Usage error
"""

import argparse
import re
import sys
from pathlib import Path

# All repos to check (relative to aget-framework/)
REPOS = [
    "aget",
    "template-advisor-aget",
    "template-analyst-aget",
    "template-architect-aget",
    "template-consultant-aget",
    "template-developer-aget",
    "template-document-processor-AGET",
    "template-executive-aget",
    "template-operator-aget",
    "template-researcher-aget",
    "template-reviewer-aget",
    "template-spec-engineer-aget",
    "template-supervisor-aget",
    "template-worker-aget",
]


def check_changelog(repo_path: Path, version: str) -> tuple[bool, str]:
    """Check if CHANGELOG.md contains an entry for the given version."""
    changelog = repo_path / "CHANGELOG.md"

    if not changelog.exists():
        return False, "CHANGELOG.md not found"

    content = changelog.read_text()

    # Look for version header patterns:
    # ## [3.10.0]  or  ## 3.10.0  or  ## v3.10.0
    patterns = [
        rf"##\s+\[{re.escape(version)}\]",
        rf"##\s+v?{re.escape(version)}",
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True, "Entry found"

    return False, "No entry for this version"


def main():
    parser = argparse.ArgumentParser(
        description="Validate CHANGELOG entries across repos (R-SYNC-002)"
    )
    parser.add_argument("--version", required=True,
                        help="Target version to check (e.g., 3.10.0)")
    args = parser.parse_args()

    # Determine aget-framework base directory
    script_dir = Path(__file__).resolve().parent.parent  # private agent repo
    base_dir = script_dir.parent  # aget-framework/

    print(f"CHANGELOG Validation for v{args.version}")
    print(f"Base: {base_dir}")
    print(f"Repos: {len(REPOS)}")
    print()

    missing = []
    found = []

    for repo_name in REPOS:
        repo_path = base_dir / repo_name
        if not repo_path.exists():
            print(f"  SKIP: {repo_name} (repo not found)")
            continue

        has_entry, reason = check_changelog(repo_path, args.version)
        if has_entry:
            print(f"  OK: {repo_name}")
            found.append(repo_name)
        else:
            print(f"  MISSING: {repo_name} — {reason}")
            missing.append(repo_name)

    # Summary
    print(f"\n{'='*40}")
    print(f"Results: {len(found)} OK, {len(missing)} missing")

    if missing:
        print(f"\nFAIL: {len(missing)} repo(s) missing CHANGELOG entry for v{args.version}:")
        for repo in missing:
            print(f"  - {repo}")
        return 1

    # A zero denominator is not a pass. Skipped repos leave BOTH the numerator and
    # the denominator empty, so the success branch was reachable having opened no
    # file at all -- it printed "PASS: All 0 repos have CHANGELOG entry" and exited 0.
    # A consumer who clones this repo alone, or into a directory laid out differently,
    # got a green light from a check that inspected nothing.
    #
    # This is the zero-denominator family the sibling instrument's own docstring
    # already forbids: "an unparseable row must not read as a clean one." The rule was
    # written down next door and not applied here.
    if not found:
        print(f"\nFAIL: 0 of {len(REPOS)} repos were readable, so nothing was verified.")
        print("  A check that inspected no files has not passed -- it has not run.")
        print("  Likely cause: the repos are not laid out where this expects them.")
        print(f"  Expected siblings of: {Path(__file__).resolve().parent.parent}")
        return 1

    if len(found) < len(REPOS):
        print(f"\nFAIL: only {len(found)} of {len(REPOS)} repos were readable.")
        print("  Partial coverage is not a pass; the unread repos are unknown, not clean.")
        return 1

    print(f"PASS: All {len(found)}/{len(REPOS)} repos have CHANGELOG entry for v{args.version}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
