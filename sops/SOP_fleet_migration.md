# SOP: Fleet Migration

**Version**: 1.6.0
**Status**: Active
**Created**: 2026-01-05
**Updated**: 2026-05-02
**Owner**: aget-framework
**Implements**: CAP-MIG-017 (Remote Supervisor Upgrade), SD-3 wave-sequencing (v1.6.0)
**Related**: L455 (AGENTS.md Invocation Verification), L457 (Cross-Machine Pre-Flight), AGET_RELEASE_SPEC, PROJECT_PLAN_fleet_v3.2_migration.md

---

## Purpose

Standard operating procedure for migrating fleet agents to new AGET framework versions. Ensures consistent deployment of version updates, session scripts, and validation across all active agents.

---

## Execution Model (Centralized by Default)

Fleet migration is **centralized by default**: the supervisor executes all agent upgrades in a single coordinated session. Distributed execution (each agent self-upgrades) is used only when agent count or machine topology makes centralized execution impractical, and requires principal approval.

| Model | When | Mechanism |
|-------|------|-----------|
| **Centralized** (default) | Fleet ≤ 40 agents, single supervisor machine | Supervisor iterates agents directly |
| **Distributed** | Fleet > 40, multi-machine, or principal directed | Each agent receives REMOTE_MIGRATION_MESSAGE; supervisor coordinates |

---

## Wave Sequencing

Fleet migration proceeds in three sequential waves. Each wave SHALL complete before the next begins; wave-boundary V-tests are blocking gates.

| Wave | Scope | Purpose | Sequencing Rule |
|------|-------|---------|-----------------|
| **Wave 0** | Supervisor self-upgrade | Validate target version on the agent that will execute the rest of the migration | MUST land before any Wave 1 work; supervisor cannot orchestrate an upgrade it has not itself completed |
| **Wave 1** | Pilot agent(s) — typically 1-3 representative agents | Risk validation: surface BC-NNN violations, V-test gaps, or framework-defects before full-fleet exposure | MUST land + soak ≥ 1 session before Wave 2; rollback at this stage is bounded to the pilot set |
| **Wave 2** | Remainder of fleet (main + secondary portfolios) | Full-fleet propagation | Proceeds only after Wave 1 success; portfolio batches sequenced per Phase 2-3 |

### Wave-to-Phase Mapping

| Wave | Phases (this SOP) | Boundary V-test |
|------|-------------------|-----------------|
| Wave 0 | Phase 0.5 (Remote Supervisor Pre-Flight) + supervisor's own version-bump | V0.5.3 (Version Verification on supervisor) |
| Wave 1 | Phase 1 (Gate 1.1 → Gate 1.4) | Gate 1.4 (Pilot Commit) |
| Wave 2 | Phase 2 + Phase 3 + Phase 4 | Gate 4.2 (Version Consistency Check across remaining fleet) |

### Why Sequenced (Not Parallel)

- **Wave 0 before Wave 1**: A supervisor running v(N-1) cannot reliably orchestrate v(N) on its workers — it lacks the target version's specs, scripts, and V-tests. Self-upgrade first is the bootstrapping invariant.
- **Wave 1 before Wave 2**: Pilots surface release-defects at bounded blast radius (1-3 agents). Skipping Wave 1 trades observability for speed; the trade is rarely worth it once fleet > 5 agents. Past cycles show 60-80% of release-defects surface in Wave 1.
- **No Wave-skip without principal approval**: An "experienced" release where Wave 1 feels redundant is exactly when L92 (Premature Victory) is most likely. Document any wave-skip in the migration session log with explicit principal approval citation.

### Wave-Boundary Rollback

If a wave fails its boundary V-test:
- **Wave 0 fail**: Halt migration; supervisor cannot proceed. Triage on supervisor itself.
- **Wave 1 fail**: Rollback pilot(s) per Rollback Criteria (see below); file release-blocking issue; do NOT enter Wave 2.
- **Wave 2 fail (per-portfolio batch)**: Halt batch; complete in-flight agents; rollback failed agents; surface to principal for triage decision (continue with other batches vs. halt all of Wave 2).

---

## Mandatory vs Optional Change Classification

Not all upgrade changes carry the same obligation. This classification determines which steps are blocking and which are contextual.

| Class | Definition | V-test Requirement | Example |
|-------|-----------|-------------------|---------|
| **Mandatory** | Required for version compliance. Agent is non-compliant at target version without these changes. | BLOCKING — must PASS before declaring agent complete | `version.json` aget_version field, AGENTS.md @aget-version header, BC-NNN breaking change compliance |
| **Optional** | Capabilities each agent adopts based on context. Non-adoption does not affect version compliance. | Recommended — WARN if missing, not FAIL | New universal skills, new PATTERN_*.md files, new AGENTS.md sections |

**When a release includes breaking changes (BC-NNN)**: BC compliance is automatically Mandatory. Check DEPLOYMENT_SPEC_vX.Y.Z.yaml for the full classification table for each release.

---

## Scope

**Applies to**: Fleet-wide version migrations (minor and major releases)

**Covers**:
- Version.json updates across fleet
- AGENTS.md @aget-version updates
- Session script deployment (wake_up.py, wind_down.py, health_check.py)
- L455 AGENTS.md Invocation Verification
- Mandatory change compliance verification
- FLEET_STATE.yaml / FLEET_REGISTRY updates

**Does NOT cover**:
- Framework/template releases (see SOP_release_process.md)
- Single-agent migrations (use SOP_aget_migrate.md)
- Breaking changes requiring code modifications (see DEPLOYMENT_SPEC_vX.Y.Z.yaml BC-NNN)

---

## Prerequisites

Before starting Fleet_Migration:

1. **Framework release complete**: Target version released via SOP_release_process.md
2. **Scripts available**: Session scripts exist in framework at target version
3. **Fleet state known**: FLEET_STATE.yaml reflects current fleet
4. **Git access**: Push access to all fleet repositories
5. **gh CLI auth verified**: `gh auth status` returns exit 0 (not keyring error)

```bash
# Pre-flight auth smoke-test — catch keyring failures before migration starts
gh auth status && echo "PASS: gh auth" || echo "FAIL: gh auth — check keyring or re-authenticate (gh auth login)"
```

**Warning**: Cloud-hosted agents may return keyring errors on `gh auth status` even when auth is configured. If any agent shows a keyring error, resolve before migration (re-run `gh auth login` on that machine). Undetected auth failures cause silent gh CLI failures during migration.

---

## Procedure

### Phase 0: Pre-Migration Verification

**Objective**: Confirm framework and fleet readiness

#### V0.1: Discover Latest Release
```bash
# Check latest release on GitHub (L723, L755)
gh release list --repo aget-framework/aget --limit 3
```
**Purpose**: Remote fleet supervisors should discover the target version from the release list, not from commit inference. Per L723: release discovery must be explicit, not inferred.

#### V0.2: Verify Framework Version
```bash
python3 -c "import json; print(json.load(open('~/github/aget-framework/aget/.aget/version.json'))['aget_version'])"
```
**Expected**: Target version matching the latest release from V0.1

#### V0.2: Verify Script Availability
```bash
ls ~/github/aget-framework/aget/scripts/{wake_up,wind_down,health_check}.py
```
**Expected**: All three scripts present

#### V0.3: Read Fleet State
```bash
python3 -c "import yaml; f=yaml.safe_load(open('~/.../FLEET_STATE.yaml')); print(f'Active: {f[\"metadata\"][\"active_agents\"]}')"
```
**Expected**: Known agent count

#### V0.4: Check for Late-Created Agents
```bash
# Identify agents created after last migration (may have missed version wave)
LAST_MIGRATION="YYYY-MM-DD"  # Date of previous fleet migration
for agent in ~/github/private-*-aget ~/github/GM-*/private-*-aget; do
  created=$(jq -r '.created // .discovered // "unknown"' $agent/.aget/version.json 2>/dev/null)
  if [[ "$created" > "$LAST_MIGRATION" ]]; then
    echo "LATE: $(basename $agent) created $created"
  fi
done
```
**Expected**: List of agents needing catch-up migration (may be empty)
**Action**: Include late-created agents in Phase 2 batches

**Decision_Point**: Framework ready? [GO/NOGO]

---

### Phase 0.5: Remote Supervisor Pre-Flight (CAP-MIG-017)

**When This Applies**: Migration executed on different machine from framework development.

**Objective**: Ensure local framework clone is synchronized before migration.

**Key Issue**: Your local framework clone may be stale, causing agents to incorrectly report "version X.X doesn't exist."

See: FLEET_MIGRATION_GUIDE_v3.md (Cross-Machine Pre-Flight section), L457

#### V0.5.1: Health Check (Remote Reachable)

```bash
# Find your framework clone (common locations below)
# Personal laptop: ~/github/aget-framework/aget/
# Work laptop: ~/code/aget-framework/aget/
# Server: /opt/aget/ or /srv/aget/
cd /path/to/your/aget-framework/aget

git ls-remote origin HEAD > /dev/null 2>&1 && echo "PASS: V0.5.1" || echo "FAIL: V0.5.1 - Remote unreachable"
```
**Expected**: PASS
**Fix (if FAIL)**: Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git`

#### V0.5.2: Framework Sync

```bash
cd /path/to/your/aget-framework/aget
git fetch origin && git pull origin main
```
**Expected**: Up-to-date or successful pull

#### V0.5.3: Version Verification

```bash
cat /path/to/your/aget-framework/aget/.aget/version.json | grep aget_version
```
**Expected**: Target version (e.g., "3.3.0")

#### V0.5.3b: SUBSTANCE Verification (version label ≠ payload present)

The version reading X.Y.Z confirms the *label* is set — NOT that the deployment contract is published or your source contains the release payload. A version bump does **not** copy new artifacts. Verify substance before migrating (FLEET-UPG-023 lessons):

```bash
FW=/path/to/your/aget-framework
# (a) Deployment contract published (read it — detection clauses + breaking_release):
test -f $FW/aget/DEPLOYMENT_SPEC_vX.Y.Z.yaml && echo "PASS: spec" || echo "FAIL: no DEPLOYMENT_SPEC_vX.Y.Z — STOP, do NOT relabel 'no spec' as version.json"
# (b) Your template source actually CONTAINS the release's new artifacts (list them per release notes):
#     for each new artifact: test -f $FW/template-{archetype}-aget/<path> || echo "FAIL: empty source pulls nothing — STOP"
```
**Expected**: PASS on both. **If FAIL**: STOP — migrating from an empty source, or relabeling a missing contract as a "deviation," are real observed failures (FLEET-UPG-023). Pull/escalate first.

Post-rollout, remember: **version-pass ≠ health-pass** — run the *full* `health_check`, expect pre-existing drift; and L444 coherence is **schema-aware** (manifests differ by archetype — worker top-level `version:` vs researcher `instance.version:`; a uniform grep false-flags).

#### V0.5.4: State Verification (Re-Study)

```
⚠️ If agent previously studied with stale framework:
   - Agent context is now INVALID
   - Agent may incorrectly report "version X.X doesn't exist"
   - Solution: Re-run study/research phase after git pull
   - Pattern: "study up, focus on: vX.Y upgrade"
```

**Decision_Point**: Remote environment ready? [GO/NOGO]

---

### Phase 1: Pilot Migration (Risk Validation)

**Objective**: Validate migration approach on representative agents

**Selection Criteria** (3 agents minimum, L583):
- 1 simple agent (structural validation — does the upgrade script work?)
- 1 high-value agent (signal validation — does it break what matters? e.g., professional-core, cli-aget)
- 1 high-complexity agent (divergence validation — does it handle organic customizations? e.g., supervisor-level skills)

**Anti-pattern**: Selecting only dormant/simple agents optimizes for procedural safety, not validation signal. Pilot evidence must be compelling enough for external fleet deployments.

#### Gate 1.1: Pilot Agent Migration

For each pilot agent:

```bash
AGENT_PATH=~/github/{agent-name}

# 1. Create scripts directory if needed
mkdir -p $AGENT_PATH/scripts

# 2. Deploy session scripts
cp ~/github/aget-framework/aget/scripts/wake_up.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/wind_down.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/health_check.py $AGENT_PATH/scripts/

# 3. Update version.json
sed -i '' 's/"aget_version": "[^"]*"/"aget_version": "X.Y.Z"/' $AGENT_PATH/.aget/version.json

# 4. Update AGENTS.md @aget-version
sed -i '' 's/@aget-version: .*/@aget-version: X.Y.Z/' $AGENT_PATH/AGENTS.md
```

#### Gate 1.2: Skill Content Sync (Conservative Protocol)

**Objective**: Sync framework skill updates to agent instances without destroying organic customizations.

**When this applies**: When the release includes skill SKILL.md changes (check RELEASE_HANDOFF for "skill updates" section).

**Why conservative**: Remote fleets have minimal visibility to outcomes. A blunt overwrite can destroy organic features (evidence-rich mode, custom project types, invocation recording, disable-model-invocation) that the agent developed through use. The classify-archive-diff-merge-verify protocol prevents silent regressions.

**Note**: ~50% of agents have `.claude/` in `.gitignore` (#317). Skill file commits require `git add -f` for these agents.

For each skill with framework updates:

```bash
AGENT_PATH=~/github/{agent-name}
TEMPLATE_PATH=~/github/aget-framework/template-{archetype}-aget
SKILL_NAME=aget-create-project  # Replace per skill

# Step 1: CLASSIFY — detect organic customizations
python3 .aget/patterns/upgrade/pre_sync_check.py \
  --baseline $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/ \
  --instance $AGENT_PATH/.claude/skills/$SKILL_NAME/

# If pre_sync_check unavailable or single-file, classify manually:
diff $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
     $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md | head -40

# Step 2: ARCHIVE — preserve current version before any changes
cp $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
   $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md.pre-vX.Y.Z

# Step 3: CLASSIFY result determines action:
```

| Classification | Organic Customizations? | Action |
|---------------|------------------------|--------|
| **Clean** (identical to prior template) | No | Safe to overwrite: `cp $TEMPLATE_PATH/...SKILL.md $AGENT_PATH/...SKILL.md` |
| **Extension** (template + additions) | Yes | **MERGE**: Add framework updates into agent's file, preserving organic sections |
| **Conflict** (incompatible changes) | Yes | **MANUAL**: Review diff, resolve conflicts, preserve organic intent |

```bash
# Step 4: For CLEAN agents — direct copy
cp $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
   $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md

# Step 4: For EXTENSION/CONFLICT agents — manual merge
# Read both files, identify framework additions vs organic features
# Add framework steps into agent's file preserving organic content

# Step 5: VERIFY — confirm framework updates present AND organic features preserved
echo "=== Framework updates ==="
grep -c "Step 0\|Step 3.6\|Step 3.7\|Step 3.8\|Step 8" \
  $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md
# Expected: 5+ matches for D62

echo "=== Organic features ==="
# Check for agent-specific features (varies per agent)
grep -c "disable-model-invocation\|evidence-rich\|gap\|record_invocation" \
  $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md
# Expected: matches for any organic features the agent had

# Step 6: COMMIT (use -f if .claude/ is gitignored)
git -C $AGENT_PATH add -f .claude/skills/$SKILL_NAME/SKILL.md \
  .claude/skills/$SKILL_NAME/SKILL.md.pre-vX.Y.Z
```

**Decision_Point**: Skill sync verified for pilot agents? [GO/NOGO]

#### Gate 1.3: L455 Verification (V-MIG-AGENTS Tests)

```bash
# V-MIG-AGENTS.1: No stale patterns
! grep -q "sanity-check" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: L455 violation"

# V-MIG-AGENTS.2: v3.1+ flags documented
grep -q "\-\-json\|\-\-dir" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: Missing --json docs"

# V-MIG-AGENTS.3: Housekeeping script works
python3 $AGENT_PATH/scripts/health_check.py --json --dir $AGENT_PATH | jq -r '.status'
```
**Expected**: PASS, PASS, healthy/warning

#### Gate 1.4: Pilot Commit

```bash
git -C $AGENT_PATH add -A
git -C $AGENT_PATH commit -m "feat: Migrate to AGET vX.Y.Z

- Deploy session scripts (wake_up.py, wind_down.py, health_check.py)
- Update version.json to vX.Y.Z
- Update AGENTS.md @aget-version

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Decision_Point**: Pilot successful? [GO/NOGO]

---

### Phase 2: Main Portfolio Migration

**Objective**: Migrate Main portfolio agents (typically largest)

**Batching Strategy**: 3-4 agents per batch for manageable commits

#### Gate 2.N: Batch Migration

For each batch:
1. Deploy scripts to all batch agents
2. Update version.json for all
3. Update AGENTS.md for all
4. Run V-MIG-AGENTS tests for all
5. Fix any L455 violations
6. Commit batch

**Decision_Point**: Main portfolio complete? [GO/NOGO]

---

### Phase 3: Secondary Portfolio Migration

**Objective**: Migrate remaining portfolios (CCB, RKB, PREDICTIONWORKS, etc.)

#### Gate 3.1: Per-Portfolio Batches

Migrate each portfolio as a batch:
- CCB (sensitive): Extra verification
- RKB: Check for symlink edge cases
- PREDICTIONWORKS: Standard procedure

#### Gate 3.2: Archive/Deprecation Handling

If portfolio is deprecated:
```bash
# Option A: Mark delegated in FLEET_STATE
# Option B: Archive to ~/archive/
tar -czvf ~/archive/GM-{PORTFOLIO}-archived-$(date +%Y-%m-%d).tar.gz ~/github/GM-{PORTFOLIO}
rm -rf ~/github/GM-{PORTFOLIO}
```

Update FLEET_STATE.yaml:
```yaml
{portfolio}:
  status: archived
  archived_date: 'YYYY-MM-DD'
  archived_location: ~/archive/{filename}.tar.gz
```

**Decision_Point**: Secondary portfolios complete? [GO/NOGO]

---

### Phase 4: Fleet Validation

**Objective**: Verify fleet-wide consistency

#### Gate 4.1: Batch Housekeeping Validation

```bash
for agent in ~/github/private-*-aget ~/github/GM-*/private-*-aget; do
  result=$(python3 $agent/scripts/health_check.py --json --dir $agent 2>&1)
  status=$(echo "$result" | jq -r '.status')
  echo "$(basename $agent): $status"
done
```
**Expected**: All healthy or warning (no errors)

#### Gate 4.2: Version Consistency Check

```bash
for agent in ~/github/private-*-aget ~/github/GM-*/private-*-aget; do
  ver=$(jq -r '.aget_version' $agent/.aget/version.json)
  echo "$(basename $agent): $ver"
done | grep -v "X.Y.Z" && echo "DRIFT DETECTED" || echo "ALL CONSISTENT"
```
**Expected**: All at target version

#### Gate 4.2.1: Migration History Check (V-MIG-HISTORY)

```bash
# Verify migration_history was updated per-agent
TARGET_VERSION="X.Y.Z"
for agent in ~/github/private-*-aget ~/github/GM-*/private-*-aget; do
  last_to=$(jq -r '.migration_history[-1].to_version // "none"' $agent/.aget/version.json 2>/dev/null)
  if [[ "$last_to" != "$TARGET_VERSION" ]]; then
    echo "MISSING: $(basename $agent) - last recorded: $last_to"
  fi
done
```
**Expected**: All agents show target version in migration_history
**Action**: If gaps found, update version.json migration_history arrays

#### Gate 4.3: FLEET_STATE Update

```bash
# Update all agent versions
sed -i '' 's/version: v.*/version: vX.Y.Z/g' ~/.../FLEET_STATE.yaml

# Update metadata
sed -i '' 's/v3_migration_status:.*/v3_migration_status: complete/' ~/.../FLEET_STATE.yaml
sed -i '' "s/last_updated:.*/last_updated: '$(date +%Y-%m-%d)'/" ~/.../FLEET_STATE.yaml
```

**Decision_Point**: Fleet validated? [GO/NOGO]

---

### Phase 5: Finalization

#### Gate 5.1: Commit FLEET_STATE

```bash
git -C ~/github/my-supervisor-agent add .aget/fleet/FLEET_STATE.yaml
git -C ~/github/my-supervisor-agent commit -m "feat: Complete Fleet vX.Y.Z Migration"
git -C ~/github/my-supervisor-agent push
```

#### Gate 5.2: Session Log

Create session log in `sessions/SESSION_YYYY-MM-DD_fleet_vX.Y.Z_migration.md`

#### Gate 5.3: PROJECT_PLAN Finalization (if applicable)

- Mark status: COMPLETE
- Add retrospective section
- Record KR achievement

#### Gate 5.4: FLEET_REGISTRY Update (BLOCKING Completion Criterion)

FLEET_REGISTRY must be updated before declaring migration complete. This is a **BLOCKING** gate — a migration without FLEET_REGISTRY update is considered incomplete even if all agents are at target version.

```bash
# Update FLEET_REGISTRY with migration record
# Location varies by supervisor; common paths:
# - .aget/fleet/FLEET_REGISTRY.yaml
# - .aget/fleet/FLEET_STATE.yaml (if consolidated)

python3 -c "
import json, yaml, datetime
registry = yaml.safe_load(open('.aget/fleet/FLEET_REGISTRY.yaml'))
registry['last_migration'] = {
  'version': 'X.Y.Z',
  'date': '$(date +%Y-%m-%d)',
  'agent_count': 0,  # fill actual count
  'method': 'centralized'
}
print(yaml.dump(registry))
"
```

**V5.4.1: FLEET_REGISTRY records target version**
```bash
grep "version: X.Y.Z" .aget/fleet/FLEET_REGISTRY.yaml && echo "PASS" || echo "FAIL"
```
**Expected**: PASS
**BLOCKING**: Do NOT mark migration COMPLETE if FAIL.

**Decision_Point**: Project complete? [COMPLETE]

---

## Rollback Criteria

Rollback is triggered when any of the following conditions occur and cannot be resolved within the session:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| V-MIG-AGENTS failures | >10% of fleet fails after remediation | Rollback affected agents to prior version |
| BC-NNN compliance failure | Any agent non-compliant after 2 remediation attempts | Escalate to framework; do not mark complete |
| Health check errors (not warnings) | >5% of fleet shows error | Rollback and investigate root cause |
| gh auth failure (cloud agents) | Any agent cannot authenticate | Pause migration; resolve auth before continuing |

**Rollback procedure** (per-agent):
```bash
AGENT_PATH=~/github/{agent-name}
PRIOR_VERSION="X.Y.Z-1"

# 1. Revert version.json
sed -i '' "s/\"aget_version\": \"[^\"]*\"/\"aget_version\": \"$PRIOR_VERSION\"/" $AGENT_PATH/.aget/version.json

# 2. Revert AGENTS.md
sed -i '' "s/@aget-version: .*/@aget-version: $PRIOR_VERSION/" $AGENT_PATH/AGENTS.md

# 3. Restore prior scripts (from framework git history)
FRAMEWORK_PATH=~/github/aget-framework/aget
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/wake_up.py" > $AGENT_PATH/scripts/wake_up.py
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/wind_down.py" > $AGENT_PATH/scripts/wind_down.py
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/health_check.py" > $AGENT_PATH/scripts/health_check.py

# 4. Commit rollback
git -C $AGENT_PATH add .aget/version.json AGENTS.md scripts/
git -C $AGENT_PATH commit -m "rollback: Revert to AGET v$PRIOR_VERSION (migration issue)"
```

**Partial migration**: If > 50% of agents migrated successfully, do not roll back the successful cohort — document partial state in session log and continue remediation in next session.

---

## Troubleshooting

### L455 Violation (V-MIG-AGENTS.1 FAIL)

**Symptom**: Agent has stale `sanity-check` pattern in AGENTS.md

**Fix**:
1. Remove/replace stale invocations
2. Add Housekeeping Commands section with correct syntax:
```markdown
## Housekeeping Commands

### Sanity Check
When user says "sanity check":
- Run: `python3 scripts/health_check.py` (human-readable output)
- Or: `python3 scripts/health_check.py --json` (JSON output)
```

### Symlink Edge Case

**Symptom**: `mkdir: scripts: Not a directory`

**Fix**:
```bash
rm $AGENT_PATH/scripts  # Remove symlink
mkdir -p $AGENT_PATH/scripts  # Create real directory
```

### Shell Aliasing Issues

**Symptom**: `command not found: mkdir` or `rm` prompts

**Fix**: Use explicit paths:
```bash
/bin/mkdir -p $AGENT_PATH/scripts
/bin/rm -f $AGENT_PATH/scripts
```

### Remote Supervisor Pre-Flight Issues (CAP-MIG-017)

| Problem | Cause | Solution |
|---------|-------|----------|
| V0.5.1 FAIL: Remote unreachable | Network/SSH issue | Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git` |
| V0.5.2 FAIL: Pull failed | Merge conflicts, uncommitted changes | `git stash` or commit first, resolve conflicts |
| V0.5.3 FAIL: Framework stale | Pull failed silently | Check git status, try `git reset --hard origin/main` |
| Agent says "version doesn't exist" | Studied with stale framework | Re-study after pull: `"study up, focus on: vX.Y upgrade"` |
| V0.5.4: Context invalid | Proceeded without re-study | Session restart with fresh study phase |

See: FLEET_MIGRATION_GUIDE_v3.md (Cross-Machine Pre-Flight), L457

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Version homogeneity | 100% | All agents at target version |
| Validation passing | 100% | All housekeeping --json pass |
| L455 compliance | 100% | No stale invocation patterns |
| Zero regressions | 0 failures | No broken deployments |

---

## Post-Migration: Ongoing Health Monitoring

After fleet migration completes, supervisors are recommended to establish a weekly fleet health check routine. Two independent supervisors (main + legalon fleets) converged on the same design independently (L831 cross-fleet spec signal), indicating this is a framework-level best practice.

**Recommended pattern**: Weekly RemoteTrigger agent running:
1. `health_check.py --json` against each agent
2. CORRECTION commit monitor (grep `\(CORRECTION\)` in recent git log)
3. Summary report to supervisor

See: `docs/patterns/PATTERN_weekly_fleet_health_monitor.md` (framework-recommended pattern)

**Prerequisites before deploying the routine**:
- Fix #1166: Remove `Write` tool from routine (not needed for read-only health checks)
- Validate CORRECTION grep pattern: `\(CORRECTION\)` (parenthesized form, not plain `CORRECTION`)
- Confirm auth smoke-test passes on target machine (keyring issue risk)

---

## References

- AGET_RELEASE_SPEC.md (version types, deployment scope)
- SOP_release_process.md (framework releases - precedes fleet migration)
- DEPLOYMENT_SPEC_vX.Y.Z.yaml (mandatory/optional change classification per release)
- L455: AGENTS.md Invocation Verification
- L457: Cross-Machine Pre-Flight
- PATTERN_weekly_fleet_health_monitor.md (post-migration health routine)
- PROJECT_PLAN_fleet_v3.2_migration.md (graduation source)

---

## Changelog

### v1.6.0 (2026-05-02)

- **Added**: Wave Sequencing section — Wave 0 (supervisor self) → Wave 1 (pilots) → Wave 2 (full fleet); wave-to-phase mapping; wave-boundary V-tests; wave-skip prohibition without principal approval; wave-boundary rollback procedure
- **Rationale**: Closes SD-3 wave-sequencing residual surfaced by Gate 1 entry-time scope re-check (F-AUDIT-REL-G1-001, plan v1.0.11). v1.5.0 covered 5/6 SD-3 required sections; wave sequencing was the absent 6th. Sequencing was implicit in Phase 0.5/Phase 1 ordering but not named or constraint-bound.
- **Sources**: VERSION_SCOPE_v3.16.0 row #2 SD-3, plan G1.1 deliverable (PROJECT_PLAN_v3.16.0_release_v1.0.md v1.0.11)

### v1.5.0 (2026-04-26)

- **Added**: Execution Model section — centralized by default (principal decision 2026-04-26); distributed requires explicit principal approval
- **Added**: Mandatory vs Optional Change Classification section — Mandatory (BLOCKING V-tests), Optional (WARN, not FAIL); references DEPLOYMENT_SPEC_vX.Y.Z.yaml
- **Added**: Prerequisites item 5 — gh auth smoke-test; addresses cloud-hosted keyring failure risk (FLEET-UPG-014 finding)
- **Added**: Gate 5.4: FLEET_REGISTRY Update as BLOCKING completion criterion (FLEET-UPG-014 D1 gap)
- **Added**: Rollback Criteria section — 4 triggers, per-agent rollback procedure, partial migration guidance
- **Added**: Post-Migration: Ongoing Health Monitoring section — weekly fleet health monitor recommendation (SD-6; L831 cross-fleet convergence from main + legalon supervisors)
- **Updated**: Scope section — added Mandatory change compliance and FLEET_REGISTRY to Covers; updated Does NOT cover
- **Updated**: References section — added DEPLOYMENT_SPEC and PATTERN_weekly_fleet_health_monitor
- Implements SD-3, SD-4 (VERSION_SCOPE_v3.16.0 directives 2026-04-26)

### v1.3.0 (2026-03-14)

- Added Gate 1.2: Skill Content Sync (Conservative Protocol)
- 6-step classify-archive-diff-merge-verify-commit protocol
- Clean/Extension/Conflict classification determines sync strategy
- Preserves organic customizations during framework skill updates
- Documents .claude/ gitignore workaround (git add -f, #317)
- Renumbered Gates 1.2→1.3, 1.3→1.4
- Implements #441 (SOP skill sync phase gap)
- Validated by: FLEET-UPG-006 supervisor D62 self-remediation (2026-03-14)

### v1.2.0 (2026-01-11)

- Added Phase 0.5: Remote Supervisor Pre-Flight (CAP-MIG-017)
- Added V0.5.1-V0.5.4: Health check, framework sync, version verification, state verification
- Added troubleshooting section for remote supervisor issues
- Cross-reference to FLEET_MIGRATION_GUIDE_v3.md Cross-Machine Pre-Flight section
- Implements CAP-MIG-017 (7 requirements)

### v1.1.0 (2026-01-07)

- Added V0.4: Late-created agent detection (Phase 0)
- Added Gate 4.2.1: V-MIG-HISTORY migration_history per-agent check
- Created L455, L457 learning documents in `docs/learnings/`
- Cross-supervisor feedback integration (multi-fleet validation)

### v1.0.0 (2026-01-05)

- Initial SOP graduated from PROJECT_PLAN_fleet_v3.2_migration.md
- Based on patterns from v2.12.0 LTS, v3.0.0, v3.2.1 migrations
- L455 V-MIG-AGENTS tests integrated
- Troubleshooting section from v3.2.1 learnings

---

## Graduation History

```yaml
graduation:
  source: "PROJECT_PLAN_fleet_v3.2_migration.md"
  pattern_executions:
    - v2.12.0_LTS_Convergence (2025-12-26)
    - v3.0.0_Migration (2025-12-27)
    - v3.2.1_Fleet_Migration (2026-01-05)
  trigger: "L436 - Pattern executed successfully 3 times"
  rationale: "Repeatable fleet migration procedure warranted formalization"
```

---

*SOP_fleet_migration.md — Fleet version migration procedure for AGET framework*
