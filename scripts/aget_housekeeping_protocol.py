#!/usr/bin/env python3
"""
AGET Housekeeping Protocol - Generic Template

Perform sanity checks and housekeeping for any AGET agent. Validates
structure, checks for issues, and reports agent health. Designed to
work across CLI agents (Claude Code, Codex CLI, Cursor, etc.).

Implements: CAP-SESSION-002 (Sanity Check Protocol)
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 aget_housekeeping_protocol.py                    # Human-readable output
    python3 aget_housekeeping_protocol.py --json             # JSON output
    python3 aget_housekeeping_protocol.py --json --pretty    # Pretty-printed JSON
    python3 aget_housekeeping_protocol.py --dir /path/agent  # Run on specific agent
    python3 aget_housekeeping_protocol.py --fix              # Attempt auto-fixes

Exit codes:
    0: All checks passed
    1: Warnings found (non-blocking)
    2: Errors found (blocking issues)
    3: Configuration/runtime error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | .aget/ dir | Verify exists before reading |
    | 2 | version.json | Load before checking version |
    | 3 | identity.json | Load before checking identity |
    | 4 | governance/ | Check before verifying files |
    | 5 | evolution/ | Check before counting L-docs |

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
# Check Result
# =============================================================================

class CheckResult:
    """Result of a single check."""

    def __init__(self, name: str, passed: bool, message: str = "",
                 severity: str = "info", fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.severity = severity  # info, warning, error
        self.fixable = fixable

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'passed': self.passed,
            'message': self.message,
            'severity': self.severity,
            'fixable': self.fixable,
        }


# =============================================================================
# Checks
# =============================================================================

def check_aget_directory(agent_path: Path) -> CheckResult:
    """L021 Check 1: Verify .aget/ directory exists."""
    exists = (agent_path / '.aget').is_dir()
    return CheckResult(
        name=".aget_directory",
        passed=exists,
        message="" if exists else ".aget/ directory not found",
        severity="error" if not exists else "info"
    )


def check_version_json(agent_path: Path) -> CheckResult:
    """L021 Check 2: Verify version.json exists and is valid."""
    version_file = agent_path / '.aget' / 'version.json'

    if not version_file.exists():
        return CheckResult(
            name="version_json",
            passed=False,
            message="version.json not found",
            severity="error"
        )

    try:
        with open(version_file) as f:
            data = json.load(f)

        if 'aget_version' not in data:
            return CheckResult(
                name="version_json",
                passed=False,
                message="version.json missing aget_version field",
                severity="warning",
                fixable=True
            )

        return CheckResult(
            name="version_json",
            passed=True,
            message=f"v{data.get('aget_version', 'unknown')}"
        )

    except json.JSONDecodeError as e:
        return CheckResult(
            name="version_json",
            passed=False,
            message=f"Invalid JSON: {e}",
            severity="error"
        )


def check_identity_json(agent_path: Path) -> CheckResult:
    """L021 Check 3: Verify identity.json exists and has north_star."""
    identity_file = agent_path / '.aget' / 'identity.json'

    if not identity_file.exists():
        return CheckResult(
            name="identity_json",
            passed=False,
            message="identity.json not found (recommended for v3.0)",
            severity="warning",
            fixable=True
        )

    try:
        with open(identity_file) as f:
            data = json.load(f)

        if 'north_star' not in data:
            return CheckResult(
                name="identity_json",
                passed=False,
                message="identity.json missing north_star field",
                severity="warning"
            )

        return CheckResult(
            name="identity_json",
            passed=True,
            message="north_star defined"
        )

    except json.JSONDecodeError:
        return CheckResult(
            name="identity_json",
            passed=False,
            message="identity.json invalid JSON",
            severity="error"
        )


def check_governance_directory(agent_path: Path) -> CheckResult:
    """L021 Check 4: Verify governance/ directory and required files."""
    gov_dir = agent_path / 'governance'

    if not gov_dir.is_dir():
        return CheckResult(
            name="governance_directory",
            passed=False,
            message="governance/ directory not found (recommended for v3.0)",
            severity="warning",
            fixable=True
        )

    required_files = ['CHARTER.md', 'MISSION.md', 'SCOPE_BOUNDARIES.md']
    missing = [f for f in required_files if not (gov_dir / f).exists()]

    if missing:
        return CheckResult(
            name="governance_directory",
            passed=False,
            message=f"Missing: {', '.join(missing)}",
            severity="warning",
            fixable=True
        )

    return CheckResult(
        name="governance_directory",
        passed=True,
        message=f"{len(required_files)} files present"
    )


def check_evolution_directory(agent_path: Path) -> CheckResult:
    """L021 Check 5: Check evolution/ for L-doc count and index."""
    evolution_dir = agent_path / '.aget' / 'evolution'

    if not evolution_dir.is_dir():
        return CheckResult(
            name="evolution_directory",
            passed=True,
            message="No evolution/ directory (OK for new agents)"
        )

    l_docs = list(evolution_dir.glob('L*.md'))
    count = len(l_docs)

    # Check if index is needed (>50 L-docs)
    if count > 50:
        index_file = evolution_dir / 'index.json'
        if not index_file.exists():
            return CheckResult(
                name="evolution_directory",
                passed=False,
                message=f"{count} L-docs but no index.json (required >50)",
                severity="warning",
                fixable=True
            )

    return CheckResult(
        name="evolution_directory",
        passed=True,
        message=f"{count} L-docs"
    )


def check_5d_structure(agent_path: Path) -> CheckResult:
    """Check 5D directory structure (v3.0 requirement)."""
    dimensions = ['persona', 'memory', 'reasoning', 'skills', 'context']
    aget_dir = agent_path / '.aget'

    present = [d for d in dimensions if (aget_dir / d).is_dir()]
    missing = [d for d in dimensions if d not in present]

    if not missing:
        return CheckResult(
            name="5d_structure",
            passed=True,
            message="5/5 dimensions present"
        )

    if len(present) == 0:
        return CheckResult(
            name="5d_structure",
            passed=False,
            message="No 5D directories (pre-v3.0 structure)",
            severity="warning"
        )

    return CheckResult(
        name="5d_structure",
        passed=False,
        message=f"Missing: {', '.join(missing)}",
        severity="warning",
        fixable=True
    )


def check_sessions_directory(agent_path: Path) -> CheckResult:
    """Check sessions/ directory exists."""
    sessions_dir = agent_path / 'sessions'

    if not sessions_dir.is_dir():
        return CheckResult(
            name="sessions_directory",
            passed=False,
            message="sessions/ directory not found",
            severity="warning",
            fixable=True
        )

    session_files = list(sessions_dir.glob('session_*.md'))
    return CheckResult(
        name="sessions_directory",
        passed=True,
        message=f"{len(session_files)} session files"
    )


def check_planning_directory(agent_path: Path) -> CheckResult:
    """Check planning/ directory exists."""
    planning_dir = agent_path / 'planning'

    if not planning_dir.is_dir():
        return CheckResult(
            name="planning_directory",
            passed=False,
            message="planning/ directory not found",
            severity="warning",
            fixable=True
        )

    plans = list(planning_dir.glob('PROJECT_PLAN_*.md'))
    return CheckResult(
        name="planning_directory",
        passed=True,
        message=f"{len(plans)} PROJECT_PLANs"
    )


# =============================================================================
# Main Protocol
# =============================================================================

def run_housekeeping(agent_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run all housekeeping checks.

    Returns structured dict suitable for JSON or human output.
    """
    data = {
        'timestamp': datetime.now().isoformat(),
        'agent_path': str(agent_path),
        'checks': [],
        'summary': {
            'total': 0,
            'passed': 0,
            'warnings': 0,
            'errors': 0,
            'fixable': 0,
        },
        'status': 'unknown',
    }

    # Run all checks
    checks = [
        check_aget_directory,
        check_version_json,
        check_identity_json,
        check_governance_directory,
        check_evolution_directory,
        check_5d_structure,
        check_sessions_directory,
        check_planning_directory,
    ]

    for check_fn in checks:
        if verbose:
            log_diagnostic(f"Running {check_fn.__name__}")

        result = check_fn(agent_path)
        data['checks'].append(result.to_dict())

        data['summary']['total'] += 1
        if result.passed:
            data['summary']['passed'] += 1
        elif result.severity == 'warning':
            data['summary']['warnings'] += 1
        elif result.severity == 'error':
            data['summary']['errors'] += 1

        if result.fixable:
            data['summary']['fixable'] += 1

    # Determine status
    if data['summary']['errors'] > 0:
        data['status'] = 'error'
    elif data['summary']['warnings'] > 0:
        data['status'] = 'warning'
    else:
        data['status'] = 'healthy'

    return data


def format_human_output(data: Dict[str, Any]) -> str:
    """Format data for human-readable output."""
    lines = []

    lines.append("\n=== AGET Housekeeping Report ===\n")

    # Summary
    summary = data['summary']
    status = data['status']

    status_symbol = {'healthy': '+', 'warning': '!', 'error': 'x'}.get(status, '?')
    lines.append(f"Status: [{status_symbol}] {status.upper()}")
    lines.append(f"Checks: {summary['passed']}/{summary['total']} passed")

    if summary['warnings']:
        lines.append(f"Warnings: {summary['warnings']}")
    if summary['errors']:
        lines.append(f"Errors: {summary['errors']}")
    if summary['fixable']:
        lines.append(f"Fixable: {summary['fixable']} (run with --fix)")

    lines.append("")
    lines.append("Checks:")

    # Individual checks
    for check in data['checks']:
        symbol = '+' if check['passed'] else ('!' if check['severity'] == 'warning' else 'x')
        name = check['name'].replace('_', ' ').title()
        message = check['message']

        if check['passed']:
            lines.append(f"  [{symbol}] {name}: {message}")
        else:
            lines.append(f"  [{symbol}] {name}: {message}")

    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='AGET Housekeeping Protocol (v3.1 template)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L021 Verification Table:
  1. .aget/ dir - Verify exists before reading
  2. version.json - Load before checking version
  3. identity.json - Load before checking identity
  4. governance/ - Check before verifying files
  5. evolution/ - Check before counting L-docs

Exit codes:
  0 - All checks passed
  1 - Warnings found
  2 - Errors found
  3 - Runtime error
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
        '--fix',
        action='store_true',
        help='Attempt to fix issues (not implemented yet)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output to stderr'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='aget_housekeeping_protocol.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    # L039: Diagnostic timing
    if args.verbose:
        log_diagnostic("Starting housekeeping protocol")

    # Find agent root
    if args.dir:
        agent_path = Path(args.dir).resolve()
    else:
        agent_path = Path.cwd()

    # Check .aget/ exists
    if not (agent_path / '.aget').is_dir():
        if args.json:
            error = {
                'status': 'error',
                'errors': ['Could not find .aget/ directory'],
            }
            print(json.dumps(error, indent=2 if args.pretty else None))
        else:
            print("Error: Could not find .aget/ directory", file=sys.stderr)
        return 3

    if args.verbose:
        log_diagnostic(f"Found agent at: {agent_path}")

    # Run housekeeping
    data = run_housekeeping(agent_path, verbose=args.verbose)

    if args.verbose:
        log_diagnostic(f"Housekeeping complete, status={data['status']}")

    # Output
    if args.json:
        print(json.dumps(data, indent=2 if args.pretty else None))
    else:
        print(format_human_output(data))

    if args.verbose:
        elapsed = (time.time() - _start_time) * 1000
        log_diagnostic(f"Complete in {elapsed:.0f}ms")

    # Exit code based on status
    if data['status'] == 'error':
        return 2
    elif data['status'] == 'warning':
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
