# AGET Evolution Specification

**Spec ID**: SPEC-EVOL-001
**Version**: 1.0.0
**Status**: ACTIVE
**Category**: Standards (Knowledge Management)
**Format Version**: 1.2
**Created**: 2026-01-06
**Updated**: 2026-01-06
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_EVOLUTION_SPEC.md`
**Change Origin**: L460 (Directory Semantics Reconciliation Gap), L461 (Evolution Entry Type Standardization)
**Related Specs**: AGET_LDOC_SPEC, AGET_TEMPLATE_SPEC (CAP-TPL-013), AGET_FILE_NAMING_CONVENTIONS

---

## Abstract

This specification defines the `.aget/evolution/` directory structure, entry types, and content placement rules for AGET agents. Evolution directories capture retrospective knowledge (learnings, decisions, discoveries) in a standardized format enabling cross-agent discovery and fleet-wide pattern sharing.

## Motivation

Prior to this specification:

1. **Entry type divergence**: gmelli/aget-aget used subdirectories (`decisions/`, `discoveries/`, `extractions/`); aget-framework used prefixed flat files (`L###_`, `D###_`, `DISC###_`)
2. **Content misplacement**: 158 PROJECT_PLAN files found in `.aget/evolution/` (wrong location)
3. **Incomplete specification**: AGET_LDOC_SPEC covered L-docs only, not D-docs or DISC-docs
4. **Semantic confusion**: Prospective documents (PROJECT_PLANs) mixed with retrospective documents (learnings)

L460 and L461 established the canonical pattern. This spec formalizes those decisions.

## Scope

**Applies to**: All AGET agents with `.aget/evolution/` directories.

**Defines**:
- Three evolution entry types (Learning, Decision, Discovery)
- File naming conventions for each type
- Directory structure (flat files, not subdirectories)
- Content placement rules
- Index file format
- Validation requirements

**Does not cover**:
- L-doc internal format (see AGET_LDOC_SPEC)
- Project planning (see AGET_PROJECT_PLAN_SPEC)
- Session notes (see AGET_SESSION_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "evolution"
    version: "1.0.0"
    inherits: "aget_core"

  entry_types:
    Evolution_Entry:
      skos:definition: "Retrospective knowledge artifact in .aget/evolution/"
      skos:narrower: ["Learning_Entry", "Decision_Entry", "Discovery_Entry"]
      aget:temporal_orientation: "retrospective"

    Learning_Entry:
      skos:definition: "Lesson learned, pattern discovered, or process improvement"
      aget:prefix: "L"
      aget:naming: "L{NNN}_{snake_case_title}.md"
      skos:example: "L460_directory_semantics_reconciliation_gap.md"
      skos:related: ["CAP-EVOL-001", "AGET_LDOC_SPEC"]

    Decision_Entry:
      skos:definition: "Architectural or strategic decision with trade-off analysis"
      aget:prefix: "D"
      aget:naming: "D{NNN}_{snake_case_title}.md"
      skos:example: "D001_centralized_vs_distributed_tracking.md"
      skos:related: ["CAP-EVOL-002"]

    Discovery_Entry:
      skos:definition: "Unexpected finding, emergent behavior, or pattern observation"
      aget:prefix: "DISC"
      aget:naming: "DISC{NNN}_{snake_case_title}.md"
      skos:example: "DISC001_concurrent_evolution_log_collision.md"
      skos:related: ["CAP-EVOL-003"]

  structure:
    Evolution_Directory:
      skos:definition: "Directory containing evolution entries"
      aget:location: ".aget/evolution/"
      aget:structure: "flat files with prefixes (not subdirectories)"

    Evolution_Index:
      skos:definition: "JSON index of evolution entries for discovery"
      aget:location: ".aget/evolution/index.json"
      skos:related: ["CAP-EVOL-006"]

  temporal:
    Retrospective:
      skos:definition: "Knowledge about what happened (past)"
      skos:note: "Evolution entries are retrospective"

    Prospective:
      skos:definition: "Plans about what will happen (future)"
      skos:note: "PROJECT_PLANs are prospective, belong in planning/"
```

---

## Requirements

### CAP-EVOL-001: Learning Entries (L-prefix)

The SYSTEM shall support Learning entries for capturing lessons learned.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-001-01 | ubiquitous | The SYSTEM shall use L-prefix for Learning entries |
| CAP-EVOL-001-02 | ubiquitous | The SYSTEM shall name Learning entries as `L{NNN}_{title}.md` |
| CAP-EVOL-001-03 | ubiquitous | The SYSTEM shall use 3-digit zero-padded numbers (L001-L999) |
| CAP-EVOL-001-04 | conditional | IF Learning count exceeds 999 THEN the SYSTEM shall use 4 digits |
| CAP-EVOL-001-05 | ubiquitous | The SYSTEM shall conform Learning entries to AGET_LDOC_SPEC format |

**Enforcement**: `validate_ldoc.py`

**When to Create L-docs**:
- After completing significant work (migrations, releases, refactoring)
- When discovering a reusable pattern
- After making a mistake worth documenting
- When establishing new protocols or practices

### CAP-EVOL-002: Decision Entries (D-prefix)

The SYSTEM shall support Decision entries for documenting architectural choices.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-002-01 | ubiquitous | The SYSTEM shall use D-prefix for Decision entries |
| CAP-EVOL-002-02 | ubiquitous | The SYSTEM shall name Decision entries as `D{NNN}_{title}.md` |
| CAP-EVOL-002-03 | ubiquitous | The SYSTEM shall include Options_Considered section |
| CAP-EVOL-002-04 | ubiquitous | The SYSTEM shall include Decision section with rationale |
| CAP-EVOL-002-05 | ubiquitous | The SYSTEM shall include Consequences section |

**Enforcement**: `validate_evolution_entry.py`

**When to Create D-docs**:
- Before making irreversible architectural changes
- When choosing between competing approaches
- When establishing policies or standards
- When the decision has fleet-wide implications

### CAP-EVOL-003: Discovery Entries (DISC-prefix)

The SYSTEM shall support Discovery entries for documenting unexpected findings.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-003-01 | ubiquitous | The SYSTEM shall use DISC-prefix for Discovery entries |
| CAP-EVOL-003-02 | ubiquitous | The SYSTEM shall name Discovery entries as `DISC{NNN}_{title}.md` |
| CAP-EVOL-003-03 | ubiquitous | The SYSTEM shall include Evidence section |
| CAP-EVOL-003-04 | ubiquitous | The SYSTEM shall include Implications section |
| CAP-EVOL-003-05 | optional | WHERE actionable, the SYSTEM shall include Action_Items section |

**Enforcement**: `validate_evolution_entry.py`

**When to Create DISC-docs**:
- When observing unexpected system behavior
- When finding patterns across multiple agents
- When identifying gaps in frameworks or documentation
- When external events affect agent operations

### CAP-EVOL-004: Directory Structure

The SYSTEM shall maintain flat file structure in evolution directories.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-004-01 | ubiquitous | The SYSTEM shall use flat file structure (not subdirectories) |
| CAP-EVOL-004-02 | ubiquitous | The SYSTEM shall NOT create decisions/, discoveries/, extractions/ subdirectories |
| CAP-EVOL-004-03 | ubiquitous | The SYSTEM shall place all evolution entries directly in .aget/evolution/ |
| CAP-EVOL-004-04 | optional | WHERE README.md exists, the SYSTEM shall document entry type conventions |

**Enforcement**: `validate_content_placement.py`

**Rationale**: Flat structure with prefixes enables simple `ls .aget/evolution/L*.md` queries and aligns with fleet-wide practice.

### CAP-EVOL-005: Content Placement

The SYSTEM shall place content in semantically correct directories.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-005-01 | ubiquitous | The SYSTEM shall place L/D/DISC entries in .aget/evolution/ |
| CAP-EVOL-005-02 | ubiquitous | The SYSTEM shall place PROJECT_PLANs in planning/ |
| CAP-EVOL-005-03 | ubiquitous | The SYSTEM shall place SOPs in sops/ |
| CAP-EVOL-005-04 | ubiquitous | The SYSTEM shall place session notes in sessions/ |
| CAP-EVOL-005-05 | ubiquitous | The SYSTEM shall NOT place prospective documents in .aget/evolution/ |

**Enforcement**: `validate_content_placement.py`

**Content Placement Matrix**:

| Content Type | Correct Location | Wrong Locations | Temporal |
|--------------|------------------|-----------------|----------|
| L-docs | `.aget/evolution/` | planning/, sessions/ | Retrospective |
| D-docs | `.aget/evolution/` | governance/, planning/ | Retrospective |
| DISC-docs | `.aget/evolution/` | knowledge/, sessions/ | Retrospective |
| PROJECT_PLANs | `planning/` | .aget/evolution/, governance/ | Prospective |
| SOPs | `sops/` | .aget/evolution/, planning/ | Reference |
| Session notes | `sessions/` | .aget/evolution/, planning/ | Ephemeral |

### CAP-EVOL-006: Evolution Index

The SYSTEM shall maintain an index for evolution entry discovery.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-006-01 | optional | WHERE index.json exists, the SYSTEM shall include entry metadata |
| CAP-EVOL-006-02 | conditional | IF entry count > 50 THEN the SYSTEM should maintain index.json |
| CAP-EVOL-006-03 | ubiquitous | The SYSTEM shall include entry type in index entries |
| CAP-EVOL-006-04 | optional | WHERE generated, the SYSTEM shall include category and scope |

**Enforcement**: `validate_evolution_index.py`

### CAP-EVOL-007: Public Learning Publication (CP-008)

The SYSTEM shall support publication of Learning entries to `docs/learnings/` for external consumption.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-007-01 | ubiquitous | The SYSTEM shall place Published_Learnings in `docs/learnings/` |
| CAP-EVOL-007-02 | conditional | IF L-doc published THEN the SYSTEM shall verify fleet-wide applicability |
| CAP-EVOL-007-03 | ubiquitous | The SYSTEM shall sanitize internal references before publication |
| CAP-EVOL-007-04 | ubiquitous | The SYSTEM shall preserve L-number from source L-doc |
| CAP-EVOL-007-05 | conditional | IF L-doc references private agents THEN the SYSTEM shall generalize references |
| CAP-EVOL-007-06 | ubiquitous | The SYSTEM shall include publication metadata in Published_Learning |
| CAP-EVOL-007-07 | conditional | IF source L-doc updated THEN the SYSTEM should review Published_Learning |

**Enforcement**: `validate_public_learnings.py`, `SOP_learning_publication.md`

**Selection Criteria** (recommended):
- L-doc has fleet-wide or universal applicability
- Pattern executed 3+ times successfully
- No internal references that cannot be generalized
- Provides value to external users

**Sanitization Checklist**:
- [ ] No `.aget/` paths (replace with `path/to/your/`)
- [ ] No `private-*-AGET` agent names (generalize or remove)
- [ ] No internal tracking issues (remove or generalize)
- [ ] No machine-specific paths (use placeholders)
- [ ] References validated for external accessibility

**Publication Metadata**:
```yaml
publication:
  date: YYYY-MM-DD
  source: ".aget/evolution/L###_*.md"
  sanitized: true
  applicability: fleet | universal
```

---

## Entry Type Templates

### Learning Entry Template (L-prefix)

```markdown
# L{NNN}: {Title}

**Status**: Active
**Created**: YYYY-MM-DD
**Author**: {agent-name}
**Category**: {category}

## Context

[What situation or observation led to this learning]

## Learning

[The core insight or pattern discovered]

## Application

[How to apply this learning]

## Evidence

[Specific examples or data supporting this learning]

## Related

- L-docs: [list]
- Issues: [list]
- Patterns: [list]
```

### Decision Entry Template (D-prefix)

```markdown
# D{NNN}: {Decision Title}

**Status**: Proposed/Accepted/Implemented/Deprecated
**Created**: YYYY-MM-DD
**Decision Makers**: {Who was involved}

## Context

[What decision needs to be made and why]

## Options Considered

### Option A: {Name}
- **Pros**: ...
- **Cons**: ...

### Option B: {Name}
- **Pros**: ...
- **Cons**: ...

## Decision

[What was chosen and why]

## Consequences

- **Positive**: {benefits}
- **Negative**: {trade-offs}
- **Neutral**: {other impacts}

## References

- Related specs
- Related L-docs
- Related issues
```

### Discovery Entry Template (DISC-prefix)

```markdown
# DISC{NNN}: {Discovery Title}

**Created**: YYYY-MM-DD
**Discovered By**: {Agent or human}
**Context**: {Where/when this was observed}

## The Discovery

[What was found or observed]

## Evidence

[Specific examples, data, or observations]

## Implications

[What does this mean for the fleet/framework]

## Action Items

- [ ] Action 1
- [ ] Action 2
```

---

## Validation

### R-EVOL-001: Entry Prefix Format

```bash
# All evolution entries must have valid prefix
ls .aget/evolution/*.md | grep -vE "^(L|D|DISC)[0-9]+_|README|MAINTENANCE|index" && echo "INVALID" || echo "VALID"
```

### R-EVOL-002: No Subdirectories

```bash
# Evolution directory should not contain subdirectories (except allowed)
find .aget/evolution -type d -mindepth 1 | grep -vE "^$" && echo "SUBDIRS FOUND" || echo "VALID"
```

### R-EVOL-003: No PROJECT_PLANs in Evolution

```bash
# PROJECT_PLANs must not be in evolution
ls .aget/evolution/PROJECT_PLAN*.md 2>/dev/null && echo "MISPLACED" || echo "VALID"
```

### R-EVOL-004: Number Sequence

```bash
# Check for duplicate L-numbers
ls .aget/evolution/L*.md | sed 's/_.*//;s/.*\///' | sort | uniq -d
```

---

## Migration

### From Subdirectory Pattern

For repos using `decisions/`, `discoveries/` subdirectories:

```bash
# 1. Flatten structure
mv .aget/evolution/decisions/*.md .aget/evolution/
mv .aget/evolution/discoveries/*.md .aget/evolution/

# 2. Rename to prefix pattern
# decisions/foo.md → D001_foo.md
# discoveries/bar.md → DISC001_bar.md

# 3. Remove empty subdirectories
rmdir .aget/evolution/decisions .aget/evolution/discoveries
```

### From PROJECT_PLANs in Evolution

For repos with PROJECT_PLANs in `.aget/evolution/`:

```bash
# 1. Create planning/ if needed
mkdir -p planning/

# 2. Move PROJECT_PLANs
mv .aget/evolution/PROJECT_PLAN_*.md planning/

# 3. Update internal references
```

See: `scripts/migrate_project_plans.py`

---

## Index File Schema

```json
{
  "format_version": "1.0",
  "last_updated": "2026-01-06T12:00:00Z",
  "stats": {
    "total": 130,
    "by_type": {
      "learning": 120,
      "decision": 5,
      "discovery": 5
    }
  },
  "entries": [
    {
      "id": "L460",
      "type": "learning",
      "title": "Directory Semantics Reconciliation Gap",
      "filename": "L460_directory_semantics_reconciliation_gap.md",
      "created": "2026-01-06",
      "category": "specification-gap"
    },
    {
      "id": "D001",
      "type": "decision",
      "title": "Centralized vs Distributed Tracking",
      "filename": "D001_centralized_vs_distributed_tracking.md",
      "created": "2026-01-04"
    }
  ]
}
```

---

## References

- **AGET_LDOC_SPEC.md**: L-doc format details
- **AGET_TEMPLATE_SPEC.md CAP-TPL-013**: Evolution entry type requirements
- **AGET_FILE_NAMING_CONVENTIONS.md Category K**: Evolution naming patterns
- **L460**: Directory Semantics Reconciliation Gap
- **L461**: Evolution Entry Type Standardization
- **Issue #50**: Reconcile evolution entry types

---

*AGET_EVOLUTION_SPEC.md - Evolution Directory Specification v1.0*
