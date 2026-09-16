# AGET Framework Upgrade Guide

**Audience**: Users upgrading between framework versions

**Purpose**: Transfer and verify release artifacts while preserving agent-specific state.

## Upgrade Sequence (All Versions)

A version edit is the final metadata step, not an upgrade. Minor and patch releases also require payload transfer. There is no universal overwrite command for an existing customized agent: use the target release's migration handoff and deployment contract to select the files for your archetype.

### 1. Establish a recoverable baseline

Work in your agent repository. Inspect `git status --short` and the current version. Commit or otherwise back up your existing work deliberately; review staged paths and exclude secrets. Begin the migration with a clean working tree. Record the baseline commit with `git rev-parse HEAD`. Back up any relevant untracked or external state separately; Git cannot restore it.

Read the target release's notes, breaking changes, migration handoff and deployment contract before changing files. For example, the [v3.34.0 migration handoff](https://github.com/aget-framework/aget/blob/v3.34.0/handoffs/RELEASE_HANDOFF_v3.34.0.md) and [deployment contract](https://github.com/aget-framework/aget/blob/v3.34.0/DEPLOYMENT_SPEC_v3.34.0.yaml) are pinned to that release. Use the corresponding artifacts for your chosen version. Missing source files or instructions are a stop condition; do not substitute a version bump.

### 2. Obtain a release-pinned source

Clone the matching archetype template at the chosen release tag into a separate, new directory. This example uses the supervisor and v3.34.0; change both intentionally for your receiver:

```bash
git clone --branch v3.34.0 --depth 1 https://github.com/aget-framework/template-supervisor-aget.git /path/to/new-template-source
git -C /path/to/new-template-source rev-parse HEAD
```

Record the resolved source commit and compare it with the target release's source/deployment records. Inspect the actual selected files in this checkout. A core release tag does not establish that every template contains the same payload. Do not silently switch to `main` if the chosen template tag or payload is missing.

### 3. Transfer the selected payload, preserving local state

Build an explicit path list from the release handoff/contract and your archetype. Record each file as copy, merge, add or remove and retain a before/after diff. Review instruction and authorization surfaces through the receiver's approval process.

- Copy unmodified framework-owned files from the pinned source.
- Merge framework changes into locally customized files; do not replace agent identity, goals, knowledge, credentials or runtime configuration with template defaults.
- Preserve instance hooks such as `scripts/wake_up_ext.py` and `scripts/wind_down_ext.py` unless the release specifically calls for a reviewed migration.
- Apply required additions and removals explicitly. Do not copy the source repository's `.git` directory.

For a single existing framework-owned file whose local contents are confirmed unmodified, the transfer looks like this (example only; include it only when selected by your release migration):

```bash
# Run inside the receiver repository after reviewing the selected path.
cp /path/to/new-template-source/scripts/wake_up.py scripts/wake_up.py
git diff -- scripts/wake_up.py
```

Repeat only for the reviewed path list, using a merge where local changes exist. Compare transferred files with the pinned source, or document intentional differences after merging. Resolve missing dependencies before proceeding. **Do not advance the receiver version while the payload is incomplete.**

### 4. Update metadata and verify the receiver

After the selected payload and dependencies are present, update `.aget/version.json` and any other version-bearing manifest identified by the release contract. Preserve the receiver's identity and migration history. Record target version, source commit, baseline commit, transferred paths and deliberate deviations.

Run the release-specific acceptance checks and the receiver's supported checks. Where these scripts are supplied, include:

```bash
python3 -m pytest tests/ -v
python3 scripts/health_check.py
python3 scripts/wake_up.py
```

Check exit codes and substantive output. A new version in wake-up output proves only the label was read. Missing checks or failures must be reported and resolved or explicitly dispositioned before claiming acceptance. Use the manifest fields actually present in the receiver when checking version consistency.

### 5. Commit the complete migration and record acceptance

Review `git diff` and stage the explicit migration paths, including the payload and metadata. Inspect `git diff --cached` before committing. Keep unrelated changes out of this commit. Record the migration commit and receiver acceptance evidence; a published release and a copied payload are distinct from a verified deployment.

## Rollback Procedure

Rollback must restore the payload and metadata together. For an isolated, committed migration, review and revert that migration commit with `git revert <migration-commit>`, then rerun the receiver checks. Do not reset shared history.

For an uncommitted migration, use the recorded baseline and path list to restore only migration changes; remove only new files introduced by that migration after reviewing them. Preserve unrelated or concurrent work. Restore any separately backed-up external state according to its own procedure. Recheck payload, version metadata, health and wake-up before declaring rollback successful. Capture the failure details before retrying.

## Historical Examples

The guides below describe older migrations. Their version-edit-only examples are historical, not a substitute for the payload-transfer and receiver-verification sequence above. Follow the target release's current migration artifacts when an older example conflicts.

---

## Version-Specific Migration Guides

### v3.7.0 → v3.8.0

**Release Date**: 2026-03-08

**Theme**: Governance Maturation — Principle Codification, Deliverable Conformance, Structural Enforcement

**Breaking Changes**: None. Fully backward compatible with v3.7.x.

**Do I need to act?**
- **YES** if: You want the new `aget-enhance-spec` skill or governance principles
- **Minimal** if: You only need the version bump (Steps 1-2 below)

**New Features**:
- GOVERNANCE_PRINCIPLES.md v1.1.0 (6 Tier 1 + 5 Tier 2 meta-principles)
- Structural Aesthetics design principle (integrated into DESIGN_PHILOSOPHY, MISSION)
- `aget-enhance-spec` skill (specification enhancement lifecycle)
- `aget-expand-ontology` skill (optional, demand-triggered)
- `pre_sync_check.py` (skill customization detection before upgrades)
- `validate_project_plan.py` (PROJECT_PLAN existence validator)
- TEMPLATE_AGENTS_MD_SPEC v1.0.0 (governance patterns in templates)

**Prerequisite**: Sync your framework clone first:
```bash
cd ~/path/to/aget-framework/aget && git pull origin main
cd ~/path/to/template-{archetype}-aget && git pull origin main

# Verify v3.8.0 is available
jq -r .aget_version ~/path/to/aget-framework/aget/.aget/version.json
# Expected: "3.8.0"
```

**Migration Steps**:

1. **Update version markers**:
   ```bash
   AGENT=~/path/to/your-agent

   # Use perl on macOS (not sed — see L570)
   perl -pi -e 's/"aget_version": "3\.7\.0"/"aget_version": "3.8.0"/' $AGENT/.aget/version.json
   perl -pi -e 's/@aget-version: 3\.7\.0/@aget-version: 3.8.0/' $AGENT/AGENTS.md
   ```

2. **Deploy aget-enhance-spec skill**:
   ```bash
   TEMPLATE=~/path/to/template-{archetype}-aget

   # Check for customizations first (new in v3.8.0!)
   python3 $TEMPLATE/.aget/patterns/upgrade/pre_sync_check.py \
     --baseline $TEMPLATE/.claude/skills \
     --instance $AGENT/.claude/skills

   # Deploy
   cp -r $TEMPLATE/.claude/skills/aget-enhance-spec $AGENT/.claude/skills/
   ```

3. **Add migration_history entry** to `.aget/version.json`:
   ```json
   "migration_history": [
     "v3.7.0 -> v3.8.0: YYYY-MM-DD (Governance Maturation - principle codification, deliverable conformance)"
   ]
   ```

4. **Verify**:
   ```bash
   python3 $AGENT/scripts/wake_up.py
   # Should show v3.8.0

   # Check for stale version references
   grep -r "3\.7\.0" $AGENT --include="*.yaml" --include="*.json" | grep -v migration_history
   # Expected: No results (or only feature-introduction markers)
   ```

**Estimated Time**: 5 minutes per agent

**See Also**: [RELEASE_HANDOFF_v3.8.0.md](../handoffs/RELEASE_HANDOFF_v3.8.0.md)

---

### v3.6.0 → v3.7.0

**Release Date**: 2026-03-05

**Theme**: Quality Reconciliation — Content Integrity, SOP Lifecycle, Positioning Reframe

**Breaking Changes**: None. Fully backward compatible with v3.6.x. However, 4 skill directory renames require attention.

**Do I need to act?**
- **YES** if: You have skills with old names (`aget-studyup`, `aget-healthcheck-*`, `aget-sanity-check`)
- **YES** if: Your AGENTS.md mentions "lawyers", "doctors", or similar profession claims
- **Minimal** if: You only need the version bump (Steps 1-2 below)

**New Features**:
- CONTENT_INTEGRITY_VALIDATION_SPEC v1.0.0 (8 dimensions of claim drift)
- AGET_SOP_SPEC v1.2.0 (SOP lifecycle management)
- Evidence-based positioning (15 READMEs reframed)
- Skill verb vocabulary aligned (4 renames)
- Supervisor template: 1 new archetype skill (`aget-review-handoff`; `aget-check-fleet` was v3.6.0)
- wind_down.py exit code fix (warnings no longer return exit 1)

**Prerequisite**: Sync your framework clone first:
```bash
cd ~/path/to/aget-framework/aget && git pull origin main
cd ~/path/to/template-{archetype}-aget && git pull origin main

# Verify v3.7.0 is available
jq -r .aget_version ~/path/to/aget-framework/aget/.aget/version.json
# Expected: "3.7.0"
```

**Migration Steps**:

1. **Update version markers**:
   ```bash
   AGENT=~/path/to/your-agent

   # Use perl on macOS (not sed — see L570)
   perl -pi -e 's/"aget_version": "3\.6\.0"/"aget_version": "3.7.0"/' $AGENT/.aget/version.json
   perl -pi -e 's/@aget-version: 3\.6\.0/@aget-version: 3.7.0/' $AGENT/AGENTS.md
   ```

2. **Rename skill directories** (P2.10 verb vocabulary):
   ```bash
   # Rename skills to new canonical names
   cd $AGENT/.claude/skills/

   # Only rename if old name exists
   [ -d "aget-studyup" ] && mv aget-studyup aget-study-up
   [ -d "aget-healthcheck-kb" ] && mv aget-healthcheck-kb aget-check-kb
   [ -d "aget-healthcheck-sessions" ] && mv aget-healthcheck-sessions aget-check-sessions
   [ -d "aget-sanity-check" ] && mv aget-sanity-check aget-check-health
   ```
   **Note**: If upgrading from v3.6.0, only `aget-studyup` → `aget-study-up` is needed — the other 3 were already renamed in v3.6.0. The `[ -d ... ] &&` guards make this safe either way.

   **Why**: AGET verb vocabulary now follows approved verb patterns. `check` replaces `healthcheck`/`sanity-check`; `study-up` adds the required hyphen. Templates include symlinks for backward compatibility, but canonical names have changed.

3. **Sync wind_down.py** (exit code fix):
   ```bash
   TEMPLATE=~/path/to/template-{archetype}-aget
   cp $TEMPLATE/scripts/wind_down.py $AGENT/scripts/wind_down.py
   ```
   **Why**: v3.7.0 fixes wind_down.py to no longer return exit code 1 for persistent warnings (e.g., skill drift). Only errors (broken state) produce non-zero exit codes. This prevents users from ignoring exit codes.

4. **Update skill references in AGENTS.md** (if your AGENTS.md lists skills):
   ```bash
   perl -pi -e 's/aget-studyup/aget-study-up/g' $AGENT/AGENTS.md
   perl -pi -e 's/aget-healthcheck-kb/aget-check-kb/g' $AGENT/AGENTS.md
   perl -pi -e 's/aget-healthcheck-sessions/aget-check-sessions/g' $AGENT/AGENTS.md
   perl -pi -e 's/aget-sanity-check/aget-check-health/g' $AGENT/AGENTS.md
   ```

5. **Add migration_history entry** to `.aget/version.json`:
   ```json
   "migration_history": [
     "v3.6.0 -> v3.7.0: YYYY-MM-DD (Quality Reconciliation - content integrity, SOP lifecycle, positioning reframe)"
   ]
   ```

6. **Verify**:
   ```bash
   python3 $AGENT/scripts/wake_up.py
   # Should show v3.7.0

   # Check for stale skill names
   ls $AGENT/.claude/skills/ | grep -E "studyup|healthcheck|sanity-check"
   # Expected: No results

   # Check for stale version references
   grep -r "3\.6\.0" $AGENT --include="*.yaml" --include="*.json" | grep -v migration_history
   # Expected: No results (or only feature-introduction markers)
   ```

**Estimated Time**: 5-10 minutes per agent

**See Also**: [RELEASE_HANDOFF_v3.7.0.md](../handoffs/RELEASE_HANDOFF_v3.7.0.md)

---

### v3.5.0 → v3.6.0

**Release Date**: 2026-02-21

**Theme**: Infrastructure Maturation — Observability, Content Integrity, Ontology

**Breaking Changes**: None. Fully backward compatible with v3.5.x.

**Do I need to act?**
- **YES** if: You want the new `aget-studyup` skill and updated platform claims
- **NO** if: You only need the version bump (Steps 1-2 below)

**New Features**:
- `aget-studyup` skill (14th universal skill for KB research)
- Release observability tooling (5 scripts)
- Canonical scripts v2.0 (`scripts/` is now the deployment target)
- Platform claims updated: Claude Code, Codex CLI, Gemini CLI

**Prerequisite**: Sync your framework clone first (especially on remote machines):
```bash
cd /path/to/aget-framework/aget && git pull origin main
cd /path/to/template-{archetype}-aget && git pull origin main

# Verify v3.6.0 is available
cat /path/to/aget-framework/aget/.aget/version.json | grep aget_version
# Expected: "3.6.0"
```

**Migration Steps**:

1. **Update version markers**:
   ```bash
   AGENT=/path/to/your-agent

   # Use perl on macOS (not sed — see L570)
   perl -pi -e 's/"aget_version": "3\.5\.0"/"aget_version": "3.6.0"/' $AGENT/.aget/version.json
   perl -pi -e 's/@aget-version: 3\.5\.0/@aget-version: 3.6.0/' $AGENT/AGENTS.md
   ```

2. **Update platform claims** in AGENTS.md:
   ```bash
   # Change "Cursor, Aider, Windsurf" → "Claude Code, Codex CLI, Gemini CLI"
   # Or if already listing Claude Code, add Codex CLI and Gemini CLI
   ```

3. **Deploy aget-studyup skill**:
   ```bash
   TEMPLATE=/path/to/template-{archetype}-aget

   # Diff existing skills first (L582)
   diff -rq "$AGENT/.claude/skills/aget-studyup" "$TEMPLATE/.claude/skills/aget-studyup" 2>/dev/null

   # Deploy
   cp -r $TEMPLATE/.claude/skills/aget-studyup $AGENT/.claude/skills/
   ```

4. **Deploy study_topic.py script**:
   ```bash
   cp $TEMPLATE/scripts/study_topic.py $AGENT/scripts/
   ```

5. **Add migration_history entry** to `.aget/version.json`:
   ```json
   "migration_history": [
     "v3.5.0 -> v3.6.0: YYYY-MM-DD (Infrastructure Maturation)"
   ]
   ```

6. **Verify**:
   ```bash
   python3 $AGENT/scripts/wake_up.py
   # Should show v3.6.0

   # Check for stale version references
   grep -r "3\.5\.0" $AGENT --include="*.yaml" --include="*.json" | grep -v migration_history
   # Expected: No results (or only feature-introduction markers)
   ```

**Estimated Time**: 5-10 minutes per agent

**See Also**: [RELEASE_HANDOFF_v3.5.0.md](../handoffs/RELEASE_HANDOFF_v3.5.0.md) (format reference; v3.6.0 handoff forthcoming)

---

### v3.4.0 → v3.5.0

**Release Date**: 2026-02-14

**Theme**: Archetype Customization + Issue Governance

**Breaking Changes**: YES - `validation/` → `verification/` rename

**Do I need to act?**
- **YES** if: Your code imports from `aget/validation/`
- **NO** if: You use published templates without custom validators

**New Features**:
- 26 archetype-specific skills (2-3 per archetype)
- `aget-file-issue` skill with L520 issue governance
- `ontology/` directory with SKOS+EARS format
- Skill deployment governance (L586)

**Migration Steps**:

1. **Update version markers**:
   ```bash
   # Use perl on macOS (not sed - see L570)
   perl -pi -e 's/"aget_version": "3\.4\.0"/"aget_version": "3.5.0"/' .aget/version.json
   perl -pi -e 's/@aget-version: 3\.4\.0/@aget-version: 3.5.0/' AGENTS.md
   ```

2. **Handle breaking change** (if applicable):
   ```bash
   # Find affected imports
   grep -r "from validation\." . --include="*.py"

   # Update: from validation.X → from verification.X
   # Note: Both directories exist during transition
   ```

3. **Create ontology directory**:
   ```bash
   mkdir -p ontology
   cp ~/path/to/aget-framework/template-{archetype}-aget/ontology/*.yaml ontology/
   ```

4. **Deploy skills** (diff existing skills first per L582):
   ```bash
   # Check for local modifications BEFORE overwriting
   diff -rq ".claude/skills/aget-wake-up" "template/.claude/skills/aget-wake-up"

   # Deploy aget-file-issue
   cp -r ~/path/to/aget-framework/aget/.claude/skills/aget-file-issue .claude/skills/
   ```

5. **Verify**:
   ```bash
   python3 .aget/patterns/session/wake_up.py
   # Should show v3.5.0

   # Check for stale version references
   grep -r "3\.4\.0" . --include="*.yaml" --include="*.json" | grep -v migration_history
   # Expected: No results
   ```

**Estimated Time**: 10-15 minutes per agent

**See Also**: [RELEASE_HANDOFF_v3.5.0.md](../handoffs/RELEASE_HANDOFF_v3.5.0.md)

---

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

## Remote/Cross-Machine Upgrades (CAP-MIG-017)

**When This Applies**: Upgrading an agent on a different machine from where the framework is developed/released.

**Key Issue**: Your local framework clone may be stale, causing "version X.X doesn't exist" errors.

**Scenarios**:
- Work laptop different from personal laptop
- Server deployment
- CI/CD environment
- Any machine that doesn't automatically sync framework

### Quick Pre-Flight

Before upgrading on a remote machine:

```bash
# 1. Find your framework clone (common locations below)
#    Personal: ~/github/aget-framework/aget/
#    Work:     ~/code/aget-framework/aget/
#    Server:   /opt/aget/ or /srv/aget/
cd /path/to/your/aget-framework/aget

# 2. Health check: Verify remote is reachable
git ls-remote origin HEAD > /dev/null && echo "Remote OK" || echo "FAIL: Check network/SSH"

# 3. Sync framework
git fetch origin && git pull origin main

# 4. Verify version
cat .aget/version.json | grep aget_version
# Should show current release version
```

### After Sync: State Verification

If your agent previously studied the upgrade with stale framework:

```
⚠️ Agent context may be INVALID
   - Agent may incorrectly report "version X.X doesn't exist"
   - Solution: Re-study after sync
   - Pattern: "study up, focus on: vX.Y upgrade"
```

### Detailed Guide

For comprehensive cross-machine migration procedures, see:
- **[FLEET_MIGRATION_GUIDE_v3.md - Cross-Machine Pre-Flight](FLEET_MIGRATION_GUIDE_v3.md#cross-machine-pre-flight-l457-cap-mig-017)**

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "Version doesn't exist" | Stale framework | Run git pull, re-study |
| Remote unreachable | Network/SSH issue | Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git` |
| Pull failed | Uncommitted changes | `git stash` or commit first |

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
*Created: 2025-12-24 | Updated: 2026-02-22 | Version: 1.2*
