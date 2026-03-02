# RELEASE_HANDOFF: v3.7.0

**Version**: 3.7.0
**Released**: 2026-03-05
**Theme**: Quality Reconciliation
**Breaking Changes**: None (verb renames require attention — see Changed)

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

v3.7.0 is a quality reconciliation release — aligning what the framework claims with what actually exists. It closes SOP gaps, strengthens content integrity tooling, reframes positioning with evidence, and reconciles skill naming across the fleet. No breaking changes, but 4 skill verb renames require attention during upgrade.

---

## What Changed

### Added

| Feature | Impact | Action Required |
|---------|--------|-----------------|
| CONTENT_INTEGRITY_VALIDATION_SPEC v1.0.0 | 8 dimensions of claim-vs-reality drift specced with 38 EARS requirements | No action — spec governs framework tooling |
| SOP_release_scope_decision.md v1.0.0 | 7-phase scope decision lifecycle | Review if managing releases |
| Specification Enhancement Lifecycle (SKILL-041) | SOP + spec for enhancing specs | No action — skill deployment deferred to v3.8.0 |
| `verify/validate_py_version_strings.py` | Python version string scanner (L608 Dim 8) | No action |

### Changed

| Change | Migration |
|--------|-----------|
| **4 skill verb renames** (P2.10) | See Upgrade Checklist — requires file renames in `.claude/skills/` |
| AGET_SOP_SPEC v1.2.0 (CAP-SOP-006) | No action — SOP lifecycle states added |
| Evidence-based positioning (15 READMEs + 2 specs) | Auto-propagated via template update |
| Skill count aligned at 15 universal | No action — already propagated to templates |
| Governance docs (CHARTER/MISSION/SCOPE_BOUNDARIES) | Auto-propagated via template update |
| Supervisor template: +1 archetype skill (`aget-review-handoff`) | Supervisor archetype only — see Archetype Reference |
| wind_down.py exit code fix | Warnings no longer return exit 1 — sync from template |

### Breaking Changes

None. v3.7.0 is fully backward compatible with v3.6.x.

---

## Upgrade Checklist

### Per Agent

1. **Update `.aget/version.json`**:
   ```json
   {
     "aget_version": "3.7.0",
     "updated": "2026-03-05"
   }
   ```
   Add migration_history entry:
   ```
   "v3.6.0 -> v3.7.0: 2026-03-05 (Quality Reconciliation - content integrity, SOP lifecycle, positioning reframe)"
   ```

2. **Update `AGENTS.md` header**:
   ```markdown
   @aget-version: 3.7.0
   ```

3. **Rename skill directories** (P2.10 verb vocabulary):
   ```bash
   # In your agent's .claude/skills/ directory:
   mv aget-studyup aget-study-up               # if present
   mv aget-healthcheck-kb aget-check-kb         # if present
   mv aget-healthcheck-sessions aget-check-sessions  # if present
   mv aget-sanity-check aget-check-health       # if present (or symlink target)
   ```
   **Note**: If upgrading from v3.6.0, only the first rename (`aget-studyup` → `aget-study-up`) is needed — the other 3 were already completed in v3.6.0.

   **Why**: AGET verb vocabulary now follows PowerShell Approved Verbs pattern. `check` replaces `healthcheck`/`sanity-check`; `study-up` adds required hyphen. Old names still work via symlinks in templates, but canonical names changed.

   **Warning — Skill Customization Risk**: If any agent has customized `SKILL.md` content (modified prompts, added domain context, adjusted parameters), a simple `mv` preserves those customizations. However, if you copy fresh `SKILL.md` files from templates instead, customizations will be lost. **Before renaming**: `diff` each agent's `SKILL.md` against the template version. Classify as framework-standard (safe to overwrite) or customized (preserve and merge). Automated skill customization detection is planned for v3.8.0.

4. **Sync wind_down.py** (exit code fix):
   ```bash
   TEMPLATE=~/path/to/template-{archetype}-aget
   cp $TEMPLATE/scripts/wind_down.py $AGENT/scripts/wind_down.py
   ```
   **Why**: v3.7.0 fixes wind_down.py to no longer return exit code 1 for persistent warnings. Only errors (broken state) produce non-zero exit codes.

5. **Update skill references in AGENTS.md** (if present):
   - `aget-studyup` → `aget-study-up`
   - `aget-healthcheck-kb` → `aget-check-kb`
   - `aget-healthcheck-sessions` → `aget-check-sessions`
   - `aget-sanity-check` → `aget-check-health`

6. **Validate**:
   ```bash
   python3 scripts/wake_up.py
   # Expected: Shows v3.7.0
   ```

### Fleet-Wide

- Wave 0: Supervisor first (validate new archetype skills)
- Wave 1: 2-3 simple agents (test verb renames)
- Wave 2: Remaining agents
- Verify: All agents at v3.7.0

---

## Context for External Fleets

> **Per R-REL-019-02**: This section explains concepts that may not be obvious to fleets outside the managing organization.

### What is "Quality Reconciliation"?

v3.7.0's theme addresses a systemic pattern (L604): AGET's forward pipeline (specify → create → deploy) was strong, but the return path (feedback, lifecycle governance, behavioral validation) was broken. Specifically:
- **Claim drift**: Public documentation sometimes claimed capabilities that weren't fully implemented (L608)
- **Phantom SOPs**: SOPs referenced in specs but never created
- **Positioning overreach**: README claims about professional use cases not supported by fleet evidence

This release doesn't add major features — it ensures what we *claim* matches what *exists*.

### What are the Verb Renames?

AGET skills follow a `aget-{verb}-{object}` naming convention (CS-002, PS-002). v3.7.0 aligns 4 skills with the approved verb vocabulary:
- `healthcheck` → `check` (standard verb, matches PowerShell `Test-`/`Get-` pattern)
- `sanity-check` → `check-health` (object is `health`, verb is `check`)
- `studyup` → `study-up` (adds required hyphen per PS-002)

**Old names continue to work** via symlinks in templates, but the canonical names have changed. Update your references for clarity.

### What is CONTENT_INTEGRITY_VALIDATION_SPEC?

A new specification (38 requirements) that defines how to detect and prevent claim-vs-reality drift across 8 dimensions:

| Dimension | What it checks | Example |
|-----------|---------------|---------|
| 1. Platform claims | CLI tool references | "Cursor" → "Codex CLI" |
| 2. Private names | Agent names in public repos | `private-*-aget` |
| 3. Skill counts | Spec vs README vs deployed | 13/14/15 mismatch |
| 4. Template identity | Agent-specific content in templates | Stale agent names |
| 5. Dead links | Broken internal references | Missing SOP refs |
| 6. Phantom SOPs | Referenced but uncreated SOPs | "See SOP_session_end" |
| 7. README versions | Version badge accuracy | v3.5.0 badge on v3.6.0 |
| 8. Script versions | Hardcoded version strings in .py | `version = "2.9.0"` |

**Deploy to**: Framework manager primarily. Useful for any agent maintaining public documentation.

### Archetype Reference

> **Per R-REL-019-05**: Not all features apply to every agent.

| Archetype | v3.7.0-Specific Changes | Action |
|-----------|------------------------|--------|
| supervisor | +1 archetype skill (`aget-review-handoff`), evidence-rich `/aget-create-project`. Note: `aget-check-fleet` was deployed in v3.6.0 | Deploy `aget-review-handoff` |
| All others | Verb renames (4 skills), positioning reframe (AGENTS.md), skill count 15 | Rename + update |

**Universal changes** (all agents): 4 verb renames, AGENTS.md positioning reframe, `@aget-version: 3.7.0`.

---

## Critical Mitigations

> **Per R-REL-019-04**: L-doc references are explained here, not just labeled.

### L608: Content Claim Drift

**The problem**: Public documentation claims capabilities that don't exist, version badges show old versions, or skill counts are wrong. Users and external fleets see outdated/incorrect information.

**The rule**: Every release must audit 8 dimensions of claim-vs-reality drift before publication.

**BEFORE upgrading**, check your agent's AGENTS.md:
```bash
# Check for stale version references
grep -n "3\.5\|3\.4\|3\.3" AGENTS.md
# Expected: 0 matches (all should reference 3.6.0 or later)

# Check for old skill names
grep -n "studyup\|healthcheck\|sanity-check" AGENTS.md
# Expected: 0 matches after v3.7.0 rename
```

### L440: Manager Migration Verification

**The problem**: Upgrading managed repos before the manager itself causes version inconsistency.

**The rule**: Managing agent updates its own version BEFORE updating managed repos (R-REL-006).

**BEFORE upgrading fleet agents**:
```bash
# Verify supervisor is at v3.7.0
python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])"
# Expected: 3.7.0
```
- **If < 3.7.0**: Upgrade supervisor first
- **If 3.7.0**: Proceed with fleet

---

## v3.6.0 Observation Status

These observations from the v3.6.0 upgrade are addressed in v3.7.0:

| # | v3.6.0 Observation | v3.7.0 Status |
|---|-------------------|---------------|
| 1 | Worker-archetype skills in supervisor baseline expectation | **Resolved** — Supervisor template now has explicit archetype skill list (6 archetype + 15 universal = 21) |
| 2 | Skill count 3-way mismatch (13/14/15) | **Resolved** — Aligned at 15/15/15 |
| 3 | `aget-study-up` missing from supervisor | **Resolved** — Propagated in v3.6.0 upgrade; name corrected `studyup`→`study-up` in v3.7.0 |
| 4 | ~7 fleet agents have no platform claims boilerplate | **Unchanged** — Custom AGENTS.md agents unaffected; sed commands will no-op |

---

## Smoke Test Checklist

1. [ ] `wake_up.py` shows v3.7.0
2. [ ] Housekeeping passes 9/9
3. [ ] Skill directories use new names (`aget-check-*`, `aget-study-up`)
4. [ ] AGENTS.md shows `@aget-version: 3.7.0`
5. [ ] AGENTS.md has updated positioning (no overreaching professional claims) — **Note**: Only applies to agents using template AGENTS.md. Agents with custom AGENTS.md may not have these terms; skip this check for them
6. [ ] Conformance report shows CONFORMANT at deep depth

---

## Pilot Tracking Template

| Agent | Portfolio | Archetype | Status | Date | Notes |
|-------|-----------|-----------|--------|------|-------|
| _[supervisor]_ | _[portfolio]_ | supervisor | | | Wave 0 — validate archetype skills |
| _[pilot 1]_ | | | | | Wave 1 pilot |
| _[pilot 2]_ | | | | | Wave 1 pilot |
| _[remaining]_ | | | | | Wave 2 |

---

## Post-Release Validation Results

| Check | Result | Notes |
|-------|--------|-------|
| GitHub Release (aget/) | PASS | https://github.com/aget-framework/aget/releases/tag/v3.7.0 |
| Tags (13 repos) | PASS | All repos tagged v3.7.0 |
| Version consistency (13 repos) | PASS | All `.aget/version.json` at 3.7.0 |
| README badges (12 templates) | PASS | All show v3.7.0 |
| Contract tests | PASS | 135/135 passing |
| Stale verb check | PASS | 0 `studyup`/`healthcheck`/`sanity-check` refs across all repos |
| Skill directory renames | PASS | All 12 templates have `aget-study-up/` (no `aget-studyup/`) |
| Push verification | PASS | 14/14 repos at 0 ahead of remote |

### Known Items (non-blocking)

- Conformance report script has 3 v3.7.0-specific check methods defined in config but not yet implemented — deferred to v3.8.0
- `template-supervisor-aget` is now **PUBLIC** — clone directly: `gh repo clone aget-framework/template-supervisor-aget`
- Session script migration incomplete: 4 of 6 scripts remain at `.aget/patterns/session/` (only wake_up.py and wind_down.py migrated to `scripts/`)

---

## References

- [CHANGELOG.md](../CHANGELOG.md) — Full v3.7.0 changes
- [UPGRADING.md](../docs/UPGRADING.md) — Migration procedures (6 steps for v3.6.0→v3.7.0)

---

## Handoff Protocol

**From**: AGET Framework Manager
**To**: Fleet Supervisors
**Date**: 2026-03-05

### Acknowledgment

- [ ] Governance Checklist completed
- [ ] Acknowledged by: _[supervisor]_
- [ ] Date: _[date]_
- [ ] Fleet broadcast sent: _[date]_

---

*RELEASE_HANDOFF_v3.7.0.md*
*Generated: 2026-03-05 | Updated: 2026-03-01*
*Per R-REL-019*
