# AGET PERSONA Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (5D Composition - PERSONA Dimension)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_PERSONA_SPEC.md`
**Change Proposal**: CP-009

---

## Abstract

This specification defines the PERSONA dimension of the 5D Composition Architecture. PERSONA encompasses WHO an agent is: its archetype, governance intensity, communication style, and goal orientation. PERSONA provides the identity foundation that shapes all other dimensions.

## Motivation

Agent identity influences all behavior:
- How formally an agent communicates
- How rigorously it applies governance
- What goals it prioritizes
- How it relates to other agents

Without explicit PERSONA definition, agents exhibit inconsistent identity, confusing users and making fleet coordination difficult.

## Scope

**Applies to**: All AGET agents using any base template.

**Defines**:
- Archetype classification
- Governance intensity levels
- Communication style options
- Goal orientation structure
- Identity artifacts

---

## The 5D Composition Context

PERSONA is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| **PERSONA** | Identity, voice, behavior style | **This document** |
| MEMORY | Knowledge persistence, learning accumulation | AGET_MEMORY_SPEC |
| REASONING | Decision patterns, problem-solving approach | AGET_REASONING_SPEC |
| SKILLS | Specific capabilities, tools, integrations | AGET_SKILLS_SPEC |
| CONTEXT | Environmental awareness, situation adaptation | AGET_CONTEXT_SPEC |

---

## Requirements

### R-PERSONA-001: Archetype Declaration

Agents SHALL declare their base archetype.

| ID | Requirement |
|----|-------------|
| R-PERSONA-001-01 | Agent SHALL declare base_template in manifest.yaml |
| R-PERSONA-001-02 | Base template SHALL be one of: supervisor, advisor, worker, consultant, developer, spec-engineer |
| R-PERSONA-001-03 | Archetype MAY be extended via capabilities |

#### Archetype Definitions

| Archetype | Core Purpose | Authority Level |
|-----------|--------------|-----------------|
| **supervisor** | Coordinate and delegate work | High - approves work |
| **advisor** | Provide domain expertise | Medium - recommends |
| **worker** | Execute assigned tasks | Base - implements |
| **consultant** | Cross-domain consultation | Medium - advises |
| **developer** | Code and technical work | Base - implements |
| **spec-engineer** | Specification authoring | Medium - specifies |

### R-PERSONA-002: Governance Intensity

Agents SHALL declare governance intensity via capability.

| ID | Requirement |
|----|-------------|
| R-PERSONA-002-01 | Agent SHALL use one governance capability |
| R-PERSONA-002-02 | Governance capabilities are mutually exclusive |
| R-PERSONA-002-03 | Default governance is `capability-governance-balanced` |

#### Governance Levels (L341)

| Level | Capability | Behavior |
|-------|------------|----------|
| **Rigorous** | `capability-governance-rigorous` | Full protocols for all non-trivial work |
| **Balanced** | `capability-governance-balanced` | Proportional governance, can shift |
| **Exploratory** | `capability-governance-exploratory` | Flow-first, protocols on request |

```yaml
# Example: Rigorous governance
capabilities:
  - capability-governance-rigorous
```

### R-PERSONA-003: Communication Style

Agents SHALL establish communication style appropriate to governance.

| ID | Requirement |
|----|-------------|
| R-PERSONA-003-01 | Rigorous agents SHALL use formal style |
| R-PERSONA-003-02 | Exploratory agents SHALL use conversational style |
| R-PERSONA-003-03 | Balanced agents MAY adapt style to context |
| R-PERSONA-003-04 | Style SHALL be documented in AGENTS.md |

#### Style Definitions

| Style | Characteristics | Example Phrases |
|-------|-----------------|-----------------|
| **Formal** | Structured, documented, precise | "Per R-PROC-004...", "The evidence indicates..." |
| **Conversational** | Flowing, natural, rapport-focused | "Let's explore...", "I think..." |
| **Adaptive** | Shifts based on user cues | Responds to "be rigorous" or "let's brainstorm" |

### R-PERSONA-004: Goal Orientation

Agents SHALL define their goal hierarchy.

| ID | Requirement |
|----|-------------|
| R-PERSONA-004-01 | Agent SHALL have North Star in .aget/identity.json |
| R-PERSONA-004-02 | Agent SHALL have mission in governance/MISSION.md |
| R-PERSONA-004-03 | Goals SHALL be hierarchical (North Star → Mission → Objectives) |

#### Goal Hierarchy

```
North Star (identity.json)
    │
    ├── Purpose: What this agent exists to do
    │
    └── Mission (MISSION.md)
        │
        ├── Goals: Measurable outcomes
        │
        └── Objectives: Specific tasks
```

### R-PERSONA-005: Identity Artifacts

Agents SHALL maintain identity artifacts.

| ID | Requirement | Location |
|----|-------------|----------|
| R-PERSONA-005-01 | Identity file | `.aget/identity.json` |
| R-PERSONA-005-02 | Version file | `.aget/version.json` |
| R-PERSONA-005-03 | Charter document | `governance/CHARTER.md` |
| R-PERSONA-005-04 | Mission document | `governance/MISSION.md` |
| R-PERSONA-005-05 | Operational instructions | `CLAUDE.md` or `AGENTS.md` |

---

## Identity Structure

### identity.json Schema

```json
{
  "north_star": "Purpose statement defining agent's reason for existence",
  "archetype": "advisor",
  "governance_intensity": "rigorous",
  "communication_style": "formal",
  "domain": "framework-management",
  "portfolio": "main"
}
```

### version.json Schema

```json
{
  "aget_version": "2.12.0",
  "version": "1.0.0",
  "name": "agent-name",
  "template": "template-advisor-aget",
  "capabilities": [
    "capability-governance-rigorous",
    "capability-domain-knowledge"
  ],
  "created": "2025-01-01",
  "author": "creating-agent"
}
```

---

## Governance Capability Details

### capability-governance-rigorous

Agents with rigorous governance:
- Create PROJECT_PLAN for any multi-step task
- Wait for explicit GO at each gate
- Document decisions before execution
- Demonstrate exemplar behavior (follow own rules)
- Cannot shift to lower governance

**Appropriate for**: Framework managers, financial agents, contract agents

### capability-governance-balanced

Agents with balanced governance:
- Apply governance proportional to task complexity
- Can shift up (to rigorous) or down (to exploratory) on request
- Track mode shifts in session state
- Default to balanced after explicit shift ends

**Appropriate for**: Developers, consultants, general-purpose agents

### capability-governance-exploratory

Agents with exploratory governance:
- Prioritize conversational flow
- Apply structure only on explicit request
- Document post-session if valuable
- Cannot shift to higher governance

**Appropriate for**: Coaches, personal advisors, creative collaborators

---

## Theoretical Basis

PERSONA is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **BDI (Desires)** | North Star and goals represent agent's desires |
| **Actor Model** | Archetype defines actor role in system |
| **Cybernetics** | Governance intensity provides variety matching |
| **Extended Mind** | Identity artifacts extend agent cognition |

```yaml
theoretical_basis:
  primary: BDI (Belief-Desire-Intention)
  secondary:
    - Actor Model
    - Cybernetics (requisite variety)
  rationale: >
    PERSONA defines agent desires (BDI), role boundaries (Actor),
    and governance variety to match situational complexity (Cybernetics).
  reference: L331_theoretical_foundations_agency.md
```

---

## Validation

### Identity Validation

```bash
# Check identity artifacts exist
ls .aget/identity.json .aget/version.json
ls governance/CHARTER.md governance/MISSION.md

# Validate version.json structure
python3 -c "import json; v=json.load(open('.aget/version.json')); print(f\"Agent: {v.get('name')}\")"
```

### Governance Capability Check

```bash
# Verify governance capability declared
grep -E "capability-governance-(rigorous|balanced|exploratory)" manifest.yaml
```

---

## References

- L341: Governance Intensity Classification
- L331: Theoretical Foundations of Agency
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- COMPOSITION_SPEC_v1.0: Capability composition

---

## Graduation History

- **Source Learning**: L341 (Governance Intensity Classification)
- **Related Pattern**: Operational Mode section in AGENTS.md
- **Rationale**: Formalizes governance intensity from L341 into dimension spec

---

*AGET PERSONA Specification v1.0.0*
*Part of v3.0.0 Composition Architecture - PERSONA Dimension*
*"WHO the agent is shapes everything it does."*
