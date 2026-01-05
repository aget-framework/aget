# AGET Layer Architecture

**Version**: 1.0.1
**Date**: 2026-01-04
**Status**: CANONICAL
**Location**: aget/docs/LAYER_ARCHITECTURE.md

---

## Overview

AGET templates form an inheritance hierarchy where specialized templates build upon foundation capabilities. This document defines the layer architecture and inheritance rules.

---

## Template Hierarchy

```
                    ┌─────────────────────────┐
                    │   WORKER_TEMPLATE_SPEC  │
                    │      (Foundation)       │
                    │    35 capabilities      │
                    └───────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │    ADVISOR    │   │  SUPERVISOR   │   │   SUBJECT     │
    │   TEMPLATE    │   │   TEMPLATE    │   │   TEMPLATE    │
    │  (Advisory)   │   │ (Coordination)│   │  (Entities)   │
    └───────┬───────┘   └───────────────┘   └───────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────────┐
│DEVELOPER│   │SPEC-ENGINEER│
│TEMPLATE │   │  TEMPLATE   │
└─────────┘   └─────────────┘
```

---

## Layer Definitions

### Layer 0: Foundation (Worker)

**Template**: `template-worker-aget`
**Specification**: [WORKER_TEMPLATE_SPEC]

The foundation layer provides capabilities that ALL templates inherit:

| Domain | Capabilities | Examples |
|--------|-------------|----------|
| Session Protocol | CAP-001 to CAP-012 | wake, study up, wind down, sign off |
| Analysis | CAP-013 to CAP-016 | file read, search, web fetch |
| Action | CAP-017 to CAP-019 | file write, command execute (instance-dependent) |
| Configuration | CAP-020 to CAP-024 | version.json, size limits |
| Evolution | CAP-025 to CAP-027 | learning documents |
| Governance | CAP-028 to CAP-030 | project plans, gates |
| Coordination | CAP-031 to CAP-032 | portfolio, supervisor |
| Verification | CAP-033 to CAP-035 | environmental grounding |

**Key Characteristics**:
- Instance type determines action capabilities (aget vs AGET)
- Session protocols are standardized
- Learning tracking is optional (intelligence_enabled)
- All agents have analysis capabilities

### Layer 1: Behavioral Specialization

Templates at this layer add behavioral patterns on top of foundation capabilities.

#### Advisor Template

**Template**: `template-advisor-aget`
**Specification**: [ADVISOR_TEMPLATE_SPEC] (planned)
**Inherits From**: [WORKER_TEMPLATE_SPEC]

**Added Capabilities**:
- Persona system (teacher, mentor, consultant, guru, coach)
- Advisory protocols (analyze before recommending)
- Scoped write permissions (v2.6.0+)
- Read-only by default with controlled exceptions

**Instance Type**: Typically `aget` (read-only advisory)

#### Supervisor Template

**Template**: `template-supervisor-aget`
**Specification**: `SUPERVISOR_TEMPLATE_SPEC_v1.0.yaml` (pending)
**Inherits From**: Worker Template

**Added Capabilities**:
- Fleet coordination
- Portfolio governance
- Agent lifecycle management
- Cross-agent orchestration

**Instance Type**: Typically `coordinator`

#### Subject Template (Future)

**Template**: `template-subject-aget`
**Specification**: `SUBJECT_TEMPLATE_SPEC_v1.0.yaml` (planned)
**Inherits From**: Worker Template

**Added Capabilities**:
- Entity tracking (people, concepts, organizations)
- Relationship management
- Longitudinal context

**Instance Type**: Typically `aget` (information tracking)

### Layer 2: Task Specialization

Templates at this layer specialize Layer 1 templates for specific tasks.

#### Developer Template

**Template**: `template-developer-aget`
**Specification**: Inherits from Advisor
**Inherits From**: Advisor Template

**Added Capabilities**:
- Code review protocols
- Development workflow support
- Technical documentation

#### Spec Engineer Template

**Template**: `template-spec-engineer-aget`
**Specification**: Inherits from Advisor
**Inherits From**: Advisor Template

**Added Capabilities**:
- EARS specification authoring
- Requirement analysis
- Contract test generation

#### Consultant Template

**Template**: `template-consultant-aget`
**Specification**: Inherits from Advisor
**Inherits From**: Advisor Template

**Added Capabilities**:
- Engagement patterns
- Deliverable templates
- Client communication styles

---

## Inheritance Rules

### Rule 1: Foundation Capabilities are Immutable

Derived templates MUST NOT remove or weaken foundation capabilities.

```yaml
# WRONG - Cannot remove foundation capability
CAP-001:
  status: REMOVED  # Not allowed!

# RIGHT - Can specialize with WHERE pattern
CAP-001-ADVISOR:
  inherits: CAP-001
  statement: "WHERE Persona_Type is consultant, WHEN Wake_Command is received..."
```

### Rule 2: Capability Numbering

| Range | Layer | Example |
|-------|-------|---------|
| CAP-001 to CAP-099 | Foundation (Worker) | CAP-035 |
| CAP-100 to CAP-199 | Layer 1 (Advisor, Supervisor) | CAP-128 |
| CAP-200 to CAP-299 | Layer 2 (Developer, Spec-Engineer) | CAP-215 |

### Rule 3: Session Protocol Compatibility

All templates MUST maintain compatible session protocols:

- `wake up` - Must produce formatted session summary
- `study up` - Must load deep context
- `wind down` - Must document session state
- `sign off` - Must close session cleanly

Derived templates may ADD to these protocols but not replace them.

### Rule 4: Specification References

Derived specifications MUST reference their parent:

```yaml
spec:
  id: SPEC-ADVISOR-TEMPLATE
  inherits_from: SPEC-WORKER-TEMPLATE
  parent_version: "1.0.0"
```

---

## Instance Type Matrix

| Template | Default Instance Type | Can Be AGET? | Notes |
|----------|---------------------|--------------|-------|
| Worker | aget | Yes | Foundation supports both |
| Advisor | aget | Limited | Scoped writes only |
| Supervisor | coordinator | Yes | Fleet management |
| Developer | AGET | Yes | Needs write for code |
| Spec-Engineer | aget | Yes | Primarily advisory |
| Consultant | aget | Limited | Scoped writes |

---

## Capability Flow

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                  Foundation Layer                    │
│  Session Protocol → Analysis → Configuration        │
└─────────────────────────────────────────────────────┘
     │
     ▼ (if specialized template)
┌─────────────────────────────────────────────────────┐
│              Behavioral Specialization               │
│  Advisor: Persona → Advisory Protocol               │
│  Supervisor: Fleet → Portfolio → Coordination       │
└─────────────────────────────────────────────────────┘
     │
     ▼ (if task-specialized template)
┌─────────────────────────────────────────────────────┐
│               Task Specialization                    │
│  Developer: Code Review → Development Workflow      │
│  Spec-Engineer: EARS Authoring → Contract Tests     │
└─────────────────────────────────────────────────────┘
     │
     ▼
Response to User
```

---

## Migration Between Templates

### Upgrading Template

When an agent needs more capabilities:

1. Identify target template (e.g., worker → advisor)
2. Update `version.json` template field
3. Add required new fields (e.g., persona for advisor)
4. Update AGENTS.md with new sections
5. Run contract tests for new template

### Downgrading Template

When an agent needs fewer capabilities:

1. Verify no dependencies on advanced capabilities
2. Remove specialized fields from version.json
3. Simplify AGENTS.md
4. Run foundation contract tests

---

## Future Architecture

### Planned Templates

| Template | Layer | Purpose | Status |
|----------|-------|---------|--------|
| Subject | 1 | Entity/relationship tracking | Planned |
| Cognitive | 2 | AI self-modeling | Conceptual |
| Orchestrator | 1 | Multi-agent workflows | Conceptual |

### Extension Points

The architecture supports extension via:

1. **New Layer 1 templates** - Add behavioral specializations
2. **New Layer 2 templates** - Add task specializations
3. **Capability domains** - Add new capability categories
4. **Instance types** - Add new permission models

---

## References

| ID | Title | Location |
|----|-------|----------|
| [WORKER_TEMPLATE_SPEC] | Foundation specification | [`specs/`][worker-spec] |
| [ADVISOR_TEMPLATE_SPEC] | Advisory specialization | (planned) |
| [L174] | Template specification debt | Internal L-doc |
| [L175] | Template taxonomy bifurcation | Internal L-doc |

[worker-spec]: ../specs/WORKER_TEMPLATE_SPEC_v1.0.yaml

---

*LAYER_ARCHITECTURE.md — Template inheritance hierarchy for AGET framework*
