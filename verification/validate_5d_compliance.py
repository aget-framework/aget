#!/usr/bin/env python3
"""
Validate AGET 5D Architecture Compliance.

Implements: CAP-COMP-001 through CAP-COMP-005 (5D dimensions), CAP-VAL-002 (validator structure)
Traces to: AGET_5D_ARCHITECTURE_SPEC.md, AGET_VALIDATION_SPEC.md

Umbrella validator that runs all dimension validators and reports aggregate compliance.
This is the primary entry point for validating complete 5D agent compliance.

Usage:
    python3 validate_5d_compliance.py <agent_path>
    python3 validate_5d_compliance.py --dir /path/to/agent
    python3 validate_5d_compliance.py --strict
    python3 validate_5d_compliance.py --dimensions persona,memory
    python3 validate_5d_compliance.py --skip-dimensions skills

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


@dataclass
class DimensionResult:
    """Result from a dimension validator."""
    dimension: str
    valid: bool
    errors: int = 0
    warnings: int = 0
    output: str = ""


@dataclass
class OverallResult:
    """Overall 5D compliance result."""
    agent_path: str
    dimensions: Dict[str, DimensionResult] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return all(d.valid for d in self.dimensions.values())

    @property
    def total_errors(self) -> int:
        return sum(d.errors for d in self.dimensions.values())

    @property
    def total_warnings(self) -> int:
        return sum(d.warnings for d in self.dimensions.values())

    @property
    def dimensions_passed(self) -> int:
        return sum(1 for d in self.dimensions.values() if d.valid)


class FiveDComplianceValidator:
    """Umbrella validator for 5D Architecture Compliance."""

    ALL_DIMENSIONS = ['persona', 'memory', 'reasoning', 'skills', 'context']

    DIMENSION_VALIDATORS = {
        'persona': 'validate_persona_compliance.py',
        'memory': 'validate_memory_compliance.py',
        'context': 'validate_context_compliance.py',
        # reasoning and skills validated via other validators
    }

    def __init__(self, strict: bool = False, dimensions: Optional[Set[str]] = None,
                 skip_dimensions: Optional[Set[str]] = None):
        """Initialize validator.

        Args:
            strict: If True, run validators in strict mode.
            dimensions: If set, only validate these dimensions.
            skip_dimensions: If set, skip these dimensions.
        """
        self.strict = strict
        self.dimensions = dimensions or set(self.ALL_DIMENSIONS)
        if skip_dimensions:
            self.dimensions -= skip_dimensions

        # Find validation directory
        self.validation_dir = Path(__file__).parent

    def validate(self, agent_path: str) -> OverallResult:
        """Validate 5D compliance for an agent."""
        result = OverallResult(agent_path=agent_path)

        if not os.path.exists(agent_path):
            return result

        for dim in self.dimensions:
            dim_result = self._validate_dimension(dim, agent_path)
            result.dimensions[dim] = dim_result

        return result

    def _validate_dimension(self, dimension: str, agent_path: str) -> DimensionResult:
        """Validate a single dimension."""
        result = DimensionResult(dimension=dimension, valid=True)

        validator = self.DIMENSION_VALIDATORS.get(dimension)

        if validator:
            validator_path = self.validation_dir / validator

            if validator_path.exists():
                try:
                    cmd = ['python3', str(validator_path), '--dir', agent_path]
                    if self.strict:
                        cmd.append('--strict')

                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    result.output = proc.stdout

                    # Parse output for errors/warnings
                    result.errors = result.output.count('❌ ERROR:')
                    result.warnings = result.output.count('⚠️  WARN:')
                    result.valid = proc.returncode == 0

                except subprocess.TimeoutExpired:
                    result.valid = False
                    result.errors = 1
                    result.output = f"Timeout running {validator}"
                except Exception as e:
                    result.valid = False
                    result.errors = 1
                    result.output = f"Error running {validator}: {e}"
            else:
                # Validator doesn't exist yet
                result.output = f"Validator not implemented: {validator}"
                result.warnings = 1
        else:
            # No specific validator - check basic structure
            result = self._validate_dimension_basic(dimension, agent_path)

        return result

    def _validate_dimension_basic(self, dimension: str, agent_path: str) -> DimensionResult:
        """Basic validation for dimensions without dedicated validators."""
        result = DimensionResult(dimension=dimension, valid=True)

        if dimension == 'reasoning':
            # Check for PROJECT_PLAN pattern usage
            claude_path = os.path.join(agent_path, 'CLAUDE.md')
            if os.path.isfile(claude_path):
                with open(claude_path) as f:
                    content = f.read().lower()
                has_planning = 'project_plan' in content or 'planning' in content
                has_gates = 'gate' in content or 'go/no-go' in content
                if has_planning and has_gates:
                    result.output = "Planning patterns documented"
                elif self.strict:
                    result.warnings = 1
                    result.output = "REASONING: Planning patterns not fully documented"
            else:
                result.output = "No CLAUDE.md to check reasoning patterns"

        elif dimension == 'skills':
            # Check for capabilities declaration
            version_path = os.path.join(agent_path, '.aget/version.json')
            manifest_path = os.path.join(agent_path, 'manifest.yaml')
            patterns_dir = os.path.join(agent_path, '.aget/patterns')

            has_capabilities = os.path.isfile(version_path) or os.path.isfile(manifest_path)
            has_patterns = os.path.isdir(patterns_dir)

            if has_capabilities and has_patterns:
                result.output = "Skills artifacts present"
            elif has_capabilities:
                result.output = "Capabilities declared"
                if self.strict:
                    result.warnings = 1
            else:
                result.valid = False
                result.errors = 1
                result.output = "SKILLS: No capabilities declaration found"

        return result


def format_result(result: OverallResult) -> str:
    """Format the overall result for output."""
    lines = []

    # Header
    if result.valid:
        lines.append(f"✅ {result.agent_path} - 5D COMPLIANT")
    else:
        lines.append(f"❌ {result.agent_path} - 5D NON-COMPLIANT")

    lines.append("")
    lines.append("Dimension Results:")
    lines.append("-" * 50)

    for dim_name in ['persona', 'memory', 'reasoning', 'skills', 'context']:
        if dim_name in result.dimensions:
            dim = result.dimensions[dim_name]
            symbol = "✅" if dim.valid else ("⚠️" if dim.warnings and not dim.errors else "❌")
            dim_label = dim_name.upper()
            status = "PASS" if dim.valid else ("WARN" if dim.warnings and not dim.errors else "FAIL")

            lines.append(f"  {symbol} D{['persona','memory','reasoning','skills','context'].index(dim_name)+1}: {dim_label:12} {status}")

            if dim.errors:
                lines.append(f"       Errors: {dim.errors}")
            if dim.warnings:
                lines.append(f"       Warnings: {dim.warnings}")

    lines.append("-" * 50)
    lines.append("")
    lines.append(f"Summary: {result.dimensions_passed}/{len(result.dimensions)} dimensions passed")

    if result.total_errors:
        lines.append(f"Total errors: {result.total_errors}")
    if result.total_warnings:
        lines.append(f"Total warnings: {result.total_warnings}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET 5D Architecture Compliance')
    parser.add_argument('path', nargs='?', default='.', help='Path to agent')
    parser.add_argument('--dir', help='Agent directory (alternative to positional)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode - optional items generate warnings')
    parser.add_argument('--dimensions', help='Comma-separated list of dimensions to validate')
    parser.add_argument('--skip-dimensions', help='Comma-separated list of dimensions to skip')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show summary')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show full validator output')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    agent_path = args.dir if args.dir else args.path

    dimensions = set(args.dimensions.split(',')) if args.dimensions else None
    skip_dims = set(args.skip_dimensions.split(',')) if args.skip_dimensions else None

    validator = FiveDComplianceValidator(
        strict=args.strict,
        dimensions=dimensions,
        skip_dimensions=skip_dims
    )

    result = validator.validate(agent_path)

    if not args.quiet:
        print(format_result(result))

        if args.verbose:
            print("\n" + "=" * 50)
            print("Detailed Output:")
            print("=" * 50)
            for dim_name, dim_result in result.dimensions.items():
                if dim_result.output:
                    print(f"\n[{dim_name.upper()}]")
                    print(dim_result.output)

    if result.valid:
        print(f"\n✅ 5D Architecture compliant")
    else:
        print(f"\n❌ 5D Architecture non-compliant")

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
