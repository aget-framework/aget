# AGET Validation Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Quality Assurance)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_VALIDATION_SPEC.md`
**Change Origin**: G-PRE.3.2 P2 Specification Remediation
**Related Specs**: AGET_TOOL_SPEC, AGET_GOVERNANCE_HIERARCHY_SPEC

---

## Abstract

This specification defines the validation requirements for AGET agents, templates, and specifications. Validation scripts must trace to specific CAP requirements, distinguish test bugs from compliance gaps (L397), and support both template and instance validation modes.

## Motivation

Validation challenges observed in practice:

1. **Arbitrary test subsets**: Scripts check what's convenient, not what's specified
2. **Missing traceability**: No mapping from tests to CAP requirements
3. **Test bug confusion**: Tests fail for wrong reasons (L397)
4. **Template/instance mismatch**: Same tests applied regardless of instance_type

L352 (Requirement-to-Test Traceability) and L397 (Test Bug vs Spec Gap Distinction) revealed these gaps. This specification formalizes validation patterns validated in v3.0.0-beta.3.

## Scope

**Applies to**: All AGET validation scripts and contract tests.

**Defines**:
- Validation traceability requirements
- Validation script structure
- Test categorization (template vs instance)
- Failure classification (test bug vs compliance gap)
- Validation report format

---

## Vocabulary

Domain terms for the VALIDATION specification:

```yaml
vocabulary:
  meta:
    domain: "validation"
    version: "1.0.0"
    inherits: "aget_core"

  validation:  # Core concepts
    Validation_Script:
      skos:definition: "Automated script that checks compliance with specifications"
      aget:location: "validation/*.py"
    Contract_Test:
      skos:definition: "Test that verifies agent contract compliance"
      aget:location: "tests/test_*.py"
    CAP_Requirement:
      skos:definition: "Capability requirement identifier (e.g., CAP-INST-002)"
    Requirement_Traceability:
      skos:definition: "Mapping from test to CAP requirement it validates"
      skos:related: ["L352"]

  classification:  # Failure classification
    Test_Bug:
      skos:definition: "Test failure due to incorrect test assertion"
      skos:related: ["L397"]
    Compliance_Gap:
      skos:definition: "Test failure due to artifact not meeting specification"
      skos:related: ["L397"]
    Spec_Gap:
      skos:definition: "Missing specification for observed behavior"

  categories:  # Test categories
    Template_Test:
      skos:definition: "Test applicable to templates (instance_type: template)"
      skos:note: "Skipped for instances"
    Instance_Test:
      skos:definition: "Test applicable to instances (instance_type: aget)"
      skos:note: "Skipped for templates"
    Universal_Test:
      skos:definition: "Test applicable to both templates and instances"
```

---

## Requirements

### CAP-VAL-001: Requirement Traceability

The SYSTEM shall trace validation tests to CAP requirements.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VAL-001-01 | ubiquitous | The SYSTEM shall document which CAP requirement each test validates |
| CAP-VAL-001-02 | ubiquitous | The SYSTEM shall include CAP ID in test docstring or decorator |
| CAP-VAL-001-03 | conditional | IF test validates multiple requirements THEN the SYSTEM shall list all CAP IDs |
| CAP-VAL-001-04 | ubiquitous | The SYSTEM shall support traceability matrix generation |

**Enforcement**: Test naming conventions, docstrings

#### Traceability Format

```python
def test_archetype_baseline_directories():
    """
    Validates: CAP-INST-002-01, CAP-INST-002-02
    Spec: AGET_INSTANCE_SPEC.md

    Verifies instance has core directories (governance/, sessions/,
    planning/, knowledge/) per archetype baseline compliance.
    """
    ...
```

### CAP-VAL-002: Validation Script Structure

The SYSTEM shall use standard validation script structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VAL-002-01 | ubiquitous | The SYSTEM shall include spec reference in script header |
| CAP-VAL-002-02 | ubiquitous | The SYSTEM shall return exit code 0 for pass, non-zero for fail |
| CAP-VAL-002-03 | ubiquitous | The SYSTEM shall output validation summary with pass/fail counts |
| CAP-VAL-002-04 | optional | WHERE verbose flag, the SYSTEM shall output detailed results |

**Enforcement**: Script templates, code review

#### Script Header Template

```python
#!/usr/bin/env python3
"""
Validate {aspect} for AGET agents.

Implements: CAP-{DOMAIN}-{NNN} (requirements from AGET_{SPEC}_SPEC)
Traces to: AGET_{SPEC}_SPEC.md

Usage: python3 validate_{aspect}.py /path/to/agent [-v]
"""
```

### CAP-VAL-003: Test Categorization

The SYSTEM shall categorize tests by applicability.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VAL-003-01 | ubiquitous | The SYSTEM shall mark tests as template, instance, or universal |
| CAP-VAL-003-02 | conditional | IF instance_type is "template" THEN the SYSTEM shall skip instance tests |
| CAP-VAL-003-03 | conditional | IF instance_type is "aget" THEN the SYSTEM shall skip template tests |
| CAP-VAL-003-04 | ubiquitous | The SYSTEM shall use pytest markers or equivalent for categorization |

**Enforcement**: `@pytest.mark.skipif(is_template())`, test structure

#### Categorization Pattern

```python
import pytest

def is_template():
    """Check if current agent is a template."""
    with open('.aget/version.json') as f:
        return json.load(f).get('instance_type') == 'template'

@pytest.mark.skipif(is_template(), reason="Template, not instance")
def test_persona_configured():
    """Instance-only: Verify persona is configured."""
    ...

@pytest.mark.skipif(not is_template(), reason="Instance, not template")
def test_template_placeholders():
    """Template-only: Verify placeholders exist."""
    ...

def test_version_json_exists():
    """Universal: Both templates and instances need version.json."""
    ...
```

### CAP-VAL-004: Failure Classification

The SYSTEM shall classify validation failures correctly.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VAL-004-01 | event-driven | WHEN test fails, the SYSTEM shall classify as test_bug or compliance_gap |
| CAP-VAL-004-02 | ubiquitous | The SYSTEM shall document classification criteria |
| CAP-VAL-004-03 | conditional | IF test_bug THEN the SYSTEM shall fix test, not create spec |
| CAP-VAL-004-04 | conditional | IF compliance_gap THEN the SYSTEM shall fix artifact or update spec |
| CAP-VAL-004-05 | prohibited | The SYSTEM shall NOT create specs to justify test assertions (L397) |

**Enforcement**: L397 (Test Bug vs Spec Gap Distinction)

#### Classification Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                 FAILURE CLASSIFICATION (L397)                    │
│                                                                  │
│  Test Failed                                                     │
│      │                                                           │
│      ▼                                                           │
│  ┌────────────────────────────────────┐                         │
│  │ Is the test assertion correct?     │                         │
│  └───────────────┬────────────────────┘                         │
│       YES        │         NO                                    │
│                  │                                               │
│                  ▼                                               │
│            ┌─────────────┐                                      │
│            │  TEST BUG   │ → Fix the test                       │
│            └─────────────┘                                      │
│       │                                                          │
│       ▼                                                          │
│  ┌────────────────────────────────────┐                         │
│  │ Does spec exist for this behavior? │                         │
│  └───────────────┬────────────────────┘                         │
│       YES        │         NO                                    │
│                  │                                               │
│                  ▼                                               │
│            ┌─────────────┐                                      │
│            │  SPEC GAP   │ → Consider new spec                  │
│            └─────────────┘                                      │
│       │                                                          │
│       ▼                                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │            COMPLIANCE GAP                               │     │
│  │  Fix artifact (if spec is right)                        │     │
│  │  OR Update spec (if behavior is correct)                │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### CAP-VAL-005: Validation Report Format

The SYSTEM shall use standard validation report format.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VAL-005-01 | ubiquitous | The SYSTEM shall output pass/fail summary |
| CAP-VAL-005-02 | ubiquitous | The SYSTEM shall output total counts (passed, failed, skipped) |
| CAP-VAL-005-03 | conditional | IF failures exist THEN the SYSTEM shall list failure details |
| CAP-VAL-005-04 | optional | WHERE JSON output requested, the SYSTEM shall produce machine-readable report |

**Enforcement**: Script output standards

#### Report Format

```
============================================================
VALIDATION REPORT: {agent_name}
============================================================

Spec: AGET_INSTANCE_SPEC v1.0.0

Checks:
  ✅ CAP-INST-001-01: instance_type is 'aget'
  ✅ CAP-INST-001-03: agent_name populated
  ✅ CAP-INST-002-01: Core directories exist
  ❌ CAP-INST-002-06: operator requires operations/

Summary:
  PASSED: 3
  FAILED: 1
  SKIPPED: 0

RESULT: FAIL
```

---

## Authority Model

```yaml
authority:
  applies_to: "validation_scripts"

  governed_by:
    spec: "AGET_VALIDATION_SPEC"
    owner: "aget-framework"

  agent_authority:
    autonomous:
      - "run validation scripts"
      - "classify failures"
      - "fix test bugs"

    requires_approval:
      - action: "create new spec for spec gap"
        approver: "spec owner"
      - action: "modify existing spec"
        approver: "spec owner"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-VAL-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT create specs to justify test assertions"
      rationale: "L397: Test bugs require test fixes, not spec creation"

    - id: "INV-VAL-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT skip traceability for new tests"
      rationale: "L352: All tests must trace to CAP requirements"

    - id: "INV-VAL-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT mix template and instance validations"
      rationale: "Different requirements apply to different instance_types"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "validation/"
      purpose: "Validation scripts"

    - path: "tests/"
      purpose: "Contract tests"

  scripts:
    - path: "validation/validate_spec_format.py"
      validates: "AGET_SPEC_FORMAT"

    - path: "validation/validate_template_manifest.py"
      validates: "AGET_TEMPLATE_SPEC"

    - path: "validation/validate_template_instance.py"
      validates: "AGET_INSTANCE_SPEC, AGET_TEMPLATE_SPEC"

    - path: "validation/validate_version_consistency.py"
      validates: "AGET_COMPATIBILITY_SPEC"
```

---

## Theoretical Basis

Validation architecture is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Requirements Traceability** | Every test maps to a requirement; gaps are visible |
| **Defensive Programming** | Explicit failure classification prevents wrong fixes |
| **Separation of Concerns** | Template vs instance tests separated by category |
| **Observability** | Validation reports provide visibility into compliance state |

```yaml
theoretical_basis:
  primary: "Requirements Traceability"
  secondary:
    - "Defensive Programming"
    - "Separation of Concerns"
    - "Observability"
  rationale: >
    Validation specification treats tests as requirement verifiers, not
    arbitrary checks. Traceability (L352) ensures coverage. Classification
    (L397) prevents wasted effort. Categorization ensures appropriate tests
    run for each context.
  references:
    - "L352_requirement_test_traceability.md"
    - "L397_test_bug_vs_spec_gap_distinction.md"
```

---

## Validation

```bash
# Run all validation scripts
python3 validation/validate_spec_format.py aget/specs/*.md
python3 validation/validate_template_instance.py /path/to/agent -v

# Run contract tests
python3 -m pytest tests/ -v

# Generate traceability report (future)
python3 validation/generate_traceability_matrix.py
```

---

## References

- AGET_TOOL_SPEC.md (tool-spec alignment)
- L352: Requirement-to-Test Traceability
- L397: Test Bug vs Spec Gap Distinction
- L391: Template vs Instance Distinction

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "validate_spec_format.py"
    - "validate_template_instance.py"
    - "@pytest.mark.skipif patterns"
  source_learnings:
    - "L352"
    - "L391"
    - "L397"
  trigger: "G-PRE.3.2 P2 Specification Remediation"
  rationale: "Validation practices were inconsistent; no specification existed"
```

---

*AGET Validation Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Quality Assurance - G-PRE.3.2*
*"Tests validate requirements; requirements don't justify tests."*
