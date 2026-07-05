# RELEASE HANDOFF: v3.25.0 — "Grounded Entities & Trusted Releases"

**Date**: 2026-07-04 (Saturday)
**From**: Framework Manager
**To**: Fleet Supervisor (fleet upgrade coordination — L511 ownership boundary)
**Release**: https://github.com/aget-framework/aget/releases/tag/v3.25.0 (live)
**Tag**: `v3.25.0` · templates tagged + Release objects published (tag policy resumes at v3.25.0; the v3.9→v3.24 template-tag gap is documented, not backfilled)

---

## Summary

Balanced double-bill. **Capability pole**: AGET_ENTITY_DIMENSION_SPEC v0.1.0 (first URI-bound spec) + its 16-V-test validator; AGET_FRICTION_SPEC v1.0.0 Active (forward-validated); aget-ask v1.0.0 production. **Integrity pole**: "RELEASED" is computed, never asserted — binary DoD gate wired into the close path, closure-substance detection, received-state V-tests, reliance self-attestation at wake-up. **Repairs**: study_topic.py active-plan detection + knowledge/ontology search scope. **Conformance model change**: templates are reliance-only (D-1) — a `@aget-canonical-specs` reference line, no local spec copies.

## Upgrade guide

- **No breaking changes** — additive + repair; rollback = file-copy restore from your v3.24.0 tag.
- Payload: overwrite 5 framework scripts (`study_topic.py`, `capture_friction.py`, `wake_up.py`, `health_check.py`, `close_gate_check.py`), version pins, the `@aget-canonical-specs` line; optional aget-ask (tier {O}).
- Full guide: `handoffs/REMOTE_MIGRATION_MESSAGE_v3.25.0.md` (at this tag) — read its operative-path caution and lineage-baseline note before fanning out a fleet.
- Deployment contract: `DEPLOYMENT_SPEC_v3.25.0.yaml` at repository root on **main** (same-day back-fill; NOT tag-reachable — see disclosure below).

## R-REL-038 Disclosure (same-day back-fill)

`DEPLOYMENT_SPEC_v3.25.0.yaml` was absent at tag time — an R-REL-038 lapse with no waiver, caught same-day by an independent downstream prerequisite check (the consumer gate working as designed). Disposition: back-fill owed (the reliance-only model governs template conformance, not deployment specs). Root cause: the computed close gate did not enumerate a DEPLOYMENT_SPEC row (enumeration gap); the row plus a full row-completeness audit against the SOP's BLOCKING set landed 2026-07-04/05. Fetch the spec from `main`, not the tag.

## Pilot tracking (deploy-verify bar = supervisor + self)

| Seat | Version | Deployed | Confirmed |
|------|---------|----------|-----------|
| Framework Manager (author) | 3.25.0 | 2026-07-04 | ✅ self-migration + smoke |
| Fleet Supervisor (non-author) | 3.25.0 | 2026-07-04 | ✅ evidence relay, received-state verified from disk 2026-07-05 |

Fleet deployment beyond the pilot pair completed under supervisor coordination (payload-lean, adoption carve-outs honored, local patches preserved via lineage-aware divergence checks).

## Deprecations

None this cycle.

## For external fleets

- Templates are tagged and carry Release objects from v3.25.0 forward — pin template-derived agents to the template tag.
- If your fleet's agents predate template tagging, do NOT classify divergence against canonical tags — build a known-good hash set from your deployment lineages first (see the migration message's lineage-baseline note).
- Verify features at the OPERATIVE path your agent config actually invokes, not just the conventional `scripts/` path — a marker-complete copy can be inert if wiring points elsewhere.
