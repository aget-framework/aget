# Release Handoff — AGET v3.37.0

**Date**: 2026-10-17. Publication is evidenced by the annotated tag `v3.37.0` and its GitHub Release object. Read the tag's peeled commit with `git rev-parse 'v3.37.0^{commit}'`; a file inside the tagged commit cannot name it.

## Release Summary

From v3.36.0, deploy the receiver migration fixes, receiver adoption kit, Ubuntu 24.04 CI pin, compiled-cache payload gates, and wind-down health reporting improvements. Read `release-notes/v3.37.0.md` and `DEPLOYMENT_SPEC_v3.37.0.yaml`. The source for copy lists is the final tag tree; no separate delivered-files manifest is published.

## Context for External Fleets

The supervisor's migration kit is copied from `scripts/migration_kit/` in the core clone. It is not installed by a template upgrade. Its batch procedure is in `sops/SOP_fleet_migration.md` v1.11.0 and its session guide is `scripts/migration_kit/BATCH_SESSION.md`. Set the real source and target releases explicitly; older internal schema and receipt labels do not select the target release.

The final authority rule is: scope-only principal approvals are refused as launch authority, whether recorded in the active ledger or preserved in the permanent, append-only `data/scope_archive.jsonl` beside the ledgers; old-format scope records block launches until retired. Record scope instructions, preserve their evidence and type launches as separate prompts. Push authority remains a separate act. See Known Items before retiring any ledger or record.

## Script Deployment

| Recipient | Deploy from the pinned core or template tree | Verify |
|---|---|---|
| Supervisor | Entire `scripts/migration_kit/` and the current fleet migration SOP | Declared dependencies; explicit release target; adoption policy and skew check; post-apply halt check (SOP Part B step B7a) |
| Receiver running core or template tests | `tests/conftest.py` and `tests/test_conftest_git_env_isolation.py` (template item M-3.37-6) | Inherited git location is cleared before collection; scratch repositories remain isolated |
| Receiver using wind-down | `scripts/wind_down.py` and `tests/test_wind_down_health_timeout.py` from core or templates; `docs/protocols/WIND_DOWN_PROTOCOL.md` from core only | Timeout configuration, distinct TIMEOUT/ERROR and real observations |
| Template producer | `scripts/instantiate_template.py`, `scripts/deploy_skill.py` and the documented release gates | Fleet gate: each template's complete tree at the tag; pre-tag gate: committed tree under its working directory or `--cwd`; inspected trees contain no compiled caches |
| Repository CI maintainer | Approved workflow changes from the relevant core or template tree | `ubuntu-24.04`, checkout v7 and setup-python v7; actual hosted result |

Use the corresponding published template tree for receiver template payloads and preserve local extensions. Core changes alone do not establish delivery in any template repository.

## Breaking Changes

No public interface removal is declared. Invalid launch authority, old-format scope records and compiled-cache payloads now receive stricter refusals. Observation-free health results report UNKNOWN but still exit 0 with `clean_close` true; only health status `error` makes wind-down exit 2. Read the Health Gate line.

## Removals

No interface removals. Compiled caches are excluded from payload copies; inspect and remove already tracked caches before producing release tags.

## Deployment Requirements

Python 3.10+ is the core minimum; the migration kit test-body witness requires Python 3.12+. The kit authority and session tools read Claude Code records. Other command-line tools have no new migration outcome evidence in this release.

## Upgrade Guide

### Requirement

The `python3` your supervisor session uses must import PyYAML and pytest (the kit runs both); check with `python3 -c "import yaml, pytest"`.

Complete the [migration message's setup and seeding steps](REMOTE_MIGRATION_MESSAGE_v3.37.0.md#prerequisites-complete-before-seeding), including adoption policy review, the release-age gate, the skew check and archive seeding, from the supervisor root.

In `sops/SOP_fleet_migration.md`, complete the remaining **Set up once per release** rows (including run root, supervisor name, batch session settings, batch-line prefix and transcripts), the batch-folder paragraph and **The migration's record** under **Kit Batch Procedure**, and **Part A — per-release inputs**. After seeding and before any Wave-1 work, follow **Wave Sequencing / Wave-0 Supervisor Self-Upgrade**, steps 1–3, for this supervisor's upgrade. The supervisor does not go through Part B as a member of its own batch. Then start Wave 1 with the pilots and run **Part B — the fixed procedure**, steps B0–B13, in order.

Use the [migration message's v3.37.0 notes for Part B](REMOTE_MIGRATION_MESSAGE_v3.37.0.md#v3370-notes-for-part-b) at their named steps and observe the SOP's declared Wave-1 soak before Wave 2.

## What was shown and what was not

The candidate contains regression tests for these changes. Attach the builder's actual local validation receipt; this handoff does not claim a final-commit test result. Hosted CI, public release availability, template tag contents, live receiver acceptance, fleet close-out and Ubuntu 26.04 qualification remain unverified by this release-files build.

## Known Items

Not in this release: propagation of the repaired close-authorization guard to the templates is deferred again to the next release, owned by the framework's release manager; until a template tag carries the repair, follow the consumer action in `handoffs/CORRECTIONS_v3.35.0.md` rows 4 and 5.

- The test-body witness can misclassify completion for injected skips, plain-closure decorators and `subTest` skips; see [Known limitations and disclosures](../release-notes/v3.37.0.md#known-limitations-and-disclosures), including the payload and health limitations.
- The kit changes only the root `@aget-version` line; it does not update `@aget-canonical-specs`. Verify the version against 3.37.0 and record the unchanged specification pin. Change that specification pin in a separate reviewed commit outside the kit batch and after-run window, then verify it against the intended release. Editing it inside that window fails the protected-file checks.
- Kit halt_check checks only root AGENTS.md/CLAUDE.md; a near-match-all receiver declaration can pass validation; pins are not bound to the target release. Inspect nested instructions, local overrides and rules separately.
- Scope evidence survives retirement in the permanent, append-only `data/scope_archive.jsonl`, beside the ledgers. The gate checks every ledger in the data folder and its archive anchor (row count and rolling hash). It refuses a missing, shortened or mismatched archive, a moved anchor, and symlinked ledger or archive paths. Commit the archive and ledgers together; never delete or edit the archive.
- A scope instruction that was never recorded cannot be recognised — type launches as separate prompts. The ledgers and archive are one trust domain: consistent edits of both, or rolling back the whole data folder, can remove the evidence. The kit locates its code directory by resolving symlinks; a replaced code directory pointing at another kit's data is outside the protection. On case-insensitive disks, seed with the exact-case path.
- Template symlink containment: a tracked symlink pointing outside a template is kept. Filtering compiled caches does not establish link containment.
- Ubuntu 26.04 qualification not yet done. Hosted CI with the new action majors is a separate validation step.
- Wind-down timeout drains pipes for at most five additional seconds; descendants outside the process group may survive. TIMEOUT does not by itself fail close.
- The Python 3.12+ test-body witness requirement and unrepaired earlier kit limitations still apply. Read `release-notes/v3.36.0.md` for the inherited release-specific labels, validation commands, payload lists and close-out limitations.

## Rollback

Never reset or rewrite shared history, and never move published tags. Revert a committed migration with `git revert`. Before commit, restore only the recorded migration path set from the saved baseline. Re-run baseline tests and wake-up, and record ROLLED_BACK or HOLD. Reverting the supervisor's kit update does not delete its records, durable migration archives or temporary run directories.

## Completion Response

Report the source and target version, baseline and final commits, tree state, paths deployed and extensions preserved. Include actual suite summaries, body skips and inconclusive checks, B7a verdicts, required hosted CI on the exact published commit, and wake-up/wind-down results. Record every refusal verbatim, additional document needed, producer intervention and command handed to the principal. A supervisor also records the target configuration, register pin, batch outcomes, scope evidence retained, separate launch/push prompts, unresolved members and close-out status.

## Fleet Action Required

Follow the migration message's setup and the SOP's adoption checks, **Wave Sequencing / Wave-0 Supervisor Self-Upgrade**, steps 1–3, and Part B, including the declared Wave-1 soak before Wave 2. A receiver receipt is evidence to review; only the producer's acknowledgment closes the loop.

## Pilot Tracking

TO CONFIRM: final core identity, publication, template availability, hosted CI and live pilot receipt. Prior-release closure and the required external receiver receipt or explicit release exception remain separate publication decisions.

## Acknowledgment

Return the completion response with PASS, HOLD or ROLLED_BACK and the reasons. This candidate handoff itself does not establish downstream acceptance.
