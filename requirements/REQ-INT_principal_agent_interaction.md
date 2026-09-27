# REQ-INT: Principal–Agent Interaction

**Version**: 0.1.0
**Date**: 2026-09-26 (created from the principal's requirements ledger)
**Status**: proposed
**Domain**: INT (Principal–Agent Interaction)
**Format**: REQUIREMENTS_FORMAT v1.1
**Inherits from**: REQ-CORE_critical_foundations.md (cross-cutting foundations)

---

## Overview

How agents communicate with the principal they serve: what every reply carries, how conformance is enforced, and how interaction quality is measured without misleading anyone.

These requirements were ruled by the principal between July and September 2026 and held only in a private ledger until this refresh (framework openness rulings, 2026-09-26). Names of private agents, hosts and internal identifiers are stripped; each states the general principle. Three further ledger entries read as contract-level and are routed to specifications instead of this layer.

---

## Requirements

```yaml
id: REQ-INT-F-001
title: "Risk-Tiered Conformance Enforcement"
type: functional
description: >
  Conformance in principal–agent interaction is enforced in tiers by
  risk. An ambiguous authorization blocks change immediately;
  lower-risk defects in interaction records are marked and reviewed
  rather than blocking.
rationale: >
  Blocking everything makes the control unusable; blocking nothing lets
  the dangerous case through.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  An ambiguous authorization is blocked in every observed case;
  lower-tier defects are marked and appear in review, not as blocks.
priority: P1
status: proposed
originator: principal
```

```yaml
id: REQ-INT-F-002
title: "Every Reply Carries Its Communicative Function"
type: functional
description: >
  Every functional part of an agent's reply to the principal carries a
  typed communicative function (answer, question, report, refusal and
  so on) and a stable link to what it replies to, at the time it is
  sent.
rationale: >
  Without a type and a link, nobody can check afterwards whether a
  reply actually discharged the request.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  Sampled replies each carry a function type from the enumerated
  register and a resolvable link to the request they answer.
priority: P1
status: proposed
originator: principal
```

```yaml
id: REQ-INT-F-003
title: "Re-Issuing a Request Is Method, Not Symptom"
type: functional
description: >
  Sending the same request to several agents is a deliberate method of
  the principal's. Re-issue frequency is not treated as a sign that an
  agent failed.
rationale: >
  Scoring re-issues as failures would penalize the principal's own
  working style and mislead any effectiveness measure.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  No effectiveness measure counts repeated identical requests as a
  negative signal.
priority: P2
status: proposed
originator: principal
```

```yaml
id: REQ-INT-F-004
title: "Principal Experience Is the Purpose of Interaction Work"
type: functional
description: >
  Work on interaction quality is justified by the principal's
  experience of working with their agents. Request observability and
  reply typing serve that purpose; instrumentation for its own sake
  does not.
rationale: >
  Instrumentation without a purpose accumulates cost and produces
  numbers nobody acts on.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  Each interaction instrument names the principal-experience outcome it
  serves.
priority: P1
status: proposed
originator: principal
```

```yaml
id: REQ-INT-Q-001
title: "Scores Declare Their Assessor"
type: quality
category: Functional Suitability
description: >
  An interaction score declares who assessed each dimension. The agent
  derives the structural dimensions; the principal validates the
  experiential ones. No unqualified composite score is issued.
rationale: >
  A composite that mixes self-assessment with principal judgment hides
  which part anyone actually checked.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  Every published interaction score lists an assessor per dimension; no
  score is published as a single unattributed number.
priority: P1
status: proposed
originator: principal
```

```yaml
id: REQ-INT-Q-002
title: "Evidence Tiers Are Never Averaged"
type: quality
category: Functional Suitability
description: >
  Interaction scoring runs in two evidence tiers — strict, with stable
  reply links, and exploratory, without them — and the two are never
  averaged or otherwise combined.
rationale: >
  Averaging strong and weak evidence produces a number that looks
  strong and is not.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-09"
fit_criterion: >
  Every interaction report states its tier, and no reported figure
  combines both tiers.
priority: P1
status: proposed
originator: principal
```

---

## Routed to specifications

One ledger entry (the telemetry that defines the four request-observability fields) reads as a contract, not a requirement; it belongs in the interaction specification.
