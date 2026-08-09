# REMOTE MIGRATION — AGET v3.30.0

**State**: RELEASE CANDIDATE — downstream receipt remains Gate-4 work.

## Breaking Changes

None. The bounded package is additive and does not authorize a trust, hook, or permission change.

## Upgrade Guide

1. Capture the receiving seat's current version, health, and test baseline.
2. Fetch and pin the public `v3.30.0` tag after publication.
3. Read `release-notes/v3.30.0.md`, `DEPLOYMENT_SPEC_v3.30.0.yaml`, and
   `handoffs/DELIVERED_FILES_v3.30.0.yaml`.
4. Record the tag commit and SHA-256 of `AGENT_SKILLS_PACKAGE.json`.
5. Preserve instance-owned extensions and local governance; apply only the applicable manifest paths and
   version pins.

## Conformance and manual smoke

```sh
python3 scripts/validate_agent_skill_package.py --json
```

Require exit 0, then follow `docs/AGENT_SKILLS_PACKAGE.md` to copy one resolved package directory and
invoke that skill in a compatible client. Record the receiving seat, package digest, command exit, invoked
skill, and documented output. A clone or successful validator alone is not ordinary-use evidence.

## Enforcement boundary

The package does not carry hooks, permissions, release gates, or D71 structural routing. The receiving
seat remains responsible for authorization and safety controls.

## Rollback

Restore the prior pin and remove the manifest-listed additive files or the manually copied skill
directory. No registry state, installer state, or data migration needs reversal.
