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
    'show_pending_work': True,  # gh#1285: surface prior session-note Pending Work
    'show_release_currency': True,  # gh#1833: release-currency signal (v3.26, C-26-01)
    'release_currency_timeout': 5,  # seconds; fail-soft budget for the network check
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
    """Get git status for the agent directory.

    Returns the uncommitted-file list (`changes`), not just a clean/dirty
    flag, so the agent reconciles the inherited working tree at boot rather
    than glossing "(dirty)" and later asserting "nothing changed" without
    having established a baseline. (Reconcile-dirty-tree-at-boot; promotes a
    one-off session critique into the script per L467 single-channel gap.)
    """
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
        if result2.returncode == 0:
            changes = [ln for ln in result2.stdout.splitlines() if ln.strip()]
            clean = len(changes) == 0
        else:
            changes = []
            clean = None

        return {'branch': branch, 'clean': clean, 'changes': changes}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {'branch': 'unknown', 'clean': None, 'changes': []}


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


def get_release_currency(own_version: str, timeout: int = 5) -> Dict[str, Any]:
    """Release-currency signal (gh#1833, v3.26 C-26-01; L467 Channel-5).

    Compares local aget_version against the latest public framework release
    tag so target-misresolution (agent plans against N-1 because no currency
    signal reached its field of view) is caught at session start.

    Fail-soft (ADR-004): any failure — no gh, offline, timeout, auth — returns
    status 'unknown' and MUST NOT block or slow wake-up beyond the timeout.
    Reference implementation: main-supervisor _release_banner (accepted at
    source, natural A/B evidence per #1833 p1 grant).
    """
    result: Dict[str, Any] = {'status': 'unknown', 'latest': None}
    try:
        # gh api (plain REST) — NOT `gh release view`: the latter blocks
        # indefinitely under a non-tty python subprocess in field testing
        # (F-REL326-G1-1, 2026-07-10), which silently defeats the signal
        # behind the fail-soft timeout. `gh api` returns in <1s.
        cmd = ["gh", "api", "repos/aget-framework/aget/releases/latest",
               "-q", ".tag_name"]
        latest = ""
        for _attempt in range(2):  # single bounded retry — transient blips
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=timeout, stdin=subprocess.DEVNULL)
            if proc.returncode == 0:
                latest = proc.stdout.strip().lstrip("v")
                if latest:
                    break
        if latest:
            result['latest'] = latest
            result['status'] = ('current' if latest == own_version
                                else 'behind')
    except Exception:
        pass
    return result


def compute_active_agents_from_fleet_state(agent_path: Path) -> Optional[Dict[str, Any]]:
    """Read `.aget/fleet/FLEET_STATE.yaml` and return live filesystem-based active count per gh#1288.

    Closes structural-not-discipline gap (L644 substrate; L648 cross-instance state coherence):
    fleet-count surfacing at wake-up SHOULD prefer FLEET_STATE.yaml live read over MEMORY-cached
    parrot or metadata-asserted numbers. Detects drift between filesystem reality
    (sum of agents with status==active) and asserted metadata.active_agents.

    Returns None if no FLEET_STATE.yaml found at agent_path (most agents don't have one;
    only supervisor-class agents). Returns dict with keys:
        - filesystem_count: int — count of agents with status==active across all portfolios
        - metadata_count: Optional[int] — value of metadata.active_agents (None if absent)
        - drift: bool — True if filesystem_count != metadata_count
        - drift_warning: Optional[str] — human-readable warning if drift detected
        - portfolios: list of portfolio names with active counts

    Designed to be called from extension hooks (`scripts/wake_up_ext.py`) that surface
    fleet counts; framework-canonical helper, instance artifact opt-in. PyYAML dependency
    fails gracefully (returns None) if not installed.
    """
    fleet_state_path = agent_path / '.aget' / 'fleet' / 'FLEET_STATE.yaml'
    if not fleet_state_path.exists():
        return None
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return None
    try:
        with open(fleet_state_path) as f:
            data = yaml.safe_load(f) or {}
    except (yaml.YAMLError, IOError):
        return None

    fleet = data.get('fleet') or {}
    metadata = data.get('metadata') or {}

    portfolios = []
    filesystem_count = 0
    for pf_name, pf_data in fleet.items():
        if not isinstance(pf_data, dict):
            continue
        agents = pf_data.get('agents') or []
        pf_active = sum(1 for a in agents if isinstance(a, dict) and a.get('status') == 'active')
        portfolios.append({'name': pf_name, 'active': pf_active})
        filesystem_count += pf_active

    metadata_count = metadata.get('active_agents')
    drift = (metadata_count is not None) and (metadata_count != filesystem_count)
    drift_warning = None
    if drift:
        drift_warning = (
            f"FLEET_STATE drift: metadata.active_agents={metadata_count} "
            f"!= filesystem count={filesystem_count}. Filesystem wins per L644 + AGENTS.md precedence rule."
        )

    return {
        'filesystem_count': filesystem_count,
        'metadata_count': metadata_count,
        'drift': drift,
        'drift_warning': drift_warning,
        'portfolios': portfolios,
    }


def get_pending_work(agent_path: Path, max_items: int = 10) -> Dict[str, Any]:
    """Surface most recent session note's `## Pending Work` section per gh#1285.

    Closes structural-not-discipline gap (L490/L563): fresh sessions inherit
    MEMORY + plan but historically did NOT auto-read prior session-note's
    Pending Work, creating a discovery lottery.

    Returns dict with keys:
        - source: relative path of session file (or None if not found)
        - items: list of bullet lines under `## Pending Work` header
        - truncated: bool — True if more items existed than max_items
    """
    result = {'source': None, 'items': [], 'truncated': False}
    sessions_dir = agent_path / 'sessions'
    if not sessions_dir.is_dir():
        return result
    session_files = sorted(
        sessions_dir.glob('session_*.md'),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not session_files:
        return result
    most_recent = session_files[0]
    try:
        result['source'] = str(most_recent.relative_to(agent_path))
    except ValueError:
        result['source'] = str(most_recent)
    try:
        text = most_recent.read_text(encoding='utf-8')
    except Exception:
        return result

    in_section = False
    items: list = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            if in_section:
                break
            if 'Pending Work' in stripped:
                in_section = True
            continue
        if in_section:
            if stripped.startswith(('- ', '* ', '+ ')):
                items.append(stripped[2:].strip())
            elif stripped and not stripped.startswith('#') and not items:
                items.append(stripped)

    if len(items) > max_items:
        result['truncated'] = True
        items = items[:max_items]
    result['items'] = items
    return result


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

    # Pending Work surfacing (gh#1285 — structural-not-discipline)
    if data['config'].get('show_pending_work', True):
        data['pending_work'] = get_pending_work(agent_path)

    # Release-currency signal (gh#1833, v3.26 C-26-01) — fail-soft, config-gated
    if data['config'].get('show_release_currency', True):
        data['release_currency'] = get_release_currency(
            data['version']['aget_version'],
            timeout=data['config'].get('release_currency_timeout', 5))

    # R-BND-001-03 self-attestation (v3.25, gh#1787): when the reliance manifest
    # and its validator are both present, attest conformance at wake-up. Absence
    # is silent (pre-adoption agents; L601 expected lag, not an error).
    manifest = agent_path / '.aget' / 'skill_reliance_manifest.yaml'
    validator = agent_path / 'scripts' / 'check_skill_reliance_manifest.py'
    if manifest.exists() and validator.exists():
        import subprocess as _sp
        try:
            r = _sp.run([sys.executable, str(validator)], capture_output=True,
                        text=True, timeout=15, cwd=str(agent_path))
            tail = (r.stdout or r.stderr).strip().splitlines()
            data['reliance_attestation'] = {
                'ok': r.returncode == 0,
                'summary': tail[-1] if tail else f'exit {r.returncode}',
            }
        except Exception as e:
            data['reliance_attestation'] = {'ok': False, 'summary': f'validator error: {e}'}

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

        # Reconcile-dirty-tree-at-boot: surface the actual uncommitted files
        # so the inherited tree is reconciled (commit/stash/explain), not
        # glossed, before any "nothing changed" claim. (L467 structural fix.)
        changes = git.get('changes') or []
        if changes:
            max_show = config.get('git_dirty_max_files', 10)
            lines.append(
                f"  ⚠ Uncommitted ({len(changes)}) — reconcile before "
                f"claiming a clean baseline:"
            )
            for ln in changes[:max_show]:
                lines.append(f"    {ln}")
            if len(changes) > max_show:
                lines.append(f"    … +{len(changes) - max_show} more")

    # Structure (toggle: show_structure)
    if config.get('show_structure', False):
        optional = data.get('structure', {}).get('optional', {})
        present = [d for d, exists in optional.items() if exists]
        if present:
            lines.append(f"Directories: {', '.join(present)}")

    # Release currency (toggle: show_release_currency; gh#1833 v3.26 C-26-01).
    # 'behind' → actionable one-liner (reference-impl wording incl. the
    # DEPLOYMENT_SPEC guard); 'current'/'unknown' → silent (ADR-004 degradation).
    if config.get('show_release_currency', True) and 'release_currency' in data:
        rc = data['release_currency']
        if rc.get('status') == 'behind':
            own = data['version']['aget_version']
            lines.append(f"Framework: v{own} local · v{rc['latest']} latest — "
                         "verify DEPLOYMENT_SPEC before upgrading")

    # Calendar (toggle: show_calendar, CAP-SESSION-011)
    if config.get('show_calendar', True) and 'calendar' in data:
        cal = data['calendar']
        lines.append(f"Date: {cal['date']} ({cal['day']})")
        if cal.get('in_release_window'):
            lines.append(f"Release Window: {cal['release_window']}")

    # Pending Work surfacing (toggle: show_pending_work, gh#1285)
    if config.get('show_pending_work', True) and 'pending_work' in data:
        pw = data['pending_work']
        if pw.get('items'):
            lines.append("")
            lines.append(f"Pending Work (from {pw.get('source', 'prior session')}):")
            for item in pw['items']:
                lines.append(f"  - {item}")
            if pw.get('truncated'):
                lines.append("  ... (truncated; see session note for full list)")

    lines.append("")

    # R-BND-001-03 self-attestation line (v3.25, gh#1787)
    ra = data.get('reliance_attestation')
    if ra:
        mark = "OK" if ra.get('ok') else "ATTENTION"
        lines.append(f"Reliance self-attestation: {mark} — {ra.get('summary', '')}")
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
