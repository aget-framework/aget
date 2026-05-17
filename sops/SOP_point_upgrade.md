# SOP: Point Upgrade

**Version**: 1.0.0
**Created**: 2026-01-10
**Updated**: 2026-01-10
**Owner**: private-aget-framework-AGET
**Implements**: L438 (Point Upgrade SOP Gap)
**Related**: L148, L444, L457, L458, AGET_SOP_SPEC.md

---

## Purpose

This SOP provides a standardized procedure for executing point upgrades (e.g., v3.2→v3.3, v3.3→v3.4) of AGET framework versions. It ensures consistent, validated upgrades with proper version coherence across all version-bearing files.

**Gap Addressed**: L438 identified that point upgrades lacked formal SOP documentation, relying on the informal UPGRADING.md guide.

---

## Scope

### In Scope

- Point upgrades within the same major version (e.g., v3.1→v3.2)
- Single-agent upgrades
- Remote agent upgrades (with framework sync)
- Version coherence validation (L444)

### Out of Scope

| Item | Reference |
|------|-----------|
| Major version migrations (e.g., v2.x→v3.0) | SOP_aget_migrate.md |
| Fleet-wide upgrade orchestration | L458 (future) |
| Automated `aget upgrade` command | L148 Phase 3 (future) |

---

## Prerequisites

Before starting a Point_Upgrade:

1. **Read CHANGELOG** for target version
2. **Identify change type**:
   - **Patch** (x.y.Z): Safe, non-breaking
   - **Minor** (x.Y.0): Backward compatible, may have new features
   - **Major** (X.0.0): Breaking changes — use SOP_aget_migrate.md instead
3. **Verify framework access** (for remote agents, sync framework first per L457)

---

## Procedure

### Phase 1: Pre-Upgrade Validation

**Objective**: Ensure safe upgrade conditions exist.

| Step | Action | Command/Location |
|------|--------|------------------|
| 1.1 | Backup current state | `git add . && git commit -m "Pre-upgrade snapshot"` |
| 1.2 | Check current version | `cat .aget/version.json` |
| 1.3 | Run version consistency check | `python3 .aget/patterns/sync/version_consistency.py` |
| 1.4 | Read target version CHANGELOG | `aget/CHANGELOG.md` or template CHANGELOG |
| 1.5 | Identify breaking changes | Look for "Breaking" or "Migration Required" |

**For Remote Agents** (L457 Pattern):
```bash
# On remote machine, sync framework first
cd /path/to/aget-framework
git pull origin main
```

### Phase 2: Upgrade Execution

**Objective**: Update all version-bearing files (L444 Version Inventory).

#### Version-Bearing Files (L444)

| File | Field | Example |
|------|-------|---------|
| `.aget/version.json` | `aget_version` | "3.3.0" |
| `.aget/version.json` | `updated` | "2026-01-10" |
| `.aget/version.json` | `migration_history` | Add entry |
| `AGENTS.md` | Header line | "- v3.3.0" |
| `manifest.yaml` | `version:` | "3.3.0" |

#### Step-by-Step

**Step 2.1**: Update `.aget/version.json`
```json
{
  "aget_version": "3.3.0",
  "updated": "2026-01-10",
  "migration_history": [
    {"from": "3.2.1", "to": "3.3.0", "date": "2026-01-10"}
  ]
}
```

**Step 2.2**: Update `AGENTS.md` header
```markdown
# AGENTS.md
# private-aget-framework-AGET - Framework Manager - v3.3.0
```

**Step 2.3**: Update `manifest.yaml` (if present)
```yaml
version: 3.3.0
```

### Phase 3: Post-Upgrade Validation

**Objective**: Verify upgrade succeeded with no coherence issues.

| Step | Action | Command | Expected |
|------|--------|---------|----------|
| 3.1 | Run contract tests | `python3 -m pytest tests/ -v` | All pass |
| 3.2 | Run wake-up | `python3 .aget/patterns/session/wake_up.py` | Shows new version |
| 3.3 | Version coherence check | See below | No stale versions |
| 3.4 | Run validator (optional) | `python3 validate_version_inventory.py` | PASS |
| 3.5 | **Conformance check** | `python3 aget/validation/validate_conformance.py .` | L2+ |

**Conformance Check (v3.4+)**:
```bash
# Run conformance assessment after upgrade
python3 ~/github/aget-framework/aget/validation/validate_conformance.py . --verbose

# Expected: L2_COMPLIANT or higher (60%+)
# If L1 or L0: Review gaps and remediate before proceeding
```

See: CONFORMANCE_RUBRIC.md for remediation patterns.

**Version Coherence Check** (L444):
```bash
# Replace OLD_VERSION with previous version (e.g., v3.2.1)
grep -r "v3.2.1" . | grep -v migration_history | grep -v CHANGELOG
# Expected: No results (all references updated)
```

### Phase 4: Documentation

**Objective**: Commit upgrade and document any issues.

```bash
git add .
git commit -m "chore: Upgrade to v3.3.0"
```

**V-test V-UPGRADE-004** (added PP-035 / closes L671 + L952 traceability axis):
- [ ] Migration PR# recorded in this agent's row of the canonical `RELEASE_HANDOFF_vX.Y.Z.md` pilot tracking table (Migration PR column), OR
- [ ] Migration PR column marked `N/A (direct-commit)` (direct-commit path used; no PR opened — acceptable per current Phase 4 workflow above)

If neither: STOP — record traceability before closing Phase 4. Cross-reference: `sops/templates/RELEASE_HANDOFF_TEMPLATE.md` Pilot Upgrade Tracking section + Migration PR column semantics. L588 mechanical-step: single V-test, no judgment protocol needed.

If issues encountered, create L-doc for future SOP improvement.

---

## Rollback Procedure

If upgrade causes issues:

```bash
# Step 1: Revert version.json
git checkout HEAD~1 .aget/version.json

# Step 2: Revert all version-bearing files
git checkout HEAD~1 AGENTS.md
git checkout HEAD~1 manifest.yaml  # if present

# Step 3: Verify rollback
python3 -m pytest tests/ -v
python3 .aget/patterns/session/wake_up.py

# Step 4: Commit rollback
git commit -m "chore: Rollback from v3.3.0 to v3.2.1"
```

---

## Version-Specific Guides

For version-specific changes, consult:

| Version Pair | Key Changes | Notes |
|--------------|-------------|-------|
| v3.2.1→v3.3.0 | Specification maturity | See PROJECT_PLAN_v3.3.0_release.md |

*Add entries as new versions are released.*

---

## Common Scenarios

### Scenario A: Simple Patch Upgrade (x.y.Z)

Patch upgrades are typically safe:
1. Skip breaking change check (patches are non-breaking)
2. Follow Phase 1-4 as normal
3. Rollback unlikely needed

### Scenario B: Minor Upgrade with New Features (x.Y.0)

1. Read CHANGELOG carefully for new features
2. Check if new required fields added
3. Follow Phase 1-4
4. Test new features work

### Scenario C: Remote Agent Upgrade (L457)

1. **On remote machine**: Sync framework first (`git pull`)
2. Follow standard Phase 1-4
3. Verify via wake-up that version matches local framework

### Scenario D: Multi-Agent Coordination (L458)

For upgrading multiple agents:
1. Upgrade managing agent first (R-REL-006)
2. Upgrade managed agents in sequence
3. Verify version consistency across fleet

---

## Troubleshooting

### Issue: Contract Tests Fail After Upgrade

**Symptoms**: `pytest` fails with import or assertion errors
**Cause**: Breaking change not identified, or new required field missing
**Resolution**:
1. Check CHANGELOG for breaking changes
2. Add missing fields per new version requirements
3. If unresolvable, rollback and consult release notes

### Issue: Version Mismatch in wake-up

**Symptoms**: Wake-up shows old version
**Cause**: Incomplete version.json update
**Resolution**:
1. Verify `aget_version` field in version.json
2. Re-run wake-up script

### Issue: Coherence Check Finds Stale Versions

**Symptoms**: `grep` finds old version references
**Cause**: Not all version-bearing files updated (L444)
**Resolution**:
1. Update all files in L444 inventory
2. Re-run coherence check

---

## References

| Document | Purpose |
|----------|---------|
| L148 | Upgrade pain analysis, solution space |
| L438 | Gap identification for this SOP |
| L444 | Version inventory coherence requirement |
| L457 | Remote supervisor upgrade pattern |
| L458 | Fleet migration coordination pattern |
| L521 | Version-Bearing File Specification-to-Tool Gap |
| UPGRADING.md | User-facing upgrade guide |
| SOP_release_process.md | Release publishing (not consuming) |
| SOP_aget_migrate.md | Major version migration |
| SOP_version_coherence_validation.md | Version_Bearing_File coherence procedure |

---

## Checklist Template

See [Point Upgrade Checklist Template](#checklist-template) in PROJECT_PLAN_point_upgrade_sop_v1.0.md, or use:

```markdown
# v3.2.1 → v3.3.0 Point Upgrade Checklist

## Pre-Upgrade
- [ ] Read CHANGELOG for v3.3.0
- [ ] Check for breaking changes
- [ ] Backup: `git add . && git commit -m "Pre-upgrade snapshot"`
- [ ] Run: `python3 .aget/patterns/sync/version_consistency.py`

## Upgrade Execution (L444)
- [ ] `.aget/version.json` → aget_version: "3.3.0"
- [ ] `.aget/version.json` → updated: "2026-01-10"
- [ ] `.aget/version.json` → migration_history: add entry
- [ ] `AGENTS.md` header → v3.3.0
- [ ] `manifest.yaml` → version: 3.3.0

## Post-Upgrade Validation
- [ ] `python3 -m pytest tests/ -v` → All pass
- [ ] `python3 .aget/patterns/session/wake_up.py` → Shows v3.3.0
- [ ] Coherence: `grep -r "v3.2.1" . | grep -v migration` → No results
- [ ] `python3 validate_version_inventory.py` → PASS (if available)

## Documentation
- [ ] `git commit -m "chore: Upgrade to v3.3.0"`
- [ ] Note issues for SOP improvement
```

---

*SOP_point_upgrade.md v1.0.0*
*Graduated from UPGRADING.md per L438*
*Implements L444 Version Inventory, references L148/L457/L458*
