# AGET Vocabulary Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Core (Standards)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
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

| Term | Definition |
|------|------------|
| `AGET` | Agent configuration & lifecycle management framework |
| `aget` | Lowercase form; read-only instance type |
| `AGET` (caps) | Action-taking instance type with write permissions |
| `Fleet_Agent` | Agent registered in Fleet_State under Supervisor coordination |
| `Template` | Reusable agent archetype (e.g., template-worker-aget) |
| `Instance` | Concrete agent created from a Template |
| `Core_Template` | Fleet role template (worker, advisor, supervisor) |
| `Specialized_Template` | Task-specific template (spec-engineer, developer) |

## Organizational Terms

| Term | Definition |
|------|------------|
| `Portfolio` | Organizational grouping (e.g., ccb, main) |
| `Fleet` | Collection of agents under supervisor coordination |
| `Fleet_State` | Canonical registry of fleet membership |
| `Supervisor` | Agent responsible for fleet coordination |
| `Principal` | Human operator with ultimate authority |

## Configuration Terms

| Term | Definition |
|------|------------|
| `Version_Json` | Identity configuration file (.aget/version.json) |
| `Agents_Md` | Behavior specification file (AGENTS.md) |
| `Claude_Md` | Symlink to Agents_Md for Claude Code |
| `Configuration` | Combined Version_Json + Agents_Md |
| `aget_version` | Framework version (e.g., "3.2.0") |

## Session Protocol Terms

| Term | Definition |
|------|------------|
| `Wake_Protocol` | Session initialization ritual |
| `Wake_Command` | User command "wake up" |
| `Wind_Down_Protocol` | Session finalization |
| `Session_State` | Current session context |
| `Silent_Execution` | Protocol without showing tool calls |

## Evolution Terms

| Term | Definition |
|------|------------|
| `Learning_Document` | L-series knowledge capture (e.g., L440) |
| `L_Doc` | Abbreviation for Learning_Document |
| `Evolution_Directory` | Storage for learning (.aget/evolution/) |
| `Pattern_Extraction` | Identifying reusable pattern |
| `Knowledge_Migration` | Moving learning between agents |

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
- W3C SKOS Reference: https://www.w3.org/TR/skos-reference/

---

## Changelog

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
