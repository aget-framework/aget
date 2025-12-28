#!/usr/bin/env python3
"""
Instantiate Template

Converts an AGET template into a working agent instance.
Creates agent-specific identity, directories, and initial configuration.

Part of AGET v3.0.0-beta.3 - Template UX improvements.

Usage:
    python3 instantiate_template.py --template template-advisor-aget --name my-advisor-AGET
    python3 instantiate_template.py --template template-developer-aget --name project-dev-AGET --persona "Project Developer"
    python3 instantiate_template.py --list  # List available templates

Exit codes:
    0: Success
    1: Error
    2: Invalid arguments
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class TemplateInstantiator:
    """Converts template to agent instance."""

    TEMPLATE_PREFIX = "template-"
    TEMPLATE_SUFFIX = "-aget"
    AGENT_SUFFIX = "-AGET"

    def __init__(self, template_path: Path, agent_name: str, agent_path: Path):
        self.template_path = template_path
        self.agent_name = agent_name
        self.agent_path = agent_path
        self.actions: List[Dict[str, Any]] = []

    def validate_template(self) -> Optional[str]:
        """Validate that source is a valid template."""
        if not self.template_path.exists():
            return f"Template not found: {self.template_path}"

        version_file = self.template_path / ".aget" / "version.json"
        if not version_file.exists():
            return f"Not an AGET template: missing .aget/version.json"

        try:
            with open(version_file) as f:
                version_data = json.load(f)
            if version_data.get("instance_type") != "template":
                return f"Not a template: instance_type is '{version_data.get('instance_type')}'"
        except json.JSONDecodeError as e:
            return f"Invalid version.json: {e}"

        return None

    def validate_agent_name(self) -> Optional[str]:
        """Validate agent name follows conventions."""
        if not self.agent_name.endswith(self.AGENT_SUFFIX):
            return f"Agent name must end with '{self.AGENT_SUFFIX}'"

        if self.agent_path.exists():
            return f"Agent directory already exists: {self.agent_path}"

        return None

    def instantiate(self, persona: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Create agent instance from template."""
        results = {
            "template": self.template_path.name,
            "agent": self.agent_name,
            "path": str(self.agent_path),
            "dry_run": dry_run,
            "actions": [],
            "success": True,
            "error": None
        }

        try:
            # Step 1: Copy template (excluding archive)
            self._copy_template(dry_run)

            # Step 2: Update version.json
            self._update_version_json(dry_run)

            # Step 3: Update identity.json
            self._update_identity_json(persona, dry_run)

            # Step 4: Create session directories
            self._create_session_dirs(dry_run)

            # Step 5: Update manifest.yaml
            self._update_manifest(dry_run)

            # Step 6: Initialize git (optional)
            self._init_git(dry_run)

            results["actions"] = self.actions

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    def _copy_template(self, dry_run: bool):
        """Copy template directory, excluding archive."""
        action = {
            "type": "copy_template",
            "source": str(self.template_path),
            "target": str(self.agent_path),
            "exclude": [".aget/archive/", ".git/", "__pycache__/"]
        }
        self.actions.append(action)

        if not dry_run:
            # Custom copy that excludes certain directories
            self._copy_with_exclusions(
                self.template_path,
                self.agent_path,
                exclude_dirs={".git", "__pycache__", "archive"}
            )

    def _copy_with_exclusions(self, src: Path, dst: Path, exclude_dirs: set):
        """Copy directory tree with exclusions."""
        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            if item.name in exclude_dirs:
                continue
            if item.name.startswith('.') and item.name in {'.git'}:
                continue

            dst_item = dst / item.name

            if item.is_dir():
                # Check for nested exclusions
                if item.name == ".aget":
                    # Special handling for .aget - copy but exclude archive
                    self._copy_with_exclusions(item, dst_item, {"archive"})
                else:
                    shutil.copytree(item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst_item)

    def _update_version_json(self, dry_run: bool):
        """Update version.json for agent instance."""
        version_file = self.agent_path / ".aget" / "version.json"

        action = {
            "type": "update_version_json",
            "path": str(version_file.relative_to(self.agent_path)),
            "changes": {
                "instance_type": "template -> aget",
                "agent_name": self.agent_name,
                "instantiated_from": self.template_path.name,
                "instantiated_date": "today"
            }
        }
        self.actions.append(action)

        if not dry_run:
            with open(version_file) as f:
                data = json.load(f)

            # Update for instance
            data["instance_type"] = "aget"
            data["agent_name"] = self.agent_name
            data["instantiated_from"] = self.template_path.name
            data["instantiated_date"] = datetime.now().strftime("%Y-%m-%d")

            # Add to migration history
            if "migration_history" not in data:
                data["migration_history"] = []
            data["migration_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "action": "instantiated",
                "from_template": self.template_path.name
            })

            with open(version_file, 'w') as f:
                json.dump(data, f, indent=2)

    def _update_identity_json(self, persona: Optional[str], dry_run: bool):
        """Update identity.json for agent instance."""
        identity_file = self.agent_path / ".aget" / "identity.json"

        action = {
            "type": "update_identity_json",
            "path": str(identity_file.relative_to(self.agent_path)),
            "changes": {
                "name": self.agent_name,
                "persona": persona or "(to be configured)"
            }
        }
        self.actions.append(action)

        if not dry_run:
            with open(identity_file) as f:
                data = json.load(f)

            # Update identity
            data["name"] = self.agent_name
            if persona:
                data["persona"] = persona

            # Mark as customizable
            data["_note"] = "Customize this identity for your specific use case"

            with open(identity_file, 'w') as f:
                json.dump(data, f, indent=2)

    def _create_session_dirs(self, dry_run: bool):
        """Create session directories for agent."""
        dirs_to_create = [
            "sessions",
            "knowledge",
            "planning"
        ]

        for dir_name in dirs_to_create:
            dir_path = self.agent_path / dir_name

            if not dir_path.exists():
                action = {
                    "type": "create_directory",
                    "path": dir_name,
                    "purpose": f"Agent {dir_name} storage"
                }
                self.actions.append(action)

                if not dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    # Add .gitkeep
                    (dir_path / ".gitkeep").touch()

    def _update_manifest(self, dry_run: bool):
        """Update manifest.yaml for agent instance."""
        manifest_file = self.agent_path / "manifest.yaml"

        if manifest_file.exists():
            action = {
                "type": "update_manifest",
                "path": "manifest.yaml",
                "changes": ["Update agent name reference"]
            }
            self.actions.append(action)

            if not dry_run:
                with open(manifest_file) as f:
                    content = f.read()

                # Replace template name with agent name
                template_name = self.template_path.name
                content = content.replace(
                    f'name: "{template_name}"',
                    f'name: "{self.agent_name}"'
                )
                content = content.replace(
                    f"name: '{template_name}'",
                    f"name: '{self.agent_name}'"
                )

                with open(manifest_file, 'w') as f:
                    f.write(content)

    def _init_git(self, dry_run: bool):
        """Initialize git repository for agent."""
        action = {
            "type": "git_init",
            "path": str(self.agent_path),
            "note": "Optional: Initialize git repository"
        }
        self.actions.append(action)

        if not dry_run:
            # Don't actually init git - let user decide
            # Just note it in the actions
            pass


def list_templates(framework_path: Path) -> List[str]:
    """List available templates in framework."""
    templates = []
    if not framework_path.exists():
        return templates

    for item in framework_path.iterdir():
        if item.is_dir() and item.name.startswith("template-") and item.name.endswith("-aget"):
            templates.append(item.name)

    return sorted(templates)


def main():
    parser = argparse.ArgumentParser(
        description="Instantiate AGET template as working agent"
    )
    parser.add_argument(
        "--template", "-t",
        help="Template to instantiate (e.g., template-advisor-aget)"
    )
    parser.add_argument(
        "--name", "-n",
        help="Name for new agent (must end with -AGET)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--persona", "-p",
        help="Initial persona description"
    )
    parser.add_argument(
        "--framework",
        help="Path to aget-framework (default: auto-detect)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available templates"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Detect framework path
    framework_path = None
    if args.framework:
        framework_path = Path(args.framework)
    else:
        # Try to find framework relative to script
        script_path = Path(__file__).resolve()
        possible_paths = [
            script_path.parent.parent.parent,  # aget-framework/aget/scripts -> aget-framework
            Path.cwd().parent,
            Path.cwd()
        ]
        for p in possible_paths:
            if (p / "template-worker-aget").exists():
                framework_path = p
                break

    # List mode
    if args.list:
        if not framework_path:
            print("Error: Cannot find aget-framework. Use --framework to specify.", file=sys.stderr)
            sys.exit(2)

        templates = list_templates(framework_path)
        if templates:
            print("Available templates:")
            for t in templates:
                print(f"  {t}")
        else:
            print("No templates found")
        sys.exit(0)

    # Validate required arguments
    if not args.template or not args.name:
        parser.error("--template and --name are required")

    # Resolve paths
    if args.template.startswith("/"):
        template_path = Path(args.template)
    elif framework_path:
        template_path = framework_path / args.template
    else:
        template_path = Path.cwd() / args.template

    output_dir = Path(args.output) if args.output else Path.cwd()
    agent_path = output_dir / args.name

    # Create instantiator
    instantiator = TemplateInstantiator(template_path, args.name, agent_path)

    # Validate
    error = instantiator.validate_template()
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)

    error = instantiator.validate_agent_name()
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)

    # Instantiate
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Instantiating template...")
    print(f"  Template: {template_path.name}")
    print(f"  Agent: {args.name}")
    print(f"  Output: {agent_path}")
    if args.persona:
        print(f"  Persona: {args.persona}")
    print()

    results = instantiator.instantiate(persona=args.persona, dry_run=args.dry_run)

    if results["success"]:
        print("Actions:")
        for action in results["actions"]:
            action_type = action["type"]
            if action_type == "copy_template":
                print(f"  + Copy template (excluding archive)")
            elif action_type == "update_version_json":
                print(f"  * Update .aget/version.json (instance_type: aget)")
            elif action_type == "update_identity_json":
                print(f"  * Update .aget/identity.json (name: {args.name})")
            elif action_type == "create_directory":
                print(f"  + Create {action['path']}/")
            elif action_type == "update_manifest":
                print(f"  * Update manifest.yaml")
            elif action_type == "git_init":
                print(f"  ? Consider: git init (manual)")

            if args.verbose and action_type in ["update_version_json", "update_identity_json"]:
                for key, value in action.get("changes", {}).items():
                    print(f"      {key}: {value}")

        print()
        if args.dry_run:
            print("DRY RUN complete. Use without --dry-run to create agent.")
        else:
            print(f"SUCCESS: Agent created at {agent_path}")
            print()
            print("Next steps:")
            print(f"  1. cd {agent_path}")
            print(f"  2. Edit .aget/identity.json to customize North Star")
            print(f"  3. Edit governance/CHARTER.md for agent-specific charter")
            print(f"  4. git init && git add . && git commit -m 'Initial agent'")
            print(f"  5. Run: python3 -m pytest tests/ -v  # Verify setup")
    else:
        print(f"ERROR: {results['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
