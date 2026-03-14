#!/usr/bin/env python3
"""
Version Bump Coordinator

Coordinates version bumps across all templates in aget-framework.
Updates 5 version-bearing artifact types atomically:
  1. version.json (primary, all repos)
  2. README.md (templates only)
  3. AGENTS.md @aget-version (templates only)
  4. codemeta.json (core only)
  5. CITATION.cff (core only)

Per R-REL-VER-001, L608 (Content Claim Drift), and D64 (version-bearing enforcement):
version-bearing files must be updated atomically.

Usage:
    python3 version_bump.py --to VERSION [--dry-run]
    python3 version_bump.py --check VERSION              # Validate only (exit 1 on mismatch)
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
    """Bump version in a single template's version.json."""
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


def bump_agents_md_version(template_path, old_version, new_version, dry_run=False):
    """Bump @aget-version in AGENTS.md (D64, R-VER-ENF-001).

    Pattern: @aget-version: X.Y.Z (line 3 in AGENTS.md)
    Applies to template repos only (aget/ core has no AGENTS.md).
    """
    agents_path = template_path / 'AGENTS.md'
    if not agents_path.exists():
        return {'agents_updated': False, 'reason': 'no AGENTS.md'}

    content = agents_path.read_text(encoding='utf-8')
    original = content

    content = re.sub(
        r'(@aget-version: )' + re.escape(old_version),
        r'\g<1>' + new_version,
        content
    )

    if content == original:
        return {'agents_updated': False, 'reason': 'no matching pattern'}

    if not dry_run:
        agents_path.write_text(content, encoding='utf-8')

    return {'agents_updated': True}


def bump_codemeta_version(core_path, new_version, dry_run=False):
    """Bump version in codemeta.json (D64, R-VER-ENF-002).

    Pattern: "version": "X.Y.Z" in codemeta.json
    Applies to aget/ core repo only.
    """
    codemeta_path = core_path / 'codemeta.json'
    if not codemeta_path.exists():
        return {'codemeta_updated': False, 'reason': 'no codemeta.json'}

    try:
        with open(codemeta_path) as f:
            data = json.load(f)

        old_version = data.get('version', 'unknown')
        data['version'] = new_version

        if not dry_run:
            with open(codemeta_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')

        return {'codemeta_updated': True, 'old': old_version}

    except Exception as e:
        return {'codemeta_updated': False, 'reason': str(e)}


def bump_citation_version(core_path, new_version, dry_run=False):
    """Bump version in CITATION.cff (D64, R-VER-ENF-003).

    Pattern: version: "X.Y.Z" in CITATION.cff (YAML)
    Applies to aget/ core repo only.
    """
    citation_path = core_path / 'CITATION.cff'
    if not citation_path.exists():
        return {'citation_updated': False, 'reason': 'no CITATION.cff'}

    content = citation_path.read_text(encoding='utf-8')
    original = content

    content = re.sub(
        r'(version: ")[\d.]+(")',
        r'\g<1>' + new_version + r'\2',
        content
    )

    if content == original:
        return {'citation_updated': False, 'reason': 'no matching pattern'}

    if not dry_run:
        citation_path.write_text(content, encoding='utf-8')

    return {'citation_updated': True}


def check_version(expected_version, templates=None):
    """Validate all version-bearing files match expected version (D64, R-VER-ENF-004).

    Returns dict with check results. Exit code 1 on any mismatch.
    """
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

    mismatches = []
    checks = 0

    for template in target_templates:
        template_path = root / template
        if not template_path.exists():
            mismatches.append(f"{template}: directory not found")
            continue

        # Check 1: version.json
        version_file = template_path / '.aget' / 'version.json'
        if version_file.exists():
            checks += 1
            with open(version_file) as f:
                data = json.load(f)
            actual = data.get('aget_version', 'unknown')
            if actual != expected_version:
                mismatches.append(f"{template}/version.json: {actual} (expected {expected_version})")

        # Check 2: AGENTS.md (templates only)
        if template.startswith('template-'):
            agents_path = template_path / 'AGENTS.md'
            if agents_path.exists():
                checks += 1
                content = agents_path.read_text(encoding='utf-8')
                match = re.search(r'@aget-version: ([\d.]+)', content)
                if match:
                    actual = match.group(1)
                    if actual != expected_version:
                        mismatches.append(f"{template}/AGENTS.md: {actual} (expected {expected_version})")
                else:
                    mismatches.append(f"{template}/AGENTS.md: no @aget-version found")

        # Check 3: codemeta.json (core only)
        if template == 'aget':
            codemeta_path = template_path / 'codemeta.json'
            if codemeta_path.exists():
                checks += 1
                with open(codemeta_path) as f:
                    data = json.load(f)
                actual = data.get('version', 'unknown')
                if actual != expected_version:
                    mismatches.append(f"aget/codemeta.json: {actual} (expected {expected_version})")

            # Check 4: CITATION.cff (core only)
            citation_path = template_path / 'CITATION.cff'
            if citation_path.exists():
                checks += 1
                content = citation_path.read_text(encoding='utf-8')
                match = re.search(r'version: "([^"]+)"', content)
                if match:
                    actual = match.group(1)
                    if actual != expected_version:
                        mismatches.append(f"aget/CITATION.cff: {actual} (expected {expected_version})")
                else:
                    mismatches.append(f"aget/CITATION.cff: no version found")

    return {
        'expected': expected_version,
        'checks': checks,
        'mismatches': mismatches,
        'all_match': len(mismatches) == 0
    }


def run_version_bump(new_version, dry_run=False, templates=None):
    """Bump version across all templates (5/5 artifact types)."""
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

            if result['success']:
                old_ver = result.get('old_version', '')

                # README.md (templates only)
                if template.startswith('template-') and old_ver:
                    readme_result = bump_readme_version(
                        template_path, old_ver, new_version, dry_run
                    )
                    result.update(readme_result)

                # AGENTS.md (templates only — D64)
                if template.startswith('template-') and old_ver:
                    agents_result = bump_agents_md_version(
                        template_path, old_ver, new_version, dry_run
                    )
                    result.update(agents_result)

                # codemeta.json (core only — D64)
                if template == 'aget':
                    codemeta_result = bump_codemeta_version(
                        template_path, new_version, dry_run
                    )
                    result.update(codemeta_result)

                # CITATION.cff (core only — D64)
                if template == 'aget':
                    citation_result = bump_citation_version(
                        template_path, new_version, dry_run
                    )
                    result.update(citation_result)

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
            extras = []
            if result.get('readme_updated'):
                extras.append('README')
            if result.get('agents_updated'):
                extras.append('AGENTS.md')
            if result.get('codemeta_updated'):
                extras.append('codemeta.json')
            if result.get('citation_updated'):
                extras.append('CITATION.cff')
            suffix = f" + {', '.join(extras)}" if extras else ""
            print(f"  [OK] {template}: {old} -> {new_version}{suffix}")
        else:
            fail_count += 1
            error = result.get('error', 'Unknown error')
            print(f"  [!!] {template}: FAILED ({error})")

    print()
    print(f"Summary: {success_count} succeeded, {fail_count} failed")
    print(f"Artifact types: version.json + README.md + AGENTS.md + codemeta.json + CITATION.cff (5/5)")
    print("="*60)

    return fail_count == 0


def print_check_report(check_result):
    """Print the version check report."""
    print("\n" + "="*60)
    print("VERSION CHECK RESULTS")
    print("="*60 + "\n")

    print(f"Expected Version: {check_result['expected']}")
    print(f"Files Checked: {check_result['checks']}")
    print()

    if check_result['all_match']:
        print("  [OK] All version-bearing files match")
    else:
        print(f"  [!!] {len(check_result['mismatches'])} mismatch(es) found:\n")
        for m in check_result['mismatches']:
            print(f"    - {m}")

    print()
    status = "PASS" if check_result['all_match'] else "FAIL"
    print(f"Result: {status}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Coordinate version bumps across AGET templates (5/5 artifact types)'
    )
    parser.add_argument(
        '--to', '-t',
        help='Target version (e.g., 3.9.0)'
    )
    parser.add_argument(
        '--check', '-c',
        metavar='VERSION',
        help='Check all version-bearing files match VERSION (exit 1 on mismatch)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--templates',
        nargs='+',
        help='Specific templates to bump/check (default: all)'
    )

    args = parser.parse_args()

    # --check mode (D64, R-VER-ENF-004)
    if args.check:
        check_result = check_version(args.check, args.templates)
        print_check_report(check_result)
        sys.exit(0 if check_result['all_match'] else 1)

    # --to mode (bump)
    if not args.to:
        parser.error("Either --to VERSION or --check VERSION is required")

    results = run_version_bump(args.to, args.dry_run, args.templates)
    success = print_report(results, args.to, args.dry_run)

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
