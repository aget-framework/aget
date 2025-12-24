# AGET Framework Versioning

**Audience**: Framework users, template developers, contributors

**Purpose**: Explain how AGET uses semantic versioning, where to find releases, and version compatibility

---

## Quick Reference

**Current Version**: See homepage badge at https://github.com/aget-framework

**All Releases**: https://github.com/aget-framework/aget/releases

**Version History**: [VERSION_HISTORY.md](VERSION_HISTORY.md) (complete timeline with gaps noted)

---

## Semantic Versioning

AGET Framework follows [Semantic Versioning 2.0.0](https://semver.org/):

### Version Format: MAJOR.MINOR.PATCH

**Example**: v2.11.0

- **MAJOR** = 2 (breaking changes)
- **MINOR** = 11 (new features, backwards compatible)
- **PATCH** = 0 (bug fixes, backwards compatible)

---

### What Each Increment Means

#### MAJOR Version (vX.0.0)

**When**: Breaking changes that require migration

**Examples**:
- Renamed configuration fields
- Removed deprecated features
- Changed contract test interfaces
- Incompatible AGENTS.md format changes

**Impact**: You MUST read migration guide and update your agents

**Frequency**: Rare (when ecosystem evolution requires)

**Recent**: v2.0.0 (2025-09-XX) - Framework architecture

---

#### MINOR Version (vX.Y.0)

**When**: New features or enhancements, backwards compatible

**Examples**:
- New patterns (Executive Advisor, Domain Specialist)
- Additional capabilities (configurable wake-up output)
- New specifications (R-PUB-001 Public Release Completeness)
- Framework enhancements (L352 traceability pattern)

**Impact**: You CAN upgrade without migration (but may want to adopt new features)

**Frequency**: Monthly (target cadence)

**Recent**: v2.11.0 (2025-12-24) - Memory Architecture + L352 Traceability

---

#### PATCH Version (vX.Y.Z)

**When**: Bug fixes only

**Examples**:
- Fixed broken links
- Corrected test failures
- Path resolution fixes
- Documentation typos

**Impact**: Safe to upgrade immediately (no migration)

**Frequency**: As needed (typically weekly during active development)

**Recent**: v2.11.1 (example - not yet released)

---

## Finding the Right Version

### Latest Stable Release

**Where**: GitHub Releases page (https://github.com/aget-framework/aget/releases)

**Badge**: Organization homepage shows current version

[![Version](https://img.shields.io/badge/version-2.11.0-blue)](https://github.com/aget-framework/aget/releases/tag/v2.11.0)

**Recommendation**: Use latest stable for new projects

---

### Specific Version

**When You Might Need**:
- Reproducing historical behavior
- Compatibility with specific CLI tool version
- Rollback after failed upgrade

**How to Find**:
```bash
# List all releases
gh release list --repo aget-framework/aget

# Or visit releases page
open https://github.com/aget-framework/aget/releases
```

---

### Pre-Release / Beta Versions

**Format**: vX.Y.Z-beta.N or vX.Y.Z-rc.N

**When Used**: Testing new features before official release

**Stability**: Not production-ready, may have bugs

**How to Identify**: GitHub Release marked as "Pre-release"

**Recommendation**: Only use for testing/experimentation

---

## Version Compatibility

### Template Compatibility

All templates share the same MAJOR.MINOR version:

```
aget:                  v2.11.0
template-worker:       v2.11.0
template-advisor:      v2.11.0
template-consultant:   v2.11.0
template-developer:    v2.11.0
template-spec-engineer: v2.11.0
```

**Rule**: All templates at v2.11.x are compatible with each other

**Mixing Versions**:
- ✅ v2.11.0 + v2.11.1 = Compatible (same major.minor)
- ⚠️ v2.11.0 + v2.10.0 = May work, not guaranteed
- ❌ v2.11.0 + v1.9.0 = Incompatible (different major)

---

### CLI Tool Compatibility

AGET Framework aims for universal CLI compatibility:

| CLI Tool | Compatibility | Notes |
|----------|---------------|-------|
| **Claude Code** | ✅ Primary support | Tested with each release |
| **Cursor** | ✅ Compatible | AGENTS.md standard |
| **Aider** | ✅ Compatible | AGENTS.md standard |
| **Windsurf** | ✅ Compatible | AGENTS.md standard |
| **Others** | ⚠️ Depends | If supports AGENTS.md |

**Minimum Requirements**:
- CLI tool must support `.aget/` directory structure
- CLI tool must read `AGENTS.md` or `CLAUDE.md`
- CLI tool must support file-based configuration

---

## Checking Your Current Version

### In Your Agent

```bash
cat .aget/version.json | grep aget_version
# Output: "aget_version": "2.11.0"
```

### Via Wake-Up

```bash
# Wake up your agent (if supports wake-up protocol)
# Output should include:
# **Version**: v2.11.0 (2025-12-24)
```

### Via Contract Tests

```bash
python3 -m pytest tests/ -v -k "test_version"
```

---

## Upgrading Versions

See [UPGRADING.md](UPGRADING.md) for detailed upgrade procedures.

**General Process**:
1. Read [CHANGELOG.md](../CHANGELOG.md) for what changed
2. If major version: Read migration guide
3. Update `.aget/version.json`: `"aget_version": "X.Y.Z"`
4. Run contract tests: `python3 -m pytest tests/`
5. Verify wake-up: Agent displays new version

**Breaking Changes**: Always documented with migration steps

**Non-Breaking**: Update version.json, no migration needed

---

## Version History & Known Gaps

**Complete Timeline**: [VERSION_HISTORY.md](VERSION_HISTORY.md)

**Transparency Note**: Versions v2.5-v2.9 have inconsistent release coverage due to private→public transition. This is acknowledged, not hidden. v2.10.0+ have complete releases across all repositories.

**Gap Summary**:
- v2.6.0: Not released (documented in migration history only)
- v2.9.0: Partial (4/7 templates)
- v2.10.0: Retroactively released 2025-12-24 (work done 2025-12-13)
- v2.11.0+: Complete releases guaranteed (R-PUB-001 requirements)

---

## Release Cadence

**Target**:
- **Minor Releases**: Monthly
- **Patch Releases**: As needed (typically weekly during active dev)
- **Major Releases**: When breaking changes necessary (rare)

**Actual**: See [RELEASES.md](RELEASES.md) for release history and patterns

**Announcement**:
- Major/minor: GitHub Release + org homepage + (future: blog/social)
- Patch: GitHub Release only

---

## Version Pinning

### When to Pin

**Recommended**:
- Production deployments (stability)
- Compliance requirements (audit trail)
- Known-good configurations (reliability)

**Not Recommended**:
- Active development (miss features)
- Experimentation (miss improvements)

### How to Pin

In `.aget/version.json`:
```json
{
  "aget_version": "2.11.0",
  "pinned": true
}
```

**Note**: Pin field is informational only. You control upgrades.

---

## Version Nomenclature

### Tags vs Releases

**Git Tag**: Developer artifact (e.g., `v2.11.0`)
- Created with `git tag -a v2.11.0`
- Marks specific commit
- Accessible via `git checkout v2.11.0`

**GitHub Release**: User artifact
- Created via `gh release create v2.11.0`
- Includes release notes, download links
- Visible on https://github.com/aget-framework/aget/releases

**Both Required**: Per L358 (Tags ≠ Releases on GitHub)

---

### Version Prefix

**Standard**: v2.11.0 (with 'v' prefix)

**Where**:
- Git tags: `v2.11.0`
- GitHub Releases: `v2.11.0`
- Organization homepage: `version-2.11.0` (badge format)

**Where NOT**:
- version.json: `"aget_version": "2.11.0"` (no 'v')
- CHANGELOG.md: `## [2.11.0]` (no 'v')

---

## Support & Questions

**Questions about versions**:
- Check [VERSION_HISTORY.md](VERSION_HISTORY.md) first
- Check [CHANGELOG.md](../CHANGELOG.md) for changes
- File issue: https://github.com/aget-framework/aget/issues

**Upgrade problems**:
- See [UPGRADING.md](UPGRADING.md)
- Check delta spec: `aget/specs/deltas/AGET_DELTA_vX.Y.md`
- File issue with "upgrade" label

**Feature requests for future versions**:
- File issue with "enhancement" label
- Describe use case and benefit
- Link to related documentation if applicable

---

## Related Documents

- **VERSION_HISTORY.md**: Complete version timeline
- **CHANGELOG.md**: What changed in each version
- **UPGRADING.md**: How to migrate between versions
- **RELEASES.md**: Release process and patterns
- **COMMUNICATION_STANDARDS.md**: How versions are announced

---

*VERSIONING.md - Understanding AGET Framework versions*
*Created: 2025-12-24 | Version: 1.0*
