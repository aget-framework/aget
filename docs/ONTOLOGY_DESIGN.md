# Ontology-Driven Design

> Moved from aget/README.md (v3.11.1) to reduce homepage length per REQ-HOM-F-005.

AGET uses **ontology-driven agent customization**:

```
Vocabulary -> Specification -> Implementation
```

| Layer | Artifact | Purpose |
|-------|----------|---------|
| **Vocabulary** | `ontology/ONTOLOGY_{archetype}.yaml` | Domain concepts (SKOS-compliant) |
| **Specification** | `specs/SKILL_{name}_SPEC.md` | Formal requirements (EARS patterns) |
| **Implementation** | `.claude/skills/{name}/` | Skill execution |

**Benefits**:
- **Precision**: Formal vocabulary prevents ambiguity
- **Consistency**: Same concepts across all archetype instances
- **Extensibility**: Add domain-specific terms to ontology

---

*See also: [AGET_VOCABULARY_SPEC](../specs/AGET_VOCABULARY_SPEC.md), [AGET_CORE_VOCABULARY](AGET_CORE_VOCABULARY.md)*
