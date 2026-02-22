#!/usr/bin/env python3
"""
validate_ontology_compliance.py - Template/Instance Ontology Compliance Validator

Validates that:
1. Templates have SKOS-compliant vocabularies in specs/
2. Instance vocabularies extend (not contradict) template vocabularies
3. Required SKOS properties are present
4. YAML ontology files contain required SKOS properties (CAP-INST-008)

Part of v3.3.0 release (G8.10, V8.14), extended v3.6.0 (CAP-INST-008).
Per L481 (Ontology-Driven Agent Creation) and L482 (SKOS+EARS Grounding).

Usage:
    # Validate template has vocabulary (Markdown + YAML)
    python3 validate_ontology_compliance.py --template template-researcher-aget

    # Validate instance extends template
    python3 validate_ontology_compliance.py --template template-researcher-aget --instance private-cli-aget

    # Validate all templates in a directory
    python3 validate_ontology_compliance.py --all --base-dir /path/to/aget-framework

    # Self-test
    python3 validate_ontology_compliance.py --test

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

# Try to import yaml; fall back gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


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


# --- YAML Ontology Validation (CAP-INST-008) ---


def find_yaml_ontology_files(template_path: Path) -> List[Path]:
    """Find YAML ontology files in a template's ontology/ directory."""
    ontology_dir = template_path / "ontology"
    if not ontology_dir.is_dir():
        return []
    files = []
    for f in ontology_dir.iterdir():
        if f.is_file() and f.suffix in ('.yaml', '.yml'):
            files.append(f)
    return sorted(files)


def parse_yaml_file(filepath: Path) -> Optional[dict]:
    """Parse a YAML file, returning None on failure."""
    if HAS_YAML:
        try:
            with open(filepath) as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    # Fallback: extract key fields using simple line parsing
    try:
        content = filepath.read_text(encoding='utf-8')
        data = {'concepts': []}
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('prefLabel:'):
                value = stripped.split(':', 1)[1].strip().strip('"\'')
                data['concepts'].append({'prefLabel': value})
            elif stripped.startswith('definition:'):
                value = stripped.split(':', 1)[1].strip().strip('"\'')
                if data['concepts']:
                    data['concepts'][-1]['definition'] = value
        return data
    except Exception:
        return None


def extract_yaml_concepts(data: dict) -> List[dict]:
    """Extract concepts from parsed YAML ontology data."""
    concepts = []

    # Handle top-level concepts list
    raw_concepts = data.get('concepts', [])
    if isinstance(raw_concepts, list):
        for c in raw_concepts:
            if isinstance(c, dict):
                concepts.append(c)

    # Handle conceptScheme.concepts (alternative structure)
    scheme = data.get('conceptScheme', {})
    if isinstance(scheme, dict):
        scheme_concepts = scheme.get('concepts', [])
        if isinstance(scheme_concepts, list):
            for c in scheme_concepts:
                if isinstance(c, dict):
                    concepts.append(c)

    return concepts


def validate_yaml_ontology(template_path: Path) -> ValidationResult:
    """Validate YAML ontology files for SKOS compliance (CAP-INST-008)."""
    result = ValidationResult(f"YAML Ontology: {template_path.name}")

    yaml_files = find_yaml_ontology_files(template_path)
    if not yaml_files:
        result.add_warning("No ontology/ directory or no YAML files found")
        return result

    result.add_pass(f"ontology/ directory with {len(yaml_files)} YAML file(s)")

    for yaml_file in yaml_files:
        data = parse_yaml_file(yaml_file)
        if data is None:
            result.add_fail(f"{yaml_file.name}: Failed to parse YAML")
            continue

        concepts = extract_yaml_concepts(data)
        if not concepts:
            result.add_fail(f"{yaml_file.name}: No concepts found")
            continue

        missing_prefLabel = 0
        missing_definition = 0

        for concept in concepts:
            if not concept.get('prefLabel'):
                missing_prefLabel += 1
            if not concept.get('definition'):
                missing_definition += 1

        if missing_prefLabel == 0:
            result.add_pass(f"{yaml_file.name}: All {len(concepts)} concepts have prefLabel")
        else:
            result.add_fail(
                f"{yaml_file.name}: {missing_prefLabel}/{len(concepts)} concepts missing prefLabel"
            )

        if missing_definition == 0:
            result.add_pass(f"{yaml_file.name}: All {len(concepts)} concepts have definition")
        else:
            result.add_fail(
                f"{yaml_file.name}: {missing_definition}/{len(concepts)} concepts missing definition"
            )

    return result


def run_self_test() -> bool:
    """Self-test to verify YAML validation behavior (CAP-INST-008)."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_ontology_compliance_test_'))
    passed = 0
    failed = 0

    try:
        # Set up mock template
        (test_dir / 'ontology').mkdir()
        (test_dir / 'specs').mkdir()

        # T1: Valid YAML ontology
        valid_yaml = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: test-ontology
  version: 1.0.0
concepts:
  - id: T001
    prefLabel: TestConcept
    definition: A test concept for validation
  - id: T002
    prefLabel: AnotherConcept
    definition: Another test concept
  - id: T003
    prefLabel: ThirdConcept
    definition: A third concept
"""
        (test_dir / 'ontology' / 'ONTOLOGY_test.yaml').write_text(valid_yaml)

        result = validate_yaml_ontology(test_dir)
        if result.success:
            print("  [+] T1 PASS: Valid YAML ontology accepted")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Valid YAML rejected: {result.failed}")
            failed += 1

        # T2: YAML with missing definition
        bad_yaml = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: bad-ontology
concepts:
  - id: B001
    prefLabel: BadConcept
  - id: B002
    prefLabel: OkConcept
    definition: This one is fine
"""
        (test_dir / 'ontology' / 'ONTOLOGY_bad.yaml').write_text(bad_yaml)

        result2 = validate_yaml_ontology(test_dir)
        has_missing_def = any('missing definition' in f for f in result2.failed)
        if has_missing_def:
            print("  [+] T2 PASS: Missing definition detected")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Expected missing definition finding")
            failed += 1

        # T3: Coverage reporting
        yaml_files = find_yaml_ontology_files(test_dir)
        md_file = find_vocabulary_file(test_dir)
        yaml_count = len(yaml_files)
        md_count = 1 if md_file else 0
        coverage = f"Checked: {yaml_count} YAML, {md_count} Markdown"
        if yaml_count == 2 and md_count == 0:
            print(f"  [+] T3 PASS: Coverage report correct ({coverage})")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected 2 YAML, 0 Markdown; got {coverage}")
            failed += 1

        # T4: No ontology directory
        empty_dir = Path(tempfile.mkdtemp(prefix='aget_empty_test_'))
        result4 = validate_yaml_ontology(empty_dir)
        has_warning = any('No ontology' in w for w in result4.warnings)
        shutil.rmtree(empty_dir)
        if has_warning:
            print("  [+] T4 PASS: Missing ontology/ handled gracefully")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: Expected warning for missing ontology/")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


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
        default=os.environ.get('AGET_FRAMEWORK_DIR', '.'),
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
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run self-test (CAP-INST-008)'
    )

    args = parser.parse_args()

    if args.test:
        print("validate_ontology_compliance.py self-test (CAP-INST-008)")
        success = run_self_test()
        sys.exit(0 if success else 1)

    base_dir = Path(args.base_dir)

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}", file=sys.stderr)
        sys.exit(2)

    results: List[ValidationResult] = []

    # Track format coverage (CAP-INST-008-03)
    yaml_files_checked = 0
    md_files_checked = 0

    if args.all:
        # Validate all templates
        templates = find_all_templates(base_dir)
        if not templates:
            print(f"No templates found in {base_dir}", file=sys.stderr)
            sys.exit(2)

        for template in templates:
            # Markdown vocabulary validation
            results.append(validate_template_vocabulary(template))
            if find_vocabulary_file(template):
                md_files_checked += 1

            # YAML ontology validation (CAP-INST-008-01)
            yaml_result = validate_yaml_ontology(template)
            results.append(yaml_result)
            yaml_files_checked += len(find_yaml_ontology_files(template))

    elif args.template:
        # Resolve template path
        template_path = Path(args.template)
        if not template_path.is_absolute():
            template_path = base_dir / args.template

        if not template_path.exists():
            print(f"Error: Template not found: {template_path}", file=sys.stderr)
            sys.exit(2)

        results.append(validate_template_vocabulary(template_path))
        if find_vocabulary_file(template_path):
            md_files_checked += 1

        # YAML ontology validation (CAP-INST-008-01)
        yaml_result = validate_yaml_ontology(template_path)
        results.append(yaml_result)
        yaml_files_checked += len(find_yaml_ontology_files(template_path))

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
            },
            "coverage": {
                "yaml_files": yaml_files_checked,
                "markdown_files": md_files_checked
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
        # CAP-INST-008-03: Format coverage report
        print(f"Checked: {yaml_files_checked} YAML, {md_files_checked} Markdown")
        print(f"{'='*50}")

    # Exit code
    if all(r.success for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
