# RELEASE_HANDOFF: v3.8.0

**Version**: 3.8.0
**Released**: 2026-03-08
**Theme**: Governance Maturation
**Breaking Changes**: None

---

## Receiving Agent Governance Checklist (BLOCKING)

**STOP**: Before executing any upgrade steps, complete this checklist:

- [ ] Located local upgrade SOP (e.g., SOP_point_upgrade.md)
- [ ] Created PROJECT_PLAN for this upgrade OR referenced existing gate
- [ ] Gate discipline acknowledged (L42)
- [ ] Principal approval obtained if required by local governance

**Governance Reference**: _[Your upgrade SOP path]_

**Warning**: Proceeding without completing this checklist is a governance violation (L562).

---

## Executive Summary

v3.8.0 is a governance maturation release — codifying principles, closing automation gaps, and adding structural enforcement to the framework. It introduces meta-principles (what rules govern the rules?), integrates Structural Aesthetics as a design principle, deploys skill customization detection for safe upgrades, and adds a PROJECT_PLAN existence validator to prevent the prompt-as-plan anti-pattern. All 12 templates updated with governance patterns and .claude/ scaffolding. No breaking changes.

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| GOVERNANCE_PRINCIPLES.md v1.1.0 | Framework-level — 6 Tier 1 + 5 Tier 2 meta-principles | No action — framework governance document |
| `aget-enhance-spec` skill (SKILL-041) | All agents — 7-phase specification enhancement lifecycle | Deployed universally; skill count 15→16 |
| `aget-expand-ontology` skill | Optional — SKOS ontology expansion with evidence-backed concepts | Acquire when >10 vocab entries from domain work |
| `scripts/validate_project_plan.py` | All agents — prevents prompt-as-plan anti-pattern (R-GOV-PLAN-001/002/003) | No action — available in scripts/ |
| `.aget/patterns/upgrade/pre_sync_check.py` | All agents — skill customization detection before upgrade | Run before skill sync (see Upgrade Checklist) |
| DEPLOYMENT_SPEC_v3.8.0.yaml | Framework — target state specification for fleet deployment | Reference during upgrade verification |
| TEMPLATE_AGENTS_MD_SPEC v1.0.0 | Framework — governance patterns for AGENTS.md | No action — governs template structure |

### Changed

| Change | Migration |
|--------|-----------|
| Structural Aesthetics added as design principle #3 | Auto-propagated via template update (DESIGN_PHILOSOPHY, MISSION) |
| AGENTS.md governance patterns (12 templates) | Auto-propagated — .claude/ scaffolding, skill routing tables |
| identity.json: `type` field added | Auto-propagated via template update |
| SOP headers: CAP-SOP-001 compliance | Auto-propagated — Status field, section naming |
| Universal skill count: 15→16 (+aget-enhance-spec) | Deploy aget-enhance-spec skill directory |
| Session scripts: 4 scripts migrated to scripts/ | Auto-propagated — study_up.py, aget_housekeeping_protocol.py now in scripts/ |
| Notification validation added to post_release_validation.py | No action — framework tooling |
| codemeta.json + CITATION.cff version corrected (was 3.6.0) | Auto-propagated |

### Breaking Changes

None. v3.8.0 is fully backward compatible with v3.7.x.

---

## Upgrade Checklist

### Per Agent

1. **Run pre-sync check** (NEW — detect skill customizations before overwriting):
   ```bash
   python3 .aget/patterns/upgrade/pre_sync_check.py \
     --baseline ~/path/to/template-{archetype}-aget/.claude/skills/ \
     --instance .claude/skills/
   ```
   Review output: `conflict` = review manually, `instance-only` = preserve, `clean` = safe to overwrite.

2. **Update `.aget/version.json`**:
   ```json
   {
     "aget_version": "3.8.0",
     "updated": "2026-03-08"
   }
   ```
   Add migration_history entry:
   ```
   "v3.7.0 -> v3.8.0: 2026-03-08 (Governance Maturation - principle codification, deliverable conformance)"
   ```

3. **Update `AGENTS.md` header**:
   ```markdown
   @aget-version: 3.8.0
   ```

4. **Deploy `aget-enhance-spec` skill** (new universal skill):
   ```bash
   # Copy from template (after pre_sync_check confirms safe)
   cp -r ~/path/to/template-{archetype}-aget/.claude/skills/aget-enhance-spec .claude/skills/
   ```

5. **Validate**:
   ```bash
   python3 scripts/wake_up.py
   # Expected: Shows v3.8.0
   ```

### Fleet-Wide

- [ ] Wave 0: Supervisor first (validate new governance documents)
- [ ] Wave 1: 2-3 simple agents (test pre_sync_check, deploy aget-enhance-spec)
- [ ] Wave 2: Remaining agents
- [ ] Verify: All agents at v3.8.0

---

## Context for External Fleets

> **Per R-REL-019-02**: This section explains concepts that may not be obvious to fleets outside the managing organization.

### What are Meta-Principles?

GOVERNANCE_PRINCIPLES.md introduces a fourth governance principle category: meta-principles answer "what rules govern the rules?" These are framework-level governance documents — individual agents don't need to deploy them, but they inform how governance evolves.

**6 Tier 1 meta-principles** (MP-0 through MP-5):
- MP-0: Rules Exist To Be Changed
- MP-1: Spec-First
- MP-2: Evidence Over Authority
- MP-3: Cross-Check Across Agents
- MP-4: Proportional Governance
- MP-5: Infrastructure Over Memory

**5 Tier 2 meta-principles**: Advisory-level guidance for governance evolution.

### What is Structural Aesthetics?

A new design principle (#3 in DESIGN_PHILOSOPHY.md and MISSION.md):

> "Attend to structural aesthetics. Beauty signals health; ugliness signals problems worth investigating. Not all ugliness is failure — some is the cost of evolution."

This principle encourages agents to treat visual/structural quality as a diagnostic signal — messy artifacts often indicate underlying issues worth investigating.

### What is pre_sync_check.py?

A new upgrade safety tool that prevents silent customization loss during version upgrades.

- **Problem it solves**: When upgrading skills from templates, agents with customized SKILL.md files risk having customizations overwritten
- **What it does**: Compares agent's skill files against template baseline, classifies each as `clean` (safe to overwrite), `conflict` (needs manual merge), or `instance-only` (agent-specific, preserve)
- **Deploy to**: All agents — run before every upgrade
- **When to use**: Step 1 of the Upgrade Checklist

### What is validate_project_plan.py?

A governance tool that prevents the "prompt-as-plan" anti-pattern (L340) — executing significant work without a formal PROJECT_PLAN.

- **Problem it solves**: Agents executing significant work using only prompt instructions, without formal plans. This bypasses gate discipline and principal review.
- **What it does**: Verifies that a PROJECT_PLAN file exists before allowing work to begin
- **Deploy to**: All agents — available in scripts/

### Archetype Reference

> **Per R-REL-019-05**: Not all features apply to every agent.

| Archetype | v3.8.0-Specific Changes | Action |
|-----------|------------------------|--------|
| All archetypes | +1 universal skill (aget-enhance-spec), governance patterns in AGENTS.md, .claude/ scaffolding | Deploy aget-enhance-spec + merge template changes |

**Universal changes** (all agents): aget-enhance-spec deployment, `@aget-version: 3.8.0`, migration_history entry, AGENTS.md governance patterns.

---

## Critical Mitigations

> **Per R-REL-019-04**: L-doc references are explained here, not just labeled.

### L629: Skill Customization Risk

**The problem**: Upgrading skills from templates silently overwrites agent-specific customizations. The framework had no detection mechanism.

**The rule**: Always run `pre_sync_check.py` before syncing skills from templates. Classify each skill as clean/conflict/instance-only.

**BEFORE upgrading skills**:
```bash
python3 .aget/patterns/upgrade/pre_sync_check.py \
  --baseline ~/path/to/framework/template-{archetype}-aget/.claude/skills/ \
  --instance .claude/skills/
# Review: 'conflict' items need manual merge
# 'instance-only' items should be preserved
# 'clean' items are safe to overwrite
```

### L340: Prompt-as-Plan Anti-Pattern

**The problem**: Agents executing significant work (like version upgrades) using only a prompt instruction, without creating a formal PROJECT_PLAN. This bypasses gate discipline and principal review.

**The rule**: Every significant task requires a PROJECT_PLAN with gates, V-tests, and principal checkpoints.

**BEFORE starting any upgrade**:
```bash
python3 scripts/validate_project_plan.py --action upgrade
# Expected: PASS — PROJECT_PLAN exists for this work
```

### L440: Manager Migration Verification

**The problem**: Upgrading managed repos before the manager itself causes version inconsistency.

**The rule**: Managing agent updates its own version BEFORE updating managed repos (R-REL-006).

**BEFORE upgrading fleet agents**:
```bash
python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])"
# Expected: 3.8.0
```
- **If < 3.8.0**: Upgrade supervisor first
- **If 3.8.0**: Proceed with fleet

---

## v3.7.0 Observation Status

These observations from the v3.7.0 upgrade cycle:

| # | v3.7.0 Observation | v3.8.0 Status |
|---|-------------------|---------------|
| 1 | Skill customization detection was manual-only (L629) | **Resolved** — pre_sync_check.py deployed (CAP-DEP-010/011/012) |
| 2 | Prompt-as-plan anti-pattern (L340) | **Resolved** — validate_project_plan.py deployed (R-GOV-PLAN-001/002/003) |
| 3 | Session scripts at deprecated path | **Partially resolved** — 4 scripts migrated to scripts/ |
| 4 | AGENTS.md version stuck at 3.6.0 | **Resolved** — fixed to 3.8.0 (version_bump.py enhancement candidate for v3.9.0) |

---

## Pilot Tracking Template

| Agent | Portfolio | Archetype | Status | Date | Notes |
|-------|-----------|-----------|--------|------|-------|
| Supervisor | | supervisor | | | Wave 0 — validate governance docs |
| | | | | | Wave 1 pilot |
| | | | | | Wave 1 pilot |
| | | | | | Wave 2 |

---

## Smoke Test Checklist

1. [ ] `wake_up.py` shows v3.8.0
2. [ ] `sanity_check.py` passes 9/9
3. [ ] `aget-enhance-spec` skill present in `.claude/skills/`
4. [ ] AGENTS.md shows `@aget-version: 3.8.0`
5. [ ] `pre_sync_check.py` runs without errors
6. [ ] Conformance report shows CONFORMANT at deep depth

---

## References

- [CHANGELOG.md](../CHANGELOG.md) - Full v3.8.0 changes
- [UPGRADING.md](../docs/UPGRADING.md) - Migration procedures
- [SOP_fleet_migration.md](../sops/SOP_fleet_migration.md) - Fleet coordination
- [DEPLOYMENT_SPEC_v3.8.0.yaml](../DEPLOYMENT_SPEC_v3.8.0.yaml) - Target state specification

---

*RELEASE_HANDOFF_v3.8.0.md*
*Generated: 2026-03-08*
*Per L511/R-REL-019*
