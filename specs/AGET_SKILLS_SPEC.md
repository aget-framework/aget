# AGET SKILLS Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (5D Composition - SKILLS Dimension)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_SKILLS_SPEC.md`
**Change Proposal**: CP-012

---

## Abstract

This specification defines the SKILLS dimension of the 5D Composition Architecture. SKILLS encompasses WHAT an agent does: its capabilities, tools, outputs, and phase alignment. SKILLS provides the behavioral repertoire that enables agent action.

## Motivation

Agent capabilities determine what work can be performed:
- What behaviors an agent can exhibit
- What tools are available
- What output formats are produced
- Which A-SDLC phases the agent supports

Without explicit SKILLS definition, agents have unclear capabilities, leading to mismatched assignments and inconsistent outputs.

## Scope

**Applies to**: All AGET agents.

**Defines**:
- Capability composition
- Tool availability
- Output formats
- A-SDLC phase alignment
- Skill artifacts

**Related Specifications**:
- COMPOSITION_SPEC_v1.0.md (capability composition mechanism)
- AGET_5D_ARCHITECTURE_SPEC.md (umbrella)

---

## The 5D Composition Context

SKILLS is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | AGET_PERSONA_SPEC |
| MEMORY | Knowledge persistence, learning accumulation | AGET_MEMORY_SPEC |
| REASONING | Decision patterns, problem-solving approach | AGET_REASONING_SPEC |
| **SKILLS** | Specific capabilities, tools, integrations | **This document** |
| CONTEXT | Environmental awareness, situation adaptation | AGET_CONTEXT_SPEC |

---

## Requirements

### R-SKILL-001: Capability Declaration

Agents SHALL declare capabilities in manifest.

| ID | Requirement |
|----|-------------|
| R-SKILL-001-01 | Agent SHALL list capabilities in manifest.yaml |
| R-SKILL-001-02 | Capabilities SHALL reference defined capability specs |
| R-SKILL-001-03 | Capability prerequisites SHALL be satisfied |
| R-SKILL-001-04 | Capability conflicts SHALL be detected and resolved |

#### Capability Declaration Format

```yaml
# manifest.yaml
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
  composition_rules:
    conflict_resolution: error
```

### R-SKILL-002: Tool Availability

Agents SHALL have access to appropriate tools.

| ID | Requirement |
|----|-------------|
| R-SKILL-002-01 | Agent SHALL have access to validators for its domain |
| R-SKILL-002-02 | Agent SHALL have pattern scripts in .aget/patterns/ |
| R-SKILL-002-03 | Tool availability SHALL be documented |
| R-SKILL-002-04 | Tools SHALL be registered in SCRIPT_REGISTRY.yaml |

#### Standard Tool Categories

| Category | Examples | Location |
|----------|----------|----------|
| Validators | validate_*.py | validation/ |
| Session patterns | wake_up.py, wind_down.py | .aget/patterns/session/ |
| Release patterns | version_bump.py | .aget/patterns/release/ |
| Sync patterns | template_sync_check.py | .aget/patterns/sync/ |

### R-SKILL-003: Output Formats

Agents SHALL define output format capabilities.

| ID | Requirement |
|----|-------------|
| R-SKILL-003-01 | Agent MAY declare structured-outputs capability |
| R-SKILL-003-02 | Output formats SHALL be documented |
| R-SKILL-003-03 | Domain-specific formats SHALL have templates |

#### Standard Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| Markdown | Standard documentation | Specs, L-docs, docs |
| YAML | Structured data | Manifests, processes |
| JSON | Machine-readable | Identity, version files |
| 5W+H | Executive briefing | Strategic communication |

### R-SKILL-004: A-SDLC Phase Alignment

Agents SHALL align with A-SDLC phases.

| ID | Requirement |
|----|-------------|
| R-SKILL-004-01 | Agent SHOULD declare primary A-SDLC phase(s) |
| R-SKILL-004-02 | Phase alignment SHALL inform capability selection |
| R-SKILL-004-03 | Cross-cutting agents MAY span multiple phases |

#### A-SDLC Phase Mapping

| Phase | Description | Template Alignment |
|-------|-------------|--------------------|
| Phase 0 | Strategic Planning | executive, researcher |
| Phase 1 | Requirements | spec-engineer, analyst |
| Phase 2 | Architecture | architect |
| Phase 3 | Implementation | developer |
| Phase 4 | Testing/Review | reviewer |
| Phase 5 | Deployment | operator |
| Phase 6 | Operations | operator, developer |
| Cross-cutting | All phases | supervisor, advisor, worker, consultant |

### R-SKILL-005: Skill Documentation

Agents SHALL document their skills.

| ID | Requirement | Location |
|----|-------------|----------|
| R-SKILL-005-01 | Capability list | manifest.yaml |
| R-SKILL-005-02 | Tool reference | .aget/patterns/README.md |
| R-SKILL-005-03 | Output examples | docs/ |
| R-SKILL-005-04 | Phase alignment | AGENTS.md |

---

## Capability Composition

SKILLS dimension leverages COMPOSITION_SPEC_v1.0 for capability composition:

### Composition Model (L330)

```
Agent = Base Template + Capability[]

Example:
  template-advisor-aget
    + capability-memory-management
    + capability-domain-knowledge
    + capability-structured-outputs
    = Data Science Advisor
```

### Composition Algebra

| Property | Formula | Meaning |
|----------|---------|---------|
| Identity | T + ∅ = T | No capabilities = base template |
| Commutativity | T + [A, B] = T + [B, A] | Order doesn't matter |
| Idempotency | T + [A, A] = T + [A] | Duplicates ignored |
| Prerequisite | A requires B → B must be in list | Dependencies satisfied |

### Standard Capabilities

| Capability | Purpose | Prerequisites |
|------------|---------|---------------|
| memory-management | 6-layer memory, KB review | — |
| domain-knowledge | Domain expertise | — |
| structured-outputs | Formatted output production | — |
| governance-rigorous | Full protocol governance | — |
| governance-balanced | Proportional governance | — |
| governance-exploratory | Flow-first governance | — |
| collaboration | Cross-agent coordination | domain-knowledge |
| org-kb | Organizational knowledge | memory-management |

---

## Validation

### Capability Validation

```bash
# Validate manifest structure
python3 validation/validate_template_manifest.py manifest.yaml

# Validate capability composition
python3 validation/validate_composition.py manifest.yaml --specs specs/capabilities/

# Verify prerequisites satisfied
python3 validation/validate_composition.py manifest.yaml -v
```

### Tool Availability Check

```bash
# Verify pattern scripts exist
ls .aget/patterns/session/
ls .aget/patterns/release/

# Verify scripts are registered
python3 validation/validate_script_registry.py SCRIPT_REGISTRY.yaml --check-files
```

---

## Theoretical Basis

SKILLS is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **BDI (Capabilities)** | Skills represent what agent CAN do |
| **Cybernetics** | Capabilities provide requisite variety |
| **Extended Mind** | Tools extend cognitive capability |
| **Actor Model** | Skills define message-handling potential |

```yaml
theoretical_basis:
  primary: Extended Mind
  secondary:
    - BDI (capability as potential)
    - Cybernetics (requisite variety)
    - Actor Model (message handling)
  rationale: >
    SKILLS extends agent cognition (Extended Mind) through tools and
    capabilities. Capabilities represent behavioral potential (BDI).
    More skills provide variety to match complexity (Cybernetics).
  reference: L331_theoretical_foundations_agency.md
```

---

## References

- L330: Capability Composition Architecture
- COMPOSITION_SPEC_v1.0: Composition mechanism
- SCRIPT_REGISTRY.yaml: Script catalog
- AGET_PYTHON_SCRIPT_SPEC: Script standards
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification

---

## Graduation History

- **Source Learning**: L330 (Capability Composition Architecture)
- **Related Pattern**: Template Manifest pattern
- **Rationale**: Formalizes capability composition into dimension spec

---

*AGET SKILLS Specification v1.0.0*
*Part of v3.0.0 Composition Architecture - SKILLS Dimension*
*"WHAT the agent does defines its value."*
