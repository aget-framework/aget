"""
Tests for AGET Capability Contracts

These tests verify that capability contracts can be properly defined,
validated, and enforced. Contracts ensure agents meet capability requirements.

Contract Types:
- directory_exists: Check that a directory exists
- file_exists: Check that a file exists
- file_contains: Check that a file contains specific content
- custom: Custom validation logic
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'validation'))


@dataclass
class ContractResult:
    """Result of evaluating a contract."""
    name: str
    passed: bool
    message: str


class ContractEvaluator:
    """Evaluates capability contracts against an agent's file structure."""

    def __init__(self, agent_root: str):
        self.agent_root = Path(agent_root)

    def evaluate_contract(self, contract: Dict[str, Any]) -> ContractResult:
        """Evaluate a single contract."""
        assertion = contract.get('assertion')
        name = contract.get('name', 'unnamed')

        if assertion == 'directory_exists':
            return self._check_directory_exists(contract)
        elif assertion == 'file_exists':
            return self._check_file_exists(contract)
        elif assertion == 'file_contains':
            return self._check_file_contains(contract)
        elif assertion == 'custom':
            return ContractResult(name=name, passed=True, message="Custom contracts require manual validation")
        else:
            return ContractResult(name=name, passed=False, message=f"Unknown assertion type: {assertion}")

    def _check_directory_exists(self, contract: Dict) -> ContractResult:
        path = contract.get('path', '')
        name = contract.get('name', 'unnamed')
        full_path = self.agent_root / path

        if full_path.is_dir():
            return ContractResult(name=name, passed=True, message=f"Directory exists: {path}")
        else:
            return ContractResult(name=name, passed=False, message=f"Directory not found: {path}")

    def _check_file_exists(self, contract: Dict) -> ContractResult:
        path = contract.get('path', '')
        name = contract.get('name', 'unnamed')
        full_path = self.agent_root / path

        if full_path.is_file():
            return ContractResult(name=name, passed=True, message=f"File exists: {path}")
        else:
            return ContractResult(name=name, passed=False, message=f"File not found: {path}")

    def _check_file_contains(self, contract: Dict) -> ContractResult:
        path = contract.get('path', '')
        pattern = contract.get('pattern', '')
        name = contract.get('name', 'unnamed')
        full_path = self.agent_root / path

        if not full_path.is_file():
            return ContractResult(name=name, passed=False, message=f"File not found: {path}")

        try:
            content = full_path.read_text()
            if pattern in content:
                return ContractResult(name=name, passed=True, message=f"Pattern found in {path}")
            else:
                return ContractResult(name=name, passed=False, message=f"Pattern not found in {path}")
        except Exception as e:
            return ContractResult(name=name, passed=False, message=f"Error reading {path}: {e}")


@pytest.fixture
def temp_agent_dir():
    """Create a temporary agent directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create standard AGET structure
        Path(tmpdir, '.aget').mkdir()
        Path(tmpdir, '.aget/evolution').mkdir()
        Path(tmpdir, 'governance').mkdir()
        Path(tmpdir, 'planning').mkdir()
        Path(tmpdir, 'docs').mkdir()
        Path(tmpdir, 'docs/patterns').mkdir()

        # Create some files
        Path(tmpdir, 'governance/CHARTER.md').write_text('# Charter\n\nThis is the charter.')
        Path(tmpdir, '.aget/identity.json').write_text('{"name": "test-agent"}')

        yield tmpdir


@pytest.fixture
def evaluator(temp_agent_dir):
    """Create a contract evaluator."""
    return ContractEvaluator(temp_agent_dir)


class TestDirectoryExistsContract:
    """Tests for directory_exists contracts."""

    def test_existing_directory_passes(self, evaluator):
        """Existing directory should pass."""
        contract = {
            'name': 'has_aget_config',
            'assertion': 'directory_exists',
            'path': '.aget/'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed

    def test_missing_directory_fails(self, evaluator):
        """Missing directory should fail."""
        contract = {
            'name': 'has_nonexistent',
            'assertion': 'directory_exists',
            'path': 'nonexistent/'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed

    def test_nested_directory_passes(self, evaluator):
        """Nested existing directory should pass."""
        contract = {
            'name': 'has_evolution',
            'assertion': 'directory_exists',
            'path': '.aget/evolution/'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed

    def test_file_as_directory_fails(self, evaluator):
        """File path should fail directory check."""
        contract = {
            'name': 'file_not_dir',
            'assertion': 'directory_exists',
            'path': 'governance/CHARTER.md'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed


class TestFileExistsContract:
    """Tests for file_exists contracts."""

    def test_existing_file_passes(self, evaluator):
        """Existing file should pass."""
        contract = {
            'name': 'has_charter',
            'assertion': 'file_exists',
            'path': 'governance/CHARTER.md'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed

    def test_missing_file_fails(self, evaluator):
        """Missing file should fail."""
        contract = {
            'name': 'has_missing',
            'assertion': 'file_exists',
            'path': 'nonexistent.md'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed

    def test_directory_as_file_fails(self, evaluator):
        """Directory path should fail file check."""
        contract = {
            'name': 'dir_not_file',
            'assertion': 'file_exists',
            'path': 'governance/'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed

    def test_nested_file_passes(self, evaluator):
        """Nested file should pass."""
        contract = {
            'name': 'has_identity',
            'assertion': 'file_exists',
            'path': '.aget/identity.json'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed


class TestFileContainsContract:
    """Tests for file_contains contracts."""

    def test_pattern_found_passes(self, evaluator):
        """Pattern found in file should pass."""
        contract = {
            'name': 'charter_has_heading',
            'assertion': 'file_contains',
            'path': 'governance/CHARTER.md',
            'pattern': '# Charter'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed

    def test_pattern_not_found_fails(self, evaluator):
        """Pattern not found should fail."""
        contract = {
            'name': 'charter_has_missing',
            'assertion': 'file_contains',
            'path': 'governance/CHARTER.md',
            'pattern': 'NONEXISTENT_PATTERN'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed

    def test_missing_file_fails(self, evaluator):
        """Missing file should fail contains check."""
        contract = {
            'name': 'missing_file_contains',
            'assertion': 'file_contains',
            'path': 'nonexistent.md',
            'pattern': 'anything'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed


class TestCustomContract:
    """Tests for custom contracts."""

    def test_custom_contract_passes(self, evaluator):
        """Custom contracts should pass (require manual validation)."""
        contract = {
            'name': 'custom_check',
            'assertion': 'custom',
            'description': 'Manual validation required'
        }
        result = evaluator.evaluate_contract(contract)
        assert result.passed


class TestUnknownAssertion:
    """Tests for unknown assertion types."""

    def test_unknown_assertion_fails(self, evaluator):
        """Unknown assertion type should fail."""
        contract = {
            'name': 'unknown',
            'assertion': 'unknown_type'
        }
        result = evaluator.evaluate_contract(contract)
        assert not result.passed


class TestContractFromCapabilitySpec:
    """Tests for contracts loaded from capability specs."""

    def test_memory_management_contracts(self, temp_agent_dir):
        """Memory management contracts should be evaluable."""
        # Add required structures
        Path(temp_agent_dir, 'docs/patterns').mkdir(parents=True, exist_ok=True)
        Path(temp_agent_dir, 'sops').mkdir(exist_ok=True)
        Path(temp_agent_dir, 'docs/patterns/PATTERN_step_back_review_kb.md').write_text('# Pattern')
        Path(temp_agent_dir, 'sops/SESSION_HANDOFF_AGET.md').write_text('# SOP')
        Path(temp_agent_dir, 'sops/SOP_pre_proposal_kb_audit.md').write_text('# SOP')

        evaluator = ContractEvaluator(temp_agent_dir)

        # Memory management contracts
        contracts = [
            {'name': 'has_governance', 'assertion': 'directory_exists', 'path': 'governance/'},
            {'name': 'has_planning', 'assertion': 'directory_exists', 'path': 'planning/'},
            {'name': 'has_evolution', 'assertion': 'directory_exists', 'path': '.aget/evolution/'},
            {'name': 'has_step_back_pattern', 'assertion': 'file_exists', 'path': 'docs/patterns/PATTERN_step_back_review_kb.md'},
            {'name': 'has_session_handoff', 'assertion': 'file_exists', 'path': 'sops/SESSION_HANDOFF_AGET.md'},
        ]

        results = [evaluator.evaluate_contract(c) for c in contracts]
        passed = sum(1 for r in results if r.passed)
        assert passed == len(contracts), f"Only {passed}/{len(contracts)} contracts passed"

    def test_domain_knowledge_contracts(self, temp_agent_dir):
        """Domain knowledge contracts should be evaluable."""
        Path(temp_agent_dir, 'docs').mkdir(exist_ok=True)

        evaluator = ContractEvaluator(temp_agent_dir)

        contracts = [
            {'name': 'has_domain_documentation', 'assertion': 'directory_exists', 'path': 'docs/'},
            {'name': 'has_aget_config', 'assertion': 'directory_exists', 'path': '.aget/'},
        ]

        results = [evaluator.evaluate_contract(c) for c in contracts]
        passed = sum(1 for r in results if r.passed)
        assert passed == len(contracts)


class TestMultipleContractEvaluation:
    """Tests for evaluating multiple contracts."""

    def test_all_contracts_evaluated(self, evaluator):
        """All contracts should be evaluated."""
        contracts = [
            {'name': 'c1', 'assertion': 'directory_exists', 'path': '.aget/'},
            {'name': 'c2', 'assertion': 'directory_exists', 'path': 'governance/'},
            {'name': 'c3', 'assertion': 'file_exists', 'path': 'governance/CHARTER.md'},
        ]

        results = [evaluator.evaluate_contract(c) for c in contracts]
        assert len(results) == 3
        assert all(r.passed for r in results)

    def test_partial_pass(self, evaluator):
        """Mixed pass/fail should be properly reported."""
        contracts = [
            {'name': 'c1', 'assertion': 'directory_exists', 'path': '.aget/'},  # pass
            {'name': 'c2', 'assertion': 'directory_exists', 'path': 'nonexistent/'},  # fail
        ]

        results = [evaluator.evaluate_contract(c) for c in contracts]
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        assert len(passed) == 1
        assert len(failed) == 1
