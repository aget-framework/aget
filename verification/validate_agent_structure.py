#!/usr/bin/env python3
"""
validate_agent_structure.py - Validate AGET agent directory structure

Validates that agent repositories follow the AGET directory structure requirements.

Requirements Implemented:
- CAP-STRUCT-001: .aget/ directory must exist
- CAP-STRUCT-002: Required subdirectories (persona, memory, reasoning, skills, context)
- CAP-STRUCT-003: identity.json must exist
- CAP-STRUCT-004: version.json must exist
- CAP-STRUCT-005: evolution/ directory with index.json

Usage:
    python3 validate_agent_structure.py <agent_path>
    python3 validate_agent_structure.py /path/to/template-advisor-aget
    python3 validate_agent_structure.py .

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected

Author: aget-framework
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Required directories in .aget/
REQUIRED_DIRS = [
    "persona",
    "memory",
    "reasoning",
    "skills",
    "context",
    "evolution",
]

# Required files in .aget/
REQUIRED_FILES = [
    "identity.json",
    "version.json",
]

# Optional but recommended files
RECOMMENDED_FILES = [
    "evolution/index.json",
]


def validate_aget_directory(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate .aget/ directory exists.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    aget_path = agent_path / ".aget"

    if not aget_path.exists():
        errors.append("CAP-STRUCT-001: .aget/ directory missing")
        return False, errors

    if not aget_path.is_dir():
        errors.append("CAP-STRUCT-001: .aget exists but is not a directory")
        return False, errors

    return True, []


def validate_required_dirs(agent_path: Path) -> Tuple[int, int, List[str]]:
    """Validate required subdirectories in .aget/.

    Returns:
        Tuple of (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []
    aget_path = agent_path / ".aget"

    for dir_name in REQUIRED_DIRS:
        dir_path = aget_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            passed += 1
        else:
            failed += 1
            errors.append(f"CAP-STRUCT-002: .aget/{dir_name}/ directory missing")

    return passed, failed, errors


def validate_required_files(agent_path: Path) -> Tuple[int, int, List[str]]:
    """Validate required files in .aget/.

    Returns:
        Tuple of (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []
    aget_path = agent_path / ".aget"

    for file_name in REQUIRED_FILES:
        file_path = aget_path / file_name
        if file_path.exists() and file_path.is_file():
            passed += 1
        else:
            failed += 1
            cap_id = "CAP-STRUCT-003" if file_name == "identity.json" else "CAP-STRUCT-004"
            errors.append(f"{cap_id}: .aget/{file_name} missing")

    return passed, failed, errors


def validate_identity_json(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate identity.json content.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    identity_path = agent_path / ".aget" / "identity.json"

    if not identity_path.exists():
        return True, []  # Already caught by validate_required_files

    try:
        with open(identity_path, "r", encoding="utf-8") as f:
            identity = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"CAP-STRUCT-003: identity.json invalid JSON: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"CAP-STRUCT-003: Could not read identity.json: {e}")
        return False, errors

    # Check required fields
    required_fields = ["name", "purpose"]
    for field in required_fields:
        if field not in identity:
            errors.append(f"CAP-STRUCT-003: identity.json missing required field: {field}")

    return len(errors) == 0, errors


def validate_version_json(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate version.json content.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    version_path = agent_path / ".aget" / "version.json"

    if not version_path.exists():
        return True, []  # Already caught by validate_required_files

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            version = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"CAP-STRUCT-004: version.json invalid JSON: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"CAP-STRUCT-004: Could not read version.json: {e}")
        return False, errors

    # Check required fields
    required_fields = ["aget_version"]
    for field in required_fields:
        if field not in version:
            errors.append(f"CAP-STRUCT-004: version.json missing required field: {field}")

    return len(errors) == 0, errors


def validate_evolution_index(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate evolution/index.json exists and is valid.

    Returns:
        Tuple of (is_valid, warnings) - warnings only
    """
    warnings = []
    index_path = agent_path / ".aget" / "evolution" / "index.json"

    if not index_path.exists():
        warnings.append("CAP-STRUCT-005 (warning): evolution/index.json missing")
        return True, warnings

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)

        if not isinstance(index, dict):
            warnings.append("CAP-STRUCT-005 (warning): evolution/index.json should be a JSON object")
    except json.JSONDecodeError:
        warnings.append("CAP-STRUCT-005 (warning): evolution/index.json is not valid JSON")
    except Exception:
        pass

    return True, warnings  # Warnings only


def validate_agent(agent_path: Path, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate agent directory structure.

    Returns:
        Tuple of (passed, failed, issues_by_check)
    """
    total_passed = 0
    total_failed = 0
    issues: Dict[str, List[str]] = {}

    # Check 1: .aget/ directory
    is_valid, errors = validate_aget_directory(agent_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] .aget/ directory exists")
    else:
        total_failed += 1
        issues["aget_directory"] = errors
        if verbose:
            print("  [FAIL] .aget/ directory missing")
        # Can't continue without .aget/
        return total_passed, total_failed, issues

    # Check 2: Required directories
    passed, failed, errors = validate_required_dirs(agent_path)
    total_passed += passed
    total_failed += failed
    if errors:
        issues["required_dirs"] = errors
    if verbose:
        print(f"  [{'PASS' if failed == 0 else 'FAIL'}] Required directories: {passed}/{passed + failed}")
        for e in errors:
            print(f"    - {e}")

    # Check 3: Required files
    passed, failed, errors = validate_required_files(agent_path)
    total_passed += passed
    total_failed += failed
    if errors:
        issues["required_files"] = errors
    if verbose:
        print(f"  [{'PASS' if failed == 0 else 'FAIL'}] Required files: {passed}/{passed + failed}")
        for e in errors:
            print(f"    - {e}")

    # Check 4: identity.json content
    is_valid, errors = validate_identity_json(agent_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] identity.json valid")
    else:
        total_failed += 1
        issues["identity_json"] = errors
        if verbose:
            print("  [FAIL] identity.json issues")
            for e in errors:
                print(f"    - {e}")

    # Check 5: version.json content
    is_valid, errors = validate_version_json(agent_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] version.json valid")
    else:
        total_failed += 1
        issues["version_json"] = errors
        if verbose:
            print("  [FAIL] version.json issues")
            for e in errors:
                print(f"    - {e}")

    # Check 6: evolution/index.json (warning only)
    is_valid, warnings = validate_evolution_index(agent_path)
    total_passed += 1  # Always passes
    if warnings and verbose:
        print(f"  [WARN] {warnings[0]}")
    elif verbose:
        print("  [PASS] evolution/index.json exists")

    return total_passed, total_failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET agent directory structure"
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

    passed, failed, issues = validate_agent(path, args.verbose)

    print(f"\n{'='*60}")
    print(f"Agent Structure Validation Summary")
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
        print(f"\nFAIL: {failed} structure validation issues")
        sys.exit(1)
    else:
        print(f"\nPASS: All structure validations passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
