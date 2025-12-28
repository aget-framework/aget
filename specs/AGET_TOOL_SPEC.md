# AGET Tool Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Tool Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_TOOL_SPEC.md`
**Change Origin**: G-PRE.3.2 P2 Specification Remediation
**Related Specs**: AGET_VALIDATION_SPEC, AGET_GOVERNANCE_HIERARCHY_SPEC

---

## Abstract

This specification defines the requirements for AGET tools (scripts, utilities, patterns). Tools must align with specifications, trace to CAP requirements they implement, and follow standard structure. This prevents tool-spec divergence where tools implement outdated or incorrect behavior.

## Motivation

Tool-spec alignment issues observed in practice:

1. **Opt-in vs mandatory divergence**: wind_down.py uses --create-note as opt-in, but AGET_SESSION_SPEC requires mandatory handoff when pending work exists
2. **Missing spec references**: Scripts lack traceability to specifications they implement
3. **Outdated behavior**: Tools implemented before specs were written continue old patterns
4. **No enforcement**: No mechanism to verify tool implements spec correctly

This specification formalizes the tool-spec alignment pattern validated in G-PRE.3.

## Scope

**Applies to**: All AGET framework tools including:
- Scripts in `scripts/`
- Patterns in `.aget/patterns/`
- Validation tools in `validation/`

**Defines**:
- Tool-spec alignment requirements
- Tool structure standards
- Spec reference requirements
- Tool governance hierarchy position

---

## Vocabulary

Domain terms for the TOOL specification:

```yaml
vocabulary:
  meta:
    domain: "tool"
    version: "1.0.0"
    inherits: "aget_core"

  tool:  # Core concepts
    Tool:
      skos:definition: "Executable script or pattern implementing specification behavior"
      skos:narrower: ["Script", "Pattern", "Validator"]
    Script:
      skos:definition: "Python script in scripts/ or validation/ directory"
      aget:location: "scripts/*.py, validation/*.py"
    Pattern:
      skos:definition: "Executable pattern in .aget/patterns/ directory"
      aget:location: ".aget/patterns/**/*.py"
    Validator:
      skos:definition: "Script that validates compliance with specifications"
      aget:location: "validation/*.py"

  alignment:  # Tool-spec alignment
    Tool_Spec_Alignment:
      skos:definition: "State where tool behavior matches specification requirements"
    Implements_Clause:
      skos:definition: "Docstring section listing CAP requirements tool implements"
    Spec_Reference:
      skos:definition: "Link from tool to specification it implements"
    Alignment_Gap:
      skos:definition: "Divergence between tool behavior and specification"

  governance:  # Hierarchy position
    Governance_Layer:
      skos:definition: "Position in 5-layer governance hierarchy"
      skos:related: ["AGET_GOVERNANCE_HIERARCHY_SPEC"]
    Tool_Authority:
      skos:definition: "What tool can do autonomously vs requires approval"
```

---

## Requirements

### CAP-TOOL-001: Spec Reference Requirement

The SYSTEM shall reference specifications in tool headers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TOOL-001-01 | ubiquitous | The SYSTEM shall include `Implements:` section in tool docstring |
| CAP-TOOL-001-02 | ubiquitous | The `Implements:` section shall list CAP requirement IDs |
| CAP-TOOL-001-03 | ubiquitous | The SYSTEM shall include `See:` section linking to specification file |
| CAP-TOOL-001-04 | optional | WHERE tool has tests, the SYSTEM shall include `Tests:` reference |

**Enforcement**: Code review, linting rules

#### Tool Header Template

```python
#!/usr/bin/env python3
"""
{Tool Description}

Implements: CAP-SESSION-005-01, CAP-SESSION-005-02 (mandatory handoff triggers)
See: aget/specs/AGET_SESSION_SPEC.md
Tests: tests/test_session_protocol.py::TestWindDown

Usage: python3 {tool_name}.py [options]
"""
```

### CAP-TOOL-002: Spec Alignment Requirement

The SYSTEM shall implement specification requirements correctly.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TOOL-002-01 | ubiquitous | The tool shall implement ALL requirements it claims to implement |
| CAP-TOOL-002-02 | prohibited | The tool shall NOT implement behavior contradicting specifications |
| CAP-TOOL-002-03 | conditional | IF spec changes THEN the tool shall be updated to match |
| CAP-TOOL-002-04 | ubiquitous | The tool shall use vocabulary terms consistent with specification |

**Enforcement**: Validation scripts, contract tests

#### Alignment Example

```
AGET_SESSION_SPEC CAP-SESSION-005-01:
  "IF pending PROJECT_PLAN with IN PROGRESS status
   THEN the SYSTEM shall create handoff"

wind_down.py MUST:
  1. Check planning/*.md for IN PROGRESS status
  2. If found, create handoff note automatically
  3. NOT require --create-note flag for this case
```

### CAP-TOOL-003: Tool Structure Standards

The SYSTEM shall follow standard tool structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TOOL-003-01 | ubiquitous | The tool shall use argparse for command-line arguments |
| CAP-TOOL-003-02 | ubiquitous | The tool shall return exit code 0 for success, non-zero for failure |
| CAP-TOOL-003-03 | ubiquitous | The tool shall include --help documentation |
| CAP-TOOL-003-04 | optional | WHERE applicable, the tool shall support --verbose flag |
| CAP-TOOL-003-05 | optional | WHERE applicable, the tool shall support --dry-run flag |

**Enforcement**: Script templates, code review

#### Standard Structure

```python
#!/usr/bin/env python3
"""Tool docstring with Implements and See sections."""

import argparse

def main():
    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # Implementation
    result = do_work(args)

    # Exit code
    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()
```

### CAP-TOOL-004: Governance Hierarchy Position

The SYSTEM shall position tools correctly in governance hierarchy.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TOOL-004-01 | ubiquitous | The tool shall acknowledge specs as authoritative over tool behavior |
| CAP-TOOL-004-02 | conditional | IF tool and spec conflict THEN spec is correct, tool must be fixed |
| CAP-TOOL-004-03 | ubiquitous | The tool shall operate within its layer authority |
| CAP-TOOL-004-04 | prohibited | The tool shall NOT override capability constraints from higher layers |

**Enforcement**: AGET_GOVERNANCE_HIERARCHY_SPEC

#### Governance Position

```
┌─────────────────────────────────────────────────────────────────┐
│                  GOVERNANCE HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Specifications    ← Authoritative                      │
│ Layer 2: Capabilities      ← Derived from specs                 │
│ Layer 3: Patterns          ← Implement capabilities             │
│ Layer 4: SOPs              ← Operationalize patterns            │
│ Layer 5: Tools             ← Execute SOPs (THIS LAYER)          │
└─────────────────────────────────────────────────────────────────┘

Tools implement higher layers; they don't define requirements.
```

### CAP-TOOL-005: Tool Maintenance

The SYSTEM shall maintain tool-spec alignment over time.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TOOL-005-01 | event-driven | WHEN specification changes, the tool owner shall review tool alignment |
| CAP-TOOL-005-02 | ubiquitous | The tool shall version-track which spec version it implements |
| CAP-TOOL-005-03 | conditional | IF tool implements outdated spec THEN the tool shall be updated |
| CAP-TOOL-005-04 | optional | WHERE breaking changes, the tool may include migration path |

**Enforcement**: Release process, deprecation notices

---

## Authority Model

```yaml
authority:
  applies_to: "aget_tools"

  governed_by:
    spec: "AGET_TOOL_SPEC"
    owner: "private-aget-framework-AGET"

  tool_authority:
    autonomous:
      - "implement specification behavior"
      - "add features consistent with specs"
      - "fix bugs in tool implementation"

    requires_approval:
      - action: "add behavior not in spec"
        approver: "spec owner (propose spec change first)"
      - action: "remove spec-required behavior"
        approver: "spec owner"
      - action: "change default that affects spec alignment"
        approver: "spec owner"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-TOOL-001"
      source: "aget_framework"
      statement: "The tool shall NOT contradict specification requirements"
      rationale: "Specs are authoritative; tools implement them"

    - id: "INV-TOOL-002"
      source: "aget_framework"
      statement: "The tool shall NOT omit Implements clause for spec-based behavior"
      rationale: "Traceability is required for maintenance"

    - id: "INV-TOOL-003"
      source: "aget_framework"
      statement: "The tool shall NOT make opt-in what spec requires as mandatory"
      rationale: "Prevents alignment gaps like wind_down.py --create-note"
```

---

## Structural Requirements

```yaml
structure:
  tool_locations:
    - path: "aget/scripts/"
      purpose: "Framework scripts (migration, instantiation)"

    - path: ".aget/patterns/"
      purpose: "Agent-specific patterns (session, release)"

    - path: "validation/"
      purpose: "Validation scripts"

  required_elements:
    docstring:
      - "Implements: CAP-XXX-NNN"
      - "See: path/to/spec.md"

    cli:
      - "--help"
      - "exit code 0/1"
```

---

## Tool Alignment Checklist

Before releasing a tool:

```markdown
## Tool Alignment Checklist

- [ ] Implements clause present with CAP IDs
- [ ] See clause links to specification
- [ ] Tests clause references test file (if applicable)
- [ ] All claimed CAP requirements are implemented
- [ ] No behavior contradicts specification
- [ ] Mandatory spec behaviors are not opt-in
- [ ] Vocabulary terms match specification
- [ ] argparse with --help
- [ ] Exit codes: 0 success, non-zero failure
```

---

## Theoretical Basis

Tool architecture is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Design by Contract** | Tools implement contracts defined by specifications |
| **Separation of Concerns** | Specs define WHAT; tools define HOW |
| **Traceability** | Implements clause creates requirement-to-implementation chain |
| **Hierarchy** | 5-layer governance ensures authority flow |

```yaml
theoretical_basis:
  primary: "Design by Contract"
  secondary:
    - "Separation of Concerns"
    - "Requirements Traceability"
    - "Governance Hierarchy"
  rationale: >
    Specifications define contracts that tools must fulfill. The Implements
    clause creates a traceable link from requirement to implementation.
    The governance hierarchy ensures specs are authoritative over tools,
    preventing implementation from driving requirements.
  references:
    - "AGET_GOVERNANCE_HIERARCHY_SPEC.md"
    - "AGET_VALIDATION_SPEC.md"
```

---

## Validation

```bash
# Check tool has Implements clause
grep -l "Implements:" aget/scripts/*.py .aget/patterns/**/*.py

# Verify alignment (future validation script)
python3 validation/validate_tool_alignment.py .aget/patterns/session/wind_down.py

# Contract tests for tool
python3 -m pytest tests/test_session_protocol.py -v
```

---

## References

- AGET_VALIDATION_SPEC.md (validation requirements)
- AGET_GOVERNANCE_HIERARCHY_SPEC.md (layer authority)
- AGET_SESSION_SPEC.md (example: wind_down.py must implement CAP-SESSION-005)

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "wake_up.py header with Implements"
    - "Tool-spec alignment issues in wind_down.py"
  source_learnings:
    - "G-PRE.3.1 analysis"
  trigger: "G-PRE.3.2 P2 Specification Remediation"
  rationale: "Tool-spec alignment was informal; no specification existed"
```

---

*AGET Tool Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Quality Assurance - G-PRE.3.2*
*"Specs define contracts; tools implement them."*
