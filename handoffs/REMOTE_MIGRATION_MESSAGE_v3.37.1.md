# Migration Message: v3.37.0 to v3.37.1

**Date**: 2026-11-04
**From**: AGET Framework Manager
**To**: Remote Fleet Supervisors
**Target Version**: 3.37.1
**Previous Release**: v3.37.0
**Migration Path**: v3.37.0 to v3.37.1. From earlier versions, follow `handoffs/REMOTE_MIGRATION_MESSAGE_v3.37.0.md` with target 3.37.1; this patch adds no steps.
**Breaking Changes**: None.
**Release identity**: Publication is evidenced by the annotated tag `v3.37.1` and its GitHub Release object. Read the tag's peeled commit with `git rev-parse 'v3.37.1^{commit}'`.
**Currency note**: Read this message and any corrections from the producer's main branch. Check release availability and the tag's peeled commit before acting.

## Migration Target

Set `to` in `.aget/migration_target.json` to `3.37.1`.

## What's New in v3.37.1

- The migration kit's default `min_release_age_days` is 0. With no adoption policy file, the release-age check reports `ADOPT NOW` on publication day. Your own declared wait, the patch rule (`--fixes-me`) and the Wave-1 soak still apply.

## Upgrade Guide

1. Re-copy `scripts/migration_kit/` from a core clone at `v3.37.1` into your supervisor repository and commit it, naming the clone's commit.
2. Run `python3 scripts/migration_kit/adoption_policy.py --show` and confirm `"min_release_age_days": 0` (or your own declared value).
3. Run `python3 scripts/migration_kit/adoption_policy.py --check-age --published <release date> --release 3.37.1 --fixes-me` only if this fix applies to your fleet: it applies if you use the kit with no declared release-age wait.
4. Continue as in the v3.37.0 message; nothing else changes.

## Known Gaps

As in `handoffs/CORRECTIONS_v3.37.0.md`, except row 2, which this release fixes.

## Report Back

Your source revision, the `--show` reading and the check-age result.

## Rollback

Restore your previous `scripts/migration_kit/` copy, or declare the wait you want in `.aget/adoption_policy.json`.

## References

`release-notes/v3.37.1.md` · `DEPLOYMENT_SPEC_v3.37.1.yaml` · `handoffs/RELEASE_HANDOFF_v3.37.1.md` · `handoffs/CORRECTIONS_v3.37.0.md`
