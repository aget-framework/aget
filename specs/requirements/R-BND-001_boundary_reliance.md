# R-BND-001: Boundary & Reliance Requirements

**Version**: 1.0
**Date**: 2026-06-27
**Status**: Active
**Category**: Governance / Reliance
**Priority**: HIGH

---

## Purpose

Define how a **cross-boundary reliance** — anything a third party outside an AGET (a fleet supervisor, another AGET, or a downstream instance) must be able to depend on the AGET providing at a release — is governed.

**Problem Addressed**: An AGET legitimately authors most of its own internal requirements (autonomy under the availability constraint; healthy). But where something *outside* the agent must verify a dependency, agent-derived specs and template parity are not a contract — a downstream consumer cannot programmatically answer "is X guaranteed at this release?" (e.g. `#1748` — skill tiers unspecified and uncheckable; `#1286` — a {S}-parity gap; `#921` — conformance to a non-existent spec). A template is an *example*, not a contract.

**Scope**: Cross-boundary reliance requirements (framework→downstream, supervisor→agent, agent→agent). Per the ratified scope-widening (principal, 2026-06-24), the principal-owned / externally-verifiable carve also extends to other high-stakes classes the principal names — **governance-critical** and **irreversible-consequence** requirements. The exact enumeration of the widened set is **principal-refinable**; this spec governs the *contract shape*, not a fixed list.

---

## Requirements

### R-BND-001-01: Principal-Owned, Externally-Verifiable Contract (Ubiquitous)

**Statement**: WHERE a third party outside an AGET must depend on that AGET providing something at a release, the dependency SHALL be expressed as a **principal-owned, externally-verifiable requirement with a single source of truth** — NOT left to agent-derived specs or template parity.

**Rationale**: Verification of a boundary requirement happens *outside* the agent, so the agent cannot be the sole author and judge of it (the closed-loop limit). Ownership sits with the principal; the declaration must be readable by the external verifier.

**Verification**:
```bash
# A declared boundary requirement resolves to a single canonical, principal-owned source
test -f ../aget/specs/requirements/R-BND-001_boundary_reliance.md
```

**Implements**: GOAL-BOUNDARY-RELIANCE (principal-owned reliance; requirements are human-level)

---

### R-BND-001-02: Single Canonical, Version-Pinned Declaration (Ubiquitous)

**Statement**: A boundary requirement SHALL have exactly **one** canonical, **version-pinned** declaration that all verifiers read from. The SYSTEM shall NOT rely on embedded or duplicated copies as the contract.

**Rationale**: Multiple copies drift; a version-pin lets a consumer state precisely what it relied on at release R (the SemVer "social contract" made checkable).

**Verification**:
```bash
# The contract carries a release pin and there is one source of truth
grep -q 'as_of_version' .aget/skill_reliance_manifest.yaml   # first instance carries a release pin
```

**Implements**: SemVer 2.0.0 (social contract; core-vs-optional tiers)

---

### R-BND-001-03: Wake-Up Self-Attestation (Optional)

**Statement**: WHERE feasible, an AGET SHOULD be able to **self-attest** conformance to its boundary requirements at wake-up — not only via a supervisor-run tool.

**Rationale**: A downstream AGET should detect its own non-conformance without waiting for an external sweep; self-attestation closes the detection gap at the earliest point.

**Verification**:
```bash
# A conformance checker exists and is runnable by the agent itself
python3 scripts/check_skill_reliance_manifest.py --json >/dev/null 2>&1
```

**Implements**: detection-at-source; CAP-SESSION-001 (wake-up)

---

### R-BND-001-04: Meets-Declared-Minimum, Not Parity-to-Template (Ubiquitous)

**Statement**: Verification of a boundary requirement SHALL be **meets-declared-minimum**, NOT **parity-to-template**. A template SHALL NOT be treated as the contract.

**Rationale**: A template is an example/starting point; conformance means "provides at least the declared minimum," not "is byte-identical to a template" — which would both over-constrain (forbidding legitimate divergence) and under-specify (a stale template is not a guarantee).

**Verification**:
```bash
# Conformance is computed against the declared contract, not a template diff
grep -q 'meets-declared-minimum\|declared minimum' ../aget/specs/requirements/R-BND-001_boundary_reliance.md
```

**Implements**: template ≠ contract

---

### R-BND-001-05: Drift Is Detectable (State-Driven)

**Statement**: WHEN deployed reality diverges from the declared minimum, the divergence SHALL be **detectable** — drift is not silent.

**Rationale**: A contract no one can tell is broken is decorative. Drift between declared and deployed must surface as a detectable signal.

**Verification**:
```bash
# The conformance checker reports divergence (non-zero / WARN on under-coverage)
python3 scripts/check_skill_reliance_manifest.py 2>&1 | grep -qiE 'ERROR|WARN|coverage|missing' || true
```

**Implements**: classification without consequence; drift detection

---

## First Instance (the pilot, not the scope)

The **release-pinned skill-reliance manifest** ({S} core / {O} optional-AGET / {D} principal-domain tiers; `#1748`) is the **first worked example** of R-BND-001 — built as the pilot to establish the boundary-requirement pattern, not to solve skills in isolation. Grounding: FODA (Kang/SEI 1990) mandatory/optional/alternative; SemVer 2.0.0; Agent Skills open standard.

Other candidate boundary requirements (principal to triage, not agent-invented): required spec set, required governance fields, archetype capabilities.

---

## Assumption Log (Phase-4b Critic)

- **A-1**: The widened set (governance-critical / irreversible-consequence beyond cross-boundary) is principal-refinable — this spec governs the contract *shape*; the enumeration is an open, principal-owned question (not closed here).
- **A-2 (naming)**: "R-BND" (Boundary) and GOAL-BOUNDARY-RELIANCE are now narrower than the ratified scope (box-2 widening). A rename / goal-broadening is **flagged, not auto-applied** — both are governed artifacts requiring their own change.

---

## Traceability

| Sub-req | Evidence (L-doc) | Enforcement | Related |
|---------|------------------|-------------|---------|
| R-BND-001-01 | principal-owned, human-level | source-of-truth presence | GOAL-BOUNDARY-RELIANCE |
| R-BND-001-02 | SemVer 2.0.0 | `as_of_version` pin | #1748 manifest |
| R-BND-001-03 | CAP-SESSION-001 (wake-up) | wake-up checker | reliance manifest |
| R-BND-001-04 | template-is-example | declared-minimum check | AGET_TEMPLATE_SPEC (template = example) |
| R-BND-001-05 | drift detection | drift detection | reliance manifest validator |

**Ratification**: principal, 2026-06-24 (4 D1 boxes disposed individually). **Promoted to canonical**: 2026-06-27 (v3.24.0 release, `/aget-enhance-spec NEW`, #725). **Drafted from**: `aget/drafts/REQ-BOUNDARY-RELIANCE_draft.md` (private substrate).

---

*R-BND-001 v1.0 — "A boundary requirement is principal-owned, version-pinned, and verified meets-declared-minimum — never parity-to-template, never a silent drift."*
