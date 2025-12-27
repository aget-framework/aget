# AGET Release Workflow Process

**Version**: 1.0.0
**Date**: 2025-12-26
**Status**: PILOT
**Location**: aget/specs/processes/PROCESS_release_workflow.md
**Structure**: PROCESS_release_workflow.yaml
**Change Proposal**: CP-002

---

## 1. Purpose

This document provides the narrative companion to PROCESS_release_workflow.yaml, explaining the rationale, examples, and edge cases for the AGET release workflow.

---

## 2. Process Overview

The AGET Release Workflow defines how changes flow from proposal to publication:

```
P-1: Intake → P-2: Scoping → P-3: Planning → P-4: Implementation → P-5: Validation → P-6: Release → P-7: Closure
```

Each phase has defined inputs, outputs, and decision points. The workflow is designed to prevent premature release declarations (L376) and ensure proper governance.

---

## 3. Phase Narratives

### P-1: Intake

**Why It Matters**: Intake ensures all Change Proposals meet format requirements before entering the review queue. This prevents wasted review effort on malformed proposals.

**Key Activities**:
- Validate CP format against AGET_CHANGE_PROPOSAL_SPEC
- Classify by category (standards, informational, process)
- Acknowledge receipt to author

**Edge Cases**:
- Invalid format: Return to author with specific errors
- Duplicate proposal: Link to existing CP

**Timing**: Continuous (CPs can be submitted anytime)

### P-2: Scoping

**Why It Matters**: Scoping prevents scope creep by explicitly deciding what goes into each version. VERSION_SCOPE is the authoritative list.

**Key Activities**:
- Review all pending CPs
- Assess version impact
- Create VERSION_SCOPE_vX.Y.md
- Identify cross-CP dependencies

**Edge Cases**:
- CP too large: Break into multiple CPs
- Conflicting CPs: Resolve in scoping or defer one
- Emergency CP: Fast-track through abbreviated scoping

**Decision Point**: Principal must approve VERSION_SCOPE before planning begins.

### P-3: Planning

**Why It Matters**: PROJECT_PLANs provide the gated execution structure that prevents premature completion declarations.

**Key Activities**:
- Create PROJECT_PLAN(s) for scoped CPs
- Define gates with clear deliverables
- Identify rollback procedures
- Get plan approval

**Edge Cases**:
- Multi-plan version: Create separate plans, reference in VERSION_SCOPE
- Plan revision needed: Return to scoping if scope changes

**Decision Point**: Principal must approve each PROJECT_PLAN.

### P-4: Implementation

**Why It Matters**: Gate-by-gate execution with GO/NOGO checkpoints ensures quality and prevents runaway implementation.

**Key Activities**:
- Execute gates sequentially
- Run mid-gate checkpoints (L002)
- Create specified artifacts
- Get per-gate approval

**Edge Cases**:
- Gate blocked: Document blocker, escalate or defer
- Scope expansion discovered: New CP, defer to next version
- "While we're at it...": RED FLAG - stop, next gate or new CP

**Decision Point**: Each gate has GO/NOGO. NOGO returns to fix issues.

### P-5: Validation

**Why It Matters**: Automated validation prevents the L376 anti-pattern (declaring complete without running validators).

**Key Activities**:
- Run ALL validators (not just some)
- Execute contract tests
- Cross-reference check
- Document any issues

**Critical Rule**: If ANY validator fails, STOP. Do NOT proceed to P-6.

**Edge Cases**:
- Validator bug: Fix validator, re-run
- Test flake: Investigate, don't ignore
- Missing validator: Create before release

**Decision Point**: All validators MUST pass for GO.

### P-6: Release

**Why It Matters**: Consistent release mechanics ensure all artifacts are properly versioned and documented.

**Key Activities**:
- Update version.json in all repos
- Update CHANGELOG.md
- Create git tags
- Create GitHub releases
- Write deep release notes

**Edge Cases**:
- Partial release: NOT allowed; all repos together
- Hotfix: Abbreviated workflow, documented as patch

**Timing**: After validation passes.

### P-7: Closure

**Why It Matters**: Closure ensures CPs are published, learnings captured, and backlog updated.

**Key Activities**:
- Set CP status to CLOSED
- Copy CPs to docs/proposals/accepted/
- Archive VERSION_SCOPE
- Capture any new learnings

**Edge Cases**:
- Deferred items: Update backlog, document in next VERSION_SCOPE planning
- Learnings: Create L-docs before session ends

---

## 4. Role Responsibilities

### Author
- Writes Change Proposals following AGET_CHANGE_PROPOSAL_SPEC
- Responds to review feedback
- Updates CPs based on decisions

### Framework Manager
- Operates the entire workflow
- Creates VERSION_SCOPE and PROJECT_PLANs
- Executes gates
- Manages releases

### Supervisor
- Approves major governance decisions
- Reviews breaking changes
- Provides oversight

### Principal
- Ultimate authority
- Approves VERSION_SCOPE
- Approves PROJECT_PLANs
- May delegate to Supervisor for routine versions

---

## 5. Artifact Flow

```
                    ┌──────────────────┐
                    │ Change Proposal  │
                    │     (DRAFT)      │
                    └────────┬─────────┘
                             │ submit
                             ▼
                    ┌──────────────────┐
                    │ Change Proposal  │
                    │   (SUBMITTED)    │
         ┌──────────┴────────┬─────────┴──────────┐
         │                   │                    │
         ▼                   ▼                    ▼
    ┌─────────┐        ┌─────────┐         ┌──────────┐
    │ACCEPTED │        │REJECTED │         │ DEFERRED │
    └────┬────┘        └─────────┘         └──────────┘
         │                                       │
         └───────────────────┬───────────────────┘
                             │ (when reconsidered)
                             ▼
                    ┌──────────────────┐
                    │  VERSION_SCOPE   │
                    │   vX.Y.Z.md      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  PROJECT_PLAN    │
                    │   vX.Y_*.md      │
                    └────────┬─────────┘
                             │ execute gates
                             ▼
                    ┌──────────────────┐
                    │   Artifacts      │
                    │ (specs, patterns,│
                    │  validators)     │
                    └────────┬─────────┘
                             │ validate
                             ▼
                    ┌──────────────────┐
                    │    Release       │
                    │   vX.Y.Z tag     │
                    └────────┬─────────┘
                             │ close
                             ▼
                    ┌──────────────────┐
                    │ docs/proposals/  │
                    │   accepted/      │
                    └──────────────────┘
```

---

## 6. Learnings Applied

| L-doc | Lesson | Application |
|-------|--------|-------------|
| L376 | Premature completion | Explicit P-5 validation phase |
| L381 | Knowledge transfer gap | CP intake and publication mechanism |
| L001 | Gate discipline | Per-gate GO/NOGO in P-4 |
| L002 | Mid-gate checkpoints | Referenced in P-4 activities |
| L042 | Stop at gate boundaries | Decision points prevent bypass |

---

## 7. Anti-Patterns

### Premature Release (L376)
**Wrong**: "Tests pass, ship it!" (skipped validators)
**Right**: Run ALL validators, get explicit validation pass

### Scope Creep
**Wrong**: Adding CPs during P-4 implementation
**Right**: New CPs go to backlog for next version

### Bypass Decision Points
**Wrong**: "Principal is busy, I'll just proceed"
**Right**: Get explicit GO or wait

### Incomplete Closure
**Wrong**: "Released! Done!" (CPs not published)
**Right**: Complete P-7 before calling version done

---

## 8. Emergency Procedures

### Hotfix
For critical bugs requiring immediate patch:
1. Create minimal CP with hotfix category
2. Abbreviated P-2: Scope to patch version
3. Abbreviated P-3: Minimal PROJECT_PLAN
4. P-4: Fix only (no feature work)
5. P-5: Run relevant validators
6. P-6: Patch release
7. P-7: Full closure

### Rollback
If release causes regression:
1. Revert git tag (create -reverted tag)
2. Revert GitHub release
3. Create new CP for fix
4. Document in learning

---

## 9. Cross-References

| Document | Relationship |
|----------|--------------|
| AGET_CHANGE_PROPOSAL_SPEC.md | Defines CP format |
| AGET_FRAMEWORK_SPEC R-PROC | Process requirements |
| VERSION_SCOPE template | Version planning |
| PROJECT_PLAN template | Gate execution |
| SOP_release_process.md | Detailed release steps |

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-26 | Initial release (v3.0.0-alpha.1) |

---

*PROCESS_release_workflow.md — Narrative companion to YAML specification*
*Status: PILOT | See PROCESS_release_workflow.yaml for structure*
