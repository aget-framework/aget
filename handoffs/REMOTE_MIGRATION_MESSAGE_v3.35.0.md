# Migration Message: v3.34.0 to v3.35.0

**Date**: 2026-09-26
**From**: AGET Framework Manager
**To**: Remote Fleet Supervisors
**Target Version**: 3.35.0. Confirm it is the latest entry in the public release list before acting; do not infer the target from versions inside your fleet.
**Migration Path**: v3.34.0 to v3.35.0
**Breaking Changes**: No
**Currency note**: read this message from `main`, not from the tag; post-tag corrections land on `main`.
**Corrections probe** (run exactly; the corrections record cannot exist at the tag):

```bash
git fetch origin
git show origin/main:handoffs/CORRECTIONS_v3.35.0.md   # apply every row on top of the tag payload
```

No delivered-files manifest is published for 3.35.0. The copy-list source is the tag tree, read with `git show v3.35.0:<path>`.

## Migration Target

- **Target version**: v3.35.0.
- **Deployment contract**: `DEPLOYMENT_SPEC_v3.35.0.yaml`, read at the tag with `git show v3.35.0:DEPLOYMENT_SPEC_v3.35.0.yaml`. Its `status` stays `prepared` at the tag under a disclosed waiver for v3.35.0 only; publication is shown by the annotated tag and the GitHub Release object.
- **Payload source**: the core repository and the matching template, both at tag `v3.35.0`.

## What's New in v3.35.0

Theme: receiver correctness.
- `/aget-propose-actions` v1.9.0 says whether each proposed action moves the outcome or only its measurement, and its deferral scan reads handoff documents on disk from configurable locations.
- The strict close gate runs in Agets created from templates.
- An advisory CI rule, CAP-CI-010, for tests that must not depend on the host.

## Breaking Changes

None. There is one registry deprecation removal (DEP-BASENAME-VPP-001), plus the retirement of a producer-internal verification matrix; neither removes a file any shipped repository carried; see the release handoff, section Removals.

## Deployment Requirements

- Python 3.10 or later.
- Tag-bound sources: the core repository and the matching template at `v3.35.0`.
- A test baseline recorded at each Aget before any payload lands.
- Skills installed only with the scripts they call; the close-gate package installed as one unit (see the release handoff).
- An Aget carrying a rebound copy of the 3.31.1 receiver-contract test: refresh it from this release or keep its local skip (see the release handoff, Deployment Requirements).

## Upgrade Guide

**Step 0: sync the framework clones.** Fetch tags; no checkout is needed.

```bash
export FW=/path/to/your/aget-framework-clones   # the directory holding aget and template-* clones
git -C "$FW/aget" fetch --tags origin
git -C "$FW/aget" show v3.35.0:.aget/version.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["aget_version"])'
# Expected: 3.35.0
```

**Step 0.5: check substance, not just the label.**

```bash
git -C "$FW/aget" cat-file -e v3.35.0:DEPLOYMENT_SPEC_v3.35.0.yaml && echo "spec OK"
T="$FW/template-<archetype>-aget"
git -C "$T" fetch --tags origin
for f in scripts/propose_actions_handoff_scan.py scripts/close_gate_lifecycle.py specs/AGET_PROJECT_PLAN_SPEC.md; do
  git -C "$T" cat-file -e "v3.35.0:$f" || echo "STOP: $f missing at the template tag"
done
```

**Per Aget**: follow the release handoff's Upgrade Guide:
1. Record the baseline first.
2. Diff each payload path against the Aget's copy.
3. Merge rather than overwrite where they differ.
4. Write the files.
5. Change version strings last.

Before overwriting any base script, compare its function definitions with yours; local-only functions need a merge, not an overwrite.

### Behavioral Smoke

| # | Payload feature | Probe | Expected |
|---|---|---|---|
| 1 | M-3.35-1 | `python3 scripts/propose_actions_handoff_scan.py --self-test` | exit 0 |
| 2 | M-3.35-1 | `python3 scripts/propose_actions_classify.py --self-test` | exit 0 |
| 3 | M-3.35-3 | the fixture-plan probe in the release handoff's Smoke Test | exit status 2, finding `gate_status_pending` |
| 4 | all | `python3 -m pytest tests/ -q` | no new failures against the baseline recorded before Wave 0 |

## Smoke Test

- [ ] `wake_up.py` shows v3.35.0.
- [ ] Full `health_check.py` passes. A version pass is not a health pass; log pre-existing drift instead of hiding it.
- [ ] `AGENTS.md` shows `@aget-version: 3.35.0`.
- [ ] Behavioral Smoke rows 1 to 4 as expected.

## Rollback

Never reset or rewrite shared history. Revert a committed migration with `git revert`; before commit, restore only the recorded migration path set from the saved baseline commit. Re-run the baseline tests and wake-up, and record `ROLLED_BACK` or `HOLD`. Published tags are never moved.

## Fleet Coordination

Wave 0: the supervisor. Wave 1: one pilot receiver. Wave 2: the rest, in small batches. After each wave, re-verify at the receiver's source (version, commit and tree state), not from the worker's self-report. A headless dispatch must grant in-session authority for the in-scope disposition, or it ends waiting for an approval that cannot arrive.

## References

- https://github.com/aget-framework/aget/blob/main/CHANGELOG.md
- https://github.com/aget-framework/aget/blob/main/release-notes/v3.35.0.md
- https://github.com/aget-framework/aget/blob/main/handoffs/RELEASE_HANDOFF_v3.35.0.md
