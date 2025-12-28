#!/usr/bin/env python3
"""
Migrate Templates to v3.1

Migrates all templates to AGET_TEMPLATE_SPEC v3.1.0:
- Removes prohibited .aget/memory/ subdirs (domain/, experiential/, organizational/)
- Adds memory config files (layer_config.yaml, inheritance.yaml, retrieval.yaml)
- Ensures core visible directories exist

Part of AGET v3.0.0-beta.3 - B3.8 Template v3.1 Migration.

Usage:
    python3 migrate_templates_to_v3.1.py <framework_path>
    python3 migrate_templates_to_v3.1.py <framework_path> --dry-run
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any


# Memory config templates
LAYER_CONFIG_YAML = """# Memory Layer Configuration
# Per AGET_MEMORY_SPEC v1.2.0 CAP-MEMORY-007

layers:
  working_memory:
    type: ephemeral
    description: "Active context window (LLM context)"

  session_memory:
    type: session
    location: "sessions/"
    description: "Session artifacts, handoffs"

  project_memory:
    type: project
    locations:
      - "governance/"
      - "planning/"
      - "knowledge/"
    description: "KB structure, planning, decisions"

  agent_memory:
    type: agent
    locations:
      - ".aget/"
      - ".aget/evolution/"
    description: "Identity, patterns, learnings"

  fleet_memory:
    type: fleet
    location: "inherited/"
    description: "Fleet-shared knowledge"
    optional: true

  context_optimization:
    type: meta
    description: "Selective loading rules"

# Note: User content goes in VISIBLE directories (governance/, planning/, etc.)
# This file configures memory BEHAVIOR, not content storage
"""

INHERITANCE_YAML = """# Memory Inheritance Configuration
# Per AGET_MEMORY_SPEC v1.2.0

inheritance:
  # What this agent inherits from fleet
  from_fleet:
    patterns: true
    governance_defaults: true
    vocabulary: true

  # What this agent passes to derived agents
  to_derived:
    - governance/CHARTER.md
    - governance/MISSION.md
    - .aget/evolution/L*.md

  # Inheritance override rules
  overrides:
    allow_governance_override: false
    allow_capability_extension: true
"""

RETRIEVAL_YAML = """# Context Retrieval Configuration
# Per AGET_MEMORY_SPEC v1.2.0 CAP-MEMORY-001-06

retrieval:
  # Wake-up context loading
  wake_up:
    priority_order:
      - ".aget/version.json"
      - ".aget/identity.json"
      - "governance/CHARTER.md"
      - "planning/PROJECT_PLAN*.md"
      - ".aget/evolution/L*.md"
    max_files: 10

  # Step-back KB review
  step_back:
    check_directories:
      - "inherited/"
      - "planning/"
      - ".aget/evolution/"
      - "governance/"
    precedent_count: 3

  # Token budget (approximate)
  token_budget:
    wake_up: 4000
    step_back: 8000
    max_context: 100000
"""

# Core visible directories per archetype
CORE_VISIBLE_DIRS = ["governance", "planning"]

# Archetype-specific visible directories
ARCHETYPE_DIRS = {
    "worker": [],
    "advisor": ["sessions"],
    "supervisor": ["sessions", "knowledge"],
    "developer": ["sessions", "knowledge", "products"],
    "consultant": ["sessions", "knowledge"],
    "spec-engineer": ["sessions", "knowledge"],
    "executive": ["sessions", "knowledge"],
    "analyst": ["sessions", "knowledge", "reports"],
    "reviewer": ["sessions", "knowledge"],
    "operator": ["sessions", "knowledge"],
    "architect": ["sessions", "knowledge", "decisions"],
    "researcher": ["sessions", "knowledge"],
}


def migrate_template(template_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Migrate a single template to v3.1."""
    results = {
        "template": template_path.name,
        "actions": [],
        "success": True,
        "error": None
    }

    memory_path = template_path / ".aget" / "memory"

    # Step 1: Remove prohibited subdirectories
    prohibited = ["domain", "experiential", "organizational"]
    for subdir in prohibited:
        subdir_path = memory_path / subdir
        if subdir_path.exists():
            action = f"Remove {subdir_path.relative_to(template_path)}"
            results["actions"].append(action)
            if not dry_run:
                shutil.rmtree(subdir_path)

    # Step 2: Add config files
    config_files = [
        ("layer_config.yaml", LAYER_CONFIG_YAML),
        ("inheritance.yaml", INHERITANCE_YAML),
        ("retrieval.yaml", RETRIEVAL_YAML),
    ]

    for filename, content in config_files:
        file_path = memory_path / filename
        if not file_path.exists():
            action = f"Create {file_path.relative_to(template_path)}"
            results["actions"].append(action)
            if not dry_run:
                memory_path.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)

    # Step 3: Ensure core visible directories exist
    archetype = template_path.name.replace("template-", "").replace("-aget", "")
    visible_dirs = CORE_VISIBLE_DIRS + ARCHETYPE_DIRS.get(archetype, [])

    for dir_name in visible_dirs:
        dir_path = template_path / dir_name
        if not dir_path.exists():
            action = f"Create {dir_name}/"
            results["actions"].append(action)
            if not dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                # Add .gitkeep
                (dir_path / ".gitkeep").touch()

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Migrate templates to AGET_TEMPLATE_SPEC v3.1.0"
    )
    parser.add_argument(
        "framework_path",
        help="Path to aget-framework directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--template", "-t",
        help="Migrate specific template only"
    )

    args = parser.parse_args()

    framework_path = Path(args.framework_path)
    if not framework_path.is_absolute():
        framework_path = Path.cwd() / framework_path

    if not framework_path.exists():
        print(f"Error: Framework path not found: {framework_path}", file=sys.stderr)
        sys.exit(2)

    # Find templates
    if args.template:
        templates = [framework_path / args.template]
    else:
        templates = sorted([
            p for p in framework_path.iterdir()
            if p.is_dir() and p.name.startswith("template-") and p.name.endswith("-aget")
        ])

    if not templates:
        print("No templates found")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Migrating {len(templates)} templates to v3.1")
    print("=" * 60)
    print()

    total_actions = 0

    for template_path in templates:
        if not template_path.exists():
            print(f"Skipping {template_path.name}: not found")
            continue

        results = migrate_template(template_path, dry_run=args.dry_run)

        if results["actions"]:
            print(f"{template_path.name}:")
            for action in results["actions"]:
                print(f"  {action}")
            total_actions += len(results["actions"])
        else:
            print(f"{template_path.name}: Already v3.1 compliant")
        print()

    print("=" * 60)
    print(f"Total actions: {total_actions}")

    if args.dry_run:
        print()
        print("DRY RUN complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
