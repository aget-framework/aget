# {Type} Template Specification

**Version**: 1.0.0
**Status**: Active
**Owner**: template-{type}-aget
**Created**: YYYY-MM-DD
**Updated**: YYYY-MM-DD
**Archetype**: {Type}
**Template**: SPEC_TEMPLATE_v3.3

---

## Abstract

{One paragraph describing the template's core purpose and domain.}

---

## Scope

This specification defines the core capabilities that all {type} instances must provide.

### In Scope

- Core {type} capabilities (≥5 requirements)
- EARS-compliant requirement format
- Archetype constraints
- Inviolables
- EKO classification

### Out of Scope

- Instance-specific extensions
- Integration with specific tools or systems

---

## Archetype Definition

### Core Identity

{Description of what this archetype fundamentally IS.}

### Authority Level

| Attribute | Value |
|-----------|-------|
| Decision Authority | {base/elevated/high} |
| Governance Intensity | {exploratory/balanced/rigorous} |
| Supervision Model | {peer/supervised/supervisor} |

---

## Capabilities

### CAP-{TYP}-001: {Primary Capability}

**WHEN** performing {type} activities
**THE** agent SHALL {primary action}

**Rationale**: Core {type} capability
**Verification**: {Verification method}

### CAP-{TYP}-002: {Secondary Capability}

**WHEN** performing {type} activities
**THE** agent SHALL {secondary action}

**Rationale**: Core {type} capability
**Verification**: {Verification method}

### CAP-{TYP}-003: {Tertiary Capability}

**WHEN** performing {type} activities
**THE** agent SHALL {tertiary action}

**Rationale**: Core {type} capability
**Verification**: {Verification method}

### CAP-{TYP}-004: {Fourth Capability}

**WHEN** {specific condition}
**THE** agent SHALL {conditional action}

**Rationale**: {Domain rationale}
**Verification**: {Verification method}

### CAP-{TYP}-005: {Fifth Capability}

**WHEN** {specific condition}
**THE** agent SHALL {conditional action}

**Rationale**: {Domain rationale}
**Verification**: {Verification method}

---

## Inviolables

### Inherited from Framework

| ID | Statement |
|----|-----------|
| INV-CORE-001 | The agent SHALL NOT perform actions outside its declared scope |
| INV-CORE-002 | The agent SHALL maintain session continuity protocols |
| INV-CORE-003 | The agent SHALL follow substantial change protocol |

### Archetype-Specific

| ID | Statement |
|----|-----------|
| INV-{TYP}-001 | {Archetype-specific constraint} |
| INV-{TYP}-002 | {Archetype-specific constraint} |

---

## EKO Classification

Per AGET_EXECUTABLE_KNOWLEDGE_SPEC.md:

| Dimension | Value | Rationale |
|-----------|-------|-----------|
| Abstraction Level | {Template/Instance/Component} | Templates define reusable patterns |
| Determinism Level | {High/Medium/Low} | {Rationale for level} |
| Reusability Level | {High/Medium/Low} | {Rationale for level} |
| Artifact Type | Specification | This is a capability specification |

---

## Archetype Constraints

### What This Template IS

- {Positive constraint 1}
- {Positive constraint 2}
- {Positive constraint 3}

### What This Template IS NOT

- {Negative constraint 1}
- {Negative constraint 2}
- {Negative constraint 3}

---

## Verification

| Requirement | Verification Method |
|-------------|---------------------|
| CAP-{TYP}-001 | Operational demonstration |
| CAP-{TYP}-002 | Operational demonstration |
| CAP-{TYP}-003 | Operational demonstration |
| CAP-{TYP}-004 | {Specific method} |
| CAP-{TYP}-005 | {Specific method} |

---

## A-SDLC Phase Coverage

| Phase | Coverage | Notes |
|-------|----------|-------|
| 0: Discovery | {Primary/Secondary/None} | |
| 1: Specification | {Primary/Secondary/None} | |
| 2: Design | {Primary/Secondary/None} | |
| 3: Implementation | {Primary/Secondary/None} | |
| 4: Validation | {Primary/Secondary/None} | |
| 5: Deployment | {Primary/Secondary/None} | |
| 6: Maintenance | {Primary/Secondary/None} | |

---

## References

- L481: Ontology-Driven Agent Creation
- L482: Executable Ontology - SKOS+EARS Grounding
- {Type}_VOCABULARY.md
- AGET_INSTANCE_SPEC.md
- AGET_TEMPLATE_SPEC.md

---

*{Type}_SPEC.md v1.0.0 — EARS-compliant capability specification*
*Template: SPEC_TEMPLATE_v3.3*
*Generated: YYYY-MM-DD*
