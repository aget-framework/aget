# AGET Rubrics — Quality Measurement at Three Layers

**Created**: 2026-04-19
**Purpose**: Front door for `aget/rubrics/` — explains why three rubrics exist, how they relate, and how to apply them.

---

## Why This Directory Exists

AGET treats requirements, specifications, and verification tests as three distinct artifact layers, each with its own quality concept. The L749 Requirements-Rubric Duality principle (a requirement implies a rubric; a rubric implies a requirement) means that every layer where AGET makes intent claims must also have a measurement instrument that determines whether those claims hold.

Without measurement, quality stays subjective. With measurement, quality becomes mechanically scorable, reproducible, and auditable from public artifacts alone. That measurement happens here.

This directory was established 2026-04-19 alongside the third rubric (verification-test quality), completing the L749 triad in public.

---

## The Three Rubrics

| File | Layer | What it measures | Sibling scorer |
|---|---|---|---|
| [`RUBRIC_requirement_quality_v1.0.md`](RUBRIC_requirement_quality_v1.0.md) | Requirements (`aget/requirements/REQ-*`) | Schema completeness, forward traceability, backward traceability, fit-criterion verifiability | [`scripts/score_requirements.py`](../../private-aget-framework-AGET/scripts/score_requirements.py) |
| [`RUBRIC_specification_maturity_v1.0.md`](RUBRIC_specification_maturity_v1.0.md) | Specifications (`aget/specs/CAP-*`, `R-*`) | L0-L5 maturity ladder: Identified → Patterned → Verifiable → Grounded → Traceable → Governed | [`scripts/score_specifications.py`](../../private-aget-framework-AGET/scripts/score_specifications.py) |
| [`RUBRIC_verification_test_quality_v1.0.md`](RUBRIC_verification_test_quality_v1.0.md) | Verification tests (`tests/test_*.py`, gate V-tests, validators) | Executability, conformance-claim specificity, failure discrimination, adequacy honesty (Dijkstra principle) | [`scripts/score_verification_tests.py`](../../private-aget-framework-AGET/scripts/score_verification_tests.py) |

---

## The Triad Relationship

The three rubrics form a triad. Each corner is meaningfully independent (a high-quality requirement does not guarantee a high-quality specification; a high-quality specification does not guarantee a high-quality verification test), but the corners bind via traceability:

- A requirement with no specification trace is **decorative** (the C291 anti-pattern at the requirement layer)
- A specification with no verification-test trace is **unverified** (the L671 anti-pattern at the specification layer)
- A verification test with no specification cited is **unmoored** (the ADR-007 No-Test-Theater concern at the verification layer)

The traceability requirement is what makes the three layers a coherent structure rather than three independent stacks.

---

## How to Apply These Rubrics

The intended usage pattern is mechanical scoring rather than human review. Each rubric has a paired scorer script that:

1. Parses the relevant artifact directory
2. Applies the rubric criteria mechanically
3. Outputs a level per artifact (L0 to L3 for REQ/V-test rubrics; L0 to L5 for SPEC rubric)
4. Reports portfolio distribution + lowest-scoring items as remediation candidates

Run a scorer in human-readable mode:

```
python3 scripts/score_requirements.py
python3 scripts/score_specifications.py
python3 scripts/score_verification_tests.py
```

Or in machine-readable mode for CI:

```
python3 scripts/score_requirements.py --quiet
python3 scripts/score_specifications.py --json
python3 scripts/score_verification_tests.py --json --pretty
```

Exit codes follow the convention: 0 = clean, 1 = L1 (warning), 2 = L0 (error: decorative/test-theater present), 3 = configuration error.

All three scorers are integrated into `scripts/health_check.py`, so portfolio quality is part of the standard health-check output.

---

## Reading Order

If you're new to this directory, read in this order:

1. **`RUBRIC_requirement_quality_v1.0.md`** first — the simplest rubric (4 dimensions, 4 critical requirements, L0-L3 scale). Establishes the structural pattern the other two follow.
2. **`RUBRIC_specification_maturity_v1.0.md`** second — climbs a 6-level ladder rather than a 4-corner score. Different shape, same intent.
3. **`RUBRIC_verification_test_quality_v1.0.md`** third — back to the 4-corner pattern but anchored in the Dijkstra principle (testing shows presence of bugs but never their absence). Most philosophically interesting because of the adequacy-honesty dimension.

After reading the rubrics, run the corresponding scorer against the framework's actual portfolio to see what the rubric produces in practice. That's the honest way to verify a rubric — apply it to real artifacts, surface the findings, and assess whether the findings match your intuition.

---

## Reference

| Anchor | Source |
|---|---|
| L749 Requirements-Rubric Duality | `.aget/evolution/L749_requirements_rubric_duality.md` (private) |
| L867 Coherence-Directed Investment as Enhance-Verb-Family | `.aget/evolution/L867_coherence_directed_investment_as_enhance_verb_family.md` (private) |
| Specification-Fault Principle (L742) | `aget/specs/AGET_FRAMEWORK_SPEC.md` |
| ADR-007 No Test Theater | `aget/specs/` (architecture decisions) |

---

*The triad is a measurement instrument. Apply it; don't venerate it.*
