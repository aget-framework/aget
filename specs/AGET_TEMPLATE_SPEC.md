# AGET TEMPLATE Specification

**Version**: 3.4.0
**Status**: Active
**Category**: Standards (Template Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2026-02-14
**Author**: aget-framework
**Location**: `aget/specs/AGET_TEMPLATE_SPEC.md`
**Change Proposal**: CP-017, CP-018
**Change Origin**: L394 (Design by Fleet Exploration)
**Supersedes**: WORKER_TEMPLATE_SPEC_v1.0.yaml, TEMPLATE_STRUCTURE_GUIDE.md

---

## Abstract

This specification defines the AGET template architecture for v3.0. Templates are reusable agent patterns that provide 5D Composition structure (PERSONA, MEMORY, REASONING, SKILLS, CONTEXT), directory layouts, and manifest schemas for creating consistent agents.

## Motivation

The v2.x template system lacked:
- Explicit 5D dimension configuration
- Component reuse mechanism
- A-SDLC phase mapping
- Clear manifest schema versioning

v3.0 templates address these gaps by providing:
- Dimension-specific directories for each of the 5D aspects
- Component reference syntax for reusable configurations
- Phase-to-template mapping for A-SDLC coverage
- Schema-validated manifests

## Scope

**Applies to**: All AGET templates and agent instances.

**Defines**:
- v3.0 directory structure
- Manifest v3 schema
- Component reference mechanism
- Template inheritance model
- A-SDLC phase coverage

---

## Vocabulary

Domain terms for the TEMPLATE specification:

```yaml
vocabulary:
  meta:
    domain: "template"
    version: "1.0.0"
    inherits: "aget_core"

  persona:  # D1: WHO
    Template:
      skos:definition: "Reusable agent pattern defining 5D composition structure"
      skos:narrower: ["Base_Template", "Derived_Template"]
    Base_Template:
      skos:definition: "Foundation template with complete 5D structure"
      skos:example: "template-worker-aget"
    Derived_Template:
      skos:definition: "Template extending another template's capabilities"
      skos:broader: "Template"
    Archetype:
      skos:definition: "Classification of agent role and authority level"
      skos:narrower: ["Worker", "Advisor", "Supervisor", "Developer", "Consultant", "Spec_Engineer", "Executive", "Analyst", "Reviewer", "Operator", "Architect", "Researcher"]

  memory:  # D2: WHAT KNOWS
    Manifest_Yaml:
      skos:definition: "Template manifest file declaring composition structure"
      aget:location: "manifest.yaml"
    Version_Json:
      skos:definition: "Agent version and identity file"
      aget:location: ".aget/version.json"
    Identity_Json:
      skos:definition: "Agent North Star and purpose"
      aget:location: ".aget/identity.json"
    Component:
      skos:definition: "Reusable configuration element that can be referenced"
      aget:location: "aget/components/"

  reasoning:  # D3: HOW THINKS
    Template_Inheritance:
      skos:definition: "Mechanism by which derived templates extend base templates"
    Component_Reference:
      skos:definition: "Syntax for including reusable components in manifests"
      skos:notation: "$ref: path/to/component.yaml"
    Override_Rule:
      skos:definition: "Policy governing what derived templates can change"

  skills:  # D4: WHAT DOES
    A_SDLC_Phase:
      skos:definition: "Agent Software Development Lifecycle phase"
      skos:narrower: ["Phase_0", "Phase_1", "Phase_2", "Phase_3", "Phase_4", "Phase_5", "Phase_6"]
    Template_Capability:
      skos:definition: "Specific functionality provided by a template"

  context:  # D5: WHERE/WHEN
    Template_Directory:
      skos:definition: "Root directory containing template files"
      skos:notation: "template-{type}-aget/"
    Instance_Directory:
      skos:definition: "Root directory containing agent instance files"
      skos:notation: "{visibility}-{name}-{type}/"
```

---

## Requirements

### CAP-TPL-001: Template Directory Structure

The SYSTEM shall maintain v3.0 Template_Directory structure.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-001-01 | ubiquitous | The SYSTEM shall organize Template_Directory according to v3.0 layout |
| CAP-TPL-001-02 | ubiquitous | The SYSTEM shall include .aget/ as root configuration directory |
| CAP-TPL-001-03 | ubiquitous | The SYSTEM shall include governance/ for governance artifacts |
| CAP-TPL-001-04 | ubiquitous | The SYSTEM shall include 5D dimension directories under .aget/ |

**Enforcement**: `validate_template_manifest.py`, `validate_5d_compliance.py`

#### v3.1 Directory Layout

```
template-{type}-aget/
│
├── .aget/                          # FRAMEWORK CONFIGURATION (Apache 2.0)
│   ├── version.json                # Agent version + template reference
│   ├── identity.json               # North Star (D1: PERSONA)
│   │
│   ├── persona/                    # D1: PERSONA dimension (config)
│   │   ├── archetype.yaml          # Selected archetype configuration
│   │   └── style.yaml              # Communication style settings
│   │
│   ├── memory/                     # D2: MEMORY dimension (CONFIG ONLY)
│   │   ├── layer_config.yaml       # 6-layer configuration
│   │   ├── inheritance.yaml        # Inheritance rules
│   │   └── retrieval.yaml          # Context loading rules
│   │   # NOTE: NO content subdirs (domain/, experiential/)
│   │   #       Content goes to visible knowledge/ directory
│   │
│   ├── reasoning/                  # D3: REASONING dimension (config)
│   │   ├── decision_authority.yaml # Decision authority matrix
│   │   └── planning_patterns.yaml  # Planning approach configuration
│   │
│   ├── skills/                     # D4: SKILLS dimension (config)
│   │   ├── capabilities.yaml       # Declared capabilities
│   │   └── phase_mapping.yaml      # A-SDLC phase assignments
│   │
│   ├── context/                    # D5: CONTEXT dimension (config)
│   │   ├── relationships.yaml      # Agent relationships
│   │   └── scope.yaml              # Operational scope
│   │
│   ├── D6_*/                       # D6+ extensions (optional)
│   │   └── *.yaml                  # Complex agents extend here
│   │
│   ├── patterns/                   # Operational patterns (scripts)
│   │   ├── session/
│   │   ├── release/
│   │   └── sync/
│   │
│   ├── evolution/                  # L-docs (PORTABLE EXCEPTION)
│   │   ├── index.json              # L-doc index for scaling
│   │   └── L*.md
│   │
│   └── state/                      # Operational state (optional)
│       └── *.json                  # Compliance, checkpoints, etc.
│
├── governance/                     # VISIBLE: Governance artifacts (core)
│   ├── CHARTER.md                  # Agent charter
│   ├── MISSION.md                  # Mission statement
│   └── SCOPE_BOUNDARIES.md         # Operational boundaries
│
├── sessions/                       # VISIBLE: Session notes (core)
│   └── SESSION_*.md
│
├── planning/                       # VISIBLE: Planning artifacts (core)
│   └── PROJECT_PLAN_*.md
│
├── knowledge/                      # VISIBLE: Domain knowledge (core)
│   ├── domain/                     # Domain-specific knowledge
│   └── research/                   # Research findings
│
├── tests/                          # Contract tests
│   └── test_contract.py
│
├── manifest.yaml                   # Template manifest (v3 schema)
├── CLAUDE.md                       # CLI configuration (symlink)
├── AGENTS.md                       # Agent behavior specification
├── README.md                       # Public documentation
└── CHANGELOG.md                    # Version history
```

### CAP-TPL-002: 5D Dimension Directories

The SYSTEM shall maintain dimension directories for 5D Composition.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-002-01 | ubiquitous | The SYSTEM shall create .aget/persona/ for PERSONA dimension |
| CAP-TPL-002-02 | ubiquitous | The SYSTEM shall create .aget/memory/ for MEMORY dimension |
| CAP-TPL-002-03 | ubiquitous | The SYSTEM shall create .aget/reasoning/ for REASONING dimension |
| CAP-TPL-002-04 | ubiquitous | The SYSTEM shall create .aget/skills/ for SKILLS dimension |
| CAP-TPL-002-05 | ubiquitous | The SYSTEM shall create .aget/context/ for CONTEXT dimension |

**Enforcement**: `validate_5d_compliance.py`

### CAP-TPL-003: Manifest Schema v3

The SYSTEM shall validate Manifest_Yaml against Schema v3.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-003-01 | ubiquitous | The SYSTEM shall require manifest_version: "3.0" in Manifest_Yaml |
| CAP-TPL-003-02 | ubiquitous | The SYSTEM shall require template metadata section |
| CAP-TPL-003-03 | ubiquitous | The SYSTEM shall require composition section with 5D references |
| CAP-TPL-003-04 | ubiquitous | The SYSTEM shall require capabilities section |
| CAP-TPL-003-05 | optional | WHERE Component_Reference is used, the SYSTEM shall resolve reference path |

**Enforcement**: `validate_template_manifest.py`

#### Manifest v3 Schema

```yaml
# manifest.yaml - Template Manifest v3.0

# Required: Manifest version
manifest_version: "3.0"

# Required: Template metadata
template:
  name: "template-{type}-aget"
  archetype: "Worker"              # Worker | Advisor | Supervisor | etc.
  description: "Brief description"
  version: "3.0.0"
  created: "2025-12-27"
  author: "author-agent"
  inherits_from: null              # null for base templates

# Required: 5D Composition
composition:
  persona:
    archetype: $ref: .aget/persona/archetype.yaml
    style: $ref: .aget/persona/style.yaml
    governance: capability-governance-balanced

  memory:
    structure: $ref: .aget/memory/
    inheritance: ["domain", "organizational"]

  reasoning:
    decision_authority: $ref: .aget/reasoning/decision_authority.yaml
    planning: $ref: .aget/reasoning/planning_patterns.yaml

  skills:
    capabilities: $ref: .aget/skills/capabilities.yaml
    phases: $ref: .aget/skills/phase_mapping.yaml

  context:
    relationships: $ref: .aget/context/relationships.yaml
    scope: $ref: .aget/context/scope.yaml

# Required: Capability declarations
capabilities:
  - capability-governance-balanced
  - capability-session-protocols
  - capability-evolution-tracking

# Optional: A-SDLC phase mapping
asdlc_phases:
  primary: [3]                     # Primary phases
  secondary: [6]                   # Secondary phases

# Optional: Inviolables
inviolables:
  inherited: []
  agent_specific: []

# Optional: Entity inheritance (L459)
entities:
  inherits:                          # Core entities to inherit
    - Person
    - Organization
    - Document
  extends:                           # Domain-specific extensions
    Person:
      attributes:
        - custom_field: {type: string}

# Optional: Contract tests
contract_tests:
  required:
    - test_version_json_required_fields
    - test_claude_md_is_symlink
  recommended:
    - test_5d_compliance
```

### CAP-TPL-004: Component Reference Mechanism

The SYSTEM shall support Component_Reference syntax for composition reuse.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-004-01 | ubiquitous | The SYSTEM shall interpret $ref: prefix as Component_Reference |
| CAP-TPL-004-02 | ubiquitous | The SYSTEM shall resolve relative paths from manifest location |
| CAP-TPL-004-03 | ubiquitous | The SYSTEM shall resolve aget: prefix paths from framework components |
| CAP-TPL-004-04 | conditional | IF Component_Reference cannot be resolved THEN the SYSTEM shall report error |

**Enforcement**: `validate_composition_refs.py`

#### Component Reference Syntax

```yaml
# Local reference (relative to manifest)
persona:
  archetype: $ref: .aget/persona/archetype.yaml

# Framework component reference
persona:
  archetype: $ref: aget:components/persona/archetype_balanced.yaml

# Inline override (no reference)
persona:
  archetype:
    type: "Worker"
    authority_level: "base"
```

### CAP-TPL-005: Template Inheritance

The SYSTEM shall support Template_Inheritance.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-005-01 | optional | WHERE inherits_from is specified, the SYSTEM shall load parent template |
| CAP-TPL-005-02 | ubiquitous | The SYSTEM shall merge child composition over parent composition |
| CAP-TPL-005-03 | ubiquitous | The SYSTEM shall preserve parent Inviolables (cannot be removed) |
| CAP-TPL-005-04 | ubiquitous | The SYSTEM shall allow child to add new capabilities |
| CAP-TPL-005-05 | conditional | IF child removes parent capability THEN the SYSTEM shall report error |

**Enforcement**: `validate_composition.py`

#### Inheritance Hierarchy

```
template-worker-aget (base)
    ├── template-advisor-aget
    │   ├── template-executive-aget
    │   ├── template-analyst-aget
    │   └── template-researcher-aget
    ├── template-supervisor-aget
    ├── template-developer-aget
    │   └── template-architect-aget
    ├── template-consultant-aget
    │   └── template-reviewer-aget
    └── template-spec-engineer-aget
         └── template-operator-aget
```

### CAP-TPL-006: Required Files

The SYSTEM shall maintain required Template files.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-006-01 | ubiquitous | The SYSTEM shall maintain .aget/version.json with required fields |
| CAP-TPL-006-02 | ubiquitous | The SYSTEM shall maintain .aget/identity.json with North_Star |
| CAP-TPL-006-03 | ubiquitous | The SYSTEM shall maintain AGENTS.md as behavior specification |
| CAP-TPL-006-04 | ubiquitous | The SYSTEM shall maintain CLAUDE.md as symlink to AGENTS.md |
| CAP-TPL-006-05 | ubiquitous | The SYSTEM shall maintain manifest.yaml with v3 schema |
| CAP-TPL-006-06 | ubiquitous | The SYSTEM shall maintain governance/CHARTER.md |
| CAP-TPL-006-07 | ubiquitous | The SYSTEM shall maintain governance/MISSION.md |

**Enforcement**: `validate_5d_compliance.py`

#### version.json Schema

```json
{
  "aget_version": "3.0.0",
  "manifest_version": "3.0",
  "created": "2025-12-27",
  "updated": "2025-12-27",
  "template": "worker",
  "agent_name": "template-worker-aget",
  "instance_type": "template",
  "domain": "worker-template",
  "portfolio": null,
  "managed_by": "none",
  "capabilities": [
    "capability-governance-balanced",
    "capability-session-protocols"
  ]
}
```

#### identity.json Schema

```json
{
  "north_star": "Enable consistent, composable agent creation through reusable templates",
  "purpose": "Provide foundation for all agent instances",
  "created": "2025-12-27"
}
```

### CAP-TPL-007: A-SDLC Phase Mapping

The SYSTEM shall map Templates to A_SDLC_Phase.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-007-01 | ubiquitous | The SYSTEM shall declare primary A_SDLC_Phase in asdlc_phases.primary |
| CAP-TPL-007-02 | optional | WHERE secondary phases exist, the SYSTEM shall declare in asdlc_phases.secondary |
| CAP-TPL-007-03 | ubiquitous | The SYSTEM shall ensure all 7 A-SDLC phases have at least one primary template |

**Enforcement**: A-SDLC coverage validation

#### A-SDLC Phase Coverage Matrix

| Phase | Name | Primary Template | Secondary Templates |
|-------|------|------------------|---------------------|
| 0 | Discovery | researcher, executive | analyst |
| 1 | Specification | spec-engineer | analyst |
| 2 | Design | architect | developer |
| 3 | Implementation | developer | worker |
| 4 | Validation | reviewer | analyst |
| 5 | Deployment | operator | worker |
| 6 | Maintenance | developer, operator | worker |

### CAP-TPL-008: Configuration Size Limits

The SYSTEM shall enforce Configuration_Size_Limit.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-008-01 | ubiquitous | The SYSTEM shall limit AGENTS.md to 40000 characters |
| CAP-TPL-008-02 | conditional | IF AGENTS.md exceeds 35000 characters THEN the SYSTEM shall emit Size_Warning |
| CAP-TPL-008-03 | ubiquitous | The SYSTEM shall limit version.json to 2000 characters |

**Enforcement**: `validate_template_manifest.py`

### CAP-TPL-009: Contract Tests

The SYSTEM shall include Contract_Tests for Template validation.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-009-01 | ubiquitous | The SYSTEM shall include tests/ directory |
| CAP-TPL-009-02 | ubiquitous | The SYSTEM shall implement required contract tests |
| CAP-TPL-009-03 | event-driven | WHEN pytest is run, the SYSTEM shall pass all required tests |

**Enforcement**: `pytest tests/`

#### Required Contract Tests

| Test | Purpose |
|------|---------|
| test_version_json_required_fields | Validates version.json schema |
| test_claude_md_is_symlink | Verifies CLAUDE.md → AGENTS.md |
| test_manifest_v3_schema | Validates manifest.yaml v3 |
| test_5d_directories_exist | Verifies 5D directory structure |
| test_governance_files_exist | Validates governance/ contents |

### CAP-TPL-010: Visible Directory Standards

The SYSTEM shall maintain visible directories for Portable_Content.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-010-01 | ubiquitous | The SYSTEM shall include governance/ as core visible directory |
| CAP-TPL-010-02 | ubiquitous | The SYSTEM shall include sessions/ as core visible directory |
| CAP-TPL-010-03 | ubiquitous | The SYSTEM shall include planning/ as core visible directory |
| CAP-TPL-010-04 | ubiquitous | The SYSTEM shall include knowledge/ as core visible directory |
| CAP-TPL-010-05 | conditional | IF archetype extends Developer THEN the SYSTEM shall include products/, workspace/, src/ |
| CAP-TPL-010-06 | conditional | IF archetype extends Advisor THEN the SYSTEM shall include clients/, engagements/ |
| CAP-TPL-010-07 | conditional | IF archetype extends Supervisor THEN the SYSTEM shall include sops/ |
| CAP-TPL-010-08 | ubiquitous | The SYSTEM shall NOT place user content in hidden directories (except .aget/evolution/) |

**Enforcement**: `validate_5d_compliance.py`, directory structure validation

**Rationale**: Fleet exploration (L394) revealed 18+ visible directories in real instances. This formalizes a layered approach: core set + archetype extensions.

#### Visible Directory Matrix

| Directory | Purpose | Core/Extension | Inherits From |
|-----------|---------|----------------|---------------|
| governance/ | Charter, Mission, Scope | Core | - |
| sessions/ | Session notes | Core | - |
| planning/ | Project plans, decisions | Core | - |
| knowledge/ | Domain knowledge, research | Core | - |
| products/ | Deliverables | Extension | Developer |
| workspace/ | Work in progress | Extension | Developer |
| src/ | Source code | Extension | Developer |
| docs/ | Documentation | Extension | Worker |
| data/ | Persistent data | Extension | Worker |
| decisions/ | ADRs | Extension | Architect |
| reports/ | Research outputs | Extension | Analyst |
| sops/ | Operating procedures | Extension | Supervisor |
| clients/ | Client relationships | Extension | Advisor |
| engagements/ | Engagement tracking | Extension | Advisor |

### CAP-TPL-011: Directory Inheritance

The SYSTEM shall support directory inheritance from parent templates.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-011-01 | optional | WHERE inherits_from is specified, the SYSTEM shall inherit parent visible directories |
| CAP-TPL-011-02 | ubiquitous | The SYSTEM shall allow child to add new visible directories |
| CAP-TPL-011-03 | conditional | IF child removes inherited directory THEN the SYSTEM shall emit warning |
| CAP-TPL-011-04 | ubiquitous | The SYSTEM shall document directory inheritance in manifest.yaml |

**Enforcement**: `validate_composition.py`

#### Directory Inheritance Example

```yaml
# template-architect-aget/manifest.yaml
template:
  inherits_from: template-developer-aget

visible_directories:
  inherited:                    # From developer
    - governance/
    - sessions/
    - planning/
    - knowledge/
    - products/
    - workspace/
    - src/
  added:                        # Architect-specific
    - decisions/               # ADRs
  removed: []                   # None (removal emits warning)
```

### CAP-TPL-012: Entity Inheritance (L459)

The SYSTEM shall support Core_Entity inheritance from AGET_VOCABULARY_SPEC Part 6.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-012-01 | optional | WHERE entities.inherits is specified, the SYSTEM shall inherit Core_Entity definitions |
| CAP-TPL-012-02 | ubiquitous | The SYSTEM shall include all base attributes from inherited Core_Entity |
| CAP-TPL-012-03 | optional | WHERE entities.extends is specified, the SYSTEM shall add domain-specific attributes |
| CAP-TPL-012-04 | ubiquitous | The SYSTEM shall NOT remove inherited Core_Entity attributes |
| CAP-TPL-012-05 | conditional | IF extended attribute narrows type THEN the SYSTEM shall allow (string → enum) |
| CAP-TPL-012-06 | conditional | IF extended attribute widens type THEN the SYSTEM shall report error |

**Enforcement**: `validate_entity_inheritance.py`

#### Entity Inheritance Rules (R-ENT-*)

| Rule ID | Rule | Description |
|---------|------|-------------|
| R-ENT-001 | Inherited entities include all base attributes | Cannot remove base attributes |
| R-ENT-002 | Extensions add attributes, cannot remove | Additive only |
| R-ENT-003 | Extensions can add relationships | New connections allowed |
| R-ENT-004 | Extensions can narrow types | string → enum allowed, not vice versa |
| R-ENT-005 | Extended entities remain compatible | Consumers of base can consume extended |

#### Entity Inheritance Example

```yaml
# In manifest.yaml
entities:
  inherits:
    - Person                     # From AGET_VOCABULARY_SPEC Part 6
    - Organization
    - Document

  extends:
    Person:
      attributes:
        - bar_number:            # Domain-specific attribute
            type: string
            description: "State bar license number"
        - jurisdiction:
            type: string
            description: "Licensing jurisdiction"
    Document:
      attributes:
        - confidentiality:
            type: enum
            values: [public, confidential, privileged]
      relationships:
        - subject_of:
            target: Legal_Matter
            cardinality: "0:many"
```

**Reference**: L459 (Core Entity Vocabulary Vision), AGET_VOCABULARY_SPEC Part 6

### CAP-TPL-013: Evolution Entry Types (L461)

The SYSTEM shall use standardized entry types in `.aget/evolution/` directory.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-013-01 | ubiquitous | The SYSTEM shall use L-prefix for Learning entries (L{NNN}_{title}.md) |
| CAP-TPL-013-02 | ubiquitous | The SYSTEM shall use D-prefix for Decision entries (D{NNN}_{title}.md) |
| CAP-TPL-013-03 | ubiquitous | The SYSTEM shall use DISC-prefix for Discovery entries (DISC{NNN}_{title}.md) |
| CAP-TPL-013-04 | ubiquitous | The SYSTEM shall use flat file structure (not subdirectories) for evolution entries |
| CAP-TPL-013-05 | ubiquitous | The SYSTEM shall place PROJECT_PLAN files in planning/, NOT in .aget/evolution/ |
| CAP-TPL-013-06 | optional | WHERE index.json exists, the SYSTEM shall maintain evolution entry metadata |

**Enforcement**: `validate_content_placement.py`

**Rationale**: L460 (Directory Semantics Reconciliation Gap) and L461 (Evolution Entry Type Standardization) established that evolution entries use flat files with prefixes (L/D/DISC), and PROJECT_PLANs belong in planning/ (prospective) not evolution/ (retrospective).

#### Evolution Entry Types

| Prefix | Type | Purpose | Temporal Orientation |
|--------|------|---------|---------------------|
| L | Learning | Lessons learned, patterns discovered | Retrospective |
| D | Decision | Architectural/strategic decisions | Retrospective |
| DISC | Discovery | Unexpected findings, emergent behaviors | Retrospective |

#### Content Placement Rules

| Content Type | Correct Location | Incorrect Location |
|--------------|------------------|-------------------|
| L-docs | `.aget/evolution/` | - |
| D-docs | `.aget/evolution/` | - |
| DISC-docs | `.aget/evolution/` | - |
| PROJECT_PLANs | `planning/` | `.aget/evolution/` |
| SOPs | `sops/` | `.aget/evolution/` |
| Session notes | `sessions/` | `.aget/evolution/` |

**Reference**: L460, L461, AGET_EVOLUTION_SPEC.md

### CAP-TPL-014: Shell Integration (v3.3.0)

The SYSTEM shall include shell integration for template portability.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-014-01 | ubiquitous | The SYSTEM shall include shell/ directory in each template |
| CAP-TPL-014-02 | ubiquitous | The SYSTEM shall include {type}_profile.zsh in shell/ |
| CAP-TPL-014-03 | ubiquitous | The SYSTEM shall include README.md in shell/ |
| CAP-TPL-014-04 | ubiquitous | The SYSTEM shall document paths to Spec, Vocabulary, Config in profile header |
| CAP-TPL-014-05 | ubiquitous | The SYSTEM shall include aget_info() function in profile |
| CAP-TPL-014-06 | ubiquitous | The SYSTEM shall include aget_docs() function in profile |
| CAP-TPL-014-07 | ubiquitous | The SYSTEM shall use AGET_AGENT_DIR for path portability |

**Enforcement**: `validate_template_exemplar.py`

**Rationale**: Shell profiles enable consistent agent activation across installations. Well-documented profiles reduce onboarding friction and ensure users can locate related specifications and documentation.

#### Profile Structure Requirements

Each template profile SHALL include:

```zsh
# Header: Documentation paths
# DOCUMENTATION
# -------------
# Shell README:    ./shell/README.md
# Template Spec:   ./specs/{Type}_SPEC.md
# Template Vocab:  ./specs/{Type}_VOCABULARY.md
# Agent Config:    ./AGENTS.md

# Configuration: Portable paths
export AGET_AGENT_DIR="${AGET_AGENT_DIR:-...}"
export AGET_SPEC="${AGET_AGENT_DIR}/specs/{Type}_SPEC.md"
export AGET_VOCAB="${AGET_AGENT_DIR}/specs/{Type}_VOCABULARY.md"

# Functions: Discovery helpers
aget_info()   # Display all paths
aget_docs()   # Open documentation
```

**Reference**: L452 (Shell Orchestration Pattern), aget/shell/README.md

### CAP-TPL-015: Repository Issue Settings (L520)

The SYSTEM shall configure repository issue settings to prevent Issue_Fragmentation.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-015-01 | ubiquitous | Template repositories SHALL have GitHub issues DISABLED |
| CAP-TPL-015-02 | ubiquitous | Issues for template improvements SHALL be filed to central aget-framework/aget tracker |
| CAP-TPL-015-03 | event-driven | WHEN publishing a template, the SYSTEM SHALL verify hasIssuesEnabled is false |

**Enforcement**: `repo_settings_validator.py --check-issues`

**Rationale**: Issue_Fragmentation occurs when issues are scattered across individual template repos instead of the central tracker. This complicates issue discovery, cross-template coordination, and release planning. Per AGET_ISSUE_GOVERNANCE_SPEC, issues should flow to:
- Private agents → `gmelli/aget-aget`
- Public/remote agents → `aget-framework/aget`

#### Repository Issue Matrix

| Repository Pattern | Issues | Rationale |
|-------------------|--------|-----------|
| `aget-framework/aget` | enabled | Central public issue tracker |
| `aget-framework/.github` | disabled | Org config, not issue target |
| `aget-framework/template-*` | **disabled** | Code templates only |

#### Verification

```bash
# Verify template repos have issues disabled
gh repo list aget-framework --json name,hasIssuesEnabled --jq \
  '.[] | select(.name | startswith("template-")) | "\(.name): \(.hasIssuesEnabled)"'
# Expected: all show "false"
```

**Reference**: L520 (Issue Governance Gap), AGET_ISSUE_GOVERNANCE_SPEC (R-ISSUE-007)

---

### R-TEMPLATE-001: SOP Directory Scaffold (Issue #59)

The SYSTEM shall support operating procedure documentation in all templates.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TEMPLATE-001-01 | ubiquitous | The SYSTEM SHALL include sops/ directory in all templates |
| R-TEMPLATE-001-02 | ubiquitous | The sops/ directory SHALL contain at least one SOP_*.md file (L555: substance check) |
| R-TEMPLATE-001-03 | ubiquitous | WHERE sops/ is included, the SYSTEM SHALL include at least one SOP file |
| R-TEMPLATE-001-04 | ubiquitous | SOPs SHALL follow naming convention SOP_{name}.md |

**Enforcement**: `validate_template_structure.py`

**V-Test** (L555 substance-aware):
```bash
# R-TEMPLATE-001-02: Substance check (not just scaffold)
sop_count=$(find sops/ -name "SOP_*.md" 2>/dev/null | wc -l)
if [ "$sop_count" -lt 1 ]; then
  echo "FAIL: sops/ exists but contains no SOP_*.md files"
  exit 1
fi
echo "PASS: sops/ contains $sop_count SOP file(s)"
```

**Rationale**: Issue #59 identified that templates lack sops/ scaffold, requiring agents to create it manually. All agent archetypes benefit from capturing operational procedures, not just Supervisors. Adding sops/ to the core directory set ensures consistent SOP governance across the fleet.

**Minimum SOP Set:**

| SOP | Purpose | All Templates? |
|-----|---------|----------------|
| SOP_wind_down.md | Session finalization procedures | Optional |
| SOP_escalation.md | When and how to escalate | Recommended |
| SOP_release_process.md | Release procedures | Framework-owning |

**Directory Layout Update:**

```
template-{type}-aget/
├── ...
├── sops/                       # VISIBLE: Operating procedures (NEW - Issue #59)
│   ├── SOP_*.md               # Agent-specific SOPs
│   └── templates/             # SOP templates (optional)
├── sessions/
├── planning/
└── ...
```

**Origin**: Issue #59 (Missing sops/ scaffold in templates)

---

## 12 Templates Specification

### Base Templates (6 Existing)

| Template | Archetype | Governance | Primary Phases |
|----------|-----------|------------|----------------|
| template-worker-aget | Worker | Balanced | 3, 6 |
| template-advisor-aget | Advisor | Balanced | Cross-cutting |
| template-supervisor-aget | Supervisor | Rigorous | Cross-cutting |
| template-developer-aget | Developer | Balanced | 3, 6 |
| template-consultant-aget | Consultant | Balanced | Cross-cutting |
| template-spec-engineer-aget | Spec_Engineer | Balanced | 1 |

### New Templates (6 New)

| Template | Archetype | Governance | Primary Phases | Extends |
|----------|-----------|------------|----------------|---------|
| template-executive-aget | Executive | Rigorous | 0 | advisor |
| template-analyst-aget | Analyst | Balanced | 0, 1, 4 | advisor |
| template-reviewer-aget | Reviewer | Balanced | 4 | consultant |
| template-operator-aget | Operator | Balanced | 5, 6 | worker |
| template-architect-aget | Architect | Balanced | 2 | developer |
| template-researcher-aget | Researcher | Exploratory | 0 | advisor |

---

## Authority Model

```yaml
authority:
  supervised_by: "aget-framework"
  supervision_type: "governance"

  can_autonomously:
    - "create agent instances from templates"
    - "extend templates with new capabilities"
    - "add agent-specific inviolables"

  requires_approval:
    - action: "modify base template structure"
      approver: "aget-framework"
    - action: "remove inherited capability"
      approver: "aget-framework (forbidden)"

  manages:
    - entity: "agent instances"
      authority: "full"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-TPL-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT remove inherited capabilities from derived templates"
    - id: "INV-TPL-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT weaken inherited inviolables"
    - id: "INV-TPL-003"
      source: "aget_framework"
      statement: "The SYSTEM shall maintain CLAUDE.md as symlink to AGENTS.md"
```

---

## Structural Requirements

```yaml
structure:
  # Framework Configuration (.aget/)
  required_framework_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration"
    - path: ".aget/persona/"
      purpose: "D1 PERSONA dimension configuration"
    - path: ".aget/memory/"
      purpose: "D2 MEMORY dimension configuration (NOT content)"
    - path: ".aget/reasoning/"
      purpose: "D3 REASONING dimension configuration"
    - path: ".aget/skills/"
      purpose: "D4 SKILLS dimension configuration"
    - path: ".aget/context/"
      purpose: "D5 CONTEXT dimension configuration"
    - path: ".aget/evolution/"
      purpose: "Learning documents (portable exception)"

  optional_framework_directories:
    - path: ".aget/D6_*/"
      purpose: "D6+ dimension extensions"
    - path: ".aget/state/"
      purpose: "Operational state"
    - path: ".aget/patterns/"
      purpose: "Pattern scripts"

  # Visible Content Directories (Portable_Content)
  required_visible_directories:
    - path: "governance/"
      purpose: "Charter, Mission, Scope (core)"
    - path: "sessions/"
      purpose: "Session notes (core)"
    - path: "planning/"
      purpose: "Project plans, decisions (core)"
    - path: "knowledge/"
      purpose: "Domain knowledge, research (core)"
    - path: "tests/"
      purpose: "Contract tests"

  archetype_extension_directories:
    developer:
      - path: "products/"
        purpose: "Deliverables"
      - path: "workspace/"
        purpose: "Work in progress"
      - path: "src/"
        purpose: "Source code"
    advisor:
      - path: "clients/"
        purpose: "Client relationships (.gitignore)"
      - path: "engagements/"
        purpose: "Engagement tracking (.gitignore)"
    supervisor:
      - path: "sops/"
        purpose: "Operating procedures"
    architect:
      - path: "decisions/"
        purpose: "Architecture Decision Records"
    analyst:
      - path: "reports/"
        purpose: "Research outputs"

  required_files:
    - path: ".aget/version.json"
      purpose: "Agent version and identity"
    - path: ".aget/identity.json"
      purpose: "North Star statement"
    - path: "manifest.yaml"
      purpose: "Template manifest v3"
    - path: "AGENTS.md"
      purpose: "Agent behavior specification"
    - path: "CLAUDE.md"
      purpose: "CLI configuration (symlink)"
    - path: "governance/CHARTER.md"
      purpose: "Agent charter"
    - path: "governance/MISSION.md"
      purpose: "Mission statement"
```

---

## Migration from v2.x

### Directory Changes

| v2.x | v3.0 | Notes |
|------|------|-------|
| `.aget/knowledge/` | `.aget/memory/` | Renamed for 5D consistency |
| (none) | `.aget/persona/` | New dimension directory |
| (none) | `.aget/reasoning/` | New dimension directory |
| (none) | `.aget/skills/` | New dimension directory |
| (none) | `.aget/context/` | New dimension directory |

### Manifest Changes

| v2.x | v3.0 |
|------|------|
| `capabilities:` list | `composition:` + `capabilities:` |
| (none) | `manifest_version: "3.0"` |
| (none) | `composition:` 5D structure |
| (none) | `asdlc_phases:` mapping |

### Migration Script

```bash
# Migrate template from v2.x to v3.0
python3 .aget/patterns/upgrade/migrate_template_v3.py --dir /path/to/template
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "5D Composition Architecture"
  secondary:
    - "BDI (Belief-Desire-Intention) for goal hierarchy"
    - "Actor Model for agent isolation"
    - "Component-Based Software Engineering"
  reference: "L330, L331, L335"
```

---

## Graduation History

```yaml
graduation:
  source_learnings:
    - "L171: Instance creation specification gap"
    - "L174: Template specification debt"
    - "L330: Capability Composition Architecture"
  pattern_origin: "WORKER_TEMPLATE_SPEC_v1.0.yaml"
  rationale: "Formalize 5D composition for v3.0 templates"
```

---

## Validation

### Validate Template

```bash
# Full 5D validation
python3 validation/validate_5d_compliance.py --dir /path/to/template

# Manifest validation
python3 validation/validate_template_manifest.py /path/to/template/manifest.yaml

# Component reference validation
python3 validation/validate_composition_refs.py --dir /path/to/template

# Contract tests
cd /path/to/template && pytest tests/ -v
```

---

### CAP-TPL-016: Archetype Customization (v3.5.0)

The SYSTEM shall support archetype-specific ontologies and skills.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-016-01 | ubiquitous | The SYSTEM shall include ontology/ directory in each template |
| CAP-TPL-016-02 | ubiquitous | The SYSTEM shall include ONTOLOGY_{archetype}.yaml in ontology/ |
| CAP-TPL-016-03 | ubiquitous | The SYSTEM shall include .claude/skills/ directory with AGET skills |
| CAP-TPL-016-04 | ubiquitous | The SYSTEM shall include 14 universal skills in all templates |
| CAP-TPL-016-05 | ubiquitous | The SYSTEM shall include archetype-specific skills per archetype |
| CAP-TPL-016-06 | conditional | IF SKILL.md exists THEN it shall have valid YAML frontmatter |

**Enforcement**: `validate_v3.5.0.py`, `validate_archetype_skills.py`

**Rationale**: v3.5.0 introduces archetype customization with specialized ontologies and skills per archetype. This enables archetype-appropriate capabilities while maintaining a universal skill foundation across all templates.

#### Archetype Ontology Structure

Each template includes an archetype ontology at `ontology/ONTOLOGY_{archetype}.yaml`:

```yaml
# ontology/ONTOLOGY_{archetype}.yaml
ontology:
  meta:
    archetype: "{archetype}"
    version: "1.0.0"
    purpose: "Archetype-specific domain concepts"

  concepts:
    {Concept_Name}:
      skos:prefLabel: "{Label}"
      skos:definition: "{Definition}"
      skos:related: []
```

#### Archetype Skill Distribution

| Archetype | Universal | Archetype Skills | Total |
|-----------|:---------:|:----------------:|:-----:|
| worker | 14 | execute-task, report-progress | 16 |
| supervisor | 14 | broadcast-fleet, review-agent, escalate-issue | 17 |
| developer | 14 | run-tests, lint-code, review-pr | 17 |
| consultant | 14 | assess-client, propose-engagement | 16 |
| advisor | 14 | assess-risk, recommend-action | 16 |
| analyst | 14 | analyze-data, generate-report | 16 |
| architect | 14 | design-architecture, assess-tradeoffs | 16 |
| researcher | 14 | search-literature, document-finding | 16 |
| operator | 14 | handle-incident, run-playbook | 16 |
| executive | 14 | make-decision, review-budget | 16 |
| reviewer | 14 | review-artifact, provide-feedback | 16 |
| spec-engineer | 14 | validate-spec, generate-requirement | 16 |

#### Universal Skills (v3.5.0)

All templates include these 14 universal skills:

| Skill | Category | Purpose |
|-------|----------|---------|
| aget-wake-up | Session | Initialize session |
| aget-wind-down | Session | End session with handoff |
| aget-check-health | Session | Run health inspection |
| aget-check-kb | Session | Validate KB health |
| aget-check-evolution | Session | Monitor evolution directory |
| aget-check-sessions | Session | Monitor sessions directory |
| aget-save-state | Session | Save workflow state |
| aget-record-lesson | Evolution | Record lessons learned |
| aget-capture-observation | Evolution | Capture research observations |
| aget-studyup | Research | Focused KB research |
| aget-create-project | Planning | Create research projects |
| aget-review-project | Planning | Review project progress |
| aget-propose-skill | Governance | Propose new skills |

#### Directory Layout (v3.5.0)

```
template-{archetype}-aget/
├── ontology/                       # NEW: Archetype ontology
│   └── ONTOLOGY_{archetype}.yaml
├── .claude/skills/                 # NEW: AGET skills
│   ├── aget-wake-up/              # Universal skill
│   │   └── SKILL.md
│   ├── aget-{archetype-skill}/    # Archetype-specific
│   │   └── SKILL.md
│   └── ...
├── ...
```

**Reference**: L574 (v3.5.0 Vocabulary & Skills Architecture), L486 (Ontology-Driven Creation)

### CAP-TPL-017: Cross-Scope Reference Resolution (v3.6.0)

The SYSTEM shall validate that template Artifact_References resolve to existing Framework_Artifacts.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-TPL-017-01 | ubiquitous | The SYSTEM shall extract Artifact_References from template markdown and YAML files |
| CAP-TPL-017-02 | event-driven | WHEN validation runs, the SYSTEM shall resolve each Artifact_Reference to a Framework_Artifact in `aget/` |
| CAP-TPL-017-03 | unwanted | Template artifacts shall NOT contain Dangling_References to non-existent framework artifacts |
| CAP-TPL-017-04 | conditional | IF Cross_Scope_Reference cannot be resolved THEN the SYSTEM shall report the unresolvable reference |
| CAP-TPL-017-05 | ubiquitous | Cross_Scope_References shall use explicit paths (e.g., `aget/sops/SOP_aget_create.md`) rather than bare filenames |

**Enforcement**: `validate_template_references.py`

**Source**: L568 (Framework Artifact Scope Specification Gap), CAP-SOP-005

---

## References

- AGET_5D_ARCHITECTURE_SPEC.md - Umbrella 5D specification
- AGET_PERSONA_SPEC.md - D1 PERSONA dimension
- AGET_MEMORY_SPEC.md - D2 MEMORY dimension
- AGET_REASONING_SPEC.md - D3 REASONING dimension
- AGET_SKILLS_SPEC.md - D4 SKILLS dimension
- AGET_CONTEXT_SPEC.md - D5 CONTEXT dimension
- WORKER_TEMPLATE_SPEC_v1.0.yaml - Foundation capabilities (superseded)
- TEMPLATE_STRUCTURE_GUIDE.md - v2.x structure (superseded)

---

*AGET TEMPLATE Specification v3.4.0*
*"Templates are composable agent patterns enabling consistent 5D composition"*
*Updated: 2026-02-14 (CAP-TPL-016 archetype customization)*
