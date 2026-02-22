# AGET Framework Releases

**Audience**: Users wanting to understand release process, frequency, and quality standards

**Purpose**: Explain how releases work, when they happen, and how to stay informed

---

## Quick Reference

**Latest Release**: See https://github.com/aget-framework/aget/releases

**Release Cadence**: Monthly minor releases (target)

**Next Release**: Check GitHub Milestones for planning

---

## How Releases Work

### Release Types

| Type | Format | Frequency | Announcement |
|------|--------|-----------|--------------|
| **Major** | vX.0.0 | Rare (breaking changes needed) | Comprehensive |
| **Minor** | vX.Y.0 | Monthly (target) | Standard |
| **Patch** | vX.Y.Z | As needed (bug fixes) | Minimal |

---

### Release Process Overview

**User-Visible Steps**:

1. **Development**: Features/fixes implemented in private
2. **Validation**: Contract tests must pass (80+ tests)
3. **Version Bump**: All 7 repos synchronized
4. **Tagging**: Git tags created
5. **Release Creation**: GitHub Releases published
6. **Homepage Update**: Organization badge updated
7. **Announcement**: Release notes published

**Behind the Scenes**:
- Multi-phase release process (5 phases)
- Pre-release validation (manager version migration)
- Post-release validation (public visibility checks)
- Automated validation scripts (R-PUB-001 requirements)

**Quality Gate**: Release not announced until ALL validation passes

---

## Release Quality Standards

Every AGET Framework release includes:

### Required Artifacts

- ✅ **Git Tags**: All 7 repositories tagged
- ✅ **GitHub Releases**: All 7 repos have release on GitHub
- ✅ **Version Consistency**: All templates at same version
- ✅ **Contract Tests**: 80+ tests passing (100% pass rate)
- ✅ **CHANGELOG**: User-facing changes documented
- ✅ **Delta Specification**: Technical changes documented
- ✅ **Organization Homepage**: Badge shows current version

### Additional (Major/Minor Only)

- ✅ **Release Notes**: Comprehensive (highlights, context, migration)
- ✅ **Migration Guide**: If breaking changes
- ✅ **Learning Documentation**: Learnings captured (L-series)

### Validation

Before announcement:
- ✅ Automated validation: 6 checks (R-PUB-001-01, 03, 04, 05, 07, 08)
- ✅ Manual validation: 2 checks (content quality, release notes depth)
- ✅ No broken links in release notes
- ✅ All repositories synchronized

**Standard**: 100% validation pass required for public announcement

---

## Release Cadence

### Target Schedule

**Minor Releases**: 1st week of each month
**Patch Releases**: As needed (bug fixes)

### Actual History

| Month | Target | Actual | Notes |
|-------|--------|--------|-------|
| Dec 2025 | v2.12.0 | v2.11.0 | On schedule |
| Nov 2025 | v2.11.0 | v2.10.0 | Delayed (capability architecture) |
| Oct 2025 | v2.10.0 | v2.7-2.9 | Rapid iteration (private→public) |

**Reality**: Early framework releases (v2.0-v2.10) were rapid iteration. v2.11.0+ follows monthly cadence.

See [VERSION_HISTORY.md](VERSION_HISTORY.md) for complete timeline.

---

## How to Stay Informed

### Watch GitHub Releases

**Recommended**: Watch the repository for release notifications

```
1. Visit https://github.com/aget-framework/aget
2. Click "Watch" (top right)
3. Select "Custom" → "Releases"
4. Click "Apply"
```

**Result**: Email notification when new release published

---

### Check Organization Homepage

**Badge**: Always shows latest version

Visit: https://github.com/aget-framework

Badge format: `version-X.Y.Z`

Click badge → Direct link to latest release

---

### RSS/Atom Feed

**GitHub Release Feed**:
```
https://github.com/aget-framework/aget/releases.atom
```

Add to your RSS reader for automatic notifications.

---

### Milestones & Roadmap

**Upcoming Releases**:
- GitHub Milestones: https://github.com/aget-framework/aget/milestones
- Shows planned features per version

**Long-Term Roadmap**:
- See aget/ README.md "Roadmap" section
- Strategic direction (quarterly/annual)

---

## What Goes Into a Release

### Feature Development

**Source**: Private experimentation → validated patterns → public release

**Criteria for Inclusion**:
- Pattern proven in production (private agents)
- Contract tests written
- Documentation complete
- No breaking changes (unless major release)

**Example**: v2.11.0 Memory Architecture
- Proven in supervisor agent (L335)
- L352 traceability pattern validated across 5 requirement groups
- 40 contract tests written
- Full documentation (patterns, SOPs, L-docs)

---

### Bug Fixes

**Priority Levels**:
- **Critical** (security, data loss): Immediate patch release
- **High** (broken functionality): Next patch release (within week)
- **Medium** (degraded experience): Next minor release
- **Low** (cosmetic, edge cases): Backlog (future release)

**Inclusion**: Bug fixes batched into patch releases when sufficient fixes accumulated.

---

### User Requests

**Feature Requests**:
1. File issue with "enhancement" label
2. Describe use case and benefit
3. Framework team evaluates for roadmap
4. If accepted, added to milestone
5. Implemented and released per schedule

**Timeline**: Feature requests typically 1-3 months (depends on scope, priority)

**Transparency**: Issue labels show status (planned, in-progress, released)

---

## Release Naming

### Version Numbering

**Format**: vMAJOR.MINOR.PATCH (e.g., v2.11.0)

**Rationale**: Semantic versioning (https://semver.org/)

---

### Release Titles

**Format**: "vX.Y.Z - Brief Theme"

**Examples**:
- v2.11.0 - Memory Architecture + L352 Traceability
- v2.10.0 - Capability Composition Architecture
- v2.9.0 - Information Storage Standardization

**Purpose**: Quickly communicate release focus

---

## Pre-Release Testing

### Contract Tests

**Requirement**: All 80+ contract tests must pass

**What They Validate**:
- Wake-up protocol
- Version consistency
- Session metadata
- Capability compliance
- Public release completeness

**Run Tests**:
```bash
cd aget
python3 -m pytest tests/ -v
```

**Standard**: 100% pass rate required for release

---

### Beta Releases (Future)

**Not Currently Used**: AGET releases stable versions directly

**Future Consideration**:
- Beta releases for major versions (v3.0.0-beta.1)
- Early adopter testing
- Feedback collection before stable

**Announcement**: If beta releases introduced, will be clearly marked

---

## Release Notes

### Where to Find

**Primary**: GitHub Release page
- https://github.com/aget-framework/aget/releases/tag/vX.Y.Z

**Secondary**: CHANGELOG.md
- Shorter format (bullets)
- Historical archive

---

### What's Included

**Standard Release Notes** (major/minor):
- **Highlights**: 3-5 key features/changes
- **Why It Matters**: User benefit, problem solved
- **Learnings Documented**: L-series references
- **Tests**: Pass rate (e.g., "80 passing, 100%")
- **Full Details**: Link to delta spec

**Patch Release Notes**:
- **Fixed**: Bug fixes (brief)
- **Link**: CHANGELOG.md for details

---

### Delta Specifications

**Location**: `aget/specs/deltas/AGET_DELTA_vX.Y.md`

**Content**: Technical specification of changes
- Requirements added/modified/removed
- Components added/modified/removed
- Capability changes
- Migration guide (if breaking)
- Traceability matrix

**Audience**: Framework developers, template authors, technical users

---

## Known Gaps (Historical)

**Transparency**: Framework acknowledges historical release inconsistencies

### Gap Summary

| Version | Status | Note |
|---------|--------|------|
| v2.6.0 | Not released | Documented in migration history only |
| v2.9.0 | Partial (4/7 repos) | Only advisor-family templates |
| v2.10.0 | Retroactive | Created 2025-12-24 (work done 2025-12-13) |

**Root Cause**: Private→public transition focused on content visibility without public release process.

**Resolution**: v2.11.0 established public framework governance (R-PUB-001 requirements, post-release validation, organization homepage updates).

**Commitment**: v2.11.0+ have complete releases guaranteed.

**Details**: [VERSION_HISTORY.md](VERSION_HISTORY.md)

---

## How to Request Features for Upcoming Releases

### Filing Enhancement Requests

1. **Check Existing**: Search issues for duplicates
   - https://github.com/aget-framework/aget/issues

2. **File Issue**:
   - Use "enhancement" label
   - Title: Clear, concise feature description
   - Body: Use case, benefit, impact
   - Examples: If applicable

3. **Discuss**: Community/maintainers may ask questions

4. **Prioritization**: Maintainers evaluate and add to milestone

### What Happens Next

**Accepted**:
- Added to milestone (e.g., "v2.12.0")
- Issue status: `planned`
- Timeline: When milestone scheduled

**Under Consideration**:
- Issue status: `needs discussion`
- May require more info or community feedback

**Declined**:
- Issue status: `wontfix`
- Explanation provided
- Alternative suggested (if applicable)

---

## Release Support

### Support Window

**Latest Release**: Full support (bug fixes, patches)

**Previous Minor** (vX.Y-1.Z): Security fixes only

**Older Releases**: No active support (upgrade recommended)

**Example**:
- v2.11.x: Full support
- v2.10.x: Security fixes
- v2.9.x and earlier: No support

---

### Upgrade Path

**Recommended**: Stay within 1-2 versions of latest

**Upgrading**: See [UPGRADING.md](UPGRADING.md) for procedures

**Rollback**: Supported (git checkout vOLD)

---

## Contributing to Releases

### How to Contribute

**Code Contributions**:
- Fork repository
- Create feature branch
- Write tests
- Submit pull request
- See CONTRIBUTING.md (future doc)

**Bug Reports**:
- File issue with "bug" label
- Include reproduction steps
- Provide version info

**Documentation**:
- Typo fixes welcome (PR)
- Missing docs (file issue)

---

## Related Documents

- **VERSIONING.md**: How versions work
- **VERSION_HISTORY.md**: Complete timeline
- **CHANGELOG.md**: What changed per version
- **UPGRADING.md**: Migration procedures
- **COMMUNICATION_STANDARDS.md**: Announcement templates

---

*RELEASES.md - Understanding AGET Framework releases*
*Created: 2025-12-24 | Version: 1.0*
