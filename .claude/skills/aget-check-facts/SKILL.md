---
name: aget-check-facts
description: Verify factual claims using a stratified 3-pass protocol (data, logic, propagation). Layer 2 Pre-Assertion Gates for the anti-confabulation architecture.
---

# /aget-check-facts

Verify factual claims using a stratified 3-pass protocol. Operationalizes the conversational assertion provenance gap (L803) as structured verification.

## Purpose

V-tests gate artifacts and ground-truth checks gate handoffs, but nothing gates mid-conversation factual claims. Unverified assertions propagate through a chain: conversation -> session record -> L-doc -> CLAUDE.md -> fleet-wide behavior. Cross-fleet evidence (4+ agents across 2+ fleets) independently identified this as a structural deficiency.

**Evidence**: L803 (Conversational Assertion Provenance Gap), L801 (Cross-Fleet False Positive — asserted "12/17 L-doc citations are fabricated" without verifying it was checking the wrong L-space), L756 (AGCI Verification Protocol), L802 (Convergent Architecture across 4+ agents), L807 (Incident Density = Urgency, 3x in one session), L782/remote (Stratified 3-pass discovery). CCB INTEL-002 (21 documented incidents).

## Input

$ARGUMENTS

Parameters:

| Mode | Trigger | Scope |
|------|---------|-------|
| **Self-check** | `/aget-check-facts` (no args) | Review own recent assertions in conversation |
| **Targeted** | `/aget-check-facts [claim]` | Verify specific claim |
| **Artifact** | `/aget-check-facts --file [path]` | Verify claims in a session file or L-doc |

Examples:
- `/aget-check-facts` — Self-check recent conversation assertions
- `/aget-check-facts the fleet has 34 agents` — Verify specific claim
- `/aget-check-facts --file sessions/SESSION_2026-04-10_1400.md` — Verify claims in artifact
- `check facts` — Natural language trigger
- `verify that` — Alias for targeted check

## Execution

### Step 1: Identify Claims

Extract factual claims from the scope:

| Scope | Extraction Method |
|-------|------------------|
| Self-check | Scan own recent conversation messages for entity names, dates, counts, identifiers, and causal assertions |
| Targeted | Parse the specific claim from $ARGUMENTS |
| Artifact | Read file, extract assertions containing names, dates, counts, identifiers |

A "claim" is any assertion containing: entity names, dates, counts, identifiers, or causal relationships.

### Step 2: Pass 1 -- Data Verification

For each claim, trace every noun-claim to its source:

**Gate question**: "Can I cite file:line, commit, or user statement for every entity name, date, count, and identifier?"

| Check | Method | Failure Mode Prevented |
|-------|--------|----------------------|
| Entity names | Grep KB for exact match | Wrong names, wrong attributions (L781) |
| Dates | Verify against file timestamps or frontmatter | Temporal confusion |
| Counts | Count actual items (ls, grep -c) | Wrong counts (L801) |
| Identifiers | Verify ID exists in expected location | Cross-scope conflation (L794) |

Record provenance for each datum: `{file:line | commit:hash | user-stated | inferred}`

### Step 3: Pass 2 -- Logic Verification

For claims that passed data verification, check inferences:

**Gate question**: "Does my conclusion follow from the data, or am I building a story?"

| Check | Detection | Failure Mode Prevented |
|-------|-----------|----------------------|
| Causal claims | Does A actually cause B, or just correlate? | Fabricated root causes (L644) |
| Narrative drift | Does conclusion match evidence, or fill a gap? | Minimum-edit bias (L780) |
| Premise chain | Are all premises verified, not just the conclusion? | Premise preservation under correction (L780/remote) |

### Step 4: Pass 3 -- Propagation Assessment

For claims that passed logic verification, assess downstream impact:

**Gate question**: "If this assertion is wrong, where will it propagate?"

| Impact Level | Definition | Response |
|--------------|-----------|----------|
| Low | Conversation-only, no persistence | Note uncertainty |
| Medium | May enter session record or L-doc | Downgrade with "[inferred, unverified]" |
| High | May propagate to CLAUDE.md or fleet behavior | Flag as CRITICAL, require verification |

### Step 5: Report

```
=== /aget-check-facts: [scope] ===

Claims checked: [N]

| # | Claim | Data | Logic | Propagation | Status |
|---|-------|:----:|:-----:|:-----------:|:------:|
| 1 | [claim summary] | PASS | PASS | PASS | OK |
| 2 | [claim summary] | FAIL | -- | -- | WARN |
| 3 | [claim summary] | PASS | PASS | FAIL | WARN |

Downgraded assertions:
- [claim]: "[inferred, unverified]" -- [reason]

Overall: [OK | WARN | CRITICAL]
```

### Conversational Micro-Gate (L803)

After verification, apply the micro-gate to any future assertions about the checked topics:

1. **Scope**: Am I the authoritative source for this claim?
2. **Provenance**: Can I cite the source?
3. **Recency**: Is my source current?

If any check fails, downgrade: "I believe X [inferred, unverified]" rather than "X is true."

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-CF-001 | Check-facts SHALL execute 3 sequential passes (data, logic, propagation) | L782/remote, SP-007 |
| REQ-CF-002 | Pass 1 SHALL trace every entity name, date, count, and identifier to source | L803, L781 |
| REQ-CF-003 | Pass 2 SHALL verify inferences follow from verified data | L644, L780 |
| REQ-CF-004 | Pass 3 SHALL assess downstream propagation impact of uncertain claims | L658, L794 |
| REQ-CF-005 | Check-facts SHALL downgrade unverified assertions with explicit uncertainty markers | L803 (micro-gate) |
| REQ-CF-006 | Check-facts SHALL support self-check, targeted, and artifact modes | SP-007 |
| REQ-CF-007 | Check-facts SHALL NOT modify source artifacts — read-only verification | Read-only principle |

## Constraints

- **C1**: Read-only — MUST NOT modify any KB artifacts, session files, or L-docs during verification
- **C2**: Passes MUST execute in order (data -> logic -> propagation) — later passes depend on earlier results
- **C3**: If Pass 1 fails for a claim, skip Passes 2-3 for that claim (data failure makes logic/propagation checks meaningless)
- **C4**: MUST NOT produce false confidence — "skill ran" does NOT mean "claims are verified" (L284 Delegation Theater guard)

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-007 (`planning/skill-proposals/PROPOSAL_aget-check-facts.md`) |
| Anti-confabulation layer | Layer 2 (Pre-Assertion Gates) |
| Architecture | DESIGN_DIRECTION_anti_confabulation_architecture.md |
| Cross-fleet evidence | Framework-AGET L801/L803, CCB INTEL-002 (21 incidents), Remote fleet L782 |
| Upstream issues | #877 (anti-confab codification), #878 (D8 epistemic measurement), #907-#909 |
| L-docs | L803 (Assertion Provenance Gap), L801 (Cross-Fleet False Positive), L756 (AGCI), L802 (Convergent Architecture), L807 (Incident Density), L782/remote (Stratified Passes) |
| Anti-patterns prevented | L736 (Assert-Before-Verify), L644 (Fabricated Diagnosis), L780 (Premise Preservation), L658 (Unverified Propagation) |

---

*aget-check-facts v0.1.0*
*Category: Quality*
*Anti-Confabulation Architecture: Layer 2 (Pre-Assertion Gates)*
