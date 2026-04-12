# Release Handoff: v3.13.0

**Date**: 2026-04-12
**Theme**: Operational Maturation & Fleet Automation
**From**: aget-framework manager
**To**: Fleet supervisors

---

## Release Summary

v3.13.0 front-loads self-consuming infrastructure into early gates, introduces the Release Delivery Triad for multi-perspective quality assessment, and adds 8 new skills (24→31). Key infrastructure: `validate_release_gate.py` (structural exit-code enforcement) and `fleet_upgrade.py` (single-script migration).

### Key Changes

- **validate_release_gate.py**: Orchestrates 7 validators, gates on exit codes (L784 fix)
- **fleet_upgrade.py**: Single-script fleet migration (25-40 prompts → ≤5)
- **Release Delivery Triad v0.2.0**: Builder/Spec Auditor/Critic skills
- **8 new skills**: promote-issue, describe-session, propose-actions, create-rubric, check-initiative, process-observation, open-session, check-facts
- **Skill Telemetry**: Mandatory Requirements section + invocation logger
- **3 new specs**: Health Check Orchestration, Wind-Down Display, Governed Discourse Boundary

### Breaking Changes

None. All changes are additive.

### Deprecations

None new in this release.

**Deployment Spec**: [`specs/DEPLOYMENT_SPEC_v3.13.0.yaml`](../specs/DEPLOYMENT_SPEC_v3.13.0.yaml) — authoritative target state with skill conflict resolution guide.

---

## Upgrade Guide

### For Each Fleet Agent

| Step | Obligation | Action | V-Test Command | Expected |
|------|-----------|--------|---------------|----------|
| 1 | MUST | Update `.aget/version.json`: set `aget_version` to "3.13.0" | `jq -r .aget_version .aget/version.json` | "3.13.0" |
| 2 | MUST | Update `AGENTS.md` header: `@aget-version: 3.13.0` | `grep '@aget-version: 3.13.0' AGENTS.md` | Match |
| 3 | SHOULD | Deploy 13 new/upgraded skills from `template-worker-aget/.claude/skills/` | `ls .claude/skills/aget-check-facts/SKILL.md` | Exists |
| 4 | SHOULD | Run `python3 scripts/health_check.py` | Exit code | 0 |

### Skill Deployment (Step 3 Detail)

**Canonical source**: `template-worker-aget/.claude/skills/` (31 skills total)

**8 new skills** (copy directory from template if agent doesn't have it):
`aget-promote-issue`, `aget-describe-session`, `aget-propose-actions`, `aget-create-rubric`, `aget-check-initiative`, `aget-process-observation`, `aget-open-session`, `aget-check-facts`

**3 upgraded skills** (replace with template version):
`aget-release-build` (v0.2.0), `aget-release-audit-specs` (v0.2.0), `aget-release-critique` (v0.2.0)

**Conflict resolution**: If an agent has an organic (locally-modified) version of a skill, compare with the template version. If template is a superset, adopt it. If organic has domain-specific additions, merge. See DEPLOYMENT_SPEC `conflict_resolution_guide` for details.

### End-State Validation

```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='3.13.0' else 'FAIL: '+v['aget_version'])"
```

---

## Pilot Tracking

| Fleet | Supervisor | Status | Date | Notes |
|-------|-----------|:------:|------|-------|
| Main | fleet supervisor | **COMPLETE** | 2026-04-12 | 34/34 upgraded + hotfix + baseline gap fix. 31 skills/agent. |
| WorkCo | legalon-supervisor | Pending | — | See "Lessons from Main Fleet" below |

---

## Lessons from Main Fleet Upgrade

The main fleet upgrade discovered 3 issues that were fixed before completion. **WorkCo should incorporate these from the start:**

### 1. Full Baseline Reconciliation (not just delta)

The DEPLOYMENT_SPEC lists 11 new/upgraded skills, but the template has 31 total. Compare your agent's full skill set against the template to catch any missing baseline skills:

```bash
# Show skills in template but missing from your agent
comm -23 <(ls ~/github/aget-framework/template-worker-aget/.claude/skills/ | sort) <(ls .claude/skills/ | sort)
```

Deploy anything missing — don't rely only on the DEPLOYMENT_SPEC's "new skills" list.

### 2. Use `\cp` or `cat >` for file overwrites

macOS aliases `cp` to `cp -i` (interactive), which silently refuses to overwrite. Use:
```bash
cat source > dest          # Always works
\cp source dest            # Bypasses alias
# shutil.copy2() in Python  # No alias issue
```

### 3. Organic skill prefix preservation

When deploying `aget-expand-ontology` v2.1.0, check `project_prefix` in the existing SKILL.md — each agent may have a domain-specific prefix. Merge (preserve prefix), don't blindly overwrite.

---

## Known Issues

- template-document-processor-AGET upgraded from v3.11.1 (skipped v3.12.0)
- 3 pre-existing unguarded script refs in template skills (study_topic → `study_up.py` deprecated name, analyze-ontology/close-session → `record_invocation.py` not yet created). Non-blocking — skills function without these scripts.

---

*RELEASE_HANDOFF_v3.13.0.md*
*Updated: 2026-04-12 (post main fleet upgrade + hotfix)*
*Created by aget-framework manager*
