# v3.32.0 — Remote Migration Message

**Version**: 3.32.0 · **Released**: 2026-08-23 · **Type**: corrective

## Breaking Changes

**None.**

## Upgrade Guide

Pull the release. No configuration change, no data migration, no API change.

If you consume `release_cadence_gap.py` programmatically, note the exit-code contract, which is now
enforced rather than implied:

| Exit | Meaning |
|---|---|
| 0 | OK |
| 1 | `BREACHED` — the subject **was read** and exceeds the cadence rule |
| 2 | `UNAVAILABLE` — the named subject could not be read. **Never substituted** |

**Do not read exit 1 as a verdict on its own.** A crash also exits 1. Require non-empty valid JSON on
stdout before interpreting it as `BREACHED`.

## Deployment Requirements

Python >= 3.10. Terminal-`Z` git tagger dates parse correctly on 3.10 as of this release.

## Smoke Test

```bash
python3 scripts/release_cadence_gap.py --json        # exits 0/1/2, always emits JSON
python3 scripts/check_deprecation_removals.py --json # resolves governance/DEPRECATIONS.md
```

Both should emit JSON naming the subject they measured.

## Rollback

Revert-on-`main`. History rewrite is barred by the `non_fast_forward` rule, so rollback is a revert
commit rather than a force-push.
