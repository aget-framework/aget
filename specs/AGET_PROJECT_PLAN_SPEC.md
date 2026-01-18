# AGET PROJECT_PLAN Specification

**Version**: 1.2.0
**Status**: Active
**Category**: Process (Planning)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-18
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_PROJECT_PLAN_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.7, Issue #30
**Related Specs**: AGET_RELEASE_SPEC, AGET_REASONING_SPEC, AGET_SOP_SPEC

---

## Abstract

This specification defines requirements for PROJECT_PLAN documents in the AGET framework. PROJECT_PLANs govern multi-gate work with structured deliverables, verification tests, and decision points. This spec formalizes patterns validated in PROJECT_PLAN_v3.0.0 through v3.2.0.

## Motivation

Planning challenges observed in practice:

1. **Missing verification**: Gate 6 marked complete but never verified (L440)
2. **Inconsistent formats**: PROJECT_PLANs varied in structure
3. **No velocity tracking**: Estimated vs actual effort not captured (L426)
4. **Missing rollback**: No documented recovery when gates fail
5. **Declarative completion**: Checkboxes without executable verification

L186 (PROJECT_PLAN Not TodoWrite), L426 (Effort Estimation), and L440 (Gate Verification Tests) revealed these gaps.

## Scope

**Applies to**: All PROJECT_PLAN documents for AGET releases and major features.

**Defines**:
- Required sections for PROJECT_PLANs
- Gate structure requirements
- Status vocabulary
- Verification test format (V-tests)
- Success criteria format
- Traceability requirements

**Does not cover**:
- Release execution (see AGET_RELEASE_SPEC)
- Retrospective process (see AGET_REASONING_SPEC CAP-REASON-008)
- SOP format (see AGET_SOP_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "planning"
    version: "1.0.0"
    inherits: "aget_core"

  plan_structure:
    PROJECT_PLAN:
      skos:definition: "Governance document for multi-gate work with verification"
      aget:naming: "PROJECT_PLAN_{scope}_v{M}.{m}.md"
      skos:example: "PROJECT_PLAN_v3.2.0_specification_architecture.md"
      skos:related: ["CAP-PP-001"]

    Gate:
      skos:definition: "Logical unit of work with deliverables and verification"
      aget:structure: ["Objective", "Deliverables", "V-tests", "Checklist", "Decision Point"]
      skos:related: ["CAP-PP-002"]

    V_Test:
      skos:definition: "Verification test with executable command and expected output"
      aget:naming: "V{gate}.{test}"
      skos:example: "V7.0.1"
      skos:related: ["CAP-PP-011", "L440"]

    Decision_Point:
      skos:definition: "Explicit pause requiring approval before next gate"
      aget:format: "Proceed to Gate {N}? [GO/NO-GO]"
      skos:related: ["CAP-PP-002", "L42"]

  status_vocabulary:
    Plan_Status:
      skos:definition: "Overall PROJECT_PLAN status"
      aget:values: ["Draft", "In Progress", "Complete", "Abandoned"]
      skos:related: ["CAP-PP-003"]

    Gate_Status:
      skos:definition: "Individual gate status"
      aget:values: ["Pending", "In Progress", "Complete", "Blocked", "Skipped"]

    Deliverable_Status:
      skos:definition: "Individual deliverable status"
      aget:values: ["Pending", "Done", "Skipped", "Deferred"]

  metrics:
    Success_Criteria:
      skos:definition: "Measurable targets for plan success"
      aget:format: "SC-{N}: {criterion} | {metric} | {target}"
      skos:related: ["CAP-PP-005"]

    Velocity:
      skos:definition: "Ratio of estimated to actual effort"
      aget:format: "Gate {N}: {estimated} → {actual} ({ratio})"
      skos:related: ["CAP-PP-009", "L426"]

  anti_patterns:
    Declarative_Completion:
      skos:definition: "Marking deliverable complete via checkbox without V-test"
      aget:anti_pattern: true
      skos:related: ["L440"]

    Scope_Creep:
      skos:definition: "Adding work mid-gate without decision point"
      aget:anti_pattern: true
      skos:related: ["L342"]
```

---

## Requirements

### CAP-PP-001: PROJECT_PLAN Format

**SHALL** requirements for PROJECT_PLAN structure:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-001-01 | PROJECT_PLAN SHALL have header with version, status, theme | Identification |
| CAP-PP-001-02 | PROJECT_PLAN SHALL have Executive Summary | Context |
| CAP-PP-001-03 | PROJECT_PLAN SHALL have Scope (in/out) | Boundaries |
| CAP-PP-001-04 | PROJECT_PLAN SHALL have Success Criteria | Measurability |
| CAP-PP-001-05 | PROJECT_PLAN SHALL have Gates section | Structure |
| CAP-PP-001-06 | PROJECT_PLAN SHALL have References section | Traceability |

**Required Sections:**

```markdown
# PROJECT_PLAN: {Title}

**Version**: {M}.{m}.{p}
**Status**: {Draft|In Progress|Complete|Abandoned}
**Theme**: {Short description}
**Tracking**: {GitHub milestone or issue}

## Executive Summary
{What, why, key outcomes}

## Scope
**In Scope:** {Included work}
**Out of Scope:** {Excluded work, deferred items}

## Success Criteria
| Criterion | Metric | Target | Actual | Verification |
|-----------|--------|--------|--------|--------------|

## Gates
{Gate sections per CAP-PP-002}

## References
{L-docs, SOPs, related plans}
```

### CAP-PP-002: Gate Structure

**SHALL** requirements for gate structure:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-002-01 | Gate SHALL have Objective | Purpose |
| CAP-PP-002-02 | Gate SHALL have Deliverables table | Clarity |
| CAP-PP-002-03 | Gate SHALL have V-tests | Verification |
| CAP-PP-002-04 | Gate SHALL have Checklist | Tracking |
| CAP-PP-002-05 | Gate SHALL have Decision Point | Control |

**Gate Structure:**

```markdown
## Gate {N}: {Title}

**Objective:** {What this gate achieves}
**Status:** {Pending|In Progress|Complete|Blocked|Skipped}

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G{N}.1 | {Item} | {Owner} | {Status} |

### Verification Tests

#### V{N}.1: {Description}
```bash
{executable_command}
```
**Expected:** {expected_output}
**BLOCKING:** (optional) Do NOT proceed if FAIL

### Checklist

- [ ] V{N}.1 PASS: {description}
- [ ] V{N}.2 PASS: {description}

**Decision Point:** Proceed to Gate {N+1}? [GO/NO-GO]
```

### CAP-PP-003: Status Vocabulary

**SHALL** requirements for status tracking:

| ID | Requirement | Values | Usage |
|----|-------------|--------|-------|
| CAP-PP-003-01 | Plan status SHALL use standard values | Draft, In Progress, Complete, Abandoned | Header |
| CAP-PP-003-02 | Gate status SHALL use standard values | Pending, In Progress, Complete, Blocked, Skipped | Gate header |
| CAP-PP-003-03 | Status transitions SHALL be documented | In execution log | Audit trail |

**Status Transitions:**

```
Plan: Draft → In Progress → Complete
              ↓
           Abandoned

Gate: Pending → In Progress → Complete
                    ↓
                 Blocked → (resolved) → In Progress
                    ↓
                 Skipped (with justification)
```

### CAP-PP-004: Rollback Requirements

**SHALL** requirements for rollback planning:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-004-01 | Gates with production impact SHALL have rollback plan | Recovery |
| CAP-PP-004-02 | Rollback plan SHALL include verification | Confidence |
| CAP-PP-004-03 | Failed V-tests SHALL trigger rollback consideration | Safety |

**Rollback Section Format:**

```markdown
### Rollback Plan

**Trigger:** {When rollback is invoked}
**Steps:**
1. {Rollback step}
2. {Verification}

**Verification:**
```bash
{command to verify rollback}
```
```

### CAP-PP-005: Success Criteria

**SHALL** requirements for success criteria:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-005-01 | Success criteria SHALL be measurable | Objectivity |
| CAP-PP-005-02 | Success criteria SHALL have target values | Clarity |
| CAP-PP-005-03 | Success criteria SHALL have verification method | Accountability |
| CAP-PP-005-04 | Actual values SHALL be recorded at completion | Learning |

**Success Criteria Format:**

```markdown
| Criterion | Metric | Target | Actual | Verification |
|-----------|--------|--------|--------|--------------|
| SC-1: Spec count | Active specs | ~24 | — | `ls specs/*.md \| wc -l` |
| SC-2: Coverage | Test coverage | ≥80% | — | `pytest --cov` |
```

### CAP-PP-006: Risk Assessment

**SHOULD** requirements for risk assessment:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-006-01 | Major plans SHOULD include Risk Assessment | Mitigation |
| CAP-PP-006-02 | Risks SHOULD have impact and probability | Prioritization |
| CAP-PP-006-03 | Risks SHOULD have mitigation strategies | Planning |

**Risk Matrix Format:**

```markdown
## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| R1: {description} | High/Med/Low | High/Med/Low | {mitigation} |
```

### CAP-PP-007: Traceability Matrix

**SHALL** requirements for traceability:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-007-01 | PROJECT_PLAN SHALL trace to issues/L-docs | Accountability |
| CAP-PP-007-02 | Each gate SHALL trace to requirements | Coverage |
| CAP-PP-007-03 | Deliverables SHALL trace to V-tests | Verification |

**Traceability Matrix Format:**

```markdown
## Traceability Matrix

### Issues → Gates
| Issue | Description | Gate | Deliverable |
|-------|-------------|------|-------------|
| #30 | PROJECT_PLAN_SPEC | G2 | G2.7 |

### L-docs → Deliverables
| L-doc | Requirement | Gate | Status |
|-------|-------------|------|--------|
| L440 | V-tests | All | Active |
```

### CAP-PP-008: Effort Estimation

**SHOULD** requirements for effort estimation (L426):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-008-01 | Gates SHOULD have effort estimates | Planning |
| CAP-PP-008-02 | Discovery work SHOULD use ranges | Uncertainty |
| CAP-PP-008-03 | Pattern-clear work MAY use point estimates | Confidence |

**Estimation Tiers:**

| Tier | Confidence | Format | Example |
|------|------------|--------|---------|
| Discovery | Low (<50%) | Range (2-8h) | Research, spike |
| Pattern-Similar | Medium (50-80%) | Range (1-3h) | Similar to previous |
| Pattern-Clear | High (>80%) | Point (2h) | Repeated pattern |

**Estimation Format:**

```markdown
### Effort Estimates

| Gate | Tier | Estimate | Notes |
|------|------|----------|-------|
| G1 | Pattern-Clear | 2h | Similar to v3.1.0 |
| G2 | Discovery | 4-12h | New specs |
```

### CAP-PP-009: Velocity Analysis

**SHOULD** requirements for velocity tracking:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-009-01 | Actual effort SHOULD be recorded | Learning |
| CAP-PP-009-02 | Velocity ratio SHOULD be calculated | Calibration |
| CAP-PP-009-03 | Significant variance SHOULD be explained | Understanding |

**Velocity Format:**

```markdown
## Velocity Analysis

| Gate | Estimated | Actual | Ratio | Notes |
|------|-----------|--------|-------|-------|
| G0 | 30m | 45m | 1.5x | More issues than expected |
| G1 | 2h | 1h45m | 0.88x | Pattern-clear execution |
```

### CAP-PP-010: References

**SHALL** requirements for references:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-010-01 | PROJECT_PLAN SHALL list related L-docs | Context |
| CAP-PP-010-02 | PROJECT_PLAN SHALL list related SOPs | Procedures |
| CAP-PP-010-03 | PROJECT_PLAN SHALL list related specs | Requirements |

**References Format:**

```markdown
## References

### L-docs
- L440: Manager Migration Verification Gap
- L426: Effort Estimation Patterns

### SOPs
- SOP_release_process.md

### Specs
- AGET_RELEASE_SPEC.md
- AGET_REASONING_SPEC.md
```

### CAP-PP-011: Gate Verification Tests (L440 Critical)

**SHALL** requirements for gate verification (L440):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-011-01 | Every gate SHALL have V-tests | Prevents declarative completion |
| CAP-PP-011-02 | V-tests SHALL be executable commands | No manual verification |
| CAP-PP-011-03 | V-tests SHALL have expected output | Clear pass/fail |
| CAP-PP-011-04 | V-tests SHALL use V{gate}.{test} naming | Identification |
| CAP-PP-011-05 | BLOCKING V-tests SHALL halt on failure | Critical path |
| CAP-PP-011-06 | V-test results SHALL be recorded | Audit trail |

**V-Test Format:**

```markdown
#### V{gate}.{test}: {description}
```bash
{executable_command}
```
**Expected:** {expected_output}
**BLOCKING:** (optional) Do NOT proceed if FAIL
**Actual:** (recorded at execution)
```

**V-Test Naming:**

| Format | Meaning | Example |
|--------|---------|---------|
| V0.1 | Gate 0, Test 1 | V0.1: Milestone exists |
| V7.0.1 | Gate 7, Sub-gate 0, Test 1 | V7.0.1: Manager version |
| V{N}.{M} | Gate N, Test M | V2.3: Spec exists |

**Critical V-Test (BLOCKING):**

```markdown
#### V7.0.1: Manager version is {VERSION} (R-REL-006)
```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='{VERSION}' else 'FAIL')"
```
**Expected:** PASS
**BLOCKING:** Do NOT proceed if FAIL
```

---

### CAP-PP-012: Plan Comprehensibility (L502)

**SHOULD** requirements for plan size and readability:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-012-01 | PROJECT_PLAN SHOULD be ≤1000 lines | Cognitive load, tool limits |
| CAP-PP-012-02 | Plans >1000 lines SHOULD use decomposition or summary pattern | Maintainability |
| CAP-PP-012-03 | V-tests MAY be extracted to separate registry for large plans | Modularity |

**Size Classification:**

| Size | Classification | Action |
|------|----------------|--------|
| ≤500 lines | Optimal | None required |
| 501-1000 lines | Acceptable | Monitor growth |
| 1001-1500 lines | Warning | Consider decomposition |
| >1500 lines | Oversized | Decompose or extract |

**Decomposition Patterns:**

1. **Child Plans**: Split into `PROJECT_PLAN_{scope}_phase{N}.md`
2. **V-Test Registry**: Extract to `tests/vtest_{plan_id}.md`
3. **Summary + Detail**: Executive summary standalone, details in appendix

**Rationale (L502):**

PROJECT_PLAN_v3.2.0 (25,088 tokens, 1,641 lines) exceeded the Read tool's 25,000 token limit. Root cause analysis revealed CAP-PP-011 (V-tests) optimized for verification without constraining comprehensibility—a single-axis optimization anti-pattern.

**Tool Constraints:**

| Constraint | Limit | Implication |
|------------|-------|-------------|
| Read tool tokens | 25,000 | ~1,500 lines max |
| Context window | Varies | Large plans fragment context |
| Human working memory | 7±2 chunks | ~500 lines optimal |

---

### CAP-PP-013: Plan Closure Checklist

**SHALL** requirements for plan completion:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-013-01 | PROJECT_PLAN SHALL have Closure Checklist section | Completeness |
| CAP-PP-013-02 | Closure SHALL verify all V-tests passed | Verification |
| CAP-PP-013-03 | Closure SHALL record actual vs estimated effort | Learning |
| CAP-PP-013-04 | Closure SHALL update status to Complete or Abandoned | State management |

---

### CAP-PP-014: Operational Template Structure (Issue #260)

**SHALL** requirements for operational PROJECT_PLAN templates:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-014-01 | Template SHALL support operational (non-release) PROJECT_PLANs | Versatility |
| CAP-PP-014-02 | Template SHALL include optional "Operational Context" section | Distinguish from release plans |
| CAP-PP-014-03 | Template SHALL support recurring task tracking | Maintenance tasks |
| CAP-PP-014-04 | Template SHALL mark release-specific sections as conditional | Clarity |

**Operational vs Release:**

| Attribute | Release PROJECT_PLAN | Operational PROJECT_PLAN |
|-----------|---------------------|-------------------------|
| Version tracking | Required | Optional |
| CHANGELOG entry | Required | N/A |
| Release checklist | Required | N/A |
| Recurring tasks | N/A | Supported |
| Example | PROJECT_PLAN_v3.4.0_*.md | PROJECT_PLAN_kb_audit_q1.md |

**Origin**: Issue #260 (PROJECT_PLAN operational template)

---

### CAP-PP-015: Template and SOP Improvement Actions (Issue #254)

**SHALL** requirements from L521 action items:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-015-01 | PROJECT_PLAN template SHALL include version-bearing file section | L521 gap |
| CAP-PP-015-02 | SOPs SHALL cross-reference related PROJECT_PLAN templates | Traceability |
| CAP-PP-015-03 | Version source SHALL be explicit (spec, SOP, or inline) | Clarity |
| CAP-PP-015-04 | Template SHALL include "Related SOPs" section | Governance |

**Origin**: Issue #254 (PROJECT_PLAN and SOP Template Improvements), L521 (Version-Bearing File Gap)

---

### CAP-PP-016: Finalization Automation Pattern (Issue #253)

**SHOULD** requirements for plan finalization automation:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-016-01 | PROJECT_PLAN SHOULD include finalization checklist in template | Consistency |
| CAP-PP-016-02 | Finalization checklist SHOULD verify all gates complete | Completeness |
| CAP-PP-016-03 | Finalization checklist SHOULD trigger retrospective | Learning |
| CAP-PP-016-04 | Template MAY support finalize_project_plan.py automation | Efficiency |

**Finalization Checklist Format:**

```markdown
## Finalization Checklist

- [ ] All gates marked Complete or Skipped (with justification)
- [ ] All V-tests executed with results recorded
- [ ] Velocity analysis completed
- [ ] Retrospective captured (per CAP-REASON-008)
- [ ] Status updated to Complete
- [ ] Related issues closed
```

**Origin**: Issue #253 (Project Finalization Automation Pattern)

---

### CAP-PP-017: Gate -1 Evidence Verification (Issue #68)

**SHALL** requirements for pre-execution evidence:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-017-01 | PROJECT_PLAN SHALL include Gate -1 for pre-execution evidence | Readiness |
| CAP-PP-017-02 | Gate -1 SHALL verify prerequisites are met | Dependencies |
| CAP-PP-017-03 | Gate -1 SHALL document prior art and related work | Context |
| CAP-PP-017-04 | Gate -1 evidence SHALL be verifiable | Accountability |

**Gate -1 Structure:**

```markdown
## Gate -1: Evidence Verification (Pre-Execution)

**Objective:** Verify prerequisites and context before execution begins

### Deliverables

| ID | Deliverable | Status |
|----|-------------|--------|
| G-1.1 | Prerequisites documented | |
| G-1.2 | Prior art reviewed | |
| G-1.3 | Dependencies verified | |

### Verification Tests

#### V-1.1: Prerequisites exist
```bash
# Verify required files/conditions exist
```
**Expected:** All prerequisites present

**Decision Point:** Proceed to Gate 0? [GO/NO-GO]
```

**Origin**: Issue #68 (Gate -1 Evidence Verification for PROJECT_PLAN)

---

### CAP-PP-018: Retrospective Requirements (Issue #52, L462)

**SHALL** requirements for plan retrospectives:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-PP-018-01 | PROJECT_PLAN SHALL include Retrospective section | Learning |
| CAP-PP-018-02 | Retrospective SHALL capture what worked | Positive patterns |
| CAP-PP-018-03 | Retrospective SHALL capture what didn't work | Improvement areas |
| CAP-PP-018-04 | Retrospective SHALL generate action items | Actionability |
| CAP-PP-018-05 | Action items SHALL trace to future work or L-docs | Closure |

**Retrospective Format:**

```markdown
## Retrospective

### What Worked
1. {Positive pattern to repeat}
2. {Effective approach}

### What Didn't Work
1. {Issue encountered}
2. {Approach to avoid}

### Action Items
| Item | Owner | Target | Status |
|------|-------|--------|--------|
| Document {learning} as L-doc | {owner} | {date} | Pending |
| Update {SOP/template} | {owner} | {date} | Pending |
```

**Origin**: Issue #52 (PROJECT_PLAN Template Improvements), L462 (Retrospective Capture Gap)

---

## PROJECT_PLAN Template

See: `templates/PROJECT_PLAN_TEMPLATE.md` (G2.9 deliverable)

**Key sections:**
1. Header (version, status, theme, tracking)
2. Executive Summary
3. Scope (in/out)
4. Success Criteria (measurable)
5. V-Test Summary (gate coverage)
6. Traceability Matrix
7. Gates (with V-tests and decision points)
8. References
9. Velocity Analysis (post-execution)
10. Retrospective (per CAP-REASON-008)

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-PP-001-* | validate_project_plan.py | Planned |
| CAP-PP-002-* | validate_project_plan.py | Planned |
| CAP-PP-003-* | Manual review | Manual |
| CAP-PP-011-* | V-test execution | Manual |
| CAP-PP-012-* | validate_artifact_size.py | Planned |

---

## Anti-Patterns

### Anti-Pattern 1: Declarative Completion (L440)

```markdown
❌ ANTI-PATTERN: Checkbox without V-test

### Gate 6 Checklist
- [x] Manager version updated to 3.1.0  ← Never verified!
```

```markdown
✅ CORRECT: V-test with result

### Gate 6 Checklist
- [x] V6.0.1 PASS: Manager version is 3.1.0 ✅

#### V6.0.1: Manager version is 3.1.0
```bash
python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])"
```
**Expected:** 3.1.0
**Actual:** 3.1.0 ✅
```

### Anti-Pattern 2: Missing Decision Points

```markdown
❌ ANTI-PATTERN: No explicit approval

### Gate 1 Complete

Moving on to Gate 2...
```

```markdown
✅ CORRECT: Explicit decision point

### Gate 1 Complete

**Decision Point:** Proceed to Gate 2?

[User response required: GO/NO-GO]
```

### Anti-Pattern 3: Scope Creep Mid-Gate

```markdown
❌ ANTI-PATTERN: Adding work without decision

### Gate 2 (In Progress)

G2.1: Create spec ✅
G2.2: Create spec ✅
G2.8: (New) Also update SOP ← Scope creep!
```

```markdown
✅ CORRECT: Defer to next gate or plan

### Gate 2 (In Progress)

G2.1: Create spec ✅
G2.2: Create spec ✅

**Note:** SOP update identified as follow-on work.
See G2.8 (already in plan) or defer to v3.3.0.
```

---

## References

- L42: Gate Boundary Discipline
- L186: PROJECT_PLAN Not TodoWrite
- L340: Execution Governance Artifact Requirement
- L342: Session Scope Validation
- L426: Effort Estimation Patterns
- L440: Manager Migration Verification Gap
- L502: Artifact Comprehensibility Gap
- CAP-REASON-008: Retrospective Requirement (AGET_REASONING_SPEC)
- SOP_release_process.md

---

## Changelog

### v1.2.0 (2026-01-18)

- Added CAP-PP-013: Plan Closure Checklist
- Added CAP-PP-014: Operational Template Structure (Issue #260)
- Added CAP-PP-015: Template and SOP Improvement Actions (Issue #254, L521)
- Added CAP-PP-016: Finalization Automation Pattern (Issue #253)
- Added CAP-PP-017: Gate -1 Evidence Verification (Issue #68)
- Added CAP-PP-018: Retrospective Requirements (Issue #52, L462)
- Part of v3.4.0 Governance Formalization

### v1.1.0 (2026-01-10)

- Added CAP-PP-012: Plan Comprehensibility (L502)
- Size classification table (optimal/acceptable/warning/oversized)
- Decomposition patterns (child plans, V-test registry, summary+detail)
- Tool constraints documentation
- Added validate_artifact_size.py to enforcement table

### v1.0.0 (2026-01-04)

- Initial specification
- Defined CAP-PP-001 through CAP-PP-011
- Gate structure requirements
- V-test format standard (L440)
- Success criteria format
- Velocity analysis format
- Traceability requirements
- Closes Issue #30

---

*AGET_PROJECT_PLAN_SPEC.md — Planning standards for AGET framework*
*"A checkbox is not a verification. A passing test is."* — L440
