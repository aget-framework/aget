# AGET PROJECT_PLAN Specification

**Version**: 1.5.0
**Status**: Active
**Category**: Process (Planning)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-08-17
**Author**: aget-framework
**Location**: `aget/specs/AGET_PROJECT_PLAN_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.7, Issue #30
**Related Specs**: AGET_RELEASE_SPEC, AGET_5D_COMPONENTS_SPEC (holds CAP-REASON-008; supersedes the
archived AGET_REASONING_SPEC), AGET_SOP_SPEC

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
- Retrospective process (see AGET_5D_COMPONENTS_SPEC CAP-REASON-008 — the REASONING dimension was
  folded into AGET_5D_COMPONENTS_SPEC; `AGET_REASONING_SPEC.md` now exists only under `specs/archive/`
  and still self-declares `Status: Active`, so do not cite it)
- SOP format (see AGET_SOP_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "planning"
    version: "1.1.0"
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
      aget:values: ["Draft", "In Progress", "Staged", "Implemented-Awaiting-Deployment-Evidence", "Piloted", "Complete", "Closed", "Closed (Partial)", "Abandoned", "Superseded"]
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
| CAP-PP-001-07 *(v1.3.0)* | PROJECT_PLAN SHALL have a `Parent Goal` header field (committed Goal id, or `(none)` + rationale) and a **Benefit hypothesis** block (CAP-PP-020) | Value linkage (rulings 2/6, 2026-07-19) |

**Required Sections:**

```markdown
# PROJECT_PLAN: {Title}

**Version**: {M}.{m}.{p}
**Plan_Status**: {Draft|In Progress|Staged|Implemented-Awaiting-Deployment-Evidence|Piloted|Complete|Closed|Closed (Partial)|Abandoned|Superseded}
**Plan_Status_Annotation**: {optional provenance metadata; never a state selector}
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
| CAP-PP-003-01 | Plan status SHALL use the closed standard enumeration | Draft, In Progress, Staged, Implemented-Awaiting-Deployment-Evidence, Piloted, Complete, Closed, Closed (Partial), Abandoned, Superseded | Header |
| CAP-PP-003-02 | Gate status SHALL use standard values | Pending, In Progress, Complete, Blocked, Skipped | Gate header |
| CAP-PP-003-03 | Status transitions SHALL be documented | In execution log | Audit trail |

> **Field and comparison semantics (v1.5.0)**: the authoritative field carrying CAP-PP-003-01's enum is
> **`Plan_Status`**; `**Status**` is a recognized legacy alias. How the enum is *resolved* when both
> fields are present, and how two values are *normalized* before comparison, are specified by
> **CAP-PP-013-11** and **CAP-PP-013-13** respectively. `Plan_Status_Annotation` is separate,
> non-authoritative provenance metadata. This specification is the sole normative vocabulary source;
> conventions, skills, and evaluators consume it and SHALL NOT add, absorb, or alias a state.

**Status Transitions:**

```
Plan: Draft → In Progress → Staged / Implemented-Awaiting-Deployment-Evidence / Piloted
         ↓          ↓
  Abandoned / Superseded     Complete / Closed / Closed (Partial) / Abandoned / Superseded

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
- AGET_5D_COMPONENTS_SPEC.md  (REASONING dimension; the standalone AGET_REASONING_SPEC.md is archived)
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
| CAP-PP-013-02 | Closure SHALL record every V-test result; `Complete` requires all to pass, while a reasoned disposition SHALL account every non-pass under CAP-PP-013-18 | Verification |
| CAP-PP-013-03 | Closure SHALL record actual vs estimated effort | Learning |
| CAP-PP-013-04 | Closure SHALL update **`Plan_Status`** to the selected terminal disposition only after CAP-PP-013-22 succeeds | State management |

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
- [ ] Retrospective captured (per AGET_5D_COMPONENTS_SPEC CAP-REASON-008)
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
10. Retrospective (per AGET_5D_COMPONENTS_SPEC CAP-REASON-008)

### CAP-PP-019: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PP-019-01 | ubiquitous | The SYSTEM shall validate all PROJECT_PLAN documents against CAP-PP-001 structural requirements before accepting them as governance artifacts. |
| CAP-PP-019-02 | event-driven | WHEN all V-tests for a Gate pass, THEN the SYSTEM shall present the Gate's Decision_Point for principal approval. |
| CAP-PP-019-03 | conditional | IF a Gate has 4 or more deliverables, THEN the SYSTEM shall insert a mid-gate checkpoint at the 50% mark (L002). |
| CAP-PP-019-04 | event-driven | WHEN the principal authorizes a Gate Decision_Point (CAP-PP-019-02), the canonical authorization mechanism is `/aget-go` (SKILL-048 v1.0.0). The skill writes an authorization record to the active session file (CAP-GO-001), verifies the principle triad against the gate's referenced spec + V-tests + L-doc evidence (CAP-GO-003), and applies Healthy Friction (CAP-GO-004) when any pre-condition is UNMET. Free-text "go" / "yes" / "proceed" remains valid for backward compat but is non-auditable; `/aget-go` is preferred for any gate that involves spec amendment, fleet-wide change, or >1 SU work. |

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-PP-001 | CAP-PP-001 | automated | PROJECT_PLAN contains required sections (Context, Gates, Success Criteria) |
| V-PP-002 | CAP-PP-002 | automated | Each gate has go/no-go decision point and deliverables list |
| V-PP-003 | CAP-PP-003 | manual | Due diligence section references 3+ KB precedents |
| V-PP-004 | CAP-PP-011 | inspection | Gate completion includes V-test execution evidence |
| V-PP-005 | CAP-PP-012 | automated | Artifact sizes within thresholds |
| V-PP-006 | CAP-PP-018 | manual | Retrospective section present with minimum depth (not perfunctory) |
| V-PP-007 | CAP-PP-003 | automated | Plan status field is valid enum (Draft/In Progress/Complete/Abandoned) — aligned with CAP-PP-003-01 (v1.2.2 #1180 fix; semantic absorptions: Draft ⊇ PROPOSED, Abandoned ⊇ SUPERSEDED — see plan-body free-text for edge cases) |

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

## Authority Model

```yaml
authority:
  applies_to: "project_plan_creation_and_execution"

  governed_by:
    spec: "AGET_PROJECT_PLAN_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "Create PROJECT_PLANs for multi-gate work"
      - "Define gates with deliverables and V-tests"
      - "Execute gates within approved plan scope"
      - "Record velocity analysis and retrospectives"
      - "Track plan status transitions (Draft to In Progress)"
    requires_approval:
      - action: "Mark plan as Complete"
        approver: "principal"
      - action: "Skip or abandon a gate"
        approver: "principal"
      - action: "Expand scope mid-gate"
        approver: "principal"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Inviolables

- A gate SHALL NOT be represented complete without its V-test evidence, plan update, and the commit that
  records that update.
- A decision point SHALL NOT be crossed without the approval required by the governing plan.
- A terminal disposition SHALL NOT be asserted while an error, integrity finding, closure-record finding,
  or unmatched finding occurrence remains unresolved.
- A closer-authored requirement SHALL NOT be enforced as an entry criterion before the closer is allowed
  to author it.
- A consumer SHALL NOT create, absorb, or alias a plan state outside CAP-PP-003.

---

## Structural Requirements

```yaml
structure:
  plan_artifact:
    path_pattern: "planning/PROJECT_PLAN_*.md"
    authoritative_status_field: "Plan_Status"
    optional_annotation_field: "Plan_Status_Annotation"
  required_sections:
    - "Executive Summary"
    - "Scope"
    - "Success Criteria"
    - "Gates"
    - "References"
    - "Closure Checklist"
  gate_structure:
    required_components: ["Objective", "Deliverables", "V-tests", "Checklist", "Decision Point"]
  close_record:
    reasoned_disposition_section: "Unfinished at Close"
    finding_identity: ["reason_key", "affected_subject", "evidence_location"]
    verification_order: ["entry", "author", "reparse", "exit", "reconcile", "transition", "commit"]
  validators:
    format: "verification/validate_spec_format.py"
    project_plan: "scripts/close_gate_check.py"
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
- Retrospective Requirement → defined in AGET_5D_COMPONENTS_SPEC §CAP-REASON-008
- SOP_release_process.md

---

## Changelog

### v1.5.0 (2026-08-17)

- **Joint lifecycle contract** (gh#2250 + gh#2223): widens CAP-PP-003 to one authoritative state
  vocabulary and adds CAP-PP-013-14..22 plus V-PP-039..047 for ETVX lifecycle classes, explicit target
  disposition, finding identity/classes, `Unfinished at Close`, lawful transitions, disposition evidence,
  bounded legacy migration, and ordered close invariants.
- **Same-day correction to v1.4.0**: replaces lossy leading-clause truncation with separate
  `Plan_Status_Annotation` metadata and fail-safe legacy qualifier handling.
- **Format self-compliance**: adds the required Inviolables and Structural Requirements sections.
- **Publication constraint**: candidate only until the coherent Gate-3 implementation and Gate-3V
  independent verification are ready; no spec-only push.

### v1.4.0 (2026-08-16)

- **Amendment v1.4.0 — Evaluation Mode, Explicit Supersession, and Status Resolution** (gh#2250): adds CAP-PP-013-05..13 and V-PP-026..038. Gives the conformance evaluator a `closure`/`audit` mode, makes gate supersession explicit metadata rather than an inference from heading text, and specifies authoritative-status resolution plus the normalization applied before two status values are compared.
- **Corrections to existing surfaces** (not additive-only): the §Required Sections example header now shows `**Plan_Status**` rather than `**Status**`; CAP-PP-013-04 now names `Plan_Status` explicitly instead of the ambiguous "status"; CAP-PP-003 gains a forward reference to CAP-PP-013-11/-13 for field and comparison semantics.
- **Not implemented at publication**: `close_gate_check.py` honours none of CAP-PP-013-05..13 as of this version. Specification-level change only; the implementing repair is separately authorized.

### v1.2.2 (2026-05-02)

- **V-PP-007 dual fix** (gmelli/aget-aget#1180): (a) enum value rewrite `{PROPOSED/IN_PROGRESS/COMPLETE/SUPERSEDED}` → `{Draft/In Progress/Complete/Abandoned}` to align with CAP-PP-003-01 (line 214 — the canonical status-enum requirement); (b) CAP binding correction `CAP-PP-019` → `CAP-PP-003` (CAP-PP-019 is "EARS System-Level Requirements," not status enum). The two defects were independent but discovered together; resolution is one V-test row edit.
- Semantic absorption documented: `Draft` ⊇ both PROPOSED + Draft semantics; `Abandoned` ⊇ both SUPERSEDED + Abandoned semantics. Plans needing the distinction record it in plan-body free-text (e.g., "Status: Abandoned — superseded by `<other plan>`"). Premature 6-value enum violates L103.
- See: gmelli/aget-aget#1180, MEMO_d_1179_1180_reconciliation_2026_05_02.md § Principal Disposition

### v1.2.1 (2026-03-17)

- Added CAP-PP-019: EARS System-Level Requirements (L682 L0→L1 uplift)
- 3 requirements with SYSTEM subject, ubiquitous/event-driven/conditional patterns

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

---

## Amendment v1.3.0 — Value Accounting (goal/value-canon arc G2.2; principal rulings 2/5/6, 2026-07-19)

### CAP-PP-020: Benefit Hypothesis at Creation

A PROJECT_PLAN SHALL carry, at creation, a **falsifiable benefit hypothesis**: an "if this lands, then ⟨measurable improvement⟩, falsified by ⟨observable⟩" statement naming the benefit (PRINCE2/ISO 21502 Output→Outcome→Benefit chain; SAFe benefit-hypothesis pattern) evaluated against the plan's `Parent Goal` frame. WHERE no Parent Goal exists, the hypothesis SHALL name its beneficiary directly and the coverage instrument reports the un-parented state (CAP-GOAL-013). First instance: `PROJECT_PLAN_goal_value_canon_arc_v1.0.md` header (2026-07-19).

### CAP-PP-021: Close-Time Value Resolution (with Cost Side)

WHEN a PROJECT_PLAN transitions to a terminal state via `/aget-close-project`, the closure SHALL record a **value-resolution verdict**: (a) the benefit hypothesis resolved (REALIZED / PARTIAL / NOT-REALIZED / UNMEASURABLE-YET, with the observable cited); (b) evaluated against the Parent Goal's frame (an Outcome is frame-evaluated — C1002); and (c) the **cost side stated** — actual effort (from Velocity Analysis) plus governance overhead honestly estimated — so net value is never asserted from the benefit numerator alone (RQ9 finding, 4-seat critique 2026-07-19: value accounting without the denominator overstates net value; a ceremonial version of this requirement is worse than its absence). A verdict of UNMEASURABLE-YET SHALL name what observable would resolve it and when.

### V-PP-020 / V-PP-021

- V-PP-020: `/aget-create-project` scaffolds refuse-or-warn on a missing benefit-hypothesis block (template ships the stub).
- V-PP-021: `close_gate_check` flags a terminal close whose Retrospective lacks a value-resolution verdict; verdicts citing no observable are placeholder-substance (existing #1568 class).

---

## Amendment v1.4.0 — Evaluation Mode, Explicit Supersession, and Status Resolution (gh#2250; principal rulings 2026-08-16)

**Why**: a conformance evaluator that answers only one question — *"may this plan close?"* — cannot also
answer *"is this plan's record tidy?"* without one of the two answers being wrong. `/aget-close-project`
enforced exit criteria at the entry position and had no verification step after the closer's task, which
is an **ETVX** violation (IBM, 1980s — Entry / Task / Verification / eXit). The requirements below give
the evaluator a mode, make supersession explicit rather than inferred, and specify how two status-bearing
fields are resolved and compared.

**Scope note**: this amendment also *corrects* two pre-existing surfaces rather than only adding to them —
the §Required Sections example header (`**Status**` → `**Plan_Status**`) and CAP-PP-013-04's unnamed
status field. Both were legacy drift made ambiguous by CAP-PP-013-11.

### CAP-PP-013-05: Mode is an evaluator invocation input, not plan metadata

WHEN a conformance evaluator is invoked against a PROJECT_PLAN, the invocation SHALL specify mode ∈ {`closure`, `audit`}. WHERE no mode is specified, the evaluator SHALL use `closure`.

*Mode is deliberately not plan metadata: a plan carrying its own mode could set itself to `audit` and escape closure blocking. Mode is a property of the question, not of the thing questioned.*

### CAP-PP-013-06: Closure mode

IF mode is `closure` THEN the evaluator SHALL return a blocking verdict for any live non-terminal gate OR any contradictory plan state, irrespective of a terminal status declared in the header.

### CAP-PP-013-07: `legitimately-terminal` (reusable predicate)

A plan is `legitimately-terminal` IFF ALL of: **(a)** authoritative status resolves to exactly one terminal disposition of the CAP-PP-003 enum; **(b)** no second status-bearing field declares a different normalized exact state (per CAP-PP-013-11; normalization per CAP-PP-013-13 — class comparison is insufficient); **(c)** closure-checklist items are checked and V-tests recorded; and **(d)** exit-phase reconciliation has run with no unresolved blocking or error finding. Implementations SHALL NOT add another terminality condition.

### CAP-PP-013-08: Audit mode, with fallback

IF mode is `audit` AND the plan is `legitimately-terminal` THEN the evaluator SHALL report non-terminal gate stamps as HYGIENE and SHALL NOT block. WHERE the plan is NOT `legitimately-terminal`, audit SHALL fall back to closure behaviour.

*The fallback is what makes a contradictory plan block in both modes — not a separate rule.*

### CAP-PP-013-09: Supersession explicit; absence means live, immediately

A gate SHALL be treated as superseded ONLY WHERE it carries a valid `superseded_by`. The evaluator SHALL NOT infer supersession from heading text, ordering, position, or dates. WHERE absent, the gate SHALL be treated as live. Legacy plans remain parseable; a migration warning MAY accompany the verdict and SHALL NOT alter it.

*No grace period. Warnings accompany, never weaken.*

### CAP-PP-013-10: `superseded_by` validity

A `superseded_by` reference is valid IFF: (a) it uniquely resolves to exactly one gate; (b) that gate is in the same plan; (c) it is non-self; (d) the resulting reference graph is acyclic. A valid reference exempts **only the declaring gate**. IF any condition fails THEN the reference is INVALID and the declaring gate SHALL be treated as live.

### CAP-PP-013-11: Authoritative-status resolution

**`Plan_Status` is the sole canonical, authoritative state field and SHALL contain exactly one CAP-PP-003 enum value.** `**Status**` is a recognized **legacy alias**. `Plan_Status_Annotation` is separate, non-authoritative provenance metadata and SHALL NOT select, change, or establish terminality. WHERE only `Plan_Status` is present, it governs. WHERE only `**Status**` is present, the evaluator SHALL resolve it under CAP-PP-013-13 and emit a migration warning that SHALL NOT alter a verdict for a clean value. WHERE both state carriers are present, the evaluator SHALL compare their normalized exact states — NOT their terminal/non-terminal classes. IF the normalized states differ THEN the plan state is contradictory and SHALL NOT satisfy `legitimately-terminal`, **irrespective of which field is authoritative**.

*Two normative sources establish `Plan_Status`: `templates/PROJECT_PLAN_TEMPLATE.md` line 4, and this spec's own `status_vocabulary` block. The §Required Sections example previously showed `**Status**` and is corrected in this amendment. Prevalence was explicitly rejected as evidence of authority — a large population using the alias is equally consistent with a large population having drifted.*

*Exact-state comparison, not class comparison: `Complete` vs `Abandoned` are BOTH terminal and are the paradigm contradiction. Class comparison is a lossy projection that discards the disagreement the predicate exists to detect. Precedence must not hide disagreement — authority decides which value governs, never whether a conflict exists.*

### CAP-PP-013-12: Blocking / HYGIENE emission

Three separate obligations: **(a)** WHEN the evaluator emits a blocking finding, it SHALL return a nonzero exit status. **(b)** WHEN the evaluator emits a HYGIENE finding, that finding SHALL NOT alter the exit status. **(c)** The rendered output SHALL label HYGIENE findings distinctly from blocking findings.

*Distinguishability comes from (c); the exit status carries blocking-vs-non-blocking, which is a different question. An earlier draft required distinguishability "in both the exit status and the rendered output" while also requiring hygiene not to alter the exit status — it named a distinguisher and disabled it one sentence later.*

### CAP-PP-013-13: Status normalization

WHEN an evaluator reads a canonical state value, it SHALL normalize only markdown emphasis, Unicode symbols, case, and whitespace before exact matching against CAP-PP-003. A legacy value with a narrative suffix remains parseable with a migration warning. Its enum prefix MAY establish state only when the suffix matches the bounded provenance grammar `terminal-verb? ISO-date reference*`, the verb agrees with the disposition (`Complete→completed|closed`, `Closed→closed`, `Closed (Partial)→closed-partial`, `Abandoned→abandoned`, `Superseded→superseded`), and each reference is `gh#digits` or an absolute HTTPS URI. Any other suffix is ambiguous or meaning-changing and SHALL NOT establish terminality. The evaluator SHALL NOT consult a synonym, alias, or equivalence list.

*This corrects v1.4.0's lossy leading-clause truncation. `Complete — closed 2026-06-28 gh#123` is descriptive legacy provenance; `Complete — validation failed` is meaning-changing and cannot certify terminality.*

### Verification Tests — V-PP-026..038

| ID | Covers | Assertion |
|----|--------|-----------|
| V-PP-026 | CAP-PP-013-05 | undeclared mode defaults to closure |
| V-PP-027 | CAP-PP-013-06 | stale gate stamp under terminal header, closure mode → BLOCK |
| V-PP-028 | CAP-PP-013-08 | same plan, audit mode → HYGIENE, exit 0 |
| V-PP-029 | CAP-PP-013-06 | contradictory plan state, closure mode → BLOCK |
| V-PP-030 | CAP-PP-013-08 | contradictory plan state, audit mode → BLOCK via fallback |
| V-PP-031 | CAP-PP-013-09/10 | valid supersession exempts only the declaring gate |
| V-PP-032 | CAP-PP-013-10 | dangling / self / cyclic reference → declaring gate live |
| V-PP-033 | CAP-PP-013-08 | audit falls back when not `legitimately-terminal` |
| V-PP-034 | CAP-PP-013-11 | resolution: `Plan_Status` alone · legacy `Status` alone (+ non-verdict-changing warning) · both agreeing · both differing |
| V-PP-034a | CAP-PP-013-11 | exact-state contradiction: `Complete` vs `Abandoned` — both terminal — MUST read contradictory |
| V-PP-034b | CAP-PP-013-11 | precedence does not mask: authoritative field terminal, alias disagreeing → still contradictory |
| V-PP-035 | CAP-PP-013-12 | blocking finding → nonzero exit |
| V-PP-035a | CAP-PP-013-12 | hygiene-only → exit unchanged (0) |
| V-PP-035b | CAP-PP-013-12 | rendered output labels HYGIENE distinctly from blocking |
| V-PP-036 | CAP-PP-013-07 | `legitimately-terminal` direct — (a), (b), (c), (d) each independently falsified; no additional condition |
| V-PP-037 | CAP-PP-013-13 | descriptive legacy provenance resolves with warning; `Complete — validation failed` cannot establish terminality; `Complete` vs `Abandoned` remains contradictory |
| V-PP-038 | CAP-PP-013-13 | bounds: `Done` does NOT resolve to `Complete` (no synonym list); a non-enum value (`gate 2`) compares by leading clause and stays contradictory against `in progress` |

**Enforcement status at publication**: specification-level only. `scripts/close_gate_check.py` implements
none of CAP-PP-013-05..13 as of v1.4.0 — the implementing repair is tracked at gh#2250 and is a separate,
separately-authorized change. This is disclosed rather than left to be discovered: a reader MUST NOT infer
from this amendment that a deployed evaluator honours these modes today.

---

## Amendment v1.5.0 — Joint Lifecycle, Evaluation, and Close-Gate Contract (gh#2250 + gh#2223)

**Why**: v1.4.0 discarded every status suffix before interpreting it, so a meaning-changing value such as
`Complete — validation failed` could be read as clean. The close workflow also accepted five terminal
dispositions while CAP-PP-003 governed only two, and it evaluated closer-authored outputs as entry
criteria. This same-day correction joins the ruled status semantics, rich lifecycle vocabulary, finding
identity, document roundtrip, and ETVX ordering in one contract.

### CAP-PP-013-14: Lifecycle-class attribute (ETVX)

Every CAP-PP-013 requirement SHALL declare exactly one lifecycle class: `creator-scaffolded`,
`pre-close-verifiable`, or `closer-authored`. Creator-scaffolded material is structure or input supplied
before close; pre-close-verifiable conditions may block entry before mutation; closer-authored material
is produced by the close task and SHALL be verified only at exit. A requirement spanning classes SHALL
be decomposed.

| Requirement | Lifecycle class | Requirement | Lifecycle class |
|---|---|---|---|
| CAP-PP-013-01 | creator-scaffolded | CAP-PP-013-12 | pre-close-verifiable |
| CAP-PP-013-02 | closer-authored | CAP-PP-013-13 | pre-close-verifiable |
| CAP-PP-013-03 | closer-authored | CAP-PP-013-14 | pre-close-verifiable |
| CAP-PP-013-04 | closer-authored | CAP-PP-013-15 | pre-close-verifiable |
| CAP-PP-013-05 | pre-close-verifiable | CAP-PP-013-16 | pre-close-verifiable |
| CAP-PP-013-06 | pre-close-verifiable | CAP-PP-013-17 | pre-close-verifiable |
| CAP-PP-013-07 | closer-authored | CAP-PP-013-18 | closer-authored |
| CAP-PP-013-08 | pre-close-verifiable | CAP-PP-013-19 | pre-close-verifiable |
| CAP-PP-013-09 | creator-scaffolded | CAP-PP-013-20 | closer-authored |
| CAP-PP-013-10 | pre-close-verifiable | CAP-PP-013-21 | creator-scaffolded |
| CAP-PP-013-11 | creator-scaffolded | CAP-PP-013-22 | closer-authored |

This table is the machine-readable classification source. Consumers SHALL derive it rather than keep a
literal copy. The classes instantiate ETVX: entry, task, verification, exit remain distinct.

### CAP-PP-013-15: Explicit target disposition

WHEN a close is invoked, the invocation SHALL provide exactly one terminal disposition from CAP-PP-003.
No default exists. Free-form reason text explains a selection and SHALL NOT select or infer it. A CLI MAY
spell `Closed (Partial)` as `CLOSED-PARTIAL`; comparison and document storage use the canonical form.

### CAP-PP-013-16: Finding occurrence identity and semantic class

Each finding SHALL carry `reason_key`, `affected_subject`, optional `evidence_location`,
`source_requirement`, and the lifecycle class derived from CAP-PP-013-14. The first three fields establish
occurrence identity; source requirement and lifecycle class govern entry/exit routing. Matching is a
deterministic one-to-one bijection; set membership SHALL NOT consume duplicate occurrences. Every raw key
SHALL map to exactly one class:

| Semantic class | Raw finding keys |
|---|---|
| `substantive_work` | `gate_status_pending`, `vtest_pending`, `status_row_nonterminal`, `gate_heading_nonterminal` |
| `closure_record` | `unchecked_closure_item`, `placeholder_substance` |
| `integrity` | `dual_status_mask`, `supersession_not_explicit`, `release_close_guard_block`, `release_close_guard_error` |

An unknown raw key is an uncovered declared surface and SHALL fail closed until mapped here.

### CAP-PP-013-17: Waivability and evaluator-mode boundary

`closure_record` and `integrity` findings are never waivable. At exit, a reasoned disposition (`Closed`,
`Closed (Partial)`, `Abandoned`, `Superseded`) MAY account for each `substantive_work` occurrence through
CAP-PP-013-18. The raw `status_row_nonterminal` finding denotes an unchecked deliverable and SHALL block
in closure and audit mode under every disposition. HYGIENE is limited to stale gate-status presentation
on a plan that already satisfies CAP-PP-013-07; it SHALL NOT absorb closure-record, integrity, or
unchecked-deliverable findings.

### CAP-PP-013-18: `Unfinished at Close` document roundtrip

For a reasoned disposition with surviving `substantive_work` findings, the closer SHALL author exactly one
`## Unfinished at Close` table with header `| reason_key | affected_subject | disposition | note |` and
one row per finding occurrence. Row disposition is `deferred`, `obsolete`, or `accepted-incomplete`.
Deferred rows name a governed vehicle and reason; obsolete rows name a reason; accepted-incomplete rows
name authority, approval receipt, and reason. Pipes are escaped as `\|`. Empty fields, unknown or
duplicate note keys, duplicate headings, malformed escapes, orphan rows, and unmatched findings are
errors or blocking findings. The exit verifier SHALL reparse the mutated document and reconcile it
one-to-one before transition. `Complete` prohibits this section; a reasoned disposition with no surviving
finding omits it.

### CAP-PP-013-19: Lawful lifecycle transitions

| Source state | Lawful terminal targets |
|---|---|
| `Draft` | `Abandoned`, `Superseded` |
| `In Progress` | `Complete`, `Closed`, `Closed (Partial)`, `Abandoned`, `Superseded` |
| `Staged` | `Complete`, `Closed`, `Closed (Partial)`, `Abandoned`, `Superseded` |
| `Implemented-Awaiting-Deployment-Evidence` | `Complete`, `Closed`, `Closed (Partial)`, `Abandoned`, `Superseded` |
| `Piloted` | `Complete`, `Closed`, `Closed (Partial)`, `Abandoned`, `Superseded` |

Terminal dispositions are immutable; correction requires an explicitly recorded reopen to `In Progress`.
The three waiting states require an advancement pointer. `Complete` is unlawful while a required
downstream deployment observable is absent; the plan remains
`Implemented-Awaiting-Deployment-Evidence` under L656.

### CAP-PP-013-20: Disposition-specific assertion and evidence

| Disposition | Assertion | Required evidence |
|---|---|---|
| `Complete` | all scoped outcomes and exit criteria realized | live gates and V-tests complete; closure record complete; no `Unfinished at Close`; value verdict and actual effort |
| `Closed` | work terminated and all remainder rerouted or retired | reason and per-occurrence accounting; every deferred item names a vehicle |
| `Closed (Partial)` | a named realized subset is retained and all remainder accounted | realized-subset statement and at least one reconciled unfinished occurrence |
| `Abandoned` | work stopped without claiming success or replacement | abandonment reason and per-occurrence accounting; no successor assertion |
| `Superseded` | a unique named successor owns the remaining intent | valid non-self successor and per-occurrence accounting to it or an explicit obsolete ruling |

All dispositions also satisfy the non-waivable closure-record and integrity rules.

### CAP-PP-013-21: Separate annotation and bounded migration

New or mutated plans SHALL store only the canonical enum in `Plan_Status` and MAY store provenance in
`Plan_Status_Annotation`. Legacy annotated values remain readable per CAP-PP-013-13. Before the supervisor
proceeds, migration is REQUIRED only for evaluated critical-path plans; other legacy plans form a backlog
and SHALL NOT be mass-rewritten as a prerequisite.

### CAP-PP-013-22: Ordered close protocol and invariants

The close protocol SHALL: **(1)** validate explicit disposition and source transition; **(2)** scan
creator-scaffolded and pre-close-verifiable inputs—integrity findings always block; `Complete` blocks on
substantive work; a reasoned disposition may carry substantive work forward to per-occurrence accounting,
except `status_row_nonterminal`, which blocks until the deliverable row is explicitly dispositioned;
**(3)** author closer-owned outputs; **(4)** reparse
the mutated document and evaluate exit findings; **(5)** reconcile every finding occurrence; **(6)**
transition status and commit only after a CLEAN or governed reasoned-disposition verdict. It preserves:

- **I1** — closure-record and integrity findings are never laundered through a reasoned disposition;
- **I2** — acceptance traverses invocation → mutation → parse → verdict;
- **I3** — identity and accounting are per occurrence;
- **I4** — declared-surface completeness is the union across normative and consuming sources, with this
  spec resolving disagreements and consumers forbidden to invent values.

The generated disposition × finding-kind × mode × phase product SHALL have exactly one outcome per cell
and zero unresolved cells. Verdict precedence is `ERROR > BLOCK > HYGIENE > CLEAN`; HYGIENE does not
alter exit status.

### Verification Tests — V-PP-039..047

| ID | Covers | Assertion |
|---|---|---|
| V-PP-039 | CAP-PP-013-14 | every CAP-PP-013-01..22 requirement has exactly one instrument-derived lifecycle class |
| V-PP-040 | CAP-PP-013-07/-11/-13/-21 | descriptive qualifier resolves with warning; negating/ambiguous qualifier cannot establish terminality; implementation adds no IFF condition |
| V-PP-041 | CAP-PP-003, CAP-PP-013-19/-20 | each state has one class; every lawful transition has target evidence; no terminal disposition is provisional |
| V-PP-042 | CAP-PP-013-15 | missing/unknown disposition errors; reason cannot select; CLI partial spelling roundtrips |
| V-PP-043 | CAP-PP-013-16/-17/-22 | every raw key maps once; product coverage has zero gaps/conflicts; a synthetic key/disposition fails closed |
| V-PP-044 | CAP-PP-013-16/-18 | two same-key findings require two acknowledgement rows |
| V-PP-045 | CAP-PP-013-18/-22 | actual write→parse→reconcile predicts verdict and rejects malformed/orphan/non-waivable rows |
| V-PP-046 | CAP-PP-013-17/-22 | unchecked deliverables and closure-record/integrity findings block in both modes; only bounded stale presentation can be HYGIENE |
| V-PP-047 | CAP-PP-013-19/-20/-22 | all five dispositions traverse invocation→document→parse→verdict; invalid source transition blocks |

**Enforcement status at publication**: specification candidate only. Gate 3 implements this contract and
Gate 3V independently exercises V-PP-040 and V-PP-042..047. Publication of this specification SHALL ride
with the coherent implementation; v1.5.0 MUST NOT be pushed as a spec-only intermediate.
