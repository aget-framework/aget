#!/usr/bin/env python3
"""
Validate AGET Published Learnings in docs/learnings/.

Implements: CAP-EVOL-007 (Public Learning Publication), CP-008
Traces to: AGET_EVOLUTION_SPEC.md, SOP_learning_publication.md

Validates Published_Learning format, sanitization, and content quality.
Published Learnings are Learning_Documents graduated from private
.aget/evolution/ to public docs/learnings/.

Usage:
    python3 validate_public_learnings.py <path>
    python3 validate_public_learnings.py docs/learnings/
    python3 validate_public_learnings.py docs/learnings/L455_*.md

Exit codes:
    0: All validations passed (or only warnings)
    1: Validation errors found
    2: File/path errors

Validation Checks:
    V-PUB-001: File matches L###_*.md pattern (ERROR)
    V-PUB-002: Has required sections (ERROR)
    V-PUB-003: Has publication metadata (WARN)
    V-PUB-004: No .aget/ internal paths (ERROR)
    V-PUB-005: No private-* agent names (WARN)
    V-PUB-006: Has ## Learning section (ERROR)
    V-PUB-007: Has ## Evidence section (WARN)
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of validating a Published Learning."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, check_id: str, message: str) -> None:
        self.errors.append(f"[{check_id}] {message}")
        self.valid = False

    def add_warning(self, check_id: str, message: str) -> None:
        self.warnings.append(f"[{check_id}] {message}")


class PublicLearningValidator:
    """Validator for AGET Published Learnings."""

    # V-PUB-001: Filename pattern
    FILENAME_PATTERN = re.compile(r'^L(\d{1,4})_([a-z][a-z0-9_]*)\.md$')

    # Title pattern: # L{NNN}: {Title}
    TITLE_PATTERN = re.compile(r'^#\s+L(\d{1,4})[:\s]+(.+)$', re.MULTILINE)

    # V-PUB-004: Internal path patterns (should not appear)
    INTERNAL_PATH_PATTERNS = [
        r'\.aget/evolution/',      # Private evolution directory
        r'~/github/GM-',           # Internal repo paths
        r'/Users/[a-z]+/',         # Machine-specific paths
        r'private-[a-z]+-AGET/',   # Private agent repo paths
    ]

    # V-PUB-005: Private agent name patterns
    PRIVATE_AGENT_PATTERN = re.compile(r'private-[a-zA-Z0-9_-]+-AGET')

    def validate(self, file_path: str) -> ValidationResult:
        """Validate a Published Learning."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error("V-PUB-000", f"File not found: {file_path}")
            return result

        filename = os.path.basename(file_path)

        # V-PUB-001: Validate filename format
        self._check_filename(filename, result)

        # Read file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error("V-PUB-000", f"Cannot read file: {e}")
            return result

        # V-PUB-002: Title validation
        self._check_title(content, filename, result)

        # V-PUB-003: Publication metadata
        self._check_publication_metadata(content, result)

        # V-PUB-004: No internal paths
        self._check_no_internal_paths(content, result)

        # V-PUB-005: No private agent names
        self._check_no_private_agents(content, result)

        # V-PUB-006: Has ## Learning section
        self._check_learning_section(content, result)

        # V-PUB-007: Has ## Evidence section
        self._check_evidence_section(content, result)

        return result

    def _check_filename(self, filename: str, result: ValidationResult) -> None:
        """V-PUB-001: Check filename matches pattern."""
        if not self.FILENAME_PATTERN.match(filename):
            result.add_error("V-PUB-001",
                f"Invalid filename. Expected L{{NNN}}_{{snake_case}}.md, got: {filename}")

    def _check_title(self, content: str, filename: str, result: ValidationResult) -> None:
        """V-PUB-002: Check title exists and matches filename."""
        title_match = self.TITLE_PATTERN.search(content)

        if not title_match:
            result.add_error("V-PUB-002", "Missing or invalid title. Expected: # LNNN: Title")
            return

        # Cross-check L-number
        filename_match = self.FILENAME_PATTERN.match(filename)
        if filename_match:
            file_number = filename_match.group(1)
            title_number = title_match.group(1)
            if file_number != title_number:
                result.add_error("V-PUB-002",
                    f"L-number mismatch: filename L{file_number}, title L{title_number}")

    def _check_publication_metadata(self, content: str, result: ValidationResult) -> None:
        """V-PUB-003: Check for publication metadata (WARN only)."""
        # Look for publication_date or similar
        has_metadata = any([
            'publication_date:' in content.lower(),
            'publication:' in content.lower(),
            '**publication**' in content.lower(),
            'published:' in content.lower(),
        ])

        if not has_metadata:
            result.add_warning("V-PUB-003",
                "No publication metadata found (optional but recommended)")

    def _check_no_internal_paths(self, content: str, result: ValidationResult) -> None:
        """V-PUB-004: Check for internal paths that should be sanitized."""
        for pattern in self.INTERNAL_PATH_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                result.add_error("V-PUB-004",
                    f"Internal path found (needs sanitization): {matches[0]}")

    def _check_no_private_agents(self, content: str, result: ValidationResult) -> None:
        """V-PUB-005: Check for private agent names."""
        matches = self.PRIVATE_AGENT_PATTERN.findall(content)
        if matches:
            # This is a warning, not error - some contexts may be acceptable
            result.add_warning("V-PUB-005",
                f"Private agent name found (consider generalizing): {matches[0]}")

    def _check_learning_section(self, content: str, result: ValidationResult) -> None:
        """V-PUB-006: Check for ## Learning section."""
        # Accept various forms: ## Learning, ## The Learning, ## Key Learning
        patterns = [
            r'^##\s+Learning',
            r'^##\s+The Learning',
            r'^##\s+Key Learning',
            r'\*\*Learning\*\*:',
        ]

        found = any(re.search(p, content, re.MULTILINE | re.IGNORECASE) for p in patterns)

        if not found:
            result.add_error("V-PUB-006",
                "Missing required section: ## Learning")

    def _check_evidence_section(self, content: str, result: ValidationResult) -> None:
        """V-PUB-007: Check for ## Evidence section (WARN only)."""
        patterns = [
            r'^##\s+Evidence',
            r'^##\s+Validation',
            r'\*\*Evidence\*\*:',
            r'\*\*Discovery\*\*:',
        ]

        found = any(re.search(p, content, re.MULTILINE | re.IGNORECASE) for p in patterns)

        if not found:
            result.add_warning("V-PUB-007",
                "Missing recommended section: ## Evidence")


def format_result(result: ValidationResult, verbose: bool = False) -> str:
    """Format a validation result for output."""
    lines = []

    if result.valid:
        status = "PASS"
        symbol = "✅"
    else:
        status = "FAIL"
        symbol = "❌"

    filename = os.path.basename(result.file_path)
    lines.append(f"{symbol} {filename}: {status}")

    if verbose or not result.valid:
        for error in result.errors:
            lines.append(f"  ❌ ERROR: {error}")

    if verbose or result.warnings:
        for warning in result.warnings:
            lines.append(f"  ⚠️  WARN: {warning}")

    return "\n".join(lines)


def find_public_learnings(base_path: str) -> List[str]:
    """Find all Published Learning files in docs/learnings/."""
    learnings = []

    # Check if path is the docs/learnings directory
    if os.path.isdir(base_path):
        search_dir = base_path
    else:
        # Try standard location
        search_dir = os.path.join(base_path, 'docs', 'learnings')

    if os.path.exists(search_dir):
        for f in os.listdir(search_dir):
            if f.startswith('L') and f.endswith('.md'):
                learnings.append(os.path.join(search_dir, f))

    return sorted(learnings)


def main():
    parser = argparse.ArgumentParser(
        description='Validate AGET Published Learnings (docs/learnings/)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Validation Checks:
  V-PUB-001  File matches L###_*.md pattern (ERROR)
  V-PUB-002  Has valid title (ERROR)
  V-PUB-003  Has publication metadata (WARN)
  V-PUB-004  No internal paths like .aget/ (ERROR)
  V-PUB-005  No private-* agent names (WARN)
  V-PUB-006  Has ## Learning section (ERROR)
  V-PUB-007  Has ## Evidence section (WARN)
        """
    )
    parser.add_argument('paths', nargs='*', help='Paths to validate')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show all checks including passes')
    parser.add_argument('--help-checks', action='store_true',
                       help='Show validation check details')

    args = parser.parse_args()

    if args.help_checks:
        print(__doc__)
        return 0

    validator = PublicLearningValidator()
    results: List[ValidationResult] = []

    if not args.paths:
        # Default: validate docs/learnings/ in current directory
        learnings = find_public_learnings('.')
        if not learnings:
            print("No Published Learnings found in docs/learnings/")
            print("Usage: python3 validate_public_learnings.py <path>")
            return 2
        for path in learnings:
            results.append(validator.validate(path))
    else:
        for path in args.paths:
            if os.path.isfile(path):
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                learnings = find_public_learnings(path)
                if not learnings:
                    # Maybe it IS the docs/learnings dir
                    for f in os.listdir(path):
                        if f.startswith('L') and f.endswith('.md'):
                            results.append(validator.validate(os.path.join(path, f)))
                else:
                    for learning_path in learnings:
                        results.append(validator.validate(learning_path))
            else:
                print(f"Path not found: {path}")
                return 2

    if not results:
        print("No Published Learnings to validate")
        return 2

    # Output results
    all_valid = True
    for result in results:
        print(format_result(result, args.verbose))
        if not result.valid:
            all_valid = False

    # Summary
    passed = sum(1 for r in results if r.valid)
    total = len(results)
    warn_count = sum(len(r.warnings) for r in results)

    print()
    if all_valid:
        print(f"✅ {passed}/{total} Published Learnings valid")
        if warn_count:
            print(f"   ({warn_count} warnings)")
    else:
        print(f"❌ {passed}/{total} Published Learnings valid")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
