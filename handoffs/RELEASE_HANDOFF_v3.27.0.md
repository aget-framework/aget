# RELEASE_HANDOFF v3.27.0 — Finish & Verify

**Released**: 2026-07-18 · **Type**: minor · **Breaking**: no
**Deployment contract**: `DEPLOYMENT_SPEC_v3.27.0.yaml` (tag-reachable; M-3.27-1..8, **first binding `executed_surface` declarations**)
**Migration guide**: `handoffs/REMOTE_MIGRATION_MESSAGE_v3.27.0.md` — its **§Behavioral Smoke is MANDATORY** (Rung 4, SOP_fleet_migration v1.7.0 Gate 4.0)
**Corrections since tag**: `handoffs/CORRECTIONS_v3.27.0.md` — created at first post-tag fix; ALL guidance surfaces point there (single-surface contract, SOP v1.57)

## Key changes (consumer-facing)

1. **Rung 4 is now the bar**: after payload lands, run the smoke probes + your own test suite + executed-surface parity. Receipt verification alone no longer confirms a migration.
2. `check_initiatives.py`: CIS-008 measures capability share among Achieve-typed ACTIVE only; CIS-010 surfaces EC tick-state. Expect honest reds where the old form was silent.
3. `check_config.py`: single-slash absolute permission rules are now named as dead rules with a rewrite route.
4. `close_gate_check.py`: dual Status/Plan_Status terminal-ness disagreement blocks a close.
5. `wind_down.py`: defers to a recent close-session file (<30min) instead of stamping a stub over it.
6. AGENTS.md gains the Transactional Execution section + workspace/ committing-intent convention.
7. Universal skill set: your archetype's full set ships; `validate_archetype_skills` should read clean post-migration.

## Context for External Fleets

- Pin template-derived agents to the template tag (`v3.27.0`); post-tag fixes live in `handoffs/CORRECTIONS_v3.27.0.md` on `main` — apply its rows on top of the tag payload (single-surface contract, new this release).
- Migration confirmations now require **behavioral evidence** (Rung 4): run the dispatch's §Behavioral Smoke on the executed surface + your own test suite — a disk receipt alone no longer confirms.
- M-3.27-4 is seat-conditional (framework-seat tool) — skip if your seat lacks the config checker; see CORRECTIONS row 1.
- Verify features at the OPERATIVE path your agent config invokes (dual-basename caution, carried from v3.25/26).

## Upgrade

Standard wave protocol per REMOTE_MIGRATION_MESSAGE (Migration Target block names **v3.27.0** explicitly — never infer). Rollback: severity-routed per SOP §Defect-Response Routing.

## Pilot tracking

| Agent (role) | Version | Date | Behavioral-probe evidence (Rung-4 bar — REQUIRED, disk receipt alone insufficient) | Source |
|---|---|---|---|---|
| framework seat (producer) | 3.27.0 | 2026-07-18 | self-migration pre-ship; CIS-010/CIS-008 live runs = the probes | this handoff |
| supervisor seat (pilot) | 3.27.0 | 2026-07-18 | **Rung-4 CONFIRMED**: probes 1/2/4/5/6 PASS + probe 3 SKIP-recorded (seat-conditional, corrections row 1); 50/50 test suite vs pre-migration baseline; executed-surface parity verified (all invocations resolve to `scripts/`); 8/8 M-row detections at operative paths | pilot ACK artifact (supervisor `handoffs/ACK_framework_aget_v3.27.0_sup_pilot_evidence_2026-07-18.md`) + gmelli/aget-aget#1938 comment; stamped by framework 2026-07-18 after evidence verification |
| *(post-pilot)* full local fleet | 3.27.0 | 2026-07-18 | 31/31 seats same-day at the Rung-4 bar, 0 refusals; population verify 29/29 + behavioral sample; supervisor migration plan closed at rubric 14/15 | gmelli/aget-aget#1950 (migration report) + #1951 (experience) |
