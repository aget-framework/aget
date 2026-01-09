# Vocabulary Prose Validator CI Integration

## Overview

The `validate_vocabulary_prose.py` validator ensures AGET Vocabulary compliance with L493 (Vocabulary_Prose_Marking_Pattern).

## Usage

```bash
# Check all prefLabel values are compound
python validation/validate_vocabulary_prose.py --check-terms specs/AGET_VOCABULARY_SPEC.md

# Check prose usage in a document
python validation/validate_vocabulary_prose.py --check-prose docs/some_doc.md

# Get fix suggestions
python validation/validate_vocabulary_prose.py --fix specs/AGET_VOCABULARY_SPEC.md
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation failed (errors found) |

## GitHub Actions Integration

```yaml
# .github/workflows/vocabulary-check.yml
name: Vocabulary Validation

on:
  push:
    paths:
      - 'specs/AGET_VOCABULARY_SPEC.md'
      - 'validation/validate_vocabulary_prose.py'
  pull_request:
    paths:
      - 'specs/AGET_VOCABULARY_SPEC.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Validate vocabulary terms
        run: |
          python validation/validate_vocabulary_prose.py --check-terms specs/AGET_VOCABULARY_SPEC.md

      - name: Check prose in specs
        run: |
          for spec in specs/*.md; do
            echo "Checking $spec..."
            python validation/validate_vocabulary_prose.py --check-prose "$spec" || true
          done
```

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: vocabulary-check
        name: AGET Vocabulary Check
        entry: python validation/validate_vocabulary_prose.py --check-terms specs/AGET_VOCABULARY_SPEC.md
        language: python
        files: AGET_VOCABULARY_SPEC\.md$
        pass_filenames: false
```

## Requirements Validated

| Requirement | Mode | Severity |
|-------------|------|----------|
| R-VOC-TERM-001 | `--check-terms` | Error |
| R-VOC-PROSE-001 | `--check-prose` | Error |
| R-VOC-PROSE-002 | `--check-prose` | Warning |
| R-VOC-VAL-003 | `--check-prose` | Error |

## Enforcement Progression (ADR-008)

| Phase | Mode | Blocking |
|-------|------|----------|
| Advisory | `--check-terms` | No (warnings only) |
| Strict | `--check-terms` | Yes (CI blocks) |
| Generator | Future | Auto-fix PRs |

---

*CI Integration for validate_vocabulary_prose.py*
*See: L493, ADR-008*
