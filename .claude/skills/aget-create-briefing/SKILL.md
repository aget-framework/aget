---
name: aget-create-briefing
description: Generate standalone narrative documents from session artifacts, optimized for a target consumption medium (NotebookLM, slides, memo, share-draft). Use when the user says "create briefing", "create a briefing for NotebookLM", "make this listenable", "summarize session for [medium]", "prepare a listen", "brief me on [topic]", or "create a summary I can share".
---

# /aget-create-briefing

Generate standalone narrative documents from session artifacts, optimized for a target consumption medium. Bridges internal KB formats to external-consumption artifacts.

## Purpose

AGET sessions produce knowledge in internal formats (L-docs, session records, ontology entries, project plans) optimized for machine-readability and cross-reference integrity. These formats are unsuitable for external consumption — whether by the principal reviewing via audio (NotebookLM), preparing a presentation, or sharing a summary.

This skill bridges that gap: select source artifacts, adapt format to target medium, strip governance ceremony, and apply audience-appropriate voice register.

**Evidence**: Two independent demand signals (L758 cross-agent convergence). CCB NotebookLM briefing (~3000 words, 2026-04-02). Framework-AGET state management briefing (2026-03-30). L384 documents the KB-to-narrative-to-NotebookLM pipeline as established practice.

## Input

$ARGUMENTS

Parameters (all optional — defaults apply):

| Parameter | Values | Default | Purpose |
|-----------|--------|---------|---------|
| `--source` | Session record path, L-doc ID(s), topic string, or `latest-session` | `latest-session` | What to synthesize |
| `--medium` | `notebooklm`, `slides`, `memo`, `share-draft` | `notebooklm` | Target consumption format |
| `--audience` | `self`, `principal`, `external` | `principal` | Who consumes this |
| `--register` | `cognitive`, `formal`, `conversational` | Per agent config or `conversational` | Voice register |

Examples:
- `/aget-create-briefing` — Briefing from latest session, NotebookLM format, principal audience
- `/aget-create-briefing --source L758 --medium memo` — Memo from specific L-doc
- `/aget-create-briefing --source sessions/SESSION_2026-04-04_*.md --medium slides` — Slides from specific session
- `/aget-create-briefing --medium share-draft --audience external` — Public-safe draft from latest session

## Execution

### Step 1: Parse Parameters

Parse $ARGUMENTS for `--source`, `--medium`, `--audience`, `--register`. Apply defaults for any omitted parameters.

If `.aget/config.json` contains a `briefing:` block, use agent-specific defaults from it. Otherwise use the universal defaults from the parameter table above.

### Step 2: Source Resolution

Resolve the `--source` to actual KB artifacts:

| Source Type | Resolution |
|-------------|-----------|
| `latest-session` (default) | Find most recent `sessions/SESSION_*.md` by date |
| Session path | Read the specified session record directly |
| L-doc ID(s) | Read `.aget/evolution/L{id}_*.md` for each ID. Multiple IDs: comma-separated (e.g., `L758,L771`) |
| Topic string | Run `python3 scripts/study_topic.py --topic "{topic}" --quiet` and read the top 5 results |

**Verify**: Confirm at least 1 source artifact was resolved. If 0, report error and stop.

### Step 3: Content Extraction

Read all resolved source artifacts. Extract:

1. **Claims**: Key findings, decisions, patterns discovered
2. **Evidence**: Data points, exemplars, citations supporting claims
3. **Open questions**: Unresolved issues, decision points pending
4. **Context**: Why the work was done, what problem it addresses

**Strip**: Remove all governance ceremony — gate references (G0, G1...), spec IDs (CAP-xxx, R-xxx), EARS patterns (SHALL/WHEN/WHERE), conformance scores, V-test results, deliverable checklists, velocity metrics. Preserve the substance these structures contained, not the structures themselves.

### Step 4: Medium Adaptation

Apply format rules based on `--medium`:

**notebooklm** (audio-optimized):
- Plain prose only. No tables, no YAML, no code blocks, no bullet lists longer than 3 items (NotebookLM struggles with structured data)
- Conversational structure with implicit question-answer flow
- Use transitions that work when spoken: "The key finding here is..." / "What makes this interesting is..." / "The question this raises is..."
- Target: 1500-3000 words (10-20 min listen)
- Sections as narrative flow, not headers (minimize headers — NotebookLM reads them awkwardly)

**slides** (visual-optimized):
- One assertion per section, bullet-heavy, minimal prose
- Each section: title (the assertion) + 2-4 supporting bullets + optional speaker note
- Target: 15-25 sections
- End with "Key Takeaways" section (3-5 bullets)

**memo** (text-optimized):
- Executive summary (3-5 bullets) at top
- Detail sections with headers, concise paragraphs
- Formal register regardless of `--register` parameter (memos are always formal)
- Target: 800-1500 words

**share-draft** (public-safe):
- Apply VOICE.md anti-patterns if available, otherwise use neutral professional tone
- **MANDATORY**: Run classification safety check (Step 5) before writing output
- Include `[DRAFT — requires principal review before external use]` watermark at top
- Target: 500-2000 words depending on source density

### Step 5: Classification Safety Check (share-draft only)

**MANDATORY for audience=external or medium=share-draft.** Skip for self/principal audiences.

Scan the draft output for these prohibited patterns:

| Pattern | Example | Action |
|---------|---------|--------|
| Private agent names | `private-*-aget`, `private-*-AGET` | Remove or replace with generic description |
| Private repo references | `gmelli/*` | Remove or replace with "internal repository" |
| Fleet size disclosures | "32 agents", "40 agents in fleet" | Remove or replace with "multiple agents" |
| Internal project IDs | `FLEET-*-###`, `REL-042` | Remove |
| Session references | `SESSION_2026-*` | Remove or replace with "a recent session" |
| Internal L-doc references | `L758`, `L771` | Remove or replace with natural language description |

**If any pattern found**: Fix it in the draft, then re-scan. Report what was sanitized.

### Step 6: Write Output

Write the briefing to `docs/briefings/` with the naming convention:

| Medium | Filename |
|--------|----------|
| notebooklm | `BRIEFING_YYYY-MM-DD_{topic}.md` |
| slides | `BRIEFING_YYYY-MM-DD_{topic}_slides.md` |
| memo | `BRIEFING_YYYY-MM-DD_{topic}_memo.md` |
| share-draft | `BRIEFING_YYYY-MM-DD_{topic}_draft.md` |

Where `{topic}` is a snake_case summary of the source content (max 50 chars).

### Step 7: Report

Display completion summary:

```
=== Briefing Created ===
File: docs/briefings/BRIEFING_YYYY-MM-DD_{topic}.md
Medium: {medium}
Audience: {audience}
Register: {register}
Sources: {count} artifacts ({list})
Words: {word_count} (~{estimated_minutes} min {read/listen})
Classification: {PASS | N/A (internal audience)}
```

## Constraints

- **C1**: MUST NOT modify any source KB artifacts. This skill is read-only on the KB. Output goes only to `docs/briefings/`.
- **C2**: MUST NOT produce output for audience=external without completing Step 5 (Classification Safety Check). Zero tolerance for private pattern leaks.
- **C3**: MUST NOT include governance ceremony in principal/external output — no CAP-xxx, R-xxx, EARS patterns, V-test results, gate references, conformance scores.
- **C4**: MUST NOT fabricate claims. Every substantive assertion in the briefing must trace to a source artifact. If evidence is tentative, say so. If uncertain, omit rather than guess.
- **C5**: MUST validate that at least 1 source artifact resolves before proceeding to Step 3. Report error on 0 sources.
- **C6**: MUST use `docs/briefings/` as output directory. Create the directory if it does not exist.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No source artifacts found | `--source` resolved to 0 files | Report: "No artifacts found for source '{source}'. Try a different source or check the path." |
| Session file not found | `latest-session` but no `sessions/SESSION_*.md` exists | Report: "No session files found in sessions/. Provide an explicit --source." |
| L-doc ID not found | Specified L-doc doesn't exist in `.aget/evolution/` | Report: "L{id} not found. Check `.aget/evolution/` for available L-docs." |
| Classification check failed | Private patterns in share-draft after 2 sanitization passes | Report: "Classification safety check failed after 2 passes. Manual review required." Refuse to write output. |
| Unknown medium | `--medium` value not in {notebooklm, slides, memo, share-draft} | Report: "Unknown medium '{value}'. Use: notebooklm, slides, memo, share-draft." |

## Related Skills

- `/aget-study-topic` — Research a topic across KB (often the precursor to creating a briefing)
- `/aget-record-observation` — Capture findings during sessions (produces the artifacts briefings synthesize)
- `/aget-record-lesson` — Record L-docs (a common briefing source type)
- `/aget-wake-up` — Session initialization (briefings often cover session output)

## Traceability

| Link | Reference |
|------|-----------|
| Proposal | SP-005 (`planning/skill-proposals/PROPOSAL_aget-create-briefing.md`) |
| Requirements | REQ-BRF v0.1.0 (`docs/drafts/REQ-BRF_briefing_creation.md`) |
| Tracking | gmelli/aget-aget#810 |
| L-docs | L384 (Spec Narrative Pattern), L733 (Voice as Composition), L745 (Multi-Modal Effectiveness), L758 (Cross-Agent Convergence), L771 (Proposal Discovery Gap) |
| Cross-agent | CCB P-005 (demand signal + parameter design + working exemplar) |

---

*aget-create-briefing v1.0.0*
*Category: Creation*
*Archetype: Universal (all agents, medium/audience parameters adapt per agent identity)*
*Template: templates/skill/SKILL.template.md*
