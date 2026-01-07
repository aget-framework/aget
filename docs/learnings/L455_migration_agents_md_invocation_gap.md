# L455: Migration AGENTS.md Invocation Gap

## Problem

When migrating agents to a new AGET version, session scripts are often deployed (e.g., `wake_up.py`, `wind_down.py`, `aget_housekeeping_protocol.py`) but AGENTS.md training instructions retain stale CLI invocations from the previous version.

**Example**: Agent migrated to v3.1 with new `--json` flag support, but AGENTS.md still documents:
```
Run: python3 scripts/aget_housekeeping_protocol.py sanity-check  # v2.x pattern - BROKEN
```

Instead of:
```
Run: python3 scripts/aget_housekeeping_protocol.py --json        # v3.1+ pattern - CORRECT
```

**Impact**:
- First session post-migration fails when following AGENTS.md instructions
- Agent attempts invalid commands (e.g., `sanity-check` subcommand that no longer exists)
- User confusion: "I followed the instructions but it does not work"
- ~2-3 minutes per incident to diagnose and fix

## Learning

**Migration must update AGENTS.md invocations, not just version numbers and script files.**

Every migration should include:
1. Deploy new scripts
2. Update version.json
3. **Update AGENTS.md CLI patterns** (this step was missing)
4. Run V-MIG-AGENTS verification tests

## V-MIG-AGENTS Tests

Three verification tests to run before committing a migration:

```bash
AGENT_PATH="/path/to/agent"

# V-MIG-AGENTS.1: No stale CLI patterns
# Checks for deprecated subcommands that no longer exist
! grep -q "sanity-check" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: stale sanity-check"

# V-MIG-AGENTS.2: v3.1+ invocations documented
# Checks that new CLI flags are present in documentation
grep -q "\-\-json\|\-\-dir" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: v3.1 flags missing"

# V-MIG-AGENTS.3: Documented commands actually work
# Tests that the commands in AGENTS.md are functional
cd $AGENT_PATH && python3 scripts/aget_housekeeping_protocol.py --json > /dev/null && echo "PASS" || echo "FAIL"
```

## Protocol

### During Migration

1. After deploying session scripts, before committing:
   - Run V-MIG-AGENTS.1: Check for stale patterns
   - Run V-MIG-AGENTS.2: Check for v3.1+ flags
   - Run V-MIG-AGENTS.3: Verify commands work
2. If any test fails, update AGENTS.md before commit
3. Batch verify for fleet migrations

### Correct v3.1 Invocations

| Script | Correct Invocation |
|--------|-------------------|
| wake_up.py | `python3 scripts/wake_up.py --json` |
| wind_down.py | `python3 scripts/wind_down.py --json --notes "notes"` |
| aget_housekeeping_protocol.py | `python3 scripts/aget_housekeeping_protocol.py --json` |

### AGENTS.md Sections to Update

When migrating to v3.1+, update these sections:
- **Housekeeping Commands** / **Sanity Check**: Remove `sanity-check` subcommand
- **Wake Up Protocol**: Add `wake_up.py --json` reference
- **Wind Down Protocol**: Replace `wind_down_checks.sh` with `wind_down.py`
- **Session Management Protocols**: Update all script references

## Evidence

**Discovery**: During fleet migration to v3.2.1

**Observed Violation Rate**: ~10-15% of agents across multiple fleets

**Pattern**: V-MIG-AGENTS tests catch violations before commit when applied consistently. Zero regressions deployed when tests are run.

## Integration Points

- **FLEET_MIGRATION_GUIDE_v3.md**: References this learning in "AGENTS.md Invocation Verification" section
- **SOP_fleet_migration.md**: V-MIG-AGENTS tests in Phase 1 gates
- **Pre-commit checklist**: Add V-MIG-AGENTS tests
- **Migration script**: Consider auto-updating AGENTS.md patterns

## Anti-Patterns

| Anti-Pattern | Description | Fix |
|--------------|-------------|-----|
| Version-only migration | Bump version number without updating CLI documentation | Run V-MIG-AGENTS.2 |
| Script-only deployment | Copy new scripts but leave stale instructions | Run V-MIG-AGENTS.1 |
| Skip verification | Assume AGENTS.md is correct without testing | Run V-MIG-AGENTS.3 |

## Impact

| Metric | Before L455 | After L455 |
|--------|-------------|------------|
| Stale invocation rate | Unknown | ~10-15% (detected) |
| Post-migration failures | Common | 0 (with V-tests) |
| Detection method | User reports | Automated V-tests |

## Related Learnings

- L373: Version Number vs Feature Parity
- L457: Cross-Machine Pre-Flight

---

*Framework learning for AGET migration process*
*Referenced by: FLEET_MIGRATION_GUIDE_v3.md, SOP_fleet_migration.md*
