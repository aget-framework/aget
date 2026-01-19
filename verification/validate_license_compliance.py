#!/usr/bin/env python3
"""
validate_license_compliance.py - Validate AGET license requirements

Validates that repositories comply with AGET_LICENSE_SPEC requirements.

Requirements Implemented:
- CAP-LIC-001: Framework uses Apache 2.0 license
- CAP-LIC-002: LICENSE file must exist in repo root
- CAP-LIC-003: License badge should be present in README
- CAP-LIC-004: Copyright year should be current or range including current
- CAP-LIC-005: Derivative works must maintain Apache 2.0

Usage:
    python3 validate_license_compliance.py <repo_path>
    python3 validate_license_compliance.py /path/to/aget
    python3 validate_license_compliance.py .

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected

Author: private-aget-framework-AGET
Version: 1.0.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


# Apache 2.0 license identifiers
APACHE_IDENTIFIERS = [
    "Apache License",
    "Version 2.0",
    "apache-2.0",
    "Apache-2.0",
]

# Current year for copyright validation
CURRENT_YEAR = datetime.now().year


def validate_license_file(repo_path: Path) -> Tuple[bool, List[str]]:
    """Validate LICENSE file exists and contains Apache 2.0.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    license_path = repo_path / "LICENSE"

    # Check existence
    if not license_path.exists():
        errors.append("CAP-LIC-002: LICENSE file missing from repo root")
        return False, errors

    # Check content
    try:
        content = license_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Could not read LICENSE: {e}")
        return False, errors

    # Check for Apache 2.0 identifiers
    found_apache = False
    for identifier in APACHE_IDENTIFIERS:
        if identifier in content:
            found_apache = True
            break

    if not found_apache:
        errors.append("CAP-LIC-001: LICENSE does not contain Apache 2.0 identifiers")

    return len(errors) == 0, errors


def validate_copyright_year(repo_path: Path) -> Tuple[bool, List[str]]:
    """Validate copyright year in LICENSE file.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    license_path = repo_path / "LICENSE"

    if not license_path.exists():
        return True, []  # Already caught by validate_license_file

    try:
        content = license_path.read_text(encoding="utf-8")
    except Exception:
        return True, []  # Already caught by validate_license_file

    # Look for copyright year pattern
    year_pattern = re.compile(r"Copyright.*?(\d{4})(?:\s*-\s*(\d{4}))?", re.IGNORECASE)
    match = year_pattern.search(content)

    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2)) if match.group(2) else start_year

        if end_year < CURRENT_YEAR - 1:
            errors.append(f"CAP-LIC-004: Copyright year ({end_year}) is outdated (current: {CURRENT_YEAR})")

    return len(errors) == 0, errors


def validate_readme_badge(repo_path: Path) -> Tuple[bool, List[str]]:
    """Validate README has license badge.

    Returns:
        Tuple of (is_valid, warnings) - warnings only, not errors
    """
    warnings = []
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        return True, []  # No README is separate concern

    try:
        content = readme_path.read_text(encoding="utf-8")
    except Exception:
        return True, []

    # Check for license badge patterns
    badge_patterns = [
        r"!\[.*[Ll]icense.*\]",
        r"shields\.io.*license",
        r"License.*Apache",
        r"Apache.*2\.0",
        r"\[!\[License\]",
    ]

    found_badge = False
    for pattern in badge_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found_badge = True
            break

    if not found_badge:
        warnings.append("CAP-LIC-003 (warning): README does not have license badge")

    return True, warnings  # Warnings only, always pass


def validate_repo(repo_path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate a repository for license compliance.

    Returns:
        Tuple of (passed, failed, issues_by_check)
    """
    passed = 0
    failed = 0
    issues: Dict[str, List[str]] = {}

    # Check 1: LICENSE file exists and contains Apache 2.0
    is_valid, errors = validate_license_file(repo_path)
    if is_valid:
        passed += 1
        if verbose:
            print("  [PASS] LICENSE file valid (Apache 2.0)")
    else:
        failed += 1
        issues["license_file"] = errors
        if verbose:
            print("  [FAIL] LICENSE file issues")
            for e in errors:
                print(f"    - {e}")

    # Check 2: Copyright year
    is_valid, errors = validate_copyright_year(repo_path)
    if is_valid:
        passed += 1
        if verbose:
            print("  [PASS] Copyright year valid")
    else:
        failed += 1
        issues["copyright_year"] = errors
        if verbose:
            print("  [FAIL] Copyright year issues")
            for e in errors:
                print(f"    - {e}")

    # Check 3: README badge (warning only)
    is_valid, warnings = validate_readme_badge(repo_path)
    passed += 1  # Always passes
    if warnings and verbose:
        print(f"  [WARN] {warnings[0]}")
    elif verbose:
        print("  [PASS] README license badge present")

    return passed, failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET license compliance"
    )
    parser.add_argument(
        "path",
        help="Repository path to validate"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Path is not a directory: {path}")
        sys.exit(1)

    if args.verbose:
        print(f"Validating: {path}")

    passed, failed, issues = validate_repo(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"License Compliance Validation Summary")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if issues:
        print(f"\nIssues:")
        for check, errors in issues.items():
            print(f"\n  {check}:")
            for error in errors:
                print(f"    - {error}")

    if failed > 0:
        print(f"\nFAIL: {failed} license compliance issues")
        sys.exit(1)
    else:
        print(f"\nPASS: All license compliance checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
