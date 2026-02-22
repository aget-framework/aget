# AGET Change Proposal Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Process
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_CHANGE_PROPOSAL_SPEC.md`
**Change Proposal**: CP-001

---

## Abstract

This specification defines the format, lifecycle, and handling requirements for Change_Proposals (CPs) in the AGET framework. Change_Proposals formalize how changes to specifications, patterns, and processes are proposed, evaluated, and tracked.

## Motivation

Framework evolution requires structured change management:
- Changes must be proposed formally
- Impact must be assessed before approval
- Lifecycle must be tracked consistently
- Completed changes must be documented

Without explicit Change_Proposal requirements, framework evolution becomes ad-hoc and poorly documented.

## Scope

**Applies to**: All agents proposing framework changes.

**Defines**:
- Required fields for Change_Proposals
- Lifecycle_States and transitions
- Categories of proposals
- Validation rules
- File naming conventions

**Does NOT Define**:
- Internal review processes (see PROCESS_release_workflow.yaml)
- Voting or consensus mechanisms
- External contribution workflows

---

## Vocabulary

Domain terms for the Change_Proposal specification:

```yaml
vocabulary:
  meta:
    domain: "change_proposal"
    version: "1.0.0"
    inherits: "aget_core"

  process:  # Primary domain
    Change_Proposal:
      skos:definition: "Formal request for framework change"
      skos:altLabel: "CP"
      aget:naming: "CP-NNN_{snake_case}.md"
    CP_ID:
      skos:definition: "Unique identifier for Change_Proposal"
      aget:pattern: "CP-\\d{3}"
    Lifecycle_State:
      skos:definition: "Current status in CP lifecycle"
      skos:narrower: ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "ACCEPTED", "REJECTED", "DEFERRED", "SCOPED", "IMPLEMENTING", "RELEASED", "CLOSED"]
    CP_Category:
      skos:definition: "Classification of Change_Proposal"
      skos:narrower: ["Standards", "Informational", "Process"]
    Impact_Assessment:
      skos:definition: "Analysis of proposal's effect on framework"
    Acceptance_Criteria:
      skos:definition: "Testable conditions for proposal completion"

  memory:  # D2: Stored artifacts
    Resolution_Section:
      skos:definition: "Section added when CP is closed"
      aget:fields: ["resolution", "resolution_date", "resolution_rationale"]
    Proposals_Directory:
      skos:definition: "Storage for accepted proposals"
      aget:location: "docs/proposals/"

  reasoning:  # D3: Decision patterns
    State_Transition:
      skos:definition: "Movement between Lifecycle_States"
    Validation_Rule:
      skos:definition: "Requirement for CP format or content"

  context:  # D5: Where/when applied
    VERSION_SCOPE:
      skos:definition: "Document assigning CPs to versions"
    PROJECT_PLAN:
      skos:definition: "Document implementing scoped CPs"
```

---

## Requirements

### CAP-CP-001: Change Proposal Format

The SYSTEM shall create Change_Proposals in defined format.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CP-001-01 | ubiquitous | The SYSTEM shall write CPs in Markdown with YAML_Front_Matter |
| CAP-CP-001-02 | ubiquitous | The SYSTEM shall include all required Preamble_Fields |
| CAP-CP-001-03 | ubiquitous | The SYSTEM shall include Abstract section (max 200 words) |
| CAP-CP-001-04 | ubiquitous | The SYSTEM shall include Motivation section |
| CAP-CP-001-05 | ubiquitous | The SYSTEM shall include Proposed_Change section |
| CAP-CP-001-06 | ubiquitous | The SYSTEM shall include Impact_Assessment section |
| CAP-CP-001-07 | ubiquitous | The SYSTEM shall include Alternatives_Considered (min 1) |
| CAP-CP-001-08 | ubiquitous | The SYSTEM shall include Acceptance_Criteria (min 1) |
| CAP-CP-001-09 | ubiquitous | The SYSTEM shall name files as CP-NNN_{snake_case}.md |

**Enforcement**: `validate_change_proposal.py`

#### Required Preamble Fields

```yaml
---
proposal_id: CP-NNN
title: string (max 80 characters)
author: agent_name
date_submitted: YYYY-MM-DD
status: Lifecycle_State
category: standards | informational | process
---
```

### CAP-CP-002: Change Proposal Lifecycle

The SYSTEM shall manage CP_Lifecycle per defined states.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CP-002-01 | ubiquitous | The SYSTEM shall set initial status to DRAFT |
| CAP-CP-002-02 | ubiquitous | The SYSTEM shall validate State_Transitions |
| CAP-CP-002-03 | conditional | IF invalid State_Transition is attempted THEN the SYSTEM shall reject transition |
| CAP-CP-002-04 | event-driven | WHEN State_Transition occurs, the SYSTEM shall update date fields |
| CAP-CP-002-05 | event-driven | WHEN CP reaches CLOSED, the SYSTEM shall add Resolution_Section |
| CAP-CP-002-06 | event-driven | WHEN CP is REJECTED, the SYSTEM shall document Rejection_Rationale |
| CAP-CP-002-07 | ubiquitous | The SYSTEM shall NOT transition from Terminal_States (REJECTED, CLOSED) |

**Enforcement**: State machine validation

### CAP-CP-003: Change Proposal Publication

The SYSTEM shall publish completed CPs.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CP-003-01 | event-driven | WHEN CP reaches CLOSED with resolution=accepted, the SYSTEM shall copy to docs/proposals/accepted/ |
| CAP-CP-003-02 | event-driven | WHEN CP is published, the SYSTEM shall update docs/proposals/README.md index |
| CAP-CP-003-03 | ubiquitous | The SYSTEM shall preserve original CP content in publication |
| CAP-CP-003-04 | event-driven | WHEN publishing, the SYSTEM shall add Publication_Date |

**Enforcement**: Publication checklist

### CAP-CP-004: Format Validation

The SYSTEM shall validate CP format.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CP-004-01 | ubiquitous | The SYSTEM shall validate Proposal_ID matches pattern ^CP-\d{3}$ |
| CAP-CP-004-02 | ubiquitous | The SYSTEM shall validate Status is valid Lifecycle_State |
| CAP-CP-004-03 | ubiquitous | The SYSTEM shall validate Category is standards, informational, or process |
| CAP-CP-004-04 | ubiquitous | The SYSTEM shall validate Date_Submitted is valid ISO_8601 |
| CAP-CP-004-05 | ubiquitous | The SYSTEM shall validate Title_Length does NOT exceed 80 characters |
| CAP-CP-004-06 | ubiquitous | The SYSTEM shall validate Abstract_Word_Count does NOT exceed 200 |

**Enforcement**: `validate_change_proposal.py --format`

### CAP-CP-005: Content Validation

The SYSTEM shall validate CP content.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-CP-005-01 | conditional | IF Breaking is true THEN the SYSTEM shall require Version_Impact = major |
| CAP-CP-005-02 | ubiquitous | The SYSTEM shall require at least one Acceptance_Criteria item |
| CAP-CP-005-03 | ubiquitous | The SYSTEM shall require at least one Alternatives_Considered item |
| CAP-CP-005-04 | ubiquitous | The SYSTEM shall require at least one Affected_Artifacts item |

**Enforcement**: `validate_change_proposal.py --content`

---

## Lifecycle States

### State Definitions

| State | Meaning | Location |
|-------|---------|----------|
| DRAFT | Author preparing proposal | Author's local repository |
| SUBMITTED | Filed for review | framework-aget inbound/ |
| UNDER_REVIEW | Being evaluated | framework-aget processing/ |
| ACCEPTED | Approved for implementation | framework-aget accepted/ |
| REJECTED | Not approved (terminal) | framework-aget resolved/ |
| DEFERRED | Postponed to future version | framework-aget backlog/ |
| SCOPED | Assigned to specific version | VERSION_SCOPE document |
| IMPLEMENTING | In active development | PROJECT_PLAN execution |
| RELEASED | Published in version | Git tag |
| CLOSED | Complete (terminal) | framework-aget resolved/ + docs/proposals/ |

### State Transition Diagram

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

### Transition Rules

| From | To | Trigger | Actor |
|------|-----|---------|-------|
| DRAFT | SUBMITTED | Author submits | Author |
| DRAFT | WITHDRAWN | Author cancels | Author |
| SUBMITTED | UNDER_REVIEW | Review begins | Framework_Manager |
| UNDER_REVIEW | ACCEPTED | Approval | Framework_Manager + Supervisor |
| UNDER_REVIEW | REJECTED | Rejection | Framework_Manager + Supervisor |
| UNDER_REVIEW | DEFERRED | Postponement | Framework_Manager |
| ACCEPTED | SCOPED | Version assignment | Framework_Manager |
| DEFERRED | ACCEPTED | Reconsideration | Framework_Manager |
| DEFERRED | REJECTED | Final rejection | Framework_Manager + Supervisor |
| SCOPED | IMPLEMENTING | Gate execution begins | Framework_Manager |
| IMPLEMENTING | RELEASED | Version tagged | Framework_Manager |
| RELEASED | CLOSED | Closure activities | Framework_Manager |

---

## Categories

### Standards

Normative changes that define requirements, specifications, or mandatory behaviors.

**Examples**: New specifications (AGET_*_SPEC), new CAP-* requirement sets
**Version_Impact**: Usually MINOR or MAJOR

### Informational

Non-normative guidance, best practices, or documentation.

**Examples**: Guides, tutorials, best practice documents
**Version_Impact**: Usually PATCH or MINOR

### Process

Workflow definitions, procedures, and operational changes.

**Examples**: PROCESS specifications, SOP updates, lifecycle changes
**Version_Impact**: Usually MINOR

---

## Authority Model

```yaml
authority:
  applies_to: "agents_proposing_framework_changes"

  governed_by:
    spec: "AGET_CHANGE_PROPOSAL_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "create DRAFT Change_Proposals"
      - "submit CPs for review"
      - "withdraw own DRAFT CPs"

    requires_approval:
      - action: "ACCEPTED transition"
        approver: "Framework_Manager + Supervisor"
      - action: "REJECTED transition"
        approver: "Framework_Manager + Supervisor"

  framework_manager_authority:
    can_autonomously:
      - "transition SUBMITTED → UNDER_REVIEW"
      - "transition ACCEPTED → SCOPED"
      - "transition SCOPED → IMPLEMENTING"
      - "transition IMPLEMENTING → RELEASED"
      - "transition RELEASED → CLOSED"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-CP-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT transition from Terminal_States"
      rationale: "REJECTED and CLOSED are final"

    - id: "INV-CP-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT accept CP WITHOUT Acceptance_Criteria"
      rationale: "Testability is mandatory for approval"

    - id: "INV-CP-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT bypass Impact_Assessment for Breaking_Changes"
      rationale: "Breaking changes require explicit assessment"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "docs/proposals/"
      purpose: "Published Change_Proposals"
      subdirectories:
        - "accepted/"
        - "rejected/"

  required_files:
    - path: "docs/proposals/README.md"
      purpose: "Proposal index"

  cp_file_structure:
    naming: "CP-NNN_{snake_case}.md"
    location_by_state:
      DRAFT: "author's repository"
      SUBMITTED: "inbound/"
      UNDER_REVIEW: "processing/"
      ACCEPTED: "accepted/"
      RESOLVED: "resolved/"
```

---

## Validation

### Format Validation

```bash
# Validate CP format
python3 validation/validate_change_proposal.py CP-001_example.md --format

# Expected checks:
# ✅ Proposal_ID matches ^CP-\d{3}$
# ✅ Status is valid Lifecycle_State
# ✅ Category is valid
# ✅ Date is ISO_8601
# ✅ Title ≤ 80 characters
# ✅ Abstract ≤ 200 words
```

### Content Validation

```bash
# Validate CP content
python3 validation/validate_change_proposal.py CP-001_example.md --content

# Expected checks:
# ✅ Acceptance_Criteria ≥ 1
# ✅ Alternatives_Considered ≥ 1
# ✅ Affected_Artifacts ≥ 1
# ✅ IF Breaking THEN Version_Impact = major
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Actor Model"
  secondary:
    - "Cybernetics (feedback loops)"
  rationale: >
    Change_Proposals implement Actor message passing for framework evolution.
    Lifecycle states and transitions provide Cybernetic feedback for change management.
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

- PROCESS_release_workflow.yaml: CP handling phases
- AGET_FRAMEWORK_SPEC: Framework-level requirements
- VERSION_SCOPE artifact: References scoped CPs
- PROJECT_PLAN template: Implements scoped CPs
- AGET_SPEC_FORMAT_v1.2: Specification format

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L381"]
  pattern_origin: "Enhancement request handling"
  governance_vision: "Formalized change management"
  rationale: "Direct to spec - governance need for structured change proposals"

history:
  - version: "1.0.0"
    date: "2025-12-26"
    changes: "Initial release (v3.0.0-alpha.1)"
  - version: "1.1.0"
    date: "2025-12-27"
    changes: "EARS/SKOS reformat (v3.0.0-alpha.5)"
```

---

*AGET Change Proposal Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture*
*"Structured proposals enable structured evolution."*
