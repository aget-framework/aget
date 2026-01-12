# {Type} Domain Vocabulary

**Version**: 1.0.0
**Status**: Active
**Owner**: template-{type}-aget
**Created**: YYYY-MM-DD
**Updated**: YYYY-MM-DD
**Scope**: Template vocabulary (DRIVES instance behavior per L481)
**Archetype**: {Type}
**Template**: VOCABULARY_TEMPLATE_v3.3

---

## Meta

```yaml
vocabulary:
  meta:
    domain: "{type_lowercase}"
    version: "1.0.0"
    owner: "template-{type}-aget"
    created: "YYYY-MM-DD"
    theoretical_basis:
      - "L481: Ontology-Driven Agent Creation"
      - "L482: Executable Ontology - SKOS+EARS Grounding"
    archetype: "{Type}"
    concept_count: 15  # Minimum required
```

---

## Concept Scheme

```yaml
{Type}_Vocabulary:
  skos:prefLabel: "{Type} Vocabulary"
  skos:definition: "Vocabulary for {type} domain agents"
  skos:hasTopConcept:
    - {Type}_Core_Concepts
    - {Type}_Domain_Concepts
    - {Type}_Process_Concepts
  rdf:type: skos:ConceptScheme
```

---

## Core Concepts (5 minimum)

### {Concept_1}

```yaml
{Concept_1}:
  skos:prefLabel: "{Concept 1}"
  skos:definition: "{Definition of core concept 1}"
  skos:broader: {Type}_Core_Concepts
  skos:inScheme: {Type}_Vocabulary
  skos:related: [{Related_Concept}]
```

### {Concept_2}

```yaml
{Concept_2}:
  skos:prefLabel: "{Concept 2}"
  skos:definition: "{Definition of core concept 2}"
  skos:broader: {Type}_Core_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Concept_3}

```yaml
{Concept_3}:
  skos:prefLabel: "{Concept 3}"
  skos:definition: "{Definition of core concept 3}"
  skos:broader: {Type}_Core_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Concept_4}

```yaml
{Concept_4}:
  skos:prefLabel: "{Concept 4}"
  skos:definition: "{Definition of core concept 4}"
  skos:broader: {Type}_Core_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Concept_5}

```yaml
{Concept_5}:
  skos:prefLabel: "{Concept 5}"
  skos:definition: "{Definition of core concept 5}"
  skos:broader: {Type}_Core_Concepts
  skos:inScheme: {Type}_Vocabulary
```

---

## Domain Concepts (5 minimum)

### {Domain_Concept_1}

```yaml
{Domain_Concept_1}:
  skos:prefLabel: "{Domain Concept 1}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Domain_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Domain_Concept_2}

```yaml
{Domain_Concept_2}:
  skos:prefLabel: "{Domain Concept 2}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Domain_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Domain_Concept_3}

```yaml
{Domain_Concept_3}:
  skos:prefLabel: "{Domain Concept 3}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Domain_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Domain_Concept_4}

```yaml
{Domain_Concept_4}:
  skos:prefLabel: "{Domain Concept 4}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Domain_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Domain_Concept_5}

```yaml
{Domain_Concept_5}:
  skos:prefLabel: "{Domain Concept 5}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Domain_Concepts
  skos:inScheme: {Type}_Vocabulary
```

---

## Process Concepts (5 minimum)

### {Process_Concept_1}

```yaml
{Process_Concept_1}:
  skos:prefLabel: "{Process Concept 1}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Process_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Process_Concept_2}

```yaml
{Process_Concept_2}:
  skos:prefLabel: "{Process Concept 2}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Process_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Process_Concept_3}

```yaml
{Process_Concept_3}:
  skos:prefLabel: "{Process Concept 3}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Process_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Process_Concept_4}

```yaml
{Process_Concept_4}:
  skos:prefLabel: "{Process Concept 4}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Process_Concepts
  skos:inScheme: {Type}_Vocabulary
```

### {Process_Concept_5}

```yaml
{Process_Concept_5}:
  skos:prefLabel: "{Process Concept 5}"
  skos:definition: "{Definition}"
  skos:broader: {Type}_Process_Concepts
  skos:inScheme: {Type}_Vocabulary
```

---

## Concept Relationships

```yaml
relationships:
  hierarchical:
    - parent: {Type}_Core_Concepts
      children: [{Concept_1}, {Concept_2}, {Concept_3}, {Concept_4}, {Concept_5}]
    - parent: {Type}_Domain_Concepts
      children: [{Domain_Concept_1}, {Domain_Concept_2}, {Domain_Concept_3}, {Domain_Concept_4}, {Domain_Concept_5}]
    - parent: {Type}_Process_Concepts
      children: [{Process_Concept_1}, {Process_Concept_2}, {Process_Concept_3}, {Process_Concept_4}, {Process_Concept_5}]

  associative:
    - subject: {Concept_1}
      predicate: skos:related
      object: {Domain_Concept_1}
    - subject: {Process_Concept_1}
      predicate: skos:related
      object: {Concept_2}
```

---

## EKO Cross-References

Per AGET_EXECUTABLE_KNOWLEDGE_SPEC.md:

| Vocabulary Term | EKO Term | Relationship |
|-----------------|----------|--------------|
| {Concept_1} | EKO:{Artifact_Type} | skos:exactMatch |
| {Domain_Concept_1} | EKO:{Pattern} | skos:closeMatch |
| {Process_Concept_1} | EKO:{Process} | skos:broadMatch |

---

## Extension Points

Instances extending this template vocabulary should:

1. Add domain-specific terms under appropriate broader concepts
2. Maintain SKOS compliance (prefLabel, definition, broader/narrower)
3. Reference foundation L-docs where applicable
4. Use `research_status` for terms under investigation
5. Maintain ≥15 concepts total
6. Include EKO cross-references for key terms

---

## Validation

```bash
# Validate SKOS compliance
python3 validation/validate_ontology_compliance.py --file {Type}_VOCABULARY.md

# Check concept count (minimum 15)
grep -c "skos:prefLabel" {Type}_VOCABULARY.md
```

---

## References

- L481: Ontology-Driven Agent Creation
- L482: Executable Ontology - SKOS+EARS Grounding
- R-REL-015: Template Ontology Conformance
- AGET_VOCABULARY_SPEC.md
- AGET_EXECUTABLE_KNOWLEDGE_SPEC.md
- {Type}_SPEC.md

---

*{Type}_VOCABULARY.md v1.0.0 — SKOS-compliant template vocabulary*
*Template: VOCABULARY_TEMPLATE_v3.3*
*Generated: YYYY-MM-DD*
