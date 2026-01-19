#!/usr/bin/env python3
"""
Validate AGET Process Specifications.

Implements: R-PROC-001 (Process_Spec_Format), CAP-VAL-002 (validator structure)
Traces to: AGET_PROCESS_SPEC.md, AGET_SPEC_FORMAT_v1.2.md

Validates Process_Specification YAML files against R-PROC requirements.
Process_Specifications define formal workflows with phases, activities,
and Decision_Points.

Usage:
    python3 validate_process_spec.py <process_spec_path>
    python3 validate_process_spec.py specs/processes/*.yaml
    python3 validate_process_spec.py --all

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
    R-PROC-002: Process Spec Validation
    R-PROC-003: Learnings Applied
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class ValidationResult:
    """Result of validating a process specification."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class ProcessSpecValidator:
    """Validator for AGET process specifications."""

    # R-PROC-001 requirements
    REQUIRED_TOP_LEVEL = ['process', 'trigger', 'phases', 'roles', 'artifacts']
    REQUIRED_PROCESS = ['id', 'name', 'version', 'status']
    REQUIRED_PHASE = ['id', 'name', 'activities']
    VALID_STATUS = ['pilot', 'draft', 'canonical', 'deprecated']

    # Phase ID pattern (R-PROC-002-03)
    PHASE_ID_PATTERN = re.compile(r'^P-\d+$')

    def __init__(self, decision_points_path: Optional[str] = None):
        self.decision_points_path = decision_points_path
        self.known_decision_points = self._load_decision_points()

    def _load_decision_points(self) -> List[str]:
        """Load known decision point documents."""
        decision_points = []
        if self.decision_points_path and os.path.exists(self.decision_points_path):
            for f in os.listdir(self.decision_points_path):
                if f.startswith('DECISION_POINT_'):
                    decision_points.append(f.replace('.md', ''))
        return decision_points

    def validate(self, file_path: str) -> ValidationResult:
        """Validate a process specification file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Check file extension
        if not file_path.endswith('.yaml') and not file_path.endswith('.yml'):
            result.add_error(f"Process specs must be YAML format (.yaml or .yml)")
            return result

        # Load YAML
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML: {e}")
            return result

        if not data:
            result.add_error("Empty specification file")
            return result

        # Validate structure
        self._validate_top_level(data, result)
        if 'process' in data:
            self._validate_process_section(data['process'], result)
        if 'phases' in data:
            self._validate_phases(data['phases'], result)
        if 'roles' in data:
            self._validate_roles(data['roles'], result)
        if 'learnings_applied' in data:
            self._validate_learnings(data['learnings_applied'], result)

        return result

    def _validate_top_level(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate required top-level sections exist."""
        for section in self.REQUIRED_TOP_LEVEL:
            if section not in data:
                result.add_error(f"Missing required section: {section}")

    def _validate_process_section(self, process: Dict[str, Any], result: ValidationResult) -> None:
        """Validate process metadata section."""
        # R-PROC-001-02 through R-PROC-001-05
        for field_name in self.REQUIRED_PROCESS:
            if field_name not in process:
                result.add_error(f"Missing required process field: {field_name}")

        # R-PROC-001-03: process_id pattern
        if 'id' in process:
            process_id = process['id']
            if not re.match(r'^[a-z][a-z0-9-]*$', process_id):
                result.add_error(f"Process ID must match pattern ^[a-z][a-z0-9-]*$, got: {process_id}")

        # R-PROC-001-05: status validation
        if 'status' in process:
            if process['status'] not in self.VALID_STATUS:
                result.add_error(f"Invalid status '{process['status']}'. Must be one of: {self.VALID_STATUS}")

    def _validate_phases(self, phases: List[Dict[str, Any]], result: ValidationResult) -> None:
        """Validate phases array."""
        if not phases:
            result.add_error("Phases array is empty")
            return

        phase_ids = set()

        for i, phase in enumerate(phases):
            if not isinstance(phase, dict):
                result.add_error(f"Phase {i} is not a dictionary")
                continue

            # R-PROC-001-07: Each phase has id, name, activities
            for field_name in self.REQUIRED_PHASE:
                if field_name not in phase:
                    result.add_error(f"Phase {i}: Missing required field: {field_name}")

            # R-PROC-002-03: Gate IDs follow pattern P-N
            if 'id' in phase:
                phase_id = phase['id']
                if not self.PHASE_ID_PATTERN.match(phase_id):
                    result.add_error(f"Phase ID must match pattern P-N, got: {phase_id}")

                # Check for duplicates
                if phase_id in phase_ids:
                    result.add_error(f"Duplicate phase ID: {phase_id}")
                phase_ids.add(phase_id)

            # Validate activities is a list
            if 'activities' in phase:
                if not isinstance(phase['activities'], list):
                    result.add_error(f"Phase {phase.get('id', i)}: activities must be a list")

            # R-PROC-002-04: Validate decision_point.next_on_go references valid phase
            if 'decision_point' in phase and phase['decision_point']:
                dp = phase['decision_point']
                if isinstance(dp, dict):
                    if 'next_on_go' in dp:
                        next_phase = dp['next_on_go']
                        if next_phase not in [p.get('id') for p in phases] and next_phase != 'COMPLETE':
                            result.add_warning(f"Phase {phase.get('id')}: decision_point.next_on_go references unknown phase: {next_phase}")

    def _validate_roles(self, roles: List[Dict[str, Any]], result: ValidationResult) -> None:
        """Validate roles array."""
        if not roles:
            result.add_warning("Roles array is empty")
            return

        for i, role in enumerate(roles):
            if not isinstance(role, dict):
                result.add_error(f"Role {i} is not a dictionary")
                continue

            if 'id' not in role:
                result.add_error(f"Role {i}: Missing required field: id")
            if 'name' not in role:
                result.add_error(f"Role {i}: Missing required field: name")
            if 'responsibilities' not in role:
                result.add_warning(f"Role {role.get('id', i)}: No responsibilities defined")

    def _validate_learnings(self, learnings: List[Dict[str, Any]], result: ValidationResult) -> None:
        """Validate learnings_applied section (R-PROC-003)."""
        if not learnings:
            result.add_warning("No learnings_applied - consider documenting applied learnings")
            return

        for i, learning in enumerate(learnings):
            if not isinstance(learning, dict):
                result.add_error(f"Learning {i} is not a dictionary")
                continue

            # R-PROC-003-02: Each learning has id
            if 'id' not in learning:
                result.add_error(f"Learning {i}: Missing required field: id (L-doc reference)")

            # R-PROC-003-03: Each learning has summary
            if 'summary' not in learning:
                result.add_error(f"Learning {learning.get('id', i)}: Missing required field: summary")

            # R-PROC-003-04: Each learning has change
            if 'change' not in learning:
                result.add_warning(f"Learning {learning.get('id', i)}: No change description")


def format_result(result: ValidationResult) -> str:
    """Format a validation result for output."""
    lines = []

    if result.valid:
        status = "PASS"
        symbol = "✅"
    else:
        status = "FAIL"
        symbol = "❌"

    lines.append(f"{symbol} {result.file_path} - {status}")

    for error in result.errors:
        lines.append(f"  ❌ ERROR: {error}")

    for warning in result.warnings:
        lines.append(f"  ⚠️  WARN: {warning}")

    return "\n".join(lines)


def find_process_specs(base_path: str) -> List[str]:
    """Find all process spec files."""
    specs = []
    processes_dir = os.path.join(base_path, 'specs', 'processes')

    if os.path.exists(processes_dir):
        for f in os.listdir(processes_dir):
            if f.startswith('PROCESS_') and (f.endswith('.yaml') or f.endswith('.yml')):
                specs.append(os.path.join(processes_dir, f))

    return specs


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Process Specifications')
    parser.add_argument('paths', nargs='*', help='Paths to process spec files')
    parser.add_argument('--all', action='store_true', help='Validate all process specs in framework')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    validator = ProcessSpecValidator()
    results: List[ValidationResult] = []

    if args.all:
        # Find aget directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)  # Go up from validation/
        specs = find_process_specs(base_path)

        if not specs:
            print("No process specs found in specs/processes/")
            return 2

        for spec_path in specs:
            results.append(validator.validate(spec_path))

    elif args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.endswith('.yaml') or f.endswith('.yml'):
                        results.append(validator.validate(os.path.join(path, f)))
            else:
                print(f"Path not found: {path}")
                return 2
    else:
        parser.print_help()
        return 2

    # Output results
    all_valid = True
    for result in results:
        if not args.quiet or not result.valid:
            print(format_result(result))
        if not result.valid:
            all_valid = False

    # Summary
    passed = sum(1 for r in results if r.valid)
    total = len(results)
    print(f"\n{'✅' if all_valid else '❌'} {passed}/{total} process specifications valid")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
