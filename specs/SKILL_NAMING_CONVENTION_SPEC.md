# SKILL_NAMING_CONVENTION_SPEC

**Version**: 1.0.0
**Status**: Active
**Category**: Specification (Skills)
**Format Version**: 1.3
**Created**: 2026-02-15
**Author**: private-aget-framework-AGET
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
```

---

## Requirements

### CAP-SKILL-NAME-001: Canonical Naming Pattern

**Statement**: All AGET skills SHALL follow the `aget-{verb}-{noun}` naming pattern.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-SKILL-NAME-001 | ubiquitous | Skill names SHALL start with `aget-` prefix |
| R-SKILL-NAME-002 | ubiquitous | Skill names SHALL follow `aget-{verb}-{noun}` structure |
| R-SKILL-NAME-003 | ubiquitous | Verb SHALL be a single word describing the action |
| R-SKILL-NAME-004 | ubiquitous | Noun SHALL be a single word (or hyphenated compound) describing the target |
| R-SKILL-NAME-005 | ubiquitous | All components SHALL be lowercase |

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
| `aget-capture-observation` | capture | observation | Capture observation |
| `aget-wake-up` | wake | up | Session initialization |
| `aget-wind-down` | wind | down | Session termination |
| `aget-file-issue` | file | issue | File GitHub issue |

---

### CAP-SKILL-NAME-002: Prohibited Patterns

**Statement**: Certain naming patterns SHALL NOT be used for new skills.

**Pattern**: prohibitive

| ID | Pattern | Statement |
|----|---------|-----------|
| R-SKILL-NAME-010 | prohibitive | Skill names SHALL NOT use `aget-{noun}check` pattern |
| R-SKILL-NAME-011 | prohibitive | Skill names SHALL NOT use `aget-healthcheck-*` pattern |
| R-SKILL-NAME-012 | prohibitive | Skill names SHALL NOT use `aget-sanity-*` pattern |
| R-SKILL-NAME-013 | prohibitive | Skill names SHALL NOT use compound verbs (e.g., `quickcheck`) |
| R-SKILL-NAME-014 | prohibitive | Skill names SHALL NOT use camelCase or PascalCase |

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

### CAP-SKILL-NAME-003: Spec-to-Skill Synchronization

**Statement**: Skill spec filenames SHALL match skill directory names.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-SKILL-NAME-020 | ubiquitous | Spec filename SHALL contain the exact skill name |
| R-SKILL-NAME-021 | ubiquitous | Skill directory name SHALL match the skill name |
| R-SKILL-NAME-022 | conditional | IF spec filename diverges from skill name, THEN rename spec to match |

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
| `SKILL-004_aget-healthcheck-evolution.yaml` | `.claude/skills/aget-check-evolution/` | ❌ Diverged |

**Correction**: Rename spec to `SKILL-004_aget-check-evolution.yaml`

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
| 1.0.0 | 2026-02-15 | Initial specification from v3.5.0 Phase 2 findings |

---

*SKILL_NAMING_CONVENTION_SPEC v1.0.0*
*"aget-{verb}-{noun}: Consistent, predictable, discoverable."*
