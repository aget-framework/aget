# Remote Migration Message — AGET v3.33.0

**Target version**: 3.33.0

**Migration path verified by this package**: v3.32.0 → v3.33.0

**Breaking changes**: None intentional

**State**: Prepared for the tag payload. This message does not assert publication, receipt, installation,
behavioural acceptance, or deployment.

## What Changes

v3.33.0 adds tested archetype-parity and conformance self-assessment instruments, improves topic study for
URLs and planning initiatives, introduces an audience-aware referent-registry substrate, sanitizes the
reusable handoff shape, and creates documented homes for future hook, pattern, and planning-template work.

The three new directory README files are homes, not the controls they describe. This release does **not**
claim that a commit hook, content sanitizer, or project-plan template was installed there. The referent
registry also does not imply that an instance-local resolver shipped publicly.

## Preconditions

- Python 3.10 or later.
- The receiver’s own upgrade authorization and point-upgrade procedure.
- A clean checkout of the annotated public `v3.33.0` core tag and the matching archetype-template tag.
- A recorded receiver baseline and rollback reference.
- `DEPLOYMENT_SPEC_v3.33.0.yaml` available at the peeled core tag commit.

If any precondition is unavailable, record `HOLD`; do not infer it from a version label or moving branch.

## Immutable Source Check

```bash
export FW=/path/to/framework
export AGENT=/path/to/receiving-agent
export ARCHETYPE=worker  # replace with the receiver's registered archetype
export SOURCE="$FW/aget-v3.33.0"
export TEMPLATE="$FW/template-${ARCHETYPE}-aget"

git clone --no-checkout https://github.com/aget-framework/aget.git "$SOURCE"
git -C "$SOURCE" fetch --tags origin
git -C "$SOURCE" checkout --detach v3.33.0
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.33.0)" = tag
CORE_SHA=$(git -C "$SOURCE" rev-parse 'v3.33.0^{commit}')
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$CORE_SHA"
test -f "$SOURCE/DEPLOYMENT_SPEC_v3.33.0.yaml"
test -f "$SOURCE/handoffs/RELEASE_HANDOFF_v3.33.0.md"

git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.33.0)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse 'v3.33.0^{commit}')

git -C "$SOURCE" rev-parse "$CORE_SHA:DEPLOYMENT_SPEC_v3.33.0.yaml"
git -C "$SOURCE" rev-parse "$CORE_SHA:handoffs/RELEASE_HANDOFF_v3.33.0.md"
```

Record both peeled commits and the deployment-spec blob identity in the receiver receipt.

## Upgrade Steps

1. Capture `BEFORE_SHA=$(git -C "$AGENT" rev-parse HEAD)`, `git status --short`, current version, and
   `python3 -m pytest tests/ -q` output before mutation.
2. Read the tag-pinned deployment specification. Select only paths applicable to this receiver and its
   matching archetype template.
3. Diff each selected destination before overwrite. Preserve local extensions and unrelated dirty paths.
4. Apply the content first and run every path-specific detection clause. Do not use a README directory
   home as proof that a future control was installed.
5. After substance is present, update all receiver-governed version surfaces to 3.33.0 and append the
   migration-history entry.
6. Run the behavioural checks below, then the receiver’s full tests and wake-up. Stage exact paths and
   commit only after they pass.

## Behavioural Checks

Run against the clean tag checkout:

```bash
(cd "$SOURCE" && python3 scripts/check_archetype_register_parity.py --self-test)
(cd "$SOURCE" && python3 scripts/self_assess_conformance.py --self-test)
(cd "$SOURCE" && python3 scripts/study_topic.py --verify)
(cd "$SOURCE" && python3 -m pytest -q \
  tests/test_archetype_register_parity.py \
  tests/test_self_assess_conformance.py \
  tests/test_study_topic_canonical_surface.py \
  tests/test_study_topic_ontology_surface.py)
```

Run against the installed receiver:

```bash
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
git -C "$AGENT" diff --check
```

Required result: the tag-checkout commands exit 0; the receiver has no new test failure against its saved
baseline; wake-up observes 3.33.0; every selected path matches its deployment-contract postcondition. An
unavailable required population, a stale version surface, or an identity mismatch is `HOLD`, not pass.

## Rollback

Never force-push or reset a shared branch. If the migration was committed as one exact-path commit:

```bash
MIGRATION_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" revert --no-edit "$MIGRATION_SHA"
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
```

If failure occurs before commit, restore only the recorded migration path set from `BEFORE_SHA`, preserve
unrelated work and the failure evidence, and record `HOLD` or `ROLLED_BACK`. A retry requires a corrected
immutable source and the same checks.

## Required Receipt

Record, at minimum:

- receiver identifier and archetype;
- observation time;
- core and template tag names and peeled commit SHAs;
- deployment-spec blob identity;
- pre-upgrade commit, version, dirty paths, and full-test baseline;
- exact selected paths and preserved extensions;
- migration commit or rollback stable cut;
- raw exit/summary for all three instrument checks, focused tests, receiver full tests, and wake-up version;
- one disposition: `ACQUIRED`, `INTEGRITY_VERIFIED`, `INSTALLED`, `BEHAVIOUR_VERIFIED`, `ACCEPTED`, `HOLD`,
  or `ROLLED_BACK`;
- receiver-side verifier and timestamp.

Do not collapse these states. Public availability does not prove acquisition; installation does not prove
behaviour; a receiver receipt does not by itself prove broader deployment. Preserve prior failed and rolled-
back attempts as immutable events.

For the complete field schema and pilot table, read
`handoffs/RELEASE_HANDOFF_v3.33.0.md` from the same peeled tag commit.
