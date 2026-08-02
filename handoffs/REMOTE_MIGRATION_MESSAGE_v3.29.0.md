# REMOTE MIGRATION — AGET v3.29.0

**State**: PUBLIC RELEASE — REMOTE PILOT READY; FLEET FAN-OUT HOLD pending the Gate 4 cold-context
discovery/invocation/recovery receipt.

> **Post-tag corrections are part of the packet.** The immutable `v3.29.0` tag contains the original
> payload, but corrections #5–#8 changed receiver-facing bytes and evidence on public `main`. A tag-only
> migration selects a known-defective packet.

## Breaking Changes

None. The Codex bundle is additive; no trust-level change is required or authorized by migration.

## Upgrade Guide

1. Capture current version, health, and test baseline.
2. Fetch the public `v3.29.0` tag and public `main`. Read tag-pinned `release-notes/v3.29.0.md`, then read
   `handoffs/CORRECTIONS_v3.29.0.md` and `handoffs/DELIVERED_FILES_v3.29.0.yaml` from **`main`**.
3. Record the composite packet identity before mutation: tag object, peeled tag commit, resolved `main`
   commit, and SHA-256 of the `main` delivered-files manifest. An unqualified “v3.29.0” receipt is not
   enough to reproduce the packet.
4. Apply every applicable manifest path and both declared `pin_edits`; preserve all instance-owned
   `*_ext.py` files. A seat already at v3.29 uses correction-only adoption: copy only changed paths, do
   not replay migration or append a duplicate migration-history row.
5. Run the behavioral smoke below from the receiving checkout and report exact PASS/FAIL/UNAVAILABLE
   states. An unknown local schema or applicability class is UNAVAILABLE and routes to its owner; do not
   guess by field position or filename prose.

## Deployment Requirements

Python 3.9+; a repository with AGET layout; Codex CLI 0.144.5+ only for the isolated hook-control POC claim.
An untrusted Codex project reports hooks unavailable and must never be labeled enforcing PASS.

## Smoke Test

```sh
python3 scripts/validate_codex_skill_discovery.py --json
python3 scripts/study_topic.py --topic release --purpose pre-release \
  --include-sessions --session-days 7 --include-instruments --json
python3 -m pytest tests/test_study_topic_purpose_recency_rendering.py \
  tests/test_codex_skill_discovery.py -q
```

Then, in cold Codex context, discover `aget-wake-up` or `aget-study-topic`, invoke it normally, checkpoint
with `aget-save-state`, and recover. This last probe is the delivery Goal behavior and must run downstream.
Its first qualifying receipt permits the release manager to re-evaluate Gate 4; it does not by itself prove
remote-fleet-wide behavior.

## Rollback

Restore the prior pinned tag/version and remove only the manifest's additive v3.29 files. Preserve local
extensions and operational logs. Re-run the pre-upgrade health/test baseline.

## Report back

Return: receiving seat, composite packet identity, verified `aget_version`, native discovery result,
invoked workflow, recovery result, and source path/command. Name the measurement timestamp and axis.
An acknowledgment without received-state/behavior evidence is not completion.
