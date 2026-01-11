"""
Unit tests for validate_artifact_size.py

Tests the artifact size validator against AGET_SPEC_FORMAT guidance.
References: L502, CAP-PP-012
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add validation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'validation'))

from validate_artifact_size import (
    LIMITS,
    SizeLimit,
    ValidationResult,
    classify_size,
    count_lines,
    detect_artifact_type,
    find_artifacts,
    get_recommendation,
    validate_file,
)


class TestDetectArtifactType:
    """Test artifact type detection from filenames."""

    def test_project_plan_detection(self):
        assert detect_artifact_type('PROJECT_PLAN_v3.2.0.md') == 'PROJECT_PLAN'
        assert detect_artifact_type('PROJECT_PLAN_test_v1.0.md') == 'PROJECT_PLAN'
        assert detect_artifact_type('PROJECT_PLAN-feature.md') == 'PROJECT_PLAN'

    def test_spec_detection(self):
        assert detect_artifact_type('AGET_FRAMEWORK_SPEC.md') == 'SPEC'
        assert detect_artifact_type('AGET_PROJECT_PLAN_SPEC.md') == 'SPEC'
        assert detect_artifact_type('CUSTOM_SPEC.md') == 'SPEC'

    def test_sop_detection(self):
        assert detect_artifact_type('SOP_release_process.md') == 'SOP'
        assert detect_artifact_type('SOP-testing.md') == 'SOP'

    def test_ldoc_detection(self):
        assert detect_artifact_type('L502_artifact_comprehensibility.md') == 'L-doc'
        assert detect_artifact_type('L001-first-learning.md') == 'L-doc'

    def test_claude_md_detection(self):
        assert detect_artifact_type('CLAUDE.md') == 'CLAUDE.md'
        assert detect_artifact_type('AGENTS.md') == 'CLAUDE.md'

    def test_non_artifact_returns_none(self):
        assert detect_artifact_type('README.md') is None
        assert detect_artifact_type('random.md') is None
        assert detect_artifact_type('notes.txt') is None


class TestClassifySize:
    """Test size classification logic."""

    def test_optimal_classification(self):
        limits = SizeLimit(optimal=500, warning=1000, error=1500)
        assert classify_size(100, limits) == 'optimal'
        assert classify_size(500, limits) == 'optimal'

    def test_acceptable_classification(self):
        limits = SizeLimit(optimal=500, warning=1000, error=1500)
        assert classify_size(501, limits) == 'acceptable'
        assert classify_size(1000, limits) == 'acceptable'

    def test_warning_classification(self):
        limits = SizeLimit(optimal=500, warning=1000, error=1500)
        assert classify_size(1001, limits) == 'warning'
        assert classify_size(1500, limits) == 'warning'

    def test_oversized_classification(self):
        limits = SizeLimit(optimal=500, warning=1000, error=1500)
        assert classify_size(1501, limits) == 'oversized'
        assert classify_size(2000, limits) == 'oversized'


class TestGetRecommendation:
    """Test recommendation generation."""

    def test_optimal_no_recommendation(self):
        assert get_recommendation('optimal', 'PROJECT_PLAN', 100) is None

    def test_acceptable_monitor(self):
        rec = get_recommendation('acceptable', 'PROJECT_PLAN', 600)
        assert 'Monitor' in rec
        assert '600' in rec

    def test_warning_project_plan(self):
        rec = get_recommendation('warning', 'PROJECT_PLAN', 1200)
        assert 'decomposition' in rec.lower()

    def test_warning_spec(self):
        rec = get_recommendation('warning', 'SPEC', 900)
        assert 'split' in rec.lower() or 'domain' in rec.lower()

    def test_oversized_decompose_required(self):
        rec = get_recommendation('oversized', 'PROJECT_PLAN', 2000)
        assert 'DECOMPOSE' in rec


class TestCountLines:
    """Test line counting."""

    def test_count_lines_simple(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            f.flush()
            assert count_lines(f.name) == 3
            os.unlink(f.name)

    def test_count_lines_empty(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            f.flush()
            assert count_lines(f.name) == 0
            os.unlink(f.name)

    def test_count_lines_nonexistent(self):
        assert count_lines('/nonexistent/file.md') == 0


class TestValidateFile:
    """Test file validation."""

    def test_validate_project_plan(self):
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', prefix='PROJECT_PLAN_test_', delete=False
        ) as f:
            f.write("# Test Plan\n" * 100)
            f.flush()
            result = validate_file(f.name)
            assert result is not None
            assert result.artifact_type == 'PROJECT_PLAN'
            assert result.lines == 100
            assert result.status == 'optimal'
            os.unlink(f.name)

    def test_validate_non_artifact(self):
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', prefix='random_', delete=False
        ) as f:
            f.write("# Random file\n")
            f.flush()
            result = validate_file(f.name)
            assert result is None
            os.unlink(f.name)


class TestFindArtifacts:
    """Test artifact discovery."""

    def test_find_in_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / 'PROJECT_PLAN_test.md').write_text('# Test')
            (Path(tmpdir) / 'README.md').write_text('# Readme')
            (Path(tmpdir) / 'L001_learning.md').write_text('# Learning')

            artifacts = find_artifacts(tmpdir)
            assert len(artifacts) == 2  # PROJECT_PLAN and L-doc, not README

    def test_find_single_file(self):
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', prefix='PROJECT_PLAN_', delete=False
        ) as f:
            f.write('# Test')
            f.flush()
            artifacts = find_artifacts(f.name)
            assert len(artifacts) == 1
            os.unlink(f.name)


class TestLimitsConfiguration:
    """Test that limits are properly configured."""

    def test_all_artifact_types_have_limits(self):
        expected_types = ['PROJECT_PLAN', 'SPEC', 'SOP', 'L-doc', 'CLAUDE.md']
        for artifact_type in expected_types:
            assert artifact_type in LIMITS
            limits = LIMITS[artifact_type]
            assert limits.optimal < limits.warning < limits.error

    def test_project_plan_limits_match_spec(self):
        """Verify limits match CAP-PP-012 specification."""
        limits = LIMITS['PROJECT_PLAN']
        assert limits.optimal == 500
        assert limits.warning == 1000
        assert limits.error == 1500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
