# Release Handoff — AGET v3.35.1

Target version: 3.35.1. Prepared 2026-10-03 for publication on 2026-10-04; publication and adoption unverified.

## Release Summary

Theme: the first weekly-train release. It ships what reached `main` after 3.35.0 (six content pull requests, #108 to #113), described in [the release notes](../release-notes/v3.35.1.md): a public decision log and refreshed requirements; the grounded term display form (CAP-VOC-006, a prose rule); a `study_topic` fix; the Antigravity CLI re-measure; a partial referent-registry fix; the 3.35.0 corrections record; and the licence file in six templates. Breaking changes: none. The one change a receiving Aget runs is `scripts/study_topic.py`. Consume the exact public core and matching-template tags, preserve receiver state, and exercise that change.

## Context for External Fleets

External fleets must treat availability, acquisition, installation, behavioural verification and acceptance as separate states. This handoff is an information and verification contract, not authority to modify a receiver. Each receiving manager applies its own governance, preserves local extensions, and returns evidence from the receiver itself. No operator-specific path, private inventory or fleet-wide deployment claim is embedded in this public artifact.

### Archetype Divergence
The runnable payload is the same for all 13 archetypes. Six templates also gain a `LICENSE` file: analyst, architect, executive, operator, researcher and reviewer.

## Script Deployment

| Path | Change | Surfaces |
|---|---|---|
| `scripts/study_topic.py` | zero-result branch reports suppressed hits instead of "novel topic" | core, 13 templates |
| `LICENSE` | new (Apache 2.0) | 6 templates |
| `specs/AGET_VOCABULARY_SPEC.md` | v1.18.0, adds CAP-VOC-006 | core |
| `governance/DECISION_LOG.md` | new | core |
| `requirements/` (seven files) | refreshed | core |
| `docs/AGET_CLI_SUPPORT_MATRIX.md`, `scripts/check_runtime_support_evidence.py` | Antigravity re-measure | core |
| `docs/REFERENT_REGISTRY.yaml` | concept links marked partial | core |

## Breaking Changes

None. Nothing is removed.

## Receiving-Agent Governance Checklist

- [ ] Obtain receiver-local approval and record the applicable migration procedure.
- [ ] Capture the pre-upgrade commit, version, dirty paths and full-test baseline before any payload lands.
- [ ] Verify the annotated core and matching-template `v3.35.1` tags and record their peeled commits.
- [ ] Read `DEPLOYMENT_SPEC_v3.35.1.yaml` from the peeled core tag.
- [ ] Diff every selected destination and preserve receiver-owned extensions.
- [ ] Prepare an exact rollback reference before changing anything.

## Deployment Requirements

Python 3.10 or later, immutable tag-bound sources, a matching archetype template, a recorded receiver baseline and a rollback reference are required. Missing evidence is `HOLD`, never an inferred pass. A receiver on 3.35.0 needs nothing else from this release; a receiver on an earlier version takes 3.35.0 first (see its handoff). If you have not yet applied `handoffs/CORRECTIONS_v3.35.0.md` row 4 (the template close-authorization guard), do so: this release does not carry that repair.

## Upgrade Guide

Run this block as one Bash script; stop on any failed command. It reads payload bytes from tag objects and checks nothing out, so a source clone shared by several Agets is never switched under another migration.

```bash
set -euo pipefail
export SOURCE=/path/to/aget
export TEMPLATE=/path/to/matching-template
export AGENT=/path/to/receiving-agent

git -C "$SOURCE" fetch --tags origin
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.35.1)" = tag
CORE_SHA=$(git -C "$SOURCE" rev-parse --verify 'v3.35.1^{commit}')
git -C "$SOURCE" show v3.35.1:.aget/version.json | python3 -c 'import json,sys; assert json.load(sys.stdin)["aget_version"] == "3.35.1"'
git -C "$SOURCE" cat-file -e v3.35.1:DEPLOYMENT_SPEC_v3.35.1.yaml

git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.35.1)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse --verify 'v3.35.1^{commit}')
echo "core $CORE_SHA template $TEMPLATE_SHA"

BEFORE_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" status --short
(cd "$AGENT" && python3 -m pytest tests/ -q)
```

Compare each payload path with your copy before writing, and preserve local extensions:

```bash
for p in scripts/study_topic.py LICENSE; do
  git -C "$TEMPLATE" cat-file -e "v3.35.1:$p" 2>/dev/null || continue
  if [ -f "$AGENT/$p" ]; then
    git -C "$TEMPLATE" show "v3.35.1:$p" | diff -q - "$AGENT/$p" || echo "DIFFERS: $p (merge; keep local extensions)"
  else
    echo "NEW: $p"
  fi
done
```

Write a path only after its difference is resolved, for example `git -C "$TEMPLATE" show "v3.35.1:<path>" > "$AGENT/<path>"`, and record source and destination blob identities. A receiver that chose its own licence keeps it. Change version strings only after the payload is in place.

### Text Replacement Table

| File | From | To |
|---|---|---|
| `.aget/version.json` | `"aget_version": "3.35.0"` | `"aget_version": "3.35.1"`, plus a `migration_history` entry |
| `AGENTS.md` | `@aget-version: 3.35.0` | `@aget-version: 3.35.1` |
| `AGENTS.md`, template-derived Agets | `/tree/v3.35.0/specs` | `/tree/v3.35.1/specs` |

## Smoke Test

```bash
(cd "$AGENT" && python3 scripts/wake_up.py)
(cd "$AGENT" && python3 -c "import sys; sys.path.insert(0, 'scripts'); import study_topic as st; r = st.generate_report('agy', {'ldocs': [], 'patterns': [], 'project_plans': [], 'sops': [], 'governance': []}, floor_info={'floor': 2.0, 'suppressed': 1}); sys.exit(0 if 'NOT a novel-topic verdict' in r and '--no-floor' in r else 1)"); echo "study_topic check exit status: $?"
(cd "$AGENT" && python3 -m pytest tests/ -q)
git -C "$AGENT" diff --check
```

Required:
- wake-up reports 3.35.1;
- the `study_topic` check exits 0 (it exits 1 on the 3.35.0 code, which is the rejection path);
- no new receiver test failures against the baseline.

Preserve raw output; do not normalize an unavailable predicate into a pass. Run the test runner directly, not through a wrapper that writes into the Aget, and record it if the working tree changes during verification.

## Rollback

Never reset or rewrite shared history. Revert a committed migration with `git revert`; before commit, restore only the recorded migration path set from `BEFORE_SHA`. Re-run the baseline tests and wake-up, preserve failure evidence, and record `ROLLED_BACK` or `HOLD`. Rolling back returns `study_topic` to reporting a suppressed result as a novel topic.

## Known Items

See the release notes, section "Known limitations". In short:
- this patch carries one specification addition (CAP-VOC-006), a prose rule with no runtime effect, and one identity-definition correction (`Aget_Instance` is now a kind of `Aget_Agent`, not of `Aget_AI_System`);
- the migration kit is not in this release;
- the templates still ship the unrepaired close-authorization guard (`handoffs/CORRECTIONS_v3.35.0.md`, row 4): apply that row's workaround.

## Completion Response

The receiver authors its receipt after exercising the installed subject. Record:
- the core and matching-template annotated tags and peeled full commits;
- the deployment-spec blob;
- the receiver's before and after commits;
- the selected paths and their digests;
- commands, raw observations, timestamps, host and authorized operator;
- limitations and the rollback reference.

A receipt counts as returned only after acknowledged transmission and verification at its source revision. BEHAVIOUR_VERIFIED qualifies only when the credited capability and an exercised rejection path pass and no blocking delivery defect remains; do not rename it ACCEPTED. A producer-authored statement about a receiver is not receiver acceptance. PENDING, HOLD, simulation and installation-only results do not establish delivery.

## Fleet Action Required

1. Confirm the target from the public release list: v3.35.1.
2. Commission one pilot receiver first, and return its receipt before any wider wave.
3. Broadcast availability after the pilot receipt, not before.
4. Report blockers against this handoff, citing the section and the exact command output.

Next release: the weekly train runs every weekend. v3.36.0, the migration kit, rides the first train it is done for.

## Pilot Tracking

| Pilot receiver | Status | Deployment evidence | Blocker | Owner |
|---|---|---|---|---|
| Designated by the receiving fleet's supervisor | Not started | none yet | none recorded | receiving manager |

No qualifying receiver receipt is recorded by this prepared artifact.

## Acknowledgment

- [ ] Supervisor acknowledged this handoff
- [ ] Pilot receiver commissioned
- [ ] Pilot receipt returned and verified at the receiver's source revision
