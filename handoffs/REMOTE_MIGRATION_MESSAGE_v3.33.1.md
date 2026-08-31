# Remote Migration Message — AGET v3.33.1

**Target version**: 3.33.1  
**Migration path**: v3.33.0 → v3.33.1  
**Breaking changes**: None intentional

## What Changes

v3.33.1 is a forward integrity correction. It supplies a complete tag-bound deployment contract and
receiver handoff, advances all governed version surfaces, and closes the document-template's missing
Skill Routing and Write Scope sections. It does not rewrite the immutable v3.33.0 release.

## Deployment Requirements

- Obtain the receiver's own upgrade authorization.
- Use the annotated core `v3.33.1` tag and matching archetype-template tag.
- Capture the receiver's commit, version, dirty paths, and full-test baseline before mutation.
- Read `DEPLOYMENT_SPEC_v3.33.1.yaml` from the peeled core tag and apply only applicable paths.
- Preserve receiver-owned extensions and prepare an exact rollback reference.

## Upgrade Guide

```bash
export SOURCE=/path/to/aget-v3.33.1
export TEMPLATE=/path/to/matching-template
export AGENT=/path/to/receiving-agent

git -C "$SOURCE" fetch --tags origin
git -C "$SOURCE" checkout --detach v3.33.1
CORE_SHA=$(git -C "$SOURCE" rev-parse 'v3.33.1^{commit}')
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.33.1)" = tag
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["aget_version"])' "$SOURCE/.aget/version.json")" = 3.33.1
test -f "$SOURCE/DEPLOYMENT_SPEC_v3.33.1.yaml"
test -f "$SOURCE/handoffs/RELEASE_HANDOFF_v3.33.1.md"

git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.33.1)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse 'v3.33.1^{commit}')
```

Record `CORE_SHA`, `TEMPLATE_SHA`, the deployment-spec blob, and the exact selected path set. Apply
substance before version labels; stage and commit only the governed migration paths after validation.

## Smoke Test

```bash
(cd "$SOURCE" && python3 -m pytest -q tests/)
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
git -C "$AGENT" diff --check
```

Required result: no new receiver test failures, wake-up observes 3.33.1, and every selected path satisfies
the tag-pinned deployment contract. Any missing source, stale version, or identity mismatch is `HOLD`.

## Rollback

Never rewrite shared history. Revert a committed migration with `git revert`; before commit, restore only
the recorded migration paths from the saved pre-upgrade commit. Preserve failure evidence and unrelated
work, then record `ROLLED_BACK` or `HOLD`.

## Completion Response

Return the receiver identifier and archetype; core/template peeled SHAs; deployment-spec blob; before and
after commits; selected paths; test and wake-up results; rollback stable cut; verifier; timestamp; and one
disposition: `ACQUIRED`, `INTEGRITY_VERIFIED`, `INSTALLED`, `BEHAVIOUR_VERIFIED`, `ACCEPTED`, `HOLD`, or
`ROLLED_BACK`.

## Known Items

- v3.33.0 remains immutable and is not repaired in place.
- Public availability is not receiver acquisition; installation is not behavioural acceptance.
- The document template retains pre-existing non-Tier-1 configuration findings outside this correction.
