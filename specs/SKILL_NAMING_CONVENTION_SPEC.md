# SKILL_NAMING_CONVENTION_SPEC

**Version**: 1.4.0
**Status**: Active
**Category**: Specification (Skills)
**Format Version**: 1.3
**Created**: 2026-02-15
**Updated**: 2026-04-18
**Author**: aget-framework
**Location**: `aget/specs/SKILL_NAMING_CONVENTION_SPEC.md`
**Related Specs**: AGET_SESSION_SPEC, AGET_SKILL_SPEC
**Related Learnings**: L582 (skill sync), Phase 2 v3.5.0 migration findings

---

## Abstract

This specification defines naming conventions for AGET skills, ensuring consistency across the framework, templates, and fleet agents. It establishes the canonical pattern, prohibited patterns, and synchronization requirements between skill directories and spec filenames.

## Motivation

Naming inconsistencies observed during v3.5.0 fleet migration:

1. **Pattern drift**: `aget-sanity-check` vs `aget-check-health` (verb position inconsistent)
2. **Legacy names**: `aget-healthcheck-evolution` (compound verb, not verb-noun)
3. **Spec-to-skill drift**: SKILL-004 spec named `aget-healthcheck-*` but skill directory used different name
4. **Discovery confusion**: Agents couldn't reliably predict skill names

## Scope

**Applies to**: All AGET skills (universal and archetype-specific)

**Defines**:
- Canonical naming pattern
- Prohibited patterns
- Spec-to-skill synchronization requirements
- Migration guidance for legacy names
- Skill lifecycle governance (deprecation marking)
- Dependency validation

**Does not cover**:
- Skill implementation details (see AGET_SKILL_SPEC)
- Skill behavior specifications (see individual SKILL-NNN specs)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "skill_naming"
    version: "1.0.0"
    inherits: "aget_core"

  patterns:
    Skill_Name:
      skos:prefLabel: "Skill_Name"
      skos:definition: "Identifier for an AGET skill, following aget-{verb}-{noun} pattern"
      aget:pattern: "aget-{verb}-{noun}"
      skos:example: ["aget-check-health", "aget-record-lesson", "aget-create-project"]

    Canonical_Pattern:
      skos:prefLabel: "Canonical_Pattern"
      skos:definition: "The required naming pattern: aget-{verb}-{noun}"
      aget:regex: "^aget-[a-z]+-[a-z]+(-[a-z]+)?$"

    Prohibited_Pattern:
      skos:prefLabel: "Prohibited_Pattern"
      skos:definition: "Naming patterns that SHALL NOT be used"
      skos:example: ["aget-healthcheck-*", "aget-sanity-*", "aget-*check"]

    Skill_Dependency:
      skos:prefLabel: "Skill_Dependency"
      skos:definition: "A file, template, spec, or directory that a skill references and requires to exist at runtime"
      skos:example: ["templates/poc/RESEARCH_PROJECT_PLAN.template.md", "specs/CLI_VOCABULARY.md"]
      aget:validation: "All dependencies SHALL exist before skill deployment"

    Skill_Status:
      skos:prefLabel: "Skill_Status"
      skos:definition: "Lifecycle state of a skill: active (default), deprecated (superseded, scheduled for removal)"
      skos:example: ["active", "deprecated"]
      aget:source: "L603 Cross-Fleet Skill Evolution Survey"

    Deprecated_Skill:
      skos:prefLabel: "Deprecated_Skill"
      skos:definition: "A skill with status: deprecated — superseded by another skill, scheduled for removal in a future upgrade. Causes healthcheck warnings when present."
      skos:broader: "Skill_Status"
      skos:related: ["Skill_Name"]
      aget:source: "L603 (both supervisors converged: dormant skills waste context and cause model confusion)"
```

---

## Requirements

### CAP-SNAME-001: Canonical Naming Pattern

**Statement**: The SYSTEM shall ensure all AGET skills follow the `aget-{verb}-{noun}` naming pattern.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SNAME-001-01 | ubiquitous | The SYSTEM shall ensure skill names start with `aget-` prefix |
| CAP-SNAME-001-02 | ubiquitous | The SYSTEM shall ensure skill names follow `aget-{verb}-{noun}` structure |
| CAP-SNAME-001-03 | ubiquitous | The SYSTEM shall ensure verb is a single word describing the action |
| CAP-SNAME-001-04 | ubiquitous | The SYSTEM shall ensure noun is a single word (or hyphenated compound) describing the target |
| CAP-SNAME-001-05 | ubiquitous | The SYSTEM shall ensure all components are lowercase |
| CAP-SNAME-001-06 | event-driven | WHEN a verb's action is intrinsically unambiguous AND variants are expressed via command-line flags (not separate skills), THE SYSTEM shall permit the single-verb form `aget-{verb}` for names listed in the Single-Verb Exception Registry (§ below) |

**Canonical Pattern**:
```
aget-{verb}-{noun}
     │      │
     │      └── Target of action (health, lesson, project, state, etc.)
     │
     └── Action verb (check, record, create, save, review, etc.)
```

**Valid Examples**:
| Skill Name | Verb | Noun | Purpose |
|------------|------|------|---------|
| `aget-check-health` | check | health | Health inspection |
| `aget-check-kb` | check | kb | Knowledge base check |
| `aget-check-evolution` | check | evolution | Evolution directory check |
| `aget-check-sessions` | check | sessions | Sessions directory check |
| `aget-record-lesson` | record | lesson | Record L-doc |
| `aget-create-project` | create | project | Create PROJECT_PLAN |
| `aget-save-state` | save | state | Save workflow state |
| `aget-review-project` | review | project | Review PROJECT_PLAN |
| `aget-record-observation` | record | observation | Record observation |
| `aget-wake-up` | wake | up | Session initialization |
| `aget-wind-down` | wind | down | Session termination |
| `aget-file-issue` | file | issue | File GitHub issue |

---

### Single-Verb Exception Registry (CAP-SNAME-001-06)

Per CAP-SNAME-001-06, the following single-verb skill names are approved exceptions to the `aget-{verb}-{noun}` pattern. Each exception requires principal approval, a rationale for why the verb is intrinsically unambiguous, and a flag-based variant scheme that replaces the noun-suffix namespace.

| Skill Name | Verb | Rationale | Flag-Based Variants | Approved |
|------------|------|-----------|---------------------|----------|
| `aget-name` | name | Action is self-contained (generate structured entity name); target is always an identifier string | `--session`, `--agent`, `--l-doc` | SP-015, 2026-04-13 |
| `aget-ask` | ask | Action is self-contained (clarifying question generation); entropy-reduction outcome is the measurable product | `--clarification` (default), `--followup` | SP-018, 2026-04-18 |

**Adding new single-verb exceptions**: Requires (a) SP-NNN proposal documenting rationale, (b) principal approval recorded by date, (c) spec version bump, (d) corresponding test fixture update. Any new single-verb skill that bypasses this registry is a governance bypass.

---

### CAP-SNAME-002: Prohibited Patterns

**Statement**: The SYSTEM shall reject certain naming patterns for new skills.

**Pattern**: prohibitive

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SNAME-002-01 | prohibitive | The SYSTEM shall NOT accept `aget-{noun}check` pattern |
| CAP-SNAME-002-02 | prohibitive | The SYSTEM shall NOT accept `aget-healthcheck-*` pattern |
| CAP-SNAME-002-03 | prohibitive | The SYSTEM shall NOT accept `aget-sanity-*` pattern |
| CAP-SNAME-002-04 | prohibitive | The SYSTEM shall NOT accept compound verbs (e.g., `quickcheck`) |
| CAP-SNAME-002-05 | prohibitive | The SYSTEM shall NOT accept camelCase or PascalCase |

**Prohibited Patterns with Corrections**:

| Prohibited | Reason | Correct Form |
|------------|--------|--------------|
| `aget-healthcheck-evolution` | Compound verb | `aget-check-evolution` |
| `aget-sanity-check` | Legacy pattern | `aget-check-health` |
| `aget-healthcheck-kb` | Compound verb | `aget-check-kb` |
| `aget-healthcheck-sessions` | Compound verb | `aget-check-sessions` |
| `aget-quicksave` | Compound verb | `aget-save-state` |
| `aget-CreateProject` | CamelCase | `aget-create-project` |

---

### CAP-SNAME-003: Spec-to-Skill Synchronization

**Statement**: The SYSTEM shall ensure skill spec filenames match skill directory names.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SNAME-003-01 | ubiquitous | The SYSTEM shall ensure spec filename contains the exact skill name |
| CAP-SNAME-003-02 | ubiquitous | The SYSTEM shall ensure skill directory name matches the skill name |
| CAP-SNAME-003-03 | conditional | IF spec filename diverges from skill name, THEN the SYSTEM shall rename spec to match |

**Synchronization Rule**:
```
Spec: SKILL-NNN_{skill-name}.yaml
             └── Must match ───────┐
                                   ▼
Directory: .claude/skills/{skill-name}/
```

**Example**:
| Spec File | Skill Directory | Status |
|-----------|-----------------|--------|
| `SKILL-003_aget-check-health.yaml` | `.claude/skills/aget-check-health/` | ✅ Synchronized |
| `SKILL-004_aget-check-evolution.yaml` | `.claude/skills/aget-check-evolution/` | ✅ Synchronized |

---

### CAP-SDEP-001: Dependency Validation

**Statement**: The SYSTEM shall NOT deploy skills without validating that all referenced dependencies exist.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SDEP-001-01 | ubiquitous | The SYSTEM shall validate all file paths referenced in SKILL.md exist before deploying a skill |
| CAP-SDEP-001-02 | ubiquitous | IF a dependency is missing, the SYSTEM shall fail deployment with explicit error listing missing paths |
| CAP-SDEP-001-03 | conditional | IF a skill references a template, THEN the SYSTEM shall verify the template exists before deployment |
| CAP-SDEP-001-04 | conditional | IF a skill references a spec, THEN the SYSTEM shall verify the spec exists (stub acceptable) before deployment |
| CAP-SDEP-001-05 | conditional | IF a skill references a directory, THEN the SYSTEM shall verify the directory exists with README before deployment |

**Validation Command**:
```bash
# Extract and validate file paths from skill
python3 aget/validation/validate_skill_dependencies.py --skill .claude/skills/aget-create-project/
```

**Rationale**: L586 documented 8/8 broken skill dependencies. Skills referencing non-existent files fail at runtime. Validation at deployment prevents this failure class.

**Reference**: L586 (Skill Infrastructure Deployment Gap)

---

### CAP-SLIFE-001: Skill Lifecycle Governance

**Statement**: The SYSTEM shall support lifecycle state tracking through SKILL.md frontmatter fields.

**Pattern**: mixed (ubiquitous + event_driven + conditional)

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SLIFE-001-01 | ubiquitous | The SYSTEM shall include a `status` field in SKILL.md frontmatter with value `active` (default) or `deprecated` |
| CAP-SLIFE-001-02 | conditional | IF `status` is `deprecated`, THEN the SYSTEM shall include `superseded_by` in SKILL.md frontmatter referencing the canonical replacement skill name |
| CAP-SLIFE-001-03 | conditional | IF `status` is `deprecated`, THEN the SYSTEM shall include `deprecated_date` in SKILL.md frontmatter in YYYY-MM-DD format |
| CAP-SLIFE-001-04 | event_driven | WHEN healthcheck or validation tooling runs, the SYSTEM shall report deprecated skills that are still present with their `superseded_by` references |
| CAP-SLIFE-001-05 | event_driven | WHEN a deprecated skill is present, the SYSTEM shall NOT block operations — deprecated is a warning, not an error |
| CAP-SLIFE-001-06 | conditional | IF `superseded_by` references a skill that does not exist in `.claude/skills/`, THEN the SYSTEM shall warn that the replacement is missing |

**Frontmatter Schema**:
```yaml
# Active skill (default — status field optional when active)
---
name: aget-check-health
description: "..."
---

# Deprecated skill (all three fields required)
---
name: aget-healthcheck-evolution
status: deprecated
superseded_by: aget-check-evolution
deprecated_date: 2026-02-20
description: "..."
---
```

**Healthcheck Output**:
```
WARN: 3 deprecated skills present:
  - aget-healthcheck-evolution → superseded by aget-check-evolution
  - aget-healthcheck-kb → superseded by aget-check-kb
  - aget-healthcheck-sessions → superseded by aget-check-sessions
  Action: Remove deprecated skills or update to canonical names
```

**V-Tests**: See consolidated Verification Tests section below.

**Rationale**: L603 cross-fleet survey found dormant skills in both fleets. Supervisor 1 identified that legacy naming duplicates (e.g., `healthcheck-*` alongside `check-*`) waste context window tokens and cause model confusion — Claude Code may invoke the deprecated name instead of the canonical name. Both supervisors converged on deprecation marking as a quick win. Deprecation is a warning (not a block) to avoid disrupting agents that may still reference deprecated skills.

**Theoretical Basis**: Deprecation as a lifecycle phase follows standard software engineering practice. The warning-not-error approach follows AGET's ADR-008 progression (Advisory → Strict → Generator): deprecation starts as advisory, can become strict in future versions.

**Reference**: L603 (Cross-Fleet Skill Evolution Survey), ADR-008 (Advisory → Strict → Generator)

---

## Migration Guidance

### Legacy Name Migration

When encountering legacy skill names:

1. **Identify**: Check if name uses prohibited pattern
2. **Map**: Determine correct canonical name
3. **Update**: Rename skill directory
4. **Sync**: Update spec filename to match
5. **Propagate**: Update references in CLAUDE.md, SKILL_VOCABULARY.md

### Migration Table (v3.5.0)

| Legacy Name | Canonical Name | Migration Status |
|-------------|---------------|------------------|
| `aget-sanity-check` | `aget-check-health` | Complete |
| `aget-healthcheck-evolution` | `aget-check-evolution` | Complete |
| `aget-healthcheck-kb` | `aget-check-kb` | Complete |
| `aget-healthcheck-sessions` | `aget-check-sessions` | Complete |

---

## Validation

### Pre-Release Check

```bash
# Validate all skill directories follow naming convention
for skill in .claude/skills/aget-*/; do
  name=$(basename "$skill")
  if [[ ! "$name" =~ ^aget-[a-z]+-[a-z]+(-[a-z]+)?$ ]]; then
    echo "❌ Invalid skill name: $name"
  else
    echo "✅ Valid: $name"
  fi
done
```

### Spec-Skill Synchronization Check

```bash
# Verify spec filenames match skill directories
for spec in specs/skills/SKILL-*_aget-*.yaml; do
  skill_name=$(basename "$spec" | sed 's/SKILL-[0-9]*_//' | sed 's/.yaml//')
  if [[ ! -d ".claude/skills/$skill_name" ]]; then
    echo "❌ Spec $spec has no matching skill directory"
  else
    echo "✅ $skill_name synchronized"
  fi
done
```

---

## Verification Tests

| V-Test | Requirement | Method | Verification |
|--------|-------------|--------|--------------|
| V-SNAME-001 | CAP-SNAME-001-01 | automated | Validate all skill directories start with `aget-` prefix |
| V-SNAME-002 | CAP-SNAME-001-02 | automated | Validate all skill directories match `aget-{verb}-{noun}` regex pattern |
| V-SNAME-003 | CAP-SNAME-001-05 | automated | Validate all skill name components are lowercase |
| V-SNAME-004 | CAP-SNAME-002-01 | automated | Validate no skill directories use `aget-{noun}check` pattern |
| V-SNAME-005 | CAP-SNAME-002-05 | automated | Validate no skill directories use camelCase or PascalCase |
| V-SNAME-006 | CAP-SNAME-003-01 | automated | Validate spec filenames contain the exact skill name |
| V-SNAME-007 | CAP-SNAME-003-02 | automated | Validate skill directory names match spec-declared names |
| V-SNAME-008 | CAP-SDEP-001-01 | automated | Run validate_skill_dependencies.py and verify all referenced paths exist |
| V-SNAME-009 | CAP-SDEP-001-02 | automated | Deploy skill with missing dependency and verify deployment fails with error |
| V-SNAME-010 | CAP-SLIFE-001-01 | inspection | Inspect SKILL.md: `status` field present with valid value (`active` or `deprecated`) or absent (defaults to `active`) |
| V-SNAME-011 | CAP-SLIFE-001-02 | inspection | For deprecated skills: `superseded_by` field present and contains a valid `aget-{verb}-{noun}` name |
| V-SNAME-012 | CAP-SLIFE-001-03 | inspection | For deprecated skills: `deprecated_date` field present in YYYY-MM-DD format |
| V-SNAME-013 | CAP-SLIFE-001-04 | automated | Run healthcheck with deprecated skill present: output includes warning listing the skill and its replacement |
| V-SNAME-014 | CAP-SLIFE-001-05 | automated | Run healthcheck with deprecated skill present: exit code is 0 (warning) not non-zero (error) |
| V-SNAME-015 | CAP-SLIFE-001-06 | manual | Create deprecated skill with `superseded_by: aget-nonexistent`: validation warns replacement is missing |

---

## Authority Model

```yaml
authority:
  applies_to: "all_agents"

  governed_by:
    spec: "SKILL_NAMING_CONVENTION_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "name skills following canonical pattern"
      - "validate skill naming compliance"
      - "rename legacy skills to canonical names"

    requires_framework:
      - "changes to canonical naming pattern"
      - "new prohibited pattern additions"
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Naming Conventions (Software Engineering)"
  secondary:
    - "Cognitive Load Theory (predictable patterns reduce mental effort)"
    - "Convention over Configuration"
  reference: "L582 (Universal Skill Customization Preservation)"
```

**Rationale**: Consistent naming enables:
- Predictable discovery (`aget-check-*` for all health checks)
- Reliable automation (pattern matching in scripts)
- Reduced cognitive load (one pattern to remember)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.3.0 | 2026-03-18 | Renumber IDs to single-word domains (CAP-SNAME, CAP-SDEP, CAP-SLIFE). Add SYSTEM subject to all requirements. Add consolidated V-tests (V-SNAME-001 through V-SNAME-015). Add Authority Model section. |
| 1.2.0 | 2026-02-20 | Add CAP-SLIFE-001 (lifecycle governance with deprecation marking). Add Skill_Status and Deprecated_Skill vocabulary. Source: L603. |
| 1.1.0 | 2026-02-15 | Add CAP-SDEP-001 (dependency validation), Skill_Dependency vocabulary |
| 1.0.0 | 2026-02-15 | Initial specification from v3.5.0 Phase 2 findings |

---

*SKILL_NAMING_CONVENTION_SPEC v1.3.0*
*"aget-{verb}-{noun}: Consistent, predictable, discoverable."*
