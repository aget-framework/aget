---
name: aget-check-health
description: Run AGET health inspection and housekeeping checks. Detect-only — pair with /aget-enhance-health for remediation.
version: 1.1.0
allowed-tools:
  - Bash
  - Read
  - Glob
---

# aget-check-health

Run health inspection on an AGET agent. This skill performs sanity checks, validates structure, and reports agent health status.

## Instructions

When this skill is invoked:

1. Run the housekeeping script:
   ```bash
   python3 scripts/health_check.py
   ```

2. The script checks:
   - `.aget/` directory structure
   - `version.json` validity
   - `identity.json` validity (if exists)
   - `governance/` directory contents
   - 5D directory structure
   - L-doc count and format

3. Report the health status:
   - **Healthy** (exit 0): All checks passed
   - **Warnings** (exit 1): Non-blocking issues found
   - **Errors** (exit 2): Blocking issues require attention

## Output Format

Present the health report:
```
Sanity Check: [HEALTHY/WARNINGS/ERRORS]

Checks:
- Structure: [PASS/WARN/FAIL]
- Version: [PASS/WARN/FAIL]
- Identity: [PASS/WARN/FAIL]
- Governance: [PASS/WARN/FAIL]

[If warnings/errors, list specific issues]

Recommendations:
- [Action items if any]
```

## Options

- `--json`: Machine-readable output
- `--dir /path`: Run on specific agent directory

**Remediation**: This skill is **detect-only**. For auto-fixes and drift remediation, use `/aget-enhance-health` (SKILL-049, governing spec CAP-SESSION-014). Canonical `check → enhance` pipeline per DESIGN_DIRECTION §Principle 9.

## Error Handling

- Exit code 0: All checks passed
- Exit code 1: Warnings found (list them)
- Exit code 2: Errors found (list them, recommend fixes)
- Exit code 3: Script configuration error

## Related

- `/aget-enhance-health` — **Pair sibling**: remediates drift detected by this skill (SKILL-049, CAP-SESSION-014)
- L532: Skills vs Learnings Distinction
- L656: Loading Dock anti-pattern (`--fix` removed v1.1.0 — was documented but never implemented)
- L671: Classification Without Consequence (`--fix` was unrooted at spec level)
- CAP-SESSION-002: Sanity Check Protocol (legacy reference — canonical is CAP-SESSION-008)
- CAP-SESSION-014: Health Remediation Protocol (governs enhance-health pair skill)

---

*v1.1.0 (2026-04-20): `--fix` flag removed (L656/L671). Remediation migrated to `/aget-enhance-health` SKILL-049.*
