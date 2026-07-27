# CORRECTIONS — v3.28.0

Post-tag corrections for v3.28.0. **This is the single surface** for fixes discovered after the tag; other
artifacts point here rather than being edited (gh#1834 rule 2).

Read from `origin/main`, not the tag.

---

## Row 1 — `DEPLOYMENT_SPEC_v3.28.0.yaml`: 5 of 6 M-row detections verify EXISTENCE, not behaviour

**Found**: 2026-07-26, post-tag, by this seat auditing its own release against the cycle's root-cause finding.

**What is wrong**: every mandatory M-row detection is a `test -f` / `grep -q` / `jq -e` string check. The
sharpest case is **`M-3.28-4`**, whose description reads *"Detection checks the guard **CAN** write it"*
while the detection is:

```
grep -q 'control_firings.jsonl' .claude/hooks/release_gate_firing_guard.sh
```

That greps a file for a **string**. It proves a filename appears in a script. It does **not** prove a single
byte is ever written — and this is the row carrying the entire evidence path for the delivery Goal's leg 3.

**A seat can pass every mandatory row of this spec while shipping a guard that never writes anything.**

**Impact on your migration**: low. The payload itself is correct — the guard *does* write the ledger, verified
at the producing seat and by the smoke probes in `REMOTE_MIGRATION_MESSAGE_v3.28.0.md` (probe 5 returns
`hook_event: PreToolUse`). What is wrong is the **detection**, which would not have caught it had it been
broken.

**What to do**: run **probe 5** rather than relying on `M-3.28-4`. The probe verifies behaviour; the M-row
verifies a string.

**Why this is disclosed rather than silently patched**: the spec is published. v3.27.0 shipped
*"tag-payload post-tag divergence undisclosed in the release body"* by its own quality score, and editing a
published artifact without a correction row is that same defect. A corrected spec ships in v3.29.

**Root**: this is the cycle's own root-cause finding — an edge checked by *name* is a node with extra steps
— reproduced in the release's own deployment contract, written four hours after the finding was recorded.

---

## Row 2 — GitHub release body was initially published in the wrong format

**Found**: 2026-07-26, principal-caught, within an hour of the tag.

The release body was first published as the full deep release notes rather than a conforming release body:
`release_body_gates` reported `conformant=False` (missing `What's New` and `Compatibility`) plus 2 voice
flags. **Corrected the same session**; the live body now passes structure, value and voice gates.

No action required. Recorded because the release body is a consumed surface and its history should be visible.

---

## Row 3 — ⛔ The enforcement payload was never propagated. v3.28.0 is tagged and hollow.

**Found**: 2026-07-26, post-tag, by an audit run against this release's own deliverable **4.4**
(post-tag re-verification of the handover package).

**What is wrong**: every executable artifact this release is named for exists **only on the producing
seat**. Verified by `find` over the working trees and by `git ls-tree -r` at both `origin/main` and the
`v3.28.0` tag — not by grep:

| Artifact | producer | canonical `aget/` | 13 templates | `origin/main` | tag `v3.28.0` |
|---|:--:|:--:|:--:|:--:|:--:|
| `.claude/hooks/release_gate_firing_guard.sh` | ✅ | ✗ | ✗ | ✗ | ✗ |
| `scripts/release_gate_battery.sh` (guard's companion) | ✅ | ✗ | ✗ | ✗ | ✗ |
| `scripts/check_score_independence.py` | ✅ | ✗ → **now present** | ✗ | ✗ | ✗ |
| `scripts/triage_freshness_tick.py` | ✅ | ✗ → **now present** | ✗ | ✗ | ✗ |
| `scripts/check_actuator_census.py` | ✅ | ✗ → **now present** | ✗ | ✗ | ✗ |
| `scripts/check_reference_resolution.py` | ✅ | ✗ → **now present** | ✗ | ✗ | ✗ |
| `tests/test_test_requirements.py` | ✅ | ✗ | ✗ | ✗ | ✗ |

The Upgrade guide's step 2 reads *"Copy `.claude/hooks/release_gate_firing_guard.sh` and register it under
`PreToolUse`."* **There was, and for the hook still is, nowhere to copy it from.**

**Why no gate caught it**: the blocking M-rows use the conditional form `test ! -f X || <check X>`, which
is TRUE when X is absent. A seat that receives nothing passes every mandatory row, and
`verify_deployment.py --version 3.28.0` certifies a clean migration of an empty payload. The form was
adopted the same day, deliberately and for a good reason — a worker template that never tags a framework
release genuinely has no use for a release-gate hook. What it never asked is that canonical `aget/` is not
a *seat* with needs; it is the **distribution point every seat copies from**, and conditionality is
meaningless there.

This is CORRECTIONS row 1's finding one level deeper. Row 1: a detection that checks a *name* does not
check *behaviour*. Row 3: when the payload is absent, a **conditional** detection checks nothing at all.

**Root, stated plainly**: this release's own deliverable 4.4 — *"re-run every M-row detection at canonical
AND ≥1 template **from the tag**"* — was written, correctly scoped, recorded as owed, and not executed
before the session closed. The failure is not that the check did not exist. It is that it was specified
and then discharged into a ledger instead of into fact.

### Row 3b — and the guard could not simply be copied either

Propagating the hook as-is would have been **worse than the hole it fills**. The guard fail-closes on a
missing companion (correctly — *"UNREACHABLE is not PASS (L967)"*), and its companion
`scripts/release_gate_battery.sh:61` checks `../aget/release-notes/v${VER}.md` — a **sibling-repo path that
exists only in the framework-release layout**. The guard also fires on *any* `git tag vX.Y.Z` in *any*
repository, with no applicability predicate.

Installed at a fleet seat, it would therefore refuse **every** semver tag that seat ever cuts, permanently,
with no route past it but unregistering the hook — the precise failure this release's own notes warn
against (*"a guard that fires on everything gets disabled, and a disabled guard protects nothing"*).

**Consequence for the delivery Goal, stated because it is load-bearing**: `DEPLOYMENT_SPEC_v3.28.0.yaml`
rests leg 3 on the supervisor seat installing this hook. Either the guard ships unmodified and bricks that
seat's tagging, or it gains an applicability predicate and never fires there for the supervisor's own
tags. **Leg 3 is unreachable as designed, in both directions** — and `POLICY_release_cadence`
R-REL-CAD-012 gates the v3.29 scope-lock on it.

**What to do**:
1. **Do not hand-copy the guard from the producing seat.** It needs an applicability predicate and its
   companion first. That work is queued, not done.
2. The four checkers are now in canonical `aget/scripts/` and are import- and execution-smoked there. They
   are advisory; expect them to report debt at your seat. That is the disclosed behaviour, not a failed
   migration.
3. Treat `M-3.28-2/-4` as **not satisfiable** this release. They will PASS at your seat vacuously.

---

## Row 4 — Both published migration surfaces told consumers not to migrate

**Found**: 2026-07-26, same audit.

For several hours after the tag went live, `release-notes/v3.28.0.md` opened with *"THIS RELEASE IS NOT
PUBLIC YET… no `v3.28.0` tag exists"* and `RELEASE_HANDOFF_v3.28.0.md` with *"**Do not begin migrating
until the tag is live.**"* Both were written pre-push under `v328-shipday:R93` and went stale at the moment
of the act they were waiting for. The release notes are, by design (`R82`), **the** migration
instructions — so a consuming seat following them correctly would have declined to migrate.

**Fixed**: both banners replaced with the post-tag state. `DEPLOYMENT_SPEC_v3.28.0.yaml`'s header carried
the same claim and is corrected too.

**Why it is recorded rather than quietly deleted**: removing a false banner without a row is the same
undisclosed-divergence defect v3.27.0's own quality score named. Deliverable 4.4 exists precisely to catch
this class; it is the deliverable that did not run.

---

## Row 5 — `DELIVERED_FILES_v3.28.0.yaml` was never emitted, and the emitter could not have seen the hook

**Found**: 2026-07-26, same audit.

SOP_release_process v1.60 Phase 3.0 step 2.5 mandates the emit; v3.26.0 and v3.27.0 both have one; v3.28.0
did not. The manifest is the **copy-list a fleet dispatch derives its add-list from** — consuming it is
what made the #1828 payload-orphan class extinct at v3.26.

**Emitted now** — and every row reads `ABSENT-AT-REF`, which is the defect in row 3 stated
machine-readably.

**But the instrument was itself blind.** On first emit it produced **2 rows for a 7-artifact payload**:

- `PATH_RE` matched only `scripts/` and `.claude/skills/`, so `.claude/hooks/` — **this release's central
  deliverable** — could not be seen. `tests/` was equally invisible.
- The parser's section alternation did not include `recommended_changes`, the heading this spec uses for
  its two edge checkers, so both were dropped silently.

So the correction to the diagnosis is: emitting the manifest at step 2.5 would have caught **2 of 7**
artifacts and stayed silent on the hook. Both defects are fixed in
`scripts/emit_delivered_files_manifest.py`; the re-emit produces 6 rows (the 7th, the battery, is named by
no M-row — a separate gap left recorded rather than papered over).

---

## Row 6 — `REMOTE_MIGRATION_MESSAGE_v3.28.0.md` was private-only

**Found**: 2026-07-26, same audit.

Public at v3.26.0 and v3.27.0; absent from `origin/main` at v3.28.0. It carries the mandatory rung-4
behavioural smoke probes, and no public artifact replicates them. **Published now**, with its stale
pre-push banner corrected and the `DELIVERED_FILES` probe restored to the header block.

---

## Row 7 — v3.28.0 has TWO payloads, and the manifest described only the missing one

**Found**: 2026-07-26 by the **supervisor seat's independent migration-prep audit** — not by this
producer. It verified the finding three ways (`git ls-tree -r` at both refs, `shasum` canonical↔tag, and a
re-run of its own `verify_v328_mrows.sh`) before reporting. Re-verified here at source before acting.

**Rows 3–6 above are correct and incomplete.** They describe the *enforcement* payload, which is absent.
There is a second payload, and it shipped **fine**:

| | Enforcement payload | Fleet-script payload |
|---|---|---|
| Artifacts | firing guard, battery, 3 checkers, traceability test | `study_topic.py`, `check_initiatives.py`, `close_gate_check.py`, `wind_down.py` |
| At tag `v3.28.0` | **0 of 7** | **present**, +585 lines |
| At 13 templates | 0 of 7 | present, byte-identical to canonical |
| Named by an M-row | yes — all VACUOUS | **no — none** |

So the accurate statement is not "the release shipped hollow." It is: **the release shipped its
fleet-facing payload correctly and withheld the enforcement payload it is named for** — and its own
deployment contract covers only the half that is missing.

### The defect this produced, which is worse than the omission

`DELIVERED_FILES_v3.28.0.yaml` is derived **exclusively from DEPLOYMENT_SPEC M-rows**. No M-row names any
of the four fleet scripts, so the manifest could not see them. As first emitted it listed six enforcement
artifacts, **every one `ABSENT-AT-REF`**, and none of the four files agents were actually going to receive.

`SOP_fleet_upgrade` G0.2 instructs a consuming seat to derive its commit add-list from that manifest.
**Following the SOP correctly would have staged zero fleet-facing files.** The correction written to fix a
payload gap became, for one afternoon, a live misdirection of the migration it was meant to unblock.

This is L320's shape (`gmelli/aget-aget#2008`, filed by a third seat the same day) recursing into the
remediation: *a check that cannot distinguish ABSENT from PASSING certifies nothing* — here, a manifest
that cannot distinguish *not-contracted* from *not-shipped*.

**Fixed**: the emitter now cross-checks the template tag diff (`v3.27.0..v3.28.0`) and emits any shipped
file no M-row contracts as an additive row carrying `spec_rows: [NO-M-ROW]`, with a header warning. The
manifest went 6 → **10 rows**; the four fleet scripts now carry real sha256 values matching the template
tag, so a hash-verified add-list is possible.

**What to do**: derive your add-list from the **full** manifest — `delivered_files` + `optional_files` +
**`additive_files`**. A mandatory-rows-only reading of v3.28.0 yields nothing.

**Still owed, not done**: the four scripts have no M-rows, so nothing verifies their arrival at a seat.
That is a DEPLOYMENT_SPEC gap and it is v3.29 work — recorded rather than back-filled into a published
contract.

**Credit**: the two-payload distinction, the G0.2 add-list consequence, and the `.aget/logs/` ledger-channel
gap are the supervisor seat's findings. This producer verified its own release twice and found neither.


---

## Row 8 — the BLOCKING pre-release check this release claims to have fixed is still unpassable

**Found**: 2026-07-26 evening, chasing a suite-runtime question the supervisor seat raised. Its premise was
different and one of its inferences does not hold (see below), but the instinct was right and neither seat
had this.

**The release notes' §Fixed states**:

> *"Pre-release validation ran the full contract suite under a 60-second timeout against a suite that took
> **528 seconds** — 81% of it inside three tests that each re-ran the entire release battery. A BLOCKING
> check was structurally unpassable, so its failure had become background noise."*

**The suite was fixed. The timeout was not.**

| | |
|---|---|
| `.aget/patterns/release/pre_release_validation.py:166` | `timeout=60` — unchanged |
| `:178` | `return False, "❌ Tests timeout (>60s)"` |
| Measured suite, 2026-07-26 | **684 passed, 1 skipped, 1 xfailed, 144.45s** |

144 > 60. The check is **still structurally unpassable**, and `validate_release_gate.py --version 3.28.0
--phase pre-release` returns **`GATE BLOCKED — 1 blocking failure`** at the producing seat right now:
`❌ FAIL: Pre-Release Validation [BLOCKING] (60.3s)`.

The cycle reduced the numerator by 3.7× and left the denominator alone. The theme was *make the gates
fire*; this gate fires, fails, and its failure is once again the background noise the entry describes.

**What I cannot resolve from here**: the cycle's record also claims *"7/8, 0 blocking — GATE OPEN"* and a
*"~30s"* suite. Both cannot be true alongside a 60s timeout and a 144s suite. Either the suite has slowed
~4.8× since the tag, or the GATE OPEN claim was already false when recorded. Distinguishing them requires
measuring the suite at the tagged tree, which this correction does not do — stated rather than guessed,
because this seat has already published one figure this cycle that did not survive re-measurement.

**Impact on your migration: none.** Probe 7 is *"no NEW failures vs your baseline"* and carries no time
bound; the suite is **green**. This is a v3.29 release-process finding, not a migration blocker.

**Owed, not done**: raise the timeout to fit the real suite (or split the suite), then re-derive the gate
result and reconcile the two published figures.
