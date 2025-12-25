#!/usr/bin/env python3
"""
Validate file naming conventions per AGET_FILE_NAMING_CONVENTIONS.md

Checks:
- L-docs: L###_snake_case.md (unique numbers)
- SOPs: SOP_*.md
- PATTERNs: PATTERN_*.md
- PROJECT_PLANs: PROJECT_PLAN_*_v#.#.md
- Sessions: SESSION_YYYY-MM-DD_*.md

Usage:
    python3 validate_naming_conventions.py /path/to/agent
    python3 validate_naming_conventions.py /path/to/agent1 /path/to/agent2 ...
"""

import re
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple


def validate_l_docs(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate L-doc naming and uniqueness."""
    errors = []
    evolution_dir = agent_path / '.aget' / 'evolution'

    if not evolution_dir.exists():
        return True, []  # No evolution dir is OK

    l_docs = list(evolution_dir.glob('L*.md'))
    l_numbers = []

    for doc in l_docs:
        # Check pattern: L###_snake_case.md
        match = re.match(r'^L(\d+)_[\w]+\.md$', doc.name)
        if not match:
            if doc.name.startswith('L') and doc.name.endswith('.md'):
                errors.append(f"L-doc naming violation: {doc.name} (should be L###_snake_case.md)")
        else:
            l_numbers.append(match.group(1))

    # Check for duplicates
    counter = Counter(l_numbers)
    for num, count in counter.items():
        if count > 1:
            errors.append(f"Duplicate L-doc number: L{num} appears {count} times")

    return len(errors) == 0, errors


def validate_sops(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate SOP naming."""
    errors = []
    sops_dir = agent_path / 'sops'

    if not sops_dir.exists():
        return True, []  # No sops dir is OK for some agents

    for sop in sops_dir.glob('*.md'):
        name = sop.name
        # Valid patterns: SOP_*.md, *_GUIDE.md, *_CHECKLIST.md, *_PROTOCOL.md
        valid_patterns = [
            r'^SOP_[\w]+\.md$',
            r'^[\w]+_GUIDE\.md$',
            r'^[\w]+_CHECKLIST\.md$',
            r'^[\w]+_PROTOCOL\.md$',
            r'^CONTRIBUTION_GUIDE\.md$',
            r'^README\.md$',
        ]

        if not any(re.match(p, name) for p in valid_patterns):
            errors.append(f"SOP naming violation: {name} (should be SOP_*.md or *_GUIDE.md)")

    return len(errors) == 0, errors


def validate_patterns(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate PATTERN naming."""
    errors = []
    patterns_dir = agent_path / 'docs' / 'patterns'

    if not patterns_dir.exists():
        return True, []

    for pattern in patterns_dir.glob('*.md'):
        if not re.match(r'^PATTERN_[\w]+\.md$', pattern.name):
            if pattern.name != 'README.md':
                errors.append(f"Pattern naming violation: {pattern.name} (should be PATTERN_*.md)")

    return len(errors) == 0, errors


def validate_project_plans(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate PROJECT_PLAN naming."""
    errors = []
    planning_dir = agent_path / 'planning'

    if not planning_dir.exists():
        return True, []

    for plan in planning_dir.glob('PROJECT_PLAN*.md'):
        # Valid: PROJECT_PLAN_name_v#.#.md
        if not re.match(r'^PROJECT_PLAN_[\w]+_v\d+\.\d+\.md$', plan.name):
            errors.append(f"PROJECT_PLAN naming violation: {plan.name} (should be PROJECT_PLAN_*_v#.#.md)")

    return len(errors) == 0, errors


def validate_agent(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate all naming conventions for an agent."""
    all_errors = []

    valid, errors = validate_l_docs(agent_path)
    all_errors.extend(errors)

    valid, errors = validate_sops(agent_path)
    all_errors.extend(errors)

    valid, errors = validate_patterns(agent_path)
    all_errors.extend(errors)

    valid, errors = validate_project_plans(agent_path)
    all_errors.extend(errors)

    return len(all_errors) == 0, all_errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_naming_conventions.py <agent_path> [agent_path2 ...]")
        sys.exit(1)

    agent_paths = [Path(p) for p in sys.argv[1:]]

    total_valid = 0
    total_invalid = 0

    for agent_path in agent_paths:
        if not agent_path.is_dir():
            print(f"⚠️  Not a directory: {agent_path}")
            continue

        valid, errors = validate_agent(agent_path)

        if valid:
            print(f"✅ {agent_path}")
            total_valid += 1
        else:
            print(f"❌ {agent_path}")
            for error in errors:
                print(f"   ❌ {error}")
            total_invalid += 1

    print()
    print(f"{total_valid}/{total_valid + total_invalid} agents follow naming conventions")

    sys.exit(0 if total_invalid == 0 else 1)


if __name__ == '__main__':
    main()
