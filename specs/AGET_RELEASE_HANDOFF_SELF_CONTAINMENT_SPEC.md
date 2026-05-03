# AGET Release Handoff Self-Containment Specification

**Version**: 0.1.0
**Date**: 2026-05-03
**Status**: DRAFT
**Location**: `aget/specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md`
**Extends**: `AGET_RELEASE_SPEC.md` v1.17.0 (CAP-REL-020 Release Handoff Requirements)
**Format**: AGET_SPEC_FORMAT v1.3
**Hypothesis**: H-RHSC-001 (`PROJECT_PLAN_release_handoff_self_containment_spec_v1.0.md`)

---

## Purpose

Define **self-containment** as a testable property of `RELEASE_HANDOFF_v{X.Y.Z}.md`: the handoff SHALL be sufficient on its own — combined with public AGET repositories and the consuming agent's local SOPs — for a remote supervisor to complete migration **without dialog dependency** on the framework manager.

Parent CAP-REL-020 (R-REL-019) requires the handoff exists, includes "Context for External Fleets", and is sanitized. This spec adds the **invariants that make the handoff functionally self-sufficient** — converting an asserted property into a gated one.

---

## Motivation

Three observed failure classes drive this spec:

1. **Silent SOP staleness** (L910): a consumer reading the canonical public SOP at v1.32 while the authoring agent operates against a private SOP at v1.42–v1.43 has no signal that the runbook is stale.
2. **Recurring REMOTE_MIGRATION_MESSAGE confusion** (L901, revised): 4 of 15 historical releases produced the supplemental file; 3 of the 4 most recent did not. The variability framed as "orphan gap" was actually the absence of a self-containment definition — the artifact-presence question is the wrong question. The right question is whether the handoff alone suffices.
3. **Implicit cross-agent dependency**: handoff text occasionally implies dialog ("consult framework manager", "see private-*", "ask aget-framework"). Self-containment is presumed, not gated.

Empirical evidence that self-containment is achievable: v3.16 fleet upgrade reached 32/34 agents at v3.16.0 with 0 rollbacks using only `RELEASE_HANDOFF_v3.16.0.md` as the published artifact (no dialog with framework manager documented).

---

## Scope

### In Scope

- Testable invariants over `handoffs/RELEASE_HANDOFF_v{X.Y.Z}.md` content (8 CAPs, 11 sub-requirements)
- Validator script contract (`aget/verification/validate_handoff_self_containment.py`)
- BLOCKING V-test wiring point in `aget/sops/SOP_release_process.md` Phase 6.3

### Out of Scope

- Handoff existence (covered by R-REL-019-01)
- Handoff publication to public repo (covered by R-REL-019-07; PP-022 G3 is a coordination point)
- Skill-text canonical authority resolution (L919; INIT-SKILL-MATURATION territory)
- Generalized private/canonical SOP sync mechanism (this spec mandates parity for handoff-cited SOP versions only)
- Qualitative SHALLs from parent (R-REL-019-03, R-REL-019-04, R-REL-019-06) — deferred to v0.2 if backfill audit demonstrates need

---

## Vocabulary

```yaml
Self_Containment:
  skos:definition: "Property of a RELEASE_HANDOFF such that a remote supervisor can complete the described migration end-to-end using only the handoff, public AGET repositories, and the consuming agent's local SOPs"
  skos:related: ["Release_Handoff", "External_Fleet", "Dialog_Dependency"]
  skos:scopeNote: "Operationalized as 8 CAPs (CAP-RHSC-001..008) over handoff content. Empirical sufficiency demonstrated by v3.16 32/34 fleet PASS with zero documented dialog."

Dialog_Dependency:
  skos:definition: "A handoff condition requiring back-channel communication with the framework manager or another remote AGET to resolve ambiguity, fetch missing artifacts, or interpret instructions"
  skos:scopeNote: "Detected by lexical patterns: 'consult framework', 'ask aget-framework', 'see private-*', 'reach out to', 'contact <agent>'"
  skos:broader: "Anti_Pattern"

Sanitization_Invariant:
  skos:definition: "A content rule that the published handoff MUST satisfy to avoid leaking private-fleet information"
  skos:related: ["R-REL-019-07", "Private_First_Routing", "L638"]

SOP_Version_Parity:
  skos:definition: "Property that all SOP versions cited in the handoff match the canonical public SOP versions at publication time"
  skos:related: ["L910", "Canonical_vs_Private"]

Sleeping_Requirement:
  skos:definition: "A specification contract (CAP/R) that has landed in the spec but has no runtime implementation in the release"
  skos:related: ["L671", "L916", "Spec_Claimed_Delegate"]

Measurement_Substrate:
  skos:definition: "The validator or script used to score a release outcome (e.g., health_check.py for KR3, validate_archetype_skills.py for KR4). When the substrate is itself part of the release being measured, the measurement carries a self-reference caveat."
  skos:related: ["L917", "Substrate_Independence"]
```

---

## Requirements

### CAP-RHSC-001: Dialog Reference Prohibition

The handoff SHALL NOT contain text patterns that require the consuming agent to communicate with the framework manager or another remote AGET to complete migration.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-001-01 | ubiquitous | The handoff SHALL NOT contain the lexical patterns: `consult framework manager`, `ask aget-framework`, `ask the framework`, `see private-*-aget`, `reach out to`, `contact <agent>` (case-insensitive) | Self-containment requires no dialog channel; matches L644 supervisor-side observation that mid-action verification belongs at the propagator |

**Detection**: regex match against handoff body text.

---

### CAP-RHSC-002: Sanitization Invariants (extends R-REL-019-07)

The published handoff SHALL satisfy all four sanitization rules from parent R-REL-019-07. This CAP operationalizes the parent SHALL as testable invariants.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-002-01 | ubiquitous | The handoff SHALL NOT contain private agent names matching the pattern `private-*-aget` or `private-*-AGET` | Private-first routing (L638); prevents internal fleet leakage |
| R-RHSC-002-02 | ubiquitous | The handoff SHALL NOT contain private repository paths matching `~/github/private-*` or `gmelli/*` | Internal repo references are not resolvable by external consumers |
| R-RHSC-002-03 | ubiquitous | The handoff SHALL NOT contain fleet size disclosures matching `\d+ agents? in fleet` or `fleet of \d+` | Internal capacity is not external information |
| R-RHSC-002-04 | ubiquitous | The handoff SHALL NOT contain internal-only tracking tables (pilot commit hashes, internal session IDs `SESSION_\d{4}-\d{2}-\d{2}`, internal project IDs `FLEET-\w+-\d+`) | Tracking artifacts are internal-fleet-only |

**Detection**: regex matches against handoff body text.

---

### CAP-RHSC-003: SOP Version Parity (closes L910)

When the handoff cites a SOP version, the cited version SHALL match the canonical public SOP version at handoff publication time.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-003-01 | ubiquitous | For each `SOP_*.md vN.M` reference in the handoff, the cited version SHALL match the version at `aget/sops/SOP_*.md` at the time the handoff is committed | L910: silent SOP drift between private (~v1.43) and canonical (~v1.32) leaves remote consumers reading a stale runbook |

**Detection**: parse `SOP_<name>.md v<X.Y>` patterns from handoff; for each, read `aget/sops/SOP_<name>.md` header and compare versions.

---

### CAP-RHSC-004: Breaking Change Detection Commands

For every breaking change documented in the handoff, an executable detection command SHALL be provided that the remote can run locally.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-004-01 | conditional | IF the handoff documents a breaking change (BC-NNN reference) THEN the handoff SHALL include a code-fenced detection command (bash, python, or grep) the remote can execute locally to determine impact | Operationalizes ADR-022 + R-REL-007-03; remote cannot self-assess BC impact without an executable check |

**Detection**: for each BC-NNN reference in the handoff, verify a code fence is present within ±20 lines of the reference.

---

### CAP-RHSC-005: Per-Archetype Branch Explicitness

When the upgrade differs by archetype, each archetype SHALL receive its own enumerated branch — no "ask which path applies" deferrals.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-005-01 | conditional | IF the upgrade procedure differs across archetypes THEN the handoff SHALL enumerate each archetype branch explicitly (e.g., "For worker template: ...", "For supervisor template: ...") | Aligned with parent R-REL-019-05; closes implicit dialog where remote would otherwise ask "which path applies to me" |

**Detection**: presence of `For (worker|supervisor|advisor|analyst|architect|consultant|developer|executive|operator|researcher|reviewer|spec-engineer|document-processor)` enumerations in the Upgrade Guide section, OR explicit "no per-archetype variation" statement.

---

### CAP-RHSC-006: Sleeping Requirement Disclosure (closes L916)

Every spec contract that landed in the release without runtime implementation SHALL be disclosed in the handoff with consumer guidance.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-006-01 | conditional | IF the release ships any CAP/R-* with status `SPEC-LANDED` and no implementation THEN the handoff SHALL include a "Sleeping Requirements Disclosure" section listing each such CAP/R, its target implementation version, and consumer guidance ("do NOT treat as runtime-binding until ...") | L916 closure; v3.16 demonstrated this is currently author-discipline rather than gated; consumer must know which contracts are runtime vs paper |

**Detection**: presence of "Sleeping Requirements Disclosure" header section AND a table with columns (CAP/R, Status, Target version, Removal threshold).

---

### CAP-RHSC-007: Measurement-Substrate Caveat

When the release upgrades the validator that measures a Key Result, the handoff SHALL state the self-reference caveat.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-007-01 | conditional | IF the release modifies a script or spec referenced as the measurement substrate for any KR (e.g., `health_check.py`, `validate_archetype_skills.py`, `verify_deployment.py`) AND a KR result is reported using that substrate THEN the handoff SHALL state the substrate version used and the caveat ("KR{N} PASS as measured by `<script>` v{X.Y.Z}") | L917 / v3.16 KR4 caveat (gh#1213, gh#1211); without disclosure, consumer cannot evaluate measurement reliability |

**Detection**: for each KR with PASS/FAIL claim, presence of `as measured by <script>` or equivalent substrate-version reference if the script is modified in the release.

---

### CAP-RHSC-008: Deprecation Replacement Naming

Every deprecation in the handoff SHALL name the replacement, not defer to follow-up communication.

| ID | Pattern | Statement | Rationale |
|----|---------|-----------|-----------|
| R-RHSC-008-01 | conditional | IF the handoff documents a deprecation THEN the deprecation entry SHALL name the replacement explicitly (`<deprecated> → <replacement>` form) and SHALL NOT defer naming to "follow-up communication", "future notice", or "TBD" | Operationalizes R-DEP-010 #5 field for handoff layer; deferral re-introduces dialog dependency the spec is designed to eliminate |

**Detection**: parse Deprecations section; for each entry, verify `→` separator with non-empty target OR explicit "(no replacement; behavior removed)" disclosure.

---

## Verification Tests

| V-Test | CAP/R | Method | Description |
|--------|-------|--------|-------------|
| V-RHSC-001 | R-RHSC-001-01 | automated | Regex scan for dialog-reference patterns; expect 0 matches |
| V-RHSC-002 | R-RHSC-002-01 | automated | Regex scan for `private-*-aget`/`AGET`; expect 0 matches |
| V-RHSC-003 | R-RHSC-002-02 | automated | Regex scan for `gmelli/`/`~/github/private-`; expect 0 matches |
| V-RHSC-004 | R-RHSC-002-03 | automated | Regex scan for fleet size patterns; expect 0 matches |
| V-RHSC-005 | R-RHSC-002-04 | automated | Regex scan for internal session/project IDs; expect 0 matches |
| V-RHSC-006 | R-RHSC-003-01 | automated | For each `SOP_*.md vX.Y` reference, read canonical SOP header, compare versions; expect parity |
| V-RHSC-007 | R-RHSC-004-01 | automated | For each BC-NNN reference, find code fence within ±20 lines; expect 1+ |
| V-RHSC-008 | R-RHSC-005-01 | automated | Detect per-archetype enumerations OR "no per-archetype variation" statement; expect at least one form |
| V-RHSC-009 | R-RHSC-006-01 | automated | If release ships SPEC-LANDED CAPs (detected via release manifest), verify Sleeping Requirements Disclosure section + table present |
| V-RHSC-010 | R-RHSC-007-01 | automated | If release modifies measurement-substrate scripts (detected via git diff), verify KR claims include `as measured by` references |
| V-RHSC-011 | R-RHSC-008-01 | automated | For each Deprecations table row, verify `→` pattern with non-empty replacement OR explicit no-replacement disclosure |

---

## Consumer

### Validator Script

`aget/verification/validate_handoff_self_containment.py`:

- **Input**: `--handoff handoffs/RELEASE_HANDOFF_v{X.Y.Z}.md`
- **Optional flags**: `--release-manifest <path>` (for CAP-006/007 release-context detection); `--json` for SOP integration; `--strict` to FAIL on any UNKNOWN
- **Output (default)**: per-CAP / per-V-test PASS/FAIL with file:line evidence
- **Exit code**: 0 if all PASS, 1 if any FAIL, 2 if validator error
- **JSON schema** (when `--json`): `{"version": "0.1.0", "handoff": "<path>", "results": [{"cap": "CAP-RHSC-001", "v_test": "V-RHSC-001", "status": "PASS|FAIL|UNKNOWN", "evidence": "<file:line>"}, ...]}`

### SOP Wiring

`aget/sops/SOP_release_process.md` Phase 6.3 BLOCKING V-test:

```bash
python3 aget/verification/validate_handoff_self_containment.py \
  --handoff handoffs/RELEASE_HANDOFF_v${VERSION}.md \
  --release-manifest aget/DEPLOYMENT_SPEC_v${VERSION}.yaml
# Exit 0 = PASS, gate proceeds. Exit 1 = FAIL, gate blocked.
```

This V-test SUPERSEDES the v1.42 private-only `test -f handoffs/REMOTE_MIGRATION_MESSAGE_vX.Y.Z.md` check (L901 revised).

---

## Theoretical Basis

- **Extended Mind** (Clark & Chalmers, 1998): the published handoff IS the cognitive substrate the remote supervisor uses to extend its planning capability with framework-side knowledge. If the substrate is incomplete or requires dialog, cognition cannot complete.
- **Stigmergy** (Grassé, 1959): coordination via environment modification. The handoff is the shared environment artifact; self-containment is the variant of stigmergy where the environment alone suffices for the next agent's action.
- **Cybernetics — Requisite Variety** (Ashby, 1958): the handoff must contain sufficient variety to handle the migration's variety. Sleeping requirements (CAP-RHSC-006) and measurement-substrate caveats (CAP-RHSC-007) are explicit variety-disclosures preventing the consumer from making assumptions.

---

## Authority Model

This spec is owned by `private-aget-framework-AGET` (manager of public `aget-framework/`). Amendments to invariants follow standard spec amendment process per AGET_GOVERNANCE_HIERARCHY_SPEC.

---

## Inviolables

- Self-containment is a **content property of the published handoff** — NOT a property of any one supplemental document (REMOTE_MIGRATION_MESSAGE, SUPERVISOR_NOTIFICATION, etc.). This spec MUST NOT be misread as mandating any particular file.
- This spec extends, never replaces, parent CAP-REL-020 (R-REL-019). Parent SHALLs that are out of scope here remain binding.

---

## Traceability

| Link | Reference |
|------|-----------|
| Hypothesis | H-RHSC-001 (`PROJECT_PLAN_release_handoff_self_containment_spec_v1.0.md`) |
| Proposal | PP-022 (`planning/project-proposals/PROPOSAL_release_handoff_self_containment_spec.md`, Promoted 2026-05-03) |
| Initiative | INIT-FRAMEWORK-TRANSPARENCY (Stream 1 extension — handoff layer) |
| Parent spec | `AGET_RELEASE_SPEC v1.17.0` CAP-REL-020 (R-REL-019) |
| Format | `AGET_SPEC_FORMAT v1.3` |
| Related specs | `AGET_VOCABULARY_SPEC` (CAP-VOC-002 grounding); `AGET_ISSUE_GOVERNANCE_SPEC` (R-ISSUE-011..014 sanitization patterns) |
| L-docs | L901 (revised by this spec); L910 (CAP-RHSC-003 closure); L916 (CAP-RHSC-006 closure); L917 (CAP-RHSC-007 motivation); L919 (CAP-RHSC-003 secondary); L723, L755 (parent CAP-REL-020 prior art); L671 (parent anti-pattern); supervisor-L644 (CAP-RHSC-001 motivation, qualified per CAP-LDOC-010) |
| Predecessor work | H-RHSE-001 (COMPLETE 2026-02-15 — content sections); H-PRHR-001 (G4 COMPLETE / G5 reframed-as-coordination 2026-02-22 — publication discipline) |
| Issues | gmelli/aget-aget#1221 (template-spec drift surfaced during this spec's drafting) |
| Wiring SOP | `aget/sops/SOP_release_process.md` (v1.32 → planned v1.33 amendment, PP-022 G3) |
| Validator | `aget/verification/validate_handoff_self_containment.py` (PP-022 G2 deliverable) |

---

## Status Lifecycle

| Status | Meaning | Next |
|--------|---------|------|
| **DRAFT** | Spec authored, awaiting Auditor lens review + backfill audit | → REVIEWED |
| REVIEWED | Auditor lens executed; findings addressed | → ACTIVE |
| ACTIVE | Spec published; validator implemented; SOP wired | → SUPERSEDED (when v0.2 lands) |

**Current**: DRAFT (2026-05-03; Auditor self-review pending at PP-022 G1 close).

---

*AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v0.1 — DRAFT*
*Authored 2026-05-03 by private-aget-framework-AGET as Gate 1 deliverable of H-RHSC-001*
