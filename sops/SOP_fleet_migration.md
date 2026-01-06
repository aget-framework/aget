# SOP: Fleet Migration

**Version**: 1.0.0
**Created**: 2026-01-05
**Owner**: private-supervisor-AGET
**Related**: L455 (AGENTS.md Invocation Verification), L457 (Cross-Machine Pre-Flight), AGET_RELEASE_SPEC, PROJECT_PLAN_fleet_v3.2_migration.md

---

## Purpose

Standard operating procedure for migrating fleet agents to new AGET framework versions. Ensures consistent deployment of version updates, session scripts, and validation across all active agents.

---

## Scope

**Applies to**: Fleet-wide version migrations (minor and major releases)

**Covers**:
- Version.json updates across fleet
- AGENTS.md @aget-version updates
- Session script deployment (wake_up.py, wind_down.py, aget_housekeeping_protocol.py)
- L455 AGENTS.md Invocation Verification
- FLEET_STATE.yaml updates

**Does NOT cover**:
- Framework/template releases (see SOP_release_process.md)
- Single-agent migrations
- Breaking changes requiring code modifications

---

## Prerequisites

Before starting Fleet_Migration:

1. **Framework release complete**: Target version released via SOP_release_process.md
2. **Scripts available**: Session scripts exist in framework at target version
3. **Fleet state known**: FLEET_STATE.yaml reflects current fleet
4. **Git access**: Push access to all fleet repositories

---

## Procedure

### Phase 0: Pre-Migration Verification

**Objective**: Confirm framework and fleet readiness

#### V0.1: Verify Framework Version
```bash
python3 -c "import json; print(json.load(open('~/github/aget-framework/aget/.aget/version.json'))['aget_version'])"
```
**Expected**: Target version (e.g., 3.2.1)

#### V0.2: Verify Script Availability
```bash
ls ~/github/aget-framework/aget/scripts/{wake_up,wind_down,aget_housekeeping_protocol}.py
```
**Expected**: All three scripts present

#### V0.3: Read Fleet State
```bash
python3 -c "import yaml; f=yaml.safe_load(open('~/.../FLEET_STATE.yaml')); print(f'Active: {f[\"metadata\"][\"active_agents\"]}')"
```
**Expected**: Known agent count

**Decision_Point**: Framework ready? [GO/NOGO]

---

### Phase 1: Pilot Migration (Risk Validation)

**Objective**: Validate migration approach on representative agents

**Selection Criteria** (3 agents minimum):
- 1 agent from Main portfolio (typical worker)
- 1 agent from high-sensitivity portfolio (e.g., CCB)
- 1 agent from secondary portfolio (e.g., RKB)

#### Gate 1.1: Pilot Agent Migration

For each pilot agent:

```bash
AGENT_PATH=~/github/{agent-name}

# 1. Create scripts directory if needed
mkdir -p $AGENT_PATH/scripts

# 2. Deploy session scripts
cp ~/github/aget-framework/aget/scripts/wake_up.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/wind_down.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/aget_housekeeping_protocol.py $AGENT_PATH/scripts/

# 3. Update version.json
sed -i '' 's/"aget_version": "[^"]*"/"aget_version": "X.Y.Z"/' $AGENT_PATH/.aget/version.json

# 4. Update AGENTS.md @aget-version
sed -i '' 's/@aget-version: .*/@aget-version: X.Y.Z/' $AGENT_PATH/AGENTS.md
```

#### Gate 1.2: L455 Verification (V-MIG-AGENTS Tests)

```bash
# V-MIG-AGENTS.1: No stale patterns
! grep -q "sanity-check" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: L455 violation"

# V-MIG-AGENTS.2: v3.1+ flags documented
grep -q "\-\-json\|\-\-dir" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: Missing --json docs"

# V-MIG-AGENTS.3: Housekeeping script works
python3 $AGENT_PATH/scripts/aget_housekeeping_protocol.py --json --dir $AGENT_PATH | jq -r '.status'
```
**Expected**: PASS, PASS, healthy/warning

#### Gate 1.3: Pilot Commit

```bash
git -C $AGENT_PATH add -A
git -C $AGENT_PATH commit -m "feat: Migrate to AGET vX.Y.Z

- Deploy session scripts (wake_up.py, wind_down.py, aget_housekeeping_protocol.py)
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
  result=$(python3 $agent/scripts/aget_housekeeping_protocol.py --json --dir $agent 2>&1)
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
git -C ~/github/private-supervisor-AGET add .aget/fleet/FLEET_STATE.yaml
git -C ~/github/private-supervisor-AGET commit -m "feat: Complete Fleet vX.Y.Z Migration"
git -C ~/github/private-supervisor-AGET push
```

#### Gate 5.2: Session Log

Create session log in `sessions/SESSION_YYYY-MM-DD_fleet_vX.Y.Z_migration.md`

#### Gate 5.3: PROJECT_PLAN Finalization (if applicable)

- Mark status: COMPLETE
- Add retrospective section
- Record KR achievement

**Decision_Point**: Project complete? [COMPLETE]

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
- Run: `python3 scripts/aget_housekeeping_protocol.py` (human-readable output)
- Or: `python3 scripts/aget_housekeeping_protocol.py --json` (JSON output)
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

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Version homogeneity | 100% | All agents at target version |
| Validation passing | 100% | All housekeeping --json pass |
| L455 compliance | 100% | No stale invocation patterns |
| Zero regressions | 0 failures | No broken deployments |

---

## References

- AGET_RELEASE_SPEC.md (version types, deployment scope)
- SOP_release_process.md (framework releases - precedes fleet migration)
- L455: AGENTS.md Invocation Verification
- L457: Cross-Machine Pre-Flight
- PROJECT_PLAN_fleet_v3.2_migration.md (graduation source)

---

## Changelog

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
