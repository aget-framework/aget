# RELEASE_HANDOFF: v3.9.0

**Version**: 3.9.0
**Released**: 2026-03-15
**Theme**: Governance Enforcement
**Breaking Changes**: None
**Framework Manager**: private-aget-framework-AGET
**Status**: READY

---

## Receiving Agent Governance Checklist (BLOCKING)

**STOP**: Before executing any upgrade steps, complete this checklist:

- [ ] Located local upgrade SOP (e.g., SOP_point_upgrade.md)
- [ ] Created PROJECT_PLAN for this upgrade OR referenced existing gate
- [ ] Gate discipline acknowledged (L42)
- [ ] Principal approval obtained if required by local governance

**Governance Reference**: _[Your upgrade SOP path]_

**Warning**: Proceeding without completing this checklist is a governance violation (L562).

---

## Executive Summary

v3.9.0 is a governance enforcement release addressing two systemic issues discovered through the Release Lifecycle Model research (L663): **100% post-release failure rate** across 8 releases and **version-bearing drift** in every release. Both trace to ungoverned transitions between development and release execution.

Key additions: Phase -1 (Release Readiness) governs the highest failure density zone, version_bump.py covers all 5 artifact types with BLOCKING validation, Gate 0 (Spec Verification) is codified in the project plan template, and Phase 0.85 (Deliverable Conformance Check) is standard release process. No breaking changes.

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| Phase -1: Release Readiness (SOP) | Framework — 3 sub-phases (B.1/B.2/B.3), 12-item checklist | No agent action — SOP governance |
| Phase 0.85: Deliverable Conformance (SOP) | Framework — SHALL violations BLOCKING | No agent action — SOP governance |
| Gate 0: Spec Verification (TEMPLATE_PROJECT_PLAN) | All agents — mandatory spec verification before implementation | Use updated template for new PROJECT_PLANs |
| GOVERNANCE_PRINCIPLES.md (public) | Framework — first publication of meta-principles | No action — governance reference document |
| release-notes/v3.9.0.md | Framework — deep release notes | No action — reference document |

### Changed

| Change | Migration |
|--------|-----------|
| version_bump.py: 2/5 → 5/5 artifact types | Auto-propagated via template sync (covers AGENTS.md, codemeta.json, CITATION.cff) |
| version_bump.py: `--check VERSION` mode | Use `--check 3.9.0` to validate all 27 files |
| SOP_release_process.md: Phase -1, Phase 0.85 | Auto-propagated |
| TEMPLATE_PROJECT_PLAN.md: Gate 0 mandatory | Auto-propagated |

### Fixed

| Fix | Impact |
|-----|--------|
| aget-enhance-spec: Phase 6 added to all categories (#418) | Phase Selection table now consistent with C3 constraint |
| aget-enhance-spec: AGET_SKILLS_SPEC → SKILL_NAMING_CONVENTION_SPEC (#419) | Phantom reference removed |

### Breaking Changes

None. v3.9.0 is fully backward compatible with v3.8.x.

---

## Upgrade Checklist

### Per Agent

1. **Run pre-sync check** (detect skill customizations before overwriting):
   ```bash
   python3 .aget/patterns/upgrade/pre_sync_check.py \
     --baseline ~/path/to/template-{archetype}-aget/.claude/skills/ \
     --instance .claude/skills/
   ```

2. **Update `.aget/version.json`**:
   ```json
   {
     "aget_version": "3.9.0",
     "updated": "2026-03-15"
   }
   ```
   Add migration_history entry:
   ```
   "v3.8.0 -> v3.9.0: 2026-03-15 (Governance Enforcement - release readiness, version management, process standardization)"
   ```

3. **Update `AGENTS.md` header**:
   ```markdown
   @aget-version: 3.9.0
   ```

4. **Sync updated scripts** (version_bump.py enhancement):
   ```bash
   # Copy from template (after pre_sync_check confirms safe)
   cp ~/path/to/template-{archetype}-aget/scripts/version_bump.py scripts/
   ```

5. **Validate**:
   ```bash
   python3 scripts/wake_up.py
   # Expected: Shows v3.9.0
   ```

### Fleet-Wide

- [ ] Wave 0: Supervisor first (validate new SOP governance)
- [ ] Wave 1: 2-3 simple agents (test version_bump.py --check)
- [ ] Wave 2: Remaining agents
- [ ] Verify: All agents at v3.9.0

---

## Context for External Fleets

> **Per R-REL-019-02**: This section explains concepts that may not be obvious to fleets outside the managing organization.

### What is Phase -1 (Release Readiness)?

A new SOP phase inserted before release execution begins. Based on Release Lifecycle Model research (L663) that identified 100% post-release failure rate across 8 releases — all failures traced to the ungoverned transition between development and release execution (Gap B).

**3 sub-phases**:
- **B.1 Release Readiness Assessment**: V-test completion, deliverable status, dependency resolution
- **B.2 Deliverable Conformance Audit**: SHALL/SHOULD verification against governing specs
- **B.3 Principal Release Approval**: Explicit GO decision with scope summary

**Impact on agents**: Agents using PROJECT_PLAN patterns for releases should adopt Phase -1 in their own release SOPs.

### What is Gate 0 (Spec Verification)?

A mandatory first gate in the PROJECT_PLAN template that verifies governing specs exist for all deliverables before implementation begins. Implements meta-principle MP-1 (Spec-First).

**Key insight from v3.9.0 development**: ~40% of VERSION_SCOPE items were already implemented (L611 pattern). Gate 0 catches these before they consume planning capacity.

### What is version_bump.py --check?

A BLOCKING validation mode that verifies all 27 version-bearing files across 13 repos match the target version. Returns exit code 1 on any mismatch.

**5 artifact types** (was 2):
- `.aget/version.json` (all repos)
- `README.md` (12 templates)
- `AGENTS.md @aget-version` (12 templates) — **NEW**
- `codemeta.json` (core only) — **NEW**
- `CITATION.cff` (core only) — **NEW**

### Archetype Reference

| Archetype | v3.9.0-Specific Changes | Action |
|-----------|------------------------|--------|
| All archetypes | version_bump.py enhanced, TEMPLATE_PROJECT_PLAN updated, aget-enhance-spec fixed | Sync scripts/version_bump.py + merge template changes |

---

## Critical Mitigations

### L663: Release Lifecycle Model

**The problem**: 30 phases, 5 macro-phases, 3 gap zones. Gap B (Development → Release Execution) had 12 combined failures, 0 SOP pages. 100% post-release failure rate across 8 releases.

**The fix**: Phase -1 (Release Readiness) provides the "on-ramp" to release execution.

**Key quote**: "Governing the middle while leaving transitions ungoverned is like a bridge with strong spans but no on-ramps."

### L611: Stale VERSION_SCOPE Classifications

**The problem**: VERSION_SCOPE items classified as "open" may already be implemented. Manual verification before scoping prevents wasted effort.

**The fix**: Gate 0 includes L611 check — verify against actual files, not just issue tracker status.

---

## v3.8.0 Observation Status

| # | v3.8.0 Observation | v3.9.0 Status |
|---|-------------------|---------------|
| 1 | AGENTS.md version not in version_bump.py | **Resolved** — version_bump.py now covers AGENTS.md (D64) |
| 2 | codemeta.json/CITATION.cff version not in version_bump.py | **Resolved** — version_bump.py now covers both (D64) |
| 3 | No pre-release conformance check | **Resolved** — Phase 0.85 added to SOP (D40) |
| 4 | No spec verification gate in project plans | **Resolved** — Gate 0 added to TEMPLATE_PROJECT_PLAN (D39) |

---

## Pilot Tracking

| Fleet | Supervisor | Agents | Status | Date | Notes |
|-------|-----------|--------|--------|------|-------|
| main | private-supervisor-AGET | 32/32 | COMPLETE | 2026-03-14 | 1 SKIP (framework-AGET self-managed). 0 rollbacks, 0 failures. L583 filed, #438 filed. |
| legalon | private-legalon-supervisor-AGET | 0/8 | PENDING | — | — |

**Total**: 32/40 agents at v3.9.0.

---

## Smoke Test Checklist

1. [ ] `wake_up.py` shows v3.9.0
2. [ ] `sanity_check.py` passes 9/9
3. [ ] AGENTS.md shows `@aget-version: 3.9.0`
4. [ ] `version_bump.py --check 3.9.0` returns exit 0
5. [ ] Conformance report shows CONFORMANT at deep depth

---

## Post-Release Validation Results

| Check | Result | Notes |
|-------|--------|-------|
| GitHub Release (13 repos) | PASS | All 13 repos released with "Latest" badge |
| Tags (13 repos) | PASS | All repos tagged v3.9.0 |
| Version consistency (27 files) | PASS | `--check 3.9.0` exit 0 |
| README badges (12 templates) | PASS | All show v3.9.0 |
| Homepage | PASS | Updated to v3.9.0 (Current) |
| CHANGELOG entries | PASS | All 13 repos have v3.9.0 entries |
| Post-release validation | 14/15 | Handoff was the 1 remaining item (this document) |

---

## References

- [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) - Full v3.9.0 changes
- [release-notes/v3.9.0.md](https://github.com/aget-framework/aget/blob/main/release-notes/v3.9.0.md) - Deep release notes
- [UPGRADING.md](https://github.com/aget-framework/aget/blob/main/docs/UPGRADING.md) - Migration procedures
- [SOP_fleet_migration.md](https://github.com/aget-framework/aget/blob/main/sops/SOP_fleet_migration.md) - Fleet coordination

---

## Handoff Protocol

**From**: private-aget-framework-AGET
**To**: private-supervisor-AGET
**Date**: 2026-03-15

### Acknowledgment

- [x] Governance Checklist completed
- [x] Acknowledged by: private-supervisor-AGET (FLEET-UPG-006)
- [x] Date: 2026-03-14
- [ ] Fleet broadcast sent: ___
- [x] Main fleet: 32/32 at v3.9.0 (2026-03-14)
- [ ] Remote fleet: 0/8 (pending)

---

*RELEASE_HANDOFF_v3.9.0.md*
*Generated: 2026-03-15*
*Per L511/R-REL-019*
