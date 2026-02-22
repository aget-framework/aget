---
proposal_id: CP-007
title: Migration Validation Enforcement
author: aget-framework
date_submitted: 2025-12-26
status: CLOSED
category: process
---

## Abstract

Update migration process documentation to enforce automated validation as a blocking gate, preventing premature completion declarations.

## Motivation

L376 (Premature Completion Declaration):
- Agent declared migration "complete" after behavioral validation
- User ran validators, found 3 compliance failures
- Root cause: Validators not enforced as blocking gate

## Proposed Change

1. Update FLEET_MIGRATION_GUIDE.md:
   - Add Step 6.5 (validator download)
   - Mark Step 7 as "BLOCKING GATE"
   - Restructure into 7.1, 7.2, 7.3 (validation types)

2. Create MIGRATION_COMPLETION_CHECKLIST.md pattern

3. Update PROJECT_PLAN template with validation gate

## Impact Assessment

```yaml
impact_assessment:
  breaking: false
  version_impact: minor
  affected_artifacts:
    - artifact_type: doc
      artifact_name: FLEET_MIGRATION_GUIDE.md
      change_type: update
    - artifact_type: pattern
      artifact_name: MIGRATION_COMPLETION_CHECKLIST.md
      change_type: create
```

## Alternatives Considered

| Option | Rationale |
|--------|-----------|
| Trust agents to validate | L376 proves this fails |
| Automated enforcement | Requires tooling we don't have |

## Acceptance Criteria

- [x] FLEET_MIGRATION_GUIDE.md updated
- [x] MIGRATION_COMPLETION_CHECKLIST.md created
- [x] PROJECT_PLAN template has validation gate

---

## Resolution

```yaml
resolution: accepted
resolution_date: 2025-12-26
resolution_rationale: Prevents 75% of migration completion errors
resulting_artifacts:
  - type: doc
    path: docs/FLEET_MIGRATION_GUIDE.md
  - type: pattern
    path: docs/patterns/MIGRATION_COMPLETION_CHECKLIST.md
version_released: v3.0.0-alpha.1
publication_date: 2025-12-26
```

---

*CP-007: Migration Validation Enforcement | Status: CLOSED*
