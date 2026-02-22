#!/usr/bin/env python3
"""
L-Doc Migration Tool - v1 to v2 Format

Migrates L-docs from simple markdown (v1) to structured format with
YAML frontmatter (v2) for cross-agent discovery.

Implements: L419 (L-Doc Format v2), SPEC-LDOC-001
Patterns: L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 migrate_ldoc_to_v2.py .aget/evolution/           # Migrate all
    python3 migrate_ldoc_to_v2.py .aget/evolution/L419.md    # Migrate one
    python3 migrate_ldoc_to_v2.py --dry-run .aget/evolution/ # Preview only
    python3 migrate_ldoc_to_v2.py --validate .aget/evolution/# Validate v2 format

Exit codes:
    0: Success
    1: Some files failed migration
    2: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | L-doc file | Verify exists before reading |
    | 2 | Frontmatter | Check if already v2 before migrating |
    | 3 | evolution/ | Verify directory exists |
    | 4 | Backup | Create backup before modifying |

Author: aget-framework
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# L039: Diagnostic Efficiency - Timing
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr (L039: diagnostics to stderr)."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# L-Doc Parsing
# =============================================================================

# Category keywords for inference
CATEGORY_KEYWORDS = {
    'pattern': ['pattern', 'how to', 'approach', 'method'],
    'anti-pattern': ['anti-pattern', 'don\'t', 'avoid', 'mistake'],
    'protocol': ['protocol', 'procedure', 'process', 'workflow'],
    'governance': ['governance', 'authority', 'decision', 'approval'],
    'tooling': ['script', 'tool', 'automation', 'command'],
    'migration': ['migration', 'upgrade', 'convert', 'transition'],
    'architecture': ['architecture', 'structure', 'design', 'layout'],
    'process': ['process', 'flow', 'sequence', 'steps'],
    'observation': ['observed', 'noticed', 'found', 'discovered'],
    'decision': ['decided', 'chose', 'selected', 'determined'],
}


def parse_ldoc_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse L-doc filename to extract ID and title.

    Returns (id, title) or (None, None) if invalid.
    """
    match = re.match(r'^(L\d+)[_\s](.+)\.md$', filename)
    if match:
        return match.group(1), match.group(2).replace('_', ' ').title()
    return None, None


def has_yaml_frontmatter(content: str) -> bool:
    """Check if content already has YAML frontmatter."""
    return content.strip().startswith('---')


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Extract YAML frontmatter from content.

    Returns (frontmatter_dict, remaining_content) or (None, content) if none.
    """
    if not has_yaml_frontmatter(content):
        return None, content

    lines = content.split('\n')
    if lines[0].strip() != '---':
        return None, content

    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, content

    # Parse YAML (simple key: value parsing)
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            key, _, value = line.partition(':')
            frontmatter[key.strip()] = value.strip()

    remaining = '\n'.join(lines[end_idx + 1:]).strip()
    return frontmatter, remaining


def infer_category(content: str) -> str:
    """Infer category from content keywords."""
    content_lower = content.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                return category

    return 'observation'  # Default


def extract_summary(content: str, max_length: int = 200) -> str:
    """Extract first meaningful paragraph as summary."""
    # Remove markdown headers and empty lines at start
    lines = []
    started = False

    for line in content.split('\n'):
        stripped = line.strip()
        if not started:
            if stripped and not stripped.startswith('#'):
                started = True
                lines.append(stripped)
        else:
            if not stripped:
                break
            lines.append(stripped)

    summary = ' '.join(lines)
    if len(summary) > max_length:
        summary = summary[:max_length - 3] + '...'

    return summary or 'No summary available.'


def extract_related_ldocs(content: str) -> List[str]:
    """Extract references to other L-docs."""
    return re.findall(r'\bL\d{2,4}\b', content)


def generate_frontmatter(ldoc_id: str, title: str, content: str,
                         created_date: Optional[str] = None) -> str:
    """Generate YAML frontmatter for L-doc."""
    category = infer_category(content)
    summary = extract_summary(content)
    related = extract_related_ldocs(content)

    # Remove self-reference
    related = [r for r in related if r != ldoc_id]
    related = list(set(related))[:5]  # Dedupe and limit

    today = datetime.now().strftime('%Y-%m-%d')
    created = created_date or today

    lines = [
        '---',
        f'id: {ldoc_id}',
        f'title: "{title}"',
        'format_version: "2.0"',
        f'created: {created}',
        f'updated: {today}',
        f'summary: "{summary}"',
        f'category: {category}',
        'applicability:',
        '  scope: agent',
        '  archetypes: [all]',
    ]

    if related:
        lines.append('related:')
        lines.append(f'  ldocs: [{", ".join(related)}]')

    lines.append('enforcement:')
    lines.append('  status: observation')
    lines.append('  mechanism: none')
    lines.append('---')

    return '\n'.join(lines)


# =============================================================================
# Migration Logic
# =============================================================================

def migrate_ldoc(file_path: Path, dry_run: bool = False,
                 verbose: bool = False) -> Tuple[bool, str]:
    """
    Migrate a single L-doc to v2 format.

    Returns (success, message).
    """
    # L021 Check 1: Verify file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    # Parse filename
    ldoc_id, title = parse_ldoc_filename(file_path.name)
    if not ldoc_id:
        return False, f"Invalid L-doc filename: {file_path.name}"

    # Read content
    try:
        content = file_path.read_text()
    except IOError as e:
        return False, f"Read error: {e}"

    # L021 Check 2: Check if already v2
    existing_fm, body = extract_frontmatter(content)
    if existing_fm and existing_fm.get('format_version') == '2.0':
        return True, f"Already v2: {ldoc_id}"

    # Get file creation date
    try:
        stat = file_path.stat()
        created_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
    except OSError:
        created_date = None

    # Generate frontmatter
    if existing_fm:
        # Upgrade existing frontmatter
        body_content = body
    else:
        body_content = content

    new_frontmatter = generate_frontmatter(ldoc_id, title, body_content, created_date)
    new_content = f"{new_frontmatter}\n\n{body_content}"

    if dry_run:
        if verbose:
            print(f"\n--- {file_path.name} ---")
            print(new_frontmatter)
            print("---")
        return True, f"Would migrate: {ldoc_id}"

    # L021 Check 4: Create backup
    backup_path = file_path.with_suffix('.md.bak')
    try:
        shutil.copy2(file_path, backup_path)
    except IOError as e:
        return False, f"Backup failed: {e}"

    # Write migrated content
    try:
        file_path.write_text(new_content)
        # Remove backup on success
        backup_path.unlink()
        return True, f"Migrated: {ldoc_id}"
    except IOError as e:
        # Restore backup
        shutil.copy2(backup_path, file_path)
        backup_path.unlink()
        return False, f"Write failed: {e}"


def validate_ldoc(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate L-doc v2 format.

    Returns (valid, list_of_issues).
    """
    issues = []

    if not file_path.exists():
        return False, ["File not found"]

    # Check filename
    ldoc_id, _ = parse_ldoc_filename(file_path.name)
    if not ldoc_id:
        issues.append("Invalid filename format")

    # Read and check frontmatter
    try:
        content = file_path.read_text()
    except IOError as e:
        return False, [f"Read error: {e}"]

    if not has_yaml_frontmatter(content):
        issues.append("Missing YAML frontmatter")
        return False, issues

    frontmatter, _ = extract_frontmatter(content)
    if not frontmatter:
        issues.append("Invalid YAML frontmatter")
        return False, issues

    # Required fields
    required = ['id', 'title', 'format_version', 'created', 'summary']
    for field in required:
        if field not in frontmatter:
            issues.append(f"Missing required field: {field}")

    # Version check
    if frontmatter.get('format_version') != '2.0':
        issues.append(f"Not v2 format (version: {frontmatter.get('format_version', 'none')})")

    return len(issues) == 0, issues


def update_index(evolution_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Generate/update index.json from L-docs.

    Returns index data.
    """
    index = {
        'format_version': '2.0',
        'last_updated': datetime.now().isoformat(),
        'count': 0,
        'categories': {},
        'ldocs': []
    }

    ldoc_files = sorted(evolution_dir.glob('L*.md'))

    for ldoc_file in ldoc_files:
        ldoc_id, title = parse_ldoc_filename(ldoc_file.name)
        if not ldoc_id:
            continue

        try:
            content = ldoc_file.read_text()
            frontmatter, _ = extract_frontmatter(content)
        except IOError:
            continue

        if frontmatter:
            category = frontmatter.get('category', 'observation')
            scope = 'agent'
            if 'applicability' in frontmatter:
                # Simple parsing
                pass
            enforcement = 'observation'
            created = frontmatter.get('created', '')
        else:
            category = infer_category(content)
            scope = 'agent'
            enforcement = 'observation'
            created = ''

        index['ldocs'].append({
            'id': ldoc_id,
            'title': title,
            'category': category,
            'scope': scope,
            'created': created,
            'enforcement': enforcement
        })

        index['categories'][category] = index['categories'].get(category, 0) + 1
        index['count'] += 1

    return index


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Migrate L-docs from v1 to v2 format (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. L-doc file - Verify exists before reading
  2. Frontmatter - Check if already v2 before migrating
  3. evolution/ - Verify directory exists
  4. Backup - Create backup before modifying

Exit codes:
  0 - All migrations successful
  1 - Some migrations failed
  2 - Configuration error
        """
    )
    parser.add_argument(
        'path',
        type=Path,
        help='L-doc file or evolution/ directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate v2 format only (no migration)'
    )
    parser.add_argument(
        '--update-index',
        action='store_true',
        help='Update index.json after migration'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='migrate_ldoc_to_v2.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if args.verbose:
        log_diagnostic("Starting L-doc migration")

    path = args.path.resolve()

    # L021 Check 3: Verify path exists
    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 2

    # Determine files to process
    if path.is_file():
        files = [path]
        evolution_dir = path.parent
    else:
        files = sorted(path.glob('L*.md'))
        evolution_dir = path
        if not files:
            print(f"No L-docs found in: {path}", file=sys.stderr)
            return 2

    if args.verbose:
        log_diagnostic(f"Processing {len(files)} L-doc(s)")

    # Process files
    results = {'success': 0, 'failed': 0, 'skipped': 0}

    for ldoc_file in files:
        if args.validate:
            valid, issues = validate_ldoc(ldoc_file)
            if valid:
                print(f"[+] {ldoc_file.name}: Valid v2")
                results['success'] += 1
            else:
                print(f"[x] {ldoc_file.name}: {', '.join(issues)}")
                results['failed'] += 1
        else:
            success, message = migrate_ldoc(ldoc_file, args.dry_run, args.verbose)
            if success:
                if 'Already' in message:
                    print(f"[-] {message}")
                    results['skipped'] += 1
                else:
                    print(f"[+] {message}")
                    results['success'] += 1
            else:
                print(f"[x] {message}")
                results['failed'] += 1

    # Update index if requested
    if args.update_index and not args.dry_run:
        if args.verbose:
            log_diagnostic("Updating index.json")

        index = update_index(evolution_dir, args.verbose)
        index_path = evolution_dir / 'index.json'

        try:
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)
            print(f"\n[+] Updated index.json: {index['count']} L-docs")
        except IOError as e:
            print(f"\n[x] Failed to update index.json: {e}", file=sys.stderr)

    # Summary
    print(f"\nSummary: {results['success']} success, {results['failed']} failed, {results['skipped']} skipped")

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    return 1 if results['failed'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
