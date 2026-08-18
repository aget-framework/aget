# REMOTE MIGRATION — AGET v3.31.1

**State**: PUBLIC RELEASE PACKAGE; receipt, adoption, and migration authorization remain receiver-owned.

## Breaking Changes

None. This patch changes close-gate correctness and packaging but does not automatically rewrite plans,
change permissions, or authorize migration.

## Upgrade Guide

1. Use only public `aget-framework/aget` materials. Fetch the annotated `v3.31.1` tag and record its
   peeled commit; do not use a private relay or an untagged main-branch commit.
2. Read `release-notes/v3.31.1.md`, `DEPLOYMENT_SPEC_v3.31.1.yaml`, and
   `handoffs/DELIVERED_FILES_v3.31.1.yaml` at that tag.
3. Verify every ordered manifest path and SHA-256 before installing or invoking the correction.
4. Preserve receiver-owned extensions and local governance. Install only through the receiver's governed
   migration procedure.

## Deployment Requirements

Require a clean checkout of `v3.31.1`, Python 3.10 or later, and no sibling repository dependency.
Publication establishes availability only. Record acquisition, integrity, clean-room verification,
installation, and adoption separately.

## Smoke Test

```sh
python3 -m pytest -q tests/test_close_gate_receiver_contract.py
```

Require exit 0. Then run the receiving supervisor's v3.30 `V4.0` against the tag-pinned implementation.
Only that receiver-owned result may clear its v3.31 `G-1.0`; do not infer clearance from this release.

## Rollback

Restore the receiver's pre-upgrade commit or v3.31.0 pin, preserve instance-owned files and the failed
fixture, record the failure, and keep self-migration parked.
