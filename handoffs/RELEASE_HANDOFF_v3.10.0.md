# RELEASE_HANDOFF: v3.10.0

**Version**: 3.10.0
**Released**: 2026-03-21
**Theme**: Structural Enforcement
**Breaking Changes**: None (3 skill renames — old dirs continue to work)
**Framework Manager**: aget-framework
**Status**: READY

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

## Deployment Requirements

**State-Based Deployment**: This release uses state-based deployment (L541, L581). Do NOT use delta-based upgrades.

**Deployment Spec**: `specs/DEPLOYMENT_SPEC_v3.10.0.yaml` (in the framework agent's private repo — delivered as part of this handoff package)

### Before Upgrading

1. Read the deployment spec (included in this handoff or available from the framework agent)
2. Verify you have access to all canonical sources listed (public templates at aget-framework/)
3. Use the verification script in the spec to validate after upgrade, or use the Smoke Test Checklist below

### Target State Summary

| Artifact Type | Count | Canonical Source |
|---------------|-------|------------------|
| Universal Skills | 16 (3 renamed in this release) | template-worker-aget/.claude/skills/ |
| Skill Specs | 18+ | aget/.aget/specs/skills/ |
| Session Scripts | 4 (wake_up.py, wind_down.py, study_up.py, aget_housekeeping_protocol.py) | aget/scripts/ |
| MUST-invoke Skills | 2 (/aget-create-project, /aget-file-issue) | AGENTS.md structural directives |

**Canonical Source**: `$FW` = path to your local clone of aget-framework/aget/

**Verification**: After upgrade, run the verification script in `specs/DEPLOYMENT_SPEC_v3.10.0.yaml` to confirm correct deployment.

---

## Release Summary

**Theme**: Structural Enforcement — the system makes ungoverned paths structurally unavoidable.

### Key Changes

1. **D71: 3-Layer Structural Enforcement** — MUST-invoke directives (Layer 1), Gate Boundary Protocol (Layer 2), Skill Completion Signal (Layer 3)
2. **D69: Dual-Repo Sync Governance** — SOP Phase -0.5, R-SYNC-002 spec, validate_content_sync.py
3. **#480: Skill Naming Reconciliation** — 3 renames (`capture`→`record`, `study-up`→`study-topic`), 633 references updated
4. **#439: SKILL_SPEC_TEMPLATE.yaml** — Standard skill spec template deployed to all 12 templates

This is the first multi-plan coordinated release in AGET history.

### Breaking Changes

None. v3.10.0 is backward compatible with v3.9.x. Skill renames maintain old directories until fleet upgrade.

### Deprecations (R-DEP-010 compliant)

| Field | `capture` verb (Learning family) | `aget-study-up` name |
|-------|----------------------------------|---------------------|
| **What** | `capture` verb in skill names (`aget-capture-observation`, `aget-capture-nugget`) | `aget-study-up` skill directory name |
| **Why** | CS-002 naming standard violation — `record` better reflects the action semantics (#480) | CS-002 — `study-topic` is more precise than `study-up` (#480) |
| **Replacement** | `record` verb: `aget-record-observation`, `aget-record-nugget` | `aget-study-topic` |
| **Removal timeline** | Old directories MAY be removed in v3.12.0 (per POL-DEP-001, R-DEP-011: 2 minor version grace) | Old directory MAY be removed in v3.12.0 |
| **Detection** | `ls .claude/skills/ \| grep capture` — any matches = deprecated name in use | `ls .claude/skills/ \| grep study-up` — any match = deprecated name in use |

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| MUST-invoke directives (CLAUDE.md) | All agents — `/aget-create-project` and `/aget-file-issue` now structurally required | Sync AGENTS.md from template |
| Gate Boundary Protocol (SOP) | Framework — plan update + commit = gate proof | No agent action — SOP governance |
| Skill Completion Signal (2 skills) | All agents — signal absence = incomplete execution | Sync skill files from template |
| SOP Phase -0.5: Content Sync | Framework — private→public sync governance | No agent action — SOP governance |
| R-SYNC-002 spec (6 EARS reqs) | Framework — content sync validation | No agent action — spec governance |
| validate_content_sync.py | Framework — sync validation tool | No agent action — framework tool |
| validate_changelogs.py | Framework — CHANGELOG consistency tool | No agent action — framework tool |
| SKILL_SPEC_TEMPLATE.yaml | All agents — standard skill spec template | Available in `.aget/specs/skills/` |
| Structural Trigger Conditions (PATTERN) | All agents — gate completion triggers step-back review | Sync pattern file from template |

### Changed

| Change | Migration |
|--------|-----------|
| 3 skill renames (#480) | See Text Replacement Table below (R4-R6) |
| `capture` verb retired from Learning family | Use `record` instead |
| Gate Execution Discipline strengthened | MUST update plan + MUST commit at gate boundary |

### Fixed

| Fix | Impact |
|-----|--------|
| Template hygiene (#574) | VERSION, setup.py classifier, SECURITY.md in 4 templates |
| wind_down.py improvements | Smarter status detection, scan_nuggets() |

---

## Upgrade Guide (with Per-Step Verification)

Each step includes a V-test command and an RFC 2119 obligation level. Run the V-test after completing the step to confirm success before proceeding.

**Obligation levels** (RFC 2119, IETF BCP 14):
- **MUST**: Absolute requirement — upgrade will fail or produce incorrect state if skipped
- **SHOULD**: Recommended — skipping is acceptable only with documented justification
- **MAY**: Optional — consumer decides based on local context

### For Instances (AGETs)

| Step | Obligation | Action | V-Test Command | Expected |
|------|-----------|--------|---------------|----------|
| 1 | SHOULD | Run pre-sync check (detect skill customizations before overwriting) | `python3 .aget/patterns/upgrade/pre_sync_check.py --baseline ~/path/to/template-{archetype}-aget/.claude/skills/ --instance .claude/skills/` | Report with 0 CONFLICT items |
| 2 | MUST | Update `.aget/version.json`: set `aget_version` to `"3.10.0"`, set `updated` to upgrade date | `jq -r .aget_version .aget/version.json` | `"3.10.0"` |
| 3 | MUST | Add migration_history entry to version.json (see below) | `jq -r '.migration_history \| last' .aget/version.json \| grep '3.10.0'` | Match |
| 4 | MUST | Update `AGENTS.md` header: `@aget-version: 3.10.0` | `grep '@aget-version: 3.10.0' AGENTS.md` | Match |
| 5 | MUST | Rename skill directories (see Text Replacement Table R4-R6) | `ls .claude/skills/ \| grep -c 'capture\|study-up'` | `0` |
| 5.5 | SHOULD | Rename spec YAML files to match new skill names (L590: spec file renames are easy to miss) | `ls .aget/specs/skills/ 2>/dev/null \| grep -c 'capture\|study-up'` | `0` |
| 6 | MUST | Sync AGENTS.md D71 sections from template (MUST-invoke, routing table, bypass detection) | `grep -c 'MUST invoke\|Structural Skill Routing\|Governance Bypass Detection' AGENTS.md` | `3` |
| 7 | MUST | Sync updated skill files from template (aget-create-project, aget-enhance-spec with Completion Signal) | `grep -c 'Skill Completion Signal' .claude/skills/aget-create-project/SKILL.md` | `1` |
| 8 | SHOULD | Sync SKILL_SPEC_TEMPLATE.yaml (#439) | `test -f .aget/specs/skills/SKILL_SPEC_TEMPLATE.yaml && echo PASS` | `PASS` |
| 9 | SHOULD | Deploy wind_down.py update from framework | `python3 scripts/wind_down.py --version 2>/dev/null \|\| echo "check manually"` | v2 or later |
| 10 | MUST | Validate: run wake_up.py | `python3 scripts/wake_up.py` | Shows v3.10.0 |

**Migration history entry**:
```
"v3.9.0 -> v3.10.0: YYYY-MM-DD (Structural Enforcement - 3-layer enforcement, dual-repo sync, skill renames)"
```

### Fleet-Wide

- [ ] Wave 0: Supervisor first (validate MUST-invoke directives work in session)
- [ ] Wave 1: 2-3 simple agents from different archetypes (test skill renames + D71 sections)
- [ ] Wave 2: Remaining agents
- [ ] Verify: All agents at v3.10.0

### End-State Validation

Run the Smoke Test Checklist above (8 checks). All 8 must PASS.

**Optional** (if conformance script is available in your fleet):
```bash
python3 .aget/patterns/conformance/aget_conformance_report.py --version 3.10.0 --depth deep --target .
```
Note: The conformance script is an internal tool — it may not exist in all deployments. The Smoke Test Checklist provides equivalent coverage.

---

## Text Replacement Table

Exact old→new string replacements for AGENTS.md and other edited files. Use Edit tool (not sed — macOS hazard). Each row is one edit operation.

| ID | File | Location Hint | Old Text (exact) | New Text (exact) | Applies To | V-Test |
|----|------|---------------|------------------|------------------|------------|--------|
| R1 | `.aget/version.json` | `aget_version` field | `"aget_version": "3.9.0"` | `"aget_version": "3.10.0"` | All agents | `jq -r .aget_version .aget/version.json` → `3.10.0` |
| R2 | `.aget/version.json` | `updated` field | `"updated": "2026-03-15"` | `"updated": "YYYY-MM-DD"` (upgrade date) | All agents | `jq -r .updated .aget/version.json` → upgrade date |
| R3 | `AGENTS.md` | Line ~3 (header) | `@aget-version: 3.9.0` | `@aget-version: 3.10.0` | All agents | `grep '@aget-version: 3.10.0' AGENTS.md` |
| R4 | `.claude/skills/` | Directory rename | `aget-capture-observation` | `aget-record-observation` | All agents with old name | `test -d .claude/skills/aget-record-observation && echo PASS` |
| R5 | `.claude/skills/` | Directory rename | `aget-capture-nugget` | `aget-record-nugget` | All agents with old name | `test -d .claude/skills/aget-record-nugget && echo PASS` |
| R6 | `.claude/skills/` | Directory rename | `aget-study-up` | `aget-study-topic` | All agents with old name | `test -d .claude/skills/aget-study-topic && echo PASS` |
| R7 | `AGENTS.md` | After "Execution Behavior" section | _(section absent)_ | Add "Governed Project Creation (STRUCTURAL — D71 Layer 1)" section | All agents | `grep -c 'MUST invoke.*/aget-create-project' AGENTS.md` → `1` |
| R8 | `AGENTS.md` | After R7 section | _(section absent)_ | Add "Structural Skill Routing (D71)" table | All agents | `grep -c 'Structural Skill Routing' AGENTS.md` → `1` |
| R9 | `AGENTS.md` | After R8 section | _(section absent)_ | Add "Governance Bypass Detection (D71)" table | All agents | `grep -c 'Governance Bypass Detection' AGENTS.md` → `1` |

**R7-R9 source**: Sync these sections from your archetype template's `AGENTS.md` (e.g., `template-worker-aget/AGENTS.md`). Do NOT write freehand — templates contain the canonical text.

**Rename commands** (R4-R6):
```bash
mv .claude/skills/aget-capture-observation .claude/skills/aget-record-observation 2>/dev/null
mv .claude/skills/aget-capture-nugget .claude/skills/aget-record-nugget 2>/dev/null
mv .claude/skills/aget-study-up .claude/skills/aget-study-topic 2>/dev/null
```

**Multi-location check**: After all replacements, verify no stale references remain:
```bash
grep -c 'aget-version: 3.9.0\|capture-observation\|capture-nugget\|aget-study-up' AGENTS.md
# Expected: 0
```

---

## Script Deployment Checklist

### Changed Scripts

| Script | Action | Source | Classification | V-Test |
|--------|--------|--------|---------------|--------|
| `wind_down.py` | Deploy latest | `$FW/scripts/wind_down.py` | Framework_Artifact (overwrite-safe) | `python3 scripts/wind_down.py --help` runs without error |
| `aget-create-project/SKILL.md` | Deploy v3.10.0 (Completion Signal added) | `template-{archetype}-aget/.claude/skills/aget-create-project/SKILL.md` | Framework_Artifact (overwrite-safe) | `grep -c 'Completion Signal' .claude/skills/aget-create-project/SKILL.md` → `1` |
| `aget-enhance-spec/SKILL.md` | Deploy v3.10.0 (Completion Signal added) | `template-{archetype}-aget/.claude/skills/aget-enhance-spec/SKILL.md` | Framework_Artifact (overwrite-safe) | `grep -c 'Completion Signal' .claude/skills/aget-enhance-spec/SKILL.md` → `1` |

### New Scripts

| Script | Source | V-Test |
|--------|--------|--------|
| (none for agent deployment — `validate_content_sync.py` and `validate_changelogs.py` are framework-only tools) | — | — |

### Instance Extension Check (BLOCKING per step)

**Before overwriting any existing script**:
1. `diff scripts/wind_down.py $FW/scripts/wind_down.py` — review differences
2. If agent has instance-specific code not in framework version:
   - Check if `scripts/wind_down_ext.py` exists (C1 hook architecture)
   - If yes: instance extensions are preserved automatically — safe to overwrite
   - If no: migrate instance code to `scripts/wind_down_ext.py` before overwriting
3. If diff shows only framework changes: safe to overwrite

### Preservation Exceptions

| Script | Agent(s) | Reason | Action |
|--------|----------|--------|--------|
| `wake_up_ext.py` | Any agent with domain-specific wake-up | Instance_Artifact | PRESERVE — never overwrite |
| `wind_down_ext.py` | Any agent with domain-specific wind-down | Instance_Artifact | PRESERVE — never overwrite |

---

## Archetype Divergence Notes

Known variations in agent AGENTS.md structure that affect upgrade applicability:

| Variation | Agents Likely Affected | Impact on Upgrade | Recommendation |
|-----------|----------------------|-------------------|----------------|
| Missing "Execution Behavior" section | Custom AGENTS.md agents, older agents | R7-R9 location hint is wrong — D71 sections have no anchor | Add sections at end of AGENTS.md, or after nearest governance section |
| Supervisor AGENTS.md has fleet coordination sections | All supervisors | D71 sections may conflict with supervisor-specific governance directives | Review for conflicts; supervisor may need to adapt MUST-invoke scope |
| Agent has custom `/aget-create-project` overrides | Agents with domain-specific project templates | R7 MUST-invoke may override custom behavior | Verify custom behavior is preserved in domain-specific routing, not skill bypass |
| Agent has no `aget-capture-*` skills (never deployed) | Agents created after v3.9.0 with manual skill setup | R4-R5 renames are no-ops | Verify `aget-record-*` skills exist directly |

**Fleet heterogeneity warning**: Do not assume all agents share the same AGENTS.md structure as the supervisor or template. Audit representative agents from each archetype before building your upgrade plan.

**Domain version vs framework version**: Lines containing version numbers in "Project Context" or domain-specific sections (e.g., `v3.0.0` for a domain project) are NOT aget framework versions. Do not update these during framework upgrades. Only `@aget-version:` and version.json are framework version indicators.

---

## Migration Guide: Skill Renames

| Old Name | New Name | Verb Change |
|----------|----------|-------------|
| `aget-capture-observation` | `aget-record-observation` | capture → record |
| `aget-capture-nugget` | `aget-record-nugget` | capture → record |
| `aget-study-up` | `aget-study-topic` | study-up → study-topic |

**Impact**: Old skill directories continue to work until the agent upgrades. The renames affect:
- `.claude/skills/` directory names
- AGENTS.md skill references
- Any custom scripts referencing old names

**Recommended**: Rename at upgrade time. No rush — backward compatibility maintained.

---

## Context for External Fleets

### What is 3-Layer Structural Enforcement?

The core innovation of v3.10.0. Instead of relying on agents to *remember* governance rules (behavioral enforcement), the system makes ungoverned paths *structurally unavailable*.

**Layer 1 — Skill Invocation**: CLAUDE.md now contains MUST-invoke directives. Creating a PROJECT_PLAN without `/aget-create-project` or filing an issue without `/aget-file-issue` is explicitly prohibited.

**Layer 2 — Gate Boundary**: Gate completion is now defined as plan update + commit. The Gate Boundary Protocol requires 6 steps at every gate boundary, with the commit serving as structural proof.

**Layer 3 — Skill Step**: Skills now emit a Completion Signal at the end of execution. If the signal is absent, the skill execution is incomplete. This makes completeness structurally visible.

**ADR-008 Level**: All 3 layers are at Strict (validator exit code). Generator level (hooks) requires #505 infrastructure.

### What are MUST-invoke Directives?

CLAUDE.md directives that structurally require skill invocation for specific operations. Currently:
- `/aget-create-project` MUST be invoked when creating `planning/PROJECT_PLAN_*.md`
- `/aget-file-issue` MUST be invoked when filing GitHub issues

**Enforcement**: Strict (CLAUDE.md directive with explicit PROHIBITED alternative).

---

## v3.9.0 Observation Status

| # | v3.9.0 Observation | v3.10.0 Status |
|---|-------------------|----------------|
| 1 | 4 human step-back interventions in [internal-project] | **Addressed** — D71 3-layer enforcement targets root cause |
| 2 | Content sync ungoverned between private/public | **Resolved** — D69 SOP Phase -0.5 + validators |
| 3 | Skill naming inconsistency (CS-002 violation) | **Resolved** — #480 renames + `capture` verb retired |
| 4 | SKILL_SPEC_TEMPLATE.yaml not in templates | **Resolved** — #439 deployed to 12 templates |

---

## Smoke Test Checklist

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Wake-up shows correct version | `python3 scripts/wake_up.py` | Shows v3.10.0 |
| 2 | Housekeeping passes | `python3 scripts/aget_housekeeping_protocol.py --json` | 9/9 healthy or warning |
| 3 | AGENTS.md version correct | `grep '@aget-version: 3.10.0' AGENTS.md` | Match |
| 4 | Version bump check passes | `python3 .aget/patterns/release/version_bump.py --check 3.10.0` | Exit 0 |
| 5 | Old skill names removed | `ls .claude/skills/ \| grep -c 'capture\|study-up'` | `0` |
| 6 | Completion Signal in governed skills | `grep -c 'Completion Signal' .claude/skills/aget-create-project/SKILL.md .claude/skills/aget-enhance-spec/SKILL.md` | `2` (one per file) |
| 7 | MUST-invoke directives present | `grep -c 'MUST invoke' AGENTS.md` | `2+` |
| 8 | D71 sections present | `grep -c 'Structural Skill Routing\|Governance Bypass Detection' AGENTS.md` | `2` |

---

## Principal Spot-Check Sequence (L715, L718)

After fleet upgrade, the principal should independently verify a sample of agents. This catches different issue classes than supervisor V-tests (L718: output verification vs outcome verification).

**Sequence** (~2 min per agent):

| Step | Action | What It Validates |
|------|--------|------------------|
| 1 | Read AGENTS.md header. Run `/aget-wake-up`. | Version, identity, structural health |
| 2 | Run `/aget-check-health full` | Specs, baselines, governance, traceability |
| 3 | Smoke test: `/aget-record-observation test` | Universal skill renamed correctly + executes (L716: must use universal skill) |
| 4 | Report findings. **Do NOT wind down.** | Spot checks are inspections, not sessions |

**Sample selection**: Pick 2-3 agents from different archetypes. Prioritize agents with organic skills or custom AGENTS.md sections (higher divergence risk).

**Known issues to watch for**:
- Deprecated `scripts/wake_up.py` path at `.aget/patterns/session/wake_up.py` (L717, #608)
- Spec YAML files not renamed to match new skill names (L590)
- AGENTS.md line count approaching limits (#609)

---

## Rollback

### Rollback Feasibility

| Aspect | Assessment |
|--------|-----------|
| Rollback complexity | Simple (version numbers + directory renames) |
| Data compatibility | Bidirectional — old skill directories work alongside new |
| Recommended approach | Revert version indicators + rename skill dirs back + remove D71 AGENTS.md sections |

### Rollback Steps

1. Revert `.aget/version.json`: set `aget_version` back to `"3.9.0"`, revert `updated` date
2. Revert `AGENTS.md`: set `@aget-version: 3.9.0`
3. Rename skill directories back: `aget-record-observation` → `aget-capture-observation`, etc.
4. Remove D71 sections from AGENTS.md (MUST-invoke, Structural Skill Routing, Governance Bypass Detection)
5. Re-deploy v3.9.0 scripts from `$FW` at tag `v3.9.0`

### Rollback V-Test

```bash
jq -r .aget_version .aget/version.json
# Expected: "3.9.0"
grep '@aget-version: 3.9.0' AGENTS.md
# Expected: match
ls .claude/skills/ | grep -c 'capture-observation\|capture-nugget\|study-up'
# Expected: 3 (old names restored)
```

---

## Known Items (non-blocking)

| Item | Impact | Recommendation |
|------|--------|----------------|
| ADR-008 enforcement is Strict, not Generator | Hooks (#505) needed for next enforcement level | No action — Strict is sufficient for v3.10.0 |
| 13 L0 specs need EARS patterns for L1 promotion | Spec maturity backlog, not deployment-blocking | Address in future spec enhancement sessions |
| `version.json` in private framework agent shows v3.9.0 | Cosmetic — public repos are v3.10.0 | Will be fixed in next private agent sync |
| `SOP_specification_enhancement.md` still at v1.0.0 | Content is v1.1.0 but header not bumped | Low priority — version header update |
| AGENTS.md Skill Routing: 0/12 templates have `/aget-enhance-spec` entry | L629 gap | Address in future template sweep |
| Some fleet agents use deprecated `wake_up.py` path `.aget/patterns/session/wake_up.py` | Canonical path is `scripts/wake_up.py` (L717, #608) | Agents will rationalize deprecated path as "expected" — check explicitly during spot-checks |
| Spec YAML file renames may be missed during upgrade | Skill rename R4-R6 needs matching spec rename (L590) | Step 5.5 added to upgrade guide; verify with `ls .aget/specs/skills/ \| grep capture` |

---

## Pilot Tracking

| Fleet | Supervisor | Agents | Status | Date | Notes |
|-------|-----------|--------|--------|------|-------|
| (your fleet) | (your supervisor) | —/— | — | — | — |

---

## Post-Release Validation Results

| Check | Result | Notes |
|-------|--------|-------|
| Version consistency (27 files) | PASS | `--check 3.10.0` exit 0 |
| CHANGELOG entries (13 repos) | PASS | validate_changelogs.py 13/13 |
| Content sync (3 pairs) | PASS | validate_content_sync.py 3/3 MATCH |
| Contract tests | 140/140 | All passing (skip resolved 2026-03-22) |
| Tags | PASS | v3.10.0 annotated tag in aget/ |

---

## References

- [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) - Full v3.10.0 changes
- [release-notes/v3.10.0.md](https://github.com/aget-framework/aget/blob/main/release-notes/v3.10.0.md) - Deep release notes
- [UPGRADING.md](https://github.com/aget-framework/aget/blob/main/docs/UPGRADING.md) - Migration procedures
- [SOP_fleet_migration.md](https://github.com/aget-framework/aget/blob/main/sops/SOP_fleet_migration.md) - Fleet coordination

---

## Handoff Protocol

**From**: aget-framework
**To**: (your supervisor agent)
**Date**: 2026-03-21

### Acknowledgment

- [ ] Governance Checklist completed
- [ ] Acknowledged by: ___
- [ ] Date: ___
- [ ] Fleet broadcast sent: ___

### Completion Response

After fleet upgrade, respond with:
- Total upgraded / total fleet
- V-test pass rate (per Smoke Test Checklist above)
- Plan revision count (target: <=1 — if >1, feedback appreciated for L613)
- Any archetype variations not documented in this handoff
- Follow-on work identified

---

*RELEASE_HANDOFF_v3.10.0.md*
*Generated: 2026-03-21 | Hotfixed: 2026-03-21 (HFX-001 Gate 0, HFX-002 Gates 0-2)*
*Per L511/R-REL-019 | Template: TEMPLATE_RELEASE_HANDOFF v2.1.0*
*Templates pushed: 2026-03-21 (12/12, D71 + Completion Signal — HFX-002 Gate 3)*
*Stability certified: 2026-03-22 (Phase 7.4, L721). Validation: 140/140. Deployment: 31/31 local, 0 rollbacks. Parity: 12/12 templates. 0 open hotfixes. Cleared for remote fleet announcement.*
