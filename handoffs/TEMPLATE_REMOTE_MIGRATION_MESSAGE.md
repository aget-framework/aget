# TEMPLATE: Remote Migration Message

**Template Version**: 1.5.0
**Created**: 2026-03-09
**Owner**: aget-framework (canonical copy; instance-operative copy lives with the framework manager)
**Implements**: R-REL-019-07 (public handoff), G4.6 (shareable message)
**Related**: L457 (framework sync), L458 (fleet migration coordination), L582 (diff before overwrite), L612 (public handoff gap), L613 (operational precision), L631 (notification sanitization), L658 (handoff ground truth verification)

---

## Purpose

Reusable template for producing sanitized, self-contained migration messages for remote/external AGET fleet supervisors. Designed for supervisors who operate independently (different machine, different fleet) and need precise upgrade instructions without access to internal artifacts.

---

## Sanitization Checklist (L631)

Before publishing, verify:

- [ ] No `private-*-aget` or `private-*-AGET` agent names
- [ ] No `gmelli/*` repo references
- [ ] No fleet size disclosures (e.g., "32 agents")
- [ ] No internal session references (e.g., `SESSION_2026-*`)
- [ ] No hardcoded paths — use `$FW` for framework, `$AGENT` for agent
- [ ] No internal project IDs (e.g., `FLEET-*-###`)
- [ ] All L-doc references explained in context (per L587)
- [ ] Accuracy verified against post-release state (per L633)
- [ ] Every file path reference verified against `$FW` filesystem (per L658)

---

## Template

```markdown
# Migration Message: vPREV → vX.Y.Z

**Date**: YYYY-MM-DD
**From**: AGET Framework Manager
**To**: Remote Fleet Supervisors
**Target Version**: X.Y.Z — verified latest via the public release list (SOP_fleet_migration V0.1); do NOT infer the target from fleet-internal versions
**Migration Path**: vPREV → vX.Y.Z
**Breaking Changes**: Yes/No
**Currency note**: read this message from `main`, not the version tag — post-tag hardening notes and repairs land on `main` (see the release body's "Post-tag repairs" section)

---

## Behavioral Smoke (MANDATORY — rung 4, gh#1881; SOP_fleet_migration Gate 4.0)

*1–3 probes per payload feature, derived from DEPLOYMENT_SPEC M-rows. Each probe runs the new
signal ON THE EXECUTED SURFACE. Always include: (a) `python3 -m pytest tests/ -q` post-payload;
(b) executed-surface parity for any dual-basename target.*

| # | Payload feature (M-row) | Probe (run this) | Expected |
|---|---|---|---|
| 1 | {M-row id} | {command} | {observable} |

## Migration Target

- **Target version**: **vX.Y.Z** (explicit — never infer from N-1; this block is MANDATORY per template v1.5.0)
- **Deployment contract**: `DEPLOYMENT_SPEC_vX.Y.Z.yaml`, tag-reachable (`git show vX.Y.Z:DEPLOYMENT_SPEC_vX.Y.Z.yaml`)
- **Payload source**: [canonical `aget/` at tag | per amended handoff guidance — name the ruling if template tags lag]

---

## Step 0: Sync Framework (CRITICAL)

Before any upgrade work, sync your local framework clone. Stale framework repos cause agents to misread version availability and conclude the new version "does not exist."

```bash
cd $FW/aget && git pull origin main
cd $FW/template-{archetype}-aget && git pull origin main

# Verify target version is available:
python3 -c "import json; print(json.load(open('$FW/aget/.aget/version.json'))['aget_version'])"
# Expected: "X.Y.Z"
```

If the version does not show X.Y.Z, your framework repo is stale. Do NOT proceed until sync is confirmed.

---

## Step 0.5: Pre-Migration Verification — SUBSTANCE, not just the label (do NOT skip)

The version reading X.Y.Z confirms the *label* is set — NOT that the payload is present or the contract published. These checks convert failure modes from prior fleet migrations (FLEET-UPG-023) into self-contained pre-flight gates. A remote fleet has no producer-side relay to catch them.

```bash
# (a) DEPLOYMENT_SPEC published — the authoritative deployment contract (existence != deviation):
test -f $FW/aget/DEPLOYMENT_SPEC_vX.Y.Z.yaml && echo "spec OK" || echo "STOP: no DEPLOYMENT_SPEC_vX.Y.Z"
#   -> read it: per-artifact detection clauses + breaking_release + propagation_gap.
#   -> if ABSENT, the contract is unpublished — STOP + escalate. Do NOT relabel "no spec" as version.json.

# (b) SOURCE actually contains the new artifacts (a version bump does NOT copy payload — existence != substance):
T=$FW/template-{archetype}-aget
for f in <list each new vX.Y.Z artifact path>; do
  test -f "$T/$f" || echo "STOP: $T/$f missing — empty source pulls nothing; pull/escalate before migrating"
done
```

If either fails, **STOP** — migrating from an empty source, or relabeling a missing contract as a "deviation," are real, observed failures.

---

## What's New in vX.Y.Z

**Theme**: _[Release theme]_

_[2-3 sentence executive summary. Focus on what changes for agents, not internal process.]_

### Key Changes

| Change | Impact | Action |
|--------|--------|--------|
| _[change 1]_ | _[who it affects]_ | _[what to do]_ |
| _[change 2]_ | _[who it affects]_ | _[what to do]_ |

### Breaking Changes

_[None / List with migration steps]_

### Post-Release Corrections

_[List any corrections made after initial release that affect upgrade steps. Per L633.]_

---

## Upgrade Steps (Per Agent)

### Pre-Flight: Script Customization Check (base scripts, not just skills)

**Before overwriting any framework script**, check for local-only functions — scripts without `_ext` hooks (`health_check.py`, `study_topic.py` as of v3.25) accumulate legitimate instance checks in the base file, and a blind overwrite deletes them (field-observed: 8 local health-check invariants at risk in one supervisor's Wave-0):

```bash
# def-level delta: local-only functions = need a function-preserving MERGE, not an overwrite
diff <(grep -E '^def |^    def ' $AGENT/scripts/<script>.py) <(grep -E '^def |^    def ' $SOURCE/scripts/<script>.py)
```

**Conformance-then-bump**: hold the version stamp until every script carries the new substance — version-first is the symbol-vs-substance trap (#1600).

### Pre-Flight: Skill Customization Check

**Before overwriting any skills**, check for local customizations:

```bash
# If pre_sync_check.py is available in your framework clone:
python3 $FW/aget/.aget/patterns/upgrade/pre_sync_check.py \
  --baseline $FW/template-{archetype}-aget/.claude/skills/ \
  --instance $AGENT/.claude/skills/

# If not available, manually diff:
diff -rq $FW/template-{archetype}-aget/.claude/skills/ $AGENT/.claude/skills/

# Results:
#   clean/identical → safe to overwrite
#   conflict/differ → STOP: review manually, merge customizations
#   instance-only   → PRESERVE: agent-specific, do not overwrite
```

For any conflicts: diff the files, merge your customizations into the new version, then proceed.

### Steps

| # | Action | V-Test | Expected |
|---|--------|--------|----------|
| 1 | _[action]_ | _[command]_ | _[expected output]_ |
| 2 | _[action]_ | _[command]_ | _[expected output]_ |

### Post-Upgrade Validation

```bash
python3 $AGENT/scripts/wake_up.py
# Expected: Shows vX.Y.Z
```

---

## Fleet Coordination

Recommended wave strategy:

| Wave | Scope | Purpose |
|------|-------|---------|
| 0 | Supervisor self-upgrade | Validate new governance docs, confirm tooling |
| 1 | 2-3 pilot agents (one per portfolio) | Catch archetype-specific issues |
| 2 | Remaining agents (batches of 3-5) | Full rollout |

**After each wave** (FLEET-UPG-023 lessons): Run wake_up.py, confirm version, check for regressions — and:
- **Re-verify independently** — never trust the worker's self-report alone; the supervisor confirms version + SHA + tree state at source.
- **Respect per-agent variance** — standing no-push policies, deliberate dirty-tree holds, and instance-version semvers are legitimate; a blanket directive must NOT silently override them (use per-file `git add`).
- **Expect transient failures** at fleet scale — design the runner to record verified facts and make failures cleanly retryable (one retry usually clears it).
- **Headless dispatch: grant in-session execution authority explicitly** (v3.26 fleet-rollout canary lesson — the ask-but-don't-wait trap). A headless session cannot receive a GO/NOGO, so a dispatched agent that ends with "plan ready, awaiting your approval" has silently failed: the dispatch prompt MUST state that the agent has authority for its chosen in-scope disposition WITHIN THIS SESSION and must decide-execute-report (or decline with reasons) — never end holding a plan for an approval that cannot arrive. Verify-from-disk afterward distinguishes "planned" from "done".

---

## Main Fleet Experience

_[Lessons from the main fleet rollout that help remote supervisors avoid known issues.]_

| Finding | Impact | Mitigation |
|---------|--------|------------|
| _[finding 1]_ | _[what happened]_ | _[what to do]_ |

---

## Smoke Test Checklist

- [ ] `wake_up.py` shows vX.Y.Z
- [ ] **Full `health_check.py` passes — version-pass ≠ health-pass.** Run the *full* check, not just the version; expect to surface *pre-existing* drift (log it; don't let "all at vX.Y.Z" imply "all healthy").
- [ ] **L444 coherence is schema-aware** — manifests are heterogeneous across archetypes (e.g. worker = top-level `version:`, researcher = `instance.version:`). A uniform `grep '^version:'` false-flags; check the field your template actually uses.
- [ ] _[version-specific checks]_
- [ ] AGENTS.md shows `@aget-version: X.Y.Z`
- [ ] Conformance report shows CONFORMANT (if available)

---

## References

- [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md)
- [UPGRADING.md](https://github.com/aget-framework/aget/blob/main/docs/UPGRADING.md)
- [SOP_fleet_migration.md](https://github.com/aget-framework/aget/blob/main/sops/SOP_fleet_migration.md)

---

*Migration Message vX.Y.Z — Per R-REL-019-07, L457, L582*
```

---

## Authoring Checklist

Before sending a message from this template:

- [ ] Sanitization checklist (above) all PASS
- [ ] Step 0 (framework sync) included and version-correct
- [ ] **Target Version header present** and verified against the live release list (`gh release list --repo aget-framework/aget --limit 1`) at authoring time — a dispatch without an explicit target produces inferred N-1 targets downstream (field-evidenced 2026-07-05)
- [ ] Pre_sync_check skill preservation step included
- [ ] Post-release corrections section reflects actual state (L633)
- [ ] Main fleet experience section populated with real findings
- [ ] All V-test commands are copy-pasteable
- [ ] Every file path in message verified against public repo filesystem (L658)
- [ ] "Could a supervisor on a different machine execute this without asking questions?"

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-03-09 | Initial template. Incorporates L457, L458, L582, L612, L613, L631, L633. Completes deferred G4-G5 of PROJECT_PLAN_public_release_handoff_remediation. |
| 1.1.0 | 2026-03-09 | L658: Added filesystem verification to sanitization + authoring checklists. Made pre_sync_check.py conditional with diff fallback. |
| 1.2.0 | 2026-06-07 | **Step 0.5 Pre-Migration Verification** (substance ≠ label): verify DEPLOYMENT_SPEC published + source actually contains the new artifacts (a version bump does NOT copy payload). Smoke test: version-pass ≠ health-pass + schema-aware L444 coherence. Coordination: independent re-verify + respect per-agent variance + expect transient retries. Source: FLEET-UPG-023 v3.21 migration lessons (#1600 symbol-vs-substance root; #1607 schema-aware tooling; supervisor 8-lesson distillation). Remote fleets lack the producer-side relay that caught these locally → bake them into the message. |
| 1.3.0 | 2026-07-05 | **Target Version header (mandatory)** + read-from-main currency note + authoring-checklist release-list verification. Source: 2026-07-05 remote-fleet round-trip — a dispatch without an explicit target resolved to N-1 (fleet-internal inference) one day after the latest release shipped; and post-tag hardening notes were not reachable at the tag the reader was directed to. Tracking: framework tracker #1835 (dispatch declares target), #1834 (tag-payload coherence). |

| 1.4.0 | 2026-07-05 | **Script Customization pre-flight** (def-level delta before any base-script overwrite; function-preserving merge when local-only defs exist; conformance-then-bump). Source: second-fleet Wave-0 GATE-0 halt — blind overwrite per the message's own instruction would have deleted 8 local health_check invariants. Tracking: framework tracker #1836 (ext-hooks for health_check/study_topic — makes "overwrite" honest once shipped). |

| 1.5.0 | 2026-07-11 | **Migration Target block (mandatory)** — explicit target version + tag-reachable deployment contract + payload-source line as the message's first section. BACK-FILL NOTE: `REMOTE_MIGRATION_MESSAGE_v3.26.0.md` cited "mandatory per template v1.5.0" while the template file itself was never updated past 1.4.0 — the version existed only as a citation (asserted-not-computed class, sibling of #1871); this entry makes the citation true. ALSO: **headless-dispatch authority clause** (Fleet Coordination) — dispatch prompts must grant in-session execution authority; a headless agent ending "awaiting GO" has silently failed (v3.26 fleet-rollout canary lesson, ask-but-don't-wait trap). |

---

*TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.6.0* (v1.6.0: mandatory §Behavioral Smoke — the v3.26 instance had it, the template didn't [same asserted-not-computed class as v1.5.0's backfill note]; gh#1881 item 1, built v3.27 G2.1) (v1.5.1: footer version drift fixed — read v1.4.0 against the v1.5.0 changelog row, F-G3-1 class; caught at v3.27 G2.5 verification 2026-07-18)
*Completes G4.6 deliverable type*
