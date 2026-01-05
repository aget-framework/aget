# AGET Documentation Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Format (Documentation Standards)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_DOCUMENTATION_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.3
**Related Specs**: AGET_FILE_NAMING_CONVENTIONS, AGET_TEMPLATE_SPEC

---

## Abstract

This specification defines documentation requirements for the AGET framework, including README structure, CLI settings files (AGENTS.md, CLAUDE.md), inline documentation, and example requirements. It establishes standards for human-AI collaborative documentation.

## Motivation

Documentation challenges observed in practice:

1. **Inconsistent READMEs**: Template READMEs varied in structure and completeness
2. **CLI settings drift**: AGENTS.md and CLAUDE.md had no standard format
3. **Missing examples**: Specs without practical examples (L394)
4. **Documentation theater**: Docs that exist but don't help (similar to L433)

R-TPL-001 (README requirements) and L394 (Example Requirement) revealed these gaps.

## Scope

**Applies to**: All AGET repositories (aget/, templates, instances).

**Defines**:
- README requirements per repository type
- CLI settings file structure (AGENTS.md, CLAUDE.md)
- Inline documentation standards
- Example requirements for specs and patterns

**Does not cover**:
- File naming (see AGET_FILE_NAMING_CONVENTIONS)
- API reference generation tools
- Release documentation (see AGET_RELEASE_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "documentation"
    version: "1.0.0"
    inherits: "aget_core"

  document_types:
    README:
      skos:definition: "Primary entry point documentation for a repository"
      aget:location: "README.md"
      skos:related: ["CAP-DOC-001", "R-TPL-001"]

    CLI_Settings_File:
      skos:definition: "Configuration file read by AI coding assistants"
      aget:examples: ["AGENTS.md", "CLAUDE.md", ".cursorrules"]
      skos:related: ["CAP-DOC-002"]

    Inline_Documentation:
      skos:definition: "Documentation embedded within code (docstrings, comments)"
      skos:related: ["CAP-DOC-003"]

    Example_Documentation:
      skos:definition: "Practical examples demonstrating spec or pattern usage"
      skos:related: ["CAP-DOC-005", "L394"]

  audiences:
    Human_User:
      skos:definition: "Human developers reading documentation"
      aget:needs: ["Quick start", "Examples", "Troubleshooting"]

    AI_Assistant:
      skos:definition: "AI coding assistants parsing settings files"
      aget:needs: ["Context", "Constraints", "Patterns"]

    Framework_Developer:
      skos:definition: "Contributor extending AGET framework"
      aget:needs: ["Architecture", "Conventions", "API reference"]

  anti_patterns:
    Documentation_Theater:
      skos:definition: "Documentation that exists but doesn't help users"
      aget:anti_pattern: true
      skos:related: ["L433"]

    Outdated_Documentation:
      skos:definition: "Documentation not synced with actual behavior"
      aget:anti_pattern: true
```

---

## Requirements

### CAP-DOC-001: README Requirements

**SHALL** requirements for README.md files:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-001-01 | Every repo SHALL have README.md | Entry point |
| CAP-DOC-001-02 | README SHALL include project purpose | Understanding |
| CAP-DOC-001-03 | README SHALL include quickstart | Accessibility |
| CAP-DOC-001-04 | README SHALL include version badge | Currency |
| CAP-DOC-001-05 | README SHALL be kept current with releases | Accuracy |

**README Structure (by repo type):**

**Core (aget/):**

```markdown
# AGET Framework

Brief description of the framework.

## Overview
What AGET is and who it's for.

## Quick Start
Minimal steps to get started.

## Documentation
Links to key specs and guides.

## Contributing
How to contribute.

## License
Apache 2.0
```

**Template (template-*-aget/):**

```markdown
# Template: {Archetype} Agent

Brief description of the archetype.

## Purpose
What this archetype is designed for.

## Quick Start
How to instantiate from this template.

## Structure
Directory layout explanation.

## Configuration
Key configuration points.

## Testing
How to run tests.

## License
Apache 2.0
```

**Instance:**

```markdown
# {Agent Name}

Brief description of this specific agent.

## Purpose
What this agent does.

## Session Protocol
Wake up and wind down procedures.

## Key Directories
Important locations and their purposes.

## Verification
How to verify agent compliance.
```

### CAP-DOC-002: CLI Settings File Requirements

**SHALL** requirements for AI assistant settings files:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-002-01 | Templates SHALL have AGENTS.md | Cross-platform settings |
| CAP-DOC-002-02 | Instances MAY have CLAUDE.md | Claude-specific config |
| CAP-DOC-002-03 | Settings files SHALL include agent identity | Context |
| CAP-DOC-002-04 | Settings files SHALL include session protocol | Operational |
| CAP-DOC-002-05 | Settings files SHALL include key commands | Efficiency |

**AGENTS.md Structure:**

```markdown
# Agent Configuration

## North Star
{Purpose statement}

## Identity
{Name, type, domain}

## Session Protocol
### Wake Up
{Steps to initialize session}

### Wind Down
{Steps to close session}

## Key Commands
| Command | Purpose |
|---------|---------|
| `python3 scripts/wake_up.py` | Session start |
| `python3 -m pytest tests/` | Run tests |

## Directory Structure
{Key directories and their purposes}

## Verification
{How to verify agent health}
```

**CLAUDE.md Extensions:**

```markdown
# Claude-Specific Configuration

@aget-version: {version}

## Substantial Change Protocol
{Steps before significant changes}

## Authority Model
{What agent can do autonomously vs escalate}

## Inherited Knowledge
{References to precedent documents}
```

### CAP-DOC-003: Inline Documentation Requirements

**SHALL** requirements for code documentation:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-003-01 | Python modules SHALL have module docstring | Purpose |
| CAP-DOC-003-02 | Public functions SHALL have docstrings | API clarity |
| CAP-DOC-003-03 | Validators SHALL trace to requirements | Traceability |
| CAP-DOC-003-04 | Complex logic SHOULD have inline comments | Understanding |

**Docstring Format:**

```python
"""
Short description of the module/function.

Longer description if needed.

Implements: CAP-XXX-NNN
Traces to: {spec_name}

Args:
    param1: Description
    param2: Description

Returns:
    Description of return value

Raises:
    ExceptionType: When this happens

Example:
    >>> function_call(arg)
    expected_result
"""
```

### CAP-DOC-004: API Documentation Requirements

**SHOULD** requirements for API documentation:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-004-01 | Scripts SHOULD document CLI interface | Usability |
| CAP-DOC-004-02 | Validators SHOULD document exit codes | Integration |
| CAP-DOC-004-03 | JSON outputs SHOULD document schema | Interoperability |

**CLI Documentation Format:**

```python
"""
Script short description.

Usage:
    python3 script.py /path/to/target [--options]

Options:
    --verbose, -v    Enable verbose output
    --json           Output as JSON

Exit codes:
    0: Success
    1: Validation failed
    2: Invalid arguments

Example:
    python3 validate_naming.py /path/to/repo --verbose
"""
```

### CAP-DOC-005: Example Requirements

**SHALL** requirements for examples (L394):

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-005-01 | Specs SHALL include at least one example | Clarity |
| CAP-DOC-005-02 | Examples SHALL be copy-pastable | Usability |
| CAP-DOC-005-03 | Examples SHALL show both correct and incorrect patterns | Learning |
| CAP-DOC-005-04 | Complex patterns SHOULD have multiple examples | Coverage |

**Example Format:**

```markdown
## Examples

### Example 1: {Scenario}

{Context for this example}

```{language}
{Working code/config}
```

**Result:** {What happens}

### Anti-Pattern Example

```{language}
{Incorrect code/config}
```

**Problem:** {Why this is wrong}

**Fix:** {How to correct it}
```

### CAP-DOC-006: Documentation Currency

**SHALL** requirements for keeping documentation current:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-DOC-006-01 | Documentation SHALL be updated with code changes | Accuracy |
| CAP-DOC-006-02 | Version numbers in docs SHALL match releases | Consistency |
| CAP-DOC-006-03 | Deprecated features SHALL be marked | User guidance |
| CAP-DOC-006-04 | Breaking changes SHALL update docs before release | User safety |

---

## Audience Matrix

| Document Type | Primary Audience | Secondary Audience |
|--------------|------------------|-------------------|
| README.md | Human User | AI Assistant |
| AGENTS.md | AI Assistant | Human User |
| CLAUDE.md | Claude AI | Human User |
| Spec | Framework Developer | AI Assistant |
| SOP | Human User | AI Assistant |
| Inline docs | Framework Developer | AI Assistant |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-DOC-001-* | validate_readme.py | Planned |
| CAP-DOC-002-* | validate_cli_settings.py | Implemented |
| CAP-DOC-003-* | pylint docstring checks | Manual |
| CAP-DOC-004-* | Manual review | Manual |
| CAP-DOC-005-* | validate_spec_format.py | Planned |
| CAP-DOC-006-* | CI version checks | Planned |

---

## Anti-Patterns

### Anti-Pattern 1: Documentation Theater

```markdown
❌ ANTI-PATTERN: Doc exists but doesn't help

# My Agent

This is my agent.

## Overview

It does stuff.

## Usage

Use it.
```

```markdown
✅ CORRECT: Doc that helps users

# My Agent

Executive advisor specializing in strategic decision support.

## Overview

This agent provides structured analysis for executive decisions using
the 5W+H framework. Best suited for strategy, planning, and governance
questions.

## Usage

1. Wake up: `python3 scripts/wake_up.py`
2. Present your strategic question
3. Review the structured analysis
4. Wind down: `python3 scripts/wind_down.py`
```

### Anti-Pattern 2: CLI Settings Without Context

```markdown
❌ ANTI-PATTERN: Settings without identity

## Commands

Run `wake_up.py` to start.
```

```markdown
✅ CORRECT: Settings with full context

# Agent Configuration

## North Star

> **Purpose**: Provide executive-level strategic advice using
> structured analytical frameworks.

## Identity

**Name**: exec-advisor-AGET
**Type**: Advisor
**Domain**: Strategy

## Session Protocol

### Wake Up
When user says "wake up":
1. Load identity from `.aget/identity.json`
2. Display: "Ready to assist with strategic decisions."
```

### Anti-Pattern 3: Examples Without Context

```python
❌ ANTI-PATTERN: Example without explanation

# Example:
validate_naming("/path/to/repo")
```

```python
✅ CORRECT: Example with context

# Example: Validate a template repository
#
# This validates all file names in the repository against
# AGET_FILE_NAMING_CONVENTIONS.md categories A-J.
# Returns exit code 0 if all files comply.
#
# >>> from validate_file_naming import validate_directory
# >>> violations, messages = validate_directory(Path("/path/to/template"))
# >>> print(f"Found {violations} violations")
# Found 0 violations
```

---

## References

- R-TPL-001: Template README requirements
- L394: Example Requirement
- L433: Validator Enforcement Theater Gap (documentation analog)
- AGET_FILE_NAMING_CONVENTIONS.md
- AGET_TEMPLATE_SPEC.md
- Keep a Changelog (https://keepachangelog.com)

---

## Changelog

### v1.0.0 (2026-01-04)

- Initial specification
- Defined CAP-DOC-001 through CAP-DOC-006
- README structure by repo type
- CLI settings file standards (AGENTS.md, CLAUDE.md)
- Inline documentation requirements
- Example requirements (L394)

---

*AGET_DOCUMENTATION_SPEC.md — Documentation standards for AGET framework*
*"Documentation that exists but doesn't help is documentation theater."*
