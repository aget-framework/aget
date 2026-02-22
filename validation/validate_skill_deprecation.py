#!/usr/bin/env python3
"""
validate_skill_deprecation.py - Skill deprecation marking validator

Per CAP-SKILL-LIFE-001: Validates SKILL.md frontmatter for deprecation fields.
Reports deprecated skills with replacements (warning, not error per R-SKILL-LIFE-005).
Validates that superseded_by references exist (R-SKILL-LIFE-006).

Usage:
    python3 validate_skill_deprecation.py --dir /path/to/agent    # Scan agent
    python3 validate_skill_deprecation.py --all --base-dir /path   # Scan all templates
    python3 validate_skill_deprecation.py --check                  # Exit 1 if errors
    python3 validate_skill_deprecation.py --test                   # Self-test

Specification: SKILL_NAMING_CONVENTION_SPEC.md CAP-SKILL-LIFE-001
Source: R-SKILL-LIFE-001 through R-SKILL-LIFE-006
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set


class SkillInfo(NamedTuple):
    """Parsed skill information from SKILL.md frontmatter."""
    path: str
    name: str
    status: str  # "active" or "deprecated"
    superseded_by: Optional[str]
    deprecated_date: Optional[str]


class Finding(NamedTuple):
    """A validation finding."""
    severity: str  # ERROR, WARN, INFO
    source: str
    message: str


def parse_skill_frontmatter(filepath: Path) -> Optional[dict]:
    """Parse YAML frontmatter from a SKILL.md file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return None

    # Extract frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"\'')
            if value:
                frontmatter[key] = value

    return frontmatter


def find_skill_dirs(agent_path: Path) -> List[Path]:
    """Find all skill directories under .claude/skills/."""
    skills_dir = agent_path / '.claude' / 'skills'
    if not skills_dir.is_dir():
        return []

    dirs = []
    for d in skills_dir.iterdir():
        if d.is_dir():
            skill_md = d / 'SKILL.md'
            if skill_md.is_file():
                dirs.append(d)
    return sorted(dirs)


def scan_skills(agent_path: Path) -> List[SkillInfo]:
    """Scan all skills in an agent directory."""
    skills = []
    for skill_dir in find_skill_dirs(agent_path):
        skill_md = skill_dir / 'SKILL.md'
        fm = parse_skill_frontmatter(skill_md)
        if fm is None:
            continue

        rel_path = str(skill_md.relative_to(agent_path))
        name = fm.get('name', skill_dir.name)
        status = fm.get('status', 'active')
        superseded_by = fm.get('superseded_by')
        deprecated_date = fm.get('deprecated_date')

        skills.append(SkillInfo(
            path=rel_path,
            name=name,
            status=status,
            superseded_by=superseded_by,
            deprecated_date=deprecated_date,
        ))

    return skills


def validate_deprecation(agent_path: Path, verbose: bool = False) -> tuple:
    """Validate skill deprecation marking.

    Returns (skills, findings) tuple.
    """
    skills = scan_skills(agent_path)
    findings = []

    if not skills:
        return skills, findings

    # Build set of known skill names for superseded_by validation
    known_skills = {s.name for s in skills}

    deprecated_count = 0
    active_count = 0

    for skill in skills:
        if skill.status == 'deprecated':
            deprecated_count += 1

            # R-SKILL-LIFE-005: Deprecated skills are warnings, not errors
            findings.append(Finding(
                severity='WARN',
                source=skill.path,
                message=f"Deprecated skill: {skill.name}"
                        + (f" (superseded by {skill.superseded_by})" if skill.superseded_by else ""),
            ))

            # R-SKILL-LIFE-002: Must have superseded_by
            if not skill.superseded_by:
                findings.append(Finding(
                    severity='ERROR',
                    source=skill.path,
                    message=f"Deprecated skill '{skill.name}' missing 'superseded_by' field",
                ))

            # R-SKILL-LIFE-003: Must have deprecated_date
            if not skill.deprecated_date:
                findings.append(Finding(
                    severity='ERROR',
                    source=skill.path,
                    message=f"Deprecated skill '{skill.name}' missing 'deprecated_date' field",
                ))
            elif not re.match(r'^\d{4}-\d{2}-\d{2}$', skill.deprecated_date):
                findings.append(Finding(
                    severity='ERROR',
                    source=skill.path,
                    message=f"Invalid deprecated_date format: '{skill.deprecated_date}' (expected YYYY-MM-DD)",
                ))

            # R-SKILL-LIFE-006: superseded_by must reference existing skill
            if skill.superseded_by and skill.superseded_by not in known_skills:
                findings.append(Finding(
                    severity='WARN',
                    source=skill.path,
                    message=f"superseded_by '{skill.superseded_by}' not found in .claude/skills/",
                ))

        else:
            active_count += 1

        if verbose:
            print(f"  SKILL: {skill.name} [{skill.status}]"
                  + (f" -> {skill.superseded_by}" if skill.superseded_by else ""))

    return skills, findings


def run_self_test() -> bool:
    """Self-test to verify validator behavior."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_skill_depr_test_'))
    passed = 0
    failed = 0

    try:
        skills_dir = test_dir / '.claude' / 'skills'

        # T1: Active skill (no status field = active)
        active_dir = skills_dir / 'aget-check-health'
        active_dir.mkdir(parents=True)
        (active_dir / 'SKILL.md').write_text(
            '---\nname: aget-check-health\ndescription: "Health check"\n---\n# Health\n'
        )

        skills, findings = validate_deprecation(test_dir)
        active_skills = [s for s in skills if s.status == 'active']
        if len(active_skills) == 1 and not findings:
            print("  [+] T1 PASS: Active skill accepted (no warnings)")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Expected 1 active skill, 0 findings; got {len(active_skills)}, {len(findings)}")
            failed += 1

        # T2: Properly deprecated skill
        depr_dir = skills_dir / 'aget-old-skill'
        depr_dir.mkdir(parents=True)
        (depr_dir / 'SKILL.md').write_text(
            '---\nname: aget-old-skill\nstatus: deprecated\n'
            'superseded_by: aget-check-health\ndeprecated_date: 2026-02-21\n'
            'description: "Old skill"\n---\n# Old\n'
        )

        skills2, findings2 = validate_deprecation(test_dir)
        warn_findings = [f for f in findings2 if f.severity == 'WARN' and 'Deprecated skill' in f.message]
        error_findings = [f for f in findings2 if f.severity == 'ERROR']
        if warn_findings and not error_findings:
            print("  [+] T2 PASS: Deprecated skill reported as warning (not error)")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Expected WARN only; got {len(warn_findings)} WARN, {len(error_findings)} ERROR")
            failed += 1

        # T3: Missing superseded_by
        bad_dir = skills_dir / 'aget-bad-depr'
        bad_dir.mkdir(parents=True)
        (bad_dir / 'SKILL.md').write_text(
            '---\nname: aget-bad-depr\nstatus: deprecated\n'
            'description: "Bad deprecation"\n---\n# Bad\n'
        )

        skills3, findings3 = validate_deprecation(test_dir)
        missing_superseded = [f for f in findings3 if "missing 'superseded_by'" in f.message]
        missing_date = [f for f in findings3 if "missing 'deprecated_date'" in f.message]
        if missing_superseded and missing_date:
            print("  [+] T3 PASS: Missing superseded_by and deprecated_date detected")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected both missing field errors")
            failed += 1

        # T4: superseded_by references non-existent skill
        phantom_dir = skills_dir / 'aget-phantom-ref'
        phantom_dir.mkdir(parents=True)
        (phantom_dir / 'SKILL.md').write_text(
            '---\nname: aget-phantom-ref\nstatus: deprecated\n'
            'superseded_by: aget-nonexistent\ndeprecated_date: 2026-02-21\n'
            'description: "Phantom ref"\n---\n# Phantom\n'
        )

        skills4, findings4 = validate_deprecation(test_dir)
        phantom_findings = [f for f in findings4 if 'not found' in f.message and 'nonexistent' in f.message]
        if phantom_findings:
            print("  [+] T4 PASS: Phantom superseded_by reference detected")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: Expected phantom reference finding")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate skill deprecation marking (CAP-SKILL-LIFE-001)',
    )
    parser.add_argument(
        '--dir', type=Path,
        help='Agent directory to scan (default: current directory)',
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Scan all templates in base directory',
    )
    parser.add_argument(
        '--base-dir', type=Path,
        default=Path(os.environ.get('AGET_FRAMEWORK_DIR', '.')),
        help='Base directory containing templates',
    )
    parser.add_argument(
        '--check', action='store_true',
        help='Exit with code 1 if errors found (CI mode)',
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show all skills checked',
    )
    parser.add_argument(
        '--test', action='store_true',
        help='Run self-test',
    )
    args = parser.parse_args()

    if args.test:
        print("validate_skill_deprecation.py self-test (CAP-SKILL-LIFE-001)")
        success = run_self_test()
        sys.exit(0 if success else 1)

    targets = []
    if args.all:
        for d in sorted(args.base_dir.iterdir()):
            if d.is_dir() and d.name.startswith('template-') and d.name.endswith('-aget'):
                targets.append(d)
    elif args.dir:
        targets.append(Path(args.dir).resolve())
    else:
        targets.append(Path.cwd())

    total_skills = 0
    total_deprecated = 0
    all_findings = []

    for target in targets:
        skills, findings = validate_deprecation(target, args.verbose)
        total_skills += len(skills)
        total_deprecated += sum(1 for s in skills if s.status == 'deprecated')
        all_findings.extend(findings)

    errors = [f for f in all_findings if f.severity == 'ERROR']
    warnings = [f for f in all_findings if f.severity == 'WARN']

    # Report
    if all_findings:
        for finding in all_findings:
            print(f"  [{finding.severity}] {finding.source}: {finding.message}")

    # Summary
    print(f"\nSkills scanned: {total_skills}")
    print(f"Active: {total_skills - total_deprecated} | Deprecated: {total_deprecated}")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    if not errors and not warnings:
        print("PASS: No deprecation issues found")

    if args.check and errors:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
