# AGET Organization Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Process (Organization)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: private-aget-framework-AGET
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

## Roadmap

| Version | Status | Theme |
|---------|--------|-------|
| vX.Y.Z | **Current** | Theme Name |
| vA.B.C | Next | Theme Name |
| vD.E.F | Planned | Theme Name |

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

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| R-REL-010-* | validate_homepage_messaging.py | Planned |
| CAP-ORG-002-* | Manual review | Manual |
| CAP-ORG-003-* | Repository inspection | Manual |

---

## References

- L431: Release Artifact Inventory
- AGET_FRAMEWORK_SPEC.md (CAP-ORG expansion)
- AGET_RELEASE_SPEC.md (R-REL-010, R-REL-011)

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial specification
- Homepage requirements from AGET_FRAMEWORK_SPEC CAP-ORG
- Repository naming conventions
- Release visibility requirements

---

*AGET_ORGANIZATION_SPEC.md — Organization standards for AGET framework*
