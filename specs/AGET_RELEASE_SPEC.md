# AGET Release Specification

**Version**: 1.6.0
**Status**: Active
**Category**: Process (Release Management)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-02-15
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

  timing:
    Release_Window:
      skos:definition: "Designated time periods for public release activities"
      skos:scopeNote: "Preferred windows minimize disruption during peak work days"
      aget:preferred_windows: ["Thursday AM", "Friday PM"]
      aget:avoid_windows: ["Monday", "Tuesday", "Wednesday", "Thursday PM", "Friday AM"]
      skos:related: ["CAP-REL-011"]

  content_alignment:
    Feature_Descriptive_Artifact:
      skos:definition: "Artifact containing content that describes framework capabilities and should evolve with major/minor releases"
      skos:example: ["AGET_IDENTITY_SPEC scope.manages", "AGET_POSITIONING_SPEC differentiators"]
      skos:related: ["L585", "R-REL-042"]
      skos:narrower: ["Version_Indicator_Artifact"]

    Version_Indicator_Artifact:
      skos:definition: "Artifact containing embedded version numbers or dates requiring automated release-time updates"
      skos:example: ["version.json", "AGENTS.md @aget-version"]
      skos:related: ["L584", "R-REL-VER-001"]

    Feature_Drift:
      skos:definition: "Anti-pattern where version is updated but feature-descriptive content remains stale"
      aget:anti_pattern: true
      skos:related: ["L585"]

  anti_patterns:
    Version_Drift:
      skos:definition: "Managing agent version behind managed repos"
      aget:anti_pattern: true
      skos:related: ["L429", "L440"]

    Declarative_Release:
      skos:definition: "Marking release complete without V-test verification"
      aget:anti_pattern: true
      skos:related: ["L440"]

    Off_Window_Release:
      skos:definition: "Releasing outside designated release windows"
      aget:anti_pattern: true
      skos:related: ["CAP-REL-011"]

  scope:
    Version_Scope:
      skos:definition: "Planning artifact defining boundaries, objectives, work items, timeline, and success criteria for a release"
      aget:location: "planning/VERSION_SCOPE_vX.Y.Z.md"
      aget:template: "planning/TEMPLATE_VERSION_SCOPE.md"
      skos:related: ["R-REL-020", "CAP-REL-012"]

    MVP_Scope:
      skos:definition: "Must-Ship items that BLOCK release if incomplete"
      skos:broader: "Version_Scope"
      skos:related: ["Release_Blocker"]

    Release_Phase:
      skos:definition: "Discrete stage in release lifecycle"
      skos:narrower: ["Pre_Release_Phase", "Release_Execution_Phase", "Post_Release_Phase"]

    Release_Retrospective:
      skos:definition: "Structured review after release to capture lessons learned"
      skos:related: ["Post_Release_Phase", "L_Doc"]

    Rollback_Plan:
      skos:definition: "Contingency procedure for reverting release on critical issues"
      skos:related: ["CAP-REL-015"]
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

### R-REL-VER-001: Version-Bearing File Coherence (L521)

**SHALL** requirements for version-bearing file coherence:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R-REL-VER-001-01 | All Version_Bearing_Files SHALL display same version | Coherence |
| R-REL-VER-001-02 | Version_Json SHALL be PRIMARY source of truth | Single source |
| R-REL-VER-001-03 | Derived files (AGENTS.md, manifest.yaml, README.md) SHALL match primary | Consistency |
| R-REL-VER-001-04 | validate_version_inventory.py SHALL check ALL Version_Bearing_Files | Enforcement |
| R-REL-VER-001-05 | Version updates SHALL update ALL Version_Bearing_Files atomically | Completeness |

**Version-Bearing File Enumeration:**

| File | Pattern | Source |
|------|---------|--------|
| `.aget/version.json` | `"aget_version": "X.Y.Z"` | PRIMARY |
| `AGENTS.md` | `@aget-version: X.Y.Z` | Derived |
| `manifest.yaml` | `version: X.Y.Z` | Derived |
| `README.md` | `**Current Version**: vX.Y.Z` | Derived |
| `CHANGELOG.md` | `## [X.Y.Z]` entry | Derived |

**V-Test for Version Coherence:**

```bash
# Check all version-bearing files match
python3 aget/validation/validate_version_inventory.py --all-files
```

**Prevents**: Version_Drift_File anti-pattern (derived file showing stale version).

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

### CAP-REL-011: Release Window Timing

**SHOULD** requirements for release timing:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-011-01 | conditional | IF releasing to public repos THEN the SYSTEM should verify Release_Window | Disruption minimization |
| CAP-REL-011-02 | conditional | IF Off_Window_Release THEN the SYSTEM should warn and require acknowledgment | Intentional override |
| CAP-REL-011-03 | ubiquitous | The SYSTEM should log release timing for retrospective analysis | Pattern tracking |

**Preferred Release Windows:**

| Window | Days | Times | Rationale |
|--------|------|-------|-----------|
| **Preferred** | Thursday | AM (before 12:00) | Mid-week buffer, weekend discovery |
| **Preferred** | Friday | PM (after 12:00) | Week completion, weekend discovery |
| **Avoid** | Mon-Wed | All day | Peak collaboration days |
| **Avoid** | Thursday | PM | Insufficient response time |
| **Avoid** | Friday | AM | Rushed fixes before weekend |

**V-Test for Release Window:**

```bash
# Check current day/time is in preferred window
day=$(date +%A)
hour=$(date +%H)
if [[ "$day" == "Thursday" && $hour -lt 12 ]] || [[ "$day" == "Friday" && $hour -ge 12 ]]; then
  echo "PASS: In preferred release window ($day $(date +%H:%M))"
else
  echo "WARN: Outside preferred release window ($day $(date +%H:%M)) - acknowledge to proceed"
fi
```

**Prevents**: Off_Window_Release anti-pattern (releasing during peak disruption periods).

**Note**: This is a SHOULD requirement (advisory). Emergency releases may override with acknowledgment.

### CAP-REL-012: VERSION_SCOPE Requirement (R-REL-020)

**SHALL** requirements for VERSION_SCOPE documentation:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-020-01 | conditional | BEFORE releasing minor/major version, THE release manager SHALL create VERSION_SCOPE document | Explicit scope definition |
| R-REL-020-02 | ubiquitous | VERSION_SCOPE SHALL define MVP (Must Ship) items | Release readiness criteria |
| R-REL-020-03 | ubiquitous | VERSION_SCOPE SHALL define Full Scope (Nice to Have) items | Scope completeness |
| R-REL-020-04 | ubiquitous | VERSION_SCOPE SHALL define Out of Scope items with rationale | Boundary clarity |
| R-REL-020-05 | ubiquitous | VERSION_SCOPE SHALL include measurable success criteria | Release quality measurement |

**When Required:**

| Release Type | VERSION_SCOPE | Rationale |
|--------------|:-------------:|-----------|
| Major (vX.0.0) | **REQUIRED** | Breaking changes need explicit scope |
| Minor (vX.Y.0) | **REQUIRED** | New features need explicit scope |
| Patch (vX.Y.Z) | OPTIONAL | Bug fixes can reference parent version |

**Template**: `planning/TEMPLATE_VERSION_SCOPE.md`

**Location**: `planning/VERSION_SCOPE_vX.Y.Z.md`

### CAP-REL-013: VERSION_SCOPE Content Requirements

**SHALL** requirements for VERSION_SCOPE content:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-021-01 | ubiquitous | VERSION_SCOPE SHALL include Release Objectives with success metrics | Goal clarity |
| R-REL-021-02 | ubiquitous | VERSION_SCOPE SHALL include three-phase release checklist | Process completeness |
| R-REL-021-03 | ubiquitous | VERSION_SCOPE SHALL include Timeline with phase dates | Planning visibility |
| R-REL-021-04 | ubiquitous | VERSION_SCOPE SHALL include Decision Log | Decision traceability |

### CAP-REL-014: VERSION_SCOPE Status Lifecycle

**SHALL** requirements for VERSION_SCOPE status:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-022-01 | ubiquitous | VERSION_SCOPE status SHALL be one of: PLANNING, READY FOR RELEASE, RELEASED, CANCELLED | Status clarity |
| R-REL-022-02 | conditional | IF status is PLANNING THEN release SHALL NOT proceed | Gate enforcement |
| R-REL-022-03 | conditional | IF release cancelled THEN VERSION_SCOPE SHALL include cancellation rationale | Decision audit |

**Status Transitions:**

```
PLANNING → READY FOR RELEASE → RELEASED
    ↓
CANCELLED (with rationale)
```

### CAP-REL-015: Rollback Plan for Major Releases

**SHOULD** requirements for rollback planning:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-023-01 | conditional | FOR major releases, VERSION_SCOPE SHOULD include Rollback Plan | Risk mitigation |
| R-REL-023-02 | conditional | IF Rollback Plan included THEN it SHALL specify triggers, procedure, and owner | Completeness |

### CAP-REL-016: Post-Release Retrospective

**SHOULD** requirements for retrospectives:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-024-01 | conditional | AFTER release completion, release manager SHOULD complete Retrospective section | Learning capture |
| R-REL-024-02 | conditional | IF retrospective completed THEN it SHOULD be within 7 days of release | Context freshness |

### CAP-REL-017: VERSION_SCOPE Template Compliance

**SHALL** requirements for template usage:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-025-01 | ubiquitous | VERSION_SCOPE documents SHALL use TEMPLATE_VERSION_SCOPE.md as starting point | Consistency |
| R-REL-025-02 | ubiquitous | VERSION_SCOPE structure SHALL match template sections | Standardization |

### CAP-REL-018: Historical VERSION_SCOPE Reconstruction

**MAY** requirements for historical documentation:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-026-01 | optional | FOR releases without VERSION_SCOPE, release manager MAY create reconstructed documents | Historical completeness |
| R-REL-026-02 | conditional | IF reconstructed THEN document SHALL include [RECONSTRUCTED] marker in header | Provenance clarity |

**V-Test for VERSION_SCOPE Existence:**

```bash
VERSION="X.Y.Z"
[ -f "planning/VERSION_SCOPE_v${VERSION}.md" ] && echo "PASS" || echo "FAIL"
```

### CAP-REL-019: Feature-Descriptive Content Review (R-REL-042) (L585)

**SHOULD** requirements for content alignment on major/minor releases:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-042-01 | conditional | BEFORE major/minor release, release manager SHOULD review Feature_Descriptive_Artifacts for content alignment | Semantic accuracy |
| R-REL-042-02 | conditional | IF new capabilities added THEN AGET_IDENTITY_SPEC scope.manages SHOULD be updated | Identity completeness |
| R-REL-042-03 | conditional | IF new differentiators exist THEN AGET_POSITIONING_SPEC differentiators SHOULD be updated | Positioning accuracy |
| R-REL-042-04 | conditional | IF release is stable THEN CHANGELOG "Latest Stable" SHOULD reflect current version | Version clarity |

**Feature-Descriptive Artifact Inventory:**

| Artifact | Section | Review For |
|----------|---------|------------|
| AGET_IDENTITY_SPEC.yaml | `scope.manages` | New capabilities |
| AGET_POSITIONING_SPEC.yaml | `differentiators` | New differentiators |
| AGET_POSITIONING_SPEC.yaml | `value_proposition` | New value propositions |
| CHANGELOG.md | Version Support | Current stable version |

**Distinction from Version-Indicator Artifacts (L584):**

| Class | Definition | Check Type | Trigger |
|-------|------------|------------|---------|
| **Version-indicator** (L584) | Embedded version numbers/dates | Automated | Every release |
| **Feature-descriptive** (L585) | Content describing capabilities | Manual review | Major/minor releases |

**V-Test for Feature-Descriptive Review:**

```bash
# Check identity spec has recent changelog entry
grep -q "$(date +%Y)" specs/AGET_IDENTITY_SPEC.yaml && echo "PASS: Identity spec reviewed this year" || echo "WARN: Identity spec may need review"
```

**Prevents**: Feature_Drift anti-pattern (version updated, content stale).

### CAP-REL-020: Release Handoff Requirements (R-REL-019) (L511, L587)

**SHALL/SHOULD** requirements for release handoff artifacts targeting external audiences:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-019-01 | ubiquitous | AFTER release completion, release manager SHALL create `handoffs/RELEASE_HANDOFF_vX.Y.Z.md` | Release-to-fleet propagation |
| R-REL-019-02 | ubiquitous | Handoff SHALL include "Context for External Fleets" section | External audience accessibility |
| R-REL-019-03 | conditional | IF new tools introduced THEN handoff SHALL explain what/when/how | Tool usability |
| R-REL-019-04 | conditional | IF L-docs referenced THEN handoff SHALL explain the lesson (not just label) | Knowledge transfer |
| R-REL-019-05 | conditional | IF archetype features added THEN handoff SHALL map features to archetypes | Applicability clarity |
| R-REL-019-06 | ubiquitous | Handoff SHALL explain WHY and WHICH, not just WHAT | Curse of knowledge mitigation |

**Vocabulary:**

```yaml
External_Fleet:
  skos:definition: "Fleet outside the managing organization with no direct access to internal artifacts"
  skos:scopeNote: "Cannot read private L-docs, unfamiliar with internal tools"
  skos:related: ["Release_Handoff", "L587"]
```

**Handoff Structure (per L587):**

| Section | Purpose | Required |
|---------|---------|----------|
| Executive Summary | Theme + key changes | YES |
| What Changed | Added/changed/breaking | YES |
| Context for External Fleets | WHY and WHICH explanations | YES (R-REL-019-02) |
| Critical Mitigations | L-doc explanations with problem/rule/commands | IF L-docs referenced |
| New Tools | what/when/how/if-fails | IF new tools |
| Archetype Reference | Feature → archetype mapping | IF archetype features |
| Pilot Tracking Template | Status table | YES |

**V-Test for Handoff Existence:**

```bash
VERSION="X.Y.Z"
[ -f "handoffs/RELEASE_HANDOFF_v${VERSION}.md" ] && echo "PASS" || echo "FAIL"
```

**V-Test for External Context:**

```bash
VERSION="X.Y.Z"
grep -q "Context for External" "handoffs/RELEASE_HANDOFF_v${VERSION}.md" && echo "PASS" || echo "FAIL"
```

**Prevents**: Curse_of_Knowledge anti-pattern (L587) - internal knowledge assumed in external docs.

**See**: `templates/TEMPLATE_RELEASE_HANDOFF.md` for reference structure.

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
| R-REL-019-* | V-test scripts (handoff existence, context check) | Implemented |

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
- L444: Version Inventory Coherence Requirement
- L521: Version-Bearing File Specification-to-Tool Gap
- SOP_release_process.md
- AGET_VERSIONING_CONVENTIONS.md
- Keep a Changelog (https://keepachangelog.com)
- Semantic Versioning (https://semver.org)

---

## Changelog

### v1.6.0 (2026-02-15)

- Added CAP-REL-020: Release Handoff Requirements (R-REL-019-01 through R-REL-019-06)
- Added vocabulary: External_Fleet
- R-REL-019-02: Handoff SHALL include "Context for External Fleets" section
- R-REL-019-03: New tools explanation requirement
- R-REL-019-04: L-doc explanation requirement (not just labels)
- R-REL-019-05: Archetype feature mapping requirement
- R-REL-019-06: WHY and WHICH, not just WHAT
- Addresses "curse of knowledge" gap (L587)
- See: L511, L587, PROJECT_PLAN_release_handoff_spec_enhancement_v1.0

### v1.5.0 (2026-02-15)

- Added CAP-REL-019: Feature-Descriptive Content Review (R-REL-042)
- Added vocabulary: Feature_Descriptive_Artifact, Version_Indicator_Artifact, Feature_Drift
- Distinguishes version-indicator (L584) from feature-descriptive (L585) artifact classes
- See: L585, PROJECT_PLAN_feature_descriptive_artifact_alignment_v1.0

### v1.4.0 (2026-01-17)

- Added CAP-REL-012: VERSION_SCOPE Requirement (R-REL-020)
- Added CAP-REL-013: VERSION_SCOPE Content Requirements
- Added CAP-REL-014: VERSION_SCOPE Status Lifecycle
- Added CAP-REL-015: Rollback Plan for Major Releases
- Added CAP-REL-016: Post-Release Retrospective
- Added CAP-REL-017: VERSION_SCOPE Template Compliance
- Added CAP-REL-018: Historical VERSION_SCOPE Reconstruction
- Added vocabulary terms: Version_Scope, MVP_Scope, Release_Phase, Release_Retrospective, Rollback_Plan
- See: PROJECT_PLAN_version_scope_standardization_v1.0

### v1.2.0 (2026-01-12)

- Added R-REL-VER-001: Version-Bearing File Coherence requirements (L521)
- Added Version-Bearing File Enumeration table
- Added R-REL-VER-001-01 through R-REL-VER-001-05 requirements
- Added references to L444, L521
- See: PROJECT_PLAN_version_bearing_file_remediation_v1.0

### v1.1.0 (2026-01-11)

- Version bump for consistency

### v1.0.0 (2026-01-04)

- Initial specification
- Formalized R-REL-006 (Manager Migration)
- Multi-repo coordination requirements
- CHANGELOG and GitHub Release requirements
- Organization homepage update requirements

---

*AGET_RELEASE_SPEC.md — Release standards for AGET framework*
*"A checkbox is not a verification. A passing test is."* — L440
