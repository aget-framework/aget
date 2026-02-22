#!/usr/bin/env python3
"""
health_logger.py - Healthcheck Result Persistence

Per CAP-REL-025: Appends healthcheck results to `.aget/logs/health_log.jsonl`.
Enables health trend analysis across sessions and regression detection.

Usage:
    python3 health_logger.py                         # Run healthcheck and log
    python3 health_logger.py --trend                 # Show trend vs prior session
    python3 health_logger.py --json                  # JSON output
    python3 health_logger.py --test                  # Self-test

Specification: AGET_RELEASE_SPEC.md CAP-REL-025
Source: L605 (Release Observability Gap)

Exit Codes:
    0: Success
    1: Failure or healthcheck errors
    3: Configuration error
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_agent_root() -> Path:
    """Get the agent root directory."""
    current = Path(__file__).resolve()
    if current.parent.name == 'scripts':
        return current.parent.parent
    return current.parent.parent.parent.parent


def run_healthcheck(agent_root: Path) -> dict:
    """Run aget_housekeeping_protocol.py and parse results."""
    # Try canonical location first, then legacy
    script_paths = [
        agent_root / 'scripts' / 'aget_housekeeping_protocol.py',
        agent_root / '.aget' / 'patterns' / 'session' / 'aget_housekeeping_protocol.py',
    ]

    script_path = None
    for sp in script_paths:
        if sp.is_file():
            script_path = sp
            break

    if not script_path:
        return {'error': 'healthcheck script not found', 'checks': []}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--json'],
            capture_output=True, text=True, timeout=30,
            cwd=str(agent_root)
        )

        if result.returncode in (0, 1) and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                return data
            except json.JSONDecodeError:
                pass

        # Fallback: parse text output
        checks = []
        for line in (result.stdout + result.stderr).split('\n'):
            line = line.strip()
            if not line:
                continue
            status = 'OK'
            if '❌' in line or 'FAIL' in line or 'CRITICAL' in line:
                status = 'CRITICAL'
            elif '⚠' in line or 'WARN' in line:
                status = 'WARN'
            elif '✅' in line or 'PASS' in line or 'OK' in line:
                status = 'OK'
            else:
                continue
            checks.append({'name': line[:60], 'status': status, 'details': line})

        return {'checks': checks}

    except subprocess.TimeoutExpired:
        return {'error': 'healthcheck timed out', 'checks': []}
    except Exception as e:
        return {'error': str(e), 'checks': []}


def create_health_record(healthcheck_data: dict, session_id: str = None) -> dict:
    """Create a Health_Log record (CAP-REL-025-01, 025-02)."""
    if session_id is None:
        session_id = f"session_{datetime.now().strftime('%Y-%m-%d_%H%M')}"

    checks = healthcheck_data.get('checks', [])

    # Normalize checks
    normalized = []
    for check in checks:
        if isinstance(check, dict):
            normalized.append({
                'name': check.get('name', 'unknown'),
                'status': check.get('status', 'unknown'),
                'details': check.get('details', ''),
            })

    ok_count = sum(1 for c in normalized if c['status'] == 'OK')
    warn_count = sum(1 for c in normalized if c['status'] == 'WARN')
    critical_count = sum(1 for c in normalized if c['status'] == 'CRITICAL')

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'session_id': session_id,
        'checks': normalized,
        'summary': {
            'ok': ok_count,
            'warn': warn_count,
            'critical': critical_count,
        },
    }


def get_log_path(agent_root: Path = None) -> Path:
    """Get the health log path."""
    if agent_root is None:
        agent_root = Path.cwd()
    log_dir = agent_root / '.aget' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / 'health_log.jsonl'


def read_prior_record(log_path: Path) -> dict:
    """Read the most recent health record from the log."""
    if not log_path.is_file():
        return None
    try:
        lines = log_path.read_text().strip().split('\n')
        if lines and lines[-1].strip():
            return json.loads(lines[-1])
    except Exception:
        pass
    return None


def compute_trend(current: dict, prior: dict) -> str:
    """Compute health trend vs prior session (CAP-REL-025-03)."""
    if not prior:
        return 'baseline'

    curr_summary = current.get('summary', {})
    prior_summary = prior.get('summary', {})

    curr_score = curr_summary.get('ok', 0) - curr_summary.get('warn', 0) * 2 - curr_summary.get('critical', 0) * 5
    prior_score = prior_summary.get('ok', 0) - prior_summary.get('warn', 0) * 2 - prior_summary.get('critical', 0) * 5

    if curr_score > prior_score:
        return 'improved'
    elif curr_score < prior_score:
        return 'degraded'
    else:
        return 'stable'


def detect_regressions(current: dict, prior: dict) -> list:
    """Detect regressions (OK -> WARN/CRITICAL) (CAP-REL-025-04)."""
    if not prior:
        return []

    prior_status = {}
    for check in prior.get('checks', []):
        prior_status[check['name']] = check['status']

    regressions = []
    for check in current.get('checks', []):
        name = check['name']
        curr_status = check['status']
        prev_status = prior_status.get(name, 'unknown')

        if prev_status == 'OK' and curr_status in ('WARN', 'CRITICAL'):
            regressions.append({
                'check': name,
                'was': prev_status,
                'now': curr_status,
            })

    return regressions


def run_self_test() -> bool:
    """Self-test for health_logger.py."""
    passed = 0
    failed = 0

    # T1: Health record creation
    data = {'checks': [
        {'name': 'check_a', 'status': 'OK', 'details': 'fine'},
        {'name': 'check_b', 'status': 'WARN', 'details': 'warning'},
        {'name': 'check_c', 'status': 'OK', 'details': 'fine'},
    ]}
    record = create_health_record(data, 'test_session')
    if record['summary']['ok'] == 2 and record['summary']['warn'] == 1:
        print("  [+] T1 PASS: Health record created with correct summary")
        passed += 1
    else:
        print(f"  [-] T1 FAIL: Summary mismatch: {record['summary']}")
        failed += 1

    # T2: Trend detection
    prior = {'summary': {'ok': 3, 'warn': 0, 'critical': 0}}
    current = {'summary': {'ok': 2, 'warn': 1, 'critical': 0}}
    trend = compute_trend(current, prior)
    if trend == 'degraded':
        print("  [+] T2 PASS: Degradation trend detected")
        passed += 1
    else:
        print(f"  [-] T2 FAIL: Expected 'degraded'; got '{trend}'")
        failed += 1

    # T3: Regression detection
    prior_rec = {'checks': [
        {'name': 'check_a', 'status': 'OK', 'details': ''},
        {'name': 'check_b', 'status': 'OK', 'details': ''},
    ]}
    current_rec = {'checks': [
        {'name': 'check_a', 'status': 'WARN', 'details': ''},
        {'name': 'check_b', 'status': 'OK', 'details': ''},
    ]}
    regressions = detect_regressions(current_rec, prior_rec)
    if len(regressions) == 1 and regressions[0]['check'] == 'check_a':
        print("  [+] T3 PASS: Regression detected (OK -> WARN)")
        passed += 1
    else:
        print(f"  [-] T3 FAIL: Expected 1 regression; got {len(regressions)}")
        failed += 1

    # T4: JSONL serialization
    try:
        line = json.dumps(record) + '\n'
        parsed = json.loads(line.strip())
        if parsed['session_id'] == 'test_session':
            print("  [+] T4 PASS: Record serializes to JSONL")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: Session ID mismatch")
            failed += 1
    except Exception as e:
        print(f"  [-] T4 FAIL: Serialization error: {e}")
        failed += 1

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Healthcheck Result Persistence (CAP-REL-025)',
    )
    parser.add_argument('--trend', action='store_true', help='Show trend vs prior session')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('--test', action='store_true', help='Run self-test')
    parser.add_argument('--session-id', help='Override session ID')
    args = parser.parse_args()

    if args.test:
        print("health_logger.py self-test (CAP-REL-025)")
        success = run_self_test()
        sys.exit(0 if success else 1)

    agent_root = get_agent_root()
    log_path = get_log_path(agent_root)

    # Run healthcheck
    healthcheck_data = run_healthcheck(agent_root)
    record = create_health_record(healthcheck_data, args.session_id)

    # Get prior record for trend
    prior = read_prior_record(log_path)
    trend = compute_trend(record, prior)
    regressions = detect_regressions(record, prior)

    # Append to log
    with open(log_path, 'a') as f:
        f.write(json.dumps(record) + '\n')

    # Output
    if args.json:
        output = {
            'record': record,
            'trend': trend,
            'regressions': regressions,
        }
        print(json.dumps(output, indent=2))
    else:
        summary = record['summary']
        print(f"Health: OK={summary['ok']} WARN={summary['warn']} CRITICAL={summary['critical']}")
        print(f"Trend: {trend}" + (f" (vs {prior['session_id']})" if prior else ""))
        if regressions:
            print(f"Regressions ({len(regressions)}):")
            for r in regressions:
                print(f"  {r['check']}: {r['was']} -> {r['now']}")
        print(f"Logged to: {log_path}")


if __name__ == '__main__':
    main()
