# REMOTE MIGRATION — AGET v3.28.0 "Make the gates fire"

*(Template: TEMPLATE_REMOTE_MIGRATION_MESSAGE v1.7.0)*

> ⚠ **PUBLIC AND TAGGED** (`v3.28.0` = `572d10d8`, 14/14 repositories in sync, verified 2026-07-26). The
> prior banner said "not yet public"; it was written pre-push under `v328-shipday:R93` and went stale at
> the tag.
>
> ⛔ **The enforcement payload is incomplete — read CORRECTIONS row 3 first.** The firing guard and its
> battery are in **no** public repository, so §Behavioral Smoke probes 1–5 below **cannot pass at your
> seat** this release. Do not hand-copy the guard from the producing seat: it fail-closes on a companion
> that only exists in the framework-release layout, and it fires on *any* `git tag vX.Y.Z`, so installing
> it would refuse every tag your seat ever cuts.

**READ FROM `origin/main`, NOT THE TAG** — corrections and the delivered-files manifest are post-tag
surfaces.

```bash
git fetch origin
git show origin/main:handoffs/CORRECTIONS_v3.28.0.md        # apply every row on top of the tag payload
git show origin/main:release-notes/v3.28.0.md               # THE migration instructions live here (R82)
git show origin/main:handoffs/DELIVERED_FILES_v3.28.0.yaml  # copy-list source — never the tag's copy
```

⚠ Every row in that manifest currently reads `ABSENT-AT-REF`. That is accurate and it is the subject of
CORRECTIONS row 3 — not a fetch error at your end.

**Baseline capture (BEFORE you touch anything)**: save `python3 -m pytest tests/ -q` output and your current
`aget_version`. You will compare against it.

---

## What makes this release different from every prior migration

**Gate behaviour changes. Acts that previously succeeded may now be refused.**

This is the first release whose payload can **block you**. If a `git tag` or `git push --tags` is refused
after you migrate, that is the release working. Do not disable the hook to get past it — read the message,
which names every failing condition.

---

## Behavioral Smoke (MANDATORY — rung 4)

Run these **after** migrating. Each probe verifies the payload *executes*, not that a file arrived.

> ⛔ **Probes 1–5 are NOT RUNNABLE at a consuming seat this release** — the guard they exercise was never
> propagated (CORRECTIONS row 3). They are retained unedited because they are the correct probes and
> because deleting them would hide what is owed. **Probes 6 and 7 are the migration bar for v3.28.0.**
> Report probes 1–5 as `N/A — payload absent`, not as pass.

| # | Feature | Probe (run this) | Expected |
|:-:|---|---|---|
| 1 | Firing guard is registered | `jq -r '.hooks.PreToolUse[].hooks[].command' .claude/settings.json \| grep -c release_gate_firing_guard` | **≥1** |
| 2 | Guard is executable | `test -x .claude/hooks/release_gate_firing_guard.sh && echo ok` | `ok` |
| 3 | Guard **refuses** a release act | `echo '{"hook_event_name":"PreToolUse","tool_input":{"command":"git tag -a v9.9.9 -m t"}}' \| bash .claude/hooks/release_gate_firing_guard.sh; echo "exit=$?"` | `exit=2` **and** `RELEASE GATE FIRING GUARD` on stderr |
| 4 | Guard **passes** ordinary work | `echo '{"hook_event_name":"PreToolUse","tool_input":{"command":"git status"}}' \| bash .claude/hooks/release_gate_firing_guard.sh; echo "exit=$?"` | `exit=0` |
| 5 | Firing ledger records the refusal | `tail -1 .aget/logs/control_firings.jsonl \| jq -r .hook_event` | `PreToolUse` |
| 6 | Version coherence | `jq -r .aget_version .aget/version.json` · `grep '@aget-version' AGENTS.md` · **`grep '@aget-canonical-specs' AGENTS.md`** | first two `3.28.0`; the third's `/tree/vX.Y.Z/` **also** `3.28.0` |
| 7 | Contract suite | `python3 -m pytest tests/ -q` | no NEW failures vs your baseline |
| 8 | **Payload present, AT TRUNK** | `TRUNK=$(git symbolic-ref -q --short refs/remotes/origin/HEAD \| sed 's#^origin/##'); TRUNK=${TRUNK:-main}`<br>`for f in study_topic wind_down check_initiatives close_gate_check; do git show "$TRUNK:$(git rev-parse --show-prefix)scripts/$f.py" \| shasum -a 256 \| sed "s/-/scripts\/$f.py/"; done` | each sha matches `handoffs/DELIVERED_FILES_v3.28.0.yaml` `additive_files` **on `origin/main`** |
| 9 | **Persisted ON TRUNK** | `TRUNK=$(git symbolic-ref -q --short refs/remotes/origin/HEAD \| sed 's#^origin/##'); TRUNK=${TRUNK:-main}`<br>`git show "$TRUNK:$(git rev-parse --show-prefix).aget/version.json" \| jq -r .aget_version` | `3.28.0` — **at trunk, not at `HEAD`, not on disk** |

> **One command instead of probes 8+9:** `python3 scripts/verify_migration_landed.py . --version 3.28.0
> --manifest handoffs/DELIVERED_FILES_v3.28.0.yaml` — resolves trunk (`origin/HEAD` → `main` → `master`,
> and **UNVERIFIABLE rather than a guess** if none resolves), scores both axes at the *same* ref, reports
> working-tree drift separately, and exits 0 only on `LANDED`. Use it in preference to the shell forms
> above; the shell forms are retained because a seat may not have the script.

⛔ **Probes 8 and 9 were added 2026-07-27 and the migration bar is now 6+7+8+9. If you migrated before
then, you have not met it — re-run.** Probes 1–7 as originally published **all read the working tree**.
Three distinct failures pass that battery cleanly, and all three were observed in the field within 24
hours of the tag:

| Failure | What passes | What is false |
|---|---|---|
| **version without payload** | probe 6 — both files say `3.28.0` | the four scripts never landed |
| **payload without persistence** | probes 6, 7, and the smoke — the working tree is correct | nothing is committed; one `git checkout` reverts the migration |
| **`exit=0` without work** | the dispatcher's exit code | the seat could not run `python3` at all and migrated nothing |

Measured in the producing fleet at one instant, 2026-07-27: **17** seats read `3.28.0` on disk · **15**
also carry the payload · **13** also have it at `HEAD`. Four seats claim the version and do not hold it,
in two non-overlapping failure modes. Every count published that day was the 17. *(Those three readings
are `HEAD`-based and therefore over-report — see the trunk correction immediately below. Re-measured
trunk-based 2026-07-29T18:09Z: **29 LANDED · 1 OFF-TRUNK · 1 NOT-APPLIED**. A census is a snapshot; run
the instrument rather than citing this line.)*

### ⛔ CORRECTED 2026-07-29 — probes 8 and 9 read the wrong REF. Re-run if you migrated before this.

**A fourth failure passes the 6+7+8+9 battery as published on 2026-07-27**, and it was found in the field:

| Failure | What passes | What is false |
|---|---|---|
| **committed but OFF-TRUNK** | probes 8 and 9 — `HEAD` carries version *and* payload | the seat's **trunk** is two releases back; the migration lives on an unmerged branch |

`private-career-aget` sat on branch `session/2026-07-17-…` with `HEAD` = `3.28.0` and `main` = **`3.26.0`**.
It passed every `HEAD`-based probe, and the framework seat's own
`verify_migration_landed.py` certified it **LANDED**. A payload on an unmerged branch is not durably
held: abandon the branch and nothing about the seat's trunk changes.

**Both probes now read at trunk**, resolved as `origin/HEAD` → `main` → `master`. `R-FU-014-6` at a
consuming seat had already superseded `HEAD` with trunk; this is canonical converging to it, not the
reverse (`gh#2059`). **A pass under the `HEAD` form is not evidence for the trunk form.**

**Probe 8 had the same defect in a second place**: it hashed the **working tree** while probe 9 read a
commit. Two probes, two refs, one verdict — so the verdict answered no single question, and a seat with any
local edit to a payload file failed probe 8 while its committed state was byte-exact
(`private-professional-core-aget`). Working-tree drift is real information and is now reported
**separately**, never against the bar.

**The repo-root prefix is KEPT, and this is the part most likely to be got wrong when copying the fix.**
`git show <ref>:<path>` resolves from the repository root, so a seat that is a *subdirectory of a monorepo*
must include `$(git rev-parse --show-prefix)` or every such seat reads as un-persisted. That prefix was
always correct — the **ref** was wrong, and nothing else. Dropping the prefix while changing the ref
reintroduces the monorepo false alarm: a correction failing to reach what was derived from it. Omitting it
is a false alarm rather than a false pass, but a check that cries wolf during normal operation gets ignored
exactly when it is right.

⚠ **Probe 6 gained a third surface on 2026-07-27 and you should re-run it if you migrated before then.**
`AGENTS.md` carries **two** version-bearing lines — `@aget-version` and `@aget-canonical-specs`, whose URL
pins a `/tree/vX.Y.Z/` ref. The original probe greped only the first and called the result *"version
coherence"*, so a seat that bumped one line and not the other passed. Measured in the producing fleet
after the fix landed: **4 seats drifted** — `@aget-version: 3.28.0` beside `.../tree/v3.27.0/specs`. Found
by a consuming seat in another fleet reading a diff, not by any check.

⚠ **Probe 3 is the important one, and probes 3+4 must BOTH pass.** A guard that blocks everything gets
disabled, and a disabled guard protects nothing. If 3 passes and 4 fails, stop and report — do not migrate
the fleet.

⚠ **Probe 5 writes a real ledger row with `hook_event: PreToolUse`.** That row is from *your* hand-run of
probe 3, so it is **not** evidence for `GOAL-V328-DELIVERED` leg 3, which requires an **unbidden** firing.
Leave the file in place; genuine firings will accumulate alongside it and are distinguishable by context,
not by this field alone. **Do not cite probe 5's row as leg-3 evidence.**

---

## Rollback

No data formats or artifact schemas changed.

```bash
# restore prior version strings
git checkout HEAD~1 -- .aget/version.json AGENTS.md      # or edit 3.28.0 -> 3.27.0 by hand
# unregister the hook
# (remove the release_gate_firing_guard entry from .claude/settings.json PreToolUse)
```

`.aget/logs/control_firings.jsonl` is append-only and harmless if left behind.

---

## Report back

Two things, both short:

1. **Confirm your version ON TRUNK, and confirm the payload at the same ref** — this closes
   `GOAL-V328-DELIVERED` leg 2.

   ```bash
   # One command, preferred — resolves trunk, scores both axes at that one ref, exit 0 only on LANDED
   python3 scripts/verify_migration_landed.py . --version 3.28.0 \
       --manifest handoffs/DELIVERED_FILES_v3.28.0.yaml

   # Or by hand (trunk = origin/HEAD, else main, else master)
   TRUNK=$(git symbolic-ref -q --short refs/remotes/origin/HEAD | sed 's#^origin/##'); TRUNK=${TRUNK:-main}
   git show "$TRUNK:$(git rev-parse --show-prefix).aget/version.json" | jq -r .aget_version   # probe 9
   git show "$TRUNK:$(git rev-parse --show-prefix)scripts/study_topic.py" | shasum -a 256      # probe 8
   ```

   > **Corrected AGAIN on 2026-07-29 — `HEAD` → trunk.** The 2026-07-27 wording below fixed
   > disk → `HEAD` and stopped one ref short. A seat whose migration sits on an unmerged branch
   > satisfies the `HEAD` form truthfully and holds nothing on its trunk. **A leg-2 confirmation
   > recorded against `HEAD` does not meet the corrected bar** — re-confirm; it is one command.

   > **This standard was corrected on 2026-07-27 and the correction matters.** It previously read
   > *"Confirm your version"*, with no ref. A seat that applies the payload and **cannot commit it**
   > satisfies that sentence **truthfully** — it reads `3.28.0` on disk and says so — while being one
   > `git checkout` from losing the migration. Two seats were in exactly that state when this was found,
   > and both would have closed leg 2 on the old wording. A disk read is not a delivery receipt.
   >
   > `POLICY_release_cadence` **R-REL-CAD-012** gates the v3.29 scope-lock on `GOAL-V328-DELIVERED`, so
   > the old bar would have released the next cycle's gate on work that can evaporate. **A leg-2
   > confirmation recorded before 2026-07-27 does not meet this bar** — it was taken against the disk.
   > Re-confirm at `HEAD`; it is one command.
2. **If any gate refuses something you did not expect**, say so. That is leg 3 substrate and it is the
   framework's most valuable signal from this release.

**Do not manufacture a refusal to help.** A deliberately triggered gate is *invoked*, which
`v328-shipday:R67` excludes from leg 3. The producing seat declined to bank leg 3 twice on that basis.

⚠ **Leg 3 is currently unreachable and that is not your problem to solve.** With the guard absent from
every public repository there is no control at your seat that *can* fire unbidden. Do not attempt to
supply leg-3 evidence for v3.28.0; do not install the guard by hand to create some. The gap is the
producing seat's, it is recorded in CORRECTIONS row 3b, and closing it is v3.29 work.
