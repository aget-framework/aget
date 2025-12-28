# AGET Migration Specification

**Version**: 1.4.0
**Status**: Active
**Category**: Standards (Lifecycle Management)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-28
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_MIGRATION_SPEC.md`

---

## Abstract

This specification defines the formal migration process for AGET agents, templates, and fleets. It establishes standard phases, validation gates, rollback procedures, and artifact formats to ensure reliable version transitions.

## Motivation

Migration challenges observed in practice:

1. **Ad-hoc processes**: Scripts created per-migration without standardization
2. **Incomplete validation**: Behavioral validation without automated compliance checks
3. **Missing rollback**: No formal recovery path when migrations fail
4. **Fleet coordination**: No standard for multi-agent migration sequencing
5. **Artifact preservation**: Inconsistent archival of pre-migration state

L392 (Pilot-Driven Migration Automation) and L394 (Design by Fleet Exploration) revealed these gaps. This specification formalizes patterns validated in v3.0.0-beta.2.

## Scope

**Applies to**: All AGET framework version transitions.

**Defines**:
- Migration_Types (Template, Instance, Fleet)
- Migration_Phases (5-phase model)
- Validation_Gate requirements
- Rollback_Protocol
- Migration_Manifest format
- Archive_Policy

---

## Vocabulary

Domain terms for migration:

```yaml
vocabulary:
  meta:
    domain: "migration"
    version: "1.0.0"
    inherits: "aget_core"

  migration:  # Core concepts
    Migration:
      skos:definition: "Controlled transition from one framework version to another"
      skos:narrower: ["Template_Migration", "Instance_Migration", "Fleet_Migration"]
    Migration_Phase:
      skos:definition: "Discrete step in migration process"
      skos:narrower: ["Analyze", "Plan", "Execute", "Validate", "Cleanup"]
    Migration_Manifest:
      skos:definition: "Record of migration actions and pre-migration state"
      aget:location: ".aget/archive/_archive_manifest.json"
    Rollback_Point:
      skos:definition: "Saved state enabling migration reversal"
    Validation_Gate:
      skos:definition: "Blocking checkpoint requiring all validators to pass"
      skos:related: "PATTERN_migration_validation_gate.md"

  types:  # Migration types
    Template_Migration:
      skos:definition: "Migration of template repository to new spec version"
      skos:note: "Templates are canonical; instances derive from them"
    Instance_Migration:
      skos:definition: "Migration of deployed agent instance"
      skos:note: "May include user content preservation"
    Fleet_Migration:
      skos:definition: "Coordinated migration of multiple agents"
      skos:narrower: ["Pilot_Phase", "Expand_Phase", "Complete_Phase"]

  phases:  # Migration phases
    Analyze_Phase:
      skos:definition: "Examine current state and identify migration scope"
      skos:output: "Compliance report, migration plan"
    Plan_Phase:
      skos:definition: "Create gated PROJECT_PLAN with rollback strategy"
      skos:output: "PROJECT_PLAN, gate definitions"
    Execute_Phase:
      skos:definition: "Perform structural changes per plan"
      skos:output: "Migrated artifacts, archive"
    Validate_Phase:
      skos:definition: "Run all validators and behavioral tests"
      skos:output: "Validation report, GO/NOGO decision"
    Cleanup_Phase:
      skos:definition: "Remove archives after verification period"
      skos:output: "Clean repository"

  artifacts:  # Migration artifacts
    Archive_Directory:
      skos:definition: "Holding location for pre-migration artifacts"
      aget:location: ".aget/archive/"
    Compliance_Report:
      skos:definition: "Analysis output showing compliant vs legacy items"
    Migration_Script:
      skos:definition: "Automated migration tool"
      skos:example: "migrate_template_to_v3.py"
```

---

## Requirements

### CAP-MIG-001: Migration Types

The SYSTEM shall support three Migration_Types.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-001-01 | ubiquitous | The SYSTEM shall support Template_Migration for template repositories |
| CAP-MIG-001-02 | ubiquitous | The SYSTEM shall support Instance_Migration for deployed agents |
| CAP-MIG-001-03 | ubiquitous | The SYSTEM shall support Fleet_Migration for multi-agent coordination |
| CAP-MIG-001-04 | conditional | IF Fleet_Migration THEN the SYSTEM shall use Pilot_Phase before full rollout |

**Enforcement**: Migration scripts must identify migration type.

#### Migration Type Matrix

```
┌──────────────────────────────────────────────────────────────────┐
│                    MIGRATION TYPE MATRIX                          │
├─────────────────┬────────────────┬───────────────────────────────┤
│ Type            │ Scope          │ Rollback Complexity           │
├─────────────────┼────────────────┼───────────────────────────────┤
│ Template        │ 1 repository   │ Low (git revert)              │
│ Instance        │ 1 agent        │ Medium (archive restore)      │
│ Fleet           │ N agents       │ High (coordinated rollback)   │
└─────────────────┴────────────────┴───────────────────────────────┘
```

### CAP-MIG-002: Five-Phase Model

The SYSTEM shall execute migrations through five sequential phases.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-002-01 | ubiquitous | The SYSTEM shall complete Analyze_Phase before Plan_Phase |
| CAP-MIG-002-02 | ubiquitous | The SYSTEM shall complete Plan_Phase before Execute_Phase |
| CAP-MIG-002-03 | ubiquitous | The SYSTEM shall complete Execute_Phase before Validate_Phase |
| CAP-MIG-002-04 | ubiquitous | The SYSTEM shall complete Validate_Phase before Cleanup_Phase |
| CAP-MIG-002-05 | conditional | IF Validate_Phase fails THEN the SYSTEM shall NOT proceed to Cleanup_Phase |

**Enforcement**: Phase gates in migration scripts.

#### Phase Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     FIVE-PHASE MIGRATION MODEL                   │
│                                                                  │
│   ┌─────────┐    ┌──────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│   │ ANALYZE │ -> │ PLAN │ -> │ EXECUTE │ -> │ VALIDATE │ -> │ CLEANUP  │
│   └─────────┘    └──────┘    └─────────┘    └──────────┘    └──────────┘
│        │              │            │              │               │
│        ▼              ▼            ▼              ▼               ▼
│   Compliance    PROJECT_PLAN  Archive +      Validators     Remove
│   Report        + Gates       Migrate        + Behavioral   Archive
│                                                    │
│                                              ┌─────┴─────┐
│                                              │  NOGO?    │
│                                              │  ROLLBACK │
│                                              └───────────┘
└─────────────────────────────────────────────────────────────────┘
```

### CAP-MIG-003: Analyze Phase

The SYSTEM shall analyze migration scope before planning.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-003-01 | event-driven | WHEN Migration is initiated, the SYSTEM shall run Compliance_Analysis |
| CAP-MIG-003-02 | ubiquitous | The SYSTEM shall identify Compliant_Items versus Legacy_Items |
| CAP-MIG-003-03 | ubiquitous | The SYSTEM shall identify Delete_Candidates (framework code in templates) |
| CAP-MIG-003-04 | ubiquitous | The SYSTEM shall generate Compliance_Report in JSON format |
| CAP-MIG-003-05 | conditional | IF Compliance_Report shows is_compliant=true THEN the SYSTEM shall skip migration |

**Enforcement**: `analyze_template_compliance.py`

#### Analysis Output Format

```json
{
  "template": "template-example-aget",
  "spec_version": "3.0",
  "analysis_date": "2025-12-27T10:00:00Z",
  "compliance": {
    "compliant_items": [...],
    "legacy_dirs": [...],
    "legacy_files": [...],
    "delete_candidates": [...]
  },
  "summary": {
    "is_compliant": false,
    "compliant_count": 19,
    "legacy_items": 24,
    "delete_candidates": 2
  }
}
```

### CAP-MIG-004: Plan Phase

The SYSTEM shall create formal migration plan before execution.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-004-01 | ubiquitous | The SYSTEM shall create PROJECT_PLAN for non-trivial migrations |
| CAP-MIG-004-02 | ubiquitous | The PROJECT_PLAN shall include Validation_Gate (BLOCKING) |
| CAP-MIG-004-03 | ubiquitous | The PROJECT_PLAN shall document Rollback_Strategy |
| CAP-MIG-004-04 | conditional | IF Fleet_Migration THEN the PROJECT_PLAN shall define Pilot_Agents |
| CAP-MIG-004-05 | ubiquitous | The SYSTEM shall require User_Approval before Execute_Phase |

**Enforcement**: PROJECT_PLAN template, gate checklist.

### CAP-MIG-005: Execute Phase

The SYSTEM shall perform migration with archive preservation.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-005-01 | ubiquitous | The SYSTEM shall create Archive_Directory before moving items |
| CAP-MIG-005-02 | ubiquitous | The SYSTEM shall archive Legacy_Items to `.aget/archive/_legacy_dirs/` |
| CAP-MIG-005-03 | ubiquitous | The SYSTEM shall archive Legacy_Files to `.aget/archive/_legacy_files/` |
| CAP-MIG-005-04 | ubiquitous | The SYSTEM shall write Migration_Manifest to `.aget/archive/_archive_manifest.json` |
| CAP-MIG-005-05 | ubiquitous | The SYSTEM shall delete Delete_Candidates after archiving |
| CAP-MIG-005-06 | optional | WHERE --dry-run flag, the SYSTEM shall show actions without executing |

**Enforcement**: `migrate_template_to_v3.py`

#### Archive Structure

```
.aget/archive/
├── _legacy_dirs/           # Archived directories
│   ├── architecture/
│   ├── backups/
│   └── ...
├── _legacy_files/          # Archived files
│   ├── BRANCHING.md
│   ├── dependencies.json
│   └── ...
└── _archive_manifest.json  # Migration record
```

#### Migration Manifest Format

```json
{
  "migration_date": "2025-12-27T10:00:00Z",
  "template": "template-example-aget",
  "from_version": "2.x",
  "to_version": "3.0",
  "archived_items": [
    {"source": ".aget/architecture/", "target": ".aget/archive/_legacy_dirs/architecture/", "type": "directory"}
  ],
  "deleted_items": [
    {"path": "aget/", "type": "directory"}
  ],
  "rollback_command": "python3 rollback_migration.py --manifest .aget/archive/_archive_manifest.json"
}
```

### CAP-MIG-006: Validate Phase (BLOCKING)

The SYSTEM shall complete all validation before cleanup.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-006-01 | ubiquitous | The SYSTEM shall run ALL required validators |
| CAP-MIG-006-02 | ubiquitous | The SYSTEM shall require Exit_Code 0 from all validators |
| CAP-MIG-006-03 | ubiquitous | The SYSTEM shall perform Behavioral_Validation per CAP-MIG-006-03a through CAP-MIG-006-03f |
| CAP-MIG-006-03a | ubiquitous | Behavioral_Validation shall execute wake_up.py without error |
| CAP-MIG-006-03b | ubiquitous | Behavioral_Validation shall verify version display matches version.json AND AGENTS.md |
| CAP-MIG-006-03c | ubiquitous | Behavioral_Validation shall verify AGENTS.md size ≤ 40000 characters (CAP-TPL-008-01) |
| CAP-MIG-006-03d | conditional | IF sanity_check script exists THEN Behavioral_Validation shall execute it |
| CAP-MIG-006-03e | conditional | IF archetype=supervisor THEN Behavioral_Validation shall verify fleet inventory accuracy |
| CAP-MIG-006-03f | conditional | IF archetype=supervisor THEN Behavioral_Validation shall verify portfolio tracking completeness |
| CAP-MIG-006-04 | conditional | IF any validator fails THEN the SYSTEM shall STOP and report |
| CAP-MIG-006-05 | prohibited | The SYSTEM shall NOT proceed to Cleanup_Phase with FAIL status |
| CAP-MIG-006-06 | event-driven | WHEN all validations pass, the SYSTEM shall issue GO decision |

**Enforcement**: `PATTERN_migration_validation_gate.md`

**Rationale**: L402 analysis of supervisor session revealed missing behavioral checks — wake_up showed correct version but fleet state was stale, AGENTS.md exceeded size limit.

#### Required Validators

| Validator | Purpose |
|-----------|---------|
| `validate_version_consistency.py` | Version alignment |
| `validate_naming_conventions.py` | L-doc/ADR naming |
| `validate_template_manifest.py` | Manifest schema |
| `validate_composition.py` | Capability composition |
| `validate_agents_md_size.py` | Configuration size (CAP-MIG-006-03c) |

### CAP-MIG-007: Cleanup Phase

The SYSTEM shall remove archives after verification period.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-007-01 | conditional | IF Verification_Period (7 days) elapsed THEN the SYSTEM may remove Archive_Directory |
| CAP-MIG-007-02 | ubiquitous | The SYSTEM shall verify no references to archived items before removal |
| CAP-MIG-007-03 | event-driven | WHEN cleanup is complete, the SYSTEM shall run final validation |
| CAP-MIG-007-04 | optional | WHERE --preserve-archive flag, the SYSTEM shall retain Archive_Directory |

**Enforcement**: `cleanup_template_archive.py`

### CAP-MIG-008: Rollback Protocol

The SYSTEM shall support migration reversal.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-008-01 | ubiquitous | The SYSTEM shall preserve Rollback_Point in Migration_Manifest |
| CAP-MIG-008-02 | event-driven | WHEN rollback is requested, the SYSTEM shall restore from Archive_Directory |
| CAP-MIG-008-03 | ubiquitous | The SYSTEM shall restore files to original locations from manifest |
| CAP-MIG-008-04 | conditional | IF Archive_Directory is missing THEN the SYSTEM shall use git history |
| CAP-MIG-008-05 | ubiquitous | The SYSTEM shall validate state after rollback |

**Enforcement**: `rollback_migration.py` (to be created)

#### Rollback Decision Tree

```
Migration Failed?
     │
     ├── YES: Archive exists?
     │         ├── YES: Run rollback_migration.py
     │         └── NO: Use git revert
     │
     └── NO: Proceed to Cleanup
```

### CAP-MIG-009: Fleet Migration

The SYSTEM shall coordinate multi-agent migrations.

### CAP-MIG-010: Version Synchronization

The SYSTEM shall maintain version consistency across all version sources.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-010-01 | ubiquitous | The SYSTEM shall update `@aget-version:` tag in AGENTS.md |
| CAP-MIG-010-02 | ubiquitous | The SYSTEM shall update `aget_version` in version.json |
| CAP-MIG-010-03 | conditional | IF CLAUDE.md is not a symlink THEN the SYSTEM shall update CLAUDE.md |
| CAP-MIG-010-04 | ubiquitous | The `@aget-version` and `aget_version` values SHALL match |

**Rationale**: L401 revealed that updating version.json without AGENTS.md causes version display inconsistency (wake_up.py reads from AGENTS.md).

**Enforcement**: `migrate_instance_to_v3.py` GATE 5.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-009-01 | ubiquitous | The SYSTEM shall use three-phase rollout (Pilot, Expand, Complete) |
| CAP-MIG-009-02 | ubiquitous | The SYSTEM shall select 1-3 Pilot_Agents for initial migration |
| CAP-MIG-009-03 | conditional | IF Pilot_Phase fails THEN the SYSTEM shall NOT proceed to Expand_Phase |
| CAP-MIG-009-04 | ubiquitous | The SYSTEM shall capture learnings between phases |
| CAP-MIG-009-05 | optional | WHERE parallel execution is safe, the SYSTEM may batch migrations |
| CAP-MIG-009-06 | event-driven | WHEN pilot migration completes, the SYSTEM shall update FLEET_MIGRATION_PLAN |
| CAP-MIG-009-07 | ubiquitous | The SYSTEM shall update agent priority from P1-pending to P1-complete |

**Enforcement**: Fleet migration PROJECT_PLAN structure.

### CAP-MIG-011: Size Compliance Validation

The SYSTEM shall validate configuration file sizes.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-011-01 | ubiquitous | The SYSTEM shall validate AGENTS.md size BEFORE migration |
| CAP-MIG-011-02 | conditional | IF AGENTS.md > 40000 characters THEN the SYSTEM shall BLOCK migration |
| CAP-MIG-011-03 | conditional | IF AGENTS.md > 35000 characters THEN the SYSTEM shall emit Size_Warning |
| CAP-MIG-011-04 | ubiquitous | The SYSTEM shall validate AGENTS.md size AFTER migration |
| CAP-MIG-011-05 | event-driven | WHEN size violation detected, the SYSTEM shall report remediation options |

**Rationale**: L402 revealed AGENTS.md at 47.6k characters (exceeds 40k limit from CAP-TPL-008-01). Size validation prevents migrations that would result in non-compliant configurations.

**Enforcement**: `validate_agents_md_size.py`, migration script pre-check.

### CAP-MIG-012: Supervisor Fleet State Synchronization

The SYSTEM shall maintain supervisor fleet state accuracy.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-012-01 | conditional | IF migrating Supervisor_Agent THEN the SYSTEM shall verify FLEET_STATE accuracy |
| CAP-MIG-012-02 | ubiquitous | Supervisor FLEET_STATE shall reflect accurate agent count |
| CAP-MIG-012-03 | ubiquitous | Supervisor FLEET_STATE shall reflect accurate portfolio tracking |
| CAP-MIG-012-04 | conditional | IF fleet version mismatch THEN wake-up shall display both supervisor and fleet versions |
| CAP-MIG-012-05 | event-driven | WHEN fleet migration completes, the SYSTEM shall update supervisor fleet inventory |

**Rationale**: L402 revealed supervisor showed 28 agents while actual count was 29, and portfolio tracking (3 vs 5) was inconsistent. Fleet state must be synchronized during supervisor migration.

**Enforcement**: `validate_supervisor_fleet_state.py` (to be created), behavioral validation.

#### Fleet Migration Phases

```
PILOT (1-3 agents)
├── Select diverse archetypes
├── Migrate with full validation
├── Capture learnings
└── Improve scripts
        │
        ▼ [GO if all pilots pass]
EXPAND (50% of fleet)
├── Apply improved scripts
├── Parallel execution if safe
├── Capture additional learnings
└── Prepare for completion
        │
        ▼ [GO if no regressions]
COMPLETE (remaining agents)
├── Batch execution
├── Final validation
└── Fleet-wide verification
```

### CAP-MIG-013: knowledge/ Directory Guidance (L403)

The SYSTEM shall ensure knowledge/ directories have population guidance.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-013-01 | ubiquitous | Templates shall include `knowledge/README.md` with L296 Portability Test |
| CAP-MIG-013-02 | conditional | IF Instance_Migration AND knowledge/README.md not exists THEN the SYSTEM shall create it |
| CAP-MIG-013-03 | ubiquitous | knowledge/README.md shall reference L296 for content routing (portable vs domain-specific) |
| CAP-MIG-013-04 | prohibited | Migration shall NOT overwrite existing knowledge/README.md content |
| CAP-MIG-013-05 | conditional | IF existing knowledge/ content exists THEN L296 guidance is additive, not disruptive |

**Rationale**: L403 revealed that github-aget successfully articulated knowledge/ guidelines because it had pre-existing documentation. Templates only had `.gitkeep`, leaving agents without guidance. The L296 Portability Test provides clear routing: "Clone to different domain. Still useful?" YES→.aget/evolution/, NO→knowledge/.

**Enforcement**:
- Templates: `knowledge/README.md` included in all 6 templates
- Migration: `migrate_instance_to_v3.py` creates README if missing
- Validation: Check `knowledge/README.md` exists and contains L296 reference

#### L296 Portability Test Summary

```
┌────────────────────────────────────────────────────────────┐
│                  L296 PORTABILITY TEST                      │
│                                                             │
│  "Clone this agent to a different domain/company.          │
│   Would this content still be useful?"                      │
│                                                             │
│   ┌─────────┐                     ┌──────────────┐         │
│   │   YES   │ ──────────────────> │ .aget/       │         │
│   │         │                     │ evolution/   │         │
│   │ Portable│                     │ (framework)  │         │
│   └─────────┘                     └──────────────┘         │
│                                                             │
│   ┌─────────┐                     ┌──────────────┐         │
│   │   NO    │ ──────────────────> │ knowledge/   │         │
│   │         │                     │ (domain)     │         │
│   │ Domain  │                     │              │         │
│   └─────────┘                     └──────────────┘         │
└────────────────────────────────────────────────────────────┘
```

### CAP-MIG-014: Legacy File Handling (L376)

The SYSTEM shall detect and handle legacy version-bearing files during migration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-014-01 | conditional | IF migration creates new version-bearing file THEN the SYSTEM shall detect legacy equivalents |
| CAP-MIG-014-02 | conditional | IF legacy version-bearing file exists THEN the SYSTEM shall archive it before removal |
| CAP-MIG-014-03 | conditional | IF legacy file removed THEN the SYSTEM shall log the action |
| CAP-MIG-014-04 | prohibited | Migration shall NOT leave stale version files that cause contract test failures |
| CAP-MIG-014-05 | ubiquitous | Archive location shall be `.aget/archive/legacy_v3_migration/` |

**Rationale**: L376 (supervisor) identified that `migrate_instance_to_v3.py` created `manifest.yaml` but left legacy `.aget/collaboration/agent_manifest.yaml` with stale version, causing contract test failures in 3/25 agents.

**Known Legacy Files**:
| New File | Legacy File | Action |
|----------|-------------|--------|
| `manifest.yaml` | `.aget/collaboration/agent_manifest.yaml` | Archive + Remove |

**Enforcement**:
- Migration: `migrate_instance_to_v3.py` Gate 5.5 handles legacy files
- Validation: Contract tests detect version mismatches
- Audit: `find .aget -name "*manifest*.yaml"` post-migration

### CAP-MIG-015: Behavioral Validation Requirement (L376, L402)

The SYSTEM shall require behavioral validation, not just structural checks.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-MIG-015-01 | ubiquitous | Post-migration validation shall include contract test execution |
| CAP-MIG-015-02 | ubiquitous | Validation shall verify no stale version files exist |
| CAP-MIG-015-03 | conditional | IF Fleet_Migration THEN minimum 3 agents shall have contract tests executed |
| CAP-MIG-015-04 | prohibited | Structural validation alone is NOT sufficient for migration completion |
| CAP-MIG-015-05 | ubiquitous | Migration scripts shall output next-step commands including validation paths |

**Rationale**: L402 and L376 revealed a recurring pattern: structural checks pass (24/24) but behavioral issues remain undetected. Root cause: "Assumed structural = complete migration."

**Validation Matrix**:
| Check Type | Example | Required |
|------------|---------|----------|
| Structural | `[ -d .aget/persona ]` | YES |
| Version | `jq .aget_version version.json` | YES |
| Contract | `pytest tests/test_identity_contract.py` | **YES** |
| Behavioral | `python3 wake_up.py` | YES |
| Legacy Audit | `find .aget -name "*manifest*"` | YES |

**Enforcement**:
- Migration: Script outputs validation commands with correct paths
- Gate 4.1: Must include contract test execution (not just structural)
- PROJECT_PLAN: Template must include behavioral validation gate

#### Validation Path Reference (CAP-MIG-016)

```
┌────────────────────────────────────────────────────────────────┐
│                    AGET TOOLING LOCATIONS                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ~/github/aget-framework/aget/                                  │
│  ├── scripts/                    <- Migration tools             │
│  │   └── migrate_instance_to_v3.py                             │
│  │                                                              │
│  └── validation/                 <- Validation tools            │
│      └── validate_template_instance.py                          │
│                                                                 │
│  Note: Validation is in validation/, NOT scripts/               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Authority Model

```yaml
authority:
  applies_to: "agents_performing_migrations"

  governed_by:
    spec: "AGET_MIGRATION_SPEC"
    owner: "private-aget-framework-AGET"

  agent_authority:
    can_autonomously:
      - "run Analyze_Phase"
      - "create migration plan draft"
      - "execute --dry-run"
      - "run validators"

    requires_approval:
      - action: "execute migration"
        approver: "user"
      - action: "fleet migration"
        approver: "supervisor"
      - action: "cleanup archives"
        approver: "user"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-MIG-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT execute migration WITHOUT Archive preservation"
      rationale: "Rollback capability is required"

    - id: "INV-MIG-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT proceed to Cleanup_Phase with validation failures"
      rationale: "Blocking gate semantics"

    - id: "INV-MIG-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT delete User_Content during migration"
      rationale: "Portability requirement (CAP-PORT-001)"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/archive/"
      purpose: "Archive holding during verification period"
      created_by: "Execute_Phase"
      removed_by: "Cleanup_Phase"

    - path: ".aget/archive/_legacy_dirs/"
      purpose: "Archived directories"

    - path: ".aget/archive/_legacy_files/"
      purpose: "Archived files"

  required_files:
    - path: ".aget/archive/_archive_manifest.json"
      purpose: "Migration record and rollback reference"
      created_by: "Execute_Phase"

  scripts:
    - path: "aget/scripts/analyze_template_compliance.py"
      purpose: "Phase 1: Analyze (templates)"

    - path: "aget/scripts/migrate_template_to_v3.py"
      purpose: "Phase 3: Execute (templates)"

    - path: "aget/scripts/migrate_instance_to_v3.py"
      purpose: "Phase 3: Execute (instances)"
      features:
        - "12 archetypes supported"
        - "5D directory creation"
        - "identity.json generation"
        - "AGENTS.md @aget-version sync (CAP-MIG-010)"
      validated: "impact-aget, supervisor-AGET (24/24 each)"

    - path: "aget/scripts/cleanup_template_archive.py"
      purpose: "Phase 5: Cleanup"

    - path: "aget/scripts/rollback_migration.py"
      purpose: "Rollback support"
      status: "to be created"
```

---

## Migration Capability Contract

Agents performing migrations MUST satisfy:

```yaml
contracts:
  - name: analyze_before_execute
    assertion: phase_order
    rule: "Analyze_Phase completes before Execute_Phase"

  - name: archive_before_delete
    assertion: action_order
    rule: "Archive action precedes Delete action"

  - name: validate_before_cleanup
    assertion: gate_blocking
    rule: "Validate_Phase must GO before Cleanup_Phase"

  - name: manifest_exists
    assertion: file_exists
    path: ".aget/archive/_archive_manifest.json"
    when: "after Execute_Phase"

  - name: rollback_documented
    assertion: manifest_contains
    field: "rollback_command"
    when: "after Execute_Phase"
```

---

## Theoretical Basis

Migration architecture is grounded in established theories:

| Theory | Application |
|--------|-------------|
| **Defense in Depth** | Multiple validation gates prevent incomplete migrations |
| **Fail-Safe Design** | Archive preservation enables recovery |
| **Staged Rollout** | Pilot → Expand → Complete reduces fleet risk |
| **Automation Theory** | Scripts reduce human error in repetitive operations |

```yaml
theoretical_basis:
  primary: "Defense in Depth"
  secondary:
    - "Fail-Safe Design"
    - "Staged Rollout"
    - "Automation Theory"
  rationale: >
    Migration specification treats version transitions as critical operations
    requiring multiple safety layers. Archive preservation (Fail-Safe) enables
    rollback. Validation gates (Defense in Depth) catch issues before propagation.
    Pilot phases (Staged Rollout) limit blast radius. Automation reduces error.
  references:
    - "L392_pilot_driven_migration_automation.md"
    - "L394_design_by_fleet_exploration.md"
    - "PATTERN_migration_validation_gate.md"
```

---

## Validation

```bash
# Analyze compliance
python3 aget/scripts/analyze_template_compliance.py template-example-aget/

# Dry run migration
python3 aget/scripts/migrate_template_to_v3.py template-example-aget/ --dry-run

# Execute migration
python3 aget/scripts/migrate_template_to_v3.py template-example-aget/ --execute

# Run validators
python3 validation/validate_version_consistency.py template-example-aget/
python3 validation/validate_template_manifest.py template-example-aget/manifest.yaml

# Cleanup (after verification period)
python3 aget/scripts/cleanup_template_archive.py template-example-aget/ --execute
```

---

## References

- L392: Pilot-Driven Migration Automation
- L394: Design by Fleet Exploration
- L395: Instance v3.0 Migration Pattern
- L400: Conceptual vs Structural Migration Understanding
- L401: AGENTS.md Version Tag Synchronization (CAP-MIG-010)
- L402: Behavioral Validation Gaps (CAP-MIG-006-03, CAP-MIG-011, CAP-MIG-012)
- L403: knowledge/ Directory Population Guidance Gap (CAP-MIG-013)
- L376: Legacy File Version Sync (CAP-MIG-014, supervisor)
- L402: Behavioral Validation Gaps (CAP-MIG-015)
- PATTERN_migration_validation_gate.md
- AGET_TEMPLATE_SPEC.md (target spec)
- AGET_INSTANCE_SPEC.md (instance requirements)
- AGET_PORTABILITY_SPEC.md (content preservation)
- AGET_COMPATIBILITY_SPEC.md (version compatibility)

---

## Graduation History

```yaml
graduation:
  source_patterns:
    - "migrate_template_to_v3.py"
    - "analyze_template_compliance.py"
    - "cleanup_template_archive.py"
  source_learnings:
    - "L392"
    - "L394"
  trigger: "Gap C3 in GAP_ANALYSIS_v3.0_fleet_exploration.md"
  rationale: "Ad-hoc migration scripts formalized into specification"
```

---

*AGET Migration Specification v1.4.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Lifecycle Management - Gap C3*
*Enhanced: CAP-MIG-014 (legacy handling), CAP-MIG-015 (behavioral validation)*
*"Controlled transitions enable safe evolution."*
