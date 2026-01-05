# PROJECT_PLAN: {Title}

**Version**: 1.0.0
**Status**: Draft
**Created**: {YYYY-MM-DD}
**Updated**: {YYYY-MM-DD}
**Author**: {agent-name}
**Theme**: {Short theme description}
**Tracking**: {GitHub milestone or issue reference}
**CAP-PP-011 Compliant**: Yes (all gates have V-tests)

---

## Executive Summary

{What this plan accomplishes and why it matters. 2-3 paragraphs.}

**Key Outcomes:**
- {Outcome 1}
- {Outcome 2}
- {Outcome 3}

---

## Scope

**In Scope:**
- {Item 1}
- {Item 2}
- {Item 3}

**Out of Scope (deferred):**
- {Deferred item 1} → {target version}
- {Deferred item 2} → {target version}

**Dependencies:**
- {Dependency 1} (✅ or ⏳)
- {Dependency 2} (✅ or ⏳)

---

## Success Criteria (CAP-PP-005)

| Criterion | Metric | Target | Actual | Verification |
|-----------|--------|--------|--------|--------------|
| SC-1: {Name} | {Metric} | {Target} | — | {Command} |
| SC-2: {Name} | {Metric} | {Target} | — | {Command} |
| SC-3: {Name} | {Metric} | {Target} | — | {Command} |

---

## Risk Assessment (CAP-PP-006)

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| R1: {Description} | High/Med/Low | High/Med/Low | {Mitigation} |
| R2: {Description} | High/Med/Low | High/Med/Low | {Mitigation} |

---

## V-Test Summary (CAP-PP-011)

| Gate | V-Tests | Result | Description |
|------|---------|--------|-------------|
| Gate 0 | V0.1-V0.{N} | — | Preparation |
| Gate 1 | V1.1-V1.{N} | — | {Description} |
| Gate 2 | V2.1-V2.{N} | — | {Description} |
| ... | ... | ... | ... |
| Gate {M} | V{M}.1-V{M}.{N} | — | Retrospective |
| **Total** | **{Total} V-tests** | **0/{Total}** | — |

---

## Traceability Matrix (CAP-PP-007)

### Issues → Gates

| Issue | Description | Gate | Deliverable |
|-------|-------------|------|-------------|
| #{N} | {Description} | G{N} | G{N}.{M} |

### L-docs → Deliverables

| L-doc | Requirement | Gate | Status |
|-------|-------------|------|--------|
| L{NNN} | {Description} | G{N} | Planned |

---

## Effort Estimates (CAP-PP-008)

| Gate | Tier | Estimate | Notes |
|------|------|----------|-------|
| G0 | Pattern-Clear | {time} | {notes} |
| G1 | Discovery | {range} | {notes} |
| G2 | Pattern-Similar | {time} | {notes} |
| ... | ... | ... | ... |

**Tier Legend:**
- Discovery: Low confidence (<50%), use range
- Pattern-Similar: Medium confidence (50-80%), use range
- Pattern-Clear: High confidence (>80%), use point estimate

---

## Gate 0: Preparation

**Objective:** {What this gate achieves}
**Status:** Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G0.1 | {Deliverable} | {Owner} | Pending |
| G0.2 | {Deliverable} | {Owner} | Pending |

### Verification Tests

#### V0.1: {Description}
```bash
{executable_command}
```
**Expected:** {expected_output}

#### V0.2: {Description}
```bash
{executable_command}
```
**Expected:** {expected_output}

### Checklist

- [ ] V0.1 PASS: {description}
- [ ] V0.2 PASS: {description}

**Decision Point:** Proceed to Gate 1? [GO/NO-GO]

---

## Gate 1: {Title}

**Objective:** {What this gate achieves}
**Status:** Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G1.1 | {Deliverable} | {Owner} | Pending |
| G1.2 | {Deliverable} | {Owner} | Pending |

### Verification Tests

#### V1.1: {Description}
```bash
{executable_command}
```
**Expected:** {expected_output}

### Checklist

- [ ] V1.1 PASS: {description}

**Decision Point:** Proceed to Gate 2? [GO/NO-GO]

---

## Gate {N}: Release

**Objective:** Execute release process
**Status:** Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G{N}.1 | Version bump | Manager | Pending |
| G{N}.2 | Git tags | Manager | Pending |
| G{N}.3 | GitHub releases | Manager | Pending |
| G{N}.4 | Homepage update | Manager | Pending |

### Verification Tests

#### V{N}.0.1: Manager version is {VERSION} (R-REL-006, BLOCKING)
```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='{VERSION}' else 'FAIL')"
```
**Expected:** PASS
**BLOCKING:** Do NOT proceed if FAIL

#### V{N}.1: All repos at {VERSION}
```bash
python3 validation/validate_version_consistency.py /path/to/repo
```
**Expected:** PASS

#### V{N}.2: GitHub releases exist
```bash
gh release view v{VERSION} --repo aget-framework/aget && echo "PASS" || echo "FAIL"
```
**Expected:** PASS

### Checklist

- [ ] V{N}.0.1 PASS (BLOCKING): Manager version is {VERSION}
- [ ] V{N}.1 PASS: All repos at {VERSION}
- [ ] V{N}.2 PASS: GitHub releases exist

**Decision Point:** Proceed to Retrospective? [GO/NO-GO]

---

## Gate {M}: Retrospective (L435, CAP-REASON-008)

**Objective:** Document learnings and close project
**Status:** Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G{M}.1 | Document learnings (L-docs) | Manager | Pending |
| G{M}.2 | Update SOPs if needed | Manager | Pending |
| G{M}.3 | Velocity analysis | Manager | Pending |
| G{M}.4 | Archive PROJECT_PLAN | Manager | Pending |

### Verification Tests

#### V{M}.1: Learnings documented
```bash
[ -f ".aget/evolution/L{NNN}_{learning}.md" ] && echo "PASS" || echo "FAIL"
```
**Expected:** PASS (at least one L-doc)

#### V{M}.2: PROJECT_PLAN marked Complete
```bash
grep -q "Status.*Complete" PROJECT_PLAN_*.md && echo "PASS" || echo "FAIL"
```
**Expected:** PASS

### Checklist

- [ ] V{M}.1 PASS: Learnings documented
- [ ] V{M}.2 PASS: PROJECT_PLAN marked Complete

**Project Complete**

---

## Velocity Analysis (CAP-PP-009)

*Complete after execution*

| Gate | Estimated | Actual | Ratio | Notes |
|------|-----------|--------|-------|-------|
| G0 | {est} | — | — | — |
| G1 | {est} | — | — | — |
| ... | ... | ... | ... | ... |
| **Total** | {total} | — | — | — |

---

## References (CAP-PP-010)

### L-docs
- L{NNN}: {Title}

### SOPs
- SOP_{name}.md

### Specs
- AGET_{NAME}_SPEC.md

### Related Plans
- PROJECT_PLAN_{name}.md

---

## Execution Log

*Record key actions and decisions during execution*

### Session {YYYY-MM-DD}

| Time | Gate | Action | Artifact | Commit |
|------|------|--------|----------|--------|
| +0m | — | Session start | — | — |
| +{N}m | G{N} | {Action} | {Artifact} | {hash} |

---

## Changelog

### v1.0.0 ({YYYY-MM-DD})

- Initial plan

---

*PROJECT_PLAN_{name}.md — Per CAP-PP-001 through CAP-PP-011*
