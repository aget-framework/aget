#!/usr/bin/env python3
"""
Validate Cross-References in AGET Documents.

Implements: CAP-DOC-001 (Reference_Integrity), CAP-VAL-002 (validator structure)
Traces to: AGET_DOCUMENTATION_SPEC.md, AGET_VALIDATION_SPEC.md

Checks that file references within documents point to existing files.
Prevents documentation rot by catching broken links.

Usage:
    python3 validate_cross_references.py <file_or_dir>
    python3 validate_cross_references.py --dir /path/to/agent
    python3 validate_cross_references.py --all

Exit codes:
    0: All references valid
    1: Broken references found
    2: File/path errors

Reference patterns detected:
    - Markdown links: [text](path)
    - See: references: See: path/to/file.md
    - Location: references: **Location**: path/to/file
    - Spec references: specs/NAME.md
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional


@dataclass
class ValidationResult:
    """Result of validating cross-references."""
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class CrossReferenceValidator:
    """Validator for cross-references in documents."""

    # Patterns for extracting references
    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    SEE_PATTERN = re.compile(r'See:\s*[`"]?([^\s`"]+\.(?:md|yaml|py|json))[`"]?', re.IGNORECASE)
    LOCATION_PATTERN = re.compile(r'\*\*Location\*\*:\s*[`"]?([^\s`"]+)[`"]?')
    PATH_PATTERN = re.compile(r'`([a-zA-Z0-9_\-/]+\.(?:md|yaml|py|json))`')

    # Patterns to skip (external URLs, anchors)
    SKIP_PATTERNS = [
        re.compile(r'^https?://'),
        re.compile(r'^#'),
        re.compile(r'^mailto:'),
    ]

    def __init__(self, base_path: str):
        self.base_path = base_path

    def validate(self, file_path: str) -> ValidationResult:
        """Validate cross-references in a file."""
        result = ValidationResult(file_path=file_path, valid=True)

        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        # Only check markdown files
        if not file_path.endswith('.md'):
            return result

        # Read file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        # Extract and validate references
        file_dir = os.path.dirname(file_path)
        references = self._extract_references(content)

        for ref, line_hint in references:
            self._validate_reference(ref, file_dir, result, line_hint)

        return result

    def _extract_references(self, content: str) -> List[Tuple[str, str]]:
        """Extract all file references from content."""
        references = []

        # Markdown links
        for match in self.MARKDOWN_LINK_PATTERN.finditer(content):
            link = match.group(2)
            if not any(p.match(link) for p in self.SKIP_PATTERNS):
                # Remove anchor from link
                link = link.split('#')[0]
                if link:
                    references.append((link, f"link [{match.group(1)}]"))

        # See: references
        for match in self.SEE_PATTERN.finditer(content):
            references.append((match.group(1), "See: reference"))

        # Location: references
        for match in self.LOCATION_PATTERN.finditer(content):
            path = match.group(1)
            if '.' in path:
                references.append((path, "Location: reference"))

        # Inline code paths
        for match in self.PATH_PATTERN.finditer(content):
            path = match.group(1)
            if '/' in path:  # Only paths, not just filenames
                references.append((path, "inline code reference"))

        return references

    def _validate_reference(self, ref: str, file_dir: str,
                           result: ValidationResult, hint: str) -> None:
        """Validate a single reference."""
        # Skip external references
        if any(p.match(ref) for p in self.SKIP_PATTERNS):
            return

        # Skip empty references
        if not ref or ref == '.':
            return

        # Try multiple resolution strategies
        paths_to_try = [
            os.path.join(file_dir, ref),  # Relative to file
            os.path.join(self.base_path, ref),  # Relative to base
            ref,  # Absolute
        ]

        # Also try without leading ./
        if ref.startswith('./'):
            paths_to_try.insert(0, os.path.join(file_dir, ref[2:]))

        # Check if any path exists
        exists = any(os.path.exists(p) for p in paths_to_try)

        if not exists:
            # Check if it might be a pattern (like *.md)
            if '*' in ref:
                return
            # Check if it's a directory reference
            if ref.endswith('/'):
                return
            # Check if it's a relative reference we can't verify
            if ref.startswith('../../../'):
                result.add_warning(f"Cannot verify deep relative path: {ref} ({hint})")
                return

            result.add_error(f"Broken reference: {ref} ({hint})")


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


def find_markdown_files(base_path: str) -> List[str]:
    """Find all markdown files recursively."""
    md_files = []

    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and common non-doc directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]

        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))

    return sorted(md_files)


def main():
    parser = argparse.ArgumentParser(description='Validate Cross-References in AGET Documents')
    parser.add_argument('paths', nargs='*', help='Paths to files or directories')
    parser.add_argument('--dir', help='Agent directory to validate')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    results: List[ValidationResult] = []

    if args.dir:
        base_path = args.dir
        validator = CrossReferenceValidator(base_path)
        md_files = find_markdown_files(base_path)

        if not md_files:
            print(f"No markdown files found in {base_path}")
            return 2

        for md_path in md_files:
            results.append(validator.validate(md_path))

    elif args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                base_path = os.path.dirname(path)
                validator = CrossReferenceValidator(base_path)
                results.append(validator.validate(path))
            elif os.path.isdir(path):
                validator = CrossReferenceValidator(path)
                for md_path in find_markdown_files(path):
                    results.append(validator.validate(md_path))
            else:
                print(f"Path not found: {path}")
                return 2
    else:
        parser.print_help()
        return 2

    # Output results
    all_valid = True
    for result in results:
        if not args.quiet or not result.valid or result.warnings:
            if result.errors or result.warnings:
                print(format_result(result))
        if not result.valid:
            all_valid = False

    # Summary
    passed = sum(1 for r in results if r.valid)
    total = len(results)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    print(f"\n{'✅' if all_valid else '❌'} {passed}/{total} files have valid references")
    if total_errors or total_warnings:
        print(f"   {total_errors} errors, {total_warnings} warnings")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
