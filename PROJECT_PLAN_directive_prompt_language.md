# PROJECT_PLAN: Directive Prompt Language Pattern

**Version**: 1.1.0
**Status**: In Progress
**Created**: 2026-01-07
**Updated**: 2026-01-07
**Author**: private-legalon-vp_of_ai-aget (cross-AGET discovery)
**Theme**: Shell helper prompt clarity
**Tracking**: [Issue #53](https://github.com/aget-framework/aget/issues/53)
**CAP-PP-011 Compliant**: Yes (all gates have V-tests)

---

## Executive Summary

Shell helper prompts that reference documented protocols should use **directive language** ("Read X", "Execute Y") rather than **suggestive language** ("e.g. read X", "you might...").

Discovery: Principal noted inconsistent wake protocol execution when using the `aget()` shell helper. Root cause: the phrase "(e.g. read AGENTS.md)" was interpreted as optional/illustrative rather than mandatory.

**Key Outcomes:**
- Update `docs/SHELL_INTEGRATION.md` with corrected prompt patterns
- Add "Prompt Language Guidelines" section documenting the pattern
- Fleet-wide consistency for protocol execution

---

## Scope

**In Scope:**
- Update CLI profile examples in SHELL_INTEGRATION.md
- Add Prompt Language Guidelines section
- Document anti-patterns and correct patterns

**Out of Scope (deferred):**
- Shell file templates in `shell/` directory → v2.12.0 (if exists)
- Automated prompt linting → future enhancement
- Fleet-wide `.zshrc` migration script → user responsibility

**Dependencies:**
- L050 lesson learned document (✅ created in vpofai)
- Issue #53 filed (✅ created)

**Deviation Note:**
- L050 resides in `vpofai/.aget/evolution/` (discovery context)
- Framework repo (`aget`) is not itself an AGET, so has no `.aget/evolution/`
- Pattern documentation now lives in `docs/SHELL_INTEGRATION.md` (canonical location)
- This cross-repo pattern (discovery in AGET → fix in framework) is expected for framework enhancements

---

## Success Criteria (CAP-PP-005)

| Criterion | Metric | Target | Actual | Verification |
|-----------|--------|--------|--------|--------------|
| SC-1: Doc updated | SHELL_INTEGRATION.md updated | Yes | ✅ Yes | `grep "Read AGENTS.md" docs/SHELL_INTEGRATION.md` |
| SC-2: Guidelines added | Prompt Language section exists | Yes | ✅ Yes | `grep "Prompt Language" docs/SHELL_INTEGRATION.md` |
| SC-3: Anti-patterns documented | Anti-pattern examples present | ≥2 | ✅ 5 | `grep -c "❌" docs/SHELL_INTEGRATION.md` |

---

## Risk Assessment (CAP-PP-006)

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| R1: Breaking existing user configs | Low | Low | Documentation change only, no code |
| R2: Inconsistency with other CLIs | Med | Med | Review all CLI profiles in same PR |

---

## V-Test Summary (CAP-PP-011)

| Gate | V-Tests | Result | Description |
|------|---------|--------|-------------|
| Gate 0 | V0.1-V0.2 | ✅ 2/2 | Preparation |
| Gate 1 | V1.1-V1.3 | ✅ 3/3 | Documentation updates |
| Gate 2 | V2.1 | ✅ 1/1 | Commit & PR |
| Gate 3 | V3.1 | — | Retrospective |
| **Total** | **7 V-tests** | **6/7** | — |

---

## Traceability Matrix (CAP-PP-007)

### Issues → Gates

| Issue | Description | Gate | Deliverable |
|-------|-------------|------|-------------|
| #53 | Directive prompt language pattern | G1 | G1.1, G1.2 |

### L-docs → Deliverables

| L-doc | Requirement | Gate | Status |
|-------|-------------|------|--------|
| L050 | Directive vs suggestive language | G1 | Reference |

---

## Effort Estimates (CAP-PP-008)

| Gate | Tier | Estimate | Notes |
|------|------|----------|-------|
| G0 | Pattern-Clear | 10m | Already done |
| G1 | Pattern-Clear | 30m | Doc edits |
| G2 | Pattern-Clear | 10m | Commit/PR |
| G3 | Pattern-Clear | 10m | Retrospective |
| **Total** | — | **~1h** | — |

---

## Gate 0: Preparation

**Objective:** Ensure prerequisites are in place
**Status:** Complete

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G0.1 | L050 lesson learned document | vpofai-aget | Done |
| G0.2 | Issue #53 filed | vpofai-aget | Done |

### Verification Tests

#### V0.1: L050 exists
```bash
[ -f ~/code/gmelli/private-legalon-vp_of_ai-aget/.aget/evolution/L050_directive_prompt_language_pattern.md ] && echo "PASS" || echo "FAIL"
```
**Expected:** PASS

#### V0.2: Issue #53 exists
```bash
gh issue view 53 --repo aget-framework/aget --json state -q '.state' | grep -q "OPEN" && echo "PASS" || echo "FAIL"
```
**Expected:** PASS

### Checklist

- [x] V0.1 PASS: L050 exists
- [x] V0.2 PASS: Issue #53 exists

**Decision Point:** Proceed to Gate 1? [GO]

---

## Gate 1: Documentation Updates

**Objective:** Update SHELL_INTEGRATION.md with directive prompt patterns
**Status:** Complete

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G1.1 | Fix Claude profile prompt (line ~207) | Agent | Done |
| G1.2 | Add "Prompt Language Guidelines" section | Agent | Done |
| G1.3 | Review/fix other CLI profiles (Codex, Gemini, custom) | Agent | Done |

### Verification Tests

#### V1.1: Claude profile uses directive language
```bash
grep -q "Read AGENTS.md and execute" ~/code/gmelli/aget/docs/SHELL_INTEGRATION.md && echo "PASS" || echo "FAIL"
```
**Expected:** PASS
**Actual:** PASS ✅

#### V1.2: Prompt Language Guidelines section exists
```bash
grep -q "## Prompt Language Guidelines" ~/code/gmelli/aget/docs/SHELL_INTEGRATION.md && echo "PASS" || echo "FAIL"
```
**Expected:** PASS
**Actual:** PASS ✅

#### V1.3: Anti-patterns documented
```bash
[ $(grep -c "❌" ~/code/gmelli/aget/docs/SHELL_INTEGRATION.md) -ge 2 ] && echo "PASS" || echo "FAIL"
```
**Expected:** PASS
**Actual:** PASS ✅ (5 anti-patterns)

### Checklist

- [x] V1.1 PASS: Claude profile uses directive language
- [x] V1.2 PASS: Prompt Language Guidelines section exists
- [x] V1.3 PASS: Anti-patterns documented

**Decision Point:** Proceed to Gate 2? [GO]

---

## Gate 2: Commit & PR

**Objective:** Commit changes and create PR
**Status:** Complete

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G2.1 | Commit with descriptive message | Agent | Done |
| G2.2 | Push to origin | Agent | Pending |

### Verification Tests

#### V2.1: Changes committed
```bash
cd ~/code/gmelli/aget && git log -1 --oneline | grep -qi "prompt\|directive\|L050" && echo "PASS" || echo "FAIL"
```
**Expected:** PASS
**Actual:** PASS ✅ (`341942b docs: Add directive prompt language pattern (L050)`)

### Checklist

- [x] V2.1 PASS: Changes committed

**Decision Point:** Proceed to Gate 3? [GO]

---

## Gate 3: Retrospective

**Objective:** Document learnings and close project
**Status:** Pending

### Deliverables

| ID | Deliverable | Owner | Status |
|----|-------------|-------|--------|
| G3.1 | Update L050 with outcome (if needed) | Agent | Pending |
| G3.2 | Close Issue #53 | Agent | Pending |
| G3.3 | Mark PROJECT_PLAN complete | Agent | Pending |

### Verification Tests

#### V3.1: Issue #53 closed
```bash
gh issue view 53 --repo aget-framework/aget --json state -q '.state' | grep -q "CLOSED" && echo "PASS" || echo "FAIL"
```
**Expected:** PASS

### Checklist

- [ ] V3.1 PASS: Issue #53 closed

**Project Complete**

---

## Velocity Analysis (CAP-PP-009)

*In progress*

| Gate | Estimated | Actual | Ratio | Notes |
|------|-----------|--------|-------|-------|
| G0 | 10m | 10m | 1.0x | Already complete |
| G1 | 30m | 20m | 0.67x | Pattern-clear edits |
| G2 | 10m | 5m | 0.5x | Direct commit to main |
| G3 | 10m | — | — | — |
| **Total** | ~1h | ~35m+ | — | — |

---

## References (CAP-PP-010)

### L-docs
- L050: Directive Prompt Language Pattern (vpofai)

### Files
- `docs/SHELL_INTEGRATION.md` - Primary update target
- `~/.zshrc` - User's local config (already updated)

### Related
- Issue #53: Enhancement request

---

## Execution Log

*Record key actions and decisions during execution*

### Session 2026-01-07

| Time | Gate | Action | Artifact | Commit |
|------|------|--------|----------|--------|
| +0m | G0 | L050 created | L050_directive_prompt_language_pattern.md | — |
| +5m | G0 | Issue #53 filed | github.com/aget-framework/aget/issues/53 | — |
| +10m | — | PROJECT_PLAN created | PROJECT_PLAN_directive_prompt_language.md | — |
| +15m | G1 | Added Prompt Language Guidelines section | docs/SHELL_INTEGRATION.md | — |
| +18m | G1 | Updated Claude profile to directive language | docs/SHELL_INTEGRATION.md | — |
| +20m | G1 | Updated Codex, Gemini, custom profiles | docs/SHELL_INTEGRATION.md | — |
| +22m | G1 | V-tests V1.1-V1.3 PASS | — | — |
| +25m | G2 | Committed changes | — | 341942b |
| +30m | — | PROJECT_PLAN updated to v1.1.0 | PROJECT_PLAN_directive_prompt_language.md | — |

---

## Changelog

### v1.1.0 (2026-01-07)

- Gate 1 complete: Documentation updates
- Gate 2 complete: Commit 341942b
- Updated Success Criteria with actual values
- Updated V-Test Summary (6/7 passing)
- Added execution log entries

### v1.0.0 (2026-01-07)

- Initial plan
- Gate 0 complete (L050, Issue #53)

---

*PROJECT_PLAN_directive_prompt_language.md — Per CAP-PP-001 through CAP-PP-011*
