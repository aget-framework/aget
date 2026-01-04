#!/usr/bin/env python3
"""
Validate file naming conventions for AGET repositories.

Implements: CAP-NAME-001 (file naming), CAP-VAL-002 (validator structure)
Traces to: AGET_FILE_NAMING_CONVENTIONS.md v2.0.0

Checks all 10 categories (A-J):
- Category A: Versioned artifacts (*_v#.#.md)
- Category B: Sequenced artifacts (L###_*.md, ADR-###-*.md)
- Category C: Temporal artifacts (SESSION_YYYY-MM-DD_*.md)
- Category D: Stable artifacts (SOP_*.md, PATTERN_*.md)
- Category E: Code files (*.py)
- Category F: Standard open-source files (README.md, LICENSE, etc.) - WHITELISTED
- Category G: Requirement documents (R-XXX-NNN patterns)
- Category H: Change proposals (CP-###_*.md)
- Category I: Protocol documents (*_PROTOCOL.md)
- Category J: Checklists (*_CHECKLIST.md)

Usage:
    python3 validate_file_naming.py /path/to/repo
    python3 validate_file_naming.py /path/to/repo --verbose

Exit codes:
    0: All validations passed
    1: Naming convention violations found
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Set


# Category F: Standard Open-Source Files (whitelisted per L439)
CATEGORY_F_WHITELIST: Set[str] = {
    'README.md',
    'LICENSE',
    'LICENSE.md',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'CODE_OF_CONDUCT.md',
    'SECURITY.md',
    'UPGRADING.md',
    'MAINTAINERS.md',      # Common open-source file
    'AUTHORS.md',          # Common open-source file
    'AGENTS.md',           # AGET-specific but community-facing
    'CLAUDE.md',           # CLI settings file
    '.gitignore',
    '.gitattributes',
    'requirements.txt',
    'pyproject.toml',
    'setup.py',
    'setup.cfg',
    'conftest.py',         # pytest convention
    '__init__.py',         # Python convention
    'Makefile',
    'Dockerfile',
    '.dockerignore',
    'manifest.yaml',       # AGET manifest
    'INVENTORY.md',        # Inventory files
}

# Directories to skip entirely
SKIP_DIRS: Set[str] = {
    '.git',
    '__pycache__',
    '.pytest_cache',
    'node_modules',
    '.venv',
    'venv',
    'archive',             # Archived files exempt
    '.aget/archive',
}


def is_category_f(filename: str) -> bool:
    """Check if file is a Category F standard open-source file."""
    return filename in CATEGORY_F_WHITELIST


def validate_category_a(filename: str) -> Tuple[bool, str]:
    """Validate Category A: Versioned artifacts."""
    # Pattern: {TYPE}_{NAME}_v{M}.{m}.md or .yaml
    pattern = r'^[A-Z][A-Z0-9_]*_v\d+\.\d+(-\w+)?\.(?:md|yaml|json)$'
    if re.match(pattern, filename):
        return True, "Category A (Versioned)"
    return False, ""


def validate_category_b_ldoc(filename: str) -> Tuple[bool, str]:
    """Validate Category B: L-docs."""
    pattern = r'^L\d{1,4}_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Category B (L-doc)"
    return False, ""


def validate_category_b_adr(filename: str) -> Tuple[bool, str]:
    """Validate Category B: ADRs."""
    pattern = r'^ADR-\d{3}-[\w-]+\.md$'
    if re.match(pattern, filename):
        return True, "Category B (ADR)"
    return False, ""


def validate_category_c(filename: str) -> Tuple[bool, str]:
    """Validate Category C: Temporal artifacts."""
    pattern = r'^(SESSION|CHECKPOINT|FINDING)_\d{4}-\d{2}-\d{2}[_T]?[\w]*\.md$'
    if re.match(pattern, filename):
        return True, "Category C (Temporal)"
    return False, ""


def validate_category_d_sop(filename: str) -> Tuple[bool, str]:
    """Validate Category D: SOPs."""
    pattern = r'^SOP_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Category D (SOP)"
    return False, ""


def validate_category_d_pattern(filename: str) -> Tuple[bool, str]:
    """Validate Category D: Patterns."""
    pattern = r'^PATTERN_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Category D (Pattern)"
    return False, ""


def validate_category_e(filename: str) -> Tuple[bool, str]:
    """Validate Category E: Python code files."""
    if filename.endswith('.py'):
        # Should be snake_case.py
        pattern = r'^[a-z][a-z0-9_]*\.py$'
        if re.match(pattern, filename):
            return True, "Category E (Code)"
        # Allow test_ prefix
        if re.match(r'^test_[a-z][a-z0-9_]*\.py$', filename):
            return True, "Category E (Test)"
    return False, ""


def validate_category_h(filename: str) -> Tuple[bool, str]:
    """Validate Category H: Change proposals."""
    pattern = r'^CP-\d{3}_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Category H (Change Proposal)"
    return False, ""


def validate_category_i(filename: str) -> Tuple[bool, str]:
    """Validate Category I: Protocol documents."""
    pattern = r'^[A-Z][A-Z0-9_]*_PROTOCOL\.md$'
    if re.match(pattern, filename):
        return True, "Category I (Protocol)"
    return False, ""


def validate_category_j(filename: str) -> Tuple[bool, str]:
    """Validate Category J: Checklists."""
    pattern = r'^[A-Z][A-Z0-9_]*_CHECKLIST\.md$'
    if re.match(pattern, filename):
        return True, "Category J (Checklist)"
    return False, ""


def validate_guide(filename: str) -> Tuple[bool, str]:
    """Validate guide documents."""
    pattern = r'^[A-Z][A-Z0-9_]*_GUIDE\.md$'
    if re.match(pattern, filename):
        return True, "Guide document"
    return False, ""


def validate_spec(filename: str) -> Tuple[bool, str]:
    """Validate spec documents (with or without version)."""
    # Versioned spec
    pattern_v = r'^AGET_[A-Z][A-Z0-9_]*_SPEC_v\d+\.\d+\.(?:md|yaml)$'
    if re.match(pattern_v, filename):
        return True, "Spec (versioned)"
    # Unversioned spec (legacy)
    pattern = r'^AGET_[A-Z][A-Z0-9_]*_SPEC\.(?:md|yaml)$'
    if re.match(pattern, filename):
        return True, "Spec"
    # Non-AGET prefixed spec
    pattern2 = r'^[A-Z][A-Z0-9_]*_SPEC\.(?:md|yaml)$'
    if re.match(pattern2, filename):
        return True, "Spec"
    return False, ""


def validate_conventions(filename: str) -> Tuple[bool, str]:
    """Validate conventions documents."""
    pattern = r'^AGET_[A-Z][A-Z0-9_]*_CONVENTIONS\.md$'
    if re.match(pattern, filename):
        return True, "Conventions"
    return False, ""


def validate_vocabulary(filename: str) -> Tuple[bool, str]:
    """Validate vocabulary documents."""
    pattern = r'^AGET_[A-Z][A-Z0-9_]*_VOCABULARY\.md$'
    if re.match(pattern, filename):
        return True, "Vocabulary"
    return False, ""


def validate_process(filename: str) -> Tuple[bool, str]:
    """Validate process documents."""
    pattern = r'^PROCESS_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Process"
    return False, ""


def validate_requirement_file(filename: str) -> Tuple[bool, str]:
    """Validate Category G requirement document files."""
    # R-XXX-NNN_description.md
    pattern = r'^R-[A-Z]{2,6}-\d{3}_[\w]+\.md$'
    if re.match(pattern, filename):
        return True, "Category G (Requirement)"
    return False, ""


def validate_delta(filename: str) -> Tuple[bool, str]:
    """Validate delta documents."""
    # Matches: AGET_DELTA_v3.0.md, AGET_DELTA_v3.0-alpha.1.md
    pattern = r'^AGET_DELTA_v[\d]+\.[\d]+([.-][\w.]+)?\.md$'
    if re.match(pattern, filename):
        return True, "Delta"
    return False, ""


def validate_template_file(filename: str) -> Tuple[bool, str]:
    """Validate template documents."""
    pattern = r'^[A-Z][A-Z0-9_]*_TEMPLATE\.md$'
    if re.match(pattern, filename):
        return True, "Template"
    return False, ""


def validate_project_plan(filename: str) -> Tuple[bool, str]:
    """Validate PROJECT_PLAN documents."""
    pattern = r'^PROJECT_PLAN_[\w]+_v\d+\.\d+\.md$'
    if re.match(pattern, filename):
        return True, "PROJECT_PLAN"
    # Legacy format without doc version
    pattern2 = r'^PROJECT_PLAN_[\w]+\.md$'
    if re.match(pattern2, filename):
        return True, "PROJECT_PLAN (legacy)"
    return False, ""


def validate_file(filepath: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Validate a single file's naming convention.

    Returns:
        (is_valid, category_or_error)
    """
    filename = filepath.name

    # Category F: Whitelisted files - always valid
    if is_category_f(filename):
        return True, "Category F (Open-Source)"

    # Try each category validator
    validators = [
        validate_category_a,
        validate_category_b_ldoc,
        validate_category_b_adr,
        validate_category_c,
        validate_category_d_sop,
        validate_category_d_pattern,
        validate_category_e,
        validate_category_h,
        validate_category_i,
        validate_category_j,
        validate_guide,
        validate_spec,
        validate_conventions,
        validate_vocabulary,
        validate_process,
        validate_requirement_file,
        validate_delta,
        validate_template_file,
        validate_project_plan,
    ]

    for validator in validators:
        is_valid, category = validator(filename)
        if is_valid:
            return True, category

    # Files that don't need validation
    skip_extensions = {'.json', '.yaml', '.yml', '.txt', '.csv', '.png', '.jpg', '.gif'}
    if filepath.suffix in skip_extensions:
        return True, "Data/config file"

    # Hidden files
    if filename.startswith('.'):
        return True, "Hidden file"

    # Session files (alternative format)
    if re.match(r'^session_\d{4}-\d{2}-\d{2}[_T]?[\w]*\.md$', filename):
        return True, "Session (lowercase)"

    # Index files
    if filename in {'index.json', 'index.md', 'index.yaml'}:
        return True, "Index file"

    # Markdown files in docs that don't match patterns
    if filepath.suffix == '.md':
        # Check if it's in a docs directory (more lenient)
        if 'docs' in filepath.parts or 'knowledge' in filepath.parts:
            return True, "Documentation"

        return False, f"Naming violation: {filename}"

    return True, "Other"


def validate_directory(repo_path: Path, verbose: bool = False) -> Tuple[int, List[str]]:
    """
    Validate all files in a repository.

    Returns:
        (violation_count, list_of_violations)
    """
    violations = []
    checked = 0

    for filepath in repo_path.rglob('*'):
        # Skip directories
        if filepath.is_dir():
            continue

        # Skip files in excluded directories
        rel_path = filepath.relative_to(repo_path)
        if any(skip in rel_path.parts for skip in SKIP_DIRS):
            continue

        is_valid, result = validate_file(filepath, verbose)
        checked += 1

        if not is_valid:
            violations.append(f"{rel_path}: {result}")
        elif verbose:
            print(f"  ✓ {rel_path}: {result}")

    return len(violations), violations


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 validate_file_naming.py /path/to/repo [--verbose]")
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)

    print(f"Validating file naming in: {repo_path}")
    print(f"Spec: AGET_FILE_NAMING_CONVENTIONS.md v2.0.0")
    print()

    violation_count, violations = validate_directory(repo_path, verbose)

    if violations:
        print(f"\n❌ Found {violation_count} naming violations:")
        for v in violations[:20]:  # Limit output
            print(f"  - {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
        sys.exit(1)
    else:
        print("✅ All file names comply with AGET_FILE_NAMING_CONVENTIONS.md")
        sys.exit(0)


if __name__ == '__main__':
    main()
