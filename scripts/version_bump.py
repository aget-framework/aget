#!/usr/bin/env python3
"""
Version Bump Coordinator

Coordinates version bumps across all templates in aget-framework.
Updates version.json (primary) and README.md version strings (derived).

Per R-REL-VER-001 and L608 (Content Claim Drift, 7th dimension):
version-bearing files must be updated atomically.

Usage: python3 version_bump.py --to VERSION [--dry-run]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime


def get_framework_root():
    """Get the aget-framework root directory."""
    current = Path(__file__).resolve()
    return current.parent.parent.parent.parent.parent


def bump_version(template_path, new_version, dry_run=False):
    """Bump version in a single template."""
    version_file = template_path / '.aget' / 'version.json'

    if not version_file.exists():
        return {'success': False, 'error': 'version.json not found'}

    try:
        with open(version_file) as f:
            data = json.load(f)

        old_version = data.get('aget_version', 'unknown')
        data['aget_version'] = new_version
        data['updated'] = datetime.now().strftime('%Y-%m-%d')

        # Add to migration history if exists
        if 'migration_history' in data:
            entry = f"v{old_version} -> v{new_version}: {datetime.now().strftime('%Y-%m-%d')}"
            data['migration_history'].append(entry)

        if not dry_run:
            with open(version_file, 'w') as f:
                json.dump(data, f, indent=2)

        return {
            'success': True,
            'old_version': old_version,
            'new_version': new_version,
            'dry_run': dry_run
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def bump_readme_version(template_path, old_version, new_version, dry_run=False):
    """Bump version strings in README.md (L608 7th dimension fix).

    Updates two patterns per Option C (Hybrid):
    - Line 5 badge: **Version**: vX.Y.Z
    - Framework spec link: [AGET vX.Y.Z](...)

    Only applies to template repos (not aget/ core which has different format).
    """
    readme_path = template_path / 'README.md'
    if not readme_path.exists():
        return {'readme_updated': False, 'reason': 'no README.md'}

    content = readme_path.read_text(encoding='utf-8')
    original = content

    # Pattern 1: Badge line — **Version**: vX.Y.Z
    content = re.sub(
        r'(\*\*Version\*\*: v)' + re.escape(old_version),
        r'\g<1>' + new_version,
        content
    )

    # Pattern 2: Framework spec link — [AGET vX.Y.Z]
    content = re.sub(
        r'(\[AGET v)' + re.escape(old_version) + r'(\])',
        r'\g<1>' + new_version + r'\2',
        content
    )

    if content == original:
        return {'readme_updated': False, 'reason': 'no matching patterns'}

    if not dry_run:
        readme_path.write_text(content, encoding='utf-8')

    return {'readme_updated': True}


def run_version_bump(new_version, dry_run=False, templates=None):
    """Bump version across all templates."""
    root = get_framework_root()

    all_templates = [
        'aget',
        'template-advisor-aget',
        'template-analyst-aget',
        'template-architect-aget',
        'template-consultant-aget',
        'template-developer-aget',
        'template-executive-aget',
        'template-operator-aget',
        'template-researcher-aget',
        'template-reviewer-aget',
        'template-spec-engineer-aget',
        'template-supervisor-aget',
        'template-worker-aget',
    ]

    if templates:
        target_templates = [t for t in all_templates if t in templates]
    else:
        target_templates = all_templates

    results = {}

    for template in target_templates:
        template_path = root / template
        if template_path.exists():
            result = bump_version(template_path, new_version, dry_run)
            # Also bump README.md for template repos (not aget/ core)
            if result['success'] and template.startswith('template-'):
                old_ver = result.get('old_version', '')
                if old_ver:
                    readme_result = bump_readme_version(
                        template_path, old_ver, new_version, dry_run
                    )
                    result.update(readme_result)
            results[template] = result
        else:
            results[template] = {'success': False, 'error': 'Directory not found'}

    return results


def print_report(results, new_version, dry_run):
    """Print the version bump report."""
    print("\n" + "="*60)
    if dry_run:
        print("VERSION BUMP DRY RUN")
    else:
        print("VERSION BUMP RESULTS")
    print("="*60 + "\n")

    print(f"Target Version: {new_version}")
    if dry_run:
        print("Mode: DRY RUN (no changes made)")
    print()

    success_count = 0
    fail_count = 0

    for template, result in results.items():
        if result['success']:
            success_count += 1
            old = result.get('old_version', 'unknown')
            readme = " + README" if result.get('readme_updated') else ""
            print(f"  [OK] {template}: {old} -> {new_version}{readme}")
        else:
            fail_count += 1
            error = result.get('error', 'Unknown error')
            print(f"  [!!] {template}: FAILED ({error})")

    print()
    print(f"Summary: {success_count} succeeded, {fail_count} failed")
    print("="*60)

    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Coordinate version bumps across AGET templates'
    )
    parser.add_argument(
        '--to', '-t',
        required=True,
        help='Target version (e.g., 2.10.0)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--templates',
        nargs='+',
        help='Specific templates to bump (default: all)'
    )

    args = parser.parse_args()

    results = run_version_bump(args.to, args.dry_run, args.templates)
    success = print_report(results, args.to, args.dry_run)

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
