# Requirement Quality Scoring Rubric

**Version**: 1.0
**Created**: 2026-04-19
**Author**: private-aget-framework-AGET
**Domain**: Quality of individual REQ-* artifacts in `aget/requirements/` against REQUIREMENTS_FORMAT.md v1.0
**Archetype**: Compliance (gate-before-pass — does this REQ meet the format contract?)
**Assessor**: Hybrid (agent scores schema/traceability mechanically; human verifies `fit_criterion:` truthfulness)
**Status**: Active
**Closes Gap**: L749 Requirements-Rubric Duality (the missing rubric counterpart for REQ-* artifacts)

---

## Purpose

Score the quality of individual REQ-* artifacts against the REQUIREMENTS_FORMAT.md v1.0 contract. Supports decisions about:

- **Publication readiness**: is this REQ mature enough to publish to `aget/requirements/`?
- **Verification prioritization**: which REQ-CORE PENDING items (#1063) are also rubric-weak?
- **Inheritance soundness**: does a domain REQ (REQ-GOV-*, REQ-HOM-*) properly inherit from REQ-CORE-*?
- **Decorative-requirement detection** (L671 / C291): which published REQs lack downstream consequence?

Closes the structural gap named in L749 — the symmetric counterpart of `RUBRIC_specification_maturity_v1.0.md` at the requirement layer.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Individual REQ-* artifact quality (per-requirement scoring) | REQ-* domain content correctness (e.g., is this the *right* requirement?) |
| Forward traceability completeness (REQ → CAP/R-*) | CAP-* / V-test quality (covered by RUBRIC_specification_maturity_v1.0 / RUBRIC_verification_test_quality — proposed) |
| Schema conformance to REQUIREMENTS_FORMAT.md | Cross-REQ consistency (covered by domain-level reviews) |
| Fit criterion verifiability at the human level | Stakeholder consensus quality |
| Evidence grounding (L700 bottom-up provenance) | Implementation correctness |

## Theoretical Basis

| Framework | Application |
|-----------|-------------|
| **L742** (Two-Level Model) | This rubric scores the *human level* (REQ-*); RUBRIC_specification_maturity_v1.0 scores the *contract level* (CAP-*) |
| **L749** (Requirements-Rubric Duality) | "A requirement without a rubric assessment path = decorative requirement" — this rubric IS that path |
| **L700** (Evidence-Driven Requirements) | D3 Backward Traceability operationalizes the bottom-up provenance mandate |
| **L671** (Classification Without Consequence) | Critical Requirement CR1 detects decorative REQs (specifications: empty) |
| **C298** (Software System Requirement, ISO/IEC/IEEE 29148:2018) | Ontology grounding — REQ-* artifacts are instances of this concept |
| **C291** (Decorative Requirement) | The L0 anti-pattern this rubric defends against |
| **C302** (Requirements Volatility, Lehman 1980) | Counter-perspective informing D3 evidence-currency check |
| **Volere Snow Card** (Robertson & Robertson 2012) | Fit Criterion as the bridge — D4 anchor |
| **EARS** (Mavin RE'09) | NOT used directly here — EARS belongs at CAP-* level (per Mavin: NFRs are not EARS-suitable) |
| **Dawson 2017** (rubric design 14 elements) | Behavioral anchoring (Section 5); observable criteria |
| **L689** (rubric-as-adversary, VP-of-AI) | Adversarial test: would a plausibly defective REQ pass each L2/L3 descriptor? Applied dimension-by-dimension. |

---

## Rubric Archetype Selection

**This rubric uses**: **Compliance** (gate-before-pass)

A REQ-* artifact either meets the REQUIREMENTS_FORMAT.md contract or it does not. Eligibility gates check structural prerequisites (presence of mandatory fields); dimension scoring then assesses depth of conformance. Failure of CR1 (forward traceability) regresses to L0 regardless of other scores.

---

## Domain Adaptation

**This rubric uses**: **Maturity** label set (Initial / Developing / Defined / Optimizing) — mirrors RUBRIC_specification_maturity_v1.0 for assessor consistency

| Level | Score | Maturity Label | Plain meaning |
|-------|------|---------------|---------------|
| L3 | 3 | Optimizing | Reference-quality REQ — used as exemplar by other domains |
| L2 | 2 | Defined | Production-ready REQ — meets all 11 schema fields + traceability |
| L1 | 1 | Developing | Draft-grade REQ — schema present but traceability incomplete |
| L0 | 0 | Initial | Decorative or unverifiable REQ — fails CR or eligibility |

**Construction method** (Mertler 2001): L3 + L0 anchored first, L1/L2 interpolated.

---

## Eligibility Gates

Binary prerequisites evaluated BEFORE dimension scoring. Any gate failure = ineligible (do not score).

| Gate ID | Requirement | Pass test |
|---------|-------------|-----------|
| EG-1 | File exists at `aget/requirements/REQ-{DOMAIN}_*.md` | `ls aget/requirements/REQ-*.md` lists the file |
| EG-2 | Contains a YAML+Markdown REQ block with `id:` matching `REQ-{DOMAIN}-{F\|Q}-{NNN}` | regex match on the id field |
| EG-3 | `status:` field present and one of {draft, proposed, validated, published} | enum check |

REQ at `status: draft` MAY be scored but expected to score L1 (Developing). Score L2/L3 only meaningful at `status: proposed` and above.

---

## Dimension Classification

All four dimensions are **Quality** dimensions (per-output observation). Maturity is captured as an eligibility gate (status:) and as a Critical Requirement, not as a separate scored dimension.

| Dimension | Classification | Why |
|-----------|----------------|-----|
| D1 Schema Completeness | Quality | Per-REQ observation — count of populated fields |
| D2 Forward Traceability | Quality | Per-REQ observation — REQ→CAP edge presence |
| D3 Backward Traceability | Quality | Per-REQ observation — evidence: field grounding |
| D4 Fit Criterion Verifiability | Quality | Per-REQ observation — Volere bridge testability |

---

## Behavioral Anchoring

Per L689 adversarial test, every L2/L3 descriptor below was checked against: *"Would a plausibly decorative REQ (C291 instance) pass this descriptor?"* — if yes, the descriptor was tightened.

---

## Dimensions

### D1: Schema Completeness

**Weight**: 35%
**Definition**: All 11 mandatory REQUIREMENTS_FORMAT.md fields present and non-empty.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D1.1 | All 11 mandatory fields present (id, title, type, description, rationale, evidence, fit_criterion, priority, specifications, status, originator) — note `category:` is mandatory only for `type: quality` | 50% | Yes |
| D1.2 | Description is implementation-free stakeholder language (no file paths, tool names, design hints) | 25% | No |
| D1.3 | Rationale connects to mission/goals (cites MISSION.md, identity.json, or principal directive) | 25% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | All 11 fields present + populated; description is stakeholder-pure with zero implementation language; rationale traces to a specific governance artifact (e.g., "MISSION.md §2", "L335 Memory Architecture") |
| **L2: Defined** | 2 | All 11 fields present + populated; description has minor implementation hints (≤1 file/tool reference); rationale connects to mission generally |
| **L1: Developing** | 1 | 8-10 of 11 fields present + populated; description leaks implementation; rationale is generic |
| **L0: Initial** | 0 | <8 fields populated; OR description is implementation-only (e.g., "use scripts/wake_up.py"); OR no rationale |

---

### D2: Forward Traceability (REQ-CORE-F-001 enforcement)

**Weight**: 30%
**Definition**: The `specifications:` field contains identifiers of contract artifacts (CAP-*, R-*, SKILL-*, or RUBRIC_*) that exist and reference this REQ in turn (or are slated to do so). Per REQUIREMENTS_FORMAT v1.1: ADRs, L-docs, governance docs, SOPs, and meta-docs do NOT belong in `specifications:` (they belong in `evidence:` or `constraints:`).

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D2.1 | `specifications:` field is non-empty | 35% | **Yes (CR1)** |
| D2.2 | All cited entries match acceptable types: CAP-*, R-*, SKILL-*, or RUBRIC_* | 25% | **Yes (CR4 — added v1.1)** |
| D2.3 | At least one cited contract exists as a real artifact (`aget/specs/` file, skill spec, or `rubrics/` file) | 25% | No |
| D2.4 | Cited contract reciprocally references the REQ ID (bidirectional link) | 15% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | All cited contracts are correct type AND exist AND each reciprocally cites this REQ; bidirectional traceability complete |
| **L2: Defined** | 2 | All cited contracts are correct type AND exist; reciprocal citation exists for at least one |
| **L1: Developing** | 1 | `specifications:` non-empty AND all entries are correct type, but at least one contract doesn't exist OR none reciprocally cite back |
| **L0: Initial** | 0 | `specifications:` is empty (CR1 fail) OR contains entries of wrong type (CR4 fail — e.g., L-doc, ADR, SOP-Phase, governance doc) OR placeholder text like "TBD" |

---

### D3: Backward Traceability (L700 evidence grounding)

**Weight**: 15%
**Definition**: The `evidence:` field cites L-docs, operational data, or principal directive — supporting the bottom-up evidence-driven model.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D3.1 | `evidence:` is non-empty | 40% | No |
| D3.2 | Cited evidence is reachable (L-doc exists; ADR cited; principal directive timestamped) | 30% | No |
| D3.3 | `originator:` is one of {principal, operational-evidence, community} — not empty, not "agent-authored" | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | 3+ pieces of evidence cited; all reachable; originator is `principal` or `operational-evidence`; at least one citation is to a recent (<6 months) operational instance |
| **L2: Defined** | 2 | 2+ pieces of evidence cited; majority reachable; originator declared |
| **L1: Developing** | 1 | 1 piece of evidence cited OR multiple but only one reachable; originator may be missing |
| **L0: Initial** | 0 | No evidence cited; OR all citations are unreachable; OR REQ originated speculatively (no operational basis, no principal directive) |

---

### D4: Fit Criterion Verifiability (Volere bridge)

**Weight**: 20%
**Definition**: The `fit_criterion:` field describes a testable, measurable condition that determines requirement satisfaction *without* needing to read the downstream specification.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D4.1 | `fit_criterion:` is non-empty | 30% | No |
| D4.2 | Fit criterion names an observable outcome (count, time, presence, ratio) — not an aspiration | 40% | No |
| D4.3 | Fit criterion is verifiable at human level — no need to read EARS spec | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | Fit criterion is quantitative (specific number/threshold), bounded (time or scope), and reproducible (any qualified human can apply it) |
| **L2: Defined** | 2 | Fit criterion names observable outcome but lacks one of {quantitative bound, time bound, reproducibility} |
| **L1: Developing** | 1 | Fit criterion present but vague ("works well", "is fast enough") OR only verifiable by reading the spec |
| **L0: Initial** | 0 | No fit criterion; OR fit criterion is a tautology ("requirement is satisfied when satisfied") |

---

## Critical Requirements (automatic L0 regardless of dimension scores)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| **CR1** | `specifications:` field is non-empty (D2.1) | REQ-CORE-F-001 forward traceability mandate. A REQ without spec linkage is structurally decorative (C291). |
| **CR2** | `evidence:` field is non-empty for any REQ at `status: validated` or `status: published` | L700 violation. A validated REQ without evidence is unfounded. |
| **CR3** | `description:` is not implementation-only (no REQ where description is solely a tool/file reference) | Two-Level Model L742 violation — description must be at human level. |
| **CR4** | All `specifications:` entries match acceptable types: CAP-*, R-*, SKILL-*, RUBRIC_* (added v1.1) | Category coherence per REQUIREMENTS_FORMAT v1.1. L-docs/ADRs/SOPs/META-DOCs in `specifications:` are category errors (per L749 duality, only contracts qualify). |

If any CR fails on a non-draft REQ, the REQ scores L0 regardless of other dimensions.

---

## Scoring Method

**Method**: GatewayFirst (Critical Requirements check first, then weighted average)

### Calculation

```
1. Eligibility gates (EG-1, EG-2, EG-3) — fail = NOT ASSESSED
2. Critical Requirements (CR1, CR2, CR3) — fail = L0 regardless of other scores
3. Score each dimension D1-D4 (0-3) using performance levels
4. Weighted composite = (D1 × 0.35) + (D2 × 0.30) + (D3 × 0.15) + (D4 × 0.20)
5. Map composite to overall level
```

### Score to Level Mapping

| Composite Score | Overall Level | Maturity Label |
|-----------------|---------------|----------------|
| 2.50 - 3.00 | L3 | Optimizing |
| 1.50 - 2.49 | L2 | Defined |
| 0.50 - 1.49 | L1 | Developing |
| 0.00 - 0.49 | L0 | Initial |

---

## Evidence Requirements

| Dimension | Required Evidence (observable from REQ-* file alone) |
|-----------|------------------------------------------------------|
| D1 | YAML field count; description text linguistic check |
| D2 | `specifications:` list; file existence in `aget/specs/`; reciprocal grep in target spec |
| D3 | `evidence:` list; L-doc file existence; `originator:` value |
| D4 | `fit_criterion:` text; presence of quantitative bounds; readability test |

---

## Remediation Guidance

### From L0 to L1 (Initial → Developing)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| CR1 failure (no specifications:) | Identify ≥1 CAP-* or R-* spec this REQ implies; populate `specifications: [CAP-XXX-NNN]` | 5 min |
| Description is implementation-only | Rewrite description in stakeholder language: "What does the principal want?" rather than "How is it built?" | 10 min |
| No fit_criterion | Add a Volere fit criterion: testable condition that doesn't require reading the spec | 5-15 min |

### From L1 to L2 (Developing → Defined)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| Cited specs missing in aget/specs/ | Either author the missing spec or change `specifications:` to point only to existing specs (note PENDING for the rest in REQ Verification Status table) | 30+ min per spec |
| Single evidence citation only | Add 1+ additional evidence citations (L-doc, operational instance, ADR) | 5 min |
| Fit criterion vague | Replace adjectives with measurable bounds (numbers, time windows, presence/absence checks) | 10 min |

### From L2 to L3 (Defined → Optimizing)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| Spec doesn't reciprocally cite REQ | Edit cited spec to add `requirement: REQ-XXX` field in its frontmatter or traceability table | 5 min per spec |
| Fit criterion lacks quantitative bound | Add specific number/threshold (e.g., "within 120 seconds" not "quickly") | 5 min |
| Evidence is stale (>6 months) | Add 1 recent operational instance citation | 10 min |

---

## Usage

### When to Apply

- Before publishing a REQ to `aget/requirements/` (publication readiness)
- During REQ-CORE PENDING verification (issue #1063 follow-up)
- When auditing for decorative-requirement risk across published REQs
- When deriving CAP-* specs from REQ-* — the REQ should score L2+ first

### How to Apply

1. Verify eligibility gates (EG-1, EG-2, EG-3)
2. Check Critical Requirements (CR1, CR2, CR3)
3. Score D1-D4 against performance levels using observable evidence from the REQ file
4. Calculate weighted composite
5. Map to overall level
6. Document in Assessment Record (template below)
7. If L0/L1, apply Remediation Guidance

### Assessment Record Template

```markdown
## Assessment: REQ-{DOMAIN}-{F|Q}-{NNN} against RUBRIC_requirement_quality v1.0

**Date**: YYYY-MM-DD
**Assessor**: {agent or human}
**Subject**: REQ-{DOMAIN}-{F|Q}-{NNN} ({title})

### Eligibility Gates
| Gate | Pass/Fail |
|------|-----------|
| EG-1 (file exists) | {Pass/Fail} |
| EG-2 (id format) | {Pass/Fail} |
| EG-3 (status enum) | {Pass/Fail} |

### Critical Requirements
| CR | Pass/Fail | Notes |
|----|-----------|-------|
| CR1 (specifications: non-empty) | {Pass/Fail} | |
| CR2 (evidence: non-empty if validated/published) | {Pass/Fail} | |
| CR3 (description not implementation-only) | {Pass/Fail} | |

### Dimension Scores
| Dim | Weight | Score | Notes |
|-----|--------|-------|-------|
| D1 Schema Completeness | 35% | {0-3} | |
| D2 Forward Traceability | 30% | {0-3} | |
| D3 Backward Traceability | 15% | {0-3} | |
| D4 Fit Criterion Verifiability | 20% | {0-3} | |

### Composite
**Score**: {X.XX}/3.0
**Level**: {L0/L1/L2/L3} ({Initial/Developing/Defined/Optimizing})

### Gaps Identified
- {gap 1}
- {gap 2}

### Recommendations
- {next step 1}
- {next step 2}
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-19 | private-aget-framework-AGET | Initial rubric — closes L749 duality gap; grounded in C298 (Software System Requirement) ontology concept added FWRK-2026-004 |

## Related Artifacts

| Artifact | Relationship |
|----------|--------------|
| `aget/requirements/REQUIREMENTS_FORMAT.md` v1.0 | The contract this rubric scores against |
| `rubrics/RUBRIC_specification_maturity_v1.0.md` | Sibling rubric at the contract level (CAP-*) |
| `rubrics/RUBRIC_verification_test_quality_v1.0.md` (proposed) | Sibling rubric at the V-test level — closes the third L749 corner |
| L742 Two-Level Model | Foundational distinction this rubric operationalizes at the human level |
| L748 Requirements Storage Gap | The gap that motivated `aget/requirements/` (now scored by this rubric) |
| L749 Requirements-Rubric Duality | The duality this rubric structurally closes for the REQ corner |
| L671 Classification Without Consequence | The anti-pattern CR1 detects |
| C298 Software System Requirement (ISO/IEC/IEEE 29148:2018) | Ontology grounding |
| C291 Decorative Requirement | The L0 anti-pattern this rubric defends against |
| C302 Requirements Volatility (Lehman 1980) | Counter-perspective informing D3.2 evidence-currency |
| Issue #1063 (REQ-CORE 4 PENDING verifications) | Initial application target |

---

*Rubric created following SOP_RUBRIC_CREATION.md v2.0 patterns (template-conformant authoring; `/aget-create-rubric` skill not invoked — Advisory level per ADR-008; bypass documented in this footer)*
*Template: RUBRIC.template.md v2.0 (archetype-aware, domain-adaptive)*
*Ontology: ONTOLOGY_personal_ai_systems_v1.0.yaml (C298, C291, C302)*
*Closes: L749 Requirements-Rubric Duality gap at the requirement layer*
