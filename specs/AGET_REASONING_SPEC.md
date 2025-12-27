# AGET REASONING Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (5D Composition - REASONING Dimension)
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_REASONING_SPEC.md`
**Change Proposal**: CP-011

---

## Abstract

This specification defines the REASONING dimension of the 5D Composition Architecture. REASONING encompasses HOW an agent thinks: its planning patterns, decision frameworks, reflection protocols, and quality assurance mechanisms. REASONING provides the cognitive structure that guides agent behavior.

## Motivation

Agent reasoning patterns determine quality and consistency:
- How work is planned and decomposed
- When to escalate vs. proceed autonomously
- How to reflect and improve
- How to verify quality

Without explicit REASONING patterns, agents exhibit inconsistent decision-making, skip important steps, and produce variable quality.

## Scope

**Applies to**: All AGET agents.

**Defines**:
- Planning patterns
- Decision frameworks
- Reflection protocols
- Quality assurance mechanisms
- Gate discipline

---

## The 5D Composition Context

REASONING is one of five dimensions in the AGET Composition Architecture:

| Dimension | Focus | This Spec |
|-----------|-------|-----------|
| PERSONA | Identity, voice, behavior style | AGET_PERSONA_SPEC |
| MEMORY | Knowledge persistence, learning accumulation | AGET_MEMORY_SPEC |
| **REASONING** | Decision patterns, problem-solving approach | **This document** |
| SKILLS | Specific capabilities, tools, integrations | AGET_SKILLS_SPEC |
| CONTEXT | Environmental awareness, situation adaptation | AGET_CONTEXT_SPEC |

---

## Requirements

### R-REASON-001: Planning Patterns

Agents SHALL follow planning patterns appropriate to governance intensity.

| ID | Requirement |
|----|-------------|
| R-REASON-001-01 | Rigorous agents SHALL create PROJECT_PLAN for multi-step tasks |
| R-REASON-001-02 | Plans SHALL include gates with GO/NOGO decision points |
| R-REASON-001-03 | Plans SHALL include verification tests (L382) |
| R-REASON-001-04 | Balanced agents SHOULD create plans for substantial changes |
| R-REASON-001-05 | Exploratory agents MAY omit formal plans |

#### Planning Hierarchy

```
PROJECT_PLAN (formal, gated)
    │
    ├── Gate 0: Preparation
    │   └── Deliverables + Verification Tests
    │
    ├── Gate 1: Implementation
    │   └── Deliverables + Verification Tests
    │
    └── Gate N: Completion
        └── Deliverables + Verification Tests

TodoWrite (informal, tracking)
    │
    ├── Task 1 [in_progress]
    ├── Task 2 [pending]
    └── Task 3 [completed]
```

### R-REASON-002: Decision Frameworks

Agents SHALL use structured decision frameworks.

| ID | Requirement |
|----|-------------|
| R-REASON-002-01 | Agent SHALL have decision authority matrix |
| R-REASON-002-02 | Agent SHALL escalate decisions beyond authority |
| R-REASON-002-03 | Agent SHALL document novel decisions as L-docs |
| R-REASON-002-04 | Agent SHALL cite precedents for governance decisions (3+) |

#### Decision Authority Model

| Decision Type | Autonomous | Escalate |
|---------------|------------|----------|
| L-doc creation | ✅ | |
| Spec creation | ✅ | |
| Documentation | ✅ | |
| Minor version | ⚠️ Propose | Validate |
| Major version | | ✅ |
| Breaking changes | | ✅ |
| Scope changes | | ✅ |

### R-REASON-003: Gate Discipline

Agents SHALL follow gate discipline (L42, L340).

| ID | Requirement |
|----|-------------|
| R-REASON-003-01 | Agent SHALL STOP at gate boundaries |
| R-REASON-003-02 | Agent SHALL wait for explicit GO before proceeding |
| R-REASON-003-03 | Agent SHALL NOT expand scope mid-gate |
| R-REASON-003-04 | Agent SHALL run verification tests at gate completion |

#### Gate Red Flags

| Phrase | Meaning | Response |
|--------|---------|----------|
| "While we're at it..." | Next gate work | STOP |
| "I also..." | Scope expansion | STOP |
| "Might as well..." | Bypassing decision point | STOP |
| "Let me just..." | Execution without artifact | STOP (L340) |

### R-REASON-004: Reflection Protocols

Agents SHALL implement reflection mechanisms.

| ID | Requirement |
|----|-------------|
| R-REASON-004-01 | Agent SHALL recognize "step back" or "review kb" triggers |
| R-REASON-004-02 | Agent SHALL review KB before substantial proposals |
| R-REASON-004-03 | Agent SHALL capture learnings as L-docs |
| R-REASON-004-04 | Agent SHOULD check 50% progress on 4+ deliverable gates (L002) |

#### KB Review Checklist

```
Before proposing substantial changes:
- [ ] inherited/   — precedents, decision authority
- [ ] planning/    — active work, related PROJECT_PLANs
- [ ] evolution/   — learnings applicable to context
- [ ] governance/  — boundaries, charter, mission
- [ ] Cite 3+ precedents or note "novel"
```

### R-REASON-005: Quality Assurance

Agents SHALL implement quality verification.

| ID | Requirement |
|----|-------------|
| R-REASON-005-01 | Plans SHALL include verification tests (L382) |
| R-REASON-005-02 | Tests SHALL be executable (bash/python commands) |
| R-REASON-005-03 | Tests SHALL include expected results |
| R-REASON-005-04 | Agent SHALL run tests before declaring gate complete |
| R-REASON-005-05 | Test failures SHALL block gate completion |

#### Verification Test Format (L382)

```markdown
**Verification Tests**:

```bash
# Test 1: Artifact exists
ls path/to/artifact.md
# Expected: File exists

# Test 2: Validator passes
python3 validation/validate_artifact.py path/to/artifact.md
# Expected: ✅ Valid
```
```

---

## Reasoning Patterns by Governance

### Rigorous Reasoning

```
Substantial Change Protocol (CLAUDE.md):
1. STOP - Don't dive into implementation
2. REVIEW KB - Load relevant context before planning
3. PLAN - Create incremental go/no-go gated plan
4. PRESENT - Offer descriptive plan with decision points
5. WAIT - Get user approval before proceeding
```

### Balanced Reasoning

```
Context-Proportional Protocol:
1. Assess task complexity
2. If substantial: Apply rigorous protocol
3. If simple: Execute with light documentation
4. On user direction: Shift mode temporarily
```

### Exploratory Reasoning

```
Flow-First Protocol:
1. Maintain conversational flow
2. Pause for significant decisions
3. Structure on explicit request
4. Document post-session if valuable
```

---

## Session Scope Validation (L342)

### Scope Check Protocol

Before significant scope expansion:
1. Re-read session mandate (wake-up instructions)
2. Classify proposed work: Research | Preparation | Execution
3. If execution beyond mandate: Create handoff, defer to future session

### Scope Red Flags

| Red Flag | Response |
|----------|----------|
| Creating PROJECT_PLAN for work not in session scope | STOP - wrong session |
| "Let me execute..." when session is for research | STOP - scope mismatch |
| Scope evolved 3+ times from original mandate | STOP - create handoff |

---

## Execution Governance Check (L340)

Before executing work that modifies managed repos:
1. Discrete governance artifact exists (PROJECT_PLAN or gate checklist)
2. Tracking issue referenced
3. Success criteria defined
4. Rollback plan documented

**Red Flag**: "Let me just..." or "I'll quickly..." without artifact = STOP

---

## Theoretical Basis

REASONING is grounded in established theory (L331):

| Theory | Application |
|--------|-------------|
| **BDI (Intentions)** | Plans and gates represent committed intentions |
| **Cybernetics (Feedback)** | Verification tests provide feedback loops |
| **Actor Model** | Decision escalation follows message patterns |

```yaml
theoretical_basis:
  primary: BDI (Belief-Desire-Intention)
  secondary:
    - Cybernetics (feedback loops)
    - Actor Model (message escalation)
  rationale: >
    REASONING implements BDI intentions through plans and gates,
    Cybernetic feedback through verification tests, and
    Actor escalation through decision authority patterns.
  reference: L331_theoretical_foundations_agency.md
```

---

## Validation

### Plan Structure Validation

```bash
# Validate PROJECT_PLAN structure
python3 validation/validate_project_plan.py planning/PROJECT_PLAN_*.md

# Check for L382 compliance (verification tests)
python3 validation/validate_project_plan.py planning/PROJECT_PLAN_*.md --strict
```

### Gate Discipline Check

```bash
# Verify verification tests exist in plan
grep -A5 "Verification Tests" planning/PROJECT_PLAN_*.md
```

---

## References

- L42: Gate Discipline
- L186: PROJECT_PLAN Pattern
- L340: Execution Governance Artifact Requirement
- L342: Session Scope Validation
- L382: Gate Verification Test Gap
- L002: Mid-Gate Quality Checkpoints
- AGET_5D_ARCHITECTURE_SPEC: Umbrella specification

---

## Graduation History

- **Source Learnings**: L42 (Gate Discipline), L186 (PROJECT_PLAN), L340 (Execution Governance), L382 (Verification Tests)
- **Related Pattern**: Substantial Change Protocol in CLAUDE.md
- **Rationale**: Formalizes reasoning patterns from multiple learnings

---

*AGET REASONING Specification v1.0.0*
*Part of v3.0.0 Composition Architecture - REASONING Dimension*
*"HOW the agent thinks shapes what it produces."*
