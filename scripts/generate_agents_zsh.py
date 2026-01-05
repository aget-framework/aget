#!/usr/bin/env python3
"""
Generate ~/.aget/agents.zsh from fleet inventory.

Creates shell aliases for all agents in a fleet, organized by portfolio.

Usage:
    python3 generate_agents_zsh.py --fleet FLEET_STATE.yaml --output ~/.aget/agents.zsh
    python3 generate_agents_zsh.py --scan ~/github --output ~/.aget/agents.zsh

Requirements: R-CLI-GEN-001
Related: L452 (Shell Orchestration Pattern)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Optional: YAML support for fleet file parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def scan_for_agents(base_dir: Path) -> list[dict]:
    """
    Scan directory tree for AGET agents.

    Looks for directories containing AGENTS.md files.
    Returns list of {"name": str, "path": str, "portfolio": str}
    """
    agents = []
    base_dir = Path(base_dir).expanduser().resolve()

    if not base_dir.exists():
        print(f"WARN: Directory not found: {base_dir}", file=sys.stderr)
        return agents

    # Find all AGENTS.md files
    for agents_md in base_dir.rglob("AGENTS.md"):
        agent_dir = agents_md.parent

        # Skip if in .git or node_modules
        if ".git" in agent_dir.parts or "node_modules" in agent_dir.parts:
            continue

        # Derive name from directory
        name = agent_dir.name

        # Clean up common prefixes/suffixes
        for prefix in ["private-", "template-"]:
            if name.startswith(prefix):
                name = name[len(prefix):]
        for suffix in ["-aget", "-AGET"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)]

        # Convert to lowercase and replace underscores/spaces
        alias_name = name.lower().replace("_", "-").replace(" ", "-")

        # Infer portfolio from path
        portfolio = "main"
        path_str = str(agent_dir)
        if "GM-CCB" in path_str:
            portfolio = "ccb"
        elif "GM-LEGALON" in path_str:
            portfolio = "legalon"
        elif "GM-RKB" in path_str:
            portfolio = "rkb"
        elif "GM-PREDICTIONWORKS" in path_str:
            portfolio = "predictionworks"
        elif "aget-framework" in path_str:
            portfolio = "framework"

        agents.append({
            "name": alias_name,
            "path": str(agent_dir),
            "portfolio": portfolio,
            "full_name": agent_dir.name
        })

    return agents


def load_fleet_yaml(fleet_file: Path) -> list[dict]:
    """
    Load agent list from FLEET_STATE.yaml or similar.

    Expected format:
    agents:
      - name: supervisor
        path: ~/github/private-supervisor-AGET
        portfolio: main
    """
    if not HAS_YAML:
        print("ERROR: PyYAML required for --fleet option. Install with: pip install pyyaml",
              file=sys.stderr)
        sys.exit(1)

    fleet_file = Path(fleet_file).expanduser()
    if not fleet_file.exists():
        print(f"ERROR: Fleet file not found: {fleet_file}", file=sys.stderr)
        sys.exit(1)

    with open(fleet_file) as f:
        data = yaml.safe_load(f)

    agents = []
    for agent in data.get("agents", []):
        agents.append({
            "name": agent.get("name", agent.get("alias", "unknown")),
            "path": agent.get("path", agent.get("directory", "")),
            "portfolio": agent.get("portfolio", "main"),
            "full_name": agent.get("full_name", agent.get("name", ""))
        })

    return agents


def generate_zsh(agents: list[dict], output_file: Path = None) -> str:
    """
    Generate zsh alias file content.
    """
    lines = [
        "# AGET Agent Aliases",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Agents: {len(agents)}",
        "#",
        "# Usage: <alias> [focus topic]",
        "# Example: supervisor \"fix the bug\"",
        "",
    ]

    # Group by portfolio
    portfolios: dict[str, list] = {}
    for agent in agents:
        portfolio = agent.get("portfolio", "main")
        if portfolio not in portfolios:
            portfolios[portfolio] = []
        portfolios[portfolio].append(agent)

    # Sort portfolios (framework and main first, then alphabetical)
    portfolio_order = ["framework", "main"] + sorted(
        [p for p in portfolios.keys() if p not in ["framework", "main"]]
    )

    for portfolio in portfolio_order:
        if portfolio not in portfolios:
            continue

        agents_in_portfolio = sorted(portfolios[portfolio], key=lambda a: a["name"])

        lines.append(f"# {'━' * 70}")
        lines.append(f"# Portfolio: {portfolio.upper()}")
        lines.append(f"# {'━' * 70}")

        for agent in agents_in_portfolio:
            name = agent["name"]
            path = agent["path"]

            # Expand ~ for display but keep it in alias
            if path.startswith(os.path.expanduser("~")):
                path = "~" + path[len(os.path.expanduser("~")):]

            lines.append(f"alias {name}='aget {path}'")

        lines.append("")

    content = "\n".join(lines)

    if output_file:
        output_file = Path(output_file).expanduser()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(content)
        print(f"Generated: {output_file} ({len(agents)} agents)", file=sys.stderr)

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Generate ~/.aget/agents.zsh from fleet inventory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan directories for agents
  python3 generate_agents_zsh.py --scan ~/github --output ~/.aget/agents.zsh

  # Use fleet inventory file
  python3 generate_agents_zsh.py --fleet ~/github/supervisor/FLEET_STATE.yaml

  # Preview without writing
  python3 generate_agents_zsh.py --scan ~/github
        """
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--fleet",
        type=str,
        help="Path to FLEET_STATE.yaml or similar inventory file"
    )
    source_group.add_argument(
        "--scan",
        type=str,
        help="Base directory to scan for agents (looks for AGENTS.md files)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--include-templates",
        action="store_true",
        help="Include template-* directories in scan"
    )

    args = parser.parse_args()

    # Load agents
    if args.fleet:
        agents = load_fleet_yaml(args.fleet)
    else:
        agents = scan_for_agents(args.scan)
        if not args.include_templates:
            agents = [a for a in agents if not a["full_name"].startswith("template-")]

    if not agents:
        print("WARN: No agents found", file=sys.stderr)
        sys.exit(0)

    # Generate output
    content = generate_zsh(agents, args.output)

    if not args.output:
        print(content)


if __name__ == "__main__":
    main()
