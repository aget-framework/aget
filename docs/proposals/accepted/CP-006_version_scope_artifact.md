---
proposal_id: CP-006
title: VERSION_SCOPE Artifact
author: aget-framework
date_submitted: 2025-12-26
status: CLOSED
category: process
---

## Abstract

Define VERSION_SCOPE as a formal artifact type that specifies which Change Proposals are included in a version, created during the Scoping phase of the release workflow.

## Motivation

Discovered during v3.0.0-alpha.1 planning:
- PROJECT_PLAN Part 0 scopes ONE plan
- Multiple plans can contribute to one version
- No artifact said "vX.Y = CP-A + CP-B + ..."
- VERSION_SCOPE fills this gap

## Proposed Change

Define VERSION_SCOPE_vX.Y.md artifact:
- Created during P-2 (Scoping)
- Lists all CPs scoped to version
- References implementing PROJECT_PLANs
- Documents deferred items
- Includes version impact assessment

## Impact Assessment

```yaml
impact_assessment:
  breaking: false
  version_impact: minor
  affected_artifacts:
    - artifact_type: process_spec
      artifact_name: PROCESS_release_workflow.yaml
      change_type: update
    - artifact_type: vocabulary
      artifact_name: AGET_CONTROLLED_VOCABULARY.md
      change_type: update
```

## Alternatives Considered

| Option | Rationale |
|--------|-----------|
| Part 0 in each plan | Doesn't aggregate across plans |
| Master PROJECT_PLAN | Too complex |

## Acceptance Criteria

- [x] VERSION_SCOPE specification in release workflow
- [x] VERSION_SCOPE_v3.0.0-alpha.1.md created (dogfooding)
- [x] Vocabulary updated with VERSION_SCOPE term

---

## Resolution

```yaml
resolution: accepted
resolution_date: 2025-12-26
resolution_rationale: Solves multi-plan aggregation problem
resulting_artifacts:
  - type: artifact_pattern
    path: planning/VERSION_SCOPE_vX.Y.md
version_released: v3.0.0-alpha.1
publication_date: 2025-12-26
```

---

*CP-006: VERSION_SCOPE Artifact | Status: CLOSED*
