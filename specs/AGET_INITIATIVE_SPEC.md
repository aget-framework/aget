# AGET INITIATIVE Specification

**Version**: 1.1.1
**Status**: Active
**Category**: Process (Planning / Governance)
**Created**: 2026-05-14
**Updated**: 2026-05-14
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_INITIATIVE_SPEC.md`
**Change Origin**: 2026-05-14 session — `/aget-propose-initiative` design request; principal GO 2026-05-14
**v1.0.1 Patch**: Fix §4 vocabulary anti-pattern stale count (6 → 7) per Gate -1 Auditor finding in PROJECT_PLAN_aget_propose_initiative_v1.0 / `planning/triad_findings.jsonl` line 35.
**v1.1.1 Patch**: Split V-INIT-PROP-003 into creation-mode + revalidation-mode per Gate 2 Auditor finding in PROJECT_PLAN_aget_propose_initiative_v1.0 / `planning/triad_findings.jsonl` line 36. Resolves creation-time-only semantics gap.
**v1.1.0 Minor (additive — no behavioral / R-INIT-PROP / V-INIT-PROP changes)**: SKOS uplift per PP-028 (PROPOSAL_spec_aget_initiative_v1.1_skos_uplift.md, principal Approve 2026-05-14 PM). §4 vocabulary table extends `Initiative` / `Initiative_Proposal` / `Initiative_Manifest` / `Stream` SKOS links to Meta-Ontological cluster (C404-C408); §4 anti-patterns add `Decorative_Initiative_Reference → skos:narrower: C408 PortfolioTheater`, `Direct_Initiative_Authoring → skos:related: C544`, `Project_Template_Reuse → skos:related: C547`; `Channel` and `Contributor_Role` add `skos:candidate` annotations naming ontology gaps (InitiativeChannelRegistry per L813, ContributorValueProfile); §10 traceability adds 5 rows. **First-instance dogfood** of INIT-ONTOLOGY-SPEC-BINDING discipline (gh#1241) applied to canonical spec landed 2026-05-14 — closes recursive C544 self-application gap assessed in same session at 5/10 grounding score. Pairs with `docs/FINDING_per_agent_ontology_grounding_gap_2026-05-14.md` Evidence 4 + `docs/MEMO_ontology_grounding_initiative_overlap_2026-05-14.md` Finding M-1.
**Related Specs**: AGET_PROJECT_PLAN_SPEC (sibling structural pattern), AGET_SOP_SPEC, AGET_ISSUE_GOVERNANCE_SPEC (#916 channel registry source)
**Related SOP**: `sops/SOP_initiative.md` v1.2.0 (procedural canon — this spec promotes its rules to contract level)

---

## 1. Abstract

This specification defines requirements for the **initiative artifact class** in the AGET framework — what an initiative IS, what its proposal artifact IS, and how proposals transition to manifests.

Today (2026-05-14), `sops/SOP_initiative.md` v1.2.0 is the only canonical source for initiative procedure. Per ADR-008 (Advisory → Strict → Generator), the SOP is graduated; this spec formalizes its contract-level requirements so that downstream skills (`/aget-propose-initiative`, `/aget-create-initiative`, `/aget-check-initiative`) can be authored against a stable governing spec rather than against the SOP directly.

**v1.0.0 scope**: This spec formalizes the **proposal stage only** (CAP-INIT-PROP-*) — the contract that `/aget-propose-initiative` implements. Create-stage and close-stage capabilities are deferred to v2.0.0 (placeholder reference: `[v2.0.0 candidate]`) to preserve the coherent verb-pair design without expanding scope-of-decision.

## 2. Motivation

Concrete failures observed in 2026-04 / 2026-05 sessions:

| # | Failure | Source | Cost |
|---|---------|--------|------|
| 1 | INIT-REQ-SPEC-TEST-DEFINED authored 2026-04-19 via direct Write — no proposal gate, no cross-initiative overlap check | 2026-04-19 session | Same-day proposal `PROPOSAL_aget-create-initiative.md` filed to close the gap. Open since. |
| 2 | INIT-PRINCIPLED-EXECUTION referenced in scope tables (v3.15 P1 #3, v3.16 CF-1) but no initiative file exists | `planning/initiatives/INDEX.md` Finding #4 | gh#1193 OPEN since 2026-05-02. Decorative reference, untriaged. |
| 3 | 6 PROPOSED initiatives (PP-014, PP-017..020, PP-027) shipped through their target version windows without disposition | INDEX.md "v3.18 Grooming Inputs" section, 2026-05-14 truth-up | Carry-forward debt; 5 of 6 now past-target. |
| 4 | Status taxonomy drift: SOP enum (ACTIVE/COMPLETE/CLOSED/PAUSED) vs. INDEX enum (ACTIVE/PROPOSED/DORMANT/RETIRED) vs. wild usage (NASCENT) — 3 vocabularies | `docs/FINDING_initiative_status_taxonomy_2026-05-14.md` | Spec-vs-wild divergence; Decide gate G4 open. |
| 5 | Initiative proposals reuse the `/aget-propose-project` template — Channels (#916), Contributors (#910), and cross-initiative-overlap sections are absent from all 7 existing initiative proposals (PP-014, 016, 017, 018, 019, 020, 027) | `planning/project-proposals/PROPOSAL_init_*.md` survey 2026-05-14: 0/7 have `## Channels`, 0/7 have `## Contributors`, 0/7 have `## Cross-Initiative Overlap` | Initiative-specific concerns invisible at proposal review time. |

L867 names the underlying class: **artifact-needs-skill** — when an artifact class lacks its own propose/create skill pair, it accumulates governance bypass debt at a measurable rate (5 of 6 PROPOSED initiatives = 83% bypass-debt accrual within 6 weeks).

## 3. Scope

**Applies to**: All INIT-*.md artifacts in any AGET agent's `planning/initiatives/` directory, and all PROPOSAL_init_*.md artifacts in any AGET agent's `planning/project-proposals/` directory.

**v0.1 Defines**:
- Initiative-proposal artifact format (R-INIT-PROP-* / CAP-INIT-PROP-*)
- Initiative-proposal lifecycle states
- Cross-initiative overlap check requirements
- Channel registry inclusion requirements (per #916)
- Contributor profile inclusion requirements (per #910 / L572)
- Verification tests for each requirement (V-INIT-PROP-*)

**v0.1 Does NOT cover** (deferred to v0.2):
- Initiative manifest format (R-INIT-MFST-* / CAP-INIT-MFST-*) — currently governed by `sops/SOP_initiative.md` §"Initiative Manifest Template"
- Proposal→manifest transition (`/aget-create-initiative` skill contract)
- Initiative closure (`/aget-close-initiative` — not yet proposed)
- Status enum reconciliation across SOP/INDEX/wild (deferred to G4 Decide; this spec normalizes to the proposal-stage state only)
- Initiative Relevance Rubric (#886) — feeds Decision section but lives elsewhere

**Does not cover** (out of scope permanently):
- PROJECT_PLAN format (see AGET_PROJECT_PLAN_SPEC)
- SOP format (see AGET_SOP_SPEC)
- Initiative execution / stream tracking (operational, not contractual)

---

## 4. Vocabulary

```yaml
vocabulary:
  meta:
    domain: "planning"
    version: "0.1.0"
    inherits: "aget_core"

  initiative_structure:
    Initiative:
      skos:definition: "Multi-version, multi-project work container grouped by initiative_id (a scope modifier per L760, not a first-class entity)"
      aget:naming: "INIT-{UPPER-KEBAB-CASE}"
      skos:example: "INIT-CORE-ARTIFACT-MATURATION"
      skos:related: ["L760", "C227-InitiativeScope", "C404-InitiativeCoverageCriterion", "C405-DemandDrivenInitiativeGraduation"]

    Initiative_Proposal:
      skos:definition: "Lightweight proposal artifact filed before initiative manifest creation; produced by /aget-propose-initiative"
      aget:naming: "PROPOSAL_init_{snake_case}.md"
      aget:location: "planning/project-proposals/"
      aget:id_format: "PP-{NNN}"
      skos:example: "PROPOSAL_init_public_surface_enhancement.md (PP-027)"
      skos:related: ["CAP-INIT-PROP-001", "C405-DemandDrivenInitiativeGraduation"]

    Initiative_Manifest:
      skos:definition: "Initiative scaffold authored after proposal approval; the canonical file representing an initiative in flight"
      aget:naming: "INIT-{UPPER-KEBAB-CASE}.md"
      aget:location: "planning/initiatives/"
      skos:related: ["sops/SOP_initiative.md §Template", "C406-StrategicAlignmentFramework"]

    Stream:
      skos:definition: "Parallel work track within an initiative; analogous to a Gate in PROJECT_PLAN but with no strict ordering across streams. Formally the third stratum of governance per C407."
      skos:broader: "C407-PortfolioProjectStreamTriStratum"
      aget:related: ["L760"]

    Channel:
      skos:definition: "External communication or coordination surface registered to an initiative (Slack, Linear, GitHub milestone, KB-only)"
      aget:format: "{name} / {ID} / {purpose} / {priority}"
      skos:related: ["#916", "REQ-CHKI-005"]
      skos:candidate: "InitiativeChannelRegistry [proposed L813 2026-04-09, not landed in ontology as of 2026-05-14]"

    Contributor_Role:
      skos:definition: "Role archetype contributing to an initiative; descriptive (value supplied) not evaluative (performance)"
      aget:format: "{role} / {value_dimensions} / {availability}"
      skos:related: ["#910", "L572"]
      skos:candidate: "ContributorValueProfile [no canonical concept exists as of 2026-05-14; ontology gap]"

  proposal_lifecycle:
    Proposal_Status:
      skos:definition: "State of a PROPOSAL_init_*.md artifact"
      aget:values: ["PROPOSED", "APPROVED", "DEFERRED", "REJECTED"]
      skos:related: ["CAP-INIT-PROP-010"]

  manifest_lifecycle:
    Manifest_Status:
      skos:definition: "State of an INIT-*.md manifest artifact (v0.1 leaves this to SOP_initiative.md; G4 Decide gate open)"
      aget:status: "DEFERRED to v0.2"

  anti_patterns:
    Direct_Initiative_Authoring:
      skos:definition: "Creating INIT-*.md via direct Write/Edit, bypassing the proposal stage"
      aget:anti_pattern: true
      skos:related: ["L867", "C544-MetaSpecificationGap", "2026-04-19 INIT-REQ-SPEC-TEST-DEFINED incident"]

    Decorative_Initiative_Reference:
      skos:definition: "Citing an INIT-NAME in scope tables, plans, or commits without a corresponding INIT-*.md file"
      aget:anti_pattern: true
      skos:narrower: "C408-PortfolioTheater (alt: Initiative Theater) — this anti-pattern is a narrower instance of the canonical theater pattern"
      skos:related: ["L671", "INIT-PRINCIPLED-EXECUTION / gh#1193"]

    Project_Template_Reuse:
      skos:definition: "Filing an initiative proposal using the /aget-propose-project template — initiative-specific sections (Channels, Contributors, Overlap) missing"
      aget:anti_pattern: true
      skos:related: ["C547-VocabularyFirstNamingDiscipline", "PP-014, PP-016, PP-017, PP-018, PP-019, PP-020, PP-027 — all 7 currently filed in this pattern"]
```

---

## 5. Requirements (Human Level — L742 Requirements Layer)

These are the principal-readable intent statements. Each requirement R-INIT-PROP-### maps to one or more EARS clauses in §6.

| ID | Requirement (principal intent) | Evidence | Maps to |
|----|-------------------------------|----------|---------|
| R-INIT-PROP-001 | Before any new INIT-*.md is authored, a proposal artifact MUST exist | L867 + 2026-04-19 INIT-REQ-SPEC-TEST-DEFINED incident | CAP-INIT-PROP-001, CAP-INIT-PROP-010 |
| R-INIT-PROP-002 | Initiative proposals MUST be distinguishable from project proposals at a glance | PP-027 mis-classified as project-class proposal; survey of PP-014..020 | CAP-INIT-PROP-001, CAP-INIT-PROP-002 |
| R-INIT-PROP-003 | The proposal MUST check for overlap with all existing initiatives (active + proposed + carry-forward) | L760 — initiatives organize; overlap is the load-bearing failure mode | CAP-INIT-PROP-003, CAP-INIT-PROP-004 |
| R-INIT-PROP-004 | The proposal MUST declare which channels (Slack, Linear, GitHub milestone, KB-only) the initiative will use | #916 Initiative-scoped channel registry pattern + REQ-CHKI-005 precedence | CAP-INIT-PROP-005 |
| R-INIT-PROP-005 | The proposal MUST declare which contributor role archetypes will supply value, and what value dimensions each supplies | #910 Contributor Value Profile + L572 | CAP-INIT-PROP-006 |
| R-INIT-PROP-006 | The proposal MUST cite ≥3 evidence anchors (L-doc, session, or issue) for its problem statement | Evidence-driven principal directive + L289 + ADR-008 readiness | CAP-INIT-PROP-007 |
| R-INIT-PROP-007 | The proposal MUST include a Decision section with explicit Approve / Defer / Reject / Fold-into-existing options | L42 Stop-at-gate + #886 Initiative Relevance Rubric input | CAP-INIT-PROP-008 |
| R-INIT-PROP-008 | The proposal MUST be assigned a unique PP-### ID in the shared PROJECT_PLAN proposal sequence | Continuity with existing PP-001..PP-027 numbering | CAP-INIT-PROP-002 |
| R-INIT-PROP-009 | The proposal MUST update `planning/project-proposals/INDEX.md` with a new row | INDEX as the authoritative proposal registry | CAP-INIT-PROP-009 |
| R-INIT-PROP-010 | The proposal MUST NOT author the INIT-*.md manifest file (separation of concerns between propose and create) | Mirrors /aget-propose-project ≠ /aget-create-project | CAP-INIT-PROP-011 |
| R-INIT-PROP-011 | The proposal SHALL cite the ADR-008 readiness state (L-doc evidence count, SOP existence, governing spec existence) | ADR-008 ladder discipline | CAP-INIT-PROP-007 |
| R-INIT-PROP-012 | The proposal MUST list target version range AND mark it past-target if any cycle in the range has already shipped | INDEX 2026-05-14 finding: 5 of 6 PROPOSED past-target without re-disposition | CAP-INIT-PROP-012 |

---

## 6. EARS Specifications (Contract Level — L742 Specifications Layer)

EARS form: `WHEN {trigger}, the system SHALL {behavior}.` Each clause is testable.

### 6.1 CAP-INIT-PROP-001: Initiative-Proposal Artifact Format

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-001-01 | WHEN `/aget-propose-initiative` is invoked, the system SHALL produce a file at `planning/project-proposals/PROPOSAL_init_{snake_case_topic}.md`. | R-INIT-PROP-001, R-INIT-PROP-002 |
| CAP-INIT-PROP-001-02 | The proposal SHALL have header fields: Date, Author, Status, Proposal ID, Proposed Initiative ID, Target Versions, Theme. | R-INIT-PROP-002, R-INIT-PROP-012 |
| CAP-INIT-PROP-001-03 | The proposal SHALL contain sections (in order): Problem/Opportunity, Evidence, Proposed Scope, **Channels**, **Contributors**, **Cross-Initiative Overlap**, Streams Sketch, Size Estimate, Dependencies, ADR-008 Readiness, Decision, Traceability. | R-INIT-PROP-002, R-INIT-PROP-003, R-INIT-PROP-004, R-INIT-PROP-005 |
| CAP-INIT-PROP-001-04 | The filename SHALL be prefixed `PROPOSAL_init_` (the `init_` infix distinguishes initiative proposals from project proposals at directory-listing time). | R-INIT-PROP-002 |

### 6.2 CAP-INIT-PROP-002: Proposal ID Assignment

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-002-01 | The system SHALL assign a unique PP-### ID by reading the highest existing PP-### in `planning/project-proposals/INDEX.md` and incrementing by 1. | R-INIT-PROP-008 |
| CAP-INIT-PROP-002-02 | The PP-### sequence SHALL be shared with `/aget-propose-project` (no separate sub-sequence). | R-INIT-PROP-008 |
| CAP-INIT-PROP-002-03 | The Proposed Initiative ID SHALL follow the pattern `INIT-{UPPER-KEBAB-CASE}` and SHALL NOT collide with any existing INIT-*.md filename or any prior PROPOSAL_init_*.md. | R-INIT-PROP-003 |

### 6.3 CAP-INIT-PROP-003: Conflict Check

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-003-01 | BEFORE writing the proposal, the system SHALL search `planning/initiatives/INIT-*.md` for any existing initiative whose ID, theme, or scope-keywords overlap with the proposed topic. | R-INIT-PROP-003 |
| CAP-INIT-PROP-003-02 | BEFORE writing the proposal, the system SHALL search `planning/project-proposals/PROPOSAL_init_*.md` for any prior proposal on the same topic. | R-INIT-PROP-003 |
| CAP-INIT-PROP-003-03 | BEFORE writing the proposal, the system SHALL search `planning/initiatives/INDEX.md` "Grooming Inputs" section for any carry-forward PROPOSED initiative without a file on the same topic. | R-INIT-PROP-003 |
| CAP-INIT-PROP-003-04 | IF a conflict is detected, the system SHALL emit a warning naming the conflicting artifact AND offer the principal: (a) proceed (new proposal), (b) amend existing, (c) abort. | R-INIT-PROP-003 |

### 6.4 CAP-INIT-PROP-004: Cross-Initiative Overlap Section

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-004-01 | The proposal SHALL contain a "Cross-Initiative Overlap" section listing every existing ACTIVE or PROPOSED initiative AND classifying the relationship as: Independent, Producer/Consumer, Sibling, Fold-Candidate, or Redundant. | R-INIT-PROP-003 |
| CAP-INIT-PROP-004-02 | IF any classification is "Fold-Candidate" or "Redundant", the proposal Decision section SHALL include an explicit option to fold rather than create. | R-INIT-PROP-003, R-INIT-PROP-007 |
| CAP-INIT-PROP-004-03 | The overlap analysis SHALL cite the `docs/MEMO_initiative_overlap_clarification_*.md` precedent format established 2026-05-14. | R-INIT-PROP-003 |

### 6.5 CAP-INIT-PROP-005: Channel Registry Inclusion

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-005-01 | The proposal Channels section SHALL list every external communication or coordination surface, with fields: name, ID, purpose ∈ {sync, agents, discussion, alerts}, priority ∈ {primary, secondary, monitor}. | R-INIT-PROP-004 |
| CAP-INIT-PROP-005-02 | IF the initiative will use only the local KB (no external channels), the section SHALL contain a single row: "KB-only / — / sync / primary". | R-INIT-PROP-004 |
| CAP-INIT-PROP-005-03 | The Channels section SHALL conform to the format defined in `sops/SOP_initiative.md` §"Channels" (the SOP table shape). | R-INIT-PROP-004 |

### 6.6 CAP-INIT-PROP-006: Contributor Profile Inclusion

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-006-01 | The proposal Contributors section SHALL list every role archetype expected to supply value, with fields: role, primary value dimensions, availability. | R-INIT-PROP-005 |
| CAP-INIT-PROP-006-02 | Primary value dimensions SHALL be drawn from the L572 / #910 controlled vocabulary: artifact production, critical-path acceleration, decision quality, knowledge generation, correctness assurance, stakeholder alignment, process health. | R-INIT-PROP-005 |
| CAP-INIT-PROP-006-03 | The Contributors section SHALL include the Principal role as a row by default (any initiative without a principal contributor SHALL be flagged for review). | R-INIT-PROP-005 |

### 6.7 CAP-INIT-PROP-007: Evidence + ADR-008 Readiness

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-007-01 | The Evidence section SHALL contain ≥3 rows, each with fields: Observation, Source, Impact. | R-INIT-PROP-006 |
| CAP-INIT-PROP-007-02 | Each Evidence row's Source SHALL cite at least one of: L-doc ID, session filename, issue number, or canonical-artifact path. Source values "anecdote" / "general knowledge" / "intuition" SHALL be REJECTED. | R-INIT-PROP-006 |
| CAP-INIT-PROP-007-03 | The ADR-008 Readiness section SHALL contain a table with rows: L-doc evidence (≥2 per L436), SOP exists, Governing spec exists. Each row SHALL be marked met / gap / n/a. | R-INIT-PROP-011 |

### 6.8 CAP-INIT-PROP-008: Decision Section

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-008-01 | The Decision section SHALL contain checkboxes for: Principal reviewed, Approved (next: `/aget-create-initiative`), Deferred (rationale: ___), Rejected (rationale: ___), Fold into {existing INIT-NAME} (rationale: ___). | R-INIT-PROP-007 |
| CAP-INIT-PROP-008-02 | The Fold option SHALL be present even when no Fold-Candidate is detected in §6.4 (the option enables principal to fold despite analysis). | R-INIT-PROP-007 |
| CAP-INIT-PROP-008-03 | The Decision section SHALL NOT be checked by the skill — only the principal SHALL check decision boxes. | R-INIT-PROP-007 |

### 6.9 CAP-INIT-PROP-009: INDEX Update

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-009-01 | AFTER writing the proposal, the system SHALL append a row to `planning/project-proposals/INDEX.md` with: PP-### / name / status=PROPOSED / agent / date / proposed-INIT-ID / one-line notes. | R-INIT-PROP-009 |
| CAP-INIT-PROP-009-02 | IF `planning/project-proposals/INDEX.md` does not exist, the system SHALL create it from the SP-006-defined template before appending. | R-INIT-PROP-009 |

### 6.10 CAP-INIT-PROP-010: Proposal Lifecycle State

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-010-01 | The proposal SHALL be created with `Status: PROPOSED` and SHALL NOT be created with any other status. | R-INIT-PROP-001 |
| CAP-INIT-PROP-010-02 | The proposal Status field SHALL transition only via principal action: PROPOSED → APPROVED (via `/aget-create-initiative`), PROPOSED → DEFERRED (Decide gate), PROPOSED → REJECTED (Decide gate). | R-INIT-PROP-001 |

### 6.11 CAP-INIT-PROP-011: Separation of Concerns

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-011-01 | `/aget-propose-initiative` SHALL NOT create a file at `planning/initiatives/INIT-*.md`. | R-INIT-PROP-010 |
| CAP-INIT-PROP-011-02 | IF a principal asks `/aget-propose-initiative` to also scaffold the manifest, the system SHALL refuse and point to `/aget-create-initiative` (or its proposal, currently `PROPOSAL_aget-create-initiative.md`, if the create-skill is not yet implemented). | R-INIT-PROP-010 |

### 6.12 CAP-INIT-PROP-012: Target Version Currency

| ID | EARS Clause | Implements |
|----|-------------|------------|
| CAP-INIT-PROP-012-01 | The Target Versions field SHALL be a range like `v3.18 – v3.20` referencing AGET framework version numbers. | R-INIT-PROP-012 |
| CAP-INIT-PROP-012-02 | IF the start version is ≤ the currently-released framework version, the proposal SHALL be flagged "past-start" and the start version SHALL be adjusted forward before final filing. | R-INIT-PROP-012 |
| CAP-INIT-PROP-012-03 | The system SHALL read the current released version from `.aget/version.json` (field `aget_version`). | R-INIT-PROP-012 |

---

## 7. Verification Tests (V-INIT-PROP-*)

Each V-test is mechanically executable against a candidate proposal file.

### V-INIT-PROP-001: Filename + path conformance
```bash
# Given a candidate proposal file path $FILE:
test "$(basename "$FILE")" =~ ^PROPOSAL_init_[a-z0-9_]+\.md$ \
  && dirname "$FILE" -ef planning/project-proposals
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-001-01, 001-04.

### V-INIT-PROP-002: Required sections present
```bash
for section in "## Problem" "## Evidence" "## Proposed Scope" "## Channels" "## Contributors" "## Cross-Initiative Overlap" "## Streams Sketch" "## Size Estimate" "## Dependencies" "## ADR-008 Readiness" "## Decision" "## Traceability"; do
  grep -qF "$section" "$FILE" || { echo "MISSING: $section"; exit 1; }
done
```
**Expected**: all sections found, exit 0. **Verifies**: CAP-INIT-PROP-001-03.

### V-INIT-PROP-003: PP-### unique + monotonic (split-mode per v1.1.1)

**Creation-mode** (verifies at file-creation time that PP-### was monotonically assigned):
```bash
PP=$(grep -oE '^\*\*Proposal ID\*\*: PP-[0-9]+' "$FILE" | grep -oE '[0-9]+')
LAST=$(grep -oE 'PP-[0-9]+' planning/project-proposals/INDEX.md | grep -oE '[0-9]+' | sort -n | tail -1)
test "$PP" -gt "$LAST" || test "$PP" -eq $((LAST + 1))
```

**Revalidation-mode** (verifies PP-### exists in INDEX exactly once; for re-running V-tests against existing proposals):
```bash
PP=$(grep -oE '^\*\*Proposal ID\*\*: PP-[0-9]+' "$FILE" | grep -oE '[0-9]+')
COUNT=$(grep -oE "PP-0*${PP}\b" planning/project-proposals/INDEX.md | wc -l)
test "$COUNT" -eq 1
```

**Mode selection**: runners SHALL try creation-mode first; if it fails, SHALL fall through to revalidation-mode. A proposal that passes either mode satisfies CAP-INIT-PROP-002-01 (the monotonicity invariant holds either at creation or in INDEX presence).

**Expected**: exit 0 in at least one mode. **Verifies**: CAP-INIT-PROP-002-01.

**Discovery**: `planning/triad_findings.jsonl` line 36 (Gate 2 Auditor finding 2026-05-14) — original single-mode V-test failed PP-027 on re-validation because PP-028 was filed later in the shared sequence; creation-time-only semantics not stated in v1.0.0 / v1.0.1 / v1.1.0.

### V-INIT-PROP-004: Proposed INIT-ID uniqueness
```bash
INIT=$(grep -oE 'INIT-[A-Z][A-Z0-9-]+' "$FILE" | head -1)
test -z "$(ls planning/initiatives/${INIT}.md 2>/dev/null)" \
  && test "$(grep -l "$INIT" planning/project-proposals/PROPOSAL_init_*.md 2>/dev/null | wc -l)" -le 1
```
**Expected**: exit 0 (only this proposal references the ID). **Verifies**: CAP-INIT-PROP-002-03.

### V-INIT-PROP-005: Evidence row count ≥ 3
```bash
awk '/^## Evidence/,/^## /' "$FILE" | grep -cE '^\|.*\|.*\|.*\|$' | awk '{exit ($1 >= 4 ? 0 : 1)}'
# (4 = 3 data rows + 1 header row)
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-007-01.

### V-INIT-PROP-006: Evidence Source citations are typed
```bash
awk '/^## Evidence/,/^## /' "$FILE" \
  | grep -E '^\|.*\|.*\|' \
  | tail -n +2 \
  | awk -F'|' '{print $3}' \
  | grep -ivE 'L[0-9]+|gh#[0-9]+|session_|aget/|\.aget/|planning/|sops/|governance/|docs/|#[0-9]+' \
  && exit 1 || exit 0
# Pass if NO row's Source column lacks a typed citation
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-007-02.

### V-INIT-PROP-007: Channels section non-empty
```bash
awk '/^## Channels/,/^## /' "$FILE" | grep -cE '^\|.*\|.*\|.*\|.*\|$' | awk '{exit ($1 >= 2 ? 0 : 1)}'
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-005-01, 005-02.

### V-INIT-PROP-008: Contributors section includes Principal
```bash
awk '/^## Contributors/,/^## /' "$FILE" | grep -q "Principal"
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-006-03.

### V-INIT-PROP-009: Cross-Initiative Overlap classifies every existing initiative
```bash
EXPECTED=$(ls planning/initiatives/INIT-*.md 2>/dev/null | wc -l)
FOUND=$(awk '/^## Cross-Initiative Overlap/,/^## /' "$FILE" | grep -cE '^\| INIT-[A-Z]')
test "$FOUND" -ge "$EXPECTED"
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-004-01.

### V-INIT-PROP-010: Decision section has all 5 options
```bash
for opt in "Principal reviewed" "Approved" "Deferred" "Rejected" "Fold into"; do
  awk '/^## Decision/,/^## /' "$FILE" | grep -qF "$opt" || { echo "MISSING decision option: $opt"; exit 1; }
done
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-008-01, 008-02.

### V-INIT-PROP-011: Status is PROPOSED at creation
```bash
grep -qE '^\*\*Status\*\*: PROPOSED' "$FILE"
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-010-01.

### V-INIT-PROP-012: INDEX has a matching row
```bash
PP=$(grep -oE 'PP-[0-9]+' "$FILE" | head -1)
grep -q "$PP" planning/project-proposals/INDEX.md
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-009-01.

### V-INIT-PROP-013: No INIT-*.md was authored by the skill
```bash
# Negative test — run after /aget-propose-initiative invocation, before any /aget-create-initiative invocation:
git diff --name-only --staged planning/initiatives/INIT-*.md 2>/dev/null | wc -l | awk '{exit ($1 == 0 ? 0 : 1)}'
```
**Expected**: exit 0 (no INIT-*.md in staged changes). **Verifies**: CAP-INIT-PROP-011-01.

### V-INIT-PROP-014: Target Versions not past-start
```bash
START=$(grep -oE 'Target Versions.*v([0-9]+\.[0-9]+)' "$FILE" | grep -oE 'v[0-9]+\.[0-9]+' | head -1 | tr -d 'v')
CURRENT=$(python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])" | grep -oE '^[0-9]+\.[0-9]+')
python3 -c "import sys; sys.exit(0 if tuple(map(int, '$START'.split('.'))) > tuple(map(int, '$CURRENT'.split('.'))) else 1)"
```
**Expected**: exit 0. **Verifies**: CAP-INIT-PROP-012-02.

---

## 8. Coherence Notes (Pre-Review Cross-Check)

| Cross-reference | Status |
|---|---|
| **vs. `sops/SOP_initiative.md` v1.2.0** | Coherent. This spec lifts the SOP §"Channels" and §"Contributors" table shapes (Steps 2.5 + 3.5) to contract level. The SOP retains procedural canon for manifest creation. |
| **vs. `aget/specs/AGET_PROJECT_PLAN_SPEC.md` v1.2.3** | Coherent. Spec format mirrors PROJECT_PLAN_SPEC structure (Abstract / Motivation / Scope / Vocabulary / Requirements / V-tests). Verb-pair `/aget-propose-X` + `/aget-create-X` maintained. |
| **vs. `aget/specs/AGET_ISSUE_GOVERNANCE_SPEC.md`** | Coherent. The "INDEX update" pattern (CAP-INIT-PROP-009) mirrors the issue-governance principle of authoritative registries. |
| **vs. existing 11 INIT-*.md files** | Coherent — no field this spec defines for proposals conflicts with manifest fields. Manifest format is OUT OF SCOPE for v0.1. (Verified: `ls planning/initiatives/INIT-*.md \| wc -l` = 11 on 2026-05-14.) |
| **vs. existing 7 PROPOSAL_init_*.md files (PP-014, 016, 017, 018, 019, 020, 027)** | **Non-coherent by design and empirically confirmed** — `grep -c` over all 7 files shows 0/7 contain `## Channels`, 0/7 contain `## Contributors`, 0/7 contain `## Cross-Initiative Overlap`. Per L867, this spec creates the obligation; pre-existing proposals are grandfathered (status-quo) and SHALL be enriched at next-Decide if revived. Recommend filing this as a known migration debt note in the v0.2 spec revision. |
| **vs. L760 (Initiative as Scope Modifier)** | Coherent. Vocabulary explicitly cites L760; Initiative defined as "scope modifier per L760, not first-class entity". |
| **vs. INDEX.md status taxonomy drift (G4 Decide open)** | Sidestepped. v0.1 defines only **proposal** status (PROPOSED/APPROVED/DEFERRED/REJECTED) — disjoint from the manifest status drift. v0.2 SHALL address manifest status after G4 resolution. |
| **vs. `/aget-propose-project` (sibling)** | Coherent. Same proposal-stage pattern; ID sequence shared (CAP-INIT-PROP-002-02); template differences are additive (3 new mandatory sections: Channels, Contributors, Cross-Initiative Overlap). |
| **vs. `/aget-check-initiative` (sibling)** | Coherent. Read-only checker can validate proposals against this spec's V-tests in addition to manifests. Spec gh#1325 unresolved channel-precedence does not block this spec. |

---

## 9. Resolved Decisions (Principal GO 2026-05-14)

| # | Decision | Resolution |
|---|----------|------------|
| Q1 | Scope at v1.0.0 release | **v0.1 → v1.0.0 ships standalone (proposal stage only)**. Manifest-stage capabilities CAP-INIT-MFST-* deferred to v2.0.0. |
| Q2 | Filename prefix | **`PROPOSAL_init_*`** (lowercase `init_` infix). Matches 7 existing proposals; lowercase chosen for grep-ability and visual contrast with INIT-* manifest filename. |
| Q3 | Enforcement level | **Advisory** (ADR-008 Layer 1). Matches sibling `/aget-propose-project`. Promotion to Strict (D71) is deferred until `/aget-create-initiative` exists as the only path to INIT-*.md. |
| Q4 | Grandfather policy | **Grandfather** the 7 existing pre-spec proposals (PP-014, 016, 017, 018, 019, 020, 027). Pre-existing proposals SHALL be enriched at next-Decide if revived; no retroactive re-authoring. Documented as known migration debt in v2.0.0 scope. |
| Q5 | PP-### sequence | **Shared** with `/aget-propose-project` (codified in CAP-INIT-PROP-002-02). |
| Q6 | Canonical promotion path | **Promote on GO**. Commit local (any day per L735); push to public repo on Saturday (push window). |

---

## 10. Traceability

| Link | Reference |
|------|-----------|
| Governing model | L760 (Initiative as Scope Modifier) |
| Anti-pattern source | L867 (Coherence-Directed Investment as enhance-Verb-Family) |
| Procedural canon | `sops/SOP_initiative.md` v1.2.0 |
| Sibling spec (structural mirror) | `aget/specs/AGET_PROJECT_PLAN_SPEC.md` v1.2.3 |
| Sibling skill (verb-pair, propose side) | `/aget-propose-project` (`.claude/skills/aget-propose-project/SKILL.md`) |
| Sibling skill (verb-pair, create side, not yet implemented) | `planning/skill-proposals/PROPOSAL_aget-create-initiative.md` (PROPOSED 2026-04-19) |
| Sibling skill (read-only) | `/aget-check-initiative` (SKILL.md; spec gaps tracked at gh#1325) |
| Channel registry pattern | gh#916 |
| Contributor profile pattern | gh#910 + L572 |
| Relevance rubric (Decision input) | gh#886 |
| Decorative-reference precedent | gh#1193 (INIT-PRINCIPLED-EXECUTION) |
| 2026-04-19 friction event | INIT-REQ-SPEC-TEST-DEFINED direct-Write incident |
| 2026-05-14 status taxonomy finding | `docs/FINDING_initiative_status_taxonomy_2026-05-14.md` |
| 2026-05-14 overlap memo template | `docs/MEMO_initiative_overlap_clarification_2026-05-14.md` |
| Two-Level Model | L742 (Requirements human-level, Specifications contract-level) |
| Evidence-driven design | L289, ADR-008 |
| Substantial Change Protocol | CLAUDE.md §"Substantial Change Protocol" |
| Verb registry | `aget/ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md` v3.16.0 (canonical post-PP-021 G5.6 promotion, 2026-05-16) — `propose` is verb #18 (Governance category, approved). Verified 2026-05-14. |
| **Governance-cluster grounding** (added v1.1.0) | C404 InitiativeCoverageCriterion (graduation threshold ≥2 plans OR ≥5 issues OR ≥3 cycles), C405 DemandDrivenInitiativeGraduation (chartering principle), C406 StrategicAlignmentFramework (mission↔capability↔initiative bridge — overlap classification), C407 PortfolioProjectStreamTriStratum (Stream is third stratum), C408 PortfolioTheater (alt: Initiative Theater — anti-pattern parent of Decorative_Initiative_Reference) |
| **Self-application gap (named pattern)** (added v1.1.0) | C544 MetaSpecificationGap — formal vocabulary exists but contract layer doesn't bind; recursive instance: this spec was the first canonical spec landed after INIT-ONTOLOGY-SPEC-BINDING charter (gh#1241) and v1.0.1 itself failed to bind, requiring v1.1.0 patch |
| **Vocabulary discipline** (added v1.1.0) | C547 VocabularyFirstNamingDiscipline — naming SHALL check ontology before coining; Project_Template_Reuse anti-pattern is its failure mode |
| **Per-agent grounding context** (added v1.1.0) | `docs/FINDING_per_agent_ontology_grounding_gap_2026-05-14.md` — names the structural gap surfaced by 2026-05-14 PM principal probe; this v1.1.0 patch is Evidence 4 of that finding |
| **Cross-initiative cluster** (added v1.1.0) | `docs/MEMO_ontology_grounding_initiative_overlap_2026-05-14.md` — 21-pair classification (CAP-INIT-PROP-004 self-applied to 7-artifact ontology-grounding cluster); this spec sits at Producer position relative to INIT-REQ-SPEC-TEST-DEFINED + PP-017 |

---

## 11. Status

**Active** at v1.0.0. Principal GO recorded 2026-05-14.

### Downstream Work Sequenced

| # | Work | Status | Owner |
|---|------|--------|-------|
| 1 | Author `/aget-propose-initiative` SKILL.md against CAP-INIT-PROP-001..012 | Pending GO on PROJECT_PLAN | private-aget-framework-AGET |
| 2 | File implementation PROJECT_PLAN via `/aget-create-project` (skill scaffold, V-test runner, dogfood, retro gates) | Pending | private-aget-framework-AGET |
| 3 | Build V-test runner for V-INIT-PROP-001..014 (mechanical conformance) | Pending | private-aget-framework-AGET |
| 4 | Dogfood: re-validate the spec by invoking `/aget-propose-initiative` on the issue-backlog stewardship topic that opened this session | Pending | private-aget-framework-AGET |

### v2.0.0 Scope (Manifest-Stage)

- Manifest-stage capabilities (CAP-INIT-MFST-*)
- `/aget-create-initiative` contract (the verb-pair create-side)
- Status taxonomy reconciliation after G4 Decide (SOP/INDEX/wild drift)
- Enrichment policy for the 7 grandfathered proposals

---

*AGET_INITIATIVE_SPEC v1.1.1*
*Authored under principle-triad: spec+verify-first, coherence-next, evidence-driven (2026-05-14)*
*v1.1.0 SKOS uplift via PP-028 — first-instance dogfood of INIT-ONTOLOGY-SPEC-BINDING discipline (2026-05-14 PM)*
*v1.1.1 V-003 split — creation-mode vs revalidation-mode per Gate 2 Auditor finding (2026-05-14 PM)*
