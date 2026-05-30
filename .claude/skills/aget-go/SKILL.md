---
name: aget-go
description: Record principal authorization (GO) with Healthy Friction enforcement of the principle-triad (spec+verify-first, coherence-next, evidence-driven); release agent execution within authorized scope. Authorization-only — does not execute the authorized work.
---

# /aget-go

Record principal authorization to proceed with a scoped piece of work, with Healthy Friction enforcement of three principles before release-to-execute.

## Purpose

Across the fleet, "GO" signals from the principal vary in clarity (`yes`, `proceed`, `do it`, `ok`), in scope (gate? action? entire goal? whole session?), and in audit value (none — they're free-text in the conversation). When the principal subsequently asks "what did we authorize?", the only record is the conversation log. This skill formalizes GO as an explicit, scoped, principle-checked, audit-traceable authorization act.

**Healthy Friction posture** (Tier 2 #11): friction MUST occur (mandatory verification of three principles); blocking is principal-elected (override preserved with reason). Distinct from Advisory (no friction) and Strict (hard block).

**Composition discipline**: this skill authorizes; it does NOT execute the authorized work. Execution is a separate act performed by the agent under the released authorization.

## Evidence

L854 (Spec-First Applied Selectively — awareness alone is insufficient), L466 (Question Is Not Approval), L178 (Human Override Principle — acknowledge / commit / execute), L671 (Classification Without Consequence — anti-pattern Healthy Friction prevents), L42 (Stop At Gate Boundaries). Espanso compensating-control retirement: `;;g*pr*` triggers retired in favor of governed `;;ago*`.  [instance-only per L600]

## Input

`$ARGUMENTS`

| Flag | Default | Purpose |
|------|---------|---------|
| `--scope <gate\|action\|goal\|session>` | resolve from context | What is being authorized |
| `--principles <triad>` | `svc-ed` (spec+verify, coherence, evidence-driven) | Which principle pre-conditions to verify |
| `--count N --shape {actions\|goals}` | absent | Compose with delegate skill (propose-actions / propose-goals) |
| `--dry-run` | false | Produce report without writing record |
| `--record-only` | false | Write record but do NOT signal release-to-execute |
| `--reason <text>` | absent | Required when overriding an UNMET pre-condition |

Example invocations:
- `/aget-go` — bare; scope resolved from active conversation; default principle triad enforced
- `/aget-go --scope gate` — disambiguate scope when ambiguous
- `/aget-go --count 5 --shape actions` — compose with `/aget-propose-actions --count 5`, then authorize the result
- `/aget-go --dry-run` — pre-commit check: would this GO pass principle verification?
- `/aget-go --reason "research session, no implementation"` — override an UNMET condition with recorded reason

## Execution

### Step 1: Resolve scope (CAP-GO-002)

If `--scope` is supplied, use it directly. Otherwise, scan conversation context for unambiguous active scope:
- Active gate (most recent `Gate {N}` deliverable not yet [x])
- Active action proposal (most recent `/aget-propose-actions` table)
- Active goal proposal (most recent `/aget-propose-goals` table)
- Whole session (fallback)

If multiple plausible scopes are active, REFUSE and list candidates. Ambiguous GO is worse than no GO (L466).  [instance-only per L600]

### Step 2: Verify principles (CAP-GO-003)

For the selected principle triad (`--principles svc-ed` default), run:

| Principle | Pre-condition Check |
|-----------|---------------------|
| **spec+verify-first** (`s`) | Active scope's PROJECT_PLAN names a governing spec AND has V-tests defined |
| **coherence-next** (`c`) | No vocabulary collisions, no conflicting active plans, no stale index entries in referenced scope |
| **evidence-driven** (`e`) | At least one L-doc, issue number, or evidence-bank entry cited in the scope's rationale |
| **diligent** (`d`) | (optional) — depth check: 3+ files read OR 3+ greps before scope locked |

For each, emit `PASS` or `UNMET <reason>`.

### Step 3: Healthy Friction decision (CAP-GO-004)

If all PASS: proceed to Step 4 (write record + release).

If any UNMET: surface the unmet conditions and pause. The principal chooses:
- **acknowledge** — proceed with override; `--reason <text>` MUST be supplied; reason is recorded in the authorization record
- **remediate** — pause, fix the unmet condition, re-invoke `/aget-go`

Friction is mandatory; blocking is principal-elected. The override path preserves principal authority while making the override visible in the audit trail.

### Step 4: Write authorization record (CAP-GO-001)

Append to the active session file (`sessions/session_YYYY-MM-DD_HHMM.md` or equivalent):

```markdown
### Authorization Record — {timestamp}

| Field | Value |
|-------|-------|
| session_id | {session id} |
| scope | {gate-N.M / action-N / goal-N / session} |
| principle_triad | svc-ed (or as supplied) |
| principles_status | s=PASS, c=PASS, e=PASS (or UNMET fields) |
| flags | --count, --shape, --dry-run, --record-only as supplied |
| override | (only if UNMET acknowledged) reason={text} |
| delegate_output | (only if --shape) reference to delegate's output |
```

Skip this step if `--dry-run`.

### Step 5: Release-to-execute (CAP-GO-006)

If not `--record-only` and not `--dry-run`: signal that the agent may proceed with the authorized work. The signal is conversational ("GO recorded — proceeding with {scope}"); the actual execution is a SEPARATE act performed by the agent's next tool invocations under this authorization.

The skill itself MUST NOT perform the authorized work. Composition discipline: GO authorizes, EXECUTE performs.

## Composition (CAP-GO-005)

When `--count N --shape {actions|goals}` is supplied:

1. Invoke the delegate skill first: `/aget-propose-actions --count N` or `/aget-propose-goals --count N`
2. Let the delegate produce its output (action table or goal list)
3. Treat the delegate's output as the scope being authorized
4. Run principle verification on the delegate's output
5. Write authorization record referencing the delegate's output
6. Release-to-execute applies to the delegate's actions/goals as a batch

## Constraints

- **C-GO-001**: SKILL shall NOT execute the authorized work. Execution is the agent's next act.
- **C-GO-002**: SKILL shall NOT write outside the session file (authorization record is the only allowed write).
- **C-GO-003**: Bare invocation MUST resolve scope unambiguously or REFUSE.
- **C-GO-004**: Override decisions MUST include free-form reason text. Reason is the audit value.
- **C-GO-005**: SKILL MUST support `--dry-run` for every invocation shape.
- **C-GO-006**: SKILL MUST NOT elevate its own enforcement to Strict without explicit ADR + principal approval.

## Espanso Migration

`/aget-go` retires three espanso compensating controls under POL-DEP-001 (grace v3.15 → v3.17):

| Retiring | Replacement | Notes |
|----------|-------------|-------|
| `;;g_pr_` | `;;ago_` | bare `/aget-go` |
| `;;g3pr_` | `;;ago3a_` (3 actions) or `;;ago3g_` (3 goals) | composed |
| `;;g5pr_` | `;;ago5a_` (5 actions) or `;;ago5g_` (5 goals) | composed |

Grammar: `a` (anchor) + `go` + `xy` optional, where `x` = count digit, `y` = shape letter (a=actions, g=goals).

## Anti-Patterns

| Anti-Pattern | Why Wrong |
|--------------|-----------|
| Free-text "go" / "proceed" / "yes" | No record, no scope, no principle check; auditable only via conversation log (L466) |  [instance-only per L600]
| Skill executes the authorized work | Conflates authorization and execution; loses Two-Level Model separation (L742) |  [instance-only per L600]
| Override without reason | Healthy Friction without recorded reason is ceremony; reason is the audit value (C-GO-004) |
| Skipping principle verification "because it's a small change" | L854 Selective Spec-First Application — the very anti-pattern Healthy Friction prevents |  [instance-only per L600]

## Traceability

| Link | Reference |
|------|-----------|
| Spec | `aget/.aget/specs/skills/SKILL-048_aget-go.yaml` v1.0.0 |
| Proposal | SP-022 (`planning/skill-proposals/PROPOSAL_aget-go.md`) |
| Coupled artifact | `governance/GOVERNANCE_PRINCIPLES.md` Tier 2 #11 (Principled Execution) |
| L-docs | L854 (selective spec-first), L466 (question ≠ approval), L178 (human override), L671 (classification w/o consequence), L42 (gate boundaries) |  [instance-only per L600]
| Verb family | `propose` (propose-actions, propose-goals, propose-skill, propose-project) → `go` (this skill, authorizes) → execute (agent's next act, this skill does NOT do it) |
| ADR position | Healthy Friction = between Advisory and Strict (ADR-008 progression); friction mandatory, block principal-elected |
| Closes | #1136 (GO discipline), #1158 (SKILL-024 GO gate); part of v3.16 INIT-PRINCIPLED-EXECUTION |

---

*aget-go v1.0.0 — promoted 2026-05-02 (v3.16 G1.7)*
*Category: Governance / Authorization*
*Verb family: propose, go (this skill), execute*
