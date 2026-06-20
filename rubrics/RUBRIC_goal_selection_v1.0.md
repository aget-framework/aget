# Goal Selection Scoring Rubric

**Version**: 1.0.0
**Created**: 2026-04-17
**Author**: private-aget-framework-AGET
**Domain**: Session-pivot ex-ante goal selection — scoring candidate goals mid-session
**Archetype**: Decision (Score-before-act)
**Assessor**: Hybrid (agent scores, principal reviews)
**Status**: Draft
**Trigger**: L845 — session-pivot ex-ante rubric coverage gap surfaced during G1/G2/G3 candidate scoring

---

## Purpose

Score candidate session goals **before** committing, so that mid-session pivots are auditable, consistent, and auto-proposable. Complements existing rubrics:
- `RUBRIC_scope_item_priority` — ex-ante, release-planning layer
- `RUBRIC_session_outcome_value` — post-hoc, session layer
- This rubric — ex-ante, session-pivot layer

Supports decisions:
- "Of these N candidate goals, which should this session pursue?"
- "Should we pivot from the current goal to a newly surfaced one?"
- "Is the goal the principal just proposed a good fit for this session's capacity?"
- "Retrospectively: why did we pivot to G2 instead of G3?"

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Session-level goals (30 min – 2 hr scope) | Version-scope items (use `RUBRIC_scope_item_priority`) |
| Ex-ante scoring (pre-commit) | Post-hoc outcome evaluation (use `RUBRIC_session_outcome_value`) |
| Candidate goals from `/aget-propose-goals`-style divergent mode | Individual actions within a goal (use NBA-style rubric) |
| Single-principal session context | Multi-stakeholder prioritization (L808 — not applicable to AGET) |

## Theoretical Basis

| Framework | Application |
|-----------|-------------|
| **L677** (Divergent Proposal Mode) | Presupposes N candidate goals — this rubric scores them |
| **L808** (Arrow's Impossibility / Single-Principal) | One decision-maker; sidesteps voting paradoxes |
| **L709** (Project Plan Quality Rubric Gap) | Precedent: high-frequency decision + no rubric = documented risk |
| **L744** (Skill Service Boundary Rubric Gap) | Companion precedent for rubric-absence as gap class |
| **L671** (Classification Without Consequence) | Rubric is "Strict" — must influence actual pivot decision, not decorative |
| **ADR-008** (Advisory → Strict → Generator) | Strict enforcement: score each candidate goal before pivot commit |
| **WSJF** (Reinertsen 2009) | Inspiration for weighted-by-time framing in D1 |
| **Dawson 2017** | Rubric design: observable criteria, L0-L3 scale |

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| 5 dimensions | Matches NBA 5D and other AGET action-layer rubrics. "If scoring takes longer than deciding, you've gone too far." |
| Equal weights (20% each) | No calibration data. Revisit after N>5 scored pivots. |
| L0-L3 scale | Coherence with 13 existing AGET rubrics |
| Beneficiary as tag, not dimension | Categorical, not scoreable; used to group candidates |
| Reflexive validation mandatory | Rubric must discriminate on known-good candidates (L839 pattern) before publication |

---

## Dimensions

### D1: Context Budget Fit (20%)

**Definition**: How well the goal fits the session's remaining capacity (context window, time, attention).

| ID | Criterion | Weight |
|----|-----------|--------|
| D1.1 | Goal completable in remaining context without compaction | High |
| D1.2 | Time estimate fits remaining session window | High |
| D1.3 | Attention cost proportionate to other queued work | Medium |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| L3: Comfortable fit | 3 | ≤50% of remaining capacity; no risk of mid-goal exhaustion |
| L2: Tight fit | 2 | 50-80% of remaining capacity; careful execution required |
| L1: Risky fit | 1 | 80-100%; may require compaction or extends to next session |
| L0: Overflow | 0 | Exceeds remaining capacity; should be deferred |

---

### D2: Evidence Decay Risk (20%)

**Definition**: How much goal value is lost if deferred to a later session. Evidence can decay via context loss, pattern fade, or situation change.

| ID | Criterion | Weight |
|----|-----------|--------|
| D2.1 | Novel evidence generated this session unavailable later | High |
| D2.2 | Pattern freshness degrades without immediate capture | High |
| D2.3 | External state may change (e.g., supervisor session ends) | Medium |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| L3: High decay | 3 | Live pattern instances this session; capture now or lose; time-boxed external window closing |
| L2: Moderate decay | 2 | Context-rich but reconstructable from transcript; cross-session recoverable with effort |
| L1: Low decay | 1 | Evidence durable across sessions; no urgent capture pressure |
| L0: No decay | 0 | Backlog item; can be done any session without value loss |

---

### D3: Scope Alignment (20%)

**Definition**: Match between the goal and what the session was chartered to do (principal's ask, session mandate, current focus area). Inspired by the SA dimension surfaced in prior rubric critique.

| ID | Criterion | Weight |
|----|-----------|--------|
| D3.1 | Goal directly answers the principal's current ask | High |
| D3.2 | Goal stays within declared session focus area | High |
| D3.3 | Goal does not open new unrelated scope | Medium |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| L3: On-mandate | 3 | Directly answers principal's current ask; zero new scope |
| L2: Adjacent | 2 | Related to session focus; small scope extension with clear justification |
| L1: Orthogonal | 1 | Legitimate work but outside current session charter |
| L0: Off-scope | 0 | Unrelated to session mandate; should be a different session |

---

### D4: Blast Radius / Reversibility (20%)

**Definition**: Breadth of impact if the goal produces wrong output + cost to undo. High-impact-low-reversibility is the worst case.

| ID | Criterion | Weight |
|----|-----------|--------|
| D4.1 | Failure scope bounded (local vs. cross-agent vs. public) | High |
| D4.2 | Reversibility mechanism exists (commit undo, issue close, delete) | High |
| D4.3 | Failure detection is possible without external escalation | Medium |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| L3: Local + reversible | 3 | All artifacts are local edits; commit-level undo; no external state affected |
| L2: Private + reversible | 2 | Private repos (e.g., issue filings to gmelli/aget-aget); reversible via close/delete |
| L1: Public or hard-to-reverse | 1 | Public repos, fleet-wide effects, or state changes requiring cross-agent coordination to undo |
| L0: Irreversible | 0 | Published releases, announcements, irretrievable commits, or permanent state changes |

---

### D5: Unblocking Value (20%)

**Definition**: Degree to which success unlocks other queued work. A goal with high unblocking value delivers leveraged return.

| ID | Criterion | Weight |
|----|-----------|--------|
| D5.1 | Completion unblocks named queued work | High |
| D5.2 | Unlocked work is itself high-value | Medium |
| D5.3 | Goal itself is on a blocking path (other work waits for it) | Medium |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| L3: High unblocking | 3 | Directly unblocks ≥2 named queued items; critical-path goal |
| L2: Moderate unblocking | 2 | Unblocks 1 named item, or unblocks generalizable work |
| L1: Parallel | 1 | Independent of other queued work; neither blocks nor unblocks |
| L0: Self-contained | 0 | One-off; completion affects only this goal's artifact |

---

## Beneficiary Tag (not scored)

Attach one of the following to each candidate goal for grouping:

| Tag | Meaning |
|-----|---------|
| `principal` | Direct principal-facing deliverable (`aget:concept/Principal`, C001) |
| `supervisor` | Unblocks or serves another agent session |
| `framework-production` | Framework artifact output (specs, skills, templates) |
| `framework-learning` | Knowledge capture (L-docs, rubrics, patterns) |
| `ecosystem` | Public-facing or cross-fleet impact |

**Ontology grounding (E4)**: of the five tags, only `principal` has a live SKOS concept (`aget:concept/Principal`, C001 — `/aget-ground-artifact` over 762 concepts). The other four are candidate concepts (no current prefLabel) — grounding awaits concept creation via `/aget-expand-ontology`, not fabricated bindings.

## Commitment-Type Tag (not scored — E7)

Attach one of the following to each candidate, **orthogonal to the score** (a high-scoring goal can still be aspirational). Folded from the sibling `SOP_near_term_ambition_projection` (L1090 — SOP and skill are one intent at two altitudes); the OKR honesty axis carries as `committed` vs `aspirational`.

| Tag | Meaning |
|-----|---------|
| `committed` | Prepared to spend this session's capacity now; has (or needs no) a governed vehicle and a clear done-state. |
| `aspirational` | A want worth surfacing, but not yet bettable this session — under-shaped, dependency-blocked, or capacity-deferred. |

**Honesty constraint (C6)**: an `aspirational` goal MUST NOT be presented as `committed`. The tag is independent of the /15 score — value (D2/D5) high + no governed vehicle = aspirational, not committed.

**Shape-it gate (C7 — E8, imports L174)**: if the highest-scoring candidate is `aspirational` or lacks a governed vehicle, the proposed next action is a **shape-it** action (`/aget-propose-project` / `/aget-propose-initiative`), never direct execution. The most ambitious-sounding candidate is often the least shaped — shaping *is* the progress (L174 ambition–governance inversion).

## Formula

```
Goal Score = D1 + D2 + D3 + D4 + D5
```

Range: 0-15. All dimensions equal-weighted pending calibration.

**Decision threshold**: In a divergent-proposal set, the highest-scoring goal becomes the proposed pivot target. Ties break by principal preference or by beneficiary tag priority (currently unset — candidate future calibration).

---

## Reflexive Validation (L839 pattern)

Test: score this session's G1/G2/G3 candidates. If the rubric cannot discriminate, it's poorly designed.

### G1 — Mediate cross-session coordination (notify supervisor of SP-016 + #1012)

| Dim | Score | Rationale |
|-----|:-----:|-----------|
| D1 Context | 3 | 5-10 min action; low burn |
| D2 Decay | 2 | Supervisor session at 11% is a closing window; not immediate but narrow |
| D3 Scope | 2 | Adjacent — session mandate was roadmap enhancements; supervisor relay is sibling work |
| D4 Blast | 2 | Issue filing is external (private repo); reversible via close |
| D5 Unblock | 3 | Directly resolves supervisor's deadlock on both open questions |
| **Total** | **12** | Beneficiary: `supervisor` |

### G2 — Continue framework production (Cycle 2 propose-actions backlog)

| Dim | Score | Rationale |
|-----|:-----:|-----------|
| D1 Context | 1 | 8-issue cluster resolution is heavy; 30+ min + external interactions |
| D2 Decay | 1 | Backlog items persist across sessions; no urgency |
| D3 Scope | 3 | Exactly what this session has been doing |
| D4 Blast | 2 | Mix of local VERSION_SCOPE + external consolidation issue; recoverable |
| D5 Unblock | 3 | P2.23a consolidation unblocks 8 named issues |
| **Total** | **10** | Beneficiary: `framework-production` |

### G3 — Harvest meta-learnings (Cycle 3: goal-selection + action-selection rubrics)

| Dim | Score | Rationale |
|-----|:-----:|-----------|
| D1 Context | 3 | L-docs + rubric fit ~30 min cleanly |
| D2 Decay | 3 | Live instances today (dual-session, A4 catch); capture now or lose |
| D3 Scope | 2 | Not the original mandate but aligns with "be diligent" capture principle |
| D4 Blast | 3 | All local L-doc + rubric writes; commit-reversible |
| D5 Unblock | 2 | Rubrics are reusable infrastructure; don't unblock specific queued items |
| **Total** | **13** | Beneficiary: `framework-learning` |

### Validation Result

**Ranking**: G3 (13) > G1 (12) > G2 (10). Discriminates cleanly; no ties.

**Principal's actual choice**: G3 (this session's execution path). Rubric validates principal's intuition without having to reconstruct it.

**Edge observation**: G2's low D1 (context) score dominates its decision. The rubric correctly surfaces that "right work, wrong time" is a frequent session-pivot failure mode — matches L131 (Stopping Point Bypass) reasoning.

## Anti-Patterns Guarded

| Anti-Pattern | Detection |
|--------------|-----------|
| **Decorative rubric** (L671) | Score must be recorded in session file; retrospectives check for rubric-free pivots |
| **Scope creep via strong evidence** (SA dimension origin) | D3 Scope Alignment prevents high-EV off-mandate goals from outranking on-mandate work |
| **Context-blind ambition** (L131 Stopping Point Bypass) | D1 Context Budget Fit must score ≥1; L0 force-defers |
| **Single-dimension dominance** | All 5 dimensions scored; no subset can drive decision alone |

## Traceability

| Link | Reference |
|------|-----------|
| Parent L-doc | L845 (Session-Pivot Goal-Selection Rubric Gap) |
| Companion gap | L846 (Action-Within-Session Rubric Gap — pending) |
| Sibling ex-ante rubric | `RUBRIC_scope_item_priority` (release-layer) |
| Sibling post-hoc rubric | `RUBRIC_session_outcome_value` (same layer, opposite timing) |
| Precedent rubric gaps | L709 (project plan), L744 (skill service boundary) |
| Reflexive test pattern | L839 (reflexive expansion validation) |
| Integrating skill (proposed) | `/aget-propose-goals` (SP-NNN, pending this session) |
| Governing paradigm | L677 (divergent-proposal mode), L808 (single-principal) |

---

*RUBRIC_goal_selection v1.0 — first draft. Reflexively validated on this session's G1/G2/G3. Calibration pending after N≥5 scored session pivots.*
