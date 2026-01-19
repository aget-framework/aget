#!/usr/bin/env python3
"""
validate_sop_compliance.py - Validate SOP format and structure

Validates that SOP documents conform to AGET_SOP_SPEC requirements.

Requirements Implemented:
- CAP-SOP-001: SOP naming convention (SOP_*.md)
- CAP-SOP-002: Required sections (Purpose, Scope, Procedure, etc.)
- CAP-SOP-003: Version and status fields
- CAP-SOP-004: Procedure steps should be numbered

Usage:
    python3 validate_sop_compliance.py <path>
    python3 validate_sop_compliance.py sops/SOP_release_process.md
    python3 validate_sop_compliance.py sops/

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


# Required SOP sections
REQUIRED_SECTIONS = [
    "Purpose",
    "Scope",
]

# Recommended SOP sections
RECOMMENDED_SECTIONS = [
    "Procedure",
    "Prerequisites",
    "Steps",
    "References",
]

# Header field pattern
HEADER_FIELD_PATTERN = re.compile(r"\*\*([^*]+)\*\*:\s*(.+)")


def validate_sop_naming(path: Path) -> Tuple[bool, List[str]]:
    """Validate SOP file naming convention.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    if not path.name.startswith("SOP_"):
        errors.append(f"CAP-SOP-001: File should start with 'SOP_', got: {path.name}")

    if not path.name.endswith(".md"):
        errors.append(f"CAP-SOP-001: File should end with '.md', got: {path.name}")

    # Check for proper snake_case after SOP_
    name_part = path.stem[4:] if path.stem.startswith("SOP_") else path.stem
    if name_part and not re.match(r"^[a-z][a-z0-9_]*$", name_part):
        errors.append(f"CAP-SOP-001: SOP name should be snake_case: {name_part}")

    return len(errors) == 0, errors


def validate_sop_header(content: str) -> Tuple[bool, List[str], Dict[str, str]]:
    """Validate SOP header fields.

    Returns:
        Tuple of (is_valid, errors, fields)
    """
    errors = []
    fields = {}

    lines = content.split("\n")

    for line in lines[:30]:  # Check first 30 lines for header
        match = HEADER_FIELD_PATTERN.match(line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()

    # Check required header fields
    if "Version" not in fields:
        errors.append("CAP-SOP-003: Missing Version field in header")

    if "Status" not in fields:
        errors.append("CAP-SOP-003: Missing Status field in header")

    return len(errors) == 0, errors, fields


def validate_sop_sections(content: str) -> Tuple[int, int, List[str]]:
    """Validate SOP has required sections.

    Returns:
        Tuple of (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    # Find all section headers (## level)
    section_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    sections = [m.group(1).strip() for m in section_pattern.finditer(content)]

    # Check required sections
    for required in REQUIRED_SECTIONS:
        found = any(required.lower() in s.lower() for s in sections)
        if found:
            passed += 1
        else:
            failed += 1
            errors.append(f"CAP-SOP-002: Missing required section: {required}")

    # Check for procedure/steps (at least one)
    has_procedure = any(
        s.lower() in ["procedure", "steps", "process", "workflow"]
        for s in sections
    )
    if has_procedure:
        passed += 1
    else:
        failed += 1
        errors.append("CAP-SOP-002: Missing Procedure/Steps section")

    return passed, failed, errors


def validate_procedure_steps(content: str) -> Tuple[bool, List[str]]:
    """Validate procedure steps are numbered.

    Returns:
        Tuple of (is_valid, warnings) - warnings only
    """
    warnings = []

    # Look for numbered lists in content
    numbered_pattern = re.compile(r"^\d+\.\s+", re.MULTILINE)
    numbered_steps = numbered_pattern.findall(content)

    if len(numbered_steps) < 3:
        warnings.append("CAP-SOP-004 (warning): SOP should have numbered procedure steps")

    return True, warnings  # Always passes, just warnings


def validate_sop_file(path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate a single SOP file.

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

    # Check 1: Naming convention
    is_valid, errors = validate_sop_naming(path)
    if is_valid:
        total_passed += 1
        if verbose:
            print(f"  [PASS] Naming convention")
    else:
        total_failed += 1
        issues["naming"] = errors
        if verbose:
            print(f"  [FAIL] Naming convention")
            for e in errors:
                print(f"    - {e}")

    # Check 2: Header fields
    is_valid, errors, fields = validate_sop_header(content)
    if is_valid:
        total_passed += 1
        if verbose:
            print(f"  [PASS] Header fields")
    else:
        total_failed += 1
        issues["header"] = errors
        if verbose:
            print(f"  [FAIL] Header fields")
            for e in errors:
                print(f"    - {e}")

    # Check 3: Required sections
    passed, failed, errors = validate_sop_sections(content)
    total_passed += passed
    total_failed += failed
    if errors:
        issues["sections"] = errors
    if verbose:
        print(f"  [{'PASS' if failed == 0 else 'FAIL'}] Sections: {passed}/{passed + failed}")
        for e in errors:
            print(f"    - {e}")

    # Check 4: Procedure steps (warning only)
    is_valid, warnings = validate_procedure_steps(content)
    total_passed += 1  # Always passes
    if warnings and verbose:
        print(f"  [WARN] {warnings[0]}")
    elif verbose:
        print(f"  [PASS] Procedure steps")

    return total_passed, total_failed, issues


def validate_sop_directory(path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, Dict[str, List[str]]]]:
    """Validate all SOP files in a directory.

    Returns:
        Tuple of (total_passed, total_failed, issues_by_file)
    """
    total_passed = 0
    total_failed = 0
    issues_by_file: Dict[str, Dict[str, List[str]]] = {}

    sop_files = list(path.glob("SOP_*.md"))

    if not sop_files:
        if verbose:
            print("No SOP files found")
        return 0, 0, {}

    for sop_file in sorted(sop_files):
        if verbose:
            print(f"\nValidating: {sop_file.name}")

        passed, failed, issues = validate_sop_file(sop_file, verbose)
        total_passed += passed
        total_failed += failed

        if issues:
            issues_by_file[sop_file.name] = issues

    return total_passed, total_failed, issues_by_file


def main():
    parser = argparse.ArgumentParser(
        description="Validate SOP format and structure"
    )
    parser.add_argument(
        "path",
        help="SOP file or directory to validate"
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

    if path.is_file():
        if args.verbose:
            print(f"Validating: {path.name}")
        passed, failed, issues = validate_sop_file(path, args.verbose)
        issues_by_file = {path.name: issues} if issues else {}
    else:
        passed, failed, issues_by_file = validate_sop_directory(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"SOP Compliance Validation Summary")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if issues_by_file:
        print(f"\nIssues:")
        for filename, issues in issues_by_file.items():
            print(f"\n  {filename}:")
            for check, errors in issues.items():
                for error in errors:
                    print(f"    - {error}")

    if failed > 0:
        print(f"\nFAIL: {failed} SOP compliance issues")
        sys.exit(1)
    else:
        print(f"\nPASS: All SOP compliance checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
