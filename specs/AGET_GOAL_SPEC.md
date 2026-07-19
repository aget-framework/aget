# AGET_GOAL_SPEC

**Version**: 0.3.0
**Status**: **CANONICAL** — v0.3.0 (2026-07-19): **two-axis formalization + structural linkage** per principal rulings 1/9 of 2026-07-19 (gh#1960 Decision-0 = FULL structural relation; two-axis execution shape RATIFIED same day). Evidence: PP-057 fleet conceptual-alignment assessment (`docs/FINDINGS_pp057_conceptual_alignment.md`, L1219) — four ladder orderings operative fleet-wide, spec-induced (this spec's own v0.2.0 C929 row diverged from the live ontology's C929). Delta: CAP-GOAL-001 v2 (two-axis placement + typed `serves` edge + referential integrity), NEW CAP-GOAL-012 (axis integrity), NEW CAP-GOAL-013 (linkage cardinality + lifecycle cascade), Benefit vocabulary (Output→Outcome→Benefit triple, ruling 5), desiderative-tier slot reserved (REQ-PRIN-2026-003 / gh#1939, ccb-drafted), V-GOAL-009..011, footer version-drift fix. Public push: L735 Saturday 2026-07-25 window. v0.2.0 history: promoted to `aget-framework/aget/specs/` in v3.23.1 (2026-06-20, L735 Saturday window). 27 Goal-Tier ontology concepts ratified (0 reciprocity defects); grounding gap closed; in-use Goal dogfooded. **storage BLOCKER RESOLVED 2026-06-20 via REQ-3** (principal two-tier Decide). The v0.1.0 review's 4 BLOCKERs shared one root (flat 5-column `governance/GOALS.md` under-dimensioned); REQ-3 replaces it with a **two-tier store**: committed Goals = a structured, principal-facing **section-per-goal** registry (carries provenance + status/lifecycle + the loop 5-tuple at ≥1 multiplicity + parent linkage — all 4 review blockers); aspirational Goals = an agent-internal lightweight store off the governance surface. **3-concept grounding gap CLOSED (2026-06-20)**: Goal Identifier (C1014) / Goal Value (C1015, minimal — full rubric next release per principal) / Commitment Tag (C1016) minted + reciprocity-validated (0 defects). **Promotion-ready**; canonical promotion via `/aget-enhance-spec` + public push gated to v3.23 weekend (L735, Saturday window open). Findings: `planning/triad_findings.jsonl` (gate GTA-G-1).
**Author**: private-aget-framework-AGET
**Owning Initiative**: INIT-CORE-ARTIFACT-MATURATION Stream 9 (PP-051)
**Governing Process**: `/aget-enhance-spec` (7-phase, L622)
**theoretical_basis**: BDI declarative goals (Rao & Georgeff 1995; Sardina & Padgham 2011) — a Goal is a declarative desire-state the agent commits to. GORE/KAOS (van Lamsweerde 2001) — goals are *achieve/maintain/avoid* predicates over system state, refined down a ladder. OKR/SAFe — objectives are outcomes, distinct from the key-results/workstreams that pursue them (the C930 separation). Cybernetics (MP#12) — a goal without a regulating loop is an orphan that decays.

---

## Abstract

This specification establishes **Goal** as a durable, governed artifact class and defines its place in the AGET commitment-tier ladder, its required loop binding, its storage form, and the verb-family contract (`propose-goals` → `create-goal`) that produces it. A Goal is a named, cross-session *outcome* — not a workstream — sitting between the agent's permanent North Star and its Initiatives/Workflows.

---

## Motivation

AGET has a plural front-door for goals (`/aget-propose-goals`, SKILL-055, matured to goal-governance) but no durable artifact for a selected candidate to commit into, and no spec placing Goal in the tier ladder. The authorizer `/aget-go` already exposes `--scope goal` and `--shape goals` but cannot resolve a *committed* Goal — latent demand with no sink. The terms above and beside Goal (Purpose, Theme, North Star) are defined nowhere formally, and the framework runs maintenance goals (MP#12 loops) without ever typing them. This spec closes those gaps so Goals become first-class, loop-owning, authorizer-resolvable artifacts.

The central failure mode this spec guards against (C930): a "Goal" defined by the *workstreams* that pursue it rather than the *outcome* it names — which is redundant with Initiative and reintroduces tier confusion.

---

## Scope

**In scope**: the Goal artifact's identity, tier placement, typing, storage, loop binding, workflow binding, conflation guard, and the `create-goal` verb contract.

**Out of scope**: the `propose-goals` generator (governed by SKILL-055); the cross-fleet near-term-"Goal" sense rename (OQ-6 cross-fleet half — principal/sibling-routed, L480); the live-ontology merge of FWRK-039/044 (separate ontology gate, L1077); per-instance goal *content* (instance-authored, not framework-governed).

---

## Vocabulary

| Term | Concept | Definition |
|------|---------|------------|
| Goal | C926 | A durable, named, cross-session **outcome** between North Star (apex) and Initiative/Workflow. Plural. A BDI declarative-goal projection. |
| Goal-Loop Ownership | C927 | Each Goal owns ≥1 loop ⟨owner, trigger, review-action, consequence, cadence⟩; operationalizes MP#12. |
| Goal-Workflow Binding | C928 | A Goal binds the workflows (releases, migrations, fan-outs) executing toward it. |
| Commitment Tier Hierarchy | C929 | **TWO-AXIS (v0.3.0, ruling 9)** — **Intent axis**: North Star/Purpose → [Theme] → **Goal** —realizes→ Outcome. **Vehicle axis**: Initiative → Project (PROJECT_PLAN) → Action. The axes are ORTHOGONAL; they join only via typed cross-axis edges (`serves`, CAP-GOAL-012). *(Supersedes both prior renderings — v0.2.0's linear "NS→Theme→Goal→Objective/Action" AND the live-ontology "NS→Goal→Initiative→Action": the two disagreed (same ID, two ladders — PP-057 F1); ontology C929 re-statement rides the FWRK merge gate.)* |
| **Benefit** | (mint pending — FWRK-062 substrate) | **Measurable improvement resulting from an Outcome, tracked before/after** (PRINCE2/ISO 21502; ruling 5, 2026-07-19). Completes the value chain **Output → Outcome (C1002) → Benefit**: Output = artifact produced (V-tested), Outcome = frame-evaluated result of use, Benefit = quantified improvement. Concept mint rides the ontology gate (L1077). |
| **Serves (cross-axis edge)** | C1222 (Satisfies family) / C1220 | The typed edge joining the axes: a vehicle-axis artifact (Initiative/Project) **serves** ≥0 committed Goals; a Goal is served-by ≥0 vehicles. Replaces rung-ordering between Goal and Initiative. |
| **Realizes** | C1221 | Goal —realizes→ Outcome (ArchiMate; FWRK-048/genus arc). |
| Goal-Initiative Conflation | C930 | (counter) The failure mode: a Goal defined by its workstreams rather than its outcome. |
| Purpose / North Star | C1006 / C966 | The permanent "why"; the apex carrier (distinct from a product KPI). *(Purpose re-pointed C957→C1006: draft C957 collided with the already-merged Gold Standard Evaluation Set; ratified at fresh id C1006, 2026-06-20.)* |
| Theme | C1007 | An organizing band over Goals — corresponds to an Initiative; not a Goal. *(re-pointed C958→C1007; draft C958 collided.)* |
| Goal type | C1012 | KAOS typing: **Achieve** (one-shot end-state — the typical committed Goal), **Maintain** (a steady-state the agent regulates — MP#12 loops), **Soft** (a quality optimized, not satisfied). *(re-pointed C963→C1012.)* |
| **Intention (Represented Goal-State)** | **C1000** | **The teleological parent of Goal** (FWRK-048): a represented, committed goal-state (Mayr *purposive*; BDI). **Goal ⊂ Intention** — a Goal is an Intention *externalized onto a regulating loop* (C927), making the purposive intention teleonomic so it persists across sessions. |
| **Outcome (Frame-Evaluated Effect)** | **C1002** | **What a Goal *realizes*** (FWRK-048) — DISTINCT from the Goal itself (Goal = intent / "what you want"; Outcome = result / "what you get", ArchiMate). ⊂ **Effect (C1001)**. An outcome is goal-relative only when an Intention lies in its causal ancestry; unintended outcomes need no goal. Resolves the C926 "Goal = an outcome" conflation. |
| **Realizable Entity** | **C997** | The genus (Disposition ⊂ Function ⊂ Intention) that connects Goal up the backbone Entity (C293) → **Thing (C292)** (FWRK-048) — the climb that ends the "floats ungrounded" gap. |
| Commitment tag | (E7) | `committed` vs `aspirational` — the agent's commitment level, orthogonal to value and to well-formedness. |

---

## Requirements (Human Level — L742)

The principal's intent, in natural language. The CAP-GOAL specifications below each trace up to one of these parent requirements (Requirements → Specifications, L742; evidence-driven, L700).

| # | Requirement | Traces to |
|---|-------------|-----------|
| **REQ-GOAL-1** | A goal is a durable **outcome**, not a task list. | CAP-GOAL-001, **-002** |
| **REQ-GOAL-2** | Each goal carries a **loop** that keeps it honest. | CAP-GOAL-003, **-004**, -005 |
| **REQ-GOAL-3** | A goal is committed through **one governed path**; **committed goals are a principal-facing surface, aspirational goals are agent-internal** (two-tier, REQ-3). | CAP-GOAL-006, -007, **-008** |
| **REQ-GOAL-4** | Work can be **authorized by goal id**. | CAP-GOAL-009 |
| **REQ-GOAL-5** | A goal's **value is scored separately** from its commitment/status. | CAP-GOAL-010 |
| **REQ-GOAL-6** | A goal has a **lifecycle**; its terminal state is **type-differentiated** (Achieve terminates; Maintain persists). | CAP-GOAL-011 |
| **REQ-GOAL-7** *(v0.3.0 — rulings 1/2/9, 2026-07-19)* | Goal↔vehicle linkage is **structural, not free text**: references resolve, coverage is full-ladder, axes never merge into one ladder. | CAP-GOAL-001 v2, **-012**, **-013** |
| **REQ-GOAL-8** *(v0.3.0 — ruling 5)* | A goal's value chain is **Output → Outcome → Benefit**; realized value is evaluated against the Goal's frame at vehicle close. | Vocabulary (Benefit); CAP-PP-020/021 (PROJECT_PLAN_SPEC — cross-spec) |

Every CAP-GOAL specification has a parent requirement; no orphan specs.

---

## Specifications (CAP-GOAL-*)

### CAP-GOAL-001: Tier Placement

*(Parent: REQ-GOAL-1)*

**(v2, two-axis — ruling 9, 2026-07-19.)** The Goal artifact SHALL be placed on the **intent axis** (North Star/Purpose → [Theme] → **Goal** —realizes→ Outcome; C929 v0.3.0). Initiative and Project are **vehicle-axis** artifacts and SHALL NOT be treated as rungs above or below Goal (CAP-GOAL-012). A Goal's `parent` field SHALL name its intent-axis parent (Theme, or North Star where no Theme exists); linkage to Initiatives/Projects SHALL be expressed as typed **`serves`/`served-by`** cross-axis edges, NOT via `parent`. WHEN a committed Goal's `parent` or `served-by` reference names an identifier, that identifier SHALL resolve to an existing artifact (referential integrity — Decision-0, gh#1960; V-GOAL-009). *(v1 history: "NS/Purpose→Theme→Goal→Objective/Action ladder + parent declares Theme-or-Initiative" — the parent-field dual reading was PP-057 F1's root; the v2 split removes Initiative from `parent` semantics.)* **Migration note**: existing `parent: INIT-*` entries are read as `served-by` edges until re-written; the coverage instrument (CAP-GOAL-013) reports them as legacy-form, not violations, for one minor version.

### CAP-GOAL-002: Outcome-Not-Workstream (Conflation Guard)

*(Parent: REQ-GOAL-1)*

A Goal SHALL be defined by a measurable end-state (an outcome), NOT by an enumeration of workstreams, tasks, or streams. WHEN a candidate Goal's definition enumerates workstreams rather than naming an outcome, `create-goal` SHALL reject it (C930). *(Resolves OQ-5: the conflation guard is a creation V-test, not a warning.)*

### CAP-GOAL-012: Axis Integrity (NEW v0.3.0)

*(Parent: REQ-GOAL-7)*

Governed artifacts SHALL NOT order intent-axis artifacts (North Star, Theme, Goal, Outcome) against vehicle-axis artifacts (Initiative, Project, Action) as rungs of one ladder. Cross-axis reference SHALL use only the typed edges `serves` / `served-by` (vehicle↔Goal) and `realizes` (Goal→Outcome). WHEN a governed artifact renders the commitment-tier hierarchy, it SHALL render both axes or the intent axis alone — never a merged single ladder. *(Root fix for PP-057 F1: four merged-ladder orderings were operative fleet-wide because v0.2.0 canon itself merged the axes inconsistently.)*

### CAP-GOAL-013: Linkage Cardinality & Lifecycle Cascade (NEW v0.3.0)

*(Parent: REQ-GOAL-7)*

Cardinality: a committed Goal MAY be served-by 0..N vehicles; an ACTIVE Initiative or ACTIVE PROJECT_PLAN SHALL be linked (`serves` or legacy `parent`) to ≥1 committed Goal (full-ladder coverage — ruling 2, 2026-07-19); `(none)` + rationale is a legible temporary state the coverage instrument reports. Lifecycle cascade: WHEN a committed Goal transitions to `abandoned`/`superseded`, every vehicle serving it SHALL be flagged for re-parenting review at its next gate boundary (no silent orphaning); WHEN an Achieve Goal transitions to `achieved`, its serving vehicles' close records SHALL cite the realized Outcome (value-resolution hook, CAP-PP-021 cross-ref). The reference instrument is `scripts/goal_link_check.py --coverage` (three-state: PASS/FAIL/UNREACHABLE).

### CAP-GOAL-003: Goal Typing

*(Parent: REQ-GOAL-2)*

A Goal SHALL be typed as one of {Achieve, Maintain, Soft} (KAOS, C1012). Maintenance loops surfaced by MP#12 SHALL be representable as **Maintain** Goals (C1010; the type-less-maintenance-goal failure mode is C965 Goal-Type Collapse).

### CAP-GOAL-004: Loop Binding Required at Creation

*(Parent: REQ-GOAL-2)*

A Goal SHALL own ≥1 loop ⟨owner, trigger, review-action, consequence, cadence⟩ (C927/MP#12), and `create-goal` SHALL require at least one bound loop **at creation time** (not loop-attach-later). *(Resolves OQ-4.)*

### CAP-GOAL-005: Workflow Binding

*(Parent: REQ-GOAL-2)*

A Goal MAY bind the workflows executing toward it (C928); WHERE a workflow is run in service of a Goal, it SHOULD reference that Goal's id.

### CAP-GOAL-006: Storage Form — Two-Tier (REQ-3)

*(Parent: REQ-GOAL-3)*

Goals SHALL be stored in **two tiers**, by commitment tag (REQ-3 — supersedes the v0.1.0 flat 5-column table, which review found under-dimensioned):

**(a) Committed Goals — principal-facing surface.** A committed Goal SHALL be stored as a **structured section** (NOT a flat table row) in **`governance/GOALS.md`** (per-instance, human-readable, principal-readable/editable). Each section SHALL carry, at minimum:
- `id` — Goal Identifier (unique within instance; scheme per C1014 Goal Identifier)
- `outcome` — the measurable end-state (CAP-GOAL-002)
- `type` — {Achieve, Maintain, Soft} (CAP-GOAL-003)
- `status` — lifecycle state (CAP-GOAL-011)
- `commitment` — `committed` (this tier)
- `parent` — Theme/Initiative linkage (CAP-GOAL-001), where one exists
- `loops[]` — ≥1 structured loop ⟨owner, trigger, review-action, consequence, cadence⟩ (CAP-GOAL-004), multiplicity ≥1
- `provenance` — `create-goal` invocation evidence (enables the CAP-GOAL-008 Strict check)

The section-per-goal form carries provenance + status/lifecycle + the loop 5-tuple at ≥1 multiplicity + parent linkage — the four dimensions the v0.1.0 flat table could not (review root-cause closed).

**(b) Aspirational Goals — agent-internal.** An aspirational Goal SHALL be stored off the governance surface in an agent-internal lightweight store (`.aget/goals/aspirational.jsonl`, append-only), NOT in `governance/GOALS.md`. Promotion aspirational→committed is a `create-goal` act that writes the (a)-tier section. *(Keeps the principal-facing surface to genuinely-committed goals; aspirational candidates do not clutter it — REQ-3.)*

*(Resolves OQ-1 at the mechanism level: two-tier, committed=structured-section / aspirational=agent-internal; direction confirmed by REQ-3 / decide-packet D4.)*

### CAP-GOAL-007: Verb-Family Contract

*(Parent: REQ-GOAL-3)*

The plural generator `/aget-propose-goals` (SKILL-055) SHALL produce a candidate set; the singular committer `/aget-create-goal` SHALL consume one selected candidate and commit it per CAP-GOAL-002..006 (L1067 two-propose semantics; L1085 plural-leads-singular).

### CAP-GOAL-008: Enforcement Level

*(Parent: REQ-GOAL-3)*

`/aget-create-goal` SHALL be **D71-Strict**: direct authoring of a committed-Goal section in `governance/GOALS.md` is prohibited; creation MUST route through the skill, which writes the structured section incl. the `provenance` field (parity with `create-project`/`create-initiative`). *(Resolves OQ-2 — principal Decide. Adds a row to the AGENTS.md D71 routing table.)* The aspirational tier (CAP-GOAL-006b) is **Advisory** — `propose-goals` may append aspirational candidates without Strict ceremony; Strict applies only at the committed-tier write.

### CAP-GOAL-011: Lifecycle & Type-Differentiated Terminal State

*(Parent: REQ-GOAL-6)*

A committed Goal SHALL carry a `status` ∈ {`active`, `achieved`, `abandoned`, `superseded`}. The terminal state SHALL be **type-differentiated** (REQ-GOAL-6): an **Achieve** Goal reaches a terminal `achieved` when its outcome is met (it terminates); a **Maintain** Goal has **no `achieved` terminal** — it persists in `active` under its regulating loop and terminates only via `abandoned`/`superseded` (a Maintain Goal that "completes" is a category error). `create-goal` SHALL set `status: active` at creation; status transitions are governed edits. *(Closes the review's status/lifecycle blocker — a Goal without lifecycle is Loading-Dock-by-construction, L656; lands REQ-GOAL-6, formerly a carried design input.)*

### CAP-GOAL-009: Authorizer Resolution

*(Parent: REQ-GOAL-4)*

`/aget-go --scope goal` SHALL resolve against a committed Goal id in `governance/GOALS.md` (today `--shape goals` only composes proposals). *(Closes the latent-demand gap found at G-1.4.)*

### CAP-GOAL-010: Value Is Separable

*(Parent: REQ-GOAL-5)*

A Goal's *potential value* (scored by the paired `RUBRIC_goal_value`, the L851 quality-loop "Rubrics" arm) SHALL be orthogonal to its commitment tag (CAP-GOAL E7) and its well-formedness (CAP-GOAL-002). The spec SHALL NOT bundle value into the commitment or conflation checks.

---

## Verification

| V-test | Requirement | Check |
|--------|-------------|-------|
| V-GOAL-001 | CAP-GOAL-002 | `create-goal` rejects a candidate whose body enumerates streams/tasks and names no outcome. |
| V-GOAL-002 | CAP-GOAL-003 | Every committed Goal row has a `type ∈ {Achieve, Maintain, Soft}`. |
| V-GOAL-003 | CAP-GOAL-004 | `create-goal` refuses to commit a Goal with zero bound loops. |
| V-GOAL-004 | CAP-GOAL-006a | A committed Goal appears as a well-formed structured section in `governance/GOALS.md` (id, outcome, type, status, commitment, ≥1 loop, provenance all present). |
| V-GOAL-005 | CAP-GOAL-008 | A `governance/GOALS.md` committed-Goal section added without `/aget-create-goal` provenance is flagged as a D71 bypass. |
| V-GOAL-006 | CAP-GOAL-009 | `/aget-go --scope goal <id>` resolves a committed Goal id. |
| V-GOAL-007 | CAP-GOAL-006b | An aspirational Goal is stored in `.aget/goals/aspirational.jsonl`, NOT on the `governance/GOALS.md` surface. |
| V-GOAL-008 | CAP-GOAL-011 | A **Maintain** Goal cannot transition to `achieved` (type-differentiated terminal); an **Achieve** Goal can. |
| V-GOAL-009 *(v0.3.0)* | CAP-GOAL-001 v2 | Every identifier named in a committed Goal's `parent`/`served-by` fields resolves to an existing artifact; a dangling reference FAILs `goal_link_check`. |
| V-GOAL-010 *(v0.3.0)* | CAP-GOAL-012/-013 | `goal_link_check --coverage` reports every ACTIVE Initiative/PROJECT_PLAN lacking a resolvable committed-Goal link; 0 false positives on conformant artifacts. |
| V-GOAL-011 *(v0.3.0)* | CAP-GOAL-013 | A Goal transitioned to `abandoned`/`superseded` with ≥1 serving vehicle produces a re-parenting flag (no silent orphaning). |

---

## Grounding Gap (PROMOTION BLOCKER — verified 2026-06-19)

Not all load-bearing terms resolve to formal concepts (L954/L1092 audit, L980).

**Teleology half — GROUNDED 2026-06-19 via `_DRAFT_FWRK-2026-048` (C997-C1005, staged; merge-gated L1077)**: **Outcome→C1002**, **Intention→C1000** (Goal's parent), Effect→C1001, Realizable Entity→C997, Disposition→C998, Function→C999, + meta-concepts Teleological Ascent (C1003), Derived Intentionality (C1004). *Correction of a prior over-claim*: this section previously listed "outcome→C926" as grounded, but C926 IS Goal and was *defined using* "outcome" — circular; Outcome is now **independently** grounded (C1002), and the Goal definition can declare `broader: Intention (C1000)` + `realizes → Outcome (C1002)` up to Thing (C292). (Prior grounded: loop→C927, commitment tier→C929, goal types→FWRK-044.)

**Plan/ICE half — STILL ungrounded + load-bearing (MUST be defined before canonical promotion)**: Workstream, Theme(-as-band), Objective, Commitment (the information-artifact / commitment-axis scaffold — a *separate* future FWRK, BFO/IAO objective-specification family), plus:

| Term | Used in | Disposition |
|------|---------|-------------|
| **Goal Identifier** | REQ-GOAL-4, CAP-GOAL-009 | **C1014** (id scheme + uniqueness) — grounded 2026-06-20 |
| **Goal Value** (potential value) | REQ-GOAL-5, CAP-GOAL-010 | **C1015** (minimal — dimension named; full `RUBRIC_goal_value` deferred to next release per principal) |
| **Commitment Tag** (committed/aspirational) | REQ-GOAL-5, CAP-GOAL-010 | **C1016** (committed vs aspirational marker) — grounded 2026-06-20 |

Acceptably informal at the Requirements level (L742, no grounding needed): "governed path" (= the D71-Strict route, rhetorical), "keeps it honest", "status", "task list".

**Owner**: INIT-ONTOLOGY-MATURATION (concept minting via the L954 vocab pre-check) + the `/aget-enhance-spec` canonical-promotion Auditor pass. NOT minted unilaterally here (no-jump-to-fix).

---

## Desiderative Tier (slot reserved — v0.3.0)

*(REQ-PRIN-2026-003, gh#1939: a Desire/Dream primitive ABOVE the aspirational tier — pre-adoption wants, five-literature grounding per ccb:L110. The section is ccb-drafted and lands here at v3.28 grooming coordination; this slot reserves the position so v0.3.0 and the ccb draft do not collide.)*

## Open Items (carried)

- **OQ-6 (cross-fleet half)**: reserve bare "Goal" = strategic-outcome here; the sibling `SOP_near_term_ambition_projection` near-term-sense rename is principal/sibling-routed (L480) — not resolved by this spec.
- **Ontology merge**: FWRK-039 (C926–C930) + FWRK-044 (C957–C966) remain staged drafts; merge to live ontology is a separate gate (L1077). This spec *references* them at the adopted depth (OQ-7: full ladder + KAOS typing).
- **`RUBRIC_goal_value`**: paired build deliverable (Gate 2); cross-fleet ownership check pending (L954) — sibling `RUBRIC_goal_scoring_v0.1` is a *selection* ranker, not a value rubric (L1093).

---

*AGET_GOAL_SPEC v0.3.0 CANONICAL — two-axis + structural linkage (2026-07-19). "A Goal is an outcome that owns a loop — and the vehicles that serve it are on another axis." (v0.1.0/v0.2.0 footer version-drift fixed this rev.)*
