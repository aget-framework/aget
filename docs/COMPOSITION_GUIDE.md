# Capability Composition Guide

**Version**: 1.0.0
**Created**: 2025-12-25
**Purpose**: Guide practitioners in composing capabilities into agent configurations

---

## Table of Contents

1. [What is Composition?](#what-is-composition)
2. [The DAG Model](#the-dag-model)
3. [Template Manifest Structure](#template-manifest-structure)
4. [Composition Rules](#composition-rules)
5. [Conflict Resolution](#conflict-resolution)
6. [Validation Process](#validation-process)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## What is Composition?

**Composition** is the process of combining a base template with one or more capabilities to create a specialized agent configuration.

### The Composition Formula

```
Agent = Base Template + Capability₁ + Capability₂ + ... + Capabilityₙ
```

### Why Composition Matters

| Without Composition | With Composition |
|---------------------|------------------|
| Copy-paste code between agents | Define once, reuse everywhere |
| Inconsistent behaviors | Standardized, tested behaviors |
| Hard to update across fleet | Update capability, all agents benefit |
| No formal contracts | Validated requirements |

### Key Concepts

- **Base Template**: Foundation structure (advisor, worker, supervisor, etc.)
- **Capability**: Composable behavior set that can be added to any compatible template
- **Template Manifest**: YAML declaration of an agent's composition
- **Composition Rules**: Constraints that ensure valid combinations

---

## The DAG Model

AGET uses a **Directed Acyclic Graph (DAG)** model for capability composition.

### DAG Properties

```
         ┌──────────────────┐
         │   Base Template  │
         │    (advisor)     │
         └────────┬─────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ memory │ │ domain │ │ struct │
   │  mgmt  │ │  know  │ │ output │
   └────────┘ └────────┘ └────────┘
```

### DAG Guarantees

1. **No Cycles**: Capabilities cannot depend on each other in circular ways
2. **Deterministic Order**: Capability loading order is well-defined
3. **Prerequisite Validation**: Dependencies are checked before activation

### Composition Algebra

The composition operation follows these algebraic properties:

| Property | Formula | Meaning |
|----------|---------|---------|
| **Identity** | T + ∅ = T | Adding nothing leaves template unchanged |
| **Commutativity** | T + A + B = T + B + A | Order of capabilities doesn't matter* |
| **Idempotency** | T + A + A = T + A | Adding same capability twice = adding once |
| **Associativity** | (T + A) + B = T + (A + B) | Grouping doesn't affect result |

*Unless conflict resolution specifies order-dependent behavior

---

## Template Manifest Structure

Every agent's composition is declared in a **Template Manifest**.

### Basic Structure

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: agent-name
  version: 1.0.0
  author: author-name

composition:
  base_template: advisor
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
  composition_rules:
    conflict_resolution: error
```

### Section Reference

#### metadata
```yaml
metadata:
  name: my-agent-name           # Lowercase with hyphens
  version: 1.0.0                # Agent version (semantic)
  created: "2025-01-01"         # Creation date
  author: author-agent          # Creating agent
  status: draft|active|deprecated
```

#### composition.base_template
```yaml
composition:
  base_template: advisor        # One of: advisor, worker, supervisor,
                                #         consultant, developer, spec-engineer
```

#### composition.capabilities
```yaml
capabilities:
  - name: capability-name       # Must exist in specs/capabilities/
    version: ">=1.0.0"          # Semantic version constraint
    config:                     # Optional capability-specific config
      key: value
```

#### composition.composition_rules
```yaml
composition_rules:
  conflict_resolution: error    # error|first-wins|last-wins|merge
  strict_mode: true             # Require all capabilities to exist
```

---

## Composition Rules

The framework enforces five composition rules:

### R-COMP-001: No Duplicate Capabilities

Each capability can appear only once in a composition.

```yaml
# ❌ INVALID - duplicate capability
capabilities:
  - name: memory-management
  - name: memory-management

# ✅ VALID
capabilities:
  - name: memory-management
```

### R-COMP-002: Prerequisites Must Be Satisfied

If capability A requires capability B, B must be in the composition.

```yaml
# ❌ INVALID - collaboration requires domain-knowledge
capabilities:
  - name: collaboration

# ✅ VALID
capabilities:
  - name: domain-knowledge
  - name: collaboration
```

### R-COMP-003: No Behavior Name Collisions

Two capabilities cannot define behaviors with the same name (unless conflict resolution is configured).

```yaml
# If both memory-management and custom-cap define "step_back"
# → Conflict unless conflict_resolution is set
```

### R-COMP-004: Composability Check

Capabilities must be compatible with the base template.

```yaml
# If org-kb says composable_with: [supervisor]
# ❌ INVALID
composition:
  base_template: worker
  capabilities:
    - name: org-kb

# ✅ VALID
composition:
  base_template: supervisor
  capabilities:
    - name: org-kb
```

### R-COMP-005: Version Compatibility

Capability versions must satisfy declared constraints.

```yaml
# If memory-management is at 1.2.0
# ❌ INVALID
capabilities:
  - name: memory-management
    version: ">=2.0.0"

# ✅ VALID
capabilities:
  - name: memory-management
    version: ">=1.0.0"
```

---

## Conflict Resolution

When capabilities have overlapping behaviors, use conflict resolution strategies.

### Strategy: error (default)

```yaml
composition_rules:
  conflict_resolution: error
```

Behavior: Fail validation if any conflicts detected.

Use when: You want to be explicit about conflicts.

### Strategy: first-wins

```yaml
composition_rules:
  conflict_resolution: first-wins
```

Behavior: First capability in list takes precedence.

Use when: You have a preferred capability order.

### Strategy: last-wins

```yaml
composition_rules:
  conflict_resolution: last-wins
```

Behavior: Last capability in list takes precedence.

Use when: Later capabilities should override earlier.

### Strategy: merge

```yaml
composition_rules:
  conflict_resolution: merge
```

Behavior: Attempt to merge overlapping behaviors.

Use when: Behaviors complement rather than conflict.

---

## Validation Process

### Step 1: Schema Validation

```bash
python3 aget/validation/validate_template_manifest.py path/to/manifest.yaml
```

Validates:
- Required fields present
- Correct types
- Valid apiVersion and kind

### Step 2: Composition Validation

```bash
python3 aget/validation/validate_composition.py path/to/manifest.yaml \
  --specs specs/capabilities/
```

Validates:
- R-COMP-001 through R-COMP-005
- Prerequisite satisfaction
- Behavior conflict detection
- Composability checks

### Step 3: Contract Verification

For each capability in the composition, verify contracts:

```python
from tests.capability_architecture.test_capability_contracts import ContractEvaluator

evaluator = ContractEvaluator(agent_root)
for contract in capability.contracts:
    result = evaluator.evaluate_contract(contract)
    if not result.passed:
        print(f"Contract failed: {result.message}")
```

### Automated Validation

Run all composition tests:

```bash
python3 -m pytest aget/tests/capability_architecture/test_composition_validation.py -v
```

---

## Examples

### Example 1: Data Science Agent

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: data-science-aget
  version: 1.0.0

composition:
  base_template: advisor
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
      config:
        domain: data-science
    - name: structured-outputs
      version: ">=1.0.0"
      config:
        formats: [markdown, json, csv]
  composition_rules:
    conflict_resolution: error
```

**Resulting Agent**:
- Base: advisor template
- Behaviors: KB management + domain expertise + formatted outputs
- Use case: Data science consulting

### Example 2: Executive Advisor

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: executive-advisor-aget
  version: 1.0.0

composition:
  base_template: advisor
  capabilities:
    - name: org-kb
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
      config:
        domain: executive-strategy
    - name: structured-outputs
      version: ">=1.0.0"
      config:
        formats: [5W+H]
  composition_rules:
    conflict_resolution: error
```

**Resulting Agent**:
- Base: advisor template
- Behaviors: 5W+H KB + strategic expertise + structured outputs
- Use case: Executive decision support

### Example 3: Specification Owner

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: spec-owner-aget
  version: 1.0.0

composition:
  base_template: spec-engineer
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
      config:
        domain: specification-management
    - name: structured-outputs
      version: ">=1.0.0"
      config:
        formats: [yaml, markdown]
  composition_rules:
    conflict_resolution: error
```

### Example 4: Multi-Agent Collaboration

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: collaborative-advisor-aget
  version: 1.0.0

composition:
  base_template: advisor
  capabilities:
    - name: domain-knowledge
      version: ">=1.0.0"
    - name: collaboration
      version: ">=1.0.0"
      config:
        handoff_protocols: [work-request, escalation]
  composition_rules:
    conflict_resolution: error
```

**Resulting Agent**:
- Base: advisor template
- Behaviors: Domain expertise + cross-agent coordination
- Use case: Agent that works with other agents

---

## Troubleshooting

### Error: Missing Prerequisite

```
CONFLICT [missing_prerequisite]: Capability 'collaboration' requires
'domain-knowledge' which is not in composition
→ Resolution: Add 'domain-knowledge' to capabilities list
```

**Fix**: Add the required capability before the one that needs it.

### Error: Behavior Name Collision

```
CONFLICT [behavior_name_collision]: Behavior 'step_back' defined in
multiple capabilities: ['memory-management', 'custom-memory']
→ Resolution: Change conflict_resolution to 'first-wins', 'last-wins', or 'merge'
```

**Fix**: Either remove one capability or set conflict_resolution strategy.

### Error: Unknown Capability

```
⚠️ Unknown capability 'nonexistent-cap' - cannot check prerequisites
```

**Fix**: Create the capability spec or check the name spelling.

### Warning: Trigger Overlap

```
⚠️ Trigger phrase 'step back' matches multiple capabilities:
['memory-management', 'custom-cap']
```

**Note**: This is a warning, not an error. Multiple capabilities may legitimately respond to the same trigger.

### Error: Composability Mismatch

```
⚠️ Capability 'org-kb' may not be compatible with base_template 'worker'
```

**Fix**: Either use a compatible base template or update the capability's `composable_with` list.

---

## Best Practices

### 1. Start Simple

Begin with base template + 1-2 capabilities. Add more as needed.

### 2. Test Incrementally

Validate after each capability addition:
```bash
python3 aget/validation/validate_composition.py my-manifest.yaml --specs specs/capabilities/
```

### 3. Use Version Constraints

Prefer `>=1.0.0` over exact versions to allow capability updates.

### 4. Document Custom Configurations

```yaml
capabilities:
  - name: domain-knowledge
    config:
      domain: my-specialty  # What domain this agent specializes in
```

### 5. Check Prerequisites First

Before adding a capability, check its spec for prerequisites:
```yaml
spec:
  prerequisites:
    - domain-knowledge  # ← Must add this first
```

---

## References

- Capability Author Guide: `docs/CAPABILITY_AUTHOR_GUIDE.md`
- Composition Specification: `specs/schemas/COMPOSITION_SPEC_v1.0.md`
- Template Manifest Schema: `specs/schemas/TEMPLATE_MANIFEST_v1.0_SCHEMA.yaml`
- Capability Spec Schema: `specs/schemas/CAPABILITY_SPEC_v1.0_SCHEMA.yaml`
- Composition Validator: `validation/validate_composition.py`
- Theoretical Foundations: `.aget/evolution/L330_capability_composition_architecture.md`

---

*Composition Guide v1.0.0*
*Part of AGET Capability Composition Architecture*
