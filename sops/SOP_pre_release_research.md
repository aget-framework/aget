# SOP: Pre-Release Research

**Implements**: R-RES-001-* (18 requirements)
- R-RES-001-01: Conduct adjacent field research before MINOR/MAJOR releases
- R-RES-001-02: Research alternative projects and competing approaches
- R-RES-001-03: Validate theoretical grounding per L332
- R-RES-001-04: Review open enhancement issues for inclusion/deferral
- R-RES-001-05: Document findings in findings/R{N}_{version}_*.md
- R-RES-001-06: Include protocol compliance section in output
- R-RES-001-07: Principal approval required before release proceeds
- R-RES-001-08: Research output informs PROJECT_PLAN gate design
- R-RES-001-09: Audit vocabulary terms for ADD/ENHANCE/PROMOTE/DEPRECATE decisions
- R-RES-001-10: Audit specification requirements for ADD/ENHANCE/PROMOTE/DEPRECATE decisions
- R-RES-001-11: Document vocabulary/spec changes in VERSION_SCOPE
- R-RES-001-12: Cross-agent vocabulary reconciliation per L537/L544
- R-RES-001-13: Audit SOPs for ADD/ENHANCE/EXTRACT/DEPRECATE decisions
- R-RES-001-14: Audit templates for ADD/EXTRACT/ENHANCE/DEPRECATE decisions
- R-RES-001-15: Verify SOP-Template triplet pattern for key artifact types
- R-RES-001-16: Query upstream ({upstream-repo}), public, AND local issue sources
- R-RES-001-17: Apply triage rubric (P1/P2/P3 priority, GO/DEFER/CLOSE decision)
- R-RES-001-18: Route issues to appropriate owner per pattern matching

**Pain Point**: L346 (Research-Before-Action Discipline), L332 (Theoretical Grounding), L537 (Cross-Agent Vocabulary Validation), L544 (Cross-Agent Vocabulary Reconciliation)
**See**: L332 (Theoretical Grounding Protocol), R3 (v2.11 Pre-Release Research)
**Tests**: Manual verification (research quality is human-judged)
**Pattern**: L346 (Protocol-First Research)

---

**Version**: 1.3.0
**Created**: 2026-01-04
**Updated**: 2026-01-17
**Owner**: {agent-name}
**Category**: Release Management
**Related**: L332, L346, SOP_release_process.md, RELEASE_VERIFICATION_CHECKLIST.md

---

## Purpose

Standard operating procedure for conducting deep research before MINOR or MAJOR releases. This ensures:

1. Framework evolution is informed by industry developments
2. Alternative approaches are evaluated (not invented in isolation)
3. Theoretical grounding is validated (per L332)
4. Enhancement backlog is triaged for release scope

**Autonomy Granted**: Agent may execute this SOP autonomously for MINOR releases. MAJOR releases require Principal checkpoint after Phase 2.

---

## Scope

### When Required

| Version Change | Research Required | Depth | Principal Checkpoint |
|----------------|-------------------|-------|---------------------|
| PATCH (3.2.0 → 3.2.1) | **No** | N/A | N/A |
| MINOR (3.2.x → 3.3.0) | **Yes** | Standard | After Phase 4 |
| MAJOR (3.x.x → 4.0.0) | **Yes** | Comprehensive | After Phase 2 AND Phase 4 |

### Trigger Recognition

Execute this SOP when:
- Planning a MINOR or MAJOR version release
- User says "prepare for vX.Y.0 release"
- Creating a release PROJECT_PLAN
- L332 theoretical grounding review is due

---

## Phase 0: Protocol Verification

**Purpose**: Confirm this SOP applies and prerequisites are met

**Duration**: 5 minutes

### Checklist

- [ ] **P0.1**: Version change is MINOR or MAJOR (not PATCH)
- [ ] **P0.2**: No blocking issues prevent research start
- [ ] **P0.3**: Previous research artifacts located (if any)

### Verification Commands

```bash
# V0.1: Check version change type
CURRENT=$(cat .aget/version.json | grep aget_version | cut -d'"' -f4)
TARGET="X.Y.Z"  # Set target version
echo "Current: $CURRENT → Target: $TARGET"
# Manual verification: Is this MINOR or MAJOR?

# V0.2: Check for blocking issues
gh issue list --repo aget-framework/aget --label "blocker" --state open

# V0.3: Locate previous research
ls -la findings/R*_pre_release_research*.md 2>/dev/null || echo "No previous research found"
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| Version change ≥ MINOR | Manual check | [ ] |
| No blockers | V0.2 returns empty | [ ] |
| Previous research located | V0.3 output reviewed | [ ] |

### Decision Gate

- **GO**: All criteria met → Proceed to Phase 1
- **NO-GO**: PATCH release → Exit SOP (not applicable)
- **BLOCKED**: Blockers exist → Resolve blockers first

---

## Phase 1: Adjacent Field Research

**Purpose**: Survey industry developments relevant to AGET

**Duration**: 30-60 minutes (MINOR), 60-120 minutes (MAJOR)

### Research Areas

| Area | Search Topics | Sources |
|------|---------------|---------|
| **1.1 AI Agent Architecture** | Agent memory, multi-agent patterns, orchestration | arXiv, industry blogs, Anthropic/OpenAI docs |
| **1.2 Human-AI Collaboration** | Scaffolding, cognitive forcing, shared regulation | CHI proceedings, Frontiers, Nature |
| **1.3 CLI Tool Ecosystem** | Claude Code updates, Cursor, Codex CLI, MCP | Official docs, release notes, changelogs |
| **1.4 Standards & Protocols** | SKOS, AGENTS.md, MCP, OpenAPI | W3C, IETF, industry standards bodies |
| **1.5 Alternative Frameworks** | LangChain, AutoGPT, CrewAI, MetaGPT | GitHub repos, documentation, comparisons |

### Checklist

- [ ] **P1.1**: AI Agent Architecture — 3+ developments documented
- [ ] **P1.2**: Human-AI Collaboration — 2+ patterns documented
- [ ] **P1.3**: CLI Tool Ecosystem — All major tools checked for updates
- [ ] **P1.4**: Standards & Protocols — Relevant standards reviewed
- [ ] **P1.5**: Alternative Frameworks — 3+ alternatives assessed

### Verification Commands

```bash
# V1.1: Verify research breadth (manual check of output)
# Research output should have sections for each area

# V1.2: Check for recency
# All sources should be from last 6 months (or note if older)

# V1.3: Minimum source count
grep -c "Source:" findings/R*_${VERSION}_*.md || echo "Count sources manually"
# Expected: ≥10 sources for MINOR, ≥20 for MAJOR
```

### Output Format

```markdown
## Part 1: Adjacent Field Advancements

### 1.1 AI Agent Architecture
| Development | Source | Date | AGET Relevance |
|-------------|--------|------|----------------|
| [development] | [source] | [date] | [relevance] |

**Assessment**: [How this informs AGET]

### 1.2 Human-AI Collaboration
[Same format]

### 1.3 CLI Tool Ecosystem
[Same format]

### 1.4 Standards & Protocols
[Same format]

### 1.5 Alternative Frameworks
[Same format]
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| All 5 areas researched | Sections exist in output | [ ] |
| ≥10 sources cited (MINOR) | Source count | [ ] |
| ≥20 sources cited (MAJOR) | Source count | [ ] |
| Each area has assessment | "Assessment:" present | [ ] |

### Decision Gate

- **GO**: All criteria met → Proceed to Phase 2
- **DEFER**: Time constraint → Document partial, schedule completion
- **BLOCKED**: No internet access → Escalate

---

## Phase 2: Theoretical Grounding Review

**Purpose**: Validate theoretical foundations per L332

**Duration**: 30-60 minutes

### Review Checklist (per L332)

- [ ] **P2.1**: New concepts inventoried (what's new in this release?)
- [ ] **P2.2**: Each concept mapped to ≥1 theoretical foundation
- [ ] **P2.3**: L331 (Theoretical Foundations) consulted
- [ ] **P2.4**: `theoretical_basis:` sections drafted for new specs

### Theoretical Foundation Reference (from L331)

| Theory | Key Concept | Apply When |
|--------|-------------|------------|
| BDI | Belief-Desire-Intention | Agent behavior definition |
| Actor Model | Encapsulated actors | Agent boundaries |
| Cybernetics | Requisite variety | Capability selection |
| Extended Mind | Cognitive extension | Capability design |
| CAS | Emergence | Fleet patterns |

### Verification Commands

```bash
# V2.1: List new concepts from planning docs
grep -rh "## New Concepts\|### Concepts Introduced" planning/*.md

# V2.2: Check for theoretical_basis sections
grep -rn "theoretical_basis:" specs/*.yaml specs/*.md

# V2.3: Verify L331 was consulted (manual - check research output)
grep -c "L331\|Theoretical Foundations" findings/R*_${VERSION}_*.md
```

### Output Format

```markdown
## Part 2: Theoretical Grounding Review

### 2.1 New Concepts Inventory

| Concept | Description | Source |
|---------|-------------|--------|
| [concept] | [description] | [spec/L-doc] |

### 2.2 Theory Mapping

| Concept | Primary Theory | Secondary | Rationale |
|---------|---------------|-----------|-----------|
| [concept] | [theory] | [theory] | [why] |

### 2.3 Grounding Gaps

| Gap | Remediation |
|-----|-------------|
| [concept without grounding] | [proposed grounding] |

### 2.4 L332 Compliance

- [ ] All new concepts grounded
- [ ] theoretical_basis sections drafted
- [ ] L331 consulted and cited
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| Concepts inventoried | Section 2.1 complete | [ ] |
| All concepts mapped | Section 2.2 complete | [ ] |
| Gaps identified | Section 2.3 complete | [ ] |
| L332 compliance checked | Section 2.4 complete | [ ] |

### Decision Gate

- **GO**: All concepts grounded → Proceed to Phase 2.5
- **DEFER**: Gaps exist → Document gaps, proceed with remediation plan
- **MAJOR CHECKPOINT**: If MAJOR release → Present to Principal before Phase 2.5

---

## Phase 2.5: Vocabulary/Spec Reconciliation

**Purpose**: Audit vocabulary and specification artifacts for changes needed in this release

**Duration**: 30-45 minutes

**Implements**: R-RES-001-09, R-RES-001-10, R-RES-001-11, R-RES-001-12

### Why This Phase Matters

Spec-first development requires systematic vocabulary/spec maintenance each release:
- **L-docs introduce concepts** that should become formal vocabulary terms
- **Proposals accumulate** that need integration decisions
- **Cross-agent work** may have introduced terms needing reconciliation
- **Obsolete terms** should be deprecated, not left to rot

### Vocabulary Audit (R-RES-001-09)

#### P2.5.1: Source Inventory

Identify vocabulary change candidates from:

| Source | Location | Look For |
|--------|----------|----------|
| L-docs since last release | `.aget/evolution/L*` | New concepts, terminology |
| Proposals | `planning/PROPOSAL_*` | Pending vocabulary terms |
| Cross-agent L-docs | Other agents' evolution/ | Reconciliation needs (L537) |
| Session transcripts | Key terminology introduced | Implicit vocabulary |

```bash
# V2.5.1a: Find L-docs since last release
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
git log ${LAST_TAG}..HEAD --name-only --pretty=format: | grep "evolution/L" | sort -u

# V2.5.1b: Find pending proposals
ls planning/PROPOSAL_*vocabulary*.md planning/PROPOSAL_*spec*.md 2>/dev/null

# V2.5.1c: Check cross-agent reconciliation L-docs
grep -l "reconcil\|L537\|L544" .aget/evolution/*.md
```

#### P2.5.2: Term Classification

For each candidate term, classify action:

| Action | Criteria | Example |
|--------|----------|---------|
| **ADD** | New concept, not in any spec | `Session_Protocol` from L535 |
| **ENHANCE** | Exists but needs expanded definition | `Release_Phase` needs narrower terms |
| **PROMOTE** | Ready to elevate from L-doc to spec | L-doc concept → VOCABULARY_SPEC term |
| **DEPRECATE** | Obsolete, superseded, or confusing | Old term replaced by better one |
| **RECONCILE** | Cross-agent alignment needed | Same concept, different names |

#### P2.5.3: Vocabulary Change Table

```markdown
| Term | Current Location | Action | Target Location | Rationale |
|------|------------------|--------|-----------------|-----------|
| [term] | L-doc/none | ADD | AGET_VOCABULARY_SPEC | [why] |
| [term] | VOCABULARY_SPEC | ENHANCE | VOCABULARY_SPEC | [what to add] |
| [term] | L-doc | PROMOTE | AGET_*_SPEC | [readiness evidence] |
| [term] | VOCABULARY_SPEC | DEPRECATE | N/A | [superseded by] |
| [term] | Agent A vs B | RECONCILE | Both | [alignment approach] |
```

### Specification Audit (R-RES-001-10)

#### P2.5.4: Spec Change Candidates

Identify specification changes needed:

| Source | Look For |
|--------|----------|
| L-docs with requirements | New R-* or CAP-* candidates |
| Governance gaps discovered | Missing EARS requirements |
| Proposals | Pending spec enhancements |
| Pain points | Undocumented requirements |

```bash
# V2.5.4a: Find L-docs with requirement patterns
grep -l "SHALL\|SHOULD\|MUST\|R-[A-Z]" .aget/evolution/L*.md

# V2.5.4b: Find spec-related proposals
ls planning/PROPOSAL_*spec*.md planning/PROPOSAL_*requirement*.md 2>/dev/null
```

#### P2.5.5: Spec Change Table

```markdown
| Requirement | Current State | Action | Target Spec | Rationale |
|-------------|---------------|--------|-------------|-----------|
| [R-XXX-*] | None | ADD | AGET_*_SPEC | [source L-doc] |
| [CAP-XXX-*] | Incomplete | ENHANCE | AGET_*_SPEC | [what to add] |
| [R-XXX-*] | Draft | PROMOTE | AGET_*_SPEC | [validation evidence] |
| [R-XXX-*] | Published | DEPRECATE | N/A | [superseded by] |
```

### Cross-Agent Reconciliation (R-RES-001-12)

#### P2.5.6: Reconciliation Check

If this agent manages shared vocabulary (e.g., aget-framework):

```bash
# V2.5.6: Check for cross-agent vocabulary L-docs
grep -rn "vocabulary\|reconcil" ../*/\.aget/evolution/*.md 2>/dev/null | head -20
```

| Pattern | Action |
|---------|--------|
| Same concept, different names | Choose canonical term, add altLabels |
| Same name, different meanings | Disambiguate or scope-qualify |
| Gaps in one agent's vocabulary | Propagate from authoritative source |

### Checklist

- [ ] **P2.5.1**: Vocabulary source inventory complete
- [ ] **P2.5.2**: All candidate terms classified (ADD/ENHANCE/PROMOTE/DEPRECATE/RECONCILE)
- [ ] **P2.5.3**: Vocabulary change table populated
- [ ] **P2.5.4**: Spec change candidates identified
- [ ] **P2.5.5**: Spec change table populated
- [ ] **P2.5.6**: Cross-agent reconciliation checked (if applicable)

### Output Format

```markdown
## Part 2.5: Vocabulary/Spec Reconciliation

### 2.5.1 Vocabulary Changes

| Term | Action | Target | Rationale |
|------|--------|--------|-----------|
| [term] | ADD/ENHANCE/PROMOTE/DEPRECATE | [spec] | [why] |

**Summary**: N terms to ADD, N to ENHANCE, N to PROMOTE, N to DEPRECATE

### 2.5.2 Specification Changes

| Requirement | Action | Target Spec | Rationale |
|-------------|--------|-------------|-----------|
| [R-XXX-*] | ADD/ENHANCE/PROMOTE/DEPRECATE | [spec] | [why] |

**Summary**: N requirements to ADD, N to ENHANCE, N to PROMOTE, N to DEPRECATE

### 2.5.3 Cross-Agent Reconciliation

| Term/Requirement | Agents | Issue | Resolution |
|------------------|--------|-------|------------|
| [item] | [agents] | [conflict] | [approach] |

### 2.5.4 VERSION_SCOPE Integration

These changes are documented in VERSION_SCOPE_vX.Y.Z.md:
- [ ] Vocabulary section updated
- [ ] Spec section updated
- [ ] Reconciliation notes added
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| Vocabulary sources audited | P2.5.1 complete | [ ] |
| All terms classified | P2.5.3 table complete | [ ] |
| Spec changes identified | P2.5.5 table complete | [ ] |
| Cross-agent check done | P2.5.6 complete or N/A | [ ] |
| VERSION_SCOPE updated | R-RES-001-11 | [ ] |

### Decision Gate

- **GO**: All changes documented → Proceed to Phase 2.6
- **DEFER**: Large reconciliation needed → Create PROJECT_PLAN, proceed
- **ESCALATE**: Cross-agent conflicts → Coordinate with other agents first

---

## Phase 2.6: SOP/Template Reconciliation

**Purpose**: Audit SOPs and templates for changes needed in this release

**Duration**: 20-30 minutes

**Implements**: R-RES-001-13, R-RES-001-14, R-RES-001-15

### Why This Phase Matters

Artifact governance requires systematic SOP/Template maintenance each release:
- **New artifact types** may need SOP + Template pairs
- **Existing SOPs** may have inline templates that should be extracted
- **Template gaps** create inconsistent artifact quality
- **Obsolete SOPs/Templates** should be deprecated

### SOP Audit (R-RES-001-13)

#### P2.6.1: SOP Inventory

Identify SOP change candidates:

| Source | Location | Look For |
|--------|----------|----------|
| L-docs since last release | `.aget/evolution/L*` | New processes needing SOPs |
| Session patterns | Repeated manual processes | SOP candidates |
| Enhancement requests | `planning/ENHANCEMENT_REQUEST_*` | Process improvements |

```bash
# V2.6.1a: List all SOPs
ls sops/SOP_*.md | wc -l

# V2.6.1b: Find L-docs mentioning SOP needs
grep -l "SOP\|process\|procedure" .aget/evolution/L*.md | tail -10

# V2.6.1c: Check for SOPs without templates
for sop in sops/SOP_*.md; do
  grep -q "TEMPLATE_\|template:" "$sop" || echo "No template ref: $sop"
done
```

#### P2.6.2: SOP Classification

For each candidate, classify action:

| Action | Criteria | Example |
|--------|----------|---------|
| **ADD** | New process needs governance | SOP_L-DOC_CREATION.md |
| **ENHANCE** | SOP exists but incomplete | Add template reference |
| **EXTRACT** | Inline template should be external | Session handoff template |
| **DEPRECATE** | SOP obsolete or superseded | Old migration SOP |

### Template Audit (R-RES-001-14)

#### P2.6.3: Template Inventory

Identify template gaps:

| Source | Look For |
|--------|----------|
| SOPs creating artifacts | Missing TEMPLATE_*.md reference |
| Inline templates | Should be extracted to sops/templates/ |
| Artifact types | No standardized template |

```bash
# V2.6.3a: List all templates
ls sops/templates/*.md planning/TEMPLATE_*.md 2>/dev/null

# V2.6.3b: Find SOPs with inline templates (```markdown blocks)
grep -l '```markdown' sops/SOP_*.md

# V2.6.3c: Count artifact types without templates
echo "Checking: L-docs, Enhancement Requests, Proposals, Patterns..."
```

#### P2.6.4: Template Classification

| Action | Criteria | Example |
|--------|----------|---------|
| **ADD** | Artifact type lacks template | TEMPLATE_L-DOC.md |
| **EXTRACT** | Inline template in SOP | TEMPLATE_SESSION_HANDOFF.md |
| **ENHANCE** | Template incomplete | Add required sections |
| **DEPRECATE** | Template obsolete | Remove unused templates |

### SOP-Template Triplet Pattern (R-RES-001-15)

#### P2.6.5: Triplet Verification

For each artifact type that should have governance:

| Artifact Type | SOP? | Template? | Gap |
|---------------|:----:|:---------:|-----|
| L-docs | ? | ? | SOP + Template |
| Enhancement Requests | ? | ? | SOP + Template |
| PROJECT_PLANs | ✅ | ✅ | None |
| SOPs | ✅ | ✅ | None |
| VERSION_SCOPEs | ✅ | ✅ | None |

**Pattern**: `SOP_{artifact}_CREATION.md` → `TEMPLATE_{artifact}.md` → Artifact

### Checklist

- [ ] **P2.6.1**: SOP inventory complete
- [ ] **P2.6.2**: All candidate SOPs classified (ADD/ENHANCE/EXTRACT/DEPRECATE)
- [ ] **P2.6.3**: Template inventory complete
- [ ] **P2.6.4**: All candidate templates classified
- [ ] **P2.6.5**: Triplet verification for key artifact types

### Output Format

```markdown
## Part 2.6: SOP/Template Reconciliation

### 2.6.1 SOP Changes

| SOP | Action | Rationale |
|-----|--------|-----------|
| [sop] | ADD/ENHANCE/EXTRACT/DEPRECATE | [why] |

**Summary**: N SOPs to ADD, N to ENHANCE, N to EXTRACT templates, N to DEPRECATE

### 2.6.2 Template Changes

| Template | Action | Source SOP | Rationale |
|----------|--------|------------|-----------|
| [template] | ADD/EXTRACT/ENHANCE/DEPRECATE | [sop] | [why] |

**Summary**: N templates to ADD, N to EXTRACT, N to ENHANCE, N to DEPRECATE

### 2.6.3 Triplet Gaps

| Artifact Type | Missing | Priority |
|---------------|---------|----------|
| [type] | SOP/Template/Both | HIGH/MEDIUM/LOW |
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| SOP inventory complete | P2.6.1 done | [ ] |
| SOPs classified | P2.6.2 table complete | [ ] |
| Templates classified | P2.6.4 table complete | [ ] |
| Triplet gaps identified | P2.6.5 table complete | [ ] |

### Decision Gate

- **GO**: All changes documented → Proceed to Phase 3
- **DEFER**: Large SOP/Template work needed → Create PROJECT_PLAN, proceed
- **ESCALATE**: Cross-cutting changes → Coordinate with template owners

---

## Phase 3: Enhancement Issue Review

**Purpose**: Triage open issues for release scope

**Duration**: 20-40 minutes (MINOR), 60-90 minutes (MAJOR or >30 issues)

**Implements**: R-RES-001-16, R-RES-001-17, R-RES-001-18

### Issue Sources (R-RES-001-16)

Query BOTH upstream and public repos:

| Repo | Purpose | Query |
|------|---------|-------|
| `{upstream-repo}` | Upstream supervisor issues | `gh issue list --repo {upstream-repo} --state open` |
| `aget-framework/aget` | Public framework issues | `gh issue list --repo aget-framework/aget --state open` |
| Local `ENHANCEMENT_REQUEST_*.md` | Agent-local requests | `ls planning/ENHANCEMENT_REQUEST_*.md` |

### Triage Rubric (R-RES-001-17)

#### Priority Classification

| Priority | Definition | Criteria |
|----------|------------|----------|
| **P1: Release-Critical** | Blocks release or addresses critical gap | ANY: Release blocker, Active pain point, Required for release theme |
| **P2: Release-Aligned** | Enhances release value, fits scope | ALL: Aligns with theme, Achievable (≤1 session), No blocking dependencies |
| **P3: Backlog** | Valid enhancement, not release-aligned | ANY: Doesn't fit theme, Large effort, Unresolved dependencies |

**Priority Decision Tree**:
```
Is issue a release blocker?
  → YES: P1
  → NO: Does issue align with VERSION_SCOPE theme?
         → YES: Is effort ≤1 session AND dependencies resolved?
                  → YES: P2
                  → NO: P3
         → NO: P3
```

#### GO/DEFER/CLOSE Decision

| Decision | Definition | Criteria |
|----------|------------|----------|
| **GO** | Include in this release | ALL: P1 or P2, This agent owns, Fits scope, Achievable |
| **DEFER** | Valid but not now | ANY: P3, Different owner, Dependencies unmet, Exceeds scope |
| **CLOSE** | Remove from backlog | ANY: Obsolete/superseded, Duplicate, Won't fix |

**Decision Matrix**:

| Priority | This Agent Owns | Fits Scope | Deps Met | → Decision |
|:--------:|:---------------:|:----------:|:--------:|------------|
| P1 | ✅ | ✅ | ✅ | **GO** |
| P1 | ✅ | ✅ | ❌ | **GO** (resolve deps) |
| P1 | ❌ | - | - | **DEFER** (route) |
| P2 | ✅ | ✅ | ✅ | **GO** |
| P2 | ✅ | ❌ | - | **DEFER** (next version) |
| P2 | ❌ | - | - | **DEFER** (route) |
| P3 | - | - | - | **DEFER** (future) |

#### Owner Routing

| Issue Pattern | Owner | Action |
|---------------|-------|--------|
| `[supervisor]` | Supervisor | DEFER + note |
| `[supervisor]` | Supervisor | DEFER + note |
| `[Framework]` | aget-framework-AGET | Evaluate |
| `[Migration]` | Named agent | DEFER + note |
| Template/Spec-related | aget-framework-AGET | Evaluate |

#### Theme Alignment Test

Check issue against VERSION_SCOPE theme components:

```
Does issue improve session skills? → Theme-aligned
Does issue improve artifact governance? → Theme-aligned
Does issue improve release process? → Theme-aligned
Does issue add vocabulary/spec formalization? → Theme-aligned
Otherwise → Not theme-aligned (P3)
```

### Review Process (R-RES-001-18)

1. Query all issue sources (upstream + public + local)
2. Apply priority rubric (P1/P2/P3)
3. Apply GO/DEFER/CLOSE decision matrix
4. Route to owner if not this agent
5. Document all decisions with rationale

### Checklist

- [ ] **P3.1**: All open issues listed with metadata
- [ ] **P3.2**: Each issue has priority assigned
- [ ] **P3.3**: Each issue has GO/DEFER/CLOSE decision
- [ ] **P3.4**: Scope documented (what's IN for this release)

### Verification Commands

```bash
# V3.1a: List upstream issues (R-RES-001-16)
gh issue list --repo {upstream-repo} --state open --json number,title,labels

# V3.1b: List public issues (R-RES-001-16)
gh issue list --repo aget-framework/aget --state open --json number,title,labels

# V3.1c: List local enhancement requests (R-RES-001-16)
ls planning/ENHANCEMENT_REQUEST_*.md

# V3.2: Count issues by decision (manual after triage)
# GO: N issues
# DEFER: N issues
# CLOSE: N issues

# V3.3: Verify no unreviewed issues
UPSTREAM=$(gh issue list --repo {upstream-repo} --state open --json number | jq length)
PUBLIC=$(gh issue list --repo aget-framework/aget --state open --json number | jq length)
LOCAL=$(ls planning/ENHANCEMENT_REQUEST_*.md 2>/dev/null | wc -l)
echo "Total: $((UPSTREAM + PUBLIC + LOCAL)) issues to review"
```

### Output Format

```markdown
## Part 3: Enhancement Issue Review

### 3.1 Open Issues Inventory

| # | Title | Priority | Decision | Rationale |
|---|-------|----------|----------|-----------|
| N | [title] | P1/P2/P3 | GO/DEFER/CLOSE | [why] |

### 3.2 Release Scope

**In Scope (GO)**:
- #N: [title]
- #N: [title]

**Deferred**:
- #N: [title] → v{next}
- #N: [title] → future

**Closed**:
- #N: [title] — [reason]

### 3.3 Triage Metrics

| Metric | Count |
|--------|-------|
| Total reviewed | N |
| GO (in scope) | N |
| DEFER | N |
| CLOSE | N |
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| All issues reviewed | V3.3 counts match | [ ] |
| Priorities assigned | Column complete | [ ] |
| Decisions documented | Column complete | [ ] |
| Scope clear | Section 3.2 complete | [ ] |

### Decision Gate

- **GO**: All issues triaged → Proceed to Phase 4
- **DEFER**: Too many issues → Timebox and proceed with partial
- **ESCALATE**: Conflicting priorities → Present to Principal

**Cross-reference**: Triaged items (GO decisions) feed into `aget/sops/SOP_release_scope_decision.md` Phase 1 (Priority_Classification) for VERSION_SCOPE assignment.

---

## Phase 4: Synthesis and Recommendations

**Purpose**: Synthesize findings into actionable recommendations

**Duration**: 20-30 minutes

### Synthesis Checklist

- [ ] **P4.1**: Gap analysis complete (what's missing?)
- [ ] **P4.2**: Recommendations documented
- [ ] **P4.3**: Risk assessment complete
- [ ] **P4.4**: Release readiness assessment

### Output Format

```markdown
## Part 4: Synthesis and Recommendations

### 4.1 Gap Analysis

| Gap | Severity | Remediation | Blocking? |
|-----|----------|-------------|-----------|
| [gap] | High/Med/Low | [action] | Yes/No |

### 4.2 Recommendations

1. **[Recommendation 1]**: [rationale]
2. **[Recommendation 2]**: [rationale]
3. **[Recommendation 3]**: [rationale]

### 4.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [risk] | High/Med/Low | High/Med/Low | [mitigation] |

### 4.4 Release Readiness

| Component | Status | Notes |
|-----------|--------|-------|
| Adjacent field alignment | ✅/⚠️/❌ | [notes] |
| Theoretical grounding | ✅/⚠️/❌ | [notes] |
| Enhancement scope | ✅/⚠️/❌ | [notes] |
| Overall readiness | ✅/⚠️/❌ | [notes] |

### 4.5 Recommended PROJECT_PLAN Gates

Based on this research, the release PROJECT_PLAN should include:

| Gate | Focus | Derived From |
|------|-------|--------------|
| G-0 | [focus] | [research finding] |
| G-1 | [focus] | [research finding] |
| ... | ... | ... |
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| Gaps documented | Section 4.1 complete | [ ] |
| ≥3 recommendations | Section 4.2 has 3+ items | [ ] |
| Risks assessed | Section 4.3 complete | [ ] |
| Readiness determined | Section 4.4 complete | [ ] |

### Decision Gate

- **GO (Ready)**: All ✅ in readiness → Proceed to Phase 5
- **GO (Conditional)**: Some ⚠️ → Proceed with documented gaps
- **NO-GO**: Any ❌ → Remediate before release
- **PRINCIPAL CHECKPOINT**: Present findings for approval

---

## Phase 5: Documentation and Handoff

**Purpose**: Finalize research artifact and hand off to release process

**Duration**: 15-20 minutes

### Documentation Checklist

- [ ] **P5.1**: Research document complete (all parts)
- [ ] **P5.2**: Protocol compliance section added
- [ ] **P5.3**: Document saved to findings/
- [ ] **P5.4**: Committed to repository

### Verification Commands

```bash
# V5.1: Verify document structure
for section in "Part 1" "Part 2" "Part 3" "Part 4"; do
  grep -q "$section" findings/R*_${VERSION}_*.md && echo "✅ $section" || echo "❌ $section"
done

# V5.2: Verify protocol compliance section
grep -q "Protocol Compliance" findings/R*_${VERSION}_*.md && echo "✅ Protocol section" || echo "❌ Protocol section"

# V5.3: Verify file location
ls -la findings/R*_${VERSION}_pre_release_research_*.md

# V5.4: Verify committed
git status findings/
```

### Output: Final Document Structure

```markdown
# R{N}: v{VERSION} Pre-Release Research Findings

**Date**: YYYY-MM-DD
**Type**: Research Report
**Author**: {agent-name}
**Purpose**: Pre-release research per SOP_pre_release_research.md

---

## Protocol Compliance

| Protocol | Requirement | Status |
|----------|-------------|--------|
| SOP_pre_release_research | Phase 0-5 complete | ✅ |
| L332 | Theoretical grounding | ✅ |
| L346 | Research-before-action | ✅ |

---

## Part 1: Adjacent Field Advancements
[From Phase 1]

## Part 2: Theoretical Grounding Review
[From Phase 2]

## Part 3: Enhancement Issue Review
[From Phase 3]

## Part 4: Synthesis and Recommendations
[From Phase 4]

---

## Conclusion

[Summary and next steps]

---

*R{N}: v{VERSION} Pre-Release Research Findings*
*{agent-name} | {date}*
```

### Exit Criteria

| Criterion | Verification | Status |
|-----------|--------------|--------|
| Document complete | V5.1 all ✅ | [ ] |
| Protocol compliance documented | V5.2 ✅ | [ ] |
| Saved correctly | V5.3 shows file | [ ] |
| Committed | V5.4 shows clean | [ ] |

### Final Decision Gate

- **COMPLETE**: All phases passed → Hand off to SOP_release_process.md
- **INCOMPLETE**: Gaps remain → Document and schedule follow-up

---

## Verification Summary

### Phase Gate Summary

| Phase | Purpose | Key Verification | Blocking? |
|-------|---------|------------------|-----------|
| P0 | Protocol verification | Version is MINOR/MAJOR | Yes |
| P1 | Adjacent field research | ≥10 sources, 5 areas | Yes |
| P2 | Theoretical grounding | All concepts mapped | Yes (MAJOR) |
| P2.5 | Vocabulary/Spec reconciliation | Changes classified (ADD/ENHANCE/PROMOTE/DEPRECATE) | Yes |
| P2.6 | SOP/Template reconciliation | SOP-Template triplet gaps identified | Yes |
| P3 | Enhancement triage | All issues reviewed | No |
| P4 | Synthesis | Readiness assessment | Yes |
| P5 | Documentation | Document committed | Yes |

### Autonomy Levels

| Release Type | Phases Autonomous | Principal Checkpoints |
|--------------|-------------------|----------------------|
| MINOR | P0-P3 | After P4 (before release) |
| MAJOR | P0-P1 | After P2, After P4 |

---

## Anti-Patterns

### 1. Research Theater

**Wrong**: Claiming research without actual web searches or source review.

**Detection**: No sources cited, no dates, generic findings.

**Right**: Cite specific sources with dates, quote findings.

### 2. Confirmation Bias

**Wrong**: Only researching topics that confirm existing approach.

**Detection**: No alternative frameworks reviewed, no challenges found.

**Right**: Actively seek alternatives and counterarguments.

### 3. Skipping Theoretical Grounding

**Wrong**: "L332 doesn't apply to this release."

**Detection**: No Part 2 in research output.

**Right**: L332 applies to ALL MINOR/MAJOR releases.

### 4. Shallow Enhancement Review

**Wrong**: "Issues look fine, proceeding."

**Detection**: No priority assignments, no GO/DEFER decisions.

**Right**: Every issue gets explicit decision with rationale.

---

## References

- L332: Theoretical Grounding Protocol
- L346: Research-Before-Action Discipline
- L331: Theoretical Foundations of Agency
- R3: v2.11 Pre-Release Research (exemplar)
- SOP_release_process.md: Release execution
- RELEASE_VERIFICATION_CHECKLIST.md: Post-release validation

---

## Naming Convention

Research output files follow:

```
findings/R{N}_{version}_pre_release_research_{date}.md
```

Where:
- `{N}` = Sequential research number (R1, R2, R3...)
- `{version}` = Target version (v3.3.0 → v3.3.0)
- `{date}` = YYYY-MM-DD

Example: `findings/R4_v3.3.0_pre_release_research_2026-01-04.md`

---

*SOP_pre_release_research.md v1.3.0 — Deep research before MINOR/MAJOR releases*
*v1.3.0: Added Phase 3 Triage Rubric (R-RES-001-16 through R-RES-001-18) — priority/decision criteria, multi-repo sources*
*v1.2.0: Added Phase 2.6 SOP/Template Reconciliation (R-RES-001-13 through R-RES-001-15)*
*v1.1.0: Added Phase 2.5 Vocabulary/Spec Reconciliation (R-RES-001-09 through R-RES-001-12)*
*Autonomy: High (MINOR) | Medium (MAJOR)*
*Verification: Strong (7 phases, 30+ checks)*
