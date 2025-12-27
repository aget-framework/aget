#!/usr/bin/env python3
"""
Validate Composition References

Validates that $ref: references in template manifests point to existing
components or files. Part of AGET v3.0.0 Component Library validation.

Usage:
    python3 validate_composition_refs.py <template_path>
    python3 validate_composition_refs.py --all

Exit codes:
    0: All references valid
    1: Invalid references found
    2: Error during validation
"""

import argparse
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class CompositionRefValidator:
    """Validates $ref: references in template manifests."""

    def __init__(self, framework_root: Optional[str] = None):
        """Initialize validator with framework root path."""
        self.framework_root = Path(framework_root) if framework_root else self._find_framework_root()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validated_refs: List[str] = []

    def _find_framework_root(self) -> Path:
        """Find the aget-framework root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "aget" / "specs").exists():
                return current
            # Check if we're in a template directory
            if current.name.startswith("template-") and (current / "manifest.yaml").exists():
                return current.parent
            current = current.parent
        return Path.cwd()

    def validate_template(self, template_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all $ref: references in a template manifest.

        Args:
            template_path: Path to template directory

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.validated_refs = []

        manifest_path = template_path / "manifest.yaml"
        if not manifest_path.exists():
            self.errors.append(f"Manifest not found: {manifest_path}")
            return False, self.errors, self.warnings

        try:
            with open(manifest_path, 'r') as f:
                content = f.read()
                manifest = yaml.safe_load(content)
        except Exception as e:
            self.errors.append(f"Failed to parse manifest: {e}")
            return False, self.errors, self.warnings

        # Find all $ref: patterns in the raw content
        # Pattern handles quoted refs: "$ref: path" or unquoted: $ref: path
        ref_pattern = r'\$ref:\s*([^\n\r"]+)'
        matches = re.findall(ref_pattern, content)

        for ref in matches:
            ref = ref.strip().rstrip('"')  # Remove trailing quote if present
            self._validate_ref(ref, template_path)

        # Validate capabilities list
        if manifest and 'capabilities' in manifest:
            self._validate_capabilities(manifest['capabilities'])

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_ref(self, ref: str, template_path: Path) -> None:
        """Validate a single $ref: reference."""
        # Handle different ref formats
        if ref.startswith('.aget/'):
            # Relative to template directory
            full_path = template_path / ref
            if not full_path.exists():
                self.errors.append(f"Missing local reference: {ref}")
            else:
                self.validated_refs.append(ref)

        elif ref.startswith('aget/components/'):
            # Framework component reference
            full_path = self.framework_root / ref
            if not full_path.exists():
                self.errors.append(f"Missing component: {ref}")
            else:
                self.validated_refs.append(ref)

        elif ref.startswith('./'):
            # Relative path
            full_path = template_path / ref[2:]
            if not full_path.exists():
                self.errors.append(f"Missing local reference: {ref}")
            else:
                self.validated_refs.append(ref)

        else:
            # Treat as relative to template
            full_path = template_path / ref
            if not full_path.exists():
                # Try framework root
                framework_path = self.framework_root / ref
                if not framework_path.exists():
                    self.warnings.append(f"Unresolved reference: {ref}")
                else:
                    self.validated_refs.append(ref)
            else:
                self.validated_refs.append(ref)

    def _validate_capabilities(self, capabilities: List[str]) -> None:
        """Validate that declared capabilities exist as components."""
        components_dir = self.framework_root / "aget" / "components"

        for cap in capabilities:
            # Look for capability in any subdirectory
            found = False
            for subdir in components_dir.rglob(f"{cap}.yaml"):
                found = True
                break

            if not found:
                # Check governance, core, and archetype directories
                for category in ['governance', 'core']:
                    cap_path = components_dir / category / f"{cap}.yaml"
                    if cap_path.exists():
                        found = True
                        break

                if not found:
                    archetype_dir = components_dir / "archetype"
                    if archetype_dir.exists():
                        for arch_subdir in archetype_dir.iterdir():
                            if arch_subdir.is_dir():
                                cap_path = arch_subdir / f"{cap}.yaml"
                                if cap_path.exists():
                                    found = True
                                    break

            if not found:
                # Not an error, just a warning - capability may be defined inline
                self.warnings.append(f"Capability component not found: {cap}")

    def validate_all_templates(self) -> Tuple[bool, Dict[str, Tuple[List[str], List[str]]]]:
        """
        Validate all templates in the framework.

        Returns:
            Tuple of (all_valid, {template: (errors, warnings)})
        """
        results = {}
        all_valid = True

        for template_dir in self.framework_root.iterdir():
            if template_dir.is_dir() and template_dir.name.startswith("template-"):
                is_valid, errors, warnings = self.validate_template(template_dir)
                if not is_valid:
                    all_valid = False
                results[template_dir.name] = (errors, warnings)

        return all_valid, results


def main():
    parser = argparse.ArgumentParser(
        description="Validate $ref: references in template manifests"
    )
    parser.add_argument(
        "template_path",
        nargs="?",
        help="Path to template directory"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all templates in framework"
    )
    parser.add_argument(
        "--framework-root",
        help="Path to aget-framework root"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    validator = CompositionRefValidator(args.framework_root)

    if args.all:
        all_valid, results = validator.validate_all_templates()

        print("=" * 60)
        print("AGET Composition Reference Validation")
        print("=" * 60)

        for template, (errors, warnings) in sorted(results.items()):
            status = "✅" if not errors else "❌"
            print(f"\n{status} {template}")

            if errors:
                for error in errors:
                    print(f"   ERROR: {error}")
            if warnings and args.verbose:
                for warning in warnings:
                    print(f"   WARN:  {warning}")

        print("\n" + "=" * 60)
        if all_valid:
            print("✅ All templates passed composition reference validation")
            sys.exit(0)
        else:
            print("❌ Some templates have invalid references")
            sys.exit(1)

    elif args.template_path:
        template_path = Path(args.template_path)
        if not template_path.is_absolute():
            template_path = Path.cwd() / template_path

        is_valid, errors, warnings = validator.validate_template(template_path)

        print(f"Validating: {template_path.name}")
        print("-" * 40)

        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  ❌ {error}")

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  ⚠️  {warning}")

        if validator.validated_refs and args.verbose:
            print("\nValidated references:")
            for ref in validator.validated_refs:
                print(f"  ✅ {ref}")

        print()
        if is_valid:
            print("✅ All composition references valid")
            sys.exit(0)
        else:
            print("❌ Invalid composition references found")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
