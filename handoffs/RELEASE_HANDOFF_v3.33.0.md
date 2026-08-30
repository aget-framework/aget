# Release Handoff — AGET v3.33.0 “Make the next migration cost less”

**Target version**: 3.33.0

**Target date**: 2026-08-30

**Breaking changes**: None intentional

**State**: Prepared for the tag payload. Publication, receipt, installation, behavioural acceptance, and
deployment are separate states and are not asserted by this artifact.

## Summary

v3.33.0 makes framework work easier to promote and verify. It adds two independently falsifiable
conformance instruments, improves topic study, introduces a public referent-registry substrate, removes
operator inventory from the reusable release-handoff template, and creates documented destination homes
for future hooks, executable patterns, and planning templates.

The release is control- and documentation-heavy. A version stamp alone is not adoption. A receiver accepts
the release only after applying the tag-pinned deployment contract, preserving local extensions, and
recording receiver-side behavioural evidence.

## Exact Payload and Boundaries

| Surface | What v3.33.0 supplies | Receiver boundary |
|---|---|---|
| `scripts/check_archetype_register_parity.py` and its test | A four-population parity instrument with both-polarity falsifiers | Missing populations are reported as unavailable; absence is not silently interpreted as parity |
| `scripts/self_assess_conformance.py` and its test | A conformance self-assessment plus an actuator/falsifier module | Its subject verdict may legitimately fail; the test proves discrimination, not that every receiver conforms |
| `scripts/study_topic.py` | URL decomposition and the planning-initiatives search surface | Zero results remain a finding only after the emitted search contract shows which surfaces were reachable |
| `docs/REFERENT_REGISTRY.yaml` | A public, audience-aware registry substrate | The instance-local resolver is not part of this public payload; registry presence alone is not resolution |
| `sops/templates/RELEASE_HANDOFF_TEMPLATE.md` | A reusable handoff shape without an operator roster | The template contains placeholders, never a receiving fleet inventory |
| `.githooks/`, `.aget/patterns/`, and `planning/` README files | Contracts for three destination directories | These are homes only. No commit hook, content sanitizer, or project-plan template is implied to ship there in this release |
| `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` | An updated current digest for the changed `study_topic.py` payload | The v3.30.0 tag digest remains the historical referent; existing receipts are not reinterpreted |
| Version and release artifacts | The 3.33.0 identity and tag-pinned receiver contract | The tagged deployment specification is authoritative for applicability; do not infer a copy list from this summary |

No instance-owned extension file is promoted by this release. Do not copy every core path into every
agent. Apply only paths selected for the receiver by `DEPLOYMENT_SPEC_v3.33.0.yaml` and the matching
archetype template at the same tag.

## Receiving-Agent Governance Checklist

Before changing a receiver:

- [ ] Follow the receiver’s own upgrade approval and change-control procedure.
- [ ] Record the pre-upgrade commit, version, dirty-path inventory, and full-test baseline.
- [ ] Verify the annotated core and matching template tags and record their peeled commits.
- [ ] Read the deployment specification from the core tag; stop if it is absent or inconsistent.
- [ ] Diff every selected destination before overwrite; preserve receiver-owned extensions.
- [ ] Prepare a rollback commit or exact pre-upgrade restore reference before mutation.

This handoff supplies information and checks. It does not authorize bypassing local governance.

## Receiver Upgrade Procedure

Set receiver-local paths; do not substitute an operator-specific path in a shared receipt:

```bash
export FW=/path/to/framework
export AGENT=/path/to/receiving-agent
export ARCHETYPE=worker  # replace with the receiver's registered template archetype
export SOURCE="$FW/aget-v3.33.0"
export TEMPLATE="$FW/template-${ARCHETYPE}-aget"
```

### 1. Acquire and bind immutable sources

Create or refresh a clean public source checkout, then detach it at the release tag:

```bash
git clone --no-checkout https://github.com/aget-framework/aget.git "$SOURCE"
git -C "$SOURCE" fetch --tags origin
git -C "$SOURCE" checkout --detach v3.33.0

test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.33.0)" = tag
CORE_SHA=$(git -C "$SOURCE" rev-parse 'v3.33.0^{commit}')
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$CORE_SHA"
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["aget_version"])' "$SOURCE/.aget/version.json")" = 3.33.0
test -f "$SOURCE/DEPLOYMENT_SPEC_v3.33.0.yaml"
test -f "$SOURCE/handoffs/RELEASE_HANDOFF_v3.33.0.md"
test -f "$SOURCE/handoffs/REMOTE_MIGRATION_MESSAGE_v3.33.0.md"
```

If the tag, version identity, deployment specification, or either handoff is absent, record `HOLD` and
stop. A moving main branch, a draft, or a version string is not a substitute for the immutable package.

Fetch the matching template tag without changing the receiver:

```bash
git -C "$TEMPLATE" fetch --tags origin
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse 'v3.33.0^{commit}')
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.33.0)" = tag
```

Record `CORE_SHA`, `TEMPLATE_SHA`, and these immutable artifact identities:

```bash
git -C "$SOURCE" rev-parse "$CORE_SHA:DEPLOYMENT_SPEC_v3.33.0.yaml"
git -C "$SOURCE" rev-parse "$CORE_SHA:handoffs/RELEASE_HANDOFF_v3.33.0.md"
git -C "$SOURCE" rev-parse "$CORE_SHA:handoffs/REMOTE_MIGRATION_MESSAGE_v3.33.0.md"
```

### 2. Capture the receiver baseline and custody

```bash
BEFORE_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" status --short
(cd "$AGENT" && python3 -m pytest tests/ -q)
```

Preserve the complete output in the receipt. A dirty repository is not automatically invalid, but no
upgrade may overwrite or stage an unrelated path. If the selected path set overlaps local work, stop and
merge deliberately or defer the receiver.

### 3. Apply substance before version labels

Read `DEPLOYMENT_SPEC_v3.33.0.yaml` at `CORE_SHA`. For each applicable path:

1. Compare the receiver, matching template at `TEMPLATE_SHA`, and core source where the specification
   names core as authority.
2. Preserve instance extensions and locally governed configuration.
3. Apply only the selected paths and record source and destination blob identities.
4. Run the path-specific detection clause from the deployment specification.
5. Only after the substance is present, update every version-bearing surface required by the receiver’s
   point-upgrade procedure to 3.33.0 and append its migration-history entry.

Do not copy a README directory home as evidence that the future control named by that README was installed.

### 4. Verify behaviour at the receiver

First prove the release instruments can discriminate in the clean tag checkout:

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

Then verify the installed receiver:

```bash
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
git -C "$AGENT" diff --check
```

Compare the full-test result to the saved baseline. New failures, an unavailable required population, a
stale version surface, or a path-identity mismatch means `HOLD`; it is not converted to pass by the version
label. Commit the migration only after all receiver-required checks pass, staging exact paths only.

## Applicability Notes

- Framework maintainers may consume the new scripts directly from the core tag.
- Agent instances consume only the subset selected by their matching template and the deployment spec.
- `check_archetype_register_parity.py` may require receiver-local register configuration to observe every
  population. Preserve `UNAVAILABLE` as a result; do not invent a fallback path.
- `self_assess_conformance.py` may report findings on a healthy installation. Record its complete result;
  do not confuse instrument correctness with a conformant subject.
- The migration-contract amendment applies only to consumers of that existing contract. It preserves the
  frozen v3.30.0 digest and changes the current payload digest; never rewrite historical receipts.

## Rollback

Rollback preserves history and receiver-owned state. Never force-push or reset a shared branch.

If the upgrade was committed as one exact-path migration commit:

```bash
MIGRATION_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" revert --no-edit "$MIGRATION_SHA"
(cd "$AGENT" && python3 -m pytest tests/ -q)
(cd "$AGENT" && python3 scripts/wake_up.py)
```

If validation failed before commit, restore only the recorded upgrade path set from `BEFORE_SHA`; do not
restore unrelated files. Preserve the failed output and source identities, record `ROLLED_BACK` or `HOLD`,
and require a corrected immutable source to pass the same procedure before retrying.

## Receiver Receipt Contract

The receiver or its verifier records the following fields without normalizing away failures:

```yaml
release: 3.33.0
receiver: <public or receiver-local identifier>
archetype: <registered template archetype>
observed_at: <ISO-8601 timestamp>
source:
  core_tag: v3.33.0
  core_peeled_commit: <full SHA>
  template_tag: v3.33.0
  template_peeled_commit: <full SHA>
  deployment_spec_blob: <git blob id>
before:
  receiver_commit: <full SHA>
  version: <version>
  dirty_paths: [<exact paths>]
  full_test: {exit: <integer>, summary: <verbatim summary>, evidence: <path or immutable reference>}
application:
  selected_paths: [<exact paths from the deployment contract>]
  preserved_extensions: [<paths or none>]
  migration_commit: <full SHA or null>
verification:
  archetype_self_test: {exit: <integer>, summary: <verbatim summary>}
  self_assess_self_test: {exit: <integer>, summary: <verbatim summary>}
  study_topic_verify: {exit: <integer>, summary: <verbatim summary>}
  receiver_full_test: {exit: <integer>, summary: <verbatim summary>, evidence: <path or immutable reference>}
  wake_up_version: <observed value>
rollback:
  stable_cut: <pre-upgrade commit or revert commit>
  exercised: <true or false>
disposition: <ACQUIRED|INTEGRITY_VERIFIED|INSTALLED|BEHAVIOUR_VERIFIED|ACCEPTED|HOLD|ROLLED_BACK>
verified_by: <receiver-side verifier>
```

State is monotonic only when evidence supports it: availability is not acquisition; acquisition is not
integrity; integrity is not installation; installation is not behavioural verification; and none of those
alone proves fleet deployment. `HOLD` and `ROLLED_BACK` remain visible rather than being overwritten by a
later attempt.

## Pilot Tracking

| Receiver | Core/template SHAs recorded | Integrity | Installed | Behaviour | Disposition | Verified by/date |
|---|---|---|---|---|---|---|
| *(pending receiver)* | pending | pending | pending | pending | pending | pending |

No row is pre-acknowledged. Populate this table only from receiver receipts.

## Tag-Pinned References

- `CHANGELOG.md`
- `release-notes/v3.33.0.md`
- `DEPLOYMENT_SPEC_v3.33.0.yaml`
- `handoffs/REMOTE_MIGRATION_MESSAGE_v3.33.0.md`
- `sops/SOP_point_upgrade.md`
