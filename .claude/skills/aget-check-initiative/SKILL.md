---
name: aget-check-initiative
description: Read-only cross-system coherence check for initiatives. Aggregates state from KB, GitHub, Linear, and Slack, then reports alignment and drift.
---

# /aget-check-initiative

Read-only cross-system coherence check for initiatives. Aggregates state across Systems of Record and the local KB, then reports alignment, drift, and gaps.

## Purpose

Checking initiative state today requires manual queries across 3-4 systems. The principal must context-switch between Linear, GitHub, Slack, and KB to build a coherent picture. This skill composes those reads into a single report, answering: "What is the current state of initiative X across all systems?"

This is the first skill implementing the SoR Consumer Pattern (L759). It reads from external systems but never writes to them.

**Evidence**: L759 (SoR Consumer Pattern), L760 (Initiative as Scope Modifier), L747 (Event Awareness SLA), L665 (File-and-Route). SOP_initiative.md v1.2.0 channel registry (#916).

## Input

$ARGUMENTS - Initiative name or ID

Examples:
- `/aget-check-initiative INIT-CORE-ARTIFACT-MATURATION` — Check specific initiative by ID
- `/aget-check-initiative voice framework` — Check by name (fuzzy match)
- `check initiative status` — Check all active initiatives
- `what's the state of the artifact maturation initiative?` — Natural language trigger

## Execution

### Step 1: Resolve Initiative

Find the initiative manifest:

1. Search `planning/initiatives/INIT-*.md` for matching ID or name
2. If no match, search `planning/PROJECT_PLAN_*.md` for initiative references
3. If still no match, report available initiatives and stop

Extract from the manifest:
- Initiative ID and name
- Stream list with expected status
- Channel registry (if `## Channels` section exists per SOP v1.1.0)

### Step 2: KB State Scan

Read local KB artifacts linked to the initiative:

| Artifact Type | Search Pattern | Extract |
|---------------|---------------|---------|
| PROJECT_PLANs | `planning/PROJECT_PLAN_*{initiative}*` | Gate status, velocity |
| L-docs | `initiative_id` in metadata | Count, latest date |
| Observations | `.aget/research/OBSERVATION_*` | Count, unprocessed count |
| Design directions | `docs/DESIGN_DIRECTION_*` | Status, version |
| Issues filed | Initiative label in issues | Open/closed counts |

### Step 3: External System Scan

Query each external system with graceful degradation (ADR-004 three-tier):

**GitHub** (via `gh` CLI):
```
gh issue list --repo gmelli/aget-aget --search "{initiative_id}" --state all
```

**Linear** (via MCP, if available):
- Query project matching initiative_id
- If MCP unavailable: report "Linear: unavailable (MCP not configured)"

**Slack** (via MCP, if available):
- Scan channels from the initiative's channel registry
- Primary channels: full scan. Secondary: summary. Monitor: latest only.
- If MCP unavailable: report "Slack: unavailable (MCP not configured)"

### Step 4: Coherence Analysis

Compare state across systems:

| Category | Definition |
|----------|-----------|
| **Aligned** | Item exists in all expected systems with consistent state |
| **Drifted** | Item exists in multiple systems but state is inconsistent |
| **Gap** | Item exists in one system but missing from others |

### Step 5: Report

```
=== Initiative: [name] ([initiative_id]) ===

KB State:
  - PROJECT_PLAN: [name] -- [status] (Gate X of Y)
  - L-docs: [N] related
  - Observations: [N] related
  - Design directions: [N]

GitHub State: [connected/unavailable]
  - Issues: [N] open / [N] closed
  - Drift: [items in GitHub not in KB]

Linear State: [connected/unavailable]
  - Project: [name] -- [N] open / [N] done
  - Drift: [items in Linear not in KB]

Slack State: [connected/unavailable]
  - Channels: [N] registered ([N] primary, [N] secondary, [N] monitor)

Coherence:
  - Aligned: [N] items consistent across systems
  - Drifted: [N] items with state mismatch
  - Gaps: [N] items in one system but missing from others

Overall: [COHERENT / DRIFT DETECTED / GAPS FOUND]
```

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-CHKI-001 | Check-initiative SHALL read from KB, GitHub, Linear, and Slack | SP-004b, L759 |
| REQ-CHKI-002 | Check-initiative SHALL degrade gracefully when external systems are unavailable | ADR-004, L759 |
| REQ-CHKI-003 | Check-initiative SHALL classify items as aligned, drifted, or gap | SP-004b |
| REQ-CHKI-004 | Check-initiative SHALL NOT write to any external System of Record | L759 (read-only) |
| REQ-CHKI-005 | Check-initiative SHALL discover channels from initiative manifest registry | SOP_initiative v1.1.0, #916 |
| REQ-CHKI-006 | Check-initiative SHALL fall back to pattern matching if no channel registry exists | SP-004b (backward compat) |
| REQ-CHKI-007 | Check-initiative SHALL report overall coherence status | SP-004b |

## Constraints

- **C1**: Read-only — MUST NOT write to any external SoR (GitHub, Linear, Slack). Reports only. The `sync` verb is reserved (L759) for future write capability.
- **C2**: Session-scoped caching only — no persistent external state stored in KB
- **C3**: Fresh pull on each invocation — no background polling or stale cache
- **C4**: MUST report system availability status even when degraded — "unavailable" is a valid report, silence is not

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-004b (`planning/skill-proposals/PROPOSAL_aget-check-initiative.md`) |
| SoR Consumer Pattern | L759 (first skill implementing this pattern) |
| Entity model | L760 (Initiative as Scope Modifier) |
| Channel discovery | #916, SOP_initiative.md v1.2.0 Step 2.5 |
| Degradation model | ADR-004 (three-tier: MCP -> CLI -> KB-only) |
| L-docs | L759, L760, L747 (Event Awareness SLA), L665 (File-and-Route) |

---

*aget-check-initiative v0.1.0*
*Category: Governance*
*Pattern: SoR Consumer (L759) -- read-only cross-system aggregation*
