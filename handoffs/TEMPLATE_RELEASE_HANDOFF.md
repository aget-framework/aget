# RELEASE_HANDOFF: v{VERSION}

**Version**: {VERSION}
**Released**: {YYYY-MM-DD}
**Theme**: {Release Theme}

---

## Executive Summary

{One paragraph summary: what changed and why it matters}

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| {Feature 1} | {Who/what affected} | {What to do} |
| {Feature 2} | {Who/what affected} | {What to do} |

### Changed

| Change | Migration |
|--------|-----------|
| {Change 1} | {How to migrate} |

### Breaking Changes

| Change | Migration |
|--------|-----------|
| {Breaking change} | {Required migration steps with commands} |

**Migration for {breaking change}**:
```bash
# Find affected files
{command}

# Update
{command}
```

---

## Upgrade Checklist

### Per Agent

- [ ] Update `.aget/version.json`: `"aget_version": "{VERSION}"`
- [ ] Update `AGENTS.md`: `@aget-version: {VERSION}`
- [ ] Update `migration_history` in version.json
- [ ] {Release-specific step 1}
- [ ] {Release-specific step 2}
- [ ] Validate: `python3 .aget/patterns/session/wake_up.py`

### Fleet-Wide

- [ ] Wave 0: Supervisor first
- [ ] Wave 1: 2-3 simple agents
- [ ] Wave 2: Remaining agents
- [ ] Verify: All agents at v{VERSION}

---

## Context for External Fleets

> **Per R-REL-019-02**: This section explains concepts that may not be obvious to fleets outside the managing organization.

### What is {New Feature/Tool 1}?

{Description of what it is}
- **Problem it solves**: {Why this exists}
- **What it does**: {Brief functional description}
- **Deploy to**: {Which agents/archetypes}

### What is {New Feature/Tool 2}?

{Description}
- **Format**: {If applicable}
- **Purpose**: {Why needed}
- **Contents**: {What's in it}

### Archetype Reference

> **Per R-REL-019-05**: Not all features apply to every agent. Deploy features matching your archetype.

| Archetype | Features/Skills | Count |
|-----------|-----------------|-------|
| supervisor | {list} | {n} |
| worker | {list} | {n} |
| advisor | {list} | {n} |
| ... | See template-{archetype}-aget/ | |

**Plus universal features** (all agents): {list}

### What is {field/concept that may be unfamiliar}?

{Explanation with example}
```json
{
  "example": "value"
}
```
**Update it** when {condition}.

---

## Critical Mitigations

> **Per R-REL-019-04**: L-doc references are explained here, not just labeled.

### {L-doc ID}: {Title}

**The problem**: {What can go wrong without this mitigation}

**The rule**: {What the L-doc teaches}

**BEFORE** {action}:
```bash
{verification command}
```
- **If {condition 1}**: {action}
- **If {condition 2}**: {action}

### {L-doc ID}: {Title}

**The problem**: {Description}

**The tool**: {Tool name and what it does}

**BEFORE** {action}:
```bash
{command with placeholder paths}
# Use: ~/path/to/framework/ (replace with your actual path)

{command}
```

**If validation fails**, {remediation steps}:
- {Step 1}
- {Step 2}

### {L-doc ID}: {Title}

**The problem**: {Description}

**AFTER** {action}, verify:
```bash
{verification command}
# Expected: {expected result}
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

- [CHANGELOG.md](../CHANGELOG.md) - Full v{VERSION} changes
- [UPGRADING.md](../docs/UPGRADING.md) - Migration procedures
- [SOP_fleet_migration.md](../sops/SOP_fleet_migration.md) - Fleet coordination
- {Additional relevant references}

---

*RELEASE_HANDOFF v{VERSION}*
*Per L511/R-REL-019*
*Template: handoffs/TEMPLATE_RELEASE_HANDOFF.md*

---

## Template Usage Notes

> Remove this section when creating an actual release handoff.

**Required sections per CAP-REL-020**:

| Section | Requirement | Required |
|---------|-------------|----------|
| Executive Summary | Theme + key changes | YES |
| What Changed | Added/changed/breaking | YES |
| Context for External Fleets | WHY and WHICH explanations | YES (R-REL-019-02) |
| Critical Mitigations | L-doc explanations with problem/rule/commands | IF L-docs referenced (R-REL-019-04) |
| New Tools | what/when/how/if-fails | IF new tools (R-REL-019-03) |
| Archetype Reference | Feature → archetype mapping | IF archetype features (R-REL-019-05) |
| Pilot Tracking Template | Status table | YES |

**Anti-patterns to avoid (L587)**:

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| Label without lesson | "per L582" | Explain the problem/rule/commands |
| Tool without tutorial | "run validate_xyz.py" | Add what/when/how/if-fails |
| Quantity without mapping | "26 archetype skills" | Table: archetype → skills |
| Action without purpose | "deploy skill X" | Explain what it does and why |
| Path without placeholder | "~/github/aget-framework" | Use "~/path/to/framework" |

**Checklist before publishing**:

- [ ] L-doc references are explained (problem/rule/commands)
- [ ] New tools have what/when/how documentation
- [ ] Archetype features are mapped to specific archetypes
- [ ] Purposes are stated, not just actions
- [ ] Paths use placeholders, not internal values
- [ ] "Would someone outside our team understand this?"
