# RELEASE HANDOFF: v3.26.0 — "Signals & Contracts"

**Date**: 2026-07-11 (Saturday)
**From**: Framework Manager
**To**: Fleet Supervisor (fleet upgrade coordination — L511 ownership boundary)
**Release**: https://github.com/aget-framework/aget/releases/tag/v3.26.0
**Tag**: `v3.26.0` · canonical + 13 templates tagged with Release objects

---

## Summary

The release hears its consumers and hardens its contracts. **Signals pole**: wake-up release-currency notice (behind → one line, current → silent); extension hook points for `health_check.py` + `study_topic.py` (the fork-pressure halt class ends); supervisor-relay issue routing with a principal-supervised direct path. **Contracts pole**: three-state check reporting (PASS/FAIL/UNREACHABLE), terminal-state vocabulary (IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE and kin), a study-topic search contract with a declared surface manifest, the verify-before-claim coverage matrix with two gates landed (`/aget-file-issue` pre-filing probes; `/aget-close-project` has-it-run), the tag-payload coherence gate, permission-QUALITY checking, and the deprecation registry's first exercised N-2 rehearsal. **Repairs**: the v3.25-payload defect trio (wake-up session glob, manifest-checker paths, close-gate independence-WARN restore).

## Upgrade guide

- **No breaking changes** — additive + repair; rollback = file-copy restore from your v3.25.0 tag.
- Payload: 5 framework-script refreshes + close-project skill refresh + version pins; file-issue/record-lesson skill refreshes optional this cycle.
- Full guide: `handoffs/REMOTE_MIGRATION_MESSAGE_v3.26.0.md` (at this tag) — note its Migration Target block: dispatches name v3.26.0 explicitly, never an inferred N-1.
- Deployment contract: `DEPLOYMENT_SPEC_v3.26.0.yaml` at repository root — **tag-reachable this cycle** (the v3.25.0 same-day-back-fill lapse is closed; the row-completeness audit that mandates it shipped in this release).

## Pilot tracking (deploy-verify bar = supervisor + self)

| Seat | Version | Deployed | Confirmed |
|------|---------|----------|-----------|
| Framework Manager (author) | 3.26.0 | 2026-07-11 | ✅ self-migration pre-ship (R-REL-006-01) + protocol verification + smoke |
| Fleet Supervisor (non-author) | 3.26.0 | 2026-07-11 | ✅ ACK relay `ACK_framework_aget_v3.26.0_sup_pilot_evidence_2026-07-11.md` (payload 6/6 sha-verified at tag, 8/8 M-row detections at operative paths, conformance-then-bump, manifest add-list + porcelain cross-check, smoke suite) + received-state re-verified from disk by framework seat same day (version.json 3.26.0) — L656 satisfied same-day; 3 payload findings relayed (M-3.26-6 template lag → #1871 pre-filed; study_topic is_active vocabulary → #1856 thread; record-lesson canonical gap → fixed on main same day) |

## Deprecations

- **DEP-PRETAG-SH-001**: `scripts/check_pretag_inventory.sh` deprecated in favor of the `--pre-tag` successor. All five R-DEP-010 fields in the registry (`governance/POLICY_deprecation.md`); runtime warning live; carried v3.27, removed v3.28. First rehearsal of the N-2 policy (R-DEP-020..023) adopted this release.

## Known residuals (disclosed, not blocking)

- Template copies of `/aget-file-issue` structurally lag canonical (pre-routing-mode shape); refresh staged for the next cycle's propagation batch — adopt from canonical directly if wanted sooner.
- **Template tags ship `check_skill_reliance_manifest.py` one delta behind** (three-state UNREACHABLE wiring missing → M-3.26-6 detection fails at template tags; found by the first consumer sweep, 2026-07-11 same-day). Fixed on every template's `main` same day, disclosed per-repo. **Pin-to-template-tag guidance is amended for this one script**: fetch it from the template's `main` or canonical `aget/scripts/` at tag.
- Interaction-channel pattern (`docs/patterns/PATTERN_interaction_channel.md`) ships as substrate; template/fleet promotion is pilot-gated (non-author validation first).
- The public-surface audit's pre-existing corpus findings (legacy backup dirs in template repos, historical docs) are a recorded cleanup backlog, not v3.26 regressions; this cycle's own delta was scrubbed clean pre-push.

## Context for External Fleets

- Pin template-derived agents to the template tag (`v3.26.0`).
- Migration dispatches SHALL name their target version explicitly (Migration Target block, mandatory from this release's template v1.5.0) — a dispatch without one gets a discovery answer, never an inferred N-1.
- Verify features at the OPERATIVE path your agent config actually invokes (carried caution from v3.25.0).
