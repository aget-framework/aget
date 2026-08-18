---
name: aget-close-project
description: Close a PROJECT_PLAN with verifiable-assertion gate (V-tests + commits + retrospective), deferred-surface scan for next-plan handoff, and status transition (ACTIVE → COMPLETE / CLOSED / ABANDONED / SUPERSEDED). Strict counterpart to /aget-create-project (D71 Layer 2). Closes asymmetric verb-pair gap at PROJECT_PLAN lifecycle.
---

# /aget-close-project

Terminally close a PROJECT_PLAN with verifiable assertion, closure checklist, and deferred-surface handoff. Strict counterpart to `/aget-create-project`.

## Input

$ARGUMENTS — PROJECT_PLAN filename (or slug; resolved against `planning/`) plus required
`--disposition <Complete|Closed|CLOSED-PARTIAL|Abandoned|Superseded>`

## Mode Detection

| Input Pattern | Mode | Behavior |
|---------------|------|----------|
| Empty | **Interactive** | List candidate plans (status=IN PROGRESS or all gates [x]), prompt for selection |
| `<filename> --disposition Complete` | **Explicit** | Resolve the plan and attempt a complete close |
| `<filename> --disposition <Closed\|CLOSED-PARTIAL\|Abandoned\|Superseded> --reason <text>` | **Explicit with reason** | Required for every reasoned disposition; the reason explains but never selects the disposition |
| `<filename> --override <text>` | **L178 override** | Bypasses the **ENTRY** gate (Step 2) with recorded reason. **Scoped deliberately**: it does NOT bypass either arm of the Step 4.5 EXIT gate (4.5a completeness, 4.5b accounting). Before the gh#2250 reorder this flag was the routine way to close an honest plan — every closer-authored checklist row tripped Step 2 — which converted an exception route into the only route. It is exceptional again; a close needing it for *closure-row* reasons is now a defect report |

## Project Closure Process

### Step 0: Scope-Fit + Identity Check

1. Read `.aget/identity.json` — extract `name`, `domain`
2. Resolve PROJECT_PLAN path; verify file exists under `planning/`
3. If file absent: ERROR with candidate-list suggestion

### Step 1: Input Analysis

Parse $ARGUMENTS:
- Plan filename or slug
- Required `--disposition <Complete|Closed|CLOSED-PARTIAL|Abandoned|Superseded>`; no default
- Optional `--reason <text>` (required for Closed/Closed (Partial)/Abandoned/Superseded); reason text
  explains the explicit selection and SHALL NOT infer or select it
- Optional `--override <text>` (L178 path — bypasses the Step 2 ENTRY gate with recorded reason; does NOT bypass Step 4.5a or 4.5b)

### Step 2: ENTRY Gate — Substantive Work Only (Strict — C-CLOSE-001)

> **Reordered 2026-08-16, gh#2250 Remedy A.** This step used to run the FULL conformance guard and refuse
> on *any* exit 2 — including unchecked Closure/Finalization rows. Those rows are **authored by Steps 3.5
> and 4, downstream of here**, so an honest plan arriving with a creator-scaffolded, still-unticked
> closure checklist was unclosable without `--override`. Measured 2026-08-15: the blocking pair is present
> at **31 of 32 registered seats** and **13 of 13 managed templates**, so every newly instantiated agent
> inherited it, and `--override` stopped being an exception and became the only route.
>
> **Named externally: this was an ETVX violation** (IBM, 1980s — Entry / Task / Verification / eXit).
> Exit criteria were being enforced at the Entry position, with no Verification step after the Task. The
> repair is not a weaker gate; it places each predicate at its lifecycle phase and adds a receiver-visible
> exit decision (Step 4.5). Unfinished work never escapes silently: `Complete` blocks it, while a reasoned
> disposition must account for every eligible occurrence on the closer's output.

**Automate the scan, don't eyeball it** (C-P1 guard, v3.20; L736 assert-before-verify):
```bash
python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md \
  --phase entry --disposition <explicit-target>
```

#### The entry predicate — ONE rule, executable

```bash
python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md --json \
  --phase entry --disposition <explicit-target>
```

> **ENTRY BLOCKS** exactly as the guard reports. The guard derives each finding's lifecycle class from
> CAP-PP-013-14: closer-authored findings are not evaluated at entry; pre-close integrity findings and
> `status_row_nonterminal` always block; `Complete` blocks substantive work; reasoned dispositions carry
> eligible substantive occurrences to exit accounting.

That sentence is the whole entry criterion. There is no second rule to reconcile it against.

**Match on `key`, never on `label`** (1R.3). The `label` is presentation — it carries issue numbers and
prose and is edited freely. The `key` is the stable identifier. This is not hypothetical: an earlier
version of this step matched labels, tolerated `Closure-section placeholder prose`, and the guard rendered
`Closure-section placeholder prose (substance, #1568)`. The declared tolerance silently never took effect,
and a test passed on the mismatch.

| `key` | Entry | Exit | Why |
|---|---|---|---|
| `unchecked_closure_item` | not evaluated (closer-authored) | BLOCK | Steps 3.5–4 tick it |
| `placeholder_substance` | not evaluated (closer-authored) | BLOCK | CAP-PP-013-03 supplies the lifecycle class; no rendered-string allow-list |
| `gate_status_pending` · `vtest_pending` · `status_row_nonterminal` · `gate_heading_nonterminal` · `dual_status_mask` · `supersession_not_explicit` · `release_close_guard_block` · `release_close_guard_error` | BLOCK | BLOCK | substantive work, or a defect in the record of it |

The table is explanatory. The executable classification is spec-derived. **If a new `key`, disposition,
or lifecycle row appears without complete schema coverage, the guard errors fail-closed.**

> **Gate 3 lifecycle correction.** Gate 2 now supplies the phase/ownership semantics that 1R.2 lacked:
> CAP-PP-013-03 is `closer-authored`. The entry gate therefore omits `placeholder_substance`; the exit
> gate still blocks it. Classification uses `source_requirement` → CAP-PP-013-14, not a label or literal
> fixture string.

> **1R.4 — the prose REFUSE list is removed, not amended.** It read *"Any gate marked `[ ]` (unmarked) in
> plan body — REFUSE"* alongside the statement that closer-authored unchecked rows are expected. Both
> sentences described `[ ]` tokens; a model could follow either and remain textually compliant, and the
> two gave opposite verdicts on the same document. Four bullets, three of them restating in prose what the
> guard already computes, are replaced by the single predicate above.
>
> The dropped bullets are not lost — each is a guard finding key: an unmarked gate is
> `gate_status_pending` / `gate_heading_nonterminal` / `status_row_nonterminal`, a missing V-test result is
> `vtest_pending`, an unparseable status field is `dual_status_mask` or resolves via CAP-PP-013-11. All
> block under the predicate. **Nothing was narrowed; the second, conflicting statement of the rule was
> deleted.**

**REFUSE close** when the entry predicate above evaluates to BLOCK — UNLESS the override path applies.

**Output on refusal**:
```
REFUSE: /aget-close-project entry gate failed (substantive work incomplete)
  Plan: planning/PROJECT_PLAN_<name>.md
  Unmarked gates: <list>
  Missing V-tests: <list>
  Note: unchecked closure/finalization rows are NOT a Step-2 refusal — they are authored at Step 4
        and enforced at Step 4.5.
  Override path: re-invoke with --override "<reason per L178>"
```

**Override path (L178)**: principal supplies reason; recorded in retrospective + commit.
**This path is exceptional again.** Before Remedy A it was the routine way to close an honest plan; if a
close still needs `--override` for closure-row reasons after this reorder, that is a defect report, not a
workflow.

### Step 2.5: Authorization Gate (Strict — C-CLOSE-002; L1102 / Q3:A hardening)

**A principal-attributed close MUST link its authorizing event; an irreversible consequence MUST be legible.** This closes the L1102 root cause — the v3.23 close recorded `Reason (principal-ruled): ... private milestone / fold to v3.24` with no linked authorization event and no legibility on the irreversible consequence (burning the `v3.23.0` public number).

```bash
python3 scripts/close_authorization_guard.py planning/PROJECT_PLAN_<name>.md
```
Exit 1 = BLOCK. Two checks fire only when relevant (an agent-autonomous close with no irreversible consequence passes — guard N/A):
- **CHECK-A**: the close reason attributes the decision to the principal (`principal-ruled`, `approved by the principal`, …) but carries **no authorization-event pointer** (a `/aget-go` record, an `Authorization log` entry, an AskUserQuestion/`Q#:X` selection, a dated principal quote). Free-text "(principal-ruled)" is **not** provenance.
- **CHECK-B**: the close carries an **irreversible / identity-level consequence** (private milestone, skip/burn a public version, fold to a later version, abandon a public release) that is **not made legible** — the consequence must be surfaced explicitly, never buried under a mechanism label, and never agent-*recommended* against a standing requirement (e.g. "release publicly each weekend").

**REFUSE close** if the guard exits 1 — UNLESS `--override` with a recorded L178 reason. On a principal-attributed close, the fix is to add the event pointer (link the GO/selection), not to override.

### Step 3: Research Phase

Before writing closure artifacts, gather context:

#### 3.1 Read full PROJECT_PLAN body
- All gate sections
- All V-test result blocks
- Existing retrospective section (if any)
- All deferred-surface markers ("deferred to next session", "Loading Dock", "spawn", "future")

#### 3.2 Read sibling closed plans for closure-pattern grounding
```bash
grep -l "^\*\*Status\*\*:\s*COMPLETE" planning/PROJECT_PLAN_*.md | head -3
```
Read the most recent 1-2 closed plans to ground retrospective style.

#### 3.3 Read commit log for this plan
```bash
git log --oneline -- planning/PROJECT_PLAN_<name>.md
```
Build V-test → commit-SHA mapping (per L001: gate completion = plan update + commit).

### Step 3.5: Closer-Mutates-Scaffold Rule (C-CLOSE-007 — v3.26 C-26-07, gh#1838)

**The closer writes to the SAME ANCHORS the creator scaffolded — it MUTATES the existing checklist/section in place; it NEVER appends a parallel prose sign-off.** The scaffolded checkboxes are the structured, greppable representation that bypass-detection and `close_gate_check.py` read; a prose paragraph beside an unticked checklist creates dual representation where the structured copy is born stale (field exhibit 2026-07-05: a COMPLETE plan whose scaffolded closure checklist retained 11 unticked boxes and a `{date}` placeholder 12 lines below the prose sign-off).

Operationally, for every closure element in Steps 4–6:
1. **Find the scaffolded section first** (Retrospective / Velocity / Closure Checklist / Finalization Checklist headings + `{TBD}`/`{date}` placeholders from the creation template).
2. **Tick and fill IN PLACE** — `[ ]` → `[x]` with evidence appended to the same line; placeholders replaced, never orphaned.
3. Add NEW sections ONLY where the scaffold has no anchor (e.g. §Deferred Surface — genuinely net-new at close).
4. **Self-check before Step 7**: `grep -c '\[ \]\|{TBD}\|{date}' <plan>` over the closure/finalization sections MUST be 0 (or each survivor individually justified in the close reason — e.g. an intentionally-open tracker row on a PARTIAL close).

### Step 4: Closure Checklist Authoring (C-CLOSE-002)

Generate or update these sections in the plan body (per AGET_PROJECT_PLAN_SPEC template, CAP-PP-013/016/018):

1. **Retrospective** (required, non-empty):
   - **Worked**: What landed as intended
   - **Didn't Work**: Friction, rework, gaps
   - **Spawned**: Items routed to other plans / initiatives / L-docs
2. **Velocity Analysis**: gates planned vs gates landed; time-on-plan vs estimate
3. **Closure Checklist** (per template — 10 items spec-defined)
4. **Finalization Checklist** — pre-close gates: index updated, supervisor notified, handoff filed if applicable

### Step 4.5: EXIT Gate — Full Conformance (Strict — C-CLOSE-001, gh#2250 Remedy A)

> **The verification step ETVX requires and this skill never had.** Step 2 confirms the plan may *enter*
> closure; this confirms closure is *finished*. It runs the identical instrument on the closer's
> **output**. Under `Complete`, every finding blocks. Under a reasoned disposition, closure-record and
> integrity findings block while eligible substantive findings must reconcile one-to-one with the
> sanctioned accounting table.

```bash
python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md --json \
  --phase exit --disposition <the-same-explicit-target>
```

> **1R.1 — the exit gate is DISPOSITION-AWARE. A first version was not, and it deadlocked three of the
> four terminal dispositions.** It read *"exit 2 = BLOCK, no kind exempt … do not proceed to Step 5. No new
> override."* Step 5 is where `CLOSED` / `ABANDONED` / `SUPERSEDED` are selected — and for those, incomplete
> work is **intrinsic to the disposition, not a defect in the close.** An abandoned plan has unfinished
> gates by definition. The gate therefore made every non-`COMPLETE` terminal state unreachable, and because
> `--override` had been scoped to entry only, nothing could rescue it. Demonstrated on a fixture: guard
> exit 2, Step 5 never reached.

The exit criterion depends on **which terminal state Step 5 will assert**. Use the explicit
`--disposition`; `--reason` never selects or infers it.

#### 4.5a — Disposition `COMPLETE`

```bash
python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md \
  --phase exit --disposition Complete
```

**Exit 2 = BLOCK, no kind exempt.** `COMPLETE` asserts the work is finished, so any surviving finding
falsifies the assertion. This is the gate that catches:
- a Closure or Finalization row Step 4 left unticked;
- a `{TBD}` / `{date}` placeholder Step 3.5's self-check missed;
- a substantive regression introduced *by the closure edit itself* — a case the old ordering could not see
  at all, because it never re-ran after authoring.

**REFUSE the status transition** if the guard exits 2. Do not proceed to Step 5. **No override**: a
failure here means the closure content is genuinely incomplete, and the remedy is to finish Step 4. If the
work is *not* finished, the correct move is a different disposition — not a bypass.

#### 4.5b — Reasoned dispositions `Closed` / `Closed (Partial)` / `Abandoned` / `Superseded`

These are **reachable with findings outstanding** — that is what they mean. They are NOT reachable with
findings *unaccounted for*. The gate becomes an accounting check rather than a completeness check:

1. Run the same guard and capture the surviving findings.
2. Prepare a JSON list with exactly one row per eligible finding occurrence. Use `deferred` (`vehicle`,
   `reason`), `obsolete` (`reason`), or `accepted-incomplete` (`authority`, `receipt`, `reason`) note keys.
3. Submit the proposal through the transactional writer:

   ```bash
   python3 scripts/close_gate_check.py planning/PROJECT_PLAN_<name>.md --json \
     --phase exit --disposition <the-same-explicit-target> \
     --write-unfinished-json <rows.json>
   ```

   The guard renders and reconciles the candidate in memory. It atomically persists exactly one
   **`## Unfinished at Close`** table only when the resulting decision is clean; any malformed, orphan,
   unmatched, non-waivable, or otherwise blocking proposal preserves the target bytes unchanged.
4. Re-run the exit command without the writer option as a received-state check.

The table uses the exact CAP-PP-013-18 header. The received-state check reparses the persisted document
and reconciles occurrences one-to-one.
   Duplicate same-key findings require duplicate rows; closure-record and integrity findings are never
   waivable; orphan, malformed, or unmatched rows block/error.

**This is the anti-laundering condition.** Without it, "abandon it" becomes the universal way to close a
plan with silent unfinished work — which is a worse false-clean than the one this lane is repairing,
because it would be governed and routine rather than accidental. With it, the incompleteness is
enumerated, attributed, and greppable, and the disposition stays honest.

**No override on 4.5b either.** The remedy for an unenumerated finding is to enumerate it — a strictly
smaller task than fixing it, and the whole point of a reasoned disposition.

**Ordering invariant (gh#1838, preserved verbatim from Step 3.5)**: the closer MUTATES the creator's
scaffold in place and never appends a parallel prose sign-off. `## Unfinished at Close` is the one
sanctioned NEW section (Step 3.5 rule 3 — "add NEW sections ONLY where the scaffold has no anchor"),
because a scaffold authored at creation cannot anticipate what will be unfinished at close.

### Step 5: Status Transition (C-CLOSE-003 — Verifiable Assertion)

Update `**Plan_Status**:` header field to one of:

| Status | Meaning | Required Evidence |
|--------|---------|-------------------|
| **Complete** | All outcomes and exit criteria realized | Full closure/V-test/value/actual-effort evidence; no Unfinished table |
| **Closed** | Work terminated; remainder rerouted or retired | Reason + per-occurrence accounting; deferred rows name vehicles |
| **Closed (Partial)** | Named realized subset retained; remainder accounted | Realized-subset statement + ≥1 reconciled occurrence |
| **Abandoned** | Stopped without success/replacement claim | Reason + per-occurrence accounting; no successor assertion |
| **Superseded** | Unique named successor owns remaining intent | Valid non-self successor + per-occurrence accounting |

**Verifiable-Assertion requirement (per CAP-PRJ-001)**: Status transition is NOT text-edit alone. The transition is valid only when accompanied by:
- V-test summary block referencing commit SHAs
- Closure timestamp + closing agent identity
- Retrospective section non-empty

### Step 5.5: Pre-COMPLETE Has-It-Run Gate (C-CLOSE-008 — v3.26 C-26-13, gh#1855, coverage-matrix channel 2)

**A plan whose deliverable is an executable mechanism cannot go COMPLETE on authoring evidence alone — it needs execution evidence.**

Before a COMPLETE transition, scan the plan's deliverables for executable-mechanism classes (script, hook, gate, validator, check, pipeline). For each one found, require ONE of:

1. **Execution evidence**: a recorded run — test output, live firing, V-test invoking the mechanism itself (not just asserting its file exists), deployment confirmation.
2. **Honest re-route**: absent evidence, the status is NOT COMPLETE — route to **IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE** (per CONVENTION_terminal_state_vocabulary, C-26-14) or **CLOSED (PARTIAL)** with the un-run mechanism named in the reason.

Field basis (2026-07-10): a supervisor seat stamped COMPLETE on a never-run mechanism — reopened by principal Decide. Positive mirror: this gate's own reference impl re-derived DoD at a v3.24 close and caught 13 un-bumped public files pre-claim. "Artifact created" is L656's Loading Dock; execution evidence is what distinguishes IMPLEMENTED from RUNNING.

Distinct from Step 2 (gates ticked) and Step 5's V-test-SHA requirement: those verify the plan's own record; this step verifies the MECHANISM ran at least once. A V-test that merely greps for the mechanism's existence does not satisfy it (L736 assert-before-verify family).

### Step 5.7: Value-Resolution Verdict (C-CLOSE-009 — CAP-PP-021, v2026-07-19)

**A terminal close records what the work was WORTH, not only that it was done.** Before Step 6, resolve the plan's **benefit hypothesis** (CAP-PP-020 header block; if the plan predates v1.3.0 and has none, record `NO-HYPOTHESIS (pre-v1.3.0 plan)` — legible, not skipped):

1. **Verdict** ∈ {REALIZED / PARTIAL / NOT-REALIZED / UNMEASURABLE-YET} — citing the observable that resolves it (a verdict with no observable is placeholder-substance, #1568 class). UNMEASURABLE-YET must name what observable would resolve it, and when.
2. **Frame**: evaluated against the `Parent Goal`'s outcome frame (C1002 — an Outcome is frame-evaluated; no Parent Goal → evaluate against the named beneficiary and flag un-parented state).
3. **Cost side (mandatory)**: actual effort from Velocity Analysis + honestly-estimated governance overhead — net value is never asserted from the benefit numerator alone (RQ9, 4-seat critique 2026-07-19).
4. Write the verdict INTO the Retrospective (mutate-scaffold rule, C-CLOSE-007) and cite it in the Parent Goal's next loop review (per-close trigger of GOAL-VALUE-CANON-LINKAGE's loop).

### Step 6: Deferred-Surface Scan (C-CLOSE-004 — MANDATORY)

Scan plan body for deferred-surface markers and emit a structured list for next-plan handoff (L913 closure):

```
## Deferred Surface (emitted by /aget-close-project — consumed by /aget-propose-actions Step 2 KB review)

| Item | Source line | Suggested route |
|------|-------------|-----------------|
| <text matching "deferred to next session" / "Loading Dock" / "spawn" / "future"> | line N | <next-plan candidate or initiative stream> |
```

This block MUST be written verbatim into the plan body (under section `## Deferred Surface`). `/aget-propose-actions` SKILL-024 v1.3.0+ scans for this header at next-plan-creation time (per #1186 wiring).

### Step 7: Output Summary

Emit one-page summary to stdout:
```
=== /aget-close-project: <plan-slug> ===

Plan: planning/PROJECT_PLAN_<name>.md
Status transition: <prev> → <new>
Gates: <X/Y> [x]   V-tests: <A/B> recorded
Retrospective: <N> lines  Deferred-surface items: <N>
Closure timestamp: <ISO-8601>
Closing agent: <identity from .aget/identity.json>
Commit prep: ready (run `git add` + `git commit` per L001)
```

### Step 7.5: Self-Verification (C-CLOSE-005)

For each closure-checklist item, emit PASS/FAIL line:
```
self-verify:
  retrospective:        PASS (3 sub-sections non-empty)
  velocity_analysis:    PASS
  closure_checklist:    PASS (10/10 items addressed)
  finalization:         PASS
  deferred_surface:     PASS (N items scanned)
  status_assertion:     PASS (V-test SHA mapping recorded)
```

If any FAIL: do NOT proceed to Step 8; surface for principal review.

### Step 8: Cross-Plan Coordination

- Do **not** hand-edit `planning/INDEX_PROJECT_PLANS.md`; it is generated. Step 9 owns the register transaction.
- Scan plan body for "Spawned" items in retrospective; flag any that lack a target plan/initiative/L-doc
- Update owning initiative file (if plan references one) — mark stream/deliverable status if applicable

### Step 9: Generated INDEX transaction (C-CLOSE-006)

After Step 5 has written the new `Plan_Status`, when `planning/INDEX_PROJECT_PLANS.md` exists, run
both commands in order:

```bash
python3 scripts/generate_project_plan_index.py
python3 scripts/generate_project_plan_index.py --check
```

The first command re-derives **every** row from the plan sources; the second is the blocking proof that
the committed register candidate is current. A direct row edit is PROHIBITED because it creates a
second status predicate beside `scripts/loading_dock_surfacer.py`. If either command fails, the close is
incomplete: do not emit Step 10's completion signal. If the INDEX is absent, emit a one-line gap note in
the closure summary instead of creating an ad-hoc register.

### Step 10: Skill completion signal

Emit terminal block:
```
/aget-close-project: COMPLETE
  Plan closed: <path>
  Next action: git add <path> && git commit (commit IS structural proof — L001)
  Deferred-surface emitted: yes (consumed by next /aget-propose-actions)
```

## Constraints

- **C-CLOSE-001 (Strict, disposition-aware gate)**: REFUSE `Complete` while any finding remains. For
  `Closed`, `Closed (Partial)`, `Abandoned`, or `Superseded`, REFUSE closure-record/integrity findings and
  any substantive occurrence not reconciled one-to-one in `Unfinished at Close`. A reason explains the
  selected disposition; it never waives an exit finding. The L178 `--override` path is entry-only.
- **C-CLOSE-002 (Closure checklist completeness)**: All template sections must be non-empty before write.
- **C-CLOSE-003 (Verifiable assertion)**: Status transition requires V-test SHA mapping + timestamp + agent identity. Text-edit alone is insufficient.
- **C-CLOSE-004 (Deferred-surface scan mandatory)**: Step 6 MUST execute. Output is consumed by `/aget-propose-actions` (L913 closure).
- **C-CLOSE-005 (Self-verification)**: Step 7.5 PASS for every checklist item before Step 8 fires.
- **C-CLOSE-006 (generated INDEX transaction mandatory when present)**: After the plan status mutation,
  when `INDEX_PROJECT_PLANS.md` exists, MUST run the generator and then `--check`; direct row edits are
  PROHIBITED and either command failing blocks the completion signal. Guarded by
  `tests/test_close_project_index_regeneration.py` (source mutation → STALE; transaction → CURRENT).
- **C-CLOSE-007 (Closer mutates scaffold — gh#1838)**: Closure facts land by MUTATING the scaffolded checklist/sections in place; appending a parallel prose sign-off beside unticked scaffold boxes is PROHIBITED (dual representation, structured copy born stale).
- **C-CLOSE-009 (Value-resolution verdict — CAP-PP-021, 2026-07-19)**: A terminal close SHALL record the benefit-hypothesis verdict + Goal-frame evaluation + cost side in the Retrospective (Step 5.7). A verdict-free terminal close is flagged by close_gate_check — **V-PP-021 WIRED 2026-08-17** (`scan_value_resolution()`; three WARN keys `value_resolution_absent` / `_costless` / `_unobservable`, surfaced in the human output and under the `value_resolution` key in `--json`). **WARN, not BLOCK**: C-CLOSE-009 says a verdict-free close is *flagged*, and making it blocking would change the verdict of every existing terminal-plan test in five modules. Fires only on a terminal `Plan_Status`. Guarded by `tests/test_close_gate_value_resolution.py` (14 tests, both polarities). Corpus at wiring time: **7 of 7** post-rule terminal closures record a verdict; **1 of 7** records benefit with no cost side (`fleet_conceptual_alignment_assessment`, whose own text notes the structural step was not yet built).
- **C-CLOSE-008 (Has-it-run pre-COMPLETE — gh#1855)**: A plan with executable-mechanism deliverables CANNOT transition to COMPLETE without execution evidence for each mechanism (Step 5.5); absent evidence → IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE or CLOSED (PARTIAL). Existence-grep V-tests do not satisfy.

## Enforcement Level

**Strict** (D71 Layer 2 — per AGENTS.md §Structural Skill Routing). Direct status-field edit on a PROJECT_PLAN's `**Plan_Status**:` from IN PROGRESS to COMPLETE/CLOSED/ABANDONED/SUPERSEDED via Edit/Write is **PROHIBITED**. The closure must route through this skill so that:
- Gate-completion gate (C-CLOSE-001) fires
- Verifiable-assertion requirement (C-CLOSE-003) is met
- Deferred-surface scan (C-CLOSE-004) emits L913 handoff

**Known risk** (transparent at v1.0): `AGET_PROJECT_PLAN_SPEC` is DRAFT (#1180). Strict enforcement before spec finalization is principal-authorized (2026-05-21 GO). Follow-on: when spec lands, V-tests V-PRJ-001/002/004 wire to this skill's constraints.

**Override path (L178)**: `--override "<reason>"` bypasses Step 2 only. Records reason in retrospective + commit message. Does not waive Steps 4-7.5.

## Related Skills

- `/aget-create-project` — sibling verb-pair (Strict, exists). Pair completes lifecycle bookend.
- `/aget-propose-actions` — consumer of Step 6 Deferred Surface output (SKILL-024 v1.3.0+).
- `/aget-record-lesson` — for ABANDONED closures with lesson-record link.
- `/aget-close-session` — sibling close-mode skill (different artifact class: session vs project).

## Traceability

| Link | Reference |
|------|-----------|
| Skill ID | SKILL-052 (`.aget/specs/skills/SKILL-052_aget-close-project.yaml`) |
| Proposal | `planning/skill-proposals/PROPOSAL_aget-close-project.md` (APPROVED 2026-05-21) |
| Owning Initiative | INIT-PROJECT-MATURATION (Stream 4 — Lifecycle Symmetry; highest-WSJF per PP-020 D4) |
| Sibling verb-pair | `/aget-create-project` (Strict) |
| Spec (governing) | AGET_PROJECT_PLAN_SPEC.md (DRAFT — #1180) |
| L-docs | L001 (gate discipline), L617 (gate ordering), L649 (closure-time structural gap — originating), L675 (consequence gap), L908 (apply-to-others-not-self), L913 (plan-close→create handoff), L131 (stopping-point bypass), L178 (Human Override), L735 (push window) |
| CAPs | CAP-PRJ-001 (verifiable assertion), CAP-PRJ-002 (closure handoff scan), CAP-PRJ-004 (symmetric close-side gate), CAP-PRJ-007 (Loading Dock detection — consumer) |
| V-tests (pending spec landing) | V-PRJ-001, V-PRJ-002, V-PRJ-004 |
| Cross-fleet evidence | FLEET-UPG-013 + FLEET-UPG-014 D4 root cause (status-field text-edit) |
| Verb registry | `close` (Active, row 29, Common, added v3.13.0; paired with `open`) |
| Architecture | SKILL.md-driven (mirrors `/aget-create-project`); no companion script per 2026-05-21 proposal revision |

---

*aget-close-project v1.0.0*
*Category: Governance (lifecycle bookend)*
*Enforcement: Strict (D71 Layer 2)*
