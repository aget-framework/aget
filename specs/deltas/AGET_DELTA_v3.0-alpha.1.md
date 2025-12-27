# AGET Delta Specification v3.0.0-alpha.1

**Version**: 3.0.0-alpha.1
**Date**: 2025-12-26
**Previous**: v2.11.0
**Status**: Pre-release
**Theme**: Process Governance

---

## Executive Summary

v3.0.0-alpha.1 establishes the **Process Governance Framework** for AGET, formalizing how knowledge evolves, changes are proposed, and releases are scoped.

**Pre-release**: This is the first alpha in the v3.0.0 series. Fleet agents remain on v2.12 LTS.

---

## Requirements Added

### R-PROC-004: Artifact Graduation (8 requirements)

| ID | Requirement |
|----|-------------|
| R-PROC-004-01 | Specifications SHOULD originate from validated patterns |
| R-PROC-004-02 | IF spec created without pattern precedent, the Agent SHALL DOCUMENT rationale |
| R-PROC-004-03 | Patterns SHOULD originate from learnings (L-docs) |
| R-PROC-004-04 | IF pattern created without L-doc precedent, the Agent SHALL DOCUMENT rationale |
| R-PROC-004-05 | The Agent SHALL TRACK graduation_history in artifact metadata |
| R-PROC-004-06 | Graduation to Specification SHALL REQUIRE Change Proposal (CP) |
| R-PROC-004-07 | The Agent SHALL INCLUDE source_learnings[] in pattern metadata |
| R-PROC-004-08 | The Agent SHALL INCLUDE source_pattern in spec metadata |

### R-PROC-005: Change Proposal Handling (8 requirements)

| ID | Requirement |
|----|-------------|
| R-PROC-005-01 | The Agent SHALL VALIDATE CP format on submission |
| R-PROC-005-02 | The Agent SHALL SET CP status to SUBMITTED after validation |
| R-PROC-005-03 | The Agent SHALL REVIEW CPs during scoping phase |
| R-PROC-005-04 | The Agent SHALL ASSIGN accepted CPs to VERSION_SCOPE |
| R-PROC-005-05 | The Agent SHALL TRACK CP status transitions |
| R-PROC-005-06 | The Agent SHALL PUBLISH closed CPs to docs/proposals/ |
| R-PROC-005-07 | IF CP is rejected, the Agent SHALL DOCUMENT rejection_rationale |
| R-PROC-005-08 | IF CP is deferred, the Agent SHALL DOCUMENT deferral_reason |

**Total New Requirements**: 16

---

## Requirements Modified

None.

---

## Requirements Removed

None.

---

## Components Added

### Specifications

| Component | Location | Purpose |
|-----------|----------|---------|
| AGET_CHANGE_PROPOSAL_SPEC.md | specs/ | Defines CP format, lifecycle, categories |
| PROCESS_release_workflow.yaml | specs/processes/ | Release workflow process structure |
| PROCESS_release_workflow.md | specs/processes/ | Release workflow narrative |

### Patterns

| Component | Location | Purpose |
|-----------|----------|---------|
| MIGRATION_COMPLETION_CHECKLIST.md | docs/patterns/ | Migration completion gate |
| PATTERN_migration_validation_gate.md | docs/patterns/ | Validation gate pattern |

### Validators

| Component | Location | Purpose |
|-----------|----------|---------|
| validate_process_spec.py | validation/ | Validate PROCESS specifications |

### Directories

| Directory | Purpose |
|-----------|---------|
| specs/processes/ | Process specifications (YAML) |
| docs/proposals/ | Published Change Proposals |
| docs/proposals/accepted/ | Accepted and closed CPs |

---

## Components Modified

### Specifications

| Component | Changes |
|-----------|---------|
| AGET_CONTROLLED_VOCABULARY.md | Added CP, Process, Graduation terms (v1.2.0) |
| AGET_FRAMEWORK_SPEC | Added R-PROC-004, R-PROC-005 |

### Templates (all 6)

| Template | Changes |
|----------|---------|
| template-*-aget | Added .aget/vocabulary/AGET_CORE_VOCABULARY.md |

---

## Components Removed

None.

---

## Migration Guide

### From v2.11.0 to v3.0.0-alpha.1

**For Framework Manager**:
1. Update to v3.0.0-alpha.1 spec
2. Create specs/processes/ directory
3. Create docs/proposals/ structure
4. Add vocabulary to templates

**For Fleet Agents**:
No action required. Fleet remains on v2.12 LTS until v3.0.0 stable.

---

## Traceability Matrix

| Change Proposal | Requirements | Artifacts |
|-----------------|--------------|-----------|
| CP-001 | R-PROC-005-* | AGET_CHANGE_PROPOSAL_SPEC.md |
| CP-002 | R-PROC-001-09 | PROCESS_release_workflow.yaml/.md |
| CP-003 | R-PROC-004-* | AGET_FRAMEWORK_SPEC updates |
| CP-004 | - | AGET_CORE_VOCABULARY.md in templates |
| CP-005 | R-PROC-005-06 | docs/proposals/ structure |
| CP-006 | - | VERSION_SCOPE artifact pattern |
| CP-007 | - | MIGRATION_COMPLETION_CHECKLIST.md |

---

## Breaking Changes

None. v3.0.0-alpha.1 is additive.

---

## Deprecations

None.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0-alpha.1 | 2025-12-26 | Initial pre-release (Process Governance) |

---

*AGET_DELTA_v3.0-alpha.1.md — Changes from v2.11.0*
*Status: Pre-release | Theme: Process Governance*
