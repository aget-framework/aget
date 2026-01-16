# VALIDATION_REPORT: Claude Code v2.1.9

**Date**: 2026-01-16
**Tester**: private-aget-framework-AGET (automated + session validation)
**CLI**: Claude Code
**CLI Version**: 2.1.9
**Environment**: macOS Darwin 24.6.0, Python 3.9.6
**Status**: BASELINE ESTABLISHED

---

## Executive Summary

Claude Code v2.1.9 is validated as the **baseline reference implementation** for AGET CLI independence testing. All 24 tests pass. This CLI is the primary development target and serves as the known-good reference against which other CLIs are compared.

---

## Test Results Summary

| Category | Tests | Pass | Fail | Skip |
|----------|-------|------|------|------|
| TC-000: CLI Availability | 2 | 2 | 0 | 0 |
| TC-001: Settings Read | 3 | 3 | 0 | 0 |
| TC-002: Wake Protocol | 3 | 3 | 0 | 0 |
| TC-003: Wind Protocol | 3 | 3 | 0 | 0 |
| TC-004: Script Execution | 5 | 5 | 0 | 0 |
| TC-005: L-doc Creation | 3 | 3 | 0 | 0 |
| TC-006: File Operations | 5 | 5 | 0 | 0 |
| **TOTAL** | **24** | **24** | **0** | **0** |

**Result**: 100% PASS

---

## Detailed Test Results

### TC-000: CLI Availability

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-000-01 | Claude Code CLI is installed | PASS | Version: 2.1.9 |
| TC-000-02 | Version meets minimum (2.0.0) | PASS | 2.1.9 >= 2.0.0 |

### TC-001: Settings Read

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-001-01 | AGENTS.md file is recognized | PASS | File structure correct |
| TC-001-02 | @aget-version tag is parseable | PASS | 3.4.0 parsed |
| TC-001-03 | North Star section present | PASS | Section found |

**Session Validation**: Claude Code reads AGENTS.md (via CLAUDE.md symlink) at session start. This is evidenced by the agent following instructions from the file, including wake-up protocol execution.

### TC-002: Wake Protocol

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-002-01 | wake_up.py script exists | PASS | Script present |
| TC-002-02 | wake_up.py is valid Python | PASS | Compiles without error |
| TC-002-03 | wake_up.py executes correctly | PASS | Output contains "Ready" |

**Session Validation**: Wake protocol executed successfully at session start. Agent displayed formatted session info and reported "Ready."

### TC-003: Wind Down Protocol

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-003-01 | wind_down.py script exists | PASS | Script present |
| TC-003-02 | wind_down.py is valid Python | PASS | Compiles without error |
| TC-003-03 | wind_down.py executes correctly | PASS | No errors |

**Note**: Full wind-down protocol tested in normal session operation.

### TC-004: Script Execution

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-004-01 | .aget/patterns/ directory exists | PASS | Directory present |
| TC-004-02 | Session pattern scripts exist | PASS | wake_up.py, wind_down.py |
| TC-004-03 | Python3 is available | PASS | Python 3.9.6 |
| TC-004-04 | Scripts can read JSON | PASS | identity.json readable |
| TC-004-05 | Script output is captured | PASS | Output contains expected patterns |

**Session Validation**: Claude Code executes Python scripts via `python3` command. Script output is captured and displayed to user.

### TC-005: L-doc Creation

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-005-01 | evolution/ directory creatable | PASS | mkdir works |
| TC-005-02 | L-doc format valid markdown | PASS | Write + read successful |
| TC-005-03 | L-doc naming follows convention | PASS | L###_description.md pattern |

**Session Validation**: L-docs created during this session (will create L532 for gate announcement pattern).

### TC-006: File Operations

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-006-01 | Files can be read | PASS | Read tool functional |
| TC-006-02 | Files can be written | PASS | Write tool functional |
| TC-006-03 | Files can be appended | PASS | Append operation works |
| TC-006-04 | Files in subdirectories | PASS | Nested paths work |
| TC-006-05 | JSON roundtrip | PASS | Read/write preserves data |

**Session Validation**: All file operations performed during this session (reading AGENTS.md, writing PROJECT_PLAN, creating test files) completed successfully.

---

## CLI-Specific Observations

### Strengths

| Feature | Observation |
|---------|-------------|
| Settings file | CLAUDE.md (symlink to AGENTS.md) read automatically |
| Context window | 200k tokens, handles large AGENTS.md files |
| Tool execution | Bash, Read, Write, Edit tools work reliably |
| Python execution | `python3` scripts execute with captured output |
| Permission model | Per-operation approval, predictable |

### Limitations

| Feature | Observation | Workaround |
|---------|-------------|------------|
| Interactive scripts | Scripts requiring stdin not supported | Use non-interactive mode |
| Long-running processes | May timeout on slow scripts | Add timeout parameter |

### Version-Specific Notes

| Version | Note |
|---------|------|
| 2.1.9 | Current validated version |
| 2.0.0 | Minimum supported (AGET v3.4 requirement) |

---

## Gaps Identified

**None.** Claude Code is the baseline implementation. No gaps by definition—other CLIs are compared against this.

---

## Manual Validation Checklist

In addition to automated tests, the following were validated during live session:

- [x] Agent wakes up with formatted output
- [x] Agent follows instructions from AGENTS.md
- [x] Agent can execute Python scripts
- [x] Agent can read/write/edit files
- [x] Agent can create L-docs
- [x] Agent tracks todos correctly
- [x] Agent follows gated execution protocol

---

## Conclusion

**Support Level**: BASELINE (Certified)

Claude Code v2.1.9 is fully validated as the baseline reference for AGET CLI independence testing. All 24 automated tests pass, and session validation confirms full operational capability.

This validation establishes the benchmark against which Codex CLI and Gemini CLI will be compared in Gates 1.2 and 1.3.

---

## Evidence

### Test Run Output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 24 items

tests/cli_verification/test_claude_code.py .......................... [100%]

============================== 24 passed in 1.36s ==============================
```

### CLI Version Verification

```
$ claude --version
2.1.9 (Claude Code)
```

---

*VALIDATION_REPORT_claude_code_v2.1.9.md*
*Generated: 2026-01-16*
*Tester: private-aget-framework-AGET*
