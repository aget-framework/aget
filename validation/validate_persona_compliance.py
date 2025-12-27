#!/usr/bin/env python3
"""
Validate AGET Persona Compliance

Validates agent persona structure against AGET_PERSONA_SPEC requirements.
Checks for identity artifacts, governance intensity, and archetype definition.

Usage:
    python3 validate_persona_compliance.py <agent_path>
    python3 validate_persona_compliance.py --dir /path/to/agent
    python3 validate_persona_compliance.py --template  # For template validation

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

See: specs/AGET_PERSONA_SPEC.md (R-PERSONA-001 through R-PERSONA-005)
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
    """Result of validating persona compliance."""
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


class PersonaComplianceValidator:
    """Validator for AGET Persona Compliance."""

    VALID_ARCHETYPES = [
        'supervisor', 'advisor', 'consultant', 'developer', 'worker',
        'executive', 'analyst', 'reviewer', 'operator', 'architect',
        'researcher', 'spec-engineer', 'repo-manager'
    ]

    VALID_GOVERNANCE_LEVELS = ['rigorous', 'balanced', 'exploratory']

    def __init__(self, is_template: bool = False, strict: bool = False):
        """Initialize validator.

        Args:
            is_template: If True, validate as template (relaxed requirements).
            strict: If True, optional items become warnings.
        """
        self.is_template = is_template
        self.strict = strict

    def validate(self, agent_path: str) -> ValidationResult:
        """Validate persona compliance for an agent."""
        result = ValidationResult(agent_path=agent_path, valid=True)

        if not os.path.exists(agent_path):
            result.add_error(f"Agent path not found: {agent_path}")
            return result

        if not os.path.isdir(agent_path):
            result.add_error(f"Path is not a directory: {agent_path}")
            return result

        # Core validations
        self._validate_archetype(agent_path, result)
        self._validate_governance(agent_path, result)
        self._validate_identity(agent_path, result)
        self._validate_governance_artifacts(agent_path, result)
        self._validate_style(agent_path, result)

        return result

    def _validate_archetype(self, agent_path: str, result: ValidationResult) -> None:
        """Validate archetype is defined (R-PERSONA-001)."""
        # Check version.json first
        version_path = os.path.join(agent_path, '.aget/version.json')
        manifest_path = os.path.join(agent_path, 'manifest.yaml')

        archetype = None

        if os.path.isfile(version_path):
            try:
                with open(version_path) as f:
                    data = json.load(f)
                archetype = data.get('template')
                if archetype:
                    # Extract archetype from template name
                    # e.g., "template-advisor-aget" -> "advisor"
                    match = re.match(r'template-(\w+)-aget', archetype)
                    if match:
                        archetype = match.group(1)
            except (json.JSONDecodeError, IOError):
                pass

        if not archetype and os.path.isfile(manifest_path):
            try:
                import yaml
                with open(manifest_path) as f:
                    data = yaml.safe_load(f)
                archetype = data.get('archetype') or data.get('template', {}).get('archetype')
            except Exception:
                pass

        if archetype:
            result.stats['archetype'] = archetype
            if archetype not in self.VALID_ARCHETYPES:
                result.add_warning(f"R-PERSONA-001: Archetype '{archetype}' not in standard list")
        elif not self.is_template:
            result.add_error("R-PERSONA-001: No archetype defined in version.json or manifest.yaml")

    def _validate_governance(self, agent_path: str, result: ValidationResult) -> None:
        """Validate governance capability is declared (R-PERSONA-002)."""
        version_path = os.path.join(agent_path, '.aget/version.json')
        manifest_path = os.path.join(agent_path, 'manifest.yaml')

        governance_level = None
        has_capability = False

        # Check version.json
        if os.path.isfile(version_path):
            try:
                with open(version_path) as f:
                    data = json.load(f)
                capabilities = data.get('capabilities', [])
                for cap in capabilities:
                    if 'governance' in cap.lower():
                        has_capability = True
                        # Extract level from capability-governance-X
                        match = re.search(r'governance[_-](\w+)', cap.lower())
                        if match:
                            governance_level = match.group(1)
                        break
            except (json.JSONDecodeError, IOError):
                pass

        # Check manifest
        if not has_capability and os.path.isfile(manifest_path):
            try:
                import yaml
                with open(manifest_path) as f:
                    data = yaml.safe_load(f)
                capabilities = data.get('capabilities', [])
                for cap in capabilities:
                    cap_name = cap if isinstance(cap, str) else cap.get('name', '')
                    if 'governance' in cap_name.lower():
                        has_capability = True
                        match = re.search(r'governance[_-](\w+)', cap_name.lower())
                        if match:
                            governance_level = match.group(1)
                        break
            except Exception:
                pass

        if governance_level:
            result.stats['governance_level'] = governance_level
            if governance_level not in self.VALID_GOVERNANCE_LEVELS:
                result.add_warning(f"R-PERSONA-002: Governance level '{governance_level}' not standard")

        # Check CLAUDE.md for governance documentation
        claude_path = os.path.join(agent_path, 'CLAUDE.md')
        if os.path.isfile(claude_path):
            try:
                with open(claude_path) as f:
                    content = f.read()
                if 'governance' in content.lower():
                    result.stats['governance_documented'] = True
            except IOError:
                pass

        if not has_capability and not self.is_template and self.strict:
            result.add_warning("R-PERSONA-002: No governance capability declared")

    def _validate_identity(self, agent_path: str, result: ValidationResult) -> None:
        """Validate identity.json with north_star (R-PERSONA-004)."""
        identity_path = os.path.join(agent_path, '.aget/identity.json')

        if os.path.isfile(identity_path):
            try:
                with open(identity_path) as f:
                    data = json.load(f)

                north_star = data.get('north_star')
                if north_star:
                    result.stats['north_star'] = north_star[:50] + '...' if len(north_star) > 50 else north_star
                else:
                    result.add_warning("R-PERSONA-004: identity.json exists but missing north_star")

                # Optional fields
                if data.get('purpose'):
                    result.stats['has_purpose'] = True
                if data.get('governance_level'):
                    result.stats['identity_governance'] = data['governance_level']

            except json.JSONDecodeError:
                result.add_error("R-PERSONA-004: identity.json is not valid JSON")
            except IOError:
                result.add_error(f"R-PERSONA-004: Cannot read identity.json")
        elif not self.is_template:
            if self.strict:
                result.add_warning("R-PERSONA-004: No identity.json found (recommended for rigorous agents)")

    def _validate_governance_artifacts(self, agent_path: str, result: ValidationResult) -> None:
        """Validate governance artifacts exist (R-PERSONA-005)."""
        charter_path = os.path.join(agent_path, 'governance/CHARTER.md')
        mission_path = os.path.join(agent_path, 'governance/MISSION.md')
        governance_dir = os.path.join(agent_path, 'governance')

        has_governance_dir = os.path.isdir(governance_dir)
        has_charter = os.path.isfile(charter_path)
        has_mission = os.path.isfile(mission_path)

        result.stats['has_governance_dir'] = has_governance_dir
        result.stats['has_charter'] = has_charter
        result.stats['has_mission'] = has_mission

        if not self.is_template:
            if not has_governance_dir:
                if self.strict:
                    result.add_warning("R-PERSONA-005: No governance/ directory")
            else:
                if not has_charter and self.strict:
                    result.add_warning("R-PERSONA-005: Missing governance/CHARTER.md")
                if not has_mission and self.strict:
                    result.add_warning("R-PERSONA-005: Missing governance/MISSION.md")

    def _validate_style(self, agent_path: str, result: ValidationResult) -> None:
        """Validate communication style is documented (R-PERSONA-003)."""
        claude_path = os.path.join(agent_path, 'CLAUDE.md')

        if os.path.isfile(claude_path):
            try:
                with open(claude_path) as f:
                    content = f.read().lower()

                # Check for style indicators
                style_keywords = ['formal', 'concise', 'rigorous', 'balanced', 'exploratory',
                                  'communication', 'style', 'tone']
                style_matches = sum(1 for kw in style_keywords if kw in content)

                if style_matches >= 2:
                    result.stats['style_documented'] = True
                elif self.strict:
                    result.add_warning("R-PERSONA-003: Communication style not clearly documented in CLAUDE.md")
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
        lines.append("  Persona:")
        if 'archetype' in result.stats:
            lines.append(f"    Archetype: {result.stats['archetype']}")
        if 'governance_level' in result.stats:
            lines.append(f"    Governance: {result.stats['governance_level']}")
        if 'north_star' in result.stats:
            lines.append(f"    North Star: {result.stats['north_star']}")
        if 'has_charter' in result.stats:
            lines.append(f"    Charter: {'✅' if result.stats['has_charter'] else '❌'}")
        if 'has_mission' in result.stats:
            lines.append(f"    Mission: {'✅' if result.stats['has_mission'] else '❌'}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Persona Compliance')
    parser.add_argument('path', nargs='?', default='.', help='Path to agent')
    parser.add_argument('--dir', help='Agent directory (alternative to positional)')
    parser.add_argument('--template', action='store_true',
                        help='Validate as template (relaxed requirements)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode - optional items generate warnings')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show errors')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    agent_path = args.dir if args.dir else args.path

    validator = PersonaComplianceValidator(is_template=args.template, strict=args.strict)
    result = validator.validate(agent_path)

    if not args.quiet or not result.valid or result.warnings:
        print(format_result(result))

    if result.valid:
        print(f"\n✅ Persona compliant")
    else:
        print(f"\n❌ Persona non-compliant")

    return 0 if result.valid else 1


if __name__ == '__main__':
    sys.exit(main())
