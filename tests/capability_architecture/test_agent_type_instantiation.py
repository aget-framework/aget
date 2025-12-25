"""
Tests for AGET Agent Type Instantiation

These tests verify that the 6 defined agent types can be properly
instantiated from base templates and capabilities.

Agent Types (from L330):
1. Data Science Aget
2. Executive Advisor Aget
3. Specification Owner Aget
4. Software Development Owner Aget
5. Knowledge Owner Aget
6. Research Advisor Aget
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'validation'))
from validate_template_manifest import TemplateManifestValidator
from validate_composition import CompositionValidator


@pytest.fixture
def manifest_validator():
    """Create manifest validator."""
    return TemplateManifestValidator()


@pytest.fixture
def composition_validator():
    """Create composition validator."""
    return CompositionValidator()


def create_manifest(name: str, agent_type: str, base_template: str, capabilities: list) -> dict:
    """Helper to create a manifest dict."""
    return {
        'apiVersion': 'aget.framework/v1',
        'kind': 'TemplateManifest',
        'metadata': {
            'name': name,
            'version': '1.0.0',
            'agent_type': agent_type,
            'description': f'{agent_type} manifest'
        },
        'composition': {
            'base_template': base_template,
            'capabilities': [{'name': c, 'version': '1.0.0'} for c in capabilities],
            'composition_rules': {
                'conflict_resolution': 'error'
            }
        }
    }


class TestDataScienceAget:
    """Tests for Data Science Aget instantiation."""

    def test_data_science_aget_composes(self, manifest_validator):
        """Data Science Aget should compose from advisor + domain-knowledge + structured-outputs."""
        manifest = create_manifest(
            name='data-science-aget',
            agent_type='Data Science Aget',
            base_template='advisor',
            capabilities=['domain-knowledge', 'structured-outputs', 'memory-management']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Data Science Aget failed: {result.errors}"
            os.unlink(f.name)

    def test_data_science_aget_has_required_capabilities(self):
        """Data Science Aget requires domain-knowledge and structured-outputs."""
        manifest = create_manifest(
            name='data-science-aget',
            agent_type='Data Science Aget',
            base_template='advisor',
            capabilities=['domain-knowledge', 'structured-outputs']
        )

        caps = {c['name'] for c in manifest['composition']['capabilities']}
        assert 'domain-knowledge' in caps
        assert 'structured-outputs' in caps


class TestExecutiveAdvisorAget:
    """Tests for Executive Advisor Aget instantiation."""

    def test_executive_advisor_aget_composes(self, manifest_validator):
        """Executive Advisor Aget should compose from advisor + org-kb."""
        manifest = create_manifest(
            name='executive-advisor-aget',
            agent_type='Executive Advisor Aget',
            base_template='advisor',
            capabilities=['org-kb', 'memory-management', 'collaboration']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Executive Advisor Aget failed: {result.errors}"
            os.unlink(f.name)

    def test_executive_advisor_aget_has_org_kb(self):
        """Executive Advisor Aget requires org-kb capability."""
        manifest = create_manifest(
            name='executive-advisor-aget',
            agent_type='Executive Advisor Aget',
            base_template='advisor',
            capabilities=['org-kb', 'memory-management']
        )

        caps = {c['name'] for c in manifest['composition']['capabilities']}
        assert 'org-kb' in caps


class TestSpecificationOwnerAget:
    """Tests for Specification Owner Aget instantiation."""

    def test_specification_owner_aget_composes(self, manifest_validator):
        """Specification Owner Aget should compose from spec-engineer + structured-outputs."""
        manifest = create_manifest(
            name='specification-owner-aget',
            agent_type='Specification Owner Aget',
            base_template='spec-engineer',
            capabilities=['structured-outputs', 'domain-knowledge', 'memory-management']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Specification Owner Aget failed: {result.errors}"
            os.unlink(f.name)


class TestSoftwareDevOwnerAget:
    """Tests for Software Development Owner Aget instantiation."""

    def test_software_dev_owner_aget_composes(self, manifest_validator):
        """Software Dev Owner Aget should compose from developer + domain-knowledge."""
        manifest = create_manifest(
            name='software-dev-owner-aget',
            agent_type='Software Development Owner Aget',
            base_template='developer',
            capabilities=['domain-knowledge', 'collaboration', 'memory-management']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Software Dev Owner Aget failed: {result.errors}"
            os.unlink(f.name)


class TestKnowledgeOwnerAget:
    """Tests for Knowledge Owner Aget instantiation."""

    def test_knowledge_owner_aget_composes(self, manifest_validator):
        """Knowledge Owner Aget should compose from advisor + memory-management."""
        manifest = create_manifest(
            name='knowledge-owner-aget',
            agent_type='Knowledge Owner Aget',
            base_template='advisor',
            capabilities=['memory-management', 'org-kb', 'structured-outputs']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Knowledge Owner Aget failed: {result.errors}"
            os.unlink(f.name)


class TestResearchAdvisorAget:
    """Tests for Research Advisor Aget instantiation."""

    def test_research_advisor_aget_composes(self, manifest_validator):
        """Research Advisor Aget should compose from advisor + domain-knowledge."""
        manifest = create_manifest(
            name='research-advisor-aget',
            agent_type='Research Advisor Aget',
            base_template='advisor',
            capabilities=['domain-knowledge', 'structured-outputs', 'memory-management']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Research Advisor Aget failed: {result.errors}"
            os.unlink(f.name)


class TestAllBaseTemplates:
    """Tests that all base templates can be used."""

    @pytest.mark.parametrize("base_template", [
        'worker', 'advisor', 'supervisor', 'consultant', 'developer', 'spec-engineer'
    ])
    def test_base_template_valid(self, manifest_validator, base_template):
        """Each base template should be valid."""
        manifest = create_manifest(
            name=f'{base_template}-test',
            agent_type=f'{base_template.title()} Test',
            base_template=base_template,
            capabilities=['memory-management']
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f)
            result = manifest_validator.validate_file(f.name)
            assert result.valid, f"Base template '{base_template}' failed: {result.errors}"
            os.unlink(f.name)
