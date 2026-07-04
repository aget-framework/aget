# DESIGN DIRECTION: Skill Verb Vocabulary

**Status**: Active
**Created**: 2026-02-23
**Origin**: Session 2026-02-23 (verb naming analysis)
**Relates To**: SKILL-009 (aget-propose-skill), SKILL-012 (aget-create-skill), AGET_SKILLS_SPEC

---

## Purpose

Defines the verb vocabulary for AGET skill naming. All skills follow the `aget-{verb}-{object}` pattern (CS-002, PS-002). This document captures the approved verb inventory, external alignment research, compliance analysis, and directional commitments for vocabulary evolution.

---

## Naming Pattern

```
aget-{verb}-{object}
```

**Constraints**:
- Verb MUST be a standalone transitive verb (can take a real object)
- Object MUST be a noun or noun phrase
- Kebab-case throughout
- Prefix `aget-` is mandatory

**Test**: Can the verb take a different object? `aget-{verb}-X` should be plausible.

---

> **Working-copy banner** (2026-05-16, PP-021 G5.6): The **canonical source of truth** for this registry is `aget/ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md` (cross-fleet read surface). This private copy is the authoring working copy maintained by `private-aget-framework-AGET`; edits here propagate to canonical via that agent. Cross-fleet consumers (templates, downstream agents, validators) SHALL read from canonical post-v3.18.0.

## Approved Verb Inventory (v3.16.0)

> **Currency note** (2026-05-02; amended 2026-05-16 at PP-021 Gate 1 G1.4): Header refreshed v3.7.0 → v3.16.0 as PP-021 Gate 1 advance work in session_2026-05-02_2121. Body has carried inline additions across v3.10.0 (capture retired), v3.13.0 (close, open), v3.14.0 (name, ask), v3.15.0 (go, score Domain Innovation). Full registry review + drift adjudication of **5 unregistered verbs** (process, promote, release, scan, update) governed by `planning/PROJECT_PLAN_verb_registry_currency_v1.0.md` Gates 0-6; separately, `describe` is in §Reserved Verbs (graduates at Gate 4 G4.1) — not unregistered drift. Maintenance cadence to be wired in Gate 5 (SOP_verb_registry_maintenance.md). v3.16.0+: no new Active verbs added (latest Active = `go` row 33 at v3.15.0).

### Compliant Verbs (37 active, 1 retired)

| # | Verb | Used In | Category | Stands Alone | Takes Objects |
|---|------|---------|----------|:---:|:---:|
| 1 | assess | assess-risk, assess-tradeoffs, assess-client | Governance | Yes | Yes |
| 2 | analyze | analyze-data | Diagnostic | Yes | Yes |
| 3 | broadcast | broadcast-fleet | Communications | Yes | Yes |
| ~~4~~ | ~~capture~~ | ~~capture-observation~~ | ~~Evolution~~ | ~~Yes~~ | ~~Yes~~ | **RETIRED v3.10.0** (#480) — all uses migrated to `record` |
| 5 | check | check-health, check-evolution, check-sessions, check-kb | Diagnostic | Yes | Yes |
| 6 | create | create-project, create-skill | Common | Yes | Yes |
| 7 | design | design-architecture | Common | Yes | Yes |
| 8 | document | document-finding | Evolution | Yes | Yes | **PENDING RETIREMENT v3.19** — collapsed-into `record --canonical` per decision 2026-05-16 (see §Future Reconciliations); deployed `document-*` skills migrate v3.19 INIT-SKILL-MATURATION Stream 4 |
| 9 | enhance | enhance-spec | Lifecycle | Yes | Yes |
| 10 | escalate | escalate-issue | Governance | Yes | Yes |
| 11 | execute | execute-task | Lifecycle | Yes | Yes |
| 12 | expand | expand-ontology | Evolution | Yes | Yes |
| 13 | file | file-issue | Governance | Yes | Yes |
| 14 | generate | generate-report, generate-requirement | Common | Yes | Yes |
| 15 | handle | handle-incident | Lifecycle | Yes | Yes |
| 16 | lint | lint-code | Diagnostic | Yes | Yes |
| 17 | make | make-decision | Common | Yes | Yes |
| 18 | propose | propose-skill, propose-project, propose-actions, propose-engagement | Governance | Yes | Yes |
| 19 | provide | provide-feedback | Communications | Yes | Yes |
| 20 | recommend | recommend-action | Governance | Yes | Yes |
| 21 | record | record-lesson | Evolution | Yes | Yes |
| 22 | report | report-progress | Communications | Yes | Yes |
| 23 | review | review-project, review-pr, review-artifact, review-budget, review-agent | Diagnostic | Yes | Yes |
| 24 | run | run-tests, run-playbook | Lifecycle | Yes | Yes |
| 25 | save | save-state | Data | Yes | Yes |
| 26 | search | search-literature | Common | Yes | Yes |
| 27 | study | study-topic | Research | Yes | Yes |
| 28 | validate | validate-spec | Diagnostic | Yes | Yes |
| 29 | **close** | close-session | Common | Yes | Yes | **Added v3.13.0** — SP-008. PowerShell: Close (Common). Paired with `open`. |
| 30 | **open** | open-session | Common | Yes | Yes | **Added v3.13.0** — SP-010 (pending). PowerShell: Open (Common). Paired with `close`. Principal confirmed 2026-04-10. |
| 31 | **name** | name-session | Common | Yes | Yes | **Added v3.14.0** — SP-015. PowerShell: Rename (Common) — divergence: `name` = generate contextual name from entity type + convention, `rename` = change existing name. Domain innovation: structured name generation using agent identity, date, and content analysis. Espanso: `;;anase` (na=name, se=session). |
| 32 | **ask** | ask-clarification, ask-followup | Research | Yes | Yes | **Production v1.0.0 (v3.25 C-25-02: SKILL-045 graduated draft->production; altitude filter ASK-006/007).** **Added v3.14.0** — SP-018. PowerShell nearest: Request (Lifecycle) — divergence: `ask` = interactive dialogue with an intelligent counterpart to narrow a prediction distribution; `request` = formal submission. Domain innovation: quality metric is entropy reduction on next-action prediction, not thoroughness. Consumes #1020, feeds #1019 prediction-accuracy reward. Principal-approved 2026-04-18. Espanso (proposed): `;;aascl` (aa=ask, cl=clarification), `;;aasfo` (aa=ask, fo=followup). |
| 33 | **go** | go (bare; flags: `--principles`, `--scope`, `--count`, `--shape`, `--record-only`, `--dry-run`) | **Governance / Authorization** | Yes (transitive via target-reading) | Yes (`--gate`, `--action`, `--goal`) | **Added v3.15.0** — SP-022. PowerShell nearest: Approve (Lifecycle) — divergence: `approve` = authorization-only; `go` = authorization + release-to-execute. Domain innovation: principal-lived vocabulary (L466 "Go ahead / Yes / Proceed = Execute"); Claude Code-native. Codifies the GO-with-scaffold compensating control (`;;g*pr*` espanso) as framework primitive. Coupled with Tier 2 meta-principle #11 "Principled Execution" + new AGET_Term "Healthy Friction" (enforcement posture between Advisory and Strict). Espanso migration: `;;g_pr_` → `;;ago_`; `;;g{3,5}pr_` → `;;ago{3,5}{a,g}_` (a=actions, g=goals). See SP-022, SKILL-048, GOVERNANCE_PRINCIPLES §Tier 2 #11. |
| 34 | **describe** | describe-session, describe-project, describe-skill | Common | Yes | Yes | **Added v3.18.0** — SP-009 (graduated from §Reserved row 5 via PP-021 Gate 2 G2.1; baseline-credits Gate 4 G4.1). Generate narrative summary of a structured artifact for human consumption. Distinct from `check` (diagnostic pass/fail) and `review` (assessment with judgment) — `describe` produces readable prose from structured data. Domain innovation — no PowerShell equivalent (`Format` is output formatting, not narrative synthesis). Motivated by: table-heavy agent output is structurally correct but hard for humans to read. Reserved-section row 5 entry to be removed at Gate 4 G4.3. |
| 35 | **process** | process-observation | Lifecycle | Yes | Yes | **Added v3.18.0** — PP-021 Gate 2 G2.2. Routing verb: classify a captured observation and dispatch to downstream skills per File-and-Route pattern (L665). Distinct from `record` (preservation), `check` (diagnostic), `route` (would be over-specialized — `process` covers classify+route+dispatch). Skill `aget-process-observation` implements File-and-Route for the capture pipeline. PowerShell nearest: none — domain-specific routing semantics; closest analogue is `Invoke-` but that's too generic. |
| 36 | **promote** | promote-issue | Governance | Yes | Yes | **Added v3.18.0** — PP-021 Gate 2 G2.3. Lifecycle promotion verb: move an artifact from a lower-trust surface to a higher-trust surface with sanitization gating. Distinct from `publish` (would be one-way without provenance), `release` (deprecated triad per §Collapsed Release Triad). Skill `aget-promote-issue` implements private→public issue promotion (private gmelli/aget-aget → public aget-framework/aget) with sanitization. Distinct semantic from `enhance` (in-place improvement). PowerShell nearest: none — promotion-with-gating is domain-specific. |
| 37 | **score** | (proto-impls: `scripts/score_requirements.py`, `score_specifications.py`, `score_verification_tests.py`; planned `/aget-score-*` skills) | Diagnostic | Yes | Yes | **Added v3.18.0** — PP-021 Gate 4 G4.2 (graduated from §Domain Innovation row pre-edit; baseline-credits future-skill-deployment trigger). Sibling of `check` in the Diagnostic category. `check` reads state qualitatively (pass/fail or ordinal); `score` applies a rubric mechanically and returns a quantitative level (L0-L3 or L0-L5). L749 Requirements-Rubric Duality formalizes the rubric+scorer pairing. Distinct from `review` (judgment-based assessment with narrative). Initial planned object pairings: `score-requirement`, `score-specification`, `score-verification-test`, `score-initiative`, `score-sop`, `score-skill`, `score-rubric`, `score-handoff`, `score-session`. Proto-implementations live in `scripts/score_*.py`; first `/aget-score-*` skill deployment activates the verb fully. PowerShell nearest: `Test` (Diagnostic) / `Measure` (Diagnostic) — divergence: `Test` returns boolean, `Measure` returns aggregates; `score` returns rubric-derived ordinal level. See L867 (coherence-directed-investment pattern). |

### Non-Compliant Verbs (5 issues)

> **Numbering note** (2026-05-02): Rows renumbered NC1..NC5 to eliminate collision with Active inventory rows 25-29 (save, search, study, validate, close). Same number identifying two different verbs was a within-document coherence violation flagged in `docs/AUDIT_verb_registry_currency_2026-05-02.md`.

| # | Current | Skill(s) | Issue | Severity |
|---|---------|----------|-------|----------|
| NC1 | **wake** | wake-up | Phrasal verb; "up" is particle, not object. But "wake" can take objects (`wake agent-X`). | Low |
| NC2 | **wind** | wind-down | Not a standalone verb. "Wind" requires "down" — inseparable phrasal verb. Cannot take other objects. | High |
| NC3 | ~~**study**~~ | ~~study-up~~ | ~~Missing hyphen.~~ **RESOLVED**: Renamed to `aget-study-up` (P2.10 Gate 1). | ~~High~~ ✅ |
| NC4 | ~~**healthcheck**~~ | ~~healthcheck-evolution, healthcheck-sessions, healthcheck-kb~~ | ~~Compound noun.~~ **RESOLVED**: Specs aligned to deployed `check-*` (P2.10 Gates 2-3). | ~~Medium~~ ✅ |
| NC5 | ~~**sanity**~~ | ~~sanity-check~~ | ~~Reversed noun-verb.~~ **RESOLVED**: Specs aligned to deployed `check-health` (P2.10 Gates 2-3). | ~~Medium~~ ✅ |

### Domain Innovation Verbs (5)

These verbs diverge from standard taxonomies (PowerShell, REST) but carry meaningful semantic distinctions worth preserving.

| Verb | Standard Equivalent | Why We Keep Ours |
|------|-------------------|------------------|
| **enhance** | Update, Edit (PowerShell) | Implies structured improvement of an existing artifact through a governed lifecycle (L622). Scope includes (a) **growth** — adding capability, requirements, cross-references, structural improvements per a defined process model; (b) **maintenance / healing** — recognizing defects encountered during enhancement work and routing per severity: *Tier-A* trivially fixable (applied in-skill), *Tier-B* structural-bounded (routed to backlog artifact), *Tier-C* scope-affecting (escalated via issue per D71). Enhance is the therapeutic counterpart of `check` (diagnostic, read-only); the canonical pipeline is `check` → `enhance` (or `deprecate` when retirement is more appropriate than healing). Fleet evidence: 5 plans across 3 agents independently converged on this verb for this activity (L436 threshold: 2+). Maintenance dimension added 2026-04-19 per principal direction; L867 captures the framework-level enhance-coherence analogue. |
| **record** | Write, Save (PowerShell) | Implies deliberate preservation of a learning. Distinct from mechanical write/save. |
| ~~**capture**~~ | ~~Write, Save (PowerShell)~~ | ~~Implies seizing a transient observation before it's lost.~~ **RETIRED v3.10.0** — semantic merged into `record`. |
| **study** | Read, Get (PowerShell) | Implies active investigation and analysis. Distinct from passive data retrieval. Maps to Bloom's Analyze level, not Remember. |
| **go** | Approve (PowerShell) | Combines authorization AND release-to-execute in one verb. Approve is authorization-only (principal grants permission); go is the complete act (authorize + release). Matches principal-lived vocabulary in `GO` / `go ahead` (L466); aligns with Claude Code-native usage. Added v3.15.0 per SP-022. |
| ~~**score**~~ | ~~Test, Measure (PowerShell)~~ | **GRADUATED v3.18.0** to §Compliant Verbs row 37 per PP-021 Gate 4 G4.2. Original Domain Innovation rationale: Sibling of `check` in the Diagnostic category. Where `check` reads state across systems and reports gaps qualitatively, `score` applies a rubric mechanically and returns a quantitative level (L0-L3 or L0-L5). The L749 Requirements-Rubric Duality formalizes the rubric+scorer pairing; today's `scripts/score_requirements.py`, `score_specifications.py`, `score_verification_tests.py` are the proto-implementations. Distinct from `check` (qualitative gap-finding) and `review` (judgment-based assessment). Added v3.15.0 per principal direction 2026-04-19; L867 captures the broader coherence-directed-investment pattern this verb operationalizes. Initial object pairings: `score-requirement`, `score-specification`, `score-verification-test`, `score-initiative`, `score-sop`, `score-skill`, `score-rubric`, `score-handoff`, `score-session`. **Status (2026-05-02)**: Pending activation — listed here as Domain Innovation but absent from numbered Active inventory; proto-implementations live in `scripts/score_*.py` not as `/aget-score-*` skills. Graduation governed by `PROJECT_PLAN_verb_registry_currency_v1.0.md` Gate 4. |

---

## External Alignment

### PowerShell Approved Verbs (primary reference)

The only production system with a formally specified, closed verb taxonomy (~100 verbs, 7 categories, explicit synonym prohibitions). Pattern: `Verb-Noun`.

| AGET Verb | PowerShell Equivalent | PS Category |
|-----------|----------------------|-------------|
| go (v3.15) | Approve (domain innovation — see above) | Lifecycle |
| open (proposed) | Open | Common |
| close (proposed) | Close | Common |
| create | New | Common |
| enhance | Update / Edit | Data (domain innovation — see above) |
| save | Save | Data |
| check | Test | Diagnostic |
| score (v3.15 — domain innovation) | Test / Measure | Diagnostic |
| review | Test / Confirm | Diagnostic / Lifecycle |
| propose | Request / Submit | Lifecycle |
| file | Submit | Lifecycle |
| record | Write / Save | Communications / Data |
| capture | Write / Save | Communications / Data |
| study | Read / Get | Communications / Common |
| validate | Test | Diagnostic |
| run | Invoke / Start | Lifecycle |
| search | Find / Search | Common |

**Source**: [PowerShell Approved Verbs](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands)

### W3C / Formal Ontologies

| Standard | Relevant Verbs | AGET Overlap |
|----------|---------------|-------------|
| **Schema.org Actions** (16 types) | CheckAction, ReviewAction, CreateAction, ControlAction (Activate/Deactivate) | check, review, create, open/close |
| **W3C ActivityStreams** (30 verbs) | Create, Offer, Flag, Read, Update, Accept, Reject | create, propose, file, study, record |
| **PROV-O** (Provenance) | generate, use, start, end, derive, inform | Session lifecycle model |
| **Bloom's Taxonomy** (6 levels) | Remember→Understand→Apply→Analyze→Evaluate→Create | Validates cognitive-level distinctions: study (Analyze) vs. record (Remember) vs. create (Create) |

### CLI Framework Patterns

| Framework | Pattern | Session Lifecycle |
|-----------|---------|-------------------|
| Docker | `docker {verb}` / `docker {noun} {verb}` | create, start, stop, kill, rm |
| Kubernetes | `kubectl {verb} {resource}` | create, delete; rollout: restart, pause, resume |
| GitHub CLI | `gh {noun} {verb}` | create, close, reopen, delete |
| Terraform | `terraform {verb}` | init, validate, plan, apply, destroy |
| Git | `git {verb}` | init, clone, commit, push, pull |
| Heroku | `heroku {topic}:{verb}` | create, destroy, restart |
| IBM CL (OS/400) | 3-letter verb + 3-letter object | CRT, DLT, CHG, DSP, STR, END |

### Session Lifecycle Verb Pairs (cross-framework)

| Pattern | Open/Start | Close/End | Used By |
|---------|-----------|-----------|---------|
| **open / close** | open | close | PowerShell, databases, HTTP, IDEs, window managers |
| **start / stop** | start | stop | Docker, PowerShell, services |
| **connect / disconnect** | connect | disconnect | PowerShell, databases |
| **begin / end** | begin | end | Database transactions, IBM CL |
| **create / destroy** | create | destroy | Terraform, Kubernetes, Docker |

**Assessment**: `open`/`close` is the dominant pattern for **stateful sessions** (load state, establish context / capture state, write artifacts). `start`/`stop` is for **processes**. AGET sessions are stateful, not process-like.

---

## Directional Commitments

### v3.7.0 (non-breaking reconciliation) — COMPLETE

| Item | Current | Target | Type | Status |
|------|---------|--------|------|--------|
| Fix study-up hyphen | `aget-studyup` | `aget-study-up` | Rename (deployed skill) | ✅ DONE (P2.10 Gate 1) |
| Reconcile healthcheck | `healthcheck-*` (spec) vs `check-*` (deployed) | `check-*` everywhere | Spec alignment | ✅ DONE (P2.10 Gates 2-3) |
| Reconcile sanity-check | `sanity-check` (spec) vs `check-health` (deployed) | `check-health` | Spec alignment | ✅ DONE (P2.10 Gates 2-3) |
| Register `check` as approved verb | Not in formal verb list | Add to approved verbs | Vocabulary update | ✅ Added to compliant verbs (row 25) |
| Register `study` as approved verb | Not in formal verb list | Add to approved verbs | Vocabulary update | ✅ Added to compliant verbs (row 26) |

### v3.10.0 (non-breaking — Learning family unification + object fix)

| Item | Current | Target | Type | Status | Issue |
|------|---------|--------|------|--------|-------|
| Unify Learning family verb | `aget-capture-observation` | `aget-record-observation` | Verb consistency | ✅ DONE (G1) | #480 |
| Unify Learning family verb | `aget-capture-nugget` | `aget-record-nugget` | Verb consistency | ✅ DONE (G1) | #480 |
| Fix particle-as-object | `aget-study-up` | `aget-study-topic` | Object compliance (CS-002) | ✅ DONE (G1) | #480 |
| Retire `capture` verb | Row 4 in approved verbs | Remove — all uses migrated to `record` | Vocabulary cleanup | ✅ DONE (G4) | #480 |

**Evidence for study-up→study-topic**: `study_up.py --topic` is required arg; skill signature always takes `<topic>`; #466 fix confirms "topic" is operative noun; accumulated usage since v3.7.0 resolves deferred decision.

### v3.13+ (non-breaking — session verb evolution)

**Updated 2026-04-10**: Downgraded from v4.0 breaking to v3.x non-breaking. Three prior successful non-breaking renames (`study-up` → `study-topic`, `capture` → `record`, `healthcheck` → `check-health`) prove alias grace periods work. Upstream issue: gmelli/aget-aget#297.

**Architecture decision**: Composition, not rename. `aget-close-session` orchestrates `aget-wind-down` (Phase 2 delegate). Wind-down remains functional with deprecation notice. See SP-008. L562 evidence: rename caused 32/32 false-positive drift at scale.

| Item | Current | Target | Architecture | Status |
|------|---------|--------|-------------|--------|
| Add `close-session` | — | `aget-close-session` | Composition (orchestrates wind-down) | SP-008 PROPOSED |
| Deprecate `wind-down` as top-level | `aget-wind-down` | Deprecated alias (POL-DEP-001, 2 minor version grace) | Retained as Phase 2 delegate | Pending SP-008 approval |
| Add `open-session` | — | `aget-open-session` | Composition (orchestrates wake-up) | **Principal confirmed 2026-04-10**. SP-010 pending. |
| Deprecate `wake-up` as top-level | `aget-wake-up` | Deprecated alias (POL-DEP-001, 2 minor version grace) | Retained as delegate | Blocked on SP-010 approval |
| ~~Generalize `study-up`~~ | ~~`aget-study-up`~~ | ~~`aget-study-topic`~~ | — | **MOVED to v3.10.0** — evidence from usage resolved deferred decision (#480) |

### Reserved Verbs (no skill yet — pre-approved for future use)

| # | Verb | Anticipated Use | Category | Rationale | L-doc |
|---|------|----------------|----------|-----------|-------|
| 1 | **sync** | sync-initiative, sync-state | Data | Bidirectional state reconciliation between AGET KB and external SoRs (Linear, GitHub, Slack). Distinct from `check` (read-only inspection) — `sync` implies write to external system. PowerShell equivalent: `Sync` (Data category). Only needed if bidirectional write is required; read-only external consumption uses `check`. | L759 |
| 2 | **fix** | fix-spec, fix-template | Lifecycle | Corrective work on an existing artifact — restores conformance, repairs defects, aligns toward target state. **Conceptual parent of `enhance`** (`enhance ⊂ fix`: growth is a type of fix — fixing what's missing). Deployment-wise, both verbs are peers: `enhance` is deployed (SKILL-041, fleet-convergence justified); `fix` remains reserved for future skills where defect-correction is the *primary* intent (e.g., `/aget-fix-spec`, `/aget-fix-template` remain likely deployments). Canonical pairing pattern (emerging): `enhance-*` pairs with rubric/ontology-like artifacts (grow toward finer measurement); `fix-*` pairs with spec/contract-like artifacts (correct toward governing conformance). PowerShell equivalent: `Repair` (Diagnostic category). | PP-002 |
| 3 | **deprecate** | deprecate-spec, deprecate-skill | Lifecycle | Signal that an artifact will be replaced. Triggers grace period, migration path, and replacement pointer per POL-DEP-001. Domain innovation — no direct PowerShell equivalent (`Disable` is closest but semantically distinct). Transition verb: `enhance` → `deprecate` → `retire`. | PP-002, L671 |
| 4 | **retire** | retire-template, retire-skill | Lifecycle | Remove an artifact from active use after deprecation grace period. Archive for reference but remove from active discovery. PowerShell equivalent: `Remove` (Common category). Pairs with `create` (Design Principle #3: lifecycle bookends). | PP-002 |

> **Graduation note** (2026-05-16, PP-021 Gate 4 G4.3): `describe` (formerly Reserved row 5; SP-009) graduated to §Compliant Verbs row 34 at v3.18.0 per Gate 2 G2.1 + Gate 4 G4.1 (baseline-credited). Row removed from Reserved; no renumbering needed (was last row).

**Activation criteria**: Reserve becomes Approved when first skill using the verb is deployed. Per ADR-008 progression.

### Deferred (post-PP-021 reconciliation, 2026-05-16)

| Item | Status | Notes |
|------|--------|-------|
| Formal approved verb registry (SKOS) | **v3.19+ candidate** (NOT subsumed by current markdown form) | Current registry is curated markdown; not SKOS-formal. Model after PowerShell's categorized verb taxonomy. Create `ONTOLOGY_skill_verbs.yaml` with categories, synonyms, and pairing rules. Trigger: when audit script needs programmatic SKOS-grade query (e.g., subsumption chain traversal beyond table-row matching). |
| ~~Verb category assignment~~ | **SUBSUMED 2026-05-16 by PP-021 Gates 0-4** | All 37 Active verbs now carry Category column (Common, Communications, Data, Diagnostic, Lifecycle, Governance, Evolution, Research). Coverage complete. |
| Synonym prohibition rules | **PARTIALLY SUBSUMED** (by §Hierarchy Decisions) | §Hierarchy Decisions table documents 11 collapse/subsumption decisions; this is the operational form of synonym prohibition. Formal closed-taxonomy prohibition list (PowerShell-style "always X never Y" rows) deferred to SKOS form (v3.19+). |

---

## Design Principles

1. **Transitive verbs only**: Every verb must be able to take a real object. No phrasal verbs that require a fixed particle.
2. **Domain innovation is acceptable**: When a standard verb (Get, Write, Save) loses meaningful semantic distinction, a domain-specific verb (study, record, capture) is justified — but must be explicitly documented.
3. **Pairing required for lifecycle verbs**: If a verb implies opening/starting something, its complement must exist (open/close, create/delete).
4. **Classify by what it IS**: Verb placement in categories follows the verb's primary semantics, not its current usage.
5. **PowerShell as primary reference**: When introducing new verbs, check PowerShell's approved list first. Diverge only with documented rationale.
6. **Hierarchy discipline (added 2026-04-18, session post-scope-lock)**: A candidate verb is canonical *only if no existing canonical verb subsumes it*. Specializations ride on flags first; they graduate to peer verbs only when flag behaviors diverge too much to coexist under one skill. Peer-verb proliferation fragments the vocabulary and hides category hierarchies.
7. **Flag-as-graduation-slot (added 2026-04-18)**: The flag name is the future skill name in waiting. Design flags so that if they eventually graduate, the skill name is already implied (`aget-check-release --requirements` → `aget-check-requirements`).
8. **Document-grounded flags (added 2026-04-18)**: Flag names should reference actual AGET artifact types (R-* requirements docs, V-tests, L-docs), not abstract evaluation dimensions. Artifact-grounded flags map cleanly to the Two-Level Model (L742).
9. **Canonical verb pipeline (added 2026-04-19)**: The typical workflow relationship is `check` (diagnostic, read-only) → `enhance` (therapeutic: growth + routine healing) *or* `deprecate` (retirement when healing is not appropriate). Check outputs feed enhance or deprecate actions; verbs should support this pipeline rather than fragmenting it. Corollary: `check` never mutates; `enhance` and `deprecate` mutate with evidence derived from check output (whether direct hand-off or logged backlog).

---

## Hierarchy Decisions (2026-04-18 session)

Three collapse decisions recorded during the collapsed-triad vocabulary session:

| Candidate verb | Genus (canonical) | Relationship | Rationale |
|----------------|-------------------|:------------:|-----------|
| `build` | `create` | `build ⊂ create` | Assembling existing parts is a specialization of creating. Adopting `create` preserves discipline; `build` may return as a flag (`--major`/`--minor`) if release specialization diverges. |
| `assess` | `check` | `assess ⊂ check` | Existing `check-*` skills already produce scored (`check-health`: 10/10), ordinal (`check-kb`: OK/WARN/CRITICAL), and stratified (`check-facts`) output. `assess` does not add a distinct capability — it is a specialization of `check` by output shape. |
| `audit` | `check` | `audit ⊂ check` | Formal-inspection connotation; subsumed by `check` with a `--requirements` flag. |
| `critique` | `check` | `critique ⊂ check` | Adversarial connotation; subsumed by `check` with a `--verifications` flag. Adversarial posture lives in the skill's instructions, not its verb. |
| `analyze` | `check` | `analyze ⊂ check` | **Added 2026-04-19.** Depth of inspection is a parameter of the diagnostic intent, not a separate verb. `check` default = lightweight tier/ratio pass-fail; `check --deep` = full analysis (what was `analyze-*`). Applied first to `/aget-analyze-ontology` → `/aget-check-ontology --deep`. Deployed `analyze-*` skills retire under POL-DEP-001 grace. |
| `enhance` | `fix` | `enhance ⊂ fix` | **Added 2026-04-19; direction corrected from initial commit.** Growth is a species of fix — fixing what's missing. Parallel to `analyze ⊂ check` on the diagnostic side. Conceptual hierarchy: `fix` is the parent (remediate gap between current and target state); `enhance` is the grow-species (add capability); healing-species (e.g., repair-mode) is the other flavor. **Deployment note**: both verbs remain peers at deployment level. `/aget-enhance-*` is deployed (fleet-convergence justified, L436); `/aget-fix-*` remains reserved for artifacts where correction is the primary intent (e.g., `/aget-fix-spec`, `/aget-fix-template`). Canonical pairing pattern: `enhance` pairs with rubric/ontology-like artifacts (measurement growth); `fix` pairs with spec/contract-like artifacts (contract correction). |
| `document` | `record` | `document ⊂ record` | **Decision recorded 2026-05-16; deployment deferred to v3.19.** Documentary intent is a parameter of recording action, not a separate verb. `record` default = generic persistence to log/journal/observation-queue; `record --canonical` = formal documentary entry to canonical surface (registry, table, spec) treated as reference by downstream consumers (what was `document-*`). Selection heuristic: ask whether the target surface is documentary (use `--canonical`) or routine log/memory (no flag). Parallel to `analyze ⊂ check` on the Evolution side; `--deep` is the wrong flag because the distinction is target-surface character + consumer treatment, not depth. **Deployment plan**: v3.19 INIT-SKILL-MATURATION Stream 4 migrates `document-*` → `record-* --canonical`; old names route to POL-DEP-001 grace alias. **Mid-cycle stability**: v3.18 T2.42 ships as `/aget-document-migration` (commitment intact per L853); migration applied post-release. Affected skills: `/aget-document-finding`, `/aget-document-migration` (T2.42 if lands v3.18). |
| `scan` | `study` | `scan ⊂ study` | **Added 2026-05-16 at PP-021 Gate 2 G2.5.** Subsumption decision: `scan` (rapid surface-level pass to identify candidates) is a specialization of `study` (active investigation per Domain Innovation row). `study --shallow` or `study --candidates-only` captures the scan semantic without a peer verb. Affected skill: `/aget-scan-fleet-cli-ideas` — **deprecated** under POL-DEP-001 grace v3.18 → v3.20; replacement: `/aget-study-fleet-cli-ideas --candidates` (deployment in v3.19 INIT-SKILL-MATURATION Stream 4). Rationale: peer-verb proliferation in the Research family is what Hierarchy Discipline (Principle #6) prevents; depth-of-investigation is a parameter, not a separate verb. |
| `update` | `enhance` | `update ⊂ enhance` (canonical-direction regression) | **Added 2026-05-16 at PP-021 Gate 2 G2.6.** Per Design Principle #9 (Canonical Verb Pipeline, 2026-04-19), `enhance` is the canonical therapeutic verb (`check → enhance` or `check → deprecate`). `update` connotes mechanical mutation without governing process; fleet-convergence (L436) selected `enhance` for governed lifecycle work. Affected skill: `/aget-update-backlog-research` — **deprecated** under POL-DEP-001 grace v3.18 → v3.20; replacement options: (a) rename to `/aget-enhance-backlog-research` (preserves scope; minimal migration cost) OR (b) collapse into `/aget-enhance-backlog --research-source` (verb-flag pattern; preferred per Principle #7 Flag-as-Graduation-Slot). Decision: option (b) at v3.19 INIT-SKILL-MATURATION Stream 4. Rationale: every appearance of `update-*` in skill names is a regression away from `enhance` canonicality. |
| `verify` | `validate` | **Peer** (boundary, not subsumption) | **Added 2026-05-16 at PP-021 Gate 3 G3.1; cites audit Pair 8 (`docs/AUDIT_near_synonym_verb_pairs_2026-05-02.md` line 156).** Closes INIT-FRAMEWORK-COHERENCE Stream 2 verify/validate named target. Semantic distinction: `validate` = **artifact-conformance check** (does this artifact conform to its spec/schema/structural rules?) — already deployed as `/aget-validate-spec` (Active row 28); `verify` = **behavioral-assertion check** (does this assertion hold true under execution/test?) — V-test execution semantic. Pair: when authoring a V-test, you `verify` an assertion; when authoring a structural check, you `validate` an artifact. **Status**: `verify` not yet deployed as a `/aget-verify-*` skill; addition to Active inventory deferred until first deployment (per minimum-viable-graduation; preempts drift on future verify-* skills). |
| `research` | `study` | **Peer** (boundary; Option A) | **Added 2026-05-16 at PP-021 Gate 3 G3.2; cites `docs/DESIGN_DIRECTION_skill_verb_vocabulary_study_research_boundary_DRAFT.md` (2026-05-02).** Both verbs survive as peers per Option A of the boundary draft. Semantic distinction: `study` (Domain Innovation row) = **active investigation across loosely-coupled sources** (KB cross-section, multi-artifact synthesis) — already deployed as `/aget-study-topic`; `research` would be **investigation within a canonical corpus** (single named source/ontology/registry). Resolution mechanism: extend `study` with `--source` flag rather than peer-verb proliferation per Principle #6 Hierarchy Discipline + Principle #7 Flag-as-Graduation-Slot — `/aget-study-topic --source <corpus>` covers canonical-corpus investigation. `research` peer-verb addition deferred until flag-behaviors-diverge condition triggers (per Principle #6). **Status**: registry retains `study` as canonical Research verb; `research` not added as Active row (flag-mediated). |

### Collapsed Release Triad (SP-019, SP-020)

The Release Delivery Triad (L818) originally used three peer verbs: `build`, `audit`, `critique`. Per the hierarchy discipline above, this was normalized to one verb for evaluation and one verb for construction:

| Triad Role | Skill | Flag | Reference Document |
|------------|-------|:----:|--------------------|
| Builder | `aget-create-release` | — | Active PROJECT_PLAN gate deliverables |
| Spec Auditor | `aget-check-release` | `--requirements` | R-REL-*, R-ISSUE-*, R-REQ-* |
| Critic | `aget-check-release` | `--verifications` | V-tests in specs + plans |

Predecessor skills (`aget-release-build`, `aget-release-audit-specs`, `aget-release-critique`) deprecated with grace v3.14 → v3.16 per POL-DEP-001.

### L854 Origin

These decisions were made during a session in which the collapsed-triad skills were created without going through `/aget-propose-skill` first — a **Spec-First Selective Application** failure documented in L854. Retroactive governance (Option C) produced SP-019/020, SKILL-046/047, and this DESIGN_DIRECTION amendment. The incident exposed a D71 STRUCTURAL gap (`/aget-propose-skill` is Advisory, not Strict) — systemic enhancement filed separately.

---

## Traceability

| Link | Reference |
|------|-----------|
| Naming pattern spec | SKILL-012 CS-002, SKILL-009 PS-002 |
| Skills INDEX | `aget/.aget/specs/skills/INDEX.md` v1.2.0 |
| Skills SPEC | `aget/specs/archive/AGET_SKILLS_SPEC.md` v1.1.0 |
| Skill vocabulary | `.aget/specs/skills/SKILL_VOCABULARY.md` v1.1.0 |
| Ontology directory | `ontology/README.md` |
| PowerShell taxonomy | [Approved Verbs](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands) |
| Schema.org Actions | [schema.org/Action](https://schema.org/Action) |
| W3C ActivityStreams | [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/) |
| Session: origin | session_2026-02-23 |

---

*DESIGN_DIRECTION_skill_verb_vocabulary.md*
*Artifact type: Design Direction (researched + directional, not yet gated)*
*Lives in ontology/ per principle: classify by what it IS (vocabulary knowledge), not what it DOES (roadmap)*
