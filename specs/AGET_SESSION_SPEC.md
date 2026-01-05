# AGET Session Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Session Lifecycle)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_SESSION_SPEC.md`
**Change Origin**: 5-why analysis on session continuity gaps (G-PRE.3.1)
**Related Specs**: AGET_MEMORY_SPEC, AGET_INSTANCE_SPEC

---

## Abstract

This specification defines the session lifecycle for AGET agents. Sessions are bounded human-AI collaboration periods with initialization (wake-up), operation, and finalization (wind-down) phases. This spec formalizes context recovery, scope validation, and mandatory handoff requirements to ensure session continuity.

## Motivation

Session continuity gaps observed in practice:

1. **Handoff gaps**: Wind-down with pending work but no handoff note → context loss
2. **Context recovery**: Each session starts fresh; no standard for recovering prior state
3. **Scope creep**: Work expands beyond session mandate without re-validation (L342)
4. **Missing protocol**: AGET_MEMORY_SPEC defines vocabulary but not lifecycle requirements

Root cause analysis revealed:
```
Why is session context lost between sessions?
  → No mandatory handoff when pending work exists
Why is handoff not mandatory?
  → wind_down.py uses --create-note as opt-in flag
Why is it opt-in?
  → No specification defines when handoff is required
Why no session lifecycle specification?
  → ROOT CAUSE: AGET_SESSION_SPEC does not exist
```

## Scope

**Applies to**: All AGET agent instances in operational state.

**Defines**:
- Wake-up protocol (session initialization)
- Context recovery patterns
- Session scope validation
- Wind-down protocol (session finalization)
- Mandatory handoff triggers
- Session continuity mechanisms

**Related**:
- AGET_MEMORY_SPEC (six-layer memory model, Session_Memory)
- AGET_INSTANCE_SPEC (instance lifecycle states)

---

## Vocabulary

Domain terms for the SESSION specification:

```yaml
vocabulary:
  meta:
    domain: "session"
    version: "1.0.0"
    inherits: "aget_core"

  session:  # Core session concepts
    Session:
      skos:definition: "Bounded period of human-AI collaboration"
      skos:narrower: ["Active_Session", "Suspended_Session"]
    Session_Lifecycle:
      skos:definition: "Phases of a session: initialization, operation, finalization"
      skos:narrower: ["Wake_Phase", "Operation_Phase", "Wind_Down_Phase"]
    Session_Mandate:
      skos:definition: "Scope defined at session start that bounds permissible work"
      skos:related: ["L342"]
    Session_Context:
      skos:definition: "State information required to operate effectively"
      skos:narrower: ["Prior_Session_Context", "Current_Session_Context"]

  wake:  # Wake-up phase
    Wake_Up_Protocol:
      skos:definition: "Session initialization procedure"
      aget:location: ".aget/patterns/session/wake_up.py"
      skos:related: ["R-SESSION-001"]
    Context_Recovery:
      skos:definition: "Loading relevant prior context into active session"
      skos:example: "Reading handoff notes, checking pending work"
    Identity_Verification:
      skos:definition: "Confirming agent identity and version"

  operation:  # Operation phase
    Session_Scope_Check:
      skos:definition: "Protocol to validate proposed work against session mandate"
      skos:related: ["L342"]
    Session_Scope_Creep:
      skos:definition: "Anti-pattern: gradual expansion beyond mandate without validation"
    Step_Back_Review_KB:
      skos:definition: "Mid-session context refresh pattern"
      skos:related: ["L335"]

  wind_down:  # Wind-down phase
    Wind_Down_Protocol:
      skos:definition: "Session finalization procedure"
      aget:location: ".aget/patterns/session/wind_down.py"
    Session_Handoff:
      skos:definition: "Document enabling session continuity"
      aget:location: "sessions/session_*.md"
    Pending_Work:
      skos:definition: "Work items not completed in current session"
      skos:note: "Detected via planning/*.md with IN PROGRESS status"
    Mandatory_Handoff_Trigger:
      skos:definition: "Condition requiring handoff note creation"
```

---

## Requirements

### CAP-SESSION-001: Wake-Up Protocol

The SYSTEM shall implement wake-up initialization for sessions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-001-01 | ubiquitous | The SYSTEM shall execute wake_up.py as primary initialization method |
| CAP-SESSION-001-02 | conditional | IF wake_up.py fails THEN the SYSTEM shall use CLAUDE.md fallback protocol |
| CAP-SESSION-001-03 | ubiquitous | The SYSTEM shall display agent identity and version in wake-up output |
| CAP-SESSION-001-04 | ubiquitous | The SYSTEM shall execute wake-up silently (no tool call visibility) |
| CAP-SESSION-001-05 | ubiquitous | The SYSTEM shall check for pending work during wake-up |
| CAP-SESSION-001-06 | conditional | IF handoff note exists THEN the SYSTEM shall display handoff summary |

**Enforcement**: wake_up.py, contract tests

#### Wake-Up Output Format

```
**Session: {agent_name}**
**Version**: v{version} ({date})

Purpose: {north_star}

Manages: {managed_repo}
Templates: {count} | Core: aget/

[Pending Work: {pending_items}]   ← IF pending work exists
[Handoff: {handoff_summary}]      ← IF handoff note exists

Ready.
```

### CAP-SESSION-002: Context Recovery

The SYSTEM shall support context recovery mechanisms.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-002-01 | ubiquitous | The SYSTEM shall support "step back. review kb." trigger phrase |
| CAP-SESSION-002-02 | ubiquitous | The SYSTEM shall load retrieval.yaml for context loading rules |
| CAP-SESSION-002-03 | conditional | IF L-doc count > 50 THEN the SYSTEM shall use index.json for navigation |
| CAP-SESSION-002-04 | ubiquitous | The SYSTEM shall cite 3+ precedents before governance decisions |
| CAP-SESSION-002-05 | conditional | IF handoff note exists THEN the SYSTEM shall read it during context recovery |

**Enforcement**: CLAUDE.md "Substantial Change Protocol", retrieval.yaml

#### Context Recovery Pattern (L335)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT RECOVERY PATTERN                      │
│                                                                  │
│   Trigger: "step back. review kb." OR governance decision        │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 1. Check inherited/          (precedents, authority)    │   │
│   │ 2. Check planning/           (active work, PROJECT_PLANs)│   │
│   │ 3. Check evolution/          (learnings, patterns)      │   │
│   │ 4. Check governance/         (charter, mission, scope)  │   │
│   │ 5. Cite 3+ precedents OR note "novel"                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Output: Grounded proposal with precedent citations             │
└─────────────────────────────────────────────────────────────────┘
```

### CAP-SESSION-003: Session Scope Validation

The SYSTEM shall validate session scope to prevent scope creep.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-003-01 | event-driven | WHEN work expands 2+ steps from mandate, the SYSTEM shall validate scope |
| CAP-SESSION-003-02 | ubiquitous | The SYSTEM shall classify work as Research, Preparation, or Execution |
| CAP-SESSION-003-03 | conditional | IF execution beyond mandate THEN the SYSTEM shall create handoff and defer |
| CAP-SESSION-003-04 | prohibited | The SYSTEM shall NOT execute work outside session mandate without approval |
| CAP-SESSION-003-05 | ubiquitous | The SYSTEM shall use "This informs a future session" when deferring |

**Enforcement**: L342 (Session Scope Validation), CLAUDE.md protocol

#### Scope Validation Decision Matrix (L342)

```
┌─────────────────────────────────────────────────────────────────┐
│                 SESSION SCOPE VALIDATION (L342)                  │
├─────────────────┬────────────────┬──────────────────────────────┤
│ Proposed Work   │ Within Mandate │ Action                       │
├─────────────────┼────────────────┼──────────────────────────────┤
│ Research        │ Yes            │ Proceed                      │
│ Research        │ No             │ Flag, get approval           │
│ Preparation     │ Yes            │ Proceed                      │
│ Preparation     │ No             │ Document as FINDINGS, defer  │
│ Execution       │ Yes            │ Proceed with governance      │
│ Execution       │ No             │ **STOP** — handoff, defer    │
└─────────────────┴────────────────┴──────────────────────────────┘
```

### CAP-SESSION-004: Wind-Down Protocol

The SYSTEM shall implement wind-down finalization for sessions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-004-01 | ubiquitous | The SYSTEM shall execute wind_down.py for session finalization |
| CAP-SESSION-004-02 | ubiquitous | The SYSTEM shall check for pending work during wind-down |
| CAP-SESSION-004-03 | ubiquitous | The SYSTEM shall check for uncommitted changes during wind-down |
| CAP-SESSION-004-04 | ubiquitous | The SYSTEM shall display wind-down summary |
| CAP-SESSION-004-05 | conditional | IF Mandatory_Handoff_Trigger THEN the SYSTEM shall create handoff note |

**Enforcement**: wind_down.py, contract tests

#### Wind-Down Output Format

```
============================================================
SESSION WIND DOWN
============================================================

Pending Work:
  - PROJECT_PLAN_v3.0.0-beta.1_implementation.md  ← triggers handoff

Uncommitted Changes:
  [list or None]

Session Note: session_2025-12-27_1430.md  ← created if trigger

============================================================
Session ended.
```

### CAP-SESSION-005: Mandatory Handoff Triggers

The SYSTEM shall create handoff notes when triggers are met.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-005-01 | conditional | IF pending PROJECT_PLAN with IN PROGRESS status THEN the SYSTEM shall create handoff |
| CAP-SESSION-005-02 | conditional | IF session scope deferred execution THEN the SYSTEM shall create handoff |
| CAP-SESSION-005-03 | conditional | IF uncommitted changes exist THEN the SYSTEM shall warn in wind-down |
| CAP-SESSION-005-04 | optional | WHERE user requests no handoff, the SYSTEM may skip with --no-handoff flag |
| CAP-SESSION-005-05 | ubiquitous | The handoff note shall include pending work and next steps |

**Enforcement**: wind_down.py (must check triggers, auto-create if met)

#### Mandatory Handoff Trigger Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                  MANDATORY HANDOFF TRIGGERS                      │
├───────────────────────────────────┬─────────────────────────────┤
│ Condition                         │ Action                      │
├───────────────────────────────────┼─────────────────────────────┤
│ PROJECT_PLAN with IN PROGRESS     │ MANDATORY handoff           │
│ Execution deferred per L342       │ MANDATORY handoff           │
│ Uncommitted changes               │ WARNING (user decision)     │
│ No pending work                   │ Optional (--create-note)    │
│ User requests --no-handoff        │ Skip with acknowledgment    │
└───────────────────────────────────┴─────────────────────────────┘
```

### CAP-SESSION-006: Session Handoff Format

The SYSTEM shall use standard handoff note format.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SESSION-006-01 | ubiquitous | The handoff note shall be named session_{date}_{time}.md |
| CAP-SESSION-006-02 | ubiquitous | The handoff note shall be placed in sessions/ directory |
| CAP-SESSION-006-03 | ubiquitous | The handoff note shall include session metadata frontmatter |
| CAP-SESSION-006-04 | ubiquitous | The handoff note shall include Pending Work section |
| CAP-SESSION-006-05 | optional | WHERE notes provided, the handoff shall include Notes section |

**Enforcement**: wind_down.py, handoff template

#### Handoff Note Template

```markdown
---
# Session Metadata Standard v1.0
session_id: session_{date}_{time}
date: {YYYY-MM-DD}
aget_version: "{version}"
agent_name: "{agent_name}"
session_type: operational

# Outcome Tracking
status: {completed|suspended|deferred}
pending_work: {true|false}
---

# Session: {date}

## Summary

{Brief description of what was accomplished}

## Pending Work

- [ ] {Pending item 1 with context}
- [ ] {Pending item 2 with context}

## Next Steps

1. {Recommended first action for next session}
2. {Recommended second action}

## Notes

{User-provided session notes}

---

*Session ended: {datetime}*
*Handoff created: mandatory (pending work detected)*
```

---

## Authority Model

```yaml
authority:
  applies_to: "agent_sessions"

  governed_by:
    spec: "AGET_SESSION_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    autonomous:
      - "execute wake_up.py"
      - "execute wind_down.py"
      - "create handoff notes"
      - "validate session scope"
      - "perform context recovery"

    requires_approval:
      - action: "execute work beyond session mandate"
        approver: "user"
      - action: "skip mandatory handoff"
        approver: "user (with --no-handoff acknowledgment)"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-SESSION-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT execute work beyond session mandate WITHOUT explicit approval"
      rationale: "Prevents session scope creep (L342)"

    - id: "INV-SESSION-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT wind down with pending work WITHOUT handoff note"
      rationale: "Ensures session continuity"

    - id: "INV-SESSION-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT skip context recovery for governance decisions"
      rationale: "Precedent-based decisions require KB review (L335)"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "sessions/"
      purpose: "Session handoff notes"

  required_files:
    - path: ".aget/patterns/session/wake_up.py"
      purpose: "Wake-up protocol implementation"
      requirements: ["CAP-SESSION-001"]

    - path: ".aget/patterns/session/wind_down.py"
      purpose: "Wind-down protocol implementation"
      requirements: ["CAP-SESSION-004", "CAP-SESSION-005"]

  configuration_files:
    - path: ".aget/memory/retrieval.yaml"
      purpose: "Context loading rules for recovery"
```

---

## Session Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SESSION LIFECYCLE                                │
│                                                                          │
│    ┌──────────────────────────────────────────────────────────────┐     │
│    │                      WAKE PHASE                               │     │
│    │  1. Execute wake_up.py                                        │     │
│    │  2. Display identity + version                                │     │
│    │  3. Check pending work → display if exists                    │     │
│    │  4. Check handoff notes → display summary                     │     │
│    │  5. Output: "Ready."                                          │     │
│    └──────────────────────────────────────────────────────────────┘     │
│                              │                                           │
│                              ▼                                           │
│    ┌──────────────────────────────────────────────────────────────┐     │
│    │                    OPERATION PHASE                            │     │
│    │                                                               │     │
│    │  Session Mandate Established                                  │     │
│    │         │                                                     │     │
│    │         ▼                                                     │     │
│    │  ┌─────────────────────────────────────────────────┐         │     │
│    │  │ Work Request                                    │         │     │
│    │  └────────────────────┬────────────────────────────┘         │     │
│    │                       │                                       │     │
│    │         ┌─────────────┴─────────────┐                        │     │
│    │         │ Scope Expanded 2+ steps?  │                        │     │
│    │         └─────────────┬─────────────┘                        │     │
│    │            YES        │          NO                          │     │
│    │                       ▼                                       │     │
│    │         ┌─────────────────────────────────────┐              │     │
│    │         │ L342 Scope Check                    │              │     │
│    │         │ - Classify: Research/Prep/Execution │              │     │
│    │         │ - Compare to mandate                │              │     │
│    │         └────────────┬────────────────────────┘              │     │
│    │                      │                                        │     │
│    │       Within Mandate │ Out of Mandate                        │     │
│    │              ↓       │                                        │     │
│    │         Proceed      │──→ Defer + Handoff                    │     │
│    │              │                                                │     │
│    │              ▼                                                │     │
│    │  ┌─────────────────────────────────────────────────┐         │     │
│    │  │ Mid-Session Context Recovery                    │         │     │
│    │  │ Trigger: "step back. review kb."                │         │     │
│    │  │ Action: Review inherited/, planning/, evolution/│         │     │
│    │  └─────────────────────────────────────────────────┘         │     │
│    └──────────────────────────────────────────────────────────────┘     │
│                              │                                           │
│                              ▼                                           │
│    ┌──────────────────────────────────────────────────────────────┐     │
│    │                    WIND-DOWN PHASE                            │     │
│    │  1. Execute wind_down.py                                      │     │
│    │  2. Check pending work                                        │     │
│    │  3. Check uncommitted changes                                 │     │
│    │  4. IF Mandatory_Handoff_Trigger → create handoff note        │     │
│    │  5. Display summary                                           │     │
│    │  6. Output: "Session ended."                                  │     │
│    └──────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Validation

```bash
# Test wake-up protocol
python3 .aget/patterns/session/wake_up.py -v

# Test wind-down with mandatory handoff
python3 .aget/patterns/session/wind_down.py --create-note

# Contract tests
python3 -m pytest tests/test_session_protocol.py -v
```

---

## Theoretical Basis

Session lifecycle is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Transaction Semantics** | Sessions as atomic units with commit (handoff) or rollback |
| **Context-Dependent Memory** | Wake-up reconstructs context; wind-down preserves it |
| **Cognitive Load Theory** | Session scope limits prevent overload; context recovery reduces re-learning |
| **Cybernetics** | Feedback loops: scope validation, context recovery, handoff |

```yaml
theoretical_basis:
  primary: "Transaction Semantics"
  secondary:
    - "Context-Dependent Memory"
    - "Cognitive Load Theory"
    - "Cybernetics (feedback loops)"
  rationale: >
    Sessions are treated as transactions in a collaboration database.
    Wake-up begins the transaction by loading context. Wind-down commits
    the transaction by creating handoff artifacts. Pending work without
    handoff is equivalent to an uncommitted transaction - state is lost.
    Scope validation prevents transaction bloat. Context recovery reduces
    the cognitive cost of session restart.
  references:
    - "L335_memory_architecture_principles.md"
    - "L342_session_scope_validation.md"
    - "AGET_MEMORY_SPEC.md"
```

---

## Shell Integration Pattern (L452)

Users can streamline session initialization using shell aliases. This pattern provides CLI-agnostic agent launching via `.zshrc` configuration.

```zsh
# Core function
aget() {
  local dir="$1"; shift
  cd "$dir" || return 1
  claude "Wake up. Focus on: $*"
}

# Agent aliases
alias supervisor='aget ~/github/private-supervisor-AGET'
```

See `docs/SHELL_INTEGRATION.md` for full setup guide including:
- Multi-CLI support (Claude Code, Codex, Gemini, Aider)
- Credential isolation patterns (L189)
- Alias generator script

---

## References

- AGET_MEMORY_SPEC.md (Session_Memory layer, context patterns)
- AGET_INSTANCE_SPEC.md (instance lifecycle states)
- L335: Memory Architecture Principles
- L342: Session Scope Validation
- L375: Session Scope Evolution Pattern
- L452: Shell Orchestration Pattern
- docs/SHELL_INTEGRATION.md (shell setup guide)

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "wake_up.py"
    - "wind_down.py"
    - "CLAUDE.md session protocol"
  source_learnings:
    - "L335"
    - "L342"
    - "L375"
  trigger: "5-why analysis on session continuity gaps (G-PRE.3.1)"
  rationale: "Session lifecycle was informal; no specification existed for handoff requirements"
```

---

*AGET Session Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Lifecycle Management - G-PRE.3.1*
*"Sessions are transactions; handoffs are commits."*
