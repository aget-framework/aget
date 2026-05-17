# AGET Organization Specification

**Version**: 1.1.2
**Status**: Active
**Category**: Process (Organization)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-03-08
**Author**: aget-framework
**Location**: `aget/specs/AGET_ORGANIZATION_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.4
**Related Specs**: AGET_FRAMEWORK_SPEC, AGET_TEMPLATE_SPEC

---

## Abstract

This specification defines organization-level requirements for the AGET framework GitHub organization, including homepage content, repository naming, pinned repositories, and release visibility.

## Motivation

Organization challenges observed in practice:

1. **Homepage staleness**: Version badges and roadmaps not updated (L431)
2. **Inconsistent naming**: Repository naming varied
3. **Discovery friction**: Key repos not pinned or visible

L431 (Release Artifact Inventory) revealed organization-level gaps.

## Scope

**Applies to**: The aget-framework GitHub organization.

**Defines**:
- Organization homepage requirements
- Repository naming conventions
- Pinned repository policy
- Release visibility requirements

**Does not cover**:
- Individual repository content (see AGET_TEMPLATE_SPEC)
- Release process (see AGET_RELEASE_SPEC)

---

## Requirements

### CAP-ORG-001: Homepage Requirements (R-REL-010)

**SHALL** requirements for organization homepage:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R-REL-010-01 | Homepage SHALL show current version | User information |
| R-REL-010-02 | Roadmap SHALL reflect release status | Planning visibility |
| R-REL-010-03 | Next version SHALL be documented | Roadmap clarity |
| CAP-ORG-001-04 | Homepage SHALL link to key documentation | Accessibility |
| CAP-ORG-001-05 | Homepage SHALL be updated with each release | Currency |
| CAP-ORG-001-06 | Roadmap SHALL include an entry for every publicly released version | Completeness (L657) |

**Homepage Location:** `.github/profile/README.md`

### CAP-ORG-002: Homepage Content Structure

**SHALL** requirements for homepage content:

| ID | Section | Required Content |
|----|---------|------------------|
| CAP-ORG-002-01 | Header | Organization name, tagline, badges |
| CAP-ORG-002-02 | Overview | What AGET is, who it's for |
| CAP-ORG-002-03 | Quick Start | Link to getting started guide |
| CAP-ORG-002-04 | Roadmap | Current version, next version, planned versions |
| CAP-ORG-002-05 | Repositories | Links to key repos with descriptions |
| CAP-ORG-002-06 | Documentation | Links to specs, guides, resources |
| CAP-ORG-002-07 | Contributing | Link to contribution guide |

#### Release History Quality (L657) — renamed from "Roadmap Quality" at v3.18 T1.12 G4 (L943 closure)

**SHALL** requirements for release history section content accuracy:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-ORG-002-08 | Each release history entry SHALL attribute only deliverables from that specific release | Attribution accuracy — prevents Content Absorption (L657) |
| CAP-ORG-002-09 | Each release history entry SHALL show accurate release date matching GitHub Release | Date accuracy — prevents stale date propagation |
| CAP-ORG-002-10 | Release history updates SHALL preserve existing release entries (incremental update, not full replacement) | Prior entry preservation — prevents version erasure |

**Badge Requirements:**

```markdown
![Version](https://img.shields.io/badge/version-{VERSION}-blue)
![Release](https://img.shields.io/badge/release-{DATE}-green)
![License](https://img.shields.io/badge/license-Apache_2.0-orange)
```

### CAP-ORG-003: Repository Naming

**SHALL** requirements for repository names:

| ID | Pattern | Example | Usage |
|----|---------|---------|-------|
| CAP-ORG-003-01 | `aget` | aget | Core framework |
| CAP-ORG-003-02 | `template-{archetype}-aget` | template-advisor-aget | Archetype templates |
| CAP-ORG-003-03 | `.github` | .github | Organization profile |

### CAP-ORG-004: Pinned Repositories

**SHOULD** requirements for pinned repos:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-ORG-004-01 | aget (core) SHOULD be pinned | Primary entry point |
| CAP-ORG-004-02 | Most-used templates SHOULD be pinned | Discovery |
| CAP-ORG-004-03 | Pinned repos SHOULD total ≤6 | GitHub limit |

### CAP-ORG-005: Release Visibility (R-REL-011)

**SHALL** requirements for release visibility:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R-REL-011-01 | Homepage SHOULD update CHANGELOG link | User access |
| R-REL-011-02 | Major releases SHOULD be announced | Communication |
| R-REL-011-03 | Roadmap SHALL show migration version history | Context |

---

## Homepage Template

```markdown
# AGET Framework

> Agent Engineering Tooling for CLI-based Human-AI Collaboration

![Version](https://img.shields.io/badge/version-X.Y.Z-blue)
![Release](https://img.shields.io/badge/release-YYYY--MM--DD-green)
![License](https://img.shields.io/badge/license-Apache_2.0-orange)

## Overview

AGET is a configuration and lifecycle management framework...

## Quick Start

See [Getting Started Guide](link)

## Release History

### vX.Y.Z (Current) - Theme Name
**Released**: YYYY-MM-DD

- Highlight 1 (attributed to THIS release only, per CAP-ORG-002-08)
- Highlight 2

### vA.B.C - Previous Theme
**Released**: YYYY-MM-DD

- Highlight 1
- Highlight 2

## Repositories

| Repository | Description |
|------------|-------------|
| [aget](link) | Core framework |
| [template-supervisor-aget](link) | Supervisor archetype |

## Documentation

- [Framework Specification](link)
- [Getting Started](link)
- [CHANGELOG](link)

## Contributing

See [CONTRIBUTING.md](link)

## License

Apache 2.0
```

### CAP-ORG-006: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-ORG-006-01 | ubiquitous | The SYSTEM shall validate homepage content against CAP-ORG-001 completeness requirements after every release. |
| CAP-ORG-006-02 | event-driven | WHEN a new version is released, THEN the SYSTEM shall update the homepage release history entry for that version (renamed from "roadmap entry" at v3.18 T1.12 G4; L943 closure). |
| CAP-ORG-006-03 | prohibited | The SYSTEM shall NOT publish homepage content that references unreleased versions as current. |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| R-REL-010-* | validate_homepage_messaging.py | Planned |
| CAP-ORG-002-* | Manual review | Manual |
| CAP-ORG-003-* | Repository inspection | Manual |

---

## Authority Model

```yaml
authority:
  applies_to: "organization_management"

  governed_by:
    spec: "AGET_ORGANIZATION_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "Update homepage version badges after a release"
      - "Update roadmap entries with accurate release dates and deliverables"
      - "Verify homepage content against CAP-ORG-002 structure requirements"
      - "Validate repository naming follows CAP-ORG-003 patterns"
    requires_approval:
      - action: "Change homepage content structure (add/remove sections)"
        approver: "aget-framework maintainer"
      - action: "Change pinned repository selection"
        approver: "principal"
      - action: "Add new repository naming patterns"
        approver: "aget-framework maintainer"
      - action: "Major release announcements"
        approver: "principal"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Vocabulary

Domain terms for the Organization specification:

```yaml
vocabulary:
  meta:
    domain: "organization"
    version: "1.0.0"
    inherits: "aget_core"

  terms:
    Organization_Homepage:
      skos:definition: "The GitHub organization profile page rendered from .github/profile/README.md, serving as the primary public entry point"
      aget:location: ".github/profile/README.md"
    Roadmap_Entry:
      skos:definition: "A versioned section on the homepage attributing specific deliverables to a single release with an accurate release date"
    Content_Absorption:
      skos:definition: "Anti-pattern where a homepage rewrite attributes deliverables from prior releases to the current release, erasing version history"
      skos:related: ["L657"]
    Version_Badge:
      skos:definition: "Shield.io badge on the homepage displaying the current framework version, release date, or license"
    Pinned_Repository:
      skos:definition: "GitHub repository pinned to the organization profile for discovery, limited to a maximum of six"
    Repository_Naming_Convention:
      skos:definition: "Standard naming pattern for organization repositories: aget for core, template-{archetype}-aget for templates, .github for profile"
    Release_Visibility:
      skos:definition: "The degree to which release information (changelog, migration history, version) is accessible from the organization homepage"
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-ORG-001 | CAP-ORG-001 | automated | Homepage shows current version badge matching latest GitHub release |
| V-ORG-002 | CAP-ORG-001-06 | manual | Roadmap contains an entry for every publicly released version |
| V-ORG-003 | CAP-ORG-002 | inspection | Homepage contains all 7 required content sections (Header, Overview, Quick Start, Roadmap, Repositories, Documentation, Contributing) |
| V-ORG-004 | CAP-ORG-002-08 | manual | Each release history entry attributes only deliverables from that specific release (no Content Absorption) |
| V-ORG-005 | CAP-ORG-003-02 | automated | Template repositories follow `template-{archetype}-aget` naming convention |
| V-ORG-006 | CAP-ORG-004 | inspection | Pinned repositories include aget (core) and total no more than 6 |
| V-ORG-007 | CAP-ORG-005 | manual | Major releases are announced and roadmap shows migration version history |
| V-ORG-008 | CAP-ORG-006-03 | automated | Homepage does not reference unreleased versions as current |

### Validation Commands

```bash
# Check homepage version badge matches latest release (V-ORG-001, V-ORG-008)
grep -E "version-[0-9]+\.[0-9]+\.[0-9]+" .github/profile/README.md

# Check template repo naming convention (V-ORG-005)
ls -d template-*-aget/ 2>/dev/null | wc -l

# Check homepage has required sections (V-ORG-003)
grep -cE "^## (Overview|Quick Start|Roadmap|Repositories|Documentation|Contributing)" .github/profile/README.md

# Future: automated homepage content validation (V-ORG-001)
python3 validation/validate_homepage_messaging.py
```

---

## References

- L431: Release Artifact Inventory
- L657: Homepage Content Absorption During Release Rewrite
- AGET_FRAMEWORK_SPEC.md (CAP-ORG expansion)
- AGET_RELEASE_SPEC.md (R-REL-010, R-REL-011)

---

## Changelog

### v1.1.1 (2026-03-17)

- Added CAP-ORG-006: EARS System-Level Requirements (L682 L0→L1 uplift)
- 3 requirements with SYSTEM subject, ubiquitous/event-driven/prohibited patterns

### v1.1.0 (2026-03-08)

- Added CAP-ORG-001-06: Roadmap completeness (every released version needs an entry)
- Added CAP-ORG-002-08/09/10: Roadmap quality — attribution accuracy, date accuracy, prior entry preservation
- Updated Homepage Template to reflect actual homepage format (bullet list pattern)
- Added L657 reference (Homepage Content Absorption During Release Rewrite)

### v1.0.0 (2026-01-04)

- Initial specification
- Homepage requirements from AGET_FRAMEWORK_SPEC CAP-ORG
- Repository naming conventions
- Release visibility requirements

---

*AGET_ORGANIZATION_SPEC.md — Organization standards for AGET framework*
