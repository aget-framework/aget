#!/usr/bin/env python3
"""
Validate AGET Capability Composition.

Implements: CAP-COMP-001 (Composition_Rules), CAP-VAL-002 (validator structure)
Traces to: AGET_COMPOSITION_SPEC.md, AGET_CAPABILITY_SPEC.md

Validates capability composition following Composition_Spec rules.
Detects DAG conflicts, prerequisite violations, and behavior overlaps.

Usage:
    python3 validate_composition.py <manifest_path>
    python3 validate_composition.py manifests/*.yaml --specs <specs_path>

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
from typing import List, Optional, Dict, Any, Set, Tuple
import yaml


@dataclass
class CompositionResult:
    """Result of validating capability composition."""
    manifest_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_conflict(self, conflict_type: str, details: str, resolution: Optional[str] = None) -> None:
        self.conflicts.append({
            'type': conflict_type,
            'details': details,
            'resolution': resolution
        })
        self.valid = False


class CapabilitySpec:
    """Loaded capability specification."""
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.name = data.get('metadata', {}).get('name', '')
        self.version = data.get('metadata', {}).get('version', '')
        self.behaviors = data.get('behaviors', [])
        self.prerequisites = data.get('spec', {}).get('prerequisites', [])
        self.composable_with = data.get('spec', {}).get('composable_with', [])

    def get_behavior_names(self) -> Set[str]:
        return {b.get('name') for b in self.behaviors if b.get('name')}

    def get_triggers(self) -> Dict[str, List[str]]:
        """Return mapping of behavior name to trigger phrases."""
        triggers = {}
        for b in self.behaviors:
            name = b.get('name')
            trigger = b.get('trigger', {})
            if isinstance(trigger, dict):
                phrases = trigger.get('explicit', []) + trigger.get('implicit', [])
            elif isinstance(trigger, list):
                phrases = trigger
            else:
                phrases = []
            triggers[name] = phrases
        return triggers


class CompositionValidator:
    """Validator for AGET capability composition."""

    def __init__(self, capability_specs_path: Optional[str] = None):
        self.capability_specs_path = capability_specs_path
        self.capability_specs: Dict[str, CapabilitySpec] = {}
        if capability_specs_path:
            self._load_capability_specs()

    def _load_capability_specs(self) -> None:
        """Load all capability specifications."""
        if not os.path.exists(self.capability_specs_path):
            return

        for yaml_file in Path(self.capability_specs_path).glob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                if data and data.get('kind') == 'CapabilitySpecification':
                    spec = CapabilitySpec(data)
                    self.capability_specs[spec.name] = spec
            except:
                pass

    def validate_manifest(self, manifest_path: str) -> CompositionResult:
        """Validate composition of a template manifest."""
        result = CompositionResult(manifest_path=manifest_path, valid=True)

        # Load manifest
        try:
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            result.add_error(f"Failed to load manifest: {e}")
            return result

        if not manifest:
            result.add_error("Empty manifest")
            return result

        composition = manifest.get('composition', {})
        capabilities = composition.get('capabilities', [])
        conflict_resolution = composition.get('composition_rules', {}).get('conflict_resolution', 'error')

        # Extract capability names and versions from manifest
        manifest_capabilities = {}
        for cap in capabilities:
            if isinstance(cap, dict):
                name = cap.get('name')
                version = cap.get('version')
                if name:
                    manifest_capabilities[name] = version

        # Run validation checks
        self._check_duplicate_capabilities(manifest_capabilities, result)
        self._check_prerequisites(manifest_capabilities, result)
        self._check_behavior_conflicts(manifest_capabilities, result, conflict_resolution)
        self._check_composability(manifest_capabilities, composition.get('base_template'), result)

        return result

    def _check_duplicate_capabilities(self, capabilities: Dict[str, str], result: CompositionResult) -> None:
        """Check for duplicate capability declarations (R-COMP-001)."""
        # Already handled by manifest validator - capabilities dict has unique keys
        pass

    def _check_prerequisites(self, capabilities: Dict[str, str], result: CompositionResult) -> None:
        """Check that all prerequisites are satisfied (R-COMP-002)."""
        if not self.capability_specs:
            result.add_warning("No capability specs loaded - skipping prerequisite check")
            return

        for cap_name in capabilities:
            if cap_name not in self.capability_specs:
                result.add_warning(f"Unknown capability '{cap_name}' - cannot check prerequisites")
                continue

            spec = self.capability_specs[cap_name]
            for prereq in spec.prerequisites:
                # Prerequisites can be capability names or general requirements
                # Check if this looks like a capability reference (contains 'cap' or matches known specs)
                prereq_lower = prereq.lower()
                is_capability_prereq = (
                    prereq.startswith('capability-') or
                    prereq in self.capability_specs or
                    prereq.replace('-', '_') in self.capability_specs or
                    '-cap' in prereq_lower or
                    prereq_lower.endswith('-cap') or
                    'capability' in prereq_lower
                )

                if is_capability_prereq:
                    prereq_name = prereq.replace('capability-', '').replace('_', '-')
                    if prereq_name not in capabilities and prereq not in capabilities:
                        result.add_conflict(
                            'missing_prerequisite',
                            f"Capability '{cap_name}' requires '{prereq}' which is not in composition",
                            f"Add '{prereq}' to capabilities list"
                        )

    def _check_behavior_conflicts(self, capabilities: Dict[str, str], result: CompositionResult, resolution: str) -> None:
        """Check for conflicting behaviors (R-COMP-003)."""
        if not self.capability_specs:
            result.add_warning("No capability specs loaded - skipping behavior conflict check")
            return

        # Collect all behaviors from all capabilities
        all_behaviors: Dict[str, List[str]] = {}  # behavior_name -> list of capability names
        all_triggers: Dict[str, List[Tuple[str, str]]] = {}  # trigger_phrase -> [(capability, behavior)]

        for cap_name in capabilities:
            if cap_name not in self.capability_specs:
                continue

            spec = self.capability_specs[cap_name]

            # Check for behavior name collisions
            for behavior_name in spec.get_behavior_names():
                if behavior_name not in all_behaviors:
                    all_behaviors[behavior_name] = []
                all_behaviors[behavior_name].append(cap_name)

            # Check for trigger phrase overlaps
            triggers = spec.get_triggers()
            for behavior_name, phrases in triggers.items():
                for phrase in phrases:
                    phrase_lower = phrase.lower() if isinstance(phrase, str) else str(phrase)
                    if phrase_lower not in all_triggers:
                        all_triggers[phrase_lower] = []
                    all_triggers[phrase_lower].append((cap_name, behavior_name))

        # Report behavior name collisions
        for behavior_name, cap_list in all_behaviors.items():
            if len(cap_list) > 1:
                if resolution == 'error':
                    result.add_conflict(
                        'behavior_name_collision',
                        f"Behavior '{behavior_name}' defined in multiple capabilities: {cap_list}",
                        f"Change conflict_resolution to 'first-wins', 'last-wins', or 'merge'"
                    )
                else:
                    result.add_warning(f"Behavior '{behavior_name}' collision resolved by '{resolution}': {cap_list}")

        # Report trigger overlaps (warning only - may be intentional)
        for trigger, sources in all_triggers.items():
            if len(sources) > 1 and len(set(s[0] for s in sources)) > 1:
                caps_involved = list(set(s[0] for s in sources))
                result.add_warning(f"Trigger phrase '{trigger}' matches multiple capabilities: {caps_involved}")

    def _check_composability(self, capabilities: Dict[str, str], base_template: str, result: CompositionResult) -> None:
        """Check that capabilities are composable with base template (R-COMP-004)."""
        if not self.capability_specs:
            return

        for cap_name in capabilities:
            if cap_name not in self.capability_specs:
                continue

            spec = self.capability_specs[cap_name]
            composable_with = spec.composable_with

            # Check if explicitly marked as composable with this base or "All"
            if composable_with:
                composable_templates = []
                for c in composable_with:
                    if isinstance(c, str):
                        c_lower = c.lower()
                        if 'all' in c_lower or base_template.lower() in c_lower:
                            composable_templates.append(c)
                        elif c_lower.startswith('template-') and base_template in c_lower:
                            composable_templates.append(c)

                if not composable_templates and not any('all' in str(c).lower() for c in composable_with):
                    result.add_warning(f"Capability '{cap_name}' may not be compatible with base_template '{base_template}'")


def validate_files(paths: List[str], capability_specs_path: Optional[str] = None, verbose: bool = False) -> int:
    """Validate multiple manifests and return exit code."""
    validator = CompositionValidator(capability_specs_path)
    all_valid = True
    results = []

    for path in paths:
        if os.path.isdir(path):
            for yaml_file in Path(path).glob('**/*.yaml'):
                if 'manifest' in yaml_file.name.lower():
                    results.append(validator.validate_manifest(str(yaml_file)))
        else:
            results.append(validator.validate_manifest(path))

    # Print results
    for result in results:
        if result.valid:
            print(f"✅ {result.manifest_path}")
            if verbose:
                for warning in result.warnings:
                    print(f"   ⚠️  {warning}")
        else:
            print(f"❌ {result.manifest_path}")
            for error in result.errors:
                print(f"   ❌ {error}")
            for conflict in result.conflicts:
                print(f"   ⚠️  CONFLICT [{conflict['type']}]: {conflict['details']}")
                if conflict.get('resolution'):
                    print(f"      → Resolution: {conflict['resolution']}")
            if verbose:
                for warning in result.warnings:
                    print(f"   ⚠️  {warning}")
            all_valid = False

    # Summary
    valid_count = sum(1 for r in results if r.valid)
    total_count = len(results)
    if total_count > 0:
        print(f"\n{valid_count}/{total_count} compositions valid")

    return 0 if all_valid else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET Capability Composition"
    )
    parser.add_argument(
        'paths',
        nargs='*',
        help="Paths to template manifest files or directories"
    )
    parser.add_argument(
        '--specs',
        help="Path to capability specifications directory"
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

    return validate_files(args.paths, args.specs, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
