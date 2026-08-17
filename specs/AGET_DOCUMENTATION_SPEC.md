# AGET Documentation Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Format (Documentation Standards)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-08-16 (v1.1.0 — Enforcement surface separates instrument-exists from instrument-is-reached; see Changelog)
**Author**: aget-framework
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

### CAP-DOC-007: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-DOC-007-01 | ubiquitous | The SYSTEM shall validate all README files against CAP-DOC-001 structural requirements. |
| CAP-DOC-007-02 | event-driven | WHEN a new template is created, THEN the SYSTEM shall generate a README from the template-appropriate structure. |
| CAP-DOC-007-03 | conditional | IF a specification references other specs, THEN the SYSTEM shall verify those cross-references resolve to existing files. |

---

## Enforcement

> **Why this table has four columns instead of two.** The previous form recorded a single
> `Status` per requirement, which merged two independent facts: whether the named instrument
> *exists*, and whether anything *runs* it. Those come apart. `validate_cli_settings.py` was
> recorded `Implemented` while having zero callers — true as a statement about the file,
> false as a statement about enforcement. A reader could not tell which claim was being made.
>
> `Exists` and `Callers` are each independently checkable. `Enforcement` is **derived** from
> them, never asserted on its own: a requirement is `ENFORCED` only where an instrument
> exists **and** something invokes it.

| Requirement | Named instrument | Exists | Callers | Enforcement |
|-------------|------------------|:------:|:-------:|-------------|
| CAP-DOC-001-* | `validate_readme.py` | ✗ | — | **NONE** — instrument absent (build-or-remove: 2026-11-16) |
| CAP-DOC-002-* | `scripts/validate_cli_settings.py` | ✓ | **0** | **NONE** — exists, never invoked |
| CAP-DOC-003-* | pylint docstring checks | ✗ | — | **NONE** — no instrument in this repository |
| CAP-DOC-004-* | *(none — human review)* | n/a | n/a | MANUAL by design |
| CAP-DOC-005-* | `verification/validate_spec_format.py` | ✓ | **0** | **NONE** — exists, never invoked |
| CAP-DOC-006-* | *(none named)* | ✗ | — | **NONE** |

**Measured** 2026-08-16 at canonical HEAD, clean tree. `Callers` counts **invocation
contexts** (`python3 X`, `run: X`, `import X`), not mentions — a spec table, a changelog or
a registry entry naming an instrument is not a caller. Predicate, including its known
limitations and a positive control, is recorded with the measurement.

**Two corrections this table makes to the previous form:**

- `CAP-DOC-002-*` read `Implemented`. The instrument exists and has **zero** callers, so
  nothing enforced that requirement. The old value overstated.
- `CAP-DOC-005-*` read `Planned`. `verification/validate_spec_format.py` **already exists**.
  The old value understated. Drift ran in both directions, which is what a single merged
  column hides.

**A validator that passes on an empty view is not enforcement.** `validate_cli_settings.py`
run against this repository reports `0 found, 0 passed` and exits **0** — canonical has no
`AGENTS.md` at its root. Wiring it here as-is would produce a green gate that proves
nothing. Any future `Callers` entry for it must be accompanied by a non-empty view.

**`NONE` is a statement of fact, not a to-do.** It records that the requirement is currently
unenforced. Where a build is intended, the row carries a **build-or-remove date**: on that
date the requirement either gains a working instrument or the enforcement claim is deleted.
A date that passes with neither is itself a detectable defect.

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

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-DOC-001 | CAP-DOC-001-01 | automated | Verify every repository has a README.md file |
| V-DOC-002 | CAP-DOC-001-02 | automated | Verify README.md contains a project purpose section |
| V-DOC-003 | CAP-DOC-001-03 | automated | Verify README.md contains a quickstart section |
| V-DOC-004 | CAP-DOC-002-01 | automated | Verify every template has an AGENTS.md file |
| V-DOC-005 | CAP-DOC-002-03 | automated | Verify AGENTS.md includes agent identity information |
| V-DOC-006 | CAP-DOC-003-01 | automated | Verify Python modules in validation/ have module docstrings |
| V-DOC-007 | CAP-DOC-005-01 | inspection | Verify specifications include at least one example section |
| V-DOC-008 | CAP-DOC-006-02 | automated | Verify version numbers in documentation match current release |
| V-DOC-009 | CAP-DOC-007-01 | automated | Verify README files pass CAP-DOC-001 structural validation |
| V-DOC-010 | CAP-DOC-007-03 | automated | Verify spec cross-references resolve to existing files |

### Validation Commands

```bash
# Check all repos have README.md (V-DOC-001)
for repo in aget/ template-*-aget/; do [ -f "$repo/README.md" ] && echo "PASS: $repo" || echo "FAIL: $repo missing README.md"; done

# Check templates have AGENTS.md (V-DOC-004)
for tmpl in template-*-aget/; do [ -f "$tmpl/AGENTS.md" ] && echo "PASS: $tmpl" || echo "FAIL: $tmpl missing AGENTS.md"; done

# Check Python modules have docstrings (V-DOC-006)
for py in validation/*.py; do python3 -c "import ast; t=ast.parse(open('$py').read()); print('PASS' if ast.get_docstring(t) else 'FAIL')" 2>/dev/null; done

# Check spec cross-references (V-DOC-010)
grep -roh "AGET_[A-Z_]*_SPEC\.md" aget/specs/ | sort -u | while read spec; do [ -f "aget/specs/$spec" ] && echo "PASS: $spec" || echo "FAIL: $spec not found"; done
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

### v1.0.1 (2026-03-17)

- Added CAP-DOC-007: EARS System-Level Requirements (L682 L0→L1 uplift)
- 3 requirements with SYSTEM subject, ubiquitous/event-driven/conditional patterns

### v1.1.0 (2026-08-16)

**Enforcement surface: separate what exists from what runs.**

The `Enforcement` table recorded one `Status` per requirement, merging two independent
facts — whether the named instrument exists, and whether anything invokes it. Measured at
canonical HEAD, that merge was hiding drift in **both** directions:

- `CAP-DOC-002-*` read `Implemented`. The instrument exists and has **zero** callers, so the
  requirement was not enforced. Overstated.
- `CAP-DOC-005-*` read `Planned`. The instrument **already exists**. Understated.
- `CAP-DOC-001-*` names `validate_readme.py`, which is **absent from the repository**, while
  four of its V-tests are labelled `automated`.

Changes:

- Table gains `Exists` and `Callers` columns, each independently checkable. `Enforcement` is
  now **derived** from them rather than asserted — `ENFORCED` requires both.
- `Callers` counts **invocation contexts**, not mentions. A spec table, changelog or registry
  entry naming an instrument is not a caller.
- Rows intending a future instrument carry a **build-or-remove date**. A date that passes
  with neither outcome is itself detectable.
- Records that a validator passing on an empty view is not enforcement:
  `validate_cli_settings.py` exits 0 against this repository, which has no `AGENTS.md` at
  root.

No CAP-DOC requirement changed. This amendment changes only how the spec reports its own
enforcement — the claims it makes about itself are now falsifiable.

Basis: principal ruling of 2026-08-16 — *a claim the framework makes about itself must be
checkable or removed*; disclosure does not discharge it.

**Known and deliberately out of scope**: `AGET_SPEC_FORMAT` defines the Enforcement field as
free text and says capabilities `SHOULD` have enforcement, not `SHALL`. It therefore permits
every defect corrected here, in any spec. That is filed separately rather than folded in, so
a fleet-wide finding does not get buried in a single-spec repair.

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
