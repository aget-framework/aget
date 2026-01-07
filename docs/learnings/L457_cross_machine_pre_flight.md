# L457: Cross-Machine Pre-Flight

## Problem

When migrating agents on a different machine from where the framework was developed, stale local framework state causes migration failures.

**Example Failure**:
```
Agent: "I need to migrate to v3.2.1"
Agent: *studies framework*
Agent: "v3.2.1 doesn't exist in the framework"
User: "But it was released yesterday..."
```

**Root Cause**: Agent studied a stale local framework clone that hadn't been synced.

**Impact**:
- Migration blocked by phantom "version not found" errors
- ~15-30 minutes debugging before realizing framework is stale
- Agent may incorrectly report capabilities or version availability
- Multi-machine fleets have inconsistent framework state

## Learning

**Before migration on any machine, sync the framework repo and re-study.**

The pattern "study once, migrate forever" fails in distributed environments. Framework state must be verified fresh before each migration session.

## Protocol

### Pre-Migration Verification

```bash
# 1. Navigate to framework repo
cd ~/github/aget-framework/aget  # or ~/code/gmelli/aget

# 2. Verify remote is configured
git remote -v
# Expected: origin  git@github.com:aget-framework/aget.git

# 3. If SSH fails, use HTTPS
git remote set-url origin https://github.com/aget-framework/aget.git

# 4. Fetch and check for updates
git fetch origin
git log origin/main --oneline -5

# 5. CRITICAL: Pull latest
git pull origin main

# 6. Verify framework version
cat .aget/version.json | grep aget_version
# Expected: Current release version
```

### Post-Sync Agent Instructions

After syncing framework:
1. Agent MUST re-study before migration
2. Previous context about "version X doesn't exist" is now stale
3. Run wake-up or study-up to refresh context

```
User: "study up, focus on: v3.2 migration"
```

## V-Tests

```bash
# V-PRE.1: Framework synced to expected version
LOCAL=$(cat .aget/version.json | grep -o '"[0-9.]*"' | head -1)
EXPECTED="3.2"  # adjust to current release
echo $LOCAL | grep -q "$EXPECTED" && echo "PASS" || echo "FAIL: framework stale"

# V-PRE.2: No uncommitted changes blocking pull
git status --short | grep -v '^??' | wc -l | grep -q '^0$' && echo "PASS" || echo "FAIL: uncommitted changes"

# V-PRE.3: Remote is reachable
git ls-remote origin HEAD > /dev/null 2>&1 && echo "PASS" || echo "FAIL: remote unreachable"
```

## Evidence

**Discovery**: During cross-machine fleet migration coordination

**Observed Pattern**: Agent on Machine B reported "v3.2.1 doesn't exist" while Machine A had successfully released it. Root cause: Machine B's framework clone was 2 weeks stale.

**Resolution Time Before L457**: ~30 minutes (debugging, hypothesis testing)
**Resolution Time After L457**: ~2 minutes (run pre-flight, sync, re-study)

## Integration Points

- **FLEET_MIGRATION_GUIDE_v3.md**: "Cross-Machine Pre-Flight" section
- **SOP_fleet_migration.md**: Phase 0 prerequisite checks
- **Multi-supervisor coordination**: Both supervisors run pre-flight before migration

## Anti-Patterns

| Anti-Pattern | Description | Fix |
|--------------|-------------|-----|
| Assume sync | Trust that framework is current without checking | Run V-PRE.1 |
| Study once | Agent studied framework weeks ago, doesn't re-study | Re-study after pull |
| Skip verification | Jump straight to migration without pre-flight | Run full V-PRE suite |
| Ignore remote | Work offline assuming local is sufficient | Run V-PRE.3 |

## Path Variations

Different machines may clone framework to different paths:

| Machine | Typical Path |
|---------|--------------|
| Personal laptop | `~/github/aget-framework/aget/` |
| Work laptop | `~/code/gmelli/aget/` |
| Server | `/opt/aget-framework/aget/` |

**Key**: The path doesn't matter as long as it's the same `aget-framework/aget` repository. Verify with:
```bash
git -C /your/path remote -v | grep aget-framework/aget
```

## Impact

| Metric | Before L457 | After L457 |
|--------|-------------|------------|
| Stale framework incidents | Recurring | Prevented |
| Debug time per incident | ~30 min | ~2 min |
| Multi-machine coordination | Ad-hoc | Formalized |

## Related Learnings

- L455: Migration AGENTS.md Invocation Gap
- L015: Cross-Laptop Migration Handoff

---

*Framework learning for cross-machine migration coordination*
*Referenced by: FLEET_MIGRATION_GUIDE_v3.md, SOP_fleet_migration.md*
