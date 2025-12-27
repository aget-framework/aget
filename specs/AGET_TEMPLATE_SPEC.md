# AGET TEMPLATE Specification

**Version**: 3.0.0
**Status**: Active
**Category**: Standards (Template Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_TEMPLATE_SPEC.md`
**Change Proposal**: CP-017, CP-018
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

#### v3.0 Directory Layout

```
template-{type}-aget/
├── .aget/                          # AGET framework directory
│   ├── version.json                # Agent version + template reference
│   ├── identity.json               # North Star (D1: PERSONA)
│   │
│   ├── persona/                    # D1: PERSONA dimension
│   │   ├── archetype.yaml          # Selected archetype configuration
│   │   └── style.yaml              # Communication style settings
│   │
│   ├── memory/                     # D2: MEMORY dimension
│   │   ├── domain/                 # Domain knowledge
│   │   ├── organizational/         # Organizational knowledge
│   │   └── experiential/           # Experience and learnings
│   │
│   ├── reasoning/                  # D3: REASONING dimension
│   │   ├── decision_authority.yaml # Decision authority matrix
│   │   └── planning_patterns.yaml  # Planning approach configuration
│   │
│   ├── skills/                     # D4: SKILLS dimension
│   │   ├── capabilities.yaml       # Declared capabilities
│   │   └── phase_mapping.yaml      # A-SDLC phase assignments
│   │
│   ├── context/                    # D5: CONTEXT dimension
│   │   ├── relationships.yaml      # Agent relationships
│   │   └── scope.yaml              # Operational scope
│   │
│   ├── patterns/                   # Operational patterns (scripts)
│   │   ├── session/
│   │   ├── release/
│   │   └── sync/
│   │
│   └── evolution/                  # Learning documents
│       └── L*.md
│
├── governance/                     # Governance artifacts
│   ├── CHARTER.md                  # Agent charter
│   ├── MISSION.md                  # Mission statement
│   └── SCOPE_BOUNDARIES.md         # Operational boundaries
│
├── tests/                          # Contract tests
│   └── contract_tests.py
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
  required_directories:
    - path: ".aget/"
      purpose: "Agent identity and configuration"
    - path: ".aget/persona/"
      purpose: "PERSONA dimension configuration"
    - path: ".aget/memory/"
      purpose: "MEMORY dimension structure"
    - path: ".aget/reasoning/"
      purpose: "REASONING dimension configuration"
    - path: ".aget/skills/"
      purpose: "SKILLS dimension configuration"
    - path: ".aget/context/"
      purpose: "CONTEXT dimension configuration"
    - path: ".aget/evolution/"
      purpose: "Learning documents"
    - path: "governance/"
      purpose: "Governance artifacts"
    - path: "tests/"
      purpose: "Contract tests"

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

*AGET TEMPLATE Specification v3.0.0*
*"Templates are composable agent patterns enabling consistent 5D composition"*
