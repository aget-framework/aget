# RELEASE_HANDOFF_v3.11.0.md

**Version**: 3.11.0
**Released**: 2026-03-28
**Breaking Changes**: No
**Framework Manager**: aget-framework release manager
**DEPLOYMENT_SPEC**: `specs/DEPLOYMENT_SPEC_v3.11.0.yaml`
**Theme**: Skill Conformance, Configuration & Requirements Formalization

---

## Receiving Agent Governance Checklist (BLOCKING)

**STOP**: Before executing any upgrade steps, complete this checklist:

- [ ] Located local upgrade SOP (e.g., SOP_point_upgrade.md)
- [ ] Created PROJECT_PLAN for this upgrade OR referenced existing gate
- [ ] Gate discipline acknowledged (L42)
- [ ] Principal approval obtained if required by local governance

**Warning**: Proceeding without completing this checklist is a governance violation (L562).

---

## Executive Summary

v3.11.0 introduces the human-level requirements layer (L742 two-level model), scaffolds hook infrastructure for ADR-008 Generator level, and remediates skill instruction conformance. All changes are backward-compatible. No breaking changes.

**Key Changes Summary** (for supervisor session prompt — R-REL-019-08):
1. **requirements/** directory: New human-level requirements artifact layer (L742). Contains REQUIREMENTS_FORMAT.md and REQ-REL exemplar.
2. **hooks/** scaffold: `.claude/hooks/` with README in all templates. ADR-008 Generator prerequisite.
3. **governance_intensity**: New AGENTS.md field declaring archetype governance level.
4. **Skill SKILL.md updates**: 17 skills remediated for L736 conformance (SICR).
5. **Terminology**: "sanity check" → "health check" across all references.
6. **AGET_RELEASE_SPEC v1.11.0**: First spec with Requirements Grounding section (L742 bidirectional traceability).

---

## Upgrade Steps

### Step 1: Version Bump (MUST)

Update these files in each agent:

| File | Old | New |
|------|-----|-----|
| `.aget/version.json` | `"aget_version": "3.10.0"` | `"aget_version": "3.11.0"` |
| `AGENTS.md` | `@aget-version: 3.10.0` | `@aget-version: 3.11.0` |
| `manifest.yaml` | `version: 3.10.0` | `version: 3.11.0` |

Add migration history entry:
```
"v3.10.0 -> v3.11.0: YYYY-MM-DD (Skill Conformance, Requirements Formalization, Hook Adoption)"
```

**V-test**: `jq -r .aget_version .aget/version.json` → expect `3.11.0`

### Step 2: New Directories (MUST)

```bash
mkdir -p requirements/
mkdir -p .claude/hooks/
```

Create `.claude/hooks/README.md`:
```markdown
# Hooks Directory

This directory contains Claude Code hooks for this agent.
See aget/HOOK_ADOPTION_GUIDE.md for adoption guidance.
```

**V-test**: `test -d requirements/ && test -d .claude/hooks/ && echo PASS`

### Step 3: AGENTS.md Governance Intensity (MUST)

Add to the Governance Capabilities section:

```markdown
### Governance Capabilities

**This agent uses**: `capability-governance-{level}`

| Attribute | Value |
|-----------|-------|
| Governance Intensity | {Rigorous|Standard|Lightweight} |
```

**Archetype mapping**:
- Supervisor, Spec-Engineer → Rigorous
- Worker, Developer, Researcher, Analyst, Architect, Operator → Standard
- Advisor, Consultant, Executive, Reviewer → Lightweight

**V-test**: `grep -c 'Governance Intensity\|governance_intensity' AGENTS.md` → expect 1+

### Step 4: Skill SKILL.md Sync (SHOULD)

Sync all 16 universal skill SKILL.md files from template source. SICR (#678) updated content for L736 conformance.

```bash
# Source: template-{archetype}-aget/.claude/skills/
# Target: .claude/skills/
```

**V-test**: Compare skill directories against template source.

### Step 5: Terminology Update (SHOULD)

Replace "sanity check" with "health check" in:
- AGENTS.md
- Any local scripts referencing sanity check

**V-test**: `grep -ri 'sanity.check' AGENTS.md scripts/ | wc -l` → expect 0

### Step 6: Script Sync (SHOULD)

Sync `wind_down.py` from `aget/scripts/` (updated in v3.11.0 with health check terminology).

**Note**: Preserve `wake_up_ext.py` and `wind_down_ext.py` if they exist (instance extensions).

---

## Skill Content Propagation (R-REL-019-09, L739)

**Important**: This release includes SKILL.md content updates (SICR, #678). The upgrade model propagates structural changes (directories, versions) automatically, but SKILL.md content requires manual sync per L739.

| Skill | Change | Priority |
|-------|--------|----------|
| All 17 skills | L736 conformance: assert-before-verify patterns removed | SHOULD |

---

## Deprecation Status

Active deprecations (from v3.10.0, unchanged):

| Item | Deprecated In | Replacement | Earliest Removal |
|------|--------------|-------------|-------------------|
| `capture` verb | v3.10.0 | `record` verb | v3.12.0 |
| `aget-study-up` name | v3.10.0 | `aget-study-topic` | v3.12.0 |
| `/aget-record-nugget` | v3.10.0 | `/aget-record-observation` Mode 4 | v3.12.0 |

No new deprecations in v3.11.0.

---

## Remote Fleet Announcement (L723, L724)

**For remote fleet supervisors** (e.g., remote fleets):

v3.11.0 is available. Key items for your fleet:
- **New directories**: `requirements/` and `.claude/hooks/` — scaffold only, no agent-specific content yet
- **AGENTS.md field**: `governance_intensity` — map your templates to the archetype table above
- **No breaking changes** — safe for immediate adoption

**Guidance level**: Specification (L724) — exact text replacements and V-tests provided above.

---

## Pilot Tracking

| Agent | Version | Date | Status | Notes |
|-------|---------|------|--------|-------|
| aget-framework release manager | 3.11.0 | 2026-03-28 | DEPLOYED | Self-upgrade, managing agent |
| | | | | |

---

## References

- DEPLOYMENT_SPEC_v3.11.0.yaml (state specification)
- release-notes/v3.11.0.md (deep release notes)
- CHANGELOG.md (concise changes)
- PROJECT_PLAN_v3.11.0_release_v1.0.md (REL-041)
- VERSION_SCOPE_v3.11.0.md v1.8.0 (SCOPE LOCKED)

---

*RELEASE_HANDOFF_v3.11.0.md*
*"Skill Conformance, Configuration & Requirements Formalization"*
