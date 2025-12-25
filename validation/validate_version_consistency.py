#!/usr/bin/env python3
"""
Validate version consistency between version.json and AGENTS.md

Per L366: AGENTS.md is the runtime source of truth for Claude Code.
version.json and AGENTS.md must have matching versions.

Usage:
    python3 validate_version_consistency.py /path/to/agent
    python3 validate_version_consistency.py /path/to/agent1 /path/to/agent2 ...
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, List


def extract_agents_md_version(agents_md_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract @aget-version tag and project context version from AGENTS.md"""
    if not agents_md_path.exists():
        return None, None

    content = agents_md_path.read_text()

    # Extract @aget-version tag (usually line 3)
    tag_match = re.search(r'@aget-version:\s*(\d+\.\d+\.\d+)', content)
    tag_version = tag_match.group(1) if tag_match else None

    # Extract version from project context (e.g., "agent-name - Description - v2.12.0")
    context_match = re.search(r'-\s*v(\d+\.\d+\.\d+)\s*$', content, re.MULTILINE)
    context_version = context_match.group(1) if context_match else None

    return tag_version, context_version


def extract_version_json_version(version_json_path: Path) -> Optional[str]:
    """Extract aget_version from version.json"""
    if not version_json_path.exists():
        return None

    try:
        data = json.loads(version_json_path.read_text())
        return data.get('aget_version')
    except json.JSONDecodeError:
        return None


def validate_agent(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate version consistency for a single agent"""
    errors = []

    version_json_path = agent_path / '.aget' / 'version.json'
    agents_md_path = agent_path / 'AGENTS.md'
    claude_md_path = agent_path / 'CLAUDE.md'

    # Check files exist
    if not version_json_path.exists():
        errors.append(f"Missing: .aget/version.json")
        return False, errors

    if not agents_md_path.exists():
        errors.append(f"Missing: AGENTS.md")
        return False, errors

    # Extract versions
    json_version = extract_version_json_version(version_json_path)
    tag_version, context_version = extract_agents_md_version(agents_md_path)

    if not json_version:
        errors.append(f"Missing 'aget_version' in version.json")

    if not tag_version:
        errors.append(f"Missing '@aget-version' tag in AGENTS.md")

    # Compare versions
    if json_version and tag_version and json_version != tag_version:
        errors.append(
            f"Version mismatch: version.json has '{json_version}' "
            f"but AGENTS.md @aget-version has '{tag_version}'"
        )

    if tag_version and context_version and tag_version != context_version:
        errors.append(
            f"AGENTS.md internal mismatch: @aget-version is '{tag_version}' "
            f"but project context shows 'v{context_version}'"
        )

    # Check CLAUDE.md symlink
    if claude_md_path.exists():
        if not claude_md_path.is_symlink():
            errors.append("CLAUDE.md exists but is not a symlink to AGENTS.md")
        elif claude_md_path.resolve() != agents_md_path.resolve():
            errors.append("CLAUDE.md symlink does not point to AGENTS.md")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_version_consistency.py <agent_path> [agent_path2 ...]")
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
    print(f"{total_valid}/{total_valid + total_invalid} agents have consistent versions")

    sys.exit(0 if total_invalid == 0 else 1)


if __name__ == '__main__':
    main()
