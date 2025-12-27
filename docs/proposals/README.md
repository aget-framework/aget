# AGET Change Proposals

This directory contains published Change Proposals (CPs) for the AGET framework.

---

## What is a Change Proposal?

A Change Proposal (CP) is a formal request for changes to the AGET framework, including:
- New specifications
- Process changes
- Template updates
- Documentation improvements

See: `specs/AGET_CHANGE_PROPOSAL_SPEC.md` for full specification.

---

## Directory Structure

```
docs/proposals/
├── README.md           # This file
├── template.md         # CP template for authors
└── accepted/           # Published accepted/closed CPs
    ├── CP-001_*.md
    ├── CP-002_*.md
    └── ...
```

---

## Published Proposals

### v3.0.0-alpha.1 (Process Governance)

| CP | Title | Category | Status |
|----|-------|----------|--------|
| [CP-001](accepted/CP-001_change_proposal_mechanism.md) | Change Proposal Mechanism | Standards | CLOSED |
| [CP-002](accepted/CP-002_release_workflow_formalization.md) | Release Workflow Formalization | Process | CLOSED |
| [CP-003](accepted/CP-003_artifact_graduation_pathway.md) | Artifact Graduation Pathway | Standards | CLOSED |
| [CP-004](accepted/CP-004_vocabulary_in_templates.md) | Vocabulary in Templates | Standards | CLOSED |
| [CP-005](accepted/CP-005_accepted_proposals_publication.md) | Accepted Proposals Publication | Informational | CLOSED |
| [CP-006](accepted/CP-006_version_scope_artifact.md) | VERSION_SCOPE Artifact | Process | CLOSED |
| [CP-007](accepted/CP-007_migration_validation_enforcement.md) | Migration Validation Enforcement | Process | CLOSED |

---

## Submitting a Change Proposal

1. Copy `template.md` to your working directory
2. Fill in all required sections
3. Self-review against AGET_CHANGE_PROPOSAL_SPEC validation rules
4. Submit to framework-aget for review

---

## Lifecycle

```
DRAFT → SUBMITTED → UNDER_REVIEW → ACCEPTED → SCOPED → IMPLEMENTING → RELEASED → CLOSED
```

Only CLOSED proposals with resolution=accepted are published here.

---

*AGET Change Proposals Index*
