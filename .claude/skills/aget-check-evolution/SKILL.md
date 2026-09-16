---
name: aget-check-evolution
description: Monitor .aget/evolution/ directory health. Validates file counts, naming conventions, disk usage, and returns health status with alerts on anomalies.
version: 1.0.1
---

# /aget-check-evolution

Monitor the health of the `.aget/evolution/` directory by checking file counts, types, naming conventions, and disk usage.

## Purpose

Provide self-diagnostic capability for AGET agents to assess their evolution directory health without supervisor intervention.

## Execution

When invoked, perform these checks. First verify `.aget/evolution/` is a readable directory and the required tools (`find`, `wc`, `du`, `jq`, Python 3) are available. If a tool or inventory operation fails, report **UNAVAILABLE** with the failed check; do not turn incomplete readings into an OK result. These checks inspect filenames and JSON syntax, not lesson schema conformance or index-to-file references.

Run each shell block in Bash and inspect its exit status. A nonzero inventory/naming/disk exit means that reading is unavailable, regardless of partial stdout; discard its counts.

### 1. File Inventory

```bash
set -euo pipefail
# Count total files
find .aget/evolution -type f | wc -l

# Count by extension
find .aget/evolution -type f -name "*.md" | wc -l
find .aget/evolution -type f -name "*.json" | wc -l
find .aget/evolution -type f ! -name "*.md" ! -name "*.json" | wc -l
```

### 2. Naming Convention Check

Expected L-doc prefix and number width: `L###_*.md` or `L####_*.md` (three or four digits, as specified by [AGET_LDOC_SPEC.md](https://github.com/aget-framework/aget/blob/v3.34.0/specs/AGET_LDOC_SPEC.md), CAP-LDOC-001). Examples: `L588_skill_invocation_control_semantics.md`, `L1000_example.md`. This check covers only the L prefix, three/four-digit number, underscore separator and .md extension. It does not validate snake_case titles, lesson contents, uniqueness or ID claims.

```bash
set -euo pipefail
# Count L-doc prefix/width matches (title conformance is not checked)
find .aget/evolution -type f \( -name "L[0-9][0-9][0-9]_*.md" -o -name "L[0-9][0-9][0-9][0-9]_*.md" \) | wc -l

# Find non-conforming files (excluding index.json)
find .aget/evolution -type f ! -name "L[0-9][0-9][0-9]_*.md" ! -name "L[0-9][0-9][0-9][0-9]_*.md" ! -name "index.json" ! -name "README.md"
```

### 3. Disk Usage

```bash
set -euo pipefail
du -sk .aget/evolution
```

Use the first output field (allocated KiB) divided by 1024 as `disk_mib` for the thresholds below.

### 4. Index JSON Syntax

Check that `index.json` contains exactly one JSON value. This syntax-only check permits any JSON value, including null; it does not validate the index schema:

```bash
if test ! -e .aget/evolution/index.json; then
  echo "missing"
elif test ! -f .aget/evolution/index.json || test ! -r .aget/evolution/index.json; then
  echo "unavailable"
elif jq -e -s 'length == 1' .aget/evolution/index.json >/dev/null; then
  echo "valid"
else
  index_check_status=$?
  case "$index_check_status" in
    1|4|5) echo "invalid" ;; # zero/multiple values or parse failure (jq 1.7 uses 5)
    *) echo "unavailable" ;; # tool, I/O or invocation failure; retain stderr
  esac
fi
```

## Thresholds

| Metric | OK | WARN | CRITICAL |
|--------|-----|------|----------|
| Total files | <500 | 500-750 | >750 |
| Non-standard files | 0-10 | 11-50 | >50 |
| Allocated disk size | <10 MiB | 10-25 MiB | >25 MiB |
| Index JSON syntax | valid | - | invalid or missing |

**Note**: Thresholds inherited from supervisor defaults. Research AGET baseline (2026-02-08): 94 files, 800K - well within OK range.

## Output Format

Report the following:

```
=== /aget-check-evolution ===

Directory: .aget/evolution/

File Counts:
  Total:     [count]
  L-prefix:  [count] (.md matching L###_*.md or L####_*.md)
  Index:     [1 if exists, 0 otherwise]
  Other:     [count] (non-conforming)

Disk Usage: [size]

Index JSON Syntax: [valid/invalid/missing/unavailable]
Index-to-file references: NOT CHECKED
L-doc title conformance: NOT CHECKED

Non-Conforming Files:
  [list any files not matching expected patterns]

Health Status: [OK | WARN | CRITICAL | UNAVAILABLE]
Alerts:
  [list any threshold violations]
```

## Health Status Logic

Apply this function to the collected readings after the preflight checks. An unavailable reading takes precedence over a computed health result; report any independently observed critical findings as well.

```python
def health_status(total_files, non_standard, disk_mib, index_status):
    if any(value is None for value in (total_files, non_standard, disk_mib)) or index_status == "unavailable":
        return "UNAVAILABLE"
    if index_status in ("invalid", "missing"):
        return "CRITICAL"
    if index_status != "valid":
        return "UNAVAILABLE"
    if total_files > 750 or disk_mib > 25 or non_standard > 50:
        return "CRITICAL"
    if total_files >= 500 or disk_mib >= 10 or non_standard > 10:
        return "WARN"
    return "OK"
```

## Constraints

- **C1**: Read-only operation. Never modify files.
- **C2**: Report ALL findings, even if status is OK.
- **C3**: List non-conforming files by name for actionability.

## Related Skills

- `/aget-check-sessions` - Sessions directory health
- `/aget-check-kb` - Knowledge base health
- `/aget-record-lesson` - Capture findings as L-docs

## Traceability

| Link | Reference |
|------|-----------|
| POC | POC-017 |
| Project | PROJECT_PLAN_AGET_UNIVERSAL_SKILLS.md |
| Source | Fleet Skill Deployment Report (supervisor) |
| Baseline | 94 files, 800K (2026-02-08) |

---

*aget-check-evolution v1.0.1*
*Category: Monitoring*
*POC-017 Phase 1*
