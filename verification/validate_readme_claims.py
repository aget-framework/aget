#!/usr/bin/env python3
"""
validate_readme_claims.py - Validate template README against R-TPL-001 requirements

Implements R-TPL-001 (Template Documentation Requirements) validation:
- R-TPL-001-01: Specification section exists
- R-TPL-001-02: Governed By link present and valid
- R-TPL-001-03: Archetype matches manifest.yaml
- R-TPL-001-04: Contract test count declared
- R-TPL-001-05: Version matches manifest.yaml

Usage:
    python3 validate_readme_claims.py /path/to/template-worker-aget
    python3 validate_readme_claims.py --all

Exit codes:
    0 - All validations passed
    1 - Validation failures found
    2 - Script error (missing files, etc.)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def load_manifest(template_path: Path) -> Optional[Dict]:
    """Load manifest.yaml from template directory."""
    manifest_path = template_path / "manifest.yaml"
    if not manifest_path.exists():
        return None

    if not YAML_AVAILABLE:
        # Fallback: parse simple YAML fields with regex
        content = manifest_path.read_text()
        manifest = {}

        # Extract version
        version_match = re.search(r'version:\s*["\']?(\d+\.\d+\.\d+)["\']?', content)
        if version_match:
            manifest['template'] = {'version': version_match.group(1)}

        # Extract archetype
        archetype_match = re.search(r'archetype:\s*["\']?(\w+)["\']?', content)
        if archetype_match:
            if 'template' not in manifest:
                manifest['template'] = {}
            manifest['template']['archetype'] = archetype_match.group(1)

        return manifest

    with open(manifest_path) as f:
        return yaml.safe_load(f)


def load_readme(template_path: Path) -> Optional[str]:
    """Load README.md from template directory."""
    readme_path = template_path / "README.md"
    if not readme_path.exists():
        return None
    return readme_path.read_text()


def check_specification_section(readme: str) -> Tuple[bool, str]:
    """R-TPL-001-01: Check Specification section exists."""
    if "## Specification" in readme:
        return True, "Specification section exists"
    return False, "Missing '## Specification' section"


def check_governed_by_link(readme: str) -> Tuple[bool, str]:
    """R-TPL-001-02: Check Governed By link present."""
    # Look for Governed By in table format
    if re.search(r'\*\*Governed By\*\*.*\[.*\]\(.*\)', readme, re.IGNORECASE):
        return True, "Governed By link present"
    # Also check simpler format
    if re.search(r'Governed [Bb]y:?\s*\[.*\]\(.*\)', readme):
        return True, "Governed By link present"
    return False, "Missing 'Governed By' link"


def check_archetype_match(readme: str, manifest: Dict) -> Tuple[bool, str]:
    """R-TPL-001-03: Check archetype matches manifest."""
    if not manifest or 'template' not in manifest:
        return False, "Cannot check archetype: manifest missing"

    manifest_archetype = manifest.get('template', {}).get('archetype', '')
    if not manifest_archetype:
        return False, "Archetype not found in manifest"

    # Look for archetype in Specification section
    archetype_pattern = rf'\*\*Archetype\*\*.*{manifest_archetype}'
    if re.search(archetype_pattern, readme, re.IGNORECASE):
        return True, f"Archetype matches: {manifest_archetype}"

    # Check if archetype appears anywhere in Specification section
    spec_section_match = re.search(r'## Specification\n(.*?)(?=\n## |\Z)', readme, re.DOTALL)
    if spec_section_match:
        spec_section = spec_section_match.group(1)
        if manifest_archetype.lower() in spec_section.lower():
            return True, f"Archetype matches: {manifest_archetype}"

    return False, f"Archetype mismatch or missing: expected '{manifest_archetype}'"


def check_contract_tests(readme: str) -> Tuple[bool, str]:
    """R-TPL-001-04: Check contract test count declared."""
    # Look for contract test count pattern
    if re.search(r'Contract Tests.*\d+\s+(required|tests)', readme, re.IGNORECASE):
        return True, "Contract test count declared"
    if re.search(r'\d+\s+required.*\d+\s+recommended', readme, re.IGNORECASE):
        return True, "Contract test count declared"
    return False, "Missing contract test count declaration"


def check_version_match(readme: str, manifest: Dict) -> Tuple[bool, str]:
    """R-TPL-001-05: Check version matches manifest."""
    if not manifest or 'template' not in manifest:
        return False, "Cannot check version: manifest missing"

    manifest_version = manifest.get('template', {}).get('version', '')
    if not manifest_version:
        return False, "Version not found in manifest"

    # Look for version in README
    # Patterns: "Version**: 3.0.0" or "**Current Version**: v3.0.0" or "v3.0.0"
    readme_version_match = re.search(
        rf'(?:Version["\']?\s*[:|\*]*\s*[vV]?)?({re.escape(manifest_version)})',
        readme
    )
    if readme_version_match:
        return True, f"Version matches: {manifest_version}"

    # Check for any version string in README
    any_version = re.search(r'v?(\d+\.\d+\.\d+)', readme)
    if any_version:
        readme_ver = any_version.group(1)
        if readme_ver == manifest_version:
            return True, f"Version matches: {manifest_version}"
        return False, f"Version mismatch: README has '{readme_ver}', manifest has '{manifest_version}'"

    return False, f"Version not found in README: expected '{manifest_version}'"


def validate_template(template_path: Path) -> Dict[str, any]:
    """Validate a single template against R-TPL-001 requirements."""
    results = {
        'template': template_path.name,
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'checks': []
    }

    # Load files
    readme = load_readme(template_path)
    if readme is None:
        results['error'] = "README.md not found"
        return results

    manifest = load_manifest(template_path)
    if manifest is None:
        results['warnings'] += 1
        results['checks'].append(('warning', 'manifest.yaml not found'))

    # Run checks
    checks = [
        ('R-TPL-001-01', check_specification_section(readme)),
        ('R-TPL-001-02', check_governed_by_link(readme)),
        ('R-TPL-001-03', check_archetype_match(readme, manifest) if manifest else (False, "Cannot check: no manifest")),
        ('R-TPL-001-04', check_contract_tests(readme)),
        ('R-TPL-001-05', check_version_match(readme, manifest) if manifest else (False, "Cannot check: no manifest")),
    ]

    for req_id, (passed, message) in checks:
        if passed:
            results['passed'] += 1
            results['checks'].append(('pass', f"{req_id}: {message}"))
        else:
            results['failed'] += 1
            results['checks'].append(('fail', f"{req_id}: {message}"))

    return results


def print_results(results: Dict[str, any], verbose: bool = False) -> None:
    """Print validation results."""
    template = results['template']

    if 'error' in results:
        print(f"{RED}ERROR{RESET} {template}: {results['error']}")
        return

    passed = results['passed']
    failed = results['failed']
    total = passed + failed

    status = f"{GREEN}PASSED{RESET}" if failed == 0 else f"{RED}FAILED{RESET}"
    print(f"\n{status}: {template} ({passed}/{total} checks passed)")

    if verbose or failed > 0:
        for check_type, message in results['checks']:
            if check_type == 'pass':
                print(f"  {GREEN}✓{RESET} {message}")
            elif check_type == 'fail':
                print(f"  {RED}✗{RESET} {message}")
            elif check_type == 'warning':
                print(f"  {YELLOW}⚠{RESET} {message}")


def find_all_templates(base_path: Path) -> List[Path]:
    """Find all template-* directories."""
    templates = []
    for item in base_path.iterdir():
        if item.is_dir() and item.name.startswith('template-') and item.name.endswith('-aget'):
            templates.append(item)
    return sorted(templates)


def main():
    parser = argparse.ArgumentParser(
        description='Validate template README against R-TPL-001 requirements'
    )
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to template directory'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all templates in aget-framework directory'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show all check results, not just failures'
    )

    args = parser.parse_args()

    if args.all:
        # Find aget-framework directory
        script_path = Path(__file__).resolve()
        aget_framework = script_path.parent.parent.parent

        templates = find_all_templates(aget_framework)
        if not templates:
            print(f"{RED}ERROR{RESET}: No templates found in {aget_framework}")
            sys.exit(2)

        print(f"Validating {len(templates)} templates against R-TPL-001...")

        total_passed = 0
        total_failed = 0

        for template_path in templates:
            results = validate_template(template_path)
            print_results(results, args.verbose)

            if 'error' in results:
                total_failed += 1
            elif results['failed'] == 0:
                total_passed += 1
            else:
                total_failed += 1

        print(f"\n{'='*60}")
        print(f"Summary: {total_passed}/{len(templates)} templates passed")

        sys.exit(0 if total_failed == 0 else 1)

    elif args.path:
        template_path = Path(args.path).resolve()
        if not template_path.exists():
            print(f"{RED}ERROR{RESET}: Path does not exist: {template_path}")
            sys.exit(2)

        results = validate_template(template_path)
        print_results(results, args.verbose)

        sys.exit(0 if results.get('failed', 0) == 0 else 1)

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == '__main__':
    main()
