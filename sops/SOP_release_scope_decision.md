# SOP: Release Scope Decision

**Version**: 1.0.0
**Created**: 2026-02-28
**Owner**: private-aget-framework-AGET
**Related**: L465, L553, L591, L605, L621, AGET_SOP_SPEC v1.1.0
**Implements**: R-REL-013 (scope consolidation), R-RES-001-17 (triage handoff)
**Pain Point**: L465 (scope consolidation gap), L621 (distributed scope decisions), L605 (post-release remediation)
**See**: AGET_SOP_SPEC v1.1.0 (CAP-SOP-001 through CAP-SOP-005)
**Tests**: tests/test_sop_compliance.py
**Patterns**: L353 (efficiency scaling), L392 (pilot-driven), L591 (scope vs debt)

---

## Purpose

Govern VERSION_SCOPE lifecycle from initialization through post-release logging. Scope decisions in AGET are distributed priority assignments across multiple VERSION_SCOPE revisions — not a single "freeze" point (L621). This SOP formalizes the priority criteria, deferral management, expansion control, and decision logging that enable structured scope governance.

---

## Scope

### When This SOP Applies

- Before every MINOR or MAJOR Framework_Release
- When VERSION_SCOPE transitions from DRAFT to READY FOR RELEASE
- When items are added to or removed from VERSION_SCOPE during execution

### When This SOP Does Not Apply

- PATCH releases (bug fixes only, no scope decision needed)
- Agent_Sop changes (instance-level, not framework-scoped)
- Individual PROJECT_PLAN gate decisions (covered by gate execution discipline, L001)

---

## Vocabulary

| Term | Definition |
|------|------------|
| Scope_Lock | Decision_Point where VERSION_SCOPE transitions from mutable DRAFT to immutable ship list; no new P1/P2 additions permitted after lock |
| Deferral_Debt | Accumulation of items deferred across multiple releases without reassessment or closure |
| Scope_Expansion_Budget | Mechanism limiting mid-cycle scope additions; new P2 items require equal deferrals |
| Remediation_Buffer | Effort reserve (10-15% of P1+P2 count) for post-release fixes based on historical rates |
| Decision_Log | Structured JSONL file recording every scope decision in real-time |

---

## Phases

### Phase 0: Scope_Initialization

**Trigger**: New version proposed.
**Output**: VERSION_SCOPE document (DRAFT) + empty Decision_Log.

**Steps**:

1. Create VERSION_SCOPE document from template
2. Seed with:
   - Deferred items from prior release
   - New proposals from PROJECT_PLANs, L-docs, user directives
   - Backlog items flagged for reassessment
3. Initialize Decision_Log: `planning/SCOPE_DECISION_LOG_v{VERSION}.jsonl`
4. Apply Deferral_Staleness pre-check to seeded deferrals (identify items at ≥2 consecutive deferrals)
5. Log each seeded item as an ADD entry in Decision_Log

**Integration**: Follows SOP_release_process.md R-REL-013 (Scope_Consolidation).

---

### Phase 1: Priority_Classification

**Trigger**: Items entered into scope.
**Output**: Each item has P1/P2/P3 assignment.

**Priority Rubric**:

| Priority | Label | Ship Expectation | Criteria (meet ANY) |
|----------|-------|:----------------:|---------------------|
| **P1** | Must_Ship | ~100% | Blocks release quality; fixes user-reported issue; breaks existing functionality if not addressed; addresses High-severity L-doc; Principal directive |
| **P2** | Should_Ship | ~80% | Improves capability or quality; addresses known gap with spec basis; manageable effort (≤1 session); has fleet evidence of need |
| **P3** | Aspirational | ~0% | No blocking dependency; can defer without consequence; exploratory or speculative; effort unknown or large |

**Decision Tree**:

```
Is this item required for release integrity?
├── YES → P1
└── NO
    ├── Does it have spec basis AND manageable effort?
    │   ├── YES → P2
    │   └── NO
    │       ├── Is effort known and bounded?
    │       │   ├── YES → P2
    │       │   └── NO → P3
    │       └── Is it speculative/exploratory?
    │           └── YES → P3
    └── Is it a Principal directive?
        └── YES → P1 (unless Principal specifies lower)
```

**Priority Change Protocol**:

| Change | Requires | Log Action |
|--------|----------|------------|
| P3 → P2 | Evidence of need (L-doc, fleet data, user request) | PROMOTE |
| P2 → P1 | Blocking dependency identified or Principal directive | PROMOTE |
| P1 → P2 | Mitigation found; Principal_Approval | DEMOTE |
| P2 → P3 | Effort exceeds estimate by 2x+ or dependency removed | DEMOTE |

Log each classification as a Decision_Log entry.

**Integration**: Receives triaged items from SOP_pre_release_research.md Phase 3 (R-RES-001-17).

---

### Phase 2: Value_Cost_Assessment

**Trigger**: All P1/P2 items classified.
**Output**: Release-level value-cost score.

**Scoring Dimensions**:

| Dimension | Weight | Scale |
|-----------|:------:|:-----:|
| **Value** | | |
| New capabilities | 25% | 0-10 |
| Bug fixes | 15% | 0-10 |
| Quality improvements | 15% | 0-10 |
| Developer experience | 10% | 0-10 |
| **Cost** | | |
| Breaking changes | -20% | 0-10 |
| New dependencies | -5% | 0-10 |
| Process changes | -5% | 0-10 |
| Migration effort | -5% | 0-10 |

**Score = (Capabilities x 0.25) + (BugFixes x 0.15) + (Quality x 0.15) + (DevEx x 0.10) - (Breaking x 0.20) - (Dependencies x 0.05) - (ProcessChanges x 0.05) - (Migration x 0.05)**

**Classification Bands**:

| Score | Classification | Recommendation |
|:-----:|---------------|----------------|
| 8-10 | High_Value | Strong push to fleet |
| 5-7 | Moderate_Value | Standard rollout |
| 3-4 | Low_Value | Consider bundling with next release |
| 1-2 | Governance_Only | Defer or bundle |

**Minimum Thresholds**:

| Release Type | Minimum Score |
|:------------:|:------------:|
| MAJOR | 7.0 |
| MINOR | 5.0 |
| PATCH | 3.0 |

If score is below threshold: consider bundling items with next release or adding value items to raise score.

Log assessment as a SCORE entry in Decision_Log.

---

### Phase 3: Scope_Evolution

**Trigger**: Ongoing during release execution.
**Output**: Decision_Log entries for each scope change.

This phase runs concurrently with release execution. Every scope change requires a Decision_Log entry.

**Scope_Expansion_Budget**:

| Addition Type | Budget Constraint |
|---------------|-------------------|
| New P1 | No deferral required — but requires Principal_Approval + Decision_Log entry |
| New P2 | Defer 1 existing P2 or P3 to maintain net scope |
| New P3 | No constraint (backlog only, won't ship) |

**Expansion Cap**: Total mid-cycle P1+P2 additions SHALL NOT exceed 25% of original P1+P2 count without Principal_Approval.

Example: 20 original P1+P2 items → max 5 mid-cycle additions before escalation.

**Tracking**: Each mid-cycle addition logged with original scope count, current addition count, remaining budget, and deferrals triggered.

---

### Phase 4: Deferral_Debt_Resolution

**Trigger**: Before Scope_Lock.
**Output**: All stale items reassessed or closed.

**Deferral_Staleness_Rule**: Items deferred ≥2 consecutive releases SHALL be reassessed.

| Deferrals | Classification | Required Action |
|:---------:|---------------|-----------------|
| 1 | Fresh | No action — normal deferral |
| 2 | Stale | Reassess: re-justify with updated evidence, or close |
| 3+ | Chronic | Reassess with escalation: why hasn't this shipped or been closed? |

**Reassessment Outcomes**:

| Outcome | Criteria | Log Action |
|---------|----------|------------|
| Re-justify | Still relevant; updated evidence; re-prioritized | REASSESS |
| Close | No longer relevant; superseded; no evidence of need | CLOSE |
| Merge | Absorbed into a broader item | MERGE |

**Bulk Resolution**: When backlog exceeds 20 stale items, apply batch triage — group by category, apply priority rubric, close groups with no P1/P2 items. Log batch decision with count and rationale.

---

### Phase 5: Scope_Lock

**Trigger**: Decision to finalize scope.
**Output**: VERSION_SCOPE transitions DRAFT → READY FOR RELEASE.

**Prerequisites**:
- [ ] All P1 items complete or have mitigation plan
- [ ] Phase 4 (Deferral_Debt_Resolution) complete
- [ ] Value-cost score meets minimum threshold (Phase 2)
- [ ] Remediation_Buffer budgeted (10-15% of P1+P2 count)

**After Scope_Lock**:

| Addition Type | Permitted? | Override |
|---------------|:----------:|----------|
| New P1 | No | Principal_Override only |
| New P2 | No | Principal_Override only |
| New P3 | Yes | Backlog; won't affect release |

Log Scope_Lock decision with rationale and final scope counts.

**Integration**: Scope_Lock enables SOP_release_process.md Phase 0 (Manager Migration).

---

### Phase 6: Post_Release_Logging

**Trigger**: After release ships.
**Output**: Ambition_Ratchet metrics recorded.

**Metrics**:

| # | Metric | Direction | Measurement |
|---|--------|:---------:|-------------|
| 1 | P1 ship rate | ↑ | Shipped P1 / Total P1 |
| 2 | P2 ship rate | ↑ | Shipped P2 / Total P2 |
| 3 | Post-release remediation items | ↓ | Count of items requiring post-release fix |
| 4 | Scope_Lock lead time (days) | ↑ | Days between Scope_Lock and release |
| 5 | Deferral_Debt count | ↓ | Items deferred ≥2 consecutive releases |
| 6 | Value-cost score | ↑ | Rubric output (Phase 2) |
| 7 | VERSION_SCOPE revision count | ↓ | Total revisions from DRAFT to RELEASED |

**Ambition_Ratchet**: Once a metric improves beyond baseline, the improved value becomes the new baseline. Regression beyond 15% of prior release requires a Decision_Log entry with explanation.

**Baseline** (v3.6.0):

| Metric | v3.6.0 Value |
|--------|:------------:|
| P1 ship rate | 100% (7/7) |
| P2 ship rate | 89% (8/9) |
| Remediation items | 3+ |
| Lock lead time | 0 days |
| Deferral_Debt | 4 (Part C) |
| Value-cost score | 6.3 (v3.5.0 only) |
| VS revisions | 8 |

Record metrics as a SCORE entry in Decision_Log. Compare against prior release. Flag regressions for next release planning.

---

## Remediation_Buffer

Reserve 10-15% of total P1+P2 item count as Remediation_Buffer. Start at 15% (conservative), ratchet down as remediation rate improves.

| Total P1+P2 | Buffer (15%) | Interpretation |
|:-----------:|:------------:|----------------|
| 10 | 2 | Reserve effort for 2 post-release fixes |
| 15 | 2-3 | Reserve effort for 2-3 post-release fixes |
| 20 | 3 | Reserve effort for 3 post-release fixes |

Buffer items are NOT pre-identified — they are effort reserves. After release, compare actual remediation against budget and feed into Ambition_Ratchet (metric #3).

---

## Minimum Viable Release Criteria

| # | Criterion | Blocking? |
|---|-----------|:---------:|
| 1 | All P1 items complete | Yes |
| 2 | P2 ship rate ≥70% | Yes |
| 3 | Value-cost score ≥ threshold (Phase 2) | Yes |
| 4 | Scope_Lock applied | Yes |
| 5 | Decision_Log complete (every item has final-state entry) | Yes |
| 6 | Contract tests pass | Yes |
| 7 | No Chronic deferral items unresolved (≥3 deferrals) | Advisory |
| 8 | Remediation_Buffer budgeted | Advisory |

If criteria 1-6 are not met, release CANNOT proceed.

---

## Principal Override Protocol

Per L591 (Scope Discipline vs Debt Tolerance): when Principal explicitly requests scope expansion or overrides scope discipline, acknowledge and execute.

**Override Types**:

| Scenario | Type |
|----------|------|
| Add P1/P2 after Scope_Lock | Lock_Override |
| Exceed Scope_Expansion_Budget | Budget_Override |
| Ship with incomplete P1 | Criteria_Override |
| Skip Value_Cost_Assessment | Process_Override |

**Protocol**:

1. **Acknowledge** the tradeoff explicitly
2. **Log** the override as an OVERRIDE entry in Decision_Log with full context
3. **Document** the debt accepted (if any)
4. **Execute** without further debate

---

## Decision_Log Format

**File**: `planning/SCOPE_DECISION_LOG_v{VERSION}.jsonl`

One JSON object per line. Required fields: `date`, `item`, `action`, `reason`, `session`.

**Actions**: ADD, DEFER, PROMOTE, DEMOTE, CLOSE, MERGE, REASSESS, LOCK, OVERRIDE, SCORE

**Schema**:

```json
{
  "date": "YYYY-MM-DD",
  "item": "P2.7",
  "action": "PROMOTE",
  "from_priority": "P3",
  "to_priority": "P2",
  "reason": "User directive: evidence-based positioning reframe",
  "evidence": "L610, fleet survey",
  "session": "session_2026-02-22_1400",
  "scope_count": {"p1": 8, "p2": 12, "p3": 5},
  "expansion_budget_remaining": 3
}
```

**Query Examples**:

```bash
# All decisions for a release
cat planning/SCOPE_DECISION_LOG_v3.8.0.jsonl | jq .

# Count by action type
cat planning/SCOPE_DECISION_LOG_v3.8.0.jsonl | jq -r '.action' | sort | uniq -c

# Items promoted during cycle
cat planning/SCOPE_DECISION_LOG_v3.8.0.jsonl | jq 'select(.action == "PROMOTE")'

# Scope count at lock point
cat planning/SCOPE_DECISION_LOG_v3.8.0.jsonl | jq 'select(.action == "LOCK") | .scope_count'

# Cross-release P2 ship rate comparison
for f in planning/SCOPE_DECISION_LOG_v*.jsonl; do
  echo -n "$(basename $f): "
  jq -r 'select(.action == "SCORE" and .item == "RELEASE") | .metrics.p2_ship_rate' "$f"
done
```

---

## Integration Points

| Integration | SOP | Direction |
|-------------|-----|-----------|
| Scope_Consolidation | SOP_release_process.md (R-REL-013) | This SOP runs AFTER R-REL-013 consolidation check |
| Issue triage | SOP_pre_release_research.md (Phase 3, R-RES-001-17) | Triaged items feed INTO this SOP's Phase 1 |
| Release execution | SOP_release_process.md (Phase 0) | Scope_Lock (Phase 5) enables release execution |

---

## Traceability

| Link | Reference |
|------|-----------|
| Spec | AGET_SOP_SPEC v1.1.0 (CAP-SOP-001 through CAP-SOP-005) |
| L-docs | L353, L392, L465, L553, L591, L605, L621 |
| ER absorbed | ER-release-value-cost-rubric (ENH-2026-01-18-002) |
| Design | findings/D_release_scope_decision_sop_design.md |
| Research | findings/R_release_scope_decision_patterns_2026.md |
| PROJECT_PLAN | PROJECT_PLAN_release_scope_decision_sop_v1.0.md |

---

*SOP_release_scope_decision.md v1.0.0*
*"Decide what ships with data, not instinct."*
