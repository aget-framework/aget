# Release Handoff: AGET v3.23.1

**Version**: v3.23.1
**Date**: 2026-06-20
**Type**: Minor (additive, no breaking changes)
**Theme**: Goal Tier (canonical) + Close-Authorization Guard

---

## Summary

v3.23.1 is the fast-follow the v3.23.0 preview promised: the **Goal Tier lands in canonical**, and the **close-authorization guard** (built but not shipped in v3.23.0) is now in `aget/` and propagated to all 13 templates.

## What's New

- **`AGET_GOAL_SPEC` v0.2.0 → canonical `specs/`** — the Goal artifact (a durable cross-session **outcome**: North Star → Goal → Initiative → Action), KAOS goal typing (Achieve / Maintain / Soft), and the requirement that every Goal owns at least one regulating loop, or it decays.
- **`aget-create-goal` + `aget-propose-goals`** — the propose→commit verb pair, with the spec canonical; two-tier store (committed vs aspirational).
- **`aget-close-project` + `close_authorization_guard.py`** — close-time authorization guard wired into close as Step 2.5 (blocks a close that claims authorization without a linked event).

## Upgrade Guide

- Drop-in minor. On upgrade, the three new skills + their engine scripts (`create_goal.py`, `record_goals_ext.py`, `close_authorization_guard.py`, `close_gate_check.py`) are present in `.claude/skills/` + `scripts/`.
- Committed Goals live in `governance/GOALS.md` (created on first `/aget-create-goal`).

## Compatibility

- **No breaking changes.** Additive only. Existing skills/specs/scripts unchanged.
- Python: stdlib-only engine scripts (import-smoke verified across archetypes).

## Deployment Requirements

- No schema or data migration. Drop-in across `aget/` + 13 templates.

## Smoke Test

```bash
python3 scripts/create_goal.py <goal.json>     # commits a Goal to governance/GOALS.md
python3 .aget/patterns/release/version_bump.py --check 3.23.1   # version coherence
```

## Rollback

Pre-deployment: no action. Post-deployment: pin to 3.23.0 (drop-in reverse; no schema migration).

## Context for External Fleets

For adopters outside the aget-framework organization: v3.23.1 introduces the **Goal Tier** as a first-class governance artifact — a durable, cross-session *outcome* that sits between an agent's permanent purpose (North Star) and its bodies of work (Initiatives). If your fleet uses the AGET templates, the upgrade is drop-in: pull the v3.23.1 template for each archetype and the Goal-Tier skills + engine scripts are present. No configuration, schema, or data migration is required. The Goal Tier is optional to adopt — existing workflows are unaffected until you invoke `/aget-propose-goals` / `/aget-create-goal`.

## Provenance

Released 2026-06-20. Claim-path verification passed on the live release (every advertised capability resolves to a present-at-source canonical artifact).
