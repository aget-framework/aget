# Shell Integration Guide

**Version**: 1.1.0
**Status**: Active
**Related**: L452 (Shell Orchestration Pattern), L189 (Credential Isolation), L050 (Directive Prompt Language)

---

## Overview

AGET agents are designed to work with CLI-based AI coding assistants (Claude Code, Codex, Gemini CLI, Aider). Since these are Unix programs, the shell is the natural integration layer.

This guide explains how to set up shell integration for launching AGET agents with a single command.

## Quick Start

### 1. Copy Shell Files

```bash
# Create AGET config directory
mkdir -p ~/.aget

# Copy from framework (adjust path as needed)
cp /path/to/aget-framework/aget/shell/*.zsh ~/.aget/
```

### 2. Add to .zshrc

```zsh
# Add this line to ~/.zshrc
source ~/.aget/aget.zsh
```

### 3. Create Agent Aliases

Create `~/.aget/agents.zsh` with your agent shortcuts:

```zsh
# ~/.aget/agents.zsh
alias supervisor='aget ~/github/private-supervisor-AGET'
alias myagent='aget ~/github/my-project-aget'
```

### 4. Reload Shell

```bash
source ~/.zshrc
```

### 5. Launch an Agent

```bash
supervisor "fix the authentication bug"
```

---

## Usage

### Basic Usage

```bash
# Launch agent with simple wake-up
supervisor

# Launch with focus topic
supervisor "implement the new feature"

# Full form
aget ~/github/private-supervisor-AGET "implement the new feature"
```

### Switching CLIs

The default CLI is Claude Code. To use a different CLI:

```bash
# For the current session
use-codex
supervisor "fix the bug"    # Uses Codex

# For a single command
AGET_CLI=gemini supervisor "fix the bug"

# Check current CLI
aget-status
```

### Available CLIs

| CLI | Command | Notes |
|-----|---------|-------|
| Claude Code | `use-claude` | Default, uses subscription auth |
| Claude Code (read-only) | `use-claude-plan` | Advisory mode, no edits |
| Codex | `use-codex` | OpenAI Codex CLI |
| Gemini | `use-gemini` | Uses @file syntax |
| Aider | `use-aider` | Interactive only |

---

## File Structure

```
~/.aget/
├── aget.zsh           # Core integration (from framework)
├── profiles.zsh       # CLI profiles (from framework)
├── agents.zsh         # Your agent aliases (you create this)
└── profiles_local.zsh # Your custom CLI profiles (optional)
```

### aget.zsh

The core `aget()` function and CLI selectors. Source this from your `.zshrc`.

### profiles.zsh

CLI-specific invocation functions. Each profile knows how to:
- Set up authentication (e.g., unset API keys)
- Format the wake-up prompt
- Handle CLI-specific flags

### agents.zsh

Your personal agent aliases. Example:

```zsh
# Core agents
alias supervisor='aget ~/github/private-supervisor-AGET'
alias framework='aget ~/github/aget-framework/private-aget-framework-AGET'

# Project agents
alias myproject='aget ~/github/my-project/private-myproject-aget'
alias webapp='aget ~/github/webapp/agent'

# Grouped by portfolio
alias ccb='aget ~/github/GM-CCB/private-ccb-AGET'
```

### profiles_local.zsh (Optional)

Add custom CLI profiles or override existing ones:

```zsh
# Example: Custom Claude path with directive prompts
_aget_claude() {
  local focus="$1"
  local prompt

  if [[ -n "$focus" ]]; then
    prompt="Read AGENTS.md and execute the Wake Up Protocol. Then focus on: $focus"
  else
    prompt="Read AGENTS.md and execute the Wake Up Protocol."
  fi

  /usr/local/bin/claude "$prompt"
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGET_CLI` | `claude` | Current CLI to use |
| `AGET_HOME` | `~/.aget` | Configuration directory |
| `AGET_CLAUDE_BIN` | `/opt/homebrew/bin/claude` | Claude Code binary path |
| `AGET_CODEX_BIN` | `codex` | Codex binary path |
| `AGET_GEMINI_BIN` | `gemini` | Gemini CLI binary path |
| `AGET_AIDER_BIN` | `aider` | Aider binary path |

### Credential Isolation (L189)

The Claude Code profile unsets `ANTHROPIC_API_KEY` to force subscription authentication:

```zsh
env -u ANTHROPIC_API_KEY /opt/homebrew/bin/claude "$prompt"
```

This allows you to have an API key set for other tools while using your Claude subscription for Claude Code.

---

## Generating Agent Aliases

For large fleets, generate aliases from an inventory:

```bash
# Generate aliases from FLEET_STATE.yaml
python3 /path/to/aget/scripts/generate_agents_zsh.py \
  --fleet ~/github/private-supervisor-AGET/FLEET_STATE.yaml \
  --output ~/.aget/agents.zsh
```

Or manually maintain `~/.aget/agents.zsh` for smaller setups.

---

## Prompt Language Guidelines

When writing shell prompts that reference AGET protocols, use **directive language** rather than **suggestive language**.

### Why This Matters

LLMs interpret prompt phrasing literally. Suggestive phrases like "e.g." or "you might" are treated as optional examples, not instructions. This causes inconsistent protocol execution.

### Language Comparison

| Type | Example | LLM Interpretation |
|------|---------|-------------------|
| ❌ Suggestive | `(e.g. read AGENTS.md)` | Optional example, may skip |
| ❌ Suggestive | `you might want to...` | Weak suggestion, often ignored |
| ❌ Suggestive | `consider reading...` | Advisory, not required |
| ✅ Directive | `Read AGENTS.md` | Clear imperative, will execute |
| ✅ Directive | `Execute the Wake Up Protocol` | Named procedure, recognized |
| ✅ Directive | `Run: python3 scripts/X.py` | Specific action required |

### Correct Patterns

```zsh
# With focus topic
"Read AGENTS.md and execute the Wake Up Protocol. Then study up and focus on: $1"

# Without focus topic
"Read AGENTS.md and execute the Wake Up Protocol."

# Script-based (fastest)
"Run: python3 scripts/wake_up.py"
```

### Anti-Patterns

```zsh
# ❌ BAD: Suggestive/example language
"Wake up (e.g. read AGENTS.md)"
"Start by maybe reading AGENTS.md"
"You could read AGENTS.md first"

# ❌ BAD: Vague references
"Do the startup thing"
"Initialize yourself"
```

**Reference**: L050 (Directive Prompt Language Pattern)

---

## CLI Profiles

### Claude Code

```zsh
_aget_claude() {
  local focus="$1"
  local prompt

  if [[ -n "$focus" ]]; then
    prompt="Read AGENTS.md and execute the Wake Up Protocol. Then study up and focus on: $focus"
  else
    prompt="Read AGENTS.md and execute the Wake Up Protocol."
  fi

  env -u ANTHROPIC_API_KEY /opt/homebrew/bin/claude "$prompt"
}
```

**Features**:
- Subscription auth preference
- Directive prompt language (L050)
- Conditional focus topic handling

### Codex CLI

```zsh
_aget_codex() {
  local focus="$1"
  local prompt

  if [[ -n "$focus" ]]; then
    prompt="Read AGENTS.md and execute the Wake Up Protocol. Then focus on: $focus"
  else
    prompt="Read AGENTS.md and execute the Wake Up Protocol."
  fi

  codex "$prompt"
}
```

**Features**:
- Uses OPENAI_API_KEY from environment
- Directive prompt language (L050)

### Gemini CLI

```zsh
_aget_gemini() {
  local focus="$1"
  local prompt

  if [[ -n "$focus" ]]; then
    prompt="@AGENTS.md Read this file and execute the Wake Up Protocol. Then focus on: $focus"
  else
    prompt="@AGENTS.md Read this file and execute the Wake Up Protocol."
  fi

  gemini -i "$prompt"
}
```

**Features**:
- Requires `-i` flag for initial prompt
- Uses `@filename` syntax for file references
- Directive prompt language (L050)

### Aider

```zsh
_aget_aider() {
  echo "NOTE: Aider doesn't support initial prompts. Use /add AGENTS.md" >&2
  aider
}
```

**Features**:
- Interactive only, no initial prompt
- Manual context loading via `/add` command

---

## Adding a New CLI Profile

1. Edit `~/.aget/profiles_local.zsh`:

```zsh
_aget_myawesomecli() {
  local focus="$1"
  local prompt

  # Use directive language (L050)
  if [[ -n "$focus" ]]; then
    prompt="Read AGENTS.md and execute the Wake Up Protocol. Then focus on: $focus"
  else
    prompt="Read AGENTS.md and execute the Wake Up Protocol."
  fi

  myawesomecli --prompt "$prompt"
}
```

2. Add to the dispatch in `aget.zsh` (or submit a PR to the framework).

---

## Troubleshooting

### "Unknown CLI" Error

```
ERROR: Unknown CLI 'foo'
Available: claude, claude-plan, codex, gemini, aider
```

Check your `AGET_CLI` value:
```bash
echo $AGET_CLI
aget-status
```

### "Directory not found" Error

The agent directory doesn't exist. Check the path in your alias:
```bash
alias supervisor
# Should show: supervisor='aget /full/path/to/agent'
```

### "No AGENTS.md" Warning

The directory exists but doesn't have an AGENTS.md file. This may indicate:
- Not an AGET-configured directory
- Missing agent configuration
- Wrong directory path

### Claude Code Uses API Key Instead of Subscription

Check that the profile is using `env -u ANTHROPIC_API_KEY`:
```bash
type _aget_claude
```

---

## Integration with oh-my-zsh

Place agent aliases in a custom plugin:

```bash
# Create plugin
mkdir -p ~/.oh-my-zsh/custom/plugins/aget
cp ~/.aget/*.zsh ~/.oh-my-zsh/custom/plugins/aget/

# Rename main file
mv ~/.oh-my-zsh/custom/plugins/aget/aget.zsh \
   ~/.oh-my-zsh/custom/plugins/aget/aget.plugin.zsh
```

Add `aget` to plugins in `.zshrc`:
```zsh
plugins=(git aget)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-01-07 | Added Prompt Language Guidelines (L050), updated all CLI profiles to use directive language |
| 1.0.0 | 2026-01-04 | Initial release |

---

## References

- [L050: Directive Prompt Language Pattern](https://github.com/aget-framework/aget/issues/53) - Use directive vs suggestive language
- [L452: Shell Orchestration Pattern](../evolution/L452_shell_orchestration_pattern.md)
- [L189: Credential Isolation Pattern](../evolution/L189_env_u_credential_isolation_pattern.md)
- [AGET_SESSION_SPEC](../specs/AGET_SESSION_SPEC.md) - Wake/wind-down protocols
