# AGET Requirements Traceability Matrix

**Version**: 1.2.0
**Status**: Active
**Updated**: 2026-01-07
**Author**: aget-framework

This document provides traceability from L-docs and issues to CAP requirements and specifications.

---

## Overview

The AGET framework uses a hierarchical requirements structure:

```
Issue/L-doc → CAP Requirement → Specification → Validator → Test
```

---

## CAP Requirements by Domain

### CAP-PERSONA (AGET_5D_COMPONENTS_SPEC Part 1)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-PERSONA-001 | Archetype Declaration | L99 | validate_persona_compliance.py |
| CAP-PERSONA-002 | Governance Intensity | L341 | validate_persona_compliance.py |
| CAP-PERSONA-003 | Communication Style | L341 | Documentation review |
| CAP-PERSONA-004 | Goal Orientation | L99 | validate_persona_compliance.py |
| CAP-PERSONA-005 | Identity Artifacts | - | validate_agent_structure.py |

### CAP-MEMORY (AGET_5D_COMPONENTS_SPEC Part 2)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-MEMORY-001 | Six Layer Memory Model | L335 | validate_memory_compliance.py |
| CAP-MEMORY-002 | Continual Learning | L335 | validate_learning_doc.py |
| CAP-MEMORY-003 | Session Protocols | L335 | Script execution |
| CAP-MEMORY-004 | Step Back Review KB | L335 | Documentation review |
| CAP-MEMORY-005 | Memory Artifacts | L335 | validate_memory_compliance.py |
| CAP-MEMORY-006 | Memory Hygiene | L335 | Manual review |
| CAP-MEMORY-007 | Memory Configuration | L394 | validate_memory_compliance.py |
| CAP-MEMORY-008 | L-doc Index | L394 | validate_ldoc_index.py |

### CAP-REASON (AGET_5D_COMPONENTS_SPEC Part 3)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-REASON-001 | Planning Patterns | L186 | validate_project_plan.py |
| CAP-REASON-002 | Decision Frameworks | - | Documentation review |
| CAP-REASON-003 | Gate Discipline | L42 | Gate review |
| CAP-REASON-004 | Reflection Protocols | L335 | Documentation review |
| CAP-REASON-005 | Quality Assurance | L382 | validate_project_plan.py |
| CAP-REASON-006 | Session Scope | L342 | Session review |
| CAP-REASON-007 | Execution Governance | L340 | Pre-execution checklist |
| CAP-REASON-008 | Release Retrospective | L435 | validate_project_plan.py --release |

### CAP-SKILL (AGET_5D_COMPONENTS_SPEC Part 4)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-SKILL-001 | Capability Declaration | L330 | validate_template_manifest.py |
| CAP-SKILL-002 | Tool Availability | - | validate_script_registry.py |
| CAP-SKILL-003 | Output Formats | - | Documentation review |
| CAP-SKILL-004 | A-SDLC Phase Alignment | - | Manifest review |
| CAP-SKILL-005 | Skill Documentation | - | Documentation review |
| CAP-SKILL-006 | Capability Composition | L330 | validate_composition.py |

### CAP-CONTEXT (AGET_5D_COMPONENTS_SPEC Part 5)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-CONTEXT-001 | Environmental Awareness | L185 | Operational review |
| CAP-CONTEXT-002 | Relationship Structure | L342 | validate_context_compliance.py |
| CAP-CONTEXT-003 | Temporal Awareness | - | Session protocol review |
| CAP-CONTEXT-004 | Scope Boundaries | L342 | Scope review |
| CAP-CONTEXT-005 | Context Documentation | - | validate_context_compliance.py |
| CAP-CONTEXT-006 | Context-Driven Adaptation | L340 | Operational review |

### CAP-VOC (AGET_VOCABULARY_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-VOC-001 | SKOS Foundation | ADR-001 | validate_vocabulary.py |
| CAP-VOC-002 | Term Usage | - | Manual review |
| CAP-VOC-003 | L440 Verification Terms | L440 | V-test execution |

### CAP-TEST (AGET_TESTING_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-TEST-001 | Contract Tests | - | pytest |
| CAP-TEST-002 | Unit Tests | - | pytest |
| CAP-TEST-003 | V-Tests | L440 | validate_project_plan.py |
| CAP-TEST-004 | Coverage | - | coverage.py |
| CAP-TEST-005 | CI Integration | - | CI workflow |
| CAP-TEST-006 | Validator Theater | L433 | Theater ratio calculation |

### CAP-REL (AGET_RELEASE_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-REL-001 | Release Coordination | v3.1 | validate_release_gate.py |
| CAP-REL-002 | Version Consistency | L429 | validate_version_consistency.py |
| CAP-REL-003 | CHANGELOG | - | CHANGELOG review |
| CAP-REL-004 | GitHub Release | - | gh release verify |
| CAP-REL-005 | Deep Release Notes | v3.1 | Documentation review |
| CAP-REL-006 | Manager Migration | L440 | validate_release_gate.py |
| CAP-REL-007 | Post-Release Validation | L406 | validate_release_gate.py |
| CAP-REL-008 | Version Inventory | L429 | Manual review |

### CAP-PP (AGET_PROJECT_PLAN_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-PP-001 | Gated Structure | L186 | validate_project_plan.py |
| CAP-PP-002 | Decision Points | L42 | Gate review |
| CAP-PP-003 | Deliverables | - | validate_project_plan.py |
| CAP-PP-004 | Status Tracking | - | validate_project_plan.py |
| CAP-PP-005 | Success Criteria | - | validate_project_plan.py |
| CAP-PP-006 | Risk Assessment | - | validate_project_plan.py |
| CAP-PP-007 | Traceability | L352 | validate_project_plan.py |
| CAP-PP-008 | Effort Estimation | - | Manual review |
| CAP-PP-009 | Velocity Analysis | - | Post-execution analysis |
| CAP-PP-010 | References | - | validate_project_plan.py |
| CAP-PP-011 | V-Tests | L440 | validate_project_plan.py --strict |

### CAP-EVOL (AGET_EVOLUTION_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-EVOL-001 | Learning Entries (L-prefix) | L461 | validate_ldoc.py |
| CAP-EVOL-002 | Decision Entries (D-prefix) | L461 | validate_evolution_entry.py |
| CAP-EVOL-003 | Discovery Entries (DISC-prefix) | L461 | validate_evolution_entry.py |
| CAP-EVOL-004 | Flat Directory Structure | L460 | validate_content_placement.py |
| CAP-EVOL-005 | Content Placement | L460 | validate_content_placement.py |
| CAP-EVOL-006 | Evolution Index | L394 | validate_evolution_index.py |

### CAP-EKO (AGET_EXECUTABLE_KNOWLEDGE_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-EKO-001 | Three-Axis Taxonomy | L451 | Documentation review |
| CAP-EKO-002 | Abstraction Level Classification | L451 | validate_artifact_type.py |
| CAP-EKO-003 | Determinism Level Classification | L451 | validate_artifact_type.py |
| CAP-EKO-004 | Reusability Level Classification | L451 | validate_artifact_type.py |
| CAP-EKO-005 | Autonomy Delegation | L451 | Manual review |
| CAP-EKO-006 | AGET Ontology Independence | L453 | Documentation review |

### CAP-DOC (AGET_DOCUMENTATION_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-DOC-001 | README Structure | - | README review |
| CAP-DOC-002 | CLI Settings Files | - | validate_cli_settings.py |
| CAP-DOC-003 | Inline Documentation | - | Code review |
| CAP-DOC-004 | Example Documentation | - | Documentation review |
| CAP-DOC-005 | Documentation Hygiene | - | Manual review |
| CAP-DOC-006 | Version References | L429 | validate_version_consistency.py |

### CAP-ORG (AGET_ORGANIZATION_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-ORG-001 | Homepage Update | R-REL-010 | Homepage review |
| CAP-ORG-002 | Homepage Content | - | validate_homepage_messaging.py |
| CAP-ORG-003 | Repository Naming | - | Naming review |
| CAP-ORG-004 | Pinned Repositories | - | Manual review |
| CAP-ORG-005 | Roadmap Visibility | - | Homepage review |

### CAP-ERR (AGET_ERROR_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-ERR-001 | Exit Codes | - | Script testing |
| CAP-ERR-002 | Error Messages | - | Code review |
| CAP-ERR-003 | Recovery Patterns | - | Documentation review |
| CAP-ERR-004 | Verbose Mode | - | Script testing |

### CAP-SEC (AGET_SECURITY_SPEC)

| CAP ID | Requirement | Source | Validator |
|--------|-------------|--------|-----------|
| CAP-SEC-001 | Content Security | L430 | validate_public_content.py |
| CAP-SEC-002 | Secrets Management | - | .gitignore review |
| CAP-SEC-003 | Pre-Publication Review | - | PR review checklist |
| CAP-SEC-004 | Public/Private Boundary | - | Manual review |
| CAP-SEC-005 | Audit Logging | - | Release review |

---

## L-doc to CAP Traceability

| L-doc | Title | CAP Requirements |
|-------|-------|------------------|
| L42 | Gate Discipline | CAP-REASON-003, CAP-PP-002 |
| L99 | Every Agent is a Worker | CAP-PERSONA-001, CAP-PERSONA-004 |
| L185 | Environmental Grounding | CAP-CONTEXT-001 |
| L186 | PROJECT_PLAN Pattern | CAP-REASON-001, CAP-PP-001 |
| L330 | Capability Composition | CAP-SKILL-001, CAP-SKILL-006 |
| L335 | Memory Architecture | CAP-MEMORY-001 to CAP-MEMORY-008 |
| L340 | Execution Governance | CAP-REASON-007, CAP-CONTEXT-006 |
| L341 | Governance Intensity | CAP-PERSONA-002, CAP-PERSONA-003 |
| L342 | Session Scope | CAP-REASON-006, CAP-CONTEXT-002, CAP-CONTEXT-004 |
| L352 | Traceability | CAP-PP-007 |
| L382 | Gate Verification | CAP-REASON-005, CAP-PP-011 |
| L394 | Design by Fleet Exploration | CAP-MEMORY-007, CAP-MEMORY-008 |
| L406 | Post-Release Validation | CAP-REL-007 |
| L429 | Version Inventory | CAP-REL-002, CAP-REL-008, CAP-DOC-006 |
| L430 | Content Security | CAP-SEC-001 |
| L433 | Validator Theater | CAP-TEST-006 |
| L435 | Retrospective Requirement | CAP-REASON-008, CAP-PP-001 |
| L440 | Verification Gap | CAP-VOC-003, CAP-TEST-003, CAP-PP-011, CAP-REL-006 |
| L451 | Executable Knowledge Ontology | CAP-EKO-001 to CAP-EKO-005 |
| L453 | AGET Ontology Independence | CAP-EKO-006 |
| L460 | Directory Semantics | CAP-EVOL-004, CAP-EVOL-005 |
| L461 | Evolution Entry Types | CAP-EVOL-001 to CAP-EVOL-003 |

---

## Issue to CAP Traceability

| Issue | Title | CAP Requirements | Status |
|-------|-------|------------------|--------|
| #30 | PROJECT_PLAN Spec | CAP-PP-001 to CAP-PP-011 | Complete |
| #33 | Naming Convention Expansion | CAP-NAME-* (File Naming) | Complete |
| #36 | Validator Enforcement | CAP-TEST-006 | In Progress |

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial requirements matrix
- 78 CAP requirements documented
- 18 L-docs traced
- 3 issues traced

---

*REQUIREMENTS_MATRIX.md — Requirements traceability for AGET framework*
