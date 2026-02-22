#!/usr/bin/env python3
"""
validate_spec_cross_refs.py - Validate cross-references between AGET specs

Validates that spec cross-references point to existing files.

Requirements Implemented:
- All referenced specs should exist
- All referenced validators should exist (or be marked planned)
- Broken references should be reported

Usage:
    python3 validate_spec_cross_refs.py <specs_directory>
    python3 validate_spec_cross_refs.py specs/
    python3 validate_spec_cross_refs.py specs/ --strict

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
from typing import List, Dict, Set, Tuple


# Pattern to match spec references like AGET_*_SPEC.md or AGET_*.md
SPEC_REF_PATTERN = re.compile(r'AGET_[A-Z_]+(?:_SPEC)?\.md')

# Pattern to match validator references like validate_*.py
VALIDATOR_REF_PATTERN = re.compile(r'validate_[a-z_]+\.py')

# Pattern to match spec ID references like AGET-XXX-NNN
SPEC_ID_PATTERN = re.compile(r'AGET-[A-Z]+-\d{3}')


def find_references(content: str, pattern: re.Pattern) -> Set[str]:
    """Find all references matching a pattern in content."""
    return set(pattern.findall(content))


def validate_spec_references(
    specs_dir: Path,
    verbose: bool = False
) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate cross-references in all specs.

    Returns:
        Tuple of (valid_count, broken_count, broken_by_file)
    """
    valid = 0
    broken = 0
    broken_by_file: Dict[str, List[str]] = {}

    # Get all existing spec files
    existing_specs = set()
    for md_file in specs_dir.glob("*.md"):
        existing_specs.add(md_file.name)
    for md_file in specs_dir.glob("**/*.md"):
        if "archive" not in str(md_file):
            existing_specs.add(md_file.name)

    # Get all existing validators
    validation_dir = specs_dir.parent / "validation"
    existing_validators = set()
    if validation_dir.exists():
        for py_file in validation_dir.glob("validate_*.py"):
            existing_validators.add(py_file.name)

    # Check each spec file
    for spec_file in sorted(specs_dir.glob("*.md")):
        try:
            content = spec_file.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print(f"Error reading {spec_file.name}: {e}")
            continue

        file_broken = []

        # Check spec references
        spec_refs = find_references(content, SPEC_REF_PATTERN)
        for ref in spec_refs:
            if ref != spec_file.name and ref not in existing_specs:
                # Check if it's in archive
                archive_path = specs_dir / "archive" / ref
                if not archive_path.exists():
                    file_broken.append(f"Spec: {ref}")

        # Check validator references (only warn, don't fail)
        validator_refs = find_references(content, VALIDATOR_REF_PATTERN)
        for ref in validator_refs:
            if ref not in existing_validators:
                # Check if marked as planned
                if "(planned)" not in content.lower() and "(Planned)" not in content:
                    file_broken.append(f"Validator (planned?): {ref}")

        if file_broken:
            broken += len(file_broken)
            broken_by_file[spec_file.name] = file_broken
        else:
            valid += 1

        if verbose:
            status = "BROKEN" if file_broken else "OK"
            print(f"  {spec_file.name}: {status}")
            for issue in file_broken:
                print(f"    - {issue}")

    return valid, broken, broken_by_file


def main():
    parser = argparse.ArgumentParser(
        description="Validate cross-references between AGET specifications"
    )
    parser.add_argument(
        "path",
        help="Specs directory to validate"
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

    valid, broken, broken_by_file = validate_spec_references(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"Spec Cross-Reference Validation Summary")
    print(f"{'='*60}")
    print(f"Specs validated: {valid + len(broken_by_file)}")
    print(f"Broken references: {broken}")

    if broken_by_file:
        print(f"\nFiles with issues:")
        for file_name, issues in sorted(broken_by_file.items()):
            print(f"\n  {file_name}:")
            for issue in issues:
                print(f"    - {issue}")

    # Only fail in strict mode or if there are actual broken spec refs
    actual_broken = sum(
        1 for issues in broken_by_file.values()
        for issue in issues
        if issue.startswith("Spec:")
    )

    if actual_broken > 0:
        print(f"\nFAIL: {actual_broken} broken spec references")
        sys.exit(1)
    elif args.strict and broken > 0:
        print(f"\nFAIL (strict): {broken} issues detected")
        sys.exit(1)
    else:
        print(f"\nPASS: No broken spec references")
        sys.exit(0)


if __name__ == "__main__":
    main()
