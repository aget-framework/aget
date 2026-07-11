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

### Step 2.5: Resolve Routing Mode (v3.26 C-26-02 — #1845 fleet-universal supervisor relay)

**Principal MC ruling (2026-07-05, enacted this cycle): no managed agent files issues directly — all filings relay through the managing supervisor.** Supervisors are the filing authority (they file for themselves AND their managed agents).

Resolve the invoking seat + mode:

| Invoking seat | Resolved routing_mode | Step 4 behavior |
|---------------|----------------------|-----------------|
| **Supervisor seat** (archetype supervisor / manages agents) | `direct` | file via `gh issue create` as below |
| **Managed agent** (has a `Managed By:` supervisor) | `supervisor_intake` (the flipped default) | **produce an INTAKE ARTIFACT, do NOT `gh issue create`** |
| Managed agent, **principal-supervised session** (principal present and directing the filing) | `direct` permitted | file directly; record `routing_mode: direct (principal-supervised)` in the body |
| Explicit `routing_mode:` in the request | as declared | honor it (lesson_first/supervisor_editorial per CAP-ISSUE-011..014) |

**Intake artifact contract (seat-side half only — queue/batching design is supervisor-lane, #1845)**: write the complete issue (title, body, labels, `routing_mode: supervisor_intake`) to `inbox/outbound/ISSUE_INTAKE_<YYYY-MM-DD>_<slug>.md` in the AGENT'S OWN repo (L480 — no cross-fleet write; the supervisor sweeps managed repos / IAC channel). The artifact IS the filing event for the agent; the `gh` filing is the supervisor's act.

> Spec basis: enacted ruling #1845 (R8); the R-ISSUE-030 default-flip spec delta rides this cycle's `/aget-enhance-spec` pass — until that lands, this skill section is the operative surface (L644-conformant: skill layer, not direct spec edit). Fleet-wide AGENTS.md propagation = next cycle (D-26-4).

### Step 3: Validate

Check required fields:
- Title present
- Type valid (enhancement, bug, feature)
- Body not empty (for bugs)

### Step 3.5: Pre-Filing Verify-Before-Claim Probe (v3.26 C-26-13 — gh#1855, coverage-matrix channel 1)

Before ANY filing (direct or intake-artifact), run BOTH probes and record results in the issue body or intake artifact. Three-state reporting per CONVENTION_check_three_state_contract (PASS / FAIL / UNREACHABLE — an unreachable tracker is not a clean probe).

**Probe A — Dedup (novelty claim)**: search the destination tracker for existing issues on the same subject:

```bash
gh issue list --repo <destination> --search "<title keywords>" --state all --limit 10
```

- Hit on same subject → STOP: comment on / reopen the existing issue instead, or explicitly record the adjacent-distinct disposition ("#NNNN is X, this is Y") in the new issue body.
- No hit → record "dedup-probed: no existing tracker" (one line suffices).
- Tracker unreachable → UNREACHABLE recorded; filing may proceed but the body carries the unprobed state honestly.

**Probe B — Target existence (existence claim)**: any spec, script, skill, path, or artifact the issue names as its TARGET (the thing to be fixed/extended/implemented-against) MUST be verified to exist before filing — `ls` / `grep` the path, or read the artifact header at source. An issue filed against a non-existent canonical target is the field failure this step exists to end (2026-07-10: filing against a non-existent canonical spec; a dedup-less re-proposal of an already-ruled p1).

- Named target verified → cite what was checked ("target verified: `path` exists, header vN.N").
- Named target absent → the issue's ask changes (it becomes "create X", not "fix X") — reframe before filing.

Reference impl: legalon `issue_freshness.py` (producer-ref-impl pattern). Spec basis: skill-layer gate per this convention; **R-ISSUE-034 spec delta rides the next AGET_ISSUE_GOVERNANCE_SPEC enhance-spec pass** (L644 — registered, not silently enacted; same precedent as Step 2.5's R-ISSUE-030 rider).

### Step 4: File Issue (direct-mode seats ONLY — Step 2.5 gates this)

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
- **C7**: MUST run the Step 3.5 dedup + target-existence probes before any filing or intake-artifact write (v3.26 C-26-13); results recorded in the body. On probe FAIL (duplicate found / target absent), filing is blocked pending disposition or reframe.

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
