# REMOTE MIGRATION — AGET v3.27.0 "Finish & Verify"

*(Template: TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.6.0)*

## Behavioral Smoke (MANDATORY — rung 4, SOP_fleet_migration v1.7.0 Gate 4.0)

| # | Payload feature (M-row) | Probe (run this) | Expected |
|---|---|---|---|
| 1 | M-3.27-3 | `python3 scripts/check_initiatives.py \| grep "Capability ratio"` | line mentions "Achieve-typed ACTIVE (D-27-A denominator…)" |
| 2 | M-3.27-3 | `python3 scripts/check_initiatives.py \| grep "EC tick-state"` | CIS-010 line renders (state PASS/WARN/N-A) |
| 3 | M-3.27-4 | `python3 scripts/check_config.py \| grep single_slash` | t3_single_slash_rules row renders |
| 4 | M-3.27-6 | `touch sessions/session_$(date +%F)_smoke.md && python3 scripts/wind_down.py; …cleanup` | guard line "recent session file … skipping stub" prints |
| 5 | always | `python3 -m pytest tests/ -q` | no NEW failures vs your pre-migration baseline |
| 6 | always | dual-basename check: for each M-row with `executed_surface`, confirm the config-invoked copy carries the payload | parity |

## Migration Target

- **Target version**: **v3.27.0** (explicit — never infer; inference resolves N-1)
- **Deployment contract**: `DEPLOYMENT_SPEC_v3.27.0.yaml` AT THE TAG
- **Payload source**: your template's `main` at tag v3.27.0

## Fleet Coordination

Dispatch grants in-session execution authority (headless seats: do not end "awaiting GO" — the ask-but-don't-wait trap). Waves per SOP_fleet_migration v1.7.0; V0.0 refuses target-less dispatches.

## Corrections since tag

Single surface: `handoffs/CORRECTIONS_v3.27.0.md` (exists only once a post-tag fix lands). If present at your migration time: apply every row on top of the tag payload. This message will NOT be edited with corrections.
