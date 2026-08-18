# Release Handoff — AGET v3.31.1

## Executive Summary

v3.31.1 is a patch correction that packages the close-gate repair as one portable, immutable,
receiver-verifiable release. It supersedes v3.31.0 for consumers waiting on this close-gate dependency.

## What Changed

- The lifecycle module is framework-owned and resolves its default specification inside the checkout.
- Human and JSON output now share one blocking decision and expose material warnings consistently.
- Invalid lifecycle mutations preserve the target; valid mutations commit by atomic replacement.
- The public receiver oracle covers channels, dispositions, errors, mutation, and clean-room topology.
- The ordered release manifest binds the complete executable, normative, test, and handoff package.

## Context for External Fleets

Use the `v3.31.1` tag because a public main-branch commit is mutable and v3.31.0 does not contain the
complete correction. Verify the manifest and oracle from a fresh clone before any local adoption.
Availability is not receipt, receipt is not installation, and installation is not behavioral acceptance.

## Critical Mitigations

The package removes two receiver hazards: a sibling-checkout path assumption and an instance-owned module
that the canonical guard imported unconditionally. Transactional writes prevent a blocked semantic
reconciliation from persisting invalid accounting rows.

## New Tools

No new user-facing command is introduced. The supported check is:

```sh
python3 -m pytest -q tests/test_close_gate_receiver_contract.py
```

If it fails, preserve the fixture and test output, roll back, and do not advance the dependent migration.

## Pilot Tracking Template

| Receiver | Tag commit recorded | Manifest verified | Clean-room oracle | Adopted | Receiver V-test |
|---|---|---|---|---|---|
| downstream supervisor | pending | pending | pending | pending | pending |

No row is pre-acknowledged. Public routing proves publication only.

## Rollback

Return to the receiving seat's pre-upgrade commit or v3.31.0 pin, preserve receiver-owned state, and keep
the dependent migration parked until a corrected immutable package passes the same receiver checks.
