# REMOTE MIGRATION — AGET v3.30.0

**State**: RELEASED — bounded downstream receipt complete; fleet convergence remains HOLD.

## Breaking Changes

None. The bounded package is additive and does not authorize a trust, hook, or permission change.

## Upgrade Guide

1. Capture the receiving seat's current version, health, and test baseline.
2. Fetch and pin the public `v3.30.0` tag after publication.
3. Read `release-notes/v3.30.0.md`, `DEPLOYMENT_SPEC_v3.30.0.yaml`, and
   `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json`. Use
   `handoffs/DELIVERED_FILES_v3.30.0.yaml` only to reproduce the immutable-tag bounded-package receipt.
4. Record the tag commit and SHA-256 of `AGENT_SKILLS_PACKAGE.json`.
5. Preserve instance-owned extensions and local governance; apply only the semantic rows that are
   applicable to the receiving seat. Do not treat the six-file bounded package or version pins alone as a
   full v3.30 migration.

## Conformance and manual smoke

```sh
python3 scripts/validate_agent_skill_package.py --json
```

Require exit 0, then follow `docs/AGENT_SKILLS_PACKAGE.md` to copy one resolved package directory and
invoke that skill from an AGET repository providing the documented receiver-local runtime. Record the
receiving seat, source and destination digests, command exit, invoked skill, whether the script or fallback
path executed, and observed output. A clone or successful source validator alone is not ordinary-use
evidence.

## Enforcement boundary

The package does not carry its receiver-local AGET scripts and repository substrate, hooks, permissions,
release gates, or D71 structural routing. The receiving seat remains responsible for runtime prerequisites,
authorization, and safety controls.

## Fleet boundary

The independent Gate-4 package receipt is complete. It does not authorize a fleet wave or prove that
`scripts/study_topic.py` and the version pins converged across the fleet. The supervisor must derive the
target denominator from its authoritative register, plan a pilot and cohorts, and collect the per-seat
receipts required by `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json`.

## Rollback

Restore the prior pin and only the semantic-row payloads changed on that seat; remove a manually copied
skill directory if applicable. Preserve instance-owned state and record the failed row. No registry state,
installer state, or data migration needs reversal.
