# AGET 5D Composition Architecture Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Umbrella)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_5D_ARCHITECTURE_SPEC.md`
**Change Proposal**: CP-008

---

## Abstract

This specification defines the **5-Dimensional Composition Architecture** for AGET agents. The 5D model provides a comprehensive framework for understanding, designing, and implementing AI agents by organizing agent characteristics into five orthogonal dimensions: PERSONA, MEMORY, REASONING, SKILLS, and CONTEXT.

## Motivation

Agent design requires coherent organization of many concerns:
- Identity and governance style
- Knowledge and learning
- Decision-making patterns
- Capabilities and outputs
- Environmental awareness

Without a unifying framework, these concerns become ad-hoc and inconsistent. The 5D Architecture provides:
1. **Conceptual clarity**: Each dimension addresses distinct concerns
2. **Composability**: Dimensions are orthogonal and compose cleanly
3. **Completeness**: Five dimensions cover all aspects of agent design
4. **Testability**: Each dimension has measurable requirements

## Scope

**Applies to**: All AGET agents (templates and instances)

**Defines**:
- Five dimensions and their relationships
- Requirements for each dimension
- Integration with capability composition
- Validation requirements

**Related Specifications**:
- AGET_PERSONA_SPEC.md (D1 detail)
- AGET_MEMORY_SPEC.md (D2 detail)
- AGET_REASONING_SPEC.md (D3 detail)
- AGET_SKILLS_SPEC.md (D4 detail)
- AGET_CONTEXT_SPEC.md (D5 detail)
- COMPOSITION_SPEC_v1.0.md (capability composition mechanism)

---

## The 5D Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGET 5D COMPOSITION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  D1: PERSONA ──────────────────────────────────── WHO (Identity)       │
│      • Archetype (supervisor, advisor, worker, etc.)                   │
│      • Governance intensity (rigorous, balanced, exploratory)          │
│      • Communication style (formal, conversational, adaptive)          │
│      • Goal orientation (North Star, mission, objectives)              │
│                                                                         │
│  D2: MEMORY ───────────────────────────────────── WHAT KNOWS           │
│      • 6-layer memory model (working → fleet)                          │
│      • Continual Learning (L-doc → Pattern → Spec)                     │
│      • Session protocols (wake, wind-down)                             │
│      • Knowledge persistence (KB as collaboration substrate)           │
│                                                                         │
│  D3: REASONING ────────────────────────────────── HOW THINKS           │
│      • Planning patterns (PROJECT_PLAN, gates)                         │
│      • Decision frameworks (escalation, authority matrix)              │
│      • Reflection protocols (step back, review KB)                     │
│      • Quality assurance (verification tests, validation)              │
│                                                                         │
│  D4: SKILLS ───────────────────────────────────── WHAT DOES            │
│      • Capabilities (composable behavioral units)                      │
│      • Tools (validators, scripts, patterns)                           │
│      • Outputs (structured formats, artifacts)                         │
│      • A-SDLC phase alignment                                          │
│                                                                         │
│  D5: CONTEXT ──────────────────────────────────── WHERE/WHEN           │
│      • Environmental awareness (codebase, repository state)            │
│      • Relationships (supervisor, peers, managed agents)               │
│      • Temporal awareness (session state, phase in workflow)           │
│      • Scope boundaries (what is/isn't in scope)                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Requirements

### R-5D-001: Dimension Completeness

Agents SHALL address all five dimensions in their design.

| ID | Requirement |
|----|-------------|
| R-5D-001-01 | Agent SHALL have defined PERSONA (archetype + governance) |
| R-5D-001-02 | Agent SHALL have MEMORY structure (.aget/evolution, governance, planning) |
| R-5D-001-03 | Agent SHALL follow REASONING patterns appropriate to governance level |
| R-5D-001-04 | Agent SHALL declare SKILLS via capabilities or manifest |
| R-5D-001-05 | Agent SHALL have CONTEXT awareness (scope, relationships) |

### R-5D-002: Dimension Orthogonality

Dimensions SHALL be independent and compose without interference.

| ID | Requirement |
|----|-------------|
| R-5D-002-01 | PERSONA choices SHALL NOT constrain MEMORY structure |
| R-5D-002-02 | SKILLS SHALL compose independently of REASONING patterns |
| R-5D-002-03 | CONTEXT awareness SHALL NOT override PERSONA identity |
| R-5D-002-04 | Dimension configurations SHALL be separately testable |

### R-5D-003: Dimension Documentation

Agents SHALL document their 5D configuration.

| ID | Requirement |
|----|-------------|
| R-5D-003-01 | AGENTS.md SHALL include dimension summary section |
| R-5D-003-02 | manifest.yaml SHALL declare capabilities (SKILLS dimension) |
| R-5D-003-03 | .aget/identity.json SHALL declare PERSONA elements |
| R-5D-003-04 | CLAUDE.md SHALL operationalize dimension requirements |

---

## Dimension Specifications

Each dimension has a dedicated specification defining detailed requirements:

| Dimension | Specification | Status |
|-----------|---------------|--------|
| D1: PERSONA | AGET_PERSONA_SPEC.md | In Progress |
| D2: MEMORY | AGET_MEMORY_SPEC.md | Active |
| D3: REASONING | AGET_REASONING_SPEC.md | In Progress |
| D4: SKILLS | AGET_SKILLS_SPEC.md | In Progress |
| D5: CONTEXT | AGET_CONTEXT_SPEC.md | In Progress |

---

## Relationship to Capability Composition

The 5D Architecture and Capability Composition (COMPOSITION_SPEC_v1.0) are **orthogonal but complementary**:

| Concern | 5D Architecture | Capability Composition |
|---------|-----------------|----------------------|
| **What** | Dimensions of agent design | How capabilities combine |
| **Focus** | Conceptual organization | Technical mechanism |
| **Question** | "What aspects define an agent?" | "How do behaviors compose?" |
| **Artifacts** | Dimension specs | DAG, prerequisites, conflicts |

### Integration

Capabilities implement aspects of the 5D dimensions:

```yaml
# Example: How capabilities map to dimensions
capabilities:
  # PERSONA dimension
  - capability-governance-rigorous    # Governance intensity

  # MEMORY dimension
  - capability-memory-management      # 6-layer model

  # REASONING dimension
  - capability-gate-discipline        # Planning patterns

  # SKILLS dimension
  - capability-domain-knowledge       # Domain expertise
  - capability-structured-outputs     # Output formats

  # CONTEXT dimension
  - capability-collaboration          # Relationship awareness
```

---

## Dimension Interaction Patterns

While dimensions are orthogonal, they interact at agent runtime:

### Pattern 1: PERSONA → REASONING

Governance intensity influences reasoning patterns:
- Rigorous → Full PROJECT_PLAN for all non-trivial work
- Balanced → Proportional governance
- Exploratory → Flow-first, structure on request

### Pattern 2: MEMORY → CONTEXT

Memory provides context for decisions:
- KB review informs contextual awareness
- Session history provides temporal context
- L-docs inform current work

### Pattern 3: SKILLS → REASONING

Available skills influence planning:
- Validator skills enable verification tests
- Pattern scripts enable automation
- Tool availability shapes execution approach

### Pattern 4: CONTEXT → PERSONA

Environment may invoke governance shifts:
- Public repo work → Higher governance (L340)
- Breaking changes → Escalation required
- Novel territory → Rigorous mode

---

## Theoretical Basis

The 5D Architecture is grounded in established theory (L331):

| Theory | 5D Application |
|--------|----------------|
| **BDI (Belief-Desire-Intention)** | PERSONA = Desires, MEMORY = Beliefs, REASONING = Intentions |
| **Actor Model** | CONTEXT = Actor boundaries, SKILLS = Message handling |
| **Cybernetics** | SKILLS = Requisite variety, MEMORY = Feedback loops |
| **Extended Mind** | MEMORY = Cognitive extension, SKILLS = Cognitive scaffolding |
| **Complex Adaptive Systems** | All dimensions interact for emergent fleet behavior |

```yaml
theoretical_basis:
  primary: BDI (Belief-Desire-Intention)
  secondary:
    - Actor Model
    - Extended Mind
    - Cybernetics
    - Complex Adaptive Systems
  rationale: >
    The 5D model maps to BDI's mental states while incorporating
    Actor Model boundaries, Extended Mind cognitive extension,
    Cybernetics feedback and variety, and CAS emergence at fleet level.
  reference: L331_theoretical_foundations_agency.md
```

---

## Validation

### Dimension Validators

| Dimension | Validator | Purpose |
|-----------|-----------|---------|
| MEMORY | validate_memory_compliance.py | 6-layer structure |
| SKILLS | validate_composition.py | Capability composition |
| All | validate_template_manifest.py | Manifest structure |

### 5D Compliance Check

```bash
# Validate MEMORY dimension
python3 validation/validate_memory_compliance.py --dir /path/to/agent

# Validate SKILLS dimension (via manifest)
python3 validation/validate_template_manifest.py /path/to/manifest.yaml

# Validate SKILLS composition
python3 validation/validate_composition.py /path/to/manifest.yaml
```

---

## Agent Design Checklist

When designing a new agent, address each dimension:

### D1: PERSONA
- [ ] Base template selected (supervisor, advisor, worker, etc.)
- [ ] Governance intensity declared (rigorous, balanced, exploratory)
- [ ] North Star defined (identity.json)
- [ ] Communication style established

### D2: MEMORY
- [ ] .aget/evolution/ directory exists
- [ ] governance/ and planning/ directories exist
- [ ] Wake/wind-down protocols defined
- [ ] L-doc conventions followed

### D3: REASONING
- [ ] Planning patterns match governance intensity
- [ ] Decision authority documented
- [ ] Escalation paths defined
- [ ] Verification tests included

### D4: SKILLS
- [ ] Capabilities declared in manifest
- [ ] Tools/validators available
- [ ] Output formats defined
- [ ] A-SDLC phase alignment clear

### D5: CONTEXT
- [ ] Scope boundaries documented
- [ ] Relationships defined (supervisor, peers)
- [ ] Environmental awareness protocols
- [ ] Session state handling

---

## Graduation History

- **Source Learnings**: L330 (Capability Composition), L331 (Theoretical Foundations), L335 (Memory Architecture), L341 (Governance Intensity)
- **Related Pattern**: 5W+H Knowledge Architecture
- **Rationale**: Unifies multiple learnings into coherent architectural framework

---

## References

- L330: Capability Composition Architecture
- L331: Theoretical Foundations of Agency
- L335: Memory Architecture Principles
- L341: Governance Intensity Classification
- COMPOSITION_SPEC_v1.0: Capability composition mechanism
- AGET_MEMORY_SPEC: D2 dimension detail

---

*AGET 5D Composition Architecture Specification v1.0.0*
*Part of v3.0.0 Composition Architecture*
*"Five dimensions, one coherent agent."*
