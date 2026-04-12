# Release Handoff: v3.13.0

**Date**: 2026-04-12
**Theme**: Operational Maturation & Fleet Automation
**From**: private-aget-framework-AGET
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

---

## Upgrade Guide

### For Each Fleet Agent

| Step | Obligation | Action | V-Test Command | Expected |
|------|-----------|--------|---------------|----------|
| 1 | MUST | Update `.aget/version.json`: set `aget_version` to "3.13.0" | `jq -r .aget_version .aget/version.json` | "3.13.0" |
| 2 | MUST | Update `AGENTS.md` header: `@aget-version: 3.13.0` | `grep '@aget-version: 3.13.0' AGENTS.md` | Match |
| 3 | SHOULD | Run `python3 scripts/health_check.py` | Exit code | 0 |

### End-State Validation

```bash
python3 -c "import json; v=json.load(open('.aget/version.json')); print('PASS' if v['aget_version']=='3.13.0' else 'FAIL: '+v['aget_version'])"
```

---

## Pilot Tracking

| Fleet | Supervisor | Status | Date | Notes |
|-------|-----------|:------:|------|-------|
| Main | private-supervisor-AGET | Pending | — | — |
| WorkCo | legalon-supervisor | Pending | — | — |

---

## Known Issues

- template-document-processor-AGET upgraded from v3.11.1 (skipped v3.12.0)
- Script divergence detected: health_check.py (3 groups), wind_down.py (4 groups) — see `check_script_divergence.py`

---

*RELEASE_HANDOFF_v3.13.0.md*
*Created by private-aget-framework-AGET*
