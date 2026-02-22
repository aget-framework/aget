#!/usr/bin/env python3
"""
CLI Settings Validation Tool

Validate CLI settings files (CLAUDE.md, AGENTS.md, .cursorrules) for
hygiene standards compliance.

Implements: #6 (CLI Settings Hygiene Standards), R-CLI-001 to R-CLI-005
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify)

Usage:
    python3 validate_cli_settings.py /path/to/agent     # Validate agent
    python3 validate_cli_settings.py --json             # JSON output
    python3 validate_cli_settings.py --all              # Check all known files

Exit codes:
    0: All validations passed
    1: Warnings found
    2: Errors found
    3: Configuration error

Author: aget-framework
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


# =============================================================================
# Configuration
# =============================================================================

CLI_FILES = {
    'claude_code': 'CLAUDE.md',
    'codex_cli': 'AGENTS.md',
    'cursor': '.cursorrules',
    'aider': '.aider',
    'windsurf': '.windsurfrules',
}

# Validation patterns
PATTERNS = {
    'version_tag': r'@aget-version:\s*[\d.]+|Version:\s*[\d.]+',
    'north_star': r'North Star|Purpose|north_star',
    'session_protocol': r'wake up|Wind Down|Session Protocol',
    'hardcoded_path': r'/Users/|/home/|C:\\\\',
    'aget_reference': r'\.aget/',
    'secrets': r'API_KEY|SECRET|PASSWORD|TOKEN\s*=\s*["\'][^"\']+["\']',
}


# =============================================================================
# Timing
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# Validation Functions
# =============================================================================

def find_cli_files(agent_path: Path) -> Dict[str, Path]:
    """Find all CLI settings files in agent."""
    found = {}
    for cli_name, filename in CLI_FILES.items():
        file_path = agent_path / filename
        if file_path.exists():
            found[cli_name] = file_path
    return found


def validate_file(file_path: Path) -> Dict[str, Any]:
    """
    Validate a single CLI settings file.

    Returns validation result.
    """
    result = {
        'file': str(file_path),
        'name': file_path.name,
        'passed': True,
        'checks': {},
        'errors': [],
        'warnings': [],
    }

    try:
        content = file_path.read_text()
    except IOError as e:
        result['passed'] = False
        result['errors'].append(f"Read error: {e}")
        return result

    # R-CLI-003: Version tag present
    if re.search(PATTERNS['version_tag'], content, re.IGNORECASE):
        result['checks']['version_tag'] = True
        # Extract version
        match = re.search(r'@aget-version:\s*([\d.]+)|Version:\s*([\d.]+)', content)
        if match:
            result['version'] = match.group(1) or match.group(2)
    else:
        result['checks']['version_tag'] = False
        result['warnings'].append("Missing version tag (@aget-version: X.Y.Z)")

    # R-CLI-002: North Star reference
    if re.search(PATTERNS['north_star'], content, re.IGNORECASE):
        result['checks']['north_star'] = True
    else:
        result['checks']['north_star'] = False
        result['warnings'].append("Missing North Star/Purpose section")

    # R-CLI-004: Session protocol
    if re.search(PATTERNS['session_protocol'], content, re.IGNORECASE):
        result['checks']['session_protocol'] = True
    else:
        result['checks']['session_protocol'] = False
        result['warnings'].append("Missing session protocol (wake up/wind down)")

    # V-CLI-004: No hardcoded paths
    hardcoded = re.findall(PATTERNS['hardcoded_path'], content)
    if hardcoded:
        result['checks']['no_hardcoded_paths'] = False
        result['warnings'].append(f"Hardcoded paths found: {len(hardcoded)}")
    else:
        result['checks']['no_hardcoded_paths'] = True

    # V-CLI-005: References .aget/
    if re.search(PATTERNS['aget_reference'], content):
        result['checks']['aget_reference'] = True
    else:
        result['checks']['aget_reference'] = False
        result['warnings'].append("No reference to .aget/ directory")

    # Security: No secrets
    secrets = re.findall(PATTERNS['secrets'], content)
    if secrets:
        result['checks']['no_secrets'] = False
        result['errors'].append("Potential secrets found in file")
        result['passed'] = False
    else:
        result['checks']['no_secrets'] = True

    # File size check
    size_kb = len(content) / 1024
    result['size_kb'] = round(size_kb, 1)
    if size_kb > 50:
        result['checks']['reasonable_size'] = False
        result['warnings'].append(f"File size {size_kb:.1f}KB exceeds 50KB recommendation")
    else:
        result['checks']['reasonable_size'] = True

    # Determine pass/fail
    if result['errors']:
        result['passed'] = False

    return result


def validate_identity_sync(agent_path: Path, cli_content: str) -> Tuple[bool, str]:
    """
    Check if CLI north star matches identity.json.

    Returns (synced, message).
    """
    identity_path = agent_path / '.aget' / 'identity.json'
    if not identity_path.exists():
        return True, "No identity.json to compare"

    try:
        with open(identity_path) as f:
            identity = json.load(f)
    except (json.JSONDecodeError, IOError):
        return True, "Could not read identity.json"

    north_star = identity.get('north_star', '')
    if isinstance(north_star, dict):
        north_star = north_star.get('statement', '')

    if not north_star:
        return True, "No north_star in identity.json"

    # Check if north star text appears in CLI file
    if north_star[:50] in cli_content:  # Check first 50 chars
        return True, "North star synced"
    else:
        return False, "North star may be out of sync with identity.json"


def validate_agent(agent_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Validate all CLI settings for an agent.

    Returns validation result.
    """
    result = {
        'timestamp': datetime.now().isoformat(),
        'agent_path': str(agent_path),
        'files_found': 0,
        'files_passed': 0,
        'files_warned': 0,
        'overall_status': 'unknown',
        'files': [],
    }

    if not agent_path.is_dir():
        result['overall_status'] = 'error'
        result['error'] = f"Not a directory: {agent_path}"
        return result

    # Find CLI files
    cli_files = find_cli_files(agent_path)
    result['files_found'] = len(cli_files)

    if not cli_files:
        result['overall_status'] = 'warning'
        result['warning'] = "No CLI settings files found"
        return result

    if verbose:
        log_diagnostic(f"Found {len(cli_files)} CLI settings file(s)")

    # Validate each file
    for cli_name, file_path in cli_files.items():
        if verbose:
            log_diagnostic(f"Validating {file_path.name}...")

        file_result = validate_file(file_path)
        file_result['cli_type'] = cli_name

        # Check identity sync
        try:
            content = file_path.read_text()
            synced, sync_msg = validate_identity_sync(agent_path, content)
            file_result['identity_sync'] = synced
            if not synced:
                file_result['warnings'].append(sync_msg)
        except IOError:
            pass

        result['files'].append(file_result)

        if file_result['passed']:
            result['files_passed'] += 1
        if file_result['warnings']:
            result['files_warned'] += 1

    # Determine overall status
    errors = sum(1 for f in result['files'] if not f['passed'])
    warnings = sum(1 for f in result['files'] if f['warnings'])

    if errors > 0:
        result['overall_status'] = 'error'
    elif warnings > 0:
        result['overall_status'] = 'warning'
    else:
        result['overall_status'] = 'healthy'

    return result


def format_human_output(result: Dict[str, Any]) -> str:
    """Format result for human-readable output."""
    lines = []

    lines.append("\n=== CLI Settings Validation ===\n")

    status = result.get('overall_status', 'unknown')
    status_symbol = {
        'healthy': '+',
        'warning': '!',
        'error': 'x'
    }.get(status, '?')

    lines.append(f"Status: [{status_symbol}] {status.upper()}")
    lines.append(f"Files: {result.get('files_found', 0)} found, {result.get('files_passed', 0)} passed")
    lines.append("")

    for file_result in result.get('files', []):
        symbol = '+' if file_result['passed'] else 'x'
        name = file_result['name']
        cli_type = file_result.get('cli_type', 'unknown')
        version = file_result.get('version', 'unknown')

        lines.append(f"  [{symbol}] {name} ({cli_type}) - v{version}")

        # Checks
        for check, passed in file_result.get('checks', {}).items():
            check_symbol = '+' if passed else '!'
            lines.append(f"      [{check_symbol}] {check.replace('_', ' ')}")

        # Errors
        for error in file_result.get('errors', []):
            lines.append(f"      [x] {error}")

        # Warnings
        for warning in file_result.get('warnings', []):
            lines.append(f"      [!] {warning}")

    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Validate CLI settings hygiene (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks performed:
  - Version tag present (R-CLI-003)
  - North Star section exists (R-CLI-002)
  - Session protocol defined (R-CLI-004)
  - No hardcoded paths (V-CLI-004)
  - References .aget/ (V-CLI-005)
  - No secrets/credentials
  - Reasonable file size

Exit codes:
  0 - All validations passed
  1 - Warnings found
  2 - Errors found
  3 - Configuration error
        """
    )
    parser.add_argument(
        'path',
        type=Path,
        nargs='?',
        default=Path.cwd(),
        help='Agent directory (default: current directory)'
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
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='validate_cli_settings.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if args.verbose:
        log_diagnostic("Starting CLI settings validation")

    agent_path = args.path.resolve()

    if not agent_path.is_dir():
        print(f"Error: Not a directory: {agent_path}", file=sys.stderr)
        return 3

    result = validate_agent(agent_path, args.verbose)

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
