# /aget-{verb}-{noun}

{Description: Two clauses — (1) specific mechanism naming key inputs/outputs/artifacts checked, (2) use-case trigger or value proposition. 50-200 chars. See CS-007.}
{Example: "Run housekeeping checks on .aget/ structure, version.json, identity.json, and governance/ integrity. Catches configuration drift before it cascades."}

## Purpose

{Why this skill exists and what problem it solves}

## Input

{input description} - {format/requirements}

Examples:
- `/aget-{verb}-{noun}` — {example with no args}
- `/aget-{verb}-{noun} arg1` — {example with arg}

## Execution

### Step 1: {First Step Name}

{Description of what happens}

```bash
# Example command if applicable
```

### Step 2: {Second Step Name}

{Description of what happens}

### Step 3: {Third Step Name}

{Description of what happens}

## Output

{What the skill produces or displays}

```
=== /aget-{verb}-{noun}: {topic} ===

{Expected output format}
```

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-{SKILL}-001 | {First requirement — what the skill SHALL do} | {L-doc, spec, or issue} |
| REQ-{SKILL}-002 | {Second requirement} | {source} |
| REQ-{SKILL}-003 | {Third requirement} | {source} |

## Constraints

- **C1**: {First constraint - use prohibitive form per L561}
- **C2**: {Second constraint}
- **C3**: MUST NOT modify {protected items}
- **C4**: MUST validate input before proceeding

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| {error message} | {cause} | {how to fix} |

## Related Skills

- `/aget-{related-skill-1}` - {relationship}
- `/aget-{related-skill-2}` - {relationship}

## Traceability

| Link | Reference |
|------|-----------|
| Spec | {SKILL-NNN or spec reference} |
| Requirements | {R-SKILL-XXX-NNN} |
| L-docs | {related L-docs} |
| POC | {POC-NNN if applicable} |

---

*aget-{verb}-{noun} v1.0.0*
*Category: {category}*
*Template: templates/skill/SKILL.template.md*
