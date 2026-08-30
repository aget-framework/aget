<!--
TEMPLATE INSTRUCTIONS:
1. Replace all {placeholders} with actual values
2. Remove sections marked [OPTIONAL] if not needed
3. Delete this instruction block before finalizing
4. Consult SOP_PROJECT_PLAN_CREATION.md for guidance
-->

---
project_id: {PREFIX}-{NUMBER}
version: 1.0
owner: {agent-name}
created: {YYYY-MM-DD}
status: proposed
target: {vX.Y.Z or TBD}
depends_on: {dependency if any, or remove line}
priority: {high|medium|low}
classification: {internal|public}
scope: {domain}
verification_gates: {count}
principal_checkpoints: {count}
---

# PROJECT_PLAN: {Title}

**Version**: 1.0
**Date**: {YYYY-MM-DD}
**Owner**: {agent-name}
**Status**: PROPOSED
**Target**: {vX.Y.Z}
**Protocol**: L335 (Step Back Review KB)
**Tracking**: {What this tracks - L-doc, gap, version}

---

## Executive Summary

{1-2 paragraphs summarizing what this project delivers and why}

### Delivered Value

| Component | Delivered | Impact |
|-----------|-----------|--------|
| **{Component 1}** | {What was delivered} | {Impact statement} |
| **{Component 2}** | {What was delivered} | {Impact statement} |

---

## KB Audit Summary

<!-- [RECOMMENDED for substantial work] Follow SOP_pre_proposal_kb_audit.md -->

**Audit Date**: {YYYY-MM-DD}
**Proposal**: {Brief description}
**Checklist Used**: {A (Feature) | B (Architecture) | C (Release) | D (Quick)}

### Artifacts Consulted

| Artifact | Lines/Sections | Key Finding |
|----------|----------------|-------------|
| {document} | {lines} | {finding} |
| RELEASE_BRIDGE_vPRIOR_to_next.md | Velocity, follow-on, recurring gaps | {velocity calibration, pre-prioritized items} |
| PROJECT_PLAN_vPRIOR_release (Retrospective) | All subsections | {what went well/poorly, lessons learned} |

### Scope Verification

- Charter: {✅ In scope | ❌ Out of scope}
- Mission alignment: {✅ Aligned | ⚠️ Partial | ❌ Misaligned}

### Decision Authority

- Authority: {✅ Autonomous | ⚠️ Propose+Validate | ❌ Escalate}

### Precedents

| Precedent | Relevance |
|-----------|-----------|
| {L-doc or ADR} | {how it applies} |

### Novel Elements

{What has no precedent — requires extra scrutiny}

### Audit Conclusion

{Proceed | Revise | Escalate | Block}

---

## Objectives & Key Results

### Objective 1: {Primary Objective}

| KR | Target | Status |
|----|--------|--------|
| KR1.1 | {Target metric} | ⏳ |
| KR1.2 | {Target metric} | ⏳ |

### Objective 2: {Secondary Objective}

<!-- [OPTIONAL] Add more objectives as needed -->

| KR | Target | Status |
|----|--------|--------|
| KR2.1 | {Target metric} | ⏳ |

---

## Scope

### In Scope

| Area | Description |
|------|-------------|
| {Area 1} | {What's included} |
| {Area 2} | {What's included} |

### Out of Scope

| Area | Rationale | Deferral Target |
|------|-----------|-----------------|
| {Area 1} | {Why excluded} | {Future version or N/A} |

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {Dependency 1} | BLOCKS | {RESOLVED | PENDING} |

### Operational Context

<!-- [OPTIONAL] Per CAP-PP-014: For operational (non-release) PROJECT_PLANs -->

| Attribute | Value |
|-----------|-------|
| **Type** | {release | operational | infrastructure | research} |
| **Aggregates** | {List of contributing PROJECT_PLANs, or N/A} |
| **Contributes To** | {Parent PROJECT_PLAN, or N/A} |
| **Scope Definition** | {VERSION_SCOPE reference, or N/A} |

### Migration Necessity and Proportionality

<!-- [REQUIRED for releases offered to a fleet] Migration scope follows receiver-local effect, not the
existence of a new version. Derive the affected population from its authoritative register. -->

| Payload class | Receiver-local surfaces changed | Affected consumer / population source | Required adoption scope | Uniform-state dependency | Expected operational effect | Migration cost cap / stop trigger | Disposition |
|---|---|---|---|---|---|---|---|
| {agent-state / shared-runtime / control-only / documentation-only} | {version pin, rulebook pointer, skill, runtime, API, data, schema, or none} | {named consumers + register/contract} | {none / targeted consumer / canary / bounded cohort / full fleet} | {compatibility, security, terminal, or N/A + evidence} | {observable agent or operator outcome} | {time, touches, attempts, threshold} | {execute / targeted adoption / defer / NOGO} |

A `control-only` or `documentation-only` release with no receiver-local configuration, runtime, API,
data, schema, or skill effect defaults to **targeted consumer adoption**, not full-fleet migration.
Full-fleet migration requires either a non-zero receiver-local state change for every in-scope seat or a
named, evidenced uniform-state dependency. A version stamp is neither an operational effect nor a
benefit. When measured migration cost reaches the declared cap without the expected accepted-state
gain, stop and reclassify the rollout rather than manufacturing another attempt.

### Work Composition Forecast and Actuals

<!-- [REQUIRED for substantial release/migration work] This is descriptive capacity evidence, not a
ratio target. Classify bounded episodes by primary purpose; separately record their state effect. -->

| Primary purpose | Forecast | Actual | Evidence / interpretation |
|---|---:|---:|---|
| Enhanced assessment of state | {episodes or time} | — | {reads, audits, falsifiers, instrument work} |
| Changing state | {episodes or time} | — | {durable or rolled-back mutations} |
| Governance, coordination, or other | {episodes or time} | — | {authority, handoff, decision records} |

| Primary purpose | Read-only effect | Supervisor-local governed write | Receiver/public/external write |
|---|---|---|---|
| Enhanced assessment | {forecast/actual} | {forecast/actual} | {forecast/actual} |
| Changing state | {forecast/actual} | {forecast/actual} | {forecast/actual} |
| Governance/other | {forecast/actual} | {forecast/actual} | {forecast/actual} |

Do not optimize for a preferred ratio. Use the actual mix to distinguish necessary verification from
repeated rebuilding, drift repair, or dormancy of assessment infrastructure.

### Assessment Instrument Register

<!-- [REQUIRED when an instrument can pass/block a gate or acceptance decision] -->

| Instrument | Governing predicate | Identity / invocation | Scope / population | Dependencies / interpreter | Positive + negative controls | Result vocabulary | Evidence / last successful run |
|---|---|---|---|---|---|---|---|
| {instrument} | {requirement or decision} | `{exact command + version/digest}` | {declared register and denominator} | {runtime/imports} | {both polarities} | {PASS/FAIL/UNAVAILABLE/etc.} | {durable path + timestamp} |

An instrument is READY only when it exists, is invocable in the intended environment, reads the declared
scope, preserves its evidence, and passes both-polarity controls. Creation or a stale prior run is not
operational readiness.

### Production Failure Surface Coverage

<!-- [REQUIRED before an instrument becomes acceptance-blocking] A green focused suite proves only the
conditions it drives. Bind the control to the received production path and preserve one genuine failing
case in which the named predicate causes the control to fail. -->

| Blocking control | Governed claim | Production identity / invocation | Realistic data / scale | Timeout + cancellation | Publication + durability claim | Recovery stable cut | Genuine failing case | Received-environment positive case | Status |
|---|---|---|---|---|---|---|---|---|---|
| {control} | {predicate} | {consumer + exact command} | {realistic corpus/worktree/population} | {bound + child cleanup evidence} | {visibility atomic / verified publication / crash durable + proof} | {pre/postmutation recovery evidence} | {failure receipt where this predicate blocked} | {successful received-path receipt} | {advisory / blocking / retire} |

**Verified publication** means the final artifact becomes visible only after completeness and integrity
checks pass. Atomic rename proves visibility atomicity, not **Crash durability**; use the latter term only
when persistence and recovery across process/host interruption are explicitly tested. Synthetic helper
tests alone do not promote a control to blocking when the governed claim depends on production identity,
data volume, subprocess lifetime, or recovery behavior.

### Release Capability Lifecycle and Verification Portfolio

<!-- [REQUIRED when a release/migration creates custom tooling or adds acceptance checks] Retention is
not reuse. Classify each artifact at creation and again at handoff; retained candidates need a consumer
and an adoption test. Every new control needs a burden and retirement disposition. -->

| Artifact / capability | Lifecycle class | Reusable nucleus | Release-specific residue | Named next consumer | Adoption test | Realized later-consumer result | Owner + review trigger | Terminal disposition |
|---|---|---|---|---|---|---|---|---|
| {tool, runner, schema, fixture} | {ephemeral / release-scoped / reuse-candidate / framework} | {general mechanism} | {version, seat, digest, patch, attempt bindings} | {release/project/None} | {consumer-environment proof or N/A} | {PASS receipt / NOT RUN / rejected + reason} | {owner + date/event} | {delete / archive / promote / retain} |

| Verification control | Control basis | Observed failure guarded | Automation / consolidation target | Principal touches forecast / actual | Retirement or reassessment trigger | Disposition |
|---|---|---|---|---|---|---|
| {check} | {durable invariant / model-tool limitation} | {evidence} | {manual step replaced or shared runner} | {count/time} | {model benchmark, adoption, lifecycle event} | {retain / consolidate / retire / unavailable} |

A `reuse-candidate` without a named consumer, owner, adoption test, and later-consumer result is
release-scoped by default. Naming a future consumer is a hypothesis; promotion requires a
distinct later release/project to execute the reusable nucleus without importing the prior release's seat, digest,
attempt, or patch residue.
A new verification control SHOULD eliminate or automate an existing manual/principal step. If it only
adds coverage, record why its marginal detection value exceeds its maintenance and attention cost.

**Verification innovation freeze**: during finalization, add a new control only when the existing
portfolio cannot evaluate a named durable invariant. Record the uncovered invariant and the control or
manual step consolidated, replaced, or retired; otherwise justify the net increase in maintenance and
principal attention.

### Conditional Decision Table

<!-- [REQUIRED when a gate obligation depends on applicability, environment, variant, or receiver state]
Every row is total: TRUE, FALSE, and unavailable/ambiguous evidence all have an explicit consequence. -->

| Decision | Receiver-observable predicate | Authority / evidence | If TRUE | If FALSE | If UNAVAILABLE / UNDETERMINED | Executor / next boundary |
|---|---|---|---|---|---|---|
| {decision} | {mechanically observable condition} | {primary source + instrument} | {APPLIES consequence} | {N/A consequence—not PASS} | {fail-closed HOLD/STOP} | {owner + trigger} |

A declared classification is not an independently observed classification. If acceptance depends on the
predicate, supervisor assertion alone cannot replace receiver-observable evidence.

### Assurance Contract Source and Consumer Matrix

<!-- [REQUIRED when two or more instruments/artifacts implement the same gate contract] Generate or
bind consumers from one authoritative source. A copied field list is a drift risk, not a second source. -->

| Contract | Authoritative contract source | Generated / bound consumers | Independent observation source | Identity / digest | Drift consequence |
|---|---|---|---|---|---|
| {schema, route, applicability, etc.} | {single source path + symbol/version} | {prompt, validator, example, test, manifest} | {consumer-local evidence path} | {source + consumer identities} | {invalidate preflight / HOLD} |

The authoritative contract source defines shared syntax and semantics. Independent observation remains
independent: it MUST NOT derive the observed value from the same declaration it is meant to test.
Cross-artifact verification checks every consumer binding and repeated field, not only each file against
the manifest.

### Accepted-State Impact and Revalidation

<!-- [REQUIRED when a verifier, schema, applicability rule, or acceptance predicate is strengthened]
Re-derive the affected accepted population before treating the new rule as ready for execution. -->

| Contract / verifier change | Previously accepted population | Impact | Revalidation instrument | Consequence | Evidence |
|---|---|---|---|---|---|
| {change} | {register + denominator + accepted IDs} | {unaffected / revalidation required / invalidated / unavailable} | `{exact invocation}` | {retain / re-open / HOLD} | {receipt} |

A prior acceptance remains historical fact, but it is not automatically current-contract acceptance.
No accepted denominator may survive a strengthened predicate by assumption.

### Fleet Observation and Mutation Strategy

<!-- [REQUIRED for multi-receiver migrations] Observation may be parallel when read-only and bounded;
mutation and acceptance stay serial unless the governing procedure explicitly proves another model. -->

| Stage | Population / register | State effect | Concurrency | Freshness / expiry | Activation or stop rule |
|---|---|---|---|---|---|
| Read-only reconnaissance | {declared population} | read-only | {parallel/bounded} | {timestamp + invalidators} | {evidence needed before GO} |
| Fresh preflight | {next receiver / fleet} | read-only | {single/bounded} | {immediate transaction window} | {READY activates execution; otherwise HOLD} |
| Mutation and acceptance | {ordered receivers} | receiver/public/external write | serial | {per-seat transaction cut} | {CONFIRM advances; FAIL/HOLD stops} |

Parallel read-only reconnaissance reduces downstream surprise; it never pre-accepts a receiver or
weakens the serial mutation boundary.

Transaction isolation, not blanket repository cleanliness, is the default safety property. Prove the
governed target/index scope and byte-exact custody for unrelated work. Require whole-worktree cleanliness
only when a named invariant depends on it. Every mutation-authorizing predicate MUST pass before custody,
lock, patch, staging, or commit; a later confirmation cannot repair a missing precondition.

### Permission Capability Contract

<!-- [REQUIRED when execution crosses protected, receiver, public, or remote boundaries] Separate stable
capability classes from one-use selectors. Never persist attempt paths, temporary bundles, or PIDs. -->

| Capability | State effect | Stable command / operation boundary | Ephemeral selectors | Persistence disposition | Failure / fallback |
|---|---|---|---|---|---|
| {preflight, audit, mutation, commit, monitor} | {read/write class} | {stable entrypoint or categorical operation} | {seat, attempt, path, PID} | {one-time / stable-prefix eligible / prohibited} | {HOLD / manual route} |

Read-only assertions do not enlarge a write grant. Compound commands SHALL be decomposed when their
segments require different authority or persistence lifetimes.

| Custodied state | Before identity | Custody identity + included paths | Success stable cut | Failure stable cut | Restoration proof |
|---|---|---|---|---|---|
| {unrelated user work} | {path/digest/index state} | {immutable reference + exact scope} | {accepted target + exact restore} | {target rollback + exact restore} | {byte/index/worktree proof} |

Custody is governed transaction state. Interruption is safe only at a named stable cut where both the
target and unrelated work have an explicit, recoverable disposition.

### Immutable Evidence Events and Derived State

<!-- [REQUIRED for repeated attempts or carry-forward] Append events; derive the operative view. -->

| Event identity | Immutable evidence | Supersedes / relates to | State transition | Derivation check |
|---|---|---|---|---|
| {attempt/decision/confirmation/rollback} | {path + digest} | {prior event identity} | {before -> after} | `{command deriving current state}` |

Current counts, accepted identities, pending work, and the next boundary MUST be reproducible from the
immutable event chain. A summary or plan view may change; prior event bytes may not.

### Verification Convergence and Time Reserve

<!-- [REQUIRED for deadline-bounded release or migration execution] Cost is an acceptance quantity, not
only retrospective prose. Set the reserve and stop rule before execution; later budget extends the
horizon only when a new principal authorization explicitly says so. -->

| Window / authority | Planned work | Evidence / wind-down reserve | Start accepted / population | End accepted / population | Attempts | Review/tooling rounds | Principal decisions / permission prompts | Controls added / consolidated / retired | Elapsed | Stop / escalation trigger | Outcome |
|---|---|---|---|---|---:|---:|---|---|---|---|---|
| {decision + budget} | {bounded actions} | {minutes protected from execution} | {n/N} | {n/N} | {count} | {count} | {decision count / prompt count} | {+n / n / -n} | {duration} | {predeclared threshold or predicate} | {advance / HOLD / close} |

Test count and artifact count are diagnostic, not convergence measures. A finalization wave demonstrates
progress through accepted-state gain, a completed terminal predicate, or measured removal of future
manual/principal work. At every checkpoint, re-derive elapsed time and remaining reserve; do not let a
follow-on request silently reset the earlier horizon. When the predeclared stop trigger fires, freeze the
truthful state before inventing another verifier or attempt.

### Release PROJECT_PLAN Requirements (L553)

<!-- [REQUIRED for Type=release] Per R-REL-007 + L553 -->

**IF Type = release**, the following requirements apply:

| Requirement | Source | Verification |
|-------------|--------|--------------|
| Gates map to SOP phases | R-REL-007 | Each gate references SOP_release_process.md phase |
| Definition of Done referenced | L553 | Final gate includes DoD criteria |
| Phase 4 validation is BLOCKING | L406 | V-test: `post_release_validation.py exit code 0` |
| Scope consolidated | R-REL-013 | Single VERSION_SCOPE, no fragmented plans |

**Gate → SOP Phase Mapping** (instantiate as appropriate):

| PROJECT_PLAN Gate | SOP Phase | Purpose |
|-------------------|-----------|---------|
| Gate -1: Pre-Execution | Phase 0 | Manager migration, scope consolidation |
| Gate 0: Preparation | Phase 1 | Branch verification, content security |
| Gate 1: Version Bump | Phase 2 | Version consistency, CHANGELOG |
| Gate 2: Artifacts | Phase 3 | Tags, releases, handoff |
| Gate 3: Validation | **Phase 4 (BLOCKING)** | User-discoverable outcomes |

**Definition of Done Reference**:

The final gate MUST NOT be marked COMPLETE until:
1. `python3 .aget/patterns/release/post_release_validation.py --version X.Y.Z` returns exit code 0
2. All user-centric criteria in SOP Definition of Done (L553) are verified

See: `sops/SOP_release_process.md` Section "Definition of Done (L553)"

---

## Phase Plan

### Gate -1: Pre-Execution Evidence ⏳

<!-- [RECOMMENDED] Per CAP-PP-017: Verify prerequisites before implementation -->

**Objective**: Verify all prerequisites are met before execution begins
**Principal Checkpoint**: OPTIONAL

**Deliverables**:
1. [ ] Scope definition complete
2. [ ] Dependencies identified and resolved
3. [ ] Risk assessment complete
4. [ ] Implementation approach documented

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G-1.1 | Scope section complete | YES | ⏳ |
| V-G-1.2 | Dependencies resolved or documented | YES | ⏳ |
| V-G-1.3 | Risk assessment exists | NO | ⏳ |

**DECISION POINT**: Ready for implementation? [GO/NO-GO]

---

### Gate 0: Spec Verification (MP-1) ⏳

<!-- MANDATORY gate per D39. Verify or create governing specs for all in-scope items
     BEFORE implementation begins. Prevents "fix-first" anti-pattern (L289, ADR-008). -->

**Objective**: Verify or create governing specs for all in-scope deliverables BEFORE implementation
**Principal Checkpoint**: OPTIONAL
**SOP Phase**: N/A (principle-enforcement gate)

**Deliverables**:
1. [ ] Spec-status verification sweep — verify each in-scope item against actual files:

| D-item | Expected Spec | Verified? | Action Needed |
|--------|--------------|:---------:|---------------|
| {item} | {spec reference} | ⏳ | {verify / write / precedent sufficient} |

<!-- Add rows for each in-scope deliverable. Check L611 (stale VERSION_SCOPE) —
     items may be PRE-RESOLVED. RELEASE_BRIDGE calibration: ~40% pre-resolved probability. -->

2. [ ] For items with no governing spec: write formal requirements before implementation

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G0.1 | All in-scope items have verified spec status | YES | ⏳ |
| V-G0.2 | Items without specs have formal requirements written | YES | ⏳ |

**DECISION POINT**: All specs verified or created? Implementation may begin? [GO/NO-GO]

---

### Gate 1: {Gate Name} ⏳

**Objective**: {What this gate achieves}
**Principal Checkpoint**: {REQUIRED | OPTIONAL}

**Deliverables**:
1. [ ] {Deliverable 1}
2. [ ] {Deliverable 2}

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-G1.1 | {Verification criterion} | YES | ⏳ |
| V-G1.2 | {Verification criterion} | NO | ⏳ |

**DECISION POINT**: {Question}? [GO/NO-GO]

---

### Gate N: Validation & Finalization ⏳

**Objective**: Validate and close project
**Principal Checkpoint**: REQUIRED

**Deliverables**:
1. [ ] All prior gates validated
2. [ ] Retrospective complete
3. [ ] Follow-on work documented
4. [ ] Status updated to COMPLETE

**V-Tests**:

| ID | Test | BLOCKING | Result |
|----|------|----------|--------|
| V-GN.1 | All prior V-tests passed | YES | ⏳ |
| V-GN.2 | Retrospective complete (8 subsections) | YES | ⏳ |

**DECISION POINT**: Project complete? [COMPLETE]

---

## Success Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| {Criterion 1} | {Target} | — | ⏳ |
| {Criterion 2} | {Target} | — | ⏳ |

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation | Status |
|------|--------|-------------|------------|--------|
| R1: {Risk description} | {High|Medium|Low} | {High|Medium|Low} | {Mitigation strategy} | Open |
| R2: {Risk description} | {High|Medium|Low} | {High|Medium|Low} | {Mitigation strategy} | Open |

---

## Retrospective

<!-- Complete when status changes to COMPLETE -->

### Project Summary

| Field | Value |
|-------|-------|
| Project ID | {id} |
| Duration | {actual} |
| Status | COMPLETE |
| Deliverables | {X of Y delivered} |

### What Went Well

| Item | Evidence | Impact |
|------|----------|--------|
| {item} | {evidence} | {impact} |

### What Could Improve

| Item | Root Cause | Recommendation |
|------|------------|----------------|
| {item} | {cause} | {recommendation} |

### Metrics vs. Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| {metric} | {target} | {actual} | {MET|MISSED} |

### Work Composition Review

- [ ] Forecast and actual primary-purpose mix reconciled; differences explained without treating
      assessment frequency itself as waste.
- [ ] State effects reconciled separately from primary purpose.
- [ ] Every gate instrument has a current invocation/evidence receipt or is explicitly UNAVAILABLE.
- [ ] Repeated assessment episodes classified as reusable verification, drift repair, dormancy recovery,
      or new discovery.
- [ ] Shared assurance contracts have one authoritative source and all consumer bindings revalidate.
- [ ] Strengthened predicates carry an accepted-state impact receipt.
- [ ] Observation and mutation phases preserve their declared state-effect and concurrency boundaries.
- [ ] Permission grants use stable capabilities rather than attempt paths, temporary files, or PIDs.
- [ ] Operative state is reproducible from immutable evidence events rather than narrative alone.
- [ ] Custom release code has an `ephemeral`, `release-scoped`, `reuse-candidate`, or `framework`
      disposition; retained candidates name a consumer and adoption test.
- [ ] Verification additions reconcile controls retained, consolidated, and retired, including the
      principal-touch delta and reassessment of model/tool-limitation compensators.
- [ ] Every blocking control has a genuine failing production case plus received-environment positive
      evidence across its identity, invocation, scale, timeout/cancellation, publication, and recovery surface.
- [ ] Reuse candidates record a realized later-consumer result; unconsumed candidates default to
      release-scoped rather than remaining framework capability by inertia.
- [ ] Mutation-authorizing predicates ran before custody/lock/patch/staging/commit; any unrelated work
      used byte-exact custody with named success and failure stable cuts.
- [ ] The finalization wave honored the verification innovation freeze or recorded the named uncovered
      invariant and net-burden justification for each new control.
- [ ] Deadline execution preserved its declared evidence/wind-down reserve and recorded attempts,
      review/tooling rounds, principal decisions/prompts, acceptance gain, and stop-trigger disposition.
- [ ] Migration scope is proportional to receiver-local effect; control-only/documentation-only payloads
      use targeted adoption unless a named uniform-state dependency proves full-fleet necessity.

### Key Decisions Made

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | {decision} | {choice} | {why} |

### Risks Realized

| Risk | Realized? | Notes |
|------|-----------|-------|
| R1 | {Yes|No} | {notes} |

### Follow-On Work Identified

| Priority | Project | Scope | Destination |
|----------|---------|-------|-------------|
| P1 | {name} | {scope} | {where} |

### Lessons Learned

1. {lesson 1}
2. {lesson 2}

### Release Bridge

<!-- [CONDITIONAL] Include for release PROJECT_PLANs only. Omit for operational/research plans. -->
<!-- Feeds into RELEASE_BRIDGE document per SOP_release_process.md Phase 7.1 -->

| Field | Value |
|-------|-------|
| Velocity Profile | {per-gate-type ratios, overall ratio} |
| Pre-Resolved Probability | {percentage of items already done at start} |

#### Gate Innovations

| Gate | Value Demonstrated | Recommendation |
|------|-------------------|----------------|
| {gate} | {evidence} | {Standard / Optional / One-off} |

#### Cumulative Pre-Release Checklist Additions

- [ ] {new check discovered this release}

#### Operational Advice

1. {what I wish I knew at the start}

### Project Closure Checklist

- [ ] All gates passed (all BLOCKING V-tests ✅)
- [ ] All deliverables verified
- [ ] Work-composition actuals and assessment-instrument liveness reconciled when applicable
- [ ] Retrospective complete (all 9 subsections; Release Bridge conditional for release plans)
- [ ] Follow-on work documented
- [ ] L-docs filed if applicable
- [ ] Status updated to COMPLETE

---

## References

- {Reference 1}: {Brief description}
- {Reference 2}: {Brief description}

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {YYYY-MM-DD} | Initial plan |

---

*PROJECT_PLAN_{name}_v1.0.md*
*Created: {YYYY-MM-DD}*
*Owner: {agent-name}*
*Status: PROPOSED*
