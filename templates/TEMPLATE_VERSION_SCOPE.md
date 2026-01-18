<!--
TEMPLATE INSTRUCTIONS:
1. Copy this file to VERSION_SCOPE_vX.Y.Z.md
2. Replace all {placeholders} with actual values
3. Remove sections marked [OPTIONAL] if not needed
4. Delete this instruction block before finalizing
5. Mark reconstructed historical docs with [RECONSTRUCTED] in header

WHEN TO CREATE:
- Before every minor or major version release
- Optional for patch releases (v3.3.1)

GOVERNANCE:
- Required by SOP_release_process.md (R-REL-020)
- Consolidates scope per R-REL-013
-->

# VERSION_SCOPE: v{X.Y.Z} — {Theme}

**Version**: 1.0.0
**Created**: {YYYY-MM-DD}
**Updated**: {YYYY-MM-DD}
**Author**: {agent-name}
**Status**: {PLANNING | READY FOR RELEASE | RELEASED | CANCELLED}
**Target**: v{X.Y.Z}
**Theme**: {Short theme description, 3-5 words}

---

## Executive Summary

{1-2 paragraphs describing what this release delivers and why it matters. Focus on user value, not implementation details.}

**Key Highlights**:
- {Highlight 1}
- {Highlight 2}
- {Highlight 3}

---

## Release Objectives

<!-- What this release aims to achieve -->

| Objective | Success Metric | Target |
|-----------|----------------|--------|
| {Objective 1} | {How measured} | {Threshold} |
| {Objective 2} | {How measured} | {Threshold} |

---

## Scope

### MVP (Must Ship)

<!-- Features/fixes that BLOCK the release if incomplete -->

| Item | Status | Tracking |
|------|:------:|----------|
| {Must-have 1} | ⬜ | {Issue/PR link} |
| {Must-have 2} | ⬜ | {Issue/PR link} |

### Full Scope (Nice to Have)

<!-- Features/fixes included if ready, but not blocking -->

| Item | Status | Tracking |
|------|:------:|----------|
| {Nice-to-have 1} | ⬜ | {Issue/PR link} |

### Out of Scope

<!-- Explicitly excluded with rationale and deferral target -->

| Item | Rationale | Deferral Target |
|------|-----------|-----------------|
| {Excluded item} | {Why excluded} | v{X.Y+1.Z} |

---

## Pre-Release Dependencies

<!-- Blockers that must resolve before release can proceed -->

| Dependency | Type | Status | Owner |
|------------|------|:------:|-------|
| {Dependency 1} | BLOCKER | ⬜ | {who} |
| {Dependency 2} | SOFT | ✅ | {who} |

---

## Work Items

### Completed

| PROJECT_PLAN / Item | Status | Key Deliverables |
|---------------------|:------:|------------------|
| {Plan or item name} | ✅ COMPLETE | {What was delivered} |

### In Progress

| PROJECT_PLAN / Item | Status | Blocker |
|---------------------|:------:|---------|
| {Plan or item name} | ⏳ | {Blocker if any} |

### Not Started

| PROJECT_PLAN / Item | Priority | Notes |
|---------------------|:--------:|-------|
| {Plan or item name} | P1 | {Notes} |

---

## Release Checklist

### Phase 0: Pre-Release Validation

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 0.1 | All MVP items complete | ⬜ | |
| 0.2 | All blockers resolved | ⬜ | |
| 0.3 | Tests passing | ⬜ | |
| 0.4 | Documentation ready | ⬜ | |
| 0.5 | VERSION_SCOPE approved | ⬜ | |

### Phase 1: Release Preparation

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 1.1 | Version bump all files | ⬜ | Per R-REL-008 |
| 1.2 | CHANGELOG.md entry | ⬜ | Per R-REL-011 |
| 1.3 | Deep release notes | ⬜ | release-notes/v{X.Y.Z}.md |
| 1.4 | Migration guide | ⬜ | [OPTIONAL: if breaking changes] |

### Phase 2: Release Execution

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 2.1 | Git tag created | ⬜ | v{X.Y.Z} |
| 2.2 | Push to remote | ⬜ | Per R-REL-001 |
| 2.3 | Announcement posted | ⬜ | [OPTIONAL] |
| 2.4 | Release handoff created | ⬜ | Per R-REL-019 |

### Phase 3: Post-Release Validation

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 3.1 | Smoke test on published version | ⬜ | |
| 3.2 | Monitor for issues (24h) | ⬜ | |
| 3.3 | Update org homepage | ⬜ | Per R-REL-010 |
| 3.4 | Schedule retrospective | ⬜ | [OPTIONAL] |

---

## Timeline

| Phase | Target Date | Status |
|-------|-------------|:------:|
| Pre-Release complete | {YYYY-MM-DD} | ⬜ |
| Release Prep complete | {YYYY-MM-DD} | ⬜ |
| Release Execution | {YYYY-MM-DD} | ⬜ |
| Post-Release complete | {YYYY-MM-DD} | ⬜ |

**Preferred Release Window**: {Day/time preference if any}

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| {Risk 1} | {H/M/L} | {H/M/L} | {Mitigation strategy} |
| {Risk 2} | {H/M/L} | {H/M/L} | {Mitigation strategy} |

---

## Rollback Plan

<!-- [OPTIONAL but recommended] How to revert if critical issues discovered -->

| Trigger | Procedure | Owner |
|---------|-----------|-------|
| P0 bug within 24h | {Steps to revert} | {who} |
| Breaking regression | {Steps to hotfix} | {who} |

---

## Success Criteria

<!-- How we know the release was successful -->

| Criterion | Target | Actual | Status |
|-----------|--------|--------|:------:|
| All MVP delivered | 100% | — | ⬜ |
| No P0 bugs post-release (48h) | 0 | — | ⬜ |
| {Custom criterion} | {target} | — | ⬜ |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| {YYYY-MM-DD} | {Decision made} | {Why} |

---

## References

### Internal

- CHANGELOG.md entry: {link or "pending"}
- Deep release notes: release-notes/v{X.Y.Z}.md
- Migration guide: {link or "N/A"}

### PROJECT_PLANs

- {PROJECT_PLAN name} ({status})

### L-docs

- {L-doc references}

### External

- {External links if any}

---

## Approval

| Role | Name | Date | Decision |
|------|------|------|----------|
| Author | {agent} | {date} | PROPOSED |
| Reviewer | {agent/user} | | |
| Approver | {user} | | |

---

## Post-Release Retrospective

<!-- Complete after release -->

### Release Summary

| Field | Value |
|-------|-------|
| Version | v{X.Y.Z} |
| Released | {YYYY-MM-DD} |
| Duration | {planning to release} |
| MVP Delivered | {X of Y} |
| Issues Post-Release | {count} |

### What Went Well

- {item}

### What Could Improve

- {item}

### Lessons Learned

- {lesson → consider L-doc}

---

*VERSION_SCOPE_v{X.Y.Z}.md*
*"{Theme tagline}"*
