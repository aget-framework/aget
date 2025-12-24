# R-PUB-001: Public Release Completeness

**Version**: 1.1
**Date**: 2025-12-24
**Status**: Active
**Category**: Release Management
**Priority**: HIGH

---

## Purpose

Define completeness criteria for public framework releases to ensure user-visible artifacts are consistent, accessible, and authoritative.

**Problem Addressed**: Gap between internal version progression (version.json updates, commits) and external visibility (GitHub Releases, organization homepage, user documentation). See L358 (Tags ≠ Releases on GitHub).

**Scope**: All aget-framework public repositories (aget/ core + 6 templates)

---

## Requirements

### R-PUB-001-01: GitHub Release Creation (Ubiquitous)

**Statement**: The system SHALL create GitHub Release for all managed repositories when framework version increments.

**Rationale**: Users discover versions via GitHub Releases page, not git tags. Tags are developer artifacts; Releases are user-facing.

**Verification**:
```bash
# For each repo, verify release exists
gh release view vX.Y.Z --repo aget-framework/REPO_NAME
# Exit code 0 = pass, non-zero = fail
```

**Implements**: External visibility requirement (L358)

---

### R-PUB-001-02: Release Artifact Completeness (State-Driven)

**Statement**: WHERE GitHub Release is created, the release SHALL include:
- Title format: "vX.Y.Z - Brief Description"
- Body with: highlights, learnings, link to delta spec
- Git tag (vX.Y.Z)
- Published status (not draft)

**Rationale**: Incomplete releases confuse users (missing context, broken links, draft status suggests unreleased).

**Verification**:
```python
release = gh_api(f"repos/aget-framework/{repo}/releases/tags/vX.Y.Z")
assert release['name'].startswith('v')
assert len(release['body']) > 100  # Has content
assert not release['draft']
assert release['tag_name'] == 'vX.Y.Z'
```

**Implements**: Release quality standard

---

### R-PUB-001-03: Organization Homepage Currency (Event-Driven)

**Statement**: WHEN new version is released, the organization homepage SHALL display current version within 24 hours.

**Rationale**: First impression for new users. Outdated version badge suggests abandoned project.

**Verification**:
```bash
curl -s https://raw.githubusercontent.com/aget-framework/.github/main/profile/README.md | grep "version-X.Y.Z"
# If found = pass, else fail
```

**Implements**: Public visibility requirement

**Location**: `aget-framework/.github/profile/README.md`

---

### R-PUB-001-04: Version Badge Accuracy (Ubiquitous)

**Statement**: The version badge on organization homepage SHALL link to valid release URL.

**Rationale**: Broken badge link (404) or wrong repo erodes trust.

**Verification**:
```bash
# Extract badge URL
BADGE_URL=$(grep "img.shields.io/badge/version" .github/profile/README.md | sed -n 's/.*(\(https[^)]*\)).*/\1/p')

# Verify URL returns 200 OK
curl -I "$BADGE_URL" | grep "200 OK"
```

**Implements**: Link integrity requirement

---

### R-PUB-001-05: Changelog Accessibility (Event-Driven)

**Statement**: WHEN version is released, CHANGELOG.md SHALL be accessible via GitHub web UI at aget/CHANGELOG.md with entry for that version.

**Rationale**: Users expect CHANGELOG.md as canonical change list. Missing or outdated changelog suggests poor maintenance.

**Verification**:
```bash
curl -s https://raw.githubusercontent.com/aget-framework/aget/main/CHANGELOG.md | grep "## \[X.Y.Z\]"
# If found = pass
```

**Implements**: User documentation standard

---

### R-PUB-001-06: Release Notes Accessibility (Conditional)

**Statement**: IF version is major or minor release, THEN release notes SHALL be accessible via GitHub Release body or docs/.

**Rationale**: Major/minor releases introduce features/changes requiring narrative context beyond changelog bullets.

**Verification**:
```python
if is_major_or_minor(version):
    release = gh_api(f"repos/aget-framework/aget/releases/tags/v{version}")
    assert len(release['body']) > 500 or exists(f"docs/releases/v{version}.md")
```

**Implements**: Context documentation requirement

**Note**: Patch releases (X.Y.Z where Z > 0) may have minimal release notes.

---

### R-PUB-001-07: Historical Version Access (Ubiquitous)

**Statement**: Users SHALL be able to access any released version via GitHub Releases page or git tag.

**Rationale**: Reproducibility, rollback capability, historical research.

**Verification**:
```bash
# Via GitHub Release
gh release view vX.Y.Z --repo aget-framework/aget

# Via git tag
git ls-remote --tags https://github.com/aget-framework/aget | grep "vX.Y.Z"
```

**Implements**: Version persistence requirement

---

### R-PUB-001-08: Broken Link Prevention (Ubiquitous)

**Statement**: Release artifacts SHALL NOT contain broken links (404 responses) to framework resources.

**Rationale**: Broken links in release notes damage credibility, frustrate users.

**Verification**:
```python
# Extract all links from release body
links = extract_links(release['body'])

# Verify each returns 200 OK
for link in links:
    if link.startswith('http'):
        assert requests.get(link).status_code == 200
```

**Implements**: Quality assurance requirement

**Note**: External links (non-aget-framework) not required to validate (subject to external service availability).

---

### R-PUB-001-09: Latest Badge Correctness (Ubiquitous)

**Statement**: The system SHALL mark the current version as "Latest" in GitHub Releases for all managed repositories.

**Rationale**: GitHub displays "Latest" badge on most recent release chronologically. Retroactive releases or out-of-order tagging can mark wrong version as Latest, confusing users.

**Verification**:
```bash
# For each repo, check Latest badge
gh release list --repo aget-framework/REPO_NAME --limit 1 | grep "vX.Y.Z.*Latest"
# If found = pass, else fail
```

**Implements**: User navigation requirement (L360)

**Added**: v1.1 (2025-12-24) - Phase 2 validation enhancement

---

### R-PUB-001-10: Homepage Content Consistency (Ubiquitous)

**Statement**: The organization homepage content SHALL be consistent with version badge (code examples, roadmap, migration history all reference current version).

**Rationale**: Badge showing v2.11.0 but content showing v2.9.0 creates user confusion. Semantic consistency required, not just badge update.

**Verification**:
```bash
# Extract homepage content
content=$(curl -s https://raw.githubusercontent.com/aget-framework/.github/main/profile/README.md)

# Check code examples
echo "$content" | grep '"aget_version": "X.Y.Z"' || fail

# Check roadmap current marker
echo "$content" | grep 'vX.Y.Z (Current)' || fail

# Check version progression
echo "$content" | grep 'v2.5 → v2.6 → ... → vX.Y.Z' || fail
```

**Implements**: Content-badge alignment requirement (L361)

**Added**: v1.1 (2025-12-24) - Phase 2 validation enhancement

---

### R-PUB-001-11: Historical Release Completeness (Conditional)

**Statement**: IF templates have N releases, THEN core (aget/) SHALL have at least N-2 releases.

**Rationale**: Significant gap (e.g., templates at v2.11, core at v2.2) suggests incomplete historical release backfill. Small gap acceptable (templates update more frequently).

**Verification**:
```bash
# Count releases
aget_count=$(gh release list --repo aget-framework/aget --limit 100 | wc -l)
template_count=$(gh release list --repo aget-framework/template-worker-aget --limit 100 | wc -l)

# Calculate gap
gap=$((template_count - aget_count))

# Acceptable gap: ≤ 2 versions
if [ $gap -le 2 ]; then
  echo "PASS: Gap = $gap (acceptable)"
else
  echo "FAIL: Gap = $gap (threshold: 2)"
fi
```

**Implements**: Historical completeness requirement (L360)

**Added**: v1.1 (2025-12-24) - Phase 2 validation enhancement

**Note**: Does not require perfect parity (1:1). Allows 2-version acceptable gap for operational flexibility.

---

## Requirement Summary Table

| ID | Type | Statement Summary | Verification |
|----|------|-------------------|--------------|
| R-PUB-001-01 | Ubiquitous | Create GitHub Releases for all repos | `gh release view` |
| R-PUB-001-02 | State-Driven | Releases include title, body, tag, published | API inspection |
| R-PUB-001-03 | Event-Driven | Org homepage updated within 24h | Curl + grep |
| R-PUB-001-04 | Ubiquitous | Badge links to valid URL | HTTP 200 check |
| R-PUB-001-05 | Event-Driven | CHANGELOG.md has version entry | Curl + grep |
| R-PUB-001-06 | Conditional | Major/minor have release notes | Body length or file exists |
| R-PUB-001-07 | Ubiquitous | Users can access historical versions | Tag/release exists |
| R-PUB-001-08 | Ubiquitous | No broken links in releases | HTTP status checks |
| R-PUB-001-09 | Ubiquitous | Current version marked "Latest" | `gh release list` grep |
| R-PUB-001-10 | Ubiquitous | Homepage content matches badge version | Content parsing |
| R-PUB-001-11 | Conditional | Core releases within 2 of templates | Release count comparison |

---

## Traceability

### Implements

| Requirement | Implements | Evidence |
|-------------|------------|----------|
| R-PUB-001-01 | L358 (tags ≠ releases) | GitHub Releases must be created explicitly |
| R-PUB-001-02 | Release quality standard | Incomplete releases confuse users |
| R-PUB-001-03 | Public visibility | Organization homepage is user entry point |
| R-PUB-001-04 | Trust/credibility | Broken links damage reputation |
| R-PUB-001-05 | User documentation | CHANGELOG is expected artifact |
| R-PUB-001-06 | Context provision | Major changes need narrative |
| R-PUB-001-07 | Reproducibility | Historical access required |
| R-PUB-001-08 | Quality assurance | Link rot prevention |
| R-PUB-001-09 | L360 (external validation) | Latest badge must reflect actual current version |
| R-PUB-001-10 | L361 (badge-content consistency) | Content must align with badge version |
| R-PUB-001-11 | L360 (completeness validation) | Historical release parity prevents gaps |

### Validated By

| Requirement | Test | Location |
|-------------|------|----------|
| R-PUB-001-01 | check_github_releases_exist() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-02 | Manual validation | sops/RELEASE_VERIFICATION_CHECKLIST.md |
| R-PUB-001-03 | check_org_homepage_currency() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-04 | check_version_badge_accuracy() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-05 | check_changelog_accessibility() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-06 | Manual validation | sops/RELEASE_VERIFICATION_CHECKLIST.md |
| R-PUB-001-07 | check_historical_version_access() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-08 | check_broken_links() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-09 | check_latest_badge_correct() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-10 | check_homepage_content_consistency() | .aget/patterns/release/post_release_validation.py |
| R-PUB-001-11 | check_historical_release_completeness() | .aget/patterns/release/post_release_validation.py |

### Referenced In

| Artifact | Reference |
|----------|-----------|
| sops/PUBLIC_RELEASE_VALIDATION.md | Manual validation checklist |
| .aget/patterns/release/post_release_validation.py | Automated validation script |
| sops/RELEASE_PROCESS.md | Phase 4: Post-Release Validation |
| docs/VERSIONING.md | User-facing version documentation |

---

## Success Criteria

**Release is complete WHEN**:
- All R-PUB-001-01 through R-PUB-001-11 requirements satisfied
- Post-release validation script exits with code 0 (9/9 automated checks passing)
- Manual validation checklist 100% checked (2 manual checks)

**Release is incomplete WHEN**:
- Any requirement fails validation
- Broken links detected
- Organization homepage shows outdated version
- Latest badge shows wrong version
- Homepage content inconsistent with badge version
- Historical release gap exceeds threshold

**Action on failure**: DO NOT announce release publicly until gaps closed.

**Automation Coverage** (v1.1):
- Automated: 9/11 requirements (82%)
- Manual: 2/11 requirements (18%)

---

## Evolution History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-24 | Initial specification (8 requirements) |
| 1.1 | 2025-12-24 | Added R-PUB-001-09 (Latest badge), R-PUB-001-10 (content consistency), R-PUB-001-11 (historical completeness) - Phase 2 validation enhancement |

---

## Related Documents

- **L358**: Tags ≠ Releases on GitHub (learning that motivated this spec)
- **Gap Analysis**: VERSION_HISTORY.md (documents historical gaps)
- **RELEASE_PROCESS.md**: Phase 4 implements these requirements
- **post_release_validation.py**: Automated verification

---

*R-PUB-001: Public Release Completeness*
*Ensures user-visible release artifacts are complete, accessible, and authoritative*
*Created: 2025-12-24 | Owner: private-aget-framework-AGET*
