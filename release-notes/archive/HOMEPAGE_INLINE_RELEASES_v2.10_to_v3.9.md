# Org-Profile Inline Release Archive: v2.10.0 – v3.9.0

**Archived**: 2026-05-16
**Source**: Retired from `.github/profile/README.md` § Roadmap (org-profile README) per Fork C Hybrid (homepage surface architecture decision, 2026-05-10).
**Reason**: Under Fork C, the org-profile README carries inline release entries for **v3.10.0+ only**. Pre-v3.10 entries are preserved in this archive (history is never deleted; just relocated to reduce homepage real-estate cost).
**Canonical authoritative source**: [GitHub Releases](https://github.com/aget-framework/aget/releases) (each version below has a full Release page with the canonical body).
**Provenance**: This archive's content was originally inline at `aget-framework/.github/profile/README.md` lines 516–647 (commit prior to 2026-05-16 Fork C implementation).

---

## v3.9.0 - Governance Enforcement

**Released**: 2026-03-15

- ✅ **Phase -1: Release Readiness**: 3 sub-phases (B.1 Assessment, B.2 Conformance Audit, B.3 Principal Approval) with 12-item checklist — governs Gap B transition
- ✅ **Phase 0.85: Deliverable Conformance Check**: SHALL violations are BLOCKING
- ✅ **Gate 0: Spec Verification (MP-1)**: Mandatory spec verification sweep before implementation begins
- ✅ **Version-Bearing Enforcement**: version_bump.py extended to 5/5 artifact types (version.json, README.md, AGENTS.md, codemeta.json, CITATION.cff) with `--check` validation mode
- ✅ **GOVERNANCE_PRINCIPLES.md**: First public publication (6 Tier 1 + 5 Tier 2 meta-principles)
- ✅ **aget-enhance-spec Fixes**: Phase 6 consistency (#418), phantom spec reference (#419)

## v3.8.0 - Governance Maturation

**Released**: 2026-03-08

- ✅ **Meta-Principle Codification**: GOVERNANCE_PRINCIPLES.md v1.1.0 — 6 Tier 1 + 5 Tier 2 meta-principles answering "what rules govern the rules?"
- ✅ **Structural Aesthetics**: Third design principle integrated into DESIGN_PHILOSOPHY, MISSION, homepage
- ✅ **Skill Customization Detection**: `pre_sync_check.py` detects, classifies, and reports skill customizations before upgrade
- ✅ **PROJECT_PLAN Validator**: `validate_project_plan.py` prevents prompt-as-plan anti-pattern
- ✅ **Private-First Issue Routing**: AGET_ISSUE_GOVERNANCE_SPEC v2.0.0 — all issues route to private repo first
- ✅ **Template Governance**: All 12 templates updated with `.claude/` scaffolding and governance patterns
- ✅ **New Skills**: `aget-enhance-spec` v1.1.0 (spec lifecycle), `aget-expand-ontology` v1.0.0 (SKOS expansion)

## v3.7.0 - Quality Reconciliation

**Released**: 2026-03-02

- ✅ **Content Integrity Validation**: CONTENT_INTEGRITY_SPEC v1.0.0 — 38 EARS requirements covering 8 dimensions of content claim drift
- ✅ **Evidence-Based Positioning**: 15 READMEs + 2 specs reframed to lead with demonstrated capabilities
- ✅ **Skill Verb Vocabulary**: 4 skill renames aligned to approved verbs (`aget-studyup` → `aget-study-up`)
- ✅ **SOP Lifecycle Management**: AGET_SOP_SPEC v1.2.0 with Draft/Active/Deprecated states
- ✅ **Specification Enhancement Lifecycle**: SKILL-041 + SOP for governed spec creation/updates
- ✅ **15 Universal Skills**: 3-way mismatch resolved — spec/README/deployed aligned at 15 universal

## v3.6.0 - Infrastructure Maturation

**Released**: 2026-02-21

- ✅ **Release Observability**: 5 scripts — validation_logger, run_gate, release_snapshot, propagation_audit, health_logger
- ✅ **Content Integrity**: 6 dimensions of claim-vs-reality drift fixed across all repos
- ✅ **Canonical Scripts v2.0.0**: C3+C1 hybrid architecture (config-driven + hook-based extensions)
- ✅ **Universal Skills**: 14 skills (added aget-studyup)
- ✅ **Vocabulary Precision**: 4 compliance behavioral terms (VOCABULARY_SPEC v1.16.0)
- ✅ **Platform Claims**: Claude Code, Codex CLI, Gemini CLI (Cursor/Aider → Experimental)
- ✅ **Conformance Tool v1.3.0**: 12/12 templates CONFORMANT at deep depth

## v3.5.0 - Archetype Customization

**Released**: 2026-02-14

- ✅ **Archetype Ontologies**: 12 ONTOLOGY_{archetype}.yaml files with 87 domain concepts
- ✅ **Archetype Skills**: 26 archetype-specific skills (2-3 per archetype)
- ✅ **Universal Skills**: 13 skills shared across all templates
- ✅ **Skill Specifications**: EARS-compliant specs for all 39 skills
- ✅ **Ontology-Driven**: Vocabulary → Specification → Instance pattern (L486)

## v3.4.0 - Session Skills Maturity + Governance Formalization

**Released**: 2026-01-18

- ✅ **Session Protocol Enhancements**: Re-entrancy guard, calendar awareness, sanity gate
- ✅ **Cross-CLI Validation**: Tested on Claude Code, Codex CLI, Gemini CLI
- ✅ **Governance Formalization**: Release, behavioral, and artifact governance patterns
- ✅ **Spec-First Documentation**: AGET_IDENTITY_SPEC.yaml, AGET_POSITIONING_SPEC.yaml
- ✅ **New SOPs**: L-doc creation, Enhancement Request, PROJECT_PLAN archival
- ✅ **Template Infrastructure**: sops/ with SOP_escalation.md in all 12 templates (R-TEMPLATE-001)
- ✅ **codemeta.json + CITATION.cff**: Standard software metadata

## v3.3.0 - Shell Integration + Executable Knowledge Ontology

**Released**: 2026-01-10

- ✅ **Shell Orchestration**: aget.zsh, profiles.zsh (5 CLI backends)
- ✅ **SKOS-Compliant Vocabularies**: All 12 templates have ontologies (R-REL-015)
- ✅ **Ontology-Driven Creation** (L481, L482): Specs drive instances, not follow them
- ✅ **AGET_EXECUTABLE_KNOWLEDGE_SPEC.md**: Executable knowledge framework
- ✅ **AGET_EVOLUTION_SPEC.md**: Evolution entry standardization
- ✅ **18 New L-docs**: L451-L503 learnings documented

## v3.2.1 - Version Inventory Coherence

**Released**: 2026-01-04

- ✅ **L444 Remediation**: Version consistency across all version-bearing files
- ✅ **Coherence Testing**: New V-tests for AGENTS.md, manifest.yaml verification
- ✅ **SOP Update**: Gate 7 V-tests for version inventory coherence

## v3.2.0 - Specification Architecture

**Released**: 2026-01-04

- ✅ **7 New Specifications**: Testing, Release, Documentation, Organization, Error, Security, Project Plan
- ✅ **Naming Conventions Expansion**: 4 → 10 categories (Categories F-J)
- ✅ **Specification Index System**: INDEX.md (30 specs) + REQUIREMENTS_MATRIX.md (78 CAP requirements)
- ✅ **6 New Validators**: License, Agent Structure, Release Gate, L-doc Index, SOP, Homepage
- ✅ **Standardized Spec Headers**: YAML frontmatter with version, status, dependencies
- ✅ **Learnings**: L439, L440, L443

## v3.1.0 - Protocol Enforcement Through Infrastructure

**Released**: 2026-01-04

- ✅ **Cross-CLI Infrastructure**: Agent-agnostic scripts with --json output
- ✅ **Complete Session Lifecycle**: wake up → sanity check → wind down
- ✅ **Verification Architecture**: Source-verified constants, enforcement testing
- ✅ **L-doc Format v2**: Cross-agent discovery, adoption tracking
- ✅ **Fleet Validation Tooling**: validate_fleet.py, version_sync.py
- ✅ **Workflow Automation**: L-doc to GitHub Issue, cascade to SOP

## v3.0.0 - 5D Composition Architecture

**Released**: 2025-12-28

- ✅ **5D Directory Structure**: persona/, memory/, reasoning/, skills/, context/
- ✅ **Instance Type System**: aget (advisory), AGET (action-taking), template
- ✅ **Template field**: Replaces deprecated roles array
- ✅ All 6 templates migrated to v3.0 architecture
- ✅ 731 contract tests passing across framework
- ✅ Breaking changes: roles removed, manifest_version 3.0

## v2.12.0 - Capability Architecture Completion

**Released**: 2025-12-25

- ✅ Complete capability composition system (5 specs, 3 validators, 80 tests)
- ✅ Template manifest system for agent composition (manifest.yaml)
- ✅ Fleet migration enablement (6 pilots validated)
- ✅ Governance exemplar enforcement (L367)

## v2.11.0 - Memory Architecture + Public Governance

**Released**: 2025-12-24

- ✅ Memory Architecture (L335): 6-layer information model
- ✅ L352 Traceability Pattern: Requirement-to-test traceability
- ✅ R-PUB-001 Public Release Completeness (8 requirements)
- ✅ Version migration protocol (R-REL-006)

## v2.10.0 - Capability Composition Architecture

**Released**: 2025-12-13

- ✅ 6 agent type specifications
- ✅ Executive Advisor pattern (5W+H knowledge architecture)
- ✅ Theoretical grounding protocol (L332)

---

## See Also

- **Current homepage**: [.github/profile/README.md](https://github.com/aget-framework/.github/blob/main/profile/README.md) — v3.10+ inline entries only (Fork C boundary)
- **Full release pages**: [GitHub Releases](https://github.com/aget-framework/aget/releases) — canonical bodies per version
- **CHANGELOG**: [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) — Keep-a-Changelog style consolidated history
- **Fork C decision memo**: [MEMO_homepage_surface_architecture_fork_2026-05-10.md](https://github.com/gmelli/private-aget-framework-AGET/blob/main/docs/MEMO_homepage_surface_architecture_fork_2026-05-10.md) (private; principal-accessible context)

---

*Archive created under T1.12 Gate 1 of `PROJECT_PLAN_v3.18_T1.12_homepage_fork_bundle_v1.0.md` (Fork C Hybrid implementation). Closes L941-L944 cluster homepage-substrate findings.*
