#!/usr/bin/env python3
"""
validate_skill_dependencies.py - Validate skill file dependencies exist

Per R-SKILL-DEP-001: BEFORE deploying a skill, validate all file paths
referenced in SKILL.md exist.

Usage:
    python3 validate_skill_dependencies.py                    # All skills in .claude/skills/
    python3 validate_skill_dependencies.py --skill <path>     # Specific skill
    python3 validate_skill_dependencies.py --check            # Exit 0/1 for CI
    python3 validate_skill_dependencies.py --verbose          # Show all paths checked

Reference: L586, SKILL_NAMING_CONVENTION_SPEC v1.1.0
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns to extract file paths from SKILL.md
FILE_PATH_PATTERNS = [
    # Backtick-quoted paths with extensions
    r'`([^`]+\.(?:md|py|yaml|json|template\.md))`',
    # Paths in specific contexts
    r'templates/[a-zA-Z0-9_/-]+\.(?:md|template\.md)',
    r'specs/[a-zA-Z0-9_/-]+\.(?:md|yaml)',
    r'planning/[a-zA-Z0-9_/-]+\.md',
    r'knowledge/[a-zA-Z0-9_/-]+/?',
    r'sops/[a-zA-Z0-9_/-]+\.md',
]

# Paths to ignore (not actual file dependencies)
IGNORE_PATTERNS = [
    r'^https?://',      # URLs
    r'^#',              # Anchors
    r'\{',              # Template variables (curly braces)
    r'^SKILL-\d+',      # Skill IDs
    r'^v\d+\.',         # Version numbers
    r'\.\./',           # Relative parent paths
    r'^example',        # Example paths
    r'\*',              # Glob patterns (*.md, L*.md)
    r'<',               # Template placeholders (<NAME>, <name>)
    r'###',             # Number placeholders (L###)
    r'YYYY',            # Date placeholders (YYYY-MM-DD)
    r'XXX',             # ID placeholders (POC-XXX, SKILL-XXX)
    r'^knowledge/README$',  # Extension mismatch (README vs README.md)
]


def extract_paths(skill_md_content: str) -> List[str]:
    """Extract file paths from SKILL.md content."""
    paths = set()

    for pattern in FILE_PATH_PATTERNS:
        matches = re.findall(pattern, skill_md_content)
        for match in matches:
            # Clean up the match
            path = match.strip('`').strip()

            # Skip ignored patterns
            if any(re.search(ignore, path) for ignore in IGNORE_PATTERNS):
                continue

            # Skip if too short or doesn't look like a path
            if len(path) < 5 or '/' not in path:
                continue

            paths.add(path)

    return sorted(paths)


def validate_paths(paths: List[str], base_dir: Path) -> List[Tuple[str, bool]]:
    """Validate each path exists relative to base_dir."""
    results = []
    for path in paths:
        full_path = base_dir / path
        exists = full_path.exists()
        results.append((path, exists))
    return results


def find_skill_dirs(skills_root: Path) -> List[Path]:
    """Find all skill directories under .claude/skills/."""
    if not skills_root.exists():
        return []
    return [d for d in skills_root.iterdir()
            if d.is_dir() and d.name.startswith('aget-')]


def validate_skill(skill_dir: Path, base_dir: Path, verbose: bool = False) -> Tuple[int, int, List[str]]:
    """
    Validate a single skill's dependencies.

    Returns: (total_paths, missing_count, missing_paths)
    """
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        if verbose:
            print(f"  No SKILL.md found in {skill_dir.name}")
        return 0, 0, []

    content = skill_md.read_text()
    paths = extract_paths(content)

    if not paths:
        if verbose:
            print(f"  No file dependencies found in {skill_dir.name}")
        return 0, 0, []

    results = validate_paths(paths, base_dir)
    missing = [path for path, exists in results if not exists]

    if verbose:
        print(f"\n  {skill_dir.name}:")
        for path, exists in results:
            status = "EXISTS" if exists else "MISSING"
            print(f"    [{status}] {path}")

    return len(paths), len(missing), missing


def main():
    parser = argparse.ArgumentParser(
        description='Validate skill file dependencies exist (R-SKILL-DEP-001)'
    )
    parser.add_argument('--skill', type=str, help='Path to specific skill directory')
    parser.add_argument('--check', action='store_true',
                        help='Exit with code 1 if any dependencies missing')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all paths checked')
    parser.add_argument('--base-dir', type=str, default='.',
                        help='Base directory for resolving paths (default: current dir)')

    args = parser.parse_args()
    base_dir = Path(args.base_dir).resolve()

    # Find skills to validate
    if args.skill:
        skill_dirs = [Path(args.skill).resolve()]
    else:
        skills_root = base_dir / '.claude' / 'skills'
        skill_dirs = find_skill_dirs(skills_root)

    if not skill_dirs:
        print("No skills found to validate")
        sys.exit(0)

    print(f"Validating skill dependencies (base: {base_dir})")
    print("=" * 60)

    total_skills = 0
    total_paths = 0
    total_missing = 0
    all_missing = []

    for skill_dir in sorted(skill_dirs):
        paths, missing, missing_list = validate_skill(skill_dir, base_dir, args.verbose)
        total_skills += 1
        total_paths += paths
        total_missing += missing

        if missing_list:
            all_missing.append((skill_dir.name, missing_list))

    # Summary
    print("\n" + "=" * 60)
    print(f"Skills checked: {total_skills}")
    print(f"Dependencies found: {total_paths}")
    print(f"Missing: {total_missing}")

    if all_missing:
        print("\nMissing Dependencies:")
        for skill_name, missing_paths in all_missing:
            print(f"\n  {skill_name}:")
            for path in missing_paths:
                print(f"    - {path}")

    if total_missing == 0:
        print("\nAll dependencies validated successfully.")
        status = "PASS"
    else:
        print(f"\nValidation FAILED: {total_missing} missing dependencies")
        status = "FAIL"

    print(f"\nR-SKILL-DEP-001 Validation: {status}")

    if args.check and total_missing > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
