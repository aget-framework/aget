# RELEASE HANDOFF — v3.28.0 "Make the gates fire"

**Prepared**: 2026-07-26 · **Class**: **governance-hardening (inward-facing)**
**Implements**: R-REL-019 (release-to-fleet handoff)

> ⚠ **PUBLIC AND TAGGED — payload incomplete. Read `CORRECTIONS_v3.28.0.md` row 3 before migrating.**
> v3.28.0 is live (`v3.28.0` = `572d10d8`, 14/14 repositories in sync, verified 2026-07-26). The prior
> banner here read *"Do not begin migrating until the tag is live"*; it was written pre-push and went stale
> at the tag, so for several hours this package instructed consumers not to proceed after the act it was
> waiting for had happened.
>
> The tag being live is **not** by itself clearance to migrate: the firing guard and its battery are absent
> from every public repository, so the upgrade guide's step 2 has no source. Row 3 of CORRECTIONS carries
> the detail.

---

## The one thing to read first

**The migration instructions are not in this file. They are in `release-notes/v3.28.0.md`** — deliberately.

The handover travels through the release notes because that replicates how a **remote** supervisor
experiences it: reading public artifacts, unable to ask the producing agent anything. A package that works
only because its author is reachable does not test what it claims to test.

**The bar**: those notes must be sufficient to migrate a supervisor seat **and drive its fleet wave
unaided**. If you need to ask the producing agent something, that is a **defect in the notes** — please
report it as one rather than working around it. That report is worth more than a smooth migration.

---

## What changed, in one paragraph

Controls that existed before v3.28 ran only when an agent chose to run them. Now a `PreToolUse` hook fires
the release battery and the release-quality gate at the moment of `git tag` / `push --tags`; a
release-quality score must carry a resolvable **independent** verification leg; gate refusals are **recorded
to a ledger**; triage freshness is a measured SLO; and the test-traceability floor ratchets instead of
sitting at an unmet aspiration.

**Expect refusals you did not get before.** That is the release working.

---

## Pilot tracking

| Seat | Version before | Deployed | Confirmed by | Notes |
|---|---|:--:|---|---|
| framework (producer) | 3.27.0 | ✅ **3.28.0** | self-migration, 2026-07-26 | R-REL-006 manager migration |
| supervisor seat | 3.27.0 | ⬜ pending | — | **delivery-Goal leg 2** |
| fleet wave | 3.27.0 | ⬜ pending | — | supervisor-driven |

---

## ⚠ Why this handoff is on the critical path, not a courtesy

`POLICY_release_cadence` v1.6.0 added **R-REL-CAD-012**:

> *"A cycle's **scope-lock ceremony SHALL NOT begin** while the prior cycle's delivery Goal has open legs …
> where 'delivered' is defined by the prior cycle's own committed Goal, **not by its tag**."*

> **⚠ Read this requirement as producer-internal, and know that you cannot open its home (added 2026-07-29).**
> `POLICY_release_cadence.md` lives in the framework agent's **private** repo. It has no public counterpart,
> so the citation above is **unresolvable for you** — the quote is faithful to the normative section, and you
> have no way to check that. Corrected here rather than left standing, because the framework's own
> `v328-prelock:R15` requires a prerequisite assertion to carry verbatim text *and a cite the reader can
> follow*, and this one satisfied only the first half. Measured: **4** public v3.28 artifacts cite this id;
> **0** public files define it (`scripts/audit_release_citation_resolution.py`).
>
> **It does not bind you.** R-REL-CAD-012 constrains *when the framework agent may open the next
> scope-lock*. Nothing in it asks a migrating seat to do anything. It appears in a handoff because it
> explains why v3.29 may be **late**, not because you owe it compliance — and a requirement addressed to
> the wrong audience reads as an obligation you cannot discharge.
>
> **Two things the policy states that were missing here.** First, the consequence was accepted at ruling
> time, not discovered: *"leg 3 is satisfiable only at a seat the releasing agent does not control, so the
> next cycle's schedule is downstream of fleet deployment. That is the intended shape of a Loading-Dock
> guard (L656) rather than a flaw in it."* Second, it is **not a deadlock** — *"Override: principal MAY lift
> with recorded reason (L178); the default is HOLD."* Both sentences are verbatim from
> `governance/POLICY_release_cadence.md` §R-REL-CAD-012 (private). Earlier framing of this gate as
> *"circular as written"* — including in my own analysis — was wrong on both counts.

The v3.28 delivery Goal has three legs:

| Leg | Condition | Who can close it |
|:-:|---|---|
| 1 | public chain complete | the producing seat — pending tag |
| 2 | **≥1 downstream seat confirmed running it** | **a consuming seat** |
| 3 | **≥1 control observed blocking something WITHOUT being invoked, at a DOWNSTREAM seat** | **any seat but the producer** |

**So the next release cycle cannot begin its scope-lock until a downstream seat has migrated and one of
these gates has refused something there.** The policy states and accepts the consequence: leg 3 is
satisfiable only at a seat the releasing agent does not control, so the next cycle's schedule is downstream
of fleet deployment.

### What that asks of a consuming seat

**Nothing extra.** Leg 3 is instrumented: any gate refusal appends to `.aget/logs/control_firings.jsonl`
with `hook_event: PreToolUse` marking a genuinely unbidden firing. Just **do not delete that file**, and
surface it when asked.

⚠ **Please do not manufacture a firing to unblock the next cycle.** A deliberately triggered gate is
*invoked*, and the governing ruling was made strict precisely to exclude that. The producing seat declined
to claim leg 3 twice on exactly that basis. A slow honest leg 3 beats a fast false one.

---

## Context for External Fleets

- Pin template-derived agents to the template tag (`v3.28.0`); post-tag fixes live in `handoffs/CORRECTIONS_v3.28.0.md`, created at first fix.
- **This release can refuse your acts.** A `PreToolUse` hook gates `git tag` / `push --tags` on the release battery and the release-quality gate. A refusal is the payload working. Read the message; it names each failing condition.
- **Two probes must BOTH pass**, not just the blocking one: the guard must refuse a release act *and* pass ordinary work. A guard that fires on everything gets disabled, and a disabled guard protects nothing.
- **M-3.28-2/-3/-4 are seat-conditional** — they bind only if your seat carries the release tooling. A worker seat that never tags a framework release skips them legitimately.
- **Do not delete `.aget/logs/control_firings.jsonl`.** Gate refusals record there, marking whether a control fired unbidden or was run by hand. It is the only evidence path for this cycle's delivery-Goal leg 3.
- **Please do not manufacture a refusal** to help close that leg. A deliberately triggered gate is *invoked*, which the governing ruling excludes. The producing seat declined to claim it twice on that basis.
- Verify features at the OPERATIVE path your agent config invokes (dual-basename caution, carried from v3.25/v3.27).

## Known limitations — stated, not discovered

### ⚠ This release's own quality score was OVERRIDDEN — disclosed here deliberately

v3.28 introduces an independence gate for release-quality scores. **Its own score did not pass that gate.**

`rubrics/RUBRIC_release_quality_v3.28.0_score.md` is **producer-run** and carries **no independence
declaration**. `check_score_independence` exits 1 against it. The tag proceeded under a recorded override.

**Why**, stated so you can judge it rather than take it on trust: the requirement is **unsatisfiable by
construction**. No seat meets all three conditions at once — not the producer, no stake in the outcome, and
reachable without crossing the supervisor's fleet-coordination lane. The supervisor is reachable but is
this release's deployment target (a consumer certifying its own supplier). Peer seats have no stake, but
the producing agent has no standing to task them. The requirement shipped blocking, with no legal route to
satisfy it.

**What this means for you**: when you run the check at your seat, it will report v3.28's score as lacking
an independent leg. **That is accurate, not a defect in your migration.** The override is recorded at
`.aget/overrides/release_gate_v3.28.0.md` with its reason, and in the firing ledger as `action=OVERRIDDEN`.

**Not claimed**: that the score was independently verified. It was not. Defining a legal independence route
is v3.29 scope.


- **The independence check tests non-identity with the producer, and nothing about the verifier's stake.**
  A seat with an interest in the outcome passes it. The supervisor seat is therefore **excluded** as
  verifier for this release, being its deployment target — a consumer certifying its own supplier.
  Structural fix owed to the next cycle.
- **15 controls were orphaned** (nothing invoked them) and are now wired; the census that found them is
  advisory, not blocking. It will report debt at your seat too.
- **29 path references in governed artifacts resolve to nothing.** A checker now reports them; they are not
  fixed.
- **`AGENTS.md` exceeds the 40k configuration limit** at the producing seat. Tracked as quality debt; it
  does not block.
- **Three phase-ordering faults** in the release process were resolved by ruling, not structure. A
  dependency model is owed.

---

## If something goes wrong

1. **A gate blocks you**: read the message; it names the condition. Fix it, or record a principal-authorized
   override with a written reason. Do not skip silently.
2. **Rollback**: no data formats or artifact schemas changed. Restore your prior version strings and
   unregister the hook. The firing ledger is append-only and harmless.
3. **The notes are insufficient**: report it. That is a defect in this release, not a gap in you.

---

## Provenance

Scope: `VERSION_SCOPE_v3.28.0.md` (SCOPE_LOCKED, 5 rows / 26 story units, all landed). The value gate passes
on LANDED scope **with a recorded override** on capability-share — *never* describe it as "green"; the
cycle's independent critic raised a finding on exactly that paraphrase.

Cycle findings — including the root-cause analysis that this release's own theme reproduced once — are in
the release notes' §Cycle findings.
