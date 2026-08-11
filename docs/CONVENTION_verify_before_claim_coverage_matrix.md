# CONVENTION: Verify-Before-Claim Coverage Matrix — claim-channels × enforcement-gates

**Status**: v1.1 (2026-08-10) — adds channel 5 (**Disclosure**), PROPOSED for v3.31. v1.0 (2026-07-11, v3.26 C-26-13) — convention rung per ADR-008 (L-doc evidence → SOP/convention → spec); the matrix is the registry, each cell's gate lives in its owning artifact.
**Evidence**: three-seat 2026-07-10 exchange — three fleets independently paid for the same lesson in one day, each blind in the channel another had covered. Field cases per channel below.
**Parent principle**: verify-before-claim is a COVERAGE MATRIX, not a single gate. A conversational-channel hook cannot catch an artifact-write miss; a close-gate cannot catch a filing-channel miss. Coverage claims about "verify-before-claim" must name the channel.

## The matrix

| # | Claim channel | Claim shape | Owning canonical artifact | Gate | Status (v3.26) |
|---|---------------|-------------|---------------------------|------|----------------|
| 1 | **Issue filing** | novelty ("this is new") + target-existence ("spec/script X exists") | `/aget-file-issue` skill (spec: AGET_ISSUE_GOVERNANCE_SPEC) | **Step 3.5 Pre-Filing Probe**: dedup probe + canonical-existence probe, three-state report | **LANDED v3.26 C-26-13** (skill layer; spec delta R-ISSUE-034 candidate rides next enhance-spec pass) |
| 2 | **Status transition** | completion ("this ran / this is deployed") | `/aget-close-project` skill | **Step 5.5 Has-It-Run Gate (C-CLOSE-008)**: executable-mechanism deliverables need execution evidence pre-COMPLETE; absent → IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE or CLOSED (PARTIAL) | **LANDED v3.26 C-26-13** |
| 3 | **Conversational** | completeness/verification assertions in session prose | AGET_SESSION_SPEC **CAP-SESSION-015** (Pre-Assertion Gate, ×4 reqs) | registered v3.26 C-26-12 (`/aget-enhance-spec` pass, spec 1.3.0); reference impl = a downstream supervisor seat's `verify_claim_gate.py` + Stop hook (pilot; live FP bound unmet — recorded honestly per the FP-bound-unmet clause) | **REGISTERED v3.26 C-26-12** |
| 4 | **Cross-fleet lesson propagation** | convergence ("only we learned this") | AGET_ISSUE_GOVERNANCE_SPEC CAP-ISSUE-011 (lesson-first filing) + `/aget-record-lesson` Step 4.5 | propagation check at lesson capture: multi-seat OR framework-artifact → lesson_first filing; `lesson_first` label = cross-namespace join key | **WIRED v3.26 C-26-31** |
| 5 | **Disclosure** | remediation ("documented, therefore handled") | this convention + `scripts/check_skill_route_contract.py` | **the falsifier, not the tier**: after the response, does a *known-defective instance* still FAIL the check? If it now passes because the defect was described rather than removed, the response was suppression | **PROPOSED v3.31** |

## Field evidence per channel (all 2026-07-10 unless noted)

1. **Filing**: a supervisor seat filed against a non-existent canonical spec and re-proposed an already-ruled priority item without a dedup probe. Positive exemplar: the framework seat's own retroactive tracker filing (2026-07-11) ran a voluntary dedup probe pre-filing — Step 3.5 makes that reflex structural.
2. **Status transition**: a supervisor seat stamped COMPLETE on a never-run mechanism (reopened by principal decision). Mirror case: `/aget-close-project` close-gate re-derived DoD at the v3.24 close and caught 13 un-bumped public files pre-claim.
3. **Conversational**: the advisory Stop hook fired live the same session it was built (FP datum) — but could not have caught channels 1–2's misses.
5. **Disclosure** (2026-08-10, framework seat): a route-contract check buckets promises as `owed` (gating) or `aspirational` — the latter defined in its own output as *"hedged prose — does not gate"*. A route whose every mention carries a hedge marker (`not built`, `never existed`, `does not exist`, …) stops gating. **12 routes were cleared by wording rather than by construction.** The exhibit documents itself: one skill disclosed at line 199 that a route did not exist, and 42 lines earlier still named that route inside its own `## Output Format` template — the block it asserts it will emit. The predicate required a leading slash, so it could reach the line *confessing* the defect and not the line *performing* it. Hedging the visible line silenced the gate while the false claim shipped.

   The same shape held in four sibling instruments the same day: a telemetry reader whose docstring claimed two schemas over a corpus holding three (producing a false first-use flag); its own V-test, which built fixtures shaped like the reader's assumption and never read the corpus; two EARS clauses at `ubiquitous`/`shall` over a script with zero callers; and a Goal checker assigning `concept-id` by regex with no resolution step — where **the repair the checker invited would itself have been a suppression**, flipping a warning green while adding another unresolvable citation.

   Why this channel needs its own row rather than folding into channel 3: the other four gates catch a claim that was *never verified*. This one catches a claim that was verified, documented accurately, and still left the defect in place — where **the documenting is what turned the check green**. A tier self-assessment ("was my response record, mitigation, or constraint?") cannot separate them, because suppression is indistinguishable from constraint when viewed from inside. Only re-running the check against a known-defective instance can.
4. **Lesson propagation**: the same lesson existed as three seat-local captures (two supervisor L-docs + the framework seat's memory) while CAP-ISSUE-011 — shipped v2.2.0 for exactly this — went unused by all three seats.

## Rules

1. **Name the channel.** "Verify-before-claim is covered" is an over-claim unless it names which channel(s); a seat asserting coverage cites the matrix row.
2. **Gates live in owning artifacts, not here.** This document registers placement + status; the enforcing text is in each skill/spec. On divergence, the owning artifact wins and this matrix is corrected.
3. **Reference impls travel by porting, not re-invention** (producer-ref-impl pattern): `issue_freshness.py` → channel 1; the close-gate DoD re-derivation → channel 2; `verify_claim_gate.py` → channel 3 (all producer-seat implementations, ported not re-invented).
4. **Asymmetric coverage is the default failure mode**: each fleet builds the gate for the channel that last burned it. New channels (e.g. memory-write claims, cross-fleet relay claims — L908/L960 family) join as rows, not as reasons to widen an existing gate.

## Adoption

- Fleet seats: channels 1–2 arrive with the v3.26 skill payload; channel 3 is spec-registered (hook adoption = pilot-gated, D-26-1 lane); channel 4 fires at `/aget-record-lesson` invocation.
- Spec promotion: when a validator consumes this matrix mechanically (e.g. a coverage report per seat), promote to spec per ADR-008.

*v3.26 C-26-13. Siblings: CONVENTION_check_three_state_contract.md (C-26-09), CONVENTION_terminal_state_vocabulary.md (C-26-14).*
