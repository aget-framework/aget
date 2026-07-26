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
| 6 | Version coherence | `jq -r .aget_version .aget/version.json` and `grep '@aget-version' AGENTS.md` | both `3.28.0` |
| 7 | Contract suite | `python3 -m pytest tests/ -q` | no NEW failures vs your baseline |

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

1. **Confirm your version** — this closes `GOAL-V328-DELIVERED` leg 2.
2. **If any gate refuses something you did not expect**, say so. That is leg 3 substrate and it is the
   framework's most valuable signal from this release.

**Do not manufacture a refusal to help.** A deliberately triggered gate is *invoked*, which
`v328-shipday:R67` excludes from leg 3. The producing seat declined to bank leg 3 twice on that basis.

⚠ **Leg 3 is currently unreachable and that is not your problem to solve.** With the guard absent from
every public repository there is no control at your seat that *can* fire unbidden. Do not attempt to
supply leg-3 evidence for v3.28.0; do not install the guard by hand to create some. The gap is the
producing seat's, it is recorded in CORRECTIONS row 3b, and closing it is v3.29 work.
