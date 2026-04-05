---
name: aget-file-issue
description: File GitHub issues with private-first routing (L638). ALL agents route to {private-tracker}. Public issues require promotion with principal approval.
archetype: universal
allowed-tools:
  - Bash
  - Read
  - Grep
---

# /aget-file-issue

File issues with private-first routing governance (L638). ALL issues go to `{private-tracker}`. Public issues on `aget-framework/aget` require explicit promotion.

## Purpose

Structured issue filing with:
- Private-first routing: ALL agents → `{private-tracker}` (L638)
- Content sanitization at promotion boundary only
- Template selection (enhancement, bug, feature)

## Input

```
/aget-file-issue <type> [title]
```

| Type | Description | Template |
|------|-------------|----------|
| `enhancement` | Feature enhancement | ENHANCEMENT_REQUEST |
| `bug` | Bug report | BUG_REPORT |
| `feature` | New feature | FEATURE_REQUEST |

## Execution

### Step 1: Detect Agent Type

```bash
# Check for private fleet markers
if grep -q "gmelli\|private-" <<< "$PWD"; then
  AGENT_TYPE="private"
elif grep -q '"fleet".*"private"' .aget/version.json 2>/dev/null; then
  AGENT_TYPE="private"
elif git remote -v 2>/dev/null | grep -q "gmelli/"; then
  AGENT_TYPE="private"
else
  AGENT_TYPE="public"
fi
```

### Step 2: Route to Private Tracker

**ALL agents route to `{private-tracker}`** (L638 private-first routing).

Agent type detection is retained for metadata tagging, but does NOT affect routing destination. Under the v2.0.0 policy, all agents — private fleet and public/remote — file to the private tracker.

### Step 3: Validate

Check required fields:
- Title present
- Type valid (enhancement, bug, feature)
- Body not empty (for bugs)

### Step 4: File Issue

```bash
# ALL agents — private-first routing (L638)
gh issue create \
  --repo {private-tracker} \
  --title "$TITLE" \
  --body "$BODY" \
  --label "type:$TYPE"
```

### Step 5: Report

Output:
```
Issue filed: <URL>
Destination: {private-tracker}
Type: <type>
```

## Output Format

```markdown
## Issue Filed

| Field | Value |
|-------|-------|
| URL | https://github.com/{private-tracker}/issues/456 |
| Destination | {private-tracker} |
| Type | enhancement |
```

## Promotion to Public (Separate Workflow)

To make a private issue publicly visible on `aget-framework/aget`:

1. Get **principal approval** (R-ISSUE-011)
2. Run sanitization check (R-ISSUE-012):
   ```bash
   echo "issue body" | python3 .aget/patterns/github/sanitize_issue_content.py --check
   ```
3. Create public issue with **source reference** (R-ISSUE-013)
4. Verify **no private identifiers** in promoted content (R-ISSUE-014)

### Sanitization Patterns (Promotion Boundary Only)

| Pattern | Replacement |
|---------|-------------|
| `private-*-aget` | `[PRIVATE-AGENT]` |
| `private-*-AGET` | `[PRIVATE-AGENT]` |
| `gmelli/*` | `[INTERNAL-REPO]` |
| `\d+ agents? in fleet` | `[N agents]` |
| `SESSION_\d{4}-\d{2}-\d{2}` | `[SESSION]` |
| `FLEET-\w+-\d+` | `[PROJECT-ID]` |

## Constraints

These are INVIOLABLE:

- **C1**: NEVER file directly to `aget-framework/aget` — ALL issues go to `{private-tracker}`
- **C2**: NEVER include private agent names in promoted public issues
- **C3**: NEVER include fleet size disclosures in promoted public issues
- **C4**: NEVER include internal repo references in promoted public issues
- **C5**: ALWAYS route to `{private-tracker}` regardless of agent type
- **C6**: ALWAYS validate destination before filing

## Examples

### Example 1: Private Agent Filing Enhancement

```
/aget-file-issue enhancement Add skill validation
```

**Result**: Files to `{private-tracker}` (no sanitization needed)

### Example 2: Public Agent Filing Bug

```
/aget-file-issue bug Template fails on Windows
```

**Result**: Files to `{private-tracker}` (same destination — L638 private-first)

### Example 3: Promoting a Private Issue

After principal approval, sanitized content filed to `aget-framework/aget` with reference to source issue in `{private-tracker}`.

## Error Handling

| Error | Response |
|-------|----------|
| No gh CLI | "Error: gh CLI not installed. Install via: brew install gh" |
| Not authenticated | "Error: gh not authenticated. Run: gh auth login" |
| Missing title | "Error: Title required. Usage: /aget-file-issue <type> <title>" |
| Invalid type | "Error: Invalid type. Use: enhancement, bug, feature" |

## Related

- L520: Issue Governance Gap
- L638: Private-First Issue Routing
- AGET_ISSUE_GOVERNANCE_SPEC v2.0.0: R-ISSUE-001 through R-ISSUE-014
- SKILL-040: aget-file-issue specification v1.1.0
- validate_issue_destination.py
- sanitize_issue_content.py

## Traceability

| Link | Reference |
|------|-----------|
| Spec | SKILL-040_aget-file-issue.yaml v1.1.0 |
| L-doc | L520 (Issue Governance Gap), L638 (Private-First Routing) |
| Governing Spec | AGET_ISSUE_GOVERNANCE_SPEC v2.0.0 |

---

*aget-file-issue v1.1.0*
*Category: Governance*
*Archetype: Universal*
