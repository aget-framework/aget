---
name: aget-record-lesson
description: Record lessons learned from sessions as persistent, searchable, committable artifacts. Classifies each lesson as Framework (help other AGETs) or Domain (help principal).
version: 1.0.1
---

# /aget-record-lesson

Record lessons learned as structured L-docs in the git repo. Each lesson is classified to determine storage location and ID scheme.

## Purpose

Capture learnings in a persistent, searchable format that survives context windows and session boundaries. Enables knowledge accumulation across sessions.

## Input

$ARGUMENTS - Optional lesson description or trigger context

## Execution

### Step 1: Gather Context

Identify what triggered the lesson:
- Session observation
- User feedback
- Error encountered
- Pattern discovered
- Process improvement

### Step 2: Classify the Lesson

Classify each distinct lesson using the rubric below. **An explicit principal classification takes
precedence**; do not ask the principal to confirm a classification already supplied. Seat identity is
context, not evidence of who benefits. A local incident can establish a portable lesson; a lesson from a
framework-manager can remain Domain.

#### Classification rubric

Judge the core lesson, not the example's vocabulary. For each dimension record a short evidence-based
answer internally; use Unknown when evidence is insufficient. These are decision criteria, not points
that can compensate for a contradictory answer.

| Dimension | Framework evidence | Domain evidence |
|---|---|---|
| Portability | Another AGET with a different principal and domain can apply the corrective rule unchanged | The useful rule depends on this principal, client, platform configuration, or subject matter |
| Local dependence | Removing identifying details leaves a specific, actionable agent/process lesson | Removing local facts removes the useful content; a generic slogan is not a portable lesson |
| Routing consequence | An L-doc would improve agent verification, coordination, governance, or reusable operation | A local knowledge pattern would help the principal operate or understand the domain |

**Obvious Framework**: an actionable portable rule survives removal of local details and its useful
consequence is agent/process improvement, with no material contrary evidence. Record Framework directly.
**Obvious Domain**: the useful content is the local/domain fact or procedure and no substantive portable
agent lesson remains. Record Domain directly. Do not manufacture a Framework abstraction from every fact.
**Mixed**: both a portable rule and independently useful local knowledge deserve preservation. Recommend
Split with the proposed boundary; confirm the two outputs unless the principal already authorized them.
**Ambiguous**: an Unknown or contradiction changes the storage/routing choice. Ask one focused question
about that distinction, with a recommendation; do not present an unexplained taxonomy menu. For multiple
lessons, record the obvious ones and bundle only the unresolved classifications into one question.

For obvious cases, the completion report states the classification and one-line rationale; no pre-write
confirmation is required. High/medium/low confidence may describe the evidence but never replaces the
rubric. Keep the classification correctable; do not renumber, move, or split existing records silently.

Routing remains: Framework -> `.aget/evolution/L###_*.md` with an ID and index entry (Steps 3 and 5);
Domain -> `knowledge/patterns/*.md`; Split -> one of each after its boundary is settled.
Classification authorizes neither an otherwise prohibited path nor external filing, publication,
cross-seat writes, or instruction changes. If the chosen destination requires approval, prepare the
record and request that actual write approval; do not recast it as classification uncertainty.

#### Calibration examples

| Evidence supplied with “record lesson” | Decision |
|---|---|
| An enabled notification setting was called working without checking event wiring; direct playback later succeeded | Framework: distinguish configured, invoked, executed, and observed behavior; record without another question |
| A particular laptop's working output device and volume setting | Domain: preserve local operating facts; the recording agent's archetype does not change that |
| A reusable retry rule plus a client's independently valuable rate-limit configuration | Propose Split; ask about the two-output boundary if not already authorized |
| “The alerts are broken” with no mechanism or usable domain detail | Ask for the missing distinction; do not invent a learned rule or confidently classify from the word “alerts” |
| Principal says “Framework” for a supplied lesson | Record Framework; no repeat confirmation |

This rubric is a decision aid, not measured classification accuracy. Validate future use by whether clear
cases complete without a classification turn and ambiguous cases surface the relevant distinction.

### Step 3: Get Next ID (Framework only)

```bash
# Read next_id from index.json
jq '.next_id' .aget/evolution/index.json
```

### Step 4: Create Lesson Document

**Framework Template** (`.aget/evolution/L{ID}_{name}.md`):

```markdown
# L{ID}: {Title}

**Date**: {YYYY-MM-DD}
**Type**: Lesson Learned
**Category**: {category}
**Status**: complete

---

## Summary

{One paragraph summary of the lesson}

---

## Context

{What triggered this lesson? What were you doing?}

---

## Key Finding

{The core insight or learning}

---

## Implications

{What should change as a result?}

---

## Traceability

| Link | Reference |
|------|-----------|
| Session | {session file if applicable} |
| Project | {project plan if applicable} |
| Trigger | {what prompted this lesson} |

---

*L{ID}: {Title}*
*Category: {category}*
```

**Domain Template** (`knowledge/patterns/{category}/{name}.md`):

```markdown
# {Title}

**Created**: {YYYY-MM-DD}
**Category**: {category}
**Type**: Domain Knowledge

---

## Summary

{Description}

---

## Details

{Full content}

---
```

### Step 4.5: Cross-Seat Propagation Check (v3.26 C-26-31, gh#1857 — CAP-ISSUE-011 point-of-use wiring)

After writing the lesson, test BOTH triggers; if either fires, OFFER the lesson-first filing path (do not silently skip):

| Trigger | Test |
|---------|------|
| **Multi-seat evidence** | Does the lesson's evidence span more than one seat/fleet (cross-seat exchange, sibling incident, relayed datum)? |
| **Framework-artifact subject** | Does the lesson name a framework artifact (canonical script/spec/skill/SOP) as cause or fix? |

If YES to either → file via `/aget-file-issue` with `routing_mode: lesson_first` (CAP-ISSUE-011..014), citing this L-doc as substrate. The tracker's `lesson_first` label is the **cross-namespace join key** the supervisors' weekly lessons-miners match on — a lesson that stays only in this repo's evolution/ is invisible fleet-wide (L467 discovery-lottery at fleet scale).

**Worked example (the motivating triple, 2026-07-10)**: three seats independently derived "authorization doesn't travel across seats, sessions, or quotations" from three different incidents — main-SUP L681, downstream-SUP L249, FWK persistent memory — each invisible to the others except via principal relay. All three had multi-seat evidence; zero used lesson-first mode (3-for-3 non-invocation of a shipped capability = L962 habit-channel gap). One lesson-first filing by any seat would have made the other two derivations dedup-hits instead of re-derivations.

### Step 5: Update Index (Framework only)

Add entry to `.aget/evolution/index.json` and increment `next_id`.

### Step 6: Confirm

Report:
- File created at: {path}
- Classification: {Framework/Domain}
- ID: {L### or N/A}

## Constraints

- **C1**: MUST classify before writing. Do not proceed without Framework/Domain decision.
- **C2**: Framework lessons get L-numbers; Domain lessons do not.
- **C3**: Always update index.json for Framework lessons.
- **C4**: Apply the classification rubric in Step 2. Honor explicit principal classification; record obvious cases directly with rationale. Ask only about unresolved ambiguity or a split not already authorized. Classification does not authorize external filing or otherwise restricted writes.

## Classification Guidance

| Lesson Type | Classification | Example |
|-------------|---------------|---------|
| Process improvement for AGET framework | Framework | "Threshold calibration methodology" |
| Domain-specific knowledge | Domain | "domain-specific contract analysis rules" |
| CLI behavior finding | Framework | "Skills work in headless mode" |
| Project-specific pattern | Domain | "API rate limit handling" |
| Anti-pattern applicable to all AGETs | Framework | "Context-Anchoring Blindness" |

## Related Skills

- `/aget-check-evolution` - Check evolution directory health
- `/aget-record-observation` - Capture observations (lighter weight)

## Traceability

| Link | Reference |
|------|-----------|
| POC | POC-017 |
| Project | PROJECT_PLAN_AGET_UNIVERSAL_SKILLS.md |
| Source | Fleet Skill Deployment Report (supervisor) |

---

*aget-record-lesson v1.0.1*
*Category: Learning*
*POC-017 Phase 2*
