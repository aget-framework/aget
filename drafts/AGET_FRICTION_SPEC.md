# AGET_FRICTION_SPEC

**Version**: 0.1.0
**Status**: DRAFT
**Created**: 2026-06-21
**Author**: private-aget-framework-AGET
**Governing Project**: PROJECT_PLAN_friction_pattern_canonicalization_v1.0 (PP-052)
**Serves Goal**: GOAL-FRICTION-CONVERGENCE
**Evidence basis**: L147 (it-consultant), L656 + L669 (supervisor, source-verified), L1111, L467

> **Forward-validation gate (L1113)**: this spec is `v0.1.0 / DRAFT` deliberately — it has N=1 dogfooded instrument (supervisor) and zero forward-validation across agents. The version label MUST NOT advance to 1.0.0 until the hook ships and ≥1 newly-scaffolded agent inherits capture (the H-FPC-001 test). Version-inflation is the L1113 anti-pattern.

---

## Purpose

Define the framework contract for **friction handling** — capturing, harvesting, remediating, and propagating the workflow-friction events agents experience — so that any AGET inherits friction recording by default rather than building it per-agent. The single most-developed friction instrument today is gitignored-runtime-only on one agent (capture = 1/36, source-verified); that is **non-propagating by construction (L1111)**. This spec is the propagation surface.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| The four friction capabilities (capture, harvest, remediate, propagate) | Fleet-wide friction corpus-merge (cross-agent aggregation — follow-on) |
| The per-agent recording contract | Fleet adoption coordination (supervisor lane, INIT-FLEET-LEARNING Stream B) |
| Template-shippability of the capture mechanism | Specific issue-tracker routing (governed by AGET_ISSUE_GOVERNANCE_SPEC) |

## Two-level framing (L742)

- **Requirement (human level)**: "friction the agent hits should resolve to structure, not silently recur."
- **Specification (contract level)**: the CAP-FRIC requirements below, each testable.

---

## Definitions

| Term | Definition |
|------|------------|
| **Friction event** | A workflow-friction occurrence (permission prompt, harness gate, tooling stall, repeated manual step) handed over via a friction marker. |
| **Friction marker** | A principal-typed prefix declaring a friction event (e.g., `note friction:`, `record friction:`). |
| **Structure-at-declaration** (L147) | Converting a remediation into durable structure (settings rule / guard / tracked script / spec) at the moment friction is declared. |
| **Owed-ledger entry** | An explicitly-recorded friction that is not yet remediated — a tracked debt, not a silent drop. |
| **Capture choke-point** (L669) | The capture+persistence boundary where a friction event is silently dropped if the marker is missed. |

---

## Capabilities

### CAP-FRIC-001 — Capture (structural, not attention-dependent)

- **CAP-FRIC-001-01**: The system SHALL capture a friction event the instant its marker is submitted, independent of whether the assistant remembers to transcribe it (structural per L656/L669).
- **CAP-FRIC-001-02**: Marker matching SHALL be **recall-biased** — a dropped capture is invisible (worst failure mode); an over-capture is cleaned cheaply at harvest. Marker matching SHALL tolerate verb variation (note/record/capture/log) and minor noun typos (L669 addendum).
- **CAP-FRIC-001-03**: The capture mechanism SHALL retain a verb prefix that prevents self-capture of quoted friction text (the over-count case).
- **CAP-FRIC-001-04**: The assistant SHALL remain the backstop — whether or not the automated capture fires, the friction SHALL land in the ledger (no regex catches arbitrary deviation).

**V-FRIC-001**: feed a `record friction: X` sample and a `note friction: X` sample → both append to the ledger; feed a quoted `"...friction:..."` with no verb → not captured. (executable smoke test)

### CAP-FRIC-002 — Persist (durable, harvestable ledger)

- **CAP-FRIC-002-01**: Captured events SHALL persist verbatim to a durable, harvestable ledger with a status field ∈ {new, filed #N, wontfix, dedup #N}.
- **CAP-FRIC-002-02**: The ledger SHALL be greppable by status (`status: new`) anchored to the entry heading (a bare grep over-counts).

**V-FRIC-002**: `grep -cE '^## FRICTION .*status: new' <ledger>` returns the unhandled count.

### CAP-FRIC-003 — Harvest (analyze → cluster → dedup)

- **CAP-FRIC-003-01**: Harvest SHALL cluster `status: new` entries by root cause and rank by leverage (frequency × reach × unmitigated-share × within-reach) per L656.
- **CAP-FRIC-003-02**: Harvest SHALL dedup against open issues **before** filing — dedup is non-optional even for high-recurrence findings (recurrence proves salience, not absence-of-issue; L669).

**V-FRIC-003**: a harvest run on a ledger whose sole entry duplicates an open issue SHALL produce 0 new filings and mark the entry `dedup #N`.

### CAP-FRIC-004 — Remediate (structure-at-declaration | owed)

- **CAP-FRIC-004-01**: A harvested friction SHALL resolve to either (a) structure-at-declaration (settings rule / guard / tracked script / spec) OR (b) an explicitly-owed ledger entry. Advisory-only mitigation is PROHIBITED as a terminal state (it is structural recurrence, L656/L490/L563).
- **CAP-FRIC-004-02**: When the remediation is in-reach and in the agent's own write-scope, fixing at source SHALL be preferred over filing.

**V-FRIC-004**: no `status: new` entry remains after harvest without either a structure artifact reference or an `owed` marker.

### CAP-FRIC-005 — Propagate (template-shippable, NOT gitignored)

- **CAP-FRIC-005-01**: The capture mechanism SHALL be **template-shippable** — it SHALL NOT be gitignored-runtime-only. (This is the L1111 root fix: a structural fix in a non-propagating location is single-agent, not fleet.)
- **CAP-FRIC-005-02**: Propagation SHALL use ≥2 channels (template + spec; AGENTS.md row where applicable) per L467 (single-point docs = discovery lottery).
- **CAP-FRIC-005-03**: Enforcement SHALL degrade gracefully off-Claude harnesses (governance ports, enforcement degrades to advisory; L1104/L474–476).

**V-FRIC-005**: `git check-ignore <hook-path>` returns empty (the hook is tracked, not ignored); the hook is present in ≥1 template.

---

## Requirements traceability

| CAP | Requirement (human level, L742) | Evidence |
|-----|----------------------------------|----------|
| CAP-FRIC-001 | friction never silently dropped | L669 (capture choke-point) |
| CAP-FRIC-002 | friction is durable + auditable | L669 |
| CAP-FRIC-003 | friction analyzed by leverage, deduped | L656 |
| CAP-FRIC-004 | friction becomes structure, not recurrence | L147 |
| CAP-FRIC-005 | friction handling reaches every agent | L1111, L467, L1104 |

## Theoretical basis (L332)

- **Stigmergy** (Grasse): the ledger is the shared trace coordinating remediation across sessions.
- **Poka-yoke** (Shingo): structural capture is mandatory friction-proofing at the error-prone step.
- **Cybernetics**: CAP-FRIC-004's loop (trigger → review → consequence) is the regulating feedback that prevents recurrence.

## Open questions

- OQ-1: Where does the cross-agent corpus-merge live (fleet aggregation) — supervisor lane or a new fleet artifact? (follow-on; out of scope here)
- OQ-2: Does CAP-FRIC-005-03 need a conformance test per harness, or is one advisory-degradation statement sufficient? (gate at canonical promotion)

---

*AGET_FRICTION_SPEC v0.1.0 DRAFT — "Friction becomes structure, or it becomes an owed debt. Never a silent drop."*
