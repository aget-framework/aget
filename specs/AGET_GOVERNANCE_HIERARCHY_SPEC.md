# AGET Governance Hierarchy Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Governance Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_GOVERNANCE_HIERARCHY_SPEC.md`
**Change Origin**: G-PRE.3.2 P2 Specification Remediation
**Related Specs**: AGET_TOOL_SPEC, AGET_VALIDATION_SPEC

---

## Abstract

This specification defines the five-layer governance hierarchy for the AGET framework. The hierarchy establishes authority flow from specifications (authoritative) through capabilities, patterns, SOPs, to tools (implementational). This prevents authority confusion and ensures consistent enforcement.

## Motivation

Governance hierarchy issues observed in practice:

1. **Undefined layer relationships**: No clear authority between specs, capabilities, patterns, SOPs, and tools
2. **Conflict resolution ambiguity**: When tool and spec conflict, which wins?
3. **Inheritance confusion**: How do capabilities inherit from specifications?
4. **Enforcement gaps**: Who enforces what at each layer?

This specification formalizes the governance structure validated across v2.x and v3.0 development.

## Scope

**Applies to**: All AGET framework governance artifacts.

**Defines**:
- Five-layer governance hierarchy
- Authority flow between layers
- Conflict resolution rules
- Layer characteristics and responsibilities

---

## Vocabulary

Domain terms for the GOVERNANCE HIERARCHY specification:

```yaml
vocabulary:
  meta:
    domain: "governance_hierarchy"
    version: "1.0.0"
    inherits: "aget_core"

  hierarchy:  # Layer structure
    Governance_Layer:
      skos:definition: "Level in the five-layer governance hierarchy"
      skos:narrower: ["Specification_Layer", "Capability_Layer", "Pattern_Layer", "SOP_Layer", "Tool_Layer"]
    Authority_Flow:
      skos:definition: "Direction of authority from higher to lower layers"
      skos:note: "Higher layers are authoritative over lower layers"
    Layer_Conflict:
      skos:definition: "Disagreement between artifacts at different layers"

  layers:  # The five layers
    Specification_Layer:
      skos:definition: "Layer 1: Formal requirements (EARS format)"
      aget:location: "aget/specs/AGET_*_SPEC.md"
      skos:altLabel: "L1"
    Capability_Layer:
      skos:definition: "Layer 2: Agent capabilities derived from specs"
      aget:location: ".aget/skills/capabilities.yaml"
      skos:altLabel: "L2"
    Pattern_Layer:
      skos:definition: "Layer 3: Reusable patterns implementing capabilities"
      aget:location: ".aget/patterns/, docs/patterns/"
      skos:altLabel: "L3"
    SOP_Layer:
      skos:definition: "Layer 4: Standard operating procedures operationalizing patterns"
      aget:location: "sops/"
      skos:altLabel: "L4"
    Tool_Layer:
      skos:definition: "Layer 5: Executable tools implementing SOPs"
      aget:location: "scripts/, validation/, .aget/patterns/**/*.py"
      skos:altLabel: "L5"

  authority:  # Authority concepts
    Authoritative:
      skos:definition: "Higher layer that defines requirements for lower layers"
    Implementational:
      skos:definition: "Lower layer that implements requirements from higher layers"
    Override:
      skos:definition: "When lower layer behavior differs from higher layer requirement"
```

---

## Requirements

### CAP-GOV-001: Five-Layer Hierarchy

The SYSTEM shall implement a five-layer governance hierarchy.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-001-01 | ubiquitous | The SYSTEM shall define Layer 1 as Specifications |
| CAP-GOV-001-02 | ubiquitous | The SYSTEM shall define Layer 2 as Capabilities |
| CAP-GOV-001-03 | ubiquitous | The SYSTEM shall define Layer 3 as Patterns |
| CAP-GOV-001-04 | ubiquitous | The SYSTEM shall define Layer 4 as SOPs |
| CAP-GOV-001-05 | ubiquitous | The SYSTEM shall define Layer 5 as Tools |

**Enforcement**: Governance documentation, artifact placement

#### Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIVE-LAYER GOVERNANCE HIERARCHY                       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 1: SPECIFICATIONS                                         │    │
│  │ What: Formal EARS requirements (CAP-XXX-NNN)                    │    │
│  │ Where: aget/specs/AGET_*_SPEC.md                                │    │
│  │ Authority: AUTHORITATIVE - defines correct behavior             │    │
│  │ Examples: AGET_INSTANCE_SPEC, AGET_SESSION_SPEC                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼ (derive from)                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 2: CAPABILITIES                                           │    │
│  │ What: Agent capabilities declared in YAML                       │    │
│  │ Where: .aget/skills/capabilities.yaml                           │    │
│  │ Authority: Derived from specs, enforced by framework            │    │
│  │ Examples: CAP-INST-002 → archetype_baseline capability          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼ (implement via)                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 3: PATTERNS                                               │    │
│  │ What: Reusable approaches documented in markdown                │    │
│  │ Where: .aget/patterns/, docs/patterns/                          │    │
│  │ Authority: Implement capabilities, inform SOPs                  │    │
│  │ Examples: PATTERN_step_back_review_kb.md, L395 migration pattern│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼ (operationalize as)                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 4: SOPs (Standard Operating Procedures)                   │    │
│  │ What: Step-by-step procedures for humans and agents             │    │
│  │ Where: sops/                                                    │    │
│  │ Authority: Operationalize patterns for execution                │    │
│  │ Examples: SOP_release_process.md, SOP_session_handoff.md        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼ (execute via)                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 5: TOOLS                                                  │    │
│  │ What: Executable scripts implementing SOPs                      │    │
│  │ Where: scripts/, validation/, .aget/patterns/**/*.py            │    │
│  │ Authority: IMPLEMENTATIONAL - executes higher layer decisions   │    │
│  │ Examples: wind_down.py, validate_template_instance.py           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### CAP-GOV-002: Authority Flow

The SYSTEM shall enforce authority flow from higher to lower layers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-002-01 | ubiquitous | Higher layers shall be authoritative over lower layers |
| CAP-GOV-002-02 | conditional | IF layers conflict THEN higher layer is correct |
| CAP-GOV-002-03 | prohibited | Lower layers shall NOT override higher layer requirements |
| CAP-GOV-002-04 | ubiquitous | The SYSTEM shall trace from tools up to specifications |
| CAP-GOV-002-05 | conditional | IF lower layer needs change THEN propose change to higher layer |

**Enforcement**: Code review, traceability, AGET_TOOL_SPEC

#### Authority Matrix

```
┌───────────────────────────────────────────────────────────────────────┐
│                        AUTHORITY MATRIX                                │
├─────────────┬───────────────────────────────────────────────────────┤
│ Layer       │ Can Modify             │ Cannot Modify               │
├─────────────┼───────────────────────────────────────────────────────┤
│ Spec (L1)   │ Own content            │ N/A (top authority)         │
│ Capability  │ Own declarations       │ Spec requirements           │
│ Pattern     │ Implementation details │ Capability definitions      │
│ SOP         │ Procedures             │ Pattern constraints         │
│ Tool (L5)   │ How to execute         │ What to execute             │
└─────────────┴───────────────────────────────────────────────────────┘
```

### CAP-GOV-003: Layer Characteristics

The SYSTEM shall define characteristics for each layer.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-003-01 | ubiquitous | Specifications shall use EARS patterns and CAP IDs |
| CAP-GOV-003-02 | ubiquitous | Capabilities shall use YAML format with inviolables |
| CAP-GOV-003-03 | ubiquitous | Patterns shall document reusable approaches |
| CAP-GOV-003-04 | ubiquitous | SOPs shall provide step-by-step procedures |
| CAP-GOV-003-05 | ubiquitous | Tools shall implement Implements clause per AGET_TOOL_SPEC |

**Enforcement**: Format validators, templates

#### Layer Characteristics Table

| Layer | Format | ID Pattern | Owner | Versioned |
|-------|--------|------------|-------|-----------|
| Specification | EARS + SKOS markdown | CAP-XXX-NNN | Framework | Yes |
| Capability | YAML | capability-name | Agent | Yes (via manifest) |
| Pattern | Markdown | PATTERN_name | Framework/Agent | Via L-doc |
| SOP | Markdown | SOP_name | Agent | Via governance |
| Tool | Python | Script name | Framework/Agent | Via version.json |

### CAP-GOV-004: Conflict Resolution

The SYSTEM shall resolve conflicts between layers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-004-01 | conditional | IF Tool conflicts with Spec THEN Spec is correct |
| CAP-GOV-004-02 | conditional | IF SOP conflicts with Pattern THEN Pattern is correct |
| CAP-GOV-004-03 | conditional | IF Capability conflicts with Spec THEN Spec is correct |
| CAP-GOV-004-04 | ubiquitous | Conflicts shall be resolved by updating lower layer |
| CAP-GOV-004-05 | conditional | IF lower layer proposes change THEN higher layer owner decides |

**Enforcement**: Governance review, L397 classification

#### Conflict Resolution Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFLICT RESOLUTION                           │
│                                                                  │
│  Detected: Tool behavior ≠ Specification requirement             │
│                                                                  │
│  Step 1: Classify conflict                                       │
│          ├── Tool is wrong (typical) → Fix tool                  │
│          └── Spec is incomplete → Propose spec update            │
│                                                                  │
│  Step 2: If tool is wrong                                        │
│          ├── Update tool to match spec                           │
│          ├── Update Implements clause                            │
│          └── Add/update tests                                    │
│                                                                  │
│  Step 3: If spec is incomplete                                   │
│          ├── Document gap                                        │
│          ├── Propose CAP requirement to spec owner               │
│          ├── Get approval                                        │
│          └── Update spec, then update tool                       │
│                                                                  │
│  Key Principle: Never change tool to define new requirement      │
│                 (that's spec's job)                              │
└─────────────────────────────────────────────────────────────────┘
```

### CAP-GOV-005: Cross-Layer Traceability

The SYSTEM shall maintain traceability across layers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-005-01 | ubiquitous | Tools shall trace to SOPs or Specs via Implements clause |
| CAP-GOV-005-02 | ubiquitous | SOPs shall reference patterns they operationalize |
| CAP-GOV-005-03 | ubiquitous | Patterns shall reference capabilities they implement |
| CAP-GOV-005-04 | ubiquitous | Capabilities shall reference specs they derive from |
| CAP-GOV-005-05 | ubiquitous | Traceability shall be verifiable via validation scripts |

**Enforcement**: L352 (Requirement-to-Test Traceability), AGET_VALIDATION_SPEC

#### Traceability Chain

```
AGET_SESSION_SPEC
    │
    │ CAP-SESSION-005: Mandatory handoff triggers
    │
    ▼
capability-session-protocols.yaml
    │
    │ capability: "session_handoff_when_pending"
    │
    ▼
PATTERN_session_handoff.md
    │
    │ Pattern: Create handoff when pending work
    │
    ▼
SOP_session_end.md
    │
    │ Step 4: If pending work, create session note
    │
    ▼
wind_down.py
    │
    │ Implements: CAP-SESSION-005-01
    │ See: AGET_SESSION_SPEC.md
```

---

## Authority Model

```yaml
authority:
  applies_to: "governance_artifacts"

  governed_by:
    spec: "AGET_GOVERNANCE_HIERARCHY_SPEC"
    owner: "aget-framework"

  layer_authority:
    specification:
      can: "define requirements (CAP-*)"
      cannot: "N/A - top of hierarchy"
      owner: "framework owner"

    capability:
      can: "declare agent capabilities"
      cannot: "contradict specification"
      owner: "agent instance"

    pattern:
      can: "document implementation approaches"
      cannot: "change capability definitions"
      owner: "framework or agent"

    sop:
      can: "define operational procedures"
      cannot: "override pattern constraints"
      owner: "agent instance"

    tool:
      can: "implement execution"
      cannot: "define new requirements"
      owner: "framework or agent"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-GOV-001"
      source: "aget_framework"
      statement: "Lower layers shall NOT override higher layer requirements"
      rationale: "Authority flows down, not up"

    - id: "INV-GOV-002"
      source: "aget_framework"
      statement: "Tools shall NOT define requirements (that's spec's job)"
      rationale: "Separation of concerns between layers"

    - id: "INV-GOV-003"
      source: "aget_framework"
      statement: "Conflicts shall be resolved by updating lower layer"
      rationale: "Higher layers are authoritative"

    - id: "INV-GOV-004"
      source: "aget_framework"
      statement: "Traceability shall NOT be broken across layers"
      rationale: "L352: All implementations trace to requirements"
```

---

## Structural Requirements

```yaml
structure:
  layer_locations:
    specification:
      path: "aget/specs/AGET_*_SPEC.md"
      format: "EARS + SKOS markdown"

    capability:
      path: ".aget/skills/capabilities.yaml"
      format: "YAML"

    pattern:
      paths:
        - ".aget/patterns/"
        - "docs/patterns/"
      format: "Markdown"

    sop:
      path: "sops/"
      format: "Markdown"

    tool:
      paths:
        - "aget/scripts/"
        - "validation/"
        - ".aget/patterns/**/*.py"
      format: "Python"
```

---

## Theoretical Basis

Governance hierarchy is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Separation of Concerns** | Each layer has distinct responsibility |
| **Information Hiding** | Lower layers hide implementation from higher layers |
| **Design by Contract** | Specs define contracts; tools fulfill them |
| **Hierarchical Decomposition** | Complex governance decomposed into manageable layers |

```yaml
theoretical_basis:
  primary: "Separation of Concerns"
  secondary:
    - "Information Hiding"
    - "Design by Contract"
    - "Hierarchical Decomposition"
  rationale: >
    The five-layer hierarchy separates WHAT (specs) from HOW (tools).
    Each layer has clear responsibility and authority. Higher layers
    are abstract and stable; lower layers are concrete and changeable.
    This enables independent evolution while maintaining consistency.
  references:
    - "AGET_TOOL_SPEC.md"
    - "AGET_VALIDATION_SPEC.md"
```

---

## Validation

```bash
# Verify tool has spec reference
grep "Implements:" scripts/*.py .aget/patterns/**/*.py

# Verify SOP references pattern
grep "Pattern:" sops/*.md

# Verify capability references spec
grep "spec:" .aget/skills/capabilities.yaml

# Future: Automated traceability validation
python3 validation/validate_governance_traceability.py
```

---

## References

- AGET_TOOL_SPEC.md (tool requirements)
- AGET_VALIDATION_SPEC.md (validation requirements)
- L352: Requirement-to-Test Traceability
- L397: Test Bug vs Spec Gap Distinction

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "Implicit layer relationships in v2.x"
    - "Tool-spec alignment issues"
    - "Conflict resolution during G-PRE.3"
  source_learnings:
    - "L352"
    - "L397"
  trigger: "G-PRE.3.2 P2 Specification Remediation"
  rationale: "Governance layer relationships were implicit; no specification existed"
```

---

*AGET Governance Hierarchy Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Governance Architecture - G-PRE.3.2*
*"Specs define; tools implement."*
