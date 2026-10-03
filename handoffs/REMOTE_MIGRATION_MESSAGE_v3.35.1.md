# Migration Message: v3.35.0 to v3.35.1

**Date**: 2026-10-04
**From**: AGET Framework Manager
**To**: Remote Fleet Supervisors
**Target Version**: 3.35.1. Confirm it is the latest entry in the public release list before acting; do not infer the target from versions inside your fleet.
**Migration Path**: v3.35.0 to v3.35.1 (an Aget on an earlier version takes v3.35.0 first, using its own migration message)
**Breaking Changes**: No
**Currency note**: read this message from `main`, not from the tag; post-tag corrections land on `main`.
**Corrections probe** (run exactly, from your core clone; a corrections record, if one is opened, cannot exist at the tag; `UNAVAILABLE` means the state is unknown, never "none"):

```bash
(  # subshell: a failure stops here without closing your shell
git fetch origin +refs/heads/main:refs/remotes/origin/main || { echo "UNAVAILABLE: fetch of main failed; corrections state unknown"; exit 1; }
REV=$(git rev-parse --verify 'refs/remotes/origin/main^{commit}') || { echo "UNAVAILABLE: origin/main unresolved"; exit 1; }
LIST=$(git ls-tree --name-only "$REV" handoffs/) && [ -n "$LIST" ] || { echo "UNAVAILABLE: cannot list handoffs/ at $REV"; exit 1; }
if printf '%s\n' "$LIST" | grep -qx 'handoffs/CORRECTIONS_v3.35.1.md'; then
  git show "$REV:handoffs/CORRECTIONS_v3.35.1.md" || { echo "UNAVAILABLE: corrections file listed but unreadable at $REV"; exit 1; }
else
  echo "No corrections recorded for 3.35.1 at $REV (handoffs/ listed; the file is not in it)"
fi
)
```

No delivered-files manifest is published for 3.35.1. The copy-list source is the tag tree, read with `git show v3.35.1:<path>`.

## Migration Target

- **Target version**: v3.35.1.
- **Deployment contract**: `DEPLOYMENT_SPEC_v3.35.1.yaml`, read at the tag with `git show v3.35.1:DEPLOYMENT_SPEC_v3.35.1.yaml`.
- **Payload source**: the core repository and the matching template, both at tag `v3.35.1`.

## What's New in v3.35.1

Theme: the first weekly-train release; it ships what reached `main` after 3.35.0.
- Still open from 3.35.0: the templates ship the unrepaired close-authorization guard; apply `handoffs/CORRECTIONS_v3.35.0.md` row 4 if you have not.
- `scripts/study_topic.py` no longer calls a topic novel when the relevance floor suppressed every hit; it reports the suppressed count and `--no-floor`. This is the one change an Aget runs.
- Six templates ship the Apache 2.0 `LICENSE` file their README declares.
- Documents only: a public decision log, refreshed requirements, the grounded term display form (CAP-VOC-006) with a correction of the `Aget_Instance` definition (now a kind of `Aget_Agent`), the Antigravity CLI re-measure and a partial referent-registry fix.

## Breaking Changes

None. Nothing is removed.

## Deployment Requirements

- Python 3.10 or later.
- Tag-bound sources: the core repository and the matching template at `v3.35.1`.
- The Aget is at v3.35.0.
- A test baseline recorded at each Aget before any payload lands.

## Upgrade Guide

**Step 0: sync the framework clones.** Fetch tags; no checkout is needed.

```bash
export FW=/path/to/your/framework-clones   # the directory holding aget and template-* clones
git -C "$FW/aget" fetch --tags origin
git -C "$FW/aget" show v3.35.1:.aget/version.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["aget_version"])'
# Expected: 3.35.1
```

**Step 0.5: check substance, not just the label.**

```bash
git -C "$FW/aget" cat-file -e v3.35.1:DEPLOYMENT_SPEC_v3.35.1.yaml && echo "spec OK"
T="$FW/template-<archetype>-aget"
git -C "$T" fetch --tags origin
git -C "$T" show v3.35.1:scripts/study_topic.py | grep -q 'NOT a novel-topic verdict' || echo "STOP: the template tag does not carry the study_topic fix"
```

**Per Aget**: follow the release handoff's Upgrade Guide:
1. Record the baseline first.
2. Diff each payload path against the Aget's copy.
3. Merge rather than overwrite where they differ.
4. Write the files.
5. Change version strings last.

Before overwriting `scripts/study_topic.py`, compare its function definitions with yours; local-only functions need a merge, not an overwrite.

### Behavioral Smoke

| # | Payload feature | Probe | Expected |
|---|---|---|---|
| 1 | M-3.35.1-1 | the `study_topic` check in the release handoff's Smoke Test | exit 0 (exit 1 on the 3.35.0 code) |
| 2 | all | `python3 -m pytest tests/ -q` | no new failures against the baseline recorded before Wave 0 |

## Smoke Test

- [ ] `wake_up.py` shows v3.35.1.
- [ ] Full `health_check.py` passes. A version pass is not a health pass; log pre-existing drift instead of hiding it.
- [ ] `AGENTS.md` shows `@aget-version: 3.35.1`.
- [ ] Behavioral Smoke rows 1 and 2 as expected.

## Rollback

Never reset or rewrite shared history. Revert a committed migration with `git revert`; before commit, restore only the recorded migration path set from the saved baseline commit. Re-run the baseline tests and wake-up, and record `ROLLED_BACK` or `HOLD`. Published tags are never moved.

## Fleet Coordination

Wave 0: the supervisor. Wave 1: one pilot receiver. Wave 2: the rest, in small batches. After each wave, re-verify at the receiver's source (version, commit and tree state), not from the worker's self-report. A headless dispatch must grant in-session authority for the in-scope disposition, or it ends waiting for an approval that cannot arrive.

## References

- https://github.com/aget-framework/aget/blob/main/CHANGELOG.md
- https://github.com/aget-framework/aget/blob/main/release-notes/v3.35.1.md
- https://github.com/aget-framework/aget/blob/main/handoffs/RELEASE_HANDOFF_v3.35.1.md
