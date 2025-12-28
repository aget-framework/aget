#!/usr/bin/env python3
"""
Migrate Template to v3

Migrates a template to AGET_TEMPLATE_SPEC v3.0 by archiving legacy items
and removing framework code.

Part of AGET v3.0.0-beta.2 migration automation (L392 Pattern).

Usage:
    python3 migrate_template_to_v3.py <template_path> --dry-run
    python3 migrate_template_to_v3.py <template_path> --execute

Exit codes:
    0: Migration complete
    1: Migration error
    2: Invalid arguments
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TemplateMigrator:
    """Migrates template to v3.0 spec compliance."""

    def __init__(self, template_path: Path, dry_run: bool = True):
        self.template_path = template_path
        self.aget_path = template_path / ".aget"
        self.archive_path = self.aget_path / "archive"
        self.dry_run = dry_run
        self.actions: List[Dict[str, Any]] = []
        self.manifest: Dict[str, Any] = {
            "migration_date": datetime.now().isoformat(),
            "template": template_path.name,
            "from_version": "2.x",
            "to_version": "3.0",
            "archived_items": [],
            "deleted_items": [],
        }

    def migrate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute migration based on analysis."""
        results = {
            "template": self.template_path.name,
            "dry_run": self.dry_run,
            "actions": [],
            "success": True,
            "error": None,
        }

        try:
            # Create archive structure
            self._create_archive_structure()

            # Archive legacy directories
            for item in analysis["compliance"]["legacy_dirs"]:
                self._archive_item(item["path"])

            # Archive legacy files
            for item in analysis["compliance"]["legacy_files"]:
                self._archive_item(item["path"])

            # Delete framework code
            for item in analysis["compliance"]["delete_candidates"]:
                self._delete_item(item["path"])

            # Write archive manifest
            self._write_manifest()

            results["actions"] = self.actions

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    def _create_archive_structure(self):
        """Create the archive directory structure."""
        dirs_to_create = [
            self.archive_path / "_legacy_dirs",
            self.archive_path / "_legacy_files",
        ]

        for dir_path in dirs_to_create:
            action = {
                "type": "create_dir",
                "path": str(dir_path.relative_to(self.template_path)),
            }
            self.actions.append(action)

            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)

    def _archive_item(self, relative_path: str):
        """Archive a legacy item."""
        # Remove trailing slash and handle path
        clean_path = relative_path.rstrip("/")
        if clean_path.startswith("./"):
            clean_path = clean_path[2:]
        source = self.template_path / clean_path
        if not source.exists():
            return

        # Determine target location
        if source.is_dir():
            dir_name = source.name
            target = self.archive_path / "_legacy_dirs" / dir_name
        else:
            file_name = source.name
            target = self.archive_path / "_legacy_files" / file_name

        action = {
            "type": "archive",
            "source": relative_path,
            "target": str(target.relative_to(self.template_path)),
        }
        self.actions.append(action)

        self.manifest["archived_items"].append({
            "source": relative_path,
            "target": str(target.relative_to(self.template_path)),
            "type": "directory" if source.is_dir() else "file",
        })

        if not self.dry_run:
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(source), str(target))

    def _delete_item(self, relative_path: str):
        """Delete a framework code directory."""
        clean_path = relative_path.rstrip("/")
        if clean_path.startswith("./"):
            clean_path = clean_path[2:]
        target = self.template_path / clean_path
        if not target.exists():
            return

        action = {
            "type": "delete",
            "path": relative_path,
            "reason": "Framework code should not be in templates",
        }
        self.actions.append(action)

        self.manifest["deleted_items"].append({
            "path": relative_path,
            "type": "directory" if target.is_dir() else "file",
        })

        if not self.dry_run:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

    def _write_manifest(self):
        """Write the archive manifest."""
        manifest_path = self.archive_path / "_archive_manifest.json"

        action = {
            "type": "write_manifest",
            "path": str(manifest_path.relative_to(self.template_path)),
        }
        self.actions.append(action)

        if not self.dry_run:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(manifest_path, "w") as f:
                json.dump(self.manifest, f, indent=2)


def run_analysis(template_path: Path) -> Dict[str, Any]:
    """Run compliance analysis on template."""
    # Import the analyzer
    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))
    from analyze_template_compliance import TemplateComplianceAnalyzer

    analyzer = TemplateComplianceAnalyzer(template_path)
    return analyzer.analyze()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate template to AGET_TEMPLATE_SPEC v3.0"
    )
    parser.add_argument(
        "template_path",
        help="Path to template directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration"
    )
    parser.add_argument(
        "--analysis", "-a",
        help="Use pre-generated analysis JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify --dry-run or --execute")
        sys.exit(2)

    template_path = Path(args.template_path)
    if not template_path.is_absolute():
        template_path = Path.cwd() / template_path

    if not template_path.exists():
        print(f"Error: Template not found: {template_path}")
        sys.exit(1)

    # Get analysis
    if args.analysis:
        with open(args.analysis) as f:
            analysis = json.load(f)
    else:
        print(f"Analyzing: {template_path.name}...")
        analysis = run_analysis(template_path)

    # Check if already compliant
    if analysis["summary"]["is_compliant"]:
        print(f"{template_path.name} is already v3.0 compliant!")
        sys.exit(0)

    # Run migration
    dry_run = args.dry_run
    migrator = TemplateMigrator(template_path, dry_run=dry_run)
    results = migrator.migrate(analysis)

    # Output results
    print()
    print("=" * 60)
    print(f"Migration {'Plan' if dry_run else 'Results'}: {template_path.name}")
    print("=" * 60)
    print()

    if dry_run:
        print("DRY RUN - No changes made")
        print()

    # Group actions by type
    create_actions = [a for a in results["actions"] if a["type"] == "create_dir"]
    archive_actions = [a for a in results["actions"] if a["type"] == "archive"]
    delete_actions = [a for a in results["actions"] if a["type"] == "delete"]
    manifest_actions = [a for a in results["actions"] if a["type"] == "write_manifest"]

    if create_actions:
        print("Create directories:")
        for action in create_actions:
            print(f"  + {action['path']}")
        print()

    if archive_actions:
        print("Archive items:")
        for action in archive_actions:
            print(f"  -> {action['source']}")
            if args.verbose:
                print(f"     to: {action['target']}")
        print()

    if delete_actions:
        print("Delete items:")
        for action in delete_actions:
            print(f"  X {action['path']}")
            if args.verbose:
                print(f"     reason: {action['reason']}")
        print()

    if manifest_actions:
        print("Write manifest:")
        for action in manifest_actions:
            print(f"  * {action['path']}")
        print()

    print("=" * 60)
    if results["success"]:
        action_verb = "would be performed" if dry_run else "performed"
        print(f"OK: {len(results['actions'])} actions {action_verb}")
        if dry_run:
            print()
            print("To execute: python3 migrate_template_to_v3.py {} --execute".format(
                template_path
            ))
    else:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    # Post-migration validation
    if not dry_run:
        print()
        print("Running post-migration validation...")
        post_analysis = run_analysis(template_path)
        if post_analysis["summary"]["is_compliant"]:
            print("PASS: Template is now v3.0 compliant!")
        else:
            print("WARN: Template still has compliance issues:")
            print(f"  Legacy items: {post_analysis['summary']['legacy_items']}")
            print(f"  Delete candidates: {post_analysis['summary']['delete_candidates']}")


if __name__ == "__main__":
    main()
