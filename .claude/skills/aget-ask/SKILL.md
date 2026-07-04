# aget-ask

Ask clarifying questions as a measurement instrument for next-action prediction. Default: `--clarification`.

## Instructions

This skill formalizes **asking clarifying questions** as an entropy-reduction tool, not UX politeness. Quality is measured by pre/post confidence delta on the agent's top-1 interpretation of the principal's intent — not by thoroughness, count, or category coverage.

### Clarification Mode (default: `--clarification`)

Generate 2-4 clarifying questions that maximally narrow the prediction distribution over what the principal wants next.

**Execution**:

1. **Pre-ask measurement**: Record the agent's top-1 interpretation of the principal's intent + confidence (0.0-1.0).

2. **Entropy threshold check**: If confidence ≥ 0.70, proceed with best-guess + verify instead of asking. If < 0.70, continue.

3. **Generate candidates**: Produce 4-8 candidate questions covering:
   - Frame-choice (which model/framing applies)
   - Replace-or-layer (affects which existing artifacts get modified)
   - Scope boundary (what's in/out for this turn)
   - Decision type (commitment level)

4. **Filter decorative / context-answerable**:
   - Drop questions answerable from memory or KB context
   - Drop wordsmithing between near-equivalent options
   - Drop questions self-labeled "deferrable" in the draft

5. **Rank by load-bearing weight**: Estimate how much each question's answer would change the next action. Higher = ranked earlier.

6. **Cap at 2-4**: Top 2-4 questions only. If the problem genuinely needs 5+, the input had structural ambiguity — consider re-scoping the request instead of adding questions.

7. **Order strictly by descending load-bearing weight**, NOT by category altitude. If your draft contains phrases like "hiding at the bottom", "biggest shape-determining", or "flag for alignment" attached to a non-first question, reorder before presenting.

8. **Present**: Numbered questions with 2-3 concrete option examples per question to make answering cheap.

9. **Post-ask measurement**: After the principal responds, record the revised top-1 interpretation + confidence.

10. **Log** (default: local-only, `sessions/entropy_log/YYYY-MM-DD.jsonl`):
    ```json
    {"ts": "...", "agent": "...", "pre_top1": "...", "pre_conf": 0.68, "post_top1": "...", "post_conf": 0.92, "delta": 0.24, "count": 2}
    ```

**Output format**:

```
**Pre-ask top-1**: [agent's best guess at principal's intent]
**Confidence**: [0.00-1.00]

N questions, ranked by load-bearing weight:

**Q1 — [topic]** (highest load — changes [X])
- Option A: [concrete option]
- Option B: [concrete option]
- Option C: [concrete option]

**Q2 — [topic]**
- Option A: ...
- Option B: ...

**Omitted as decorative/deferrable**: [brief list] (L848 compliance)
```

### Followup Mode (`--followup`)

Invoke the L345 principal-probe pattern: "what else should we ask?"

Used after an initial exchange to surface tacit knowledge the principal may hold but not volunteer.

**Execution**:
1. Review the just-completed exchange
2. Identify under-covered dimensions: near-misses, decision rationale, edge cases, future concerns
3. Ask 1-2 questions that probe for knowledge likely-tacit (per L345 question categories)
4. Log same as clarification mode

**Output format**:
```
**Followup probes** (L345 pattern — surface tacit knowledge):

1. [probe question] — [why this dimension may be tacit]
2. [probe question] — [why this dimension may be tacit]
```

### Altitude Filter (`--altitude={requirement|verification}`)

A **cross-cutting filter** (not a mode) that frames questions at one of the two levels of the AGET two-level model (L742). It **composes** with `--clarification` and `--followup`, and never bypasses the 2-4 cap or the load-bearing ordering (constraint C6).

| Altitude | Level (L742) | Keeps | Suppresses |
|----------|--------------|-------|------------|
| `--altitude=requirement` | Requirements (human intent) | Questions clarifying WHAT the principal wants — need, goal, value, intent | Specification / mechanism / implementation questions |
| `--altitude=verification` | Specifications (enforceable contract) | Questions clarifying HOW completion is confirmed — acceptance criteria, test conditions, done-definition | Questions that re-open settled requirement intent |

Default (no `--altitude`): both altitudes eligible; rank purely by load-bearing weight.

**Examples**:
- `/aget-ask --altitude=requirement` on "make releases smoother" → asks *what "smoother" means to you* (fewer HOLDs? shorter gap? less ceremony?), not *which script to edit*.
- `/aget-ask --altitude=verification` on "graduate aget-ask" (intent settled) → asks *what proves it's done* (canonical present? templates ≥13? tests green?), not *whether to graduate*.

### Parameters

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `--clarification` | **Yes** | Generate entropy-reducing questions before an action |
| `--followup` | No | L345 principal-probe for tacit knowledge (post-exchange) |
| `--altitude={requirement\|verification}` | none | Cross-cutting filter — frame questions at the requirements or verification level (L742); composes with modes (C6) |
| `--count N` | 3 | Override count (range 2-4; emits warning at ≥5) |
| `--log` | true | Emit entropy-log entry for future #1019 rollup |

## Anti-Patterns (reject at draft time)

1. **Context-answerable** (#1020) — if KB recall would answer, don't ask
2. **Decorative** (#1020) — if the answer doesn't change the next action, drop
3. **Over-count** (#1020) — 6+ questions = friction; re-scope instead
4. **Too-late** (#1020) — asked after the action is already committed
5. **Buried load-bearing** (L848) — most-constraining question asked last
6. **Category fill-pressure** (L848) — empty slots in Gate-0/Architectural/Infrastructure altitudes exerting fill-pressure (L756 sister pattern)

## Error Handling

- If entropy-log directory is missing, create `sessions/entropy_log/` on first write
- If pre-ask confidence cannot be estimated, default to 0.5 and note in the log entry
- If ≥5 candidate questions pass the filter, emit warning and truncate to top 4 by load-bearing weight

## Implementation Notes

**Logging architecture (v1.0.0)**: Local JSONL logging only. The #1019 rollup-consumer schema is **formally PARKED** (Gate 0, 2026-07-03; #1019 verified OPEN at source) — the log contract is versioned with the skill and revisable when the consumer defines its input schema; graduation does not block on it. Principal may override logging path via `--log-path`. Original coupling debt per SP-018 Q2:B decision (2026-04-18).

**Dogfood provenance**: This SKILL.md's design was itself produced using the skill's principles (2026-04-18 session — SP-018 approval turn). Pre-ask top-1: "implement `/aget-ask` now"; confidence: 0.68; delta after principal Q1:A response: +0.32.

## Related

- #1020: Clarifying questions as a tool to optimize next-action prediction accuracy (primary spec target)
- #1019: Reward AGETs by prediction accuracy of principal's next action (quality-metric consumer)
- L848: Clarifying-Question Quality Is Entropy Reduction, Not Thoroughness
- L345: Interactive Handoff Pattern (followup probe origin)
- L831: Cross-Agent Question Convergence as Specification Signal
- L756: Format-Driven Confabulation (fill-pressure sister pattern)
- L693: 5-action default (count-cap analog for propose-actions)
- DESIGN_DIRECTION_clarifying_questions.md v0.1.0
- SP-018: PROPOSAL_aget-ask.md
- SKILL_VOCABULARY.md: verb #32 (`ask`), SKILL-045

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-018 (PROPOSAL_aget-ask.md) |
| Verb | `ask` — approved verb #32 (v3.14, principal-approved 2026-04-18) |
| SKILL ID | SKILL-045 (production spec — `.aget/specs/skills/SKILL-045_aget-ask.yaml` v1.0.0) |
| Category | Research |
| Consumes | #1020 (spec definition) |
| Feeds | #1019 (prediction-accuracy reward) |

---

*aget-ask v1.0.0*
*Category: Research*
*Default: --clarification (entropy-reduction question generation); --altitude filter composes (L742)*
