# PATTERN: Migration Validation Gate

**Pattern Name**: Migration Validation Gate (Blocking)
**Category**: PROJECT_PLAN Gates
**Created**: 2025-12-26
**Source**: L376 (Premature Completion Declaration)

---

## Purpose

Standard gate structure for migration PROJECT_PLANs to enforce complete validation before declaring migration complete.

**Problem**: Migrations declared complete after behavioral validation but before automated compliance validation, resulting in undetected issues.

**Solution**: Explicit blocking gate that enforces both automated and behavioral validation.

---

## When to Use

Use this gate pattern in PROJECT_PLANs for:
- Agent migrations (version upgrades)
- Template migrations
- Fleet-wide migrations
- Any work that requires compliance verification

**Signal**: If the plan involves updating agent versions or structures, include this gate.

---

## Gate Template

```markdown
## Gate N: Validation (BLOCKING)

**Objective**: Verify migration completeness via automated + behavioral validation

**Prerequisites**:
- [ ] Structural migration complete (files created/updated)
- [ ] Validators downloaded to .aget/validation/

**Deliverables**:

| # | Deliverable | Verification |
|---|-------------|--------------|
| N.1 | Download validators (if needed) | `ls .aget/validation/*.py` shows 4 files |
| N.2 | Run validate_version_consistency.py | Exit code 0, ✅ PASS |
| N.3 | Run validate_naming_conventions.py | Exit code 0, ✅ PASS |
| N.4 | Run validate_template_manifest.py | Exit code 0, ✅ PASS |
| N.5 | Run validate_composition.py | Exit code 0, ✅ PASS |
| N.6 | Verify CLAUDE.md symlink (L366) | `readlink CLAUDE.md` = "AGENTS.md" |
| N.7 | Edge cases audit (optional but recommended) | See Edge Cases section |
| N.8 | Behavioral validation (wake-up, capability tests) | All capabilities functional |
| N.9 | Fix any issues found | Re-run all checks until pass |

**Success Criteria**:
- ALL automated validators show ✅ PASS
- Behavioral validation confirms capabilities work
- No regressions detected
- Git working directory clean

**Validation Checklist**: See `docs/patterns/MIGRATION_COMPLETION_CHECKLIST.md`

**Decision Point**:
- **GO** if all validators pass + behavioral validation passes
- **NOGO** if any validation fails → return to previous gate, fix issues

**CRITICAL**: This gate is BLOCKING. Do NOT proceed to completion with any FAIL or PENDING status.
```

---

## Pattern Elements

### 1. Validator Download (Deliverable N.1)

**Why**: Enables self-validation without full framework repo (L027 pattern)

**Command**:
```bash
mkdir -p .aget/validation
cd .aget/validation
curl -sO https://raw.githubusercontent.com/aget-framework/aget/main/validation/validate_*.py
```

### 2. Automated Validators (Deliverables N.2-N.5)

**Required Validators**:
1. `validate_version_consistency.py` - Version alignment check
2. `validate_naming_conventions.py` - L-doc/ADR naming compliance
3. `validate_template_manifest.py` - Manifest schema validation
4. `validate_composition.py` - Capability composition validation

**Execution**: All must pass before proceeding.

### 3. Behavioral Validation (Deliverable N.6)

**Tests**:
- Agent wakes up with correct version
- Capabilities are functional
- No regressions in existing behavior

**Method**: Manual verification via agent interaction

### 4. Issue Resolution (Deliverable N.7)

**Process**:
1. If any validator fails → STOP
2. Fix identified issues
3. Re-run ALL validators
4. Repeat until all pass

**Anti-Pattern**: Marking validators PENDING and continuing

### 5. Edge Cases Audit (Deliverable N.7 - Optional but Recommended)

**Purpose**: Catch structural issues not covered by standard validators

**Checks**:

1. **CLAUDE.md Symlink** (L366 requirement)
   ```bash
   readlink CLAUDE.md
   # Expected: "AGENTS.md"
   ```

2. **No Duplicate Migration History**
   ```bash
   cat .aget/version.json | grep -c "v2.12.0"
   # Expected: 1 (not 2+)
   ```

3. **Valid Migration Date**
   ```bash
   # Check migration_history date is YYYY-MM-DD format
   grep "2025-12-26" .aget/version.json
   # Expected: Match
   ```

4. **Capabilities Array Exists** (v2.12.0+)
   ```bash
   jq '.capabilities' .aget/version.json
   # Expected: Array (not null)
   ```

5. **L-doc Naming Compliance**
   ```bash
   ls .aget/evolution/L*.md | grep -v "L[0-9]\{3\}_.*\.md"
   # Expected: No output (all files match L###_snake_case.md)
   ```

**When to Skip**: Simple migrations with minimal customization

**When Required**: Fleet migrations, complex customizations, governance agents

---

## Blocking Semantics

**"BLOCKING GATE" means**:
- Cannot proceed to next gate until all deliverables complete
- Cannot declare project complete with FAIL or PENDING items
- GO/NOGO decision is binary (all pass or return to fix)

**Enforcement**:
- Make gate status visible in execution log
- Require explicit GO decision before proceeding
- Document any NOGO decisions and remediation

---

## Success Pattern

```
Structural Migration (previous gates)
    ↓
Validator Download
    ↓
Run ALL 4 Automated Validators
    ↓
All Pass? → NO → Fix Issues → Re-run Validators
          ↓ YES
Behavioral Validation
    ↓
All Tests Pass? → NO → Fix Issues → Re-test
                ↓ YES
Declare Migration Complete ✅
```

---

## Anti-Patterns (L376)

### ❌ Premature Completion

**What NOT to Do**:
- Skip automated validators ("behavioral is enough")
- Assume validators unavailable without checking
- Mark validators PENDING and declare complete
- Run only some validators, not all 4

**Consequence**: Undetected compliance issues, user correction required

### ✅ Correct Pattern

**What TO Do**:
- Download validators if not present (L027)
- Run ALL 4 validators sequentially
- Fix ALL issues before proceeding
- Complete behavioral validation
- ONLY THEN declare complete

---

## Usage in PROJECT_PLANs

### Standard Placement

Insert this gate **before** the final completion gate:

```
Gate N-2: Execute Migration
    ↓
Gate N-1: Validation (BLOCKING) ← INSERT HERE
    ↓
Gate N: Commit & Complete
```

### Copy-Paste Template

When creating migration PROJECT_PLAN:
1. Copy gate template from this document
2. Renumber gate (N = actual gate number)
3. Keep all deliverables (N.1-N.7)
4. Keep BLOCKING semantics
5. Reference this pattern in "Cross-References"

---

## Validation Checklist Reference

For detailed migration completion criteria, see:
- `docs/patterns/MIGRATION_COMPLETION_CHECKLIST.md`

For step-by-step migration guide, see:
- `docs/FLEET_MIGRATION_GUIDE.md` (Step 7: Validation)

---

## Examples

### Example 1: Single Agent Migration

```markdown
## Gate 3: Validation (BLOCKING)

[Use full template from above, with N=3]

**Context**: Migrating private-example-aget from v2.11 to v2.12
```

### Example 2: Fleet Migration

```markdown
## Gate 2: Pilot Validation (BLOCKING)

**Objective**: Verify all 6 pilot agents pass validation

**Deliverables**:
| # | Deliverable | Verification |
|---|-------------|--------------|
| 2.1 | Download validators to each pilot | 6 pilots have .aget/validation/ |
| 2.2 | Run all 4 validators on each pilot | 24 validator runs (6 × 4) |
| 2.3 | Fix any issues | All validators pass |
| 2.4 | Behavioral validation on each pilot | All 6 pilots functional |

[Rest of template structure same as standard]
```

---

## Metrics

**Effectiveness Indicators**:
- Migration completion error rate < 5%
- Validator pass rate on first run (tracks quality)
- Time to fix validation failures (tracks issue complexity)
- User satisfaction with migration clarity

**Success**: All migrations include this gate, all validators pass before completion

---

## Cross-References

- L376: Premature Completion Declaration (trigger)
- L371: Behavioral vs Structural Migration (pattern basis)
- L027: Validator Download Pattern (precedent)
- MIGRATION_COMPLETION_CHECKLIST.md (detailed checklist)
- FLEET_MIGRATION_GUIDE.md Step 7 (implementation)

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2025-12-26 | 1.0 | Initial pattern created from L376 learning |

---

*PATTERN: Migration Validation Gate (Blocking)*
*Ensures complete validation before migration completion*
*Prevents L376-class premature completion errors*
