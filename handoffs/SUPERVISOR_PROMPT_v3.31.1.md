# SUPERVISOR PROMPT — AGET v3.31.1

**Target**: independently verify and adopt the receiver-safe close-gate correction before resuming a
fleet migration.

Use only public GitHub materials. Do not use a private relay, private repository path, or untagged
working-tree file as evidence for the correction.

## Acquire and identify

1. Fetch the annotated `v3.31.1` tag from `aget-framework/aget` and record its peeled commit.
2. Read these files from that tag:
   - `handoffs/REMOTE_MIGRATION_MESSAGE_v3.31.1.md`
   - `handoffs/DELIVERED_FILES_v3.31.1.yaml`
   - `handoffs/TRACEABILITY_EXCEPTION_v3.31.1.md`
   - `DEPLOYMENT_SPEC_v3.31.1.yaml`
3. Verify every ordered package digest and the manifest tuple digest before installing anything.

## Verify before adoption

Run the receiver contract from a clean checkout of the tag:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -s -p no:cacheprovider tests/test_close_gate_receiver_contract.py
```

Require all 18 tests to pass. A producer test result, public availability, or a matching version string
does not substitute for this receiver-owned verification.

## Adopt in controlled stages

Preserve local governance and receiver-owned extensions. Install only the manifest-bound correction
through the receiving supervisor's governed migration procedure. Record these as separate facts:

1. the package was retrieved and its identity verified;
2. the correction was installed;
3. both blocking and passing close-gate behavior were verified locally; and
4. the supervisor's prior-version close test passed.

Do not authorize fleet migration merely because the Release exists. Resume downstream migration only
after the supervisor has adopted the correction, passed its own close test, and recorded the resulting
migration-gate decision.
