# AGET SKILLS Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (5D Composition - SKILLS Dimension)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_SKILLS_SPEC.md`
**Change Proposal**: CP-012

---

## Abstract

This specification defines the SKILLS dimension of the 5D Composition Architecture. SKILLS encompasses WHAT an agent does: its Capabilities, Tools, Outputs, and Phase_Alignment. SKILLS provides the behavioral repertoire that enables agent action.

## Motivation

Agent capabilities determine what work can be performed:
- What behaviors an agent can exhibit
- What tools are available
- What output formats are produced
- Which A_SDLC phases the agent supports

Without explicit SKILLS definition, agents have unclear capabilities, leading to mismatched assignments and inconsistent outputs.

## Scope

**Applies to**: All AGET agents.

**Defines**:
- Capability_Composition
- Tool_Availability
- Output_Formats
- A_SDLC Phase_Alignment
- Skill_Artifacts

**Related Specifications**:
- COMPOSITION_SPEC_v1.0.md (capability composition mechanism)
- AGET_5D_ARCHITECTURE_SPEC.md (umbrella)

---

## The 5D Composition Context

SKILLS is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | AGET_PERSONA_SPEC |
| MEMORY | Knowledge persistence, learning accumulation | AGET_MEMORY_SPEC |
| REASONING | Decision patterns, problem-solving approach | AGET_REASONING_SPEC |
| **SKILLS** | Specific capabilities, tools, integrations | **This document** |
| CONTEXT | Environmental awareness, situation adaptation | AGET_CONTEXT_SPEC |

---

## Vocabulary

Domain terms for the SKILLS dimension:

```yaml
vocabulary:
  meta:
    domain: "skills"
    version: "1.0.0"
    inherits: "aget_core"

  skills:  # D4: WHAT DOES
    Capability:
      skos:definition: "Composable behavior unit declared in Manifest_Yaml"
      skos:narrower: ["Memory_Management", "Domain_Knowledge", "Governance_Capability"]
    Capability_Composition:
      skos:definition: "Mechanism for combining capabilities into agent behavior"
      aget:reference: "COMPOSITION_SPEC_v1.0"
    Tool:
      skos:definition: "Executable script or validator available to agent"
      skos:narrower: ["Validator", "Pattern_Script"]
    Validator:
      skos:definition: "Python script that checks compliance"
      aget:location: "validation/"
      aget:naming: "validate_*.py"
    Pattern_Script:
      skos:definition: "Reusable operational pattern implementation"
      aget:location: ".aget/patterns/"
    Output_Format:
      skos:definition: "Structured format for agent outputs"
      skos:narrower: ["Markdown", "YAML", "JSON", "Five_W_H"]
    A_SDLC_Phase:
      skos:definition: "Agentic Software Development Lifecycle phase"
      skos:narrower: ["Phase_0", "Phase_1", "Phase_2", "Phase_3", "Phase_4", "Phase_5", "Phase_6"]

  persona:  # D1: Related identity terms
    Archetype:
      skos:definition: "Base agent classification"
      skos:broader: "AGET_PERSONA_SPEC"

  memory:  # D2: Stored artifacts
    Manifest_Yaml:
      skos:definition: "Agent manifest declaring capabilities"
      aget:location: "manifest.yaml"
    SCRIPT_REGISTRY:
      skos:definition: "Registry of available scripts and validators"
      aget:location: "SCRIPT_REGISTRY.yaml"

  reasoning:  # D3: Related decision patterns
    Capability_Prerequisite:
      skos:definition: "Dependency between capabilities"
    Capability_Conflict:
      skos:definition: "Incompatibility between capabilities"

  context:  # D5: Where/when applied
    Phase_Alignment:
      skos:definition: "Which A_SDLC phases agent primarily serves"
```

---

## Requirements

### CAP-SKILL-001: Capability Declaration

The SYSTEM shall declare Capabilities in Manifest_Yaml.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-001-01 | ubiquitous | The SYSTEM shall list Capabilities in Manifest_Yaml |
| CAP-SKILL-001-02 | ubiquitous | The SYSTEM shall reference defined Capability_Specs |
| CAP-SKILL-001-03 | conditional | IF Capability has Prerequisites THEN the SYSTEM shall satisfy Prerequisites |
| CAP-SKILL-001-04 | event-driven | WHEN Capability_Conflict is detected, the SYSTEM shall resolve Conflict |

**Enforcement**: `validate_template_manifest.py`, `validate_composition.py`

#### Capability Declaration Format

```yaml
# manifest.yaml
composition:
  base_template: advisor
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
      config:
        domain: data-science
    - name: structured-outputs
      version: ">=1.0.0"
  composition_rules:
    conflict_resolution: error
```

### CAP-SKILL-002: Tool Availability

The SYSTEM shall have access to appropriate Tools.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-002-01 | ubiquitous | The SYSTEM shall have access to Validators for its Domain |
| CAP-SKILL-002-02 | ubiquitous | The SYSTEM shall have Pattern_Scripts in .aget/patterns/ |
| CAP-SKILL-002-03 | ubiquitous | The SYSTEM shall document Tool_Availability |
| CAP-SKILL-002-04 | ubiquitous | The SYSTEM shall register Tools in SCRIPT_REGISTRY |

**Enforcement**: `validate_script_registry.py`

#### Standard Tool Categories

| Category | Examples | Location |
|----------|----------|----------|
| Validators | validate_*.py | validation/ |
| Session_Patterns | wake_up.py, wind_down.py | .aget/patterns/session/ |
| Release_Patterns | version_bump.py | .aget/patterns/release/ |
| Sync_Patterns | template_sync_check.py | .aget/patterns/sync/ |

### CAP-SKILL-003: Output Formats

The SYSTEM shall define Output_Format capabilities.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-003-01 | optional | WHERE Structured_Outputs capability exists, the SYSTEM shall produce formatted output |
| CAP-SKILL-003-02 | ubiquitous | The SYSTEM shall document Output_Formats |
| CAP-SKILL-003-03 | conditional | IF Domain_Specific_Format is used THEN the SYSTEM shall have Template |

**Enforcement**: Documentation review

#### Standard Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| Markdown | Standard documentation | Specifications, L-docs, docs |
| YAML | Structured data | Manifests, processes |
| JSON | Machine-readable | Identity, version files |
| Five_W_H | Executive briefing | Strategic communication |

### CAP-SKILL-004: A-SDLC Phase Alignment

The SYSTEM shall align with A_SDLC phases.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-004-01 | ubiquitous | The SYSTEM should declare primary A_SDLC_Phase(s) |
| CAP-SKILL-004-02 | ubiquitous | The SYSTEM shall use Phase_Alignment to inform Capability selection |
| CAP-SKILL-004-03 | optional | WHERE Cross_Cutting role exists, the SYSTEM may span multiple phases |

**Enforcement**: Manifest review

#### A-SDLC Phase Mapping

| Phase | Description | Template_Alignment |
|-------|-------------|--------------------|
| Phase_0 | Strategic Planning | executive, researcher |
| Phase_1 | Requirements | spec-engineer, analyst |
| Phase_2 | Architecture | architect |
| Phase_3 | Implementation | developer |
| Phase_4 | Testing/Review | reviewer |
| Phase_5 | Deployment | operator |
| Phase_6 | Operations | operator, developer |
| Cross_Cutting | All phases | supervisor, advisor, worker, consultant |

### CAP-SKILL-005: Skill Documentation

The SYSTEM shall document its Skills.

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-SKILL-005-01 | ubiquitous | The SYSTEM shall document Capability_List | manifest.yaml |
| CAP-SKILL-005-02 | ubiquitous | The SYSTEM shall document Tool_Reference | .aget/patterns/README.md |
| CAP-SKILL-005-03 | ubiquitous | The SYSTEM shall provide Output_Examples | docs/ |
| CAP-SKILL-005-04 | ubiquitous | The SYSTEM shall document Phase_Alignment | AGENTS.md |

**Enforcement**: Documentation review

### CAP-SKILL-006: Capability Composition

The SYSTEM shall follow Capability_Composition rules.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-006-01 | ubiquitous | The SYSTEM shall compose as Agent = Base_Template + Capabilities |
| CAP-SKILL-006-02 | ubiquitous | The SYSTEM shall satisfy Capability_Prerequisites |
| CAP-SKILL-006-03 | conditional | IF Duplicate_Capability exists THEN the SYSTEM shall ignore Duplicate |
| CAP-SKILL-006-04 | ubiquitous | The SYSTEM shall apply Composition in order-independent manner |

**Enforcement**: `validate_composition.py`

---

## Capability Composition

SKILLS dimension leverages COMPOSITION_SPEC_v1.0 for Capability_Composition:

### Composition Model (L330)

```
Agent = Base_Template + Capability[]

Example:
  template-advisor-aget
    + capability-memory-management
    + capability-domain-knowledge
    + capability-structured-outputs
    = Data Science Advisor
```

### Composition Algebra

| Property | Formula | Meaning |
|----------|---------|---------|
| Identity | T + ∅ = T | No capabilities = base template |
| Commutativity | T + [A, B] = T + [B, A] | Order doesn't matter |
| Idempotency | T + [A, A] = T + [A] | Duplicates ignored |
| Prerequisite | A requires B → B must be in list | Dependencies satisfied |

### Standard Capabilities

| Capability | Purpose | Prerequisites |
|------------|---------|---------------|
| memory-management | Six_Layer_Memory, KB_Review | — |
| domain-knowledge | Domain expertise | — |
| structured-outputs | Formatted output production | — |
| governance-rigorous | Full protocol governance | — |
| governance-balanced | Proportional governance | — |
| governance-exploratory | Flow-first governance | — |
| collaboration | Cross-agent coordination | domain-knowledge |
| org-kb | Organizational knowledge | memory-management |

---

## Authority Model

```yaml
authority:
  applies_to: "all_agents"

  governed_by:
    spec: "AGET_SKILLS_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "declare Capabilities in Manifest_Yaml"
      - "create and use Pattern_Scripts"
      - "produce documented Output_Formats"
      - "register Tools in SCRIPT_REGISTRY"

    requires_template:
      - "Available Capabilities defined by Base_Template"
      - "Required Capabilities inherited from template"

  composition_authority:
    - action: "Define new Capability_Spec"
      approver: "framework-aget"
    - action: "Add capability to template"
      approver: "template owner"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-SKILL-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT use Capability WITHOUT declaring in Manifest_Yaml"
      rationale: "Capabilities must be explicit for composition"

    - id: "INV-SKILL-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT bypass Capability_Prerequisites"
      rationale: "Prerequisite satisfaction is mandatory"

    - id: "INV-SKILL-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT use unregistered Tools in production"
      rationale: "Tool registry enables validation and maintenance"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/patterns/"
      purpose: "Pattern_Script storage"
      subdirectories:
        - "session/"
        - "release/"
        - "sync/"

    - path: "validation/"
      purpose: "Validator storage"
      naming: "validate_*.py"

  required_files:
    - path: "manifest.yaml"
      purpose: "Capability declaration"
      schema: "manifest_schema.yaml"

    - path: ".aget/patterns/README.md"
      purpose: "Tool documentation"

  optional_files:
    - path: "SCRIPT_REGISTRY.yaml"
      purpose: "Tool registry"
      note: "Framework-level only; agents inherit"

  domain_structure:
    - path: "docs/outputs/"
      purpose: "Output_Format examples"
```

---

## Validation

### Capability Validation

```bash
# Validate Manifest_Yaml structure
python3 validation/validate_template_manifest.py manifest.yaml

# Validate Capability_Composition
python3 validation/validate_composition.py manifest.yaml --specs specs/capabilities/

# Verify Prerequisites satisfied
python3 validation/validate_composition.py manifest.yaml -v
```

### Tool Availability Check

```bash
# Verify Pattern_Scripts exist
ls .aget/patterns/session/
ls .aget/patterns/release/

# Verify scripts are registered
python3 validation/validate_script_registry.py SCRIPT_REGISTRY.yaml --check-files
```

---

## Theoretical Basis

SKILLS is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **Extended Mind** | Tools extend cognitive capability |
| **BDI (Capabilities)** | Skills represent what agent CAN do |
| **Cybernetics** | Capabilities provide requisite variety |
| **Actor Model** | Skills define message-handling potential |

```yaml
theoretical_basis:
  primary: "Extended Mind"
  secondary:
    - "BDI (capability as potential)"
    - "Cybernetics (requisite variety)"
    - "Actor Model (message handling)"
  rationale: >
    SKILLS extends agent cognition (Extended Mind) through tools and
    capabilities. Capabilities represent behavioral potential (BDI).
    More skills provide variety to match complexity (Cybernetics).
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

- L330: Capability Composition Architecture
- COMPOSITION_SPEC_v1.0: Composition mechanism
- SCRIPT_REGISTRY.yaml: Script catalog
- AGET_PYTHON_SCRIPT_SPEC: Script standards
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- AGET_SPEC_FORMAT_v1.2: Specification format

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L330"]
  pattern_origin: "Template Manifest pattern"
  rationale: "Formalizes capability composition into dimension spec"
```

---

*AGET SKILLS Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture - SKILLS Dimension*
*"WHAT the agent does defines its value."*
