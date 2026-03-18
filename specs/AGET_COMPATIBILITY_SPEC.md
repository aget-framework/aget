# AGET Compatibility Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Lifecycle Management)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_COMPATIBILITY_SPEC.md`

---

## Abstract

This specification defines the version compatibility model for AGET framework. It establishes semantic versioning rules, compatibility matrices, deprecation policies, and upgrade/downgrade paths to ensure predictable version transitions.

## Motivation

Compatibility challenges observed in practice:

1. **Version drift**: Framework evolves while agents remain on older versions
2. **Breaking ambiguity**: Unclear what constitutes a breaking change
3. **Upgrade uncertainty**: No defined path from v2.x to v3.x
4. **Validator mismatches**: Validators from v3.1 running against v3.0 agents
5. **Deprecation confusion**: Features removed without transition period

Gap B3 in GAP_ANALYSIS_v3.0_fleet_exploration.md: "Framework v3.1 → agent on v3.0?" This specification provides the answer.

## Scope

**Applies to**: All AGET framework and agent versions.

**Defines**:
- Semantic_Versioning rules
- Compatibility_Matrix
- Breaking_Change criteria
- Deprecation_Policy
- Upgrade_Path patterns
- Downgrade_Constraints

---

## Vocabulary

Domain terms for compatibility:

```yaml
vocabulary:
  meta:
    domain: "compatibility"
    version: "1.0.0"
    inherits: "aget_core"

  versioning:  # Version concepts
    Semantic_Version:
      skos:definition: "Version number in MAJOR.MINOR.PATCH format"
      skos:example: "3.1.0, 3.0.0-beta.2"
    Major_Version:
      skos:definition: "First segment; changes indicate breaking changes"
      skos:example: "3.x.x"
    Minor_Version:
      skos:definition: "Second segment; changes indicate new features (backward compatible)"
      skos:example: "x.1.x"
    Patch_Version:
      skos:definition: "Third segment; changes indicate bug fixes only"
      skos:example: "x.x.1"
    Pre_Release:
      skos:definition: "Version suffix indicating non-production status"
      skos:example: "alpha.1, beta.2, rc.1"

  compatibility:  # Compatibility concepts
    Backward_Compatible:
      skos:definition: "New version works with artifacts created by older version"
    Forward_Compatible:
      skos:definition: "Old version works with artifacts created by newer version"
    Breaking_Change:
      skos:definition: "Change that breaks backward compatibility"
      skos:narrower: ["Structural_Break", "Behavioral_Break", "API_Break"]
    Compatibility_Matrix:
      skos:definition: "Table showing which versions work together"
    Deprecation_Warning:
      skos:definition: "Notice that feature will be removed in future version"

  changes:  # Change types
    Structural_Break:
      skos:definition: "Change to directory layout, file locations, or schemas"
      skos:example: "Moving .aget/memory/ subdirs"
    Behavioral_Break:
      skos:definition: "Change to expected agent behavior or protocols"
      skos:example: "New required validation step"
    API_Break:
      skos:definition: "Change to script interfaces or manifest schemas"
      skos:example: "New required manifest field"
    Additive_Change:
      skos:definition: "New feature that doesn't affect existing functionality"
      skos:example: "New optional dimension D6+"
```

---

## Requirements

### CAP-COMPAT-001: Semantic Versioning

The SYSTEM shall use Semantic_Versioning for all versions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-001-01 | ubiquitous | The SYSTEM shall format versions as MAJOR.MINOR.PATCH |
| CAP-COMPAT-001-02 | ubiquitous | The SYSTEM shall increment Major_Version for Breaking_Changes |
| CAP-COMPAT-001-03 | ubiquitous | The SYSTEM shall increment Minor_Version for Additive_Changes |
| CAP-COMPAT-001-04 | ubiquitous | The SYSTEM shall increment Patch_Version for bug fixes only |
| CAP-COMPAT-001-05 | optional | WHERE pre-release, the SYSTEM shall use suffix (alpha, beta, rc) |

**Enforcement**: Version validation in `validate_version_consistency.py`

#### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
  3.0.0           - Major release
  3.1.0           - Minor release (new features)
  3.1.1           - Patch release (bug fixes)
  3.0.0-alpha.1   - Pre-release (testing)
  3.0.0-beta.2    - Pre-release (feature complete)
  3.0.0-rc.1      - Release candidate
```

### CAP-COMPAT-002: Compatibility Matrix

The SYSTEM shall maintain explicit Compatibility_Matrix.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-002-01 | ubiquitous | The SYSTEM shall document which framework versions support which agent versions |
| CAP-COMPAT-002-02 | ubiquitous | The SYSTEM shall support agents from N-1 minor versions (backward compatible) |
| CAP-COMPAT-002-03 | conditional | IF Major_Version differs THEN the SYSTEM shall require migration |
| CAP-COMPAT-002-04 | ubiquitous | The SYSTEM shall document forward compatibility limits |

**Enforcement**: Compatibility matrix in release notes.

#### Framework-Agent Compatibility Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRAMEWORK-AGENT COMPATIBILITY MATRIX                  │
├──────────────────┬──────────────────────────────────────────────────────┤
│ Framework Version│              Agent Version                           │
│                  ├──────────┬──────────┬──────────┬──────────┬──────────┤
│                  │ v2.11.x  │ v2.12.x  │ v3.0.x   │ v3.1.x   │ v3.2.x   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ v2.11.x          │ ✅ Full  │ ⚠️ Partial│ ❌ None  │ ❌ None  │ ❌ None  │
│ v2.12.x          │ ✅ Full  │ ✅ Full  │ ⚠️ Partial│ ❌ None  │ ❌ None  │
│ v3.0.x           │ ❌ None  │ ⚠️ Migrate│ ✅ Full  │ ⚠️ Partial│ ❌ None  │
│ v3.1.x           │ ❌ None  │ ⚠️ Migrate│ ✅ Full  │ ✅ Full  │ ⚠️ Partial│
│ v3.2.x           │ ❌ None  │ ❌ Migrate│ ✅ Full  │ ✅ Full  │ ✅ Full  │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

Legend:
  ✅ Full      - All features work, no warnings
  ⚠️ Partial   - Core features work, optional features may not
  ⚠️ Migrate   - Migration required, tools available
  ❌ None      - Incompatible, migration required
```

#### Validator Compatibility Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VALIDATOR-AGENT COMPATIBILITY                         │
├──────────────────┬──────────────────────────────────────────────────────┤
│ Validator From   │              Agent Version                           │
│                  ├──────────┬──────────┬──────────┬──────────┬──────────┤
│                  │ v2.12.x  │ v3.0.x   │ v3.1.x   │ v3.2.x   │ v4.0.x   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ v3.0.x validators│ ⚠️ Warn   │ ✅ Full  │ ✅ Full  │ ✅ Full  │ ⚠️ Partial│
│ v3.1.x validators│ ⚠️ Warn   │ ⚠️ Lenient│ ✅ Full  │ ✅ Full  │ ⚠️ Partial│
│ v3.2.x validators│ ❌ Fail   │ ⚠️ Lenient│ ⚠️ Lenient│ ✅ Full  │ ⚠️ Partial│
└──────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

Rule: Validators should run in LENIENT mode against older agent versions.
```

### CAP-COMPAT-003: Breaking Change Criteria

The SYSTEM shall define what constitutes Breaking_Change.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-003-01 | ubiquitous | Structural_Break (directory/file changes) shall be Breaking_Change |
| CAP-COMPAT-003-02 | ubiquitous | Removing required manifest field shall be Breaking_Change |
| CAP-COMPAT-003-03 | ubiquitous | Changing validator exit codes shall be Breaking_Change |
| CAP-COMPAT-003-04 | conditional | IF spec requirement is mandatory THEN removing it is Breaking_Change |
| CAP-COMPAT-003-05 | ubiquitous | Adding optional feature shall NOT be Breaking_Change |

**Enforcement**: Change classification in release notes.

#### Breaking vs Non-Breaking Changes

```
BREAKING (requires major version bump):
  ❌ Remove required directory (e.g., .aget/persona/)
  ❌ Rename required file (e.g., version.json → identity.json)
  ❌ Remove required manifest field
  ❌ Change existing CAP requirement from optional to prohibited
  ❌ Remove validator without replacement
  ❌ Change exit code semantics

NON-BREAKING (minor version bump):
  ✅ Add new optional directory (e.g., D6_fleet/)
  ✅ Add new optional manifest field
  ✅ Add new CAP requirement (optional)
  ✅ Add new validator
  ✅ Deprecate (with warning) existing feature
  ✅ Add new archetype

PATCH ONLY:
  ✅ Fix validator bug
  ✅ Clarify documentation
  ✅ Fix typo in spec
```

### CAP-COMPAT-004: Deprecation Policy

The SYSTEM shall follow structured deprecation.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-004-01 | ubiquitous | The SYSTEM shall provide Deprecation_Warning for 2 minor versions |
| CAP-COMPAT-004-02 | ubiquitous | The SYSTEM shall document deprecation in CHANGELOG |
| CAP-COMPAT-004-03 | ubiquitous | The SYSTEM shall provide migration path for deprecated features |
| CAP-COMPAT-004-04 | conditional | IF feature is deprecated THEN validators shall warn, not fail |
| CAP-COMPAT-004-05 | ubiquitous | The SYSTEM shall remove deprecated feature in next major version |

**Enforcement**: Deprecation notices in specs and validators.

#### Deprecation Timeline

```
v3.0.0: Feature X is current (no warning)
        │
        ▼
v3.1.0: Feature X is DEPRECATED
        - Deprecation notice in CHANGELOG
        - Validator warns but passes
        - Migration guide published
        │
        ▼
v3.2.0: Feature X still works, warnings continue
        - "Will be removed in v4.0.0" notice
        │
        ▼
v4.0.0: Feature X is REMOVED
        - Validators fail if Feature X detected
        - Migration required

Timeline: 2 minor versions = ~6 months typical
```

#### Deprecation Notice Format

```yaml
deprecation:
  feature: ".aget/memory/domain/"
  deprecated_in: "3.1.0"
  removal_in: "4.0.0"
  reason: "Content belongs in visible knowledge/ directory"
  migration_path: |
    1. Move content from .aget/memory/domain/ to knowledge/
    2. Update any references
    3. Run validate_memory_compliance.py
  validator_behavior: "warn"  # warn | fail
```

### CAP-COMPAT-005: Upgrade Paths

The SYSTEM shall define supported Upgrade_Paths.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-005-01 | ubiquitous | The SYSTEM shall support direct upgrade within same major version |
| CAP-COMPAT-005-02 | ubiquitous | The SYSTEM shall provide migration script for major version upgrades |
| CAP-COMPAT-005-03 | conditional | IF upgrading multiple major versions THEN the SYSTEM shall require sequential migration |
| CAP-COMPAT-005-04 | ubiquitous | The SYSTEM shall document minimum supported upgrade path |

**Enforcement**: Migration scripts and documentation.

#### Supported Upgrade Paths

```
DIRECT UPGRADE (same major):
  v3.0.0 → v3.1.0 → v3.2.0  ✅ Direct
  v3.0.2 → v3.1.0           ✅ Direct

MIGRATION REQUIRED (cross-major):
  v2.12.x → v3.0.x          ⚠️ Use migrate_template_to_v3.py
  v2.11.x → v3.0.x          ⚠️ First upgrade to v2.12, then v3.0

UNSUPPORTED:
  v2.10.x → v3.0.x          ❌ Too old, manual migration
  v1.x.x → v3.0.x           ❌ Too old, fresh start recommended
```

### CAP-COMPAT-006: Downgrade Constraints

The SYSTEM shall define Downgrade_Constraints.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-006-01 | conditional | IF downgrade within patch THEN the SYSTEM shall support it |
| CAP-COMPAT-006-02 | conditional | IF downgrade within minor THEN the SYSTEM shall support with feature loss |
| CAP-COMPAT-006-03 | prohibited | The SYSTEM shall NOT support downgrade across major versions |
| CAP-COMPAT-006-04 | event-driven | WHEN downgrade is requested, the SYSTEM shall warn about feature loss |

**Enforcement**: Downgrade validation in scripts.

#### Downgrade Matrix

```
DOWNGRADE SUPPORT:
  v3.1.1 → v3.1.0  ✅ Full (patch only)
  v3.1.0 → v3.0.0  ⚠️ Feature loss (new v3.1 features removed)
  v3.0.0 → v2.12.0 ❌ Not supported (use backup/git history)

Feature Loss on Downgrade v3.1 → v3.0:
  - D6+ extension directories (must be removed or renamed)
  - CAP-TPL-010 visible directory matrix (ignored)
  - index.json for L-docs (optional anyway)
```

### CAP-COMPAT-007: Spec Version Independence

The SYSTEM shall allow specs to version independently.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-COMPAT-007-01 | ubiquitous | Each spec shall have its own version number |
| CAP-COMPAT-007-02 | ubiquitous | Spec version shall follow Semantic_Versioning |
| CAP-COMPAT-007-03 | conditional | IF spec changes break agents THEN spec major version shall increment |
| CAP-COMPAT-007-04 | ubiquitous | The SYSTEM shall track spec versions in framework release notes |

**Enforcement**: Spec header version field.

#### Spec Version Tracking

```yaml
# Example: v3.1.0 release spec versions
specs:
  AGET_TEMPLATE_SPEC: "3.1.0"    # Updated from 3.0.0
  AGET_MEMORY_SPEC: "1.2.0"      # Updated from 1.1.0
  AGET_PORTABILITY_SPEC: "1.1.0" # Updated from 1.0.0
  AGET_5D_ARCHITECTURE_SPEC: "1.2.0" # Updated from 1.1.0
  AGET_MIGRATION_SPEC: "1.0.0"   # NEW
  AGET_COMPATIBILITY_SPEC: "1.0.0" # NEW
```

---

## Authority Model

```yaml
authority:
  applies_to: "framework_and_agents"

  governed_by:
    spec: "AGET_COMPATIBILITY_SPEC"
    owner: "aget-framework"

  framework_authority:
    can_autonomously:
      - "define compatibility matrix"
      - "set deprecation timeline"
      - "create migration scripts"

    requires_approval:
      - action: "declare breaking change"
        approver: "supervisor"
      - action: "remove deprecated feature"
        approver: "supervisor"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-COMPAT-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT remove feature WITHOUT deprecation period"
      rationale: "Users need transition time"

    - id: "INV-COMPAT-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT break backward compatibility in minor versions"
      rationale: "Semantic versioning contract"

    - id: "INV-COMPAT-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT release major version WITHOUT migration path"
      rationale: "Continuity requirement"
```

---

## Structural Requirements

```yaml
structure:
  required_in_releases:
    - path: "CHANGELOG.md"
      content: "Breaking changes, deprecations, migration notes"

    - path: "docs/MIGRATION_GUIDE.md"
      content: "Step-by-step upgrade instructions"

  required_in_specs:
    - field: "Version"
      format: "MAJOR.MINOR.PATCH"

    - section: "Graduation History"
      purpose: "Track spec evolution"
```

---

## Compatibility Contract

Framework releases MUST satisfy:

```yaml
contracts:
  - name: semantic_versioning
    assertion: version_format
    rule: "Version matches MAJOR.MINOR.PATCH[-PRERELEASE]"

  - name: backward_compatibility
    assertion: minor_version_compatible
    rule: "Minor version changes maintain backward compatibility"

  - name: deprecation_period
    assertion: feature_lifecycle
    rule: "Deprecated features remain for 2 minor versions"

  - name: migration_available
    assertion: major_version_migration
    rule: "Major version changes include migration script"
```

---

## Theoretical Basis

Compatibility architecture is grounded in:

| Theory | Application |
|--------|-------------|
| **Semantic Versioning** | Predictable version meaning |
| **Hyrum's Law** | Users depend on any observable behavior |
| **Backward Compatibility** | New versions work with old artifacts |
| **Graceful Degradation** | Partial functionality when mismatched |

```yaml
theoretical_basis:
  primary: "Semantic Versioning (semver.org)"
  secondary:
    - "Hyrum's Law"
    - "Postel's Law (Be liberal in what you accept)"
    - "Graceful Degradation"
  rationale: >
    Compatibility specification treats version contracts seriously.
    Semantic versioning (semver) provides predictable meaning.
    Hyrum's Law reminds us that any observable behavior becomes depended upon.
    Postel's Law guides validators to be lenient with older versions.
    Graceful degradation enables partial functionality during transitions.
  references:
    - "https://semver.org/"
    - "GAP_ANALYSIS_v3.0_fleet_exploration.md (Gap B3)"
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-COMPAT-001 | CAP-COMPAT-001 | automated | Verify all versions follow MAJOR.MINOR.PATCH format with optional pre-release suffix |
| V-COMPAT-002 | CAP-COMPAT-002 | inspection | Verify compatibility matrix is documented and agents from N-1 minor versions are supported |
| V-COMPAT-003 | CAP-COMPAT-003 | inspection | Verify breaking change criteria are applied correctly (structural, behavioral, API breaks require major bump) |
| V-COMPAT-004 | CAP-COMPAT-004 | manual | Verify deprecated features provide 2 minor versions of warning with migration path before removal |
| V-COMPAT-005 | CAP-COMPAT-005 | automated | Verify migration scripts exist for major version upgrades and direct upgrade works within same major |
| V-COMPAT-006 | CAP-COMPAT-006 | inspection | Verify downgrade constraints are enforced (patch OK, minor with warning, cross-major prohibited) |
| V-COMPAT-007 | CAP-COMPAT-007 | automated | Verify each spec has independent version number following semantic versioning |
| V-COMPAT-008 | CAP-COMPAT-001 | automated | Verify version.json across all templates uses valid MAJOR.MINOR.PATCH format |
| V-COMPAT-009 | CAP-COMPAT-004 | automated | Verify CHANGELOG documents deprecation notices with removal version target |
| V-COMPAT-010 | CAP-COMPAT-005 | manual | Verify sequential migration is required when upgrading across multiple major versions |

### Validation Commands

```bash
# Check version format consistency (V-COMPAT-001, V-COMPAT-008)
python3 validation/validate_version_consistency.py agent-path/

# Check framework-agent compatibility (V-COMPAT-002)
python3 validation/validate_compatibility.py \
  --framework-version 3.1.0 \
  --agent-version 3.0.0

# Verify spec version independence (V-COMPAT-007)
for spec in aget/specs/AGET_*_SPEC.md; do
  version=$(grep -m1 "^\*\*Version\*\*:" "$spec" | sed 's/.*: //')
  echo "$spec: $version"
done
```

---

## References

- Semantic Versioning 2.0.0 (semver.org)
- AGET_MIGRATION_SPEC.md (migration procedures)
- AGET_TEMPLATE_SPEC.md (template version requirements)
- GAP_ANALYSIS_v3.0_fleet_exploration.md (Gap B3)
- L394: Design by Fleet Exploration

---

## Graduation History

```yaml
graduation:
  trigger: "Gap B3 in GAP_ANALYSIS_v3.0_fleet_exploration.md"
  question: "Framework v3.1 → agent on v3.0?"
  source_patterns:
    - "Semantic versioning in version.json"
    - "Migration scripts for major versions"
  rationale: "Implicit compatibility rules formalized into specification"
```

---

*AGET Compatibility Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Lifecycle Management - Gap B3*
*"Predictable versions enable confident evolution."*
