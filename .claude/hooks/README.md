# AGET Hooks

Platform-native lifecycle event handlers for Claude Code agents.

## Available Events

| Event | When | Can Block? | Use Case |
|-------|------|:----------:|----------|
| `SessionStart` | Session begins | No | Context loading |
| `SessionEnd` | Session closes | No | State capture, wind-down |
| `PreToolUse` | Before tool execution | Yes | Policy enforcement |
| `PostToolUse` | After tool execution | No | Logging, validation |
| `UserPromptSubmit` | Before processing input | Yes | Input validation |
| `Stop` | Claude finishes responding | No | Post-response actions |

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/wind_down.py\" --json --skip-health",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Reference Implementation

This agent uses two hooks as validated examples:

| Hook | Event | Script | Purpose |
|------|-------|--------|---------|
| Wind-down | `SessionEnd` | `scripts/wind_down.py` | Automatic session state capture |
| Push window | `PreToolUse` (Bash) | `.claude/hooks/push_window_guard.sh` | Saturday-only push enforcement |

## Hook Script Protocol

- **Input**: JSON on stdin with `session_id`, `cwd`, `tool_input` (for PreToolUse)
- **Exit 0**: Allow / success
- **Exit 2**: Block (PreToolUse only) — stderr message fed back to agent
- **Timeout**: Default 600s, configurable per hook

## ADR-008 Context

Hooks enable **Generator level** enforcement — the highest ADR-008 tier:

| Level | Mechanism | Example |
|-------|-----------|---------|
| Advisory | CLAUDE.md text | "Push on Saturday" |
| Strict | Skill instructions | `/aget-file-issue` routing |
| **Generator** | **Hooks** | `push_window_guard.sh` blocks non-Saturday pushes |

---

*See: L640 (adoption gap), L694 (CLI convergence), #505 (hook adoption pilot)*
