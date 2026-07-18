---
name: aget-process-observation
description: Classify captured observations and route actionable items to downstream skills. Implements L665 File-and-Route for the capture pipeline.
---

# /aget-process-observation

Classify captured observations and route actionable items to downstream skills. The missing middle step between capture and promotion in the capture pipeline.

## Purpose

Observations are captured (`/aget-record-observation`) and can be promoted to L-docs (`/aget-record-lesson`) or issues (`/aget-file-issue`), but there is no governed step that classifies captured input, routes actionable items to downstream skills, and updates observation status. This skill fills that gap, implementing L665 (File-and-Route) for the capture pipeline: the user captures once, the system processes and routes optimally.

**Evidence**: L665 (File-and-Route), L671 (Classification Without Consequence), L669 (Principal Sense Amplification), L692 (Data Sovereignty). CAP-001 Gates 4-5 alignment. Principal observation (2026-03-18): "we are looking for the next investment. /aget-process-observation for example."

## Input

$ARGUMENTS

Parameters:

| Parameter | Values | Default | Purpose |
|-----------|--------|---------|---------|
| `--source` | Observation file path or `unprocessed` | `unprocessed` | What to process |

Examples:
- `/aget-process-observation` — Process all unprocessed observations
- `/aget-process-observation --source .aget/research/OBSERVATION_2026-04-10_patterns.md` — Process specific observation
- `process this observation` — Process most recently captured observation
- `route this finding` — Natural language trigger

## Execution

### Step 1: Resolve Source

| Source | Resolution |
|--------|-----------|
| `unprocessed` (default) | Scan `.aget/research/OBSERVATION_*.md` for files with `status: Captured` |
| Specific path | Read the specified observation file directly |
| Most recent | Find latest `.aget/research/OBSERVATION_*.md` by date |

If 0 unprocessed observations found, report "No unprocessed observations." and stop.

### Step 2: Read and Classify

For each observation, read its content and classify the input types present:

| Input Type | Indicators | Routing Implication |
|------------|-----------|---------------------|
| Screenshot evidence | Image references, visual description | Visual record — archive |
| Web research finding | URLs, citations, external sources | Source attribution — ontology or L-doc |
| Verbal observation | Pattern description, gap identification | Pattern/gap — L-doc or issue |
| Environmental context | State snapshot, configuration data | State record — session note |
| Metric or measurement | Numbers, counts, comparisons | Data point — rubric or spec enhancement |

An observation may contain multiple input types. Classify each actionable item separately.

### Step 3: Route Actionable Items

For each actionable item identified, determine the downstream route:

| Action Type | Route To | Downstream Skill |
|-------------|----------|-----------------|
| Lesson learned | L-doc creation | `/aget-record-lesson` |
| Issue or gap | Issue filing | `/aget-file-issue` |
| Vocabulary candidate | Ontology expansion | `/aget-expand-ontology` |
| Design direction | DESIGN_DIRECTION update | Manual (report as recommended action) |
| Spec enhancement | Spec update | `/aget-enhance-spec` |
| Pipeline input | PROJECT_PLAN update | Manual (report as recommended action) |

### Step 4: Execute Routes

For each routed item:
1. If the downstream skill exists and the route is unambiguous, invoke it
2. If the route requires manual action, list it as a recommended next step
3. If multiple routes apply, present options and let the user choose

### Step 5: Update Status

Update the observation file's `status` from `Captured` to `Processed`. Add a `processed_routes` field listing where items were sent.

### Step 6: Report

```
=== Observation Processed ===
Source: [file path]
Input types: [list of classified types]
Items routed: [count]
  - [item summary] -> [downstream skill/action]
  - [item summary] -> [downstream skill/action]
Manual actions recommended: [count]
  - [action description]
Status: Captured -> Processed
```

## Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| REQ-PROC-001 | Process-observation SHALL classify input types before routing | L665, SP-002 |
| REQ-PROC-002 | Process-observation SHALL route each actionable item to the appropriate downstream skill | L665 (File-and-Route) |
| REQ-PROC-003 | Process-observation SHALL update observation status from Captured to Processed | SP-002 |
| REQ-PROC-004 | Process-observation SHALL handle multi-type observations (single observation, multiple routes) | SP-002 |
| REQ-PROC-005 | Process-observation SHALL report manual actions separately from automated routes | SP-002 |
| REQ-PROC-006 | Process-observation SHALL NOT fabricate actionable items — only route what the observation contains | L671 |
| REQ-PROC-007 | Input characterization SHALL precede routing — classify what kind of information, not just topic | L665, SP-002 |

## Constraints

- **C1**: Classification MUST precede routing — do NOT route without first classifying input type (L665: input characterization is prerequisite)
- **C2**: MUST NOT fabricate actionable items — only route what the observation actually contains
- **C3**: MUST update observation status after processing — an untracked status change is a L671 instance (classification without consequence)
- **C4**: Manual routes MUST be reported as recommendations, not silently skipped

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-002 (`planning/skill-proposals/PROPOSAL_aget-process-observation.md`) |
| Pipeline position | Capture -> **Process** -> Promote |
| CAP-001 alignment | Gates 4-5 (wire classification to consequences, File-and-Route prototype) |
| L-docs | L665 (File-and-Route), L671 (Classification Without Consequence), L669 (Sense Amplification), L692 (Data Sovereignty) |
| Upstream skills | `/aget-record-observation` (capture) |
| Downstream skills | `/aget-record-lesson`, `/aget-file-issue`, `/aget-expand-ontology`, `/aget-enhance-spec` |

---

*aget-process-observation v0.1.0*
*Category: Knowledge Management*
*Pipeline: Capture -> Process -> Promote (this skill = Process)*
