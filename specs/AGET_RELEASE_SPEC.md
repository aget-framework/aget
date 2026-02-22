# AGET Release Specification

**Version**: 1.8.0
**Status**: Active
**Category**: Process (Release Management)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-02-20
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

  observability:
    Validation_Log:
      skos:definition: "Persistent structured record of validation script executions"
      aget:location: ".aget/logs/validation_log.jsonl"
      aget:format: "JSON Lines (one JSON object per line)"
      skos:related: ["CAP-REL-021", "L605"]

    Gate_Record:
      skos:definition: "Immutable record of gate execution with pass/fail status"
      aget:location: ".aget/logs/gate_log.jsonl"
      aget:format: "JSON Lines"
      skos:related: ["CAP-REL-022", "Release_Gate", "L605"]

    Release_Snapshot:
      skos:definition: "Structured capture of all repo states before and after release execution"
      aget:location: ".aget/logs/release_snapshots/"
      skos:related: ["CAP-REL-023", "L605"]

    Propagation_Audit_Record:
      skos:definition: "Record of expected vs actual propagation state for template-targeting changes"
      aget:location: ".aget/logs/propagation_log.jsonl"
      skos:related: ["CAP-REL-024", "L596", "L605"]

    Health_Log:
      skos:definition: "Persistent record of healthcheck results enabling trend analysis"
      aget:location: ".aget/logs/health_log.jsonl"
      skos:related: ["CAP-REL-025", "L605"]

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

    Ephemeral_Validation:
      skos:definition: "Running validation scripts whose results vanish after execution — no audit trail, no trend analysis, no regression detection"
      aget:anti_pattern: true
      skos:related: ["L605", "CAP-REL-021"]

    Manual_Gate_Enforcement:
      skos:definition: "Relying on human discipline (checkboxes, SOP text) to enforce gate sequencing instead of machine-verified blocking"
      aget:anti_pattern: true
      skos:related: ["L605", "CAP-REL-022"]

    Workspace_Local_Validation:
      skos:definition: "Validating changes against authoring workspace instead of deployment targets (template repos)"
      aget:anti_pattern: true
      skos:related: ["L596", "L605", "CAP-REL-024"]

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

### CAP-REL-021: Persistent Validation Logging (L605, ER-VALIDATE-LOG)

**SHALL** requirements for validation result persistence:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-021-01 | ubiquitous | Every validation script SHALL append a structured JSON record to `.aget/logs/validation_log.jsonl` | Audit trail — results must survive session end |
| CAP-REL-021-02 | ubiquitous | Each Validation_Log record SHALL include: timestamp, script_name, aget_version, checks_passed (count), checks_failed (count), exit_code, and check_details (array) | Queryable structured data |
| CAP-REL-021-03 | ubiquitous | The `.aget/logs/` directory SHALL be created automatically if absent when any logging script runs | No manual setup required |
| CAP-REL-021-04 | conditional | IF a validation script exits non-zero THEN the Validation_Log record SHALL include failure_details with specific check names and error messages | Actionable failure diagnosis |
| CAP-REL-021-05 | prohibitive | Validation scripts SHALL NOT produce only ephemeral output (stdout/stderr without persistent log) | Prevents Ephemeral_Validation anti-pattern |

**Validation_Log Record Schema:**

```json
{
  "timestamp": "2026-02-20T19:50:00Z",
  "script": "post_release_validation.py",
  "aget_version": "3.6.0",
  "checks_passed": 11,
  "checks_failed": 1,
  "exit_code": 1,
  "check_details": [
    {"name": "version_coherence", "status": "pass"},
    {"name": "github_releases", "status": "fail", "error": "template-worker-aget missing GitHub Release"}
  ]
}
```

**V-Test for Validation Logging:**

```bash
# After running any validation script, log should have new entry
BEFORE=$(wc -l < .aget/logs/validation_log.jsonl 2>/dev/null || echo 0)
python3 .aget/patterns/session/aget_housekeeping_protocol.py --json
AFTER=$(wc -l < .aget/logs/validation_log.jsonl 2>/dev/null || echo 0)
[ "$AFTER" -gt "$BEFORE" ] && echo "PASS: Validation logged" || echo "FAIL: No log entry created"
```

**Prevents**: Ephemeral_Validation anti-pattern (L605) — validation results that vanish after execution.

**Implementing Script**: `scripts/validation_logger.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-022: Gate Execution Enforcement (L605, ER-GATE-ENFORCE)

**SHALL** requirements for gate sequencing enforcement:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-022-01 | ubiquitous | Gate completion SHALL produce an immutable Gate_Record in `.aget/logs/gate_log.jsonl` | Machine-verifiable gate history |
| CAP-REL-022-02 | ubiquitous | Each Gate_Record SHALL include: gate_id, timestamp, aget_version, status (pass/fail), validation_summary, and operator | Audit completeness |
| CAP-REL-022-03 | conditional | BEFORE executing gate N, the system SHALL verify gate N-1 has a PASS record in gate_log.jsonl | Sequential gate enforcement |
| CAP-REL-022-04 | conditional | IF prior gate record is missing or status is FAIL THEN the system SHALL BLOCK progression and display the blocking reason | Prevents gate skipping |
| CAP-REL-022-05 | conditional | IF gate is the first in sequence (Gate 0) THEN prior gate check SHALL be skipped | Bootstrap: first gate has no predecessor |
| CAP-REL-022-06 | prohibitive | Gate completion SHALL NOT be recorded by manual checkbox alone — a gate script SHALL produce the record | Prevents Manual_Gate_Enforcement anti-pattern |

**Gate_Record Schema:**

```json
{
  "gate_id": "G7.1",
  "timestamp": "2026-02-20T19:50:00Z",
  "aget_version": "3.6.0",
  "status": "pass",
  "checks_total": 3,
  "checks_passed": 3,
  "checks_failed": 0,
  "validation_summary": "V7.1.1 PASS, V7.1.2 PASS, V7.1.3 PASS",
  "operator": "private-aget-framework-AGET",
  "prior_gate": "G7.0"
}
```

**V-Test for Gate Enforcement:**

```bash
# Attempt gate N+1 without gate N record — should be blocked
python3 .aget/patterns/release/run_gate.py --gate G7.1 --version 3.6.0 2>&1
# Expected: "BLOCKED: Gate G7.0 has no PASS record. Complete G7.0 before proceeding to G7.1."
```

**Prevents**: Manual_Gate_Enforcement anti-pattern (L605) — relying on human checkpoint discipline instead of machine verification.

**Implementing Script**: `scripts/run_gate.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-023: Release State Snapshots (L605, ER-RELEASE-SNAPSHOT)

**SHALL/SHOULD** requirements for pre/post release state capture:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-023-01 | conditional | BEFORE release execution begins (Gate 0), the system SHALL capture a pre-release Release_Snapshot | Baseline for diff validation |
| CAP-REL-023-02 | conditional | AFTER release completion (final gate), the system SHALL capture a post-release Release_Snapshot | Outcome measurement |
| CAP-REL-023-03 | ubiquitous | Each Release_Snapshot SHALL include: version files (all repos), GitHub Release existence, CHANGELOG latest entry, homepage version state | Comprehensive state capture |
| CAP-REL-023-04 | ubiquitous | The diff between pre and post snapshots SHALL be logged to `.aget/logs/release_snapshots/v{VERSION}_diff.json` | Diff-based validation |
| CAP-REL-023-05 | conditional | IF diff shows unexpected unchanged items (version file not bumped, GitHub Release not created) THEN the system SHALL flag them as release gaps | Regression detection |

**Release_Snapshot Schema:**

```json
{
  "timestamp": "2026-02-20T19:50:00Z",
  "aget_version": "3.6.0",
  "phase": "pre-release",
  "repos": {
    "aget": {"version_json": "3.5.0", "changelog_latest": "3.5.0", "github_release": "v3.5.0"},
    "template-worker-aget": {"version_json": "3.5.0", "changelog_latest": "3.5.0", "github_release": "v3.5.0"}
  },
  "homepage": {"badge_version": "3.5.0", "roadmap_current": "3.5.0"}
}
```

**V-Test for State Snapshots:**

```bash
VERSION="3.6.0"
[ -f ".aget/logs/release_snapshots/v${VERSION}_pre.json" ] && echo "PASS: Pre-release snapshot exists" || echo "FAIL"
[ -f ".aget/logs/release_snapshots/v${VERSION}_post.json" ] && echo "PASS: Post-release snapshot exists" || echo "FAIL"
[ -f ".aget/logs/release_snapshots/v${VERSION}_diff.json" ] && echo "PASS: Release diff exists" || echo "FAIL"
```

**Prevents**: Post-release discovery of version drift and stale homepage (L605 categories 1 and 3).

**Implementing Script**: `scripts/release_snapshot.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-024: Propagation Audit (L605, L596, ER-PROPAGATION-AUDIT)

**SHALL** requirements for template propagation tracking:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-024-01 | conditional | WHEN changes target template repos, the system SHALL log a Propagation_Audit_Record with expected targets and expected changes | Propagation planning |
| CAP-REL-024-02 | ubiquitous | Each Propagation_Audit_Record SHALL include: source_repo, target_repos (array), expected_changes, actual_changes, propagation_complete (boolean) | Verifiable propagation state |
| CAP-REL-024-03 | conditional | IF propagation_complete is false for any target THEN the associated PROJECT_PLAN or release gate SHALL NOT be marked complete | Prevents workspace-local-only validation |
| CAP-REL-024-04 | ubiquitous | Propagation audit SHALL verify against deployment targets (template-*-aget repos), not the authoring workspace (private-aget-framework-AGET) | L596: measure where users clone from |

**Propagation_Audit_Record Schema:**

```json
{
  "timestamp": "2026-02-20T19:50:00Z",
  "aget_version": "3.6.0",
  "source_repo": "private-aget-framework-AGET",
  "targets": [
    {"repo": "template-worker-aget", "expected": ["version.json", "CHANGELOG.md"], "actual": ["version.json", "CHANGELOG.md"], "complete": true},
    {"repo": "template-advisor-aget", "expected": ["version.json", "CHANGELOG.md"], "actual": ["version.json"], "complete": false, "missing": ["CHANGELOG.md"]}
  ],
  "all_complete": false
}
```

**V-Test for Propagation Audit:**

```bash
# Check propagation log shows all targets complete
python3 -c "
import json
with open('.aget/logs/propagation_log.jsonl') as f:
    records = [json.loads(l) for l in f if l.strip()]
latest = records[-1]
print('PASS' if latest['all_complete'] else 'FAIL: Incomplete propagation — ' + str([t['repo'] for t in latest['targets'] if not t['complete']]))
"
```

**Prevents**: Workspace_Local_Validation anti-pattern (L596, L605 category 5) — releasing from authoring workspace without verifying deployment targets received changes.

**Implementing Script**: `scripts/propagation_audit.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-025: Healthcheck Result Persistence (L605, ER-HEALTH-PERSIST)

**SHOULD** requirements for healthcheck trend tracking:

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-025-01 | ubiquitous | Healthcheck skill executions SHOULD append results to `.aget/logs/health_log.jsonl` | Trend analysis across sessions |
| CAP-REL-025-02 | ubiquitous | Each Health_Log record SHOULD include: timestamp, check_name, status (OK/WARN/CRITICAL), details, and session_id | Session-correlated health data |
| CAP-REL-025-03 | conditional | IF session wake-up includes health display THEN it SHOULD show trend vs. prior session (improved/stable/degraded) | Health trajectory visibility |
| CAP-REL-025-04 | conditional | IF health status transitions from OK to WARN or CRITICAL THEN the system SHOULD flag the regression in wake-up | Regression detection |

**Health_Log Record Schema:**

```json
{
  "timestamp": "2026-02-20T19:50:00Z",
  "session_id": "session_2026-02-20_1950",
  "checks": [
    {"name": "evolution_health", "status": "OK", "details": "185 L-docs, naming valid"},
    {"name": "kb_health", "status": "WARN", "details": "ontology/ stale (>90 days)"}
  ],
  "summary": {"ok": 3, "warn": 1, "critical": 0}
}
```

**V-Test for Health Persistence:**

```bash
# After healthcheck, log should have new entry
[ -f ".aget/logs/health_log.jsonl" ] && echo "PASS: Health log exists" || echo "FAIL: No health log"
```

**Prevents**: Loss of health trajectory data — healthchecks currently produce ephemeral output with no cross-session comparison capability.

**Implementing Script**: `scripts/health_logger.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-026: Release Command Hazards (L589, L570, L594, ER-HAZARD)

Release handoffs and migration scripts SHALL document platform-specific command hazards.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| CAP-REL-026-01 | ubiquitous | Release handoffs using perl substitution SHALL escape `@` characters in replacement strings | L589: `@aget` interpolates as empty array in perl double-quoted strings |
| CAP-REL-026-02 | ubiquitous | Release handoffs using sed on macOS SHALL use `sed -i ''` (empty extension) or prefer perl/Edit tool over in-place sed | L570: BSD sed `-i` without extension argument zeroes the file |
| CAP-REL-026-03 | ubiquitous | Release handoff templates SHALL include a "Platform Hazards" section listing known command pitfalls | Prevents rediscovery of known hazards by downstream operators |
| CAP-REL-026-04 | conditional | IF a release handoff includes shell commands for downstream execution THEN those commands SHALL be tested on the target platform before inclusion | L594: commands tested on Linux may fail on macOS and vice versa |

**Known Hazards Registry:**

| Hazard | Platform | Command | Symptom | Mitigation | L-doc |
|--------|----------|---------|---------|------------|-------|
| Perl sigil interpolation | All | `perl -pi -e 's/old/@new/'` | `@new` expands to empty array | Use `\@new` or single quotes around pattern | L589 |
| BSD sed file zeroing | macOS | `sed -i 's/old/new/' file` | File becomes 0 bytes | Use `sed -i '' 's/old/new/' file` | L570 |
| GNU/BSD sed flag incompatibility | Cross-platform | `sed -i` | Different `-i` semantics | Prefer perl or Edit tool for portability | L570 |

**V-Test for Hazard Documentation:**

```bash
# V-REL-026: Handoff template includes Platform Hazards section
grep -q "Platform Hazards\|Command Hazards" templates/RELEASE_HANDOFF_TEMPLATE.md && echo "PASS" || echo "FAIL: Missing hazard section"
```

**Prevents**: Rediscovery_Of_Known_Hazards anti-pattern — operators encountering documented hazards because the documentation wasn't included in release handoffs.

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
| CAP-REL-021-* | validation_logger.py (wraps existing scripts) | **v3.6.0** |
| CAP-REL-022-* | run_gate.py (gate execution + enforcement) | **v3.6.0** |
| CAP-REL-023-* | release_snapshot.py (pre/post state capture) | **v3.6.0** |
| CAP-REL-024-* | propagation_audit.py (target verification) | **v3.6.0** |
| CAP-REL-025-* | health_logger.py (wraps healthcheck skills) | **v3.6.0** |

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

### Anti-Pattern 4: Ephemeral Validation (L605)

```
❌ ANTI-PATTERN: Validation results vanish after execution

$ python3 post_release_validation.py
PASS: version coherence
FAIL: template-worker-aget GitHub Release missing
Exit code: 1

# Session ends. Results gone. Next session: "Did we run validation? What failed?"
# No audit trail. No trend analysis. No regression detection.
```

```
✅ CORRECT: Validation appends to persistent log (CAP-REL-021)

$ python3 post_release_validation.py
# Stdout output as before, PLUS:
# → Appended to .aget/logs/validation_log.jsonl
# → Queryable: "Show all failures for v3.6.0"
# → Comparable: "What failed this release vs. last?"
```

### Anti-Pattern 5: Manual Gate Enforcement (L605)

```
❌ ANTI-PATTERN: Human discipline as gate mechanism

Gate 1: [x] Version updates complete  ← Manual checkbox
Gate 2: [x] Documentation complete    ← Manual checkbox
Gate 3: Proceed to release            ← Nothing verifies Gate 1 & 2 actually passed

# SOP says "complete Gate 2 before Gate 3"
# But nothing prevents jumping to Gate 3 if Gate 2 was skipped
```

```
✅ CORRECT: Machine-enforced gate sequencing (CAP-REL-022)

$ python3 run_gate.py --gate G7.2 --version 3.6.0
BLOCKED: Gate G7.1 has no PASS record in gate_log.jsonl.
Complete G7.1 before proceeding to G7.2.

# Gate script reads gate_log.jsonl and refuses to proceed
# No manual discipline required — machine enforces sequence
```

### Anti-Pattern 6: Workspace-Local Validation (L596, L605)

```
❌ ANTI-PATTERN: Validate authoring workspace, not deployment targets

$ python3 validate_version_consistency.py  ← Runs in private-aget-framework-AGET
PASS: All version files match v3.6.0

# But template-worker-aget (what users clone) still at v3.5.0!
# Validation passed in workspace; deployment target untouched.
```

```
✅ CORRECT: Verify deployment targets received changes (CAP-REL-024)

$ python3 propagation_audit.py --version 3.6.0
template-worker-aget: version.json ✓, CHANGELOG.md ✗ (MISSING)
template-advisor-aget: version.json ✓, CHANGELOG.md ✓
INCOMPLETE: 1 target has missing propagation
```

---

## References

- L358: Release Artifact Gaps
- L429: Version Inventory Requirement
- L440: Manager Migration Verification Gap
- L444: Version Inventory Coherence Requirement
- L521: Version-Bearing File Specification-to-Tool Gap
- L596: Workspace-Local Remediation Propagation Gap
- L605: Release Observability and Enforcement Gap
- L604: Systemic Top-Down-Only Framework Pattern
- SOP_release_process.md
- AGET_VERSIONING_CONVENTIONS.md
- Keep a Changelog (https://keepachangelog.com)
- Semantic Versioning (https://semver.org)

---

## Changelog

### v1.8.0 (2026-02-20)

- Added CAP-REL-026: Release Command Hazards (ER-HAZARD, L589, L570, L594)
- Added Known Hazards Registry (perl sigil, BSD sed, cross-platform sed)
- See: L589, L570, L594, VERSION_SCOPE_v3.6.0.md

### v1.7.0 (2026-02-20)

- Added CAP-REL-021: Persistent Validation Logging (ER-VALIDATE-LOG, L605)
- Added CAP-REL-022: Gate Execution Enforcement (ER-GATE-ENFORCE, L605)
- Added CAP-REL-023: Release State Snapshots (ER-RELEASE-SNAPSHOT, L605)
- Added CAP-REL-024: Propagation Audit (ER-PROPAGATION-AUDIT, L605, L596)
- Added CAP-REL-025: Healthcheck Result Persistence (ER-HEALTH-PERSIST, L605)
- Added vocabulary: Validation_Log, Gate_Record, Release_Snapshot, Propagation_Audit_Record, Health_Log
- Added anti-patterns: Ephemeral_Validation, Manual_Gate_Enforcement, Workspace_Local_Validation
- 5 new CAP groups (24 EARS requirements) for release observability and enforcement
- Enforcement table updated with 5 v3.6.0-targeted validators
- Design principle: "The user is not the enforcement mechanism" (L605)
- See: L605, L604, L596, VERSION_SCOPE_v3.6.0.md

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
