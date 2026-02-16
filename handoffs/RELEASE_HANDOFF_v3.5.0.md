# RELEASE_HANDOFF: v3.5.0

**Version**: 3.5.0
**Released**: 2026-02-14
**Theme**: Archetype Customization + Issue Governance

---

## Executive Summary

v3.5.0 adds 26 archetype-specific skills, universal issue governance (L520), and ontology integration. One breaking change: `validation/` → `verification/` directory rename.

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| 26 archetype skills | 2-3 skills per archetype | Deploy from `template-{archetype}-aget/.claude/skills/` |
| `aget-file-issue` skill | Universal issue filing with L520 compliance | Deploy from `aget/.claude/skills/aget-file-issue` |
| `ontology/` directory | SKOS+EARS format ontologies | Create from `template-{archetype}-aget/ontology/` |

### Breaking Change

| Change | Migration |
|--------|-----------|
| `validation/` → `verification/` | Update import paths (see below) |

**Migration for validation/ rename**:
```bash
# Find affected files
grep -r "from validation\." . --include="*.py"
grep -r "validation/" . --include="*.py" --include="*.md"

# Update imports
# OLD: from validation.aget_verify_conformance import ...
# NEW: from verification.aget_verify_conformance import ...

# Note: Both directories exist during transition. validation/ will be removed in v3.6.0.
```

---

## Upgrade Checklist

### Per Agent

- [ ] Update `.aget/version.json`: `"aget_version": "3.5.0"`
- [ ] Update `AGENTS.md`: `@aget-version: 3.5.0`
- [ ] Create `ontology/` directory (copy from matching template)
- [ ] Deploy `aget-file-issue` skill
- [ ] Deploy archetype-specific skills (diff existing skills first per L582)
- [ ] Validate: `python3 .aget/patterns/session/wake_up.py`

### Fleet-Wide

- [ ] Wave 0: Supervisor first
- [ ] Wave 1: 2-3 simple agents
- [ ] Wave 2: Remaining agents
- [ ] Verify: All agents at v3.5.0

---

## Critical Mitigations

### L582: Skill Extension Preservation

**BEFORE** overwriting any existing skill:
```bash
diff -rq ".claude/skills/$skill" "template/.claude/skills/$skill"
```
If differences exist, review before overwriting. Preserve local extensions.

### L586: Skill Dependency Validation

**BEFORE** deploying skills:
```bash
python3 aget/validation/validate_skill_dependencies.py --check
```
Missing dependencies cause runtime failures.

---

## Pilot Tracking Template

| Agent | Status | Blocker | Owner |
|-------|--------|---------|-------|
| Supervisor | | | |
| Agent 1 | | | |
| Agent 2 | | | |
| ... | | | |

---

## References

- [CHANGELOG.md](../CHANGELOG.md) - Full v3.5.0 changes
- [UPGRADING.md](../docs/UPGRADING.md) - Migration procedures
- [SOP_fleet_migration.md](../sops/SOP_fleet_migration.md) - Fleet coordination

---

*RELEASE_HANDOFF v3.5.0*
*Per L511/R-REL-019*
