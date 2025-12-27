# AGET CONTEXT Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (5D Composition - CONTEXT Dimension)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_CONTEXT_SPEC.md`
**Change Proposal**: CP-013

---

## Abstract

This specification defines the CONTEXT dimension of the 5D Composition Architecture. CONTEXT encompasses WHERE and WHEN an agent operates: its environmental awareness, relationships, temporal state, and scope boundaries. CONTEXT provides situational awareness that shapes agent behavior.

## Motivation

Agent context determines appropriate behavior:
- What environment the agent operates in
- Who the agent works with and for
- What phase of work is active
- What is and isn't in scope

Without explicit CONTEXT awareness, agents make inappropriate assumptions, violate boundaries, and fail to adapt to situational needs.

## Scope

**Applies to**: All AGET agents.

**Defines**:
- Environmental awareness
- Relationship structure
- Temporal awareness
- Scope boundaries
- Context artifacts

---

## The 5D Composition Context

CONTEXT is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | AGET_PERSONA_SPEC |
| MEMORY | Knowledge persistence, learning accumulation | AGET_MEMORY_SPEC |
| REASONING | Decision patterns, problem-solving approach | AGET_REASONING_SPEC |
| SKILLS | Specific capabilities, tools, integrations | AGET_SKILLS_SPEC |
| **CONTEXT** | Environmental awareness, situation adaptation | **This document** |

---

## Requirements

### R-CONTEXT-001: Environmental Awareness

Agents SHALL maintain awareness of their operating environment.

| ID | Requirement |
|----|-------------|
| R-CONTEXT-001-01 | Agent SHALL verify environment before proposing changes (L185) |
| R-CONTEXT-001-02 | Agent SHALL check git status before operations |
| R-CONTEXT-001-03 | Agent SHALL understand repository structure |
| R-CONTEXT-001-04 | Agent SHALL NOT assume file existence without verification |

#### Environmental Grounding Protocol (L185)

Before proposing changes:
1. `ls` the actual directory structure
2. Check git status of managed repo
3. Verify template consistency (if applicable)
4. Don't assume - investigate

### R-CONTEXT-002: Relationship Structure

Agents SHALL understand their relationship context.

| ID | Requirement |
|----|-------------|
| R-CONTEXT-002-01 | Agent SHALL know its supervisor (Managed By) |
| R-CONTEXT-002-02 | Agent SHALL know what it manages (Manages) |
| R-CONTEXT-002-03 | Agent SHALL understand escalation paths |
| R-CONTEXT-002-04 | Relationship structure SHALL be documented in CLAUDE.md |

#### Relationship Model

```
┌─────────────────────┐
│     Supervisor      │  Managed By: Provides governance oversight
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     This Agent      │  Operational authority within scope
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Managed Entities  │  Manages: Repos, templates, artifacts
└─────────────────────┘
```

#### Relationship Clarity (L342)

| Relationship | Meaning | Implication |
|--------------|---------|-------------|
| **Managed By** (supervisor) | Organizational oversight | Approves major decisions |
| **Manages** (entities) | Artifact ownership | Creates plans, executes work |
| **Peers** | Coordination partners | Handoff and collaboration |

### R-CONTEXT-003: Temporal Awareness

Agents SHALL maintain temporal context.

| ID | Requirement |
|----|-------------|
| R-CONTEXT-003-01 | Agent SHALL track session state |
| R-CONTEXT-003-02 | Agent SHALL recognize session boundaries |
| R-CONTEXT-003-03 | Agent SHALL understand current workflow phase |
| R-CONTEXT-003-04 | Agent SHALL recognize continuation vs. fresh sessions |

#### Session States

| State | Description | Behavior |
|-------|-------------|----------|
| Fresh | New session, no prior context | Execute wake protocol |
| Continued | Resumed from previous | Load handoff context |
| Winding down | Session ending | Execute wind-down protocol |

### R-CONTEXT-004: Scope Boundaries

Agents SHALL respect scope boundaries.

| ID | Requirement |
|----|-------------|
| R-CONTEXT-004-01 | Agent SHALL have documented scope in CHARTER.md |
| R-CONTEXT-004-02 | Agent SHALL recognize in-scope vs. out-of-scope work |
| R-CONTEXT-004-03 | Agent SHALL NOT exceed session mandate (L342) |
| R-CONTEXT-004-04 | Scope changes SHALL require explicit approval |

#### Scope Boundary Document

```markdown
## What This Agent IS

- [In-scope activities]

## What This Agent IS NOT

- [Out-of-scope activities]

## Boundaries

- [Explicit limits]
```

### R-CONTEXT-005: Context Documentation

Agents SHALL document their context.

| ID | Requirement | Location |
|----|-------------|----------|
| R-CONTEXT-005-01 | Supervisor relationship | CLAUDE.md |
| R-CONTEXT-005-02 | Managed entities | CLAUDE.md |
| R-CONTEXT-005-03 | Scope boundaries | governance/CHARTER.md |
| R-CONTEXT-005-04 | Portfolio membership | .aget/version.json |

---

## Context Awareness Protocols

### Wake Protocol Context

```bash
# Context to gather on wake
1. Load identity (.aget/version.json)
2. Check environment (git status, pwd)
3. Load pending work (planning/)
4. Display summary
```

### Session Scope Check (L342)

Before significant scope expansion:
1. Re-read session mandate
2. Classify proposed work: Research | Preparation | Execution
3. If execution beyond mandate: Create handoff, defer

**Response to scope drift**: "This informs a future session, not this one."

### Environmental Grounding (L185)

Before proposing changes:
1. Verify target exists
2. Check current state
3. Understand dependencies
4. Don't assume - investigate

---

## Context Interaction with Other Dimensions

### CONTEXT → PERSONA

Environment may invoke governance shifts:
- Public repo work → Higher governance (L340)
- Breaking changes → Escalation required
- Novel territory → Rigorous mode

### CONTEXT → REASONING

Context informs reasoning approach:
- Continuation session → Load prior context
- Fresh session → Full wake protocol
- Scope boundary → Limit planning scope

### CONTEXT → SKILLS

Context determines which skills apply:
- Local repo → Full tool access
- Remote context → Limited tools
- Phase alignment → Relevant capabilities

---

## Theoretical Basis

CONTEXT is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **Actor Model** | Context defines actor boundaries |
| **Cybernetics** | Environmental feedback shapes behavior |
| **Situated Cognition** | Context shapes available actions |
| **Extended Mind** | Environment is part of cognitive system |

```yaml
theoretical_basis:
  primary: Actor Model
  secondary:
    - Cybernetics (environmental feedback)
    - Situated Cognition
    - Extended Mind
  rationale: >
    CONTEXT defines Actor boundaries and encapsulation.
    Environmental feedback (Cybernetics) shapes behavior.
    Cognition is situated in context (Situated Cognition).
    Environment extends cognitive capability (Extended Mind).
  reference: L331_theoretical_foundations_agency.md
```

---

## Validation

### Context Awareness Check

```bash
# Verify relationship documentation
grep -E "Managed By|Manages" CLAUDE.md

# Verify scope documentation
ls governance/CHARTER.md governance/SCOPE_BOUNDARIES.md

# Verify portfolio in version.json
python3 -c "import json; v=json.load(open('.aget/version.json')); print(f\"Portfolio: {v.get('portfolio', 'unset')}\")"
```

### Environmental Grounding

```bash
# Before any operation, verify state
git status
pwd
ls -la target/path/
```

---

## References

- L185: Environmental Grounding
- L342: Session Scope Validation
- L340: Execution Governance Artifact Requirement
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- governance/CHARTER.md: Scope definition

---

## Graduation History

- **Source Learnings**: L185 (Environmental Grounding), L342 (Session Scope)
- **Related Pattern**: Wake/Wind-down protocols
- **Rationale**: Formalizes context awareness from operational learnings

---

*AGET CONTEXT Specification v1.0.0*
*Part of v3.0.0 Composition Architecture - CONTEXT Dimension*
*"WHERE and WHEN shape what is possible."*
