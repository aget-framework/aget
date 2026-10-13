# REQ-CORE: Critical Foundational Requirements

**Version**: 0.2.2
**Date**: 2026-10-12 (editorial correction; requirement statements retain their 2026-09-26 source edition)
**Status**: proposed (all requirement blocks; this correction does not adopt them)
**Domain**: CORE (cross-cutting, foundational)
**Specifications**: AGET_SPEC_FORMAT, REQUIREMENTS_FORMAT, ADR-001, ADR-004, ADR-005, ADR-008, AGET_SESSION_SPEC, AGET_ISSUE_GOVERNANCE_SPEC, AGET_RELEASE_SPEC, governance/MISSION.md
**Author**: aget-framework
**Tracking**: #725 (requirements publication), #539 (community documentation), #808 (discoverability)

---

## Overview

This document presents **sixteen proposed foundational requirements** of the AGET framework — the cross-cutting, foundational properties that define what AGET *is*. These are the requirements that, if violated, would make the resulting system not-AGET, regardless of the specific domain in question (release, session, governance, etc.).

These requirements are deliberately top-level. They are not intended to enumerate every requirement of every domain (those live in `REQ-{DOMAIN}_*.md` documents). Instead, they capture the principles every domain document inherits from, and the constraints every specification must respect.

The set uses three explanatory anchors, whose meanings are stated here so that private source records are not needed to interpret the requirements:

1. **[Two-level model](#two-level-model)** (historical source label L742) — Requirements (human level, principal-owned) and Specifications (contract level, framework-owned, EARS-formatted) are distinct artifacts with forward traceability.
2. **[Evidence-driven graduation](#evidence-driven-graduation)** (historical source label L700) — Requirements emerge from operational experience (bottom-up), not from PRDs (top-down). The principal curates and approves graduation; agents do not author requirements declaratively.
3. **[Memory and the knowledge base](#memory-and-the-knowledge-base)** (historical source label L335) — The KB is the collaboration substrate. Sessions recover context fast and contribute back.

Each [requirement](REQUIREMENTS_FORMAT.md#purpose) below carries a [fit criterion](REQUIREMENTS_FORMAT.md#field-definitions) that is testable *without reading the corresponding specification*, providing the bridge between human-readable intent and EARS-formalized contracts.

---


## Publication context and meanings

**Audience and scope:** Readers, builders and maintainers of the public framework. This is the cross-cutting foundational requirement set, not the full inventory of domain requirements and not a report that these needs are implemented.

| Field | Disposition |
|---|---|
| Publication edition | 0.2.2, October 12, 2026. Editorial correction of the 0.2.0 requirement set; all sixteen YAML requirement blocks retain their original text and proposed status. |
| Framework source basis | [Public source revision da2b6f725c72ef4b2a8ca258786e9a74dc596f03](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/requirements/REQ-CORE_critical_foundations.md), read for this correction. This identifies documentary evidence, not tested software. |
| Intended applicability | These proposed needs address framework collaboration and publication governance across domains. Their intended scope is not limited to one release; their adoption and assessed applicability to any numbered release are **not established** by this page. |
| Release membership | The [v3.36.0 tagged document](https://github.com/aget-framework/aget/blob/24de1eb0104962ef7aab39f05ccc740876d5e5f2/requirements/REQ-CORE_critical_foundations.md) is the earlier 0.2.0 edition. This corrected edition is a later documentation revision, **not the file included in that tag**. All sixteen proposed YAML requirement blocks are unchanged from the tagged document. Tagged inclusion does not adopt them or establish satisfaction or runtime compatibility. |
| Evidence strength | Editorial population, metadata and summary checks only. Existing verification labels and source reports are historical; this revision runs no implementation acceptance tests and makes no runtime compatibility claim. |

The framework Aget is the accountable publication maintainer. The human [Principal](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_VOCABULARY_SPEC.md#organizational-terms) retains authority over adopting the needs. Historical principal directions explain the proposals' origins; publication or this edit does not change `status: proposed`. Proposed “shall” statements and the constraints below describe the intended contract, not newly adopted obligations.

### Two-level model

[Requirements and specifications](REQUIREMENTS_FORMAT.md#two-level-model-l742) distinguish what the Principal wants from the contracts used to make that intent testable. In the blocks below, `specifications:` lists contract identifiers under the [published field rules](REQUIREMENTS_FORMAT.md#field-definitions). The [vocabulary's Aget_Specification](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_VOCABULARY_SPEC.md#L951-L957) instead denotes a formal document. Those senses differ: a listed clause is not the entire specification document. This editorial correction preserves the proposed field convention; harmonizing the two definitions remains the maintainer's work before a substantive change to that convention.

### Evidence-driven graduation

Here graduation means progressing from observed need or an explicit Principal direction to a formal contract, as stated by [F-002](#req-core-f-002). The [format's evidence field](REQUIREMENTS_FORMAT.md#field-definitions) carries provenance; a source label by itself is not public verification of the underlying observation. Private lesson and ledger labels in the preserved blocks remain provenance labels, not accessible public evidence. Their operative rationale and acceptance criteria are stated in each block.

### Memory and the knowledge base

Here the knowledge base means the persistent context and contribution records described by [F-003](#req-core-f-003) and [F-004](#req-core-f-004). A [collaboration session](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/docs/architecture/grounded-views-2026-10-08/accepted-draft/public-model.json#L242-L245) is a bounded work episode; its parent, [Channel Interaction](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/docs/architecture/grounded-views-2026-10-08/accepted-draft/public-model.json#L1269-L1273), is a bounded communicative exchange. The portable companion also supplies these meanings. This usage does not equate the persistent records with the runtime that reads them. A [gate](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_VOCABULARY_SPEC.md#L474-L475) is a decision checkpoint with deliverables and verification tests; [F-007](#req-core-f-007) states the proposed completion discipline.

The original blocks below are preserved so readers can distinguish editorial explanations from changes to the proposed needs. Each `description`, `rationale`, `evidence` and `fit_criterion` must be read together. Source labels whose public targets are unresolved have a common owner and review trigger in [Maintenance](#maintenance-and-open-evidence).

---

## Functional Requirements

### REQ-CORE-F-001

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

### REQ-CORE-F-002

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

### REQ-CORE-F-003

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

### REQ-CORE-F-004

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

### REQ-CORE-F-005

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

### REQ-CORE-F-006

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
  - "CAP-DEGRADE-001 (Three-Tier Capability Degradation — authored 2026-04-19 in AGET_FRAMEWORK_SPEC.md, 8 sub-requirements)"
constraints:
  - "ADR-004 (Three-tier degradation: gh → git → filesystem) — the architectural decision this REQ operationalizes"
status: proposed
originator: principal
```

### REQ-CORE-F-007

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

### REQ-CORE-Q-008

```yaml
id: REQ-CORE-Q-008
title: "Framework Reconstructability"
type: quality
category: Maintainability
description: >
  An outsider can rebuild what the framework does and why from its
  public side alone. The most authoritative layers are the most
  visible: the requirements that drive the framework, and the decisions
  behind them, are published — not only the specifications and tests
  that follow from them.
rationale: >
  Public visibility has run opposite to authority: in April 2026
  requirements had about 20% public coverage while tests were the most
  complete layer, and by September 2026 the gap had widened. Outside
  readers could see what the framework does but not why, which blocks
  independent review and adoption. This requirement's first target
  (v3.16.0) lapsed without an instrument or an owner; it is revived
  with both.
evidence:
  - "Principal directive 2026-04-16: reverse-engineerability should be manifest"
  - "Inverted authority gradient, measured April 2026 and re-measured September 2026"
  - "Principal rulings 2026-09-26: publish a plain decision log; refresh requirements from the ledger; judge at the next release"
fit_criterion: >
  At each release the framework openness measurement reports four
  things: (1) the public decision log covers every framework decision
  made since its start date, other than one-night operational ones;
  (2) every principal requirement that is neither ruled private nor
  routed to a specification has a public counterpart; (3) every public
  specification area traces back to at least one public requirement;
  (4) every highlighted term on a public page has a public definition.
  Items 1 and 2 are first judged at the first release after
  2026-09-26; items 3 and 4 at the release after that.
priority: P1
constraints:
  - "Framework openness measurement (not yet public)"
  - "A release check that fails when public requirements fall behind the principal's requirements (proposed for the release specification)"
status: proposed
originator: principal
```

### REQ-CORE-Q-009

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

### REQ-CORE-Q-010

```yaml
id: REQ-CORE-Q-010
title: "Collaboration-Outcomes Optimization"
type: quality
category: Interaction Capability
description: >
  AGET optimizes for human-AI collaboration outcomes, managing
  tradeoffs across five dimensions: OUTCOMES (fixed target),
  TIME, BUDGET, RISK, and DISCOVERY. Design decisions shall favor
  coherence, auditability, and shared understanding — not maximize
  throughput, minimize cost, eliminate risk, or preempt the
  principal's capacity to encounter their own domain.
rationale: >
  This is the foundational design philosophy distinguishing AGET
  from autonomous-agent frameworks. The tradeoff model is
  five-dimensional: OUTCOMES is the fixed optimization target;
  TIME, BUDGET, RISK, and DISCOVERY are managed variables.
  DISCOVERY (L905, grounded in Atkinson 1999 organizational and
  professional learning) captures the principal's encounter
  capacity — the conditions under which latent wants form (L898).
  Without this axis, every gate, evidence requirement, and
  authority check risks being reframed as friction to optimize
  away rather than a feature to preserve.
evidence:
  - "DESIGN_PHILOSOPHY line 480: 'AGET optimizes for human-AI partnership quality'"
  - "L99 (Every agent is a worker; supervision is a capability)"
  - "L143 (AGET = Configuration & Lifecycle Management for CLI-Based Human-AI Collaborative Coding)"
  - "L905 (Collaboration Optimization 5D Model — OUTCOMES + TIME/BUDGET/RISK/DISCOVERY; 3 grounded options)"
  - "L904 (Requirements Execution-Formation Asymmetry — companion gap; all 10 most-aligned REQs are execution-layer)"
  - "L898 (Desire-Discovery Erosion — DISCOVERY axis: automation preempts encounter, erodes latent-want formation)"
  - "Atkinson 1999 Square Route — organizational learning + professional learning as explicit success criteria"
  - "PRINCE2 hexagon — Benefits distinct from Quality (confirms OUTCOMES over quality as label)"
  - "governance/MISSION.md"
fit_criterion: >
  (1) ADRs that propose performance, throughput, or autonomy
  optimizations cite a 5D tradeoff analysis (OUTCOMES / TIME /
  BUDGET / RISK / DISCOVERY) in their Consequences section.
  (2) Optimization proposals that lack this analysis are flagged
  at review. (3) Features that reduce DISCOVERY without explicit
  principal consent are escalated per L898 / L904.
  Verifiable by ADR review pass at gate boundaries.
priority: P0
specifications:
  - "RUBRIC_session_outcome_value_v1.0 (assessment view of collaboration outcomes per session)"
  - "RUBRIC_cross_session_dialogue_depth_v1.0 (assessment view of collaboration outcomes across sessions)"
constraints:
  - "governance/MISSION.md (the mission this REQ operationalizes)"
  - "governance/CHARTER.md (charter scope boundary)"
  - "DESIGN_PHILOSOPHY line 480 (source of the partnership-quality principle; 5D model is the operationalization)"
  - "L688 (Path A — sovereignty is individual; DISCOVERY axis is the formation-capacity corollary)"
status: proposed
originator: principal
```

---

## Added 2026-09-26 — from the principal's requirements ledger

These requirements were ruled by the principal between July and September 2026 and held only in a private ledger until this refresh (framework openness rulings, 2026-09-26). Names of private agents, hosts and internal identifiers are stripped; each states the general principle. Across the whole ledger (not per file), three further entries read as contract-level and are routed to specifications instead of this layer.

### REQ-CORE-F-011

```yaml
id: REQ-CORE-F-011
title: "A Home for Un-Adopted Wants"
type: functional
description: >
  The framework keeps a first-class place for wants the principal has
  not yet adopted as goals, above the goal layer, so that a hope is
  recorded as a hope rather than lost or promoted into a commitment too
  early.
rationale: >
  Without a place for un-adopted wants, they are either forgotten or
  forced into goals the principal never committed to.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-07-18"
fit_criterion: >
  A want can be recorded without creating a goal, and a later promotion
  to a goal is a separate, recorded act.
priority: P2
status: proposed
originator: principal
```

### REQ-CORE-F-012

```yaml
id: REQ-CORE-F-012
title: "Concurrent Sessions Governed by Visibility"
type: functional
description: >
  Several attended sessions working in one repository at once are
  acceptable practice. They are governed by making each visible to the
  others, not by prohibiting them.
rationale: >
  Parallel sessions are how the principal works; a prohibition would be
  ignored, while visibility prevents collisions.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-07-18"
fit_criterion: >
  A session starting while another is live in the same working tree is
  told so at start-up, with enough detail to avoid overwriting its
  work.
priority: P1
status: proposed
originator: principal
```

### REQ-CORE-F-013

```yaml
id: REQ-CORE-F-013
title: "Ambiguous Authorization Changes Nothing"
type: functional
description: >
  When a principal authorization could plausibly refer to more than one
  pending action, nothing is changed and the agent asks which one was
  meant. A short approval binds directly only when exactly one action
  is pending.
rationale: >
  Acting on a guessed referent spends the principal's authority on
  something they may not have approved.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  Given two live candidates and a bare approval, the agent makes zero
  changes and emits a request naming both candidates.
priority: P0
status: proposed
originator: principal
```

### REQ-CORE-Q-014

```yaml
id: REQ-CORE-Q-014
title: "Self-Claims Are Checkable or Removed"
type: quality
category: Functional Suitability
description: >
  Any claim the framework makes about itself — in documentation,
  release notes or records — can be checked by a reader, or it is
  removed. This is the operative meaning of done for framework records.
rationale: >
  An uncheckable self-claim cannot be told apart from an error, and
  accumulates into a record nobody can trust.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-16"
fit_criterion: >
  Sampling claims from a release's public records, each names the check
  or source that confirms it; a claim with neither is absent.
priority: P1
status: proposed
originator: principal
```

### REQ-CORE-Q-015

```yaml
id: REQ-CORE-Q-015
title: "Counts Carry Their Population"
type: quality
category: Functional Suitability
description: >
  Every count, census or coverage figure the framework states carries
  the exact population it was derived over: where it searched, how
  deep, and what it included.
rationale: >
  A figure without its population cannot be reproduced, and the same
  number can mean different things at different vantage points.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-29 (ruled for one agent; proposed framework-wide)"
fit_criterion: >
  Each figure in a sampled public record is accompanied by its search
  root, bound and inclusion rule, enough to re-run it.
priority: P1
status: proposed
originator: principal
```


### REQ-CORE-F-016

```yaml
id: REQ-CORE-F-016
title: "The Openness Position Is Stated"
type: functional
description: >
  The framework states publicly, in plain words, what kind of open it is:
  its code is released under the Apache 2.0 license; its deliberation is
  private first; and the reasons for its decisions are published in a
  public decision log at governance/DECISION_LOG.md.
rationale: >
  Measured against the Open Source Definition the framework is open source,
  because that definition tests only the license. Measured against standards
  that ask whether a system can be rebuilt, or whether it is developed in the
  open, it is not. Saying only "open source" without that distinction reads as
  open-washing; stating the position keeps the public claim true.
evidence:
  - "Principal ruling 2026-09-26: state the openness position as a public requirement"
  - "Openness study 2026-09-26 against the Open Source Definition, the Open Source AI Definition, the Model Openness Framework and the Apache Way"
fit_criterion: >
  This requirements set carries the three-part statement (license,
  private-first deliberation, public decision log), and the public decision
  log exists at the location the statement names.
priority: P1
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

Population: all sixteen `id: REQ-CORE-*` YAML blocks in this file, without following other files. Every linked block supplies its stated need (`description`), rationale, source claims (`evidence`) and acceptance check (`fit_criterion`). The table preserves each block's declared forward contract population; an undeclared contract is shown rather than silently omitted. Listing a contract does not prove implementation or acceptance.

| Requirement and acceptance | Declared forward contract | Domain coverage | Resolution or limit |
|---|---|---|---|
| [REQ-CORE-F-001](#req-core-f-001) | [RUBRIC_requirement_quality_v1.0](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/rubrics/RUBRIC_requirement_quality_v1.0.md) | All REQ-* docs | Public rubric assesses requirement-artifact quality; this is not implementation acceptance |
| [REQ-CORE-F-002](#req-core-f-002) | CAP-PP-006 (as named in the block) | All spec authoring | Unresolved meaning: the public project-plan spec uses CAP-PP-006 for risk assessment, not evidence verification |
| [REQ-CORE-F-003](#req-core-f-003) | [CAP-SESSION-001-03/04](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_SESSION_SPEC.md#cap-session-001-wake-up-protocol) | Session lifecycle | The cited clauses cover identity and silent execution, not the complete timed four-class acceptance criterion |
| [REQ-CORE-F-004](#req-core-f-004) | [CAP-SESSION-002](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_SESSION_SPEC.md#cap-session-002-context-recovery) + [CAP-SESSION-013](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_SESSION_SPEC.md#cap-session-013-close-session-protocol) (block labels it PROPOSED) | Session lifecycle | Mismatch: 002 is context recovery, not wind-down; 013 now has public clauses. Original block retained pending reconciliation |
| [REQ-CORE-F-005](#req-core-f-005) | SKILL-024 | Action proposal | Identifier mismatch: the public tree names SKILL-024 as aget-review-pr, not aget-propose-actions; binding unresolved |
| [REQ-CORE-F-006](#req-core-f-006) | [CAP-DEGRADE-001](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_FRAMEWORK_SPEC.md#cap-degrade-001-three-tier-degradation-path) | All skills/commands | Public contract explicitly inherits from F-006; satisfaction not reassessed |
| [REQ-CORE-F-007](#req-core-f-007) | [CAP-REL-022](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_RELEASE_SPEC.md#cap-rel-022-gate-execution-enforcement-l605-er-gate-enforce); CAP-GATE-001 PROPOSED | All gated work | Release gate contract resolves; proposed broader contract and framework-wide sufficiency remain unresolved |
| [REQ-CORE-Q-008](#req-core-q-008) | No specifications field declared | Public framework | Acceptance is the block’s fit criterion; public measurement dependency unresolved |
| [REQ-CORE-Q-009](#req-core-q-009) | [R-ISSUE-011](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_ISSUE_GOVERNANCE_SPEC.md#L590-L593) + [SKILL-040](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/.aget/specs/skills/SKILL-040_aget-file-issue.yaml) | Issue filing | Mismatch: R-ISSUE-011 requires approval; R-ISSUE-012 concerns sanitization. Original requirement preserved; mapping repair owed |
| [REQ-CORE-Q-010](#req-core-q-010) | RUBRIC_session_outcome_value_v1.0; RUBRIC_cross_session_dialogue_depth_v1.0 | Design decisions | Named contracts; public targets not resolved in this correction |
| [REQ-CORE-F-011](#req-core-f-011) | No specifications field declared | Un-adopted wants | Acceptance is the block’s fit criterion; forward contract not declared |
| [REQ-CORE-F-012](#req-core-f-012) | No specifications field declared | Concurrent sessions | Acceptance is the block’s fit criterion; forward contract not declared |
| [REQ-CORE-F-013](#req-core-f-013) | No specifications field declared | Authorization | Acceptance is the block’s fit criterion; forward contract not declared |
| [REQ-CORE-Q-014](#req-core-q-014) | No specifications field declared | Checkable public claims | Acceptance is the block’s fit criterion; forward contract not declared |
| [REQ-CORE-Q-015](#req-core-q-015) | No specifications field declared | Counts and coverage | Acceptance is the block’s fit criterion; forward contract not declared |
| [REQ-CORE-F-016](#req-core-f-016) | No specifications field declared | Openness position | Acceptance is the block’s fit criterion and named public decision-log location; forward contract not declared |

The public [project-plan specification](https://github.com/aget-framework/aget/blob/da2b6f725c72ef4b2a8ca258786e9a74dc596f03/specs/AGET_PROJECT_PLAN_SPEC.md#cap-pp-006-risk-assessment) exposes the F-002 citation mismatch. A plausible related requirement is not substituted without review. The seven blocks without a `specifications:` field have their own fit criteria but no declared forward contract; that gap is not satisfaction of F-001. Framework maintenance owns each unresolved citation and missing contract, with reconciliation required before the next substantive requirement revision or use of the affected citation as verification evidence.

---

## Evidence

The sixteen proposed requirements cite the following source families. The lesson and ledger records are historical/private provenance unless a public target is linked; this list does not independently verify the source claims:

- **Two-level model**: L742, L748, ISO/IEC/IEEE 29148:2018, Volere
- **Evidence-driven inversion**: L700, L436, ADR-008
- **Memory architecture**: L335 (Extended Mind, Transactive Memory, Distributed Cognition, Stigmergy, Cybernetics)
- **Authority and governance**: Decision Authority Matrix, L178, L42, L001, L002, ADR-005
- **Degradation and portability**: ADR-004, L185
- **Reconstructability**: inverted authority gradient measured April 2026, re-measured September 2026; public decision log started 2026-09-26
- **Routing security**: L638, L520, R-ISSUE-011
- **Foundational philosophy**: DESIGN_PHILOSOPHY, L99, L143, governance/MISSION.md

---

## Verification Status (spec+verify-first)

This is a verification plan and historical evidence register. No implementation acceptance test was run for this editorial correction. Prior “VERIFIED” and “PARTIAL” reports lack a source-bound public test receipt here; in particular, tooling existence alone does not verify routing behavior. Their labels and summarized reasons are retained in the historical column, not endorsed as current satisfaction.

| Requirement | Verification method (see block fit criterion) | Current disposition | Prior edition report |
|---|---|---|---|
| [REQ-CORE-F-001](#req-core-f-001) | Audit forward and reverse contract references | NOT REASSESSED | PENDING |
| [REQ-CORE-F-002](#req-core-f-002) | Inspect evidence before contract graduation | NOT REASSESSED | PENDING |
| [REQ-CORE-F-003](#req-core-f-003) | Time context recovery and inspect four output classes | NOT REASSESSED | PARTIAL (informal timing) |
| [REQ-CORE-F-004](#req-core-f-004) | Inspect a contribution and wind-down warning behavior | NOT REASSESSED | PARTIAL (artifact presence) |
| [REQ-CORE-F-005](#req-core-f-005) | Exercise proposal authority classifications | NOT REASSESSED | VERIFIED (past-session output) |
| [REQ-CORE-F-006](#req-core-f-006) | Exercise or inspect the filesystem-only path | NOT REASSESSED | PENDING |
| [REQ-CORE-F-007](#req-core-f-007) | Audit gate deliverables against plan-update commits | NOT REASSESSED | PARTIAL (enforcement in progress) |
| [REQ-CORE-Q-008](#req-core-q-008) | Measure all four openness criteria | NOT REASSESSED | PENDING |
| [REQ-CORE-Q-009](#req-core-q-009) | Exercise routing and sanitization behavior | NOT REASSESSED | VERIFIED (tooling existence) |
| [REQ-CORE-Q-010](#req-core-q-010) | Review proposed optimizations against the five dimensions | NOT REASSESSED | PENDING |
| [REQ-CORE-F-011](#req-core-f-011) | Record a want without committing a goal; separately test promotion | NOT ASSESSED | No row in prior table |
| [REQ-CORE-F-012](#req-core-f-012) | Start a concurrent session and inspect visibility information | NOT ASSESSED | No row in prior table |
| [REQ-CORE-F-013](#req-core-f-013) | Present ambiguous approval over two candidates; require zero changes | NOT ASSESSED | No row in prior table |
| [REQ-CORE-Q-014](#req-core-q-014) | Sample public claims for a checkable source | NOT ASSESSED | No row in prior table |
| [REQ-CORE-Q-015](#req-core-q-015) | Reproduce sampled counts from declared populations | NOT ASSESSED | No row in prior table |
| [REQ-CORE-F-016](#req-core-f-016) | Read license, deliberation position and public decision log | NOT ASSESSED | No row in prior table |

**Population and totals:** The ten rows present in the 0.2.0 verification table reported **2 VERIFIED, 3 PARTIAL and 5 PENDING**; its former 2/4/4 summary was arithmetically wrong. The six later requirement blocks had no rows in that table. This edition accounts for **16/16** YAML requirement blocks: **10 NOT REASSESSED** historical rows and **6 NOT ASSESSED** added rows. **0/16** have a newly executed acceptance result from this editorial correction. These populations are limited to this file and the explicitly identified prior table; they are not a framework compliance census.

The framework maintainer owns the verification backlog. Review the affected fit criterion on a supporting implementation change or before claiming requirement satisfaction; missing results remain explicit.

---

## Coherence Check (coherence-next)

The sixteen listed requirements cover the following declared concerns. This is an editorial coverage map, not proof of complete framework coverage or mutual independence.

| Concern | Requirements |
|---|---|
| Foundational philosophy | Q-010 |
| Two-level model and evidence | F-001, F-002 |
| Session lifecycle and concurrency | F-003, F-004, F-012 |
| Authority and commitment | F-005, F-007, F-011, F-013 |
| Portability and degradation | F-006 |
| Public visibility and openness | Q-008, F-016 |
| Boundary security | Q-009 |
| Checkable claims and populations | Q-014, Q-015 |

The map includes every YAML requirement block once. Some concerns interact; this edit does not claim that the requirements are exhaustive, non-overlapping or independently satisfiable.

## Maintenance and open evidence

The framework Aget owns this publication's accuracy and its traceability/verification backlog. Use the [public issue tracker](https://github.com/aget-framework/aget/issues) to report a discrepancy or request an accessible source. Reviews occur on a changed supporting source, definition, requirement or implementation, a reported discrepancy, and before a substantive publication update. Release-triggered review is required only where a relevant source or applicability claim changes; publication maintenance also occurs between releases.

Open items include the disclosed forward-contract gaps and mismatches, public evidence for inherited historical source/verification claims, the document-versus-clause meaning distinction, and numbered-release applicability and membership in other releases. The maintainer owns each item. Resolve or explicitly redisposition it before the next substantive revision or earlier reuse of the affected claim; verify compatibility or membership before asserting either. Unknown applicability is disclosure, not compatibility evidence.

This revision preserves the sixteen proposed requirement blocks verbatim. It updates presentation, public meaning links and evidence limits; it does not approve new obligations, promote private records, or claim the proposed needs have been fulfilled.

---

*REQ-CORE: Critical Foundational Requirements v0.2.2*
*"What the principal wants from the framework itself — published, traceable, assessable."*
