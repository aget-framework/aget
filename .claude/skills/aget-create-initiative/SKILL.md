---
name: aget-create-initiative
description: Scaffold approved initiative manifests at planning/initiatives/INIT-*.md. Mirrors /aget-create-project STRICT (D71 Layer 2) — direct Write/Edit to planning/initiatives/ is PROHIBITED once this skill is invoked. Implements SOP_initiative.md (graduated procedure) + future AGET_INITIATIVE_SPEC. Consumes PROPOSAL_init_*.md substrate produced by /aget-propose-initiative.
version: 1.0.0
---

# /aget-create-initiative

Create a new AGET initiative manifest at `planning/initiatives/INIT-*.md`. Mirrors the `/aget-create-project` Strict pattern (D71 Layer 2): once invoked, direct Write/Edit to `planning/initiatives/INIT-*.md` is **PROHIBITED**. This skill closes the verb-pair gap with `/aget-propose-initiative` (Advisory).

## Purpose

Per L867 (Coherence-Directed Investment) + D71 (Structural Skill Routing), each artifact-class needs a Strict create-side skill. The framework has:

- `/aget-create-project` → `PROJECT_PLAN_*.md` (Strict)
- `/aget-create-skill` → skill scaffolding (Strict-adjacent)
- `/aget-create-rubric` → rubric scaffolding (Generator)
- `/aget-create-briefing` → briefing artifact (Generator)
- **`/aget-create-initiative` → `INIT-*.md` (THIS SKILL — Strict, D71 Layer 2)**

**Evidence** (2026-05-16):
- v3.18 orphan-routing batch scaffolded `INIT-FLEET-OBSERVABILITY.md` by direct Write (governance bypass — L867 self-instance)
- 23 of 60 v3.18 items lacked owning initiative (38% orphan rate) — initiatives are critical infrastructure per principal directive
- `planning/skill-proposals/PROPOSAL_aget-create-initiative.md` PROPOSED 2026-04-19; design complete; awaits implementation
- Direct INIT-* authoring observed: INIT-REQ-SPEC-TEST-DEFINED (2026-04-19), INIT-FLEET-OBSERVABILITY (2026-05-16)

**Governing Spec**: `sops/SOP_initiative.md` v1.2.0 (graduated procedure; serves as governing contract until `aget/specs/AGET_INITIATIVE_SPEC.md` is authored at v3.19+).

### Ontology Bindings (FWRK-2026-020 substrate)

This skill SHALL be interpreted in terms of the following AGET ontology concepts
(ontology v1.0.0, per `aget:concept/ConceptPinningByVersion` C643):

- `aget:concept/SpecificationToOntologyBinding` (C644) — initiative manifests
  authored by this skill are downstream binding consumers; new initiatives SHALL
  declare their concept bindings inline (`aget:concept/X`).
- `aget:concept/ConceptLifecycleState` (C651) — initiative lifecycle states
  (PROPOSED / ACTIVE / DORMANT / RETIRED) mirror SKOS concept lifecycle; the
  same governance discipline applies.
- `aget:concept/EditorialWorkflowStateLabel` (C658) — `**Status**:` field in
  manifest header is the state label per AGET INDEX convention.
- `aget:concept/NormativeConceptBinding` (C641) — the discipline that, when
  applied to initiative manifests, makes Cross-Initiative Overlap claims
  operationally verifiable (currently text-only).
- `aget:concept/AuthorAssertedCleanlinessAntiPattern` (C671) — Step 8
  self-verification SHALL be replaced by validator output when Strict promotion
  matures (currently author-asserted).

Vocabulary version: `ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml` v1.0.0.
Concept Editor (`aget:concept/ConceptEditorRole` C657): aget-framework.

## Input

`$ARGUMENTS` — Approved INIT-ID (e.g., `INIT-SUBSTRATE-HYGIENE`) OR the PP-### reference of an approved PROPOSAL_init_*.md.

Examples:
- `/aget-create-initiative INIT-SUBSTRATE-HYGIENE`
- `/aget-create-initiative PP-036`
- `/aget-create-initiative PP-037 INIT-EVOLUTION-DISCIPLINE`

If no arguments provided:
```
Error: Approved INIT-ID or PP-### reference required.
Usage: /aget-create-initiative <INIT-NAME> | <PP-NNN>
Example: /aget-create-initiative INIT-SUBSTRATE-HYGIENE
Prerequisite: PROPOSAL_init_*.md must exist with Status: APPROVED via principal Decide.
```

## Constraints

**INVIOLABLE** — MUST NOT violate:

1. **C1 (D71 Layer 2 Strict)**: NEVER scaffold `planning/initiatives/INIT-*.md` unless a corresponding APPROVED `PROPOSAL_init_*.md` exists. If proposal is PROPOSED (not yet Approved), REFUSE and direct user to `/aget-propose-initiative` flow + principal Decide.
2. **C2 (Status default)**: NEVER default new initiatives to `Status: ACTIVE`. Default is `Status: NASCENT`. Promotion to ACTIVE requires explicit principal GO + cross-initiative coordination check (Open Questions).
3. **C3 (No proposal bypass)**: NEVER author the proposal-step content in this skill. Proposal is `/aget-propose-initiative` responsibility. If user attempts to use this skill to also create the PROPOSAL, REFUSE and point to `/aget-propose-initiative`.
4. **C4 (SOP conformance)**: MUST verify all manifest sections defined in `sops/SOP_initiative.md` are present before write. Missing sections = blocked write.
5. **C5 (Cross-initiative coordination MANDATORY)**: MUST execute Step 8 cross-initiative coordination check; Open Questions section MUST flag overlap with every existing INIT-* + every PROPOSED-but-fileless entry in `planning/initiatives/INDEX.md`.
6. **C6 (Self-verification)**: MUST execute Step 7.5 + Step 8 self-verification; report PASS/FAIL/PARTIAL per section.

## Execution

### Step 0: Scope-Fit Validation

1. Read `.aget/identity.json` — extract `domain`, `north_star`, `archetype`
2. Read `governance/SCOPE_BOUNDARIES.md` — extract in-scope and out-of-scope areas
3. Verify proposed INIT topic falls within agent's domain
4. If out-of-scope: REFUSE; suggest routing to appropriate agent

### Step 1: Input Analysis

Extract from `$ARGUMENTS`:
- **INIT-ID**: `INIT-{UPPER-KEBAB-CASE}` (from explicit arg or derived from PP-###)
- **PP-### reference**: lookup the approved proposal substrate
- **Snake-case filename slug**: lowercase snake_case for `INIT-{NAME}.md`

### Step 2: Proposal Existence & Approval Check (C1 — Strict)

```bash
# 2a. Locate PROPOSAL_init_{slug}.md substrate
PROPOSAL_FILE=$(ls planning/project-proposals/PROPOSAL_init_*.md | grep -i "{slug}" | head -1)

# 2b. Verify Status: APPROVED in PROPOSAL header
grep -i "^\*\*Status\*\*:.*APPROVED" "$PROPOSAL_FILE"
```

**If proposal does NOT exist**: REFUSE — direct user to `/aget-propose-initiative` flow.
**If proposal exists but Status is PROPOSED (not APPROVED)**: REFUSE — propose-review-approve-create gate not closed; await principal Decide.
**If proposal exists with Status: APPROVED**: PROCEED.

This is the Strict gate (C1).

### Step 3: Research Phase

#### 3.1 Read AGET Identity
```bash
python3 -c "import json; d=json.load(open('.aget/identity.json')); print(d.get('north_star',{}).get('statement',''))"
```

#### 3.2 Read SOP_initiative.md (canonical procedure)
```bash
cat sops/SOP_initiative.md  # extract manifest template structure
```

#### 3.3 Conflict check — does INIT-{NAME}.md already exist?
```bash
test ! -f "planning/initiatives/INIT-{NAME}.md" || REFUSE
```

#### 3.4 Cross-initiative inventory (mandatory per C5)
```bash
ls planning/initiatives/INIT-*.md  # list all existing initiatives for overlap check
```

#### 3.5 Read approved PROPOSAL substrate
Extract from `PROPOSAL_init_{slug}.md`:
- North Star / Theme
- Problem / Opportunity
- Evidence rows (≥3 typed)
- Proposed Scope (In Scope / Out of Scope)
- Channels
- Contributors
- Cross-Initiative Overlap (relationship classifications)
- Streams Sketch
- Dependencies
- ADR-008 Readiness

### Step 4: Template Selection & Scaffold Generation

Apply `sops/SOP_initiative.md` manifest template + sibling-initiative patterns (e.g., `planning/initiatives/INIT-SKILL-MATURATION.md`).

Required manifest sections (per SOP_initiative.md):
- Header (Initiative ID, Status, Created, Approved, Author, Target Versions, Parent Proposal, optional Sibling Initiative)
- North Star (one-line statement)
- Purpose (problem statement + opportunity + trigger)
- Channels (table; KB-only if no external channels)
- Contributors (table; Principal mandatory)
- Streams (table; 2-6 parallel work tracks)
- Capabilities (EARS — CAP-{NAME}-NNN; one per stream minimum)
- Verifications (V-{NAME}-NNN paired with CAPs)
- Dependencies (table)
- ADR-008 Readiness (L-doc evidence / SOP / Spec status per row)
- Relationship to Sibling Initiatives (table; classify EVERY ACTIVE initiative)
- Approval Trail (Decide gate citation + Loading Dock duration)
- Loading Dock Closure Note (if applicable)
- Traceability (link table; Proposal / Sibling / Related L-docs / Related issues)

### Step 5: Status Lifecycle Default (C2)

```markdown
**Status**: NASCENT (default — promotion to ACTIVE requires explicit principal GO + cross-initiative coordination check passed)
```

NEVER default to ACTIVE. Per the 2026-04-19 INIT-REQ-SPEC-TEST-DEFINED pattern, decorative-active-initiative anti-pattern is prevented by NASCENT default.

### Step 6: Write to planning/initiatives/INIT-{NAME}.md

```bash
# Write the scaffolded manifest
# (use Write tool with full manifest content per Step 4 template)
```

### Step 7: Report Output Summary

```
=== Initiative Created ===
File: planning/initiatives/INIT-{NAME}.md
Status: NASCENT
Parent Proposal: PP-### (Approved YYYY-MM-DD)
Streams scaffolded: N
Capabilities defined: M
Dependencies cited: K
Sibling initiatives classified: L

Next steps:
1. Cross-initiative coordination check (Step 8 self-verification)
2. Principal Decide on NASCENT → ACTIVE promotion
3. Stream-level PROJECT_PLAN authoring (via /aget-create-project per stream)
```

### Step 7.5: Self-Verification (C6 — MUST execute)

Verify each manifest section is present and non-empty:

| Section | Status | Evidence |
|---------|:------:|----------|
| Header | PASS/FAIL | Initiative ID + Status + Approved + Author cited |
| North Star | PASS/FAIL | Single-sentence statement present |
| Purpose | PASS/FAIL | Problem + Opportunity + Trigger present |
| Channels | PASS/FAIL | Table with ≥1 row (KB-only allowed) |
| Contributors | PASS/FAIL | Table includes Principal + agent owners |
| Streams | PASS/FAIL | Table with 2-6 streams |
| Capabilities (CAP-*) | PASS/FAIL | ≥1 CAP per stream |
| Verifications (V-*) | PASS/FAIL | ≥1 V-* paired with each CAP |
| Dependencies | PASS/FAIL | Table present |
| ADR-008 Readiness | PASS/FAIL | L-doc/SOP/Spec rows present |
| Sibling Relationships | PASS/FAIL | EVERY existing INIT classified |
| Approval Trail | PASS/FAIL | Decide gate + Loading Dock duration cited |
| Traceability | PASS/FAIL | Proposal / L-docs / Issues linked |

Any FAIL = REVERT scaffold; report to user; do NOT leave a partial INIT-*.md.

### Step 8: Cross-Initiative Coordination Check (C5 — MUST execute)

For each existing initiative in `planning/initiatives/INIT-*.md`:
- Verify classification appears in §"Relationship to Sibling Initiatives" of new manifest
- Classification vocabulary: Independent | Producer/Consumer | Sibling | Fold-Candidate | Redundant

For each PROPOSED-but-fileless entry in `planning/initiatives/INDEX.md`:
- Note overlap or distinction

If any Fold-Candidate or Redundant classification: ADD to §"Open Questions" of new manifest; surface to principal.

### Step 9: INDEX Update

Append to `planning/initiatives/INDEX.md`:
```
| INIT-{NAME} | NASCENT | YYYY-MM-DD | PP-### | one-line summary |
```

### Step 10: Skill Completion Signal

Report: status of all gates, file path, NASCENT → ACTIVE promotion checklist for principal.

## Enforcement Model

This skill is **Strict** per ADR-008 Layer 2 + D71 Structural Skill Routing:

| Action | Enforcement |
|--------|-------------|
| Direct Write/Edit to `planning/initiatives/INIT-*.md` | **PROHIBITED** — flag as governance bypass per L867 |
| `/aget-create-initiative` without Approved proposal | **REFUSED** at Step 2 |
| Missing manifest section | **REVERT** at Step 7.5 |
| Missing cross-initiative classification | **OPEN QUESTION** surface at Step 8 |

D71 Strict promotion: parallels `/aget-create-project` Strict. Future hook enforcement at v3.19+ via pre-commit gate (check that `planning/initiatives/INIT-*.md` was created within the same session as `/aget-create-initiative` invocation).

## Verification (V-tests)

| V-test | Verifies | Constraint |
|--------|----------|------------|
| V-CI-001 | Approved PROPOSAL_init_*.md exists before scaffold | C1 |
| V-CI-002 | Status defaults to NASCENT (never ACTIVE) | C2 |
| V-CI-003 | No proposal-step content inside the manifest | C3 |
| V-CI-004 | All SOP_initiative.md manifest sections present | C4 |
| V-CI-005 | Open Questions classifies every ACTIVE + PROPOSED initiative | C5 |
| V-CI-006 | Self-verification report executed at Step 7.5 | C6 |
| V-CI-007 | Filename matches INIT-{UPPER-KEBAB-CASE}.md pattern | structural |
| V-CI-008 | INDEX.md has matching row | structural |
| V-CI-009 | CAP-{NAME}-NNN and V-{NAME}-NNN naming present | structural |
| V-CI-010 | Sibling Mode-1 dual-approval recorded when applicable | structural |

## Composition (Verb-Pair)

`/aget-propose-initiative` (Advisory) → `/aget-create-initiative` (Strict — this skill)

Mirrors:
- `/aget-propose-project` (Advisory) → `/aget-create-project` (Strict)
- `/aget-propose-skill` (Advisory) → skill-implementation flow

The verb-pair is the canonical pattern per AGENTS.md §"Structural Skill Routing" (D71).

## Related Skills

- **`/aget-propose-initiative`** — sibling propose-side (Advisory); produces `PROPOSAL_init_*.md` consumed by this skill
- **`/aget-check-initiative`** — read-only cross-system coherence check; runs AFTER this skill creates the manifest
- **`/aget-create-project`** — Strict sibling for PROJECT_PLAN scaffolding
- **`/aget-enhance-spec`** — for v3.19+ when AGET_INITIATIVE_SPEC is authored, manifest enhancement routes here

## Traceability

| Link | Reference |
|------|-----------|
| Skill ID | SKILL-053 (`.aget/specs/skills/SKILL-053_aget-create-initiative.yaml`) |
| Proposal | `planning/skill-proposals/PROPOSAL_aget-create-initiative.md` (PROPOSED 2026-04-19) |
| Sibling skill (verb-pair) | `.claude/skills/aget-propose-initiative/SKILL.md` v1.0.0 |
| Sibling skill (structural mirror) | `.claude/skills/aget-create-project/SKILL.md` |
| Governing SOP (graduated procedure) | `sops/SOP_initiative.md` v1.2.0 |
| Future Governing Spec | `aget/specs/AGET_INITIATIVE_SPEC.md` (CANDIDATE — v3.19+ per PROPOSAL §Dependencies) |
| ADR | ADR-008 (Advisory → Strict → Generator progression — this skill graduates SOP_initiative to skill level Strict) |
| D71 | AGENTS.md §"Structural Skill Routing" (Strict enforcement level) |
| L-docs | L760 (Initiative as Scope Modifier), L867 (Coherence-Directed Investment as enhance-Verb-Family), L617 (Gate Ordering), L944 (Verb-Pair Discipline) |
| Verb registry | `ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md` v3.16 — `create` is verb #6 (Common, approved) |
| Trigger | 2026-04-19 INIT-REQ-SPEC-TEST-DEFINED direct-Write incident + 2026-05-16 INIT-FLEET-OBSERVABILITY direct-Write self-instance |
| v3.18 scope | VERSION_SCOPE_v3.18.0.md §2.9 T2.46 (post-Gate-1 amendment 2026-05-16 PM) |
| Closes | D71 STRUCTURAL gap on initiative-class authoring; verb-pair gap with `/aget-propose-initiative` |

---

*aget-create-initiative v1.0.0 — implemented 2026-05-16 PM under v3.18 scope amendment 2.9 (T2.46).*
*Category: Creation*
*Enforcement: Strict (ADR-008 Layer 2 + D71 Layer 2)*
*Verb family: propose-initiative (propose) → **create-initiative (this skill, create)** → check-initiative (verify) → enhance-spec (post-AGET_INITIATIVE_SPEC v3.19+)*
*Authored under principle-triad: spec+verify-first, coherence-next, evidence-driven, diligent (per principal directive 2026-05-16 PM)*
