# Release Handoff — AGET v3.23.0

**Version**: 3.23.0
**Released**: 2026-06-20
**Theme**: Goal Tier & Integrity Hardening
**Type**: Minor (no breaking changes)

## Summary

v3.23.0 introduces the **Goal Tier** as a usable preview and hardens release-close integrity. It is a drop-in upgrade from 3.22.0.

## What's New

- **Goal Tier (preview)** — `aget-create-goal` commits a selected candidate goal into a governed Goal artifact (North Star → Goal → Initiative), backed by `AGET_GOAL_SPEC` v0.2.0 (draft). Canonical spec promotion follows in 3.23.1.
- **`aget-propose-goals`** — generates N ranked candidate session-goals, each scored ex-ante by a goal-selection rubric.
- **Close-time authorization guard** — `/aget-close-project` now requires a linked authorization event for principal-attributed closes and flags irreversible consequences.

## Fixed

- Scope-board generation against a locked version scope (#1654).
- Homepage `--apply` no-op on multi-section content updates (#1656).

## Upgrade Guide

1. Pull the latest `aget/` and your template(s) at 3.23.0.
2. No migration required — minor release, no breaking changes.
3. The Goal Tier ships as a preview (skill + draft spec); canonical spec promotion and template skill propagation land in 3.23.1.

## Deferred

- Self-oversight ratchet generalization and interaction-channel rung → 3.24.
- Goal-Tier canonical spec promotion (ontology grounding) → 3.23.1.

## Pilot Tracking

| Adopter | Version Confirmed | Notes |
|---------|-------------------|-------|
| _(pending downstream confirmation)_ | | |
