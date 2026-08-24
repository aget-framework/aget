# Release Handoff — v3.32.0 "Truthful Release Evidence"

**Version**: 3.32.0 · **Released**: 2026-08-23 · **Type**: corrective · **Breaking changes**: none
**Producer**: framework manager · **Consumer**: supervisor-class seats (fleet upgrade coordination)

## Summary

Two release-evidence controls were reporting wrongly at their shipped public subjects. Both are repaired.

1. **`release_cadence_gap.py`** silently substituted a different source when the named one did not resolve,
   and exited 0. Now `UNAVAILABLE` (exit 2), never substituted, never conflated with `BREACHED`. The
   winning resolution strategy is disclosed in the output. A Python 3.10 crash on terminal-`Z` tagger dates
   is fixed in the same area.
2. **`check_deprecation_removals.py`** had no public registry to read, so the default invocation exited 2.
   `governance/DEPRECATIONS.md` now ships, and the checker names the subject it measured.

## Upgrade Guide

Pull the release. No configuration change, no migration, no API change. Consumers of the cadence tool
should read `handoffs/REMOTE_MIGRATION_MESSAGE_v3.32.0.md` for the exit-code contract — in particular that
**exit 1 is not a verdict without valid JSON on stdout**.

## Scope, stated exactly

**Two product items.** Two further candidates were verified and are **carried forward, NOT delivered**:

| Item | State |
|---|---|
| `C-32-03` | Verified private candidate. No canonical counterpart; awaits a governed public name, path, and consumer. **Do not describe as delivered.** |
| `C-32-04` | Verified private fix. Public templates lack the cited surface; modernization is out of scope. **Do not describe as delivered.** |

## Release topology

Core plus **13 registered templates** (14 repos). **This cycle touches core only** — both repairs are
core-side scripts with no template counterpart. Zero template payload is a scope fact, not an omission.

## Known state at handoff — read before deploying

| Item | State |
|---|---|
| Value floor | **FAILED and OVERRIDDEN, not passed.** Locked Tier-1 carries zero V1=L3 rows; cleared by recorded exception. Fourth override this cycle |
| Independent review | **Budget unspent** at time of writing; one review is owed at the stable PR head |
| Python 3.10 verification | Repair is by construction; **execution on 3.10 was UNAVAILABLE at the producer seat** |

## Pilot Tracking

| Seat | Version confirmed | Behavioural proof | Date | Notes |
|---|---|---|---|---|
| *(pending)* | | | | Awaiting deployment |

**Deployment verification is a release-completion obligation, not a pre-publication blocker.** Producer
owns this artifact and the release execution; **fleet upgrade coordination is the supervisor's.**
