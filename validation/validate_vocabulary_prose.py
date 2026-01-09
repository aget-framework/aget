#!/usr/bin/env python3
"""
validate_vocabulary_prose.py - AGET Vocabulary Prose Validator

Validates that AGET Vocabulary terms follow the compound naming convention (L493)
and that prose usage is consistent.

Usage:
    python validate_vocabulary_prose.py --check-terms [PATH]
    python validate_vocabulary_prose.py --check-prose [PATH]
    python validate_vocabulary_prose.py --fix [PATH]

Modes:
    --check-terms   Validate all skos:prefLabel values are compound (contain underscore)
    --check-prose   Validate prose usage of vocabulary terms
    --fix           Suggest corrections for violations

Requirements:
    R-VOC-TERM-001: All skos:prefLabel values MUST be compound
    R-VOC-PROSE-001: Prose MUST use exact skos:prefLabel form
    R-VOC-PROSE-002: Generic English MUST use lowercase

See: L493 (Vocabulary_Prose_Marking_Pattern)
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Compound term pattern: Title_Case with underscores
COMPOUND_PATTERN = re.compile(r'^[A-Z][a-z]+(_[A-Z][a-z0-9]+)+$')

# Single word pattern (violation)
SINGLE_WORD_PATTERN = re.compile(r'^[A-Z][a-z]+$')

# Acronym pattern (acceptable)
ACRONYM_PATTERN = re.compile(r'^[A-Z]{2,}$')

# Template/example terms to ignore
TEMPLATE_TERMS = {'Term_Name', 'New_Term', 'New_Artifact', 'Parent_Term', 'Similar_Term'}


class VocabularyValidator:
    """Validates AGET Vocabulary compliance with L493."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.vocabulary: Dict[str, str] = {}  # prefLabel -> definition

    def load_vocabulary(self, spec_path: Path) -> bool:
        """Load vocabulary terms from AGET_VOCABULARY_SPEC.md."""
        if not spec_path.exists():
            self.errors.append(f"Vocabulary spec not found: {spec_path}")
            return False

        content = spec_path.read_text()

        # Extract all skos:prefLabel values
        prefLabel_pattern = re.compile(r'skos:prefLabel:\s*["\']([^"\']+)["\']')
        definition_pattern = re.compile(r'skos:definition:\s*["\']([^"\']+)["\']')

        matches = prefLabel_pattern.findall(content)
        definitions = definition_pattern.findall(content)

        for i, term in enumerate(matches):
            if term not in TEMPLATE_TERMS:
                self.vocabulary[term] = definitions[i] if i < len(definitions) else ""

        if self.verbose:
            print(f"Loaded {len(self.vocabulary)} vocabulary terms")

        return True

    def check_terms(self, spec_path: Path) -> Tuple[int, int]:
        """
        Validate all skos:prefLabel values are compound.

        Returns: (error_count, warning_count)
        """
        if not self.load_vocabulary(spec_path):
            return (1, 0)

        error_count = 0
        warning_count = 0

        for term in self.vocabulary.keys():
            if term in TEMPLATE_TERMS:
                continue

            if COMPOUND_PATTERN.match(term):
                if self.verbose:
                    print(f"  ✓ {term}")
            elif ACRONYM_PATTERN.match(term):
                # Acronyms are acceptable but should have compound form
                warning_count += 1
                self.warnings.append(f"Acronym without compound form: {term}")
                if self.verbose:
                    print(f"  ⚠ {term} (acronym, consider compound form)")
            elif SINGLE_WORD_PATTERN.match(term):
                error_count += 1
                self.errors.append(f"Single-word prefLabel: {term}")
                print(f"  ✗ {term} (single word - violates R-VOC-TERM-001)")
            else:
                # Other patterns
                if '_' not in term:
                    error_count += 1
                    self.errors.append(f"Non-compound prefLabel: {term}")
                    print(f"  ✗ {term} (not compound - violates R-VOC-TERM-001)")
                elif self.verbose:
                    print(f"  ✓ {term}")

        return (error_count, warning_count)

    def check_prose(self, file_path: Path) -> Tuple[int, int]:
        """
        Validate prose usage of vocabulary terms.

        Returns: (error_count, warning_count)
        """
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return (1, 0)

        content = file_path.read_text()
        error_count = 0
        warning_count = 0

        # Check for lowercase usage of vocabulary terms
        for term in self.vocabulary.keys():
            # Create pattern for lowercase version
            lowercase_term = term.lower().replace('_', ' ')
            if lowercase_term in content.lower():
                # Check if it's actually lowercase (not the proper form)
                pattern = re.compile(rf'\b{re.escape(lowercase_term)}\b', re.IGNORECASE)
                matches = pattern.findall(content)
                for match in matches:
                    if match != term and match.lower() == lowercase_term:
                        warning_count += 1
                        self.warnings.append(f"Possible informal usage: '{match}' (should be '{term}')")

        # Check for inconsistent marking
        term_patterns = {}
        for term in self.vocabulary.keys():
            base = term.replace('_', ' ').lower()
            if base not in term_patterns:
                term_patterns[base] = []
            # Find all variations in document
            pattern = re.compile(rf'\b{re.escape(term)}\b|\b{re.escape(base)}\b', re.IGNORECASE)
            term_patterns[base].extend(pattern.findall(content))

        for base, usages in term_patterns.items():
            unique_usages = set(usages)
            if len(unique_usages) > 1:
                error_count += 1
                self.errors.append(f"Inconsistent marking: {unique_usages}")

        return (error_count, warning_count)

    def suggest_fix(self, term: str) -> Optional[str]:
        """Suggest compound form for a single-word term."""
        suggestions = {
            'Agent': 'Aget_Agent or Aget_Instance',
            'Session': 'Aget_Session',
            'Task': 'Task_Entity or Aget_Task',
            'Capability': 'Aget_Capability',
            'Template': 'Aget_Template',
            'Principal': 'Aget_Principal',
            'Artifact': 'Aget_Artifact',
            'Protocol': 'Protocol_Concept',
            'Algorithm': 'Algorithm_Concept',
            'Runbook': 'Runbook_Artifact',
            'Playbook': 'Playbook_Artifact',
            'SOP': 'SOP_Artifact',
        }
        return suggestions.get(term)

    def fix_mode(self, spec_path: Path) -> None:
        """Print suggested fixes for violations."""
        if not self.load_vocabulary(spec_path):
            return

        print("\n=== Suggested Fixes ===\n")

        for term in self.vocabulary.keys():
            if term in TEMPLATE_TERMS:
                continue

            if not COMPOUND_PATTERN.match(term) and not ACRONYM_PATTERN.match(term):
                suggestion = self.suggest_fix(term)
                if suggestion:
                    print(f"  {term} → {suggestion}")
                else:
                    print(f"  {term} → {term}_[Suffix] (suggest appropriate suffix)")

    def print_summary(self) -> None:
        """Print validation summary."""
        print(f"\n=== Summary ===")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print(f"\nErrors:")
            for err in self.errors:
                print(f"  - {err}")

        if self.warnings:
            print(f"\nWarnings:")
            for warn in self.warnings:
                print(f"  - {warn}")


def main():
    parser = argparse.ArgumentParser(
        description='AGET Vocabulary Prose Validator (L493)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--check-terms', action='store_true',
                        help='Validate prefLabel values are compound')
    parser.add_argument('--check-prose', action='store_true',
                        help='Validate prose usage of vocabulary terms')
    parser.add_argument('--fix', action='store_true',
                        help='Suggest fixes for violations')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('path', nargs='?',
                        default='specs/AGET_VOCABULARY_SPEC.md',
                        help='Path to vocabulary spec or document to check')

    args = parser.parse_args()

    if not any([args.check_terms, args.check_prose, args.fix]):
        parser.print_help()
        sys.exit(1)

    validator = VocabularyValidator(verbose=args.verbose)
    path = Path(args.path)

    # Find spec file if checking terms or prose
    spec_path = path if path.name.endswith('VOCABULARY_SPEC.md') else Path('specs/AGET_VOCABULARY_SPEC.md')

    exit_code = 0

    if args.check_terms:
        print(f"=== Checking Terms ({spec_path}) ===\n")
        errors, warnings = validator.check_terms(spec_path)
        if errors > 0:
            exit_code = 1

    if args.check_prose:
        print(f"\n=== Checking Prose ({path}) ===\n")
        if not validator.vocabulary:
            validator.load_vocabulary(spec_path)
        errors, warnings = validator.check_prose(path)
        if errors > 0:
            exit_code = 1

    if args.fix:
        validator.fix_mode(spec_path)

    validator.print_summary()

    if exit_code == 0:
        print("\n✓ Validation passed")
    else:
        print("\n✗ Validation failed")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
