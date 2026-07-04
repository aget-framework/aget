# AGET_ENTITY_DIMENSION_SPEC

**Status**: DRAFT v0.1.0 (canonical placement 2026-07-04; graduated from private draft after two independent Gate-5 Critic passes — see Provenance)
**Version**: 0.1.0
**Canonical-Location**: `specs/AGET_ENTITY_DIMENSION_SPEC.md` (placed 2026-07-04, Saturday window)
**Governing-Spec-Candidate-Of**: AGET_VOCABULARY_SPEC Part 6 (Core Domain Entities) — absorption target, Stream 5
**Binds-Against**: `ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml` (ontology yaml `version: 1.0.0`; 871 concepts; reconciled 2026-06-28)
**Initiative**: INIT-ONTOLOGY-SPEC-BINDING (Stream 1 of 5)
**Substrate**: FWRK-2026-012 (C535–C547) + binding cluster C641/C644
**References**: L924 (binding gap), L459 (core entity vocabulary), L671 (classification-without-consequence), L795 (governed discourse grounding), L922 (recursive-coverage), L742 (two-level model)

> **URI form (corrected 2026-07-03 after independent Gate-5 Critic pass)**: the ontology's canonical URI is **name-based** — `aget:concept/<PrefLabelCamelCase>` (e.g. `aget:concept/EntityDefinitionDimension`), NOT the id-based form `aget:concept/<Cnnn>` (a `C` + digits). The `<Cnnn>` id is the ontology's internal `id:` field, cited here in parentheses as a stable cross-reference only. All bindings below use the name-based URI, matching the existing generator `scripts/ground_artifact.py`.

> **Self-demonstration**: This spec uses the binding pattern it specifies. Every normative domain noun phrase below **SHALL be interpreted in terms of aget:concept/NormativeConceptBinding** (C641) — the pattern is reused, not coined (the binding cluster C641/C644 was pre-grounded by prior ontology expansion); mention-without-binding is the counter-form `aget:concept/SpecificationToOntologyBinding` (C644).

---

## Abstract

Author the first AGET specification that **normatively binds vocabulary by URI** — defining the binding pattern (`<normative noun phrase> SHALL be interpreted in terms of aget:concept/<Name>`) and demonstrating it in its own text. The spec specifies the seven `aget:concept/EntityCharacterizationDimension` (C535) axes along which any `aget:concept/Entity` (C293) MAY be characterized, the per-dimension coverage requirements, and the grading `aget:concept/DimensionalFormalizationMaturity` (C543). It is the reusable template INIT-ONTOLOGY-SPEC-BINDING Streams 2–5 inherit.

---

## Problem Statement

L924 established (2026-05-04) that AGET's SKOS ontology is structurally disconnected from the spec/requirements/governance contract layer: canonical specs carried **0** inline `aget:concept/` URI references. Mention is not binding (`aget:concept/SpecificationToOntologyBinding`, C644) — without inline normative reference the ontology is decorative metadata (`aget:concept/AuthorAssertedCleanlinessAntiPattern`-adjacent classification-without-consequence, L671). This spec closes that gap for the entity-characterization vocabulary and provides the portable pattern. *(Full L924 empirical table lives in the governing PROJECT_PLAN, not duplicated here.)*

---

## Scope

### In Scope (v0.1)
1. The 7 `aget:concept/EntityCharacterizationDimension` (C535) classes: Definition (C536), Interrelationship (C537), Action (C538), Lifecycle (C539), Persistence (C540), Governance (C541), Provenance (C542).
2. The normative binding pattern definition (reuses `aget:concept/NormativeConceptBinding`, C641).
3. Per-dimension coverage requirements + a definition of "fully characterized."
4. Dimensional Formalization Maturity grading (`aget:concept/DimensionalFormalizationMaturity`, C543; 5-level).
5. Conformance rules for new-entity-type proposers.
6. V-tests per capability (the conformance contract Stream 3's validator consumes).

### Out of Scope (deferred)
- Validator implementation (`validate_spec_binding.py`) — Stream 3.
- Audit/remediate existing canonical specs — Stream 4.
- AGET_VOCABULARY_SPEC Part 6 absorption — Stream 5.
- Cross-vocabulary binding (single-vocabulary spec).

---

## Concepts Overview  *(first-instance demonstration of the binding pattern)*

| # | Dimension | URI binding | Characterizes |
|---|-----------|-------------|---------------|
| 1 | Definition | `aget:concept/EntityDefinitionDimension` (C536) | What the entity *is* — identity, essential attributes |
| 2 | Interrelationship | `aget:concept/EntityInterrelationshipDimension` (C537) | How it relates to other entities |
| 3 | Action | `aget:concept/EntityActionDimension` (C538) | Operations acting on / performed by it (SVO, L817/L912) |
| 4 | Lifecycle | `aget:concept/EntityLifecycleDimension` (C539) | Its state-transition model |
| 5 | Persistence | `aget:concept/EntityPersistenceDimension` (C540) | Continuant vs occurrent endurance |
| 6 | Governance | `aget:concept/EntityGovernanceDimension` (C541) | What authority/policy constrains it |
| 7 | Provenance | `aget:concept/EntityProvenanceDimension` (C542) | Its origin, authorship, derivation |

Meta-concepts: parent axis `aget:concept/EntityCharacterizationDimension` (C535); root `aget:concept/Entity` (C293); grading `aget:concept/DimensionalFormalizationMaturity` (C543); anti-pattern `aget:concept/MetaSpecificationGap` (C544); discipline `aget:concept/VocabularyFirstNamingDiscipline` (C547); pattern `aget:concept/NormativeConceptBinding` (C641); counter-form `aget:concept/SpecificationToOntologyBinding` (C644).

---

## Capabilities (CAP-ENTDIM-001..010)  *— Gate 2*

### CAP-ENTDIM-001 — Normative Binding Pattern
Defines the inline form `<normative noun phrase> SHALL be interpreted in terms of aget:concept/<Name>`, reusing `aget:concept/NormativeConceptBinding` (C641); the mention-≠-binding counter-form is `aget:concept/SpecificationToOntologyBinding` (C644). Parent axis: `aget:concept/EntityCharacterizationDimension` (C535).

### CAP-ENTDIM-002 — Definition Dimension
Characterizes what `aget:concept/Entity` (C293) *is* via `aget:concept/EntityDefinitionDimension` (C536).

### CAP-ENTDIM-003 — Interrelationship Dimension
Characterizes inter-entity relations via `aget:concept/EntityInterrelationshipDimension` (C537).

### CAP-ENTDIM-004 — Action Dimension
Characterizes operations via `aget:concept/EntityActionDimension` (C538) (SVO grounding, L817/L912).

### CAP-ENTDIM-005 — Lifecycle Dimension
Characterizes state transitions via `aget:concept/EntityLifecycleDimension` (C539).

### CAP-ENTDIM-006 — Persistence Dimension
Characterizes endurance via `aget:concept/EntityPersistenceDimension` (C540).

### CAP-ENTDIM-007 — Governance Dimension
Characterizes constraining authority via `aget:concept/EntityGovernanceDimension` (C541).

### CAP-ENTDIM-008 — Provenance Dimension
Characterizes origin/derivation via `aget:concept/EntityProvenanceDimension` (C542).

### CAP-ENTDIM-009 — Multi-Dimensional Coverage
Defines "fully characterized" and grades coverage via `aget:concept/DimensionalFormalizationMaturity` (C543); the anti-pattern is `aget:concept/MetaSpecificationGap` (C544).

### CAP-ENTDIM-010 — Vocabulary-First Authoring
Requires reuse of an existing prefLabel before coinage, per `aget:concept/VocabularyFirstNamingDiscipline` (C547).

## Requirements (R-ENTDIM-001..016)  *— Gate 3*

- R-ENTDIM-001: Every normative noun phrase referencing a domain entity `aget:concept/Entity` (C293) **SHALL** bind to its prefLabel via a name-based `aget:concept/<Name>` URI. *(CAP-ENTDIM-001)*
- R-ENTDIM-002: At least one binding **SHALL** be written in the full sentence form `<noun phrase> SHALL be interpreted in terms of aget:concept/<Name>` per `aget:concept/NormativeConceptBinding` (C641); subsequent references to an already-bound concept **MAY** use the URI short form `aget:concept/<Name>` (R-001). *(CAP-ENTDIM-001)* *(Existential, not universal: a bare URI reference is a valid binding per R-001 and V-002 checks presence, not that every reference is a full sentence.)*
- R-ENTDIM-003: A spec introducing an entity-type **SHALL** characterize it on `aget:concept/EntityDefinitionDimension` (C536). *(CAP-ENTDIM-002)*
- R-ENTDIM-004: Such a spec **SHOULD** characterize the entity on `aget:concept/EntityInterrelationshipDimension` (C537) (baseline-conformance level; see R-011). *(CAP-ENTDIM-003)*
- R-ENTDIM-005: Such a spec **SHALL** characterize the entity on `aget:concept/EntityActionDimension` (C538) when any operation acts on it. *(CAP-ENTDIM-004)*
- R-ENTDIM-006: Such a spec **SHALL** characterize the entity on `aget:concept/EntityLifecycleDimension` (C539) when the entity has states. *(CAP-ENTDIM-005)*
- R-ENTDIM-007: Such a spec **SHALL** declare `aget:concept/EntityPersistenceDimension` (C540) (continuant vs occurrent). *(CAP-ENTDIM-006)*
- R-ENTDIM-008: Such a spec **SHALL** declare the `aget:concept/EntityGovernanceDimension` (C541) constraining the entity. *(CAP-ENTDIM-007)*
- R-ENTDIM-009: Such a spec **SHOULD** record `aget:concept/EntityProvenanceDimension` (C542) (baseline-conformance level; see R-011). *(CAP-ENTDIM-008)*
- R-ENTDIM-010: A spec **SHALL** declare per-dimension coverage status via `aget:concept/DimensionalFormalizationMaturity` (C543). *(CAP-ENTDIM-009)*
- R-ENTDIM-011: **Two-tier bar.** *Baseline conformance* requires satisfying the SHALL dimensions (R-003/005/006/007/008 as their conditions apply) plus the R-010 coverage declaration. *"Fully characterized"* is a distinct, **aspirational** grade requiring ≥ maturity level 3 on **all 7** dimensions (including the R-004/R-009 SHOULD dimensions). A spec MAY be baseline-conformant without being fully characterized; the two are not the same bar. *(CAP-ENTDIM-009)*
- R-ENTDIM-012: A spec introducing an entity-type **SHALL NOT** exhibit `aget:concept/MetaSpecificationGap` (C544) — strong coverage on some dimensions and silence on others **without** an explicit R-010 coverage declaration naming the silent dimensions. *(CAP-ENTDIM-009)*
- R-ENTDIM-013: Before coining a new entity noun phrase, an author **SHALL** check existing prefLabels per `aget:concept/VocabularyFirstNamingDiscipline` (C547). *(CAP-ENTDIM-010)*
- R-ENTDIM-014: Each `aget:concept/<Name>` URI reference **SHALL** resolve to a `uri:` present in the declared ontology version. *(CAP-ENTDIM-001)*
- R-ENTDIM-015: Mention of a concept by word without an inline URI binding **SHALL NOT** count as binding (`aget:concept/SpecificationToOntologyBinding`, C644). *(CAP-ENTDIM-001)*
- R-ENTDIM-016: The spec **SHALL** declare the ontology name + version it binds against (see front-matter `Binds-Against`). *(CAP-ENTDIM-001)*

**Modal-leveling rationale** (addresses the SHALL/SHOULD asymmetry): Definition/Action/Lifecycle/Persistence/Governance are SHALL because an entity that omits them is under-specified for *conformance* (identity, behavior, state, endurance-class, and constraining authority are load-bearing for interpretation). Interrelationship and Provenance are SHOULD at baseline because they are frequently derivable or genuinely N/A for leaf entities — but both are required for the *fully-characterized* grade (R-011).

## Verification (V-ENTDIM-001..016)  *— Gate 4*  *(binding-layer conformance contract Stream 3's validator consumes)*

> **Scope honesty**: V-003..V-010, V-012, V-013, V-015 are **binding-PRESENCE** checks (is the dimension's URI referenced?), not **coverage-DEPTH** checks (is the entity substantively characterized on that dimension?). Depth is a Stream-3 validator + qualitative-reviewer concern, deliberately NOT asserted mechanically here. This is a binding-layer contract.

- V-ENTDIM-001: Reviewer confirms every normative domain noun phrase carries an `aget:concept/<Name>` binding. *(R-001, qualitative — the "normative noun phrase" set needs human judgment)*
- V-ENTDIM-002: `grep -qE 'SHALL be interpreted in terms of aget:concept/[A-Za-z]' <spec>` → present. *(R-002, executable)*
- V-ENTDIM-003: `grep -q 'aget:concept/EntityDefinitionDimension' <spec>` → bound. *(R-003, executable presence)*
- V-ENTDIM-004: `grep -q 'aget:concept/EntityInterrelationshipDimension' <spec>` → bound (SHOULD; warn-only). *(R-004, executable presence)*
- V-ENTDIM-005: `grep -q 'aget:concept/EntityActionDimension' <spec>` → bound. *(R-005, executable presence)*
- V-ENTDIM-006: `grep -q 'aget:concept/EntityLifecycleDimension' <spec>` → bound. *(R-006, executable presence)*
- V-ENTDIM-007: `grep -q 'aget:concept/EntityPersistenceDimension' <spec>` → bound. *(R-007, executable presence)*
- V-ENTDIM-008: `grep -q 'aget:concept/EntityGovernanceDimension' <spec>` → bound. *(R-008, executable presence)*
- V-ENTDIM-009: `grep -q 'aget:concept/EntityProvenanceDimension' <spec>` → bound (SHOULD; warn-only). *(R-009, executable presence)*
- V-ENTDIM-010: `grep -q 'aget:concept/DimensionalFormalizationMaturity' <spec>` → maturity declaration present. *(R-010, executable presence)*
- V-ENTDIM-011: Reviewer confirms the two-tier bar (baseline vs fully-characterized) is stated and internally consistent. *(R-011, qualitative)*
- V-ENTDIM-012: `grep -q 'aget:concept/MetaSpecificationGap' <spec>` → anti-pattern named. *(R-012, executable presence)*
- V-ENTDIM-013: `grep -q 'aget:concept/VocabularyFirstNamingDiscipline' <spec>` → discipline cited. *(R-013, executable presence)*
- V-ENTDIM-014: `for n in $(grep -oE 'aget:concept/[A-Za-z][A-Za-z]+' <spec> | sort -u); do grep -qxF "    uri: $n" <ontology> || echo "UNRESOLVED $n"; done` → empty. *(R-014, executable — tests URI resolution, not id existence)*
- V-ENTDIM-015: `grep -q 'aget:concept/SpecificationToOntologyBinding' <spec>` → mention≠binding counter-form present. *(R-015, executable presence)*
- V-ENTDIM-016: `grep -qE 'Binds-Against.*ONTOLOGY_personal_ai_systems.*version.*1\.0' <spec>` → ontology name **and** version both declared (the `version` clause is verified, not just the filename). *(R-016, executable)*

*(16 V-tests: 12 executable, 2 qualitative-by-nature (V-001/V-011), 2 executable presence flagged warn-only. "Executable" here means mechanically runnable; per the scope-honesty note above, the presence checks verify binding, not coverage depth.)*

---

## Self-Conformance Statement  *(L922 — the spec's own contract, audited at Gate 5)*

This spec SHALL pass its own R-ENTDIM-001/002/014/016: every normative domain noun phrase above is bound inline via a name-based `aget:concept/<Name>` URI that resolves in the declared ontology (R-014); ≥1 binding is written in the R-002 mandated sentence form (see the self-demonstration front-matter note); the ontology version is declared (R-016, front-matter).

**R-010 self-application — per-dimension maturity of this spec's own subject** (grades on `aget:concept/DimensionalFormalizationMaturity` C543: L1 convention-only · L2 documented · L3 specified-with-CAP/R · L4 test-validated · L5 full stack). The subject entity graded is the entity-characterization framework this spec introduces:

| Dimension | URI | Maturity | Basis |
|-----------|-----|:--------:|-------|
| Definition | `aget:concept/EntityDefinitionDimension` (C536) | **L4** | CAP-002 + R-003 + V-003; each dimension carries an ontology prefLabel+definition |
| Interrelationship | `aget:concept/EntityInterrelationshipDimension` (C537) | **L3** | CAP-003 + R-004; Concepts Overview declares parent axis (C535) + root (C293) relations |
| Action | `aget:concept/EntityActionDimension` (C538) | **L2** | CAP-004 + R-005 cite SVO discipline but operations on the dimensions are not enumerated |
| Lifecycle | `aget:concept/EntityLifecycleDimension` (C539) | **L1** | CAP-005 + R-006 present, but no state-transition model given for the dimension entities |
| Persistence | `aget:concept/EntityPersistenceDimension` (C540) | **L1** | CAP-006 + R-007 present, but continuant/occurrent class not declared for the dimensions |
| Governance | `aget:concept/EntityGovernanceDimension` (C541) | **L2** | CAP-007 + R-008; governed by INIT-ONTOLOGY-SPEC-BINDING + the PROJECT_PLAN |
| Provenance | `aget:concept/EntityProvenanceDimension` (C542) | **L3** | CAP-008 + R-009; substrate (FWRK-2026-012, C535–C547) + C-ids declared in front-matter |

**Honest coverage note (R-012 self-application)**: this v0.1's coverage is lopsided — strong on `aget:concept/EntityDefinitionDimension` (C536), weak (L1) on `aget:concept/EntityLifecycleDimension` (C539) and `aget:concept/EntityPersistenceDimension` (C540). Per R-012 this incompleteness is **explicitly declared** (the table above IS the R-010 declaration), which is what keeps the spec out of the `aget:concept/MetaSpecificationGap` (C544) it forbids: the gap is silent under-coverage, not declared under-coverage. Raising the L1 rows is deferred to v0.2. Gate 5 re-audits the completed text; residual failures are BLOCKING (L922).

---

*AGET_ENTITY_DIMENSION_SPEC v0.1.0 DRAFT — "The spec demonstrates the pattern it advocates."*
*Authored 2026-07-03 (Gates 1–4). Binding token + V-test semantics corrected after a first independent Gate-5 Critic pass; R-002 wording, V-016 verifier, and R-010 self-application table corrected after a second independent Gate-5 Critic re-review. Gate-5 sign-off (handoff brief + Critic L-doc) + canonical placement remaining.*
