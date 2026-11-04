# Release Handoff — AGET v3.37.1

**Release type**: patch on v3.37.0 · **Planned date**: 2026-11-04 · **Previous release**: v3.37.0

## Release Summary

One fix: the migration kit for supervisors no longer waits seven days before a new release may be adopted. With no adoption policy file, `adoption_policy.py --check-age` now reports `ADOPT NOW` on the day a release is published. The ruled default is 0; v3.37.0 disclosed the 7-day value as a correction (`handoffs/CORRECTIONS_v3.37.0.md`, row 2, now marked fixed).

## Context for External Fleets

Templates change only their version identity (`.aget/version.json`, the `AGENTS.md` pins, `CHANGELOG.md`, `README.md`). The fix is in the core framework's `scripts/migration_kit/`, which is not a template payload.

## Script Deployment

No session script changes. Copy `scripts/migration_kit/` again from a core clone at `v3.37.1` into your supervisor repository, replacing the v3.37.0 copy, and commit it naming the clone's commit.

## Breaking Changes

None.

## Removals

None.

## Deployment Requirements

Unchanged from v3.37.0 (`DEPLOYMENT_SPEC_v3.37.1.yaml`).

## Upgrade Guide

1. Verify the annotated tag `v3.37.1` and its peeled commit: `git rev-parse 'v3.37.1^{commit}'`.
2. Re-copy the kit as above. A `min_release_age_days: 0` workaround set under v3.37.0 may stay or go; the result is the same.
3. Check: `python3 scripts/migration_kit/adoption_policy.py --show` prints `"min_release_age_days": 0` when nothing else sets it.

## What was shown and what was not

Shown before release: an automated clean install of the supervisor template plus the kit, with no policy file, reported `ADOPT NOW` for a release published that day (v3.37.0 reported `DO NOT ADOPT YET`); a patch without `--fixes-me` was still held; a release 8 days old was adopted either way; the core suite showed no new failures against v3.37.0. Not shown: a person following the steps, a receiver fleet's migration with this kit, hosted CI on the published commit (recorded at publication).

## Known Items

v3.37.0's known items stand (`handoffs/CORRECTIONS_v3.37.0.md`), except row 2. The supervisor template's quick start asks you to set your own `domain`, and one template test then expects `supervision`; tracked separately.

## Rollback

Set `min_release_age_days` in your policy file to the wait you want, or keep the v3.37.0 kit with its documented workaround.

## Completion Response

Report the receiver's source revision, the `--show` reading and the check-age result for the release you adopt.

## Fleet Action Required

Supervisors using the kit: re-copy it. Others: none.

## Pilot Tracking

| Pilot | Version deployed | Verified at receiver revision | Result |
|---|---|---|---|
| (none yet) | | | |

## Acknowledgment

Producer-written; never counts as receiver acceptance.
