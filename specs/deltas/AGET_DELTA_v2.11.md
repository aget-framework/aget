# AGET Delta: v2.10 → v2.11

**Implements**: R-SPEC-002-* (8 requirements)
- R-SPEC-002-01: Created when framework version incremented (v2.10 → v2.11)
- R-SPEC-002-02: Documents version increment (From/To metadata)
- R-SPEC-002-03: Lists requirements added (Requirements Changes → Added)
- R-SPEC-002-04: Lists requirements removed (Requirements Changes → Removed)
- R-SPEC-002-05: Lists components added/modified/removed (Component Changes)
- R-SPEC-002-06: Includes migration guide (Migration Guide section)
- R-SPEC-002-07: Includes traceability matrix (Traceability Matrix section)
- R-SPEC-002-08: Saved to specs/deltas/AGET_DELTA_v2.11.md

**Pain Point**: PROJECT_PLAN_v2.11_consistency_verification (missing traceability)
**See**: aget/specs/AGET_FRAMEWORK_SPEC_v2.11.md Section R-SPEC-002
**Tests**: tests/test_delta_specification.py::TestDeltaSpecification
**Pattern**: L352 (Requirement-to-Test Traceability)

---

**From**: v2.10.0 (2025-12-13)
**To**: v2.11.0 (2025-12-23)
**Type**: Minor release
**Format**: AGET_SPEC_FORMAT_v1.1

---

## Summary

v2.11 introduces Memory Architecture, Vocabulary Standard, CLI Settings Hygiene, Process Specification Pilot, Framework Specification Pattern, and Configurable Wake-Up.

**Theme**: Knowledge Management & Standards Maturation

**User-Driven Enhancements**: Version announcement and configurable wake-up output improve operational visibility and personalization (L356).

---

## Requirements Changes

### Added

| ID | Requirement | Source | Artifact |
|----|-------------|--------|----------|
| R-MEM-001 | The SYSTEM shall support 6-layer Memory_Architecture | L335 | governance/MEMORY_VISION.md |
| R-MEM-002 | The SYSTEM shall enable Session_Handoff via structured protocols | L335 | sops/SESSION_HANDOFF_AGET.md |
| R-MEM-003 | WHEN Step_Back_Command is received, the SYSTEM shall execute KB_Review_Protocol | L335 | docs/patterns/PATTERN_step_back_review_kb.md |
| R-MEM-004 | The SYSTEM shall maintain Context_Recovery within 2 minutes | L335 | Wake_Protocol |
| R-MEM-005 | The SYSTEM shall treat KB as Collaboration_Substrate for human-AI memory | L335 | governance/MEMORY_VISION.md |
| R-VOC-001 | The SYSTEM shall follow SKOS-based Vocabulary_Standard | L339 | specs/AGET_GLOSSARY_STANDARD_SPEC_v1.0.md |
| R-VOC-002 | The SYSTEM shall use Title_Case for domain objects | L339 | AGET_CONTROLLED_VOCABULARY.md |
| R-VOC-003 | WHERE Term_Definition is required, the SYSTEM shall reference Controlled_Vocabulary | L339 | validation/validate_vocabulary.py |
| R-VOC-004 | The SYSTEM shall provide Vocabulary_Validation tooling | L339 | validation/ |
| R-CLI-001 | The SYSTEM shall provide CLI_Settings templates for multi-CLI support | Issue #6 | .claude/, .codex/, .gemini/, .cursor/ |
| R-CLI-002 | WHERE CLI_Tool is Claude_Code, the SYSTEM shall provide settings.local.json.template | Issue #6 | .claude/ |
| R-CLI-003 | WHERE CLI_Tool is Codex, the SYSTEM shall provide config.toml.template | Issue #6 | .codex/ |
| R-CLI-004 | WHERE CLI_Tool is Gemini, the SYSTEM shall provide settings.json.template | Issue #6 | .gemini/ |
| R-CLI-005 | The SYSTEM shall maintain GEMINI.md symlink to AGENTS.md | Issue #6 | GEMINI.md |
| R-PROC-001 | The SYSTEM shall support Process_Specification for workflows | L344 | specs/AGET_PROCESS_SPEC_FORMAT_v0.1.md |
| R-PROC-002 | WHERE Process_Spec exists, the SYSTEM shall validate against Schema | L344 | specs/schemas/process_spec_v0.1.json |
| R-PROC-003 | The SYSTEM shall track Learnings_Applied in process specifications | L344 | learnings_applied section |
| R-SPEC-001 | The SYSTEM shall maintain AGET_FRAMEWORK_SPEC for each release | v2.11 | specs/AGET_FRAMEWORK_SPEC_v2.11.md |
| R-SPEC-002 | The SYSTEM shall produce AGET_DELTA for changes between releases | v2.11 | specs/deltas/AGET_DELTA_v2.11.md |
| R-SPEC-003 | WHEN Release_Preparation is initiated, the SYSTEM shall create Framework_Spec as prerequisite | v2.11 | PROJECT_PLAN_framework_specification |
| R-SPEC-004 | The SYSTEM shall use EARS patterns for all formal requirements | AGET_SPEC_FORMAT_v1.1 | All specs |
| R-SPEC-005 | WHERE Gate exists in process, the SYSTEM shall trace to Requirement | L348 | Process specs |
| R-VER-001-08 | WHEN --include-manager flag provided, version consistency check SHALL include managing agent | GAP_ANALYSIS | .aget/patterns/sync/version_consistency.py |
| R-REL-006 | WHEN framework version increments, managing agent SHALL update version.json before tagging release | GAP_ANALYSIS | sops/RELEASE_PROCESS.md Phase 0 |

### Modified

(none)

### Enhanced

| ID | Enhancement | Source | Impact |
|----|-------------|--------|--------|
| R-SESSION-001-03 | Added version announcement to wake-up output | User feedback (L356) | Operational visibility improved |
| R-SESSION-001 | Added configurable wake-up sections via .aget/config.json | User feedback (L356) | User personalization enabled |

### Removed

(none)

---

## Component Changes

### Added

| Component | Location | Purpose | Requirement |
|-----------|----------|---------|-------------|
| MEMORY_VISION.md | governance/ | Memory architecture vision | R-MEM-001 |
| SESSION_HANDOFF_AGET.md | sops/ | Session handoff SOP | R-MEM-002 |
| PATTERN_step_back_review_kb.md | docs/patterns/ | KB review pattern | R-MEM-003 |
| AGET_GLOSSARY_STANDARD_SPEC_v1.0.md | specs/ | Vocabulary standard | R-VOC-001 |
| validate_vocabulary.py | validation/ | SKOS validation | R-VOC-004 |
| project_skos_to_ears.py | validation/ | SKOS to EARS projection | R-VOC-004 |
| AGET_PROCESS_SPEC_FORMAT_v0.1.md | specs/ | Process spec format | R-PROC-001 |
| AGET_RELEASE_PROCESS_v2.11.yaml | specs/processes/ | Release process spec | R-PROC-001 |
| process_spec_v0.1.json | specs/schemas/ | Process spec schema | R-PROC-002 |
| AGET_FRAMEWORK_SPEC_v2.11.md | specs/ | Framework specification | R-SPEC-001 |
| AGET_DELTA_v2.11.md | specs/deltas/ | This document | R-SPEC-002 |
| .claude/settings.local.json.template | templates/ | Claude settings | R-CLI-002 |
| .codex/config.toml.template | templates/ | Codex settings | R-CLI-003 |
| .gemini/settings.json.template | templates/ | Gemini settings | R-CLI-004 |
| .cursor/rules/aget.mdc.template | templates/ | Cursor settings | R-CLI-001 |
| GEMINI.md symlink | templates/ | Gemini entry point | R-CLI-005 |
| .gitignore | Root | Ignore user-specific config | R-SESSION-001 |
| planning/GAP_ANALYSIS_version_migration_v1.0.md | Docs | Gap analysis and fix documentation | R-REL-006 |
| planning/PROJECT_PLAN_L352_phase2_plus_enhancements_v1.0.md | Docs | Phase 2 + enhancements complete | L352 |
| .aget/evolution/L353_pattern_efficiency_scaling.md | Learnings | Pattern efficiency learning | L353 |
| .aget/evolution/L354_meta_testing_viability.md | Learnings | Meta-testing learning | L354 |
| .aget/evolution/L355_pilot_phase_flexibility.md | Learnings | Pilot threshold learning | L355 |
| .aget/evolution/L356_user_driven_enhancement_value.md | Learnings | User feedback learning | L356 |

### Modified

| Component | Change | Requirement |
|-----------|--------|-------------|
| AGET_CONTROLLED_VOCABULARY.md | Added SKOS integration | R-VOC-001 |
| .gitignore | Added CLI ignore patterns | R-CLI-001 |
| CLAUDE.md | Added memory architecture section | R-MEM-001 |
| .aget/patterns/session/wake_up.py | Added version display and config system | R-SESSION-001-03 |
| tests/test_session_protocol.py | Added version assertion | R-SESSION-001-03 |
| CLAUDE.md | Updated wake-up output format | R-SESSION-001-03 |
| .aget/version.json | Updated to v2.11.0 | R-REL-006 |
| sops/RELEASE_PROCESS.md | Added Phase 0: Manager Migration | R-REL-006 |
| .aget/patterns/sync/version_consistency.py | Added --include-manager flag | R-VER-001-08 |

---

## Capability Changes

### Added

| Capability | Description | Requirements |
|------------|-------------|--------------|
| Memory Architecture | 6-layer information model with context optimization | R-MEM-001 through R-MEM-005 |
| Vocabulary Standard | SKOS-based terminology with conformance levels | R-VOC-001 through R-VOC-004 |
| CLI Settings | Multi-CLI configuration templates | R-CLI-001 through R-CLI-005 |
| Process Specification | YAML-based workflow definition (pilot) | R-PROC-001 through R-PROC-003 |
| Framework Specification | Cumulative + delta spec pattern | R-SPEC-001 through R-SPEC-005 |
| Configurable Wake-Up | User-customizable wake-up sections (7 options) | R-SESSION-001 |
| Version Migration | Manager self-updates before releasing framework version | R-REL-006, R-VER-001-08 |

---

## L-doc Additions

| L-doc | Title | Key Learning |
|-------|-------|--------------|
| L335 | Memory Architecture Principles | KB as collaboration substrate |
| L339 | Vocabulary Architecture Patterns | SKOS-based terminology |
| L341 | Governance Intensity Classification | Rigorous/Standard/Light modes |
| L344 | Process Specification Pilot | YAML-based workflow definition |
| L345 | Interactive Handoff Pattern | Real-time Q&A knowledge transfer |
| L346 | Research-Before-Action Discipline | Consult protocols before ad-hoc |
| L347 | Historical Provenance for Ownership | History enables true ownership |
| L348 | Pilot-Then-Standardize Pattern | Test before formalizing |
| L353 | Pattern Efficiency Scaling | 40-60% time reduction after first pattern use |
| L354 | Meta-Testing Viability | Tests can self-enforce pattern compliance |
| L355 | Pilot-Phase Flexibility | Progressive thresholds enable pattern adoption |
| L356 | User-Driven Enhancement Value | User feedback during implementation adds fleet-wide value |

---

## Breaking Changes

(none)

---

## Deprecations

(none)

---

## Migration Guide

### From v2.10 to v2.11

**No breaking changes** - upgrade in place.

**Optional Adoptions**:

1. **Memory Architecture** (recommended):
   - Add "step back. review kb." workflow to substantial change protocol
   - Adopt SESSION_HANDOFF_AGET.md for session continuity
   - Review governance/MEMORY_VISION.md for design principles

2. **Vocabulary Standard** (recommended):
   - Run `validation/validate_vocabulary.py` to check compliance
   - Reference AGET_GLOSSARY_STANDARD_SPEC_v1.0.md for term definitions

3. **CLI Settings** (optional):
   - Copy .claude/, .codex/, .gemini/, .cursor/ templates if using those CLIs
   - Create GEMINI.md → AGENTS.md symlink if using Gemini

4. **Process Specification** (experimental):
   - Pilot format available in specs/AGET_PROCESS_SPEC_FORMAT_v0.1.md
   - Full standardization planned for v2.12

5. **Framework Specification** (new pattern):
   - Each release now includes AGET_FRAMEWORK_SPEC_vX.Y.md
   - Changes documented in AGET_DELTA_vX.Y.md

6. **Configurable Wake-Up** (optional):
   - Create `.aget/config.json` to customize wake-up output
   - 7 configurable sections: version, purpose, repos, templates, git status, template versions, minimal
   - No config file = defaults (current behavior)
   - Example: `{"wake_up": {"show_git_status": true, "minimal": false}}`

---

## Traceability Matrix

### Memory Architecture

| Requirement | L-doc | Issue | Artifact |
|-------------|-------|-------|----------|
| R-MEM-001 | L335 | — | governance/MEMORY_VISION.md |
| R-MEM-002 | L335 | — | sops/SESSION_HANDOFF_AGET.md |
| R-MEM-003 | L335 | — | docs/patterns/PATTERN_step_back_review_kb.md |
| R-MEM-004 | L335 | — | Wake_Protocol |
| R-MEM-005 | L335 | — | governance/MEMORY_VISION.md |

### Vocabulary Standard

| Requirement | L-doc | Issue | Artifact |
|-------------|-------|-------|----------|
| R-VOC-001 | L339 | #9 | specs/AGET_GLOSSARY_STANDARD_SPEC_v1.0.md |
| R-VOC-002 | L339 | #9 | AGET_CONTROLLED_VOCABULARY.md |
| R-VOC-003 | L339 | #9 | Controlled vocabulary references |
| R-VOC-004 | L339 | #9 | validation/ tools |

### CLI Settings

| Requirement | L-doc | Issue | Artifact |
|-------------|-------|-------|----------|
| R-CLI-001 | — | #6 | .claude/, .codex/, .gemini/, .cursor/ |
| R-CLI-002 | — | #6 | .claude/settings.local.json.template |
| R-CLI-003 | — | #6 | .codex/config.toml.template |
| R-CLI-004 | — | #6 | .gemini/settings.json.template |
| R-CLI-005 | — | #6 | GEMINI.md symlink |

### Process Specification

| Requirement | L-doc | Issue | Artifact |
|-------------|-------|-------|----------|
| R-PROC-001 | L344 | — | specs/AGET_PROCESS_SPEC_FORMAT_v0.1.md |
| R-PROC-002 | L344 | — | specs/schemas/process_spec_v0.1.json |
| R-PROC-003 | L344 | — | learnings_applied section |

### Framework Specification

| Requirement | L-doc | Issue | Artifact |
|-------------|-------|-------|----------|
| R-SPEC-001 | — | — | specs/AGET_FRAMEWORK_SPEC_v2.11.md |
| R-SPEC-002 | — | — | specs/deltas/AGET_DELTA_v2.11.md |
| R-SPEC-003 | — | — | PROJECT_PLAN_framework_specification |
| R-SPEC-004 | — | — | AGET_SPEC_FORMAT_v1.1 |
| R-SPEC-005 | L348 | — | Process spec traceability |

### Wake-Up Enhancements

| Enhancement | L-doc | User Feedback | Artifact |
|-------------|-------|---------------|----------|
| Version announcement | L356 | Operational visibility | .aget/patterns/session/wake_up.py |
| Configurable wake-up | L356 | Personalization | .aget/config.json, wake_up.py |

---

## Theoretical Basis

| Concept | Theory | L-doc |
|---------|--------|-------|
| Memory Architecture | Extended Mind, Transactive Memory, Stigmergy | L335 |
| Vocabulary Standard | SKOS, Knowledge Organization Systems | L339 |
| Governance Intensity | Cybernetics, BDI | L341 |
| Process Specification | Workflow languages, Double-loop learning | L344 |
| Pilot-Then-Standardize | Lean Startup, Premature Abstraction | L348 |
| Framework Specification | Requirements traceability, SRS | v2.11 |
| Pattern Efficiency Scaling | Learning curve theory, Deliberate practice | L353 |
| Meta-Testing Viability | Reflective architecture, Quality assurance theory | L354 |
| Pilot-Phase Flexibility | Quality progression, Technical debt management | L355 |
| User-Driven Enhancement | Participatory design, Agile development | L356 |

---

*AGET_DELTA_v2.11.md — What CHANGED from v2.10 to v2.11*
*Created: 2025-12-23*
*Format: AGET_SPEC_FORMAT_v1.1*
