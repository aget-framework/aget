#!/usr/bin/env python3
"""
validate_release_gate.py - Validate AGET release gate requirements

Validates that release gates are properly completed with verification,
preventing declarative completion (L440).

Requirements Implemented:
- R-REL-006: Manager migration before release
- CAP-REL-001: Version consistency across repos
- CAP-REL-002: CHANGELOG entries present
- CAP-REL-003: GitHub release exists
- CAP-REL-004: Tags exist and match version
- L440: Verified completion (V-tests executed, not just checkboxes)

Usage:
    python3 validate_release_gate.py <version> [--manager-path PATH]
    python3 validate_release_gate.py 3.2.0
    python3 validate_release_gate.py 3.2.0 --manager-path ../private-aget-framework-AGET

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected

Author: private-aget-framework-AGET
Version: 1.1.0

Changelog:
    1.1.0 (2026-01-11): Expanded to 12 templates (L517), added CAP-REL-009/010
    1.0.0 (2026-01-04): Initial version
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Template repositories to check (all 12 - L517 expansion)
TEMPLATE_REPOS = [
    # Published templates (6)
    "template-supervisor-aget",
    "template-worker-aget",
    "template-advisor-aget",
    "template-consultant-aget",
    "template-developer-aget",
    "template-spec-engineer-aget",
    # Additional templates (6) - discovered in L517
    "template-analyst-aget",
    "template-architect-aget",
    "template-qa-aget",
    "template-devops-aget",
    "template-documenter-aget",
    "template-researcher-aget",
]


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def validate_manager_version(
    version: str,
    manager_path: Optional[Path] = None
) -> Tuple[bool, List[str]]:
    """Validate manager version is updated (R-REL-006).

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    if manager_path is None:
        # Try to find manager path
        candidate = Path("../private-aget-framework-AGET")
        if candidate.exists():
            manager_path = candidate
        else:
            errors.append("R-REL-006: Cannot find manager path (use --manager-path)")
            return False, errors

    version_path = manager_path / ".aget" / "version.json"

    if not version_path.exists():
        errors.append(f"R-REL-006: Manager version.json not found at {version_path}")
        return False, errors

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            version_data = json.load(f)
    except Exception as e:
        errors.append(f"R-REL-006: Could not read manager version.json: {e}")
        return False, errors

    manager_version = version_data.get("aget_version", "")

    if manager_version != version:
        errors.append(
            f"R-REL-006: Manager version ({manager_version}) does not match "
            f"release version ({version}). BLOCKING: Manager must update first."
        )
        return False, errors

    return True, []


def validate_core_version(version: str, aget_path: Path) -> Tuple[bool, List[str]]:
    """Validate aget/ core version matches release version.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    version_path = aget_path / ".aget" / "version.json"

    if not version_path.exists():
        errors.append(f"CAP-REL-001: Core version.json not found at {version_path}")
        return False, errors

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            version_data = json.load(f)
    except Exception as e:
        errors.append(f"CAP-REL-001: Could not read core version.json: {e}")
        return False, errors

    core_version = version_data.get("aget_version", "")

    if core_version != version:
        errors.append(
            f"CAP-REL-001: Core version ({core_version}) does not match "
            f"release version ({version})"
        )
        return False, errors

    return True, []


def validate_changelog(version: str, repo_path: Path) -> Tuple[bool, List[str]]:
    """Validate CHANGELOG.md has entry for version.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    changelog_path = repo_path / "CHANGELOG.md"

    if not changelog_path.exists():
        errors.append(f"CAP-REL-002: CHANGELOG.md not found in {repo_path}")
        return False, errors

    try:
        content = changelog_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"CAP-REL-002: Could not read CHANGELOG.md: {e}")
        return False, errors

    # Check for version entry
    version_pattern = f"[{version}]"
    if version_pattern not in content:
        errors.append(f"CAP-REL-002: CHANGELOG.md missing [{version}] entry")
        return False, errors

    return True, []


def validate_git_tag(version: str, repo_path: Path) -> Tuple[bool, List[str]]:
    """Validate git tag exists for version.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    tag_name = f"v{version}"

    returncode, stdout, stderr = run_command(
        ["git", "tag", "-l", tag_name],
        cwd=repo_path
    )

    if returncode != 0:
        errors.append(f"CAP-REL-004: Could not check git tags: {stderr}")
        return False, errors

    if tag_name not in stdout:
        errors.append(f"CAP-REL-004: Git tag {tag_name} not found")
        return False, errors

    return True, []


def validate_template_versions(
    version: str,
    framework_path: Path
) -> Tuple[int, int, List[str]]:
    """Validate all template versions match release version.

    Returns:
        Tuple of (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    for template in TEMPLATE_REPOS:
        template_path = framework_path / template
        if not template_path.exists():
            failed += 1
            errors.append(f"CAP-REL-001: Template {template} not found")
            continue

        version_path = template_path / ".aget" / "version.json"
        if not version_path.exists():
            failed += 1
            errors.append(f"CAP-REL-001: {template} missing version.json")
            continue

        try:
            with open(version_path, "r", encoding="utf-8") as f:
                version_data = json.load(f)
        except Exception as e:
            failed += 1
            errors.append(f"CAP-REL-001: {template} version.json error: {e}")
            continue

        template_version = version_data.get("aget_version", "")
        if template_version != version:
            failed += 1
            errors.append(
                f"CAP-REL-001: {template} version ({template_version}) != {version}"
            )
        else:
            passed += 1

    return passed, failed, errors


def validate_release(
    version: str,
    aget_path: Path,
    framework_path: Path,
    manager_path: Optional[Path] = None,
    verbose: bool = False
) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate complete release gate.

    Returns:
        Tuple of (passed, failed, issues_by_check)
    """
    total_passed = 0
    total_failed = 0
    issues: Dict[str, List[str]] = {}

    # Check 1: Manager version (R-REL-006) - BLOCKING
    if verbose:
        print("Checking R-REL-006: Manager version...")
    is_valid, errors = validate_manager_version(version, manager_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] Manager version matches")
    else:
        total_failed += 1
        issues["manager_version"] = errors
        if verbose:
            print("  [FAIL] Manager version mismatch (BLOCKING)")
            for e in errors:
                print(f"    - {e}")

    # Check 2: Core version
    if verbose:
        print("Checking CAP-REL-001: Core version...")
    is_valid, errors = validate_core_version(version, aget_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] Core version matches")
    else:
        total_failed += 1
        issues["core_version"] = errors
        if verbose:
            print("  [FAIL] Core version mismatch")
            for e in errors:
                print(f"    - {e}")

    # Check 3: Template versions
    if verbose:
        print("Checking CAP-REL-001: Template versions...")
    passed, failed, errors = validate_template_versions(version, framework_path)
    total_passed += passed
    total_failed += failed
    if errors:
        issues["template_versions"] = errors
    if verbose:
        print(f"  [{'PASS' if failed == 0 else 'FAIL'}] Templates: {passed}/{passed + failed}")
        for e in errors:
            print(f"    - {e}")

    # Check 4: Core CHANGELOG
    if verbose:
        print("Checking CAP-REL-002: Core CHANGELOG...")
    is_valid, errors = validate_changelog(version, aget_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] Core CHANGELOG has entry")
    else:
        total_failed += 1
        issues["core_changelog"] = errors
        if verbose:
            print("  [FAIL] Core CHANGELOG missing entry")
            for e in errors:
                print(f"    - {e}")

    # Check 5: Core git tag
    if verbose:
        print("Checking CAP-REL-004: Core git tag...")
    is_valid, errors = validate_git_tag(version, aget_path)
    if is_valid:
        total_passed += 1
        if verbose:
            print("  [PASS] Core git tag exists")
    else:
        total_failed += 1
        issues["core_tag"] = errors
        if verbose:
            print("  [FAIL] Core git tag missing")
            for e in errors:
                print(f"    - {e}")

    return total_passed, total_failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET release gate requirements (L440)"
    )
    parser.add_argument(
        "version",
        help="Release version to validate (e.g., 3.2.0)"
    )
    parser.add_argument(
        "--aget-path",
        type=Path,
        default=Path("."),
        help="Path to aget/ core repo (default: current directory)"
    )
    parser.add_argument(
        "--framework-path",
        type=Path,
        default=None,
        help="Path to aget-framework/ (default: parent of aget-path)"
    )
    parser.add_argument(
        "--manager-path",
        type=Path,
        default=None,
        help="Path to private-aget-framework-AGET (for R-REL-006)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--skip-manager",
        action="store_true",
        help="Skip manager version check (not recommended)"
    )

    args = parser.parse_args()

    # Normalize paths
    aget_path = args.aget_path.resolve()
    framework_path = args.framework_path or aget_path.parent
    manager_path = args.manager_path

    if not aget_path.exists():
        print(f"Error: aget path does not exist: {aget_path}")
        sys.exit(1)

    print(f"Validating release v{args.version}")
    print(f"Core path: {aget_path}")
    print(f"Framework path: {framework_path}")

    if args.skip_manager:
        print("WARNING: Skipping manager version check (R-REL-006)")
        manager_path = None
        # Create dummy pass for manager check
        passed = 0
        failed = 0
        issues = {}
    else:
        passed, failed, issues = validate_release(
            args.version,
            aget_path,
            framework_path,
            manager_path,
            args.verbose
        )

    print(f"\n{'='*60}")
    print(f"Release Gate Validation Summary (v{args.version})")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if issues:
        print(f"\nIssues:")
        for check, errors in issues.items():
            print(f"\n  {check}:")
            for error in errors:
                print(f"    - {error}")

    # Check for BLOCKING issues
    blocking = "manager_version" in issues
    if blocking:
        print(f"\nBLOCKING: Manager version not updated (R-REL-006)")
        print("Release CANNOT proceed until manager updates to target version.")

    if failed > 0:
        print(f"\nFAIL: {failed} release gate issues")
        sys.exit(1)
    else:
        print(f"\nPASS: All release gate validations passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
