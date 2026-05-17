# Template AGENTS.md Structure Specification

**Version**: 1.0.0
**Status**: Active (canonical — promoted from Draft via ACC-001 Gate 0 / PP-040 Q3 / SP-028 Q2 authorization 2026-05-16T~18:30Z)
**Category**: Standards (Template Governance)
**Format Version**: 1.3
**Created**: 2026-03-02
**Updated**: 2026-05-16T~18:30Z (canonical promotion via ACC-001 Gate 0 — direct execution per Option B; `/aget-enhance-spec` skill-fit gap captured as observation candidate at ACC-001 Gate 9)
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/TEMPLATE_AGENTS_MD_SPEC.md` (canonical in `aget-framework/aget` public repo; promoted from private `./specs/` per ACC-001 Gate 0)
**Change Origin**: PROJECT_PLAN_cli_feature_adoption_remediation_v1.0.md (Gate 1)
**Related Specs**: AGET_TEMPLATE_SPEC (CAP-TPL-006-03, CAP-TPL-008-01), AGET_5D_COMPONENTS_SPEC (CAP-PERSONA-005-05)
**Consumed by**: PROPOSAL_aget-enhance-config.md (SP-027) §Inheritable substrate ; PROPOSAL_aget-check-config.md (SP-028) §Dependencies + Tier 1 spec authority ; PROJECT_PLAN_aget_check_config_skill_v1.0.md (ACC-001) — Tier 1 spec authority

---

## Abstract

This specification defines required structural sections for template AGENTS.md files. Existing specs (AGET_TEMPLATE_SPEC) govern AGENTS.md existence and size but not internal structure. This spec fills that gap by codifying governance patterns validated by L596 (100% behavioral compliance in production) and informed by L621 (external best practices favoring compact, structured AGENTS.md over comprehensive, long files).

## Motivation

A fleet CLI scan (2026-03-02) revealed that the smallest AGENTS.md (CLI-AGET, 256 lines) contains governance patterns absent from larger agents and all 12 templates. Gate -1 of this project confirmed: no spec defines required AGENTS.md sections. Existing specs treat AGENTS.md as a container (exists, has version tag, stays under size limit) without specifying what constitutes a well-formed behavior specification.

### Evidence

| Finding | Source | Gate |
|---------|--------|------|
| 0/12 templates have Skill Routing tables | G0.1 audit | Gate 0 |
| 3/12 templates have Prohibitive Constraints (advisor-derived only) | G0.1 audit | Gate 0 |
| 3/12 templates have Write Scope (advisor-derived only) | G0.1 audit | Gate 0 |
| Skill Routing table = 100% behavioral compliance | L596 (CLI-AGET validation) | — |
| Prohibitive Constraints = 100% behavioral compliance | L596 (CLI-AGET validation) | — |
| No spec defines required AGENTS.md sections | Gate -1 governing spec inventory | Gate -1 |
| R-AMS-001 does not exist — actual ceiling is CAP-TPL-008-01 (40,000 chars) | Gate -1 finding | Gate -1 |
| Two template generations: v2-era (have some patterns) vs v3-era (minimal) | G0.1 audit | Gate 0 |

## Scope

**Applies to**: All 12 template AGENTS.md files in `aget-framework/template-*/AGENTS.md`.

**Complements** (does not replace):
- CAP-TPL-006-03: "The SYSTEM shall maintain AGENTS.md as behavior specification" (existence)
- CAP-TPL-008-01: "The SYSTEM shall limit AGENTS.md to 40000 characters" (size ceiling)
- CAP-TPL-008-02: "IF AGENTS.md exceeds 35000 characters THEN emit Size_Warning" (size warning)
- INV-TPL-003: "The SYSTEM shall maintain CLAUDE.md as symlink to AGENTS.md" (symlink)

**This spec adds**: Structural requirements defining what "behavior specification" means — required sections that serve specific governance purposes.

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "template_agents_md"
    version: "1.0.0"
    inherits: "aget_core"

  template_agents_md:
    Governance_Section:
      skos:definition: "A named section within AGENTS.md that serves a specific governance purpose — identity, routing, constraint, or boundary definition."
      skos:related: ["Behavior_Specification", "Template_AGENTS_MD"]

    Skill_Routing_Table:
      skos:definition: "A table within AGENTS.md that maps agent tasks or action categories to specific skills, enabling deterministic skill invocation."
      skos:related: ["Agent_Skill", "Governance_Section"]
      skos:note: "L596 validated 100% behavioral compliance with this pattern in CLI-AGET production."

    Prohibitive_Constraint:
      skos:definition: "An explicit statement of what the agent MUST NOT do, using prohibitive language (NEVER, shall NOT, CANNOT)."
      skos:related: ["Governance_Section", "Write_Scope"]
      skos:note: "L596 validated 100% behavioral compliance with this pattern in CLI-AGET production."

    Write_Scope:
      skos:definition: "An explicit boundary definition specifying where the agent is allowed and not allowed to write, preventing cross-KB contamination."
      skos:related: ["Governance_Section", "Prohibitive_Constraint"]
```

---

## Requirements

### CAP-TAS-001: Required Sections

Template AGENTS.md files SHALL contain the following governance sections to constitute a well-formed behavior specification.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TAS-001-01 | ubiquitous | The template AGENTS.md SHALL contain a version tag line matching `@aget-version: X.Y.Z` |
| R-TAS-001-02 | ubiquitous | The template AGENTS.md SHALL contain a North Star or Purpose section stating the agent's primary purpose |
| R-TAS-001-03 | ubiquitous | The template AGENTS.md SHALL contain a Skill Routing section mapping tasks to skills |
| R-TAS-001-04 | ubiquitous | The template AGENTS.md SHALL contain a Prohibitive Constraints section listing explicit NEVER/CANNOT rules |
| R-TAS-001-05 | ubiquitous | The template AGENTS.md SHALL contain a Write Scope section defining allowed and prohibited write targets |
| R-TAS-001-06 | ubiquitous | The template AGENTS.md SHALL contain an Agent Identity section with name, type, and domain |

**Enforcement**: Template conformance check (future validator). Manual review at release gate.

**Rationale**: L596 demonstrated 100% behavioral compliance for Skill Routing and Prohibitive Constraints in production. These patterns are proven, not speculative. Adding them to templates ensures new agents start with governance infrastructure.

### CAP-TAS-002: Section Minimum Content

Each required section SHALL contain substantive content, not just a heading.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TAS-002-01 | conditional | IF Skill Routing section exists THEN it SHALL contain a table with at least 2 task-to-skill mappings |
| R-TAS-002-02 | conditional | IF Prohibitive Constraints section exists THEN it SHALL contain at least 1 explicit NEVER or CANNOT rule |
| R-TAS-002-03 | conditional | IF Write Scope section exists THEN it SHALL specify at least 1 allowed AND 1 prohibited write target |

**Enforcement**: Content presence check (grep-based validator).

**Rationale**: L555 (scaffold vs substance gap) showed that empty sections create false confidence. Minimum content requirements prevent ceremonial compliance.

### CAP-TAS-003: Size Guidance

Template AGENTS.md files SHOULD favor compact, structured content over comprehensive, long content.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TAS-003-01 | ubiquitous | The template AGENTS.md SHALL NOT exceed 40,000 characters (per CAP-TPL-008-01) |
| R-TAS-003-02 | conditional | IF template AGENTS.md exceeds 35,000 characters THEN emit Size_Warning (per CAP-TPL-008-02) |
| R-TAS-003-03 | optional | WHERE practical, template AGENTS.md SHOULD use progressive disclosure — essential governance in AGENTS.md, detailed documentation in linked files (specs/, docs/, sops/) |

**Enforcement**: Character count check (existing validator covers R-TAS-003-01/02).

**Rationale**: L621 (external best practices) and L600 (compliance degrades at high rule density) support compact AGENTS.md. However, the formal ceiling remains CAP-TPL-008-01 (40,000 chars), not an arbitrary line count. Progressive disclosure keeps governance sections visible without inflating the file.

### CAP-TAS-004: Template Generation Compatibility

The spec SHALL apply uniformly to both template generations (v2-era and v3-era) discovered in Gate 0.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TAS-004-01 | ubiquitous | The required sections (CAP-TAS-001) SHALL apply to all 12 templates regardless of template generation |
| R-TAS-004-02 | conditional | IF a v2-era template already has equivalent patterns (e.g., "What Advisors CANNOT Do"), THEN those patterns SHALL be accepted as satisfying R-TAS-001-04 without requiring reformatting |
| R-TAS-004-03 | conditional | IF a v3-era template lacks all required sections, THEN all sections SHALL be added during remediation |

**Enforcement**: Template conformance check with pattern aliases (e.g., "CANNOT Do" satisfies "Prohibitive Constraints").

**Rationale**: Gate 0 found two template generations — v2-era (advisor/consultant/developer with existing governance patterns) and v3-era (9 minimal templates). The spec must not break existing v2-era templates while requiring v3-era templates to add governance sections.

---

## V-Tests

| ID | Test | BLOCKING | Procedure |
|----|------|----------|-----------|
| V-TAS-001 | All 12 templates have version tag | YES | `grep -q '@aget-version' template-*/AGENTS.md` |
| V-TAS-002 | All 12 templates have North Star/Purpose | YES | `grep -qi 'north.star\|purpose\|## Purpose' template-*/AGENTS.md` |
| V-TAS-003 | All 12 templates have Skill Routing | YES | `grep -qi 'skill.routing\|task.*skill.*table' template-*/AGENTS.md` |
| V-TAS-004 | All 12 templates have Prohibitive Constraints | YES | `grep -qi 'prohibitive\|NEVER\|CANNOT\|shall NOT' template-*/AGENTS.md` |
| V-TAS-005 | All 12 templates have Write Scope | YES | `grep -qi 'write.scope\|write.boundar\|write.*allowed\|write.*prohibited' template-*/AGENTS.md` |
| V-TAS-006 | All 12 templates under 40,000 chars | YES | `wc -c < template-*/AGENTS.md` (all < 40000) |
| V-TAS-007 | Skill Routing has 2+ mappings | NO | Content depth check |
| V-TAS-008 | Prohibitive has 1+ NEVER rule | NO | Content depth check |

---

## Traceability

| Link | Reference |
|------|-----------|
| Parent spec | AGET_TEMPLATE_SPEC (CAP-TPL-006-03, CAP-TPL-008-01) |
| Complementary | CONTENT_INTEGRITY_VALIDATION_SPEC (R-CIV-001-02, R-CIV-004-02) |
| Evidence | L596 (governance pattern validation), L621 (external best practices) |
| Gate -1 | `planning/analysis/governing_spec_inventory.md` — GAP confirmed |
| Gate 0 | `planning/analysis/template_agents_md_audit.md` — 0/12 Skill Routing |
| Project | `planning/PROJECT_PLAN_cli_feature_adoption_remediation_v1.0.md` |
| Cross-agent | CLI-AGET fleet scan report (2026-03-02) |

---

*TEMPLATE_AGENTS_MD_SPEC v1.0.0*
*"Define the structure, not just the container."*
