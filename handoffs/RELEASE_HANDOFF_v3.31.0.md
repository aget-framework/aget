# RELEASE HANDOFF — v3.31.0

**Version**: 3.31.0 · **Type**: minor · **Prepared**: 2026-08-15 · **State**: CANDIDATE
**Producer**: framework manager · **Consumer**: supervisor-class seats coordinating fleet upgrade
**Release notes**: `release-notes/v3.31.0.md`

## Summary

Five verification instruments promoted to canonical, each with its test, plus the accumulated fixes
above v3.30.0. Version coherence across all fourteen release repositories. Modest by design: these are
tools that already worked and were held back only by the absence of a promotion step.

## Breaking Changes

**None.** All five instruments are additive. No existing command, path, or contract changes behaviour.

## Upgrade Guide

1. Pull the tag: `git fetch --tags && git checkout v3.31.0`
2. Nothing to migrate — no configuration, schema, or path changes.
3. The five new instruments live in `scripts/` and are standalone; each supports `--help`.
4. Confirm your seat reads `3.31.0` in `.aget/version.json`.

## Deployment Requirements

- Python 3 with the standard library only. **None of the five instruments imports a third-party package
  or a sibling script**, so the missing-companion failure mode does not apply to them.
- No new services, credentials, or network access.

## Smoke Test

From a clean checkout at the tag:

```bash
for s in check_skill_route_contract check_deprecation_removals release_cadence_gap \
         validate_changelogs validate_initiative_proposal; do
  python3 scripts/$s.py --help >/dev/null && echo "ok   $s" || echo "FAIL $s"
done
python3 -m pytest tests/test_skill_route_contract.py tests/test_release_cadence_gap.py \
  tests/test_validate_changelogs_inventory.py tests/test_validate_changelogs_zero_denominator.py \
  tests/test_validate_initiative_proposal.py tests/test_deprecation_removal_check.py -q
```

**Expected**: 5/5 `ok`; suite green. Producer result on a clean consumer-vantage clone: **5/5 running,
47 passed / 2 skipped**. The skips are correct — they are portability guards standing down where a
consumer's corpus legitimately differs, and they still fail where it is present but wrong.

## Context for External Fleets

**Read the "Known limitations" section of the release notes before wiring any of these into CI.** Three
of the five have disclosed defects. Most consequential for automation:

- `check_skill_route_contract` **fails on a clean checkout** — it correctly reports routes that shipped
  skills name but that are not shipped. That is the tool working, not breaking, but it means adding it
  to a build without a baseline produces an immediate red.
- `check_deprecation_removals` reports `UNAVAILABLE` here because the registry it reads is not shipped,
  and its `--advisory` flag does not force exit 0 despite its help text.
- `release_cadence_gap` uses exit 1 for both "breached" and "could not find the repository".

## Rollback

Instruments are additive and standalone; removing the five files and their tests returns the repository
to v3.30.0 behaviour. No state, schema, or configuration is written by installing them.

## Pilot tracking

| Seat | Received | Conformant | Behavioural | Bundle digest | Notes |
|---|:--:|:--:|:--:|---|---|
| *(unassigned)* | — | — | — | — | Acceptance bar for this cycle is **one** downstream confirmation, per principal ruling 2026-08-15 |

**Not yet populated.** Publication has not occurred.

## Status disclosure — read before treating this as a shipped release

This handoff is prepared at **candidate** state. As of preparation:

- **Nothing is published.** All fourteen public repositories read `3.30.0`; the fourteen `v3.31.0` tags
  exist locally and are unpushed.
- **Publication is gated** on a separate, principal-owned sensitivity ruling covering private content in
  the public repositories. That exposure predates this release, is not caused by it, and is not
  remediated by it.
- The independent cross-engine verification leg specified for this cycle **did not run**. It is recorded
  as a deviation in the engine receipt rather than omitted.

A consumer reading this document at the tag should treat the pilot table's emptiness as accurate, not as
an oversight.
