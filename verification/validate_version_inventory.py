#!/usr/bin/env python3
"""
validate_version_inventory.py - Validate version coherence across all version-bearing files

Implements L444 (Version Inventory Coherence Requirement) and R-REL-VER-001.

This validator performs COHERENCE testing (not just existence testing per L421).
All version-bearing files must have consistent versions, with version.json as PRIMARY.

Version-Bearing Files Inventory (R-REL-VER-001):
- .aget/version.json: aget_version field (PRIMARY source of truth)
- AGENTS.md: @aget-version tag
- manifest.yaml: template.version field
- README.md: **Current Version**: vX.Y.Z pattern (L521 gap fix)
- CHANGELOG.md: [X.Y.Z] entry must exist

Requirements Implemented:
- R-REL-VER-001: Version inventory coherence
- V7.1.4: AGENTS.md header version check
- V7.1.5: manifest.yaml version field check
- V7.1.6: No stale version references check

Usage:
    python3 validate_version_inventory.py <repo_path>
    python3 validate_version_inventory.py /path/to/template-supervisor-aget
    python3 validate_version_inventory.py . --check-stale 3.1.0

Exit Codes:
    0 - All validations passed (coherence verified)
    1 - Validation failures detected (version mismatch)

Author: private-aget-framework-AGET
Version: 1.1.0
Created: 2026-01-04
Updated: 2026-01-12
Related: L444, L421, L429, L521, R-REL-VER-001
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import yaml


def extract_version_json(repo_path: Path) -> Tuple[Optional[str], List[str]]:
    """Extract aget_version from version.json (PRIMARY source of truth).

    Returns:
        Tuple of (version_string, errors)
    """
    errors = []
    version_json_path = repo_path / ".aget" / "version.json"

    if not version_json_path.exists():
        errors.append("R-REL-VER-001: .aget/version.json does not exist")
        return None, errors

    try:
        data = json.loads(version_json_path.read_text(encoding="utf-8"))
        version = data.get("aget_version")
        if not version:
            errors.append("R-REL-VER-001: 'aget_version' field missing in version.json")
            return None, errors
        return version, errors
    except json.JSONDecodeError as e:
        errors.append(f"R-REL-VER-001: Invalid JSON in version.json: {e}")
        return None, errors


def extract_agents_md_version(repo_path: Path) -> Tuple[Optional[str], List[str]]:
    """Extract @aget-version from AGENTS.md.

    Returns:
        Tuple of (version_string, errors)
    """
    errors = []
    agents_md_path = repo_path / "AGENTS.md"

    if not agents_md_path.exists():
        errors.append("V7.1.4: AGENTS.md does not exist")
        return None, errors

    try:
        content = agents_md_path.read_text(encoding="utf-8")
        # Match @aget-version: X.Y.Z or @aget-version: X.Y.Z-beta.N
        match = re.search(r'@aget-version:\s*([\d.]+(?:-[a-zA-Z0-9.]+)?)', content)
        if match:
            return match.group(1), errors
        else:
            errors.append("V7.1.4: @aget-version tag not found in AGENTS.md")
            return None, errors
    except Exception as e:
        errors.append(f"V7.1.4: Could not read AGENTS.md: {e}")
        return None, errors


def extract_manifest_version(repo_path: Path) -> Tuple[Optional[str], List[str]]:
    """Extract version from manifest.yaml template.version field.

    Returns:
        Tuple of (version_string, errors)
    """
    errors = []
    manifest_path = repo_path / "manifest.yaml"

    if not manifest_path.exists():
        # manifest.yaml is optional for core aget/ repo
        return None, []

    try:
        content = manifest_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        # Try template.version first (v3.0 format)
        if isinstance(data, dict):
            template = data.get("template", {})
            if isinstance(template, dict):
                version = template.get("version")
                if version:
                    return str(version), errors

        # Fallback to top-level version
        version = data.get("version") if isinstance(data, dict) else None
        if version:
            return str(version), errors

        errors.append("V7.1.5: 'version' field not found in manifest.yaml")
        return None, errors
    except yaml.YAMLError as e:
        errors.append(f"V7.1.5: Invalid YAML in manifest.yaml: {e}")
        return None, errors
    except Exception as e:
        errors.append(f"V7.1.5: Could not read manifest.yaml: {e}")
        return None, errors


def extract_readme_version(repo_path: Path) -> Tuple[Optional[str], List[str]]:
    """Extract version from README.md **Current Version**: vX.Y.Z pattern.

    L521 gap fix: README.md was not previously checked, allowing version drift.

    Returns:
        Tuple of (version_string, errors)
    """
    errors = []
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        # README.md should exist but version line is optional for some repos
        return None, []

    try:
        content = readme_path.read_text(encoding="utf-8")
        # Match **Current Version**: vX.Y.Z or variations
        # Patterns: "**Current Version**: vX.Y.Z", "Current Version: vX.Y.Z", "Version: vX.Y.Z"
        patterns = [
            r'\*\*Current Version\*\*:\s*v?([\d.]+(?:-[a-zA-Z0-9.]+)?)',  # **Current Version**: vX.Y.Z
            r'Current Version:\s*v?([\d.]+(?:-[a-zA-Z0-9.]+)?)',  # Current Version: vX.Y.Z
            r'- Current Version:\s*v?([\d.]+(?:-[a-zA-Z0-9.]+)?)',  # - Current Version: vX.Y.Z
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1), errors

        # No version pattern found - this is OK for some repos
        return None, []
    except Exception as e:
        errors.append(f"L521: Could not read README.md: {e}")
        return None, errors


def check_changelog_entry(repo_path: Path, version: str) -> Tuple[bool, List[str]]:
    """Check if CHANGELOG.md has entry for specified version.

    Returns:
        Tuple of (has_entry, errors)
    """
    errors = []
    changelog_path = repo_path / "CHANGELOG.md"

    if not changelog_path.exists():
        errors.append(f"CHANGELOG.md does not exist")
        return False, errors

    try:
        content = changelog_path.read_text(encoding="utf-8")
        # Look for ## [X.Y.Z] pattern
        pattern = rf"\[{re.escape(version)}\]"
        if re.search(pattern, content):
            return True, errors
        else:
            errors.append(f"CHANGELOG.md missing entry for [{version}]")
            return False, errors
    except Exception as e:
        errors.append(f"Could not read CHANGELOG.md: {e}")
        return False, errors


def check_stale_references(repo_path: Path, old_version: str) -> Tuple[int, List[str]]:
    """Check for stale version references (excluding CHANGELOG history).

    Returns:
        Tuple of (stale_count, file_list)
    """
    stale_files = []
    extensions = [".md", ".yaml", ".yml", ".json"]

    for ext in extensions:
        for filepath in repo_path.rglob(f"*{ext}"):
            # Skip CHANGELOG (legitimately contains history)
            if filepath.name == "CHANGELOG.md":
                continue
            # Skip hidden directories except .aget
            rel_path = filepath.relative_to(repo_path)
            parts = rel_path.parts
            skip = False
            for part in parts[:-1]:  # Check all but filename
                if part.startswith(".") and part != ".aget":
                    skip = True
                    break
            if skip:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                # Check for old version patterns
                if f"v{old_version}" in content or f"version: {old_version}" in content:
                    stale_files.append(str(rel_path))
            except Exception:
                pass  # Skip unreadable files

    return len(stale_files), stale_files


def validate_coherence(repo_path: Path, check_stale: Optional[str] = None, verbose: bool = False) -> Tuple[int, int, Dict[str, List[str]]]:
    """Validate version coherence across all version-bearing files.

    Returns:
        Tuple of (passed, failed, issues_by_check)
    """
    passed = 0
    failed = 0
    issues: Dict[str, List[str]] = {}

    # Step 1: Extract PRIMARY version from version.json
    primary_version, errors = extract_version_json(repo_path)
    if errors:
        failed += 1
        issues["version_json"] = errors
        if verbose:
            print("  [FAIL] version.json")
            for e in errors:
                print(f"    - {e}")
    else:
        passed += 1
        if verbose:
            print(f"  [PASS] version.json: {primary_version} (PRIMARY)")

    if not primary_version:
        # Cannot continue without primary version
        return passed, failed, issues

    # Step 2: Check AGENTS.md @aget-version (V7.1.4)
    # Note: AGENTS.md is optional for core framework repos (aget/)
    agents_version, errors = extract_agents_md_version(repo_path)
    agents_md_exists = (repo_path / "AGENTS.md").exists()
    if not agents_md_exists:
        # AGENTS.md is optional for core repos
        passed += 1
        if verbose:
            print("  [PASS] AGENTS.md: not applicable (core repo)")
    elif errors:
        failed += 1
        issues["agents_md"] = errors
        if verbose:
            print("  [FAIL] AGENTS.md")
            for e in errors:
                print(f"    - {e}")
    elif agents_version != primary_version:
        failed += 1
        issues["agents_md"] = [
            f"V7.1.4: AGENTS.md has @aget-version: {agents_version} but version.json has {primary_version}"
        ]
        if verbose:
            print(f"  [FAIL] AGENTS.md: {agents_version} != {primary_version}")
    else:
        passed += 1
        if verbose:
            print(f"  [PASS] AGENTS.md: @aget-version: {agents_version}")

    # Step 3: Check manifest.yaml version (V7.1.5)
    manifest_version, errors = extract_manifest_version(repo_path)
    if errors:
        failed += 1
        issues["manifest_yaml"] = errors
        if verbose:
            print("  [FAIL] manifest.yaml")
            for e in errors:
                print(f"    - {e}")
    elif manifest_version is None:
        # manifest.yaml doesn't exist or has no version - OK for core repo
        passed += 1
        if verbose:
            print("  [PASS] manifest.yaml: not applicable")
    elif manifest_version != primary_version:
        failed += 1
        issues["manifest_yaml"] = [
            f"V7.1.5: manifest.yaml has version: {manifest_version} but version.json has {primary_version}"
        ]
        if verbose:
            print(f"  [FAIL] manifest.yaml: {manifest_version} != {primary_version}")
    else:
        passed += 1
        if verbose:
            print(f"  [PASS] manifest.yaml: version: {manifest_version}")

    # Step 4: Check README.md version (L521 gap fix)
    readme_version, errors = extract_readme_version(repo_path)
    if errors:
        failed += 1
        issues["readme_md"] = errors
        if verbose:
            print("  [FAIL] README.md")
            for e in errors:
                print(f"    - {e}")
    elif readme_version is None:
        # README.md doesn't have version pattern - OK for some repos
        passed += 1
        if verbose:
            print("  [PASS] README.md: no version pattern (not applicable)")
    elif readme_version != primary_version:
        failed += 1
        issues["readme_md"] = [
            f"L521: README.md has Current Version: v{readme_version} but version.json has {primary_version}"
        ]
        if verbose:
            print(f"  [FAIL] README.md: v{readme_version} != {primary_version}")
    else:
        passed += 1
        if verbose:
            print(f"  [PASS] README.md: Current Version: v{readme_version}")

    # Step 5: Check CHANGELOG.md has entry (was Step 4 before L521)
    has_entry, errors = check_changelog_entry(repo_path, primary_version)
    if not has_entry:
        failed += 1
        issues["changelog"] = errors
        if verbose:
            print("  [FAIL] CHANGELOG.md")
            for e in errors:
                print(f"    - {e}")
    else:
        passed += 1
        if verbose:
            print(f"  [PASS] CHANGELOG.md: [{primary_version}] entry exists")

    # Step 6: Check for stale references (V7.1.6) - optional
    if check_stale:
        stale_count, stale_files = check_stale_references(repo_path, check_stale)
        if stale_count > 0:
            failed += 1
            issues["stale_refs"] = [
                f"V7.1.6: {stale_count} files contain stale version references to {check_stale}:"
            ] + [f"  - {f}" for f in stale_files[:10]]  # Limit to first 10
            if stale_count > 10:
                issues["stale_refs"].append(f"  ... and {stale_count - 10} more")
            if verbose:
                print(f"  [FAIL] Stale references to v{check_stale}")
                for f in stale_files[:5]:
                    print(f"    - {f}")
        else:
            passed += 1
            if verbose:
                print(f"  [PASS] No stale references to v{check_stale}")

    return passed, failed, issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate version coherence across all version-bearing files (L444)"
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
        "--check-stale",
        metavar="VERSION",
        help="Check for stale references to specified version (e.g., 3.1.0)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Path is not a directory: {path}")
        sys.exit(1)

    if args.verbose and not args.json:
        print(f"Validating version inventory: {path}")
        print()

    passed, failed, issues = validate_coherence(path, args.check_stale, args.verbose and not args.json)

    if args.json:
        result = {
            "path": str(path),
            "passed": passed,
            "failed": failed,
            "coherent": failed == 0,
            "issues": issues
        }
        print(json.dumps(result, indent=2))
    else:
        print()
        print("=" * 60)
        print("Version Inventory Coherence Validation (L444)")
        print("=" * 60)
        print(f"Repository: {path.name}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if issues:
            print("\nIssues:")
            for check, errors in issues.items():
                print(f"\n  {check}:")
                for error in errors:
                    print(f"    - {error}")

        if failed > 0:
            print(f"\nFAIL: Version inventory is NOT coherent")
            sys.exit(1)
        else:
            print(f"\nPASS: Version inventory is coherent")
            sys.exit(0)


if __name__ == "__main__":
    main()
