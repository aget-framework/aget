# RELEASE_HANDOFF: v3.21.0

**Released**: 2026-06-06
**Theme**: Always-On Fleet Operations (governance-scoped)
**Upgrade type**: version-bump only (no breaking changes)

---

## Executive Summary

v3.21.0 is a **net governance-inflow** release: it ships the bounding rules for unattended/always-on agent operation **before** the runtime that consumes them (artifact-now / operations-later — the 24×7 host, cross-machine dispatch, and fleet-cohort runtime are deferred to the next minor). The release also lands a read-only initiative portfolio rollup and promotes `/aget-create-initiative` to STRICT canonical core (closing its verb-pair gap with `/aget-propose-initiative`). Existing instances upgrade by version-bump only.

## Context for External Fleets

> **Per R-REL-019-02**: explains concepts that may not be obvious to fleets outside the managing organization.

### What is `AGET_UNATTENDED_AUTONOMY_SPEC`?

A governance contract for agents that run **without a human in the loop** (scheduled jobs, always-on hosts, headless dispatch).

- **Problem it solves**: an unattended agent needs explicit, testable boundaries on what it may decide alone versus what it must pause and escalate — otherwise "autonomy" silently widens at the worst time.
- **What it does**: 8 EARS requirements (`CAP-UNATTEND-001..008`) draw that line. It is *specification only* — no runtime ships this release.
- **Deploy to**: any agent you intend to run unattended. If all your agents are interactive, this is informational; copy the spec but skip the config envelope.

### What is `check_initiatives.py`?

A read-only portfolio rollup over an agent's `planning/initiatives/INIT-*.md` files.

- **Problem it solves**: long-running initiatives drift — some go past their target date, some get approved but never scaffolded, some go stale — and nothing surfaces the whole picture at once.
- **What it does**: inventories initiatives by status and flags past-target, approved-but-unscaffolded, and stale items (it does not modify anything).
- **If it fails**: it is non-blocking and read-only — a failure means you simply have no rollup, not a broken agent.

### Why `/aget-create-initiative` went STRICT

It mirrors the existing `/aget-propose-initiative` so the propose→create verb-pair is symmetric. STRICT (D71) means: once initiatives are part of your governance, the canonical skill is the required path to create one (direct file authoring bypasses spec-conformance and self-verification). External fleets not using initiatives are unaffected.

## What Changed

### Added

- **`AGET_UNATTENDED_AUTONOMY_SPEC` v1.0.0** — new specification: 8 EARS requirements (`CAP-UNATTEND-001..008`) bounding what an agent may do unattended versus what it must escalate. Governance-only; no runtime is shipped this release.
- **`check_initiatives.py`** — new read-only portfolio rollup over `planning/initiatives/INIT-*.md`: inventory by status, past-target detection, approved-but-unscaffolded surfacing, staleness, and recursion-handled self-row (10 V-tests).
- **`/aget-create-initiative`** — promoted to canonical core at STRICT enforcement (D71), closing the verb-pair gap with the existing `/aget-propose-initiative`.

### Notes on Test Posture

All `AGET_UNATTENDED_AUTONOMY` behavioral V-tests are **runtime-pending** — they govern a runtime not yet built, and per the no-test-theater principle (ADR-007) they are not asserted as passing against absent code. The only runnable-now check is the coverage-invariant meta-test `tests/test_unattended_autonomy_spec.py` (5/5 PASS).

### Breaking Changes

None. v3.21.0 is fully backward-compatible with v3.20.x.

## Upgrade Checklist

### Per Agent

- [ ] Pull latest framework
- [ ] Bump `aget_version` to `3.21.0` (or accept the framework's bump); keep `version.json` + `AGENTS.md` + manifest coherent
- [ ] Copy `check_initiatives.py` if you maintain initiatives
- [ ] Copy `/aget-create-initiative` to `.claude/skills/` (remove any phantom-marker AGENTS.md row once the skill is present)
- [ ] Add an `AGET_UNATTENDED_AUTONOMY` envelope block to config **only if** you run agents unattended
- [ ] Confirm session protocol scripts run cleanly (`wake_up.py`)
- [ ] No migration required (no breaking changes)

### Fleet-Wide

- [ ] One pilot agent confirms v3.21.0 deploys + runs (see Pilot Tracking below)
- [ ] Coordinator records confirmation before declaring fleet-wide done (deployment-verification discipline: implemented ≠ running)

## DEPLOYMENT_SPEC Note (Option B)

No new `DEPLOYMENT_SPEC_v3.21.0.yaml` is shipped. v3.21.0 inherits the `DEPLOYMENT_SPEC_v3.16.0.yaml` contract semantically — there is no deployment-contract change in this release (consistent with v3.17–v3.20, which also inherited v3.16.0). Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z}.yaml` (currently `v3.16.0`).

## Delta Spec Note (Option B)

No `specs/deltas/AGET_DELTA_v3.21.md` is shipped. v3.21.0's changes are additive (a new governance spec, a read-only rollup script, and a skill promotion) with no spec-contract delta requiring a formal delta document.

## Pilot Tracking

| Agent | Version Confirmed | Date | Notes |
|-------|:-----------------:|------|-------|
| _(framework owner)_ | ✅ 3.21.0 deployed | 2026-06-06 | Self-migrated to 3.21.0 pre-ship per R-REL-006-01; `wake_up.py` confirms v3.21.0 — first deployment confirmed |
| _(coordinator)_ | ☐ | — | Awaiting second-agent confirmation |
| _(broader-fleet)_ | ☐ | — | Awaiting cohort rollout |

## References

- CHANGELOG.md `## [3.21.0]`
- `SOP_release_process.md` (release procedure)
- `AGET_RELEASE_SPEC.md` (R-REL-019 release-to-fleet handoff)
- `AGET_UNATTENDED_AUTONOMY_SPEC.md` (CAP-UNATTEND-001..008)

---

*Generated for the public aget-framework. Paths use placeholders, not internal values. No private fleet identifiers included.*
