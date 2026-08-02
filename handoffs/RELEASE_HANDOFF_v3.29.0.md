# RELEASE HANDOFF — v3.29.0

**Prepared**: 2026-08-01 · **State**: PUBLIC RELEASE — POST-TAG CORRECTIONS ACTIVE ON `main`

> v3.29.0 is public. Do not report it as delivered from this artifact. Gate 4 must verify received state
> and ordinary downstream Codex behavior. Corrections #5–#8 repair receiver payload, validation, and
> surfaces on `main`; they do not prove that a receiving seat applied them.

## Breaking Changes

None. Claude skill paths remain. Codex-native exposure is additive; literal `/aget-*` compatibility remains
out of scope until v3.30.

## Upgrade Guide

Read `release-notes/v3.29.0.md`, pin the immutable v3.29.0 tag for the original payload, then read
`handoffs/CORRECTIONS_v3.29.0.md` and use the corrected delivered-files manifest from `main`. Apply every
applicable manifest path—including the M-3.29-1 POSITION document—update the seat version pins, preserve
instance extensions, and run the receiving seat's own health/tests. Do not change Codex project trust as
part of migration.

For a seat already at v3.29, correction adoption is **correction-only**: compare the current `main`
manifest hashes, copy only changed paths, run their receiving-seat checks, and commit only those paths.
Do not replay the full migration, append a duplicate migration-history row, or rewrite unrelated version
surfaces to consume one correction. The manifest's `pin_edits` list names the release-owned pins. If a
fleet maintains additional local version fields, select them by that fleet's declared schema meaning;
never edit “the first semver-shaped field.” An unknown schema is unmeasurable and requires owner routing,
not a positional guess (for example, a template-provenance version is not necessarily the seat version).

## Deployment Requirements

Use `DEPLOYMENT_SPEC_v3.29.0.yaml` and `handoffs/DELIVERED_FILES_v3.29.0.yaml`. Confirm the three native
Codex skills resolve, the study-topic contract exposes purpose/recency/external bounds, and no private
manager paths or identifiers entered the public payload.

## Smoke Test

1. `python3 scripts/validate_codex_skill_discovery.py --json` → PASS.
2. Run study-topic with `--purpose pre-release --include-sessions --include-instruments --json`; confirm at
   least one matching artifact has `purpose_boost=2.0`, session day basis is present, and the work-repo/web
   scope note is present.
3. Run the receiver's contract suite; no new failures relative to baseline.
4. On one downstream v3.29 Codex seat, discover and invoke one exposed workflow and exercise save-state
   recovery. Record this separately as Gate 4 evidence; producer rehearsal cannot substitute.

## Context for External Fleets

v3.29.0 is an additive minor release. External fleets do not need access to the framework manager's
private planning or decision ledgers: use the public release notes, delivered-files manifest, deployment
specification, and this handoff. Supported-client conformance is limited to Claude Code and Codex CLI.

Codex-native support means discovery through `.agents/skills/`; it does not promise literal `/aget-*`
commands. Preserve local extensions and trust settings, and treat producer state, public availability,
received version, and ordinary downstream behavior as four separate facts. A successful tag fetch or
version bump does not establish discovery/invocation/recovery behavior.

Post-tag release corrections are disclosed at `handoffs/CORRECTIONS_v3.29.0.md` on `main`; immutable tags
are never moved to hide a release-time documentation defect. Payload remains tag-pinned, while corrected
migration instructions and correction payload hashes are read from `main`.

The remote entrypoint is `handoffs/REMOTE_MIGRATION_MESSAGE_v3.29.0.md` on `main`, not the tagged copy.
It requires a composite packet receipt (tag object + peeled commit + resolved `main` commit + delivered-
manifest SHA-256). Any later correction invalidates dependent packet-currency claims until receivers
re-derive them against the new identity. Remote pilot readiness and fleet fan-out readiness are separate:
fan-out remains on HOLD until Gate 4 has a qualifying cold-context behavior receipt.

## Rollback

Restore the prior version/tag and version pins; remove the `.agents/skills` exposure links; restore the prior
study-topic script. No data schema rollback is required.

## Pilot tracking

| Seat | v3.29 received state | Native discovery/invocation/recovery | Evidence |
|---|---|---|---|
| framework producer | v3.29 at release Gate 2 | producer tests PASS; not downstream evidence | release-manager Gate 2 receipt |
| downstream v3.29 receiver | verified 2026-08-02 | cold-context Codex discovery/invocation/recovery still pending | verified at source by release manager; private receiver identity not published |
