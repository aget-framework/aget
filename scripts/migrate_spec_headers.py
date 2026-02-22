#!/usr/bin/env python3
"""
migrate_spec_headers.py - Migrate AGET specification headers to v1.2 format

Migrates spec headers to add Spec ID and standardize format per AGET_SPEC_FORMAT v1.2.

Usage:
    python3 migrate_spec_headers.py <spec_file_or_directory>
    python3 migrate_spec_headers.py specs/AGET_TESTING_SPEC.md
    python3 migrate_spec_headers.py specs/ --dry-run
    python3 migrate_spec_headers.py specs/ --execute

Options:
    --dry-run   Show what would be changed (default)
    --execute   Actually make changes

Author: aget-framework
Version: 1.0.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import date


# Spec ID Registry - maps spec filenames to Spec IDs
SPEC_ID_REGISTRY = {
    "AGET_FRAMEWORK_SPEC.md": "AGET-CORE-001",
    "AGET_5D_ARCHITECTURE_SPEC.md": "AGET-5D-001",
    "AGET_5D_COMPONENTS_SPEC.md": "AGET-5D-002",
    "AGET_VOCABULARY_SPEC.md": "AGET-VOC-001",
    "AGET_GOVERNANCE_HIERARCHY_SPEC.md": "AGET-GOV-001",
    "AGET_LICENSE_SPEC.md": "AGET-LIC-001",
    "AGET_ORGANIZATION_SPEC.md": "AGET-ORG-001",
    "AGET_SECURITY_SPEC.md": "AGET-SEC-001",
    "AGET_TEMPLATE_SPEC.md": "AGET-TPL-001",
    "AGET_INSTANCE_SPEC.md": "AGET-INST-001",
    "AGET_MIGRATION_SPEC.md": "AGET-MIG-001",
    "AGET_COMPATIBILITY_SPEC.md": "AGET-COMPAT-001",
    "AGET_SESSION_SPEC.md": "AGET-SES-001",
    "AGET_PYTHON_SCRIPT_SPEC.md": "AGET-SCRIPT-001",
    "AGET_VALIDATION_SPEC.md": "AGET-VAL-001",
    "AGET_TESTING_SPEC.md": "AGET-TEST-001",
    "AGET_CI_SPEC.md": "AGET-CI-001",
    "AGET_PORTABILITY_SPEC.md": "AGET-PORT-001",
    "AGET_ERROR_SPEC.md": "AGET-ERR-001",
    "AGET_CHANGE_PROPOSAL_SPEC.md": "AGET-CP-001",
    "AGET_SOP_SPEC.md": "AGET-SOP-001",
    "AGET_RELEASE_SPEC.md": "AGET-REL-001",
    "AGET_LDOC_SPEC.md": "AGET-LDOC-001",
    "AGET_PROJECT_PLAN_SPEC.md": "AGET-PP-001",
    "AGET_SPEC_FORMAT.md": "AGET-FMT-001",
    "AGET_FILE_NAMING_CONVENTIONS.md": "AGET-NAME-001",
    "AGET_VERSIONING_CONVENTIONS.md": "AGET-VER-001",
    "AGET_DOCUMENTATION_SPEC.md": "AGET-DOC-001",
    "AGET_TOOL_SPEC.md": "AGET-TOOL-001",
}


def get_spec_id(filename: str) -> Optional[str]:
    """Get Spec ID for a given filename."""
    return SPEC_ID_REGISTRY.get(filename)


def parse_header_lines(content: str) -> Tuple[List[str], int, Dict[str, str]]:
    """Parse header from content.

    Returns:
        Tuple of (header_lines, header_end_index, parsed_fields)
    """
    lines = content.split("\n")
    header_lines = []
    header_end = 0
    fields = {}

    in_header = False
    for i, line in enumerate(lines):
        # Title
        if line.startswith("# "):
            in_header = True
            header_lines.append(line)
            fields["Title"] = line[2:].strip()
            continue

        # End of header
        if in_header and line.strip() == "---":
            header_lines.append(line)
            header_end = i + 1
            break

        if in_header:
            header_lines.append(line)
            # Parse field
            match = re.match(r"\*\*([^*]+)\*\*:\s*(.+)", line)
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()

    return header_lines, header_end, fields


def generate_new_header(fields: Dict[str, str], spec_id: Optional[str], filename: str) -> List[str]:
    """Generate standardized header lines."""
    lines = []

    # Title
    title = fields.get("Title", f"AGET {filename.replace('.md', '')} Specification")
    lines.append(f"# {title}")
    lines.append("")

    # Spec ID (if available)
    if spec_id:
        lines.append(f"**Spec ID**: {spec_id}")

    # Required fields
    lines.append(f"**Version**: {fields.get('Version', '1.0.0')}")
    lines.append(f"**Status**: {fields.get('Status', 'Active')}")
    lines.append(f"**Category**: {fields.get('Category', 'Unspecified')}")
    lines.append(f"**Format Version**: {fields.get('Format Version', '1.2')}")
    lines.append(f"**Created**: {fields.get('Created', str(date.today()))}")
    lines.append(f"**Updated**: {fields.get('Updated', str(date.today()))}")
    lines.append(f"**Author**: {fields.get('Author', 'aget-framework')}")

    # Location
    location = fields.get("Location", f"`aget/specs/{filename}`")
    lines.append(f"**Location**: {location}")

    # Optional fields (preserve if present)
    optional_fields = [
        "Change Proposal",
        "Change Origin",
        "Implements",
        "Supersedes",
        "Related Specs",
        "Consolidates",
    ]

    for field in optional_fields:
        if field in fields:
            lines.append(f"**{field}**: {fields[field]}")

    lines.append("")
    lines.append("---")

    return lines


def migrate_spec(path: Path, dry_run: bool = True) -> Tuple[bool, str]:
    """Migrate a single spec file.

    Returns:
        Tuple of (changed, message)
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Could not read: {e}"

    # Skip non-spec files
    if not content.strip().startswith("#"):
        return False, "Not a spec file (no title)"

    # Parse current header
    header_lines, header_end, fields = parse_header_lines(content)

    if header_end == 0:
        return False, "Could not find header end (---)"

    # Get spec ID
    spec_id = get_spec_id(path.name)

    # Check if already has Spec ID
    if "Spec ID" in fields:
        return False, "Already has Spec ID"

    # Generate new header
    new_header_lines = generate_new_header(fields, spec_id, path.name)

    # Get rest of content
    lines = content.split("\n")
    rest_of_content = "\n".join(lines[header_end:])

    # Combine
    new_content = "\n".join(new_header_lines) + "\n" + rest_of_content

    if dry_run:
        return True, f"Would update header (add Spec ID: {spec_id or 'N/A'})"
    else:
        path.write_text(new_content, encoding="utf-8")
        return True, f"Updated header (added Spec ID: {spec_id or 'N/A'})"


def main():
    parser = argparse.ArgumentParser(
        description="Migrate AGET specification headers to v1.2 format"
    )
    parser.add_argument(
        "path",
        help="Spec file or directory to migrate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be changed (default)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually make changes"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()
    path = Path(args.path)

    dry_run = not args.execute

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    if path.is_file():
        changed, message = migrate_spec(path, dry_run)
        mode = "DRY-RUN" if dry_run else "EXECUTE"
        status = "CHANGE" if changed else "SKIP"
        print(f"[{mode}] [{status}] {path.name}: {message}")

    else:
        # Directory
        changed_count = 0
        skipped_count = 0

        spec_files = list(path.glob("*.md"))
        # Also check subdirectories (but not archive)
        for subdir in ["core", "governance", "lifecycle", "technical", "process", "format"]:
            subdir_path = path / subdir
            if subdir_path.exists():
                spec_files.extend(subdir_path.glob("*.md"))

        for spec_file in sorted(spec_files):
            changed, message = migrate_spec(spec_file, dry_run)
            if changed:
                changed_count += 1
                mode = "DRY-RUN" if dry_run else "EXECUTE"
                print(f"[{mode}] [CHANGE] {spec_file.name}: {message}")
            else:
                skipped_count += 1
                if args.verbose:
                    print(f"[SKIP] {spec_file.name}: {message}")

        print(f"\nSummary:")
        print(f"  Changed: {changed_count}")
        print(f"  Skipped: {skipped_count}")

        if dry_run and changed_count > 0:
            print(f"\nRun with --execute to apply changes")


if __name__ == "__main__":
    main()
