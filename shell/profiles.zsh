# AGET CLI Profiles
# Version: 1.0.0
# Source: aget-framework/aget/shell/profiles.zsh
#
# CLI-specific invocation functions for the aget() launcher.
# Each profile handles auth, flags, and prompt format for its CLI.
#
# To add a new CLI:
#   1. Create _aget_<cli>() function below
#   2. Add case to aget() in aget.zsh
#   3. Document in SHELL_INTEGRATION.md

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Claude Code
# Binary: claude (Homebrew: /opt/homebrew/bin/claude)
# Auth: Unsets ANTHROPIC_API_KEY to prefer subscription auth (L189)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_claude() {
  local focus="$1"
  local prompt
  local claude_bin="${AGET_CLAUDE_BIN:-/opt/homebrew/bin/claude}"

  if [[ -n "$focus" ]]; then
    prompt="Wake up (e.g. read AGENTS.md plus ...). Afterwards, study up. And focus on: $focus"
  else
    prompt="Wake up."
  fi

  # env -u removes ANTHROPIC_API_KEY for this invocation only
  # This forces Claude Code to use subscription auth instead of API key
  env -u ANTHROPIC_API_KEY "$claude_bin" "$prompt"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Claude Code (Plan Mode)
# Read-only advisory mode - no file edits
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_claude_plan() {
  local focus="$1"
  local prompt
  local claude_bin="${AGET_CLAUDE_BIN:-/opt/homebrew/bin/claude}"

  if [[ -n "$focus" ]]; then
    prompt="Wake up. Today you are in advisory mode (no edits). Focus on: $focus"
  else
    prompt="Wake up. Today you are in advisory mode (no edits)."
  fi

  env -u ANTHROPIC_API_KEY "$claude_bin" --permission-mode plan "$prompt"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Codex CLI (OpenAI)
# Binary: codex
# Auth: Uses OPENAI_API_KEY from environment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_codex() {
  local focus="$1"
  local codex_bin="${AGET_CODEX_BIN:-codex}"

  if [[ -n "$focus" ]]; then
    "$codex_bin" "wake up. focus on: $focus"
  else
    "$codex_bin" "wake up"
  fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Gemini CLI (Google)
# Binary: gemini
# Auth: Uses GOOGLE_API_KEY from environment
# Note: Requires -i flag for initial prompt, uses @file syntax for file refs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_gemini() {
  local focus="$1"
  local gemini_bin="${AGET_GEMINI_BIN:-gemini}"

  # Gemini uses @filename syntax to reference files
  if [[ -n "$focus" ]]; then
    "$gemini_bin" -i "@AGENTS.md wake up. focus on: $focus"
  else
    "$gemini_bin" -i "@AGENTS.md wake up"
  fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Aider
# Binary: aider
# Auth: Various (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
# Note: Aider doesn't support initial prompts - launches interactive
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_aider() {
  local focus="$1"
  local aider_bin="${AGET_AIDER_BIN:-aider}"

  # Aider is interactive-only, can't pass initial prompt
  if [[ -n "$focus" ]]; then
    echo "NOTE: Aider doesn't support initial prompts. Focus topic: $focus" >&2
    echo "Use /add AGENTS.md and paste your focus after launch." >&2
  fi

  "$aider_bin"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Profile: Cursor (placeholder)
# Binary: cursor
# Note: Cursor CLI behavior TBD - placeholder for future
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_aget_cursor() {
  local focus="$1"
  echo "ERROR: Cursor CLI profile not yet implemented" >&2
  echo "Contributions welcome: aget-framework/aget/shell/profiles.zsh" >&2
  return 1
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# User Local Profiles
# Source user's custom profiles if they exist
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[[ -f ~/.aget/profiles_local.zsh ]] && source ~/.aget/profiles_local.zsh
