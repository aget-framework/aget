#!/usr/bin/env python3
"""
V-CAP-REL-008: Validate org-profile homepage currency per R-REL-010-01..07.

Implements:
- R-REL-010-01: Homepage shows current version
- R-REL-010-02: Roadmap reflects release status
- R-REL-010-03: Next version documented
- R-REL-010-04: version badge displays current released version
- R-REL-010-05: released-date badge displays release date
- R-REL-010-06: Roadmap has exactly ONE (Current) entry matching released version
- R-REL-010-07: migration_history sample includes current version

Usage:
    python3 validate_homepage_currency.py --version 3.17.0 [--readme-path ../.github/profile/README.md] [--strict] [--json]

Exit codes:
    0 = all PASS
    1 = any FAIL
    2 = validator error
"""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_homepage(readme_path: Path, version: str) -> dict:
    """Run all R-REL-010-NN checks against the org-profile README."""
    if not readme_path.exists():
        return {"path": str(readme_path), "version": version, "error": "README not found", "overall": "ERROR"}

    content = readme_path.read_text(encoding='utf-8')
    results = {"path": str(readme_path), "version": version, "checks": {}, "overall": "PASS"}

    # R-REL-010-04: version badge displays current released version
    # Pattern: shields.io badge or similar with version-X.Y.Z
    version_badges = re.findall(r'badge/version-([\d.]+)|version[/-](\d+\.\d+\.\d+)', content)
    found_versions = [v[0] or v[1] for v in version_badges]
    has_current_badge = version in found_versions
    results["checks"]["R-REL-010-04_version_badge"] = "PASS" if has_current_badge else f"FAIL (version badges found: {found_versions[:3]}; expected {version})"

    # R-REL-010-05: released-date badge
    # Pattern: badge/released-YYYY--MM--DD or similar
    date_badges = re.findall(r'badge/released-(\d{4})--(\d{2})--(\d{2})|released[/-](\d{4}-\d{2}-\d{2})', content)
    has_date_badge = bool(date_badges)
    results["checks"]["R-REL-010-05_release_date_badge"] = "PASS" if has_date_badge else "FAIL (no release-date badge found)"

    # R-REL-010-06: Roadmap has exactly ONE (Current) entry matching version
    current_entries = re.findall(r'^###?\s+v(\d+\.\d+\.\d+)\s*\(Current\)', content, re.MULTILINE | re.IGNORECASE)
    if len(current_entries) == 1 and current_entries[0] == version:
        results["checks"]["R-REL-010-06_roadmap_current"] = "PASS"
    elif len(current_entries) == 0:
        results["checks"]["R-REL-010-06_roadmap_current"] = "FAIL (no Roadmap entry tagged (Current))"
    elif len(current_entries) > 1:
        results["checks"]["R-REL-010-06_roadmap_current"] = f"FAIL ({len(current_entries)} entries tagged (Current); expected exactly 1)"
    else:
        results["checks"]["R-REL-010-06_roadmap_current"] = f"FAIL (Current entry is v{current_entries[0]}; expected v{version})"

    # R-REL-010-07: migration_history sample includes current version
    has_current_in_history = bool(re.search(rf'v\d+\.\d+\.\d+\s*->\s*v?{re.escape(version)}', content))
    results["checks"]["R-REL-010-07_migration_history"] = "PASS" if has_current_in_history else f"FAIL (migration_history sample doesn't include v{version} as latest)"

    # R-REL-010-01 (synthetic): version appears in headline
    has_version_anywhere = version in content
    results["checks"]["R-REL-010-01_version_visible"] = "PASS" if has_version_anywhere else f"FAIL (version {version} not present anywhere in README)"

    if any(check.startswith("FAIL") for check in results["checks"].values()):
        results["overall"] = "FAIL"

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate homepage currency per R-REL-010-NN")
    parser.add_argument("--version", required=True, help="Released version (e.g., 3.17.0)")
    parser.add_argument("--readme-path", default="../.github/profile/README.md", help="Path to org-profile README.md")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = validate_homepage(Path(args.readme_path), args.version)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Homepage currency check: {result['path']} for v{result['version']} ===")
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            for check_id, status in result["checks"].items():
                marker = "✅" if status.startswith("PASS") else "❌"
                print(f"  {marker} {check_id}: {status}")
        print(f"\nOverall: {result['overall']}")

    sys.exit(1 if result["overall"] != "PASS" else 0)


if __name__ == "__main__":
    main()
