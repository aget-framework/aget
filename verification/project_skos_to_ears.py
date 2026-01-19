#!/usr/bin/env python3
"""
SKOS to EARS Vocabulary Projector

Converts AGET SKOS-based vocabulary to simple EARS vocabulary format.

EARS vocabulary format is minimal:
    vocabulary:
      Term_Name:
        definition: "..."

SKOS format is richer (per ADR-001):
    Term_Name:
      skos:prefLabel: "Term_Name"
      skos:definition: "..."
      skos:broader: "Parent"
      aget:has: [...]

This tool projects SKOS → EARS by extracting only prefLabel + definition.

Usage:
    python project_skos_to_ears.py <skos_vocabulary.yaml>
    python project_skos_to_ears.py <vocabulary.md> --output ears_vocab.yaml
    python project_skos_to_ears.py --help

Reference:
    AGET_GLOSSARY_STANDARD_SPEC_v1.0.md
    ADR-001: Controlled Vocabulary Standard Selection
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_markdown_vocabulary(content: str) -> Dict[str, Dict[str, Any]]:
    """Parse vocabulary from Markdown format."""
    terms = {}

    # Try table format first (| Term | Definition |)
    table_pattern = r'\|\s*`?([A-Z][a-z_A-Z]+)`?\s*\|\s*(.+?)\s*\|'
    for match in re.finditer(table_pattern, content):
        term = match.group(1).strip('`')
        definition = match.group(2).strip()
        if definition.startswith('-') or definition.lower() == 'definition':
            continue
        terms[term] = {
            "skos:prefLabel": term,
            "skos:definition": definition
        }

    if terms:
        return terms

    # Fall back to header-based format
    current_term = None
    current_data = {}

    for line in content.split('\n'):
        term_match = re.match(r'^#{2,4}\s+(.+?)(?:\s+\(DEPRECATED\))?$', line.strip())
        if term_match:
            if current_term:
                terms[current_term] = current_data
            current_term = term_match.group(1).strip()
            current_data = {"skos:prefLabel": current_term}
            continue

        if current_term:
            def_match = re.match(r'\*\*Definition\*\*:\s*(.+)', line)
            if def_match:
                current_data["skos:definition"] = def_match.group(1)

    if current_term:
        terms[current_term] = current_data

    return terms


def parse_yaml_vocabulary(content: str) -> Dict[str, Dict[str, Any]]:
    """Parse vocabulary from YAML format."""
    if not HAS_YAML:
        raise ImportError("PyYAML required. Install with: pip install pyyaml")

    data = yaml.safe_load(content)

    if not data:
        return {}

    # Handle different structures
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
        metadata_keys = {"metadata", "namespaces", "concept_scheme", "version", "status"}
        return {k: v for k, v in data.items() if k not in metadata_keys and isinstance(v, dict)}


def load_vocabulary(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Load vocabulary from file."""
    content = filepath.read_text()

    if filepath.suffix in ['.yaml', '.yml']:
        return parse_yaml_vocabulary(content)
    elif filepath.suffix == '.md':
        return parse_markdown_vocabulary(content)
    else:
        raise ValueError(f"Unsupported format: {filepath.suffix}")


def project_to_ears(terms: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    """
    Project SKOS vocabulary to EARS format.

    EARS format: Term_Name: { definition: "..." }

    Projection rules:
    - Extract skos:prefLabel as term key
    - Extract skos:definition as definition value
    - Optionally include skos:example
    - Discard all other SKOS/AGET properties
    """
    ears_vocab = {}

    for term_name, term_data in terms.items():
        # Get term name (prefer explicit prefLabel)
        pref_label = term_data.get("skos:prefLabel", term_name)

        # Get definition
        definition = term_data.get("skos:definition", "")

        if not definition:
            # Skip terms without definition
            continue

        ears_entry = {"definition": definition}

        # Optionally include examples
        example = term_data.get("skos:example")
        if example:
            if isinstance(example, list):
                ears_entry["examples"] = example
            else:
                ears_entry["example"] = example

        ears_vocab[pref_label] = ears_entry

    return ears_vocab


def format_ears_yaml(ears_vocab: Dict[str, Dict[str, str]]) -> str:
    """Format EARS vocabulary as YAML."""
    if HAS_YAML:
        output = {"vocabulary": ears_vocab}
        return yaml.dump(output, default_flow_style=False, sort_keys=False, allow_unicode=True)
    else:
        # Manual YAML formatting
        lines = ["vocabulary:"]
        for term, data in sorted(ears_vocab.items()):
            lines.append(f"  {term}:")
            definition = data.get("definition", "")
            # Escape quotes in definition
            definition = definition.replace('"', '\\"')
            lines.append(f'    definition: "{definition}"')
        return "\n".join(lines)


def format_ears_markdown(ears_vocab: Dict[str, Dict[str, str]]) -> str:
    """Format EARS vocabulary as Markdown table."""
    lines = [
        "# Vocabulary",
        "",
        "| Term | Definition |",
        "|------|------------|",
    ]

    for term, data in sorted(ears_vocab.items()):
        definition = data.get("definition", "")
        # Truncate long definitions for table
        if len(definition) > 80:
            definition = definition[:77] + "..."
        lines.append(f"| `{term}` | {definition} |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Project SKOS vocabulary to EARS format"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="SKOS vocabulary file (.yaml or .md)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["yaml", "markdown"],
        default="yaml",
        help="Output format (default: yaml)"
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        terms = load_vocabulary(args.file)
    except Exception as e:
        print(f"Error loading vocabulary: {e}", file=sys.stderr)
        sys.exit(1)

    if not terms:
        print("Warning: No terms found in vocabulary", file=sys.stderr)
        sys.exit(0)

    ears_vocab = project_to_ears(terms)

    print(f"# Projected {len(ears_vocab)} terms from {len(terms)} SKOS entries",
          file=sys.stderr)

    if args.format == "yaml":
        output = format_ears_yaml(ears_vocab)
    else:
        output = format_ears_markdown(ears_vocab)

    if args.output:
        args.output.write_text(output)
        print(f"# Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
