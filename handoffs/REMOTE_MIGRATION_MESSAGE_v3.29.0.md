# REMOTE MIGRATION — AGET v3.29.0

**State**: PRE-PUSH. Use only after `v3.29.0` is independently confirmed at the public origin.

## Breaking Changes

None. The Codex bundle is additive; no trust-level change is required or authorized by migration.

## Upgrade Guide

1. Capture current version, health, and test baseline.
2. Fetch the public `v3.29.0` tag and read `release-notes/v3.29.0.md` plus
   `handoffs/DELIVERED_FILES_v3.29.0.yaml` from that tag.
3. Apply every manifest path and both version-pin edits; preserve all instance-owned `*_ext.py` files.
4. Run the behavioral smoke below and report exact PASS/FAIL/UNAVAILABLE states.

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

## Rollback

Restore the prior pinned tag/version and remove only the manifest's additive v3.29 files. Preserve local
extensions and operational logs. Re-run the pre-upgrade health/test baseline.

## Report back

Return: receiving seat, verified `aget_version`, native discovery result, invoked workflow, recovery result,
and source path/command. An acknowledgment without received-state/behavior evidence is not completion.
