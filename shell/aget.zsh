# AGET Shell Integration
# Version: 1.0.0
# Source: aget-framework/aget/shell/aget.zsh
#
# Shell-native orchestration layer for CLI agents.
# See: aget/docs/SHELL_INTEGRATION.md
#
# Installation:
#   mkdir -p ~/.aget
#   cp aget/shell/*.zsh ~/.aget/
#   echo 'source ~/.aget/aget.zsh' >> ~/.zshrc
#
# Usage:
#   aget <directory> [focus topic...]
#   supervisor "fix the bug"
#   AGET_CLI=gemini supervisor "fix the bug"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Default CLI (override with: export AGET_CLI=codex)
: ${AGET_CLI:=claude}

# AGET home directory
: ${AGET_HOME:=~/.aget}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Load Profiles
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Source profiles from same directory as this file, or from AGET_HOME
_aget_script_dir="${0:A:h}"
if [[ -f "$_aget_script_dir/profiles.zsh" ]]; then
  source "$_aget_script_dir/profiles.zsh"
elif [[ -f "$AGET_HOME/profiles.zsh" ]]; then
  source "$AGET_HOME/profiles.zsh"
else
  echo "WARN: profiles.zsh not found" >&2
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Core Function: aget
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Usage: aget <directory> [focus topic...]
#
# Changes to the agent's directory and launches the configured CLI
# with the appropriate wake-up prompt.
#
# Examples:
#   aget ~/github/my-supervisor-agent
#   aget ~/github/my-supervisor-agent "fix the authentication bug"
#   AGET_CLI=gemini aget ~/github/my-agent "review the PR"
#
aget() {
  local dir="$1"
  shift
  local focus="$*"

  # Validate arguments
  if [[ -z "$dir" ]]; then
    echo "Usage: aget <directory> [focus topic...]" >&2
    echo "       AGET_CLI=$AGET_CLI" >&2
    return 1
  fi

  # Expand and validate directory
  dir="${dir/#\~/$HOME}"
  if [[ ! -d "$dir" ]]; then
    echo "ERROR: Directory not found: $dir" >&2
    return 1
  fi

  # Change to agent directory
  cd "$dir" || {
    echo "ERROR: Cannot cd to $dir" >&2
    return 1
  }

  # Warn if no AGENTS.md (agent may not be properly configured)
  if [[ ! -f AGENTS.md ]]; then
    echo "WARN: No AGENTS.md in $(pwd)" >&2
    echo "      Agent may not have proper context." >&2
  fi

  # Dispatch to CLI profile
  case "$AGET_CLI" in
    claude)      _aget_claude "$focus" ;;
    claude-plan) _aget_claude_plan "$focus" ;;
    codex)       _aget_codex "$focus" ;;
    gemini)      _aget_gemini "$focus" ;;
    aider)       _aget_aider "$focus" ;;
    cursor)      _aget_cursor "$focus" ;;
    *)
      echo "ERROR: Unknown CLI '$AGET_CLI'" >&2
      echo "Available: claude, claude-plan, codex, gemini, aider" >&2
      return 1
      ;;
  esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Selectors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Quick commands to switch the default CLI for the session.
# The change persists until you close the terminal or switch again.
#

alias use-claude='export AGET_CLI=claude && echo "AGET CLI: claude"'
alias use-claude-plan='export AGET_CLI=claude-plan && echo "AGET CLI: claude-plan (read-only)"'
alias use-codex='export AGET_CLI=codex && echo "AGET CLI: codex"'
alias use-gemini='export AGET_CLI=gemini && echo "AGET CLI: gemini"'
alias use-aider='export AGET_CLI=aider && echo "AGET CLI: aider"'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Status & Help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

aget-status() {
  echo "AGET Shell Integration v1.0.0"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Current CLI:  $AGET_CLI"
  echo "AGET_HOME:    $AGET_HOME"
  echo ""
  echo "Available CLIs:"
  echo "  claude       Claude Code (default)"
  echo "  claude-plan  Claude Code read-only mode"
  echo "  codex        Codex CLI (OpenAI)"
  echo "  gemini       Gemini CLI (Google)"
  echo "  aider        Aider (interactive)"
  echo ""
  echo "Switch CLI:   use-claude | use-codex | use-gemini | use-aider"
  echo "One-off:      AGET_CLI=gemini supervisor \"task\""
  echo ""

  # Count defined agent aliases
  local agent_count=$(alias | grep -c "='aget " 2>/dev/null || echo "0")
  echo "Agent aliases defined: $agent_count"
}

aget-help() {
  cat << 'EOF'
AGET Shell Integration
━━━━━━━━━━━━━━━━━━━━━━

USAGE
  aget <directory> [focus topic...]

EXAMPLES
  aget ~/github/my-supervisor-agent
  aget ~/github/my-supervisor-agent "fix the authentication bug"
  AGET_CLI=gemini aget ~/github/my-agent "review the PR"

With agent aliases:
  supervisor                     # Simple wake-up
  supervisor "fix the bug"       # Wake-up with focus topic
  AGET_CLI=codex supervisor      # Use different CLI

CLI SELECTION
  use-claude       Switch to Claude Code
  use-claude-plan  Switch to Claude Code read-only mode
  use-codex        Switch to Codex CLI
  use-gemini       Switch to Gemini CLI
  use-aider        Switch to Aider

CONFIGURATION
  AGET_CLI         Current CLI (default: claude)
  AGET_HOME        Config directory (default: ~/.aget)
  AGET_CLAUDE_BIN  Path to claude binary
  AGET_CODEX_BIN   Path to codex binary
  AGET_GEMINI_BIN  Path to gemini binary
  AGET_AIDER_BIN   Path to aider binary

FILES
  ~/.aget/aget.zsh         Core integration (this file)
  ~/.aget/profiles.zsh     CLI profile functions
  ~/.aget/agents.zsh       Your agent aliases
  ~/.aget/profiles_local.zsh  Your custom profiles (optional)

MORE INFO
  aget-status              Show current configuration
  https://github.com/aget-framework/aget/blob/main/docs/SHELL_INTEGRATION.md
EOF
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Load User Agent Aliases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Source user's agent aliases if they exist
[[ -f "$AGET_HOME/agents.zsh" ]] && source "$AGET_HOME/agents.zsh"
