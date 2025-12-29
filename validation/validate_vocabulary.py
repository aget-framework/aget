#!/usr/bin/env python3
"""
Validate AGET Vocabulary (SKOS).

Implements: CAP-VOC-001 (Vocabulary_Compliance), ADR-001 (SKOS adoption), CAP-VAL-002
Traces to: AGET_GLOSSARY_STANDARD_SPEC_v1.0.md, AGET_CONTROLLED_VOCABULARY.md

Validates Vocabulary files against AGET Glossary Standard (SKOS-based).

Conformance Levels:
    Level 1 (Basic): skos:prefLabel + skos:definition required
    Level 2 (Standard): + hierarchy + examples + lifecycle
    Level 3 (Full SKOS): + all AGET extensions + Validation

Usage:
    python validate_vocabulary.py <vocabulary_file>
    python validate_vocabulary.py --level 2 <vocabulary_file>
    python validate_vocabulary.py --help

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# SKOS Core Properties
SKOS_REQUIRED_L1 = {"skos:prefLabel", "skos:definition"}
SKOS_OPTIONAL = {
    "skos:altLabel", "skos:broader", "skos:narrower",
    "skos:related", "skos:example", "skos:notation"
}

# AGET Extension Properties
AGET_RELATIONSHIP_PROPERTIES = {
    "aget:has", "aget:operatesWithin", "aget:derivedFrom",
    "aget:requires", "aget:supervises", "aget:coordinatesWith",
    "aget:defines", "aget:exhibits"
}

AGET_METADATA_PROPERTIES = {
    "aget:technicalTerm", "aget:characteristics", "aget:distinguishedFrom",
    "aget:antiPattern", "aget:location", "aget:structure",
    "aget:whyItMatters", "aget:validationRule", "aget:deprecation",
    "aget:preconditions", "aget:postconditions", "aget:triggers"
}


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.term_count: int = 0
        self.level_achieved: int = 0

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_info(self, msg: str):
        self.info.append(msg)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.is_valid,
            "level_achieved": self.level_achieved,
            "term_count": self.term_count,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }


def parse_markdown_vocabulary(content: str) -> Dict[str, Dict[str, Any]]:
    """Parse vocabulary from Markdown format."""
    terms = {}
    current_term = None
    current_data = {}

    lines = content.split('\n')

    for line in lines:
        # Term header: ### Term_Name or #### Term_Name
        term_match = re.match(r'^#{2,4}\s+(.+?)(?:\s+\(DEPRECATED\))?$', line.strip())
        if term_match:
            if current_term:
                terms[current_term] = current_data
            current_term = term_match.group(1).strip()
            current_data = {"skos:prefLabel": current_term}
            continue

        if current_term:
            # Definition: **Definition**: ...
            def_match = re.match(r'\*\*Definition\*\*:\s*(.+)', line)
            if def_match:
                current_data["skos:definition"] = def_match.group(1)

            # Also known as: **Also known as**: ...
            aka_match = re.match(r'\*\*Also known as\*\*:\s*(.+)', line)
            if aka_match:
                aliases = [a.strip() for a in aka_match.group(1).split(',')]
                current_data["skos:altLabel"] = aliases

            # Example: **Example**: ...
            example_match = re.match(r'\*\*Example\*\*:\s*(.+)', line)
            if example_match:
                current_data["skos:example"] = example_match.group(1)

    if current_term:
        terms[current_term] = current_data

    return terms


def parse_yaml_vocabulary(content: str) -> Dict[str, Dict[str, Any]]:
    """Parse vocabulary from YAML format."""
    if not HAS_YAML:
        raise ImportError("PyYAML required for YAML parsing. Install with: pip install pyyaml")

    data = yaml.safe_load(content)

    if not data:
        return {}

    # Handle different YAML structures
    if "terms" in data:
        return data["terms"]
    elif "concepts" in data:
        return data["concepts"]
    elif "vocabulary" in data:
        vocab = data["vocabulary"]
        if isinstance(vocab, dict) and "terms" in vocab:
            return vocab["terms"]
        return vocab
    else:
        # Assume top-level is terms
        # Filter out metadata keys
        metadata_keys = {"metadata", "namespaces", "concept_scheme", "version", "status"}
        return {k: v for k, v in data.items() if k not in metadata_keys and isinstance(v, dict)}


def parse_table_vocabulary(content: str) -> Dict[str, Dict[str, Any]]:
    """Parse vocabulary from Markdown table format."""
    terms = {}

    # Find tables with Term | Definition pattern
    table_pattern = r'\|\s*`?([A-Z][a-z_A-Z]+)`?\s*\|\s*(.+?)\s*\|'

    for match in re.finditer(table_pattern, content):
        term = match.group(1).strip('`')
        definition = match.group(2).strip()

        # Skip header rows
        if definition.startswith('-') or definition.lower() == 'definition':
            continue

        terms[term] = {
            "skos:prefLabel": term,
            "skos:definition": definition
        }

    return terms


def load_vocabulary(filepath: Path) -> Tuple[Dict[str, Dict[str, Any]], str]:
    """Load vocabulary from file, detecting format."""
    content = filepath.read_text()

    if filepath.suffix in ['.yaml', '.yml']:
        return parse_yaml_vocabulary(content), "yaml"
    elif filepath.suffix == '.md':
        # Try table format first (AGET_CONTROLLED_VOCABULARY uses tables)
        table_terms = parse_table_vocabulary(content)
        if table_terms:
            return table_terms, "markdown_table"

        # Fall back to header-based format
        return parse_markdown_vocabulary(content), "markdown"
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def validate_level1(terms: Dict[str, Dict[str, Any]], result: ValidationResult):
    """Validate Level 1 (Basic) conformance."""
    for term_name, term_data in terms.items():
        # Check required properties
        if not term_data.get("skos:prefLabel"):
            result.add_error(f"[{term_name}] Missing required: skos:prefLabel")

        if not term_data.get("skos:definition"):
            result.add_error(f"[{term_name}] Missing required: skos:definition")

    if not result.errors:
        result.level_achieved = 1


def validate_level2(terms: Dict[str, Dict[str, Any]], result: ValidationResult):
    """Validate Level 2 (Standard) conformance."""
    validate_level1(terms, result)

    if result.errors:
        return

    # Check hierarchy consistency
    broader_refs = set()
    narrower_refs = set()
    term_names = set(terms.keys())

    for term_name, term_data in terms.items():
        broader = term_data.get("skos:broader")
        if broader:
            if isinstance(broader, str):
                broader_refs.add((term_name, broader))
            elif isinstance(broader, list):
                for b in broader:
                    broader_refs.add((term_name, b))

        narrower = term_data.get("skos:narrower")
        if narrower:
            if isinstance(narrower, str):
                narrower_refs.add((term_name, narrower))
            elif isinstance(narrower, list):
                for n in narrower:
                    narrower_refs.add((term_name, n))

    # Check bidirectional consistency (warning, not error for L2)
    for child, parent in broader_refs:
        if parent in term_names:
            if (parent, child) not in narrower_refs:
                result.add_warning(
                    f"[{child}] skos:broader '{parent}' lacks inverse skos:narrower"
                )

    # Check for examples (recommended)
    terms_without_examples = [
        name for name, data in terms.items()
        if not data.get("skos:example")
    ]
    if len(terms_without_examples) > len(terms) * 0.5:
        result.add_warning(
            f"{len(terms_without_examples)}/{len(terms)} terms lack examples"
        )

    result.level_achieved = 2


def validate_level3(terms: Dict[str, Dict[str, Any]], result: ValidationResult):
    """Validate Level 3 (Full SKOS) conformance."""
    validate_level2(terms, result)

    if result.level_achieved < 2:
        return

    term_names = set(terms.keys())

    for term_name, term_data in terms.items():
        # Check Aget_* terms have broader
        if term_name.startswith("Aget_"):
            if not term_data.get("skos:broader"):
                result.add_error(
                    f"[{term_name}] Aget_* terms require skos:broader"
                )

        # Check hierarchy integrity
        broader = term_data.get("skos:broader")
        if broader:
            if isinstance(broader, str) and broader not in term_names:
                result.add_warning(
                    f"[{term_name}] skos:broader '{broader}' not defined"
                )

        # Check symmetric relationships
        coordinates = term_data.get("aget:coordinatesWith")
        if coordinates:
            coords = [coordinates] if isinstance(coordinates, str) else coordinates
            for coord in coords:
                if coord in term_names:
                    other_coords = terms[coord].get("aget:coordinatesWith", [])
                    if isinstance(other_coords, str):
                        other_coords = [other_coords]
                    if term_name not in other_coords:
                        result.add_warning(
                            f"[{term_name}] aget:coordinatesWith '{coord}' lacks inverse"
                        )

        # Check deprecation has replacement
        deprecation = term_data.get("aget:deprecation")
        if deprecation:
            if isinstance(deprecation, dict):
                if deprecation.get("status") == "deprecated":
                    if not deprecation.get("replacement"):
                        result.add_warning(
                            f"[{term_name}] Deprecated term lacks replacement"
                        )

    if not any(e for e in result.errors if "Aget_*" in e):
        result.level_achieved = 3


def validate_vocabulary(
    filepath: Path,
    target_level: int = 2
) -> ValidationResult:
    """
    Validate vocabulary file against AGET Glossary Standard.

    Args:
        filepath: Path to vocabulary file
        target_level: Target conformance level (1, 2, or 3)

    Returns:
        ValidationResult with errors, warnings, and achieved level
    """
    result = ValidationResult()

    try:
        terms, format_type = load_vocabulary(filepath)
        result.add_info(f"Parsed {len(terms)} terms from {format_type} format")
        result.term_count = len(terms)
    except Exception as e:
        result.add_error(f"Failed to parse vocabulary: {e}")
        return result

    if not terms:
        result.add_error("No terms found in vocabulary")
        return result

    # Validate at target level
    if target_level >= 1:
        validate_level1(terms, result)
    if target_level >= 2 and result.level_achieved >= 1:
        validate_level2(terms, result)
    if target_level >= 3 and result.level_achieved >= 2:
        validate_level3(terms, result)

    return result


def format_report(filepath: Path, result: ValidationResult) -> str:
    """Format validation report."""
    lines = [
        f"\n{'='*60}",
        f"Vocabulary Validation Report",
        f"{'='*60}",
        f"File: {filepath}",
        f"Terms: {result.term_count}",
        f"Level Achieved: {result.level_achieved}",
        f"Status: {'PASS' if result.is_valid else 'FAIL'}",
        f"{'='*60}",
    ]

    if result.info:
        lines.append("\nInfo:")
        for msg in result.info:
            lines.append(f"  {msg}")

    if result.errors:
        lines.append(f"\nErrors ({len(result.errors)}):")
        for msg in result.errors:
            lines.append(f"  [ERROR] {msg}")

    if result.warnings:
        lines.append(f"\nWarnings ({len(result.warnings)}):")
        for msg in result.warnings:
            lines.append(f"  [WARN] {msg}")

    if result.is_valid:
        lines.append(f"\n✓ Vocabulary passes Level {result.level_achieved} validation")
    else:
        lines.append(f"\n✗ Vocabulary fails validation")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate AGET vocabulary against Glossary Standard (SKOS-based)"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Vocabulary file to validate (.md or .yaml)"
    )
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Target conformance level (default: 2)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if validation fails"
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    result = validate_vocabulary(args.file, args.level)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_report(args.file, result))

    if args.strict and not result.is_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
