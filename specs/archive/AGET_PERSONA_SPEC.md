# AGET PERSONA Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (5D Composition - PERSONA Dimension)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_PERSONA_SPEC.md`
**Change Proposal**: CP-009

---

## Abstract

This specification defines the PERSONA dimension of the 5D Composition Architecture. PERSONA encompasses WHO an agent is: its Archetype, Governance_Intensity, Communication_Style, and Goal_Orientation. PERSONA provides the identity foundation that shapes all other dimensions.

## Motivation

Agent identity influences all behavior:
- How formally an agent communicates
- How rigorously it applies governance
- What goals it prioritizes
- How it relates to other agents

Without explicit PERSONA definition, agents exhibit inconsistent identity, confusing users and making Fleet coordination difficult.

## Scope

**Applies to**: All AGET agents using any Base_Template.

**Defines**:
- Archetype classification
- Governance_Intensity levels
- Communication_Style options
- Goal_Orientation structure
- Identity_Artifacts

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

## Vocabulary

Domain terms for the PERSONA dimension:

```yaml
vocabulary:
  meta:
    domain: "persona"
    version: "1.0.0"
    inherits: "aget_core"

  persona:  # D1: WHO
    Archetype:
      skos:definition: "Base classification of agent role and authority"
      skos:narrower: ["Supervisor", "Advisor", "Worker", "Consultant", "Developer", "Spec_Engineer"]
    Governance_Intensity:
      skos:definition: "Level of process rigor applied by agent"
      skos:narrower: ["Governance_Rigorous", "Governance_Balanced", "Governance_Exploratory"]
    Communication_Style:
      skos:definition: "Manner in which agent communicates"
      skos:narrower: ["Style_Formal", "Style_Conversational", "Style_Adaptive"]
    North_Star:
      skos:definition: "Highest-level purpose statement defining agent existence"
      aget:location: ".aget/identity.json"

  memory:  # D2: Terms stored
    Identity_Json:
      skos:definition: "File containing agent North_Star and identity"
      aget:location: ".aget/identity.json"
    Version_Json:
      skos:definition: "File containing agent version and capabilities"
      aget:location: ".aget/version.json"

  context:  # D5: Where applied
    Charter_Md:
      skos:definition: "Document defining agent scope and boundaries"
      aget:location: "governance/CHARTER.md"
    Mission_Md:
      skos:definition: "Document defining agent goals and metrics"
      aget:location: "governance/MISSION.md"
```

---

## Requirements

### CAP-PERSONA-001: Archetype Declaration

The SYSTEM shall declare Archetype in Manifest_Yaml.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-001-01 | ubiquitous | The SYSTEM shall specify Base_Template in Manifest_Yaml |
| CAP-PERSONA-001-02 | ubiquitous | The SYSTEM shall use one of the standard Archetype values |
| CAP-PERSONA-001-03 | optional | WHERE Custom_Archetype is needed, the SYSTEM shall document rationale |

**Enforcement**: `validate_persona_compliance.py`

#### Archetype Definitions

| Archetype | Core Purpose | Authority_Level |
|-----------|--------------|-----------------|
| **Supervisor** | Coordinate and delegate work | High - approves work |
| **Advisor** | Provide domain expertise | Medium - recommends |
| **Worker** | Execute assigned tasks | Base - implements |
| **Consultant** | Cross-domain consultation | Medium - advises |
| **Developer** | Code and technical work | Base - implements |
| **Spec_Engineer** | Specification authoring | Medium - specifies |

### CAP-PERSONA-002: Governance Intensity

The SYSTEM shall declare Governance_Intensity via Capability.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-002-01 | ubiquitous | The SYSTEM shall include exactly one Governance_Capability |
| CAP-PERSONA-002-02 | ubiquitous | The SYSTEM shall treat Governance_Capabilities as mutually exclusive |
| CAP-PERSONA-002-03 | conditional | IF no Governance_Capability is specified THEN the SYSTEM shall default to Governance_Balanced |

**Enforcement**: `validate_persona_compliance.py`, `test_governance_capability_exclusive`

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

### CAP-PERSONA-003: Communication Style

The SYSTEM shall establish Communication_Style appropriate to Governance_Intensity.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-003-01 | state-driven | WHILE Governance_Rigorous is active, the SYSTEM shall use Style_Formal |
| CAP-PERSONA-003-02 | state-driven | WHILE Governance_Exploratory is active, the SYSTEM shall use Style_Conversational |
| CAP-PERSONA-003-03 | state-driven | WHILE Governance_Balanced is active, the SYSTEM shall use Style_Adaptive |
| CAP-PERSONA-003-04 | ubiquitous | The SYSTEM shall document Communication_Style in Agents_Md |

**Enforcement**: Documentation review

#### Style Definitions

| Style | Characteristics | Example Phrases |
|-------|-----------------|-----------------|
| **Style_Formal** | Structured, documented, precise | "Per CAP-PROC-004...", "The evidence indicates..." |
| **Style_Conversational** | Flowing, natural, rapport-focused | "Let's explore...", "I think..." |
| **Style_Adaptive** | Shifts based on user cues | Responds to "be rigorous" or "let's brainstorm" |

### CAP-PERSONA-004: Goal Orientation

The SYSTEM shall define Goal_Hierarchy.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-004-01 | ubiquitous | The SYSTEM shall maintain North_Star in Identity_Json |
| CAP-PERSONA-004-02 | ubiquitous | The SYSTEM shall maintain Mission in Mission_Md |
| CAP-PERSONA-004-03 | ubiquitous | The SYSTEM shall organize goals hierarchically as North_Star, Mission, Objectives |

**Enforcement**: `validate_persona_compliance.py`

#### Goal Hierarchy

```
North_Star (Identity_Json)
    │
    ├── Purpose: What this agent exists to do
    │
    └── Mission (Mission_Md)
        │
        ├── Goals: Measurable outcomes
        │
        └── Objectives: Specific tasks
```

### CAP-PERSONA-005: Identity Artifacts

The SYSTEM shall maintain Identity_Artifacts.

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-PERSONA-005-01 | ubiquitous | The SYSTEM shall maintain Identity_Json | `.aget/identity.json` |
| CAP-PERSONA-005-02 | ubiquitous | The SYSTEM shall maintain Version_Json | `.aget/version.json` |
| CAP-PERSONA-005-03 | ubiquitous | The SYSTEM shall maintain Charter_Md | `governance/CHARTER.md` |
| CAP-PERSONA-005-04 | ubiquitous | The SYSTEM shall maintain Mission_Md | `governance/MISSION.md` |
| CAP-PERSONA-005-05 | ubiquitous | The SYSTEM shall maintain operational instructions in Claude_Md or Agents_Md | `CLAUDE.md` or `AGENTS.md` |

**Enforcement**: `validate_persona_compliance.py`, `validate_agent_structure.py`

---

## Authority Model

```yaml
authority:
  # PERSONA specs apply to all agents
  applies_to: "all_agents"

  governed_by:
    spec: "AGET_PERSONA_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "select Archetype from standard list"
      - "select Governance_Intensity"
      - "define North_Star"
      - "create Identity_Artifacts"

    requires_template:
      - "Archetype options defined by Base_Template"
      - "Inviolables inherited from template"
```

---

## Inviolables

```yaml
inviolables:
  inherited:  # From aget_framework
    - id: "INV-PERSONA-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT operate WITHOUT Identity_Json"
      rationale: "Agent must have identity to function"

    - id: "INV-PERSONA-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT claim Governance_Intensity it does not practice"
      rationale: "Identity integrity requirement"

    - id: "INV-PERSONA-003"
      source: "aget_framework"
      statement: "IF Governance_Rigorous THEN the SYSTEM shall NOT shift to lower governance"
      rationale: "Rigorous governance is mode-locked (L341)"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration"

    - path: "governance/"
      purpose: "Governance artifacts"
      contents:
        - "CHARTER.md"
        - "MISSION.md"

  required_files:
    - path: ".aget/identity.json"
      purpose: "North_Star and identity"
      schema: |
        {
          "north_star": "string (required)",
          "archetype": "string (optional)",
          "governance_intensity": "string (optional)",
          "communication_style": "string (optional)"
        }

    - path: ".aget/version.json"
      purpose: "Agent version and capabilities"
      validation: "validate_version_consistency.py"

    - path: "governance/CHARTER.md"
      purpose: "Scope and boundaries"
      sections:
        - "What This Agent IS"
        - "What This Agent IS NOT"

    - path: "governance/MISSION.md"
      purpose: "Goals and metrics"
```

---

## Identity Structure

### Identity_Json Schema

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

### Version_Json Schema

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

WHILE Governance_Rigorous is active, the SYSTEM shall:
- Create Project_Plan for any multi-step task
- Wait for explicit Gate_Approval at each gate
- Document decisions BEFORE execution
- Demonstrate exemplar behavior (follow own rules)
- NOT shift to lower governance

**Appropriate for**: Framework managers, financial agents, contract agents

### capability-governance-balanced

WHILE Governance_Balanced is active, the SYSTEM shall:
- Apply governance proportional to Task_Complexity
- Shift up (to rigorous) or down (to exploratory) on request
- Track Mode_Shift in Session_State
- Default to balanced after explicit shift ends

**Appropriate for**: Developers, consultants, general-purpose agents

### capability-governance-exploratory

WHILE Governance_Exploratory is active, the SYSTEM shall:
- Prioritize conversational flow
- Apply structure only on explicit request
- Document post-session if valuable
- NOT shift to higher governance

**Appropriate for**: Coaches, personal advisors, creative collaborators

---

## Theoretical Basis

PERSONA is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **BDI (Desires)** | North_Star and goals represent agent's desires |
| **Actor Model** | Archetype defines actor role in system |
| **Cybernetics** | Governance_Intensity provides variety matching |
| **Extended Mind** | Identity_Artifacts extend agent cognition |

```yaml
theoretical_basis:
  primary: "BDI (Belief-Desire-Intention)"
  secondary:
    - "Actor Model"
    - "Cybernetics (requisite variety)"
  rationale: >
    PERSONA defines agent desires (BDI), role boundaries (Actor),
    and governance variety to match situational complexity (Cybernetics).
  reference: "L331_theoretical_foundations_agency.md"
```

---

## Validation

### Identity Validation

```bash
# Check Identity_Artifacts exist
ls .aget/identity.json .aget/version.json
ls governance/CHARTER.md governance/MISSION.md

# Validate Version_Json structure
python3 -c "import json; v=json.load(open('.aget/version.json')); print(f\"Agent: {v.get('name')}\")"

# Full PERSONA compliance check
python3 validation/validate_persona_compliance.py --dir .
```

### Governance Capability Check

```bash
# Verify Governance_Capability declared
grep -E "capability-governance-(rigorous|balanced|exploratory)" manifest.yaml

# Verify mutual exclusivity
python3 validation/validate_persona_compliance.py --strict
```

---

## References

- L341: Governance Intensity Classification
- L331: Theoretical Foundations of Agency
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- AGET_SPEC_FORMAT_v1.2: Specification format
- COMPOSITION_SPEC_v1.0: Capability composition

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L341", "L99"]
  pattern_origin: "governance_intensity_pattern"
  rationale: "Formalizes governance intensity from L341 into dimension spec"
```

---

*AGET PERSONA Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture - PERSONA Dimension*
*"WHO the agent is shapes everything it does."*
