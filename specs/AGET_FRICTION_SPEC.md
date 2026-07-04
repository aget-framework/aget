# AGET_FRICTION_SPEC

**Version**: 1.0.0
**Status**: Active (canonical promotion 2026-07-04, v3.25 C-25-22; graduated from private draft v0.2.0)
**Created**: 2026-06-21
**Updated**: 2026-06-24 (v0.2.0 — added CAP-FRIC-006 Triage-by-value; closes gmelli/aget-aget#1747)
**Author**: private-aget-framework-AGET
**Governing Project**: PROJECT_PLAN_friction_pattern_canonicalization_v1.0 (PP-052)
**Serves Goal**: GOAL-FRICTION-CONVERGENCE
**Evidence basis**: L147 (it-consultant), L656 + L669 (supervisor, source-verified), L1111, L467, L1127 (triage-not-elimination; preserve-pole)

> **Forward-validation gate (L1113) — SATISFIED 2026-07-04**: the 1.0.0 label was withheld until the hook shipped and a non-author agent inherited capture. Evidence: **H-FPC-001b PASS** (gmelli/aget-aget#1747 — supervisor non-author run: INHERIT PASS, SELFTEST PASS, CAPTURE PASS via the stdin contract), re-confirmed locally at promotion (trio PASS 2026-07-04). Value-class placement per the validator caveat: the capture surface stamps `value-class: owed` (the CAP-FRIC-006-04 ambiguity fail-safe) at emit; triage refines at harvest — capture never pre-classifies `avoidable`.

---

## Purpose

Define the framework contract for **friction handling** — capturing, harvesting, remediating, and propagating the workflow-friction events agents experience — so that any AGET inherits friction recording by default rather than building it per-agent. The single most-developed friction instrument today is gitignored-runtime-only on one agent (capture = 1/36, source-verified); that is **non-propagating by construction (L1111)**. This spec is the propagation surface.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| The friction capabilities (capture, persist, harvest, **triage**, remediate, propagate) | Fleet-wide friction corpus-merge (cross-agent aggregation — follow-on) |
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
| **Friction value-class** (L1127) | The triage classification of a captured friction by its value: **avoidable** (extraneous workflow friction — eligible for remediation), **structural-healthy** (a deliberate compensating control / Healthy Friction — to be PRESERVED and calibrated, not removed; ontology `aget:concept/HealthyFriction` C1066), or **owed** (deferred, tracked). |
| **Triage-by-value** (L1127) | Classifying a captured friction into a value-class *before* remediation applies — the "classify-before-reduce" hinge (ontology `aget:concept/FrictionTriage` C1069). |

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

### CAP-FRIC-006 — Triage (classify by value before remediate)

> **Pipeline position**: CAP-FRIC-006 logically precedes CAP-FRIC-004; it is numbered 006 to preserve existing CAP-FRIC-004/005 references. Order: capture(001) → persist(002) → harvest(003) → **triage(006)** → remediate(004) → propagate(005).

**Why** (L1127): friction reduction is a *triage* problem, not an *elimination* problem. AGET deliberately installs **healthy friction** — compensating controls such as authority-expanding edit prompts, the public-push window (L735), and STRUCTURAL skill routing (D71). A remediation contract that treats *all* captured friction as avoidable would route these toward removal, making the friction-handling mechanism an **erosion vector** for the controls it should protect. Triage is the gate that prevents this (closes gmelli/aget-aget#1747).

- **CAP-FRIC-006-01**: Before CAP-FRIC-004 remediation applies, every harvested friction SHALL be classified by **value-class** ∈ {avoidable, structural-healthy, owed}. (Mirrors the close-session 3-way classification, CAP-SESSION-013-D / R-CLOSE-018.)
- **CAP-FRIC-006-02**: A friction classified **structural-healthy** SHALL NOT be routed to CAP-FRIC-004 remediation-to-removal. Its only valid responses are **calibration** (adjust the control's threshold) or **affirmation** (record why it is kept). Treating a structural-healthy event as remediation-debt is PROHIBITED.
- **CAP-FRIC-006-03**: Any capture/reporting surface (skill, hook, or marker) that emits to the ledger SHALL carry the value-class forward. A surface that routes captured friction toward remediation WITHOUT a triage step is **non-conformant** (the *Friction-Reporting Front-Door Anti-Pattern*, ontology `aget:concept/FrictionReportingFrontDoorAntiPattern` C1072).
- **CAP-FRIC-006-04** (ambiguity fail-safe): WHEN the value-class is ambiguous, classification SHALL default to **owed** (tracked, not auto-remediated) — never to **avoidable** (which would route a possibly-healthy friction toward removal).

**V-FRIC-006**: a ledger entry classified `structural-healthy` that is routed to a CAP-FRIC-004 removal-remediation is a conformance failure; a capture surface that emits a ledger entry with no value-class field fails CAP-FRIC-006-03; an ambiguous entry that defaults to anything other than `owed` fails CAP-FRIC-006-04.

### CAP-FRIC-004 — Remediate (structure-at-declaration | owed)

- **CAP-FRIC-004-01**: Following triage (CAP-FRIC-006), a friction classified **avoidable** SHALL resolve to either (a) structure-at-declaration (settings rule / guard / tracked script / spec) OR (b) an explicitly-owed ledger entry. Advisory-only mitigation is PROHIBITED as a terminal state (it is structural recurrence, L656/L490/L563). A friction classified **structural-healthy** is out of CAP-FRIC-004 scope per CAP-FRIC-006-02.
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
| CAP-FRIC-006 | healthy friction is preserved, not eliminated — classify before reduce | L1127, Healthy Friction (GOVERNANCE_PRINCIPLES.md), R-CLOSE-018 |
| CAP-FRIC-004 | friction becomes structure, not recurrence (for *avoidable* friction) | L147 |
| CAP-FRIC-005 | friction handling reaches every agent | L1111, L467, L1104 |

## Theoretical basis (L332)

- **Stigmergy** (Grasse; ontology `aget:concept/Stigmergy` C031): the ledger is the shared trace coordinating remediation across sessions.
- **Poka-yoke** (Shingo): structural capture is mandatory friction-proofing at the error-prone step; CAP-FRIC-006's structural-healthy class IS poka-yoke friction — to be preserved, not removed.
- **Desirable difficulties** (Bjork & Bjork 2011): the cognitive-science grounding for the structural-healthy class — effortful steps that build durable capability ("which friction is *the way*"). Triage (CAP-FRIC-006) is the discipline of telling that friction apart from friction that is merely *in the way*.
- **Cybernetics**: CAP-FRIC-004's loop (trigger → review → consequence) is the regulating feedback that prevents recurrence.

## Open questions

- OQ-1: Where does the cross-agent corpus-merge live (fleet aggregation) — supervisor lane or a new fleet artifact? (follow-on; out of scope here)
- OQ-2: Does CAP-FRIC-005-03 need a conformance test per harness, or is one advisory-degradation statement sufficient? (gate at canonical promotion)
- OQ-3: Should the value-class set {avoidable, structural-healthy, owed} (CAP-FRIC-006-01) be a fixed enum or a config-extensible list? Held fixed for v0.x to match R-CLOSE-018; revisit at canonical promotion. **RESOLVED at promotion 2026-07-04: fixed enum retained** — R-CLOSE-018 parity outweighs config-extensibility; extending the enum re-opens the front-door anti-pattern (C1072) surface. Revisit only on cross-fleet evidence of a missing class.

---

## Version history

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-06-21 | Initial DRAFT — CAP-FRIC-001..005 (capture / persist / harvest / remediate / propagate). PP-052 Gate 1. |
| 0.2.0 | 2026-06-24 | Added **CAP-FRIC-006 Triage-by-value** (+ value-class / triage-by-value definitions, V-FRIC-006, traceability row, desirable-difficulties theoretical basis); amended CAP-FRIC-004-01 to gate on `avoidable` class. Closes gmelli/aget-aget#1747. Still DRAFT per L1113 forward-validation gate (no version advance to 1.0.0 until hook ships + ≥1 agent inherits capture). |

*AGET_FRICTION_SPEC v0.2.0 DRAFT — "Friction becomes structure, or an owed debt, or — if it is the way — it is kept. Never a silent drop, never a blind removal."*
