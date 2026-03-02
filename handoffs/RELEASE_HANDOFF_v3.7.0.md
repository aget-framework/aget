# RELEASE_HANDOFF: v3.7.0

**Version**: 3.7.0
**Released**: 2026-03-05
**Theme**: Quality Reconciliation

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
| Supervisor template: +2 archetype skills | Supervisor archetype only |

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

3. **Rename 4 skill directories** (P2.10 verb vocabulary):
   ```bash
   # In your agent's .claude/skills/ directory:
   mv aget-studyup aget-study-up               # if present
   mv aget-healthcheck-kb aget-check-kb         # if present
   mv aget-healthcheck-sessions aget-check-sessions  # if present
   mv aget-sanity-check aget-check-health       # if present
   ```
   **Why**: AGET verb vocabulary now follows PowerShell Approved Verbs pattern. `check` replaces `healthcheck`/`sanity-check`; `study-up` adds required hyphen.

4. **Update skill references in AGENTS.md** (if present):
   - `aget-studyup` → `aget-study-up`
   - `aget-healthcheck-kb` → `aget-check-kb`
   - `aget-healthcheck-sessions` → `aget-check-sessions`
   - `aget-sanity-check` → `aget-check-health`

5. **Validate**:
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

## Smoke Test Checklist

1. `wake_up.py` shows v3.7.0
2. Housekeeping passes 9/9
3. Skill directories use new names (`aget-check-*`, `aget-study-up`)
4. AGENTS.md shows `@aget-version: 3.7.0`
5. AGENTS.md has updated positioning (no overreaching professional claims)
6. Conformance report shows CONFORMANT at deep depth

---

## Context for External Fleets

### What is "Quality Reconciliation"?

v3.7.0's theme addresses a systemic pattern (L604): AGET's forward pipeline (specify, create, deploy) was strong, but the return path (feedback, lifecycle governance, behavioral validation) was broken. Specifically:
- **Claim drift**: Public documentation sometimes claimed capabilities that weren't fully implemented (L608)
- **Phantom SOPs**: SOPs referenced in specs but never created
- **Positioning overreach**: README claims about professional use cases not supported by fleet evidence

This release doesn't add major features — it ensures what we *claim* matches what *exists*.

### What are the Verb Renames?

AGET skills follow a `aget-{verb}-{object}` naming convention. v3.7.0 aligns 4 skills with the approved verb vocabulary:
- `healthcheck` → `check` (standard verb, matches PowerShell `Test-`/`Get-` pattern)
- `sanity-check` → `check-health` (object is `health`, verb is `check`)
- `studyup` → `study-up` (adds required hyphen)

Old names continue to work via symlinks in templates, but the canonical names have changed.

### Archetype Reference

| Archetype | v3.7.0-Specific Changes | Action |
|-----------|------------------------|--------|
| supervisor | +2 archetype skills (`aget-check-fleet`, `aget-review-handoff`) | Deploy new skills |
| All others | Verb renames (4 skills), positioning reframe, skill count 15 | Rename + update |

---

## References

- [CHANGELOG.md](../CHANGELOG.md) — Full v3.7.0 changes
- [UPGRADING.md](../docs/UPGRADING.md) — Migration procedures
- [VERSION_SCOPE_v3.7.0.md](https://github.com/aget-framework/aget/releases/tag/v3.7.0) — Release

---

*RELEASE_HANDOFF_v3.7.0.md*
*Generated: 2026-03-05*
*Per R-REL-019*
