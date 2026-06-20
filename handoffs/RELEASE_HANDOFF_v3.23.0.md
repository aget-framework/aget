# Release Handoff — AGET v3.23.0

**Version**: 3.23.0
**Released**: 2026-06-20
**Theme**: Goal Tier (preview)
**Type**: Minor (no breaking changes)

## Summary

v3.23.0 introduces the **Goal Tier** as a usable preview (two skills + a draft spec in canonical core). It is a drop-in upgrade from 3.22.0.

## What's New

- **Goal Tier (preview)** — `aget-create-goal` commits a selected candidate goal into a governed Goal artifact (North Star → Goal → Initiative), backed by `AGET_GOAL_SPEC` v0.2.0 (draft). Canonical spec promotion follows in 3.23.1.
- **`aget-propose-goals`** — generates N ranked candidate session-goals, each scored ex-ante by a goal-selection rubric.

## Not in this release (corrected post-release)

- A **close-time authorization guard** was built and exercised in the framework-manager instance this cycle but is **not** in canonical `aget/` — it lands (with a population-spanning pilot) in 3.23.1. The original "Integrity Hardening" theme + guard bullet were corrected because they named a capability not present in the public framework.
- The two internal release-tooling fixes (#1654/#1656) live in the manager instance, not canonical, and were removed from the public notes.

## Upgrade Guide

1. Pull the latest `aget/` and your template(s) at 3.23.0.
2. No migration required — minor release, no breaking changes.
3. The Goal Tier ships as a preview (skill + draft spec); canonical spec promotion and template skill propagation land in 3.23.1.

## Deferred

- Self-oversight ratchet generalization and interaction-channel rung → 3.24.
- Goal-Tier canonical spec promotion (ontology grounding) → 3.23.1.

## Context for External Fleets

Adopters running their own AGET fleets can upgrade to 3.23.0 at will — it is a drop-in minor with no breaking changes. The Goal Tier ships as a preview, so external fleets can begin exercising `aget-propose-goals` and `aget-create-goal` now; the canonical `AGET_GOAL_SPEC` and template skill propagation arrive in 3.23.1 without requiring any rework of preview usage. No coordinated migration is needed.

## Pilot Tracking

| Adopter | Version Confirmed | Notes |
|---------|-------------------|-------|
| _(pending downstream confirmation)_ | | |
