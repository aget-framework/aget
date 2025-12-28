#!/usr/bin/env python3
"""
Analyze Template Compliance

Analyzes a template directory against AGET_TEMPLATE_SPEC v3.0 and produces
a JSON compliance report with recommendations for migration.

Part of AGET v3.0.0-beta.2 migration automation (L392 Pattern).

Usage:
    python3 analyze_template_compliance.py <template_path>
    python3 analyze_template_compliance.py --all

Exit codes:
    0: Analysis complete
    1: Analysis error
    2: Invalid arguments
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


# v3.0 Spec-compliant structure
SPEC_REQUIRED = {
    ".aget/version.json": "Version and instance metadata",
    ".aget/identity.json": "North Star and agent identity",
    ".aget/persona/archetype.yaml": "D1: Archetype configuration",
    ".aget/persona/style.yaml": "D1: Communication style",
    ".aget/memory/domain/": "D2: Domain knowledge (directory)",
    ".aget/memory/organizational/": "D2: Organizational knowledge (directory)",
    ".aget/memory/experiential/": "D2: Experiential knowledge (directory)",
    ".aget/reasoning/decision_authority.yaml": "D3: Decision authority matrix",
    ".aget/reasoning/planning_patterns.yaml": "D3: Planning approach",
    ".aget/skills/capabilities.yaml": "D4: Capability declarations",
    ".aget/skills/phase_mapping.yaml": "D4: A-SDLC phase mapping",
    ".aget/context/relationships.yaml": "D5: Agent relationships",
    ".aget/context/scope.yaml": "D5: Operational scope",
}

SPEC_OPTIONAL = {
    ".aget/patterns/session/wake_up.py": "Session initialization",
    ".aget/patterns/session/wind_down.py": "Session end",
    ".aget/patterns/release/version_bump.py": "Version coordination",
    ".aget/patterns/release/pre_release_validation.py": "Pre-release checks",
    ".aget/patterns/release/post_release_validation.py": "Post-release checks",
    ".aget/patterns/sync/version_consistency.py": "Version sync check",
    ".aget/patterns/sync/template_sync_check.py": "Template sync check",
    ".aget/evolution/": "Learning documents (directory)",
}

# Root-level spec items
ROOT_REQUIRED = {
    "manifest.yaml": "Template manifest (v3.0)",
    "governance/CHARTER.md": "Agent charter",
    "governance/MISSION.md": "Mission statement",
    "governance/SCOPE_BOUNDARIES.md": "Scope boundaries",
    "tests/": "Contract tests (directory)",
    "README.md": "Template readme",
}

ROOT_OPTIONAL = {
    "CHANGELOG.md": "Version history",
    ".gitignore": "Git ignore patterns",
}

# Known legacy items to archive
LEGACY_AGET_DIRS = {
    "architecture", "backups", "client_progress", "commitments",
    "docs", "examples", "intelligence", "learning_history",
    "schemas", "sessions", "specs", "tools", "vocabulary",
}

LEGACY_AGET_FILES = {
    "BRANCHING.md", "claude_costs.jsonl", "cost_tracking_config.json",
    "dependencies.json", "ETHOS_CHECK.md", "organization_manifest.json",
    "OWNERSHIP.md", "RELEASE_CHECKLIST.md", "v2-baseline.json",
}

# Root-level items to delete (not archive)
DELETE_ROOT_DIRS = {"aget", "docs"}


class TemplateComplianceAnalyzer:
    """Analyzes template compliance with AGET_TEMPLATE_SPEC v3.0."""

    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.aget_path = template_path / ".aget"
        self.results: Dict[str, Any] = {
            "template": template_path.name,
            "spec_version": "3.0",
            "analysis_date": datetime.now().isoformat(),
            "compliance": {
                "required_present": [],
                "required_missing": [],
                "optional_present": [],
                "optional_missing": [],
                "legacy_dirs": [],
                "legacy_files": [],
                "delete_candidates": [],
                "unknown": [],
            },
            "recommendations": [],
            "summary": {},
        }

    def analyze(self) -> Dict[str, Any]:
        """Run full compliance analysis."""
        self._check_required_items()
        self._check_optional_items()
        self._check_root_items()
        self._identify_legacy()
        self._identify_unknown()
        self._generate_recommendations()
        self._generate_summary()
        return self.results

    def _check_required_items(self):
        """Check for required spec items."""
        for item, description in SPEC_REQUIRED.items():
            full_path = self.template_path / item
            if item.endswith("/"):
                exists = full_path.is_dir()
            else:
                exists = full_path.is_file()

            if exists:
                self.results["compliance"]["required_present"].append({
                    "path": item,
                    "description": description,
                })
            else:
                self.results["compliance"]["required_missing"].append({
                    "path": item,
                    "description": description,
                })

    def _check_optional_items(self):
        """Check for optional spec items."""
        for item, description in SPEC_OPTIONAL.items():
            full_path = self.template_path / item
            if item.endswith("/"):
                exists = full_path.is_dir()
            else:
                exists = full_path.is_file()

            if exists:
                self.results["compliance"]["optional_present"].append({
                    "path": item,
                    "description": description,
                })
            else:
                self.results["compliance"]["optional_missing"].append({
                    "path": item,
                    "description": description,
                })

    def _check_root_items(self):
        """Check root-level required and optional items."""
        for item, description in ROOT_REQUIRED.items():
            full_path = self.template_path / item
            if item.endswith("/"):
                exists = full_path.is_dir()
            else:
                exists = full_path.is_file()

            if exists:
                self.results["compliance"]["required_present"].append({
                    "path": item,
                    "description": description,
                })
            else:
                self.results["compliance"]["required_missing"].append({
                    "path": item,
                    "description": description,
                })

        for item, description in ROOT_OPTIONAL.items():
            full_path = self.template_path / item
            exists = full_path.exists()

            if exists:
                self.results["compliance"]["optional_present"].append({
                    "path": item,
                    "description": description,
                })

    def _identify_legacy(self):
        """Identify legacy items in .aget directory."""
        if not self.aget_path.exists():
            return

        for item in self.aget_path.iterdir():
            name = item.name

            if name in LEGACY_AGET_DIRS and item.is_dir():
                self.results["compliance"]["legacy_dirs"].append({
                    "path": f".aget/{name}/",
                    "action": "archive",
                })
            elif name in LEGACY_AGET_FILES and item.is_file():
                self.results["compliance"]["legacy_files"].append({
                    "path": f".aget/{name}",
                    "action": "archive",
                })

        # Check root-level delete candidates
        for dirname in DELETE_ROOT_DIRS:
            full_path = self.template_path / dirname
            if full_path.is_dir():
                self.results["compliance"]["delete_candidates"].append({
                    "path": f"{dirname}/",
                    "action": "delete",
                    "reason": "Framework code should not be in templates",
                })

    def _identify_unknown(self):
        """Identify items not in spec or legacy lists."""
        if not self.aget_path.exists():
            return

        known_dirs = {"persona", "memory", "reasoning", "skills", "context",
                      "patterns", "evolution", "archive"} | LEGACY_AGET_DIRS
        known_files = {"version.json", "identity.json"} | LEGACY_AGET_FILES

        for item in self.aget_path.iterdir():
            name = item.name

            if item.is_dir() and name not in known_dirs:
                self.results["compliance"]["unknown"].append({
                    "path": f".aget/{name}/",
                    "type": "directory",
                })
            elif item.is_file() and name not in known_files:
                self.results["compliance"]["unknown"].append({
                    "path": f".aget/{name}",
                    "type": "file",
                })

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recs = []

        # Missing required items
        for item in self.results["compliance"]["required_missing"]:
            recs.append({
                "priority": "high",
                "action": "create",
                "path": item["path"],
                "description": f"Create required: {item['description']}",
            })

        # Legacy items to archive
        for item in self.results["compliance"]["legacy_dirs"]:
            recs.append({
                "priority": "medium",
                "action": "archive",
                "path": item["path"],
                "target": f".aget/archive/_legacy_dirs/{item['path'].split('/')[-2]}/",
            })

        for item in self.results["compliance"]["legacy_files"]:
            recs.append({
                "priority": "medium",
                "action": "archive",
                "path": item["path"],
                "target": f".aget/archive/_legacy_files/{item['path'].split('/')[-1]}",
            })

        # Delete candidates
        for item in self.results["compliance"]["delete_candidates"]:
            recs.append({
                "priority": "high",
                "action": "delete",
                "path": item["path"],
                "reason": item["reason"],
            })

        # Unknown items
        for item in self.results["compliance"]["unknown"]:
            recs.append({
                "priority": "low",
                "action": "review",
                "path": item["path"],
                "description": "Not in spec - review for archive or keep",
            })

        self.results["recommendations"] = recs

    def _generate_summary(self):
        """Generate summary statistics."""
        c = self.results["compliance"]
        total_required = len(SPEC_REQUIRED) + len(ROOT_REQUIRED)
        present_required = len(c["required_present"])

        self.results["summary"] = {
            "required_compliance": f"{present_required}/{total_required}",
            "compliance_percent": round(present_required / total_required * 100, 1),
            "legacy_items": len(c["legacy_dirs"]) + len(c["legacy_files"]),
            "delete_candidates": len(c["delete_candidates"]),
            "unknown_items": len(c["unknown"]),
            "total_recommendations": len(self.results["recommendations"]),
            "is_compliant": present_required == total_required and
                           len(c["legacy_dirs"]) == 0 and
                           len(c["legacy_files"]) == 0 and
                           len(c["delete_candidates"]) == 0,
        }


def find_framework_root() -> Path:
    """Find the aget-framework root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "aget" / "specs").exists():
            return current
        current = current.parent
    return Path.cwd()


def analyze_all_templates(framework_root: Path) -> Dict[str, Any]:
    """Analyze all templates in the framework."""
    results = {
        "analysis_date": datetime.now().isoformat(),
        "templates": {},
        "summary": {
            "total": 0,
            "compliant": 0,
            "needs_work": 0,
        }
    }

    for template_dir in sorted(framework_root.iterdir()):
        if template_dir.is_dir() and template_dir.name.startswith("template-"):
            analyzer = TemplateComplianceAnalyzer(template_dir)
            result = analyzer.analyze()
            results["templates"][template_dir.name] = result
            results["summary"]["total"] += 1
            if result["summary"]["is_compliant"]:
                results["summary"]["compliant"] += 1
            else:
                results["summary"]["needs_work"] += 1

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Analyze template compliance with AGET_TEMPLATE_SPEC v3.0"
    )
    parser.add_argument(
        "template_path",
        nargs="?",
        help="Path to template directory"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all templates in framework"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary only"
    )

    args = parser.parse_args()

    framework_root = find_framework_root()

    if args.all:
        results = analyze_all_templates(framework_root)

        if args.summary:
            print("=" * 60)
            print("AGET Template Compliance Analysis")
            print("=" * 60)
            print()
            for name, result in results["templates"].items():
                s = result["summary"]
                status = "COMPLIANT" if s["is_compliant"] else "NEEDS WORK"
                icon = "OK" if s["is_compliant"] else "XX"
                print(f"[{icon}] {name}")
                print(f"     Required: {s['required_compliance']} ({s['compliance_percent']}%)")
                print(f"     Legacy: {s['legacy_items']} | Delete: {s['delete_candidates']} | Unknown: {s['unknown_items']}")
                print()
            print("=" * 60)
            print(f"Total: {results['summary']['total']} | Compliant: {results['summary']['compliant']} | Needs Work: {results['summary']['needs_work']}")
        else:
            output = json.dumps(results, indent=2)
            if args.output:
                Path(args.output).write_text(output)
                print(f"Results written to {args.output}")
            else:
                print(output)

    elif args.template_path:
        template_path = Path(args.template_path)
        if not template_path.is_absolute():
            template_path = Path.cwd() / template_path

        analyzer = TemplateComplianceAnalyzer(template_path)
        results = analyzer.analyze()

        if args.summary:
            s = results["summary"]
            print(f"Template: {results['template']}")
            print(f"Required: {s['required_compliance']} ({s['compliance_percent']}%)")
            print(f"Legacy items: {s['legacy_items']}")
            print(f"Delete candidates: {s['delete_candidates']}")
            print(f"Unknown: {s['unknown_items']}")
            print(f"Status: {'COMPLIANT' if s['is_compliant'] else 'NEEDS WORK'}")
        else:
            output = json.dumps(results, indent=2)
            if args.output:
                Path(args.output).write_text(output)
                print(f"Results written to {args.output}")
            else:
                print(output)

        sys.exit(0 if results["summary"]["is_compliant"] else 1)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
