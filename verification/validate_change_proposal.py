#!/usr/bin/env python3
"""
Validate AGET Change Proposals.

Implements: R-CP-001 (Change_Proposal_Format), R-CP-002 (Change_Proposal_Lifecycle), CAP-VAL-002
Traces to: AGET_CHANGE_PROPOSAL_SPEC.md, AGET_VALIDATION_SPEC.md

Validates Change_Proposal (CP) documents against AGET_CHANGE_PROPOSAL_SPEC.
CPs are formal change requests with defined lifecycle and format.

Usage:
    python3 validate_change_proposal.py <cp_path>
    python3 validate_change_proposal.py docs/proposals/accepted/*.md
    python3 validate_change_proposal.py --all

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
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
    """Result of validating a Change Proposal."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class ChangeProposalValidator:
    """Validator for AGET Change Proposals."""

    # R-CP-001 requirements
    REQUIRED_PREAMBLE = ['proposal_id', 'title', 'author', 'date_submitted', 'status', 'category']
    REQUIRED_SECTIONS = ['Abstract', 'Motivation', 'Proposed Change', 'Impact Assessment',
                         'Alternatives Considered', 'Acceptance Criteria']

    # Valid values
    VALID_CATEGORIES = ['standards', 'informational', 'process']
    VALID_STATUSES = ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED',
                      'DEFERRED', 'SCOPED', 'IMPLEMENTING', 'RELEASED', 'CLOSED']
    TERMINAL_STATUSES = ['REJECTED', 'CLOSED']

    # Patterns
    CP_ID_PATTERN = re.compile(r'^CP-\d{3}$')
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    def validate(self, file_path: str) -> ValidationResult:
        """Validate a Change Proposal file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Check file naming
        filename = os.path.basename(file_path)
        if not filename.startswith('CP-'):
            result.add_warning(f"File should start with 'CP-': {filename}")

        # Read file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        # Parse YAML front matter
        preamble = self._extract_preamble(content, result)
        if preamble:
            self._validate_preamble(preamble, result)

        # Check required sections
        self._validate_sections(content, result)

        # Check resolution section for terminal states
        if preamble and preamble.get('status') in self.TERMINAL_STATUSES:
            self._validate_resolution(content, result)

        return result

    def _extract_preamble(self, content: str, result: ValidationResult) -> Optional[Dict[str, Any]]:
        """Extract YAML front matter from markdown."""
        if not content.startswith('---'):
            result.add_error("Missing YAML front matter (must start with ---)")
            return None

        parts = content.split('---', 2)
        if len(parts) < 3:
            result.add_error("Invalid YAML front matter format")
            return None

        try:
            preamble = yaml.safe_load(parts[1])
            return preamble if preamble else {}
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML in front matter: {e}")
            return None

    def _validate_preamble(self, preamble: Dict[str, Any], result: ValidationResult) -> None:
        """Validate preamble fields."""
        # Check required fields
        for field_name in self.REQUIRED_PREAMBLE:
            if field_name not in preamble:
                result.add_error(f"Missing required preamble field: {field_name}")

        # Validate proposal_id format (V-CP-001)
        if 'proposal_id' in preamble:
            cp_id = preamble['proposal_id']
            if not self.CP_ID_PATTERN.match(str(cp_id)):
                result.add_error(f"proposal_id must match pattern CP-NNN, got: {cp_id}")

        # Validate category (V-CP-003)
        if 'category' in preamble:
            if preamble['category'] not in self.VALID_CATEGORIES:
                result.add_error(f"Invalid category '{preamble['category']}'. Must be one of: {self.VALID_CATEGORIES}")

        # Validate status (V-CP-002)
        if 'status' in preamble:
            if preamble['status'] not in self.VALID_STATUSES:
                result.add_error(f"Invalid status '{preamble['status']}'. Must be one of: {self.VALID_STATUSES}")

        # Validate date format (V-CP-004)
        if 'date_submitted' in preamble:
            date_str = str(preamble['date_submitted'])
            if not self.DATE_PATTERN.match(date_str):
                result.add_error(f"date_submitted must be YYYY-MM-DD format, got: {date_str}")

        # Validate title length (V-CP-005)
        if 'title' in preamble:
            if len(str(preamble['title'])) > 80:
                result.add_error(f"title exceeds 80 characters: {len(preamble['title'])}")

    def _validate_sections(self, content: str, result: ValidationResult) -> None:
        """Validate required sections exist."""
        for section in self.REQUIRED_SECTIONS:
            # Look for markdown headers
            pattern = rf'^##\s+{re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                result.add_error(f"Missing required section: ## {section}")

        # Check for at least one alternative (V-CP-012)
        if '## Alternatives Considered' in content or '## Alternatives' in content:
            # Simple check for table or list content
            alt_section = content.split('## Alternatives')[1] if '## Alternatives' in content else ''
            if alt_section:
                next_section = alt_section.find('\n## ')
                if next_section > 0:
                    alt_section = alt_section[:next_section]
                if '|' not in alt_section and '-' not in alt_section:
                    result.add_warning("Alternatives Considered section appears empty")

        # Check for at least one acceptance criterion (V-CP-011)
        if '## Acceptance Criteria' in content:
            acc_section = content.split('## Acceptance Criteria')[1] if '## Acceptance Criteria' in content else ''
            if acc_section:
                next_section = acc_section.find('\n## ')
                if next_section > 0:
                    acc_section = acc_section[:next_section]
                if '[' not in acc_section and '-' not in acc_section:
                    result.add_warning("Acceptance Criteria section appears empty")

    def _validate_resolution(self, content: str, result: ValidationResult) -> None:
        """Validate resolution section for closed CPs."""
        if '## Resolution' not in content:
            result.add_error("CLOSED/REJECTED status requires ## Resolution section")
            return

        # Check for resolution field in resolution section
        resolution_section = content.split('## Resolution')[1] if '## Resolution' in content else ''
        if 'resolution:' not in resolution_section.lower():
            result.add_error("Resolution section missing 'resolution:' field")


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


def find_change_proposals(base_path: str) -> List[str]:
    """Find all CP files."""
    cps = []
    proposals_dir = os.path.join(base_path, 'docs', 'proposals', 'accepted')

    if os.path.exists(proposals_dir):
        for f in os.listdir(proposals_dir):
            if f.startswith('CP-') and f.endswith('.md'):
                cps.append(os.path.join(proposals_dir, f))

    return sorted(cps)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Change Proposals')
    parser.add_argument('paths', nargs='*', help='Paths to CP files')
    parser.add_argument('--all', action='store_true', help='Validate all CPs in framework')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    validator = ChangeProposalValidator()
    results: List[ValidationResult] = []

    if args.all:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)
        cps = find_change_proposals(base_path)

        if not cps:
            print("No Change Proposals found in docs/proposals/accepted/")
            return 2

        for cp_path in cps:
            results.append(validator.validate(cp_path))

    elif args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.endswith('.md'):
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
    print(f"\n{'✅' if all_valid else '❌'} {passed}/{total} Change Proposals valid")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
