# COMPOSITION_SPEC v1.0

**Version**: 1.0.1
**Date**: 2025-12-24
**Author**: aget-framework
**Status**: Approved
**Reference**: L330 (Capability Composition Architecture)

---

## Purpose

This specification defines the rules for composing agents from base templates and capabilities in the AGET framework. It formalizes the DAG-based composition model introduced in L330.

---

## Scope

### In Scope

- Composition algebra (how capabilities combine)
- Conflict detection rules
- DAG validation requirements
- Resolution strategies
- Validation process

### Out of Scope

- Individual capability definitions (see CAPABILITY_SPEC)
- Manifest structure (see TEMPLATE_MANIFEST_SPEC)
- Runtime behavior execution

---

## Composition Model

### Core Equation

```
Agent = Base_Template ⊕ Capability_1 ⊕ Capability_2 ⊕ ... ⊕ Capability_n
```

Where:
- `Base_Template` is one of: worker, advisor, supervisor, consultant, developer, spec-engineer
- `Capability_n` is a defined capability specification
- `⊕` is the composition operator

### Composition Operator (⊕)

The composition operator combines a base template or agent with a capability:

```
agent ⊕ capability → enhanced_agent
```

The operator:
- Adds capability behaviors to the agent
- Registers capability contracts
- Merges capability configurations
- Validates prerequisites

---

## Composition Algebra

### Axiom 1: Identity

```
agent ⊕ ∅ = agent
```

Composing with an empty capability set leaves the agent unchanged.

### Axiom 2: Commutativity

```
cap_A ⊕ cap_B = cap_B ⊕ cap_A
```

The order of capability composition does not affect the final result, assuming no conflicts.

**Exception**: When using `first-wins` or `last-wins` conflict resolution, order matters for conflicting capabilities.

### Axiom 3: Idempotency

```
cap_A ⊕ cap_A = cap_A
```

Composing the same capability twice has no additional effect.

**Enforcement**: Duplicate capabilities in a manifest result in a warning and deduplication.

### Axiom 4: Associativity

```
(cap_A ⊕ cap_B) ⊕ cap_C = cap_A ⊕ (cap_B ⊕ cap_C)
```

Grouping does not affect the composition result.

---

## Conflict Detection

### Conflict Types

| Type | Description | Severity | Detection |
|------|-------------|----------|-----------|
| **Duplicate Capability** | Same capability name, different version | WARNING | Name collision check |
| **Behavior Overlap** | Multiple capabilities define same behavior name | ERROR | Behavior name collision |
| **Contract Conflict** | Incompatible contract assertions | ERROR | Contract compatibility check |
| **Prerequisite Missing** | Required capability not in composition | ERROR | Prerequisite graph check |
| **Circular Dependency** | Capability A requires B, B requires A | ERROR | DAG cycle detection |
| **Version Incompatibility** | Capability versions incompatible | ERROR | Version constraint check |

### Detection Rules

#### R-COMP-001: Duplicate Capability Detection

```
WHEN manifest contains capabilities with same name but different versions
THEN system SHALL report duplicate capability warning
AND system SHALL use the first occurrence (or apply conflict_resolution strategy)
```

#### R-COMP-002: Behavior Overlap Detection

```
WHEN two capabilities define behaviors with identical names
THEN system SHALL report behavior overlap error
UNLESS conflict_resolution is set to merge, first-wins, or last-wins
```

#### R-COMP-003: Prerequisite Validation

```
WHEN capability specifies prerequisites in its specification
THEN composition SHALL include all prerequisite capabilities
OR system SHALL report prerequisite missing error
```

#### R-COMP-004: Cycle Detection

```
WHEN prerequisite graph contains a cycle
THEN system SHALL report circular dependency error
AND composition SHALL fail
```

#### R-COMP-005: Version Compatibility

```
WHEN capability specifies version constraints
THEN all dependent capabilities SHALL satisfy version constraints
OR system SHALL report version incompatibility error
```

---

## Conflict Resolution Strategies

### Strategy: error (Default)

```yaml
composition_rules:
  conflict_resolution: error
```

- Any conflict results in composition failure
- Safest option, requires explicit resolution
- Recommended for production manifests

### Strategy: first-wins

```yaml
composition_rules:
  conflict_resolution: first-wins
```

- Earlier capability in list takes precedence
- Later conflicting behaviors are ignored
- Useful for legacy compatibility

### Strategy: last-wins

```yaml
composition_rules:
  conflict_resolution: last-wins
```

- Later capability in list takes precedence
- Earlier conflicting behaviors are overridden
- Useful for override patterns

### Strategy: merge

```yaml
composition_rules:
  conflict_resolution: merge
```

- Attempt to merge conflicting behaviors
- Combines triggers, extends protocols
- May not always be possible (falls back to error)

---

## DAG Validation

### Validation Steps

1. **Parse Manifest**
   - Load manifest YAML
   - Validate against TEMPLATE_MANIFEST_SPEC schema
   - Extract composition section

2. **Load Capabilities**
   - For each capability in composition:
     - Load capability specification
     - Validate against CAPABILITY_SPEC schema
     - Extract prerequisites, behaviors, contracts

3. **Build Prerequisite Graph**
   - Create directed graph of prerequisites
   - Each capability is a node
   - Each prerequisite is an edge

4. **Detect Cycles**
   - Run topological sort on prerequisite graph
   - If sort fails, cycle exists → ERROR

5. **Check Prerequisites**
   - For each capability:
     - Verify all prerequisites in composition
     - If missing → ERROR

6. **Detect Conflicts**
   - Build behavior map (behavior_name → capability)
   - If multiple capabilities claim same behavior → conflict
   - Apply conflict resolution strategy

7. **Validate Versions**
   - Check version constraints
   - Verify compatibility

8. **Report Results**
   - Return validation result
   - List all errors, warnings
   - Include resolution suggestions

### Validation Result Structure

```yaml
validation_result:
  status: pass | fail | warning
  timestamp: "2025-12-24T00:00:00Z"
  manifest: manifest-name

  checks:
    - name: schema_valid
      status: pass
    - name: dag_acyclic
      status: pass
    - name: prerequisites_satisfied
      status: pass
    - name: no_conflicts
      status: pass
    - name: versions_compatible
      status: pass

  errors: []
  warnings: []

  suggestions: []
```

---

## Composition Process

### Step 1: Manifest Parsing

```python
def parse_manifest(manifest_path: str) -> TemplateManifest:
    """
    Load and validate manifest against schema.
    """
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    validate_schema(manifest, TEMPLATE_MANIFEST_SCHEMA)
    return TemplateManifest(manifest)
```

### Step 2: Capability Resolution

```python
def resolve_capabilities(manifest: TemplateManifest) -> List[Capability]:
    """
    Load all capability specifications.
    """
    capabilities = []
    for cap_ref in manifest.composition.capabilities:
        cap_spec = load_capability_spec(cap_ref.name, cap_ref.version)
        capabilities.append(cap_spec)
    return capabilities
```

### Step 3: DAG Construction

```python
def build_dag(capabilities: List[Capability]) -> DirectedGraph:
    """
    Build prerequisite DAG.
    """
    graph = DirectedGraph()
    for cap in capabilities:
        graph.add_node(cap.name)
        for prereq in cap.prerequisites:
            graph.add_edge(prereq, cap.name)
    return graph
```

### Step 4: Validation

```python
def validate_composition(manifest: TemplateManifest) -> ValidationResult:
    """
    Full composition validation.
    """
    result = ValidationResult()

    # Load capabilities
    capabilities = resolve_capabilities(manifest)

    # Build and validate DAG
    dag = build_dag(capabilities)
    if not dag.is_acyclic():
        result.add_error("Circular dependency detected")
        return result

    # Check prerequisites
    for cap in capabilities:
        for prereq in cap.prerequisites:
            if prereq not in [c.name for c in capabilities]:
                result.add_error(f"Missing prerequisite: {prereq}")

    # Check conflicts
    behavior_map = {}
    for cap in capabilities:
        for behavior in cap.behaviors:
            if behavior.name in behavior_map:
                result.add_conflict(behavior.name, cap.name, behavior_map[behavior.name])
            else:
                behavior_map[behavior.name] = cap.name

    # Apply resolution strategy
    if result.has_conflicts():
        result = apply_resolution(result, manifest.composition_rules)

    return result
```

### Step 5: Agent Instantiation

```python
def instantiate_agent(manifest: TemplateManifest) -> Agent:
    """
    Create agent from validated manifest.
    """
    # Validate first
    result = validate_composition(manifest)
    if not result.is_valid():
        raise CompositionError(result.errors)

    # Load base template
    agent = load_template(manifest.composition.base_template)

    # Compose capabilities
    for cap in manifest.composition.capabilities:
        agent = compose(agent, cap)

    return agent
```

---

## Behavioral Composition

### Behavior Merging Rules

When behaviors from different capabilities are composed:

| Aspect | Merge Strategy |
|--------|----------------|
| Triggers | Union (all triggers activate behavior) |
| Protocol | Sequence (protocols execute in order) |
| Output | Last capability's output definition |
| Contracts | Union (all contracts must pass) |

### Behavior Override Rules

When using `first-wins` or `last-wins`:

| Strategy | Trigger | Protocol | Output | Contracts |
|----------|---------|----------|--------|-----------|
| first-wins | First | First | First | Union |
| last-wins | Last | Last | Last | Union |

---

## Contract Composition

### Contract Compatibility

Contracts are compatible if:
1. They don't contradict each other
2. They can all be satisfied simultaneously
3. They reference valid paths/resources

### Contract Merging

```python
def merge_contracts(contracts: List[Contract]) -> List[Contract]:
    """
    Merge contracts from multiple capabilities.

    Rules:
    - Duplicate contracts (same name) are deduplicated
    - Conflicting assertions raise error
    - All contracts must pass for composition to be valid
    """
    merged = {}
    for contract in contracts:
        if contract.name in merged:
            if contract != merged[contract.name]:
                raise ContractConflict(contract.name)
        else:
            merged[contract.name] = contract
    return list(merged.values())
```

---

## Error Messages

### Standard Error Formats

```
COMP-001: Duplicate capability '{name}' with versions {v1} and {v2}
COMP-002: Behavior overlap: '{behavior}' defined by both '{cap1}' and '{cap2}'
COMP-003: Missing prerequisite: '{prereq}' required by '{cap}'
COMP-004: Circular dependency: {cap1} → {cap2} → ... → {cap1}
COMP-005: Version incompatibility: '{cap}' requires '{dep}' {constraint}, found {actual}
COMP-006: Contract conflict: '{contract}' has incompatible assertions
COMP-007: Invalid base template: '{template}'
COMP-008: Capability not found: '{cap}' version {version}
```

### Resolution Suggestions

Each error should include a resolution suggestion:

```
COMP-003: Missing prerequisite: 'memory-management' required by 'domain-knowledge'
  Suggestion: Add 'memory-management' to capabilities list

COMP-002: Behavior overlap: 'step_back' defined by both 'memory-management' and 'custom-kb'
  Suggestion: Use conflict_resolution: merge, or remove one capability
```

---

## Testing Composition

### Test Categories

1. **Valid Compositions**
   - All agent types compose successfully
   - No errors or warnings

2. **Invalid Compositions**
   - Missing prerequisites detected
   - Cycles detected
   - Conflicts detected (with error strategy)

3. **Edge Cases**
   - Empty capability list
   - Single capability
   - Maximum capability count
   - Deep prerequisite chains

4. **Resolution Strategies**
   - first-wins resolves correctly
   - last-wins resolves correctly
   - merge combines behaviors

### Example Test Cases

```python
class TestComposition:
    def test_valid_data_science_aget(self):
        """Data Science Aget composes correctly."""
        manifest = load_manifest("data-science-aget.yaml")
        result = validate_composition(manifest)
        assert result.is_valid()

    def test_missing_prerequisite(self):
        """Missing prerequisite is detected."""
        manifest = create_manifest(
            base="advisor",
            capabilities=[
                {"name": "domain-knowledge", "version": "1.0.0"}
                # Missing: memory-management (prerequisite)
            ]
        )
        result = validate_composition(manifest)
        assert not result.is_valid()
        assert "COMP-003" in result.errors[0]

    def test_circular_dependency(self):
        """Circular dependencies are detected."""
        # Create capabilities with circular prereqs
        result = validate_composition(circular_manifest)
        assert not result.is_valid()
        assert "COMP-004" in result.errors[0]
```

---

## Implementation Notes

### Performance Considerations

- Capability specs should be cached after first load
- DAG construction is O(n) where n = capability count
- Cycle detection is O(n + e) using topological sort
- Conflict detection is O(n × b) where b = behaviors per capability

### Extensibility

The composition model is extensible:
- New conflict resolution strategies can be added
- Custom validation rules can be registered
- Capability-specific composition logic supported

---

## Authority Model

```yaml
authority:
  applies_to: "composition_operations"

  governed_by:
    spec: "COMPOSITION_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "Compose agents from base templates and capabilities using the composition operator"
      - "Run DAG validation on capability prerequisite graphs"
      - "Detect and report composition conflicts (duplicate, overlap, circular)"
      - "Apply conflict resolution strategies (error, first-wins, last-wins, merge)"
      - "Validate version compatibility of composed capabilities"
    requires_approval:
      - action: "Add new composition axioms or modify existing algebra"
        approver: "aget-framework maintainer"
      - action: "Add new conflict resolution strategies"
        approver: "aget-framework maintainer"
      - action: "Change prerequisite validation rules"
        approver: "principal"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Vocabulary

Domain terms for the Composition specification:

```yaml
vocabulary:
  meta:
    domain: "composition"
    version: "1.0.0"
    inherits: "aget_core"

  terms:
    Composition_Operator:
      skos:definition: "Binary operator (denoted as a circled plus) that combines a base template or agent with a capability to produce an enhanced agent"
      skos:notation: "⊕"
    Base_Template:
      skos:definition: "Starting archetype template from which an agent is composed, such as worker, advisor, supervisor, consultant, developer, or spec-engineer"
    Capability:
      skos:definition: "A defined specification that adds behaviors, contracts, and configuration to an agent through the composition operator"
    Conflict_Resolution_Strategy:
      skos:definition: "Policy for handling behavior overlaps during composition, one of: error, first-wins, last-wins, or merge"
      skos:narrower: ["Strategy_Error", "Strategy_First_Wins", "Strategy_Last_Wins", "Strategy_Merge"]
    Prerequisite_Graph:
      skos:definition: "Directed graph where nodes represent capabilities and edges represent prerequisite dependencies, which must be acyclic (DAG)"
    Behavior_Overlap:
      skos:definition: "Conflict condition where two or more capabilities define behaviors with identical names in the same composition"
    DAG_Validation:
      skos:definition: "Process of verifying that the capability prerequisite graph forms a directed acyclic graph with no cycles, missing prerequisites, or version incompatibilities"
    Composition_Algebra:
      skos:definition: "Mathematical framework governing capability composition through four axioms: identity, commutativity, idempotency, and associativity"
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-COMPOSE-001 | R-COMP-001 | automated | Verify duplicate capability detection reports warning for same-name different-version capabilities |
| V-COMPOSE-002 | R-COMP-002 | automated | Verify behavior overlap detection reports error when two capabilities define identical behavior names |
| V-COMPOSE-003 | R-COMP-003 | automated | Verify prerequisite validation reports error when required capabilities are missing from composition |
| V-COMPOSE-004 | R-COMP-004 | automated | Verify cycle detection reports error and fails composition when prerequisite graph contains a cycle |
| V-COMPOSE-005 | R-COMP-005 | automated | Verify version constraint checking reports error for incompatible capability versions |
| V-COMPOSE-006 | R-COMP-006-01 | automated | Verify composition graphs are validated as acyclic (DAG property) |
| V-COMPOSE-007 | R-COMP-006-02 | automated | Verify declared capability dependencies exist in the capability registry |
| V-COMPOSE-008 | R-COMP-006-03 | automated | Verify circular capability inheritance chains are rejected |

### Validation Commands

```bash
# Run composition validation (V-COMPOSE-001 through V-COMPOSE-005)
python3 validate_composition.py --manifest manifest.yaml

# Run DAG cycle detection (V-COMPOSE-004, V-COMPOSE-006)
python3 validate_composition.py --manifest manifest.yaml --check-dag

# Run full composition test suite (V-COMPOSE-001 through V-COMPOSE-008)
python3 -m pytest tests/test_composition.py -v
```

---

## References

| Document | Purpose |
|----------|---------|
| L330 | Capability Composition Architecture |
| L331 | Theoretical Foundations |
| CAPABILITY_SPEC_v1.0_SCHEMA | Capability schema |
| TEMPLATE_MANIFEST_v1.0_SCHEMA | Manifest schema |

### R-COMP-006: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| R-COMP-006-01 | ubiquitous | The SYSTEM shall validate that capability composition graphs are acyclic (DAG property). |
| R-COMP-006-02 | conditional | IF a template declares a capability dependency, THEN the SYSTEM shall verify that dependency exists in the capability registry. |
| R-COMP-006-03 | prohibited | The SYSTEM shall NOT allow circular capability inheritance chains. |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.1 | 2026-03-17 | Added R-COMP-006: EARS System-Level Requirements (L682 L0→L1 uplift) |
| 1.0.0 | 2025-12-24 | Initial specification |

---

*COMPOSITION_SPEC v1.0*
*Defines rules for DAG-based agent composition*
*Part of AGET Capability Composition Architecture (L330)*
