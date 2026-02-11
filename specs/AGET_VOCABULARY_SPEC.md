# AGET Vocabulary Specification

**Version**: 1.11.0
**Status**: Active
**Category**: Core (Standards)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-02-11
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_VOCABULARY_SPEC.md`
**Change Origin**: PROJECT_PLAN_standards_ontology_elevation_v1.0
**Related Specs**: AGET_FRAMEWORK_SPEC
**Consolidates**: AGET_GLOSSARY_STANDARD_SPEC.md, AGET_CONTROLLED_VOCABULARY.md

---

## Abstract

This specification consolidates vocabulary standards and controlled terminology for the AGET framework. It defines SKOS-based vocabulary format, AGET extensions, and canonical terms used across all specifications.

## Motivation

v3.2.0 consolidation goals:
- Reduce spec fragmentation (L434)
- Single source of truth for vocabulary
- Add terms from new Gate 2 specifications
- Include L440 verification vocabulary (Declarative_Completion, Verified_Completion, V_Test)

This spec combines AGET_GLOSSARY_STANDARD_SPEC.md (format) with AGET_CONTROLLED_VOCABULARY.md (terms).

## Scope

**Applies to**: All AGET framework specifications and agents.

**Defines**:
- SKOS foundation and AGET extensions (Part 1)
- Core framework terms (Part 2)
- Domain-specific terms (Part 3)
- Format and validation terms (Part 4)
- Contribution guidelines (Part 5)
- Core domain entities (Part 6) — L459
- Standards Document Ontology (Part 7) — L502

---

# Part 1: Vocabulary Standard

## SKOS Foundation (ADR-001)

Per ADR-001, AGET adopts W3C SKOS as vocabulary foundation:

| SKOS Property | AGET Usage | Required |
|---------------|------------|----------|
| `skos:prefLabel` | Canonical term name | Yes |
| `skos:definition` | Complete definition | Yes |
| `skos:altLabel` | Synonyms, abbreviations | No |
| `skos:broader` | IS-A parent relationship | No |
| `skos:narrower` | IS-A child relationship | No |
| `skos:related` | Associative relationship | No |
| `skos:example` | Usage examples | No |

## AGET Extensions

Custom properties extending SKOS:

| Property | Definition | Cardinality |
|----------|------------|-------------|
| `aget:has` | Possession/containment | 1:many |
| `aget:operatesWithin` | Scope boundary | 1:1 |
| `aget:derivedFrom` | Creation source | 1:many |
| `aget:requires` | Dependency prerequisite | 0:many |
| `aget:supervises` | Authority relationship | 1:many |
| `aget:coordinatesWith` | Peer collaboration | many:many |
| `aget:defines` | Spec → Implementation | 1:many |
| `aget:exhibits` | Instance → Pattern | 1:many |
| `aget:location` | Canonical file path | 0:1 |
| `aget:validationRule` | Automated check | 0:many |
| `aget:anti_pattern` | Invalid usage marker | boolean |
| `aget:pattern` | Valid usage marker | boolean |
| `aget:determinism` | Determinism level (deterministic, probabilistic, syllogistic) | 0:1 |
| `aget:reusability` | Reusability level (universal, parameterized, one_time) | 0:1 |
| `aget:abstraction` | Abstraction level (algorithm → execution) | 0:1 |
| `aget:core_entity` | Marks entity as inheritable core entity (L459) | boolean |
| `aget:attributes` | Entity attribute definitions | 0:many |
| `aget:relationships` | Entity relationship definitions | 0:many |

## Entry Format Patterns

### Minimal Entry
```yaml
Term_Name:
  skos:definition: "Complete definition."
```

### Standard Entry
```yaml
Term_Name:
  skos:prefLabel: "Term_Name"
  skos:definition: "Complete definition."
  skos:altLabel: ["TN", "Alt"]
  skos:example: "Example usage."
```

### Rich Entry
```yaml
Term_Name:
  skos:prefLabel: "Term_Name"
  skos:definition: "Complete definition."
  skos:broader: "Parent_Term"
  skos:narrower: ["Child_A", "Child_B"]
  aget:distinguishedFrom:
    - term: "Similar_Term"
      reason: "Explanation"
  skos:example: ["Example 1", "Example 2"]
```

## Conformance Levels

| Level | Requirements |
|-------|--------------|
| Level 1 (Basic) | prefLabel + definition for all terms |
| Level 2 (Standard) | Level 1 + hierarchies + distinctions |
| Level 3 (Full SKOS) | Level 2 + all relationships + validation |

## Term Usage in Documents (L493)

Per **L493 (Vocabulary_Prose_Marking_Pattern)**, all AGET Vocabulary terms MUST be self-disambiguating in prose through compound construction.

### Design Principle

> **Self-disambiguation by construction eliminates context-dependent judgment.**

If all AGET Vocabulary terms are compound (`Aget_Agent`, `Task_Entity`, `Session_Handoff`), they are unambiguous in ANY context without requiring human judgment.

### Marking Convention

| Category | Convention | Examples |
|----------|------------|----------|
| **AGET Framework** | `Aget_Word` | `Aget_Agent`, `Aget_Instance`, `Aget_Session` |
| **Domain Entity** | `Word_Entity` | `Person_Entity`, `Task_Entity`, `Document_Entity` |
| **AGET Concept** | `Word_Word` | `Aget_Capability`, `Core_Entity_Vocabulary` |
| **AGET Role** | `Aget_Word` | `Aget_Principal`, `Aget_Supervisor` |
| **Artifact Type** | `UPPER_CASE` | `SOP`, `PROJECT_PLAN`, `L_Document` |
| **Technical ID** | `kebab-case` | `capability-action-item-management` |
| **Generic English** | `lowercase` | "tracking", "persistent", "work" |

### Prose Requirements

| ID | Requirement |
|----|-------------|
| R-VOC-PROSE-001 | AGET Vocabulary references MUST use exact `skos:prefLabel` form |
| R-VOC-PROSE-002 | Generic English MUST use lowercase |
| R-VOC-PROSE-003 | Single-word Vocabulary terms are PROHIBITED (use compound forms) |

### Example

**Ambiguous (Wrong)**:
```
Enable agents to track action items that emerge from sessions.
```

**Self-Disambiguating (Correct)**:
```
Enable Aget_Instances to track Action_Items that emerge from Aget_Sessions.
```

### Machine-Parseability

Compound AGET Vocabulary terms match this regex:
```regex
[A-Z][a-z]+(_[A-Z][a-z]+)+
```

---

# Part 2: Core Framework Terms

## Casing Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Domain Objects | Title_Case | `Fleet_Agent`, `Version_Json` |
| Verbs | lowercase | `read`, `execute`, `validate` |
| Constraint Keywords | UPPERCASE | `WITHIN`, `WITHOUT`, `BEFORE` |
| Capability IDs | CAP-XXX-NNN | `CAP-REL-001` |

## Identity Terms

| Term | Definition | altLabel |
|------|------------|----------|
| `AGET` | Agent configuration & lifecycle management framework | — |
| `aget` | Lowercase form; read-only instance type | — |
| `AGET` (caps) | Action-taking instance type with write permissions | — |
| `Fleet_Agent` | Agent registered in Fleet_State under Aget_Supervisor coordination | — |
| `Aget_Template` | Reusable agent archetype (e.g., template-worker-aget) | Template |
| `Aget_Instance` | Concrete agent created from an Aget_Template | Instance |
| `Core_Template` | Fleet role template (worker, advisor, supervisor) | — |
| `Specialized_Template` | Task-specific template (spec-engineer, developer) | — |

## Organizational Terms

| Term | Definition | altLabel |
|------|------------|----------|
| `Aget_Portfolio` | Organizational grouping (e.g., ccb, main) | Portfolio |
| `Aget_Fleet` | Collection of Aget_Instances under Aget_Supervisor coordination | Fleet |
| `Fleet_State` | Canonical registry of Aget_Fleet membership | — |
| `Aget_Supervisor` | Aget_Instance responsible for Aget_Fleet coordination | Supervisor |
| `Aget_Principal` | Human operator with ultimate authority | Principal |

## Configuration Terms

| Term | Definition | altLabel |
|------|------------|----------|
| `Version_Json` | Identity configuration file (.aget/version.json) | — |
| `Agents_Md` | Behavior specification file (AGENTS.md) | — |
| `Claude_Md` | Symlink to Agents_Md for Claude Code | — |
| `Aget_Configuration` | Combined Version_Json + Agents_Md | Configuration |
| `aget_version` | Framework version (e.g., "3.2.0") | — |

## Session Protocol Terms

| Term | Definition | altLabel |
|------|------------|----------|
| `Wake_Protocol` | Aget_Session initialization ritual | — |
| `Wake_Command` | User command "wake up" | — |
| `Wind_Down_Protocol` | Aget_Session finalization | — |
| `Aget_Session_State` | Current Aget_Session context | Session_State |
| `Silent_Execution` | Protocol without showing tool calls | — |

## Evolution Terms

| Term | Definition | altLabel |
|------|------------|----------|
| `Learning_Document` | L-series knowledge capture (e.g., L440) | — |
| `L_Doc` | Abbreviation for Learning_Document | — |
| `Evolution_Directory` | Storage for learning (.aget/evolution/) | — |
| `Published_Learning` | Learning_Document graduated from private evolution to public docs/learnings/ | — |
| `Pattern_Extraction` | Identifying reusable Aget_Pattern | — |
| `Knowledge_Migration` | Moving learning between Aget_Instances | — |

## Ontology Terms (v3.5.0)

| Term | Definition | altLabel |
|------|------------|----------|
| `Ontology_Directory` | Agent directory containing formal vocabulary definitions using SKOS+EARS format | — |
| `Ontology_File` | YAML file containing SKOS-aligned concept definitions and optional EARS requirements | — |

```yaml
Ontology_Directory:
  skos:prefLabel: "Ontology_Directory"
  skos:definition: "Agent directory containing formal vocabulary definitions using SKOS+EARS format."
  skos:broader: "Agent_Directory"
  aget:location: "{agent}/ontology/"
  aget:required: true
  skos:related: ["Knowledge_Directory", "Specs_Directory", "Evolution_Directory"]

Ontology_File:
  skos:prefLabel: "Ontology_File"
  skos:definition: "YAML file containing SKOS-aligned concept definitions and optional EARS requirements."
  aget:format: "YAML+SKOS+EARS"
  aget:naming_pattern: "ONTOLOGY_<domain>_vX.Y.yaml"
  skos:broader: "Agent_Artifact"
  skos:related: ["Learning_Document", "Specification"]
```

**L-doc Reference**: L482 (Executable Ontology - SKOS+EARS Grounding)

---

# Part 3: Domain Terms

## Process Terms (CAP-PP-*)

| Term | Definition |
|------|------------|
| `PROJECT_PLAN` | Formal gated execution plan |
| `Gate` | Decision checkpoint with deliverables and V-tests |
| `Gate_Approval` | GO/NOGO decision at gate boundary |
| `Decision_Point` | Explicit pause requiring approval |
| `Substantial_Change` | Change requiring formal planning |

## Verification Terms (L440 Critical)

```yaml
Declarative_Completion:
  skos:definition: "Marking deliverable complete via manual checkbox without verification"
  aget:anti_pattern: true
  skos:related: ["Verification_Theater", "L440"]

Verified_Completion:
  skos:definition: "Marking deliverable complete after executing verification test"
  aget:pattern: true
  skos:related: ["V_Test", "L352_Traceability"]

V_Test:
  skos:definition: "Verification test with executable command and expected output"
  aget:naming_pattern: "V{gate}.{test}"
  skos:example: ["V0.1", "V7.0.1", "V2.3"]
  skos:related: ["CAP-PP-011", "CAP-TEST-006"]
```

| Term | Definition |
|------|------------|
| `V_Test` | Verification test with executable command and expected output |
| `Declarative_Completion` | ANTI-PATTERN: Checkbox without verification |
| `Verified_Completion` | PATTERN: Completion after V-test execution |
| `BLOCKING_Test` | V-test that halts gate on failure |

## Testing Terms (CAP-TEST-*)

| Term | Definition |
|------|------------|
| `Contract_Test` | Test verifying compliance with specifications |
| `Unit_Test` | Test verifying individual function behavior |
| `V_Test` | Verification test in PROJECT_PLAN gates |
| `Test_Coverage` | Percentage of code exercised by tests |
| `Theater_Ratio` | Ratio of missing validators to referenced |
| `Validator_Theater` | Referencing validators that don't exist |

## Release Terms (CAP-REL-*)

```yaml
Version_Bearing_File:
  skos:prefLabel: "Version_Bearing_File"
  skos:definition: "A file that contains version information and must be updated during releases to maintain version coherence."
  skos:narrower:
    - Version_Json
    - Agents_Md
    - Manifest_Yaml
    - README
    - CHANGELOG
  aget:primary_source: "Version_Json"
  aget:derived_sources: ["Agents_Md", "Manifest_Yaml", "README", "CHANGELOG"]
  aget:enforcement: "validate_version_inventory.py"
  skos:related: ["R-REL-VER-001", "L429", "L444", "L521"]
  skos:example: [".aget/version.json (primary)", "AGENTS.md (@aget-version)", "manifest.yaml", "README.md"]

Version_Coherence:
  skos:prefLabel: "Version_Coherence"
  skos:definition: "The state where all Version_Bearing_Files display the same version string."
  skos:related: ["Version_Bearing_File", "R-REL-VER-001", "L444"]
  aget:validation: "All derived sources must match primary source"

Version_Drift_File:
  skos:prefLabel: "Version_Drift_File"
  skos:definition: "ANTI-PATTERN: A Version_Bearing_File showing a stale version that doesn't match the primary source."
  aget:anti_pattern: true
  skos:related: ["Version_Bearing_File", "Version_Coherence", "L521"]
  skos:example: "README.md showing v3.1.0 when version.json shows v3.3.0"
```

| Term | Definition |
|------|------------|
| `Release_Version` | Semantic version identifying a release |
| `Manager_Migration` | Updating managing agent version before release (R-REL-006) |
| `Multi_Repo_Coordination` | Synchronized release across repositories |
| `Release_Gate` | Verification checkpoint in release process |
| `CHANGELOG` | Document tracking notable changes per version |
| `GitHub_Release` | GitHub release object with tag and notes |
| `Deep_Release_Notes` | Narrative documentation beyond CHANGELOG |
| `Version_Bearing_File` | File containing version info requiring update during releases (R-REL-VER-001) |
| `Version_Coherence` | State where all Version_Bearing_Files show same version |
| `Version_Drift` | ANTI-PATTERN: Manager behind managed repos |
| `Version_Drift_File` | ANTI-PATTERN: Version_Bearing_File with stale version (L521) |
| `Declarative_Release` | ANTI-PATTERN: Declaring version in commit message without updating version.json (L517) |
| `Version_Overrun` | ANTI-PATTERN: Instance version exceeds framework version (L517) |
| `Template_Abandonment` | ANTI-PATTERN: Published templates left behind during upgrades (R-REL-015 violation, L517) |
| `SOP_Theater` | ANTI-PATTERN: SOP steps without verification (L517) |
| `Release_Verification` | Automated validation that all release artifacts complete before push (CAP-REL-009) |
| `Pre_Push_Gate` | BLOCKING validation checkpoint before git push (CAP-REL-009) |
| `Version_Ceiling` | Constraint that instance version ≤ framework version (CAP-REL-010) |

### VERSION_SCOPE Terms (R-REL-020)

```yaml
Version_Scope:
  skos:prefLabel: "Version_Scope"
  skos:altLabel: ["VERSION_SCOPE", "Release_Scope"]
  skos:definition: "Planning artifact that defines the boundaries, objectives, work items, timeline, and success criteria for a specific version release; serves as the authoritative scope document for release coordination"
  skos:broader: ["Planning_Artifact", "Release_Governance"]
  skos:narrower: ["MVP_Scope", "Full_Scope", "Out_of_Scope"]
  skos:related: ["PROJECT_PLAN", "CHANGELOG", "Release_Notes", "Release_Checklist"]
  aget:location: "planning/VERSION_SCOPE_vX.Y.Z.md"
  aget:template: "planning/TEMPLATE_VERSION_SCOPE.md"
  skos:example: "VERSION_SCOPE_v3.4.0.md"

Release_Phase:
  skos:prefLabel: "Release_Phase"
  skos:definition: "Discrete stage in the release lifecycle with specific objectives, deliverables, and completion criteria"
  skos:broader: "Release_Governance"
  skos:narrower: ["Pre_Release_Phase", "Release_Execution_Phase", "Post_Release_Phase"]
  skos:related: ["Version_Scope", "Release_Checklist"]

Pre_Release_Phase:
  skos:prefLabel: "Pre_Release_Phase"
  skos:altLabel: ["Phase_0", "Pre_Release_Validation"]
  skos:definition: "Release phase focused on validation and preparation before deployment; includes scope finalization, testing completion, documentation readiness, and blocker resolution"
  skos:broader: "Release_Phase"
  skos:related: ["Feature_Freeze", "Code_Freeze", "Release_Blocker"]

Release_Execution_Phase:
  skos:prefLabel: "Release_Execution_Phase"
  skos:altLabel: ["Phase_1_2", "Release_Day"]
  skos:definition: "Release phase covering version bump, tagging, deployment, and announcement; the actual release execution"
  skos:broader: "Release_Phase"
  skos:related: ["Version_Bump", "Git_Tag", "Release_Handoff"]

Post_Release_Phase:
  skos:prefLabel: "Post_Release_Phase"
  skos:altLabel: ["Phase_3", "Post_Release_Validation"]
  skos:definition: "Release phase focused on validation, monitoring, and learning after deployment; includes smoke testing, issue monitoring, and retrospective"
  skos:broader: "Release_Phase"
  skos:related: ["Release_Retrospective", "Hotfix", "Rollback"]

MVP_Scope:
  skos:prefLabel: "MVP_Scope"
  skos:altLabel: ["Must_Ship", "Blocking_Scope"]
  skos:definition: "Subset of Version_Scope containing items that MUST be complete for the release to proceed; incomplete MVP items block release"
  skos:broader: "Version_Scope"
  skos:related: ["Release_Blocker", "Full_Scope"]
  aget:constraint: "All MVP items must be complete before Release_Execution_Phase"

Rollback_Plan:
  skos:prefLabel: "Rollback_Plan"
  skos:definition: "Contingency procedure for reverting a release if critical issues are discovered post-deployment; includes triggers, steps, and owner"
  skos:broader: "Release_Governance"
  skos:related: ["Post_Release_Phase", "Hotfix", "Risk_Mitigation"]

Release_Retrospective:
  skos:prefLabel: "Release_Retrospective"
  skos:altLabel: ["Post_Release_Retrospective", "Release_Review"]
  skos:definition: "Structured review conducted after release completion to capture lessons learned, identify improvements, and update processes"
  skos:broader: "Release_Governance"
  skos:related: ["Post_Release_Phase", "Lesson_Learned", "L_Doc"]
```

| Term | Definition |
|------|------------|
| `Version_Scope` | Planning artifact defining boundaries, objectives, and success criteria for a release (R-REL-020) |
| `Release_Phase` | Discrete stage in release lifecycle (Pre-Release, Execution, Post-Release) |
| `Pre_Release_Phase` | Phase 0: validation before deployment (scope, testing, blockers) |
| `Release_Execution_Phase` | Phase 1-2: version bump, tagging, deployment |
| `Post_Release_Phase` | Phase 3: validation after deployment (monitoring, retrospective) |
| `MVP_Scope` | Must-Ship items that BLOCK release if incomplete |
| `Rollback_Plan` | Contingency procedure for reverting release on critical issues |
| `Release_Retrospective` | Structured review after release to capture lessons learned |

## Documentation Terms (CAP-DOC-*)

| Term | Definition |
|------|------------|
| `README` | Primary entry point documentation |
| `CLI_Settings_File` | AI assistant configuration (AGENTS.md, CLAUDE.md) |
| `Inline_Documentation` | Documentation within code (docstrings) |
| `Example_Documentation` | Practical examples for specs/patterns |
| `Documentation_Theater` | ANTI-PATTERN: Docs that don't help |

## Organization Terms (CAP-ORG-*)

| Term | Definition |
|------|------------|
| `Homepage` | Organization README profile |
| `Version_Badge` | Badge showing current version |
| `Roadmap` | Version planning visibility |
| `Pinned_Repository` | Featured repo on organization page |

## Error Terms (CAP-ERR-*)

| Term | Definition |
|------|------------|
| `Exit_Code` | Process return code (0=success, 1=failure) |
| `Error_Message` | Human-readable failure description |
| `Recovery_Pattern` | Strategy for handling errors |
| `Verbose_Mode` | Extended output for debugging |

## Security Terms (CAP-SEC-*)

| Term | Definition |
|------|------------|
| `Content_Security` | Preventing sensitive info in public repos |
| `Secrets_Management` | Handling API keys and credentials |
| `Pre_Publication_Review` | Review before public push |
| `Public_Private_Boundary` | Separation of public/private content |
| `Sanitization` | Removing sensitive content from L-docs |

## Issue Governance Terms (CAP-ISSUE-*)

```yaml
Issue_Destination:
  skos:prefLabel: "Issue_Destination"
  skos:definition: "Target repository for issue filing based on agent type."
  skos:narrower:
    - Private_Issue_Destination
    - Public_Issue_Destination
  aget:governed_by: "AGET_ISSUE_GOVERNANCE_SPEC"
  skos:related: ["R-ISSUE-001", "R-ISSUE-002"]

Private_Issue_Destination:
  skos:prefLabel: "Private_Issue_Destination"
  skos:definition: "Issue destination for Private_Fleet_Agent (gmelli/aget-aget)."
  skos:broader: "Issue_Destination"
  aget:value: "gmelli/aget-aget"

Public_Issue_Destination:
  skos:prefLabel: "Public_Issue_Destination"
  skos:definition: "Issue destination for Public_Remote_Agent (aget-framework/aget)."
  skos:broader: "Issue_Destination"
  aget:value: "aget-framework/aget"

Private_Fleet_Agent:
  skos:prefLabel: "Private_Fleet_Agent"
  skos:definition: "Agent in gmelli's private fleet, may reference private details in issues."
  skos:related: ["R-ISSUE-001", "Issue_Sanitization"]

Public_Remote_Agent:
  skos:prefLabel: "Public_Remote_Agent"
  skos:definition: "Agent not in private fleet, issue content must be sanitized for public."
  skos:related: ["R-ISSUE-002", "Issue_Sanitization"]

Issue_Sanitization:
  skos:prefLabel: "Issue_Sanitization"
  skos:definition: "Process of removing private information from issue content before public filing."
  skos:related: ["R-ISSUE-003", "R-ISSUE-004", "Private_Pattern"]
  aget:enforcement: "sanitize_issue_content.py"

Private_Pattern:
  skos:prefLabel: "Private_Pattern"
  skos:definition: "Content pattern indicating private/internal information that should not appear in public issues."
  skos:example: ["private-*-aget", "gmelli/*", "fleet size disclosure"]
  aget:detection_script: "sanitize_issue_content.py"

Cross_Boundary_Filing:
  skos:prefLabel: "Cross_Boundary_Filing"
  skos:definition: "ANTI-PATTERN: Private agent filing to public repo without sanitization."
  aget:anti_pattern: true
  aget:severity: "high"
  skos:related: ["R-ISSUE-001", "R-ISSUE-005"]

Issue_Fragmentation:
  skos:prefLabel: "Issue_Fragmentation"
  skos:definition: "ANTI-PATTERN: Issues scattered across template repos instead of central tracker."
  aget:anti_pattern: true
  skos:related: ["R-ISSUE-007", "R-ISSUE-009"]
```

| Term | Definition |
|------|------------|
| `Issue_Destination` | Target repository for issue filing based on agent type |
| `Private_Issue_Destination` | Private fleet issue destination (gmelli/aget-aget) |
| `Public_Issue_Destination` | Public/remote issue destination (aget-framework/aget) |
| `Private_Fleet_Agent` | Agent in private fleet, may include private details |
| `Public_Remote_Agent` | Agent outside private fleet, content must be sanitized |
| `Issue_Sanitization` | Removing private info before public issue filing |
| `Private_Pattern` | Content pattern indicating private information |
| `Cross_Boundary_Filing` | ANTI-PATTERN: Private agent filing to public repo |
| `Issue_Fragmentation` | ANTI-PATTERN: Issues scattered across template repos |

## Migration Terms (CAP-MIG-*)

| Term | Definition |
|------|------------|
| `Pre_Flight` | Verification procedure executed before primary operation to ensure environment readiness |
| `Health_Check` | Network/service reachability verification using lightweight probes (e.g., `git ls-remote`) |
| `Framework_Sync` | Synchronization of local framework clone with remote origin |
| `Remote_Supervisor` | Aget_Supervisor executing migration on a machine different from framework development |
| `Cross_Machine_Migration` | Fleet_Migration where execution environment differs from framework development environment |
| `Stale_Framework` | Framework clone that has not been synchronized with remote, causing version mismatch errors |
| `State_Verification` | Re-study/re-research procedure after Framework_Sync to ensure agent context is valid |

## Executable Knowledge Ontology Terms (L451)

### EKO Core

```yaml
Executable_Knowledge_Ontology:
  skos:prefLabel: "Executable_Knowledge_Ontology"
  skos:altLabel: ["EKO"]
  skos:definition: "Taxonomy of actionable artifacts that agents produce, consume, and execute—spanning from abstract algorithms to concrete execution traces, characterized along dimensions of abstraction, determinism, and reusability."
  skos:broader: "Ontology"
  aget:source: "L451"
```

| Term | Definition |
|------|------------|
| `EKO` | Executable Knowledge Ontology - three-axis artifact taxonomy |
| `Abstraction_Level` | EKO axis: position from specification to execution |
| `Determinism_Level` | EKO axis: predictability of artifact behavior |
| `Reusability_Level` | EKO axis: frequency and scope of artifact application |

### Abstraction Axis Terms

```yaml
Algorithm_Concept:
  skos:prefLabel: "Algorithm_Concept"
  skos:altLabel: ["Algorithm"]
  skos:definition: "Formal operation composed of basic formal operations that terminates."
  skos:broader: "Aget_Concept"
  aget:abstraction: "highest"

Process_Concept:
  skos:prefLabel: "Process_Concept"
  skos:altLabel: ["Process"]
  skos:definition: "Activity sequence transforming inputs through states."
  skos:broader: "Aget_Concept"
  aget:abstraction: "medium"

Procedure_Concept:
  skos:prefLabel: "Procedure_Concept"
  skos:altLabel: ["Procedure"]
  skos:definition: "Sequence of steps to accomplish a task."
  skos:broader: "Aget_Concept"
  aget:abstraction: "medium"

Function_Concept:
  skos:prefLabel: "Function_Concept"
  skos:altLabel: ["Function"]
  skos:definition: "Maps every domain member to range member."
  skos:broader: "Aget_Concept"
  aget:abstraction: "high"

Workflow_Concept:
  skos:prefLabel: "Workflow_Concept"
  skos:altLabel: ["Workflow"]
  skos:definition: "Orchestrates task sequences through execution engine."
  skos:broader: "Aget_Concept"
  aget:abstraction: "medium-low"

Protocol_Concept:
  skos:prefLabel: "Protocol_Concept"
  skos:altLabel: ["Protocol"]
  skos:definition: "Rules governing interaction or communication between parties."
  skos:broader: "Aget_Concept"
  aget:abstraction: "medium"
```

### Determinism Axis Terms

```yaml
Deterministic_Property:
  skos:prefLabel: "Deterministic_Property"
  skos:altLabel: ["Deterministic"]
  skos:definition: "Artifact behavior where same input always produces same output."
  skos:broader: "Aget_Property"
  aget:autonomy: "high"
  skos:example: ["Algorithm_Concept", "SOP", "Runbook"]

Probabilistic_Property:
  skos:prefLabel: "Probabilistic_Property"
  skos:altLabel: ["Probabilistic"]
  skos:definition: "Artifact behavior with formally modeled uncertainty."
  skos:broader: "Aget_Property"
  aget:autonomy: "medium"
  skos:example: ["ML_Model", "Monte_Carlo", "A_B_Test"]

Syllogistic_Property:
  skos:prefLabel: "Syllogistic_Property"
  skos:altLabel: ["Syllogistic", "Adaptive"]
  skos:definition: "Artifact behavior requiring reasoning and judgment."
  skos:broader: "Aget_Property"
  aget:autonomy: "low"
  skos:example: ["Playbook", "PROJECT_PLAN", "Strategic_Planning"]
```

### Reusability Axis Terms

```yaml
Universal_Property:
  skos:prefLabel: "Universal_Property"
  skos:altLabel: ["Universal"]
  skos:definition: "Artifact applied same way across all contexts."
  skos:broader: "Aget_Property"
  skos:example: ["SOP", "Algorithm_Concept", "Utility_Function"]

Parameterized_Property:
  skos:prefLabel: "Parameterized_Property"
  skos:altLabel: ["Parameterized"]
  skos:definition: "Artifact template with inputs for context-specific execution."
  skos:broader: "Aget_Property"
  skos:example: ["Runbook", "Configurable_Protocol"]

One_Time_Property:
  skos:prefLabel: "One_Time_Property"
  skos:altLabel: ["One_Time"]
  skos:definition: "Artifact for specific instance, unique execution."
  skos:broader: "Aget_Property"
  skos:example: ["PROJECT_PLAN", "Execution_Trace"]
```

### Artifact Type Terms

```yaml
SOP_Artifact:
  skos:prefLabel: "SOP_Artifact"
  skos:altLabel: ["SOP", "Standard_Operating_Procedure"]
  skos:definition: "Formal organizational reference document for routine tasks."
  aget:determinism: "deterministic"
  aget:reusability: "universal"
  aget:naming: "SOP_{scope}.md"

Runbook_Artifact:
  skos:prefLabel: "Runbook_Artifact"
  skos:altLabel: ["Runbook"]
  skos:definition: "Compiles routine procedures for predictable outcomes with decision points."
  aget:determinism: "deterministic"
  aget:reusability: "parameterized"
  aget:naming: "RUNBOOK_{scope}.md"

Playbook_Artifact:
  skos:prefLabel: "Playbook_Artifact"
  skos:altLabel: ["Playbook"]
  skos:definition: "Strategic guidelines with multiple plays for scenario-based response."
  aget:determinism: "syllogistic"
  aget:reusability: "parameterized"
  aget:naming: "PLAYBOOK_{scenario}.md"

Project_Plan:
  skos:prefLabel: "Project_Plan"
  skos:altLabel: ["PROJECT_PLAN"]
  skos:definition: "Formal approved document guiding one-time execution with gates."
  aget:determinism: "syllogistic"
  aget:reusability: "one_time"
  aget:naming: "PROJECT_PLAN_{scope}_v{M}.{m}.md"
```

### Meta-Ontology Terms (L494)

Per **L494 (Vocabulary_Meta_Ontology_Pattern)**, the AGET vocabulary framework self-hosts its own meta-ontology through four foundational terms. These meta-terms classify all other vocabulary entries.

```yaml
Aget_Entity:
  skos:prefLabel: "Aget_Entity"
  skos:altLabel: ["Entity"]
  skos:definition: "A distinct, identifiable thing in the domain that can have attributes and relationships. The root of all domain objects that Aget_Instances work with."
  aget:meta_entity: true
  skos:narrower: ["Person_Entity", "Organization_Entity", "Document_Entity", "Task_Entity", "Event_Entity", "Project_Entity", "Decision_Entity", "Requirement_Entity"]
  skos:example: "Person_Entity, Task_Entity, Document_Entity"

Aget_Concept:
  skos:prefLabel: "Aget_Concept"
  skos:altLabel: ["Concept"]
  skos:definition: "An abstract notion or category used for classification, reasoning, or organization within the AGET framework. Parent of EKO abstraction axis terms."
  aget:meta_entity: true
  skos:narrower: ["Algorithm_Concept", "Process_Concept", "Procedure_Concept", "Function_Concept", "Workflow_Concept", "Protocol_Concept"]
  skos:example: "Algorithm_Concept, Protocol_Concept, Workflow_Concept"

Aget_Property:
  skos:prefLabel: "Aget_Property"
  skos:altLabel: ["Property"]
  skos:definition: "A characteristic or attribute that describes how an artifact behaves or can be applied. Parent of EKO determinism and reusability axis terms."
  aget:meta_entity: true
  skos:narrower: ["Deterministic_Property", "Probabilistic_Property", "Syllogistic_Property", "Universal_Property", "Parameterized_Property", "One_Time_Property"]
  skos:example: "Deterministic_Property, Universal_Property, One_Time_Property"

Aget_Specification:
  skos:prefLabel: "Aget_Specification"
  skos:altLabel: ["Specification", "Spec"]
  skos:definition: "A formal document that defines requirements, formats, or standards within the AGET framework. Joins Aget_Entity, Aget_Concept, and Aget_Property through normative definitions."
  aget:meta_entity: true
  skos:narrower: ["AGET_VOCABULARY_SPEC", "AGET_TEMPLATE_SPEC", "AGET_INSTANCE_SPEC", "AGET_FRAMEWORK_SPEC"]
  skos:example: "AGET_VOCABULARY_SPEC.md, AGET_TEMPLATE_SPEC.md"
```

#### Meta-Ontology ERD

```
                    ┌─────────────────────┐
                    │ Aget_Specification  │
                    │                     │
                    │ Defines/documents   │
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Aget_Entity   │ │  Aget_Concept   │ │  Aget_Property  │
│                 │ │                 │ │                 │
│ Domain objects  │ │ Abstractions    │ │ Characteristics │
│ worked WITH     │ │ of executable   │ │ and behavioral  │
│                 │ │ knowledge       │ │ attributes      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
  Person_Entity       Algorithm_Concept   Deterministic_Property
  Task_Entity         Protocol_Concept    Universal_Property
  Document_Entity     Workflow_Concept    One_Time_Property
  ...                 ...                 ...
```

---

# Part 4: Format Terms

## Naming Convention Terms

| Term | Definition |
|------|------------|
| `Naming_Category` | Classification of file naming pattern (A-J) |
| `Domain_Code` | Prefix identifying requirement domain (REL, TPL, TEST) |
| `Category_F` | Standard open-source files (README.md, LICENSE) |
| `Whitelist` | Files exempt from naming validation |

## Versioning Terms

| Term | Definition |
|------|------------|
| `Semver` | Semantic versioning (MAJOR.MINOR.PATCH) |
| `Version_Inventory` | All files containing version strings |
| `Pre_Release_Tag` | Version suffix (-alpha, -beta, -rc) |
| `Version_Consistency` | All repos at same version after release |

## Validation Terms

| Term | Definition |
|------|------------|
| `Validator` | Script that checks compliance |
| `Validation_Mode` | How validator reports (strict, advisory) |
| `Enforcement` | Mechanism for requiring compliance |
| `Planned_Validator` | Validator referenced but not implemented |

---

# Part 5: Contribution Guidelines

## Adding New Terms (G2.4 per L453)

Per **L453 (AGET Ontology Independence)**, AGET vocabulary is self-contained. External ontologies (GM-RKB, SKOS registries) inform but do not constrain contributions.

### Contribution Process

1. **Check existing terms** - Search this spec before proposing new terms
2. **Use minimal entry** - Start with `skos:prefLabel` + `skos:definition`
3. **Add relationships** - Include `skos:broader` if term has clear parent
4. **Submit PR** - Create PR against `aget/specs/AGET_VOCABULARY_SPEC.md`
5. **Review** - Maintainer validates term consistency

### Entry Template

```yaml
New_Term:
  skos:prefLabel: "New_Term"
  skos:definition: "Clear, complete definition in one sentence."
  skos:broader: "Parent_Term"  # Optional
  skos:example: "Usage example"  # Recommended
```

### EKO Terms (L451)

For executable knowledge artifacts, include EKO axes:

```yaml
New_Artifact:
  skos:prefLabel: "New_Artifact"
  skos:definition: "..."
  aget:determinism: "deterministic|probabilistic|syllogistic"
  aget:reusability: "universal|parameterized|one_time"
  aget:naming: "PATTERN_{scope}.md"  # If file-based
```

### Validation

- Terms MUST have `skos:definition`
- Terms SHOULD have `skos:broader` if parent exists
- Term names MUST use Title_Case with underscores
- No external approval gates required (L453)

---

# Part 6: Core Domain Entities (L459, L530)

Core domain entities are standardized foundational entities that AGET agents inherit by default and extend only when domain-specific requirements demand. Per **L459 (Core Entity Vocabulary Vision)**, this addresses the "reinvention anti-pattern" where agents independently define common entities.

**Relationship to Meta-Ontology (L494)**:
- `Aget_Entity` is defined in the Meta-Ontology section as the root meta-term for all domain objects
- This Part 6 extends that meta-definition with the full entity hierarchy and concrete entities

**Relationship to EKO (L451)**:
- EKO defines **executable knowledge** (what Aget_Instances DO) — SOPs, Runbooks, Playbooks
- Core Entity Vocabulary defines **domain objects** (what Aget_Instances WORK WITH) — Aget_Person, Aget_Organization, Aget_Document

**Relationship to Ontology Foundation (L530)**:
- L530 establishes the theoretical grounding for entity categories
- DAG structure allows multi-parent inheritance (e.g., Aget_Person is both Aget_Agent and Aget_Living_Organism)
- Naming convention: All ontology classes use `Aget_*` prefix for self-disambiguation

## Upper-Level Entity Categories

The AGET ontology follows a DAG (Directed Acyclic Graph) structure rooted in `Aget_Thing`. Per L530 Finding 5, DAG allows entities to have multiple parents (e.g., Aget_Person inherits from both Aget_Agent and Aget_Living_Organism).

```yaml
Aget_Thing:
  skos:prefLabel: "Aget_Thing"
  skos:definition: "The universal root class for all AGET ontology entities. Everything in the AGET domain model is an Aget_Thing."
  aget:theoretical_basis: "BFO:Entity (root of Basic Formal Ontology)"
  skos:narrower: ["Aget_Continuant", "Aget_Occurrent", "Aget_Intangible"]
  skos:example: "Every Aget_Person, Aget_Task, and Aget_Rule is an Aget_Thing."

Aget_Continuant:
  skos:prefLabel: "Aget_Continuant"
  skos:altLabel: ["Continuant", "Continuant_Category"]
  skos:definition: "Aget_Thing that persists through time while maintaining identity. Continuants exist wholly at any moment they exist."
  skos:broader: "Aget_Thing"
  aget:theoretical_basis: "BFO:Continuant, DOLCE:Endurant"
  aget:user_facing: false
  skos:narrower: ["Aget_Agent", "Aget_System", "Aget_Artifact", "Aget_CreatedWork"]
  skos:example: "Alice is an Aget_Person (Continuant) — she exists continuously, not as an event."

Aget_Occurrent:
  skos:prefLabel: "Aget_Occurrent"
  skos:altLabel: ["Occurrent", "Occurrent_Category"]
  skos:definition: "Aget_Thing that happens in time, with a beginning and end. Occurrents unfold over time."
  skos:broader: "Aget_Thing"
  aget:theoretical_basis: "BFO:Occurrent, DOLCE:Perdurant"
  aget:user_facing: false
  skos:narrower: ["Aget_Action", "Aget_Event", "Aget_Decision"]
  skos:example: "A meeting is an Aget_Event (Occurrent) — it happens at a specific time."

Aget_Intangible:
  skos:prefLabel: "Aget_Intangible"
  skos:altLabel: ["Intangible", "Abstract", "Abstract_Category"]
  skos:definition: "Aget_Thing that is non-physical and exists as a conceptual construct. Intangibles are neither continuants nor occurrents."
  skos:broader: "Aget_Thing"
  aget:theoretical_basis: "Schema.org:Intangible, BFO:GenericallyDependentContinuant"
  aget:user_facing: false
  skos:narrower: ["Aget_Belief", "Aget_Rule", "Aget_Capability", "Aget_Promise", "Aget_Pattern", "Aget_Goal"]
  skos:example: "A rule is an Aget_Intangible — it exists as a concept, not a physical thing."
  skos:note: "Renamed from 'Abstract' per L530 Finding 4 (readability): 'A rule is an Aget_Intangible' scores 4/5 vs 'A rule is an Aget_Abstract' at 2/5."

# Legacy compatibility mapping
Aget_Entity:
  skos:prefLabel: "Aget_Entity"
  skos:altLabel: "Entity"
  skos:definition: "A distinct, identifiable thing in the domain that can have attributes and relationships. Equivalent to Aget_Thing in the ontology hierarchy."
  aget:meta_entity: true
  skos:related: "Aget_Thing"
  skos:narrower: ["Aget_Continuant", "Aget_Occurrent", "Aget_Intangible"]
  skos:note: "For backward compatibility with L459/L494. New code should use Aget_Thing as root."
```

## Continuant Branch (L530 - Agent-Centric)

The Continuant branch emphasizes **Aget_Agent** as the central AGET concept. Per L530 Lesson 8, the framework starts from Agent and expands outward, rather than assuming generic ontology structure.

### Agent Hierarchy

```yaml
Aget_Agent:
  skos:prefLabel: "Aget_Agent"
  skos:altLabel: ["Agent"]
  skos:definition: "Aget_Continuant capable of autonomous action, possessing beliefs, desires, and intentions (BDI)."
  skos:broader: "Aget_Continuant"
  aget:theoretical_basis: "BDI Architecture (Bratman, Rao & Georgeff), L331"
  aget:core_entity: true
  skos:narrower: ["Aget_Person", "Aget_AI_System", "Aget_Organization"]
  skos:example: "Alice is an Aget_Agent — she can form intentions and take autonomous actions."

Aget_Person:
  skos:prefLabel: "Aget_Person"
  skos:altLabel: ["Person", "Person_Entity"]
  skos:definition: "Aget_Agent that is a human individual. DAG: also an Aget_Living_Organism."
  skos:broader: ["Aget_Agent", "Aget_Living_Organism"]
  aget:theoretical_basis: "BFO:Object, Schema.org:Person"
  aget:core_entity: true
  aget:dag_parents: ["Aget_Agent (primary)", "Aget_Living_Organism (secondary)"]
  skos:example: "Alice is an Aget_Person — both an agent with intentions and a living organism."

Aget_AI_System:
  skos:prefLabel: "Aget_AI_System"
  skos:altLabel: ["AI_System"]
  skos:definition: "Aget_Agent that is an artificial intelligence system. DAG: also an Aget_Technical_System."
  skos:broader: ["Aget_Agent", "Aget_Technical_System"]
  aget:theoretical_basis: "BDI Architecture for artificial agents"
  aget:core_entity: true
  aget:dag_parents: ["Aget_Agent (primary)", "Aget_Technical_System (secondary)"]
  skos:narrower: ["Aget_Instance"]
  skos:example: "Claude is an Aget_AI_System — an agent implemented as a technical system."

Aget_Instance:
  skos:prefLabel: "Aget_Instance"
  skos:altLabel: ["Instance"]
  skos:definition: "Aget_AI_System that is configured using the AGET framework (version.json + AGENTS.md)."
  skos:broader: "Aget_AI_System"
  aget:core_entity: true
  skos:example: "private-aget-framework-AGET is an Aget_Instance — an AI system configured via AGET."

Aget_Organization:
  skos:prefLabel: "Aget_Organization"
  skos:altLabel: ["Organization", "Organization_Entity"]
  skos:definition: "Aget_Agent that is a structured group of agents with a shared purpose."
  skos:broader: "Aget_Agent"
  aget:theoretical_basis: "Schema.org:Organization"
  aget:core_entity: true
  skos:narrower: ["Aget_Team", "Aget_Fleet"]
  skos:example: "Anthropic is an Aget_Organization — a collective agent."

Aget_Team:
  skos:prefLabel: "Aget_Team"
  skos:altLabel: ["Team"]
  skos:definition: "Aget_Organization of persons working together on shared goals."
  skos:broader: "Aget_Organization"
  aget:core_entity: true
  skos:example: "The AGET development team is an Aget_Team."

Aget_Fleet:
  skos:prefLabel: "Aget_Fleet"
  skos:altLabel: ["Fleet"]
  skos:definition: "Aget_Organization of Aget_Instances under coordinator supervision."
  skos:broader: "Aget_Organization"
  aget:core_entity: true
  skos:example: "The 28-agent main portfolio is an Aget_Fleet."
```

### System Hierarchy

```yaml
Aget_System:
  skos:prefLabel: "Aget_System"
  skos:altLabel: ["System"]
  skos:definition: "Aget_Continuant composed of organized, interacting components."
  skos:broader: "Aget_Continuant"
  aget:theoretical_basis: "Systems Theory"
  skos:narrower: ["Aget_Technical_System", "Aget_Biological_System"]
  skos:example: "A computer is an Aget_System — organized components working together."

Aget_Technical_System:
  skos:prefLabel: "Aget_Technical_System"
  skos:altLabel: ["Technical_System"]
  skos:definition: "Aget_System designed and built by agents for a specific purpose."
  skos:broader: "Aget_System"
  skos:narrower: ["Aget_Software_System"]
  skos:example: "A server cluster is an Aget_Technical_System."

Aget_Software_System:
  skos:prefLabel: "Aget_Software_System"
  skos:altLabel: ["Software_System"]
  skos:definition: "Aget_Technical_System implemented in software."
  skos:broader: "Aget_Technical_System"
  skos:example: "The AGET framework is an Aget_Software_System."

Aget_Biological_System:
  skos:prefLabel: "Aget_Biological_System"
  skos:altLabel: ["Biological_System"]
  skos:definition: "Aget_System that is alive or composed of living components."
  skos:broader: "Aget_System"
  skos:narrower: ["Aget_Living_Organism"]
  skos:example: "An ecosystem is an Aget_Biological_System."

Aget_Living_Organism:
  skos:prefLabel: "Aget_Living_Organism"
  skos:altLabel: ["Living_Organism"]
  skos:definition: "Aget_Biological_System that is an individual living entity."
  skos:broader: "Aget_Biological_System"
  skos:narrower: ["Aget_Animal"]
  skos:example: "A tree is an Aget_Living_Organism."

Aget_Animal:
  skos:prefLabel: "Aget_Animal"
  skos:altLabel: ["Animal"]
  skos:definition: "Aget_Living_Organism that is a member of the animal kingdom."
  skos:broader: "Aget_Living_Organism"
  skos:example: "A dog is an Aget_Animal (and potentially an Aget_Agent if we model it that way)."
```

### Artifact Hierarchy

```yaml
Aget_Artifact:
  skos:prefLabel: "Aget_Artifact"
  skos:altLabel: ["Artifact"]
  skos:definition: "Aget_Continuant that is a physical object created by agents."
  skos:broader: "Aget_Continuant"
  aget:theoretical_basis: "BFO:Object, Schema.org:Product"
  skos:narrower: ["Aget_Device", "Aget_Tool"]
  skos:example: "A laptop is an Aget_Artifact."

Aget_Device:
  skos:prefLabel: "Aget_Device"
  skos:altLabel: ["Device"]
  skos:definition: "Aget_Artifact designed to perform specific functions."
  skos:broader: "Aget_Artifact"
  skos:example: "A smartphone is an Aget_Device."

Aget_Tool:
  skos:prefLabel: "Aget_Tool"
  skos:altLabel: ["Tool"]
  skos:definition: "Aget_Artifact used to extend agent capabilities."
  skos:broader: "Aget_Artifact"
  skos:example: "A hammer is an Aget_Tool."
```

### CreatedWork Hierarchy

```yaml
Aget_CreatedWork:
  skos:prefLabel: "Aget_CreatedWork"
  skos:altLabel: ["CreatedWork"]
  skos:definition: "Aget_Continuant that is an informational object created by agents."
  skos:broader: "Aget_Continuant"
  aget:theoretical_basis: "FRBR:Work, Schema.org:CreativeWork"
  aget:display_alias: "Work"
  skos:narrower: ["Aget_Document", "Aget_Specification", "Aget_Code"]
  skos:example: "A research paper is an Aget_CreatedWork."

Aget_Document:
  skos:prefLabel: "Aget_Document"
  skos:altLabel: ["Document", "Document_Entity"]
  skos:definition: "Aget_CreatedWork that is a persistent information artifact."
  skos:broader: "Aget_CreatedWork"
  aget:core_entity: true
  skos:example: "This specification is an Aget_Document."

Aget_Specification:
  skos:prefLabel: "Aget_Specification"
  skos:altLabel: ["Specification"]
  skos:definition: "Aget_Document that defines requirements, formats, or standards."
  skos:broader: "Aget_Document"
  skos:example: "AGET_VOCABULARY_SPEC is an Aget_Specification."

Aget_Code:
  skos:prefLabel: "Aget_Code"
  skos:altLabel: ["Code"]
  skos:definition: "Aget_CreatedWork that is executable or interpretable by machines."
  skos:broader: "Aget_CreatedWork"
  skos:example: "wake_up.py is an Aget_Code artifact."
```

## Occurrent Branch (L530)

The Occurrent branch captures things that happen over time.

```yaml
Aget_Action:
  skos:prefLabel: "Aget_Action"
  skos:altLabel: ["Action"]
  skos:definition: "Aget_Occurrent that is an intentional doing by an agent."
  skos:broader: "Aget_Occurrent"
  aget:theoretical_basis: "BDI:Intention → Action"
  skos:narrower: ["Aget_Task"]
  skos:example: "Committing code is an Aget_Action."

Aget_Task:
  skos:prefLabel: "Aget_Task"
  skos:altLabel: ["Task", "Task_Entity"]
  skos:definition: "Aget_Action that is a unit of work with assignee and status."
  skos:broader: "Aget_Action"
  aget:core_entity: true
  skos:example: "Implement feature X is an Aget_Task."

Aget_Event:
  skos:prefLabel: "Aget_Event"
  skos:altLabel: ["Event", "Event_Entity"]
  skos:definition: "Aget_Occurrent that happens at a specific time, typically involving multiple participants."
  skos:broader: "Aget_Occurrent"
  aget:theoretical_basis: "BFO:Process, Schema.org:Event"
  aget:core_entity: true
  skos:narrower: ["Aget_Meeting", "Aget_Block"]
  skos:example: "A team standup is an Aget_Event."

Aget_Meeting:
  skos:prefLabel: "Aget_Meeting"
  skos:altLabel: ["Meeting"]
  skos:definition: "Aget_Event where agents gather for discussion or coordination."
  skos:broader: "Aget_Event"
  aget:core_entity: true
  skos:example: "The weekly sync is an Aget_Meeting."

Aget_Block:
  skos:prefLabel: "Aget_Block"
  skos:altLabel: ["Block", "TimeBlock", "FocusBlock"]
  skos:definition: "Aget_Event representing a reserved time period for focused work."
  skos:broader: "Aget_Event"
  aget:display_alias: "Focus Block"
  skos:example: "A 2-hour deep work block is an Aget_Block."

Aget_Decision:
  skos:prefLabel: "Aget_Decision"
  skos:altLabel: ["Decision", "Decision_Entity"]
  skos:definition: "Aget_Occurrent where an agent commits to a choice, creating obligations or beliefs."
  skos:broader: "Aget_Occurrent"
  aget:theoretical_basis: "BDI: Belief + Desire → Intention (Decision)"
  aget:core_entity: true
  skos:example: "Choosing REST over GraphQL is an Aget_Decision."
```

## Intangible Branch (L530 - Extended Research)

The Intangible branch captures conceptual constructs including beliefs, rules, promises, and their consequences. Per L530 Findings 7-10, this branch integrates deontic logic, contract theory, and epistemology.

### Belief and Epistemology Hierarchy (L530 Finding 10)

Per Justified True Belief (JTB) and AGM Belief Revision theory:

```yaml
Aget_Belief:
  skos:prefLabel: "Aget_Belief"
  skos:altLabel: ["Belief"]
  skos:definition: "Aget_Intangible representing an agent's acceptance that a proposition is true."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "BDI Architecture (B component), AGM Belief Revision"
  aget:core_entity: true
  skos:narrower: ["Aget_Assumption", "Aget_Hypothesis", "Aget_Conviction"]
  aget:attributes:
    - confidence: {type: float, range: "[0,1]", description: "Bayesian credence level"}
    - truth_status: {type: enum, values: [unknown, verified_true, verified_false]}
  skos:example: "Alice believes the meeting starts at 3pm."

Aget_Assumption:
  skos:prefLabel: "Aget_Assumption"
  skos:altLabel: ["Assumption"]
  skos:definition: "Aget_Belief that is accepted without verification."
  skos:broader: "Aget_Belief"
  skos:example: "Assuming the API will respond within 100ms."

Aget_Hypothesis:
  skos:prefLabel: "Aget_Hypothesis"
  skos:altLabel: ["Hypothesis"]
  skos:definition: "Aget_Belief that is testable and falsifiable."
  skos:broader: "Aget_Belief"
  aget:theoretical_basis: "Scientific Method, Popperian Falsificationism"
  skos:example: "The hypothesis that caching will improve latency by 50%."

Aget_Conviction:
  skos:prefLabel: "Aget_Conviction"
  skos:altLabel: ["Conviction"]
  skos:definition: "Aget_Belief held with high confidence, resistant to revision."
  skos:broader: "Aget_Belief"
  skos:example: "A core conviction that code should be tested before deployment."

Aget_Knowledge:
  skos:prefLabel: "Aget_Knowledge"
  skos:altLabel: ["Knowledge"]
  skos:definition: "Aget_Intangible that is a justified true belief — Belief + Verified True + Justified."
  skos:broader: "Aget_Intangible"
  skos:related: ["Aget_Belief", "Aget_Justification"]
  aget:theoretical_basis: "Justified True Belief (JTB), Gettier Problem awareness"
  aget:core_entity: true
  skos:example: "Knowledge that the build passed (verified by CI)."

Aget_Justification:
  skos:prefLabel: "Aget_Justification"
  skos:altLabel: ["Justification"]
  skos:definition: "Aget_Intangible providing epistemic support for a belief."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Epistemology, Evidence Theory"
  skos:narrower: ["Aget_Evidence", "Aget_Testimony", "Aget_Inference"]
  skos:example: "The justification for believing the test passed is the green CI badge."

Aget_Evidence:
  skos:prefLabel: "Aget_Evidence"
  skos:altLabel: ["Evidence"]
  skos:definition: "Aget_Justification based on direct observation or data."
  skos:broader: "Aget_Justification"
  skos:example: "Log output showing successful completion."

Aget_Testimony:
  skos:prefLabel: "Aget_Testimony"
  skos:altLabel: ["Testimony"]
  skos:definition: "Aget_Justification based on another agent's assertion."
  skos:broader: "Aget_Justification"
  skos:example: "Alice said the feature was deployed."

Aget_Inference:
  skos:prefLabel: "Aget_Inference"
  skos:altLabel: ["Inference"]
  skos:definition: "Aget_Justification derived from reasoning over other beliefs."
  skos:broader: "Aget_Justification"
  skos:example: "Inferring the system is down because the health check failed."
```

### Rule and Deontic Hierarchy (L530 Finding 7)

Per Standard Deontic Logic (von Wright):

```yaml
Aget_Rule:
  skos:prefLabel: "Aget_Rule"
  skos:altLabel: ["Rule"]
  skos:definition: "Aget_Intangible that prescribes, permits, or prohibits behavior."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Deontic Logic"
  skos:narrower: ["Aget_Constraint", "Aget_Norm"]
  skos:example: "A rule that all commits must have tests."

Aget_Constraint:
  skos:prefLabel: "Aget_Constraint"
  skos:altLabel: ["Constraint"]
  skos:definition: "Aget_Rule that limits possible states or actions."
  skos:broader: "Aget_Rule"
  skos:example: "A constraint that file names must be lowercase."

Aget_Norm:
  skos:prefLabel: "Aget_Norm"
  skos:altLabel: ["Norm"]
  skos:definition: "Aget_Rule with deontic force (obligation, prohibition, or permission)."
  skos:broader: "Aget_Rule"
  aget:theoretical_basis: "Standard Deontic Logic (von Wright)"
  aget:core_entity: true
  skos:narrower: ["Aget_Obligation", "Aget_Prohibition", "Aget_Permission"]
  skos:example: "A norm that agents SHALL document decisions."

Aget_Obligation:
  skos:prefLabel: "Aget_Obligation"
  skos:altLabel: ["Obligation", "SHALL"]
  skos:definition: "Aget_Norm requiring an action or state (deontic SHALL)."
  skos:broader: "Aget_Norm"
  aget:theoretical_basis: "Deontic Logic: O(p) — it ought to be that p"
  aget:deontic_operator: "SHALL"
  aget:hohfeldian_correlative: "Aget_Right"
  skos:example: "Agents SHALL run V-tests before marking gates complete."

Aget_Prohibition:
  skos:prefLabel: "Aget_Prohibition"
  skos:altLabel: ["Prohibition", "SHALL_NOT"]
  skos:definition: "Aget_Norm forbidding an action or state (deontic SHALL NOT)."
  skos:broader: "Aget_Norm"
  aget:theoretical_basis: "Deontic Logic: F(p) — it is forbidden that p"
  aget:deontic_operator: "SHALL NOT"
  skos:example: "Agents SHALL NOT commit secrets to public repositories."

Aget_Permission:
  skos:prefLabel: "Aget_Permission"
  skos:altLabel: ["Permission", "MAY"]
  skos:definition: "Aget_Norm allowing an action or state (deontic MAY)."
  skos:broader: "Aget_Norm"
  aget:theoretical_basis: "Deontic Logic: P(p) — it is permitted that p"
  aget:deontic_operator: "MAY"
  aget:hohfeldian_equivalent: "Aget_Privilege"
  skos:example: "Agents MAY use abbreviated commit messages for trivial fixes."

Aget_Capability:
  skos:prefLabel: "Aget_Capability"
  skos:altLabel: ["Capability"]
  skos:definition: "Aget_Intangible representing an agent's ability to perform actions. NOT deontic — about CAN, not MAY."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Ability vs Permission distinction (L530 Finding 7)"
  aget:core_entity: true
  skos:note: "Capability is about Ability (CAN), not Permission (MAY). Initial intuition to place under Rule was incorrect."
  skos:example: "The capability to execute bash commands."
```

### Promise and Commitment Hierarchy (L530 Finding 8)

Per Speech Act Theory (Austin, Searle):

```yaml
Aget_Promise:
  skos:prefLabel: "Aget_Promise"
  skos:altLabel: ["Promise"]
  skos:definition: "Aget_Intangible representing a commitment to future action made by an agent."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Speech Act Theory (Searle: Commissives)"
  skos:narrower: ["Aget_Commitment"]
  skos:example: "A promise to deliver the feature by Friday."

Aget_Commitment:
  skos:prefLabel: "Aget_Commitment"
  skos:altLabel: ["Commitment"]
  skos:definition: "Aget_Promise that has been formalized, creating obligations."
  skos:broader: "Aget_Promise"
  aget:theoretical_basis: "BDI Architecture (Intention as Commitment)"
  aget:core_entity: true
  skos:example: "A commitment tracked in the project plan."
```

### Agreement and Contract Hierarchy (L530 Finding 8)

Per Hohfeldian Positions and UFO-L:

```yaml
Aget_Agreement:
  skos:prefLabel: "Aget_Agreement"
  skos:altLabel: ["Agreement"]
  skos:definition: "Aget_Intangible representing mutual commitments between agents."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Contract Theory, UFO-L"
  skos:narrower: ["Aget_Contract"]
  skos:example: "An agreement to share code review responsibilities."

Aget_Contract:
  skos:prefLabel: "Aget_Contract"
  skos:altLabel: ["Contract"]
  skos:definition: "Aget_Agreement with formal obligations, rights, and consequences."
  skos:broader: "Aget_Agreement"
  aget:theoretical_basis: "Legal Ontology, FIBO"
  skos:example: "A service level agreement (SLA)."

Aget_Right:
  skos:prefLabel: "Aget_Right"
  skos:altLabel: ["Right"]
  skos:definition: "Aget_Intangible representing an entitlement correlative to another's obligation."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Hohfeldian Positions: Right-Duty correlation"
  aget:hohfeldian_correlative: "Aget_Obligation"
  skos:example: "The right to receive code review within 24 hours."

Aget_Power:
  skos:prefLabel: "Aget_Power"
  skos:altLabel: ["Power"]
  skos:definition: "Aget_Intangible representing the ability to create, modify, or extinguish rights."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Hohfeldian Positions: Power-Liability"
  skos:example: "The power to approve or reject a pull request."
```

### Consequence Hierarchy (L530 Finding 9)

Per Speech Act Theory (consequences of commitments):

```yaml
Aget_Consequence:
  skos:prefLabel: "Aget_Consequence"
  skos:altLabel: ["Consequence"]
  skos:definition: "Aget_Intangible representing outcomes resulting from actions or commitments."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "Speech Act Theory, Contract Theory"
  skos:narrower: ["Aget_Sanction", "Aget_Reward", "Aget_Breach", "Aget_Fulfillment"]
  aget:impact_dimensions: ["self_impact", "relational_impact", "organizational_impact", "financial_impact", "emotional_impact", "reputational_impact"]
  skos:example: "The consequence of missing a deadline."

Aget_Sanction:
  skos:prefLabel: "Aget_Sanction"
  skos:altLabel: ["Sanction"]
  skos:definition: "Aget_Consequence that is a negative outcome for breach of obligation."
  skos:broader: "Aget_Consequence"
  skos:related: "Aget_Breach"
  skos:example: "Loss of commit privileges after repeated policy violations."

Aget_Reward:
  skos:prefLabel: "Aget_Reward"
  skos:altLabel: ["Reward"]
  skos:definition: "Aget_Consequence that is a positive outcome for fulfillment of commitment."
  skos:broader: "Aget_Consequence"
  skos:related: "Aget_Fulfillment"
  skos:example: "Recognition for completing a difficult migration."

Aget_Breach:
  skos:prefLabel: "Aget_Breach"
  skos:altLabel: ["Breach"]
  skos:definition: "Aget_Consequence representing violation of an agreement or obligation."
  skos:broader: "Aget_Consequence"
  skos:related: ["Aget_Agreement", "Aget_Obligation", "Aget_Sanction"]
  skos:example: "Breach of SLA by exceeding response time limits."

Aget_Fulfillment:
  skos:prefLabel: "Aget_Fulfillment"
  skos:altLabel: ["Fulfillment"]
  skos:definition: "Aget_Consequence representing satisfaction of an agreement or commitment."
  skos:broader: "Aget_Consequence"
  skos:related: ["Aget_Agreement", "Aget_Commitment", "Aget_Reward"]
  skos:example: "Fulfillment of the release commitment by shipping on schedule."
```

### Additional Intangible Classes

```yaml
Aget_Pattern:
  skos:prefLabel: "Aget_Pattern"
  skos:altLabel: ["Pattern"]
  skos:definition: "Aget_Intangible representing a reusable solution to a recurring problem."
  skos:broader: "Aget_Intangible"
  aget:core_entity: true
  skos:example: "The gate verification test pattern."

Aget_Project:
  skos:prefLabel: "Aget_Project"
  skos:altLabel: ["Project", "Project_Entity"]
  skos:definition: "Aget_Intangible representing a planned initiative with goals and timeline."
  skos:broader: "Aget_Intangible"
  aget:core_entity: true
  skos:example: "The AGET Ontology Foundation project."

Aget_Goal:
  skos:prefLabel: "Aget_Goal"
  skos:altLabel: ["Goal"]
  skos:definition: "Aget_Intangible representing a desired future state an agent intends to achieve."
  skos:broader: "Aget_Intangible"
  aget:theoretical_basis: "BDI Architecture (D component - Desire/Goal)"
  aget:core_entity: true
  skos:example: "The goal to release v3.5.0 by end of quarter."
```

## DAG Relationship Summary

Per L530 Finding 5, the following entities have multiple parents:

| Entity | Primary Parent | Secondary Parent |
|--------|----------------|------------------|
| Aget_Person | Aget_Agent | Aget_Living_Organism |
| Aget_AI_System | Aget_Agent | Aget_Technical_System |

## Legacy Core Entity Definitions

The following definitions maintain backward compatibility with L459. New implementations should use the Aget_* prefixed versions above.

### Person_Entity

```yaml
Person_Entity:
  skos:prefLabel: "Person_Entity"
  skos:altLabel: "Person"
  skos:definition: "A human individual participating in a system or process."
  skos:broader: "Continuant_Category"
  aget:core_entity: true
  aget:attributes:
    - name:
        type: string
        required: true
        description: "Full name of the person"
    - email:
        type: string
        format: email
        description: "Primary contact email"
    - identifier:
        type: string
        description: "External identifier (ORCID, employee ID, etc.)"
    - roles:
        type: array
        items: string
        description: "Roles held by this person"
  aget:relationships:
    - affiliated_with:
        target: Organization_Entity
        cardinality: "0:many"
        inverse: has_member
    - authors:
        target: Document_Entity
        cardinality: "0:many"
        inverse: authored_by
    - makes:
        target: Decision_Entity
        cardinality: "0:many"
        inverse: made_by
    - assigned_to:
        target: Task_Entity
        cardinality: "0:many"
        inverse: assignee
```

### Organization_Entity

```yaml
Organization_Entity:
  skos:prefLabel: "Organization_Entity"
  skos:altLabel: "Organization"
  skos:definition: "A structured group of persons with a shared purpose."
  skos:broader: "Continuant_Category"
  aget:core_entity: true
  aget:attributes:
    - name:
        type: string
        required: true
        description: "Official name of the organization"
    - type:
        type: enum
        values: [company, team, department, agency, consortium, community]
        description: "Classification of organization type"
    - identifier:
        type: string
        description: "External identifier (DUNS, EIN, etc.)"
  aget:relationships:
    - has_member:
        target: Person_Entity
        cardinality: "0:many"
        inverse: affiliated_with
    - owns:
        target: Project_Entity
        cardinality: "0:many"
        inverse: owned_by
    - produces:
        target: Document_Entity
        cardinality: "0:many"
        inverse: produced_by
    - parent_of:
        target: Organization_Entity
        cardinality: "0:many"
        inverse: child_of
```

### Document_Entity

```yaml
Document_Entity:
  skos:prefLabel: "Document_Entity"
  skos:altLabel: "Document"
  skos:definition: "A persistent information artifact that can be referenced and versioned."
  skos:broader: "Continuant_Category"
  aget:core_entity: true
  aget:attributes:
    - title:
        type: string
        required: true
        description: "Document title"
    - type:
        type: enum
        values: [spec, plan, report, record, correspondence, artifact]
        description: "Document classification"
    - version:
        type: string
        description: "Version identifier"
    - location:
        type: uri
        description: "Canonical location (file path or URL)"
    - created:
        type: date
        description: "Creation date"
    - status:
        type: enum
        values: [draft, active, archived, superseded]
        description: "Document lifecycle status"
  aget:relationships:
    - authored_by:
        target: Person_Entity
        cardinality: "1:many"
        inverse: authors
    - produced_by:
        target: Organization_Entity
        cardinality: "0:1"
        inverse: produces
    - references:
        target: Document_Entity
        cardinality: "0:many"
        inverse: referenced_by
    - supersedes:
        target: Document_Entity
        cardinality: "0:1"
        inverse: superseded_by
```

### Decision_Entity

```yaml
Decision_Entity:
  skos:prefLabel: "Decision_Entity"
  skos:altLabel: "Decision"
  skos:definition: "A choice made by persons that affects future actions or states."
  skos:broader: "Abstract_Category"
  aget:core_entity: true
  aget:attributes:
    - description:
        type: string
        required: true
        description: "What was decided"
    - date:
        type: date
        required: true
        description: "When the decision was made"
    - rationale:
        type: string
        description: "Why this decision was made"
    - status:
        type: enum
        values: [proposed, approved, rejected, superseded, implemented]
        description: "Decision lifecycle status"
  aget:relationships:
    - made_by:
        target: Person_Entity
        cardinality: "1:many"
        inverse: makes
    - affects:
        target: Requirement_Entity
        cardinality: "0:many"
    - documented_in:
        target: Document_Entity
        cardinality: "0:1"
    - supersedes:
        target: Decision_Entity
        cardinality: "0:1"
```

### Event_Entity

```yaml
Event_Entity:
  skos:prefLabel: "Event_Entity"
  skos:altLabel: "Event"
  skos:definition: "Something that happens at a specific time, with a beginning and end."
  skos:broader: "Occurrent_Category"
  aget:core_entity: true
  aget:attributes:
    - name:
        type: string
        required: true
        description: "Event name or title"
    - type:
        type: enum
        values: [meeting, release, incident, milestone, review]
        description: "Event classification"
    - start_time:
        type: datetime
        description: "When the event began"
    - end_time:
        type: datetime
        description: "When the event ended"
    - status:
        type: enum
        values: [planned, in_progress, completed, cancelled]
        description: "Event status"
  aget:relationships:
    - involves:
        target: Person_Entity
        cardinality: "0:many"
    - hosted_by:
        target: Organization_Entity
        cardinality: "0:1"
    - produces:
        target: Document_Entity
        cardinality: "0:many"
    - results_in:
        target: Decision_Entity
        cardinality: "0:many"
```

### Task_Entity

```yaml
Task_Entity:
  skos:prefLabel: "Task_Entity"
  skos:altLabel: "Task"
  skos:definition: "A unit of work to be completed, with assignee and status."
  skos:broader: "Occurrent_Category"
  aget:core_entity: true
  aget:attributes:
    - description:
        type: string
        required: true
        description: "What needs to be done"
    - status:
        type: enum
        values: [pending, in_progress, completed, blocked, cancelled]
        description: "Task status"
    - priority:
        type: enum
        values: [low, medium, high, critical]
        description: "Task priority"
    - due_date:
        type: date
        description: "When the task should be completed"
  aget:relationships:
    - assignee:
        target: Person_Entity
        cardinality: "0:many"
        inverse: assigned_to
    - part_of:
        target: Project_Entity
        cardinality: "0:1"
    - blocked_by:
        target: Task_Entity
        cardinality: "0:many"
    - implements:
        target: Requirement_Entity
        cardinality: "0:many"
```

### Project_Entity

```yaml
Project_Entity:
  skos:prefLabel: "Project_Entity"
  skos:altLabel: "Project"
  skos:definition: "A planned initiative with goals, timeline, and resources."
  skos:broader: "Continuant_Category"
  aget:core_entity: true
  aget:attributes:
    - name:
        type: string
        required: true
        description: "Project name"
    - description:
        type: string
        description: "Project description and goals"
    - status:
        type: enum
        values: [proposed, active, completed, on_hold, cancelled]
        description: "Project status"
    - start_date:
        type: date
        description: "Project start date"
    - end_date:
        type: date
        description: "Project end date or target"
  aget:relationships:
    - owned_by:
        target: Organization_Entity
        cardinality: "0:1"
        inverse: owns
    - has_task:
        target: Task_Entity
        cardinality: "0:many"
        inverse: part_of
    - has_requirement:
        target: Requirement_Entity
        cardinality: "0:many"
    - produces:
        target: Document_Entity
        cardinality: "0:many"
```

### Requirement_Entity

```yaml
Requirement_Entity:
  skos:prefLabel: "Requirement_Entity"
  skos:altLabel: "Requirement"
  skos:definition: "A condition or capability needed to satisfy a goal or contract."
  skos:broader: "Abstract_Category"
  aget:core_entity: true
  aget:attributes:
    - identifier:
        type: string
        required: true
        description: "Requirement ID (e.g., REQ-001, CAP-REL-001)"
    - description:
        type: string
        required: true
        description: "What is required"
    - type:
        type: enum
        values: [functional, non_functional, constraint, interface]
        description: "Requirement classification"
    - priority:
        type: enum
        values: [must, should, may, wont]
        description: "MoSCoW priority"
    - status:
        type: enum
        values: [proposed, approved, implemented, verified, deferred]
        description: "Requirement lifecycle status"
  aget:relationships:
    - source:
        target: Person_Entity
        cardinality: "0:many"
        description: "Who requested this requirement"
    - implemented_by:
        target: Task_Entity
        cardinality: "0:many"
        inverse: implements
    - verified_by:
        target: Document_Entity
        cardinality: "0:many"
        description: "Test or verification evidence"
```

## Entity Inheritance Mechanism

Agents declare entity usage in `manifest.yaml`:

```yaml
# Agent's manifest.yaml
entities:
  inherits:           # List of core entities to inherit
    - Person
    - Organization
    - Document

  extends:            # Domain-specific extensions
    Person:
      attributes:
        - bar_number: {type: string, description: "State bar license"}
        - jurisdiction: {type: string, description: "Licensing jurisdiction"}
    Document:
      attributes:
        - confidentiality: {type: enum, values: [public, confidential, privileged]}
      relationships:
        - subject_of: {target: Legal_Matter, cardinality: "0:many"}
```

### Inheritance Rules

| Rule ID | Rule | Description |
|---------|------|-------------|
| R-ENT-001 | Inherited entities include all base attributes | Cannot remove base attributes |
| R-ENT-002 | Extensions add attributes, cannot remove | Additive only |
| R-ENT-003 | Extensions can add relationships | New connections allowed |
| R-ENT-004 | Extensions can narrow types | string → enum allowed, not vice versa |
| R-ENT-005 | Extended entities remain compatible | Consumers of base can consume extended |

## Entity Summary Table

| Entity | Category | Required Attributes | Key Relationships |
|--------|----------|---------------------|-------------------|
| **Person** | Continuant | name | affiliated_with, authors, makes, assigned_to |
| **Organization** | Continuant | name | has_member, owns, produces, parent_of |
| **Document** | Continuant | title | authored_by, produced_by, references, supersedes |
| **Decision** | Abstract | description, date | made_by, affects, documented_in |
| **Event** | Occurrent | name | involves, hosted_by, produces, results_in |
| **Task** | Occurrent | description | assignee, part_of, blocked_by, implements |
| **Project** | Continuant | name | owned_by, has_task, has_requirement, produces |
| **Requirement** | Abstract | identifier, description | source, implemented_by, verified_by |

---

# Part 7: Standards Document Ontology

This part elevates AGET standards documents (specifications, SOPs, templates, learnings) as first-class ontology entities. Per **PROJECT_PLAN_standards_ontology_elevation_v1.0**, this enables queryable relationships between documents and the concepts they define.

## Document Type Hierarchy

```
Document_Entity (Part 6)
├── Normative_Document
│   ├── Specification_Document (CANONICAL > Active > Draft > Deprecated)
│   ├── SOP_Document
│   └── Template_Document
├── Informative_Document
│   ├── Guide_Document
│   ├── Pattern_Document
│   └── Learning_Document (observation > recommendation > advisory > enforced)
└── Process_Document
    ├── Project_Plan_Document
    ├── Session_Document
    └── Handoff_Document
```

## Authority Model

| Level | Meaning | Mutation Allowed | Examples |
|-------|---------|------------------|----------|
| **CANONICAL** | Immutable reference standard | Major version only | AGET_SPEC_FORMAT, AGET_FILE_NAMING_CONVENTIONS |
| **Active** | Current normative | Minor/patch allowed | AGET_TEMPLATE_SPEC, AGET_VOCABULARY_SPEC |
| **Draft** | Under development | Any change | New specs before approval |
| **Deprecated** | Superseded, read-only | None | AGET_GLOSSARY_STANDARD_SPEC (archived) |

## Traceability Properties

| Property | Definition | Example |
|----------|------------|---------|
| `aget:defines` | Specification → Terms it defines | AGET_VOCABULARY_SPEC defines V_Test |
| `aget:implements` | SOP → Spec requirements it implements | SOP_release_process implements CAP-REL-* |
| `aget:supersedes` | Document → Document it replaces | AGET_VOCABULARY_SPEC supersedes AGET_GLOSSARY_STANDARD_SPEC |
| `aget:governed_by` | Any document → Spec that governs it | PROJECT_PLAN governed_by AGET_PROJECT_PLAN_SPEC |

## Document Type Definitions

### Normative_Document

```yaml
Normative_Document:
  skos:prefLabel: "Normative_Document"
  skos:definition: "Document that establishes requirements, standards, or authoritative guidance that MUST or SHOULD be followed."
  skos:broader: "Document_Entity"
  skos:narrower: ["Specification_Document", "SOP_Document", "Template_Document"]
  skos:example: "AGET_FRAMEWORK_SPEC.md, SOP_release_process.md"
```

### Specification_Document

```yaml
Specification_Document:
  skos:prefLabel: "Specification_Document"
  skos:definition: "Formal document defining requirements, formats, or standards using EARS patterns and CAP-{DOMAIN}-{NNN} requirement IDs."
  skos:broader: "Normative_Document"
  aget:authority_levels: ["CANONICAL", "Active", "Draft", "Deprecated"]
  aget:naming_pattern: "{NAME}_SPEC.md or {NAME}_SPEC_v{M}.{m}.md"
  aget:location: "aget/specs/"
  skos:narrower: []  # Populated with spec instances in Part 7.4
  skos:example: "AGET_VOCABULARY_SPEC.md, AGET_TEMPLATE_SPEC.md"
```

### SOP_Document

```yaml
SOP_Document:
  skos:prefLabel: "SOP_Document"
  skos:definition: "Standard Operating Procedure document defining repeatable processes with Purpose, Scope, and Procedure sections."
  skos:broader: "Normative_Document"
  aget:determinism: "deterministic"
  aget:reusability: "universal"
  aget:naming_pattern: "SOP_{snake_case}.md"
  aget:location: "aget/sops/ or sops/"
  aget:required_sections: ["Purpose", "Scope"]
  skos:example: "SOP_release_process.md, SOP_fleet_migration.md"
```

### Template_Document

```yaml
Template_Document:
  skos:prefLabel: "Template_Document"
  skos:definition: "Reusable document pattern providing structure for creating conformant artifacts."
  skos:broader: "Normative_Document"
  aget:naming_pattern: "{NAME}_TEMPLATE.md or TEMPLATE_{name}.md"
  aget:location: "aget/templates/ or docs/templates/"
  skos:example: "PROJECT_PLAN_TEMPLATE.md, ADR_TEMPLATE.md, SPEC_TEMPLATE_v3.3.md"
```

### Informative_Document

```yaml
Informative_Document:
  skos:prefLabel: "Informative_Document"
  skos:definition: "Document that provides guidance, patterns, or knowledge without establishing requirements."
  skos:broader: "Document_Entity"
  skos:narrower: ["Guide_Document", "Pattern_Document", "Learning_Document"]
  skos:example: "GETTING_STARTED.md, PATTERN_gate_verification_tests.md, L459_core_entity_vocabulary.md"
```

### Guide_Document

```yaml
Guide_Document:
  skos:prefLabel: "Guide_Document"
  skos:definition: "Instructional document explaining how to accomplish tasks or use features."
  skos:broader: "Informative_Document"
  aget:naming_pattern: "{NAME}_GUIDE.md or GUIDE_{name}.md"
  skos:example: "GETTING_STARTED.md, FLEET_MIGRATION_GUIDE.md, ENTITY_EXTENSION_GUIDE.md"
```

### Pattern_Document

```yaml
Pattern_Document:
  skos:prefLabel: "Pattern_Document"
  skos:definition: "Document describing a reusable solution to a recurring problem in a specific context."
  skos:broader: "Informative_Document"
  aget:naming_pattern: "PATTERN_{snake_case}.md"
  aget:location: "docs/patterns/"
  skos:example: "PATTERN_gate_verification_tests.md, PATTERN_step_back_review_kb.md"
```

### Learning_Document

```yaml
Learning_Document:
  skos:prefLabel: "Learning_Document"
  skos:altLabel: ["L_Doc", "L-doc"]
  skos:definition: "Experiential knowledge capture with structured YAML frontmatter documenting discoveries, decisions, or patterns."
  skos:broader: "Informative_Document"
  aget:naming_pattern: "L{NNN}_{snake_case}.md"
  aget:location: ".aget/evolution/"
  aget:enforcement_progression: ["observation", "recommendation", "advisory", "enforced"]
  aget:numbering_scope: "per-agent"
  skos:example: "L459_core_entity_vocabulary.md, L493_vocabulary_prose_marking.md"
```

### Process_Document

```yaml
Process_Document:
  skos:prefLabel: "Process_Document"
  skos:definition: "Document supporting workflow execution with temporal scope (sessions, projects, handoffs)."
  skos:broader: "Document_Entity"
  skos:narrower: ["Project_Plan_Document", "Session_Document", "Handoff_Document"]
  skos:example: "PROJECT_PLAN_v3.2.0.md, session_2026-01-12_0930.md"
```

### Project_Plan_Document

```yaml
Project_Plan_Document:
  skos:prefLabel: "Project_Plan_Document"
  skos:altLabel: ["PROJECT_PLAN"]
  skos:definition: "Formal gated execution plan with objectives, deliverables, V-tests, and decision points."
  skos:broader: "Process_Document"
  aget:determinism: "syllogistic"
  aget:reusability: "one_time"
  aget:naming_pattern: "PROJECT_PLAN_{scope}_v{M}.{m}.md"
  aget:location: "planning/"
  aget:governed_by: "AGET_PROJECT_PLAN_SPEC"
  skos:example: "PROJECT_PLAN_v3.2.0_specification_architecture.md"
```

### Session_Document

```yaml
Session_Document:
  skos:prefLabel: "Session_Document"
  skos:definition: "Document capturing session state, pending work, and handoff context for continuity."
  skos:broader: "Process_Document"
  aget:naming_pattern: "session_{YYYY-MM-DD}_{HHMM}.md"
  aget:location: "sessions/"
  aget:governed_by: "AGET_SESSION_SPEC"
  skos:example: "session_2026-01-12_0930.md"
```

### Handoff_Document

```yaml
Handoff_Document:
  skos:prefLabel: "Handoff_Document"
  skos:definition: "Document facilitating transfer of context between sessions, agents, or releases."
  skos:broader: "Process_Document"
  aget:naming_pattern: "RELEASE_HANDOFF_v{M}.{m}.{p}.md or HANDOFF_{context}.md"
  aget:location: "handoffs/"
  skos:example: "RELEASE_HANDOFF_v3.3.0.md"
```

## Document Type Summary Table

| Document Type | Category | Authority/Enforcement | Location | Naming Pattern |
|---------------|----------|----------------------|----------|----------------|
| **Specification_Document** | Normative | CANONICAL/Active/Draft/Deprecated | aget/specs/ | {NAME}_SPEC.md |
| **SOP_Document** | Normative | Active | aget/sops/ | SOP_{name}.md |
| **Template_Document** | Normative | Active | aget/templates/ | {NAME}_TEMPLATE.md |
| **Guide_Document** | Informative | N/A | aget/docs/ | {NAME}_GUIDE.md |
| **Pattern_Document** | Informative | N/A | docs/patterns/ | PATTERN_{name}.md |
| **Learning_Document** | Informative | observation→enforced | .aget/evolution/ | L{NNN}_{name}.md |
| **Project_Plan_Document** | Process | One-time | planning/ | PROJECT_PLAN_{scope}_v{M}.{m}.md |
| **Session_Document** | Process | One-time | sessions/ | session_{date}_{time}.md |
| **Handoff_Document** | Process | One-time | handoffs/ | HANDOFF_{context}.md |

## Specification Instances (Exemplars)

The following entries demonstrate specification documents as first-class ontology entities with `aget:defines` traceability.

### AGET_VOCABULARY_SPEC

```yaml
AGET_VOCABULARY_SPEC:
  skos:prefLabel: "AGET_VOCABULARY_SPEC"
  skos:definition: "Consolidated vocabulary standards and controlled terminology for the AGET framework, including SKOS foundation, core terms, domain terms, and standards document ontology."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-VOC-001"
  aget:authority: "Active"
  aget:version: "1.8.0"
  aget:location: "aget/specs/AGET_VOCABULARY_SPEC.md"
  aget:defines:
    - "V_Test"
    - "Declarative_Completion"
    - "Verified_Completion"
    - "Aget_Entity"
    - "Aget_Concept"
    - "Aget_Property"
    - "Aget_Specification"
    - "Specification_Document"
    - "SOP_Document"
    - "Learning_Document"
  aget:supersedes: "AGET_GLOSSARY_STANDARD_SPEC"
```

### AGET_TEMPLATE_SPEC

```yaml
AGET_TEMPLATE_SPEC:
  skos:prefLabel: "AGET_TEMPLATE_SPEC"
  skos:definition: "Template architecture specification defining 5D composition, manifest schemas, and archetype requirements for AGET templates."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-TPL-001"
  aget:authority: "Active"
  aget:version: "3.3.1"
  aget:location: "aget/specs/AGET_TEMPLATE_SPEC.md"
  aget:defines:
    - "Aget_Template"
    - "Aget_Instance"
    - "Core_Template"
    - "Specialized_Template"
```

### AGET_SPEC_FORMAT

```yaml
AGET_SPEC_FORMAT:
  skos:prefLabel: "AGET_SPEC_FORMAT"
  skos:definition: "CANONICAL specification format defining EARS-based requirement patterns, header structure, and conformance levels for all AGET specifications."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-FMT-001"
  aget:authority: "CANONICAL"
  aget:version: "1.2"
  aget:location: "aget/specs/AGET_SPEC_FORMAT.md"
  aget:defines:
    - "CAP requirement pattern"
    - "EARS patterns (ubiquitous, event-driven, state-driven, optional, conditional)"
```

### AGET_FILE_NAMING_CONVENTIONS

```yaml
AGET_FILE_NAMING_CONVENTIONS:
  skos:prefLabel: "AGET_FILE_NAMING_CONVENTIONS"
  skos:definition: "CANONICAL file naming conventions defining naming patterns for all AGET artifact categories (A-J)."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-NAME-001"
  aget:authority: "CANONICAL"
  aget:version: "2.1.0"
  aget:location: "aget/specs/AGET_FILE_NAMING_CONVENTIONS.md"
  aget:defines:
    - "Naming_Category"
    - "Category A-J patterns"
    - "L-doc numbering"
    - "ADR numbering"
```

### AGET_PROJECT_PLAN_SPEC

```yaml
AGET_PROJECT_PLAN_SPEC:
  skos:prefLabel: "AGET_PROJECT_PLAN_SPEC"
  skos:definition: "Specification defining PROJECT_PLAN requirements including gate structure, V-tests, decision points, and closure checklist."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-PP-001"
  aget:authority: "Active"
  aget:version: "1.1.0"
  aget:location: "aget/specs/AGET_PROJECT_PLAN_SPEC.md"
  aget:defines:
    - "PROJECT_PLAN"
    - "Gate"
    - "V_Test"
    - "Decision_Point"
    - "Project Closure Checklist"
  aget:governed_by: "AGET_SPEC_FORMAT"
```

### AGET_SOP_SPEC

```yaml
AGET_SOP_SPEC:
  skos:prefLabel: "AGET_SOP_SPEC"
  skos:definition: "Specification defining Standard Operating Procedure requirements including required sections and vocabulary compliance."
  skos:broader: "Specification_Document"
  aget:spec_id: "AGET-SOP-001"
  aget:authority: "Active"
  aget:version: "1.1.0"
  aget:location: "aget/specs/AGET_SOP_SPEC.md"
  aget:defines:
    - "SOP_Document"
    - "Purpose section"
    - "Scope section"
  aget:governed_by: "AGET_SPEC_FORMAT"
```

---

# Part 8: Agent Capabilities Vocabulary (L536, L533)

This section defines vocabulary for agent capabilities — the behavioral patterns that extend base model capabilities. Based on cli-aget optimization experiments (L533, L536, L557, L570).

## Key Insight (L536)

> **Agent_Skill, Agent_Hook, and Session_Protocol are PEERS under Agent_Capability, not in a parent-child hierarchy.**

This ontological correction was established through empirical research showing that skills are stateless (per Agent Skills Standard) while protocols may require state.

## Agent Capability Terms

### Agent_Capability

```yaml
Agent_Capability:
  skos:prefLabel: "Agent_Capability"
  skos:definition: "Abstract parent for all agent behavioral patterns that extend base model capabilities through configuration or instruction."
  skos:altLabel: ["Agent_Extension", "Behavioral_Module"]
  skos:narrower: ["Agent_Skill", "Agent_Hook", "Session_Protocol"]
  skos:related: ["Capability", "Specialization_Mechanism"]
  aget:theoretical_basis: "Object-Capability Model (Dennis & Van Horn 1966)"
  aget:source: "L536 Ontological Correction"
```

### Agent_Skill

```yaml
Agent_Skill:
  skos:prefLabel: "Agent_Skill"
  skos:definition: "Stateless, portable, on-demand capability that AI agents discover and load via SKILL.md manifest. Designed for cross-CLI portability."
  skos:altLabel: ["CLI_Skill", "SKILL.md"]
  skos:broader: "Agent_Capability"
  skos:related: ["Session_Protocol", "Agent_Hook"]
  aget:theoretical_basis: "Agent Skills Standard (agentskills.io)"
  aget:source: "L557 Agent Skills Standard Ontology"
  aget:note: "Skills are stateless by design; protocols may require state."
```

### Agent_Hook

```yaml
Agent_Hook:
  skos:prefLabel: "Agent_Hook"
  skos:definition: "Platform-specific lifecycle event handler that executes at defined points in agent/session lifecycle."
  skos:altLabel: ["Lifecycle_Hook", "Session_Hook"]
  skos:broader: "Agent_Capability"
  skos:related: ["Agent_Skill", "Session_Protocol"]
  aget:theoretical_basis: "Event-Driven Architecture (Michelson 2006)"
  aget:source: "L570 Session Protocol Ontological Clarification"
  aget:enum_values: ["SessionStart", "SessionEnd", "PreToolCall", "PostToolCall"]
```

### Session_Protocol

```yaml
Session_Protocol:
  skos:prefLabel: "Session_Protocol"
  skos:definition: "AGET-specific behavioral pattern that combines lifecycle awareness with on-demand capabilities. Hybrid of hooks and skills."
  skos:altLabel: ["AGET_Protocol"]
  skos:broader: "Agent_Capability"
  skos:narrower: ["Lifecycle_Protocol", "On_Demand_Protocol"]
  skos:related: ["Agent_Skill", "Agent_Hook"]
  aget:theoretical_basis: "L536 Ontological Correction"
  aget:note: "Session_Protocol is a PEER of Agent_Skill, not a subtype."
```

### Lifecycle_Protocol

```yaml
Lifecycle_Protocol:
  skos:prefLabel: "Lifecycle_Protocol"
  skos:definition: "Session protocol that executes at lifecycle boundaries (session start, session end). Implemented via hooks where available, scripts as fallback."
  skos:altLabel: ["Session_Lifecycle_Protocol"]
  skos:broader: "Session_Protocol"
  skos:related: ["Agent_Hook"]
  skos:example: ["wake_up", "wind_down"]
  aget:source: "L536, L570"
  aget:test_coverage: ["TestWakeUpProtocol (3)", "TestWindDownProtocol (8)"]
```

### On_Demand_Protocol

```yaml
On_Demand_Protocol:
  skos:prefLabel: "On_Demand_Protocol"
  skos:definition: "Session protocol that executes on user request, not at lifecycle boundaries. Fully portable via SKILL.md format."
  skos:altLabel: ["Invocable_Protocol"]
  skos:broader: "Session_Protocol"
  skos:related: ["Agent_Skill"]
  skos:example: ["study_up", "sanity_check", "step_back"]
  aget:source: "L536, L557"
  aget:test_coverage: ["TestStudyUpProtocol (6)", "TestSanityCheckProtocol (7)", "TestStepBackProtocol (6)"]
```

## CLI Support Terms

### CLI_Support_Level

```yaml
CLI_Support_Level:
  skos:prefLabel: "CLI_Support_Level"
  skos:definition: "Classification of AGET support level for a specific CLI agent, based on empirical validation evidence."
  skos:altLabel: ["CLI_Compatibility_Level"]
  aget:theoretical_basis: "L533 Support Level Framework"
  aget:source: "76/76 infrastructure tests passing"
  aget:enum_values:
    - Baseline: "CI + live session validation (primary target)"
    - Validated: "VALIDATION_REPORT + live session confirmation"
    - Compatible: "Infrastructure tests pass (should work, verify)"
    - Experimental: "Architecture analysis only (may work, untested)"
    - Unsupported: "Known blockers exist (does not work)"
```

## Agent Capability Terms Summary

| Term | Type | Parent | Source |
|------|------|--------|--------|
| Agent_Capability | Concept | (root) | L536 |
| Agent_Skill | Concept | Agent_Capability | L557 |
| Agent_Hook | Concept | Agent_Capability | L570 |
| Session_Protocol | Concept | Agent_Capability | L536 |
| Lifecycle_Protocol | Concept | Session_Protocol | L536 |
| On_Demand_Protocol | Concept | Session_Protocol | L536 |
| CLI_Support_Level | Enum | (root) | L533 |

## Ontology Reference

Full concept definitions with theoretical grounding are in:
`ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml` (Cluster 10, Concepts C041-C047)

---

## Requirements

### CAP-VOC-001: SKOS Foundation

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-VOC-001-01 | Terms SHALL have skos:prefLabel | Canonical name |
| CAP-VOC-001-02 | Terms SHALL have skos:definition | Understanding |
| CAP-VOC-001-03 | Hierarchies SHALL be acyclic | Reasoning |

### CAP-VOC-002: Term Usage

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-VOC-002-01 | Specs SHALL use vocabulary terms | Consistency |
| CAP-VOC-002-02 | New terms SHALL be added to vocabulary | Single source |
| CAP-VOC-002-03 | Terms SHALL use Title_Case | Convention |

### CAP-VOC-003: L440 Verification Terms

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-VOC-003-01 | V_Test SHALL be used for gate verification | L440 |
| CAP-VOC-003-02 | Declarative_Completion SHALL be marked anti-pattern | Prevention |
| CAP-VOC-003-03 | Verified_Completion SHALL be marked pattern | Best practice |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-VOC-001-* | validate_vocabulary.py | Planned |
| CAP-VOC-002-* | Manual review | Manual |
| CAP-VOC-003-* | V-test execution | Manual |

---

## References

- ADR-001: Controlled Vocabulary Standard Selection
- L437: Vocabulary Enhancement Roadmap
- L440: Manager Migration Verification Gap
- L451: Executable Knowledge Ontology (EKO)
- L453: AGET Ontology Independence Decision
- L459: Core Entity Vocabulary Vision
- L493: Vocabulary Prose Marking Pattern
- L494: Vocabulary Meta-Ontology Pattern
- W3C SKOS Reference: https://www.w3.org/TR/skos-reference/
- GM-RKB: https://www.gabormelli.com/RKB/

---

## Changelog

### v1.11.0 (2026-02-11)

- **NEW**: Added Part 8: Agent Capabilities Vocabulary (L536, L533)
- Added 7 vocabulary terms from cli-aget optimization experiments:
  - Agent_Capability: Abstract parent for agent behavioral patterns
  - Agent_Skill: Stateless, portable, on-demand (per Agent Skills Standard)
  - Agent_Hook: Platform-specific lifecycle event handler
  - Session_Protocol: AGET-specific hybrid of hooks and skills
  - Lifecycle_Protocol: Session start/end protocols (wake_up, wind_down)
  - On_Demand_Protocol: User-invoked protocols (study_up, sanity_check)
  - CLI_Support_Level: Support classification (Baseline, Validated, Compatible, Experimental, Unsupported)
- Documented L536 ontological correction: peers not hierarchy
- Added test coverage mapping for all protocol terms
- Cross-referenced to ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml (Cluster 10, C041-C047)
- See: PROJECT_PLAN_skills_ontology_integration_v1.0, L533, L536, L557, L570

### v1.10.0 (2026-01-17)

- Added VERSION_SCOPE Terms subsection to Release Terms (R-REL-020)
- Added 8 vocabulary terms for release scope planning:
  - Version_Scope: Planning artifact for release boundaries and success criteria
  - Release_Phase: Discrete stage in release lifecycle
  - Pre_Release_Phase, Release_Execution_Phase, Post_Release_Phase: Three-phase model
  - MVP_Scope: Must-Ship items that block release
  - Rollback_Plan: Contingency procedure for release reversion
  - Release_Retrospective: Post-release lesson capture
- See: PROJECT_PLAN_version_scope_standardization_v1.0

### v1.9.0 (2026-01-16)

- **MAJOR**: Added AGET Ontology Foundation (L530) to Part 6
- Added Aget_Thing as universal root class with BFO:Entity grounding
- Renamed top-level categories to use Aget_* prefix (Aget_Continuant, Aget_Occurrent, Aget_Intangible)
- Renamed Abstract_Category to Aget_Intangible per L530 Finding 4 (readability)
- Added Agent-centric Continuant hierarchy (16 classes):
  - Aget_Agent, Aget_Person, Aget_AI_System, Aget_Instance, Aget_Organization, Aget_Team, Aget_Fleet
  - Aget_System, Aget_Technical_System, Aget_Software_System, Aget_Biological_System, Aget_Living_Organism, Aget_Animal
  - Aget_Artifact, Aget_Device, Aget_Tool
  - Aget_CreatedWork, Aget_Document, Aget_Specification, Aget_Code
- Added Occurrent hierarchy (6 classes):
  - Aget_Action, Aget_Task, Aget_Event, Aget_Meeting, Aget_Block, Aget_Decision
- Added Intangible branch (24 classes - L530 Findings 7-10):
  - Epistemology: Aget_Belief, Aget_Assumption, Aget_Hypothesis, Aget_Conviction, Aget_Knowledge, Aget_Justification, Aget_Evidence, Aget_Testimony, Aget_Inference
  - Deontic: Aget_Rule, Aget_Constraint, Aget_Norm, Aget_Obligation, Aget_Prohibition, Aget_Permission, Aget_Capability
  - Commitments: Aget_Promise, Aget_Commitment, Aget_Agreement, Aget_Contract, Aget_Right, Aget_Power
  - Consequences: Aget_Consequence, Aget_Sanction, Aget_Reward, Aget_Breach, Aget_Fulfillment
  - Other: Aget_Pattern, Aget_Project, Aget_Goal
- Added DAG relationship support (multi-parent inheritance)
- Added new AGET extensions: aget:theoretical_basis, aget:dag_parents, aget:user_facing, aget:display_alias, aget:deontic_operator, aget:hohfeldian_correlative, aget:impact_dimensions
- Maintained backward compatibility with Person_Entity, Organization_Entity, etc.
- See: L530 (AGET Ontology Foundation Research), PROJECT_PLAN_aget_ontology_foundation_v1.0

### v1.8.0 (2026-01-12)

- Added Part 7: Standards Document Ontology (L502)
- Added document type hierarchy (Normative, Informative, Process)
- Added specification instances as first-class entities
- See: PROJECT_PLAN_standards_ontology_elevation_v1.0

### v1.7.0 (2026-01-12)

- Added Version_Bearing_File vocabulary term with SKOS structure
- Added Version_Coherence vocabulary term
- Added Version_Drift_File anti-pattern term
- Added terms to Release Terms table
- Supports R-REL-VER-001 (Version-Bearing File Coherence)
- See: L521 (Version-Bearing File Specification-to-Tool Gap), PROJECT_PLAN_version_bearing_file_remediation_v1.0

### v1.6.0 (2026-01-11)

- Added Issue Governance Terms section (CAP-ISSUE-*)
- Added 9 issue governance vocabulary terms: Issue_Destination, Private_Issue_Destination, Public_Issue_Destination, Private_Fleet_Agent, Public_Remote_Agent, Issue_Sanitization, Private_Pattern, Cross_Boundary_Filing, Issue_Fragmentation
- Added SKOS relationships linking terms to AGET_ISSUE_GOVERNANCE_SPEC requirements
- Supports CAP-ISSUE-001 through CAP-ISSUE-004
- See: L520 (Issue Governance Gap), PROJECT_PLAN_issue_governance_v1.0

### v1.5.0 (2026-01-11)

- Version bump for consistency

### v1.4.0 (2026-01-11)

- Added Migration Terms section (CAP-MIG-*)
- Added 7 migration vocabulary terms: Pre_Flight, Health_Check, Framework_Sync, Remote_Supervisor, Cross_Machine_Migration, Stale_Framework, State_Verification
- Supports CAP-MIG-017 (Remote Supervisor Upgrade)
- See: L457 (Remote Supervisor Upgrade Pattern), FLEET_MIGRATION_GUIDE_v3.md

### v1.3.0 (2026-01-09)

- Added "Term Usage in Documents" section (L493 Vocabulary_Prose_Marking_Pattern)
- Migrated all single-word terms to compound forms per L493:
  - Abstraction axis: Algorithm_Concept, Process_Concept, Procedure_Concept, Function_Concept, Workflow_Concept, Protocol_Concept
  - Determinism axis: Deterministic_Property, Probabilistic_Property, Syllogistic_Property
  - Reusability axis: Universal_Property, Parameterized_Property, One_Time_Property
  - Artifact types: SOP_Artifact, Runbook_Artifact, Playbook_Artifact
  - Entity categories: Continuant_Category, Occurrent_Category, Abstract_Category
- Added Meta-Ontology Terms section (L494 Vocabulary_Meta_Ontology_Pattern)
- Defined four meta-terms: Aget_Entity, Aget_Concept, Aget_Property, Aget_Specification
- Added Meta-Ontology ERD showing term hierarchy
- Added skos:altLabel for backward compatibility on all migrated terms
- Updated Part 6 intro to reference L494 meta-ontology relationship
- Updated cross-references (skos:broader) to use compound category names
- Issue #TBD: Vocabulary Prose Marking (v3.5.0)

### v1.2.0 (2026-01-06)

- Added Part 6: Core Domain Entities (L459)
- Added 8 core entity definitions: Person, Organization, Document, Decision, Event, Task, Project, Requirement
- Added upper-level entity categories: Entity, Continuant, Occurrent, Abstract
- Added AGET extensions: aget:core_entity, aget:attributes, aget:relationships
- Added entity inheritance mechanism (inherits:, extends: in manifest.yaml)
- Added inheritance rules R-ENT-001 through R-ENT-005
- Added entity summary table with required attributes and relationships
- Issue #48: Core Entity Vocabulary

### v1.1.1 (2026-01-04)

- Fixed changelog per L453 (AGET Ontology Independence)
- Added contribution guidelines section (G2.4)
- Removed gmrkb_uri references (L453: vocabulary is self-contained)

### v1.1.0 (2026-01-04)

- Added Executable Knowledge Ontology (EKO) terms (L451)
- Added AGET extensions: determinism, reusability, abstraction
- Added abstraction axis terms: Algorithm, Process, Procedure, Function, Workflow, Protocol
- Added determinism axis terms: Deterministic, Probabilistic, Syllogistic
- Added reusability axis terms: Universal, Parameterized, One_Time
- Added artifact types: SOP, Runbook, Playbook, Project_Plan

### v1.0.0 (2026-01-04)

- Initial consolidated specification
- Merged AGET_GLOSSARY_STANDARD_SPEC.md (format)
- Merged AGET_CONTROLLED_VOCABULARY.md (terms)
- Added L440 verification terms (V_Test, Declarative_Completion, Verified_Completion)
- Added terms from Gate 2 specs (Testing, Release, Documentation, Organization, Error, Security)
- Four-part structure: Standard, Core Terms, Domain Terms, Format Terms

---

*AGET_VOCABULARY_SPEC.md — Vocabulary standards for AGET framework*
*Consolidates: AGET_GLOSSARY_STANDARD_SPEC.md + AGET_CONTROLLED_VOCABULARY.md*
