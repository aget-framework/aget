# AGET Portability Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (Architecture)
**Format Version**: 1.2
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_PORTABILITY_SPEC.md`
**Change Origin**: L394 (Design by Fleet Exploration)

---

## Abstract

This specification defines the portability model for AGET agents, establishing clear boundaries between framework-specific configuration and portable agent knowledge. The specification enables three use cases: migration to other frameworks, framework-free operation, and long-term data preservation.

## Motivation

Users investing in AGET agents accumulate valuable knowledge:
- Learnings captured in L-docs
- Governance decisions and rationale
- Planning artifacts and project history
- Session notes and work products

This knowledge should not be locked to the AGET framework. Users need:
1. **Discoverability**: Hidden `.aget/` directory obscures valuable content
2. **Portability**: Knowledge should survive framework changes
3. **Freedom**: Users should be able to exit the framework with their work
4. **Preservation**: Knowledge should persist even if AGET is abandoned

## Scope

**Applies to**: All AGET agents (templates and instances).

**Defines**:
- Portable_Content vs Framework_Configuration distinction
- Export mechanism requirements
- Discoverability requirements
- Constraint acknowledgment requirements

**Related Specifications**:
- AGET_LICENSE_SPEC.md (licensing separation)
- AGET_MEMORY_SPEC.md (6-layer memory model)
- AGET_5D_ARCHITECTURE_SPEC.md (dimension structure)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "portability"
    version: "1.0.0"
    inherits: "aget_core"

  portability:
    Portable_Content:
      skos:definition: "Agent knowledge that can be used independently of AGET framework"
      skos:narrower: ["Learning_Content", "Governance_Content", "Planning_Content", "Work_Product", "Knowledge_Content"]
    Framework_Configuration:
      skos:definition: "AGET-specific schemas, formats, and mechanisms"
      skos:narrower: ["Identity_Schema", "Composition_Config", "Pattern_Scripts", "Capability_DAG", "Operational_State"]
    Export_Mechanism:
      skos:definition: "Tooling to extract Portable_Content from agent"
    Framework_Ejection:
      skos:definition: "Process of removing AGET framework while preserving Portable_Content"
    Constraint_Acknowledgment:
      skos:definition: "Explicit user confirmation of removed safety constraints"
    Discoverability:
      skos:definition: "Ability to find and access agent knowledge without framework knowledge"
    Visibility:
      skos:definition: "Property that content is not in hidden directories (except .aget/evolution/)"
      skos:note: "All Portable_Content MUST be visible except L-docs (portable exception)"
    Operational_State:
      skos:definition: "Runtime state such as compliance.json, checkpoints, session state"
      skos:note: "Classified as Framework_Configuration, not portable"

  memory:
    Content_Layer:
      skos:definition: "The semantic meaning and insights within memory artifacts"
    Format_Layer:
      skos:definition: "The structural representation and schema of memory artifacts"
```

---

## Requirements

### CAP-PORT-001: Portable Content Definition

The SYSTEM shall distinguish Portable_Content from Framework_Configuration.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-001-01 | ubiquitous | The SYSTEM shall classify L-doc *content* as Portable_Content |
| CAP-PORT-001-02 | ubiquitous | The SYSTEM shall classify governance/ artifacts as Portable_Content |
| CAP-PORT-001-03 | ubiquitous | The SYSTEM shall classify planning/ artifacts as Portable_Content |
| CAP-PORT-001-04 | ubiquitous | The SYSTEM shall classify work products (src/, docs/, data/) as Portable_Content |
| CAP-PORT-001-05 | ubiquitous | The SYSTEM shall classify .aget/*.json schemas as Framework_Configuration |
| CAP-PORT-001-06 | ubiquitous | The SYSTEM shall classify 5D YAML configs as Framework_Configuration |
| CAP-PORT-001-07 | ubiquitous | The SYSTEM shall classify pattern scripts as Framework_Configuration |
| CAP-PORT-001-08 | ubiquitous | The SYSTEM shall classify knowledge/ artifacts as Portable_Content |
| CAP-PORT-001-09 | ubiquitous | The SYSTEM shall classify decisions/ artifacts as Portable_Content |
| CAP-PORT-001-10 | ubiquitous | The SYSTEM shall classify operational state (.aget/state/, checkpoints/) as Framework_Configuration |

**Enforcement**: Export mechanism validation

### CAP-PORT-001A: Visibility Requirement

The SYSTEM shall ensure Portable_Content is visible (not hidden).

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-001A-01 | ubiquitous | The SYSTEM shall place Portable_Content in visible directories |
| CAP-PORT-001A-02 | ubiquitous | The SYSTEM shall NOT place user content in hidden directories (except .aget/evolution/) |
| CAP-PORT-001A-03 | conditional | IF privacy-sensitive content exists THEN the SYSTEM shall use .gitignore (not hiding) |
| CAP-PORT-001A-04 | ubiquitous | The SYSTEM shall treat .aget/evolution/ as portable exception (hidden but portable) |

**Enforcement**: Directory structure validation

**Rationale**: Fleet exploration (L394) revealed that hiding user content impairs discoverability. Privacy concerns should be addressed via .gitignore, not directory hiding.

#### Portability Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PORTABILITY CLASSIFICATION v1.1                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PORTABLE_CONTENT (User-owned, survives framework exit)                 │
│  ─────────────────────────────────────────────────────                  │
│                                                                         │
│  CORE SET (all archetypes):                                             │
│  │ Location              │ Content Type        │ Visible │ Portable │   │
│  ├───────────────────────┼─────────────────────┼─────────┼──────────┤   │
│  │ governance/           │ Charter, mission    │ ✅      │ ✅       │   │
│  │ sessions/             │ Session notes       │ ✅      │ ✅       │   │
│  │ planning/             │ Plans, decisions    │ ✅      │ ✅       │   │
│  │ knowledge/            │ Domain knowledge    │ ✅      │ ✅       │   │
│  │ .aget/evolution/*.md  │ L-docs (learnings)  │ ❌*     │ ✅       │   │
│  │                       │ *Portable exception │         │          │   │
│                                                                         │
│  ARCHETYPE EXTENSIONS (inherit with override):                          │
│  │ Location              │ Content Type        │ Archetypes          │   │
│  ├───────────────────────┼─────────────────────┼─────────────────────┤   │
│  │ products/             │ Deliverables        │ Developer+          │   │
│  │ workspace/            │ Work in progress    │ Developer+          │   │
│  │ src/                  │ Source code         │ Developer+          │   │
│  │ docs/                 │ Documentation       │ All                 │   │
│  │ data/                 │ Persistent data     │ All                 │   │
│  │ decisions/            │ ADRs                │ Architect+          │   │
│  │ reports/              │ Research outputs    │ Analyst+            │   │
│  │ sops/                 │ Operating procs     │ Supervisor+         │   │
│  │ clients/              │ Client relations    │ Advisor+ (.gitignore)│  │
│  │ engagements/          │ Engagement tracking │ Advisor+ (.gitignore)│  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FRAMEWORK_CONFIGURATION (Apache 2.0, requires framework)               │
│  ───────────────────────────────────────────────────────────            │
│  │ Location              │ Content Type        │ Format    │           │
│  ├───────────────────────┼─────────────────────┼───────────┤           │
│  │ .aget/version.json    │ Agent metadata      │ JSON      │ ⚙️        │
│  │ .aget/identity.json   │ North Star schema   │ JSON      │ ⚙️        │
│  │ .aget/persona/*.yaml  │ D1 config           │ YAML      │ ⚙️        │
│  │ .aget/memory/*.yaml   │ D2 config (NOT content!) │ YAML │ ⚙️        │
│  │ .aget/reasoning/*.yaml│ D3 config           │ YAML      │ ⚙️        │
│  │ .aget/skills/*.yaml   │ D4 config           │ YAML      │ ⚙️        │
│  │ .aget/context/*.yaml  │ D5 config           │ YAML      │ ⚙️        │
│  │ .aget/D6_*/*.yaml     │ D6+ extensions      │ YAML      │ ⚙️        │
│  │ .aget/patterns/*      │ Pattern scripts     │ Python    │ ⚙️        │
│  │ .aget/state/*         │ Operational state   │ Various   │ ⚙️        │
│  │ manifest.yaml         │ Capability compose  │ YAML      │ ⚙️        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### CAP-PORT-002: Export Mechanism

The SYSTEM shall provide formal Export_Mechanism for Framework_Ejection.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-002-01 | ubiquitous | The SYSTEM shall provide `export_agent_knowledge.py` script |
| CAP-PORT-002-02 | ubiquitous | The SYSTEM shall extract Portable_Content to visible directories |
| CAP-PORT-002-03 | ubiquitous | The SYSTEM shall preserve L-docs in original markdown format |
| CAP-PORT-002-04 | ubiquitous | The SYSTEM shall generate export manifest documenting what was extracted |
| CAP-PORT-002-05 | conditional | IF --remove-framework specified THEN the SYSTEM shall delete .aget/ |
| CAP-PORT-002-06 | ubiquitous | The SYSTEM shall support --dry-run mode |

**Enforcement**: Script existence and functionality tests

#### Export Script Specification

```bash
# Usage
python3 aget/scripts/export_agent_knowledge.py /path/to/agent \
  --output /path/to/exported \
  --dry-run                          # Show what would be exported
  --remove-framework                 # Delete .aget/ after export
  --acknowledge-constraints-removed  # Required with --remove-framework

# Output Structure (framework-free)
exported/
├── knowledge/                       # From .aget/evolution/ (L-docs)
│   └── *.md                         # L-docs preserved as-is
├── governance/                      # Preserved (core)
├── planning/                        # Preserved (core)
├── sessions/                        # Preserved (core)
├── docs/                            # Preserved (if exists)
├── src/                             # Preserved (if exists)
├── data/                            # Preserved (if exists)
├── products/                        # Preserved (if exists)
├── workspace/                       # Preserved (if exists)
├── decisions/                       # Preserved (if exists)
├── reports/                         # Preserved (if exists)
├── sops/                            # Preserved (if exists)
├── clients/                         # Preserved (if exists, privacy-sensitive)
├── engagements/                     # Preserved (if exists, privacy-sensitive)
├── EXPORT_MANIFEST.md               # What was exported, when, from where
└── REMOVED_CONSTRAINTS.md           # If --remove-framework used
```

### CAP-PORT-003: Discoverability

The SYSTEM shall address hidden directory Discoverability concerns.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-003-01 | ubiquitous | The SYSTEM shall document .aget/ contents in visible README |
| CAP-PORT-003-02 | ubiquitous | The SYSTEM shall provide `ls-knowledge` pattern showing key locations |
| CAP-PORT-003-03 | conditional | IF user requests knowledge locations THEN the SYSTEM shall list visible paths |
| CAP-PORT-003-04 | ubiquitous | The SYSTEM shall place high-value content in visible directories when possible |

**Enforcement**: Documentation review, pattern availability

#### Discoverability Pattern

```markdown
# In README.md or AGENTS.md

## Knowledge Locations

| What | Where | Hidden? |
|------|-------|---------|
| Learnings | `.aget/evolution/` | Yes (use `ls .aget/evolution/`) |
| Governance | `governance/` | No |
| Planning | `planning/` | No |
| Sessions | `sessions/` | No |
| Patterns | `.aget/patterns/` | Yes |
```

### CAP-PORT-004: Constraint Acknowledgment

The SYSTEM shall require explicit Constraint_Acknowledgment for Framework_Ejection.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-004-01 | conditional | IF --remove-framework specified THEN the SYSTEM shall require --acknowledge-constraints-removed |
| CAP-PORT-004-02 | ubiquitous | The SYSTEM shall list removed Inviolables in REMOVED_CONSTRAINTS.md |
| CAP-PORT-004-03 | ubiquitous | The SYSTEM shall list removed Capabilities in REMOVED_CONSTRAINTS.md |
| CAP-PORT-004-04 | ubiquitous | The SYSTEM shall warn about governance enforcement removal |

**Enforcement**: Flag requirement, constraint documentation

#### Removed Constraints Documentation

```markdown
# REMOVED_CONSTRAINTS.md (generated by export)

## Warning

This agent has been exported from the AGET framework. The following
safety constraints are NO LONGER ENFORCED:

## Removed Inviolables

| ID | Statement | Was Enforced By |
|----|-----------|-----------------|
| INV-CORE-001 | shall NOT execute Destructive_Action WITHOUT User_Confirmation | .aget/persona/archetype.yaml |
| INV-CORE-002 | shall NOT modify Production_Data WITHOUT Explicit_Authorization | .aget/persona/archetype.yaml |

## Removed Capabilities

- capability-governance-rigorous (governance enforcement)
- capability-gate-discipline (planning gates)
- capability-memory-management (session protocols)

## Removed Enforcement

- Validators no longer run automatically
- Pattern scripts no longer available
- Wake/wind-down protocols removed

## Your Responsibility

You are now responsible for implementing equivalent constraints
in your chosen framework or workflow.

---
*Exported: 2025-12-27*
*From: my-agent-AGET*
*By: export_agent_knowledge.py v1.0.0*
```

### CAP-PORT-005: Memory Layer Portability

The SYSTEM shall apply Content/Format separation to memory layers.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-PORT-005-01 | ubiquitous | The SYSTEM shall treat L-doc *content* (insights) as Portable_Content |
| CAP-PORT-005-02 | ubiquitous | The SYSTEM shall treat L-doc *naming convention* as Framework_Configuration |
| CAP-PORT-005-03 | ubiquitous | The SYSTEM shall preserve markdown format in export (no conversion needed) |
| CAP-PORT-005-04 | ubiquitous | The SYSTEM shall NOT require L-doc format changes for portability |

**Enforcement**: Export preserves original files

#### Memory Layer Analysis

| Layer | Content (Portable) | Format (Framework) |
|-------|-------------------|-------------------|
| L1: Working | Ephemeral | N/A |
| L2: Session | Session notes, decisions | Session_Handoff template |
| L3: Project | Plans, governance docs | PROJECT_PLAN format |
| L4: Agent | L-doc insights | L-doc naming (LNNN_*.md) |
| L5: Fleet | Inherited knowledge | Inheritance mechanism |
| L6: Context | Loaded context | Loading protocols |

**Key Insight**: L-docs are already markdown. The `LNNN_` naming convention is minor and doesn't impede portability. No export conversion needed.

---

## Authority Model

```yaml
authority:
  applies_to: "all_agents"

  governed_by:
    spec: "AGET_PORTABILITY_SPEC"
    owner: "private-aget-framework-AGET"

  user_authority:
    can_autonomously:
      - "export Portable_Content at any time"
      - "remove AGET framework from their agent"
      - "choose destination for exported content"

    requires_acknowledgment:
      - action: "Framework_Ejection"
        acknowledgment: "--acknowledge-constraints-removed"
        rationale: "User must understand removed safety constraints"

  framework_authority:
    cannot:
      - "prevent export of Portable_Content"
      - "require framework for knowledge access"
      - "lock user data to AGET"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-PORT-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT prevent export of Portable_Content"
      rationale: "User freedom is paramount"

    - id: "INV-PORT-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT require AGET for Portable_Content access"
      rationale: "Knowledge independence from framework"

    - id: "INV-PORT-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT perform Framework_Ejection WITHOUT Constraint_Acknowledgment"
      rationale: "User must understand consequences"
```

---

## Use Cases

### Use Case 1: Migration to Other Framework

User adopts different AI agent framework, wants to preserve work.

```bash
# Export knowledge, keep .aget/ for reference
python3 export_agent_knowledge.py my-agent-AGET/ --output exported/

# Result: exported/ contains all portable content
# Original agent unchanged, can continue using AGET
```

### Use Case 2: Framework-Free Operation

User wants agent without any framework overhead.

```bash
# Export and remove framework
python3 export_agent_knowledge.py my-agent-AGET/ \
  --output my-agent-lite/ \
  --remove-framework \
  --acknowledge-constraints-removed

# Result: my-agent-lite/ is framework-free
# REMOVED_CONSTRAINTS.md documents what was removed
```

### Use Case 3: Data Preservation

User wants knowledge to survive if AGET is abandoned.

```bash
# Export to archive location
python3 export_agent_knowledge.py my-agent-AGET/ \
  --output /archive/my-agent-backup/

# Result: All knowledge preserved in standard formats
# No AGET dependency for future access
```

---

## Structural Requirements

```yaml
structure:
  export_output:
    required_directories:
      - path: "knowledge/"
        purpose: "L-docs from .aget/evolution/"
      - path: "governance/"
        purpose: "Governance artifacts"
      - path: "planning/"
        purpose: "Planning artifacts"

    required_files:
      - path: "EXPORT_MANIFEST.md"
        purpose: "Export documentation"

    conditional_files:
      - path: "REMOVED_CONSTRAINTS.md"
        condition: "IF --remove-framework used"
        purpose: "Constraint removal documentation"
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Data Portability Rights"
  secondary:
    - "Vendor Lock-in Avoidance"
    - "User Sovereignty"
    - "Knowledge Preservation"
  rationale: >
    Users invest significant effort building agent knowledge.
    This knowledge is their intellectual property and should
    remain accessible regardless of framework choice. The
    Content/Format separation enables portability without
    requiring format conversion for most valuable assets.
  reference: "GDPR Data Portability (Article 20) principles"
```

---

## Validation

```bash
# Test export mechanism
python3 aget/scripts/export_agent_knowledge.py /path/to/agent --dry-run

# Validate portability classification
python3 validation/validate_portability_compliance.py --dir /path/to/agent

# Expected output:
# ✅ Portable content identified: 45 files
# ✅ Framework config identified: 23 files
# ✅ Export mechanism available
# ✅ Discoverability documentation present
```

---

## References

- AGET_LICENSE_SPEC.md (licensing separation)
- AGET_MEMORY_SPEC.md (6-layer model)
- AGET_5D_ARCHITECTURE_SPEC.md (dimension structure)
- L393: Framework vs Agent Content Distinction (if captured)
- L452: Shell Orchestration Pattern (CLI portability)
- docs/SHELL_INTEGRATION.md (multi-CLI invocation guide)

---

## Graduation History

```yaml
graduation:
  source: "User question about .aget/ vs outside distinction"
  pattern_origin: "Framework portability concern"
  rationale: "Formalize implicit content/config separation into testable specification"
```

---

*AGET Portability Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*"Your knowledge is yours. The framework is just the scaffold."*
*Updated: 2025-12-27 (L394 visibility requirement)*
