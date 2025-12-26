# Migration Completion Checklist

**Purpose**: Unambiguous checklist to verify migration completeness. DO NOT declare "migration complete" until all items checked.

**Pattern**: Complete = Structure + Automated Validation + Behavioral Validation

**References**:
- L371: Behavioral vs Structural Migration
- L376: Premature Completion Declaration
- FLEET_MIGRATION_GUIDE.md

---

## Pre-Migration
- [ ] Agent is in working state
- [ ] Git working directory clean
- [ ] Backup/commit point exists
- [ ] Target capabilities identified

## Structural Migration
- [ ] Created manifest.yaml
- [ ] Updated .aget/version.json (aget_version, capabilities[], migration_history)
- [ ] Updated AGENTS.md (@aget-version tag + project context)
- [ ] Created required directories (governance/, planning/, docs/patterns/, sops/)
- [ ] Added .gitignore entries (if needed)

## Validator Setup
- [ ] Downloaded validators to .aget/validation/ (if not present)
- [ ] Verified all 4 validators present:
  - validate_version_consistency.py
  - validate_naming_conventions.py
  - validate_template_manifest.py
  - validate_composition.py

## Automated Validation (BLOCKING)
- [ ] validate_version_consistency.py → ✅ PASS
- [ ] validate_naming_conventions.py → ✅ PASS
- [ ] validate_template_manifest.py → ✅ PASS
- [ ] validate_composition.py → ✅ PASS

**CRITICAL**: If ANY validator fails, STOP here. Fix issues, re-run validators. Do NOT proceed until all pass.

## Edge Cases Audit

Additional structural checks not covered by standard validators:

- [ ] CLAUDE.md is symlink to AGENTS.md
  - Verification: `readlink CLAUDE.md` returns "AGENTS.md"
- [ ] No duplicate entries in migration_history array
  - Verification: `cat .aget/version.json | grep -c "v2.12.0"` returns 1
- [ ] Migration date is valid YYYY-MM-DD format
  - Verification: Date in migration_history matches `date +%Y-%m-%d`
- [ ] Capabilities array exists in version.json (v2.12.0+)
  - Verification: `jq '.capabilities' .aget/version.json` returns array
- [ ] All L-docs follow L###_snake_case.md naming
  - Verification: `ls .aget/evolution/L*.md` shows no violations

## Behavioral Validation
- [ ] Agent wakes up successfully
- [ ] Version displays correctly (target version, not old version)
- [ ] Capabilities functional:
  - [ ] memory-management (can access .aget/evolution/, knowledge/)
  - [ ] domain-knowledge (can access governance/, domain docs)
  - [ ] collaboration (can access fleet registry - if applicable)
  - [ ] structured-outputs (output formats work)
  - [ ] org-kb (can access organizational knowledge - if applicable)
- [ ] No regressions in existing functionality
- [ ] Session patterns work (wake up, wind down)

## Final Checks
- [ ] KB reviewed for migration patterns (followed precedents?)
- [ ] All PENDING items resolved (no open questions)
- [ ] Git status clean (ready to commit)
- [ ] Migration commit message prepared

---

## Completion Criteria

✅ **Migration Complete** ONLY when:
1. ALL automated validators pass
2. ALL behavioral tests pass
3. NO regressions detected
4. Git ready to commit

❌ **NOT Complete** if:
- Any validator shows FAIL or WARN
- Any behavioral test fails
- Any PENDING items remain
- Unable to commit cleanly

---

## Anti-Patterns (L376)

❌ **Premature Completion**:
- Declaring complete after behavioral validation only
- Skipping automated validators
- Assuming validators unavailable without checking
- Marking items PENDING instead of completing them

✅ **Correct Pattern**:
- Download validators if not present (L027)
- Run ALL validators, fix ALL issues
- Complete behavioral validation
- ONLY THEN declare complete

---

## Usage

1. Copy this checklist to migration session notes
2. Check items as completed
3. Do NOT skip items
4. Do NOT declare complete until ALL items checked
5. If blocked, escalate (don't mark PENDING and continue)

---

*Pattern: Migration Completion Checklist*
*Created: 2025-12-26*
*Source: L376 (Premature Completion Declaration)*
