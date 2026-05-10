# RELEASE_HANDOFF_v3.17.0.md

**Version**: 3.17.0
**Released**: 2026-05-09 (Saturday) — 1 week early of 2026-05-16 primary target
**Theme**: **C3 — Canonical Coherence + Structural Self-Conformance**
**Breaking Changes**: NONE
**Framework Manager**: aget-framework-manager (archetype: framework-manager)

---

## Receiving Agent Governance Checklist (BLOCKING)

**STOP**: Before executing any upgrade steps, complete this checklist:

- [ ] Located local upgrade SOP (e.g., SOP_point_upgrade.md)
- [ ] Created PROJECT_PLAN for this upgrade OR referenced existing gate
- [ ] Gate discipline acknowledged (L42)
- [ ] Principal approval obtained if required by local governance

**Governance Reference**: _[Your upgrade SOP path]_

**Warning**: Proceeding without completing this checklist is a governance violation (L562).

---

## Release Summary

v3.17.0 ratifies Theme C3 (Canonical Coherence + Structural Self-Conformance) operationally. The framework was forced to pass its own audits at every gate boundary; the audits caught real drift (CITATION.cff 3-cycle stale; V-test scope incompleteness; script-spec self-divergence) that prior cycles had silently masked. v3.16's #1 lesson — V-tests verify correctness, not presence — extended to a SECOND axis: scope correctness (V-test must cover the actual canonical-artifact universe, not the assumed universe). Three in-cycle empirical recurrences ratify this lesson.

### Key Deliverables

- **Framework-manager archetype** (T1.7): Coined; closes self-classification gap surfaced via L908 self-application audit. 6-site multi-site equality propagation (identity.json + version.json + CHARTER + SCOPE_BOUNDARIES + AGENTS.md/CLAUDE.md + ontology C610). SKOS grounding via Stewardship Theory of Management.
- **Sibling-quadruple spec authoring**: T2.18 SOP_scope_lock_ceremony LANDED v1.0.0 (codifies the 4-gate ceremony executed at v3.16+v3.17 lock events; Theme C3 self-conformance); T2.19 AGET_SKILL_LIFECYCLE_SPEC LANDED v1.0.0 with full V-test authoring (7 CAPs + 14 R-IDs + 7 V-tests; rejected v3.16 SPEC-LANDED-IMPL-DEFERRED precedent path); T2.20 AGET_FLEET_UPGRADE_SPEC v0.1.0 DRAFT (calibrated demote per L103 risk-mitigation); T2.23 AGET_TASK_ROUTING_SPEC v0.1.0 DRAFT (calibrated demote).
- **CAP-REL-030 + CAP-REL-031 implementation closure** (T1.1 + T1.2): Closes v3.16 sleeping CAPs (post-release CHANGELOG validator + tag validator).
- **Substance-aware health check** (T1.8, gh#1211): Closes L656 check-by-shape vs check-by-substance gap.
- **SOP_release_process v1.32 → v1.45** (T1.5 + T1.6): H-RHSC-001 G3+G4 SOP wiring; V-G7.x broadened to multi-condition correctness.

### Gate Velocity (this release)

| Gate | Outcome | Real-time |
|------|---------|:---------:|
| Gate -1 (Spec verification + carry) | ✅ Complete | ~75 min |
| Gate 0 (Tier 1 scope re-check) | ✅ Complete | ~10 min |
| Gate 1 (Tier 1 Build 9/9) | ✅ Complete | ~135 min (across 3 prior batches + this batch) |
| Gate 1.5 (Tier 2 quadruple 4/4) | ✅ Complete | ~50 min |
| Gate 2 (Version bumps × 14) | ✅ Complete | ~25 min |
| Gate 3 (CHANGELOGs × 14 + notes + L909) | ✅ Complete | ~30 min |
| Gate 4 (Pre-release validators + coherence) | ✅ Complete | ~25 min |
| Gate 5 (Tag cut) | ✅ Complete | ~10 min |
| Gate 6 (Public push 14 repos + 14 tags + 14 releases) | ✅ Complete | ~10 min |

Cycle ~370 min total real-time across multiple sessions; final session (Gates 1.5 → 6) ~3.5h continuous.

---

## Sleeping Requirements Disclosure

This release ships ZERO new sleeping CAPs. Inherited from v3.16:
- **CAP-REL-030 + CAP-REL-031**: previously SPEC-LANDED-IMPLEMENTATION-DEFERRED — **NOW IMPLEMENTED** (T1.1 + T1.2 closures; closes v3.16 sleeping CAPs)
- **CAP-REL-032 + CAP-REL-033**: SPEC-LANDED-IMPLEMENTATION-DEFERRED → **GRACE-EXTENDED to v3.18.0** per Q1=B disposition; R-DEP-011 grace-period rationale recorded in `governance/POLICY_deprecation.md` Active Grace Extensions

T2.20 + T2.23 are at DRAFT rigor (not LANDED): canonical promotion + V-test authoring + ontology binding queued v3.18 P1 per L103 Premature Abstraction discipline (calibrated demote pattern; selective rigor).

T2.19 ships LANDED at full V-test rigor (Q-G1.5-2=B principal Decide rejected v3.16 SPEC-LANDED-IMPL-DEFERRED precedent path) — NO sleeping CAPs at V-test layer; state-machine diagram and ontology SKOS concept URI bindings deferred to v0.2 (sub-deliverables outside Q-G1.5-2=B scope).

---

## Upgrade Guide (for instances and templates)

### For Instance Agents (e.g., private-* agents)

1. **Pull canonical updates** from your archetype template (e.g., `template-supervisor-aget`, `template-developer-aget`).
2. **Bump `.aget/version.json` aget_version**: 3.16.0 → 3.17.0.
3. **Bump `AGENTS.md` `@aget-version`**: 3.16.0 → 3.17.0.
4. **Optional adoption**: if your agent is a framework-management agent, consider adopting `archetype: "framework-manager"` in `.aget/identity.json` (closes self-classification gap).
5. **Run health check**: `python3 scripts/health_check.py` — verify substance-aware evolution check passes (new in T1.8).
6. **Run pytest**: should pass at your agent's pre-migration baseline + any newly-bundled framework tests (post-test-registration parity per F-V317-G2-FIX-003 inline remediation). 160/160 is the framework-manager agent's count; your count varies by archetype role (e.g., supervisor adds session-specific tests; worker varies by domain). Treat the migration as PASS if pytest count matches your previous baseline plus any expected new tests, with no regressions — not by literal 160 match.

### For Templates (downstream of aget-framework)

1. Pull `template-<archetype>-aget` v3.17.0 from `aget-framework/template-<archetype>-aget`.
2. Sync framework artifacts per AGENTS.md template-sync section.
3. CAP-REL-032 + CAP-REL-033 grace-extended; no implementation required at v3.17.0.

### DEPLOYMENT_SPEC Note

**No `DEPLOYMENT_SPEC_v3.17.0.yaml` ships** — explicit policy per principal Decide (closure of cross-session-Critic findings F-R2-A + F-R2-B). v3.17.0 inherits v3.16.0's DEPLOYMENT_SPEC contract semantically (no breaking changes). Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z}.yaml` (currently `v3.16.0`) as the contractual artifact set. Formal `aget/specs/AGET_DEPLOYMENT_SPEC_FORMAT.md` standardization is routed to v3.18. See `aget/CHANGELOG.md` line 76 for full rationale. **This is intentional, not oversight** — do not file `where-is-DEPLOYMENT_SPEC` issues.

### Migration

**No breaking changes** in v3.17. Existing instances upgrade by version-bump only. The framework-manager archetype field addition is additive (existing `archetype` values continue to function).

### Per-Archetype Variation Disclosure

This release applies uniformly across all 13 archetype templates: **no per-archetype variation** in v3.17.0 deliverables. Each template (advisor, analyst, architect, consultant, developer, document-processor, executive, operator, researcher, reviewer, spec-engineer, supervisor, worker) gets the same boilerplate v3.17.0 CHANGELOG entry (Theme + Changed + Compatibility); each bumps version.json + AGENTS.md @aget-version uniformly. The framework-manager archetype is NEW and currently has no template (sole instance is the framework-management agent itself; template proposal queued v3.18).

---

## Fleet Action Required (Pilot Tracking)

| Pilot Agent | Status | Confirmed Date | Notes |
|-------------|:------:|:--------------:|-------|
| Framework manager agent (self) | ✅ Running v3.17.0 | 2026-05-09 | First confirmed deployment (framework-manager archetype self-deploy) |
| Supervisor agent (upstream) | ⏳ Pending | — | Supervisor coordinates fleet upgrade per FLEET-MIGRATION sequence |
| (additional pilot agents) | ⏳ Pending | — | Per supervisor disposition |

**L656 Loading Dock guard**: This handoff documents what landed; deployment verification confirms it is running. Self-deployment confirmed at framework-manager (this agent) post-Gate-6 push. Cross-fleet verification deferred to supervisor-coordinated pilot pass.

**Self-tick prevention (L656 + L908)**: Receiving agents SHALL NOT mark their own row ✅ on self-deploy alone. L656 requires cross-AGENT deployment evidence; self-confirmation instantiates the L908 self-application gap. v3.17.0 caught two paired same-week recurrences of this pattern: framework-manager scored PIR D6=2/3 with `self ✅` (corrected to 1/3 post-Critic; commit `ab12440`); a sibling fleet agent proposed migration-prep NBAs without proposing its own self-migration as NBA #0. Supervisor coordinates pilot pass and updates this table; receiving agents update only their own *handoff-consumed* + *upgrade-guide-executed* status, not pilot-confirmed deployment status.

---

## Theme C3 Lesson — V-test Scope-of-Validation as Second Axis of Correctness

v3.16 ratified: V-tests verify correctness, not presence.
v3.17 extends: V-test correctness has TWO axes —

1. **Assertion correctness** — defended by multi-condition equality, set-membership, cross-site equality. v3.16's #1 lesson.
2. **Scope correctness** — defended by Critic review of declared scope vs canonical-artifact universe. v3.17's ratification.

A V-test that asserts the right conditions across the wrong site set is still wrong.

Three in-cycle empirical recurrences in v3.17:
- **T1.7**: V-T1.7 v0 (4 declared sites) → V-T1.7-EXT (6 actual sites). Critic-at-exit caught L908 self-application gaps.
- **Gate 2**: V-2.1 declared 5 sites including AGENTS.md; aget/ canonical does not have AGENTS.md (script artifact_types listing showed only 3 sites). V-test corrected at execution.
- **Gate 4**: V-1.5.2 narrow regex (`V-test (deferred to v0.2)`) vs broader pattern (`deferred to v0.2`). Auditor caught at gate-4 mid-cycle pulse — recursive Theme C3 instance (V-test designed to catch scope-of-validation gaps had a scope-of-validation gap).

Candidate v3.18 L-doc: "V-test scope-of-validation as second axis of correctness" — now with 3 in-cycle empirical recurrences as grounding.

---

## v3.18 Retro Candidates Accumulated

| # | Candidate | Class | Source |
|---|-----------|-------|--------|
| 1 | CAP-VTEST-006 URI-resolution-validity V-test pattern | Spec amendment | Gate 1 Critic-at-exit ROUTE-V3.18 |
| 2 | SOP_skill_promotion test-registration parity (SKILL_SPEC_MAP + SINGLE_VERB_EXCEPTIONS + private spec file copy) | SOP amendment | F-V317-G2-FIX-003 root cause |
| 3 | Cross-spec coherence Critic across the T2.18-23 cluster | Process amendment | F-V317-G15-CRITIC-007 |
| 4 | tag_release.py --push-only should push BOTH tags AND main branch | Script amendment | F-V317-G6-FIX-001 |
| 5 | SOP_release_process Phase 6.3.1 retroactive sanitization for historical CHANGELOG entries | SOP amendment | F-V317-G3-FIX-002 (a private upstream-agent leak in v3.0 entry surviving 6 cycles) |
| 6 | Ontology header concept count + validation.conceptCount stale (recurring 8+ FWRK iterations) | Ontology hygiene | F-A5-002 + Gate 1.5 G1.5.3 changelog entry |
| 7 | aget-go.yaml proposed/ duplicate cleanup | Housekeeping | F-G4-AUDIT-003 |
| 8 | L-doc: "V-test scope-of-validation as second axis of correctness" | New L-doc | 3 in-cycle empirical recurrences |
| 9 | Plan_Updated freshness vs amendment-log freshness (CAP-PP-003 sibling gap) | Spec amendment | F-G4-AUDIT-004 |
| 10 | T2.20 AGET_FLEET_UPGRADE_SPEC LANDED rigor + V-test authoring + canonical promotion | Spec promotion | Q-G1.5-1=A demote |
| 11 | T2.23 AGET_TASK_ROUTING_SPEC LANDED rigor + V-test authoring + canonical promotion + operational tool | Spec promotion | Q-G1.5-1=A demote |

---

## Acknowledgment

v3.17 closes substantial framework-discipline scope (Tier 1 9/9 + Tier 2 4/4) within the Saturday push window per L735 — 1 week early of the primary target (2026-05-16 → 2026-05-09 actual). The cycle proved Theme C3 is operational, not aspirational — the framework was forced to pass its own audits at every gate, and the audits caught real drift that prior cycles had silently masked.

The Q-G1.5-2=B principal decision to reject the v3.16 SPEC-LANDED-IMPL-DEFERRED precedent for T2.19 is significant: the framework now has a fully-authored spec for its own skill governance, with V-tests, on-disk, in the cycle that landed it. NO sleeping CAPs at V-test layer in T2.19. This is what calibrated rigor looks like.

The empirical pattern observation about /aget-propose-actions vs linear /aget-go (recorded mid-cycle) was itself a Theme C3 moment: the framework's own tools have appropriate-use phase boundaries, and using a tool outside its appropriate phase is a coherence drift.

---

## Deprecations (continuing; removal targets per POL-DEP-001)

| Item | Deprecated | Replacement | Removal Target | Status |
|------|------------|-------------|:--------------:|:------:|
| `wake_up.py` (top-level shim) | v3.10 | `scripts/wake_up.py` (canonical) → use canonical path | v3.18.0 (extended from v3.17.0 per Q9=B) | Active grace |
| `wind_down.py` (top-level shim) | v3.10 | `scripts/wind_down.py` (canonical) → use canonical path | v3.18.0 (extended from v3.17.0 per Q9=B) | Active grace |
| `wake_up_ext.py` (top-level shim) | v3.11 | `scripts/wake_up_ext.py` (canonical) → use canonical path | v3.18.0 (extended from v3.17.0 per Q9=B) | Active grace |
| `wind_down_ext.py` (top-level shim) | v3.11 | `scripts/wind_down_ext.py` (canonical) → use canonical path | v3.18.0 (extended from v3.17.0 per Q9=B) | Active grace |
| CAP-REL-032 (Post-Release Badge/Parity Validator) | v3.16 SPEC-LANDED-IMPL-DEFERRED | (no-replacement; impl pending) → IMPLEMENTATION queued v3.18.0 | v3.18.0 (Q1=B GRACE-EXTEND; R-DEP-011 rationale) | Active grace |
| CAP-REL-033 (Post-Release Contract-Test Validator) | v3.16 SPEC-LANDED-IMPL-DEFERRED | (no-replacement; impl pending) → IMPLEMENTATION queued v3.18.0 | v3.18.0 (Q1=B GRACE-EXTEND; R-DEP-011 rationale) | Active grace |

---

## References

| Resource | Location |
|----------|----------|
| Public release tag | github.com/aget-framework/aget releases/tag/v3.17.0 |
| 13 template releases | github.com/aget-framework/template-{archetype}-aget releases/tag/v3.17.0 |
| Deep release notes | release-notes/v3.17.0.md (~16KB; private repo authoritative; canonical via GitHub Releases) |
| Public CHANGELOG | aget/CHANGELOG.md (canonical; commit bb2f688) |
| AGET_SKILL_LIFECYCLE_SPEC | aget/specs/drafts/AGET_SKILL_LIFECYCLE_SPEC_v0.1.md (canonical promotion v3.18) |
| SOP_scope_lock_ceremony | aget/sops/SOP_scope_lock_ceremony.md v1.0.0 LANDED |
| Spec-fault carry | gh#1179 (R-REL-022-01 enum) + gh#1180 (V-PP-007 enum) — OPEN; L708 annotation per v3.16 precedent |

---

**Self-containment**: This handoff is self-contained per AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v0.1.0 (8 CAPs / 11 R-RHSC sub-requirements). Receiving agents have all information needed to upgrade without consulting external sources beyond the cited references.
