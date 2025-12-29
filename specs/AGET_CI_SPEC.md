# AGET CI Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Quality Assurance)
**Format Version**: 1.2
**Created**: 2025-12-28
**Updated**: 2025-12-28
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_CI_SPEC.md`
**Change Origin**: L404 (CI Test Isolation Requirements)
**Related Specs**: AGET_VALIDATION_SPEC, AGET_TEMPLATE_SPEC

---

## Abstract

This specification defines the Continuous Integration (CI) requirements for AGET templates and agent repositories. It establishes standards for test isolation, package configuration, CI workflow structure, and validation to prevent import errors and ensure consistent CI behavior across the framework.

## Motivation

On 2025-12-28, all 5 AGET templates with CI failed simultaneously due to `ModuleNotFoundError: No module named 'aget'`. Root cause analysis (L404) revealed:

1. Tests imported from non-existent `aget.*` modules
2. Package directories lacked `__init__.py` files
3. `setup.py` didn't configure package discovery correctly
4. No specification existed to define CI requirements

This specification formalizes CI patterns validated during the remediation and prevents recurrence.

## Scope

**Applies to**: All AGET templates and agent repositories with CI.

**Defines**:
- Test isolation requirements
- Package configuration requirements
- CI workflow structure
- CI trigger patterns
- Validation and enforcement

**Does NOT Define**:
- Deployment pipelines
- Release automation (see PROCESS_release_workflow.yaml)
- Code review processes

---

## Vocabulary

Domain terms for the CI specification:

```yaml
vocabulary:
  meta:
    domain: "ci"
    version: "1.0.0"
    inherits: "aget_core"

  persona:  # D1: WHO runs CI
    CI_System:
      skos:definition: "Automated system executing CI workflows"
      skos:example: "GitHub Actions"
    CI_Workflow:
      skos:definition: "Complete CI pipeline definition"
      aget:location: ".github/workflows/*.yml"

  memory:  # D2: WHAT CI knows
    Package_Configuration:
      skos:definition: "Python package setup file"
      aget:location: "setup.py or pyproject.toml"
    Test_Matrix:
      skos:definition: "Set of Python versions for testing"
      skos:example: "['3.8', '3.9', '3.10', '3.11', '3.12']"
    Init_File:
      skos:definition: "__init__.py file marking directory as Python package"

  reasoning:  # D3: HOW CI decides
    Test_Isolation:
      skos:definition: "Requirement for tests to be self-contained without external imports"
      skos:related: ["L404"]
    Collection_Error:
      skos:definition: "pytest failed to import test modules"
    Import_Error:
      skos:definition: "Module not found during test collection"

  skills:  # D4: WHAT CI does
    CI_Job:
      skos:definition: "Individual job within CI workflow"
      skos:narrower: ["Test_Job", "Lint_Job", "Security_Job", "Integration_Test_Job"]
    CI_Step:
      skos:definition: "Individual step within CI job"
    Test_Job:
      skos:definition: "CI job that runs pytest test suite"
    Lint_Job:
      skos:definition: "CI job that runs code quality checks"
    Security_Job:
      skos:definition: "CI job that runs security scans"

  context:  # D5: WHERE/WHEN CI runs
    CI_Trigger:
      skos:definition: "Event that initiates CI execution"
      skos:narrower: ["Push_Trigger", "PR_Trigger"]
    Push_Trigger:
      skos:definition: "CI trigger on git push to branch"
    PR_Trigger:
      skos:definition: "CI trigger on pull request"
```

---

## Requirements

### CAP-CI-001: Test Isolation

The SYSTEM shall ensure Test_Isolation for all template tests.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CI-001-01 | ubiquitous | The SYSTEM shall not import from external packages in template tests unless package is installed |
| CAP-CI-001-02 | ubiquitous | The SYSTEM shall use relative imports or sys.path manipulation for local modules |
| CAP-CI-001-03 | conditional | IF test requires package import THEN the SYSTEM shall install package via setup.py |
| CAP-CI-001-04 | ubiquitous | The SYSTEM shall not use @patch decorators referencing non-existent modules |

**Enforcement**: Contract test `test_ci_test_isolation`

**Anti-Pattern** (L404):
```python
# BAD: Import from non-existent package
from aget.config.commands.init import InitCommand

# BAD: Patch non-existent module
@patch('aget.config.commands.validate.ProjectValidator')
def test_something(self, mock):
    ...
```

**Correct Pattern**:
```python
# GOOD: Use local mock or installed package
class MockInitCommand:
    ...

# GOOD: Test actual local code
from scripts.validate_patterns import validate
```

### CAP-CI-002: Package Configuration

The SYSTEM shall correctly configure Package_Configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CI-002-01 | ubiquitous | The SYSTEM shall include Init_File in all package directories |
| CAP-CI-002-02 | optional | WHERE setup.py uses src/ layout, the SYSTEM shall set `package_dir={'': 'src'}` |
| CAP-CI-002-03 | ubiquitous | The SYSTEM shall use `find_packages()` with correct `where` parameter |
| CAP-CI-002-04 | ubiquitous | The SYSTEM shall declare Python version requirements in setup.py |

**Enforcement**: Contract test `test_ci_package_configuration`

**Correct setup.py Pattern**:
```python
from setuptools import setup, find_packages

setup(
    name='template-name',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    ...
)
```

### CAP-CI-003: CI Workflow Structure

WHEN CI_Trigger occurs, the SYSTEM shall execute CI_Workflow.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CI-003-01 | ubiquitous | The SYSTEM shall include Test_Job in CI_Workflow |
| CAP-CI-003-02 | ubiquitous | The SYSTEM shall include Lint_Job in CI_Workflow |
| CAP-CI-003-03 | ubiquitous | The SYSTEM shall include Security_Job in CI_Workflow |
| CAP-CI-003-04 | ubiquitous | The SYSTEM shall test against Python_Version_Matrix [3.8, 3.9, 3.10, 3.11, 3.12] |
| CAP-CI-003-05 | ubiquitous | The SYSTEM shall use pytest for Test_Job |
| CAP-CI-003-06 | optional | WHERE template has integration tests, the SYSTEM shall include Integration_Test_Job |

**Enforcement**: Contract test `test_ci_workflow_structure`

**Standard CI Workflow Structure**:
```yaml
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
```

### CAP-CI-004: CI Triggers

The SYSTEM shall respond to standard CI_Triggers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CI-004-01 | event-driven | WHEN Push_Trigger on main branch, the SYSTEM shall execute CI_Workflow |
| CAP-CI-004-02 | event-driven | WHEN Push_Trigger on develop branch, the SYSTEM shall execute CI_Workflow |
| CAP-CI-004-03 | event-driven | WHEN PR_Trigger to main branch, the SYSTEM shall execute CI_Workflow |

**Enforcement**: CI workflow file validation

### CAP-CI-005: CI Validation

The SYSTEM shall validate CI configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CI-005-01 | ubiquitous | The SYSTEM shall verify test collection succeeds before running tests |
| CAP-CI-005-02 | conditional | IF Collection_Error occurs THEN the SYSTEM shall report Import_Error details |
| CAP-CI-005-03 | ubiquitous | The SYSTEM shall fail CI if any test fails |
| CAP-CI-005-04 | optional | WHERE lint errors exist, the SYSTEM may report as warning (non-blocking) |

**Enforcement**: Contract test `test_ci_validation`

---

## Validation

### Test Collection Check

Before running tests, verify collection succeeds:

```bash
# Verify test collection
python3 -m pytest tests/ --collect-only 2>&1 | grep -E "error|Error"

# Should return empty (no errors)
```

### CI Workflow Validation

```bash
# Check CI file exists
ls .github/workflows/ci.yml

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

---

## Traceability

| Requirement | Contract Test | Enforcement |
|-------------|---------------|-------------|
| CAP-CI-001-01 | test_ci_test_isolation | grep for external imports |
| CAP-CI-001-02 | test_ci_test_isolation | import analysis |
| CAP-CI-001-03 | test_ci_test_isolation | setup.py validation |
| CAP-CI-001-04 | test_ci_test_isolation | @patch decorator analysis |
| CAP-CI-002-01 | test_ci_package_configuration | __init__.py check |
| CAP-CI-002-02 | test_ci_package_configuration | setup.py parsing |
| CAP-CI-002-03 | test_ci_package_configuration | find_packages validation |
| CAP-CI-002-04 | test_ci_package_configuration | python_requires check |
| CAP-CI-003-01 | test_ci_workflow_structure | workflow file parsing |
| CAP-CI-003-02 | test_ci_workflow_structure | job existence check |
| CAP-CI-003-03 | test_ci_workflow_structure | job existence check |
| CAP-CI-003-04 | test_ci_workflow_structure | matrix validation |
| CAP-CI-004-01 | test_ci_triggers | trigger validation |
| CAP-CI-004-02 | test_ci_triggers | trigger validation |
| CAP-CI-004-03 | test_ci_triggers | trigger validation |
| CAP-CI-005-01 | test_ci_validation | collection check |
| CAP-CI-005-03 | test_ci_validation | exit code check |

---

## Learnings Applied

| L-doc | Lesson | Application |
|-------|--------|-------------|
| L404 | CI Test Isolation | CAP-CI-001 test isolation requirements |
| L352 | Requirement-to-Test Traceability | Traceability matrix above |
| L397 | Test Bug vs Spec Gap | CAP-CI-005-02 error reporting |

---

## References

- L404: CI Test Isolation Requirements
- AGET_VALIDATION_SPEC.md: Test categorization patterns
- AGET_TEMPLATE_SPEC.md: Template structure requirements
- AGET_CONTROLLED_VOCABULARY.md: CI/CD Terms section
- SOP_ci_cd_process.md: CI/CD operational procedures

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-28 | Initial release (L404 remediation) |

---

*AGET_CI_SPEC.md — CI requirements for AGET framework*
*Format Version: 1.2 | Category: Standards (Quality Assurance)*
