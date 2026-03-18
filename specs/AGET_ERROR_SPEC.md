# AGET Error Specification

**Version**: 1.0.1
**Status**: Active
**Category**: Technical (Error Handling)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: aget-framework
**Location**: `aget/specs/AGET_ERROR_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.5
**Related Specs**: AGET_VALIDATION_SPEC, AGET_PYTHON_SCRIPT_SPEC

---

## Abstract

This specification defines error handling requirements for the AGET framework, including error codes, message formats, exit codes, and recovery patterns.

## Motivation

Error handling challenges observed in practice:

1. **Inconsistent exit codes**: Scripts used 0/1 without standard meanings
2. **Cryptic messages**: Errors didn't explain what to do
3. **Missing context**: Hard to trace error source
4. **No recovery guidance**: Users stuck after errors

## Scope

**Applies to**: All AGET validators, scripts, and tools.

**Defines**:
- Exit code taxonomy
- Error message format
- Logging requirements
- Recovery patterns

**Does not cover**:
- Validation logic (see AGET_VALIDATION_SPEC)
- Script structure (see AGET_PYTHON_SCRIPT_SPEC)

---

## Requirements

### CAP-ERR-001: Exit Code Taxonomy

**SHALL** requirements for exit codes:

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | All checks passed |
| 1 | Validation failure | Content failed validation |
| 2 | Invalid arguments | CLI usage error |
| 3 | File not found | Required file missing |
| 4 | Permission error | Cannot read/write |
| 5 | Configuration error | Invalid config |
| 10+ | Domain-specific | Reserved for validators |

**Python Implementation:**

```python
import sys

EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_INVALID_ARGS = 2
EXIT_FILE_NOT_FOUND = 3
EXIT_PERMISSION_ERROR = 4
EXIT_CONFIG_ERROR = 5

def main():
    if not args.path.exists():
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)
```

### CAP-ERR-002: Error Message Format

**SHALL** requirements for error messages:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-ERR-002-01 | Errors SHALL include what failed | Clarity |
| CAP-ERR-002-02 | Errors SHALL include why it failed | Understanding |
| CAP-ERR-002-03 | Errors SHOULD include how to fix | Actionability |
| CAP-ERR-002-04 | Errors SHALL go to stderr | Convention |

**Message Format:**

```
Error: {what_failed}
  Reason: {why_it_failed}
  Fix: {how_to_fix}
  Reference: {spec_or_doc_link}
```

**Example:**

```
Error: File naming violation in specs/myspec.md
  Reason: Expected AGET_*_SPEC.md pattern
  Fix: Rename to AGET_MYSPEC_SPEC.md
  Reference: AGET_FILE_NAMING_CONVENTIONS.md Category E
```

### CAP-ERR-003: Logging Requirements

**SHOULD** requirements for logging:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-ERR-003-01 | Scripts SHOULD support --verbose flag | Debugging |
| CAP-ERR-003-02 | Verbose output SHOULD show progress | Feedback |
| CAP-ERR-003-03 | Errors SHOULD include timestamp in verbose mode | Debugging |

**Verbose Output Pattern:**

```python
def log(message: str, verbose: bool = False):
    if verbose:
        print(f"[{datetime.now().isoformat()}] {message}")
```

### CAP-ERR-004: Recovery Patterns

**SHOULD** requirements for error recovery:

| ID | Pattern | Usage |
|----|---------|-------|
| CAP-ERR-004-01 | Fail fast on critical errors | Config, permissions |
| CAP-ERR-004-02 | Collect all validation errors | Show full report |
| CAP-ERR-004-03 | Provide fix suggestions | Actionable output |

**Collect-All Pattern:**

```python
violations = []
for file in files:
    if not is_valid(file):
        violations.append(f"{file}: {reason}")

if violations:
    print(f"Found {len(violations)} violations:")
    for v in violations:
        print(f"  - {v}")
    sys.exit(EXIT_VALIDATION_FAILED)
```

### CAP-ERR-005: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-ERR-005-01 | ubiquitous | The SYSTEM shall assign a unique exit code to each error category per CAP-ERR-001. |
| CAP-ERR-005-02 | event-driven | WHEN a validation script encounters an error, THEN the SYSTEM shall output a structured error message containing error code, description, and recovery suggestion. |
| CAP-ERR-005-03 | prohibited | The SYSTEM shall NOT use exit code 0 for operations that completed with warnings or partial failures. |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-ERR-001-* | Manual review | Manual |
| CAP-ERR-002-* | Manual review | Manual |
| CAP-ERR-003-* | Manual review | Manual |

---

## Examples

### Good Error Message

```
❌ Error: Version mismatch in template-advisor-aget
  File: .aget/version.json
  Expected: 3.1.0
  Found: 3.0.0
  Fix: Run `python3 scripts/version_bump.py --to 3.1.0`
  Reference: AGET_VERSIONING_CONVENTIONS.md
```

### Bad Error Message

```
❌ Bad: Error: validation failed
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-ERR-001 | CAP-ERR-001 | automated | Verify scripts use standard exit code taxonomy (0=success, 1=validation failure, 2=invalid args, 3=file not found, 4=permission, 5=config) |
| V-ERR-002 | CAP-ERR-002 | inspection | Verify error messages include what failed, why it failed, and how to fix |
| V-ERR-003 | CAP-ERR-002 | automated | Verify errors are written to stderr (not stdout) |
| V-ERR-004 | CAP-ERR-003 | automated | Verify scripts support --verbose flag for detailed progress output |
| V-ERR-005 | CAP-ERR-004 | inspection | Verify scripts use collect-all pattern for validation errors rather than fail-fast |
| V-ERR-006 | CAP-ERR-004 | automated | Verify validation scripts provide fix suggestions in error output |
| V-ERR-007 | CAP-ERR-005 | automated | Verify exit code 0 is not used for operations with warnings or partial failures |
| V-ERR-008 | CAP-ERR-005 | automated | Verify structured error messages contain error code, description, and recovery suggestion |

### Validation Commands

```bash
# Verify exit code taxonomy in Python scripts (V-ERR-001)
for script in scripts/*.py; do
  grep -q "sys.exit" "$script" && echo "PASS: $script uses sys.exit" || echo "SKIP: $script"
done

# Verify errors go to stderr (V-ERR-003)
grep -rn "file=sys.stderr" scripts/*.py && echo "PASS: stderr usage found" || echo "WARN: check stderr usage"

# Verify --verbose flag support (V-ERR-004)
for script in scripts/*.py; do
  grep -q "\-\-verbose\|verbose" "$script" && echo "PASS: $script supports verbose" || echo "INFO: $script no verbose"
done
```

---

## Changelog

### v1.0.1 (2026-03-17)

- Added CAP-ERR-005: EARS System-Level Requirements (L682 L0→L1 uplift)
- 3 requirements with SYSTEM subject, ubiquitous/event-driven/prohibited patterns

### v1.0.0 (2026-01-04)

- Initial specification
- Exit code taxonomy
- Error message format
- Recovery patterns

---

*AGET_ERROR_SPEC.md — Error handling standards for AGET framework*
