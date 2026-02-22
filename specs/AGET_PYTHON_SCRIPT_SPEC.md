# AGET Python Script Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Standards
**Format Version**: 1.2
**Created**: 2025-12-26
**Updated**: 2025-12-27
**Author**: aget-framework
**Location**: `aget/specs/AGET_PYTHON_SCRIPT_SPEC.md`
**Change Proposal**: CP-002

---

## Abstract

This specification defines conventions for Python scripts in the AGET framework. It establishes CLI_Interface standards, Exit_Codes, Output_Formats, and Registry_Requirements to ensure consistency across validators, tools, and pattern scripts.

## Motivation

AGET v3.0.0-alpha.1 introduced 6 new validators without formal standards. Analysis revealed inconsistencies in:
- CLI_Flag conventions
- Exit_Code semantics
- Output_Formatting
- Discoverability (no central registry)

This specification addresses these gaps with formal EARS requirements.

## Scope

**Applies to**:
- `aget/validation/*.py` - Validators
- `aget/tools/*.py` - Framework tools (future)
- `.aget/patterns/**/*.py` - Agent Pattern_Scripts

**Does NOT Apply to**:
- `tests/**/*.py` - Test files (follow pytest conventions)
- `__init__.py` - Package markers

---

## Vocabulary

Domain terms for the Python_Script specification:

```yaml
vocabulary:
  meta:
    domain: "python_script"
    version: "1.0.0"
    inherits: "aget_core"

  skills:  # D4: Primary domain (scripts are capabilities)
    Python_Script:
      skos:definition: "Executable Python file conforming to AGET standards"
      skos:narrower: ["Validator", "Tool", "Pattern_Script"]
    Validator:
      skos:definition: "Script that checks artifact compliance"
      aget:naming: "validate_{target}.py"
      aget:location: "validation/"
    Tool:
      skos:definition: "Framework utility script"
      aget:naming: "{verb}_{noun}.py"
      aget:location: "tools/"
    Pattern_Script:
      skos:definition: "Agent operational pattern implementation"
      aget:naming: "{action}.py"
      aget:location: ".aget/patterns/"
    CLI_Interface:
      skos:definition: "Command-line interface for script invocation"
      skos:narrower: ["CLI_Flag", "Argument_Parser"]
    CLI_Flag:
      skos:definition: "Command-line option for script behavior"
      skos:narrower: ["Help_Flag", "Version_Flag", "Quiet_Flag", "Verbose_Flag", "Log_Flag"]
    Exit_Code:
      skos:definition: "Numeric value indicating script completion status"
      skos:narrower: ["Exit_Success", "Exit_Failure", "Exit_Usage_Error"]
    Exit_Success:
      skos:definition: "Exit code 0 - operation completed successfully"
    Exit_Failure:
      skos:definition: "Exit code 1 - validation failed or operation error"
    Exit_Usage_Error:
      skos:definition: "Exit code 2 - invalid arguments or file not found"

  memory:  # D2: Stored artifacts
    SCRIPT_REGISTRY:
      skos:definition: "Central registry of all AGET scripts"
      aget:location: "SCRIPT_REGISTRY.yaml"
    Registry_Entry:
      skos:definition: "Script metadata in SCRIPT_REGISTRY"
      aget:fields: ["path", "description", "category", "version", "author", "created"]
    Module_Docstring:
      skos:definition: "Python docstring at module level with usage information"

  reasoning:  # D3: Decision patterns
    Output_Format:
      skos:definition: "Standardized format for script output"
      skos:narrower: ["Success_Indicator", "Failure_Indicator", "Warning_Indicator"]
    Success_Indicator:
      skos:definition: "Visual prefix for successful operations"
      aget:symbol: "✅"
    Failure_Indicator:
      skos:definition: "Visual prefix for failed operations"
      aget:symbol: "❌"
    Warning_Indicator:
      skos:definition: "Visual prefix for warnings"
      aget:symbol: "⚠️"
    Compliance_Level:
      skos:definition: "Degree of specification adherence"
      skos:narrower: ["Level_Minimal", "Level_Standard", "Level_Full"]
```

---

## Requirements

### CAP-SCRIPT-001: CLI Interface

The SYSTEM shall provide Standard_CLI_Interface.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-001-01 | ubiquitous | The SYSTEM shall support Help_Flag (`--help` or `-h`) |
| CAP-SCRIPT-001-02 | ubiquitous | The SYSTEM should support Version_Flag (`--version`) |
| CAP-SCRIPT-001-03 | ubiquitous | The SYSTEM should support Quiet_Flag (`--quiet` or `-q`) for reduced output |
| CAP-SCRIPT-001-04 | optional | WHERE Detailed_Output is needed, the SYSTEM may support Verbose_Flag (`--verbose` or `-v`) |
| CAP-SCRIPT-001-05 | optional | WHERE Persistent_Logging is needed, the SYSTEM may support Log_Flag (`--log <path>`) |
| CAP-SCRIPT-001-06 | ubiquitous | The SYSTEM shall use argparse for Argument_Parsing |

**Enforcement**: `validate_script_compliance.py`

#### CLI Interface Example

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

### CAP-SCRIPT-002: Exit Codes

The SYSTEM shall use consistent Exit_Codes.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-002-01 | event-driven | WHEN Script_Succeeds, the SYSTEM shall return Exit_Code 0 |
| CAP-SCRIPT-002-02 | event-driven | WHEN Validation_Fails OR Operation_Error occurs, the SYSTEM shall return Exit_Code 1 |
| CAP-SCRIPT-002-03 | event-driven | WHEN Invalid_Arguments OR File_Not_Found occurs, the SYSTEM shall return Exit_Code 2 |

**Enforcement**: Manual review, exit code tests

#### Exit Code Example

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

### CAP-SCRIPT-003: Output Format

The SYSTEM shall follow Output_Format conventions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-003-01 | event-driven | WHEN Success, the SYSTEM shall prefix output with Success_Indicator (✅) |
| CAP-SCRIPT-003-02 | event-driven | WHEN Failure, the SYSTEM shall prefix output with Failure_Indicator (❌) |
| CAP-SCRIPT-003-03 | event-driven | WHEN Warning, the SYSTEM shall prefix output with Warning_Indicator (⚠️) |
| CAP-SCRIPT-003-04 | ubiquitous | The SYSTEM shall format Summary_Line as `{symbol} {passed}/{total} {description}` |
| CAP-SCRIPT-003-05 | ubiquitous | The SYSTEM shall indent Error_Details with 2 spaces |
| CAP-SCRIPT-003-06 | state-driven | WHILE Quiet_Mode is active, the SYSTEM shall show only Errors and Summary |

**Enforcement**: Output format review

#### Output Example

```
✅ manifest.yaml - PASS
❌ config.yaml - FAIL
  ❌ ERROR: Missing required field: version
  ⚠️  WARN: Deprecated field: legacy_mode

✅ 1/2 files valid
```

### CAP-SCRIPT-004: Module Docstring

The SYSTEM shall include Module_Docstring with Usage_Information.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-004-01 | ubiquitous | The SYSTEM shall describe Script_Purpose in Module_Docstring |
| CAP-SCRIPT-004-02 | ubiquitous | The SYSTEM shall include Usage_Section in Module_Docstring |
| CAP-SCRIPT-004-03 | ubiquitous | The SYSTEM shall document Exit_Codes in Module_Docstring |
| CAP-SCRIPT-004-04 | optional | WHERE Related_Specs exist, the SYSTEM may reference them in Module_Docstring |

**Enforcement**: Docstring validation

#### Docstring Example

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

### CAP-SCRIPT-005: File Naming

The SYSTEM shall follow Naming_Conventions.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-005-01 | ubiquitous | The SYSTEM shall name Validators as `validate_{target}.py` |
| CAP-SCRIPT-005-02 | ubiquitous | The SYSTEM shall name Tools as `{verb}_{noun}.py` |
| CAP-SCRIPT-005-03 | ubiquitous | The SYSTEM shall name Pattern_Scripts as `{action}.py` |
| CAP-SCRIPT-005-04 | ubiquitous | The SYSTEM shall use snake_case for all Script_Names |

**Enforcement**: `validate_script_registry.py`

### CAP-SCRIPT-006: Registry Entry

The SYSTEM shall register Scripts in SCRIPT_REGISTRY.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-006-01 | ubiquitous | The SYSTEM shall have Registry_Entry for each Script |
| CAP-SCRIPT-006-02 | ubiquitous | The SYSTEM shall include path, description, category in Registry_Entry |
| CAP-SCRIPT-006-03 | ubiquitous | The SYSTEM should include version, author, created in Registry_Entry |
| CAP-SCRIPT-006-04 | conditional | IF Script is unregistered THEN the SYSTEM shall generate Validator_Warning |

**Enforcement**: `validate_script_registry.py --check-files`

#### Registry Entry Format

```yaml
scripts:
  - path: validation/validate_template_manifest.py
    description: Validates manifest.yaml against TemplateManifest schema
    category: validator
    version: 1.0.0
    author: aget-framework
    created: 2025-12-20
    flags:
      - --help
      - --quiet
      - --dir
    exit_codes: [0, 1, 2]
```

### CAP-SCRIPT-007: Shebang and Header

The SYSTEM shall include proper Script_Header.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SCRIPT-007-01 | ubiquitous | The SYSTEM shall include Shebang `#!/usr/bin/env python3` as first line |
| CAP-SCRIPT-007-02 | ubiquitous | The SYSTEM shall NOT require Encoding_Declaration (UTF-8 default in Python 3) |

**Enforcement**: Script header validation

---

## Script Categories

| Category | Location | Purpose | Examples |
|----------|----------|---------|----------|
| Validator | `validation/` | Validate artifacts | validate_template_manifest.py |
| Tool | `tools/` | Framework utilities | check_vocabulary.py |
| Test | `tests/` | pytest test files | test_capability_contracts.py |
| Pattern | `.aget/patterns/` | Agent operations | wake_up.py, version_bump.py |

---

## Compliance Levels

### Level_Minimal (MUST)

Required for all scripts:
- Help_Flag (`--help`) works
- Exit_Codes 0/1/2 used correctly
- Module_Docstring present

### Level_Standard (SHOULD)

Recommended for production scripts:
- Version_Flag (`--version`)
- Quiet_Flag (`--quiet`)
- Output_Format follows CAP-SCRIPT-003
- Registry_Entry exists

### Level_Full (MAY)

Optional enhanced compliance:
- Log_Flag for Persistent_Logging
- Verbose_Flag for Detailed_Output
- JSON_Output option (`--json`)

---

## Authority Model

```yaml
authority:
  applies_to: "framework_maintainers"

  governed_by:
    spec: "AGET_PYTHON_SCRIPT_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "create new Scripts following specification"
      - "register Scripts in SCRIPT_REGISTRY"
      - "update Script versions"
      - "add optional CLI_Flags"

    requires_approval:
      - action: "change Exit_Code semantics"
        approver: "framework-aget"
      - action: "add new Script_Category"
        approver: "framework-aget"

  validation_authority:
    - action: "validate_script_compliance.py"
      authority: "automated"
    - action: "validate_script_registry.py"
      authority: "automated"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-SCRIPT-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT omit Help_Flag from executable Script"
      rationale: "Help is mandatory for discoverability"

    - id: "INV-SCRIPT-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT use Exit_Codes outside 0/1/2 semantics"
      rationale: "Consistent exit codes enable automation"

    - id: "INV-SCRIPT-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT deploy unregistered Scripts to production"
      rationale: "Registry enables maintenance and discovery"

    - id: "INV-SCRIPT-004"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT omit Module_Docstring from Scripts"
      rationale: "Documentation is mandatory for maintainability"
```

---

## Structural Requirements

```yaml
structure:
  required_directories:
    - path: "validation/"
      purpose: "Validator scripts"
      naming: "validate_*.py"

    - path: ".aget/patterns/"
      purpose: "Pattern scripts"
      subdirectories:
        - "session/"
        - "release/"
        - "sync/"

  optional_directories:
    - path: "tools/"
      purpose: "Framework utility scripts"
      naming: "{verb}_{noun}.py"

  required_files:
    - path: "SCRIPT_REGISTRY.yaml"
      purpose: "Central script registry"
      schema: "script_registry_schema.yaml"

  script_structure:
    required_elements:
      - shebang: "#!/usr/bin/env python3"
      - module_docstring: "Purpose, Usage, Exit codes"
      - argparse: "CLI argument parsing"
      - main_function: "Entry point returning exit code"
```

---

## Validation

### Script Compliance Check

```bash
# Validate script registry
python3 validation/validate_script_registry.py SCRIPT_REGISTRY.yaml

# Check individual script compliance (future)
python3 validation/validate_script_compliance.py validation/validate_template_manifest.py

# Verify all scripts registered
python3 validation/validate_script_registry.py SCRIPT_REGISTRY.yaml --check-files
```

### EARS Pattern Verification

```bash
# Count EARS patterns in this spec
grep -cE "WHEN |WHILE |WHERE |IF .* THEN|The SYSTEM shall" aget/specs/AGET_PYTHON_SCRIPT_SPEC.md
# Expected: > 25
```

---

## Migration

Existing scripts should be updated incrementally:

1. **Immediate**: Add to SCRIPT_REGISTRY.yaml
2. **Alpha.2**: Add `--version` flag
3. **Alpha.3**: Add `--log` flag (optional)

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Cybernetics"
  secondary:
    - "Extended Mind (tools as extensions)"
  rationale: >
    Scripts extend agent capability (Extended Mind) through
    executable tools. Consistent interfaces provide requisite
    variety (Cybernetics) for automation and integration.
  reference: "L331_theoretical_foundations_agency.md"
```

---

## References

- L382: Gate Verification Test Gap (triggered standardization need)
- PATTERN_gate_verification_tests.md (uses script output patterns)
- PEP 8: Python Style Guide
- argparse documentation
- AGET_SPEC_FORMAT_v1.2: Specification format

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L382"]
  pattern_origin: "N/A (novel specification)"
  rationale: "Direct to spec - immediate need, no pattern precedent"

history:
  - version: "1.0.0"
    date: "2025-12-26"
    changes: "Initial release (v3.0.0-alpha.1)"
  - version: "1.1.0"
    date: "2025-12-27"
    changes: "EARS/SKOS reformat (v3.0.0-alpha.5)"
```

---

*AGET Python Script Specification v1.1.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*Part of v3.0.0 Composition Architecture*
*"Consistent scripts enable consistent automation."*
