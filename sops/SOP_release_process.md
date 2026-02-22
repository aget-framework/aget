# SOP: Release Process

**Version**: 1.8.0
**Created**: 2026-01-04
**Updated**: 2026-02-21
**Owner**: aget-framework
**Implements**: AGET_RELEASE_SPEC, CAP-REL-001 through CAP-REL-025, CAP-SOP-001, R-REL-006, R-REL-019, R-REL-042, CAP-MIG-017, L555-L559, L585, L587, L605, R-SYNC-001

---

## Purpose

Standard operating procedure for releasing updates to the AGET framework.

---

## Scope

This SOP covers releases for:
- Core framework (aget/)
- Template repositories (template-*-aget/) — 12 repos
- Organization artifacts (.github/)

**Release Scope**: 14 repositories total (aget + 12 templates + .github)

**Public-Facing Version Indicators** (L578):
- README.md version badges (all templates)
- Organization profile (.github/profile/README.md)
- GitHub Releases (not just git tags)

---

## Phase 0: Pre-Release Verification (L440)

**Critical**: Verify manager, version state, and release timing before starting release.

### V0.0: Check release window timing (CAP-REL-011)
```bash
day=$(date +%A)
hour=$(date +%H)
if [[ "$day" == "Thursday" && $hour -lt 12 ]] || [[ "$day" == "Friday" && $hour -ge 12 ]]; then
  echo "PASS: In preferred release window ($day $(date +%H:%M))"
else
  echo "WARN: Outside preferred release window ($day $(date +%H:%M))"
  echo "Preferred: Thursday AM or Friday PM"
  echo "To proceed: Acknowledge off-window release with reason"
fi
```
**Expected**: PASS (in preferred window) or acknowledged WARN
**Advisory**: Off-window releases require acknowledgment, not blocked

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

### V0.4: Spec Coverage Check (L557, L559)

**Critical**: Verify specs exist and have V-tests before release.

```bash
# Check that release-critical areas have specs
python3 .aget/patterns/validation/validate_spec_coverage.py
```

**Three-Part Check** (per L557):
- [ ] Specs EXIST for all release-critical areas (L559)
- [ ] Each spec has a V-test that checks substance, not scaffold (L555)
- [ ] V-tests run as BLOCKING gates

**Expected**: PASS (all specs covered with V-tests)
**Blocking**: If any release-critical area lacks spec or V-test, STOP and create before proceeding.

### V0.5: Template Sync Check (R-SYNC-001)

```bash
# Check private templates are synced to public
python3 .aget/patterns/validation/validate_template_sync.py
```
**Expected**: PASS (all templates synced)
**Blocking**: Missing templates block release

### V0.6: Feature-Descriptive Content Review (R-REL-042, L585)

**Applies to**: Major and minor releases only (not patches).

**Purpose**: Ensure specs describing capabilities are aligned with release features.

**Artifact Inventory**:

| Artifact | Section | Review For |
|----------|---------|------------|
| AGET_IDENTITY_SPEC.yaml | `scope.manages` | New capabilities added this release |
| AGET_POSITIONING_SPEC.yaml | `differentiators` | New differentiators |
| AGET_POSITIONING_SPEC.yaml | `value_proposition` | New value propositions |
| CHANGELOG.md | Version Support | "Latest Stable" reflects this version |

**V-Test for Feature-Descriptive Review**:

```bash
# Check identity spec changelog has entry for this year
grep -q "$(date +%Y)" specs/AGET_IDENTITY_SPEC.yaml && echo "PASS" || echo "WARN: Review AGET_IDENTITY_SPEC"

# Check positioning spec changelog has entry for this year
grep -q "$(date +%Y)" specs/AGET_POSITIONING_SPEC.yaml && echo "PASS" || echo "WARN: Review AGET_POSITIONING_SPEC"

# Check CHANGELOG "Latest Stable" matches release version
grep "Latest Stable" CHANGELOG.md | grep -q "X.Y.Z" && echo "PASS" || echo "FAIL: Update Latest Stable"
```

**Checklist** (manual review):

- [ ] AGET_IDENTITY_SPEC `scope.manages` includes new capabilities
- [ ] AGET_POSITIONING_SPEC `differentiators` includes new differentiators
- [ ] AGET_POSITIONING_SPEC `value_proposition` updated for new value
- [ ] CHANGELOG "Latest Stable" shows this version

**Advisory**: This is a SHOULD requirement. Skip with acknowledgment for releases with no new capabilities.

**Distinction from Version-Indicator Artifacts (L584)**:

| Class | Check Type | When |
|-------|------------|------|
| Version-indicator (L584) | Automated | Every release |
| Feature-descriptive (L585) | Manual review | Major/minor only |

### V0.7: Release Handoff Preparation (R-REL-019, L587)

**Purpose**: Ensure release handoff documentation serves external audiences, not just internal teams.

**Background**: Per L587 (Curse of Knowledge Documentation Gap), internal teams document WHAT to do but assume readers understand WHY and WHICH. External fleets cannot execute handoffs that assume internal knowledge.

**Checklist** (per R-REL-019-02 through R-REL-019-06):

- [ ] "Context for External Fleets" section planned
- [ ] New tools have what/when/how documentation planned
- [ ] L-doc references will be EXPLAINED (not just labeled)
- [ ] Archetype features mapped to specific archetypes
- [ ] Handoff explains WHY and WHICH, not just WHAT
- [ ] Reviewed with "curse of knowledge" lens: Would someone outside our team understand this?

**V-Test for Handoff Readiness**:

```bash
# Check template exists
[ -f "handoffs/TEMPLATE_RELEASE_HANDOFF.md" ] && echo "PASS" || echo "FAIL: Missing template"
```

**Anti-Patterns to Prevent** (L587):

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| Label without lesson | "per L582" | Explain the problem/rule/commands |
| Tool without tutorial | "run validate_skill_dependencies.py" | Add what/when/how/if-fails |
| Quantity without mapping | "26 archetype skills" | Table: archetype → skills |
| Action without purpose | "deploy aget-file-issue" | Explain what it does and why |
| Path without placeholder | "~/github/aget-framework" | Use "~/path/to/framework" |

**Advisory**: This phase prepares for Phase 6.4 (Release Handoff Creation). Actual handoff is created after release completion.

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

### 6.3 Verify Public-Facing Version Indicators (R-REL-035, R-REL-036, R-REL-037)

**Critical** (L578): Users see README badges and GitHub Releases, not version.json.

#### R-REL-035: README Version Badges

```bash
# Check ALL 12 templates have correct version badge
for t in template-*-aget; do
  VERSION=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' $t/README.md | head -1)
  echo "$t: $VERSION"
done
# Expected: ALL show vX.Y.Z
```

#### R-REL-036: .github Repo Pushed

```bash
# Verify .github is NOT ahead of origin
git -C /path/to/aget-framework/.github status -sb
# Expected: "## main" (not "## main...origin/main [ahead N]")
```

#### R-REL-037: GitHub Release Created

```bash
# Verify GitHub Release exists (not just tag)
gh release view vX.Y.Z --repo aget-framework/aget
# Expected: Release details displayed (not "release not found")
```

**V-Tests**:

| ID | Test | Command | BLOCKING |
|----|------|---------|----------|
| V-REL-035 | README badges correct | Loop check all template README.md | **YES** |
| V-REL-036 | .github repo pushed | `git -C .github status -sb` | **YES** |
| V-REL-037 | GitHub Release exists | `gh release view vX.Y.Z` | **YES** |

**Decision_Point**: All public-facing indicators updated? [GO/NOGO]

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

## Phase 7: Pre-Push Gate (L517, CAP-REL-009, CAP-SOP-001)

**BLOCKING**: This phase MUST pass BEFORE executing Phase 3.3 (Push).

**Purpose**: Prevent Declarative_Release anti-pattern by verifying all version metadata is updated before push.

### 7.1 Run Release Validator

```bash
python3 validation/validate_release_gate.py X.Y.Z
```

**Expected**: PASS (exit code 0)
**BLOCKING**: Do NOT proceed with push if FAIL

### 7.2 V-REL Tests

| ID | Test | Phase | Command | BLOCKING |
|----|------|-------|---------|----------|
| V-REL-001 | Release validator passes | Pre-Push | `python3 validation/validate_release_gate.py $VERSION` | **YES** |
| V-REL-002 | Framework version.json correct | 1.2 | `jq -r '.aget_version' aget/.aget/version.json` | **YES** |
| V-REL-003 | ALL 12 templates correct | 1.3 | Loop check all template version.json | **YES** |
| V-REL-004 | CHANGELOG entry exists | 1.2 | `grep "$VERSION" CHANGELOG.md` | No |
| V-REL-005 | Git tag exists | 3.2 | `git tag -l "v$VERSION"` | No |
| V-REL-006 | migration_history updated | 1.2 | `jq '.migration_history[-1]' aget/.aget/version.json` | No |
| V-REL-007 | No instance exceeds framework | Pre-Push | `python3 validation/validate_version_ceiling.py` | **YES** |

### 7.3 V-Test Execution

```bash
# V-REL-002: Framework version
jq -r '.aget_version' /path/to/aget-framework/aget/.aget/version.json
# Expected: X.Y.Z

# V-REL-003: All templates (12 total)
TEMPLATES=(
  template-supervisor-aget
  template-worker-aget
  template-advisor-aget
  template-consultant-aget
  template-developer-aget
  template-spec-engineer-aget
  template-analyst-aget
  template-architect-aget
  template-qa-aget
  template-devops-aget
  template-documenter-aget
  template-researcher-aget
)
for t in "${TEMPLATES[@]}"; do
  VERSION=$(jq -r '.aget_version' /path/to/aget-framework/$t/.aget/version.json 2>/dev/null || echo "NOT_FOUND")
  echo "$t: $VERSION"
done
# Expected: ALL show X.Y.Z (or NOT_FOUND for unpublished templates)

# V-REL-006: migration_history
jq -r '.migration_history[-1]' /path/to/aget-framework/aget/.aget/version.json
# Expected: Contains "vX.Y.Z" or "X.Y.Z"

# V-REL-007: Version ceiling (when validator exists)
python3 validation/validate_version_ceiling.py /path/to/instances
# Expected: PASS (no instance exceeds framework version)
```

### 7.4 Decision Point

**Mandatory Check Before Push**:
- [ ] V-REL-001 PASS (release validator)
- [ ] V-REL-002 PASS (framework version.json)
- [ ] V-REL-003 PASS (all templates, or documented exceptions)
- [ ] V-REL-007 PASS (version ceiling)

**Anti-Patterns to Prevent** (L517):
- **Declarative_Release**: Version in commit message but not version.json
- **Version_Overrun**: Instance version exceeds framework version
- **Template_Abandonment**: Templates left behind during upgrade

**Decision_Point**: All BLOCKING V-tests pass? [GO/NOGO]

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

## Release Observability Tooling (v3.6.0, L605)

The following scripts provide persistent, structured observability throughout the release process. All are registered in `SCRIPT_REGISTRY.yaml`.

| Script | CAP | Purpose | When to Use |
|--------|-----|---------|-------------|
| `scripts/validation_logger.py` | CAP-REL-021 | Wraps validation scripts with JSONL logging | Every validation step |
| `scripts/run_gate.py` | CAP-REL-022 | Records gate completion, enforces sequencing | Gate boundaries |
| `scripts/release_snapshot.py` | CAP-REL-023 | Pre/post release state capture + diff | Gate 0 (pre) and final gate (post) |
| `scripts/propagation_audit.py` | CAP-REL-024 | Verifies template propagation | After template updates |
| `scripts/health_logger.py` | CAP-REL-025 | Persistent healthcheck logging | Session wake-up, ad hoc |

**Usage examples:**

```bash
# Wrap a validation with persistent logging
python3 scripts/validation_logger.py --wrap scripts/pre_release_validation.py -- --version 3.6.0

# Record gate completion
python3 scripts/run_gate.py --gate G0 --version 3.6.0 --status pass --summary "V-G0.1 PASS, V-G0.2 PASS"

# Pre-release snapshot
python3 scripts/release_snapshot.py --version 3.6.0 --phase pre --skip-gh

# Check propagation
python3 scripts/propagation_audit.py --version 3.6.0 --check
```

---

## References

- AGET_RELEASE_SPEC.md (CAP-REL-001 through CAP-REL-025)
- AGET_VERSIONING_CONVENTIONS.md
- RELEASE_VERIFICATION_CHECKLIST.md
- L440: Manager Migration Verification Gap
- L435: Retrospective Requirement (CAP-REASON-008)
- L605: Release Observability Gap

---

## Changelog

### v1.8.0 (2026-02-21)

- **Added Release Observability Tooling section** (CAP-REL-021 through 025, L605)
  - Tool reference table: 5 scripts with CAP mappings and usage guidance
  - Usage examples for validation logging, gate recording, snapshots, propagation
  - Updated Implements header to include CAP-REL-021-025 and L605

### v1.7.0 (2026-02-15)

- **Added V0.7: Release Handoff Preparation** (R-REL-019, L587)
  - Curse of knowledge mitigation checklist
  - Anti-patterns table (label without lesson, tool without tutorial, etc.)
  - External audience review step
  - References TEMPLATE_RELEASE_HANDOFF.md
- Updated Implements header to include CAP-REL-020, R-REL-019, L587

### v1.6.0 (2026-02-15)

- **Added V0.6: Feature-Descriptive Content Review** (R-REL-042, L585)
  - Manual review phase for major/minor releases
  - AGET_IDENTITY_SPEC scope.manages check
  - AGET_POSITIONING_SPEC differentiators/value_proposition check
  - CHANGELOG "Latest Stable" check
  - Distinguishes from version-indicator checks (L584)
- Updated Implements header to include CAP-REL-019, R-REL-042, L585

### v1.5.0 (2026-02-14)

- **Added Phase 6.3: Public-Facing Version Indicators** (L578)
  - R-REL-035: README version badges (all 12 templates)
  - R-REL-036: .github repo pushed (14 repos total)
  - R-REL-037: GitHub Release created (not just tags)
  - V-REL-035/036/037 blocking tests
- Updated Scope section with explicit 14-repo count
- Added Public-Facing Version Indicators callout

### v1.2.0 (2026-01-11)

- **Added Phase 7: Pre-Push Gate** (L517, CAP-REL-009, CAP-SOP-001)
  - BLOCKING verification before git push
  - V-REL-001 through V-REL-007 tests
  - Prevents Declarative_Release anti-pattern
  - All 12 templates validation
  - Version ceiling constraint enforcement
- Updated Implements header (CAP-REL-009, CAP-REL-010, CAP-SOP-001)

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
