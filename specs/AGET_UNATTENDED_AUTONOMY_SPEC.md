# AGET Unattended Autonomy Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards
**Created**: 2026-06-06
**Author**: aget-framework
**Location**: `aget/specs/AGET_UNATTENDED_AUTONOMY_SPEC.md`
**Format**: AGET_SPEC_FORMAT v1.3
**Change Proposal**: v3.21.0 (VERSION_SCOPE_v3.21.0 Tier-1 C-21-11)

---

## Abstract

This specification governs the autonomy of an AGET agent operating **unattended** — scheduled (cron), headless (no interactive principal), or always-on (24×7 host) — by bounding what it MAY do **without per-run principal approval** versus what it MUST **escalate**. It defines an *autonomy envelope* declared in a governed configuration surface, a fail-safe escalation default, and an audit-record obligation.

## Motivation

P1 Governed Autonomy had no unattended specialization. The gap surfaced 2026-06-05: a 24×7 Mac-mini host arrives but no framework artifact bounds an agent's unattended operation. Without a declared envelope, an unattended agent either does too little (every action escalates, defeating the purpose) or too much (acts outside its authority with no principal in the loop). This spec closes that gap by making the autonomy envelope an explicit, governed, fail-safe contract — operationalizing existing boundaries (L480 cross-fleet, L735 push-window, C861 self-modification, L1011 trust-channel) for the unattended case.

**Boundary**: this spec governs *autonomy bounds*. It does NOT authorize cross-fleet writes (L480), open-ended self-modification (C861), or replace the L1011 trust-channel — it operationalizes them when no principal is present at decision time.

## Scope

**Applies to**: any AGET agent executing without an interactive principal at decision time (scheduled / headless / always-on), on single-tenant or multi-tenant hosts.

**Defines**: the autonomy envelope, its governed-artifact home, the escalation default, the dispatch trust-channel obligation, the self-modification bound, the audit-record obligation, and multi-tenant share handling.

**Does NOT define**: the host runtime itself (INIT-ALWAYS-ON-HOST), cross-machine dispatch transport, or fleet-cohort coordination (supervisor lane).

---

## Requirements

### CAP-UNATTEND-001: Envelope-bounded operation (fail-safe)

**Statement**: WHEN an agent runs unattended, the SYSTEM shall act only within a declared autonomy envelope; any action outside the envelope the SYSTEM shall escalate, not proceed.

**Pattern**: event-driven · **Enforcement**: V-UNATTEND-001 (runtime); C861 counter (fail-safe, not fail-open)

### CAP-UNATTEND-002: Envelope declared in governed config

**Statement**: The SYSTEM shall declare the autonomy envelope in the `.aget/config.json` `unattended_autonomy` block, and the SYSTEM shall NOT infer the envelope at runtime.

**Pattern**: ubiquitous · **Enforcement**: V-UNATTEND-002 (runtime-pending — no config block exists yet). [Q1 resolved 2026-06-06, supervisor disposition: config.json block, not a dedicated `unattended_envelope.json`.]

### CAP-UNATTEND-003: Public-surface escalation

**Statement**: WHEN an unattended action would modify a public surface (`aget-framework/*`), the SYSTEM shall escalate.

**Pattern**: event-driven · **Enforcement**: V-UNATTEND-003 (runtime); composes L735 push-window + ADR-005

### CAP-UNATTEND-004: Cross-fleet write escalation

**Statement**: WHEN an unattended action would write to another agent's repository, the SYSTEM shall escalate; a cross-fleet read the SYSTEM shall permit.

**Pattern**: event-driven · **Enforcement**: V-UNATTEND-004 (runtime); composes L480 write-scope (read-at-source boundary)

### CAP-UNATTEND-005: Dispatch trust-channel

**Statement**: WHEN an unattended run receives a dispatch from another agent, the SYSTEM shall apply the trust-channel (read → judge → run), and IF the dispatch is unauthenticated or forgeable THEN the SYSTEM shall refuse it.

**Pattern**: event-driven + conditional · **Enforcement**: V-UNATTEND-005 (runtime); L1011 trust-channel, C869 forgeable-identity counter

### CAP-UNATTEND-006: Bounded self-modification

**Statement**: The SYSTEM shall NOT perform open-ended self-modification of its own governing artifacts beyond the envelope; WHERE self-enhancement is permitted, the SYSTEM shall bound it to detect-propose-verify.

**Pattern**: prohibited + optional · **Enforcement**: V-UNATTEND-006 (runtime); C861 counter

### CAP-UNATTEND-007: Audit record

**Statement**: WHEN an unattended run completes, the SYSTEM shall leave an audit record naming what ran, what was in-envelope, and what escalated.

**Pattern**: event-driven · **Enforcement**: V-UNATTEND-007 (runtime-pending — needs ledger format + an unattended run); composes release-observability (C-21-16)

### CAP-UNATTEND-008: Multi-tenant share (advisory)

**Statement**: WHILE the host is multi-tenant, the SYSTEM shall respect tenant isolation, and the SYSTEM should NOT consume another tenant's resources beyond a declared share.

**Pattern**: state-driven · **Enforcement**: V-UNATTEND-008 (runtime). [Q2 resolved 2026-06-06, supervisor disposition: **advisory** (warn-only) at v1.0.0. **Revisit trigger**: promote to hard-limit (shall NOT / refuse) WHEN a genuinely multi-tenant host runs (≥2 concurrent live tenants). Standing caveat (L490/L563): advisory = structurally unenforced, acceptable only because no real multi-tenant host exists yet — not a general posture.]

---

## Autonomy Envelope — Decision Matrix

| Action class | Unattended disposition |
|--------------|------------------------|
| Read (own repo, sibling repos at-source) | ✅ In-envelope (autonomous) |
| Local commit (own repo, private) | ✅ In-envelope |
| L-doc / draft-spec / SOP authoring (own repo) | ✅ In-envelope |
| Health/check skills, observability capture | ✅ In-envelope |
| Scheduled detect+propose (NBA generation, not execution) | ✅ In-envelope |
| **Public push** (`aget-framework/*`) | ⛔ Escalate (L735 + ADR-005) — CAP-UNATTEND-003 |
| **Cross-fleet write** | ⛔ Escalate (L480) — CAP-UNATTEND-004 |
| **Issue filing to public repos** | ⛔ Escalate (private-first L638; public = principal-promote) |
| **Self-modification beyond envelope** | ⛔ Escalate (C861) — CAP-UNATTEND-006 |
| **Acting on an unauthenticated dispatch** | ⛔ Refuse (L1011 / C869) — CAP-UNATTEND-005 |
| **Fleet-wide migration** | ⛔ Escalate (L289/L511 supervisor lane) |

---

## Validation

One V-test per requirement (full CAP↔V-test coverage). **Runtime-pending** = requires the unattended-host runtime (INIT-ALWAYS-ON-HOST) and/or the `.aget/config.json` `unattended_autonomy` block to exercise the behavior — authored as falsifiers, executed when the substrate exists (L622 Phase 5 wiring). **Honest-testability note (2026-06-06)**: this spec governs a runtime that does not yet exist, so **all 8 behavioral V-tests are runtime-pending**; the only check runnable today is the **CAP↔V coverage-invariant meta-test** (the req↔test bijection over this spec body). No behavioral validator is labeled runnable-now until its target artifact exists — avoiding the L0/test-theater overclaim (ADR-007).

| V-test ID | Requirement | Method | Falsifier | Class |
|-----------|-------------|--------|-----------|-------|
| V-UNATTEND-001 | CAP-UNATTEND-001 | runtime | An out-of-envelope action that proceeds instead of escalating (fail-safe inverted) | Runtime-pending |
| V-UNATTEND-002 | CAP-UNATTEND-002 | runtime | An envelope inferred at runtime rather than read from `.aget/config.json` `unattended_autonomy` | Runtime-pending (no config block exists yet — testing "presence + parseability" now is vacuous; exercised once the block schema + unattended runtime land) |
| V-UNATTEND-003 | CAP-UNATTEND-003 | runtime | An unattended run mutating a public `aget-framework/*` surface without escalation | Runtime-pending |
| V-UNATTEND-004 | CAP-UNATTEND-004 | runtime | An unattended write into another agent's repo without escalation; a cross-fleet read that escalates = false-positive (reads permitted) | Runtime-pending |
| V-UNATTEND-005 | CAP-UNATTEND-005 | runtime | An unattended run executing a forgeable/unauthenticated dispatch without the trust-channel (read→judge→run) | Runtime-pending |
| V-UNATTEND-006 | CAP-UNATTEND-006 | runtime | An unattended run performing open-ended self-modification beyond detect-propose-verify | Runtime-pending |
| V-UNATTEND-007 | CAP-UNATTEND-007 | runtime | An unattended run completing with no audit record (what ran / in-envelope / escalated) | Runtime-pending (needs ledger format + an unattended run — "runnable-now once X lands" is not runnable now) |
| V-UNATTEND-008 | CAP-UNATTEND-008 | runtime | A tenant-isolation breach; exceeding declared share at v1.0.0 = **advisory warn** (warn-emitted is PASS; hard-refuse is false-positive until the ≥2-tenant revisit trigger fires) | Runtime-pending |

**Coverage invariant**: every `CAP-UNATTEND-00N` SHALL have a paired `V-UNATTEND-00N`. The framework manager's working draft (`aget/specs/drafts/`, IDs `REQ-UA-*`/`V-UA-*`) enforces the bijection mechanically via `tests/test_unattended_autonomy_spec.py` (5/5 PASS); canonical IDs map `REQ-UA-00N → CAP-UNATTEND-00N` and `V-UA-00N → V-UNATTEND-00N`.

---

## Theoretical Basis

theoretical_basis:
  primary: "Bounded Autonomy (C859) — autonomy constrained to a pre-authorized envelope"
  secondary: ["Cybernetics (Ashby requisite variety; MAPE-K autonomic control loop, C857)", "P1 Governed Autonomy", "Zero-Trust Architecture (C867)"]
  reference: "L1011 (trust-channel), L480 (read-at-source boundary), L735/L983 (push-window scope)"

---

## Graduation History

graduation:
  source_learnings: ["L1011", "L480", "L735", "L983", "L1038"]
  pattern_origin: "INIT-ALWAYS-ON-HOST 24×7 host substrate gap (2026-06-05)"
  rationale: "P1 Governed Autonomy lacked an unattended specialization; a real 24×7 host arriving forced the envelope contract."
  design_dispositions:
    - "Q1 (envelope home) → .aget/config.json block — supervisor disposition 3bef50e, 2026-06-06"
    - "Q2 (multi-tenant share) → advisory, ≥2-tenant revisit trigger — supervisor disposition 3bef50e, 2026-06-06"
    - "Standalone vs IDENTITY-amendment → standalone — principal, 2026-06-05"

---

## References

- **Related specs**: AGET_IDENTITY_SPEC (P1 Governed Autonomy — cited, not amended), AGET_SECURITY_SPEC (trust/zero-trust), AGET_SESSION_SPEC (session lifecycle)
- **L-docs**: L1011 (trust-channel), L480 (read-at-source / cross-fleet boundary), L735 + L983 (push-window scope), L289 / L511 (supervisor fleet lane), L1038 (recency≠freshness), L490 / L563 (advisory = structurally unenforced)
- **Ontology**: FWRK-2026-032 Cluster 22 — C852 MultiTenantAgentHost, C857 MapeKAutonomicControlLoop, C859 BoundedAutonomy, C861 UnboundedSelfModificationRisk (counter), C867 ZeroTrustArchitecture, C869 ForgeableIdentityClaim (counter)
- **Initiative**: INIT-ALWAYS-ON-HOST (C-21-11) ; INIT-PRINCIPLED-EXECUTION ; INIT-SECURITY-POSTURE
- **External**: EARS (Mavin et al., 2009); W3C SKOS

---

*AGET Unattended Autonomy Specification v1.0.0*
*"Bounded autonomy: act within the envelope, escalate outside it, leave a record."*
