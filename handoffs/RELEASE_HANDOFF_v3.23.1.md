# Release Handoff: AGET v3.23.1

**Version**: v3.23.1
**Date**: 2026-06-20
**Type**: Minor (additive, no breaking changes)
**Theme**: Goal Tier (canonical) + Close-Authorization Guard

---

## Summary

v3.23.1 is the fast-follow the v3.23.0 preview promised: the **Goal Tier lands in canonical**, and the **close-authorization guard** (built but explicitly *not* shipped in v3.23.0) is now in `aget/` and propagated to all 13 templates.

## What's New

- **`AGET_GOAL_SPEC` v0.2.0 → canonical `specs/`** — the Goal artifact (a durable cross-session **outcome**: North Star → Goal → Initiative → Action), KAOS goal typing (Achieve / Maintain / Soft), and the ≥1-loop requirement (a Goal owns a regulating loop or it decays).
- **`aget-create-goal` + `aget-propose-goals`** — the propose→commit verb pair, with the spec canonical; two-tier store (committed vs aspirational).
- **`aget-close-project` + `close_authorization_guard.py`** — close-time authorization guard wired into close as Step 2.5 (blocks a close that claims authorization without a linked event).

## Upgrade Guide

- Drop-in minor. On upgrade, the three new skills + their engine scripts (`create_goal.py`, `record_goals_ext.py`, `close_authorization_guard.py`, `close_gate_check.py`) are present in `.claude/skills/` + `scripts/`.
- Committed Goals live in `governance/GOALS.md` (created on first `/aget-create-goal`).

## Compatibility

- **No breaking changes.** Additive only. Existing skills/specs/scripts unchanged.
- Python: stdlib-only engine scripts (import-smoke verified across archetypes).

## Deployment Requirements

- Fleet upgrade is the supervisor's lane (L511). Minimum pilot = framework-AGET (this instance, in-use Goal dogfooded) + supervisor (self-migration pending).

## Smoke Test

```bash
python3 scripts/create_goal.py <goal.json>     # commits a Goal to governance/GOALS.md
python3 .aget/patterns/release/version_bump.py --check 3.23.1   # version coherence
```

## Rollback

Pre-deployment: no action. Post-deployment P0: pin to 3.23.0 (drop-in reverse; no schema migration).

## Pilot Tracking

| Agent | Version confirmed | Notes |
|-------|-------------------|-------|
| private-aget-framework-AGET | 3.22.0 (manager) | canonical author; Goal Tier dogfooded in-use (GOAL-RELEASE-INTEGRITY) |
| private-supervisor-AGET | _pending_ | self-migration = the ≥1-downstream-deployment bar (principal Q4) |

## Provenance

Released 2026-06-20 (L735 Saturday window). Post-release remediation: this handoff + body-conformance + homepage were completed in a same-session recovery after an L967 process-bypass (release run from the plan's gate-list rather than the SOP, skipping the pre-tag completeness gate). Claim-path gate PASS on the live release (no overclaim).
