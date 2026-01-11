# AGET Vocabulary Specification

**Version**: 1.5.0
**Status**: Active
**Category**: Core (Standards)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-11
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_VOCABULARY_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 3.1
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

| Term | Definition |
|------|------------|
| `Release_Version` | Semantic version identifying a release |
| `Manager_Migration` | Updating managing agent version before release (R-REL-006) |
| `Multi_Repo_Coordination` | Synchronized release across repositories |
| `Release_Gate` | Verification checkpoint in release process |
| `CHANGELOG` | Document tracking notable changes per version |
| `GitHub_Release` | GitHub release object with tag and notes |
| `Deep_Release_Notes` | Narrative documentation beyond CHANGELOG |
| `Version_Drift` | ANTI-PATTERN: Manager behind managed repos |
| `Declarative_Release` | ANTI-PATTERN: Declaring version in commit message without updating version.json (L517) |
| `Version_Overrun` | ANTI-PATTERN: Instance version exceeds framework version (L517) |
| `Template_Abandonment` | ANTI-PATTERN: Published templates left behind during upgrades (R-REL-015 violation, L517) |
| `SOP_Theater` | ANTI-PATTERN: SOP steps without verification (L517) |
| `Release_Verification` | Automated validation that all release artifacts complete before push (CAP-REL-009) |
| `Pre_Push_Gate` | BLOCKING validation checkpoint before git push (CAP-REL-009) |
| `Version_Ceiling` | Constraint that instance version ≤ framework version (CAP-REL-010) |

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

# Part 6: Core Domain Entities (L459)

Core domain entities are standardized foundational entities that AGET agents inherit by default and extend only when domain-specific requirements demand. Per **L459 (Core Entity Vocabulary Vision)**, this addresses the "reinvention anti-pattern" where agents independently define common entities.

**Relationship to Meta-Ontology (L494)**:
- `Aget_Entity` is defined in the Meta-Ontology section as the root meta-term for all domain objects
- This Part 6 extends that meta-definition with the full entity hierarchy and concrete entities

**Relationship to EKO (L451)**:
- EKO defines **executable knowledge** (what Aget_Instances DO) — SOPs, Runbooks, Playbooks
- Core Entity Vocabulary defines **domain objects** (what Aget_Instances WORK WITH) — Person_Entity, Organization_Entity, Document_Entity

## Upper-Level Entity Categories

```yaml
Aget_Entity:
  skos:prefLabel: "Aget_Entity"
  skos:altLabel: "Entity"
  skos:definition: "A distinct, identifiable thing in the domain that can have attributes and relationships."
  aget:meta_entity: true
  skos:narrower: ["Continuant_Category", "Occurrent_Category", "Abstract_Category"]

Continuant_Category:
  skos:prefLabel: "Continuant_Category"
  skos:altLabel: ["Continuant"]
  skos:definition: "Aget_Entity that persists through time while maintaining identity."
  skos:broader: "Aget_Entity"
  skos:narrower: ["Person_Entity", "Organization_Entity", "Document_Entity", "Project_Entity"]
  skos:example: "A person exists continuously; they don't happen and end."

Occurrent_Category:
  skos:prefLabel: "Occurrent_Category"
  skos:altLabel: ["Occurrent"]
  skos:definition: "Aget_Entity that happens in time, with a beginning and end."
  skos:broader: "Aget_Entity"
  skos:narrower: ["Event_Entity", "Task_Entity"]
  skos:example: "A meeting happens at a specific time; it has a start and end."

Abstract_Category:
  skos:prefLabel: "Abstract_Category"
  skos:altLabel: ["Abstract"]
  skos:definition: "Aget_Entity that is non-physical and exists as a conceptual construct."
  skos:broader: "Aget_Entity"
  skos:narrower: ["Decision_Entity", "Requirement_Entity"]
  skos:example: "A decision exists as a concept, not as a physical thing."
```

## Core Entity Definitions

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
