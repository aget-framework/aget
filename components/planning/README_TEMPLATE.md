# Planning Directory

This directory contains PROJECT_PLANs and related planning artifacts.

## Contents

| Pattern | Purpose |
|---------|---------|
| `PROJECT_PLAN_*.md` | Active and historical project plans |
| `DECISION_POINT_*.md` | Captured decision points |
| `FLEET_MIGRATION_PLAN_*.md` | Fleet-wide migration plans |

## Governance (L186)

### When to Use PROJECT_PLAN

Use PROJECT_PLAN pattern for **substantial work**:
- Multi-step implementations
- Cross-agent coordination
- Work requiring go/no-go gates

**Not TodoWrite** — TodoWrite is for session-level task tracking, not governance artifacts.

### Gate Discipline (L42)

- Include go/no-go gates with decision points
- Stop at gate boundaries
- Wait for explicit GO before proceeding
- Document gate completion with evidence

## Guidance

### Naming Convention

```
PROJECT_PLAN_<topic>_v<version>.md
DECISION_POINT_<topic>.md
FLEET_MIGRATION_PLAN_v<version>.md
```

### Lifecycle

| State | Meaning |
|-------|---------|
| PROPOSED | Awaiting approval |
| ACTIVE | In execution |
| BLOCKED | Waiting on dependency |
| COMPLETE | All gates passed |
| ARCHIVED | Historical reference |

### Archival

- Archive completed plans with completion date suffix
- Reference learnings (L-docs) in post-completion notes
- Move to `archive/` subdirectory if desired

## Anti-Patterns

| Anti-Pattern | Why Bad | Instead |
|--------------|---------|---------|
| No gates | No decision points | Add go/no-go gates |
| Unbounded scope | Scope creep | Define explicit deliverables |
| Missing success criteria | Can't validate completion | Add measurable criteria |

## Cross-References

| Document | Relationship |
|----------|--------------|
| `.aget/evolution/L186_*.md` | PROJECT_PLAN pattern learning |
| `.aget/evolution/L42_*.md` | Gate discipline learning |
| `governance/MISSION.md` | Alignment with goals |

---

*Template version: 1.0.0 (L403 pattern)*
*Created by: private-aget-framework-AGET*
