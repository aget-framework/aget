# AGET Template Structure Guide

**Version**: 2.0.0
**Date**: 2026-01-11
**Status**: CANONICAL
**Location**: aget/docs/TEMPLATE_STRUCTURE_GUIDE.md
**Framework Version**: 3.3.0

---

## Overview

This guide defines the standard directory structure and file organization for AGET templates and agent instances. Updated for v3.3 to include shell integration, specification structure, and vocabulary requirements.

---

## Standard Template Structure (v3.3)

```
template-{type}-aget/
├── .aget/                          # AGET framework directory
│   ├── version.json                # Agent identity and configuration
│   ├── evolution/                  # Learning documents (L-series)
│   │   ├── L001_example.md
│   │   └── ...
│   ├── specs/                      # Specifications (if applicable)
│   │   └── {TEMPLATE}_SPEC_v1.0.yaml
│   ├── docs/                       # Internal documentation
│   │   └── ...
│   ├── architecture/               # ADRs (optional)
│   │   └── ADR-001-example.md
│   └── tests/                      # Contract tests (optional)
│       └── contract_tests.py
├── specs/                          # Template specifications (v3.3)
│   ├── {Type}_SPEC.md              # Capability specification
│   └── {Type}_VOCABULARY.md        # Domain vocabulary
├── shell/                          # Shell integration (v3.3, CAP-TPL-014)
│   ├── {type}_profile.zsh          # Shell profile with helpers
│   └── README.md                   # Shell integration documentation
├── AGENTS.md                       # Agent behavior specification
├── CLAUDE.md -> AGENTS.md          # Symlink for Claude Code
├── README.md                       # Public documentation
├── CHANGELOG.md                    # Version history
├── manifest.yaml                   # 5D composition manifest
├── docs/                           # Extended documentation (optional)
│   └── ...
└── scripts/                        # Utility scripts (optional)
    └── ...
```

---

## Required Files

### .aget/version.json

Identity and configuration file.

```json
{
  "aget_version": "2.9.0",
  "created": "2025-12-01",
  "updated": "2025-12-01",
  "template": "worker",
  "agent_name": "template-worker-aget",
  "instance_type": "template",
  "domain": "worker-template",
  "portfolio": null,
  "managed_by": "none",
  "intelligence_enabled": true,
  "collaboration_enabled": true,
  "patterns": {
    "session": "1.1.0",
    "documentation": "1.0.0"
  }
}
```

**Required Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `aget_version` | string | Framework version (semver) |
| `agent_name` | string | Full agent identifier |
| `instance_type` | string | aget, AGET, template, or coordinator |
| `domain` | string | Agent's area of operation |
| `created` | string | Creation date (YYYY-MM-DD) |

**Optional Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `updated` | string | Last update date |
| `template` | string | Base template type |
| `portfolio` | string | Portfolio assignment |
| `managed_by` | string | Supervisor reference |
| `intelligence_enabled` | boolean | Learning tracking active |
| `collaboration_enabled` | boolean | Multi-agent coordination |
| `patterns` | object | Pattern version tracking |
| `migration_history` | array | Version migration log |

### AGENTS.md

Agent behavior specification. This is the primary configuration file that defines how the agent operates.

**Required Sections**:

```markdown
# Agent Configuration

@aget-version: 2.9.0

## Substantial Change Protocol
[Required for all agents]

## Agent Identity
[Name, Type, Domain, Portfolio, Manages, Managed By]

## Purpose
[Mission statement]

## Session Protocol
### Wake Up Protocol
### Wind Down Protocol

## [Domain-Specific Sections]
[Vary by template type]

---
*Footer with agent identifier*
```

### CLAUDE.md

MUST be a symlink to AGENTS.md:

```bash
ln -s AGENTS.md CLAUDE.md
```

This ensures Claude Code reads the correct configuration.

---

## Optional Directories

### .aget/evolution/

Learning documents captured during agent operation.

**Naming Convention**: `L{NNN}_{snake_case_description}.md`

```
.aget/evolution/
├── L001_initial_setup.md
├── L002_workflow_discovery.md
└── L187_wake_protocol_silent_execution.md
```

**L-doc Structure**:

```markdown
# L{NNN}: {Title}

**Date**: YYYY-MM-DD
**Context**: {session or source}
**Status**: ACTIVE | SUPERSEDED

---

## Observation
{What was observed}

## Learning
{What was learned}

## Protocol
{How to apply this learning}

## Impact
{Before/after comparison}

---
*{Pattern statement}*
```

### .aget/specs/

Formal specifications for the template or agent.

**Naming Convention**: `{NAME}_SPEC_v{X.Y}.yaml`

```
.aget/specs/
├── WORKER_TEMPLATE_SPEC_v1.0.yaml
└── CUSTOM_CAPABILITY_SPEC_v1.0.yaml
```

### .aget/architecture/

Architectural Decision Records.

**Naming Convention**: `ADR-{NNN}-{kebab-case-title}.md`

```
.aget/architecture/
├── ADR-001-initial-architecture.md
└── ADR-012-migration-strategy.md
```

### .aget/tests/

Contract tests for specification compliance.

```python
# contract_tests.py
def test_version_json_required_fields():
    """Verify all required fields present."""
    pass

def test_claude_md_is_symlink():
    """Verify CLAUDE.md is symlink to AGENTS.md."""
    pass
```

---

## Instance vs Template

### Template Structure

Templates are reference implementations. They have:

- `instance_type: "template"`
- `managed_by: "none"`
- Complete documentation
- Example configurations

### Instance Structure

Instances are deployed agents. They have:

- `instance_type: "aget"` or `"AGET"`
- `managed_by: "{supervisor-agent}"`
- Portfolio assignment
- Customized AGENTS.md

**Instance Creation from Template**:

```bash
# Clone template
cp -r template-worker-aget private-myagent-aget

# Update version.json
# - Change agent_name
# - Set instance_type to aget or AGET
# - Set portfolio
# - Set managed_by

# Update AGENTS.md
# - Customize for specific use case

# Recreate symlink
rm CLAUDE.md
ln -s AGENTS.md CLAUDE.md
```

---

## File Size Guidelines

### AGENTS.md Size Limit

- **Hard limit**: 40,000 characters
- **Warning threshold**: 35,000 characters (L146)

**Strategies for large configurations**:

1. Extract verbose content to .aget/docs/
2. Use references instead of inline content
3. Move historical context to evolution/
4. Compress examples

### version.json Size

- Keep under 2,000 characters
- Move complex nested objects to separate files

---

## Naming Conventions

> **Full Specification**: See [AGET_FILE_NAMING_CONVENTIONS.md](../specs/AGET_FILE_NAMING_CONVENTIONS.md) for complete patterns, decision tree, and anti-patterns.

### Directory Names

```
{visibility}-{identifier}-{type}

visibility: private | public | template
identifier: kebab-case descriptive name
type: aget | AGET

Examples:
- template-worker-aget
- my-supervisor-AGET
- my-impact-aget
```

### File Names

| Type | Convention | Example |
|------|------------|---------|
| Specs | `{NAME}_SPEC_v{M}.{m}.yaml` | `WORKER_TEMPLATE_SPEC_v1.0.yaml` |
| ADRs | `ADR-{NNN}-{kebab-case}.md` | `ADR-001-initial-architecture.md` |
| L-docs | `L{NNN}_{snake_case}.md` | `L187_wake_protocol.md` |
| Plans | `PROJECT_PLAN_{name}_v{M}.{m}.md` | `PROJECT_PLAN_file_naming_v1.0.md` |
| Sessions | `SESSION_{YYYY-MM-DD}_{name}.md` | `SESSION_2025-12-20_research.md` |
| SOPs | `SOP_{snake_case}.md` | `SOP_release_process.md` |

---

## Validation Checklist

Before committing a template or instance:

### Core Requirements (all versions)

- [ ] version.json has all required fields
- [ ] aget_version matches framework version
- [ ] CLAUDE.md is symlink to AGENTS.md
- [ ] AGENTS.md under 40k characters
- [ ] @aget-version header present in AGENTS.md
- [ ] Substantial Change Protocol section exists
- [ ] Session protocols defined
- [ ] README.md exists and is current

### v3.3 Exemplar Requirements (CAP-TPL-014)

- [ ] specs/{Type}_SPEC.md exists with required sections
  - [ ] Abstract
  - [ ] Archetype Definition
  - [ ] Capabilities (≥3)
  - [ ] Inviolables
  - [ ] EKO Classification
  - [ ] Archetype Constraints
  - [ ] A-SDLC Phase Coverage
- [ ] specs/{Type}_VOCABULARY.md exists with required sections
  - [ ] Concept Scheme (SKOS)
  - [ ] Core Concepts (≥5)
  - [ ] Concept Relationships
  - [ ] EKO Cross-References
- [ ] shell/ directory exists
  - [ ] {type}_profile.zsh with aget_info(), aget_docs()
  - [ ] README.md with usage instructions
- [ ] .aget/evolution/ directory exists with seed L-doc
- [ ] manifest.yaml exists (5D composition)

---

## Common Patterns

### Minimal Template

```
minimal-aget/
├── .aget/
│   └── version.json
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
└── README.md
```

### Full-Featured Template

```
full-aget/
├── .aget/
│   ├── version.json
│   ├── evolution/
│   │   └── L001_initial.md
│   ├── specs/
│   │   └── TEMPLATE_SPEC_v1.0.yaml
│   ├── architecture/
│   │   └── ADR-001-design.md
│   ├── docs/
│   │   └── INTERNAL_GUIDE.md
│   └── tests/
│       └── contract_tests.py
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
├── README.md
├── CHANGELOG.md
├── docs/
│   └── USER_GUIDE.md
└── scripts/
    └── setup.sh
```

---

## References

| ID | Title | Location |
|----|-------|----------|
| [WORKER_TEMPLATE_SPEC] | Foundation capabilities | [`specs/`][worker-spec] |
| [VOCABULARY_SPEC] | Standard terminology | [`specs/`][vocab-spec] |
| [VERSIONING_CONVENTIONS] | Version rules | [`specs/`][version-spec] |
| [L171] | Instance creation specification gap | Internal L-doc |

[worker-spec]: ../specs/WORKER_TEMPLATE_SPEC_v1.0.yaml
[vocab-spec]: ../specs/AGET_VOCABULARY_SPEC.md
[version-spec]: ../specs/AGET_VERSIONING_CONVENTIONS.md

---

*TEMPLATE_STRUCTURE_GUIDE.md — Standard structure for AGET templates*
