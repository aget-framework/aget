# SOP: Agent Instance Creation (Ontology-Driven)

**Version**: 2.2.0
**Created**: 2026-01-07
**Updated**: 2026-02-14 (Archetype skill guidance per v3.5.0)
**Owner**: aget-framework
**Implements**: L481 (Ontology-Driven Agent Creation), L482 (SKOS+EARS Grounding)
**Traces to**: AGET_INSTANCE_SPEC.md, AGET_IDENTITY_JSON_SCHEMA.md, L171 (Instance Creation Specification Gap)
**Related**: L480 (Write Scope Vocabulary), L478 (Interface Specialist Pattern), L488 (SOP Template vs Operational Reality)
**Validated By**: Agent instantiation (2026-01-08), identity schema remediation (2026-01-08)
**Applies To**: All new agent instance creation in AGET framework

---

## Purpose

Standard operating procedure for creating new agent instances using **ontology-driven** approach. Vocabulary and specifications DRIVE agent creation - they are not afterthoughts.

**Key Principle (L481)**: Define what the agent IS before instantiating it.

---

## Prerequisites

Before starting instance creation:

- [ ] **Review GETTING_STARTED.md** (L487: New SOPs must INHERIT from existing processes)
- [ ] Template selected (see Template Selection below)
- [ ] **Template maturity assessed** (L487: Skeleton templates require more remediation)
- [ ] Write scope determined: `-aget` (internal KB) or `-AGET` (external systems)
- [ ] Domain vocabulary concepts identified
- [ ] Research scope defined
- [ ] **Fleet version checked** (L487: Target current fleet standard aget_version)

---

## Pre-Creation Checkpoint (CRITICAL)

**Stop and verify understanding before proceeding**:

| Statement | Confirm |
|-----------|---------|
| Vocabulary and specs are created BEFORE the agent instance | [ ] |
| `-aget` suffix means internal KB writes only (L480) | [ ] |
| `-AGET` suffix means external system writes (L480) | [ ] |
| SKOS format for vocabulary definitions (L482) | [ ] |
| EARS format for behavioral requirements (L482) | [ ] |

**If any statement is unclear, read L480, L481, L482 before proceeding.**

---

## Write Scope Determination (L480)

### Decision Tree

```
Does the agent need to modify external systems?
|
+- NO -> Use lowercase `-aget`
|       Examples: private-{name}-aget, private-{research}-aget
|       Scope: Internal KB writes only (L-docs, specs, sessions)
|
+- YES -> Use uppercase `-AGET`
         Examples: private-{name}-AGET
         Scope: External system writes (repos, releases, publications)
```

### Distinguishing Criteria for `-AGET`

An agent requires uppercase `-AGET` if ANY of these apply:

| Criterion | Example |
|-----------|---------|
| Modifies external repositories | Push to public repos |
| Has publication/release authority | Create releases, tags |
| Manages other repositories | Cross-repo coordination |

**Default**: Use `-aget`. Elevate to `-AGET` only with justification.

---

## Gate Structure

| Gate | Objective | Key Artifacts |
|------|-----------|---------------|
| G0 | Pre-Requisites | Template selection, tooling assessment, fleet version |
| **G1** | **Ontology (SKOS+EARS)** | **VOCABULARY.md, SPEC.md, METHODOLOGY.md** |
| G2 | Tooling (conditional) | Script enhancement if needed |
| G3 | Instance Creation | Agent directory from template + specs + CLAUDE.md |
| G4 | Capability Configuration | 5D config, governance files |
| G5 | Validation | Structural + spec compliance + **operational test** |
| G6 | Initial Assignment | Knowledge prepopulation, backlog |
| **G7** | **Supervisor Handoff** | **Handoff document, supervisor review** |
| **G8** | **Acknowledgment** | **Fleet registry, ACK document** |

**Note (L487)**: Gates 0-6 create the agent. Gates 7-8 register it with the fleet. Agent is not "active" until G8 completes.

---

## Gate 0: Pre-Requisites

### Objective

Ensure tooling and template selection are complete.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G0.1 | Template selection | V0.1: Template exists and is accessible |
| G0.2 | Tooling assessment | V0.2: Script supports naming convention |
| G0.3 | Directory location | V0.3: Parent directory writable |
| G0.4 | **Template maturity assessment** | V0.4: Session scripts present, CLAUDE.md pattern |
| G0.5 | **Fleet version check** | V0.5: Target aget_version matches fleet standard |

### Template Selection Guide (v3.5.0+)

| Template | Archetype | Entity Affinity | Archetype Skills | Use Case |
|----------|-----------|-----------------|------------------|----------|
| template-worker-aget | worker | Task, Work_Item | execute-task, report-progress | Task execution |
| template-supervisor-aget | supervisor | Fleet, Agent | broadcast-fleet, review-agent, escalate-issue | Fleet coordination |
| template-developer-aget | developer | Code, Module | run-tests, lint-code, review-pr | Code development |
| template-consultant-aget | consultant | Client, Engagement | assess-client, propose-engagement | Client advisory |
| template-advisor-aget | advisor | Risk, Recommendation | assess-risk, recommend-action | Risk & guidance |
| template-analyst-aget | analyst | Data, Metric | analyze-data, generate-report | Data analysis |
| template-architect-aget | architect | System, Component | design-architecture, assess-tradeoffs | System design |
| template-researcher-aget | researcher | Finding, Literature | search-literature, document-finding | Research |
| template-operator-aget | operator | Incident, Playbook | handle-incident, run-playbook | Operations |
| template-executive-aget | executive | Decision, Budget | make-decision, review-budget | Leadership |
| template-reviewer-aget | reviewer | Artifact, Feedback | review-artifact, provide-feedback | Quality review |
| template-spec-engineer-aget | spec-engineer | Requirement, Spec | validate-spec, generate-requirement | Specification |

```
Question 1: Primary function?
+- Research/Analysis -> template-researcher-aget (2 archetype skills)
+- Specification authoring -> template-spec-engineer-aget (2 archetype skills)
+- Guidance/recommendations -> template-advisor-aget (2 archetype skills)
+- Development/coding -> template-developer-aget (3 archetype skills)
+- General execution -> template-worker-aget (2 archetype skills)
+- Fleet coordination -> template-supervisor-aget (3 archetype skills)

Question 2: Does archetype match your entity model?
+- Check Entity Affinity column above
+- Agent will work primarily with these entity types
+- Mismatch = potential friction

Question 3: Capabilities needed from other templates?
+- List capabilities to borrow
+- Document in G1.3 METHODOLOGY.md
```

**Skill Preview**: Each template includes 14 universal skills + archetype-specific skills (16-17 total).

### V-Tests

```bash
# V0.1: Template exists
ls -la /path/to/aget-framework/template-{type}-aget/
# Expected: Directory with .aget/, AGENTS.md

# V0.2: Script assessment
python3 /path/to/aget/scripts/instantiate_template.py --help
# Expected: Understand suffix validation behavior

# V0.3: Directory writable
touch /path/to/target/directory/.write_test && rm /path/to/target/directory/.write_test
# Expected: Success (no permission error)

# V0.4: Template maturity (L487)
ls -la /path/to/aget-framework/template-{type}-aget/.aget/patterns/session/
# Expected: wake_up.py, wind_down.py present (if not, plan for remediation)

# V0.5: Fleet version check (L487)
jq -r '.aget_version' {supervisor-path}/.aget/version.json
# Expected: Current fleet standard (e.g., 3.2.1) - target this version
```

### Gate 0 Decision Point

- [ ] Template selected and accessible
- [ ] Tooling requirements understood
- [ ] Directory location confirmed
- [ ] **Template maturity assessed** (L487: Session scripts, CLAUDE.md)
- [ ] **Fleet version identified** (L487: Target current standard)
- [ ] GO / NO-GO for ontology creation

---

## Gate 1: Ontology Creation (SKOS+EARS)

### Objective

Define the agent's conceptual framework BEFORE instantiation.

**Rationale (L481, L482)**: The vocabulary and specifications DRIVE agent creation. SKOS provides formal vocabulary. EARS provides testable requirements.

### Deliverables

| ID | Deliverable | Format | V-Test |
|----|-------------|--------|--------|
| G1.1 | {DOMAIN}_VOCABULARY.md | SKOS | V1.1: SKOS compliance |
| G1.2 | {DOMAIN}_SPEC.md | EARS | V1.2: EARS compliance |
| G1.3 | RESEARCH_METHODOLOGY.md | Prose | V1.3: Sections complete |
| G1.4 | Archetype ontology customization | YAML | V1.4: ONTOLOGY_{archetype}.yaml reviewed (v3.5.0+) |

### G1.1: Vocabulary Template (SKOS)

```yaml
# {DOMAIN} Research Domain Vocabulary
# Owned by: private-{name}-aget
# Status: Agent-specific (not framework vocabulary)
# Purpose: DRIVES agent identity, scope, and behavior

vocabulary:
  meta:
    domain: "{domain_identifier}"
    version: "1.0.0"
    owner: "private-{name}-aget"
    framework_proposal: null  # Set if proposed to AGET framework
    created: "YYYY-MM-DD"

  concepts:
    # Primary domain concepts (SKOS required properties)
    {Concept_Name}:
      skos:prefLabel: "{Human readable name}"
      skos:definition: "{Formal definition}"
      skos:narrower: []       # Child concepts (optional)
      skos:broader: null      # Parent concept (optional)
      skos:related: []        # Related concepts (optional)
      skos:example: []        # Concrete examples (recommended)
      research_status: "placeholder|foundation|complete"

  patterns:
    # Behavioral patterns within domain
    {Pattern_Name}:
      skos:definition: "{Pattern description}"
      skos:related: []        # Related L-docs or concepts
```

### G1.2: Specification Template (EARS)

```markdown
# {Domain} Specification

**Version**: 0.1.0
**Status**: DRAFT
**Owner**: private-{name}-aget
**Scope**: Agent-internal research framework
**Purpose**: DEFINES research scope and behavioral constraints

## Abstract

This specification defines [what] as understood by private-{name}-aget
for [purpose].

## Research Scope

This agent investigates:
1. [Topic 1]
2. [Topic 2]
...

## Requirements (EARS Format)

### Ubiquitous Requirements

R-{DOM}-001: The agent SHALL {behavior}.
R-{DOM}-002: The agent SHALL {behavior}.

### Event-Driven Requirements

R-{DOM}-010: When {trigger}, the agent SHALL {action}.
R-{DOM}-011: When {trigger}, the agent SHALL {action}.

### Constraints

R-{DOM}-090: The agent SHALL NOT {prohibited behavior}.

## Success Criteria

Research is complete when:
- [ ] Each {concept} has comprehensive L-docs
- [ ] {Pattern} interactions documented
- [ ] Framework implications identified

## Traceability

| Requirement | Vocabulary Term | V-Test |
|-------------|-----------------|--------|
| R-{DOM}-001 | {Concept_Name} | V-{DOM}-001 |
```

### G1.3: Methodology Template

```markdown
# Research Methodology

**Version**: 1.0.0
**Owner**: private-{name}-aget
**Purpose**: DEFINES how this agent conducts research

## Approach

1. **{Method 1}**
   - {Details}

2. **{Method 2}**
   - {Details}

## Quality Standards

- Every claim has evidence (doc link or test)
- Every finding links to vocabulary term
- Every L-doc includes theoretical basis

## Borrowed Capabilities

| Capability | Source Template | Usage |
|------------|-----------------|-------|
| {capability} | template-{type}-aget | {how used} |
```

### G1.4: Archetype Ontology Review (v3.5.0+)

Each template includes a pre-defined archetype ontology at `ontology/ONTOLOGY_{archetype}.yaml`. Review and customize as needed:

```yaml
# Template: ontology/ONTOLOGY_{archetype}.yaml
# Review these archetype-specific concepts

ontology:
  meta:
    archetype: "{archetype}"
    version: "1.0.0"
    purpose: "Archetype-specific domain concepts"

  concepts:
    # Review each concept for applicability to your instance
    # Customize prefLabels and definitions as needed
    {Concept_Name}:
      skos:prefLabel: "{Label}"
      skos:definition: "{Definition}"
```

**Actions**:
1. Review `ONTOLOGY_{archetype}.yaml` in selected template
2. Identify concepts relevant to instance specialization
3. Document any customizations needed in METHODOLOGY.md
4. Verify ontology aligns with domain vocabulary (G1.1)

### Staging Location

Specs are created in staging BEFORE the agent instance:

```
planning/artifacts/private-{name}-aget/
+-- specs/
|   +-- {DOMAIN}_VOCABULARY.md     # G1.1
|   +-- {DOMAIN}_SPEC.md           # G1.2
|   +-- RESEARCH_METHODOLOGY.md    # G1.3
```

### V-Tests

```bash
# V1.1: SKOS compliance
grep -c "skos:definition" planning/artifacts/private-{name}-aget/specs/{DOMAIN}_VOCABULARY.md
# Expected: >= 1 per concept

grep -c "skos:prefLabel" planning/artifacts/private-{name}-aget/specs/{DOMAIN}_VOCABULARY.md
# Expected: >= 1 per concept

# V1.2: EARS compliance
grep -cE "^R-[A-Z]+-[0-9]+:" planning/artifacts/private-{name}-aget/specs/{DOMAIN}_SPEC.md
# Expected: >= 3 requirements

grep -c "SHALL" planning/artifacts/private-{name}-aget/specs/{DOMAIN}_SPEC.md
# Expected: >= 3 (one per requirement minimum)

# V1.3: Methodology sections
for section in "Approach" "Quality Standards" "Borrowed Capabilities"; do
  grep -q "## $section" planning/artifacts/private-{name}-aget/specs/RESEARCH_METHODOLOGY.md && \
    echo "PASS $section" || echo "FAIL $section missing"
done

# V1.4: Archetype ontology reviewed (v3.5.0+)
ls /path/to/aget-framework/template-{type}-aget/ontology/ONTOLOGY_{archetype}.yaml
# Expected: File exists in template
# Action: Review concepts for instance-specific customization needs
```

### Gate 1 Decision Point

- [ ] Vocabulary has SKOS-compliant definitions for all domain concepts
- [ ] Specification has EARS-compliant requirements (R-XXX-NNN)
- [ ] Methodology documents approach and borrowed capabilities
- [ ] All V-Tests pass
- [ ] Ontology ready to DRIVE instance creation
- [ ] GO / NO-GO for tooling/instantiation

---

## Gate 2: Tooling Enhancement (Conditional)

### Objective

Update instantiate_template.py if needed to support naming convention.

**Condition**: Only if G0.2 determined enhancement is required.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G2.1 | Suffix validation update | V2.1: Both `-aget` and `-AGET` accepted |
| G2.2 | Documentation update | V2.2: GETTING_STARTED.md reflects L480 |

### V-Tests

```bash
# V2.1: Lowercase suffix accepted
python3 instantiate_template.py --template template-researcher-aget \
  --name test-example-aget --dry-run 2>&1 | grep -v "Error"
# Expected: Success or dry-run output (no suffix error)

# V2.2: Documentation updated
grep -q "aget.*internal" /path/to/GETTING_STARTED.md && \
  grep -q "AGET.*external" /path/to/GETTING_STARTED.md
# Expected: Both patterns found
```

### Gate 2 Decision Point

- [ ] Script accepts required naming convention (or workaround documented)
- [ ] GO / NO-GO for instance creation

---

## Gate 3: Instance Creation

### Objective

Create agent instance FROM the ontology defined in Gate 1.

**Key Principle**: Instance derives from vocabulary + specification.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G3.1 | Clone template | V3.1: Directory structure exists |
| G3.2 | Copy specs from staging | V3.2: specs/ directory populated |
| G3.3 | Update version.json | V3.3: Valid JSON with required fields |
| G3.4 | Update identity.json | V3.4: North Star derived from spec |
| G3.5 | Create/update AGENTS.md | V3.5: References vocabulary and spec |
| G3.6 | **Create CLAUDE.md symlink** | V3.6: CLAUDE.md -> AGENTS.md symlink |
| G3.7 | **Deploy session scripts** | V3.7: wake_up.py, wind_down.py present |
| G3.8 | **Verify archetype skills** | V3.8: Archetype-specific skills present (v3.5.0+) |

### version.json Template (Derived from Specs)

```json
{
  "agent_name": "private-{name}-aget",
  "version": "1.0.0",
  "instance_type": "aget",
  "manifest_version": "3.0",
  "archetype": "{archetype}",
  "specialization": "{domain}",
  "aget_version": "3.2.0",
  "template_origin": "template-{type}-aget",
  "created_date": "YYYY-MM-DD",
  "write_scope": "internal",
  "managed_by": "{supervisor-agent}",
  "portfolio": "{portfolio}",
  "specs_version": "1.0.0",
  "vocabulary_ref": "specs/{DOMAIN}_VOCABULARY.md",
  "spec_ref": "specs/{DOMAIN}_SPEC.md"
}
```

### identity.json Template (Derived from Specs)

**CRITICAL**: `north_star` MUST be an object, not a string. See AGET_IDENTITY_JSON_SCHEMA.md.

```json
{
  "name": "private-{name}-aget",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "version": "1.0.0",
  "north_star": {
    "type": "purpose",
    "statement": "{Derived from SPEC success criteria - what the agent aims to achieve}",
    "success_looks_like": [
      "{Observable indicator 1 from spec}",
      "{Observable indicator 2 from spec}"
    ],
    "failure_looks_like": [
      "{Failure indicator 1}",
      "{Failure indicator 2}"
    ]
  },
  "identity_dimensions": {
    "role": "{Role description from spec}",
    "scope": "{Scope from spec}",
    "relationship_to_supervisor": "Child agent managed by {supervisor-agent}"
  },
  "operating_principles": [
    "{Principle 1 from methodology}",
    "{Principle 2 from methodology}"
  ],
  "archetype": "{archetype}",
  "vocabulary_ref": "specs/{DOMAIN}_VOCABULARY.md",
  "spec_ref": "specs/{DOMAIN}_SPEC.md"
}
```

**Schema Reference**: `aget-framework/aget/specs/AGET_IDENTITY_JSON_SCHEMA.md`

### V-Tests

```bash
# V3.1: Directory structure exists
ls -la private-{name}-aget/.aget/
# Expected: version.json, identity.json, evolution/, etc.

# V3.2: Specs copied
ls private-{name}-aget/specs/
# Expected: {DOMAIN}_VOCABULARY.md, {DOMAIN}_SPEC.md, RESEARCH_METHODOLOGY.md

# V3.3: version.json valid and complete
cat private-{name}-aget/.aget/version.json | python3 -m json.tool > /dev/null && \
  jq -e '.agent_name and .specs_version and .vocabulary_ref' \
    private-{name}-aget/.aget/version.json
# Expected: Valid JSON, required fields present

# V3.4: identity.json has North Star (MUST be object with statement)
jq -e '.north_star.statement | length > 10' private-{name}-aget/.aget/identity.json
# Expected: North Star is object with meaningful statement (>10 chars)
# NOTE: String north_star will FAIL this test (correct behavior - see L488)

# V3.5: AGENTS.md references specs
grep -q "vocabulary_ref\|VOCABULARY.md" private-{name}-aget/AGENTS.md || \
  grep -q "spec_ref\|SPEC.md" private-{name}-aget/AGENTS.md
# Expected: At least one spec reference

# V3.6: CLAUDE.md symlink (L487)
ls -la private-{name}-aget/CLAUDE.md | grep -q "AGENTS.md"
# Expected: CLAUDE.md -> AGENTS.md symlink (per GETTING_STARTED.md)

# V3.7: Session scripts deployed (L487)
ls private-{name}-aget/.aget/patterns/session/
# Expected: wake_up.py, wind_down.py present

# V3.8: Archetype skills present (v3.5.0+)
ls private-{name}-aget/.claude/skills/aget-*/SKILL.md | wc -l
# Expected: 16-17 (14 universal + 2-3 archetype-specific)
# Verify archetype skills match template:
#   worker: execute-task, report-progress (2)
#   supervisor: broadcast-fleet, review-agent, escalate-issue (3)
#   developer: run-tests, lint-code, review-pr (3)
#   (see Template Selection Guide for complete list)
```

### Gate 3 Decision Point

- [ ] Instance created FROM specs (not independently)
- [ ] Specs copied to instance specs/ directory
- [ ] version.json references specs_version
- [ ] identity.json derived from specification
- [ ] **CLAUDE.md symlink created** (L487)
- [ ] **Session scripts deployed** (L487)
- [ ] All V-Tests pass
- [ ] GO / NO-GO for capability configuration

---

## Gate 4: Capability Configuration

### Objective

Configure 5D architecture and governance files (derived from methodology).

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G4.1 | D1 Persona config | V4.1: archetype.yaml exists |
| G4.2 | D4 Skills config | V4.2: Capabilities from methodology declared |
| G4.3 | D5 Context config | V4.3: Relationships set |
| G4.4 | Governance files | V4.4: CHARTER, MISSION, SCOPE exist |

### V-Tests

```bash
# V4.1: Persona configured
cat private-{name}-aget/.aget/persona/archetype.yaml | grep -q "archetype:"
# Expected: archetype field present

# V4.2: Capabilities declared (from methodology)
cat private-{name}-aget/.aget/skills/capabilities.yaml
# Expected: Lists capabilities from RESEARCH_METHODOLOGY.md

# V4.3: Relationships configured
cat private-{name}-aget/.aget/context/relationships.yaml | grep -q "managed_by:"
# Expected: managed_by field present

# V4.4: Governance files exist with content
for f in CHARTER.md MISSION.md SCOPE_BOUNDARIES.md; do
  [ -s "private-{name}-aget/governance/$f" ] && \
    echo "PASS $f" || echo "FAIL $f missing or empty"
done
# Expected: All three files exist and have content
```

### Gate 4 Decision Point

- [ ] 5D configuration complete
- [ ] Governance files created
- [ ] Capabilities match methodology
- [ ] All V-Tests pass
- [ ] GO / NO-GO for validation

---

## Gate 5: Validation

### Objective

Validate instance compliance with specifications AND framework requirements.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G5.1 | Structural validation | V5.1: validate_template_instance.py passes |
| G5.2 | Spec compliance | V5.2: Instance implements spec requirements |
| G5.3 | Naming compliance | V5.3: validate_naming_conventions.py passes |
| G5.4 | Wake-up executes | V5.4: wake_up.py runs without error |
| G5.5 | **Operational test** | V5.5: "wake up" command produces valid session output |
| G5.6 | **Conformance check** | V5.6: validate_conformance.py scores L2+ |
| G5.7 | **Archetype skill validation** | V5.7: Archetype skills match template type (v3.5.0+) |

**Note (L487)**: Structural validation is not the same as operational validation. V5.1-V5.4 check structure; V5.5-V5.6 confirm the agent works and meets conformance standards.

### V-Tests

```bash
# V5.1: Structural validation (24 checks)
python3 ~/github/aget-framework/aget/validation/validate_template_instance.py \
  private-{name}-aget/
# Expected: 24/24 PASS (or current check count)

# V5.2: Spec compliance - verify traceable requirements
# For each R-XXX-NNN in spec, verify implementation exists
grep -oE "R-[A-Z]+-[0-9]+" private-{name}-aget/specs/{DOMAIN}_SPEC.md | sort -u | while read req; do
  grep -rq "$req" private-{name}-aget/ && \
    echo "PASS $req traceable" || echo "WARN $req not traced"
done
# Expected: All requirements traceable

# V5.3: Naming conventions
python3 ~/github/aget-framework/aget/validation/validate_naming_conventions.py \
  private-{name}-aget/
# Expected: PASS

# V5.4: Wake-up executes
cd private-{name}-aget && python3 .aget/patterns/session/wake_up.py
# Expected: Session summary output (no errors)

# V5.5: Operational test (L487 - critical)
# In Claude Code session, with CLAUDE.md symlink, issue "wake up" command
# Expected: Agent responds with session summary, demonstrates understanding of:
#   - Own identity (from identity.json)
#   - Own purpose (from north_star)
#   - Vocabulary scope (from VOCABULARY.md)
# This confirms the agent is operationally functional, not just structurally valid

# V5.6: Conformance check (v3.4+)
python3 ~/github/aget-framework/aget/validation/validate_conformance.py private-{name}-aget/ --verbose
# Expected: L2_COMPLIANT or higher (60%+ score)
# If L1 or L0: Review gaps in output and remediate using CONFORMANCE_RUBRIC.md patterns

# V5.7: Archetype skill validation (v3.5.0+)
# Verify archetype-specific skills are present and match template type
ARCHETYPE=$(jq -r '.archetype' private-{name}-aget/.aget/version.json)
case "$ARCHETYPE" in
  worker) EXPECTED_SKILLS="execute-task report-progress" ;;
  supervisor) EXPECTED_SKILLS="broadcast-fleet review-agent escalate-issue" ;;
  developer) EXPECTED_SKILLS="run-tests lint-code review-pr" ;;
  consultant) EXPECTED_SKILLS="assess-client propose-engagement" ;;
  advisor) EXPECTED_SKILLS="assess-risk recommend-action" ;;
  analyst) EXPECTED_SKILLS="analyze-data generate-report" ;;
  architect) EXPECTED_SKILLS="design-architecture assess-tradeoffs" ;;
  researcher) EXPECTED_SKILLS="search-literature document-finding" ;;
  operator) EXPECTED_SKILLS="handle-incident run-playbook" ;;
  executive) EXPECTED_SKILLS="make-decision review-budget" ;;
  reviewer) EXPECTED_SKILLS="review-artifact provide-feedback" ;;
  spec-engineer) EXPECTED_SKILLS="validate-spec generate-requirement" ;;
esac
for skill in $EXPECTED_SKILLS; do
  [ -f "private-{name}-aget/.claude/skills/aget-$skill/SKILL.md" ] && \
    echo "PASS aget-$skill" || echo "FAIL aget-$skill missing"
done
# Expected: All archetype skills present
```

### Gate 5 Decision Point

- [ ] Structural validation passes
- [ ] All spec requirements are traceable
- [ ] Naming conventions compliant
- [ ] Wake-up protocol functional
- [ ] **Operational test passes** (L487: Agent works in actual session)
- [ ] **Conformance check passes** (v3.4+: L2+ score)
- [ ] **Archetype skills validated** (v3.5.0+: All archetype skills present)
- [ ] All V-Tests pass
- [ ] GO / NO-GO for initial assignment

---

## Gate 6: Initial Assignment

### Objective

Prepopulate knowledge base and create research backlog.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G6.1 | knowledge/ structure | V6.1: Directories match vocabulary |
| G6.2 | Research backlog | V6.2: Topics derived from vocabulary |
| G6.3 | evolution/index.json | V6.3: Valid JSON, count >= 0 |
| G6.4 | Fleet registration | V6.4: Entry in FLEET_STATE.yaml |

### V-Tests

```bash
# V6.1: Knowledge structure matches vocabulary concepts
for concept in $(grep "skos:prefLabel" private-{name}-aget/specs/{DOMAIN}_VOCABULARY.md | \
  sed 's/.*"\(.*\)"/\1/' | tr ' ' '_' | tr '[:upper:]' '[:lower:]'); do
  [ -d "private-{name}-aget/knowledge/$concept" ] || \
    [ -f "private-{name}-aget/knowledge/$concept.md" ] && \
    echo "PASS $concept" || echo "WARN $concept not in knowledge/"
done
# Expected: Key concepts have knowledge entries

# V6.2: Backlog exists with vocabulary terms
[ -f "private-{name}-aget/planning/RESEARCH_BACKLOG.md" ] && \
  grep -q "Vocabulary Term" private-{name}-aget/planning/RESEARCH_BACKLOG.md
# Expected: Backlog exists and references vocabulary

# V6.3: evolution/index.json valid
cat private-{name}-aget/.aget/evolution/index.json | python3 -m json.tool > /dev/null
# Expected: Valid JSON

# V6.4: Fleet registration (if applicable)
grep -q "private-{name}-aget" {supervisor-path}/.aget/fleet/FLEET_STATE.yaml 2>/dev/null || \
  echo "WARN Not yet registered in fleet (may be intentional)"
# Expected: Entry exists OR intentionally deferred
```

### Gate 6 Decision Point

- [ ] Knowledge structure aligned with vocabulary
- [ ] Research backlog created from vocabulary terms
- [ ] evolution/index.json initialized
- [ ] All V-Tests pass
- [ ] GO / NO-GO for supervisor handoff

---

## Gate 7: Supervisor Handoff (L487)

### Objective

Formally notify supervisor of new agent and receive review.

**Rationale (L487)**: Fleet registration is not automatic - it requires supervisor review to catch context-dependent issues that validation scripts miss.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G7.1 | Handoff document | V7.1: Document created at supervisor handoffs/ |
| G7.2 | Supervisor review | V7.2: Review received with compliance scorecard |
| G7.3 | Remediation (if needed) | V7.3: All remediation items addressed |

### Handoff Document Template

Location: `{supervisor-path}/handoffs/HANDOFF_{agent_name}_{date}.md`

Required sections:
- Executive Summary
- Agent Identity (table)
- North Star
- Provenance (creation methodology, validation status)
- Capabilities
- Write Scope
- Key Artifacts (paths)
- Requested Actions (1. Add to fleet registry, 2. Create acknowledgment)

### Supervisor Review Checklist

The supervisor will verify:

| Check | Required | Notes |
|-------|----------|-------|
| version.json valid | Yes | |
| identity.json valid | Yes | |
| CLAUDE.md symlink | Yes | |
| governance/ files | Yes | |
| specs/ files | Yes | |
| manifest_version | Yes | Must be 3.0 |
| aget_version | Yes | Must match fleet standard |
| Session scripts | Yes | wake_up.py, wind_down.py |
| Location | Document | Standard or exception documented |
| Naming | Document | Standard or exception documented |

### Remediation Process

If supervisor identifies issues:
1. Address each remediation item
2. Create RESPONSE document at `{framework-agent-path}/handoffs/RESPONSE_{agent_name}_review_{date}.md`
3. Re-submit for acknowledgment

### Gate 7 Decision Point

- [ ] Handoff document created
- [ ] Supervisor review received
- [ ] All remediation items addressed
- [ ] GO / NO-GO for acknowledgment

---

## Gate 8: Acknowledgment (L487)

### Objective

Receive formal acknowledgment and fleet registry update.

**Rationale (L487)**: Agent is not "active" in the fleet until formally acknowledged. This ensures proper tracking and governance.

### Deliverables

| ID | Deliverable | V-Test |
|----|-------------|--------|
| G8.1 | Fleet registry entry | V8.1: Entry in FLEET_STATE.yaml |
| G8.2 | ACK document | V8.2: ACK document at supervisor handoffs/ |
| G8.3 | Status: active | V8.3: Agent marked active in registry |

### Expected Acknowledgment

Location: `{supervisor-path}/handoffs/ACK_{agent_name}_{date}.md`

Contains:
- Fleet registration confirmation
- Fleet count update
- Any noted exceptions
- Agent status (active/inactive)

### V-Tests

```bash
# V8.1: Fleet registry entry
grep -q "private-{name}-aget" {supervisor-path}/.aget/fleet/FLEET_STATE.yaml
# Expected: Entry present

# V8.2: ACK document exists
ls {supervisor-path}/handoffs/ACK_private-{name}-aget_*.md
# Expected: ACK document present

# V8.3: Status is active
grep -A5 "private-{name}-aget" {supervisor-path}/.aget/fleet/FLEET_STATE.yaml | \
  grep -q "status: active"
# Expected: status: active
```

### Gate 8 Decision Point

- [ ] Fleet registry updated
- [ ] ACK document received
- [ ] Agent status: active
- [ ] **AGENT CREATION COMPLETE**

---

## Post-Creation Summary

### Verification Checklist

```bash
# Run complete verification suite
echo "=== Gate 1: Ontology ===" && \
  ls -la private-{name}-aget/specs/ && \

echo "=== Gate 3: Instance ===" && \
  cat private-{name}-aget/.aget/version.json | jq '.specs_version, .vocabulary_ref' && \

echo "=== Gate 5: Validation ===" && \
  python3 ~/github/aget-framework/aget/validation/validate_template_instance.py private-{name}-aget/ && \

echo "=== Gate 6: Assignment ===" && \
  ls private-{name}-aget/knowledge/ && \

echo "=== Complete ==="
```

### Expected Final Structure

```
private-{name}-aget/
+-- .aget/
|   +-- version.json           # References specs_version
|   +-- identity.json          # North Star from spec
|   +-- evolution/
|   |   +-- index.json
|   +-- persona/
|   +-- memory/
|   +-- reasoning/
|   +-- skills/
|   +-- context/
|   +-- patterns/
+-- specs/                     # ONTOLOGY (Gate 1)
|   +-- {DOMAIN}_VOCABULARY.md # SKOS
|   +-- {DOMAIN}_SPEC.md       # EARS
|   +-- RESEARCH_METHODOLOGY.md
+-- governance/
|   +-- CHARTER.md
|   +-- MISSION.md
|   +-- SCOPE_BOUNDARIES.md
+-- knowledge/                 # Aligned with vocabulary
+-- planning/
|   +-- RESEARCH_BACKLOG.md    # Derived from vocabulary
+-- sessions/
+-- AGENTS.md                  # References specs
```

---

## Troubleshooting

### "Specs created after instance"

**Problem**: Ontology created as afterthought, not driver.

**Fix**: Delete instance, return to Gate 1, create specs FIRST.

### "Requirements not traceable"

**Problem**: R-XXX-NNN requirements exist but no implementation traces.

**Fix**: Add `# Satisfies: R-XXX-NNN` comments or update spec traceability table.

### "Vocabulary terms not in knowledge/"

**Problem**: Knowledge structure doesn't match vocabulary.

**Fix**: Create knowledge directories/files for each major vocabulary concept.

---

## Time Estimate

| Gate | Effort | Cumulative |
|------|--------|------------|
| G0: Pre-Requisites | 15 min | 15 min |
| **G1: Ontology** | **45 min** | **60 min** |
| G2: Tooling (conditional) | 30 min | 90 min |
| G3: Instance Creation | 30 min | 120 min |
| G4: Capability Configuration | 30 min | 150 min |
| G5: Validation | 30 min | 180 min |
| G6: Initial Assignment | 25 min | 205 min |
| **G7: Supervisor Handoff** | **variable** | **varies** |
| **G8: Acknowledgment** | **variable** | **varies** |
| **Total (G0-G6)** | **~3.5 hours** | |

**Note (L487)**: Gates 7-8 timing depends on supervisor response time and remediation cycles. Initial instances may require multiple remediation cycles before registration.

---

## References

### Foundation L-docs

- L171: Instance Creation Specification Gap (identified the need)
- L478: Interface Specialist Agent Pattern
- L480: aget/AGET Write Scope Vocabulary Gap
- L481: Ontology-Driven Agent Creation
- L482: Executable Ontology - SKOS+EARS Grounding

### Lessons Learned (from initial agent instantiations)

- L483: Specification-Validation Drift (specs exist but validation doesn't enforce)
- L484: Wind Down Protocol - Capture vs Commit (session end should capture, not commit)
- L485: Archetype Purity vs Configured Instances (pure archetypes are theoretical)
- L486: Ontology-Driven Agent Creation - Validated (empirical proof of methodology)
- L487: Fleet Registration Process - Lessons Learned (handoff/acknowledgment pattern)

### Related Specifications

- AGET_INSTANCE_SPEC.md
- AGET_VOCABULARY_SPEC.md
- GETTING_STARTED.md (operational requirements)

---

*SOP: Agent Instance Creation (Ontology-Driven) v2.2.0*
*"Define what the agent IS before instantiating it."*
*Created: 2026-01-07 based on L480, L481, L482 learnings*
*Updated: 2026-01-08 based on L483-L487 lessons from initial agent instantiation*
*Updated: 2026-02-14 v3.5.0 archetype skill guidance (G1.4, G3.8, V5.7)*
