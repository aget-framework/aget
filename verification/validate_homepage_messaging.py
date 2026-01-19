#!/usr/bin/env python3
"""
validate_homepage_messaging.py - Validate GitHub organization homepage

Validates that the aget-framework organization homepage follows requirements.

Requirements Implemented:
- CAP-ORG-001: Homepage update requirements
- CAP-ORG-002: Homepage content structure
- R-REL-010: Version badges should be current
- R-REL-011: Roadmap should be visible

Usage:
    python3 validate_homepage_messaging.py <readme_path>
    python3 validate_homepage_messaging.py .github/profile/README.md

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


# Required sections in homepage
REQUIRED_SECTIONS = [
    "Overview",
    "Templates",
    "Roadmap",
]

# Alternative acceptable section names
SECTION_ALIASES = {
    "Overview": ["About", "Introduction", "What is AGET"],
    "Templates": ["Agent Templates", "Available Templates"],
    "Roadmap": ["Release Roadmap", "Upcoming", "Future"],
}

# Badge patterns to check
BADGE_PATTERNS = {
    "version": r"!\[.*[Vv]ersion.*\]|shields\.io.*version|badge.*v\d",
    "license": r"!\[.*[Ll]icense.*\]|shields\.io.*license",
    "release_date": r"!\[.*[Dd]ate.*\]|shields\.io.*date|\d{4}-\d{2}-\d{2}",
}


def validate_required_sections(content: str) -> Tuple[int, int, List[str]]:
    """Validate required sections are present.

    Returns:
        Tuple of (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    # Find all headers
    headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    headers_lower = [h.lower() for h in headers]

    for required in REQUIRED_SECTIONS:
        # Check main name and aliases
        names_to_check = [required.lower()] + [a.lower() for a in SECTION_ALIASES.get(required, [])]

        found = any(
            any(name in h for name in names_to_check)
            for h in headers_lower
        )

        if found:
            passed += 1
        else:
            failed += 1
            errors.append(f"CAP-ORG-002: Missing required section: {required}")

    return passed, failed, errors


def validate_badges(content: str) -> Tuple[int, int, List[str]]:
    """Validate required badges are present.

    Returns:
        Tuple of (passed, failed, warnings) - warnings only
    """
    passed = 0
    failed = 0
    warnings = []

    for badge_name, pattern in BADGE_PATTERNS.items():
        if re.search(pattern, content, re.IGNORECASE):
            passed += 1
        else:
            failed += 1
            warnings.append(f"CAP-ORG-001 (warning): Missing {badge_name} badge")

    return passed, failed, warnings


def validate_version_current(content: str) -> Tuple[bool, List[str]]:
    """Validate version badge is reasonably current.

    Returns:
        Tuple of (is_valid, warnings)
    """
    warnings = []

    # Look for version patterns
    version_match = re.search(r"v(\d+\.\d+\.\d+)", content)
    if version_match:
        version = version_match.group(1)
        major, minor, patch = map(int, version.split("."))

        # Check if version seems current (major >= 3 for AGET)
        if major < 3:
            warnings.append(f"R-REL-010 (warning): Version {version} may be outdated")

    return True, warnings  # Always passes, just warnings


def validate_roadmap_content(content: str) -> Tuple[bool, List[str]]:
    """Validate roadmap section has meaningful content.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Find roadmap section
    roadmap_match = re.search(r"##\s*.*[Rr]oadmap.*\n([\s\S]*?)(?=\n##|\Z)", content)

    if roadmap_match:
        roadmap_content = roadmap_match.group(1)

        # Check for version references
        has_versions = re.search(r"v\d+\.\d+", roadmap_content)
        if not has_versions:
            errors.append("R-REL-011: Roadmap should include version numbers")

        # Check for status indicators
        has_status = re.search(r"Current|Next|Planned|✅|⬜|🚧", roadmap_content)
        if not has_status:
            errors.append("R-REL-011: Roadmap should include status indicators")

    return len(errors) == 0, errors


def validate_homepage(path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate homepage content.

    Returns:
        Tuple of (passed, failed, issues)
    """
    total_passed = 0
    total_failed = 0
    issues: Dict[str, List[str]] = {}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return 0, 1, {"read_error": [f"Could not read file: {e}"]}

    # Check 1: Required sections
    passed, failed, errors = validate_required_sections(content)
    total_passed += passed
    total_failed += failed
    if errors:
        issues["sections"] = errors
    if verbose:
        print(f"  [{'PASS' if failed == 0 else 'FAIL'}] Required sections: {passed}/{passed + failed}")
        for e in errors:
            print(f"    - {e}")

    # Check 2: Badges (warning only)
    passed, failed, warnings = validate_badges(content)
    total_passed += passed  # Count as passed since warnings only
    if warnings and verbose:
        print(f"  [WARN] Badge issues:")
        for w in warnings:
            print(f"    - {w}")
    elif verbose:
        print(f"  [PASS] All badges present")

    # Check 3: Version currency (warning only)
    is_valid, warnings = validate_version_current(content)
    total_passed += 1  # Always passes
    if warnings and verbose:
        print(f"  [WARN] {warnings[0]}")
    elif verbose:
        print(f"  [PASS] Version appears current")

    # Check 4: Roadmap content
    is_valid, errors = validate_roadmap_content(content)
    if is_valid:
        total_passed += 1
        if verbose:
            print(f"  [PASS] Roadmap content valid")
    else:
        total_failed += 1
        issues["roadmap"] = errors
        if verbose:
            print(f"  [FAIL] Roadmap content issues")
            for e in errors:
                print(f"    - {e}")

    return total_passed, total_failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate GitHub organization homepage"
    )
    parser.add_argument(
        "path",
        help="Path to homepage README.md"
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

    if not path.is_file():
        print(f"Error: Path is not a file: {path}")
        sys.exit(1)

    if args.verbose:
        print(f"Validating: {path}")

    passed, failed, issues = validate_homepage(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"Homepage Messaging Validation Summary")
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
        print(f"\nFAIL: {failed} homepage messaging issues")
        sys.exit(1)
    else:
        print(f"\nPASS: All homepage messaging checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
