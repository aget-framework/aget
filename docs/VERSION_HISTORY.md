# AGET Framework Version History

This document provides a complete timeline of AGET Framework versions and their release status across all repositories.

**Legend**:
- ✅ GitHub Release exists
- ❌ No GitHub Release (gap)
- ⚠️ Partial (some repos only)
- 🔄 Retroactive (created after work completed)

---

## Current Version

**v3.9.0** (2026-03-15) - Governance Enforcement

All 13 repositories (aget + 12 templates) at v3.9.0: ✅

---

## Version Timeline

### v3.9.0 (2026-03-15) ✅

**Theme**: Governance Enforcement — release readiness, version management, process standardization

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + SOP release process v1.28 + GOVERNANCE_PRINCIPLES |
| template-advisor-aget | ✅ | Version bump + CHANGELOG |
| template-analyst-aget | ✅ | Version bump + CHANGELOG |
| template-architect-aget | ✅ | Version bump + CHANGELOG |
| template-consultant-aget | ✅ | Version bump + CHANGELOG |
| template-developer-aget | ✅ | Version bump + CHANGELOG |
| template-executive-aget | ✅ | Version bump + CHANGELOG |
| template-operator-aget | ✅ | Version bump + CHANGELOG |
| template-researcher-aget | ✅ | Version bump + CHANGELOG |
| template-reviewer-aget | ✅ | Version bump + CHANGELOG |
| template-spec-engineer-aget | ✅ | Version bump + CHANGELOG |
| template-supervisor-aget | ✅ | Version bump + CHANGELOG |
| template-worker-aget | ✅ | Version bump + CHANGELOG |

**Key Features**:
- SOP release process v1.28 with Phase -1 (readiness assessment) and Phase 0.85 (scope lock)
- GOVERNANCE_PRINCIPLES.md published (meta-principles for governance rules)
- PROJECT_PLAN template with Gate 0 (due diligence)
- version_bump.py v1.5 covering 5 artifact types (version.json, README.md, AGENTS.md, codemeta.json, CITATION.cff)
- 135+ contract tests passing
- /aget-create-project principles enforcement (ADR-008 Advisory → Strict for MP-1/MP-5)

**See**: CHANGELOG.md for detailed changes

---

### v3.8.0 (2026-03-08) ✅

**Theme**: Governance Maturation — principle codification, deliverable conformance

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + governance principles + conformance tooling |
| template-advisor-aget | ✅ | Version bump + CHANGELOG |
| template-analyst-aget | ✅ | Version bump + CHANGELOG |
| template-architect-aget | ✅ | Version bump + CHANGELOG |
| template-consultant-aget | ✅ | Version bump + CHANGELOG |
| template-developer-aget | ✅ | Version bump + CHANGELOG |
| template-executive-aget | ✅ | Version bump + CHANGELOG |
| template-operator-aget | ✅ | Version bump + CHANGELOG |
| template-researcher-aget | ✅ | Version bump + CHANGELOG |
| template-reviewer-aget | ✅ | Version bump + CHANGELOG |
| template-spec-engineer-aget | ✅ | Version bump + CHANGELOG |
| template-supervisor-aget | ✅ | Version bump + CHANGELOG |
| template-worker-aget | ✅ | Version bump + CHANGELOG |

**Key Features**:
- Meta-principles codification (GOVERNANCE_PRINCIPLES.md draft)
- Deliverable conformance tooling and gap analysis
- Loading Dock anti-pattern defense (L656 — deployment verification before next-cycle planning)
- Homepage quality rubric (L657 — 5 dimensions, L0-L3)
- wake_up.py v2.0.0 rolled out to all 12 templates
- DEPLOYMENT_SPEC reconciliation (6 divergences resolved)
- post_release_validation.py check 15 (template content verification)

**See**: CHANGELOG.md for detailed changes

---

### v3.7.0 (2026-03-01) ✅

**Theme**: Quality Reconciliation — content integrity, SOP lifecycle, positioning reframe

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + content integrity + SOP lifecycle |
| template-advisor-aget | ✅ | Version bump + CHANGELOG |
| template-analyst-aget | ✅ | Version bump + CHANGELOG |
| template-architect-aget | ✅ | Version bump + CHANGELOG |
| template-consultant-aget | ✅ | Version bump + CHANGELOG |
| template-developer-aget | ✅ | Version bump + CHANGELOG |
| template-executive-aget | ✅ | Version bump + CHANGELOG |
| template-operator-aget | ✅ | Version bump + CHANGELOG |
| template-researcher-aget | ✅ | Version bump + CHANGELOG |
| template-reviewer-aget | ✅ | Version bump + CHANGELOG |
| template-spec-engineer-aget | ✅ | Version bump + CHANGELOG |
| template-supervisor-aget | ✅ | Version bump + CHANGELOG |
| template-worker-aget | ✅ | Version bump + CHANGELOG |

**Key Features**:
- Content integrity remediation (claim-vs-reality drift)
- SOP lifecycle governance improvements
- Positioning reframe (AGET as governance framework, not autonomous agent platform)
- Release observability enhancements

**See**: CHANGELOG.md for detailed changes

---

### v3.6.0 (2026-02-21) ✅

**Theme**: Infrastructure Maturation — observability, content integrity, ontology

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + 5 observability scripts + 4 validators |
| template-advisor-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-analyst-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-architect-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-consultant-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-developer-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-executive-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-operator-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-researcher-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-reviewer-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-spec-engineer-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-supervisor-aget | ✅ | aget-studyup + platform claims + study_up.py |
| template-worker-aget | ✅ | aget-studyup + platform claims + study_up.py |

**Key Features**:
- Release observability tooling (L605): validation_logger, run_gate, release_snapshot, propagation_audit, health_logger
- Content integrity remediation (L607, L608): 6 dimensions of claim-vs-reality drift fixed
- Canonical scripts v2.0.0 (CSE-001): C3+C1 architecture (config-driven + hook-based extensions)
- Universal skill: aget-studyup (14th universal, all 12 templates)
- Vocabulary precision: 4 compliance behavioral terms (VOCABULARY_SPEC v1.16.0)
- Platform claims: Claude Code, Codex CLI, Gemini CLI (Cursor/Aider → Experimental)
- DEPLOYMENT_SPEC_v3.6.0.yaml for fleet deployment
- Conformance tool v1.3.0 with v3.6.0 support

**See**: CHANGELOG.md for detailed changes

---

### v3.5.0 (2026-02-14) ✅

**Theme**: Archetype Customization + Issue Governance

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + 26 archetype skills + issue governance |
| template-advisor-aget | ✅ | 2 archetype skills + ontology |
| template-analyst-aget | ✅ | 2 archetype skills + ontology |
| template-architect-aget | ✅ | 2 archetype skills + ontology |
| template-consultant-aget | ✅ | 2 archetype skills + ontology |
| template-developer-aget | ✅ | 3 archetype skills + ontology |
| template-executive-aget | ✅ | 2 archetype skills + ontology |
| template-operator-aget | ✅ | 2 archetype skills + ontology |
| template-researcher-aget | ✅ | 2 archetype skills + ontology |
| template-reviewer-aget | ✅ | 2 archetype skills + ontology |
| template-spec-engineer-aget | ✅ | 2 archetype skills + ontology |
| template-supervisor-aget | ✅ | 3 archetype skills + ontology |
| template-worker-aget | ✅ | 2 archetype skills + ontology |

**Key Features**:
- 26 archetype-specific skills across 12 archetypes
- aget-file-issue universal skill (L520 compliance)
- Archetype ontologies (ONTOLOGY_{archetype}.yaml) in SKOS+EARS format
- Skills specification infrastructure (INDEX.md, SKILL_VOCABULARY.md, ONTOLOGY_skills.yaml)
- DEPLOYMENT_SPEC_v3.5.0.yaml

**See**: CHANGELOG.md for detailed changes

---

### v3.4.0 (2026-01-18) ✅

**Theme**: Session Skills Maturity + Governance Formalization

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + session enhancements |
| template-advisor-aget | ✅ | Session protocol updates |
| template-analyst-aget | ✅ | Session protocol updates |
| template-architect-aget | ✅ | Session protocol updates |
| template-consultant-aget | ✅ | Session protocol updates |
| template-developer-aget | ✅ | Session protocol updates |
| template-executive-aget | ✅ | Session protocol updates |
| template-operator-aget | ✅ | Session protocol updates |
| template-researcher-aget | ✅ | Session protocol updates |
| template-reviewer-aget | ✅ | Session protocol updates |
| template-spec-engineer-aget | ✅ | Session protocol updates |
| template-supervisor-aget | ✅ | Session protocol updates |
| template-worker-aget | ✅ | Session protocol updates |

**Key Features**:
- Re-entrancy guard for wind_down (CAP-SESSION-010)
- Calendar awareness in wake_up (CAP-SESSION-011)
- Cross-CLI validation (Claude Code, Codex CLI, Gemini CLI)
- Governance formalization patterns
- Self-upgrade validation (L560)

**See**: CHANGELOG.md for detailed changes

---

### v3.3.1 (2026-01-11) ✅

**Theme**: Repository Visibility Governance

**Status**: Complete release (all repos)

**Key Features**: R-REL-016/017/018 repository visibility rules

**See**: CHANGELOG.md for detailed changes

---

### v3.3.0 (2026-01-10) ✅

**Theme**: Shell Integration + Executable Knowledge Ontology

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework + shell integration |
| template-advisor-aget | ✅ | SKOS vocabulary added |
| template-analyst-aget | ✅ | SKOS vocabulary added |
| template-architect-aget | ✅ | SKOS vocabulary added |
| template-consultant-aget | ✅ | SKOS vocabulary added |
| template-developer-aget | ✅ | SKOS vocabulary added |
| template-executive-aget | ✅ | SKOS vocabulary added |
| template-operator-aget | ✅ | SKOS vocabulary added |
| template-researcher-aget | ✅ | SKOS vocabulary added |
| template-reviewer-aget | ✅ | SKOS vocabulary added |
| template-spec-engineer-aget | ✅ | SKOS vocabulary added |
| template-supervisor-aget | ✅ | SKOS vocabulary added |
| template-worker-aget | ✅ | SKOS vocabulary added |

**Key Features**:
- Shell orchestration: aget.zsh, profiles.zsh (5 CLI backends)
- SKOS-compliant template vocabularies (12 templates)
- Ontology-driven agent creation (L481, L482)
- AGET_EXECUTABLE_KNOWLEDGE_SPEC.md
- AGET_EVOLUTION_SPEC.md
- 18 new L-docs (L451-L503)
- validate_ontology_compliance.py
- generate_template_ontology.py
- SOP_point_upgrade.md (L444 conformance)
- R-REL-015: "We do not leave published templates behind"

**See**: CHANGELOG.md for detailed changes

---

### v3.0.0 - v3.2.1 (2025-12-28 to 2026-01-04)

**Versions**: v3.0.0, v3.1.0, v3.2.0, v3.2.1

**Status**: Released (see CHANGELOG.md for details)

**Note**: VERSION_HISTORY.md was not updated during v3.x releases. See CHANGELOG.md for complete v3.0.0-v3.2.1 history.

---

### v2.11.0 (2025-12-24) ✅

**Theme**: Memory Architecture + L352 Traceability + Version Migration

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ | Core framework |
| template-supervisor | ✅ | Supervisor template |
| template-worker | ✅ | Worker template |
| template-advisor | ✅ | Advisor template |
| template-consultant | ✅ | Consultant template |
| template-developer | ✅ | Developer template |
| template-spec-engineer | ✅ | Spec engineer template |

**Key Features**:
- Memory Architecture (L335): 6-layer information model
- L352 Traceability Pattern: Five-tier requirement-to-test traceability
- Version Migration (R-REL-006): Manager self-updates
- 40 contract tests with full traceability
- Configurable wake-up output

**See**: [AGET_DELTA_v2.11.md](../specs/deltas/AGET_DELTA_v2.11.md)

---

### v2.10.0 (2025-12-13) 🔄

**Theme**: Capability Composition Architecture

**Status**: Complete release (retroactively created 2025-12-24)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ✅ 🔄 | Created 2025-12-24 |
| template-supervisor | ✅ 🔄 | Created 2025-12-24 |
| template-worker | ✅ 🔄 | Created 2025-12-24 |
| template-advisor | ✅ 🔄 | Created 2025-12-24 |
| template-consultant | ✅ 🔄 | Created 2025-12-24 |
| template-developer | ✅ 🔄 | Created 2025-12-24 |
| template-spec-engineer | ✅ 🔄 | Created 2025-12-24 |

**Key Features**:
- 6 agent type specifications
- Executive Advisor pattern (5W+H knowledge architecture)
- Domain Specialist pattern (structured outputs)
- L330-L332 learnings (knowledge inheritance, theoretical grounding)

**Note**: Work completed 2025-12-13. GitHub Releases created retroactively on 2025-12-24 as part of public framework governance enhancement (Gap Analysis → L358).

**See**: aget/specs/deltas/AGET_DELTA_v2.10.md (if exists)

---

### v2.9.0 (2025-12-01) ⚠️

**Theme**: Information Storage Standardization

**Status**: Partial release (4/7 repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ❌ | No release |
| template-supervisor | ❌ | No release |
| template-worker | ❌ | No release |
| template-advisor | ✅ | Released 2025-11-24 |
| template-consultant | ✅ | Released 2025-11-24 |
| template-developer | ✅ | Released 2025-11-24 |
| template-spec-engineer | ✅ | Released 2025-11-24 |

**Key Features**: Core specifications, vocabulary standards

**Known Gap**: Only advisor-family templates received GitHub Releases

---

### v2.8.0 (2025-11-08) ✅

**Theme**: Planning & Infrastructure

**Status**: Complete release (all repos)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ❌ | No release (core had no releases until v2.11.0) |
| template-supervisor | ✅ | Released 2025-11-10 |
| template-worker | ✅ | Released 2025-11-10 |
| template-advisor | ✅ | Released 2025-11-10 |
| template-consultant | ✅ | Released 2025-11-10 |
| template-developer | ✅ | Released 2025-11-10 |
| template-spec-engineer | ✅ | Released 2025-11-10 |

**Key Features**: Friction reduction, enhancement filing protocol, planning framework

---

### v2.7.0 (2025-10-13) ✅

**Theme**: Portfolio Governance

**Status**: Partial release (most templates)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ❌ | No release |
| template-supervisor | ✅ | Released 2025-10-13 |
| template-worker | ✅ | Released 2025-10-13 |
| template-advisor | ✅ | Released 2025-10-13 |
| template-consultant | ⚠️ | Uncertain |
| template-developer | ✅ | Released 2025-10-20 |
| template-spec-engineer | ⚠️ | Uncertain |

**Key Features**: Portfolio field, naming conventions, advisor personas

---

### v2.6.0 (2025-10-12) ❌

**Theme**: Size Management

**Status**: No GitHub Releases (known gap)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ❌ | Migration history exists, no tag/release |
| All templates | ❌ | No releases created |

**Known Gap**: Version documented in migration history but no releases published

---

### v2.5.0 (2025-10-06) ⚠️

**Theme**: Validation Framework

**Status**: Partial release (some templates)

| Repository | Release | Notes |
|------------|---------|-------|
| aget | ❌ | No release |
| template-worker | ✅ | Released 2025-10-04 |
| Others | ⚠️ | Uncertain/incomplete |

**Known Gap**: Incomplete release coverage

---

### v2.4.0 and Earlier

See individual repository release pages for v2.0-v2.4 history.

Most repositories have GitHub Releases for v2.1-v2.4 created during early framework development.

---

## Known Gaps Summary

### Complete Gaps (No Releases Anywhere)

- **v2.6.0**: Documented in migration history, no releases created

### Partial Gaps (Some Repos Missing)

- **v2.9.0**: Only advisor-family templates (4/7)
- **v2.7.0**: Most templates, but some uncertain
- **v2.5.0**: Incomplete coverage

### Core Repository (aget/) Historical Gap

The core framework repository (`aget/`) did NOT have GitHub Releases until v2.11.0, despite having version history documented in migration_history.

**Affected Versions**: v2.5.0, v2.6.0, v2.7.0, v2.8.0, v2.9.0
**Reason**: Private→public transition focused on making repos visible without establishing public release process
**Addressed**: v2.10.0 created retroactively (2025-12-24), v2.11.0 includes complete release process

---

## Why Gaps Exist

**Root Cause**: Private→public transition (2024-2025)

During the transition from private experimentation to public framework:
- **Internal versioning** (version.json, migration_history) was maintained ✅
- **Public releases** (GitHub Releases, tags, announcements) were inconsistent ❌

**Analysis**: See `.aget/evolution/L358_tags_vs_releases_github.md` in the framework manager agent

**Resolution**: Public framework governance established (v2.11.0+) with:
- Post-release validation (user-visible state)
- Organization homepage currency
- Complete release specifications (R-PUB-001)

---

## Going Forward (v3.9.0+)

**Commitment**: Every version increment will include:

1. ✅ Git tags (all 13 repos)
2. ✅ GitHub Releases (all 13 repos)
3. ✅ Organization homepage update
4. ✅ CHANGELOG entries
5. ✅ DEPLOYMENT_SPEC (fleet deployment target state)
6. ✅ Migration guide (if breaking)

**Validation**: Release observability tooling ensures completeness:
- `validation_logger.py` — structured pass/fail logging
- `run_gate.py` — gate execution records
- `release_snapshot.py` — pre-release state capture
- `propagation_audit.py` — cross-repo consistency
- `health_logger.py` — KB health tracking

**Transparency**: Version gaps acknowledged, not hidden

---

## How to Access Versions

### Latest Stable

Visit: https://github.com/aget-framework/aget/releases

### Specific Version

```bash
# View all releases
gh release list --repo aget-framework/aget

# Clone specific version
git clone --branch v3.9.0 https://github.com/aget-framework/aget.git

# Checkout existing clone
git checkout v3.9.0
```

### Version Compatibility

All templates share the same major.minor version:
- aget: v3.9.0
- template-*: v3.9.0

Templates at v3.x.y are compatible with aget v3.x.z (patch versions independent).

---

## Contributing

Found a version gap or inconsistency? Please file an issue:
https://github.com/aget-framework/aget/issues

We acknowledge historical gaps transparently and focus on complete releases going forward.

---

*VERSION_HISTORY.md - Complete version timeline for AGET Framework*
*Last Updated: 2026-03-15*
*Maintained by: aget-framework*
