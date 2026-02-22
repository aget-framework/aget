#!/usr/bin/env python3
"""
validate_spec_header.py - Validate AGET specification headers

Validates that spec headers conform to AGET_SPEC_FORMAT v1.2 requirements.

Requirements Implemented:
- CAP-FMT-001: Spec headers SHALL have required fields
- CAP-FMT-002: Spec headers SHALL use standard date format (YYYY-MM-DD)
- CAP-FMT-003: Spec headers SHALL have valid Status value

Usage:
    python3 validate_spec_header.py <spec_path_or_directory>
    python3 validate_spec_header.py specs/AGET_TESTING_SPEC.md
    python3 validate_spec_header.py specs/  # Validate all specs in directory

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected

Author: aget-framework
Version: 1.0.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# Required header fields (per AGET_SPEC_FORMAT v1.2)
# Core fields are always required; extended fields required in strict mode
REQUIRED_FIELDS_CORE = [
    "Version",
    "Status",
]

REQUIRED_FIELDS_STRICT = [
    "Version",
    "Status",
    "Created",
    "Updated",
    "Author",
]

# Optional header fields
OPTIONAL_FIELDS = [
    "Spec ID",
    "Category",
    "Format Version",
    "Location",
    "Change Proposal",
    "Change Origin",
    "Implements",
    "Supersedes",
    "Related Specs",
    "Consolidates",
]

# Valid status values (including legacy values for backwards compatibility)
# Case-insensitive matching handled separately
VALID_STATUS = [
    "Draft", "Active", "Deprecated", "Archived",  # Standard
    "CANONICAL", "Approved", "Released",           # Legacy
    "ACTIVE", "DRAFT",                             # Case variants
]

# Date format pattern (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Version format pattern (X.Y.Z or X.Y.Z-prerelease)
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")


def parse_header(content: str) -> Tuple[Dict[str, str], List[str]]:
    """Parse spec header fields from markdown content.

    Returns:
        Tuple of (parsed_fields dict, errors list)
    """
    fields = {}
    errors = []

    lines = content.split("\n")
    in_header = False
    header_end = 0

    for i, line in enumerate(lines):
        # Title line
        if line.startswith("# "):
            in_header = True
            fields["Title"] = line[2:].strip()
            continue

        # Blank lines and separators in header
        if line.strip() == "" or line.strip() == "---":
            if in_header and i > 5:  # Past initial header block
                header_end = i
                break
            continue

        # Field lines (bold key: value)
        match = re.match(r"\*\*([^*]+)\*\*:\s*(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            fields[key] = value
        elif in_header and line.startswith("**"):
            # Malformed field
            errors.append(f"Malformed header field on line {i+1}: {line[:50]}")

    return fields, errors


def validate_required_fields(fields: Dict[str, str], strict: bool = False) -> List[str]:
    """Validate that all required fields are present."""
    errors = []
    required = REQUIRED_FIELDS_STRICT if strict else REQUIRED_FIELDS_CORE
    for field in required:
        if field not in fields:
            errors.append(f"Missing required field: {field}")
    return errors


def validate_field_values(fields: Dict[str, str]) -> List[str]:
    """Validate field values have correct format."""
    errors = []

    # Validate Status
    if "Status" in fields:
        status = fields["Status"]
        if status not in VALID_STATUS:
            errors.append(f"Invalid Status '{status}', must be one of: {VALID_STATUS}")

    # Validate Version
    if "Version" in fields:
        version = fields["Version"]
        if not VERSION_PATTERN.match(version):
            errors.append(f"Invalid Version format '{version}', expected X.Y.Z or X.Y.Z-prerelease")

    # Validate Created date
    if "Created" in fields:
        created = fields["Created"]
        if not DATE_PATTERN.match(created):
            errors.append(f"Invalid Created date '{created}', expected YYYY-MM-DD")

    # Validate Updated date
    if "Updated" in fields:
        updated = fields["Updated"]
        if not DATE_PATTERN.match(updated):
            errors.append(f"Invalid Updated date '{updated}', expected YYYY-MM-DD")

    # Validate Format Version if present
    if "Format Version" in fields:
        fv = fields["Format Version"]
        if not re.match(r"^\d+\.\d+$", fv):
            errors.append(f"Invalid Format Version '{fv}', expected X.Y")

    return errors


def validate_spec_file(path: Path, verbose: bool = False, strict: bool = False) -> Tuple[bool, List[str]]:
    """Validate a single spec file.

    Returns:
        Tuple of (is_valid, errors)
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    # Check if this looks like a spec file (has a markdown title)
    if not content.strip().startswith("#"):
        return True, []  # Skip non-spec files

    all_errors = []

    # Parse header
    fields, parse_errors = parse_header(content)
    all_errors.extend(parse_errors)

    # Validate required fields
    all_errors.extend(validate_required_fields(fields, strict))

    # Validate field values
    all_errors.extend(validate_field_values(fields))

    if verbose and fields:
        print(f"  Fields found: {list(fields.keys())}")

    return len(all_errors) == 0, all_errors


def validate_directory(directory: Path, verbose: bool = False, strict: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate all spec files in a directory.

    Returns:
        Tuple of (passed_count, failed_count, errors_by_file)
    """
    passed = 0
    failed = 0
    errors_by_file = {}

    # Find all .md files (excluding archive/, schemas/, etc.)
    spec_files = []
    for md_file in directory.glob("*.md"):
        spec_files.append(md_file)

    # Also check subdirectories (but not archive)
    for subdir in ["core", "governance", "lifecycle", "technical", "process", "format"]:
        subdir_path = directory / subdir
        if subdir_path.exists():
            for md_file in subdir_path.glob("*.md"):
                spec_files.append(md_file)

    for spec_file in sorted(spec_files):
        if verbose:
            print(f"Validating: {spec_file.name}")

        is_valid, errors = validate_spec_file(spec_file, verbose, strict)

        if is_valid:
            passed += 1
            if verbose:
                print(f"  [PASS]")
        else:
            failed += 1
            errors_by_file[str(spec_file)] = errors
            if verbose:
                print(f"  [FAIL]")
                for error in errors:
                    print(f"    - {error}")

    return passed, failed, errors_by_file


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET specification headers"
    )
    parser.add_argument(
        "path",
        help="Spec file or directory to validate"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed validation output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any warnings (not just errors)"
    )

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    if path.is_file():
        # Single file validation
        is_valid, errors = validate_spec_file(path, args.verbose, args.strict)

        if is_valid:
            print(f"PASS: {path.name}")
            sys.exit(0)
        else:
            print(f"FAIL: {path.name}")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    else:
        # Directory validation
        passed, failed, errors_by_file = validate_directory(path, args.verbose, args.strict)

        print(f"\n{'='*60}")
        print(f"Spec Header Validation Summary")
        print(f"{'='*60}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total:  {passed + failed}")

        if errors_by_file:
            print(f"\nFailures:")
            for file_path, errors in errors_by_file.items():
                print(f"\n  {Path(file_path).name}:")
                for error in errors:
                    print(f"    - {error}")

        if failed > 0:
            sys.exit(1)
        else:
            print(f"\nAll specs pass header validation.")
            sys.exit(0)


if __name__ == "__main__":
    main()
