# Release Handoff — AGET v3.35.0

Target version: 3.35.0. Prepared 2026-09-25 for publication on 2026-09-26; publication and adoption unverified.

## Release Summary

Theme: receiver correctness. This release carries three outcomes, described in [the release notes](../release-notes/v3.35.0.md): proposed actions that say what they move, with a deferral scan that reads what is on disk; an advisory CI rule for host-independent tests; and a strict close gate that runs in Agets created from templates. Breaking changes: none. Consume the exact public core and matching-template tags, preserve receiver state, and exercise the capability credited to this upgrade. Before accepting, read the known limitations in the release notes and every row of `handoffs/CORRECTIONS_v3.35.0.md` on `main`.

## Context for External Fleets

External fleets must treat availability, acquisition, installation, behavioural verification and acceptance as separate states. This handoff is an information and verification contract, not authority to modify a receiver. Each receiving manager applies its own governance, preserves local extensions, and returns evidence from the receiver itself. No operator-specific path, private inventory or fleet-wide deployment claim is embedded in this public artifact.

### What is the deferral scan?
- **Problem it solves**: `/aget-propose-actions` must not propose work that a recent handoff document deliberately parked. The earlier scan looked only in `docs/`, and its selector either treated every handoff in a fresh clone as recent or could not see an untracked one.
- **What it does**: `scripts/propose_actions_handoff_scan.py` lists handoff documents committed inside the window, by authored date, plus untracked or locally modified ones. It reports `MATCHED`, `NONE-MATCHED`, `NO-CANDIDATES` or `UNAVAILABLE`; `UNAVAILABLE` is never a pass.
- **Configure it** when your Aget keeps handoffs elsewhere: `.aget/config.json`, key `propose_actions.handoff_locations`, a list of repository-relative directories. The default is `docs`, `planning` and `inbox/outbound`.

### What is the strict close gate?
- **Problem it solves**: `/aget-close-project` must not mark a project complete while gates, V-tests or closure items are still open.
- **What it does**: `scripts/close_gate_check.py` evaluates the plan in an entry phase and an exit phase, using `scripts/close_gate_lifecycle.py` and the lifecycle rows in `specs/AGET_PROJECT_PLAN_SPEC.md`. The three files are one unit.
- **What it does not do**: it does not catch every unfinished status wording. See Known Items.

### What is CAP-CI-010?
An advisory requirement in `specs/AGET_CI_SPEC.md` v1.5.0: declare any dependence on something outside the repository checkout as a precondition, and skip without it; never weaken the assertion. No receiver action is required.

### Archetype Divergence
The payload is the same for all 13 archetypes. One existing gap closes: the document-processor template carried the propose-actions skill without `scripts/propose_actions_classify.py`; it now receives both scripts.

## Script Deployment

| Path | Change | Surfaces |
|---|---|---|
| `scripts/propose_actions_handoff_scan.py` | new | core, 13 templates |
| `scripts/propose_actions_classify.py` | updated; new in the document-processor template | core, 13 templates |
| `.claude/skills/aget-propose-actions/SKILL.md` | v1.9.0 | core, 13 templates |
| `scripts/close_gate_lifecycle.py` | new in templates (already in core) | 13 templates |
| `specs/AGET_PROJECT_PLAN_SPEC.md` | new in templates; editorial change in core | core, 13 templates |
| `.claude/skills/aget-close-project/SKILL.md` | replaced by the core copy | 13 templates |
| `specs/AGET_CI_SPEC.md` | v1.5.0, adds CAP-CI-010 | core |
| `governance/DEPRECATIONS.md` | DEP-BASENAME-VPP-001 moved to Closed | core |

## Breaking Changes

None. Two deprecation removals are described under Removals; neither removes a file that any shipped repository carried.

## Removals

**DEP-BASENAME-VPP-001, the script name `scripts/validate_project_plan.py`.** Originally deprecated in 3.32.0 and announced in the public registry `governance/DEPRECATIONS.md`, which first shipped with 3.32.0. Grace period satisfied: marked 3.32.0, carried 3.33, removable from 3.34.0, removed 3.35.0. Migration: use `scripts/validate_execution_authorization.py` for the authorization gate and `verification/validate_project_plan.py <path> --strict` for plan conformance. No shipped repository carried the shim. Not a breaking change.

**A retired release-closure requirement.** A five-row behavioural-verification matrix in the producer's release procedure. Its closure force was withdrawn on 2026-08-29; it was carried through two minor releases and removed in 3.35.0 as scheduled. It was never part of the shipped framework; no migration is needed.

## Receiving-Agent Governance Checklist

- [ ] Obtain receiver-local approval and record the applicable migration procedure.
- [ ] Capture the pre-upgrade commit, version, dirty paths and full-test baseline before any payload lands.
- [ ] Verify the annotated core and matching-template `v3.35.0` tags and record their peeled commits.
- [ ] Read `DEPLOYMENT_SPEC_v3.35.0.yaml` from the peeled core tag, and `handoffs/CORRECTIONS_v3.35.0.md` from `main`.
- [ ] Diff every selected destination and preserve receiver-owned extensions.
- [ ] Prepare an exact rollback reference before changing anything.

## Deployment Requirements

Python 3.10 or later, immutable tag-bound sources, a matching archetype template, a recorded receiver baseline and a rollback reference are required. Missing evidence is `HOLD`, never an inferred pass.

Install a skill only together with the scripts it calls. `/aget-propose-actions` needs `scripts/propose_actions_handoff_scan.py` and `scripts/propose_actions_classify.py`. `/aget-close-project` needs `scripts/close_gate_check.py`, `scripts/close_gate_lifecycle.py` and `specs/AGET_PROJECT_PLAN_SPEC.md`, all from the same tag; mixing versions makes the gate fail closed with a schema error (exit 3).

If your Aget installed the 3.31.1 close-gate package, it may carry its own copy of `tests/test_close_gate_receiver_contract.py` and `handoffs/DELIVERED_FILES_v3.31.1.yaml`, rebound to your repository. Taking the 3.35.0 `specs/AGET_PROJECT_PLAN_SPEC.md` turns such a copy red if it pins the earlier specification digest. Either refresh the test from this release, which reads the 3.31.1 tag and skips with a declared precondition where that tag is absent, or keep the local skip you already carry. Do not overwrite a local skip without replacing it. Record which you chose in your receipt.

## Upgrade Guide

Run this block as one Bash script; stop on any failed command. It reads payload bytes from tag objects and checks nothing out, so a source clone shared by several Agets is never switched under another migration.

```bash
set -euo pipefail
export SOURCE=/path/to/aget
export TEMPLATE=/path/to/matching-template
export AGENT=/path/to/receiving-agent

git -C "$SOURCE" fetch --tags origin
test "$(git -C "$SOURCE" cat-file -t refs/tags/v3.35.0)" = tag
CORE_SHA=$(git -C "$SOURCE" rev-parse --verify 'v3.35.0^{commit}')
git -C "$SOURCE" show v3.35.0:.aget/version.json | python3 -c 'import json,sys; assert json.load(sys.stdin)["aget_version"] == "3.35.0"'
git -C "$SOURCE" cat-file -e v3.35.0:DEPLOYMENT_SPEC_v3.35.0.yaml

git -C "$TEMPLATE" fetch --tags origin
test "$(git -C "$TEMPLATE" cat-file -t refs/tags/v3.35.0)" = tag
TEMPLATE_SHA=$(git -C "$TEMPLATE" rev-parse --verify 'v3.35.0^{commit}')
echo "core $CORE_SHA template $TEMPLATE_SHA"

BEFORE_SHA=$(git -C "$AGENT" rev-parse HEAD)
git -C "$AGENT" status --short
(cd "$AGENT" && python3 -m pytest tests/ -q)
```

Compare each payload path with your copy before writing, and preserve local extensions:

```bash
for p in scripts/propose_actions_handoff_scan.py scripts/propose_actions_classify.py .claude/skills/aget-propose-actions/SKILL.md scripts/close_gate_lifecycle.py specs/AGET_PROJECT_PLAN_SPEC.md .claude/skills/aget-close-project/SKILL.md; do
  if [ -f "$AGENT/$p" ]; then
    git -C "$TEMPLATE" show "v3.35.0:$p" | diff -q - "$AGENT/$p" || echo "DIFFERS: $p (merge; keep local extensions)"
  else
    echo "NEW: $p"
  fi
done
```

Write a path only after its difference is resolved, for example `git -C "$TEMPLATE" show "v3.35.0:<path>" > "$AGENT/<path>"`, and record source and destination blob identities. Change version strings only after the payload is in place.

### Text Replacement Table

| File | From | To |
|---|---|---|
| `.aget/version.json` | `"aget_version": "3.34.0"` | `"aget_version": "3.35.0"`, plus a `migration_history` entry |
| `AGENTS.md` | `@aget-version: 3.34.0` | `@aget-version: 3.35.0` |
| `AGENTS.md`, template-derived Agets | `/tree/v3.34.0/specs` | `/tree/v3.35.0/specs` |

## Smoke Test

```bash
(cd "$AGENT" && python3 scripts/wake_up.py)
(cd "$AGENT" && python3 scripts/propose_actions_handoff_scan.py --self-test)
(cd "$AGENT" && python3 scripts/propose_actions_classify.py --self-test)
(cd "$AGENT" && python3 scripts/close_gate_check.py --help)
F=$(mktemp -d)/PROJECT_PLAN_smoke.md
printf '%s\n' '# PROJECT_PLAN: smoke' '' '**Plan_Status**: In Progress' '' '**Gate_Status**: Pending' > "$F"
(cd "$AGENT" && python3 scripts/close_gate_check.py --json --phase entry --disposition Complete "$F"); echo "gate exit status: $?"
(cd "$AGENT" && python3 -m pytest tests/ -q)
git -C "$AGENT" diff --check
```

Required:
- wake-up reports 3.35.0;
- both self-tests exit 0;
- the gate's `--help` exits 0, which shows the gate imports;
- the fixture plan returns exit status 2 with a finding keyed `gate_status_pending`, which shows the gate evaluated the plan;
- no new receiver test failures against the baseline.

A module-not-found error, or exit status 3 with a schema error, means the close-gate package is incomplete or mixed across versions. Preserve raw output; do not normalize an unavailable predicate into a pass. Run the test runner directly, not through a wrapper that writes into the Aget, and record it if the working tree changes during verification.

## Rollback

Never reset or rewrite shared history. Revert a committed migration with `git revert`; before commit, restore only the recorded migration path set from `BEFORE_SHA`. Re-run the baseline tests and wake-up, preserve failure evidence, and record `ROLLED_BACK` or `HOLD`. Rolling back the close-gate package returns a template-derived Aget to a gate that stops on import: that is the pre-upgrade state, not a safe one.

## Known Items

See the release notes, section "Known limitations and disclosures", and `handoffs/CORRECTIONS_v3.35.0.md` on `main`. In short:
- the close gate runs but does not catch every unfinished status wording;
- the close-project skill cites requirement IDs and tests the framework does not ship;
- the deployment specification stays `prepared` at the tag, by a waiver for v3.35.0 only.

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

1. Confirm the target from the public release list: v3.35.0.
2. Commission one pilot receiver first, and return its receipt before any wider wave.
3. Broadcast availability after the pilot receipt, not before.
4. Report blockers against this handoff, citing the section and the exact command output.

Next release: v3.36.0 is planned as a weekly, landed-first release, built through Thu 2026-10-01 and planned for publication on Sat 2026-10-03. Items deferred from 3.35.0 are candidates for it.

## Pilot Tracking

| Pilot receiver | Status | Deployment evidence | Blocker | Owner |
|---|---|---|---|---|
| Designated by the receiving fleet's supervisor | Not started | none yet | none recorded | receiving manager |

No qualifying receiver receipt is recorded by this prepared artifact.

## Acknowledgment

- [ ] Supervisor acknowledged this handoff
- [ ] Pilot receiver commissioned
- [ ] Pilot receipt returned and verified at the receiver's source revision
