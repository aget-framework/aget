# /aget-propose-goals

Propose N ranked **candidate session-goals** scored ex-ante by `RUBRIC_goal_selection_v1.0`, recorded for retrospective audit. The goal-altitude sibling of `/aget-propose-actions` (action-altitude).

## Purpose

Formalize the mid-session **candidate-goals** pattern. When a session faces a pivot decision — the principal asks "what should we do next?" or the agent independently identifies a choice point — the prior ad-hoc pattern produced N candidate goals in conversation, informally described, with no durable scored artifact. This skill:

- Generates N candidate goals in divergent-proposal mode (L677), each with a one-sentence thrust + beneficiary tag
- Scores each ex-ante with `RUBRIC_goal_selection_v1.0` (5 dimensions, /15)
- Presents ranked by total score with the dominant dimension surfaced per candidate
- **Records** the scored candidate set in the session file so retrospectives can audit "why did we pivot to G2?"

**Plurality (L1067)**: `propose-goals` is **PLURAL** — a candidate-set generator (output is *selected*, not scaffolded), structurally a sibling of `propose-actions`, NOT of the singular commitment-pipeline skills (`propose-project`/`propose-skill`). It has no `create` counterpart; a selected goal funnels into the (separate, downstream) `create-goal` committer when the Goal-tier lands.

**Evidence**: SP-017 (`planning/skill-proposals/PROPOSAL_aget-propose-goals.md`); parent L845 (session-pivot rubric gap); L1067 (two-propose semantics); `RUBRIC_goal_selection_v1.0` (the scoring engine, reflexively validated G3>G1>G2).

## Input

`<topic>` — optional focus for the candidate goals.

Parameters (parsed from natural language or flags):

| Parameter | Source | Default | Grammar |
|-----------|--------|---------|---------|
| `count` | First number in prompt | **3** (goal-altitude default; heavier than the 5-action default per L693) | "propose N candidate goals" |
| `focus` | Remainder of prompt | Session mandate | "focus on X" / "for Y" |
| `budget` | Context % or time hint | Remaining session capacity | "within remaining context" |

**Appetite-flexes-scope (E9, Shape Up).** `budget` is an **appetite**, not an estimate: it is fixed first, and a candidate's scope flexes to fit it — never the reverse. When a goal's natural scope exceeds the appetite, the rubric's D1 (Context Budget Fit) scores it down and the goal is **cut to fit** (de-scoped) or deferred — the appetite is not silently expanded to rescue an over-large goal. This is the L131 (stopping-point bypass) guard at the goal-selection layer: "right work, wrong size" is a pivot failure mode, and a fixed appetite forces the scope decision up front.

Examples:
- `/aget-propose-goals` — 3 candidate goals, session-mandate focus
- `/aget-propose-goals propose tomorrow's main goals` — 3 candidates for next session
- `/aget-propose-goals 4 candidate goals for the v3.23 release` — 4 candidates, release focus
- `which goal should this session pursue` — natural-language trigger

## Triggers

When the user says:
- "propose N candidate goals" / "propose goals"
- "what are our goal candidates" / "score these goal candidates"
- "which goal should this session pursue"
- "propose tomorrow's main goal(s)"

## Execution (6 steps)

### Step 0: Auto-Fire Trigger (E2 — advisory)

A session-pivot is the moment this skill is most valuable and most often skipped. Two **mechanically detectable** pivot signals SHOULD auto-fire `/aget-propose-goals` before new substrate is started:

```bash
# (a) post-ceremony resume — same trigger as PATTERN_post_ceremony_critic_autofire
git log -5 --pretty=format:"%s" | grep -Eiq "SCOPE_LOCK|RELEASED|cycle.close|wind.down" && echo PIVOT
# (b) explicit step-back — the principal asks "what next?" / runs a step-back command
```

On either signal, propose goal candidates (this skill) before `/aget-propose-actions`.

**Ceiling (L474–476)**: a skill is model-followed instruction, not harness-enforced — so true *automatic* firing needs a hook. That hook is **deferred to the canonical wake-up / PreToolUse infrastructure** built by `PROJECT_PLAN_self_oversight_structural_enforcement` (#618 channel-4) and is **not duplicated here** — same hook mechanism, distinct trigger. Until then E2 is advisory: documented trigger + agent discipline.

### Step 1: Parse Parameters

Extract `count` (default 3), `focus` (default session mandate), `budget` (default remaining session capacity) from the trigger or conversation context. Apply defaults for omitted parameters.

### Step 2: KB Review (L335)

Before generating candidates, scan current state — read active PROJECT_PLANs in `planning/`, session state / pending work queues, git status, and the conversation mandate. This is **mandatory**: candidates without current-state grounding are stale. The KB review is what makes a goal *valuable* — it surfaces what is blocked, decaying, or on-mandate.

### Step 3: Generate Candidates

Produce `count` candidate goals (N ∈ [2, 7]). Each candidate carries:
- A one-sentence **thrust** (what the goal pursues)
- A **beneficiary tag** ∈ {`principal`, `supervisor`, `framework-production`, `framework-learning`, `ecosystem`} (per the rubric's beneficiary taxonomy)
- A **commitment-type tag** ∈ {`committed`, `aspirational`} (E7 — honesty axis; see Step 4.5)
- A short **dependency note** (what it unblocks / waits on)

### Step 4: Score with RUBRIC_goal_selection_v1.0

Score every candidate on the 5 dimensions (L0–L3 each, equal-weighted, /15):

| Dim | Name | Captures |
|-----|------|----------|
| D1 | Context Budget Fit | fit to remaining session capacity |
| D2 | Evidence Decay Risk | value lost if deferred |
| D3 | Scope Alignment | match to session mandate |
| D4 | Blast Radius / Reversibility | impact + cost-to-undo if wrong |
| D5 | Unblocking Value | queued work unlocked on success |

`Goal Score = D1 + D2 + D3 + D4 + D5` (range 0–15). Rubric invocation is **mandatory** (C1) — an unscored goal is decorative (L671).

### Step 4.5: Honesty + Shape-It Gates (E7 + E8)

Two governance gates folded in from the sibling `SOP_near_term_ambition_projection` (L1090 — the SOP and this skill are one intent at two altitudes). They run after scoring, before the recommendation:

**E7 — Commitment-type honesty (C6).** Tag each candidate `committed` or `aspirational` — a tag *orthogonal* to the score (a high-scoring goal can still be aspirational):

| Tag | Meaning |
|-----|---------|
| `committed` | The principal/agent is prepared to spend this session's capacity on it now; it has (or needs no) a governed vehicle and a clear done-state. |
| `aspirational` | A want worth surfacing, but not yet bettable this session — under-shaped, dependency-blocked, or capacity-deferred. |

A goal scoring high on value (D2/D5) but with no governed vehicle is **aspirational, not committed** — present it as such. An `aspirational` goal **MUST NOT** be presented as `committed` (C6) — that is the OKR honesty failure the tag prevents.

**E8 — Unshaped→shape-it gate (C7; imports L174 ambition–governance inversion).** The most ambitious-sounding candidate is often the *least* shaped — it gap-selects an unshaped aspiration. So: if the recommended target is `aspirational` **or** lacks a governed vehicle (no owning `planning/PROJECT_PLAN_*` / `planning/initiatives/INIT-*` / spec), the recommended next action is a **shape-it** action (`/aget-propose-project`, `/aget-propose-initiative`, or `/aget-create-project`), **never** a do-it action. Shaping *is* the progress; direct execution of an unshaped goal is the inversion L174 names.

### Step 5: Present

Rank by total score; surface the **dominant dimension** per candidate; state the recommended pivot target; **break ties explicitly** (C5 — principal preference or documented beneficiary-tag heuristic, never left ambiguous).

### Step 6: Record (structural — E1)

Append the scored candidate set to the current session file so retrospectives can audit the pivot decision. Session-file recording is **mandatory** (C2) — it is the anti-decorative guard that makes the scoring auditable.

**Structural close (E1)**: recording is no longer pure advice. Write the scored set (the Output Format table) inside a `PROPOSE-GOALS-RECORD` block via the helper, so a session-protocol verifier or retrospective can *bite* on a record-free pivot:

```bash
python3 scripts/record_goals_ext.py --record --session <current session file> \
    --focus "<restated focus>" --table-file <rendered scored table>
# negative control (a presented-but-unrecorded set fails this — exit 1):
python3 scripts/record_goals_ext.py --verify --session <current session file>
```

The helper is best-effort (a recording failure warns + exits 1 but MUST NOT abort the skill — the set was still presented). This moves C2 from advisory agent-discipline to a checkable surface (L605/L671 close).

## Output Format

```
**[Agent Name] -- [count] Candidate Goals (remaining context: X%):**

**Current focus**: [session mandate restated]
**Scoring**: RUBRIC_goal_selection_v1.0

| # | Goal (thrust) | Tag | Commit | D1 | D2 | D3 | D4 | D5 | Score | Dominant Dim |
|---|---------------|-----|--------|:--:|:--:|:--:|:--:|:--:|:-----:|--------------|
| 1 | G1 thrust | beneficiary | committed | 3 | 2 | 2 | 2 | 3 | 12 | D5 (unblocks deadlock) |
| 2 | G2 thrust | beneficiary | aspirational | 1 | 1 | 3 | 2 | 3 | 10 | D3 (on-mandate, context-heavy) |
| 3 | G3 thrust | beneficiary | committed | 3 | 3 | 2 | 3 | 2 | 13 | D2 (evidence decays if deferred) |

**▶ Recommended pivot target**: G3 (13/15)
**Tie-break (if any)**: [principal preference / beneficiary-tag priority]
**Shape-it gate (E8)**: [if the recommended target is `aspirational` or has no governed vehicle → name the shape-it action, e.g. "G2 is aspirational + unshaped → next action is `/aget-propose-project`, not direct execution"]
```

## Relationship to `/aget-propose-actions`

| Dimension | `propose-actions` | `propose-goals` |
|-----------|-------------------|-----------------|
| Scope | executable steps *within* a goal | session-level *direction* |
| Count default | 5 (L693) | 3 |
| Budget | time-window (e.g., 30 min) | session-capacity (context budget) |
| Rubric | NBA 6D | `RUBRIC_goal_selection_v1.0` |
| Execute-all default | yes (Principal-adapted) | **no — goals are selected, not executed-all** |
| Output durability | ephemeral (conversation) | **recorded** (session file) |

The two compose: `propose-goals` picks direction; `propose-actions` executes within it. When the Goal-tier lands, the funnel is `propose-goals` → `create-goal` → `propose-actions` (L1067).

## Constraints

- **C1**: Rubric invocation is **mandatory** — unscored goals are decorative (L671 guard).
- **C2**: Session-file recording is **mandatory** — retrospective audit is the anti-decorative guard.
- **C3**: N ≥ 2 — a singleton is not a candidate set; use `/aget-propose-project` for single-goal commitment.
- **C4**: N ≤ 7 — beyond 7 exceeds principal working memory (Miller 1956); if more candidates exist, cluster first.
- **C5**: Ties MUST be broken explicitly (principal preference or documented heuristic) — never left ambiguous.
- **C6** (E7 — commitment-type honesty): Each candidate MUST carry a commitment-type tag (`committed` | `aspirational`). An `aspirational` goal MUST NOT be presented as `committed` — a high score does not make a want a commitment (folded from `SOP_near_term_ambition_projection`, L1090).
- **C7** (E8 — unshaped→shape-it gate): A recommended target that is `aspirational` OR lacks a governed vehicle (no owning `planning/PROJECT_PLAN_*` / `planning/initiatives/INIT-*` / spec) MUST route to a **shape-it** action (`/aget-propose-project` / `/aget-propose-initiative` / `/aget-create-project`), never to direct execution (L174 ambition–governance inversion).

## Dependencies

- `RUBRIC_goal_selection_v1.0.md` (the scoring engine — present)
- `/aget-propose-actions` (companion — executes within the selected goal)
- Session-file convention for candidate-set recording

## When to Use

| Scenario | Use /aget-propose-goals |
|----------|-------------------------|
| Mid-session pivot decision ("what next?") | Yes — score candidates before pivoting |
| "Propose tomorrow's main goals" | Yes — ex-ante goal selection for next session |
| Choosing among ≥2 session directions | Yes — divergent-proposal mode |
| Individual steps within a chosen goal | No — use `/aget-propose-actions` |
| Committing to a single named goal | No — use `/aget-propose-project` (or `create-goal` when the tier lands) |

## Related Skills

- `/aget-propose-actions` — action-altitude sibling (executes within a selected goal)
- `/aget-propose-project` — singular commitment-pipeline (single-goal artifact)
- `/aget-create-rubric` — authored the scoring engine this skill invokes

## Traceability

| Link | Reference |
|------|-----------|
| Spec | SKILL-055_aget-propose-goals v1.0.0 |
| Proposal | SP-017 (`planning/skill-proposals/PROPOSAL_aget-propose-goals.md`) |
| Rubric | `rubrics/RUBRIC_goal_selection_v1.0.md` |
| L-docs | L845 (parent — session-pivot rubric gap), L846 (companion action-rubric gap), L1067 (two-propose semantics / plurality), L677 (divergent proposal), L693 (count default), L671 (classification without consequence), L839 (reflexive validation) |
| Owning initiative | INIT-CORE-ARTIFACT-MATURATION Stream 9 (PP-051) |
| Verb family | propose-skill (SP-009) / propose-project (SP-006) / propose-actions (SP-011) / propose-initiative (SP-NNN) / **propose-goals (SP-017)** |
| Tests | `tests/test_propose_goals.py` |

---

*aget-propose-goals v1.0.0*
*Category: Planning*
*Plural candidate-set generator (L1067) — no `create` sibling; funnels to `create-goal` when the Goal-tier lands.*
