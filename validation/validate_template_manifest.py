#!/usr/bin/env python3
"""
Validate AGET Template Manifests

Validates template manifest YAML files against the TEMPLATE_MANIFEST schema.
Template manifests declare agent composition (base template + capabilities).

Usage:
    python3 validate_template_manifest.py <manifest_path>
    python3 validate_template_manifest.py manifests/*.yaml
    python3 validate_template_manifest.py --all

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
    """Result of validating a template manifest."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class TemplateManifestValidator:
    """Validator for AGET template manifests."""

    REQUIRED_TOP_LEVEL = ['apiVersion', 'kind', 'metadata', 'composition']
    REQUIRED_METADATA = ['name', 'version', 'agent_type']
    REQUIRED_COMPOSITION = ['base_template', 'capabilities']
    VALID_BASE_TEMPLATES = ['worker', 'advisor', 'supervisor', 'consultant', 'developer', 'spec-engineer']
    VALID_CONFLICT_RESOLUTION = ['first-wins', 'last-wins', 'merge', 'error']

    def __init__(self, capability_specs_path: Optional[str] = None):
        self.capability_specs_path = capability_specs_path
        self.known_capabilities = self._load_known_capabilities()

    def _load_known_capabilities(self) -> Dict[str, str]:
        """Load known capability names from specs."""
        capabilities = {}
        if self.capability_specs_path and os.path.exists(self.capability_specs_path):
            for yaml_file in Path(self.capability_specs_path).glob('*.yaml'):
                try:
                    with open(yaml_file, 'r') as f:
                        spec = yaml.safe_load(f)
                    name = spec.get('metadata', {}).get('name')
                    version = spec.get('metadata', {}).get('version')
                    if name:
                        capabilities[name] = version
                except:
                    pass
        return capabilities

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single template manifest file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Parse YAML
        try:
            with open(file_path, 'r') as f:
                manifest = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML syntax: {e}")
            return result

        if manifest is None:
            result.add_error("Empty manifest file")
            return result

        # Validate structure
        self._validate_top_level(manifest, result)
        if not result.valid:
            return result

        self._validate_metadata(manifest.get('metadata', {}), result)
        self._validate_composition(manifest.get('composition', {}), result)
        self._validate_capabilities(manifest.get('composition', {}).get('capabilities', []), result)

        return result

    def _validate_top_level(self, manifest: Dict, result: ValidationResult) -> None:
        """Validate top-level required fields."""
        for field in self.REQUIRED_TOP_LEVEL:
            if field not in manifest:
                result.add_error(f"Missing required top-level field: {field}")

        # Check apiVersion
        if manifest.get('apiVersion') != 'aget.framework/v1':
            result.add_error(f"Invalid apiVersion: expected 'aget.framework/v1', got '{manifest.get('apiVersion')}'")

        # Check kind
        if manifest.get('kind') != 'TemplateManifest':
            result.add_error(f"Invalid kind: expected 'TemplateManifest', got '{manifest.get('kind')}'")

    def _validate_metadata(self, metadata: Dict, result: ValidationResult) -> None:
        """Validate metadata section."""
        for field in self.REQUIRED_METADATA:
            if field not in metadata:
                result.add_error(f"Missing required metadata field: {field}")

    def _validate_composition(self, composition: Dict, result: ValidationResult) -> None:
        """Validate composition section."""
        for field in self.REQUIRED_COMPOSITION:
            if field not in composition:
                result.add_error(f"Missing required composition field: {field}")

        # Validate base_template
        base_template = composition.get('base_template')
        if base_template and base_template not in self.VALID_BASE_TEMPLATES:
            result.add_error(f"Invalid base_template '{base_template}', must be one of: {self.VALID_BASE_TEMPLATES}")

        # Validate composition_rules if present
        rules = composition.get('composition_rules', {})
        if rules:
            conflict_resolution = rules.get('conflict_resolution')
            if conflict_resolution and conflict_resolution not in self.VALID_CONFLICT_RESOLUTION:
                result.add_error(f"Invalid conflict_resolution '{conflict_resolution}', must be one of: {self.VALID_CONFLICT_RESOLUTION}")

    def _validate_capabilities(self, capabilities: List, result: ValidationResult) -> None:
        """Validate capabilities list."""
        if not capabilities:
            result.add_warning("No capabilities defined - manifest has only base template")
            return

        if not isinstance(capabilities, list):
            result.add_error("'capabilities' must be a list")
            return

        capability_names = set()
        for cap in capabilities:
            if not isinstance(cap, dict):
                result.add_error("Each capability must be an object with 'name' and 'version'")
                continue

            name = cap.get('name')
            version = cap.get('version')

            if not name:
                result.add_error("Capability missing required field: name")
                continue

            if not version:
                result.add_error(f"Capability '{name}' missing required field: version")

            # Check for duplicates
            if name in capability_names:
                result.add_error(f"Duplicate capability: {name}")
            capability_names.add(name)

            # Check if capability is known
            if self.known_capabilities and name not in self.known_capabilities:
                result.add_warning(f"Unknown capability '{name}' - not found in capability specs")
            elif self.known_capabilities and name in self.known_capabilities:
                known_version = self.known_capabilities[name]
                if version != known_version:
                    result.add_warning(f"Capability '{name}' version mismatch: manifest has {version}, spec has {known_version}")


def validate_files(paths: List[str], capability_specs_path: Optional[str] = None, verbose: bool = False) -> int:
    """Validate multiple files and return exit code."""
    validator = TemplateManifestValidator(capability_specs_path)
    all_valid = True
    results = []

    for path in paths:
        if os.path.isdir(path):
            for yaml_file in Path(path).glob('**/*.yaml'):
                if 'manifest' in yaml_file.name.lower() or yaml_file.parent.name == 'manifests':
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
    print(f"\n{valid_count}/{total_count} manifests valid")

    return 0 if all_valid else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET Template Manifests"
    )
    parser.add_argument(
        'paths',
        nargs='*',
        help="Paths to template manifest files or directories"
    )
    parser.add_argument(
        '--capability-specs',
        help="Path to capability specifications for cross-validation"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Show warnings in addition to errors"
    )

    args = parser.parse_args()

    if not args.paths:
        parser.print_help()
        return 2

    return validate_files(args.paths, args.capability_specs, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
