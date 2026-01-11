# Fleet Instance_Migration Guide v3.0

**Version**: 1.4.0
**Date**: 2026-01-11
**Updated**: CAP-MIG-017 Cross-Machine Pre-Flight generalization (industry patterns, Quick Reference Card)
**Owner**: aget-framework
**Implements**: CAP-MIG-001 (Instance_Migration), CAP-MIG-015 (Behavioral_Validation), CAP-MIG-017 (Remote Supervisor Upgrade)
**Location**: `aget/docs/FLEET_MIGRATION_GUIDE_v3.md`

---

## Purpose

Supervisor guide for migrating agent fleets from v2.x to v3.0 5D Composition Architecture.

---

## Prerequisites

```bash
# Sync framework (required before migration)
# See "Common Framework Locations" in Cross-Machine Pre-Flight section
cd /path/to/your/aget-framework/aget
git pull origin main

# Verify version
cat .aget/version.json | grep aget_version
# Expected: Current release version (e.g., "3.3.0")
```

---

## Cross-Machine Pre-Flight (L457, CAP-MIG-017)

**When This Applies**: Migration executed on different machine from framework development.

**Key Issue**: Your local framework clone may be stale, causing agents to incorrectly report "version X.X doesn't exist."

### When to Run Pre-Flight

**Run when ANY apply:**
- Switching between machines (work ↔ personal)
- Framework not synced in >7 days
- Agent reports "version doesn't exist" after framework update
- First migration on new machine

**Skip if:**
- Same machine, continuous work session
- Framework synced this session
- Agent already studied current framework version

### Common Framework Locations

| Environment | Typical Path |
|-------------|--------------|
| Personal laptop | `~/github/aget-framework/aget/` |
| Work laptop | `~/code/aget-framework/aget/` |
| Server deployment | `/opt/aget/` or `/srv/aget/` |
| CI/CD | `$WORKSPACE/aget-framework/aget/` |

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  CROSS-MACHINE PRE-FLIGHT - QUICK REFERENCE                 │
├─────────────────────────────────────────────────────────────┤
│  1. HEALTH CHECK                                            │
│     cd /path/to/your/aget-framework/aget                    │
│     git ls-remote origin HEAD                               │
│                                                             │
│  2. SYNC FRAMEWORK                                          │
│     git fetch origin && git pull origin main                │
│                                                             │
│  3. VERIFY VERSION                                          │
│     cat .aget/version.json | grep aget_version              │
│                                                             │
│  4. RE-STUDY (if agent previously studied stale framework)  │
│     User: "study up, focus on: vX.Y upgrade"                │
│                                                             │
│  5. PROCEED WITH MIGRATION                                  │
│     Follow standard migration procedure below               │
└─────────────────────────────────────────────────────────────┘
```

### Pre-Flight Steps

```bash
# 0. Find your framework clone (see Common Framework Locations above)
cd /path/to/your/aget-framework/aget

# 1. HEALTH CHECK: Verify remote is reachable
git ls-remote origin HEAD > /dev/null 2>&1 && echo "PASS: Remote reachable" || echo "FAIL: Check network/SSH"

# 2. Verify framework repo has remote configured
git remote -v
# Expected: origin  git@github.com:aget-framework/aget.git (fetch/push)

# 3. If SSH fails, use HTTPS
git remote set-url origin https://github.com/aget-framework/aget.git

# 4. Verify can fetch
git fetch origin

# 5. Verify remote has newer commits
git log origin/main --oneline -5

# 6. SYNC: Pull latest framework (CRITICAL - was missing pre-L457)
git pull origin main

# 7. Verify framework version after sync
cat .aget/version.json | grep aget_version
# Expected: Current release version (e.g., "3.3.0")
```

### Post-Sync: State Verification

After syncing framework, agents MUST re-study before migration:

```
⚠️ STATE VERIFICATION (Industry Pattern: Check last action before continuing)

If agent previously studied with stale framework:
   - Agent context is now INVALID
   - Agent may incorrectly report "version X.X doesn't exist"
   - Solution: Re-run study/research phase after git pull
   - Pattern: "study up, focus on: vX.Y upgrade"

This ensures agent has current framework knowledge before proceeding.
```

### Stale Context Symptoms

Agent may exhibit:
- "I don't see version X.Y in the framework" (version exists after sync)
- "File Z doesn't exist" (file present after sync)
- References outdated protocol names or deprecated features
- Proposes changes already in current framework

**Cause**: Agent studied pre-sync, framework updated, agent context now stale

**Solution**: User says `"study up, focus on: vX.Y upgrade"`

### V-Tests

```bash
# V-PRE.0: Health check (remote reachable)
git ls-remote origin HEAD > /dev/null 2>&1 && echo "PASS: V-PRE.0" || echo "FAIL: V-PRE.0 - Remote unreachable"

# V-PRE.1: Framework synced to expected version
LOCAL=$(cat .aget/version.json | grep -o '"[0-9.]*"' | head -1)
EXPECTED="3.3"  # adjust to current release
echo $LOCAL | grep -q "$EXPECTED" && echo "PASS: V-PRE.1" || echo "FAIL: V-PRE.1 - Framework stale ($LOCAL vs $EXPECTED)"

# V-PRE.2: No uncommitted changes blocking pull
git status --short | grep -v '^??' | wc -l | grep -q '^0$' && echo "PASS: V-PRE.2" || echo "FAIL: V-PRE.2 - Uncommitted changes"

# V-PRE.3: On main branch
BRANCH=$(git branch --show-current)
[ "$BRANCH" = "main" ] && echo "PASS: V-PRE.3" || echo "FAIL: V-PRE.3 - Not on main ($BRANCH)"
```

### Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "Remote unreachable" | Network/SSH issue | Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git` |
| "Framework stale" | Pull failed | Check for merge conflicts, stash changes |
| Agent says "version doesn't exist" | Studied with stale framework | Re-study after pull: `"study up, focus on: vX.Y upgrade"` |
| "Uncommitted changes" | Local modifications | `git stash` or commit first |

See: L457 (Remote Supervisor Upgrade Pattern), CAP-MIG-017 (Remote Supervisor Upgrade)

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **AGET_MIGRATION_SPEC.md** | `aget/specs/` | CAP-MIG-* requirements |
| **AGET_INSTANCE_SPEC.md** | `aget/specs/` | Instance structure requirements |
| **AGET_SOP_SPEC.md** | `aget/specs/` | SOP vocabulary requirements |
| **INVENTORY.md** | `aget/validation/` | All validators with usage |
| **migrate_instance_to_v3.py** | `aget/scripts/` | Migration automation |

---

## Migration Script

### Setup

```bash
# Set framework path (adjust to your environment - see Common Framework Locations)
FRAMEWORK="/path/to/your/aget-framework/aget"
```

### Single Agent

```bash
python3 $FRAMEWORK/scripts/migrate_instance_to_v3.py /path/to/agent \
  --archetype <archetype> \
  --specialization <specialization> \
  --north-star "Agent purpose statement" \
  --execute
```

### Archetypes

| Archetype | Use For |
|-----------|---------|
| `supervisor` | Fleet coordination agents |
| `advisor` | Strategic guidance agents |
| `consultant` | Domain expertise agents |
| `developer` | Code/product agents |
| `operator` | Operations/infrastructure agents |
| `worker` | Task execution agents |
| `analyst` | Data analysis agents |
| `researcher` | Research/investigation agents |
| `reviewer` | Review/audit agents |
| `spec-engineer` | Specification agents |
| `architect` | Architecture/design agents |
| `executive` | Executive function agents |

### Dry-Run First

```bash
# Preview changes (no --execute)
python3 $FRAMEWORK/scripts/migrate_instance_to_v3.py /path/to/agent \
  --archetype advisor \
  --specialization domain-advisor \
  --north-star "Purpose"

# Review output, then add --execute
```

---

## Post-Migration Validation Suite

Run **all 5 validators** per CAP-MIG-015:

```bash
# Set paths (adjust to your environment)
FRAMEWORK="/path/to/your/aget-framework/aget"
AGENT_PATH="/path/to/agent"

# 1. Structural Validation (24 checks)
python3 $FRAMEWORK/validation/validate_template_instance.py $AGENT_PATH
# Expected: 24/24 PASS

# 2. Naming Conventions
python3 $FRAMEWORK/validation/validate_naming_conventions.py $AGENT_PATH
# Expected: ✅ PASS (pre-existing violations acceptable)

# 3. Version Consistency
python3 $FRAMEWORK/validation/validate_version_consistency.py $AGENT_PATH
# Expected: ✅ PASS

# 4. Legacy File Audit (L376)
find $AGENT_PATH/.aget -name "agent_manifest.yaml" 2>/dev/null
# Expected: No output (no legacy files)

# 5. Contract Tests (if available)
[ -d "$AGENT_PATH/tests" ] && python3 -m pytest $AGENT_PATH/tests/test_identity_contract.py -v
# Expected: All tests pass
```

---

## Batch Validation (Fleet)

```bash
# Set framework path (adjust to your environment)
FRAMEWORK="/path/to/your/aget-framework/aget"

# Example: Validate all agents in a directory
# Adjust AGENT_DIR to your agent location pattern
AGENT_DIR="/path/to/your/agents"

for agent in $AGENT_DIR/private-*-aget $AGENT_DIR/private-*-AGET; do
  [ -d "$agent" ] || continue
  echo "=== $(basename $agent) ==="
  python3 $FRAMEWORK/validation/validate_template_instance.py "$agent" 2>/dev/null | tail -3
  python3 $FRAMEWORK/validation/validate_version_consistency.py "$agent" 2>/dev/null | tail -1
done

# For multiple portfolios, repeat with different AGENT_DIR values
# Example:
#   AGENT_DIR="/path/to/portfolio-1" && for agent in ...
#   AGENT_DIR="/path/to/portfolio-2" && for agent in ...
```

---

## Content Archaeology (Fix #15)

During migration, you may discover accumulated non-standard content:

| Discovery | Example | Recommendation |
|-----------|---------|----------------|
| Non-standard directories | `org-knowledge/`, `notes/` | Document but don't reorganize |
| Legacy naming patterns | `SESSION_NOTES/` vs `sessions/` | Add to remediation backlog |
| Orphan files | `.aget/specs/DEPRECATED_*.md` | Archive or remove post-migration |

**Guidance**: Keep migration focused on structural changes. Create separate PROJECT_PLAN for content reorganization if discoveries are extensive.

See: L016 (Content Archaeology During Migration)

---

## Post-Migration Customization (Fix #15)

⚠️ **Migration creates files with placeholder content that needs customization:**

| File | Review For |
|------|------------|
| `governance/CHARTER.md` | IS/IS NOT definition |
| `governance/MISSION.md` | North star, goals |
| `governance/SCOPE_BOUNDARIES.md` | Authority limits |
| `.aget/identity.json` | `north_star` field |
| `.aget/persona/archetype.yaml` | `archetype` field |
| `manifest.yaml` | `specialization`, `north_star` |

**Minimum action**: Verify `archetype` and `north_star` are correct before committing.

---

## AGENTS.md Invocation Verification (L455)

⚠️ **After script migration, AGENTS.md training instructions must match new CLI interfaces.**

### Problem (L455)

Migration often copies new scripts (wake_up.py, wind_down.py, housekeeping) but leaves stale CLI invocations in AGENTS.md. The agent's first session then fails:

```
User: "sanity check"
Agent: python3 scripts/aget_housekeeping_protocol.py sanity-check
Script: error: unrecognized arguments: sanity-check
```

### V-Tests

```bash
AGENT_PATH="/path/to/agent"

# V-MIG-AGENTS.1: No stale CLI patterns
! grep -q "sanity-check" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: stale sanity-check"

# V-MIG-AGENTS.2: v3.1+ invocations documented
grep -q "\-\-json\|\-\-dir" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: v3.1 flags missing"

# V-MIG-AGENTS.3: Documented commands actually work
cd $AGENT_PATH && python3 scripts/aget_housekeeping_protocol.py --json > /dev/null && echo "PASS" || echo "FAIL"
```

### Checklist Addition

Add to per-agent migration:

- [ ] AGENTS.md invocations updated to match v3.1+ script interfaces
- [ ] No stale subcommand references (sanity-check, etc.)
- [ ] Documented commands tested and working

### Correct v3.1 Invocations

| Script | Invocation |
|--------|------------|
| wake_up.py | `python3 scripts/wake_up.py --json` |
| wind_down.py | `python3 scripts/wind_down.py --json --notes "session notes"` |
| housekeeping | `python3 scripts/aget_housekeeping_protocol.py --json` |

See: L455 (Migration AGENTS.md Invocation Gap), R-MIG-AGENTS-001

---

## Troubleshooting

### "identity.json not found"

```bash
cat > $AGENT_PATH/.aget/identity.json << 'EOF'
{
  "name": "agent-name",
  "north_star": "Agent purpose"
}
EOF
```

### "governance/ not found"

```bash
mkdir -p $AGENT_PATH/governance
touch $AGENT_PATH/governance/{CHARTER,MISSION,SCOPE_BOUNDARIES}.md
```

### Version mismatch after migration

```bash
# Check AGENTS.md has @aget-version tag
grep "@aget-version" $AGENT_PATH/AGENTS.md
# Should show: @aget-version: 3.0.0-beta.3 (or later)

# If missing, script should have added it. Manual fix:
# Add "@aget-version: 3.0.0-beta.3" as line 3 of AGENTS.md
```

### Legacy agent_manifest.yaml found

```bash
# Archive and remove (L376)
mkdir -p $AGENT_PATH/.aget/archive
mv $AGENT_PATH/.aget/agent_manifest.yaml $AGENT_PATH/.aget/archive/
```

---

## Multi-Supervisor Coordination (L458)

When multiple supervisors manage different fleet segments:

### Sequential Validation Pattern

```
Supervisor 1 (smaller fleet) executes first
    ↓
[VALIDATION GATE] - All V-tests pass?
    ↓
[HANDOFF SIGNAL] → Supervisor 2
    ↓
Supervisor 2 pilot (cross-portfolio)
    ↓
[VALIDATION GATE] - Pilot successful?
    ↓
Supervisor 2 main fleet rollout
```

### Handoff Signals

| Signal | Meaning |
|--------|---------|
| "Remote complete - GO for local" | Pattern validated, proceed |
| "Remote complete with findings: [X]" | Issues to address first |
| "HOLD" | Stop all migration |

### Pilot Selection

Select 3-5 agents across different portfolios for pilot:
- Validates pattern works across portfolio boundaries
- Catches portfolio-specific issues early
- Example: 1 Main + 1 CCB + 1 RKB

### Script Source Chain

```
✅ CORRECT: Framework → Fleet (direct)
   $FRAMEWORK/scripts/ → agent/scripts/

❌ WRONG: Framework → Supervisor → Fleet (chain)
   May propagate supervisor-specific modifications
```

See: L458 (Fleet Migration Coordination Pattern)

---

## Completion Checklist

- [ ] Framework synced to latest (`git pull origin main`)
- [ ] Each agent migrated with script (`--execute`)
- [ ] Each agent passes Structural_Validation (24/24)
- [ ] Each agent passes Version_Consistency
- [ ] No legacy `agent_manifest.yaml` files remain
- [ ] **AGENTS.md invocations match v3.1+ script interfaces (L455)**
- [ ] Commit migrations per agent

---

## Known Issues

| Issue | Classification | Action |
|-------|---------------|--------|
| Naming convention violations | Pre-existing debt | P3, remediate later |
| Legacy agents (no governance) | Excluded | No migration needed |
| PROJECT_PLAN naming restriction | Documentation | See note below |

### PROJECT_PLAN Naming (Fix #15)

Pattern `PROJECT_PLAN_[\w]+_v\d+\.\d+\.md` doesn't allow dots in name portion:

```
❌ PROJECT_PLAN_fleet_migration_v3.0_v1.0.md   (dots in "v3.0")
✅ PROJECT_PLAN_fleet_v3_migration_v1.0.md    (no dots before version)
✅ PROJECT_PLAN_fleet_migration_v1.0.md       (simple name)
```

**Workaround**: Replace dots with underscores in name portion.

---

## References

- L015: Cross-Laptop Migration Handoff
- L016: Content Archaeology During Migration
- L017: v3.0 Framework Recommendations
- L376: Legacy File Version Sync
- L377: Validation Suite Orchestration Gap
- L395: Instance v3.0 Migration Pattern
- L400: Conceptual vs Structural Migration
- **L455: Migration AGENTS.md Invocation Gap**
- **L457: Remote Supervisor Upgrade Pattern**
- CAP-MIG-014: Legacy File Handling
- CAP-MIG-015: Behavioral_Validation Requirement
- **R-MIG-AGENTS-001: AGENTS.md Training Coherence**

---

*FLEET_MIGRATION_GUIDE_v3.md — Supervisor guide for v3.0 fleet migration*
*Syncs to all machines via `git pull origin main`*
