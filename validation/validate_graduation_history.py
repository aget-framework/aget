#!/usr/bin/env python3
"""
Validate Artifact Graduation History (R-PROC-004)

Validates that specifications and patterns track their graduation history,
enforcing the L-doc → Pattern → Specification pathway.

Usage:
    python3 validate_graduation_history.py <file_or_dir>
    python3 validate_graduation_history.py --specs specs/
    python3 validate_graduation_history.py --patterns docs/patterns/

Exit codes:
    0: All artifacts have proper graduation history
    1: Missing graduation history
    2: File/path errors

R-PROC-004 Requirements:
    - Specs SHOULD have source_pattern or graduation_history
    - Patterns SHOULD have source_learnings or graduation_history
    - Exceptions require documented rationale
"""

import argparse
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import yaml


@dataclass
class ValidationResult:
    """Result of validating graduation history."""
    file_path: str
    valid: bool
    artifact_type: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class GraduationHistoryValidator:
    """Validator for artifact graduation history."""

    # Graduation indicators
    GRADUATION_KEYWORDS = [
        'graduation_history',
        'source_pattern',
        'source_learnings',
        'source_learning',
        'originated from',
        'evolved from',
        'based on L',
    ]

    # Exception keywords
    EXCEPTION_KEYWORDS = [
        'rationale',
        'novel',
        'no pattern precedent',
        'no learning precedent',
        'direct to spec',
    ]

    def validate_spec(self, file_path: str) -> ValidationResult:
        """Validate a specification for graduation history."""
        result = ValidationResult(file_path=file_path, valid=True, artifact_type='specification')

        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        # Check for graduation history or source pattern
        content_lower = content.lower()

        has_graduation = any(kw in content_lower for kw in self.GRADUATION_KEYWORDS)
        has_exception = any(kw in content_lower for kw in self.EXCEPTION_KEYWORDS)

        # Look for specific sections
        has_history_section = 'graduation history' in content_lower
        has_source_section = 'source' in content_lower and ('pattern' in content_lower or 'learning' in content_lower)

        # Check for L-doc references
        ldoc_pattern = re.compile(r'L\d{1,4}[_:\s]', re.IGNORECASE)
        has_ldoc_ref = ldoc_pattern.search(content)

        if not (has_graduation or has_exception or has_history_section or has_ldoc_ref):
            result.add_warning("R-PROC-004: No graduation_history or source_pattern found")
            result.add_warning("Specs SHOULD originate from patterns. Document rationale if novel.")
        elif has_exception and not has_graduation:
            result.add_warning("Exception noted but no graduation history documented")

        return result

    def validate_pattern(self, file_path: str) -> ValidationResult:
        """Validate a pattern for graduation history."""
        result = ValidationResult(file_path=file_path, valid=True, artifact_type='pattern')

        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result

        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        content_lower = content.lower()

        # Check for source learnings
        has_source_learnings = 'source_learning' in content_lower or 'source learning' in content_lower
        has_ldoc_ref = re.search(r'L\d{1,4}', content)
        has_exception = any(kw in content_lower for kw in self.EXCEPTION_KEYWORDS)

        # Check for "Source:" or "Origin:" sections
        has_source_section = bool(re.search(r'\*\*(Source|Origin|From)\*\*:', content, re.IGNORECASE))

        if not (has_source_learnings or has_ldoc_ref or has_exception or has_source_section):
            result.add_warning("R-PROC-004: No source_learnings or L-doc reference found")
            result.add_warning("Patterns SHOULD originate from learnings. Document rationale if novel.")

        return result

    def validate(self, file_path: str) -> ValidationResult:
        """Validate any artifact for graduation history."""
        filename = os.path.basename(file_path).lower()

        # Determine artifact type
        if 'spec' in filename or file_path.endswith('_SPEC.md') or '/specs/' in file_path:
            return self.validate_spec(file_path)
        elif filename.startswith('pattern') or '/patterns/' in file_path:
            return self.validate_pattern(file_path)
        else:
            # Unknown type - do basic check
            result = ValidationResult(file_path=file_path, valid=True, artifact_type='unknown')
            result.add_warning("Could not determine artifact type (spec or pattern)")
            return result


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

    lines.append(f"{symbol} {result.file_path} [{result.artifact_type}] - {status}")

    for error in result.errors:
        lines.append(f"  ❌ ERROR: {error}")

    for warning in result.warnings:
        lines.append(f"  ⚠️  WARN: {warning}")

    return "\n".join(lines)


def find_specs(base_path: str) -> List[str]:
    """Find specification files."""
    specs = []
    specs_dir = os.path.join(base_path, 'specs')

    if os.path.exists(specs_dir):
        for f in os.listdir(specs_dir):
            if f.endswith('.md') and 'SPEC' in f:
                specs.append(os.path.join(specs_dir, f))

    return sorted(specs)


def find_patterns(base_path: str) -> List[str]:
    """Find pattern files."""
    patterns = []
    patterns_dir = os.path.join(base_path, 'docs', 'patterns')

    if os.path.exists(patterns_dir):
        for f in os.listdir(patterns_dir):
            if f.endswith('.md'):
                patterns.append(os.path.join(patterns_dir, f))

    return sorted(patterns)


def main():
    parser = argparse.ArgumentParser(description='Validate Artifact Graduation History')
    parser.add_argument('paths', nargs='*', help='Paths to files')
    parser.add_argument('--specs', help='Validate specs in directory')
    parser.add_argument('--patterns', help='Validate patterns in directory')
    parser.add_argument('--dir', help='Validate all artifacts in agent directory')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    validator = GraduationHistoryValidator()
    results: List[ValidationResult] = []

    if args.dir:
        # Validate all specs and patterns
        for spec_path in find_specs(args.dir):
            results.append(validator.validate_spec(spec_path))
        for pattern_path in find_patterns(args.dir):
            results.append(validator.validate_pattern(pattern_path))

    elif args.specs:
        if os.path.isdir(args.specs):
            for f in os.listdir(args.specs):
                if f.endswith('.md'):
                    results.append(validator.validate_spec(os.path.join(args.specs, f)))
        else:
            results.append(validator.validate_spec(args.specs))

    elif args.patterns:
        if os.path.isdir(args.patterns):
            for f in os.listdir(args.patterns):
                if f.endswith('.md'):
                    results.append(validator.validate_pattern(os.path.join(args.patterns, f)))
        else:
            results.append(validator.validate_pattern(args.patterns))

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

    if not results:
        print("No artifacts found to validate")
        return 2

    # Output results
    all_valid = True
    has_warnings = False
    for result in results:
        if not args.quiet or not result.valid or result.warnings:
            print(format_result(result))
        if not result.valid:
            all_valid = False
        if result.warnings:
            has_warnings = True

    # Summary
    passed = sum(1 for r in results if r.valid and not r.warnings)
    warned = sum(1 for r in results if r.valid and r.warnings)
    failed = sum(1 for r in results if not r.valid)
    total = len(results)

    print(f"\n{'✅' if all_valid and not has_warnings else '⚠️' if all_valid else '❌'} "
          f"{passed} passed, {warned} warnings, {failed} failed (of {total})")

    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
