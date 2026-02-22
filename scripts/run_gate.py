#!/usr/bin/env python3
"""
Gate Execution Enforcement

Records gate completion and enforces sequential progression
per CAP-REL-022.

Implements:
    CAP-REL-022-01: Gate completion produces Gate_Record in gate_log.jsonl
    CAP-REL-022-02: Record includes gate_id, timestamp, aget_version,
                     status, validation_summary, operator
    CAP-REL-022-03: Verify prior gate has PASS record before executing
    CAP-REL-022-04: BLOCK progression if prior gate missing/failed
    CAP-REL-022-05: First gate in sequence skips prior gate check
    CAP-REL-022-06: Gate completion recorded by script, not manual checkbox

Prevents: Manual_Gate_Enforcement anti-pattern (L605)

Usage:
    # Record a gate completion:
    python3 run_gate.py --gate G0 --version 3.6.0 --status pass \\
        --summary "V-G0.1 PASS, V-G0.2 PASS"

    # Record with prior gate enforcement:
    python3 run_gate.py --gate G1 --version 3.6.0 --status pass \\
        --prior-gate G0 --summary "V-G1.1 PASS, V-G1.2 PASS"

    # Check if gate can proceed (dry run):
    python3 run_gate.py --check G1 --version 3.6.0 --prior-gate G0

    # Query gate history:
    python3 run_gate.py --history --version 3.6.0

    # Self-test:
    python3 run_gate.py --test

Exit Codes:
    0: Gate recorded / check passed / test passed
    1: Gate blocked (prior gate not passed)
    2: Gate recorded with fail status
    3: Configuration error
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_agent_root() -> Path:
    """Find agent root by looking for .aget/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / '.aget').is_dir():
            return current
        current = current.parent
    return Path.cwd()


def get_aget_version(agent_root: Path) -> str:
    """Read aget_version from .aget/version.json."""
    version_file = agent_root / '.aget' / 'version.json'
    if version_file.exists():
        try:
            with open(version_file) as f:
                data = json.load(f)
                return data.get('aget_version', 'unknown')
        except (json.JSONDecodeError, IOError):
            pass
    return 'unknown'


def get_agent_name(agent_root: Path) -> str:
    """Read agent name from .aget/identity.json."""
    identity_file = agent_root / '.aget' / 'identity.json'
    if identity_file.exists():
        try:
            with open(identity_file) as f:
                data = json.load(f)
                return data.get('name', 'unknown')
        except (json.JSONDecodeError, IOError):
            pass
    return 'unknown'


def ensure_logs_dir(agent_root: Path) -> Path:
    """Auto-create .aget/logs/ if absent."""
    logs_dir = agent_root / '.aget' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_gate_log_path(agent_root: Path) -> Path:
    """Get path to gate_log.jsonl."""
    return ensure_logs_dir(agent_root) / 'gate_log.jsonl'


def read_gate_log(agent_root: Path) -> list:
    """Read all gate records from gate_log.jsonl."""
    log_file = get_gate_log_path(agent_root)
    records = []
    if log_file.exists():
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return records


def find_gate_record(records: list, gate_id: str, version: str = None) -> dict:
    """Find the most recent record for a gate, optionally filtered by version."""
    matching = [r for r in records if r.get('gate_id') == gate_id]
    if version:
        matching = [r for r in matching if r.get('aget_version') == version]
    return matching[-1] if matching else None


def check_prior_gate(agent_root: Path, prior_gate: str, version: str) -> tuple:
    """CAP-REL-022-03/04: Verify prior gate has PASS record.

    Returns (allowed: bool, reason: str).
    """
    records = read_gate_log(agent_root)
    prior = find_gate_record(records, prior_gate, version)

    if prior is None:
        return False, f"BLOCKED: No record for gate '{prior_gate}' (version {version})"
    if prior.get('status') != 'pass':
        return False, f"BLOCKED: Gate '{prior_gate}' status is '{prior.get('status')}', not 'pass'"
    return True, f"OK: Gate '{prior_gate}' passed at {prior.get('timestamp', '?')}"


def create_gate_record(
    gate_id: str,
    aget_version: str,
    status: str,
    validation_summary: str,
    operator: str,
    prior_gate: str = None,
    checks_total: int = 0,
    checks_passed: int = 0,
    checks_failed: int = 0,
) -> dict:
    """Create a Gate_Record per CAP-REL-022-02."""
    record = {
        'gate_id': gate_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'aget_version': aget_version,
        'status': status,
        'checks_total': checks_total,
        'checks_passed': checks_passed,
        'checks_failed': checks_failed,
        'validation_summary': validation_summary,
        'operator': operator,
    }
    if prior_gate:
        record['prior_gate'] = prior_gate
    return record


def append_gate_record(agent_root: Path, record: dict) -> Path:
    """Append record to gate_log.jsonl. Returns log file path."""
    log_file = get_gate_log_path(agent_root)
    with open(log_file, 'a') as f:
        f.write(json.dumps(record, separators=(',', ':')) + '\n')
    return log_file


def record_gate(args, agent_root: Path) -> int:
    """Record gate completion with enforcement."""
    version = args.version or get_aget_version(agent_root)
    operator = get_agent_name(agent_root)

    # CAP-REL-022-03: Check prior gate (unless first gate)
    if args.prior_gate:
        allowed, reason = check_prior_gate(agent_root, args.prior_gate, version)
        if not allowed:
            # CAP-REL-022-04: Block and display reason
            print(reason, file=sys.stderr)
            return 1

    # Parse checks from summary
    checks_total = args.summary.count('PASS') + args.summary.count('FAIL')
    checks_passed = args.summary.count('PASS')
    checks_failed = args.summary.count('FAIL')

    record = create_gate_record(
        gate_id=args.gate,
        aget_version=version,
        status=args.status,
        validation_summary=args.summary,
        operator=operator,
        prior_gate=args.prior_gate,
        checks_total=checks_total,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
    )

    log_file = append_gate_record(agent_root, record)
    print(f"Gate '{args.gate}' recorded as '{args.status}' in {log_file.relative_to(agent_root)}")

    return 0 if args.status == 'pass' else 2


def check_gate(args, agent_root: Path) -> int:
    """Check if gate can proceed (dry run)."""
    version = args.version or get_aget_version(agent_root)

    if not args.prior_gate:
        # CAP-REL-022-05: First gate has no predecessor
        print(f"OK: Gate '{args.check}' has no prior gate requirement")
        return 0

    allowed, reason = check_prior_gate(agent_root, args.prior_gate, version)
    print(reason)
    return 0 if allowed else 1


def show_history(args, agent_root: Path) -> int:
    """Show gate history, optionally filtered by version."""
    records = read_gate_log(agent_root)
    if args.version:
        records = [r for r in records if r.get('aget_version') == args.version]

    if not records:
        print("No gate records found.")
        return 0

    print(f"Gate History ({len(records)} records):")
    print(f"{'Gate':<10} {'Status':<8} {'Version':<10} {'Timestamp':<28} {'Summary'}")
    print('-' * 90)
    for r in records:
        gate = r.get('gate_id', '?')
        status = r.get('status', '?')
        version = r.get('aget_version', '?')
        ts = r.get('timestamp', '?')[:25]
        summary = r.get('validation_summary', '')[:40]
        marker = '✅' if status == 'pass' else '❌'
        print(f"{gate:<10} {marker} {status:<6} {version:<10} {ts:<28} {summary}")
    return 0


def self_test(agent_root: Path) -> int:
    """Self-test: record test gates and verify enforcement."""
    logs_dir = ensure_logs_dir(agent_root)
    log_file = logs_dir / 'gate_log.jsonl'

    # Count lines before
    before = 0
    if log_file.exists():
        with open(log_file) as f:
            before = sum(1 for _ in f)

    test_version = 'test'
    operator = get_agent_name(agent_root)

    # Test 1: Record a first gate (no prior gate check)
    record = create_gate_record(
        gate_id='test-G0',
        aget_version=test_version,
        status='pass',
        validation_summary='self_test PASS',
        operator=operator,
    )
    append_gate_record(agent_root, record)
    print("PASS: First gate recorded without prior gate check (CAP-REL-022-05)")

    # Test 2: Verify enforcement blocks without prior
    allowed, reason = check_prior_gate(agent_root, 'test-nonexistent', test_version)
    assert not allowed, "Should block when prior gate doesn't exist"
    print("PASS: Blocked when prior gate missing (CAP-REL-022-04)")

    # Test 3: Verify enforcement allows with prior
    allowed, reason = check_prior_gate(agent_root, 'test-G0', test_version)
    assert allowed, "Should allow when prior gate passed"
    print("PASS: Allowed when prior gate passed (CAP-REL-022-03)")

    # Test 4: Record second gate with enforcement
    record = create_gate_record(
        gate_id='test-G1',
        aget_version=test_version,
        status='pass',
        validation_summary='self_test PASS',
        operator=operator,
        prior_gate='test-G0',
    )
    append_gate_record(agent_root, record)
    print("PASS: Sequential gate recorded (CAP-REL-022-01)")

    # Test 5: Verify record structure
    records = read_gate_log(agent_root)
    last = records[-1]
    required_fields = ['gate_id', 'timestamp', 'aget_version', 'status', 'validation_summary', 'operator']
    for field in required_fields:
        assert field in last, f"Missing field: {field}"
    print("PASS: Record structure valid (CAP-REL-022-02)")

    # Count lines after
    with open(log_file) as f:
        after = sum(1 for _ in f)

    assert after == before + 2, f"Expected {before + 2} records, got {after}"
    print(f"PASS: {after} total gate records in log")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Gate Execution Enforcement (CAP-REL-022)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--gate', metavar='GATE_ID',
                      help='Record gate completion')
    mode.add_argument('--check', metavar='GATE_ID',
                      help='Check if gate can proceed (dry run)')
    mode.add_argument('--history', action='store_true',
                      help='Show gate history')
    mode.add_argument('--test', action='store_true',
                      help='Self-test: verify enforcement works')

    # Gate recording arguments
    parser.add_argument('--version', help='AGET version')
    parser.add_argument('--status', choices=['pass', 'fail'], default='pass',
                        help='Gate status (default: pass)')
    parser.add_argument('--summary', default='',
                        help='Validation summary (e.g., "V-G1.1 PASS, V-G1.2 PASS")')
    parser.add_argument('--prior-gate', metavar='GATE_ID',
                        help='Prior gate that must have passed')

    args = parser.parse_args()
    agent_root = get_agent_root()

    if args.test:
        return self_test(agent_root)
    elif args.history:
        return show_history(args, agent_root)
    elif args.check:
        return check_gate(args, agent_root)
    elif args.gate:
        if not args.summary:
            parser.error('--summary is required with --gate')
        return record_gate(args, agent_root)

    return 3


if __name__ == '__main__':
    sys.exit(main())
