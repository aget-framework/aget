# AGET Memory Specification

**Version**: 1.2.0
**Status**: Active
**Category**: Standards (5D Composition - MEMORY Dimension)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_MEMORY_SPEC.md`

---

## Abstract

This specification defines the MEMORY dimension of the 5D Composition Architecture. Memory enables persistent, structured, shareable knowledge across sessions, agents, and humans. The specification formalizes the Six_Layer_Memory_Model, Continual_Learning patterns, and Memory_Compliance requirements.

## Motivation

Human-AI collaboration faces fundamental asymmetry:
- AI has no persistent memory (each session starts fresh)
- Human has limited bandwidth to re-explain context
- Project state exists but isn't systematically loaded

L335 (Memory Architecture Principles) established that **Knowledge_Base is not storage—Knowledge_Base is the Collaboration_Substrate**. This specification formalizes that insight into testable requirements.

## Scope

**Applies to**: All AGET agents using Memory_Management capability.

**Defines**:
- Six_Layer_Memory_Model
- Continual_Learning framework
- Memory_Artifact types
- Session_Protocol
- Compliance requirements

---

## The 5D Composition Context

Memory is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | AGET_PERSONA_SPEC |
| **MEMORY** | Knowledge persistence, learning accumulation | **This document** |
| REASONING | Decision patterns, problem-solving approach | AGET_REASONING_SPEC |
| SKILLS | Specific capabilities, tools, integrations | AGET_SKILLS_SPEC |
| CONTEXT | Environmental awareness, situation adaptation | AGET_CONTEXT_SPEC |

---

## Vocabulary

Domain terms for the MEMORY dimension:

```yaml
vocabulary:
  meta:
    domain: "memory"
    version: "1.0.0"
    inherits: "aget_core"

  memory:  # D2: WHAT KNOWS
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
    Graduation_Pathway:
      skos:definition: "Process by which learnings become patterns become specs"
    Memory_Configuration:
      skos:definition: "Framework configuration for memory behavior (not content)"
      aget:location: ".aget/memory/"
      skos:note: "Contains layer_config.yaml, inheritance.yaml, retrieval.yaml"
    L_doc_Index:
      skos:definition: "Index file for navigating large Learning_Document collections"
      aget:location: ".aget/evolution/index.json"
      skos:note: "Required when L-doc count exceeds 50"
    Memory_Content:
      skos:definition: "User work products stored in visible directories"
      skos:note: "Portable content NOT stored in .aget/"
      skos:example: "knowledge/, sessions/, decisions/"

  persona:  # D1: Terms defined
    Evolution_Directory:
      skos:definition: "Directory containing Learning_Documents"
      aget:location: ".aget/evolution/"

  skills:  # D4: Capabilities
    Wake_Protocol:
      skos:definition: "Session initialization loading context"
      aget:location: ".aget/patterns/session/wake_up.py"
    Wind_Down_Protocol:
      skos:definition: "Session finalization capturing artifacts"
      aget:location: ".aget/patterns/session/wind_down.py"
    Step_Back_Review_KB:
      skos:definition: "Mid-session context refresh pattern"

  context:  # D5: Where applied
    Session_Handoff:
      skos:definition: "Document enabling session continuity"
```

---

## Requirements

### CAP-MEMORY-001: Six Layer Memory Model

The SYSTEM shall implement the Six_Layer_Memory_Model.

| ID | Pattern | Statement | Layer |
|----|---------|-----------|-------|
| CAP-MEMORY-001-01 | ubiquitous | The SYSTEM shall maintain Working_Memory as active context | Layer 1 |
| CAP-MEMORY-001-02 | ubiquitous | The SYSTEM shall support Session_Memory via handoff artifacts | Layer 2 |
| CAP-MEMORY-001-03 | ubiquitous | The SYSTEM shall maintain Project_Memory in governance, planning, decisions | Layer 3 |
| CAP-MEMORY-001-04 | ubiquitous | The SYSTEM shall maintain Agent_Memory in .aget/, evolution/, patterns/ | Layer 4 |
| CAP-MEMORY-001-05 | optional | WHERE Fleet_Membership exists, the SYSTEM shall participate in Fleet_Memory | Layer 5 |
| CAP-MEMORY-001-06 | ubiquitous | The SYSTEM shall implement Context_Optimization for selective loading | Layer 6 |

**Enforcement**: `validate_memory_compliance.py`

#### Layer Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: Context_Optimization                                   │
│ Selective loading of relevant context into active window        │
│ Patterns: Step_Back_Review_KB, Wake_Protocol, Context_Budget    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 5: Fleet_Memory                                           │
│ Cross-agent knowledge sharing, Pattern_Graduation               │
│ Artifacts: FLEET_STATE.yaml, upstream/downstream flow           │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: Agent_Memory                                           │
│ Identity persistence, capability evolution, pattern libraries   │
│ Artifacts: .aget/, evolution/, patterns/                        │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Project_Memory                                         │
│ KB structure, planning artifacts, decision records              │
│ Artifacts: governance/, planning/, decisions/, docs/            │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Session_Memory                                         │
│ Session artifacts, decisions made, learnings captured           │
│ Artifacts: sessions/, Session_Handoff, workspace/               │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Working_Memory                                         │
│ Active context window, current conversation state               │
│ Artifacts: None (ephemeral—LLM context window)                  │
└─────────────────────────────────────────────────────────────────┘
```

### CAP-MEMORY-002: Continual Learning

The SYSTEM shall accumulate knowledge through Continual_Learning.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-002-01 | event-driven | WHEN Significant_Insight occurs, the SYSTEM shall capture Learning_Document |
| CAP-MEMORY-002-02 | ubiquitous | The SYSTEM shall format Learning_Documents with Context, Insight, Application sections |
| CAP-MEMORY-002-03 | conditional | IF Learning applies to 3+ situations THEN the SYSTEM shall consider Pattern_Graduation |
| CAP-MEMORY-002-04 | conditional | IF Pattern is broadly applicable THEN the SYSTEM shall propose Specification_Graduation |
| CAP-MEMORY-002-05 | ubiquitous | The SYSTEM shall track Graduation_History in artifacts |
| CAP-MEMORY-002-06 | ubiquitous | The SYSTEM shall improve techniques based on learnings |

**Enforcement**: `validate_learning_doc.py`, `validate_graduation_history.py`

#### Continual Learning Cycle

```
    ┌────────────────────────────────────────────────────┐
    │                CONTINUAL_LEARNING                   │
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

### CAP-MEMORY-003: Session Protocols

The SYSTEM shall implement Session_Protocol for memory continuity.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-003-01 | event-driven | WHEN Session_Start occurs, the SYSTEM shall execute Wake_Protocol |
| CAP-MEMORY-003-02 | event-driven | WHEN Session_End occurs, the SYSTEM shall execute Wind_Down_Protocol |
| CAP-MEMORY-003-03 | conditional | IF Session is significant THEN the SYSTEM shall create Session_Handoff |
| CAP-MEMORY-003-04 | ubiquitous | The SYSTEM shall complete Context_Recovery WITHIN 2 minutes |
| CAP-MEMORY-003-05 | ubiquitous | The SYSTEM shall document decisions and Pending_Work in Wind_Down_Protocol |

**Enforcement**: Wake/wind-down script execution, session review

#### Wake_Protocol

```bash
# Minimal wake protocol
1. Load Version_Json (identity)
2. Load Identity_Json (North_Star)
3. Check Git_Status (current state)
4. Display Summary
```

#### Wind_Down_Protocol

```markdown
# Session_Handoff Template
## What we set out to do
## What we actually did
## Decisions that changed direction
## Current state
## Next session should start with
## Critical context not to forget
## KB artifacts created/modified
```

### CAP-MEMORY-004: Step Back Review KB

The SYSTEM shall support Mid_Session_Context_Refresh.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-004-01 | event-driven | WHEN Step_Back_Trigger is received, the SYSTEM shall execute KB_Review |
| CAP-MEMORY-004-02 | ubiquitous | The SYSTEM shall load relevant KB_Artifacts by context |
| CAP-MEMORY-004-03 | ubiquitous | The SYSTEM shall check inherited/, planning/, evolution/, governance/ |
| CAP-MEMORY-004-04 | conditional | IF Governance_Decision is proposed THEN the SYSTEM shall cite 3+ precedents |
| CAP-MEMORY-004-05 | conditional | IF no precedent exists THEN the SYSTEM shall note Novel_Decision |

**Enforcement**: Documentation review, precedent citation check

#### Review KB Checklist

```
BEFORE proposing substantial changes:
- [ ] inherited/   — precedents, Decision_Authority
- [ ] planning/    — active work, related Project_Plans
- [ ] evolution/   — learnings applicable to context
- [ ] governance/  — boundaries, charter, mission
- [ ] Cite 3+ precedents OR note "novel"
```

### CAP-MEMORY-005: Memory Artifacts

The SYSTEM shall maintain required Memory_Artifact structure.

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

The SYSTEM shall maintain Memory_Health.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-006-01 | conditional | IF Artifact is stale (>6 months) THEN the SYSTEM shall archive Artifact |
| CAP-MEMORY-006-02 | ubiquitous | The SYSTEM shall prune Orphaned_Documents |
| CAP-MEMORY-006-03 | event-driven | WHEN Document moves, the SYSTEM shall update Cross_References |
| CAP-MEMORY-006-04 | ubiquitous | The SYSTEM shall leave Knowledge_Base better than found |
| CAP-MEMORY-006-05 | ubiquitous | The SYSTEM shall add/update artifacts in 80%+ of Significant_Sessions |

**Enforcement**: Memory hygiene review

### CAP-MEMORY-007: Memory Configuration Structure

The SYSTEM shall separate Memory_Configuration from Memory_Content.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-007-01 | ubiquitous | The SYSTEM shall store Memory_Configuration in `.aget/memory/` |
| CAP-MEMORY-007-02 | ubiquitous | The SYSTEM shall store Memory_Content in visible directories |
| CAP-MEMORY-007-03 | prohibited | The SYSTEM shall NOT store user work products in `.aget/memory/` |
| CAP-MEMORY-007-04 | ubiquitous | The `.aget/memory/` directory shall contain only configuration files |
| CAP-MEMORY-007-05 | ubiquitous | The SYSTEM shall use visible `knowledge/`, `sessions/`, `decisions/` for content |

**Enforcement**: `validate_memory_compliance.py`

#### Memory Configuration vs Content

```
CONFIGURATION (in .aget/memory/):        CONTENT (in visible directories):
├── layer_config.yaml                    ├── knowledge/
│   └── 6-layer model settings           │   └── domain expertise, research
├── inheritance.yaml                     ├── sessions/
│   └── what to inherit from fleet       │   └── session notes, handoffs
└── retrieval.yaml                       ├── decisions/
    └── context loading priorities       │   └── decision records
                                         └── docs/
                                             └── documentation artifacts

EXCEPTION:
.aget/evolution/*.md (L-docs)
└── Framework-licensed learnings
└── Portable via Apache 2.0
└── Hidden but tracked in git
```

#### Rationale

```yaml
rationale:
  principle: "Portability requires visibility"
  source: "L394 (Design by Fleet Exploration)"
  insight: >
    Fleet exploration revealed that .aget/memory/ subdirectories (domain/,
    experiential/, organizational/) implied content storage. User work
    products must be visible for portability. Configuration (how memory
    works) belongs in .aget/; content (what was learned) belongs in
    visible directories.
  reference: "AGET_PORTABILITY_SPEC CAP-PORT-001A"
```

### CAP-MEMORY-008: L-doc Index Requirement

The SYSTEM shall support L-doc scaling through indexing.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEMORY-008-01 | conditional | IF L-doc count exceeds 50 THEN the SYSTEM shall maintain `index.json` |
| CAP-MEMORY-008-02 | ubiquitous | The `index.json` shall list all L-docs with id, title, date, tags |
| CAP-MEMORY-008-03 | ubiquitous | The SYSTEM shall support L-doc search by tag, date range, keyword |
| CAP-MEMORY-008-04 | event-driven | WHEN L-doc is created, the SYSTEM shall update `index.json` |
| CAP-MEMORY-008-05 | ubiquitous | The flat file structure shall be preserved (no subdirectories) |

**Enforcement**: `validate_ldoc_index.py`

#### Index Structure

```json
{
  "meta": {
    "version": "1.0.0",
    "generated": "2025-12-27T10:00:00Z",
    "count": 338
  },
  "entries": [
    {
      "id": "L001",
      "file": "L001_gate_execution_discipline.md",
      "title": "Gate Execution Discipline",
      "date": "2025-01-15",
      "tags": ["governance", "gates", "execution"],
      "status": "active"
    },
    {
      "id": "L394",
      "file": "L394_design_by_fleet_exploration.md",
      "title": "Design by Fleet Exploration",
      "date": "2025-12-27",
      "tags": ["design", "fleet", "specification"],
      "status": "active"
    }
  ],
  "categories": {
    "governance": ["L001", "L042", "L099"],
    "design": ["L289", "L394"],
    "memory": ["L335", "L340"]
  }
}
```

#### Scaling Rationale

```yaml
rationale:
  problem: "Real agents accumulate 300+ L-docs"
  evidence: "private-supervisor-AGET: 338 L-docs"
  solution: "Index + flat structure"
  tradeoffs:
    index_overhead: "Minimal (generated automatically)"
    search_benefit: "O(1) lookup by id/tag vs O(n) file scan"
    flat_preservation: "Maintains simplicity, no nested navigation"
  source: "L394 Fleet Exploration, GAP_ANALYSIS A5"
```

---

## Authority Model

```yaml
authority:
  applies_to: "agents_with_memory_management_capability"

  governed_by:
    spec: "AGET_MEMORY_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "create Learning_Documents"
      - "execute Wake_Protocol"
      - "execute Wind_Down_Protocol"
      - "propose Pattern_Graduation"

    requires_approval:
      - action: "Specification_Graduation"
        approver: "framework-aget"
      - action: "Fleet_Memory modification"
        approver: "supervisor"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-MEMORY-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT delete Learning_Documents WITHOUT Archive"
      rationale: "Institutional memory preservation"

    - id: "INV-MEMORY-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT skip Wind_Down_Protocol for Significant_Sessions"
      rationale: "Session continuity requirement"

    - id: "INV-MEMORY-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT claim context it has not loaded"
      rationale: "Memory integrity requirement"
```

---

## Structural Requirements

```yaml
structure:
  # FRAMEWORK CONFIGURATION (.aget/ - hidden, Apache 2.0)
  required_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration"

    - path: ".aget/evolution/"
      purpose: "Learning_Documents storage"
      naming: "L{NNN}_{snake_case}.md"
      scaling: "index.json when count > 50"

    - path: ".aget/memory/"
      purpose: "Memory configuration (NOT content)"
      contents:
        - "layer_config.yaml"      # 6-layer model settings
        - "inheritance.yaml"       # Fleet inheritance rules
        - "retrieval.yaml"         # Context loading priorities
      prohibited: "User work products, domain content"

  # VISIBLE CONTENT (portable, user-licensed)
  required_visible_directories:
    - path: "governance/"
      purpose: "Governance artifacts"

    - path: "planning/"
      purpose: "Planning artifacts"

  optional_visible_directories:
    - path: "knowledge/"
      purpose: "Domain expertise, research"

    - path: "sessions/"
      purpose: "Session_Handoff storage"

    - path: "decisions/"
      purpose: "Decision records"

    - path: "inherited/"
      purpose: "Fleet-inherited knowledge"

  # OPTIONAL FRAMEWORK (.aget/ subdirs)
  optional_framework_directories:
    - path: ".aget/patterns/"
      purpose: "Agent pattern scripts"

  required_files:
    - path: ".aget/version.json"
      purpose: "Agent identity"

  optional_files:
    - path: ".aget/evolution/index.json"
      purpose: "L-doc index for scaling"
      required_when: "L-doc count > 50"

  domain_structure:
    - path: ".aget/evolution/"
      purpose: "Learning accumulation"
      pattern: "L{NNN}_{snake_case}.md"
      minimum_entries: 1
      index_required: "when count > 50"

  # ANTI-PATTERN: These should NOT exist
  prohibited_structures:
    - path: ".aget/memory/domain/"
      reason: "Content belongs in visible knowledge/"
    - path: ".aget/memory/experiential/"
      reason: "Content belongs in visible sessions/"
    - path: ".aget/memory/organizational/"
      reason: "Content belongs in visible governance/"
```

---

## Memory Capability Contract

Agents with Memory_Management capability MUST satisfy:

```yaml
contracts:
  # Core structure
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

  # v1.2.0 additions: Config vs Content
  - name: memory_config_only
    assertion: no_content_subdirs
    path: .aget/memory/
    prohibited_subdirs:
      - domain/
      - experiential/
      - organizational/
    rationale: "Content belongs in visible directories"

  - name: has_ldoc_index_when_scaled
    assertion: file_exists_if_threshold
    path: .aget/evolution/index.json
    threshold:
      count_files: ".aget/evolution/L*.md"
      minimum: 50
    warning_only: true

  - name: content_in_visible_directories
    assertion: content_not_in_hidden
    visible_paths:
      - knowledge/
      - sessions/
      - decisions/
    hidden_content_prohibited:
      - .aget/memory/**/
    rationale: "Portability requires visibility"
```

---

## Theoretical Basis

Memory architecture is grounded in established theories (L335):

| Theory | Application |
|--------|-------------|
| **Extended Mind** (Clark/Chalmers, 1998) | Knowledge_Base extends cognitive capacity beyond individual minds |
| **Transactive Memory** (Wegner, 1987) | Human-AI pairs develop shared "who knows what" |
| **Distributed Cognition** (Hutchins, 1995) | Cognition happens across people, tools, artifacts |
| **Stigmergy** (Grassé, 1959) | Coordination through environment modification |
| **Cybernetics** (Ashby, 1956) | Knowledge_Base provides requisite variety for Context_Recovery |

```yaml
theoretical_basis:
  primary: "Extended Mind"
  secondary:
    - "Transactive Memory"
    - "Distributed Cognition"
    - "Stigmergy"
    - "Cybernetics (Requisite Variety)"
  rationale: >
    Memory architecture treats Knowledge_Base as cognitive infrastructure, not
    documentation. The Knowledge_Base extends human-AI cognition (Extended Mind),
    serves as shared knowledge index (Transactive Memory), carries
    cognition across sessions (Distributed Cognition), enables
    coordination through environment modification (Stigmergy), and
    provides variety to handle situational complexity (Cybernetics).
  reference: "L335_memory_architecture_principles.md"
```

---

## Validation

```bash
# Validate Memory_Compliance
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
- L394: Design by Fleet Exploration (source of v1.2.0 insights)
- MEMORY_VISION.md (governance document)
- PATTERN_step_back_review_kb.md
- CAP-PROC-004: Artifact Graduation Pathway
- AGET_SPEC_FORMAT_v1.2: Specification format
- AGET_PORTABILITY_SPEC: Content vs Configuration model
- GAP_ANALYSIS_v3.0_fleet_exploration.md: Gap A5 (L-doc scaling)

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L335"]
  pattern_origin: "PATTERN_step_back_review_kb.md"
  governance_vision: "MEMORY_VISION.md"
  rationale: "User-discovered 'step back. review kb.' pattern formalized into dimension spec"
```

---

*AGET Memory Specification v1.2.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture - MEMORY Dimension*
*"Knowledge_Base is not storage—Knowledge_Base is the Collaboration_Substrate."*
*v1.2.0: Config vs Content separation, L-doc index scaling (L394)*
