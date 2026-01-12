#!/usr/bin/env python3
"""
Validate AGET PROJECT_PLANs.

Implements: CAP-PLAN-001 (Project_Plan_Format), L382 (Verification_Tests), CAP-VAL-002
Traces to: AGET_PLANNING_SPEC.md, AGET_FILE_NAMING_CONVENTIONS.md
Updated: L515 (Template Coherence Gap), #233 (Gate Naming Convention)

Validates Project_Plan documents for proper Project_Gate structure, deliverables,
Decision_Points, and Verification_Tests (L382).

Gate Naming Conventions Supported (#233):
    - Sequential: ## G-0:, ## G-1:, ## G-2: (simple linear, <10 gates)
    - Hierarchical: ## Gate 0:, ## Gate 1:, ## Gate 1.1: (multi-phase, 10+ gates)
    - Track-prefixed: ## S-1:, ## W-1: (parallel tracks)

Usage:
    python3 validate_project_plan.py <plan_path>
    python3 validate_project_plan.py planning/*.md
    python3 validate_project_plan.py --dir /path/to/agent
    python3 validate_project_plan.py --strict  # Require Verification_Tests + Closure Checklist

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

L382 Requirements:
    - Each Project_Gate SHOULD have a Verification_Tests section
    - Tests SHOULD be executable (bash/python commands)
    - Tests SHOULD have expected output patterns

L515/247 Requirements (--strict mode):
    - Plans marked COMPLETE SHOULD have Closure Checklist
    - Plans marked COMPLETE SHOULD have Retrospective section
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ValidationResult:
    """Result of validating a PROJECT_PLAN."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class ProjectPlanValidator:
    """Validator for AGET PROJECT_PLANs."""

    # Required sections
    REQUIRED_SECTIONS = [
        'Executive Summary',
        'Gate Structure',
    ]

    # Recommended sections
    RECOMMENDED_SECTIONS = [
        'Success Criteria',
        'Risk Assessment',
        'Rollback',
    ]

    # Gate patterns - supports multiple naming conventions (#233, L515)
    # Sequential: ## G-0:, ## G-1:
    # Hierarchical: ## Gate 0:, ## Gate 1:, ## Gate 1.1:
    # Track-prefixed: ## S-1:, ## W-1:
    GATE_PATTERNS = [
        re.compile(r'^##\s+G-(\d+):', re.MULTILINE),  # G-0:, G-1:
        re.compile(r'^##\s+Gate\s+(\d+):', re.MULTILINE),  # Gate 0:, Gate 1:
        re.compile(r'^##\s+Gate\s+(\d+)\.(\d+):', re.MULTILINE),  # Gate 1.1:
        re.compile(r'^##\s+([A-Z])-(\d+):', re.MULTILINE),  # S-1:, W-1:
    ]
    GATE_FULL_PATTERNS = [
        re.compile(r'^##\s+G-\d+:.*$', re.MULTILINE),
        re.compile(r'^##\s+Gate\s+\d+:.*$', re.MULTILINE),
        re.compile(r'^##\s+Gate\s+\d+\.\d+:.*$', re.MULTILINE),
        re.compile(r'^##\s+[A-Z]-\d+:.*$', re.MULTILINE),
    ]
    # Legacy pattern for backward compatibility
    GATE_HEADER_PATTERN = re.compile(r'^##\s+G-(\d+):', re.MULTILINE)
    GATE_FULL_PATTERN = re.compile(r'^##\s+G-\d+:.*$', re.MULTILINE)

    # Decision point pattern
    DECISION_POINT_PATTERN = re.compile(r'\*\*(GO|NOGO|Decision|Decision Point)\*\*', re.IGNORECASE)
    GONOGO_PATTERN = re.compile(r'GO.*NOGO|NOGO.*GO', re.IGNORECASE)

    # Verification test patterns (L382)
    VERIFICATION_TESTS_PATTERN = re.compile(r'\*\*Verification Tests\*\*', re.IGNORECASE)
    CODE_BLOCK_PATTERN = re.compile(r'```(?:bash|python|shell)?\n(.*?)```', re.DOTALL)
    EXPECTED_PATTERN = re.compile(r'#\s*Expected:', re.IGNORECASE)

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: If True, missing verification tests are errors, not warnings.
        """
        self.strict = strict

    def validate(self, file_path: str) -> ValidationResult:
        """Validate a PROJECT_PLAN file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Check file naming
        filename = os.path.basename(file_path)
        if not filename.startswith('PROJECT_PLAN'):
            result.add_warning(f"File should start with 'PROJECT_PLAN': {filename}")

        # Read file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        # Validate structure
        self._validate_header(content, result)
        self._validate_required_sections(content, result)
        self._validate_recommended_sections(content, result)
        self._validate_gates(content, result)
        self._validate_decision_points(content, result)
        self._validate_deliverables(content, result)
        self._validate_verification_tests(content, result)
        self._validate_closure(content, result)  # L515/#247

        return result

    def _validate_header(self, content: str, result: ValidationResult) -> None:
        """Validate plan header metadata."""
        # Check for title
        if not content.startswith('#'):
            result.add_error("Plan must start with # title")
            return

        # Check for key metadata
        required_meta = ['Version', 'Date', 'Owner', 'Status']
        for meta in required_meta:
            pattern = rf'\*\*{meta}\*\*:'
            if not re.search(pattern, content[:2000], re.IGNORECASE):
                result.add_warning(f"Missing recommended metadata: **{meta}**:")

    def _validate_required_sections(self, content: str, result: ValidationResult) -> None:
        """Validate required sections exist."""
        for section in self.REQUIRED_SECTIONS:
            # Special case: "Gate Structure" is satisfied by having actual gates
            if section == 'Gate Structure':
                gate_numbers, _, _ = self._find_gates(content)
                if gate_numbers:
                    continue  # Gates found, requirement satisfied
                # Also accept literal "Gate Structure" section
                if 'gate structure' in content.lower():
                    continue

            pattern = rf'^##\s+.*{re.escape(section)}.*$'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                # Try without exact match
                if section.lower() not in content.lower():
                    result.add_error(f"Missing required section: {section}")

    def _validate_recommended_sections(self, content: str, result: ValidationResult) -> None:
        """Check for recommended sections."""
        for section in self.RECOMMENDED_SECTIONS:
            if section.lower() not in content.lower():
                result.add_warning(f"Missing recommended section: {section}")

    def _find_gates(self, content: str) -> tuple:
        """Find gates using any supported naming convention (#233).

        Returns:
            Tuple of (gate_numbers, gate_matches, convention_name)
        """
        # Try each pattern, use first one that matches
        conventions = [
            ('G-N', self.GATE_PATTERNS[0], self.GATE_FULL_PATTERNS[0]),
            ('Gate N', self.GATE_PATTERNS[1], self.GATE_FULL_PATTERNS[1]),
            ('Gate N.M', self.GATE_PATTERNS[2], self.GATE_FULL_PATTERNS[2]),
            ('Track-N', self.GATE_PATTERNS[3], self.GATE_FULL_PATTERNS[3]),
        ]

        for name, header_pattern, full_pattern in conventions:
            matches = header_pattern.findall(content)
            if matches:
                full_matches = list(full_pattern.finditer(content))
                # Extract gate numbers (handle tuples from multi-group patterns)
                if matches and isinstance(matches[0], tuple):
                    gate_numbers = [int(m[0]) for m in matches]
                else:
                    gate_numbers = [int(m) for m in matches]
                return gate_numbers, full_matches, name

        return [], [], None

    def _validate_gates(self, content: str, result: ValidationResult) -> None:
        """Validate gate structure (supports multiple naming conventions per #233)."""
        gate_numbers, gate_matches, convention = self._find_gates(content)

        if not gate_numbers:
            result.add_error("No gates found (expected ## G-N:, ## Gate N:, or ## {Track}-N: format)")
            return

        # Should start with 0 or 1
        if gate_numbers[0] not in [0, 1]:
            result.add_warning(f"Gates typically start at 0 or 1, found {gate_numbers[0]}")

        # Check for gaps (only for sequential patterns)
        if convention in ('G-N', 'Gate N'):
            for i in range(1, len(gate_numbers)):
                expected = gate_numbers[i-1] + 1
                if gate_numbers[i] != expected and gate_numbers[i] != gate_numbers[i-1]:
                    result.add_warning(f"Gate numbering gap: {gate_numbers[i-1]} to {gate_numbers[i]}")

        # Check each gate has content
        for i, match in enumerate(gate_matches):
            gate_start = match.end()
            gate_end = gate_matches[i+1].start() if i+1 < len(gate_matches) else len(content)
            gate_content = content[gate_start:gate_end]
            gate_name = match.group().strip()[:30]  # Truncate for display

            # Check for Objective
            if 'objective' not in gate_content.lower():
                result.add_warning(f"{gate_name}...: Missing **Objective**")

            # Check for Deliverables
            if 'deliverable' not in gate_content.lower():
                result.add_warning(f"{gate_name}...: Missing Deliverables section")

    def _validate_decision_points(self, content: str, result: ValidationResult) -> None:
        """Validate decision points in gates."""
        _, gate_matches, _ = self._find_gates(content)

        for i, match in enumerate(gate_matches):
            gate_start = match.end()
            gate_end = gate_matches[i+1].start() if i+1 < len(gate_matches) else len(content)
            gate_content = content[gate_start:gate_end]
            gate_name = match.group().strip()[:30]

            # Check for GO/NOGO decision point
            has_decision = (
                self.DECISION_POINT_PATTERN.search(gate_content) or
                self.GONOGO_PATTERN.search(gate_content) or
                '**GO**' in gate_content or
                'Decision Point' in gate_content
            )

            if not has_decision:
                result.add_warning(f"{gate_name}...: Missing GO/NOGO decision point")

    def _validate_deliverables(self, content: str, result: ValidationResult) -> None:
        """Validate deliverables tables or lists."""
        # Look for deliverables tables
        table_pattern = re.compile(r'\|\s*#\s*\|\s*Deliverable', re.IGNORECASE)
        list_pattern = re.compile(r'^\d+\.\s+', re.MULTILINE)
        checkbox_pattern = re.compile(r'^\s*-\s*\[[ x]\]', re.MULTILINE)

        has_table = table_pattern.search(content)
        has_list = list_pattern.search(content)
        has_checkbox = checkbox_pattern.search(content)

        if not (has_table or has_list or has_checkbox):
            result.add_warning("No structured deliverables found (tables, numbered lists, or checklists)")

    def _validate_verification_tests(self, content: str, result: ValidationResult) -> None:
        """Validate verification tests in gates (L382)."""
        _, gate_matches, _ = self._find_gates(content)

        if not gate_matches:
            return  # Already reported in _validate_gates

        gates_without_tests = []
        gates_without_expected = []

        for i, match in enumerate(gate_matches):
            gate_start = match.end()
            gate_end = gate_matches[i+1].start() if i+1 < len(gate_matches) else len(content)
            gate_content = content[gate_start:gate_end]
            gate_name = match.group().strip()[:20]

            # Check for Verification Tests section
            has_tests = self.VERIFICATION_TESTS_PATTERN.search(gate_content)

            if not has_tests:
                gates_without_tests.append(gate_name)
            else:
                # Check for code blocks with tests
                code_blocks = self.CODE_BLOCK_PATTERN.findall(gate_content)
                if not code_blocks:
                    gates_without_tests.append(gate_name)
                else:
                    # Check for Expected: comments
                    has_expected = self.EXPECTED_PATTERN.search(gate_content)
                    if not has_expected:
                        gates_without_expected.append(gate_name)

        # Report findings
        if gates_without_tests:
            msg = f"L382: Gates missing Verification Tests: {', '.join(gates_without_tests)}"
            if self.strict:
                result.add_error(msg)
            else:
                result.add_warning(msg)

        if gates_without_expected:
            msg = f"L382: Gates with tests but no Expected: comments: {', '.join(gates_without_expected)}"
            result.add_warning(msg)

        # Summary
        total_gates = len(gate_matches)
        gates_with_tests = total_gates - len(gates_without_tests)
        if gates_with_tests < total_gates:
            coverage = f"{gates_with_tests}/{total_gates}"
            result.add_warning(f"L382: Verification test coverage: {coverage} gates")

    def _validate_closure(self, content: str, result: ValidationResult) -> None:
        """Validate closure checklist for COMPLETE plans (L515, #247).

        Only enforced in --strict mode.
        """
        if not self.strict:
            return

        # Check if plan is marked COMPLETE
        status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', content, re.IGNORECASE)
        if not status_match:
            return  # Can't determine status

        status = status_match.group(1).upper()
        if 'COMPLETE' not in status:
            return  # Not complete, no closure check needed

        # Plan is COMPLETE - check for closure checklist
        has_closure = bool(re.search(r'(Project\s+)?Closure\s+Checklist', content, re.IGNORECASE))
        has_retrospective = bool(re.search(r'Retrospective|What\s+Went\s+Well', content, re.IGNORECASE))

        if not has_closure:
            result.add_warning("L515/#247: Plan marked COMPLETE but missing Closure Checklist")

        if not has_retrospective:
            result.add_warning("L515/#247: Plan marked COMPLETE but missing Retrospective section")


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


def find_project_plans(base_path: str) -> List[str]:
    """Find all PROJECT_PLAN files."""
    plans = []
    planning_dir = os.path.join(base_path, 'planning')

    if os.path.exists(planning_dir):
        for f in os.listdir(planning_dir):
            if f.startswith('PROJECT_PLAN') and f.endswith('.md'):
                plans.append(os.path.join(planning_dir, f))

    return sorted(plans)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET PROJECT_PLANs')
    parser.add_argument('paths', nargs='*', help='Paths to PROJECT_PLAN files')
    parser.add_argument('--dir', help='Agent directory to search for plans')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode: require V-tests (L382), check closure checklist (L515/#247)')

    args = parser.parse_args()

    validator = ProjectPlanValidator(strict=args.strict)
    results: List[ValidationResult] = []

    if args.dir:
        plans = find_project_plans(args.dir)
        if not plans:
            print(f"No PROJECT_PLANs found in {args.dir}/planning/")
            return 2
        for plan_path in plans:
            results.append(validator.validate(plan_path))

    elif args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.startswith('PROJECT_PLAN') and f.endswith('.md'):
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
    print(f"\n{'✅' if all_valid else '❌'} {passed}/{total} PROJECT_PLANs valid")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
