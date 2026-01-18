# SOP: {Title}

<!--
TEMPLATE INSTRUCTIONS:
1. Replace all {placeholders} with actual values
2. Remove sections marked [OPTIONAL] if not needed
3. Delete this instruction block before finalizing
4. Follow SOP_SOP_CREATION.md for the full creation process
-->

**Implements**: {R-DOMAIN-NNN-* | Remove if no requirements}
**Pain Point**: {L### reference | Remove if none}
**See**: {Spec section reference | Remove if none}
**Pattern**: {L### reference | Remove if none}

---

**Version**: 1.0.0
**Created**: {YYYY-MM-DD}
**Owner**: {agent-name}
**Category**: {Governance | Operations | Migration | Session | Release | Memory | Security}
**Related**: {comma-separated list of L-docs, specs, patterns}

---

## Purpose

{One paragraph explaining why this SOP exists. Be specific about the problem solved.}

**Problem Solved**: {What happens without this SOP - the pain point it addresses}

---

## Scope

### When to Use This SOP

| Trigger | Example |
|---------|---------|
| {Trigger condition 1} | {Concrete example} |
| {Trigger condition 2} | {Concrete example} |

### When NOT to Use This SOP

| Situation | Alternative |
|-----------|-------------|
| {Situation 1} | {What to do instead} |
| {Situation 2} | {What to do instead} |

---

## Prerequisites

<!-- [OPTIONAL] Include if there are requirements before starting -->

- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}
- [ ] {Prerequisite 3}

---

## Procedure

### Step 1: {Step Title}

{Clear instructions for this step}

```bash
# Example command if applicable
{command}
```

### Step 2: {Step Title}

{Clear instructions for this step}

### Step 3: {Step Title}

{Clear instructions for this step}

---

## Checklists

<!-- [OPTIONAL] Include multiple checklists for different scenarios -->

### Checklist A: {Scenario A Name}

Use when: {When to use this checklist}

- [ ] {Check item 1}
- [ ] {Check item 2}
- [ ] {Check item 3}

### Checklist B: {Scenario B Name}

Use when: {When to use this checklist}

- [ ] {Check item 1}
- [ ] {Check item 2}
- [ ] {Check item 3}

---

## Output Template

<!-- [OPTIONAL] Include if this SOP produces a specific artifact -->

```markdown
# {Output Title}

**Date**: {YYYY-MM-DD}
**Created By**: {who}

## {Section 1}

{content}

## {Section 2}

{content}
```

---

## Examples

### Example: Good

{Description of a correct execution of this SOP}

```
{Example of correct usage}
```

### Example: Bad (Anti-Pattern)

{Description of incorrect execution}

```
{Example of incorrect usage}
```

**Why it's wrong**: {Explanation}

---

## Anti-Patterns

| Anti-Pattern | Consequence | Prevention |
|--------------|-------------|------------|
| {Anti-pattern 1} | {What goes wrong} | {How to avoid} |
| {Anti-pattern 2} | {What goes wrong} | {How to avoid} |
| {Anti-pattern 3} | {What goes wrong} | {How to avoid} |

---

## Common Misconceptions

<!-- [OPTIONAL] Include if there are frequent misunderstandings -->

| Misconception | Reality |
|---------------|---------|
| {Wrong belief 1} | {Correct understanding} |
| {Wrong belief 2} | {Correct understanding} |

---

## Troubleshooting

<!-- [OPTIONAL] Include if problems are common -->

### Problem: {Problem Description}

**Symptoms**: {What you observe}

**Cause**: {Why this happens}

**Solution**: {How to fix}

---

## Rollback

<!-- [OPTIONAL] Include if procedure can be undone -->

If this procedure needs to be reversed:

1. {Rollback step 1}
2. {Rollback step 2}
3. {Rollback step 3}

---

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| {Metric 1} | {What it measures} | {Target value} |
| {Metric 2} | {What it measures} | {Target value} |

---

## Quick Reference

### Minimum Viable Execution

1. {Essential step 1}
2. {Essential step 2}
3. {Essential step 3}

### Decision Tree

```
{Decision question 1}?
    │
    ├── {Option A} → {Action A}
    └── {Option B} → {Action B}
```

---

## Integration

<!-- [OPTIONAL] Include if this SOP connects to other protocols -->

### Related Protocols

| Protocol | Relationship |
|----------|--------------|
| {Protocol 1} | {How they connect} |
| {Protocol 2} | {How they connect} |

### Workflow Position

```
{Previous step/protocol}
        ↓
    THIS SOP
        ↓
{Next step/protocol}
```

---

## References

- {Reference 1}: {Brief description}
- {Reference 2}: {Brief description}
- {Reference 3}: {Brief description}

---

## Graduation History

<!-- [OPTIONAL] Include if SOP graduated from PROJECT_PLAN -->

```yaml
graduation:
  source: "{PROJECT_PLAN name}"
  trigger: "{What triggered graduation}"
  executions: {number of times pattern was executed}
  l_docs_consolidated: [{list of L-docs if consolidation}]
```

---

*SOP_{name}.md v1.0.0 — "{Tagline summarizing the SOP}"*
*Created: {YYYY-MM-DD}*
*Owner: {agent-name}*
