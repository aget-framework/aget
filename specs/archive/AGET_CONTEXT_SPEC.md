# AGET CONTEXT Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (5D Composition - CONTEXT Dimension)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_CONTEXT_SPEC.md`
**Change Proposal**: CP-013

---

## Abstract

This specification defines the CONTEXT dimension of the 5D Composition Architecture. CONTEXT encompasses WHERE and WHEN an agent operates: its Environmental_Awareness, Relationship_Structure, Temporal_State, and Scope_Boundaries. CONTEXT provides situational awareness that shapes agent behavior.

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
- Environmental_Awareness
- Relationship_Structure
- Temporal_Awareness
- Scope_Boundaries
- Context_Artifacts

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

## Vocabulary

Domain terms for the CONTEXT dimension:

```yaml
vocabulary:
  meta:
    domain: "context"
    version: "1.0.0"
    inherits: "aget_core"

  context:  # D5: WHERE/WHEN
    Environmental_Awareness:
      skos:definition: "Agent's understanding of its operating environment"
      aget:reference: "L185"
    Relationship_Structure:
      skos:definition: "Network of relationships defining agent's position"
      skos:narrower: ["Supervisor_Relationship", "Managed_Entity", "Peer_Relationship"]
    Supervisor_Relationship:
      skos:definition: "Governance oversight relationship"
      aget:annotation: "Managed By"
    Managed_Entity:
      skos:definition: "Entity the agent has authority over"
      aget:annotation: "Manages"
    Temporal_Awareness:
      skos:definition: "Agent's understanding of time and session state"
      skos:narrower: ["Session_State", "Workflow_Phase"]
    Session_State:
      skos:definition: "Current state within session lifecycle"
      skos:narrower: ["Fresh_Session", "Continued_Session", "Winding_Down"]
    Scope_Boundary:
      skos:definition: "Defined limits of agent authority and responsibility"
      aget:reference: "L342"
    Portfolio:
      skos:definition: "Organizational grouping of agents"

  persona:  # D1: Related identity terms
    Governance_Shift:
      skos:definition: "Change in governance intensity based on context"

  memory:  # D2: Stored artifacts
    Charter_Md:
      skos:definition: "Document defining agent scope and boundaries"
      aget:location: "governance/CHARTER.md"
    Scope_Boundaries_Md:
      skos:definition: "Document defining explicit limits"
      aget:location: "governance/SCOPE_BOUNDARIES.md"

  reasoning:  # D3: Related decision patterns
    Session_Scope_Check:
      skos:definition: "Protocol for validating work against session mandate"
      aget:reference: "L342"
    Environmental_Grounding:
      skos:definition: "Protocol for verifying environment before action"
      aget:reference: "L185"

  skills:  # D4: Related capabilities
    Wake_Protocol:
      skos:definition: "Session initialization gathering context"
    Wind_Down_Protocol:
      skos:definition: "Session finalization preserving context"
```

---

## Requirements

### CAP-CONTEXT-001: Environmental Awareness

The SYSTEM shall maintain awareness of its Operating_Environment.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-001-01 | ubiquitous | The SYSTEM shall verify Environment before proposing changes (L185) |
| CAP-CONTEXT-001-02 | event-driven | WHEN Operation is proposed, the SYSTEM shall check Git_Status |
| CAP-CONTEXT-001-03 | ubiquitous | The SYSTEM shall understand Repository_Structure |
| CAP-CONTEXT-001-04 | ubiquitous | The SYSTEM shall NOT assume File_Existence WITHOUT verification |

**Enforcement**: `validate_context_compliance.py`, operational review

#### Environmental Grounding Protocol (L185)

Before proposing changes:
1. `ls` the actual directory structure
2. Check Git_Status of managed repo
3. Verify Template_Consistency (if applicable)
4. Don't assume - investigate

### CAP-CONTEXT-002: Relationship Structure

The SYSTEM shall understand its Relationship_Context.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-002-01 | ubiquitous | The SYSTEM shall know its Supervisor (Managed_By) |
| CAP-CONTEXT-002-02 | ubiquitous | The SYSTEM shall know what it Manages |
| CAP-CONTEXT-002-03 | ubiquitous | The SYSTEM shall understand Escalation_Paths |
| CAP-CONTEXT-002-04 | ubiquitous | The SYSTEM shall document Relationship_Structure in Claude_Md |

**Enforcement**: `validate_context_compliance.py`, documentation review

#### Relationship Model

```
┌─────────────────────┐
│     Supervisor      │  Managed_By: Provides governance oversight
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     This Agent      │  Operational_Authority within scope
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Managed_Entities  │  Manages: Repos, templates, artifacts
└─────────────────────┘
```

#### Relationship Clarity (L342)

| Relationship | Meaning | Implication |
|--------------|---------|-------------|
| **Managed_By** (supervisor) | Organizational oversight | Approves major decisions |
| **Manages** (entities) | Artifact ownership | Creates plans, executes work |
| **Peers** | Coordination partners | Handoff and collaboration |

### CAP-CONTEXT-003: Temporal Awareness

The SYSTEM shall maintain Temporal_Context.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-003-01 | ubiquitous | The SYSTEM shall track Session_State |
| CAP-CONTEXT-003-02 | event-driven | WHEN Session_Boundary occurs, the SYSTEM shall recognize transition |
| CAP-CONTEXT-003-03 | ubiquitous | The SYSTEM shall understand current Workflow_Phase |
| CAP-CONTEXT-003-04 | conditional | IF Continued_Session THEN the SYSTEM shall load prior context |

**Enforcement**: Session protocol review

#### Session States

| State | Description | Behavior |
|-------|-------------|----------|
| Fresh_Session | New session, no prior context | Execute Wake_Protocol |
| Continued_Session | Resumed from previous | Load Session_Handoff context |
| Winding_Down | Session ending | Execute Wind_Down_Protocol |

### CAP-CONTEXT-004: Scope Boundaries

The SYSTEM shall respect Scope_Boundaries.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-004-01 | ubiquitous | The SYSTEM shall have documented Scope in Charter_Md |
| CAP-CONTEXT-004-02 | ubiquitous | The SYSTEM shall recognize In_Scope vs. Out_Of_Scope work |
| CAP-CONTEXT-004-03 | ubiquitous | The SYSTEM shall NOT exceed Session_Mandate (L342) |
| CAP-CONTEXT-004-04 | conditional | IF Scope_Change is proposed THEN the SYSTEM shall require explicit Approval |
| CAP-CONTEXT-004-05 | conditional | IF Scope evolved 3+ times THEN the SYSTEM shall STOP and create Session_Handoff |

**Enforcement**: Scope review, session validation

#### Scope Boundary Document

```markdown
## What This Agent IS

- [In_Scope activities]

## What This Agent IS NOT

- [Out_Of_Scope activities]

## Boundaries

- [Explicit limits]
```

### CAP-CONTEXT-005: Context Documentation

The SYSTEM shall document its Context.

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-CONTEXT-005-01 | ubiquitous | The SYSTEM shall document Supervisor_Relationship | CLAUDE.md |
| CAP-CONTEXT-005-02 | ubiquitous | The SYSTEM shall document Managed_Entities | CLAUDE.md |
| CAP-CONTEXT-005-03 | ubiquitous | The SYSTEM shall document Scope_Boundaries | governance/CHARTER.md |
| CAP-CONTEXT-005-04 | ubiquitous | The SYSTEM shall document Portfolio membership | .aget/version.json |

**Enforcement**: `validate_context_compliance.py`

### CAP-CONTEXT-006: Context-Driven Adaptation

The SYSTEM shall adapt behavior based on Context.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-006-01 | conditional | IF Public_Repo_Work THEN the SYSTEM shall apply Higher_Governance (L340) |
| CAP-CONTEXT-006-02 | conditional | IF Breaking_Change THEN the SYSTEM shall require Escalation |
| CAP-CONTEXT-006-03 | conditional | IF Novel_Territory THEN the SYSTEM shall apply Rigorous_Mode |
| CAP-CONTEXT-006-04 | event-driven | WHEN Environmental_Change occurs, the SYSTEM shall re-evaluate Context |

**Enforcement**: Operational review

---

## Context Awareness Protocols

### Wake Protocol Context

```bash
# Context to gather on wake
1. Load Identity (.aget/version.json)
2. Check Environment (git status, pwd)
3. Load Pending_Work (planning/)
4. Display Summary
```

### Session Scope Check (L342)

Before significant Scope_Expansion:
1. Re-read Session_Mandate
2. Classify proposed work: Research | Preparation | Execution
3. If execution beyond mandate: Create Session_Handoff, defer

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

Environment may invoke Governance_Shifts:
- Public_Repo work → Higher_Governance (L340)
- Breaking_Changes → Escalation required
- Novel_Territory → Rigorous_Mode

### CONTEXT → REASONING

Context informs Reasoning approach:
- Continued_Session → Load prior context
- Fresh_Session → Full Wake_Protocol
- Scope_Boundary → Limit planning scope

### CONTEXT → SKILLS

Context determines which Skills apply:
- Local_Repo → Full Tool_Access
- Remote_Context → Limited Tools
- Phase_Alignment → Relevant Capabilities

---

## Authority Model

```yaml
authority:
  applies_to: "all_agents"

  governed_by:
    spec: "AGET_CONTEXT_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "check and document Environment"
      - "execute Wake_Protocol and Wind_Down_Protocol"
      - "track Session_State"
      - "recognize Scope_Boundaries"

    requires_approval:
      - action: "Scope_Expansion beyond Session_Mandate"
        approver: "principal"
      - action: "Modify Scope_Boundaries in Charter_Md"
        approver: "supervisor"

  relationship_authority:
    - action: "Change Supervisor_Relationship"
      approver: "current supervisor"
    - action: "Add Managed_Entity"
      approver: "supervisor"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-CONTEXT-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT exceed Session_Mandate WITHOUT approval (L342)"
      rationale: "Session scope discipline is foundational"

    - id: "INV-CONTEXT-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT assume Environment WITHOUT verification (L185)"
      rationale: "Environmental grounding prevents assumption errors"

    - id: "INV-CONTEXT-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT ignore Supervisor_Relationship for major decisions"
      rationale: "Governance structure must be respected"

    - id: "INV-CONTEXT-004"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT operate outside documented Scope_Boundaries"
      rationale: "Scope discipline enables coordination"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "governance/"
      purpose: "Governance and scope documentation"
      contents:
        - "CHARTER.md"
        - "MISSION.md"

  required_files:
    - path: "governance/CHARTER.md"
      purpose: "Scope definition"
      sections:
        - "What This Agent IS"
        - "What This Agent IS NOT"

    - path: "CLAUDE.md"
      purpose: "Operational instructions including relationship structure"
      sections:
        - "Agent Identity"
        - "Managed By"
        - "Manages"

    - path: ".aget/version.json"
      purpose: "Identity including portfolio membership"
      fields:
        - "portfolio"

  optional_files:
    - path: "governance/SCOPE_BOUNDARIES.md"
      purpose: "Detailed scope boundaries"
```

---

## Validation

### Context Awareness Check

```bash
# Verify Relationship_Documentation
grep -E "Managed By|Manages" CLAUDE.md

# Verify Scope_Documentation
ls governance/CHARTER.md governance/SCOPE_BOUNDARIES.md

# Verify Portfolio in Version_Json
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
  primary: "Actor Model"
  secondary:
    - "Cybernetics (environmental feedback)"
    - "Situated Cognition"
    - "Extended Mind"
  rationale: >
    CONTEXT defines Actor boundaries and encapsulation.
    Environmental feedback (Cybernetics) shapes behavior.
    Cognition is situated in context (Situated Cognition).
    Environment extends cognitive capability (Extended Mind).
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

- L185: Environmental Grounding
- L342: Session Scope Validation
- L340: Execution Governance Artifact Requirement
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- AGET_SPEC_FORMAT_v1.2: Specification format
- governance/CHARTER.md: Scope definition

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L185", "L342", "L340"]
  pattern_origin: "Wake/Wind-down protocols"
  rationale: "Formalizes context awareness from operational learnings"
```

---

*AGET CONTEXT Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture - CONTEXT Dimension*
*"WHERE and WHEN shape what is possible."*
