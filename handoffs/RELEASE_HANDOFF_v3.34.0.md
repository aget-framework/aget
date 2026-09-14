# Release Handoff — AGET v3.34.0

Target version: 3.34.0. Prepared 2026-09-13; publication and adoption unverified.

## Summary

This release carries fifteen selected outcomes described in [the release notes](../release-notes/v3.34.0.md). Consume the exact public core and matching-template commits, preserve receiver state, and exercise the capability actually credited to this upgrade. Review the disclosed shipped-test coverage shortfall and inherited lint backlog before accepting.

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
- [ ] Read `DEPLOYMENT_SPEC_v3.34.0.yaml` from the peeled core tag.
- [ ] Diff every selected destination and preserve receiver-owned extensions.
- [ ] Prepare an exact rollback reference before mutation.

## Deployment Requirements

Python 3.10 or later, immutable tag-bound sources, a matching archetype template, a receiver baseline,
and a rollback stable cut are required. Missing evidence is `HOLD`, never an inferred pass.

## Upgrade Guide

Run this block as one Bash script; stop on any failed command. Both source checkouts must be clean, including untracked files, before selecting the tag-bound bytes. Preserve any existing edits separately under your own governance; this guide does not discard them.

```bash
set -euo pipefail
export SOURCE=/path/to/aget-v3.34.0
export TEMPLATE=/path/to/matching-template
export AGENT=/path/to/receiving-agent

test -z "$(git -C "$SOURCE" status --porcelain --untracked-files=all)"
git -C "$SOURCE" fetch --tags origin
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.34.0)" = tag
CORE_SHA=$(git -C "$SOURCE" rev-parse --verify 'v3.34.0^{commit}')
git -C "$SOURCE" checkout --detach "$CORE_SHA"
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$CORE_SHA"
test -z "$(git -C "$SOURCE" status --porcelain --untracked-files=all)"
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["aget_version"])' "$SOURCE/.aget/version.json")" = 3.34.0
test -f "$SOURCE/DEPLOYMENT_SPEC_v3.34.0.yaml"

test -z "$(git -C "$TEMPLATE" status --porcelain --untracked-files=all)"
git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.34.0)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse --verify 'v3.34.0^{commit}')
git -C "$TEMPLATE" checkout --detach "$TEMPLATE_SHA"
test "$(git -C "$TEMPLATE" rev-parse HEAD)" = "$TEMPLATE_SHA"
test -z "$(git -C "$TEMPLATE" status --porcelain --untracked-files=all)"

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

Required: no new receiver test failures, wake-up reports 3.34.0, and each selected path meets its
tag-pinned postcondition. Preserve raw output; do not normalize an unavailable predicate into pass.

## Rollback

Never reset or force-push shared history. Revert a committed migration with `git revert`; before commit,
restore only the recorded migration path set from `BEFORE_SHA`. Re-run the baseline tests and wake-up,
preserve failure evidence, and record `ROLLED_BACK` or `HOLD`.

## Receiver Receipt Contract

The receiver authors its receipt after exercising the installed subject. Record core and matching-template annotated tags and peeled full commits; deployment-spec blob; ordered payload manifest digest; receiver before/after commits; selected paths and their digests; commands, raw observations, timestamps, host and authorized operator; limitations and rollback reference.

A receipt counts as returned only after acknowledged transmission and verification at its source revision. BEHAVIOUR_VERIFIED qualifies only when the credited capability and an exercised rejection path pass and no blocking delivery defect remains; do not rename it ACCEPTED. A producer-authored statement about a receiver is not receiver acceptance. PENDING, HOLD, simulation and installation-only results do not establish delivery.

## Pilot Tracking

No qualifying receiver receipt is recorded by this prepared artifact. The receiving fleet owns commissioning an available authorized operator and returning its own evidence.
