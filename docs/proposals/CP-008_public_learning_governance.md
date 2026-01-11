---
proposal_id: CP-008
title: Public Learning Governance
author: private-aget-framework-AGET
date_submitted: 2026-01-11
status: ACCEPTED
category: process
---

## Abstract

Formalize the governance pathway for publishing learnings from private `.aget/evolution/` directories to public `docs/learnings/`, including vocabulary terms, specification requirements, standard operating procedure, and validation tooling. This addresses the gap where L455 and L457 were published ad-hoc without formal criteria.

## Motivation

**Problem**: The `docs/learnings/` directory currently contains 2 published learnings (L455, L457) but lacks formal governance:

| Layer | Private (`.aget/evolution/`) | Public (`docs/learnings/`) |
|-------|------------------------------|----------------------------|
| Vocabulary | `Learning_Document`, `L_Doc` | Missing |
| Specification | AGET_LDOC_SPEC, AGET_EVOLUTION_SPEC | Missing |
| SOP | N/A (private) | Missing |
| Validator | validate_ldoc.py | Missing |

**Impact of not making this change**:
- Ad-hoc publication decisions with inconsistent criteria
- No sanitization requirements (risk of internal references leaking)
- No validation of published content quality
- No discoverable process for future publications

**Industry alignment**: Lessons learned processes require validation, scoping, and institutionalization phases (PMI, Stan Garfield).

## Proposed Change

### 1. Vocabulary Extension

Add `Published_Learning` term to `AGET_VOCABULARY_SPEC.md`:

```yaml
Published_Learning:
  skos:definition: "Learning document graduated from private evolution to public docs/learnings/"
  aget:location: "docs/learnings/"
  skos:broader: "Learning_Document"
  skos:related: ["Sanitization", "Graduation"]
```

### 2. Specification Extension

Add CAP-EVOL-007 (Public Learning Publication) to `AGET_EVOLUTION_SPEC.md`:

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-EVOL-007-01 | ubiquitous | The SYSTEM shall place Published_Learnings in `docs/learnings/` |
| CAP-EVOL-007-02 | conditional | IF L-doc published THEN the SYSTEM shall verify fleet-wide applicability |
| CAP-EVOL-007-03 | ubiquitous | The SYSTEM shall sanitize internal references before publication |
| CAP-EVOL-007-04 | ubiquitous | The SYSTEM shall preserve L-number from source L-doc |
| CAP-EVOL-007-05 | conditional | IF L-doc references private agents THEN the SYSTEM shall generalize references |
| CAP-EVOL-007-06 | ubiquitous | The SYSTEM shall include `publication_date` in published L-doc |
| CAP-EVOL-007-07 | conditional | IF source L-doc updated THEN the SYSTEM should review Published_Learning |

### 3. SOP Creation

Create `sops/SOP_learning_publication.md` with:
- Gate 1: Selection criteria
- Gate 2: Sanitization checklist
- Gate 3: Publication steps
- Gate 4: Verification (V-PUB tests)

### 4. Validator Creation

Create `validation/validate_public_learnings.py` with checks:
- V-PUB-001: File matches L###_*.md pattern
- V-PUB-002: Has YAML frontmatter
- V-PUB-003: Has publication_date (WARN for legacy)
- V-PUB-004: No .aget/ paths
- V-PUB-005: No private-* agent names (WARN)
- V-PUB-006: Has ## Learning section
- V-PUB-007: Has ## Evidence section (WARN)

## Impact Assessment

```yaml
impact_assessment:
  breaking: false
  version_impact: minor
  affected_artifacts:
    - artifact_type: spec
      artifact_name: AGET_EVOLUTION_SPEC.md
      change_type: update
    - artifact_type: spec
      artifact_name: AGET_VOCABULARY_SPEC.md
      change_type: update
    - artifact_type: sop
      artifact_name: SOP_learning_publication.md
      change_type: create
    - artifact_type: validator
      artifact_name: validate_public_learnings.py
      change_type: create
```

## Alternatives Considered

| Option | Rationale for not choosing |
|--------|---------------------------|
| No formal governance | Risk of inconsistent quality, internal reference leaks |
| Automated graduation pipeline | Over-engineering for current scale (2 L-docs) |
| New standalone spec | Better to extend AGET_EVOLUTION_SPEC (same domain) |

## Acceptance Criteria

- [x] `Published_Learning` term exists in AGET_VOCABULARY_SPEC.md
- [x] CAP-EVOL-007 requirements (7) exist in AGET_EVOLUTION_SPEC.md
- [x] SOP_learning_publication.md exists with 4 gates
- [x] validate_public_learnings.py passes on L455, L457
- [x] Synthetic invalid file fails validation

---

## Resolution

```yaml
resolution: accepted
resolution_date: 2026-01-11
resolution_rationale: Formalizes governance for docs/learnings/ with vocabulary, spec, SOP, and validator
resulting_artifacts:
  - type: vocabulary
    path: specs/AGET_VOCABULARY_SPEC.md (Published_Learning term)
  - type: spec
    path: specs/AGET_EVOLUTION_SPEC.md (CAP-EVOL-007)
  - type: sop
    path: sops/SOP_learning_publication.md
  - type: validator
    path: validation/validate_public_learnings.py
version_released: v3.4.0
```

---

*CP-008: Public Learning Governance | Status: ACCEPTED*
