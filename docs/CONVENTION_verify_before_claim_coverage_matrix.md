# CONVENTION: Verify-Before-Claim Coverage Matrix — claim-channels × enforcement-gates

**Status**: v1.0 (2026-07-11, v3.26 C-26-13) — convention rung per ADR-008 (L-doc evidence → SOP/convention → spec); the matrix is the registry, each cell's gate lives in its owning artifact.
**Evidence**: gh#1855 (three-seat 2026-07-10 exchange — three fleets independently paid for the same lesson in one day, each blind in the channel another had covered). Field cases per channel below.
**Parent principle**: verify-before-claim is a COVERAGE MATRIX, not a single gate. A conversational-channel hook cannot catch an artifact-write miss; a close-gate cannot catch a filing-channel miss. Coverage claims about "verify-before-claim" must name the channel.

## The matrix

| # | Claim channel | Claim shape | Owning canonical artifact | Gate | Status (v3.26) |
|---|---------------|-------------|---------------------------|------|----------------|
| 1 | **Issue filing** | novelty ("this is new") + target-existence ("spec/script X exists") | `/aget-file-issue` skill (spec: AGET_ISSUE_GOVERNANCE_SPEC) | **Step 3.5 Pre-Filing Probe**: dedup probe + canonical-existence probe, three-state report | **LANDED v3.26 C-26-13** (skill layer; spec delta R-ISSUE-034 candidate rides next enhance-spec pass) |
| 2 | **Status transition** | completion ("this ran / this is deployed") | `/aget-close-project` skill | **Step 5.5 Has-It-Run Gate (C-CLOSE-008)**: executable-mechanism deliverables need execution evidence pre-COMPLETE; absent → IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE or CLOSED (PARTIAL) | **LANDED v3.26 C-26-13** |
| 3 | **Conversational** | completeness/verification assertions in session prose | AGET_SESSION_SPEC **CAP-SESSION-015** (Pre-Assertion Gate, ×4 reqs) | registered v3.26 C-26-12 (`/aget-enhance-spec` pass, spec 1.3.0); reference impl = legalon `verify_claim_gate.py` + Stop hook (pilot; live FP bound unmet — recorded honestly per the FP-bound-unmet clause) | **REGISTERED v3.26 C-26-12** |
| 4 | **Cross-fleet lesson propagation** | convergence ("only we learned this") | AGET_ISSUE_GOVERNANCE_SPEC CAP-ISSUE-011 (lesson-first filing) + `/aget-record-lesson` Step 4.5 | propagation check at lesson capture: multi-seat OR framework-artifact → lesson_first filing; `lesson_first` label = cross-namespace join key | **WIRED v3.26 C-26-31** |

## Field evidence per channel (all 2026-07-10 unless noted)

1. **Filing**: legalon filed against a non-existent canonical spec (#1853 shape) and re-proposed a ruled p1 without a dedup probe (#1854 → folded #1845). Positive exemplar: framework seat's #1869 filing (2026-07-11) ran a voluntary dedup probe pre-filing — Step 3.5 makes that reflex structural.
2. **Status transition**: legalon stamped COMPLETE on a never-run mechanism (reopened by principal Decide). Main-fleet mirror: `/aget-close-project` close-gate re-derived DoD at the v3.24 close and caught 13 un-bumped public files pre-claim.
3. **Conversational**: legalon's advisory Stop hook fired live same-session it was built (FP datum) — but could not have caught channels 1–2's misses.
4. **Lesson propagation**: the same lesson existed as three private captures (main L681, legalon L249, framework memory) while CAP-ISSUE-011 — shipped v2.2.0 for exactly this — went unused by all three seats.

## Rules

1. **Name the channel.** "Verify-before-claim is covered" is an over-claim unless it names which channel(s); a seat asserting coverage cites the matrix row.
2. **Gates live in owning artifacts, not here.** This document registers placement + status; the enforcing text is in each skill/spec. On divergence, the owning artifact wins and this matrix is corrected.
3. **Reference impls travel by porting, not re-invention** (producer-ref-impl pattern, D-26-1): legalon `issue_freshness.py` → channel 1; main close-gate → channel 2; legalon `verify_claim_gate.py` → channel 3.
4. **Asymmetric coverage is the default failure mode**: each fleet builds the gate for the channel that last burned it. New channels (e.g. memory-write claims, cross-fleet relay claims — L908/L960 family) join as rows, not as reasons to widen an existing gate.

## Adoption

- Fleet seats: channels 1–2 arrive with the v3.26 skill payload; channel 3 is spec-registered (hook adoption = pilot-gated, D-26-1 lane); channel 4 fires at `/aget-record-lesson` invocation.
- Spec promotion: when a validator consumes this matrix mechanically (e.g. a coverage report per seat), promote to spec per ADR-008.

*v3.26 C-26-13 (gh#1855). Siblings: CONVENTION_check_three_state_contract.md (C-26-09), CONVENTION_terminal_state_vocabulary.md (C-26-14).*
