---
name: aget-create-rubric
description: Create scoring rubrics with domain-adaptive structure, extreme anchoring, and governed storage. ADR-008 Generator level for rubric creation.
---

# /aget-create-rubric

Create scoring rubrics with domain-adaptive structure, extreme anchoring, and governed storage. Wraps SOP_RUBRIC_CREATION.md and RUBRIC.template.md into a Generator-level skill.

## Purpose

Six agents actively produce rubrics with four incompatible storage conventions and no shared construction methodology (L731). The SOP and template are mature (v1.0, active since 2026-02-13) but require manual discovery and application. This skill is the ADR-008 Generator level for rubric creation, progressing from the current Strict level (SOP + template).

**Evidence**: L731 (Fleet Rubric Adoption Snapshot), L730 (Domain-Fit Gap), L729 (Assessment Tool Recursion), L518 (Conformance Assessment Pattern). SOP + template mature 4+ months. 6 agents producing rubrics without tooling.

## Input

$ARGUMENTS - Description of what the rubric will evaluate

Examples:
- `/aget-create-rubric skill proposal readiness` — Rubric for evaluating skill proposals
- `/aget-create-rubric CI/CD investment priority` — Rubric for CI/CD decisions
- `/aget-create-rubric session process quality` — Rubric for session quality assessment
- `create a rubric for release readiness` — Natural language trigger

## Execution

### Step 1: Domain Identification

Prompt for or derive from $ARGUMENTS:
1. **Evaluation target**: What will be scored? (artifact, process, decision, behavior)
2. **Decision this supports**: What action does scoring inform? (approve/reject, prioritize, improve)
3. **Assessor**: Who scores? (human, agent, hybrid) — per SOP Phase 1 Step 1 prerequisite (L730)

If assessor is not provided, this is a blocking prerequisite — ask before proceeding.

### Step 2: Domain Classification

Classify the rubric domain to determine label set:

| Domain Type | L0 | L1 | L2 | L3 |
|-------------|----|----|----|----|
| Conformance | Non-Conformant | Baseline | Compliant | Exemplary |
| Creative Quality | Unrecognizable | Emerging | Achieved | Transcendent |
| Maturity | Initial | Developing | Defined | Optimizing |
| Process Quality | Ad-hoc | Repeatable | Measured | Optimizing |

Present classification and label set for confirmation before proceeding.

### Step 3: Dimension Scaffolding

Propose 3-7 dimensions with definitions. For each dimension, ask:
- "Is this pass/fail or graduated?" (constraint vs dimension — L730)
- If pass/fail: move to Constraints section (binary eligibility gates)
- If graduated: keep as scored dimension

### Step 4: Extreme Anchoring (Mertler 2001)

For each dimension, write level descriptions in this order:
1. **L3 first** (best case) — What does exemplary look like?
2. **L0 second** (worst case) — What does failure look like?
3. **L1 and L2** (interpolate) — Fill the middle from the extremes

This is the Mertler construction method. Writing extremes first prevents anchor collapse.

### Step 5: Anti-Pattern Check

Verify the rubric does NOT contain:

| Anti-Pattern | Source | Detection |
|--------------|--------|-----------|
| Score multipliers | L018 | Warn if weights sum >100% or any weight >40% |
| Constraints as dimensions | L730 | Any dimension with only 2 meaningful levels = should be a constraint |
| Missing assessor identity | L730 | Blocking prerequisite — must be set in Step 1 |
| Achievement framing | Goodhart | Descriptions should say what behavior looks like, not what it achieves |

### Step 6: Fleet Lesson Surfacing

Display relevant rubric design lessons:
- L018: No score multipliers
- L183: Scoring is a tool role
- L679: Rubrics = personalization mechanism
- L705: Cross-agent traceability

### Step 7: Quality Checklist (SOP Phase 3)

Run the SOP_RUBRIC_CREATION.md Phase 3 quality checklist automatically:
- All dimensions have L0-L3 descriptions
- Labels match domain type
- Constraints are separated from dimensions
- Scoring procedure is documented
- Assessor is identified

### Step 8: Write Rubric

Write to `rubrics/RUBRIC_{name}_v1.0.md` using the RUBRIC.template.md structure.

### Step 9: Update Index

If `rubrics/README.md` exists, append entry to the rubric table.

### Step 10: Report

```
=== Rubric Created ===
File: rubrics/RUBRIC_{name}_v1.0.md
Domain: {domain_type}
Dimensions: {count}
Constraints: {count}
Assessor: {assessor}
Labels: {L0} / {L1} / {L2} / {L3}
```

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-RUB-001 | Create-rubric SHALL identify assessor before scaffolding dimensions | SOP Phase 1 Step 1, L730 |
| REQ-RUB-002 | Create-rubric SHALL classify domain and apply domain-adaptive labels | L730 |
| REQ-RUB-003 | Create-rubric SHALL use extreme anchoring (L3 then L0 then interpolate) | Mertler 2001, SOP Phase 2 |
| REQ-RUB-004 | Create-rubric SHALL separate binary constraints from scored dimensions | L730, CMMI/CLEAR pattern |
| REQ-RUB-005 | Create-rubric SHALL run quality checklist before writing | SOP Phase 3 |
| REQ-RUB-006 | Create-rubric SHALL store output in rubrics/ directory | C092 convention |
| REQ-RUB-007 | Create-rubric SHALL NOT use score multipliers or weights >40% | L018 |

## Constraints

- **C1**: MUST identify assessor before proceeding past Step 1 — this is a blocking prerequisite
- **C2**: MUST separate pass/fail constraints from graduated dimensions — mixing them inflates or deflates scores
- **C3**: MUST write L3 and L0 before L1 and L2 — prevents anchor collapse (Mertler 2001)
- **C4**: MUST write to `rubrics/` directory — no other storage location is governed

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-003 (`planning/skill-proposals/PROPOSAL_aget-create-rubric.md`) |
| SOP | SOP_RUBRIC_CREATION.md v1.0 |
| Template | rubrics/RUBRIC.template.md |
| Ontology | ONTOLOGY_scoring_rubric_v1.0.yaml |
| ADR-008 | Advisory -> Strict -> Generator progression (this skill = Generator) |
| L-docs | L729 (Recursion), L730 (Domain-Fit Gap), L731 (Fleet Snapshot), L518 (Conformance), L572 (Ontology), L679 (Personalization), L705 (Cross-Agent) |
| Research | Mertler 2001, Brookhart 2013, Stevens & Levi 2013, CMMI, CLEAR, Galileo |

---

*aget-create-rubric v0.1.0*
*Category: Governance*
*ADR-008 Level: Generator (wraps SOP + template)*
