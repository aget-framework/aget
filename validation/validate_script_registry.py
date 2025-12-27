#!/usr/bin/env python3
"""
Validate AGET Script Registry

Validates SCRIPT_REGISTRY.yaml for completeness and correctness.
Checks that registered scripts exist and unregistered scripts are flagged.

Usage:
    python3 validate_script_registry.py <registry_path>
    python3 validate_script_registry.py SCRIPT_REGISTRY.yaml
    python3 validate_script_registry.py --check-files

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

See: specs/AGET_PYTHON_SCRIPT_SPEC.md (R-SCRIPT-006)
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set, Optional
import yaml


@dataclass
class ValidationResult:
    """Result of validating the script registry."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class ScriptRegistryValidator:
    """Validator for AGET Script Registry."""

    # Required top-level fields
    REQUIRED_FIELDS = ['version', 'scripts']

    # Required script entry fields
    REQUIRED_SCRIPT_FIELDS = ['path', 'description', 'category']

    # Valid categories
    VALID_CATEGORIES = ['validator', 'tool', 'test', 'pattern']

    # Patterns for finding scripts
    SCRIPT_PATTERNS = [
        'validation/*.py',
        'tools/*.py',
    ]

    # Exclusions
    EXCLUDED_PATTERNS = [
        '__pycache__',
        '__init__.py',
        'test_*.py',
        'tests/',
    ]

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.getcwd()

    def validate(self, registry_path: str, check_files: bool = False) -> ValidationResult:
        """Validate a script registry file."""
        result = ValidationResult(file_path=registry_path, valid=True)

        # Check file exists
        if not os.path.exists(registry_path):
            result.add_error(f"Registry file not found: {registry_path}")
            return result

        # Load YAML
        try:
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML: {e}")
            return result

        if not registry:
            result.add_error("Registry is empty")
            return result

        # Validate structure
        self._validate_required_fields(registry, result)
        self._validate_scripts(registry.get('scripts', []), result)

        if check_files:
            self._validate_file_existence(registry.get('scripts', []), result)
            self._check_unregistered_scripts(registry.get('scripts', []), result)

        # Validate summary if present
        if 'summary' in registry:
            self._validate_summary(registry, result)

        return result

    def _validate_required_fields(self, registry: dict, result: ValidationResult) -> None:
        """Validate required top-level fields."""
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in registry:
                result.add_error(f"Missing required field: {field_name}")

    def _validate_scripts(self, scripts: List[dict], result: ValidationResult) -> None:
        """Validate script entries."""
        if not scripts:
            result.add_error("No scripts registered")
            return

        paths_seen = set()

        for i, script in enumerate(scripts):
            if not isinstance(script, dict):
                result.add_error(f"Script entry {i} is not a dictionary")
                continue

            # Check required fields
            for field_name in self.REQUIRED_SCRIPT_FIELDS:
                if field_name not in script:
                    path = script.get('path', f'entry {i}')
                    result.add_error(f"Script '{path}': Missing required field '{field_name}'")

            # Validate path format
            path = script.get('path', '')
            if path:
                if not path.endswith('.py'):
                    result.add_warning(f"Script '{path}': Path should end with .py")

                # Check for duplicates
                if path in paths_seen:
                    result.add_error(f"Duplicate script path: {path}")
                paths_seen.add(path)

            # Validate category
            category = script.get('category', '')
            if category and category not in self.VALID_CATEGORIES:
                result.add_warning(f"Script '{path}': Unknown category '{category}'")

            # Validate exit_codes if present
            exit_codes = script.get('exit_codes', [])
            if exit_codes:
                for code in exit_codes:
                    if not isinstance(code, int) or code < 0 or code > 255:
                        result.add_warning(f"Script '{path}': Invalid exit code {code}")

    def _validate_file_existence(self, scripts: List[dict], result: ValidationResult) -> None:
        """Check that registered scripts exist on disk."""
        for script in scripts:
            path = script.get('path', '')
            location = script.get('location', 'framework')

            # Skip pattern scripts (they're in agent repos, not framework)
            if location == 'agent_repo':
                continue

            full_path = os.path.join(self.base_path, path)
            if not os.path.exists(full_path):
                result.add_error(f"Registered script not found: {path}")

    def _check_unregistered_scripts(self, scripts: List[dict], result: ValidationResult) -> None:
        """Check for scripts that exist but aren't registered."""
        registered_paths = {s.get('path', '') for s in scripts}

        # Find all Python files in validation/
        validation_dir = os.path.join(self.base_path, 'validation')
        if os.path.exists(validation_dir):
            for f in os.listdir(validation_dir):
                if f.endswith('.py') and not f.startswith('__'):
                    rel_path = f'validation/{f}'
                    if rel_path not in registered_paths:
                        result.add_warning(f"Unregistered script: {rel_path}")

        # Find all Python files in tools/ (if exists)
        tools_dir = os.path.join(self.base_path, 'tools')
        if os.path.exists(tools_dir):
            for f in os.listdir(tools_dir):
                if f.endswith('.py') and not f.startswith('__'):
                    rel_path = f'tools/{f}'
                    if rel_path not in registered_paths:
                        result.add_warning(f"Unregistered script: {rel_path}")

    def _validate_summary(self, registry: dict, result: ValidationResult) -> None:
        """Validate summary statistics match actual counts."""
        scripts = registry.get('scripts', [])
        summary = registry.get('summary', {})

        # Check total count
        actual_total = len(scripts)
        declared_total = summary.get('total_scripts', 0)
        if actual_total != declared_total:
            result.add_warning(
                f"Summary mismatch: declared {declared_total} scripts, found {actual_total}"
            )

        # Check category counts
        by_category = summary.get('by_category', {})
        actual_counts = {}
        for script in scripts:
            cat = script.get('category', 'unknown')
            actual_counts[cat] = actual_counts.get(cat, 0) + 1

        for cat, declared_count in by_category.items():
            actual_count = actual_counts.get(cat, 0)
            if actual_count != declared_count:
                result.add_warning(
                    f"Category '{cat}' mismatch: declared {declared_count}, found {actual_count}"
                )


def format_result(result: ValidationResult) -> str:
    """Format a validation result for output."""
    lines = []

    if result.valid and not result.warnings:
        status = "PASS"
        symbol = "✅"
    elif result.valid:
        status = "WARN"
        symbol = "⚠️"
    else:
        status = "FAIL"
        symbol = "❌"

    lines.append(f"{symbol} {result.file_path} - {status}")

    for error in result.errors:
        lines.append(f"  ❌ ERROR: {error}")

    for warning in result.warnings:
        lines.append(f"  ⚠️  WARN: {warning}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Script Registry')
    parser.add_argument('path', nargs='?', default='SCRIPT_REGISTRY.yaml',
                        help='Path to registry file')
    parser.add_argument('--check-files', action='store_true',
                        help='Check that registered scripts exist')
    parser.add_argument('--base-path', help='Base path for file checks')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show errors')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    base_path = args.base_path
    if not base_path:
        # Infer base path from registry location
        base_path = os.path.dirname(os.path.abspath(args.path))
        if base_path.endswith('/validation'):
            base_path = os.path.dirname(base_path)

    validator = ScriptRegistryValidator(base_path=base_path)
    result = validator.validate(args.path, check_files=args.check_files)

    if not args.quiet or not result.valid or result.warnings:
        print(format_result(result))

    # Summary
    scripts_count = 0
    try:
        with open(args.path, 'r') as f:
            registry = yaml.safe_load(f)
            scripts_count = len(registry.get('scripts', []))
    except:
        pass

    if result.valid:
        print(f"\n✅ Registry valid ({scripts_count} scripts)")
    else:
        print(f"\n❌ Registry invalid")

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
