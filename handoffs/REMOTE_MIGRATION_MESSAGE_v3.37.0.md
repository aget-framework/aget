# Migration Message: v3.36.0 to v3.37.0

**Date**: 2026-10-17
**From**: AGET Framework Manager
**To**: Remote Fleet Supervisors
**Target Version**: 3.37.0
**Previous Release**: v3.36.0
**Migration Path**: v3.36.0 to v3.37.0; earlier versions must reconcile the intervening handoffs first.
**Breaking Changes**: No public interface removal; stricter launch and payload refusals apply.
**Release identity**: Publication is evidenced by the annotated tag `v3.37.0` and its GitHub Release object. Read the tag's peeled commit with `git rev-parse 'v3.37.0^{commit}'`; a file inside the tagged commit cannot name it.
**Currency note**: Read this message and any corrections from the producer's main branch. Check release availability and the final tag's peeled commit before acting. This build establishes neither.

## Migration Target

Verify the annotated core tag `v3.37.0` and its GitHub Release object; read the peeled commit with `git rev-parse 'v3.37.0^{commit}'`, and verify the corresponding template tag for each receiver. Stop if release identity cannot be verified. Read `handoffs/CORRECTIONS_v3.37.0.md` on the current main branch if it exists; absence means no correction has been filed. No delivered-files manifest is published: use the verified tag tree and `DEPLOYMENT_SPEC_v3.37.0.yaml`.

## What's New in v3.37.0

- Core and template tests isolate inherited git location; template deployment item M-3.37-6 carries `tests/conftest.py` and `tests/test_conftest_git_env_isolation.py`. A body's runtime skip stays a skip, and the launch prompt tells the receiver session to stage new protected files that git does not ignore, without editing them.
- Scope-only principal approvals are refused as launch authority, whether recorded in the active ledger or preserved in the permanent, append-only `data/scope_archive.jsonl` beside the ledgers; old-format scope records block launches until retired.
- The adoption kit checks fleet skew before ledger creation and the supervisor upgrade (SOP once-per-release setup), and checks root instruction files after apply (SOP Part B step B7a). Its whole-line pin allowlist includes the templates' long canonical-specification reliance form.
- Core CI pins Ubuntu 24.04 with checkout v7 and setup-python v7. Verify template workflow delivery separately.
- Template payloads filter compiled caches; the fleet gate reads each template's complete tree at the tag, while the pre-tag gate reads the committed tree under its working directory or `--cwd`. Run the pre-tag gate from the repository root or pass that root as `--cwd`. Wind-down reports TIMEOUT and ERROR distinctly; observation-free results report UNKNOWN with exit 0 and `clean_close` true. Only health status `error` makes wind-down exit 2; read the Health Gate line.

## Retained from the previous release, v3.36.0

The supervisor migration kit, typed per-act authority, batch procedure and close-out gate are retained. Earlier disclosures apply unless explicitly repaired in the new release notes. Read `handoffs/CORRECTIONS_v3.36.0.md` before upgrading.

## Breaking Changes

No public interface removal. Expect refusals for scope prompts reused as launch authority, old-format scope records and compiled-cache payloads. Observation-free health results report UNKNOWN but still exit 0 with `clean_close` true; only health status `error` makes wind-down exit 2. Scope retirement preserves the evidence in the permanent archive; read Known Gaps for the trust limits.

## Deployment Requirements

Core requires Python 3.10+; the migration kit's test-body witness needs Python 3.12+. Copy the whole `scripts/migration_kit/` from the pinned core tree into the supervisor. The kit is separate from the template payload. Its session authority tools depend on Claude Code transcripts. Configure the actual source version and `3.37.0` target explicitly.

## Upgrade Guide

### Requirement

The `python3` your supervisor session uses must import PyYAML and pytest (the kit runs both); check with `python3 -c "import yaml, pytest"`.

### Prerequisites (complete before seeding)

Run these commands from the supervisor root. Replace `<core-clone>` with the core checkout and use its verified release tree.

1. Verify release identity: `git -C <core-clone> cat-file -t v3.37.0` must read `tag`; read the peeled commit with `git -C <core-clone> rev-parse 'v3.37.0^{commit}'` and check out that exact commit. Publication is evidenced by the annotated tag and its GitHub Release object. Verify the corresponding template tags too. Save the supervisor's baseline commit, source version, tree status and local extensions; read the handoff and inherited corrections. Read any current `handoffs/CORRECTIONS_v3.37.0.md` from producer main. Offline, local tag inspection cannot establish the Release object or current-main currency; stop release verification if those are unavailable.
2. Physically copy the whole kit into the supervisor at `scripts/migration_kit/`, saving any installed kit outside this destination first so the copy replaces the whole directory:

   ```bash
   mkdir -p scripts
   cp -R <core-clone>/scripts/migration_kit scripts/
   ```

3. Review or declare `.aget/adoption_policy.json`, including skew limits, minimum release age (`min_release_age_days`) and Wave-1 soak (`wave1_soak`), before running the skew check; its declarations extend the defaults for every member checked. Before deciding to adopt, run `python3 scripts/migration_kit/adoption_policy.py --check-age --published 2026-10-17 --release 3.37.0`; stop on exit 1 or 2. Wait for the declared Wave-1 soak before Wave 2, as required by the SOP's adoption checks.
4. Commit the exact production register bytes at `.aget/fleet/FLEET_STATE.yaml` in this supervisor repository before choosing `register_pin`. Stop on a dirty or unpinned register. A source commit from another repository does not pin a data-only copy. Set `.aget/migration_target.json` using the actual fields read by `release_target.py`: `from`, `to`, `register_pin`, `pinned_members`, `framework_root`, optional `pilots` (a list of pilot member names), and optional `producer` (the release producer when it is also a local fleet member; omit for remote fleets). This concrete example migrates from 3.36.0 to 3.37.0 and derives the member setting from the pinned register, rather than a batch size:

```bash
mkdir -p .aget
python3 - <<'PY'
import json
import subprocess
from pathlib import Path
import yaml

register_path = ".aget/fleet/FLEET_STATE.yaml"
pin = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
pinned = subprocess.check_output(["git", "show", f"{pin}:{register_path}"])
if Path(register_path).read_bytes() != pinned:
    raise SystemExit("STOP: commit the exact register bytes before configuring the target")
register = yaml.safe_load(pinned)
members = [agent for group in register["fleet"].values() if isinstance(group, dict)
           for agent in (group.get("agents") or [])
           if agent.get("agent_name") and agent.get("location")]
target = {"from": "3.36.0", "to": "3.37.0", "register_pin": pin,
          "pinned_members": len(members), "framework_root": "../aget-framework"}
Path(".aget/migration_target.json").write_text(json.dumps(target, indent=2) + "\n")
PY
```

Add `pilots` with the register names of the chosen pilots before readiness checks. Adjust `from` to the actual source version and `framework_root` to the folder holding `aget/` plus the template clones, with both source and target release tags available. Keep different source versions in separate batches. Existing `AGET_MIGRATION_*` and `AGET_FRAMEWORK_ROOT` environment settings override the file; remove stale overrides before proceeding.

5. Run `python3 scripts/migration_kit/check_fleet_skew.py --json` against the configured target before creating a ledger, seeding the permanent archive or upgrading the supervisor. Read the verdict: stop on BLOCKED or UNAVAILABLE. Bring floor members up in a separate migration with the appropriate target, then reconfigure this target and rerun the check before continuing.
6. Create the active ledger `data/v337_ledger/records.json` containing `{}` if it does not already exist. Preserve an existing ledger and its history:

   ```bash
   mkdir -p data/v337_ledger
   if [ ! -e data/v337_ledger/records.json ]; then
       printf '{}\n' > data/v337_ledger/records.json
   fi
   ```

### Seed before any launch

After all prerequisites, seed every earlier ledger that exists in `data/` AND the active ledger. From the supervisor root, the full command form is `python3 scripts/migration_kit/record_authority.py --archive-ledger data/<ledger>/records.json`. For each earlier ledger that exists, seed its scope history, then seed the active ledger. This example skips absent earlier ledgers:

```bash
if [ -e data/v335_ledger/records.json ]; then
    python3 scripts/migration_kit/record_authority.py --archive-ledger data/v335_ledger/records.json
fi
if [ -e data/v336_ledger/records.json ]; then
    python3 scripts/migration_kit/record_authority.py --archive-ledger data/v336_ledger/records.json
fi
python3 scripts/migration_kit/record_authority.py --archive-ledger data/v337_ledger/records.json
```

Repeat for every other earlier ledger that exists. Seeding appends to `data/scope_archive.jsonl` beside the ledgers and updates the active ledger's anchor; a different old source ledger remains unchanged. The gate names unseeded ledgers and refuses launches until all are seeded. Use exact-case paths on case-insensitive disks. Commit the archive and ledgers together; never delete or edit the archive.

If a missing active ledger produces a refusal ending `repair or move it out of the data folder`, complete prerequisite 6, then repeat seeding; that refusal's remedy does not describe fresh-ledger setup.

### Continue the migration

In `sops/SOP_fleet_migration.md`, complete the remaining **Set up once per release** rows (including run root, supervisor name, batch session settings, batch-line prefix and transcripts), the batch-folder paragraph and **The migration's record** under **Kit Batch Procedure**, and **Part A — per-release inputs**. After seeding and before any Wave-1 work, follow **Wave Sequencing / Wave-0 Supervisor Self-Upgrade**, steps 1–3, for this supervisor's upgrade. The supervisor does not go through Part B as a member of its own batch. Then start Wave 1 with the pilots and run **Part B — the fixed procedure**, steps B0–B13, in order.

#### v3.37.0 notes for Part B

- At B1, inspect retained external template symlinks for containment; compiled-cache filtering does not establish that retained links stay within the template.
- At B5, if a stale target caused seeding of the previous active ledger and the gate prints a refusal containing `scope archive has no ledger anchor; run record_authority.py --anchor-archive`, correct the target, create the new active ledger and repeat seeding including the active ledger; re-anchor with `python3 scripts/migration_kit/record_authority.py --anchor-archive` only after verifying the archive's complete history, never to bless lost evidence.
- At B7a, inspect nested instructions, local overrides and rules separately because the halt check covers only root `AGENTS.md` and `CLAUDE.md`.
- At B8, verify the version pin against `3.37.0` and record the unchanged `@aget-canonical-specs` pin for its separate reviewed update outside the kit batch and after-run window.

## Migration Kit: Shown and Not Shown

The candidate contains regression tests for the receiver fixes, adoption checks, payload gates and wind-down results. The builder's actual validation record supplies local test outcomes. This message claims no live migration to the final commit, hosted CI result, published template payload, successful fleet close-out or Ubuntu 26.04 qualification. Historical v3.36.0 rehearsals do not establish these outcomes for v3.37.0.

## Known Gaps

- The test-body witness can misclassify completion for injected skips, plain-closure decorators and `subTest` skips; see [Known limitations and disclosures](../release-notes/v3.37.0.md#known-limitations-and-disclosures), including the payload and health limitations.
- Propagation of the repaired close-authorization guard to the templates remains deferred; follow `handoffs/CORRECTIONS_v3.35.0.md` rows 4 and 5 until a template tag carries the repair.
- The kit changes only the root `@aget-version` line; it does not update `@aget-canonical-specs`. Verify the version against 3.37.0 and record the unchanged specification pin. Change that specification pin in a separate reviewed commit outside the kit batch and after-run window, then verify it against the intended release. Editing it inside that window fails the protected-file checks.
- Kit halt_check checks only root AGENTS.md/CLAUDE.md; a near-match-all receiver declaration can pass validation; pins are not bound to the target release. Inspect other instructions and pins separately.
- Scope evidence survives retirement in the permanent, append-only `data/scope_archive.jsonl`, beside the ledgers. The gate checks every ledger in the data folder and its archive anchor (row count and rolling hash). It refuses a missing, shortened or mismatched archive, a moved anchor, and symlinked ledger or archive paths. Commit the archive and ledgers together; never delete or edit the archive.
- A scope instruction that was never recorded cannot be recognised — type launches as separate prompts. The ledgers and archive are one trust domain: consistent edits of both, or rolling back the whole data folder, can remove the evidence. The kit locates its code directory by resolving symlinks; a replaced code directory pointing at another kit's data is outside the protection. On case-insensitive disks, seed with the exact-case path.
- Template symlink containment: a tracked symlink pointing outside a template is kept. Review retained links explicitly.
- Ubuntu 26.04 qualification not yet done. Hosted validation of the runner pin and action majors remains separate.
- The test-body witness needs Python 3.12+. Earlier kit labels, payload lists and fixed validation commands remain. Read the previous release's limitations where these were not explicitly repaired.
- Wind-down descendants outside the health process group may survive; pipe draining adds at most five seconds. TIMEOUT alone does not fail session close.

## Report Back

Return the release handoff's Completion Response: actual versions, baseline/final commits, status, deployed paths, preserved extensions, tests, halt results, health observations and exact-commit hosted CI where required. Include refusals verbatim, documents needed beyond the handoff and procedure, producer interventions and commands handed to the principal. Mark unresolved work HOLD and retain its evidence.

## Rollback

Never rewrite shared history or move published tags. Revert committed migration changes with `git revert`; before commit restore only recorded migration paths from the saved baseline. Re-run baseline tests and wake-up, and record ROLLED_BACK or HOLD. Supervisor records, archives and temporary run directories survive a kit revert.

## Fleet Coordination

Use the SOP's adoption checks, **Wave Sequencing / Wave-0 Supervisor Self-Upgrade**, steps 1–3, and Part B for fleet coordination, including the declared Wave-1 soak before Wave 2; obtain producer acknowledgment of the receipt. Final core SHA, publication, template tags, hosted CI, prior-release closure and the required external receipt or explicit release exception remain TO CONFIRM.

## References

- `CHANGELOG.md`
- `release-notes/v3.37.0.md`
- `handoffs/RELEASE_HANDOFF_v3.37.0.md`
- `sops/SOP_fleet_migration.md`
