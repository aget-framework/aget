#!/usr/bin/env python3
"""
Analyze Knowledge Content

Audit knowledge/ directory for content placement, naming conventions,
and structural patterns. Based on fleet exploration (L399, L394).

Implements: CAP-INST-002 (Archetype Baseline), CAP-MEMORY-* (future)
See: aget/specs/AGET_INSTANCE_SPEC.md
Tests: tests/test_knowledge_audit.py (future)

Fleet Patterns Observed (2025-12-27):
- 3 archetypes: Rich Domain, Portfolio/Fleet, Empty/Stub
- Naming: FOUNDATIONAL_*, STRATEGIC_*, INTELLIGENCE_*, PROGRAM_*, _ARCHIVE_*
- Boundaries: L-docs in .aget/evolution/, PROJECT_PLANs in planning/

Usage:
    python3 analyze_knowledge_content.py <agent_path>
    python3 analyze_knowledge_content.py <agent_path> --strict
    python3 analyze_knowledge_content.py <agent_path> --json
    python3 analyze_knowledge_content.py --fleet <fleet_root>  # Audit entire fleet

Exit codes:
    0: All checks pass (or only warnings)
    1: Failures detected
    2: Invalid arguments
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class KnowledgeAuditor:
    """Audits knowledge/ directory for content patterns and placement."""

    # Known naming prefixes from fleet exploration
    KNOWN_PREFIXES = [
        "FOUNDATIONAL_",
        "STRATEGIC_",
        "INTELLIGENCE_",
        "PROGRAM_",
        "CONSULTING_",
        "IMPACT_",
        "FLEET_",
        "REFERENCE_",
        "_ARCHIVE_",
        "ARCHIVED_",
    ]

    # Files that should NOT be in knowledge/
    MISPLACED_PATTERNS = [
        (r"^L\d+_", "L-doc", ".aget/evolution/"),
        (r"^PROJECT_PLAN", "PROJECT_PLAN", "planning/"),
        (r"^CHARTER\.md$", "Charter", "governance/"),
        (r"^MISSION\.md$", "Mission", "governance/"),
        (r"^SCOPE", "Scope", "governance/"),
    ]

    # Maturity thresholds
    MATURITY_THRESHOLDS = {
        "empty": 0,
        "stub": 1,
        "minimal": 5,
        "active": 20,
        "mature": 999999,
    }

    def __init__(self, path: Path):
        self.path = path
        self.knowledge_path = path / "knowledge"
        self.results: List[Dict[str, Any]] = []
        self.files: List[Path] = []
        self.instance_type: Optional[str] = None

    def detect_instance_type(self) -> Optional[str]:
        """Detect if this is a template or instance."""
        version_file = self.path / ".aget" / "version.json"
        if version_file.exists():
            try:
                with open(version_file) as f:
                    data = json.load(f)
                    self.instance_type = data.get("instance_type")
                    return self.instance_type
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def audit(self) -> Dict[str, Any]:
        """Run all audit checks."""
        self.results = []
        self.detect_instance_type()

        # Check if knowledge/ exists
        if not self.knowledge_path.exists():
            self._add_result(
                "knowledge_exists",
                "fail",
                "knowledge/ directory missing",
                "Required by CAP-INST-002-01"
            )
            return self._summary()

        self._add_result(
            "knowledge_exists",
            "pass",
            "knowledge/ directory exists"
        )

        # Get all files (excluding .gitkeep)
        self.files = [
            f for f in self.knowledge_path.rglob("*")
            if f.is_file() and f.name != ".gitkeep"
        ]

        # Run checks
        self._check_readme()
        self._check_maturity()
        self._check_misplacements()
        self._check_naming_conventions()
        self._check_versioning()
        self._check_index()
        self._check_archive_pattern()

        return self._summary()

    def _add_result(self, check: str, status: str, message: str, note: str = ""):
        """Add an audit result."""
        self.results.append({
            "check": check,
            "status": status,
            "message": message,
            "note": note
        })

    def _check_readme(self):
        """Check for README.md in knowledge/."""
        readme = self.knowledge_path / "README.md"
        if readme.exists():
            # Check if it has content beyond placeholder
            content = readme.read_text()
            if len(content) > 100:
                self._add_result(
                    "readme_exists",
                    "pass",
                    "README.md exists with content"
                )
            else:
                self._add_result(
                    "readme_exists",
                    "warn",
                    "README.md exists but minimal content",
                    "Consider adding taxonomy and content guidelines"
                )
        else:
            self._add_result(
                "readme_exists",
                "fail" if self.instance_type == "aget" else "warn",
                "README.md missing",
                "Required for documenting knowledge taxonomy"
            )

    def _check_maturity(self):
        """Assess knowledge base maturity."""
        file_count = len(self.files)

        if file_count == 0:
            level = "empty"
        elif file_count <= 1:
            level = "stub"
        elif file_count <= 5:
            level = "minimal"
        elif file_count <= 20:
            level = "active"
        else:
            level = "mature"

        # Templates should be empty
        if self.instance_type == "template":
            if file_count == 0:
                self._add_result(
                    "maturity",
                    "pass",
                    f"Template knowledge is empty (correct)",
                    "Templates inherit knowledge from parent agents"
                )
            else:
                self._add_result(
                    "maturity",
                    "warn",
                    f"Template has {file_count} knowledge files",
                    "Templates typically have empty knowledge/"
                )
        else:
            # Instances should have content
            status = "pass" if level in ["active", "mature"] else "info"
            self._add_result(
                "maturity",
                status,
                f"Knowledge maturity: {level} ({file_count} files)"
            )

    def _check_misplacements(self):
        """Check for content that doesn't belong in knowledge/."""
        misplacements = []

        for f in self.files:
            for pattern, content_type, correct_location in self.MISPLACED_PATTERNS:
                if re.match(pattern, f.name):
                    misplacements.append((f, content_type, correct_location))

        if misplacements:
            for f, content_type, correct_location in misplacements:
                rel_path = f.relative_to(self.knowledge_path)
                self._add_result(
                    "misplacement",
                    "warn",
                    f"Possible misplacement: {rel_path}",
                    f"{content_type} typically belongs in {correct_location}"
                )
        else:
            self._add_result(
                "misplacement",
                "pass",
                "No obvious misplacements detected"
            )

    def _check_naming_conventions(self):
        """Check for consistent naming conventions."""
        if len(self.files) == 0:
            return

        # Find files with known prefixes
        prefixed = []
        unprefixed = []

        for f in self.files:
            if f.name == "README.md":
                continue

            has_prefix = any(
                f.name.startswith(prefix) for prefix in self.KNOWN_PREFIXES
            )
            if has_prefix:
                prefixed.append(f)
            else:
                unprefixed.append(f)

        total = len(prefixed) + len(unprefixed)
        if total == 0:
            return

        prefix_ratio = len(prefixed) / total

        if prefix_ratio >= 0.8:
            self._add_result(
                "naming_convention",
                "pass",
                f"Strong naming convention: {len(prefixed)}/{total} files use known prefixes"
            )
        elif prefix_ratio >= 0.5:
            self._add_result(
                "naming_convention",
                "info",
                f"Partial naming convention: {len(prefixed)}/{total} files use known prefixes",
                "Consider standardizing remaining files"
            )
        else:
            self._add_result(
                "naming_convention",
                "info",
                f"Custom naming: {len(prefixed)}/{total} files use known prefixes",
                "Document your naming convention in README.md"
            )

        # List unprefixed files if few
        if unprefixed and len(unprefixed) <= 5:
            names = [f.name for f in unprefixed]
            self._add_result(
                "naming_detail",
                "info",
                f"Files without known prefix: {', '.join(names)}"
            )

    def _check_versioning(self):
        """Check for version numbers in document names."""
        if len(self.files) == 0:
            return

        version_pattern = re.compile(r'_v\d+(\.\d+)*\.md$|_v\d+(\.\d+)*$')
        versioned = [f for f in self.files if version_pattern.search(f.name)]

        if len(versioned) > 0:
            self._add_result(
                "versioning",
                "info",
                f"{len(versioned)}/{len(self.files)} files have version numbers"
            )

    def _check_index(self):
        """Check for index file in large knowledge bases."""
        if len(self.files) <= 20:
            return

        index_files = [
            "INDEX.md", "index.md", "INDEX.json", "index.json",
            "TAXONOMY.md", "taxonomy.md"
        ]
        has_index = any(
            (self.knowledge_path / idx).exists() for idx in index_files
        )

        if has_index:
            self._add_result(
                "index",
                "pass",
                "Index/taxonomy file exists for large knowledge base"
            )
        else:
            self._add_result(
                "index",
                "warn",
                f"Large knowledge base ({len(self.files)} files) without index",
                "Consider adding INDEX.md or TAXONOMY.md"
            )

    def _check_archive_pattern(self):
        """Check for proper archive handling."""
        archive_files = [
            f for f in self.files
            if f.name.startswith("_ARCHIVE_") or f.name.startswith("ARCHIVED_")
        ]
        archive_dirs = [
            d for d in self.knowledge_path.iterdir()
            if d.is_dir() and d.name.lower() in ["archive", "_archive"]
        ]

        if archive_files or archive_dirs:
            self._add_result(
                "archive_pattern",
                "pass",
                f"Archive pattern in use ({len(archive_files)} files, {len(archive_dirs)} dirs)"
            )

    def _summary(self) -> Dict[str, Any]:
        """Generate audit summary."""
        passed = len([r for r in self.results if r["status"] == "pass"])
        failed = len([r for r in self.results if r["status"] == "fail"])
        warnings = len([r for r in self.results if r["status"] == "warn"])
        info = len([r for r in self.results if r["status"] == "info"])

        return {
            "path": str(self.path),
            "knowledge_path": str(self.knowledge_path),
            "instance_type": self.instance_type,
            "file_count": len(self.files),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "info": info,
            "results": self.results
        }


def audit_fleet(fleet_root: Path) -> List[Dict[str, Any]]:
    """Audit all agents in a fleet."""
    results = []

    # Directories that are NOT agent instances (core framework code)
    SKIP_DIRS = {"aget", "docs", "scripts", "validation", "tests"}

    # Find all directories with .aget/
    for agent_dir in fleet_root.iterdir():
        if not agent_dir.is_dir():
            continue
        if agent_dir.name in SKIP_DIRS:
            continue
        if (agent_dir / ".aget").exists():
            auditor = KnowledgeAuditor(agent_dir)
            results.append(auditor.audit())

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Audit knowledge/ directory content (L394, L399)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to agent directory"
    )
    parser.add_argument(
        "--fleet",
        help="Audit entire fleet at this root path"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all checks including info"
    )

    args = parser.parse_args()

    # Fleet mode
    if args.fleet:
        fleet_root = Path(args.fleet)
        if not fleet_root.exists():
            print(f"Error: Fleet root not found: {fleet_root}", file=sys.stderr)
            sys.exit(2)

        results = audit_fleet(fleet_root)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Fleet Audit: {fleet_root}")
            print("=" * 60)
            print()

            for result in results:
                agent_name = Path(result["path"]).name
                status = "PASS" if result["failed"] == 0 else "FAIL"
                print(f"{status}: {agent_name} ({result['file_count']} files, {result['warnings']} warnings)")

            print()
            print("=" * 60)
            total_failed = sum(r["failed"] for r in results)
            print(f"Total: {len(results)} agents, {total_failed} failures")

        sys.exit(1 if any(r["failed"] > 0 for r in results) else 0)

    # Single agent mode
    if not args.path:
        parser.print_help()
        sys.exit(2)

    path = Path(args.path)
    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(2)

    auditor = KnowledgeAuditor(path)
    results = auditor.audit()

    if args.json:
        print(json.dumps(results, indent=2))
        exit_code = 1 if results["failed"] > 0 else 0
        if args.strict and results["warnings"] > 0:
            exit_code = 1
        sys.exit(exit_code)

    # Human output
    print(f"Knowledge Audit: {path.name}")
    print(f"Type: {results['instance_type'] or 'unknown'}")
    print(f"Files: {results['file_count']}")
    print("=" * 60)
    print()

    for result in results["results"]:
        status = result["status"]
        message = result["message"]
        note = result.get("note", "")

        # Filter by verbosity
        if status == "info" and not args.verbose:
            continue

        if status == "pass":
            icon = "✅"
        elif status == "warn":
            icon = "⚠️"
        elif status == "fail":
            icon = "❌"
        else:
            icon = "ℹ️"

        print(f"{icon} {message}")
        if note and status != "pass":
            print(f"   {note}")

    print()
    print("=" * 60)
    print(f"PASSED: {results['passed']}")
    print(f"FAILED: {results['failed']}")
    print(f"WARNINGS: {results['warnings']}")
    if args.verbose:
        print(f"INFO: {results['info']}")

    if results["failed"] > 0:
        print()
        print("RESULT: FAIL")
        sys.exit(1)
    elif args.strict and results["warnings"] > 0:
        print()
        print("RESULT: FAIL (strict mode)")
        sys.exit(1)
    else:
        print()
        print("RESULT: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
