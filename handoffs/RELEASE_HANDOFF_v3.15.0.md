# Release Handoff: v3.15.0

**Date**: 2026-04-25
**Theme**: Two-Level Model Coherence + Security Hardening + Weekly Cadence Formalization
**From**: aget-framework manager
**To**: Fleet supervisors

---

## Release Summary

v3.15 is the **first breaking release in the 3.x minor cycle**. Two breaking changes (BC-001, BC-002) affect agents reading `version.json` with old field names or invoking skills with `--fix`. Migration time estimate: **30–60 min per agent** (vs 15–20 min for non-breaking releases).

The release also introduces the first dedicated security spec (AGET_SECURITY_SPEC v0.2), budget grammar formalization (AGET_BUDGET_GRAMMAR_SPEC v0.2), and formalizes the weekly Saturday release cadence as a durable policy (POL-REL-001).

### Key Changes

- **`/aget-enhance-health` (SKILL-049 v1.0.0)**: 7-phase health remediation. Pairs with `/aget-check-health` (detect-only) as the canonical `check → enhance` pipeline. Deploys to all 13 templates.
- **AGET_SECURITY_SPEC v0.2**: 8 CAP-SEC contracts — 4 outside-threat (boundary enforcement, input validation, information disclosure, dependency integrity) + 4 within-threat (authority overstep, scope creep, output contamination, autonomous action bounds). First dedicated security spec.
- **AGET_BUDGET_GRAMMAR_SPEC v0.2**: 4 CAP-BGG contracts formalizing budget grammar used across skills and session protocols.
- **CAP-REL-029**: Pre-release gate checklist as testable EARS requirement.
- **POL-REL-001**: Weekly Saturday release policy formalized from 6-release empirical record (v3.10–v3.15 all landed on consecutive Saturdays).
- **ADR-022**: Breaking-change policy ratified — codifies Q3=(b) interpretation (honor stated deprecation timelines; only BC-001 and BC-002 accelerated).
- **`verification/validate_archetype_skills.py`**: Promoted to canonical `aget/verification/`. Mechanically enforces CAP-TPL-016-04 universal-skill mandate.
- **PIR infrastructure**: SOP Phase 7.1.5 — Post-Implementation Review as a blocking release gate.

### Breaking Changes

See `docs/BREAKING_CHANGES_v3.15.md` for complete migration guide and grep recipes.

- **BC-001 — `version.json` old field names removed**: 19 fields renamed in v3.14 (e.g. `agent_name` → `aget_agent_name`, `domain` → `aget_domain`, `portfolio` → `aget_portfolio`). Dual-read backward-compat shim removed in v3.15. Any script, skill, or agent code reading old names breaks at upgrade.
- **BC-002 — `--fix` flag surfaces removed**: Flag documented across 13+ SKILL.md files since 2026-02-10 but never implemented (decorative). Removed in this release. Any invocation with `--fix` will error. Replacement: `/aget-enhance-health` (SKILL-049).

### Deprecations

Per ADR-022 interpretation (b) — the following remain on their POL-DEP-001 schedule (NOT accelerated):

| Item | Deprecated in | Scheduled removal | v3.15 behavior |
|------|:-------------:|:-----------------:|----------------|
| `scripts/wake_up.py` shim | v3.14 | v3.16 | Active through v3.15 |
| `scripts/wind_down.py` shim | v3.14 | v3.16 | Active through v3.15 |
| `scripts/wake_up_ext.py` shim | v3.14 | v3.16 | Active through v3.15 |
| `scripts/wind_down_ext.py` shim | v3.14 | v3.16 | Active through v3.15 |

New in v3.15:
- **`/aget-check-health --fix` flag** (DEP-FIX-FLAG-001): Removed same release per R-DEP-011 grace-period exemption. Replacement: `/aget-enhance-health`.

---

## Upgrade Guide

### Before Upgrading — Pre-Flight Checks

```bash
# 1. Verify current version
python3 -c "import json; v=json.load(open('.aget/version.json')); print(v.get('aget_version','MISSING'))"
# Expected: 3.14.0 or 3.14.1

# 2. BC-001: Check for aget_-prefixed field name reads in scripts/skills
# (version.json keys are NOT renamed — shim was removed; code reading new names breaks)
grep -rE '"(aget_agent_name|aget_domain|aget_portfolio|aget_managed_by|aget_manages|aget_instance_type|aget_archetype|aget_specialization|aget_template|aget_identity_file|aget_intelligence_enabled|aget_collaboration_enabled|aget_capabilities|aget_patterns|aget_knowledge_inheritance)"' scripts/ .claude/ 2>/dev/null
# If matches found: update to use original key names (agent_name, domain, etc.) — the JSON was not renamed

# 3. BC-002: Check for --fix flag usage
grep -r -- '--fix' .claude/skills/ scripts/ 2>/dev/null
# If matches found: replace with /aget-enhance-health invocation
```

### For Each Fleet Agent

| Step | Obligation | Action | V-Test Command | Expected |
|------|-----------|--------|---------------|----------|
| 1 | MUST | Update `.aget/version.json`: set `aget_version` to `"3.15.0"` | `jq -r .aget_version .aget/version.json` | `"3.15.0"` |
| 2 | MUST | Update `AGENTS.md` header: `@aget-version: 3.15.0` | `grep '@aget-version: 3.15.0' AGENTS.md` | Match |
| 3 | MUST | Verify no old `version.json` field names in agent code | BC-001 grep above | 0 matches |
| 4 | MUST | Verify no `--fix` flag usage in skills/scripts | BC-002 grep above | 0 matches |
| 5 | SHOULD | Deploy `/aget-enhance-health` (SKILL-049 v1.0.0) from `template-worker-aget` | `ls .claude/skills/aget-enhance-health/SKILL.md` | Exists |
| 6 | SHOULD | Run `python3 scripts/health_check.py` | Exit code | 0 |
| 7 | SHOULD | Run contract tests if present: `python3 -m pytest tests/ -q` | All pass | No failures |

### Skill Deployment (Step 5 Detail)

**New skill** (copy from `template-worker-aget/.claude/skills/`):
- `aget-enhance-health` — 7-phase health remediation (SKILL-049 v1.0.0)

**Upgraded skill**:
- `aget-check-health` v1.0.0 → v1.1.0 — detect-only scope declared; SC-007 (`--fix`) removed

### End-State Validation

```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='3.15.0' else 'FAIL: '+v['aget_version'])"
```

---

## Pilot Tracking

| Fleet | Supervisor | Status | Date | Notes |
|-------|-----------|:------:|------|-------|
| Main | fleet supervisor | Pending | — | BC-001/BC-002 pre-flight required |

---

## Known Issues

- `validate_archetype_skills.py` reports 2/14 templates conformant — 10 templates missing 15 universal skills each. This is a known pre-existing gap (stalled migration). Non-blocking for v3.15 upgrade; will be addressed in v3.16 universal-skills migration push (target 2026-05-02).
- Health check: 2 L0-theater gaps (Spec portfolio + V-test portfolio) — pre-existing, not introduced in v3.15. Accepted per L632 precedent.

---

*RELEASE_HANDOFF_v3.15.0.md*
*Created: 2026-04-25*
*Created by aget-framework manager*
