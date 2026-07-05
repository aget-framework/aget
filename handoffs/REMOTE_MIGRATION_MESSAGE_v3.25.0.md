# Remote Fleet Migration — v3.25.0 "Grounded Entities & Trusted Releases"

**From**: aget-framework release management · **Date**: 2026-07-04 · **Applies to**: any AGET instance on v3.24.0 (or v3.23.x)

## Breaking Changes

None. v3.25.0 is additive + repair.

## Upgrade Guide

1. **Refresh framework scripts** (Framework_Artifacts — overwrite; your `*_ext.py` hooks are untouched):
   `study_topic.py`, `capture_friction.py`, `wake_up.py`, `health_check.py`, `close_gate_check.py` from canonical `aget/scripts/` (or your template repo at tag `v3.25.0`).
2. **Adopt aget-ask** (optional, tier {O}): copy `.claude/skills/aget-ask/` and the SKILL-045 spec yaml from `.aget/specs/skills/` (same paths in your template repo at the tag).
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

## Fleet-migration hardening notes (added 2026-07-05, from the first executed fleet migration)

1. **Deployment contract**: `DEPLOYMENT_SPEC_v3.25.0.yaml` lives at canonical root on **main** (same-day back-fill — NOT reachable at the `v3.25.0` tag). Fetch it from main; its M-row detection clauses are your per-agent verify checklist.
2. **Operative-path caution**: detection clauses verify file content at conventional paths (`scripts/`). Before classifying or verifying any agent, resolve each script's OPERATIVE path from the agent's own config (AGENTS.md / skill invocations) and run checks against THAT path — a marker-complete copy at `scripts/` is inert if the agent's wiring invokes a copy elsewhere (observed once in the pilot fleet: a patterns-dir wake-up).
3. **Lineage baseline, not tag baseline**: if your agents predate template tagging (v3.9→v3.24 gap), comparing agent scripts against canonical-tag bytes will flag your entire fleet as "locally patched" (observed: 33/33 false positives). Build a known-good hash set from every framework-shipped version across your deployment lineages (canonical + template git histories + ≥N-agent consensus on identical copies), and route only true outliers to per-agent diff review — overwrite (logged), re-base (gated on the feature-marker detection clause), or honored refusal.
4. **Expected WARN**: the reliance C3 cross-repo check may report "archetype index unreachable" from standard agent seats — expected for non-adjacent checkouts, graceful, not an upgrade regression.
5. **Upgrade-revealed debt**: the new `health_check.py` gates (permission accumulation, reliance) surface PRE-EXISTING conditions on first run. Diagnose with the two-checker test: if the v3.24-era health check exits 0 on the same tree, the finding is revealed debt, not an upgrade regression.
