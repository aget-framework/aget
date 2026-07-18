---
name: aget-describe-session
description: Generate a readable narrative summary from structured session data. Converts table-heavy session state into prose optimized for human consumption.
---

# /aget-describe-session

Generate a readable narrative summary from structured session data. Converts table-heavy session artifacts into prose optimized for human scanning.

## Purpose

AGET sessions produce structured output (frontmatter, tables, bullet lists, commit logs) that is machine-parseable but hard for humans to read at a glance. This skill transforms structured session artifacts into narrative prose that conveys the same information in a form a principal or collaborator can scan quickly.

**Evidence**: Principal feedback (2026-04-10) — "this report is hard to read" on a 7-row table summarizing 7 sequential steps, where 2 lines of prose conveyed the same information more clearly. Tables are effective for comparison data (rubric scores, deployment status). Prose is effective for sequential narratives (what happened, what was decided, what's next).

## Input

$ARGUMENTS

Parameters (all optional):

| Parameter | Values | Default | Purpose |
|-----------|--------|---------|---------|
| `--source` | Session file path or `current` | `current` | Which session to describe |
| `--length` | `brief`, `standard`, `detailed` | `standard` | Narrative depth |

Examples:
- `/aget-describe-session` — Describe current session in standard length
- `/aget-describe-session --source sessions/SESSION_2026-04-10_1400.md` — Describe a prior session
- `/aget-describe-session --length brief` — Short 1-2 paragraph summary of current session

## Execution

### Step 1: Resolve Source

Determine the session to describe:

| Source | Resolution |
|--------|-----------|
| `current` (default) | Synthesize from conversation context — what was worked on, decisions made, artifacts produced |
| Session file path | Read the specified session record from `sessions/` |
| `latest` | Find most recent `sessions/SESSION_*.md` by date |

**Verify**: Confirm source material exists. If describing current session, verify there is meaningful work to describe (not just wake-up).

### Step 2: Extract Narrative Elements

From the source, extract:

1. **Arc**: What was the session's goal? What happened? How did it end?
2. **Decisions**: Key choices made and their rationale
3. **Artifacts**: What was created, modified, or deployed
4. **Discoveries**: Patterns found, lessons learned, surprises encountered
5. **Next**: What follows from this session's work

### Step 3: Compose Narrative

Write narrative prose following the `--length` parameter:

| Length | Target | Structure |
|--------|--------|-----------|
| `brief` | 2-4 sentences | Single paragraph: goal + outcome + next |
| `standard` | 3-5 paragraphs | Opening (goal + context), body (work + decisions), closing (outcomes + next) |
| `detailed` | 5-8 paragraphs | Full arc with evidence citations, decision rationale, and artifact inventory |

**Format rules**:
- Use prose, not tables — tables are for `check` and `review` skills
- Use transitions that convey sequence: "Starting with...", "This led to...", "The session concluded with..."
- Include specific artifact names and counts where relevant
- Do NOT include governance ceremony (gate refs, spec IDs, EARS patterns)

### Step 4: Present

Display the narrative directly in conversation. Do NOT write to a file unless the user explicitly asks.

If the user wants a file, write to `docs/briefings/SESSION_NARRATIVE_YYYY-MM-DD_{theme}.md`.

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-DESC-001 | Describe SHALL produce narrative prose, not tables or bullet lists | SP-009, principal feedback |
| REQ-DESC-002 | Describe SHALL include session arc (goal, work, outcome) | SP-009 |
| REQ-DESC-003 | Describe SHALL include key decisions with rationale | SP-009 |
| REQ-DESC-004 | Describe SHALL list artifacts produced with counts | SP-009 |
| REQ-DESC-005 | Describe SHALL NOT modify any source artifacts | Read-only principle |
| REQ-DESC-006 | Describe SHALL strip governance ceremony from output | SP-009 (no CAP-xxx, R-xxx, EARS, V-tests) |
| REQ-DESC-007 | Describe SHALL respect --length parameter for output depth | SP-009 |

## Constraints

- **C1**: Read-only — MUST NOT modify session files or any KB artifacts
- **C2**: Output is prose, not structured data — tables are prohibited in output (use `/aget-review-project` for tabular session data)
- **C3**: MUST NOT fabricate session events — every claim must trace to conversation context or session file content
- **C4**: MUST NOT include governance ceremony (gate references, spec IDs, V-test results, EARS patterns) in output

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-009 (`planning/skill-proposals/PROPOSAL_aget-describe-session.md`) |
| Verb vocabulary | DESIGN_DIRECTION_skill_verb_vocabulary.md (`describe`: reserved #5) |
| L-docs | L670 (Session Quality Assessment Gap) |
| Related skills | `/aget-close-session` (SP-008, may delegate to describe-session for Phase 3 narrative) |
| Future family | `describe-project`, `describe-skill` (same `describe` verb pattern) |

---

*aget-describe-session v0.1.0*
*Category: Session*
*Verb: describe (narrative synthesis from structured data)*
