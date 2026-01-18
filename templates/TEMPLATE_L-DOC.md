# L{NNN}: {Title}

<!--
TEMPLATE INSTRUCTIONS:
1. Replace all {placeholders} with actual values
2. Remove sections marked [OPTIONAL] if not needed
3. Delete this instruction block before finalizing
4. Follow SOP_L-DOC_CREATION.md for the full creation process
5. After creating, add entry to .aget/evolution/index.json
-->

**Type**: {Pattern | Gap Discovery | Decision | Anti-Pattern | Observation | Proposal}
**Date**: {YYYY-MM-DD}
**Status**: {OPEN | RESOLVED | DEPRECATED}
**Severity**: {Critical | High | Medium | Low} <!-- For Gap type only -->
**Domain**: {Governance | Session | Memory | Release | Migration | Operations}
**Source**: {What triggered this learning - session, issue, implementation, etc.}

---

## Summary

{1-2 sentences capturing the essence of this learning. Should be understandable without reading the full document.}

---

## Context

{What led to this discovery? Include:
- Session or project context
- What you were trying to do
- What happened or was observed
- Why this matters}

---

## Core Content

<!-- Choose the appropriate subsection based on Type -->

### For Pattern Type: The Pattern

{Describe the pattern:
- When to apply it
- How it works
- Step-by-step if applicable}

### For Gap Type: Gap Analysis

| Current State | Desired State |
|---------------|---------------|
| {What exists now} | {What should exist} |

**Impact of Gap**:
- {Impact 1}
- {Impact 2}

### For Decision Type: Decision Record

**Decision**: {The decision made}

**Alternatives Considered**:

| Option | Pros | Cons |
|--------|------|------|
| {Option A} | {pros} | {cons} |
| {Option B} | {pros} | {cons} |

**Rationale**: {Why this option was chosen}

**Trade-offs**: {What we gave up}

**Reversibility**: {Reversible | Irreversible}

### For Anti-Pattern Type: The Anti-Pattern

**Pattern Name**: {Name the anti-pattern}

**Description**: {What the anti-pattern looks like}

**Why It Happens**: {Root cause}

**Consequences**: {What goes wrong}

**Prevention**: {How to avoid}

**Recovery**: {How to fix if caught}

### For Proposal Type: Proposed Change

**Current**: {How things work now}

**Proposed**: {How things would work}

**Benefits**: {What improves}

**Costs**: {What it takes}

**Migration Path**: {How to get from current to proposed}

---

## Evidence

<!-- [RECOMMENDED] Concrete examples strengthen L-docs -->

### Example 1: {Example Title}

{Concrete example demonstrating the learning}

```
{Code, output, or structured example if applicable}
```

### Evidence Summary

| Evidence | Source | Date |
|----------|--------|------|
| {Evidence 1} | {session/issue/etc} | {date} |
| {Evidence 2} | {session/issue/etc} | {date} |

---

## Recommended Actions

<!-- [OPTIONAL for Observations, REQUIRED for Gaps] -->

| Priority | Action | Target | Owner |
|----------|--------|--------|-------|
| P1 | {Urgent action} | {Version/timeline} | {Agent} |
| P2 | {Important action} | {Version/timeline} | {Agent} |
| P3 | {Nice-to-have} | {Version/timeline} | {Agent} |

---

## Resolution Criteria

<!-- [REQUIRED for Gap type] -->

- [ ] {Criterion 1 for considering this resolved}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

---

## Anti-Patterns

<!-- [OPTIONAL but recommended] -->

| Don't Do This | Do This Instead |
|---------------|-----------------|
| {Anti-pattern 1} | {Correct approach} |
| {Anti-pattern 2} | {Correct approach} |

---

## Related

<!-- Cross-references to other knowledge base entries -->

- **L-docs**: {L### related learnings}
- **Specs**: {Relevant specifications}
- **SOPs**: {Relevant procedures}
- **ADRs**: {Relevant architectural decisions}
- **Issues**: {GitHub issues if applicable}

---

## Adoption Notes

<!-- [OPTIONAL] For patterns being propagated across fleet -->

| Field | Value |
|-------|-------|
| Applicability | {agent | portfolio | fleet | framework} |
| Adopted By | {List of agents using this} |
| Pilot Started | {Date if applicable} |

---

## Resolution Log

<!-- [OPTIONAL] Track when and how gap was resolved -->

| Date | Action | Result |
|------|--------|--------|
| {date} | {action taken} | {outcome} |

---

*L{NNN}_{snake_case_title}.md*
*Discovered: {YYYY-MM-DD}*
*Agent: {agent-name} v{X.Y.Z}*
*Status: {OPEN | RESOLVED | DEPRECATED}*
