# AGET Component Library

**Version**: 3.0.0
**Location**: `aget/components/`

---

## Overview

The AGET Component Library provides reusable capability definitions that templates reference using the `$ref:` syntax. Components enable composition while ensuring consistency across the framework.

## Directory Structure

```
components/
├── governance/                    # Governance capabilities
│   ├── capability-governance-balanced.yaml
│   ├── capability-governance-rigorous.yaml
│   └── capability-governance-minimal.yaml
│
├── core/                          # Universal capabilities
│   ├── capability-session-protocols.yaml
│   ├── capability-evolution-tracking.yaml
│   └── capability-memory-management.yaml
│
└── archetype/                     # Archetype-specific capabilities
    ├── advisor/
    │   ├── capability-recommendation.yaml
    │   ├── capability-analysis.yaml
    │   ├── capability-teaching.yaml
    │   └── capability-persona-modes.yaml
    │
    ├── developer/
    │   ├── capability-code-implementation.yaml
    │   ├── capability-debugging.yaml
    │   ├── capability-testing.yaml
    │   ├── capability-code-review.yaml
    │   ├── capability-refactoring.yaml
    │   └── capability-documentation.yaml
    │
    ├── supervisor/
    │   ├── capability-fleet-coordination.yaml
    │   ├── capability-portfolio-governance.yaml
    │   ├── capability-release-approval.yaml
    │   └── capability-work-delegation.yaml
    │
    ├── consultant/
    │   └── capability-domain-expertise.yaml
    │
    ├── spec-engineer/
    │   ├── capability-ears-authoring.yaml
    │   └── capability-traceability.yaml
    │
    ├── executive/
    │   └── capability-strategic-planning.yaml
    │
    ├── analyst/
    │   └── capability-data-analysis.yaml
    │
    ├── reviewer/
    │   └── capability-quality-gates.yaml
    │
    ├── operator/
    │   ├── capability-deployment.yaml
    │   └── capability-incident-response.yaml
    │
    ├── architect/
    │   ├── capability-architecture-design.yaml
    │   └── capability-trade-off-analysis.yaml
    │
    └── researcher/
        ├── capability-literature-review.yaml
        └── capability-hypothesis-testing.yaml
```

## Component Categories

### Governance (3 components)
Control how agents operate and make decisions.

| Component | Description |
|-----------|-------------|
| `capability-governance-balanced` | Standard governance for most agents |
| `capability-governance-rigorous` | Heightened governance for production/supervisory |
| `capability-governance-minimal` | Lightweight for exploratory agents |

### Core (3 components)
Universal capabilities required by all agents.

| Component | Description |
|-----------|-------------|
| `capability-session-protocols` | Session lifecycle management |
| `capability-evolution-tracking` | Learning document management |
| `capability-memory-management` | 6-layer memory architecture |

### Archetype-Specific (20+ components)
Capabilities specific to agent archetypes.

## Component Schema

Each component follows this structure:

```yaml
capability:
  id: capability-{name}
  name: Human readable name
  version: 3.0.0
  category: governance | core | archetype
  archetype: (if archetype-specific)

  description: |
    What this capability provides.

  # Capability-specific configuration
  behaviors: {}
  constraints: []
  compatible_archetypes: []

  theoretical_basis:
    - Foundation: Explanation
```

## Using Components

Reference components in template manifests:

```yaml
composition:
  persona:
    governance: $ref: aget/components/governance/capability-governance-balanced.yaml

capabilities:
  - capability-governance-balanced
  - capability-session-protocols
  - capability-evolution-tracking
```

## Validation

Run composition reference validation:

```bash
python3 aget/validation/validate_composition_refs.py template-worker-aget/
```

## Adding New Components

1. Identify need for reusable capability
2. Choose appropriate category/archetype
3. Create YAML file following schema
4. Reference in template manifests
5. Update this README

---

*AGET Component Library v3.0.0*
*Part of the 5D Composition Architecture*
