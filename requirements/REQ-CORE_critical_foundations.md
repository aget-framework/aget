# REQ-CORE: Critical Foundational Requirements

**Version**: 0.1.0
**Date**: 2026-04-18
**Status**: proposed
**Domain**: CORE (cross-cutting, foundational)
**Specifications**: AGET_SPEC_FORMAT, REQUIREMENTS_FORMAT, ADR-001, ADR-004, ADR-005, ADR-008, AGET_SESSION_SPEC, AGET_ISSUE_GOVERNANCE_SPEC, AGET_RELEASE_SPEC, governance/MISSION.md
**Author**: private-aget-framework-AGET
**Tracking**: #725 (requirements publication), #539 (community documentation), #808 (discoverability)

---

## Overview

This document formalizes the **ten most critical requirements** of the AGET framework — the cross-cutting, foundational properties that define what AGET *is*. These are the requirements that, if violated, would make the resulting system not-AGET, regardless of the specific domain in question (release, session, governance, etc.).

These requirements are deliberately top-level. They are not intended to enumerate every requirement of every domain (those live in `REQ-{DOMAIN}_*.md` documents). Instead, they capture the principles every domain document inherits from, and the constraints every specification must respect.

The set is grounded in three architectural anchors:

1. **L742 Two-Level Model** — Requirements (human level, principal-owned) and Specifications (contract level, framework-owned, EARS-formatted) are distinct artifacts with forward traceability.
2. **L700 Evidence-Driven Inversion** — Requirements emerge from operational experience (bottom-up), not from PRDs (top-down). The principal curates and approves graduation; agents do not author requirements declaratively.
3. **L335 Memory Architecture** — The KB is the collaboration substrate. Sessions recover context fast and contribute back.

Each requirement below carries a Volere-style fit criterion that is testable *without reading the corresponding specification*, providing the bridge between human-readable intent and EARS-formalized contracts.

---

## Functional Requirements

```yaml
id: REQ-CORE-F-001
title: "Two-Level Model Coherence"
type: functional
description: >
  AGET shall maintain parallel human-level requirements (REQ-*) and
  contract-level artifacts with explicit forward traceability from
  each requirement to one or more contracts. Acceptable contract
  types: CAP-* (capability specs), R-* (requirement specs),
  SKILL-* (skill specs), RUBRIC_* (rubric-as-spec per L749 duality).
rationale: >
  Without forward traceability, requirements become decorative (L671)
  and contracts lose accountability to stakeholder intent. The
  two-level model only delivers value when the levels are linked.
  Per L749 duality, rubrics ARE the assessment view of requirements
  and therefore qualify as contracts; per the AGET skill architecture,
  skills carry internal CAP-* specs and qualify as compound contracts.
evidence:
  - "L742 (Requirements human level / Specifications contract level)"
  - "L748 (Requirements artifact storage gap)"
  - "L749 (Requirements-Rubric Duality)"
  - "ISO/IEC/IEEE 29148:2018 (StRS → SyRS traceability)"
  - "C298 (Software System Requirement, ISO/IEC/IEEE 29148:2018)"
fit_criterion: >
  Every REQ-* document with status >= proposed declares a non-empty
  `specifications:` field listing only identifiers of types CAP-*,
  R-*, SKILL-*, or RUBRIC_*. ADR/governance/L-doc/SOP/META-DOC
  references appear in `constraints:` or `evidence:` fields per
  REQUIREMENTS_FORMAT v1.1 routing. Reverse spot-check: at least
  80% of CAP-SESSION-* / CAP-REL-* / CAP-GOV-* specs are reachable
  from at least one REQ-* document.
priority: P0
specifications:
  - "RUBRIC_requirement_quality_v1.0 (this REQ is the foundational input to the rubric; rubric serves as the verification contract per L749 duality)"
constraints:
  - "REQUIREMENTS_FORMAT v1.1 (the format meta-doc this REQ implicitly conforms to)"
  - "AGET_SPEC_FORMAT v1.3 (the parallel meta-doc for the contract level)"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-F-002
title: "Evidence-Driven Graduation"
type: functional
description: >
  Operational evidence (L-docs, observations, principal directives)
  shall precede formalization. Specifications do not appear without
  traceable origin in operational experience or explicit principal
  intent.
rationale: >
  AGET inverts traditional product management: requirements bubble
  UP from operation, not DOWN from analysis. Specifications without
  evidence are speculative; evidence without graduation is wasted
  learning.
evidence:
  - "L700 (Evidence-driven requirements model — inversion)"
  - "L436 (PROJECT_PLAN to SOP graduation, 3+ occurrences threshold)"
  - "L789 (graduation pattern instances)"
fit_criterion: >
  Every CAP-* or R-* specification with status >= validated includes
  either (a) >= 1 L-doc reference in its evidence/source field, OR
  (b) explicit principal directive citation with date, OR (c) >= 3
  operational occurrences documented in PROJECT_PLAN retrospective.
priority: P0
specifications:
  - "CAP-PP-006 (Evidence Verification — `/aget-create-project` skill enforces evidence requirement at project gate)"
constraints:
  - "ADR-008 (Advisory → Strict → Generator enforcement progression)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-CORE-F-003
title: "Session Context Recovery"
type: functional
description: >
  An agent shall recover essential session context — identity, active
  projects, recent findings, and pending work — within two minutes of
  session start, so the principal can resume collaboration without
  re-explaining state.
rationale: >
  Context recovery latency is the dominant cost of session boundaries.
  Slow recovery erodes the value of memory architecture and forces
  the principal to act as transactive memory store (Wegner) rather
  than the KB itself fulfilling that role.
evidence:
  - "L335 (Memory Architecture: 'recover essential context within 2 minutes')"
  - "L748 (Requirements home gap — session context as candidate REQ)"
  - "CAP-SESSION-001 wake-up protocol field deployment evidence"
fit_criterion: >
  `python3 scripts/wake_up.py` (or its successor `aget_open_session.py`)
  completes within 120 seconds wall-clock and emits the four context
  classes (identity, projects, findings, pending) in its summary
  output. Verifiable by timing measurement on any AGET agent.
priority: P0
specifications:
  - CAP-SESSION-001-03
  - CAP-SESSION-001-04
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-F-004
title: "KB Net-Positive Sessions"
type: functional
description: >
  Every agent session shall leave the knowledge base in a better
  state than it was found — at minimum one lesson, observation,
  refinement, or governed artifact contribution per session.
rationale: >
  Memory is the collaboration substrate (L335). A session that
  consumes context but contributes nothing back is a memory leak —
  the KB stops compounding. Net-positive is the structural anti-leak.
evidence:
  - "L335 (Memory Architecture: 'every session should leave the KB better than it found it')"
  - "Wind-down protocol field evidence (sessions/markers/*)"
  - "L671 (decorative-metadata risk if unenforced)"
fit_criterion: >
  Wind-down detects at least one of: new `.aget/evolution/L*.md`,
  new `sessions/` artifact, new observation, modified governance/
  spec/skill/SOP, or contributed PROJECT_PLAN update. Absence triggers
  a non-fatal warning surfaced in the wind-down summary.
priority: P1
specifications:
  - "CAP-SESSION-002 (wind-down protocol)"
  - "CAP-SESSION-013 (close-session triage — see PROPOSAL_cap_session_013_close_session_triage.md; spec authoring deferred to v3.15)"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-F-005
title: "Principal Authority Gradient"
type: functional
description: >
  Every action that an agent proposes shall classify the principal's
  required involvement on a five-value gradient: Autonomous, Approve,
  Decide, Execute, or Inform. Agent execution behavior shall adapt
  per classification — not all proposals are equal in authority.
rationale: >
  Without explicit authority classification, agents either over-defer
  (asking the principal about trivia) or over-act (executing items
  that needed explicit GO). The gradient makes the boundary visible
  per-action, not per-session.
evidence:
  - "L178 (Human override principle: acknowledge, commit, execute)"
  - "Operational evidence: 10+ /aget-propose-actions invocations across 6 agents in v3.12.0 lifecycle"
fit_criterion: >
  All `/aget-propose-actions` outputs render a `Principal` column
  with one of {Autonomous, Approve, Decide, Execute, Inform} per
  row. Execute-all default behavior auto-runs only Autonomous items
  and pauses on the others.
priority: P1
specifications:
  - "SKILL-024 (aget-propose-actions skill spec, v1.1.0 — internal CAP-PA-008/009)"
constraints:
  - "inherited/DECISION_AUTHORITY_MATRIX.md (the authority taxonomy this REQ operationalizes per-action)"
  - "DESIGN_DIRECTION_propose_actions.md v0.1.0 (design direction document)"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-F-006
title: "Three-Tier Degradation"
type: functional
description: >
  All command capabilities shall implement a tier_basic path that
  works with filesystem-only access. Higher tiers (gh, git) are
  progressive enhancements layered above tier_basic, not preconditions.
rationale: >
  AGET runs across heterogeneous environments — supervisor agents
  with full tooling, worker agents in restricted contexts, archived
  artifacts examined years later. Hard dependencies on `gh` or `git`
  break recoverability and portability.
evidence:
  - "L185 (Environmental grounding)"
  - "Operational evidence: heterogeneous agent runtime contexts across 32-agent fleet"
fit_criterion: >
  Every skill spec passes a degradation check: a documented
  tier_basic invocation path exists and produces a non-empty,
  meaningful result without invoking external command-line tools
  (gh, git, network APIs). Verified by inspecting the spec's
  Implementation section.
priority: P0
specifications:
  - "CAP-DEGRADE-001 (proposed — see PROPOSAL_cap_framework_degradation.md; spec authoring deferred to v3.15)"
constraints:
  - "ADR-004 (Three-tier degradation: gh → git → filesystem) — the architectural decision this REQ operationalizes"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-F-007
title: "Gate Boundary Discipline"
type: functional
description: >
  Agents shall stop at gate boundaries and wait for explicit principal
  GO before crossing into the next gate's work. A gate is structurally
  complete only when its plan is updated and the update is committed
  — the commit is the proof of compliance, not the deliverables alone.
rationale: >
  Gate slack accumulates without structural enforcement. "While we're
  at it" and "I also..." are how scope expands into the next gate
  without decision. The plan-update-and-commit pattern makes gate
  completion auditable from git history alone.
evidence:
  - "L42 (Stop at gate boundaries, wait for GO)"
  - "L001 / L002 (Gate Execution Discipline + Mid-Gate Checkpoints)"
  - "D71 STRUCTURAL enforcement instances (Gate without plan update flagged in retrospectives)"
fit_criterion: >
  For every PROJECT_PLAN with completed gates, each [x] gate
  deliverable is matched by a commit message referencing the gate ID
  and including V-test results in the commit body or referenced plan
  file. No gate marked complete without a corresponding commit.
priority: P0
specifications:
  - "CAP-REL-022 (Gate Execution Enforcement — closest existing contract; cross-cutting framework-wide CAP-GATE-001 proposed for v3.15 — see PROPOSAL_cap_framework_gate.md)"
constraints:
  - "ADR-005 (Gates = release points)"
  - "AGENTS.md Gate Execution Discipline section (L001)"
status: proposed
originator: principal
```

---

## Quality Requirements

```yaml
id: REQ-CORE-Q-008
title: "Framework Reconstructability"
type: quality
category: Maintainability
description: >
  The framework's most authoritative layers (governance, specifications,
  fleet topology) shall be reverse-engineerable from publicly visible
  artifacts. What is most authoritative shall be most visible — the
  authority gradient and the visibility gradient shall align.
rationale: >
  Today the inverse holds: requirements have 20% public coverage but
  drive everything; fleet topology is internal but constrains
  external integration. External readers cannot reconstruct the
  framework's commitments from what they can see, blocking community
  adoption and external review.
evidence:
  - "L840 (Inverted authority gradient; reverse-engineerability study)"
  - "INIT-FRAMEWORK-TRANSPARENCY (Theme #9, v3.14 cycle)"
  - "Principal directive 2026-04-16: 'reverse-engineerability should be manifest'"
fit_criterion: >
  Reconstructability rubric (per item #29j) scores >= 3/5 on each of
  the dimensions {requirements coverage, specification EARS density,
  test coverage, fleet formalization} for all 15 CAP-* domains by
  v3.16.0. Baseline measured at v3.14.0; trajectory tracked per release.
priority: P1
specifications:
  - "CAP-FLEET-001 (PROPOSED — first capability spec within AGET_FLEET_SPEC.md, #29h in development)"
  - "RUBRIC_reconstructability_v1.0 (PROPOSED — see PROPOSAL_rubric_reconstructability.md, #29j in development)"
constraints:
  - "DESIGN_DIRECTION_framework_transparency.md (#29k — design direction document)"
  - "L840 (Inverted Authority Gradient — the diagnosis this REQ addresses)"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-Q-009
title: "Private-First Routing"
type: quality
category: Security
description: >
  Internal communications, identifiers, and fleet references shall
  default to private routing. Promotion to public artifacts is an
  explicit, sanitized act — never an accidental side effect of normal
  operation.
rationale: >
  AGET fleets contain agent names, project IDs, and session references
  that leak internal capacity, structure, and client identity if
  promoted unsanitized. Default-private inverts the failure mode:
  forgetting to sanitize fails closed (private), not open (public leak).
evidence:
  - "L638 (Private-first issue routing architecture)"
  - "L520 (Issue governance precedent)"
  - "R-ISSUE-011 (promotion-boundary sanitization)"
  - "AGET_ISSUE_GOVERNANCE_SPEC v2.1.0"
fit_criterion: >
  All `gh issue create` invocations route to the configured private
  tracker by default (currently `gmelli/aget-aget`; per #1028 becoming
  fleet-configurable). Promotion to public requires R-ISSUE-011
  sanitization pass with zero matches against `private-*-aget`,
  `gmelli/*`, fleet-size disclosures, internal project IDs, or session
  identifiers. Verifiable via `validate_issue_destination.py --check`
  and `sanitize_issue_content.py --check`.
priority: P0
specifications:
  - "R-ISSUE-011 (promotion-boundary content sanitization within AGET_ISSUE_GOVERNANCE_SPEC v2.1.0)"
  - "SKILL-040 (aget-file-issue, Strict per ADR-008)"
constraints:
  - "AGET_ISSUE_GOVERNANCE_SPEC v2.1.0 (becoming v2.2.0 per #1028) — the meta-spec containing R-ISSUE-* contracts"
  - "L638 (Private-First Issue Routing — the architecture this REQ enforces)"
status: proposed
originator: principal
```

```yaml
id: REQ-CORE-Q-010
title: "Collaboration-Quality Optimization"
type: quality
category: Interaction Capability
description: >
  AGET optimizes for human-AI collaboration quality, not autonomous
  agent speed. Design tradeoffs shall favor coherence, auditability,
  and shared understanding over raw throughput or autonomous
  decision velocity.
rationale: >
  This is the foundational design philosophy that distinguishes AGET
  from autonomous-agent frameworks. Without it, every other
  requirement (gates, evidence, two-level model, principal authority)
  becomes friction to be optimized away rather than feature to be
  preserved.
evidence:
  - "DESIGN_PHILOSOPHY (supervisor inherited): 'AGET optimizes for human-AI collaboration quality, not autonomous agent speed'"
  - "L99 (Every agent is a worker; supervision is a capability)"
  - "L143 (AGET = Configuration & Lifecycle Management for CLI-Based Human-AI Collaborative Coding)"
  - "governance/MISSION.md"
fit_criterion: >
  ADRs that propose performance, throughput, or autonomy
  optimizations cite a coherence-or-collaboration tradeoff analysis
  in their Consequences section. Optimization proposals that lack
  this analysis are flagged at review. Verifiable by ADR review
  pass at gate boundaries.
priority: P0
specifications:
  - "RUBRIC_session_outcome_value_v1.0 (assessment view of collaboration quality per session)"
  - "RUBRIC_cross_session_dialogue_depth_v1.0 (assessment view of collaboration quality across sessions)"
constraints:
  - "governance/MISSION.md (the mission this REQ operationalizes)"
  - "governance/CHARTER.md (charter scope boundary)"
  - "DESIGN_PHILOSOPHY (supervisor inherited): 'AGET optimizes for human-AI collaboration quality, not autonomous agent speed'"
status: proposed
originator: principal
```

---

## Constraints

The following non-negotiable boundaries apply across all REQ-CORE-* requirements:

| Constraint | Source | Implication |
|------------|--------|-------------|
| **Single principal** | L688 (Path A — sovereignty is individual), Arrow's Impossibility (L808) | These requirements assume a single decision-maker. Multi-stakeholder synthesis is out of scope. |
| **Conversation layer only** | ADR-001 | Requirements address agent collaboration, not infrastructure or runtime systems. |
| **Specification-fault principle** | L742 | When a CORE requirement appears violated, the spec is at fault first; check the spec before the implementation. |
| **No spec without evidence** | L700, REQ-CORE-F-002 | Adding a CORE requirement requires either operational evidence or principal directive — no speculation. |

---

## Traceability

| Requirement | Forward → Specification | Domain Coverage |
|-------------|-------------------------|-----------------|
| REQ-CORE-F-001 | RUBRIC_requirement_quality_v1.0 | All REQ-* docs |
| REQ-CORE-F-002 | CAP-PP-006 (Evidence Verification) | All spec authoring |
| REQ-CORE-F-003 | CAP-SESSION-001-03/04 | Session lifecycle |
| REQ-CORE-F-004 | CAP-SESSION-002 + CAP-SESSION-013 (PROPOSED) | Session lifecycle |
| REQ-CORE-F-005 | SKILL-024 (aget-propose-actions) | Action proposal |
| REQ-CORE-F-006 | CAP-DEGRADE-001 (PROPOSED) | All skills/commands |
| REQ-CORE-F-007 | CAP-REL-022 (Gate Execution Enforcement); CAP-GATE-001 PROPOSED | All gated work |
| REQ-CORE-Q-008 | AGET_FLEET_SPEC (PROPOSED), RUBRIC_reconstructability (PROPOSED) | Public framework |
| REQ-CORE-Q-009 | AGET_ISSUE_GOVERNANCE_SPEC v2.1.0, R-ISSUE-011, SKILL-040 | All issue filing |
| REQ-CORE-Q-010 | RUBRIC_session_outcome_value_v1.0, RUBRIC_cross_session_dialogue_depth_v1.0 | Design decisions |

Forward traceability is mandatory (REQ-CORE-F-001). The table above shall remain synchronized with each REQ block's `specifications:` field.

---

## Evidence

The ten requirements above are grounded in operational evidence and architectural anchors:

- **Two-level model**: L742, L748, ISO/IEC/IEEE 29148:2018, Volere
- **Evidence-driven inversion**: L700, L436, ADR-008
- **Memory architecture**: L335 (Extended Mind, Transactive Memory, Distributed Cognition, Stigmergy, Cybernetics)
- **Authority and governance**: Decision Authority Matrix, L178, L42, L001, L002, ADR-005
- **Degradation and portability**: ADR-004, L185
- **Reconstructability**: L840, INIT-FRAMEWORK-TRANSPARENCY (v3.14 theme #9)
- **Routing security**: L638, L520, R-ISSUE-011
- **Foundational philosophy**: DESIGN_PHILOSOPHY, L99, L143, governance/MISSION.md

---

## Verification Status (spec+verify-first)

| Requirement | Verification Method | Status |
|-------------|---------------------|:------:|
| F-001 | Manual audit of REQ + CAP cross-references | PENDING (post-publication) |
| F-002 | Spec authoring checklist amendment | PENDING |
| F-003 | Wake-up wall-clock timing on N agents | PARTIAL (informal evidence) |
| F-004 | Wind-down summary inspection | PARTIAL (sessions/ artifacts present) |
| F-005 | `/aget-propose-actions` output schema check | VERIFIED (this session's output) |
| F-006 | Skill spec degradation field audit | PENDING (#921 spec-coverage work) |
| F-007 | Git history audit for gate IDs in commits | PARTIAL (D71 enforcement in progress) |
| Q-008 | Reconstructability rubric scoring | PENDING (rubric in development, #29j) |
| Q-009 | `validate_issue_destination.py --check` + sanitizer | VERIFIED (tooling exists) |
| Q-010 | ADR review for collaboration-quality rationale | PENDING |

**Overall**: 2/10 VERIFIED, 4/10 PARTIAL, 4/10 PENDING. Verification gaps are tracked as input to future REQ-CORE versions.

---

## Coherence Check (coherence-next)

The 10 requirements form a coherent set covering the AGET stack:

| Layer | Requirements |
|-------|-------------|
| **Foundational philosophy** | Q-010 |
| **Two-level model** | F-001, F-002 |
| **Session lifecycle** | F-003, F-004 |
| **Authority structure** | F-005, F-007 |
| **Portability / degradation** | F-006 |
| **Public visibility** | Q-008 |
| **Boundary security** | Q-009 |

No layer is unrepresented; no requirement duplicates another. Each can fail independently — the set is decomposed, not bundled.

---

*REQ-CORE: Critical Foundational Requirements v0.1.0*
*"What the principal wants from the framework itself — published, traceable, assessable."*
