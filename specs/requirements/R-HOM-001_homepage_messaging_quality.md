# R-HOM-001: Homepage Messaging Quality

**Version**: 1.0
**Date**: 2025-12-29
**Status**: Active
**Category**: Public Presence
**Priority**: HIGH

---

## Purpose

Define messaging quality requirements for the AGET organization homepage to ensure claims are credible, audience-appropriate, and evidence-based.

**Problem Addressed**: Gap between aspirational marketing claims and demonstrated capabilities. Homepage claiming outcomes ("10x faster contract analysis") without evidence damages credibility with technical audience.

**Scope**: Organization homepage (`.github/profile/README.md`) Use Cases section

**Theoretical Basis**:
- Evidence-first design (L289)
- Premature victory anti-pattern (L92)
- Governance grounding (L333)

---

## Requirements

### R-HOM-001-01: Evidence-Based Claims (Ubiquitous)

**Statement**: The homepage use cases SHALL only claim what AGET demonstrates through its own usage.

**Rationale**: Borrowing credibility from other companies ("Allianz does insurance claims processing") is not evidence that AGET enables it. Claims must be self-demonstrated.

**Verification**:
```python
# Each claim must have proof_link to AGET artifact
for claim in homepage_claims:
    assert claim.proof_link.startswith('https://github.com/aget-framework/')
    assert requests.get(claim.proof_link).status_code == 200
```

**Implements**: L289 (Evidence-first design)

---

### R-HOM-001-02: Audience Targeting (Ubiquitous)

**Statement**: The homepage SHALL target CLI power users and small technical teams, NOT enterprise buyers.

**Rationale**: AGET's current distribution is via GitHub. Primary audience finds us through search, not enterprise sales. Messaging must match actual audience.

**Verification**:
```python
# Persona check
VALID_PERSONAS = ['developer', 'power_user', 'small_team', 'technical_individual']
assert homepage.target_persona in VALID_PERSONAS
assert 'enterprise' not in homepage.primary_messaging
```

**Implements**: L407 (Pain-point framing superiority)

---

### R-HOM-001-03: Aspirational Marking (Conditional)

**Statement**: IF a claim is "Validated" (others do it, not AGET), THEN it SHALL be clearly marked as aspirational or "Coming Soon".

**Rationale**: Mixing demonstrated and aspirational claims without distinction misleads users about current capabilities.

**Verification**:
```python
for use_case in homepage_use_cases:
    if use_case.credibility_level == 'validated':
        assert use_case.section == 'coming_soon' or 'aspirational' in use_case.label
```

**Implements**: L407 (Credibility level taxonomy)

---

### R-HOM-001-04: Pain-Point Framing (Ubiquitous)

**Statement**: Homepage use cases SHALL lead with user pain points, NOT industry verticals.

**Rationale**: Users search for problems ("AI forgets context") not industries ("insurance claims processing"). Pain-point framing matches search intent and claims only what AGET solves.

**EARS Pattern**: Ubiquitous - Always applies to use case presentation.

**Verification**:
```python
# Use case structure check
for use_case in homepage_use_cases:
    assert use_case.has_pain_statement  # "I explain the same context every session"
    assert use_case.has_solution  # How AGET solves it
    assert not use_case.leads_with_industry  # NOT "Insurance Claims Processing"
```

**Implements**: L407 (Pain-point vs industry vertical decision)

**Examples**:

| ❌ Industry Vertical | ✅ Pain-Point |
|---------------------|---------------|
| Insurance Claims Processing | "My agents don't know about each other" |
| Legal Contract Analysis | "I explain the same context every session" |
| Healthcare Diagnosis | "Knowledge walks out when people leave" |

---

### R-HOM-001-05: Proof Links Required (Ubiquitous)

**Statement**: Each use case SHALL include a "See it in action" link to a real AGET artifact demonstrating the claim.

**Rationale**: Claims without evidence are marketing. Claims with links to working examples are credible.

**Verification**:
```python
for use_case in homepage_use_cases:
    assert use_case.proof_link is not None
    assert requests.get(use_case.proof_link).status_code == 200
    # Link must be to AGET artifact, not external
    assert 'aget-framework' in use_case.proof_link or 'github.com/gabormelli' in use_case.proof_link
```

**Implements**: L289 (Evidence-first), R-PUB-001-12 (Link integrity)

---

### R-HOM-001-06: 5D Framework Evaluation (Event-Driven)

**Statement**: WHEN a new use case is proposed for the homepage, it SHALL be evaluated on the 5D Use Case Characterization Framework before inclusion.

**Rationale**: Systematic evaluation prevents ad-hoc additions that dilute messaging quality.

**5D Dimensions**:
| Dimension | Best Score for Homepage |
|-----------|------------------------|
| D1: Credibility | Demonstrated |
| D2: Complexity | Low-Medium |
| D3: Coordination | Any |
| D4: Governance Fit | Strong |
| D5: Adoption Friction | Low |

**Verification**:
```python
def evaluate_use_case(use_case):
    score = {
        'd1_credibility': use_case.credibility_level,  # Must be 'demonstrated'
        'd2_complexity': use_case.domain_complexity,
        'd3_coordination': use_case.agent_pattern,
        'd4_governance_fit': use_case.aget_value_alignment,
        'd5_friction': use_case.adoption_barrier
    }
    return score['d1_credibility'] == 'demonstrated' and score['d4_governance_fit'] == 'strong'
```

**Implements**: L408 (5D Use Case Characterization Framework)

---

### R-HOM-001-07: Credibility Indicators (Ubiquitous)

**Statement**: Homepage SHALL include credibility indicators distinguishing Demonstrated, Validated, and Aspirational use cases.

**Rationale**: Transparent credibility levels build trust. Users can distinguish "AGET does this" from "AGET could do this".

**Credibility Levels**:

| Level | Definition | Homepage Treatment |
|-------|------------|-------------------|
| **Demonstrated** | AGET does it, artifact exists | Primary use cases |
| **Validated** | Industry does it, documented | "Coming Soon" section |
| **Aspirational** | Plausible but unproven | Exclude or clearly mark |

**Verification**:
```python
for use_case in homepage_use_cases:
    assert use_case.credibility_level in ['demonstrated', 'validated', 'aspirational']
    if use_case.in_primary_section:
        assert use_case.credibility_level == 'demonstrated'
```

**Implements**: L407 (Credibility level taxonomy)

---

## Requirement Summary Table

| ID | Type | Statement Summary | Verification |
|----|------|-------------------|--------------|
| R-HOM-001-01 | Ubiquitous | Only claim what AGET demonstrates | Proof link check |
| R-HOM-001-02 | Ubiquitous | Target CLI power users, not enterprise | Persona check |
| R-HOM-001-03 | Conditional | Mark validated claims as aspirational | Section check |
| R-HOM-001-04 | Ubiquitous | Lead with pain points, not industries | Structure check |
| R-HOM-001-05 | Ubiquitous | Include proof links to AGET artifacts | HTTP 200 check |
| R-HOM-001-06 | Event-Driven | Evaluate new use cases on 5D framework | Score check |
| R-HOM-001-07 | Ubiquitous | Include credibility indicators | Label check |

---

## Traceability

### Implements

| Requirement | Implements | Evidence |
|-------------|------------|----------|
| R-HOM-001-01 | L289 (Evidence-first) | Claims require demonstration |
| R-HOM-001-02 | L407 (Audience match) | Technical audience via GitHub |
| R-HOM-001-03 | L92 (No premature claims) | Clear aspiration marking |
| R-HOM-001-04 | L407 (Pain-point framing) | User-centric messaging |
| R-HOM-001-05 | R-PUB-001-12 (Link integrity) | Verified proof links |
| R-HOM-001-06 | L408 (5D Framework) | Systematic evaluation |
| R-HOM-001-07 | L407 (Credibility taxonomy) | Transparent levels |

### Validated By

| Requirement | Test | Location |
|-------------|------|----------|
| R-HOM-001-01 | check_evidence_based_claims() | validate_homepage_messaging.py |
| R-HOM-001-02 | check_audience_targeting() | validate_homepage_messaging.py |
| R-HOM-001-03 | check_aspirational_marking() | validate_homepage_messaging.py |
| R-HOM-001-04 | check_pain_point_framing() | validate_homepage_messaging.py |
| R-HOM-001-05 | check_proof_links() | validate_homepage_messaging.py |
| R-HOM-001-06 | Manual review | PROJECT_PLAN for new use cases |
| R-HOM-001-07 | check_credibility_indicators() | validate_homepage_messaging.py |

### Referenced In

| Artifact | Reference |
|----------|-----------|
| PROJECT_PLAN_homepage_use_cases_v1.0.md | Implementation plan |
| L407_pain_point_framing_superiority.md | Decision rationale |
| L408_5d_use_case_characterization.md | Evaluation framework |
| .github/profile/README.md | Implementation target |

---

## Success Criteria

**Homepage messaging is compliant WHEN**:
- All R-HOM-001-01 through R-HOM-001-07 requirements satisfied
- validate_homepage_messaging.py exits with code 0
- No claims without proof links
- No industry-vertical-first framing
- Credibility indicators present

**Homepage messaging is non-compliant WHEN**:
- Claims made without AGET demonstration
- Enterprise-targeted messaging
- Industry verticals lead over pain points
- Missing or broken proof links
- Undistinguished aspirational claims

---

## Gate Integration (L557)

**Enforcement Level**: BLOCKING

**V-Test Requirements** (L555 substance-aware):

| V-Test ID | Requirement | BLOCKING | Substance Check |
|-----------|-------------|:--------:|-----------------|
| V-R-HOM-001-01 | Evidence-based claims | YES | All proof links return HTTP 200 |
| V-R-HOM-001-02 | Audience targeting | YES | No "enterprise" in primary messaging |
| V-R-HOM-001-03 | Aspirational marking | YES | Validated claims in "Coming Soon" section |
| V-R-HOM-001-04 | Pain-point framing | YES | Use cases lead with pain, not industry |
| V-R-HOM-001-05 | Proof links | YES | All links resolve to AGET artifacts |
| V-R-HOM-001-07 | Credibility indicators | YES | Labels present for each use case |

**Release Gate**: Gate 0 (pre-execution)

**Integration** (add to SOP_release_process.md):
```markdown
### Homepage Messaging Check (R-HOM-001)
- [ ] Run: `python3 .aget/patterns/validation/validate_homepage_messaging.py`
- [ ] All claims verified: BLOCKING
- [ ] All proof links valid: BLOCKING
```

**Validator Location**: `.aget/patterns/validation/validate_homepage_messaging.py`

**Traceability**: L555 (Scaffold vs Substance), L557 (Spec-to-Enforcement)

---

## Evolution History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-29 | Initial specification (7 requirements) |

---

## Related Documents

- **L407**: Pain-Point Framing Superiority (decision rationale)
- **L408**: 5D Use Case Characterization Framework (evaluation method)
- **R-PUB-001**: Public Release Completeness (homepage link requirements)
- **L289**: Evidence-First Design (foundational principle)
- **L92**: Premature Victory Anti-Pattern (claim discipline)

---

*R-HOM-001: Homepage Messaging Quality*
*Ensures homepage claims are credible, audience-appropriate, and evidence-based*
*Created: 2025-12-29 | Owner: aget-framework*
