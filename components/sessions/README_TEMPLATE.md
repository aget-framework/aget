# Sessions Directory

This directory contains session notes and handoff documentation.

## Contents

| Pattern | Purpose |
|---------|---------|
| `session_YYYY-MM-DD_*.md` | Session notes |
| `HANDOFF_*.md` | Inter-session continuity documents |

## Session Protocol

### Wake Up (Session Start)

1. Execute `python3 .aget/patterns/session/wake_up.py`
2. Review pending work from previous sessions
3. Create session note with date stamp

### Wind Down (Session End)

1. Execute `python3 .aget/patterns/session/wind_down.py`
2. Update session note with work completed
3. Create HANDOFF if work continues to next session

## Guidance

### Session Note Content

| Section | Content |
|---------|---------|
| Context | What session was about |
| Work Completed | What was accomplished |
| Decisions Made | Key decisions and rationale |
| Blocked Items | What couldn't be completed and why |
| Next Actions | What needs to happen next |

### HANDOFF Content

| Section | Content |
|---------|---------|
| Current State | Where work stands |
| Critical Context | What next session needs to know |
| Files Modified | Key files touched |
| Pending Items | What remains to be done |
| Learnings | L-docs captured during session |

### Naming Convention

```
session_YYYY-MM-DD_<topic>.md
session_YYYY-MM-DD_HHMM.md  (if multiple sessions per day)
HANDOFF_<topic>_YYYY-MM-DD.md
```

## Anti-Patterns

| Anti-Pattern | Why Bad | Instead |
|--------------|---------|---------|
| No session notes | Context lost between sessions | Always create session note |
| Missing HANDOFF | Continuity broken | Create HANDOFF for ongoing work |
| Too verbose | Hard to scan | Focus on decisions and actions |

## Cross-References

| Document | Relationship |
|----------|--------------|
| `.aget/patterns/session/wake_up.py` | Session initialization |
| `.aget/patterns/session/wind_down.py` | Session finalization |
| `planning/` | PROJECT_PLANs referenced in sessions |

---

*Template version: 1.0.0 (L403 pattern)*
*Created by: private-aget-framework-AGET*
