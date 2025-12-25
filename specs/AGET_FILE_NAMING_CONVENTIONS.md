# AGET File Naming Conventions

**Version**: 1.0.0
**Date**: 2025-12-20
**Status**: CANONICAL
**Location**: aget/specs/AGET_FILE_NAMING_CONVENTIONS.md

---

## Purpose

This specification defines canonical file naming conventions for all AGET framework artifacts. It consolidates patterns previously scattered across AGET_CONTROLLED_VOCABULARY.md, TEMPLATE_STRUCTURE_GUIDE.md, and NAMING_CONVENTIONS.md.

**Scope**: File and directory naming within AGET repositories. Does not cover:
- Python package naming (see PEP 8, PEP 423)
- Git branch naming
- External artifact naming

---

## Quick Reference

| Artifact Type | Pattern | Example |
|---------------|---------|---------|
| Specs | `{NAME}_SPEC_v{M}.{m}.yaml` | `WORKER_TEMPLATE_SPEC_v1.0.yaml` |
| PROJECT_PLANs | `PROJECT_PLAN_{name}_v{M}.{m}.md` | `PROJECT_PLAN_file_naming_v1.0.md` |
| ADRs | `ADR-{NNN}-{kebab-case}.md` | `ADR-001-initial-architecture.md` |
| L-docs | `L{NNN}_{snake_case}.md` | `L338_gate_verification.md` |
| Sessions | `SESSION_{YYYY-MM-DD}_{snake_case}.md` | `SESSION_2025-12-20_research.md` |
| SOPs | `SOP_{snake_case}.md` | `SOP_release_process.md` |
| Patterns | `PATTERN_{snake_case}.md` | `PATTERN_step_back_review.md` |
| Python code | `{snake_case}.py` | `validate_file_naming.py` |
| Directories | `{visibility}-{identifier}-{type}` | `private-supervisor-AGET` |

---

## Category A: Versioned Artifacts

Artifacts that evolve through discrete versions. Version indicates document evolution, not content topic.

### Pattern

```
{TYPE}_{NAME}_v{M}.{m}[-{prerelease}].{ext}

TYPE:       SCREAMING_CASE (e.g., SPEC, PROJECT_PLAN, MIGRATION_MANIFEST)
NAME:       SCREAMING_SNAKE_CASE or snake_case (e.g., WORKER_TEMPLATE, file_naming)
v:          Literal lowercase "v"
M:          Major version (breaking changes)
m:          Minor version (additions, non-breaking)
prerelease: Optional: alpha, beta, rc1, etc.
ext:        yaml, md, json
```

### Examples

```
✅ WORKER_TEMPLATE_SPEC_v1.0.yaml
✅ PROJECT_PLAN_file_naming_conventions_v1.0.md
✅ AGET_SPEC_FORMAT_v1.1.md
✅ RELEASE_NOTES_v2.0-alpha.md
✅ MIGRATION_MANIFEST_v1.0.md
✅ session_metadata_v1.0.yaml (schemas)
```

### Artifact Types

| Type Prefix | Purpose | Versioned? |
|-------------|---------|------------|
| `*_SPEC_` | Formal specifications | Always |
| `PROJECT_PLAN_` | Gated execution plans | Always |
| `MIGRATION_MANIFEST_` | Migration tracking | Always |
| `RELEASE_NOTES_` | Release documentation | Always |
| `*_GUIDE_` | Comprehensive guides | Usually |

### Version Semantics

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change | Major (M) | v1.0 → v2.0 |
| New content, compatible | Minor (m) | v1.0 → v1.1 |
| Typo fix, clarification | Minor (m) | v1.1 → v1.2 |
| Pre-release | Suffix | v2.0-alpha → v2.0-beta → v2.0 |

### Archive Policy

Only current version in active directory. Previous versions move to `archive/`:
```
specs/
├── WORKER_TEMPLATE_SPEC_v2.0.yaml  ← Current
└── archive/
    ├── WORKER_TEMPLATE_SPEC_v1.0.yaml
    └── WORKER_TEMPLATE_SPEC_v1.1.yaml
```

---

## Category B: Sequenced Artifacts

Artifacts identified by sequence number. Number is permanent ID, not version.

### Pattern

```
{PREFIX}{NNN}_{snake_case}.md

PREFIX:  L (learnings), ADR- (decisions)
NNN:     3-digit zero-padded sequence (001-999)
```

### Examples

```
✅ L001_initial_setup.md
✅ L338_gate_verification_requirements.md
✅ ADR-001-initial-architecture.md
✅ ADR-012-migration-strategy.md
```

### Artifact Types

| Prefix | Purpose | Sequence Scope |
|--------|---------|----------------|
| `L` | Learning documents | Per-agent (resets per agent) |
| `ADR-` | Architecture Decision Records | Per-repository |

### Sequence Rules

1. Numbers are **permanent** - never reuse after deletion
2. Numbers are **sequential** - no gaps in new assignments
3. Descriptions can change - number stays fixed
4. Cross-references use number: "See L338" not "See gate verification"

### Supersession

When a learning is superseded:
```markdown
# L042: Original Topic

**Status**: SUPERSEDED by L187

[Original content preserved for history]
```

---

## Category C: Temporal Artifacts

Artifacts identified by date. Date is creation timestamp, serves as unique ID.

### Pattern

```
{TYPE}_{YYYY-MM-DD}_{snake_case}.md

TYPE:  SESSION, CHECKPOINT, FINDING
DATE:  ISO 8601 date format
```

### Examples

```
✅ SESSION_2025-12-20_file_naming_research.md
✅ CHECKPOINT_2025-12-20_gate_1_complete.md
✅ FINDING_2025-12-19_memory_architecture.md
```

### Artifact Types

| Type | Purpose | Retention |
|------|---------|-----------|
| `SESSION_` | Session logs and notes | Archive after 90 days |
| `CHECKPOINT_` | Gate completion records | Keep with project |
| `FINDING_` | Discovery documentation | Permanent |

### Multiple Same-Day Artifacts

If multiple artifacts of same type on same day, add sequence:
```
SESSION_2025-12-20_morning_research.md
SESSION_2025-12-20_afternoon_review.md
```

Or use timestamp:
```
SESSION_2025-12-20T0930_research.md
SESSION_2025-12-20T1400_review.md
```

---

## Category D: Stable Artifacts

Artifacts that rarely change and don't need version tracking.

### Pattern

```
{TYPE}_{snake_case}.md

TYPE:  SOP, PATTERN, TEMPLATE, GUIDE (when not versioned)
```

### Examples

```
✅ SOP_release_process.md
✅ SOP_pre_proposal_kb_audit.md
✅ PATTERN_step_back_review_kb.md
✅ KB_AUDIT_TEMPLATE.md
✅ SESSION_HANDOFF_GUIDE.md
```

### Artifact Types

| Type | Purpose | When to Version |
|------|---------|-----------------|
| `SOP_` | Standard operating procedures | If breaking changes |
| `PATTERN_` | Reusable patterns | If breaking changes |
| `*_TEMPLATE` | Document templates | If structure changes |

### Promotion to Versioned

When a stable artifact needs versioning:
1. Rename: `SOP_release.md` → `SOP_release_v1.0.md`
2. Update references
3. Document in changelog

---

## Category E: Code Files

Python and other code files follow language conventions.

### Pattern (Python)

```
{snake_case}.py

Per PEP 8: lowercase with underscores
```

### Examples

```
✅ validate_file_naming.py
✅ wake_protocol.py
✅ version_bump.py
✅ conftest.py
```

### Migration Scripts

Migration scripts may include version in name for clarity:
```
✅ migrate_v20_to_v21.py
✅ aget_v21_migration.py
```

This is acceptable as it describes the migration target, not file version.

---

## Directory Naming

### Agent Directories

```
{visibility}-{identifier}-{type}

visibility:  private, public, template
identifier:  kebab-case descriptive name
type:        aget (read-only) or AGET (action-taking)
```

### Examples

```
✅ template-worker-aget
✅ private-supervisor-AGET
✅ public-OpenAI-DeepResearch-aget
```

### Internal Directories

Standard internal directories use lowercase:
```
✅ .aget/
✅ .aget/evolution/
✅ .aget/specs/
✅ docs/
✅ planning/
✅ findings/
```

---

## Case Convention Summary

| Element | Convention | Example |
|---------|------------|---------|
| TYPE prefix | SCREAMING_CASE | `PROJECT_PLAN`, `SPEC`, `SOP` |
| Descriptive name (files) | snake_case | `file_naming_conventions` |
| Descriptive name (dirs) | kebab-case | `private-supervisor-AGET` |
| Sequence numbers | 3-digit padded | `001`, `012`, `338` |
| Version prefix | lowercase v | `_v1.0`, `_v2.1-alpha` |
| Date format | ISO 8601 | `2025-12-20` |

---

## Decision Tree: Which Category?

```
Is this a formal specification or plan?
├── YES → Category A (Versioned): {TYPE}_{NAME}_v{M}.{m}.md
└── NO
    ↓
Does it have a sequence number (L###, ADR-###)?
├── YES → Category B (Sequenced): {PREFIX}{NNN}_{name}.md
└── NO
    ↓
Is it tied to a specific date/session?
├── YES → Category C (Temporal): {TYPE}_{YYYY-MM-DD}_{name}.md
└── NO
    ↓
Is it code?
├── YES → Category E (Code): {snake_case}.py
└── NO → Category D (Stable): {TYPE}_{name}.md
```

---

## Anti-Patterns

### Anti-Pattern 1: Inconsistent Version Format

```
❌ SPEC_v1.yaml           # Missing minor version
❌ SPEC-v1.0.yaml         # Hyphen instead of underscore
❌ SPEC.v1.0.yaml         # Dot instead of underscore
❌ SPECv1.0.yaml          # No separator
❌ SPEC_V1.0.yaml         # Uppercase V
✅ SPEC_v1.0.yaml         # Correct
```

### Anti-Pattern 2: Version in Temporal Artifacts

```
❌ SESSION_2025-12-20_v1.0.md    # Date + version = redundant
❌ L338_v1.0_gate.md             # L-docs don't version
✅ SESSION_2025-12-20_topic.md   # Date is ID
✅ L338_gate_verification.md     # L-number is ID
```

### Anti-Pattern 3: Wrong Case Convention

```
❌ project_plan_naming.md        # TYPE should be SCREAMING
❌ PROJECT-PLAN-naming.md        # Hyphen in filename
❌ ProjectPlan_naming.md         # PascalCase
✅ PROJECT_PLAN_naming_v1.0.md   # Correct
```

### Anti-Pattern 4: Multiple Versions in Active Directory

```
❌ specs/SPEC_v1.0.yaml
❌ specs/SPEC_v2.0.yaml          # Both in specs/
❌ specs/SPEC_v3.0.yaml

✅ specs/SPEC_v3.0.yaml          # Current only
✅ specs/archive/SPEC_v1.0.yaml  # Old in archive
✅ specs/archive/SPEC_v2.0.yaml
```

### Anti-Pattern 5: Spaces or Special Characters

```
❌ Project Plan v1.0.md          # Spaces
❌ PROJECT_PLAN_(draft).md       # Parentheses
❌ SPEC_v1.0[final].yaml         # Brackets
✅ PROJECT_PLAN_draft_v0.1.md    # Underscores only
```

---

## Validation

### Manual Checklist

Before committing a new artifact:
- [ ] Identified correct category (A-E)
- [ ] Used correct pattern for category
- [ ] TYPE prefix is SCREAMING_CASE
- [ ] Descriptive name is snake_case
- [ ] Version format is `_v{M}.{m}` (if versioned)
- [ ] No spaces or special characters
- [ ] Extension matches content type

### Automated Validation

```bash
# Run file naming validator
python3 .aget/tools/validate_file_naming.py <path>
```

---

## Grandfathered Exceptions

The following existing files are grandfathered and don't require renaming:

| File | Reason |
|------|--------|
| `PROJECT_PLAN_v2.10_capability_architecture.md` | Topic version without doc version (pre-standard) |
| `PROJECT_PLAN_v2.10_correction_template_coordination.md` | Topic version without doc version (pre-standard) |
| `ROADMAP_v2.md` | Major-only version (legacy) |

New files MUST follow this specification.

---

## References

- AGET_CONTROLLED_VOCABULARY.md - Terminology (now references this spec)
- TEMPLATE_STRUCTURE_GUIDE.md - Directory structure (now references this spec)
- NAMING_CONVENTIONS.md - Entity naming (separate concern)
- PEP 8 - Python code style
- PEP 423 - Python package naming

---

## Changelog

### v1.0.0 (2025-12-20)

- Initial consolidated specification
- Defined 5 categories (A-E)
- Added pre-release version support
- Documented anti-patterns
- Added grandfathered exceptions
- Created decision tree

---

*AGET_FILE_NAMING_CONVENTIONS.md — Canonical file naming for AGET framework*
