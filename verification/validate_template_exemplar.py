#!/usr/bin/env python3
"""
Validate AGET Template Exemplar Compliance (v3.3)

Validates that a template meets all v3.3 exemplar requirements:
- Core files (AGENTS.md, CLAUDE.md symlink, README.md, etc.)
- Specification structure (required sections)
- Vocabulary structure (SKOS compliance)
- Shell integration (CAP-TPL-014)

Usage:
    python3 validate_template_exemplar.py --template template-supervisor-aget
    python3 validate_template_exemplar.py --all

Implements: CAP-TPL-014, R-REL-015, SOP_template_validation
"""

import argparse
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Default templates to validate
TEMPLATES = [
    "template-supervisor-aget",
    "template-worker-aget",
    "template-advisor-aget",
    "template-consultant-aget",
    "template-developer-aget",
    "template-spec-engineer-aget",
    "template-analyst-aget",
    "template-architect-aget",
    "template-researcher-aget",
]

# Base path for aget-framework
BASE_PATH = Path(__file__).parent.parent.parent


class ValidationResult:
    """Holds validation results."""

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []

    def add_pass(self, test: str):
        self.passed.append(test)

    def add_fail(self, test: str):
        self.failed.append(test)

    def add_warning(self, test: str):
        self.warnings.append(test)

    @property
    def is_valid(self) -> bool:
        return len(self.failed) == 0


def validate_core_files(template_path: Path) -> ValidationResult:
    """Validate core file structure."""
    result = ValidationResult()

    # Required files
    required_files = [
        ".aget/version.json",
        "AGENTS.md",
        "README.md",
    ]

    for f in required_files:
        if (template_path / f).exists():
            result.add_pass(f"Core file exists: {f}")
        else:
            result.add_fail(f"Missing core file: {f}")

    # CLAUDE.md must be symlink
    claude_md = template_path / "CLAUDE.md"
    if claude_md.is_symlink():
        result.add_pass("CLAUDE.md is symlink")
    elif claude_md.exists():
        result.add_fail("CLAUDE.md exists but is not a symlink")
    else:
        result.add_fail("CLAUDE.md does not exist")

    # Required directories
    required_dirs = [
        "specs",
        "shell",
        ".aget/evolution",
    ]

    for d in required_dirs:
        if (template_path / d).is_dir():
            result.add_pass(f"Directory exists: {d}")
        else:
            result.add_fail(f"Missing directory: {d}")

    return result


def validate_spec_structure(template_path: Path) -> ValidationResult:
    """Validate specification structure."""
    result = ValidationResult()

    # Find spec file
    specs_dir = template_path / "specs"
    spec_files = list(specs_dir.glob("*_SPEC.md"))

    if not spec_files:
        result.add_fail("No *_SPEC.md file found in specs/")
        return result

    spec_file = spec_files[0]
    result.add_pass(f"Spec file exists: {spec_file.name}")

    content = spec_file.read_text()

    # Required sections
    required_sections = [
        "## Abstract",
        "## Archetype Definition",
        "## Capabilities",
        "## Inviolables",
        "## EKO Classification",
        "## Archetype Constraints",
    ]

    for section in required_sections:
        if section in content:
            result.add_pass(f"Spec has section: {section}")
        else:
            result.add_fail(f"Spec missing section: {section}")

    # Check for at least 3 capabilities
    cap_count = len(re.findall(r"### CAP-", content))
    if cap_count >= 3:
        result.add_pass(f"Spec has {cap_count} capabilities (≥3)")
    else:
        result.add_fail(f"Spec has only {cap_count} capabilities (need ≥3)")

    return result


def validate_vocabulary_structure(template_path: Path) -> ValidationResult:
    """Validate vocabulary structure."""
    result = ValidationResult()

    # Find vocabulary file
    specs_dir = template_path / "specs"
    vocab_files = list(specs_dir.glob("*_VOCABULARY.md"))

    if not vocab_files:
        result.add_fail("No *_VOCABULARY.md file found in specs/")
        return result

    vocab_file = vocab_files[0]
    result.add_pass(f"Vocabulary file exists: {vocab_file.name}")

    content = vocab_file.read_text()

    # Required sections
    required_sections = [
        "## Concept Scheme",
        "## Core Concepts",
        "## Concept Relationships",
        "## EKO Cross-References",
    ]

    for section in required_sections:
        if section in content:
            result.add_pass(f"Vocabulary has section: {section}")
        else:
            result.add_fail(f"Vocabulary missing section: {section}")

    # Check SKOS compliance (at least 5 concepts)
    preflabel_count = len(re.findall(r"skos:prefLabel", content))
    if preflabel_count >= 6:  # 1 scheme + 5 concepts
        result.add_pass(f"Vocabulary has {preflabel_count} SKOS prefLabels (≥6)")
    else:
        result.add_fail(f"Vocabulary has only {preflabel_count} prefLabels (need ≥6)")

    return result


def validate_shell_integration(template_path: Path) -> ValidationResult:
    """Validate shell integration (CAP-TPL-014)."""
    result = ValidationResult()

    shell_dir = template_path / "shell"

    # Check for profile file
    profile_files = list(shell_dir.glob("*_profile.zsh"))

    if not profile_files:
        result.add_fail("No *_profile.zsh file found in shell/")
        return result

    profile_file = profile_files[0]
    result.add_pass(f"Shell profile exists: {profile_file.name}")

    content = profile_file.read_text()

    # Required functions
    if "aget_info()" in content:
        result.add_pass("Profile has aget_info() function")
    else:
        result.add_fail("Profile missing aget_info() function")

    if "aget_docs()" in content:
        result.add_pass("Profile has aget_docs() function")
    else:
        result.add_fail("Profile missing aget_docs() function")

    # Required variables
    if "AGET_SPEC=" in content or "AGET_SPEC}" in content:
        result.add_pass("Profile defines AGET_SPEC path")
    else:
        result.add_fail("Profile missing AGET_SPEC definition")

    if "AGET_VOCAB=" in content or "AGET_VOCAB}" in content:
        result.add_pass("Profile defines AGET_VOCAB path")
    else:
        result.add_fail("Profile missing AGET_VOCAB definition")

    # Check for shell README
    readme = shell_dir / "README.md"
    if readme.exists():
        result.add_pass("Shell README.md exists")
    else:
        result.add_fail("Shell README.md missing")

    return result


def validate_template(template_name: str) -> Tuple[str, ValidationResult]:
    """Validate a single template."""
    template_path = BASE_PATH / template_name

    if not template_path.exists():
        result = ValidationResult()
        result.add_fail(f"Template directory not found: {template_path}")
        return template_name, result

    combined = ValidationResult()

    # Run all validations
    for validator in [
        validate_core_files,
        validate_spec_structure,
        validate_vocabulary_structure,
        validate_shell_integration,
    ]:
        result = validator(template_path)
        combined.passed.extend(result.passed)
        combined.failed.extend(result.failed)
        combined.warnings.extend(result.warnings)

    return template_name, combined


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET template exemplar compliance"
    )
    parser.add_argument(
        "--template", "-t",
        help="Template to validate (e.g., template-supervisor-aget)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Validate all 9 templates"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all passed tests"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if not args.template and not args.all:
        parser.print_help()
        sys.exit(1)

    templates = TEMPLATES if args.all else [args.template]

    results: Dict[str, ValidationResult] = {}

    for template in templates:
        name, result = validate_template(template)
        results[name] = result

    # Output results
    if args.json:
        import json
        output = {
            name: {
                "passed": len(r.passed),
                "failed": len(r.failed),
                "valid": r.is_valid,
                "failures": r.failed,
            }
            for name, r in results.items()
        }
        print(json.dumps(output, indent=2))
    else:
        total_pass = 0
        total_fail = 0

        for name, result in results.items():
            print(f"\n{'='*60}")
            print(f"Template: {name}")
            print(f"{'='*60}")

            if args.verbose:
                for p in result.passed:
                    print(f"  [PASS] {p}")

            for f in result.failed:
                print(f"  [FAIL] {f}")

            status = "VALID" if result.is_valid else "INVALID"
            print(f"\n  Status: {status} ({len(result.passed)} passed, {len(result.failed)} failed)")

            total_pass += len(result.passed)
            total_fail += len(result.failed)

        print(f"\n{'='*60}")
        print(f"SUMMARY: {total_pass} passed, {total_fail} failed")
        all_valid = all(r.is_valid for r in results.values())
        print(f"Overall: {'ALL VALID' if all_valid else 'SOME INVALID'}")
        print(f"{'='*60}")

        sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
