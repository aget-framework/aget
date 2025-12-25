# AGET Glossary Standard Specification

**Version**: 1.0.0
**Date**: 2025-12-21
**Status**: CANONICAL
**Location**: aget/specs/AGET_GLOSSARY_STANDARD_SPEC_v1.0.md
**Author**: private-aget-framework-AGET
**Enhancement**: [aget-framework/aget#9](https://github.com/aget-framework/aget/issues/9)
**Related**: ADR-001 (SKOS adoption), AGET_CONTROLLED_VOCABULARY.md, L339

---

## Executive Summary

This specification defines the standard format, organization, and validation rules for AGET framework glossaries and controlled vocabularies. It codifies best practices observed across 11 vocabulary documents from 4 agents and establishes SKOS (Simple Knowledge Organization System) as the foundation per ADR-001.

### Purpose

Provide a consistent, standards-based approach for:
1. Defining and organizing terminology across AGET agents
2. Enabling vocabulary interoperability between agents
3. Supporting both human-readable Markdown and machine-readable YAML formats
4. Validating vocabulary completeness and consistency

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
    definition: "Complete definition statement."
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

**Markdown equivalent**:

```markdown
### Term_Name

**Definition**: Complete definition using controlled vocabulary.

**Also known as**: TN, Alternative Name

**Example**: Example usage in context.
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

**Markdown equivalent**:

```markdown
### Term_Name

**Technical Term**: Formal Technical Name

**Definition**: Complete definition using controlled vocabulary.

**Also known as**: TN

**Parent**: [Parent_Term](#parent_term)

**Has**: Child_A, Child_B

**Not to be confused with**: Similar_Term (Explanation of difference)

**Examples**:
- Example 1: Context
- Example 2: Different context

**Validation**: Must have X property
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

**Markdown equivalent**:

```markdown
### Action: Validate

**Technical Term**: Pattern Validation Process

**Definition**: Verify pattern meets quality criteria.

**Preconditions**:
- Pattern documentation exists
- Pattern has README.md

**Postconditions**:
- Validation report generated
- Pattern marked as validated or failing

**Triggers**:
- PR submission
- Manual invocation

**Example**: Validate invoked during CI pipeline.
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

**Markdown equivalent**:

```markdown
### Deprecated_Term (DEPRECATED)

> **Deprecated since v2.9.0**: Use [New_Term](#new_term) instead.

**Definition**: Original definition.

**Migration**:
```
Replace all instances of Deprecated_Term with New_Term.
Update imports: old.path → new.path
```
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

```markdown
## A-Z Index

| Term | Category | Page |
|------|----------|------|
| Agent | Entity | #agent |
| Validate | Action | #validate |
...

## Definitions

### Agent
...

### Validate
...
```

### Pattern O4: Hierarchical (SKOS Concept Scheme)

Top concepts with narrower terms nested.

```yaml
concept_scheme:
  hasTopConcept:
    - Agent:
        narrower: [Fleet_Agent, Supervisor, Worker]
    - Session:
        narrower: [Aget_Session, Planning_Session]
    - Artifact:
        narrower: [Learning, Specification, ADR]
```

---

## Special Sections

### Critical Distinctions

Document commonly confused term pairs.

```markdown
## Critical Distinctions

| Term A | Term B | Key Difference |
|--------|--------|----------------|
| Template | Instance | Template is blueprint; Instance is running agent |
| aget | AGET | Lowercase = read-only; Uppercase = action-taking |
| Pattern | Script | Pattern is parameterized; Script is fixed |
```

### Numeric Constants as Vocabulary

When domain requires numeric constants as terms.

```yaml
Zero_Point_Two_Five:
  skos:prefLabel: "Zero_Point_Two_Five"
  skos:definition: "Threshold value (0.25) for confidence scoring"
  aget:numericValue: 0.25
  aget:usedIn: ["confidence_scoring", "validation"]
```

### Version History

Track vocabulary evolution.

```markdown
## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2025-12-01 | Added deprecated terms section |
| 1.0.0 | 2025-11-15 | Initial release |

### Changelog

**v1.1.0**
- Added: `New_Term_A`, `New_Term_B`
- Deprecated: `Old_Term` → replaced by `New_Term_A`
- Changed: `Existing_Term` definition clarified
```

---

## File Formats

### Standalone Markdown Glossary

```markdown
# {Domain} Glossary

**Version**: X.Y.Z
**Date**: YYYY-MM-DD
**Status**: DRAFT | CANONICAL

---

## Quick Reference

| Term | Definition (Brief) |
|------|-------------------|
| ... | ... |

---

## Definitions

### Term_Name
...
```

### YAML Embedded Vocabulary

For EARS specifications and machine-readable use.

```yaml
vocabulary:
  metadata:
    version: "1.0.0"
    status: draft
    skos:conceptScheme: "aget:Domain_Vocabulary"

  terms:
    Term_Name:
      skos:prefLabel: "Term_Name"
      skos:definition: "..."
```

### SKOS Full Format

Complete SKOS representation for tooling.

```yaml
# AGET_VOCABULARY_SKOS_v1.0.yaml
metadata:
  version: "1.0.0"
  standard: "W3C SKOS + AGET Extensions"

namespaces:
  skos: "http://www.w3.org/2004/02/skos/core#"
  aget: "https://aget-framework.org/vocab#"

concept_scheme:
  uri: "aget:Domain_Controlled_Vocabulary"
  skos:prefLabel: "Domain Controlled Vocabulary"
  hasTopConcept: [...]

concepts:
  Term_Name:
    skos:prefLabel: "Term_Name"
    skos:definition: "..."
    skos:broader: "Parent_Term"
    aget:has: [...]
```

---

## Validation Rules

### Required Properties

| Level | Property | Requirement |
|-------|----------|-------------|
| P0 | `skos:prefLabel` | Exactly 1 per term |
| P0 | `skos:definition` | Exactly 1 per term |
| P1 | `skos:broader` | Required for Aget_* terms |
| P2 | `skos:example` | Recommended for complex terms |

### Hierarchical Integrity

1. Every `skos:broader` reference MUST have corresponding `skos:narrower` inverse
2. Hierarchies MUST be acyclic (no circular broader relationships)
3. All `Aget_*` prefixed terms MUST have generic parent

### Relationship Integrity

1. Symmetric relationships (`aget:coordinatesWith`) MUST have inverse
2. Required optionality relationships MUST be present
3. Cardinality constraints MUST be validated

### Cross-Reference Integrity

1. All term references MUST resolve to defined terms
2. Deprecated term replacements MUST exist
3. External links SHOULD be validated

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Term names | Title_Case | `Fleet_Agent` |
| Action terms | lowercase_verb | `validate`, `migrate` |
| Type prefixes | SCREAMING_CASE | `AGET_`, `SPEC_` |

---

## Tooling Requirements

### Required Tools

| Tool | Purpose | Location |
|------|---------|----------|
| `validate_vocabulary.py` | SKOS validation | `.aget/tools/` |
| `project_skos_to_ears.py` | SKOS → EARS projection | `.aget/tools/` |

### Validation Commands

```bash
# Validate SKOS vocabulary
python3 .aget/tools/validate_vocabulary.py vocabulary.yaml

# Project to EARS format
python3 .aget/tools/project_skos_to_ears.py vocabulary.yaml > ears_vocab.yaml

# Check cross-references
python3 .aget/tools/check_xrefs.py glossary.md
```

### CI Integration

```yaml
# .github/workflows/vocabulary.yml
vocabulary-validation:
  runs-on: ubuntu-latest
  steps:
    - name: Validate vocabulary
      run: python3 .aget/tools/validate_vocabulary.py
```

---

## Migration Guide

### From Plain Markdown to SKOS-Aligned

1. Add metadata header (version, date, status)
2. Add `skos:` property names to entries
3. Extract hierarchy into `skos:broader`/`skos:narrower`
4. Add validation rules section

### From Custom YAML to SKOS

| Current Field | SKOS Mapping |
|---------------|--------------|
| `term_name` | `skos:prefLabel` |
| `definition` | `skos:definition` |
| `aka` | `skos:altLabel` |
| `examples` | `skos:example` |
| `relationship` (IS-A) | `skos:broader` |
| Custom relationships | `aget:{type}` |

---

## Examples from Fleet

### Example 1: Framework Vocabulary (Supervisor Pattern)

From `private-supervisor-AGET/.aget/evolution/CONTROLLED_VOCABULARY.md`:

```markdown
#### Entity: Pattern

- **Technical Term**: Reusable Behavior Component
- **Definition**: A self-contained, parameterized behavioral template that can be invoked with context-specific parameters to perform consistent operations across agents.
- **Not to be confused with**: Template (agent archetype), Script (non-parameterized)
- **Example Usage**: "The session pattern manages wake/wind-down protocols"
- **Validation Rule**: Must have README.md, be in patterns/ directory
```

### Example 2: Domain Vocabulary (LegalOn Pattern)

From LegalOn GenAI Evaluation Framework:

```markdown
### Contract Clause

**Definition**: A distinct section of a contract that addresses a specific subject, typically identified by a heading and containing related provisions.

**Industry Usage**: Legal document component
**AGET Usage**: Extraction target for AI analysis
```

### Example 3: SKOS Full Entry

```yaml
Aget_Session:
  skos:prefLabel: "Aget_Session"
  aget:technicalTerm: "AGET Framework Session Instance"
  skos:definition: "Session for Aget_Agent complying with Session_Metadata_Standard_v1.0, including wake/wind-down protocols and metadata persistence."
  skos:broader: "Session"
  skos:altLabel: ["agent session"]
  aget:derivedFrom: ["SESSION_{date}_{name}.md"]
  aget:exhibits: ["Planning_Pattern", "Discovery_Pattern", "Gate_Execution_Pattern"]
  aget:location: "sessions/"
  aget:structure: "YAML metadata + Markdown narrative"
  skos:example:
    - "SESSION_2025-12-21_vocabulary_research.md"
  aget:validationRule: "Must have metadata header per session_metadata_v1.0.yaml"
```

---

## Conformance Levels

### Level 1: Basic (EARS-Compatible)

- All terms have `skos:prefLabel` and `skos:definition`
- Terms organized in clear sections
- No validation tooling required

### Level 2: Standard (Recommended)

- Level 1 requirements
- Hierarchical relationships documented (`skos:broader`/`skos:narrower`)
- Critical distinctions section
- Version history maintained

### Level 3: Full SKOS (Framework-Level)

- Level 2 requirements
- All 9 AGET relationship types documented where applicable
- SKOS validation tooling passes
- EARS projection generates valid output
- CI integration for vocabulary validation

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

### Evidence Base

This specification synthesizes patterns from 11 vocabulary documents:

| Document | Key Pattern Adopted |
|----------|---------------------|
| Supervisor CONTROLLED_VOCABULARY.md | Rich entry format, Critical Distinctions |
| Supervisor TERMINOLOGY.md | Deprecation handling, Version history |
| ____XXX____ GLOSSARY.md | "Why it matters" field |
| ____XXX___ Evaluation Glossary | Framework vs Domain split |
| ____XXX____ Ontology Spec | Numeric constants as vocabulary |
| ____XXX____ Glossary | Quick Reference table |

---

## Appendix: Decision Record

### Why SKOS?

Per ADR-001 evaluation:

| Option | Assessment |
|--------|------------|
| EARS Vocabulary only | Too limited (no hierarchies, no relationships) |
| Custom YAML | Reinventing the wheel |
| **SKOS + AGET Extensions** | **Selected**: W3C standard, extensible, tooling exists |

### SKOS Benefits

1. **Standards compliance**: W3C Recommendation since 2009
2. **Hierarchy built-in**: `skos:broader`/`skos:narrower`
3. **Extensible**: Custom `aget:*` properties for 9 relationship types
4. **Tooling**: Validators, reasoners available
5. **EARS compatible**: Simple projection for spec vocabulary sections

---

*AGET_GLOSSARY_STANDARD_SPEC_v1.0.md — Canonical glossary format for AGET framework*
*Created: 2025-12-21 by private-aget-framework-AGET*
*Foundation: ADR-001 (SKOS adoption) + Fleet pattern synthesis (R2, L339)*
*Enhancement: [aget-framework/aget#9](https://github.com/aget-framework/aget/issues/9)*
*Target: v2.11.0 (bundled with Memory Architecture Vision)*
