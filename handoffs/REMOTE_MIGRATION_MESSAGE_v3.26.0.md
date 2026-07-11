# Remote Fleet Migration — v3.26.0 "Signals & Contracts"

**From**: aget-framework release management · **Date**: 2026-07-11

## Migration Target

- **Target version**: **v3.26.0** (explicit — never infer from N-1; this block is mandatory per TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.5.0)
- **Verified against the release list**: v3.26.0 is the latest published release at authoring time (2026-07-11)
- **Applies to**: any AGET instance on v3.25.0 (or v3.24.x — the v3.25.0 message's steps compose cleanly before these)

## Breaking Changes

None. v3.26.0 is additive + repair.

## Upgrade Guide

1. **Refresh framework scripts** (Framework_Artifacts — `*_ext.py` hooks untouched; see the customized-base-script caution below BEFORE overwriting):
   `wake_up.py`, `health_check.py`, `study_topic.py`, `check_skill_reliance_manifest.py`, `close_gate_check.py` from canonical `aget/scripts/` at tag `v3.26.0`.
2. **New extension hook points**: `health_check.py` and `study_topic.py` now call `health_check_ext.py:post_health` / `study_topic_ext.py:post_study` when present. If you carried local additions in either base file, migrate them into the ext file as part of this refresh — that is the supported customization surface from v3.26.0 on.
3. **Refresh skills**: `.claude/skills/aget-close-project/SKILL.md` (C-CLOSE-007 + C-CLOSE-008). Optionally `.claude/skills/aget-file-issue/SKILL.md` (routing + probe steps — adopt from canonical; template copies structurally lag this cycle) and `.claude/skills/aget-record-lesson/SKILL.md` (Step 4.5).
4. **Version pins**: `AGENTS.md` `@aget-version: 3.26.0`; `.aget/version.json` `aget_version` + migration_history entry.

## What you get

- `wake_up.py` tells you at session start when your framework version is behind the latest release (silent when current; fail-soft when offline).
- `health_check.py` / `study_topic.py` customization without forking (ext hooks) — ends the blind-overwrite risk class the v3.25.0 message warned about.
- `study_topic.py` reports exactly which surfaces it searched and which it deliberately did not (absence-vs-negative discipline), with token-boundary matching and a relevance floor.
- Project closes are guarded twice more: the closer must mutate the scaffolded checklist in place (C-CLOSE-007), and an executable-mechanism deliverable cannot go COMPLETE without execution evidence (C-CLOSE-008).
- Check scripts begin reporting PASS / FAIL / UNREACHABLE distinctly (three-state contract) — a missing dependency stops masquerading as a pass.

## Smoke Test

```bash
python3 scripts/wake_up.py             # shows v3.26.0; currency line only if behind latest
python3 scripts/health_check.py        # runs clean; ext hook fires if you created health_check_ext.py
python3 scripts/study_topic.py --topic "<any topic>"   # output carries a 'Surfaces searched' + 'NOT searched' manifest
grep -c "C-CLOSE-008" .claude/skills/aget-close-project/SKILL.md   # expect >= 1
```

## Rollback

All changes are file-copy; restore prior copies from your `v3.26.0`-predecessor tag (`v3.25.0`). No data-format migrations.

## Carried cautions (from the v3.25.0 message — still operative)

1. **Operative-path caution**: verify at the path your agent's config actually invokes, not just conventional `scripts/`.
2. **Lineage baseline, not tag baseline**: agents predating template tagging (v3.9→v3.24 gap) need a known-good hash set from deployment lineages before divergence classification.
3. **Customized-base-script caution**: diff local vs source at function level before overwrite; local-only defs need a function-preserving merge — and from this release, a migration into the new ext hooks.
4. **Conformance-then-bump**: hold the version pin until every script carries the new substance.
