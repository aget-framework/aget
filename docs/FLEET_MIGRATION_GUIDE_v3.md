# Fleet Instance_Migration Guide v3.0

**Version**: 1.0.0
**Date**: 2025-12-28
**Owner**: aget-framework
**Implements**: CAP-MIG-001 (Instance_Migration), CAP-MIG-015 (Behavioral_Validation)
**Location**: `aget/docs/FLEET_MIGRATION_GUIDE_v3.md`

---

## Purpose

Supervisor guide for migrating agent fleets from v2.x to v3.0 5D Composition Architecture.

---

## Prerequisites

```bash
# Sync framework (required before migration)
cd ~/github/aget-framework/aget
git pull origin main

# Verify version (9903984 or later)
git log --oneline -1
```

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **AGET_MIGRATION_SPEC.md** | `aget/specs/` | CAP-MIG-* requirements |
| **AGET_INSTANCE_SPEC.md** | `aget/specs/` | Instance structure requirements |
| **AGET_SOP_SPEC.md** | `aget/specs/` | SOP vocabulary requirements |
| **INVENTORY.md** | `aget/validation/` | All validators with usage |
| **migrate_instance_to_v3.py** | `aget/scripts/` | Migration automation |

---

## Migration Script

### Single Agent

```bash
python3 ~/github/aget-framework/aget/scripts/migrate_instance_to_v3.py /path/to/agent \
  --archetype <archetype> \
  --specialization <specialization> \
  --north-star "Agent purpose statement" \
  --execute
```

### Archetypes

| Archetype | Use For |
|-----------|---------|
| `supervisor` | Fleet coordination agents |
| `advisor` | Strategic guidance agents |
| `consultant` | Domain expertise agents |
| `developer` | Code/product agents |
| `operator` | Operations/infrastructure agents |
| `worker` | Task execution agents |
| `analyst` | Data analysis agents |
| `researcher` | Research/investigation agents |
| `reviewer` | Review/audit agents |
| `spec-engineer` | Specification agents |
| `architect` | Architecture/design agents |
| `executive` | Executive function agents |

### Dry-Run First

```bash
# Preview changes (no --execute)
python3 ~/github/aget-framework/aget/scripts/migrate_instance_to_v3.py /path/to/agent \
  --archetype advisor \
  --specialization domain-advisor \
  --north-star "Purpose"

# Review output, then add --execute
```

---

## Post-Migration Validation Suite

Run **all 5 validators** per CAP-MIG-015:

```bash
AGENT_PATH="/path/to/agent"

# 1. Structural Validation (24 checks)
python3 ~/github/aget-framework/aget/validation/validate_template_instance.py $AGENT_PATH
# Expected: 24/24 PASS

# 2. Naming Conventions
python3 ~/github/aget-framework/aget/validation/validate_naming_conventions.py $AGENT_PATH
# Expected: ✅ PASS (pre-existing violations acceptable)

# 3. Version Consistency
python3 ~/github/aget-framework/aget/validation/validate_version_consistency.py $AGENT_PATH
# Expected: ✅ PASS

# 4. Legacy File Audit (L376)
find $AGENT_PATH/.aget -name "agent_manifest.yaml" 2>/dev/null
# Expected: No output (no legacy files)

# 5. Contract Tests (if available)
[ -d "$AGENT_PATH/tests" ] && python3 -m pytest $AGENT_PATH/tests/test_identity_contract.py -v
# Expected: All tests pass
```

---

## Batch Validation (Fleet)

```bash
# Main portfolio
for agent in ~/github/private-*-aget ~/github/private-*-AGET; do
  echo "=== $(basename $agent) ==="
  python3 ~/github/aget-framework/aget/validation/validate_template_instance.py "$agent" 2>/dev/null | tail -3
  python3 ~/github/aget-framework/aget/validation/validate_version_consistency.py "$agent" 2>/dev/null | tail -1
done

# Other portfolios (adjust paths)
for agent in ~/github/GM-CCB/private-* ~/github/GM-RKB/private-*; do
  echo "=== $(basename $agent) ==="
  python3 ~/github/aget-framework/aget/validation/validate_template_instance.py "$agent" 2>/dev/null | tail -3
done
```

---

## Troubleshooting

### "identity.json not found"

```bash
cat > $AGENT_PATH/.aget/identity.json << 'EOF'
{
  "name": "agent-name",
  "north_star": "Agent purpose"
}
EOF
```

### "governance/ not found"

```bash
mkdir -p $AGENT_PATH/governance
touch $AGENT_PATH/governance/{CHARTER,MISSION,SCOPE_BOUNDARIES}.md
```

### Version mismatch after migration

```bash
# Check AGENTS.md has @aget-version tag
grep "@aget-version" $AGENT_PATH/AGENTS.md
# Should show: @aget-version: 3.0.0-beta.3 (or later)

# If missing, script should have added it. Manual fix:
# Add "@aget-version: 3.0.0-beta.3" as line 3 of AGENTS.md
```

### Legacy agent_manifest.yaml found

```bash
# Archive and remove (L376)
mkdir -p $AGENT_PATH/.aget/archive
mv $AGENT_PATH/.aget/agent_manifest.yaml $AGENT_PATH/.aget/archive/
```

---

## Completion Checklist

- [ ] Framework synced to latest (`git pull origin main`)
- [ ] Each agent migrated with script (`--execute`)
- [ ] Each agent passes Structural_Validation (24/24)
- [ ] Each agent passes Version_Consistency
- [ ] No legacy `agent_manifest.yaml` files remain
- [ ] Commit migrations per agent

---

## Known Issues

| Issue | Classification | Action |
|-------|---------------|--------|
| Naming convention violations | Pre-existing debt | P3, remediate later |
| Legacy agents (no governance) | Excluded | No migration needed |

---

## References

- L395: Instance v3.0 Migration Pattern
- L400: Conceptual vs Structural Migration
- L376: Legacy File Version Sync
- L377: Validation Suite Orchestration Gap
- CAP-MIG-014: Legacy File Handling
- CAP-MIG-015: Behavioral_Validation Requirement

---

*FLEET_MIGRATION_GUIDE_v3.md — Supervisor guide for v3.0 fleet migration*
*Syncs to all machines via `git pull origin main`*
