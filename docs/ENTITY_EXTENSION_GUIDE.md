# Entity Extension Guide

**Version**: 1.0.0
**Status**: Active (v3.4.0)
**Author**: aget-framework
**Reference**: L459 (Core Entity Vocabulary Vision), AGET_VOCABULARY_SPEC Part 6, CAP-TPL-012

---

## Overview

AGET agents work with common domain entities like Person, Organization, Document, and Task. Instead of reinventing these entities in each agent, the Core Entity Vocabulary provides standardized definitions that agents inherit by default and extend only when domain-specific requirements demand.

This guide explains how to:
1. Inherit core entities in your agent's manifest
2. Extend entities with domain-specific attributes
3. Add custom relationships
4. Validate your entity declarations

---

## Quick Start

### Basic Inheritance

Add an `entities:` section to your `manifest.yaml`:

```yaml
# manifest.yaml
entities:
  inherits:
    - Person
    - Document
    - Task
```

This gives your agent access to all attributes and relationships defined in the Core Entity Vocabulary for Person, Document, and Task.

### With Extensions

For domain-specific requirements, extend inherited entities:

```yaml
entities:
  inherits:
    - Person
    - Organization
    - Document

  extends:
    Person:
      attributes:
        - bar_number: {type: string}
        - jurisdiction: {type: string}
    Document:
      attributes:
        - confidentiality: {type: enum, values: [public, confidential, privileged]}
      relationships:
        - subject_of: {target: Legal_Matter, cardinality: "0:many"}
```

---

## Core Entities Reference

The Core Entity Vocabulary defines 8 entities organized into upper-level categories:

### Upper-Level Categories

| Category | Description | Entities |
|----------|-------------|----------|
| **Continuant** | Persists through time | Person, Organization, Document, Project |
| **Occurrent** | Happens in time | Event, Task |
| **Abstract** | Non-physical concepts | Decision, Requirement |

### Entity Summary

| Entity | Required Attributes | Common Relationships |
|--------|---------------------|---------------------|
| **Person** | name | affiliated_with, authors, makes, assigned_to |
| **Organization** | name | has_member, owns, produces, parent_of |
| **Document** | title | authored_by, produced_by, references, supersedes |
| **Decision** | description, date | made_by, affects, documented_in, supersedes |
| **Event** | name | involves, hosted_by, produces, results_in |
| **Task** | description | assignee, part_of, blocked_by, implements |
| **Project** | name | owned_by, has_task, has_requirement, produces |
| **Requirement** | identifier, description | source, implemented_by, verified_by |

For complete definitions, see `AGET_VOCABULARY_SPEC.md` Part 6.

---

## Inheritance Rules

Entity inheritance follows five rules (R-ENT-001 through R-ENT-005):

### R-ENT-001: Full Base Attributes

When you inherit an entity, you get ALL its base attributes. You cannot remove them.

```yaml
# Person comes with: name (required), email, identifier, roles
entities:
  inherits:
    - Person  # Automatically includes name, email, identifier, roles
```

### R-ENT-002: Additive Extensions Only

Extensions can only ADD attributes, not remove or replace base attributes.

```yaml
# CORRECT: Adding new attributes
extends:
  Person:
    attributes:
      - employee_id: {type: string}    # New attribute
      - department: {type: string}     # New attribute

# INCORRECT: Cannot remove base attributes
# (There's no syntax for this, by design)
```

### R-ENT-003: New Relationships Allowed

Extensions can add new relationships to other entities.

```yaml
extends:
  Document:
    relationships:
      - classified_by: {target: Classification, cardinality: "1:1"}
      - reviewed_by: {target: Person, cardinality: "0:many"}
```

### R-ENT-004: Type Narrowing (Not Widening)

You can narrow types (string -> enum), but not widen them.

```yaml
# CORRECT: Narrowing string to enum
extends:
  Task:
    attributes:
      - status: {type: enum, values: [backlog, in_progress, review, done]}

# INCORRECT: Widening enum to string
# (Would break existing consumers)
```

### R-ENT-005: Compatibility Guarantee

Extended entities remain compatible with consumers expecting the base entity.

If code expects a `Person` with `name`, your extended `Legal_Person` with `name` + `bar_number` will work because `name` is still present.

---

## Extension Examples

### Example 1: Legal Domain Agent

A legal practice management agent needs attorneys and case documents:

```yaml
# manifest.yaml for legal-practice-aget

entities:
  inherits:
    - Person
    - Organization
    - Document
    - Task
    - Project

  extends:
    Person:
      attributes:
        - bar_number: {type: string}
        - jurisdiction: {type: string}
        - practice_areas: {type: array, items: string}
        - billable_rate: {type: number}
      relationships:
        - represents: {target: Organization, cardinality: "0:many"}
        - assigned_cases: {target: Legal_Matter, cardinality: "0:many"}

    Document:
      attributes:
        - document_type: {type: enum, values: [pleading, motion, contract, memo, letter]}
        - confidentiality: {type: enum, values: [public, confidential, privileged]}
        - court_filed: {type: boolean}
        - filing_date: {type: date}
      relationships:
        - filed_in: {target: Court, cardinality: "0:1"}
        - subject_of: {target: Legal_Matter, cardinality: "1:1"}

    Organization:
      attributes:
        - client_type: {type: enum, values: [individual, corporation, government, nonprofit]}
        - billing_address: {type: string}
        - matter_limit: {type: number}
      relationships:
        - primary_contact: {target: Person, cardinality: "1:1"}
```

### Example 2: Research Lab Agent

A research management agent needs publications and experiments:

```yaml
# manifest.yaml for research-lab-aget

entities:
  inherits:
    - Person
    - Organization
    - Document
    - Project
    - Requirement

  extends:
    Person:
      attributes:
        - orcid: {type: string}
        - h_index: {type: number}
        - research_interests: {type: array, items: string}
      relationships:
        - affiliated_labs: {target: Organization, cardinality: "0:many"}
        - publications: {target: Document, cardinality: "0:many"}

    Document:
      attributes:
        - document_type: {type: enum, values: [paper, preprint, thesis, grant, dataset]}
        - doi: {type: string}
        - peer_reviewed: {type: boolean}
        - citation_count: {type: number}
      relationships:
        - cites: {target: Document, cardinality: "0:many"}
        - funded_by: {target: Grant, cardinality: "0:many"}

    Project:
      attributes:
        - funding_source: {type: string}
        - grant_number: {type: string}
        - irb_approved: {type: boolean}
      relationships:
        - principal_investigator: {target: Person, cardinality: "1:1"}
        - co_investigators: {target: Person, cardinality: "0:many"}
```

### Example 3: DevOps Agent (Minimal Extension)

A DevOps agent primarily uses Task and Event without heavy extensions:

```yaml
# manifest.yaml for devops-aget

entities:
  inherits:
    - Person
    - Task
    - Event
    - Document

  extends:
    Task:
      attributes:
        - sprint_id: {type: string}
        - story_points: {type: number}
        - environment: {type: enum, values: [dev, staging, prod]}

    Event:
      attributes:
        - incident_severity: {type: enum, values: [sev1, sev2, sev3, sev4]}
        - mttr_minutes: {type: number}
        - runbook_ref: {type: string}
```

---

## Validation

Use the `validate_entity_inheritance.py` validator to check your manifest:

```bash
# Validate a specific manifest
python3 validation/validate_entity_inheritance.py manifest.yaml

# Validate with verbose output
python3 validation/validate_entity_inheritance.py -v manifest.yaml

# Validate an agent directory
python3 validation/validate_entity_inheritance.py --dir /path/to/agent

# List available core entities
python3 validation/validate_entity_inheritance.py --list-entities
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Unknown entity 'X'" | Inheriting non-existent entity | Use only: Person, Organization, Document, Decision, Event, Task, Project, Requirement |
| "Cannot extend 'X' - not in inherits" | Extending without inheriting | Add entity to `inherits:` first |
| "'X.attributes' must be a list" | Wrong syntax | Use YAML list syntax: `- name: {type: string}` |

---

## Best Practices

### 1. Start Minimal

Inherit only what you need. Adding entities later is easy; removing dependencies is hard.

```yaml
# Good: Start with what you actually use
entities:
  inherits:
    - Person
    - Task

# Avoid: Inheriting "just in case"
# entities:
#   inherits:
#     - Person
#     - Organization
#     - Document
#     - Decision
#     - Event
#     - Task
#     - Project
#     - Requirement
```

### 2. Extend, Don't Redefine

If your domain needs a "Customer", don't create a new entity. Extend Person or Organization:

```yaml
# Good: Extension
extends:
  Organization:
    attributes:
      - customer_tier: {type: enum, values: [standard, premium, enterprise]}
      - account_manager: {type: string}

# Avoid: Parallel definition (creates confusion)
# entities:
#   custom:
#     Customer:
#       ...
```

### 3. Document Extensions

When adding domain-specific attributes, document their purpose:

```yaml
extends:
  Person:
    attributes:
      # Legal domain: Bar association membership
      - bar_number: {type: string}
      # Geographic scope of practice
      - jurisdiction: {type: string}
```

### 4. Use Standard Types

Prefer standard YAML types for attributes:

| Type | Use For | Example |
|------|---------|---------|
| `string` | Free text | `name: {type: string}` |
| `number` | Integers/floats | `age: {type: number}` |
| `boolean` | True/false | `active: {type: boolean}` |
| `date` | ISO dates | `created: {type: date}` |
| `enum` | Fixed choices | `status: {type: enum, values: [a, b, c]}` |
| `array` | Lists | `tags: {type: array, items: string}` |

---

## Migration Guide

### Adding Entities to Existing Agents

1. **Identify entity usage**: Scan your agent's knowledge and sessions for entity-like concepts
2. **Map to core entities**: Person, Organization, Document, Decision, Event, Task, Project, Requirement
3. **Add inheritance**: Update manifest.yaml with `entities.inherits`
4. **Add extensions**: If domain-specific attributes exist, add `entities.extends`
5. **Validate**: Run `validate_entity_inheritance.py`
6. **Update docs**: Document entity usage in AGENTS.md

### Example Migration

Before (implicit entities):
```markdown
<!-- In knowledge/contacts.md -->
## John Smith
- Email: john@example.com
- Role: Primary stakeholder
```

After (explicit inheritance):
```yaml
# manifest.yaml
entities:
  inherits:
    - Person
```

```yaml
# In structured knowledge
contacts:
  - entity: Person
    name: John Smith
    email: john@example.com
    roles: [primary_stakeholder]
```

---

## Relationship to EKO

Core Entity Vocabulary and Executable Knowledge Ontology (EKO) are complementary:

| Aspect | Core Entities (This Guide) | EKO |
|--------|---------------------------|-----|
| Focus | Domain objects (what agents WORK WITH) | Knowledge artifacts (what agents DO) |
| Examples | Person, Document, Task | SOP, Runbook, Playbook |
| Category | Continuant/Occurrent/Abstract | Determinism/Reusability axes |
| Reference | VOCABULARY_SPEC Part 6 | EXECUTABLE_KNOWLEDGE_SPEC |

An agent might inherit `Task` (core entity) while producing `Runbook` (EKO artifact):

```yaml
entities:
  inherits:
    - Task
    - Document

# The agent produces Runbook documents (EKO type)
# that describe how to complete Tasks (core entity)
```

---

## FAQ

### Q: Do I have to use entity inheritance?

No. The `entities:` section is optional. However, using it provides:
- Standardized vocabulary across agents
- Validation of entity usage
- Compatibility with entity-aware tools

### Q: Can I define custom entities not in the core vocabulary?

The current spec focuses on inheritance and extension of core entities. Custom entity definition (beyond the 8 core entities) is planned for v4.0.0+.

### Q: What if I need a relationship not in the base entity?

Add it in `extends:`. See R-ENT-003.

### Q: How do entities relate to memory/knowledge?

Entities define the schema; knowledge instances are the data. When you record "John Smith is a Person with email X", you're creating a knowledge instance conforming to the Person entity schema.

---

## References

- **L459**: Core Entity Vocabulary Vision
- **AGET_VOCABULARY_SPEC Part 6**: Entity definitions
- **AGET_TEMPLATE_SPEC CAP-TPL-012**: Manifest entity section
- **validate_entity_inheritance.py**: Validator source

---

*ENTITY_EXTENSION_GUIDE.md v1.0.0 - Core Entity Vocabulary for AGET Agents*
