# REQ-GOV: Agent Governance Requirements

**Version**: 0.2.0
**Date**: 2026-04-18 (promoted from scratchpad draft v0.1 dated 2026-03-27)
**Status**: proposed
**Domain**: GOV (Governance)
**Format**: REQUIREMENTS_FORMAT v1.0
**Inherits from**: REQ-CORE_critical_foundations.md (cross-cutting foundations)
**Specifications**: AGET_GOVERNANCE_HIERARCHY_SPEC, AGET_FRAMEWORK_SPEC, AGET_ISSUE_GOVERNANCE_SPEC v2.1.0, governance/SCOPE_BOUNDARIES.md, governance/MISSION.md
**Tracking**: #725 (requirements formalization), v3.14.0 VERSION_SCOPE item #24

---

## Overview

Agent governance defines the boundaries, authorities, and safety constraints that ensure agents operate within their intended scope. These requirements are grounded in AGET's governance hierarchy (supervisor → agent → artifact), scope boundary enforcement, and the principle that agents optimize for human-AI collaboration quality, not autonomous speed.

**Principal intent**: Agents should be predictable, bounded, and transparent — never surprising the principal with unauthorized scope expansion or ungoverned actions.

This document is the second domain-specific REQ-* document published in `aget/requirements/`. It inherits from REQ-CORE (cross-cutting foundations) and specializes those foundations to the governance domain. The inheritance map is in the *REQ-CORE Inheritance* section below.

---

## REQ-CORE Inheritance

| GOV requirement | Specializes REQ-CORE | Specialization |
|-----------------|----------------------|----------------|
| REQ-GOV-F-001 (Scope Boundary Enforcement) | REQ-CORE-F-007 (Gate Boundary Discipline) | Governance-domain scope as a gate type |
| REQ-GOV-F-002 (Authority Model Clarity) | REQ-CORE-F-005 (Principal Authority Gradient) | Per-agent authority model that informs per-action gradient |
| REQ-GOV-F-003 (Private-First Information Routing) | REQ-CORE-Q-009 (Private-First Routing) | Information-routing instance of the default-private rule |
| REQ-GOV-F-004 (Governance Artifact Requirement) | REQ-CORE-F-002 (Evidence-Driven Graduation) + REQ-CORE-F-007 | Artifact precondition for gated execution |
| REQ-GOV-Q-001 (Governance Transparency) | REQ-CORE-Q-010 (Collaboration-Quality Optimization) | Transparency as collaboration-quality enabler |
| REQ-GOV-Q-002 (Agent Safety Boundaries) | REQ-CORE-F-005 + REQ-CORE-Q-009 | Safety envelope spanning authority and routing |

REQ-GOV does not introduce requirements that contradict REQ-CORE; every GOV requirement is a specialization. If conflict appears in future revisions, REQ-CORE wins (per REQ-CORE-F-001 mandatory inheritance).

---

## Functional Requirements

```yaml
id: REQ-GOV-F-001
title: "Scope Boundary Enforcement"
type: functional
description: >
  Every agent should operate within defined scope boundaries.
  Actions outside scope should require explicit escalation
  to the supervisor or principal.
rationale: >
  Unbounded agents create unpredictable outcomes. L42 (gate
  boundaries) and ADR-001 (conversation layer only) establish
  that scope is the primary governance mechanism.
evidence:
  - "L42 (Stop at gate boundaries, wait for GO)"
  - "ADR-001 (AGET = conversation layer only)"
  - "governance/SCOPE_BOUNDARIES.md (per-agent scope)"
  - "L342 (Session Scope Validation)"
fit_criterion: >
  Agent has a SCOPE_BOUNDARIES.md with explicit in-scope and
  out-of-scope areas. Actions classified as out-of-scope
  trigger escalation (not silent execution). Session scope
  checks (L342) execute before significant expansion.
priority: P0
specifications:
  - "CAP-GOV-001 (scope boundary enforcement contract)"
constraints:
  - "governance/SCOPE_BOUNDARIES.md (per-agent scope document)"
  - "ADR-001 (AGET = conversation layer only)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-GOV-F-002
title: "Authority Model Clarity"
type: functional
description: >
  Every agent should have a clear authority model specifying
  which decisions it can make autonomously, which require
  approval, and which must be escalated.
rationale: >
  Without explicit authority, agents either over-escalate
  (wasting principal time) or under-escalate (unauthorized
  actions). The decision authority matrix prevents both.
evidence:
  - "L342 (Authority Model — Relationship Clarity)"
  - "inherited/DECISION_AUTHORITY_MATRIX.md"
  - "ADR-005 (Gates = release points)"
fit_criterion: >
  Agent has a DECISION_AUTHORITY_MATRIX (or equivalent in
  AGENTS.md) covering at minimum: autonomous decisions,
  propose-and-execute decisions, and escalation-required
  decisions. Matrix is referenced during gate execution and
  consumed by the per-action authority gradient (REQ-CORE-F-005).
priority: P0
specifications:
  - "SKILL-024 (aget-propose-actions — operationalizes the authority model per-action via REQ-PA-008/009)"
constraints:
  - "AGENTS.md Authority Model section (the per-agent declaration)"
  - "inherited/DECISION_AUTHORITY_MATRIX.md (the inherited authority taxonomy)"
  - "ADR-005 (Gates = release points)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-GOV-F-003
title: "Private-First Information Routing"
type: functional
description: >
  All agent-generated artifacts containing internal information
  should route to private repositories first. Public publication
  requires explicit approval and content sanitization.
rationale: >
  L638 established private-first routing after discovering
  agents could inadvertently expose private agent names, fleet
  sizes, and internal references in public issues. The
  default-private invariant (REQ-CORE-Q-009) makes the failure
  mode fail closed (private), not open (public leak).
evidence:
  - "L638 (Private-First Issue Routing)"
  - "L520 (Issue Governance Gap)"
  - "AGET_ISSUE_GOVERNANCE_SPEC v2.1.0"
  - "REQ-CORE-Q-009 (cross-cutting routing rule)"
fit_criterion: >
  100% of agent-filed issues route to the configured private
  tracker. 0% of promoted public issues contain private agent
  names, fleet-size disclosures, internal project IDs, or
  session identifiers. Sanitization check executes before any
  promotion (R-ISSUE-011).
priority: P0
specifications:
  - "R-ISSUE-001 through R-ISSUE-014 (issue governance contracts within AGET_ISSUE_GOVERNANCE_SPEC v2.1.0)"
  - "SKILL-040 (aget-file-issue, Strict per ADR-008)"
constraints:
  - "AGET_ISSUE_GOVERNANCE_SPEC v2.1.0 (the meta-spec containing R-ISSUE-* contracts)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-GOV-F-004
title: "Governance Artifact Requirement"
type: functional
description: >
  Significant work should be governed by discrete artifacts
  (PROJECT_PLAN, gate checklist, or tracking issue) before
  execution begins. The artifact is the precondition for
  any execution that modifies public repos.
rationale: >
  L340 found that ungoverned execution ("let me just...")
  produces artifacts without traceability, success criteria,
  or rollback plans. The governance artifact is the minimum
  viable structure that makes gate completion auditable
  (REQ-CORE-F-007).
evidence:
  - "L340 (Execution Governance Artifact Requirement)"
  - "L675 (Consequence Gap — plans without enforcement)"
  - "ADR-008 (Advisory → Strict → Generator)"
fit_criterion: >
  Every execution that modifies public repos has a referenced
  tracking issue AND either a PROJECT_PLAN or gate checklist.
  "Let me just..." without artifact triggers STOP. Strict
  enforcement: PROJECT_PLAN creation requires
  /aget-create-project (ADR-008 Strict level).
priority: P1
specifications:
  - "CAP-PP-001 through CAP-PP-007 (project-plan governance contracts within AGET_PROJECT_PLAN_SPEC)"
constraints:
  - "AGET_PROJECT_PLAN_SPEC (the meta-spec containing CAP-PP-* contracts)"
  - "L340 (Execution Governance Artifact Requirement)"
  - "ADR-008 (Advisory → Strict → Generator — sets enforcement level for /aget-create-project)"
status: proposed
originator: operational-evidence
```

---

## Quality Requirements

```yaml
id: REQ-GOV-Q-001
title: "Governance Transparency"
type: quality
category: Interaction Capability
description: >
  Governance decisions should be transparent — the principal
  should always be able to trace why an agent took an action,
  what authority it exercised, and what alternatives existed.
rationale: >
  AGET optimizes for human-AI collaboration quality (REQ-CORE-Q-010).
  Opaque governance erodes trust. L-docs, decision logs, and
  gate records provide the transparency substrate.
evidence:
  - "DESIGN_PHILOSOPHY: 'collaboration quality, not autonomous speed'"
  - "L335 (Memory Architecture — shared human-AI artifact)"
  - "L706 (Incremental Progress Reporting)"
fit_criterion: >
  Every gate completion includes a plan update commit with
  V-test results and decision rationale. Principal can
  reconstruct decision path from artifacts alone (no session
  replay needed). Verifiable by audit of any merged PR.
priority: P1
specifications:
  - "CAP-PP-002 (Decision Points contract within AGET_PROJECT_PLAN_SPEC)"
constraints:
  - "AGENTS.md Gate Execution Discipline section (L001)"
  - "L706 (Incremental Progress Reporting)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-GOV-Q-002
title: "Agent Safety Boundaries"
type: quality
category: Safety
description: >
  Agents should have fail-safe boundaries that prevent
  destructive actions without explicit principal authorization.
  Scope boundaries, escalation rules, and permission governance
  form the safety envelope.
rationale: >
  ISO 25010:2023 Safety category applies directly to agent
  governance. An agent that force-pushes, deletes branches,
  or modifies shared state without authorization creates
  irreversible harm.
evidence:
  - "L474 (CLI Agent Skills Enforcement Model)"
  - "L500 (Permission Governance Detection Gap)"
  - "L99 (Every agent is a worker — no autonomous authority escalation)"
  - "L027 (Permission accumulation evidence)"
fit_criterion: >
  Destructive operations (force-push, branch deletion, shared
  state modification) require explicit principal authorization.
  Permission accumulation monitored (WARN at >100, CRITICAL at
  >200). Skills cannot override AGENTS.md scope boundaries for
  harmful operations.
priority: P0
specifications:
  - "CAP-SAFETY-001 (PROPOSED — see PROPOSAL_cap_safety_001_destructive_op_authorization.md; spec authoring deferred to v3.15)"
constraints:
  - "ADR-001 (conversation layer only — limits scope)"
  - "AGENTS.md CLI Agent Skills Warning section"
  - "AGENTS.md Permission Governance section"
status: proposed
originator: operational-evidence
```

---

## Constraints

| Constraint | Source | Description |
|------------|--------|-------------|
| Conversation layer only | ADR-001 | AGET operates within the CLI conversation, not as runtime |
| Single principal model | L688 (Path A), L808 (Arrow's Impossibility) | One principal per agent, not multi-tenant |
| Knowledge inheritance | L330 | Framework Owners must inherit institutional knowledge |
| Evidence-first design | L289 | Audit before architecture, evidence before proposals |
| Gate discipline | L42, REQ-CORE-F-007 | Stop at boundaries, wait for GO |
| REQ-CORE inheritance | REQ-CORE-F-001 | All GOV requirements specialize a CORE requirement; conflicts resolve in CORE's favor |

---

## Traceability

| Requirement | Forward → Specification | Inherits ← REQ-CORE |
|-------------|-------------------------|---------------------|
| REQ-GOV-F-001 | CAP-GOV-001 | REQ-CORE-F-007 |
| REQ-GOV-F-002 | SKILL-024 (aget-propose-actions) | REQ-CORE-F-005 |
| REQ-GOV-F-003 | AGET_ISSUE_GOVERNANCE_SPEC v2.1.0, R-ISSUE-001—014, SKILL-040 | REQ-CORE-Q-009 |
| REQ-GOV-F-004 | CAP-PP-001—007, AGET_PROJECT_PLAN_SPEC | REQ-CORE-F-002, REQ-CORE-F-007 |
| REQ-GOV-Q-001 | CAP-PP-002 | REQ-CORE-Q-010 |
| REQ-GOV-Q-002 | CAP-SAFETY-001 (PROPOSED) | REQ-CORE-F-005, REQ-CORE-Q-009 |

---

## Evidence Summary

| L-doc | Title | Requirement(s) |
|-------|-------|----------------|
| L42 | Gate Discipline | REQ-GOV-F-001, Constraints |
| L99 | Every Agent is a Worker | REQ-GOV-Q-002 |
| L340 | Execution Governance Artifact | REQ-GOV-F-004 |
| L342 | Session Scope Validation | REQ-GOV-F-001, REQ-GOV-F-002 |
| L474 | Skills Enforcement Model | REQ-GOV-Q-002 |
| L500 | Permission Governance | REQ-GOV-Q-002 |
| L520 | Issue Governance Gap | REQ-GOV-F-003 |
| L638 | Private-First Routing | REQ-GOV-F-003 |
| L335 | Memory Architecture | REQ-GOV-Q-001 |
| L675 | Consequence Gap | REQ-GOV-F-004 |

---

## Promotion Notes (v0.1 → v0.2)

Changes from `scratchpad/REQ-GOV_agent_governance_draft_v0.1.md` (2026-03-27):

- **Status**: draft → proposed
- **Inheritance**: Added explicit REQ-CORE inheritance section + per-requirement inheritance column. Each REQ-GOV-* now names which REQ-CORE-* requirement it specializes.
- **Format conformance**: Quoted multi-line YAML evidence list entries (REQUIREMENTS_FORMAT v1.0 conformance). Added "REQ-CORE inheritance" mention to rationale fields where applicable.
- **Spec references refreshed**: AGET_ISSUE_GOVERNANCE_SPEC v2.0.0 → v2.1.0; SKILL-040 noted as Strict (ADR-008).
- **Constraints**: Added REQ-CORE inheritance constraint and L688/L808 grounding for single-principal model.
- **Substance preserved**: All 4 functional + 2 quality requirements unchanged in intent. Only metadata, inheritance, and references refreshed.

Promotion authority: Principal-directed via same-session NBA chain 2026-04-18.

---

*REQ-GOV v0.2.0 — Agent Governance Requirements*
*Second domain-specific REQ-* document; specializes REQ-CORE_critical_foundations.md.*
*4 functional + 2 quality requirements, grounded in 10 L-docs and 1 cross-cutting REQ-CORE.*
