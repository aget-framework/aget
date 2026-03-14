# SOP: Release Process

**Version**: 1.29
**Created**: 2025-11-30
**Updated**: 2026-03-08
**Owner**: private-aget-framework-AGET

**Implements**: R-REL-001-* (5 requirements), R-REL-006 through R-REL-020, R-REL-024, R-REL-025, R-REL-026, R-REL-027, R-REL-030 through R-REL-038, R-REL-042, R-REL-VER-001, R-LIC-001, R-SPEC-010, R-ISSUE-007, R-ISSUE-008, CAP-REL-021 (Persistent Validation Logging), CAP-REL-022 (Gate Execution Enforcement), CAP-REL-023 (Release State Snapshots), CAP-REL-024 (Propagation Audit), CAP-REL-025 (Healthcheck Persistence)
- R-REL-001-01: Commit all repos locally before pushing
- R-REL-001-02: Verify version consistency before pushing
- R-REL-001-03: Push aget/ core first (dependency root)
- R-REL-001-04: Push templates in alphabetical order
- R-REL-001-05: If any push fails, abort and report
- R-REL-006: Managing agent updates version before release (L357)
- R-REL-007: PROJECT_PLAN gates derive from RELEASE_VERIFICATION_CHECKLIST (L376)
- R-REL-008: Version Inventory - ALL version-bearing files must be updated atomically (L429)
- R-REL-009: Pre-Publication Content Security - Scan for proprietary info before pushing (L430)
- R-REL-010: Organization Homepage Update - Update org homepage within release session (L431)
- R-REL-011: CHANGELOG Discipline - CHANGELOG.md entry required before tagging (L431)
- R-REL-013: Scope Consolidation - ALL PROJECT_PLANs targeting version must be consolidated (L465)
- R-REL-014: Protocol Verification - Verify session protocols before release (L491)
- R-REL-015: Template Ontology Conformance - ALL published templates must conform or be deprecated
- R-REL-016: Branch Verification - All repos must be on main branch before push (L505)
- R-REL-017: Branch Protection Verification - All repos must have branch protection enabled (L508)
- R-REL-018: Template Visibility Verification - All templates have consistent visibility or documented exception (L509)
- R-REL-019: Release-to-Fleet Handoff - Create handoff artifact with governance checklist and notify supervisor (L511, L562)
- R-REL-020: VERSION_SCOPE Required - VERSION_SCOPE document required for minor/major releases (PROJECT_PLAN_version_scope_standardization)
- R-REL-024: Self-Upgrade Validation - Managing agent operationally validates upgrade before public release (L560)
- R-REL-027: Template Deep Conformance - ALL templates must pass deep conformance check before release
- R-REL-030: Dogfood Validation - Pilot validation on template/instance before public release (L576)
- R-REL-031: Conformance Regression - Existing instance must not regress (L576)
- R-REL-032: Rollback Plan - Documented rollback strategy before release (L576)
- R-REL-033: Smoke Test - Post-release verification defined (L576)
- R-REL-034: Monitoring Channel - Feedback/issue channel identified (L576)
- R-REL-035: GitHub Release Required - `gh release create` for ALL tagged repos (L579)
- R-REL-036: Per-Template CHANGELOG - Each template CHANGELOG.md MUST have version entry (L579)
- R-REL-037: Metadata Files - codemeta.json and CITATION.cff MUST reflect current version (L579)
- R-REL-038: Deployment Spec Required - DEPLOYMENT_SPEC_vX.Y.Z.yaml MUST exist before tagging release (L581)
- R-REL-039: Version-Bearing Spec Inventory - SOP SHALL maintain inventory of specs with embedded versions (L584)
- R-REL-040: Version-Bearing Spec Validation - BEFORE release, ALL version-bearing specs MUST match release version (L584)
- R-REL-041: Spec Creation SOP Integration - WHEN creating spec with version field, add to inventory (L584)
- R-REL-042: Skill Dependency Validation - BEFORE release, ALL templates MUST pass validate_skill_dependencies.py --check (L586, L596)
- R-REL-VER-001: Version Inventory Coherence - ALL version-bearing files must be consistent (L444)

**Pain Point**: L333 (Governance Grounding), L429 (Version Inventory), L430 (Content Security), L431 (Release Artifacts), L444 (Version Inventory Coherence), L465 (Scope Consolidation), L505 (Branch Verification), L508 (Branch Protection), L509 (Visibility Consistency), L511 (Release-to-Fleet Propagation), L520 (Issue Governance), L560 (Release Self-Validation), L576 (Release Quality Validation), L579 (Version-Bearing File Enumeration Gap), L581 (Process vs State Documentation Gap), L582 (Universal Skill Customization Preservation Gap), L584 (Public-Facing Version Indicator Gap), L596 (Workspace-Local Remediation Propagation Gap), L605 (Release Observability and Enforcement Gap), enhancement aget#1 (Release Coordination)
**See**: aget/specs/AGET_FRAMEWORK_SPEC_v2.11.md Section R-REL-001
**Tests**: tests/test_release_coordination.py::TestMultiRepoRelease
**Patterns**: L352 (Traceability), L376 (Checklist-Driven Design), L406 (Systematic Validation)

---

## Purpose

Standard operating procedure for releasing updates to aget-framework templates.

---

## Scope

This SOP covers releases for:
- Individual templates (template-*-aget/)
- Core framework module (aget/)

**Note**: Each template is an independent git repository. Releases are per-template, not unified.

---

## Definition of Done (L553)

**⚠️ A release is NOT complete when code is pushed. A release is complete when users can discover it.**

### User-Centric Completion Criteria

A release is DONE when ALL of these conditions are met:

| Outcome | Verification | SOP Phase |
|---------|--------------|-----------|
| **Discoverable**: User can find version at org homepage | Badge shows vX.Y.Z at github.com/aget-framework | Phase 4.3 |
| **Accessible**: User can download/clone tagged version | GitHub Release exists with "Latest" badge | Phase 3.3 |
| **Documented**: User can read what changed | CHANGELOG.md entry + release notes exist | Phase 2, Phase 3.2 |
| **Consistent**: All repos show same version | version.json, AGENTS.md, manifest.yaml aligned | Phase 3.1 |
| **Validated**: Automated checks pass | `post_release_validation.py` exit code 0 | Phase 4.1 |

### What "DONE" Does NOT Mean

- ❌ Tags pushed to remote (necessary but not sufficient)
- ❌ CHANGELOG updated (necessary but not sufficient)
- ❌ PROJECT_PLAN marked COMPLETE (internal tracking only)
- ❌ Commits on main branch (internal state only)

### Enforcement

1. **SOP Phases 1-3**: Create artifacts (internal state)
2. **SOP Phase 4**: Validate user-visible outcomes (BLOCKING)
3. **SOP Phase 5**: Announce (optional, only after Phase 4 passes)

**PROJECT_PLAN Integration**: Release PROJECT_PLANs MUST include a gate that explicitly:
- References SOP Phase 4 as BLOCKING
- Runs `post_release_validation.py --version X.Y.Z`
- Achieves exit code 0 before marking COMPLETE

See: `.aget/evolution/L553_definition_of_done_release.md`

---

## Critical: Release Scope Consolidation (L465)

**⚠️ WARNING: Multiple PROJECT_PLANs targeting the same version create coordination risk and user confusion.**

### Lesson Learned (L465)

v3.3.0 planning revealed scope fragmentation across 5 documents:
- PROJECT_PLAN_v3.3.0_shell_integration.md (Shell only)
- PROJECT_PLAN_executable_knowledge_ontology_v1.0.md (EKO foundation)
- PROJECT_PLAN_directory_semantics_reconciliation_v1.0.md (Directory semantics)
- PROJECT_PLAN_core_entity_vocabulary_v1.0.md (Identified dependencies)
- ROADMAP_v3.3.0_specification_maturity.md (Lightweight L-doc list)

**Root Cause**: No SOP requirement for pre-release scope consolidation. Each work stream created independent plans without coordination.

**User Signal**: "v3.3 seems light, why?" — Homepage showed 5 items while actual scope included 15+ deliverables.

### Requirement: R-REL-013 (Scope Consolidation)

**BEFORE** Phase 0 (Manager Migration)

**Cross-reference**: After scope consolidation, apply `aget/sops/SOP_release_scope_decision.md` for scope governance (priority classification, value-cost assessment, Scope_Lock).

**THE** release manager SHALL verify scope consolidation:

1. [ ] Audit all PROJECT_PLANs targeting this version
2. [ ] Audit all ROADMAPs targeting this version
3. [ ] Create consolidated PROJECT_PLAN_vX.Y.Z_release.md (if multiple plans exist)
4. [ ] Map each source plan's deliverables to consolidated gates
5. [ ] Mark superseded plans with: `Superseded by PROJECT_PLAN_vX.Y.Z_release.md`
6. [ ] Update organization homepage to reflect consolidated scope

### Scope Consolidation Search

```bash
# Find all plans targeting version
VERSION="X.Y.Z"
grep -l "v${VERSION}\|${VERSION}" planning/PROJECT_PLAN_*.md planning/ROADMAP_*.md
```

**Expected Output**:
- 0-1 files: Scope is consolidated (proceed)
- 2+ files: Consolidation required (STOP and consolidate first)

### Consolidated Release Plan Template

A consolidated release plan MUST include:

| Section | Content |
|---------|---------|
| Work Streams | Table mapping source plans to gates |
| Scope | Consolidated in/out scope from all sources |
| Traceability | Work Streams → Gates mapping |
| Superseded Plans | List with status |
| SOP References | R-REL-* requirements addressed |

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| 2+ PROJECT_PLANs for same version | Coordination risk | Consolidate |
| Homepage shows fewer items than planned | User confusion | Update homepage |
| "I'll coordinate as I go" | Scope drift | Consolidate first |
| No single release plan | Unclear ownership | Create consolidated plan |

### Pattern: Single Source of Truth for Version Scope

Just as `version.json` is the PRIMARY source for version number (R-REL-VER-001), `PROJECT_PLAN_vX.Y.Z_release.md` is the PRIMARY source for version scope.

---

## Critical: VERSION_SCOPE Requirement (R-REL-020)

**⚠️ WARNING: Releases without VERSION_SCOPE documents lack explicit scope definition and success criteria.**

### Requirement: R-REL-020 (VERSION_SCOPE Required)

**BEFORE** releasing a minor or major version,
**THE** release manager SHALL create a VERSION_SCOPE document
**THAT** defines scope, objectives, work items, and success criteria.

**Template**: `planning/TEMPLATE_VERSION_SCOPE.md`

**File Location**: `planning/VERSION_SCOPE_vX.Y.Z.md`

### Requirement: R-REL-025 (Value-Cost Assessment)

**BEFORE** pushing a release to fleet,
**THE** release manager SHALL complete the Value-Cost Assessment section
**THAT** evaluates whether the release justifies migration effort.

**Value Dimensions** (65% weight):
| Dimension | Weight | Criteria |
|-----------|--------|----------|
| New capabilities | 25% | User-facing features added |
| Bug fixes | 15% | Issues resolved |
| Performance/quality | 15% | Non-functional improvements |
| Developer experience | 10% | Easier to use/extend |

**Cost Dimensions** (35% weight - negative):
| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Breaking changes | -20% | Higher = more breaking |
| New dependencies | -5% | Additional requirements |
| Process changes | -5% | New workflows to learn |
| Validation effort | -5% | Testing burden on adopters |

**Scoring Guide**:
| Score | Classification | Recommendation |
|-------|---------------|----------------|
| 8-10 | High Value | Strong push to fleet |
| 5-7 | Moderate Value | Standard rollout |
| 3-4 | Low Value | Consider bundling with next release |
| 1-2 | Governance Only | Defer or bundle |

**Red Flag**: Score <3 = "light migration" — consider bundling with next release.

### Requirement: R-REL-026 (Migration Validation Script)

**WHEN** releasing a version with new capabilities,
**THE** release manager SHALL create a version-specific validation script:

**Location**: `.aget/patterns/upgrade/validate_vX.Y.Z.py`

**Required Checks**:
1. Core checks (version.json, AGENTS.md header, required directories)
2. Session protocol checks (wake_up, sanity_check, wind_down)
3. Version-specific feature checks (new capabilities introduced)

**Usage**:
```bash
# Self-validation (Phase 0.7)
python3 .aget/patterns/upgrade/validate_vX.Y.Z.py

# Fleet validation (by supervisor or pilots)
python3 .aget/patterns/upgrade/validate_vX.Y.Z.py --target /path/to/agent
python3 .aget/patterns/upgrade/validate_vX.Y.Z.py --json  # For automation
```

**Script Template**: See `validate_v3.4.0.py` as exemplar.

**Rationale**: Enables fleet agents to validate their own migrations and produce conformance reports.

### When VERSION_SCOPE is Required

| Release Type | VERSION_SCOPE | Rationale |
|--------------|:-------------:|-----------|
| Major (vX.0.0) | **REQUIRED** | Breaking changes need explicit scope |
| Minor (vX.Y.0) | **REQUIRED** | New features need explicit scope |
| Patch (vX.Y.Z) | OPTIONAL | Bug fixes can reference parent version |

### VERSION_SCOPE Creation Checklist

**BEFORE** Phase 0 (Pre-Release Validation):

1. [ ] Create `planning/VERSION_SCOPE_vX.Y.Z.md` from `TEMPLATE_VERSION_SCOPE.md`
2. [ ] Define **MVP (Must Ship)** items — blocking release
3. [ ] Define **Full Scope (Nice to Have)** items — included if ready
4. [ ] Define **Out of Scope** with rationale and deferral targets
5. [ ] Set **Success Criteria** with measurable targets
6. [ ] Include **Release Objectives** with success metrics
7. [ ] Populate **Release Checklist** for all 4 phases (0-3)
8. [ ] Get VERSION_SCOPE approved (status → READY FOR RELEASE)

### VERSION_SCOPE Status Lifecycle

| Status | Meaning |
|--------|---------|
| PLANNING | Initial draft, scope being defined |
| READY FOR RELEASE | Scope approved, pre-release validation complete |
| RELEASED | Release execution complete |
| CANCELLED | Release abandoned (rationale documented) |

### VERSION_SCOPE Verification

```bash
VERSION="X.Y.Z"

# Check VERSION_SCOPE exists
[ -f "planning/VERSION_SCOPE_v${VERSION}.md" ] && echo "✅ VERSION_SCOPE exists" || echo "❌ VERSION_SCOPE MISSING"

# Check required sections
grep -cE "MVP \(Must Ship\)|Full Scope|Out of Scope|Success Criteria|Release Checklist" \
  planning/VERSION_SCOPE_v${VERSION}.md | xargs -I {} test {} -ge 5 && echo "✅ Required sections" || echo "❌ Missing sections"

# Check status
grep -q "Status.*READY FOR RELEASE\|Status.*RELEASED" \
  planning/VERSION_SCOPE_v${VERSION}.md && echo "✅ Status valid" || echo "⚠️ Status: check manually"
```

### Skip Conditions

VERSION_SCOPE MAY be skipped for patch releases (vX.Y.Z where only Z changes):

1. [ ] Bug fix only — no new features
2. [ ] No breaking changes
3. [ ] Rationale documented in commit message

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "Let me just release..." without VERSION_SCOPE | Undefined scope, no success criteria | Create VERSION_SCOPE first |
| No MVP distinction | Unclear release readiness | Define MVP vs Full Scope |
| Missing success criteria | No way to measure release quality | Add measurable criteria |
| PLANNING status at release time | Unapproved scope | Update status before release |

### Reconstructed VERSION_SCOPE Documents

For historical releases without VERSION_SCOPE, reconstructed documents MAY be created:

1. Use `[RECONSTRUCTED]` marker in header
2. Source from: release-notes/, CHANGELOG.md, PROJECT_PLANs
3. Clearly note reconstruction date and sources

**Example**: `VERSION_SCOPE_v2.10.0.md [RECONSTRUCTED]`

### References

- `planning/TEMPLATE_VERSION_SCOPE.md` — VERSION_SCOPE template
- `planning/PROPOSAL_version_scope_vocabulary.md` — Vocabulary terms
- `planning/PROPOSAL_version_scope_spec_requirements.md` — Spec requirements (R-REL-020 through R-REL-028)
- `PROJECT_PLAN_version_scope_standardization_v1.0.md` — Standardization project

---

## Pre-Release Checklist

### Governance Grounding (L333)

Before planning any release, consult governance specifications:

- [ ] Consulted AGET_VERSIONING_CONVENTIONS.md (lines 142-148)
- [ ] Template version bumps identified (all 6 templates)
- [ ] Core version bump planned (aget/)
- [ ] CHANGELOG entries drafted
- [ ] Release plan cites governance spec with line references

### Technical Readiness

- [ ] Changes tested locally
- [ ] CHANGELOG.md updated in target template
- [ ] Version bumped in `.aget/version.json`
- [ ] No breaking changes (or migration guide prepared)
- [ ] README.md current

---

## Critical: Version Inventory - ALL Files Must Be Updated (L429)

**⚠️ WARNING: Updating only `version.json` leaves 15+ files with stale versions.**

### Lesson Learned (L429)

v3.1.0 was released but only `version.json` was updated. Post-release validation revealed:
- README.md showed v3.0.0 (user-facing!)
- AGENTS.md showed v3.0.0
- governance/*.md showed v3.0.0
- All .aget/**/*.yaml files showed v3.0.0

**Root Cause**: Release process assumed version.json was the only version source. In reality, 17+ files per template contain version strings.

### Version Inventory (Template Repos)

**ALL of these files contain version strings and MUST be updated atomically**:

#### Primary (User-Facing)
| File | Field/Pattern |
|------|---------------|
| `README.md` | `**Current Version**: vX.Y.Z` |
| `CHANGELOG.md` | `## [X.Y.Z] - YYYY-MM-DD` (new entry) |
| `AGENTS.md` | `@aget-version: X.Y.Z` |
| `manifest.yaml` | `version: X.Y.Z` |

#### Identity & Config
| File | Field/Pattern |
|------|---------------|
| `.aget/version.json` | `"aget_version": "X.Y.Z"` (PRIMARY) |
| `.aget/identity.json` | `"version": "X.Y.Z"` |

#### Governance
| File | Field/Pattern |
|------|---------------|
| `governance/CHARTER.md` | `**Version**: X.Y.Z` |
| `governance/MISSION.md` | `**Version**: X.Y.Z` |
| `governance/SCOPE_BOUNDARIES.md` | `**Version**: X.Y.Z` |

#### 5D Composition (YAML Comments)
| File | Field/Pattern |
|------|---------------|
| `.aget/context/*.yaml` | `# Version: X.Y.Z` |
| `.aget/reasoning/*.yaml` | `# Version: X.Y.Z` |
| `.aget/skills/*.yaml` | `# Version: X.Y.Z` |
| `.aget/persona/*.yaml` | `# Version: X.Y.Z` |

#### Documentation
| File | Field/Pattern |
|------|---------------|
| `knowledge/README.md` | `*part of AGET vX.Y.Z*` |

### Pre-Release Validation (BLOCKING)

**BEFORE committing**, verify no old version remains:

```bash
OLD_VERSION="3.0.0"  # Version being replaced
NEW_VERSION="3.1.0"  # New version

# Find all files still containing old version
grep -rn "v${OLD_VERSION}\|${OLD_VERSION}" \
  --include="*.md" --include="*.yaml" --include="*.json" \
  /Users/gabormelli/github/aget-framework/template-*-aget/ \
  | grep -v CHANGELOG  # CHANGELOG legitimately contains history
```

**Expected Output**: No results (or only CHANGELOG history entries)

**If files found**: Update them BEFORE committing.

### Post-Release Validation

```bash
# Verify new version appears in all expected places
grep -rn "${NEW_VERSION}" \
  --include="*.md" --include="*.yaml" --include="*.json" \
  /Users/gabormelli/github/aget-framework/template-*-aget/
```

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "I'll just update version.json" | 15+ stale files | Use version inventory |
| "README is just docs" | Users see wrong version | README is user-facing |
| "YAML comments don't matter" | Internal inconsistency | All artifacts must align |

---

## Critical: Version Inventory Coherence Testing (L444)

**⚠️ WARNING: Existence testing is insufficient. Coherence testing is required.**

### Lesson Learned (L444)

v3.2.0 was released with AGENTS.md and manifest.yaml still showing v3.1.0. Gate 7 only verified version.json files, missing other version-bearing files. This created user-visible inconsistency discovered during post-release retrospective.

**Root Cause (5-Why)**:
1. Gate 7 checklist only verified version.json, CHANGELOG, and tags
2. L429 (Version Inventory) focused on version.json as PRIMARY
3. No systematic version inventory requirement for ALL version-bearing files
4. Validation philosophy prioritized existence ("does file exist?") over coherence ("are references consistent?")
5. **Root Cause**: L421 created implicit culture of existence testing without coherence verification

### Requirement: R-REL-VER-001 (Version Inventory Coherence)

**WHEN** releasing a version
**THE** release manager SHALL verify version consistency across:

| File | Field/Pattern | Source of Truth |
|------|---------------|-----------------|
| `.aget/version.json` | `"aget_version"` | **PRIMARY** |
| `AGENTS.md` | Header line (e.g., `- vX.Y.Z`) | Derived |
| `manifest.yaml` | `version:` field | Derived |
| `CHANGELOG.md` | `## [X.Y.Z]` entry | Derived |
| `README.md` | Version badges/references | Derived |
| `.github/profile/README.md` | Version badge + text | Derived |

### Coherence Testing vs Existence Testing

| Test Type | Question | Example |
|-----------|----------|---------|
| Existence (L421) | "Does the file exist?" | `[ -f version.json ]` |
| Coherence (L444) | "Are all references consistent?" | `grep "3.2.0" manifest.yaml` |

**Both are required for release quality.**

### V-Tests for Gate 7 (Version Coherence)

```bash
VERSION="3.2.0"  # Target version

# V7.1.1: version.json contains correct version
grep -q "\"aget_version\": \"$VERSION\"" .aget/version.json && echo "✅ V7.1.1" || echo "❌ V7.1.1"

# V7.1.2: CHANGELOG has entry
grep -q "\\[$VERSION\\]" CHANGELOG.md && echo "✅ V7.1.2" || echo "❌ V7.1.2"

# V7.1.3: Git tag exists
git tag -l "v$VERSION" | grep -q "v$VERSION" && echo "✅ V7.1.3" || echo "❌ V7.1.3"

# V7.1.4: AGENTS.md header contains version (NEW - L444)
grep -q "v$VERSION" AGENTS.md && echo "✅ V7.1.4" || echo "❌ V7.1.4"

# V7.1.5: manifest.yaml version field (NEW - L444)
grep -q "version: $VERSION" manifest.yaml && echo "✅ V7.1.5" || echo "❌ V7.1.5"

# V7.1.6: No stale version references (NEW - L444)
OLD_VERSION="3.1.0"  # Previous version
STALE=$(grep -rn "v$OLD_VERSION\|version: $OLD_VERSION" --include="*.md" --include="*.yaml" . | grep -v CHANGELOG | wc -l)
[ "$STALE" -eq 0 ] && echo "✅ V7.1.6" || echo "❌ V7.1.6 ($STALE stale references)"
```

### Coherence Validation Script

```bash
# Run before committing release
VERSION="X.Y.Z"
OLD_VERSION="X.Y.Z-1"  # Previous version

echo "=== VERSION COHERENCE CHECK (L444) ==="

for repo in aget template-*-aget; do
  echo "--- $repo ---"
  cd /Users/gabormelli/github/aget-framework/$repo

  # Check version.json (PRIMARY)
  grep "\"aget_version\": \"$VERSION\"" .aget/version.json > /dev/null && echo "✅ version.json" || echo "❌ version.json"

  # Check AGENTS.md header
  grep "v$VERSION" AGENTS.md > /dev/null && echo "✅ AGENTS.md" || echo "❌ AGENTS.md"

  # Check manifest.yaml
  grep "version: $VERSION" manifest.yaml > /dev/null && echo "✅ manifest.yaml" || echo "❌ manifest.yaml"

  # Check for stale references
  STALE=$(grep -rn "v$OLD_VERSION" --include="*.md" --include="*.yaml" . | grep -v CHANGELOG | wc -l)
  [ "$STALE" -eq 0 ] && echo "✅ No stale refs" || echo "❌ $STALE stale refs"

  cd ..
done
```

### Anti-Pattern: Partial Version Update

**Pattern**: Updating only version.json without updating derived files.

**Detection**: `grep -r "vOLD_VERSION" . | grep -v CHANGELOG`

**Consequence**: User-visible version inconsistency, credibility damage.

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "version.json updated, done" | AGENTS.md, manifest.yaml stale | Run coherence check |
| "Gate 7 checklist passed" | Checklist incomplete | Add V7.1.4-V7.1.6 |
| "Only version.json matters" | User confusion | All version-bearing files matter |

---

## Critical: Version-Bearing File Enumeration (L579)

**⚠️ WARNING: Abstract requirements ("ALL files") without concrete enumeration cause version drift.**

### Lesson Learned (L579)

v3.5.0 5-whys analysis revealed L521 remediation was incomplete. Multiple version-bearing file types were not enumerated:
- GitHub Releases: Not created for templates
- Per-template CHANGELOG.md: Not enforced
- codemeta.json: Not updated
- CITATION.cff: Not updated
- migration_history: Not updated

**Root Cause**: R-REL requirements used abstract terms ("ALL version-bearing files") without concrete enumeration of what files those are.

### Canonical Enumeration

See: `docs/VERSION_BEARING_FILES.md` for the complete enumeration.

| File | Location | Pattern | Check Command |
|------|----------|---------|---------------|
| version.json | `.aget/version.json` | `"aget_version": "X.Y.Z"` | `jq .aget_version` |
| AGENTS.md | Root | `@aget-version: X.Y.Z` | `grep @aget-version` |
| manifest.yaml | Root | `version: X.Y.Z` | `yq .version` |
| README.md | Root | `**Version**: vX.Y.Z` | `grep Version` |
| CHANGELOG.md | Root | `## [X.Y.Z]` | `grep "## \[X.Y.Z\]"` |
| GitHub Release | GitHub | vX.Y.Z tag + release | `gh release view vX.Y.Z` |
| codemeta.json | Root (core) | `"version": "X.Y.Z"` | `jq .version` |
| CITATION.cff | Root (core) | `version: "X.Y.Z"` | `yq .version` |
| migration_history | `.aget/version.json` | Array entry | `jq .migration_history` |

### Requirement: R-REL-035 (GitHub Release Required)

**WHEN** tagging a release
**THE** release manager SHALL create GitHub Releases for ALL tagged repos:

```bash
# Create releases for all repos (not just push tags)
for repo in aget template-*-aget; do
  cd /Users/gabormelli/github/aget-framework/$repo
  gh release create vX.Y.Z --title "vX.Y.Z: Release Title" --notes "Release notes"
done
```

**Verification**:
```bash
for repo in aget template-*-aget; do
  gh release view vX.Y.Z --repo aget-framework/$(basename $repo) --json tagName -q .tagName 2>/dev/null && echo "✅ $repo" || echo "❌ $repo"
done
```

### Requirement: R-REL-036 (Per-Template CHANGELOG)

**WHEN** releasing a version
**THE** release manager SHALL ensure EACH template CHANGELOG.md has a version entry:

```bash
# Verify all templates have CHANGELOG entry
for repo in template-*-aget; do
  grep -q "## \[X.Y.Z\]" /Users/gabormelli/github/aget-framework/$repo/CHANGELOG.md && \
    echo "✅ $repo" || echo "❌ $repo MISSING CHANGELOG entry"
done
```

**Note**: Core aget/CHANGELOG.md tracks framework changes. Template CHANGELOGs track template-specific changes for that release.

### Requirement: R-REL-037 (Metadata Files)

**WHEN** releasing a version
**THE** release manager SHALL update metadata files in core aget/:

| File | Field | Update |
|------|-------|--------|
| `codemeta.json` | `"version"` | X.Y.Z |
| `codemeta.json` | `"dateModified"` | YYYY-MM-DD |
| `CITATION.cff` | `version` | X.Y.Z |
| `CITATION.cff` | `date-released` | YYYY-MM-DD |

**Verification**:
```bash
cd /Users/gabormelli/github/aget-framework/aget
jq '.version' codemeta.json  # Should show "X.Y.Z"
grep "^version:" CITATION.cff  # Should show version: "X.Y.Z"
```

### Pre-Release Version Inventory Check

**BEFORE committing**, run complete version inventory check:

```bash
VERSION="X.Y.Z"

echo "=== VERSION-BEARING FILE CHECK (L579) ==="

# 1. Core aget/
echo "--- aget/ ---"
grep "\"aget_version\": \"$VERSION\"" aget/.aget/version.json && echo "✅ version.json" || echo "❌ version.json"
grep "## \[$VERSION\]" aget/CHANGELOG.md && echo "✅ CHANGELOG" || echo "❌ CHANGELOG"
jq -r '.version' aget/codemeta.json | grep -q "$VERSION" && echo "✅ codemeta.json" || echo "❌ codemeta.json"
grep "version: \"$VERSION\"" aget/CITATION.cff && echo "✅ CITATION.cff" || echo "❌ CITATION.cff"

# 2. All templates
for repo in template-*-aget; do
  echo "--- $repo ---"
  grep "\"aget_version\": \"$VERSION\"" $repo/.aget/version.json && echo "✅ version.json" || echo "❌ version.json"
  grep "## \[$VERSION\]" $repo/CHANGELOG.md && echo "✅ CHANGELOG" || echo "❌ CHANGELOG"
  grep "v$VERSION" $repo/migration_history 2>/dev/null || grep "$VERSION" $repo/.aget/version.json | grep migration && echo "✅ migration_history" || echo "⚠️ check migration_history"
done

# 3. GitHub Releases (post-push only)
echo "--- GitHub Releases ---"
for repo in aget template-*-aget; do
  gh release view v$VERSION --repo aget-framework/$repo --json tagName -q .tagName 2>/dev/null && echo "✅ $repo" || echo "❌ $repo"
done
```

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "Tags pushed, releases exist" | Tags ≠ Releases | Run `gh release create` |
| "Core CHANGELOG updated" | Template CHANGELOGs stale | Update each template |
| "version.json is enough" | codemeta/CITATION outdated | Update all metadata |
| "migration_history is internal" | Version history incomplete | Add entry |

---

## Version-Bearing Spec Inventory (L584)

**Purpose**: Specs with embedded version numbers that MUST be updated each release.

### Inventory (R-REL-039)

| Spec | Field | Location |
|------|-------|----------|
| `AGET_IDENTITY_SPEC.yaml` | `versioning.current_version` | `aget/specs/` |
| `SESSION_SKILLS_INDEX.yaml` | `meta.framework_version` | `aget/specs/` |
| `README.md` | Generation date footer | `aget/` |

**Canonical Source**: `.aget/version.json` → `aget_version`

### Pre-Release Validation (R-REL-040)

```bash
VERSION="X.Y.Z"

echo "=== VERSION-BEARING SPEC CHECK (L584) ==="

# Canonical source
CANONICAL=$(jq -r '.aget_version' aget/.aget/version.json)
echo "Canonical: $CANONICAL"

# AGET_IDENTITY_SPEC
IDENTITY_VER=$(grep "current_version:" aget/specs/AGET_IDENTITY_SPEC.yaml | head -1 | awk '{print $2}' | tr -d '"')
[ "$IDENTITY_VER" = "$VERSION" ] && echo "✅ AGET_IDENTITY_SPEC: $IDENTITY_VER" || echo "❌ AGET_IDENTITY_SPEC: $IDENTITY_VER (expected $VERSION)"

# SESSION_SKILLS_INDEX
SKILLS_VER=$(grep "framework_version:" aget/specs/SESSION_SKILLS_INDEX.yaml | head -1 | awk '{print $2}' | tr -d '"')
[ "$SKILLS_VER" = "$VERSION" ] && echo "✅ SESSION_SKILLS_INDEX: $SKILLS_VER" || echo "❌ SESSION_SKILLS_INDEX: $SKILLS_VER (expected $VERSION)"

# README generation date (manual check - should match release date)
README_DATE=$(grep "Generated from specifications" aget/README.md | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}")
echo "ℹ️  README.md generated: $README_DATE (verify matches release date)"
```

### Adding New Specs to Inventory (R-REL-041)

When creating a new spec with a version field:
1. Add to inventory table above
2. Add to validation script
3. Document in spec's changelog: "Note: Requires release-time version update"

---

## Critical: Post-Release Validation is MANDATORY (L406)

**⚠️ WARNING: A release is NOT complete until Phase 4 validation passes.**

### Lesson Learned (L406)

v3.0.0 was released but declared complete without running Phase 4 validation. This resulted in:
- Organization homepage showing wrong version (2.12.0 instead of 3.0.0)
- Release date badge incorrect
- Example version.json snippets outdated
- Roadmap section stale

**Root Cause**: PROJECT_PLAN Gate 6 performed spot checks instead of running the full RELEASE_VERIFICATION_CHECKLIST.md.

### Requirement

Any PROJECT_PLAN that includes a release MUST:

1. **Explicitly require**: "Run Phase 4 validation from SOP_release_process.md"
2. **Include gate deliverable**: "RELEASE_VERIFICATION_CHECKLIST.md completed (all items ✅)"
3. **Block announcement**: Until validation script returns exit code 0

**Checklist Location**: `sops/RELEASE_VERIFICATION_CHECKLIST.md`

**Validation Script**: `python3 .aget/patterns/release/post_release_validation.py --version X.Y.Z`

---

## Critical: PROJECT_PLAN Gates Must Derive from Checklist (L376)

**⚠️ WARNING: Creating PROJECT_PLAN without reading RELEASE_VERIFICATION_CHECKLIST.md guarantees missed items.**

### Lesson Learned (L376)

v2.12.0 release missed org homepage badge update. User had to spot-check (L362 anti-pattern).

**Root Cause**: PROJECT_PLAN gates created ad-hoc, not derived from RELEASE_VERIFICATION_CHECKLIST.md.

**Key Insight**: The checklist should INFORM the PROJECT_PLAN, not just VERIFY after.

### Pattern: Checklist-Driven Gate Design

When creating a release PROJECT_PLAN:

1. **READ**: `sops/RELEASE_VERIFICATION_CHECKLIST.md` FIRST
2. **MAP**: Each R-PUB-001-XX to a gate deliverable
3. **ENSURE**: Every verification item has a creation step
4. **VERIFY**: Cross-reference checklist sections to plan gates

**Checklist Section → Gate Mapping**:

| Checklist Section | Maps To |
|-------------------|---------|
| Section 1: Release Infrastructure | G-Tags, G-Releases, G-Homepage |
| Section 2: Content Quality | G-Release-Notes (if major/minor) |
| Section 3: Historical Consistency | G-Pre-Flight |
| Section 4: Framework Compliance | G-Pre-Gate or G-0 |
| Section 5: Process Compliance | All gates (cross-cutting) |

### Pre-Planning Checklist (R-REL-007)

Before creating any release PROJECT_PLAN:

- [ ] Read `sops/RELEASE_VERIFICATION_CHECKLIST.md` (14 R-PUB-001 requirements)
- [ ] Map each R-PUB-001-XX to a gate deliverable
- [ ] Verify: Every verification item has a creation step
- [ ] Add explicit gate: "Phase 4 Validation (BLOCKING)"

### Red Flags During Planning

If you see these patterns, STOP and read the checklist:

- Creating gates without opening RELEASE_VERIFICATION_CHECKLIST.md
- "Simplified plan" that skips infrastructure steps
- No explicit "org homepage" deliverable
- No Phase 4 blocking validation gate

---

### Red Flags During Release

If you see these patterns, STOP and run full validation:

- "I checked and releases exist" → Did you run the full checklist?
- "CI is passing" → Did you check org homepage?
- "Gate 6 complete" → Did you run the validation script?

---

## Critical: Pre-Publication Content Security (L430)

**⚠️ WARNING: Templates extracted from private agents may contain proprietary information.**

### Lesson Learned (L430)

v3.1.0 template-spec-engineer-aget contained proprietary client name "Law Insider" in:
- README.md (user-facing!)
- Session history files
- Git commit history

Required emergency remediation: git filter-repo + force push + tag rewrite.

### Requirement: R-REL-009

**BEFORE pushing ANY template to public repository**:

1. [ ] Run content security scan (see patterns below)
2. [ ] Check git history: `git log -S "PATTERN" --all`
3. [ ] If template originated from private agent: FULL AUDIT required

### Content Security Scan

```bash
# Scan for proprietary patterns
grep -ri "PATTERNS_TO_CHECK" repo/ \
  --include="*.md" --include="*.py" --include="*.yaml" --include="*.json"
```

**Patterns to scan**:

| Category | Examples | Action |
|----------|----------|--------|
| Client names | Company names, project codenames | BLOCK |
| Internal URLs | Internal domains, staging URLs | BLOCK |
| Portfolio names | legalon, workco, predictionworks | REVIEW |
| Private repos | private-*, gmelli/* (except LICENSE) | REVIEW |
| Credentials | API keys, tokens, passwords | BLOCK |
| Personal info | Email addresses (except LICENSE) | REVIEW |

### Template Origin Classification

| Origin | Risk | Required Review |
|--------|------|-----------------|
| New (greenfield) | Low | Standard scan |
| Extracted from private agent | **HIGH** | Full content + history audit |
| Forked from public repo | Medium | Scan for additions |

### If Proprietary Content Found in Git History

File edits alone are insufficient. Must rewrite git history with **TWO PASSES**:

```bash
# Pass 1: Replace in FILE CONTENT
echo 'PROPRIETARY_NAME==>GENERIC_NAME' > /tmp/replace.txt
python3 -m git_filter_repo --replace-text /tmp/replace.txt --force

# Pass 2: Replace in COMMIT MESSAGES (CRITICAL - often missed!)
git remote add origin git@github.com:aget-framework/REPO.git
python3 -m git_filter_repo --message-callback \
  'return message.replace(b"PROPRIETARY_NAME", b"GENERIC_NAME")' --force

# Re-add remote and force push
git remote add origin git@github.com:aget-framework/REPO.git
git push origin main --force
git push origin --tags --force

# VERIFY BOTH are clean
git log -S "PROPRIETARY_NAME" --all --oneline      # Files: 0
git log --all --oneline --grep="PROPRIETARY_NAME"  # Messages: 0
```

**CRITICAL**: `--replace-text` only replaces FILE CONTENT. Commit messages visible on GitHub require separate `--message-callback` pass.

**Consequences of history rewrite**:
- All existing clones become incompatible
- All forks become incompatible
- Requires re-cloning by anyone who has repo

---

## Critical: Organization-Level Artifacts (L431)

**⚠️ WARNING: Repository releases do not update organization homepage automatically.**

### Lesson Learned (L431)

v3.1.0 was released but organization homepage still showed v3.0.0 as current. The roadmap, version badge, and release date badge were all outdated.

**Root Cause**: R-PUB-001 covers repository-level artifacts only. Organization homepage is a separate artifact category not previously specified.

### Requirement: R-REL-010 (Organization Homepage Update)

**WHEN** a new version is released
**THEN** the organization homepage SHALL be updated within the same release session:

| Element | Location | Update |
|---------|----------|--------|
| Version badge | Line 9 | `version-X.Y.Z-blue` |
| Release date badge | Line 11 | `released-YYYY--MM--DD-lightgrey` |
| Badge link | Line 9 | `/releases/tag/vX.Y.Z` |
| Roadmap section | ~Line 386 | New version as "Current" |

**File**: `.github/profile/README.md`

### Requirement: R-REL-011 (CHANGELOG Discipline)

**BEFORE** tagging any release:

1. [ ] CHANGELOG.md contains entry for new version
2. [ ] Entry has proper date: `## [X.Y.Z] - YYYY-MM-DD`
3. [ ] Content matches release notes

**Consequence of violation**: Users see release but no changelog entry, creating confusion.

### Organization Artifact Checklist

Before Phase 5 (announcement), verify:

- [ ] `.github/profile/README.md` version badge updated
- [ ] `.github/profile/README.md` release date badge updated
- [ ] `.github/profile/README.md` roadmap section updated
- [ ] `aget/CHANGELOG.md` has entry for new version
- [ ] `.github` repo committed and pushed

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "Repos are pushed, we're done" | Org homepage stale | Check R-REL-010 |
| "CHANGELOG is just docs" | User confusion | R-REL-011 is blocking |
| "I'll update homepage later" | Forgotten, user sees old | Same session requirement |

---

## Critical: License Compliance (L432)

### Lesson Learned (L432)

v3.1.0 post-release audit revealed:
- Homepage badge showed MIT (should be Apache 2.0)
- aget/ core had no LICENSE file
- template-consultant-aget had MIT license (inconsistent)

**Root Cause**: LICENSE file creation and verification not in release checklist.

### Requirement: R-LIC-001 (License Verification)

**BEFORE** tagging any release
**THE** release manager SHALL verify license compliance:

| Check | Command | Expected |
|-------|---------|----------|
| aget/ LICENSE exists | `ls aget/LICENSE` | File exists |
| Templates have LICENSE | `ls template-*/LICENSE` | All exist |
| All are Apache 2.0 | `head -1 */LICENSE` | "Apache License" |
| Homepage badge correct | Visual check | Apache 2.0 badge |

### License Verification Script

```bash
echo "=== LICENSE VERIFICATION ==="
for repo in aget .github template-*-aget; do
  if [ -f "$repo/LICENSE" ]; then
    license_type=$(head -1 "$repo/LICENSE")
    if echo "$license_type" | grep -q "Apache"; then
      echo "✅ $repo: Apache 2.0"
    else
      echo "❌ $repo: Non-Apache ($license_type)"
    fi
  else
    echo "❌ $repo: LICENSE MISSING"
  fi
done
```

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "LICENSE is just formality" | Legal exposure | CAP-LIC-001 is mandatory |
| Missing LICENSE in repo | Ambiguous licensing | Create from template |
| MIT badge with Apache file | User confusion | Update badge |

---

## Critical: Validator Enforcement Integrity (L433)

### Lesson Learned (L433)

v3.1.0 audit found 14 validators referenced in specs that don't exist:
- validate_license_compliance.py (referenced in AGET_LICENSE_SPEC)
- validate_homepage_messaging.py (referenced in R-HOM-001)
- 12 others (see L433 for full list)

**Root Cause**: Specs written aspirationally with "Enforcement:" sections referencing non-existent validators. This violates ADR-007 (No Test Theater).

### Requirement: R-SPEC-010 (Validator Existence Gate)

**BEFORE** releasing a spec version
**THE** release manager SHALL verify all "Enforcement:" references:

| Validator Status | Spec Text Required |
|------------------|-------------------|
| Exists and works | `Enforcement: validator.py` |
| Planned with issue | `Enforcement: validator.py (planned, #issue)` |
| Deferred with reason | `Enforcement: validator.py (deferred)` |
| No automation | `Enforcement: Manual review per SOP_X` |

### Validator Existence Check

```bash
# Extract all validator references from specs
grep -rh "validate_.*\.py" aget/specs/ | \
  grep -oE "validate_[a-z_]+\.py" | \
  sort -u | while read v; do
    if [ -f "aget/validation/$v" ]; then
      echo "✅ $v"
    else
      echo "❌ $v MISSING"
    fi
  done
```

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "We'll create validators later" | Governance theater | Mark "(planned)" |
| Spec approved with missing validators | False confidence | Block approval |
| 30%+ missing validators | Systematic theater | Audit and remediate |

---

## Critical: Template Ontology Conformance (R-REL-015)

**⚠️ WARNING: We do not leave published templates behind.**

### Lesson Learned (v3.3.0 Assessment)

During v3.3.0 planning, assessment revealed:
- 12 published templates exist
- 0 templates had specs/ directories or SKOS vocabularies
- Original plan only covered 6 templates
- Gap: User expectation was ALL templates would exemplify v3.3.0 approach

**Root Cause**: No requirement that published templates must conform to current version's approach.

### Requirement: R-REL-015 (Template Ontology Conformance)

**WHEN** releasing a version that introduces ontology-driven patterns (L481, L482)
**THE** release manager SHALL ensure ALL published templates conform:

> **"We do not leave published templates behind."**

| Check | Requirement |
|-------|-------------|
| Template count | ALL published templates accounted for |
| specs/ directory | ALL templates have specs/ directory |
| Vocabulary spec | ALL templates have *_VOCABULARY.md |
| SKOS compliance | ALL vocabularies have skos:definition |
| Deprecation | Non-conforming templates MUST be deprecated |

### Template Inventory Check

```bash
# List all published templates
ls -d /Users/gabormelli/github/aget-framework/template-*-aget/ | wc -l
# Expected: Count matches plan coverage

# Verify all have specs/
for t in /Users/gabormelli/github/aget-framework/template-*-aget; do
  [ -d "$t/specs" ] && echo "✅ $(basename $t)" || echo "❌ $(basename $t) MISSING specs/"
done

# Verify all have vocabularies
for t in /Users/gabormelli/github/aget-framework/template-*-aget; do
  ls "$t/specs/"*_VOCABULARY.md >/dev/null 2>&1 && \
    echo "✅ $(basename $t)" || echo "❌ $(basename $t) MISSING vocabulary"
done
```

### Template Tier Classification

| Tier | Definition | Action |
|------|------------|--------|
| **Established** | >30 files, full structure | MUST have ontology |
| **Skeleton** | <20 files, minimal | Migrate OR deprecate |
| **Deprecated** | Not maintained | Mark deprecated, archive |

### Deprecated Template Process

If a template cannot conform to current version approach:

1. **Create deprecation notice**: Add `DEPRECATED.md` to template root
2. **Update README**: Add deprecation warning at top
3. **Archive (optional)**: Move to `archive/` directory or separate org
4. **Remove from template count**: Deprecated templates don't count toward conformance

**DEPRECATED.md Template**:
```markdown
# DEPRECATED: template-{name}-aget

**Deprecated**: vX.Y.Z
**Reason**: [Cannot conform to ontology-driven approach / Superseded by template-X]
**Alternative**: [Use template-Y-aget instead]
**Archive Date**: YYYY-MM-DD

This template is no longer maintained and does not conform to AGET vX.Y.Z requirements.
```

### Pre-Release Template Verification

Before ANY release, verify template conformance:

```bash
VERSION="X.Y.Z"
TEMPLATES=$(ls -d /Users/gabormelli/github/aget-framework/template-*-aget/ 2>/dev/null | wc -l)
DEPRECATED=$(find /Users/gabormelli/github/aget-framework/template-*-aget -name "DEPRECATED.md" 2>/dev/null | wc -l)
ACTIVE=$((TEMPLATES - DEPRECATED))

echo "=== TEMPLATE CONFORMANCE CHECK (R-REL-015) ==="
echo "Total templates: $TEMPLATES"
echo "Deprecated: $DEPRECATED"
echo "Active (must conform): $ACTIVE"

# Verify all active have ontologies
PASS=0; FAIL=0
for t in /Users/gabormelli/github/aget-framework/template-*-aget; do
  if [ -f "$t/DEPRECATED.md" ]; then
    echo "⏭️ $(basename $t) (deprecated)"
    continue
  fi
  if ls "$t/specs/"*_VOCABULARY.md >/dev/null 2>&1; then
    echo "✅ $(basename $t)"
    ((PASS++))
  else
    echo "❌ $(basename $t) MISSING vocabulary"
    ((FAIL++))
  fi
done

echo "---"
echo "Conforming: $PASS/$ACTIVE"
[ $FAIL -eq 0 ] && echo "✅ R-REL-015 PASS" || echo "❌ R-REL-015 FAIL"
```

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "Only core templates matter" | User confusion, inconsistent fleet | ALL or deprecate |
| "We'll migrate them later" | Templates never updated | Block release |
| "Skeleton templates are fine" | Incomplete user experience | Migrate or deprecate |
| Template count mismatch | Missing templates | Audit and update |

---

## Critical: Repository Governance (L505, L508, L509)

**⚠️ WARNING: Repository settings are governance scope, not just content.**

### Lesson Learned (L508)

During v3.3.0 post-release review, discovered:
- 13/13 public repos had NO branch protection enabled
- All repos vulnerable to force push and branch deletion
- GitHub UI warning "Your main branch isn't protected" went unnoticed

**Root Cause**: Repository settings (branch protection, visibility) not included in release validation scope.

### Lesson Learned (L509)

While enabling branch protection, discovered template-supervisor-aget was PRIVATE while 11 other templates were PUBLIC.

**Resolution**: Documented as intentional ("Private until supervisor patterns stabilize" in README). Created visibility exception mechanism.

### Requirement: R-REL-016 (Branch Verification)

**BEFORE** pushing to public repositories
**THE** release manager SHALL verify all repos are on main branch:

```bash
# Verify all repos on main branch
for dir in /Users/gabormelli/github/aget-framework/*/; do
  branch=$(git -C "$dir" branch --show-current 2>/dev/null)
  [ "$branch" = "main" ] && echo "✅ $(basename $dir)" || echo "❌ $(basename $dir): $branch"
done
```

### Requirement: R-REL-017 (Branch Protection Verification)

**WHEN** releasing to public repositories
**THE** release manager SHALL verify branch protection is enabled:

```bash
# Verify all repos have branch protection
python3 .aget/patterns/validation/repo_settings_validator.py
# Expected: All checks pass
```

### Requirement: R-REL-018 (Template Visibility Verification)

**BEFORE** releasing templates
**THE** release manager SHALL verify template visibility is consistent
**UNLESS** intentionally different (documented in repo README):

```bash
# Check visibility consistency
python3 .aget/patterns/validation/repo_settings_validator.py --json | jq '.summary'
# Expected: visibility_violation = 0
```

### Repository Settings Validation

Run the repository settings validator before each release:

```bash
python3 .aget/patterns/validation/repo_settings_validator.py
```

**Expected Output**:
- 15/15 repos protected
- 0 visibility violations (exceptions documented)
- 15/15 repos on main branch

### Documented Visibility Exceptions

| Repo | Visibility | Rationale |
|------|------------|-----------|
| template-supervisor-aget | PRIVATE | "Private until supervisor patterns stabilize" (README) |

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "It's fine, protection was set up months ago" | Drift undetected | Run validator every release |
| Skipping visibility check | Inconsistent user experience | Run validator |
| "Just push, we'll fix settings later" | Vulnerable window | Validate before push |
| New repo without protection | Governance gap | Add to validator expected list |

---

## Critical: Issue Settings Governance (L520, L638)

**⚠️ WARNING: Template repos with issues enabled create Issue_Fragmentation and information leakage risk.**

### Lesson Learned (L520)

During issue filing, private agent filed internal issue to `aget-framework/template-supervisor-aget`, exposing:
- Private agent names (`vp_of_ai-aget`, `private-work-supervisor-AGET`)
- Fleet size and internal incident details

**Root Cause**: Template repos had GitHub issues enabled by default. No governance requiring issues be disabled on template repos.

### Requirement: R-ISSUE-007, R-ISSUE-008 (Issue Settings)

**BEFORE** releasing templates
**THE** release manager SHALL verify issue settings:

| Check | Expected | Command |
|-------|----------|---------|
| Template repos issues | DISABLED | `gh repo view aget-framework/template-* --json hasIssuesEnabled` |
| .github repo issues | DISABLED | `gh repo view aget-framework/.github --json hasIssuesEnabled` |
| Core aget/ issues | ENABLED | `gh repo view aget-framework/aget --json hasIssuesEnabled` |

### Issue Settings Validation

```bash
# Verify issue settings across org
echo "=== ISSUE SETTINGS VERIFICATION (L520) ==="

# Template repos should have issues DISABLED
for repo in $(gh repo list aget-framework --json name --jq '.[].name' | grep "template-"); do
  issues=$(gh repo view "aget-framework/$repo" --json hasIssuesEnabled --jq '.hasIssuesEnabled')
  [ "$issues" = "false" ] && echo "✅ $repo: issues disabled" || echo "❌ $repo: issues ENABLED (violation)"
done

# .github should have issues DISABLED
issues=$(gh repo view "aget-framework/.github" --json hasIssuesEnabled --jq '.hasIssuesEnabled')
[ "$issues" = "false" ] && echo "✅ .github: issues disabled" || echo "❌ .github: issues ENABLED"

# Core aget/ should have issues ENABLED
issues=$(gh repo view "aget-framework/aget" --json hasIssuesEnabled --jq '.hasIssuesEnabled')
[ "$issues" = "true" ] && echo "✅ aget: issues enabled (central tracker)" || echo "⚠️ aget: issues disabled"
```

### Issue Destination Matrix

| Repository | Issues Setting | Rationale |
|------------|---------------|-----------|
| `aget-framework/aget` | **ENABLED** | Central public issue tracker |
| `aget-framework/.github` | DISABLED | Org config only |
| `aget-framework/template-*` | DISABLED | Code templates, not issue targets |
| `gmelli/aget-aget` | ENABLED | Private fleet issue tracker |

### Private-First Issue Routing (L638)

**All agents file to `gmelli/aget-aget`.** Public issues on `aget-framework/aget` require explicit promotion with principal approval.

| Stage | Destination | Content Rules |
|-------|-------------|---------------|
| Filing (all agents) | `gmelli/aget-aget` | No sanitization needed — private repo |
| Promotion (optional) | `aget-framework/aget` | Principal-approved, sanitized content only |

### Red Flags

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| Template repo with issues enabled | Issue_Fragmentation | `gh repo edit --enable-issues=false` |
| Any agent filing directly to `aget-framework/aget` | Bypasses private-first routing | File to `gmelli/aget-aget` instead |
| Promoted issue contains private agent names | Exposure risk | Sanitize before promotion |

### References

- AGET_ISSUE_GOVERNANCE_SPEC v2.0.0 (R-ISSUE-001 through R-ISSUE-014)
- AGET_TEMPLATE_SPEC (CAP-TPL-015)
- L638: Private-First Issue Routing

---

## Release Steps

### 1. Verify Clean State

```bash
cd /Users/gabormelli/github/aget-framework/[template-name]
git status  # Should be clean or only release changes
```

### 2. Update Version

Edit `.aget/version.json`:
```json
{
  "aget_version": "X.Y.Z",  // Bump appropriately
  "updated": "YYYY-MM-DD"
}
```

### 3. Update Changelog

Edit `CHANGELOG.md`:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

### 4. Commit Release

```bash
git add .aget/version.json CHANGELOG.md
git commit -m "Release vX.Y.Z: Brief description"
```

### 5. Tag Release

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 6. Push

```bash
git push origin main --tags
```

### 7. Verify

#### Core Checks
- [ ] Tag visible on GitHub
- [ ] CHANGELOG reflects release
- [ ] No CI failures (if applicable)

#### Version-Bearing File V-Tests (L579, R-REL-035/036/037)

**BLOCKING**: All must pass before release is considered complete.

| ID | Test | Command | Pass Criteria |
|----|------|---------|---------------|
| V-G7.1 | GitHub releases exist | `gh release view vX.Y.Z` (all 13 repos) | Release exists for each repo |
| V-G7.2 | Template CHANGELOGs updated | `grep "## \[X.Y.Z\]" CHANGELOG.md` (12 templates) | Entry exists in each |
| V-G7.3 | Metadata files updated | `jq .version codemeta.json` + `yq .version CITATION.cff` | Both show X.Y.Z |
| V-G7.4 | migration_history updated | `jq '.migration_history | last' .aget/version.json` (12 templates) | Last entry contains X.Y.Z |

**Quick Validation Script**:

```bash
# Run from aget-framework/ directory
VERSION="X.Y.Z"  # Replace with actual version

echo "=== V-G7.1: GitHub Releases ==="
for repo in aget template-{advisor,analyst,architect,consultant,developer,executive,operator,researcher,reviewer,spec-engineer,supervisor,worker}-aget; do
    result=$(cd $repo && gh release view "v$VERSION" --json tagName -q '.tagName' 2>/dev/null)
    if [ "$result" = "v$VERSION" ]; then
        echo "[OK] $repo"
    else
        echo "[FAIL] $repo"
    fi
done

echo ""
echo "=== V-G7.2: Template CHANGELOGs ==="
for repo in template-*-aget; do
    if grep -q "## \[$VERSION\]" "$repo/CHANGELOG.md" 2>/dev/null; then
        echo "[OK] $repo"
    else
        echo "[FAIL] $repo"
    fi
done

echo ""
echo "=== V-G7.3: Metadata Files ==="
CM=$(jq -r .version aget/codemeta.json 2>/dev/null)
CF=$(yq -r .version aget/CITATION.cff 2>/dev/null)
[ "$CM" = "$VERSION" ] && echo "[OK] codemeta.json: $CM" || echo "[FAIL] codemeta.json: $CM"
[ "$CF" = "$VERSION" ] && echo "[OK] CITATION.cff: $CF" || echo "[FAIL] CITATION.cff: $CF"

echo ""
echo "=== V-G7.4: migration_history ==="
for repo in template-*-aget; do
    MH=$(jq -r '.migration_history | last' "$repo/.aget/version.json" 2>/dev/null)
    if echo "$MH" | grep -q "$VERSION"; then
        echo "[OK] $repo"
    else
        echo "[FAIL] $repo (last: $MH)"
    fi
done
```

**See**: `docs/VERSION_BEARING_FILES.md` for complete enumeration and pre-release validation script.

---

## Version Numbering

Follow semantic versioning:
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

---

## Deep Release Notes (Optional)

For significant releases, create narrative documentation:

**Location**: `private-aget-framework-AGET/release-notes/vX.Y.Z.md`

**When to create**:
- Major version bumps
- Breaking changes
- Significant new capabilities

**Template**: See `release-notes/TEMPLATE.md` (Tier 2 deliverable)

---

## Rollback

If release has issues:

```bash
# Delete remote tag
git push origin :refs/tags/vX.Y.Z

# Delete local tag
git tag -d vX.Y.Z

# Revert commit if needed
git revert HEAD
git push origin main
```

---

## Multi-Repo Release Deployment Protocol (L333)

When releasing framework versions that span multiple repositories (aget/ + 6 templates):

### Critical: Gate Enforcement (CAP-REL-022, L605)

**⚠️ WARNING: Every gate checkpoint below MUST produce a machine-verifiable record. Text checkpoints ("Do NOT proceed") are insufficient — every prior release required user remediation despite text-based blocking (L605).**

**Requirement**: Per CAP-REL-022 (Gate Execution Enforcement), each gate completion SHALL produce a Gate_Record in `.aget/logs/gate_log.jsonl`. The next gate SHALL verify the prior gate has a PASS record before proceeding.

**Applies to**: All Phase checkpoints below (Phase 0 through Phase 6).

**Tooling** (v3.6.0):
```bash
# Record gate completion:
python3 .aget/patterns/release/run_gate.py --gate <GATE_ID> --version <VERSION> \
    --status pass --prior-gate <PRIOR_GATE_ID> --summary "<V-TEST RESULTS>"

# Check if gate can proceed (dry run):
python3 .aget/patterns/release/run_gate.py --check <GATE_ID> --version <VERSION> \
    --prior-gate <PRIOR_GATE_ID>

# View gate history:
python3 .aget/patterns/release/run_gate.py --history --version <VERSION>
```

**Design principle** (L605): The user is not the enforcement mechanism. If the principal is the one catching gaps, the process has failed.

---

### Critical: Pre-Release State Snapshot (CAP-REL-023, L605)

**Requirement**: Per CAP-REL-023, BEFORE Phase 0 begins, capture a pre-release Release_Snapshot of all repo states (version files, GitHub Releases, CHANGELOG latest entries, homepage state). This establishes the baseline for diff-based release validation.

**Rationale** (L605): Absolute validation ("does it pass?") misses regressions. Diff-based validation ("what changed?") catches version drift, stale homepages, and missed propagation targets that absolute checks miss.

**Implementation status**: CAP-REL-023 specifies the requirements. Tooling (`release_snapshot.py`) targets v3.6.0. Until tooling is implemented, capture state manually in `findings/` directory.

---

### Phase -1: Release Readiness (Gap B Governance — D63, L663)

**Purpose**: Verify development is complete and release execution is authorized. Governs the transition from development to release execution — previously invisible (0 SOP pages, 12 combined failures across 8 releases).

**When**: AFTER all development gates complete (implementation, conformance audit), BEFORE Phase 0 (Manager Migration)

**Rationale** (L663): Gap B (Development → Release Execution) has the highest failure density in the release lifecycle. B.1/B.2/B.3 phases were ungoverned, causing 100% post-release failure rate across 8 releases with formal plans.

**Implements**: R-GAP-B-001 through R-GAP-B-005

#### B.1: Release Readiness Assessment

Verify all development work is complete and ready for release execution.

- [ ] All in-scope D-items implemented or PRE-RESOLVED (check VERSION_SCOPE)
- [ ] All BLOCKING V-tests from development gates passing
- [ ] VERSION_SCOPE status reflects development completion
- [ ] Cumulative pre-release checklist reviewed (from VERSION_SCOPE)
- [ ] No open blockers or unresolved dependencies

#### B.2: Deliverable Conformance Audit

Verify all new/modified artifacts conform to their governing specifications.

- [ ] Conformance audit run on all new/modified deliverables
- [ ] 0 SHALL-level violations remain
- [ ] New scripts tested (--help, --verify where applicable)
- [ ] New SOP sections conform to SOP header template

#### B.3: Principal Release Approval

Obtain explicit principal authorization to proceed with release execution.

- [ ] Present release summary to principal (scope, risks, timeline)
- [ ] Principal provides explicit GO for release execution
- [ ] GO decision recorded in PROJECT_PLAN or session notes

**Checkpoint**: All B.1/B.2/B.3 items checked. Principal GO received.

**Red Flags**:

| Red Flag | Consequence | Fix |
|----------|-------------|-----|
| "Phases 0-3 are just mechanical" | Skips readiness verification | Complete B.1/B.2 first |
| No explicit principal GO | Assumed approval | Get recorded GO |
| "I'll fix conformance during release" | Conformance debt compounds | Fix before Phase 0 |
| VERSION_SCOPE still shows pending items | Premature release | Resolve or defer items first |

---

### Phase 0: Manager Migration (NEW - R-REL-006)

**Purpose**: Ensure framework manager migrates to version it releases

**Rationale**: Per GAP_ANALYSIS_version_migration_v1.0.md, managing agent must update its own version before releasing public repos. Prevents "documenting future while living in past" gap.

```bash
# 1. Update managing agent version
cd /Users/gabormelli/github/aget-framework/private-aget-framework-AGET

# Edit .aget/version.json:
# - Change "aget_version": "X.Y.Z-old" → "X.Y.Z"
# - Update "updated": "YYYY-MM-DD"
# - Add migration_history entry: "vX.Y.Z-old -> vX.Y.Z: YYYY-MM-DD (Description)"

# 2. Verify wake-up displays new version
python3 .aget/patterns/session/wake_up.py | grep "vX.Y.Z"
# Should show: **Version**: vX.Y.Z (YYYY-MM-DD)

# 3. Commit manager version bump
git add .aget/version.json
git commit -m "chore: Bump version to vX.Y.Z"

# 4. Run contract tests to verify
python3 -m pytest tests/ -v
```

**Checkpoint**: Manager displays new version, tests pass.

**Implements**: R-REL-006 (Managing agent updates version before release)

### Phase 0.5: Protocol Verification (NEW - R-REL-014)

**Purpose**: Verify session protocols work correctly before releasing

**Rationale**: Per L491 (Script-Level Semantic Slippage), agents can execute wrong scripts even with correct intent. Field observation showed "wind down" executing wrong script despite correct phrase. Protocol verification catches such issues before public release.

**When**: After Phase 0 (Manager Migration), before Phase 1 (Commit)

```bash
# 1. Verify all session protocols identify correctly
python3 .aget/patterns/session/verify_session_protocols.py

# Expected output:
# ============================================================
# SESSION PROTOCOL VERIFICATION
# ============================================================
# ## Overall: **PASS**
# [PASS] **wake_up** (CAP-SESSION-001)
# [PASS] **wind_down** (CAP-SESSION-004)
# [PASS] **sanity_check** (CAP-SESSION-008)
# [PASS] **step_back** (CAP-SESSION-002)
# [PASS] **study_up** (CAP-SESSION-007)
# ============================================================

# 2. If any protocol fails, investigate before proceeding
python3 .aget/patterns/session/verify_session_protocols.py --json | python3 -m json.tool

# 3. Verify single protocol (if needed)
python3 .aget/patterns/session/verify_session_protocols.py --protocol wake_up
```

**Checkpoint**: All 5 protocols PASS before proceeding to Phase 1.

**If Failures**:
1. **STOP** - Do NOT proceed to Phase 1
2. **Investigate** - Check script paths, --verify flag implementations
3. **Fix** - Update scripts to support --verify flag per L491
4. **Re-run** - Verify all protocols pass

**Implements**: R-REL-014 (Protocol Verification Before Release)
**Related**: L491 (Script-Level Semantic Slippage), CAP-SESSION-009

### Phase 0.7: Self-Upgrade Validation (R-REL-024)

**Purpose**: Validate that upgrade works operationally before public release

**Rationale**: L560 revealed that v3.4.0 was released to public but managing agent remained at v3.3.1. Historical practice ("migrate you and supervisor and one of its AGETs") was not codified. This phase ensures the managing agent actually uses the new version before releasing it to users.

**When**: AFTER Phase 0.5 (Protocol Verification), BEFORE Phase 1 (Commit)

**Checklist**:

1. [ ] **Upgrade version files**:
   ```bash
   # Update .aget/version.json
   #   - aget_version: "X.Y.Z"
   #   - updated: "YYYY-MM-DD"
   #   - Add migration_history entry

   # Update AGENTS.md @aget-version
   ```

2. [ ] **Verify wake_up**:
   ```bash
   python3 .aget/patterns/session/wake_up.py | grep "vX.Y.Z"
   # Expected: Version displays correctly
   ```

3. [ ] **Verify sanity_check**:
   ```bash
   python3 .aget/patterns/session/aget_housekeeping_protocol.py
   # Expected: ≥8/9 checks pass
   ```

4. [ ] **Trial new SOP/artifact** (if any created in this release):
   - Select one new SOP or governance artifact
   - Execute on a real case
   - Document friction/gaps discovered
   - Fix or file enhancement issue

5. [ ] **Document in PROJECT_PLAN**:
   - Record upgrade results
   - Note any issues discovered
   - Confirm ready for public release

**Checkpoint**: Self-upgrade complete with passing checks before proceeding to Phase 1.

**If Issues**:
1. **STOP** - Do NOT proceed to Phase 1
2. **Document** - Record issues in PROJECT_PLAN
3. **Fix** - Resolve issues before public release
4. **Re-verify** - Run wake_up and sanity_check again

**Implements**: R-REL-024 (Self-Upgrade Validation)
**Related**: L560 (Release Self-Validation Gap), R-REL-006 (Manager Migration)

### Phase 0.8: Template Deep Conformance (R-REL-027)

**Purpose**: Validate ALL templates pass deep conformance check before public release

**Rationale**: Template conformance spotcheck (2026-01-18) revealed template-supervisor-aget had wake_up.py showing wrong version. Deep conformance catches structural issues, naming convention violations, and spec compliance gaps that light/standard checks miss.

**When**: AFTER Phase 0.7 (Self-Upgrade Validation), BEFORE Phase 1 (Commit)

**Checklist**:

1. [ ] **Run deep conformance on ALL templates**:
   ```bash
   # Run from managing agent directory
   cd /Users/gabormelli/github/aget-framework/private-aget-framework-AGET

   for template in /Users/gabormelli/github/aget-framework/template-*-aget; do
     echo "=== $(basename $template) ==="
     python3 .aget/patterns/conformance/aget_conformance_report.py \
       --version X.Y.Z --depth deep --target "$template"
   done
   ```

2. [ ] **Verify ALL templates CONFORMANT**:
   - Expected: 12/12 templates pass (exit code 0)
   - Check: No FAIL status in any template output

3. [ ] **Review warnings** (acceptable for templates):
   - `identity.json` missing name/type (placeholder by design)
   - `README.md` in sops/ (documentation by design)
   - Session scripts skipped (optional for templates)

4. [ ] **Fix any failures before proceeding**:
   - Version mismatches in version.json or AGENTS.md
   - wake_up.py showing wrong version
   - Structural requirements missing (e.g., no .aget/ directory)

5. [ ] **Document in PROJECT_PLAN**:
   - Record: "Template conformance: X/12 passed"
   - Note any warnings worth addressing in future release

**Checkpoint**: All templates pass deep conformance (CONFORMANT status) before Phase 1.

**If Failures**:
1. **STOP** - Do NOT proceed to Phase 1
2. **Fix** - Resolve failures in affected templates
3. **Re-run** - Verify fix with deep conformance
4. **Document** - Record issue and resolution in PROJECT_PLAN

**Script**: `.aget/patterns/conformance/aget_conformance_report.py` v1.2.0+

**Implements**: R-REL-027 (Template Deep Conformance)
**Related**: Fleet Conformance Spotcheck (PROJECT_PLAN_fleet_conformance_spotcheck_v1.0.md)

### Phase 0.85: Deliverable Conformance Check (D40, L652)

**Purpose**: Verify all new/modified deliverables conform to their governing specifications before release

**Rationale** (L652): Gate 4.5 in v3.8.0 proved valuable — caught conformance gaps between deliverables and specs that template-level checks miss. This phase codifies that innovation as standard process.

**When**: AFTER Phase 0.8 (Template Deep Conformance), BEFORE Phase 0.9 (Dogfood & Release Quality)

**Checklist**:

1. [ ] **Identify all new/modified artifacts** in this release:
   - New scripts (`.py`)
   - Modified SOPs (`.md`)
   - New/modified specs (`.md`)
   - New/modified templates (`.md`)
   - New/modified skills (`.claude/skills/`)

2. [ ] **For each artifact, verify conformance**:
   - Artifact has a governing spec identified
   - All SHALL requirements from governing spec are met
   - All SHOULD requirements from governing spec are met (or deviation documented)

3. [ ] **Resolve any violations**:
   - SHALL violations: MUST be fixed before proceeding (BLOCKING)
   - SHOULD violations: Document rationale if not addressing
   - Record: "Deliverable conformance: X/Y artifacts conformant"

4. [ ] **Document in PROJECT_PLAN**:
   - Record conformance audit results
   - Note any waivers or deviations

**Checkpoint**: 0 SHALL violations across all new/modified deliverables.

**If Violations**:
1. **STOP** — Do NOT proceed to Phase 0.9
2. **Fix** — Resolve SHALL violations
3. **Re-verify** — Confirm fix resolves violation
4. **Document** — Record issue and resolution

**Implements**: D40 (SOP Phase 0.85 Deliverable Conformance Check), L652 (Deliverable Conformance Gap)

---

### Phase 0.9: Dogfood & Release Quality (R-REL-030 through R-REL-034)

**Purpose**: Validate changes through internal usage before public release

**Rationale**: L576 revealed release SOP optimizes for "release mechanics" not "release quality." Dogfooding, conformance regression, and rollback planning were ad-hoc. This phase ensures release confidence, not just release completion.

**When**: AFTER Phase 0.8 (Template Conformance), BEFORE Phase 1 (Commit)

**Requirements**:

| ID | Requirement | Purpose |
|----|-------------|---------|
| R-REL-030 | Dogfood on pilot template/instance | Validate real-world usage |
| R-REL-031 | Conformance regression on existing instance | Ensure no breakage |
| R-REL-032 | Rollback plan documented | Recovery readiness |
| R-REL-033 | Post-release smoke test defined | Verify deployment |
| R-REL-034 | Monitoring/feedback channel identified | Issue detection |

**Checklist**:

1. [ ] **R-REL-030: Dogfood on Pilot** (BLOCKING):
   ```bash
   # Select pilot (typically template-developer-aget or managing agent)
   PILOT="template-developer-aget"

   # Validate new features work in real usage
   # - If new skills: invoke and verify behavior
   # - If new SOP: execute on real case
   # - If new spec: validate conformance

   # Document pilot results
   echo "Pilot: $PILOT"
   echo "Features tested: [list]"
   echo "Issues found: [list or none]"
   ```

2. [ ] **R-REL-031: Conformance Regression** (BLOCKING):
   ```bash
   # Run conformance on existing private instance
   python3 .aget/patterns/conformance/validate_conformance.py \
     /Users/gabormelli/github/aget-framework/private-aget-framework-AGET \
     --verbose

   # Expected: L2+ score (60%+ compliance)
   # If regression: STOP and investigate
   ```

3. [ ] **R-REL-032: Rollback Plan** (BLOCKING):
   ```markdown
   # Document in PROJECT_PLAN:

   ## Rollback Plan

   IF release causes issues:
   1. Revert: `git revert HEAD~N` on affected repos
   2. Restore: Previous skill/ontology versions from backup
   3. Notify: Fleet via supervisor, external via GitHub
   4. Document: File incident L-doc

   Rollback owner: [agent name]
   Rollback trigger: [conditions]
   ```

4. [ ] **R-REL-033: Smoke Test Defined**:
   ```bash
   # Define post-release checks (run after Phase 3)

   POST_RELEASE_SMOKE="
   1. Clone fresh template
   2. Run instantiation script
   3. Verify wake_up works
   4. Verify new features accessible
   "
   ```

5. [ ] **R-REL-034: Monitoring Channel**:
   ```markdown
   # Document in PROJECT_PLAN:

   ## Monitoring & Feedback

   - Issue intake: aget-framework/aget issues
   - Response SLA: 48 hours for critical, 1 week for normal
   - Escalation: via supervisor if blocking
   ```

**Checkpoint**: All 5 requirements satisfied before proceeding to Phase 1.

**If Issues**:
1. **STOP** - Do NOT proceed to Phase 1
2. **Fix** - Address dogfood/regression issues
3. **Update** - Refine rollback plan if needed
4. **Re-verify** - Run pilot and regression again

**Implements**: R-REL-030 through R-REL-034 (Release Quality Validation)
**Related**: L576 (Release Quality Validation Gap), PROJECT_PLAN_archetype_customization_v3.5_v1.0.md Gate 5.75

### Phase 0.95: Skill Dependency Validation (R-REL-042)

**Purpose**: Verify all skill dependencies exist in template repos before release

**Rationale**: L586 revealed skills deployed without runtime dependencies (8/8 broken). L596 revealed workspace-local fixes not propagated to templates. This gate ensures templates ship with complete skill infrastructure.

**When**: AFTER Phase 0.9 (Dogfood), BEFORE Phase 1 (Commit)

**Checklist**:
- [ ] Run validator on all template repos:
```bash
FRAMEWORK_DIR="/Users/gabormelli/github/aget-framework"
for repo in $FRAMEWORK_DIR/template-*-aget; do
  RESULT=$(python3 $FRAMEWORK_DIR/aget/validation/validate_skill_dependencies.py \
    --base-dir "$repo" --check 2>&1 | tail -1)
  echo "$(basename $repo): $RESULT"
done
```
- [ ] ALL templates report `R-SKILL-DEP-001 Validation: PASS`
- [ ] If ANY fail: STOP, remediate missing dependencies, re-validate

**If Failures**:
1. **STOP** - Do NOT proceed to Phase 1
2. **Identify** - Run with `--verbose` to see missing paths
3. **Fix** - Create missing files or fix SKILL.md path references
4. **Re-validate** - All templates must pass

**Implements**: R-REL-042 (Skill Dependency Validation)
**Related**: L586 (Skill Infrastructure Deployment Gap), L596 (Propagation Gap), SOP_skill_deployment.md

---

### Phase 0.97: Public Surface Audit

**Purpose**: Verify no private information has leaked into public repos and all versions are consistent before committing/pushing the release.

**Rationale**: L638 revealed 50 issues filed to the public repo took 2 months to detect. L430 found proprietary company names in public templates. L653 found AGENTS.md stuck 2 releases behind. This automated check catches leaks before they ship.

**When**: AFTER Phase 0.95 (Skill Dependencies), BEFORE Phase 1 (Commit)

**Checklist**:
- [ ] Run public surface audit against target version:
```bash
python3 scripts/public_surface_audit.py --version X.Y.Z
```
- [ ] Dimension 1 (Private Info): 0 true critical findings
- [ ] Dimension 2 (Version Drift): All repos match target version
- [ ] Dimension 3 (Issue Routing): 0 private content in public issues
- [ ] Dimension 4 (Metadata): codemeta.json and CITATION.cff match target version
- [ ] If ANY critical findings: STOP, remediate, re-run

**If Failures**:
1. **STOP** — Do NOT proceed to Phase 1
2. **Categorize** — Run `--json` to identify finding context (spec/scaffold = expected vs. true leak)
3. **Fix** — Sanitize or remove private content from public repos
4. **Re-run** — All dimensions must pass

**Note on False Positives**: The audit detects patterns in specs and governance docs that MUST reference private patterns (e.g., issue governance spec defines routing rules). These are expected. True critical findings are private info in non-governance content (session files, legacy plans, READMEs).

**Implements**: L638 (Private-First Issue Routing), L430 (Content Security), L653 (Version Drift)
**Related**: SOP_pre_publication_security.md, CONTENT_INTEGRITY_VALIDATION_SPEC.md, sanitize_issue_content.py

---

### Phase 1: Commit (Local Verification)

```bash
# 1. Commit all repos locally (don't push yet)
for repo in aget template-supervisor-aget template-worker-aget \
            template-advisor-aget template-consultant-aget \
            template-developer-aget template-spec-engineer-aget; do
  cd /Users/gabormelli/github/aget-framework/$repo
  git add . && git commit -m "Release vX.Y.Z: description"
done

# 2. Verify version consistency
grep '"aget_version"' /Users/gabormelli/github/aget-framework/*/.aget/version.json

# 3. Run contract tests
cd /Users/gabormelli/github/aget-framework/private-aget-framework-AGET
python3 -m pytest tests/ -v
```

**Checkpoint**: All repos committed locally, versions match, tests pass.

### Phase 2: Push (Deployment)

```bash
# 1. Push aget/ core first (dependency root)
cd /Users/gabormelli/github/aget-framework/aget
git push origin main

# 2. Push templates alphabetically
for repo in template-advisor-aget template-consultant-aget \
            template-developer-aget template-spec-engineer-aget \
            template-supervisor-aget template-worker-aget; do
  cd /Users/gabormelli/github/aget-framework/$repo
  git push origin main
done

# 3. Verify all pushes succeeded
for repo in aget template-*-aget; do
  echo "=== $repo ==="
  cd /Users/gabormelli/github/aget-framework/$repo
  git status
done
```

**Checkpoint**: All 7 repos pushed, no failures.

### Phase 3: Tag & Release

**Purpose**: Create git tags and GitHub Releases for all repos

**Important**: Tags ≠ Releases on GitHub. Tags are git objects; Releases are GitHub UI features created separately.

#### 3.1. Create Tags (All Repos)

```bash
cd /Users/gabormelli/github/aget-framework

# Tag all repos (core + 6 templates)
for repo in aget template-supervisor-aget template-worker-aget template-advisor-aget template-consultant-aget template-developer-aget template-spec-engineer-aget; do
  echo "=== Tagging $repo ==="
  cd "$repo"
  git tag -a vX.Y.Z -m "Release vX.Y.Z: Brief description

Full release notes at:
https://github.com/aget-framework/aget/blob/main/specs/deltas/AGET_DELTA_vX.Y.md"
  cd ..
done
```

#### 3.2. Push Tags

```bash
# Push tags to remote
for repo in aget template-supervisor-aget template-worker-aget template-advisor-aget template-consultant-aget template-developer-aget template-spec-engineer-aget; do
  echo "=== Pushing tag for $repo ==="
  cd "$repo"
  git push origin vX.Y.Z
  cd ..
done
```

#### 3.3. Create GitHub Releases

**Note**: Pushing tags does NOT create GitHub Releases. Use `gh` CLI:

```bash
# Create releases for all repos
for repo in aget template-supervisor-aget template-worker-aget template-advisor-aget template-consultant-aget template-developer-aget template-spec-engineer-aget; do
  echo "=== Creating release for $repo ==="
  cd "$repo"
  gh release create vX.Y.Z \
    --title "vX.Y.Z - Brief Title" \
    --notes "Release notes content here

See https://github.com/aget-framework/aget/blob/main/specs/deltas/AGET_DELTA_vX.Y.md for complete changes."
  cd ..
done
```

**Release Notes Template**: Use standard release notes (see section below)

#### 3.4. Verify Releases

```bash
# Check releases are visible
for repo in aget template-supervisor-aget template-worker-aget template-advisor-aget template-consultant-aget template-developer-aget template-spec-engineer-aget; do
  echo "=== $repo ==="
  open "https://github.com/aget-framework/$repo/releases"
done
```

**Verification Checklist**:
- [ ] All 7 repos show new release on GitHub Releases page
- [ ] Release marked as "Latest" (green badge)
- [ ] Release notes display correctly
- [ ] Delta spec link works

**Checkpoint**: All 7 GitHub Releases visible and marked "Latest".

---

### Phase 4: Post-Release Validation (BLOCKING)

**⚠️ CRITICAL: This phase is BLOCKING. You MUST NOT proceed to Phase 5 until exit code 0.**

**Purpose**: Verify user-visible state before public announcement

**Implements**: R-PUB-001 (Public Release Completeness)

**When to Run**: AFTER Phase 3 complete, BEFORE announcing release

**Non-Negotiable**:
- Validation MUST pass (exit code 0)
- User spot-checking indicates process failure
- NO exceptions, NO shortcuts, NO "we'll fix it later"

---

#### 4.1. Automated Validation (BLOCKING)

**⚠️ DO NOT SKIP THIS STEP. DO NOT PROCEED WITHOUT EXIT CODE 0.**

Run post-release validation script:

```bash
cd /Users/gabormelli/github/aget-framework/private-aget-framework-AGET

python3 .aget/patterns/release/post_release_validation.py --version X.Y.Z
```

**Checks Performed** (12 automated checks):
- R-PUB-001-01: GitHub Releases exist (all 7 repos)
- R-PUB-001-09: Latest badge correctness (v2.11+ enhancement)
- R-PUB-001-03: Organization homepage shows current version
- R-PUB-001-10: Homepage content consistency (v2.11+ enhancement)
- R-PUB-001-04: Version badge links correctly
- R-PUB-001-05: CHANGELOG.md has version entry
- R-PUB-001-11: Historical release completeness (v2.11+ enhancement)
- R-PUB-001-07: Version accessible via git tag/release
- R-PUB-001-08: No broken links in release notes
- R-PUB-001-12: Homepage link integrity (v2.11+ Phase 4A)
- R-PUB-001-13: Validation completeness (v2.11+ Phase 4C - meta-requirement)
- R-PUB-001-14: Repository README quality (v2.11+ Phase 4C - learning release)

**Expected Output**:
```
✅ ALL VALIDATIONS PASSED
Ready for vX.Y.Z public announcement

Result: 12/12 checks passed
Exit code: 0
```

**If Exit Code 1** (VALIDATION FAILED):
1. **STOP** - Do NOT proceed to Phase 5
2. **REVIEW** - Examine failed checks in output
3. **FIX** - Address ALL failures (no exceptions)
4. **RE-RUN** - Execute validation again
5. **REPEAT** - Until exit code 0 achieved

**Save Validation Results**:
```bash
# Required for audit trail
python3 .aget/patterns/release/post_release_validation.py --version X.Y.Z > findings/VALIDATION_RESULT_vX.Y.Z_post_phase4.txt
```

**Checkpoint**: Exit code 0 achieved, validation results saved

---

#### 4.2. Manual Validation

Run manual checks from checklist:

```bash
# Open manual validation checklist
open sops/PUBLIC_RELEASE_VALIDATION.md
```

**Manual Checks** (not automated):
- R-PUB-001-02: Release artifact completeness (content quality)
- R-PUB-001-06: Release notes depth (if major/minor)

**Verification**:
- [ ] Spot-check one release: proper title, body, tag, published status
- [ ] If major/minor: Release notes comprehensive (>500 chars or separate doc)

---

#### 4.3. Organization Homepage Update (if not done)

**Check**: Did Phase 3 update org homepage?

If automated script shows homepage outdated:

```bash
cd /Users/gabormelli/github/aget-framework/.github

# Update profile/README.md
# Change version badge: version-OLD → version-X.Y.Z
# Change badge link: /tag/vOLD → /tag/vX.Y.Z

git add profile/README.md
git commit -m "docs: Update organization homepage to vX.Y.Z"
git push origin main
```

**Verification**:
- [ ] Visit https://github.com/aget-framework
- [ ] Badge shows vX.Y.Z
- [ ] Badge link works (not 404)

**Homepage Quality Rubric Check** (RUBRIC_homepage_quality_v1.0.md):

After updating the homepage, score it against the homepage quality rubric. Minimum **L2 (Compliant)** required to proceed.

```
Dimensions to check:
  D1: Version Accuracy  — badges, dates, roadmap header match GitHub Release
  D2: Roadmap Completeness — every released version has an entry
  D3: Content Attribution — each entry lists only its own deliverables
  D4: Content Freshness  — no stale announcement language in standing content
  D5: Link Validity      — all links resolve to current targets

Critical Requirements (auto-fail to L0):
  CR-1: Version badge MUST match latest GitHub Release tag
  CR-2: No more than 1 released version may be missing from roadmap
```

- [ ] Homepage rubric score ≥ L2 (record score: ____/3.0)
- [ ] If score < L2: remediate per rubric guidance before proceeding

---

#### 4.4. Validation Record (CAP-REL-021)

**Requirement**: Per CAP-REL-021 (Persistent Validation Logging), validation results SHALL be persisted as structured JSON to `.aget/logs/validation_log.jsonl`. This replaces the previously planned (but never implemented) `.aget/releases/validation_log.txt`.

**Rationale** (L605): Every prior release's validation results were ephemeral (stdout only). No audit trail existed, preventing trend analysis and regression detection across releases. The SOP previously referenced `validation_log.txt` but the file and directory were never created.

**Tooling** (v3.6.0):
```bash
cd /Users/gabormelli/github/aget-framework/private-aget-framework-AGET

# Wrap any validation script with persistent logging:
python3 .aget/patterns/release/validation_logger.py \
    --wrap .aget/patterns/release/post_release_validation.py -- --version X.Y.Z

# Or wrap pre-release validation:
python3 .aget/patterns/release/validation_logger.py \
    --wrap .aget/patterns/release/pre_release_validation.py -- --version X.Y.Z

# Or wrap housekeeping sanity check:
python3 .aget/patterns/release/validation_logger.py \
    --wrap .aget/patterns/session/aget_housekeeping_protocol.py

# Commit validation log:
git add .aget/logs/validation_log.jsonl
git commit -m "chore: Record vX.Y.Z validation (CAP-REL-021)"
```

The wrapper preserves original script output while appending a structured JSON record to `.aget/logs/validation_log.jsonl` (CAP-REL-021-01 through 021-05). The `.aget/logs/` directory is created automatically if absent (CAP-REL-021-03).
```

**Replaces**: The previously specified `echo "..." >> .aget/releases/validation_log.txt` which was never implemented.

**Note**: `validation_logger.py` self-test: `python3 .aget/patterns/release/validation_logger.py --test`

---

#### 4.5. Propagation Audit (CAP-REL-024)

**Requirement**: Per CAP-REL-024 (Propagation Audit), verify that all changes intended for template repos actually reached their deployment targets. Validate against the repos users will clone (template-*-aget), not the authoring workspace.

**Rationale** (L596, L605): v3.4.0 and v3.5.0 both had workspace-local validation pass while template repos remained at prior versions. The managing agent released versions it hadn't itself validated at the deployment target.

**Implementation status**: CAP-REL-024 specifies the requirements. Until `propagation_audit.py` tooling is implemented (v3.6.0 target), verify propagation manually:

```bash
VERSION="X.Y.Z"

# Verify each template repo received the version update
for repo in template-{supervisor,worker,advisor,consultant,developer,spec-engineer}-aget; do
  REPO_VERSION=$(python3 -c "import json; print(json.load(open('/Users/gabormelli/github/aget-framework/$repo/.aget/version.json'))['aget_version'])" 2>/dev/null || echo "MISSING")
  CHANGELOG=$(grep -c "\[$VERSION\]" "/Users/gabormelli/github/aget-framework/$repo/CHANGELOG.md" 2>/dev/null || echo "0")
  echo "$repo: version.json=$REPO_VERSION, CHANGELOG=$([[ $CHANGELOG -gt 0 ]] && echo 'present' || echo 'MISSING')"
done
```

**Blocking**: Per CAP-REL-024-03, release SHALL NOT be marked complete if propagation_complete is false for any target.

#### 4.5.1. Publication Integrity Verification (L659, D60)

**Requirement**: Verify that every deliverable claimed in CHANGELOG.md and DEPLOYMENT_SPEC actually exists at its claimed path in the public repos. Prevents "Release Announcement Ahead of Reality" anti-pattern (L659).

**Rationale** (L658, L659): v3.8.0 had a 53% publication integrity score — 8 of 17 claimed deliverables did not exist at their claimed paths. Root cause: the release process marks deliverables as IMPLEMENTED internally without verifying publication to public repos.

**Procedure**:
```bash
# For each file path claimed in CHANGELOG.md or DEPLOYMENT_SPEC:
for claimed_path in <list_of_claimed_paths>; do
  if [ -f "/Users/gabormelli/github/aget-framework/$claimed_path" ]; then
    echo "PASS: $claimed_path"
  else
    echo "FAIL: $claimed_path — does not exist in public repo"
  fi
done
# All must PASS. Any FAIL → publish the file or remove the claim.
```

**Blocking**: Do NOT create RELEASE_HANDOFF until all claimed deliverables are verified present. Missing files must be either published or removed from claims.

---

#### 4.6. Post-Release State Snapshot (CAP-REL-023)

**Requirement**: Per CAP-REL-023-02, AFTER release completion, capture a post-release Release_Snapshot. Diff against the pre-release snapshot (captured before Phase 0) to produce the release diff.

**Implementation status**: CAP-REL-023 specifies the requirements. Until `release_snapshot.py` tooling is implemented (v3.6.0 target), capture state manually and diff against pre-release baseline.

---

**Checkpoint**: All validations passed (automated + manual), org homepage current, propagation verified (CAP-REL-024), post-release snapshot captured (CAP-REL-023)

**Decision Point**: Proceed to announcement, or stop here?

---

### Phase 5: Public Announcement (Optional)

**Applies**: Major and minor releases (vX.0.0, vX.Y.0)

**Skip**: Patch releases (vX.Y.Z where Z > 0) - release notes sufficient

---

#### 5.1. Announcement Channels

**Primary** (always):
- GitHub Release notes (already done)
- Organization homepage badge (already done)

**Secondary** (future):
- Blog post (if blog established)
- Social media (if active)
- Discord/Slack (if community channels exist)
- Mailing list (if mailing list exists)

---

#### 5.2. Announcement Template

See: `docs/COMMUNICATION_STANDARDS.md` for full template

**Key Elements**:
- What's New (3-5 highlights)
- Why It Matters (user benefit)
- How to Upgrade (migration steps if breaking)
- Learn More (links to changelog, delta spec, learnings)

---

**Checkpoint**: Release announced, users informed

---

### Phase 6: Fleet Handoff (R-REL-019)

**Purpose**: Bridge the gap between "release exists" and "fleet has adopted"

**When**: AFTER Phase 4 or Phase 5 completion (public release validated)

**Rationale** (L511): Release success metric previously excluded downstream adoption. Framework releases were considered complete when public artifacts existed, but fleet upgrade status was unknown.

---

#### 6.1. Ownership Boundary

| Responsibility | Owner |
|----------------|-------|
| Public release execution | private-aget-framework-AGET |
| Release handoff artifact | private-aget-framework-AGET |
| Fleet upgrade coordination | private-supervisor-AGET |
| Pilot upgrade execution | Individual pilot AGETs |
| Adoption tracking | private-supervisor-AGET |

---

#### 6.2. Create Handoff Artifact

```bash
# Create handoff artifact from template
cp sops/templates/RELEASE_HANDOFF_TEMPLATE.md handoffs/RELEASE_HANDOFF_vX.Y.Z.md

# Edit with version-specific content
# - Update version, date, breaking changes
# - Fill release summary, key changes
# - Include upgrade guide
# - Add pilot tracking table with all known pilots
```

**Required Sections**:
- **Receiving Agent Governance Checklist** (BLOCKING - L562)
- Release Summary (theme, key changes, new specs)
- Upgrade Guide (for instances and templates)
- Fleet Action Required (supervisor tasks, pilot tracking)
- Acknowledgment section

**Governance Note (L562)**: Handoff artifacts MUST include a governance checklist that reminds receiving agent to follow their own upgrade SOP before executing. Handoff provides information, not authorization to bypass governance.

**Deployment Requirements (L582)**:

When syncing universal skills to fleet agents, supervisor MUST follow:

- **R-DEP-004**: MUST diff before overwriting skills with local modifications
- **R-DEP-005**: Extensions (additions beyond template) MUST be preserved

Pre-sync check protocol:
```bash
# Before overwriting any skill
for skill in $UNIVERSAL_SKILLS; do
  if [ -d "$AGENT/.claude/skills/$skill" ]; then
    diff -rq "$AGENT/.claude/skills/$skill" "$TEMPLATE/.claude/skills/$skill"
    # If differs: classify as drift (fix) vs extension (preserve)
  fi
done
```

---

#### 6.3. Handoff Checklist

- [ ] Create `handoffs/RELEASE_HANDOFF_vX.Y.Z.md` from template
- [ ] Fill Release Summary with key changes
- [ ] Include upgrade guide (or reference UPGRADING.md)
- [ ] Add all known pilot AGETs to tracking table
- [ ] Set adoption targets and priorities
- [ ] Notify supervisor of new version availability
- [ ] **Publish public handoff** (6.3.1 below)

---

#### 6.3.1. Public Handoff Publication (R-REL-019-07, L612)

**Purpose**: Make handoff discoverable by external/remote fleet supervisors who cannot access private repos.

**Procedure**:
1. Copy private handoff as starting point:
   ```bash
   cp handoffs/RELEASE_HANDOFF_vX.Y.Z.md /path/to/aget/handoffs/RELEASE_HANDOFF_vX.Y.Z.md
   ```
2. Apply sanitization checklist (ALL items MUST pass):
   - [ ] No private agent names (`grep -c "private-" file` returns 0)
   - [ ] No private repo paths (`grep -c "gmelli/" file` returns 0)
   - [ ] No fleet size disclosures (`grep -ci "32 agents\|fleet.*[0-9]" file` returns 0)
   - [ ] No internal commit hashes in tracking tables
   - [ ] Pilot tracking table uses blank template (not filled internal data)
   - [ ] "Context for External Fleets" section present (R-REL-019-02)
   - [ ] Every file path reference verified against public repo filesystem (L658)
   - [ ] Message under 60 lines for non-breaking minor releases (L660)
3. Verify sanitization:
   ```bash
   grep -c "private-" aget/handoffs/RELEASE_HANDOFF_vX.Y.Z.md  # Must be 0
   grep -q "Context for External" aget/handoffs/RELEASE_HANDOFF_vX.Y.Z.md  # Must match
   ```
4. Commit to public repo

**Precedent**: `aget/handoffs/RELEASE_HANDOFF_v3.5.0.md` (format reference)

---

#### 6.4. Supervisor Notification

**Spec**: AGET_SUPERVISOR_NOTIFICATION_SPEC v1.0.0 (18 requirements, 5 CAP groups)
**Template**: `handoffs/TEMPLATE_SUPERVISOR_NOTIFICATION.md`
**Method**: Direct notification (session handoff, email, or messaging)

**Required Sections** (R-NOTIFY-001 through R-NOTIFY-007):

| Section | Content | Requirement |
|---------|---------|-------------|
| Executive Summary | Version, theme, handoff link | R-NOTIFY-001 |
| Release Highlights | Numbered key changes | R-NOTIFY-002 |
| Breaking Changes | "None" or list with migration | R-NOTIFY-003 |
| Fleet Action Required | Numbered steps for supervisor | R-NOTIFY-004 |
| Post-Release Quality | Validation results table | R-NOTIFY-005 |
| Traceability | Public links to handoff, changelog, release | R-NOTIFY-006 |
| Supervisor Response Log | Acknowledgment checkboxes | R-NOTIFY-007 |

**Conditional Sections**:
- Upgrade Warnings: REQUIRED if upgrade carries risk of customization loss (R-NOTIFY-008)
- Known Items: OPTIONAL for non-blocking issues (R-NOTIFY-009)

**Sanitization** (R-NOTIFY-010 through R-NOTIFY-016):
- From/To fields use role names ("Framework Manager", "Fleet Supervisor"), not private agent names
- Traceability links use public URLs (`https://github.com/aget-framework/...`)
- No private agent names, repo paths, fleet size, or session references

**Expected Response** (within 48 hours):
- Acknowledgment receipt
- Fleet broadcast confirmation
- Pilot upgrade tracking initiated

---

#### 6.4.1. Supervisor Session Prompt (Copy-Paste Ready)

**Use this prompt to start a supervisor session for handoff acknowledgment:**

```
wake up.

RELEASE HANDOFF NOTIFICATION

Version: vX.Y.Z has been released to aget-framework.

Action Required:
1. Review the release handoff: https://github.com/aget-framework/aget/blob/main/handoffs/RELEASE_HANDOFF_vX.Y.Z.md
2. Acknowledge receipt in the handoff artifact
3. Broadcast vX.Y.Z availability to fleet
4. Initiate pilot upgrade tracking

Breaking Changes: [Yes/No]
Priority: [P1: main portfolio by DATE / P2: other portfolios by DATE]

Handoff From: Framework Manager
```

**Customization Notes**:
- Replace `X.Y.Z` with actual version
- Update Breaking Changes field
- Set realistic priority dates (typically P1: 1 week, P2: 3 weeks)
- For internal supervisors with private repo access, you may add the private handoff path alongside the public URL

---

#### 6.5. Handoff Verification

```bash
# Verify handoff artifact exists
[ -f "handoffs/RELEASE_HANDOFF_vX.Y.Z.md" ] && echo "PASS" || echo "FAIL"

# Verify required sections
grep -cE "Release Summary|Upgrade Guide|Fleet Action|Acknowledgment" \
  handoffs/RELEASE_HANDOFF_vX.Y.Z.md | xargs -I {} test {} -ge 4 && echo "PASS" || echo "FAIL"

# Verify pilot tracking table
grep -q "Pilot.*Status\|private-supervisor-AGET" \
  handoffs/RELEASE_HANDOFF_vX.Y.Z.md && echo "PASS" || echo "FAIL"
```

---

**Checkpoint**: Handoff artifact created, supervisor notified

**Decision Point**: Proceed to Phase 7 (Release Knowledge Transfer)? [GO/NO-GO]

---

### Phase 7: Release Knowledge Transfer

**Trigger**: Phase 6 complete (handoff delivered, supervisor notified).
**Output**: Release_Bridge document + prior release research integrated into next release cycle.

This phase has two sub-phases with different timing:

#### 7.1. Bridge Creation (at release completion)

**When**: After PROJECT_PLAN retrospective is complete (Gate 9 or equivalent).

**Purpose**: Capture release velocity, follow-on items, recurring gaps, gate innovations, and operational advice in a structured document that directly informs the next release cycle.

**Steps**:

1. Create `planning/RELEASE_BRIDGE_vX.Y.Z_to_next.md` from `planning/TEMPLATE_RELEASE_BRIDGE.md`
2. Populate velocity profile from PROJECT_PLAN velocity analysis
3. Extract follow-on items from retrospective (pre-prioritize for next scope decision)
4. Identify recurring gaps (items deferred 2+ consecutive releases)
5. Document gate innovations with carry-forward recommendation (Standard / Optional / One-off)
6. Add cumulative pre-release checklist items discovered during this release
7. Write operational advice ("What I wish I knew at the start" — 3-5 concrete items)

**Verification**:
```bash
# Bridge document exists
[ -f "planning/RELEASE_BRIDGE_vX.Y.Z_to_next.md" ] && echo "PASS" || echo "FAIL"

# Contains velocity data
grep -q "Velocity Profile" planning/RELEASE_BRIDGE_vX.Y.Z_to_next.md && echo "PASS" || echo "FAIL"

# Contains follow-on items
grep -q "Follow-On Items" planning/RELEASE_BRIDGE_vX.Y.Z_to_next.md && echo "PASS" || echo "FAIL"
```

**Checkpoint**: Bridge document created and references retrospective.

---

#### 7.2. Prior Release Research (at next release start)

**When**: BEFORE creating VERSION_SCOPE for the next release. This sub-phase executes at the START of the next release cycle, not at the end of the current one.

**Purpose**: Ensure the next release benefits from institutional memory by requiring structured research into prior release outcomes before planning begins.

**Prerequisite — Deployment Verification (L656)**:

Before researching the prior release, verify it was actually deployed:

0. Check prior release deployment status:
   - Read `handoffs/RELEASE_HANDOFF_vPRIOR.md` pilot tracking table
   - Verify >= 1 agent has deployed and confirmed the prior version
   - If no deployment evidence exists: **STOP** — deployment verification is #1 priority, not next-release planning
   - Document deployment status in "Prior Release Research" section

**Loading Dock guard**: If deployment is unverified, the next-best action is "verify deployment," not "plan next release." Do not create VERSION_SCOPE until at least one downstream deployment is confirmed. (L656)

**Steps**:

1. Read the most recent RELEASE_BRIDGE document (if exists)
2. Read the prior 1-2 release PROJECT_PLAN retrospectives (all subsections)
3. Review velocity analysis from prior releases (calibrate effort estimates)
4. Check for recurring gaps (items deferred 2+ consecutive releases)
5. Extract cumulative pre-release checklist additions into the new release plan
6. Document findings in "Prior Release Research" section of the new PROJECT_PLAN's KB Audit

**Output**: "Prior Release Research" section populated in new release PROJECT_PLAN.

**Integration**: Feeds directly into SOP_release_scope_decision.md Phase 0 (Scope_Initialization).

**Checkpoint**: Prior release research documented in new PROJECT_PLAN KB Audit. Deployment verification status recorded.

**Decision Point**: Prior release research complete. Proceed to scope initialization.

---

#### 7.3. Continuous Deployment Monitoring (per-session)

**When**: Every session after release completion, until at least one deployment is confirmed.

**Purpose**: Structural enforcement of deployment verification. Behavioral guards (Phase 7.2 prerequisite, CLAUDE.md rules) depend on the agent reading and complying. This phase adds automated, per-session monitoring that surfaces deployment status whether or not the agent remembers to check. (CAP-REL-027, L656)

**Mechanism**:

The releasing agent's wake-up extension (`scripts/wake_up_ext.py`) automatically calls `scripts/deployment_monitor.py` to check deployment status:

| Status | Condition | Display | Action |
|--------|-----------|---------|--------|
| GREEN | >= 1 confirmed deployment | "vX.Y.Z deployed (N confirmed)" | None |
| YELLOW | 0 confirmed, < 7 days old | "vX.Y.Z UNVERIFIED (Nd)" | Advisory — check supervisor status |
| RED | 0 confirmed, >= 7 days old | "vX.Y.Z UNVERIFIED. BLOCKED." | VERSION_SCOPE creation blocked (R-REL-027-05) |

**Setup** (one-time, at Phase 6 completion):

```bash
# Initialize deployment record after release
python3 scripts/deployment_monitor.py --init --version X.Y.Z
```

This creates a `Deployment_Status_Record` in `.aget/logs/deployment_status.jsonl` with `status=RELEASED` and `confirmed_deployments=0`.

**Per-session** (automatic via wake_up_ext.py):

The wake-up extension reads config (`deployment_monitoring.enabled` in `.aget/config.json`) and, if enabled, calls the deployment monitor to check status and append a status line to wake-up output.

**Manual operations**:

```bash
# Check deployment status
python3 scripts/deployment_monitor.py --check --version X.Y.Z

# Check supervisor version via filesystem (ADR-004 tier_basic)
python3 scripts/deployment_monitor.py --check-supervisor --local /path/to/supervisor

# Confirm a deployment
python3 scripts/deployment_monitor.py --confirm --version X.Y.Z --deployer "supervisor" --method filesystem
```

**Three-Tier Compliance** (ADR-004):

| Tier | Method | Usage |
|------|--------|-------|
| Basic (filesystem) | `--check-supervisor --local /path` | Default for co-located supervisors |
| Standard (git) | Version comparison via git tags | Future enhancement |
| Rich (gh) | `--check-supervisor --remote repo` | For remote supervisors via GitHub API |

**Checkpoint**: Deployment status visible in every wake-up until confirmed.

---

## Rollback

If release has issues:

```bash
# Delete remote tag
git push origin :refs/tags/vX.Y.Z

# Delete local tag
git tag -d vX.Y.Z

# Revert commit if needed
git revert HEAD
git push origin main
```

---

## References

**Patterns**:
- L333: Governance Grounding Protocol
- L352: Requirement-to-Test Traceability
- L357: Version Migration as Explicit Deliverable
- L376: PROJECT_PLAN Checklist Derivation (Checklist-Driven Gate Design)
- L406: Post-Release Validation Must Be Systematic
- L421: Enforcement vs Existence Testing
- L429: Version Inventory Requirement for Atomic Releases
- L430: Pre-Publication Content Security Review
- L431: Release Artifact Inventory Requirement (Organization-Level Artifacts)
- L444: Version Inventory Coherence Requirement (Coherence Testing)
- L465: Release Scope Consolidation Requirement (Single Source of Truth for Scope)
- L511: Release-to-Fleet Propagation Gap (Fleet Handoff Protocol)
- L521: Version-Bearing File Specification-to-Tool Gap
- L579: Version-Bearing File Enumeration Gap (Concrete File Inventory)
- L596: Workspace-Local Remediation Propagation Gap
- L604: Systemic Top-Down-Only Framework Pattern
- L605: Release Observability and Enforcement Gap (root cause: fixes are documentation, not enforcement)
- L656: Loading Dock Anti-Pattern (deployment verification before next-release planning)
- L658: Handoff Artifact Ground Truth Verification (filesystem verification before handoff)
- L659: Release Publication Integrity Gap (verify claimed deliverables exist in public repos)
- L660: Governance-First Communication Anti-Pattern (line budget for external handoffs)

**Related SOPs**:
- SOP_version_coherence_validation.md (Version_Bearing_File coherence procedure)

**Specifications**:
- AGET_VERSIONING_CONVENTIONS.md (lines 142-148)
- RELEASE_VERIFICATION_CHECKLIST.md (14 R-PUB-001 requirements)
- AGET_RELEASE_SPEC.md v1.10.0 — CAP-REL-021 through CAP-REL-027 (release observability, enforcement, deployment monitoring)

**Tracking**:
- aget-framework/aget#1: Release Coordination Protocol enhancement

---

*SOP_release_process.md v1.29 — Phase 4.5.1: Publication Integrity Verification + Phase 6.3.1: L658/L660 guards (D60, L659)*
