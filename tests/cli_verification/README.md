# CLI Verification Test Framework

**Version**: 1.0.0
**Status**: ACTIVE
**Implements**: PROJECT_PLAN_cli_independence_validation_v1.0

---

## Purpose

Validate AGET's CLI independence by testing core operations across multiple CLI agents. This framework provides:

1. **Version-tracked validation** — Records which CLI version was tested
2. **Reproducible tests** — Same tests run on any CLI
3. **Gap documentation** — Captures CLI-specific differences
4. **Honest outcomes** — "Fail" is a valid result

---

## Supported CLIs

| CLI | Vendor | Min Version | Status |
|-----|--------|-------------|--------|
| Claude Code | Anthropic | 2.0.0 | Baseline |
| Codex CLI | OpenAI | 0.70.0 | Validation Target |
| Gemini CLI | Google | 0.20.0 | Validation Target |

---

## Test Categories

| ID | Category | Description | Tests |
|----|----------|-------------|-------|
| TC-001 | Settings Read | CLI reads AGENTS.md and follows instructions | 3 |
| TC-002 | Wake Protocol | wake_up.py executes correctly | 3 |
| TC-003 | Wind Protocol | wind_down.py executes correctly | 3 |
| TC-004 | Script Execution | `.aget/patterns/` scripts work | 5 |
| TC-005 | L-doc Creation | Can create/update L-docs | 3 |
| TC-006 | File Operations | Read/write/edit per CLI tool model | 5 |

---

## Directory Structure

```
tests/cli_verification/
├── README.md              # This file
├── conftest.py            # Shared fixtures
├── cli_versions.json      # Version tracking
├── test_claude_code.py    # Claude Code tests
├── test_codex_cli.py      # Codex CLI tests
├── test_gemini_cli.py     # Gemini CLI tests
└── validation_reports/    # Output reports (gitignored)
```

---

## Version Tracking

All validations are version-tracked in `cli_versions.json`:

```json
{
  "tested_versions": {
    "claude_code": {
      "versions": ["2.1.9"],
      "last_tested": "2026-01-16"
    }
  }
}
```

**Why version tracking matters**: CLI agents iterate rapidly. A test that passes on v0.77.0 may fail on v0.78.0. Version tracking enables:
- Reproducibility
- Regression detection
- Support matrix accuracy

---

## Running Tests

### Prerequisites

1. Target CLI must be installed and authenticated
2. Python 3.10+
3. pytest installed

### Run All Tests

```bash
# From aget/ directory
pytest tests/cli_verification/ -v
```

### Run for Specific CLI

```bash
pytest tests/cli_verification/test_claude_code.py -v
pytest tests/cli_verification/test_codex_cli.py -v
pytest tests/cli_verification/test_gemini_cli.py -v
```

### Skip Unavailable CLIs

```bash
# Skip if CLI not installed
pytest tests/cli_verification/ -v --ignore-glob="*codex*"
```

---

## Validation Reports

After running tests, generate a validation report:

```bash
python tests/cli_verification/generate_report.py \
  --cli claude_code \
  --version 2.1.9 \
  --output docs/validation/
```

Report template: `VALIDATION_REPORT_<cli>_v<version>.md`

---

## Support Levels

Based on validation results, CLIs are assigned support levels:

| Level | Meaning | Evidence |
|-------|---------|----------|
| **Certified** | Full CI validation, all tests pass | CI + VALIDATION_REPORT |
| **Validated** | Manual validation, all tests pass | VALIDATION_REPORT |
| **Compatible** | Basic operations work, documented gaps | VALIDATION_REPORT + GAP_ANALYSIS |
| **Experimental** | Untested, architecture should support | None |
| **Unsupported** | Known blockers | GAP_ANALYSIS |

---

## Adding a New CLI

1. Create `test_<cli_name>.py` following existing patterns
2. Add CLI to `cli_versions.json`
3. Run validation tests
4. Generate VALIDATION_REPORT
5. Update AGET_CLI_SUPPORT_MATRIX.md

---

## Fixtures

Common fixtures in `conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `test_agent_dir` | Temporary AGET agent directory |
| `cli_version` | Current CLI version being tested |
| `agents_md_content` | Standard AGENTS.md content |
| `wake_up_script` | Path to wake_up.py |

---

## References

- PROJECT_PLAN_cli_independence_validation_v1.0
- L452: Shell Orchestration Pattern
- CLI_SETTINGS_STANDARD.md
- AGET_FRAMEWORK_SPEC.md

---

*CLI Verification Test Framework - Prove before you claim*
