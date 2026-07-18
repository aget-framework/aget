---
name: aget-open-session
description: Open a session with context-aware establishment. Orchestrates wake-up, recovers prior session context, surfaces pending work, and proposes a session agenda.
---

# /aget-open-session

Open a session with context-aware establishment. Orchestrates wake-up, then adds context recovery, health gating, and session provenance.

## Purpose

The current `/aget-wake-up` skill runs `wake_up.py` and displays agent identity — but leaves context recovery to the principal. Open-session transforms session initialization from identity display into context-aware session establishment by adding: prior session context recovery, pre-session health gating, and `opened_by` provenance (mirroring `closed_by` from SP-008).

**Evidence**: SP-008 (close-session) validated composition architecture with cross-fleet evidence (8 sessions). L562 (rename caused 32/32 false-positive drift) confirms composition over rename. L335 (Memory Architecture) specifies 2-minute context recovery target. L670 (Session Quality Assessment Gap). Principal confirmed open/close verb pair (2026-04-10) over start/stop and init/close alternatives.

## Input

$ARGUMENTS (none required)

Examples:
- `/aget-open-session` — Full open with context recovery
- `open session` — Natural language trigger
- `open this session` — Natural language trigger

## Execution

### Phase 1: Wake-Up Delegation

Run wake-up infrastructure as a single Bash call:

Run the wake-up script using the agent's canonical path:

```bash
# Try canonical paths in order (agents may have different locations)
if test -f scripts/wake_up.py; then
  python3 scripts/wake_up.py
elif test -f .aget/patterns/session/wake_up.py; then
  python3 .aget/patterns/session/wake_up.py
else
  echo "No wake_up.py found — run manual wake-up"
fi
```

Optionally log invocation if telemetry script available:
```bash
test -f scripts/log_skill_invocation.py && python3 scripts/log_skill_invocation.py --skill aget-open-session --version 0.1.0 --outcome success --duration-seconds 0
```

This produces agent identity, version, git status, and health check.

### Phase 2: Context Recovery

Using Read, Grep, and Glob (no Bash — zero permission cost):

1. **Prior session**: Find most recent `sessions/SESSION_*.md` by date
   - Extract `theme`, `next_steps`, and `pending_work` from frontmatter/content
   - If session is >7 days old, note staleness warning
   - If no prior session exists, display "First session" and skip to Phase 3
2. **Active projects**: List `planning/PROJECT_PLAN_*.md` files with current gate status
3. **Uncommitted work**: Use Glob to check for stale files from prior sessions
4. **Resume hint**: Surface the prior session's resume recommendation

### Phase 3: Session Establishment

Present enriched session briefing:

```
Open Session: [AGENT NAME] v[VERSION]
- Purpose: [North Star statement]
- Manages: [managed repos/templates]
- Git: [branch] ([clean/dirty])
- Health: [healthy/warnings/errors]
- Skills: [N] | Learnings: [N]

Context Recovery:
- Last session: [theme] ([date])
- Resume: [resume hint from prior session]
- Active projects: [count] ([names])
- Pending: [uncommitted files from prior sessions, if any]

Ready.
```

### Friction Budget

| Metric | Target | Method |
|--------|:------:|--------|
| Permission prompts | <=1 | Single Bash call for wake_up.py (+ record_invocation.py) |
| Context recovery | 0 prompts | Read/Grep/Glob only — no Bash |

**PROHIBITED Bash calls**: `git status`, `git log`, `ls`, `cat`, `grep`. Use dedicated tools.

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-OPEN-001 | Open-session SHALL run wake_up.py as Phase 1 delegate | SP-010, AGET_SESSION_SPEC CAP-SESSION-001 |
| REQ-OPEN-002 | Open-session SHALL recover context from most recent prior session | SP-010, L335 |
| REQ-OPEN-003 | Open-session SHALL list active PROJECT_PLANs with gate status | SP-010 |
| REQ-OPEN-004 | Open-session SHALL surface resume hint from prior session | SP-010, L580 |
| REQ-OPEN-005 | Open-session SHALL handle cold start gracefully (no prior session) | SP-010, V-OPEN-005 |
| REQ-OPEN-006 | Open-session SHALL achieve <=1 permission prompt per invocation | SP-010 (friction budget) |
| REQ-OPEN-007 | Open-session SHALL warn if prior session is >7 days old | SP-010 (staleness detection) |

## Constraints

- **C1**: Composition architecture — orchestrates wake-up, does NOT replace or rename it (L562 guard)
- **C2**: Permission budget <=1 — context recovery MUST use Read/Grep/Glob, not Bash
- **C3**: MUST handle cold start (no prior session) without errors — display "First session" note
- **C4**: MUST NOT modify any session files or KB artifacts — read-only context recovery

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-010 (`planning/skill-proposals/PROPOSAL_aget-open-session.md`) |
| Paired skill | `/aget-close-session` (SP-008, lifecycle bookend) |
| Verb vocabulary | DESIGN_DIRECTION_skill_verb_vocabulary.md (`open`: row 30, Common category) |
| Deprecates | `/aget-wake-up` (POL-DEP-001 grace period, functional through v3.14) |
| Upstream issues | #297 (v4.0 session skill rename), #925 (`{verb}_by` self-recording) |
| L-docs | L335 (Memory Architecture), L562 (Rename Drift), L580 (Session State Continuity), L670 (Session Quality Gap) |

---

*aget-open-session v0.1.0*
*Category: Session*
*Architecture: Composition (orchestrates /aget-wake-up)*
