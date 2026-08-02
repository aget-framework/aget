# RELEASE HANDOFF — v3.29.0

**Prepared**: 2026-08-01 · **State**: PRE-PUSH CANDIDATE

> Do not report this release as public or delivered from this artifact. Gate 3 must verify the public chain;
> Gate 4 must verify received state and ordinary downstream Codex behavior.

## Breaking Changes

None. Claude skill paths remain. Codex-native exposure is additive; literal `/aget-*` compatibility remains
out of scope until v3.30.

## Upgrade Guide

Read `release-notes/v3.29.0.md`, pin the v3.29.0 tag after it is public, apply the complete delivered-files
manifest, update the seat version pins, preserve instance extensions, and run the receiving seat's own
health/tests. Do not change Codex project trust as part of migration.

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
are never moved to hide a release-time documentation defect.

## Rollback

Restore the prior version/tag and version pins; remove the `.agents/skills` exposure links; restore the prior
study-topic script. No data schema rollback is required.

## Pilot tracking

| Seat | v3.29 received state | Native discovery/invocation/recovery | Evidence |
|---|---|---|---|
| framework producer | pending Gate 2 migration | producer tests PASS; not downstream evidence | Gate 0 receipt |
| downstream v3.29 Codex seat | pending Gate 4 | pending Gate 4 | must be verified at source |
