---
proposal_id: CP-004
title: Vocabulary in Templates
author: private-aget-framework-AGET
date_submitted: 2025-12-26
status: CLOSED
category: standards
---

## Abstract

Include a subset of AGET_CONTROLLED_VOCABULARY.md in each template so vocabulary is available immediately after cloning, without requiring access to the full framework.

## Motivation

When templates are cloned:
- Full vocabulary not available
- Agents may use inconsistent terminology
- No immediate reference for controlled terms

## Proposed Change

Create AGET_CORE_VOCABULARY.md (70 terms) and add to all 6 templates:
- Location: `.aget/vocabulary/AGET_CORE_VOCABULARY.md`
- Categories: Artifact types, Lifecycle states, Process terms, Verbs, Governance

## Impact Assessment

```yaml
impact_assessment:
  breaking: false
  version_impact: minor
  affected_artifacts:
    - artifact_type: doc
      artifact_name: AGET_CORE_VOCABULARY.md
      change_type: create
    - artifact_type: template
      artifact_name: template-*-aget
      change_type: update
```

## Alternatives Considered

| Option | Rationale |
|--------|-----------|
| Full vocabulary copy | Too large for templates |
| URL reference only | Not available offline |
| No vocabulary | Inconsistent terminology |

## Acceptance Criteria

- [x] AGET_CORE_VOCABULARY.md created
- [x] Added to all 6 templates
- [x] Clone test: vocabulary present after clone

---

## Resolution

```yaml
resolution: accepted
resolution_date: 2025-12-26
resolution_rationale: Clone-ready consistency
resulting_artifacts:
  - type: doc
    path: docs/AGET_CORE_VOCABULARY.md
  - type: template_update
    path: template-*-aget/.aget/vocabulary/
version_released: v3.0.0-alpha.1
publication_date: 2025-12-26
```

---

*CP-004: Vocabulary in Templates | Status: CLOSED*
