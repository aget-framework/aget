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
