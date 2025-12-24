# AGET Framework Communication Standards

**Audience**: Contributors, community members, framework maintainers

**Purpose**: Define expectations for version announcements, issue responses, PR reviews, and community engagement

**Status**: Active (v1.0, 2025-12-24)

---

## Overview

Clear, consistent communication builds trust and enables collaboration. This document establishes standards for how AGET Framework communicates with its community.

**Principles**:
- **Transparency**: Acknowledge gaps, don't hide them
- **Timeliness**: Respond within SLAs, communicate delays
- **Clarity**: Use plain language, avoid jargon where possible
- **Respect**: Every contribution deserves acknowledgment

---

## Version Announcements

### When to Announce

| Release Type | Announcement Required | Channel |
|--------------|----------------------|---------|
| **Major** (vX.0.0) | Yes (comprehensive) | GitHub Release + org homepage + (future: blog/social) |
| **Minor** (vX.Y.0) | Yes (standard) | GitHub Release + org homepage |
| **Patch** (vX.Y.Z) | Optional | GitHub Release (minimal notes acceptable) |

### Announcement Template (Major/Minor)

```markdown
# AGET Framework vX.Y.Z Released

**Release Date**: YYYY-MM-DD

## What's New

[3-5 key highlights, user-benefit focused]

- **Feature/Enhancement**: Brief description (why it matters)
- **Feature/Enhancement**: Brief description (impact)
- **Improvement**: What got better

## Why This Matters

[1-2 paragraphs explaining user benefit, problem solved, or capability unlocked]

## How to Upgrade

[If breaking changes:]
- Read migration guide: [link]
- Update version.json: `"aget_version": "X.Y.Z"`
- Run tests: `python3 -m pytest tests/`

[If non-breaking:]
- Update version.json: `"aget_version": "X.Y.Z"`
- No migration needed

## Learn More

- Full changelog: [CHANGELOG.md link]
- Delta specification: [link to aget/specs/deltas/AGET_DELTA_vX.Y.md]
- Learnings documented: [List L-doc IDs, e.g., L353-L357]

## Thank You

[If applicable] This release includes contributions from: [names/handles]

---

Questions? File an issue: https://github.com/aget-framework/aget/issues
```

### Announcement Template (Patch)

```markdown
# AGET Framework vX.Y.Z (Patch)

**Release Date**: YYYY-MM-DD

## Fixed

- Bug fix description
- Bug fix description

## Changelog

Full details: [CHANGELOG.md link]

---

Upgrade: Update `"aget_version": "X.Y.Z"` in your version.json
```

---

## Changelog Format

### Structure

Location: `aget/CHANGELOG.md`

Format: Keep a Changelog (https://keepachangelog.com/)

```markdown
# Changelog

All notable changes to AGET Framework.

## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature (user-facing impact)
- New capability (what it enables)

### Changed
- Enhancement to existing feature (what improved)
- Behavior change (what's different)

### Deprecated
- Feature being phased out (timeline, alternative)

### Removed
- Feature removed (migration path)

### Fixed
- Bug fix (what was broken, now works)
- Issue resolution (GitHub issue reference)

### Security
- Vulnerability fix (CVE if applicable, impact)

## [X.Y.Z-1] - YYYY-MM-DD
...
```

### User-Facing vs Developer-Facing

**DO Include** (user impact):
- New features users can access
- Breaking changes requiring migration
- Bug fixes users experienced
- Deprecated features users should know about

**DON'T Include** (internal changes):
- Refactoring (unless performance impact)
- Internal code organization
- Developer-only tooling
- Test infrastructure (unless affects users)

**Example**:
```markdown
### Added
- Configurable wake-up output (7 customizable sections) ← YES (user feature)

### Changed
- Refactored version_consistency.py for maintainability ← NO (internal)
```

---

## Migration Guide Structure

### When Required

Breaking changes (major version or incompatible minor) require migration guide.

### Location

- Short guide: CHANGELOG.md "Changed" section
- Detailed guide: `docs/migrations/vX.Y.Z.md`

### Template

```markdown
# Migration Guide: vOLD → vX.Y.Z

**Breaking Changes**: [Count] breaking changes

**Estimated Time**: [10 min | 30 min | 1 hour | varies]

---

## Breaking Change 1: [Name]

**What Changed**: [Old behavior vs new behavior]

**Why**: [Rationale for breaking change]

**Impact**: [Who is affected, what breaks]

**Migration**:
1. Step 1 (specific action)
2. Step 2 (specific action)
3. Verification: [How to confirm migration successful]

**Example**:
```[before/after code or configuration]```

---

## Breaking Change 2: [Name]
...

---

## Non-Breaking Enhancements

[Optional features that don't require migration]

---

## Rollback

If migration fails:
```bash
# Revert version.json
git checkout vOLD .aget/version.json

# Verify
python3 .aget/patterns/session/wake_up.py
```

---

## Support

Issues with migration? File issue: [link]
```

---

## Issue Response Standards

### SLA (Service Level Agreement)

| Issue Type | Response Time | Resolution Time |
|------------|---------------|-----------------|
| **Security** | 24 hours | 1 week (high), 1 month (medium) |
| **Bug** | 1 week | Varies (severity-dependent) |
| **Feature Request** | 2 weeks | Varies (roadmap-dependent) |
| **Question/Support** | 1 week | Best effort |
| **Documentation** | 2 weeks | 1 month |

**Response** = Acknowledgment, not resolution. Sets expectations on timeline.

### Response Template

```markdown
Thank you for filing this issue!

**Triaged**: [Bug | Feature Request | Question | Documentation]

**Priority**: [High | Medium | Low]

**Timeline**: [Expected response time]

[If bug:] Can you provide additional details: [specific questions]

[If feature:] This aligns with [roadmap area]. We'll consider for [version].

[If question:] [Answer or point to documentation]

We'll update this issue as we make progress.
```

### Issue Labels

Standard labels:

| Label | Use Case |
|-------|----------|
| `bug` | Something broken |
| `enhancement` | New feature request |
| `documentation` | Docs improvement |
| `question` | Support request |
| `good first issue` | Beginner-friendly |
| `help wanted` | Community contribution welcome |
| `wontfix` | Not planned, with explanation |
| `duplicate` | Links to original issue |

---

## Pull Request Review Standards

### Review SLA

| PR Type | Review Time | Merge Time |
|---------|-------------|------------|
| **Security/Hotfix** | 48 hours | 1 week |
| **Bug Fix** | 1 week | 2 weeks |
| **Feature** | 2 weeks | Varies (complexity) |
| **Documentation** | 1 week | 2 weeks |

### Review Checklist

Before approving PR:

- [ ] Code quality: Readable, maintainable
- [ ] Tests: Coverage for new code, all tests pass
- [ ] Documentation: Updated if behavior changed
- [ ] Breaking changes: Flagged, migration guide included
- [ ] Commit messages: Clear, reference issues
- [ ] CHANGELOG: Updated (if user-facing)

### Feedback Template

```markdown
Thanks for the contribution!

**Review Status**: [Approved | Changes Requested | Needs Discussion]

**Feedback**:
1. [Specific issue with code/approach]
2. [Suggestion for improvement]

**Questions**:
1. [Clarification needed]

**Next Steps**:
- [Action for contributor]
- [Action for maintainer]

We appreciate your work on this!
```

---

## Community Engagement Patterns

### Welcoming Contributors

First-time contributor response:

```markdown
Welcome to AGET Framework! 🎉

Thank you for your first contribution. We're excited to have you in the community.

[Provide specific feedback on their PR/issue]

If you have questions about the contribution process, see [CONTRIBUTING.md link].

Looking forward to collaborating!
```

### Acknowledging Contributions

In release notes:

```markdown
## Contributors

This release includes contributions from:
- @username (feature description)
- @username (bug fix)

Thank you for making AGET better!
```

In commit messages:

```
feat: Add configurable wake-up output

Co-authored-by: Contributor Name <email@example.com>
```

---

## Governance Communication

### Decision Announcements

When framework makes significant decision:

```markdown
# Decision: [Topic]

**Date**: YYYY-MM-DD

**Context**: [Why this decision needed]

**Options Considered**:
1. Option A: [pros/cons]
2. Option B: [pros/cons]

**Decision**: [Chosen option]

**Rationale**: [Why this option]

**Impact**: [Who/what affected]

**Timeline**: [When effective]

**Feedback**: [How community can provide input, if applicable]
```

### Deprecation Notices

Minimum 1 minor version warning before removal:

```markdown
## Deprecation Notice

**Feature**: [What's being deprecated]

**Deprecated in**: vX.Y.Z (YYYY-MM-DD)

**Removal scheduled**: vX+1.0.0 (estimated YYYY-MM)

**Reason**: [Why deprecating]

**Migration**: [Alternative feature/approach]

**Support**: [Where to get help]
```

---

## Transparency Standards

### Acknowledging Gaps

When gaps discovered (like VERSION_HISTORY gaps):

```markdown
## Known Issue: [Description]

**Discovered**: YYYY-MM-DD

**Scope**: [What's affected]

**Root Cause**: [Why it happened]

**Impact**: [Who's affected, severity]

**Resolution**:
- [Immediate action taken]
- [Preventive measures for future]

**Timeline**: [When fully resolved]

We acknowledge this transparently and are committed to preventing recurrence.
```

### Status Updates

For long-running issues/features:

```markdown
## Status Update: [Issue/Feature]

**Date**: YYYY-MM-DD

**Progress**: [What's been done]

**Current Status**: [Where we are]

**Next Steps**: [What's happening next]

**Timeline**: [Revised estimate if changed]

[If blocked:] **Blocker**: [What's preventing progress]
```

---

## Documentation Standards

### Tone and Voice

- **Active voice**: "The system creates..." not "The system is created..."
- **Present tense**: "The agent runs..." not "The agent will run..."
- **Direct address**: "You can configure..." not "One can configure..."
- **Plain language**: Avoid jargon, explain abbreviations on first use

### Example Quality

Good example:
```markdown
Update version to v2.11.0:

```json
{
  "aget_version": "2.11.0"
}
```
```

Bad example:
```markdown
Update version.

[No example provided, no context]
```

### Documentation Updates

When releasing:

- [ ] README reflects current version
- [ ] CHANGELOG has version entry
- [ ] VERSION_HISTORY updated (if version timeline doc exists)
- [ ] Migration guides included (if breaking)
- [ ] API docs updated (if API changed)

---

## Related Documents

- **R-PUB-001**: Public Release Completeness (specifications)
- **VERSION_HISTORY.md**: Complete version timeline
- **CONTRIBUTING.md**: How to contribute (future)
- **CODE_OF_CONDUCT.md**: Community behavior (future)

---

*COMMUNICATION_STANDARDS.md*
*Defines community communication expectations for AGET Framework*
*Created: 2025-12-24 | Version: 1.0*
