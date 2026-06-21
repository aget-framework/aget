---
name: aget-close-project
description: Close a PROJECT_PLAN with verifiable-assertion gate (V-tests + commits + retrospective), deferred-surface scan for next-plan handoff, and status transition (ACTIVE → COMPLETE / CLOSED / ABANDONED / SUPERSEDED). Strict counterpart to /aget-create-project (D71 Layer 2). Closes asymmetric verb-pair gap at PROJECT_PLAN lifecycle.
---

# /aget-close-project

Terminally close a PROJECT_PLAN with verifiable assertion, closure checklist, and deferred-surface handoff. Strict counterpart to `/aget-create-project`.

## Input

$ARGUMENTS — PROJECT_PLAN filename (or slug; resolved against `planning/`)

## Mode Detection

| Input Pattern | Mode | Behavior |
|---------------|------|----------|
| Empty | **Interactive** | List candidate plans (status=IN PROGRESS or all gates [x]), prompt for selection |
| `<filename>` or `<slug>` | **Explicit** | Resolve to `planning/PROJECT_PLAN_<name>.md`; close that plan |
| `<filename> --reason <text>` | **Explicit with reason** | Required for non-COMPLETE closures (CLOSED, ABANDONED, SUPERSEDED) |
| `<filename> --override <text>` | **L178 override** | Bypasses gate-completion gate (Step 2) with recorded reason |

## Project Closure Process

### Step 0: Scope-Fit + Identity Check

1. Read `.aget/identity.json` — extract `name`, `domain`
2. Resolve PROJECT_PLAN path; verify file exists under `planning/`
3. If file absent: ERROR with candidate-list suggestion

### Step 1: Input Analysis

Parse $ARGUMENTS:
- Plan filename or slug
- Optional `--reason <text>` (required for CLOSED/ABANDONED/SUPERSEDED)
- Optional `--override <text>` (L178 path — bypasses Step 2 with recorded reason)

### Step 2: Gate-Completion Gate (Strict — C-CLOSE-001)

**Automate the scan, don't eyeball it** (C-P1 guard, v3.20; L736 assert-before-verify):
```bash
python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md
```
Exit 2 = BLOCK (unchecked conformance signals listed: Pending/In-Progress gate status, PENDING V-test rows, unchecked Closure/Finalization items). Exit 0 = clean. The script is the consumer's check (C-P4) that backs the prose criteria below — do not assert closure-readiness without running it.

**REFUSE close** if any of:
- Any gate marked `[ ]` (unmarked) in plan body — UNLESS override path
- Any V-test result missing for a CAP that has gates
- Plan header `**Status:**` field absent or not parseable
- `close_gate_check.py` exits 2 (unchecked conformance signals) — UNLESS override path

**Output on refusal**:
```
REFUSE: /aget-close-project gate-completion gate failed
  Plan: planning/PROJECT_PLAN_<name>.md
  Unmarked gates: <list>
  Missing V-tests: <list>
  Override path: re-invoke with --override "<reason per L178>"
```

**Override path (L178)**: principal supplies reason; recorded in retrospective + commit.

### Step 2.5: Authorization Gate (Strict — C-CLOSE-002; L1102 / Q3:A hardening)

**A principal-attributed close MUST link its authorizing event; an irreversible consequence MUST be legible.** This closes the L1102 root cause — the v3.23 close recorded `Reason (principal-ruled): ... private milestone / fold to v3.24` with no linked authorization event and no legibility on the irreversible consequence (burning the `v3.23.0` public number).

```bash
python3 scripts/close_authorization_guard.py planning/PROJECT_PLAN_<name>.md
```
Exit 1 = BLOCK. Two checks fire only when relevant (an agent-autonomous close with no irreversible consequence passes — guard N/A):
- **CHECK-A**: the close reason attributes the decision to the principal (`principal-ruled`, `approved by the principal`, …) but carries **no authorization-event pointer** (a `/aget-go` record, an `Authorization log` entry, an AskUserQuestion/`Q#:X` selection, a dated principal quote). Free-text "(principal-ruled)" is **not** provenance.
- **CHECK-B**: the close carries an **irreversible / identity-level consequence** (private milestone, skip/burn a public version, fold to a later version, abandon a public release) that is **not made legible** — the consequence must be surfaced explicitly, never buried under a mechanism label, and never agent-*recommended* against a standing requirement (e.g. "release publicly each weekend").

**REFUSE close** if the guard exits 1 — UNLESS `--override` with a recorded L178 reason. On a principal-attributed close, the fix is to add the event pointer (link the GO/selection), not to override.

### Step 3: Research Phase

Before writing closure artifacts, gather context:

#### 3.1 Read full PROJECT_PLAN body
- All gate sections
- All V-test result blocks
- Existing retrospective section (if any)
- All deferred-surface markers ("deferred to next session", "Loading Dock", "spawn", "future")

#### 3.2 Read sibling closed plans for closure-pattern grounding
```bash
grep -l "^\*\*Status\*\*:\s*COMPLETE" planning/PROJECT_PLAN_*.md | head -3
```
Read the most recent 1-2 closed plans to ground retrospective style.

#### 3.3 Read commit log for this plan
```bash
git log --oneline -- planning/PROJECT_PLAN_<name>.md
```
Build V-test → commit-SHA mapping (per L001: gate completion = plan update + commit).

### Step 4: Closure Checklist Authoring (C-CLOSE-002)

Generate or update these sections in the plan body (per AGET_PROJECT_PLAN_SPEC template, CAP-PP-013/016/018):

1. **Retrospective** (required, non-empty):
   - **Worked**: What landed as intended
   - **Didn't Work**: Friction, rework, gaps
   - **Spawned**: Items routed to other plans / initiatives / L-docs
2. **Velocity Analysis**: gates planned vs gates landed; time-on-plan vs estimate
3. **Closure Checklist** (per template — 10 items spec-defined)
4. **Finalization Checklist** — pre-close gates: index updated, supervisor notified, handoff filed if applicable

### Step 5: Status Transition (C-CLOSE-003 — Verifiable Assertion)

Update `**Plan_Status**:` header field to one of:

| Status | Meaning | Required Evidence |
|--------|---------|-------------------|
| **COMPLETE** | All gates [x], V-tests pass, retrospective recorded | Full closure checklist + V-test SHA mapping |
| **CLOSED** | Terminated without full completion (deferred/superseded/abandoned) | `--reason` text + reroute targets in retrospective |
| **ABANDONED** | Closed without success, no reroute | `--reason` text + lesson-record link |
| **SUPERSEDED** | Replaced by another plan | Pointer to replacement plan filename |

**Verifiable-Assertion requirement (per CAP-PRJ-001)**: Status transition is NOT text-edit alone. The transition is valid only when accompanied by:
- V-test summary block referencing commit SHAs
- Closure timestamp + closing agent identity
- Retrospective section non-empty

### Step 6: Deferred-Surface Scan (C-CLOSE-004 — MANDATORY)

Scan plan body for deferred-surface markers and emit a structured list for next-plan handoff (L913 closure):

```
## Deferred Surface (emitted by /aget-close-project — consumed by /aget-propose-actions Step 2 KB review)

| Item | Source line | Suggested route |
|------|-------------|-----------------|
| <text matching "deferred to next session" / "Loading Dock" / "spawn" / "future"> | line N | <next-plan candidate or initiative stream> |
```

This block MUST be written verbatim into the plan body (under section `## Deferred Surface`). `/aget-propose-actions` SKILL-024 v1.3.0+ scans for this header at next-plan-creation time (per #1186 wiring).

### Step 7: Output Summary

Emit one-page summary to stdout:
```
=== /aget-close-project: <plan-slug> ===

Plan: planning/PROJECT_PLAN_<name>.md
Status transition: <prev> → <new>
Gates: <X/Y> [x]   V-tests: <A/B> recorded
Retrospective: <N> lines  Deferred-surface items: <N>
Closure timestamp: <ISO-8601>
Closing agent: <identity from .aget/identity.json>
Commit prep: ready (run `git add` + `git commit` per L001)
```

### Step 7.5: Self-Verification (C-CLOSE-005)

For each closure-checklist item, emit PASS/FAIL line:
```
self-verify:
  retrospective:        PASS (3 sub-sections non-empty)
  velocity_analysis:    PASS
  closure_checklist:    PASS (10/10 items addressed)
  finalization:         PASS
  deferred_surface:     PASS (N items scanned)
  status_assertion:     PASS (V-test SHA mapping recorded)
```

If any FAIL: do NOT proceed to Step 8; surface for principal review.

### Step 8: Cross-Plan Coordination

- If `planning/INDEX_PROJECT_PLANS.md` exists (Stream 3 deliverable of INIT-PROJECT-MATURATION): update row for this plan
- Scan plan body for "Spawned" items in retrospective; flag any that lack a target plan/initiative/L-doc
- Update owning initiative file (if plan references one) — mark stream/deliverable status if applicable

### Step 9: INDEX update (C-CLOSE-006)

When `planning/INDEX_PROJECT_PLANS.md` exists: MUST update the row corresponding to this plan with new status + closure date. If INDEX absent (Stream 3 not yet landed): emit a one-line note in the closure summary noting the gap.

### Step 10: Skill completion signal

Emit terminal block:
```
/aget-close-project: COMPLETE
  Plan closed: <path>
  Next action: git add <path> && git commit (commit IS structural proof — L001)
  Deferred-surface emitted: yes (consumed by next /aget-propose-actions)
```

## Constraints

- **C-CLOSE-001 (Strict gate)**: REFUSE close if any gate `[ ]` or any V-test missing. Override path L178 with `--reason`.
- **C-CLOSE-002 (Closure checklist completeness)**: All template sections must be non-empty before write.
- **C-CLOSE-003 (Verifiable assertion)**: Status transition requires V-test SHA mapping + timestamp + agent identity. Text-edit alone is insufficient.
- **C-CLOSE-004 (Deferred-surface scan mandatory)**: Step 6 MUST execute. Output is consumed by `/aget-propose-actions` (L913 closure).
- **C-CLOSE-005 (Self-verification)**: Step 7.5 PASS for every checklist item before Step 8 fires.
- **C-CLOSE-006 (INDEX update mandatory when present)**: When `INDEX_PROJECT_PLANS.md` exists, MUST update.

## Enforcement Level

**Strict** (D71 Layer 2 — per AGENTS.md §Structural Skill Routing). Direct status-field edit on a PROJECT_PLAN's `**Plan_Status**:` from IN PROGRESS to COMPLETE/CLOSED/ABANDONED/SUPERSEDED via Edit/Write is **PROHIBITED**. The closure must route through this skill so that:
- Gate-completion gate (C-CLOSE-001) fires
- Verifiable-assertion requirement (C-CLOSE-003) is met
- Deferred-surface scan (C-CLOSE-004) emits L913 handoff

**Known risk** (transparent at v1.0): `AGET_PROJECT_PLAN_SPEC` is DRAFT (#1180). Strict enforcement before spec finalization is principal-authorized (2026-05-21 GO). Follow-on: when spec lands, V-tests V-PRJ-001/002/004 wire to this skill's constraints.

**Override path (L178)**: `--override "<reason>"` bypasses Step 2 only. Records reason in retrospective + commit message. Does not waive Steps 4-7.5.

## Related Skills

- `/aget-create-project` — sibling verb-pair (Strict, exists). Pair completes lifecycle bookend.
- `/aget-propose-actions` — consumer of Step 6 Deferred Surface output (SKILL-024 v1.3.0+).
- `/aget-record-lesson` — for ABANDONED closures with lesson-record link.
- `/aget-close-session` — sibling close-mode skill (different artifact class: session vs project).

## Traceability

| Link | Reference |
|------|-----------|
| Skill ID | SKILL-052 (`.aget/specs/skills/SKILL-052_aget-close-project.yaml`) |
| Proposal | `planning/skill-proposals/PROPOSAL_aget-close-project.md` (APPROVED 2026-05-21) |
| Owning Initiative | INIT-PROJECT-MATURATION (Stream 4 — Lifecycle Symmetry; highest-WSJF per PP-020 D4) |
| Sibling verb-pair | `/aget-create-project` (Strict) |
| Spec (governing) | AGET_PROJECT_PLAN_SPEC.md (DRAFT — #1180) |
| L-docs | L001 (gate discipline), L617 (gate ordering), L649 (closure-time structural gap — originating), L675 (consequence gap), L908 (apply-to-others-not-self), L913 (plan-close→create handoff), L131 (stopping-point bypass), L178 (Human Override), L735 (push window) |
| CAPs | CAP-PRJ-001 (verifiable assertion), CAP-PRJ-002 (closure handoff scan), CAP-PRJ-004 (symmetric close-side gate), CAP-PRJ-007 (Loading Dock detection — consumer) |
| V-tests (pending spec landing) | V-PRJ-001, V-PRJ-002, V-PRJ-004 |
| Cross-fleet evidence | FLEET-UPG-013 + FLEET-UPG-014 D4 root cause (status-field text-edit) |
| Verb registry | `close` (Active, row 29, Common, added v3.13.0; paired with `open`) |
| Architecture | SKILL.md-driven (mirrors `/aget-create-project`); no companion script per 2026-05-21 proposal revision |

---

*aget-close-project v1.0.0*
*Category: Governance (lifecycle bookend)*
*Enforcement: Strict (D71 Layer 2)*
