#!/usr/bin/env python3
"""
Validate AGET Capability Specifications.

Implements: CAP-CAP-001 (Capability_Spec_Format), CAP-VAL-002 (validator structure)
Traces to: AGET_CAPABILITY_SPEC.md, AGET_SPEC_FORMAT_v1.2.md

Validates capability specification YAML files against the Capability_Spec schema.

Usage:
    python3 validate_capability_spec.py <spec_path>
    python3 validate_capability_spec.py specs/capabilities/*.yaml
    python3 validate_capability_spec.py --all

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
"""

import argparse
import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class ValidationResult:
    """Result of validating a capability specification."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class CapabilitySpecValidator:
    """Validator for AGET capability specifications."""

    REQUIRED_TOP_LEVEL = ['apiVersion', 'kind', 'metadata', 'spec', 'behaviors']
    REQUIRED_METADATA = ['name', 'version', 'created', 'author', 'status']
    REQUIRED_SPEC = ['name', 'display_name', 'category', 'purpose']
    REQUIRED_BEHAVIOR = ['name', 'display_name', 'description', 'trigger', 'protocol', 'output']
    VALID_STATUSES = ['draft', 'review', 'approved', 'deprecated']
    VALID_ASSERTIONS = ['directory_exists', 'file_exists', 'file_contains', 'custom']

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single capability specification file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Parse YAML
        try:
            with open(file_path, 'r') as f:
                spec = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML syntax: {e}")
            return result

        if spec is None:
            result.add_error("Empty specification file")
            return result

        # Validate structure
        self._validate_top_level(spec, result)
        if not result.valid:
            return result

        self._validate_metadata(spec.get('metadata', {}), result)
        self._validate_spec_section(spec.get('spec', {}), result)
        self._validate_behaviors(spec.get('behaviors', []), result)
        self._validate_contracts(spec.get('contracts', []), result)
        self._validate_adoption(spec.get('adoption', {}), result)
        self._validate_references(spec, result, file_path)

        return result

    def _validate_top_level(self, spec: Dict, result: ValidationResult) -> None:
        """Validate top-level required fields."""
        for field in self.REQUIRED_TOP_LEVEL:
            if field not in spec:
                result.add_error(f"Missing required top-level field: {field}")

        # Check apiVersion
        if spec.get('apiVersion') != 'aget.framework/v1':
            result.add_error(f"Invalid apiVersion: expected 'aget.framework/v1', got '{spec.get('apiVersion')}'")

        # Check kind
        if spec.get('kind') != 'CapabilitySpecification':
            result.add_error(f"Invalid kind: expected 'CapabilitySpecification', got '{spec.get('kind')}'")

    def _validate_metadata(self, metadata: Dict, result: ValidationResult) -> None:
        """Validate metadata section."""
        for field in self.REQUIRED_METADATA:
            if field not in metadata:
                result.add_error(f"Missing required metadata field: {field}")

        # Validate status
        status = metadata.get('status')
        if status and status not in self.VALID_STATUSES:
            result.add_error(f"Invalid status '{status}', must be one of: {self.VALID_STATUSES}")

        # Validate name pattern
        name = metadata.get('name', '')
        if name and not self._is_valid_name(name):
            result.add_warning(f"Name '{name}' should be lowercase with hyphens (e.g., 'memory-management')")

    def _validate_spec_section(self, spec: Dict, result: ValidationResult) -> None:
        """Validate spec section."""
        for field in self.REQUIRED_SPEC:
            if field not in spec:
                result.add_error(f"Missing required spec field: {field}")

        # Check composable_with if present
        composable = spec.get('composable_with', [])
        if composable and not isinstance(composable, list):
            result.add_error("'composable_with' must be a list")

    def _validate_behaviors(self, behaviors: List, result: ValidationResult) -> None:
        """Validate behaviors section."""
        if not behaviors:
            result.add_error("At least one behavior is required")
            return

        if not isinstance(behaviors, list):
            result.add_error("'behaviors' must be a list")
            return

        behavior_names = set()
        for i, behavior in enumerate(behaviors):
            if not isinstance(behavior, dict):
                result.add_error(f"Behavior {i} must be an object")
                continue

            for field in self.REQUIRED_BEHAVIOR:
                if field not in behavior:
                    result.add_error(f"Behavior '{behavior.get('name', i)}' missing required field: {field}")

            # Check for duplicate names
            name = behavior.get('name')
            if name:
                if name in behavior_names:
                    result.add_error(f"Duplicate behavior name: {name}")
                behavior_names.add(name)

            # Validate protocol is a list
            protocol = behavior.get('protocol', [])
            if protocol and not isinstance(protocol, list):
                result.add_error(f"Behavior '{name}' protocol must be a list")

            # Validate trigger structure (can be dict with explicit/implicit or simple list)
            trigger = behavior.get('trigger', {})
            if trigger and not isinstance(trigger, (dict, list)):
                result.add_error(f"Behavior '{name}' trigger must be an object or list")

    def _validate_contracts(self, contracts: List, result: ValidationResult) -> None:
        """Validate contracts section."""
        if not contracts:
            result.add_warning("No contracts defined - consider adding validation contracts")
            return

        if not isinstance(contracts, list):
            result.add_error("'contracts' must be a list")
            return

        for contract in contracts:
            if not isinstance(contract, dict):
                result.add_error("Each contract must be an object")
                continue

            if 'name' not in contract:
                result.add_error("Contract missing required field: name")

            if 'assertion' not in contract:
                result.add_error(f"Contract '{contract.get('name')}' missing required field: assertion")
            else:
                assertion = contract.get('assertion')
                if assertion not in self.VALID_ASSERTIONS:
                    result.add_error(f"Contract '{contract.get('name')}' has invalid assertion '{assertion}', must be one of: {self.VALID_ASSERTIONS}")

    def _validate_adoption(self, adoption: Dict, result: ValidationResult) -> None:
        """Validate adoption section."""
        if not adoption:
            result.add_warning("No adoption section - consider documenting adoption roadmap")
            return

        # Check priority
        priority = adoption.get('priority')
        if priority and priority not in ['P0', 'P1', 'P2', 'P3']:
            result.add_warning(f"Non-standard priority '{priority}', expected P0-P3")

    def _validate_references(self, spec: Dict, result: ValidationResult, file_path: str) -> None:
        """Validate that referenced files exist."""
        # Check behavior references
        behaviors = spec.get('behaviors', [])
        for behavior in behaviors:
            ref = behavior.get('reference')
            if ref:
                # References are relative to agent root, not aget root
                # This is a soft check - just warn if reference looks suspicious
                if ref.startswith('/'):
                    result.add_warning(f"Behavior '{behavior.get('name')}' has absolute reference path: {ref}")

    def _is_valid_name(self, name: str) -> bool:
        """Check if name follows convention (lowercase with hyphens)."""
        import re
        return bool(re.match(r'^[a-z][a-z0-9-]*$', name))


def validate_files(paths: List[str], verbose: bool = False) -> int:
    """Validate multiple files and return exit code."""
    validator = CapabilitySpecValidator()
    all_valid = True
    results = []

    for path in paths:
        if os.path.isdir(path):
            # Find all YAML files in directory
            for yaml_file in Path(path).glob('**/*.yaml'):
                if 'CAPABILITY_SPEC' in yaml_file.name:
                    results.append(validator.validate_file(str(yaml_file)))
        else:
            results.append(validator.validate_file(path))

    # Print results
    for result in results:
        if result.valid:
            print(f"✅ {result.file_path}")
            if verbose and result.warnings:
                for warning in result.warnings:
                    print(f"   ⚠️  {warning}")
        else:
            print(f"❌ {result.file_path}")
            for error in result.errors:
                print(f"   ❌ {error}")
            if verbose:
                for warning in result.warnings:
                    print(f"   ⚠️  {warning}")
            all_valid = False

    # Summary
    valid_count = sum(1 for r in results if r.valid)
    total_count = len(results)
    print(f"\n{valid_count}/{total_count} specifications valid")

    return 0 if all_valid else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET Capability Specifications"
    )
    parser.add_argument(
        'paths',
        nargs='*',
        help="Paths to capability specification files or directories"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Validate all capability specs in default locations"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Show warnings in addition to errors"
    )

    args = parser.parse_args()

    if args.all:
        # Default locations
        paths = [
            'specs/capabilities/',
            '../private-aget-framework-AGET/specs/capabilities/',
        ]
        paths = [p for p in paths if os.path.exists(p)]
    elif args.paths:
        paths = args.paths
    else:
        parser.print_help()
        return 2

    if not paths:
        print("No valid paths found")
        return 2

    return validate_files(paths, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
