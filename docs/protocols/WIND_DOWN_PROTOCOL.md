# Wind Down Protocol

**Version**: 1.0.0
**Implements**: CAP-SESSION-003
**Patterns**: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

---

## Purpose

Gracefully end a session with proper state capture. The wind down protocol ensures:
- Session work is documented
- Sanity checks pass before closing
- Pending work is flagged for next session
- Clean handoff state

---

## RECOMMENDED Directives (v3.1)

The following are RECOMMENDED behaviors for all AGET agents. Implementations SHOULD follow these patterns for consistency across CLI environments.

### R-WIND-001: Execute Script First

**RECOMMENDED**: Execute `python3 .aget/patterns/session/wind_down.py` as the wind down action.

```
When user says "wind down":
1. RECOMMENDED: Execute wind_down.py
2. RECOMMENDED: Display session summary
3. RECOMMENDED: Show sanity check results
4. RECOMMENDED: Confirm clean close or warn of issues
```

### R-WIND-002: Sanity Gate Before Close

**RECOMMENDED**: Run sanity check as mandatory gate before session close.

| Sanity Status | Action |
|---------------|--------|
| healthy | Confirm clean close |
| warning | Display warnings, allow close |
| error | WARN user, require acknowledgment |

### R-WIND-003: Session Notes Capture

**RECOMMENDED**: Capture session metadata including sanity check results.

```json
{
  "session_id": "session_2026-01-04_1200",
  "started": "2026-01-04T10:00:00",
  "ended": "2026-01-04T12:00:00",
  "sanity_check": {
    "status": "healthy",
    "checks_passed": 8,
    "checks_total": 8,
    "timestamp": "2026-01-04T12:00:00"
  },
  "pending_work": [],
  "handoff_notes": ""
}
```

### R-WIND-004: JSON Output Support

**RECOMMENDED**: Support `--json` flag for programmatic consumption.

```bash
python3 wind_down.py --json | jq '.sanity_check.status'
```

### R-WIND-005: Performance Target

**RECOMMENDED**: Complete wind down in under 3 seconds (includes sanity check).

```
Target: <3s execution time
Measure: time python3 wind_down.py --json > /dev/null
```

### R-WIND-006: Cross-CLI Consistency

**RECOMMENDED**: Produce identical output regardless of CLI environment.

---

## Implementation

### Script Location

```
# Canonical template (in aget/ core)
aget/scripts/wind_down.py

# Instance override (in agent)
.aget/patterns/session/wind_down.py
```

### Usage

```bash
# Human-readable output
python3 wind_down.py

# JSON output
python3 wind_down.py --json

# Pretty JSON
python3 wind_down.py --json --pretty

# Specify agent directory
python3 wind_down.py --dir /path/to/agent

# Add handoff notes
python3 wind_down.py --notes "Continue with Gate 3"

# Skip sanity check (not recommended)
python3 wind_down.py --skip-sanity
```

---

## Wind Down Sequence

```
┌─────────────────────────────────────────┐
│           WIND DOWN SEQUENCE            │
├─────────────────────────────────────────┤
│ 1. Gather session metadata              │
│    - Start time, duration               │
│    - Files modified                     │
│    - Commits made                       │
│                                         │
│ 2. Run sanity check (R-WIND-002)        │
│    - Execute housekeeping protocol      │
│    - Capture results                    │
│                                         │
│ 3. Evaluate sanity gate                 │
│    - healthy → proceed                  │
│    - warning → display, proceed         │
│    - error → WARN, require ack          │
│                                         │
│ 4. Capture session notes (R-WIND-003)   │
│    - Include sanity results             │
│    - Note pending work                  │
│    - Save handoff notes                 │
│                                         │
│ 5. Display session summary              │
│    - Duration                           │
│    - Sanity status                      │
│    - Pending items                      │
│    - Clean close confirmation           │
└─────────────────────────────────────────┘
```

---

## Output Format

### Human-Readable

```
**Session Complete: agent-name**
**Duration**: 2h 15m

Sanity Check: [+] HEALTHY (8/8 passed)

Session Summary:
- Files modified: 5
- Commits: 2
- L-docs created: 1

Pending Work: None

Clean close confirmed.
```

### JSON

```json
{
  "timestamp": "2026-01-04T12:00:00.000000",
  "agent_path": "/path/to/agent",
  "session": {
    "started": "2026-01-04T10:00:00",
    "ended": "2026-01-04T12:00:00",
    "duration_seconds": 7200
  },
  "sanity_check": {
    "status": "healthy",
    "checks_passed": 8,
    "checks_total": 8,
    "warnings": 0,
    "errors": 0
  },
  "pending_work": [],
  "handoff_notes": "",
  "clean_close": true
}
```

---

## L021 Verification Table

| # | Check | Resource | Before Action |
|---|-------|----------|---------------|
| 1 | session start | `.aget/session_state.json` | Load to calculate duration |
| 2 | sanity check | housekeeping script | Run before generating summary |
| 3 | pending work | `planning/` directory | Scan for in-progress items |
| 4 | sessions dir | `sessions/` | Verify exists before writing |

---

## Sanity Gate Details

### Gate Behavior

The sanity gate (R-WIND-002) ensures session doesn't close with structural issues.

**Healthy** (exit code 0):
```
Sanity Check: [+] HEALTHY (8/8 passed)
Clean close confirmed.
```

**Warning** (exit code 1):
```
Sanity Check: [!] WARNING (6/8 passed, 2 warnings)
Warnings:
  - identity.json: north_star not defined
  - sessions/: directory not found

Proceeding with close (warnings noted).
```

**Error** (exit code 2):
```
Sanity Check: [x] ERROR (5/8 passed, 3 errors)
Errors:
  - .aget/: directory not found
  - version.json: invalid JSON

⚠️  Session has structural errors.
    Run sanity check --fix or address manually.
    Type 'acknowledge' to close anyway.
```

---

## Session State File

Optional file for tracking session state:

**Location**: `.aget/session_state.json`

```json
{
  "current_session": {
    "id": "session_2026-01-04_1000",
    "started": "2026-01-04T10:00:00",
    "wake_up_completed": true
  },
  "last_session": {
    "id": "session_2026-01-03_1400",
    "ended": "2026-01-03T16:30:00",
    "sanity_status": "healthy"
  }
}
```

---

## References

- `aget/scripts/wind_down.py` - Canonical template
- `aget/scripts/aget_housekeeping_protocol.py` - Sanity check script
- CAP-SESSION-003 - Wind Down Protocol capability
- L038 - Agent-Agnostic Infrastructure
- L021 - Verify-Before-Modify Pattern
- L039 - Diagnostic Efficiency

---

*WIND_DOWN_PROTOCOL.md - v3.1 Session Protocol*
