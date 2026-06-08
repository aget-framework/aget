---
name: aget-propose-initiative
description: Create lightweight initiative proposals (PROPOSAL_init_*.md) before full INIT-*.md scaffolding. Follows 'propose -> review -> approve -> create' governance pattern. Advisory enforcement. Implements AGET_INITIATIVE_SPEC v1.0.1 CAP-INIT-PROP-001..012.
version: 1.0.0
---

# /aget-propose-initiative

Create a lightweight initiative proposal before committing to full `/aget-create-initiative` scaffolding. Follows governance pattern: propose → review → approve → create. Implements **AGET_INITIATIVE_SPEC v1.0.1** clauses CAP-INIT-PROP-001 through CAP-INIT-PROP-012.

## Purpose

Prevent direct authoring of `INIT-*.md` manifests without a proposal gate. Per **L867** (artifact-needs-skill pattern) and **ADR-008** (L-doc evidence → SOP → Spec → Skill ladder), this skill closes the propose-half of the initiative verb-pair (the create-half is `/aget-create-initiative`, currently proposed but not implemented).

**Evidence**:
- 2026-04-19 INIT-REQ-SPEC-TEST-DEFINED authored via direct Write — no proposal gate, no cross-initiative overlap check (`planning/skill-proposals/PROPOSAL_aget-create-initiative.md`)
- 7 existing `PROPOSAL_init_*.md` files (PP-014, 016, 017, 018, 019, 020, 027) authored via `/aget-propose-project` — 0/7 contain Channels, Contributors, or Cross-Initiative Overlap sections (empirical grep 2026-05-14)
- gh#1193 INIT-PRINCIPLED-EXECUTION referenced in scope tables without file — decorative-reference anti-pattern

**Governing Spec**: `../aget/specs/AGET_INITIATIVE_SPEC.md` v1.0.1 (canonical commit `7bb93f0`)

## Input

`$ARGUMENTS` — Initiative topic, theme, or problem description

Examples:
- `/aget-propose-initiative issue-inbox stewardship for 1228 open issues`
- `/aget-propose-initiative cross-fleet observation propagation discipline`
- `/aget-propose-initiative skill canonical promotion fleet-wide`

If no arguments provided:
```
Error: Initiative topic required.
Usage: /aget-propose-initiative <topic or theme description>
Example: /aget-propose-initiative issue-inbox stewardship
```

## Execution

### Step 1: Parse Input

Extract from `$ARGUMENTS`:
1. **Topic**: What the initiative addresses
2. **Proposed INIT-ID**: `INIT-{UPPER-KEBAB-CASE}` derived from topic (e.g., "issue-inbox stewardship" → `INIT-ISSUE-INBOX-STEWARDSHIP`)
3. **Snake-case filename slug**: lowercase snake_case for `PROPOSAL_init_{slug}.md` (e.g., `issue_inbox_stewardship`)

### Step 2: Conflict Check (implements CAP-INIT-PROP-003)

Three scans BEFORE writing the proposal:

#### 2a: Existing initiatives (CAP-INIT-PROP-003-01)
```bash
ls planning/initiatives/INIT-*.md 2>/dev/null
grep -li "<topic_keywords>" planning/initiatives/INIT-*.md 2>/dev/null
```

#### 2b: Prior proposals (CAP-INIT-PROP-003-02)
```bash
ls planning/project-proposals/PROPOSAL_init_*.md 2>/dev/null
grep -li "<topic_keywords>" planning/project-proposals/PROPOSAL_init_*.md 2>/dev/null
```

#### 2c: Carry-forward PROPOSED-without-file (CAP-INIT-PROP-003-03)
```bash
awk '/## Grooming Inputs/,/## Convention/' planning/initiatives/INDEX.md | grep -i "<topic_keywords>"
```

#### 2d: Conflict handling (CAP-INIT-PROP-003-04)
If a conflict is detected, emit a warning naming the conflicting artifact AND offer the principal:
- **(a)** Proceed (new proposal — accept the overlap)
- **(b)** Amend the existing artifact instead
- **(c)** Abort

### Step 3: Gather Context

#### 3.1 Read AGET Identity
```bash
python3 -c "import json; d=json.load(open('.aget/identity.json')); print(d.get('north_star',{}).get('statement',''))"
cat .aget/version.json | python3 -m json.tool
```
Extract:
- `north_star.statement`: Agent purpose (for scope-fit assessment)
- `aget_version`: Currently-released framework version (for CAP-INIT-PROP-012-03)

#### 3.2 Search Related L-docs
```bash
python3 scripts/study_topic.py --topic "<topic>" --quiet 2>/dev/null \
  || grep -rl "<topic_keywords>" .aget/evolution/L*.md | head -5
```

#### 3.3 Inventory Existing Initiatives (for §6 cross-overlap analysis)
```bash
ls planning/initiatives/INIT-*.md 2>/dev/null
```

### Step 4: Cross-Initiative Overlap Analysis (implements CAP-INIT-PROP-004)

Classify the proposed initiative's relationship to EVERY existing INIT-*.md AND every PROPOSED-but-fileless entry in INDEX.md. Classification vocabulary (per CAP-INIT-PROP-004-01):

| Class | Meaning |
|-------|---------|
| **Independent** | Distinct scope, no shared artifacts or theme |
| **Producer/Consumer** | One initiative's deliverable is the other's input (e.g., spec → skill) |
| **Sibling** | Same parent theme, parallel work tracks |
| **Fold-Candidate** | Significant overlap; recommend folding into existing |
| **Redundant** | Same scope as an existing initiative; recommend rejection |

If ANY classification is `Fold-Candidate` or `Redundant` (per CAP-INIT-PROP-004-02), the proposal Decision section MUST include the explicit Fold option (it does by default — see Step 7).

Cite the format precedent (CAP-INIT-PROP-004-03): `docs/MEMO_initiative_overlap_clarification_2026-05-14.md`.

### Step 5: Assign PP-### (implements CAP-INIT-PROP-002)

```bash
# Read the highest existing PP-### and increment (CAP-INIT-PROP-002-01)
LAST=$(grep -oE 'PP-[0-9]+' planning/project-proposals/INDEX.md | grep -oE '[0-9]+' | sort -n | tail -1)
NEW_PP=$(printf "PP-%03d" $((LAST + 1)))
```

The PP-### sequence is **shared** with `/aget-propose-project` (CAP-INIT-PROP-002-02). No separate sub-sequence.

Verify the proposed INIT-ID is unique (CAP-INIT-PROP-002-03):
```bash
test ! -f "planning/initiatives/${INIT_ID}.md" \
  && test -z "$(grep -l "$INIT_ID" planning/project-proposals/PROPOSAL_init_*.md 2>/dev/null)"
```

### Step 6: Verify Target Version Currency (implements CAP-INIT-PROP-012)

```bash
CURRENT=$(python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])")
echo "Current released version: $CURRENT"
```

The proposal's Target Versions field MUST be a range like `v3.18 – v3.20` (CAP-INIT-PROP-012-01) referencing AGET framework versions.

If the start version is ≤ `$CURRENT` (CAP-INIT-PROP-012-02), flag the proposal "past-start" and adjust the start version forward to the next unreleased version before final filing.

### Step 7: Create Proposal File (implements CAP-INIT-PROP-001, 005, 006, 007, 008, 010)

Write to `planning/project-proposals/PROPOSAL_init_{snake_case_slug}.md` (CAP-INIT-PROP-001-01, 001-04 — `init_` infix is required).

**MUST contain sections in this order** (CAP-INIT-PROP-001-03):

```markdown
# Initiative Proposal: {Title}

**Date**: {YYYY-MM-DD}
**Author**: {agent name from identity.json}
**Status**: PROPOSED                          <!-- CAP-INIT-PROP-010-01: MUST be PROPOSED at creation -->
**Proposal ID**: {PP-###}                     <!-- from Step 5 -->
**Proposed Initiative ID**: {INIT-NAME}       <!-- CAP-INIT-PROP-001-02 -->
**Target Versions**: v{X.Y} – v{X.Y}          <!-- from Step 6 -->
**Theme**: {one-sentence theme}

---

## Problem / Opportunity

{What gap, friction, or opportunity this initiative addresses. 1-3 paragraphs.}

## Evidence

<!-- CAP-INIT-PROP-007-01: ≥3 rows required. CAP-INIT-PROP-007-02: each Source SHALL cite L-doc/session/issue/path; anecdote/intuition REJECTED. -->

| Observation | Source | Impact |
|-------------|--------|--------|
| {observation 1} | {L###, gh#NNN, session_YYYY-MM-DD_HHMM, or canonical path} | {what happens if unaddressed} |
| {observation 2} | {typed citation} | {impact} |
| {observation 3} | {typed citation} | {impact} |

## Proposed Scope

{1-3 sentences on what the initiative would deliver across its target version range}

### In Scope
- {item 1}
- {item 2}

### Out of Scope
- {exclusion 1}

## Channels

<!-- CAP-INIT-PROP-005-01: list every external communication/coordination surface
     CAP-INIT-PROP-005-02: if KB-only, single row: "KB-only / — / sync / primary"
     CAP-INIT-PROP-005-03: format conforms to sops/SOP_initiative.md §"Channels" -->

| Channel | ID | Purpose | Priority |
|---------|----|---------|----------|
| {name or "KB-only"} | {ID or "—"} | {sync, agents, discussion, alerts} | {primary, secondary, monitor} |

## Contributors

<!-- CAP-INIT-PROP-006-01: list every role archetype expected to supply value
     CAP-INIT-PROP-006-02: value dimensions from L572 / #910 controlled vocabulary
     CAP-INIT-PROP-006-03: Principal SHALL be present by default -->

| Role | Primary Value Dimensions | Availability |
|------|-------------------------|--------------|
| Principal | decision quality, stakeholder alignment | On-demand |
| {agent or human role} | {artifact production, critical-path acceleration, decision quality, knowledge generation, correctness assurance, stakeholder alignment, process health — one or more} | {Full, Part-time, On-demand} |

*Descriptive (value supplied) not evaluative (performance). See gh#910, L572.*

## Cross-Initiative Overlap

<!-- CAP-INIT-PROP-004-01: classify every existing ACTIVE or PROPOSED initiative
     CAP-INIT-PROP-004-03: format precedent at docs/MEMO_initiative_overlap_clarification_2026-05-14.md -->

| Initiative | Relationship | Notes |
|------------|-------------|-------|
| INIT-{NAME} | {Independent, Producer/Consumer, Sibling, Fold-Candidate, Redundant} | {1-line rationale} |
| ... (one row per existing initiative; cover ALL ACTIVE + PROPOSED) | | |

## Streams Sketch

{Initial decomposition of the work into 2-6 parallel streams. Each stream becomes a PROJECT_PLAN after `/aget-create-initiative` lands.}

| # | Stream | Target Version | One-line description |
|---|--------|---------------|---------------------|
| 1 | {name} | v{X.Y} | {what it delivers} |

## Size Estimate

**{Small (<1 day) | Medium (<2 weeks) | Large (2+ weeks) | Multi-cycle (initiative-scale)}**

For initiatives, the natural unit is **multi-cycle**. Sub-streams may have smaller scopes.

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {prerequisite} | {spec / SOP / skill / initiative / decision} | {exists / pending / missing} |

## ADR-008 Readiness

<!-- CAP-INIT-PROP-007-03: each row marked met / gap / n/a -->

| Prerequisite | Status |
|--------------|--------|
| L-doc evidence (≥2 per L436) | {met / gap / n/a} |
| SOP exists | {met / gap / n/a} |
| Governing spec exists | {met / gap / n/a} |

## Decision

<!-- CAP-INIT-PROP-008-01: all 5 options below
     CAP-INIT-PROP-008-02: Fold option present even when no Fold-Candidate detected
     CAP-INIT-PROP-008-03: skill SHALL NOT check boxes; only principal -->

- [ ] Principal reviewed
- [ ] Approved (next: `/aget-create-initiative` to scaffold the INIT-*.md manifest)
- [ ] Deferred (rationale: ___)
- [ ] Rejected (rationale: ___)
- [ ] Fold into {existing INIT-NAME} (rationale: ___)

## Traceability

| Link | Reference |
|------|-----------|
| Trigger | {what prompted this proposal} |
| Related L-docs | {L-doc references from Step 3.2} |
| Related sessions | {session files} |
| Governing spec | `../aget/specs/AGET_INITIATIVE_SPEC.md` v1.0.1 |
| Cross-initiative analysis precedent | `docs/MEMO_initiative_overlap_clarification_2026-05-14.md` |

---

*When approved, invoke `/aget-create-initiative` to scaffold the INIT-{NAME}.md manifest, referencing this proposal as trigger.*
```

### Step 8: Update INDEX (implements CAP-INIT-PROP-009)

Append a row to `planning/project-proposals/INDEX.md` (CAP-INIT-PROP-009-01):

```markdown
| {PP-###} | {init-name} | PROPOSED | {agent} | {YYYY-MM-DD} | {INIT-NAME} | {one-line notes} |
```

If `INDEX.md` does not exist (CAP-INIT-PROP-009-02), create it from the SP-006-defined template before appending.

### Step 9: Report

Output summary:
```
=== Initiative Proposal Created ===
File: planning/project-proposals/PROPOSAL_init_{slug}.md
Proposal ID: {PP-###}
Proposed Initiative ID: {INIT-NAME}
Target Versions: v{X.Y} – v{X.Y}
Related L-docs: {count} found
Existing initiatives analyzed for overlap: {count}
Fold-candidates flagged: {count or 0}

Next steps:
1. Review proposal with principal
2. Apply Decision (Approve / Defer / Reject / Fold)
3. If Approved: run /aget-create-initiative to scaffold INIT-*.md manifest
```

## Constraints

These are INVIOLABLE — MUST NOT violate:

1. **C1 (CAP-INIT-PROP-011-01)**: NEVER create a file at `planning/initiatives/INIT-*.md`. This skill creates proposals only; manifest creation is `/aget-create-initiative`'s responsibility.
2. **C2 (CAP-INIT-PROP-011-02)**: IF the principal asks this skill to also scaffold the manifest, REFUSE and point to `/aget-create-initiative` (or its proposal `planning/skill-proposals/PROPOSAL_aget-create-initiative.md` if the create-skill is not yet implemented).
3. **C3 (CAP-INIT-PROP-003)**: NEVER skip the 3-scan conflict check (Step 2) before writing the proposal.
4. **C4 (CAP-INIT-PROP-007-01, 007-02)**: NEVER write a proposal with fewer than 3 evidence rows OR with any Source value of "anecdote" / "general knowledge" / "intuition".
5. **C5 (CAP-INIT-PROP-008-03)**: NEVER check decision boxes — only the principal SHALL apply Decision values.
6. **C6 (CAP-INIT-PROP-010-01)**: NEVER create a proposal with any Status other than `PROPOSED` at file creation time.

## Enforcement Model

This skill is **Advisory** (ADR-008 Layer 1). It produces a proposal artifact. If an agent bypasses it and creates INIT-*.md directly via Write/Edit:
- No runtime block occurs
- The proposal step is recommended but not structurally enforced
- Flag as governance bypass in retrospective per L867

Promotion to Strict (D71) is deferred until `/aget-create-initiative` lands as the only path to INIT-*.md authoring. The pair-promotion model mirrors `/aget-propose-project` (Advisory) → `/aget-create-project` (Strict).

## Verification (V-tests from spec §7)

After invocation, the output PROPOSAL file SHALL pass all 14 V-INIT-PROP-### tests defined in AGET_INITIATIVE_SPEC v1.0.1 §7:

| V-test | Verifies |
|--------|----------|
| V-INIT-PROP-001 | Filename + path conformance |
| V-INIT-PROP-002 | All 12 required sections present |
| V-INIT-PROP-003 | PP-### unique + monotonic |
| V-INIT-PROP-004 | Proposed INIT-ID uniqueness |
| V-INIT-PROP-005 | Evidence row count ≥ 3 |
| V-INIT-PROP-006 | Evidence Source citations are typed |
| V-INIT-PROP-007 | Channels section non-empty |
| V-INIT-PROP-008 | Contributors section includes Principal |
| V-INIT-PROP-009 | Cross-Initiative Overlap classifies every existing initiative |
| V-INIT-PROP-010 | Decision section has all 5 options |
| V-INIT-PROP-011 | Status is PROPOSED at creation |
| V-INIT-PROP-012 | INDEX has matching row |
| V-INIT-PROP-013 | No INIT-*.md authored (separation) |
| V-INIT-PROP-014 | Target Versions not past-start |

Run mechanically via `python3 scripts/validate_initiative_proposal.py --file <path>` (implemented at Gate 2 of this skill's PROJECT_PLAN).

## Related Skills

- **`/aget-propose-project`** — sibling verb-pair (propose-side) for cycle-bounded work (`PROPOSAL_*.md` → `PROJECT_PLAN_*.md`)
- **`/aget-propose-skill`** — sibling verb-pair (propose-side) for new skills (`planning/skill-proposals/PROPOSAL_aget-*.md`)
- **`/aget-create-initiative`** — successor verb-pair (create-side) for INIT-*.md manifest scaffolding. **PROPOSED 2026-04-19, not yet implemented**. When implemented, will be Strict per D71.
- **`/aget-check-initiative`** — read-only cross-system coherence check for an existing initiative (post-creation)

## Traceability

| Link | Reference |
|------|-----------|
| Skill ID | SKILL-054 (`.aget/specs/skills/SKILL-054_aget-propose-initiative.yaml`) |
| Governing Spec | `../aget/specs/AGET_INITIATIVE_SPEC.md` v1.0.1 (CAP-INIT-PROP-001..012; V-INIT-PROP-001..014) |
| Procedural canon | `sops/SOP_initiative.md` v1.2.0 (Channels + Contributors table shapes) |
| Sibling skill (structural mirror) | `.claude/skills/aget-propose-project/SKILL.md` |
| Verb-pair create-side (not implemented) | `planning/skill-proposals/PROPOSAL_aget-create-initiative.md` (PROPOSED 2026-04-19) |
| Foundational L-doc | L760 (Initiative as Scope Modifier, Not First-Class Entity) |
| Artifact-needs-skill pattern | L867 (Coherence-Directed Investment as enhance-Verb-Family) |
| Two-level model | L742 (Requirements human-level, Specifications contract-level) |
| Anti-pattern: direct INIT-* authoring | 2026-04-19 INIT-REQ-SPEC-TEST-DEFINED incident |
| Anti-pattern: decorative reference | gh#1193 (INIT-PRINCIPLED-EXECUTION) |
| Channel registry pattern | gh#916 |
| Contributor profile pattern | gh#910 + L572 |
| Initiative relevance rubric | gh#886 (Decision section input) |
| Verb registry | `ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md` v3.16 — `propose` is verb #18 (Governance, approved) |
| Implementation plan | `planning/PROJECT_PLAN_aget_propose_initiative_v1.0.md` |
| ADR | ADR-008 (Advisory → Strict → Generator progression) |

---

*aget-propose-initiative v1.0.0*
*Category: Governance*
*Enforcement: Advisory (ADR-008 Layer 1)*
*Authored under principle-triad: spec+verify-first, coherence-next, evidence-driven (2026-05-14)*
