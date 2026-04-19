# Verification Test Quality Scoring Rubric

**Version**: 1.0
**Created**: 2026-04-19
**Author**: private-aget-framework-AGET
**Domain**: Quality of individual V-test artifacts (contract tests, gate V-tests, validators) against the AGET verification practice
**Archetype**: Compliance (gate-before-pass — does this V-test verify what it claims?)
**Assessor**: Hybrid (agent scores executability/specificity/discrimination mechanically; human verifies adequacy honesty)
**Status**: Active
**Closes Gap**: L749 Requirements-Rubric Duality (the third corner — V-test layer)

---

## Purpose

Score the quality of individual verification test artifacts in AGET. Supports decisions about:

- **Test theater detection** (ADR-007 enforcement): which V-tests merely report success without actual verification?
- **Gate readiness**: which gate V-tests are mature enough to be relied on as release blockers?
- **Coverage prioritization**: which CAP-* / REQ-* lack adequate verification?
- **Premature victory defense** (L92): which V-tests pass before the property they claim to verify exists?

Closes the third corner of L749 Requirements-Rubric Duality. With `RUBRIC_requirement_quality_v1.0` (REQ-* layer) and `RUBRIC_specification_maturity_v1.0` (CAP-* layer) operational, this rubric makes the verification layer mechanically scorable for the first time. ADR-007 (No Test Theater) gets its measurement instrument; the L671 (Classification Without Consequence) failure mode at the V-test layer is now closable.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Individual V-test artifact quality (per-test scoring) | Test domain content correctness (does the test test the right thing?) |
| Executability and machine-readability of test results | Test runtime performance optimization |
| Specificity of conformance claims (REQ/CAP traceability) | Cross-test redundancy elimination |
| Failure discrimination (adversarial check per L689) | Test maintenance burden estimation |
| Adequacy honesty (Dijkstra principle per C304) | Test framework selection (pytest vs shell vs gh API) |
| Suite-level coverage reporting | Mutation testing depth |

## Theoretical Basis

| Framework | Application |
|-----------|-------------|
| **L749** (Requirements-Rubric Duality) | This rubric is the third corner; without it, the triad is incomplete and ADR-007 stays decorative |
| **ADR-007** (No Test Theater) | The architectural decision this rubric operationalizes — measurement instrument for the prohibition |
| **C300** (Software System Test, ISO/IEC/IEEE 29119-1:2022) | Ontology grounding — V-test artifacts are instances of this concept |
| **C301** (Software System Verification Test, ISO/IEC/IEEE 12207:2017 §6.4.9) | Specifically the verification subtype (vs validation per Boehm's V-model) |
| **C304** (Test Adequacy Limit, Dijkstra EWD249 1970) | The structural counter-perspective — informs D4 (Adequacy Honesty) |
| **L92** (Premature Victory) | Anti-pattern that D3 (Failure Discrimination) defends against |
| **L284** (Delegation Theater) | Anti-pattern that CR3 (not test theater) defends against |
| **L671** (Classification Without Consequence) | The failure mode this rubric prevents at the V-test layer |
| **L689** (Rubric-as-Adversary, VP-of-AI) | Adversarial test: would a plausibly defective V-test pass each L2/L3 descriptor? Applied dimension-by-dimension. |
| **Goodenough & Gerhart 1975** (Toward a Theory of Test Data Selection, IEEE TSE SE-1:2) | Formal limit on test adequacy — informs D4 |
| **Dawson 2017** (rubric design 14 elements) | Behavioral anchoring; observable criteria |

---

## Rubric Archetype Selection

**This rubric uses**: **Compliance** (gate-before-pass)

A V-test either verifies a specific property executable in finite time, or it does not. Eligibility gates check structural prerequisites (the test exists as an executable artifact); dimension scoring assesses depth of verification. CR3 (not test theater) and CR4 (cites the spec/REQ verified) are auto-L0 conditions.

Sibling consistency: identical archetype to `RUBRIC_requirement_quality_v1.0` and `RUBRIC_specification_maturity_v1.0`.

---

## Domain Adaptation

**This rubric uses**: **Maturity** label set (Initial / Developing / Defined / Optimizing) — sibling consistency.

| Level | Score | Maturity Label | Plain meaning |
|-------|------|---------------|---------------|
| L3 | 3 | Optimizing | Reference-quality V-test — used as exemplar; cited in test-design docs |
| L2 | 2 | Defined | Production-grade V-test — gate-blocking ready |
| L1 | 1 | Developing | Useful V-test with at least one structural weakness |
| L0 | 0 | Initial | Test theater, decorative test, or unverifiable claim |

**Construction method** (Mertler 2001): L3 + L0 anchored first, L1/L2 interpolated.

---

## Eligibility Gates

Binary prerequisites evaluated BEFORE dimension scoring. Any gate failure = ineligible (do not score).

| Gate ID | Requirement | Pass test |
|---------|-------------|-----------|
| EG-1 | Test exists as a resolvable artifact (file path, function reference, or shell command) | The artifact can be located and invoked |
| EG-2 | Test has a stable identifier (function name, test ID, or numbered V-test reference) | The identifier is referenced from at least one external location (CI config, gate checklist, or spec) |
| EG-3 | Test is not abandoned (last invocation within current release cycle, or marked `@pytest.mark.skip` with explicit reason) | Visible in test discovery output OR has documented skip rationale |

---

## Dimension Classification

All four dimensions are **Quality** dimensions (per-test observation). Suite-level maturity (cross-test consistency) is captured separately as a composite metric, not a per-test dimension.

| Dimension | Classification | Why |
|-----------|----------------|-----|
| D1 Executability | Quality | Per-test observation — can it run? |
| D2 Conformance Claim Specificity | Quality | Per-test observation — what does it claim to verify? |
| D3 Failure Discrimination | Quality | Per-test observation — does it fail when the property is broken? |
| D4 Adequacy Honesty | Quality | Per-test observation — does it acknowledge its scope? |

---

## Behavioral Anchoring

Per L689 adversarial test, every L2/L3 descriptor below was checked against: *"Would a plausibly decorative V-test (test-theater instance) pass this descriptor?"* — if yes, the descriptor was tightened. The Dijkstra principle (C304) was applied as a sanity floor: no descriptor can claim a V-test "proves correctness."

---

## Dimensions

### D1: Executability

**Weight**: 35%
**Definition**: The test can be run programmatically with a machine-readable result, in a time bounded sufficiently for CI/gate use.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D1.1 | Test has an executable invocation (pytest function, shell command, gh API call, etc.) — NOT "verify by inspection" | 50% | **Yes (CR1 prerequisite)** |
| D1.2 | Test result is machine-readable (exit code 0/1, parseable JSON, structured pytest output) — not "look at the logs" | 30% | No |
| D1.3 | Test completes in < 60 seconds wall-clock (suitable for gate execution) | 20% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | Executable + machine-readable + < 30 seconds; integrated with CI matrix; structured failure messages identify the violated property |
| **L2: Defined** | 2 | Executable + machine-readable + < 60 seconds; runs reliably in any AGET environment |
| **L1: Developing** | 1 | Executable but result requires human interpretation OR runtime > 60 seconds OR environment-specific (won't run in CI) |
| **L0: Initial** | 0 | "Verify by inspection" only; no executable artifact; or runtime so long it cannot be used as a gate |

---

### D2: Conformance Claim Specificity

**Weight**: 25%
**Definition**: The test asserts a specific, named property of a specific spec or requirement — not a generic "system works" claim.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D2.1 | Test has at least one explicit assertion (`assert`, `expect`, `[[ -f X ]]`, etc.) — NOT just "logs success and exits 0" | 40% | **Yes (CR3)** |
| D2.2 | Test cites the specific CAP-*, R-*, REQ-*, or RUBRIC_* it verifies (in function name, docstring, or comment) | 35% | **Yes (CR4)** |
| D2.3 | Test asserts a single behavioral property — not a "smoke test" claiming to verify N unrelated things at once | 25% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | Single explicit assertion citing one specific CAP-*/R-*/REQ-*/RUBRIC-* identifier; failure message names the violated provision verbatim |
| **L2: Defined** | 2 | Explicit assertion citing the verified contract; minor multi-property entanglement OK if related |
| **L1: Developing** | 1 | Assertion exists but contract citation is implicit (only in test name, not docstring) OR multiple unrelated properties bundled |
| **L0: Initial** | 0 | No assertion (relies on absence of exception); OR asserts only "succeeded" without naming what; OR claims to verify many unrelated things ("smoke test") |

---

### D3: Failure Discrimination (L689 adversarial check)

**Weight**: 20%
**Definition**: The test reliably fails when the property it claims to verify is actually broken — and does not silently pass on environmental issues.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D3.1 | Test has been observed to fail when the verified property is broken (regression evidence in git history or test output) | 40% | No |
| D3.2 | Test would discriminate the failure mode it claims to detect (passes for a known-good case, fails for a known-bad case — the L689 adversarial check) | 35% | No |
| D3.3 | Test does not silently pass on environmental issues (missing file → fail, not skip; network failure → fail, not skip; unless explicitly justified) | 25% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | Documented regression where the test fired before remediation; adversarial pair (good/bad fixture) included in test code; environmental failures are loud |
| **L2: Defined** | 2 | Test discriminates good/bad cases reliably; environmental failures are loud; regression evidence may be informal |
| **L1: Developing** | 1 | Test discriminates, but only at known-good cases — never observed to fail in practice; OR silently skips on environmental failures |
| **L0: Initial** | 0 | Test passes regardless of input (truly trivial assertion like `assert True`); OR silently passes on environmental failures (premature-victory enabler per L92) |

---

### D4: Adequacy Honesty (C304 Dijkstra principle)

**Weight**: 20%
**Definition**: The test acknowledges its sampling boundary — it claims evidence of partial correctness, not proof of correctness.

#### Criteria

| ID | Criterion | Weight | Critical? |
|----|-----------|--------|-----------|
| D4.1 | Test docstring or comment names what is NOT tested (the sampling boundary, the unverified neighbors) | 40% | No |
| D4.2 | Suite-level coverage is reported alongside the test's pass rate (the test does not pretend to be the entire verification) | 30% | No |
| D4.3 | Test result is framed as "evidence of partial correctness," not "proof of correctness" — specifically, no documentation claims the test "verifies" or "proves" the system is correct | 30% | No |

#### Performance Levels

| Level | Score | Criteria |
|-------|-------|----------|
| **L3: Optimizing** | 3 | Docstring explicitly names the verified property, the unverified neighbors, and links to suite-level coverage report; failure message acknowledges the test is one sample among many |
| **L2: Defined** | 2 | Docstring names what IS tested precisely (so the unverified scope is implicit); suite is reported alongside the individual test's pass |
| **L1: Developing** | 1 | Test verifies a specific property but documentation overstates scope ("ensures X works") OR coverage context absent |
| **L0: Initial** | 0 | Documentation claims the test "proves" or "guarantees" the system is correct (Dijkstra violation); OR no acknowledgement of scope at all |

---

## Critical Requirements (automatic L0 regardless of dimension scores)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| **CR1** | Test has an executable invocation (D1.1) | Without an executable test, there is no verification — only an aspiration. |
| **CR2** | Test is invoked at a documented gate or trigger (CI config, gate checklist, hook, or SOP step references it) | An orphan test is not a verification of any system property; it is a side artifact. |
| **CR3** | Test has at least one explicit assertion (D2.1) — ADR-007 enforcement | Test theater = test that returns success without performing verification. CR3 is the structural prohibition against ADR-007 violations. |
| **CR4** | Test cites the specific CAP-*, R-*, REQ-*, or RUBRIC_* it verifies (D2.2) | Verification without traceability is unmoored — what does the test prove fits which specification? Per L749 duality and REQ-CORE-F-001 forward-traceability mandate. |

If any CR fails, the V-test scores L0 regardless of other dimensions.

---

## Scoring Method

**Method**: GatewayFirst (Eligibility gates, then Critical Requirements, then weighted average)

### Calculation

```
1. Eligibility gates (EG-1, EG-2, EG-3) — fail = NOT ASSESSED
2. Critical Requirements (CR1, CR2, CR3, CR4) — fail = L0 regardless of other scores
3. Score each dimension D1-D4 (0-3) using performance levels
4. Weighted composite = (D1 × 0.35) + (D2 × 0.25) + (D3 × 0.20) + (D4 × 0.20)
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

| Dimension | Required Evidence (observable from test artifact alone) |
|-----------|---------------------------------------------------------|
| D1 | Executable invocation (file path, function name, command line); runtime measurement; exit code or structured output |
| D2 | Assertion count; CAP/R/REQ/RUBRIC citation in name, docstring, or comment; behavioral property scope |
| D3 | Git history of test failures; presence of adversarial good/bad fixtures; environmental-failure handling code path |
| D4 | Test docstring contents; documentation surrounding the test; suite-level coverage report presence |

---

## Remediation Guidance

### From L0 to L1 (Initial → Developing)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| CR1 fail (no executable invocation) | Convert "verify by inspection" into a runnable assertion; if truly inspection-only, accept that this is governance, not verification | 15-30 min |
| CR3 fail (no assertion) | Add at least one `assert` or equivalent that fails when the property is broken | 5-15 min |
| CR4 fail (no contract citation) | Add the CAP-*/R-*/REQ-* identifier to the test docstring, name, or comment | 2-5 min |
| Test theater (CR3) | Either delete the test or replace its body with actual verification logic; pretending verification is worse than no verification | 30+ min |

### From L1 to L2 (Developing → Defined)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| Runtime > 60 seconds | Refactor for speed (mock external dependencies, use fixtures, parallelize); if truly slow, mark as `slow` and exclude from gate runs | 30-60 min |
| Assertion is implicit (only in name) | Add explicit docstring naming the verified property and its provision citation | 5 min |
| No regression evidence | Run the test against a known-broken fixture; if it doesn't fail, the test is not discriminating; rewrite | 15-30 min |
| Documentation overstates scope ("ensures X works") | Replace with precise scope claim ("verifies X under condition Y") | 5 min |
| Silently skips on environmental failures | Convert skip to fail; require explicit reason for any retained skip | 10-20 min |

### From L2 to L3 (Defined → Optimizing)

| Gap | Remediation Steps | Effort |
|-----|-------------------|--------|
| Multi-property entanglement | Split into single-property tests; one assertion per test | 30 min per split |
| No adversarial fixture | Add a known-bad fixture proving the test discriminates | 15 min |
| Environmental loudness mediocre | Audit all skip/error paths; ensure missing files, network failures, version mismatches trigger fail not skip | 30 min |
| Suite-level coverage not reported | Add a coverage roll-up that the individual test references | 30 min |
| Documentation does not acknowledge scope boundary | Add explicit "what this does NOT test" line to docstring | 5 min per test |

---

## Usage

### When to Apply

- Before adding a V-test to a gate's blocking-deliverables list
- During ADR-007 audits (test-theater detection sweep)
- When debugging a "passing test, broken behavior" incident (D3 failure)
- When a CAP-* or REQ-* lacks adequate verification (coverage gap analysis)
- During post-release retrospectives (which V-tests caught what; which missed what)

### How to Apply

1. Verify eligibility gates (EG-1, EG-2, EG-3)
2. Check Critical Requirements (CR1, CR2, CR3, CR4)
3. Score D1-D4 against performance levels using observable evidence from the test artifact
4. Calculate weighted composite
5. Map to overall level
6. Document in Assessment Record (template below)
7. If L0/L1, apply Remediation Guidance

### Suite-Level Composition

Per-test scores aggregate to suite-level metrics:

| Suite Metric | Computation |
|--------------|-------------|
| Suite L3 ratio | Count of L3 V-tests / Total scored V-tests |
| Suite L0 ratio (test theater density) | Count of L0 V-tests / Total scored V-tests |
| Critical Requirement pass rate | Count of (CR1 AND CR2 AND CR3 AND CR4 = pass) / Total scored V-tests |
| Coverage breadth | Distinct CAP-*/REQ-* IDs cited / Total CAP-*/REQ-* IDs in scope |

**Suite L0 ratio > 10%** = framework-level test-theater concern; ADR-007 audit warranted.
**Coverage breadth < 50%** = verification gap requiring CAP-*/REQ-* prioritization.

### Assessment Record Template

```markdown
## Assessment: {V-test ID or path} against RUBRIC_verification_test_quality v1.0

**Date**: YYYY-MM-DD
**Assessor**: {agent or human}
**Subject**: {test function name, file path, or gate V-test ID}
**Verifies**: {CAP-* or R-* or REQ-* identifier}

### Eligibility Gates
| Gate | Pass/Fail |
|------|-----------|
| EG-1 (resolvable artifact) | {Pass/Fail} |
| EG-2 (stable identifier + external reference) | {Pass/Fail} |
| EG-3 (not abandoned) | {Pass/Fail} |

### Critical Requirements
| CR | Pass/Fail | Notes |
|----|-----------|-------|
| CR1 (executable invocation) | {Pass/Fail} | |
| CR2 (invoked at gate/trigger) | {Pass/Fail} | |
| CR3 (explicit assertion — ADR-007) | {Pass/Fail} | |
| CR4 (contract citation) | {Pass/Fail} | |

### Dimension Scores
| Dim | Weight | Score | Notes |
|-----|--------|-------|-------|
| D1 Executability | 35% | {0-3} | |
| D2 Conformance Claim Specificity | 25% | {0-3} | |
| D3 Failure Discrimination | 20% | {0-3} | |
| D4 Adequacy Honesty | 20% | {0-3} | |

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
| 1.0 | 2026-04-19 | private-aget-framework-AGET | Initial rubric — closes L749 third corner; grounded in C300/C301/C304 ontology concepts added FWRK-2026-004 |

## Related Artifacts

| Artifact | Relationship |
|----------|--------------|
| `aget/rubrics/RUBRIC_requirement_quality_v1.0.md` | Sibling rubric at REQ-* layer (L749 first corner) |
| `rubrics/RUBRIC_specification_maturity_v1.0.md` | Sibling rubric at CAP-* layer (L749 second corner — currently in private/aget-framework agent) |
| **L749** Requirements-Rubric Duality | The duality this rubric structurally closes for the V-test corner |
| **ADR-007** No Test Theater | The architectural decision this rubric operationalizes — measurement instrument |
| **L92** Premature Victory | Anti-pattern D3 (Failure Discrimination) defends against |
| **L284** Delegation Theater | Anti-pattern CR3 defends against |
| **L671** Classification Without Consequence | The failure mode this rubric prevents at the V-test layer |
| **C300** Software System Test (ISO/IEC/IEEE 29119-1:2022) | Ontology grounding |
| **C301** Software System Verification Test (ISO/IEC/IEEE 12207:2017 §6.4.9, IEEE 1012-2016, Boehm 1981 V-model) | Ontology grounding (verification vs validation) |
| **C304** Test Adequacy Limit (Dijkstra EWD249, Goodenough-Gerhart 1975) | Counter-perspective informing D4 (Adequacy Honesty) |
| `planning/project-proposals/PROPOSAL_verification_test_quality_rubric.md` | The proposal that motivated this rubric (now superseded — implementation done) |
| AGET contract test suite (`tests/test_*.py`, 160+ tests across templates) | Initial application target |

---

## Closing Note: The Triad Is Now Complete

```
┌─ Requirements ──────────┐    ┌─ Specifications ────────┐    ┌─ Verifications ─────────┐
│ REQ-* (35 published)    │←──→│ CAP-* (~40 in specs/)   │←──→│ V-* (160+ contract tests │
│                          │    │                          │    │   + N gate V-tests)     │
│ RUBRIC: ✓ v1.0          │    │ RUBRIC: ✓ v1.0          │    │ RUBRIC: ✓ v1.0          │
│ (REQ-* layer)           │    │ (CAP-* layer)           │    │ (V-* layer)             │
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
       L749 corner CLOSED              L749 corner CLOSED              L749 corner CLOSED
```

With this rubric, AGET has mechanical scoring instruments at all three corners of the L749 duality. Test theater (ADR-007 violation) is now detectable. Premature victory (L92) is now measurable. Classification Without Consequence (L671) at the V-test layer is now closable.

---

*Rubric created following SOP_RUBRIC_CREATION.md v2.0 patterns and the structure of RUBRIC_requirement_quality_v1.0 for sibling consistency. `/aget-create-rubric` skill not invoked — Advisory level per ADR-008.*
*Template: RUBRIC.template.md v2.0 (archetype-aware, domain-adaptive)*
*Ontology: ONTOLOGY_personal_ai_systems_v1.0.yaml (C300, C301, C304 — added FWRK-2026-004)*
*Closes: L749 Requirements-Rubric Duality gap at the verification layer (third corner)*
