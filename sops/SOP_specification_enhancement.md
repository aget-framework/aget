# SOP: Specification Enhancement

**Implements**: CAP-SOP-001 (SOP Structure), CAP-SOP-002 (Vocabulary Compliance), CAP-SOP-004 (Traceability)
**Pain Point**: L622 (Specification Enhancement Lifecycle), L546 (Cultural vs Structural Enforcement)
**See**: AGET_SOP_SPEC.md v1.1.0, L434 (Specification Enhancement Roadmap)
**Pattern**: L436 (PROJECT_PLAN to SOP Graduation Pattern)

---

**Version**: 1.0.0
**Created**: 2026-02-28
**Owner**: aget-framework
**Category**: Governance
**Scope Classification**: Framework_Sop (target: `aget/sops/`)
**Related**: L622, L623, L434, L436, L546, L557, L560, ADR-008, SOP_sop_creation.md, SOP_specification_consolidation.md

---

## Purpose

Standard operating procedure for enhancing AGET specifications — creating, updating, wiring, and validating specs across the framework.

**Problem Solved**: Without this SOP:
- Each agent reinvents the spec enhancement process independently (5 plans, 3 agents, same 11-phase process discovered independently — L622)
- Process knowledge is hard-won and lost between sessions (Supervisor Wave 1 required 5 plan revisions)
- Cultural enforcement fails under time pressure (L546)
- Bootstrapping paradox (L560) and Decorative Spec Basis anti-patterns go undetected

**ADR-008 Position**: This SOP is the **Advisory** layer (step 1 of Advisory → Strict → Generator). The `/aget-enhance-spec` skill (Generator) will automate these procedures.

---

## Scope

### When to Use This SOP

| Trigger | Example |
|---------|---------|
| **New spec needed** | Gap identified; no spec exists for a capability area |
| **Spec version bump** | Adding requirements to existing spec |
| **Cross-reference wiring** | Connecting specs to L-docs, V-tests, or other specs |
| **Spec consolidation** | Merging related specs (see also SOP_specification_consolidation.md) |
| **Spec deprecation** | Marking spec as superseded |
| **Post-release remediation** | Fixing spec issues discovered after release |

### When NOT to Use This SOP

| Situation | Alternative |
|-----------|-------------|
| One-time document edit (typo, formatting) | Direct edit |
| L-doc creation | `/aget-record-lesson` |
| SOP creation | SOP_sop_creation.md |
| Template-only changes (no spec change) | SOP_template_lifecycle.md |
| Spec consolidation only (no new content) | SOP_specification_consolidation.md (subset) |

---

## Enhancement Category Taxonomy

Classify each enhancement before starting. The category determines which phases are required.

| Category | Description | Required Phases | Source |
|----------|-------------|:---------------:|--------|
| **NEW** | Create spec from scratch | 0-6 (all core) | L434 |
| **UPDATE** | Version bump with added/changed requirements | 0-6 | L434 |
| **ADD-REQ** | Add requirements to existing spec without version bump | 0-6 | L434 |
| **WIRE** | Add cross-references between specs, L-docs, V-tests | 0, 1, 5, 6 | L557 |
| **CONSOLIDATE** | Merge related specs or absorb content | 0-6 + SOP_specification_consolidation | L434 |
| **DEPRECATE** | Mark spec as superseded | 0, 1, 3, 6 | SOP_pre_release_research |

---

## Procedure: Core Authoring Phases (0-6)

*These phases apply to all Enhancement_Categories. Phases are sequential; each phase's exit criteria must be met before proceeding.*

### Phase 0: Trigger & Diagnosis

**Objective**: Identify the specification gap and gather evidence.

**Checklist**:
- [ ] Identify the spec gap — what's missing, wrong, or outdated
- [ ] Classify the Enhancement_Category (NEW, UPDATE, ADD-REQ, WIRE, CONSOLIDATE, DEPRECATE)
- [ ] Root cause analysis (5-whys where applicable)
- [ ] Gather evidence:
  - [ ] Related L-docs (search `.aget/evolution/`)
  - [ ] Related specs (search `specs/`, `aget/specs/`)
  - [ ] Fleet data or session findings
- [ ] Document evidence in PROJECT_PLAN or working document

**Governance Classification** (L624):

| Scope | Category | Governance Required |
|-------|----------|:-------------------:|
| Public framework spec | UPDATE, NEW | PROJECT_PLAN required before proceeding |
| Public framework spec | ADD-REQ, WIRE | Enhancement_Decision_Log (skill output) |
| Private agent spec | Any | Enhancement_Decision_Log (skill output) |
| Fleet-deployed spec | Any | PROJECT_PLAN + tracking issue |

- [ ] Determine governance level from table above
- [ ] If PROJECT_PLAN required: create before proceeding past Phase 0

**Exit Criteria**: Enhancement_Category assigned. Evidence documented. Gap clearly stated. Governance level determined.

---

### Phase 1: Governing Spec Verification

**Objective**: Read the governing spec(s) before modifying anything. Verify cross-reference targets are accurate.

**Checklist**:
- [ ] Identify governing spec(s) for artifacts being modified
- [ ] Read each governing spec — cite specific requirements (CAP-xxx-nnn)
- [ ] Verify cross-reference targets in governing spec are not stale
- [ ] If stale targets found: remediate BEFORE proceeding (see Phase 5a)
- [ ] If no governing spec exists: document as finding; proceed with caution

**Exit Criteria**: Governing spec(s) read and cited. Cross-reference targets verified as current.

**Anti-Pattern**: *Decorative Spec Basis* — declaring a spec basis without actually reading it or deriving deliverables from it. Detection: Spec Basis section exists but no CAP-xxx citations appear in deliverables.

---

### Phase 2: Census & Classification

**Objective**: Inventory all artifacts that need enhancement. Classify and prioritize.

**Checklist**:
- [ ] Enumerate all specs/artifacts in scope
- [ ] For each, classify the Enhancement_Category
- [ ] Record current version and status of each
- [ ] Identify dependency order (which specs reference which)
- [ ] Prioritize by: dependency order first, then impact

**Output**: Census table with columns: Artifact | Current Version | Enhancement_Category | Dependencies | Priority

**Exit Criteria**: All artifacts inventoried. Dependencies mapped. Priority assigned.

---

### Phase 3: Draft/Update Spec

**Objective**: Write or update the specification content.

**Checklist**:
- [ ] Update spec header (version, status, metadata)
- [ ] Write/update requirements in EARS patterns:
  - Ubiquitous: `The SYSTEM shall...`
  - Conditional: `IF condition THEN the SYSTEM shall...`
  - Event-driven: `WHEN event THEN the SYSTEM shall...`
  - Optional: `WHERE condition, the SYSTEM should...`
  - Prohibited: `The SYSTEM shall NOT...`
  - Unwanted: `artifact shall NOT...`
- [ ] Include vocabulary section (SKOS format) if new terms introduced
- [ ] Include theoretical basis section if applicable
- [ ] Each requirement has unique ID: R-{DOMAIN}-{NNN}
- [ ] "Codify existing behavior" approach where applicable (fastest — see Pro-Core evidence in L622)

**Exit Criteria**: Spec content written. All requirements have IDs and EARS patterns.

---

### Phase 4: Structural Validation

**Objective**: Verify spec meets structural requirements.

**Checklist**:
- [ ] Required sections present (per AGET_SPEC_FORMAT)
- [ ] Naming conventions correct (per AGET_FILE_NAMING_CONVENTIONS)
- [ ] EARS pattern compliance for all requirements
- [ ] Version number updated correctly (semantic versioning)
- [ ] Run structural validators if available (`validate_spec_compliance.py`)

**Exit Criteria**: Spec passes structural validation. No format errors.

**Note**: Structural validation alone is insufficient — it catches format issues but not semantic issues. Self-compliance check (Phase 6) is also required.

---

### Phase 5: Cross-Reference Wiring

**Objective**: Connect spec to related artifacts. Ensure bidirectional traceability.

#### Phase 5a: Stale Artifact Remediation (prerequisite)

Before wiring, verify targets are current:
- [ ] Check each cross-reference target exists
- [ ] Check each target's version/status is current
- [ ] If stale: update target first, then wire

#### Phase 5b: Primary Cross-Wiring

- [ ] Link each requirement to evidence L-doc(s) — why does this requirement exist?
- [ ] Link each requirement to V-test — how is this requirement enforced?
- [ ] Link spec to related specs (broader/narrower/related)
- [ ] Update AGET identity/config references if applicable
- [ ] Update index files (INDEX.md, relevant registries)

#### Phase 5c: Bidirectional Verification

- [ ] For each outgoing reference: verify target acknowledges this spec
- [ ] For each incoming reference: verify this spec acknowledges source
- [ ] Run cross-reference validator if available

**Exit Criteria**: All requirements trace to evidence and enforcement. Bidirectional references verified.

---

### Phase 6: Self-Compliance Check

**Objective**: Verify the enhancement itself complies with its own specs and the specs it modifies.

**Checklist**:
- [ ] **Bootstrapping paradox check** (L560): Does the plan/work comply with the lessons it remediates?
- [ ] **Spec self-compliance**: Does the spec comply with its own requirements?
- [ ] **Format compliance**: Does the enhancement follow the governing spec format?
- [ ] **Vocabulary compliance** (CAP-SOP-002 equivalent for specs): Are all terms controlled?

**Exit Criteria**: Self-compliance confirmed. No bootstrapping paradox detected.

**Anti-Pattern**: *Certainty Bias* (L555) — skipping self-compliance because "we know what we're doing." Always run this check, even for small changes.

---

## Procedure: Deployment Phases (7-10)

*These phases are **conditional** — triggered only for Framework-scoped specs that need template or fleet propagation (per CAP-SOP-005).*

*IF Enhancement_Scope is Framework THEN execute phases 7-10.*
*IF Enhancement_Scope is Agent THEN skip to Closure.*

### Phase 7: Template Enforcement

**Objective**: Propagate spec requirements into template slots.

**Checklist**:
- [ ] Identify template files affected by spec changes
- [ ] Update template slots with new/changed spec content
- [ ] Verify template structure matches spec (L554: absence of slot guarantees absence of content)
- [ ] Validate template structure

**Exit Criteria**: Templates reflect spec. No missing slots.

---

### Phase 8: Tooling Alignment

**Objective**: Update validators, scripts, and automation to enforce new/changed specs.

*IF automated enforcement exists for this spec THEN execute Phase 8.*

**Checklist**:
- [ ] Identify validators/scripts that enforce this spec
- [ ] Update validator logic to match new requirements
- [ ] Update test suites
- [ ] Verify tooling catches violations (not just passes — L433 Validator Enforcement Theater)
- [ ] Run full test suite

**Exit Criteria**: Tooling aligned with spec. Validators catch violations, not just pass.

---

### Phase 9: Fleet Propagation

**Objective**: Deploy spec changes across fleet agents.

**Checklist**:
- [ ] Create upgrade handoff artifact (R-REL-019, `handoffs/RELEASE_HANDOFF_vX.Y.Z.md`)
- [ ] Pilot with subset of agents (recommended: 2-3 before fleet-wide)
- [ ] Monitor for regression
- [ ] Track upgrade completion (pilot tracking table)
- [ ] Notify supervisor of new version availability

**Exit Criteria**: Fleet upgraded. Pilot tracking complete. Supervisor notified.

---

### Phase 10: Post-Deployment Verification

**Objective**: Verify specs are correctly deployed and enforced in production.

**Checklist**:
- [ ] Run contract tests across fleet
- [ ] Verify spec compliance in deployed agents
- [ ] Capture lessons learned (L-doc if novel pattern discovered)
- [ ] Update L-docs with deployment findings
- [ ] Close PROJECT_PLAN if applicable

**Exit Criteria**: Fleet compliance verified. Lessons captured.

---

## Anti-Patterns

| Anti-Pattern | Detection | Consequence | Prevention |
|--------------|-----------|-------------|------------|
| **Decorative Spec Basis** | Spec Basis declared but no CAP citations in deliverables | 2nd-order enforcement failure — spec exists but doesn't govern | Phase 1: cite specific requirements |
| **Bootstrapping Paradox** (L560) | Plan/work violates the lessons it remediates | Produced artifacts contain the flaws they're meant to fix | Phase 6: self-compliance check |
| **Certainty Bias** (L555) | Self-compliance check skipped ("we know what we're doing") | Undetected violations accumulate | Always run Phase 6 |
| **Ephemeral Process Model** | Process knowledge exists only in conversation/memory | Lost between sessions; must be re-derived | Document in L-doc (Phase 0) |
| **Memory-Based Assertions** (L611) | Claims about spec state asserted from memory, not file reads | Stale classifications; wrong decisions | Phase 1: read actual files |
| **ADR-008 Progression Skip** | Jumping to Generator (skill) without Advisory (SOP) or Strict (spec) | Missing governance layers; skill operates without spec | Follow L622 lifecycle |
| **Sample Bias** | Process model derived from small sample | May miss edge cases from other agents | Document sample size; check for counter-evidence |
| **Validator Enforcement Theater** (L433) | Validators exist but don't catch actual violations | False confidence in compliance | Phase 8: verify validators catch violations, not just pass |

---

## Quick Reference

### Minimum Viable Enhancement

For simple changes (ADD-REQ, WIRE):
1. Phase 0: Identify gap, classify category
2. Phase 1: Read governing spec, cite requirements
3. Phase 3: Write/update requirement
4. Phase 5b: Wire cross-references
5. Phase 6: Self-compliance check

### Full Enhancement

For NEW or UPDATE:
1. Phases 0-6: All core authoring phases
2. Phases 7-10: If Framework-scoped

### Decision Tree

```
Enhancement needed?
    │
    ├── Classify: NEW / UPDATE / ADD-REQ / WIRE / CONSOLIDATE / DEPRECATE
    │
    ├── Read governing spec (Phase 1)
    │   └── Spec Basis citations in deliverables?
    │       ├── No → Decorative Spec Basis — STOP and fix
    │       └── Yes → Continue
    │
    ├── Census artifacts (Phase 2)
    │
    ├── Draft/update spec (Phase 3) + validate (Phase 4)
    │
    ├── Wire cross-references (Phase 5)
    │   └── Stale targets?
    │       ├── Yes → Remediate first (Phase 5a)
    │       └── No → Wire (Phase 5b) + verify (Phase 5c)
    │
    ├── Self-compliance check (Phase 6)
    │   └── Bootstrapping paradox?
    │       ├── Yes → Fix compliance, re-check
    │       └── No → Continue
    │
    └── Framework-scoped?
        ├── Yes → Phases 7-10 (template, tooling, fleet, verify)
        └── No → Close
```

---

## Examples

### Example: Good Enhancement (UPDATE)

```
Trigger: L568 identified Framework Artifact Scope specification gap
Category: UPDATE (add CAP-SOP-005 to AGET_SOP_SPEC)

Phase 0: Evidence from L568 + 3 related L-docs
Phase 1: Read AGET_SOP_SPEC v1.0.0, cited CAP-SOP-001 through CAP-SOP-004
Phase 2: Census — 1 spec, 0 dependencies
Phase 3: Wrote CAP-SOP-005 (5 requirements) in EARS format
Phase 4: Structural validation passed
Phase 5: Wired L568 → CAP-SOP-005, V-test defined
Phase 6: Self-compliance — SOP_sop_creation used this spec ✓

Result: AGET_SOP_SPEC v1.1.0, clean merge
```

### Example: Bad Enhancement (Anti-Pattern)

```
Trigger: "We need a spec for X"
Category: NEW

Phase 0: Skipped ("obvious need")
Phase 1: Declared "based on AGET_SPEC_FORMAT" but didn't read it
Phase 3: Wrote spec without EARS patterns
Phase 6: Skipped ("we know what we're doing")

Result: Spec with wrong format, no requirement IDs, no V-tests.
Anti-patterns hit: Certainty Bias, Decorative Spec Basis, Memory-Based Assertions
```

---

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Phase completion | % of phases executed per enhancement | 100% for required phases |
| Self-compliance pass rate | % of enhancements passing Phase 6 on first check | > 80% |
| Cross-reference completeness | % of requirements with both evidence and V-test links | 100% |
| Plan revisions before first gate pass | Count of plan version bumps | <= 2 (down from 5) |
| Anti-pattern detection rate | % of anti-patterns caught before merge | > 90% |

---

## Graduation History

```yaml
graduation:
  source_plans:
    - "PROJECT_PLAN_spec_enhancement_wave1 (supervisor, COMPLETE)"
    - "PROJECT_PLAN_spec_deployment_wave2 (supervisor, In_Progress)"
    - "PROJECT_PLAN_template_v11_compliance (supervisor, COMPLETE)"
    - "PROJECT_PLAN_ldoc_spec_audit (pro-core, COMPLETE)"
    - "PROJECT_PLAN_governance_doc_specification_enhancements (framework, Phase -1)"
  execution_count: 5
  l436_threshold: "2+ (met: 5 executions)"
  trigger: "L622 — 11-phase process model converged from 5 independent plans"
  research:
    plans_analyzed: 12 (5 primary + 7 counter-evidence check)
    agents_represented: 3 of 32 (9%)
    l_docs_mined: 9 (L434, L436, L546, L554, L555, L557, L560, L474, L622)
    sessions: "session_2026-02-28_1501, session_2026-02-28_1528"
  validation: "Self-validates — this SOP follows its own Phase 0-6 procedures"
```

---

## References

- L622: Specification Enhancement Lifecycle — 11-Phase Process Model
- L623: Meta-Governance Gap — Governance Principles Below Their Prescribed Level
- L434: Specification Enhancement Roadmap (9-issue taxonomy)
- L436: PROJECT_PLAN to SOP Graduation Pattern
- L546: Cultural vs Structural Enforcement
- L557: Spec-to-Enforcement Traceability
- L560: Bootstrapping Paradox
- L555: Certainty-Bias Anti-Pattern
- L554: Universal Rollback Gap
- L433: Validator Enforcement Theater Gap
- L611: Stale VERSION_SCOPE Classifications
- ADR-008: Advisory → Strict → Generator
- AGET_SOP_SPEC.md v1.1.0 (governing spec)
- SOP_sop_creation.md v1.0.0 (creation procedure)
- SOP_specification_consolidation.md (CONSOLIDATE category subset)
- SOP_pre_release_research.md (classification taxonomy)
- PROJECT_PLAN_aget_enhance_spec_skill_v1.0.md (parent project)

---

*SOP_specification_enhancement.md v1.0.0 — "Five plans, three agents, one process. Now documented."*
*Created: 2026-02-28*
*Owner: aget-framework*
*Scope: Framework_Sop (publish to aget/sops/ at release)*
