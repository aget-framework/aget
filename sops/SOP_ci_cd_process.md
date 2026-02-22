# SOP: CI/CD Process

**Version**: 1.0
**Created**: 2025-12-28
**Reference Spec**: AGET_CI_SPEC.md
**Change Origin**: L404 (CI Test Isolation Requirements)

---

## Purpose

Define standard operating procedures for CI/CD configuration, maintenance, and troubleshooting in AGET templates and agent repositories.

---

## Scope

**Applies to**: All AGET templates with CI workflows.

**Templates with CI**:
| Template | CI Status | Reference |
|----------|-----------|-----------|
| template-worker-aget | Active | Standard CI |
| template-developer-aget | Active | Standard CI |
| template-advisor-aget | Active | Standard CI |
| template-spec-engineer-aget | Active | Standard CI |
| template-consultant-aget | Active | Enhanced CI |
| template-supervisor-aget | Active | Standard CI |

---

## CI Workflow Structure

### Required Jobs (CAP-CI-003)

Every CI workflow must include:

| Job | Purpose | Required |
|-----|---------|----------|
| `test` | Run pytest suite | Yes |
| `lint` | Run code quality checks | Yes |
| `security` | Run security scans | Yes |
| `integration-test` | Run integration tests | Optional |

### Python Version Matrix (CAP-CI-003-04)

All test jobs must test against:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

---

## Adding CI to a Template

### Step 1: Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### Step 2: Create CI Workflow File

Create `.github/workflows/ci.yml`:

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
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pip install -e .
      - run: pytest tests/ -v

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install ruff
      - run: ruff check . || true

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install bandit
      - run: bandit -r . -ll || true
```

### Step 3: Create Package Configuration

Create or verify `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name='template-name',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'pytest>=7.0.0',
    ],
)
```

### Step 4: Create Init Files

Ensure all package directories have `__init__.py`:

```bash
touch src/__init__.py
touch src/package_name/__init__.py
```

### Step 5: Verify Test Isolation (CAP-CI-001)

Check tests don't import from external packages:

```bash
# Check for invalid imports
grep -r "^from aget\." tests/
grep -r "^import aget\." tests/

# Should return empty (no matches)
```

### Step 6: Test Locally

```bash
# Verify test collection
python3 -m pytest tests/ --collect-only

# Run tests
python3 -m pytest tests/ -v
```

---

## Troubleshooting CI Failures

### ModuleNotFoundError

**Symptom**: `ModuleNotFoundError: No module named 'xxx'`

**Cause**: Tests import from packages not installed in CI.

**Resolution**:
1. Check test imports
2. Remove imports from non-existent packages
3. Use local mocks or fixtures instead

```python
# BAD: Import from non-existent package
from aget.config.commands import SomeCommand

# GOOD: Use local mock
class MockSomeCommand:
    pass
```

### Collection Error

**Symptom**: `pytest: error collecting tests`

**Cause**: Syntax error or import error in test file.

**Resolution**:
1. Run `python3 -m pytest tests/ --collect-only`
2. Fix reported errors
3. Verify test files are valid Python

### @patch Decorator Errors

**Symptom**: `ModuleNotFoundError` during test setup

**Cause**: @patch targeting non-existent module.

**Resolution**:
1. Remove @patch decorators referencing external modules
2. Use local fixtures instead

```python
# BAD: Patch non-existent module
@patch('aget.config.commands.validate.ProjectValidator')
def test_something(self, mock):
    ...

# GOOD: Use fixture
@pytest.fixture
def mock_validator():
    return MockValidator()
```

---

## CI Maintenance

### Regular Checks

| Frequency | Check | Action |
|-----------|-------|--------|
| Per PR | CI passes | Required for merge |
| Weekly | Flaky tests | Investigate failures |
| Monthly | Dependency updates | Review security alerts |
| Per release | All templates pass | Required for release |

### Updating CI Configuration

When updating CI configuration:

1. Update reference template first (template-supervisor-aget)
2. Test changes locally
3. Push and verify CI passes
4. Propagate to other templates (see SOP_template_sync.md)

---

## Validation

### Contract Test Verification

Run contract tests to verify CI compliance:

```bash
cd /path/to/aget-framework/aget
python3 -m pytest tests/ci/test_ci_contract.py -v
```

Expected: 15 tests passing

### Manual Verification Checklist

- [ ] CI workflow file exists at `.github/workflows/ci.yml`
- [ ] Workflow triggers on push to main and develop
- [ ] Workflow triggers on PR to main
- [ ] Test job uses Python version matrix (3.8-3.12)
- [ ] Test job uses pytest
- [ ] Lint job present
- [ ] Security job present
- [ ] All tests pass locally
- [ ] Test collection succeeds (no import errors)

---

## References

- AGET_CI_SPEC.md: CI requirements specification
- L404: CI Test Isolation Requirements
- SOP_template_sync.md: Template synchronization procedures

---

*SOP_ci_cd_process.md v1.0*
*Reference: AGET_CI_SPEC.md | L404*
