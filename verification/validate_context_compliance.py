#!/usr/bin/env python3
"""
Validate AGET Context Compliance (D5).

Implements: CAP-COMP-005 (Context_Dimension), R-CONTEXT-001 through R-CONTEXT-005, CAP-VAL-002
Traces to: AGET_CONTEXT_SPEC.md, AGET_5D_ARCHITECTURE_SPEC.md

Validates agent Context structure against AGET_CONTEXT_SPEC requirements.
Checks for relationship documentation, Scope_Boundaries, and environmental awareness.

Usage:
    python3 validate_context_compliance.py <agent_path>
    python3 validate_context_compliance.py --dir /path/to/agent
    python3 validate_context_compliance.py --strict

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
"""

import argparse
import sys
import os
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ValidationResult:
    """Result of validating context compliance."""
    agent_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class ContextComplianceValidator:
    """Validator for AGET Context Compliance."""

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: If True, optional items become warnings.
        """
        self.strict = strict

    def validate(self, agent_path: str) -> ValidationResult:
        """Validate context compliance for an agent."""
        result = ValidationResult(agent_path=agent_path, valid=True)

        if not os.path.exists(agent_path):
            result.add_error(f"Agent path not found: {agent_path}")
            return result

        if not os.path.isdir(agent_path):
            result.add_error(f"Path is not a directory: {agent_path}")
            return result

        # Core validations
        self._validate_relationships(agent_path, result)
        self._validate_scope_boundaries(agent_path, result)
        self._validate_portfolio(agent_path, result)
        self._validate_environmental_awareness(agent_path, result)

        return result

    def _validate_relationships(self, agent_path: str, result: ValidationResult) -> None:
        """Validate relationship structure is documented (R-CONTEXT-002)."""
        claude_path = os.path.join(agent_path, 'CLAUDE.md')

        if not os.path.isfile(claude_path):
            result.add_error("R-CONTEXT-002-04: CLAUDE.md not found")
            return

        try:
            with open(claude_path) as f:
                content = f.read()
                content_lower = content.lower()

            # Check for supervisor relationship
            has_managed_by = bool(re.search(r'managed\s*by\s*[:\-]?\s*\w+', content_lower))
            has_supervisor = 'supervisor' in content_lower

            # Check for managed entities
            has_manages = bool(re.search(r'manages\s*[:\-]', content_lower))

            result.stats['has_managed_by'] = has_managed_by or has_supervisor
            result.stats['has_manages'] = has_manages

            if not (has_managed_by or has_supervisor):
                if self.strict:
                    result.add_warning("R-CONTEXT-002-01: Supervisor relationship not explicit in CLAUDE.md")
            else:
                # Try to extract supervisor name
                match = re.search(r'managed\s*by\s*[:\-]?\s*(\S+)', content_lower)
                if match:
                    result.stats['supervisor'] = match.group(1)

            if not has_manages and self.strict:
                result.add_warning("R-CONTEXT-002-02: Managed entities not documented in CLAUDE.md")

        except IOError:
            result.add_error("R-CONTEXT-002-04: Cannot read CLAUDE.md")

    def _validate_scope_boundaries(self, agent_path: str, result: ValidationResult) -> None:
        """Validate scope boundaries are documented (R-CONTEXT-004)."""
        charter_path = os.path.join(agent_path, 'governance/CHARTER.md')
        scope_path = os.path.join(agent_path, 'governance/SCOPE_BOUNDARIES.md')

        has_charter = os.path.isfile(charter_path)
        has_scope = os.path.isfile(scope_path)

        result.stats['has_charter'] = has_charter
        result.stats['has_scope_doc'] = has_scope

        if has_charter:
            try:
                with open(charter_path) as f:
                    content = f.read().lower()

                # Check for scope patterns
                has_is_section = bool(re.search(r'what this agent is\b', content))
                has_is_not_section = bool(re.search(r'what this agent is not\b', content))
                has_boundaries = 'boundaries' in content or 'scope' in content

                result.stats['scope_is_documented'] = has_is_section
                result.stats['scope_is_not_documented'] = has_is_not_section

                if not has_is_section and self.strict:
                    result.add_warning("R-CONTEXT-004-01: CHARTER.md missing 'What This Agent IS' section")
                if not has_is_not_section and self.strict:
                    result.add_warning("R-CONTEXT-004-01: CHARTER.md missing 'What This Agent IS NOT' section")

            except IOError:
                result.add_error("R-CONTEXT-004-01: Cannot read CHARTER.md")
        else:
            if self.strict:
                result.add_warning("R-CONTEXT-004-01: No governance/CHARTER.md for scope documentation")

    def _validate_portfolio(self, agent_path: str, result: ValidationResult) -> None:
        """Validate portfolio membership is documented (R-CONTEXT-005-04)."""
        version_path = os.path.join(agent_path, '.aget/version.json')

        if os.path.isfile(version_path):
            try:
                with open(version_path) as f:
                    data = json.load(f)

                portfolio = data.get('portfolio')
                if portfolio:
                    result.stats['portfolio'] = portfolio
                elif self.strict:
                    result.add_warning("R-CONTEXT-005-04: No portfolio defined in version.json")

            except (json.JSONDecodeError, IOError):
                pass

    def _validate_environmental_awareness(self, agent_path: str, result: ValidationResult) -> None:
        """Validate environmental awareness patterns (R-CONTEXT-001)."""
        claude_path = os.path.join(agent_path, 'CLAUDE.md')

        if os.path.isfile(claude_path):
            try:
                with open(claude_path) as f:
                    content = f.read().lower()

                # Check for environmental grounding references
                env_patterns = [
                    'environmental grounding',
                    'git status',
                    'verify environment',
                    'l185',
                    "don't assume"
                ]

                matches = sum(1 for p in env_patterns if p in content)
                result.stats['env_awareness_score'] = matches

                if matches >= 2:
                    result.stats['env_grounding_documented'] = True
                elif self.strict:
                    result.add_warning("R-CONTEXT-001: Environmental grounding protocol not documented")

            except IOError:
                pass


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

    if result.stats:
        lines.append("")
        lines.append("  Context:")
        if 'supervisor' in result.stats:
            lines.append(f"    Supervisor: {result.stats['supervisor']}")
        if 'has_managed_by' in result.stats:
            lines.append(f"    Relationship documented: {'✅' if result.stats['has_managed_by'] else '❌'}")
        if 'portfolio' in result.stats:
            lines.append(f"    Portfolio: {result.stats['portfolio']}")
        if 'has_charter' in result.stats:
            lines.append(f"    Scope (Charter): {'✅' if result.stats['has_charter'] else '❌'}")
        if 'env_awareness_score' in result.stats:
            lines.append(f"    Env awareness: {result.stats['env_awareness_score']}/5 patterns")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Context Compliance')
    parser.add_argument('path', nargs='?', default='.', help='Path to agent')
    parser.add_argument('--dir', help='Agent directory (alternative to positional)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode - optional items generate warnings')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show errors')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    agent_path = args.dir if args.dir else args.path

    validator = ContextComplianceValidator(strict=args.strict)
    result = validator.validate(agent_path)

    if not args.quiet or not result.valid or result.warnings:
        print(format_result(result))

    if result.valid:
        print(f"\n✅ Context compliant")
    else:
        print(f"\n❌ Context non-compliant")

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
