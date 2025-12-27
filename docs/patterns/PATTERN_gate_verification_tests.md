# Pattern: Gate Verification Tests

**Purpose**: Ensure each PROJECT_PLAN gate includes explicit, executable verification tests.

**Source Learning**: L382 (v3.0.0-alpha.1 release revealed verification gaps)

---

## Problem

PROJECT_PLANs specify "Success Criteria" in prose but lack executable test commands. This leads to:
- Verification skipped or inconsistent
- New validators created but not self-tested
- Artifacts created but not validated against their own specs

## Pattern

Each gate SHOULD include a **Verification Tests** section with:

1. **Executable commands** (not just prose criteria)
2. **Expected outputs** (what success looks like)
3. **Validators used** (which validators apply to this gate's artifacts)

## Template

```markdown
## G-N: [Gate Name]

**Objective**: [What this gate accomplishes]

**Deliverables**:
| # | Deliverable | Verification |
|---|-------------|--------------|
| N.1 | [Artifact] | [How to verify] |

**Verification Tests** (MANDATORY):

```bash
# Test N.1: [Description]
python3 validation/[validator].py [target]
# Expected: [output pattern]

# Test N.2: [Description]
[command]
# Expected: [output pattern]
```

**Success Criteria**:
- [ ] All verification tests pass
- [ ] [Additional criteria]

**Decision Point**:
- **GO**: All tests pass
- **NOGO**: Fix issues, re-run tests
```

## Gate-Specific Validators

| Gate Creates | Validator to Use |
|--------------|------------------|
| Specification | validate_spec_format.py (future) |
| Process YAML | validate_process_spec.py |
| Change Proposal | validate_change_proposal.py |
| PROJECT_PLAN | validate_project_plan.py |
| L-doc | validate_learning_doc.py |
| Pattern | validate_graduation_history.py |
| Any markdown | validate_cross_references.py |
| Template changes | validate_template_manifest.py |
| Vocabulary | validate_vocabulary.py |

## Self-Test Requirement

When a gate **creates a new validator**, the gate MUST include:

1. Validator runs on its intended target type
2. Validator produces expected output format
3. Validator handles edge cases (empty, malformed, missing)

Example for G-5.5 (validate_process_spec.py):

```bash
# Self-test: New validator works
python3 validation/validate_process_spec.py specs/processes/PROCESS_release_workflow.yaml
# Expected: ✅ 1/1 process specs valid

# Edge case: No YAML files
python3 validation/validate_process_spec.py /tmp/empty/
# Expected: Exit 2, "No process specs found"
```

## Integration Test Requirement

Before release gate (G-N), run ALL applicable validators:

```bash
# Comprehensive validation before release
python3 validation/validate_process_spec.py specs/processes/
python3 validation/validate_change_proposal.py docs/proposals/accepted/
python3 validation/validate_cross_references.py --dir .
python3 validation/validate_graduation_history.py --dir .
python3 -m pytest tests/ -v
```

## Anti-Patterns

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| "Verify spec is complete" | `python3 validate_spec.py spec.md` |
| "Check all fields present" | List expected fields + test command |
| "Success: Spec validates" | Show exact command + expected output |
| Creating validator without testing it | Add self-test in same gate |

## Application

**Retroactive**: Completed plans should document what tests WERE run (for audit).

**Prospective**: New plans MUST include Verification Tests sections.

---

## v3.0.0-alpha.1 Retroactive Verification

Tests that SHOULD have been in plan but weren't explicit:

```bash
# CP-001 verification (G-1)
python3 validation/validate_change_proposal.py docs/proposals/accepted/CP-001*.md

# New validators self-test (G-5.5 through G-5.10)
python3 validation/validate_process_spec.py specs/processes/
python3 validation/validate_change_proposal.py docs/proposals/accepted/
python3 validation/validate_project_plan.py --help
python3 validation/validate_learning_doc.py --help
python3 validation/validate_cross_references.py --dir aget/
python3 validation/validate_graduation_history.py specs/

# Integration (G-6)
# All above + template validation + pytest
```

---

*Pattern: Gate Verification Tests*
*Source: L382 (Gate Verification Gap)*
*Created: 2025-12-26*
