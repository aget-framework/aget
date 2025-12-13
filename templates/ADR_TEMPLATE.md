# ADR-{NNN}: {Title}

**Date**: {YYYY-MM-DD}
**Status**: {Proposed | Accepted | Deprecated | Superseded}
**Context**: {Brief context phrase}
**Decision**: {One-line decision summary}

---

## Context

{Describe the issue motivating this decision. Include:
- What problem are we trying to solve?
- What constraints exist?
- What forces are at play?}

---

## Decision

{State the decision clearly and concisely.}

{Optionally expand with:
- Key principles
- Implementation approach
- Boundaries/scope}

---

## Consequences

### Positive

{List benefits of this decision}

- Benefit 1
- Benefit 2
- Benefit 3

### Negative

{List drawbacks or costs}

- Cost 1
- Cost 2

### Neutral

{List effects that are neither positive nor negative}

- Observation 1

---

## Alternatives Considered

### Alternative 1: {Name}

{Brief description}

**Why not chosen**: {Reason}

### Alternative 2: {Name}

{Brief description}

**Why not chosen**: {Reason}

---

## Implementation

{Optional: Phases or steps for implementation}

### Phase 1: {Name}

- [ ] Task 1
- [ ] Task 2

### Phase 2: {Name}

- [ ] Task 3
- [ ] Task 4

---

## Related Documents

- {Link to related ADR, spec, or doc}
- {Link to related ADR, spec, or doc}

---

## Decision Outcome

**{Status}**: {Summary of outcome and any conditions}

{For Accepted: What triggers reconsideration?}
{For Deprecated: What replaces this?}
{For Superseded: Link to superseding ADR}

---

*Signed off by: {Role/Team}*
*Review date: {YYYY-MM-DD}*

---

# ADR Template Usage Guide

## When to Write an ADR

Write an ADR when:
- Making a significant architectural decision
- Choosing between multiple viable approaches
- Establishing a pattern that others should follow
- Making a decision that would be hard to reverse

## ADR Numbering

```
ADR-{NNN}-{kebab-case-title}.md

Examples:
- ADR-001-aget-framework-repository.md
- ADR-012-migration-strategy.md
```

## Status Transitions

```
Proposed → Accepted → [Deprecated | Superseded]
                    ↘ [remains Accepted indefinitely]
```

## Best Practices

1. **Be concise**: ADRs should be readable in 5 minutes
2. **Focus on "why"**: Context matters more than "what"
3. **Document alternatives**: Show you considered options
4. **Update status**: Don't leave ADRs in "Proposed" forever
5. **Link related docs**: Create traceable decision chains

## Template Sections

| Section | Required | Purpose |
|---------|----------|---------|
| Header | Yes | Quick reference metadata |
| Context | Yes | Problem statement |
| Decision | Yes | The actual decision |
| Consequences | Yes | Impact analysis |
| Alternatives | Recommended | Shows due diligence |
| Implementation | Optional | Execution plan |
| Related Documents | Optional | Cross-references |
| Decision Outcome | Yes | Final status |

---

*ADR_TEMPLATE.md — Standard format for architectural decisions*
