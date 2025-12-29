#!/usr/bin/env python3
"""
Validate AGET Specification Format v1.2.

Implements: CAP-SPEC-001 (Spec_Format_Compliance), CAP-VAL-002 (validator structure)
Traces to: AGET_SPEC_FORMAT_v1.2.md, AGET_VALIDATION_SPEC.md

Validates specification files against AGET_SPEC_FORMAT v1.2 requirements:
- EARS temporal patterns
- Required v1.2 sections
- CAP-{DOMAIN}-{NNN} capability IDs
- Title_Case vocabulary terms

Usage:
    python3 validate_spec_format.py <spec_file>
    python3 validate_spec_format.py specs/*.md
    python3 validate_spec_format.py --all

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any


# EARS pattern regexes
EARS_PATTERNS = {
    'ubiquitous': r'The SYSTEM shall\b',
    'event_driven': r'\bWHEN\b.*,?\s*the SYSTEM shall',
    'state_driven': r'\bWHILE\b.*,?\s*the SYSTEM shall',
    'optional': r'\bWHERE\b.*,?\s*the SYSTEM (shall|may)',
    'conditional': r'\bIF\b.*\bTHEN\b.*the SYSTEM shall',
}

# Required v1.2 sections
REQUIRED_SECTIONS_V12 = [
    'Vocabulary',
    'Authority Model',
    'Inviolables',
    'Structural Requirements',
]

# Required header fields
REQUIRED_HEADER_FIELDS = [
    'Version',
    'Status',
    'Category',
    'Format Version',
]

# CAP ID pattern
CAP_ID_PATTERN = r'CAP-[A-Z]+-\d{3}'


def read_file(path: Path) -> str:
    """Read file contents."""
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        sys.exit(2)


def count_ears_patterns(content: str) -> Dict[str, int]:
    """Count EARS patterns in content."""
    counts = {}
    for pattern_name, regex in EARS_PATTERNS.items():
        matches = re.findall(regex, content, re.IGNORECASE)
        counts[pattern_name] = len(matches)
    return counts


def check_required_sections(content: str) -> List[str]:
    """Check for required v1.2 sections. Returns missing sections."""
    missing = []
    for section in REQUIRED_SECTIONS_V12:
        # Look for markdown heading with section name
        pattern = rf'^##+ .*{re.escape(section)}'
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing.append(section)
    return missing


def check_format_version(content: str) -> Tuple[bool, str]:
    """Check for Format Version: 1.2 in header."""
    match = re.search(r'\*\*Format Version\*\*:\s*(\S+)', content)
    if match:
        version = match.group(1)
        return version == '1.2', version
    return False, 'not found'


def count_cap_ids(content: str) -> int:
    """Count CAP-{DOMAIN}-{NNN} IDs."""
    matches = re.findall(CAP_ID_PATTERN, content)
    return len(matches)


def check_vocabulary_section(content: str) -> bool:
    """Check if Vocabulary section has YAML code block with skos:definition."""
    vocab_match = re.search(r'## Vocabulary.*?```yaml(.*?)```', content, re.DOTALL)
    if vocab_match:
        yaml_content = vocab_match.group(1)
        return 'skos:definition' in yaml_content
    return False


def validate_spec(path: Path) -> Tuple[bool, Dict[str, Any]]:
    """Validate a single specification file."""
    content = read_file(path)
    results = {
        'file': str(path),
        'ears_patterns': {},
        'total_ears': 0,
        'missing_sections': [],
        'format_version_ok': False,
        'format_version': '',
        'cap_ids': 0,
        'has_skos_vocabulary': False,
        'errors': [],
        'warnings': [],
    }

    # Count EARS patterns
    results['ears_patterns'] = count_ears_patterns(content)
    results['total_ears'] = sum(results['ears_patterns'].values())

    # Check required sections
    results['missing_sections'] = check_required_sections(content)

    # Check format version
    results['format_version_ok'], results['format_version'] = check_format_version(content)

    # Count CAP IDs
    results['cap_ids'] = count_cap_ids(content)

    # Check vocabulary section
    results['has_skos_vocabulary'] = check_vocabulary_section(content)

    # Determine errors
    if results['total_ears'] < 5:
        results['errors'].append(f"Too few EARS patterns: {results['total_ears']} (minimum 5)")

    if results['missing_sections']:
        results['errors'].append(f"Missing sections: {', '.join(results['missing_sections'])}")

    if not results['format_version_ok']:
        results['errors'].append(f"Format Version should be 1.2, found: {results['format_version']}")

    # Warnings
    if results['cap_ids'] == 0:
        results['warnings'].append("No CAP-{DOMAIN}-{NNN} IDs found")

    if not results['has_skos_vocabulary']:
        results['warnings'].append("No SKOS vocabulary (skos:definition) in Vocabulary section")

    passed = len(results['errors']) == 0
    return passed, results


def print_results(results: Dict[str, Any], verbose: bool = False) -> None:
    """Print validation results."""
    file_name = Path(results['file']).name
    passed = len(results['errors']) == 0

    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {file_name}")

    if verbose or not passed:
        print(f"  EARS patterns: {results['total_ears']}")
        if verbose:
            for pattern, count in results['ears_patterns'].items():
                if count > 0:
                    print(f"    {pattern}: {count}")
        print(f"  CAP IDs: {results['cap_ids']}")
        print(f"  Format Version: {results['format_version']}")

        for error in results['errors']:
            print(f"  ❌ ERROR: {error}")

        for warning in results['warnings']:
            print(f"  ⚠️  WARN: {warning}")


def find_spec_files(base_path: Path) -> List[Path]:
    """Find all AGET spec files."""
    specs_dir = base_path / 'specs'
    if not specs_dir.exists():
        print(f"❌ Specs directory not found: {specs_dir}")
        sys.exit(2)

    # Find AGET_*_SPEC*.md files
    spec_files = list(specs_dir.glob('AGET_*_SPEC*.md'))
    # Exclude format specs and versioned duplicates
    spec_files = [f for f in spec_files if 'FORMAT' not in f.name]
    return sorted(spec_files)


def main():
    parser = argparse.ArgumentParser(
        description='Validate AGET specification format v1.2'
    )
    parser.add_argument('paths', nargs='*', help='Paths to validate')
    parser.add_argument('--all', action='store_true', help='Validate all specs in aget/specs/')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (errors only)')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    if not args.paths and not args.all:
        parser.print_help()
        return 2

    # Determine files to validate
    if args.all:
        # Find aget repo root
        current = Path.cwd()
        while current != current.parent:
            if (current / 'specs').exists() and (current / 'validation').exists():
                break
            current = current.parent
        files = find_spec_files(current)
    else:
        files = [Path(p) for p in args.paths]

    if not files:
        print("❌ No specification files found")
        return 2

    # Validate each file
    all_passed = True
    total_ears = 0
    total_cap_ids = 0

    for file_path in files:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            all_passed = False
            continue

        passed, results = validate_spec(file_path)
        all_passed = all_passed and passed
        total_ears += results['total_ears']
        total_cap_ids += results['cap_ids']

        if not args.quiet or not passed:
            print_results(results, args.verbose)

    # Summary
    if len(files) > 1:
        print()
        status = "✅" if all_passed else "❌"
        passed_count = sum(1 for f in files if validate_spec(f)[0])
        print(f"{status} {passed_count}/{len(files)} specs valid")
        print(f"   Total EARS patterns: {total_ears}")
        print(f"   Total CAP IDs: {total_cap_ids}")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
