# AGET Shell Integration

Shell-native orchestration layer for CLI agents.

## Files

| File | Purpose |
|------|---------|
| `aget.zsh` | Core `aget()` function and CLI selectors |
| `profiles.zsh` | CLI-specific invocation functions |

## Installation

```bash
# Copy to your home
mkdir -p ~/.aget
cp *.zsh ~/.aget/

# Add to .zshrc
echo 'source ~/.aget/aget.zsh' >> ~/.zshrc

# Create your agent aliases in ~/.aget/agents.zsh
```

## Documentation

See [SHELL_INTEGRATION.md](../docs/SHELL_INTEGRATION.md) for full setup guide.

## Related

- L452: Shell Orchestration Pattern
- L189: Credential Isolation Pattern
- `scripts/generate_agents_zsh.py`: Generate aliases from fleet inventory
