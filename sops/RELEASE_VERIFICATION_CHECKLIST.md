# Release Verification Checklist

**Version**: 1.3.0
**Status**: ACTIVE
**Implements**: R-PUB-001, R-REL-001, R-REL-010, R-REL-011, R-LIC-001, R-SPEC-010, L515
**Updated**: 2026-01-11

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

### Gate 7: Organization Artifacts (R-REL-010, R-REL-011)

**⚠️ BLOCKING: Must complete within release session**

- [ ] aget/CHANGELOG.md has entry for this release (R-REL-011)
- [ ] `.github/profile/README.md` version badge updated to new version
- [ ] `.github/profile/README.md` release date badge updated
- [ ] `.github/profile/README.md` roadmap section shows new version as "Current"
- [ ] `.github` repo committed and pushed
- [ ] Organization homepage displays correctly (visual verification)

### Gate 8: License Compliance (R-LIC-001, L432)

**⚠️ BLOCKING: Legal requirement**

- [ ] aget/ has LICENSE file (Apache 2.0)
- [ ] .github/ has LICENSE file (Apache 2.0)
- [ ] All templates have LICENSE file (Apache 2.0)
- [ ] Homepage license badge shows "Apache 2.0"
- [ ] No MIT licenses in template fleet (CAP-LIC-001)

```bash
# Verification command
for repo in aget .github template-*-aget; do
  echo -n "$repo: "; head -1 "$repo/LICENSE" 2>/dev/null || echo "MISSING"
done
```

### Gate 9: Validator Existence (R-SPEC-010, L433)

**⚠️ Pre-release: Run before major releases**

- [ ] All "Enforcement:" references in specs have existing validators OR "(planned)" marker
- [ ] Validator theater ratio < 20% (missing/total)
- [ ] New specs don't reference non-existent validators

```bash
# Verification command
grep -rh "Enforcement.*validate_" aget/specs/ | grep -v "(planned)" | \
  grep -oE "validate_[a-z_]+\.py" | sort -u | while read v; do
    [ -f "aget/validation/$v" ] || echo "MISSING: $v"
  done
```

### Gate 10: Template Coherence (L515)

**⚠️ BLOCKING: Templates must align with validators**

- [ ] Single canonical location per template (no duplicates in docs/templates/)
- [ ] Each template passes its own validator
- [ ] Template versions bumped if format changed
- [ ] SOP_template_lifecycle.md followed for any template changes

```bash
# Verification command: template coherence check
echo "=== Template Coherence Check ==="

# Check for duplicates
echo "Checking for duplicate templates..."
for tmpl in PROJECT_PLAN ADR SPEC VOCABULARY; do
  count=$(find aget/ -name "${tmpl}_TEMPLATE.md" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 1 ]; then
    echo "FAIL: Multiple ${tmpl}_TEMPLATE.md found"
    find aget/ -name "${tmpl}_TEMPLATE.md"
  elif [ "$count" -eq 0 ]; then
    echo "WARN: No ${tmpl}_TEMPLATE.md found"
  else
    echo "PASS: Single ${tmpl}_TEMPLATE.md"
  fi
done

# Validate PROJECT_PLAN template
echo ""
echo "Validating PROJECT_PLAN template..."
python3 aget/validation/validate_project_plan.py aget/templates/PROJECT_PLAN_TEMPLATE.md
```

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

## Requirements Mapping

| Requirement | Gate | Verification |
|-------------|------|--------------|
| R-PUB-001-01 | Gate 1 | Documentation review |
| R-PUB-001-02 | Gate 2 | Version sync check |
| R-PUB-001-03 | Gate 3 | Test execution |
| R-PUB-001-04 | Gate 4 | Structural validation |
| R-PUB-001-05 | Gate 5 | Git status check |
| R-PUB-001-06 | Gate 6 | Tag application |
| R-REL-010 | Gate 7 | Organization homepage update |
| R-REL-011 | Gate 7 | CHANGELOG entry verification |
| R-LIC-001 | Gate 8 | License file verification |
| CAP-LIC-001 | Gate 8 | Apache 2.0 compliance |
| R-SPEC-010 | Gate 9 | Validator existence check |
| L433 | Gate 9 | Enforcement theater audit |
| L515 | Gate 10 | Template coherence check |

---

## References

- AGET_VERSIONING_CONVENTIONS.md - Version rules
- R-REL-001 - Multi-repo coordination protocol
- scripts/version_sync.py - Version checking
- scripts/validate_fleet.py - Fleet validation

---

*RELEASE_VERIFICATION_CHECKLIST.md - Pre-release gate checklist*
