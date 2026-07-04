# Remote Fleet Migration — v3.25.0 "Grounded Entities & Trusted Releases"

**From**: aget-framework release management · **Date**: 2026-07-04 · **Applies to**: any AGET instance on v3.24.0 (or v3.23.x)

## Breaking Changes

None. v3.25.0 is additive + repair.

## Upgrade Guide

1. **Refresh framework scripts** (Framework_Artifacts — overwrite; your `*_ext.py` hooks are untouched):
   `study_topic.py`, `capture_friction.py`, `wake_up.py`, `health_check.py`, `close_gate_check.py` from canonical `aget/scripts/` (or your template repo at tag `v3.25.0`).
2. **Adopt aget-ask** (optional, tier {O}): copy `.claude/skills/aget-ask/` + `.aget/specs/skills/SKILL-045_aget-ask.yaml`.
3. **Version pins**: `AGENTS.md` `@aget-version: 3.25.0`; `.aget/version.json` `aget_version` + migration_history entry.
4. **Reliance-only conformance line** (new model, D-1): add under your version label:
   `@aget-canonical-specs: https://github.com/aget-framework/aget/tree/v3.25.0/specs — reliance-only conformance`

## What you get

- `study_topic.py` stops rendering your live plans as `[inactive]` (case-fold + Plan_Status-first) and searches `knowledge/` + `ontology/`.
- `wake_up.py` self-attests reliance-manifest conformance when you carry a manifest (silent otherwise).
- `health_check.py` adds reliance + permission-accumulation checks (graceful when N/A).
- Release-class plan closes are DoD-guarded (blocks false-green closes).
- Friction captures carry a triage value-class (`owed` default — healthy controls are not remediation-eligible).

## Smoke Test

```bash
python3 scripts/wake_up.py            # shows v3.25.0 + (if manifest) attestation line
python3 scripts/health_check.py       # reliance_manifest + permission_accumulation rows present
python3 scripts/study_topic.py --topic "<your active plan's topic>"   # live plan renders ACTIVE
```

## Rollback

All changes are file-copy; restore prior copies from your `v3.24.0` tag. No data-format migrations.
