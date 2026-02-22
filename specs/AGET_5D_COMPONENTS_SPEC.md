# AGET 5D Components Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Core (Architecture)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: aget-framework
**Location**: `aget/specs/AGET_5D_COMPONENTS_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 3.2
**Related Specs**: AGET_5D_ARCHITECTURE_SPEC, AGET_VOCABULARY_SPEC
**Consolidates**: AGET_PERSONA_SPEC, AGET_MEMORY_SPEC, AGET_REASONING_SPEC, AGET_SKILLS_SPEC, AGET_CONTEXT_SPEC

---

## Abstract

This specification consolidates the five dimension specifications of the AGET Composition Architecture into a single comprehensive reference. It defines the PERSONA (WHO), MEMORY (WHAT KNOWS), REASONING (HOW THINKS), SKILLS (WHAT DOES), and CONTEXT (WHERE/WHEN) dimensions that compose agent behavior.

## Motivation

v3.2.0 consolidation goals:
- Reduce spec fragmentation (L434)
- Single source of truth for 5D component specifications
- Unified vocabulary and cross-references
- Preserve all CAP requirements from source specs
- Maintain theoretical grounding for each dimension

This spec combines five separate dimension specs (~2,600 lines) while preserving complete requirement coverage.

## Scope

**Applies to**: All AGET agents using the 5D Composition Architecture.

**Defines**:
- Part 1: PERSONA - Identity, voice, behavior style
- Part 2: MEMORY - Knowledge persistence, learning accumulation
- Part 3: REASONING - Decision patterns, problem-solving approach
- Part 4: SKILLS - Capabilities, tools, integrations
- Part 5: CONTEXT - Environmental awareness, situation adaptation

**Related Specifications**:
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- AGET_VOCABULARY_SPEC: Vocabulary standards
- COMPOSITION_SPEC_v1.0: Capability composition mechanism

---

## The 5D Composition Architecture

The five dimensions form a complete agent specification:

| Dimension | Focus | Question |
|-----------|-------|----------|
| **PERSONA** | Identity, voice, behavior style | WHO is this agent? |
| **MEMORY** | Knowledge persistence, learning | WHAT does it know? |
| **REASONING** | Decision patterns, problem-solving | HOW does it think? |
| **SKILLS** | Capabilities, tools, outputs | WHAT can it do? |
| **CONTEXT** | Environment, relationships, scope | WHERE/WHEN operates? |

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT COMPOSITION                     │
├─────────────┬─────────────┬─────────────┬───────────────┤
│   PERSONA   │   MEMORY    │  REASONING  │    SKILLS     │
│   (WHO)     │ (WHAT KNOWS)│ (HOW THINKS)│  (WHAT DOES)  │
├─────────────┴─────────────┴─────────────┴───────────────┤
│                       CONTEXT                            │
│                    (WHERE / WHEN)                        │
└─────────────────────────────────────────────────────────┘
```

---

# Part 1: PERSONA Dimension

## PERSONA Overview

PERSONA encompasses WHO an agent is: its Archetype, Governance_Intensity, Communication_Style, and Goal_Orientation. PERSONA provides the identity foundation that shapes all other dimensions.

### PERSONA Vocabulary

```yaml
persona:
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
```

## PERSONA Requirements

### CAP-PERSONA-001: Archetype Declaration

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

### CAP-PERSONA-003: Communication Style

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-003-01 | state-driven | WHILE Governance_Rigorous is active, the SYSTEM shall use Style_Formal |
| CAP-PERSONA-003-02 | state-driven | WHILE Governance_Exploratory is active, the SYSTEM shall use Style_Conversational |
| CAP-PERSONA-003-03 | state-driven | WHILE Governance_Balanced is active, the SYSTEM shall use Style_Adaptive |
| CAP-PERSONA-003-04 | ubiquitous | The SYSTEM shall document Communication_Style in Agents_Md |

**Enforcement**: Documentation review

### CAP-PERSONA-004: Goal Orientation

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PERSONA-004-01 | ubiquitous | The SYSTEM shall maintain North_Star in Identity_Json |
| CAP-PERSONA-004-02 | ubiquitous | The SYSTEM shall maintain Mission in Mission_Md |
| CAP-PERSONA-004-03 | ubiquitous | The SYSTEM shall organize goals hierarchically as North_Star, Mission, Objectives |

**Enforcement**: `validate_persona_compliance.py`

### CAP-PERSONA-005: Identity Artifacts

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-PERSONA-005-01 | ubiquitous | The SYSTEM shall maintain Identity_Json | `.aget/identity.json` |
| CAP-PERSONA-005-02 | ubiquitous | The SYSTEM shall maintain Version_Json | `.aget/version.json` |
| CAP-PERSONA-005-03 | ubiquitous | The SYSTEM shall maintain Charter_Md | `governance/CHARTER.md` |
| CAP-PERSONA-005-04 | ubiquitous | The SYSTEM shall maintain Mission_Md | `governance/MISSION.md` |
| CAP-PERSONA-005-05 | ubiquitous | The SYSTEM shall maintain operational instructions in Claude_Md or Agents_Md | `CLAUDE.md` or `AGENTS.md` |

**Enforcement**: `validate_persona_compliance.py`, `validate_agent_structure.py`

## PERSONA Inviolables

```yaml
inviolables:
  - id: "INV-PERSONA-001"
    statement: "The SYSTEM shall NOT operate WITHOUT Identity_Json"
    rationale: "Agent must have identity to function"

  - id: "INV-PERSONA-002"
    statement: "The SYSTEM shall NOT claim Governance_Intensity it does not practice"
    rationale: "Identity integrity requirement"

  - id: "INV-PERSONA-003"
    statement: "IF Governance_Rigorous THEN the SYSTEM shall NOT shift to lower governance"
    rationale: "Rigorous governance is mode-locked (L341)"
```

---

# Part 2: MEMORY Dimension

## MEMORY Overview

MEMORY encompasses WHAT an agent knows: persistent, structured, shareable knowledge across sessions, agents, and humans. The specification formalizes the Six_Layer_Memory_Model, Continual_Learning patterns, and Memory_Compliance requirements.

L335 established: **Knowledge_Base is not storage—Knowledge_Base is the Collaboration_Substrate**.

### MEMORY Vocabulary

```yaml
memory:
  Knowledge_Base:
    skos:definition: "Structured persistent storage for agent knowledge"
    skos:altLabel: "KB"
  Learning_Document:
    skos:definition: "Captured insight in L-doc format"
    skos:altLabel: "L-doc"
    aget:naming: "L{NNN}_{snake_case}.md"
    aget:location: ".aget/evolution/"
  Six_Layer_Memory_Model:
    skos:definition: "Architecture defining memory from working to fleet level"
    skos:narrower: ["Working_Memory", "Session_Memory", "Project_Memory", "Agent_Memory", "Fleet_Memory", "Context_Optimization"]
  Continual_Learning:
    skos:definition: "Framework for accumulating and graduating knowledge"
  Memory_Configuration:
    skos:definition: "Framework configuration for memory behavior (not content)"
    aget:location: ".aget/memory/"
```

## MEMORY Requirements

### CAP-MEMORY-001: Six Layer Memory Model

| ID | Pattern | Statement | Layer |
|----|---------|-----------|-------|
| CAP-MEMORY-001-01 | ubiquitous | The SYSTEM shall maintain Working_Memory as active context | Layer 1 |
| CAP-MEMORY-001-02 | ubiquitous | The SYSTEM shall support Session_Memory via handoff artifacts | Layer 2 |
| CAP-MEMORY-001-03 | ubiquitous | The SYSTEM shall maintain Project_Memory in governance, planning, decisions | Layer 3 |
| CAP-MEMORY-001-04 | ubiquitous | The SYSTEM shall maintain Agent_Memory in .aget/, evolution/, patterns/ | Layer 4 |
| CAP-MEMORY-001-05 | optional | WHERE Fleet_Membership exists, the SYSTEM shall participate in Fleet_Memory | Layer 5 |
| CAP-MEMORY-001-06 | ubiquitous | The SYSTEM shall implement Context_Optimization for selective loading | Layer 6 |

**Enforcement**: `validate_memory_compliance.py`

#### Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: Context_Optimization - Selective loading into window   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 5: Fleet_Memory - Cross-agent knowledge sharing           │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: Agent_Memory - .aget/, evolution/, patterns/           │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Project_Memory - governance/, planning/, decisions/    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Session_Memory - sessions/, Session_Handoff            │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Working_Memory - Ephemeral LLM context window          │
└─────────────────────────────────────────────────────────────────┘
```

### CAP-MEMORY-002: Continual Learning

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-002-01 | event-driven | WHEN Significant_Insight occurs, the SYSTEM shall capture Learning_Document |
| CAP-MEMORY-002-02 | ubiquitous | The SYSTEM shall format Learning_Documents with Context, Insight, Application sections |
| CAP-MEMORY-002-03 | conditional | IF Learning applies to 3+ situations THEN the SYSTEM shall consider Pattern_Graduation |
| CAP-MEMORY-002-04 | conditional | IF Pattern is broadly applicable THEN the SYSTEM shall propose Specification_Graduation |
| CAP-MEMORY-002-05 | ubiquitous | The SYSTEM shall track Graduation_History in artifacts |
| CAP-MEMORY-002-06 | ubiquitous | The SYSTEM shall improve techniques based on learnings |

**Enforcement**: `validate_learning_doc.py`, `validate_graduation_history.py`

### CAP-MEMORY-003: Session Protocols

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-003-01 | event-driven | WHEN Session_Start occurs, the SYSTEM shall execute Wake_Protocol |
| CAP-MEMORY-003-02 | event-driven | WHEN Session_End occurs, the SYSTEM shall execute Wind_Down_Protocol |
| CAP-MEMORY-003-03 | conditional | IF Session is significant THEN the SYSTEM shall create Session_Handoff |
| CAP-MEMORY-003-04 | ubiquitous | The SYSTEM shall complete Context_Recovery WITHIN 2 minutes |
| CAP-MEMORY-003-05 | ubiquitous | The SYSTEM shall document decisions and Pending_Work in Wind_Down_Protocol |

**Enforcement**: Wake/wind-down script execution

### CAP-MEMORY-004: Step Back Review KB

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-004-01 | event-driven | WHEN Step_Back_Trigger is received, the SYSTEM shall execute KB_Review |
| CAP-MEMORY-004-02 | ubiquitous | The SYSTEM shall load relevant KB_Artifacts by context |
| CAP-MEMORY-004-03 | ubiquitous | The SYSTEM shall check inherited/, planning/, evolution/, governance/ |
| CAP-MEMORY-004-04 | conditional | IF Governance_Decision is proposed THEN the SYSTEM shall cite 3+ precedents |
| CAP-MEMORY-004-05 | conditional | IF no precedent exists THEN the SYSTEM shall note Novel_Decision |

**Enforcement**: Documentation review, precedent citation check

### CAP-MEMORY-005: Memory Artifacts

| ID | Pattern | Statement | Path |
|----|---------|-----------|------|
| CAP-MEMORY-005-01 | ubiquitous | The SYSTEM shall maintain Version_Json | `.aget/version.json` |
| CAP-MEMORY-005-02 | ubiquitous | The SYSTEM shall maintain Evolution_Directory | `.aget/evolution/` |
| CAP-MEMORY-005-03 | ubiquitous | The SYSTEM shall maintain Patterns_Directory | `.aget/patterns/` or `docs/patterns/` |
| CAP-MEMORY-005-04 | ubiquitous | The SYSTEM shall maintain Governance_Directory | `governance/` |
| CAP-MEMORY-005-05 | ubiquitous | The SYSTEM shall maintain Planning_Directory | `planning/` |
| CAP-MEMORY-005-06 | optional | WHERE Fleet_Membership exists, the SYSTEM shall maintain Inherited_Directory | `inherited/` |

**Enforcement**: `validate_memory_compliance.py`, `validate_agent_structure.py`

### CAP-MEMORY-006: Memory Hygiene

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-006-01 | conditional | IF Artifact is stale (>6 months) THEN the SYSTEM shall archive Artifact |
| CAP-MEMORY-006-02 | ubiquitous | The SYSTEM shall prune Orphaned_Documents |
| CAP-MEMORY-006-03 | event-driven | WHEN Document moves, the SYSTEM shall update Cross_References |
| CAP-MEMORY-006-04 | ubiquitous | The SYSTEM shall leave Knowledge_Base better than found |
| CAP-MEMORY-006-05 | ubiquitous | The SYSTEM shall add/update artifacts in 80%+ of Significant_Sessions |

**Enforcement**: Memory hygiene review

### CAP-MEMORY-007: Memory Configuration Structure

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-007-01 | ubiquitous | The SYSTEM shall store Memory_Configuration in `.aget/memory/` |
| CAP-MEMORY-007-02 | ubiquitous | The SYSTEM shall store Memory_Content in visible directories |
| CAP-MEMORY-007-03 | prohibited | The SYSTEM shall NOT store user work products in `.aget/memory/` |
| CAP-MEMORY-007-04 | ubiquitous | The `.aget/memory/` directory shall contain only configuration files |
| CAP-MEMORY-007-05 | ubiquitous | The SYSTEM shall use visible `knowledge/`, `sessions/`, `decisions/` for content |

**Enforcement**: `validate_memory_compliance.py`

### CAP-MEMORY-008: L-doc Index Requirement

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-008-01 | conditional | IF L-doc count exceeds 50 THEN the SYSTEM shall maintain `index.json` |
| CAP-MEMORY-008-02 | ubiquitous | The `index.json` shall list all L-docs with id, title, date, tags |
| CAP-MEMORY-008-03 | ubiquitous | The SYSTEM shall support L-doc search by tag, date range, keyword |
| CAP-MEMORY-008-04 | event-driven | WHEN L-doc is created, the SYSTEM shall update `index.json` |
| CAP-MEMORY-008-05 | ubiquitous | The flat file structure shall be preserved (no subdirectories) |

**Enforcement**: `validate_ldoc_index.py`

## MEMORY Inviolables

```yaml
inviolables:
  - id: "INV-MEMORY-001"
    statement: "The SYSTEM shall NOT delete Learning_Documents WITHOUT Archive"
    rationale: "Institutional memory preservation"

  - id: "INV-MEMORY-002"
    statement: "The SYSTEM shall NOT skip Wind_Down_Protocol for Significant_Sessions"
    rationale: "Session continuity requirement"

  - id: "INV-MEMORY-003"
    statement: "The SYSTEM shall NOT claim context it has not loaded"
    rationale: "Memory integrity requirement"
```

---

# Part 3: REASONING Dimension

## REASONING Overview

REASONING encompasses HOW an agent thinks: its Planning_Patterns, Decision_Frameworks, Reflection_Protocols, and Quality_Assurance mechanisms. REASONING provides the cognitive structure that guides agent behavior.

### REASONING Vocabulary

```yaml
reasoning:
  Planning_Pattern:
    skos:definition: "Approach to decomposing and organizing work"
    skos:narrower: ["PROJECT_PLAN", "Gate_Structure", "TodoWrite"]
  Decision_Framework:
    skos:definition: "Structure for making and documenting decisions"
    skos:narrower: ["Decision_Authority_Matrix", "Escalation_Pattern"]
  Reflection_Protocol:
    skos:definition: "Process for reviewing and learning from work"
    skos:narrower: ["Step_Back_Review_KB", "Mid_Gate_Checkpoint"]
  Gate_Discipline:
    skos:definition: "Protocol for stopping at decision boundaries"
    aget:reference: "L42"
  Scope_Expansion:
    skos:definition: "Work beyond current gate or session mandate"
    aget:anti_pattern: true
```

## REASONING Requirements

### CAP-REASON-001: Planning Patterns

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-001-01 | state-driven | WHILE Governance_Rigorous is active, the SYSTEM shall create PROJECT_PLAN for Multi_Step_Tasks |
| CAP-REASON-001-02 | ubiquitous | The SYSTEM shall include Gates with GO_NOGO decision points in PROJECT_PLAN |
| CAP-REASON-001-03 | ubiquitous | The SYSTEM shall include Verification_Tests in PROJECT_PLAN (L382) |
| CAP-REASON-001-04 | state-driven | WHILE Governance_Balanced is active, the SYSTEM should create PROJECT_PLAN for Substantial_Changes |
| CAP-REASON-001-05 | state-driven | WHILE Governance_Exploratory is active, the SYSTEM may omit PROJECT_PLAN |

**Enforcement**: `validate_project_plan.py`

### CAP-REASON-002: Decision Frameworks

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-002-01 | ubiquitous | The SYSTEM shall maintain Decision_Authority_Matrix |
| CAP-REASON-002-02 | conditional | IF Decision exceeds Authority_Level THEN the SYSTEM shall escalate to Supervisor |
| CAP-REASON-002-03 | event-driven | WHEN Novel_Decision occurs, the SYSTEM shall create Learning_Document |
| CAP-REASON-002-04 | conditional | IF Governance_Decision is proposed THEN the SYSTEM shall cite 3+ Precedents |
| CAP-REASON-002-05 | conditional | IF no Precedent exists THEN the SYSTEM shall note Novel_Decision |

**Enforcement**: Documentation review, escalation audit

### CAP-REASON-003: Gate Discipline

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-003-01 | event-driven | WHEN Gate_Boundary is reached, the SYSTEM shall STOP execution |
| CAP-REASON-003-02 | ubiquitous | The SYSTEM shall wait for explicit GO before proceeding past Gate_Boundary |
| CAP-REASON-003-03 | ubiquitous | The SYSTEM shall NOT expand Scope mid-gate |
| CAP-REASON-003-04 | event-driven | WHEN Gate is complete, the SYSTEM shall run Verification_Tests |
| CAP-REASON-003-05 | conditional | IF Verification_Test fails THEN the SYSTEM shall block Gate_Completion |

**Enforcement**: Gate review, test execution

#### Gate Red Flags

| Phrase | Meaning | Response |
|--------|---------|----------|
| "While we're at it..." | Next_Gate work | STOP |
| "I also..." | Scope_Expansion | STOP |
| "Might as well..." | Bypassing Decision_Point | STOP |
| "Let me just..." | Execution without Governance_Artifact | STOP (L340) |

### CAP-REASON-004: Reflection Protocols

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-004-01 | event-driven | WHEN Step_Back_Trigger is received, the SYSTEM shall execute KB_Review |
| CAP-REASON-004-02 | ubiquitous | The SYSTEM shall review Knowledge_Base before Substantial_Proposals |
| CAP-REASON-004-03 | event-driven | WHEN Significant_Insight occurs, the SYSTEM shall capture Learning_Document |
| CAP-REASON-004-04 | conditional | IF Gate has 4+ deliverables THEN the SYSTEM should check Mid_Gate_Progress (L002) |

**Enforcement**: KB review checklist, L-doc creation

### CAP-REASON-005: Quality Assurance

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-005-01 | ubiquitous | The SYSTEM shall include Verification_Tests in PROJECT_PLAN (L382) |
| CAP-REASON-005-02 | ubiquitous | The SYSTEM shall make Verification_Tests executable (bash/python) |
| CAP-REASON-005-03 | ubiquitous | The SYSTEM shall include Expected_Results in Verification_Tests |
| CAP-REASON-005-04 | event-driven | WHEN declaring Gate_Complete, the SYSTEM shall run Verification_Tests |
| CAP-REASON-005-05 | conditional | IF Verification_Test fails THEN the SYSTEM shall block Gate_Completion |

**Enforcement**: `validate_project_plan.py --strict`

### CAP-REASON-006: Session Scope Validation

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-006-01 | event-driven | WHEN Significant_Scope_Expansion is proposed, the SYSTEM shall re-read Session_Mandate |
| CAP-REASON-006-02 | ubiquitous | The SYSTEM shall classify proposed work as Research, Preparation, or Execution |
| CAP-REASON-006-03 | conditional | IF Execution beyond Session_Mandate THEN the SYSTEM shall create Session_Handoff |
| CAP-REASON-006-04 | conditional | IF Scope evolved 3+ times THEN the SYSTEM shall STOP and create Session_Handoff |

**Enforcement**: Session review

### CAP-REASON-007: Execution Governance

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-007-01 | ubiquitous | The SYSTEM shall have Governance_Artifact before modifying Managed_Repos |
| CAP-REASON-007-02 | ubiquitous | The SYSTEM shall reference Tracking_Issue in Governance_Artifact |
| CAP-REASON-007-03 | ubiquitous | The SYSTEM shall define Success_Criteria in Governance_Artifact |
| CAP-REASON-007-04 | ubiquitous | The SYSTEM shall document Rollback_Plan in Governance_Artifact |

**Enforcement**: Pre-execution checklist

### CAP-REASON-008: Release Retrospective (L435)

**CRITICAL**: Release PROJECT_PLANs SHALL include retrospective sections.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-REASON-008-01 | ubiquitous | Release PROJECT_PLAN shall include Retrospective section |
| CAP-REASON-008-02 | ubiquitous | Retrospective shall include What_Went_Well (min 3 items) |
| CAP-REASON-008-03 | ubiquitous | Retrospective shall include What_Could_Be_Improved (min 3 items) |
| CAP-REASON-008-04 | ubiquitous | Retrospective shall include Key_Decisions_Made (min 3 items) |
| CAP-REASON-008-05 | ubiquitous | Retrospective shall include Recommendations (prioritized) |
| CAP-REASON-008-06 | ubiquitous | Retrospective shall include Release_Health_Score (X/10) |

**Enforcement**: `validate_project_plan.py --release`

#### Retrospective Section Template

```markdown
## Retrospective

### What Went Well
| Area | Observation | Evidence |
|------|-------------|----------|

### What Could Be Improved
| Area | Issue | Recommendation |
|------|-------|----------------|

### Key Decisions Made
| Decision | Context | Outcome |
|----------|---------|---------|

### Recommendations for Future Releases
| Category | Recommendation | Priority |
|----------|----------------|----------|

### Release Health Score
| Dimension | Score | Notes |
|-----------|-------|-------|
| **Overall** | **X/10** | |
```

## REASONING Inviolables

```yaml
inviolables:
  - id: "INV-REASON-001"
    statement: "The SYSTEM shall NOT proceed past Gate_Boundary WITHOUT explicit GO"
    rationale: "Gate discipline is foundational (L42)"

  - id: "INV-REASON-002"
    statement: "The SYSTEM shall NOT expand Scope mid-gate"
    rationale: "Scope discipline prevents scope creep"

  - id: "INV-REASON-003"
    statement: "The SYSTEM shall NOT skip Verification_Tests for gates"
    rationale: "Quality assurance is mandatory (L382)"

  - id: "INV-REASON-004"
    statement: "The SYSTEM shall NOT execute without Governance_Artifact (L340)"
    rationale: "Execution governance prevents undocumented changes"
```

---

# Part 4: SKILLS Dimension

## SKILLS Overview

SKILLS encompasses WHAT an agent does: its Capabilities, Tools, Outputs, and Phase_Alignment. SKILLS provides the behavioral repertoire that enables agent action.

### SKILLS Vocabulary

```yaml
skills:
  Capability:
    skos:definition: "Composable behavior unit declared in Manifest_Yaml"
    skos:narrower: ["Memory_Management", "Domain_Knowledge", "Governance_Capability"]
  Capability_Composition:
    skos:definition: "Mechanism for combining capabilities into agent behavior"
    aget:reference: "COMPOSITION_SPEC_v1.0"
  Tool:
    skos:definition: "Executable script or validator available to agent"
    skos:narrower: ["Validator", "Pattern_Script"]
  Validator:
    skos:definition: "Python script that checks compliance"
    aget:location: "validation/"
    aget:naming: "validate_*.py"
  Output_Format:
    skos:definition: "Structured format for agent outputs"
    skos:narrower: ["Markdown", "YAML", "JSON", "Five_W_H"]
  A_SDLC_Phase:
    skos:definition: "Agentic Software Development Lifecycle phase"
```

## SKILLS Requirements

### CAP-SKILL-001: Capability Declaration

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-001-01 | ubiquitous | The SYSTEM shall list Capabilities in Manifest_Yaml |
| CAP-SKILL-001-02 | ubiquitous | The SYSTEM shall reference defined Capability_Specs |
| CAP-SKILL-001-03 | conditional | IF Capability has Prerequisites THEN the SYSTEM shall satisfy Prerequisites |
| CAP-SKILL-001-04 | event-driven | WHEN Capability_Conflict is detected, the SYSTEM shall resolve Conflict |

**Enforcement**: `validate_template_manifest.py`, `validate_composition.py`

### CAP-SKILL-002: Tool Availability

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-002-01 | ubiquitous | The SYSTEM shall have access to Validators for its Domain |
| CAP-SKILL-002-02 | ubiquitous | The SYSTEM shall have Pattern_Scripts in .aget/patterns/ |
| CAP-SKILL-002-03 | ubiquitous | The SYSTEM shall document Tool_Availability |
| CAP-SKILL-002-04 | ubiquitous | The SYSTEM shall register Tools in SCRIPT_REGISTRY |

**Enforcement**: `validate_script_registry.py`

#### Standard Tool Categories

| Category | Examples | Location |
|----------|----------|----------|
| Validators | validate_*.py | validation/ |
| Session_Patterns | wake_up.py, wind_down.py | .aget/patterns/session/ |
| Release_Patterns | version_bump.py | .aget/patterns/release/ |
| Sync_Patterns | template_sync_check.py | .aget/patterns/sync/ |

### CAP-SKILL-003: Output Formats

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-003-01 | optional | WHERE Structured_Outputs capability exists, the SYSTEM shall produce formatted output |
| CAP-SKILL-003-02 | ubiquitous | The SYSTEM shall document Output_Formats |
| CAP-SKILL-003-03 | conditional | IF Domain_Specific_Format is used THEN the SYSTEM shall have Template |

**Enforcement**: Documentation review

### CAP-SKILL-004: A-SDLC Phase Alignment

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-004-01 | ubiquitous | The SYSTEM should declare primary A_SDLC_Phase(s) |
| CAP-SKILL-004-02 | ubiquitous | The SYSTEM shall use Phase_Alignment to inform Capability selection |
| CAP-SKILL-004-03 | optional | WHERE Cross_Cutting role exists, the SYSTEM may span multiple phases |

**Enforcement**: Manifest review

#### A-SDLC Phase Mapping

| Phase | Description | Template_Alignment |
|-------|-------------|--------------------|
| Phase_0 | Strategic Planning | executive, researcher |
| Phase_1 | Requirements | spec-engineer, analyst |
| Phase_2 | Architecture | architect |
| Phase_3 | Implementation | developer |
| Phase_4 | Testing/Review | reviewer |
| Phase_5 | Deployment | operator |
| Phase_6 | Operations | operator, developer |
| Cross_Cutting | All phases | supervisor, advisor, worker, consultant |

### CAP-SKILL-005: Skill Documentation

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-SKILL-005-01 | ubiquitous | The SYSTEM shall document Capability_List | manifest.yaml |
| CAP-SKILL-005-02 | ubiquitous | The SYSTEM shall document Tool_Reference | .aget/patterns/README.md |
| CAP-SKILL-005-03 | ubiquitous | The SYSTEM shall provide Output_Examples | docs/ |
| CAP-SKILL-005-04 | ubiquitous | The SYSTEM shall document Phase_Alignment | AGENTS.md |

**Enforcement**: Documentation review

### CAP-SKILL-006: Capability Composition

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SKILL-006-01 | ubiquitous | The SYSTEM shall compose as Agent = Base_Template + Capabilities |
| CAP-SKILL-006-02 | ubiquitous | The SYSTEM shall satisfy Capability_Prerequisites |
| CAP-SKILL-006-03 | conditional | IF Duplicate_Capability exists THEN the SYSTEM shall ignore Duplicate |
| CAP-SKILL-006-04 | ubiquitous | The SYSTEM shall apply Composition in order-independent manner |

**Enforcement**: `validate_composition.py`

#### Composition Algebra

| Property | Formula | Meaning |
|----------|---------|---------|
| Identity | T + ∅ = T | No capabilities = base template |
| Commutativity | T + [A, B] = T + [B, A] | Order doesn't matter |
| Idempotency | T + [A, A] = T + [A] | Duplicates ignored |
| Prerequisite | A requires B → B must be in list | Dependencies satisfied |

## SKILLS Inviolables

```yaml
inviolables:
  - id: "INV-SKILL-001"
    statement: "The SYSTEM shall NOT use Capability WITHOUT declaring in Manifest_Yaml"
    rationale: "Capabilities must be explicit for composition"

  - id: "INV-SKILL-002"
    statement: "The SYSTEM shall NOT bypass Capability_Prerequisites"
    rationale: "Prerequisite satisfaction is mandatory"

  - id: "INV-SKILL-003"
    statement: "The SYSTEM shall NOT use unregistered Tools in production"
    rationale: "Tool registry enables validation and maintenance"
```

---

# Part 5: CONTEXT Dimension

## CONTEXT Overview

CONTEXT encompasses WHERE and WHEN an agent operates: its Environmental_Awareness, Relationship_Structure, Temporal_State, and Scope_Boundaries. CONTEXT provides situational awareness that shapes agent behavior.

### CONTEXT Vocabulary

```yaml
context:
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
  Session_State:
    skos:definition: "Current state within session lifecycle"
    skos:narrower: ["Fresh_Session", "Continued_Session", "Winding_Down"]
  Scope_Boundary:
    skos:definition: "Defined limits of agent authority and responsibility"
    aget:reference: "L342"
```

## CONTEXT Requirements

### CAP-CONTEXT-001: Environmental Awareness

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

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-002-01 | ubiquitous | The SYSTEM shall know its Supervisor (Managed_By) |
| CAP-CONTEXT-002-02 | ubiquitous | The SYSTEM shall know what it Manages |
| CAP-CONTEXT-002-03 | ubiquitous | The SYSTEM shall understand Escalation_Paths |
| CAP-CONTEXT-002-04 | ubiquitous | The SYSTEM shall document Relationship_Structure in Claude_Md |

**Enforcement**: `validate_context_compliance.py`, documentation review

#### Relationship Clarity (L342)

| Relationship | Meaning | Implication |
|--------------|---------|-------------|
| **Managed_By** (supervisor) | Organizational oversight | Approves major decisions |
| **Manages** (entities) | Artifact ownership | Creates plans, executes work |
| **Peers** | Coordination partners | Handoff and collaboration |

### CAP-CONTEXT-003: Temporal Awareness

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

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-004-01 | ubiquitous | The SYSTEM shall have documented Scope in Charter_Md |
| CAP-CONTEXT-004-02 | ubiquitous | The SYSTEM shall recognize In_Scope vs. Out_Of_Scope work |
| CAP-CONTEXT-004-03 | ubiquitous | The SYSTEM shall NOT exceed Session_Mandate (L342) |
| CAP-CONTEXT-004-04 | conditional | IF Scope_Change is proposed THEN the SYSTEM shall require explicit Approval |
| CAP-CONTEXT-004-05 | conditional | IF Scope evolved 3+ times THEN the SYSTEM shall STOP and create Session_Handoff |

**Enforcement**: Scope review, session validation

### CAP-CONTEXT-005: Context Documentation

| ID | Pattern | Statement | Location |
|----|---------|-----------|----------|
| CAP-CONTEXT-005-01 | ubiquitous | The SYSTEM shall document Supervisor_Relationship | CLAUDE.md |
| CAP-CONTEXT-005-02 | ubiquitous | The SYSTEM shall document Managed_Entities | CLAUDE.md |
| CAP-CONTEXT-005-03 | ubiquitous | The SYSTEM shall document Scope_Boundaries | governance/CHARTER.md |
| CAP-CONTEXT-005-04 | ubiquitous | The SYSTEM shall document Portfolio membership | .aget/version.json |

**Enforcement**: `validate_context_compliance.py`

### CAP-CONTEXT-006: Context-Driven Adaptation

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CONTEXT-006-01 | conditional | IF Public_Repo_Work THEN the SYSTEM shall apply Higher_Governance (L340) |
| CAP-CONTEXT-006-02 | conditional | IF Breaking_Change THEN the SYSTEM shall require Escalation |
| CAP-CONTEXT-006-03 | conditional | IF Novel_Territory THEN the SYSTEM shall apply Rigorous_Mode |
| CAP-CONTEXT-006-04 | event-driven | WHEN Environmental_Change occurs, the SYSTEM shall re-evaluate Context |

**Enforcement**: Operational review

## CONTEXT Inviolables

```yaml
inviolables:
  - id: "INV-CONTEXT-001"
    statement: "The SYSTEM shall NOT exceed Session_Mandate WITHOUT approval (L342)"
    rationale: "Session scope discipline is foundational"

  - id: "INV-CONTEXT-002"
    statement: "The SYSTEM shall NOT assume Environment WITHOUT verification (L185)"
    rationale: "Environmental grounding prevents assumption errors"

  - id: "INV-CONTEXT-003"
    statement: "The SYSTEM shall NOT ignore Supervisor_Relationship for major decisions"
    rationale: "Governance structure must be respected"

  - id: "INV-CONTEXT-004"
    statement: "The SYSTEM shall NOT operate outside documented Scope_Boundaries"
    rationale: "Scope discipline enables coordination"
```

---

## Dimension Interactions

### Cross-Dimension Dependencies

```
PERSONA ←→ REASONING
  - Governance_Intensity determines Planning_Pattern strictness
  - Communication_Style affects how decisions are presented

MEMORY ←→ REASONING
  - KB_Review informs planning decisions
  - Learning_Documents capture reasoning insights

CONTEXT ←→ PERSONA
  - Environment may invoke Governance_Shifts
  - Public_Repo work → Higher_Governance

SKILLS ←→ CONTEXT
  - Context determines which tools apply
  - Phase_Alignment drives capability selection

MEMORY ←→ SKILLS
  - Pattern_Scripts stored as memory artifacts
  - Capabilities reference knowledge structures
```

---

## Theoretical Basis

All five dimensions are grounded in established theory (L331):

| Theory | Primary Application | Dimensions |
|--------|---------------------|------------|
| **BDI (Belief-Desire-Intention)** | Goals as desires, plans as intentions | PERSONA, REASONING |
| **Actor Model** | Boundaries, message passing, encapsulation | CONTEXT, SKILLS |
| **Cybernetics** | Feedback loops, requisite variety | REASONING, MEMORY |
| **Extended Mind** | KB extends cognition, tools extend capability | MEMORY, SKILLS |
| **Transactive Memory** | Shared "who knows what" | MEMORY |
| **Distributed Cognition** | Cognition across artifacts | MEMORY |
| **Stigmergy** | Coordination through environment | MEMORY, CONTEXT |
| **Situated Cognition** | Context shapes available actions | CONTEXT |

---

## Structural Requirements Summary

### Required Directories

| Path | Purpose | Dimension |
|------|---------|-----------|
| `.aget/` | Agent identity and configuration | PERSONA, MEMORY |
| `.aget/evolution/` | Learning_Documents storage | MEMORY |
| `.aget/patterns/` | Pattern_Script storage | SKILLS |
| `governance/` | Governance artifacts | PERSONA, CONTEXT |
| `planning/` | PROJECT_PLANs and planning | REASONING |
| `validation/` | Validator storage | SKILLS |

### Required Files

| Path | Purpose | Dimension |
|------|---------|-----------|
| `.aget/version.json` | Agent identity | PERSONA |
| `.aget/identity.json` | North_Star | PERSONA |
| `governance/CHARTER.md` | Scope boundaries | PERSONA, CONTEXT |
| `governance/MISSION.md` | Goals and metrics | PERSONA |
| `CLAUDE.md` or `AGENTS.md` | Operational instructions | ALL |
| `manifest.yaml` | Capability declaration | SKILLS |

---

## Enforcement Summary

| Dimension | Primary Validators |
|-----------|-------------------|
| PERSONA | `validate_persona_compliance.py`, `validate_agent_structure.py` |
| MEMORY | `validate_memory_compliance.py`, `validate_ldoc_index.py` |
| REASONING | `validate_project_plan.py`, gate review |
| SKILLS | `validate_template_manifest.py`, `validate_composition.py` |
| CONTEXT | `validate_context_compliance.py`, operational review |

---

## References

- L331: Theoretical Foundations of Agency
- L335: Memory Architecture Principles
- L341: Governance Intensity Classification
- L342: Session Scope Validation
- L340: Execution Governance Artifact Requirement
- L42: Gate Discipline
- L185: Environmental Grounding
- L382: Gate Verification Test Gap
- L435: PROJECT_PLAN Retrospective Requirement
- L436: PROJECT_PLAN to SOP Graduation Pattern
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification
- COMPOSITION_SPEC_v1.0: Capability composition mechanism
- AGET_VOCABULARY_SPEC: Vocabulary standards

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial consolidated specification
- Merged AGET_PERSONA_SPEC.md (450 lines)
- Merged AGET_MEMORY_SPEC.md (670 lines)
- Merged AGET_REASONING_SPEC.md (547 lines)
- Merged AGET_SKILLS_SPEC.md (462 lines)
- Merged AGET_CONTEXT_SPEC.md (495 lines)
- Five-part structure matching 5D architecture
- Preserved all CAP requirements (48 requirements across 5 dimensions)
- Preserved all inviolables (14 total)
- Added cross-dimension interaction section
- Added theoretical basis summary table

---

*AGET_5D_COMPONENTS_SPEC.md — Consolidated 5D component specifications for AGET framework*
*Consolidates: AGET_PERSONA_SPEC + AGET_MEMORY_SPEC + AGET_REASONING_SPEC + AGET_SKILLS_SPEC + AGET_CONTEXT_SPEC*
