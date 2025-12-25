# Changelog

All notable changes to the AGET Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: This CHANGELOG reflects the public aget-framework/aget repository. For complete version history including release gaps and template-specific changes, see [VERSION_HISTORY.md](docs/VERSION_HISTORY.md).

---

## [Unreleased]

No unreleased changes at this time.

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

**Latest Stable**: v2.12.0
**Support Window**: Latest release receives full support (bug fixes, enhancements)
**Previous Minor** (v2.11.x): Security fixes only
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

*CHANGELOG.md - Generated 2025-12-24*
*Maintained by: private-aget-framework-AGET*
