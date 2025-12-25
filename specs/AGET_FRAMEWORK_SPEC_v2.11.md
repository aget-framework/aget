# AGET Framework Specification v2.11

**Version**: 2.11.0
**Date**: 2025-12-23
**Status**: Current
**Previous**: v2.10.0
**Format**: AGET_SPEC_FORMAT_v1.1
**Vocabulary**: AGET_CONTROLLED_VOCABULARY.md

---

## 1. Executive Summary

AGET (Agent) is a configuration and lifecycle management framework for CLI-based human-AI collaborative coding. This specification defines the behavioral requirements for AGET-compliant agents.

**Requirement Count**: ~300 specific behavioral statements
**Categories**: 9 (Core, Session, Governance, Template, Memory, Vocabulary, CLI, Process, Specification)

---

## 2. Scope

### 2.1 What This Specification Defines

- Required behaviors for AGET-compliant agents
- File formats and locations
- Protocol sequences
- Failure modes and error handling

### 2.2 What This Specification Does Not Define

- CLI tool internals (Claude Code, Cursor, etc.)
- LLM model behavior
- Code execution semantics

---

## 3. Requirements

### Legend

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

## R-CORE: Core Configuration Requirements

### R-CORE-001: Version Identity

The Agent reads and uses version identity from .aget/version.json.

| ID | Requirement |
|----|-------------|
| R-CORE-001-01 | The Agent SHALL READ .aget/version.json at session initialization |
| R-CORE-001-02 | The Agent SHALL EXTRACT aget_version field and SET agent.version |
| R-CORE-001-03 | The Agent SHALL EXTRACT agent_name field and SET agent.name |
| R-CORE-001-04 | The Agent SHALL EXTRACT instance_type field and SET agent.type |
| R-CORE-001-05 | The Agent SHALL EXTRACT domain field and SET agent.domain |
| R-CORE-001-06 | The Agent SHALL EXTRACT portfolio field and SET agent.portfolio |
| R-CORE-001-07 | The Agent SHALL EXTRACT managed_by field and SET agent.supervisor |
| R-CORE-001-08 | IF .aget/version.json does not exist, the Agent SHALL FAIL with "Missing .aget/version.json" |
| R-CORE-001-09 | IF aget_version field is missing, the Agent SHALL FAIL with "Invalid version.json: missing aget_version" |
| R-CORE-001-10 | IF aget_version format is not semver, the Agent SHALL WARN "Non-standard version format" |

### R-CORE-002: Agent Configuration Entry Point

The Agent reads behavior from AGENTS.md.

| ID | Requirement |
|----|-------------|
| R-CORE-002-01 | The Agent SHALL READ AGENTS.md from repository root at session initialization |
| R-CORE-002-02 | The Agent SHALL EXTRACT North Star section and SET agent.north_star |
| R-CORE-002-03 | The Agent SHALL EXTRACT Agent Identity section and SET agent.identity |
| R-CORE-002-04 | The Agent SHALL EXTRACT Purpose section and SET agent.purpose |
| R-CORE-002-05 | IF AGENTS.md does not exist, the Agent SHALL FAIL with "Missing AGENTS.md" |
| R-CORE-002-06 | IF North Star section is missing, the Agent SHALL WARN "No North Star defined" |
| R-CORE-002-07 | The Agent SHALL CHECK that CLAUDE.md exists as symlink to AGENTS.md |
| R-CORE-002-08 | IF CLAUDE.md is not a symlink to AGENTS.md, the Agent SHALL WARN "CLAUDE.md misconfigured" |

### R-CORE-003: Directory Structure

The Agent validates required directory structure.

| ID | Requirement |
|----|-------------|
| R-CORE-003-01 | The Agent SHALL CHECK that .aget/ directory exists |
| R-CORE-003-02 | The Agent SHALL CHECK that .aget/version.json exists in .aget/ |
| R-CORE-003-03 | IF .aget/ directory is missing, the Agent SHALL FAIL with "Not an AGET repository" |
| R-CORE-003-04 | The Agent SHALL CHECK for .aget/evolution/ directory |
| R-CORE-003-05 | IF .aget/evolution/ is missing, the Agent SHALL CREATE .aget/evolution/ |
| R-CORE-003-06 | The Agent SHALL CHECK for .aget/patterns/ directory |
| R-CORE-003-07 | The Agent SHALL CHECK for governance/ directory |
| R-CORE-003-08 | The Agent SHALL CHECK for planning/ directory |
| R-CORE-003-09 | IF governance/ is missing, the Agent SHALL WARN "No governance structure" |

### R-CORE-004: Semantic Versioning

The Agent enforces semantic versioning.

| ID | Requirement |
|----|-------------|
| R-CORE-004-01 | The Agent SHALL VALIDATE that aget_version matches pattern MAJOR.MINOR.PATCH |
| R-CORE-004-02 | WHEN version changes, the Agent SHALL INCREMENT appropriate segment |
| R-CORE-004-03 | IF breaking change, the Agent SHALL INCREMENT MAJOR and RESET MINOR, PATCH to 0 |
| R-CORE-004-04 | IF new feature, the Agent SHALL INCREMENT MINOR and RESET PATCH to 0 |
| R-CORE-004-05 | IF bug fix, the Agent SHALL INCREMENT PATCH |
| R-CORE-004-06 | WHEN version changes, the Agent SHALL UPDATE .aget/version.json updated field |
| R-CORE-004-07 | WHEN version changes, the Agent SHALL APPEND entry to CHANGELOG.md |

### R-CORE-005: Configuration Validation

The Agent validates configuration on load.

| ID | Requirement |
|----|-------------|
| R-CORE-005-01 | The Agent SHALL VALIDATE version.json contains required fields |
| R-CORE-005-02 | The Agent SHALL VALIDATE AGENTS.md is valid markdown |
| R-CORE-005-03 | The Agent SHALL CHECK configuration size is under 40,000 characters |
| R-CORE-005-04 | IF configuration exceeds 40,000 characters, the Agent SHALL WARN "Configuration size limit exceeded" |
| R-CORE-005-05 | The Agent SHALL VALIDATE instance_type is one of: aget, AGET, coordinator |
| R-CORE-005-06 | IF instance_type is invalid, the Agent SHALL FAIL with "Invalid instance_type" |

---

## R-SES: Session Protocol Requirements

### R-SES-001: Wake Protocol

The Agent executes wake protocol on "wake up" command.

| ID | Requirement |
|----|-------------|
| R-SES-001-01 | WHEN user inputs "wake up", the Agent SHALL BEGIN Wake_Protocol |
| R-SES-001-02 | The Agent SHALL READ .aget/version.json |
| R-SES-001-03 | The Agent SHALL READ .aget/identity.json IF it exists |
| R-SES-001-04 | The Agent SHALL READ AGENTS.md |
| R-SES-001-05 | The Agent SHALL EXTRACT North Star from AGENTS.md |
| R-SES-001-06 | The Agent SHALL SET session.active = true |
| R-SES-001-07 | The Agent SHALL EXECUTE git status on managed repositories |
| R-SES-001-08 | The Agent SHALL CHECK for PENDING.md and READ if exists |
| R-SES-001-09 | The Agent SHALL DISPLAY agent name from version.json |
| R-SES-001-10 | The Agent SHALL DISPLAY agent version from version.json |
| R-SES-001-11 | The Agent SHALL DISPLAY North Star purpose statement |
| R-SES-001-12 | The Agent SHALL DISPLAY managed repository paths |
| R-SES-001-13 | The Agent SHALL DISPLAY git status summary |
| R-SES-001-14 | IF PENDING.md exists, the Agent SHALL DISPLAY pending items |
| R-SES-001-15 | The Agent SHALL COMPLETE Wake_Protocol with "Ready." message |
| R-SES-001-16 | The Agent SHALL NOT DISPLAY tool invocations during Wake_Protocol |
| R-SES-001-17 | IF any required file missing, the Agent SHALL FAIL with specific error |

### R-SES-002: Wind Down Protocol

The Agent executes wind down protocol on "wind down" command.

| ID | Requirement |
|----|-------------|
| R-SES-002-01 | WHEN user inputs "wind down", the Agent SHALL BEGIN Wind_Down_Protocol |
| R-SES-002-02 | The Agent SHALL CHECK for uncommitted git changes |
| R-SES-002-03 | IF uncommitted changes exist, the Agent SHALL PROMPT user for disposition |
| R-SES-002-04 | The Agent SHALL UPDATE PENDING.md with incomplete work items |
| R-SES-002-05 | The Agent SHALL APPEND session decisions to PENDING.md if significant |
| R-SES-002-06 | The Agent SHALL CHECK for new learnings to capture |
| R-SES-002-07 | IF significant learning identified, the Agent SHALL PROMPT to create L-doc |
| R-SES-002-08 | The Agent SHALL DISPLAY session summary |
| R-SES-002-09 | The Agent SHALL SET session.active = false |
| R-SES-002-10 | The Agent SHALL COMPLETE Wind_Down_Protocol with confirmation |

### R-SES-003: Study Up Protocol

The Agent executes study up protocol on "study up" command.

| ID | Requirement |
|----|-------------|
| R-SES-003-01 | WHEN user inputs "study up", the Agent SHALL BEGIN Study_Up_Protocol |
| R-SES-003-02 | The Agent SHALL READ governance/MISSION.md IF exists |
| R-SES-003-03 | The Agent SHALL READ governance/CHARTER.md IF exists |
| R-SES-003-04 | The Agent SHALL READ governance/SCOPE_BOUNDARIES.md IF exists |
| R-SES-003-05 | The Agent SHALL LIST files in .aget/evolution/ directory |
| R-SES-003-06 | The Agent SHALL READ 5 most recent L-docs from .aget/evolution/ |
| R-SES-003-07 | The Agent SHALL LIST files in planning/ directory |
| R-SES-003-08 | The Agent SHALL READ active PROJECT_PLANs from planning/ |
| R-SES-003-09 | The Agent SHALL DISPLAY governance context summary |
| R-SES-003-10 | The Agent SHALL DISPLAY recent learnings summary |
| R-SES-003-11 | The Agent SHALL DISPLAY active planning items |
| R-SES-003-12 | The Agent SHALL COMPLETE Study_Up_Protocol with context summary |

### R-SES-004: Session State Management

The Agent maintains session state across interactions.

| ID | Requirement |
|----|-------------|
| R-SES-004-01 | The Agent SHALL SET session.start_time at session initialization |
| R-SES-004-02 | The Agent SHALL TRACK session.decisions_made[] list |
| R-SES-004-03 | The Agent SHALL TRACK session.files_read[] list |
| R-SES-004-04 | The Agent SHALL TRACK session.files_modified[] list |
| R-SES-004-05 | The Agent SHALL TRACK session.artifacts_created[] list |
| R-SES-004-06 | The Agent SHALL TRACK session.errors[] list |
| R-SES-004-07 | The Agent SHALL INCREMENT session.exchange_count on each user message |
| R-SES-004-08 | WHEN session.exchange_count exceeds 50, the Agent SHALL WARN about context length |
| R-SES-004-09 | The Agent SHALL PRESERVE session state across message exchanges |
| R-SES-004-10 | IF session state is lost, the Agent SHALL WARN "Session state reset" |

### R-SES-005: Sign Off Protocol

The Agent executes sign off protocol on "sign off" command.

| ID | Requirement |
|----|-------------|
| R-SES-005-01 | WHEN user inputs "sign off", the Agent SHALL BEGIN Sign_Off_Protocol |
| R-SES-005-02 | The Agent SHALL EXECUTE Wind_Down_Protocol first |
| R-SES-005-03 | The Agent SHALL VALIDATE all work is committed or documented |
| R-SES-005-04 | The Agent SHALL DISPLAY final session summary |
| R-SES-005-05 | The Agent SHALL DISPLAY handoff notes for next session |
| R-SES-005-06 | The Agent SHALL SET session.signed_off = true |
| R-SES-005-07 | The Agent SHALL COMPLETE Sign_Off_Protocol with closure message |

---

## R-GOV: Governance Requirements

### R-GOV-001: Gate Discipline

The Agent follows gate discipline for planning.

| ID | Requirement |
|----|-------------|
| R-GOV-001-01 | WHEN substantial change proposed, the Agent SHALL CREATE PROJECT_PLAN |
| R-GOV-001-02 | The Agent SHALL STRUCTURE PROJECT_PLAN with numbered gates G-0, G-1, G-2... |
| R-GOV-001-03 | Each gate SHALL CONTAIN deliverables list with verification criteria |
| R-GOV-001-04 | Each gate SHALL CONTAIN success criteria section |
| R-GOV-001-05 | Each gate SHALL CONTAIN rollback procedure |
| R-GOV-001-06 | Each gate SHALL END with decision point: GO/NOGO |
| R-GOV-001-07 | The Agent SHALL STOP at gate boundary |
| R-GOV-001-08 | The Agent SHALL WAIT for explicit GO before proceeding to next gate |
| R-GOV-001-09 | IF user signals NOGO, the Agent SHALL EXECUTE rollback procedure |
| R-GOV-001-10 | The Agent SHALL NOT EXECUTE next gate work until current gate complete |
| R-GOV-001-11 | IF Agent detects "while we're at it" scope creep, the Agent SHALL STOP |
| R-GOV-001-12 | IF Agent detects "might as well" scope creep, the Agent SHALL STOP |

### R-GOV-002: Decision Authority

The Agent respects decision authority boundaries.

| ID | Requirement |
|----|-------------|
| R-GOV-002-01 | WHERE instance_type is aget, the Agent SHALL NOT WRITE files |
| R-GOV-002-02 | WHERE instance_type is aget, the Agent SHALL NOT EXECUTE commands |
| R-GOV-002-03 | WHERE instance_type is AGET, the Agent SHALL WRITE files when authorized |
| R-GOV-002-04 | WHERE instance_type is AGET, the Agent SHALL EXECUTE commands when authorized |
| R-GOV-002-05 | The Agent SHALL READ inherited/DECISION_AUTHORITY_MATRIX.md IF exists |
| R-GOV-002-06 | The Agent SHALL CHECK authority before major decisions |
| R-GOV-002-07 | IF decision requires escalation per matrix, the Agent SHALL ESCALATE to supervisor |
| R-GOV-002-08 | The Agent SHALL NOT CREATE breaking changes without explicit approval |
| R-GOV-002-09 | The Agent SHALL NOT PUSH to remote without explicit approval |
| R-GOV-002-10 | The Agent SHALL DOCUMENT escalation decisions in session log |

### R-GOV-003: Substantial Change Protocol

The Agent follows substantial change protocol.

| ID | Requirement |
|----|-------------|
| R-GOV-003-01 | WHEN multi-step task detected, the Agent SHALL STOP before implementation |
| R-GOV-003-02 | The Agent SHALL REVIEW KB before proposing changes |
| R-GOV-003-03 | The Agent SHALL READ inherited/ directory for precedents |
| R-GOV-003-04 | The Agent SHALL READ planning/ directory for active work |
| R-GOV-003-05 | The Agent SHALL READ .aget/evolution/ for relevant learnings |
| R-GOV-003-06 | The Agent SHALL READ governance/ for boundaries |
| R-GOV-003-07 | The Agent SHALL CITE 3+ precedents or NOTE "novel situation" |
| R-GOV-003-08 | The Agent SHALL CREATE incremental gated plan |
| R-GOV-003-09 | The Agent SHALL PRESENT plan with decision points |
| R-GOV-003-10 | The Agent SHALL WAIT for user approval before execution |

### R-GOV-004: Execution Governance

The Agent requires governance artifacts for execution.

| ID | Requirement |
|----|-------------|
| R-GOV-004-01 | BEFORE modifying public repositories, the Agent SHALL CHECK for PROJECT_PLAN |
| R-GOV-004-02 | IF no PROJECT_PLAN exists for work, the Agent SHALL CREATE one |
| R-GOV-004-03 | The Agent SHALL CHECK that tracking issue is referenced |
| R-GOV-004-04 | The Agent SHALL CHECK that success criteria are defined |
| R-GOV-004-05 | The Agent SHALL CHECK that rollback plan is documented |
| R-GOV-004-06 | IF "let me just..." pattern detected, the Agent SHALL STOP |
| R-GOV-004-07 | IF "I'll quickly..." pattern detected, the Agent SHALL STOP |
| R-GOV-004-08 | The Agent SHALL VALIDATE governance artifact exists before execution |

### R-GOV-005: Human Override

The Agent respects human override principle.

| ID | Requirement |
|----|-------------|
| R-GOV-005-01 | WHEN principal overrides recommendation, the Agent SHALL ACKNOWLEDGE override |
| R-GOV-005-02 | The Agent SHALL DOCUMENT the override decision |
| R-GOV-005-03 | The Agent SHALL EXECUTE the overridden action |
| R-GOV-005-04 | The Agent SHALL NOT repeatedly argue against explicit override |
| R-GOV-005-05 | IF override creates risk, the Agent SHALL WARN once then proceed |
| R-GOV-005-06 | The Agent SHALL TRACK overrides in session.overrides[] |

---

## R-TPL: Template Requirements

### R-TPL-001: Template Inheritance

The Agent resolves template inheritance.

| ID | Requirement |
|----|-------------|
| R-TPL-001-01 | The Agent SHALL READ spec.inherits_from field from template spec |
| R-TPL-001-02 | IF inherits_from is declared, the Agent SHALL LOAD parent template |
| R-TPL-001-03 | The Agent SHALL MERGE parent capabilities into child capabilities |
| R-TPL-001-04 | WHEN key collision occurs, the Agent SHALL USE child value |
| R-TPL-001-05 | The Agent SHALL PRESERVE parent capability IDs in merged result |
| R-TPL-001-06 | IF parent template not found, the Agent SHALL FAIL with "Parent template missing" |
| R-TPL-001-07 | The Agent SHALL VALIDATE merged capabilities against spec format |

### R-TPL-002: Template Structure

The Agent validates template structure.

| ID | Requirement |
|----|-------------|
| R-TPL-002-01 | The Agent SHALL CHECK for AGENTS.md in template root |
| R-TPL-002-02 | The Agent SHALL CHECK for CLAUDE.md symlink in template root |
| R-TPL-002-03 | The Agent SHALL CHECK for .aget/ directory in template |
| R-TPL-002-04 | The Agent SHALL CHECK for .aget/version.json in template |
| R-TPL-002-05 | IF any required file missing, the Agent SHALL REPORT missing files |
| R-TPL-002-06 | The Agent SHALL VALIDATE template against WORKER_TEMPLATE_SPEC |
| R-TPL-002-07 | The Agent SHALL REPORT validation errors with file:line references |

### R-TPL-003: Template Versioning

The Agent manages template versions.

| ID | Requirement |
|----|-------------|
| R-TPL-003-01 | The Agent SHALL READ aget_version from each template's version.json |
| R-TPL-003-02 | The Agent SHALL CHECK version consistency across templates |
| R-TPL-003-03 | IF versions differ, the Agent SHALL REPORT version mismatches |
| R-TPL-003-04 | WHEN bumping version, the Agent SHALL UPDATE all template version.json files |
| R-TPL-003-05 | The Agent SHALL UPDATE CHANGELOG.md in each template |
| R-TPL-003-06 | The Agent SHALL VERIFY version bump completed in all templates |

### R-TPL-004: Template Sync

The Agent keeps templates synchronized.

| ID | Requirement |
|----|-------------|
| R-TPL-004-01 | The Agent SHALL LIST all template-* directories |
| R-TPL-004-02 | The Agent SHALL CHECK each template for version.json |
| R-TPL-004-03 | The Agent SHALL COMPARE versions across templates |
| R-TPL-004-04 | The Agent SHALL REPORT any out-of-sync templates |
| R-TPL-004-05 | WHEN syncing, the Agent SHALL UPDATE version.json in each template |
| R-TPL-004-06 | WHEN syncing, the Agent SHALL COMMIT changes to each template |
| R-TPL-004-07 | The Agent SHALL VERIFY sync completed successfully |

---

## R-MEM: Memory Architecture Requirements

### R-MEM-001: 6-Layer Memory Model

The Agent implements 6-layer memory architecture.

| ID | Requirement |
|----|-------------|
| R-MEM-001-01 | The Agent SHALL MAINTAIN Layer 1: Working Memory (context window) |
| R-MEM-001-02 | The Agent SHALL TRACK Layer 2: Session Memory in session state |
| R-MEM-001-03 | The Agent SHALL ACCESS Layer 3: Project Memory via governance/, planning/ |
| R-MEM-001-04 | The Agent SHALL ACCESS Layer 4: Agent Memory via .aget/ |
| R-MEM-001-05 | The Agent SHALL ACCESS Layer 5: Fleet Memory via inherited/ |
| R-MEM-001-06 | The Agent SHALL EXECUTE Layer 6: Context Optimization via protocols |
| R-MEM-001-07 | WHEN loading context, the Agent SHALL SELECT from appropriate layer |
| R-MEM-001-08 | The Agent SHALL PRIORITIZE recent session memory over older project memory |
| R-MEM-001-09 | The Agent SHALL NOT EXCEED context window limits |

### R-MEM-002: Step Back / Review KB

The Agent executes KB review on trigger.

| ID | Requirement |
|----|-------------|
| R-MEM-002-01 | WHEN user inputs "step back", the Agent SHALL PAUSE current work |
| R-MEM-002-02 | WHEN user inputs "review kb", the Agent SHALL BEGIN KB review |
| R-MEM-002-03 | The Agent SHALL READ inherited/ directory for precedents |
| R-MEM-002-04 | The Agent SHALL READ planning/ directory for active work |
| R-MEM-002-05 | The Agent SHALL READ .aget/evolution/ for relevant learnings |
| R-MEM-002-06 | The Agent SHALL READ governance/ for boundaries and charter |
| R-MEM-002-07 | The Agent SHALL SUMMARIZE relevant findings |
| R-MEM-002-08 | The Agent SHALL CITE specific precedents found |
| R-MEM-002-09 | IF no precedents found, the Agent SHALL NOTE "novel situation" |
| R-MEM-002-10 | The Agent SHALL RESUME work with loaded context |

### R-MEM-003: Session Handoff

The Agent creates session handoff documents.

| ID | Requirement |
|----|-------------|
| R-MEM-003-01 | WHEN significant session ending, the Agent SHALL CREATE handoff document |
| R-MEM-003-02 | The Agent SHALL WRITE handoff to workspace/ or inherited/ |
| R-MEM-003-03 | The handoff SHALL CONTAIN decisions_made section |
| R-MEM-003-04 | The handoff SHALL CONTAIN pending_items section |
| R-MEM-003-05 | The handoff SHALL CONTAIN context_for_next_session section |
| R-MEM-003-06 | The handoff SHALL CONTAIN files_modified list |
| R-MEM-003-07 | The handoff SHALL CONTAIN artifacts_created list |
| R-MEM-003-08 | WHEN next session starts, the Agent SHALL CHECK for handoff documents |
| R-MEM-003-09 | IF handoff exists, the Agent SHALL LOAD handoff into context |
| R-MEM-003-10 | The Agent SHALL DISPLAY handoff summary to user |

### R-MEM-004: Context Recovery

The Agent recovers context within time limit.

| ID | Requirement |
|----|-------------|
| R-MEM-004-01 | The Agent SHALL COMPLETE context recovery within 2 minutes |
| R-MEM-004-02 | The Agent SHALL LOAD identity from version.json immediately |
| R-MEM-004-03 | The Agent SHALL LOAD North Star from AGENTS.md immediately |
| R-MEM-004-04 | The Agent SHALL CHECK for handoff documents |
| R-MEM-004-05 | IF handoff exists, the Agent SHALL LOAD handoff context |
| R-MEM-004-06 | The Agent SHALL CHECK for PENDING.md |
| R-MEM-004-07 | IF PENDING.md exists, the Agent SHALL LOAD pending items |
| R-MEM-004-08 | The Agent SHALL REPORT context recovery complete |

### R-MEM-005: Learning Capture

The Agent captures learnings as L-docs.

| ID | Requirement |
|----|-------------|
| R-MEM-005-01 | WHEN significant learning identified, the Agent SHALL PROMPT to capture |
| R-MEM-005-02 | IF user approves, the Agent SHALL CREATE L-doc in .aget/evolution/ |
| R-MEM-005-03 | The Agent SHALL GENERATE next L-doc number from existing files |
| R-MEM-005-04 | The L-doc SHALL FOLLOW format: L{NNN}_{snake_case}.md |
| R-MEM-005-05 | The L-doc SHALL CONTAIN Date, Category, Related fields |
| R-MEM-005-06 | The L-doc SHALL CONTAIN Problem section |
| R-MEM-005-07 | The L-doc SHALL CONTAIN Learning section |
| R-MEM-005-08 | The L-doc SHALL CONTAIN Evidence section |
| R-MEM-005-09 | The L-doc SHALL CONTAIN Application section |
| R-MEM-005-10 | The Agent SHALL COMMIT L-doc with descriptive message |

---

## R-VOC: Vocabulary Requirements

### R-VOC-001: Controlled Vocabulary Usage

The Agent uses controlled vocabulary.

| ID | Requirement |
|----|-------------|
| R-VOC-001-01 | The Agent SHALL USE Title_Case for domain objects |
| R-VOC-001-02 | The Agent SHALL USE lowercase for verbs |
| R-VOC-001-03 | The Agent SHALL USE lowercase for prepositions |
| R-VOC-001-04 | The Agent SHALL USE UPPERCASE for constraint keywords |
| R-VOC-001-05 | WHEN writing specifications, the Agent SHALL REFERENCE AGET_CONTROLLED_VOCABULARY.md |
| R-VOC-001-06 | IF term not in vocabulary, the Agent SHALL PROPOSE addition |
| R-VOC-001-07 | The Agent SHALL NOT USE undefined terms in specifications |

### R-VOC-002: SKOS Compliance

The Agent follows SKOS vocabulary structure.

| ID | Requirement |
|----|-------------|
| R-VOC-002-01 | The Agent SHALL STRUCTURE vocabulary entries with prefLabel |
| R-VOC-002-02 | The Agent SHALL INCLUDE definition for each term |
| R-VOC-002-03 | The Agent SHALL SPECIFY broader/narrower relationships |
| R-VOC-002-04 | The Agent SHALL SPECIFY related term relationships |
| R-VOC-002-05 | The Agent SHALL INCLUDE scopeNote for usage context |
| R-VOC-002-06 | The Agent SHALL VALIDATE vocabulary against SKOS patterns |

### R-VOC-003: Vocabulary Validation

The Agent validates vocabulary compliance.

| ID | Requirement |
|----|-------------|
| R-VOC-003-01 | The Agent SHALL RUN validate_vocabulary.py on specifications |
| R-VOC-003-02 | The Agent SHALL REPORT undefined terms found |
| R-VOC-003-03 | The Agent SHALL REPORT incorrect casing violations |
| R-VOC-003-04 | IF validation fails, the Agent SHALL LIST all violations |
| R-VOC-003-05 | The Agent SHALL SUGGEST corrections for violations |
| R-VOC-003-06 | The Agent SHALL NOT APPROVE spec with vocabulary violations |

### R-VOC-004: Term Definition

The Agent defines new terms properly.

| ID | Requirement |
|----|-------------|
| R-VOC-004-01 | WHEN new term needed, the Agent SHALL CHECK if already defined |
| R-VOC-004-02 | IF term exists, the Agent SHALL USE existing definition |
| R-VOC-004-03 | IF term is new, the Agent SHALL WRITE definition |
| R-VOC-004-04 | The definition SHALL BE precise and unambiguous |
| R-VOC-004-05 | The Agent SHALL SPECIFY term type (Entity, Action, State, Event) |
| R-VOC-004-06 | The Agent SHALL ADD term to AGET_CONTROLLED_VOCABULARY.md |
| R-VOC-004-07 | The Agent SHALL COMMIT vocabulary update |

---

## R-CLI: CLI Settings Requirements

### R-CLI-001: Multi-CLI Configuration

The Agent configures multiple CLI tools.

| ID | Requirement |
|----|-------------|
| R-CLI-001-01 | The Agent SHALL CHECK for .claude/ directory |
| R-CLI-001-02 | The Agent SHALL CHECK for .codex/ directory |
| R-CLI-001-03 | The Agent SHALL CHECK for .gemini/ directory |
| R-CLI-001-04 | The Agent SHALL CHECK for .cursor/ directory |
| R-CLI-001-05 | IF template requested, the Agent SHALL CREATE missing CLI directories |
| R-CLI-001-06 | The Agent SHALL NOT COMMIT actual settings files (only templates) |

### R-CLI-002: Claude Code Settings

The Agent manages Claude Code configuration.

| ID | Requirement |
|----|-------------|
| R-CLI-002-01 | The Agent SHALL CHECK for .claude/settings.local.json |
| R-CLI-002-02 | IF .claude/settings.local.json.template exists, the Agent SHALL NOTE template available |
| R-CLI-002-03 | The Agent SHALL VALIDATE settings.local.json format IF exists |
| R-CLI-002-04 | The Agent SHALL ADD .claude/settings.local.json to .gitignore |
| R-CLI-002-05 | The Agent SHALL NOT COMMIT .claude/settings.local.json |

### R-CLI-003: Codex Settings

The Agent manages Codex configuration.

| ID | Requirement |
|----|-------------|
| R-CLI-003-01 | The Agent SHALL CHECK for .codex/config.toml |
| R-CLI-003-02 | IF .codex/config.toml.template exists, the Agent SHALL NOTE template available |
| R-CLI-003-03 | The Agent SHALL VALIDATE config.toml format IF exists |
| R-CLI-003-04 | The Agent SHALL ADD .codex/config.toml to .gitignore |
| R-CLI-003-05 | The Agent SHALL NOT COMMIT .codex/config.toml |

### R-CLI-004: Gemini Settings

The Agent manages Gemini configuration.

| ID | Requirement |
|----|-------------|
| R-CLI-004-01 | The Agent SHALL CHECK for .gemini/settings.json |
| R-CLI-004-02 | IF .gemini/settings.json.template exists, the Agent SHALL NOTE template available |
| R-CLI-004-03 | The Agent SHALL VALIDATE settings.json format IF exists |
| R-CLI-004-04 | The Agent SHALL ADD .gemini/settings.json to .gitignore |
| R-CLI-004-05 | The Agent SHALL CHECK for GEMINI.md symlink |
| R-CLI-004-06 | IF GEMINI.md missing, the Agent SHALL CREATE symlink to AGENTS.md |
| R-CLI-004-07 | IF GEMINI.md is not symlink to AGENTS.md, the Agent SHALL WARN |

### R-CLI-005: Cursor Settings

The Agent manages Cursor configuration.

| ID | Requirement |
|----|-------------|
| R-CLI-005-01 | The Agent SHALL CHECK for .cursor/rules/ directory |
| R-CLI-005-02 | IF .cursor/rules/aget.mdc.template exists, the Agent SHALL NOTE template available |
| R-CLI-005-03 | The Agent SHALL ADD .cursor/rules/*.mdc to .gitignore (except templates) |
| R-CLI-005-04 | The Agent SHALL NOT COMMIT actual .mdc files |

---

## R-PROC: Process Specification Requirements

### R-PROC-001: Process Spec Format

The Agent creates process specifications in YAML.

| ID | Requirement |
|----|-------------|
| R-PROC-001-01 | The Agent SHALL WRITE process specs in YAML format |
| R-PROC-001-02 | The Agent SHALL INCLUDE spec_format_version field |
| R-PROC-001-03 | The Agent SHALL INCLUDE process_id matching pattern ^[a-z][a-z0-9-]*$ |
| R-PROC-001-04 | The Agent SHALL INCLUDE process_name field |
| R-PROC-001-05 | The Agent SHALL INCLUDE status field (pilot, draft, canonical, deprecated) |
| R-PROC-001-06 | The Agent SHALL INCLUDE gates[] array |
| R-PROC-001-07 | Each gate SHALL HAVE id, name, activities[], decision_point |
| R-PROC-001-08 | The Agent SHALL INCLUDE learnings_applied[] section |
| R-PROC-001-09 | The Agent SHALL SAVE process specs to specs/processes/ |

### R-PROC-002: Process Spec Validation

The Agent validates process specifications.

| ID | Requirement |
|----|-------------|
| R-PROC-002-01 | The Agent SHALL VALIDATE process spec against JSON schema |
| R-PROC-002-02 | The Agent SHALL CHECK all required fields present |
| R-PROC-002-03 | The Agent SHALL VALIDATE gate IDs follow pattern G-N |
| R-PROC-002-04 | The Agent SHALL VALIDATE decision_point.next_on_go references valid gate |
| R-PROC-002-05 | IF validation fails, the Agent SHALL REPORT specific errors |
| R-PROC-002-06 | The Agent SHALL NOT APPROVE process spec with validation errors |

### R-PROC-003: Learnings Applied

The Agent tracks learnings in process specs.

| ID | Requirement |
|----|-------------|
| R-PROC-003-01 | The Agent SHALL INCLUDE learnings_applied section in process specs |
| R-PROC-003-02 | Each learning SHALL HAVE id (L-doc reference) |
| R-PROC-003-03 | Each learning SHALL HAVE summary description |
| R-PROC-003-04 | Each learning SHALL HAVE change description showing how applied |
| R-PROC-003-05 | WHEN process fails, the Agent SHALL CHECK for applicable learnings |
| R-PROC-003-06 | IF learning applicable, the Agent SHALL UPDATE learnings_applied |

---

## R-SPEC: Specification Requirements

### R-SPEC-001: Framework Specification

The Agent maintains framework specification per release.

| ID | Requirement |
|----|-------------|
| R-SPEC-001-01 | BEFORE release, the Agent SHALL CREATE AGET_FRAMEWORK_SPEC_vX.Y.md |
| R-SPEC-001-02 | The spec SHALL DEFINE all requirements in EARS format |
| R-SPEC-001-03 | The spec SHALL LIST all components with locations |
| R-SPEC-001-04 | The spec SHALL DESCRIBE all capabilities |
| R-SPEC-001-05 | The spec SHALL DOCUMENT architecture layers |
| R-SPEC-001-06 | The spec SHALL DEFINE conformance levels |
| R-SPEC-001-07 | The Agent SHALL SAVE spec to specs/AGET_FRAMEWORK_SPEC_vX.Y.md |

### R-SPEC-002: Delta Specification

The Agent creates delta specification per release.

| ID | Requirement |
|----|-------------|
| R-SPEC-002-01 | BEFORE release, the Agent SHALL CREATE AGET_DELTA_vX.Y.md |
| R-SPEC-002-02 | The delta SHALL LIST requirements added |
| R-SPEC-002-03 | The delta SHALL LIST requirements modified |
| R-SPEC-002-04 | The delta SHALL LIST requirements removed |
| R-SPEC-002-05 | The delta SHALL LIST components added/modified/removed |
| R-SPEC-002-06 | The delta SHALL INCLUDE migration guide |
| R-SPEC-002-07 | The delta SHALL INCLUDE traceability matrix |
| R-SPEC-002-08 | The Agent SHALL SAVE delta to specs/deltas/AGET_DELTA_vX.Y.md |

### R-SPEC-003: EARS Format

The Agent uses EARS patterns for requirements.

| ID | Requirement |
|----|-------------|
| R-SPEC-003-01 | The Agent SHALL USE "The Agent SHALL" for ubiquitous requirements |
| R-SPEC-003-02 | The Agent SHALL USE "WHEN X, the Agent SHALL" for event-driven |
| R-SPEC-003-03 | The Agent SHALL USE "WHILE X, the Agent SHALL" for state-driven |
| R-SPEC-003-04 | The Agent SHALL USE "WHERE X, the Agent SHALL" for optional |
| R-SPEC-003-05 | The Agent SHALL USE "IF X, the Agent SHALL" for conditional |
| R-SPEC-003-06 | The Agent SHALL USE concrete verbs from vocabulary |
| R-SPEC-003-07 | The Agent SHALL NOT USE vague verbs (support, provide, enable) |
| R-SPEC-003-08 | The Agent SHALL SPECIFY object of action explicitly |

### R-SPEC-004: Requirement Traceability

The Agent traces requirements to artifacts.

| ID | Requirement |
|----|-------------|
| R-SPEC-004-01 | Each requirement SHALL HAVE unique ID (R-CAT-NNN-NN) |
| R-SPEC-004-02 | The Agent SHALL TRACE requirement to L-doc source IF applicable |
| R-SPEC-004-03 | The Agent SHALL TRACE requirement to issue IF applicable |
| R-SPEC-004-04 | The Agent SHALL TRACE requirement to artifact implementing it |
| R-SPEC-004-05 | The Agent SHALL CREATE traceability matrix in delta spec |
| R-SPEC-004-06 | The Agent SHALL VERIFY all requirements have at least one trace |

### R-SPEC-005: Gate Requirement Linkage

The Agent links gates to requirements.

| ID | Requirement |
|----|-------------|
| R-SPEC-005-01 | Each gate in process spec SHALL REFERENCE requirements it satisfies |
| R-SPEC-005-02 | The Agent SHALL LIST "Requirements Satisfied" in gate documentation |
| R-SPEC-005-03 | IF gate has no requirement linkage, the Agent SHALL WARN |
| R-SPEC-005-04 | The Agent SHALL VALIDATE all gate requirements exist in framework spec |
| R-SPEC-005-05 | The Agent SHALL REPORT orphan gates (no requirement linkage) |

---

## 4. Conformance Levels

### 4.1 Minimal Conformance

| Requirement Set | Count |
|-----------------|-------|
| R-CORE-001 (Version Identity) | 10 |
| R-CORE-002 (Entry Point) | 8 |
| R-CORE-003-01 to 03 (Basic Structure) | 3 |
| R-SES-001-01 to 05 (Basic Wake) | 5 |
| **Total** | **26** |

### 4.2 Standard Conformance

Minimal plus:

| Requirement Set | Count |
|-----------------|-------|
| All R-CORE | 32 |
| All R-SES | 44 |
| R-GOV-001 (Gate Discipline) | 12 |
| R-MEM-001 to 003 | 29 |
| **Total** | **~120** |

### 4.3 Full Conformance

All requirements: **~300**

---

## 5. Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.11.0 | 2025-12-23 | Expanded to ~300 behavioral requirements |
| v2.10.0 | 2025-12-13 | Initial framework spec structure |

---

## 6. References

| Document | Purpose |
|----------|---------|
| AGET_CONTROLLED_VOCABULARY.md | Term definitions |
| AGET_SPEC_FORMAT_v1.1.md | EARS patterns |
| AGET_DELTA_v2.11.md | Changes from v2.10 |

---

*AGET_FRAMEWORK_SPEC_v2.11.md — Behavioral Specification for AGET v2.11*
*~300 requirements across 9 categories*
*Created: 2025-12-23*
