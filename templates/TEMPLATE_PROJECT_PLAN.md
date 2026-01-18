<!--
TEMPLATE INSTRUCTIONS:
1. Replace all {placeholders} with actual values
2. Remove sections marked [OPTIONAL] if not needed
3. Delete this instruction block before finalizing
4. Consult SOP_PROJECT_PLAN_CREATION.md for guidance
-->

---
project_id: {PREFIX}-{NUMBER}
version: 1.0
owner: {agent-name}
created: {YYYY-MM-DD}
status: proposed
target: {vX.Y.Z or TBD}
depends_on: {dependency if any, or remove line}
priority: {high|medium|low}
classification: {internal|public}
scope: {domain}
verification_gates: {count}
principal_checkpoints: {count}
---

# PROJECT_PLAN: {Title}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Owner**: {agent-name}
**Status**: PROPOSED
**Target**: {vX.Y.Z}
**Protocol**: L335 (Step Back Review KB)
**Tracking**: {What this tracks - L-doc, gap, version}

---

## Executive Summary

{1-2 paragraphs summarizing what this project delivers and why}

### Delivered Value

| Component | Delivered | Impact |
|-----------|-----------|--------|
| **{Component 1}** | {What was delivered} | {Impact statement} |
| **{Component 2}** | {What was delivered} | {Impact statement} |

---

## KB Audit Summary

<!-- [RECOMMENDED for substantial work] Follow SOP_pre_proposal_kb_audit.md -->

**Audit Date**: {YYYY-MM-DD}
**Proposal**: {Brief description}
**Checklist Used**: {A (Feature) | B (Architecture) | C (Release) | D (Quick)}

### Artifacts Consulted

| Artifact | Lines/Sections | Key Finding |
|----------|----------------|-------------|
| {document} | {lines} | {finding} |

### Scope Verification

- Charter: {✅ In scope | ❌ Out of scope}
- Mission alignment: {✅ Aligned | ⚠️ Partial | ❌ Misaligned}

### Decision Authority

- Authority: {✅ Autonomous | ⚠️ Propose+Validate | ❌ Escalate}

### Precedents

| Precedent | Relevance |
|-----------|-----------|
| {L-doc or ADR} | {how it applies} |

### Novel Elements

{What has no precedent — requires extra scrutiny}

### Audit Conclusion

{Proceed | Revise | Escalate | Block}

---

## Objectives & Key Results

### Objective 1: {Primary Objective}

| KR | Target | Status |
|----|--------|--------|
| KR1.1 | {Target metric} | ⏳ |
| KR1.2 | {Target metric} | ⏳ |

### Objective 2: {Secondary Objective}

<!-- [OPTIONAL] Add more objectives as needed -->

| KR | Target | Status |
|----|--------|--------|
| KR2.1 | {Target metric} | ⏳ |

---

## Scope

### In Scope

| Area | Description |
|------|-------------|
| {Area 1} | {What's included} |
| {Area 2} | {What's included} |

### Out of Scope

| Area | Rationale | Deferral Target |
|------|-----------|-----------------|
| {Area 1} | {Why excluded} | {Future version or N/A} |

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {Dependency 1} | BLOCKS | {RESOLVED | PENDING} |

### Operational Context

<!-- [OPTIONAL] Per CAP-PP-014: For operational (non-release) PROJECT_PLANs -->

| Attribute | Value |
|-----------|-------|
| **Type** | {release | operational | infrastructure | research} |
| **Aggregates** | {List of contributing PROJECT_PLANs, or N/A} |
| **Contributes To** | {Parent PROJECT_PLAN, or N/A} |
| **Scope Definition** | {VERSION_SCOPE reference, or N/A} |

### Release PROJECT_PLAN Requirements (L553)

<!-- [REQUIRED for Type=release] Per R-REL-007 + L553 -->

**IF Type = release**, the following requirements apply:

| Requirement | Source | Verification |
|-------------|--------|--------------|
| Gates map to SOP phases | R-REL-007 | Each gate references SOP_release_process.md phase |
| Definition of Done referenced | L553 | Final gate includes DoD criteria |
| Phase 4 validation is BLOCKING | L406 | V-test: `post_release_validation.py exit code 0` |
| Scope consolidated | R-REL-013 | Single VERSION_SCOPE, no fragmented plans |

**Gate → SOP Phase Mapping** (instantiate as appropriate):

| PROJECT_PLAN Gate | SOP Phase | Purpose |
|-------------------|-----------|---------|
| Gate -1: Pre-Execution | Phase 0 | Manager migration, scope consolidation |
| Gate 0: Preparation | Phase 1 | Branch verification, content security |
| Gate 1: Version Bump | Phase 2 | Version consistency, CHANGELOG |
| Gate 2: Artifacts | Phase 3 | Tags, releases, handoff |
| Gate 3: Validation | **Phase 4 (BLOCKING)** | User-discoverable outcomes |

**Definition of Done Reference**:

The final gate MUST NOT be marked COMPLETE until:
1. `python3 .aget/patterns/release/post_release_validation.py --version X.Y.Z` returns exit code 0
2. All user-centric criteria in SOP Definition of Done (L553) are verified

See: `sops/SOP_release_process.md` Section "Definition of Done (L553)"

---

## Phase Plan

### Gate -1: Pre-Execution Evidence ⏳

<!-- [RECOMMENDED] Per CAP-PP-017: Verify prerequisites before implementation -->

**Objective**: Verify all prerequisites are met before execution begins
**Principal Checkpoint**: OPTIONAL

**Deliverables**:
1. [ ] Scope definition complete
2. [ ] Dependencies identified and resolved
3. [ ] Risk assessment complete
4. [ ] Implementation approach documented

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G-1.1 | Scope section complete | YES | ⏳ |
| V-G-1.2 | Dependencies resolved or documented | YES | ⏳ |
| V-G-1.3 | Risk assessment exists | NO | ⏳ |

**DECISION POINT**: Ready for implementation? [GO/NO-GO]

---

### Gate 0: {Gate Name} ⏳

**Objective**: {What this gate achieves}
**Principal Checkpoint**: {REQUIRED | OPTIONAL}

**Deliverables**:
1. [ ] {Deliverable 1}
2. [ ] {Deliverable 2}

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G0.1 | {Verification criterion} | YES | ⏳ |
| V-G0.2 | {Verification criterion} | YES | ⏳ |

**DECISION POINT**: {Question}? [GO/NO-GO]

---

### Gate 1: {Gate Name} ⏳

**Objective**: {What this gate achieves}
**Principal Checkpoint**: {REQUIRED | OPTIONAL}

**Deliverables**:
1. [ ] {Deliverable 1}
2. [ ] {Deliverable 2}

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G1.1 | {Verification criterion} | YES | ⏳ |
| V-G1.2 | {Verification criterion} | NO | ⏳ |

**DECISION POINT**: {Question}? [GO/NO-GO]

---

### Gate N: Validation & Finalization ⏳

**Objective**: Validate and close project
**Principal Checkpoint**: REQUIRED

**Deliverables**:
1. [ ] All prior gates validated
2. [ ] Retrospective complete
3. [ ] Follow-on work documented
4. [ ] Status updated to COMPLETE

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-GN.1 | All prior V-tests passed | YES | ⏳ |
| V-GN.2 | Retrospective complete (8 subsections) | YES | ⏳ |

**DECISION POINT**: Project complete? [COMPLETE]

---

## Success Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| {Criterion 1} | {Target} | — | ⏳ |
| {Criterion 2} | {Target} | — | ⏳ |

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation | Status |
|------|--------|-------------|------------|--------|
| R1: {Risk description} | {High|Medium|Low} | {High|Medium|Low} | {Mitigation strategy} | Open |
| R2: {Risk description} | {High|Medium|Low} | {High|Medium|Low} | {Mitigation strategy} | Open |

---

## Retrospective

<!-- Complete when status changes to COMPLETE -->

### Project Summary

| Field | Value |
|-------|-------|
| Project ID | {id} |
| Duration | {actual} |
| Status | COMPLETE |
| Deliverables | {X of Y delivered} |

### What Went Well

| Item | Evidence | Impact |
|------|----------|--------|
| {item} | {evidence} | {impact} |

### What Could Improve

| Item | Root Cause | Recommendation |
|------|------------|----------------|
| {item} | {cause} | {recommendation} |

### Metrics vs. Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| {metric} | {target} | {actual} | {MET|MISSED} |

### Key Decisions Made

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | {decision} | {choice} | {why} |

### Risks Realized

| Risk | Realized? | Notes |
|------|-----------|-------|
| R1 | {Yes|No} | {notes} |

### Follow-On Work Identified

| Priority | Project | Scope | Destination |
|----------|---------|-------|-------------|
| P1 | {name} | {scope} | {where} |

### Lessons Learned

1. {lesson 1}
2. {lesson 2}

### Project Closure Checklist

- [ ] All gates passed (all BLOCKING V-tests ✅)
- [ ] All deliverables verified
- [ ] Retrospective complete (all 8 subsections)
- [ ] Follow-on work documented
- [ ] L-docs filed if applicable
- [ ] Status updated to COMPLETE

---

## References

- {Reference 1}: {Brief description}
- {Reference 2}: {Brief description}

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {YYYY-MM-DD} | Initial plan |

---

*PROJECT_PLAN_{name}_v1.0.md*
*Created: {YYYY-MM-DD}*
*Owner: {agent-name}*
*Status: PROPOSED*
