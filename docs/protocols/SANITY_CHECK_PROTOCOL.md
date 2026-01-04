# Sanity Check Protocol

**Version**: 1.0.0
**Implements**: CAP-SESSION-002
**Patterns**: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

---

## Purpose

Perform health checks on agent structure and configuration. The sanity check protocol ensures agents maintain:
- Structural integrity (required files and directories)
- Configuration validity (JSON files parseable)
- Compliance awareness (warnings for missing recommended elements)

---

## RECOMMENDED Directives (v3.1)

The following are RECOMMENDED behaviors for all AGET agents. Implementations SHOULD follow these patterns for consistency across CLI environments.

### R-SANITY-001: Execute Script First

**RECOMMENDED**: Execute `python3 .aget/patterns/session/sanity_check.py` or the canonical template.

```
When performing sanity check:
1. RECOMMENDED: Execute sanity check script
2. RECOMMENDED: Display human-readable summary
3. RECOMMENDED: Return appropriate exit code
```

### R-SANITY-002: Structured Check Results

**RECOMMENDED**: Each check should return a structured result with:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Check identifier |
| `passed` | boolean | Whether check passed |
| `message` | string | Human-readable result |
| `severity` | enum | info, warning, error |
| `fixable` | boolean | Can auto-fix address this |

### R-SANITY-003: JSON Output Support

**RECOMMENDED**: Support `--json` flag for programmatic consumption.

```bash
python3 sanity_check.py --json | jq '.summary'
```

### R-SANITY-004: Exit Code Semantics

**RECOMMENDED**: Use meaningful exit codes.

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All checks passed | Proceed |
| 1 | Warnings found | Review, may proceed |
| 2 | Errors found | Must fix before proceeding |
| 3 | Runtime error | Check configuration |

### R-SANITY-005: Performance Target

**RECOMMENDED**: Complete sanity check in under 2 seconds.

```
Target: <2s execution time
Measure: time python3 sanity_check.py --json > /dev/null
```

### R-SANITY-006: Cross-CLI Consistency

**RECOMMENDED**: Produce identical output regardless of CLI environment.

The same sanity_check.py should work identically on:
- Claude Code
- Codex CLI
- Cursor
- Custom agents

---

## Implementation

### Script Location

```
# Canonical template (in aget/ core)
aget/scripts/aget_housekeeping_protocol.py

# Instance override (in agent)
.aget/patterns/session/sanity_check.py
```

### Usage

```bash
# Human-readable output
python3 sanity_check.py

# JSON output
python3 sanity_check.py --json

# Pretty JSON
python3 sanity_check.py --json --pretty

# Specify agent directory
python3 sanity_check.py --dir /path/to/agent

# Attempt auto-fixes
python3 sanity_check.py --fix
```

---

## Standard Checks

### Required Checks

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 1 | `.aget/` directory | error | Must exist |
| 2 | `version.json` | error | Must exist and be valid JSON |
| 3 | `identity.json` | warning | Should exist for v3.0+ |
| 4 | `governance/` | warning | Should exist for v3.0+ |

### Recommended Checks

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 5 | `evolution/` | info | L-doc count, index presence |
| 6 | `5D structure` | warning | persona, memory, reasoning, skills, context |
| 7 | `sessions/` | warning | Session log directory |
| 8 | `planning/` | warning | Planning artifacts directory |

---

## Output Format

### Human-Readable

```
=== AGET Housekeeping Report ===

Status: [+] HEALTHY
Checks: 8/8 passed

Checks:
  [+] .aget Directory:
  [+] Version Json: v3.1.0
  [+] Identity Json: north_star defined
  [+] Governance Directory: 3 files present
  [+] Evolution Directory: 42 L-docs
  [+] 5d Structure: 5/5 dimensions present
  [+] Sessions Directory: 15 session files
  [+] Planning Directory: 3 PROJECT_PLANs
```

### JSON

```json
{
  "timestamp": "2026-01-04T12:00:00.000000",
  "agent_path": "/path/to/agent",
  "checks": [
    {
      "name": ".aget_directory",
      "passed": true,
      "message": "",
      "severity": "info",
      "fixable": false
    }
  ],
  "summary": {
    "total": 8,
    "passed": 8,
    "warnings": 0,
    "errors": 0,
    "fixable": 0
  },
  "status": "healthy"
}
```

---

## L021 Verification Table

| # | Check | Resource | Before Action |
|---|-------|----------|---------------|
| 1 | .aget/ dir | `.aget/` | Verify exists before reading files |
| 2 | version.json | `.aget/version.json` | Load before checking fields |
| 3 | identity.json | `.aget/identity.json` | Load before checking north_star |
| 4 | governance/ | `governance/` | Check exists before listing files |
| 5 | evolution/ | `.aget/evolution/` | Check exists before counting L-docs |

---

## Wind Down Integration

### R-SANITY-007: Wind Down Sanity Gate

**RECOMMENDED**: Run sanity check as part of wind down protocol.

```
Wind Down Sequence:
1. Save session notes
2. Run sanity check
3. If errors: WARN user before closing
4. If warnings: Display summary
5. If healthy: Confirm clean close
```

The wind down protocol SHOULD include sanity check results in session metadata:

```json
{
  "session_notes": {
    "started": "2026-01-04T10:00:00",
    "ended": "2026-01-04T12:00:00",
    "sanity_check": {
      "status": "healthy",
      "checks_passed": 8,
      "checks_total": 8
    }
  }
}
```

---

## References

- `aget/scripts/aget_housekeeping_protocol.py` - Canonical template
- CAP-SESSION-002 - Sanity Check Protocol capability
- L038 - Agent-Agnostic Infrastructure
- L021 - Verify-Before-Modify Pattern
- L039 - Diagnostic Efficiency

---

*SANITY_CHECK_PROTOCOL.md - v3.1 Session Protocol*
