"""
Tests for AGET Template Manifest Validation

These tests verify that the template manifest validator correctly:
1. Validates well-formed manifests
2. Rejects malformed manifests
3. Checks required fields
4. Validates base templates and capabilities
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'validation'))
from validate_template_manifest import TemplateManifestValidator, ValidationResult


@pytest.fixture
def validator():
    """Create a validator instance."""
    return TemplateManifestValidator()


@pytest.fixture
def valid_manifest():
    """A minimal valid template manifest."""
    return {
        'apiVersion': 'aget.framework/v1',
        'kind': 'TemplateManifest',
        'metadata': {
            'name': 'test-agent',
            'version': '1.0.0',
            'agent_type': 'Test Agent',
            'description': 'A test agent manifest'
        },
        'composition': {
            'base_template': 'advisor',
            'capabilities': [
                {'name': 'memory-management', 'version': '1.0.0'},
                {'name': 'domain-knowledge', 'version': '1.0.0'}
            ],
            'composition_rules': {
                'conflict_resolution': 'error'
            }
        }
    }


class TestValidManifest:
    """Tests for valid manifests."""

    def test_valid_manifest_passes(self, validator, valid_manifest):
        """A valid manifest should pass validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert result.valid, f"Errors: {result.errors}"
            os.unlink(f.name)

    def test_all_base_templates_valid(self, validator, valid_manifest):
        """All valid base templates should pass."""
        valid_templates = ['worker', 'advisor', 'supervisor', 'consultant', 'developer', 'spec-engineer']
        for template in valid_templates:
            valid_manifest['composition']['base_template'] = template
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(valid_manifest, f)
                result = validator.validate_file(f.name)
                assert result.valid, f"Template '{template}' failed: {result.errors}"
                os.unlink(f.name)


class TestMissingRequiredFields:
    """Tests for missing required fields."""

    def test_missing_apiversion_fails(self, validator, valid_manifest):
        """Missing apiVersion should fail."""
        del valid_manifest['apiVersion']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_missing_kind_fails(self, validator, valid_manifest):
        """Missing kind should fail."""
        del valid_manifest['kind']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_missing_metadata_fails(self, validator, valid_manifest):
        """Missing metadata should fail."""
        del valid_manifest['metadata']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_missing_composition_fails(self, validator, valid_manifest):
        """Missing composition should fail."""
        del valid_manifest['composition']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_missing_base_template_fails(self, validator, valid_manifest):
        """Missing base_template should fail."""
        del valid_manifest['composition']['base_template']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)


class TestInvalidValues:
    """Tests for invalid field values."""

    def test_invalid_apiversion_fails(self, validator, valid_manifest):
        """Invalid apiVersion should fail."""
        valid_manifest['apiVersion'] = 'wrong/version'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_invalid_kind_fails(self, validator, valid_manifest):
        """Invalid kind should fail."""
        valid_manifest['kind'] = 'WrongKind'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_invalid_base_template_fails(self, validator, valid_manifest):
        """Invalid base_template should fail."""
        valid_manifest['composition']['base_template'] = 'invalid-template'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_invalid_conflict_resolution_fails(self, validator, valid_manifest):
        """Invalid conflict_resolution should fail."""
        valid_manifest['composition']['composition_rules']['conflict_resolution'] = 'invalid'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)


class TestCapabilitiesValidation:
    """Tests for capabilities validation."""

    def test_empty_capabilities_warns(self, validator, valid_manifest):
        """Empty capabilities should generate warning."""
        valid_manifest['composition']['capabilities'] = []
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert result.valid  # Still valid
            assert len(result.warnings) > 0
            os.unlink(f.name)

    def test_capability_without_name_fails(self, validator, valid_manifest):
        """Capability without name should fail."""
        valid_manifest['composition']['capabilities'] = [{'version': '1.0.0'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_capability_without_version_fails(self, validator, valid_manifest):
        """Capability without version should fail."""
        valid_manifest['composition']['capabilities'] = [{'name': 'test'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_duplicate_capabilities_fails(self, validator, valid_manifest):
        """Duplicate capabilities should fail."""
        valid_manifest['composition']['capabilities'] = [
            {'name': 'test-cap', 'version': '1.0.0'},
            {'name': 'test-cap', 'version': '1.0.0'}
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)
