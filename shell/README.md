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

## Template Shell Profiles (v3.3.0)

Each AGET template includes a `shell/` directory with agent-specific profiles.

### Template Profile Requirements

Template profiles (`{type}_profile.zsh`) SHALL include:

| Requirement | Purpose |
|-------------|---------|
| Header documentation | Paths to README, Spec, Vocabulary |
| `AGET_AGENT_DIR` | Portability across installations |
| Derived paths | AGET_SPEC, AGET_VOCAB, AGET_CONFIG, etc. |
| `aget_info()` | Display all documentation paths |
| `aget_docs()` | Open documentation files |
| Customization notes | Guide for instantiation |

### Example Usage

```bash
# Source template profile
export AGET_AGENT_DIR="/path/to/my-agent"
source shell/worker_profile.zsh

# View documentation paths
aget_info

# Open spec file
aget_docs spec
```

### Template Profile Locations

| Template | Profile |
|----------|---------|
| template-supervisor-aget | `shell/supervisor_profile.zsh` |
| template-worker-aget | `shell/worker_profile.zsh` |
| template-advisor-aget | `shell/advisor_profile.zsh` |
| template-consultant-aget | `shell/consultant_profile.zsh` |
| template-developer-aget | `shell/developer_profile.zsh` |
| template-spec-engineer-aget | `shell/spec_engineer_profile.zsh` |
| template-analyst-aget | `shell/analyst_profile.zsh` |
| template-architect-aget | `shell/architect_profile.zsh` |
| template-researcher-aget | `shell/researcher_profile.zsh` |

## Documentation

See [SHELL_INTEGRATION.md](../docs/SHELL_INTEGRATION.md) for full setup guide.

## Related

- L452: Shell Orchestration Pattern
- L189: Credential Isolation Pattern
- AGET_TEMPLATE_SPEC.md (CAP-TPL-014: Shell Integration)
- `scripts/generate_agents_zsh.py`: Generate aliases from fleet inventory
