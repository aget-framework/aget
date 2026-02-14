# Ontology Directory

Formal vocabulary definitions for {{AGENT_NAME}}.

## Purpose

This directory stores the agent's domain ontology — the formal vocabulary that defines **what concepts exist** and **how they relate**. This is distinct from:

| Directory | Purpose | Analogy |
|-----------|---------|---------|
| `ontology/` | Schema (concepts, relationships) | Database schema |
| `knowledge/` | Instances (curated content) | Database rows |
| `.aget/` | Framework config (AGET vX) | Operating system |
| `specs/` | Requirements, designs | Engineering docs |

## Format: YAML + SKOS + EARS

Per L482 (Executable Ontology - SKOS+EARS Grounding), ontology files use:

### SKOS: What Concepts Exist

```yaml
concepts:
  - id: C001
    uri: aget:concept/<ConceptName>
    prefLabel: "<Human Label>"
    definition: "<Formal definition>"
    broader: null
    narrower: [<ChildConcepts>]
    related: [<RelatedConcepts>]
    theoreticalBasis:
      primary: "<Theory Name>"
      source: "<Citation>"
```

**SKOS Properties**:
- `prefLabel` — Canonical name
- `definition` — Formal definition
- `broader` — Taxonomic parent(s)
- `narrower` — Taxonomic children
- `related` — Non-hierarchical relationships
- `example` — Concrete instances

### EARS: What Behaviors Are Required (Optional)

```yaml
requirements:
  - id: R-DOM-001
    type: event_driven
    trigger: "<trigger condition>"
    system: <SystemName>
    response: "<system> SHALL <action>"
```

**EARS Templates**:
- **Ubiquitous**: `The <system> SHALL <action>`
- **Event-Driven**: `When <trigger>, the <system> SHALL <action>`
- **State-Driven**: `While <state>, the <system> SHALL <action>`
- **Optional**: `Where <feature>, the <system> SHALL <action>`
- **Unwanted**: `If <condition>, then the <system> SHALL NOT <action>`

## Naming Convention

```
ONTOLOGY_<domain>_v<major>.<minor>.yaml
```

Examples:
- `ONTOLOGY_{{DOMAIN}}_v1.0.yaml`

## Contents

| File | Description | Concepts |
|------|-------------|----------|
| *(empty — populate with domain ontology)* | | |

## Validation

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('ontology/ONTOLOGY_<domain>_v1.0.yaml'))"

# Future: SKOS compliance checker
# python3 aget/validation/validate_ontology_format.py ontology/
```

## Theoretical Grounding

| Theory | Application |
|--------|-------------|
| **SKOS** (W3C) | Vocabulary formalization standard |
| **EARS** (Rolls-Royce) | Requirements syntax for testability |
| **Formal Ontology** (Guarino) | Ontology as engineering artifact |
| **Applied Ontology** | Domain-specific, purpose-driven |

## Related

- `knowledge/` — Curated domain content (instances)
- `.aget/evolution/L482` — Executable Ontology pattern
- `.aget/evolution/L481` — Ontology-Driven Agent Creation
- `specs/` — Requirements and design specifications

## References

- [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- [EARS: Easy Approach to Requirements Syntax](https://alistairmavin.com/ears/)
- [Enterprise Knowledge: Ontology vs Knowledge Graph](https://enterprise-knowledge.com/whats-the-difference-between-an-ontology-and-a-knowledge-graph/)

---

*Created: {{DATE}} per PROJECT_PLAN_ontology_directory_standard_v1.0*
*Format: YAML + SKOS + EARS (L482)*
