# RELEASE_HANDOFF: v3.20.0

**Released**: 2026-05-30
**Theme**: Debt Paydown + Structural-Guard Deployment + Functional Capability
**Upgrade type**: version-bump only (no breaking changes)

---

## Executive Summary

v3.20.0 spends an accumulated reliability dividend on three fronts: retiring carry-forward debt (a long-standing citation-resolution gap and a spec-scoring fault), deploying structural guards that make release-and-close discipline enforced rather than advisory, and adding direct user-facing value on the highest-frequency session surface (`/aget-propose-actions`). Existing instances upgrade by version-bump only.

## What Changed

### Added

- **`/aget-propose-actions` presentation enhancement** — per proposed action: an Evidence column (the grounding citation), a ▶ Recommendation line (the agent's lead pick + why), and a ⚠ Decisions-needed callout that lifts judgment-call items out of the autonomous rows. Principals get a recommendation, not just a menu.
- **Close-gate conformance guard** — a conformance check mechanically blocks marking a PROJECT_PLAN COMPLETE while V-test gates remain unchecked (replaces manual eyeballing). Wired into the close-project flow.
- **Health/wind-down signal-class severity** — findings classified by signal class so blocking conditions are distinguished from advisory ones.
- **"Verify with the consumer's own check" rule** — codified in the release SOP: cross-repo/CI claims are verified by the consumer's actual check (e.g. the real CI run), not a local proxy.

### Changed / Fixed

- **Duplicate `CAP-REL-035` declaration in `AGET_RELEASE_SPEC`** — the capability was declared twice, tripping the declaration-uniqueness gate and scoring the entire 224-requirement spec as NONE; merged into the single mature block; spec now scores L5 (Governed).
- **Citation-resolution remediation (R-REL-044 / CAP-REL-035)** — resolved the citations the release citation validator flagged on published surfaces; cross-repo readers no longer hit unexplained 404s.
- **Citation validator `.aget/specs/` resolver** — fixed a leading-dot path-resolution bug that falsely flagged correct `.aget/specs/...` citations; regression test added.
- **Framework CI capability** — pre-push hook hardening; corrected a `--critical` mode that would have run hardcoded tests absent from templates.

### Breaking Changes

None. v3.20.0 is fully backward-compatible with v3.19.0.

## Upgrade Checklist

### Per Agent
- [ ] Pull latest framework
- [ ] Bump `aget_version` to `3.20.0` (or accept the framework's bump)
- [ ] Confirm session protocol scripts run cleanly (`wake_up.py`)
- [ ] No migration required (no breaking changes)

### Fleet-Wide
- [ ] One pilot agent confirms v3.20.0 deploys + runs (see Pilot Tracking below)
- [ ] Coordinator records confirmation before declaring fleet-wide done (deployment-verification discipline: implemented ≠ running)

## DEPLOYMENT_SPEC Note (Option B)

No new `DEPLOYMENT_SPEC_v3.20.0.yaml` is shipped. v3.20.0 inherits the `DEPLOYMENT_SPEC_v3.16.0.yaml` contract semantically — there is no deployment-contract change in this release (consistent with v3.17–v3.19, which also inherited v3.16.0). Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z}.yaml` (currently `v3.16.0`).

## Delta Spec Note (Option B)

No `specs/deltas/AGET_DELTA_v3.20.md` is shipped. v3.20.0's changes are additive (new skill presentation, structural guards, fixes) with no spec-contract delta requiring a formal delta document.

## Pilot Tracking

| Agent | Version Confirmed | Date | Notes |
|-------|:-----------------:|------|-------|
| _(framework owner)_ | ✅ 3.20.0 deployed | 2026-05-30 | Self-migrated per R-REL-006; `wake_up.py` confirms v3.20.0 — first deployment confirmed |
| _(fleet pilot)_ | ⏳ pending | — | Broader-fleet deploy coordinated by supervisor (notification filed) |

## References

- CHANGELOG.md `## [3.20.0]`
- `SOP_release_process.md` (release procedure)
- `AGET_RELEASE_SPEC.md` (CAP-REL-035 / R-REL-044 citation gate)

---

*Generated for the public aget-framework. Paths use placeholders, not internal values. No private fleet identifiers included.*
