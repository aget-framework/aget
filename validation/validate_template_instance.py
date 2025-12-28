#!/usr/bin/env python3
"""
Validate Template or Instance

Template-aware validator that applies appropriate checks based on instance_type.
Templates have different requirements than deployed agent instances.

Part of AGET v3.0.0-beta.3 - Template UX improvements (L391).

Usage:
    python3 validate_template_instance.py <path>
    python3 validate_template_instance.py <path> --strict  # Fail on warnings
    python3 validate_template_instance.py <path> --json    # JSON output

Exit codes:
    0: All checks pass
    1: Failures detected
    2: Invalid arguments
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class TemplateInstanceValidator:
    """Validates templates and instances with appropriate checks."""

    def __init__(self, path: Path):
        self.path = path
        self.aget_path = path / ".aget"
        self.version_file = self.aget_path / "version.json"
        self.instance_type: Optional[str] = None
        self.results: List[Dict[str, Any]] = []

    def detect_type(self) -> Tuple[Optional[str], Optional[str]]:
        """Detect if path is template or instance."""
        if not self.version_file.exists():
            return None, "No .aget/version.json found"

        try:
            with open(self.version_file) as f:
                data = json.load(f)
            self.instance_type = data.get("instance_type")
            return self.instance_type, None
        except json.JSONDecodeError as e:
            return None, f"Invalid version.json: {e}"

    def validate(self) -> Dict[str, Any]:
        """Run validation checks based on instance type."""
        self.results = []

        # Detect type first
        instance_type, error = self.detect_type()
        if error:
            return {
                "path": str(self.path),
                "instance_type": None,
                "error": error,
                "passed": 0,
                "failed": 1,
                "warnings": 0,
                "results": []
            }

        # Run common checks
        self._check_common()

        # Run type-specific checks
        if instance_type == "template":
            self._check_template()
        elif instance_type == "aget":
            self._check_instance()
        else:
            self._add_result(
                "instance_type_valid",
                "fail",
                f"Unknown instance_type: '{instance_type}' (expected: 'template' or 'aget')"
            )

        # Summarize
        passed = len([r for r in self.results if r["status"] == "pass"])
        failed = len([r for r in self.results if r["status"] == "fail"])
        warnings = len([r for r in self.results if r["status"] == "warn"])

        return {
            "path": str(self.path),
            "instance_type": instance_type,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "results": self.results
        }

    def _add_result(self, check: str, status: str, message: str, note: str = ""):
        """Add a validation result."""
        self.results.append({
            "check": check,
            "status": status,
            "message": message,
            "note": note
        })

    def _check_common(self):
        """Checks applicable to both templates and instances."""
        # Check .aget/ exists
        if self.aget_path.exists():
            self._add_result(
                "aget_directory",
                "pass",
                ".aget/ directory exists"
            )
        else:
            self._add_result(
                "aget_directory",
                "fail",
                ".aget/ directory missing"
            )
            return

        # Check version.json
        if self.version_file.exists():
            self._add_result(
                "version_json",
                "pass",
                ".aget/version.json exists"
            )
        else:
            self._add_result(
                "version_json",
                "fail",
                ".aget/version.json missing"
            )

        # Check identity.json
        identity_file = self.aget_path / "identity.json"
        if identity_file.exists():
            self._add_result(
                "identity_json",
                "pass",
                ".aget/identity.json exists"
            )
        else:
            self._add_result(
                "identity_json",
                "fail",
                ".aget/identity.json missing"
            )

        # Check 5D directories
        dimensions = ["persona", "memory", "reasoning", "skills", "context"]
        for dim in dimensions:
            dim_path = self.aget_path / dim
            if dim_path.exists():
                self._add_result(
                    f"dimension_{dim}",
                    "pass",
                    f".aget/{dim}/ exists"
                )
            else:
                self._add_result(
                    f"dimension_{dim}",
                    "fail",
                    f".aget/{dim}/ missing"
                )

        # Check governance directory
        gov_path = self.path / "governance"
        if gov_path.exists():
            self._add_result(
                "governance_dir",
                "pass",
                "governance/ exists"
            )

            # Check governance files
            for gov_file in ["CHARTER.md", "MISSION.md", "SCOPE_BOUNDARIES.md"]:
                if (gov_path / gov_file).exists():
                    self._add_result(
                        f"governance_{gov_file}",
                        "pass",
                        f"governance/{gov_file} exists"
                    )
                else:
                    self._add_result(
                        f"governance_{gov_file}",
                        "fail",
                        f"governance/{gov_file} missing"
                    )
        else:
            self._add_result(
                "governance_dir",
                "fail",
                "governance/ missing"
            )

        # Check manifest.yaml
        manifest_file = self.path / "manifest.yaml"
        if manifest_file.exists():
            self._add_result(
                "manifest_yaml",
                "pass",
                "manifest.yaml exists"
            )
        else:
            self._add_result(
                "manifest_yaml",
                "fail",
                "manifest.yaml missing"
            )

    def _check_template(self):
        """Template-specific checks."""
        self._add_result(
            "instance_type",
            "pass",
            "Detected as TEMPLATE",
            "Applying template-specific validation"
        )

        # Templates should NOT have session content
        sessions_path = self.path / "sessions"
        if sessions_path.exists():
            session_files = list(sessions_path.glob("*.md"))
            if len(session_files) > 1:  # Allow README
                self._add_result(
                    "template_no_sessions",
                    "warn",
                    f"Template has {len(session_files)} session files",
                    "Templates should not have session content"
                )
            else:
                self._add_result(
                    "template_no_sessions",
                    "pass",
                    "No session content (correct for template)"
                )

        # Templates should have minimal L-docs
        evolution_path = self.aget_path / "evolution"
        if evolution_path.exists():
            ldocs = list(evolution_path.glob("L*.md"))
            if len(ldocs) > 10:
                self._add_result(
                    "template_minimal_ldocs",
                    "warn",
                    f"Template has {len(ldocs)} L-docs",
                    "Templates typically have few L-docs"
                )
            else:
                self._add_result(
                    "template_minimal_ldocs",
                    "pass",
                    f"Reasonable L-doc count: {len(ldocs)}"
                )

        # Templates should NOT have archive (cleaned up)
        archive_path = self.aget_path / "archive"
        if archive_path.exists():
            self._add_result(
                "template_no_archive",
                "warn",
                ".aget/archive/ exists",
                "Consider running cleanup_template_archive.py"
            )
        else:
            self._add_result(
                "template_no_archive",
                "pass",
                "No archive directory (clean template)"
            )

        # Templates should NOT have framework code
        framework_dirs = ["aget", "docs"]  # Old cruft
        for dir_name in framework_dirs:
            if (self.path / dir_name).exists():
                self._add_result(
                    f"template_no_{dir_name}",
                    "fail",
                    f"{dir_name}/ exists in template",
                    "Framework code should not be in templates"
                )

        # Check README mentions template
        readme_path = self.path / "README.md"
        if readme_path.exists():
            with open(readme_path) as f:
                content = f.read().lower()
            if "template" in content:
                self._add_result(
                    "template_readme",
                    "pass",
                    "README mentions 'template'"
                )
            else:
                self._add_result(
                    "template_readme",
                    "warn",
                    "README doesn't mention 'template'",
                    "Consider documenting template usage"
                )

    def _check_instance(self):
        """Instance-specific checks."""
        self._add_result(
            "instance_type",
            "pass",
            "Detected as INSTANCE (aget)",
            "Applying instance-specific validation"
        )

        # Instances should have agent_name
        try:
            with open(self.version_file) as f:
                data = json.load(f)
            if data.get("agent_name"):
                self._add_result(
                    "instance_agent_name",
                    "pass",
                    f"Agent name: {data['agent_name']}"
                )
            else:
                self._add_result(
                    "instance_agent_name",
                    "warn",
                    "No agent_name in version.json"
                )
        except Exception:
            pass

        # Instances should have L-docs (learning accumulation)
        evolution_path = self.aget_path / "evolution"
        if evolution_path.exists():
            ldocs = list(evolution_path.glob("L*.md"))
            if len(ldocs) > 0:
                self._add_result(
                    "instance_has_ldocs",
                    "pass",
                    f"Instance has {len(ldocs)} L-docs"
                )

                # Check for index if over threshold
                if len(ldocs) > 50:
                    index_file = evolution_path / "index.json"
                    if index_file.exists():
                        self._add_result(
                            "instance_ldoc_index",
                            "pass",
                            "L-doc index.json exists (required for 50+ L-docs)"
                        )
                    else:
                        self._add_result(
                            "instance_ldoc_index",
                            "warn",
                            f"{len(ldocs)} L-docs but no index.json",
                            "Run generate_ldoc_index.py"
                        )
            else:
                self._add_result(
                    "instance_has_ldocs",
                    "warn",
                    "Instance has no L-docs yet"
                )

        # Instances should have planning directory
        planning_path = self.path / "planning"
        if planning_path.exists():
            self._add_result(
                "instance_planning",
                "pass",
                "planning/ exists"
            )
        else:
            self._add_result(
                "instance_planning",
                "warn",
                "planning/ missing",
                "Instances typically have planning artifacts"
            )

        # Instances may have sessions
        sessions_path = self.path / "sessions"
        if sessions_path.exists():
            session_files = list(sessions_path.glob("*.md"))
            self._add_result(
                "instance_sessions",
                "pass",
                f"sessions/ exists ({len(session_files)} files)"
            )

        # Check visible content directories (v3.1 requirement)
        core_visible = ["governance", "planning"]
        for dir_name in core_visible:
            if (self.path / dir_name).exists():
                pass  # Already checked
            else:
                self._add_result(
                    f"instance_visible_{dir_name}",
                    "warn",
                    f"Core visible directory {dir_name}/ missing"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Template-aware AGET validator (L391)"
    )
    parser.add_argument(
        "path",
        help="Path to template or agent directory"
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
        help="Show all checks (not just failures)"
    )

    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(2)

    validator = TemplateInstanceValidator(path)
    results = validator.validate()

    # JSON output
    if args.json:
        print(json.dumps(results, indent=2))
        exit_code = 1 if results["failed"] > 0 else 0
        if args.strict and results["warnings"] > 0:
            exit_code = 1
        sys.exit(exit_code)

    # Human output
    print(f"Validating: {path.name}")
    print(f"Type: {results['instance_type'] or 'unknown'}")
    print("=" * 60)
    print()

    # Group results by status
    for result in results["results"]:
        status = result["status"]
        check = result["check"]
        message = result["message"]
        note = result.get("note", "")

        # Determine what to show
        show = args.verbose or status in ["fail", "warn"]

        if show:
            if status == "pass":
                icon = "✅"
            elif status == "warn":
                icon = "⚠️"
            else:
                icon = "❌"

            print(f"{icon} {message}")
            if note and (status != "pass" or args.verbose):
                print(f"   {note}")

    # Summary
    print()
    print("=" * 60)
    print(f"PASSED: {results['passed']}")
    print(f"FAILED: {results['failed']}")
    print(f"WARNINGS: {results['warnings']}")

    if results["failed"] > 0:
        print()
        print("RESULT: FAIL")
        sys.exit(1)
    elif args.strict and results["warnings"] > 0:
        print()
        print("RESULT: FAIL (strict mode, warnings present)")
        sys.exit(1)
    else:
        print()
        print("RESULT: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
