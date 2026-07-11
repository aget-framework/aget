# CONVENTION: Three-State Check Contract — {PASS, FAIL, UNREACHABLE}

**Status**: v1.0 (2026-07-10, v3.26 C-26-09) — convention rung per ADR-008 (L-doc evidence → SOP/convention → spec); spec promotion when a validator consumes this contract mechanically.
**Evidence**: gh#1842 (three independent same-24h derivations) + gh#1844 (supervisor-lane); field case: `check_skill_reliance_manifest.py` C3 silently degraded to WARN "archetype index unreachable" fleet-wide for two releases — readers could not distinguish "checked and conformant" from "never checked" (gh#1837 d2).
**Maturity**: ADR-004 three-tier degradation is the parent principle; this contract names the reporting half.

## The contract

Every `check_*` script / skill / gate SHALL report each check as exactly one of three states:

| State | Meaning | NOT to be conflated with |
|-------|---------|--------------------------|
| **PASS** | the check RAN and the condition holds | — |
| **FAIL** | the check RAN and the condition does not hold | UNREACHABLE (a missing dependency is not a conformance failure) |
| **UNREACHABLE** | the check COULD NOT RUN — missing dependency, absent input surface, no network, wrong vantage | PASS-by-absence ("nothing found" when the surface wasn't looked at) and FAIL-by-absence |

## Rules

1. **UNREACHABLE is never silent.** It appears in output with the reason (what dependency was missing) — a summary that folds UNREACHABLE checks into the PASS count or omits them entirely violates the contract (the gh#1837-d2 failure shape).
2. **UNREACHABLE does not gate.** Exit codes: FAIL may block; UNREACHABLE degrades per ADR-004 (warn-and-continue) unless the check is explicitly declared reachability-critical.
3. **Aggregate lines carry all three counts** when any UNREACHABLE exists: `12 PASS · 1 FAIL · 2 UNREACHABLE(reason, reason)` — never `12/15 passed`.
4. **Absence-vs-negative discipline** (same family as the study_topic surface manifest, CAP-SESSION-007-08): a consumer must always be able to distinguish "verified absent" (FAIL/PASS on a reachable surface) from "not verifiable from here" (UNREACHABLE).

## Reference exemplar

`scripts/check_skill_reliance_manifest.py` C3: when no archetype-index candidate path exists, report `C3 UNREACHABLE (archetype index not found at any candidate path)` — not WARN-and-blend, not silent skip. (Candidate-path fix `b18053f` made C3 reachable on standard deployments; the UNREACHABLE state remains the honest report for non-standard layouts.)

## Adoption

- New check surfaces: apply from first commit.
- Existing check-* family: adopt at next substantive touch (no big-bang rewrite; L601 expected lag is fine — a check not yet emitting UNREACHABLE is lagging, not violating, until touched).
- Self-application (L922): the v3.26 release plan's own V-test rows adopt the vocabulary from this convention's landing commit forward.

## Traceability

gh#1842 (contract) · gh#1844 (supervisor evidence) · gh#1837-d2 (field failure) · ADR-004 (degradation parent) · CAP-SESSION-007-08 (absence-interpretability sibling) · v3.26 C-26-09.
