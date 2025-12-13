# AGET Specification Format v1.1

**Version**: 1.1.0
**Date**: 2025-12-01
**Status**: CANONICAL
**Location**: aget/specs/AGET_SPEC_FORMAT_v1.1.md

---

## Purpose

This document defines the canonical format for AGET specifications. All template specifications, capability definitions, and formal requirements MUST follow this format.

---

## Grammar Structure

### Core Pattern

```
[PATTERN] SYSTEM shall <verb> <Object> [preposition] [Constraint]
```

The PATTERN prefix specifies temporal/conditional behavior using EARS (Easy Approach to Requirements Syntax).

---

## EARS Temporal Patterns

EARS provides 5 patterns that eliminate ambiguity about when/how requirements apply:

### 1. Ubiquitous (Always-True)

**Format**: `The SYSTEM shall <requirement>`

**When to use**: Continuous, always-active requirements

**Examples**:
```
The SYSTEM shall maintain Session_State across interactions
The SYSTEM shall enforce Configuration_Size_Limit of 40k characters
The SYSTEM shall track Learning_Documents in evolution directory
```

### 2. Event-Driven (WHEN)

**Format**: `WHEN <trigger> the SYSTEM shall <requirement>`

**When to use**: Requirements triggered by specific events

**Examples**:
```
WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol
WHEN Session_End is signaled, the SYSTEM shall execute Wind_Down_Protocol
WHEN Configuration_Change is detected, the SYSTEM shall validate Version_Json
```

### 3. State-Driven (WHILE)

**Format**: `WHILE <state> the SYSTEM shall <requirement>`

**When to use**: Requirements active during specific states

**Examples**:
```
WHILE in Planning_Mode, the SYSTEM shall await Gate_Approval before execution
WHILE Processing_Large_Codebase, the SYSTEM shall display Progress_Indicator
WHILE in Read_Only_Mode, the SYSTEM shall prevent Write_Operations
```

### 4. Optional (WHERE)

**Format**: `WHERE <feature> the SYSTEM shall <requirement>`

**When to use**: Context-specific requirements (configurations, features)

**Examples**:
```
WHERE Instance_Type is AGET, the SYSTEM shall permit Action_Capabilities
WHERE Portfolio_Assignment exists, the SYSTEM shall enforce Portfolio_Boundaries
WHERE Intelligence_Enabled is true, the SYSTEM shall track Learning_Documents
```

### 5. Conditional (IF...THEN)

**Format**: `IF <condition> THEN the SYSTEM shall <requirement>`

**When to use**: Logical conditions with consequences

**Examples**:
```
IF Configuration_Size exceeds 40k THEN the SYSTEM shall trigger Size_Warning
IF Gate_Approval is NOGO THEN the SYSTEM shall halt Execution
IF Breaking_Change is detected THEN the SYSTEM shall require Migration_Guide
```

---

## Pattern Selection Guide

| Pattern | When Requirement Applies | Example Use Case |
|---------|-------------------------|------------------|
| **Ubiquitous** | Always (continuous) | Core functionality, invariants |
| **WHEN** | After specific event | Protocol triggers, handlers |
| **WHILE** | During specific state | Mode-specific behavior |
| **WHERE** | Specific configuration | Optional features, instance types |
| **IF...THEN** | Logical condition true | Thresholds, conditional logic |

**Default**: If unsure, use **ubiquitous**. It's always-active and least ambiguous.

---

## Language Elements

### Verbs (lowercase)

```
# Analysis
read, search, analyze, identify, detect, recognize

# Transformation
transform, convert, migrate, normalize, update

# Persistence
store, retrieve, persist, cache, track

# Communication
display, render, report, present, output

# Control
execute, invoke, trigger, halt, prevent

# Validation
validate, verify, check, enforce, ensure
```

### Prepositions/Connectors (lowercase)

```
from, to, as, with, within, containing
when, upon, after, before, during
matching, excluding, including, across
```

### Constraint Keywords (UPPERCASE)

```
WITHIN <time>           # Temporal constraint
WITHOUT <consequence>   # Exclusion constraint
MAINTAINING <property>  # Invariant constraint
EXCEEDING <threshold>   # Threshold constraint
BEFORE <event>          # Sequencing constraint
AFTER <event>           # Sequencing constraint
```

---

## Controlled Vocabulary (Title_Case)

All domain objects use Title_Case with underscores. See `AGET_CONTROLLED_VOCABULARY.md` for the complete registry.

### Framework Identity
```
Fleet_Agent              # Agent registered in fleet
Template                 # Reusable agent archetype
Instance                 # Concrete agent from template
Portfolio                # Organizational grouping
Supervisor               # Coordinating agent
```

### Configuration Objects
```
Version_Json             # .aget/version.json file
Agents_Md                # AGENTS.md configuration file
Configuration_Size       # Character count of config
Fleet_State              # Fleet membership registry
```

### Session Objects
```
Wake_Protocol            # Session initialization
Wind_Down_Protocol       # Session finalization
Session_State            # Current session context
Learning_Document        # L-series knowledge capture
```

---

## Specification File Structure

### YAML Format

```yaml
spec:
  id: SPEC-{NAME}
  version: "X.Y.Z"
  maturity: bootstrapping | minimal | standard | exemplary
  format_version: "1.1"
  description: "Brief description"
  system_name: "{template-or-agent-name}"
  changelog:
    - version: "X.Y.Z"
      date: "YYYY-MM-DD"
      changes: "Description of changes"

capabilities:
  CAP-001:
    domain: {domain_name}
    statement: "EARS-formatted requirement statement"
    pattern: ubiquitous | event-driven | state-driven | optional | conditional
    trigger: {event}           # For event-driven
    precondition: {state}      # For optional/conditional
    inputs: ["input1", "input2"]
    outputs: ["output1"]
    enforcement: "How this is enforced (contract test, documentation, etc.)"
    notes: "Additional context"

dependencies:
  CAP-002: [CAP-001]          # CAP-002 depends on CAP-001
```

### Maturity Levels

| Level | Definition | Requirements |
|-------|------------|--------------|
| **bootstrapping** | Initial creation | Basic structure, <10 capabilities |
| **minimal** | Functional | Core capabilities defined, basic tests |
| **standard** | Production-ready | Complete capabilities, contract tests |
| **exemplary** | Reference implementation | Full documentation, examples, guides |

---

## Contract Test Integration

Each capability SHOULD have an associated contract test:

```yaml
CAP-001:
  domain: session_protocol
  statement: "WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol"
  enforcement: "Contract test test_wake_protocol_execution"
```

Test naming convention: `test_{capability_name}` or `test_{domain}_{behavior}`

---

## Benefits of This Format

1. **Unambiguous Parsing** - EARS patterns eliminate temporal ambiguity
2. **Machine Readable** - YAML structure enables tooling
3. **Human Readable** - Natural language statements
4. **Traceable** - Capability IDs enable tracking
5. **Testable** - Direct mapping to contract tests
6. **Versionable** - Clear changelog and maturity tracking

---

## Migration from Prose Requirements

When converting prose requirements to EARS format:

1. Identify the temporal context (always? when? while? if?)
2. Select appropriate EARS pattern
3. Extract the core action (verb + object)
4. Identify constraints
5. Use controlled vocabulary for domain objects

**Before** (prose):
> "The agent should read files when asked"

**After** (EARS):
```
WHEN File_Read_Request is received, the SYSTEM shall retrieve File_Content from specified File_Path
```

---

## References

- EARS: Easy Approach to Requirements Syntax (Mavin et al., 2009)
- AGET_CONTROLLED_VOCABULARY.md - Canonical vocabulary registry
- AGET_VERSIONING_CONVENTIONS.md - Version numbering rules

---

*AGET_SPEC_FORMAT_v1.1.md — Canonical specification format for AGET framework*
