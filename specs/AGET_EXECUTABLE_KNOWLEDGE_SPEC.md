# AGET Executable Knowledge Specification

**Spec ID**: AGET-EKO-001
**Version**: 1.0.0
**Status**: Active
**Category**: Core (Ontology)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: aget-framework
**Location**: `aget/specs/AGET_EXECUTABLE_KNOWLEDGE_SPEC.md`
**Change Origin**: PROJECT_PLAN_executable_knowledge_ontology_v1.0 Gate 4
**Related Specs**: AGET_VOCABULARY_SPEC, AGET_FILE_NAMING_CONVENTIONS

---

## Abstract

This specification defines the Executable Knowledge Ontology (EKO) — a taxonomy for classifying actionable artifacts that agents produce, consume, and execute. EKO provides a three-axis classification system enabling agents to reason about artifact determinism, reusability, and abstraction level.

## Motivation

AGET agents work with diverse knowledge artifacts: SOPs, Runbooks, Playbooks, PROJECT_PLANs, Patterns, and more. Without systematic classification:

1. **Autonomy Decisions Unclear**: When can an agent proceed autonomously vs. requiring human approval?
2. **Artifact Selection Difficult**: Which artifact type fits a given task?
3. **Vocabulary Ambiguity**: "Procedure" vs "Protocol" vs "Process" confusion

EKO addresses these gaps with a self-contained vocabulary (per L453: AGET Ontology Independence) that enables agents to classify and reason about executable knowledge.

---

## Scope

**Applies to**: All AGET artifacts that encode executable knowledge.

**Defines**:
- Three-axis taxonomy (Abstraction, Determinism, Reusability)
- Classification requirements for AGET artifact types
- Autonomy delegation principles

**Does NOT define**:
- External ontology bindings (per L453)
- Implementation details for specific artifact types
- Execution semantics (runtime behavior)

---

## Three-Axis Taxonomy

### Axis 1: Abstraction Level

Measures position from abstract specification to concrete execution.

```
Highest Abstraction
        │
        ├── Algorithm   → Formal operation that terminates
        ├── Function    → Maps domain to range
        ├── Procedure   → Steps to accomplish task
        ├── Protocol    → Rules for interaction
        ├── Process     → Activity sequence with state
        ├── Workflow    → Orchestrated task sequence
        └── Execution   → Specific instance with timestamp
        │
Lowest Abstraction
```

### Axis 2: Determinism Level

Measures predictability of artifact behavior.

| Level | Definition | Autonomy Implication |
|-------|------------|---------------------|
| **Deterministic** | Same input → Same output | HIGH autonomy delegable |
| **Probabilistic** | Formally modeled uncertainty | MEDIUM autonomy delegable |
| **Syllogistic** | Reasoning-based, judgment required | LOW autonomy delegable |

### Axis 3: Reusability Level

Measures frequency and scope of artifact application.

| Level | Definition | Example |
|-------|------------|---------|
| **Universal** | Same every time, all contexts | SOP, Algorithm |
| **Parameterized** | Template with inputs | Runbook, Protocol |
| **One-Time** | Specific instance, unique execution | PROJECT_PLAN |

---

## AGET Artifact Classification

| Artifact | Abstraction | Determinism | Reusability |
|----------|-------------|-------------|-------------|
| `SOP_*.md` | Procedure | Deterministic | Universal |
| `RUNBOOK_*.md` | Procedure | Deterministic | Parameterized |
| `PLAYBOOK_*.md` | Protocol | Syllogistic | Parameterized |
| `PROJECT_PLAN_*.md` | Process | Syllogistic | One-Time |
| `PATTERN_*.md` | Protocol | Deterministic | Universal |
| `*_PROTOCOL.md` | Protocol | Deterministic | Universal |
| `*_CHECKLIST.md` | Procedure | Deterministic | Parameterized |

---

## Autonomy Delegation Principle

EKO's determinism axis enables autonomy decisions:

```
Determinism Level → Autonomy Guidance
─────────────────────────────────────
Deterministic     → Agent MAY proceed autonomously
Probabilistic     → Agent SHOULD verify with human
Syllogistic       → Agent MUST consult human
```

**Application**:
- Agent executing `SOP_release_process.md` (deterministic) → Can proceed
- Agent executing `PLAYBOOK_security_breach.md` (syllogistic) → Must consult Principal

---

## Requirements

### CAP-EKO-001: Three-Axis Taxonomy

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-EKO-001-01 | Artifacts SHOULD classify abstraction level | Enables abstraction reasoning |
| CAP-EKO-001-02 | Abstraction levels SHALL use EKO vocabulary terms | Consistency |
| CAP-EKO-001-03 | Vocabulary definitions SHALL be in AGET_VOCABULARY_SPEC | Single source |

### CAP-EKO-002: Determinism Classification

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-EKO-002-01 | Artifacts SHOULD classify determinism level | Autonomy guidance |
| CAP-EKO-002-02 | Determinism classification MAY inform automation decisions | Decision support |
| CAP-EKO-002-03 | Determinism values SHALL be: Deterministic, Probabilistic, Syllogistic | Vocabulary consistency |

### CAP-EKO-003: Reusability Classification

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-EKO-003-01 | Artifacts SHOULD classify reusability level | Template selection |
| CAP-EKO-003-02 | Reusability values SHALL be: Universal, Parameterized, One_Time | Vocabulary consistency |

### CAP-EKO-004: Independence (L453)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-EKO-004-01 | EKO vocabulary SHALL be self-contained | Community contribution readiness |
| CAP-EKO-004-02 | External ontologies MAY inform but SHALL NOT bind | No approval gates |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-EKO-001-* | Manual review | Advisory |
| CAP-EKO-002-* | Manual review | Advisory |
| CAP-EKO-003-* | Manual review | Advisory |
| CAP-EKO-004-* | validate_vocabulary.py | Planned |

---

## Usage Examples

### Example 1: Classifying a New Artifact

When creating `RUNBOOK_deployment.md`:

1. **What is the abstraction?** → Procedure (steps to accomplish deployment)
2. **What is the determinism?** → Deterministic (same inputs → same outcome)
3. **What is the reusability?** → Parameterized (template with environment inputs)

Result: `aget:abstraction=procedure`, `aget:determinism=deterministic`, `aget:reusability=parameterized`

### Example 2: Autonomy Decision

Agent encounters `PLAYBOOK_incident_response.md`:

1. Check determinism → Syllogistic
2. Apply principle → Agent MUST consult human
3. Action → "I've identified an incident. Here are my recommended actions. Please approve before I proceed."

---

## Theoretical Grounding

EKO is grounded in established theory:

| Theory | Application |
|--------|-------------|
| **Procedural Knowledge Ontology** | Hierarchy of executable artifacts |
| **Bounded Rationality (Simon)** | Determinism axis → decision complexity |
| **Design Patterns** | Reusability axis → pattern vs instance |
| **Semiotics** | Abstraction axis → specification to execution |

---

## References

### L-docs

- L450: GM-RKB ↔ AGET Taxonomy Alignment (historical research)
- L451: Executable Knowledge Ontology (EKO) vision document
- L453: AGET Ontology Independence Decision

### Related Specs

- AGET_VOCABULARY_SPEC.md — EKO terms defined
- AGET_FILE_NAMING_CONVENTIONS.md — Artifact naming patterns
- AGET_PROJECT_PLAN_SPEC.md — One-time artifact requirements

### External Research

- [Procedural Knowledge Ontology](https://arxiv.org/html/2503.20634v1)
- [ISO 9001 Document Hierarchy](https://the9000store.com/iso-9001-2015-requirements/)
- [Runbook vs Playbook Distinctions](https://www.cutover.com/blog/differences-runbooks-playbooks-sops)

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial specification created (PROJECT_PLAN_executable_knowledge_ontology Gate 4)
- Three-axis taxonomy defined (Abstraction, Determinism, Reusability)
- CAP-EKO-001 through CAP-EKO-004 requirements
- AGET artifact classification table
- Autonomy delegation principle
- L453 independence requirements

---

*AGET_EXECUTABLE_KNOWLEDGE_SPEC.md — Executable Knowledge Ontology for AGET framework*
*"EKO enables agents to reason about what they can do autonomously versus when to ask for help."*
