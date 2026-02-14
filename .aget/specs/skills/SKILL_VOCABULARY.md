# AGET Skill Vocabulary

**Version**: 1.2.0
**Created**: 2026-02-10
**Updated**: 2026-02-14
**Status**: production
**Format**: Human-readable markdown (companion to SKOS ontology)
**SKOS Version**: ONTOLOGY_skills.yaml (machine-readable, L482-compliant)

This vocabulary defines terms specific to AGET Skills and their specifications.
For formal SKOS-compliant definitions, see `ONTOLOGY_skills.yaml`.

**Term Count**: 32 terms across 8 categories

---

## Core Terms

### AGET_Skill

**Definition**: Claude Code capability extension following AGET patterns.

**Characteristics**:
- Invoked via `/aget-{name}` slash command
- Located in `.claude/skills/{name}/SKILL.md`
- Has YAML frontmatter with name, description, allowed-tools
- Follows AGET governance (propose → review → approve → implement)

**Related**: Skill_Specification, Skill_Invocation

---

### Skill_Specification

**Definition**: YAML artifact defining skill requirements in EARS format.

**Characteristics**:
- Located in `.aget/specs/skills/SKILL-XXX_{name}.yaml`
- Contains capabilities, test_cases, constraints sections
- Uses EARS patterns (ubiquitous, event-driven, conditional, optional, complex)
- Includes traceability to SKILL.md and L-docs

**Related**: AGET_Skill, EARS_Pattern

---

### Skill_Invocation

**Definition**: User triggering skill via `/aget-{name}` command or Claude auto-invoking based on context.

**Characteristics**:
- Primary trigger: explicit slash command
- Secondary trigger: Claude context matching (if enabled)
- Produces skill-specific output

**Related**: AGET_Skill

---

### Skill_Category

**Definition**: Classification of skill purpose.

**Values**:
| Category | Description | Examples |
|----------|-------------|----------|
| Session | Wake-up, wind-down, save-state lifecycle | aget-wake-up, aget-wind-down |
| Monitoring | Healthcheck, validation, status reporting | aget-healthcheck-evolution |
| Learning | Lesson recording, observation capture | aget-record-lesson |
| Governance | Proposal, review, approval workflows | aget-propose-skill |
| Planning | Project creation, project review | aget-review-project |
| Creation | Skill creation, artifact generation | aget-create-skill |

**Related**: AGET_Skill

---

### Healthcheck_Skill

**Definition**: Skill that validates directory health against thresholds.

**Characteristics**:
- Returns status: OK | WARN | CRITICAL
- Based on file count and size metrics
- Read-only (never modifies files)
- Threshold calibrated per agent archetype

**Instances**: aget-healthcheck-evolution, aget-healthcheck-sessions, aget-healthcheck-kb

**Related**: Health_Status, Threshold

---

## Supporting Terms

### Health_Status

**Definition**: Result of health check evaluation.

**Values**:
- **OK**: All metrics within acceptable range
- **WARN**: Some metrics at warning threshold
- **CRITICAL**: Metrics exceed critical threshold or blocking issue found

**Related**: Healthcheck_Skill

---

### EARS_Pattern

**Definition**: Easy Approach to Requirements Syntax pattern for capability statements.

**Types**:
| Pattern | Format | Example |
|---------|--------|---------|
| Ubiquitous | The SKILL shall {action}. | "The SKILL shall report file counts." |
| Event-driven | WHEN {trigger}, the SKILL shall {action}. | "WHEN invoked, the SKILL shall run script." |
| State-driven | WHILE {state}, the SKILL shall {action}. | "WHILE scanning, the SKILL shall report progress." |
| Optional | WHERE {condition}, the SKILL shall {action}. | "WHERE --json flag provided, output JSON." |
| Complex | IF {condition} THEN WHEN {trigger}... | Combination patterns |

**Related**: Skill_Specification

---

### Advisory_Enforcement

**Definition**: Governance pattern where compliance is voluntary and supervised, not technically blocked.

**Characteristics**:
- No runtime blocking if bypassed
- Supervisor detects violations via healthchecks
- Intervention follows supervision patterns (critique + teaching)

**Used by**: aget-propose-skill

---

## Session Terms

### Session_Initialization

**Definition**: Process of starting an AGET session with status briefing.

**Related**: AGET_Skill, Skill_Invocation

---

### Session_Termination

**Definition**: Process of ending an AGET session with state capture.

**Related**: Wind_Down_Protocol

---

### Wind_Down_Protocol

**Definition**: Structured session ending with notes, commit staging, and sanity checks.

**Related**: Session_Termination, Session_State

---

### Session_State

**Definition**: Captured context of an active session for resume/recovery.

**Related**: Checkpoint, Session_Artifact

---

### Checkpoint

**Definition**: Saved workflow state at a natural breakpoint for recovery.

**Location**: `sessions/checkpoints/{name}.checkpoint.yaml`

**Related**: Session_State

---

### Sanity_Check

**Definition**: Health inspection and housekeeping validation of agent state.

**Related**: Healthcheck_Skill, Health_Status

---

## Directory Terms

### Evolution_Directory

**Definition**: Directory containing framework learnings and process patterns.

**Location**: `.aget/evolution/`

**Related**: Learning_Document

---

### Sessions_Directory

**Definition**: Directory containing session logs and checkpoints.

**Location**: `sessions/`

**Related**: Session_Artifact

---

### Knowledge_Base

**Definition**: Structured collection of agent knowledge including learnings, specs, and vocabulary.

**Related**: Evolution_Directory, Framework_Belief

---

## Learning Terms

### Learning_Document

**Definition**: Markdown artifact documenting a process learning (L-doc).

**Format**: `L###_{title}.md`

**Location**: `.aget/evolution/`

**Related**: Framework_Belief

---

### Framework_Belief

**Definition**: Process pattern or methodology knowledge portable across domains.

**Location**: `.aget/evolution/`

**Related**: Domain_Belief, Learning_Document

---

### Domain_Belief

**Definition**: Domain-specific knowledge not portable across contexts.

**Location**: `knowledge/` at root

**Related**: Framework_Belief

---

### Observation

**Definition**: Research finding or pattern discovered during session work.

**Related**: Session_Artifact, Learning_Document

---

### Session_Artifact

**Definition**: Any artifact produced during a session (logs, observations, checkpoints).

**Location**: `sessions/`

**Related**: Observation, Checkpoint

---

## Planning Terms

### Project_Plan

**Definition**: Gated execution plan for multi-phase work.

**Format**: `PROJECT_PLAN_{name}.md`

**Location**: `planning/`

**Related**: V_Test, Research_Phase

---

### Project_Review

**Definition**: Mid-flight assessment of project health and progress.

**Related**: Project_Plan, V_Test

---

### V_Test

**Definition**: Verification test that validates gate completion.

**Format**: `V-{gate}.{number}`

**Related**: Project_Plan

---

### Research_Phase

**Definition**: Pre-execution phase for gathering evidence and context.

**Related**: Project_Plan

---

## Creation Terms

### Skill_Proposal

**Definition**: Structured proposal for a new skill following governance patterns.

**Location**: `planning/skill-proposals/`

**Related**: AGET_Skill, Advisory_Enforcement

---

### Skill_Implementation

**Definition**: The SKILL.md file that implements a skill's behavior.

**Related**: SKILL_MD, AGET_Skill

---

### SKILL_MD

**Definition**: Markdown file with YAML frontmatter defining skill behavior.

**Location**: `.claude/skills/{name}/SKILL.md`

**Related**: Skill_Implementation, AGET_Skill

---

## Governance Terms

### Issue_Routing

**Definition**: Determining correct destination repository for an issue based on agent type.

**Characteristics**:
- Private fleet agents → `gmelli/aget-aget`
- Public/remote agents → `aget-framework/aget`
- Based on path, version.json, or git remote detection

**Related**: Content_Sanitization, L520

---

### Content_Sanitization

**Definition**: Removing or redacting private information before filing to public repositories.

**Patterns to sanitize**:
- Private agent names (`private-*-aget`)
- Internal repo references (`gmelli/*`)
- Fleet size disclosures
- Session references

**Related**: Issue_Routing, L520

---

### Issue_Governance

**Definition**: L520-compliant process for filing issues with correct routing and content handling.

**Components**:
1. Agent type detection
2. Destination routing
3. Content sanitization
4. Template selection
5. Validation before filing

**Related**: Issue_Routing, Content_Sanitization, SKILL-040

---

## Traceability

| Link | Reference |
|------|-----------|
| L-docs | L532, L589 |
| Template | SKILL_SPEC_TEMPLATE.yaml |
| Specs | SKILL-001 through SKILL-013 |
| Project | PROJECT_PLAN_skill_specification_remediation_v1.0.md |

---

*SKILL_VOCABULARY.md v1.0.0*
*Created as part of Skill Specification Remediation project*
