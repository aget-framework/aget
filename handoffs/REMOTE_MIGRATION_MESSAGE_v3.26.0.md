# Remote Fleet Migration — v3.26.0 "Signals & Contracts"

**From**: aget-framework release management · **Date**: 2026-07-11 (regenerated 2026-07-11 — see Post-Release Corrections)
**Currency note**: read this message from `main`, not the version tag — post-tag repairs and hardening notes land on `main` (see Post-Release Corrections below and the release body's post-tag repair notes).

## Migration Target

- **Target version**: **v3.26.0** (explicit — never infer from N-1; this block is mandatory per TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.5.0)
- **Verified against the release list**: v3.26.0 is the latest published release at regeneration time (2026-07-11)
- **Deployment contract**: `DEPLOYMENT_SPEC_v3.26.0.yaml`, tag-reachable (`git show v3.26.0:DEPLOYMENT_SPEC_v3.26.0.yaml`)
- **Payload source**: canonical `aget/` at tag `v3.26.0` **plus the enumerated post-tag correction SHAs below** (scripts); template payload from **template repo `main` branches** this cycle (see Post-Release Corrections item C)
- **Applies to**: any AGET instance on v3.25.0 (or v3.24.x — the v3.25.0 message's steps compose cleanly before these)

## Breaking Changes

None. v3.26.0 is additive + repair.

## Post-Release Corrections (read BEFORE the Upgrade Guide)

Fixes landed on canonical `main` after the `v3.26.0` tag. Pull these specific artifacts at the listed SHAs (or any later `main`) instead of the tag copies — the tag copies carry the defects described:

| # | SHA | Artifact | Why the tag copy is not enough |
|---|-----|----------|-------------------------------|
| A | `e87f223` | `scripts/study_topic.py` | At tag, keyword matching silently breaks on edge punctuation (a trailing comma in a topic defeats word-boundary matching) and common function words dilute results. |
| B | `e5e4598` + `497acd2` | `scripts/permission_cleanup.py` | At tag, an unrecognized argument (including `--help`) **falls through to the live mutating path**, and the keep-heuristic is category-blind (drops all non-Bash grants). Do not run any permission cleanup from the tag copy. |
| C | (template mains) | template repo payloads | Template *tags* fail the M-3.26-6 mandatory-row check (payload lag, fixed and disclosed on template mains same day). Pull template payload from each template repo's `main`, not its `v3.26.0` tag, this cycle. |
| D | `875e423` | `.claude/skills/aget-record-lesson/SKILL.md` | The canonical repo carried **no copy at tag** — "adopt from canonical" is true from `main` forward only. At-tag consumers: adopt from `template-worker-aget` at its tag instead. |
| E | `e1514c8` + `29773ca` | `scripts/emit_delivered_files_manifest.py`, `scripts/check_mrow_conformance.py`, `handoffs/DELIVERED_FILES_v3.26.0.yaml` | New (post-tag) delivery-verification tooling — optional but recommended; see Delivery Verification below. |

## Step 0: Sync Framework (CRITICAL)

Before any upgrade work, sync your local framework clone. Stale framework repos cause agents to misread version availability and conclude the new version "does not exist."

```bash
cd $FW/aget && git pull origin main
cd $FW/template-{archetype}-aget && git pull origin main

# Verify target version is available:
python3 -c "import json; print(json.load(open('$FW/aget/.aget/version.json'))['aget_version'])"
# Expected: "3.26.0"
```

If the version does not show 3.26.0, your framework repo is stale. Do NOT proceed until sync is confirmed.

## Step 0.5: Pre-Migration Verification — substance, not just the label (do NOT skip)

The version reading 3.26.0 confirms the *label* — not that the payload is present or the contract published. A remote fleet has no producer-side relay to catch these.

```bash
# (a) Deployment contract published:
test -f $FW/aget/DEPLOYMENT_SPEC_v3.26.0.yaml && echo "spec OK" || echo "STOP: no DEPLOYMENT_SPEC_v3.26.0"
#   -> if ABSENT, STOP + escalate. Do NOT relabel "no spec" as a deviation.

# (b) Source actually contains the new artifacts (a version bump does NOT copy payload):
for f in scripts/wake_up.py scripts/health_check.py scripts/study_topic.py \
         scripts/check_skill_reliance_manifest.py scripts/close_gate_check.py \
         .claude/skills/aget-close-project/SKILL.md; do
  test -f "$FW/template-{archetype}-aget/$f" || echo "STOP: $f missing from source"
done
```

## Upgrade Guide

1. **Refresh framework scripts** (Framework_Artifacts — `*_ext.py` hooks untouched; run the customized-base-script pre-flight below BEFORE overwriting):
   `wake_up.py`, `health_check.py`, `study_topic.py`, `check_skill_reliance_manifest.py`, `close_gate_check.py` — from canonical `aget/scripts/` at tag `v3.26.0`, **except** `study_topic.py` (take `e87f223`+). If your agents carry `permission_cleanup.py`, refresh it too (Correction B) even though it is not v3.26.0 payload.
2. **New extension hook points**: `health_check.py` and `study_topic.py` now call `health_check_ext.py:post_health` / `study_topic_ext.py:post_study` when present. If you carried local additions in either base file, migrate them into the ext file as part of this refresh — that is the supported customization surface from v3.26.0 on.
3. **Refresh skills**: `.claude/skills/aget-close-project/SKILL.md` (C-CLOSE-007 + C-CLOSE-008). Optionally `aget-file-issue` (routing + probe steps — adopt from canonical `main`; template copies structurally lag this cycle) and `aget-record-lesson` (Step 4.5 — source per Correction D).
4. **Version pins**: `AGENTS.md` `@aget-version: 3.26.0`; `.aget/version.json` `aget_version` + migration_history entry. **Conformance-then-bump**: hold the pins until every script carries the new substance.

### Pre-Flight: Script Customization Check (base scripts, not just skills)

Before overwriting any framework script, check for local-only functions — a blind overwrite deletes them:

```bash
diff <(grep -E '^def |^    def ' $AGENT/scripts/<script>.py) \
     <(grep -E '^def |^    def ' $SOURCE/scripts/<script>.py)
# local-only defs -> function-preserving MERGE (into the new *_ext.py hooks where applicable), not overwrite
```

### Pre-Flight: Skill Customization Check

```bash
diff -rq $FW/template-{archetype}-aget/.claude/skills/ $AGENT/.claude/skills/
# identical -> safe to overwrite | differ -> merge customizations first | instance-only -> PRESERVE
```

## What you get

- `wake_up.py` tells you at session start when your framework version is behind the latest release (silent when current; fail-soft when offline).
- `health_check.py` / `study_topic.py` customization without forking (ext hooks) — ends the blind-overwrite risk class the v3.25.0 message warned about.
- `study_topic.py` reports exactly which surfaces it searched and which it deliberately did not (absence-vs-negative discipline), with token-boundary matching and a relevance floor.
- Project closes are guarded twice more: the closer must mutate the scaffolded checklist in place (C-CLOSE-007), and an executable-mechanism deliverable cannot go COMPLETE without execution evidence (C-CLOSE-008).
- Check scripts begin reporting PASS / FAIL / UNREACHABLE distinctly (three-state contract) — a missing dependency stops masquerading as a pass. First upgrades will SURFACE previously-silent UNREACHABLE states; that is revealed honesty, not regression.

## Delivery Verification (optional, recommended)

The post-tag tooling (Correction E) converts "trust the label" into runnable checks:

```bash
# What files SHOULD this release have delivered (sha256 at tag):
cat $FW/aget/handoffs/DELIVERED_FILES_v3.26.0.yaml

# Verify mandatory/optional detection rows at any ref:
python3 $FW/aget/scripts/check_mrow_conformance.py --help
```

## Fleet Coordination

| Wave | Scope | Purpose |
|------|-------|---------|
| 0 | Supervisor self-upgrade | Validate tooling, experience the pattern firsthand |
| 1 | 2–3 pilot agents (one per portfolio) | Catch archetype-specific issues |
| 2 | Remaining agents (batches of 3–5) | Full rollout |

After each wave: re-verify independently (never trust the worker's self-report alone — confirm version + SHA + tree state at source); respect per-agent variance (standing no-push policies, deliberate dirty-tree holds, and instance-version semvers are legitimate — use per-file `git add`, never a blanket override); expect transient failures at fleet scale (design the runner so failures are cleanly retryable).

**Headless dispatch — grant in-session execution authority explicitly.** A headless session cannot receive a GO/NOGO, so a dispatched agent that ends with "plan ready, awaiting your approval" has silently failed. The dispatch prompt MUST state that the agent has authority for its chosen in-scope disposition WITHIN THIS SESSION and must decide-execute-report (or decline with reasons). Verify from disk afterward — that is what distinguishes "planned" from "done".

## Main Fleet Experience

| Finding | Impact | Mitigation |
|---------|--------|------------|
| Deployment-receipt verification is not regression verification | A rollout can grade fully green on receipt evidence (sha-match, version pins) while agents carry live behavioral regressions found only later | Run the Behavioral Smoke (below) per agent before marking it done |
| Release-banner impls calling `gh release view` hang under non-tty python subprocess; a fail-soft timeout masks the hang as silence | The wake-up release-currency banner never fires, silently | Use the shipped canonical `wake_up.py` (`gh api`, <1s), or swap the call in local impls |
| `permission_cleanup.py` at tag: `--help` fell through to the live mutating path; cleanup was category-blind | Live permission mutations from an innocuous invocation (recovered from the script's own backup) | Correction B — refresh from `main` before any cleanup; keep the backup the script writes |
| Dual-basename scripts: payload delivered to `scripts/<name>.py` while the agent's config executes a different copy (e.g. `.aget/patterns/session/<name>.py`) | Upgrade is dead-on-arrival on the executed surface — version says 3.26.0, behavior is old | Behavioral Smoke probe 4: verify at the path your config actually invokes |
| Agent test suites importing symbols that moved into `*_ext.py` | CI red post-upgrade | `pytest --collect-only` immediately after payload (probe 3) |

## Smoke Test

### State checks

```bash
python3 scripts/wake_up.py             # shows v3.26.0; currency line only if behind latest
python3 scripts/health_check.py        # FULL check — version-pass != health-pass; expect pre-existing drift to surface, log it
python3 scripts/study_topic.py --topic "release"   # output carries 'Surfaces searched' + 'NOT searched' manifest
grep -c "C-CLOSE-008" .claude/skills/aget-close-project/SKILL.md   # expect >= 1
grep "@aget-version: 3.26.0" AGENTS.md                             # version pin present
```

### Behavioral Smoke (per agent — receipt evidence is not regression evidence)

1. **Release-currency signal fires**: on an agent one version behind, wake-up prints the currency line; on a current agent it is silent.
2. **Ext hooks fire**: create a trivial `health_check_ext.py:post_health` / `study_topic_ext.py:post_study` and confirm both run.
3. **Test suite collects clean**: `pytest --collect-only` — symbol moves into `*_ext.py` can strand local imports.
4. **Executed-surface check**: for any script with a second copy outside `scripts/` (check `.aget/config.json` and `.aget/patterns/` for dual basenames), confirm the copy your config invokes carries the v3.26.0 substance — `grep` a v3.26.0-only symbol at the executed path.

## Rollback

All changes are file-copy; restore prior copies from your `v3.26.0`-predecessor tag (`v3.25.0`). No data-format migrations.

## Carried cautions (from the v3.25.0 message — still operative)

1. **Operative-path caution**: verify at the path your agent's config actually invokes, not just conventional `scripts/` (now also Behavioral Smoke probe 4).
2. **Lineage baseline, not tag baseline**: agents predating template tagging (v3.9→v3.24 gap) need a known-good hash set from deployment lineages before divergence classification.
3. **Customized-base-script caution**: diff local vs source at function level before overwrite; local-only defs need a function-preserving merge — and from this release, a migration into the new ext hooks.
4. **Conformance-then-bump**: hold the version pin until every script carries the new substance.

## References

- [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md)
- [Release notes v3.26.0](https://github.com/aget-framework/aget/blob/v3.26.0/release-notes/v3.26.0.md)
- [SOP_fleet_migration.md](https://github.com/aget-framework/aget/blob/main/sops/SOP_fleet_migration.md)

---

*Migration Message v3.26.0 (regenerated 2026-07-11) — per TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.5.0, R-REL-019-07*
