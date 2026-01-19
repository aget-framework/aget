#!/usr/bin/env python3
"""
validate_artifact_size.py - AGET Artifact Size Validator

Checks artifact sizes against AGET_SPEC_FORMAT guidance (L502, CAP-PP-012).

Usage:
    python3 validate_artifact_size.py [path] [--strict] [--json]

Exit codes:
    0 = All artifacts within optimal/acceptable limits
    1 = Warnings (soft limit exceeded)
    2 = Errors (hard limit exceeded, --strict mode only)

References:
    - L502: Artifact Comprehensibility Gap
    - CAP-PP-012: Plan Comprehensibility
    - AGET_SPEC_FORMAT.md: Artifact Size Guidance
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional


class SizeLimit(NamedTuple):
    """Size limits for an artifact type."""
    optimal: int
    warning: int
    error: int


class ValidationResult(NamedTuple):
    """Result of validating a single file."""
    path: str
    artifact_type: str
    lines: int
    status: str  # 'optimal', 'acceptable', 'warning', 'oversized'
    recommendation: Optional[str]


# Size limits per artifact type (in lines)
# Based on AGET_SPEC_FORMAT.md "Artifact Size Guidance" section
LIMITS: Dict[str, SizeLimit] = {
    'PROJECT_PLAN': SizeLimit(optimal=500, warning=1000, error=1500),
    'SPEC': SizeLimit(optimal=600, warning=800, error=1200),
    'SOP': SizeLimit(optimal=400, warning=600, error=800),
    'L-doc': SizeLimit(optimal=150, warning=250, error=400),
    'CLAUDE.md': SizeLimit(optimal=600, warning=800, error=1200),
}

# Patterns to detect artifact types
ARTIFACT_PATTERNS = [
    (r'PROJECT_PLAN[_\-].*\.md$', 'PROJECT_PLAN'),
    (r'AGET_.*_SPEC\.md$', 'SPEC'),
    (r'.*_SPEC\.md$', 'SPEC'),
    (r'SOP[_\-].*\.md$', 'SOP'),
    (r'L\d{3}[_\-].*\.md$', 'L-doc'),
    (r'CLAUDE\.md$', 'CLAUDE.md'),
    (r'AGENTS\.md$', 'CLAUDE.md'),  # Same limits as CLAUDE.md
]


def detect_artifact_type(filepath: str) -> Optional[str]:
    """Detect artifact type from filename."""
    filename = os.path.basename(filepath)
    for pattern, artifact_type in ARTIFACT_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return artifact_type
    return None


def count_lines(filepath: str) -> int:
    """Count lines in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def classify_size(lines: int, limits: SizeLimit) -> str:
    """Classify size status based on limits."""
    if lines <= limits.optimal:
        return 'optimal'
    elif lines <= limits.warning:
        return 'acceptable'
    elif lines <= limits.error:
        return 'warning'
    else:
        return 'oversized'


def get_recommendation(status: str, artifact_type: str, lines: int) -> Optional[str]:
    """Get recommendation based on status."""
    if status == 'optimal':
        return None
    elif status == 'acceptable':
        return f"Monitor growth ({lines} lines)"
    elif status == 'warning':
        if artifact_type == 'PROJECT_PLAN':
            return f"Consider decomposition into phases ({lines} lines)"
        elif artifact_type == 'SPEC':
            return f"Consider splitting by domain ({lines} lines)"
        elif artifact_type == 'SOP':
            return f"Consider modularizing procedures ({lines} lines)"
        else:
            return f"Consider reducing scope ({lines} lines)"
    else:  # oversized
        return f"DECOMPOSE REQUIRED ({lines} lines exceeds limit)"


def validate_file(filepath: str) -> Optional[ValidationResult]:
    """Validate a single file."""
    artifact_type = detect_artifact_type(filepath)
    if artifact_type is None:
        return None

    limits = LIMITS.get(artifact_type)
    if limits is None:
        return None

    lines = count_lines(filepath)
    status = classify_size(lines, limits)
    recommendation = get_recommendation(status, artifact_type, lines)

    return ValidationResult(
        path=filepath,
        artifact_type=artifact_type,
        lines=lines,
        status=status,
        recommendation=recommendation
    )


def find_artifacts(root_path: str) -> List[str]:
    """Find all potential artifacts in a directory."""
    artifacts = []
    root = Path(root_path)

    if root.is_file():
        return [str(root)]

    # Skip common non-artifact directories
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'archive'}

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip directories
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(dirpath, filename)
                if detect_artifact_type(filepath):
                    artifacts.append(filepath)

    return sorted(artifacts)


def print_results(results: List[ValidationResult], json_output: bool = False) -> None:
    """Print validation results."""
    if json_output:
        output = [
            {
                'path': r.path,
                'type': r.artifact_type,
                'lines': r.lines,
                'status': r.status,
                'recommendation': r.recommendation
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
        return

    # Group by status
    by_status = {'optimal': [], 'acceptable': [], 'warning': [], 'oversized': []}
    for r in results:
        by_status[r.status].append(r)

    # Print summary
    print(f"\n{'='*60}")
    print("AGET Artifact Size Validation (L502, CAP-PP-012)")
    print(f"{'='*60}\n")

    total = len(results)
    print(f"Total artifacts scanned: {total}")
    print(f"  Optimal:    {len(by_status['optimal'])}")
    print(f"  Acceptable: {len(by_status['acceptable'])}")
    print(f"  Warning:    {len(by_status['warning'])}")
    print(f"  Oversized:  {len(by_status['oversized'])}")
    print()

    # Print warnings and oversized
    if by_status['warning'] or by_status['oversized']:
        print(f"{'-'*60}")
        print("ISSUES FOUND:")
        print(f"{'-'*60}\n")

        for r in by_status['oversized']:
            rel_path = os.path.relpath(r.path)
            print(f"[OVERSIZED] {rel_path}")
            print(f"  Type: {r.artifact_type} | Lines: {r.lines}")
            print(f"  {r.recommendation}\n")

        for r in by_status['warning']:
            rel_path = os.path.relpath(r.path)
            print(f"[WARNING] {rel_path}")
            print(f"  Type: {r.artifact_type} | Lines: {r.lines}")
            print(f"  {r.recommendation}\n")
    else:
        print("No issues found. All artifacts within acceptable limits.")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate AGET artifact sizes against spec guidance.',
        epilog='References: L502, CAP-PP-012, AGET_SPEC_FORMAT.md'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to validate (file or directory, default: current directory)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error (2) if any artifact exceeds error limit'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only show warnings and errors'
    )

    args = parser.parse_args()

    # Find and validate artifacts
    artifacts = find_artifacts(args.path)
    results = []

    for filepath in artifacts:
        result = validate_file(filepath)
        if result:
            results.append(result)

    if not results:
        if not args.json:
            print(f"No artifacts found in {args.path}")
        return 0

    # Print results
    if not args.quiet or any(r.status in ('warning', 'oversized') for r in results):
        print_results(results, args.json)

    # Determine exit code
    has_oversized = any(r.status == 'oversized' for r in results)
    has_warnings = any(r.status == 'warning' for r in results)

    if args.strict and has_oversized:
        return 2
    elif has_warnings or has_oversized:
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
