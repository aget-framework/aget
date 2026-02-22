#!/usr/bin/env python3
"""
Persistent Validation Logger

Wraps validation scripts with structured JSON logging to
.aget/logs/validation_log.jsonl per CAP-REL-021.

Implements:
    CAP-REL-021-01: Append structured JSON record to validation_log.jsonl
    CAP-REL-021-02: Record includes timestamp, script_name, aget_version,
                     checks_passed, checks_failed, exit_code, check_details
    CAP-REL-021-03: Auto-create .aget/logs/ if absent
    CAP-REL-021-04: Include failure_details on non-zero exit
    CAP-REL-021-05: Never produce only ephemeral output

Prevents: Ephemeral_Validation anti-pattern (L605)

Usage:
    # Wrap an existing validation script:
    python3 validation_logger.py --wrap pre_release_validation.py -- --version 3.6.0

    # Log a result directly (for scripts that already collect results):
    python3 validation_logger.py --log --script my_script --version 3.6.0 \\
        --passed 5 --failed 1 --exit-code 1 --details '[{"name":"check1","status":"pass"}]'

    # Self-test:
    python3 validation_logger.py --test

Exit Codes:
    Inherits from wrapped script (--wrap mode)
    0: Success (--log and --test modes)
    1: Failure
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


def ensure_logs_dir(agent_root: Path) -> Path:
    """CAP-REL-021-03: Auto-create .aget/logs/ if absent."""
    logs_dir = agent_root / '.aget' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def create_validation_record(
    script_name: str,
    aget_version: str,
    checks_passed: int,
    checks_failed: int,
    exit_code: int,
    check_details: list,
    failure_details: list = None,
) -> dict:
    """Create a Validation_Log record per CAP-REL-021-02."""
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'script': script_name,
        'aget_version': aget_version,
        'checks_passed': checks_passed,
        'checks_failed': checks_failed,
        'exit_code': exit_code,
        'check_details': check_details,
    }
    # CAP-REL-021-04: Include failure_details on non-zero exit
    if exit_code != 0 and failure_details:
        record['failure_details'] = failure_details
    return record


def append_to_log(agent_root: Path, record: dict) -> Path:
    """Append record to validation_log.jsonl. Returns log file path."""
    logs_dir = ensure_logs_dir(agent_root)
    log_file = logs_dir / 'validation_log.jsonl'
    with open(log_file, 'a') as f:
        f.write(json.dumps(record, separators=(',', ':')) + '\n')
    return log_file


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)


def parse_script_output(stdout: str, stderr: str) -> list:
    """Best-effort parse of validation script output into check_details.

    Recognizes multiple output formats:
    - Emoji: ✅ PASS: name / ❌ FAIL: name  (post_release_validation.py)
    - Bracket: [+] Name: detail / [-] Name: detail  (aget_housekeeping_protocol.py)
    - Text: PASS: name / FAIL: name  (pre_release_validation.py)
    """
    check_details = []
    for line in stdout.splitlines():
        clean = _strip_ansi(line).strip()

        # Format 1: emoji markers (✅/❌)
        if clean.startswith('✅') or clean.startswith('❌'):
            is_pass = clean.startswith('✅')
            rest = clean.split(':', 1)
            name = rest[1].strip() if len(rest) > 1 else clean[2:].strip()
            # Remove PASS/FAIL prefix if present
            for prefix in ['PASS ', 'FAIL ']:
                if name.startswith(prefix):
                    name = name[len(prefix):]

        # Format 2: bracket markers ([+]/[-]/[!])
        elif clean.startswith('[+]') or clean.startswith('[-]') or clean.startswith('[!]'):
            is_pass = clean.startswith('[+]')
            rest = clean[3:].strip().split(':', 1)
            name = rest[0].strip()

        # Format 3: text PASS/FAIL prefix
        elif clean.startswith('✅ PASS:') or clean.startswith('❌ FAIL:'):
            is_pass = 'PASS' in clean[:10]
            name = clean.split(':', 1)[1].strip() if ':' in clean else clean

        else:
            continue

        detail = {'name': name.strip(), 'status': 'pass' if is_pass else 'fail'}
        if not is_pass:
            detail['error'] = name.strip()
        check_details.append(detail)

    return check_details


def wrap_script(script_path: str, script_args: list, agent_root: Path) -> int:
    """Run a validation script and log its results."""
    script_name = os.path.basename(script_path)
    aget_version = get_aget_version(agent_root)

    # Run the script
    cmd = [sys.executable, script_path] + script_args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(agent_root),
        )
    except subprocess.TimeoutExpired:
        record = create_validation_record(
            script_name=script_name,
            aget_version=aget_version,
            checks_passed=0,
            checks_failed=1,
            exit_code=124,
            check_details=[{'name': 'timeout', 'status': 'fail', 'error': 'Script timed out after 300s'}],
            failure_details=[{'reason': 'timeout', 'timeout_seconds': 300}],
        )
        append_to_log(agent_root, record)
        print("TIMEOUT: Script exceeded 300s", file=sys.stderr)
        return 124
    except FileNotFoundError:
        print(f"ERROR: Script not found: {script_path}", file=sys.stderr)
        return 3

    # Print original output (preserve existing behavior)
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)

    # Parse output into check_details
    check_details = parse_script_output(result.stdout, result.stderr)
    checks_passed = sum(1 for d in check_details if d['status'] == 'pass')
    checks_failed = sum(1 for d in check_details if d['status'] == 'fail')

    failure_details = [d for d in check_details if d['status'] == 'fail']

    record = create_validation_record(
        script_name=script_name,
        aget_version=aget_version,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        exit_code=result.returncode,
        check_details=check_details,
        failure_details=failure_details if failure_details else None,
    )

    log_file = append_to_log(agent_root, record)
    print(f"\n[validation_logger] Logged to {log_file.relative_to(agent_root)}", file=sys.stderr)

    return result.returncode


def log_direct(args, agent_root: Path) -> int:
    """Log a result directly from structured input."""
    try:
        details = json.loads(args.details) if args.details else []
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in --details: {e}", file=sys.stderr)
        return 3

    failure_details = [d for d in details if d.get('status') == 'fail']

    record = create_validation_record(
        script_name=args.script,
        aget_version=args.version or get_aget_version(agent_root),
        checks_passed=args.passed,
        checks_failed=args.failed,
        exit_code=args.exit_code,
        check_details=details,
        failure_details=failure_details if failure_details else None,
    )

    log_file = append_to_log(agent_root, record)
    print(f"Logged to {log_file.relative_to(agent_root)}")
    return 0


def self_test(agent_root: Path) -> int:
    """Self-test: create a test record and verify it was written."""
    logs_dir = ensure_logs_dir(agent_root)
    log_file = logs_dir / 'validation_log.jsonl'

    # Count lines before
    before = 0
    if log_file.exists():
        with open(log_file) as f:
            before = sum(1 for _ in f)

    # Create test record
    record = create_validation_record(
        script_name='validation_logger.py --test',
        aget_version=get_aget_version(agent_root),
        checks_passed=1,
        checks_failed=0,
        exit_code=0,
        check_details=[{'name': 'self_test', 'status': 'pass'}],
    )
    append_to_log(agent_root, record)

    # Count lines after
    with open(log_file) as f:
        after = sum(1 for _ in f)

    if after > before:
        print(f"PASS: Validation logged ({log_file.relative_to(agent_root)})")
        # Verify JSON is valid
        with open(log_file) as f:
            lines = f.readlines()
            last_line = json.loads(lines[-1])
            assert last_line['script'] == 'validation_logger.py --test'
            assert last_line['exit_code'] == 0
            assert 'timestamp' in last_line
            assert 'aget_version' in last_line
        print(f"PASS: Record structure valid (CAP-REL-021-02)")
        print(f"PASS: {after} total records in log")
        return 0
    else:
        print("FAIL: No log entry created")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Persistent Validation Logger (CAP-REL-021)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--wrap', metavar='SCRIPT',
                      help='Wrap a validation script with logging')
    mode.add_argument('--log', action='store_true',
                      help='Log a result directly')
    mode.add_argument('--test', action='store_true',
                      help='Self-test: create test record and verify')

    # --log mode arguments
    parser.add_argument('--script', help='Script name (--log mode)')
    parser.add_argument('--version', help='AGET version (--log mode)')
    parser.add_argument('--passed', type=int, default=0, help='Checks passed (--log mode)')
    parser.add_argument('--failed', type=int, default=0, help='Checks failed (--log mode)')
    parser.add_argument('--exit-code', type=int, default=0, help='Exit code (--log mode)')
    parser.add_argument('--details', help='JSON array of check details (--log mode)')

    # Passthrough arguments for wrapped script
    parser.add_argument('script_args', nargs='*',
                        help='Arguments to pass to wrapped script (after --)')

    args = parser.parse_args()
    agent_root = get_agent_root()

    if args.test:
        return self_test(agent_root)
    elif args.log:
        if not args.script:
            parser.error('--script is required with --log')
        return log_direct(args, agent_root)
    elif args.wrap:
        return wrap_script(args.wrap, args.script_args, agent_root)

    return 3


if __name__ == '__main__':
    sys.exit(main())
