"""
Tests for AGET Composition Validation

These tests verify that the composition validator correctly:
1. Detects DAG conflicts
2. Validates prerequisites
3. Detects behavior overlaps
4. Validates composability
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'validation'))
from validate_composition import CompositionValidator, CompositionResult, CapabilitySpec


@pytest.fixture
def validator():
    """Create a validator without capability specs loaded."""
    return CompositionValidator()


@pytest.fixture
def valid_manifest():
    """A minimal valid template manifest for composition testing."""
    return {
        'apiVersion': 'aget.framework/v1',
        'kind': 'TemplateManifest',
        'metadata': {
            'name': 'test-agent',
            'version': '1.0.0',
            'agent_type': 'Test Agent'
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


@pytest.fixture
def capability_spec_data():
    """Sample capability specification data."""
    return {
        'apiVersion': 'aget.framework/v1',
        'kind': 'CapabilitySpecification',
        'metadata': {
            'name': 'test-capability',
            'version': '1.0.0',
            'created': '2025-12-24',
            'author': 'test',
            'status': 'approved'
        },
        'spec': {
            'name': 'test-capability',
            'display_name': 'Test',
            'category': 'Test',
            'purpose': 'Testing',
            'prerequisites': ['other-capability'],
            'composable_with': ['All base templates']
        },
        'behaviors': [{
            'name': 'test_behavior',
            'display_name': 'Test',
            'description': 'Test',
            'trigger': {'explicit': ['test trigger']},
            'protocol': ['Step 1'],
            'output': 'Output'
        }]
    }


class TestBasicValidation:
    """Tests for basic composition validation."""

    def test_valid_composition_passes(self, validator, valid_manifest):
        """A valid composition should pass."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_manifest, f)
            result = validator.validate_manifest(f.name)
            # Without capability specs, should have warnings but pass
            assert result.valid or len(result.conflicts) == 0
            os.unlink(f.name)

    def test_empty_manifest_fails(self, validator):
        """Empty manifest should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')
            f.flush()
            result = validator.validate_manifest(f.name)
            assert not result.valid
            os.unlink(f.name)

    def test_invalid_yaml_fails(self, validator):
        """Invalid YAML should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: [')
            f.flush()
            result = validator.validate_manifest(f.name)
            assert not result.valid
            os.unlink(f.name)


class TestCapabilitySpecLoading:
    """Tests for capability spec loading."""

    def test_capability_spec_parsing(self, capability_spec_data):
        """CapabilitySpec should parse data correctly."""
        spec = CapabilitySpec(capability_spec_data)
        assert spec.name == 'test-capability'
        assert spec.version == '1.0.0'
        assert len(spec.behaviors) == 1
        assert 'other-capability' in spec.prerequisites

    def test_get_behavior_names(self, capability_spec_data):
        """Should extract behavior names correctly."""
        spec = CapabilitySpec(capability_spec_data)
        names = spec.get_behavior_names()
        assert 'test_behavior' in names

    def test_get_triggers(self, capability_spec_data):
        """Should extract triggers correctly."""
        spec = CapabilitySpec(capability_spec_data)
        triggers = spec.get_triggers()
        assert 'test_behavior' in triggers
        assert 'test trigger' in triggers['test_behavior']


class TestPrerequisiteValidation:
    """Tests for prerequisite validation."""

    def test_missing_prerequisite_detected(self):
        """Missing prerequisite should be detected when specs are loaded."""
        # Create temp directory with capability specs
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a capability that requires another
            cap1 = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'CapabilitySpecification',
                'metadata': {'name': 'dependent-cap', 'version': '1.0.0', 'created': '2025-12-24', 'author': 'test', 'status': 'approved'},
                'spec': {
                    'name': 'dependent-cap',
                    'display_name': 'Dependent',
                    'category': 'Test',
                    'purpose': 'Test',
                    'prerequisites': ['required-cap']
                },
                'behaviors': [{'name': 'b1', 'display_name': 'B1', 'description': 'D', 'trigger': [], 'protocol': [], 'output': 'O'}]
            }
            with open(os.path.join(tmpdir, 'cap1.yaml'), 'w') as f:
                yaml.dump(cap1, f)

            validator = CompositionValidator(tmpdir)

            # Create manifest that uses dependent-cap without required-cap
            manifest = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'TemplateManifest',
                'metadata': {'name': 'test', 'version': '1.0.0', 'agent_type': 'Test'},
                'composition': {
                    'base_template': 'advisor',
                    'capabilities': [{'name': 'dependent-cap', 'version': '1.0.0'}],
                    'composition_rules': {'conflict_resolution': 'error'}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                result = validator.validate_manifest(f.name)
                # Should have conflict for missing prerequisite
                assert any(c['type'] == 'missing_prerequisite' for c in result.conflicts)
                os.unlink(f.name)


class TestBehaviorConflicts:
    """Tests for behavior conflict detection."""

    def test_behavior_name_collision_detected(self):
        """Behavior name collision should be detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two capabilities with same behavior name
            for i, name in enumerate(['cap1', 'cap2']):
                cap = {
                    'apiVersion': 'aget.framework/v1',
                    'kind': 'CapabilitySpecification',
                    'metadata': {'name': name, 'version': '1.0.0', 'created': '2025-12-24', 'author': 'test', 'status': 'approved'},
                    'spec': {'name': name, 'display_name': name, 'category': 'Test', 'purpose': 'Test'},
                    'behaviors': [{'name': 'conflicting_behavior', 'display_name': 'Conflict', 'description': 'D', 'trigger': {'explicit': ['trigger']}, 'protocol': ['S1'], 'output': 'O'}]
                }
                with open(os.path.join(tmpdir, f'{name}.yaml'), 'w') as f:
                    yaml.dump(cap, f)

            validator = CompositionValidator(tmpdir)

            manifest = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'TemplateManifest',
                'metadata': {'name': 'test', 'version': '1.0.0', 'agent_type': 'Test'},
                'composition': {
                    'base_template': 'advisor',
                    'capabilities': [
                        {'name': 'cap1', 'version': '1.0.0'},
                        {'name': 'cap2', 'version': '1.0.0'}
                    ],
                    'composition_rules': {'conflict_resolution': 'error'}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                result = validator.validate_manifest(f.name)
                assert any(c['type'] == 'behavior_name_collision' for c in result.conflicts)
                os.unlink(f.name)

    def test_behavior_collision_with_merge_passes(self):
        """Behavior collision with 'merge' resolution should pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ['cap1', 'cap2']:
                cap = {
                    'apiVersion': 'aget.framework/v1',
                    'kind': 'CapabilitySpecification',
                    'metadata': {'name': name, 'version': '1.0.0', 'created': '2025-12-24', 'author': 'test', 'status': 'approved'},
                    'spec': {'name': name, 'display_name': name, 'category': 'Test', 'purpose': 'Test'},
                    'behaviors': [{'name': 'shared_behavior', 'display_name': 'Shared', 'description': 'D', 'trigger': [], 'protocol': [], 'output': 'O'}]
                }
                with open(os.path.join(tmpdir, f'{name}.yaml'), 'w') as f:
                    yaml.dump(cap, f)

            validator = CompositionValidator(tmpdir)

            manifest = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'TemplateManifest',
                'metadata': {'name': 'test', 'version': '1.0.0', 'agent_type': 'Test'},
                'composition': {
                    'base_template': 'advisor',
                    'capabilities': [
                        {'name': 'cap1', 'version': '1.0.0'},
                        {'name': 'cap2', 'version': '1.0.0'}
                    ],
                    'composition_rules': {'conflict_resolution': 'merge'}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                result = validator.validate_manifest(f.name)
                # With merge, should be valid (warnings only)
                assert result.valid or not any(c['type'] == 'behavior_name_collision' for c in result.conflicts)
                os.unlink(f.name)


class TestComposabilityChecks:
    """Tests for composability validation."""

    def test_incompatible_capability_warns(self):
        """Incompatible capability should generate warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cap = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'CapabilitySpecification',
                'metadata': {'name': 'supervisor-only-cap', 'version': '1.0.0', 'created': '2025-12-24', 'author': 'test', 'status': 'approved'},
                'spec': {
                    'name': 'supervisor-only-cap',
                    'display_name': 'Supervisor Only',
                    'category': 'Test',
                    'purpose': 'Test',
                    'composable_with': ['supervisor']  # Only works with supervisor
                },
                'behaviors': [{'name': 'b1', 'display_name': 'B1', 'description': 'D', 'trigger': [], 'protocol': [], 'output': 'O'}]
            }
            with open(os.path.join(tmpdir, 'cap.yaml'), 'w') as f:
                yaml.dump(cap, f)

            validator = CompositionValidator(tmpdir)

            manifest = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'TemplateManifest',
                'metadata': {'name': 'test', 'version': '1.0.0', 'agent_type': 'Test'},
                'composition': {
                    'base_template': 'advisor',  # Not supervisor
                    'capabilities': [{'name': 'supervisor-only-cap', 'version': '1.0.0'}]
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                result = validator.validate_manifest(f.name)
                # Should have warning about compatibility
                assert any('compatible' in w.lower() for w in result.warnings)
                os.unlink(f.name)


class TestConflictResolutionStrategies:
    """Tests for different conflict resolution strategies."""

    @pytest.mark.parametrize("strategy", ['first-wins', 'last-wins', 'merge'])
    def test_non_error_strategies_resolve_collisions(self, strategy):
        """Non-error strategies should resolve behavior collisions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ['cap1', 'cap2']:
                cap = {
                    'apiVersion': 'aget.framework/v1',
                    'kind': 'CapabilitySpecification',
                    'metadata': {'name': name, 'version': '1.0.0', 'created': '2025-12-24', 'author': 'test', 'status': 'approved'},
                    'spec': {'name': name, 'display_name': name, 'category': 'Test', 'purpose': 'Test'},
                    'behaviors': [{'name': 'shared', 'display_name': 'Shared', 'description': 'D', 'trigger': [], 'protocol': [], 'output': 'O'}]
                }
                with open(os.path.join(tmpdir, f'{name}.yaml'), 'w') as f:
                    yaml.dump(cap, f)

            validator = CompositionValidator(tmpdir)

            manifest = {
                'apiVersion': 'aget.framework/v1',
                'kind': 'TemplateManifest',
                'metadata': {'name': 'test', 'version': '1.0.0', 'agent_type': 'Test'},
                'composition': {
                    'base_template': 'advisor',
                    'capabilities': [
                        {'name': 'cap1', 'version': '1.0.0'},
                        {'name': 'cap2', 'version': '1.0.0'}
                    ],
                    'composition_rules': {'conflict_resolution': strategy}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                result = validator.validate_manifest(f.name)
                # Should have warning (resolved) not error
                collision_conflicts = [c for c in result.conflicts if c['type'] == 'behavior_name_collision']
                assert len(collision_conflicts) == 0, f"Strategy '{strategy}' should resolve collision"
                os.unlink(f.name)
