#!/usr/bin/env python3
"""
Wake Up Protocol - Generic Template

Initialize session for any AGET agent. Displays agent identity, version,
and session context. Designed to work across CLI agents (Claude Code,
Codex CLI, Cursor, etc.).

Implements: CAP-SESSION-001 (Wake-Up Protocol), R-SESSION-001-*
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 wake_up.py                    # Human-readable output
    python3 wake_up.py --json             # JSON output (for programmatic use)
    python3 wake_up.py --json --pretty    # Pretty-printed JSON
    python3 wake_up.py --dir /path/agent  # Run on specific agent

Exit codes:
    0: Success
    1: Agent structure validation failed
    2: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | version.json | Load before displaying version |
    | 2 | identity.json | Load before displaying north_star |
    | 3 | .aget/ dir | Verify exists before reading |
    | 4 | config.json | Load with defaults if missing |

Author: private-aget-framework-AGET (canonical template)
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


# =============================================================================
# L039: Diagnostic Efficiency - Timing
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr (L039: diagnostics to stderr)."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# Core Functions
# =============================================================================

def find_agent_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find agent root by looking for .aget/ directory.

    L021: Verify .aget/ exists before proceeding.
    """
    if start_path:
        path = Path(start_path).resolve()
    else:
        path = Path.cwd()

    # Check current and up to 3 parent levels
    for _ in range(4):
        if (path / '.aget').is_dir():
            return path
        if path.parent == path:
            break
        path = path.parent

    return None


def load_json_file(path: Path, default: Any = None) -> Any:
    """
    Load JSON file with default fallback.

    L021: Verify file exists before reading.
    """
    if not path.exists():
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def get_wake_data(agent_path: Path) -> Dict[str, Any]:
    """
    Gather all data needed for wake output.

    Returns structured dict suitable for JSON or human output.
    """
    data = {
        'timestamp': datetime.now().isoformat(),
        'agent_path': str(agent_path),
        'valid': True,
        'errors': [],
    }

    # L021 Check 1: version.json
    version_file = agent_path / '.aget' / 'version.json'
    version_data = load_json_file(version_file, {})

    data['version'] = {
        'aget_version': version_data.get('aget_version', 'unknown'),
        'updated': version_data.get('updated', ''),
        'agent_name': version_data.get('agent_name', agent_path.name),
        'archetype': version_data.get('archetype', ''),
        'template': version_data.get('template', ''),
    }

    # L021 Check 2: identity.json
    identity_file = agent_path / '.aget' / 'identity.json'
    identity_data = load_json_file(identity_file, {})

    north_star = identity_data.get('north_star', '')
    if isinstance(north_star, dict):
        north_star = north_star.get('statement', '')

    data['identity'] = {
        'name': identity_data.get('name', data['version']['agent_name']),
        'north_star': north_star,
    }

    # L021 Check 3: Structure validation
    required_dirs = ['.aget']
    optional_dirs = ['governance', 'sessions', 'planning']

    data['structure'] = {
        'required': {},
        'optional': {},
    }

    for d in required_dirs:
        exists = (agent_path / d).is_dir()
        data['structure']['required'][d] = exists
        if not exists:
            data['valid'] = False
            data['errors'].append(f"Missing required directory: {d}")

    for d in optional_dirs:
        data['structure']['optional'][d] = (agent_path / d).is_dir()

    # L021 Check 4: Config
    config_file = agent_path / '.aget' / 'config.json'
    config_data = load_json_file(config_file, {})
    data['config'] = config_data.get('wake_up', {})

    return data


def format_human_output(data: Dict[str, Any]) -> str:
    """Format data for human-readable output."""
    lines = []

    # Session header
    agent_name = data['identity']['name'] or data['version']['agent_name']
    lines.append(f"\n**Session: {agent_name}**")

    # Version
    version = data['version']['aget_version']
    updated = data['version']['updated']
    if updated:
        lines.append(f"**Version**: v{version} ({updated})")
    else:
        lines.append(f"**Version**: v{version}")

    lines.append("")

    # North star
    north_star = data['identity']['north_star']
    if north_star:
        lines.append(f"Purpose: {north_star}")
        lines.append("")

    # Archetype
    archetype = data['version']['archetype']
    if archetype:
        lines.append(f"Archetype: {archetype}")

    # Template
    template = data['version']['template']
    if template:
        lines.append(f"Template: {template}")

    if archetype or template:
        lines.append("")

    # Ready
    lines.append("Ready.")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Wake up protocol for AGET agents (v3.1 template)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. version.json - Load before displaying version
  2. identity.json - Load before displaying north_star
  3. .aget/ dir - Verify exists before reading
  4. config.json - Load with defaults if missing

Exit codes:
  0 - Success
  1 - Agent structure validation failed
  2 - Configuration error
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
        help='Agent directory (default: current directory)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output to stderr'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='wake_up.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    # L039: Diagnostic timing
    if args.verbose:
        log_diagnostic("Starting wake_up protocol")

    # Find agent root
    agent_path = find_agent_root(args.dir)

    if not agent_path:
        if args.json:
            error = {
                'valid': False,
                'errors': ['Could not find .aget/ directory'],
            }
            print(json.dumps(error, indent=2 if args.pretty else None))
        else:
            print("Error: Could not find .aget/ directory", file=sys.stderr)
        return 2

    if args.verbose:
        log_diagnostic(f"Found agent at: {agent_path}")

    # Gather data
    data = get_wake_data(agent_path)

    if args.verbose:
        log_diagnostic(f"Data gathered, valid={data['valid']}")

    # Output
    if args.json:
        print(json.dumps(data, indent=2 if args.pretty else None))
    else:
        print(format_human_output(data))

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    # Exit code based on validation
    return 0 if data['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
