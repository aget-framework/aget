# AGET File Naming Conventions

**Version**: 2.1.0
**Date**: 2026-01-04
**Status**: CANONICAL
**Location**: aget/specs/AGET_FILE_NAMING_CONVENTIONS.md

---

## Purpose

This specification defines canonical file naming conventions for all AGET framework artifacts. It consolidates patterns previously scattered across AGET_CONTROLLED_VOCABULARY.md, TEMPLATE_STRUCTURE_GUIDE.md, and NAMING_CONVENTIONS.md.

**Scope**: File, directory, git branch, and git tag naming within AGET repositories. Does not cover:
- Python package naming (see PEP 8, PEP 423)
- External artifact naming

---

## Quick Reference

| Cat | Artifact Type | Pattern | Example |
|-----|---------------|---------|---------|
| A | Specs | `{NAME}_SPEC_v{M}.{m}.yaml` | `WORKER_TEMPLATE_SPEC_v1.0.yaml` |
| A | PROJECT_PLANs | `PROJECT_PLAN_{name}_v{M}.{m}.md` | `PROJECT_PLAN_file_naming_v1.0.md` |
| B | ADRs | `ADR-{NNN}-{kebab-case}.md` | `ADR-001-initial-architecture.md` |
| B | L-docs | `L{NNN}_{snake_case}.md` | `L338_gate_verification.md` |
| C | Sessions | `SESSION_{YYYY-MM-DD}_{snake_case}.md` | `SESSION_2025-12-20_research.md` |
| D | SOPs | `SOP_{snake_case}.md` | `SOP_release_process.md` |
| D | Runbooks | `RUNBOOK_{snake_case}.md` | `RUNBOOK_deployment.md` |
| D | Playbooks | `PLAYBOOK_{snake_case}.md` | `PLAYBOOK_incident_response.md` |
| D | Patterns | `PATTERN_{snake_case}.md` | `PATTERN_step_back_review.md` |
| E | Python code | `{snake_case}.py` | `validate_file_naming.py` |
| F | Open-source | `{EXACT_NAME}` | `README.md`, `LICENSE` |
| G | Requirements | `R-{DOMAIN}-{NNN}` | `R-REL-006` |
| H | Change Proposals | `CP-{NNN}_{name}.md` | `CP-001_capability.md` |
| I | Protocols | `{NAME}_PROTOCOL.md` | `WAKE_UP_PROTOCOL.md` |
| J | Checklists | `{NAME}_CHECKLIST.md` | `RELEASE_CHECKLIST.md` |
| — | Directories | `{visibility}-{identifier}-{type}` | `my-supervisor-AGET` |

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

TYPE:  SOP, RUNBOOK, PLAYBOOK, PATTERN, TEMPLATE, GUIDE (when not versioned)
```

### Examples

```
✅ SOP_release_process.md
✅ SOP_pre_proposal_kb_audit.md
✅ RUNBOOK_deployment.md
✅ RUNBOOK_database_migration.md
✅ PLAYBOOK_incident_response.md
✅ PLAYBOOK_security_breach.md
✅ PATTERN_step_back_review_kb.md
✅ KB_AUDIT_TEMPLATE.md
✅ SESSION_HANDOFF_GUIDE.md
```

### Artifact Types

| Type | Purpose | When to Version |
|------|---------|-----------------|
| `SOP_` | Standard operating procedures (universal) | If breaking changes |
| `RUNBOOK_` | Operational procedures with decision points (parameterized) | If breaking changes |
| `PLAYBOOK_` | Strategic guidelines for scenarios (adaptive) | If breaking changes |
| `PATTERN_` | Reusable patterns | If breaking changes |
| `*_TEMPLATE` | Document templates | If structure changes |

### EKO Artifact Distinctions (L451)

Per the Executable Knowledge Ontology:

| Artifact | Determinism | Reusability | Example |
|----------|-------------|-------------|---------|
| `SOP_` | Deterministic | Universal | `SOP_release_process.md` |
| `RUNBOOK_` | Deterministic | Parameterized | `RUNBOOK_deployment.md` |
| `PLAYBOOK_` | Syllogistic | Parameterized | `PLAYBOOK_incident_response.md` |

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

## Category F: Standard Open-Source Files

Community-standard files that follow external conventions, NOT AGET patterns. Per L439.

### Pattern

```
{EXACT_COMMUNITY_NAME}

No AGET prefix. Use exact names expected by GitHub, package managers, and community tools.
```

### Standard Files

| File | Convention Source | Required? | Notes |
|------|------------------|-----------|-------|
| `README.md` | GitHub | Yes | Repository root |
| `LICENSE` | OSI/GitHub | Yes | No extension preferred |
| `CHANGELOG.md` | Keep a Changelog | Yes | Semantic versioning |
| `CONTRIBUTING.md` | GitHub | Recommended | Contribution guide |
| `CODE_OF_CONDUCT.md` | Contributor Covenant | Recommended | Community standards |
| `SECURITY.md` | GitHub Security Advisories | Recommended | Vulnerability reporting |
| `UPGRADING.md` | Package managers | If applicable | Version migration |
| `.gitignore` | Git | Yes | Standard patterns |
| `requirements.txt` | pip | If Python | Dependencies |
| `pyproject.toml` | PEP 517/518 | If Python | Modern packaging |

### Examples

```
✅ README.md
✅ LICENSE
✅ CHANGELOG.md
✅ CONTRIBUTING.md
✅ CODE_OF_CONDUCT.md
✅ SECURITY.md
❌ AGET_README.md         # Don't prefix
❌ LICENSE.md             # No extension
❌ CHANGE_LOG.md          # Exact spelling
```

### Validation Exception

Validators MUST whitelist Category F files and NOT flag them as naming violations.

---

## Category G: Requirement Documents

Formal requirements using domain-prefixed identifiers.

### Pattern

```
R-{DOMAIN}-{NNN}

R:       Literal "R" prefix
DOMAIN:  3-4 letter domain code (see Domain Codes Registry)
NNN:     3-digit sequence within domain
```

### Examples

```
✅ R-REL-001    # Release requirement 001
✅ R-REL-006    # Release requirement 006 (manager migration)
✅ R-TPL-001    # Template requirement 001
✅ R-WAKE-003   # Wake protocol requirement 003
✅ R-SANITY-007 # Sanity check requirement 007
```

### Domain Codes Registry

| Code | Domain | Scope |
|------|--------|-------|
| `REL` | Release | Release process, versioning |
| `TPL` | Template | Template structure, compliance |
| `WAKE` | Wake Protocol | Session initialization |
| `WIND` | Wind-down Protocol | Session close |
| `SANITY` | Sanity Checks | Housekeeping, validation |
| `CLI` | CLI Settings | CLAUDE.md, AGENTS.md |
| `SPEC` | Specifications | Spec format, compliance |
| `DOC` | Documentation | README, guides |
| `LIC` | License | License compliance |
| `ORG` | Organization | GitHub org, homepage |
| `TEST` | Testing | Contract tests, V-tests |
| `SEC` | Security | Security requirements |
| `PP` | Project Plans | PROJECT_PLAN format |
| `VOC` | Vocabulary | SKOS, controlled terms |
| `NAME` | Naming | File/entity naming |
| `MEM` | Memory | L-docs, knowledge |
| `HOM` | Homepage | Org homepage messaging |

### Requirement Document Files

Requirements are typically embedded in specs, not standalone files:
```yaml
# In AGET_RELEASE_SPEC.md
requirements:
  - id: R-REL-006
    text: "Managing agent MUST update version BEFORE releasing managed repos"
    rationale: "Prevents version drift (L440)"
```

---

## Category H: Change Proposals

Formal proposals for significant changes.

### Pattern

```
CP-{NNN}_{snake_case}.md

CP:   Literal "CP" prefix
NNN:  3-digit sequence
```

### Examples

```
✅ CP-001_capability_composition.md
✅ CP-002_fleet_communication.md
✅ CP-003_memory_architecture.md
```

### Status Lifecycle

```
DRAFT → PROPOSED → ACCEPTED/REJECTED → IMPLEMENTED/WITHDRAWN
```

---

## Category I: Protocol Documents

Reusable protocols for repeated processes.

### Pattern

```
{NAME}_PROTOCOL.md

NAME:  SCREAMING_SNAKE_CASE
```

### Examples

```
✅ WAKE_UP_PROTOCOL.md
✅ WIND_DOWN_PROTOCOL.md
✅ SESSION_HANDOFF_PROTOCOL.md
✅ KB_AUDIT_PROTOCOL.md
```

### Distinction from SOPs

| Type | Purpose | Scope |
|------|---------|-------|
| `*_PROTOCOL.md` | Step-by-step execution sequence | Narrow, focused |
| `SOP_*.md` | Comprehensive operating procedure | Broad, policy-inclusive |

---

## Category J: Checklists

Verification and compliance checklists.

### Pattern

```
{NAME}_CHECKLIST.md

NAME:  SCREAMING_SNAKE_CASE
```

### Examples

```
✅ RELEASE_VERIFICATION_CHECKLIST.md
✅ MIGRATION_CHECKLIST.md
✅ TEMPLATE_COMPLIANCE_CHECKLIST.md
✅ PRE_RELEASE_CHECKLIST.md
```

### Checklist Format

```markdown
## {Checklist Name}

### Section 1
- [ ] Item 1
- [ ] Item 2

### Section 2
- [ ] Item 3
```

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
✅ my-supervisor-AGET
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
| Descriptive name (dirs) | kebab-case | `my-supervisor-AGET` |
| Sequence numbers | 3-digit padded | `001`, `012`, `338` |
| Version prefix | lowercase v | `_v1.0`, `_v2.1-alpha` |
| Date format | ISO 8601 | `2025-12-20` |

---

## Git Branch Naming

### Pattern

```
{type}/{scope}-{description}

type:        feature, fix, docs, refactor, release, hotfix
scope:       Optional: gate number, issue number, or component
description: kebab-case summary
```

### Examples

```
✅ feature/gate-1-naming-conventions
✅ feature/issue-33-naming-expansion
✅ fix/validator-whitelist
✅ docs/release-notes-v3.2
✅ release/v3.2.0
✅ hotfix/l440-manager-version
```

### Branch Type Rules

| Type | Purpose | Merge Target |
|------|---------|--------------|
| `feature/` | New functionality | main |
| `fix/` | Bug fixes | main |
| `docs/` | Documentation only | main |
| `refactor/` | Code restructuring | main |
| `release/` | Release preparation | main |
| `hotfix/` | Urgent production fix | main + release |

---

## Git Tag Naming

### Pattern

```
v{M}.{m}.{p}[-{prerelease}]

v:          Literal lowercase "v"
M:          Major version
m:          Minor version
p:          Patch version
prerelease: Optional: alpha, beta, rc1, etc.
```

### Examples

```
✅ v3.0.0
✅ v3.1.0
✅ v3.2.0-alpha
✅ v3.2.0-beta.1
✅ v3.2.0-rc1
✅ v3.2.0
```

### Tag Rules

1. Tags are **immutable** — never delete or move
2. Tags must match version in `version.json`
3. Pre-release tags precede stable: `v3.2.0-alpha` → `v3.2.0-beta` → `v3.2.0`
4. Annotated tags preferred: `git tag -a v3.2.0 -m "Release v3.2.0"`

---

## Decision Tree: Which Category?

```
Is this a community-standard file (README, LICENSE, CHANGELOG)?
├── YES → Category F (Open-Source): {EXACT_NAME}
└── NO
    ↓
Is this a formal specification or plan?
├── YES → Category A (Versioned): {TYPE}_{NAME}_v{M}.{m}.md
└── NO
    ↓
Does it have a sequence number (L###, ADR-###, R-XXX-###, CP-###)?
├── L### or ADR-### → Category B (Sequenced): {PREFIX}{NNN}_{name}.md
├── R-XXX-### → Category G (Requirements): R-{DOMAIN}-{NNN}
├── CP-### → Category H (Change Proposals): CP-{NNN}_{name}.md
└── NO
    ↓
Is it tied to a specific date/session?
├── YES → Category C (Temporal): {TYPE}_{YYYY-MM-DD}_{name}.md
└── NO
    ↓
Is it code?
├── YES → Category E (Code): {snake_case}.py
└── NO
    ↓
Is it a protocol (step-by-step execution)?
├── YES → Category I (Protocol): {NAME}_PROTOCOL.md
└── NO
    ↓
Is it a checklist?
├── YES → Category J (Checklist): {NAME}_CHECKLIST.md
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

### v2.1.0 (2026-01-04)

- Added RUNBOOK and PLAYBOOK to Category D (Stable Artifacts)
- Added EKO Artifact Distinctions table (L451)
- Updated Quick Reference with new artifact types
- Aligns with VOCABULARY_SPEC v1.1.1 (EKO terms)

### v2.0.0 (2026-01-04)

- **Breaking**: Expanded from 5 to 10 categories (A-J)
- Added Category F: Standard Open-Source Files (L439)
- Added Category G: Requirement Documents (R-XXX-NNN)
- Added Category H: Change Proposals (CP-NNN)
- Added Category I: Protocol Documents (*_PROTOCOL.md)
- Added Category J: Checklists (*_CHECKLIST.md)
- Added Domain Codes Registry (17 domains)
- Added Git Branch Naming section
- Added Git Tag Naming section
- Updated Decision Tree for new categories
- Updated Quick Reference with category column

### v1.0.0 (2025-12-20)

- Initial consolidated specification
- Defined 5 categories (A-E)
- Added pre-release version support
- Documented anti-patterns
- Added grandfathered exceptions
- Created decision tree

---

*AGET_FILE_NAMING_CONVENTIONS.md — Canonical file naming for AGET framework*
