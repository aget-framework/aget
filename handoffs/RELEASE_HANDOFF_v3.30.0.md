# RELEASE HANDOFF — v3.30.0

**Prepared**: 2026-08-09 · **State**: RELEASE CANDIDATE

> Publication is not downstream delivery. `GOAL-V330-DELIVERED` remains active until an independent seat
> obtains the public package, records its digest, receives a conformance exit 0, and invokes one packaged
> skill through the documented manual path.

## Breaking Changes

None. Existing Claude and Agent Skills paths remain; no trust or permission setting is changed.

## Upgrade Guide

Read `release-notes/v3.30.0.md`, pin the immutable v3.30.0 tag after publication, and use
`handoffs/DELIVERED_FILES_v3.30.0.yaml` with `DEPLOYMENT_SPEC_v3.30.0.yaml`. Preserve instance-owned
extensions and local governance. This release does not authorize marketplace registration, an installer,
or changes to client trust.

## Deployment Requirements

Python 3.9+ and a compatible Agent Skills client. Run:

```bash
python3 scripts/validate_agent_skill_package.py --json
```

Require exit 0 before copying a resolved package directory. The package carries instructions, not the
producer's hooks, permission model, release gates, or structural enforcement.

## Smoke Test

1. Record the public package-manifest SHA-256 and receiving seat.
2. Run the shipped conformance command and require exit 0.
3. Follow `docs/AGENT_SKILLS_PACKAGE.md` to copy one resolved skill directory.
4. Invoke one packaged skill and record its documented output.

Steps 1–4 must be performed by an independent downstream seat for the Gate-4 receipt. Producer rehearsal
does not satisfy the Goal.

## Rollback

Restore the prior pinned tag/version and remove only the manifest-listed v3.30 additive files. A manually
copied skill may be removed independently. Preserve local extensions and operational logs.

## Pilot tracking

| Seat | v3.30 received state | Conformance | Manual invocation | Evidence |
|---|---|---|---|---|
| framework producer | candidate built | producer PASS; not downstream | producer documentation only | Gate 0A receipt |
| independent receiver | pending Gate 4 | pending | pending | Independent-seat receipt required: package digest, conformance exit 0, one documented manual-path invocation, and seat named |
