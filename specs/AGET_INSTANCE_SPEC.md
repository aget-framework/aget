# AGET Instance Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Instance Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_INSTANCE_SPEC.md`
**Change Origin**: 5-why analysis on missing `knowledge/` directory (G-PRE.3.1)
**Related Specs**: AGET_TEMPLATE_SPEC, AGET_5D_ARCHITECTURE_SPEC, AGET_PORTABILITY_SPEC

---

## Abstract

This specification defines the requirements for AGET agent instances. Instances are operational agents derived from templates, with populated identity, active sessions, and accumulated knowledge. This spec distinguishes instance requirements from template requirements and mandates archetype baseline compliance.

## Motivation

Analysis revealed that while AGET_TEMPLATE_SPEC defines template structure, no specification existed for instances:

1. **No instance-specific requirements**: Templates have manifest_version, archetype fields; instances lacked formalization
2. **Archetype baseline drift**: Instance pilot (private-aget-framework-AGET) missing `knowledge/` directory despite operator archetype requiring it
3. **Template vs instance confusion**: Users cloning templates encounter validation failures with no guidance
4. **Instance migration undefined**: L395 pattern emerged from practice but lacked spec backing

Root cause analysis (5-why):
```
Why is knowledge/ missing?
  → L395 doesn't add archetype directories
Why doesn't L395 include that step?
  → Derived from single pilot with existing directories
Why wasn't pilot checked for archetype baseline?
  → No validation for archetype directories
Why doesn't validation check archetype requirements?
  → Designed for templates not instances
Why no spec for instance archetype compliance?
  → ROOT CAUSE: No AGET_INSTANCE_SPEC exists
```

## Scope

**Applies to**: All AGET agent instances (instance_type: "aget").

**Defines**:
- Instance identity requirements
- Archetype baseline compliance
- Instance vs template distinction
- Instance lifecycle states
- Migration requirements

**Does NOT apply to**: Templates (instance_type: "template").

---

## Vocabulary

Domain terms for the INSTANCE specification:

```yaml
vocabulary:
  meta:
    domain: "instance"
    version: "1.0.0"
    inherits: "aget_core"

  core:  # Core instance concepts
    Instance:
      skos:definition: "Operational AGET agent derived from a template"
      skos:narrower: ["Active_Instance", "Dormant_Instance", "Migrating_Instance"]
      skos:related: ["Template"]
    Template:
      skos:definition: "Reusable agent pattern (instance_type: 'template')"
      skos:related: ["Instance"]
    Instantiation:
      skos:definition: "Process of creating an instance from a template"
      skos:related: ["instantiate_template.py"]

  identity:  # Instance identity
    Instance_Type:
      skos:definition: "Classification: 'template' or 'aget'"
      aget:location: ".aget/version.json:instance_type"
    Archetype:
      skos:definition: "Agent role classification from AGET_TEMPLATE_SPEC"
      skos:example: ["worker", "advisor", "supervisor", "operator"]
    Specialization:
      skos:definition: "Instance-specific role refinement"
      skos:example: ["repo-manager", "framework-owner"]
    Agent_Name:
      skos:definition: "Unique identifier for the instance"
      skos:pattern: "{project}-{role}-AGET"

  structure:  # Instance structure
    Archetype_Baseline:
      skos:definition: "Standard visible directories for archetype"
      skos:related: ["AGET_PORTABILITY_SPEC:CAP-PORT-001A"]
    Core_Directories:
      skos:definition: "Directories all instances must have"
      skos:narrower: ["governance/", "sessions/", "planning/", "knowledge/"]
    Extended_Directories:
      skos:definition: "Archetype-specific additional directories"
      skos:example: ["products/", "decisions/", "clients/"]
    Accumulated_Content:
      skos:definition: "User-generated content over instance lifetime"
      skos:narrower: ["L-docs", "Session_Notes", "Plans"]

  lifecycle:  # Instance states
    Active_Instance:
      skos:definition: "Instance with recent session activity"
    Dormant_Instance:
      skos:definition: "Instance without recent sessions but preserved state"
    Migrating_Instance:
      skos:definition: "Instance undergoing version transition"
```

---

## Requirements

### CAP-INST-001: Instance Identity

The SYSTEM shall maintain instance identity distinct from templates.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-INST-001-01 | ubiquitous | The SYSTEM shall set `instance_type: "aget"` in version.json for instances |
| CAP-INST-001-02 | ubiquitous | The SYSTEM shall set `instance_type: "template"` in version.json for templates |
| CAP-INST-001-03 | ubiquitous | The SYSTEM shall populate `agent_name` in version.json for instances |
| CAP-INST-001-04 | ubiquitous | The SYSTEM shall populate `archetype` in version.json for instances |
| CAP-INST-001-05 | optional | WHERE instance has role refinement, the SYSTEM shall populate `specialization` |

**Enforcement**: `validate_template_instance.py`

#### Instance version.json Schema

```json
{
  "agent_name": "private-aget-framework-AGET",
  "version": "3.0.0",
  "instance_type": "aget",
  "manifest_version": "3.0",
  "archetype": "operator",
  "specialization": "framework-manager",
  "aget_version": "3.0.0",
  "template_origin": "template-operator-aget",
  "created_date": "2024-12-01",
  "migration_history": [
    {"from": "2.12.0", "to": "3.0.0", "date": "2025-12-28"}
  ]
}
```

### CAP-INST-002: Archetype Baseline Compliance

The SYSTEM shall maintain archetype-standard visible directories.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-INST-002-01 | ubiquitous | The SYSTEM shall have Core_Directories: governance/, sessions/, planning/, knowledge/ |
| CAP-INST-002-02 | conditional | IF archetype is "developer" THEN the SYSTEM shall have products/ directory |
| CAP-INST-002-03 | conditional | IF archetype is "advisor" THEN the SYSTEM shall have clients/ directory |
| CAP-INST-002-04 | conditional | IF archetype is "architect" THEN the SYSTEM shall have decisions/ directory |
| CAP-INST-002-05 | conditional | IF archetype is "analyst" THEN the SYSTEM shall have reports/ directory |
| CAP-INST-002-06 | conditional | IF archetype is "operator" THEN the SYSTEM shall have knowledge/ directory |
| CAP-INST-002-07 | conditional | IF archetype is "supervisor" THEN the SYSTEM shall have fleet/ directory |

**Enforcement**: `validate_template_instance.py` (archetype directory check)

#### Archetype Directory Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARCHETYPE VISIBLE DIRECTORY MATRIX                    │
├─────────────┬────────────┬──────────┬──────────┬──────────┬─────────────┤
│ Directory   │ governance │ sessions │ planning │ knowledge│ Archetype-  │
│             │ (core)     │ (core)   │ (core)   │ (core)   │ Specific    │
├─────────────┼────────────┼──────────┼──────────┼──────────┼─────────────┤
│ worker      │ ✓          │ ✓        │ ✓        │ ✓        │ -           │
│ advisor     │ ✓          │ ✓        │ ✓        │ ✓        │ clients/    │
│ supervisor  │ ✓          │ ✓        │ ✓        │ ✓        │ fleet/      │
│ developer   │ ✓          │ ✓        │ ✓        │ ✓        │ products/   │
│ consultant  │ ✓          │ ✓        │ ✓        │ ✓        │ clients/    │
│ spec-engineer│ ✓         │ ✓        │ ✓        │ ✓        │ specs/      │
│ executive   │ ✓          │ ✓        │ ✓        │ ✓        │ decisions/  │
│ analyst     │ ✓          │ ✓        │ ✓        │ ✓        │ reports/    │
│ reviewer    │ ✓          │ ✓        │ ✓        │ ✓        │ reviews/    │
│ operator    │ ✓          │ ✓        │ ✓        │ ✓        │ operations/ │
│ architect   │ ✓          │ ✓        │ ✓        │ ✓        │ decisions/  │
│ researcher  │ ✓          │ ✓        │ ✓        │ ✓        │ research/   │
└─────────────┴────────────┴──────────┴──────────┴──────────┴─────────────┘
```

### CAP-INST-003: Instance vs Template Distinction

The SYSTEM shall differentiate instance and template behavior.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-INST-003-01 | conditional | IF instance_type is "template" THEN the SYSTEM shall skip instance-specific tests |
| CAP-INST-003-02 | conditional | IF instance_type is "aget" THEN the SYSTEM shall run full instance validation |
| CAP-INST-003-03 | ubiquitous | The SYSTEM shall display instance_type in wake-up output |
| CAP-INST-003-04 | event-driven | WHEN instantiating template, the SYSTEM shall change instance_type to "aget" |

**Enforcement**: `instantiate_template.py`, contract tests with `@skipif(is_template)`

#### Distinction Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEMPLATE vs INSTANCE DISTINCTION                      │
├─────────────────────┬─────────────────────┬─────────────────────────────┤
│ Aspect              │ Template            │ Instance                    │
├─────────────────────┼─────────────────────┼─────────────────────────────┤
│ instance_type       │ "template"          │ "aget"                      │
│ agent_name          │ null/placeholder    │ populated                   │
│ identity.json       │ placeholder North   │ actual North Star           │
│ Sessions            │ none (empty)        │ accumulated                 │
│ L-docs              │ minimal (examples)  │ accumulated (may be 300+)   │
│ Governance          │ template defaults   │ populated/customized        │
│ Validation          │ template subset     │ full instance validation    │
│ Purpose             │ reusable pattern    │ operational agent           │
└─────────────────────┴─────────────────────┴─────────────────────────────┘
```

### CAP-INST-004: Instance Lifecycle

The SYSTEM shall support instance lifecycle states.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-INST-004-01 | ubiquitous | The SYSTEM shall support Instantiation from template |
| CAP-INST-004-02 | ubiquitous | The SYSTEM shall support Active state with session activity |
| CAP-INST-004-03 | ubiquitous | The SYSTEM shall support Dormant state with preserved content |
| CAP-INST-004-04 | ubiquitous | The SYSTEM shall support Migration between framework versions |
| CAP-INST-004-05 | conditional | IF instance is Migrating THEN the SYSTEM shall preserve Accumulated_Content |

**Enforcement**: AGET_MIGRATION_SPEC, session patterns

#### Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INSTANCE LIFECYCLE                                │
│                                                                          │
│    ┌──────────┐                                                          │
│    │ TEMPLATE │                                                          │
│    └────┬─────┘                                                          │
│         │ instantiate_template.py                                        │
│         ▼                                                                │
│    ┌──────────┐     wake up      ┌────────────┐                         │
│    │ DORMANT  │ ───────────────► │   ACTIVE   │                         │
│    │          │ ◄─────────────── │            │                         │
│    └────┬─────┘    wind down     └─────┬──────┘                         │
│         │                              │                                 │
│         │         migrate              │ migrate                         │
│         ▼                              ▼                                 │
│    ┌─────────────────────────────────────────┐                          │
│    │              MIGRATING                  │                          │
│    │  (content preserved, structure updated) │                          │
│    └─────────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### CAP-INST-005: Instance Migration Requirements

The SYSTEM shall support version migration for instances.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-INST-005-01 | ubiquitous | The SYSTEM shall follow AGET_MIGRATION_SPEC for version transitions |
| CAP-INST-005-02 | ubiquitous | The SYSTEM shall preserve L-docs during migration |
| CAP-INST-005-03 | ubiquitous | The SYSTEM shall preserve governance content during migration |
| CAP-INST-005-04 | ubiquitous | The SYSTEM shall add missing archetype directories during migration |
| CAP-INST-005-05 | ubiquitous | The SYSTEM shall record migration in version.json migration_history |

**Enforcement**: `migrate_instance.py`, L395 (Instance v3.0 Migration Pattern)

#### Instance Migration Pattern (L395)

```
Pre-Migration State (v2.x)          Post-Migration State (v3.0)
─────────────────────────           ─────────────────────────────
.aget/                              .aget/
├── evolution/                      ├── persona/        ← NEW
├── identity.json                   ├── memory/         ← NEW
├── patterns/                       ├── reasoning/      ← NEW
└── version.json                    ├── skills/         ← NEW
                                    ├── context/        ← NEW
                                    ├── evolution/      ← preserved
                                    ├── identity.json   ← preserved
                                    ├── patterns/       ← preserved
                                    └── version.json    ← updated

Visible Directories:
governance/    ← preserved          governance/         ← preserved
planning/      ← preserved          planning/           ← preserved
sessions/      ← preserved          sessions/           ← preserved
                                    knowledge/          ← ADDED per archetype
```

---

## Authority Model

```yaml
authority:
  applies_to: "agent_instances"

  governed_by:
    spec: "AGET_INSTANCE_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    autonomous:
      - "maintain archetype baseline directories"
      - "accumulate session content"
      - "accumulate L-docs"
      - "run instance validation"

    requires_approval:
      - action: "major version migration"
        approver: "user"
      - action: "archetype change"
        approver: "user"
      - action: "framework ejection"
        approver: "user (with constraint acknowledgment)"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-INST-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT lose Accumulated_Content during migration"
      rationale: "L-docs, session notes, governance are user property"
      related: ["CAP-PORT-001", "CAP-MIG-005"]

    - id: "INV-INST-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT set instance_type to invalid value"
      rationale: "Only 'template' or 'aget' are valid"

    - id: "INV-INST-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT operate instance without archetype baseline"
      rationale: "Archetype directories are required for portability"
```

---

## Structural Requirements

```yaml
structure:
  required_files:
    - path: ".aget/version.json"
      purpose: "Instance identity"
      required_fields: ["agent_name", "instance_type", "archetype"]

    - path: ".aget/identity.json"
      purpose: "North Star and purpose"
      required_fields: ["north_star"]
      schema_ref: "AGET_IDENTITY_JSON_SCHEMA.md"
      notes: "north_star MUST be object with 'statement' field (not string) - see L488"

  required_directories:
    core:
      - path: "governance/"
        purpose: "Charter, mission, scope"
      - path: "sessions/"
        purpose: "Session notes"
      - path: "planning/"
        purpose: "Plans, decisions"
      - path: "knowledge/"
        purpose: "Domain knowledge"

    archetype_specific:
      worker: []
      advisor: ["clients/"]
      supervisor: ["fleet/"]
      developer: ["products/"]
      consultant: ["clients/"]
      spec-engineer: ["specs/"]
      executive: ["decisions/"]
      analyst: ["reports/"]
      reviewer: ["reviews/"]
      operator: ["operations/"]
      architect: ["decisions/"]
      researcher: ["research/"]
```

---

## Validation

```bash
# Check instance identity
python3 validation/validate_template_instance.py /path/to/instance -v

# Expected output for valid instance:
# ✅ instance_type: aget
# ✅ archetype: operator
# ✅ Core directories: governance/, sessions/, planning/, knowledge/
# ✅ Archetype directories: operations/
# PASSED: 19, FAILED: 0
```

---

## Theoretical Basis

Instance architecture is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Type Theory** | Template = type, Instance = value. Instances inherit structure, populate content |
| **Prototype-Based OO** | Templates as prototypes; instances clone and extend |
| **Extended Mind** | Accumulated content (L-docs, sessions) extends cognitive capacity |
| **Configuration Management** | version.json tracks identity and migration history |

```yaml
theoretical_basis:
  primary: "Type Theory"
  secondary:
    - "Prototype-Based Object Orientation"
    - "Extended Mind (Clark/Chalmers)"
    - "Configuration Management"
  rationale: >
    The template/instance distinction mirrors type/value in type theory.
    Templates define structure (the type); instances populate that structure
    with actual content (the value). Extended Mind theory explains why
    accumulated content (L-docs, sessions) is user property that must be
    preserved during migration - it extends the human-agent system's
    cognitive capacity.
  references:
    - "L395_instance_v3_migration_pattern.md"
    - "L397_test_bug_vs_spec_gap_distinction.md"
    - "AGET_TEMPLATE_SPEC.md"
```

---

## References

- AGET_TEMPLATE_SPEC.md (template requirements)
- AGET_5D_ARCHITECTURE_SPEC.md (5D structure)
- AGET_PORTABILITY_SPEC.md (content visibility)
- AGET_MIGRATION_SPEC.md (migration process)
- L395: Instance v3.0 Migration Pattern
- L397: Test Bug vs Spec Gap Distinction

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "L395_instance_v3_migration_pattern.md"
    - "instantiate_template.py"
    - "validate_template_instance.py"
  source_learnings:
    - "L395"
    - "L397"
  trigger: "5-why analysis on missing knowledge/ directory (G-PRE.3.1)"
  rationale: "No formal specification existed for agent instances vs templates"
```

---

*AGET Instance Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Lifecycle Management - G-PRE.3.1*
*"Instances are operational agents; templates are reusable patterns."*
