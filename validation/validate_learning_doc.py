#!/usr/bin/env python3
"""
Validate AGET Learning Documents (L-docs)

Validates L-doc format, naming, and required sections.
L-docs capture experiential knowledge and form the foundation
of the continual learning system.

Usage:
    python3 validate_learning_doc.py <ldoc_path>
    python3 validate_learning_doc.py .aget/evolution/*.md
    python3 validate_learning_doc.py --dir /path/to/agent

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

L-doc Format Requirements:
    - Filename: L{NNN}_{snake_case_title}.md
    - Title: # L{NNN}: {Title}
    - Required sections: Context, Insight, Application
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ValidationResult:
    """Result of validating a Learning Document."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class LearningDocValidator:
    """Validator for AGET Learning Documents."""

    # Filename pattern: L{NNN}_{snake_case}.md
    FILENAME_PATTERN = re.compile(r'^L(\d{1,4})_([a-z][a-z0-9_]*)?\.md$')

    # Title pattern: # L{NNN}: {Title} or # L{NNN} {Title}
    TITLE_PATTERN = re.compile(r'^#\s+L(\d{1,4})[:\s]+(.+)$', re.MULTILINE)

    # Required sections
    REQUIRED_SECTIONS = ['Context', 'Insight', 'Application']

    # Recommended sections
    RECOMMENDED_SECTIONS = ['Date', 'Source', 'Related']

    def validate(self, file_path: str) -> ValidationResult:
        """Validate a Learning Document."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        filename = os.path.basename(file_path)

        # Validate filename format
        filename_match = self.FILENAME_PATTERN.match(filename)
        if not filename_match:
            result.add_error(f"Invalid filename format. Expected L{{NNN}}_{{snake_case}}.md, got: {filename}")

        # Read file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        # Validate content
        self._validate_title(content, filename, filename_match, result)
        self._validate_required_sections(content, result)
        self._validate_recommended_sections(content, result)
        self._validate_length(content, result)

        return result

    def _validate_title(self, content: str, filename: str,
                        filename_match: Optional[re.Match], result: ValidationResult) -> None:
        """Validate title matches filename."""
        title_match = self.TITLE_PATTERN.search(content)

        if not title_match:
            result.add_error("Missing or invalid title. Expected: # LNNN: Title")
            return

        title_number = title_match.group(1)

        # Cross-check with filename
        if filename_match:
            file_number = filename_match.group(1)
            if title_number != file_number:
                result.add_error(f"L-number mismatch: filename has L{file_number}, title has L{title_number}")

    def _validate_required_sections(self, content: str, result: ValidationResult) -> None:
        """Validate required sections exist."""
        content_lower = content.lower()

        for section in self.REQUIRED_SECTIONS:
            # Look for section as header or bold
            patterns = [
                rf'^##\s+{section}',
                rf'^###\s+{section}',
                rf'\*\*{section}\*\*',
            ]

            found = False
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    found = True
                    break

            # Also accept inline if section name appears
            if not found and section.lower() in content_lower:
                # Lenient: accept if word appears in context
                found = True

            if not found:
                result.add_error(f"Missing required section: {section}")

    def _validate_recommended_sections(self, content: str, result: ValidationResult) -> None:
        """Check for recommended sections."""
        for section in self.RECOMMENDED_SECTIONS:
            if section.lower() not in content.lower():
                result.add_warning(f"Missing recommended element: {section}")

    def _validate_length(self, content: str, result: ValidationResult) -> None:
        """Validate content length is reasonable."""
        lines = content.strip().split('\n')
        word_count = len(content.split())

        if len(lines) < 5:
            result.add_warning(f"L-doc seems too short ({len(lines)} lines)")

        if word_count < 50:
            result.add_warning(f"L-doc seems too brief ({word_count} words)")

        if word_count > 2000:
            result.add_warning(f"L-doc may be too long ({word_count} words). Consider splitting.")


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


def find_learning_docs(base_path: str) -> List[str]:
    """Find all L-doc files."""
    ldocs = []
    evolution_dir = os.path.join(base_path, '.aget', 'evolution')

    if os.path.exists(evolution_dir):
        for f in os.listdir(evolution_dir):
            if f.startswith('L') and f.endswith('.md'):
                ldocs.append(os.path.join(evolution_dir, f))

    return sorted(ldocs)


def main():
    parser = argparse.ArgumentParser(description='Validate AGET Learning Documents')
    parser.add_argument('paths', nargs='*', help='Paths to L-doc files')
    parser.add_argument('--dir', help='Agent directory to search for L-docs')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    validator = LearningDocValidator()
    results: List[ValidationResult] = []

    if args.dir:
        ldocs = find_learning_docs(args.dir)
        if not ldocs:
            print(f"No L-docs found in {args.dir}/.aget/evolution/")
            return 2
        for ldoc_path in ldocs:
            results.append(validator.validate(ldoc_path))

    elif args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.startswith('L') and f.endswith('.md'):
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
    print(f"\n{'✅' if all_valid else '❌'} {passed}/{total} Learning Documents valid")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
