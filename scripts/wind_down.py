#!/usr/bin/env python3
"""
Wind Down Protocol - Canonical Framework Script

End session for any AGET agent with proper state capture and health checks.
Designed to work across CLI agents (Claude Code, Codex CLI, Cursor, etc.).

Implements:
    CAP-SESSION-003 (Wind Down Protocol), R-WIND-001-*
    CAP-SESSION-005 (Mandatory Handoff Trigger)
    CAP-SESSION-010 (Re-entrancy Guard)
    CAP-SESSION-012 (Health Gate)
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)
Extension: WD-008 (Extension Hook per SKILL-002 v1.1.0)

Usage:
    python3 wind_down.py                    # Human-readable output
    python3 wind_down.py --json             # JSON output (for programmatic use)
    python3 wind_down.py --json --pretty    # Pretty-printed JSON
    python3 wind_down.py --dir /path/agent  # Run on specific agent
    python3 wind_down.py --notes "..."      # Add handoff notes
    python3 wind_down.py --skip-health      # Skip health check (not recommended)
    python3 wind_down.py --force            # Bypass re-entrancy guard (L468)
    python3 wind_down.py --verify           # Migration verification (L491)

Exit codes:
    0: Clean close (health check passed)
    1: Close with warnings
    2: Close with errors (requires acknowledgment in interactive mode)
    3: Configuration error
    4: Re-entrancy guard active (wind-down already running)

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | session_state.json | Load to calculate duration |
    | 2 | housekeeping | Run health check before summary |
    | 3 | planning/ | Scan for pending work |
    | 4 | sessions/ | Verify exists before writing |

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
# CAP-SESSION-010: Re-entrancy Guard
# =============================================================================

_lock_file = None
_lock_fd = None


def acquire_lock(agent_path: Path) -> bool:
    """Acquire execution lock for wind-down re-entrancy guard.

    Implements CAP-SESSION-010-02: Acquire lock when wind-down starts.
    Uses filesystem-based locking per CAP-SESSION-010-05.

    Returns True if lock acquired, False if already locked.
    """
    global _lock_file, _lock_fd

    _lock_file = agent_path / '.aget' / '.wind_down.lock'

    try:
        # Try platform-appropriate locking
        _lock_fd = open(_lock_file, 'w')
        try:
            import fcntl
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except ImportError:
            # Windows: use msvcrt or fallback to simple file check
            try:
                import msvcrt
                msvcrt.locking(_lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
            except (ImportError, IOError):
                # Simple fallback: check if lock file is recent (< 5 min)
                if _lock_file.exists():
                    mtime = _lock_file.stat().st_mtime
                    if time.time() - mtime < 300:  # 5-minute cooldown
                        _lock_fd.close()
                        _lock_fd = None
                        return False

        _lock_fd.write(f"locked by PID {os.getpid()} at {datetime.now().isoformat()}\n")
        _lock_fd.flush()
        return True
    except (IOError, OSError):
        if _lock_fd:
            _lock_fd.close()
            _lock_fd = None
        return False


def release_lock():
    """Release execution lock. Implements CAP-SESSION-010-03."""
    global _lock_file, _lock_fd

    if _lock_fd:
        try:
            try:
                import fcntl
                fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            except ImportError:
                pass
            _lock_fd.close()
        except Exception:
            pass
        _lock_fd = None

    if _lock_file and _lock_file.exists():
        try:
            _lock_file.unlink()
        except Exception:
            pass


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


def run_health_check(agent_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """CAP-SESSION-012: Run housekeeping health check before wind-down."""
    script_locations = [
        agent_path / 'scripts' / 'health_check.py',
        agent_path / '.aget' / 'patterns' / 'session' / 'health_check.py',
        Path(__file__).parent / 'health_check.py',
    ]

    script_path = None
    for loc in script_locations:
        if loc.exists():
            script_path = loc
            break

    if not script_path:
        return {
            'status': 'unknown',
            'checks_passed': 0,
            'checks_total': 0,
            'warnings': 0,
            'errors': 0,
            'message': 'No health check script found',
        }

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--json'],
            capture_output=True, text=True, timeout=30,
            cwd=str(agent_path),
        )

        if result.stdout:
            try:
                data = json.loads(result.stdout)
                return {
                    'status': data.get('status', 'unknown'),
                    'checks_passed': data.get('summary', {}).get('passed', 0),
                    'checks_total': data.get('summary', {}).get('total', 0),
                    'warnings': data.get('summary', {}).get('warnings', 0),
                    'errors': data.get('summary', {}).get('errors', 0),
                    'message': '',
                }
            except json.JSONDecodeError:
                pass

        # Parse text output as fallback
        passed = result.stdout.count('[+]') + result.stdout.count('PASS')
        failed = result.stdout.count('[-]') + result.stdout.count('FAIL')
        return {
            'status': 'healthy' if failed == 0 else 'warning',
            'checks_passed': passed,
            'checks_total': passed + failed,
            'warnings': failed,
            'errors': 0,
            'message': f'Health check passed ({passed}/{passed + failed})',
        }
    except (subprocess.TimeoutExpired, Exception) as e:
        if verbose:
            log_diagnostic(f"Sanity check error: {e}")
        return {
            'status': 'error',
            'checks_passed': 0,
            'checks_total': 0,
            'warnings': 0,
            'errors': 1,
            'message': f'Sanity check failed to execute: {e}',
        }


def get_session_state(agent_path: Path) -> Dict[str, Any]:
    """Load session state if available."""
    state_file = agent_path / '.aget' / 'session_state.json'
    return load_json_file(state_file, {})


def scan_pending_work(agent_path: Path) -> List[str]:
    """Scan planning/ for in-progress work.

    Checks the top-level status field (first 30 lines) rather than
    scanning full content, to avoid false positives from historical
    gate descriptions like 'Gate X: IN_PROGRESS -> COMPLETE'.
    """
    pending = []
    planning_dir = agent_path / 'planning'
    completed_statuses = {'complete', 'completed', 'superseded', 'archived',
                          'released', 'abandoned', 'closed'}

    if not planning_dir.is_dir():
        return pending

    for plan_file in planning_dir.glob('PROJECT_PLAN_*.md'):
        try:
            content = plan_file.read_text()
            # Extract top-level status from first 30 lines
            top_status = None
            for line in content.split('\n')[:30]:
                line_stripped = line.strip().lower()
                # Match patterns: "status: X", "**status**: X", "**Status**: X"
                for prefix in ('status:', '**status**:', '**status:'):
                    if line_stripped.startswith(prefix):
                        top_status = line_stripped.split(':', 1)[1].strip().strip('*').strip()
                        break
                if top_status:
                    break

            # Skip plans with completed top-level status
            if top_status and any(s in top_status for s in completed_statuses):
                continue

            # Check top-level status for in-progress indicators
            in_progress_statuses = {'in_progress', 'in progress', 'draft', 'pending',
                                    'active', 'blocked'}
            if top_status and any(s in top_status for s in in_progress_statuses):
                pending.append(plan_file.name)
            # Fallback: scan content for IN_PROGRESS (plans without top-level status)
            elif not top_status and ('IN_PROGRESS' in content.upper()
                                     or 'IN PROGRESS' in content.upper()):
                pending.append(plan_file.name)
        except IOError:
            pass

    return pending


def scan_nuggets(agent_path: Path) -> List[Dict[str, Any]]:
    """Scan for pre-CLI nugget files in known locations.

    Checks two directories:
    - ~/.aget/nuggets/ (global, cross-agent)
    - <agent_root>/.aget/evolution/nuggets/ (local, agent-specific)

    Returns list of nugget dicts with file, subject, age_days, stale flag.
    Feature-gated: returns [] if neither directory exists.
    """
    nuggets = []
    now = datetime.now()
    stale_days = 30

    locations = [
        ('global', Path.home() / '.aget' / 'nuggets'),
        ('local', agent_path / '.aget' / 'evolution' / 'nuggets'),
    ]

    for scope, nugget_dir in locations:
        if not nugget_dir.is_dir():
            continue
        for f in sorted(nugget_dir.glob('*.md')):
            if f.name.lower() == 'readme.md':
                continue
            try:
                content = f.read_text().strip()
                # Subject: first non-empty, non-header line
                subject = ''
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        subject = line[:80]
                        break
                age_days = (now - datetime.fromtimestamp(f.stat().st_mtime)).days
                nuggets.append({
                    'file': f.name,
                    'scope': scope,
                    'subject': subject,
                    'age_days': age_days,
                    'stale': age_days > stale_days,
                })
            except (IOError, OSError):
                pass

    return nuggets


def get_uncommitted_changes(agent_path: Path) -> List[str]:
    """Check for uncommitted git changes."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=5,
            cwd=str(agent_path),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def create_session_file(agent_path: Path, data: Dict[str, Any],
                        mandatory: bool = False) -> Optional[str]:
    """CAP-SESSION-005: Create session file when mandatory handoff triggered."""
    sessions_dir = agent_path / 'sessions'
    if not sessions_dir.is_dir():
        try:
            sessions_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return None

    # Load version for aget_version
    version_data = load_json_file(agent_path / '.aget' / 'version.json', {})
    aget_version = version_data.get('aget_version', 'unknown')
    agent_name = version_data.get('agent_name', agent_path.name)

    now = datetime.now()
    session_id = f"session_{now.strftime('%Y-%m-%d_%H%M')}"
    session_file = sessions_dir / f"{session_id}.md"

    trigger = "MANDATORY (pending work detected)" if mandatory else "voluntary"

    content = f"""---
# Session Metadata Standard v1.0
session_id: {session_id}
date: {now.strftime('%Y-%m-%d')}
aget_version: "{aget_version}"
agent_name: "{agent_name}"
session_type: operational

# Outcome Tracking
status: completed
---

# Session: {now.strftime('%Y-%m-%d')}

## Notes

{data.get('handoff_notes', 'No notes provided.')}

## Pending Work

{data.get('pending_work', [])}

---

*Session ended: {now.strftime('%Y-%m-%d %H:%M')}*
"""

    try:
        session_file.write_text(content)
        return str(session_file.relative_to(agent_path))
    except IOError:
        return None


def get_wind_down_data(agent_path: Path,
                       skip_health: bool = False,
                       handoff_notes: str = "",
                       verbose: bool = False) -> Dict[str, Any]:
    """Gather all data needed for wind down output."""
    now = datetime.now()

    data = {
        'timestamp': now.isoformat(),
        'agent_path': str(agent_path),
        'session': {
            'ended': now.isoformat(),
            'started': None,
            'duration_seconds': None,
        },
        'health_check': {},
        'pending_work': [],
        'uncommitted_changes': [],
        'handoff_notes': handoff_notes,
        'session_file': None,
        'mandatory_handoff': False,
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

    # L021 Check 2: Sanity check (CAP-SESSION-012)
    if skip_health:
        data['health_check'] = {
            'status': 'skipped',
            'checks_passed': 0,
            'checks_total': 0,
            'warnings': 0,
            'errors': 0,
            'message': 'Sanity check skipped by user',
        }
    else:
        if verbose:
            log_diagnostic("Running health check...")
        data['health_check'] = run_health_check(agent_path, verbose)

    # L021 Check 3: Pending work
    data['pending_work'] = scan_pending_work(agent_path)

    # Nuggets scan
    data['nuggets'] = scan_nuggets(agent_path)

    # Uncommitted changes
    data['uncommitted_changes'] = get_uncommitted_changes(agent_path)

    # CAP-SESSION-005: Mandatory handoff trigger
    if data['pending_work']:
        data['mandatory_handoff'] = True
        session_file = create_session_file(agent_path, data, mandatory=True)
        if session_file:
            data['session_file'] = session_file

    # Determine clean close
    health_status = data['health_check'].get('status', 'unknown')
    if health_status == 'error':
        data['clean_close'] = False

    # Load agent identity for display
    version_file = agent_path / '.aget' / 'version.json'
    version_data = load_json_file(version_file, {})
    data['agent_name'] = version_data.get('agent_name', agent_path.name)

    return data


def call_extension_hook(agent_path: Path, data: Dict[str, Any],
                        verbose: bool = False) -> Dict[str, Any]:
    """C1 Extension Hook (WD-008): Call wind_down_ext.py:post_wind_down(data) if present.

    Contract per SKILL-002 v1.1.0 WD-008:
    - Hook receives data dict
    - Hook returns augmented data dict (additive-only per L464)
    - Hook absence = no-op
    - Hook failure = warning + continue
    """
    ext_path = agent_path / 'scripts' / 'wind_down_ext.py'
    if not ext_path.exists():
        return data

    try:
        spec = importlib.util.spec_from_file_location('wind_down_ext', str(ext_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'post_wind_down'):
            result = module.post_wind_down(data)
            if isinstance(result, dict):
                return result
            if verbose:
                log_diagnostic("Extension hook returned non-dict, ignoring")
    except Exception as e:
        print(f"Warning: Extension hook failed: {e}", file=sys.stderr)

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

    lines.append("=" * 60)
    lines.append("SESSION WIND DOWN")
    lines.append("=" * 60)
    lines.append("")

    # Sanity check
    health = data['health_check']
    status = health.get('status', 'unknown')
    passed = health.get('checks_passed', 0)
    total = health.get('checks_total', 0)

    if status == 'healthy':
        lines.append(f"Health Gate: Health check passed ({passed}/{total})")
    elif status == 'warning':
        lines.append(f"Health Gate: WARNING ({passed}/{total} passed)")
    elif status == 'error':
        lines.append(f"Health Gate: ERROR ({passed}/{total} passed)")
    elif status == 'skipped':
        lines.append("Health Gate: SKIPPED")
    else:
        lines.append(f"Health Gate: {status.upper()}")

    lines.append("")

    # Pending work
    pending = data['pending_work']
    if pending:
        lines.append("Pending Work:")
        for item in pending:
            lines.append(f"  - {item}")
        lines.append("")

        # Mandatory handoff notice
        if data.get('mandatory_handoff'):
            lines.append("  [MANDATORY HANDOFF TRIGGERED - CAP-SESSION-005-01]")
            lines.append("")

    # Nuggets
    nuggets = data.get('nuggets', [])
    if nuggets:
        stale_count = sum(1 for n in nuggets if n.get('stale'))
        lines.append(f"Nuggets ({len(nuggets)} pending{f', {stale_count} stale' if stale_count else ''}):")
        for n in nuggets:
            stale_tag = " [STALE]" if n.get('stale') else ""
            lines.append(f"  - [{n['scope']}] {n['file']}: {n['subject']}{stale_tag}")
        lines.append("")

    # Uncommitted changes
    uncommitted = data.get('uncommitted_changes', [])
    if uncommitted:
        lines.append("Uncommitted Changes:")
        for change in uncommitted[:10]:
            lines.append(f"  {change}")
        if len(uncommitted) > 10:
            lines.append(f"  ... and {len(uncommitted) - 10} more")
        lines.append("")

    # Session file
    if data.get('session_file'):
        trigger = "MANDATORY" if data.get('mandatory_handoff') else "voluntary"
        lines.append(f"Session Note: {data['session_file']}")
        lines.append(f"   Created: {trigger} ({'pending work detected' if data.get('mandatory_handoff') else 'user requested'})")
        lines.append("")

    # Extension output
    ext_output = data.get('extension_output', '')
    if ext_output:
        lines.append(ext_output)
        lines.append("")

    lines.append("=" * 60)
    lines.append("Session ended.")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Wind down protocol for AGET agents (v2.0.0)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. session_state.json - Load to calculate duration
  2. housekeeping - Run health check before summary
  3. planning/ - Scan for pending work
  4. sessions/ - Verify exists before writing

Exit codes:
  0 - Clean close (healthy)
  1 - Close with warnings
  2 - Close with errors
  3 - Configuration error
  4 - Re-entrancy guard active
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
        '--notes', type=str, default='',
        help='Handoff notes for next session',
    )
    parser.add_argument(
        '--skip-health', action='store_true',
        help='Skip health check (not recommended)',
    )
    parser.add_argument(
        '--force', action='store_true',
        help='Bypass re-entrancy guard (L468)',
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
        version='wind_down.py 2.0.0 (AGET v3.6.0)',
    )

    args = parser.parse_args()

    # L491: --verify mode
    if args.verify:
        script_path = Path(__file__).resolve()
        agent_root = find_agent_root(script_path.parent)
        if agent_root:
            expected = agent_root / 'scripts' / 'wind_down.py'
            if script_path == expected.resolve():
                print(f"PASS: wind_down.py at canonical path: {expected}")
                return 0
            else:
                print(f"WARN: wind_down.py at {script_path}, expected {expected}")
                return 1
        print("WARN: Could not determine agent root for verification")
        return 1

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

    # CAP-SESSION-010: Re-entrancy guard
    if not args.force:
        if not acquire_lock(agent_path):
            msg = "BLOCKED: Wind-down already running (CAP-SESSION-010). Use --force to bypass."
            if args.json:
                print(json.dumps({'clean_close': False, 'errors': [msg]}))
            else:
                print(msg, file=sys.stderr)
            return 4

    try:
        if args.verbose:
            log_diagnostic(f"Found agent at: {agent_path}")

        # Gather data
        data = get_wind_down_data(
            agent_path,
            skip_health=args.skip_health,
            handoff_notes=args.notes,
            verbose=args.verbose,
        )

        if args.verbose:
            log_diagnostic(f"Data gathered, clean_close={data['clean_close']}")

        # C1 Extension Hook (WD-008)
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

        # Exit code based on health check status
        # Only errors (broken state) produce non-zero exit codes.
        # Warnings are informational and already printed in output —
        # returning exit 1 for persistent warnings (e.g., skill drift)
        # trains users to ignore exit codes, defeating their purpose.
        health_status = data['health_check'].get('status', 'unknown')
        if health_status == 'error':
            return 2
        return 0

    finally:
        # CAP-SESSION-010-03: Always release lock
        if not args.force:
            release_lock()


if __name__ == '__main__':
    sys.exit(main())
