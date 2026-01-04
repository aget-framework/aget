# PATTERN: Role Boundary Awareness

**Pattern ID**: L029
**Version**: 1.0.0
**Status**: ACTIVE
**Implements**: #22

---

## Problem

Agents operating within a fleet often exceed their defined scope, creating:
- Duplicate work across agents
- Conflicting decisions without proper escalation
- Scope creep that compounds across sessions
- Unclear handoff points between agents

---

## Solution

Each agent maintains explicit awareness of:
1. **Own boundaries** - What it owns, can modify, must not touch
2. **Neighbor awareness** - Who handles related concerns
3. **Escalation paths** - When and where to defer decisions
4. **Handoff protocols** - How to transfer work cleanly

---

## Pattern Structure

### R-ROLE-001: Scope Declaration

**REQUIRED**: Every agent MUST have a `governance/SCOPE_BOUNDARIES.md` file.

```markdown
# Scope Boundaries

## I Own (Can Modify Unilaterally)
- [list of artifacts, directories, decisions]

## I Touch (Requires Coordination)
- [artifacts shared with other agents]

## I Must Not Touch
- [explicit out-of-scope items]

## Handoff Points
- [conditions that trigger escalation/delegation]
```

### R-ROLE-002: Neighbor Registry

**RECOMMENDED**: Agents SHOULD maintain awareness of related agents.

```json
{
  "neighbors": {
    "upstream": ["supervisor-aget"],
    "downstream": ["template-advisor-aget", "template-worker-aget"],
    "peers": ["private-other-framework-AGET"]
  },
  "handoff_matrix": {
    "breaking_changes": "supervisor-aget",
    "template_updates": "self",
    "fleet_migration": "supervisor-aget"
  }
}
```

### R-ROLE-003: Escalation Triggers

**REQUIRED**: Define explicit escalation triggers.

| Condition | Action | Escalate To |
|-----------|--------|-------------|
| Breaking API change | STOP, document | supervisor |
| Cross-template impact | Coordinate | peer templates |
| Scope boundary unclear | Ask, don't assume | supervisor |
| Fleet-wide decision | Propose, await approval | supervisor |

### R-ROLE-004: Session Scope Check

**RECOMMENDED**: At session start, validate work against scope.

```
Before executing work:
1. Read governance/SCOPE_BOUNDARIES.md
2. Compare proposed work against "I Own" list
3. If work touches "I Must Not Touch" → STOP, escalate
4. If work touches "I Touch" → Coordinate first
```

---

## Implementation

### Scope Boundaries File

Location: `governance/SCOPE_BOUNDARIES.md`

```markdown
# Scope Boundaries: [agent-name]

## I Own (Autonomous Authority)

| Artifact | Authority Level |
|----------|-----------------|
| `.aget/evolution/` | Full (create, modify, delete) |
| `planning/` | Full |
| `sessions/` | Full |
| `sops/` | Full (internal procedures) |

## I Touch (Coordination Required)

| Artifact | Coordination With |
|----------|-------------------|
| `governance/` | supervisor-aget (major changes) |
| `docs/` | peers (shared patterns) |

## I Must Not Touch

| Artifact | Owner |
|----------|-------|
| Other agents' repos | respective owners |
| Fleet-wide governance | supervisor-aget |
| Public API contracts | supervisor-aget approval |

## Handoff Points

| Trigger | Action |
|---------|--------|
| Scope unclear | Ask supervisor before proceeding |
| Breaking change | Document impact, await approval |
| Fleet migration | Propose plan, coordinate rollout |
```

### Identity Extension

Add to `.aget/identity.json`:

```json
{
  "name": "agent-name",
  "north_star": "...",
  "scope": {
    "owns": ["planning/", ".aget/evolution/", "sessions/"],
    "touches": ["governance/", "docs/"],
    "must_not_touch": ["other-agent/"]
  },
  "escalation": {
    "supervisor": "supervisor-aget",
    "peers": ["peer-1-aget", "peer-2-aget"]
  }
}
```

---

## Anti-Patterns

### Anti-Pattern 1: Scope Creep Cascade

**Problem**: Agent expands scope incrementally across sessions.

```
Session 1: "I'll just add this helper..."
Session 2: "While I'm here, I'll also..."
Session 3: "This is now effectively my responsibility..."
```

**Solution**: R-ROLE-004 session scope check.

### Anti-Pattern 2: Silent Boundary Crossing

**Problem**: Agent modifies artifacts outside scope without coordination.

**Solution**: R-ROLE-003 escalation triggers.

### Anti-Pattern 3: Assumption-Based Handoff

**Problem**: "I assume they'll handle it."

**Solution**: Explicit handoff with confirmation.

---

## Verification

### V-ROLE-001: Scope Boundaries Exist

```bash
ls governance/SCOPE_BOUNDARIES.md
# Expected: File exists
```

### V-ROLE-002: Three Sections Present

```bash
grep -c "## I Own\|## I Touch\|## I Must Not Touch" governance/SCOPE_BOUNDARIES.md
# Expected: 3
```

### V-ROLE-003: Escalation Defined

```bash
grep -c "Handoff\|Escalat" governance/SCOPE_BOUNDARIES.md
# Expected: >= 1
```

---

## Related Patterns

- **L342**: Session Scope Validation
- **L340**: Execution Governance Artifact Requirement
- **L042**: Gate Boundary Discipline
- **L178**: Human Override Principle

---

## References

- Issue #22: Role Boundary Awareness Pattern
- `governance/SCOPE_BOUNDARIES.md` - Template in templates
- `.aget/identity.json` - Scope extension

---

*PATTERN_role_boundary_awareness.md - L029 Fleet Governance Pattern*
