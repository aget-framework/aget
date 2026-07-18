---
name: aget-expand-ontology
description: Expand SKOS ontology vocabularies with web-researched, evidence-backed concepts. Identifies thin topics, proposes expansion areas, researches best-practice concepts, creates bridging interlinkage, writes formal SKOS entries, and enriches matched existing entries.
version: 2.1.0
status: active
spec: SKILL-019
category: Creation
ontology:
  vocabulary_glob: "ontology/ONTOLOGY_*.yaml"
  validation_command: "test -f tools/validate_ontology.py && python3 tools/validate_ontology.py --format=report --log-history || echo 'Validation skipped (tools/validate_ontology.py not available)'"
  quality_history: "ontology/QUALITY_HISTORY.yaml"
  vocabulary_index: "ontology/VOCABULARY-INDEX.md"
  project_prefix: "FWRK"
  staging_file: "ontology/EXPANSION_CANDIDATES.yaml"
---

# /aget-expand-ontology

Expand this agent's SKOS vocabularies with new web-researched, evidence-backed concepts targeting thin topics. Merged from professional-core v1.5.0 + framework-AGET v1.0.0 + supervisor additions (SKILL-019 spec).

## Purpose

Automate the research-informed ontology expansion workflow:
1. **Diagnose**: Identify thin topics and KB gaps
2. **Propose**: Rank expansion areas by gap size and tier importance
3. **Research**: Web-search for best-practice evidenced concepts
4. **Design**: Write formal SKOS entries with interlinkage
5. **Enrich**: Enhance matched existing concepts with new evidence
6. **Verify**: Validate no orphans, topic density improved

## Input

Optional parameters after skill name:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--areas N` | 3 | Number of expansion areas to propose |
| `--concepts-per-area N` | 7 | Domain concepts per area |
| `--bridging-per-area N` | 3 | Bridging/interlinkage concepts per area |
| `--vocabulary V` | Auto (smallest) | Target specific vocabulary file |
| `--from-kb <path>` | None | Extract concepts from KB document instead of web search |
| `--dry-run` | false | Output project plan without writing to vocabulary |
| `--skip-web-search` | false | Use KB-only gap analysis (no web research) |
| `--skip-enhance` | false | Skip enhancement of matched concepts during deduplication |
| `--plan` | false | Output structured expansion plan without executing |
| `--summary` | false | Output only summary metrics |
| `--provenance "desc"` | None | Strategic context that triggered this expansion (event, motivation, audience) |

Examples:
- `/aget-expand-ontology` — Auto-detect thinnest vocabulary, 3 areas, 7+3 concepts each
- `/aget-expand-ontology --vocabulary ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml` — Target specific vocabulary
- `/aget-expand-ontology --from-kb knowledge/REPORT.md` — Document-driven expansion
- `/aget-expand-ontology --dry-run` — Propose expansion without writing
- `/aget-expand-ontology --concepts-per-area 5 --bridging-per-area 2` — Smaller expansion
- `/aget-expand-ontology --provenance "Marcus 1:1 surfaced missing meta-concepts for team topology"` — Expansion with strategic context

## Configuration

The `ontology` config block in frontmatter defines all paths. **Agents MUST customize this block** for their vocabulary layout:

```yaml
ontology:
  vocabulary_glob: "ontology/ONTOLOGY_*.yaml"           # Glob for vocabulary files
  validation_command: "test -f tools/validate_ontology.py && python3 tools/validate_ontology.py --format=report --log-history || echo 'Validation skipped (tools/validate_ontology.py not available)'"
  quality_history: "ontology/QUALITY_HISTORY.yaml"       # Expansion audit trail
  vocabulary_index: "ontology/VOCABULARY-INDEX.md"       # Optional index file
  project_prefix: "FWRK"                                # Expansion project ID prefix
  staging_file: "ontology/EXPANSION_CANDIDATES.yaml"     # Deferred concepts staging
```

**Example configurations**:
- Standard agent: `vocabulary_glob: "ontology/ONTOLOGY_*.yaml"`
- Professional-core: `vocabulary_glob: "vocabulary/INTELLIGENCE_VOCABULARY_v*.yaml"`
- Multi-vocabulary: `vocabulary_glob: "knowledge/frameworks/*-vocabulary-skos.yaml"`

## Execution

### Step 0.5: Prerequisite Validation

Before loading state, validate required files exist:

1. Check vocabulary files match `vocabulary_glob` from config block
2. Check `quality_history` file exists (or create empty)
3. Check validation command is available

If prerequisites fail, STOP and advise which files are missing.

### Step 1: Load Current Ontology State

Read required files to understand current state:

1. List vocabularies matching config `vocabulary_glob`
2. If `--vocabulary` specified, filter to that file only
3. Read target vocabulary (smallest by concept count if multiple)
4. Parse concept scheme, clusters/topics, and concept counts
5. Read quality history from config `quality_history` path

### Step 1b: Capture Expansion Provenance

If `--provenance` was provided, store it for use in Steps 8 and 10.

If `--provenance` was NOT provided, prompt:

> **What triggered this expansion?**
> Briefly describe the event, motivation, or audience (e.g., "Marcus 1:1 surfaced missing meta-concepts" or "pre-release vocabulary gap audit").
> Press Enter to skip.

If user provides a response, store as provenance. If skipped, provenance is `null` (no provenance recorded — expansion proceeds without strategic context).

Provenance structure (used in Steps 8 and 10):
```yaml
provenance:
  event: "{what happened}"
  motivation: "{why it matters}"
  audience: "{who benefits}"
```

If the user provides a single string, parse it as `event` and leave `motivation` and `audience` as null.

### Step 2: Gap Analysis

From the loaded vocabulary, analyze concept distribution:

```
For each cluster/topic:
  - current_concepts: count concepts in cluster
  - tier: from topic/cluster metadata (if available)
  - priority_score = (5 - tier) * (target_density - current_concepts)
    where target_density = 10 for top-level, 6 for subtopics, 4 for leaf
```

Then scan KB artifacts for ungrounded concepts:
```
Search knowledge/, docs/, .aget/evolution/ for terms not yet in vocabulary
```

### Step 3: Propose Expansion Areas

Rank candidate areas by `priority_score` and select top N (default 3).

For each proposed area, report:
- **Area name**: Descriptive label
- **Target clusters/topics**: Which thin areas this strengthens (with before-after projection)
- **Target categories**: Which existing categories receive new concepts
- **KB evidence**: Which KB artifacts contain related ungrounded concepts
- **Rationale**: Why this area is a natural expansion

Present areas to user. If `--dry-run` or `--plan`, present and stop here.

### Step 4: Web Research (Parallelized)

For each expansion area, launch a parallel web search agent (Task tool, subagent_type: general-purpose):

**Search prompt template**:
```
Search the web for well-established, best-practice concepts in {AREA_NAME}
suitable for a {VOCABULARY_DOMAIN} vocabulary. Focus on concepts with
strong evidence grounding (academic papers, industry reports, standards bodies).

Search for these specific areas:
{SPECIFIC_SEARCH_TOPICS}

Vocabulary context for this expansion:
- Target clusters: {TARGET_CLUSTERS_WITH_COUNTS}
- Key existing concepts to connect to: {KEY_EXISTING_CONCEPTS}
- Hierarchy opportunities: {HIERARCHY_NOTES}

For each concept found, provide:
- Canonical term name
- Brief definition (1-2 sentences)
- Key source/evidence (author, publication, year)
- Why it matters for the vocabulary domain
- Which existing concept(s) it would connect to

Return at least {CONCEPTS_PER_AREA + 4} well-evidenced concepts with sources.
```

If `--from-kb <path>` is provided, extract concepts from the document instead.
If `--skip-web-search` is passed, use KB-only analysis.

**Evidence quality tiers** (target: 60%+ at Tier 1-2):
- Tier 1 (Gold): Peer-reviewed paper, W3C/NIST/ISO standard
- Tier 2 (Silver): Major industry research (McKinsey, Gartner, ACM, IEEE)
- Tier 3 (Bronze): Industry report, conference talk, well-sourced blog

### Step 5: Concept Selection and Curation

From web research results, select top N concepts per area:

**Selection criteria**:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Evidence strength | 40% | Tier 1-2 preferred |
| Gap-filling value | 25% | Strengthens thinnest clusters = higher priority |
| Interlinkage potential | 20% | Connects to more existing concepts = higher priority |
| Novelty | 15% | NOT redundant with existing vocabulary |

**Deduplication**: Check each candidate against existing vocabulary prefLabels and altLabels.

Split selected concepts into:
- **Domain concepts** (N per area): Core concepts for the expansion area
- **Bridging concepts** (M per area): Concepts connecting new area to existing ontology

### Step 5a: Counter-Perspective Gate

After concept selection and before SKOS writing, verify balanced perspective.

**Gate check**:
1. Classify each selected concept as **advocacy** (capabilities, benefits, best practices) or **counter-perspective** (limitations, failures, risks, critiques)
2. Calculate ratio: `counter_count / total_selected`
3. Compare against threshold: **20-30%**

**Gate outcomes**:

| Ratio | Action |
|-------|--------|
| 20-30% | PASS — proceed to Step 5b/Step 6 |
| <20% | HOLD — launch targeted counter-perspective research, then re-check |
| >30% | WARN — expansion may be overly skeptical; present to user for review |

### Step 5b: Enhance Matched Concepts

During deduplication, concepts matching existing entries are candidates for **enhancement** rather than silent discard. Skip if `--skip-enhance` is passed.

For each matched concept:

1. **Assess new evidence**: Compare source evidence with existing `example` and `sources` fields
2. **Determine enhancement value**:

| Criterion | Enhance? | Example |
|-----------|----------|---------|
| New evidence is from a different source | Yes | Existing: paper A -> New: paper B |
| New evidence is more recent | Yes | Existing: 2025 -> New: 2026 |
| New evidence provides quantitative data | Yes | Existing: qualitative -> New: metrics |
| New evidence is redundant | No | Same source, same data point |
| New evidence is lower quality | No | Existing: Tier 1 -> New: Tier 3 |

3. **Apply enhancements** (append-only):
   - **`example`**: Append new evidence after existing text, with date attribution
   - **`sources`**: Append new source reference to list
   - **`definition`**: Update ONLY if new evidence materially changes the concept's meaning

4. **Track enhancements**: Record each for the expansion report

### Step 5c: Persist Unused Concepts

Valid concepts not selected for this expansion are written to the `staging_file` from config block for future consideration.

### Step 6: Assign Concept IDs

For each new concept:
1. Determine target category/cluster based on semantic fit
2. Find next available ID in that category
3. Assign ID following vocabulary's naming convention
4. Auto-increment project ID from quality_history

### Step 7: Write Formal SKOS Definitions

For each concept, write complete SKOS entry:

```yaml
{ID}:
  prefLabel: "{canonical name}"
  status: active
  altLabel:
    - "{alternative name 1}"
  definition: "{1-2 sentence formal definition}"
  broader: {parent concept or null}
  narrower: [{child concepts}]
  related: [{related concepts - MUST include >=1 existing concept}]
  example: "{concrete example with source attribution and year}"
  sources:
    - "{Primary source with year}"
```

**SKOS relationship rules**:
- `related`: MUST contain at least 1 existing concept (no orphans)
- `broader`/`narrower`: Use when clear hierarchical relationship exists
- `sources`: MUST contain real, verifiable references (NEVER fabricate)

**PrefLabel quality rules** (PL-01 through PL-05):

| Rule | Check | If FAIL |
|------|-------|---------|
| PL-01 | Contains domain-anchoring term relevant to vocabulary's domain | Add domain qualifier |
| PL-02 | Distinguishable from unrelated domains without reading definition | Narrow the label |
| PL-03 | Primary descriptor is literal, not metaphorical | Move metaphor to altLabel |
| PL-04 | <=8 words | Shorten or split |
| PL-05 | No company/proper noun as primary descriptor | Restructure with parenthetical attribution |

**Gate**: >10% of new concepts failing PL-01 triggers review before proceeding to Step 8.

### Step 7a: Reciprocal Link Verification

After writing SKOS entries and before writing to vocabulary, verify reciprocal link integrity.

**For each new concept**, check every link it declares:

| New Concept Declares | Existing Concept Must Have | Action if Missing |
|---------------------|---------------------------|-------------------|
| `related: [X1, X2]` | X1.related includes new ID | Add new concept ID to X's `related` |
| `broader: P1` | P1.narrower includes new ID | Add new concept ID to P1's `narrower` |
| `narrower: [C1]` | C1.broader = new ID | Set C1's `broader` to new concept ID |

Include reciprocal link updates in the Step 8 vocabulary write.

### Step 8: Write to Vocabulary

If NOT `--dry-run`:

1. **Add SKOS entries** to appropriate clusters in vocabulary YAML
2. **Apply enhancements** to matched existing concepts (unless `--skip-enhance`)
3. **Apply reciprocal link updates** to existing concepts
4. **Update metadata**: concept count, extension projects, version history
5. **Write provenance** (if captured in Step 1b): Add `provenance:` sub-field to the new `version_history` entry:
   ```yaml
   - version: "X.Y.Z"
     date: "YYYY-MM-DD"
     provenance:
       event: "{from Step 1b}"
       motivation: "{from Step 1b}"
       audience: "{from Step 1b}"
     changes:
       - "..."
   ```
6. **Write provenance to quality_history** (if captured): Add `provenance:` field to the snapshot entry in the config `quality_history` file

### Step 8b: Update Index

If `vocabulary_index` path exists in config, update it with new concepts and categories.

### Step 9: Validate

Run validation command from config block and verify:
- Quality score maintained or improved
- 0 orphan concepts
- All new concepts have sources
- Cluster/topic density improved as projected
- Concept count matches metadata

### Step 10: Report Results

```markdown
## Ontology Expansion Complete

**Vocabulary**: {name} v{before} -> v{after}
**Concepts**: {before} -> {after} (+{delta})
**Project**: {prefix}-{YYYY}-{NNN}
**Provenance**: {event} (or "none captured")

### Areas Expanded

| Area | Concepts | Clusters | Impact |
|------|----------|----------|--------|
| {name} | {N} domain + {M} bridging | {clusters} | {before}->{after} |

### Enhanced Existing Concepts

| ID | prefLabel | Fields Updated | New Evidence Summary |
|----|-----------|----------------|---------------------|
| {id} | {label} | example, sources | {brief description} |

### Reciprocal Link Maintenance

| Existing Concept | Link Type Added | New Concept |
|-----------------|----------------|-------------|
| {id} | related | {new_id} |

### Quality
- Orphan concepts: 0
- Cross-cluster connections: {count}
- Evidence tier distribution: {T1}% / {T2}% / {T3}%
- Counter-perspective ratio: {ratio}%
```

### Step 10b: Update Registry

If NOT `--dry-run` and project registry exists:

1. Append project entry to registry
2. Update `metadata.next_available_id`
3. Update `metadata.total_allocated`

If registry does not exist, WARN and skip.

### Step 10c: Expansion Retrospective

After reporting results and updating registry, prompt:

> **Expansion Retrospective** (optional)
> - **Went well**: What worked in this expansion cycle?
> - **Could improve**: What would you change next time?
> - **Concepts**: Any concepts that surprised you or seem off?

If user provides a response, include it in the session file under `## Retrospective`.
If user declines (empty response or "skip"), proceed without recording.

This step is **non-blocking** — the expansion is already complete and committed. The retrospective captures process learning for future cycles.

## Constraints

- **C1**: NEVER fabricate sources — all sources MUST be real, verifiable references
- **C2**: NEVER create orphan concepts — all concepts MUST have >=1 related link to existing ontology
- **C3**: NEVER remove or modify existing concepts — expansion is additive only
- **C4**: NEVER skip web research unless `--skip-web-search` or `--from-kb` explicitly passed
- **C5**: NEVER write to vocabulary without running validation afterward
- **C6**: MUST log expansion to quality_history
- **C7**: MUST achieve 60%+ concepts at evidence Tier 1-2
- **C8**: MUST check for duplicates against existing prefLabels and altLabels
- **C9**: MUST present expansion areas to user before executing web research
- **C10**: MUST read current ontology state before proposing expansions
- **C11**: Enhancement is additive only — NEVER remove existing field content
- **C12**: Enhanced concepts MUST retain all existing field content
- **C13**: MUST verify prefLabels against PL-01 through PL-05 before writing; >10% failure triggers review
- **C14**: MUST update project registry after execution-mode expansion (if registry exists)
- **C15**: MUST verify 20-30% counter-perspective ratio before SKOS writing
- **C16**: MUST NOT contain hardcoded vocabulary, validation tool, or index paths — all from config block
- **C17**: MUST verify and maintain reciprocal SKOS links for all new concepts
- **C18**: MUST prompt for expansion provenance when `--provenance` is not provided; provenance is optional but prompted (not silently skipped)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No vocabulary files | No files match vocabulary_glob | Advise user to create vocabulary first |
| Missing prerequisites | Required files not found | STOP with advisory listing missing files |
| Web search returns <N concepts | Insufficient evidence | Reduce concepts-per-area or widen search |
| YAML parse error after write | Malformed YAML | Revert changes, report error |
| Quality score drops | New concepts caused regression | Review and fix topic/related assignments |
| Duplicate concept detected | Already exists under different ID | Skip duplicate, report to user |
| Counter-perspective ratio <20% | Expansion skews advocacy | Launch targeted counter-perspective research |

## Related Skills

- `/aget-record-observation` — Record raw observations before expansion
- `/aget-record-lesson` — Record expansion learnings
- `/aget-study-topic` — Research topic context before expansion
- `/aget-analyze-ontology` — Analyze ontology health (complementary)

## Traceability

| Link | Reference |
|------|-----------|
| Spec | `.aget/specs/skills/SKILL-019_aget-expand-ontology.yaml` |
| Promotion Plan | `planning/PROJECT_PLAN_expand_ontology_skill_promotion_v1.0.md` |
| Lineage (pro-core) | professional-core-aget v1.5.0 (Steps 5a, 5b, 7a, PrefLabel spec, registry) |
| Lineage (framework) | framework-AGET v1.0.0 (generalized structure, multi-vocabulary) |
| Lineage (supervisor) | Config block, --from-kb, staging, PROCO auto-increment, lifecycle frontmatter |
| L-docs | L545 (convergent evolution), L552 (spec-first merge), L580 (graduated autonomy), L584 (skill deficit), L823 (meta-meta gap taxonomy) |
| Enhancement | #388 (provenance capture), #561 (embedded retro) |

---

*aget-expand-ontology v2.1.0*
*Category: Creation*
*Merged: professional-core v1.5.0 + framework-AGET v1.0.0 + supervisor additions*
*Spec: SKILL-019 (31 capabilities, 16 constraints)*
*v2.1.0: +--provenance (EO-030, C18, #388) +Step 10c retro (EO-031, #561)*
