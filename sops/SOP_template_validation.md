# SOP: Template Validation

**Version**: 1.0.0
**Date**: 2026-01-11
**Status**: Active
**Owner**: aget-framework
**Implements**: CAP-TPL-014, R-REL-015

---

## Purpose

Define the standard procedure for validating AGET templates against v3.3 exemplar requirements.

---

## Scope

This SOP applies to:
- All 9 AGET templates in the public framework
- New template creation
- Template updates

---

## Prerequisites

- Access to template directory
- Understanding of AGET v3.3 structure
- Familiarity with SKOS and EARS standards

---

## Procedure

### 1. Structural Validation

Run the following checks for each template:

#### 1.1 Core Files (Required)

| Check | Command | Expected |
|-------|---------|----------|
| version.json exists | `test -f .aget/version.json` | Success |
| AGENTS.md exists | `test -f AGENTS.md` | Success |
| CLAUDE.md is symlink | `test -L CLAUDE.md` | Success |
| README.md exists | `test -f README.md` | Success |
| CHANGELOG.md exists | `test -f CHANGELOG.md` | Success |

#### 1.2 v3.3 Directories (Required)

| Check | Command | Expected |
|-------|---------|----------|
| specs/ exists | `test -d specs` | Success |
| shell/ exists | `test -d shell` | Success |
| .aget/evolution/ exists | `test -d .aget/evolution` | Success |

#### 1.3 v3.3 Files (Required)

| Check | Command | Expected |
|-------|---------|----------|
| {Type}_SPEC.md exists | `ls specs/*_SPEC.md` | 1 file |
| {Type}_VOCABULARY.md exists | `ls specs/*_VOCABULARY.md` | 1 file |
| {type}_profile.zsh exists | `ls shell/*_profile.zsh` | 1 file |
| shell/README.md exists | `test -f shell/README.md` | Success |

### 2. Specification Validation

Verify spec structure:

```bash
spec_file=$(ls specs/*_SPEC.md | head -1)

# Required sections
grep -c "^## Abstract" "$spec_file"              # Must be 1
grep -c "^## Archetype Definition" "$spec_file"  # Must be 1
grep -c "^## Capabilities" "$spec_file"          # Must be 1
grep -c "^## Inviolables" "$spec_file"           # Must be 1
grep -c "^## EKO Classification" "$spec_file"    # Must be 1
grep -c "^## Archetype Constraints" "$spec_file" # Must be 1
grep -c "^## A-SDLC Phase Coverage" "$spec_file" # Must be 1
```

### 3. Vocabulary Validation

Verify vocabulary structure:

```bash
vocab_file=$(ls specs/*_VOCABULARY.md | head -1)

# Required sections
grep -c "^## Concept Scheme" "$vocab_file"        # Must be 1
grep -c "^## Core Concepts" "$vocab_file"         # Must be 1
grep -c "^## Concept Relationships" "$vocab_file" # Must be 1
grep -c "^## EKO Cross-References" "$vocab_file"  # Must be 1

# SKOS compliance (minimum 5 concepts)
grep -c "skos:prefLabel" "$vocab_file"            # Must be ≥6 (1 scheme + 5 concepts)
```

### 4. Shell Integration Validation

Verify shell profile:

```bash
profile_file=$(ls shell/*_profile.zsh | head -1)

# Required functions
grep -c "aget_info()" "$profile_file"  # Must be 1
grep -c "aget_docs()" "$profile_file"  # Must be 1

# Required documentation paths
grep -c "AGET_SPEC=" "$profile_file"   # Must be 1
grep -c "AGET_VOCAB=" "$profile_file"  # Must be 1
```

---

## V-Tests Summary

| ID | Test | BLOCKING |
|----|------|----------|
| V-SOP-TV-01 | Core files exist | YES |
| V-SOP-TV-02 | v3.3 directories exist | YES |
| V-SOP-TV-03 | Spec has required sections | YES |
| V-SOP-TV-04 | Vocabulary has SKOS structure | YES |
| V-SOP-TV-05 | Shell profile has required functions | YES |

---

## Automation

For automated validation, use:

```bash
python3 validation/validate_template_exemplar.py --template template-{type}-aget
```

---

## Failure Handling

If validation fails:

1. Document the failure in the template's CHANGELOG.md
2. Create issue if structural gap
3. For content gaps, defer to PROJECT_PLAN_template_content_enrichment

---

## References

- TEMPLATE_STRUCTURE_GUIDE.md (v2.0.0)
- AGET_TEMPLATE_SPEC.md (CAP-TPL-014)
- SPEC_TEMPLATE_v3.3.md
- VOCABULARY_TEMPLATE_v3.3.md

---

*SOP_template_validation.md v1.0.0 - Template validation procedure*
