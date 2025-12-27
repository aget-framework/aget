# AGET Python Script Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards
**Created**: 2025-12-26
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_PYTHON_SCRIPT_SPEC.md`

---

## Abstract

This specification defines conventions for Python scripts in the AGET framework. It establishes CLI interface standards, exit codes, output formats, and registry requirements to ensure consistency across validators, tools, and pattern scripts.

## Motivation

AGET v3.0.0-alpha.1 introduced 6 new validators without formal standards. Analysis revealed inconsistencies in:
- CLI flag conventions
- Exit code semantics
- Output formatting
- Discoverability (no central registry)

This specification addresses these gaps.

## Scope

**Applies to**:
- `aget/validation/*.py` - Validators
- `aget/tools/*.py` - Framework tools (future)
- `.aget/patterns/**/*.py` - Agent pattern scripts

**Does not apply to**:
- `tests/**/*.py` - Test files (follow pytest conventions)
- `__init__.py` - Package markers

---

## Requirements

### R-SCRIPT-001: CLI Interface

All executable scripts SHALL support standard CLI flags.

| ID | Requirement | Priority |
|----|-------------|----------|
| R-SCRIPT-001-01 | Script SHALL support `--help` or `-h` flag | MUST |
| R-SCRIPT-001-02 | Script SHALL support `--version` flag | SHOULD |
| R-SCRIPT-001-03 | Script SHALL support `--quiet` or `-q` flag for reduced output | SHOULD |
| R-SCRIPT-001-04 | Script MAY support `--verbose` or `-v` flag for detailed output | MAY |
| R-SCRIPT-001-05 | Script MAY support `--log <path>` for persistent logging | MAY |
| R-SCRIPT-001-06 | Script SHALL use `argparse` for argument parsing | MUST |

**Example**:
```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Validate AGET template manifests'
    )
    parser.add_argument('paths', nargs='*', help='Paths to validate')
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--log', help='Log output to file')

    args = parser.parse_args()
```

### R-SCRIPT-002: Exit Codes

Scripts SHALL use consistent exit codes.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-002-01 | Exit code 0: Success (all validations passed, operation complete) |
| R-SCRIPT-002-02 | Exit code 1: Failure (validations failed, operation error) |
| R-SCRIPT-002-03 | Exit code 2: Usage error (invalid arguments, file not found) |

**Example**:
```python
import sys

def main():
    if not args.paths:
        parser.print_help()
        return 2  # Usage error

    if validation_failed:
        return 1  # Failure

    return 0  # Success

if __name__ == '__main__':
    sys.exit(main())
```

### R-SCRIPT-003: Output Format

Scripts SHALL follow output formatting conventions.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-003-01 | Success indicator: `✅` prefix |
| R-SCRIPT-003-02 | Failure indicator: `❌` prefix |
| R-SCRIPT-003-03 | Warning indicator: `⚠️` prefix |
| R-SCRIPT-003-04 | Summary line format: `{symbol} {passed}/{total} {description}` |
| R-SCRIPT-003-05 | Error details indented with 2 spaces |
| R-SCRIPT-003-06 | Quiet mode (`-q`) shows only errors and summary |

**Example output**:
```
✅ manifest.yaml - PASS
❌ config.yaml - FAIL
  ❌ ERROR: Missing required field: version
  ⚠️  WARN: Deprecated field: legacy_mode

✅ 1/2 files valid
```

### R-SCRIPT-004: Docstring

Scripts SHALL include module docstring with usage information.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-004-01 | Module docstring SHALL describe purpose |
| R-SCRIPT-004-02 | Module docstring SHALL include Usage section |
| R-SCRIPT-004-03 | Module docstring SHALL document exit codes |
| R-SCRIPT-004-04 | Module docstring MAY reference related specs |

**Example**:
```python
#!/usr/bin/env python3
"""
Validate AGET Template Manifests

Validates manifest.yaml files against the TemplateManifest schema.

Usage:
    python3 validate_template_manifest.py <path>
    python3 validate_template_manifest.py --dir /path/to/agent

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File/path errors

See: specs/COMPOSITION_SPEC_v1.0.md
"""
```

### R-SCRIPT-005: File Naming

Scripts SHALL follow naming conventions.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-005-01 | Validators: `validate_{target}.py` |
| R-SCRIPT-005-02 | Tools: `{verb}_{noun}.py` (e.g., `check_vocabulary.py`) |
| R-SCRIPT-005-03 | Pattern scripts: `{action}.py` (e.g., `wake_up.py`) |
| R-SCRIPT-005-04 | All names use snake_case |

### R-SCRIPT-006: Registry Entry

Scripts SHALL be registered in SCRIPT_REGISTRY.yaml.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-006-01 | Each script SHALL have registry entry |
| R-SCRIPT-006-02 | Entry SHALL include: path, description, category |
| R-SCRIPT-006-03 | Entry SHOULD include: version, author, created |
| R-SCRIPT-006-04 | Unregistered scripts generate validator warning |

**Registry entry format**:
```yaml
scripts:
  - path: validation/validate_template_manifest.py
    description: Validates manifest.yaml against TemplateManifest schema
    category: validator
    version: 1.0.0
    author: private-aget-framework-AGET
    created: 2025-12-20
    flags:
      - --help
      - --quiet
      - --dir
    exit_codes: [0, 1, 2]
```

### R-SCRIPT-007: Shebang and Encoding

Scripts SHALL include proper header.

| ID | Requirement |
|----|-------------|
| R-SCRIPT-007-01 | First line: `#!/usr/bin/env python3` |
| R-SCRIPT-007-02 | Encoding declaration NOT required (UTF-8 default in Python 3) |

---

## Script Categories

| Category | Location | Purpose | Examples |
|----------|----------|---------|----------|
| validator | `validation/` | Validate artifacts | validate_template_manifest.py |
| tool | `tools/` | Framework utilities | check_vocabulary.py |
| test | `tests/` | pytest test files | test_capability_contracts.py |
| pattern | `.aget/patterns/` | Agent operations | wake_up.py, version_bump.py |

---

## Compliance Levels

### Level 1: Minimal (MUST)

- `--help` flag works
- Exit codes 0/1/2 used correctly
- Module docstring present

### Level 2: Standard (SHOULD)

- `--version` flag
- `--quiet` flag
- Output format follows R-SCRIPT-003
- Registry entry exists

### Level 3: Full (MAY)

- `--log` flag for persistent logging
- `--verbose` flag for detailed output
- JSON output option (`--json`)

---

## Migration

Existing scripts should be updated incrementally:

1. **Immediate**: Add to SCRIPT_REGISTRY.yaml
2. **Alpha.2**: Add `--version` flag
3. **Alpha.3**: Add `--log` flag (optional)

---

## Validation

```bash
# Validate script registry
python3 validation/validate_script_registry.py SCRIPT_REGISTRY.yaml

# Check individual script compliance (future)
python3 validation/validate_script_compliance.py validation/validate_template_manifest.py
```

---

## References

- L382: Gate Verification Test Gap (triggered standardization need)
- PATTERN_gate_verification_tests.md (uses script output patterns)
- PEP 8: Python Style Guide
- argparse documentation

---

## Graduation History

- **Source**: L382 (Gap Analysis during alpha.1 review)
- **Pattern**: N/A (novel specification)
- **Rationale**: Direct to spec - immediate need, no pattern precedent

---

*AGET Python Script Specification v1.0.0*
*Part of v3.0.0 Composition Architecture*
