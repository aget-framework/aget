# AGET Versioning Conventions

**Version**: 1.0.0
**Date**: 2025-12-01
**Status**: CANONICAL
**Location**: aget/specs/AGET_VERSIONING_CONVENTIONS.md

---

## Purpose

This document defines versioning conventions for the AGET framework, including semantic versioning rules, version fields, and migration requirements.

---

## Semantic Versioning

AGET follows [Semantic Versioning 2.0.0](https://semver.org/) with framework-specific interpretations.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
- 2.9.0        (stable release)
- 2.9.1        (patch release)
- 3.0.0-alpha  (pre-release)
```

### Version Components

| Component | When to Increment | Example Change |
|-----------|------------------|----------------|
| **MAJOR** | Breaking changes | New required fields, removed capabilities |
| **MINOR** | New features, backward compatible | New optional capabilities, new templates |
| **PATCH** | Bug fixes, documentation | Fix typo, clarify spec |
| **PRERELEASE** | Testing/preview | alpha, beta, rc1 |

---

## Breaking Change Definition

A change is **breaking** if it requires existing agents to modify their configuration to remain compliant.

### Breaking Changes (require MAJOR bump)

- Adding required fields to Version_Json
- Removing or renaming existing capabilities
- Changing AGENTS.md required sections
- Modifying session protocol signatures
- Changing contract test requirements

### Non-Breaking Changes (MINOR or PATCH)

- Adding optional fields
- Adding new capabilities
- Deprecating (not removing) features
- Documentation improvements
- Bug fixes in validation

---

## Version Fields

### aget_version (Required)

The framework version this agent complies with.

```json
{
  "aget_version": "2.9.0"
}
```

**Rules**:
- MUST be valid semver
- MUST match a released framework version
- Determines which specifications apply

### Version Compatibility

| Agent Version | Framework Compatibility |
|--------------|------------------------|
| 2.9.x | Compatible with 2.9.0 specs |
| 2.8.x | Compatible with 2.8.0 specs |
| 2.x.x | May require migration for 3.0.0 |

---

## Migration Requirements

### Migration Triggers

| Version Change | Migration Required | Migration Type |
|---------------|-------------------|----------------|
| 2.9.0 → 2.9.1 | No | None |
| 2.8.0 → 2.9.0 | Maybe | Review release notes |
| 2.x.x → 3.0.0 | Yes | Full migration |

### Migration History Field

Track migrations in Version_Json:

```json
{
  "aget_version": "2.9.0",
  "migration_history": [
    "v2.0.0 -> v2.5.0: 2025-10-06 (validation framework)",
    "v2.5.0 -> v2.6.0: 2025-10-12 (size management)",
    "v2.6.0 -> v2.7.0: 2025-10-13 (portfolio governance)",
    "v2.7.0 -> v2.8.0: 2025-11-08 (friction reduction)",
    "v2.8.0 -> v2.9.0: 2025-12-01 (core specifications)"
  ]
}
```

### Migration Script Convention

```
scripts/migrations/v{FROM}_to_v{TO}.py

Examples:
- v2.8_to_v2.9.py
- v2.9_to_v3.0.py
```

---

## Release Process

### Multi-Repo Coordination Protocol (R-REL-001)

The AGET framework spans multiple repositories that must be version-synchronized.

**Repository Structure**:
```
aget-framework/
├── aget/                    <- Core framework (primary version)
├── template-supervisor-aget/
├── template-worker-aget/
├── template-advisor-aget/
├── template-consultant-aget/
├── template-developer-aget/
└── template-spec-engineer-aget/
```

**R-REL-001-01: Core First**
```
The aget/ core repository is versioned and tagged first.
All template repositories inherit this version.
```

**R-REL-001-02: Atomic Fleet Release**
```
When releasing:
1. Update aget/ core version
2. Update all template version.json files
3. Tag aget/ first
4. Tag all templates with same version
5. Push all tags atomically
```

**R-REL-001-03: Version Sync Validation**
```bash
# All templates must match core version
python3 scripts/version_sync.py --check
```

### Pre-Release Checklist

- [ ] All changes documented in CHANGELOG.md
- [ ] Breaking changes identified
- [ ] Migration guide written (if breaking)
- [ ] Contract tests pass
- [ ] Version bumped in all affected files
- [ ] Version sync validated across all repos (R-REL-001)

### Version Bump Locations

When releasing, update version in:

1. `aget/README.md` - Version footer
2. Template `version.json` files - `aget_version` field
3. Specification files - `version` field
4. CHANGELOG.md - New section header

### Tagging Convention

```bash
git tag -a v2.9.0 -m "Release v2.9.0: Core specifications"
git push origin v2.9.0
```

Tag format: `v{MAJOR}.{MINOR}.{PATCH}`

---

## Deprecation Policy

### Deprecation Process

1. **Announce**: Mark feature as deprecated in release notes
2. **Document**: Add deprecation notice to specification
3. **Warn**: Emit warning when deprecated feature used
4. **Remove**: Remove in next MAJOR version

### Deprecation Notice Format

```yaml
CAP-OLD:
  status: DEPRECATED
  deprecated_in: "2.9.0"
  removed_in: "3.0.0"
  replacement: "CAP-NEW"
  migration: "Use CAP-NEW instead; see MIGRATION_GUIDE.md"
```

### Minimum Deprecation Period

- MINOR features: 1 MINOR version
- MAJOR features: 1 MAJOR version

---

## Version History

### Current Version: 2.10.0

| Version | Date | Highlights |
|---------|------|------------|
| 2.10.0 | 2025-12-13 | Capability Composition Architecture, L330-L332 |
| 2.9.0 | 2025-12-01 | Core specifications, WORKER_TEMPLATE_SPEC |
| 2.8.0 | 2025-11-08 | Friction reduction, planning framework |
| 2.7.0 | 2025-10-13 | Portfolio governance, fleet coordination |
| 2.6.0 | 2025-10-12 | Configuration size management |
| 2.5.0 | 2025-10-06 | Validation framework, contract tests |

### Planned Versions

| Version | Target | Scope |
|---------|--------|-------|
| 2.9.x | Q4 2025 | Patch releases for core specs |
| 3.0.0 | Q2 2026 | Full framework conformance spec |

---

## Compatibility Matrix

### Template Compatibility

| Template Version | Framework 2.8.x | Framework 2.9.x | Framework 3.0.x |
|-----------------|-----------------|-----------------|-----------------|
| 2.8.x | Full | Backward | Migration Required |
| 2.9.x | - | Full | Migration Required |
| 3.0.x | - | - | Full |

### CLI Compatibility

AGET is designed for universal CLI compatibility:

| CLI | Support Level |
|-----|--------------|
| Claude Code | Full |
| Cursor | Full |
| Aider | Full |
| Windsurf | Full |

---

## Version Checking

### Programmatic Version Check

```python
import json

def check_version_compatibility(agent_path, required_version):
    """Check if agent meets minimum version requirement."""
    with open(f"{agent_path}/.aget/version.json") as f:
        config = json.load(f)

    agent_version = config.get("aget_version", "0.0.0")

    # Parse versions
    agent_parts = [int(x) for x in agent_version.split(".")]
    required_parts = [int(x) for x in required_version.split(".")]

    # Compare major.minor (patch is always compatible)
    return agent_parts[:2] >= required_parts[:2]
```

### Contract Test

```python
def test_version_is_valid_semver():
    """Verify aget_version follows semver format."""
    import re
    version = config["aget_version"]
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$"
    assert re.match(pattern, version), f"Invalid version: {version}"
```

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- ADR-012: Migration Strategy
- AGET_SPEC_FORMAT_v1.1.md

---

*AGET_VERSIONING_CONVENTIONS.md — Version governance for AGET framework*
