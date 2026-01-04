# AGET SOP Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (Process)
**Format Version**: 1.2
**Created**: 2025-12-28
**Updated**: 2026-01-04
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_SOP_SPEC.md`
**Change Origin**: Pre-migration conformance review
**Related Specs**: AGET_VALIDATION_SPEC, AGET_FILE_NAMING_CONVENTIONS

---

## Abstract

This specification defines the format, structure, and vocabulary requirements for Standard Operating Procedures (SOPs) within the AGET framework. SOPs provide repeatable, documented procedures for common agent operations. This spec ensures consistency, traceability, and vocabulary compliance across all SOPs.

## Motivation

SOP challenges observed in practice:

1. **Inconsistent format**: SOPs vary in structure, missing required sections
2. **Informal vocabulary**: Terms like "gate" vs `Gate`, "validation" vs `Validation`
3. **Missing traceability**: No references to governing specifications or learnings
4. **No governing spec**: Unlike validators (AGET_VALIDATION_SPEC), SOPs had no formal specification

Root cause analysis:
```
Why are SOPs inconsistent across agents?
  → No specification defines SOP format
Why no SOP specification?
  → Framework focused on technical specs first
Why is vocabulary inconsistent?
  → No enforcement mechanism
Why no enforcement?
  → ROOT CAUSE: AGET_SOP_SPEC does not exist
```

## Scope

**Applies to**: All SOP documents in AGET agents and templates.

**Defines**:
- SOP file naming conventions
- Required sections and structure
- Vocabulary compliance requirements
- Traceability requirements
- Validation criteria

**Related**:
- AGET_FILE_NAMING_CONVENTIONS (naming rules)
- AGET_CORE_VOCABULARY (controlled terms)
- AGET_VALIDATION_SPEC (validator structure)

---

## Vocabulary

Domain terms for the SOP specification:

```yaml
vocabulary:
  meta:
    domain: "sop"
    version: "1.0.0"
    inherits: "aget_core"

  sop:  # Core SOP concepts
    SOP:
      skos:definition: "Standard Operating Procedure - documented repeatable process"
      skos:altLabel: "Standard_Operating_Procedure"
      aget:location: "sops/*.md"
    SOP_Header:
      skos:definition: "Metadata section at top of SOP document"
      skos:narrower: ["Version", "Owner", "Created", "Related"]
    SOP_Section:
      skos:definition: "Logical division within SOP document"
      skos:narrower: ["Purpose", "Scope", "Procedure", "References"]

  structure:  # SOP structure elements
    Purpose_Section:
      skos:definition: "Section describing why this SOP exists"
    Scope_Section:
      skos:definition: "Section defining applicability boundaries"
    Procedure_Section:
      skos:definition: "Section containing step-by-step instructions"
    References_Section:
      skos:definition: "Section listing related documents"

  compliance:  # Vocabulary compliance
    Vocabulary_Term:
      skos:definition: "Controlled term from AGET_CORE_VOCABULARY"
      skos:example: "Gate, Validation, Migration"
    Informal_Term:
      skos:definition: "Non-controlled term that should be replaced"
      skos:example: "gate, validation, migration"

  process_hierarchy:  # L436: PROJECT_PLAN to SOP graduation
    Process_Artifact:
      skos:definition: "Document defining how work is done"
      skos:narrower: ["PROJECT_PLAN", "SOP", "Specification"]
    PROJECT_PLAN:
      skos:definition: "One-time gated plan for specific scope"
      skos:broader: "Process_Artifact"
      aget:graduation_target: "SOP"
      aget:location: "planning/PROJECT_PLAN_*.md"
    SOP:
      skos:definition: "Repeatable formalized procedure (graduated PROJECT_PLAN)"
      skos:broader: "Process_Artifact"
      aget:graduation_source: "PROJECT_PLAN"
      aget:graduation_target: "Specification"
      aget:location: "sops/*.md"
    Graduation:
      skos:definition: "Process by which repeated PROJECT_PLANs become formalized SOPs"
      skos:related: ["PROJECT_PLAN", "SOP"]
      aget:trigger: "Pattern executed successfully 2+ times"
```

**Process Artifact Hierarchy (L436):**

```
Ad-hoc Task → PROJECT_PLAN (one-time) → SOP (repeatable) → Specification (normative)
```

| Level | Nature | Execution | When to Use |
|-------|--------|-----------|-------------|
| **Ad-hoc** | Informal | Once | Simple, low-risk tasks |
| **PROJECT_PLAN** | Formal, gated | Once | Complex, multi-step tasks |
| **SOP** | Formal, procedural | Repeatable | Procedures executed 2+ times |
| **Specification** | Formal, normative | N/A | Requirements that define behavior |

---

## Requirements

### CAP-SOP-001: SOP Structure

The SYSTEM shall enforce standard SOP structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SOP-001-01 | ubiquitous | The SOP shall include Version in header |
| CAP-SOP-001-02 | ubiquitous | The SOP shall include Owner in header |
| CAP-SOP-001-03 | ubiquitous | The SOP shall include Created date in header |
| CAP-SOP-001-04 | ubiquitous | The SOP shall include Purpose section |
| CAP-SOP-001-05 | ubiquitous | The SOP shall include Scope section |
| CAP-SOP-001-06 | conditional | IF SOP references specs THEN the SOP shall include Related in header |
| CAP-SOP-001-07 | optional | WHERE SOP has learnings, the SOP shall include References section |

**Enforcement**: `validate_sop_compliance.py` (to be created)

#### SOP Header Template

```markdown
# SOP: {Title}

**Version**: {M.m.p}
**Created**: {YYYY-MM-DD}
**Owner**: {agent-name}
**Related**: {L-docs, specs, patterns}

---

## Purpose

{Why this SOP exists}

---

## Scope

{When this SOP applies, when it doesn't}

---
```

### CAP-SOP-002: Vocabulary Compliance

The SYSTEM shall enforce controlled vocabulary in SOPs.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SOP-002-01 | ubiquitous | The SOP shall use Title_Case for domain objects |
| CAP-SOP-002-02 | ubiquitous | The SOP shall use controlled vocabulary terms from AGET_CORE_VOCABULARY |
| CAP-SOP-002-03 | conditional | IF term not in AGET_CORE_VOCABULARY THEN the SOP shall define it locally |
| CAP-SOP-002-04 | prohibited | The SOP shall NOT use informal terms in requirement statements |
| CAP-SOP-002-05 | conditional | IF generic term has AGET-specific context THEN the SOP shall use compound term |
| CAP-SOP-002-06 | ubiquitous | The SOP shall prefer compound vocabulary (e.g., `Validation_Gate`) over generic vocabulary (e.g., `Gate`) |

**Enforcement**: Vocabulary audit, `validate_vocabulary_specificity.py` (future)

#### Genericness Test

**Question**: Is this term AGET-specific or would it mean the same thing outside AGET?

| Term | AGET-Specific? | Action |
|------|----------------|--------|
| "gate" | No (generic) | Use `Project_Gate`, `Validation_Gate` |
| "validation" | No (generic) | Use `Structural_Validation`, `Migration_Validation` |
| "Learning_Document" | Yes (L-docs are AGET) | Use as-is |
| "Wake_Protocol" | Yes (AGET session) | Use as-is |
| "Fleet_Migration" | Yes (AGET fleet) | Use as-is |

**Rule**: If the term would be understood identically in a non-AGET context, make it compound/specific.

#### Vocabulary Application Rules

**Principle**: Use Title_Case for AGET-specific concepts; prefer compound terms over generic ones.

| Context | Generic (Avoid) | Specific (Prefer) | When to Use |
|---------|-----------------|-------------------|-------------|
| PROJECT_PLAN stages | "gate" | `Project_Gate`, `Validation_Gate` | In gated execution contexts |
| Quality checks | "validation" | `Structural_Validation`, `Behavioral_Validation` | When specifying validation type |
| Version upgrades | "migration" | `Instance_Migration`, `Fleet_Migration` | When type matters |
| Recovery | "rollback" | `Migration_Rollback`, `Release_Rollback` | When context-specific |
| Mid-process | "checkpoint" | `Mid_Gate_Checkpoint` | Per L002 pattern |
| Go/no-go | "decision point" | `Decision_Point`, `Gate_Boundary` | At explicit stops |
| Session continuity | "handoff" | `Session_Handoff` | Between sessions |
| Version publication | "release" | `Framework_Release`, `Version_Release` | Publishing context |
| Authorization | "approval" | `Gate_Approval`, `Principal_Approval` | Who approves matters |
| Authority escalation | "escalation" | `Scope_Escalation`, `Authority_Escalation` | Type of escalation |

**When Title_Case is Required**:
1. In EARS requirement statements (`The SYSTEM shall...`)
2. When referencing AGET-specific concepts
3. In section headers defining AGET processes

**When lowercase is Acceptable**:
1. In casual explanatory prose
2. In code comments
3. When the term is used generically (not AGET-specific)

### CAP-SOP-003: Naming Conventions

The SYSTEM shall enforce SOP naming conventions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SOP-003-01 | ubiquitous | The SOP file shall use pattern `SOP_{snake_case}.md` |
| CAP-SOP-003-02 | conditional | IF guide document THEN the file shall use pattern `{NAME}_GUIDE.md` |
| CAP-SOP-003-03 | conditional | IF checklist document THEN the file shall use pattern `{NAME}_CHECKLIST.md` |
| CAP-SOP-003-04 | ubiquitous | The SOP shall reside in `sops/` directory |

**Enforcement**: `validate_naming_conventions.py`

#### Valid Naming Patterns

```
SOP_release_process.md         ✅ Standard SOP
SOP_instance_migration_v3.md   ✅ Versioned SOP
CONTRIBUTION_GUIDE.md          ✅ Guide document
RELEASE_VERIFICATION_CHECKLIST.md  ✅ Checklist
sops/README.md                 ✅ Index file
```

### CAP-SOP-004: Traceability

The SYSTEM shall support SOP traceability.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SOP-004-01 | optional | WHERE SOP implements requirements, the SOP should include `Implements:` line |
| CAP-SOP-004-02 | optional | WHERE SOP has related learnings, the SOP should reference L-docs |
| CAP-SOP-004-03 | optional | WHERE SOP has related patterns, the SOP should reference PATTERN_*.md |
| CAP-SOP-004-04 | event-driven | WHEN SOP is updated, the SOP shall update Version |

**Enforcement**: Code review, self-documentation

---

## Authority Model

```yaml
authority:
  applies_to: "sop_documents"

  governed_by:
    spec: "AGET_SOP_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    autonomous:
      - "create SOP for agent-specific procedures"
      - "update SOP version"
      - "add local vocabulary terms"

    requires_approval:
      - action: "create framework-wide SOP"
        approver: "framework owner"
      - action: "modify AGET_CORE_VOCABULARY"
        approver: "framework owner"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-SOP-001"
      source: "aget_framework"
      statement: "The SOP shall NOT use informal vocabulary in requirement statements"
      rationale: "Vocabulary consistency enables automation and clarity"

    - id: "INV-SOP-002"
      source: "aget_framework"
      statement: "The SOP shall NOT omit Purpose section"
      rationale: "Every procedure must explain its reason for existing"

    - id: "INV-SOP-003"
      source: "aget_framework"
      statement: "The SOP shall NOT use undocumented local vocabulary"
      rationale: "All terms must be traceable to definition"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "sops/"
      purpose: "SOP document storage"

  required_sections:
    - name: "Purpose"
      required: true
      order: 1

    - name: "Scope"
      required: true
      order: 2

  optional_sections:
    - name: "Prerequisites"
    - name: "Procedure"
    - name: "Troubleshooting"
    - name: "Rollback"
    - name: "References"

  naming:
    pattern: "SOP_{snake_case}.md"
    alternatives:
      - "{NAME}_GUIDE.md"
      - "{NAME}_CHECKLIST.md"
      - "{NAME}_PROTOCOL.md"
```

---

## Theoretical Basis

SOP specification is grounded in established process theory:

| Theory | Application |
|--------|-------------|
| **Standardization** | Consistent format enables cross-agent understanding |
| **Vocabulary Control** | Controlled terms reduce ambiguity |
| **Traceability** | References enable impact analysis |
| **Self-Documentation** | SOPs explain their own existence and scope |

```yaml
theoretical_basis:
  primary: "Standardization"
  secondary:
    - "Vocabulary Control"
    - "Traceability"
    - "Self-Documentation"
  rationale: >
    SOPs are operational documentation that must be consistent, clear,
    and traceable. Vocabulary control (AGET_CORE_VOCABULARY) ensures
    terms have consistent meaning. Traceability (Related, References)
    enables change impact analysis. Self-documentation (Purpose, Scope)
    ensures SOPs justify their existence.
```

---

## Validation

```bash
# Validate SOP naming
python3 validation/validate_naming_conventions.py /path/to/agent

# Validate SOP structure (future)
python3 validation/validate_sop_compliance.py sops/*.md

# Vocabulary audit (manual)
grep -E '\b(gate|validation|migration|rollback)\b' sops/*.md
```

---

## References

- AGET_FILE_NAMING_CONVENTIONS.md (naming rules)
- AGET_CORE_VOCABULARY.md (controlled vocabulary)
- AGET_VALIDATION_SPEC.md (validator structure pattern)
- AGET_REASONING_SPEC.md (PROJECT_PLAN requirements)
- L377: Validation Suite Orchestration Gap
- L436: PROJECT_PLAN to SOP Graduation Pattern

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "SOP_release_process.md"
    - "SOP_session_handoff.md"
    - "SOP_instance_migration_v3.md"
  source_learnings:
    - "L377"
    - "L436"
  trigger: "Pre-migration conformance review"
  rationale: "SOPs lacked governing specification; vocabulary inconsistent"

  v1.1.0_additions:
    - update: "process_hierarchy vocabulary"
      source: "L436"
      description: "PROJECT_PLAN to SOP graduation pattern"
```

---

*AGET SOP Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*"Standardized procedures enable standardized quality."*
