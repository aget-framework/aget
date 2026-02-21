#!/usr/bin/env python3
"""
Wake Up Protocol - Canonical Framework Script

Initialize session for any AGET agent. Displays agent identity, version,
and session context. Designed to work across CLI agents (Claude Code,
Codex CLI, Cursor, etc.).

Implements:
    CAP-SESSION-001 (Wake-Up Protocol), R-SESSION-001-*
    CAP-SESSION-011 (Calendar-Aware Wake-Up)
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)
Extension: WU-008 (Extension Hook per SKILL-001 v1.1.0)

Usage:
    python3 wake_up.py                    # Human-readable output
    python3 wake_up.py --json             # JSON output (for programmatic use)
    python3 wake_up.py --json --pretty    # Pretty-printed JSON
    python3 wake_up.py --dir /path/agent  # Run on specific agent
    python3 wake_up.py --verify           # Migration verification (L491)

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

Author: aget-framework (canonical template)
Version: 2.0.0 (v3.6.0)
"""

import argparse
import importlib.util
import json
import os
import subprocess
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
# Config-driven display defaults (C3 — CAP-SESSION-001)
# =============================================================================

DEFAULT_CONFIG = {
    'show_version': True,
    'show_purpose': True,
    'show_archetype': True,
    'show_template': True,
    'show_git_status': True,
    'show_structure': False,
    'show_calendar': True,
}


# =============================================================================
# Core Functions
# =============================================================================

def find_agent_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find agent root by looking for .aget/ directory."""
    if start_path:
        path = Path(start_path).resolve()
    else:
        path = Path.cwd()

    for _ in range(4):
        if (path / '.aget').is_dir():
            return path
        if path.parent == path:
            break
        path = path.parent

    return None


def load_json_file(path: Path, default: Any = None) -> Any:
    """Load JSON file with default fallback."""
    if not path.exists():
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def get_git_status(agent_path: Path) -> Dict[str, Any]:
    """Get git status for the agent directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, timeout=5,
            cwd=str(agent_path),
        )
        branch = result.stdout.strip() if result.returncode == 0 else 'unknown'

        result2 = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=5,
            cwd=str(agent_path),
        )
        clean = len(result2.stdout.strip()) == 0 if result2.returncode == 0 else None

        return {'branch': branch, 'clean': clean}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {'branch': 'unknown', 'clean': None}


def get_calendar_context(config: Dict[str, Any]) -> Dict[str, Any]:
    """CAP-SESSION-011: Calendar awareness for session context."""
    now = datetime.now()
    day_name = now.strftime('%A')
    date_str = now.strftime('%Y-%m-%d')

    # Release window detection (config-driven)
    release_windows = config.get('release_windows', [])
    in_release_window = False
    window_name = ''

    for window in release_windows:
        window_day = window.get('day', '')
        window_period = window.get('period', '')
        if day_name.lower() == window_day.lower():
            hour = now.hour
            if window_period == 'AM' and hour < 12:
                in_release_window = True
                window_name = f"{window_day} {window_period}"
            elif window_period == 'PM' and hour >= 12:
                in_release_window = True
                window_name = f"{window_day} {window_period}"

    return {
        'date': date_str,
        'day': day_name,
        'in_release_window': in_release_window,
        'release_window': window_name,
    }


def get_wake_data(agent_path: Path) -> Dict[str, Any]:
    """Gather all data needed for wake output."""
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

    # L021 Check 4: Config (C3 — config-driven display)
    config_file = agent_path / '.aget' / 'config.json'
    config_data = load_json_file(config_file, {})
    wake_config = config_data.get('wake_up', {})

    # Merge with defaults
    data['config'] = {**DEFAULT_CONFIG, **wake_config}

    # Git status (conditional on config toggle)
    if data['config'].get('show_git_status', True):
        data['git'] = get_git_status(agent_path)

    # Calendar awareness (CAP-SESSION-011)
    if data['config'].get('show_calendar', True):
        data['calendar'] = get_calendar_context(wake_config)

    return data


def call_extension_hook(agent_path: Path, data: Dict[str, Any],
                        verbose: bool = False) -> Dict[str, Any]:
    """C1 Extension Hook (WU-008): Call wake_up_ext.py:post_wake(data) if present.

    Contract per SKILL-001 v1.1.0 WU-008:
    - Hook receives data dict
    - Hook returns augmented data dict (additive-only per L464)
    - Hook absence = no-op
    - Hook failure = warning + continue
    """
    ext_path = agent_path / 'scripts' / 'wake_up_ext.py'
    if not ext_path.exists():
        return data

    try:
        spec = importlib.util.spec_from_file_location('wake_up_ext', str(ext_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'post_wake'):
            result = module.post_wake(data)
            if isinstance(result, dict):
                return result
            if verbose:
                log_diagnostic("Extension hook returned non-dict, ignoring")
    except Exception as e:
        print(f"Warning: Extension hook failed: {e}", file=sys.stderr)

    return data


def format_human_output(data: Dict[str, Any]) -> str:
    """Format data for human-readable output with config-driven toggles."""
    lines = []
    config = data.get('config', DEFAULT_CONFIG)

    # Session header
    agent_name = data['identity']['name'] or data['version']['agent_name']
    lines.append(f"\n**Session: {agent_name}**")

    # Version (toggle: show_version)
    if config.get('show_version', True):
        version = data['version']['aget_version']
        updated = data['version']['updated']
        if updated:
            lines.append(f"**Version**: v{version} ({updated})")
        else:
            lines.append(f"**Version**: v{version}")

    lines.append("")

    # North star (toggle: show_purpose)
    if config.get('show_purpose', True):
        north_star = data['identity']['north_star']
        if north_star:
            lines.append(f"Purpose: {north_star}")
            lines.append("")

    # Archetype (toggle: show_archetype)
    if config.get('show_archetype', True):
        archetype = data['version']['archetype']
        if archetype:
            lines.append(f"Archetype: {archetype}")

    # Template (toggle: show_template)
    if config.get('show_template', True):
        template = data['version']['template']
        if template:
            lines.append(f"Template: {template}")

    # Git status (toggle: show_git_status)
    if config.get('show_git_status', True) and 'git' in data:
        git = data['git']
        status = 'clean' if git.get('clean') else 'dirty' if git.get('clean') is False else ''
        if status:
            lines.append(f"Git: {git['branch']} ({status})")
        else:
            lines.append(f"Git: {git['branch']}")

    # Structure (toggle: show_structure)
    if config.get('show_structure', False):
        optional = data.get('structure', {}).get('optional', {})
        present = [d for d, exists in optional.items() if exists]
        if present:
            lines.append(f"Directories: {', '.join(present)}")

    # Calendar (toggle: show_calendar, CAP-SESSION-011)
    if config.get('show_calendar', True) and 'calendar' in data:
        cal = data['calendar']
        lines.append(f"Date: {cal['date']} ({cal['day']})")
        if cal.get('in_release_window'):
            lines.append(f"Release Window: {cal['release_window']}")

    lines.append("")

    # Extension output (from hook)
    ext_output = data.get('extension_output', '')
    if ext_output:
        lines.append(ext_output)
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
        description='Wake up protocol for AGET agents (v2.0.0)',
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
        '--json', action='store_true',
        help='Output as JSON',
    )
    parser.add_argument(
        '--pretty', action='store_true',
        help='Pretty-print JSON output',
    )
    parser.add_argument(
        '--dir', type=Path,
        help='Agent directory (default: current directory)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable diagnostic output to stderr',
    )
    parser.add_argument(
        '--verify', action='store_true',
        help='Migration verification: confirm script is at canonical path (L491)',
    )
    parser.add_argument(
        '--version', action='version',
        version='wake_up.py 2.0.0 (AGET v3.6.0)',
    )

    args = parser.parse_args()

    # L491: --verify mode
    if args.verify:
        script_path = Path(__file__).resolve()
        agent_root = find_agent_root(script_path.parent)
        if agent_root:
            expected = agent_root / 'scripts' / 'wake_up.py'
            if script_path == expected.resolve():
                print(f"PASS: wake_up.py at canonical path: {expected}")
                return 0
            else:
                print(f"WARN: wake_up.py at {script_path}, expected {expected}")
                return 1
        print("WARN: Could not determine agent root for verification")
        return 1

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

    # C1 Extension Hook (WU-008)
    data = call_extension_hook(agent_path, data, verbose=args.verbose)

    if args.verbose:
        log_diagnostic("Extension hook complete")

    # Output
    if args.json:
        print(json.dumps(data, indent=2 if args.pretty else None, default=str))
    else:
        print(format_human_output(data))

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    return 0 if data['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
