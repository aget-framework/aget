#!/usr/bin/env python3
"""
validate_version_ceiling.py - Validate instance versions don't exceed framework version

Implements CAP-REL-010 (Version Ceiling Constraint) from L517:
- Instance aget_version SHALL NOT exceed framework aget_version
- Detects Version_Overrun anti-pattern

Usage:
    python3 validate_version_ceiling.py <instances_path> [--framework-path PATH]
    python3 validate_version_ceiling.py /path/to/private-agents
    python3 validate_version_ceiling.py . --framework-path /path/to/aget-framework/aget

Exit Codes:
    0 - All instances within ceiling
    1 - Version overrun detected (instance > framework)

Author: private-aget-framework-AGET
Version: 1.0.0
Created: 2026-01-11
Implements: CAP-REL-010, L517
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def parse_version(version_str: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into comparable tuple.

    Returns: (major, minor, patch, prerelease)
    Prerelease is empty string for release versions.
    """
    # Handle prerelease suffix
    prerelease = ""
    if "-" in version_str:
        version_str, prerelease = version_str.split("-", 1)

    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")

    # Parse major.minor.patch
    parts = version_str.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0

    return (major, minor, patch, prerelease)


def version_exceeds(instance_version: str, framework_version: str) -> bool:
    """Check if instance version exceeds framework version.

    Returns True if instance > framework (Version_Overrun).
    """
    inst = parse_version(instance_version)
    frame = parse_version(framework_version)

    # Compare major.minor.patch
    inst_tuple = (inst[0], inst[1], inst[2])
    frame_tuple = (frame[0], frame[1], frame[2])

    if inst_tuple > frame_tuple:
        return True

    # If same version numbers, prerelease is "less than" release
    # e.g., 3.3.0-alpha < 3.3.0
    if inst_tuple == frame_tuple:
        # If framework has prerelease but instance doesn't, instance is higher
        if frame[3] and not inst[3]:
            return True

    return False


def get_version_from_file(version_path: Path) -> Optional[str]:
    """Extract aget_version from version.json file."""
    if not version_path.exists():
        return None

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("aget_version")
    except Exception:
        return None


def find_instances(instances_path: Path) -> List[Path]:
    """Find all AGET instances (directories with .aget/version.json)."""
    instances = []

    # Check if instances_path itself is an instance
    version_file = instances_path / ".aget" / "version.json"
    if version_file.exists():
        instances.append(instances_path)

    # Check subdirectories
    for subdir in instances_path.iterdir():
        if subdir.is_dir():
            version_file = subdir / ".aget" / "version.json"
            if version_file.exists():
                instances.append(subdir)

    return instances


def validate_ceiling(
    instances_path: Path,
    framework_path: Path,
    verbose: bool = False
) -> Tuple[int, int, List[str]]:
    """Validate all instances are within version ceiling.

    Returns: (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    # Get framework version
    framework_version_path = framework_path / ".aget" / "version.json"
    framework_version = get_version_from_file(framework_version_path)

    if not framework_version:
        errors.append(f"CAP-REL-010: Cannot read framework version from {framework_version_path}")
        return 0, 1, errors

    if verbose:
        print(f"Framework version: {framework_version}")
        print(f"Version ceiling: {framework_version}")
        print()

    # Find and check instances
    instances = find_instances(instances_path)

    if not instances:
        if verbose:
            print("No instances found to check.")
        return 0, 0, []

    for instance_path in instances:
        version_path = instance_path / ".aget" / "version.json"
        instance_version = get_version_from_file(version_path)

        if not instance_version:
            if verbose:
                print(f"  {instance_path.name}: SKIP (no version)")
            continue

        if version_exceeds(instance_version, framework_version):
            failed += 1
            error_msg = (
                f"CAP-REL-010: Version_Overrun detected: "
                f"{instance_path.name} ({instance_version}) > framework ({framework_version})"
            )
            errors.append(error_msg)
            if verbose:
                print(f"  {instance_path.name}: FAIL ({instance_version} > {framework_version})")
        else:
            passed += 1
            if verbose:
                print(f"  {instance_path.name}: PASS ({instance_version} <= {framework_version})")

    return passed, failed, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate instance versions don't exceed framework (CAP-REL-010)"
    )
    parser.add_argument(
        "instances_path",
        type=Path,
        help="Path to directory containing AGET instances"
    )
    parser.add_argument(
        "--framework-path",
        type=Path,
        default=None,
        help="Path to aget/ core (default: look for ../aget-framework/aget)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    instances_path = args.instances_path.resolve()

    # Find framework path
    if args.framework_path:
        framework_path = args.framework_path.resolve()
    else:
        # Try common locations
        candidates = [
            instances_path.parent / "aget-framework" / "aget",
            instances_path.parent / "aget",
            Path("/Users/gabormelli/github/aget-framework/aget"),
        ]
        framework_path = None
        for candidate in candidates:
            if (candidate / ".aget" / "version.json").exists():
                framework_path = candidate
                break

        if not framework_path:
            print("Error: Cannot find framework path. Use --framework-path.")
            sys.exit(1)

    if not instances_path.exists():
        print(f"Error: Instances path does not exist: {instances_path}")
        sys.exit(1)

    if not framework_path.exists():
        print(f"Error: Framework path does not exist: {framework_path}")
        sys.exit(1)

    print(f"Validating version ceiling (CAP-REL-010)")
    print(f"Instances: {instances_path}")
    print(f"Framework: {framework_path}")
    print()

    passed, failed, errors = validate_ceiling(
        instances_path,
        framework_path,
        args.verbose
    )

    print(f"\n{'='*60}")
    print(f"Version Ceiling Validation Summary")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if errors:
        print(f"\nVersion_Overrun Detected:")
        for error in errors:
            print(f"  - {error}")

    if failed > 0:
        print(f"\nFAIL: {failed} instances exceed framework version")
        print("This is the Version_Overrun anti-pattern (L517).")
        print("Resolution: Either upgrade framework or downgrade instances.")
        sys.exit(1)
    else:
        print(f"\nPASS: All instances within version ceiling")
        sys.exit(0)


if __name__ == "__main__":
    main()
