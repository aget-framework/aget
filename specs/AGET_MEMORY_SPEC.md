# AGET Memory Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (5D Composition - MEMORY Dimension)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_MEMORY_SPEC.md`

---

## Abstract

This specification defines the MEMORY dimension of the 5D Composition Architecture. Memory enables persistent, structured, shareable knowledge across sessions, agents, and humans. The specification formalizes the 6-layer memory model, continual learning patterns, and memory compliance requirements.

## Motivation

Human-AI collaboration faces fundamental asymmetry:
- AI has no persistent memory (each session starts fresh)
- Human has limited bandwidth to re-explain context
- Project state exists but isn't systematically loaded

L335 (Memory Architecture Principles) established that **KB is not storage—KB is the collaboration substrate**. This specification formalizes that insight into testable requirements.

## Scope

**Applies to**: All AGET agents using `memory-management` capability.

**Defines**:
- 6-layer memory model
- Continual Learning framework
- Memory artifact types
- Session protocols
- Compliance requirements

---

## The 5D Composition Context

Memory is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | - |
| **MEMORY** | Knowledge persistence, learning accumulation | **This document** |
| REASONING | Decision patterns, problem-solving approach | - |
| SKILLS | Specific capabilities, tools, integrations | - |
| CONTEXT | Environmental awareness, situation adaptation | - |

---

## Requirements

### R-MEM-001: 6-Layer Memory Model

Agents SHALL implement the 6-layer memory architecture.

| ID | Requirement | Layer |
|----|-------------|-------|
| R-MEM-001-01 | Agent SHALL maintain working memory (active context) | Layer 1 |
| R-MEM-001-02 | Agent SHALL support session memory (handoff artifacts) | Layer 2 |
| R-MEM-001-03 | Agent SHALL maintain project memory (governance, planning, decisions) | Layer 3 |
| R-MEM-001-04 | Agent SHALL maintain agent memory (.aget/, evolution/, patterns/) | Layer 4 |
| R-MEM-001-05 | Agent MAY participate in fleet memory (cross-agent knowledge) | Layer 5 |
| R-MEM-001-06 | Agent SHALL implement context optimization (selective loading) | Layer 6 |

#### Layer Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: Context Optimization                                   │
│ Selective loading of relevant context into active window        │
│ Patterns: Step Back/Review KB, Wake Protocol, Context Budget    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 5: Fleet Memory                                           │
│ Cross-agent knowledge sharing, pattern graduation               │
│ Artifacts: FLEET_STATE.yaml, upstream/downstream flow           │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: Agent Memory                                           │
│ Identity persistence, capability evolution, pattern libraries   │
│ Artifacts: .aget/, evolution/, patterns/                        │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Project Memory                                         │
│ KB structure, planning artifacts, decision records              │
│ Artifacts: governance/, planning/, decisions/, docs/            │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Session Memory                                         │
│ Session artifacts, decisions made, learnings captured           │
│ Artifacts: sessions/, handoff documents, workspace/             │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Working Memory                                         │
│ Active context window, current conversation state               │
│ Artifacts: None (ephemeral—LLM context window)                  │
└─────────────────────────────────────────────────────────────────┘
```

### R-MEM-002: Continual Learning

Agents SHALL accumulate knowledge through structured learning mechanisms.

| ID | Requirement |
|----|-------------|
| R-MEM-002-01 | Agent SHALL capture learnings as L-docs (L{NNN}_{title}.md) |
| R-MEM-002-02 | L-docs SHALL include: Context, Insight, Application sections |
| R-MEM-002-03 | Learnings MAY graduate to patterns (L-doc → Pattern) |
| R-MEM-002-04 | Patterns MAY graduate to specifications (Pattern → Spec) |
| R-MEM-002-05 | Agent SHALL track graduation history in artifacts |
| R-MEM-002-06 | Agent SHOULD improve techniques based on learnings |

#### Continual Learning Cycle

```
    ┌────────────────────────────────────────────────────┐
    │                CONTINUAL LEARNING                   │
    │                                                     │
    │  Experience ──► L-doc ──► Pattern ──► Spec        │
    │       │           │          │          │          │
    │       │           │          │          │          │
    │       ▼           ▼          ▼          ▼          │
    │   [Session]   [Agent]   [Framework] [Standard]     │
    │    memory     memory     memory      memory        │
    │                                                     │
    │  Each cycle improves agent capability              │
    └────────────────────────────────────────────────────┘
```

**Graduation Pathway** (R-PROC-004):
1. **Experience** → Captured as L-doc in `.aget/evolution/`
2. **L-doc** → If pattern emerges, create pattern document
3. **Pattern** → If broadly applicable, propose specification
4. **Spec** → Framework-level standard

### R-MEM-003: Session Protocols

Agents SHALL implement session memory protocols.

| ID | Requirement |
|----|-------------|
| R-MEM-003-01 | Agent SHALL implement wake protocol (context loading) |
| R-MEM-003-02 | Agent SHALL implement wind-down protocol (artifact capture) |
| R-MEM-003-03 | Agent SHOULD create session handoff for significant sessions |
| R-MEM-003-04 | Wake protocol SHALL complete context recovery < 2 minutes |
| R-MEM-003-05 | Wind-down protocol SHALL document decisions and pending work |

#### Wake Protocol

```bash
# Minimal wake protocol
1. Load .aget/version.json (identity)
2. Load .aget/identity.json (North Star)
3. Check git status (current state)
4. Display summary
```

#### Wind-Down Protocol

```markdown
# Session Handoff Template
## What we set out to do
## What we actually did
## Decisions that changed direction
## Current state
## Next session should start with
## Critical context not to forget
## KB artifacts created/modified
```

### R-MEM-004: Step Back / Review KB

Agents SHALL support mid-session context refresh.

| ID | Requirement |
|----|-------------|
| R-MEM-004-01 | Agent SHALL recognize "step back" or "review kb" triggers |
| R-MEM-004-02 | Review SHALL load relevant KB artifacts by context |
| R-MEM-004-03 | Review SHALL check inherited/, planning/, evolution/, governance/ |
| R-MEM-004-04 | Agent SHALL cite 3+ precedents for governance decisions |
| R-MEM-004-05 | If no precedent exists, agent SHALL note "novel" |

#### Review KB Checklist

```
Before proposing substantial changes:
- [ ] inherited/   — precedents, decision authority
- [ ] planning/    — active work, related PROJECT_PLANs
- [ ] evolution/   — learnings applicable to context
- [ ] governance/  — boundaries, charter, mission
- [ ] Cite 3+ precedents or note "novel"
```

### R-MEM-005: Memory Artifacts

Agents SHALL maintain required memory artifact structure.

| ID | Requirement | Path |
|----|-------------|------|
| R-MEM-005-01 | Agent SHALL have identity file | `.aget/version.json` |
| R-MEM-005-02 | Agent SHALL have evolution directory | `.aget/evolution/` |
| R-MEM-005-03 | Agent SHOULD have patterns directory | `.aget/patterns/` or `docs/patterns/` |
| R-MEM-005-04 | Agent SHALL have governance directory | `governance/` |
| R-MEM-005-05 | Agent SHALL have planning directory | `planning/` |
| R-MEM-005-06 | Agent MAY have inherited knowledge | `inherited/` |

### R-MEM-006: Memory Hygiene

Agents SHOULD maintain memory health.

| ID | Requirement |
|----|-------------|
| R-MEM-006-01 | Agent SHOULD archive stale artifacts (>6 months untouched) |
| R-MEM-006-02 | Agent SHOULD prune orphaned documents |
| R-MEM-006-03 | Agent SHOULD update cross-references when documents move |
| R-MEM-006-04 | Session SHOULD leave KB better than found |
| R-MEM-006-05 | 80%+ of significant sessions SHOULD add/update artifacts |

---

## Memory Capability Contract

Agents with `memory-management` capability MUST satisfy:

```yaml
# Contract for memory-management capability
contracts:
  - name: has_evolution_directory
    assertion: directory_exists
    path: .aget/evolution/

  - name: has_identity_file
    assertion: file_exists
    path: .aget/version.json

  - name: has_governance_directory
    assertion: directory_exists
    path: governance/

  - name: has_planning_directory
    assertion: directory_exists
    path: planning/

  - name: wake_protocol_exists
    assertion: file_exists_or_pattern_implemented
    options:
      - .aget/patterns/session/wake_up.py
      - AGENTS.md (contains wake protocol)

  - name: has_learning_documents
    assertion: directory_not_empty
    path: .aget/evolution/
    warning_only: true
```

---

## Theoretical Basis

Memory architecture is grounded in established theories (L335):

| Theory | Application |
|--------|-------------|
| **Extended Mind** (Clark/Chalmers, 1998) | KB extends cognitive capacity beyond individual minds |
| **Transactive Memory** (Wegner, 1987) | Human-AI pairs develop shared "who knows what" |
| **Distributed Cognition** (Hutchins, 1995) | Cognition happens across people, tools, artifacts |
| **Stigmergy** (Grassé, 1959) | Coordination through environment modification |
| **Cybernetics** (Ashby, 1956) | KB provides requisite variety for context recovery |

```yaml
theoretical_basis:
  primary: Extended Mind
  secondary:
    - Transactive Memory
    - Distributed Cognition
    - Stigmergy
    - Cybernetics (Requisite Variety)
  rationale: >
    Memory architecture treats KB as cognitive infrastructure, not
    documentation. The KB extends human-AI cognition (Extended Mind),
    serves as shared knowledge index (Transactive Memory), carries
    cognition across sessions (Distributed Cognition), enables
    coordination through environment modification (Stigmergy), and
    provides variety to handle situational complexity (Cybernetics).
  reference: L335_memory_architecture_principles.md
```

---

## Continual Learning Framework

### Definition

**Continual Learning** is the framework by which agents accumulate knowledge and improve techniques over time through structured capture, graduation, and application of experiential insights.

### Components

1. **Learning Capture** (L-docs)
   - Format: `L{NNN}_{snake_case_title}.md`
   - Required sections: Context, Insight, Application
   - Location: `.aget/evolution/`

2. **Pattern Emergence**
   - When learning applies to 3+ situations, consider pattern
   - Format: `PATTERN_{name}.md`
   - Location: `docs/patterns/` or `.aget/patterns/`

3. **Specification Graduation**
   - When pattern is broadly applicable, propose spec
   - Requires Change Proposal (CP)
   - Follows R-PROC-004 graduation pathway

4. **Technique Improvement**
   - Agent applies learnings to improve behavior
   - Learnings inform pattern script updates
   - Patterns inform capability definitions

### Example Graduation

```
L376 (Premature Completion Declaration)
    │
    ▼ Pattern extracted (applies to multiple migrations)
PATTERN_migration_validation_gate.md
    │
    ▼ Formalized in specification (R-PROC requirements)
AGET_FRAMEWORK_SPEC (R-PROC-004)
    │
    ▼ Tooling created (enforcement)
validate_graduation_history.py
```

---

## Validation

```bash
# Validate memory compliance
python3 validation/validate_memory_compliance.py --dir /path/to/agent

# Expected output:
# ✅ .aget/version.json exists
# ✅ .aget/evolution/ exists (12 L-docs)
# ✅ governance/ exists
# ✅ planning/ exists
# ⚠️  inherited/ missing (optional)
# ✅ Memory structure compliant
```

---

## References

- L335: Memory Architecture Principles
- L331: Theoretical Foundations of Agency
- MEMORY_VISION.md (governance document)
- PATTERN_step_back_review_kb.md
- R-PROC-004: Artifact Graduation Pathway

---

## Graduation History

- **Source Learning**: L335 (Memory Architecture Principles)
- **Related Pattern**: PATTERN_step_back_review_kb.md
- **Governance Vision**: MEMORY_VISION.md
- **Rationale**: User-discovered "step back. review kb." pattern formalized

---

*AGET Memory Specification v1.0.0*
*Part of v3.0.0 Composition Architecture - MEMORY Dimension*
*"KB is not storage—KB is the collaboration substrate."*
