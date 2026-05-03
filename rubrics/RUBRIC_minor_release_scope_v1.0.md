# Minor Release Scope Estimation Rubric

**Version**: 1.0.0
**Created**: 2026-05-02
**Updated**: 2026-05-02 (initial; v3.16.0 cycle as N=1 evidence)
**Author**: private-aget-framework-AGET v3.16.0
**Domain**: Pre-release scope sizing for MINOR cycles (vX.Y.0)
**Status**: Active (single-cycle calibration; rolling 4-cycle baseline targeted by v3.20)
**Governing Spec**: `aget/specs/AGET_RELEASE_SPEC.md` CAP-REL-012 (VERSION_SCOPE Requirement); `governance/POLICY_release_cadence.md` POL-REL-001 R-REL-CAD-006

## Purpose

Replace the prior informal "1 SU = 1 hour" rule, which v3.16.0 retrospective confirmed over-estimated spec-authoring work by 6-12x (cycle elapsed ~9.5h vs estimate 28-36h; F-CRITIC-REL-040). This rubric provides per-item-type effective-hour baselines so VERSION_SCOPE Tier 1 sizing matches actual cycle capacity.

**Decisions this rubric supports**:
1. **Pre-cycle scope-lock** (primary): What item count fits a Saturday cycle? — author grades VERSION_SCOPE candidate list before scope-lock.
2. **Mid-cycle re-scope** (secondary): When velocity outpaces estimate, how much Tier 2 can absorb?
3. **Post-cycle calibration** (tertiary): Update baselines from actuals; quarterly rubric refresh.

**NOT in scope**: MAJOR (vX.0) sizing — MAJORs ship 2-3 times/year per POL-REL-001 R-REL-CAD-006; insufficient evidence (zero MAJORs under current process); defer rubric until 1-2 MAJORs ship.

## Per-Item-Type Effective-Hour Baseline

| Item type | Effective hours | Confidence | v3.16 evidence |
|-----------|----------------:|:----------:|----------------|
| Spec amendment (text-only, single CAP) | **0.2-0.3** | high | G1.1, G1.2, G1.3, G1.5 (4 instances; 5-30 min actual range) |
| Spec amendment (multi-CAP, ≤5 CAPs) | **0.5-0.8** | medium | G1.6 (4 CAPs in ~30 min) |
| Skill spec promotion (proposed → production + body + integration) | **0.7-1.0** | low | G1.7 (~50 min single instance) |
| New skeleton + governing CAP | **0.3-0.5** | low | G1.4 (.agetignore + CAP-SEC-007 in ~15 min) |
| Multi-template fanout (validator-driven, 10-15 templates) | **0.5-1.0** | low | G1.8 (150 dirs in ~30 min) |
| Authoring (CHANGELOG × N + release notes) | **0.5-0.7** | medium | G3 (14 CHANGELOGs + release notes in ~35 min); v3.15 ~consistent |
| Mechanical (version bumps + tags × 14) | **0.3-0.4** | medium | G2 (~15 min); G5/Phase 6.4.5.1 (~5 min) |
| Network-bound (push N repos + GH releases) | **0.3-0.5** | low | G6/Phase 6.4.5.2-3 (~15 min single cycle) |
| Coherence audit + test runs | **0.2-0.3** | low | G4 (~10 min) |
| Distributed Triad invocation (Auditor or Critic subagent) | **0.1-0.2** | medium | 3 invocations this cycle (Gate 1 entry, defects audit, mid-cycle pulse) |
| Defects-audit overhead (when Triad surfaces material findings) | **1.5-2.5** | low | v3.16 Gate 1 defects audit (~2h for 7 closures) |

**Source-rule**: Effective hours = realistic actuals from cycle execution, NOT idealized authoring time and NOT inflated SU. Baseline assumes Claude+spec authoring; principal-only authoring tracks ~3-5x slower.

## Cycle Capacity Model

| Component | Hours |
|-----------|------:|
| Single focused Saturday session | 4-6 working |
| Per gating-Triad invocation overhead | +0.1-0.2 each |
| Reserve for principal corrections / mid-cycle re-scope | -1.0 to -2.0 |
| **Net per-cycle deliverable capacity** | **3-5h actual work** |

**Cadence note**: Weekly Saturday cadence per POL-REL-001 R-REL-CAD-001. Cycles that complete <50% of Tier 1 in this window indicate over-scope; recalibrate at next scope-lock per L894.

## Tier Sizing Heuristic

Per **net deliverable capacity** above, recommended Tier sizing:

| Tier | Item count (text-only spec mix) | Item count (mixed spec + skill + multi-template) | Notes |
|------|---------------------------------|--------------------------------------------------|-------|
| **Tier 1 (MUST-SHIP)** | 8-12 items | 6-10 items | Sized at capacity floor; honor without demotion |
| **Tier 2 (SHOULD)** | additional 4-6 | additional 3-5 | Absorb if velocity holds; demote-to-T3 at G1 mid-gate if pace falters |
| **Tier 3 (STRETCH)** | additional 2-4 | additional 2-3 | Only if Tier 1 lands ≤50% capacity (i.e., ≤2.5h actual) |

**Total cycle scope** (T1+T2+T3 stretch): **14-22 items** for text-only minor; **11-18 items** for mixed minor.

**Compare**: v3.16.0 shipped Tier 1 = 8 items in ~3h (post-defects-audit). At new rubric, this would have allowed Tier 1 = 12-15 + Tier 2 = 4-6 stretched. Conservative-by-3-4x in actual.

## Calibration Discipline

**Per-cycle**: After Gate 8 retrospective, append per-item-type actuals to `private-aget-framework-AGET/workspace/cycle_actuals.md` (private; effort estimates carry process metadata). Format: `cycle / item-type / planned-SU / actual-hours / notes`.

**Quarterly**: Review rolling 4-cycle baseline; update this rubric's Per-Item-Type table; bump version. Promote to v1.1 when N≥4 cycles per item-type.

**WARN signals** (raise at scope-lock):
- Estimated cycle > 1.5x last cycle's actual → likely estimate inflation; recalibrate before lock
- Tier 1 sizing > 1.2x rolling-average capacity → likely over-scope; demote candidates pre-lock
- Single item-type estimate > 2x rubric baseline without justification → likely category mis-classification; re-categorize

## What This Rubric Does NOT Cover

| Out-of-scope | Why deferred | Tracking |
|--------------|--------------|----------|
| MAJOR (vX.0) scope sizing | Zero MAJOR evidence under current process; v4.x will be first | POL-REL-001 R-REL-CAD-006 + future RUBRIC_major_release_scope after 1-2 MAJORs ship |
| BC item ceremony cost (ADR ratification + test cohort + supervisor BC pre-flight) | BC items batched into MAJORs (R-REL-CAD-006); separate from MINOR scope | RUBRIC_major_release_scope (future) |
| Cross-fleet propagation cost (template feature propagation per #1195) | Process maturity dimension; covered by upcoming v3.17 Feature Propagation Verifier (gmelli/aget-aget#1195) | #1195 + v3.17 P1 |
| Spec-amendment-conformance V-test overhead | Process maturity dimension; covered by v3.17 P1 spec-amendment-conformance V-test | v3.17 P1 (L807 cluster fix) |

## Anti-Patterns This Rubric Prevents

| Anti-pattern | Consequence at v3.X | Closure mechanism |
|--------------|---------------------|-------------------|
| 1 SU = 1 hour informal rule | v3.16 sized 28-36h cycle for ~9.5h actual work; defects-audit eat slack budget that didn't exist | Per-item-type baseline + WARN signals |
| Estimate-anchoring (locked scope ≠ revised when velocity outpaces) | Tier 1 honored but Tier 2 untouched despite ~22h unused capacity | Mid-cycle re-scope guidance + L894 recurrence-check |
| Conservative-by-default Tier 1 sizing | Smaller releases than capacity allows; reduces cumulative throughput | Tier sizing heuristic anchored at capacity floor (8-12), not safety floor (4-6) |
| MAJOR-vs-MINOR scope confusion | BC items spread across MINORs with grace periods (ceremony amortization fails) | Out-of-scope row routes BC items to MAJOR cycle |

## References

- L894 (plan-driven discipline) — recurrence-check the estimate-anchoring pattern
- F-CRITIC-REL-040 (velocity-as-evidence inversion) — v3.16.0 cycle calibration evidence
- POL-REL-001 R-REL-CAD-006 (Major Cadence) — MAJOR rhythm complement to this rubric
- v3.16.0 PROJECT_PLAN_release retrospective Velocity Analysis table (private)
- AGET_RELEASE_SPEC CAP-REL-012 (VERSION_SCOPE Requirement) — governing spec layer
- L749 Requirements-Rubric Duality — every estimation requirement implies an estimation rubric (this artifact)

---

*RUBRIC_minor_release_scope_v1.0 — initial calibration from v3.16.0 cycle (N=1). Refresh quarterly with rolling 4-cycle baseline.*
