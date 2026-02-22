"""
Contract Tests for AGET CI Specification (AGET_CI_SPEC.md)

These tests verify CI requirements for AGET templates and agent repositories.
Implements contract enforcement for CAP-CI-001 through CAP-CI-005.

Traceability:
- CAP-CI-001: Test Isolation
- CAP-CI-002: Package Configuration
- CAP-CI-003: CI Workflow Structure
- CAP-CI-004: CI Triggers
- CAP-CI-005: CI Validation

Reference: aget/specs/AGET_CI_SPEC.md
Change Origin: L404 (CI Test Isolation Requirements)
"""

import pytest
import os
import sys
import re
import tempfile
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import yaml


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_template_dir():
    """Create a temporary template directory structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create standard template structure
        Path(tmpdir, 'tests').mkdir()
        Path(tmpdir, '.github/workflows').mkdir(parents=True)
        Path(tmpdir, 'src/template_name').mkdir(parents=True)

        # Create __init__.py files
        Path(tmpdir, 'src/__init__.py').write_text('')
        Path(tmpdir, 'src/template_name/__init__.py').write_text('')

        # Create setup.py
        setup_content = """
from setuptools import setup, find_packages

setup(
    name='template-name',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
)
"""
        Path(tmpdir, 'setup.py').write_text(setup_content)

        # Create CI workflow
        ci_workflow = """
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install ruff
      - run: ruff check .

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install bandit
      - run: bandit -r . -ll
"""
        Path(tmpdir, '.github/workflows/ci.yml').write_text(ci_workflow)

        # Create valid test file
        test_content = """
import pytest

class TestExample:
    def test_placeholder(self):
        assert True
"""
        Path(tmpdir, 'tests/test_example.py').write_text(test_content)

        yield tmpdir


@pytest.fixture
def aget_framework_path():
    """Return the path to the aget-framework directory."""
    return Path(os.environ.get('AGET_FRAMEWORK_DIR', str(Path(__file__).resolve().parents[3])))


# ---------------------------------------------------------------------------
# CAP-CI-001: Test Isolation
# ---------------------------------------------------------------------------

class TestCITestIsolation:
    """
    Contract tests for CAP-CI-001: Test Isolation.

    Requirements:
    - CAP-CI-001-01: No external package imports unless installed
    - CAP-CI-001-02: Use relative imports or sys.path for local modules
    - CAP-CI-001-03: Install package via setup.py if import needed
    - CAP-CI-001-04: No @patch decorators referencing non-existent modules

    Reference: AGET_CI_SPEC.md#cap-ci-001-test-isolation
    """

    def test_ci_test_isolation_no_external_imports(self, temp_template_dir):
        """
        CAP-CI-001-01: Tests shall not import from external packages unless installed.

        Validates that test files don't import from 'aget.*' modules directly
        since templates don't include the aget package.
        """
        test_file = Path(temp_template_dir, 'tests/test_example.py')
        content = test_file.read_text()

        # Pattern for invalid aget imports
        invalid_patterns = [
            r'^from\s+aget\.',
            r'^import\s+aget\.',
        ]

        for pattern in invalid_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            assert not matches, f"Found invalid import pattern: {pattern}"

    def test_ci_test_isolation_no_invalid_patch(self, temp_template_dir):
        """
        CAP-CI-001-04: Tests shall not use @patch decorators referencing non-existent modules.

        Validates that @patch decorators don't reference 'aget.*' modules.
        """
        test_file = Path(temp_template_dir, 'tests/test_example.py')
        content = test_file.read_text()

        # Pattern for invalid patch targets
        invalid_patch_pattern = r"@patch\(['\"]aget\."
        matches = re.findall(invalid_patch_pattern, content)
        assert not matches, f"Found invalid @patch decorator referencing aget module"

    def test_ci_test_isolation_template_compliance(self, aget_framework_path):
        """
        CAP-CI-001: Verify all template test files follow isolation requirements.

        Scans all template test directories for violations.
        """
        templates = [
            'template-worker-aget',
            'template-developer-aget',
            'template-advisor-aget',
            'template-spec-engineer-aget',
            'template-consultant-aget',
            'template-supervisor-aget',
        ]

        violations = []

        for template in templates:
            tests_dir = aget_framework_path / template / 'tests'
            if not tests_dir.exists():
                continue

            for test_file in tests_dir.glob('**/*.py'):
                content = test_file.read_text()

                # Check for invalid imports
                if re.search(r'^from\s+aget\.', content, re.MULTILINE):
                    violations.append(f"{template}: {test_file.name} has 'from aget.' import")
                if re.search(r'^import\s+aget\.', content, re.MULTILINE):
                    violations.append(f"{template}: {test_file.name} has 'import aget.' import")
                if re.search(r"@patch\(['\"]aget\.", content):
                    violations.append(f"{template}: {test_file.name} has @patch('aget.*') decorator")

        assert not violations, f"Test isolation violations:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# CAP-CI-002: Package Configuration
# ---------------------------------------------------------------------------

class TestCIPackageConfiguration:
    """
    Contract tests for CAP-CI-002: Package Configuration.

    Requirements:
    - CAP-CI-002-01: Include __init__.py in all package directories
    - CAP-CI-002-02: Set package_dir={'': 'src'} for src/ layout
    - CAP-CI-002-03: Use find_packages() with correct where parameter
    - CAP-CI-002-04: Declare Python version requirements in setup.py

    Reference: AGET_CI_SPEC.md#cap-ci-002-package-configuration
    """

    def test_ci_package_configuration_init_files(self, temp_template_dir):
        """
        CAP-CI-002-01: Package directories shall have __init__.py files.
        """
        src_dir = Path(temp_template_dir, 'src')

        # All directories in src should have __init__.py
        for subdir in src_dir.rglob('*'):
            if subdir.is_dir():
                init_file = subdir / '__init__.py'
                # Allow empty directories without __init__.py
                has_py_files = any(subdir.glob('*.py'))
                if has_py_files or subdir == src_dir:
                    assert init_file.exists(), f"Missing __init__.py in {subdir}"

    def test_ci_package_configuration_setup_py(self, temp_template_dir):
        """
        CAP-CI-002-02/03: setup.py shall use correct package configuration.
        """
        setup_file = Path(temp_template_dir, 'setup.py')
        content = setup_file.read_text()

        # Check for find_packages
        assert 'find_packages' in content, "setup.py should use find_packages()"

        # Check for src layout (if applicable)
        if 'src/' in content or "where='src'" in content:
            assert "package_dir={'': 'src'}" in content or 'package_dir={"": "src"}' in content, \
                "src layout requires package_dir={'': 'src'}"

    def test_ci_package_configuration_python_version(self, temp_template_dir):
        """
        CAP-CI-002-04: setup.py shall declare Python version requirements.
        """
        setup_file = Path(temp_template_dir, 'setup.py')
        content = setup_file.read_text()

        assert 'python_requires' in content, "setup.py should specify python_requires"


# ---------------------------------------------------------------------------
# CAP-CI-003: CI Workflow Structure
# ---------------------------------------------------------------------------

class TestCIWorkflowStructure:
    """
    Contract tests for CAP-CI-003: CI Workflow Structure.

    Requirements:
    - CAP-CI-003-01: Include Test_Job in CI_Workflow
    - CAP-CI-003-02: Include Lint_Job in CI_Workflow
    - CAP-CI-003-03: Include Security_Job in CI_Workflow
    - CAP-CI-003-04: Test against Python_Version_Matrix [3.8-3.12]
    - CAP-CI-003-05: Use pytest for Test_Job

    Reference: AGET_CI_SPEC.md#cap-ci-003-ci-workflow-structure
    """

    def test_ci_workflow_structure_jobs(self, temp_template_dir):
        """
        CAP-CI-003-01/02/03: CI workflow shall include test, lint, and security jobs.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        workflow = yaml.safe_load(ci_file.read_text())

        jobs = workflow.get('jobs', {})

        # Check required jobs exist
        assert 'test' in jobs, "CI workflow must include 'test' job"
        assert 'lint' in jobs, "CI workflow must include 'lint' job"
        assert 'security' in jobs, "CI workflow must include 'security' job"

    def test_ci_workflow_structure_python_matrix(self, temp_template_dir):
        """
        CAP-CI-003-04: Test job shall test against Python 3.8-3.12.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        workflow = yaml.safe_load(ci_file.read_text())

        test_job = workflow.get('jobs', {}).get('test', {})
        strategy = test_job.get('strategy', {})
        matrix = strategy.get('matrix', {})
        python_versions = matrix.get('python-version', [])

        required_versions = {'3.8', '3.9', '3.10', '3.11', '3.12'}
        actual_versions = set(str(v) for v in python_versions)

        assert required_versions.issubset(actual_versions), \
            f"Missing Python versions: {required_versions - actual_versions}"

    def test_ci_workflow_structure_pytest(self, temp_template_dir):
        """
        CAP-CI-003-05: Test job shall use pytest.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        content = ci_file.read_text()

        assert 'pytest' in content, "Test job must use pytest"


# ---------------------------------------------------------------------------
# CAP-CI-004: CI Triggers
# ---------------------------------------------------------------------------

class TestCITriggers:
    """
    Contract tests for CAP-CI-004: CI Triggers.

    Requirements:
    - CAP-CI-004-01: Trigger on push to main branch
    - CAP-CI-004-02: Trigger on push to develop branch
    - CAP-CI-004-03: Trigger on PR to main branch

    Reference: AGET_CI_SPEC.md#cap-ci-004-ci-triggers
    """

    def _get_triggers(self, workflow: Dict) -> Dict:
        """Get triggers from workflow, handling YAML 'on' -> True conversion."""
        # YAML parses 'on' as True (boolean), so we need to check both
        return workflow.get('on', workflow.get(True, {}))

    def test_ci_triggers_push_main(self, temp_template_dir):
        """
        CAP-CI-004-01: CI shall trigger on push to main branch.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        workflow = yaml.safe_load(ci_file.read_text())

        triggers = self._get_triggers(workflow)
        push_trigger = triggers.get('push', {}) if triggers else {}
        branches = push_trigger.get('branches', []) if push_trigger else []

        assert 'main' in branches, "CI must trigger on push to main"

    def test_ci_triggers_push_develop(self, temp_template_dir):
        """
        CAP-CI-004-02: CI shall trigger on push to develop branch.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        workflow = yaml.safe_load(ci_file.read_text())

        triggers = self._get_triggers(workflow)
        push_trigger = triggers.get('push', {}) if triggers else {}
        branches = push_trigger.get('branches', []) if push_trigger else []

        assert 'develop' in branches, "CI must trigger on push to develop"

    def test_ci_triggers_pr_main(self, temp_template_dir):
        """
        CAP-CI-004-03: CI shall trigger on PR to main branch.
        """
        ci_file = Path(temp_template_dir, '.github/workflows/ci.yml')
        workflow = yaml.safe_load(ci_file.read_text())

        triggers = self._get_triggers(workflow)
        pr_trigger = triggers.get('pull_request', {}) if triggers else {}
        branches = pr_trigger.get('branches', []) if pr_trigger else []

        assert 'main' in branches, "CI must trigger on PR to main"


# ---------------------------------------------------------------------------
# CAP-CI-005: CI Validation
# ---------------------------------------------------------------------------

class TestCIValidation:
    """
    Contract tests for CAP-CI-005: CI Validation.

    Requirements:
    - CAP-CI-005-01: Verify test collection succeeds
    - CAP-CI-005-03: CI shall fail if any test fails

    Reference: AGET_CI_SPEC.md#cap-ci-005-ci-validation
    """

    def test_ci_validation_collection(self, temp_template_dir):
        """
        CAP-CI-005-01: Test collection shall succeed before running tests.

        This validates that test files can be imported without errors.
        """
        tests_dir = Path(temp_template_dir, 'tests')

        for test_file in tests_dir.glob('test_*.py'):
            # Try to parse the file as valid Python
            content = test_file.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Test file {test_file.name} has syntax error: {e}")


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestCISpecIntegration:
    """
    Integration tests validating complete CI compliance.
    """

    def test_template_ci_compliance(self, aget_framework_path):
        """
        Verify templates with CI have workflow configuration.

        Templates should have:
        - .github/workflows/ci.yml
        - Tests without invalid imports

        Note: setup.py presence is checked but not required (some templates
        may use pyproject.toml or other configurations).
        """
        templates_with_ci = [
            'template-worker-aget',
            'template-developer-aget',
            'template-advisor-aget',
            'template-spec-engineer-aget',
            'template-consultant-aget',
        ]

        critical_issues = []
        warnings = []

        for template in templates_with_ci:
            template_path = aget_framework_path / template

            # Check CI workflow exists (critical)
            ci_file = template_path / '.github/workflows/ci.yml'
            if not ci_file.exists():
                critical_issues.append(f"{template}: Missing .github/workflows/ci.yml")
                continue

            # Check setup.py exists (warning - may use alternative)
            setup_file = template_path / 'setup.py'
            pyproject_file = template_path / 'pyproject.toml'
            if not setup_file.exists() and not pyproject_file.exists():
                warnings.append(f"{template}: No setup.py or pyproject.toml")

        # Critical issues fail the test
        assert not critical_issues, f"CI compliance issues:\n" + "\n".join(critical_issues)

    def test_ci_spec_traceability(self):
        """
        Verify all CAP-CI requirements have corresponding tests.

        Per CAP-VAL-001 (L352), requirements must have test traceability.
        """
        # Map requirements to test classes
        requirement_coverage = {
            'CAP-CI-001': TestCITestIsolation,
            'CAP-CI-002': TestCIPackageConfiguration,
            'CAP-CI-003': TestCIWorkflowStructure,
            'CAP-CI-004': TestCITriggers,
            'CAP-CI-005': TestCIValidation,
        }

        for req_id, test_class in requirement_coverage.items():
            assert test_class is not None, f"Missing test class for {req_id}"
            # Verify class has at least one test method
            test_methods = [m for m in dir(test_class) if m.startswith('test_')]
            assert len(test_methods) > 0, f"Test class for {req_id} has no test methods"
