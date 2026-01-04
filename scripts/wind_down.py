#!/usr/bin/env python3
"""
Wind Down Protocol - Generic Template

End session for any AGET agent with proper state capture and sanity checks.
Designed to work across CLI agents (Claude Code, Codex CLI, Cursor, etc.).

Implements: CAP-SESSION-003 (Wind Down Protocol), R-WIND-001-*
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 wind_down.py                    # Human-readable output
    python3 wind_down.py --json             # JSON output (for programmatic use)
    python3 wind_down.py --json --pretty    # Pretty-printed JSON
    python3 wind_down.py --dir /path/agent  # Run on specific agent
    python3 wind_down.py --notes "..."      # Add handoff notes
    python3 wind_down.py --skip-sanity      # Skip sanity check (not recommended)

Exit codes:
    0: Clean close (sanity healthy)
    1: Close with warnings
    2: Close with errors (requires acknowledgment in interactive mode)
    3: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | session_state.json | Load to calculate duration |
    | 2 | housekeeping | Run sanity check before summary |
    | 3 | planning/ | Scan for pending work |
    | 4 | sessions/ | Verify exists before writing |

Author: private-aget-framework-AGET (canonical template)
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
from typing import Dict, Any, List, Optional


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


def run_sanity_check(agent_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run housekeeping sanity check.

    L021 Check 2: Run sanity before generating summary.
    """
    # Try to find housekeeping script
    script_locations = [
        agent_path / '.aget' / 'patterns' / 'session' / 'sanity_check.py',
        agent_path / '.aget' / 'patterns' / 'session' / 'housekeeping.py',
        Path(__file__).parent / 'aget_housekeeping_protocol.py',
    ]

    script_path = None
    for loc in script_locations:
        if loc.exists():
            script_path = loc
            break

    if not script_path:
        # Return minimal result if no script found
        return {
            'status': 'unknown',
            'checks_passed': 0,
            'checks_total': 0,
            'warnings': 0,
            'errors': 0,
            'message': 'No sanity check script found'
        }

    try:
        result = subprocess.run(
            ['python3', str(script_path), '--json', '--dir', str(agent_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout:
            data = json.loads(result.stdout)
            return {
                'status': data.get('status', 'unknown'),
                'checks_passed': data.get('summary', {}).get('passed', 0),
                'checks_total': data.get('summary', {}).get('total', 0),
                'warnings': data.get('summary', {}).get('warnings', 0),
                'errors': data.get('summary', {}).get('errors', 0),
                'message': ''
            }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        if verbose:
            log_diagnostic(f"Sanity check error: {e}")

    return {
        'status': 'error',
        'checks_passed': 0,
        'checks_total': 0,
        'warnings': 0,
        'errors': 1,
        'message': 'Sanity check failed to execute'
    }


def get_session_state(agent_path: Path) -> Dict[str, Any]:
    """
    Load session state if available.

    L021 Check 1: Load session_state.json to calculate duration.
    """
    state_file = agent_path / '.aget' / 'session_state.json'
    return load_json_file(state_file, {})


def scan_pending_work(agent_path: Path) -> List[str]:
    """
    Scan planning/ for in-progress work.

    L021 Check 3: Scan planning/ directory.
    """
    pending = []
    planning_dir = agent_path / 'planning'

    if not planning_dir.is_dir():
        return pending

    for plan_file in planning_dir.glob('PROJECT_PLAN_*.md'):
        try:
            content = plan_file.read_text()
            # Look for in_progress or IN_PROGRESS markers
            if 'IN_PROGRESS' in content.upper() or 'status: in_progress' in content.lower():
                pending.append(plan_file.name)
        except IOError:
            pass

    return pending


def get_wind_down_data(agent_path: Path,
                       skip_sanity: bool = False,
                       handoff_notes: str = "",
                       verbose: bool = False) -> Dict[str, Any]:
    """
    Gather all data needed for wind down output.

    Returns structured dict suitable for JSON or human output.
    """
    now = datetime.now()

    data = {
        'timestamp': now.isoformat(),
        'agent_path': str(agent_path),
        'session': {
            'ended': now.isoformat(),
            'started': None,
            'duration_seconds': None,
        },
        'sanity_check': {},
        'pending_work': [],
        'handoff_notes': handoff_notes,
        'clean_close': True,
    }

    # L021 Check 1: Session state
    session_state = get_session_state(agent_path)
    current = session_state.get('current_session', {})
    if current.get('started'):
        data['session']['started'] = current['started']
        try:
            started = datetime.fromisoformat(current['started'])
            data['session']['duration_seconds'] = int((now - started).total_seconds())
        except ValueError:
            pass

    # L021 Check 2: Sanity check
    if skip_sanity:
        data['sanity_check'] = {
            'status': 'skipped',
            'checks_passed': 0,
            'checks_total': 0,
            'warnings': 0,
            'errors': 0,
            'message': 'Sanity check skipped by user'
        }
    else:
        if verbose:
            log_diagnostic("Running sanity check...")
        data['sanity_check'] = run_sanity_check(agent_path, verbose)

    # L021 Check 3: Pending work
    data['pending_work'] = scan_pending_work(agent_path)

    # Determine clean close
    sanity_status = data['sanity_check'].get('status', 'unknown')
    if sanity_status == 'error':
        data['clean_close'] = False
    elif sanity_status == 'warning':
        data['clean_close'] = True  # Warnings allow close

    # Load agent identity for display
    version_file = agent_path / '.aget' / 'version.json'
    version_data = load_json_file(version_file, {})
    data['agent_name'] = version_data.get('agent_name', agent_path.name)

    return data


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in human-readable form."""
    if seconds is None:
        return "unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def format_human_output(data: Dict[str, Any]) -> str:
    """Format data for human-readable output."""
    lines = []

    # Session header
    agent_name = data.get('agent_name', 'unknown')
    lines.append(f"\n**Session Complete: {agent_name}**")

    # Duration
    duration = format_duration(data['session'].get('duration_seconds'))
    lines.append(f"**Duration**: {duration}")
    lines.append("")

    # Sanity check
    sanity = data['sanity_check']
    status = sanity.get('status', 'unknown')
    passed = sanity.get('checks_passed', 0)
    total = sanity.get('checks_total', 0)

    if status == 'healthy':
        lines.append(f"Sanity Check: [+] HEALTHY ({passed}/{total} passed)")
    elif status == 'warning':
        warnings = sanity.get('warnings', 0)
        lines.append(f"Sanity Check: [!] WARNING ({passed}/{total} passed, {warnings} warnings)")
    elif status == 'error':
        errors = sanity.get('errors', 0)
        lines.append(f"Sanity Check: [x] ERROR ({passed}/{total} passed, {errors} errors)")
    elif status == 'skipped':
        lines.append("Sanity Check: [-] SKIPPED")
    else:
        lines.append(f"Sanity Check: [?] {status.upper()}")

    lines.append("")

    # Pending work
    pending = data['pending_work']
    if pending:
        lines.append("Pending Work:")
        for item in pending:
            lines.append(f"  - {item}")
    else:
        lines.append("Pending Work: None")

    lines.append("")

    # Handoff notes
    if data['handoff_notes']:
        lines.append(f"Handoff Notes: {data['handoff_notes']}")
        lines.append("")

    # Close confirmation
    if data['clean_close']:
        lines.append("Clean close confirmed.")
    else:
        lines.append("Session has issues - review sanity check results.")

    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Wind down protocol for AGET agents (v3.1 template)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. session_state.json - Load to calculate duration
  2. housekeeping - Run sanity check before summary
  3. planning/ - Scan for pending work
  4. sessions/ - Verify exists before writing

Exit codes:
  0 - Clean close (healthy)
  1 - Close with warnings
  2 - Close with errors
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
        help='Agent directory (default: current directory)'
    )
    parser.add_argument(
        '--notes',
        type=str,
        default='',
        help='Handoff notes for next session'
    )
    parser.add_argument(
        '--skip-sanity',
        action='store_true',
        help='Skip sanity check (not recommended)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output to stderr'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='wind_down.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    # L039: Diagnostic timing
    if args.verbose:
        log_diagnostic("Starting wind_down protocol")

    # Find agent root
    agent_path = find_agent_root(args.dir)

    if not agent_path:
        if args.json:
            error = {
                'clean_close': False,
                'errors': ['Could not find .aget/ directory'],
            }
            print(json.dumps(error, indent=2 if args.pretty else None))
        else:
            print("Error: Could not find .aget/ directory", file=sys.stderr)
        return 3

    if args.verbose:
        log_diagnostic(f"Found agent at: {agent_path}")

    # Gather data
    data = get_wind_down_data(
        agent_path,
        skip_sanity=args.skip_sanity,
        handoff_notes=args.notes,
        verbose=args.verbose
    )

    if args.verbose:
        log_diagnostic(f"Data gathered, clean_close={data['clean_close']}")

    # Output
    if args.json:
        print(json.dumps(data, indent=2 if args.pretty else None))
    else:
        print(format_human_output(data))

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    # Exit code based on sanity status
    sanity_status = data['sanity_check'].get('status', 'unknown')
    if sanity_status == 'error':
        return 2
    elif sanity_status == 'warning':
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
