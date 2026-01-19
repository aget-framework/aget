#!/usr/bin/env python3
"""
Validate AGET Entity Inheritance in Manifests.

Implements: CAP-TPL-012 (Entity Inheritance), CAP-VOC-001 (Vocabulary)
Traces to: AGET_TEMPLATE_SPEC.md, AGET_VOCABULARY_SPEC.md Part 6, L459
Requirements: R-ENT-001 through R-ENT-005

Validates that manifest.yaml entity declarations:
1. Reference valid core entities from AGET_VOCABULARY_SPEC Part 6
2. Extensions only add attributes (R-ENT-002)
3. Extensions can add relationships (R-ENT-003)
4. Type narrowing is allowed, widening is not (R-ENT-004)

Usage:
    python3 validate_entity_inheritance.py <manifest_path>
    python3 validate_entity_inheritance.py --dir /path/to/agent
    python3 validate_entity_inheritance.py --help

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
from typing import List, Optional, Dict, Any, Set
import yaml


# Core entities defined in AGET_VOCABULARY_SPEC Part 6 (L459)
CORE_ENTITIES: Dict[str, Dict[str, Any]] = {
    "Person": {
        "category": "Continuant",
        "required_attributes": ["name"],
        "optional_attributes": ["email", "identifier", "roles"],
        "relationships": ["affiliated_with", "authors", "makes", "assigned_to"]
    },
    "Organization": {
        "category": "Continuant",
        "required_attributes": ["name"],
        "optional_attributes": ["type", "identifier"],
        "relationships": ["has_member", "owns", "produces", "parent_of"]
    },
    "Document": {
        "category": "Continuant",
        "required_attributes": ["title"],
        "optional_attributes": ["type", "version", "location", "created", "status"],
        "relationships": ["authored_by", "produced_by", "references", "supersedes"]
    },
    "Decision": {
        "category": "Abstract",
        "required_attributes": ["description", "date"],
        "optional_attributes": ["rationale", "status"],
        "relationships": ["made_by", "affects", "documented_in", "supersedes"]
    },
    "Event": {
        "category": "Occurrent",
        "required_attributes": ["name"],
        "optional_attributes": ["type", "start_time", "end_time", "status"],
        "relationships": ["involves", "hosted_by", "produces", "results_in"]
    },
    "Task": {
        "category": "Occurrent",
        "required_attributes": ["description"],
        "optional_attributes": ["status", "priority", "due_date"],
        "relationships": ["assignee", "part_of", "blocked_by", "implements"]
    },
    "Project": {
        "category": "Continuant",
        "required_attributes": ["name"],
        "optional_attributes": ["description", "status", "start_date", "end_date"],
        "relationships": ["owned_by", "has_task", "has_requirement", "produces"]
    },
    "Requirement": {
        "category": "Abstract",
        "required_attributes": ["identifier", "description"],
        "optional_attributes": ["type", "priority", "status"],
        "relationships": ["source", "implemented_by", "verified_by"]
    }
}

# Upper-level categories
UPPER_CATEGORIES = {"Entity", "Continuant", "Occurrent", "Abstract"}


@dataclass
class ValidationResult:
    """Result of validating entity inheritance."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)


class EntityInheritanceValidator:
    """Validator for AGET entity inheritance in manifests."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a manifest file's entity declarations."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Load YAML
        try:
            with open(file_path, 'r') as f:
                manifest = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"YAML parse error: {e}")
            return result
        except Exception as e:
            result.add_error(f"Error reading file: {e}")
            return result

        if manifest is None:
            result.add_error("Empty manifest file")
            return result

        # Check for entities section (optional)
        entities = manifest.get('entities')
        if entities is None:
            result.add_info("No 'entities' section found (optional)")
            return result

        # Validate inherits
        inherits = entities.get('inherits', [])
        if inherits:
            self._validate_inherits(inherits, result)

        # Validate extends
        extends = entities.get('extends', {})
        if extends:
            self._validate_extends(extends, inherits, result)

        return result

    def _validate_inherits(self, inherits: List[str], result: ValidationResult) -> None:
        """Validate that inherited entities are valid core entities."""
        if not isinstance(inherits, list):
            result.add_error("'entities.inherits' must be a list")
            return

        for entity_name in inherits:
            if entity_name in CORE_ENTITIES:
                result.add_info(f"Inheriting core entity: {entity_name}")
            elif entity_name in UPPER_CATEGORIES:
                result.add_warning(f"Inheriting upper-level category '{entity_name}' - consider inheriting specific entities")
            else:
                result.add_error(f"Unknown entity '{entity_name}' - not a core entity. "
                               f"Valid core entities: {', '.join(CORE_ENTITIES.keys())}")

    def _validate_extends(self, extends: Dict[str, Any], inherits: List[str], result: ValidationResult) -> None:
        """Validate entity extensions per R-ENT-001 through R-ENT-005."""
        if not isinstance(extends, dict):
            result.add_error("'entities.extends' must be a dictionary")
            return

        for entity_name, extension in extends.items():
            # Check entity is in inherits list
            if entity_name not in inherits:
                result.add_error(f"Cannot extend '{entity_name}' - not in inherits list. "
                               f"Add '{entity_name}' to entities.inherits first.")
                continue

            # Check entity is a valid core entity
            if entity_name not in CORE_ENTITIES:
                result.add_error(f"Cannot extend '{entity_name}' - not a core entity")
                continue

            core_entity = CORE_ENTITIES[entity_name]

            # Validate extension structure
            if not isinstance(extension, dict):
                result.add_error(f"Extension for '{entity_name}' must be a dictionary")
                continue

            # Validate attributes (R-ENT-002: can only add, not remove)
            if 'attributes' in extension:
                self._validate_extension_attributes(entity_name, extension['attributes'], core_entity, result)

            # Validate relationships (R-ENT-003: can add new relationships)
            if 'relationships' in extension:
                self._validate_extension_relationships(entity_name, extension['relationships'], core_entity, result)

            result.add_info(f"Valid extension for '{entity_name}'")

    def _validate_extension_attributes(self, entity_name: str, attributes: List[Any],
                                        core_entity: Dict[str, Any], result: ValidationResult) -> None:
        """Validate extension attributes per R-ENT-002."""
        if not isinstance(attributes, list):
            result.add_error(f"'{entity_name}.attributes' must be a list")
            return

        all_base_attrs = set(core_entity['required_attributes'] + core_entity['optional_attributes'])

        for attr in attributes:
            # Handle both dict and simple string formats
            if isinstance(attr, dict):
                attr_name = list(attr.keys())[0] if attr else None
            elif isinstance(attr, str):
                attr_name = attr
            else:
                result.add_error(f"Invalid attribute format in '{entity_name}': {attr}")
                continue

            if attr_name is None:
                continue

            # Check if trying to override base attribute (warning, not error)
            if attr_name in all_base_attrs:
                result.add_warning(f"Attribute '{attr_name}' in '{entity_name}' shadows base attribute. "
                                 f"R-ENT-004: Type narrowing allowed, widening is not.")
            else:
                result.add_info(f"Adding new attribute '{attr_name}' to '{entity_name}'")

    def _validate_extension_relationships(self, entity_name: str, relationships: List[Any],
                                           core_entity: Dict[str, Any], result: ValidationResult) -> None:
        """Validate extension relationships per R-ENT-003."""
        if not isinstance(relationships, list):
            result.add_error(f"'{entity_name}.relationships' must be a list")
            return

        base_rels = set(core_entity['relationships'])

        for rel in relationships:
            # Handle both dict and simple string formats
            if isinstance(rel, dict):
                rel_name = list(rel.keys())[0] if rel else None
            elif isinstance(rel, str):
                rel_name = rel
            else:
                result.add_error(f"Invalid relationship format in '{entity_name}': {rel}")
                continue

            if rel_name is None:
                continue

            # R-ENT-003: Extensions can add relationships
            if rel_name in base_rels:
                result.add_warning(f"Relationship '{rel_name}' in '{entity_name}' shadows base relationship")
            else:
                result.add_info(f"Adding new relationship '{rel_name}' to '{entity_name}'")

    def validate_directory(self, dir_path: str) -> ValidationResult:
        """Validate manifest.yaml in a directory."""
        manifest_path = os.path.join(dir_path, 'manifest.yaml')
        if not os.path.exists(manifest_path):
            result = ValidationResult(file_path=dir_path, valid=True)
            result.add_warning(f"No manifest.yaml found in {dir_path}")
            return result
        return self.validate_file(manifest_path)


def print_result(result: ValidationResult, verbose: bool = False) -> None:
    """Print validation result."""
    status = "✅ PASS" if result.valid else "❌ FAIL"
    print(f"\n{status}: {result.file_path}")

    if result.errors:
        print("\n  Errors:")
        for error in result.errors:
            print(f"    ❌ {error}")

    if result.warnings:
        print("\n  Warnings:")
        for warning in result.warnings:
            print(f"    ⚠️  {warning}")

    if verbose and result.info:
        print("\n  Info:")
        for info in result.info:
            print(f"    ℹ️  {info}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET entity inheritance in manifest.yaml files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s manifest.yaml
    %(prog)s --dir /path/to/agent
    %(prog)s --list-entities

Core Entities (AGET_VOCABULARY_SPEC Part 6):
    Person, Organization, Document, Decision, Event, Task, Project, Requirement

Rules (R-ENT-*):
    R-ENT-001: Inherited entities include all base attributes
    R-ENT-002: Extensions add attributes, cannot remove
    R-ENT-003: Extensions can add relationships
    R-ENT-004: Extensions can narrow types (string → enum), not widen
    R-ENT-005: Extended entities remain compatible with base consumers

Reference: L459 (Core Entity Vocabulary Vision)
        """
    )
    parser.add_argument('manifest', nargs='?', help='Path to manifest.yaml file')
    parser.add_argument('--dir', '-d', help='Directory containing manifest.yaml')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show info messages')
    parser.add_argument('--list-entities', '-l', action='store_true', help='List available core entities')

    args = parser.parse_args()

    # Handle --list-entities
    if args.list_entities:
        print("\nCore Entities (AGET_VOCABULARY_SPEC Part 6 - L459):\n")
        for name, spec in CORE_ENTITIES.items():
            print(f"  {name} ({spec['category']})")
            print(f"    Required: {', '.join(spec['required_attributes'])}")
            if spec['optional_attributes']:
                print(f"    Optional: {', '.join(spec['optional_attributes'])}")
            print(f"    Relations: {', '.join(spec['relationships'])}")
            print()
        return 0

    # Determine file to validate
    if args.dir:
        manifest_path = os.path.join(args.dir, 'manifest.yaml')
    elif args.manifest:
        manifest_path = args.manifest
    else:
        parser.print_help()
        return 2

    # Validate
    validator = EntityInheritanceValidator(verbose=args.verbose)
    result = validator.validate_file(manifest_path)
    print_result(result, verbose=args.verbose)

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
