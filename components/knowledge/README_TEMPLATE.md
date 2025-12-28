# Domain Knowledge

This directory contains domain-specific beliefs and knowledge that are **NOT portable** to other agents (per L296 portability test).

## Portability Test (L296)

> **"Clone this agent to a different domain/company. Would this content still be useful?"**
> - **YES** → `.aget/evolution/` (framework beliefs, portable)
> - **NO** → `knowledge/` (domain beliefs, NOT portable)

## Taxonomy

| Location | Content Type | Portability | Example |
|----------|--------------|-------------|---------|
| `.aget/evolution/` | Framework beliefs | Portable | "Gate discipline prevents scope creep" |
| `knowledge/` | Domain beliefs | NOT portable | "This workspace uses 30-day archive cycles" |
| `sessions/` | Temporal facts | Session-specific | "2025-12-27: Migrated to v3.0" |
| `data/` | Entity facts | Observations | Measurements, objects |

## Content Types

| Prefix | Type | Description |
|--------|------|-------------|
| `FOUNDATIONAL_*` | Core Concepts | Domain fundamentals, definitions, principles |
| `STRATEGIC_*` | Strategy | Long-term positioning, frameworks, roadmaps |
| `INTELLIGENCE_*` | Analysis | Market research, competitive analysis, insights |
| `PROGRAM_*` | Programs | Multi-project initiatives, cross-cutting concerns |
| `REFERENCE_*` | Reference | Glossaries, lookup tables, standards |
| `_ARCHIVE_*` | Archived | Deprecated content (kept for historical reference) |

## Structure

For small knowledge bases (<10 files):
```
knowledge/
├── README.md           # This file
├── FOUNDATIONAL_*.md   # Core domain concepts
└── REFERENCE_*.md      # Lookup tables, standards
```

For mature knowledge bases (>20 files):
```
knowledge/
├── README.md
├── INDEX.md            # Cross-reference map
├── {domain}/           # Domain-specific subdirectory
│   ├── patterns/       # Workflow patterns
│   └── heuristics/     # Decision rules
├── thresholds/         # Environment-specific values
└── _archive/           # Deprecated content
```

## Capture Protocol

**When to capture domain knowledge:**
1. **Session end**: "What did I learn specific to THIS domain?"
2. **Discovery**: "This pattern only works HERE"
3. **Decision**: "This threshold is right for THIS environment"

**Format:**
- Patterns: Markdown (`.md`)
- Heuristics: YAML with decision rules (`.yaml`)
- Thresholds: YAML with numeric values (`.yaml`)

## Validation States

Content progresses through validation:
1. **Hypothesis**: Untested assumption
2. **Validated**: Tested 3+ times, works consistently
3. **Established**: Proven pattern (becomes "knowledge")

Mark validation status in each document's frontmatter:
```yaml
---
status: validated  # hypothesis | validated | established
validated_count: 5
last_validated: 2025-12-27
---
```

## Graduation Triggers

Content moves from `sessions/` → `knowledge/` when:
1. Referenced 3+ times across sessions
2. Explicitly marked for graduation by user
3. Represents stable, reusable domain knowledge

## Boundaries

**knowledge/ is for:**
- Enduring reference material
- Domain-specific knowledge (NOT portable)
- Curated insights that survive sessions

**knowledge/ is NOT for:**
- L-docs (belong in `.aget/evolution/`)
- PROJECT_PLANs (belong in `planning/`)
- Session notes (belong in `sessions/`)
- Charter/Mission/Scope (belong in `governance/`)
- Framework beliefs (belong in `.aget/evolution/`)

---

*This template is part of AGET v3.0.0*
*See: L296 (Portability Test), L399 (Content Semantics), L403 (Population Guidance)*
*Canonical guide: KNOWLEDGE_TAXONOMY_GUIDE.md*
