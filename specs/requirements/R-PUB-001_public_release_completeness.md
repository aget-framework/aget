# R-PUB-001: Public Release Completeness

**Version**: 1.0
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

### Validated By

| Requirement | Test | Location |
|-------------|------|----------|
| R-PUB-001-01 | test_github_releases_exist() | tests/test_public_release_completeness.py |
| R-PUB-001-02 | test_release_artifact_completeness() | tests/test_public_release_completeness.py |
| R-PUB-001-03 | test_org_homepage_currency() | tests/test_public_release_completeness.py |
| R-PUB-001-04 | test_version_badge_accuracy() | tests/test_public_release_completeness.py |
| R-PUB-001-05 | test_changelog_accessibility() | tests/test_public_release_completeness.py |
| R-PUB-001-06 | test_release_notes_accessibility() | tests/test_public_release_completeness.py |
| R-PUB-001-07 | test_historical_version_access() | tests/test_public_release_completeness.py |
| R-PUB-001-08 | test_broken_link_prevention() | tests/test_public_release_completeness.py |

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
- All R-PUB-001-01 through R-PUB-001-08 requirements satisfied
- Post-release validation script exits with code 0
- Manual validation checklist 100% checked

**Release is incomplete WHEN**:
- Any requirement fails validation
- Broken links detected
- Organization homepage shows outdated version

**Action on failure**: DO NOT announce release publicly until gaps closed.

---

## Evolution History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-24 | Initial specification (8 requirements) |

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
