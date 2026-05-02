# AGET L-Doc Specification

**Spec ID**: SPEC-LDOC-001
**Version**: 2.3.0
**Status**: ACTIVE
**Implements**: L419 (L-Doc Format v2), SD-2 Stream 5 Qualified L-Doc IDs (v2.3.0; L801, L807)
**Updated**: 2026-05-02

---

## Purpose

Learning Documents (L-docs) capture experiential knowledge gained during agent operation. This specification defines the format, structure, and metadata requirements for L-docs to enable cross-agent discovery and fleet-wide pattern sharing.

---

## Conformance Status (2026-04-26 audit)

Empirical baseline from private-aget-framework-AGET fleet (568 L-docs):

| Requirement | Conformant | Non-Conformant | Rate |
|-------------|:----------:|:--------------:|:----:|
| CAP-LDOC-001 (filename) | 568 | 0 | 100% |
| CAP-LDOC-002 (v2 frontmatter) | 2 | 566 | 0.4% |
| CAP-LDOC-005 (body sections — Context) | 323 | 245 | 57% |
| CAP-LDOC-005 (body sections — Learning) | 104 | 464 | 18% |
| CAP-LDOC-005 (body sections — Application) | 68 | 500 | 12% |
| CAP-LDOC-005 (body sections — Evidence) | 187 | 381 | 33% |
| CAP-LDOC-005 (body sections — Related) | 139 | 429 | 24% |
| CAP-LDOC-003 (index freshness, ≤10 gap) | ✓ | — | 1 gap |

**Root cause**: v2 format migration (CAP-LDOC-002) has not occurred for legacy L-docs. The spec is aspirational; enforcement is Advisory (E1). Six distinct format schemas observed in legacy files (S1–S6, see below).

**Six observed format schemas (S1–S6)**:

| Schema | Identifying pattern | Example | Count (approx.) |
|--------|---------------------|---------|:---------------:|
| S1 | No frontmatter; `**Date**: YYYY` + `**Type**: X` header | L148 | ~50 |
| S2 | No frontmatter; `**Status**: X` + `**Created**: X` + `**Author**: X` | L462 | ~200 |
| S3 | No frontmatter; `**Date**: X` + `**Type**: X` + `**Category**: X` | L901 | ~150 |
| S4 | No frontmatter; S2 extended with `**Severity**: X` + `**Target**: X` | L735 | ~100 |
| S5 | True v2 YAML frontmatter (`---\nid: L###\n...`) | L429, L521 | 2 |
| S6 | Minimal — title only, free-form body | early L-docs | ~66 |

**Migration posture**: S1–S4/S6 legacy L-docs are granted a migration grace period (see CAP-LDOC-009). All L-docs created on or after v3.16.0 release MUST use S5 format.

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
  "L419": {
    "title": "L-Doc Format v2 Proposal",
    "date": "2026-01-04",
    "category": "pattern",
    "status": "active"
  }
}
```

> **Implementation note (2026-04-26)**: The actual `index.json` uses flat top-level `L###` keys (not a `ldocs: []` array). The spec schema above reflects the actual implementation. Cross-agent discovery queries must iterate over keys matching `^L\d+$`.

### Index Generation

The index should be regenerated when:
- L-doc is created or updated
- L-doc count exceeds previous count + 10
- Manual regeneration requested

---

## Qualified L-Doc IDs (v2.3.0 — SD-2 Stream 5)

### Problem (L801, L807)

L-Doc IDs are integer-suffixed within a single agent (`L638`). When agents cite each other's learnings cross-fleet, the same numeric ID resolves to different content per agent: `L638` in framework-AGET ≠ `L638` in supervisor-AGET. Cross-fleet citations produce **false positives** when an agent verifies another fleet's L-doc IDs against its own index. Three such false positives occurred in a single session despite agent awareness (L807 incident-density signal).

### Format

Qualified L-Doc IDs are prefixed with the agent's short name from `version.json` `aget_short_name`:

```
{agent_short_name}-L{NNN}
```

Examples:
- `framework-L638` — L638 in private-aget-framework-AGET
- `supervisor-L638` — L638 in private-supervisor-AGET
- `legalon-L638` — L638 in legalon-vp-AGET

### Backward Compatibility

Unqualified IDs (`L638`) remain valid **within a single agent's scope**. Agents reading their own L-docs continue to use unqualified IDs without change.

| Citation Context | Format | Example |
|------------------|--------|---------|
| Agent's own L-doc, internal reference | Unqualified (legacy) | `See L638` |
| Cross-agent / cross-fleet reference | Qualified (NEW) | `See framework-L638` |
| Cross-fleet table or citation index | Qualified | `[supervisor-L807, legalon-L394]` |
| Authored by THIS agent for OTHER agents | Qualified | "We file as `framework-L805`..." |

### When Qualification Is Required

Qualification is **REQUIRED** in these contexts:
- Cross-agent citations in any artifact (memos, plans, retrospectives, briefings)
- Cross-fleet tables (e.g., `key_patterns.md` rows referencing other agents' learnings)
- Public communications where multiple fleet sources are referenced
- L-doc-to-L-doc cross-references where the target L-doc is in another agent

Qualification is **OPTIONAL** in these contexts:
- Body of an L-doc citing other learnings within the same agent
- Local plans/SOPs citing the agent's own L-docs
- Conversational references where the agent context is clear

### Atomic Assignment

L-doc ID assignment is atomic per agent (using `next_id` in each agent's `index.json`). Cross-session races are prevented by per-agent atomicity. Qualified format does not change assignment semantics — the prefix is derived at citation time from `aget_short_name`.

### Index Lookup

Cross-agent lookup requires reading the foreign agent's `index.json`:

```python
import json, pathlib

def lookup_qualified_l_doc(qualified_id: str, fleet_root: pathlib.Path) -> dict:
    """Resolve qualified L-doc ID to its index entry.

    Format: {agent_short_name}-L{NNN}
    Example: 'framework-L638' resolves to private-aget-framework-AGET/.aget/evolution/L638...
    """
    short_name, l_id = qualified_id.split('-', 1)
    # Map short_name → agent directory via FLEET_REGISTRY (fleet-level; or convention)
    # Read agent's .aget/evolution/index.json
    # Return entry for l_id
    ...
```

### Migration Note

Existing L-docs do NOT need to be rewritten with qualified IDs. The qualification convention applies at citation time (forward-looking). Bulk re-citation of historical artifacts is out of scope; only new authoring SHALL use qualified IDs in cross-agent contexts.

### Conformance

See CAP-LDOC-010 (qualified-ID requirement for cross-agent citations).

---

## Cross-Agent Discovery

### Query by Scope

```python
import json, re
idx = json.load(open('.aget/evolution/index.json'))
l_keys = [k for k in idx if re.match(r'^L\d+$', k)]
fleet_learnings = [k for k in l_keys if idx[k].get('scope') == 'fleet']
```

### Query by Category

```python
import json, re
idx = json.load(open('.aget/evolution/index.json'))
l_keys = [k for k in idx if re.match(r'^L\d+$', k)]
patterns = [k for k in l_keys if idx[k].get('category') == 'pattern']
```

### Query by Enforcement

```python
import json, re
idx = json.load(open('.aget/evolution/index.json'))
l_keys = [k for k in idx if re.match(r'^L\d+$', k)]
enforced = [k for k in l_keys if idx[k].get('enforcement') == 'enforced']
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

## Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LDOC-001 | ubiquitous | The SYSTEM shall name all Learning_Document files using the pattern `L{NUMBER}_{snake_case_title}.md`. |
| CAP-LDOC-002 | ubiquitous | The SYSTEM shall include YAML frontmatter containing `id`, `title`, `format_version`, `created`, and `summary` fields in every Learning_Document. |
| CAP-LDOC-003 | prohibited | The Evolution_Index shall NOT have a Learning_Document count more than 10 behind the actual file count. |
| CAP-LDOC-004 | conditional | IF a Learning_Document applies beyond a single agent, THEN the SYSTEM shall include an `applicability.scope` field with one of: agent, archetype, fleet, universal. |
| CAP-LDOC-005 | ubiquitous | The SYSTEM shall include `Context`, `Learning`, `Application`, `Evidence`, and `Related` sections in every Learning_Document body. |
| CAP-LDOC-006 | event-driven | WHEN a Learning_Document is created or updated, THEN the SYSTEM shall regenerate the Evolution_Index. |
| CAP-LDOC-007 | ubiquitous | The SYSTEM shall track Enforcement_Status for each Learning_Document using one of: observation, recommendation, advisory, enforced. |
| CAP-LDOC-008 | ubiquitous | The SYSTEM shall report Learning_Document v2 conformance statistics in health_check.py `evolution_directory` output, including: total count, v2-conformant count, and non-conformant count. |
| CAP-LDOC-009 | event-driven | WHEN a Learning_Document is created on or after the v3.16.0 release date, THEN the SYSTEM shall enforce YAML frontmatter presence (CAP-LDOC-002) as a blocking check, not advisory. |
| CAP-LDOC-010 | conditional | IF an artifact cites a Learning_Document authored in another agent's evolution directory, THEN the citation SHALL use the qualified format `{agent_short_name}-L{NNN}` to disambiguate cross-fleet references. Unqualified `L{NNN}` remains valid within a single agent's own artifacts. |

**Evidence basis for CAP-LDOC-008/009**: 2026-04-26 conformance audit — 2/568 (0.35%) v2 conformance, 6 legacy schemas (S1–S6, see § Conformance Status). CAP-LDOC-008 surfaces the gap via health_check; CAP-LDOC-009 prevents further drift without requiring immediate bulk migration of 566 legacy L-docs.

**Evidence basis for CAP-LDOC-010**: L801 (cross-fleet false-positive verification: 3 instances in single session despite awareness) + L807 (incident-density threshold: 3+ recurrences = structural fix required). FLEET-UPG-013 vs FLEET-UPG-014 collision class confirmed at project ID layer; same root cause class as L-doc IDs. Backward-compatible: unqualified IDs valid within agent scope; qualification mandatory only for cross-agent reference points.

**Vocabulary**: Learning_Document, Evolution_Index, Enforcement_Status, Applicability_Scope

**Migration**: R-LDOC-001→CAP-LDOC-001, R-LDOC-002→CAP-LDOC-002, R-LDOC-003→CAP-LDOC-003. CAP-LDOC-004 through CAP-LDOC-007 are new (codified from existing spec content). CAP-LDOC-008/009 are new (evidence-driven, 2026-04-26 conformance audit).

---

## Authority Model

```yaml
authority:
  applies_to: "ldoc_management"

  governed_by:
    spec: "AGET_LDOC_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "Create L-docs with required frontmatter (id, title, format_version, created, summary)"
      - "Set applicability scope (agent, archetype, fleet, universal)"
      - "Set enforcement status (observation, recommendation, advisory)"
      - "Update the evolution index when L-docs are created or modified"
      - "Migrate L-docs from v1 to v2 format"
    requires_approval:
      - action: "Promote enforcement status to 'enforced'"
        approver: "principal"
      - action: "Add new applicability scope values"
        approver: "aget-framework maintainer"
      - action: "Change required frontmatter fields"
        approver: "aget-framework maintainer"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Vocabulary

Domain terms for the L-Doc specification:

```yaml
vocabulary:
  meta:
    domain: "ldoc"
    version: "1.0.0"
    inherits: "aget_core"

  terms:
    Learning_Document:
      skos:definition: "Markdown file capturing experiential knowledge gained during agent operation, named L{NUMBER}_{snake_case_title}.md with structured YAML frontmatter"
      skos:altLabel: "L-doc"
    Evolution_Index:
      skos:definition: "JSON file at .aget/evolution/index.json that catalogs all L-docs with their category, scope, and enforcement status for cross-agent discovery"
      aget:location: ".aget/evolution/index.json"
    Enforcement_Status:
      skos:definition: "Progression level indicating how strictly a learning is applied, one of: observation, recommendation, advisory, enforced"
      skos:narrower: ["Observation", "Recommendation", "Advisory", "Enforced"]
    Applicability_Scope:
      skos:definition: "Breadth of a learning's relevance, one of: agent (single agent), archetype (all agents of a type), fleet (all agents), universal (beyond AGET)"
      skos:narrower: ["Agent_Scope", "Archetype_Scope", "Fleet_Scope", "Universal_Scope"]
    YAML_Frontmatter:
      skos:definition: "Structured metadata block at the top of an L-doc containing required fields (id, title, format_version, created, summary) and optional discovery fields"
    Cross_Agent_Discovery:
      skos:definition: "Capability to query and find relevant L-docs across agents using the evolution index, filtered by scope, category, or enforcement status"
    Format_Version:
      skos:definition: "Schema version of the L-doc structure, currently 2.0, distinguishing structured frontmatter format from legacy free-form format"
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-LDOC-001 | CAP-LDOC-001 | automated | All L-doc filenames match `L[0-9]+_[a-z0-9_]+.md` pattern |
| V-LDOC-002 | CAP-LDOC-002 | inspection | Required frontmatter fields present (id, title, format_version, created, summary) — *inspection until CAP-LDOC-008 health_check extension is implemented* |
| V-LDOC-003 | CAP-LDOC-003 | automated | Index freshness: gap between actual L-docs and indexed count <= 10 |
| V-LDOC-004 | CAP-LDOC-004 | inspection | L-doc categories match allowed taxonomy |
| V-LDOC-005 | CAP-LDOC-005 | inspection | L-doc body contains required sections (Context, Learning, Application, Evidence, Related) |
| V-LDOC-006 | CAP-LDOC-006 | automated | Evolution index regenerated when L-doc is created or updated |
| V-LDOC-007 | CAP-LDOC-007 | automated | Index.json `next_id` is consistent with highest L-doc on filesystem |
| V-LDOC-008 | CAP-LDOC-008 | automated | health_check.py `evolution_directory` output includes `v2_conformant` and `non_conformant` counts |
| V-LDOC-009 | CAP-LDOC-009 | automated | L-docs created on or after v3.16.0 release without v2 frontmatter are flagged as ERROR (not WARNING) |

### Validation Commands

```bash
# V-LDOC-001: Filename format
ls .aget/evolution/L*.md | grep -E "^L[0-9]+_[a-z0-9_]+\.md$"

# V-LDOC-002: Required frontmatter
python3 scripts/validate_ldoc.py L419_example.md

# V-LDOC-003: Index freshness
actual=$(ls .aget/evolution/L*.md | wc -l)
indexed=$(python3 -c "import json; print(json.load(open('.aget/evolution/index.json'))['count'])")
[ $((actual - indexed)) -le 10 ]

# V-LDOC-008: V2 conformance statistics (pending health_check.py extension)
python3 -c "
import os, re
docs = [f for f in os.listdir('.aget/evolution') if re.match(r'L\d+_.*\.md', f)]
v2 = 0
for f in docs:
    with open(f'.aget/evolution/{f}') as fh:
        first = fh.readline().strip()
        if first == '---':
            v2 += 1
total = len(docs)
print(f'V2 conformant: {v2}/{total} ({100*v2//total}%)')
print(f'Non-conformant: {total-v2}/{total}')
"

# V-LDOC-009: New L-docs (post v3.16.0) must have frontmatter — manual check until enforcer built
# Pass criterion: any L-doc with created >= 2026-05-10 must have --- on line 1
```

---

## References

- Schema: `schemas/ldoc_v2.json`
- Migration: `scripts/migrate_ldoc_to_v2.py`
- Validation: `scripts/validate_ldoc.py`
- Issue #23: L-Doc Format v2

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.2.0 | 2026-04-26 | Added § Conformance Status (empirical audit: 2/568 v2 conformant, 6 legacy schemas). Added CAP-LDOC-008 (health_check v2 reporting) + CAP-LDOC-009 (new-doc enforcement gate post v3.16.0). Fixed index.json schema to match actual flat `L###` key implementation. Updated V-LDOC-002 from automated→inspection (pending health_check extension). Added V-LDOC-008/009. Evidence: 2026-04-26 conformance audit (private-aget-framework-AGET fleet). |
| 2.1.0 | 2026-03-16 | Added EARS-patterned requirements (CAP-LDOC-001 through 007). Migrated R-LDOC-* IDs to CAP-LDOC-*. Per L682 maturity uplift L0→L1. |
| 2.0.0 | — | Initial v2 format with YAML frontmatter and cross-agent discovery. |

---

*AGET_LDOC_SPEC.md - L-Doc Format Specification v2.2.0*
