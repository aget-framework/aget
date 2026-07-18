---
name: aget-propose-actions
description: Propose ranked next-best actions with evidence grounding, time budgets, and execute-all default. Formalizes the fleet's highest-frequency interaction pattern.
---

# /aget-propose-actions

Propose ranked next-best actions with evidence grounding, time budgets, and execute-all default. Supersedes the informal "step back. N next-best actions" trigger phrase.

## Purpose

The principal's most frequent interaction pattern across the entire fleet (3-5x per session, every agent, every session) is: "step back. N next-best actions, in this session, within the next M mins." Currently each agent interprets this differently — varying in depth, format, evidence citation, and execution behavior. This skill standardizes input parsing, KB review trigger (L335), output format, evidence grounding, parameterization, and the execute-all default (AGENTS.md).

**Evidence**: 34+ agents use identical phrasing. L637 (Mid-Session Steering via NBAs), L677 (Divergent Proposal Mode), L693 (5-action default), L787 (interpretation variance across agents). #721 (prior issue). 10+ invocations across 6 agents in v3.12.0 lifecycle.

## Input

$ARGUMENTS

Parameters (parsed from natural language):

| Parameter | Source | Default | Grammar |
|-----------|--------|---------|---------|
| `count` | First number in prompt | 5 (per L693) | "N next-best actions" |
| `budget` | Time expression in prompt | 30 min | "within the next N mins/hr" |
| `focus` | Remainder of prompt | Session mandate | "focus on X" / "for Y" |

**Authorization-shape flags (mode-gated — REQ-PA-017)**: the following are **documented** parameters, but `documented ≠ unconditionally accepted`. Their acceptance is **invoker-mode-gated** per Step 2.8: **principal-typed → ACCEPT** (REQ-PA-014); **agent-self-issued → REFUSE** (REQ-PA-015, preserves the L976/L979 NBA-fill safety core). Documenting them here promotes them out of "undocumented/aspirational" status (removing the per-session re-litigation friction the F1 arc surfaced) **without** loosening the agent-mode refusal.

| Flag | Meaning | Default | Acceptance gate |
|------|---------|---------|-----------------|
| `count=auto` | Agent picks the count from trigger-evidence (budget = ceiling, trigger-presence = floor) | off (use `count` numeric) | principal-mode only |
| `batch` | Treat the proposed set as one batch-authorizable unit | off | principal-mode only |
| `go` | Batch-level GO (satisfies Step 4.5); authorizes execution of **trigger-evidenced** actions only | off | principal-mode only |

Examples:
- `/aget-propose-actions` — 5 actions, 30-min budget, session mandate focus
- `/aget-propose-actions 3 actions within 45 mins` — 3 actions, 45-min budget
- `/aget-propose-actions 7 actions focus on release prep` — 7 actions, 30-min default, release focus
- `step back. 5 next-best actions, in this session, within the next 1hr` — Natural language trigger

## Execution

### Step 1: Parse Parameters

Extract `count`, `budget`, and `focus` from $ARGUMENTS or conversation context. Apply defaults for omitted parameters.

### Step 2: KB Review (L335)

Before proposing, scan current state:

1. Read active PROJECT_PLANs in `planning/` — identify current gates and pending deliverables
2. Check git status for uncommitted work
3. Review conversation context for session mandate and progress so far
4. Surface any pending work from prior sessions (resume hints)

This is mandatory (R-PA-005). Proposals without current-state grounding are stale.

### Step 2.5: D71 Structural Trigger Check (REQ-PA-011)

Before generating NBAs, evaluate each candidate Action against AGENTS.md §Structural Skill Routing (D71) trigger conditions:

| If candidate Action would | Required skill MUST be invoked |
|---------------------------|--------------------------------|
| Create `planning/PROJECT_PLAN_*.md` | `/aget-create-project` |
| Create `planning/initiatives/INIT-*.md` | `/aget-create-initiative` |
| File a GitHub issue | `/aget-file-issue` |

For each candidate Action, check whether the required skill has been invoked in the current session arc.

- **If all triggers either don't apply OR have a matching skill invocation**: proceed to Step 3.
- **If any trigger is met for an UN-invoked STRUCTURAL skill**: REFUSE the batch. Emit:
  > "REFUSAL (REQ-PA-011): D71 STRUCTURAL trigger met for {skill} but skill not invoked in current session arc. Redirect: invoke {skill} first, then re-run /aget-propose-actions. Principal override permitted per L178."
- **Override path** (L178): if the principal provides an explicit override phrase in the trigger prompt (e.g., "override D71 check — reason: ...") or a subsequent `/aget-go --reason <text>` invocation, proceed with override recorded in NBA preamble.

This is REQ-PA-011 (closes L962 structural-defense gap; gh#1414).

### Step 2.6: HANDOFF-Deferral Scan (REQ-PA-012; L961 Channel 2 wiring v3.18 G4.A)

Before generating NBAs, scan `docs/HANDOFF_*.md` files modified within the last 14 days. For each candidate Action subject (skill name, PROJECT_PLAN name, initiative name, issue number):

1. **Match check**: Does the candidate Action subject appear in any HANDOFF file's body or title? (substring match on skill name / plan slug / issue number)
2. **If MATCHED**:
   - Check the current session's trigger prompt for an explicit re-authorization phrase referencing the matched subject (e.g., "lift deferral on X", "re-authorize X", "execute X despite HANDOFF", `/aget-go X --reason "deferral lift"`)
   - **If re-auth phrase ABSENT**: REFUSE the candidate Action with:
     > "REFUSAL (REQ-PA-012): Candidate action {subject} matches HANDOFF deferral at {path} ({age} days old). HANDOFF artifacts mark deferral, not invitation (L961). Cross-session lift requires fresh re-authorization phrase in trigger or `/aget-go --reason 'deferral lift'`. Principal override permitted per L178."
   - **If re-auth phrase PRESENT**: proceed with override recorded in NBA preamble (form: `Override: REQ-PA-012 — deferral lift on {subject} authorized by trigger phrase "{phrase}"`).
3. **If no match**: proceed to Step 3.

**Implementation note**: skill consumers MAY use a simple grep over `docs/HANDOFF_*.md` files (`find docs -name "HANDOFF_*.md" -mtime -14`) and substring-match against candidate Action subjects. False-positive risk (incidental string match) is accepted; principal override via L178 closes it. False-negative risk (HANDOFF file at non-standard path, e.g. `handoffs/RELEASE_HANDOFF_*.md` which is release-handoff class, NOT deferral class) — REQ-PA-012 scope is `docs/HANDOFF_*.md` ONLY (deferral semantics); release-handoffs at `handoffs/` are out of REQ-PA-012 scope per L961 §"deferral marker, not invitation" definition.

This is REQ-PA-012 (closes L961 cross-session L908 propagation gap as Channel 2 wiring per L467 multi-channel propagation; v3.18 G4.A-2 deliverable). Empirical anchor: session_1730 H3 Critic finding where Action 6 violated session_1706 principal Decide despite explicit close-note deferral.

### Step 2.7: Audit-After-Synthesis Pre-Check (REQ-PA-013; L980 / gh#1476 Layer 5)

Before generating NBAs, inspect the proposed Action batch for **synthesis-without-paired-audit** on a governed artifact. This is the structural (Layer 5) wiring of the L980 audit-after-synthesis pairing rule — the action-layer analog of the scope-lock ceremony's G1.AUDIT step (SOP Channel-2) and AGENTS.md §Audit-After-Synthesis Pairing (Channel-1).

For each proposed Action, identify its target governed-artifact path (under `planning/`, `governance/`, `.aget/`, `aget/`, `ontology/`, `sops/`, `docs/`, or `AGENTS.md`/`CLAUDE.md`) and classify it per CAP-PA-013:

| CAP | Heuristic |
|-----|-----------|
| CAP-PA-013-01 (audit-class) | description contains a primary-source re-derivation verb (re-count / re-derive / re-grep / re-read / re-verify / audit / verify-from-source / reconcile / cross-check) |
| CAP-PA-013-02 (synthesis-class) | description contains a composition verb (compose / write / fold / update / narrate / summarize / draft / populate / integrate / annotate / add-row / merge) on a governed-artifact path |
| CAP-PA-013-03 (same-artifact detection) | normalized path equality (repo-relative, leading-`./` stripped, lowercased extension) across Actions in the batch |
| CAP-PA-013-04 (ambiguity, fail-safe) | when neither verb-set matches OR both match, default to **synthesis** — `audit` is returned only when an audit verb is present AND no synthesis verb is present, so a synthesis Action cannot masquerade as audit to satisfy the pairing |

**The check** (REQ-PA-013): WHEN ≥2 proposed Actions target the same normalized governed-artifact path, at least one of those Actions MUST classify as **audit-class**. The reference classifier is `scripts/propose_actions_classify.py` (`--check-batch <json>` / `--classify <text>`; `check_pairing()` returns `pairing_status` PASS|UNMET).

- **If satisfied (≥1 audit-class per same-artifact group)**: proceed to Step 3.
- **If UNMET (a same-artifact group has only synthesis-class Actions)**: surface as a **Healthy Friction** violation via AskUserQuestion with options:
  > "FRICTION (REQ-PA-013): Actions {indices} all write synthesis-class rows to {artifact} with no paired audit-class action. Per L980, synthesis on a governed artifact must be paired with an audit-class re-derivation from primary sources within the same batch, or the composed counts/claims commit unverified. Options: [add an audit-class Action that re-derives the artifact's quantities from primary sources / re-scope so the Actions touch distinct artifacts / proceed under L178 override with recorded reason / skip NBA]."
- **Override path** (L178): principal supplies an explicit override (e.g., `/aget-go --reason <text>`); the override + reason are recorded in the NBA preamble.

This is REQ-PA-013 (closes gh#1476 Layer 5; L980 audit-after-synthesis structural pairing; sibling pre-flight to Step 2.8's authorization-shape check). Friction is mandatory for an UNMET pairing; blocking is principal-elected (Healthy Friction negative-contract). See `.aget/evolution/L980_*.md`, AGENTS.md §Audit-After-Synthesis Pairing (Channel-1), `sops/SOP_scope_lock_ceremony.md` §G1.AUDIT (Channel-2, ceremony-layer).

### Step 2.8: Authorization-Shape Flag Pre-Check (REQ-PA-015 + REQ-PA-014)

Before generating NBAs, inspect the invocation for flag-form parameters in either of two classes (v1.7.1 two-class separation — post-REQ-PA-017, "aspirational" no longer describes the three promoted flags):

1. **Authorization-shape flags** (documented, mode-gated): `--count=auto`, `--batch`, `--go` — see §Input → Authorization-shape flags, REQ-PA-017. Promotion to documented status changed the *vocabulary* — these flags are no longer "undocumented/aspirational" — but did **not** change the *gate*: their acceptance remains invoker-mode-conditional, so the mode-check below still fires.
2. **Aspirational flags** (residual class): any other flag-form NOT in the documented parameter set (`count`, `budget`, `focus`, and the three authorization-shape flags). These remain undocumented; the same mode-check applies.

If no authorization-shape flag is present: proceed to Step 3.

If an authorization-shape flag IS present, determine the **invoker mode** before doing anything else:

| Mode | Detection (CAP) | Disposition |
|------|-----------------|-------------|
| **Agent-mode** (self-issued) | CAP-PA-015-01: the flag-form originates from the agent's own self-invocation within an active execution loop — the agent generated the `/aget-propose-actions …` call under its own budget pressure | **REFUSE (REQ-PA-015)** |
| **Principal-mode** (principal-typed) | CAP-PA-014-01: the flag-form appears in the **current session's user-prompt** — the principal explicitly typed it as the invocation | **ACCEPT (REQ-PA-014)** |

**Agent-mode → REFUSE (REQ-PA-015)** — emit:
> "REFUSAL (REQ-PA-015): flag-form {flag} is agent-self-issued ({class}: authorization-shape flags are documented but mode-gated; aspirational flags are undocumented). An agent-self-issued flag of either class triggers NBA-fill / deliberation-suspension at the execution-loop layer (L976/L979). Re-issue with a bounded `count`, OR proceed under explicit L178 override with `/aget-go --reason <text>`."

Surface via AskUserQuestion with options: [re-issue bounded count / skip NBA / explicit L178 override with reason / sidestep with a specific action] (CAP-PA-015-02).

**Principal-mode → ACCEPT (REQ-PA-014)**:
The principal explicitly typing the flag-form is a **declared authorization-shape** under standing L178 override — the explicit invocation plus conversation context IS the recorded reason. ACCEPT and proceed; do **NOT** surface the 4-option AskUserQuestion ceremony (that ceremony is itself the F1 friction the principal flagged on 2026-05-22 after ~7 friction events on the v3.19 arc) (CAP-PA-014-02).

Even in principal-mode, `--go` authorizes execution of **trigger-evidenced** actions only: budget is the ceiling, trigger-presence is the floor — the L976 core is preserved (CAP-PA-014-04).

**Ambiguity resolution (CAP-PA-014-03 / CAP-PA-015-03)**: if mode detection cannot disambiguate within one inference step, default to **REFUSE** and surface via AskUserQuestion. Fail safe, not fail open.

**Examples (authorization-shape modes)**:
- Principal types `/aget-propose-actions --count=auto --batch --go` → **principal-mode → ACCEPT**; execute trigger-evidenced actions, no ceremony.
- Agent self-issues `/aget-propose-actions --budget=60 --count=auto --batch --go` inside its own execution loop → **agent-mode → REFUSE (REQ-PA-015)**; surface the 4-option AskUserQuestion.
- Principal types `/aget-propose-actions 5 actions` (no authorization-shape or aspirational flag) → Step 2.8 is a no-op; proceed to Step 3.

This implements REQ-PA-015 (agent-mode refusal — closes the L976/L979 self-issue vector; gh#1463/#1475) and REQ-PA-014 (principal-mode acceptance — F1; closes the friction-fatigue gap of 2026-05-22; L1070 — formerly mis-cited as "L987/L988 candidates": those numbers were consumed by unrelated lessons 2026-05-23; the principal-mode lesson is filed as L1070, 2026-06-12). It is the Channel-2 (point-of-use) wiring of AGENTS.md §"NBA Authorization-Shape Discipline" + §"Principal-Mode Exception" per L467 multi-channel propagation.

### Step 3: Generate Actions

For each proposed action:
1. Derive from KB review findings, session mandate, and focus area
2. Estimate duration (must fit within budget)
3. Cite evidence (L-doc, issue number, session finding, or PROJECT_PLAN reference)
4. Assess risk-if-skipped (what happens if this is deferred)

Rank by value-to-time ratio. Total estimated time MUST fit within budget.

### Step 3.5: Self-Critique (REQ-PA-018/019/020; C-22-02 / #1094/#1095/#1096)

**Before** presenting (Step 4), run the **10-point self-critique checklist** over the drafted Action set. The principal routinely prompts "critique this report" after emission; the resulting critique historically surfaces ~10 defects recoverable without new research (L025, session 2026-04-23, private-social-media-AGET — obs093–105). Running it inline pre-empts that round-trip. For each point, if the set fails, **re-ideate the offending action(s) before Step 4** — do not present a known-defective set.

| # | Checklist point | Test | Source |
|---|-----------------|------|--------|
| 1 | **Budget-fit** | Does the set use (not under/over-use) the budget window? | obs093 |
| 2 | **Agent-scope per action** | Is each action within THIS agent's write-scope + authority (no cross-fleet / out-of-mandate creep)? | obs101 |
| 3 | **Evidence grounding** | Does every action cite verifiable evidence (no stretches / unsupported claims)? | obs103 |
| 4 | **No option-menus** | Does any action hide a decision as "(a) or (b)?" instead of doing the obvious in-scope next action (Skill C4)? | obs094 |
| 5 | **Named-person leverage** (REQ-PA-019) | Scanned MEMORY.md for named people with standalone entries; does the focus map to anyone's expertise → candidate outreach action? | obs097 / #1095 |
| 6 | **Action-type diversity** (REQ-PA-020) | Is the set all-artifact, or does it include ≥1 non-artifact action (measurement / outreach / wait / handoff)? | obs098 / #1096 |
| 7 | **Cite-freshness** | Are cited figures / issue numbers / statuses re-verified at source (no stale-propagation recidivism)? | obs095 |
| 8 | **Same-day-reframe bias** | For public-facing / irreversible actions, is a soak/wait the right default before acting on a same-session reframe? | obs096 |
| 9 | **Target verification** | Are referenced targets (URLs, files, identifiers) verified to exist? | obs102 |
| 10 | **Baseline / measurement** | Is a measurement baseline missing that a measurement action should establish first? | obs104/105 |

**Structural enforcement (budget ≥ 1 day)** — these two points are not advisory at longer budgets:
- **REQ-PA-019 (named-person)**: at least ONE named-person leverage check MUST appear in the output — either as an executed outreach Action OR as an explicit "no named-person fit for this focus" note. The check is mandatory; proposing outreach is not.
- **REQ-PA-020 (non-artifact)**: the set MUST contain ≥1 non-artifact Action (Type ∈ {measurement, outreach, wait, handoff}). If the drafted set is 100% artifact, re-ideate to replace ≥1, or emit an explicit footer flag if no non-artifact action genuinely fits.

At budget < 1 day, points 5–6 are advisory (run the check; no hard requirement). Points 1–4 and 7–10 always apply.

### Step 4: Present (v3.20 C-F1 enhancement — evidence-visible · recommendation-led · decisions-surfaced)

Output using standardized format:

```
**[Agent Name] -- [count] Next-Best Actions ([budget]-minute window):**

**Session goal**: [restate primary objective]
**Progress**: [key milestones reached]
**▶ Recommendation**: [the single highest-value action + one-line why — what the agent would do first if the principal does nothing else]

| # | Action | Type | Time | Principal | Value | Evidence | Risk if Skipped |
|---|--------|:----:|:----:|:---------:|-------|----------|-----------------|
| 1 | ... | artifact | N min | Autonomous | ... | [L-doc / #issue / finding / PROJECT_PLAN] | ... |

**Type** ∈ {artifact, measurement, outreach, wait, handoff} (#1096 Option C — makes action-type bias *visible* without refusing output). At budget ≥ 1 day, REQ-PA-020 requires ≥1 non-`artifact` row (Step 3.5 point 6).

**⚠ Decisions needed** (Decide-class — block execute-all until ruled):
- #N: [the judgment call, framed as a question + the agent's lean]
  (omit this block entirely when no Decide-class action is present)

Execution default: all [count], priority order — adapted by Principal role (per Execute-All Default).
```

**C-F1 rationale** (v3.20; INIT-PRINCIPAL-EXPERIENCE Stream 2, CAP-PEX-003 — wire wow-lever into propose-actions): the highest-frequency session surface gains three principal-facing improvements over the prior flat table:
1. **Evidence column** — surfaces the per-action citation Step 3.3 already gathers but the prior table dropped; the principal can *inspect the grounding* of each option, not just its label (raises V3 reach / observability).
2. **▶ Recommendation line** — the agent's single lead pick + why, so the principal sees a *recommendation*, not only a menu (the L680 decision-impact lever).
3. **⚠ Decisions-needed callout** — Decide-class items are lifted out of the table into an explicit block framed as questions, so required judgment calls don't hide among autonomous rows.

**Principal column values** (derived from Decision Authority Matrix):

| Value | Meaning | Execute-All Behavior |
|-------|---------|---------------------|
| **Autonomous** | Agent executes, no principal involvement | Auto-execute |
| **Approve** | Agent proposes, principal gives GO | Pause for GO |
| **Decide** | Principal must make a judgment call | Present options, wait |
| **Execute** | Human-only action | Surface as handoff |
| **Inform** | FYI, no action needed | Display only |

### Step 4.5: Batch GO Capture (REQ-PA-006a)

**Before** any Autonomous-class action auto-executes (per Step 5), the agent SHALL capture an explicit `/aget-go` for the action-batch as a whole. The batch-level GO is a precondition for execute-all default behavior — it does NOT substitute for per-action Principal-classification handling (Step 5), and per-action handling does NOT substitute for it.

Two-layer GO model:

| Layer | Surface | Trigger |
|-------|---------|---------|
| **Batch-level** (this step) | `/aget-go` for the proposed action set as a whole | After Step 4 presentation, before Step 5 auto-execute fires |
| **Per-action** (Step 5) | Pause-for-GO on Approve-class items; Decide-class options; Execute-class handoff | Per Principal column classification |

Without batch-level GO, no auto-execute (including Autonomous-class) fires. The skill output is a proposal; the principal's `/aget-go` is the authorization to begin Step 5.

**Rationale**: per-action Principal classification (REQ-PA-008/009) is necessary but not sufficient. In post-ceremony resume sessions, structural-self-conformance discipline relaxes (L908 self-application gap), and Autonomous-class items can auto-execute under the per-action rules without a batch-level GO ever being captured. Evidence: 2-of-2 sessions on 2026-05-09 (gh#1267).

### Step 5: Execute-All Default (Principal-Adapted)

**Precondition**: Step 4.5 (batch GO captured). If no `/aget-go` authorization record cites this batch, do NOT proceed to Step 5.

After presenting AND after batch GO captured, execute actions adapted by their Principal classification:
- **Autonomous**: Execute immediately in priority order
- **Approve**: Present and wait for explicit GO before executing
- **Decide**: Present options with trade-offs, wait for principal's decision
- **Execute**: Surface as handoff — agent cannot execute these
- **Inform**: Display only, no execution step

Do NOT ask "which ones?" for Autonomous items — the default is full execution. Pause only where the Principal column requires it.

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-PA-001 | Propose-actions SHALL include identity header (agent name + session goal) | #618, SP-011 |
| REQ-PA-002 | NBA count SHALL match requested count or explain shortfall | SP-011 |
| REQ-PA-003 | Each NBA SHALL cite evidence (L-doc, issue, or session finding) | SP-011, L335 |
| REQ-PA-004 | Total estimated time SHALL fit within budget parameter | SP-011 |
| REQ-PA-005 | KB review SHALL be performed before proposing (active plans, git status) | L335, SP-011 |
| REQ-PA-006 | Execute-all SHALL be the default behavior after presentation | AGENTS.md Execute-All Default |
| REQ-PA-006a | Before any auto-execute action runs (Autonomous-class included), the agent SHALL capture an explicit `/aget-go` for the action-batch as a whole. The batch-level GO is a precondition for REQ-PA-006; it neither replaces nor is replaced by REQ-PA-009 per-action Principal-classification handling. | gh#1267, L854 (selective spec-first), L963 (verify-before-authorize), 2-of-2 evidence 2026-05-09 |
| REQ-PA-007 | Focus parameter SHALL constrain all NBAs to the specified area | SP-011 |
| REQ-PA-008 | Each proposed action SHALL include a Principal column classifying the principal's required involvement (Autonomous, Approve, Decide, Execute, Inform) | DESIGN_DIRECTION_propose_actions.md, Decision Authority Matrix |
| REQ-PA-009 | Execute-all default behavior SHALL adapt to the Principal classification per action | REQ-PA-008, DESIGN_DIRECTION_propose_actions.md |
| REQ-PA-011 | Pre-flight (Step 2.5) SHALL evaluate each candidate Action against AGENTS.md §Structural Skill Routing (D71). If a trigger is met for an un-invoked STRUCTURAL skill, the skill SHALL REFUSE the batch with explicit redirect. Principal override permitted per L178. | L962, gh#1414, AGENTS.md D71 |
| REQ-PA-012 | Pre-flight (Step 2.6) SHALL scan `docs/HANDOFF_*.md` files (≤14 days old) for matches against each candidate Action subject. If matched AND no re-authorization phrase appears in the current session's trigger prompt, the skill SHALL REFUSE the candidate with explicit redirect to fresh `/aget-go --reason 'deferral lift'` invocation. Principal override permitted per L178. | L961 (HANDOFF-deferral cross-session L908), L467 (multi-channel propagation), AGENTS.md §HANDOFF-Deferral Discipline |
| REQ-PA-013 | Pre-flight (Step 2.7) SHALL classify each proposed Action targeting a governed artifact as synthesis-class or audit-class per CAP-PA-013-01/02 and detect same-artifact groups per CAP-PA-013-03. WHEN ≥2 Actions target the same normalized governed-artifact path, at least one SHALL classify as audit-class; if UNMET, the skill SHALL surface a Healthy Friction violation (AskUserQuestion: add-audit-Action / re-scope / L178-override / skip). Ambiguity defaults to synthesis (CAP-PA-013-04, fail-safe). Reference classifier: `scripts/propose_actions_classify.py`. | L980 (audit-after-synthesis self-catch), gh#1476 (Layer 5), L908/L939/L960 (verification chain), L467 (Channel-2 sibling at ceremony layer = SOP G1.AUDIT) |
| CAP-PA-013-01 | audit-class heuristic: description contains a primary-source re-derivation verb (re-count/re-derive/re-grep/re-read/re-verify/audit/verify-from-source/reconcile/cross-check) | REQ-PA-013, L939 |
| CAP-PA-013-02 | synthesis-class heuristic: description contains a composition verb (compose/write/fold/update/narrate/summarize/draft/populate/integrate/annotate/add-row/merge) on a governed-artifact path | REQ-PA-013, L980 |
| CAP-PA-013-03 | same-artifact detection: normalized path equality (repo-relative, leading-`./` stripped, lowercased extension) | REQ-PA-013 |
| CAP-PA-013-04 | ambiguity fail-safe: neither-match OR both-match → synthesis; `audit` only when audit-verb present AND synthesis-verb absent (synthesis cannot masquerade as audit) | REQ-PA-013, L908 |
| REQ-PA-014 | WHEN the skill is invoked with an authorization-shape flag-form (`--count=auto`, `--batch`, `--go`) AND the invoker is principal-mode (the flag appears in the current session's user-prompt), the framework SHALL ACCEPT the flag-form as a declared authorization-shape under standing L178 override and SHALL NOT surface the 4-option refusal ceremony. `--go` authorizes execution of trigger-evidenced actions only (budget = ceiling, trigger-presence = floor). | F1; L1070 (principal-mode lesson, filed 2026-06-12 — supersedes the "L987/L988 candidates" citation; those numbers were consumed by unrelated lessons), L976 (core preserved), L178 (override), L467 (Channel-2), AGENTS.md §Principal-Mode Exception |
| REQ-PA-015 | WHEN the skill is invoked with an authorization-shape flag-form (`--count=auto`, `--batch`, `--go`) OR an aspirational (undocumented) flag-form, AND the invoker is agent-mode (self-invocation within an active execution loop), the framework SHALL REFUSE the flag-form and surface for principal re-issuance with a bounded `count`, OR proceed under explicit L178 override with recorded reason. Aspirational flags are any flag-form NOT in the documented parameter set (`count`, `budget`, `focus`, and the authorization-shape flags per REQ-PA-017). | L976 (NBA-fill / deliberation-suspension), L979 (24h self-recurrence), gh#1463/#1475, L178 (override) |
| REQ-PA-017 | The authorization-shape flags `--count=auto`, `--batch`, `--go` SHALL be documented first-class parameters (§Input → Authorization-shape flags). Documentation SHALL NOT loosen their acceptance gate: acceptance remains invoker-mode-conditional (principal-mode ACCEPT per REQ-PA-014; agent-mode REFUSE per REQ-PA-015). Promotion removes the "undocumented/aspirational" framing (and its per-session re-litigation friction) while the L976/L979 safety core is preserved unchanged. | F1 arc (2026-06-01 principal directive); L976/L979 (safety core preserved), L1070 (principal-mode lesson — corrected citation 2026-06-12), L467 (Channel-2 vocabulary alignment), REQ-PA-014/015 (acceptance gate retained) |
| REQ-PA-018 | Pre-presentation (Step 3.5) SHALL run the 10-point self-critique checklist over the drafted Action set; any failing point SHALL be re-ideated before Step 4. Points 1–4 and 7–10 always apply; points 5–6 are advisory at budget < 1 day and structurally required at budget ≥ 1 day (REQ-PA-019/020). | C-22-02; #1094; L025 (obs093–105 self-critique), L908 (verify-before-present) |
| REQ-PA-019 | WHEN budget ≥ 1 day, the output SHALL include ≥1 named-person leverage check — either an outreach Action or an explicit "no named-person fit for this focus" note — derived from a MEMORY.md pass over named people with standalone entries. | C-22-02; #1095; obs097 |
| REQ-PA-020 | WHEN budget ≥ 1 day, the Action set SHALL contain ≥1 non-artifact Action (Type ∈ {measurement, outreach, wait, handoff}); a 100%-artifact set SHALL be re-ideated or carry an explicit footer flag. The Step 4 output table SHALL carry a **Type** column (Option C) to make action-type bias visible. | C-22-02; #1096 (Option C); obs098 |

## V-tests

| ID | Test | Pass criterion |
|----|------|----------------|
| V-PA-006a | After /aget-propose-actions output, before any Autonomous auto-execute fires, the session record SHALL contain a `/aget-go` authorization record citing the proposed batch | Authorization record present in `sessions/session_*.md` with scope referencing the batch (e.g., `scope: batch-N` or `scope: action-1..N proposed by /aget-propose-actions`). Falsifier: any Autonomous-class action executed in same session without a preceding `/aget-go` capture record = REQ-PA-006a regression. |
| V-PA-012 | Given a session with an active HANDOFF deferral in `docs/HANDOFF_*.md` (≤14 days), invoke `/aget-propose-actions` with a candidate Action subject matching the HANDOFF subject AND no re-authorization phrase in trigger | Skill output contains REFUSAL message citing REQ-PA-012 and the matched HANDOFF path. Falsifier: any NBA batch including the matched subject without an explicit override-recorded preamble = REQ-PA-012 regression. Smoke test: simulate by creating `docs/HANDOFF_test_v3.18_g4a.md` referencing subject X; invoke skill with X as candidate; expect REFUSAL. |
| V-PA-013 | Replay the L980 session arc (2026-05-21): batch of 3 Actions on `planning/initiatives/INDEX.md` — 2 synthesis (fold/update) + 1 audit (audit stream-stamps) | `check_pairing()` returns `pairing_status=PASS` (audit-class present); removing the audit Action returns `UNMET` + the REQ-PA-013 Healthy Friction surface; a 2-Action batch on distinct artifacts returns `PASS` (no same-artifact group, no false-positive). `python3 scripts/propose_actions_classify.py --self-test` exits 0; `python3 -m pytest tests/test_propose_actions_step_2_7.py -v` all PASS. Falsifier: a same-artifact synthesis-only batch that does not surface the friction = REQ-PA-013 regression (re-opens the L980 vector). |
| V-PA-014 | Principal types `/aget-propose-actions --count=auto --batch --go` in the current user-prompt | Skill ACCEPTS (principal-mode), proceeds to generate trigger-evidenced actions, and emits NO 4-option AskUserQuestion ceremony. Falsifier: any REFUSAL or 4-option ceremony surfaced in response to a principal-typed authorization-shape flag = REQ-PA-014 regression (re-introduces the F1 friction-fatigue gap). |
| V-PA-015 | Agent self-issues `/aget-propose-actions --budget=N --count=auto --batch --go` within its own execution loop (no principal-typed flag in current user-prompt) | Skill output contains REFUSAL message citing REQ-PA-015 and surfaces the 4-option AskUserQuestion. Falsifier: any agent-self-issued authorization-shape or aspirational flag batch that auto-executes without REFUSAL or L178-recorded override = REQ-PA-015 regression (re-opens the L976/L979 vector). |
| V-PA-017 | After REQ-PA-017 promotion, re-run V-PA-014 (principal-typed → ACCEPT) AND V-PA-015 (agent-self-issued → REFUSE) | Both pass unchanged: promotion altered vocabulary (flags now documented) but NOT the gate. Falsifier: V-PA-015 now passing the agent-self-issued flag through (because it is "documented") = REQ-PA-017 regression — promotion silently loosened the acceptance gate, re-opening the L976/L979 vector. |
| V-PA-018 | Invoke the skill; inspect whether Step 3.5 ran before Step 4 (the 10-point checklist is applied to the drafted set) | Step 3.5 self-critique is performed pre-presentation; a set failing any always-on point (1–4, 7–10) is re-ideated, not presented. Falsifier: a presented set with an obvious budget-misfit / option-menu / unverified-target defect that Step 3.5 should have caught = REQ-PA-018 regression. |
| V-PA-019 | Invoke with budget ≥ 1 day in an agent whose MEMORY.md names ≥1 person with a standalone entry | Output contains ≥1 named-person leverage check (outreach Action OR explicit "no named-person fit" note). Falsifier: a ≥1-day report with zero named-person checks despite a named standalone entry = REQ-PA-019 regression (re-opens obs097). |
| V-PA-020 | Invoke with budget ≥ 1 day; inspect the Action set Type column | Set contains ≥1 non-`artifact` Type, OR carries an explicit footer flag justifying an all-artifact set; the table renders a Type column. Falsifier: a ≥1-day 100%-artifact set with no re-ideation and no footer flag = REQ-PA-020 regression (re-opens obs098 artifact-production bias). |

Notes:
- V-PA-006a is the falsifier-test for the new REQ-PA-006a. Wiring (the capture mechanism that produces the audit record at runtime) is owned by INIT-PRINCIPLED-EXECUTION Stream 1 / v3.18 T1.10 — separate from this spec amendment.
- Existing requirements REQ-PA-001..005 + REQ-PA-007..009 + REQ-PA-011 do not yet have V-tests defined; gap acknowledged at T1.8 GO-time (s=UNMET on the broader V-test scope, V-PA-006a closes only the new requirement). Broader V-test backfill is candidate for v3.19 P2 or INIT-SKILL-MATURATION Stream 2.

## Constraints

- **C1**: This skill is NBA-only — do NOT include kb-review, kb-maintenance, or plan-revision modes (those are separate concerns)
- **C2**: MUST perform KB review before proposing — proposals without current-state grounding are prohibited
- **C3**: MUST cite evidence for every action — no unsupported suggestions
- **C5**: MUST REFUSE the batch when D71 trigger is met for an un-invoked STRUCTURAL skill (REQ-PA-011). Refusal is a negative-contract requirement; override path is L178 with explicit reason.
- **C4**: MUST NOT ask "which ones?" after presenting — execute-all is the default
- **C6**: MUST NOT proceed to Step 5 auto-execute without a preceding `/aget-go` authorization record citing the proposed batch (REQ-PA-006a precondition). Override path is L178 with explicit reason.
- **C7**: MUST distinguish invoker mode before acting on an authorization-shape or aspirational flag-form (REQ-PA-014/REQ-PA-015). Agent-self-issued flags of either class MUST be REFUSED (Step 2.8); principal-typed authorization-shape flags MUST be ACCEPTED without refusal ceremony. On ambiguity, default to REFUSE (fail safe). This is a Healthy-Friction negative-contract — friction is mandatory for agent-mode; blocking is principal-elected.

## Traceability

| Link | Reference |
|------|-----------|
| Spec | SKILL-024_aget-propose-actions v1.8.0 (private-repo-local SKILL-NNN label; numbering collision noted — at canonical `../aget/.aget/specs/skills/`, SKILL-024 = `/aget-review-pr`; /aget-propose-actions has no canonical SKILL-NNN yet. Tracked for v3.18 retrospective / F-G-1-B) |
| Closes | gh#1414 (REQ-PA-011 D71 pre-flight, L962 structural defense); gh#1267 partial (REQ-PA-006a spec amendment — wiring closure pending T1.10); L961 cross-session L908 Channel 2 wiring (REQ-PA-012; v3.18 G4.A-2); gh#1463/#1475 (REQ-PA-015 agent-mode aspirational-flag refusal; v3.19 T1.2); F1 principal-mode acceptance (REQ-PA-014; v3.19 T1.5) |
| L-docs (added v1.3.0) | L961 (HANDOFF-deferral cross-session L908), L962 (Skill-Selection Discipline Lives Only in Habit Channel), L467 (Critical Pattern Propagation — multi-channel), L854 (Spec-First Applied Selectively — empirical basis for REQ-PA-006a), L963 (Verify-Before-Authorize — companion discipline at GO-step) |
| L-docs (added v1.5.0) | L976 (budget+go → NBA-fill / deliberation-suspension at execution-loop layer — REQ-PA-015 origin), L979 (L976 24h cross-session self-recurrence), ~~L987 + L988 (candidates)~~ → **L1070** (principal-mode default; corrected 2026-06-12 — the candidate numbers L987/L988 were consumed by unrelated lessons filed 2026-05-23, leaving the citation dangling until L1070 was filed), L974/C707 (over-application / Skilled Incompetence — failure mode REQ-PA-014 guards) |
| REQ-PA-013 collision | Resolved at F1 Gate -1 (2026-05-23): REQ-PA-013 + Step 2.7 → L980 audit-after-synthesis (T1.1, retains); REQ-PA-014 → F1 principal-mode (this amendment); REQ-PA-015 → L976 aspirational-flag refusal (this amendment); REQ-PA-016 → L973/gh#1458 pending-signoff (reserved, deferred) |
| Design Direction | `docs/DESIGN_DIRECTION_propose_actions.md` v0.1.0 |
| Proposal | SP-011 (`planning/skill-proposals/PROPOSAL_aget-propose-actions.md`) |
| Supersedes | PROPOSAL_aget-step-back.md (scope narrowed to NBA-only) |
| Verb family | propose-skill (SP-NNN), propose-project (SP-NNN), propose-actions (SP-011) |
| Upstream issues | #721 (aget-next-actions), #618 (identity header), #865 (NBA rendering) |
| L-docs | L335 (Memory Architecture), L637 (Mid-Session Steering), L677 (Divergent Proposal), L693 (5-action default), L787 (interpretation variance) |

---

*aget-propose-actions v1.8.0* (v1.8.0: **C-22-02 / v3.22 Gate 2** — Step 3.5 Self-Critique (10-point checklist from L025 obs093–105) + REQ-PA-018/019/020 + V-PA-018/019/020 + Type column on the Step 4 table (#1096 Option C); #1094 (self-critique) + #1095 (named-person leverage, budget≥day) + #1096 (≥1 non-artifact action, budget≥day); 2026-06-13. v1.7.1: vocabulary completion of REQ-PA-017 — two-class separation in Step 2.8 (authorization-shape = documented mode-gated trio; aspirational = residual undocumented flags); REFUSE-message factual fix (the trio IS documented post-017); L987/L988 candidate citations rebound to L1070; gate unchanged — V-PA-014/015/017 semantics preserved; 2026-06-12. v1.7.0: REQ-PA-017 — promote `--count=auto`/`--batch`/`--go` to documented mode-gated parameters; acceptance gate unchanged (REQ-PA-014/015 preserved); F1 arc 2026-06-01. v3.19 T1.1: Step 2.7 Audit-After-Synthesis Pre-Check — REQ-PA-013 + CAP-PA-013-01..04 + classifier `scripts/propose_actions_classify.py`; L980/gh#1476 Layer 5. v1.5.0: Step 2.8 aspirational-flag — REQ-PA-014/015 T1.2+T1.5)
*Category: Research*
*Verb family: propose-skill, propose-project, propose-actions*
