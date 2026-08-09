# RELEASE HANDOFF — v3.30.0

**Prepared**: 2026-08-09 · **State**: RELEASED

> Publication was not treated as downstream delivery. An independent seat has now completed the bounded
> package receipt: public digest recorded, conformance exit 0, destination digest verified, and one
> packaged skill invoked. This does not prove fleet-wide semantic convergence; that separate contract is
> `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` and remains on HOLD pending a supervisor wave plan.

The immutable `v3.30.0` tag was cut before publication and still contains `State: RELEASE CANDIDATE` in
this file. Mutable `main` records the released state and post-tag corrections; the tag is not moved.

## Breaking Changes

None. Existing Claude and Agent Skills paths remain; no trust or permission setting is changed.

## Upgrade Guide

Read `release-notes/v3.30.0.md`, pin the immutable v3.30.0 tag after publication, and use
`handoffs/DELIVERED_FILES_v3.30.0.yaml` only for the bounded package receipt. For an AGET fleet upgrade,
use `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` with `DEPLOYMENT_SPEC_v3.30.0.yaml`. Preserve
instance-owned extensions and local governance. This release does not authorize marketplace registration,
an installer, changes to client trust, or fleet dispatch.

## Deployment Requirements

Python 3.9+, a compatible Agent Skills client, and an AGET repository substrate providing the
receiver-local scripts and paths named in `docs/AGENT_SKILLS_PACKAGE.md`. Run:

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

## Context for External Fleets

v3.30.0 is an additive minor release. External fleets should consume the public package manifest,
conformance validator, package guide, deployment specification, semantic fleet-migration contract, and
this handoff; private release ledgers are not part of the delivery contract.

The package provides a bounded manual path across compatible clients **inside an AGET repository
substrate**. It does not provide marketplace registration, a one-command installer, automatic client
discovery, receiver-local scripts, or portable hooks, permissions, release gates, and structural
enforcement. Preserve local governance and trust settings. The independent Gate-4 receipt proves this
bounded package was received once; it is not a fleet-upgrade receipt.

The immutable v3.30.0 tag contains the shipped package. Post-tag corrections to mutable instructions are
read from `main`; tags are never moved to conceal a correction.

## Rollback

Restore the prior pinned tag/version and remove only the manifest-listed v3.30 additive files. A manually
copied skill may be removed independently. Preserve local extensions and operational logs.

## Pilot tracking

| Seat | v3.30 received state | Conformance | Manual invocation | Evidence |
|---|---|---|---|---|
| framework producer | released | producer PASS; not downstream | producer documentation only | Gate 0A receipt |
| independent downstream seat | received from public tag | PASS, exit 0; destination digest matched | PASS, `aget-wake-up`, exit 0 ending `Ready.` | `gmelli/aget-aget#2191`; full receipt retained in the governed producer/supervisor evidence chain |
