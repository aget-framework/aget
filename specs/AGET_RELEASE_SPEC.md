# AGET Release Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Process (Release Management)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-11
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_RELEASE_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.2
**Related Specs**: AGET_FRAMEWORK_SPEC, AGET_VERSIONING_CONVENTIONS

---

## Abstract

This specification defines release requirements for the AGET framework, including version numbering, manager migration protocol (R-REL-006), multi-repo coordination, and release documentation. It formalizes patterns validated in v3.0.0 through v3.1.0.

## Motivation

Release challenges observed in practice:

1. **Manager version drift**: Managing agent at v3.0.0 while releasing v3.1.0 (L440)
2. **Missing CHANGELOGs**: Template releases without changelog entries
3. **Incomplete GitHub Releases**: Tags exist but Releases don't
4. **Verification theater**: Gate 6 checkboxes without actual verification

L358 (Release Artifact Gaps) and L440 (Manager Migration Verification Gap) revealed these gaps.

## Scope

**Applies to**: All AGET framework releases (aget/ and templates).

**Defines**:
- Release process requirements
- Version numbering rules
- Manager migration protocol
- Multi-repo coordination
- Release documentation requirements

**Does not cover**:
- Version file format (see AGET_VERSIONING_CONVENTIONS)
- PROJECT_PLAN format (see AGET_PROJECT_PLAN_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "release"
    version: "1.0.0"
    inherits: "aget_core"

  release:
    Release_Version:
      skos:definition: "Semantic version identifying a release"
      aget:format: "v{MAJOR}.{MINOR}.{PATCH}[-{prerelease}]"
      skos:example: "v3.2.0, v3.2.0-alpha"

    Manager_Migration:
      skos:definition: "Updating managing agent version before releasing managed repos"
      skos:related: ["R-REL-006", "L440"]

    Multi_Repo_Coordination:
      skos:definition: "Synchronized release across multiple repositories"
      aget:repos: ["aget", "template-*-aget"]

    Release_Gate:
      skos:definition: "Verification checkpoint in release process"
      skos:related: ["V_Test", "CAP-TEST-006"]

  artifacts:
    CHANGELOG:
      skos:definition: "Document tracking notable changes per version"
      aget:format: "Keep a Changelog"
      aget:location: "CHANGELOG.md"

    GitHub_Release:
      skos:definition: "GitHub release object with tag and notes"
      aget:required: true

    Deep_Release_Notes:
      skos:definition: "Narrative release documentation beyond CHANGELOG bullets"
      aget:location: "release-notes/v{VERSION}.md"

  anti_patterns:
    Version_Drift:
      skos:definition: "Managing agent version behind managed repos"
      aget:anti_pattern: true
      skos:related: ["L429", "L440"]

    Declarative_Release:
      skos:definition: "Marking release complete without V-test verification"
      aget:anti_pattern: true
      skos:related: ["L440"]
```

---

## Requirements

### CAP-REL-001: Release Process Requirements

**SHALL** requirements for release process:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-001-01 | Releases SHALL follow PROJECT_PLAN gates | Structured execution |
| CAP-REL-001-02 | Every gate SHALL have V-tests | Prevents declarative completion |
| CAP-REL-001-03 | Release gates SHALL be executed in order | Dependency management |
| CAP-REL-001-04 | BLOCKING V-tests SHALL halt on failure | Critical path protection |

### CAP-REL-002: Version Numbering

**SHALL** requirements for version numbers:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-002-01 | Versions SHALL follow semver (MAJOR.MINOR.PATCH) | Industry standard |
| CAP-REL-002-02 | Breaking changes SHALL increment MAJOR | Compatibility signaling |
| CAP-REL-002-03 | New features SHALL increment MINOR | Feature signaling |
| CAP-REL-002-04 | Bug fixes SHALL increment PATCH | Fix signaling |
| CAP-REL-002-05 | Pre-releases SHALL use suffix (-alpha, -beta, -rc) | Stability signaling |

**Version Progression:**

```
v3.1.0 → v3.2.0-alpha → v3.2.0-beta → v3.2.0-rc1 → v3.2.0
```

### CAP-REL-003: Manager Migration Protocol (R-REL-006)

**SHALL** requirements for manager migration (L440 critical):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R-REL-006-01 | Managing agent SHALL update version BEFORE releasing | Prevents version drift |
| R-REL-006-02 | Manager version update SHALL be verified by V-test | No declarative completion |
| R-REL-006-03 | Manager version SHALL match release version | Consistency |
| R-REL-006-04 | V-test for manager migration SHALL be BLOCKING | Critical path |

**Manager Migration V-Test:**

```markdown
#### V7.0.1: Manager version is {VERSION} (R-REL-006)
```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='{VERSION}' else 'FAIL: '+v['aget_version'])"
```
**Expected:** PASS
**BLOCKING:** Do NOT proceed if FAIL
```

**Migration Sequence:**

```
1. Manager updates own version.json to {VERSION}
2. V7.0.1 verifies manager version (BLOCKING)
3. Manager updates aget/ version.json
4. Manager updates template version.json files
5. Continue with release gates
```

### CAP-REL-004: Multi-Repo Coordination

**SHALL** requirements for multi-repo releases:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-004-01 | All repos SHALL be at same version after release | Consistency |
| CAP-REL-004-02 | Version updates SHALL be atomic per repo | Commit hygiene |
| CAP-REL-004-03 | Tags SHALL be created for all repos | Release tracking |
| CAP-REL-004-04 | GitHub Releases SHALL be created for all repos | User visibility |

**Repo Coordination Order:**

```
1. private-aget-framework-AGET (manager) → version bump first
2. aget-framework/aget (core) → version bump + CHANGELOG
3. template-supervisor-aget → version bump + CHANGELOG
4. template-worker-aget → version bump + CHANGELOG
5. template-advisor-aget → version bump + CHANGELOG
6. template-consultant-aget → version bump + CHANGELOG
7. template-developer-aget → version bump + CHANGELOG
8. template-spec-engineer-aget → version bump + CHANGELOG
```

### CAP-REL-005: CHANGELOG Requirements

**SHALL** requirements for CHANGELOGs:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-005-01 | Every repo SHALL have CHANGELOG.md | Change tracking |
| CAP-REL-005-02 | CHANGELOG SHALL follow Keep a Changelog format | Standardization |
| CAP-REL-005-03 | Every release SHALL have CHANGELOG entry | Completeness |
| CAP-REL-005-04 | Entry SHALL include version, date, and theme | Identification |

**CHANGELOG Format:**

```markdown
## [{VERSION}] - {YYYY-MM-DD} - "{Theme}"

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Fix 1

### Notes
- Context or migration notes
```

### CAP-REL-006: GitHub Release Requirements

**SHALL** requirements for GitHub Releases:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-006-01 | Every tag SHALL have corresponding GitHub Release | User visibility |
| CAP-REL-006-02 | Release notes SHALL summarize CHANGELOG | Accessibility |
| CAP-REL-006-03 | Pre-releases SHALL be marked as such | Stability signaling |

### CAP-REL-007: Release Documentation

**SHALL** requirements for release documentation:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-REL-007-01 | Major/minor releases SHALL have deep release notes | Context |
| CAP-REL-007-02 | Deep notes SHALL explain "why" beyond CHANGELOG | Understanding |
| CAP-REL-007-03 | Breaking changes SHALL include migration guide | User support |

**Deep Release Notes Location:**

```
private-aget-framework-AGET/release-notes/v{VERSION}.md
```

### CAP-REL-008: Organization Homepage Update

**SHALL** requirements for homepage updates (R-REL-010):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R-REL-010-01 | Homepage SHALL show current version | User information |
| R-REL-010-02 | Roadmap SHALL reflect release status | Planning visibility |
| R-REL-010-03 | Next version SHALL be documented | Roadmap clarity |

### CAP-REL-009: Release Verification (L517)

**SHALL** requirements for release verification before push:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-009-01 | ubiquitous | The SYSTEM shall run validate_release_gate.py before push | Automated verification |
| CAP-REL-009-02 | ubiquitous | The SYSTEM shall BLOCK release if validation fails | Gate enforcement |
| CAP-REL-009-03 | ubiquitous | The SYSTEM shall verify framework version.json matches release | Source of truth |
| CAP-REL-009-04 | ubiquitous | The SYSTEM shall verify ALL templates match release version | R-REL-015 compliance |

**Prevents**: Declarative_Release anti-pattern (declaring version without updating metadata).

### CAP-REL-010: Version Ceiling Constraint (L517)

**SHALL** requirements for instance-framework version relationship:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-010-01 | ubiquitous | Instance aget_version SHALL NOT exceed framework aget_version | Version ceiling |
| CAP-REL-010-02 | conditional | IF instance > framework THEN the SYSTEM shall flag Version_Overrun | Detection |
| CAP-REL-010-03 | conditional | IF Version_Overrun detected THEN the SYSTEM shall block upgrade | Prevention |

**Prevents**: Version_Overrun anti-pattern (instance version exceeds framework version).

### CAP-SOP-001: SOP Verification Requirements (L517)

**SHALL** requirements for SOP verification:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-SOP-001-01 | ubiquitous | SOPs for releases SHALL include V-tests | Verified process |
| CAP-SOP-001-02 | ubiquitous | Each SOP phase SHALL have ≥1 BLOCKING V-test | Gate discipline |
| CAP-SOP-001-03 | conditional | IF step can be skipped silently THEN V-test SHALL verify | No silent failures |

**Prevents**: SOP_Theater anti-pattern (procedural steps without verification).

---

## Release Gate Structure

Standard release gates per PROJECT_PLAN:

| Gate | Purpose | V-Tests | BLOCKING |
|------|---------|---------|----------|
| G7.0 | Manager Migration | V7.0.1-V7.0.3 | **YES** (V7.0.1) |
| G7.1 | Version Updates | V7.1.1-V7.1.3 | No |
| G7.2 | Documentation | V7.2.1-V7.2.3 | No |
| G7.3 | Git Operations | V7.3.1-V7.3.4 | No |
| G7.4 | GitHub Operations | V7.4.1-V7.4.4 | No |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-REL-001-* | validate_project_plan.py | Planned |
| CAP-REL-002-* | validate_version_consistency.py | Implemented |
| R-REL-006-* | validate_release_gate.py | Planned |
| CAP-REL-004-* | validate_fleet.py | Implemented |
| CAP-REL-005-* | validate_changelog.py | Planned |
| CAP-REL-006-* | gh release view | Manual |
| R-REL-010-* | validate_homepage_messaging.py | Planned |

---

## Anti-Patterns

### Anti-Pattern 1: Version Drift (L440)

```
❌ ANTI-PATTERN: Manager behind managed repos

private-aget-framework-AGET: v3.0.0  ← Still at old version!
aget-framework/aget: v3.1.0          ← Released
templates: v3.1.0                    ← Released
```

```
✅ CORRECT: Manager updates first (R-REL-006)

private-aget-framework-AGET: v3.1.0  ← Updated FIRST
aget-framework/aget: v3.1.0          ← Then released
templates: v3.1.0                    ← Then released
```

### Anti-Pattern 2: Missing GitHub Releases (L358)

```
❌ ANTI-PATTERN: Tags without Releases

$ git tag -l v3.1.0
v3.1.0  ← Tag exists

$ gh release view v3.1.0
release not found  ← Release missing!
```

### Anti-Pattern 3: Declarative Release Completion (L440)

```markdown
❌ ANTI-PATTERN: Checkbox without verification

- [x] Manager version updated  ← Marked but never verified!
- [x] Templates at v3.1.0      ← Marked but never checked!
```

---

## References

- L358: Release Artifact Gaps
- L429: Version Inventory Requirement
- L440: Manager Migration Verification Gap
- SOP_release_process.md
- AGET_VERSIONING_CONVENTIONS.md
- Keep a Changelog (https://keepachangelog.com)
- Semantic Versioning (https://semver.org)

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial specification
- Formalized R-REL-006 (Manager Migration)
- Multi-repo coordination requirements
- CHANGELOG and GitHub Release requirements
- Organization homepage update requirements

---

*AGET_RELEASE_SPEC.md — Release standards for AGET framework*
*"A checkbox is not a verification. A passing test is."* — L440
