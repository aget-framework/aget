# AGET Specification Format v1.2

**Version**: 1.2.0
**Date**: 2025-12-26
**Status**: CANONICAL
**Location**: `aget/specs/AGET_SPEC_FORMAT_v1.2.md`
**Supersedes**: AGET_SPEC_FORMAT_v1.1.md
**Change Proposal**: v3.0.0-alpha.5

---

## Purpose

This document defines the canonical format for AGET specifications. All specifications MUST use EARS (Easy Approach to Requirements Syntax) for requirements and SKOS for vocabulary terms.

**v1.2 Enhancements**:
- Dual format support (Markdown + YAML)
- Namespaced capability IDs (CAP-{DOMAIN}-{NNN})
- Standard markdown section order
- Dimension-organized vocabulary (D1-D5)
- Authority model (per-agent)
- Inviolables (template-inherited boundaries)
- Structural requirements (directory/artifact specs)
- Optional theoretical basis section
- Optional graduation history section

---

## Quick Reference

### EARS Patterns

| Pattern | Format | When to Use |
|---------|--------|-------------|
| **Ubiquitous** | `The SYSTEM shall <action>` | Always-active requirements |
| **Event-Driven** | `WHEN <trigger>, the SYSTEM shall <action>` | Triggered by events |
| **State-Driven** | `WHILE <state>, the SYSTEM shall <action>` | Active during states |
| **Optional** | `WHERE <feature>, the SYSTEM shall <action>` | Configuration-specific |
| **Conditional** | `IF <condition> THEN the SYSTEM shall <action>` | Logical conditions |

### Vocabulary Format

| Element | Format | Example |
|---------|--------|---------|
| Domain objects | `Title_Case` | `Session_State`, `Wake_Protocol` |
| Verbs | lowercase | `validate`, `execute`, `track` |
| Constraints | UPPERCASE | `WITHIN`, `BEFORE`, `MAINTAINING` |

---

## EARS Temporal Patterns

### 1. Ubiquitous (Always-True)

**Format**: `The SYSTEM shall <verb> <Object>`

**When to use**: Continuous, always-active requirements.

**Examples**:
```
The SYSTEM shall maintain Session_State across interactions.
The SYSTEM shall declare Archetype in Manifest_Yaml.
The SYSTEM shall track Learning_Documents in Evolution_Directory.
```

### 2. Event-Driven (WHEN)

**Format**: `WHEN <Trigger_Event>, the SYSTEM shall <verb> <Object>`

**When to use**: Requirements triggered by specific events.

**Examples**:
```
WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol.
WHEN Gate_Boundary is reached, the SYSTEM shall await Approval.
WHEN Breaking_Change is detected, the SYSTEM shall require Migration_Guide.
```

### 3. State-Driven (WHILE)

**Format**: `WHILE <State_Condition>, the SYSTEM shall <verb> <Object>`

**When to use**: Requirements active during specific states.

**Examples**:
```
WHILE in Planning_Mode, the SYSTEM shall create Project_Plan.
WHILE Governance_Rigorous is active, the SYSTEM shall enforce Gate_Discipline.
WHILE in Exploratory_Mode, the SYSTEM shall permit Scope_Flexibility.
```

### 4. Optional (WHERE)

**Format**: `WHERE <Feature_Condition>, the SYSTEM shall <verb> <Object>`

**When to use**: Context-specific requirements, optional features.

**Examples**:
```
WHERE Instance_Type is AGET, the SYSTEM shall permit Action_Capabilities.
WHERE Governance_Rigorous is enabled, the SYSTEM shall require Project_Plan.
WHERE Portfolio_Assignment exists, the SYSTEM shall enforce Portfolio_Boundaries.
```

### 5. Conditional (IF...THEN)

**Format**: `IF <Logical_Condition> THEN the SYSTEM shall <verb> <Object>`

**When to use**: Logical conditions with consequences.

**Examples**:
```
IF Configuration_Size exceeds Limit THEN the SYSTEM shall trigger Size_Warning.
IF Gate_Approval is NOGO THEN the SYSTEM shall halt Execution.
IF Scope_Boundary_Violation is detected THEN the SYSTEM shall escalate.
```

---

## Controlled Vocabulary (Title_Case)

All domain objects use Title_Case with underscores. Terms SHOULD be defined in AGET_CONTROLLED_VOCABULARY.md.

### Core Framework Terms

```
Agent                    # An AGET entity
Template                 # Reusable agent archetype
Instance                 # Concrete agent from template
Supervisor               # Coordinating agent
Fleet                    # Collection of agents
Portfolio                # Organizational grouping
```

### Configuration Terms

```
Manifest_Yaml            # manifest.yaml file
Version_Json             # .aget/version.json file
Claude_Md                # CLAUDE.md configuration
Charter_Md               # governance/CHARTER.md
```

### Session Terms

```
Session_State            # Current session context
Wake_Protocol            # Session initialization
Wind_Down_Protocol       # Session finalization
Learning_Document        # L-series knowledge capture
```

### Governance Terms

```
Gate_Boundary            # Decision checkpoint
Gate_Approval            # GO/NOGO decision
Project_Plan             # Planning artifact
Governance_Rigorous      # High governance intensity
Governance_Balanced      # Medium governance intensity
Governance_Exploratory   # Low governance intensity
```

---

## Namespaced Capability IDs

Capabilities use namespaced IDs for traceability:

```
CAP-{DOMAIN}-{NNN}[-{SUB}]

Where:
  DOMAIN = spec domain (PERSONA, MEMORY, REASON, SKILL, CONTEXT, etc.)
  NNN    = three-digit sequence (001, 002, ...)
  SUB    = optional sub-requirement (01, 02, ...)
```

**Examples**:
```
CAP-PERSONA-001       # Primary requirement
CAP-PERSONA-001-01    # Sub-requirement
CAP-MEMORY-003        # Memory spec requirement
CAP-REASON-002-05     # Reasoning sub-requirement
```

**Domain Abbreviations**:

| Domain | Abbreviation |
|--------|--------------|
| 5D_ARCHITECTURE | 5D |
| PERSONA | PERSONA |
| MEMORY | MEMORY |
| REASONING | REASON |
| SKILLS | SKILL |
| CONTEXT | CONTEXT |
| CHANGE_PROPOSAL | CP |
| PYTHON_SCRIPT | SCRIPT |
| FRAMEWORK | FW |

---

## Dimension-Organized Vocabulary

Domain vocabularies SHALL be organized by the 5D dimensions. This ensures vocabulary terms reflect the structural organization of agent knowledge.

### Structure

```yaml
vocabulary:
  meta:
    domain: "domain_name"
    version: "1.0.0"
    inherits: "aget_core"  # Framework vocabulary inheritance

  persona:  # D1: WHO
    Domain_Advisor:
      skos:definition: "Agent providing domain expertise"
      skos:broader: "Advisor"

  memory:  # D2: WHAT KNOWS
    Invoice_Line_Item:
      skos:definition: "Single line entry in an invoice"
      aget:structure: "memory/invoices/{id}/lines/"
    Ledger_Entry:
      skos:definition: "Accounting record in the general ledger"

  reasoning:  # D3: HOW THINKS
    Reconciliation_Pattern:
      skos:definition: "Pattern for matching transactions"
      skos:broader: "Verification_Pattern"

  skills:  # D4: WHAT DOES
    Invoice_Validation:
      skos:definition: "Capability to validate invoice correctness"
      aget:phase: [3, 4]  # A-SDLC phases

  context:  # D5: WHERE/WHEN
    Fiscal_Period:
      skos:definition: "Accounting time boundary"
      skos:example: "Q4 2025"
```

### Inheritance

```
aget_core (framework)
    └── domain_vocabulary (e.g., accounting)
            └── agent_vocabulary (e.g., accounting-aget)
```

Agents inherit vocabulary from:
1. **aget_core**: Framework-level terms (Session_State, Wake_Protocol, etc.)
2. **domain**: Domain-specific terms (Invoice_Line_Item, etc.)
3. **agent**: Agent-specific extensions

---

## Authority Model

Each agent specification SHALL declare its authority relationships.

### Authority Section

```yaml
authority:
  supervised_by: "supervisor-agent-name"
  supervision_type: "governance"  # governance | operational | advisory

  can_autonomously:
    - "create Learning_Documents"
    - "create Specifications"
    - "execute Minor_Releases"

  requires_approval:
    - action: "Major_Release"
      approver: "supervisor"
    - action: "Breaking_Change"
      approver: "supervisor"
    - action: "Fleet_Migration"
      approver: "vp-of-ai"

  manages:
    - entity: "template-*-aget"
      authority: "full"
    - entity: "aget/"
      authority: "publish"
```

### Authority Levels

| Level | Description | Example Actions |
|-------|-------------|-----------------|
| **autonomous** | No approval needed | L-docs, internal docs |
| **propose** | Create and propose | Minor releases |
| **escalate** | Must escalate | Breaking changes, major releases |

---

## Inviolables

Inviolables are boundaries that CANNOT be overridden, even by supervisors. They originate from framework templates and may be extended by agents.

### Inviolable Section

```yaml
inviolables:
  inherited:  # From template
    - id: "INV-CORE-001"
      source: "template-advisor-aget"
      statement: "The SYSTEM shall NOT execute Destructive_Action WITHOUT User_Confirmation"
    - id: "INV-CORE-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT modify Production_Data WITHOUT Explicit_Authorization"

  agent_specific:  # This agent adds
    - id: "INV-ACCT-001"
      statement: "The SYSTEM shall NOT approve Financial_Transaction exceeding Approval_Threshold"
      rationale: "Segregation of duties requirement"
      enforcement: "pre_action_validation_hook"
```

### Inviolable Format

```
INV-{DOMAIN}-{NNN}

Where:
  DOMAIN = CORE (framework) | agent domain abbreviation
  NNN    = three-digit sequence
```

### Inheritance Chain

```
aget_framework (INV-CORE-*)
    └── template (may add INV-TEMPLATE-*)
            └── agent (may add INV-{DOMAIN}-*)
```

**Key Principle**: Inviolables can only be ADDED, never removed or weakened.

---

## Structural Requirements

Directory and artifact structure IS a specification. Agents SHALL declare structural requirements.

### Structure Section

```yaml
structure:
  required_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration"
      contents:
        - "version.json"
        - "identity.json"
    - path: ".aget/evolution/"
      purpose: "Learning documents"
      naming: "L{NNN}_{snake_case}.md"
    - path: "governance/"
      purpose: "Governance artifacts"
      contents:
        - "CHARTER.md"
        - "MISSION.md"
    - path: "planning/"
      purpose: "Planning artifacts"

  required_files:
    - path: "CLAUDE.md"
      purpose: "Agent configuration"
      validation: "validate_claude_md.py"
    - path: ".aget/version.json"
      purpose: "Agent identity"
      schema: "version_json_schema.yaml"

  domain_structure:  # Domain-specific
    - path: "memory/invoices/"
      purpose: "Invoice storage"
      pattern: "{invoice_id}/"
    - path: "memory/ledger/"
      purpose: "Ledger entries"
```

### Structure Validation

```bash
# Validate agent structure
python3 validate_agent_structure.py --dir /path/to/agent --spec AGET_ACCOUNTING_SPEC.yaml
```

---

## Dual Format Support

### Markdown Format (.md)

Human-readable, includes narrative context.

```markdown
# AGET {NAME} Specification

**Version**: X.Y.Z
**Status**: Active | Draft | Deprecated
**Category**: Standards | Process | Informational
**Created**: YYYY-MM-DD
**Author**: agent-name
**Location**: `path/to/AGET_{NAME}_SPEC.md`
**Change Proposal**: CP-XXX (if applicable)

---

## Abstract

Brief overview of what this specification defines.

## Motivation

Why this specification is needed.

## Scope

**Applies to**: What agents/templates this covers.

**Defines**: What this specification establishes.

---

## Requirements

### CAP-{DOMAIN}-001: Requirement Name

**Statement**: The SYSTEM shall <verb> <Object>.

**Pattern**: ubiquitous | event-driven | state-driven | optional | conditional

**Enforcement**: How this is validated (contract test, validator, etc.)

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-{DOMAIN}-001-01 | ubiquitous | The SYSTEM shall ... |
| CAP-{DOMAIN}-001-02 | event-driven | WHEN <event>, the SYSTEM shall ... |

---

## Validation

How to validate compliance with this specification.

---

## Theoretical Basis (Optional)

theoretical_basis:
  primary: "Theory Name"
  secondary: ["Theory 2", "Theory 3"]
  reference: "L-doc reference"

---

## Graduation History (Optional)

graduation:
  source_learnings: ["L123", "L456"]
  pattern_origin: "pattern_name"
  rationale: "Why this was formalized"

---

## References

- Related specs
- L-docs
- External references

---

*AGET {NAME} Specification vX.Y.Z*
```

### YAML Format (.yaml)

Machine-readable, enables validation.

```yaml
spec:
  id: SPEC-{NAME}
  version: "X.Y.Z"
  status: active | draft | deprecated
  category: standards | process | informational
  format_version: "1.2"
  created: "YYYY-MM-DD"
  author: "agent-name"
  location: "path/to/AGET_{NAME}_SPEC.yaml"
  description: "Brief description"

capabilities:
  CAP-{DOMAIN}-001:
    name: "Requirement Name"
    domain: domain_name
    statement: "EARS-formatted requirement statement"
    pattern: ubiquitous | event-driven | state-driven | optional | conditional
    trigger: event_name          # For event-driven
    state: state_condition       # For state-driven
    feature: feature_condition   # For optional
    condition: logical_condition # For conditional
    enforcement: "validation method"
    notes: "Additional context"

  CAP-{DOMAIN}-001-01:
    parent: CAP-{DOMAIN}-001
    statement: "Sub-requirement statement"
    pattern: ubiquitous

dependencies:
  CAP-{DOMAIN}-002: [CAP-{DOMAIN}-001]

theoretical_basis:                # Optional
  primary: "Theory Name"
  secondary: ["Theory 2"]
  reference: "L-doc"

graduation:                       # Optional
  source_learnings: ["L123"]
  pattern_origin: "pattern_name"
  rationale: "Formalization reason"
```

### Format Transformation Rules

| Markdown | YAML |
|----------|------|
| `### CAP-{DOMAIN}-NNN: Name` | `CAP-{DOMAIN}-NNN:` with `name:` |
| Prose requirement | `statement:` field |
| Pattern in description | `pattern:` field |
| Verification section | `enforcement:` field |
| Theoretical Basis | `theoretical_basis:` block |
| Graduation History | `graduation:` block |

---

## Maturity Levels

| Level | Definition | Criteria |
|-------|------------|----------|
| **bootstrapping** | Initial creation | Basic structure, <10 capabilities |
| **minimal** | Functional | Core capabilities, basic validation |
| **standard** | Production-ready | Complete capabilities, contract tests |
| **exemplary** | Reference | Full documentation, examples, guides |

---

## Contract Test Integration

Each capability SHOULD have enforcement:

```yaml
CAP-PERSONA-001:
  statement: "The SYSTEM shall declare Archetype in Manifest_Yaml"
  enforcement: "validate_persona_compliance.py, test_archetype_declared"
```

Test naming: `test_{capability_name}` or `test_{domain}_{behavior}`

---

## Migration from v1.1

### ID Migration

```
# v1.1 (unnamespaced)
CAP-001  →  CAP-{DOMAIN}-001

# R-style IDs (non-EARS)
R-PERSONA-001  →  CAP-PERSONA-001
```

### Statement Migration

```
# v1.1 (informal)
"Agent SHALL declare archetype"

# v1.2 (EARS)
"The SYSTEM shall declare Archetype in Manifest_Yaml"
```

---

## Validation

### EARS Pattern Check

Compliant statements contain one of:
- `The SYSTEM shall` (ubiquitous)
- `WHEN .* the SYSTEM shall` (event-driven)
- `WHILE .* the SYSTEM shall` (state-driven)
- `WHERE .* the SYSTEM shall` (optional)
- `IF .* THEN the SYSTEM shall` (conditional)

### Vocabulary Check

Domain objects should be Title_Case: `[A-Z][a-z]+(_[A-Z][a-z]+)*`

### ID Format Check

Capability IDs match: `CAP-[A-Z]+-[0-9]{3}(-[0-9]{2})?`

---

## References

- EARS: Easy Approach to Requirements Syntax (Mavin et al., 2009)
- SKOS: W3C Simple Knowledge Organization System
- AGET_CONTROLLED_VOCABULARY.md
- AGET_GLOSSARY_STANDARD_SPEC_v1.0.md
- L331: Theoretical Foundations of Agency

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2025-12-26 | Dimension-organized vocabulary, authority model, inviolables, structural requirements, dual format, namespaced IDs, theoretical basis, graduation history |
| 1.1.0 | 2025-12-01 | Initial EARS-based format |

---

*AGET_SPEC_FORMAT_v1.2.md — Canonical specification format for AGET framework*
*"Specs in proper language enable proper validation"*
