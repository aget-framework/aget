# SOP: Release Process

**Version**: 1.1.0
**Created**: 2026-01-04
**Updated**: 2026-01-11
**Owner**: aget-framework
**Implements**: AGET_RELEASE_SPEC, CAP-REL-001 through CAP-REL-008, R-REL-006, CAP-MIG-017

---

## Purpose

Standard operating procedure for releasing updates to the AGET framework.

---

## Scope

This SOP covers releases for:
- Core framework (aget/)
- Template repositories (template-*-aget/)
- Organization artifacts (.github/)

---

## Phase 0: Pre-Release Verification (L440)

**Critical**: Verify manager and version state before starting release.

### V0.1: Check manager version
```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print(f'Manager: {v[\"aget_version\"]}')"
```
**Expected**: Current version (should be updated to release version)

### V0.2: Check git status
```bash
git status -sb
```
**Expected**: Clean working directory or known pending changes

### V0.3: Version consistency check
```bash
python3 validation/validate_version_consistency.py /path/to/repo
```
**Expected**: PASS (all versions match)

---

## Phase 1: Version Update

### 1.1 Update Manager Version First (R-REL-006)

**Critical**: Managing agent updates its own version BEFORE updating managed repos.

```bash
# Update managing agent version.json
python3 -c "import json; v=json.load(open('.aget/version.json')); v['aget_version']='X.Y.Z'; json.dump(v, open('.aget/version.json','w'), indent=2)"
```

### 1.2 Update Core Framework (aget/)

```bash
cd /path/to/aget-framework/aget
# Update version.json
# Update CHANGELOG.md
# Update manifest.yaml if present
```

### 1.3 Update Templates

Update each template in order:
1. template-supervisor-aget
2. template-worker-aget
3. template-advisor-aget
4. template-consultant-aget
5. template-developer-aget
6. template-spec-engineer-aget

For each template:
- Update .aget/version.json
- Update CHANGELOG.md
- Update README.md version badge
- Update AGENTS.md @aget-version

---

## Phase 2: Validation

### 2.1 Run Contract Tests

```bash
for t in template-supervisor-aget template-worker-aget ...; do
  python3 -m pytest /path/to/$t/tests/ -v
done
```

### 2.2 Validate Version Consistency

```bash
python3 validation/validate_fleet.py /path/to/aget-framework
```

### 2.3 Validate File Naming

```bash
python3 validation/validate_file_naming.py /path/to/aget-framework/aget
```

---

## Phase 3: Git Operations

### 3.1 Commit Changes

```bash
# Core
git -C /path/to/aget-framework/aget add -A
git -C /path/to/aget-framework/aget commit -m "chore: Bump version to X.Y.Z"

# Each template
for t in template-*-aget; do
  git -C $t add -A
  git -C $t commit -m "chore: Bump version to X.Y.Z"
done
```

### 3.2 Create Tags

```bash
# Core
git -C /path/to/aget-framework/aget tag -a vX.Y.Z -m "Release vX.Y.Z"

# Each template
for t in template-*-aget; do
  git -C $t tag -a vX.Y.Z -m "Release vX.Y.Z"
done
```

### 3.3 Push

```bash
# Push core first (dependency root per R-REL-001-03)
git -C /path/to/aget-framework/aget push origin main
git -C /path/to/aget-framework/aget push origin vX.Y.Z

# Push templates
for t in template-*-aget; do
  git -C $t push origin main
  git -C $t push origin vX.Y.Z
done
```

---

## Phase 4: GitHub Releases

### 4.1 Create GitHub Releases

```bash
# Core
gh release create vX.Y.Z --repo aget-framework/aget --title "vX.Y.Z" --notes "See CHANGELOG.md"

# Each template
for t in template-*-aget; do
  gh release create vX.Y.Z --repo aget-framework/$t --title "vX.Y.Z" --notes "See CHANGELOG.md"
done
```

---

## Phase 5: Organization Update (R-REL-010)

### 5.1 Update Homepage

Edit `.github/profile/README.md`:
- Update version badge
- Update release date badge
- Update roadmap (current → next)

### 5.2 Push Homepage

```bash
git -C /path/to/aget-framework/.github add profile/README.md
git -C /path/to/aget-framework/.github commit -m "docs: Update homepage for vX.Y.Z"
git -C /path/to/aget-framework/.github push origin main
```

---

## Phase 6: Post-Release Validation

### 6.1 Verify GitHub Releases

```bash
for repo in aget template-supervisor-aget template-worker-aget ...; do
  gh release view vX.Y.Z --repo aget-framework/$repo
done
```

### 6.2 Verify Homepage

```bash
curl -s https://raw.githubusercontent.com/aget-framework/.github/main/profile/README.md | grep -q "X.Y.Z" && echo "PASS" || echo "FAIL"
```

---

## Phase 6.5: Remote Upgrade Documentation (CAP-MIG-017)

**Objective**: Ensure remote upgrade documentation is current for this release.

### 6.5.1 Verify Cross-Machine Section

```bash
# Check version references in cross-machine section
grep -A5 "Expected:" aget/docs/FLEET_MIGRATION_GUIDE_v3.md | grep -q "X.Y.Z" && echo "PASS" || echo "UPDATE NEEDED"
```

### 6.5.2 Checklist

- [ ] FLEET_MIGRATION_GUIDE cross-machine section references correct version
- [ ] Example version numbers updated (e.g., `# Expected: X.Y.Z`)
- [ ] Quick Reference Card version updated
- [ ] L457 learning document still accurate
- [ ] SOP_fleet_migration Phase 0.5 V-tests reference correct version
- [ ] UPGRADING.md Remote/Cross-Machine section current

**Decision_Point**: Remote documentation current? [GO/NOGO]

---

## Gate 8: Retrospective (L435)

**Required**: Every release PROJECT_PLAN SHALL include a retrospective gate.

### 8.1 Document Learnings

Create L-docs for significant discoveries during release:
- What worked well
- What caused friction
- What should change

### 8.2 Update SOPs

If release revealed SOP gaps:
- Update relevant SOP
- Add to SOP changelog

### 8.3 Review Velocity

Compare estimated vs actual effort:
```markdown
| Gate | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| ... | ... | ... | ... |
```

### 8.4 Archive PROJECT_PLAN

- Mark PROJECT_PLAN status as Complete
- Record final success criteria values
- Link to release notes

---

## Rollback Procedure

If release has critical issues:

### Emergency Rollback

```bash
# Revert to previous tag
git -C /path/to/aget revert HEAD
git -C /path/to/aget push origin main

# Delete bad release
gh release delete vX.Y.Z --repo aget-framework/aget --yes
git -C /path/to/aget tag -d vX.Y.Z
git -C /path/to/aget push origin :refs/tags/vX.Y.Z
```

### Verification

```bash
gh release view v{PREVIOUS} --repo aget-framework/aget
```

---

## References

- AGET_RELEASE_SPEC.md
- AGET_VERSIONING_CONVENTIONS.md
- RELEASE_VERIFICATION_CHECKLIST.md
- L440: Manager Migration Verification Gap
- L435: Retrospective Requirement (CAP-REASON-008)

---

## Changelog

### v1.1.0 (2026-01-11)

- Added Phase 6.5: Remote Upgrade Documentation (CAP-MIG-017)
- Checklist for cross-machine documentation verification
- Cross-reference to FLEET_MIGRATION_GUIDE_v3.md and UPGRADING.md

### v1.0.0 (2026-01-04)

- Initial public SOP
- Phase 0 verification commands (L440)
- Gate 8 retrospective section (L435)
- Based on patterns from v3.0.0-v3.1.0 releases

---

*SOP_release_process.md — Release procedure for AGET framework*
