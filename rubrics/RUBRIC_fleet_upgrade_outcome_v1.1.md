# Fleet Upgrade Release Outcome Rubric

**Version**: 1.2.0
**Created**: 2026-04-26
**Updated**: 2026-04-26 (v1.1.0 — calibration from two scored instances)
**Author**: private-aget-framework-AGET v3.15.0
**Cross-Agent Source**: private-supervisor-AGET (v1.0.0 original, FLEET-UPG-013), private-legalon-supervisor-AGET (FLEET-UPG-014 calibration feedback, #1165)
**Domain**: Conformance — fleet upgrade release outcome (FLEET-UPG-NNN close-out)
**Status**: Active (two scored instances: 13/15 Exemplary, 10/15 Compliant)
**Governing Spec**: `aget/specs/AGET_RELEASE_SPEC.md` CAP-REL-016 R-REL-024-03

## Purpose

Evaluate the quality and completeness of a fleet upgrade release outcome. Closes the gap identified during FLEET-UPG-013 close-out (2026-04-26): the `RELEASE_HANDOFF.md` Completion Response section listed fields but none required a rubric-scored report, leaving "successful release" as a vibe, not a measurement. See #1149.

**Decisions this rubric supports**:
1. **Self-check** (primary): Is this release outcome rigorous enough to report as complete? — supervisor grades own output before final close-out commit.
2. **Principal meta-assessment** (secondary): Are release quality standards consistent across migrations?
3. **Framework signal**: Does this release generate upstream improvements that benefit future upgrades?

**Subjects evaluated**:
- FLEET-UPG-NNN PROJECT_PLAN (all gates completed)
- FLEET_STATE.yaml coherence post-upgrade
- DEPLOYMENT_SPEC published at governed path
- Residuals captured, filed, and tracked
- Upstream artifacts (L-docs, SOP updates, template updates, framework candidates)

**Out of scope**:
- Individual agent conformance (use `verify_deployment.py`)
- CI health per-agent (use `scripts/ci_health_check.py`)
- Session log quality

## Calibration History

| Instance | Score | Band | Scored By | Notes |
|----------|:-----:|------|-----------|-------|
| FLEET-UPG-013, v3.15.0 (main fleet, 34/34) | 13/15 | Exemplary | private-supervisor-AGET | D4=1/3: G3/G4 gate Status retroactive; motivates v3.16 structural enforcement candidates |
| FLEET-UPG-014, v3.15.0 (legalon fleet, 7/7) | 10/15 | Compliant | private-legalon-supervisor-AGET | D5=low: no fleet upgrade scripts/L-docs; drove format-agnostic calibration in v1.1 |

**Version history**:
- v1.0.0 (2026-04-26): Initial draft; first scored instance FLEET-UPG-013. Draft status pending calibration.
- v1.1.0 (2026-04-26): Active status after second scored instance. Five calibration fixes applied (C-A timing, C-D format-agnostic, D3.3 L100 vocabulary, D4.1 format-agnostic, D4.3 clarification). FLEET-UPG-NNN namespacing note added.
- v1.2.0 (2026-05-30): C-A made conditional on `breaking_release` (#1517 D3 ruling R1, requested via private-supervisor-AGET reconciliation memo). Non-breaking releases satisfy C-A via an explicitly-inherited, origin/main-published spec (3-part proviso); breaking releases still require a version-specific spec; documenting absence still fails. Closes the text-vs-intent gap where Option-B-inherit (v3.20 → v3.16.0) failed C-A literally despite meeting its intent. Note: the prior #1517 ruling comment misattributed "13/15 Exemplary" to v3.16 — 13/15 is FLEET-UPG-013/v3.15.0 (main fleet) per the calibration table above; v3.16 (FLEET-UPG-014) is a distinct per-fleet id (§FLEET-UPG-NNN namespace note); immaterial to C-A (v3.16 passes either way).

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Fleet upgrade close-out ceremony | Individual agent upgrade quality |
| Pre-flight BC detection and handling | Per-agent CI health |
| V-test completion and gate discipline | Session log quality |
| Residual filing and meta-pattern analysis | Issue content quality |
| Upstream value (L-docs, SOPs, templates) | Framework-AGET implementation work |

**FLEET-UPG-NNN namespace note**: The FLEET-UPG-NNN identifier is maintained per-fleet. Two fleets may each have a FLEET-UPG-013 that refers to different migration events. When citing scores across fleets, always qualify with fleet name (e.g., "main fleet FLEET-UPG-013" vs "legalon fleet FLEET-UPG-013"). This rubric scores a single fleet's upgrade; cross-fleet comparison requires fleet-qualified identifiers.

## Theoretical Basis

| Framework | Application |
|-----------|-------------|
| Gate Execution Discipline (L42) | D4 derives from L42's "execute only current gate, wait for explicit GO" |
| Advisory vs Structural Enforcement | D4 also tests whether V-test rows were enforced vs advisory |
| Evidence Before Implementation | D2 derives from BC pre-flight requirement |
| Fleet Upgrade Pattern | Scope basis — this rubric covers the G0–G4 fleet upgrade lifecycle |
| Score Multipliers Invert Intent (L018) | Design constraint — equal weights (20% each) to prevent any single dimension dominating |
| Extreme Anchoring (Mertler 2001) | Construction — L3 and L0 levels written first, L1/L2 interpolated |

**Scale Design**: L0–L3 conformance levels with equal weights to prevent any one dimension dominating.

| Level | Numeric | Label | Meaning |
|:-----:|:-------:|-------|---------|
| L3 | 3 | Exemplary | Sets pattern for next upgrade cycle |
| L2 | 2 | Compliant | Release outcome acceptable as-is |
| L1 | 1 | Baseline | Concerning — gap documented; improvement required next cycle |
| L0 | 0 | Non-Conformant | Release outcome not credible — rework or escalate |

**Aggregate score** = sum of dimension scores (max 15, since 5 dimensions × 3 max each). Mapping:
- **13–15**: Exemplary outcome. Pattern for fleet.
- **10–12**: Compliant. Release accepted.
- **6–9**: Baseline. Release accepted only with explicit gap documentation.
- **0–5**: Non-Conformant. Do not declare release complete.

## Constraints (Binary Eligibility Gates)

These pass/fail before the release is eligible for graduated scoring. **Any constraint failed → outcome scored 0 (Non-Conformant) regardless of dimension scores.**

| ID | Constraint | Pass Criterion |
|----|------------|----------------|
| C-A | **DEPLOYMENT_SPEC governing the release published before rollout** | **Conditional on release type** (keyed to the `breaking_release` field in the DEPLOYMENT_SPEC). **Breaking** (`breaking_release: true`): a version-specific `aget/DEPLOYMENT_SPEC_vX.Y.Z.yaml` (X.Y.Z = release version) committed + pushed to `origin/main` before any agent upgraded. **Non-breaking** (`breaking_release: false`): satisfied by the most-recent published DEPLOYMENT_SPEC the release **explicitly inherits**, PROVIDED **(1)** that inherited spec is committed + pushed to `origin/main` before rollout, **(2)** the release **names** the inherited source spec in its handoff/Gate-0, AND **(3)** the deployment contract is genuinely unchanged (no new install/verify/sleeping-requirement steps). Documenting the **absence** of any governing spec does **NOT** satisfy C-A (the declined β-path, #1517). Tag-vs-HEAD: the governing artifact need not be in the release tag — `origin/main` having it before the adopter's upgrade started suffices. (Amended v1.2.0 per #1517 D3 ruling R1, 2026-05-30.) |
| C-B | **All known residuals filed before close-out** | Every identified issue has a GitHub issue number filed before `Plan_Status: COMPLETE` is set |
| C-C | **Plan_Status field is COMPLETE** | The plan-level `**Plan_Status**:` field reads `COMPLETE` (distinct from per-gate `**Status**:` or `**Gate_Status**:` fields) |
| C-D | **All V-test outcomes recorded at time of report** | All V-tests in each gate block have a recorded outcome at time this report is authored. For checkbox-format plans: zero unchecked `- [ ]` V-test rows. For execution-log-format plans: every V-test item has a prose outcome entry (PASS/FAIL/SKIP with rationale). Format determines representation; the constraint is outcome coverage, not checkbox state. |

---

## Dimensions

### D1: Coverage Fidelity

**Weight**: 20%
**Definition**: Was the target fleet coverage achieved and verified by tooling — not stated, tooling-confirmed — with edge cases (LOCAL_ONLY, legacy, excluded) explicitly documented?

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|:------:|:---------:|
| D1.1 | Coverage verified by script output (not manual inspection) | 40% | Yes |
| D1.2 | FLEET_STATE.yaml (or equivalent fleet registry) per-agent version fields coherent with tooling output | 30% | No |
| D1.3 | Edge cases documented: LOCAL_ONLY agents, legacy exclusions, deferred agents | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|:-----:|----------|
| L3: Exemplary | 3 | 100% coverage verified by script (not sampling). Fleet registry per-agent fields coherent with scan output. LOCAL_ONLY agents explicitly named (committed but not pushed). Legacy exclusions named with rationale. Deferred agents listed with open issue. Fleet metadata (fleet_version, migration_status) consistent. |
| L2: Compliant | 2 | 100% coverage verified by tooling. Fleet registry metadata correct. Edge cases acknowledged but not all explicitly named. |
| L1: Baseline | 1 | Coverage claimed at 100% but verified by sampling or manual. Fleet registry updated. Edge cases not explicitly documented. |
| L0: Non-Conformant | 0 | Coverage stated but not tooling-verified. Fleet registry stale or incoherent. Residuals discovered post-close. |

---

### D2: Breaking Change Management

**Weight**: 20%
**Definition**: Were breaking changes identified in a pre-flight gate (before any agent upgraded), their scope bounded, and zero violations confirmed post-rollout?

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|:------:|:---------:|
| D2.1 | BCs identified and scoped in pre-flight gate (not during rollout) | 40% | Yes |
| D2.2 | Zero BC violations in rollout (or violations resolved before close-out) | 30% | Yes |
| D2.3 | Pre-flight protocol codified: SOP updated or issue filed for pattern reuse | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|:-----:|----------|
| L3: Exemplary | 3 | All BCs identified pre-flight with scope, mechanism, and affected agents named. Zero violations in rollout (each BC confirmed no-violation in V-tests). Pre-flight BC check pattern added to SOP or issue filed for framework. |
| L2: Compliant | 2 | BCs identified pre-flight. Zero violations. Pre-flight pattern not codified but documented in L-doc or session note. |
| L1: Baseline | 1 | BCs identified during rollout (not pre-flight) but before close-out. Violations discovered and resolved. No pattern capture. |
| L0: Non-Conformant | 0 | BCs discovered post-rollout. Violations unreported. No pre-flight analysis. |

---

### D3: Residual Capture

**Weight**: 20%
**Definition**: Were all residuals (issues, stale refs, open items) systematically identified, filed with evidence, root-caused, and promoted to meta-patterns where applicable?

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|:------:|:---------:|
| D3.1 | All residuals filed with evidence (issue number + root cause) before close-out | 40% | Yes |
| D3.2 | Root-cause analysis performed (e.g., 5-Why) with meta-pattern promoted to L-doc | 30% | No |
| D3.3 | Cross-fleet scope assessed; framework candidates filed via fleet-specific mechanism | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|:-----:|----------|
| L3: Exemplary | 3 | All residuals filed with evidence before close-out. 5-Why or equivalent performed; meta-root promoted to L-doc with evidence table. Cross-fleet scope assessed (other fleets, adjacent agents) with scope-limiting notes filed as issue comments. Framework candidates filed via the fleet's standard mechanism (e.g., an issue labeled with the target version, or a structured upstream notification) before close-out. |
| L2: Compliant | 2 | All residuals filed before close-out with evidence. No 5-Why. No cross-fleet scope check. |
| L1: Baseline | 1 | Most residuals filed; 1–2 discovered post-close. Some evidence. No root cause analysis. |
| L0: Non-Conformant | 0 | Residuals known at close-out but not filed. "Will handle later" without issue tracking. |

---

### D4: Gate Discipline

**Weight**: 20%
**Definition**: Were V-tests completed before gates were marked COMPLETE, gate Status lines updated before Plan_Status set to COMPLETE, and the plan health check clean immediately after close-out?

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|:------:|:---------:|
| D4.1 | V-tests completed at the gate they belong to (not retroactively at final close-out) | 40% | Yes |
| D4.2 | All per-gate `**Status**:` (or `**Gate_Status**:`) lines updated to COMPLETE before Plan_Status set | 30% | No |
| D4.3 | Agent plan health check (e.g., `wake_up.py` or equivalent) reports no false-active plans immediately post-close | 30% | No |

**Format note for D4.1**: Gate V-test completion depends on plan format. For checkbox-format plans (`- [ ]` rows): the checkbox must be ticked at the gate's own close-out step, not retroactively at final close-out. For execution-log-format plans: an outcome entry (PASS/FAIL with evidence) must be recorded for each V-test at the time the gate is closed, not retroactively. In both formats, retroactive completion at final close-out is L1, not L2 or L3.

**Clarification for D4.3**: "False-active plan" means the plan health check reports the project as still in-progress when it should be COMPLETE. This typically occurs when the plan-level `**Plan_Status**:` field is COMPLETE but one or more per-gate status fields are not updated to match, causing the health-check script to surface the plan as active. The specific script and field name vary by agent implementation — what matters is that the agent's own plan health mechanism confirms the plan is not surfacing as active.

#### Performance Levels

| Level | Score | Criteria |
|-------|:-----:|----------|
| L3: Exemplary | 3 | V-tests completed at the gate they belong to before the gate was marked COMPLETE (no retroactive completion). Gate Status lines swept as part of gate exit, not only at final close-out. Plan health check clean post-close. |
| L2: Compliant | 2 | V-tests all completed by final close-out (some retroactive, but none skipped). Gate Status lines swept at close-out. Plan health check clean. |
| L1: Baseline | 1 | V-tests partially incomplete at gate close; discovered and completed retroactively during the same session before final sign-off. Gate Status lines missed on at least one gate. Plan health check false-active discovered and fixed. |
| L0: Non-Conformant | 0 | V-tests incomplete when release declared complete. Plan_Status or Status line incoherence not resolved. Plan health check still reports false-active at close-out. |

---

### D5: Upstream Value

**Weight**: 20%
**Definition**: Did this release generate reusable improvements — L-docs, SOP updates, template fixes, framework candidates — that benefit future upgrades?

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|:------:|:---------:|
| D5.1 | ≥1 new L-doc capturing a structural lesson from this release | 40% | No |
| D5.2 | ≥1 SOP or template update derived from release findings | 30% | No |
| D5.3 | ≥1 framework candidate filed via the fleet's standard mechanism before close-out | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|:-----:|----------|
| L3: Exemplary | 3 | ≥2 new L-docs. ≥1 SOP update AND ≥1 template update. ≥1 framework candidate filed (issue labeled for target version or equivalent structured upstream notification). Reusable artifacts (fleet script, patch script) committed and documented. |
| L2: Compliant | 2 | ≥1 L-doc. ≥1 SOP or template update. ≥1 framework candidate identified (filed or in version scope). |
| L1: Baseline | 1 | Retrospective filed as issue. No structural SOP/template improvements. No framework candidates. |
| L0: Non-Conformant | 0 | No retrospective. No L-docs. No SOP updates. Knowledge siloed in session log. |

---

## Anti-Patterns Avoided in This Rubric

| Anti-Pattern | Source | How This Rubric Avoids It |
|--------------|--------|---------------------------|
| Score multipliers | L018 | Equal weights (20% each); no dimension >40% |
| Constraints as dimensions | L730 | C-A through C-D are binary eligibility gates, separate from D1–D5 |
| Achievement framing | Goodhart | Descriptions describe observable behavior ("V-tests completed at gate"), not outcomes ("release was smooth") |
| Single-dimension blocking | L018 | Critical-criterion failures penalize their own dimension to L0/L1 but don't block whole rubric (constraints handle blocking) |
| Post-hoc score inflation | Gate Discipline Pattern | D4 penalizes retroactive V-test completion — process discipline matters, not just final state |
| Format-dependent criteria | v1.1 calibration | D4.1 and C-D are format-agnostic: checkbox and execution-log plans both have a path to L3 |

## Scoring Procedure

1. **Constraint check**: Verify all four constraints (C-A through C-D) pass. If any fail → deliverable is Non-Conformant, score = 0, do not proceed.
2. **Dimension scoring**: For each of D1–D5, assess against the level criteria and assign 0–3.
3. **Critical criterion check**: If any "Critical? = Yes" criterion is unmet at L0, penalize that dimension to L0 regardless of other criteria in it.
4. **Aggregate**: Sum dimension scores. Map to overall band per the Scale Design table above.
5. **Document**: Record per-dimension reasoning (2–3 sentences each) in the release outcome report. Do not collapse to a bare number.

## Recommended Cadence

- **Self-check** (every FLEET-UPG close-out): Apply before filing the final close-out commit. Target: ≥10 (Compliant). Below 10 → flag explicitly or rework before declaring complete.
- **Principal meta-assessment** (per release): Apply retrospectively. Use to calibrate release quality standards across FLEET-UPG-NNN history.
- **Trajectory tracking** (FLEET-UPG-011 and later): Plot scores over time. Drift downward → process degradation; drift upward → process maturation.

## Open Questions for Principal Calibration

1. Should "upstream retro issue filed" be a constraint (C-E) rather than a D5 criterion? Filing the retro issue is more of a binary gate than a quality gradient. (Calibration feedback from FLEET-UPG-014 #1165.)

---

## Reference

| Link | Source |
|------|--------|
| Governing spec | `aget/specs/AGET_RELEASE_SPEC.md` CAP-REL-016 R-REL-024-03 |
| Template | `aget/templates/PROJECT_PLAN_TEMPLATE.md` (Closure Checklist) |
| Scored instances | FLEET-UPG-013 (13/15), FLEET-UPG-014 (10/15) |
| Promotion issue | gmelli/aget-aget#1165 |
| Calibration feedback | gmelli/aget-aget#1165 (five calibration points; four applied in v1.1) |

---

*Created via /aget-create-rubric (Generator level per ADR-008).*
*First scored instance: FLEET-UPG-013 (v3.15.0, 2026-04-26).*
*Second scored instance: FLEET-UPG-014 (v3.15.0, 2026-04-26) — drove v1.1 calibration.*
