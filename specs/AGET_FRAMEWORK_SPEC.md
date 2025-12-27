# AGET Framework Specification

**Version**: 3.0.0-alpha.5
**Status**: Pre-release
**Category**: Standards (Framework)
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_FRAMEWORK_SPEC.md`
**Previous**: v2.11.0
**Vocabulary**: AGET_GLOSSARY_STANDARD_SPEC.md

---

## Abstract

AGET (Agent) is a configuration and lifecycle management framework for CLI-based human-AI collaborative coding. This specification defines the behavioral requirements for AGET-compliant agents across 9 capability domains: Core, Session, Governance, Template, Memory, Vocabulary, CLI, Process, and Specification.

## Motivation

Agent behavior requires formal specification:
- Consistent behavior across agent instances
- Testable requirements for validation
- Clear conformance levels for adoption
- Traceability from requirements to implementation

Without explicit behavioral specification, agent behavior becomes inconsistent and unverifiable.

## Scope

**Applies to**: All AGET-compliant agents.

**Defines**:
- Required behaviors for AGET-compliant agents
- File formats and locations
- Protocol sequences
- Failure modes and error handling

**Does NOT Define**:
- CLI tool internals (Claude Code, Cursor, etc.)
- LLM model behavior
- Code execution semantics

---

## Vocabulary

Domain terms for the Framework specification:

```yaml
vocabulary:
  meta:
    domain: "framework"
    version: "1.0.0"
    inherits: "aget_core"

  persona:  # D1: WHO/WHAT identity
    Agent:
      skos:definition: "AGET-compliant entity executing behaviors"
      skos:narrower: ["Instance_Type_aget", "Instance_Type_AGET", "Coordinator"]
    Instance_Type:
      skos:definition: "Classification of agent write authority"
      skos:narrower: ["aget", "AGET", "coordinator"]
    Supervisor:
      skos:definition: "Agent providing governance oversight"

  memory:  # D2: Stored artifacts
    Version_Json:
      skos:definition: "Agent identity file"
      aget:location: ".aget/version.json"
      aget:fields: ["aget_version", "agent_name", "instance_type", "domain", "portfolio", "managed_by"]
    AGENTS_Md:
      skos:definition: "Agent behavior entry point"
      aget:location: "AGENTS.md"
      aget:sections: ["North Star", "Agent Identity", "Purpose"]
    CLAUDE_Md:
      skos:definition: "Symlink to AGENTS.md for Claude Code"
      aget:location: "CLAUDE.md"
    L_Doc:
      skos:definition: "Learning capture document"
      aget:naming: "L{NNN}_{snake_case}.md"
      aget:location: ".aget/evolution/"
    PROJECT_PLAN:
      skos:definition: "Gated execution plan for substantial changes"
      aget:location: "planning/"
    Handoff_Document:
      skos:definition: "Session continuity artifact"
      aget:sections: ["decisions_made", "pending_items", "context_for_next_session"]

  reasoning:  # D3: Decision patterns
    Gate_Discipline:
      skos:definition: "Gated execution with decision points"
      aget:reference: "L42"
    Substantial_Change_Protocol:
      skos:definition: "Review KB, plan, present, wait pattern"
      aget:reference: "L335"
    Human_Override:
      skos:definition: "Principal can override agent recommendations"
      aget:reference: "L178"
    Scope_Creep_Detection:
      skos:definition: "Recognition of scope expansion patterns"
      aget:patterns: ["while we're at it", "might as well", "let me just"]

  skills:  # D4: WHAT DOES
    Wake_Protocol:
      skos:definition: "Session initialization sequence"
    Wind_Down_Protocol:
      skos:definition: "Session finalization sequence"
    Study_Up_Protocol:
      skos:definition: "Deep context loading sequence"
    Sign_Off_Protocol:
      skos:definition: "Complete session closure sequence"
    KB_Review:
      skos:definition: "Step back and review knowledge base"
      aget:trigger: "step back. review kb."

  context:  # D5: WHERE/WHEN
    Session_State:
      skos:definition: "Current session status"
      skos:narrower: ["session.active", "session.signed_off"]
    Conformance_Level:
      skos:definition: "Degree of specification adherence"
      skos:narrower: ["Minimal", "Standard", "Full"]
```

---

## Requirement Verbs

| Verb | Meaning |
|------|---------|
| READ | Access file contents from filesystem |
| WRITE | Create or update file on filesystem |
| CREATE | Make new artifact that did not exist |
| DELETE | Remove artifact from filesystem |
| SET | Assign value to agent state variable |
| GET | Retrieve value from agent state variable |
| EXTRACT | Parse specific field from structured data |
| LOAD | Read file and parse into memory structure |
| DISPLAY | Output to user interface |
| REPORT | Generate formatted output for user |
| CHECK | Verify condition is true |
| VALIDATE | Check against defined rules, report violations |
| TRACK | Maintain list/history across operations |
| APPEND | Add item to existing list |
| EXECUTE | Run defined protocol or command |
| BEGIN | Start multi-step protocol |
| COMPLETE | Finish multi-step protocol |
| WARN | Alert user without stopping execution |
| FAIL | Stop execution with error message |
| ABORT | Immediately terminate operation |
| PROMPT | Request input from user |

---

## Requirements

### CAP-CORE: Core Configuration Requirements

#### CAP-CORE-001: Version Identity

The SYSTEM shall read and use Version_Identity from Version_Json.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CORE-001-01 | event-driven | WHEN Session_Initialization occurs, the SYSTEM shall READ Version_Json |
| CAP-CORE-001-02 | ubiquitous | The SYSTEM shall EXTRACT aget_version field and SET agent.version |
| CAP-CORE-001-03 | ubiquitous | The SYSTEM shall EXTRACT agent_name field and SET agent.name |
| CAP-CORE-001-04 | ubiquitous | The SYSTEM shall EXTRACT instance_type field and SET agent.type |
| CAP-CORE-001-05 | ubiquitous | The SYSTEM shall EXTRACT domain field and SET agent.domain |
| CAP-CORE-001-06 | ubiquitous | The SYSTEM shall EXTRACT portfolio field and SET agent.portfolio |
| CAP-CORE-001-07 | ubiquitous | The SYSTEM shall EXTRACT managed_by field and SET agent.supervisor |
| CAP-CORE-001-08 | conditional | IF Version_Json does not exist THEN the SYSTEM shall FAIL with "Missing .aget/version.json" |
| CAP-CORE-001-09 | conditional | IF aget_version field is missing THEN the SYSTEM shall FAIL with "Invalid version.json" |
| CAP-CORE-001-10 | conditional | IF aget_version format is not semver THEN the SYSTEM shall WARN "Non-standard version format" |

**Enforcement**: `validate_version_consistency.py`

#### CAP-CORE-002: Agent Configuration Entry Point

The SYSTEM shall read behavior from AGENTS_Md.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CORE-002-01 | event-driven | WHEN Session_Initialization occurs, the SYSTEM shall READ AGENTS_Md from repository root |
| CAP-CORE-002-02 | ubiquitous | The SYSTEM shall EXTRACT North_Star section and SET agent.north_star |
| CAP-CORE-002-03 | ubiquitous | The SYSTEM shall EXTRACT Agent_Identity section and SET agent.identity |
| CAP-CORE-002-04 | ubiquitous | The SYSTEM shall EXTRACT Purpose section and SET agent.purpose |
| CAP-CORE-002-05 | conditional | IF AGENTS_Md does not exist THEN the SYSTEM shall FAIL with "Missing AGENTS.md" |
| CAP-CORE-002-06 | conditional | IF North_Star section is missing THEN the SYSTEM shall WARN "No North Star defined" |
| CAP-CORE-002-07 | ubiquitous | The SYSTEM shall CHECK that CLAUDE_Md exists as symlink to AGENTS_Md |
| CAP-CORE-002-08 | conditional | IF CLAUDE_Md is not symlink to AGENTS_Md THEN the SYSTEM shall WARN "CLAUDE.md misconfigured" |

**Enforcement**: Template validation

#### CAP-CORE-003: Directory Structure

The SYSTEM shall validate required Directory_Structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CORE-003-01 | ubiquitous | The SYSTEM shall CHECK that .aget/ directory exists |
| CAP-CORE-003-02 | ubiquitous | The SYSTEM shall CHECK that Version_Json exists in .aget/ |
| CAP-CORE-003-03 | conditional | IF .aget/ directory is missing THEN the SYSTEM shall FAIL with "Not an AGET repository" |
| CAP-CORE-003-04 | ubiquitous | The SYSTEM shall CHECK for .aget/evolution/ directory |
| CAP-CORE-003-05 | conditional | IF .aget/evolution/ is missing THEN the SYSTEM shall CREATE .aget/evolution/ |
| CAP-CORE-003-06 | ubiquitous | The SYSTEM shall CHECK for .aget/patterns/ directory |
| CAP-CORE-003-07 | ubiquitous | The SYSTEM shall CHECK for governance/ directory |
| CAP-CORE-003-08 | ubiquitous | The SYSTEM shall CHECK for planning/ directory |
| CAP-CORE-003-09 | conditional | IF governance/ is missing THEN the SYSTEM shall WARN "No governance structure" |

**Enforcement**: Directory structure validation

#### CAP-CORE-004: Semantic Versioning

The SYSTEM shall enforce Semantic_Versioning.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CORE-004-01 | ubiquitous | The SYSTEM shall VALIDATE that aget_version matches pattern MAJOR.MINOR.PATCH |
| CAP-CORE-004-02 | event-driven | WHEN Version_Change occurs, the SYSTEM shall INCREMENT appropriate segment |
| CAP-CORE-004-03 | conditional | IF Breaking_Change THEN the SYSTEM shall INCREMENT MAJOR and RESET MINOR, PATCH to 0 |
| CAP-CORE-004-04 | conditional | IF New_Feature THEN the SYSTEM shall INCREMENT MINOR and RESET PATCH to 0 |
| CAP-CORE-004-05 | conditional | IF Bug_Fix THEN the SYSTEM shall INCREMENT PATCH |
| CAP-CORE-004-06 | event-driven | WHEN Version_Change occurs, the SYSTEM shall UPDATE Version_Json updated field |
| CAP-CORE-004-07 | event-driven | WHEN Version_Change occurs, the SYSTEM shall APPEND entry to CHANGELOG.md |

**Enforcement**: Version validation

#### CAP-CORE-005: Configuration Validation

The SYSTEM shall validate Configuration on load.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CORE-005-01 | ubiquitous | The SYSTEM shall VALIDATE Version_Json contains required fields |
| CAP-CORE-005-02 | ubiquitous | The SYSTEM shall VALIDATE AGENTS_Md is valid markdown |
| CAP-CORE-005-03 | ubiquitous | The SYSTEM shall CHECK Configuration_Size is under 40,000 characters |
| CAP-CORE-005-04 | conditional | IF Configuration_Size exceeds 40,000 characters THEN the SYSTEM shall WARN "Configuration size limit exceeded" |
| CAP-CORE-005-05 | ubiquitous | The SYSTEM shall VALIDATE instance_type is one of: aget, AGET, coordinator |
| CAP-CORE-005-06 | conditional | IF instance_type is invalid THEN the SYSTEM shall FAIL with "Invalid instance_type" |

**Enforcement**: Configuration validation

---

### CAP-SES: Session Protocol Requirements

#### CAP-SES-001: Wake Protocol

The SYSTEM shall execute Wake_Protocol on "wake up" command.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SES-001-01 | event-driven | WHEN user inputs "wake up", the SYSTEM shall BEGIN Wake_Protocol |
| CAP-SES-001-02 | ubiquitous | The SYSTEM shall READ Version_Json |
| CAP-SES-001-03 | conditional | IF Identity_Json exists THEN the SYSTEM shall READ Identity_Json |
| CAP-SES-001-04 | ubiquitous | The SYSTEM shall READ AGENTS_Md |
| CAP-SES-001-05 | ubiquitous | The SYSTEM shall EXTRACT North_Star from AGENTS_Md |
| CAP-SES-001-06 | ubiquitous | The SYSTEM shall SET session.active = true |
| CAP-SES-001-07 | ubiquitous | The SYSTEM shall EXECUTE git status on Managed_Repositories |
| CAP-SES-001-08 | ubiquitous | The SYSTEM shall CHECK for PENDING.md and READ if exists |
| CAP-SES-001-09 | ubiquitous | The SYSTEM shall DISPLAY agent.name from Version_Json |
| CAP-SES-001-10 | ubiquitous | The SYSTEM shall DISPLAY agent.version from Version_Json |
| CAP-SES-001-11 | ubiquitous | The SYSTEM shall DISPLAY North_Star purpose statement |
| CAP-SES-001-12 | ubiquitous | The SYSTEM shall DISPLAY Managed_Repository paths |
| CAP-SES-001-13 | ubiquitous | The SYSTEM shall DISPLAY git status summary |
| CAP-SES-001-14 | conditional | IF PENDING.md exists THEN the SYSTEM shall DISPLAY pending items |
| CAP-SES-001-15 | ubiquitous | The SYSTEM shall COMPLETE Wake_Protocol with "Ready." message |
| CAP-SES-001-16 | ubiquitous | The SYSTEM shall NOT DISPLAY tool invocations during Wake_Protocol |
| CAP-SES-001-17 | conditional | IF any required file missing THEN the SYSTEM shall FAIL with specific error |

**Enforcement**: Wake protocol tests

#### CAP-SES-002: Wind Down Protocol

The SYSTEM shall execute Wind_Down_Protocol on "wind down" command.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SES-002-01 | event-driven | WHEN user inputs "wind down", the SYSTEM shall BEGIN Wind_Down_Protocol |
| CAP-SES-002-02 | ubiquitous | The SYSTEM shall CHECK for uncommitted git changes |
| CAP-SES-002-03 | conditional | IF uncommitted changes exist THEN the SYSTEM shall PROMPT user for disposition |
| CAP-SES-002-04 | ubiquitous | The SYSTEM shall UPDATE PENDING.md with incomplete work items |
| CAP-SES-002-05 | conditional | IF significant THEN the SYSTEM shall APPEND session decisions to PENDING.md |
| CAP-SES-002-06 | ubiquitous | The SYSTEM shall CHECK for new learnings to capture |
| CAP-SES-002-07 | conditional | IF significant learning identified THEN the SYSTEM shall PROMPT to create L_Doc |
| CAP-SES-002-08 | ubiquitous | The SYSTEM shall DISPLAY session summary |
| CAP-SES-002-09 | ubiquitous | The SYSTEM shall SET session.active = false |
| CAP-SES-002-10 | ubiquitous | The SYSTEM shall COMPLETE Wind_Down_Protocol with confirmation |

**Enforcement**: Wind down protocol tests

#### CAP-SES-003: Study Up Protocol

The SYSTEM shall execute Study_Up_Protocol on "study up" command.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SES-003-01 | event-driven | WHEN user inputs "study up", the SYSTEM shall BEGIN Study_Up_Protocol |
| CAP-SES-003-02 | conditional | IF governance/MISSION.md exists THEN the SYSTEM shall READ it |
| CAP-SES-003-03 | conditional | IF governance/CHARTER.md exists THEN the SYSTEM shall READ it |
| CAP-SES-003-04 | conditional | IF governance/SCOPE_BOUNDARIES.md exists THEN the SYSTEM shall READ it |
| CAP-SES-003-05 | ubiquitous | The SYSTEM shall LIST files in .aget/evolution/ directory |
| CAP-SES-003-06 | ubiquitous | The SYSTEM shall READ 5 most recent L_Docs from .aget/evolution/ |
| CAP-SES-003-07 | ubiquitous | The SYSTEM shall LIST files in planning/ directory |
| CAP-SES-003-08 | ubiquitous | The SYSTEM shall READ active PROJECT_PLANs from planning/ |
| CAP-SES-003-09 | ubiquitous | The SYSTEM shall DISPLAY governance context summary |
| CAP-SES-003-10 | ubiquitous | The SYSTEM shall DISPLAY recent learnings summary |
| CAP-SES-003-11 | ubiquitous | The SYSTEM shall DISPLAY active planning items |
| CAP-SES-003-12 | ubiquitous | The SYSTEM shall COMPLETE Study_Up_Protocol with context summary |

**Enforcement**: Study up protocol tests

#### CAP-SES-004: Session State Management

The SYSTEM shall maintain Session_State across interactions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SES-004-01 | event-driven | WHEN Session_Initialization occurs, the SYSTEM shall SET session.start_time |
| CAP-SES-004-02 | ubiquitous | The SYSTEM shall TRACK session.decisions_made[] list |
| CAP-SES-004-03 | ubiquitous | The SYSTEM shall TRACK session.files_read[] list |
| CAP-SES-004-04 | ubiquitous | The SYSTEM shall TRACK session.files_modified[] list |
| CAP-SES-004-05 | ubiquitous | The SYSTEM shall TRACK session.artifacts_created[] list |
| CAP-SES-004-06 | ubiquitous | The SYSTEM shall TRACK session.errors[] list |
| CAP-SES-004-07 | event-driven | WHEN user_message received, the SYSTEM shall INCREMENT session.exchange_count |
| CAP-SES-004-08 | conditional | IF session.exchange_count exceeds 50 THEN the SYSTEM shall WARN about context length |
| CAP-SES-004-09 | ubiquitous | The SYSTEM shall PRESERVE Session_State across message exchanges |
| CAP-SES-004-10 | conditional | IF Session_State is lost THEN the SYSTEM shall WARN "Session state reset" |

**Enforcement**: Session state tests

#### CAP-SES-005: Sign Off Protocol

The SYSTEM shall execute Sign_Off_Protocol on "sign off" command.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SES-005-01 | event-driven | WHEN user inputs "sign off", the SYSTEM shall BEGIN Sign_Off_Protocol |
| CAP-SES-005-02 | ubiquitous | The SYSTEM shall EXECUTE Wind_Down_Protocol first |
| CAP-SES-005-03 | ubiquitous | The SYSTEM shall VALIDATE all work is committed or documented |
| CAP-SES-005-04 | ubiquitous | The SYSTEM shall DISPLAY final session summary |
| CAP-SES-005-05 | ubiquitous | The SYSTEM shall DISPLAY handoff notes for next session |
| CAP-SES-005-06 | ubiquitous | The SYSTEM shall SET session.signed_off = true |
| CAP-SES-005-07 | ubiquitous | The SYSTEM shall COMPLETE Sign_Off_Protocol with closure message |

**Enforcement**: Sign off protocol tests

---

### CAP-GOV: Governance Requirements

#### CAP-GOV-001: Gate Discipline

The SYSTEM shall follow Gate_Discipline for planning.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-001-01 | event-driven | WHEN Substantial_Change proposed, the SYSTEM shall CREATE PROJECT_PLAN |
| CAP-GOV-001-02 | ubiquitous | The SYSTEM shall STRUCTURE PROJECT_PLAN with numbered gates G-0, G-1, G-2... |
| CAP-GOV-001-03 | ubiquitous | Each gate shall CONTAIN Deliverables_List with Verification_Criteria |
| CAP-GOV-001-04 | ubiquitous | Each gate shall CONTAIN Success_Criteria section |
| CAP-GOV-001-05 | ubiquitous | Each gate shall CONTAIN Rollback_Procedure |
| CAP-GOV-001-06 | ubiquitous | Each gate shall END with Decision_Point: GO/NOGO |
| CAP-GOV-001-07 | ubiquitous | The SYSTEM shall STOP at Gate_Boundary |
| CAP-GOV-001-08 | ubiquitous | The SYSTEM shall WAIT for explicit GO before proceeding to next gate |
| CAP-GOV-001-09 | conditional | IF user signals NOGO THEN the SYSTEM shall EXECUTE Rollback_Procedure |
| CAP-GOV-001-10 | ubiquitous | The SYSTEM shall NOT EXECUTE next gate work until current gate complete |
| CAP-GOV-001-11 | conditional | IF Scope_Creep_Pattern "while we're at it" detected THEN the SYSTEM shall STOP |
| CAP-GOV-001-12 | conditional | IF Scope_Creep_Pattern "might as well" detected THEN the SYSTEM shall STOP |

**Enforcement**: Gate discipline validation

#### CAP-GOV-002: Decision Authority

The SYSTEM shall respect Decision_Authority boundaries.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-002-01 | state-driven | WHILE instance_type is aget, the SYSTEM shall NOT WRITE files |
| CAP-GOV-002-02 | state-driven | WHILE instance_type is aget, the SYSTEM shall NOT EXECUTE commands |
| CAP-GOV-002-03 | state-driven | WHILE instance_type is AGET, the SYSTEM shall WRITE files when authorized |
| CAP-GOV-002-04 | state-driven | WHILE instance_type is AGET, the SYSTEM shall EXECUTE commands when authorized |
| CAP-GOV-002-05 | conditional | IF inherited/DECISION_AUTHORITY_MATRIX.md exists THEN the SYSTEM shall READ it |
| CAP-GOV-002-06 | ubiquitous | The SYSTEM shall CHECK authority before major decisions |
| CAP-GOV-002-07 | conditional | IF decision requires escalation per matrix THEN the SYSTEM shall ESCALATE to Supervisor |
| CAP-GOV-002-08 | ubiquitous | The SYSTEM shall NOT CREATE Breaking_Changes without explicit approval |
| CAP-GOV-002-09 | ubiquitous | The SYSTEM shall NOT PUSH to remote without explicit approval |
| CAP-GOV-002-10 | ubiquitous | The SYSTEM shall DOCUMENT escalation decisions in session log |

**Enforcement**: Authority validation

#### CAP-GOV-003: Substantial Change Protocol

The SYSTEM shall follow Substantial_Change_Protocol.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-003-01 | event-driven | WHEN Multi_Step_Task detected, the SYSTEM shall STOP before implementation |
| CAP-GOV-003-02 | ubiquitous | The SYSTEM shall REVIEW KB before proposing changes |
| CAP-GOV-003-03 | ubiquitous | The SYSTEM shall READ inherited/ directory for precedents |
| CAP-GOV-003-04 | ubiquitous | The SYSTEM shall READ planning/ directory for active work |
| CAP-GOV-003-05 | ubiquitous | The SYSTEM shall READ .aget/evolution/ for relevant learnings |
| CAP-GOV-003-06 | ubiquitous | The SYSTEM shall READ governance/ for boundaries |
| CAP-GOV-003-07 | ubiquitous | The SYSTEM shall CITE 3+ precedents or NOTE "novel situation" |
| CAP-GOV-003-08 | ubiquitous | The SYSTEM shall CREATE incremental gated plan |
| CAP-GOV-003-09 | ubiquitous | The SYSTEM shall PRESENT plan with decision points |
| CAP-GOV-003-10 | ubiquitous | The SYSTEM shall WAIT for user approval before execution |

**Enforcement**: Protocol compliance validation

#### CAP-GOV-004: Execution Governance

The SYSTEM shall require Governance_Artifacts for execution.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-004-01 | event-driven | BEFORE modifying public repositories, the SYSTEM shall CHECK for PROJECT_PLAN |
| CAP-GOV-004-02 | conditional | IF no PROJECT_PLAN exists for work THEN the SYSTEM shall CREATE one |
| CAP-GOV-004-03 | ubiquitous | The SYSTEM shall CHECK that Tracking_Issue is referenced |
| CAP-GOV-004-04 | ubiquitous | The SYSTEM shall CHECK that Success_Criteria are defined |
| CAP-GOV-004-05 | ubiquitous | The SYSTEM shall CHECK that Rollback_Plan is documented |
| CAP-GOV-004-06 | conditional | IF Scope_Creep_Pattern "let me just..." detected THEN the SYSTEM shall STOP |
| CAP-GOV-004-07 | conditional | IF Scope_Creep_Pattern "I'll quickly..." detected THEN the SYSTEM shall STOP |
| CAP-GOV-004-08 | ubiquitous | The SYSTEM shall VALIDATE Governance_Artifact exists before execution |

**Enforcement**: Execution governance validation

#### CAP-GOV-005: Human Override

The SYSTEM shall respect Human_Override principle.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GOV-005-01 | event-driven | WHEN principal overrides recommendation, the SYSTEM shall ACKNOWLEDGE override |
| CAP-GOV-005-02 | ubiquitous | The SYSTEM shall DOCUMENT the override decision |
| CAP-GOV-005-03 | ubiquitous | The SYSTEM shall EXECUTE the overridden action |
| CAP-GOV-005-04 | ubiquitous | The SYSTEM shall NOT repeatedly argue against explicit override |
| CAP-GOV-005-05 | conditional | IF override creates risk THEN the SYSTEM shall WARN once then proceed |
| CAP-GOV-005-06 | ubiquitous | The SYSTEM shall TRACK overrides in session.overrides[] |

**Enforcement**: Override pattern validation

---

### CAP-TPL: Template Requirements

#### CAP-TPL-001: Template Inheritance

The SYSTEM shall resolve Template_Inheritance.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-001-01 | ubiquitous | The SYSTEM shall READ spec.inherits_from field from Template_Spec |
| CAP-TPL-001-02 | conditional | IF inherits_from is declared THEN the SYSTEM shall LOAD Parent_Template |
| CAP-TPL-001-03 | ubiquitous | The SYSTEM shall MERGE parent capabilities into child capabilities |
| CAP-TPL-001-04 | event-driven | WHEN Key_Collision occurs, the SYSTEM shall USE child value |
| CAP-TPL-001-05 | ubiquitous | The SYSTEM shall PRESERVE parent Capability_IDs in merged result |
| CAP-TPL-001-06 | conditional | IF Parent_Template not found THEN the SYSTEM shall FAIL with "Parent template missing" |
| CAP-TPL-001-07 | ubiquitous | The SYSTEM shall VALIDATE merged capabilities against spec format |

**Enforcement**: Template validation

#### CAP-TPL-002: Template Structure

The SYSTEM shall validate Template_Structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-002-01 | ubiquitous | The SYSTEM shall CHECK for AGENTS_Md in template root |
| CAP-TPL-002-02 | ubiquitous | The SYSTEM shall CHECK for CLAUDE_Md symlink in template root |
| CAP-TPL-002-03 | ubiquitous | The SYSTEM shall CHECK for .aget/ directory in template |
| CAP-TPL-002-04 | ubiquitous | The SYSTEM shall CHECK for Version_Json in template |
| CAP-TPL-002-05 | conditional | IF any required file missing THEN the SYSTEM shall REPORT missing files |
| CAP-TPL-002-06 | ubiquitous | The SYSTEM shall VALIDATE template against WORKER_TEMPLATE_SPEC |
| CAP-TPL-002-07 | ubiquitous | The SYSTEM shall REPORT validation errors with file:line references |

**Enforcement**: `validate_template_manifest.py`

#### CAP-TPL-003: Template Versioning

The SYSTEM shall manage Template_Versioning.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-003-01 | ubiquitous | The SYSTEM shall READ aget_version from each template's Version_Json |
| CAP-TPL-003-02 | ubiquitous | The SYSTEM shall CHECK Version_Consistency across templates |
| CAP-TPL-003-03 | conditional | IF versions differ THEN the SYSTEM shall REPORT version mismatches |
| CAP-TPL-003-04 | event-driven | WHEN bumping version, the SYSTEM shall UPDATE all template Version_Json files |
| CAP-TPL-003-05 | ubiquitous | The SYSTEM shall UPDATE CHANGELOG.md in each template |
| CAP-TPL-003-06 | ubiquitous | The SYSTEM shall VERIFY Version_Bump completed in all templates |

**Enforcement**: `validate_version_consistency.py`

#### CAP-TPL-004: Template Sync

The SYSTEM shall keep templates synchronized.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-004-01 | ubiquitous | The SYSTEM shall LIST all template-* directories |
| CAP-TPL-004-02 | ubiquitous | The SYSTEM shall CHECK each template for Version_Json |
| CAP-TPL-004-03 | ubiquitous | The SYSTEM shall COMPARE versions across templates |
| CAP-TPL-004-04 | ubiquitous | The SYSTEM shall REPORT any out-of-sync templates |
| CAP-TPL-004-05 | event-driven | WHEN syncing, the SYSTEM shall UPDATE Version_Json in each template |
| CAP-TPL-004-06 | event-driven | WHEN syncing, the SYSTEM shall COMMIT changes to each template |
| CAP-TPL-004-07 | ubiquitous | The SYSTEM shall VERIFY sync completed successfully |

**Enforcement**: Template sync validation

---

### CAP-MEM: Memory Architecture Requirements

#### CAP-MEM-001: 6-Layer Memory Model

The SYSTEM shall implement Six_Layer_Memory architecture.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEM-001-01 | ubiquitous | The SYSTEM shall MAINTAIN Layer_1: Working_Memory (context window) |
| CAP-MEM-001-02 | ubiquitous | The SYSTEM shall TRACK Layer_2: Session_Memory in Session_State |
| CAP-MEM-001-03 | ubiquitous | The SYSTEM shall ACCESS Layer_3: Project_Memory via governance/, planning/ |
| CAP-MEM-001-04 | ubiquitous | The SYSTEM shall ACCESS Layer_4: Agent_Memory via .aget/ |
| CAP-MEM-001-05 | ubiquitous | The SYSTEM shall ACCESS Layer_5: Fleet_Memory via inherited/ |
| CAP-MEM-001-06 | ubiquitous | The SYSTEM shall EXECUTE Layer_6: Context_Optimization via protocols |
| CAP-MEM-001-07 | event-driven | WHEN loading context, the SYSTEM shall SELECT from appropriate layer |
| CAP-MEM-001-08 | ubiquitous | The SYSTEM shall PRIORITIZE recent Session_Memory over older Project_Memory |
| CAP-MEM-001-09 | ubiquitous | The SYSTEM shall NOT EXCEED Context_Window limits |

**Enforcement**: Memory architecture validation

#### CAP-MEM-002: Step Back / Review KB

The SYSTEM shall execute KB_Review on trigger.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEM-002-01 | event-driven | WHEN user inputs "step back", the SYSTEM shall PAUSE current work |
| CAP-MEM-002-02 | event-driven | WHEN user inputs "review kb", the SYSTEM shall BEGIN KB_Review |
| CAP-MEM-002-03 | ubiquitous | The SYSTEM shall READ inherited/ directory for precedents |
| CAP-MEM-002-04 | ubiquitous | The SYSTEM shall READ planning/ directory for active work |
| CAP-MEM-002-05 | ubiquitous | The SYSTEM shall READ .aget/evolution/ for relevant learnings |
| CAP-MEM-002-06 | ubiquitous | The SYSTEM shall READ governance/ for boundaries and charter |
| CAP-MEM-002-07 | ubiquitous | The SYSTEM shall SUMMARIZE relevant findings |
| CAP-MEM-002-08 | ubiquitous | The SYSTEM shall CITE specific precedents found |
| CAP-MEM-002-09 | conditional | IF no precedents found THEN the SYSTEM shall NOTE "novel situation" |
| CAP-MEM-002-10 | ubiquitous | The SYSTEM shall RESUME work with loaded context |

**Enforcement**: KB review validation

#### CAP-MEM-003: Session Handoff

The SYSTEM shall create Handoff_Documents.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEM-003-01 | event-driven | WHEN significant session ending, the SYSTEM shall CREATE Handoff_Document |
| CAP-MEM-003-02 | ubiquitous | The SYSTEM shall WRITE handoff to workspace/ or inherited/ |
| CAP-MEM-003-03 | ubiquitous | The handoff shall CONTAIN decisions_made section |
| CAP-MEM-003-04 | ubiquitous | The handoff shall CONTAIN pending_items section |
| CAP-MEM-003-05 | ubiquitous | The handoff shall CONTAIN context_for_next_session section |
| CAP-MEM-003-06 | ubiquitous | The handoff shall CONTAIN files_modified list |
| CAP-MEM-003-07 | ubiquitous | The handoff shall CONTAIN artifacts_created list |
| CAP-MEM-003-08 | event-driven | WHEN next session starts, the SYSTEM shall CHECK for Handoff_Documents |
| CAP-MEM-003-09 | conditional | IF handoff exists THEN the SYSTEM shall LOAD handoff into context |
| CAP-MEM-003-10 | ubiquitous | The SYSTEM shall DISPLAY handoff summary to user |

**Enforcement**: Handoff validation

#### CAP-MEM-004: Context Recovery

The SYSTEM shall recover context within Time_Limit.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEM-004-01 | ubiquitous | The SYSTEM shall COMPLETE Context_Recovery within 2 minutes |
| CAP-MEM-004-02 | ubiquitous | The SYSTEM shall LOAD identity from Version_Json immediately |
| CAP-MEM-004-03 | ubiquitous | The SYSTEM shall LOAD North_Star from AGENTS_Md immediately |
| CAP-MEM-004-04 | ubiquitous | The SYSTEM shall CHECK for Handoff_Documents |
| CAP-MEM-004-05 | conditional | IF handoff exists THEN the SYSTEM shall LOAD handoff context |
| CAP-MEM-004-06 | ubiquitous | The SYSTEM shall CHECK for PENDING.md |
| CAP-MEM-004-07 | conditional | IF PENDING.md exists THEN the SYSTEM shall LOAD pending items |
| CAP-MEM-004-08 | ubiquitous | The SYSTEM shall REPORT Context_Recovery complete |

**Enforcement**: Context recovery tests

#### CAP-MEM-005: Learning Capture

The SYSTEM shall capture learnings as L_Docs.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MEM-005-01 | event-driven | WHEN significant learning identified, the SYSTEM shall PROMPT to capture |
| CAP-MEM-005-02 | conditional | IF user approves THEN the SYSTEM shall CREATE L_Doc in .aget/evolution/ |
| CAP-MEM-005-03 | ubiquitous | The SYSTEM shall GENERATE next L_Doc number from existing files |
| CAP-MEM-005-04 | ubiquitous | The L_Doc shall FOLLOW format: L{NNN}_{snake_case}.md |
| CAP-MEM-005-05 | ubiquitous | The L_Doc shall CONTAIN Date, Category, Related fields |
| CAP-MEM-005-06 | ubiquitous | The L_Doc shall CONTAIN Problem section |
| CAP-MEM-005-07 | ubiquitous | The L_Doc shall CONTAIN Learning section |
| CAP-MEM-005-08 | ubiquitous | The L_Doc shall CONTAIN Evidence section |
| CAP-MEM-005-09 | ubiquitous | The L_Doc shall CONTAIN Application section |
| CAP-MEM-005-10 | ubiquitous | The SYSTEM shall COMMIT L_Doc with descriptive message |

**Enforcement**: L-doc validation

---

### CAP-VOC: Vocabulary Requirements

#### CAP-VOC-001: Controlled Vocabulary Usage

The SYSTEM shall use Controlled_Vocabulary.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VOC-001-01 | ubiquitous | The SYSTEM shall USE Title_Case for Domain_Objects |
| CAP-VOC-001-02 | ubiquitous | The SYSTEM shall USE lowercase for verbs |
| CAP-VOC-001-03 | ubiquitous | The SYSTEM shall USE lowercase for prepositions |
| CAP-VOC-001-04 | ubiquitous | The SYSTEM shall USE UPPERCASE for Constraint_Keywords |
| CAP-VOC-001-05 | event-driven | WHEN writing specifications, the SYSTEM shall REFERENCE AGET_GLOSSARY_STANDARD_SPEC.md |
| CAP-VOC-001-06 | conditional | IF term not in vocabulary THEN the SYSTEM shall PROPOSE addition |
| CAP-VOC-001-07 | ubiquitous | The SYSTEM shall NOT USE undefined terms in specifications |

**Enforcement**: `validate_vocabulary.py`

#### CAP-VOC-002: SKOS Compliance

The SYSTEM shall follow SKOS_Vocabulary structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VOC-002-01 | ubiquitous | The SYSTEM shall STRUCTURE vocabulary entries with prefLabel |
| CAP-VOC-002-02 | ubiquitous | The SYSTEM shall INCLUDE definition for each term |
| CAP-VOC-002-03 | ubiquitous | The SYSTEM shall SPECIFY broader/narrower relationships |
| CAP-VOC-002-04 | ubiquitous | The SYSTEM shall SPECIFY related term relationships |
| CAP-VOC-002-05 | ubiquitous | The SYSTEM shall INCLUDE scopeNote for usage context |
| CAP-VOC-002-06 | ubiquitous | The SYSTEM shall VALIDATE vocabulary against SKOS patterns |

**Enforcement**: SKOS validation

#### CAP-VOC-003: Vocabulary Validation

The SYSTEM shall validate Vocabulary_Compliance.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VOC-003-01 | ubiquitous | The SYSTEM shall RUN validate_vocabulary.py on specifications |
| CAP-VOC-003-02 | ubiquitous | The SYSTEM shall REPORT undefined terms found |
| CAP-VOC-003-03 | ubiquitous | The SYSTEM shall REPORT incorrect casing violations |
| CAP-VOC-003-04 | conditional | IF validation fails THEN the SYSTEM shall LIST all violations |
| CAP-VOC-003-05 | ubiquitous | The SYSTEM shall SUGGEST corrections for violations |
| CAP-VOC-003-06 | ubiquitous | The SYSTEM shall NOT APPROVE spec with vocabulary violations |

**Enforcement**: Vocabulary validation

#### CAP-VOC-004: Term Definition

The SYSTEM shall define new terms properly.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-VOC-004-01 | event-driven | WHEN new term needed, the SYSTEM shall CHECK if already defined |
| CAP-VOC-004-02 | conditional | IF term exists THEN the SYSTEM shall USE existing definition |
| CAP-VOC-004-03 | conditional | IF term is new THEN the SYSTEM shall WRITE definition |
| CAP-VOC-004-04 | ubiquitous | The definition shall BE precise and unambiguous |
| CAP-VOC-004-05 | ubiquitous | The SYSTEM shall SPECIFY term type (Entity, Action, State, Event) |
| CAP-VOC-004-06 | ubiquitous | The SYSTEM shall ADD term to AGET_GLOSSARY_STANDARD_SPEC.md |
| CAP-VOC-004-07 | ubiquitous | The SYSTEM shall COMMIT vocabulary update |

**Enforcement**: Term definition validation

---

### CAP-CLI: CLI Settings Requirements

#### CAP-CLI-001: Multi-CLI Configuration

The SYSTEM shall configure multiple CLI_Tools.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CLI-001-01 | ubiquitous | The SYSTEM shall CHECK for .claude/ directory |
| CAP-CLI-001-02 | ubiquitous | The SYSTEM shall CHECK for .codex/ directory |
| CAP-CLI-001-03 | ubiquitous | The SYSTEM shall CHECK for .gemini/ directory |
| CAP-CLI-001-04 | ubiquitous | The SYSTEM shall CHECK for .cursor/ directory |
| CAP-CLI-001-05 | conditional | IF template requested THEN the SYSTEM shall CREATE missing CLI directories |
| CAP-CLI-001-06 | ubiquitous | The SYSTEM shall NOT COMMIT actual settings files (only templates) |

**Enforcement**: CLI configuration validation

#### CAP-CLI-002: Claude Code Settings

The SYSTEM shall manage Claude_Code configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CLI-002-01 | ubiquitous | The SYSTEM shall CHECK for .claude/settings.local.json |
| CAP-CLI-002-02 | conditional | IF .claude/settings.local.json.template exists THEN the SYSTEM shall NOTE template available |
| CAP-CLI-002-03 | conditional | IF settings.local.json exists THEN the SYSTEM shall VALIDATE format |
| CAP-CLI-002-04 | ubiquitous | The SYSTEM shall ADD .claude/settings.local.json to .gitignore |
| CAP-CLI-002-05 | ubiquitous | The SYSTEM shall NOT COMMIT .claude/settings.local.json |

**Enforcement**: Claude settings validation

#### CAP-CLI-003: Codex Settings

The SYSTEM shall manage Codex configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CLI-003-01 | ubiquitous | The SYSTEM shall CHECK for .codex/config.toml |
| CAP-CLI-003-02 | conditional | IF .codex/config.toml.template exists THEN the SYSTEM shall NOTE template available |
| CAP-CLI-003-03 | conditional | IF config.toml exists THEN the SYSTEM shall VALIDATE format |
| CAP-CLI-003-04 | ubiquitous | The SYSTEM shall ADD .codex/config.toml to .gitignore |
| CAP-CLI-003-05 | ubiquitous | The SYSTEM shall NOT COMMIT .codex/config.toml |

**Enforcement**: Codex settings validation

#### CAP-CLI-004: Gemini Settings

The SYSTEM shall manage Gemini configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CLI-004-01 | ubiquitous | The SYSTEM shall CHECK for .gemini/settings.json |
| CAP-CLI-004-02 | conditional | IF .gemini/settings.json.template exists THEN the SYSTEM shall NOTE template available |
| CAP-CLI-004-03 | conditional | IF settings.json exists THEN the SYSTEM shall VALIDATE format |
| CAP-CLI-004-04 | ubiquitous | The SYSTEM shall ADD .gemini/settings.json to .gitignore |
| CAP-CLI-004-05 | ubiquitous | The SYSTEM shall CHECK for GEMINI.md symlink |
| CAP-CLI-004-06 | conditional | IF GEMINI.md missing THEN the SYSTEM shall CREATE symlink to AGENTS_Md |
| CAP-CLI-004-07 | conditional | IF GEMINI.md is not symlink to AGENTS_Md THEN the SYSTEM shall WARN |

**Enforcement**: Gemini settings validation

#### CAP-CLI-005: Cursor Settings

The SYSTEM shall manage Cursor configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CLI-005-01 | ubiquitous | The SYSTEM shall CHECK for .cursor/rules/ directory |
| CAP-CLI-005-02 | conditional | IF .cursor/rules/aget.mdc.template exists THEN the SYSTEM shall NOTE template available |
| CAP-CLI-005-03 | ubiquitous | The SYSTEM shall ADD .cursor/rules/*.mdc to .gitignore (except templates) |
| CAP-CLI-005-04 | ubiquitous | The SYSTEM shall NOT COMMIT actual .mdc files |

**Enforcement**: Cursor settings validation

---

### CAP-PROC: Process Specification Requirements

#### CAP-PROC-001: Process Spec Format

The SYSTEM shall create Process_Specs in YAML.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PROC-001-01 | ubiquitous | The SYSTEM shall WRITE Process_Specs in YAML format |
| CAP-PROC-001-02 | ubiquitous | The SYSTEM shall INCLUDE spec_format_version field |
| CAP-PROC-001-03 | ubiquitous | The SYSTEM shall INCLUDE process_id matching pattern ^[a-z][a-z0-9-]*$ |
| CAP-PROC-001-04 | ubiquitous | The SYSTEM shall INCLUDE process_name field |
| CAP-PROC-001-05 | ubiquitous | The SYSTEM shall INCLUDE status field (pilot, draft, canonical, deprecated) |
| CAP-PROC-001-06 | ubiquitous | The SYSTEM shall INCLUDE gates[] array |
| CAP-PROC-001-07 | ubiquitous | Each gate shall HAVE id, name, activities[], decision_point |
| CAP-PROC-001-08 | ubiquitous | The SYSTEM shall INCLUDE learnings_applied[] section |
| CAP-PROC-001-09 | ubiquitous | The SYSTEM shall SAVE Process_Specs to specs/processes/ |

**Enforcement**: Process spec validation

#### CAP-PROC-002: Process Spec Validation

The SYSTEM shall validate Process_Specs.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PROC-002-01 | ubiquitous | The SYSTEM shall VALIDATE Process_Spec against JSON schema |
| CAP-PROC-002-02 | ubiquitous | The SYSTEM shall CHECK all required fields present |
| CAP-PROC-002-03 | ubiquitous | The SYSTEM shall VALIDATE Gate_IDs follow pattern G-N |
| CAP-PROC-002-04 | ubiquitous | The SYSTEM shall VALIDATE decision_point.next_on_go references valid gate |
| CAP-PROC-002-05 | conditional | IF validation fails THEN the SYSTEM shall REPORT specific errors |
| CAP-PROC-002-06 | ubiquitous | The SYSTEM shall NOT APPROVE Process_Spec with validation errors |

**Enforcement**: `validate_process_spec.py`

#### CAP-PROC-003: Learnings Applied

The SYSTEM shall track learnings in Process_Specs.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PROC-003-01 | ubiquitous | The SYSTEM shall INCLUDE learnings_applied section in Process_Specs |
| CAP-PROC-003-02 | ubiquitous | Each learning shall HAVE id (L_Doc reference) |
| CAP-PROC-003-03 | ubiquitous | Each learning shall HAVE summary description |
| CAP-PROC-003-04 | ubiquitous | Each learning shall HAVE change description showing how applied |
| CAP-PROC-003-05 | event-driven | WHEN process fails, the SYSTEM shall CHECK for applicable learnings |
| CAP-PROC-003-06 | conditional | IF learning applicable THEN the SYSTEM shall UPDATE learnings_applied |

**Enforcement**: Learnings tracking validation

#### CAP-PROC-004: Artifact Graduation

The SYSTEM shall follow Graduation_Pathway for knowledge artifacts.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PROC-004-01 | ubiquitous | Specifications should originate from Validated_Patterns |
| CAP-PROC-004-02 | conditional | IF spec created without pattern precedent THEN the SYSTEM shall DOCUMENT rationale in spec preamble |
| CAP-PROC-004-03 | ubiquitous | Patterns should originate from L_Docs |
| CAP-PROC-004-04 | conditional | IF pattern created without L_Doc precedent THEN the SYSTEM shall DOCUMENT rationale in pattern header |
| CAP-PROC-004-05 | ubiquitous | The SYSTEM shall TRACK graduation_history in artifact metadata |
| CAP-PROC-004-06 | ubiquitous | Graduation to Specification shall REQUIRE Change_Proposal (CP) |
| CAP-PROC-004-07 | ubiquitous | The SYSTEM shall INCLUDE source_learnings[] in pattern metadata |
| CAP-PROC-004-08 | ubiquitous | The SYSTEM shall INCLUDE source_pattern in spec metadata |

**Enforcement**: Graduation pathway validation

#### CAP-PROC-005: Change Proposal Handling

The SYSTEM shall process Change_Proposals per defined workflow.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PROC-005-01 | event-driven | WHEN CP submitted, the SYSTEM shall VALIDATE CP format |
| CAP-PROC-005-02 | ubiquitous | The SYSTEM shall SET CP status to SUBMITTED after validation |
| CAP-PROC-005-03 | ubiquitous | The SYSTEM shall REVIEW CPs during Scoping_Phase |
| CAP-PROC-005-04 | ubiquitous | The SYSTEM shall ASSIGN accepted CPs to VERSION_SCOPE |
| CAP-PROC-005-05 | ubiquitous | The SYSTEM shall TRACK CP status transitions |
| CAP-PROC-005-06 | event-driven | WHEN CP closed, the SYSTEM shall PUBLISH to docs/proposals/ |
| CAP-PROC-005-07 | conditional | IF CP is rejected THEN the SYSTEM shall DOCUMENT Rejection_Rationale |
| CAP-PROC-005-08 | conditional | IF CP is deferred THEN the SYSTEM shall DOCUMENT Deferral_Reason and Target_Version |

**Enforcement**: CP workflow validation

---

### CAP-SPEC: Specification Requirements

#### CAP-SPEC-001: Framework Specification

The SYSTEM shall maintain Framework_Spec per release.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SPEC-001-01 | event-driven | BEFORE release, the SYSTEM shall CREATE AGET_FRAMEWORK_SPEC.md |
| CAP-SPEC-001-02 | ubiquitous | The spec shall DEFINE all requirements in EARS format |
| CAP-SPEC-001-03 | ubiquitous | The spec shall LIST all components with locations |
| CAP-SPEC-001-04 | ubiquitous | The spec shall DESCRIBE all capabilities |
| CAP-SPEC-001-05 | ubiquitous | The spec shall DOCUMENT architecture layers |
| CAP-SPEC-001-06 | ubiquitous | The spec shall DEFINE Conformance_Levels |
| CAP-SPEC-001-07 | ubiquitous | The SYSTEM shall SAVE spec to specs/AGET_FRAMEWORK_SPEC.md |

**Enforcement**: Framework spec validation

#### CAP-SPEC-002: Delta Specification

The SYSTEM shall create Delta_Spec per release.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SPEC-002-01 | event-driven | BEFORE release, the SYSTEM shall CREATE AGET_DELTA_vX.Y.md |
| CAP-SPEC-002-02 | ubiquitous | The delta shall LIST requirements added |
| CAP-SPEC-002-03 | ubiquitous | The delta shall LIST requirements modified |
| CAP-SPEC-002-04 | ubiquitous | The delta shall LIST requirements removed |
| CAP-SPEC-002-05 | ubiquitous | The delta shall LIST components added/modified/removed |
| CAP-SPEC-002-06 | ubiquitous | The delta shall INCLUDE Migration_Guide |
| CAP-SPEC-002-07 | ubiquitous | The delta shall INCLUDE Traceability_Matrix |
| CAP-SPEC-002-08 | ubiquitous | The SYSTEM shall SAVE delta to specs/deltas/AGET_DELTA_vX.Y.md |

**Enforcement**: Delta spec validation

#### CAP-SPEC-003: EARS Format

The SYSTEM shall use EARS_Patterns for requirements.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SPEC-003-01 | ubiquitous | The SYSTEM shall USE "The SYSTEM shall" for ubiquitous requirements |
| CAP-SPEC-003-02 | ubiquitous | The SYSTEM shall USE "WHEN X, the SYSTEM shall" for event-driven |
| CAP-SPEC-003-03 | ubiquitous | The SYSTEM shall USE "WHILE X, the SYSTEM shall" for state-driven |
| CAP-SPEC-003-04 | ubiquitous | The SYSTEM shall USE "WHERE X, the SYSTEM shall" for optional |
| CAP-SPEC-003-05 | ubiquitous | The SYSTEM shall USE "IF X THEN the SYSTEM shall" for conditional |
| CAP-SPEC-003-06 | ubiquitous | The SYSTEM shall USE concrete verbs from vocabulary |
| CAP-SPEC-003-07 | ubiquitous | The SYSTEM shall NOT USE vague verbs (support, provide, enable) |
| CAP-SPEC-003-08 | ubiquitous | The SYSTEM shall SPECIFY object of action explicitly |

**Enforcement**: EARS validation

#### CAP-SPEC-004: Requirement Traceability

The SYSTEM shall trace requirements to artifacts.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SPEC-004-01 | ubiquitous | Each requirement shall HAVE unique ID (CAP-{DOMAIN}-NNN-NN) |
| CAP-SPEC-004-02 | conditional | IF applicable THEN the SYSTEM shall TRACE requirement to L_Doc source |
| CAP-SPEC-004-03 | conditional | IF applicable THEN the SYSTEM shall TRACE requirement to issue |
| CAP-SPEC-004-04 | ubiquitous | The SYSTEM shall TRACE requirement to artifact implementing it |
| CAP-SPEC-004-05 | ubiquitous | The SYSTEM shall CREATE Traceability_Matrix in Delta_Spec |
| CAP-SPEC-004-06 | ubiquitous | The SYSTEM shall VERIFY all requirements have at least one trace |

**Enforcement**: Traceability validation

#### CAP-SPEC-005: Gate Requirement Linkage

The SYSTEM shall link gates to requirements.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SPEC-005-01 | ubiquitous | Each gate in Process_Spec shall REFERENCE requirements it satisfies |
| CAP-SPEC-005-02 | ubiquitous | The SYSTEM shall LIST "Requirements Satisfied" in gate documentation |
| CAP-SPEC-005-03 | conditional | IF gate has no requirement linkage THEN the SYSTEM shall WARN |
| CAP-SPEC-005-04 | ubiquitous | The SYSTEM shall VALIDATE all gate requirements exist in Framework_Spec |
| CAP-SPEC-005-05 | ubiquitous | The SYSTEM shall REPORT Orphan_Gates (no requirement linkage) |

**Enforcement**: Gate linkage validation

---

## Conformance Levels

### Minimal_Conformance

| Requirement Set | Count |
|-----------------|-------|
| CAP-CORE-001 (Version Identity) | 10 |
| CAP-CORE-002 (Entry Point) | 8 |
| CAP-CORE-003-01 to 03 (Basic Structure) | 3 |
| CAP-SES-001-01 to 05 (Basic Wake) | 5 |
| **Total** | **26** |

### Standard_Conformance

Minimal plus:

| Requirement Set | Count |
|-----------------|-------|
| All CAP-CORE | 32 |
| All CAP-SES | 44 |
| CAP-GOV-001 (Gate Discipline) | 12 |
| CAP-MEM-001 to 003 | 29 |
| **Total** | **~120** |

### Full_Conformance

All requirements: **~300**

---

## Authority Model

```yaml
authority:
  applies_to: "all_aget_agents"

  governed_by:
    spec: "AGET_FRAMEWORK_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "execute Session_Protocols"
      - "read and validate Configuration"
      - "track Session_State"
      - "capture L_Docs"

    requires_approval:
      - action: "create Breaking_Changes"
        approver: "supervisor + principal"
      - action: "push to remote"
        approver: "principal"
      - action: "modify Scope_Boundaries"
        approver: "supervisor"

  instance_type_authority:
    aget:
      can: ["READ", "CHECK", "VALIDATE", "REPORT"]
      cannot: ["WRITE", "CREATE", "DELETE", "EXECUTE"]
    AGET:
      can: ["READ", "WRITE", "CREATE", "DELETE", "EXECUTE", "CHECK", "VALIDATE"]
      cannot: ["push without approval", "breaking changes without approval"]
    coordinator:
      can: ["all AGET capabilities", "manage multiple agents"]
      cannot: ["bypass supervisor approval"]
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-CORE-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT proceed past Gate_Boundary without explicit GO"
      rationale: "Gate discipline is foundational (L42)"

    - id: "INV-CORE-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT make Breaking_Changes without explicit approval"
      rationale: "Breaking changes require stakeholder consent"

    - id: "INV-CORE-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT ignore Human_Override"
      rationale: "Principal authority is paramount (L178)"

    - id: "INV-CORE-004"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT exceed instance_type authority"
      rationale: "Advisory agents (aget) cannot write"

    - id: "INV-CORE-005"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT bypass Substantial_Change_Protocol for multi-step tasks"
      rationale: "KB review before execution prevents costly mistakes"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/"
      purpose: "Agent configuration and memory"
      contents:
        - "version.json"
        - "evolution/"
        - "patterns/"

    - path: "governance/"
      purpose: "Agent governance artifacts"
      contents:
        - "CHARTER.md"
        - "MISSION.md"

    - path: "planning/"
      purpose: "Project planning artifacts"

  required_files:
    - path: "AGENTS.md"
      purpose: "Agent behavior entry point"
      sections:
        - "North Star"
        - "Agent Identity"
        - "Purpose"

    - path: "CLAUDE.md"
      purpose: "Symlink to AGENTS.md"
      type: "symlink"

    - path: ".aget/version.json"
      purpose: "Agent identity"
      schema: "version_schema.json"

  optional_files:
    - path: ".aget/identity.json"
      purpose: "Extended identity information"

    - path: "PENDING.md"
      purpose: "Session continuity"
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Actor Model"
  secondary:
    - "BDI (Belief-Desire-Intention)"
    - "Cybernetics (Ashby's requisite variety)"
    - "Extended Mind"
    - "Complex Adaptive Systems"
  rationale: >
    AGET agents are Actors with well-defined message handling (Actor Model).
    They maintain beliefs about state, desires via North Star, and intentions
    via PROJECT_PLANs (BDI). Gate discipline provides requisite variety for
    complexity management (Cybernetics). Knowledge base extends cognition
    (Extended Mind).
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

| Document | Purpose |
|----------|---------|
| AGET_GLOSSARY_STANDARD_SPEC.md | Term definitions |
| AGET_SPEC_FORMAT_v1.2.md | EARS patterns and format |
| AGET_DELTA_v3.0-alpha.md | Changes from v2.11 |
| L331 | Theoretical foundations |
| L335 | Memory architecture |

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L42", "L99", "L143", "L178", "L331", "L335"]
  pattern_origin: "Framework behavior observations"
  rationale: "Formalized agent behaviors from operational learnings"

history:
  - version: "2.10.0"
    date: "2025-12-13"
    changes: "Initial framework spec structure"
  - version: "2.11.0"
    date: "2025-12-23"
    changes: "Expanded to ~300 behavioral requirements"
  - version: "3.0.0-alpha.1"
    date: "2025-12-26"
    changes: "5D Architecture integration"
  - version: "3.0.0-alpha.5"
    date: "2025-12-27"
    changes: "EARS/SKOS reformat (v1.2)"
```

---

*AGET Framework Specification v3.0.0-alpha.5*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*~300 requirements across 9 capability domains*
*"Behavioral specification enables consistent agents."*
