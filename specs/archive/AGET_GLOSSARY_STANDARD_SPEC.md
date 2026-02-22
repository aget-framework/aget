# AGET Glossary Standard Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards (Informational)
**Format Version**: 1.2
**Created**: 2025-12-21
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_GLOSSARY_STANDARD_SPEC.md`
**Change Proposal**: CP-003
**Enhancement**: [aget-framework/aget#9](https://github.com/aget-framework/aget/issues/9)
**Related**: ADR-001 (SKOS adoption), AGET_CONTROLLED_VOCABULARY.md, L339

---

## Abstract

This specification defines the standard format, organization, and validation rules for AGET framework glossaries and controlled vocabularies. It codifies best practices observed across vocabulary documents and establishes SKOS (Simple Knowledge Organization System) as the foundation per ADR-001.

## Motivation

Vocabulary standardization requires explicit specification:
- Consistent terminology across AGET agents
- Vocabulary interoperability between agents
- Support for both human-readable Markdown and machine-readable YAML
- Validation of vocabulary completeness and consistency

Without explicit glossary standards, terminology becomes inconsistent and vocabulary documents become incompatible.

## Scope

**Applies to**: All AGET framework glossaries and controlled vocabularies.

**Defines**:
- SKOS property usage for AGET
- AGET extension properties
- Entry format patterns (Minimal, Standard, Rich, Action, Deprecated)
- Organization patterns
- Validation rules
- Conformance levels

**Does NOT Define**:
- Specific term definitions (see AGET_CONTROLLED_VOCABULARY.md)
- LLM vocabulary processing

---

## Vocabulary

Domain terms for the Glossary specification:

```yaml
vocabulary:
  meta:
    domain: "glossary"
    version: "1.0.0"
    inherits: "aget_core"

  persona:  # D1: Standard identity
    SKOS:
      skos:definition: "Simple Knowledge Organization System - W3C vocabulary standard"
      aget:reference: "https://www.w3.org/TR/skos-reference/"
    Concept_Scheme:
      skos:definition: "SKOS aggregation of concepts organized hierarchically"

  memory:  # D2: Stored artifacts
    Glossary:
      skos:definition: "Document containing term definitions"
      aget:location: "docs/ or .aget/vocabulary/"
    Controlled_Vocabulary:
      skos:definition: "Glossary with formal validation rules"
    Vocabulary_Entry:
      skos:definition: "Single term definition within glossary"
      skos:narrower: ["Minimal_Entry", "Standard_Entry", "Rich_Entry", "Action_Entry", "Deprecated_Entry"]

  reasoning:  # D3: Decision patterns
    Entry_Pattern:
      skos:definition: "Format template for vocabulary entries"
    Organization_Pattern:
      skos:definition: "Structure for organizing glossary entries"
    Validation_Rule:
      skos:definition: "Constraint checked during vocabulary validation"

  skills:  # D4: Capabilities
    SKOS_Property:
      skos:definition: "Standard SKOS vocabulary property"
      skos:narrower: ["prefLabel", "definition", "altLabel", "broader", "narrower", "related", "example"]
    AGET_Extension:
      skos:definition: "Custom AGET property extending SKOS"
      skos:narrower: ["aget:has", "aget:operatesWithin", "aget:derivedFrom", "aget:requires", "aget:supervises"]
    Conformance_Level:
      skos:definition: "Degree of specification adherence"
      skos:narrower: ["Level_1_Basic", "Level_2_Standard", "Level_3_Full_SKOS"]

  context:  # D5: WHERE/WHEN
    Framework_Vocabulary:
      skos:definition: "Terms portable across all AGET agents"
    Domain_Vocabulary:
      skos:definition: "Terms specific to a particular domain or agent"
```

---

## Requirements

### CAP-GLOSS-001: SKOS Foundation

The SYSTEM shall use SKOS as vocabulary foundation.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GLOSS-001-01 | ubiquitous | The SYSTEM shall include skos:prefLabel for each term |
| CAP-GLOSS-001-02 | ubiquitous | The SYSTEM shall include skos:definition for each term |
| CAP-GLOSS-001-03 | optional | WHERE Synonyms exist, the SYSTEM may include skos:altLabel |
| CAP-GLOSS-001-04 | optional | WHERE Hierarchy exists, the SYSTEM may include skos:broader |
| CAP-GLOSS-001-05 | optional | WHERE Children exist, the SYSTEM may include skos:narrower |
| CAP-GLOSS-001-06 | optional | WHERE Associations exist, the SYSTEM may include skos:related |
| CAP-GLOSS-001-07 | optional | WHERE Examples needed, the SYSTEM may include skos:example |

**Enforcement**: `validate_vocabulary.py`

### CAP-GLOSS-002: AGET Extensions

The SYSTEM shall support AGET extension properties.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GLOSS-002-01 | optional | WHERE Possession relationship exists, the SYSTEM may use aget:has |
| CAP-GLOSS-002-02 | optional | WHERE Scope boundary exists, the SYSTEM may use aget:operatesWithin |
| CAP-GLOSS-002-03 | optional | WHERE Source exists, the SYSTEM may use aget:derivedFrom |
| CAP-GLOSS-002-04 | optional | WHERE Dependency exists, the SYSTEM may use aget:requires |
| CAP-GLOSS-002-05 | optional | WHERE Authority relationship exists, the SYSTEM may use aget:supervises |
| CAP-GLOSS-002-06 | optional | WHERE Peer relationship exists, the SYSTEM may use aget:coordinatesWith |
| CAP-GLOSS-002-07 | optional | WHERE Validation needed, the SYSTEM may use aget:validationRule |
| CAP-GLOSS-002-08 | optional | WHERE Deprecation needed, the SYSTEM may use aget:deprecation |

**Enforcement**: `validate_vocabulary.py`

### CAP-GLOSS-003: Entry Format

The SYSTEM shall follow Entry_Format patterns.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GLOSS-003-01 | ubiquitous | The SYSTEM shall support Minimal_Entry (prefLabel + definition) |
| CAP-GLOSS-003-02 | ubiquitous | The SYSTEM shall support Standard_Entry (Minimal + altLabel + example) |
| CAP-GLOSS-003-03 | ubiquitous | The SYSTEM shall support Rich_Entry (Standard + relationships) |
| CAP-GLOSS-003-04 | optional | WHERE Actions defined, the SYSTEM may use Action_Entry (preconditions + postconditions) |
| CAP-GLOSS-003-05 | conditional | IF Term is deprecated THEN the SYSTEM shall use Deprecated_Entry format |
| CAP-GLOSS-003-06 | ubiquitous | The SYSTEM shall use Title_Case for term names |

**Enforcement**: Entry format validation

### CAP-GLOSS-004: Organization

The SYSTEM shall organize glossaries following Organization_Patterns.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GLOSS-004-01 | ubiquitous | The SYSTEM should separate Framework_Vocabulary from Domain_Vocabulary |
| CAP-GLOSS-004-02 | optional | WHERE Many terms exist, the SYSTEM may use Category_Based organization |
| CAP-GLOSS-004-03 | optional | WHERE Index needed, the SYSTEM may use Alphabetical_With_Index organization |
| CAP-GLOSS-004-04 | optional | WHERE Hierarchy central, the SYSTEM may use Hierarchical organization |
| CAP-GLOSS-004-05 | ubiquitous | The SYSTEM shall document Critical_Distinctions for confusable terms |

**Enforcement**: Organization review

### CAP-GLOSS-005: Validation

The SYSTEM shall validate vocabulary compliance.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-GLOSS-005-01 | ubiquitous | The SYSTEM shall validate all terms have prefLabel and definition |
| CAP-GLOSS-005-02 | ubiquitous | The SYSTEM shall validate hierarchies are acyclic |
| CAP-GLOSS-005-03 | ubiquitous | The SYSTEM shall validate broader/narrower inverses exist |
| CAP-GLOSS-005-04 | ubiquitous | The SYSTEM shall validate term references resolve |
| CAP-GLOSS-005-05 | conditional | IF Deprecated THEN the SYSTEM shall validate replacement term exists |
| CAP-GLOSS-005-06 | ubiquitous | The SYSTEM shall use Title_Case for Entity terms |
| CAP-GLOSS-005-07 | ubiquitous | The SYSTEM shall use lowercase for Action terms |

**Enforcement**: `validate_vocabulary.py`

---

## Standards Foundation

### W3C SKOS (Primary)

Per ADR-001 (2025-11-21), AGET adopts W3C SKOS as the vocabulary standard foundation:

| SKOS Property | AGET Usage | Required |
|---------------|------------|----------|
| `skos:prefLabel` | Canonical term name | Yes |
| `skos:definition` | Complete definition | Yes |
| `skos:altLabel` | Synonyms, abbreviations (aka) | No |
| `skos:broader` | IS-A parent relationship | No |
| `skos:narrower` | IS-A child relationship | No |
| `skos:related` | Associative relationship | No |
| `skos:example` | Usage examples | No |

### AGET Extensions

Nine custom relationship properties extend SKOS for AGET domain semantics:

| Property | Definition | Cardinality |
|----------|------------|-------------|
| `aget:has` | Possession/containment | 1:many |
| `aget:operatesWithin` | Scope boundary | 1:1 |
| `aget:derivedFrom` | Creation source | 1:many |
| `aget:requires` | Dependency prerequisite | 0:many |
| `aget:supervises` | Authority relationship | 1:many |
| `aget:coordinatesWith` | Peer collaboration (symmetric) | many:many |
| `aget:defines` | Spec → Implementation | 1:many |
| `aget:exhibits` | Instance → Pattern | 1:many |

Additional AGET properties:

| Property | Purpose |
|----------|---------|
| `aget:characteristics` | Key attributes |
| `aget:distinguishedFrom` | Clarifying distinctions |
| `aget:antiPattern` | Invalid usage patterns |
| `aget:location` | Canonical file path |
| `aget:structure` | Internal organization |
| `aget:whyItMatters` | Practical importance (optional) |
| `aget:validationRule` | Automated check criteria |
| `aget:deprecation` | Deprecation metadata |

---

## Entry Format Patterns

### Pattern A: Minimal Entry (EARS-Compatible)

Suitable for simple term lists in EARS specifications.

```yaml
vocabulary:
  Term_Name:
    skos:definition: "Complete definition statement."
```

**Use when**: Embedded in EARS specs, minimal overhead needed.

### Pattern B: Standard Entry

Standard format for general glossaries.

```yaml
Term_Name:
  skos:prefLabel: "Term_Name"
  skos:definition: "Complete definition using controlled vocabulary."
  skos:altLabel: ["TN", "Alternative Name"]
  skos:example: "Example usage in context."
```

### Pattern C: Rich Entry (Recommended)

Full entry format with technical term, examples, and relationships.

```yaml
Term_Name:
  skos:prefLabel: "Term_Name"
  aget:technicalTerm: "Formal Technical Name"
  skos:definition: "Complete definition using controlled vocabulary."
  skos:altLabel: ["TN"]
  skos:broader: "Parent_Term"
  aget:has: ["Child_A", "Child_B"]
  aget:distinguishedFrom:
    - term: "Similar_Term"
      reason: "Explanation of difference"
  skos:example:
    - "Example 1: Context"
    - "Example 2: Different context"
  aget:validationRule: "Must have X property"
```

### Pattern D: Action Entry

For actions/verbs with preconditions and postconditions.

```yaml
Action_Name:
  skos:prefLabel: "Action_Name"
  aget:technicalTerm: "Formal Process Name"
  skos:definition: "Action description."
  aget:preconditions:
    - "Required state before action"
  aget:postconditions:
    - "Resulting state after action"
  aget:triggers:
    - "Event that initiates action"
  skos:example: "Action invoked when X occurs"
```

### Pattern E: Deprecated Entry

For terms being phased out.

```yaml
Deprecated_Term:
  skos:prefLabel: "Deprecated_Term"
  skos:definition: "Original definition."
  aget:deprecation:
    status: deprecated
    since: "v2.9.0"
    replacement: "New_Term"
    migrationGuide: |
      Replace all instances of Deprecated_Term with New_Term.
      Update imports: old.path → new.path
```

---

## Organization Patterns

### Pattern O1: Framework vs Domain Split

Separate portable framework terminology from domain-specific terms.

```
glossary/
├── FRAMEWORK_VOCABULARY.md    # Portable across all agents
└── DOMAIN_VOCABULARY.md       # Domain-specific terms
```

**Portability Test**: Can term be used unchanged in any AGET agent? Yes → Framework. No → Domain.

### Pattern O2: Category-Based Organization

Group terms by semantic category.

```markdown
## Core Entities
- Agent, Session, Learning...

## Core Actions
- Validate, Graduate, Migrate...

## States & Transitions
- Draft, Active, Deprecated...

## Relationships
- has, requires, supervises...
```

### Pattern O3: Alphabetical with Index

A-Z listing with cross-references.

### Pattern O4: Hierarchical (SKOS Concept Scheme)

Top concepts with narrower terms nested.

---

## Conformance Levels

### Level_1_Basic (EARS-Compatible)

- All terms have `skos:prefLabel` and `skos:definition`
- Terms organized in clear sections
- No validation tooling required

### Level_2_Standard (Recommended)

- Level 1 requirements
- Hierarchical relationships documented (`skos:broader`/`skos:narrower`)
- Critical distinctions section
- Version history maintained

### Level_3_Full_SKOS (Framework-Level)

- Level 2 requirements
- All 9 AGET relationship types documented where applicable
- SKOS validation tooling passes
- CI integration for vocabulary validation

---

## Authority Model

```yaml
authority:
  applies_to: "vocabulary_maintainers"

  governed_by:
    spec: "AGET_GLOSSARY_STANDARD_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "create vocabulary entries following patterns"
      - "update term definitions"
      - "add relationship properties"
      - "mark terms as deprecated"

    requires_approval:
      - action: "add new AGET extension property"
        approver: "framework-aget"
      - action: "change SKOS property usage"
        approver: "framework-aget"
      - action: "remove terms from Framework_Vocabulary"
        approver: "framework-aget"

  validation_authority:
    - action: "validate_vocabulary.py"
      authority: "automated"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-GLOSS-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT omit skos:prefLabel from Vocabulary_Entry"
      rationale: "Every term needs a canonical name"

    - id: "INV-GLOSS-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT omit skos:definition from Vocabulary_Entry"
      rationale: "Every term needs a definition"

    - id: "INV-GLOSS-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT create circular skos:broader hierarchies"
      rationale: "Hierarchies must be acyclic for reasoning"

    - id: "INV-GLOSS-004"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT deprecate term without replacement"
      rationale: "Deprecation requires migration path"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: ".aget/vocabulary/"
      purpose: "Agent-specific vocabulary"
      optional: true

  optional_directories:
    - path: "docs/glossary/"
      purpose: "Published glossary documents"

  required_files:
    - path: "AGET_CONTROLLED_VOCABULARY.md"
      purpose: "Core framework vocabulary"
      location: "aget/specs/ or aget/docs/"

  file_formats:
    markdown:
      extension: ".md"
      usage: "Human-readable glossaries"
    yaml:
      extension: ".yaml"
      usage: "Machine-readable vocabularies"
      schema: "AGET_VOCABULARY_SCHEMA_SKOS_v1.0.yaml"
```

---

## Validation

### Validation Commands

```bash
# Validate SKOS vocabulary
python3 validation/validate_vocabulary.py vocabulary.yaml

# Check cross-references
python3 validation/check_xrefs.py glossary.md
```

### EARS Pattern Verification

```bash
# Count EARS patterns in this spec
grep -cE "WHEN |WHILE |WHERE |IF .* THEN|The SYSTEM shall" aget/specs/AGET_GLOSSARY_STANDARD_SPEC.md
# Expected: > 20
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "SKOS (W3C Recommendation)"
  secondary:
    - "Knowledge Organization Systems"
    - "Controlled Vocabularies"
  rationale: >
    SKOS provides standards-based vocabulary structure (W3C 2009).
    Hierarchies and relationships enable machine reasoning.
    AGET extensions preserve domain-specific semantics.
  reference: "https://www.w3.org/TR/skos-reference/"
```

---

## References

### Standards

- W3C SKOS Reference: https://www.w3.org/TR/skos-reference/
- W3C SKOS Primer: https://www.w3.org/TR/skos-primer/
- ISO 704:2022 - Terminology work principles

### AGET Documents

- ADR-001: Controlled Vocabulary Standard Selection
- AGET_CONTROLLED_VOCABULARY.md (core framework)
- AGET_VOCABULARY_SCHEMA_SKOS_v1.0.yaml (schema definition)
- L339: Vocabulary research learnings

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L339"]
  pattern_origin: "Fleet vocabulary pattern synthesis"
  rationale: "Codified best practices from 11 vocabulary documents"

history:
  - version: "1.0.0"
    date: "2025-12-21"
    changes: "Initial release (v2.11.0)"
  - version: "1.1.0"
    date: "2025-12-27"
    changes: "EARS/SKOS reformat (v3.0.0-alpha.5)"
```

---

*AGET Glossary Standard Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture*
*"Standardized vocabulary enables standardized communication."*
