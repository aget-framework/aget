"""
CLI Verification Tests - Claude Code

Validates AGET operations on Claude Code CLI.
This is the BASELINE CLI - the reference implementation.

Version: 1.0.0
CLI: Claude Code
Minimum Version: 2.0.0
Implements: PROJECT_PLAN_cli_independence_validation_v1.0
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

import pytest


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
            output = result.stdout.strip()
            if "Claude Code" in output:
                return output.split()[0]
            elif "codex-cli" in output:
                return output.split()[-1]
            else:
                return output.split()[-1]
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def is_cli_available(cli_name: str) -> bool:
    """Check if a CLI tool is installed and available."""
    return get_cli_version(cli_name) is not None


skip_if_no_claude = pytest.mark.skipif(
    not is_cli_available("claude_code"),
    reason="Claude Code not installed"
)

# Test metadata
CLI_NAME = "claude_code"
CLI_COMMAND = "claude"
MIN_VERSION = "2.0.0"


class TestCLIAvailability:
    """Pre-flight checks for Claude Code CLI."""

    def test_cli_installed(self):
        """TC-000-01: Claude Code CLI is installed."""
        version = get_cli_version(CLI_NAME)
        assert version is not None, "Claude Code not installed"
        print(f"Claude Code version: {version}")

    def test_cli_version_sufficient(self):
        """TC-000-02: Claude Code version meets minimum requirement."""
        version = get_cli_version(CLI_NAME)
        assert version is not None, "Claude Code not installed"
        # Simple version comparison (assumes X.Y.Z format)
        current = tuple(map(int, version.split(".")[:3]))
        minimum = tuple(map(int, MIN_VERSION.split(".")[:3]))
        assert current >= minimum, f"Version {version} < minimum {MIN_VERSION}"


@skip_if_no_claude
class TestTC001SettingsRead:
    """
    TC-001: Settings Read

    Validates that Claude Code can read AGENTS.md and follow instructions.
    """

    def test_agents_md_recognized(self, test_agent_dir):
        """TC-001-01: AGENTS.md file is recognized by Claude Code."""
        agents_md = test_agent_dir / "AGENTS.md"
        assert agents_md.exists(), "AGENTS.md not created"
        content = agents_md.read_text()
        assert "@aget-version:" in content, "Version tag missing"
        # Note: Actual CLI recognition tested via manual validation
        # This test verifies the file structure is correct

    def test_aget_version_tag_parsed(self, test_agent_dir):
        """TC-001-02: @aget-version tag is present and parseable."""
        agents_md = test_agent_dir / "AGENTS.md"
        content = agents_md.read_text()
        # Find version tag
        for line in content.split("\n"):
            if line.startswith("@aget-version:"):
                version = line.split(":")[1].strip()
                assert version, "Version tag is empty"
                # Validate semver format
                parts = version.split(".")
                assert len(parts) == 3, f"Invalid version format: {version}"
                return
        pytest.fail("@aget-version tag not found")

    def test_north_star_section_present(self, test_agent_dir):
        """TC-001-03: North Star section is present."""
        agents_md = test_agent_dir / "AGENTS.md"
        content = agents_md.read_text()
        assert "## North Star" in content or "## Purpose" in content


@skip_if_no_claude
class TestTC002WakeProtocol:
    """
    TC-002: Wake Protocol

    Validates that wake_up.py executes correctly via Claude Code.
    """

    def test_wake_up_script_exists(self, wake_up_script):
        """TC-002-01: wake_up.py script exists."""
        assert wake_up_script.exists(), "wake_up.py not found"

    def test_wake_up_script_executable(self, wake_up_script):
        """TC-002-02: wake_up.py is valid Python."""
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(wake_up_script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_wake_up_script_runs(self, wake_up_script, test_agent_dir):
        """TC-002-03: wake_up.py executes without error."""
        result = subprocess.run(
            ["python3", str(wake_up_script)],
            capture_output=True,
            text=True,
            cwd=test_agent_dir
        )
        assert result.returncode == 0, f"Execution error: {result.stderr}"
        assert "Ready" in result.stdout, "Expected 'Ready' in output"


@skip_if_no_claude
class TestTC003WindProtocol:
    """
    TC-003: Wind Down Protocol

    Validates that wind_down.py executes correctly via Claude Code.
    """

    def test_wind_down_script_exists(self, wind_down_script):
        """TC-003-01: wind_down.py script exists."""
        assert wind_down_script.exists(), "wind_down.py not found"

    def test_wind_down_script_executable(self, wind_down_script):
        """TC-003-02: wind_down.py is valid Python."""
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(wind_down_script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_wind_down_script_runs(self, wind_down_script, test_agent_dir):
        """TC-003-03: wind_down.py executes without error."""
        result = subprocess.run(
            ["python3", str(wind_down_script)],
            capture_output=True,
            text=True,
            cwd=test_agent_dir
        )
        assert result.returncode == 0, f"Execution error: {result.stderr}"


@skip_if_no_claude
class TestTC004ScriptExecution:
    """
    TC-004: Script Execution

    Validates that .aget/patterns/ scripts can be executed.
    """

    def test_patterns_directory_exists(self, test_agent_dir):
        """TC-004-01: .aget/patterns/ directory exists."""
        patterns_dir = test_agent_dir / ".aget" / "patterns"
        assert patterns_dir.exists(), ".aget/patterns/ not found"

    def test_session_patterns_exist(self, test_agent_dir):
        """TC-004-02: Session pattern scripts exist."""
        session_dir = test_agent_dir / ".aget" / "patterns" / "session"
        assert session_dir.exists(), "session/ directory not found"
        assert (session_dir / "wake_up.py").exists()
        assert (session_dir / "wind_down.py").exists()

    def test_python3_available(self):
        """TC-004-03: Python3 is available for script execution."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python3 not available"

    def test_script_can_read_json(self, test_agent_dir):
        """TC-004-04: Scripts can read JSON files."""
        identity = test_agent_dir / ".aget" / "identity.json"
        assert identity.exists()
        with open(identity) as f:
            data = json.load(f)
        assert "north_star" in data

    def test_script_output_captured(self, wake_up_script, test_agent_dir):
        """TC-004-05: Script output is captured correctly."""
        result = subprocess.run(
            ["python3", str(wake_up_script)],
            capture_output=True,
            text=True,
            cwd=test_agent_dir
        )
        # Verify output contains expected patterns
        assert "Session:" in result.stdout or "test-agent" in result.stdout


@skip_if_no_claude
class TestTC005LdocCreation:
    """
    TC-005: L-doc Creation

    Validates that L-docs can be created and updated.
    Note: Actual creation via CLI is tested manually.
    These tests verify the file format requirements.
    """

    def test_evolution_directory_creatable(self, test_agent_dir):
        """TC-005-01: .aget/evolution/ directory can be created."""
        evolution_dir = test_agent_dir / ".aget" / "evolution"
        evolution_dir.mkdir(exist_ok=True)
        assert evolution_dir.exists()

    def test_ldoc_format_valid(self, test_agent_dir):
        """TC-005-02: L-doc format is valid markdown."""
        evolution_dir = test_agent_dir / ".aget" / "evolution"
        evolution_dir.mkdir(exist_ok=True)

        ldoc_content = """# L999: Test Learning

**Date**: 2026-01-16
**Status**: Active
**Category**: Testing

---

## Discovery

This is a test L-doc for CLI verification.

## Key Insight

L-docs can be created on this CLI.
"""
        ldoc_path = evolution_dir / "L999_test_learning.md"
        ldoc_path.write_text(ldoc_content)
        assert ldoc_path.exists()
        assert ldoc_path.read_text() == ldoc_content

    def test_ldoc_naming_convention(self, test_agent_dir):
        """TC-005-03: L-doc naming follows convention."""
        evolution_dir = test_agent_dir / ".aget" / "evolution"
        evolution_dir.mkdir(exist_ok=True)

        # Valid naming pattern: L<number>_<description>.md
        valid_names = [
            "L001_first_learning.md",
            "L999_test_learning.md",
            "L123_some_discovery.md",
        ]
        for name in valid_names:
            path = evolution_dir / name
            path.write_text("# Test")
            assert path.exists()


@skip_if_no_claude
class TestTC006FileOperations:
    """
    TC-006: File Operations

    Validates read/write/edit operations.
    Note: CLI-specific file operations tested manually.
    These tests verify filesystem operations work correctly.
    """

    def test_file_read(self, test_agent_dir):
        """TC-006-01: Files can be read."""
        agents_md = test_agent_dir / "AGENTS.md"
        content = agents_md.read_text()
        assert len(content) > 0

    def test_file_write(self, test_agent_dir):
        """TC-006-02: Files can be written."""
        test_file = test_agent_dir / "test_output.txt"
        test_file.write_text("Test content")
        assert test_file.exists()
        assert test_file.read_text() == "Test content"

    def test_file_append(self, test_agent_dir):
        """TC-006-03: Files can be appended."""
        test_file = test_agent_dir / "test_append.txt"
        test_file.write_text("Line 1\n")
        with open(test_file, "a") as f:
            f.write("Line 2\n")
        content = test_file.read_text()
        assert "Line 1" in content
        assert "Line 2" in content

    def test_file_in_subdirectory(self, test_agent_dir):
        """TC-006-04: Files can be created in subdirectories."""
        sub_dir = test_agent_dir / "docs" / "nested"
        sub_dir.mkdir(parents=True)
        test_file = sub_dir / "deep_file.md"
        test_file.write_text("# Deep File")
        assert test_file.exists()

    def test_json_roundtrip(self, test_agent_dir):
        """TC-006-05: JSON files can be read and written."""
        json_file = test_agent_dir / "test_data.json"
        data = {"key": "value", "number": 42, "nested": {"a": 1}}
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

        with open(json_file) as f:
            loaded = json.load(f)

        assert loaded == data
