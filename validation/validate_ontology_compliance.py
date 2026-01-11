#!/usr/bin/env python3
"""
validate_ontology_compliance.py - Template/Instance Ontology Compliance Validator

Validates that:
1. Templates have SKOS-compliant vocabularies in specs/
2. Instance vocabularies extend (not contradict) template vocabularies
3. Required SKOS properties are present

Part of v3.3.0 release (G8.10, V8.14).
Per L481 (Ontology-Driven Agent Creation) and L482 (SKOS+EARS Grounding).

Usage:
    # Validate template has vocabulary
    python3 validate_ontology_compliance.py --template template-researcher-aget

    # Validate instance extends template
    python3 validate_ontology_compliance.py --template template-researcher-aget --instance private-cli-aget

    # Validate all templates in a directory
    python3 validate_ontology_compliance.py --all --base-dir /path/to/aget-framework

Exit codes:
    0 - All validations pass
    1 - Validation failures
    2 - Configuration/usage error
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# SKOS properties that indicate compliance
REQUIRED_SKOS_PROPERTIES = {
    'skos:prefLabel',
    'skos:definition',
}

OPTIONAL_SKOS_PROPERTIES = {
    'skos:broader',
    'skos:narrower',
    'skos:related',
    'skos:inScheme',
    'skos:hasTopConcept',
    'skos:altLabel',
    'skos:example',
    'skos:note',
    'skos:scopeNote',
}

# Minimum SKOS definitions for a valid vocabulary
MIN_SKOS_DEFINITIONS = 3


class ValidationResult:
    """Container for validation results."""

    def __init__(self, name: str):
        self.name = name
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []

    @property
    def success(self) -> bool:
        return len(self.failed) == 0

    def add_pass(self, message: str):
        self.passed.append(message)

    def add_fail(self, message: str):
        self.failed.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def __str__(self) -> str:
        lines = [f"\n=== {self.name} ==="]

        if self.passed:
            lines.append(f"\n✅ Passed ({len(self.passed)}):")
            for p in self.passed:
                lines.append(f"   - {p}")

        if self.warnings:
            lines.append(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"   - {w}")

        if self.failed:
            lines.append(f"\n❌ Failed ({len(self.failed)}):")
            for f in self.failed:
                lines.append(f"   - {f}")

        status = "PASS" if self.success else "FAIL"
        lines.append(f"\nResult: {status}")

        return "\n".join(lines)


def find_vocabulary_file(template_path: Path) -> Optional[Path]:
    """Find the vocabulary file in a template's specs/ directory."""
    specs_dir = template_path / "specs"
    if not specs_dir.exists():
        return None

    # Look for *_VOCABULARY.md files
    vocab_files = list(specs_dir.glob("*_VOCABULARY.md"))
    if vocab_files:
        return vocab_files[0]

    return None


def extract_skos_concepts(content: str) -> Dict[str, Dict[str, str]]:
    """Extract SKOS concepts from markdown vocabulary file."""
    concepts = {}

    # Pattern to match YAML blocks with SKOS properties
    yaml_block_pattern = r'```yaml\s*([\s\S]*?)```'

    for match in re.finditer(yaml_block_pattern, content):
        yaml_content = match.group(1)

        # Extract concept name (first non-indented line ending with :)
        concept_match = re.search(r'^(\w+):\s*$', yaml_content, re.MULTILINE)
        if concept_match:
            concept_name = concept_match.group(1)
            concepts[concept_name] = {}

            # Extract SKOS properties
            for prop in REQUIRED_SKOS_PROPERTIES | OPTIONAL_SKOS_PROPERTIES:
                prop_pattern = rf'{re.escape(prop)}:\s*["\']?([^"\'\n]+)["\']?'
                prop_match = re.search(prop_pattern, yaml_content)
                if prop_match:
                    concepts[concept_name][prop] = prop_match.group(1).strip()

    return concepts


def count_skos_definitions(content: str) -> int:
    """Count number of skos:definition entries in content."""
    return len(re.findall(r'skos:definition', content))


def validate_template_vocabulary(template_path: Path) -> ValidationResult:
    """Validate that a template has a SKOS-compliant vocabulary."""
    result = ValidationResult(f"Template: {template_path.name}")

    # Check specs/ directory exists
    specs_dir = template_path / "specs"
    if not specs_dir.exists():
        result.add_fail(f"Missing specs/ directory")
        return result
    result.add_pass("specs/ directory exists")

    # Find vocabulary file
    vocab_file = find_vocabulary_file(template_path)
    if not vocab_file:
        result.add_fail("No *_VOCABULARY.md file found in specs/")
        return result
    result.add_pass(f"Vocabulary file found: {vocab_file.name}")

    # Read and validate content
    content = vocab_file.read_text()

    # Check for minimum SKOS definitions
    def_count = count_skos_definitions(content)
    if def_count >= MIN_SKOS_DEFINITIONS:
        result.add_pass(f"SKOS definitions: {def_count} (minimum: {MIN_SKOS_DEFINITIONS})")
    else:
        result.add_fail(f"Insufficient SKOS definitions: {def_count} (minimum: {MIN_SKOS_DEFINITIONS})")

    # Check for required SKOS properties
    for prop in REQUIRED_SKOS_PROPERTIES:
        if prop in content:
            result.add_pass(f"Contains {prop}")
        else:
            result.add_fail(f"Missing required property: {prop}")

    # Check for ConceptScheme
    if 'skos:ConceptScheme' in content or 'ConceptScheme' in content:
        result.add_pass("Has ConceptScheme")
    else:
        result.add_warning("No explicit ConceptScheme defined")

    # Check for broader/narrower hierarchy
    if 'skos:broader' in content or 'skos:narrower' in content:
        result.add_pass("Has concept hierarchy (broader/narrower)")
    else:
        result.add_warning("No concept hierarchy defined")

    # Extract and count concepts
    concepts = extract_skos_concepts(content)
    if concepts:
        result.add_pass(f"Concepts extracted: {len(concepts)}")
    else:
        result.add_warning("Could not extract YAML concept blocks")

    return result


def validate_instance_extends_template(
    template_path: Path,
    instance_path: Path
) -> ValidationResult:
    """Validate that instance vocabulary extends template vocabulary."""
    result = ValidationResult(
        f"Instance Extension: {instance_path.name} extends {template_path.name}"
    )

    # Get template vocabulary
    template_vocab = find_vocabulary_file(template_path)
    if not template_vocab:
        result.add_fail(f"Template {template_path.name} has no vocabulary")
        return result

    # Get instance vocabulary
    instance_vocab = find_vocabulary_file(instance_path)
    if not instance_vocab:
        result.add_fail(f"Instance {instance_path.name} has no vocabulary")
        return result

    result.add_pass(f"Both vocabularies found")

    # Extract concepts
    template_concepts = extract_skos_concepts(template_vocab.read_text())
    instance_concepts = extract_skos_concepts(instance_vocab.read_text())

    if not template_concepts:
        result.add_warning("Could not extract template concepts for comparison")
        return result

    if not instance_concepts:
        result.add_warning("Could not extract instance concepts for comparison")
        return result

    # Check that instance doesn't redefine template concepts with different definitions
    contradictions = []
    extensions = []

    for concept, props in instance_concepts.items():
        if concept in template_concepts:
            template_def = template_concepts[concept].get('skos:definition', '')
            instance_def = props.get('skos:definition', '')

            if template_def and instance_def and template_def != instance_def:
                contradictions.append(
                    f"{concept}: template='{template_def[:50]}...' vs instance='{instance_def[:50]}...'"
                )
        else:
            extensions.append(concept)

    if contradictions:
        for c in contradictions:
            result.add_fail(f"Definition contradiction: {c}")
    else:
        result.add_pass("No definition contradictions")

    if extensions:
        result.add_pass(f"Instance extends template with {len(extensions)} new concepts")

    return result


def find_all_templates(base_dir: Path) -> List[Path]:
    """Find all template directories in base directory."""
    templates = []
    for d in base_dir.iterdir():
        if d.is_dir() and d.name.startswith('template-') and d.name.endswith('-aget'):
            templates.append(d)
    return sorted(templates)


def main():
    parser = argparse.ArgumentParser(
        description='Validate template/instance ontology compliance (SKOS)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--template',
        help='Template directory name or path'
    )
    parser.add_argument(
        '--instance',
        help='Instance directory name or path (validates extension)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all templates in base directory'
    )
    parser.add_argument(
        '--base-dir',
        default=os.environ.get('AGET_FRAMEWORK_DIR', '/Users/gabormelli/github/aget-framework'),
        help='Base directory containing templates (default: AGET_FRAMEWORK_DIR or ~/github/aget-framework)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only show failures and summary'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    base_dir = Path(args.base_dir)

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}", file=sys.stderr)
        sys.exit(2)

    results: List[ValidationResult] = []

    if args.all:
        # Validate all templates
        templates = find_all_templates(base_dir)
        if not templates:
            print(f"No templates found in {base_dir}", file=sys.stderr)
            sys.exit(2)

        for template in templates:
            results.append(validate_template_vocabulary(template))

    elif args.template:
        # Resolve template path
        template_path = Path(args.template)
        if not template_path.is_absolute():
            template_path = base_dir / args.template

        if not template_path.exists():
            print(f"Error: Template not found: {template_path}", file=sys.stderr)
            sys.exit(2)

        results.append(validate_template_vocabulary(template_path))

        # If instance specified, validate extension
        if args.instance:
            instance_path = Path(args.instance)
            if not instance_path.is_absolute():
                instance_path = base_dir / args.instance

            if not instance_path.exists():
                print(f"Error: Instance not found: {instance_path}", file=sys.stderr)
                sys.exit(2)

            results.append(validate_instance_extends_template(template_path, instance_path))

    else:
        parser.print_help()
        sys.exit(2)

    # Output results
    if args.json:
        import json
        output = {
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "passed": r.passed,
                    "failed": r.failed,
                    "warnings": r.warnings
                }
                for r in results
            ],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success)
            }
        }
        print(json.dumps(output, indent=2))
    else:
        for result in results:
            if not args.quiet or not result.success:
                print(result)

        # Summary
        total = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total - passed

        print(f"\n{'='*50}")
        print(f"Summary: {passed}/{total} passed, {failed}/{total} failed")
        print(f"{'='*50}")

    # Exit code
    if all(r.success for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
