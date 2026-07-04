#!/usr/bin/env python3
"""
AGET Housekeeping Protocol - Generic Template

Perform sanity checks and housekeeping for any AGET agent. Validates
structure, checks for issues, and reports agent health. Designed to
work across CLI agents (Claude Code, Codex CLI, Cursor, etc.).

Implements: CAP-SESSION-002 (Sanity Check Protocol)
Patterns: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

Usage:
    python3 health_check.py                    # Human-readable output
    python3 health_check.py --json             # JSON output
    python3 health_check.py --json --pretty    # Pretty-printed JSON
    python3 health_check.py --dir /path/agent  # Run on specific agent
    python3 health_check.py --fix              # Attempt auto-fixes

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

Author: aget-framework (canonical template)
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import re
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

    # SC-011: Use correct SESSION_*.md convention with legacy fallback
    session_files = list(sessions_dir.glob('SESSION_*.md'))
    if not session_files:
        session_files = list(sessions_dir.glob('session_*.md'))  # legacy fallback
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


def check_duplicate_ldoc_ids(agent_path: Path) -> CheckResult:
    """L131: Detect duplicate L-doc IDs (two distinct lessons sharing one L###).

    Presence/count checks cannot catch ID collisions. This check CAN fail on a
    real, independently-detectable defect — the test L131/L671 demand of every
    health check ("what real failure turns this RED?").
    """
    evolution_dir = agent_path / '.aget' / 'evolution'
    if not evolution_dir.is_dir():
        return CheckResult("duplicate_ldoc_ids", True,
                           "No evolution/ directory", "info")

    seen: Dict[str, int] = {}
    for f in evolution_dir.glob('L*.md'):
        m = re.match(r'(L\d+)_', f.name)
        if m:
            seen[m.group(1)] = seen.get(m.group(1), 0) + 1

    dups = sorted(k for k, v in seen.items() if v > 1)
    if dups:
        return CheckResult(
            name="duplicate_ldoc_ids",
            passed=False,
            message=(f"{len(dups)} duplicate L-doc ID(s): {', '.join(dups)} "
                     "(two lessons share one ID; renumber per L131)"),
            severity="warning"
        )
    return CheckResult(
        name="duplicate_ldoc_ids",
        passed=True,
        message=f"{len(seen)} unique L-doc IDs, no collisions"
    )


def check_config_size(agent_path: Path) -> CheckResult:
    """L146: AGENTS.md must stay under the 40k hard limit (30k recommended)."""
    agents_md = agent_path / 'AGENTS.md'
    if not agents_md.exists():
        return CheckResult("config_size", True, "No AGENTS.md", "info")

    size = agents_md.stat().st_size
    if size > 40000:
        return CheckResult(
            name="config_size",
            passed=False,
            message=f"AGENTS.md {size} bytes exceeds 40k hard limit (L146)",
            severity="error"
        )
    if size > 30000:
        return CheckResult(
            name="config_size",
            passed=False,
            message=(f"AGENTS.md {size} bytes over 30k recommended (L146); "
                     "extract content to .aget/docs/"),
            severity="warning"
        )
    return CheckResult(
        name="config_size",
        passed=True,
        message=f"AGENTS.md {size} bytes (under 30k)"
    )


# =============================================================================
# Main Protocol
# =============================================================================

# D71-STRUCTURAL skills the agent MUST be able to model-invoke (AGENTS.md D71)
D71_STRUCTURAL_SKILLS = (
    "aget-create-project", "aget-close-project",
    "aget-create-initiative", "aget-file-issue",
)


def check_structural_skill_frontmatter(agent_path: Path) -> CheckResult:
    """D71 invariant: no D71-STRUCTURAL skill may carry `disable-model-invocation`.

    The flag blocks model (agent) invocation, but D71 mandates the agent MUST
    invoke these skills; a drifted flag makes D71 unsatisfiable on this instance.
    Ref: gmelli/aget-aget#1489 (SGR remediation F2).
    """
    skills_dir = agent_path / ".claude" / "skills"
    if not skills_dir.is_dir():
        return CheckResult("structural_skill_frontmatter", True,
                           "No .claude/skills/ — not applicable", "info")
    offenders = []
    absent = []
    for skill in D71_STRUCTURAL_SKILLS:
        sk = skills_dir / skill / "SKILL.md"
        if not sk.is_file():
            absent.append(skill)
            continue
        try:
            text = sk.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # inspect only the frontmatter (between the first two '---' markers)
        parts = text.split("---", 2)
        front = parts[1] if text.startswith("---") and len(parts) >= 3 else text
        for line in front.splitlines():
            s = line.strip().replace(" ", "")
            if s.startswith("disable-model-invocation:true"):
                offenders.append(skill)
                break
    if offenders:
        return CheckResult(
            "structural_skill_frontmatter", False,
            "D71 violation: disable-model-invocation on STRUCTURAL skill(s): "
            f"{', '.join(offenders)} — agent cannot model-invoke; remove the flag (ref #1489)",
            severity="error", fixable=True)
    if absent:
        present = len(D71_STRUCTURAL_SKILLS) - len(absent)
        return CheckResult(
            "structural_skill_frontmatter", True,
            f"{present}/{len(D71_STRUCTURAL_SKILLS)} D71-STRUCTURAL skills present + clean; "
            f"ABSENT (not model-invocable; expected if unmigrated phantom, else drift): "
            f"{', '.join(absent)} (ref #1553)",
            severity="warning")
    return CheckResult("structural_skill_frontmatter", True,
                       f"All {len(D71_STRUCTURAL_SKILLS)} D71-STRUCTURAL skills present + "
                       "carry no disable-model-invocation", "info")


def check_permission_accumulation(agent_path: Path) -> CheckResult:
    """L500/L027 (#1516, v3.25 C-25-06): permission-file accumulation gate.

    WARN over 100 permissions or 30KB; ERROR over 200 or 50KB. Previously a
    documented threshold with no failing check — HEALTHY-through (L671).
    """
    worst = None
    for name in ('settings.local.json', 'settings.json'):
        f = agent_path / '.claude' / name
        if not f.exists():
            continue
        size = f.stat().st_size
        try:
            allow = json.loads(f.read_text()).get('permissions', {}).get('allow', [])
        except Exception:
            allow = []
        n = len(allow)
        if n > 200 or size > 50_000:
            return CheckResult('permission_accumulation', False,
                               f'{name}: {n} permissions / {size} bytes exceeds CRITICAL '
                               f'(200 / 50KB) — run SOP_permission_cleanup', severity='error')
        if n > 100 or size > 30_000:
            worst = f'{name}: {n} permissions / {size} bytes over WARN (100 / 30KB)'
    if worst:
        return CheckResult('permission_accumulation', False, worst, severity='warning')
    return CheckResult('permission_accumulation', True, 'within L500 thresholds')


def check_reliance_manifest(agent_path: Path) -> CheckResult:
    """R-BND-001-03 (v3.25, gh#1787): self-attest reliance-manifest conformance.

    Graceful: agents without a manifest (pre-adoption) PASS with an advisory
    message — absence is expected lag, not an error (L601). When both the
    manifest and its validator are present, the validator's verdict is the check.
    """
    manifest = agent_path / '.aget' / 'skill_reliance_manifest.yaml'
    validator = agent_path / 'scripts' / 'check_skill_reliance_manifest.py'
    if not manifest.exists():
        return CheckResult('reliance_manifest', True,
                           'no manifest (pre-adoption — advisory, not required)')
    if not validator.exists():
        return CheckResult('reliance_manifest', False,
                           'manifest present but validator missing (R-BND-001-03 wiring gap)',
                           severity='warning')
    import subprocess
    try:
        r = subprocess.run([sys.executable, str(validator)], capture_output=True,
                           text=True, timeout=15, cwd=str(agent_path))
        ok = r.returncode == 0
        tail = (r.stdout or r.stderr).strip().splitlines()
        msg = tail[-1] if tail else f'exit {r.returncode}'
        return CheckResult('reliance_manifest', ok, msg,
                           severity='info' if ok else 'warning')
    except Exception as e:
        return CheckResult('reliance_manifest', False, f'validator error: {e}',
                           severity='warning')


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
        check_duplicate_ldoc_ids,
        check_config_size,
        check_structural_skill_frontmatter,
        check_reliance_manifest,
        check_permission_accumulation,
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
        version='health_check.py 1.0.0 (AGET v3.1.0)'
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
