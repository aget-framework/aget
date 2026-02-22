#!/usr/bin/env python3
"""
validate_ldoc_index.py - Validate L-doc index consistency

Validates that the evolution/index.json is consistent with L-doc files.

Requirements Implemented:
- CAP-MEMORY-008: L-doc Index shall exist and be maintained
- L-docs in index should have corresponding files
- L-doc files should be registered in index

Usage:
    python3 validate_ldoc_index.py <agent_path>
    python3 validate_ldoc_index.py /path/to/template-advisor-aget
    python3 validate_ldoc_index.py .

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected

Author: aget-framework
Version: 1.0.0
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set


# L-doc filename pattern
LDOC_PATTERN = re.compile(r"^L(\d+)_.*\.md$")


def find_ldoc_files(evolution_path: Path) -> Set[str]:
    """Find all L-doc files in evolution directory.

    Returns:
        Set of L-doc IDs (e.g., {"L001", "L042", "L335"})
    """
    ldocs = set()

    if not evolution_path.exists():
        return ldocs

    for md_file in evolution_path.glob("L*.md"):
        match = LDOC_PATTERN.match(md_file.name)
        if match:
            ldoc_id = f"L{match.group(1)}"
            ldocs.add(ldoc_id)

    return ldocs


def parse_index_ldocs(index_path: Path) -> Tuple[Set[str], List[str]]:
    """Parse L-doc index and extract registered L-docs.

    Returns:
        Tuple of (ldoc_ids, errors)
    """
    ldocs = set()
    errors = []

    if not index_path.exists():
        errors.append("CAP-MEMORY-008: evolution/index.json not found")
        return ldocs, errors

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"CAP-MEMORY-008: index.json invalid JSON: {e}")
        return ldocs, errors
    except Exception as e:
        errors.append(f"CAP-MEMORY-008: Could not read index.json: {e}")
        return ldocs, errors

    # Extract L-doc IDs from index
    # Support multiple index formats
    if isinstance(index, dict):
        # Format 1: {"L001": {...}, "L002": {...}}
        for key in index.keys():
            if key.startswith("L") and key[1:].isdigit():
                ldocs.add(key)

        # Format 2: {"learnings": [{"id": "L001"}, ...]}
        if "learnings" in index and isinstance(index["learnings"], list):
            for entry in index["learnings"]:
                if isinstance(entry, dict) and "id" in entry:
                    ldocs.add(entry["id"])

        # Format 3: {"entries": {"L001": {...}}}
        if "entries" in index and isinstance(index["entries"], dict):
            for key in index["entries"].keys():
                if key.startswith("L") and key[1:].isdigit():
                    ldocs.add(key)

    return ldocs, errors


def validate_ldoc_index(agent_path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate L-doc index consistency.

    Returns:
        Tuple of (passed, failed, issues)
    """
    total_passed = 0
    total_failed = 0
    issues: Dict[str, List[str]] = {}

    evolution_path = agent_path / ".aget" / "evolution"
    index_path = evolution_path / "index.json"

    # Check 1: index.json exists
    if not index_path.exists():
        total_failed += 1
        issues["index_exists"] = ["CAP-MEMORY-008: evolution/index.json not found"]
        if verbose:
            print("  [FAIL] evolution/index.json not found")
        return total_passed, total_failed, issues
    else:
        total_passed += 1
        if verbose:
            print("  [PASS] evolution/index.json exists")

    # Get L-docs from files
    file_ldocs = find_ldoc_files(evolution_path)

    # Get L-docs from index
    index_ldocs, parse_errors = parse_index_ldocs(index_path)

    if parse_errors:
        total_failed += 1
        issues["index_parse"] = parse_errors
        if verbose:
            print("  [FAIL] Index parse errors")
            for e in parse_errors:
                print(f"    - {e}")
        return total_passed, total_failed, issues
    else:
        total_passed += 1
        if verbose:
            print(f"  [PASS] Index parsed ({len(index_ldocs)} entries)")

    # Check 2: Files not in index
    orphan_files = file_ldocs - index_ldocs
    if orphan_files:
        total_failed += 1
        orphan_errors = [f"L-doc file not in index: {ldoc}" for ldoc in sorted(orphan_files)]
        issues["orphan_files"] = orphan_errors
        if verbose:
            print(f"  [FAIL] {len(orphan_files)} L-doc files not in index")
            for e in orphan_errors[:5]:  # Show first 5
                print(f"    - {e}")
            if len(orphan_errors) > 5:
                print(f"    ... and {len(orphan_errors) - 5} more")
    else:
        total_passed += 1
        if verbose:
            print("  [PASS] All L-doc files are in index")

    # Check 3: Index entries without files (warning only)
    missing_files = index_ldocs - file_ldocs
    if missing_files:
        # This is a warning, not a failure - some L-docs may be inherited
        if verbose:
            print(f"  [WARN] {len(missing_files)} index entries without files (may be inherited)")
            for ldoc in sorted(list(missing_files)[:5]):
                print(f"    - {ldoc}")
    else:
        if verbose:
            print("  [PASS] All index entries have files")

    total_passed += 1  # Warning check always passes

    return total_passed, total_failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate L-doc index consistency"
    )
    parser.add_argument(
        "path",
        help="Agent repository path to validate"
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

    passed, failed, issues = validate_ldoc_index(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"L-doc Index Validation Summary")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if issues:
        print(f"\nIssues:")
        for check, errors in issues.items():
            print(f"\n  {check}:")
            for error in errors[:10]:
                print(f"    - {error}")
            if len(errors) > 10:
                print(f"    ... and {len(errors) - 10} more")

    if failed > 0:
        print(f"\nFAIL: {failed} L-doc index issues")
        sys.exit(1)
    else:
        print(f"\nPASS: L-doc index is consistent")
        sys.exit(0)


if __name__ == "__main__":
    main()
