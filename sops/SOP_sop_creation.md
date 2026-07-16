# SOP: SOP Creation

**Implements**: CAP-SOP-001 (SOP Structure), CAP-SOP-002 (Vocabulary Compliance)
**Pain Point**: L436 (PROJECT_PLAN to SOP Graduation Pattern)
**See**: AGET_SOP_SPEC.md, L524 (Pattern Consolidation)
**Pattern**: L376 (Checklist-Driven Gate Design)

---

**Version**: 1.1.0
**Status**: Active
**Created**: 2026-01-16
**Updated**: 2026-07-16
**Owner**: private-aget-framework-AGET
**Category**: Governance
**Related**: AGET_SOP_SPEC.md, L436, L524, L376

---

## Purpose

Standard operating procedure for creating SOPs within the AGET framework. This meta-SOP ensures:
- SOPs are grounded in research (not created ad-hoc)
- SOPs meet graduation criteria before formalization (L436)
- SOPs conform to AGET_SOP_SPEC structure
- SOPs include proper traceability and validation

**Problem Solved**: Without a formal SOP creation process:
- SOPs are created prematurely (before pattern is proven)
- SOPs lack research foundation
- SOPs miss required sections
- SOPs have inconsistent quality

---

## Scope

### When to Use This SOP

| Trigger | Example |
|---------|---------|
| **Pattern proven** | Procedure executed 2+ times successfully |
| **Consolidation needed** | 3+ L-docs document related patterns (L524) |
| **Enhancement request** | Formal request for documented procedure |
| **Governance gap** | Observed inconsistency needing standardization |

### When NOT to Use This SOP

| Situation | Alternative |
|-----------|-------------|
| One-time procedure | Use PROJECT_PLAN instead |
| Ad-hoc task | Execute directly |
| Pattern not yet proven | Document as L-doc first |
| Simple checklist only | Use CHECKLIST_*.md format |

---

## 4-Phase SOP Creation Process

```
Phase 1: Research Investment
    │
    ↓ [Research Complete]
    │
Phase 2: Graduation Validation (L436)
    │
    ↓ [Graduation Criteria Met]
    │
Phase 3: SOP Creation (AGET_SOP_SPEC)
    │
    ↓ [SOP Authored]
    │
Phase 4: Validation
    │
    ↓ [SOP Complete]
```

---

## Phase 1: Research Investment

**Objective**: Gather evidence before creating SOP.

### Research Investment Checklist

- [ ] **Trigger Identification**
  - [ ] What pattern or problem initiates this SOP?
  - [ ] L-doc(s) documenting the pattern: ___
  - [ ] Enhancement request(s) if any: ___

- [ ] **L-doc Mining**
  - [ ] Searched `.aget/evolution/` for related learnings
  - [ ] Keywords used: ___
  - [ ] L-docs found: ___

- [ ] **Existing SOP Audit**
  - [ ] Checked `sops/` for similar SOPs
  - [ ] Similar SOPs found: ___
  - [ ] Differentiation from existing: ___

- [ ] **Consolidation Check (L524)**
  - [ ] Count of related L-docs: ___
  - [ ] If 3+, consolidation opportunity: Yes/No

- [ ] **Research Documentation**
  - [ ] Findings documented in PROJECT_PLAN or scratch

### Research Questions to Answer

| Question | Finding |
|----------|---------|
| What triggers this procedure? | ___ |
| Who executes this procedure? | ___ |
| What are the inputs/outputs? | ___ |
| What can go wrong? | ___ |
| What existing patterns apply? | ___ |

---

## Phase 2: Graduation Validation (L436)

**Objective**: Verify pattern meets graduation criteria before formalizing as SOP.

### Graduation Validation Checklist

Required for SOPs that graduate from PROJECT_PLAN:

- [ ] **Execution Count**
  - [ ] Pattern executed successfully: ___ times
  - [ ] Minimum 2+ executions: Yes/No

- [ ] **General Applicability**
  - [ ] Pattern applies beyond specific context: Yes/No
  - [ ] Applicable scenarios: ___

- [ ] **Value Assessment**
  - [ ] Documentation value exceeds maintenance cost: Yes/No
  - [ ] Justification: ___

- [ ] **Complexity Warrant**
  - [ ] Procedure complexity warrants documentation: Yes/No
  - [ ] Key complexity factors: ___

- [ ] **Source PROJECT_PLAN(s)**
  - [ ] Graduating from: ___
  - [ ] Related PROJECT_PLANs: ___

### Skip Conditions

Graduation validation may be skipped if:
- Creating from consolidation (3+ L-docs → SOP per L524)
- Creating from enhancement request with clear need
- Creating meta-SOP (e.g., this SOP)

---

## Phase 3: SOP Creation (AGET_SOP_SPEC)

**Objective**: Author SOP conforming to specification.

### SOP Creation Checklist

#### Required Elements (CAP-SOP-001)

- [ ] **File naming**: `sops/SOP_{snake_case}.md`
- [ ] **Header block**:
  - [ ] Version: M.m.p (start at 1.0.0)
  - [ ] Created: YYYY-MM-DD
  - [ ] Owner: {agent-name}
  - [ ] Related: {L-docs, specs}
- [ ] **Purpose section**: Why this SOP exists
- [ ] **Scope section**: When it applies, when it doesn't

#### Recommended Elements (Best Practice)

- [ ] **Implements**: R-{DOMAIN}-{NNN}-* (if requirements exist)
- [ ] **Pain Point**: L-doc reference
- [ ] **See**: Spec section reference
- [ ] **Pattern**: L-doc reference
- [ ] **Triggers section**: Mandatory/Optional tables
- [ ] **Procedure section**: Step-by-step instructions
- [ ] **Checklists**: Per scenario type (A/B/C/D pattern)
- [ ] **Output Template**: What the SOP produces
- [ ] **Examples section**: Good and bad examples
- [ ] **Anti-Patterns section**: What to avoid
- [ ] **Metrics section**: How to measure success
- [ ] **Common Misconceptions**: Clarifications
- [ ] **Quick Reference section**: Condensed guidance
- [ ] **References section**: Related documents

#### Vocabulary Compliance (CAP-SOP-002)

- [ ] Title_Case for AGET-specific domain objects
- [ ] Compound terms for generic concepts (e.g., `Validation_Gate` not `gate`)
- [ ] Local vocabulary defined if new terms used
- [ ] No informal terms in requirement statements

#### AGET Lifecycle SOP Naming Convention

**Pattern**: `SOP_aget_{active_verb}.md`

**Rationale**: Active verbs are clearer, more action-oriented, and align with
command-style naming (like CLI commands: `create`, `delete`, `migrate`).

| Lifecycle Phase | SOP Name | Purpose |
|-----------------|----------|---------|
| Instantiation | `SOP_aget_create.md` | Create new AGET from template |
| Version change | `SOP_aget_upgrade.md` | Increment AGET version |
| Structural change | `SOP_aget_migrate.md` | Major structural migration |
| Retirement | `SOP_aget_decommission.md` | Archive/remove AGET |

**Verb Selection**:
- Use present tense, imperative form: `create` not `creation`
- Match L501 Artifact_Lifecycle_Status transitions where applicable
- Avoid ambiguous verbs: prefer `decommission` over `delete` (implies process, not just removal)

**Specialization** (when needed):
- `SOP_aget_template_create.md` — Template-specific
- `SOP_aget_portfolio_create.md` — Portfolio-specific

**Migration Note**: Existing SOPs using noun forms (e.g., `SOP_aget_create.md`)
will be renamed to active verb pattern in future release.

| Current | Target |
|---------|--------|
| `SOP_aget_create.md` | `SOP_aget_create.md` |
| `SOP_aget_migrate.md` | `SOP_aget_migrate.md` |

### SOP Structure Template

```markdown
# SOP: {Title}

**Implements**: {R-xxx-nnn-* if applicable}
**Pain Point**: {L-doc reference}
**See**: {Spec section reference}
**Pattern**: {L-doc reference}

---

**Version**: 1.0.0
**Created**: {YYYY-MM-DD}
**Owner**: {agent-name}
**Category**: {category}
**Related**: {L-docs, specs, patterns}

---

## Purpose

{Why this SOP exists}

**Problem Solved**: {What happens without this SOP}

---

## Scope

### When to Use This SOP

| Trigger | Example |
|---------|---------|
| {trigger} | {example} |

### When NOT to Use This SOP

| Situation | Alternative |
|-----------|-------------|
| {situation} | {alternative} |

---

## Procedure

### Step 1: {Title}

{Instructions}

### Step 2: {Title}

{Instructions}

---

## Examples

### Example: Good

{Good example}

### Example: Bad (Anti-Pattern)

{Bad example with why it's wrong}

---

## Anti-Patterns

| Anti-Pattern | Consequence |
|--------------|-------------|
| {anti-pattern} | {consequence} |

---

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| {metric} | {description} | {target} |

---

## References

- {Reference 1}
- {Reference 2}

---

*SOP_{name}.md v1.0.0 — {tagline}*
```

---

## Phase 4: Validation

**Objective**: Verify SOP meets all requirements.

### SOP Validation Checklist

#### Structural Validation

- [ ] File in correct location: `sops/`
- [ ] File naming follows pattern: `SOP_{snake_case}.md`
- [ ] Required sections present: Purpose, Scope
- [ ] Header complete: Version, Created, Owner

#### Content Validation

- [ ] Purpose clearly states why SOP exists
- [ ] Scope clearly states when to apply/not apply
- [ ] Procedure is actionable (if included)
- [ ] Examples are realistic (if included)

#### Traceability Validation

- [ ] Implements line references requirements (if applicable)
- [ ] Related line references L-docs/specs
- [ ] References section links to related docs

#### Vocabulary Validation

- [ ] No informal terms in requirement statements
- [ ] Title_Case used for AGET-specific concepts
- [ ] Generic terms use compound form

#### Self-Documentation Validation

- [ ] Would someone new understand the SOP?
- [ ] Anti-patterns help avoid common mistakes?
- [ ] Metrics define success measurement?

---

## Examples

### Example: Good SOP Creation

```
Trigger: L524 pattern (3+ L-docs on cross-AGET communication)

Phase 1: Research
- Found L180, L336, L337, L373, L415 on topic
- No existing SOP covers this
- Consolidation opportunity identified

Phase 2: Graduation (Skip - consolidation path)

Phase 3: Creation
- Created sops/SOP_cross_aget_communication.md
- Included all required sections
- Referenced all 5 L-docs

Phase 4: Validation
- All checklist items pass
- SOP complete
```

### Example: Bad SOP Creation (Anti-Pattern)

```
Trigger: "We need an SOP for X"

Action: Create SOP immediately

Problems:
- No research investment
- No graduation validation
- Pattern not proven (executed 0 times)
- Will likely require major revisions
```

---

## Anti-Patterns

| Anti-Pattern | Consequence | Prevention |
|--------------|-------------|------------|
| **Premature SOP** | SOP for unproven pattern | Apply L436 graduation criteria |
| **Research Skip** | Missing context, incomplete SOP | Complete Phase 1 checklist |
| **SOP Theater** | SOP exists but isn't followed | Validate SOP is actionable |
| **Section Skip** | Missing Purpose or Scope | Use creation checklist |
| **Vocabulary Drift** | Informal terms in formal doc | Apply vocabulary validation |
| **Orphan SOP** | No traceability to L-docs/specs | Include Related and References |

---

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Research coverage | % of SOPs with documented research | 100% |
| Graduation compliance | % of SOPs meeting L436 criteria | 90% |
| Structure compliance | % of SOPs passing structural validation | 100% |
| Traceability | % of SOPs with proper references | 100% |

---

## Quick Reference

### Minimum Viable SOP

1. **Research**: Search L-docs and existing SOPs
2. **Graduation**: Confirm 2+ executions OR consolidation trigger
3. **Create**: File naming, Purpose, Scope
4. **Validate**: Structural + Content check

### Decision Tree

```
Want to create SOP?
    │
    ├── Has pattern been proven?
    │   ├── No → Document as L-doc first
    │   └── Yes → Continue
    │
    ├── 3+ related L-docs exist?
    │   ├── Yes → Consolidation path (skip graduation)
    │   └── No → Continue
    │
    ├── Executed 2+ times?
    │   ├── No → Wait for more executions
    │   └── Yes → Continue
    │
    └── Create SOP following Phase 3-4
```

---

## References

- AGET_SOP_SPEC.md v1.2.0 — SOP structure requirements
- L436: PROJECT_PLAN to SOP Graduation Pattern
- L524: Pattern Consolidation into SOP
- L376: Checklist-Driven Gate Design
- L435: PROJECT_PLAN Retrospective Requirement
- TEMPLATE_SOP.md — Reusable SOP template

---

## Graduation History

```yaml
graduation:
  source: "PROJECT_PLAN_sop_creation_sop_v1.0.md"
  trigger: "Meta-SOP needed to govern SOP creation"
  research:
    enhancement_requests: 0
    existing_sops_audited: 20+
    exemplary_sops_analyzed: 5
    l_docs_mined: 4
  validation: "validate_sop_compliance.py — PASS (v1.1.0, 2026-07-16)"
  correction_2026_07_16: |
    v1.0.0 asserted "Self-validates (this SOP passes its own criteria)" while
    failing validate_sop_compliance.py on two counts (non-snake_case filename,
    missing Status field). The claim was never mechanically checked. Renamed
    SOP_SOP_CREATION.md -> SOP_sop_creation.md and added Status; the validator
    is now wired into health_check.py so the assertion is re-tested every run
    rather than trusted.
```

---

*SOP_sop_creation.md v1.1.0 — "The SOP for creating SOPs"*
*Created: 2026-01-16 | Updated: 2026-07-16*
*Owner: private-aget-framework-AGET*
