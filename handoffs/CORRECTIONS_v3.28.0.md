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
rests leg 3 on `private-supervisor-AGET` installing this hook. Either the guard ships unmodified and bricks that
seat's tagging, or it gains an applicability predicate and never fires there for that seat's own
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

**Found**: 2026-07-26 by **`private-supervisor-AGET`**'s independent migration-prep audit — not by this
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
gap are `private-supervisor-AGET`'s findings. This producer verified its own release twice and found neither.


---

## Row 8 — the BLOCKING pre-release check this release claims to have fixed is still unpassable

**Found**: 2026-07-26 evening, chasing a suite-runtime question `private-supervisor-AGET` raised. Its premise was
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


---

## Row 9 — a self-replicating commit loop can fire during YOUR migration; the published diagnosis was wrong

**Found**: 2026-07-26, during the fleet wave. **Diagnosed correctly only on the fourth firing.**

**What happens**: a migrating seat is instructed to run its contract suite (baseline, then post-migration
probe). At some seats that suite commits to the live repository and re-invokes itself. Observed:
**527 junk commits in 67 minutes, unattended**, `.git` to 305 MB, `.aget/evolution/index.json` corrupted by
concurrent writers. Nothing was pushed, so damage stayed local — but the seat's history needs surgery.

**The mechanism, stated correctly.** An earlier issue attributed this to unmocked `wind_down_pattern()`
call sites in `tests/`. **That diagnosis is false and was falsified in both directions the same day**: one
seat carried the call sites and never detonated (not sufficient); another guarded every one and detonated
anyway (not necessary). The actual cause is a `Path.cwd()` default in a vendored command module reached
through `init --with-patterns`, which applies patterns to the *current* directory rather than the one it
just created. A second `Path.cwd()` on the evolution path explains an accompanying file hoard.

**Scope, measured**: the vendored `aget/config/commands/` package is present at **8 of 31 seats** in this
fleet, all 8 carrying the defect. It is **not shipped by canonical `aget/` and not present at the
`v3.28.0` tag** — there is no importable package, no console entry point, and `import aget` fails on a
migrated host. It is legacy vendored code that only a seat's own test suite reaches.

**What to do at your seat**:

1. Before running any suite during migration, assert the **two-clause gate** — `git rev-list --count HEAD`
   *and* `git status --porcelain` unchanged across the run. The count clause alone is insufficient: a clean
   count passed a run that wrote 18 untracked files.
2. If your suite mutates the repo, **bisect per file** with that gate rather than guessing at call sites.
   `--deselect` the igniter, run the rest, and report the probe **PARTIAL naming the deselection** — never
   as a clean pass.
3. If you carry `aget/config/commands/`, check whether anything outside your tests reaches it. If nothing
   does, **deleting the vendored package removes the ignition source permanently** — a stronger fix than
   correcting its argument handling, which repairs code no user path reaches.

**Not claimed**: that this is a user-facing defect in a shipped command. On the fleet's filesystem there is
no route by which a user reaches it. That negative is bounded to what was measurable here; if the package
ships from a source not visible on this host, this row does not cover it.

**Durable procedure from this incident** — the two-clause gate, divergence-scaled timeouts, two-signal
liveness, and executed-surface verification — is in `sops/SOP_fleet_migration.md` **§Dispatch Safety**
(v1.8.0), not here. This row is the v3.28-specific fact; that section is the procedure.


---

## Row 10 — CORRECTING ROW 8: the gate failure was real, my diagnosis of it was not

**Found**: 2026-07-26, hours after row 8 was published, while fixing the thing row 8 described.

Row 8 asserts: *"The suite was fixed 528 → 144s. The 60s timeout was never raised. 144 > 60 — the check
is still structurally unpassable."*

**The 144.45s figure is load-contaminated.** Re-measured with the identical command
(`pytest tests/ -q --no-header -p no:cacheprovider`):

| | Tests | Wall |
|---|---|---|
| Original measurement | 684 passed | **144.45s** |
| Clean re-measurement | 699 passed | **31.25s** |

The first was taken while three agent sessions and a self-replicating pytest loop at another seat were
competing for CPU — the same evening's incident. **31 < 60 comfortably**, so the check is *not*
structurally unpassable, and the v3.28 suite fix was not incomplete.

**What survives, and it is not nothing**: the gate *did* return `❌ Tests timeout (>60s)` and
`FAIL: Pre-Release Validation [BLOCKING]` at the producing seat. That was observed, not inferred. A
BLOCKING release gate that fails under ordinary multi-session load on a shared machine is a real defect —
just a **different** one than "the timeout was never raised."

**What changed as a result** (`.aget/patterns/release/pre_release_validation.py`): budget 60s → 300s, sized
against the *contended* observation rather than the quiet one, because a budget that only holds on an idle
machine reproduces the defect elsewhere. And `-v` → `-q`: the gate needs an exit code and a count, and
rendering 699 verbose result lines is work done to be discarded. Gate now returns
`✅ All tests passed (699 tests, 37s / 300s budget)`.

**Why this row exists rather than an edit to row 8.** Row 8 is published and consumed. Silently correcting
a number in it is the undisclosed-divergence defect this file exists to prevent — the same rule row 1
invokes against a published spec.

**The transferable part**: row 8 named its instrument (`pytest -q`, the file, the line numbers) and did not
name its **conditions**. A wall-clock measurement on a shared machine is a claim about the machine as much
as the code. `L1220 §Count` says name the instrument; this says the instrument is not sufficient when the
quantity is time.


---

## Row 11 — "the supervisor seat" was ambiguous across fleets, and a remote seat paid for it

**Found**: 2026-07-26 late, by `private-legalon-supervisor-AGET` — a supervisor in a **different fleet**,
reading these artifacts as its only source while planning its own v3.28.0 wave.

Rows 3b/7/8 and the manifest's `verify_rule` credited findings to *"the supervisor seat"*, unqualified,
five times across two public artifacts. There is more than one. That seat wrote:

> *"CORRECTIONS rows 7 and the manifest's own `verify_rule` both credit 'the supervisor seat'…
> **Unverified at this seat** — no `verify_v328_mrows.sh` exists here and no session note today mentions
> v3.28. **Treat as a peer seat's work until probed, not as ours.**"*

It could not determine whether it was being credited with work it had not done, and had to park the
question. **Fixed**: all five now read `private-supervisor-AGET`. The manifest was re-emitted rather than
hand-edited, so its generator carries the fix too.

**Why this is a correction row and not a typo fix.** A seat name in a public artifact is an
**identifier**, and an unqualified one resolves at the *reading* seat — the same failure this framework
already rules on for L-doc citations, where `LNNN` without a seat prefix is *"a coin-flip, not a
citation."* That rule was written for lesson IDs and never extended to prose references, which is the
surface a multi-fleet audience actually reads. `seat:LNNN` is canonical because the qualifier is
decidable without a registry lookup; **"the supervisor seat" is not decidable at all** without knowing
which fleet is being discussed.

**For consumers**: wherever these artifacts name a seat, the name is now the FLEET_STATE-registered one.
If you find an unqualified role-noun (*"the supervisor"*, *"the framework seat"*) in any v3.28 artifact,
it is a defect — report it rather than inferring which seat is meant.

**Credit**: found by a consuming seat in another fleet, on first contact with these artifacts, without
asking the producer anything. That is the outcome the self-sufficiency bar was set for, and this defect
is the cost it surfaced.

---

## Row 12 — CORRECTING ROW 11: the fix it announced landed at three of five sites, not five

**Found**: 2026-07-27, auditing row 11's own completeness claim before relying on it.

Row 11 states: *"**Fixed**: all five now read `private-supervisor-AGET`."* **Two of the five were still
unqualified when that sentence was written** — and they are two of the three rows row 11 names by
number:

| Site | State at row 11's publication |
|---|---|
| Row 3b (`…never fires there for **the supervisor's** own tags`) | **unfixed** |
| Row 7 (`Found: by the **supervisor seat's** independent migration-prep audit`) | **unfixed** — the primary credit line, and the one the remote seat actually quoted |
| Row 8, row 3b's leg-3 sentence, manifest `verify_rule` | fixed, correctly |

Both are now fixed. Row 3b's second instance is resolved by anaphora (*"that seat's own tags"*) rather
than a fourth repetition of the name.

**Row 11 was never published, and that is a second finding.** It was committed locally and the commit was
never pushed. `origin/main` carried **10 rows** while the working copy carried 11 — so the remote seat
whose quote row 11 credits was reading the *original, unqualified* artifacts, not row 11's account of
them. Row 11's own text (*"**Fixed**: all five now read…"*, *"**For consumers**: …"*) is written in the
voice of a published correction and was never one. A correction that does not reach `origin/main` has the
same consumer value as no correction at all — the L656 Loading-Dock shape, at the corrections surface
that exists specifically to defeat it.

**Why this is a row and not a silent edit of row 11.** Since row 11 never reached a reader, editing its
claim in place would have been defensible. It is kept as a separate row because both rows now go public
in the same push, and the reader is better served seeing what was claimed alongside what was true than
seeing a tidied row 11 that never records the miss. Same disposition as row 10 correcting row 8 —
different reason: row 8 *was* published; row 11 was not.

**The instrument lesson, which is the transferable part.** The first audit run here searched
`the supervisor seat` and returned row 7's line as **absent** — because the file writes it as
`the **supervisor seat's**`, and the `**` breaks the phrase adjacency the pattern required. A clean
negative from a pattern that cannot match its own subject reads exactly like a clean bill of health. The
audit that produced row 11's "all five" is likely to have been the same shape. **Strip markdown emphasis
before matching prose identifiers** — `re.sub(r'[*\`_]', '', line)` — or the emphasis you added for
readability silently exempts the term from every audit that follows.

**For consumers**: row 11's *substance* stands — unqualified role-nouns are defects and the canonical
form is the FLEET_STATE-registered name. Only its completeness claim was wrong, and it never reached you
in any case. The standing instruction to report any unqualified role-noun you find is now more
load-bearing, not less: **two** audits of this surface have now returned a false all-clear on it.

---

## Row 13 — probe 6 checked two of the three version-bearing surfaces and was named for all of them

**Found**: 2026-07-27 by `private-legalon-supervisor-AGET` — **from a permission-prompt diff**, mid-wave,
not from running any check. The dialog rendered three lines of context around the edit, and line 4 was
visibly wrong.

`REMOTE_MIGRATION_MESSAGE_v3.28.0.md` probe 6 read:

> `jq -r .aget_version .aget/version.json` and `grep '@aget-version' AGENTS.md` → both `3.28.0`

and was titled **"Version coherence."** `AGENTS.md` carries **two** version-bearing lines:

```
@aget-version: 3.28.0
@aget-canonical-specs: https://github.com/aget-framework/aget/tree/v3.27.0/specs — reliance-only conformance
```

The second pins a `/tree/vX.Y.Z/` ref and sits **two lines below** the one the probe greps. A seat that
bumps `@aget-version` and not the specs pin passes probe 6 cleanly while pointing its conformance
reference at the previous release.

**Measured in the producing fleet, after the finding**: 30 of 31 seats carry the field; **4 are drifted**
— `3.28.0` beside `/tree/v3.27.0/`. Every one of them had passed probe 6.

**Why it survived every self-check.** The producing seat's own `AGENTS.md` is **the one file in the fleet
that does not carry `@aget-canonical-specs`**. No amount of dogfooding at the producer could surface it;
the probe was correct-by-construction on the only instance its author could see. This is the
non-representative-pilot failure the release SOP already names at Phase 7.8 (*"FWK+SUP pilots were 2 of
only 3 clean agents"*), recurring at the probe-authoring layer.

**Fixed**: probe 6 now checks all three surfaces and carries a re-run notice for seats that migrated
before this row. The 4 drifted seats are **routed to their owners, not fixed here** — a cross-fleet write
is prohibited and the fix is one line at each seat.

**For consumers**: if you migrated before 2026-07-27, re-run probe 6 in its new form. A pass under the old
form is not evidence for the new one.

**The transferable part**: a check named for a *property* ("version coherence") and implemented against
an *enumeration of surfaces* silently narrows to whatever surfaces existed when it was written. When you
name a probe after the property, state the surface list and say why it is complete.

---

## Row 14 — every probe in this release read the working tree, and leg 2's evidence bar did too

**Found**: 2026-07-27, from a supervisor seat's Gate-3 fan-out. Row 13 fixed probe 6 by adding a *third
surface*. This row is the question row 13 did not ask: **are all its surfaces the same KIND of surface?**
They were. Probes 1–7 are seven filesystem reads.

**Three failures pass that battery**, all observed in the field within 24 hours of the tag:

| Failure | What passes | What is false |
|---|---|---|
| **version without payload** | probe 6 — both files say `3.28.0` | the four scripts never landed |
| **payload without persistence** | probes 6, 7 and the smoke — the working tree is correct | nothing committed; one `git checkout` reverts it |
| **`exit=0` without work** | a dispatcher's exit code | the seat could not execute `python3` and migrated nothing |

They share one cause, stated by the seat that found the third: *the signal was always whatever was
cheapest to read — an exit code, a version string, a hash of a file on disk — never the thing actually
claimed, which is that the seat carries the capability, durably.*

**Measured in the producing fleet at one instant** (`scripts/verify_migration_landed.py`):

| Instrument | Reading |
|---|---:|
| `.aget/version.json` on disk == `3.28.0` | **17**/31 |
| …and payload sha matches the manifest | **15**/31 |
| …and `version.json` == `3.28.0` **at `HEAD`** | **13**/31 |

Four seats claimed the version and did not hold it, in **two non-overlapping** modes — two carrying an
uncommitted payload, two carrying a version with no payload. Every fleet count published that day was
the 17.

### The part with teeth: leg 2's bar admitted work that can evaporate

§Report back read *"**Confirm your version** — this closes `GOAL-V328-DELIVERED` leg 2."* No ref. A seat
that applies the payload and **cannot commit it** — headless dispatch can edit files but cannot `git
commit` without an allow rule — satisfies that sentence **truthfully**, reading `3.28.0` off its own disk.
Two seats were in exactly that state and both would have closed leg 2 on the old wording.

`POLICY_release_cadence` **R-REL-CAD-012** gates the v3.29 scope-lock on `GOAL-V328-DELIVERED`. The old
bar would have released the next cycle's gate on work one `git checkout` from gone.

**Fixed**: §Report back now requires the version **at `HEAD`** plus the payload sha, with both commands
inline. **A leg-2 confirmation recorded before 2026-07-27 does not meet the corrected bar** — it was
taken against the disk. Re-confirm; it is one command.

**Also fixed**: probes **8** (payload sha vs the manifest) and **9** (version at `HEAD`) added. The
migration bar for v3.28.0 is now **6+7+8+9**.

### One trap worth copying, and one instrument

`git show HEAD:<path>` is **repo-root-relative**. A seat that is a subdirectory of a monorepo needs
`$(git rev-parse --show-prefix)` or it reads un-persisted. That is a false alarm rather than a false pass
— but a check that cries wolf during normal operation gets ignored exactly when it is right. The same
class bit two independent instruments at the consuming seat within one hour.

`scripts/verify_migration_landed.py` implements all three axes per seat
(`LANDED` / `NOT-COMMITTED` / `VERSION-ONLY` / `NOT-APPLIED` / `UNVERIFIABLE`), handles the prefix,
reports an unchecked payload axis as `UNCHECKED` rather than as pass, and exits 0 only on `LANDED`.
Self-test 8/8; control-tested 5/5 against seats whose true state was established independently, including
a monorepo seat. **Use it instead of a version grep — and when you publish a count, name which of the
three readings you mean.**

---

## Row 15 — probes 8 and 9 read the wrong REF, and the instrument written to fix that had the same defect three times

**Found**: 2026-07-29 by `private-supervisor-AGET` and `private-aget-framework-AGET` measuring the same
fleet independently. **Both reported `22/31 LANDED`. The sets were different.** That is the finding; the
ref bug is only its cause.

Row 14 moved the migration bar from *disk* to *`HEAD`* and stopped one ref short. **A fourth failure
passes the 6+7+8+9 battery as published:**

| Failure | What passes | What is false |
|---|---|---|
| **committed but OFF-TRUNK** | probes 8 and 9 — `HEAD` carries version *and* payload | the seat's **trunk** is two releases back; the migration lives on an unmerged branch |

`private-career-aget` sat on `session/2026-07-17-…` with `HEAD` = `3.28.0` and `main` = **`3.26.0`**. It
passed every `HEAD`-based probe. `R-FU-014-6` at the consuming seat had **already** superseded `HEAD` with
trunk; canonical had not converged, so the consuming seat's bar was knowingly stronger than the published
one for two days. **Canonical now converges to it** (`gh#2059`) — the consuming seat was right and this is
the producer following, not the reverse.

### The three defects in `scripts/verify_migration_landed.py`, the file written to kill this class

1. **Version axis read `HEAD`, not trunk** — it certified `career` LANDED.
2. **Payload axis hashed the WORKING TREE while the version axis read a commit.** Two axes, two refs, one
   verdict, so the verdict answered no single question. One local edit made
   `private-professional-core-aget` read DIVERGENT while its committed state was byte-exact. Worktree
   drift is real information and is now reported **separately**, never against the verdict.
3. **Payload axis silently scored ONE of THREE sha-bearing manifest sections** (`additive_files` only,
   with `delivered_files` and `optional_files` unread and unmentioned, while the manifest's own
   `verify_rule` names all three). At v3.28 the narrow read was **accidentally correct** — the
   `delivered_files` enforcement payload never shipped (row 3), so scoring it would have reported
   DIVERGENT at all 31 seats. The accident inverts the moment a release ships its `delivered_files`.
   This is row 12's lesson one layer down: prose named three sections, the actuator mechanised one.

**Defects 1 and 2 were sign-opposed and cancelled exactly.** That is why two seats agreed on `22` from
different sets: one over-counted `career` and under-counted `professional-core`; the other did neither.
**An aggregate cannot surface a sign-opposed pair. An element-wise diff of the SET can.** Publish the
per-seat set, not the count.

### Two more defects, found on the first live runs of the fix itself

- **`ABSENT-AT-REF` is a SENTINEL, not a hash.** The manifest writes it into `sha256` for every
  enforcement-payload row. Comparing it as a hash reported **all 31 seats DIVERGENT** for correctly not
  having files that were never shipped — a disclosed producer-side gap re-rendered as 31 phantom consumer
  defects. Sentinel rows are now `declared-absent`: not scoreable as delivery, and a seat that *does* hold
  one is flagged `PRESENT-ANOMALY` (provenance not this release) rather than passed or failed.
- **Precedence.** The payload axis is scored *at trunk*, so a stale trunk **entails** a stale payload.
  Scoring payload first made `career` read `VERSION-ONLY`, whose stated meaning is "version pinned,
  payload absent" and whose remedy is **re-migration**. `career`'s real remedy is a conflict-free
  fast-forward. Reporting a consequence in place of its cause hands the reader the wrong repair, which is
  worse than a vague answer. Trunk position is now answered first, and `OFF-TRUNK` is a distinct verdict.

**The repo-root prefix is KEPT.** Probe 9's `$(git rev-parse --show-prefix)` was always correct — that is
the monorepo fix (`R-FU-014-5`). Only the **ref** was wrong. Dropping the prefix while changing the ref
reintroduces the monorepo false alarm: a correction failing to reach what was derived from it.

**What to do**: re-run probes 8 and 9 in their trunk form, or run
`python3 scripts/verify_migration_landed.py . --version 3.28.0 --manifest handoffs/DELIVERED_FILES_v3.28.0.yaml`
(one command, both axes at one ref, exit 0 only on `LANDED`). **A leg-2 confirmation recorded against
`HEAD` does not meet the corrected bar.** Re-confirm; it is one command.

**Re-measured trunk-based, 2026-07-29T18:09Z**: **29 LANDED · 1 OFF-TRUNK (`career`) · 1 NOT-APPLIED
(`llm-connectivity`)**. Self-test 8 → 10 cases, including one deliberate precedence flip recorded rather
than silently re-asserted. A census is a snapshot — run the instrument rather than citing this line.

---

## Row 16 — canonical `study_topic.py` moved: two lint defects fixed, and one of them was a dead capability

**Found**: 2026-07-29, fixing `gh#2041`'s upstream half.

`gh#2041` established that the shipped `study_topic.py` fails a standard ruff gate, making probe-8
byte-identity and a seat's own pre-commit hook mutually unsatisfiable. **Both defects are now fixed on
canonical `HEAD`.**

**This moves no manifest sha and cannot un-land any seat.** `DELIVERED_FILES_v3.28.0.yaml` pins
`source_ref: "v3.28.0"` — the immutable tag. Verified: the tag's blob still hashes `2f3bd28ae29e…`;
canonical `HEAD` now hashes `7e570c4563a2…`, and the two are *meant* to differ. **Do not re-cut any hash,
and do not "fix" your local copy toward a value you computed** — the bytes probe 8 measures are still the
tag's. The dispatch precedence clause (`--no-verify` authorized for the migration commit only) therefore
still stands unchanged.

**The F841 was not lint.** `purpose_globs` was computed in `main()` and discarded, and chasing it found
**CAP-SESSION-007-06 (purpose weighting via `priority_areas`) is entirely dead code**:

| Component | State |
|---|---|
| `get_purpose_globs()` | implemented, works |
| `compute_purpose_boost()` | implemented, works — reachable **only** from `search_directory()` |
| `search_directory()` | **zero callers** |
| `find_ldocs` … `find_inbox` (9 functions) | all take `domain_keywords`; **none takes `purpose_globs`** |
| `--purpose` flag | accepted, and documented as *"weights results by KB area"* |

So `--purpose` has never weighted a single result. **The assignment is deliberately retained with an
explicit `# noqa: F841` and a comment**, because deleting it to satisfy the linter would have erased the
last trace of a built-and-unreachable capability — the tidy fix that destroys the finding.

**Not fixed here, on purpose**: wiring it changes result ranking for every study at every seat, which
needs a V-test and a release, not a lint pass. **It survived v3.28's own orphaned-control census** (15
controls wired that cycle), and that is the more useful finding: the census reads controls, and this is a
capability whose orphaning lives at a *parameter* call site.

---

## Row 17 — this release told you a requirement gates the next cycle, and pointed at a file you do not have

**Found 2026-07-29 by the framework seat, auditing its own release artifacts. Not consumer-affecting;
correcting it anyway, because the defect is a citation this release asked you to trust.**

**R-REL-CAD-012** is cited as the gate on the v3.29 scope-lock in **four** artifacts you received —
`DEPLOYMENT_SPEC_v3.28.0.yaml`, `RELEASE_HANDOFF_v3.28.0.md`, `REMOTE_MIGRATION_MESSAGE_v3.28.0.md`, and
this file. All twelve `R-REL-CAD-*` requirements are defined **only** in
`governance/POLICY_release_cadence.md`, which exists in the framework agent's **private** repo and has no
public counterpart. Measured with `scripts/audit_release_citation_resolution.py`, counted from its `--json`
path rather than its printed table: **4 public citations, 0 public definitions.**

**Why this is a defect and not a nitpick.** The framework's own `v328-prelock:R15` requires that an
artifact asserting a prerequisite carry the **verbatim text** *and* a **cite the reader can follow**. The
handoff's quote is faithful — verified against the normative section, not against the version-history line
(`v328-shipday:R63` forbids grounding an assertion in metadata) — but you had no way to establish that.
**A faithful quote plus an unopenable cite is an unfalsifiable claim**, and the rule exists specifically to
make fabrication mechanically visible. Satisfying half of it produces the appearance of the guarantee
without the guarantee.

**Two corrections that run in your favour**, both quoted verbatim from that section:

- *"Accepted consequence, stated at ruling time: leg 3 is satisfiable only at a seat the releasing agent
  does not control, so the next cycle's schedule is downstream of fleet deployment. That is the intended
  shape of a Loading-Dock guard (L656) rather than a flaw in it."*
- *"Override: principal MAY lift with recorded reason (L178); the default is HOLD."*

So the gate is **deliberate and overridable**. Characterisations of it as *"circular as written"* — including
in the framework seat's own analysis earlier the same day, and in a peer seat's — were wrong twice over:
the consequence was ruled, not stumbled into, and a documented lift exists. The residual defect is
narrower: leg 3's only *specified* route (the supervisor installs the firing guard) is the one **Row 3b of
this file forbids**, so the route is blocked while the gate is fine.

**And it was addressed to the wrong audience.** R-REL-CAD-012 constrains *the framework agent*. Nothing in
it asks a migrating seat for anything. Citing it to consumers reads as an obligation you cannot discharge —
which is the same shape as `gh#2076` one level down, where a shipped skill cites `AGENTS.md` sections
present at 1 of 31 seats and every consumer pre-flight reports PASS regardless.

**Fixed in this release's artifacts** (audience-scoped, full quote, override disclosed). **Owed, not
claimed** (L671): no instrument gates a public artifact citing a private-only requirement id at publication
time — the audit exists and is not wired into the release gate.
