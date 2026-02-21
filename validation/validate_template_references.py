#!/usr/bin/env python3
"""
validate_template_references.py - Validate cross-scope artifact references

Per CAP-TPL-017: Template artifacts shall not contain Dangling_References
to non-existent framework artifacts. Cross_Scope_References shall use
explicit paths.

Usage:
    python3 validate_template_references.py                  # Scan all templates
    python3 validate_template_references.py template-*/      # Specific templates
    python3 validate_template_references.py --check          # Exit 0/1 for CI
    python3 validate_template_references.py --strict         # Treat warnings as errors
    python3 validate_template_references.py --verbose        # Show all refs checked
    python3 validate_template_references.py --test           # Self-test

Specification: AGET_TEMPLATE_SPEC.md CAP-TPL-017
Source: L568, CAP-CORE-006, CAP-SOP-005
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple


class Reference(NamedTuple):
    """A reference found in a template file."""
    source_file: str   # File containing the reference
    line_number: int    # Line where reference appears
    ref_text: str       # The reference text
    ref_type: str       # "explicit" or "bare"
    target_path: str    # Resolved target path


class Finding(NamedTuple):
    """A validation finding."""
    severity: str       # "ERROR" or "WARN"
    ref: Reference
    message: str


# Framework artifact patterns to look for in templates
EXPLICIT_REF_PATTERNS = [
    # aget/ prefixed paths (explicit cross-scope references)
    r'`(aget/(?:specs|sops|docs|scripts|validation)/[A-Za-z0-9_./-]+)`',
    r'\(aget/((?:specs|sops|docs|scripts|validation)/[A-Za-z0-9_./-]+)\)',
    r'\[(.*?)\]\(aget/((?:specs|sops|docs|scripts|validation)/[A-Za-z0-9_./-]+)\)',
]

# Bare SOP references (might be framework SOPs without path)
BARE_SOP_PATTERN = r'(?<![/`])(SOP_aget_\w+\.md)'

# Framework SOPs that should exist in aget/sops/
KNOWN_FRAMEWORK_SOPS = {
    'SOP_aget_create.md',
    'SOP_aget_migrate.md',
    'SOP_aget_decommission.md',
}

# Core directories per CAP-CORE-006
CORE_DIRECTORIES = ['specs', 'docs', 'sops', 'scripts', 'validation']

# Paths to ignore (template variables, examples, etc.)
IGNORE_PATTERNS = [
    r'\{',              # Template variables
    r'<',               # Placeholders
    r'YYYY',            # Date placeholders
    r'^example',        # Example paths
    r'#',               # Anchors only
]

# Files to skip scanning
SKIP_FILES = {'.git', 'node_modules', '__pycache__', '.aget'}


def find_framework_root(start: Path) -> Path:
    """Find the aget-framework root directory containing aget/."""
    current = start.resolve()
    # If we're in a template directory, go up to parent
    if current.name.startswith('template-') or current.name == 'aget':
        return current.parent
    # If we're in the framework root already
    if (current / 'aget').is_dir():
        return current
    # Walk up
    for parent in current.parents:
        if (parent / 'aget').is_dir():
            return parent
    return current


def find_templates(root: Path, specific: List[str] = None) -> List[Path]:
    """Find template directories to scan."""
    if specific:
        return [Path(s).resolve() for s in specific if Path(s).is_dir()]

    templates = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and entry.name.startswith('template-') and entry.name.endswith('-aget'):
            templates.append(entry)
    return templates


def scan_markdown_files(template_dir: Path) -> List[Path]:
    """Find all markdown files in a template directory."""
    md_files = []
    for root, dirs, files in os.walk(template_dir):
        # Skip hidden and vendor directories
        dirs[:] = [d for d in dirs if d not in SKIP_FILES and not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                md_files.append(Path(root) / f)
    return md_files


def should_ignore(ref_text: str) -> bool:
    """Check if a reference should be ignored."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, ref_text):
            return True
    return False


def extract_references(filepath: Path, framework_root: Path) -> List[Reference]:
    """Extract cross-scope references from a markdown file."""
    refs = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, PermissionError):
        return refs

    lines = content.split('\n')
    rel_source = str(filepath.relative_to(framework_root))

    for line_num, line in enumerate(lines, 1):
        # Skip code blocks
        if line.strip().startswith('```'):
            continue

        # Check explicit aget/ references
        for pattern in EXPLICIT_REF_PATTERNS:
            for match in re.finditer(pattern, line):
                # Get the path part (last group is always the path)
                groups = match.groups()
                ref_path = groups[-1]
                if ref_path.startswith('aget/'):
                    ref_path = ref_path[5:]  # Remove aget/ prefix

                if should_ignore(ref_path):
                    continue

                target = framework_root / 'aget' / ref_path
                refs.append(Reference(
                    source_file=rel_source,
                    line_number=line_num,
                    ref_text=match.group(0),
                    ref_type='explicit',
                    target_path=str(target),
                ))

        # Check bare SOP references
        for match in re.finditer(BARE_SOP_PATTERN, line):
            sop_name = match.group(1)
            if should_ignore(sop_name):
                continue
            if sop_name in KNOWN_FRAMEWORK_SOPS:
                target = framework_root / 'aget' / 'sops' / sop_name
                refs.append(Reference(
                    source_file=rel_source,
                    line_number=line_num,
                    ref_text=sop_name,
                    ref_type='bare',
                    target_path=str(target),
                ))

    return refs


def validate_references(refs: List[Reference]) -> List[Finding]:
    """Validate that all references resolve to existing artifacts."""
    findings = []

    for ref in refs:
        target = Path(ref.target_path)
        if not target.exists():
            if ref.ref_type == 'bare':
                findings.append(Finding(
                    severity='WARN',
                    ref=ref,
                    message=f"Bare reference '{ref.ref_text}' not found at {ref.target_path}. "
                            f"Use explicit path: aget/sops/{ref.ref_text}",
                ))
            else:
                findings.append(Finding(
                    severity='ERROR',
                    ref=ref,
                    message=f"Dangling_Reference: '{ref.ref_text}' not found at {ref.target_path}",
                ))

    return findings


def validate_core_directories(framework_root: Path) -> List[Finding]:
    """Validate CAP-CORE-006: Framework distribution has required directories."""
    findings = []
    aget_dir = framework_root / 'aget'

    if not aget_dir.is_dir():
        findings.append(Finding(
            severity='ERROR',
            ref=Reference('aget/', 0, 'aget/', 'structure', str(aget_dir)),
            message="Framework distribution directory aget/ not found",
        ))
        return findings

    for dir_name in CORE_DIRECTORIES:
        dir_path = aget_dir / dir_name
        if not dir_path.is_dir():
            findings.append(Finding(
                severity='WARN',
                ref=Reference('aget/', 0, f'aget/{dir_name}/', 'structure', str(dir_path)),
                message=f"Missing Core_Directory: aget/{dir_name}/",
            ))

    return findings


def run_self_test() -> bool:
    """Self-test to verify validator behavior."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_ref_test_'))
    passed = 0
    failed = 0

    try:
        # Set up mock framework structure
        (test_dir / 'aget' / 'specs').mkdir(parents=True)
        (test_dir / 'aget' / 'sops').mkdir(parents=True)
        (test_dir / 'aget' / 'docs').mkdir(parents=True)
        (test_dir / 'aget' / 'scripts').mkdir(parents=True)
        (test_dir / 'aget' / 'validation').mkdir(parents=True)
        (test_dir / 'aget' / 'specs' / 'AGET_FRAMEWORK_SPEC.md').write_text('# Test spec')
        (test_dir / 'aget' / 'sops' / 'SOP_aget_create.md').write_text('# Test SOP')

        # Test template with valid reference
        tpl_dir = test_dir / 'template-test-aget'
        tpl_dir.mkdir()
        (tpl_dir / 'test_good.md').write_text(
            'See `aget/specs/AGET_FRAMEWORK_SPEC.md` for details.\n'
        )
        (tpl_dir / 'test_bad.md').write_text(
            'See `aget/specs/NONEXISTENT_SPEC.md` for details.\n'
        )
        (tpl_dir / 'test_bare.md').write_text(
            'Follow SOP_aget_create.md for creation.\n'
        )

        # Test 1: Extract references
        refs = extract_references(tpl_dir / 'test_good.md', test_dir)
        if len(refs) == 1 and refs[0].ref_type == 'explicit':
            print("  [+] T1 PASS: Explicit reference extracted")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Expected 1 explicit ref, got {len(refs)}")
            failed += 1

        # Test 2: Valid reference resolves
        findings = validate_references(refs)
        if len(findings) == 0:
            print("  [+] T2 PASS: Valid reference resolves")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Valid ref reported as finding: {findings}")
            failed += 1

        # Test 3: Dangling reference detected
        refs_bad = extract_references(tpl_dir / 'test_bad.md', test_dir)
        findings_bad = validate_references(refs_bad)
        if len(findings_bad) == 1 and findings_bad[0].severity == 'ERROR':
            print("  [+] T3 PASS: Dangling reference detected as ERROR")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected 1 ERROR, got {len(findings_bad)}")
            failed += 1

        # Test 4: Bare SOP reference detected
        refs_bare = extract_references(tpl_dir / 'test_bare.md', test_dir)
        findings_bare = validate_references(refs_bare)
        if len(refs_bare) == 1 and refs_bare[0].ref_type == 'bare':
            # SOP exists, so should be 0 findings
            if len(findings_bare) == 0:
                print("  [+] T4 PASS: Bare SOP reference resolved")
                passed += 1
            else:
                print(f"  [-] T4 FAIL: Bare SOP ref to existing SOP produced finding")
                failed += 1
        else:
            print(f"  [-] T4 FAIL: Expected 1 bare ref, got {len(refs_bare)}")
            failed += 1

        # Test 5: Core directories validated
        findings_dirs = validate_core_directories(test_dir)
        if len(findings_dirs) == 0:
            print("  [+] T5 PASS: Core directories validated")
            passed += 1
        else:
            print(f"  [-] T5 FAIL: Expected 0 dir findings, got {len(findings_dirs)}")
            failed += 1

        # Test 6: Missing core directory detected
        shutil.rmtree(test_dir / 'aget' / 'scripts')
        findings_dirs2 = validate_core_directories(test_dir)
        if len(findings_dirs2) == 1 and 'scripts' in findings_dirs2[0].message:
            print("  [+] T6 PASS: Missing core directory detected")
            passed += 1
        else:
            print(f"  [-] T6 FAIL: Expected 1 dir finding for scripts/")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate cross-scope artifact references in templates (CAP-TPL-017)',
    )
    parser.add_argument(
        'templates', nargs='*',
        help='Template directories to scan (default: all template-*-aget/)',
    )
    parser.add_argument(
        '--check', action='store_true',
        help='Exit with code 1 if errors found (CI mode)',
    )
    parser.add_argument(
        '--strict', action='store_true',
        help='Treat warnings as errors',
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show all references checked, not just findings',
    )
    parser.add_argument(
        '--test', action='store_true',
        help='Run self-test',
    )
    parser.add_argument(
        '--help-extended', action='store_true',
        help='Show extended help with examples',
    )
    args = parser.parse_args()

    if args.test:
        print("validate_template_references.py self-test")
        success = run_self_test()
        sys.exit(0 if success else 1)

    # Find framework root
    script_dir = Path(__file__).resolve().parent
    framework_root = find_framework_root(script_dir)

    if not (framework_root / 'aget').is_dir():
        print("ERROR: Cannot find aget/ framework directory", file=sys.stderr)
        sys.exit(2)

    # Find templates
    templates = find_templates(framework_root, args.templates or None)
    if not templates:
        print("No template directories found", file=sys.stderr)
        sys.exit(2)

    # Validate core directories first
    all_findings = validate_core_directories(framework_root)

    # Scan each template
    total_refs = 0
    for tpl in templates:
        md_files = scan_markdown_files(tpl)
        for md_file in md_files:
            refs = extract_references(md_file, framework_root)
            total_refs += len(refs)

            if args.verbose and refs:
                for ref in refs:
                    print(f"  REF: {ref.source_file}:{ref.line_number} -> {ref.ref_text}")

            findings = validate_references(refs)
            all_findings.extend(findings)

    # Report
    errors = [f for f in all_findings if f.severity == 'ERROR']
    warnings = [f for f in all_findings if f.severity == 'WARN']

    if all_findings:
        for finding in all_findings:
            prefix = finding.severity
            loc = f"{finding.ref.source_file}:{finding.ref.line_number}" if finding.ref.line_number else finding.ref.source_file
            print(f"  [{prefix}] {loc}: {finding.message}")

    # Summary
    print(f"\nTemplates scanned: {len(templates)}")
    print(f"References checked: {total_refs}")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    if not errors and not warnings:
        print("PASS: All references resolve")

    # Exit code
    if args.check or args.strict:
        if errors or (args.strict and warnings):
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
