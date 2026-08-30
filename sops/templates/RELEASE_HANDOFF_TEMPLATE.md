# RELEASE_HANDOFF_vX.Y.Z.md

**Version**: X.Y.Z
**Released**: YYYY-MM-DD
**Breaking Changes**: Yes/No
**Framework Manager**: _[framework-manager agent]_

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

**Theme**: [Brief theme/title, e.g., "Shell Integration + Executable Knowledge"]

### Key Changes

1. **[Major Change 1]**: [Brief description]
2. **[Major Change 2]**: [Brief description]
3. **[Major Change 3]**: [Brief description]

### Migration Necessity and Proportionality

| Payload class | Receiver-local surfaces changed | Affected consumer / population source | Required adoption scope | Uniform-state dependency | Expected operational effect | Migration cost cap / stop trigger | Disposition |
|---|---|---|---|---|---|---|---|
| {agent-state / shared-runtime / control-only / documentation-only} | {version/rulebook/skill/runtime/API/data/schema/none} | {named consumers + authoritative register/contract} | {none / targeted consumer / canary / bounded cohort / full fleet} | {named invariant + evidence, or N/A} | {received behavioral or operator outcome} | {time/touches/attempts/threshold} | {execute / targeted adoption / defer / NOGO} |

`control-only` and `documentation-only` releases with no receiver-local state effect default to
**targeted consumer adoption**. A full-fleet wave requires a non-zero receiver-local change for every
in-scope seat or a named, evidenced **uniform-state dependency** such as compatibility, security, or a
terminal invariant. Version adoption alone is not delivered value. If the migration cost cap fires
without the expected accepted-state gain, freeze evidence and reclassify the rollout before another
attempt.

### New Specifications

- [List new specs, e.g., AGET_SPEC_NAME.md]
- [Or "None" if no new specs]

### New Validators

| Instrument | Governing predicate | Invocation + identity | Scope / population | Dependencies / interpreter | Controls | Result vocabulary | Evidence / last run |
|---|---|---|---|---|---|---|---|
| {validator path or None} | {requirement/decision or N/A} | `{exact command + version/digest}` | {register + denominator} | {runtime/imports} | {positive + negative} | {PASS/FAIL/UNAVAILABLE/etc.} | {receipt + timestamp} |

Listing a validator proves only existence. A release SHALL NOT describe it as operational unless the
documented invocation works in the intended consumer environment, its declared population is observed,
both-polarity controls pass, and its complete result is preserved.

### Production Failure Surface Coverage

<!-- Complete for every acceptance-blocking validator. Focused/unit success is insufficient when the
release claim depends on received identity, realistic scale, subprocess behavior, publication, or
recovery. -->

| Blocking control | Governed claim | Received identity / invocation | Realistic data / scale | Timeout + cancellation | Publication + durability claim | Recovery stable cut | Genuine failing case | Received positive case | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| {control} | {predicate} | {seat + exact command} | {worktree/corpus/population} | {bound + child cleanup} | {visibility atomic / verified publication / crash durable + evidence} | {rollback/restore proof} | {receipt showing this predicate fail} | {receipt showing production-path pass} | {blocking / advisory / retire} |

**Verified publication** requires completeness and integrity checks before the final path is visible.
Atomic rename alone does not establish **Crash durability**. A control stays advisory when its only
negative evidence is synthetic but its governed claim depends on received-environment behavior.

### Assurance Contract and Consumer Coherence

<!-- Complete when two or more release artifacts implement one schema, applicability rule, route
contract, or acceptance predicate. -->

| Contract | Authoritative contract source | Bound consumers | Independent observation source | Source / consumer identities | Drift consequence |
|---|---|---|---|---|---|
| {contract} | {single source path + symbol/version} | {prompt, validator, manifest, example, tests} | {receiver-observable evidence} | {digests/versions} | {preflight invalid / HOLD} |

Prompts, validators, examples, manifests, and tests SHALL NOT maintain independent copies of the same
field or branch contract. Cross-artifact coherence is checked separately from per-artifact validity.

### Capability Harvest and Verification Retirement

<!-- Complete when release work created custom tooling, schemas, fixtures, prompts, or checks. Code
survival is not evidence of reuse; retained candidates require a named consumer and adoption proof. -->

| Artifact / capability | Lifecycle class | Reusable nucleus | Release residue | Next consumer | Adoption test / deadline | Realized adoption result | Owner | Disposition |
|---|---|---|---|---|---|---|---|---|
| {artifact} | {ephemeral / release-scoped / reuse-candidate / framework} | {portable mechanism} | {version/seat/digest/attempt bindings} | {named release/project/None} | {consumer-environment test + trigger} | {PASS receipt / NOT RUN / rejected + reason} | {owner} | {delete / archive / promote / retain} |

| Verification control | Basis | Manual or principal step replaced | Principal-touch delta | Reassessment / retirement trigger | Handoff disposition |
|---|---|---|---|---|---|
| {control} | {durable invariant / model-tool limitation} | {step or None + justification} | {forecast -> actual} | {benchmark/adoption/lifecycle event} | {retain / consolidate / retire} |

`reuse-candidate` defaults to `release-scoped` when no later consumer adopts it by the declared trigger.
A named consumer is not adoption: promotion requires a distinct later release/project to execute the
reusable nucleus without inheriting the originating release's seat, digest, attempt, or patch residue. Model-
or tool-limitation controls SHALL be reassessed against the receiving default toolchain; concurrency,
freshness, rollback, evidence-authorship, and terminal-truth controls are not retired solely because the
model is stronger.

**Verification innovation freeze**: during release finalization, new assurance machinery requires a
named durable invariant that the existing portfolio cannot evaluate, plus the manual/control work it
consolidates, replaces, or retires—or an explicit net-burden justification.

### Accepted-State Impact

<!-- Complete for any release that strengthens a verifier, schema, applicability rule, or acceptance
predicate used by an already accepted deployment. -->

| Changed predicate | Previously accepted register / population | Impact | Revalidation | Required disposition | Evidence |
|---|---|---|---|---|---|
| {change} | {register + denominator + accepted identities} | {unaffected / revalidation required / invalidated / unavailable} | `{exact invocation}` | {retain / re-open / HOLD} | {receipt} |

A historical acceptance is not automatically valid under a strengthened contract. The handoff MUST
state the impact before presenting the new verifier as fleet-ready.

### Verification Convergence and Time Reserve

| Window / authority | Planned work | Evidence / wind-down reserve | Start accepted / population | End accepted / population | Attempts | Review/tooling rounds | Principal decisions / permission prompts | Controls added / consolidated / retired | Elapsed | Stop / escalation trigger | Outcome |
|---|---|---|---|---|---:|---:|---|---|---|---|---|
| {decision + budget} | {bounded actions} | {protected minutes} | {n/N} | {n/N} | {count} | {count} | {decision count / prompt count} | {+n / n / -n} | {duration} | {predeclared predicate} | {advance / HOLD / close} |

Green test count is not fleet convergence. Report accepted-state gain, terminal-predicate progress, and
measured manual/principal work removed. Re-derive remaining time at checkpoints; a later request extends
the horizon only when explicitly authorized. When the reserve or stop trigger is reached, freeze evidence
before adding another control or attempt.

### New L-docs

[Count and range, e.g., "18 L-docs: L451-L503, L505, L508-L511"]

---

## Upgrade Guide

### For Instances (AGETs)

1. Update `.aget/version.json`:
   ```json
   {
     "aget_version": "X.Y.Z",
     "migration_history": [
       "... existing ...",
       "vOLD -> vX.Y.Z: YYYY-MM-DD (Theme)"
     ]
   }
   ```

2. Update `AGENTS.md` header:
   ```markdown
   @aget-version: X.Y.Z
   ```

3. [Version-specific steps, if any]

4. **Run pytest**: should pass at your agent's pre-migration baseline + any newly-bundled framework tests. The N/N expected count varies by archetype role (e.g., framework-manager ~160, supervisor ~33, worker varies by domain). Treat the migration as PASS if pytest count matches your previous baseline plus any expected new tests, with no regressions — not by literal N/N match against the framework-manager number.

### DEPLOYMENT_SPEC Note (per release)

[Choose one — fill at handoff authoring time:]

- **Option A (default)**: `DEPLOYMENT_SPEC_vX.Y.Z.yaml` ships at canonical aget/ root. Fleet-upgrade tooling SHALL use this version's contract.
- **Option B (deployment-spec-optional, when applied)**: **No `DEPLOYMENT_SPEC_vX.Y.Z.yaml` ships** — explicit policy per principal Decide. vX.Y.Z inherits the prior available DEPLOYMENT_SPEC contract semantically (no breaking changes). Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z-prior}.yaml` as the contractual artifact set. **This is intentional, not oversight** — do not file `where-is-DEPLOYMENT_SPEC` issues. Cite full rationale in `aget/CHANGELOG.md` for this version.

### For Templates

[Template-specific guidance, or "Templates already updated. No action required if using vX.Y.Z templates."]

### Breaking Changes

[None, or list breaking changes with migration instructions]

### Per-Archetype Variation Disclosure

[State whether this release applies uniformly across all 13 archetype templates or has per-archetype variation.]

- **Uniform** (default): "This release applies uniformly across all 13 archetype templates: **no per-archetype variation** in vX.Y.Z deliverables. Each template (advisor, analyst, architect, consultant, developer, document-processor, executive, operator, researcher, reviewer, spec-engineer, supervisor, worker) gets the same boilerplate vX.Y.Z CHANGELOG entry; each bumps version.json + AGENTS.md @aget-version uniformly."
- **Variant** (when applied): "This release has per-archetype variation. See §Variation Detail below for which archetypes differ and what changes."

### Conditional Migration Decisions

<!-- [CONDITIONAL] Complete when an upgrade obligation depends on route shape, archetype, installed
capability, environment, or other applicability predicate. Omit only when no conditional obligation exists. -->

| Decision | Applicability predicate | Receiver-observable authority | If TRUE | If FALSE / N/A | If UNAVAILABLE / UNDETERMINED | Evidence |
|---|---|---|---|---|---|---|
| {decision} | {mechanically observable condition} | {primary source + instrument} | {required action} | {explicit non-applicability disposition} | {fail-closed HOLD/STOP} | {receipt path} |

The release declaration may bind an expected variant, but it does not substitute for receiver-observed
classification. Applicability and result are separate axes: `N/A` is not `PASS`, and ambiguity is not
permission to infer either branch.

### Fleet Observation and Mutation Strategy

| Stage | Population / register | State effect | Concurrency | Freshness / invalidators | Activation / stop rule |
|---|---|---|---|---|---|
| Read-only reconnaissance | {fleet population} | read-only | parallel / bounded | {receipt + invalidators} | {identifies receiver-specific risk only} |
| Fresh preflight | {fleet or next receiver} | read-only | bounded | {transaction freshness window} | `READY` conditionally activates execution |
| Receiver mutation | {ordered receivers} | receiver write | serial | {per-seat custody cut} | CONFIRM advances; FAIL/HOLD stops |

Parallel read-only reconnaissance is not execution or acceptance. Serial mutation remains the default
blast-radius boundary.

Transaction isolation, not blanket repository cleanliness, is the default safety property. Before
custody, lock, patch, staging, or commit, prove target/index scope, rollback readiness, response-path
availability, and byte-exact custody for unrelated work. Whole-worktree cleanliness is required only
when the handoff names the invariant that depends on it.

### Permission Capability Readiness

- [ ] Stable capability boundaries are named separately from seat, attempt, temporary path, and PID.
- [ ] Read-only verification is not coupled into a persistent write grant.
- [ ] One-use transaction commands offer one-time authority, not a reusable historical selector.
- [ ] Monitoring and custody checks have a bounded read-only route that cannot launch duplicate work.

| Custodied state | Before identity | Custody identity + included paths | Success stable cut | Failure stable cut | Restoration proof |
|---|---|---|---|---|---|
| {unrelated work} | {path/digest/index state} | {immutable reference + exact scope} | {accepted target + exact restore} | {target rollback + exact restore} | {byte/index/worktree proof} |

### Immutable Evidence Chain

| Event | Immutable artifact + digest | Prior / superseded event | State transition | Current-state derivation |
|---|---|---|---|---|
| {attempt / confirmation / HOLD / rollback / supersession} | {path + digest} | {event identity} | {before -> after} | `{derivation invocation}` |

Current accepted and pending populations SHALL be derived from the event chain. A new attempt appends;
it never overwrites a prior confirmation, HOLD, rollback, or carry-forward event.

---

## Sleeping Requirements Disclosure

[Disclose sleeping CAPs status for this release. Required even if "ZERO" — visibility is the discipline.]

- **New sleeping CAPs (this release)**: [list, or "None"]
- **Inherited sleeping CAPs (from prior releases)**: [list with current grace status, or "None"]
- **Sleeping CAPs closed (this release)**: [list with closure references, or "None"]

Per L731 sleeping-CAP discipline + R-DEP-013 visibility-through-2+-channels: every release SHALL re-disclose sleeping-requirement state, even if ZERO.

---

## Fleet Action Required

### Assessment Instrument Readiness

Before the first migration mutation:

- [ ] Every acceptance-blocking instrument in **New Validators** is invocable at the consuming seat.
- [ ] Runtime dependencies and the declared interpreter are available.
- [ ] The instrument observes the declared population and emits PASS, FAIL, and UNAVAILABLE distinctly.
- [ ] Positive and negative controls pass in the consumer environment.
- [ ] Exact receiver-authored responses are preserved completely; truncation or normalization fails closed.
- [ ] Any conditional decision above is independently observable or explicitly UNDETERMINED/HOLD.
- [ ] Shared contracts have one authoritative source and every bound consumer identity matches it.
- [ ] Strengthened predicates carry an accepted-state impact and revalidation receipt.
- [ ] Reconnaissance and mutation obey their declared read/write and concurrency boundaries.
- [ ] Operative counts and next boundary reproduce from the immutable evidence chain.
- [ ] Every custom release artifact has a lifecycle disposition; each retained reuse candidate names a
      consumer, owner, adoption test, and deadline or trigger.
- [ ] Verification controls record the principal-touch delta, consolidation result, and retirement or
      reassessment trigger; model-compensating checks are not treated as permanent invariants.
- [ ] Each acceptance-blocking control has a genuine failing production case and received-environment
      positive evidence across identity, invocation, scale, timeout/cancellation, publication, and recovery.
- [ ] Reuse candidates record realized later-consumer adoption; a named future consumer alone does not
      promote release-scoped code to framework capability.
- [ ] Every mutation-authorizing precondition passed before custody/lock/patch/staging/commit, and every
      custody path has named success and failure stable cuts with exact restoration proof.
- [ ] Finalization honored the verification innovation freeze or records the uncovered invariant and
      net-burden justification for each new assurance surface.
- [ ] Deadline execution preserved a predeclared evidence/wind-down reserve and reports attempts,
      review/tooling rounds, principal decisions/prompts, acceptance gain, and the stop-trigger outcome.
- [ ] Migration scope matches receiver-local effect; control-only/documentation-only payloads default to
      targeted adoption unless a named uniform-state dependency proves full-fleet necessity.

### Supervisor Tasks

- [ ] Acknowledge receipt of this handoff
- [ ] Broadcast vX.Y.Z availability to fleet
- [ ] Prioritize pilot upgrades
- [ ] Track and report adoption status

### Pilot Upgrade Tracking

| Pilot | Portfolio | Status | Date | Migration PR | Notes |
|-------|-----------|--------|------|--------------|-------|
| _[fleet-coordinator agent]_ | main | ⏳ Pending | | | Fleet coordinator |
| _[framework-manager agent]_ | main | ✅ Complete | YYYY-MM-DD | | Self (framework manager) |
| _[pilot agent]_ | main | ⏳ Pending | | | |
| _[pilot agent]_ | _[portfolio]_ | ⏳ Pending | | | |
| [Add other pilots as needed] | | ⏳ Pending | | | |

> Fill this roster with the agent names your own fleet uses. The rows above are **shape, not a
> roster** — a published template must not carry any operator's actual agent inventory.

**Migration PR column semantics** (added PP-035 / closes gh#1392 / L952):
- **Purpose**: Records the PR# that shipped the migration to this agent. Closes L952 deployment-evidence-channel traceability axis (PR# was previously unrecorded at migration moment).
- **Format (private/internal handoff)**: `{private-org}/{repo}#NNN` for internal agent migrations.
- **Format (promoted/public handoff per R-REL-019-07)**: `aget-framework/{repo}#NNN` only — private-org refs are sanitized per R-RHSC-002-02 / L631.
- **`N/A (direct-commit)` permitted** when migration uses direct-commit path (no PR opened). Acceptable per current SOP_point_upgrade.md Phase 4.
- **Value is forward-looking**: column populates non-N/A once branched-PR "heavyweight" route per gh#1392 is adopted; current default = `N/A (direct-commit)` for direct-commit migrations.
- **V-test V-UPGRADE-004**: SOP_point_upgrade.md Phase 4 requires PR# recording or `N/A (direct-commit)` marking (procedural consequence: STOP if neither).

### Adoption Target

- **Priority 1**: Supervisor + main portfolio (by YYYY-MM-DD)
- **Priority 2**: Other portfolios (by YYYY-MM-DD)

### Self-Tick Prevention (L656 + L908)

**Receiving agents SHALL NOT mark their own row ✅ on self-deploy alone.** L656 requires cross-AGENT deployment evidence; self-confirmation instantiates the L908 self-application gap. Receiving agents update only their own *handoff-consumed* + *upgrade-guide-executed* status. Pilot-confirmed deployment status (`✅`) is set by the supervisor or framework-manager on cross-AGENT verification, not self-tick. v3.17.0 caught two paired same-week recurrences of this pattern (framework-manager D6 over-statement; sibling fleet agent everything-but-self-migrate) — see gh#1277 for grounding evidence and v3.18 retro candidate D0 for the structural L-doc.

**Cross-AGENT pair**: framework-manager + supervisor at vX.Y.Z constitutes the minimum L656 cross-AGENT evidence; subsequent fleet rows are confirmed via supervisor pilot pass.

---

## Release Artifacts

| Artifact | URL |
|----------|-----|
| aget/ release | https://github.com/aget-framework/aget/releases/tag/vX.Y.Z |
| CHANGELOG | https://github.com/aget-framework/aget/blob/main/CHANGELOG.md |
| VERSION_HISTORY | https://github.com/aget-framework/aget/blob/main/docs/VERSION_HISTORY.md |
| Homepage | https://github.com/aget-framework |

---

## Deprecations (continuing; removal targets per POL-DEP-001)

[Re-list active deprecations with current grace status. Required every release per R-DEP-013 (visibility-through-2+-channels).]

| Item | Deprecated | Replacement | Removal Target | Status |
|------|------------|-------------|:--------------:|:------:|
| [item] | vA.B.C | [replacement] | vX.Y.Z | Active grace / Removed |

If no active deprecations: state "**No active deprecations at this release.**"

---

## Handoff Protocol

**From**: _[framework-manager agent]_ (Framework Manager)
**To**: _[fleet-coordinator agent]_ (Fleet Coordinator)
**Date**: YYYY-MM-DD
**Method**: This artifact + direct notification

### Acknowledgment

Supervisor: Please update this section upon receipt.

```
[ ] Acknowledged by: _______________
[ ] Date: _______________
[ ] Fleet broadcast sent: _______________
```

---

*RELEASE_HANDOFF_vX.Y.Z.md*
*Created: YYYY-MM-DD*
*Status: Awaiting supervisor acknowledgment*
