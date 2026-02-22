# AGET Adoption Guide

**Version**: 3.5.0
**Last Updated**: 2026-02-14
**Audience**: External users and fleets adopting AGET

---

## Overview

This guide covers:
1. **New Adoption** — Starting fresh with AGET v3.5.0
2. **Migration** — Upgrading from v3.4.x to v3.5.0
3. **Fleet Adoption** — Deploying AGET across multiple agents
4. **Customization** — Extending archetypes for your domain

---

## Part 1: New Adoption

### Quick Start

1. **Choose archetype** based on use case (see [GETTING_STARTED.md](GETTING_STARTED.md))
2. **Clone template**:
   ```bash
   gh repo clone aget-framework/template-{archetype}-aget my-agent
   ```
3. **Configure identity** in `.aget/version.json`
4. **Run tests**:
   ```bash
   python3 -m pytest tests/ -v
   ```
5. **Start using** with your CLI tool (Claude Code, Codex CLI, Gemini CLI, etc.)

### What You Get

| Component | Description |
|-----------|-------------|
| `.aget/` | Agent configuration and evolution tracking |
| `ontology/` | Domain concepts for your archetype |
| `.claude/skills/` | 14 universal + 2-3 archetype skills |
| `tests/` | Contract tests for validation |
| `AGENTS.md` / `CLAUDE.md` | CLI tool configuration |

---

## Part 2: Migration from v3.4.x

### Overview

v3.5.0 adds:
- **Archetype ontologies** (`ontology/ONTOLOGY_{archetype}.yaml`)
- **Archetype skills** (2-3 specialized skills per archetype)
- **Updated SOPs** (SOP_aget_create v2.2.0, SOP_aget_migrate v1.2.0)

### Migration Steps

#### Step 1: Backup

```bash
cd your-agent
git stash  # or commit pending changes
```

#### Step 2: Update Version

Edit `.aget/version.json`:

```json
{
  "aget_version": "3.5.0",
  "archetype": "{your-archetype}"
}
```

#### Step 3: Add Ontology Directory

```bash
mkdir -p ontology

# Copy ontology from template
ARCHETYPE=$(jq -r '.archetype' .aget/version.json)
curl -sL "https://raw.githubusercontent.com/aget-framework/template-${ARCHETYPE}-aget/main/ontology/ONTOLOGY_${ARCHETYPE}.yaml" \
  -o "ontology/ONTOLOGY_${ARCHETYPE}.yaml"
```

#### Step 4: Add Archetype Skills

```bash
ARCHETYPE=$(jq -r '.archetype' .aget/version.json)
TEMPLATE_URL="https://github.com/aget-framework/template-${ARCHETYPE}-aget"

# Clone template temporarily
git clone --depth 1 "$TEMPLATE_URL" /tmp/template-${ARCHETYPE}

# Copy archetype-specific skills
for skill in /tmp/template-${ARCHETYPE}/.claude/skills/aget-*/; do
  skill_name=$(basename "$skill")
  if [ ! -d ".claude/skills/${skill_name}" ]; then
    cp -r "$skill" .claude/skills/
    echo "Added: ${skill_name}"
  fi
done

# Cleanup
rm -rf /tmp/template-${ARCHETYPE}
```

#### Step 5: Validate

```bash
# Check ontology
ls ontology/ONTOLOGY_*.yaml

# Check skill count (should be 16-17)
ls .claude/skills/aget-*/SKILL.md | wc -l

# Run tests
python3 -m pytest tests/ -v
```

#### Step 6: Update Migration History

Edit `.aget/version.json` to add migration entry:

```json
{
  "migration_history": [
    "...",
    "v3.4.0 -> v3.5.0: 2026-02-14"
  ]
}
```

### Migration Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Version updated | `jq '.aget_version' .aget/version.json` | `"3.5.0"` |
| Archetype set | `jq '.archetype' .aget/version.json` | Your archetype |
| Ontology exists | `ls ontology/ONTOLOGY_*.yaml` | 1 file |
| Skills deployed | `ls .claude/skills/aget-*/SKILL.md \| wc -l` | 16-17 |
| Tests pass | `pytest tests/ -v` | All pass |

---

## Part 3: Fleet Adoption

### Overview

For organizations deploying multiple AGET agents:

```
Organization Fleet
├── supervisor-agent (supervisor archetype)
│   ├── worker-1 (worker archetype)
│   ├── worker-2 (worker archetype)
│   ├── developer-1 (developer archetype)
│   └── analyst-1 (analyst archetype)
```

### Fleet Setup

#### Step 1: Designate Supervisor

Create a supervisor agent first:

```bash
gh repo clone aget-framework/template-supervisor-aget fleet-supervisor
```

Configure as your fleet coordinator.

#### Step 2: Create Worker Agents

For each team member/function:

```bash
# Development team
gh repo clone aget-framework/template-developer-aget dev-agent-1
gh repo clone aget-framework/template-developer-aget dev-agent-2

# Analysis team
gh repo clone aget-framework/template-analyst-aget analyst-agent-1

# General workers
gh repo clone aget-framework/template-worker-aget worker-agent-1
```

#### Step 3: Fleet Configuration

In each agent's `.aget/version.json`, set fleet reference:

```json
{
  "fleet": {
    "supervisor": "fleet-supervisor",
    "position": "worker"
  }
}
```

### Fleet Coordination Patterns

| Pattern | Use Case | Supervisor Skill |
|---------|----------|------------------|
| Broadcast | Announce to all agents | `aget-broadcast-fleet` |
| Review | Assess agent work | `aget-review-agent` |
| Escalate | Elevate issues | `aget-escalate-issue` |

---

## Part 4: Customization

### Extending Ontology

Add domain-specific concepts to `ontology/ONTOLOGY_{archetype}.yaml`:

```yaml
# Example: Adding legal domain concepts to advisor ontology
concepts:
  - id: C100
    prefLabel: Legal_Case
    definition: A legal matter being analyzed
    category: domain_extension

  - id: C101
    prefLabel: Contract_Clause
    definition: A specific provision within a contract
    category: domain_extension
```

### Creating Custom Skills

1. **Create directory**:
   ```bash
   mkdir -p .claude/skills/aget-my-custom-skill
   ```

2. **Create SKILL.md**:
   ```markdown
   ---
   name: aget-my-custom-skill
   description: Description of what this skill does
   archetype: your-archetype
   allowed-tools:
     - Read
     - Glob
   ---

   # /aget-my-custom-skill

   Description of the skill...

   ## Instructions

   1. Step one...
   2. Step two...

   ## Constraints

   - **C1**: NEVER do X
   - **C2**: ALWAYS do Y
   ```

3. **Test the skill** by invoking `/aget-my-custom-skill` in your CLI tool.

### Customization Guidelines

| Guideline | Rationale |
|-----------|-----------|
| Extend ontology, don't replace | Preserves archetype foundation |
| Follow S-V-O skill naming | Consistency with framework |
| Use prohibitive constraints | Clear boundaries (NEVER/ALWAYS) |
| Add domain-specific concepts | Specialize for your work |

---

## Support

### Documentation

- [GETTING_STARTED.md](GETTING_STARTED.md) — Quick start
- [README.md](README.md) — Overview
- [specs/](specs/) — Framework specifications
- [docs/](docs/) — Detailed guides

### Community

- **Issues**: [aget-framework/aget](https://github.com/aget-framework/aget/issues)
- **Discussions**: GitHub Discussions
- **Releases**: [aget-framework/aget/releases](https://github.com/aget-framework/aget/releases)

### Issue Filing

When filing issues:
1. Use appropriate template (bug, feature, enhancement)
2. Include version (`jq '.aget_version' .aget/version.json`)
3. Include archetype (`jq '.archetype' .aget/version.json`)
4. Describe expected vs actual behavior

---

## Changelog

### v3.5.0 (2026-02-14)

- **Archetype Customization**: 12 archetype ontologies, 26 archetype skills
- **Skill Framework**: 40 total skills (14 universal + 26 archetype)
- **Ontology-Driven Creation**: Vocabulary → Specification → Instance pattern
- **SOP Updates**: SOP_aget_create v2.2.0, SOP_aget_migrate v1.2.0

---

*ADOPTION_GUIDE.md — External adoption guide for AGET v3.5.0*
