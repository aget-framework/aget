#!/usr/bin/env python3
"""
AGET Vocabulary Compliance Checker

Validates that specification files use controlled vocabulary terms.

Usage:
    python check_aget_vocabulary.py <file_or_directory>
    python check_aget_vocabulary.py --help

Examples:
    python check_aget_vocabulary.py ../specs/WORKER_TEMPLATE_SPEC_v1.0.yaml
    python check_aget_vocabulary.py ../specs/
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Core controlled vocabulary (Title_Case terms)
CONTROLLED_VOCABULARY: Set[str] = {
    # Framework Identity
    "AGET", "Fleet_Agent", "Template", "Instance", "Core_Template",
    "Specialized_Template", "Portfolio", "Fleet", "Fleet_State",
    "Supervisor", "Principal",

    # Instance Types
    "Instance_Type",

    # Configuration
    "Version_Json", "Agents_Md", "Claude_Md", "Configuration",
    "Configuration_Size", "Configuration_Size_Limit", "Size_Warning",
    "Size_Violation",

    # Version Fields
    "aget_version", "agent_name", "instance_type", "domain", "portfolio",
    "managed_by", "intelligence_enabled", "collaboration_enabled",

    # Session Protocol
    "Wake_Protocol", "Wake_Command", "Study_Up_Protocol",
    "Wind_Down_Protocol", "Sign_Off_Protocol", "Session_State",
    "Session_Summary", "Session_Log", "Silent_Execution",

    # Evolution
    "Learning_Document", "L_Doc", "Evolution_Directory",
    "Learning_Registry", "Learning_Capture", "Pattern_Extraction",
    "Knowledge_Migration",

    # Governance
    "Project_Plan", "Gate", "Gate_Approval", "Tier",
    "Substantial_Change", "Gate_Override", "Plan_Approval",

    # Capabilities
    "Analysis_Capability", "Action_Capability", "Coordination_Capability",
    "Evolution_Capability", "File_Read", "Pattern_Search", "Web_Fetch",
    "File_Write", "Command_Execute", "Gate_Coordination",

    # Specifications
    "Specification", "Capability_Statement", "Contract_Test",
    "Spec_Maturity",

    # EARS Patterns
    "Ubiquitous_Pattern", "Event_Driven_Pattern", "State_Driven_Pattern",
    "Optional_Pattern", "Conditional_Pattern",

    # Release
    "Release", "Version_Bump", "Changelog", "Deep_Release_Notes",
    "Breaking_Change", "Migration_Guide",

    # Validation
    "Vocabulary_Compliance", "Format_Compliance", "Contract_Compliance",
    "Size_Compliance",

    # Common Objects (extensible)
    "File_Path", "File_Content", "Error_Message", "Progress_Indicator",
    "Read_Only_Mode", "Write_Operations",
}

# EARS keywords (should be UPPERCASE in statements)
EARS_KEYWORDS = {"WHEN", "WHILE", "WHERE", "IF", "THEN", "SYSTEM", "shall"}

# Constraint keywords (should be UPPERCASE)
CONSTRAINT_KEYWORDS = {
    "WITHIN", "WITHOUT", "MAINTAINING", "EXCEEDING", "BEFORE", "AFTER"
}


def extract_title_case_terms(text: str) -> List[str]:
    """Extract all Title_Case terms from text."""
    # Pattern: Word starting with capital, may contain underscores and more capitals
    pattern = r'\b[A-Z][a-z]+(?:_[A-Z][a-z]+)*\b'
    return re.findall(pattern, text)


def extract_potential_vocabulary(text: str) -> List[str]:
    """Extract terms that look like they should be in vocabulary."""
    # Title_Case with underscores
    pattern = r'\b[A-Z][a-z]+(?:_[A-Za-z]+)+\b'
    return re.findall(pattern, text)


def check_file(filepath: Path) -> Tuple[List[str], List[str], List[str]]:
    """
    Check a file for vocabulary compliance.

    Returns:
        Tuple of (known_terms, unknown_terms, suggestions)
    """
    try:
        content = filepath.read_text()
    except Exception as e:
        return [], [], [f"Error reading file: {e}"]

    found_terms = extract_potential_vocabulary(content)

    known = []
    unknown = []

    for term in found_terms:
        if term in CONTROLLED_VOCABULARY:
            known.append(term)
        else:
            unknown.append(term)

    # Remove duplicates while preserving order
    known = list(dict.fromkeys(known))
    unknown = list(dict.fromkeys(unknown))

    suggestions = []
    if unknown:
        suggestions.append(
            "Consider adding these terms to AGET_CONTROLLED_VOCABULARY.md "
            "or using existing vocabulary terms."
        )

    return known, unknown, suggestions


def check_ears_compliance(filepath: Path) -> List[str]:
    """Check EARS pattern compliance in specification files."""
    issues = []

    try:
        content = filepath.read_text()
    except Exception:
        return issues

    # Check for lowercase EARS keywords in statements
    statement_pattern = r'statement:\s*["\'](.+?)["\']'
    statements = re.findall(statement_pattern, content, re.MULTILINE)

    for stmt in statements:
        # Check SYSTEM is capitalized
        if "system" in stmt.lower() and "SYSTEM" not in stmt:
            issues.append(f"Use 'SYSTEM' (uppercase) in: {stmt[:50]}...")

        # Check 'shall' is lowercase
        if "SHALL" in stmt:
            issues.append(f"Use 'shall' (lowercase) in: {stmt[:50]}...")

    return issues


def format_report(
    filepath: Path,
    known: List[str],
    unknown: List[str],
    suggestions: List[str],
    ears_issues: List[str]
) -> str:
    """Format a compliance report for a file."""
    lines = [
        f"\n{'='*60}",
        f"File: {filepath}",
        f"{'='*60}",
    ]

    if known:
        lines.append(f"\n✓ Known vocabulary terms ({len(known)}):")
        for term in known[:10]:  # Show first 10
            lines.append(f"  - {term}")
        if len(known) > 10:
            lines.append(f"  ... and {len(known) - 10} more")

    if unknown:
        lines.append(f"\n⚠ Unknown terms ({len(unknown)}):")
        for term in unknown:
            lines.append(f"  - {term}")

    if ears_issues:
        lines.append(f"\n⚠ EARS compliance issues ({len(ears_issues)}):")
        for issue in ears_issues:
            lines.append(f"  - {issue}")

    if suggestions:
        lines.append("\n📝 Suggestions:")
        for suggestion in suggestions:
            lines.append(f"  - {suggestion}")

    if not unknown and not ears_issues:
        lines.append("\n✓ File is vocabulary compliant!")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check AGET vocabulary compliance in specification files"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to check"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if unknown terms found"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show issues, not compliant terms"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)

    # Collect files to check
    if args.path.is_file():
        files = [args.path]
    else:
        files = list(args.path.glob("**/*.md")) + list(args.path.glob("**/*.yaml"))

    if not files:
        print(f"No .md or .yaml files found in {args.path}")
        sys.exit(0)

    total_unknown = 0

    for filepath in files:
        known, unknown, suggestions = check_file(filepath)
        ears_issues = check_ears_compliance(filepath)

        total_unknown += len(unknown)

        if args.quiet and not unknown and not ears_issues:
            continue

        report = format_report(filepath, known, unknown, suggestions, ears_issues)
        print(report)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: Checked {len(files)} file(s)")
    print(f"Total unknown terms: {total_unknown}")
    print(f"{'='*60}")

    if args.strict and total_unknown > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
