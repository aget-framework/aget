# Release Handoff — AGET v3.33.1 “Receiver-visible integrity”

**Target version**: 3.33.1  
**Target date**: 2026-08-30  
**Breaking changes**: None intentional  
**State**: Candidate content; publication and deployment are not asserted by this artifact.

## Summary

v3.33.1 is the forward-only integrity correction for the immutable v3.33.0 release. It restores a
complete tag-bound deployment package, advances the core and thirteen templates coherently, repairs the
organization homepage, and adds substantive Skill Routing and Write Scope guidance to the document
template. It does not move or reinterpret any v3.33.0 tag or Release object.

## Exact Payload

| Surface | Correction | Receiver boundary |
|---|---|---|
| Core release artifacts | Complete 3.33.1 deployment spec, notes, handoffs, history, and identity | Read only from the peeled core tag |
| Thirteen templates | Coherent 3.33.1 identity and migration history | Use only the receiver's matching archetype template |
| Document template | Adds substantive Skill Routing and Write Scope sections | Other pre-existing configuration findings remain outside scope |
| Organization homepage | Restores current-version and migration discoverability | Mutable discovery evidence, not receiver deployment evidence |

## Context for External Fleets

External fleets must treat availability, acquisition, installation, behavioural verification, and
acceptance as separate states. This handoff is an information and verification contract, not authority to
modify a receiver. Each receiving manager applies its own governance, preserves local extensions, and
returns evidence from the receiver itself. No operator-specific path, private inventory, or fleet-wide
deployment claim is embedded in this public artifact.

## Receiving-Agent Governance Checklist

- [ ] Obtain receiver-local approval and record its applicable migration procedure.
- [ ] Capture pre-upgrade commit, version, dirty paths, and full-test baseline.
- [ ] Verify annotated core and matching-template tags and record peeled commits.
- [ ] Read `DEPLOYMENT_SPEC_v3.33.1.yaml` from the peeled core tag.
- [ ] Diff every selected destination and preserve receiver-owned extensions.
- [ ] Prepare an exact rollback reference before mutation.

## Deployment Requirements

Python 3.10 or later, immutable tag-bound sources, a matching archetype template, a receiver baseline,
and a rollback stable cut are required. Missing evidence is `HOLD`, never an inferred pass.

## Upgrade Guide

```bash
export SOURCE=/path/to/aget-v3.33.1
export TEMPLATE=/path/to/matching-template
export AGENT=/path/to/receiving-agent

git -C "$SOURCE" fetch --tags origin
git -C "$SOURCE" checkout --detach v3.33.1
CORE_SHA=$(git -C "$SOURCE" rev-parse 'v3.33.1^{commit}')
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.33.1)" = tag
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["aget_version"])' "$SOURCE/.aget/version.json")" = 3.33.1
test -f "$SOURCE/DEPLOYMENT_SPEC_v3.33.1.yaml"

git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.33.1)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse 'v3.33.1^{commit}')

BEFORE_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" status --short
(cd "$AGENT" && python3 -m pytest tests/ -q)
```

Select only paths applicable under the deployment specification. Compare source and destination, preserve
local extensions, apply content before labels, and record source/destination blob identities.

## Smoke Test

```bash
(cd "$SOURCE" && python3 -m pytest -q tests/)
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
git -C "$AGENT" diff --check
```

Required: no new receiver test failures, wake-up reports 3.33.1, and each selected path meets its
tag-pinned postcondition. Preserve raw output; do not normalize an unavailable predicate into pass.

## Rollback

Never reset or force-push shared history. Revert a committed migration with `git revert`; before commit,
restore only the recorded migration path set from `BEFORE_SHA`. Re-run the baseline tests and wake-up,
preserve failure evidence, and record `ROLLED_BACK` or `HOLD`.

## Receiver Receipt Contract

Record receiver and archetype; observation time; core/template tags and peeled commits; deployment-spec
blob; pre-upgrade commit/version/dirty paths/test baseline; selected paths and preserved extensions;
migration commit; raw test and wake-up results; rollback stable cut; verifier; and exactly one disposition:
`ACQUIRED`, `INTEGRITY_VERIFIED`, `INSTALLED`, `BEHAVIOUR_VERIFIED`, `ACCEPTED`, `HOLD`, or `ROLLED_BACK`.

## Completion Response

Return the receipt to the release manager through the receiving fleet's governed handoff route. A receipt
proves only the named receiver and observed state; it does not prove fleet-wide deployment.

## Known Items

- v3.33.0 remains immutable.
- The document template's non-Tier-1 legacy configuration findings remain outside this correction.
- Homepage correctness is discoverability evidence, not installation evidence.

## Pilot Tracking

| Receiver | Archetype | State | Evidence |
|---|---|---|---|
| Pending | Pending | NOT_OBSERVED | Receiver-owned receipt required |

## Tag-Pinned References

- `DEPLOYMENT_SPEC_v3.33.1.yaml`
- `release-notes/v3.33.1.md`
- `handoffs/REMOTE_MIGRATION_MESSAGE_v3.33.1.md`
