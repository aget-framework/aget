---
name: aget-enhance-health
description: Remediate health drift detected by /aget-check-health. Applies Tier A/B/C severity routing per DESIGN_DIRECTION §Principle 9 (canonical check → enhance pipeline). Generator layer (ADR-008) sibling to /aget-check-health.
version: 1.0.0
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# /aget-enhance-health

Remediate agent health drift. Consumes `/aget-check-health` output, classifies findings by severity Tier (A/B/C), applies Tier-A in-skill, routes Tier-B to backlog, escalates Tier-C via `/aget-file-issue`, and re-verifies. Instantiates the canonical `check → enhance` pipeline (DESIGN_DIRECTION §Principle 9) for the health domain.

This is the **Generator layer** (ADR-008 step 3), built on `/aget-check-health` (Advisory/detect) and `scripts/health_check.py` (implementation substrate). Governing spec: AGET_SESSION_SPEC CAP-SESSION-014.

## Input

$ARGUMENTS - Optional check-health output path or invocation flag.

Format:
- `/aget-enhance-health` — run `/aget-check-health` inline, then enhance
- `/aget-enhance-health <path-to-json>` — consume pre-existing check output
- `/aget-enhance-health --tier A` — apply only Tier-A remediations (skip B/C)
- `/aget-enhance-health --dry-run` — classify findings but do not remediate

## Execution

### Phase 0: Diagnose

**Objective**: Obtain current check-health state. Either consume existing output or run inline.

Execute:
1. Check for input JSON path in arguments
2. If no input, invoke `/aget-check-health --json` and capture output:
   ```bash
   python3 scripts/health_check.py --json > /tmp/aeh_check_$$.json
   ```
3. Parse findings — enumerate each WARN and ERROR
4. If no findings (status = HEALTHY): report "No remediation needed" and exit with Skill Completion Signal

**User Checkpoint**: Present findings summary:
```
Health Check Findings:
  Status: [HEALTHY/WARNINGS/ERRORS]
  WARN count: <n>
  ERROR count: <n>

Proceed to classification? (yes/adjust/abort)
```

**Exit Criteria**: Findings captured. User approved progression or skill exited clean.

### Phase 1: Classify (Tier A/B/C)

**Objective**: Assign severity Tier to each finding per DESIGN_DIRECTION §enhance verb model.

Execute:
1. For each finding, evaluate:
   - **Tier-A** (trivially fixable, applied in-skill): ALL of (a) reversible via `git revert`, (b) bounded to invoking agent's tree, (c) idempotent
   - **Tier-B** (structural-bounded, routed to backlog): affects single artifact but needs broader review or cross-agent input
   - **Tier-C** (scope-affecting, escalated via issue): multi-agent, multi-repo, or policy-level implications
2. If a finding is ambiguous between Tiers, default to the **higher** Tier (more cautious) and document ambiguity
3. Produce classification table:
   ```
   | # | Finding | Tier | Rationale | Proposed Action |
   |---|---------|:-:|-----------|-----------------|
   ```

**User Checkpoint**: Present classification table and ask:
```
Classifications: <A-count> Tier-A, <B-count> Tier-B, <C-count> Tier-C

Approve classification and proceed to census? (yes/reclassify/abort)
```

**Exit Criteria**: Every finding has Tier assignment. User approved classification.

### Phase 2: Census

**Objective**: Inventory all artifacts affected by the remediation plan.

Execute:
1. For each Tier-A finding, enumerate target files and dependencies
2. Read current file state (NEVER assert from memory — L611)
3. Produce census table:
   ```
   | Finding | Target Artifact | Current State | Remediation Action |
   |---------|-----------------|---------------|---------------------|
   ```

**Exit Criteria**: All Tier-A target artifacts inventoried with current state read from files.

### Phase 3: Apply Tier-A Remediations

**Objective**: Remediate Tier-A findings idempotently with reversible changes.

Execute per Tier-A finding:
1. Present the proposed change to the user (diff format preferred)
2. **User Checkpoint**: "Apply this change? (yes/skip/abort)"
3. On yes: apply change via Edit tool (idempotent)
4. Record: file path, digest before/after, reversal command (`git revert <sha>` or `Edit` reverse)
5. Continue to next finding

**Governance boundary** (R-013 / CAP-SESSION-014-07): SKILL SHALL NOT modify files outside the invoking agent's tree. If a remediation requires cross-agent or cross-repo edits, promote to Tier-C.

**Exit Criteria**: All approved Tier-A changes applied. Decision Log records each change with reversal path.

### Phase 4: Route Tier-B to Backlog

**Objective**: Capture Tier-B findings in planning/ backlog for structured follow-up.

Execute:
1. Check for existing `planning/BACKLOG_health_*.md` file
2. If none exists, create `planning/BACKLOG_health_YYYY-MM-DD.md`
3. For each Tier-B finding, append entry:
   ```markdown
   ## BL-<datestamp>-<NNN>: <Finding title>
   - **Severity**: Tier-B
   - **Evidence**: <L-doc or artifact>
   - **Problem**: <statement>
   - **Proposed action**: <action>
   - **Filed by**: /aget-enhance-health on <date>
   ```
4. Record backlog file path in Decision Log

**Exit Criteria**: All Tier-B findings written to backlog with problem/action/evidence.

### Phase 5: Escalate Tier-C via Issue

**Objective**: File issues for Tier-C findings via STRUCTURAL skill routing.

**Governance** (C-EH-002 inviolable): MUST invoke `/aget-file-issue`; MUST NOT invoke `gh issue create` directly (D71 STRUCTURAL).

Execute per Tier-C finding:
1. Compose issue body: finding summary, impact assessment, evidence chain (L-docs/artifacts), proposed scope
2. Invoke `/aget-file-issue <type> <title>` with composed body
3. Capture returned issue number (e.g., `gmelli/aget-aget#NNNN`)
4. Record in Decision Log

**Exit Criteria**: All Tier-C findings escalated via `/aget-file-issue`. Issue numbers captured.

### Phase 6: Re-verify

**Objective**: Confirm Tier-A remediations resolved the reported drift.

Execute:
1. Re-invoke `/aget-check-health --json`:
   ```bash
   python3 scripts/health_check.py --json > /tmp/aeh_recheck_$$.json
   ```
2. Compare against Phase 0 output:
   - Findings that were Tier-A: confirm resolved (absent from re-check)
   - Findings that were Tier-B/C: expected to persist (not remediated this cycle)
3. Report delta:
   ```
   Re-verification delta:
     Tier-A findings at Phase 0: <n>
     Tier-A findings at Phase 6: <m> (expect 0 — else flag incomplete)
     Tier-B findings (unchanged, routed to backlog): <n>
     Tier-C findings (unchanged, escalated via issue): <n>
   ```
4. If any Tier-A finding persists, surface to user as incomplete remediation

**Exit Criteria**: Re-verification executed. Delta reported. Incomplete remediations flagged.

## Triggers

When user says:
- "enhance health"
- "remediate health drift"
- "heal this agent"
- "fix drift"
- "apply health remediations"

## Scope Boundary

**Does**:
- Remediate agent instance health drift (config, structure, version, identity, governance integrity)
- Apply Tier-A fixes in-skill (idempotent, reversible via git)
- Route Tier-B findings to `planning/BACKLOG_health_*.md`
- Escalate Tier-C findings via `/aget-file-issue` (D71 STRUCTURAL)
- Re-verify via `/aget-check-health` after Tier-A application

**Does NOT**:
- Detect issues (delegated to `/aget-check-health`)
- Modify specs (delegated to `/aget-enhance-spec`)
- Remediate cross-artifact coherence (delegated to `/aget-enhance-coherence`)
- Remediate CI/test failures (out of scope; future `/aget-enhance-ci` candidate)
- Modify files outside the invoking agent's tree (governance boundary — CAP-SESSION-014-07)
- Invoke `gh issue create` directly (D71 STRUCTURAL — route via `/aget-file-issue`)

## Constraints

These are INVIOLABLE — SKILL MUST NOT violate these:

1. **C1**: SKILL SHALL NOT modify files outside the invoking agent's tree (CAP-SESSION-014-07)
2. **C2**: SKILL SHALL NOT invoke `gh issue create` directly; MUST route via `/aget-file-issue` (D71 STRUCTURAL)
3. **C3**: SKILL SHALL NOT assert file state from memory; MUST read files (L611)
4. **C4**: Tier-A classifications SHALL meet reversibility + boundedness + idempotence criteria (R-005)
5. **C5**: SKILL SHALL present a user checkpoint at Phase 0, Phase 1, and Phase 3
6. **C6**: SKILL SHALL emit Skill Completion Signal (D71 Layer 3) as last output section
7. **C7**: SKILL SHALL NOT attempt Phase B (scripts/enhance_health.py) or Phase C (--enhance shortcut) — evidence-gated for later releases per SP-023 incrementality and L103

## Anti-Pattern Detection

| Anti-Pattern | Phase | Detection |
|--------------|:-----:|-----------|
| Memory-Based Assertions (L611) | 2, 3 | File state claimed without read |
| Classification Without Consequence (L671) | 1 | Tier assigned but no downstream action |
| Loading Dock (L656) | 3 | Remediation "applied" but not committed/verified |
| Decorative Escalation | 5 | Tier-C flagged but no issue filed via `/aget-file-issue` |
| Premature Abstraction (L103) | N/A | Attempting Phase B/C before Phase A dogfood evidence |
| Test Theater (ADR-007) | 6 | Re-verification claims PASS without actually running check-health |

## Skill Completion Signal (D71 Layer 3)

**Purpose**: Make skill execution completeness structurally visible. If this signal is absent from the skill output, the skill execution is incomplete.

The skill MUST output this signal as the LAST section of the report:

```markdown
## Skill Completion Signal
**Phase 0 (Diagnose)**: PASS (findings: N WARN, M ERROR) | SKIP (HEALTHY — no remediation needed)
**Phase 1 (Classify)**: PASS (Tier-A: A, Tier-B: B, Tier-C: C) | ABORT (user rejected classification)
**Phase 2 (Census)**: PASS (N artifacts inventoried)
**Phase 3 (Apply Tier-A)**: PASS (N applied, M skipped) | SKIP (no Tier-A findings)
**Phase 4 (Route Tier-B)**: PASS (N entries in planning/BACKLOG_health_*.md) | SKIP (no Tier-B)
**Phase 5 (Escalate Tier-C)**: PASS (N issues filed) | SKIP (no Tier-C)
**Phase 6 (Re-verify)**: PASS (Tier-A delta: -N) | FAIL (N Tier-A findings persist)
**Phases Completed**: 0→1→2→3→4→5→6
```

If any phase is SKIP, the signal MUST state the reason. If any phase is FAIL, the signal MUST identify the specific failure.

**Enforcement**: Strict (ADR-008, D71). Signal absence = incomplete execution.

## Related Skills

- `/aget-check-health` (SKILL-003) — pair sibling, detect layer (Advisory); consumed by this skill
- `/aget-enhance-spec` (SKILL-041) — parallel pattern (artifact-level L622 enhancement lifecycle)
- `/aget-enhance-config` (#614, in-dev) — config-level sibling (enhance-verb family)
- `/aget-enhance-coherence` (VERSION_SCOPE v3.15.0 P2 #13) — framework-level sibling
- `/aget-file-issue` — Tier-C escalation (STRUCTURAL per D71)
- `/aget-create-project` — invoked if Tier-B accumulates beyond backlog threshold

## Traceability

| Link | Reference |
|------|-----------|
| Governing Spec | AGET_SESSION_SPEC CAP-SESSION-014 (Health Remediation Protocol) |
| Sibling Spec | AGET_SESSION_SPEC CAP-SESSION-008 (Sanity Check Protocol — consumed by this skill) |
| Skill Spec | SKILL-049 (`.aget/specs/skills/SKILL-049_aget-enhance-health.yaml`) v1.0.0 |
| Parent Proposal (skill) | SP-023 (self-scored 27/27 on RUBRIC_skill_proposal_readiness_v1.0) |
| Parent Proposal (project) | PP-006 (promoted) |
| Implementation Plan | AEH-001 (`planning/PROJECT_PLAN_aget_enhance_health_skill_v1.0.md`) |
| Pattern Template | SKILL-041 `/aget-enhance-spec` v1.1.0 |
| Verb | `enhance` (#9, Lifecycle, approved via DESIGN_DIRECTION row 46) |
| Pipeline | check → enhance (DESIGN_DIRECTION §Principle 9, 2026-04-19) |
| Tier Model | DESIGN_DIRECTION §enhance verb (Tier A/B/C routing) |
| ADR | ADR-008 (Generator layer); ADR-007 (no test theater); D71 (structural routing) |
| L-docs | L867 (enhance-verb family), L656 (Loading Dock — replaces unimplemented --fix), L671 (decorative classification), L622 (11-phase spec enhancement), L103 (premature abstraction), L611 (memory-based assertions) |
| Tracking Issue | gmelli/aget-aget#1081 |

---

*aget-enhance-health v1.0.0*
*Category: Governance (Health Maintenance)*
*"Check detects; enhance heals."*
