# REQ-IAC: Inter-Agent Communication

**Version**: 0.1.0
**Date**: 2026-09-26 (created from the principal's requirements ledger)
**Status**: proposed
**Domain**: IAC (Inter-Agent Communication)
**Format**: REQUIREMENTS_FORMAT v1.1
**Inherits from**: REQ-CORE_critical_foundations.md (cross-cutting foundations)

---

## Overview

How agents exchange requests and findings with each other without corrupting what they measure or losing messages that have nowhere to go.

These requirements were ruled by the principal between July and September 2026 and held only in a private ledger until this refresh (framework openness rulings, 2026-09-26). Names of private agents, hosts and internal identifiers are stripped; each states the general principle. Across the whole ledger (not per file), three further entries read as contract-level and are routed to specifications instead of this layer.

---

## Requirements

```yaml
id: REQ-IAC-F-001
title: "A Request Never Shows the Receiver What It Measures"
type: functional
description: >
  A request one agent sends another does not expose the sender's
  prediction, expected behavior, suspected mechanism, confidence,
  falsifiers or scoring rubric to the agent being measured.
rationale: >
  A receiver that can see what it is scored on can perform to the
  score, which destroys the measurement.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-23"
fit_criterion: >
  A check over outbound request cards finds none of the listed
  sender-side fields in the receiver-visible payload.
priority: P1
status: proposed
originator: principal
```

```yaml
id: REQ-IAC-F-002
title: "A Proposed Message Names Its Route"
type: functional
description: >
  When an agent proposes to send guidance, a finding or a request to
  another agent, the proposal names the existing route it will travel,
  or states plainly that no route exists.
rationale: >
  A proposal with no route looks actionable and silently goes nowhere.
evidence:
  - "Principal ruling, recorded in the framework's requirements ledger, 2026-08-29 (ruled for one agent; proposed framework-wide)"
fit_criterion: >
  Every sampled cross-agent proposal names a route or states that none
  exists.
priority: P2
status: proposed
originator: principal
```

---

## Routed to specifications

Two ledger entries (freshness of dispatch requests against received state; custody binding in review-packet verifiers) read as contracts, not requirements; they belong in the inter-agent communication specification.
