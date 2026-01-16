"""
CLI Verification Test Framework - Shared Fixtures

Provides common fixtures for validating AGET operations across
multiple CLI agents (Claude Code, Codex CLI, Gemini CLI).

Version: 1.0.0
Implements: PROJECT_PLAN_cli_independence_validation_v1.0
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import pytest

# Path to this test directory
TEST_DIR = Path(__file__).parent
CLI_VERSIONS_FILE = TEST_DIR / "cli_versions.json"


def get_cli_version(cli_name: str) -> Optional[str]:
    """Get installed version of a CLI tool."""
    commands = {
        "claude_code": ["claude", "--version"],
        "codex_cli": ["codex", "--version"],
        "gemini_cli": ["gemini", "--version"],
    }

    if cli_name not in commands:
        return None

    try:
        result = subprocess.run(
            commands[cli_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Parse version from output
            output = result.stdout.strip()
            # Handle different version output formats
            if "Claude Code" in output:
                # "2.1.9 (Claude Code)" -> "2.1.9"
                return output.split()[0]
            elif "codex-cli" in output:
                # "codex-cli 0.77.0" -> "0.77.0"
                return output.split()[-1]
            else:
                # Generic: take last word
                return output.split()[-1]
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def is_cli_available(cli_name: str) -> bool:
    """Check if a CLI tool is installed and available."""
    return get_cli_version(cli_name) is not None


@pytest.fixture(scope="session")
def cli_versions():
    """Load CLI versions configuration."""
    with open(CLI_VERSIONS_FILE) as f:
        return json.load(f)


@pytest.fixture
def test_agent_dir(tmp_path):
    """
    Create a temporary AGET agent directory with minimal structure.

    Structure:
        tmp_path/
        ├── AGENTS.md
        ├── .aget/
        │   ├── version.json
        │   ├── identity.json
        │   └── patterns/
        │       └── session/
        │           ├── wake_up.py
        │           └── wind_down.py
        └── governance/
    """
    # Create directory structure
    aget_dir = tmp_path / ".aget"
    patterns_dir = aget_dir / "patterns" / "session"
    governance_dir = tmp_path / "governance"

    aget_dir.mkdir()
    patterns_dir.mkdir(parents=True)
    governance_dir.mkdir()

    # Create AGENTS.md
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(MINIMAL_AGENTS_MD)

    # Create version.json
    version_json = aget_dir / "version.json"
    version_json.write_text(json.dumps({
        "name": "test-agent",
        "version": "0.1.0",
        "instance_type": "aget"
    }, indent=2))

    # Create identity.json
    identity_json = aget_dir / "identity.json"
    identity_json.write_text(json.dumps({
        "north_star": "Test agent for CLI verification"
    }, indent=2))

    # Create minimal wake_up.py
    wake_up = patterns_dir / "wake_up.py"
    wake_up.write_text(MINIMAL_WAKE_UP_SCRIPT)

    # Create minimal wind_down.py
    wind_down = patterns_dir / "wind_down.py"
    wind_down.write_text(MINIMAL_WIND_DOWN_SCRIPT)

    return tmp_path


@pytest.fixture
def agents_md_content():
    """Return standard AGENTS.md content for testing."""
    return MINIMAL_AGENTS_MD


@pytest.fixture
def wake_up_script(test_agent_dir):
    """Return path to wake_up.py in test agent directory."""
    return test_agent_dir / ".aget" / "patterns" / "session" / "wake_up.py"


@pytest.fixture
def wind_down_script(test_agent_dir):
    """Return path to wind_down.py in test agent directory."""
    return test_agent_dir / ".aget" / "patterns" / "session" / "wind_down.py"


# Skip markers for CLI availability
skip_if_no_claude = pytest.mark.skipif(
    not is_cli_available("claude_code"),
    reason="Claude Code not installed"
)

skip_if_no_codex = pytest.mark.skipif(
    not is_cli_available("codex_cli"),
    reason="Codex CLI not installed"
)

skip_if_no_gemini = pytest.mark.skipif(
    not is_cli_available("gemini_cli"),
    reason="Gemini CLI not installed"
)


# --- Minimal test content ---

MINIMAL_AGENTS_MD = """# Agent Configuration

@aget-version: 3.4.0

## North Star

> **Purpose**: Test agent for CLI verification

See: `.aget/identity.json`

## Session Protocol

### Wake Up Protocol
When user says "wake up":
1. Execute `python3 .aget/patterns/session/wake_up.py`
2. Display: "Test agent ready"

### Wind Down Protocol
When user says "wind down":
1. Execute `python3 .aget/patterns/session/wind_down.py`
2. Display: "Test agent closing"

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Identity | `.aget/identity.json` | Agent purpose |
| Version | `.aget/version.json` | Agent version |
"""

MINIMAL_WAKE_UP_SCRIPT = '''#!/usr/bin/env python3
"""Minimal wake_up.py for CLI verification testing."""

import json
from pathlib import Path

def main():
    # Read identity
    identity_path = Path(__file__).parent.parent.parent / "identity.json"
    if identity_path.exists():
        with open(identity_path) as f:
            identity = json.load(f)
        purpose = identity.get("north_star", "Unknown")
    else:
        purpose = "Identity file not found"

    # Output
    print("**Session: test-agent**")
    print(f"Purpose: {purpose}")
    print("Ready.")

if __name__ == "__main__":
    main()
'''

MINIMAL_WIND_DOWN_SCRIPT = '''#!/usr/bin/env python3
"""Minimal wind_down.py for CLI verification testing."""

def main():
    print("**Session Closing: test-agent**")
    print("No pending work.")
    print("Clean close.")

if __name__ == "__main__":
    main()
'''
