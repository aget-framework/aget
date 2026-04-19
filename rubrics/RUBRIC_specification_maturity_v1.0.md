# Specification Maturity Scoring Rubric

**Version**: 1.0
**Created**: 2026-03-16
**Author**: private-aget-framework-AGET
**Domain**: Specification maturity assessment — how close a spec is to verified fabric
**Status**: Active
**Cross-Agent Source**: F159 (private-professional-core-aget), L682

## Purpose

Assess the maturity of individual specifications and the overall spec portfolio using observable criteria. Supports decisions about:
- Release readiness: is this spec mature enough to ship?
- Enhancement prioritization: which specs need uplift?
- Fleet propagation: what adoption risk does this spec carry?
- Governance coverage: are specs verified or decorative?

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Individual spec maturity (per-spec scoring) | Requirement content quality (domain correctness) |
| Portfolio-level maturity distribution | Template-specific customization quality |
| Maturity progression tracking across releases | Agent adoption behavior (covered by L510) |
| Cross-reference completeness | Ontology concept quality (covered by RUBRIC_ontology_maturity) |

## Theoretical Basis

| Framework | Application |
|-----------|-------------|
| F159 (professional-core) | L0-L5 Requirements Formalization Maturity — foundational model |
| L682 (Requirements Maturity Model) | 5-dimension maturity framework — this rubric operationalizes D1 (Content) |
| ADR-008 | Advisory → Strict → Generator — enforcement progression mapped to levels |
| L622 | 11-phase specification enhancement lifecycle — phases map to level transitions |
| L671 | Classification Without Consequence — each level must trigger different actions |
| Dawson 2017 | 14 rubric design elements — observable criteria, concrete thresholds |
| IEEE 830 | SRS quality attributes — completeness, consistency, testability |

---

## Levels

### L0: Identified

The spec exists with named requirements that have unique IDs.

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| Spec file exists in `specs/` | File present with `.md` or `.yaml` extension | |
| Requirements have unique IDs | Each requirement has `R-DOMAIN-NNN` or `CAP-DOMAIN-NNN` | |
| No duplicate IDs | `grep -c` for each ID returns exactly 1 within the spec | |
| No orphaned requirements | Every requirement is in a numbered section, not floating text | |

**Transition to L1**: Apply EARS sentence patterns to all requirements.

### L1: Patterned

Every requirement follows an EARS sentence pattern with explicit keywords.

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| EARS keywords present | Each requirement uses SHALL/SHALL NOT/SHOULD/WHERE/WHEN/IF-THEN | |
| Pattern type recorded | Each requirement tagged: ubiquitous/conditional/event-driven/optional/prohibited | |
| Subject identified | Each requirement names the system/actor (e.g., "The SYSTEM shall...") | |
| No ambiguous modal verbs | No "may", "might", "could" in requirement statements (use in rationale only) | |

**Transition to L2**: Define verification method for each requirement.

### L2: Verifiable

Every requirement has an explicit verification method and V-test ID.

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| V-test IDs assigned | Each requirement links to `V-DOMAIN-NNN` | |
| Verification method specified | Each V-test declares method: automated / manual / inspection | |
| No "verify by inspection only" for SHALL requirements | SHALL requirements have automated or manual test, not just inspection | |
| V-test is executable | V-test describes a concrete check (not "verify it works") | |

**Transition to L3**: Ground requirements in controlled vocabulary.

### L3: Grounded

Requirements reference controlled vocabulary terms (SKOS concepts) and cite evidence.

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| Vocabulary section present | Spec includes `vocabulary:` section with SKOS definitions | |
| Key terms defined | Domain-specific terms in requirements are defined in vocabulary | |
| Evidence cited | Requirements cite L-doc or external source (why this requirement exists) | |
| No undefined jargon | Terms not in vocabulary or common English are flagged | |

**Transition to L4**: Wire bidirectional cross-references.

### L4: Traceable

Requirements have bidirectional traceability: evidence (why), enforcement (how), related specs (what else).

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| Evidence traceability | Each requirement links to L-doc (source of learning) | |
| Enforcement traceability | Each requirement links to V-test (verification) | |
| Spec cross-references | Related specs cited with bidirectional acknowledgment | |
| Cross-reference report exists | Phase 5 report produced during /aget-enhance-spec | |
| No stale cross-references | All referenced artifacts verified current (L611) | |

**Transition to L5**: Establish formal change control.

### L5: Governed

Spec has formal change control, authority tracking, and conformance validation.

| Criterion | Observable Evidence | Pass/Fail |
|-----------|-------------------|-----------|
| Version history | Spec tracks version changes with dates and rationale | |
| Change authority defined | Who can modify this spec? (Decision Authority Matrix reference) | |
| Conformance validator exists | Automated script checks compliance (exit code enforcement) | |
| Self-compliance verified | Spec has passed Phase 6 self-compliance check (L560 bootstrapping) | |
| Fleet conformance tracked | Downstream agent compliance rate measured and reported | |

---

## Portfolio Assessment Template

Score each spec and identify the constraining level:

| Spec | L0 | L1 | L2 | L3 | L4 | L5 | Effective | Constraining Gap |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|-----------------|
| AGET_FRAMEWORK_SPEC | | | | | | | | |
| AGET_INSTANCE_SPEC | | | | | | | | |
| AGET_PROJECT_PLAN_SPEC | | | | | | | | |
| AGET_GOVERNANCE_HIERARCHY_SPEC | | | | | | | | |
| AGET_ISSUE_GOVERNANCE_SPEC | | | | | | | | |
| R-SYNC-001 | | | | | | | | |
| [Add specs...] | | | | | | | | |

**Scoring**: FULL (100%), PARTIAL (50-99% criteria met), GAP (<50%)

**Effective Level**: Highest level where ALL criteria are FULL.

**Portfolio Score**: Distribution of effective levels across all specs (e.g., "3 at L3, 2 at L2, 1 at L1").

## Consequence Map (L671)

Each level must trigger different actions:

| Effective Level | Consequence |
|----------------|-------------|
| L0 | Spec exists but is not release-ready. Must reach L1 before VERSION_SCOPE inclusion. |
| L1 | Spec has form but not verification. Can be included in VERSION_SCOPE as draft. |
| L2 | Spec has testable criteria. Can be enforced locally (Strict layer). |
| L3 | Spec is grounded in vocabulary. Can be published to templates. |
| L4 | Spec is fully wired. Can be used as governance reference by other specs. |
| L5 | Spec is production-grade. Can be used as exemplar for fleet-wide conformance. |

## Anti-Patterns

| Anti-Pattern | Detection | Source |
|-------------|-----------|--------|
| **Maturity Theater** | Advancing levels on rubric without improving spec usefulness | F176 (professional-core) |
| **Level Skipping** | Claiming L4 without passing L2 (no V-tests but has cross-refs) | L682 cross-dimensional constraints |
| **Decorative Vocabulary** | SKOS section present but terms not used in requirements | L671 |
| **Aspirational Traceability** | Cross-references declared but targets don't exist | L611 stale assertions |

---

*RUBRIC_specification_maturity_v1.0.md*
*Adapted from F159 (private-professional-core-aget) for framework spec portfolio*
*Per L671: each level triggers different downstream actions*
