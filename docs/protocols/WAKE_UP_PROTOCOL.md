# Wake Up Protocol

**Version**: 1.0.0
**Implements**: CAP-SESSION-001
**Patterns**: L038 (Agent-Agnostic), L021 (Verify-Before-Modify), L039 (Diagnostic Efficiency)

---

## Purpose

Initialize a session with proper context. The wake up protocol ensures agents start with:
- Identity awareness (who am I)
- Current state awareness (what's my version, what's pending)
- Operational context (what can I do, what are my boundaries)

---

## RECOMMENDED Directives (v3.1)

The following are RECOMMENDED behaviors for all AGET agents. Implementations SHOULD follow these patterns for consistency across CLI environments.

### R-WAKE-001: Execute Script First

**RECOMMENDED**: Execute `python3 .aget/patterns/session/wake_up.py` as the first action.

```
When user says "wake up":
1. RECOMMENDED: Execute wake_up.py silently
2. RECOMMENDED: Display formatted output only
3. RECOMMENDED: Do NOT show tool calls
```

### R-WAKE-002: Load Identity Before Proceeding

**RECOMMENDED**: Verify identity files exist before proceeding with session.

| Check | File | Action if Missing |
|-------|------|-------------------|
| 1 | `.aget/version.json` | WARN: Cannot determine version |
| 2 | `.aget/identity.json` | WARN: No north star defined |
| 3 | `governance/MISSION.md` | INFO: Mission not documented |

### R-WAKE-003: JSON Output Support

**RECOMMENDED**: Support `--json` flag for programmatic consumption.

```bash
python3 wake_up.py --json | jq '.version.aget_version'
```

### R-WAKE-004: Performance Target

**RECOMMENDED**: Complete wake up in under 1 second.

```
Target: <1s execution time
Measure: time python3 wake_up.py --json > /dev/null
```

### R-WAKE-005: Cross-CLI Consistency

**RECOMMENDED**: Produce identical output regardless of CLI environment.

The same wake_up.py should work identically on:
- Claude Code
- Codex CLI
- Cursor
- Custom agents

---

## Implementation

### Script Location

```
# Canonical template (in aget/ core)
aget/scripts/wake_up.py

# Instance override (in agent)
.aget/patterns/session/wake_up.py
```

### Usage

```bash
# Human-readable output
python3 wake_up.py

# JSON output
python3 wake_up.py --json

# Pretty JSON
python3 wake_up.py --json --pretty

# Specify agent directory
python3 wake_up.py --dir /path/to/agent
```

---

## Output Format

### Human-Readable

```
**Session: agent-name**
**Version**: vX.Y.Z (YYYY-MM-DD)

Purpose: North star statement

Ready.
```

### JSON

```json
{
  "timestamp": "2026-01-04T12:00:00.000000",
  "agent_path": "/path/to/agent",
  "valid": true,
  "errors": [],
  "version": {
    "aget_version": "3.1.0",
    "updated": "2026-01-04",
    "agent_name": "my-agent",
    "archetype": "advisor",
    "template": "template-advisor-aget"
  },
  "identity": {
    "name": "my-agent",
    "north_star": "Purpose statement"
  },
  "structure": {
    "required": {".aget": true},
    "optional": {"governance": true, "sessions": true}
  }
}
```

---

## L021 Verification Table

| # | Check | Resource | Before Action |
|---|-------|----------|---------------|
| 1 | version.json | `.aget/version.json` | Load before displaying version |
| 2 | identity.json | `.aget/identity.json` | Load before displaying north_star |
| 3 | .aget/ dir | `.aget/` | Verify exists before reading files |
| 4 | config.json | `.aget/config.json` | Load with defaults if missing |

---

## References

- `aget/scripts/wake_up.py` - Canonical template
- CAP-SESSION-001 - Wake-Up Protocol capability
- L038 - Agent-Agnostic Infrastructure
- L021 - Verify-Before-Modify Pattern
- L039 - Diagnostic Efficiency

---

*WAKE_UP_PROTOCOL.md - v3.1 Session Protocol*
