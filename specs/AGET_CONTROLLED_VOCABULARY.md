# AGET Controlled Vocabulary

**Version**: 1.1.0
**Date**: 2025-12-21
**Status**: CANONICAL
**Location**: aget/specs/AGET_CONTROLLED_VOCABULARY.md
**Conformance**: Level 2 (Standard) per [AGET_GLOSSARY_STANDARD_SPEC_v1.0.md](AGET_GLOSSARY_STANDARD_SPEC_v1.0.md)
**Foundation**: W3C SKOS + AGET Extensions (per ADR-001)

---

## Purpose

This document defines the canonical vocabulary for AGET framework specifications. All specifications MUST use these terms with the defined meanings.

> **Standard Reference**: See [AGET_GLOSSARY_STANDARD_SPEC_v1.0.md](AGET_GLOSSARY_STANDARD_SPEC_v1.0.md) for vocabulary format patterns, conformance levels, and validation rules.

---

## Casing Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Domain Objects | Title_Case | `Fleet_Agent`, `Version_Json` |
| Verbs | lowercase | `read`, `execute`, `validate` |
| Prepositions | lowercase | `from`, `to`, `within` |
| Constraint Keywords | UPPERCASE | `WITHIN`, `WITHOUT`, `BEFORE` |
| Capability IDs | CAPS-NNN | `CAP-001`, `CAP-042` |
| Spec IDs | SPEC-NAME | `SPEC-WORKER-TEMPLATE` |

---

## Core Framework Terms

### Identity Terms

| Term | Definition |
|------|------------|
| `AGET` | Agent configuration & lifecycle management framework |
| `aget` | Lowercase form; also denotes read-only instance type |
| `AGET` (caps) | Action-taking instance type with write permissions |
| `Fleet_Agent` | Agent registered in Fleet_State under Supervisor coordination |
| `Template` | Reusable agent archetype (e.g., template-worker-aget) |
| `Instance` | Concrete agent created from a Template |
| `Core_Template` | Fleet role template (worker, advisor, supervisor) |
| `Specialized_Template` | Task-specific template (spec-engineer, developer) |

### Organizational Terms

| Term | Definition |
|------|------------|
| `Portfolio` | Organizational grouping (e.g., ccb, main, legalon) |
| `Fleet` | Collection of agents under supervisor coordination |
| `Fleet_State` | Canonical registry of fleet membership (FLEET_STATE.yaml) |
| `Supervisor` | Agent responsible for fleet coordination |
| `Principal` | Human operator with ultimate authority |

### Instance Types

| Term | Definition |
|------|------------|
| `Instance_Type` | Capability classification: aget, AGET, coordinator |
| `aget` (type) | Read-only instance; analysis and advisory only |
| `AGET` (type) | Action-taking instance; can modify files and execute |
| `Coordinator` | Special type for fleet coordination (supervisor) |

---

## Configuration Terms

### File Objects

| Term | Definition |
|------|------------|
| `Version_Json` | Identity configuration file (.aget/version.json) |
| `Agents_Md` | Behavior specification file (AGENTS.md) |
| `Claude_Md` | Symlink to Agents_Md for Claude Code compatibility |
| `Fleet_State_Yaml` | Fleet membership registry |
| `Configuration` | Combined Version_Json + Agents_Md |

### Configuration Fields

| Term | Definition |
|------|------------|
| `aget_version` | Framework version (e.g., "2.9.0") |
| `agent_name` | Full agent identifier (e.g., "private-example-aget") |
| `instance_type` | Capability level (aget/AGET/coordinator) |
| `domain` | Agent's area of operation |
| `portfolio` | Portfolio assignment |
| `managed_by` | Supervisor reference |
| `intelligence_enabled` | Learning tracking active |
| `collaboration_enabled` | Multi-agent coordination active |

### Size Management

| Term | Definition |
|------|------------|
| `Configuration_Size` | Character count of configuration files |
| `Configuration_Size_Limit` | Maximum allowed size (40,000 characters) |
| `Size_Warning` | Alert when approaching limit |
| `Size_Violation` | Error when exceeding limit |

---

## Session Protocol Terms

### Protocol Names

| Term | Definition |
|------|------------|
| `Wake_Protocol` | Session initialization ritual |
| `Wake_Command` | User command "wake up" |
| `Study_Up_Protocol` | Deep context loading |
| `Wind_Down_Protocol` | Session finalization |
| `Sign_Off_Protocol` | Complete session closure |

### Session Objects

| Term | Definition |
|------|------------|
| `Session_State` | Current session context and history |
| `Session_Summary` | Condensed session output |
| `Session_Log` | Detailed session record |
| `Silent_Execution` | Protocol execution without showing tool calls |

---

## Evolution Terms

### Learning Objects

| Term | Definition |
|------|------------|
| `Learning_Document` | L-series knowledge capture (e.g., L187) |
| `L_Doc` | Abbreviation for Learning_Document |
| `Evolution_Directory` | Storage for learning (.aget/evolution/) |
| `Learning_Registry` | Index of all L-docs |

### Evolution Actions

| Term | Definition |
|------|------------|
| `Learning_Capture` | Recording new insight as L-doc |
| `Pattern_Extraction` | Identifying reusable pattern from experience |
| `Knowledge_Migration` | Moving learning between agents |

---

## Governance Terms

### Planning Objects

| Term | Definition |
|------|------------|
| `Project_Plan` | Formal gated execution plan |
| `Gate` | Decision checkpoint in plan |
| `Gate_Approval` | GO/NOGO decision at gate |
| `Tier` | Grouping of gates by activation trigger |

### Governance Actions

| Term | Definition |
|------|------------|
| `Substantial_Change` | Change requiring formal planning |
| `Gate_Override` | Explicit approval to skip gating |
| `Plan_Approval` | Principal acceptance of plan |

---

## Capability Terms

### Capability Types

| Term | Definition |
|------|------------|
| `Analysis_Capability` | Read, search, fetch operations |
| `Action_Capability` | Write, execute, modify operations |
| `Coordination_Capability` | Multi-agent orchestration |
| `Evolution_Capability` | Learning and adaptation |

### Specific Capabilities

| Term | Definition |
|------|------------|
| `File_Read` | Read file contents |
| `Pattern_Search` | Search for patterns in codebase |
| `Web_Fetch` | Retrieve web content |
| `File_Write` | Create or modify files |
| `Command_Execute` | Run shell commands |
| `Gate_Coordination` | Manage gated execution |

---

## Specification Terms

### Spec Objects

| Term | Definition |
|------|------------|
| `Specification` | Formal requirements document |
| `Capability_Statement` | EARS-formatted requirement |
| `Contract_Test` | Automated specification verification |
| `Spec_Maturity` | Completeness level (bootstrapping→exemplary) |

### EARS Patterns

| Term | Definition |
|------|------------|
| `Ubiquitous_Pattern` | Always-active requirement |
| `Event_Driven_Pattern` | WHEN-triggered requirement |
| `State_Driven_Pattern` | WHILE-active requirement |
| `Optional_Pattern` | WHERE-conditional requirement |
| `Conditional_Pattern` | IF-THEN requirement |

---

## Release Terms

| Term | Definition |
|------|------------|
| `Release` | Tagged version publication |
| `Version_Bump` | Increment version number |
| `Changelog` | Record of changes per version |
| `Deep_Release_Notes` | Narrative documentation beyond changelog |
| `Breaking_Change` | Change requiring migration |
| `Migration_Guide` | Instructions for version upgrade |

---

## Validation Terms

| Term | Definition |
|------|------------|
| `Vocabulary_Compliance` | Using only defined terms |
| `Format_Compliance` | Following EARS patterns |
| `Contract_Compliance` | Passing contract tests |
| `Size_Compliance` | Within configuration limits |

---

## Naming Conventions

> **Full Specification**: See [AGET_FILE_NAMING_CONVENTIONS.md](AGET_FILE_NAMING_CONVENTIONS.md) for complete patterns, decision tree, and anti-patterns.

### Quick Reference

| Artifact Type | Pattern | Example |
|---------------|---------|---------|
| Agent directories | `{visibility}-{identifier}-{type}` | `private-supervisor-AGET` |
| Specs | `{NAME}_SPEC_v{M}.{m}.yaml` | `WORKER_TEMPLATE_SPEC_v1.0.yaml` |
| PROJECT_PLANs | `PROJECT_PLAN_{name}_v{M}.{m}.md` | `PROJECT_PLAN_file_naming_v1.0.md` |
| ADRs | `ADR-{NNN}-{kebab-case}.md` | `ADR-001-initial-architecture.md` |
| L-docs | `L{NNN}_{snake_case}.md` | `L338_gate_verification.md` |
| Sessions | `SESSION_{YYYY-MM-DD}_{name}.md` | `SESSION_2025-12-20_research.md` |
| SOPs | `SOP_{snake_case}.md` | `SOP_release_process.md` |
| Python code | `{snake_case}.py` | `validate_file_naming.py` |

### Case Conventions

| Element | Convention | Example |
|---------|------------|---------|
| TYPE prefix | SCREAMING_CASE | `PROJECT_PLAN`, `SPEC` |
| Descriptive name (files) | snake_case | `file_naming_conventions` |
| Descriptive name (dirs) | kebab-case | `private-supervisor-AGET` |
| Version | `_v{M}.{m}` | `_v1.0`, `_v2.1-alpha` |

---

## Usage in Specifications

### Correct Usage

```yaml
# Good: Using controlled vocabulary
CAP-001:
  statement: "WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol"

CAP-002:
  statement: "The SYSTEM shall enforce Configuration_Size_Limit of 40k characters"
```

### Incorrect Usage

```yaml
# Bad: Using undefined terms
CAP-001:
  statement: "When user says wake up, the system should start"  # Not EARS format

CAP-002:
  statement: "The SYSTEM shall limit config to 40k"  # "config" not in vocabulary
```

---

## Extending the Vocabulary

To add new terms:

1. Identify the category (Identity, Configuration, Session, etc.)
2. Define the term with Title_Case
3. Write clear definition
4. Submit PR to aget/specs/AGET_CONTROLLED_VOCABULARY.md
5. Update dependent specifications

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2025-12-21 | Added SKOS foundation reference, conformance level declaration |
| 1.0.0 | 2025-12-01 | Initial release (v2.9 Core Specs Gate 2) |

---

*AGET_CONTROLLED_VOCABULARY.md — Canonical vocabulary for AGET framework*
*Conformance: Level 2 (Standard) per AGET_GLOSSARY_STANDARD_SPEC_v1.0.md*
