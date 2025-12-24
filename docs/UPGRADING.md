# AGET Framework Upgrade Guide

**Audience**: Users upgrading between framework versions

**Purpose**: Provide step-by-step procedures for safe version upgrades

---

## Quick Upgrade (Non-Breaking Changes)

For minor and patch releases with no breaking changes:

```bash
# 1. Backup current state
cd /path/to/your-agent
git add . && git commit -m "Pre-upgrade snapshot"

# 2. Update version
vim .aget/version.json
# Change: "aget_version": "OLD" → "aget_version": "NEW"

# 3. Verify
python3 -m pytest tests/ -v

# 4. Check wake-up
python3 .aget/patterns/session/wake_up.py
# Should display new version
```

**Time**: ~5 minutes

**Risk**: Low (backwards compatible)

---

## Safe Upgrade Process (All Versions)

### Step 1: Pre-Upgrade Checklist

Before upgrading:

- [ ] Read [CHANGELOG.md](../CHANGELOG.md) for version you're upgrading to
- [ ] Check if major version (vX.0.0) → Read migration guide mandatory
- [ ] Backup your agent: `git add . && git commit -m "Pre-upgrade vOLD"`
- [ ] Note current version: `cat .aget/version.json | grep aget_version`
- [ ] Ensure working directory clean: `git status`

---

### Step 2: Check for Breaking Changes

**Quick Check**:
```bash
# Read CHANGELOG for target version
curl https://raw.githubusercontent.com/aget-framework/aget/main/CHANGELOG.md | grep -A 20 "## \[X.Y.Z\]"
```

**Look For**:
- "Breaking" keyword
- "Removed" section
- "Deprecated" warnings
- "Migration" instructions

**If NO breaking changes**: Proceed with quick upgrade (Step 3)

**If breaking changes**: Read migration guide first (see version-specific guides below)

---

### Step 3: Update version.json

```bash
cd /path/to/your-agent

# Edit version file
vim .aget/version.json
```

Change:
```json
{
  "aget_version": "2.10.0"  ← OLD
}
```

To:
```json
{
  "aget_version": "2.11.0"  ← NEW
}
```

**Also Update** (if applicable):
- `updated`: Current date (YYYY-MM-DD)
- `migration_history`: Add entry for this upgrade

**Example**:
```json
{
  "aget_version": "2.11.0",
  "updated": "2025-12-24",
  "migration_history": [
    "v2.10.0 -> v2.11.0: 2025-12-24 (Memory Architecture + L352)"
  ]
}
```

---

### Step 4: Verify Upgrade

#### Run Contract Tests

```bash
python3 -m pytest tests/ -v
```

**Expected**: All tests pass

**If tests fail**:
- Read test output (what requirement failed)
- Check if migration step missed
- Consult delta spec: `aget/specs/deltas/AGET_DELTA_vX.Y.md`

---

#### Check Wake-Up

```bash
python3 .aget/patterns/session/wake_up.py
```

**Expected Output**:
```
**Session: your-agent-name**
**Version**: vX.Y.Z (YYYY-MM-DD)

Purpose: [your agent purpose]
Ready.
```

**Verify**: Version shows NEW version (vX.Y.Z), not OLD

---

#### Version Consistency (Multi-Template Agents)

If managing multiple templates:

```bash
cd /path/to/your-agent
python3 .aget/patterns/sync/version_consistency.py --expected X.Y.Z
```

**Expected**: "CONSISTENT - All repos at vX.Y.Z"

---

### Step 5: Commit Upgrade

```bash
git add .aget/version.json
git commit -m "chore: Upgrade to vX.Y.Z"
```

**Done!** Upgrade complete.

---

## Rollback Procedure

If upgrade fails or causes issues:

```bash
# 1. Revert version.json
git checkout HEAD~1 .aget/version.json

# 2. Verify rollback
cat .aget/version.json | grep aget_version
# Should show OLD version

# 3. Run tests
python3 -m pytest tests/ -v

# 4. Commit rollback
git commit -m "rollback: Revert to vOLD due to [issue]"
```

**Then**: File issue with upgrade problem details

---

## Version-Specific Migration Guides

### v2.10.0 → v2.11.0

**Release Date**: 2025-12-24

**Theme**: Memory Architecture + L352 Traceability + Version Migration

**Breaking Changes**: None

**New Features**:
- Memory Architecture (L335): 6-layer information model
- L352 Traceability Pattern: Five-tier requirement-to-test traceability
- Configurable wake-up output
- Version migration protocol (R-REL-006)

**Migration Steps**:

1. **Update version.json**:
   ```json
   {
     "aget_version": "2.11.0",
     "updated": "2025-12-24"
   }
   ```

2. **No code changes required** (backwards compatible)

3. **Optional**: Adopt new features
   - Create `.aget/config.json` for configurable wake-up
   - Review L352 pattern for your agent's requirements

4. **Verify**:
   ```bash
   python3 -m pytest tests/ -v
   # All tests should pass (80+ tests)
   ```

**Estimated Time**: 5 minutes (no migration needed)

---

### v2.9.0 → v2.10.0

**Note**: v2.10.0 releases were created retroactively on 2025-12-24. If you're on v2.9.0, you can upgrade directly to v2.11.0 (see above).

**Upgrade Path**: v2.9.0 → v2.10.0 → v2.11.0 OR v2.9.0 → v2.11.0 (direct)

---

### v2.8.0 → v2.9.0

**Note**: v2.9.0 had partial release (4/7 repos). If your template doesn't have v2.9.0 release, upgrade directly to v2.11.0.

---

### Older Versions (v2.7 and earlier)

**Recommendation**: Upgrade to latest stable (v2.11.0+) via incremental steps

**Incremental Upgrade**:
```
v2.7.0 → v2.8.0 → v2.9.0 → v2.10.0 → v2.11.0
```

**Or Direct** (if no breaking changes between):
```
v2.7.0 → v2.11.0
```

**Consult**: [VERSION_HISTORY.md](VERSION_HISTORY.md) for each version's changes

---

## Common Upgrade Scenarios

### Scenario 1: Upgrading New Template Instance

**Situation**: Cloned template yesterday, already at v2.11.0

**Action**: No upgrade needed

**Verification**: `cat .aget/version.json | grep aget_version`

---

### Scenario 2: Pinned to Specific Version

**Situation**: Deliberately staying on v2.9.0 for stability

**Action**: Continue using v2.9.0 (but note: no support, security fixes only)

**When to Upgrade**: When features needed or security concern

---

### Scenario 3: Multiple Templates, Mixed Versions

**Situation**: Some templates at v2.10.0, others at v2.11.0

**Problem**: Version inconsistency can cause compatibility issues

**Solution**: Synchronize all templates to same version

```bash
# For each template directory
for template in template-*; do
  cd "$template"
  vim .aget/version.json  # Update to v2.11.0
  cd ..
done

# Verify consistency
python3 .aget/patterns/sync/version_consistency.py --expected 2.11.0
```

---

### Scenario 4: Custom Modifications on Top of Template

**Situation**: You've modified AGENTS.md, added custom patterns

**Concern**: Upgrade might overwrite customizations

**Solution**:
1. Version control your changes: `git diff`
2. Note customizations before upgrade
3. Upgrade version.json only (don't pull template changes)
4. Reapply customizations if needed
5. Test thoroughly

**Best Practice**: Keep customizations in separate files (`.aget/custom/`)

---

## Troubleshooting Upgrades

### Problem: Tests Fail After Upgrade

**Symptoms**:
```
FAILED tests/test_version.py::test_version_current
AssertionError: Version mismatch
```

**Cause**: version.json not updated OR test caching

**Fix**:
```bash
# Clear pytest cache
rm -rf .pytest_cache __pycache__ tests/__pycache__

# Re-run tests
python3 -m pytest tests/ -v --tb=short
```

---

### Problem: Wake-Up Shows Wrong Version

**Symptoms**: Wake-up displays old version after upgrade

**Cause**: version.json not saved OR wrong file edited

**Fix**:
```bash
# Verify version.json was actually updated
cat .aget/version.json | grep aget_version

# If wrong, edit again
vim .aget/version.json

# Verify change saved
git diff .aget/version.json
```

---

### Problem: "No module named 'pytest'"

**Symptoms**: Cannot run tests after upgrade

**Cause**: pytest not installed

**Fix**:
```bash
# Install pytest
pip install pytest

# Or if using requirements
pip install -r requirements.txt
```

---

### Problem: Contract Tests Changed Between Versions

**Symptoms**: New tests appear OR tests renamed

**Cause**: Framework test suite evolved

**Fix**: Normal behavior - run new tests, should pass if upgrade correct

---

## Upgrade Best Practices

### Before Upgrading

- ✅ Read CHANGELOG for target version
- ✅ Backup current state (git commit)
- ✅ Check for breaking changes
- ✅ Plan downtime if production agent

### During Upgrade

- ✅ Follow migration guide exactly
- ✅ Update one version at a time (if major versions)
- ✅ Run tests after each step
- ✅ Verify wake-up shows new version

### After Upgrading

- ✅ Run full test suite
- ✅ Test core workflows
- ✅ Document any issues
- ✅ Commit upgrade

### If Uncertain

- ⚠️ Test in clone first (non-production agent)
- ⚠️ Consult VERSION_HISTORY.md
- ⚠️ File issue if unclear
- ⚠️ Ask in community (if channels exist)

---

## Multi-Agent Upgrades

### Coordinating Fleet Upgrades

If managing multiple agents (5+):

1. **Inventory**: List all agents + current versions
   ```bash
   for agent in agent-*; do
     echo "$agent: $(cat $agent/.aget/version.json | grep aget_version)"
   done
   ```

2. **Prioritize**: Critical agents first, experimental last

3. **Batch**: Upgrade in groups (e.g., 5 at a time)

4. **Test**: Each batch before proceeding

5. **Roll Forward**: Complete all agents to avoid version drift

---

## Staying Up-to-Date

**Recommended**: Upgrade within 1-2 releases of latest

**Why**:
- Security fixes
- Bug fixes
- New features
- Community support

**How**:
- Watch GitHub releases (email notifications)
- Check homepage badge monthly
- Review CHANGELOG quarterly

---

## Upgrade Support

**Questions**:
- Check [VERSIONING.md](VERSIONING.md)
- Check [RELEASES.md](RELEASES.md)
- File issue: https://github.com/aget-framework/aget/issues

**Bugs After Upgrade**:
- Rollback first (see Rollback Procedure)
- File issue with "upgrade" label
- Include: old version, new version, error details

**Feature Requests for Migration Tools**:
- File issue with "enhancement" label
- Describe desired automation

---

## Related Documents

- **VERSIONING.md**: How versions work
- **RELEASES.md**: Release process and cadence
- **VERSION_HISTORY.md**: Complete timeline
- **CHANGELOG.md**: What changed per version
- **Delta Specs**: `aget/specs/deltas/AGET_DELTA_vX.Y.md`

---

*UPGRADING.md - Safe version upgrade procedures*
*Created: 2025-12-24 | Version: 1.0*
