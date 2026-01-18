# Changelog

All notable changes to the AGET Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: This CHANGELOG reflects the public aget-framework/aget repository. For complete version history including release gaps and template-specific changes, see [VERSION_HISTORY.md](docs/VERSION_HISTORY.md).

---

## [Unreleased]

*No unreleased changes*

---

## [3.4.0] - 2026-01-18

**Theme**: Session Skills Maturity + Governance Formalization

### Added

- **Session Protocol Enhancements** (CAP-SESSION-010, 011, 012):
  - `wind_down.py`: Re-entrancy guard prevents concurrent executions (CAP-SESSION-010)
  - `wind_down.py`: Sanity gate runs abbreviated health check before session end (CAP-SESSION-012)
  - `wake_up.py`: Calendar awareness displays date and release window notifications (CAP-SESSION-011)
  - Cross-CLI validation on Claude Code, Codex CLI, and Gemini CLI

- **Governance Artifact SOPs and Templates**:
  - `SOP_L-DOC_CREATION.md`: Standard procedure for creating L-docs
  - `TEMPLATE_L-DOC.md`: Reusable L-doc template
  - `SOP_ENHANCEMENT_REQUEST.md`: Standard procedure for Enhancement Requests
  - `TEMPLATE_ENHANCEMENT_REQUEST.md`: Reusable Enhancement Request template
  - `SOP_project_plan_archival.md`: PROJECT_PLAN → evolution workflow (CAP-EVOL-008)

- **Release Governance** (VERSION_SCOPE formalization):
  - AGET_VOCABULARY_SPEC: 8 VERSION_SCOPE terms formalized
  - CAP-REL-012 through CAP-REL-018: VERSION_SCOPE requirements in EARS format
  - SOP Phase 2.5: Vocabulary/spec reconciliation protocol
  - SOP Phase 2.6: SOP/Template reconciliation protocol

- **Behavioral Governance**:
  - L552: Imperative Escalation Bypass pattern documented
  - R-BEHAV-EAC-*: Behavioral requirements for escalation acknowledgment

- **Spec-First Documentation**:
  - `AGET_IDENTITY_SPEC.yaml`: Agent identity specification (machine-readable)
  - `AGET_POSITIONING_SPEC.yaml`: Market positioning specification (machine-readable)
  - `codemeta.json`: Software metadata standard
  - `CITATION.cff`: Citation file format for academic reference

- **Template Infrastructure**:
  - `sops/` directory with SOP_escalation.md in all 12 templates (R-TEMPLATE-001)

- **Standards Document Ontology** (L502, PROJECT_PLAN_standards_ontology_elevation_v1.0):
  - AGET_VOCABULARY_SPEC Part 7: Document type hierarchy, authority model, traceability properties
  - 6 exemplar specification entries with `aget:defines` traceability
  - `check_ontology_coherence.sh`: Lightweight vocabulary coherence checker
  - `SOP_specification_consolidation.md`: Consolidation process
  - `SOP_artifact_deprecation.md`: Deprecation process with authority lifecycle
  - INDEX.md Authority column (CANONICAL, Active, Draft, Deprecated)

- **Release Window Timing** (CAP-REL-011):
  - AGET_RELEASE_SPEC v1.3.0: Release_Window vocabulary, CAP-REL-011 requirements
  - SOP_release_process.md v1.3.0: V0.0 timing check in Phase 0
  - Preferred windows: Thursday AM, Friday PM
  - Advisory (SHOULD) requirement with acknowledgment for off-window releases

### Changed

- **AGET_SESSION_SPEC.md**: 1.1.0 → 1.2.0 (CAP-SESSION-010, 011, 012)
- **AGET_PROJECT_PLAN_SPEC.md**: 1.1.0 → 1.2.0 (CAP-PP-013 through 018)
- **AGET_TEMPLATE_SPEC.md**: 3.3.1 → 3.3.2 (R-TEMPLATE-001)
- **AGET_EVOLUTION_SPEC.md**: 1.0.0 → 1.1.0 (PROJECT_PLAN_Entry type, CAP-EVOL-008)

- **PROJECT_PLAN Template v2.0** (L515, #233, #247):
  - Consolidated to single canonical template at `templates/PROJECT_PLAN_TEMPLATE.md`
  - Removed duplicate from `docs/templates/`
  - Added Plan_Status controlled vocabulary (#232)
  - Added Gate Naming Convention guidance (#233)
  - Added mandatory Project Closure Checklist (#247)
  - Added status transition rules
  - Added Gate -1 (Pre-Execution) gate
  - Added Operational Context section (CAP-PP-014)
  - Added Retrospective section (L435)

- **validate_project_plan.py** (L515, #233):
  - Now supports multiple gate naming conventions: G-N:, Gate N:, Gate N.M:, {Track}-N:
  - Extended --strict mode to check closure checklist (L515/#247)
  - Improved error messages with gate name truncation

- **AGET Lifecycle SOPs renamed to active verb pattern** (AI-1, SOP_SOP_CREATION.md):
  - `SOP_agent_instance_creation.md` → `SOP_aget_create.md`
  - `SOP_instance_migration_v3.md` → `SOP_aget_migrate.md`
  - Pattern: `SOP_aget_{active_verb}.md` per naming convention
  - 50 files updated across 7 repositories

### Learnings Captured

- L554: Hierarchical PROJECT_PLAN gap — SOP needs top-level vs contributing guidance
- L555-candidate: KB review should precede governance artifact creation
- L556-candidate: V-tests validate presence, not correctness

### Metrics

| Metric | Value |
|--------|-------|
| GO issues resolved | 10 |
| Implementations completed | 12 |
| Specs updated | 4 |
| New SOPs | 4 |
| New templates | 3 |
| Templates with sops/ + SOP files | 12/12 |
| Session tests passing | 38 |

### Migration Guide

**For Existing Agents**:
1. Update version files: Bump `.aget/version.json` to 3.4.0
2. Create sops/ directory: If not present, create `sops/` and add at least one SOP file (e.g., `SOP_escalation.md`)
3. Review session scripts: Verify wake_up.py and wind_down.py compatibility

**Breaking Changes**: None. v3.4.0 is backward compatible with v3.3.x agents.

### Contributing Projects

This release aggregates work from six completed PROJECT_PLANs:
1. PROJECT_PLAN_session_skills_maturity_v1.0.md
2. PROJECT_PLAN_conformance_rubric_v3.4_v1.0.md
3. PROJECT_PLAN_spec_first_documentation_v1.0.md
4. PROJECT_PLAN_version_scope_standardization_v1.0.md
5. PROJECT_PLAN_project_plan_creation_sop_v1.0.md
6. PROJECT_PLAN_sop_creation_sop_v1.0.md

---

## [3.3.0] - 2026-01-10

**Theme**: Shell Integration + Executable Knowledge Ontology

### Added

- **Shell Integration** (L452):
  - `shell/aget.zsh`: Main shell orchestration file
  - `shell/profiles.zsh`: CLI backend profiles (Claude Code, Cursor, Aider, Gemini, Windsurf)
  - `scripts/generate_agents_zsh.py`: Alias generator for agent directories
  - `docs/SHELL_INTEGRATION.md`: User documentation

- **Executable Knowledge Ontology** (L451, L453):
  - `AGET_EXECUTABLE_KNOWLEDGE_SPEC.md`: EKO axis definitions (Determinism, Reusability, Abstraction)
  - `AGET_EVOLUTION_SPEC.md`: Evolution entry type standardization (L-doc, D-doc, DISC-doc)
  - VOCABULARY_SPEC Part 5: EKO terms

- **Ontology-Driven Agent Creation** (L481, L482):
  - `SOP_aget_create.md`: SKOS+EARS-grounded creation process
  - `scripts/generate_template_ontology.py`: Template vocabulary generator
  - `validation/validate_ontology_compliance.py`: SKOS compliance validator
  - 12 template vocabularies: All templates now have specs/*_VOCABULARY.md
  - R-REL-015: "We do not leave published templates behind"

- **Session Governance**:
  - `SOP_point_upgrade.md`: Formal point upgrade procedure (L444 conformance)
  - CAP-PP-012: Artifact comprehensibility (merged #67)

- **18 New L-docs**: L451-L453, L460-L468, L478-L482, L500-L503

### Changed

- **Template Conformance**: All 12 templates now have SKOS-compliant vocabularies
- **SOP_release_process.md**: v1.10 with R-REL-015 (template conformance)
- **AGET_PORTABILITY_SPEC.md**: Shell integration references
- **AGET_COMPATIBILITY_SPEC.md**: Zsh/bash support section

### Fixed

- **Version Documentation Gap**: README.md and VERSION_HISTORY.md updated (were stale at v2.11.0)

### Notes

This release establishes the foundation for ontology-driven agent creation, where template
vocabularies DRIVE instance behavior (L481). All published templates now conform to
SKOS vocabulary standards, enabling fleet supervisors to validate instance compliance.

---

## [3.2.1] - 2026-01-04

**Theme**: Version Inventory Coherence (L444 Remediation)

### Fixed

- **Version Consistency**: All version-bearing files now consistent across 7 repos
  - AGENTS.md headers updated (were stuck at v3.1.0)
  - manifest.yaml version fields updated (were stuck at 3.1.0)
  - version.json files updated to 3.2.1
- **Coherence Testing**: Added V7.1.4, V7.1.5, V7.1.6 tests to Gate 7
  - V7.1.4: AGENTS.md header version check
  - V7.1.5: manifest.yaml version field check
  - V7.1.6: No stale version references check
- **SOP Update**: `SOP_release_process.md` v1.7 with L444 coherence testing section

### Added

- **L444**: Version Inventory Coherence Requirement learning document
- **R-REL-VER-001**: New requirement for version inventory coherence

### Notes

This patch release addresses version inconsistencies discovered during v3.2.0 retrospective.
Root cause: Gate 7 checklist verified version.json but not AGENTS.md or manifest.yaml.

See L444 for full 5-why analysis and process improvements.

---

## [3.2.0] - 2026-01-04

**Theme**: Specification Architecture

### Added

- **7 New Specifications**: Comprehensive governance coverage
  - `AGET_TESTING_SPEC.md`: Contract testing requirements (CAP-TEST-001 to CAP-TEST-009)
  - `AGET_RELEASE_SPEC.md`: Release process requirements (CAP-REL-001 to CAP-REL-006)
  - `AGET_DOCUMENTATION_SPEC.md`: Documentation standards (CAP-DOC-001 to CAP-DOC-007)
  - `AGET_ORGANIZATION_SPEC.md`: Organization artifacts (CAP-ORG-001 to CAP-ORG-003)
  - `AGET_ERROR_SPEC.md`: Error handling patterns (CAP-ERR-001 to CAP-ERR-005)
  - `AGET_SECURITY_SPEC.md`: Security requirements (CAP-SEC-001 to CAP-SEC-004)
  - `AGET_PROJECT_PLAN_SPEC.md`: Planning standards (CAP-PP-001 to CAP-PP-011)
- **Naming Convention Expansion**: 4 → 10 categories (L439)
  - Category F: Standard Open-Source Files (README, LICENSE, CHANGELOG, CONTRIBUTING)
  - Category G: Requirement Documents (R-XXX-NNN pattern)
  - Category H: Change Proposals (CP-NNN_name.md)
  - Category I: Protocol Documents (*_PROTOCOL.md)
  - Category J: Checklists (*_CHECKLIST.md)
  - Domain Codes Registry (17 registered: REL, TPL, WAKE, etc.)
  - Git Branch Naming (feature/, fix/, docs/, etc.)
  - Git Tag Naming (vM.m.p[-prerelease])
- **Specification Index System**:
  - `INDEX.md`: Master list of 30 specifications
  - `REQUIREMENTS_MATRIX.md`: 78 CAP requirements cross-referenced
- **Standardized Spec Headers**:
  - YAML frontmatter with version, status, domain, dependencies
  - `migrate_spec_headers.py` migration script
  - JSON Schema for header validation
- **6 New Validators** (L433 remediation):
  - `validate_license_compliance.py`: Apache 2.0 verification (CAP-LIC-001 to CAP-LIC-004)
  - `validate_agent_structure.py`: 5D directory validation (CAP-STRUCT-001 to CAP-STRUCT-005)
  - `validate_release_gate.py`: Release gate enforcement (R-REL-006, L440)
  - `validate_ldoc_index.py`: L-doc index consistency (CAP-MEMORY-008)
  - `validate_sop_compliance.py`: SOP format validation (CAP-SOP-001 to CAP-SOP-004)
  - `validate_homepage_messaging.py`: Homepage validation (CAP-ORG-001, CAP-ORG-002)

### Changed

- Validator inventory: 24 → 30 implemented
- Spec count: 23 → 30 (7 new specifications)
- Naming categories: 4 → 10 (6 new categories)
- All specs now have standardized headers with version, status, dependencies
- VALIDATOR_INVENTORY.md now tracks theater ratio (33% → target <10%)

### Documentation

- INDEX.md: Central specification registry
- REQUIREMENTS_MATRIX.md: Complete CAP requirement inventory
- PROJECT_PLAN_TEMPLATE.md: Standard planning format with V-tests (CAP-PP-011)

### Learnings Captured

- L439: Standard Open-Source Files as Category F
- L440: "A checkbox is not a verification. A passing test is."
- L441: Theater Ratio as Specification Quality Metric
- L442: Declarative vs Executable Verification
- L443: Theater Ratio Paradox (new specs increase denominator)

### Tests

30 validators implemented (theater ratio 33%, target <10% for v3.3.0)

---

## [3.1.0] - 2026-01-04

### Added

- **Complete Session Lifecycle**: Full session protocol suite in all templates
  - `wake_up.py`: Session initialization (R-WAKE-001 to R-WAKE-007)
  - `aget_housekeeping_protocol.py`: Mid-session sanity checks (R-SANITY-001 to R-SANITY-007)
  - `wind_down.py`: Session close with sanity gate (R-WIND-001 to R-WIND-006)
- **L-Doc Format v2**: Structured metadata for cross-agent pattern discovery
  - `format_version: "2.0"` header
  - `migrate_ldoc_to_v2.py` migration tool
  - JSON Schema validation (`schemas/ldoc_v2.json`)
- **Fleet Governance Patterns**:
  - Role Boundary Awareness (PATTERN_role_boundary_awareness.md)
  - Version Sync (`version_sync.py`) for fleet-wide consistency
  - Issue Routing via `.aget/config/issue_routing.yaml`
- **Workflow Automation Scripts**:
  - `learning_to_enhancement.py`: L-doc → GitHub Issue workflow
  - `cascade_ldoc_to_sop.py`: L-doc → SOP cascade automation
  - `validate_cli_settings.py`: CLI settings hygiene validation
  - `validate_fleet.py`: Fleet-wide validation
- **CLI Settings Standard**: R-CLI-001 to R-CLI-005 for Claude Code, Codex, Cursor
- **Organization Artifact Specification**: CAP-ORG-001 (homepage update requirements)

### Changed

- All scripts support `--json` output for cross-CLI automation
- All scripts implement L038 (Agent-Agnostic) and L021 (Verify-Before-Modify)
- AGET_FRAMEWORK_SPEC updated to 10 capability domains (added CAP-ORG)
- RELEASE_VERIFICATION_CHECKLIST updated with Gate 7 (Organization Artifacts)

### Fixed

- #14: Naming validator index file exception
- #15: Migration guide documentation enhancements
- #16: AGENTS.md Project Context version in migration script

---

## [3.0.0] - 2025-12-28

### Added

- **5D Composition Architecture**: Structured directories for agent composition
  - `.aget/persona/` - Agent identity and behavioral characteristics
  - `.aget/memory/` - Session handoffs and persistent state
  - `.aget/reasoning/` - Decision frameworks and policies
  - `.aget/skills/` - Patterns, SOPs, and automation scripts
  - `.aget/context/` - Environmental and domain information
- **Instance Type System**: Clear distinction between `aget` (advisory), `AGET` (action-taking), and `template`
- **Template Field**: Replaces `roles` array with single `template` field in version.json
- **Archetype Field**: High-level classification (supervisor, worker, advisor, consultant, developer, spec-engineer)
- **v3.0 Contract Tests**: Updated test suite supporting 5D architecture and v3.0 schema

### Changed

- **BREAKING**: `roles` field removed from version.json (use `template` and `instance_type`)
- **BREAKING**: `persona` field in version.json now optional (use `.aget/persona/` directory)
- Manifest version: 2.0 → 3.0
- All 6 templates migrated to 5D architecture

### Migration Guide

Agents upgrading from v2.x:
1. Add `template` field (archetype name)
2. Add `instance_type` field (`aget`, `AGET`, or `template`)
3. Add `archetype` field (high-level classification)
4. Create `.aget/persona/`, `.aget/memory/`, `.aget/reasoning/`, `.aget/skills/`, `.aget/context/` directories
5. Remove `roles` field (deprecated)
6. See `docs/FLEET_MIGRATION_GUIDE.md` for detailed steps

---

## [2.12.0] - 2025-12-25

### Added

- **Capability Architecture Completion**: Full implementation of capability composition system
- **CAPABILITY_SPEC_v1.0_SCHEMA.yaml**: JSON Schema for capability specifications
- **TEMPLATE_MANIFEST_v1.0_SCHEMA.yaml**: JSON Schema for agent composition declarations
- **COMPOSITION_SPEC_v1.0.md**: DAG composition rules, conflict detection, resolution strategies
- **5 Capability Specifications**:
  - `memory-management` (upgraded from DRAFT to v1.0 APPROVED)
  - `domain-knowledge` (P0 - 12+ agent demand)
  - `structured-outputs` (P0 - 8+ agent demand)
  - `collaboration` (P1 - multi-agent coordination)
  - `org-kb` (P1 - 5W+H organizational knowledge base)
- **3 Validators**:
  - `validate_capability_spec.py`: Schema compliance for capability specs
  - `validate_template_manifest.py`: Manifest structure validation
  - `validate_composition.py`: DAG conflict detection, prerequisite checking
- **80 Capability Architecture Tests**: Comprehensive test suite across 5 test files
- **3 Practitioner Guides**:
  - `CAPABILITY_AUTHOR_GUIDE.md`: How to create new capabilities (521 lines)
  - `COMPOSITION_GUIDE.md`: How to compose agents from capabilities (556 lines)
  - `FLEET_MIGRATION_GUIDE.md`: Step-by-step migration procedures (618 lines)

### Changed

- Architecture completeness: 65% → 100% (all 5 layers complete)
- Fleet Migration Phase 2 prerequisites: All satisfied

### Documentation

- Pattern documents for structured-outputs and collaboration capabilities
- Cross-referenced documentation ecosystem for practitioners
- Pilot agent inventory with version gap analysis

### Tests

80 passing (capability architecture tests)
- test_capability_spec_validation.py (18 tests)
- test_template_manifest_validation.py (14 tests)
- test_composition_validation.py (16 tests)
- test_agent_type_instantiation.py (12 tests)
- test_capability_contracts.py (20 tests)

### Fleet Migration Enablement

- 5 pilot agents documented with projected compositions
- Migration complexity ranking established
- Recommended migration order (3 waves)

---

## [2.11.0] - 2025-12-24

### Added

- **Memory Architecture (L335)**: 6-layer information model for persistent knowledge across sessions
- **L352 Traceability Pattern**: Five-tier requirement-to-test traceability system
- **R-PUB-001 Public Release Completeness**: 8 requirements ensuring user-visible release quality
- **Post-release validation automation**: `post_release_validation.py` automates 6/8 completeness checks
- **Public framework governance documentation**: VERSIONING.md, RELEASES.md, UPGRADING.md, COMMUNICATION_STANDARDS.md
- **Configurable wake-up output**: 7 customizable sections for agent session initialization
- **Version migration protocol (R-REL-006)**: Framework manager self-updates before releasing public repos
- **Process Specification Pilot (v0.1)**: YAML-based workflow definitions
- **Vocabulary Standard**: SKOS-based terminology management
- **CLI Settings templates**: Pre-configured settings for Claude Code, Codex, Gemini, Cursor

### Changed

- Enhanced RELEASE_PROCESS.md with Phase 4 (Post-Release Validation) and Phase 5 (Public Announcement)
- Framework Specification pattern now supports cumulative + delta views
- SESSION_HANDOFF protocol updated with memory layer integration

### Documentation

- Created VERSION_HISTORY.md: Complete version timeline with transparent gap acknowledgment
- Created PUBLIC_RELEASE_VALIDATION.md: Manual validation checklist for releases
- Enhanced organizational homepage with current version consistency
- Added 40 contract tests with full L352 traceability matrix

### Learnings Captured

- L353: Pattern Efficiency Scaling
- L354: Meta-Testing Viability
- L355: Pilot-Phase Flexibility
- L356: User-Driven Enhancement Value
- L357: Version Migration as Explicit Deliverable
- L358: Tags ≠ Releases on GitHub (process gap discovery)

### Tests

80 passing (40 L352 pattern tests + 40 baseline tests)

**See**: [AGET_DELTA_v2.11.md](specs/deltas/AGET_DELTA_v2.11.md) for complete technical specification

---

## [2.10.0] - 2025-12-24

**Note**: Work completed 2025-12-13. GitHub Release created retroactively on 2025-12-24 as part of public framework governance enhancement.

### Added

- **Capability Composition Architecture**: Framework for defining agent types via capability combinations
- **6 Agent Type Specifications**: Data Science, Executive Advisor, Specification Owner, Software Development Owner, Knowledge Owner, Research Advisor
- **Executive Advisor Pattern**: 5W+H knowledge base architecture for strategic guidance
- **Domain Specialist Pattern**: Structured output formats for specialized agent responses
- **Theoretical Grounding Protocol (L332)**: Maps framework concepts to established theory (BDI, Actor Model, Extended Mind, Cybernetics)
- **Knowledge Inheritance Requirement (L330)**: Framework owners must inherit institutional knowledge

### Changed

- Agent type model: From rigid categories to capability-based composition
- Pattern documentation: Structured format with theoretical foundations

### Learnings Captured

- L330: Knowledge Inheritance Requirement
- L331: Theoretical Foundations of Agency
- L332: Theoretical Grounding Protocol

### Tests

39 passing (contract tests for capability specifications)

**See**: specs/deltas/AGET_DELTA_v2.10.md for complete changes (if available)

---

## [2.9.0] - 2025-11-24

**Note**: Partial release - only advisor-family templates received GitHub Releases. Core aget/ repository did not have a public release.

### Added

- **Session location standard**: sessions/ directory at repository root
- **Session metadata standard**: YAML frontmatter for session files
- **Memory layer for advisors**: .memory/ directory structure for knowledge persistence
- **5-layer knowledge architecture**: Organized knowledge storage system
- **Fleet-wide migration protocol**: Coordinated version updates across 28 agents

### Changed

- Information storage standardized across all agent types
- Memory patterns enhanced for long-running advisory sessions

**See**: Template-specific releases for detailed changes:
- [template-advisor-aget v2.9.0](https://github.com/aget-framework/template-advisor-aget/releases/tag/v2.9.0)
- [template-consultant-aget v2.9.0](https://github.com/aget-framework/template-consultant-aget/releases/tag/v2.9.0)
- [template-developer-aget v2.9.0](https://github.com/aget-framework/template-developer-aget/releases/tag/v2.9.0)
- [template-spec-engineer-aget v2.9.0](https://github.com/aget-framework/template-spec-engineer-aget/releases/tag/v2.9.0)

---

## [2.8.0] - 2025-11-10

**Note**: Core aget/ repository did not have a public GitHub Release for this version.

### Added

- **Friction Reduction Enhancements**: Streamlined workflows for common agent tasks
- **Enhancement Filing Protocol**: Standardized process for proposing framework improvements
- **Planning Framework**: PROJECT_PLAN templates for multi-gate work

### Changed

- Agent configuration templates simplified
- Documentation structure reorganized for better discoverability

**See**: Template-specific releases for detailed changes (all 6 templates released)

---

## [2.7.0] - 2025-10-13

**Note**: Core aget/ repository did not have a public GitHub Release for this version.

### Added

- **Portfolio Governance**: Multi-portfolio agent management (main, ccb, legalon, etc.)
- **Portfolio Field**: `portfolio` metadata in .aget/version.json
- **Naming Conventions**: Standardized agent naming patterns (domain-specialty-type format)
- **Advisor Personas**: Enhanced role definitions for advisor-type agents

### Changed

- Agent identity model expanded to include portfolio affiliation
- Scope boundaries clarified across portfolios

**See**: Template-specific releases for detailed changes

---

## [2.6.0] - 2025-10-12

**Note**: Version documented in internal migration history but no public GitHub Releases created (known gap).

### Added

- **Size Management**: Mechanisms for handling large knowledge bases

### Known Gap

This version exists in migration_history but was never published as a GitHub Release. Work transitioned directly to v2.7.0.

---

## [2.5.0] - 2025-10-04

**Note**: Partial release - only some templates (template-worker-aget confirmed).

### Added

- **Validation Framework**: Contract testing infrastructure
- **Quality Gates**: Validation checkpoints for agent compliance

**See**: [template-worker-aget v2.5.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.5.0) for details

---

## [2.4.0] - 2025-10-03

### Added

- **Clarity Enhancements**: Improved documentation and agent instructions
- **Configuration Refinements**: Streamlined AGENTS.md templates

**See**: [template-worker-aget v2.4.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.4.0)

---

## [2.3.0] - 2025-10-02

### Added

- **Collaboration Infrastructure**: Patterns for human-AI collaboration
- **Session Protocols**: Standards for agent session management

**See**: [template-worker-aget v2.3.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.3.0)

---

## [2.2.0] - 2025-09-30

### Added

- **Intelligence-Enabled Specification Creation**: AI-assisted spec generation
- **Specification Templates**: Structured formats for requirement documentation

**See**: [template-worker-aget v2.2.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.2.0)

---

## [2.1.0] - 2025-09-29

**The Ownership Release**

### Added

- **Ownership Model**: Agents manage specific repositories and artifacts
- **Responsibility Boundaries**: Clear definitions of agent scope and authority

**See**: [template-worker-aget v2.1.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.1.0)

---

## [2.0.0] - 2025-09-XX

**Initial Public Framework Architecture**

### Added

- **AGET Framework Core**: CLI-based human-AI collaborative coding framework
- **Template System**: Reusable agent configurations (Worker, Advisor, Supervisor)
- **AGENTS.md Standard**: Configuration file format for CLI tool integration
- **Contract Testing**: Validation system for agent compliance
- **.aget/ Directory Structure**: Standard configuration and pattern storage

### Core Principles Established

- AGET = Configuration & Lifecycle Management (not a runtime)
- Conversation layer only (no code execution)
- Optimizes for human-AI collaboration quality

**Breaking Changes from v1.x**

- Complete architecture redesign
- New configuration format
- Template-based approach replaces ad-hoc configurations

---

## Historical Version Gaps

**Transparency Note**: The aget/ core repository had incomplete GitHub Release history prior to v2.11.0 due to the private→public transition process focusing on content visibility without establishing comprehensive public release discipline.

**Gaps**:
- v2.5.0 through v2.9.0: No aget/ releases (template releases exist)
- v2.6.0: No releases for any repository
- v2.9.0: Partial release (4/7 templates)

**Root Cause**: Internal versioning (version.json) was maintained rigorously, but public releases (GitHub Releases) were inconsistent.

**Resolution**: v2.11.0 established public framework governance with R-PUB-001 requirements and automated post-release validation.

**See**: [VERSION_HISTORY.md](docs/VERSION_HISTORY.md) for complete gap analysis

---

## Version Support

**Latest Stable**: v3.4.0
**Support Window**: Latest release receives full support (bug fixes, enhancements)
**Previous Minor** (v3.3.x): Security fixes only
**Older Versions**: No active support (upgrade recommended)

---

## How to Upgrade

See [UPGRADING.md](docs/UPGRADING.md) for version-specific migration guides and safe upgrade procedures.

---

## Links

- [GitHub Releases](https://github.com/aget-framework/aget/releases)
- [Version History](docs/VERSION_HISTORY.md)
- [Versioning Policy](docs/VERSIONING.md)
- [Release Process](docs/RELEASES.md)
- [Upgrade Guide](docs/UPGRADING.md)
- [Issue Tracker](https://github.com/aget-framework/aget/issues)

---

*CHANGELOG.md - Updated 2026-01-18*
*Maintained by: private-aget-framework-AGET*
