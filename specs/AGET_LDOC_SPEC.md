# AGET L-Doc Specification

**Spec ID**: SPEC-LDOC-001
**Version**: 2.0.0
**Status**: ACTIVE
**Implements**: L419 (L-Doc Format v2)

---

## Purpose

Learning Documents (L-docs) capture experiential knowledge gained during agent operation. This specification defines the format, structure, and metadata requirements for L-docs to enable cross-agent discovery and fleet-wide pattern sharing.

---

## Format Versions

### Version 1.0 (Legacy)

Simple markdown with minimal structure:
- Filename: `L{number}_{title}.md`
- No structured metadata
- Free-form content

### Version 2.0 (Current)

Structured markdown with YAML frontmatter:
- Filename: `L{number}_{title}.md`
- Required YAML frontmatter
- Cross-agent discovery metadata
- Enforcement progression tracking

---

## L-Doc v2 Structure

### Filename Convention

```
L{NUMBER}_{snake_case_title}.md
```

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | `L` | `L` |
| Number | 3-4 digits | `419` |
| Separator | `_` | `_` |
| Title | snake_case | `ldoc_format_v2_proposal` |
| Extension | `.md` | `.md` |

**Full Example**: `L419_ldoc_format_v2_proposal.md`

### Required Frontmatter

```yaml
---
id: L419
title: L-Doc Format v2 Proposal
format_version: "2.0"
created: 2026-01-04
summary: |
  Structured L-doc format with YAML frontmatter enabling
  cross-agent pattern discovery and enforcement tracking.
---
```

### Recommended Frontmatter

```yaml
---
id: L419
title: L-Doc Format v2 Proposal
format_version: "2.0"
created: 2026-01-04
updated: 2026-01-04
author: aget-framework
summary: |
  Structured L-doc format with YAML frontmatter enabling
  cross-agent pattern discovery and enforcement tracking.
category: pattern
applicability:
  scope: fleet
  archetypes: [all]
  domains: [governance, knowledge-management]
  conditions:
    - "When capturing experiential knowledge"
    - "When sharing patterns across agents"
related:
  ldocs: [L029, L376]
  issues: ["#23"]
  patterns: [PATTERN_role_boundary_awareness]
enforcement:
  status: recommendation
  mechanism: documentation
tags: [ldoc, format, v2, discovery]
origin:
  session: session_2026-01-04
  trigger: "Need for cross-agent pattern discovery"
---
```

### Body Structure

```markdown
---
[YAML frontmatter]
---

# L{NUMBER}: {Title}

## Context

[What situation or observation led to this learning]

## Learning

[The core insight or pattern discovered]

## Application

[How to apply this learning]

## Evidence

[Specific examples or data supporting this learning]

## Related

- L-docs: [list of related L-docs]
- Issues: [list of related issues]
- Patterns: [list of related patterns]
```

---

## Applicability Scope

The `applicability.scope` field defines how broadly the learning applies:

| Scope | Description | Example |
|-------|-------------|---------|
| `agent` | Specific to one agent | "My agent's specific workflow" |
| `archetype` | Applies to archetype class | "All advisors should..." |
| `fleet` | Applies to entire fleet | "All agents must..." |
| `universal` | Applies beyond AGET | "General software pattern" |

---

## Enforcement Progression (L418)

L-docs progress through enforcement levels:

| Status | Meaning | Mechanism |
|--------|---------|-----------|
| `observation` | Noticed, not yet validated | none |
| `recommendation` | Suggested practice | documentation |
| `advisory` | Should follow, soft enforcement | validation warnings |
| `enforced` | Must follow, hard enforcement | gate blocking |

---

## Index File Specification

### Location

```
.aget/evolution/index.json
```

### Schema

```json
{
  "format_version": "2.0",
  "last_updated": "2026-01-04T12:00:00Z",
  "count": 150,
  "categories": {
    "pattern": 45,
    "anti-pattern": 12,
    "protocol": 20,
    "governance": 18,
    "tooling": 15,
    "migration": 10,
    "architecture": 8,
    "process": 12,
    "observation": 5,
    "decision": 5
  },
  "ldocs": [
    {
      "id": "L419",
      "title": "L-Doc Format v2 Proposal",
      "category": "pattern",
      "scope": "fleet",
      "created": "2026-01-04",
      "enforcement": "recommendation"
    }
  ]
}
```

### Index Generation

The index should be regenerated when:
- L-doc is created or updated
- L-doc count exceeds previous count + 10
- Manual regeneration requested

---

## Cross-Agent Discovery

### Query by Scope

```python
# Find all fleet-wide learnings
fleet_learnings = [l for l in index['ldocs'] if l.get('scope') == 'fleet']
```

### Query by Category

```python
# Find all patterns
patterns = [l for l in index['ldocs'] if l.get('category') == 'pattern']
```

### Query by Enforcement

```python
# Find all enforced learnings
enforced = [l for l in index['ldocs'] if l.get('enforcement') == 'enforced']
```

---

## Migration from v1 to v2

### Migration Script

```bash
python3 scripts/migrate_ldoc_to_v2.py .aget/evolution/
```

### Migration Process

1. Parse existing L-doc markdown
2. Extract title from filename
3. Infer category from content keywords
4. Set default scope (agent)
5. Generate YAML frontmatter
6. Preserve original body content
7. Update index.json

### Dry Run

```bash
python3 scripts/migrate_ldoc_to_v2.py --dry-run .aget/evolution/
```

---

## Validation

### R-LDOC-001: Filename Format

```bash
# All L-docs must match pattern
ls .aget/evolution/L*.md | grep -E "^L[0-9]+_[a-z0-9_]+\.md$"
```

### R-LDOC-002: Required Frontmatter

```bash
# Must have id, title, format_version, created, summary
python3 scripts/validate_ldoc.py L419_example.md
```

### R-LDOC-003: Index Freshness

```bash
# Index should not be more than 10 L-docs behind
actual=$(ls .aget/evolution/L*.md | wc -l)
indexed=$(python3 -c "import json; print(json.load(open('.aget/evolution/index.json'))['count'])")
[ $((actual - indexed)) -le 10 ]
```

---

## References

- Schema: `schemas/ldoc_v2.json`
- Migration: `scripts/migrate_ldoc_to_v2.py`
- Validation: `scripts/validate_ldoc.py`
- Issue #23: L-Doc Format v2

---

*AGET_LDOC_SPEC.md - L-Doc Format Specification v2.0*
