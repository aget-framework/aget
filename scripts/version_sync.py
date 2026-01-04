#!/usr/bin/env python3
"""
Version Sync Tool

Check and synchronize versions across AGET framework repositories.
Ensures all templates match the core framework version.

Implements: #10 (Fleet Validation Tooling), R-REL-001
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify)

Usage:
    python3 version_sync.py --check              # Check version consistency
    python3 version_sync.py --check --json       # JSON output
    python3 version_sync.py --sync TO_VERSION    # Sync all to version
    python3 version_sync.py --sync TO_VERSION --dry-run  # Preview sync

Exit codes:
    0: All versions in sync
    1: Version drift detected
    2: Sync failed
    3: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | repos dir | Verify exists before scanning |
    | 2 | version.json | Load before reading version |
    | 3 | version.json | Verify writable before updating |

Author: private-aget-framework-AGET
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# L039: Diagnostic Efficiency
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# Configuration
# =============================================================================

TEMPLATE_REPOS = [
    'template-supervisor-aget',
    'template-worker-aget',
    'template-advisor-aget',
    'template-consultant-aget',
    'template-developer-aget',
    'template-spec-engineer-aget',
]

CORE_REPO = 'aget'


# =============================================================================
# Version Functions
# =============================================================================

def get_version(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Get version from repository.

    Returns (version, error).
    """
    version_file = repo_path / '.aget' / 'version.json'

    # L021 Check 2: Load before reading
    if not version_file.exists():
        return None, 'version.json not found'

    try:
        with open(version_file) as f:
            data = json.load(f)
        return data.get('aget_version'), None
    except json.JSONDecodeError as e:
        return None, f'Invalid JSON: {e}'
    except IOError as e:
        return None, f'Read error: {e}'


def set_version(repo_path: Path, new_version: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Set version in repository.

    Returns (success, message).
    """
    version_file = repo_path / '.aget' / 'version.json'

    # L021 Check 3: Verify writable
    if not version_file.exists():
        return False, 'version.json not found'

    try:
        with open(version_file) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return False, f'Read error: {e}'

    old_version = data.get('aget_version', 'unknown')

    if old_version == new_version:
        return True, f'Already at {new_version}'

    if dry_run:
        return True, f'Would update {old_version} -> {new_version}'

    # Update version
    data['aget_version'] = new_version
    data['updated'] = datetime.now().strftime('%Y-%m-%d')

    # Add to migration history if present
    if 'migration_history' in data:
        history_entry = f"v{old_version} -> v{new_version}: {data['updated']} (version sync)"
        data['migration_history'].append(history_entry)

    try:
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True, f'Updated {old_version} -> {new_version}'
    except IOError as e:
        return False, f'Write error: {e}'


def find_repos(base_path: Path) -> Dict[str, Path]:
    """Find repositories."""
    repos = {}

    # Core
    core_path = base_path / CORE_REPO
    if core_path.is_dir():
        repos[CORE_REPO] = core_path

    # Templates
    for template in TEMPLATE_REPOS:
        template_path = base_path / template
        if template_path.is_dir():
            repos[template] = template_path

    return repos


def check_versions(base_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Check version consistency across fleet.

    Returns check result.
    """
    result = {
        'timestamp': datetime.now().isoformat(),
        'base_path': str(base_path),
        'consistent': True,
        'core_version': None,
        'repos': {},
        'drift': []
    }

    repos = find_repos(base_path)

    if not repos:
        result['error'] = 'No repositories found'
        return result

    # Get all versions
    for name, path in repos.items():
        version, error = get_version(path)
        result['repos'][name] = {
            'version': version,
            'error': error
        }

        if name == CORE_REPO and version:
            result['core_version'] = version

    # Check consistency
    core_version = result['core_version']
    if core_version:
        for name, info in result['repos'].items():
            if name != CORE_REPO:
                if info['version'] != core_version:
                    result['consistent'] = False
                    result['drift'].append({
                        'repo': name,
                        'expected': core_version,
                        'actual': info['version']
                    })

    return result


def sync_versions(base_path: Path, target_version: str,
                  dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Synchronize all repos to target version.

    Returns sync result.
    """
    result = {
        'timestamp': datetime.now().isoformat(),
        'target_version': target_version,
        'dry_run': dry_run,
        'success': True,
        'updates': []
    }

    repos = find_repos(base_path)

    for name, path in repos.items():
        if verbose:
            log_diagnostic(f"Syncing {name}...")

        success, message = set_version(path, target_version, dry_run)
        result['updates'].append({
            'repo': name,
            'success': success,
            'message': message
        })

        if not success:
            result['success'] = False

    return result


def format_check_output(result: Dict[str, Any]) -> str:
    """Format check result for human output."""
    lines = []

    lines.append("\n=== Version Sync Check ===\n")

    core = result.get('core_version', 'unknown')
    lines.append(f"Core Version: {core}")

    if result.get('consistent'):
        lines.append("[+] All versions in sync")
    else:
        lines.append("[!] Version drift detected")

    lines.append("")

    # List versions
    for name, info in result.get('repos', {}).items():
        version = info.get('version', 'unknown')
        error = info.get('error')

        if error:
            lines.append(f"  [x] {name}: {error}")
        elif name == CORE_REPO:
            lines.append(f"  [*] {name}: v{version} (core)")
        elif version != core:
            lines.append(f"  [!] {name}: v{version} (expected {core})")
        else:
            lines.append(f"  [+] {name}: v{version}")

    lines.append("")

    return "\n".join(lines)


def format_sync_output(result: Dict[str, Any]) -> str:
    """Format sync result for human output."""
    lines = []

    target = result.get('target_version')
    dry_run = result.get('dry_run')

    lines.append("\n=== Version Sync ===\n")
    lines.append(f"Target: v{target}")

    if dry_run:
        lines.append("[DRY RUN - no changes made]")

    lines.append("")

    for update in result.get('updates', []):
        name = update['repo']
        success = update['success']
        message = update['message']

        symbol = '+' if success else 'x'
        lines.append(f"  [{symbol}] {name}: {message}")

    lines.append("")

    if result.get('success'):
        lines.append("[+] Sync complete")
    else:
        lines.append("[x] Sync failed")

    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Check and sync AGET framework versions (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 version_sync.py --check
  python3 version_sync.py --sync 3.1.0
  python3 version_sync.py --sync 3.1.0 --dry-run

Exit codes:
  0 - Versions in sync / sync successful
  1 - Version drift detected / sync warnings
  2 - Sync failed
  3 - Configuration error
        """
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check version consistency'
    )
    parser.add_argument(
        '--sync',
        type=str,
        metavar='VERSION',
        help='Sync all repos to VERSION'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON'
    )
    parser.add_argument(
        '--dir',
        type=Path,
        help='Base directory (default: parent of aget/)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview sync without changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='version_sync.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if not args.check and not args.sync:
        parser.error("Must specify --check or --sync VERSION")

    if args.verbose:
        log_diagnostic("Starting version sync")

    # Determine base path
    if args.dir:
        base_path = args.dir.resolve()
    else:
        script_path = Path(__file__).resolve()
        base_path = script_path.parent.parent.parent

    # L021 Check 1: Verify base path
    if not base_path.is_dir():
        print(f"Error: Base path not found: {base_path}", file=sys.stderr)
        return 3

    if args.verbose:
        log_diagnostic(f"Base path: {base_path}")

    # Execute command
    if args.check:
        result = check_versions(base_path, args.verbose)

        if args.json:
            print(json.dumps(result, indent=2 if args.pretty else None))
        else:
            print(format_check_output(result))

        return 0 if result.get('consistent') else 1

    elif args.sync:
        result = sync_versions(base_path, args.sync, args.dry_run, args.verbose)

        if args.json:
            print(json.dumps(result, indent=2 if args.pretty else None))
        else:
            print(format_sync_output(result))

        return 0 if result.get('success') else 2


if __name__ == '__main__':
    sys.exit(main())
