#!/usr/bin/env python3
"""
generate_readme.py - Generate README.md from AGET specifications

This script generates a Standard Readme compliant README.md from:
- AGET_IDENTITY_SPEC.yaml (identity, philosophy, definitions)
- AGET_POSITIONING_SPEC.yaml (platforms, differentiators, strategic context)

Usage:
    python3 generate_readme.py                    # Generate to stdout
    python3 generate_readme.py --output README.md # Write to file
    python3 generate_readme.py --verify           # Verify specs exist
    python3 generate_readme.py --dry-run          # Show what would be generated

Implements: PROJECT_PLAN_spec_first_documentation_v1.0.md Gate 4
Related: L545 (Strategic Positioning Evolution)
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_spec(spec_path: Path) -> dict:
    """Load a YAML specification file."""
    if not spec_path.exists():
        raise FileNotFoundError(f"Specification not found: {spec_path}")

    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)


def generate_readme(identity_spec: dict, positioning_spec: dict) -> str:
    """Generate README content from specifications."""

    # Extract identity fields
    identity = identity_spec.get('identity', {})
    full_name = identity.get('full_name', 'AGET Framework')
    short_def = identity.get('definition', {}).get('short', '')
    full_def = identity.get('definition', {}).get('full', '')
    philosophy = identity.get('core_philosophy', {})
    not_defs = identity.get('not_definition', [])

    # Extract positioning fields
    positioning = positioning_spec.get('positioning', {})
    platforms = positioning.get('relationship_to_platforms', {}).get('platforms', [])
    differentiators = positioning.get('differentiators', [])
    evolution = positioning.get('evolution_trajectory', {})
    thesis = positioning.get('strategic_thesis', {})

    # Build README content
    lines = []

    # Title
    lines.append(f"# {full_name}")
    lines.append("")

    # Short description (badge line would go here)
    lines.append(f"> {short_def}")
    lines.append("")

    # What is AGET?
    lines.append("## What is AGET?")
    lines.append("")
    lines.append(full_def.strip())
    lines.append("")

    # Philosophy
    lines.append("## Philosophy")
    lines.append("")
    primary = philosophy.get('primary', '')
    lines.append(f"**{primary}**")
    lines.append("")

    principles = philosophy.get('principles', [])
    for p in principles:
        name = p.get('name', '')
        statement = p.get('statement', '')
        lines.append(f"- **{name}**: {statement}")
    lines.append("")

    # What AGET is NOT
    if not_defs:
        lines.append("## What AGET is NOT")
        lines.append("")
        for nd in not_defs:
            if isinstance(nd, dict):
                statement = nd.get('statement', '')
                clarification = nd.get('clarification', '')
                lines.append(f"- **{statement}** — {clarification}")
            else:
                lines.append(f"- {nd}")
        lines.append("")

    # Supported Platforms
    if platforms:
        lines.append("## Supported Platforms")
        lines.append("")
        lines.append("AGET works across CLI agent platforms:")
        lines.append("")
        lines.append("| Platform | Type | Integration |")
        lines.append("|----------|------|-------------|")
        for p in platforms:
            name = p.get('name', '')
            ptype = p.get('type', '')
            integration = p.get('integration_mechanism', p.get('integration', 'TBD'))
            lines.append(f"| {name} | {ptype} | `{integration}` |")
        lines.append("")

    # Key Features (Differentiators)
    if differentiators:
        lines.append("## Key Features")
        lines.append("")
        for d in differentiators:
            name = d.get('name', '')
            desc = d.get('description', '')
            lines.append(f"- **{name}**: {desc}")
        lines.append("")

    # Evolution / Strategic Context
    if evolution:
        lines.append("## Strategic Context")
        lines.append("")
        stages = evolution.get('stages', [])
        if stages:
            lines.append("| Era | Term | Scope |")
            lines.append("|-----|------|-------|")
            for s in stages:
                era = s.get('era', '')
                term = s.get('term', '')
                scope = s.get('scope', '')
                lines.append(f"| {era} | **{term}** | {scope} |")
            lines.append("")

        insight = evolution.get('key_insight', '')
        if insight:
            lines.append(f"> {insight.strip()}")
            lines.append("")

    # Quick Start (placeholder)
    lines.append("## Quick Start")
    lines.append("")
    lines.append("1. Choose a template from [aget-framework](https://github.com/aget-framework)")
    lines.append("2. Copy template to your project")
    lines.append("3. Configure `AGENTS.md` or `CLAUDE.md` for your CLI agent")
    lines.append("4. Start with `wake up` protocol")
    lines.append("")

    # Templates
    lines.append("## Templates")
    lines.append("")
    lines.append("| Template | Purpose |")
    lines.append("|----------|---------|")
    lines.append("| [template-worker-aget](https://github.com/aget-framework/template-worker-aget) | Foundation template |")
    lines.append("| [template-advisor-aget](https://github.com/aget-framework/template-advisor-aget) | Advisory with personas |")
    lines.append("| [template-supervisor-aget](https://github.com/aget-framework/template-supervisor-aget) | Fleet coordination |")
    lines.append("| [template-consultant-aget](https://github.com/aget-framework/template-consultant-aget) | Consulting engagements |")
    lines.append("| [template-developer-aget](https://github.com/aget-framework/template-developer-aget) | Development workflows |")
    lines.append("| [template-spec-engineer-aget](https://github.com/aget-framework/template-spec-engineer-aget) | Specification authoring |")
    lines.append("")

    # Session Protocols
    lines.append("## Session Protocols")
    lines.append("")
    lines.append("| Command | Protocol | Purpose |")
    lines.append("|---------|----------|---------|")
    lines.append("| `wake up` | Wake_Protocol | Initialize session, load context |")
    lines.append("| `study up [topic]` | Study_Up_Protocol | Deep dive on specific topic |")
    lines.append("| `step back` | Step_Back_Protocol | Review KB before proposing |")
    lines.append("| `sanity check` | Sanity_Check_Protocol | Verify agent health |")
    lines.append("| `wind down` | Wind_Down_Protocol | End session, create handoff |")
    lines.append("")

    # Contributing
    lines.append("## Contributing")
    lines.append("")
    lines.append("Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.")
    lines.append("")

    # License
    lines.append("## License")
    lines.append("")
    lines.append("Apache License 2.0 - See [LICENSE](LICENSE)")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated from specifications on {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("*See: [AGET_IDENTITY_SPEC.yaml](specs/AGET_IDENTITY_SPEC.yaml), [AGET_POSITIONING_SPEC.yaml](specs/AGET_POSITIONING_SPEC.yaml)*")
    lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate README.md from AGET specifications'
    )
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--verify', action='store_true', help='Verify specs exist')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated')
    parser.add_argument('--specs-dir', type=str, default='specs', help='Specs directory')

    args = parser.parse_args()

    # Find specs directory
    script_dir = Path(__file__).parent
    aget_dir = script_dir.parent
    specs_dir = aget_dir / args.specs_dir

    identity_path = specs_dir / 'AGET_IDENTITY_SPEC.yaml'
    positioning_path = specs_dir / 'AGET_POSITIONING_SPEC.yaml'

    # Verify mode
    if args.verify:
        print("=== SPEC VERIFICATION ===")
        print(f"Identity spec: {identity_path}")
        print(f"  Exists: {identity_path.exists()}")
        print(f"Positioning spec: {positioning_path}")
        print(f"  Exists: {positioning_path.exists()}")

        if identity_path.exists() and positioning_path.exists():
            print("\nVERIFY: generate_readme.py ready")
            sys.exit(0)
        else:
            print("\nVERIFY: FAILED - specs missing")
            sys.exit(1)

    # Load specs
    try:
        identity_spec = load_spec(identity_path)
        positioning_spec = load_spec(positioning_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate README
    readme_content = generate_readme(identity_spec, positioning_spec)

    # Dry run
    if args.dry_run:
        print("=== DRY RUN - Would generate: ===")
        print(readme_content)
        print("=== END DRY RUN ===")
        sys.exit(0)

    # Output
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = aget_dir / output_path

        with open(output_path, 'w') as f:
            f.write(readme_content)
        print(f"Generated: {output_path}")
    else:
        print(readme_content)


if __name__ == '__main__':
    main()
