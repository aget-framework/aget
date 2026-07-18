---
name: aget-close-session
description: Close session with pre-close triage, enriched output, and dual provenance. Orchestrates wind-down — does not replace it.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# aget-close-session

Close an AGET agent session with decision support. Scans for quick wins, auto-executes them, then runs wind-down and enriches the session note.

## Governing Requirements

`planning/artifacts/CAP-SESSION-013_close_session_requirements.md` v0.1.0
Extends: AGET_SESSION_SPEC v1.2.0 (CAP-SESSION-004: Wind-Down Protocol)
Proposal: SP-008

## Modification Guard

**Before modifying this skill**: update `planning/artifacts/CAP-SESSION-013_close_session_requirements.md` requirements first. SKILL.md implements the spec, not the other way around. (OBS-13, L157)

## Instructions

When this skill is invoked:

### Phase 1: Pre-Close Triage (R-CLOSE-001 through R-CLOSE-007)

**Before running wind-down**, scan session context for remaining low-effort work.

**Friction rule**: Use Glob and Grep to discover uncommitted files and session state — do NOT use `git status` via Bash. This avoids a wasted permission prompt (R-CLOSE-040, R-CLOSE-041).

1. **Review** what the session was working on and what's unfinished
2. **Identify quick wins** (≤5 min each, same repo, single action):
   - Undeployed deliverables the session already built
   - Memory saves that prevent future re-discovery
   - Stale file cleanup the session identified but didn't act on
   - Status updates on tracked items (PROJECT_PLANs, issues)
   - Draft finalization (docs already written but not committed)
3. **Execute them automatically** — do NOT ask permission (R-CLOSE-002)
4. **Report** what was done in the output under `Pre-close actions:`
5. **Skip** anything requiring >5 min, new research, multi-file refactors, or other agents' work (R-CLOSE-005)
6. If a quick win fails, note the failure and continue closing (R-CLOSE-007)

**Triage boundary**: Fix time ≤5 min qualifies. Diagnostic time is excluded from the 5-min budget but counts against the friction budget (R-CLOSE-020).

### Phase 2: Wind-Down Delegation (CAP-SESSION-004)

Run wind-down and telemetry as a **single Bash call** (R-CLOSE-042):

1. **Check** if `scripts/record_invocation.py` exists using Glob (not Bash)
2. **If exists**, run both chained:
   ```bash
   python3 scripts/wind_down.py --force && python3 scripts/record_invocation.py aget-close-session
   ```
3. **If not**, run wind-down only:
   ```bash
   python3 scripts/wind_down.py --force
   ```

This consumes **1 permission prompt** for all of Phase 2. `--force` bypasses the re-entrancy guard since close-session is the orchestrator.

### FRICTION RULES (R-CLOSE-040 through R-CLOSE-044)

**Target: ≤2 permission prompts for the entire invocation.**

The only Bash calls allowed are:
1. `python3 scripts/wind_down.py --force [&& python3 scripts/record_invocation.py aget-close-session]` (Phase 2, single combined call)
2. `git add ... && git commit ...` (Phase 3, single combined call)

Everything else MUST use dedicated tools:
- File discovery → Glob (not `git status`, not `ls`)
- File content → Read (not `cat`, not `head`)
- Content search → Grep (not `grep`, not `rg`)
- File state check → Glob (not `test -f`)

**PROHIBITED Bash calls**: `git status`, `git diff`, `git log`, `git diff --stat`, `ls`, `cat`, `grep`. These each cost a permission prompt and are replaceable by dedicated tools.

### Phase 3: Session Enrichment (R-CLOSE-008 through R-CLOSE-035)

Enrich the session note created by wind_down.py:

1. **Read** the stub created by wind_down.py
2. **Overwrite** with enriched content:
   - Add `theme:` and `closed_by: aget-close-session/1.0.0` to YAML frontmatter (R-CLOSE-008, R-CLOSE-011)
   - Add session summary, objectives, key decisions, artifacts created
   - Add retrospective (What Went Well, What We Learned, What Was Missing)
   - Add `## Session Friction` section with table classifying events as avoidable/structural/operational (R-CLOSE-017, R-CLOSE-018). If zero friction events, write `None observed.` (R-CLOSE-019)
   - Preserve `pending_work` and `health_check` data from the stub
3. **Selective commit** (R-CLOSE-032 through R-CLOSE-035):
   - Identify this session's files by reviewing what was created/modified
   - `git add` only this session's files
   - Commit them — do NOT defer because other sessions' files are dirty
   - Report other sessions' uncommitted files as informational:
     ```
     Other sessions' uncommitted files (not committed):
       - [filename] (likely from [session/date])
     ```
4. **Present** the close-session output

## Output Format (R-CLOSE-013)

Present the close-session summary. All fields are mandatory.

```
Close Session Complete: [THEME IN CAPS]
- Session: [duration]
- Sanity: [healthy/warnings/errors]
- Pending: [N] items in planning/
- Changes: [committed/staged/unstaged counts]
- Pre-close actions: [N quick wins executed — list them] (omit if 0)
- Artifacts: [count and types: L-docs, issues, scripts, session notes, skills]
- Friction: [N] events ([M] avoidable)
- Context: [N]% remaining (estimate from status bar)

CRITICAL: [blocker description] (only if critical blockers exist — omit otherwise)
Resume: [one-line actionable hint for next session]
Type `exit` to end this session.
```

**Mandatory fields**: ALL lines are mandatory. `Friction:` MUST appear even when 0 events — write `Friction: 0 events (0 avoidable)` (R-CLOSE-035).

**Tail ordering** (mandatory): CRITICAL (conditional) → Resume (always) → exit line (always).

### Session Note Frontmatter (R-CLOSE-008, R-CLOSE-011)

```yaml
---
date: YYYY-MM-DD
aget_version: "X.Y.Z"
agent_name: "agent-name"
theme: "DESCRIPTIVE SESSION THEME"
closed_by: aget-close-session/1.0.0
status: completed
---
```

- `theme:` is the canonical field name — NOT `title:`, NOT `name:` (R-CLOSE-012)
- `closed_by` version MUST match this skill's version (R-CLOSE-010)

## Friction Minimization (R-CLOSE-020 through R-CLOSE-023)

Target: ≤2 permission prompts per invocation.

- **Use dedicated tools**: Read/Grep/Glob instead of Bash(cat/grep/find) for all diagnostics (R-CLOSE-021)
- **Run wind_down.py once**: Do NOT re-run for diagnostics (R-CLOSE-022). If sanity fails, diagnose using Read tool on health_check.py output (R-CLOSE-023)
- **Batch git operations**: Single `git add` + `git commit` call

Expected prompts: wind_down.py (1) + git commit (1) = 2.

## Relationship to /aget-wind-down

| Aspect | /aget-wind-down | /aget-close-session |
|--------|-----------------|---------------------|
| Role | Infrastructure (stub + health check) | Orchestrator (triage + wind-down + enrichment) |
| Invocation | Phase 2 delegate | Top-level skill |
| Output | Minimal session stub | Enriched session note |
| Provenance | None | `closed_by` + `record_invocation.py` |
| Status | Deprecated (POL-DEP-001, grace until v4.0) | Canonical |

`/aget-wind-down` remains functional. A deprecation notice should be added to its SKILL.md:

> **DEPRECATED**: Use `/aget-close-session` instead. This skill is retained during POL-DEP-001 grace period. Expires at v4.0 per DESIGN_DIRECTION_skill_verb_vocabulary.md.

## Error Handling

- wind_down.py exit code 0: proceed with enrichment
- wind_down.py exit code 1: proceed with warning noted in output
- wind_down.py exit code 2: proceed, note error, add CRITICAL line to output
- wind_down.py exit code 3: configuration error — report and stop
- wind_down.py exit code 4: re-entrancy guard — use `--force` if within close-session invocation
- record_invocation.py missing: skip silently (frontmatter is primary provenance)

## Traceability

| Link | Reference |
|------|-----------|
| Requirements | CAP-SESSION-013 (planning/artifacts/) |
| Extends | AGET_SESSION_SPEC v1.2.0 CAP-SESSION-004 |
| Proposal | SP-008 (planning/skill-proposals/PROPOSAL_aget-close-session.md) |
| Verb vocabulary | DESIGN_DIRECTION_skill_verb_vocabulary.md (close: proposed, Common category) |
| Upstream issues | #925 ({verb}_by), #926 (friction budget), #297 (v4.0 rename) |
| Cross-fleet evidence | Legalon FLEET_CLOSE_SESSION_SPEC v1.1.0 (9 CAPs, 8 scored sessions, 0.74 avg) |
| L-docs | L670, L699, L605 (framework); L157, L159, L160, L162 (Legalon) |
| Session observations | OBS-5 through OBS-11 (SESSION_2026-04-10) |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-10 | Initial creation. Composition architecture (orchestrates wind-down). 3 phases: pre-close triage, wind-down delegation, session enrichment. Governed by CAP-SESSION-013. Cross-fleet evidence from Legalon v1.0-v1.3 (8 sessions, 0.50→0.74). |

---

*aget-close-session v1.0.0*
*Category: Lifecycle*
*Architecture: Composition (orchestrates /aget-wind-down)*
