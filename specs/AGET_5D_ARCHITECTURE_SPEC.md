# AGET 5D Composition Architecture Specification

**Version**: 1.2.0
**Status**: Active
**Category**: Standards (Umbrella)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_5D_ARCHITECTURE_SPEC.md`
**Change Proposal**: CP-008
**Change Origin**: L394 (Design by Fleet Exploration)

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
- Integration with Capability_Composition
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
│      • Governance_Intensity (rigorous, balanced, exploratory)          │
│      • Communication_Style (formal, conversational, adaptive)          │
│      • Goal_Orientation (North_Star, Mission, Objectives)              │
│                                                                         │
│  D2: MEMORY ───────────────────────────────────── WHAT KNOWS           │
│      • Six_Layer_Memory_Model (working → fleet)                        │
│      • Continual_Learning (L-doc → Pattern → Spec)                     │
│      • Session_Protocol (wake, wind-down)                              │
│      • Knowledge_Persistence (KB as Collaboration_Substrate)           │
│                                                                         │
│  D3: REASONING ────────────────────────────────── HOW THINKS           │
│      • Planning_Patterns (PROJECT_PLAN, gates)                         │
│      • Decision_Frameworks (escalation, Authority_Matrix)              │
│      • Reflection_Protocols (step back, review KB)                     │
│      • Quality_Assurance (Verification_Tests, validation)              │
│                                                                         │
│  D4: SKILLS ───────────────────────────────────── WHAT DOES            │
│      • Capabilities (composable behavioral units)                      │
│      • Tools (Validators, scripts, patterns)                           │
│      • Outputs (structured formats, artifacts)                         │
│      • A_SDLC Phase_Alignment                                          │
│                                                                         │
│  D5: CONTEXT ──────────────────────────────────── WHERE/WHEN           │
│      • Environmental_Awareness (codebase, repository state)            │
│      • Relationships (Supervisor, Peers, Managed_Agents)               │
│      • Temporal_Awareness (Session_State, Workflow_Phase)              │
│      • Scope_Boundaries (what is/isn't in scope)                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Vocabulary

Core terms for the 5D Architecture:

```yaml
vocabulary:
  meta:
    domain: "5d_architecture"
    version: "1.0.0"
    inherits: "aget_core"

  architecture:  # Cross-cutting terms
    Five_D_Model:
      skos:definition: "Framework organizing agent design into five orthogonal dimensions"
      skos:narrower: ["PERSONA", "MEMORY", "REASONING", "SKILLS", "CONTEXT"]
    Dimension:
      skos:definition: "Orthogonal aspect of agent design"
    Dimension_Completeness:
      skos:definition: "Requirement that agents address all five dimensions"
    Dimension_Orthogonality:
      skos:definition: "Property that dimensions are independent and compose without interference"
    Capability_Composition:
      skos:definition: "Mechanism for combining capabilities into agent behavior"
      aget:reference: "COMPOSITION_SPEC_v1.0"

  persona:  # D1: WHO
    PERSONA:
      skos:definition: "D1 - Identity dimension defining WHO the agent is"
      skos:narrower: ["Archetype", "Governance_Intensity", "Communication_Style", "Goal_Orientation"]

  memory:  # D2: WHAT KNOWS
    MEMORY:
      skos:definition: "D2 - Knowledge dimension defining WHAT the agent knows"
      skos:narrower: ["Six_Layer_Memory_Model", "Continual_Learning", "Session_Protocol"]

  reasoning:  # D3: HOW THINKS
    REASONING:
      skos:definition: "D3 - Cognitive dimension defining HOW the agent thinks"
      skos:narrower: ["Planning_Pattern", "Decision_Framework", "Reflection_Protocol", "Quality_Assurance"]

  skills:  # D4: WHAT DOES
    SKILLS:
      skos:definition: "D4 - Capability dimension defining WHAT the agent does"
      skos:narrower: ["Capability", "Tool", "Output_Format", "Phase_Alignment"]

  context:  # D5: WHERE/WHEN
    CONTEXT:
      skos:definition: "D5 - Situational dimension defining WHERE/WHEN the agent operates"
      skos:narrower: ["Environmental_Awareness", "Relationship_Structure", "Temporal_Awareness", "Scope_Boundary"]
```

---

## Requirements

### CAP-5D-001: Dimension Completeness

The SYSTEM shall address all five dimensions in agent design.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-5D-001-01 | ubiquitous | The SYSTEM shall have defined PERSONA (Archetype + Governance_Intensity) |
| CAP-5D-001-02 | ubiquitous | The SYSTEM shall have MEMORY structure (.aget/evolution, governance, planning) |
| CAP-5D-001-03 | ubiquitous | The SYSTEM shall follow REASONING patterns appropriate to Governance_Intensity |
| CAP-5D-001-04 | ubiquitous | The SYSTEM shall declare SKILLS via Capabilities or Manifest_Yaml |
| CAP-5D-001-05 | ubiquitous | The SYSTEM shall have CONTEXT awareness (Scope_Boundaries, Relationships) |

**Enforcement**: `validate_5d_compliance.py`

### CAP-5D-002: Dimension Orthogonality

Dimensions SHALL be independent and compose without interference.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-5D-002-01 | ubiquitous | The SYSTEM shall ensure PERSONA choices do NOT constrain MEMORY structure |
| CAP-5D-002-02 | ubiquitous | The SYSTEM shall ensure SKILLS compose independently of REASONING patterns |
| CAP-5D-002-03 | ubiquitous | The SYSTEM shall ensure CONTEXT awareness does NOT override PERSONA identity |
| CAP-5D-002-04 | ubiquitous | The SYSTEM shall make Dimension configurations separately testable |

**Enforcement**: Architecture review, dimension validators

### CAP-5D-003: Dimension Documentation

The SYSTEM shall document its 5D configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-5D-003-01 | ubiquitous | The SYSTEM shall include Dimension_Summary section in Agents_Md |
| CAP-5D-003-02 | ubiquitous | The SYSTEM shall declare Capabilities (SKILLS dimension) in Manifest_Yaml |
| CAP-5D-003-03 | ubiquitous | The SYSTEM shall declare PERSONA elements in Identity_Json |
| CAP-5D-003-04 | ubiquitous | The SYSTEM shall operationalize Dimension requirements in Claude_Md |

**Enforcement**: `validate_5d_compliance.py`, documentation review

### CAP-5D-004: Dimension Interaction

The SYSTEM shall support appropriate Dimension_Interactions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-5D-004-01 | conditional | IF Governance_Rigorous is active THEN the SYSTEM shall apply full REASONING protocols |
| CAP-5D-004-02 | ubiquitous | The SYSTEM shall use MEMORY to inform CONTEXT awareness |
| CAP-5D-004-03 | ubiquitous | The SYSTEM shall use SKILLS availability to shape REASONING approach |
| CAP-5D-004-04 | conditional | IF CONTEXT changes significantly THEN the SYSTEM may invoke PERSONA Governance_Shift |

**Enforcement**: Operational review

### CAP-5D-005: Dimension Extensions

The SYSTEM shall support Dimension_Extensions beyond the core 5D.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-5D-005-01 | optional | WHERE agent complexity requires, the SYSTEM may add D6+ dimensions |
| CAP-5D-005-02 | ubiquitous | The SYSTEM shall name extension dimensions as D6_{domain}, D7_{domain}, etc. |
| CAP-5D-005-03 | ubiquitous | The SYSTEM shall place extension dimension config in .aget/D6_{domain}/ |
| CAP-5D-005-04 | ubiquitous | The SYSTEM shall document extension dimensions in manifest.yaml |
| CAP-5D-005-05 | ubiquitous | The SYSTEM shall ensure extension dimensions maintain Dimension_Orthogonality |

**Enforcement**: Architecture review, manifest validation

**Rationale**: Fleet exploration (L394) revealed that complex agents (e.g., supervisors with 35+ .aget/ subdirs) require organizational structures beyond the core 5D. Extensions enable scaling without violating core architecture.

#### Extension Dimension Examples

| Extension | Purpose | Used By |
|-----------|---------|---------|
| D6_fleet | Fleet management, portfolio tracking | Supervisors |
| D6_coordination | Multi-agent coordination | Supervisors |
| D6_compliance | Compliance state, audit trails | Rigorous agents |
| D6_intelligence | Advanced reasoning, ML state | Intelligence-enabled agents |

#### Extension Structure

```
.aget/
├── persona/          # D1 (core)
├── memory/           # D2 (core)
├── reasoning/        # D3 (core)
├── skills/           # D4 (core)
├── context/          # D5 (core)
│
├── D6_fleet/         # D6 Extension: Fleet management
│   ├── portfolios.yaml
│   ├── agents.yaml
│   └── coordination.yaml
│
├── D7_compliance/    # D7 Extension: Compliance
│   ├── audit_trail.yaml
│   └── checkpoints/
│
└── ...               # Additional extensions as needed
```

#### Extension Declaration

```yaml
# manifest.yaml
composition:
  # Core 5D
  persona: ...
  memory: ...
  reasoning: ...
  skills: ...
  context: ...

  # Extensions
  extensions:
    - dimension: D6_fleet
      purpose: "Fleet management and portfolio tracking"
      config: $ref: .aget/D6_fleet/
    - dimension: D7_compliance
      purpose: "Compliance state and audit trails"
      config: $ref: .aget/D7_compliance/
```

---

## Dimension Specifications

Each dimension has a dedicated specification defining detailed requirements:

| Dimension | Specification | Version | Status |
|-----------|---------------|---------|--------|
| D1: PERSONA | AGET_PERSONA_SPEC.md | 1.1.0 | Active |
| D2: MEMORY | AGET_MEMORY_SPEC.md | 1.1.0 | Active |
| D3: REASONING | AGET_REASONING_SPEC.md | 1.1.0 | Active |
| D4: SKILLS | AGET_SKILLS_SPEC.md | 1.1.0 | Active |
| D5: CONTEXT | AGET_CONTEXT_SPEC.md | 1.1.0 | Active |

---

## Relationship to Capability Composition

The 5D Architecture and Capability_Composition (COMPOSITION_SPEC_v1.0) are **orthogonal but complementary**:

| Concern | Five_D_Architecture | Capability_Composition |
|---------|---------------------|------------------------|
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
  - capability-governance-rigorous    # Governance_Intensity

  # MEMORY dimension
  - capability-memory-management      # Six_Layer_Model

  # REASONING dimension
  - capability-gate-discipline        # Planning_Patterns

  # SKILLS dimension
  - capability-domain-knowledge       # Domain expertise
  - capability-structured-outputs     # Output_Formats

  # CONTEXT dimension
  - capability-collaboration          # Relationship_Awareness
```

---

## Dimension Interaction Patterns

WHILE dimensions are orthogonal, they interact at agent runtime:

### Pattern 1: PERSONA → REASONING

Governance_Intensity influences REASONING patterns:
- Governance_Rigorous → Full PROJECT_PLAN for all non-trivial work
- Governance_Balanced → Proportional governance
- Governance_Exploratory → Flow-first, structure on request

### Pattern 2: MEMORY → CONTEXT

MEMORY provides context for decisions:
- KB_Review informs contextual awareness
- Session_History provides Temporal_Context
- Learning_Documents inform current work

### Pattern 3: SKILLS → REASONING

Available SKILLS influence planning:
- Validator skills enable Verification_Tests
- Pattern_Scripts enable automation
- Tool_Availability shapes execution approach

### Pattern 4: CONTEXT → PERSONA

Environment may invoke Governance_Shifts:
- Public_Repo work → Higher_Governance (L340)
- Breaking_Changes → Escalation required
- Novel_Territory → Rigorous_Mode

---

## Authority Model

```yaml
authority:
  applies_to: "all_agents"

  governed_by:
    spec: "AGET_5D_ARCHITECTURE_SPEC"
    owner: "private-aget-framework-AGET"

  dimension_authority:
    D1_PERSONA:
      spec: "AGET_PERSONA_SPEC"
      owner: "private-aget-framework-AGET"
    D2_MEMORY:
      spec: "AGET_MEMORY_SPEC"
      owner: "private-aget-framework-AGET"
    D3_REASONING:
      spec: "AGET_REASONING_SPEC"
      owner: "private-aget-framework-AGET"
    D4_SKILLS:
      spec: "AGET_SKILLS_SPEC"
      owner: "private-aget-framework-AGET"
    D5_CONTEXT:
      spec: "AGET_CONTEXT_SPEC"
      owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "implement all five dimensions"
      - "configure dimension settings within constraints"
      - "document 5D configuration"

    requires_template:
      - "Base dimension configuration from template"
      - "Inviolables inherited from template"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-5D-001"
      source: "aget_framework"
      statement: "The SYSTEM shall address all five dimensions"
      rationale: "5D completeness is foundational to agent design"

    - id: "INV-5D-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT violate Dimension_Orthogonality"
      rationale: "Orthogonality enables clean composition"

    - id: "INV-5D-003"
      source: "aget_framework"
      statement: "The SYSTEM shall inherit dimension Inviolables from templates"
      rationale: "Template inviolables cannot be weakened"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration (PERSONA, MEMORY)"

    - path: ".aget/evolution/"
      purpose: "Learning_Documents (MEMORY)"

    - path: "governance/"
      purpose: "Governance artifacts (PERSONA, CONTEXT)"

    - path: "planning/"
      purpose: "Planning artifacts (REASONING)"

  required_files:
    - path: ".aget/version.json"
      purpose: "Agent identity (PERSONA)"

    - path: ".aget/identity.json"
      purpose: "North_Star (PERSONA)"

    - path: "governance/CHARTER.md"
      purpose: "Scope_Boundaries (CONTEXT)"

    - path: "CLAUDE.md"
      purpose: "Operational instructions (all dimensions)"

    - path: "manifest.yaml"
      purpose: "Capability declaration (SKILLS)"

  dimension_mapping:
    PERSONA: [".aget/identity.json", ".aget/version.json", "governance/"]
    MEMORY: [".aget/evolution/", "planning/", "governance/"]
    REASONING: ["planning/", "CLAUDE.md"]
    SKILLS: ["manifest.yaml", ".aget/patterns/", "validation/"]
    CONTEXT: ["governance/CHARTER.md", "CLAUDE.md", ".aget/version.json"]
```

---

## Validation

### Dimension Validators

| Dimension | Validator | Purpose |
|-----------|-----------|---------|
| PERSONA | validate_persona_compliance.py | Identity and governance |
| MEMORY | validate_memory_compliance.py | Six_Layer structure |
| REASONING | validate_project_plan.py | Planning patterns |
| SKILLS | validate_composition.py | Capability_Composition |
| CONTEXT | validate_context_compliance.py | Scope and relationships |
| All | validate_5d_compliance.py | Umbrella validator |

### 5D Compliance Check

```bash
# Full 5D compliance validation
python3 validation/validate_5d_compliance.py --dir /path/to/agent

# Individual dimension checks
python3 validation/validate_persona_compliance.py --dir /path/to/agent
python3 validation/validate_memory_compliance.py --dir /path/to/agent
python3 validation/validate_context_compliance.py --dir /path/to/agent

# Capability composition (SKILLS)
python3 validation/validate_composition.py /path/to/manifest.yaml
```

---

## Agent Design Checklist

WHEN designing a new agent, the SYSTEM shall address each dimension:

### D1: PERSONA
- [ ] Base_Template selected (supervisor, advisor, worker, etc.)
- [ ] Governance_Intensity declared (rigorous, balanced, exploratory)
- [ ] North_Star defined (identity.json)
- [ ] Communication_Style established

### D2: MEMORY
- [ ] .aget/evolution/ directory exists
- [ ] governance/ and planning/ directories exist
- [ ] Wake/Wind_Down protocols defined
- [ ] L-doc conventions followed

### D3: REASONING
- [ ] Planning_Patterns match Governance_Intensity
- [ ] Decision_Authority documented
- [ ] Escalation_Paths defined
- [ ] Verification_Tests included

### D4: SKILLS
- [ ] Capabilities declared in Manifest_Yaml
- [ ] Tools/Validators available
- [ ] Output_Formats defined
- [ ] A_SDLC Phase_Alignment clear

### D5: CONTEXT
- [ ] Scope_Boundaries documented
- [ ] Relationships defined (Supervisor, Peers)
- [ ] Environmental_Awareness protocols
- [ ] Session_State handling

---

## Theoretical Basis

The 5D Architecture is grounded in established theory (L331):

| Theory | Five_D Application |
|--------|-------------------|
| **BDI (Belief-Desire-Intention)** | PERSONA = Desires, MEMORY = Beliefs, REASONING = Intentions |
| **Actor Model** | CONTEXT = Actor boundaries, SKILLS = Message handling |
| **Cybernetics** | SKILLS = Requisite variety, MEMORY = Feedback loops |
| **Extended Mind** | MEMORY = Cognitive extension, SKILLS = Cognitive scaffolding |
| **Complex Adaptive Systems** | All dimensions interact for emergent Fleet behavior |

```yaml
theoretical_basis:
  primary: "BDI (Belief-Desire-Intention)"
  secondary:
    - "Actor Model"
    - "Extended Mind"
    - "Cybernetics"
    - "Complex Adaptive Systems"
  rationale: >
    The 5D model maps to BDI's mental states while incorporating
    Actor Model boundaries, Extended Mind cognitive extension,
    Cybernetics feedback and variety, and CAS emergence at fleet level.
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

- L330: Capability Composition Architecture
- L331: Theoretical Foundations of Agency
- L335: Memory Architecture Principles
- L341: Governance Intensity Classification
- COMPOSITION_SPEC_v1.0: Capability composition mechanism
- AGET_SPEC_FORMAT_v1.2: Specification format
- AGET_PERSONA_SPEC, AGET_MEMORY_SPEC, AGET_REASONING_SPEC, AGET_SKILLS_SPEC, AGET_CONTEXT_SPEC

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L330", "L331", "L335", "L341"]
  pattern_origin: "5W+H Knowledge Architecture"
  rationale: "Unifies multiple learnings into coherent architectural framework"
```

---

*AGET 5D Composition Architecture Specification v1.2.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture*
*"Five dimensions, extensible when needed, one coherent agent."*
*Updated: 2025-12-27 (L394 dimension extensions)*
