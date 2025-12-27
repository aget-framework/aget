# Change Proposal Template

Copy this template and fill in all sections to create a Change Proposal.

---

```yaml
---
proposal_id: CP-NNN
title: Short descriptive title (max 80 chars)
author: your-agent-name
date_submitted: YYYY-MM-DD
status: DRAFT
category: standards | informational | process
---
```

## Abstract

One paragraph (max 200 words) describing the purpose of this proposal.

## Motivation

Explain why this change is needed:
- What problem does this solve?
- What existing limitation does this address?
- What is the impact of not making this change?

## Proposed Change

Detailed description of the proposed change:
- What specifically will change
- New artifacts to be created
- Existing artifacts to be modified
- Example content (if applicable)

## Impact Assessment

```yaml
impact_assessment:
  breaking: false
  version_impact: minor
  affected_artifacts:
    - artifact_type: spec
      artifact_name: EXAMPLE_SPEC.md
      change_type: create
```

## Alternatives Considered

| Option | Rationale for not choosing |
|--------|---------------------------|
| Alternative 1 | Why this wasn't chosen |
| Alternative 2 | Why this wasn't chosen |

## Acceptance Criteria

- [ ] Criterion 1 (how to verify)
- [ ] Criterion 2 (how to verify)
- [ ] Criterion 3 (how to verify)

---

## Resolution (added when closed)

```yaml
resolution: accepted | rejected | deferred | withdrawn
resolution_date: YYYY-MM-DD
resolution_rationale: Explanation
resulting_artifacts:
  - type: spec
    path: specs/EXAMPLE_SPEC.md
version_released: vX.Y.Z
```

---

*Change Proposal Template*
*See: specs/AGET_CHANGE_PROPOSAL_SPEC.md for full requirements*
