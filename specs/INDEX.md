# AGET Specification Index

**Version**: 1.4.0
**Status**: Active
**Updated**: 2026-01-12
**Author**: aget-framework

This document provides an index of all AGET framework specifications with their Spec IDs, status, authority level, and descriptions.

---

## Spec ID Registry

| Spec ID | Spec Name | Status | Authority | Description |
|---------|-----------|--------|-----------|-------------|
| AGET-CORE-001 | AGET_FRAMEWORK_SPEC | Released | Active | Master framework specification |
| AGET-5D-001 | AGET_5D_ARCHITECTURE_SPEC | Active | Active | 5D Composition Architecture umbrella |
| AGET-5D-002 | AGET_5D_COMPONENTS_SPEC | Active | Active | Consolidated 5D component specs (PERSONA, MEMORY, REASONING, SKILLS, CONTEXT) |
| AGET-VOC-001 | AGET_VOCABULARY_SPEC | Active | Active | Consolidated vocabulary standards |
| AGET-EKO-001 | AGET_EXECUTABLE_KNOWLEDGE_SPEC | Active | Active | Executable Knowledge Ontology (three-axis taxonomy) |
| AGET-GOV-001 | AGET_GOVERNANCE_HIERARCHY_SPEC | Active | Active | Governance hierarchy and authority |
| AGET-LIC-001 | AGET_LICENSE_SPEC | Active | Active | License requirements (Apache 2.0) |
| AGET-ORG-001 | AGET_ORGANIZATION_SPEC | Active | Active | Organization homepage requirements |
| AGET-SEC-001 | AGET_SECURITY_SPEC | Active | Active | Content security and sanitization |
| AGET-TPL-001 | AGET_TEMPLATE_SPEC | Active | Active | Template requirements |
| AGET-INST-001 | AGET_INSTANCE_SPEC | Active | Active | Instance requirements |
| AGET-MIG-001 | AGET_MIGRATION_SPEC | Active | Active | Version migration procedures |
| AGET-COMPAT-001 | AGET_COMPATIBILITY_SPEC | Active | Active | Compatibility requirements |
| AGET-SES-001 | AGET_SESSION_SPEC | Active | Active | Session protocols (wake/wind-down) |
| AGET-SCRIPT-001 | AGET_PYTHON_SCRIPT_SPEC | Active | Active | Python script standards |
| AGET-VAL-001 | AGET_VALIDATION_SPEC | Active | Active | Validator requirements |
| AGET-TEST-001 | AGET_TESTING_SPEC | Active | Active | Testing requirements |
| AGET-CI-001 | AGET_CI_SPEC | Active | Active | CI/CD requirements |
| AGET-PORT-001 | AGET_PORTABILITY_SPEC | Active | Active | Portability requirements |
| AGET-ERR-001 | AGET_ERROR_SPEC | Active | Active | Error handling and exit codes |
| AGET-CP-001 | AGET_CHANGE_PROPOSAL_SPEC | Active | Active | Change proposal process |
| AGET-SOP-001 | AGET_SOP_SPEC | Active | Active | SOP requirements |
| AGET-REL-001 | AGET_RELEASE_SPEC | Active | Active | Release requirements |
| AGET-LDOC-001 | AGET_LDOC_SPEC | Active | Active | L-doc requirements |
| AGET-EVOL-001 | AGET_EVOLUTION_SPEC | Active | Active | Evolution directory requirements (L/D/DISC entry types) |
| AGET-PP-001 | AGET_PROJECT_PLAN_SPEC | Active | Active | PROJECT_PLAN requirements (CAP-PP-011) |
| AGET-FMT-001 | AGET_SPEC_FORMAT | Active | **CANONICAL** | Specification format v1.2 |
| AGET-NAME-001 | AGET_FILE_NAMING_CONVENTIONS | Active | **CANONICAL** | File naming conventions |
| AGET-VER-001 | AGET_VERSIONING_CONVENTIONS | Active | **CANONICAL** | Versioning conventions |
| AGET-DOC-001 | AGET_DOCUMENTATION_SPEC | Active | Active | Documentation requirements |
| AGET-TOOL-001 | AGET_TOOL_SPEC | Active | Active | Tool specifications |
| AGET-COMP-001 | COMPOSITION_SPEC_v1.0 | Approved | Active | Capability composition mechanism |

**Total: 32 specifications**

### Authority Levels

Per AGET_VOCABULARY_SPEC Part 7 (Standards Document Ontology):

| Authority | Meaning | Mutation Allowed |
|-----------|---------|------------------|
| **CANONICAL** | Immutable reference standard | Major version only |
| **Active** | Current normative | Minor/patch allowed |
| **Draft** | Under development | Any change |
| **Deprecated** | Superseded, read-only | None |

---

## Spec ID Format

```
AGET-{DOMAIN}-{NNN}
```

| Component | Description | Examples |
|-----------|-------------|----------|
| `AGET-` | Framework prefix | — |
| `{DOMAIN}` | 2-6 character domain code | CORE, 5D, VOC, GOV |
| `{NNN}` | 3-digit sequence | 001, 002, 003 |

### Domain Codes

| Domain | Description | Specs |
|--------|-------------|-------|
| CORE | Core framework | 1 |
| 5D | 5D Architecture | 2 |
| VOC | Vocabulary | 1 |
| EKO | Executable Knowledge | 1 |
| GOV | Governance | 1 |
| LIC | License | 1 |
| ORG | Organization | 1 |
| SEC | Security | 1 |
| TPL | Template | 1 |
| INST | Instance | 1 |
| MIG | Migration | 1 |
| COMPAT | Compatibility | 1 |
| SES | Session | 1 |
| SCRIPT | Scripts | 1 |
| VAL | Validation | 1 |
| TEST | Testing | 1 |
| CI | CI/CD | 1 |
| PORT | Portability | 1 |
| ERR | Error | 1 |
| CP | Change Proposal | 1 |
| SOP | SOP | 1 |
| REL | Release | 1 |
| LDOC | L-docs | 1 |
| PP | Project Plan | 1 |
| FMT | Format | 1 |
| NAME | Naming | 1 |
| VER | Versioning | 1 |
| DOC | Documentation | 1 |
| TOOL | Tools | 1 |
| COMP | Composition | 1 |

---

## Specs by Category

### Core Architecture

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-CORE-001 | AGET_FRAMEWORK_SPEC | Master specification with all CAP requirements |
| AGET-5D-001 | AGET_5D_ARCHITECTURE_SPEC | 5D Composition Architecture overview |
| AGET-5D-002 | AGET_5D_COMPONENTS_SPEC | Consolidated dimension specs |
| AGET-VOC-001 | AGET_VOCABULARY_SPEC | SKOS-based vocabulary |
| AGET-EKO-001 | AGET_EXECUTABLE_KNOWLEDGE_SPEC | Executable Knowledge Ontology |
| AGET-COMP-001 | COMPOSITION_SPEC_v1.0 | Capability composition algebra |

### Governance

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-GOV-001 | AGET_GOVERNANCE_HIERARCHY_SPEC | Authority and escalation |
| AGET-LIC-001 | AGET_LICENSE_SPEC | Apache 2.0 requirements |
| AGET-ORG-001 | AGET_ORGANIZATION_SPEC | GitHub org requirements |
| AGET-SEC-001 | AGET_SECURITY_SPEC | Content security |

### Lifecycle

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-TPL-001 | AGET_TEMPLATE_SPEC | Template structure |
| AGET-INST-001 | AGET_INSTANCE_SPEC | Instance requirements |
| AGET-MIG-001 | AGET_MIGRATION_SPEC | Migration procedures |
| AGET-COMPAT-001 | AGET_COMPATIBILITY_SPEC | Version compatibility |

### Technical

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-SES-001 | AGET_SESSION_SPEC | Wake/wind-down protocols |
| AGET-SCRIPT-001 | AGET_PYTHON_SCRIPT_SPEC | Script standards |
| AGET-VAL-001 | AGET_VALIDATION_SPEC | Validator requirements |
| AGET-TEST-001 | AGET_TESTING_SPEC | Testing requirements |
| AGET-CI-001 | AGET_CI_SPEC | CI/CD requirements |
| AGET-PORT-001 | AGET_PORTABILITY_SPEC | Portability requirements |
| AGET-ERR-001 | AGET_ERROR_SPEC | Error handling |
| AGET-TOOL-001 | AGET_TOOL_SPEC | Tool specifications |

### Process

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-CP-001 | AGET_CHANGE_PROPOSAL_SPEC | Change proposal process |
| AGET-SOP-001 | AGET_SOP_SPEC | SOP requirements |
| AGET-REL-001 | AGET_RELEASE_SPEC | Release requirements |
| AGET-LDOC-001 | AGET_LDOC_SPEC | L-doc requirements |
| AGET-PP-001 | AGET_PROJECT_PLAN_SPEC | PROJECT_PLAN requirements |

### Format

| Spec ID | Spec | Description |
|---------|------|-------------|
| AGET-FMT-001 | AGET_SPEC_FORMAT | Specification format |
| AGET-NAME-001 | AGET_FILE_NAMING_CONVENTIONS | Naming conventions |
| AGET-VER-001 | AGET_VERSIONING_CONVENTIONS | Versioning conventions |
| AGET-DOC-001 | AGET_DOCUMENTATION_SPEC | Documentation standards |

---

## Archived Specs

The following specs have been superseded and moved to `specs/archive/`:

| Original Spec | Superseded By | Date |
|---------------|---------------|------|
| AGET_GLOSSARY_STANDARD_SPEC | AGET_VOCABULARY_SPEC | 2026-01-04 |
| AGET_CONTROLLED_VOCABULARY | AGET_VOCABULARY_SPEC | 2026-01-04 |
| AGET_PERSONA_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |
| AGET_MEMORY_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |
| AGET_REASONING_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |
| AGET_SKILLS_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |
| AGET_CONTEXT_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |
| AGET_SPEC_FORMAT_v1.1 | AGET_SPEC_FORMAT (v1.2) | 2026-01-04 |

---

## Quick Reference

### Finding Specs by Topic

| If you need... | See Spec ID |
|----------------|-------------|
| Framework overview | AGET-CORE-001 |
| Agent identity (WHO) | AGET-5D-002 Part 1 |
| Agent memory (WHAT KNOWS) | AGET-5D-002 Part 2 |
| Agent reasoning (HOW THINKS) | AGET-5D-002 Part 3 |
| Agent skills (WHAT DOES) | AGET-5D-002 Part 4 |
| Agent context (WHERE/WHEN) | AGET-5D-002 Part 5 |
| Vocabulary terms | AGET-VOC-001 |
| Release process | AGET-REL-001 |
| Testing requirements | AGET-TEST-001 |
| File naming | AGET-NAME-001 |
| PROJECT_PLAN format | AGET-PP-001 |

---

## Changelog

### v1.3.0 (2026-01-09)

- AGET_VOCABULARY_SPEC updated to v1.3.0 (L493, L494)
- All vocabulary prefLabels now compound per L493
- Added Meta-Ontology Terms (Aget_Entity, Aget_Concept, Aget_Property, Aget_Specification)
- Added validate_vocabulary_prose.py validator
- Added CAPABILITY_SPEC_action_item_management.yaml exemplar
- Added Vocabulary Prose Migration Guide

### v1.2.0 (2026-01-06)

- AGET_VOCABULARY_SPEC updated with Core Domain Entities (L459)
- Added AGET-EVOL-001: AGET_EVOLUTION_SPEC

### v1.1.0 (2026-01-04)

- Added AGET-EKO-001: AGET_EXECUTABLE_KNOWLEDGE_SPEC (L451, L453)
- Added EKO domain code
- Total specifications: 30 → 31

### v1.0.0 (2026-01-04)

- Initial index created (PROJECT_PLAN_v3.2.0 Gate 4)
- 30 specifications registered
- 29 domain codes defined
- 8 archived specs documented

---

*INDEX.md — AGET Specification Index*
