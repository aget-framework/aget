#!/usr/bin/env python3
"""
L-doc to SOP Cascade Protocol

Automate cascading learnings from L-docs to Standard Operating Procedures.
When a pattern becomes established, update relevant SOPs.

Implements: #4 (L-doc to SOP Cascade Protocol)
Patterns: L376 (Checklist-Driven), L004 (Learning Capture)

Usage:
    python3 cascade_ldoc_to_sop.py --ldoc L376           # Analyze cascade
    python3 cascade_ldoc_to_sop.py --ldoc L376 --dry-run # Preview changes
    python3 cascade_ldoc_to_sop.py --ldoc L376 --apply   # Apply cascade
    python3 cascade_ldoc_to_sop.py --scan                # Find cascade candidates

Exit codes:
    0: Success
    1: No cascade needed
    2: Processing error
    3: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | L-doc file | Verify exists before parsing |
    | 2 | SOPs dir | Check sops/ exists |
    | 3 | Target SOP | Verify writable before modifying |

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
# Configuration
# =============================================================================

# L-doc categories that cascade to SOPs
CASCADE_CATEGORIES = {
    'protocol': ['SOP_*.md'],
    'process': ['SOP_*.md'],
    'governance': ['SOP_*.md', 'CHARTER.md'],
    'pattern': ['PATTERN_*.md', 'SOP_*.md'],
}

# SOP sections that L-docs can update
SOP_SECTIONS = {
    'references': r'##\s+References',
    'related': r'##\s+Related',
    'patterns': r'##\s+Patterns',
    'learnings': r'##\s+Learnings',
}

# Minimum enforcement level for cascade
MIN_ENFORCEMENT = ['recommendation', 'advisory', 'enforced']


# =============================================================================
# Timing
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# L-doc Parsing
# =============================================================================

def find_ldoc(ldoc_id: str, search_paths: List[Path]) -> Optional[Path]:
    """Find L-doc file by ID."""
    for path in search_paths:
        if not path.is_dir():
            continue
        for ldoc_file in path.glob(f"{ldoc_id}*.md"):
            return ldoc_file
    return None


def parse_ldoc_for_cascade(file_path: Path) -> Dict[str, Any]:
    """Parse L-doc for cascade analysis."""
    result = {
        'id': None,
        'title': None,
        'category': 'observation',
        'enforcement': 'observation',
        'summary': '',
        'content': '',
        'cascade_candidate': False,
        'target_sops': [],
        'cascade_type': None,
    }

    try:
        content = file_path.read_text()
    except IOError as e:
        result['error'] = f"Read error: {e}"
        return result

    result['content'] = content

    # Extract ID
    match = re.match(r'^(L\d+)', file_path.name)
    if match:
        result['id'] = match.group(1)

    # Parse frontmatter
    if content.startswith('---'):
        lines = content.split('\n')
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx:
            for line in lines[1:end_idx]:
                if ':' in line:
                    key, _, value = line.partition(':')
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    if key == 'title':
                        result['title'] = value
                    elif key == 'category':
                        result['category'] = value
                    elif key == 'summary':
                        result['summary'] = value
                    elif key == 'enforcement':
                        # Handle nested enforcement
                        pass

    # Check for enforcement in content
    enforcement_match = re.search(r'enforcement[:\s]+(\w+)', content, re.IGNORECASE)
    if enforcement_match:
        result['enforcement'] = enforcement_match.group(1).lower()

    # Extract title from header if not in frontmatter
    if not result['title']:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            result['title'] = match.group(1)

    # Determine cascade candidacy
    category = result['category']
    enforcement = result['enforcement']

    # Must be enforced or at least recommendation
    if enforcement in MIN_ENFORCEMENT:
        result['cascade_candidate'] = True

        # Determine target SOP patterns
        if category in CASCADE_CATEGORIES:
            result['target_sops'] = CASCADE_CATEGORIES[category]

        # Determine cascade type
        if category == 'protocol':
            result['cascade_type'] = 'process_update'
        elif category == 'pattern':
            result['cascade_type'] = 'reference_add'
        elif category == 'governance':
            result['cascade_type'] = 'governance_update'
        else:
            result['cascade_type'] = 'reference_add'

    return result


# =============================================================================
# SOP Analysis
# =============================================================================

def find_related_sops(agent_path: Path, ldoc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find SOPs that should reference this L-doc."""
    sops_dir = agent_path / 'sops'
    related = []

    if not sops_dir.is_dir():
        return related

    ldoc_id = ldoc.get('id', '')
    ldoc_title = ldoc.get('title', '')
    ldoc_category = ldoc.get('category', '')

    # Get target patterns
    target_patterns = ldoc.get('target_sops', ['SOP_*.md'])

    for pattern in target_patterns:
        for sop_file in sops_dir.glob(pattern):
            try:
                content = sop_file.read_text()
            except IOError:
                continue

            # Check if L-doc already referenced
            already_referenced = ldoc_id in content

            # Check for keyword matches
            keywords = ldoc_title.lower().split() if ldoc_title else []
            keyword_matches = sum(1 for kw in keywords if kw in content.lower())

            # Calculate relevance score
            score = 0
            if keyword_matches >= 2:
                score += 30
            if ldoc_category in content.lower():
                score += 20

            # Check for References section
            has_references = bool(re.search(SOP_SECTIONS['references'], content))

            related.append({
                'file': str(sop_file),
                'name': sop_file.name,
                'already_referenced': already_referenced,
                'relevance_score': score,
                'has_references_section': has_references,
                'keyword_matches': keyword_matches,
            })

    # Sort by relevance
    related.sort(key=lambda x: x['relevance_score'], reverse=True)
    return related


def generate_cascade_update(ldoc: Dict[str, Any], sop: Dict[str, Any]) -> Dict[str, Any]:
    """Generate update content for SOP."""
    update = {
        'sop': sop['name'],
        'type': ldoc.get('cascade_type', 'reference_add'),
        'content': '',
        'section': 'references',
    }

    ldoc_id = ldoc.get('id', 'Unknown')
    ldoc_title = ldoc.get('title', 'Untitled')
    ldoc_summary = ldoc.get('summary', '')[:100]

    if update['type'] == 'reference_add':
        update['content'] = f"- {ldoc_id}: {ldoc_title}"
        if ldoc_summary:
            update['content'] += f" - {ldoc_summary}"
    elif update['type'] == 'process_update':
        update['content'] = f"\n### {ldoc_id}: {ldoc_title}\n\n{ldoc_summary}\n"
        update['section'] = 'patterns'

    return update


def apply_cascade_update(sop_path: Path, update: Dict[str, Any],
                         dry_run: bool = False) -> Tuple[bool, str]:
    """Apply cascade update to SOP."""
    if not sop_path.exists():
        return False, "SOP file not found"

    try:
        content = sop_path.read_text()
    except IOError as e:
        return False, f"Read error: {e}"

    # Find target section
    section_pattern = SOP_SECTIONS.get(update['section'])
    if not section_pattern:
        section_pattern = r'##\s+References'

    match = re.search(section_pattern, content)

    if match:
        # Insert after section header
        insert_pos = match.end()
        # Find next line
        next_line = content.find('\n', insert_pos)
        if next_line != -1:
            insert_pos = next_line + 1

        new_content = (
            content[:insert_pos] +
            update['content'] + '\n' +
            content[insert_pos:]
        )
    else:
        # Append References section at end
        new_content = content.rstrip() + f"\n\n## References\n\n{update['content']}\n"

    if dry_run:
        return True, f"Would update {sop_path.name}"

    # Backup
    backup_path = sop_path.with_suffix('.md.bak')
    try:
        shutil.copy2(sop_path, backup_path)
    except IOError as e:
        return False, f"Backup failed: {e}"

    # Write update
    try:
        sop_path.write_text(new_content)
        backup_path.unlink()
        return True, f"Updated {sop_path.name}"
    except IOError as e:
        # Restore backup
        shutil.copy2(backup_path, sop_path)
        backup_path.unlink()
        return False, f"Write failed: {e}"


# =============================================================================
# Scanning
# =============================================================================

def scan_for_cascade_candidates(agent_path: Path,
                                verbose: bool = False) -> List[Dict[str, Any]]:
    """Scan for L-docs that should cascade to SOPs."""
    candidates = []

    search_paths = [
        agent_path / '.aget' / 'evolution',
        agent_path / 'evolution',
    ]

    for path in search_paths:
        if not path.is_dir():
            continue

        for ldoc_file in path.glob('L*.md'):
            if verbose:
                log_diagnostic(f"Scanning {ldoc_file.name}...")

            ldoc = parse_ldoc_for_cascade(ldoc_file)

            if ldoc.get('cascade_candidate'):
                related_sops = find_related_sops(agent_path, ldoc)
                unreferenced = [s for s in related_sops if not s['already_referenced']]

                if unreferenced:
                    candidates.append({
                        'id': ldoc.get('id'),
                        'title': ldoc.get('title'),
                        'category': ldoc.get('category'),
                        'enforcement': ldoc.get('enforcement'),
                        'target_sops': [s['name'] for s in unreferenced[:3]],
                        'file': str(ldoc_file),
                    })

    return candidates


def format_human_output(ldoc: Dict[str, Any],
                        related_sops: List[Dict[str, Any]],
                        updates: List[Dict[str, Any]]) -> str:
    """Format output for human reading."""
    lines = []

    lines.append(f"\n=== Cascade Analysis: {ldoc.get('id')} ===\n")

    lines.append(f"Title: {ldoc.get('title', 'Unknown')}")
    lines.append(f"Category: {ldoc.get('category')}")
    lines.append(f"Enforcement: {ldoc.get('enforcement')}")
    lines.append(f"Cascade Candidate: {'Yes' if ldoc.get('cascade_candidate') else 'No'}")
    lines.append(f"Cascade Type: {ldoc.get('cascade_type', 'N/A')}")
    lines.append("")

    if related_sops:
        lines.append("Related SOPs:")
        for sop in related_sops[:5]:
            ref_status = "referenced" if sop['already_referenced'] else "NOT referenced"
            lines.append(f"  - {sop['name']} ({ref_status}, score: {sop['relevance_score']})")
        lines.append("")

    if updates:
        lines.append("Proposed Updates:")
        for update in updates:
            lines.append(f"  - {update['sop']}: {update['type']}")
            lines.append(f"    Content: {update['content'][:60]}...")
        lines.append("")

    if not ldoc.get('cascade_candidate'):
        lines.append("Note: Not a cascade candidate. Requirements:")
        lines.append("  - Category: protocol, process, governance, or pattern")
        lines.append("  - Enforcement: recommendation, advisory, or enforced")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='L-doc to SOP cascade protocol (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cascade_ldoc_to_sop.py --ldoc L376
  python3 cascade_ldoc_to_sop.py --ldoc L376 --dry-run
  python3 cascade_ldoc_to_sop.py --scan

Exit codes:
  0 - Success
  1 - No cascade needed
  2 - Processing error
  3 - Configuration error
        """
    )
    parser.add_argument(
        '--ldoc',
        type=str,
        help='L-doc ID to process (e.g., L376)'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for cascade candidates'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply cascade updates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without applying'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--dir',
        type=Path,
        help='Agent directory (default: current)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='cascade_ldoc_to_sop.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if not args.ldoc and not args.scan:
        parser.error("Must specify --ldoc ID or --scan")

    if args.verbose:
        log_diagnostic("Starting L-doc to SOP cascade")

    # Determine agent path
    if args.dir:
        agent_path = args.dir.resolve()
    else:
        agent_path = Path.cwd()

    # Search paths
    search_paths = [
        agent_path / '.aget' / 'evolution',
        agent_path / 'evolution',
    ]

    # Scan mode
    if args.scan:
        candidates = scan_for_cascade_candidates(agent_path, args.verbose)

        if args.json:
            print(json.dumps({'candidates': candidates}, indent=2))
        else:
            print(f"\n=== Cascade Candidates ({len(candidates)} found) ===\n")
            for c in candidates[:10]:
                print(f"  {c['id']}: {c.get('title', 'Untitled')}")
                print(f"    Category: {c['category']}, Enforcement: {c['enforcement']}")
                print(f"    Target SOPs: {', '.join(c['target_sops'])}")
                print("")
            if len(candidates) > 10:
                print(f"  ... and {len(candidates) - 10} more")

        return 0

    # Process specific L-doc
    ldoc_file = find_ldoc(args.ldoc, search_paths)
    if not ldoc_file:
        print(f"Error: L-doc {args.ldoc} not found", file=sys.stderr)
        return 3

    if args.verbose:
        log_diagnostic(f"Found L-doc: {ldoc_file}")

    ldoc = parse_ldoc_for_cascade(ldoc_file)

    if ldoc.get('error'):
        print(f"Error: {ldoc['error']}", file=sys.stderr)
        return 2

    # Find related SOPs
    related_sops = find_related_sops(agent_path, ldoc)

    # Generate updates
    updates = []
    for sop in related_sops:
        if not sop['already_referenced'] and sop['relevance_score'] > 0:
            update = generate_cascade_update(ldoc, sop)
            updates.append(update)

    if args.json:
        print(json.dumps({
            'ldoc': ldoc,
            'related_sops': related_sops,
            'updates': updates,
        }, indent=2, default=str))
    else:
        print(format_human_output(ldoc, related_sops, updates))

    # Check if cascade needed
    if not ldoc.get('cascade_candidate') or not updates:
        return 1

    # Apply updates if requested
    if args.apply:
        for update in updates:
            sop_path = agent_path / 'sops' / update['sop']
            success, message = apply_cascade_update(sop_path, update, args.dry_run)
            print(f"  {message}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
