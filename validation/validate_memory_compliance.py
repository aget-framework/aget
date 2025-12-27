#!/usr/bin/env python3
"""
Validate AGET Memory Compliance

Validates agent memory structure against AGET_MEMORY_SPEC requirements.
Checks for required directories, artifacts, and learning documents.

Usage:
    python3 validate_memory_compliance.py <agent_path>
    python3 validate_memory_compliance.py --dir /path/to/agent
    python3 validate_memory_compliance.py --strict

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

See: specs/AGET_MEMORY_SPEC.md (R-MEM-001 through R-MEM-006)
"""

import argparse
import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ValidationResult:
    """Result of validating memory compliance."""
    agent_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class MemoryComplianceValidator:
    """Validator for AGET Memory Compliance."""

    # Required directories (R-MEM-005)
    REQUIRED_DIRS = {
        '.aget': 'Agent identity directory',
        '.aget/evolution': 'Learning documents directory',
        'governance': 'Governance artifacts',
        'planning': 'Planning artifacts',
    }

    # Optional directories
    OPTIONAL_DIRS = {
        '.aget/patterns': 'Agent pattern scripts',
        'docs/patterns': 'Pattern documents',
        'inherited': 'Inherited knowledge',
        'decisions': 'Decision records',
        'sops': 'Standard operating procedures',
    }

    # Required files (R-MEM-005)
    REQUIRED_FILES = {
        '.aget/version.json': 'Agent identity file',
    }

    # Optional files
    OPTIONAL_FILES = {
        '.aget/identity.json': 'North Star identity',
        'governance/CHARTER.md': 'Agent charter',
        'governance/MISSION.md': 'Agent mission',
    }

    # L-doc patterns
    LDOC_PATTERN = 'L*.md'

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: If True, optional items become warnings.
        """
        self.strict = strict

    def validate(self, agent_path: str) -> ValidationResult:
        """Validate memory compliance for an agent."""
        result = ValidationResult(agent_path=agent_path, valid=True)

        # Check path exists
        if not os.path.exists(agent_path):
            result.add_error(f"Agent path not found: {agent_path}")
            return result

        if not os.path.isdir(agent_path):
            result.add_error(f"Path is not a directory: {agent_path}")
            return result

        # Validate structure
        self._validate_required_dirs(agent_path, result)
        self._validate_optional_dirs(agent_path, result)
        self._validate_required_files(agent_path, result)
        self._validate_optional_files(agent_path, result)
        self._validate_learning_docs(agent_path, result)
        self._validate_memory_layers(agent_path, result)

        return result

    def _validate_required_dirs(self, agent_path: str, result: ValidationResult) -> None:
        """Validate required directories exist."""
        for rel_path, description in self.REQUIRED_DIRS.items():
            full_path = os.path.join(agent_path, rel_path)
            if os.path.isdir(full_path):
                # Count contents
                contents = os.listdir(full_path)
                result.stats[rel_path] = len(contents)
            else:
                result.add_error(f"R-MEM-005: Missing required directory: {rel_path} ({description})")

    def _validate_optional_dirs(self, agent_path: str, result: ValidationResult) -> None:
        """Check optional directories."""
        for rel_path, description in self.OPTIONAL_DIRS.items():
            full_path = os.path.join(agent_path, rel_path)
            if os.path.isdir(full_path):
                contents = os.listdir(full_path)
                result.stats[rel_path] = len(contents)
            elif self.strict:
                result.add_warning(f"Optional directory missing: {rel_path} ({description})")

    def _validate_required_files(self, agent_path: str, result: ValidationResult) -> None:
        """Validate required files exist."""
        for rel_path, description in self.REQUIRED_FILES.items():
            full_path = os.path.join(agent_path, rel_path)
            if not os.path.isfile(full_path):
                result.add_error(f"R-MEM-005: Missing required file: {rel_path} ({description})")

    def _validate_optional_files(self, agent_path: str, result: ValidationResult) -> None:
        """Check optional files."""
        for rel_path, description in self.OPTIONAL_FILES.items():
            full_path = os.path.join(agent_path, rel_path)
            if not os.path.isfile(full_path) and self.strict:
                result.add_warning(f"Optional file missing: {rel_path} ({description})")

    def _validate_learning_docs(self, agent_path: str, result: ValidationResult) -> None:
        """Validate learning documents (R-MEM-002)."""
        evolution_dir = os.path.join(agent_path, '.aget/evolution')

        if not os.path.isdir(evolution_dir):
            return  # Already reported as missing

        # Count L-docs
        ldocs = [f for f in os.listdir(evolution_dir)
                 if f.startswith('L') and f.endswith('.md')]

        result.stats['ldocs'] = len(ldocs)

        if len(ldocs) == 0:
            result.add_warning("R-MEM-002: No learning documents found in .aget/evolution/")
        elif len(ldocs) < 3:
            result.add_warning(f"R-MEM-002: Few learning documents ({len(ldocs)}). Agents should accumulate learnings.")

        # Validate L-doc naming
        import re
        ldoc_pattern = re.compile(r'^L\d{1,4}_[a-z][a-z0-9_]*\.md$')

        for ldoc in ldocs:
            if not ldoc_pattern.match(ldoc):
                result.add_warning(f"R-MEM-002: Invalid L-doc naming: {ldoc} (expected L{{NNN}}_{{snake_case}}.md)")

    def _validate_memory_layers(self, agent_path: str, result: ValidationResult) -> None:
        """Validate 6-layer memory model (R-MEM-001)."""
        # Layer 4: Agent memory
        layer4_dirs = ['.aget', '.aget/evolution']
        layer4_present = all(os.path.isdir(os.path.join(agent_path, d)) for d in layer4_dirs)

        if not layer4_present:
            result.add_error("R-MEM-001-04: Layer 4 (Agent Memory) incomplete")

        # Layer 3: Project memory
        layer3_dirs = ['governance', 'planning']
        layer3_present = all(os.path.isdir(os.path.join(agent_path, d)) for d in layer3_dirs)

        if not layer3_present:
            result.add_error("R-MEM-001-03: Layer 3 (Project Memory) incomplete")

        # Layer 5: Fleet memory (optional)
        fleet_indicators = ['inherited', 'FLEET_STATE.yaml']
        has_fleet = any(os.path.exists(os.path.join(agent_path, f)) for f in fleet_indicators)

        if has_fleet:
            result.stats['fleet_memory'] = 1

        # Summary
        layers_present = 0
        if layer4_present:
            layers_present += 1
        if layer3_present:
            layers_present += 1
        if has_fleet:
            layers_present += 1

        result.stats['memory_layers'] = layers_present


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

    lines.append(f"{symbol} {result.agent_path} - {status}")

    for error in result.errors:
        lines.append(f"  ❌ ERROR: {error}")

    for warning in result.warnings:
        lines.append(f"  ⚠️  WARN: {warning}")

    # Statistics
    if result.stats:
        lines.append("")
        lines.append("  Statistics:")
        if 'ldocs' in result.stats:
            lines.append(f"    L-docs: {result.stats['ldocs']}")
        if '.aget/evolution' in result.stats:
            lines.append(f"    Evolution files: {result.stats['.aget/evolution']}")
        if 'governance' in result.stats:
            lines.append(f"    Governance files: {result.stats['governance']}")
        if 'planning' in result.stats:
            lines.append(f"    Planning files: {result.stats['planning']}")
        if 'memory_layers' in result.stats:
            lines.append(f"    Memory layers: {result.stats['memory_layers']}/6")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Memory Compliance')
    parser.add_argument('path', nargs='?', default='.', help='Path to agent')
    parser.add_argument('--dir', help='Agent directory (alternative to positional)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode - optional items generate warnings')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show errors')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    agent_path = args.dir if args.dir else args.path

    validator = MemoryComplianceValidator(strict=args.strict)
    result = validator.validate(agent_path)

    if not args.quiet or not result.valid or result.warnings:
        print(format_result(result))

    # Summary
    if result.valid:
        print(f"\n✅ Memory structure compliant")
    else:
        print(f"\n❌ Memory structure non-compliant")

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
