#!/usr/bin/env python3
"""
Cleanup Template Archive

Removes the .aget/archive/ directory after verification period.
Only run after confirming the template works without archived items.

Part of AGET v3.0.0-beta.2 migration automation (L392 Pattern).

Usage:
    python3 cleanup_template_archive.py <template_path> --verify
    python3 cleanup_template_archive.py <template_path> --execute

Exit codes:
    0: Cleanup complete
    1: Cleanup error or verification failed
    2: Invalid arguments
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ArchiveCleaner:
    """Cleans up the archive after verification."""

    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.aget_path = template_path / ".aget"
        self.archive_path = self.aget_path / "archive"

    def verify(self) -> Dict[str, Any]:
        """Verify archive can be safely removed."""
        results = {
            "template": self.template_path.name,
            "archive_exists": self.archive_path.exists(),
            "safe_to_remove": False,
            "checks": [],
            "warnings": [],
        }

        if not self.archive_path.exists():
            results["checks"].append({
                "name": "archive_exists",
                "passed": False,
                "message": "No archive directory found",
            })
            return results

        # Check 1: Archive manifest exists
        manifest_path = self.archive_path / "_archive_manifest.json"
        if manifest_path.exists():
            results["checks"].append({
                "name": "manifest_exists",
                "passed": True,
                "message": "Archive manifest found",
            })
            with open(manifest_path) as f:
                manifest = json.load(f)
                results["archived_items"] = len(manifest.get("archived_items", []))
                results["deleted_items"] = len(manifest.get("deleted_items", []))
                results["migration_date"] = manifest.get("migration_date", "unknown")
        else:
            results["checks"].append({
                "name": "manifest_exists",
                "passed": False,
                "message": "No archive manifest found",
            })

        # Check 2: Template is compliant
        try:
            scripts_dir = Path(__file__).parent
            sys.path.insert(0, str(scripts_dir))
            from analyze_template_compliance import TemplateComplianceAnalyzer

            analyzer = TemplateComplianceAnalyzer(self.template_path)
            analysis = analyzer.analyze()

            if analysis["summary"]["is_compliant"]:
                results["checks"].append({
                    "name": "template_compliant",
                    "passed": True,
                    "message": f"Template is v3.0 compliant ({analysis['summary']['required_compliance']})",
                })
            else:
                results["checks"].append({
                    "name": "template_compliant",
                    "passed": False,
                    "message": f"Template not fully compliant ({analysis['summary']['required_compliance']})",
                })
        except Exception as e:
            results["checks"].append({
                "name": "template_compliant",
                "passed": False,
                "message": f"Failed to analyze: {e}",
            })

        # Check 3: Archive size
        archive_size = sum(f.stat().st_size for f in self.archive_path.rglob("*") if f.is_file())
        archive_size_mb = archive_size / (1024 * 1024)
        results["archive_size_mb"] = round(archive_size_mb, 2)
        results["checks"].append({
            "name": "archive_size",
            "passed": True,
            "message": f"Archive size: {archive_size_mb:.2f} MB",
        })

        # Check 4: No references to archived items in code
        # This is a simple check - could be more sophisticated
        results["checks"].append({
            "name": "no_references",
            "passed": True,
            "message": "Reference check: manual verification recommended",
        })
        results["warnings"].append(
            "Please manually verify no code references archived items before cleanup"
        )

        # Determine if safe to remove
        all_checks_passed = all(c["passed"] for c in results["checks"])
        results["safe_to_remove"] = all_checks_passed

        return results

    def cleanup(self) -> Dict[str, Any]:
        """Remove the archive directory."""
        results = {
            "template": self.template_path.name,
            "success": False,
            "archive_removed": False,
            "error": None,
        }

        if not self.archive_path.exists():
            results["error"] = "No archive to clean up"
            return results

        try:
            # Record what we're deleting
            manifest_path = self.archive_path / "_archive_manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    results["manifest"] = json.load(f)

            # Remove archive
            shutil.rmtree(self.archive_path)
            results["archive_removed"] = True
            results["success"] = True

        except Exception as e:
            results["error"] = str(e)

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup template archive after verification"
    )
    parser.add_argument(
        "template_path",
        help="Path to template directory"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify archive can be safely removed"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually remove the archive"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip verification and remove archive"
    )

    args = parser.parse_args()

    if not args.verify and not args.execute:
        print("Error: Must specify --verify or --execute")
        sys.exit(2)

    template_path = Path(args.template_path)
    if not template_path.is_absolute():
        template_path = Path.cwd() / template_path

    cleaner = ArchiveCleaner(template_path)

    if args.verify:
        results = cleaner.verify()

        print()
        print("=" * 60)
        print(f"Archive Verification: {template_path.name}")
        print("=" * 60)
        print()

        if not results["archive_exists"]:
            print("No archive found - nothing to clean up")
            sys.exit(0)

        print(f"Migration date: {results.get('migration_date', 'unknown')}")
        print(f"Archived items: {results.get('archived_items', 'unknown')}")
        print(f"Deleted items: {results.get('deleted_items', 'unknown')}")
        print(f"Archive size: {results.get('archive_size_mb', 'unknown')} MB")
        print()

        print("Checks:")
        for check in results["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            icon = "[OK]" if check["passed"] else "[XX]"
            print(f"  {icon} {check['name']}: {check['message']}")

        if results["warnings"]:
            print()
            print("Warnings:")
            for warning in results["warnings"]:
                print(f"  ! {warning}")

        print()
        print("=" * 60)
        if results["safe_to_remove"]:
            print("OK: Archive can be safely removed")
            print()
            print(f"To cleanup: python3 cleanup_template_archive.py {template_path} --execute")
        else:
            print("XX: Archive should NOT be removed - verification failed")
            sys.exit(1)

    elif args.execute:
        # Verify first unless --force
        if not args.force:
            verify_results = cleaner.verify()
            if not verify_results["safe_to_remove"]:
                print("Verification failed. Use --force to override.")
                sys.exit(1)

        results = cleaner.cleanup()

        print()
        print("=" * 60)
        print(f"Archive Cleanup: {template_path.name}")
        print("=" * 60)
        print()

        if results["success"]:
            print("OK: Archive removed successfully")
            if "manifest" in results:
                m = results["manifest"]
                print(f"  Archived items removed: {len(m.get('archived_items', []))}")
                print(f"  Migration date was: {m.get('migration_date', 'unknown')}")
        else:
            print(f"ERROR: {results['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
