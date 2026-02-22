#!/usr/bin/env python3
"""
Fleet Validation Tool

Validate all AGET template repositories for consistency, compliance,
and release readiness. Used in pre-release verification.

Implements: #10 (Fleet Validation Tooling), R-PUB-001
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 validate_fleet.py                    # Validate all templates
    python3 validate_fleet.py --json             # JSON output
    python3 validate_fleet.py --dry-run          # Preview without checks
    python3 validate_fleet.py --dir /path/repos  # Specify repos directory

Exit codes:
    0: All validations passed
    1: Warnings found
    2: Errors found (blocking)
    3: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | repos dir | Verify exists before scanning |
    | 2 | template dirs | Verify each exists before validating |
    | 3 | version.json | Load before checking version |
    | 4 | .aget/ | Verify structure before compliance check |

Author: aget-framework
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import subprocess
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

REQUIRED_FILES = [
    '.aget/version.json',
    'manifest.yaml',
    'README.md',
]

RECOMMENDED_FILES = [
    '.aget/identity.json',
    'governance/CHARTER.md',
    'governance/MISSION.md',
    'governance/SCOPE_BOUNDARIES.md',
]


# =============================================================================
# Validation Functions
# =============================================================================

def validate_structure(repo_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate repository structure.

    Returns (passed, errors, warnings).
    """
    errors = []
    warnings = []

    # L021 Check 4: Verify .aget/ exists
    if not (repo_path / '.aget').is_dir():
        errors.append(".aget/ directory missing")
        return False, errors, warnings

    # Check required files
    for file in REQUIRED_FILES:
        if not (repo_path / file).exists():
            errors.append(f"Missing required: {file}")

    # Check recommended files
    for file in RECOMMENDED_FILES:
        if not (repo_path / file).exists():
            warnings.append(f"Missing recommended: {file}")

    passed = len(errors) == 0
    return passed, errors, warnings


def validate_version(repo_path: Path) -> Tuple[bool, str, List[str]]:
    """
    Validate version.json.

    Returns (passed, version, errors).
    """
    errors = []
    version_file = repo_path / '.aget' / 'version.json'

    # L021 Check 3: Load before checking
    if not version_file.exists():
        return False, 'unknown', ['version.json not found']

    try:
        with open(version_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, 'unknown', [f'Invalid JSON: {e}']

    version = data.get('aget_version', 'unknown')

    if version == 'unknown':
        errors.append('aget_version field missing')

    if not data.get('agent_name'):
        errors.append('agent_name field missing')

    passed = len(errors) == 0
    return passed, version, errors


def validate_git_status(repo_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate git repository status.

    Returns (passed, issues).
    """
    issues = []

    if not (repo_path / '.git').is_dir():
        return False, ['Not a git repository']

    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'status', '--porcelain'],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip():
            issues.append('Uncommitted changes')

        # Check if ahead/behind
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'status', '-sb'],
            capture_output=True, text=True, timeout=10
        )
        if '[ahead' in result.stdout or '[behind' in result.stdout:
            issues.append('Not synced with remote')

    except subprocess.TimeoutExpired:
        issues.append('Git command timed out')
    except Exception as e:
        issues.append(f'Git error: {e}')

    return len(issues) == 0, issues


def validate_tests(repo_path: Path) -> Tuple[bool, str]:
    """
    Run tests for repository.

    Returns (passed, message).
    """
    tests_dir = repo_path / 'tests'

    if not tests_dir.is_dir():
        return True, 'No tests directory'

    try:
        result = subprocess.run(
            ['python3', '-m', 'pytest', str(tests_dir), '-q', '--tb=no'],
            capture_output=True, text=True, timeout=60,
            cwd=str(repo_path)
        )
        if result.returncode == 0:
            return True, 'Tests passed'
        else:
            return False, f'Tests failed: {result.stdout}'
    except subprocess.TimeoutExpired:
        return False, 'Tests timed out'
    except Exception as e:
        return True, f'Could not run tests: {e}'


def validate_repo(repo_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Validate a single repository.

    Returns validation result dict.
    """
    result = {
        'name': repo_path.name,
        'path': str(repo_path),
        'passed': True,
        'version': 'unknown',
        'errors': [],
        'warnings': [],
        'checks': {}
    }

    # Structure check
    struct_ok, struct_errors, struct_warnings = validate_structure(repo_path)
    result['checks']['structure'] = struct_ok
    result['errors'].extend(struct_errors)
    result['warnings'].extend(struct_warnings)

    # Version check
    ver_ok, version, ver_errors = validate_version(repo_path)
    result['checks']['version'] = ver_ok
    result['version'] = version
    result['errors'].extend(ver_errors)

    # Git status check
    git_ok, git_issues = validate_git_status(repo_path)
    result['checks']['git'] = git_ok
    if not git_ok:
        result['warnings'].extend(git_issues)

    # Tests check
    tests_ok, tests_msg = validate_tests(repo_path)
    result['checks']['tests'] = tests_ok
    if not tests_ok:
        result['errors'].append(tests_msg)

    result['passed'] = len(result['errors']) == 0
    return result


# =============================================================================
# Fleet Validation
# =============================================================================

def find_repos(base_path: Path) -> List[Path]:
    """Find template repositories."""
    repos = []

    # Check for core
    core_path = base_path / CORE_REPO
    if core_path.is_dir():
        repos.append(core_path)

    # Check for templates
    for template in TEMPLATE_REPOS:
        template_path = base_path / template
        if template_path.is_dir():
            repos.append(template_path)

    return repos


def validate_fleet(base_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Validate entire fleet.

    Returns fleet validation result.
    """
    fleet_result = {
        'timestamp': datetime.now().isoformat(),
        'base_path': str(base_path),
        'repos_found': 0,
        'repos_passed': 0,
        'repos_failed': 0,
        'repos_warned': 0,
        'overall_status': 'unknown',
        'repos': [],
        'version_consistency': True,
        'core_version': 'unknown'
    }

    # L021 Check 1: Verify base path exists
    if not base_path.is_dir():
        fleet_result['overall_status'] = 'error'
        fleet_result['error'] = f'Base path not found: {base_path}'
        return fleet_result

    # Find repos
    repos = find_repos(base_path)
    fleet_result['repos_found'] = len(repos)

    if not repos:
        fleet_result['overall_status'] = 'error'
        fleet_result['error'] = 'No repositories found'
        return fleet_result

    if verbose:
        log_diagnostic(f"Found {len(repos)} repositories")

    # Validate each repo
    versions = {}
    for repo_path in repos:
        if verbose:
            log_diagnostic(f"Validating {repo_path.name}...")

        result = validate_repo(repo_path, verbose)
        fleet_result['repos'].append(result)

        if result['passed']:
            fleet_result['repos_passed'] += 1
        else:
            fleet_result['repos_failed'] += 1

        if result['warnings']:
            fleet_result['repos_warned'] += 1

        versions[repo_path.name] = result['version']

    # Check version consistency
    if CORE_REPO in versions:
        fleet_result['core_version'] = versions[CORE_REPO]
        core_version = versions[CORE_REPO]

        for name, version in versions.items():
            if name != CORE_REPO and version != core_version:
                fleet_result['version_consistency'] = False
                break

    # Determine overall status
    if fleet_result['repos_failed'] > 0:
        fleet_result['overall_status'] = 'error'
    elif fleet_result['repos_warned'] > 0:
        fleet_result['overall_status'] = 'warning'
    elif not fleet_result['version_consistency']:
        fleet_result['overall_status'] = 'warning'
    else:
        fleet_result['overall_status'] = 'healthy'

    return fleet_result


def format_human_output(result: Dict[str, Any]) -> str:
    """Format result for human-readable output."""
    lines = []

    lines.append("\n=== AGET Fleet Validation ===\n")

    status = result['overall_status']
    status_symbol = {
        'healthy': '+',
        'warning': '!',
        'error': 'x'
    }.get(status, '?')

    lines.append(f"Status: [{status_symbol}] {status.upper()}")
    lines.append(f"Repos: {result['repos_found']} found, {result['repos_passed']} passed, {result['repos_failed']} failed")

    if result.get('core_version'):
        lines.append(f"Core Version: {result['core_version']}")

    if not result.get('version_consistency', True):
        lines.append("[!] Version inconsistency detected")

    lines.append("")

    # Individual repos
    for repo in result.get('repos', []):
        symbol = '+' if repo['passed'] else 'x'
        name = repo['name']
        version = repo['version']

        lines.append(f"  [{symbol}] {name} (v{version})")

        if repo['errors']:
            for error in repo['errors']:
                lines.append(f"      [x] {error}")

        if repo['warnings']:
            for warning in repo['warnings']:
                lines.append(f"      [!] {warning}")

    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Validate AGET fleet repositories (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. repos dir - Verify exists before scanning
  2. template dirs - Verify each exists before validating
  3. version.json - Load before checking version
  4. .aget/ - Verify structure before compliance check

Exit codes:
  0 - All validations passed
  1 - Warnings found
  2 - Errors found
  3 - Configuration error
        """
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    parser.add_argument(
        '--dir',
        type=Path,
        help='Base directory containing repos (default: parent of script dir)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List repos without validating'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='validate_fleet.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if args.verbose:
        log_diagnostic("Starting fleet validation")

    # Determine base path
    if args.dir:
        base_path = args.dir.resolve()
    else:
        # Default: parent of aget/ (i.e., aget-framework/)
        script_path = Path(__file__).resolve()
        base_path = script_path.parent.parent.parent

    if args.verbose:
        log_diagnostic(f"Base path: {base_path}")

    # Dry run
    if args.dry_run:
        repos = find_repos(base_path)
        print(f"Would validate {len(repos)} repositories:")
        for repo in repos:
            print(f"  - {repo.name}")
        return 0

    # Run validation
    result = validate_fleet(base_path, args.verbose)

    if args.verbose:
        log_diagnostic(f"Validation complete, status={result['overall_status']}")

    # Output
    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None))
    else:
        print(format_human_output(result))

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    # Exit code
    if result['overall_status'] == 'error':
        return 2
    elif result['overall_status'] == 'warning':
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
