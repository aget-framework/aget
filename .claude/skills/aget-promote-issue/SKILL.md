# /aget-promote-issue

Promote issues from the private tracker (gmelli/aget-aget) to the public tracker (aget-framework/aget) through governed content sanitization and principal approval. Prevents private information leakage at the promotion boundary.

## Purpose

The private-first routing model (L638) means all issues start in `gmelli/aget-aget`. Some need public visibility. This skill governs that boundary crossing with content sanitization (R-ISSUE-011), principal approval, and source traceability.

## Input

`issue_number` - The private issue number to promote (required)

Examples:
- `/aget-promote-issue #834` — Promote issue 834
- `/aget-promote-issue #834 --dry-run` — Preview sanitized content without filing

## Execution

### Step 1: Read Source Issue

```bash
gh issue view {issue_number} --repo gmelli/aget-aget --json title,body,labels,state
```

Verify: issue exists, is open, belongs to `gmelli/aget-aget`.

### Step 2: Content Sanitization

Scan title and body for private patterns:

| Pattern | Example | Action |
|---------|---------|--------|
| Private agent names | `private-*-aget`, `private-*-AGET` | BLOCK |
| Private repo refs | `gmelli/*` | BLOCK |
| Fleet size | "32 agents", "40 agents" | BLOCK |
| Internal project IDs | `FLEET-*-###` | BLOCK |
| Session references | `SESSION_2026-*` | BLOCK |

If ANY pattern detected: display matches, ask user to revise source issue first.

### Step 3: Draft Promoted Content

- **Title**: Sanitized version of source title
- **Body**: Sanitized body + footer: `_Promoted from internal tracker._`
- **Labels**: Transfer `type:*` and `domain:*` labels. Do NOT transfer `owner:*` or `status:*`.

### Step 4: Principal Approval Gate

Display drafted content and checklist:

```
=== Promotion Preview: #{issue_number} ===

Title: {sanitized_title}
Body: {sanitized_body}
Labels: {transferred_labels}
Destination: aget-framework/aget

Checklist:
- [ ] Principal approval (R-ISSUE-011)
- [ ] Content sanitization passed (R-ISSUE-012)
- [ ] Source traceability included (R-ISSUE-013)
- [ ] Label mapping complete (R-ISSUE-014)

Proceed? [Y/N]
```

**WAIT** for explicit principal GO before filing.

### Step 5: File Public Issue

```bash
gh issue create --repo aget-framework/aget \
    --title "{sanitized_title}" \
    --body "{sanitized_body}" \
    --label "{labels}"
```

### Step 6: Cross-Reference

Add comment on private issue linking to public issue:

```bash
gh issue comment {issue_number} --repo gmelli/aget-aget \
    --body "Promoted to public: aget-framework/aget#{public_number}"
```

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-PROMOTE-001 | Skill SHALL scan for private patterns before promotion | R-ISSUE-011, L638 |
| REQ-PROMOTE-002 | Skill SHALL block on private pattern detection | R-ISSUE-012 |
| REQ-PROMOTE-003 | Skill SHALL require explicit principal approval | R-ISSUE-011 |
| REQ-PROMOTE-004 | Skill SHALL include source traceability in promoted issue | R-ISSUE-013 |
| REQ-PROMOTE-005 | Skill SHALL cross-reference private and public issues | R-ISSUE-014 |

## Constraints

- **C1**: MUST NOT file public issue without principal approval
- **C2**: MUST NOT transfer `owner:*` or `status:*` labels (private metadata)
- **C3**: MUST block if any private pattern detected — no override
- **C4**: MUST use `gh` CLI for all GitHub operations (ADR-004 tier)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not found | Wrong number or repo | Verify issue exists on gmelli/aget-aget |
| Private pattern detected | Unsanitized content | Edit source issue first, then re-promote |
| gh auth failure | Token expired | Run `gh auth login` |

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-004 |
| Spec | AGET_ISSUE_GOVERNANCE_SPEC v2.1.0 (CAP-ISSUE-005) |
| Requirements | R-ISSUE-011 through R-ISSUE-014 |
| L-docs | L638 (Private-First Routing), L674 (Bypass Incidents) |
| Sibling Skill | /aget-file-issue (filing, not promotion) |

---

*aget-promote-issue v0.1.0*
*Category: Governance*
*Enforcement: Advisory (ADR-008)*
