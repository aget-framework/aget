# AGET Testing Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Technical (Quality Assurance)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_TESTING_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.1
**Related Specs**: AGET_VALIDATION_SPEC, AGET_CI_SPEC

---

## Abstract

This specification defines testing requirements for the AGET framework, including contract tests, unit tests, V-tests (verification tests), and coverage requirements. It establishes the test pyramid for AGET quality assurance.

## Motivation

Testing challenges observed in practice:

1. **Missing contract tests**: Templates released without compliance verification
2. **Inconsistent test naming**: Hard to understand what tests verify
3. **Low coverage on validators**: Critical validation logic untested
4. **No V-test standard**: Gate completion verification was ad-hoc (L440)

L352 (Requirement-to-Test Traceability), L382 (Theater Ratio), and L440 (Verification Tests) revealed these gaps.

## Scope

**Applies to**: All AGET test suites, validators, and PROJECT_PLANs.

**Defines**:
- Test categories and their purposes
- Contract test requirements
- Unit test requirements
- V-test (verification test) format
- Coverage requirements
- Test naming conventions

**Does not cover**:
- Validation script implementation (see AGET_VALIDATION_SPEC)
- CI pipeline configuration (see AGET_CI_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "testing"
    version: "1.0.0"
    inherits: "aget_core"

  test_types:
    Contract_Test:
      skos:definition: "Test verifying agent/template compliance with specifications"
      aget:location: "tests/test_*_contract.py"
      skos:related: ["CAP-TEST-001"]

    Unit_Test:
      skos:definition: "Test verifying individual function/module behavior"
      aget:location: "tests/test_*.py"
      skos:related: ["CAP-TEST-002"]

    V_Test:
      skos:definition: "Verification test with executable command and expected output"
      aget:naming_pattern: "V{gate}.{test}"
      skos:example: "V0.1, V1.3, V7.0.1"
      skos:related: ["CAP-TEST-006", "L440"]

    Integration_Test:
      skos:definition: "Test verifying interaction between components"
      aget:location: "tests/test_*_integration.py"

  verification:
    Declarative_Completion:
      skos:definition: "Marking deliverable complete via manual checkbox without verification"
      aget:anti_pattern: true
      skos:related: ["L440"]

    Verified_Completion:
      skos:definition: "Marking deliverable complete after executing verification test"
      aget:pattern: true
      skos:related: ["L440", "V_Test"]

  metrics:
    Test_Coverage:
      skos:definition: "Percentage of code exercised by tests"
      aget:target: ">=80% for validators"

    Theater_Ratio:
      skos:definition: "Ratio of missing validators to referenced validators"
      aget:target: "<10%"
      skos:related: ["L433"]
```

---

## Requirements

### CAP-TEST-001: Contract Test Requirements

**SHALL** requirements for contract tests:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-TEST-001-01 | Every template SHALL have contract tests | Ensures template compliance |
| CAP-TEST-001-02 | Contract tests SHALL trace to CAP requirements | L352 traceability |
| CAP-TEST-001-03 | Contract tests SHALL pass before release | Release quality gate |
| CAP-TEST-001-04 | Contract tests SHALL distinguish template vs instance | Different requirements apply |
| CAP-TEST-001-05 | Contract test failures SHALL be classified | Test bug vs compliance gap (L397) |

**Contract Test Structure:**

```python
# tests/test_wake_contract.py

import pytest

class TestWakeContract:
    """Contract tests for wake protocol compliance.

    Traces to: CAP-SESSION-001, R-WAKE-001 to R-WAKE-007
    """

    @pytest.mark.contract
    def test_wake_output_format(self, agent_path):
        """R-WAKE-003: Wake output SHALL include version."""
        # Test implementation
        pass
```

### CAP-TEST-002: Unit Test Requirements

**SHALL** requirements for unit tests:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-TEST-002-01 | Validators SHALL have unit tests | Critical path coverage |
| CAP-TEST-002-02 | Unit tests SHALL be independent | No test order dependencies |
| CAP-TEST-002-03 | Unit tests SHALL be fast (<1s each) | Developer feedback loop |
| CAP-TEST-002-04 | Unit tests SHALL use pytest | Framework standardization |

### CAP-TEST-003: Test Naming Conventions

**SHALL** requirements for test naming:

| ID | Requirement | Pattern | Example |
|----|-------------|---------|---------|
| CAP-TEST-003-01 | Test files | `test_{module}.py` | `test_validate_naming.py` |
| CAP-TEST-003-02 | Contract test files | `test_{domain}_contract.py` | `test_wake_contract.py` |
| CAP-TEST-003-03 | Test functions | `test_{what}_{condition}` | `test_version_is_semver` |
| CAP-TEST-003-04 | Test classes | `Test{Component}` | `TestWakeContract` |

### CAP-TEST-004: Coverage Requirements

**SHALL** requirements for test coverage:

| ID | Requirement | Target | Enforcement |
|----|-------------|--------|-------------|
| CAP-TEST-004-01 | Validator coverage | ≥80% | CI gate |
| CAP-TEST-004-02 | Script coverage | ≥70% | CI gate |
| CAP-TEST-004-03 | Core module coverage | ≥60% | Advisory |
| CAP-TEST-004-04 | Coverage SHALL be measured | pytest-cov | Required |

**Coverage Command:**

```bash
pytest --cov=validation --cov-report=term-missing --cov-fail-under=80 tests/
```

### CAP-TEST-005: CI Test Execution

**SHALL** requirements for CI integration:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-TEST-005-01 | Tests SHALL run on every push | Continuous quality |
| CAP-TEST-005-02 | Test failures SHALL block merge | Quality gate |
| CAP-TEST-005-03 | Coverage report SHALL be generated | Visibility |
| CAP-TEST-005-04 | Test results SHALL be visible | Transparency |

### CAP-TEST-006: V-Test (Verification Test) Requirements

**SHALL** requirements for PROJECT_PLAN verification tests (L440):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-TEST-006-01 | Every gate SHALL have V-tests | Prevents declarative completion |
| CAP-TEST-006-02 | V-tests SHALL be executable | No manual verification |
| CAP-TEST-006-03 | V-tests SHALL have expected output | Clear pass/fail criteria |
| CAP-TEST-006-04 | BLOCKING V-tests SHALL halt on failure | Critical path protection |
| CAP-TEST-006-05 | V-tests SHALL use V{gate}.{test} naming | Standardized identification |

**V-Test Format:**

```markdown
#### V{gate}.{test}: {description}
```bash
{executable_command}
```
**Expected:** {expected_output}
**BLOCKING:** (optional) Do NOT proceed if FAIL
```

**Example:**

```markdown
#### V7.0.1: Manager version is 3.2.0 (R-REL-006)
```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='3.2.0' else 'FAIL')"
```
**Expected:** PASS
**BLOCKING:** Do NOT proceed if FAIL
```

---

## Test Pyramid

```
                    ╱╲
                   ╱  ╲
                  ╱ V  ╲         V-Tests (PROJECT_PLAN gates)
                 ╱ TESTS╲        - Executable verification
                ╱────────╲       - Gate completion criteria
               ╱          ╲
              ╱ CONTRACT   ╲     Contract Tests
             ╱   TESTS      ╲    - Template compliance
            ╱────────────────╲   - CAP requirement traces
           ╱                  ╲
          ╱   INTEGRATION      ╲  Integration Tests
         ╱      TESTS           ╲ - Component interaction
        ╱────────────────────────╲
       ╱                          ╲
      ╱       UNIT TESTS           ╲ Unit Tests
     ╱══════════════════════════════╲ - Function behavior
                                      - Fast, independent
```

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-TEST-001-* | validate_contract_tests.py | Planned |
| CAP-TEST-002-* | pytest collection | Implemented |
| CAP-TEST-003-* | validate_test_naming.py | Planned |
| CAP-TEST-004-* | pytest-cov | Implemented |
| CAP-TEST-005-* | GitHub Actions | Implemented |
| CAP-TEST-006-* | validate_project_plan.py | Planned |

---

## Examples

### Contract Test Example

```python
# tests/test_template_contract.py

import pytest
from pathlib import Path

class TestTemplateContract:
    """Contract tests for template compliance.

    Traces to: CAP-TPL-*, R-TPL-001
    """

    @pytest.fixture
    def template_path(self):
        return Path(__file__).parent.parent

    @pytest.mark.contract
    def test_manifest_exists(self, template_path):
        """CAP-TPL-001: Template SHALL have manifest.yaml."""
        assert (template_path / "manifest.yaml").exists()

    @pytest.mark.contract
    def test_readme_exists(self, template_path):
        """R-TPL-001: Template SHALL have README.md."""
        assert (template_path / "README.md").exists()

    @pytest.mark.contract
    def test_version_is_semver(self, template_path):
        """CAP-TPL-002: Version SHALL follow semver."""
        import json
        import re
        version_file = template_path / ".aget" / "version.json"
        version = json.load(open(version_file))["aget_version"]
        assert re.match(r"^\d+\.\d+\.\d+", version)
```

### V-Test Execution Example

```bash
# Execute all V-tests for a gate
echo "=== Gate 1 V-Tests ==="

echo "V1.1: Categories documented"
categories=$(grep -c "^## Category [A-J]:" specs/AGET_FILE_NAMING_CONVENTIONS.md)
[ "$categories" -ge 9 ] && echo "PASS: $categories" || echo "FAIL: $categories"

echo "V1.2: Domain codes exist"
grep -q "Domain Codes Registry" specs/AGET_FILE_NAMING_CONVENTIONS.md && echo "PASS" || echo "FAIL"

# Aggregate results
echo "=== Gate 1 Summary: 2/2 PASS ==="
```

---

## Anti-Patterns

### Anti-Pattern 1: Declarative Completion (L440)

```markdown
❌ ANTI-PATTERN: Checkbox without verification

### Gate 6 Checklist
- [x] Manager version updated to 3.1.0  ← Marked done, never verified!
```

```markdown
✅ CORRECT: V-test with verification

### Gate 6 Checklist
- [x] V6.0.1 PASS: Manager version is 3.1.0 ✅

#### V6.0.1: Manager version is 3.1.0
```bash
python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])"
```
**Expected:** 3.1.0
**Actual:** 3.1.0 ✅
```

### Anti-Pattern 2: Test Without Trace

```python
❌ ANTI-PATTERN: No requirement trace

def test_something():
    assert True  # What does this verify?
```

```python
✅ CORRECT: Traced to requirement

def test_version_format():
    """CAP-VER-001: Version SHALL be semver format."""
    assert re.match(r"^\d+\.\d+\.\d+", version)
```

---

## References

- L352: Requirement-to-Test Traceability
- L382: Theater Ratio Concept
- L397: Test Bug vs Spec Gap Distinction
- L433: Validator Enforcement Theater Gap
- L440: Manager Migration Verification Gap
- AGET_VALIDATION_SPEC.md
- AGET_CI_SPEC.md

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial specification
- Defined CAP-TEST-001 through CAP-TEST-006
- V-test format from L440
- Test pyramid structure
- Coverage requirements

---

*AGET_TESTING_SPEC.md — Testing standards for AGET framework*
*"A checkbox is not a verification. A passing test is."* — L440
