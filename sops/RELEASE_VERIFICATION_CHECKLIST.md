# Release Verification Checklist

**Version**: 1.0.0
**Status**: ACTIVE
**Implements**: R-PUB-001, R-REL-001
**Updated**: 2026-01-04

---

## Purpose

Pre-release verification checklist ensuring quality, consistency, and governance compliance before publishing AGET framework releases.

---

## Pre-Release Gates

### Gate 1: Documentation Quality (R-PUB-001-01)

- [ ] README.md updated with current version
- [ ] CHANGELOG.md has entry for this release
- [ ] Breaking changes documented in migration guide
- [ ] All new features documented in specs

### Gate 2: Version Consistency (R-REL-001)

- [ ] Core aget/ version.json updated
- [ ] All template version.json files updated
- [ ] Version sync check passes: `python3 scripts/version_sync.py --check`
- [ ] No version drift between repos

### Gate 3: Test Validation

- [ ] Unit tests pass: `python3 -m pytest tests/`
- [ ] Contract tests pass on all templates
- [ ] Wake up protocol works on 3+ templates
- [ ] Sanity check passes on all templates

### Gate 4: Structural Compliance

- [ ] All templates have required files (.aget/, governance/)
- [ ] All templates pass persona validation
- [ ] All templates pass naming convention check
- [ ] No breaking structural changes without migration path

### Gate 5: Git Hygiene

- [ ] No uncommitted changes in any repo
- [ ] All changes committed with proper message format
- [ ] No merge conflicts
- [ ] Branch is up-to-date with main

### Gate 6: Tag Preparation

- [ ] Tag message prepared
- [ ] Tag follows format: `vMAJOR.MINOR.PATCH`
- [ ] Tag applied to aget/ core first
- [ ] Tags applied to all templates

---

## Checklist Execution

### Step 1: Run Automated Checks

```bash
# Version sync
python3 scripts/version_sync.py --check

# Fleet validation
python3 scripts/validate_fleet.py

# Tests
python3 -m pytest tests/ -v
```

### Step 2: Manual Review

| Item | Verified | Notes |
|------|----------|-------|
| README accurate | [ ] | |
| CHANGELOG complete | [ ] | |
| Migration guide (if needed) | [ ] | |
| No sensitive data | [ ] | |

### Step 3: Tag and Push

```bash
# Core first
git -C aget/ tag -a vX.Y.Z -m "Release vX.Y.Z: Description"
git -C aget/ push origin vX.Y.Z

# Templates
for template in template-*-aget; do
  git -C $template tag -a vX.Y.Z -m "vX.Y.Z"
  git -C $template push origin vX.Y.Z
done
```

---

## Post-Release Verification

### Immediately After Release

- [ ] Tags visible on GitHub for all repos
- [ ] Release notes published (if major/minor)
- [ ] Announcement posted (if significant)

### Within 24 Hours

- [ ] Verify fresh clone works
- [ ] Run wake up on cloned template
- [ ] Sanity check on cloned template

---

## Rollback Procedure

If issues discovered post-release:

1. **Hotfix Path** (for minor issues):
   - Create vX.Y.Z+1 patch
   - Fast-follow release

2. **Rollback Path** (for blocking issues):
   - Document issue
   - Revert commits
   - Delete tags (if not widely distributed)
   - Re-tag with fixed content

---

## R-PUB-001 Requirements Mapping

| Requirement | Gate | Verification |
|-------------|------|--------------|
| R-PUB-001-01 | Gate 1 | Documentation review |
| R-PUB-001-02 | Gate 2 | Version sync check |
| R-PUB-001-03 | Gate 3 | Test execution |
| R-PUB-001-04 | Gate 4 | Structural validation |
| R-PUB-001-05 | Gate 5 | Git status check |
| R-PUB-001-06 | Gate 6 | Tag application |

---

## References

- AGET_VERSIONING_CONVENTIONS.md - Version rules
- R-REL-001 - Multi-repo coordination protocol
- scripts/version_sync.py - Version checking
- scripts/validate_fleet.py - Fleet validation

---

*RELEASE_VERIFICATION_CHECKLIST.md - Pre-release gate checklist*
