# REQ-REL: Release Quality Requirements

**Version**: 1.3.0
**Date**: 2026-03-28
**Status**: proposed (wired to AGET_RELEASE_SPEC v1.11.0)
**Domain**: REL (Release Management)
**Format**: REQUIREMENTS_FORMAT v1.0 (requirements/REQUIREMENTS_FORMAT.md)
**Specifications**: AGET_RELEASE_SPEC.md, SOP_release_process.md, RUBRIC_release_handoff_quality_v1.0.md
**Tracking**: #725 (requirements formalization)

---

## Overview

Release quality defines how well the AGET framework delivers validated changes to downstream consumers (agents, fleets, community). These requirements are grounded in evidence from 8 releases (v3.3→v3.10), 2 hotfix cycles, and 10+ evolution documents.

The release process has matured from minimal conformance checks (v3.3) to 3-layer structural enforcement (v3.10), but regressions still occur at coordination boundaries (L711) and the stability commitment gap (L721) persists.

**Principal intent**: Releases should be predictable, high-quality, and immediately consumable by downstream agents without investigation or remediation.

---

## Functional Requirements

```yaml
id: REQ-REL-F-001
title: "Release Readiness Gate"
type: functional
description: >
  Every release should pass a readiness assessment before
  development begins, verifying that scope is consolidated,
  dependencies are met, and the release plan exists.
rationale: >
  100% post-release failure rate (v3.3-v3.9) traced to
  Gap B — the development-to-release-execution transition
  was ungoverned. Phase -1 prevents starting releases
  that aren't ready.
evidence:
  - L663 (Release Lifecycle — 30 phases, Gap B ungoverned)
  - v3.9.0 retrospective (4 human interventions)
  - L465 (Release Scope Consolidation Gap)
fit_criterion: >
  A blocking Phase -1 checklist (12+ items) executes before
  any release development. Checklist covers: consolidated
  VERSION_SCOPE, tracking issues referenced, success criteria
  defined, rollback plan documented.
priority: P0
specifications:
  - R-REL-025 (Release Readiness)
  - SOP Phase -1
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-002
title: "Handoff Completeness"
type: functional
description: >
  Every release should produce a handoff artifact that enables
  downstream consumers to upgrade without investigation —
  the handoff is an execution guide, not a notification.
rationale: >
  v3.10.0 handoff was missing 6 template sections and had no
  DEPLOYMENT_SPEC. Supervisor entered investigation mode,
  requiring HFX-001 remediation (242→376 lines).
evidence:
  - L711 (Coordination Pressure → Handoff Quality Regression)
  - HFX-001 (v3.10.0 handoff quality hotfix)
  - L587 (Author-Consumer Curse of Knowledge)
fit_criterion: >
  Handoff artifact contains all 14 template sections (verified
  by grep V-test returning 6+ required section headers).
  DEPLOYMENT_SPEC_vX.Y.Z.yaml exists. Score L2+ on
  RUBRIC_release_handoff_quality.
priority: P0
specifications:
  - R-REL-019 (Release-to-Fleet Handoff)
  - SOP Phase 5.3 (DEPLOYMENT_SPEC — BLOCKING)
  - SOP Phase 6.3 (Handoff Template Conformance V-test)
  - RUBRIC_release_handoff_quality_v1.0.md
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-003
title: "Stability Certification"
type: functional
description: >
  A release should be certified stable before announcement
  to external fleets. "Released and locally deployed" is
  not sufficient — stability requires evidence across
  validation, deployment, and parity dimensions.
rationale: >
  v3.10.0 required 2 hotfix cycles (HFX-001, HFX-002) between
  local deployment and remote announcement. Local supervisor
  became an unplanned canary.
evidence:
  - L721 (Stability Commitment Gap)
  - v3.10.0 timeline (released 03-21, stable 03-22)
  - STABILITY_CERTIFICATION_v3.10.0.md (first certification)
fit_criterion: >
  A STABILITY_CERTIFICATION artifact exists with three
  evidence classes all PASS: (a) validation — contract tests
  green, validators pass; (b) deployment — local fleet 100%,
  0 rollbacks, hotfixes closed; (c) parity — templates match
  fleet state.
priority: P0
specifications:
  - SOP Phase 7.4 (Stability Certification Gate)
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-004
title: "Template-Fleet Content Parity"
type: functional
description: >
  Content sync during releases should cover all artifact
  types — structural files, governance text, and skill
  instructions. Partial sync creates template-fleet gaps
  that break downstream upgrades.
rationale: >
  HFX-002: 12 public templates were missing D71 governance
  sections after v3.10.0 release because content sync only
  covered 5 file types, not SKILL.md files.
evidence:
  - L719 (Template-Fleet Inversion)
  - L714 (AGENTS.md Governance Text Gap)
  - HFX-002 (template-fleet gap hotfix)
  - L739 (Fleet Content Propagation Blind Spot)
fit_criterion: >
  Content sync manifest (SOP Phase -0.5) enumerates all
  artifact types including skill SKILL.md files.
  validate_content_sync.py structural check passes before
  release announcement.
priority: P1
specifications:
  - R-SYNC-002 (Content Sync)
  - SOP Phase -0.5 (Dual-Repo Sync)
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-005
title: "Post-Release Validation"
type: functional
description: >
  Every release should pass automated validation before
  the handoff phase. Contract tests, changelog existence,
  GitHub tags, and template parity should all be verified
  structurally, not manually.
rationale: >
  Post-release validation failure recurred across v3.6→v3.10
  (L727). SOP says BLOCKING but release plans accepted
  partial pass — the plan is operative, the SOP is
  aspirational. They must agree.
evidence:
  - L727 (Post-Release Validation Recurrence)
  - L553 (original v3.4.0 regression)
  - v3.8→v3.10 regression pattern (5 consecutive releases)
fit_criterion: >
  post_release_validation.py returns exit code 0 (100% pass,
  no partial). Contract tests 140/140. Validator covers:
  CHANGELOG per template, GitHub tags per repo, README badges,
  template parity.
priority: P1
specifications:
  - SOP Phase 4.3 (Post-Release Validation — BLOCKING)
  - R-REL-025-029
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-006
title: "Version Scope Pre-Release Audit"
type: functional
description: >
  Before release execution, the VERSION_SCOPE should be
  audited against actual implementation status — not issue
  tracker status. Pre-resolved items (~40%) should be
  identified and removed from estimates.
rationale: >
  Three consecutive releases (v3.8→v3.10) showed 40%
  pre-resolved probability (L611 calibration). Estimates
  that don't account for this waste 0.3-0.5x of budget.
evidence:
  - L611 (Pre-Resolved Item Calibration)
  - v3.8.0 (40% pre-resolved)
  - v3.9.0 (40% pre-resolved)
  - v3.10.0 (40% pre-resolved, 0.13x velocity)
fit_criterion: >
  VERSION_SCOPE has a pre-release audit column showing
  actual implementation status (not issue status).
  Items confirmed pre-resolved are marked and excluded
  from velocity estimates.
priority: P2
specifications:
  - SOP Phase 0 (Scope Initialization)
  - VERSION_SCOPE template
status: proposed
originator: operational-evidence
```

---

## Quality Requirements

```yaml
id: REQ-REL-Q-001
title: "Release Predictability"
type: quality
category: reliability
description: >
  Release velocity should be predictable within a
  calibrated range, enabling accurate session planning
  and principal scheduling.
rationale: >
  Velocity has improved from 0.27x (v3.9) to 0.13x (v3.10)
  but estimates remain inflated. Principal needs to know
  how long a release actually takes to allocate time.
evidence:
  - v3.8.0 (0.16x), v3.9.0 (0.27x), v3.10.0 (0.13x)
  - RELEASE_BRIDGE velocity profiles
fit_criterion: >
  Release velocity ratio falls within 0.10-0.25x of
  estimated time for releases with mature governance
  tooling. Estimate accuracy improves across consecutive
  releases.
priority: P2
specifications: []
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-Q-002
title: "Downstream Executability"
type: quality
category: interaction_capability
description: >
  Release artifacts should enable downstream consumers
  to upgrade autonomously — without asking the release
  author for clarification or performing investigation.
rationale: >
  L587 (author-consumer curse of knowledge): release authors
  know what changed but don't realize what consumers need.
  The handoff should transfer enough context for autonomous
  execution.
evidence:
  - L587 (Author-Consumer Curse of Knowledge)
  - L711 (Coordination Pressure Regression)
  - L724 (Specification-Level Guidance)
fit_criterion: >
  A downstream agent can complete upgrade using only the
  handoff artifact and DEPLOYMENT_SPEC — no session with
  the release author needed. Measured by: upgrade
  completion without clarification requests.
priority: P1
specifications:
  - RUBRIC_release_handoff_quality D4 (Downstream Executability)
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-Q-003
title: "Zero-Hotfix Release Target"
type: quality
category: functional_suitability
description: >
  Releases should ship without requiring post-release
  hotfix cycles. Hotfixes indicate quality gates failed
  to catch issues before announcement.
rationale: >
  v3.10.0 required 2 hotfix cycles (HFX-001, HFX-002)
  before remote announcement. Prior releases (v3.3-v3.9)
  had 0 hotfixes. The regression was caused by increased
  coordination complexity (multi-plan release).
evidence:
  - v3.10.0 (2 hotfixes — first release with hotfixes)
  - v3.3-v3.9 (0 hotfixes each)
  - L711 (Coordination Pressure → Quality Regression)
fit_criterion: >
  Release completes with 0 post-release hotfix cycles
  before stability certification. If hotfixes are needed,
  they are captured as regression evidence and the root
  cause addresses a quality gate gap.
priority: P2
specifications:
  - SOP Phase 7.4 (Stability Certification)
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-007
title: "Deployment Verification Tooling"
type: functional
description: >
  Every DEPLOYMENT_SPEC should include or reference an executable
  verification script that checks whether an agent is correctly
  deployed at the target version. The verification script is the
  enforcement mechanism for the state description.
rationale: >
  DEPLOYMENT_SPEC_v3.10.0 included verify_v3.10.0.sh (100+ lines,
  7 check categories). DEPLOYMENT_SPEC_v3.11.0 was created without
  one. The supervisor reached fleet migration G2 (pilot validation)
  without version-specific verification tooling, forcing ad hoc
  script adaptation.
evidence:
  - L754 (Deployment Verification Script Gap)
  - L671 (Classification Without Consequence — state without enforcement)
  - DEPLOYMENT_SPEC_v3.10.0 (has script, used in FLEET-UPG-008)
  - DEPLOYMENT_SPEC_v3.11.0 (missing script, caught during FLEET-UPG-009 prep)
fit_criterion: >
  DEPLOYMENT_SPEC_vX.Y.Z includes a verification_script section
  referencing an executable script. The script accepts --version
  and --path arguments and returns exit code 0 (pass) or 1 (fail).
  Running the script against a correctly deployed agent produces
  0 FAIL results.
priority: P1
specifications:
  - R-REL-038 (DEPLOYMENT_SPEC Required)
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-REL-F-008
title: "Remote Fleet Notification"
type: functional
description: >
  Every release should notify all known fleet supervisors,
  local and remote, within the release session. Remote
  supervisors who monitor the public repo passively may not
  discover releases for hours or days, leading to planning
  against wrong assumptions.
rationale: >
  v3.11.0 released 2026-03-28. Workco remote supervisor
  was still planning for "v3.11 likely theme: Ontology
  Coherence" 6+ hours later. No push notification exists
  for remote fleets, only pull (GitHub Release page).
evidence:
  - L723 (Remote Fleet Handoff Delivery Gap)
  - L747 (Event Awareness SLA)
  - L755 (Post-Release Premature Victory)
  - v3.11.0 remote supervisor unaware 6+ hours after release
fit_criterion: >
  REMOTE_MIGRATION_MESSAGE_vX.Y.Z.md created and delivered
  to all known remote fleet supervisors within the release
  session. Delivery confirmation recorded in pilot tracking.
priority: P1
specifications:
  - SOP Phase 7.3 (Remote Fleet Notification)
  - R-REL-019 (Release-to-Fleet Handoff)
status: proposed
originator: operational-evidence
```

---

## Constraints

| Constraint | Source | Description |
|------------|--------|-------------|
| Saturday push window | L735 | All public pushes on Saturday only |
| Semantic versioning | ADR-005 | MAJOR.MINOR.PATCH, gates = release points |
| 13-repo coordination | Architecture | aget/ core + 12 templates must be version-consistent |
| Private-first routing | L638 | Release issues filed to gmelli/aget-aget |
| No breaking changes without escalation | L42 | Breaking changes require principal approval |

---

## Traceability

| Requirement | Specification(s) | CAP-REL Coverage | Rubric Dimension |
|-------------|-------------------|-----------------|-----------------|
| REQ-REL-F-001 | R-REL-025, SOP Phase -1 | CAP-REL-001, CAP-REL-009, CAP-REL-012 | — |
| REQ-REL-F-002 | R-REL-019, SOP Phase 5.3/6.3 | CAP-REL-020, CAP-REL-007 | RUBRIC_release_handoff D1-D4 |
| REQ-REL-F-003 | SOP Phase 7.4 | CAP-REL-027, CAP-REL-016 | — |
| REQ-REL-F-004 | R-SYNC-002, SOP Phase -0.5 | CAP-REL-004, CAP-REL-024 | — |
| REQ-REL-F-005 | SOP Phase 4.3, R-REL-025-029 | CAP-REL-009, CAP-REL-021, CAP-REL-025 | — |
| REQ-REL-F-006 | SOP Phase 0, VERSION_SCOPE | CAP-REL-012, CAP-REL-013, CAP-REL-014 | — |
| REQ-REL-F-007 | R-REL-038, verify_deployment.py | R-REL-038 | — |
| REQ-REL-F-008 | SOP Phase 7.3, R-REL-019 | R-REL-019 | — |
| REQ-REL-Q-001 | RELEASE_BRIDGE velocity | CAP-REL-011 | — |
| REQ-REL-Q-002 | RUBRIC D4 | CAP-REL-020, CAP-REL-007 | RUBRIC_release_handoff D4 |
| REQ-REL-Q-003 | SOP Phase 7.4 | CAP-REL-009, CAP-REL-021—025 | — |

---

## Evidence Summary

| Release | Velocity | Hotfixes | Key Quality Issue | L-doc |
|---------|----------|----------|-------------------|-------|
| v3.7 | N/A | 0 | 4 skill renames, SOP gaps | L604 |
| v3.8 | 0.16x | 0 | Version drift, 40% pre-resolved | L650-L655 |
| v3.9 | 0.27x | 0 | 4 human interventions, behavioral gaps | L663, L674 |
| v3.10 | 0.13x | 2 | Handoff regression, template-fleet gap | L711, L721 |

---

*REQ-REL_release_quality_draft_v0.1.md*
*Published to aget/requirements/. First exemplar of REQUIREMENTS_FORMAT v1.0.*
*6 functional + 3 quality requirements, grounded in 8 releases of evidence.*
