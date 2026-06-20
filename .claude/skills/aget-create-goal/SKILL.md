---
name: aget-create-goal
description: Commit a selected candidate goal into a durable, governed Goal artifact. The D71-Strict singular committer of the propose-goals→create-goal verb pair (L1067/L1085). Two-tier (REQ-3): committed goals = a structured section in governance/GOALS.md; aspirational = agent-internal .aget/goals/aspirational.jsonl. Direct authoring of a committed-Goal section is PROHIBITED once this skill is invoked. Implements AGET_GOAL_SPEC v0.2.0 (CAP-GOAL-001..011).
---

# /aget-create-goal

Commit a Goal — a durable, named, cross-session **outcome** (C926) — into governed storage. The singular committer that consumes a `/aget-propose-goals` candidate; the create-side of the verb pair (L1067 two-propose semantics; L1085 plural-leads-singular).

**Enforcement: D71-Strict (CAP-GOAL-008).** Once invoked, direct Write/Edit of a committed-Goal section in `governance/GOALS.md` is **PROHIBITED** — creation MUST route through this skill, which writes the `provenance` field that the bypass check reads. Mirrors `/aget-create-project` and `/aget-create-initiative`.

## Input

`<candidate>` — a selected `/aget-propose-goals` candidate, or a goal description. Flags: `--aspirational` (record to the agent-internal tier instead of committing).

## Engine

The falsifiable core is `scripts/create_goal.py` (11 firing falsifiers in `tests/test_create_goal.py`, ADR-007). This skill orchestrates it; the script enforces the spec.

## Steps

### Step 0: Tier decision (REQ-3 two-tier)
- **Committed** (default): a goal the principal commits to → structured section in `governance/GOALS.md` (principal-facing surface), D71-Strict.
- **Aspirational** (`--aspirational`): a candidate not yet committed → `.aget/goals/aspirational.jsonl` (agent-internal), Advisory. Promotion aspirational→committed is a later `create-goal` (committed) act.

### Step 1: Conflation guard (CAP-GOAL-002 / C930)
Reject a "goal" defined by workstreams/tasks rather than a measurable end-state. `validate_outcome()` fires on stream-enumeration with no outcome. If rejected, return the candidate to `/aget-propose-project` (it is a project, not a goal).

### Step 2: Required fields
- `type` ∈ {Achieve, Maintain, Soft} (CAP-GOAL-003)
- `≥1 loop` ⟨owner, trigger, review-action, consequence, cadence⟩ at creation (CAP-GOAL-004 / MP#12) — a Goal without a loop is an orphan that decays. The skill REFUSES to commit a loop-less Goal.
- `parent` (Theme/Initiative) where one exists (CAP-GOAL-001)
- `status: active` set at creation (CAP-GOAL-011)

### Step 3: Commit
- Committed → `commit_goal()` writes the structured section incl. `provenance` (this skill's invocation) + idempotency guard on id.
- Aspirational → `append_aspirational()`.

### Step 4: Lifecycle (CAP-GOAL-011)
Status transitions are governed edits. **Type-differentiated terminal**: an **Achieve** Goal reaches `achieved`; a **Maintain** Goal has no `achieved` (it persists under its loop; terminate via `abandoned`/`superseded`). `validate_transition()` enforces this.

## Constraints (INVIOLABLE)

1. **NEVER** author a committed-Goal section in `governance/GOALS.md` without this skill (D71-Strict bypass; CAP-GOAL-008).
2. **NEVER** commit a Goal with zero bound loops (CAP-GOAL-004).
3. **NEVER** commit a Goal defined by workstreams not an outcome (CAP-GOAL-002).
4. **NEVER** transition a Maintain Goal to `achieved` (CAP-GOAL-011).
5. **DO** write aspirational goals to the agent-internal tier, off the governance surface (CAP-GOAL-006b).

## Traceability

| Link | Reference |
|------|-----------|
| Spec | AGET_GOAL_SPEC v0.2.0 (`aget/drafts/AGET_GOAL_SPEC.md`) — CAP-GOAL-001..011 |
| Engine | `scripts/create_goal.py` · Tests `tests/test_create_goal.py` (11) |
| Verb pair | `/aget-propose-goals` (SKILL-055, plural producer) → `/aget-create-goal` (SKILL-057, singular committer) |
| SKILL ID | SKILL-057 |
| Owning Initiative | INIT-CORE-ARTIFACT-MATURATION Stream 9 (PP-051); v3.23 release C-23-01 |
| L-docs | L1067, L1085 (verb-pair semantics); MP#12 (loop binding); L656 (lifecycle/Loading-Dock); L742 (REQ→CAP) |

> **Canonical-promotion gate**: this skill + spec are DRAFT. Promotion to canonical (`aget/`) + the AGENTS.md D71 routing-table row + public push are gated on (a) the 3-concept grounding gap (Goal Identifier/Goal Value/Commitment Tag — INIT-ONTOLOGY-MATURATION) and (b) the L735 weekend window. Locally drivable now.

---

*aget-create-goal v0.1.0 — "A Goal is an outcome that owns a loop." (SKILL-057)*
