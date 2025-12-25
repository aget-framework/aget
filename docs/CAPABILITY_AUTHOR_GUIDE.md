# Capability Author Guide

**Version**: 1.0.0
**Created**: 2025-12-25
**Purpose**: Enable practitioners to create new AGET capabilities

---

## Table of Contents

1. [What is a Capability?](#what-is-a-capability)
2. [When to Create a Capability](#when-to-create-a-capability)
3. [Capability Specification Structure](#capability-specification-structure)
4. [Step-by-Step Creation Process](#step-by-step-creation-process)
5. [Validation Checklist](#validation-checklist)
6. [Examples](#examples)
7. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
8. [Theoretical Grounding Requirements](#theoretical-grounding-requirements)

---

## What is a Capability?

A **capability** is a composable unit of agent behavior that can be added to any base template. Capabilities enable:

- **Reuse**: Define behavior once, apply to many agents
- **Composition**: Combine capabilities to create specialized agents
- **Standardization**: Consistent behaviors across the fleet
- **Validation**: Testable contracts for quality assurance

### Capability vs. Template

| Aspect | Template | Capability |
|--------|----------|------------|
| Purpose | Define base agent structure | Add specific behaviors |
| Scope | Complete agent foundation | Focused behavior set |
| Composition | Standalone | Composable with templates |
| Examples | worker, advisor, supervisor | memory-management, domain-knowledge |

### The Capability Composition Model

```
Agent = Base Template + Capability₁ + Capability₂ + ... + Capabilityₙ
```

Example:
```
Data Science Aget = advisor + domain-knowledge + structured-outputs + memory-management
```

---

## When to Create a Capability

### Create a Capability When:

1. **Multiple agents need the same behavior**
   - If 3+ agents would benefit, consider a capability

2. **Behavior is independent of domain**
   - Can be applied regardless of agent's specialty

3. **Behavior has clear contracts**
   - Can define testable requirements

4. **Behavior has theoretical grounding**
   - Aligns with established patterns (L331, L332)

### Don't Create a Capability When:

1. **Behavior is domain-specific**
   - Use domain documentation instead

2. **Only one agent needs it**
   - Keep as agent-specific pattern

3. **Behavior is too granular**
   - Combine related behaviors into one capability

4. **Behavior overlaps significantly with existing capability**
   - Extend existing capability instead

---

## Capability Specification Structure

Every capability is defined by a YAML specification following the `CAPABILITY_SPEC` schema.

### Required Sections

```yaml
apiVersion: aget.framework/v1
kind: CapabilitySpecification

metadata:
  name: capability-name           # Lowercase with hyphens
  version: 1.0.0                  # Semantic versioning
  created: "YYYY-MM-DD"
  author: agent-name
  status: draft|review|approved|deprecated
  target_version: vX.Y.Z          # Framework version

spec:
  name: capability-name
  display_name: Capability Name
  category: Category Name
  purpose: |
    What this capability enables agents to do.
  insight: |
    Core insight or principle behind this capability.
  composable_with:
    - Template or capability names
  prerequisites:
    - Required capabilities or conditions

behaviors:
  - name: behavior_name
    display_name: Behavior Name
    description: What this behavior does
    trigger:
      explicit: ["trigger phrases"]
      implicit: ["trigger conditions"]
    protocol:
      - Step 1
      - Step 2
    output: What the behavior produces
    reference: path/to/detailed/doc.md

theoretical_basis:
  primary: Primary Theory
  secondary:
    - Other theories
  rationale: |
    Why this theoretical grounding

contracts:
  - name: contract_name
    assertion: directory_exists|file_exists|file_contains|custom
    path: path/to/check
    description: What this contract verifies

adoption:
  priority: P0|P1|P2|P3
  demand: Description of agent demand
  rollout_phases:
    - phase: 1
      name: Pilot
      agents: [agent-list]
      version: vX.Y.Z
  success_metrics:
    - metric: Metric name
      target: Target value
      measurement: How to measure
```

### Section Details

#### metadata
- **name**: Lowercase with hyphens (e.g., `memory-management`)
- **version**: Semantic versioning (MAJOR.MINOR.PATCH)
- **status**: Lifecycle stage (draft → review → approved → deprecated)

#### spec
- **purpose**: 2-3 sentences explaining what the capability enables
- **insight**: Core principle or "aha" moment
- **composable_with**: List compatible templates and capabilities
- **prerequisites**: What must exist before this capability works

#### behaviors
- Each behavior defines a discrete action the capability provides
- **trigger**: When the behavior activates (explicit phrases or implicit conditions)
- **protocol**: Step-by-step process
- **output**: What the behavior produces
- **reference**: Link to detailed documentation

#### theoretical_basis
- Ground capability in established theory (per L331, L332)
- See [Theoretical Grounding Requirements](#theoretical-grounding-requirements)

#### contracts
- Testable assertions that verify the capability is properly implemented
- Types: `directory_exists`, `file_exists`, `file_contains`, `custom`

#### adoption
- **priority**: P0 (critical) to P3 (nice-to-have)
- **demand**: How many agents need this capability
- **rollout_phases**: Staged adoption plan

---

## Step-by-Step Creation Process

### Step 1: Identify the Need

1. Review existing capabilities to avoid duplication
2. Document the demand (which agents? how many?)
3. Verify the behavior is reusable across contexts

### Step 2: Draft the Specification

1. Create file: `specs/capabilities/CAPABILITY_SPEC_<name>.yaml`
2. Fill in all required sections
3. Set `status: draft`

### Step 3: Define Behaviors

For each behavior:
1. Name it descriptively (verb_noun pattern)
2. Document explicit triggers (phrases users might say)
3. Document implicit triggers (conditions that activate it)
4. Define step-by-step protocol
5. Specify expected output

### Step 4: Establish Contracts

For each requirement:
1. Choose assertion type
2. Define path or pattern
3. Document what it verifies

### Step 5: Add Theoretical Grounding

1. Identify primary theory (Extended Mind, Actor Model, etc.)
2. List secondary theories
3. Write rationale connecting theory to capability

### Step 6: Validate

```bash
python3 aget/validation/validate_capability_spec.py specs/capabilities/CAPABILITY_SPEC_<name>.yaml
```

### Step 7: Create Supporting Artifacts

1. Pattern document: `docs/patterns/PATTERN_<name>.md`
2. SOP if needed: `sops/SOP_<name>.md`

### Step 8: Request Review

1. Change status to `review`
2. Create PR or request supervisor review
3. Address feedback

### Step 9: Approve and Adopt

1. Change status to `approved`
2. Update adoption phases
3. Notify fleet of new capability

---

## Validation Checklist

Before submitting for review:

### Structure
- [ ] File follows naming convention: `CAPABILITY_SPEC_<name>.yaml`
- [ ] All required sections present
- [ ] apiVersion is `aget.framework/v1`
- [ ] kind is `CapabilitySpecification`

### Metadata
- [ ] Name is lowercase with hyphens
- [ ] Version follows semantic versioning
- [ ] Status is valid (draft, review, approved, deprecated)
- [ ] Author is specified

### Spec
- [ ] Purpose clearly explains what capability enables
- [ ] Insight provides core principle
- [ ] composable_with lists compatible elements
- [ ] Prerequisites are documented

### Behaviors
- [ ] At least one behavior defined
- [ ] Each behavior has name, display_name, description
- [ ] Triggers are defined (explicit and/or implicit)
- [ ] Protocol has clear steps
- [ ] Output is specified
- [ ] No duplicate behavior names

### Contracts
- [ ] At least one contract defined
- [ ] Each contract has valid assertion type
- [ ] Paths are correct

### Theoretical Basis
- [ ] Primary theory identified
- [ ] Rationale connects theory to capability

### Adoption
- [ ] Priority set (P0-P3)
- [ ] Demand documented
- [ ] At least one rollout phase defined

### Validation
- [ ] Passes `validate_capability_spec.py`
- [ ] Supporting pattern document exists

---

## Examples

### Example 1: memory-management

```yaml
apiVersion: aget.framework/v1
kind: CapabilitySpecification
metadata:
  name: memory-management
  version: 1.0.0
  created: "2025-12-19"
  author: private-aget-framework-AGET
  status: approved
  target_version: v2.12.0

spec:
  name: memory-management
  display_name: Memory Management
  category: Core Infrastructure
  purpose: |
    Enable agents to systematically manage KB context for improved
    human-AI collaboration quality.
  insight: |
    KB is not storage — KB is the collaboration substrate that enables
    continuity across sessions, agents, and humans.
  composable_with:
    - All base templates
  prerequisites:
    - Agent has KB structure (governance/, planning/, evolution/)
    - Agent has .aget/ configuration

behaviors:
  - name: step_back_review_kb
    display_name: Step Back / Review KB
    description: Mid-session context refresh before proposing changes
    trigger:
      explicit: ["step back", "review kb"]
      implicit: ["About to propose substantial change"]
    protocol:
      - STEP BACK — Pause current momentum
      - REVIEW KB — Load relevant artifacts
      - PROPOSE — Articulate with precedent citations
    output: Informed proposal grounded in KB context
    reference: docs/patterns/PATTERN_step_back_review_kb.md

theoretical_basis:
  primary: Extended Mind
  secondary:
    - Transactive Memory
    - Distributed Cognition
  rationale: |
    Memory capabilities extend agent cognition by providing persistent
    cognitive scaffolding (Extended Mind).

contracts:
  - name: has_governance
    assertion: directory_exists
    path: governance/
    description: Agent must have governance directory
```

### Example 2: domain-knowledge

```yaml
apiVersion: aget.framework/v1
kind: CapabilitySpecification
metadata:
  name: domain-knowledge
  version: 1.0.0
  status: approved

spec:
  name: domain-knowledge
  display_name: Domain Knowledge
  category: Core Expertise
  purpose: |
    Enable agents to maintain and apply deep expertise in a specific domain.
  insight: |
    Domain expertise is organized knowledge that enables pattern recognition
    and contextual judgment, not just information retrieval.

behaviors:
  - name: domain_context_loading
    display_name: Domain Context Loading
    description: Load relevant domain knowledge before responding
    trigger:
      implicit: ["Query relates to agent's domain"]
    protocol:
      - Identify query's domain relevance
      - Load domain vocabulary and key concepts
      - Load relevant domain patterns
      - Apply domain context to response
    output: Response grounded in domain expertise

  - name: domain_expertise_boundaries
    display_name: Domain Expertise Boundaries
    description: Recognize and communicate boundaries of expertise
    trigger:
      implicit: ["Query outside domain expertise"]
    protocol:
      - Assess query against domain boundaries
      - If outside domain, acknowledge limitation
      - Suggest appropriate expert or resource
    output: Clear communication of expertise boundaries

contracts:
  - name: has_domain_documentation
    assertion: directory_exists
    path: docs/
    description: Agent must have documentation directory
```

---

## Common Mistakes to Avoid

### 1. Creating Too-Granular Capabilities

**Wrong**: Separate capabilities for `file-reading`, `file-writing`, `file-searching`

**Right**: Single `file-management` capability with multiple behaviors

### 2. Duplicating Existing Capabilities

Always check:
- `specs/capabilities/` for existing specs
- `docs/patterns/` for existing patterns

### 3. Missing Theoretical Grounding

Every capability should connect to established theory. See L331 for foundations:
- BDI (Belief-Desire-Intention)
- Actor Model
- Extended Mind
- Cybernetics
- Complex Adaptive Systems

### 4. Vague Triggers

**Wrong**: `trigger: ["do the thing"]`

**Right**:
```yaml
trigger:
  explicit: ["review my knowledge base", "step back"]
  implicit: ["About to propose substantial change", "Session has 10+ exchanges"]
```

### 5. Missing Contracts

Contracts enable automated validation. Every capability should have:
- At least one structural contract (directory or file exists)
- Behavioral contracts for key requirements

### 6. Forgetting Supporting Artifacts

A capability spec alone isn't complete. Create:
- Pattern document explaining the capability in detail
- SOP for procedural aspects
- Examples of usage

---

## Theoretical Grounding Requirements

Per L331 and L332, capabilities must be grounded in established theory.

### Available Foundations

| Theory | Key Concept | When to Use |
|--------|-------------|-------------|
| **BDI** | Belief-Desire-Intention | Agent decision-making, goal pursuit |
| **Actor Model** | Message passing, encapsulation | Multi-agent coordination, handoffs |
| **Extended Mind** | Cognition extends to artifacts | KB as cognitive scaffold, memory |
| **Cybernetics** | Requisite variety, feedback | Adaptation, context sensitivity |
| **Complex Adaptive Systems** | Emergence, self-organization | Fleet patterns, collaboration |
| **Transactive Memory** | "Who knows what" | Cross-agent knowledge, routing |
| **Distributed Cognition** | Cognition across artifacts | Human-AI collaboration |

### Grounding Process

1. **Identify primary theory** that best explains the capability's core function
2. **List secondary theories** that inform specific behaviors
3. **Write rationale** connecting theory to practical implementation
4. **Reference L-docs** that establish theoretical foundations

### Example Grounding

```yaml
theoretical_basis:
  primary: Extended Mind
  secondary:
    - Transactive Memory
    - Distributed Cognition
    - Stigmergy
  rationale: |
    Memory capabilities extend agent cognition by providing persistent
    cognitive scaffolding (Extended Mind). KB serves as shared "who knows
    what" index between human and AI (Transactive Memory). Cognition is
    distributed across human, AI, and KB artifacts (Distributed Cognition).
    KB modifications enable coordination without direct communication
    (Stigmergy).
  references:
    - .aget/evolution/L331_theoretical_foundations_agency.md
    - .aget/evolution/L332_theoretical_grounding_protocol.md
```

---

## References

- Schema: `specs/schemas/CAPABILITY_SPEC_v1.0_SCHEMA.yaml`
- Validator: `validation/validate_capability_spec.py`
- Theoretical Foundations: `.aget/evolution/L331_theoretical_foundations_agency.md`
- Theoretical Grounding Protocol: `.aget/evolution/L332_theoretical_grounding_protocol.md`

---

*Capability Author Guide v1.0.0*
*Part of AGET Capability Composition Architecture*
