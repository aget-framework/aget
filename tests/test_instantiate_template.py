"""
Unit tests for instantiate_template.py

Tests suffix validation, symlink creation, session script deployment,
and archetype skill validation.

References: L480 (write scope), SOP_aget_create G3
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from instantiate_template import TemplateInstantiator, list_templates


@pytest.fixture
def temp_framework(tmp_path):
    """Create a minimal framework structure for testing."""
    # Create a template
    template_dir = tmp_path / "template-worker-aget"
    template_dir.mkdir()

    # .aget/version.json
    aget_dir = template_dir / ".aget"
    aget_dir.mkdir()
    version_data = {
        "aget_version": "3.6.0",
        "agent_name": "template-worker-aget",
        "instance_type": "template"
    }
    (aget_dir / "version.json").write_text(json.dumps(version_data))

    # .aget/identity.json
    identity_data = {
        "name": "template-worker-aget",
        "north_star": {"statement": "Template purpose"}
    }
    (aget_dir / "identity.json").write_text(json.dumps(identity_data))

    # AGENTS.md
    (template_dir / "AGENTS.md").write_text("# Agent Config\n")

    # .claude/skills/ with a test skill
    skills_dir = template_dir / ".claude" / "skills" / "aget-wake-up"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# wake-up skill\n")

    # Create canonical scripts in aget/scripts/
    scripts_dir = tmp_path / "aget" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "wake_up.py").write_text("# wake up script\n")
    (scripts_dir / "wind_down.py").write_text("# wind down script\n")

    return tmp_path


class TestSuffixValidation:
    """Test L480 two-tier write scope suffix validation."""

    def test_lowercase_aget_accepted(self, temp_framework):
        """Lowercase -aget suffix should be accepted (internal KB agents)."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "my-worker-aget"
        inst = TemplateInstantiator(template_path, "my-worker-aget", agent_path)
        assert inst.validate_agent_name() is None

    def test_uppercase_aget_accepted(self, temp_framework):
        """Uppercase -AGET suffix should be accepted (external system agents)."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "my-worker-AGET"
        inst = TemplateInstantiator(template_path, "my-worker-AGET", agent_path)
        assert inst.validate_agent_name() is None

    def test_invalid_suffix_rejected(self, temp_framework):
        """Invalid suffix should be rejected with clear error."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "my-worker-invalid"
        inst = TemplateInstantiator(template_path, "my-worker-invalid", agent_path)
        error = inst.validate_agent_name()
        assert error is not None
        assert "-aget" in error
        assert "-AGET" in error

    def test_existing_directory_rejected(self, temp_framework):
        """Existing agent directory should be rejected."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "existing-aget"
        agent_path.mkdir()
        inst = TemplateInstantiator(template_path, "existing-aget", agent_path)
        error = inst.validate_agent_name()
        assert error is not None
        assert "already exists" in error


class TestInstanceType:
    """Test instance type derivation from suffix."""

    def test_lowercase_gives_aget_type(self, temp_framework):
        """Lowercase -aget suffix should produce instance_type 'aget'."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "my-worker-aget"
        inst = TemplateInstantiator(template_path, "my-worker-aget", agent_path)
        assert inst._get_instance_type() == "aget"

    def test_uppercase_gives_AGET_type(self, temp_framework):
        """Uppercase -AGET suffix should produce instance_type 'AGET'."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "my-worker-AGET"
        inst = TemplateInstantiator(template_path, "my-worker-AGET", agent_path)
        assert inst._get_instance_type() == "AGET"


class TestSymlinkCreation:
    """Test CLAUDE.md -> AGENTS.md symlink (SOP G3.6)."""

    def test_symlink_created(self, temp_framework):
        """Symlink should be created when AGENTS.md exists."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "test-worker-aget"
        inst = TemplateInstantiator(template_path, "test-worker-aget", agent_path)
        inst.instantiate(dry_run=False)

        claude_md = agent_path / "CLAUDE.md"
        assert claude_md.is_symlink()
        assert os.readlink(str(claude_md)) == "AGENTS.md"

    def test_symlink_in_dry_run(self, temp_framework):
        """Symlink should NOT be created in dry-run mode."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "test-worker-aget"
        inst = TemplateInstantiator(template_path, "test-worker-aget", agent_path)
        inst.instantiate(dry_run=True)

        claude_md = agent_path / "CLAUDE.md"
        assert not claude_md.exists()


class TestSessionScriptDeployment:
    """Test session script deployment (SOP G3.7)."""

    def test_scripts_deployed(self, temp_framework):
        """Session scripts should be copied from aget/scripts/."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "test-worker-aget"
        inst = TemplateInstantiator(template_path, "test-worker-aget", agent_path)
        inst.instantiate(dry_run=False)

        scripts_dir = agent_path / "scripts"
        assert (scripts_dir / "wake_up.py").exists()
        assert (scripts_dir / "wind_down.py").exists()

    def test_scripts_not_deployed_in_dry_run(self, temp_framework):
        """Scripts should NOT be deployed in dry-run mode."""
        template_path = temp_framework / "template-worker-aget"
        agent_path = temp_framework / "test-worker-aget"
        inst = TemplateInstantiator(template_path, "test-worker-aget", agent_path)
        inst.instantiate(dry_run=True)

        scripts_dir = agent_path / "scripts"
        assert not scripts_dir.exists()


class TestListTemplates:
    """Test template listing."""

    def test_finds_templates(self, temp_framework):
        """Should find templates matching template-*-aget pattern."""
        templates = list_templates(temp_framework)
        assert "template-worker-aget" in templates

    def test_nonexistent_path(self, tmp_path):
        """Should return empty list for non-existent path."""
        templates = list_templates(tmp_path / "nonexistent")
        assert templates == []
