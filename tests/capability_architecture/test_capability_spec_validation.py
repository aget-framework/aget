"""
Tests for AGET Capability Specification Validation

These tests verify that the capability spec validator correctly:
1. Validates well-formed specifications
2. Rejects malformed specifications
3. Checks required fields
4. Validates field types and patterns
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'validation'))
from validate_capability_spec import CapabilitySpecValidator, ValidationResult


@pytest.fixture
def validator():
    """Create a validator instance."""
    return CapabilitySpecValidator()


@pytest.fixture
def valid_spec():
    """A minimal valid capability specification."""
    return {
        'apiVersion': 'aget.framework/v1',
        'kind': 'CapabilitySpecification',
        'metadata': {
            'name': 'test-capability',
            'version': '1.0.0',
            'created': '2025-12-24',
            'author': 'test-agent',
            'status': 'draft'
        },
        'spec': {
            'name': 'test-capability',
            'display_name': 'Test Capability',
            'category': 'Test',
            'purpose': 'For testing purposes'
        },
        'behaviors': [{
            'name': 'test_behavior',
            'display_name': 'Test Behavior',
            'description': 'A test behavior',
            'trigger': {'explicit': ['test']},
            'protocol': ['Step 1', 'Step 2'],
            'output': 'Test output'
        }],
        'contracts': [{
            'name': 'test_contract',
            'assertion': 'directory_exists',
            'path': '.aget/',
            'description': 'Test contract'
        }],
        'adoption': {
            'priority': 'P0',
            'demand': 'Test agents'
        }
    }


@pytest.fixture
def temp_spec_file(valid_spec):
    """Create a temporary spec file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(valid_spec, f)
        return f.name


class TestValidSpec:
    """Tests for valid specifications."""

    def test_valid_spec_passes(self, validator, temp_spec_file):
        """A valid specification should pass validation."""
        result = validator.validate_file(temp_spec_file)
        assert result.valid, f"Errors: {result.errors}"
        os.unlink(temp_spec_file)

    def test_valid_spec_has_no_errors(self, validator, temp_spec_file):
        """A valid specification should have no errors."""
        result = validator.validate_file(temp_spec_file)
        assert len(result.errors) == 0
        os.unlink(temp_spec_file)


class TestMissingRequiredFields:
    """Tests for missing required fields."""

    def test_missing_apiversion_fails(self, validator, valid_spec):
        """Missing apiVersion should fail."""
        del valid_spec['apiVersion']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('apiVersion' in e for e in result.errors)
            os.unlink(f.name)

    def test_missing_kind_fails(self, validator, valid_spec):
        """Missing kind should fail."""
        del valid_spec['kind']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('kind' in e for e in result.errors)
            os.unlink(f.name)

    def test_missing_metadata_fails(self, validator, valid_spec):
        """Missing metadata should fail."""
        del valid_spec['metadata']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('metadata' in e for e in result.errors)
            os.unlink(f.name)

    def test_missing_spec_fails(self, validator, valid_spec):
        """Missing spec should fail."""
        del valid_spec['spec']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('spec' in e for e in result.errors)
            os.unlink(f.name)

    def test_missing_behaviors_fails(self, validator, valid_spec):
        """Missing behaviors should fail."""
        del valid_spec['behaviors']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('behaviors' in e for e in result.errors)
            os.unlink(f.name)

    def test_missing_metadata_name_fails(self, validator, valid_spec):
        """Missing metadata.name should fail."""
        del valid_spec['metadata']['name']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('name' in e for e in result.errors)
            os.unlink(f.name)


class TestInvalidValues:
    """Tests for invalid field values."""

    def test_invalid_apiversion_fails(self, validator, valid_spec):
        """Invalid apiVersion value should fail."""
        valid_spec['apiVersion'] = 'wrong/version'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('apiVersion' in e for e in result.errors)
            os.unlink(f.name)

    def test_invalid_kind_fails(self, validator, valid_spec):
        """Invalid kind value should fail."""
        valid_spec['kind'] = 'WrongKind'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('kind' in e for e in result.errors)
            os.unlink(f.name)

    def test_invalid_status_fails(self, validator, valid_spec):
        """Invalid status value should fail."""
        valid_spec['metadata']['status'] = 'invalid-status'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('status' in e for e in result.errors)
            os.unlink(f.name)

    def test_invalid_contract_assertion_fails(self, validator, valid_spec):
        """Invalid contract assertion should fail."""
        valid_spec['contracts'][0]['assertion'] = 'invalid_assertion'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('assertion' in e for e in result.errors)
            os.unlink(f.name)


class TestBehaviorValidation:
    """Tests for behavior validation."""

    def test_empty_behaviors_fails(self, validator, valid_spec):
        """Empty behaviors list should fail."""
        valid_spec['behaviors'] = []
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('behavior' in e.lower() for e in result.errors)
            os.unlink(f.name)

    def test_behavior_without_name_fails(self, validator, valid_spec):
        """Behavior without name should fail."""
        del valid_spec['behaviors'][0]['name']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_duplicate_behavior_names_fails(self, validator, valid_spec):
        """Duplicate behavior names should fail."""
        valid_spec['behaviors'].append(valid_spec['behaviors'][0].copy())
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('duplicate' in e.lower() for e in result.errors)
            os.unlink(f.name)

    def test_behavior_with_list_trigger_passes(self, validator, valid_spec):
        """Behavior with list-style trigger should pass."""
        valid_spec['behaviors'][0]['trigger'] = ['trigger1', 'trigger2']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert result.valid, f"Errors: {result.errors}"
            os.unlink(f.name)


class TestFileErrors:
    """Tests for file-related errors."""

    def test_nonexistent_file_fails(self, validator):
        """Non-existent file should fail."""
        result = validator.validate_file('/nonexistent/path/file.yaml')
        assert not result.valid
        assert any('not found' in e.lower() for e in result.errors)

    def test_invalid_yaml_fails(self, validator):
        """Invalid YAML should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            f.flush()
            result = validator.validate_file(f.name)
            assert not result.valid
            assert any('yaml' in e.lower() for e in result.errors)
            os.unlink(f.name)

    def test_empty_file_fails(self, validator):
        """Empty file should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')
            f.flush()
            result = validator.validate_file(f.name)
            assert not result.valid
            os.unlink(f.name)


class TestWarnings:
    """Tests for warning conditions."""

    def test_no_contracts_warns(self, validator, valid_spec):
        """No contracts should generate warning."""
        del valid_spec['contracts']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert result.valid  # Still valid, just has warning
            assert len(result.warnings) > 0
            os.unlink(f.name)

    def test_no_adoption_warns(self, validator, valid_spec):
        """No adoption section should generate warning."""
        del valid_spec['adoption']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_spec, f)
            result = validator.validate_file(f.name)
            assert result.valid
            assert len(result.warnings) > 0
            os.unlink(f.name)
