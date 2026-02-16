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

## Context for External Fleets

### What is `aget-file-issue`?

A universal skill for filing GitHub issues with proper routing:
- **Problem it solves**: Private fleet agents accidentally filing issues to public repos, leaking internal details
- **What it does**: Routes issues to correct destination, sanitizes content
- **Deploy to**: ALL agents (universal skill)

### What is `ontology/`?

A directory containing vocabulary definitions for your agent's domain:
- **Format**: YAML using SKOS+EARS (standard ontology formats)
- **Purpose**: Defines terms, concepts, and relationships your agent uses
- **Contents**: `ONTOLOGY_{archetype}.yaml` - pre-built for each archetype
- **Why required**: Enables consistent vocabulary across agents

### Archetype Skill Reference

Not all 26 skills apply to every agent. Deploy skills matching your archetype:

| Archetype | Skills | Count |
|-----------|--------|-------|
| supervisor | aget-broadcast-fleet, aget-review-agent, aget-escalate-issue | 3 |
| developer | aget-run-tests, aget-lint-code, aget-review-pr | 3 |
| researcher | aget-search-literature, aget-document-finding | 2 |
| analyst | aget-analyze-data, aget-generate-report | 2 |
| advisor | aget-assess-risk, aget-recommend-action | 2 |
| ... | See template-{archetype}-aget/.claude/skills/ | |

**Plus universal skills** (all agents): aget-file-issue, aget-wake-up, aget-wind-down, etc.

### What is `migration_history`?

A field in `.aget/version.json` tracking upgrade history:
```json
{
  "aget_version": "3.5.0",
  "migration_history": [
    {"from": "3.4.0", "to": "3.5.0", "date": "2026-02-15"}
  ]
}
```
**Update it** when upgrading to maintain audit trail.

---

## Critical Mitigations

These reference internal lessons learned (L-docs). Here's what they mean:

### L582: Skill Extension Preservation

**The problem**: Full skill overwrite destroys legitimate local customizations. One fleet lost custom workflows when skills were blindly copied from template.

**The rule**: If your agent has ADDED features to a skill (not just drifted), those are extensions to PRESERVE.

**BEFORE** overwriting any existing skill:
```bash
diff -rq ".claude/skills/$skill" "template/.claude/skills/$skill"
```
- **If identical**: Safe to overwrite
- **If different**: Review the diff. Is it drift (fix) or extension (preserve)?

### L586: Skill Dependency Validation

**The problem**: Skills reference files (templates, specs, directories) that must exist at runtime. 8/8 skills failed in one fleet because dependencies were missing.

**The tool**: `validate_skill_dependencies.py` checks that all referenced files exist.

**BEFORE** deploying skills:
```bash
# Validate specific skill
python3 ~/path/to/aget/validation/validate_skill_dependencies.py \
  --skill .claude/skills/aget-create-project/

# Validate all skills in agent
python3 ~/path/to/aget/validation/validate_skill_dependencies.py --check
```

**If validation fails**, create the missing dependencies (stubs OK):
- `templates/poc/RESEARCH_PROJECT_PLAN.template.md`
- `specs/CLI_VOCABULARY.md`
- `planning/skill-proposals/INDEX.md`
- `knowledge/patterns/` directory

### L584: Stale Version References

**The problem**: After upgrade, old version numbers remain in files, causing confusion.

**AFTER** upgrading, verify no stale references:
```bash
grep -r "3\.4\.0" . --include="*.yaml" --include="*.json" --include="*.md" \
  | grep -v migration_history
# Expected: No results
```

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
- [SOP_skill_deployment.md](../sops/SOP_skill_deployment.md) - Skill deployment with validation gate
- [verification/INVENTORY.md](../verification/INVENTORY.md) - All verification scripts explained

---

*RELEASE_HANDOFF v3.5.0*
*Per L511/R-REL-019*
