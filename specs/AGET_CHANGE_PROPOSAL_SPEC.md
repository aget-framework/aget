# AGET Change Proposal Specification v1.0

**Version**: 1.0.0
**Date**: 2025-12-26
**Status**: PILOT
**Location**: aget/specs/AGET_CHANGE_PROPOSAL_SPEC.md
**Format**: AGET_SPEC_FORMAT_v1.1
**Vocabulary**: AGET_CONTROLLED_VOCABULARY.md
**Change Proposal**: CP-001

---

## 1. Purpose

This specification defines the format, lifecycle, and handling requirements for Change Proposals (CPs) in the AGET framework. Change Proposals formalize how changes to specifications, patterns, and processes are proposed, evaluated, and tracked.

---

## 2. Scope

### 2.1 What This Specification Defines

- Required fields for Change Proposals
- Lifecycle states and transitions
- Categories of proposals
- Validation rules
- File naming conventions

### 2.2 What This Specification Does Not Define

- Internal review processes (see PROCESS_release_workflow.yaml)
- Voting or consensus mechanisms
- External contribution workflows

---

## 3. Terminology

| Term | Definition |
|------|------------|
| Change_Proposal | Formal request for framework change (abbrev: CP) |
| CP_ID | Unique identifier (pattern: CP-NNN) |
| Lifecycle_State | Current status in CP lifecycle |
| Category | Classification: standards, informational, process |

---

## 4. Change Proposal Format

### 4.1 File Format

Change Proposals are written in Markdown with YAML front matter.

**File naming**: `CP-NNN_{snake_case_title}.md`

**Example**: `CP-001_change_proposal_mechanism.md`

### 4.2 Required Sections

#### Preamble (YAML Front Matter)

```yaml
---
proposal_id: CP-NNN
title: string (max 80 characters)
author: agent_name
date_submitted: YYYY-MM-DD
status: lifecycle_state
category: standards | informational | process
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| proposal_id | string | YES | Unique identifier matching ^CP-\d{3}$ |
| title | string | YES | Short descriptive title (max 80 chars) |
| author | string | YES | Name of proposing agent |
| date_submitted | date | YES | ISO 8601 date |
| status | enum | YES | Current lifecycle state |
| category | enum | YES | Proposal classification |

#### Abstract

One paragraph (max 200 words) describing the purpose of the proposal.

#### Motivation

Explanation of why this change is needed. Should answer:
- What problem does this solve?
- What existing limitation does this address?
- What is the impact of not making this change?

#### Proposed Change

Detailed description of the proposed change. Should include:
- What specifically will change
- New artifacts to be created
- Existing artifacts to be modified
- Example content (if applicable)

#### Impact Assessment

```yaml
impact_assessment:
  breaking: boolean
  version_impact: major | minor | patch
  affected_artifacts:
    - artifact_type: spec | template | pattern | sop | validator
      artifact_name: string
      change_type: create | update | delete
```

#### Alternatives Considered

At least one alternative approach with rationale for why it was not chosen.

```yaml
alternatives_considered:
  - option: string
    rationale: string
```

#### Acceptance Criteria

List of testable conditions that must be true for the proposal to be considered complete.

```yaml
acceptance_criteria:
  - criterion: string
    verification: string
```

### 4.3 Resolution Section (Added When Closed)

When a CP is closed (REJECTED, CLOSED), this section is added:

```yaml
resolution: accepted | rejected | deferred | withdrawn
resolution_date: YYYY-MM-DD
resolution_rationale: string
resulting_artifacts:
  - type: spec | pattern | validator | template
    path: string
version_released: vX.Y.Z
```

---

## 5. Lifecycle States

### 5.1 State Definitions

| State | Meaning | Location |
|-------|---------|----------|
| DRAFT | Author preparing proposal | Author's local repository |
| SUBMITTED | Filed for review | framework-aget inbound/ |
| UNDER_REVIEW | Being evaluated | framework-aget processing/ |
| ACCEPTED | Approved for implementation | framework-aget accepted/ |
| REJECTED | Not approved for implementation | framework-aget resolved/ |
| DEFERRED | Postponed to future version | framework-aget backlog/ |
| SCOPED | Assigned to specific version | VERSION_SCOPE document |
| IMPLEMENTING | In active development | PROJECT_PLAN execution |
| RELEASED | Published in version | Git tag |
| CLOSED | Complete | framework-aget resolved/ + docs/proposals/ |

### 5.2 State Transitions

```
DRAFT ──submit──► SUBMITTED ──review──► UNDER_REVIEW
                                              │
                  ┌───────────────────────────┼───────────────────┐
                  ▼                           ▼                   ▼
              ACCEPTED                    REJECTED            DEFERRED
                  │                      (terminal)               │
                  ▼                                               │
               SCOPED ◄───────────────────────────────────────────┘
                  │                        (can be reconsidered)
                  ▼
           IMPLEMENTING
                  │
                  ▼
              RELEASED
                  │
                  ▼
               CLOSED
                (terminal)
```

### 5.3 Transition Rules

| From | To | Trigger | Actor |
|------|-----|---------|-------|
| DRAFT | SUBMITTED | Author submits | Author |
| DRAFT | WITHDRAWN | Author cancels | Author |
| SUBMITTED | UNDER_REVIEW | Review begins | Framework Manager |
| UNDER_REVIEW | ACCEPTED | Approval | Framework Manager + Supervisor |
| UNDER_REVIEW | REJECTED | Rejection | Framework Manager + Supervisor |
| UNDER_REVIEW | DEFERRED | Postponement | Framework Manager |
| ACCEPTED | SCOPED | Version assignment | Framework Manager |
| DEFERRED | ACCEPTED | Reconsideration | Framework Manager |
| DEFERRED | REJECTED | Final rejection | Framework Manager + Supervisor |
| SCOPED | IMPLEMENTING | Gate execution begins | Framework Manager |
| IMPLEMENTING | RELEASED | Version tagged | Framework Manager |
| RELEASED | CLOSED | Closure activities | Framework Manager |

---

## 6. Categories

### 6.1 Standards

Normative changes that define requirements, specifications, or mandatory behaviors.

**Examples**:
- New specifications (AGET_*_SPEC)
- New R-* requirement sets
- Mandatory format changes

**Version Impact**: Usually MINOR or MAJOR

### 6.2 Informational

Non-normative guidance, best practices, or documentation.

**Examples**:
- Guides and tutorials
- Best practice documents
- Explanatory notes

**Version Impact**: Usually PATCH or MINOR

### 6.3 Process

Workflow definitions, procedures, and operational changes.

**Examples**:
- PROCESS specifications
- SOP updates
- Lifecycle changes

**Version Impact**: Usually MINOR

---

## 7. Validation Rules

### 7.1 Format Validation

| Rule | Description |
|------|-------------|
| V-CP-001 | proposal_id MUST match pattern ^CP-\d{3}$ |
| V-CP-002 | status MUST be one of defined lifecycle states |
| V-CP-003 | category MUST be one of: standards, informational, process |
| V-CP-004 | date_submitted MUST be valid ISO 8601 date |
| V-CP-005 | title length MUST NOT exceed 80 characters |
| V-CP-006 | abstract word count MUST NOT exceed 200 |

### 7.2 Content Validation

| Rule | Description |
|------|-------------|
| V-CP-010 | IF breaking: true THEN version_impact MUST be major |
| V-CP-011 | acceptance_criteria MUST have at least one item |
| V-CP-012 | alternatives_considered MUST have at least one item |
| V-CP-013 | affected_artifacts MUST have at least one item |

### 7.3 Lifecycle Validation

| Rule | Description |
|------|-------------|
| V-CP-020 | State transitions MUST follow defined paths |
| V-CP-021 | Terminal states (REJECTED, CLOSED) MUST NOT transition |
| V-CP-022 | CLOSED status MUST have resolution section |

---

## 8. Requirements

### R-CP-001: Change Proposal Format

The Agent creates Change Proposals in defined format.

| ID | Requirement |
|----|-------------|
| R-CP-001-01 | The Agent SHALL WRITE CPs in Markdown with YAML front matter |
| R-CP-001-02 | The Agent SHALL INCLUDE all required preamble fields |
| R-CP-001-03 | The Agent SHALL INCLUDE abstract section (max 200 words) |
| R-CP-001-04 | The Agent SHALL INCLUDE motivation section |
| R-CP-001-05 | The Agent SHALL INCLUDE proposed_change section |
| R-CP-001-06 | The Agent SHALL INCLUDE impact_assessment section |
| R-CP-001-07 | The Agent SHALL INCLUDE alternatives_considered (min 1) |
| R-CP-001-08 | The Agent SHALL INCLUDE acceptance_criteria (min 1) |
| R-CP-001-09 | The Agent SHALL NAME files as CP-NNN_{snake_case}.md |

### R-CP-002: Change Proposal Lifecycle

The Agent manages CP lifecycle per defined states.

| ID | Requirement |
|----|-------------|
| R-CP-002-01 | The Agent SHALL SET initial status to DRAFT |
| R-CP-002-02 | The Agent SHALL VALIDATE state transitions |
| R-CP-002-03 | The Agent SHALL REJECT invalid state transitions |
| R-CP-002-04 | The Agent SHALL UPDATE date fields on state changes |
| R-CP-002-05 | WHEN CP reaches CLOSED, the Agent SHALL ADD resolution section |
| R-CP-002-06 | WHEN CP is REJECTED, the Agent SHALL DOCUMENT rejection_rationale |

### R-CP-003: Change Proposal Publication

The Agent publishes completed CPs.

| ID | Requirement |
|----|-------------|
| R-CP-003-01 | WHEN CP reaches CLOSED with resolution=accepted, the Agent SHALL COPY to docs/proposals/accepted/ |
| R-CP-003-02 | The Agent SHALL UPDATE docs/proposals/README.md index |
| R-CP-003-03 | The Agent SHALL PRESERVE original CP content in publication |
| R-CP-003-04 | The Agent SHALL ADD publication_date to published CP |

---

## 9. Cross-References

| Document | Relationship |
|----------|--------------|
| PROCESS_release_workflow.yaml | Defines CP handling phases |
| AGET_FRAMEWORK_SPEC R-PROC-005 | CP handling requirements |
| VERSION_SCOPE artifact | References scoped CPs |
| PROJECT_PLAN template | Implements scoped CPs |

---

## 10. Graduation History

This specification originated from:

| Stage | Artifact | Date |
|-------|----------|------|
| Learning | L381_enhancement_request_driven_learning_transfer.md | 2025-12-26 |
| Pattern | (direct to spec - governance need) | - |
| Specification | AGET_CHANGE_PROPOSAL_SPEC.md | 2025-12-26 |
| Change Proposal | CP-001 | 2025-12-26 |

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-26 | Initial release (v3.0.0-alpha.1) |

---

*AGET_CHANGE_PROPOSAL_SPEC.md — Specification for Change Proposals*
*Status: PILOT | Format: AGET_SPEC_FORMAT_v1.1*
