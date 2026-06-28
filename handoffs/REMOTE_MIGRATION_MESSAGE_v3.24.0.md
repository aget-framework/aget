# Fleet Migration Message — AGET v3.24.0 ("Reliance & Boundaries")

**Version**: v3.24.0 · **Date**: 2026-06-27 · **Type**: Minor (additive)

## Breaking Changes

None. v3.24.0 is additive — a new requirement (R-BND-001), a new schema + validator (skill-reliance manifest), and a new standard (AGET_HOST_RUNTIME_SPEC). Existing skills, specs, and scripts are unchanged. **Existing agents continue to run unaffected at their current behavior** even if none of the new payload is adopted.

## Upgrade Guide

An existing-agent point-upgrade to v3.24.0 has **two distinct layers** — keep them separate:

**1. Blocking (required for v3.24.0 conformance) — the L444 coherence triplet only:**
   - `.aget/version.json` `aget_version` → `3.24.0` (+ a `migration_history` entry)
   - `AGENTS.md` `@aget-version:` → `3.24.0`
   - `manifest.yaml` `version:` → `3.24.0`
   That triplet is the *entire* blocking set for an existing agent. Nothing else is required to be conformant.

**2. Additive (optional — adopt only if the agent declares a reliance contract):**
   - `specs/requirements/R-BND-001_boundary_reliance.md` (boundary & reliance requirement)
   - `schemas/skill_reliance_manifest.schema.yaml` + `scripts/check_skill_reliance_manifest.py`
   - `specs/AGET_HOST_RUNTIME_SPEC.md` (host-runtime filesystem-layout standard)
   - `.aget/skill_reliance_manifest.yaml` (the declared `{S}`/`{O}`/`{D}` contract — author only if you want a release-pinned, self-checkable reliance contract)

   **If you adopt the payload: conformance-then-bump.** Install the additive artifacts and (for a reliance contract) pass the validator *first*, then bump the triplet. Never bump the version label to advertise payload you have not actually installed — a label that overstates installed payload is the failure mode this release's own rollout had to correct.

## Deployment Requirements

- Python 3 (stdlib only — no new dependencies).
- No schema migration. No data migration.
- The reliance feature is **opt-in**: an agent not declaring a reliance contract needs no manifest and is fully conformant on the triplet alone.
- Fleet rollout cadence is the supervisor's lane (L511).

## Smoke Test

```bash
# 1. Coherence triplet (the blocking set) — expect all three == 3.24.0
grep -m1 'aget_version' $AGENT/.aget/version.json
grep -m1 '@aget-version:' $AGENT/AGENTS.md
grep -m1 '^version:' $AGENT/manifest.yaml    # N/A if the manifest carries no agent-level version stamp (see Playbook #1)

# 2. Health (version-pass != health-pass — run both)
python3 $FW/scripts/health_check.py --dir $AGENT     # expect healthy 9/9

# 3. Reliance validator — ONLY if a contract was declared (additive layer)
python3 $AGENT/scripts/check_skill_reliance_manifest.py
```

## Rollback

Drop-in reverse: pin to 3.23.1. No schema/data migration to unwind. The additive artifacts (R-BND-001, schema/validator, HOST_RUNTIME_SPEC, reliance manifest) are inert under 3.23.1 — harmless if left in place; the version triplet is the only thing to revert.

---

## Operational Playbook — lessons from an executed v3.23.1 → v3.24.0 fleet migration

The reference fleet ran this migration end-to-end (all active agents upgraded, zero failures / zero health regression). The findings below are **transferable** (no fleet-specific assumptions) and sharpen — not replace — your portfolio's `SOP_fleet_upgrade` and `SOP_release_process` Phase 7.

1. **"Triplet" is really triplet-OR-doublet — a missing manifest stamp is N/A, not stale.** Some agents carry a schema-only `manifest_version:` key (no agent-level `version:` stamp) or no `manifest.yaml` at all. For those the manifest bump is a **no-op**, so the upgrade touches two files, not three. A block-aware patcher correctly skips a stamp that does not exist; do not flag its absence as drift. All such agents are still fully conformant on `version.json` + `AGENTS.md`.

2. **Separate blocking from additive before you start.** The v3.24 blocking set is the coherence triplet only; the reliance payload is additive. Migrating an existing fleet does **not** require fanning the payload to every agent — adopt it only where a reliance contract is wanted. Imposing full payload fleet-wide is work the spec does not require.

3. **Conformance-then-bump, never label-only.** If an agent adopts the reliance payload, install it and pass the validator *before* bumping the version label. A version label that advertises payload not actually present is a badge≠state defect — verify the payload on disk, then bump.

4. **Verify from disk, never from labels or exit codes.** The fleet registry's per-agent version field can lag the actual on-disk `version.json` (it is a reconciled label, not ground truth) — in this migration the registry and disk disagreed on nearly every row mid-flight. Headless self-upgrade sessions also return `exit=0` even when a stamp silently failed. Re-read each agent's `version.json` after every wave; reconcile the registry **from disk**, not toward the target version.

5. **Pre-flight must classify bump / repair / skip — not just OK/fail.** A pre-flight that collapses everything into "OK" hides agents that need a *repair* path (e.g., a partial prior state) behind the same green as a clean *bump*. Classify each agent's required action explicitly before the rollout.

6. **One owning session per migration.** Two coordinator sessions running on one migration is a real hazard (duplicate monitors, racing registry writes). Assign a single owner; other sessions stay read-only.

7. **Canary, then fan out; pick population-spanning pilots.** Upgrade one representative agent and verify from disk before the batch. Choose pilots that span manifest-schema × location-class (incl. monorepo agents whose git lives at a parent) × transitive-deps — the convenient/coordinator-adjacent agents are the *least* representative.

8. **Known v3.24 issue — the reliance validator assumes canonical adjacency.** `check_skill_reliance_manifest.py` resolves the canonical framework as a sibling directory; run from a non-adjacent seat it may WARN / leave `{S}` unverified even when the contract is valid. A fix (config-key + parent-walk fallback) is in progress upstream; until then, run the validator from a framework-adjacent checkout, or treat an adjacency WARN as non-fatal after a manual `{S}` spot-check.

**Reusable harness shape** (R-CLI-004-safe — each agent reads → judges → runs the patcher *on itself*; the coordinator never writes another repo): block-aware triplet patcher (`--dry-run`, bump/repair/skip classification) → parent-walking fail-loud dispatch → from-disk verifier (triplet + health + origin-sync) → registry reconcile from disk → branch-aware push (honor per-agent no-push policies).

*Generic by design — no agent names or fleet sizes. Pair with your portfolio's `SOP_fleet_upgrade`.*
