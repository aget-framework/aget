# AGET Release Specification

**Version**: 1.17.0
**Status**: Active
**Category**: Process (Release Management)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-05-02
**Author**: aget-framework
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

    Loading_Dock:
      skos:definition: "Starting next-release planning before verifying current-release deployment — finished goods sit undelivered while next batch starts production"
      aget:anti_pattern: true
      skos:related: ["L656", "CAP-REL-027"]

  deployment:
    Deployment_Status_Record:
      skos:definition: "Machine-readable record tracking release deployment lifecycle from RELEASED through DEPLOYED"
      aget:location: ".aget/logs/deployment_status.jsonl"
      aget:format: "JSON Lines"
      skos:related: ["CAP-REL-027", "L656"]

    Release_Discovery:
      skos:definition: "Process by which a downstream agent discovers new upstream releases without manual notification"
      skos:related: ["CAP-REL-027", "L656", "L604"]

    Deployment_Delta:
      skos:definition: "Version gap between released version and deployed version on a target"
      skos:related: ["CAP-REL-027", "L656"]

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
1. framework-manager (manager) → version bump first
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
framework-manager/release-notes/v{VERSION}.md
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
| R-REL-022-01 | ubiquitous | VERSION_SCOPE status SHALL be one of: PLANNING, SCOPE_LOCKED, READY FOR RELEASE, RELEASED, CANCELLED | Status clarity (SCOPE_LOCKED added v1.16.0 per #1179 + L708 vocabulary) |
| R-REL-022-02 | conditional | IF status is PLANNING THEN release SHALL NOT proceed | Gate enforcement |
| R-REL-022-03 | conditional | IF release cancelled THEN VERSION_SCOPE SHALL include cancellation rationale | Decision audit |

**Status Transitions:**

```
PLANNING → SCOPE_LOCKED → READY FOR RELEASE → RELEASED
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
| R-REL-024-03 | conditional | FOR fleet upgrade close-outs (FLEET-UPG-NNN), the fleet supervisor SHALL author a rubric-scored Release_Outcome_Report using `aget/rubrics/RUBRIC_fleet_upgrade_outcome_v1.1.md` before setting `Plan_Status: COMPLETE`. The report SHALL record per-dimension scores (D1–D5) and reasoning (2–3 sentences each). A score of ≥10 (Compliant band) is required; scores below 10 SHALL be explicitly documented as gaps requiring remediation in the next cycle. | Closes the vibe-not-measurement gap (FLEET-UPG-013 retrospective finding, #1149); two-supervisor convergence (FLEET-UPG-013 = 13/15, FLEET-UPG-014 = 10/15) validates rubric applicability |

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
| R-REL-019-07 | ubiquitous | AFTER release completion, release manager SHALL publish a sanitized handoff to the public framework repository at `aget/handoffs/RELEASE_HANDOFF_vX.Y.Z.md` | External fleet discoverability (L612) |

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

**Sanitization Requirements (R-REL-019-07):**

The public handoff MUST NOT contain:
- Private agent names (`private-*-aget`, `private-*-AGET`)
- Private repository paths (`~/github/private-*`, `gmelli/*`)
- Fleet size disclosures (e.g., "32 agents")
- Internal tracking tables (pilot commit hashes, internal dates)

**V-Test for Handoff Existence:**

```bash
VERSION="X.Y.Z"
[ -f "handoffs/RELEASE_HANDOFF_v${VERSION}.md" ] && echo "PASS" || echo "FAIL"
```

**V-Test for Public Handoff Existence (R-REL-019-07):**

```bash
VERSION="X.Y.Z"
[ -f "aget/handoffs/RELEASE_HANDOFF_v${VERSION}.md" ] && echo "PASS" || echo "FAIL"
```

**V-Test for Sanitization (R-REL-019-07):**

```bash
VERSION="X.Y.Z"
grep -c "private-" "aget/handoffs/RELEASE_HANDOFF_v${VERSION}.md" | grep -q "^0$" && echo "PASS" || echo "FAIL: contains private references"
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
python3 .aget/patterns/session/health_check.py --json
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
  "operator": "framework-manager",
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
| CAP-REL-024-04 | ubiquitous | Propagation audit SHALL verify against deployment targets (template-*-aget repos), not the authoring workspace (framework-manager) | L596: measure where users clone from |

**Propagation_Audit_Record Schema:**

```json
{
  "timestamp": "2026-02-20T19:50:00Z",
  "aget_version": "3.6.0",
  "source_repo": "framework-manager",
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

### CAP-REL-027: Post-Release Deployment Monitoring (L656, L604, ER-DEPLOY-MONITOR)

After release completion, the releasing agent SHALL monitor deployment status to prevent the Loading_Dock anti-pattern — starting next-release planning before verifying current-release deployment.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-027-01 | event-driven | WHEN a release is completed, the releasing agent SHALL record a Deployment_Status_Record in `.aget/logs/deployment_status.jsonl` with status=RELEASED and confirmed_deployments=0 | Deployment tracking starts at release, not at deployment |
| R-REL-027-02 | event-driven | WHEN wake-up runs on an agent with `release_discovery` configured, the extension SHALL query the latest GitHub release from the configured repo | Pull-based discovery eliminates manual notification dependency (L604) |
| R-REL-027-03 | conditional | IF the discovered version is newer than the agent's current version THEN the extension SHALL display an upgrade advisory referencing the DEPLOYMENT_SPEC | Advisory encourages spec verification, not automatic upgrade |
| R-REL-027-04 | conditional | WHEN the releasing agent's wake-up runs AND the latest deployment record shows 0 confirmed deployments AND release is >= 48h old THEN the extension SHALL display a DEPLOYMENT UNVERIFIED warning | Time-based escalation surfaces stalled deployments |
| R-REL-027-05 | prohibitive | The releasing agent SHALL NOT create a VERSION_SCOPE for the next release WHEN the latest deployment record shows 0 confirmed deployments | Structural gate prevents Loading_Dock anti-pattern |

**Design Principles:**

- **Deployable signal, not just existence**: R-REL-027-03 references DEPLOYMENT_SPEC, not RELEASE_HANDOFF. Remote supervisors access DEPLOYMENT_SPEC via `gh` from the public repo.
- **Three-tier degradation** (ADR-004): Deployment monitoring uses filesystem for local checks (tier_basic), `gh` CLI for remote checks (tier_rich). Release discovery is non-blocking — `gh` failure = graceful degradation.
- **Non-blocking wake-up** (C-WU-002): All deployment checks in wake_up_ext.py must not block session initialization.

**V-Test for Deployment Monitoring:**

```bash
# V-REL-027: Deployment status record exists after release
[ -f ".aget/logs/deployment_status.jsonl" ] && echo "PASS: Deployment log exists" || echo "FAIL: No deployment log"

# V-REL-027: VERSION_SCOPE blocked when unverified
python3 scripts/deployment_monitor.py --check --version X.Y.Z --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('PASS' if d.get('confirmed_deployments',0)==0 and d.get('blocked',False) else 'FAIL')"
```

**Prevents**: Loading_Dock anti-pattern — governance rewards artifact creation (IMPLEMENTED) but has no mechanism to verify deployment. Releasing agent starts next-cycle planning before current-cycle deployment is confirmed. (L656)

**Implementing Script**: `scripts/deployment_monitor.py` (SCRIPT_REGISTRY.yaml)

### CAP-REL-028: Upstream Deployment Feedback (REQ-REL-F-009, L825, L826)

After completing a fleet upgrade, fleet supervisors SHOULD file an upstream enhancement issue capturing deployment retrospective findings — ensuring that friction events, tool effectiveness, and improvement recommendations flow back to the framework agent for next-release planning.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-028-01 | event-driven | WHEN a fleet supervisor completes a fleet upgrade using the MIGRATION_COMPLETION_REPORT, the supervisor SHOULD file an enhancement issue to `gmelli/aget-aget` containing friction events, tool effectiveness, and improvement recommendations | Deployment learnings embedded in local plans are invisible to the framework agent (L825, FLEET-UPG-011 evidence) |
| R-REL-028-02 | ubiquitous | The MIGRATION_COMPLETION_REPORT template SHALL include an "Upstream Enhancement Issue" section with guidance on what to include in the feedback issue | Template-driven prompting ensures consistent feedback content |
| R-REL-028-03 | conditional | IF the framework agent receives an upstream feedback issue THEN the framework agent SHOULD reference it in the next VERSION_SCOPE grooming | Closes the feedback loop — deployment learnings inform next release planning |

**Design Principles:**

- **SHOULD, not SHALL**: Supervisor feedback is advisory, not blocking. Fleet supervisors own their upgrade cadence (CAP-REL-027 covers the framework agent's deployment monitoring obligation; this covers the reverse flow).
- **Issue as handoff artifact**: The GitHub issue is the cross-agent boundary object — discoverable via `study_topic.py`, searchable, and naturally incorporated into VERSION_SCOPE grooming.
- **Private-first routing** (L638): Feedback issues go to `gmelli/aget-aget` like all other issues.

**V-Test for Template Section:**

```bash
grep -c "Upstream Enhancement Issue" templates/MIGRATION_COMPLETION_REPORT.template.md | grep -qv "^0$" && echo "PASS" || echo "FAIL"
```

**V-Test for Feedback Loop:**

```bash
# After fleet upgrade, check if supervisor filed feedback
gh issue list --repo gmelli/aget-aget --search "Fleet upgrade retro: vX.Y.Z" --json number --jq length
# Expected: >= 1 for recent releases
```

**Prevents**: Deployment Feedback Gap — the release lifecycle ends at "deployment verified" (CAP-REL-027) with no structured path for deployment learnings to return upstream. Supervisor retros with actionable findings (friction taxonomy, tool recommendations, convergent invention) stay buried in local plans. (L825, L826)

---

### CAP-REL-029: Release Readiness Gate (R-REL-025) — Pre-Release Conformance Contract

**Status**: LANDED (v0.2-equivalent for spec, 2026-04-25) — full EARS rigor; closes REQ-REL-F-001 (Pre-Release Validation procedure existed in SOP since v1.38, no R-REL-* contract). v3.15 P1 #4a Wave-1A first contract (1 of 5).

**Threat-Class Anchor**: SOP Phase -1 Pre-Flight Conformance Audit (added v1.38 / refined v1.40) is the procedural pattern; without an R-REL-* level contract, the audit's PASS criteria are convention-based not spec-bound. L671 instance — procedure exists, contract missing.

#### Requirement Set (EARS Ubiquitous + Conditional + State-Driven composite)

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-029-01 | ubiquitous | The release manager SHALL execute the Pre-Release Conformance Gate before any version-bump activity | SOP Phase -1 (v1.38+) procedure must be spec-bound, not convention-bound (L671 closure) |
| R-REL-029-02 | ubiquitous | The Pre-Release Conformance Gate SHALL invoke `aget/verification/validate_archetype_skills.py` (CAP-TPL-016-04 universal-skill conformance) | First concrete validator consumer landed in v3.15 P1 #10 (commit `dff5e47`) |
| R-REL-029-03 | conditional | IF the validator reports drift between AGET_TEMPLATE_SPEC mandate and worker-baseline OR fewer than N-1 templates conformant (where N is total `-aget` template count, allowing 1 known-outlier per current document-processor exclusion), THEN the release SHALL HALT until either (a) the spec is updated, OR (b) templates are remediated | Release-blocker semantics formalized; aligns with SOP v1.40 Pre-Flight FAIL semantics |
| R-REL-029-04 | ubiquitous | The Pre-Release Conformance Gate SHALL verify `aget/README.md` archetype count + universal-skill count match `AGET_TEMPLATE_SPEC.md` mandate | Catches documentation drift before release ships rhetoric (#1116 evidence; staleness since v3.13.0 was caught only by external review) |
| R-REL-029-05 | ubiquitous | The Pre-Release Conformance Gate SHALL verify VERSION_SCOPE_v{VERSION}.md status ∈ {SCOPE_LOCKED, READY FOR RELEASE} | R-REL-020 dependency; release without locked scope is structurally premature (L850); enum aligned with R-REL-022-01 (v1.16.0 #1179 fix) |
| R-REL-029-06 | conditional | IF an active PROJECT_PLAN_v{VERSION}_release_v{N}.md exists AND that plan declares Gate 1 (or equivalent build-phase gate) IN PROGRESS THEN the Pre-Release Conformance Gate SHALL surface "Gate 1 not complete; release-build phase artifacts incomplete" as advisory | L894 plan-driven discipline; warns against premature release execution while build phase still has open Work Streams |
| R-REL-029-07 | conditional | IF release is `breaking` per current `BREAKING_CHANGES_v{VERSION}.md` AND no ADR has ratified the breaking-change policy for this cycle THEN the Pre-Release Conformance Gate SHALL HALT until ADR ratified | ADR-022 precedent (v3.15); breaking change without ADR = ungoverned scope |
| R-REL-029-08 | ubiquitous | The Pre-Release Conformance Gate SHALL emit a structured PASS/FAIL summary to `sessions/release_readiness_audit_{DATE}.md` with per-check status + remediation links for any FAIL | Audit trail for release retrospective; consumed by Phase 7.1.5 PIR scoring (R-REL-024) |

#### Definitions

| Term | Definition |
|------|------------|
| Pre-Release Conformance Gate | The structural verification gate at SOP Phase -1, before any version-bump activity, contracted by this CAP |
| N-1 conformance allowance | Acceptance threshold permitting 1 known-outlier template per cycle (current: template-document-processor-AGET pending #1121 lifecycle decision); may tighten to N/N in future versions |
| Active PROJECT_PLAN | A `planning/PROJECT_PLAN_v{VERSION}_release_v{N}.md` with status not equal to COMPLETE |
| Breaking release | A release containing at least one breaking change per `BREAKING_CHANGES_v{VERSION}.md` manifest (v3.15 precedent) |
| Release Readiness Audit | The structured PASS/FAIL summary emitted by R-REL-029-08 |

#### Mechanism (concrete)

1. **Gate invocation script** at `scripts/release_readiness_gate.py` (or extend existing `scripts/validate_release_gate.py`):
   ```python
   from dataclasses import dataclass
   from typing import Literal, List, Optional
   from pathlib import Path

   CheckStatus = Literal["PASS", "FAIL", "WARN"]

   @dataclass(frozen=True)
   class ReadinessCheck:
       requirement_id: str  # e.g., "R-REL-029-02"
       check_name: str
       status: CheckStatus
       detail: str
       remediation_link: Optional[str] = None

   def run_release_readiness_gate(version: str) -> List[ReadinessCheck]:
       checks = []
       checks.append(check_validator_conformance())  # R-REL-029-02/03
       checks.append(check_readme_consistency())      # R-REL-029-04
       checks.append(check_version_scope_locked(version))  # R-REL-029-05
       checks.append(check_active_release_plan(version))  # R-REL-029-06
       checks.append(check_breaking_change_adr(version))  # R-REL-029-07
       return checks

   def emit_audit(checks: List[ReadinessCheck], date: str) -> Path:
       """Write sessions/release_readiness_audit_{date}.md per R-REL-029-08."""
   ```

2. **SOP integration**: SOP_release_process.md Pre-Flight Conformance Audit section (lines 366+, v1.40) cites this CAP. The current text at line 374 invokes `validate_archetype_skills.py` directly; per this CAP, future iteration wraps invocation in `release_readiness_gate.py` orchestration that runs all R-REL-029-* checks.

3. **Audit artifact** at `sessions/release_readiness_audit_{YYYY-MM-DD}.md`: structured PASS/FAIL per check; consumed by Phase 7.1.5 PIR scoring; archived per L605 release observability discipline.

4. **Cross-CAP relationships**:
   - **CAP-REL-021** (Persistent Validation Logging) — release-readiness audit IS a validation log entry per CAP-REL-021's pattern
   - **CAP-REL-022** (Gate Execution Enforcement) — this gate is one such structural gate; CAP-REL-022 enforces that all gates are executed
   - **CAP-REL-024** (Post-Release Retrospective) — audit artifact feeds into retrospective input
   - **CAP-TPL-016-04** (32 universal skills mandate) — R-REL-029-02 is the consumer of this mandate at release time

#### Acceptance Criteria

- AC-REL-029-1: Validator drift detected (e.g., spec says 32, baseline derives 33) → R-REL-029-03 HALT triggered with diagnostic naming both values
- AC-REL-029-2: README count mismatch with spec (e.g., README says "12 archetypes" but filesystem shows 13) → R-REL-029-04 FAIL with diagnostic
- AC-REL-029-3: VERSION_SCOPE status ∉ {SCOPE_LOCKED, READY FOR RELEASE} → R-REL-029-05 HALT
- AC-REL-029-4: Active PROJECT_PLAN with Gate 1 IN PROGRESS → R-REL-029-06 advisory (not HALT — informational only)
- AC-REL-029-5: BREAKING_CHANGES manifest present + ADR-NN with `Status: Accepted` ratifying breaking policy → R-REL-029-07 PASS; missing ADR → HALT
- AC-REL-029-6: Audit artifact emitted at `sessions/release_readiness_audit_{DATE}.md` with all 7 R-REL-029-NN checks recorded with PASS/FAIL + remediation links
- AC-REL-029-7: All checks PASS → release manager may proceed to version-bump (Phase 0); any FAIL → HALT semantics enforced
- AC-REL-029-8: Audit artifact persists across sessions; PIR (Phase 7.1.5) can reference it for post-release scoring

#### Verification (V-REL-029)

```bash
# V-REL-029-A: Validator conformance check (R-REL-029-02/03)
python3 scripts/release_readiness_gate.py --version 3.15.0 --check validator_conformance 2>&1 | grep -E "PASS|HALT" && \
echo "V-REL-029-A: validator check exists" || echo "V-REL-029-A: FAIL"

# V-REL-029-B: README consistency check (R-REL-029-04)
python3 scripts/release_readiness_gate.py --version 3.15.0 --check readme_consistency 2>&1 | grep -E "PASS|FAIL" && \
echo "V-REL-029-B PASS" || echo "V-REL-029-B FAIL"

# V-REL-029-C: VERSION_SCOPE status ∈ {SCOPE_LOCKED, READY FOR RELEASE} check (R-REL-029-05)
python3 scripts/release_readiness_gate.py --version 3.15.0 --check version_scope_locked 2>&1 | grep -E "PASS|HALT" && \
echo "V-REL-029-C PASS" || echo "V-REL-029-C FAIL"

# V-REL-029-D: Audit artifact emission (R-REL-029-08)
python3 scripts/release_readiness_gate.py --version 3.15.0 && \
test -f sessions/release_readiness_audit_$(date +%Y-%m-%d).md && \
grep -qE "R-REL-029-0[1-8]" sessions/release_readiness_audit_$(date +%Y-%m-%d).md && \
echo "V-REL-029-D PASS" || echo "V-REL-029-D FAIL"
```

V-test PASS criterion: all four sub-tests (A/B/C/D) exit 0; readiness gate is invocable + produces structured audit.

#### Companion Implementation

CAP-REL-029's `scripts/release_readiness_gate.py` is its implementation. **Companion VERSION_SCOPE work**: P1 #4a Wave-1A first contract (this CAP) — implementation script is part of the contract delivery scope. Implementation may extend existing `scripts/validate_release_gate.py` rather than create new module.

#### REQ-REL-F-001 Closure

This CAP closes REQ-REL-F-001 (Pre-Release Validation procedure exists in SOP since v1.38; needs R-REL-* level contract per `PROPOSAL_v315_missing_release_specs.md` 2026-04-19). The procedural pattern was implemented; this contract makes it spec-bound.

#### v3.15 P1 #4a Progress

| Wave-1A Contract | Status | Notes |
|------------------|:------:|-------|
| **R-REL-025 (CAP-REL-029) — Release Readiness Gate** | **LANDED 2026-04-25** (spec + implementation) | First of 5; only CAP with shipped implementation |
| **R-REL-026 (CAP-REL-030) — Post-Release CHANGELOG Validator** | **SPEC-LANDED 2026-05-02; impl-deferred v3.17** | Wave-1A item 2; v3.16 G1.6; #1149/#1151 root cause; **sleeping-requirement** |
| **R-REL-027 (CAP-REL-031) — Post-Release Tag Validator** | **SPEC-LANDED 2026-05-02; impl-deferred v3.17** | Wave-1A item 3; v3.16 G1.6; #1154 spec-layer pair; **inline V-test in SOP v1.30 Phase 6.4.5 enforces invariant procedurally**; CAP closes L671 split when impl lands |
| **R-REL-028 (CAP-REL-032) — Post-Release Badge/Parity Validator** | **SPEC-LANDED 2026-05-02; impl-deferred v3.17** | Wave-1A item 4; v3.16 G1.6; **sleeping-requirement** |
| **R-REL-029 (CAP-REL-033) — Post-Release Contract-Test Validator** | **SPEC-LANDED 2026-05-02; impl-deferred v3.17** | Wave-1A item 5; v3.16 G1.6; #1148 BC-detection scope; **sleeping-requirement** |

**Sleeping-requirement disclosure**: 4 of 5 Wave-1A CAPs ship requirements at v3.16 without implementation. Per R-DEP-010, grace period is 2 minor versions (v3.16 → v3.18). Implementation milestone targets v3.17. This disclosure is per principal direction post-Gate-1-defects-audit (2026-05-02): spec-truthfulness over spec-aspiration.

**Numbering note**: The proposal `PROPOSAL_v315_missing_release_specs.md` reserves R-REL-025 through R-REL-029 as the 5-contract Wave-1A. Existing AGET_RELEASE_SPEC.md uses CAP-REL-NNN format; this CAP claims CAP-REL-029 (next available) and treats `R-REL-025` as the proposal-facing label / requirement-set anchor. Subsequent Wave-1A contracts (proposal labels R-REL-026/027/028/029) will be authored as CAP-REL-030/031/032/033 to avoid further collision; the proposal-facing labels will be cross-referenced in each new CAP's header.

**Evidence**: PROPOSAL_v315_missing_release_specs.md (2026-04-19); SOP_release_process.md v1.38+ Pre-Flight Conformance Audit; v1.40 governing-spec citation correction; #1116 (README count drift evidence); R-REL-020 (VERSION_SCOPE requirement); ADR-022 (breaking change policy precedent); L671 (parent pattern — procedure without contract).

---

### CAP-REL-030: Post-Release CHANGELOG Validator (R-REL-026) — Wave-1A Item 2

**Status**: SPEC-LANDED 2026-05-02 (v3.16 G1.6); IMPLEMENTATION DEFERRED to v3.17 (no `scripts/post_release_changelog_validator.py` at v3.16.0 release; spec defines contract, implementation pending). R-DEP-010 grace-period annotation: 2-minor-version window (v3.16 → v3.18 removal if implementation does not land by v3.17). Wave-1A second contract (2 of 5).

**⚠️ Sleeping-requirement disclaimer**: This CAP defines requirements (R-REL-030-01..05) but no enforcement code exists at v3.16. Consumers SHALL NOT treat this CAP as binding at runtime until the validator script lands. v3.17 implementation milestone tracks closure.

**Threat-Class Anchor**: Post-release verification that CHANGELOG.md entries land correctly. v3.15 retro identified two L-doc-named gaps: L900 (CHANGELOG sanitization gap, #1151) and L909 (under-sanitization at write time, sibling to L900). Without contract enforcement, CHANGELOG entries can be missing, malformed, or contain unsanitized private-fleet references.

#### Requirement Set

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-030-01 | ubiquitous | The release manager SHALL verify, post-release, that the released version has a corresponding entry in `CHANGELOG.md` for every released repo (aget/ + N templates) | Per-repo CHANGELOG required by R-REL-011 + R-REL-036; post-release check confirms compliance |
| R-REL-030-02 | ubiquitous | Each CHANGELOG entry SHALL include version header, date, and a non-empty summary section | Empty or template-placeholder entries indicate incomplete release execution |
| R-REL-030-03 | conditional | IF the release is breaking per `BREAKING_CHANGES_v{VERSION}.md` THEN the CHANGELOG entry SHALL include a "Breaking Changes" subsection with at least one BC-NNN reference | ADR-022 + #1148 BC-detection scope traceability |
| R-REL-030-04 | conditional | IF a CHANGELOG entry references private agent names (`private-*-aget`), private repo paths (`gmelli/*`), or fleet size disclosures THEN the validator SHALL FAIL with sanitization findings | L909 closure (sanitization gate at write-time → audit at post-release as backstop) + L900 #1151 root cause |
| R-REL-030-05 | ubiquitous | The validator SHALL emit per-repo PASS/FAIL results to `sessions/post_release_changelog_audit_{VERSION}_{DATE}.md` | Audit trail consumed by Phase 8 retrospective + PIR scoring |

#### Mechanism

Implementation script: `scripts/post_release_changelog_validator.py`. Iterates released repos via FLEET_REGISTRY or the release's repo list, reads CHANGELOG.md, applies R-REL-030-01..04 checks, emits structured audit per R-REL-030-05.

#### Acceptance Criteria

- AC-REL-030-1: Repo missing CHANGELOG entry for released version → R-REL-030-01 FAIL with diagnostic
- AC-REL-030-2: CHANGELOG entry present but body empty/placeholder → R-REL-030-02 FAIL
- AC-REL-030-3: Breaking release without BC-NNN reference in CHANGELOG → R-REL-030-03 FAIL
- AC-REL-030-4: CHANGELOG contains `private-supervisor-AGET` or `gmelli/aget-aget` → R-REL-030-04 FAIL with line numbers
- AC-REL-030-5: All checks PASS → audit artifact emits at `sessions/post_release_changelog_audit_{VERSION}_{DATE}.md`

#### Verification (V-REL-030)

```bash
# V-REL-030: Validator invocable + audit artifact emitted
python3 scripts/post_release_changelog_validator.py --version 3.16.0 && \
  test -f "sessions/post_release_changelog_audit_3.16.0_$(date +%Y-%m-%d).md" && \
  echo "V-REL-030 PASS" || echo "V-REL-030 FAIL"
```

#### Cross-CAP Relationships

- **R-REL-011 + R-REL-036**: This CAP is the post-release audit pair to the pre-release CHANGELOG-required contracts
- **CAP-SEC-001/004** (Content Security + Public/Private Boundary): R-REL-030-04 is the CHANGELOG-specific instance of CAP-SEC sanitization
- **L900 + L909**: Sibling-of-L909 sanitization gate at write time + this contract as audit backstop

---

### CAP-REL-031: Post-Release Tag Validator (R-REL-027) — Wave-1A Item 3

**Status**: SPEC-LANDED 2026-05-02 (v3.16 G1.6); IMPLEMENTATION DEFERRED to v3.17 (no `scripts/post_release_tag_validator.py` at v3.16.0 release). R-DEP-010 grace-period annotation: v3.16 → v3.18. Wave-1A third contract (3 of 5).

**⚠️ Sleeping-requirement disclaimer**: Same as CAP-REL-030 — requirements defined, no enforcement code at v3.16. **Note**: SOP_release_process.md v1.30 Phase 6.4.5 includes the tag-resolvability check inline (post-tag V-test) so the headline #1154 invariant IS enforced procedurally at release time; this CAP's value is making the invariant audit-script-bound rather than only SOP-step-bound. Implementation closure at v3.17 lifts the procedural-vs-spec L671 split.

**Threat-Class Anchor**: Post-release verification that tags are correctly cut, pushed, and resolve handoff artifacts. #1154 (tag-vs-HEAD fleet artifact gap, root-caused from legalon #1152) confirmed that tags cut at SOP Phase 3 (pre-handoff) returned "not found" for `git show vX.Y.Z:handoffs/RELEASE_HANDOFF_vX.Y.Z.md`. SOP_release_process.md v1.30 (G1.3) moved tag-cut to Phase 6.4.5 procedurally; this CAP makes the tag-resolvability invariant spec-bound (procedure → contract per L671 progression).

#### Requirement Set

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-031-01 | ubiquitous | The release manager SHALL verify, post-tag-push, that `git ls-remote origin v{VERSION}` returns the tag for every released repo | Verifies tag is reachable on remote; not just locally created |
| R-REL-031-02 | ubiquitous | The validator SHALL verify that `git show v{VERSION}:handoffs/RELEASE_HANDOFF_v{VERSION}.md` resolves for the framework repo (aget/) | #1154 closure: tag-pinned handoff must be readable; closes the legalon #1152 root cause class |
| R-REL-031-03 | conditional | IF the release publishes `DEPLOYMENT_SPEC_v{VERSION}.yaml` THEN the validator SHALL verify `git show v{VERSION}:DEPLOYMENT_SPEC_v{VERSION}.yaml` (or `git show v{VERSION}:aget/DEPLOYMENT_SPEC_v{VERSION}.yaml` per L910 path canonicalization) resolves | Tag-pinned deployment spec required for remote fleet supervisors checking out tag |
| R-REL-031-04 | ubiquitous | The validator SHALL verify that tag annotation message includes the version string and a non-empty release-notes pointer | R-REL-035 GitHub Release pair: tag without annotation degrades discoverability |
| R-REL-031-05 | ubiquitous | The validator SHALL emit per-repo tag-resolvability PASS/FAIL to `sessions/post_release_tag_audit_{VERSION}_{DATE}.md` | Audit trail; pair with CAP-REL-030's CHANGELOG audit |

#### Mechanism

Implementation: `scripts/post_release_tag_validator.py`. Uses `git ls-remote` + `git show {tag}:{path}` to verify reachability and tag-pinned content resolution. Sibling to SOP_release_process.md v1.30 Phase 6.4.5 BLOCKING V-test (the SOP runs the check at tag time; this CAP runs it as standalone audit + provides spec backing).

#### Acceptance Criteria

- AC-REL-031-1: Tag missing on remote → R-REL-031-01 FAIL with diagnostic
- AC-REL-031-2: `git show v3.16.0:handoffs/RELEASE_HANDOFF_v3.16.0.md` returns "not found" → R-REL-031-02 FAIL (this is the #1154 regression detection)
- AC-REL-031-3: DEPLOYMENT_SPEC published but not tag-resolvable → R-REL-031-03 FAIL
- AC-REL-031-4: Tag annotation empty or version-string-mismatched → R-REL-031-04 FAIL
- AC-REL-031-5: All checks PASS → audit artifact emits

#### Verification (V-REL-031)

```bash
# V-REL-031: tag-resolvability invariant per #1154
python3 scripts/post_release_tag_validator.py --version 3.16.0 && \
  test -f "sessions/post_release_tag_audit_3.16.0_$(date +%Y-%m-%d).md" && \
  echo "V-REL-031 PASS" || echo "V-REL-031 FAIL"

# V-REL-031-handoff: explicit tag-resolution check (the headline #1154 invariant)
git show v3.16.0:handoffs/RELEASE_HANDOFF_v3.16.0.md >/dev/null 2>&1 && \
  echo "V-REL-031-handoff PASS" || echo "V-REL-031-handoff FAIL — #1154 regression"
```

#### Cross-CAP Relationships

- **R-REL-035**: GitHub Release pair (Releases require tags; this CAP audits tag side, R-REL-035 audits Release side)
- **R-REL-038**: DEPLOYMENT_SPEC pair (spec must exist before tag; this CAP verifies tag resolves it)
- **SOP_release_process.md v1.30 Phase 6.4.5**: This CAP is the spec-layer pair to the SOP-layer fix; SOP enforces ordering at release time, this CAP audits invariant post-release
- **#1154 + legalon #1152**: Root cause class spec-bound here

---

### CAP-REL-032: Post-Release Badge/Parity Validator (R-REL-028) — Wave-1A Item 4

**Status**: SPEC-LANDED 2026-05-02 (v3.16 G1.6); IMPLEMENTATION DEFERRED to v3.17 (no `scripts/post_release_parity_validator.py` at v3.16.0 release). R-DEP-010 grace-period annotation: v3.16 → v3.18. Wave-1A fourth contract (4 of 5).

**⚠️ Sleeping-requirement disclaimer**: Same as CAP-REL-030.

**Threat-Class Anchor**: Post-release verification of org homepage badge (`version: vX.Y.Z`) and parity across templates (README + AGENTS.md @aget-version). v3.15 retro identified silent staleness when badge was not updated despite tags landing — Definition of Done "Discoverable" requires user can find version at org homepage. Without contract, badge update is a discretionary SOP step.

#### Requirement Set

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-032-01 | ubiquitous | The validator SHALL verify, post-release, that the organization homepage (`.github` profile/README.md) displays the released version in a "Latest Release" badge or equivalent visible marker | Definition of Done "Discoverable" criterion (L553) |
| R-REL-032-02 | ubiquitous | The validator SHALL verify that aget/README.md displays the released version in its header | Per-repo README parity |
| R-REL-032-03 | ubiquitous | The validator SHALL verify that every released template's `version.json` `aget_version` field equals the released version | R-REL-VER-001 + R-REL-008 post-release check |
| R-REL-032-04 | ubiquitous | The validator SHALL verify that every released template's AGENTS.md `@aget-version` header equals the released version | Catches AGENTS.md drift independent of version.json (L429 lineage) |
| R-REL-032-05 | conditional | IF parity check fails THEN the validator SHALL classify the failure: (a) badge-missing (org homepage stale), (b) version-drift (intra-repo inconsistency), (c) cross-repo-drift (templates inconsistent), (d) release-body-thin (GitHub Release body < 500 bytes for non-trivial release) | Diagnostic structure for remediation routing; release-body-thin added v3.16.1+ post-defect (L671 at GitHub-Release surface) |
| R-REL-032-06 | ubiquitous | The validator SHALL emit per-repo + cross-repo parity PASS/FAIL to `sessions/post_release_parity_audit_{VERSION}_{DATE}.md` | Audit trail; complements CAP-REL-030/031 |
| R-REL-032-07a | ubiquitous | The validator SHALL verify, post-release, that the **aget core** (`aget-framework/aget`) GitHub Release body content meets **depth-driven** norms: floor 1000 bytes for non-trivial releases; soft cap **2500 bytes** even for non-breaking minor with sleeping-CAPs disclosure; soft cap **3500 bytes** for substantive themed minors. Body bytes > 3500 = WARN (likely verbose-rationale-leakage; per-spec detail belongs in CHANGELOG, not release body). Body SHALL be L909-sanitized; body SHOULD source from CHANGELOG entry per SOP_release_process v1.32 Phase 6.4.5.3, but condensed (release body is at-a-glance scannable; CHANGELOG is full detail). | v3.16.0 calibration history: 138 (under-floor; L671 anti-pattern) → 8904 (over-cap; CHANGELOG-paste anti-pattern) → 1679 (correct; sleeping-CAPs disclosure tight). Caps revised 2026-05-02 after principal "It is still verbose" correction. Sleeping-CAPs/themes justify a few extra bullets but NOT verbose multi-paragraph rationales. Companion: `aget/sops/templates/RELEASE_BODY_TEMPLATE_core.md`. |
| R-REL-032-07b | ubiquitous | The validator SHALL verify, post-release, that each **template-{archetype}-aget** GitHub Release body content meets **alignment-driven** norms: floor 200 bytes for trivial alignment releases; floor 400 bytes when archetype-specific changes shipped; soft cap 1000 (above 1000 = WARN, indicates likely core-content inflation per anti-pattern); body SHALL be L909-sanitized; body SHOULD construct per `aget/sops/templates/RELEASE_BODY_TEMPLATE_template.md` skeleton selection. | v3.16.0 calibration history: archetype-templates at 138 (under-floor) → 1155 (over-cap; CHANGELOG-paste anti-pattern) → 766 (correct; skeleton 2 norm). supervisor/worker stayed at 637-638 (skeleton 3 norm; release-execution archetype). document-processor at 695 (skeleton 4 norm; dormant). Inverse-of-core invariant: a verbose aget core release body SHALL NOT pull templates above their alignment-norm. |
| R-REL-032-07c | conditional | IF a release's aget core body exceeds 3500 bytes AND any template body exceeds 1000 bytes simultaneously, THEN the validator SHALL FLAG "verbose-core-leaked-into-template" pattern (alignment-driven discipline broken; templates picked up core-perspective content). | Inverse-of-core invariant codification. v3.16.0 cycle (post-recalibration) at 1679 core + 766 archetype-templates is well below the joint-threshold; principal "It is still verbose" correction caught the original 8904 + 1155 over-correction before this conditional would have flagged. Threshold-tightening 5000 → 3500 reflects post-correction calibration. |

#### Mechanism

Implementation: `scripts/post_release_parity_validator.py`. Reads org homepage README via `gh api repos/aget-framework/.github/contents/profile/README.md`, parses version badge; for each released repo reads `version.json` and AGENTS.md `@aget-version`; computes parity matrix.

#### Acceptance Criteria

- AC-REL-032-1: Org homepage badge stale (v3.15) after v3.16 release → R-REL-032-01 FAIL classified as `badge-missing`
- AC-REL-032-2: aget/README.md missing version header → R-REL-032-02 FAIL
- AC-REL-032-3: One template's version.json shows old version → R-REL-032-03 FAIL classified as `version-drift`
- AC-REL-032-4: AGENTS.md @aget-version stale on a template → R-REL-032-04 FAIL
- AC-REL-032-5: Two templates show different versions → R-REL-032-03 FAIL classified as `cross-repo-drift`
- AC-REL-032-6: All checks PASS → audit artifact emits

#### Verification (V-REL-032)

```bash
python3 scripts/post_release_parity_validator.py --version 3.16.0 && \
  test -f "sessions/post_release_parity_audit_3.16.0_$(date +%Y-%m-%d).md" && \
  echo "V-REL-032 PASS" || echo "V-REL-032 FAIL"
```

#### Cross-CAP Relationships

- **R-REL-010** (Organization Homepage Update): Pre-release contract; R-REL-032-01 is the post-release audit pair
- **R-REL-008 + R-REL-VER-001**: Version inventory + coherence; this CAP audits at post-release
- **L553 (Definition of Done)**: "Discoverable" outcome criterion; R-REL-032-01 is the spec-bound enforcement

---

### CAP-REL-033: Post-Release Contract-Test Validator (R-REL-029) — Wave-1A Item 5

**Status**: SPEC-LANDED 2026-05-02 (v3.16 G1.6); IMPLEMENTATION DEFERRED to v3.17 (no `scripts/post_release_contract_validator.py` at v3.16.0 release). R-DEP-010 grace-period annotation: v3.16 → v3.18. Wave-1A fifth contract (5 of 5).

**⚠️ Sleeping-requirement disclaimer**: Same as CAP-REL-030.

**Threat-Class Anchor**: Post-release verification that contract tests run on the released tag and pass. v3.15 retro identified BC-002 detection scope gap (#1148): breaking changes were not consistently caught by contract tests, especially when test scope didn't align with the BC-NNN scope. Without spec-bound enforcement, contract tests can drift into theater (ADR-007 anti-pattern).

#### Requirement Set

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-REL-033-01 | ubiquitous | The validator SHALL verify, post-release, that `pytest tests/` (or equivalent test harness) runs against the released tag and exits 0 | Tag must be testable at the released state, not just at HEAD |
| R-REL-033-02 | conditional | IF the release contains BC-NNN entries THEN the validator SHALL verify that at least one contract test exists per BC-NNN with a test name or docstring referencing the BC ID | #1148 closure: BC detection scope must be spec-bound, not implicit |
| R-REL-033-03 | ubiquitous | The validator SHALL verify that test count against the tag does not regress more than 5% from the prior released version (warn) or 10% (FAIL) | ADR-007 No Test Theater; sudden test-count drop indicates skipped/deleted tests masquerading as compliance |
| R-REL-033-04 | conditional | IF any test is `pytest.mark.skip` or `@unittest.skip` THEN the validator SHALL collect and report skip-reasons; skip-reasons containing "TODO" or empty SHALL FAIL | Skip-without-reason is L671 decorative metadata; skip-with-TODO is unfinished work shipped |
| R-REL-033-05 | ubiquitous | The validator SHALL emit per-repo test results + BC-coverage matrix to `sessions/post_release_contract_audit_{VERSION}_{DATE}.md` | Audit trail; consumed by Phase 8 retrospective |

#### Mechanism

Implementation: `scripts/post_release_contract_validator.py`. Checks out released tag in temporary worktree, runs test harness, parses results, computes BC coverage matrix by mapping BC-NNN identifiers to test name/docstring matches. Worktree avoids polluting working tree.

#### Acceptance Criteria

- AC-REL-033-1: Tests on released tag exit non-zero → R-REL-033-01 FAIL
- AC-REL-033-2: BC-002 declared but no test references "BC-002" → R-REL-033-02 FAIL with BC-NNN-without-test diagnostic (#1148 closure)
- AC-REL-033-3: Test count drops from 160 → 130 between releases → R-REL-033-03 FAIL (>10% regression)
- AC-REL-033-4: Skipped test with reason "TODO: fix this" → R-REL-033-04 FAIL
- AC-REL-033-5: All checks PASS → audit artifact emits with full BC-coverage matrix

#### Verification (V-REL-033)

```bash
python3 scripts/post_release_contract_validator.py --version 3.16.0 && \
  test -f "sessions/post_release_contract_audit_3.16.0_$(date +%Y-%m-%d).md" && \
  echo "V-REL-033 PASS" || echo "V-REL-033 FAIL"
```

#### Cross-CAP Relationships

- **ADR-007** (No Test Theater): Parent precedent; R-REL-033-03/04 enforce no-theater post-release
- **#1148 (BC-002 detection scope)**: Root cause spec-bound here via R-REL-033-02
- **CAP-REL-030 (CHANGELOG)**: BC-NNN must appear in CHANGELOG (R-REL-030-03); this CAP verifies BC-NNN has test coverage; together they bind BC declarations end-to-end

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
| CAP-REL-027-* | deployment_monitor.py (deployment tracking + VERSION_SCOPE gate) | **v3.9.0** |
| CAP-REL-028-* | MIGRATION_COMPLETION_REPORT template (upstream feedback section) | **v3.13.0** |

---

## Anti-Patterns

### Anti-Pattern 1: Version Drift (L440)

```
❌ ANTI-PATTERN: Manager behind managed repos

framework-manager: v3.0.0  ← Still at old version!
aget-framework/aget: v3.1.0          ← Released
templates: v3.1.0                    ← Released
```

```
✅ CORRECT: Manager updates first (R-REL-006)

framework-manager: v3.1.0  ← Updated FIRST
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

$ python3 validate_version_consistency.py  ← Runs in framework-manager workspace
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

### Anti-Pattern 7: Loading Dock (L656)

```
❌ ANTI-PATTERN: Start next release before verifying current deployment

v3.8.0 released ← Artifacts created, GitHub tagged
Supervisor notified ← Notification in sender's repo
Fleet at v3.7.0 ← No deployment verified
Agent proposes v3.9.0 ← Next batch starts while v3.8.0 sits on loading dock

# Governance declared victory at IMPLEMENTED
# 0/32 agents deployed. CREATED ≠ DEPLOYED.
```

```
✅ CORRECT: Deployment monitoring blocks next-release planning (CAP-REL-027)

$ python3 scripts/deployment_monitor.py --check --version 3.8.0
Status: RELEASED (72h ago)
Confirmed deployments: 0
⚠️ DEPLOYMENT UNVERIFIED — verify supervisor deployment before VERSION_SCOPE

$ python3 scripts/deployment_monitor.py --confirm --version 3.8.0 --deployer supervisor
Status: DEPLOYING (1 confirmed)
✅ VERSION_SCOPE creation unblocked
```

---

## Authority Model

```yaml
authority:
  applies_to: "version_releases_and_tagging"

  governed_by:
    spec: "AGET_RELEASE_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "Bump version numbers across all repos"
      - "Update CHANGELOG entries"
      - "Run release validation scripts"
      - "Create release handoff artifacts"
      - "Monitor deployment status post-release"
      - "Capture release state snapshots"
    requires_approval:
      - action: "Tag and push release to public repos"
        approver: "principal"
      - action: "Create GitHub Releases"
        approver: "principal"
      - action: "Increment MAJOR version"
        approver: "principal"
      - action: "Override release window timing"
        approver: "principal"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Requirements Grounding (L742)

Per the two-level model (L742): requirements define principal intent (human level); specifications define testable contracts (contract level). This spec traces to `requirements/REQ-REL_release_quality.md`.

| Requirement | Title | CAP-REL Coverage |
|-------------|-------|-----------------|
| REQ-REL-F-001 | Release Readiness Gate | CAP-REL-001, CAP-REL-009, CAP-REL-012 |
| REQ-REL-F-002 | Handoff Completeness | CAP-REL-020, CAP-REL-007 |
| REQ-REL-F-003 | Stability Certification | CAP-REL-027, CAP-REL-016 |
| REQ-REL-F-004 | Template-Fleet Content Parity | CAP-REL-004, CAP-REL-024 |
| REQ-REL-F-005 | Post-Release Validation | CAP-REL-009, CAP-REL-021, CAP-REL-025 |
| REQ-REL-F-006 | Version Scope Pre-Release Audit | CAP-REL-012, CAP-REL-013, CAP-REL-014 |
| REQ-REL-F-007 | Deployment Verification Tooling | R-REL-038 (DEPLOYMENT_SPEC) |
| REQ-REL-F-008 | Remote Fleet Notification | R-REL-019, CAP-REL-020 |
| REQ-REL-Q-001 | Release Predictability | CAP-REL-011 (timing), SOP velocity tracking |
| REQ-REL-Q-002 | Downstream Executability | CAP-REL-020, CAP-REL-007 |
| REQ-REL-Q-003 | Zero-Hotfix Release Target | CAP-REL-009, CAP-REL-021-025 (observability) |
| REQ-REL-F-009 | Upstream Deployment Feedback | CAP-REL-028 |

**Uncovered CAP-RELs** (no upward requirement yet — candidates for REQ-REL v1.1):
- CAP-REL-002 (Version Numbering) — SemVer is an industry standard, not a principal requirement
- CAP-REL-003 (Manager Migration) — operational detail, not principal intent
- CAP-REL-005 (CHANGELOG) — documentation format, subsumed by F-002/Q-002
- CAP-REL-006 (GitHub Releases) — delivery channel, subsumed by F-002
- CAP-REL-008 (Homepage Update) — subsumed by F-002
- CAP-REL-010 (Version Ceiling) — architectural constraint
- CAP-REL-015 (Rollback Plan) — operational detail
- CAP-REL-017/018 (VERSION_SCOPE compliance/reconstruction) — administrative
- CAP-REL-019 (Feature-Descriptive Review) — review process detail
- CAP-REL-022/023 (Gate Enforcement, Snapshots) — observability infrastructure
- CAP-REL-026 (Command Hazards) — operational safety

**Note**: Not every CAP-REL needs a requirement. Specs may contain implementation-level details (operational constraints, format standards) that don't map to principal-level requirements. The traceability table above captures the meaningful upward links.

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
- L656: Loading Dock Anti-Pattern
- SOP_release_process.md
- AGET_VERSIONING_CONVENTIONS.md
- Keep a Changelog (https://keepachangelog.com)
- Semantic Versioning (https://semver.org)

---

## Changelog

### v1.16.1 (2026-05-02)

- **R-REL-022-01 cascade completion**: v1.16.0 amendment landed enum extension at line 519 + R-REL-029-05 line 998, but missed 3 downstream references that still cited the old `LOCKED` value: status-flow diagram (line 526 — `PLANNING → READY FOR RELEASE → RELEASED` lacked SCOPE_LOCKED), AC-REL-029-3 acceptance criterion (line 1058), V-REL-029-C V-test name (line 1076). All three updated to use the canonical 5-value enum or `status ∈ {SCOPE_LOCKED, READY FOR RELEASE}` predicate. Surfaced by distributed-Auditor pass 2026-05-02 13:45 (F-AUDIT-REL-030); incomplete-cascade was effectively L671 at the cross-reference layer.
- See: gmelli/aget-aget#1179 (parent fix), F-AUDIT-REL-030

### v1.16.0 (2026-05-02)

- **R-REL-022-01 enum extension**: added `SCOPE_LOCKED` to VERSION_SCOPE status enum. Now `{PLANNING, SCOPE_LOCKED, READY FOR RELEASE, RELEASED, CANCELLED}`. Closes 3-way vocabulary collision flagged in gmelli/aget-aget#1179: spec text used `LOCKED`/`READY FOR RELEASE` in different requirements; canonical now aligned with L708 vocabulary verbatim
- **R-REL-029-05 cascade**: Pre-Release Conformance Gate now verifies `status ∈ {SCOPE_LOCKED, READY FOR RELEASE}` (was: `exists at LOCKED status` — a value never in the R-REL-022-01 enum); enum coherence restored
- **Header version drift correction**: prior release amendment 457387a (2026-04-26) added v1.15.0 changelog entry but did not bump the **Version** header (left at v1.14.0). v1.16.0 bumps from latest changelog-marked version + this amendment. L671 instance at version-bump layer recorded
- See: gmelli/aget-aget#1179, L708, L914 (path-resolution discipline note from 2026-05-02 session)

### v1.15.0 (2026-04-26)

- Added R-REL-024-03 to CAP-REL-016: fleet upgrade close-outs SHALL include rubric-scored Release_Outcome_Report using `RUBRIC_fleet_upgrade_outcome_v1.1.md`. Score ≥10 required; below 10 must be documented as gaps.
- Closes vibe-not-measurement gap identified in FLEET-UPG-013 (#1149); validated by two-supervisor convergence (FLEET-UPG-013 = 13/15, FLEET-UPG-014 = 10/15)
- See: `aget/rubrics/RUBRIC_fleet_upgrade_outcome_v1.1.md`, #1149, #1165

### v1.14.0 (2026-04-12)

- Added CAP-REL-028: Upstream Deployment Feedback (REQ-REL-F-009, L825, L826)
- 3 EARS requirements for supervisor feedback flow after fleet upgrades
- Added enforcement table entry: MIGRATION_COMPLETION_REPORT template (v3.13.0)
- Added Requirements Grounding entry: REQ-REL-F-009 → CAP-REL-028
- Closes the deployment feedback gap: release lifecycle now extends past "deployment verified" to include deployment learnings return
- See: L825, L826, FLEET-UPG-011, #955

### v1.11.0 (2026-03-28)

- Added Requirements Grounding section (L742 two-level model)
- Maps 9 REQ-REL requirements → CAP-REL coverage
- Identifies 11 uncovered CAP-RELs (operational/format details without principal-level requirements)
- First spec to implement bidirectional requirements ↔ spec traceability
- See: requirements/REQ-REL_release_quality.md, L742, #725

### v1.10.0 (2026-03-08)

- Added CAP-REL-027: Post-Release Deployment Monitoring (ER-DEPLOY-MONITOR, L656, L604)
- Added vocabulary: Deployment_Status_Record, Release_Discovery, Deployment_Delta, Loading_Dock (anti-pattern)
- Added Anti-Pattern 7: Loading Dock (L656)
- Added enforcement table entry: deployment_monitor.py (v3.9.0)
- 5 EARS requirements for deployment status tracking, release discovery, and VERSION_SCOPE blocking
- Design principles: deployable signal (not just existence), ADR-004 three-tier, C-WU-002 non-blocking
- See: L656, L604, PROJECT_PLAN_structural_deployment_verification_v1.0.md

### v1.9.0 (2026-02-22)

- Added R-REL-019-07: Public handoff publication requirement (L612)
- Added sanitization requirements for public handoffs (no private names, paths, fleet size)
- Added V-tests for public handoff existence and sanitization
- See: L612, PROJECT_PLAN_public_release_handoff_remediation_v1.0.md

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
