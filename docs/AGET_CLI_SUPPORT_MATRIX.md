# AGET CLI Support Matrix

**Version**: 1.0.0
**Date**: 2026-01-16
**Status**: ACTIVE
**Implements**: PROJECT_PLAN_cli_independence_validation_v1.0

---

## Overview

AGET is designed to be CLI-agnostic, working with multiple AI coding assistants. This document tracks validation status and support levels for each CLI.

**Validation Date**: 2026-01-16
**AGET Version**: 3.4.0

---

## Support Matrix

| CLI | Vendor | Version Tested | Support Level | Tests | Notes |
|-----|--------|----------------|---------------|-------|-------|
| **Claude Code** | Anthropic | 2.1.9 | **Baseline** | 24/24 | Primary development target |
| **Codex CLI** | OpenAI | 0.77.0 | Compatible | 26/26 | Native AGENTS.md support |
| **Gemini CLI** | Google | 0.23.0 | Compatible | 26/26 | Newest, expect changes |
| Cursor | Cursor | - | Experimental | - | Not validated |
| Aider | Open Source | - | Experimental | - | Not validated |
| Windsurf | - | - | Experimental | - | Not validated |

---

## Support Level Definitions

| Level | Meaning | Evidence Required |
|-------|---------|-------------------|
| **Baseline** | Reference implementation, fully validated | CI + live session + all tests pass |
| **Validated** | Manual validation, all tests pass | VALIDATION_REPORT + live session |
| **Compatible** | Infrastructure tests pass, live session pending | VALIDATION_REPORT (infra only) |
| **Experimental** | Untested, architecture should support | None |
| **Unsupported** | Known incompatibilities | GAP_ANALYSIS documenting blockers |

---

## Validated CLI Details

### Claude Code (Baseline)

| Attribute | Value |
|-----------|-------|
| Vendor | Anthropic |
| Version Tested | 2.1.9 |
| Minimum Supported | 2.0.0 |
| Settings File | CLAUDE.md (symlink to AGENTS.md) |
| Support Level | Baseline |
| Test Results | 24/24 pass |
| Live Session | Validated |

**Validation Report**: `docs/validation/VALIDATION_REPORT_claude_code_v2.1.9.md`

**Notes**:
- Primary development and testing target
- All AGET features designed against Claude Code first
- 200k token context window, handles large AGENTS.md
- Full tool support (Read, Write, Edit, Bash)

---

### Codex CLI (Compatible)

| Attribute | Value |
|-----------|-------|
| Vendor | OpenAI |
| Version Tested | 0.77.0 |
| Minimum Supported | 0.70.0 |
| Settings File | AGENTS.md (native) |
| Support Level | Compatible |
| Test Results | 26/26 pass |
| Live Session | Pending |

**Validation Report**: `docs/validation/VALIDATION_REPORT_codex_cli_v0.77.0.md`

**Notes**:
- Reads AGENTS.md natively (no symlink needed)
- `-y` flag available for automation
- Rapidly evolving (0.x series)
- Live session validation needed for full certification

**Known Gaps**:
- GAP-001: Live session validation pending

---

### Gemini CLI (Compatible)

| Attribute | Value |
|-----------|-------|
| Vendor | Google |
| Version Tested | 0.23.0 |
| Minimum Supported | 0.20.0 |
| Settings File | Unknown (needs validation) |
| Support Level | Compatible |
| Test Results | 26/26 pass |
| Live Session | Pending |

**Validation Report**: `docs/validation/VALIDATION_REPORT_gemini_cli_v0.23.0.md`

**Notes**:
- Newest of the three CLIs
- Uses `@filename` syntax for file references
- Settings file compatibility unknown
- Expect rapid changes in 0.x series

**Known Gaps**:
- GAP-001: Settings file compatibility unknown
- GAP-002: Live session validation pending
- GAP-003: File reference syntax differs

---

## Test Categories

All CLI validations cover these test categories:

| ID | Category | Description |
|----|----------|-------------|
| TC-001 | Settings Read | CLI reads AGENTS.md and follows instructions |
| TC-002 | Wake Protocol | wake_up.py executes correctly |
| TC-003 | Wind Protocol | wind_down.py executes correctly |
| TC-004 | Script Execution | .aget/patterns/ scripts work |
| TC-005 | L-doc Creation | Can create/update L-docs |
| TC-006 | File Operations | Read/write/edit per CLI tool model |

---

## Version Tracking

CLI agents evolve rapidly. AGET maintains version tracking in:
- `tests/cli_verification/cli_versions.json`

**Minimum Supported Versions**:

| CLI | Minimum Version | Rationale |
|-----|-----------------|-----------|
| Claude Code | 2.0.0 | Major version stability |
| Codex CLI | 0.70.0 | Feature completeness |
| Gemini CLI | 0.20.0 | Basic functionality |

**Re-validation Cadence**: Major version updates or quarterly review.

---

## Using AGET with Different CLIs

### Claude Code

```bash
# AGENTS.md is read via CLAUDE.md symlink
ln -s AGENTS.md CLAUDE.md  # If not already present

# Standard invocation
claude "wake up"
```

### Codex CLI

```bash
# AGENTS.md is read natively
codex "wake up"

# With automation flag
codex -y "wake up"
```

### Gemini CLI

```bash
# Settings file may need configuration
gemini "wake up"

# File references use @ syntax
gemini "read @AGENTS.md"
```

---

## Shell Orchestration

AGET provides shell integration for CLI-agnostic invocation (see L452):

```zsh
# ~/.aget/aget.zsh
export AGET_CLI=claude  # Default CLI

aget() {
    local dir="$1"; shift
    cd "$dir" || return 1
    $AGET_CLI "Wake up. $*"
}

# Override per-invocation
AGET_CLI=codex aget ~/my-agent "fix the bug"
```

---

## Contributing Validation

To validate a new CLI:

1. Create `test_<cli_name>.py` following existing patterns
2. Add CLI to `cli_versions.json`
3. Run validation tests
4. Generate VALIDATION_REPORT
5. Submit PR to update this matrix

---

## References

- PROJECT_PLAN_cli_independence_validation_v1.0
- L452: Shell Orchestration Pattern
- CLI_SETTINGS_STANDARD.md
- AGET_FRAMEWORK_SPEC.md

---

*AGET CLI Support Matrix - Prove before you claim*
