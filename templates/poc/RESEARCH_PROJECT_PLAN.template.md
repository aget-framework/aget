# PROJECT_PLAN: {Title}

<!-- `Version` is the generated PROJECT_PLAN artifact version. The template's
     own release version is declared in `Template` and repeated in the footer. -->
**Version**: 1.0.0
**Plan_Status**: Draft
**Theme**: {Short description of the project theme}
**Tracking**: {governed issue, intake artifact, or other tracking reference}
**Created**: {YYYY-MM-DD}
**Author**: {AGET name}
**Project_Type**: {Release | Operational | Remediation | Research}
**Hypothesis**: H-{PREFIX}-001
**Template**: `templates/poc/RESEARCH_PROJECT_PLAN.template.md` v1.6.2
**Governing Spec**: AGET_PROJECT_PLAN_SPEC v1.5.0
**Parent Goal**: {committed Goal id from governance/GOALS.md, or "(none)" + one-line rationale — CAP-PP-001-07}

> **Benefit hypothesis (CAP-PP-020)**: {If this plan lands, then ⟨measurable improvement⟩, evaluated against the Parent Goal's frame; falsified by ⟨observable⟩. Resolved at close via /aget-close-project Step 5.7 — verdict + cost side.}

---

## Executive Summary

{1-2 sentences describing what this research project investigates}

---

## Problem Statement

{Description of the gap, issue, or question being investigated}

### Evidence

| Observation | Source | Impact |
|-------------|--------|--------|
| {observation 1} | {where observed} | {impact if not addressed} |

---

## Hypothesis

**H-{PREFIX}-001**: {Falsifiable hypothesis statement}

---

## Scope

### In Scope

1. {Research question 1}
2. {Research question 2}

### Out of Scope

- {What this research does NOT cover}

---

## Operational Context (Optional)

**Operating cadence**: {one-time research | recurring review cadence}
**Dependencies**: {required inputs, systems, or governed artifacts}
**Consumers**: {who or what will use the findings}

### Recurring Task Tracking (Optional)

| Task | Cadence | Owner | Last Run | Next Run | Status |
|------|---------|-------|----------|----------|--------|
| {recurring task, if any} | {cadence} | {owner} | {date or N/A} | {date or N/A} | Pending |

---

## Phase -1: Due Diligence

### L-doc Review

| L-doc | Title | Key Lesson | Application |
|-------|-------|------------|-------------|
| {L###} | {title} | {lesson} | {how it applies} |

### Prior Work

| Artifact | Relevance |
|----------|-----------|
| {PROJECT_PLAN or doc} | {how it relates} |

### Vocabulary Terms

| Term | Definition | Source |
|------|------------|--------|
| {term} | {definition} | {spec} |

---

## V-Test Standards by Project Type

| Project Type | V-test Standard | Example |
|-------------|-----------------|---------|
| **Remediation** | Executable bash ONLY. Prose criteria NOT permitted. | `grep -c "14 universal" file.md # expect 0` |
| **Research** | Executable bash preferred. Qualitative criteria acceptable when verification is inherently non-automatable. | "Hypothesis tested with 3+ evidence sources" |

**How to determine project type**: If your deliverables modify existing artifacts (fix counts, update scripts, correct specs), this is a **remediation** project. If your deliverables are new knowledge artifacts (L-docs, analysis, recommendations), this is a **research** project.

**L625**: The "or criteria" escape hatch was removed in v1.3.0 because it allowed prose V-tests in remediation projects where executable verification is always possible.

---

## Gates

<!-- Gate ordering follows spec-first principle (MP-1, L617):
     Gate -1: Governing spec verification (deductive, MUST come first)
     Gate 0:  Evidence/prerequisite collection
     Gates 1-N: Implementation (ordered by dependency, not discovery sequence)
     Verification gates: Conformance checks AFTER implementation
     Coherence gates: Cross-artifact alignment AFTER verification
     Integration gates: Traceability, tracking, closure LAST

     Anti-pattern: ordering gates by "what we found first" (inductive) instead of
     "what we should verify first" (deductive). See L617.

     Triad Checkpoint Pattern (L818, L834):
     Each gate carries an optional "Triad Checkpoint" block. At gate execution:
       1. Score dimensions D1-D5 via RUBRIC_triad_invocation_gating v1.1.0
       2. Rubric decision determines which perspectives to invoke (Builder/Auditor/Critic)
       3. Findings append to planning/triad_findings.jsonl (spec-ID tagged)
     Override rules: ALWAYS invoke Critic on final gate; ALWAYS invoke Auditor
     when new specs created (D2 >= L2); principal override per L178.
     Advisory level by default (ADR-008). Final gate Critic is implicit-required. -->

## Gate -1: Governing Spec Verification

**Objective**: Identify and read governing specs before designing gates (MP-1: Spec-First + Verification). This gate is STANDARD for all project types per CAP-PP-017.
**Gate_Status**: Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G-1.1 | Identify governing spec(s) for artifacts being created or modified. For research projects: identify whether governing specs exist for the domain under investigation. | {owner} | Pending |
| G-1.2 | Read governing spec(s) and cite specific requirements (CAP-xxx-nnn). If no governing spec exists, note "greenfield — no governing spec" and document as finding. | {owner} | Pending |
| **Midpoint** | **Pause after 2 of 4 deliverables: verify the governing-spec baseline and correct scope drift before continuing.** | {owner} | Pending |
| G-1.3 | Verify cross-reference targets are accurate (not stale). | {owner} | Pending |
| G-1.4 | Verify evidence claims against actual artifacts (CAP-PP-017-04 — assumptions are not evidence). | {owner} | Pending |

### Verification Tests

#### V-1.1: Governing-spec and evidence verification

```bash
{Verification command — executable bash that returns PASS/FAIL}
```

**Expected:** PASS

**Actual:** NOT RUN — record command, exit status and evidence at gate execution.

**Exit Criteria**: Governing specs read (or absence documented); no structural conflicts; evidence verified

### Checklist

- [ ] V-1.1 PASS: governing specs and evidence verified

**Triad Checkpoint** (per RUBRIC_triad_invocation_gating v1.1.0):

| Dim | Score (L0-L3) | Rationale |
|-----|:-------------:|-----------|
| D1 Gate Complexity | — | {deliverable count + dependencies} |
| D2 Spec Surface Area | — | {specs touched/created} |
| D3 Blast Radius | — | {downstream consumer count} |
| D4 Prior Findings | — | {N/A for first gate} |
| D5 Budget | — | {session time remaining} |

**Risk Score**: — /12 | **Budget Factor**: — /3 → **Decision**: [Full Triad / Audit+Critique / Critique Only / Skip / Builder Only]

**Perspectives invoked**: [ ] Builder  [ ] Auditor  [ ] Critic
**Findings** (append spec-ID-tagged entries to `planning/triad_findings.jsonl`):
- {finding-1 or "none" if clean}

**Decision Point** (authorization via `/aget-go`): Proceed to Gate 0? [GO/NO-GO]

---

## Gate 0: Research Foundation

**Objective**: Establish the evidence baseline and bounded research scope.
**Gate_Status**: Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G0.1 | Define research questions. | {owner} | Pending |
| G0.2 | Identify data sources. | {owner} | Pending |
| G0.3 | Create L-doc if a novel pattern is discovered. | {owner} | Pending |

*For gates with 4+ deliverables, insert a mid-gate checkpoint at 50% (per L002).*

### Verification Tests

#### V0.1: Research-foundation verification

```bash
{Verification command — executable bash that returns PASS/FAIL}
```

**Expected:** PASS

**Actual:** NOT RUN — record command, exit status and evidence at gate execution.

**Exit Criteria**: Research scope clearly defined

### Checklist

- [ ] V0.1 PASS: research foundation verified

**Triad Checkpoint**: D1=— D2=— D3=— D4=— D5=— → Decision: [skip/critique/audit+critique/full] | Perspectives: [ ]B [ ]A [ ]C | Findings: {none or ID-tagged}

**Decision Point** (authorization via `/aget-go`): Proceed to Gate 1? [GO/NO-GO]

---

## Gate 1: Investigation

**Objective**: Gather the evidence required to test the project hypothesis.
**Gate_Status**: Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G1.1 | {First investigation task} | {owner} | Pending |
| G1.2 | {Second investigation task} | {owner} | Pending |

*For gates with 4+ deliverables, insert a mid-gate checkpoint at 50% (per L002).*

### Verification Tests

#### V1.1: Investigation-evidence verification

```bash
{Verification command — executable bash that returns PASS/FAIL}
```

**Expected:** PASS

**Actual:** NOT RUN — record command, exit status and evidence at gate execution.

**Exit Criteria**: Evidence gathered to test hypothesis

### Checklist

- [ ] V1.1 PASS: investigation evidence verified

**Triad Checkpoint**: D1=— D2=— D3=— D4=— D5=— → Decision: [skip/critique/audit+critique/full] | Perspectives: [ ]B [ ]A [ ]C | Findings: {none or ID-tagged}

**Decision Point** (authorization via `/aget-go`): Proceed to Gate 2? [GO/NO-GO]

---

## Gate 2: Analysis & Conclusion

**Objective**: Resolve the hypothesis and route any verified follow-on work.
**Gate_Status**: Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G2.1 | Analyze findings. | {owner} | Pending |
| G2.2 | Document conclusions. | {owner} | Pending |
| G2.3 | Create a follow-on PROJECT_PLAN if actionable. | {owner} | Pending |

*For gates with 4+ deliverables, insert a mid-gate checkpoint at 50% (per L002).*

### Verification Tests

#### V2.1: Analysis-and-conclusion verification

```bash
{Verification command — executable bash that returns PASS/FAIL}
```

**Expected:** PASS

**Actual:** NOT RUN — record command, exit status and evidence at gate execution.

**Exit Criteria**: Hypothesis confirmed or refuted with evidence

### Checklist

- [ ] V2.1 PASS: analysis and conclusion verified

**Triad Checkpoint** (FINAL GATE — Critic MANDATORY per override rule): D1=— D2=— D3=— D4=— D5=— → Decision: [critique/audit+critique/full] (skip not permitted on final gate) | Perspectives: [ ]B [x]A? [x]C | Findings: {none or ID-tagged}

**Decision Point** (authorization via `/aget-go`): Proceed to project closure? [GO/NO-GO]

---

## Effort Estimates

*Estimate per gate. Include cumulative total. Update as gates complete.*

| Gate | Estimated Hours | Notes |
|------|:---------------:|-------|
| Gate -1 | {est} | {scope note} |
| Gate 0 | {est} | {scope note} |
| Gate 1 | {est} | {scope note} |
| Gate 2 | {est} | {scope note} |
| **Total** | **{sum}** | |

---

## Rollback Plan

*How to revert each gate's changes if needed.*

**Trigger**: A blocking V-test fails, evidence provenance cannot be verified, or an approved scope boundary is crossed.

| Gate | Rollback |
|------|----------|
| Gate 0 | {how to revert} |
| Gate 1 | {how to revert} |
| Gate 2 | {how to revert} |

**Verification**: {command or inspection that proves the rollback restored the prior state}

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {research or governance risk} | High/Med/Low | High/Med/Low | {prevention or response} |

---

## Version-Bearing Files

| File | Version Source | Current Version | Planned Version | Verification |
|------|----------------|-----------------|-----------------|--------------|
| {file, or N/A for a non-versioned research artifact} | {governing spec, SOP, or inline source} | {version or N/A} | {version or N/A} | {command or inspection} |

---

## References

### L-docs

| L-doc | Title | Application |
|-------|-------|-------------|
| {L###} | {title} | {how it informs this project} |

### Related SOPs

| SOP | Application |
|-----|-------------|
| {SOP name} | {how it governs this project} |

### Specs

| Spec | Application |
|------|-------------|
| {spec name} | {which requirements apply} |

---

## Traceability Matrix

### Issues and Evidence → Gates

| Trigger / Issue | Description | Gate | Deliverable |
|-----------------|-------------|------|-------------|
| {what prompted this research} | {evidence or governed issue} | {Gate} | {Gx.y} |

### Requirements and Precedents → Deliverables

| Requirement / L-doc | Application | Gate | Deliverable | Status |
|---------------------|-------------|------|-------------|--------|
| {CAP-xxx-nnn or L###} | {constraint or lesson} | {Gate} | {Gx.y} | Pending |

### Deliverables → V-Tests

| Deliverable | Verification Test | Expected Evidence |
|-------------|-------------------|-------------------|
| {Gx.y} | {Vx.y} | {observable PASS evidence} |

### Supporting Context

| Link | Reference |
|------|-----------|
| Vocabulary | {terms from specs or ontology} |
| Session | {session file} |

---

## Success Criteria

| Criterion | Metric | Target | Actual | Verification |
|-----------|--------|--------|--------|--------------|
| SC-1: Hypothesis tested | Confirmed or refuted | With 3+ evidence sources | — | {executable V-test, or a named structured evidence protocol when the project is research-only} |
| SC-2: L-doc created | New pattern documented | If novel pattern found | — | `ls .aget/evolution/L*_{topic}*.md` |
| SC-3: Follow-on work | Documented if needed | PROJECT_PLAN or D-item filed | — | {Reference to follow-on artifact} |

---

## Velocity Analysis

*Record actual effort at gate completion. Calculate ratio and explain significant variance (>1.5x or <0.5x).*

| Gate | Estimated | Actual | Ratio | Notes |
|------|-----------|--------|-------|-------|
| Gate -1 | {est} | — | — | |
| Gate 0 | {est} | — | — | |
| Gate 1 | {est} | — | — | |
| Gate 2 | {est} | — | — | |

---

## Finalization Checklist

*Complete this checklist when all gates are done, before marking the plan COMPLETE.*

- [ ] All gates marked Complete or Skipped (with justification)
- [ ] All V-tests executed with results recorded
- [ ] Velocity analysis completed (actual effort filled in above)
- [ ] Retrospective captured (see below)
- [ ] **Per-cycle ledgers fed** (release-class plans) — append planned-SU vs actual-hours to
      `workspace/cycle_actuals.md` per `RUBRIC_minor_release_scope:67`, and record the release-quality
      score per SOP Phase 7.1.5. *Mark UNAVAILABLE where a datum was never captured; do not leave a
      silent gap and do not back-fill a guess.*
- [ ] Status updated to Complete

> **Why the ledger line is here and not in the rubric that mandates it (L1338)**: a record obligation
> written into the artifact it updates is enforced only by recall, and lapses invisibly — `cycle_actuals.md`
> went six shipped cycles unfed and Phase 7.1.5 was skipped four consecutive times while labelled BLOCKING.
> An unfed ledger emits no signal, so its absence is indistinguishable from a clean run. The trigger belongs
> on a surface whose completion is already structural proof: this checklist.
- [ ] Related issues closed

---

## Closure Checklist

- [ ] All gates passed their V-tests
- [ ] Actual vs estimated effort recorded in Velocity Analysis
- [ ] Status field updated to Complete
- [ ] Downstream artifacts verified (if any modified)

---

## Retrospective

*Complete when project reaches COMPLETE status. Per CAP-PP-018.*

### What Worked

1. {Positive pattern to repeat}
2. {Effective approach}

### What Didn't Work

1. {Issue encountered}
2. {Approach to avoid}

### Action Items

| Item | Owner | Target | Status |
|------|-------|--------|--------|
| {Document learning as L-doc} | {owner} | {date} | Pending |
| {Update SOP/template if needed} | {owner} | {date} | Pending |

---

*RESEARCH_PROJECT_PLAN template v1.6.2*
*"Research before remediation. Verify before proceeding."*
