"""
Contract Tests for Release Observability Scripts (CAP-REL-021 through CAP-REL-025)

Verifies the Gate 3 release observability scripts exist, have correct structure,
and pass self-tests. These scripts implement the L605 remediation.

Specification: AGET_RELEASE_SPEC.md (CAP-REL-021 through CAP-REL-025)
Source: PROJECT_PLAN_v3.6.0_release_v1.0.md, Gate 3.5 R4
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

import pytest


def get_scripts_dir() -> Path:
    """Get the scripts/ directory path."""
    return Path(__file__).resolve().parent.parent / 'scripts'


SCRIPTS_DIR = get_scripts_dir()


# ============================================================
# CAP-REL-021: Persistent Validation Logging
# ============================================================

class TestValidationLogger:
    """Contract tests for scripts/validation_logger.py (CAP-REL-021)."""

    SCRIPT = SCRIPTS_DIR / 'validation_logger.py'

    def test_script_exists(self):
        """validation_logger.py exists in scripts/."""
        assert self.SCRIPT.is_file(), f"Missing: {self.SCRIPT}"

    def test_has_help(self):
        """validation_logger.py supports --help."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--help'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert 'CAP-REL-021' in result.stdout

    def test_self_test_passes(self):
        """validation_logger.py --test passes."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--test'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Self-test failed: {result.stdout}\n{result.stderr}"
        assert 'PASS' in result.stdout

    def test_docstring_has_exit_codes(self):
        """validation_logger.py docstring documents exit codes."""
        content = self.SCRIPT.read_text()
        assert 'Exit Codes:' in content or 'Exit codes:' in content.lower()

    def test_has_cap_reference(self):
        """validation_logger.py references its CAP specification."""
        content = self.SCRIPT.read_text()
        assert 'CAP-REL-021' in content


# ============================================================
# CAP-REL-022: Gate Execution Enforcement
# ============================================================

class TestRunGate:
    """Contract tests for scripts/run_gate.py (CAP-REL-022)."""

    SCRIPT = SCRIPTS_DIR / 'run_gate.py'

    def test_script_exists(self):
        """run_gate.py exists in scripts/."""
        assert self.SCRIPT.is_file(), f"Missing: {self.SCRIPT}"

    def test_has_help(self):
        """run_gate.py supports --help."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--help'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert 'CAP-REL-022' in result.stdout

    def test_self_test_passes(self):
        """run_gate.py --test passes."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--test'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Self-test failed: {result.stdout}\n{result.stderr}"
        assert 'PASS' in result.stdout

    def test_docstring_has_exit_codes(self):
        """run_gate.py docstring documents exit codes."""
        content = self.SCRIPT.read_text()
        assert 'Exit Codes:' in content or 'Exit codes:' in content.lower()

    def test_has_cap_reference(self):
        """run_gate.py references its CAP specification."""
        content = self.SCRIPT.read_text()
        assert 'CAP-REL-022' in content


# ============================================================
# CAP-REL-023: Release State Snapshots
# ============================================================

class TestReleaseSnapshot:
    """Contract tests for scripts/release_snapshot.py (CAP-REL-023)."""

    SCRIPT = SCRIPTS_DIR / 'release_snapshot.py'

    def test_script_exists(self):
        """release_snapshot.py exists in scripts/."""
        assert self.SCRIPT.is_file(), f"Missing: {self.SCRIPT}"

    def test_has_help(self):
        """release_snapshot.py supports --help."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--help'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert 'CAP-REL-023' in result.stdout

    def test_self_test_passes(self):
        """release_snapshot.py --test passes."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--test'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Self-test failed: {result.stdout}\n{result.stderr}"
        assert 'PASS' in result.stdout

    def test_docstring_has_exit_codes(self):
        """release_snapshot.py docstring documents exit codes."""
        content = self.SCRIPT.read_text()
        assert 'Exit Codes:' in content or 'Exit codes:' in content.lower()

    def test_has_cap_reference(self):
        """release_snapshot.py references its CAP specification."""
        content = self.SCRIPT.read_text()
        assert 'CAP-REL-023' in content


# ============================================================
# CAP-REL-024: Propagation Audit
# ============================================================

class TestPropagationAudit:
    """Contract tests for scripts/propagation_audit.py (CAP-REL-024)."""

    SCRIPT = SCRIPTS_DIR / 'propagation_audit.py'

    def test_script_exists(self):
        """propagation_audit.py exists in scripts/."""
        assert self.SCRIPT.is_file(), f"Missing: {self.SCRIPT}"

    def test_has_help(self):
        """propagation_audit.py supports --help."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--help'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert 'CAP-REL-024' in result.stdout

    def test_self_test_passes(self):
        """propagation_audit.py --test passes."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--test'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Self-test failed: {result.stdout}\n{result.stderr}"
        assert 'PASS' in result.stdout

    def test_docstring_has_exit_codes(self):
        """propagation_audit.py docstring documents exit codes."""
        content = self.SCRIPT.read_text()
        assert 'Exit Codes:' in content or 'Exit codes:' in content.lower()

    def test_has_cap_reference(self):
        """propagation_audit.py references its CAP specification."""
        content = self.SCRIPT.read_text()
        assert 'CAP-REL-024' in content


# ============================================================
# CAP-REL-025: Healthcheck Result Persistence
# ============================================================

class TestHealthLogger:
    """Contract tests for scripts/health_logger.py (CAP-REL-025)."""

    SCRIPT = SCRIPTS_DIR / 'health_logger.py'

    def test_script_exists(self):
        """health_logger.py exists in scripts/."""
        assert self.SCRIPT.is_file(), f"Missing: {self.SCRIPT}"

    def test_has_help(self):
        """health_logger.py supports --help."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--help'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert 'CAP-REL-025' in result.stdout

    def test_self_test_passes(self):
        """health_logger.py --test passes."""
        result = subprocess.run(
            [sys.executable, str(self.SCRIPT), '--test'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Self-test failed: {result.stdout}\n{result.stderr}"
        assert 'PASS' in result.stdout

    def test_docstring_has_exit_codes(self):
        """health_logger.py docstring documents exit codes."""
        content = self.SCRIPT.read_text()
        assert 'Exit Codes:' in content or 'Exit codes:' in content.lower()

    def test_has_cap_reference(self):
        """health_logger.py references its CAP specification."""
        content = self.SCRIPT.read_text()
        assert 'CAP-REL-025' in content


# ============================================================
# Cross-cutting: SCRIPT_REGISTRY compliance
# ============================================================

class TestRegistryCompliance:
    """Verify all Gate 3 scripts are registered in SCRIPT_REGISTRY.yaml."""

    REGISTRY = Path(__file__).resolve().parent.parent / 'SCRIPT_REGISTRY.yaml'
    GATE3_SCRIPTS = [
        'scripts/validation_logger.py',
        'scripts/run_gate.py',
        'scripts/release_snapshot.py',
        'scripts/propagation_audit.py',
        'scripts/health_logger.py',
    ]

    def test_registry_exists(self):
        """SCRIPT_REGISTRY.yaml exists."""
        assert self.REGISTRY.is_file()

    def test_gate3_scripts_registered(self):
        """All Gate 3 scripts are listed in SCRIPT_REGISTRY.yaml."""
        content = self.REGISTRY.read_text()
        missing = [s for s in self.GATE3_SCRIPTS if s not in content]
        assert not missing, f"Unregistered scripts: {missing}"

    def test_no_hardcoded_paths(self):
        """No Gate 3 scripts contain hardcoded user paths."""
        for script_rel in self.GATE3_SCRIPTS:
            script = Path(__file__).resolve().parent.parent / script_rel
            if script.is_file():
                content = script.read_text()
                assert '/Users/' not in content, f"Hardcoded path in {script_rel}"
