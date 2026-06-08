# SOP: Initiative Management

**Version**: 1.3.0
**Created**: 2026-04-04
**Updated**: 2026-05-14 (v1.3.0 — Label Management section added)
**Owner**: private-aget-framework-AGET
**Category**: Governance
**Related**: L760 (Initiative as Scope Modifier), C227 (InitiativeScope), SP-004 (aget-check-initiative), #916 (Initiative-scoped channel registry), #910 (Contributor value profiles), gh#1193 (INIT-PRINCIPLED-EXECUTION file gap), L524 (Pattern Consolidation)

---

## Purpose

Standard operating procedure for creating, tracking, and closing initiatives — multi-project, multi-version work containers that group related PROJECT_PLANs, issues, L-docs, and sessions under a shared scope modifier.

**Problem Solved**: Without a formal initiative process:
- Multi-version work has no container (context lost between versions)
- Related PROJECT_PLANs are discoverable only by filename search
- Principal must manually bridge cross-project context at gate reviews
- No mechanism to track progress across related but independent projects

---

## Scope

### When to Use This SOP

| Trigger | Example |
|---------|---------|
| **Work spans 2+ versions** | "Core Artifact Maturation" across v3.13–v3.15 |
| **Work spans 3+ PROJECT_PLANs** | Multiple related projects that share a theme |
| **Principal requests tracking** | "Track this as an initiative" |

### When NOT to Use This SOP

| Trigger | Use Instead |
|---------|-------------|
| Single PROJECT_PLAN, single version | `/aget-create-project` |
| Research with no implementation plan | `/aget-study-topic` |
| One-off task | Task tracking within session |

---

## Key Concept

**Initiative is a scope modifier, not a first-class entity** (L760). It groups existing entities (PROJECT_PLANs, L-docs, issues, sessions) via an `initiative_id` tag. It does not have its own lifecycle independent of its children — its state derives from the entities it groups.

---

## Initiative ID Convention

### Format

```
INIT-{SHORT-NAME}
```

**Rules**:
- Prefix: `INIT-` (always uppercase)
- Short name: 2-4 word kebab-case identifier
- Unique within the agent's planning/ directory

**Examples**:
- `INIT-CORE-ARTIFACT-MATURATION`
- `INIT-LDOC-V2`
- `INIT-FLEET-UPGRADE-AUTOMATION`

### Where initiative_id Appears

| Artifact Type | Field | Example |
|---------------|-------|---------|
| Initiative manifest | `initiative_id` header | `INIT-CORE-ARTIFACT-MATURATION` |
| PROJECT_PLAN | Optional metadata field | `**Initiative**: INIT-CORE-ARTIFACT-MATURATION` |
| GitHub issue | Label | `initiative:core-artifact-maturation` |
| Session file | Frontmatter | `initiative: INIT-CORE-ARTIFACT-MATURATION` |
| L-doc | Related section | `Initiative: INIT-CORE-ARTIFACT-MATURATION` |

---

## Label Management

GitHub issue labels named `initiative:{short-name}` are the rollup substrate for issue-to-initiative traceability. The label namespace is governed here.

### Naming

| Rule | Value |
|------|-------|
| Namespace | `initiative:` (lowercase, colon-separated) |
| Short-name | Kebab-case derived from `INIT-{SHORT-NAME}` — strip prefix, lowercase, hyphens preserved |
| Example | `INIT-CORE-ARTIFACT-MATURATION` → `initiative:core-artifact-maturation` |

### Color

| Property | Value | Rationale |
|----------|-------|-----------|
| Color | `#5319e7` (governance-purple) | Matches `type:governance` hue family; distinct from `priority:*` / `severity:*` / `type:*` semantic ranges |
| Description | `INIT-{UPPER-NAME}` | One-line; the exact INIT-ID for unambiguous traceability |

**Anti-pattern**: `#0E8A16` (green) — collides with `priority:low` and `priority:p3`. Pre-2026-05-14 labels using this color SHALL be recolored at next label maintenance pass.

### Registry

The authoritative list of created `initiative:*` labels lives in `planning/initiatives/INDEX.md` Active Initiatives table — each Active initiative SHOULD have a matching label. Labels for PROPOSED initiatives are deferred until ACTIVE transition (avoids namespace churn on Decide reversal).

| Trigger | Label Action |
|---------|-------------|
| Initiative transitions PROPOSED → ACTIVE | Create label per Naming + Color above |
| Initiative reaches COMPLETE/CLOSED | Keep label (historical traceability); do not delete |
| Initiative renamed | Create new label; rename existing issues; deprecate old label per `governance/POLICY_deprecation.md` |

### Retroactive Coverage

When a new `initiative:*` label is created for an existing initiative, perform a retroactive labeling sweep:

| Phase | Action | Scope |
|-------|--------|-------|
| **Phase B1** (default) | `gh search issues "INIT-{NAME}"` in title/body → label matches | Grep-discoverable subset (~50-100 typical) |
| **Phase B2** (escalation) | Full open-inbox sweep with manual classification | Only when B1 coverage <25% of expected issues |
| **Phase B3** (forward-only) | No retroactive; rely on filing-time labeling | Only with principal Decide; document rationale |

Default policy: **Phase B1**. Phase B2/B3 require explicit principal Decide.

### Filing-Time Labeling

`/aget-file-issue` skill SHOULD detect `INIT-*` references in issue title/body and suggest the matching label at filing time. Wiring is OUT OF SCOPE for this SOP — tracked separately. Until skill wiring lands, manual labeling per Step 6 below.

---

## Procedure

### Phase 1: Create Initiative

**Step 1**: Verify initiative is warranted (see "When to Use" above)

**Step 2**: Assign initiative_id per convention above

**Step 2.5**: Identify and register initiative channels — for each external channel (Slack, Linear project, GitHub milestone) associated with this initiative, record in the manifest `## Channels` section with: channel name, ID, purpose classification (sync, agents, discussion, alerts), and scan priority (primary, secondary, monitor). See #916.

**Step 3**: Create initiative manifest at `planning/initiatives/INIT-{SHORT-NAME}.md` using the template below

**Step 3.5**: Identify contributor roles and expected value dimensions — for each role archetype contributing to this initiative (e.g., Principal, Engineer, Data Scientist, Product, AGET), record in the manifest `## Contributors` section: role, primary value dimensions (artifact production, critical path acceleration, decision quality, knowledge generation, correctness assurance, stakeholder alignment, process health), and availability. This is descriptive (what value does this role type supply?) not evaluative (how well is this person performing?). See #910, L572.

**Step 4**: Tag any existing PROJECT_PLANs, issues, or L-docs with the initiative_id

### Phase 2: Track Initiative

**Step 5**: When creating new PROJECT_PLANs within the initiative, add `**Initiative**: INIT-{SHORT-NAME}` to the header

**Step 6**: When filing issues related to the initiative, add label `initiative:{short-name}` per "Label Management" section above. If the label does not yet exist, create it first per the Naming + Color spec.

**Step 7**: At version boundaries (scope lock), review the initiative manifest:
- Update stream status
- Note which child projects completed, deferred, or spawned
- Update target version if scope shifted

### Phase 3: Close Initiative

**Step 8**: When all streams are complete (or explicitly deferred/cancelled):
- Update initiative manifest status to COMPLETE or CLOSED
- Record retrospective in the manifest
- Note any follow-on initiatives spawned

---

## Initiative Manifest Template

```markdown
# Initiative: {Title}

**Initiative ID**: INIT-{SHORT-NAME}
**Status**: ACTIVE | COMPLETE | CLOSED | PAUSED
**Created**: YYYY-MM-DD
**Author**: {agent name}
**Target Versions**: v{X.Y} – v{X.Y}
**Theme**: {1-sentence description}

---

## Purpose

{Why this initiative exists. What problem or opportunity it addresses.}

## Channels

| Channel | ID | Purpose | Priority |
|---------|----|---------|----------|
| {#channel-name or system:project} | {ID} | {sync, agents, discussion, alerts} | {primary, secondary, monitor} |

## Contributors

| Role | Primary Value Dimensions | Availability |
|------|-------------------------|--------------|
| {Principal, Engineer, DS, Product, AGET, etc.} | {e.g., Decision Quality, Stakeholder Alignment} | {e.g., Full, Part-time, On-demand} |

*Descriptive, not evaluative. Maps what value each role type supplies to this initiative. See #910.*

## Streams

| # | Stream | Description | Status | Child Projects | Target Version |
|---|--------|-------------|--------|----------------|----------------|
| 1 | {name} | {what it delivers} | NOT STARTED | {PP-### or PROJECT_PLAN ref} | v{X.Y} |
| 2 | {name} | {what it delivers} | NOT STARTED | — | v{X.Y} |

## Success Metrics

| Metric | Baseline | Target | Actual |
|--------|:--------:|:------:|:------:|
| {metric 1} | {current} | {goal} | — |

## Evidence Base

| Source | Key Finding | Date |
|--------|-------------|------|
| {L-doc, session, research} | {finding} | {date} |

## Timeline

| Version | Streams | Milestone |
|---------|---------|-----------|
| v{X.Y} | 1, 2 | Foundation |
| v{X.Y} | 3, 4 | Specification |

## Retrospective

*Complete when initiative reaches COMPLETE or CLOSED status.*

### What Worked
1. {pattern to repeat}

### What Didn't Work
1. {pattern to avoid}

### Spawned Initiatives
- {INIT-### if any follow-on work}

---

## Traceability

| Link | Reference |
|------|-----------|
| Trigger | {what prompted this initiative} |
| Related L-docs | {L-doc references} |
| Related issues | {issue references} |
| Related sessions | {session references} |
```

---

## Validation

| Check | Method |
|-------|--------|
| Initiative manifest exists | `ls planning/initiatives/INIT-*.md` |
| initiative_id follows convention | Format: `INIT-{UPPER-KEBAB-CASE}` |
| At least 1 child project tagged | `grep -l "Initiative: INIT-" planning/PROJECT_PLAN_*.md` |
| Status is current | Manual review at version boundaries |

---

## Traceability

| Link | Reference |
|------|-----------|
| Conceptual model | L760 (Initiative as Scope Modifier) |
| Ontology | C227 (InitiativeScope) |
| Related skill proposal | SP-004 (aget-check-initiative) |
| Related proposal | PP-001 (Initiative Construct v1) |
| Governing SOP | SOP_SOP_CREATION.md |

---

*SOP_initiative.md v1.3.0*
*"Initiatives group projects. Projects contain gates. Gates produce artifacts."*
