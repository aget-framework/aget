# AGET Adoption Guide

**Version**: 3.15.0
**Last Updated**: 2026-04-26
**Audience**: External users and fleets adopting AGET

---

## Overview

This guide covers:
1. **New Adoption** — Starting fresh with AGET v3.15.0
2. **Migration** — Upgrading to v3.15.0 (including breaking changes)
3. **Fleet Adoption** — Deploying AGET across multiple agents
4. **Customization** — Extending archetypes for your domain

---

## Listen to the Introduction

New to AGET? Start with the audio introduction — a narrated walkthrough covering session rhythm, key skills, fleet creation, and the knowledge base.

- **Audio briefing**: [AGET Intro: Memory and Mission for CLI AI Agents](https://youtu.be/zLSFeT9TF8E)
- **Channel**: [@AGETFramework on YouTube](https://www.youtube.com/@AGETFramework)

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
| `.claude/skills/` | 32 universal + 4-6 archetype skills |
| `tests/` | Contract tests for validation |
| `AGENTS.md` / `CLAUDE.md` | CLI tool configuration |

---

## Part 2: Migration to v3.15.0

### Breaking Changes

v3.15.0 includes two breaking changes. Read carefully before upgrading.

#### BC-001: Backward-Compatibility Shim Removed

The shim that allowed code to read legacy field names (e.g., `aget_agent_name`, `aget_instance_type`) from `version.json` has been removed. Code that accessed `aget_`-prefixed field names via this shim must be updated to read the canonical field names directly.

**Detection**: Search your scripts and patterns for usages:
```bash
grep -r "aget_agent_name\|aget_instance_type\|aget_archetype" scripts/ .aget/patterns/
```

**Fix**: Update to use canonical field names (e.g., `agent_name`, `instance_type`, `archetype`).

> **Scope clarification**: The `version.json` field names themselves are NOT renamed. Only the removed shim is affected.

#### BC-002: See Release Notes

See [releases/v3.15.0](https://github.com/aget-framework/aget/releases/tag/v3.15.0) and [docs/BREAKING_CHANGES_v3.15.md](docs/BREAKING_CHANGES_v3.15.md) for full BC-002 details.

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
  "aget_version": "3.15.0",
  "archetype": "{your-archetype}"
}
```

#### Step 3: Remediate BC-001 (if applicable)

```bash
# Check whether any scripts use the removed shim
grep -r "aget_agent_name\|aget_instance_type" scripts/ .aget/patterns/ || echo "No BC-001 impact"
```

#### Step 4: Verify Skills

```bash
# Conformant templates have 32 universal skills
ls .claude/skills/ | wc -l
# If fewer than 32, run your template's upgrade script or re-clone from current template
```

#### Step 5: Run Tests

```bash
python3 -m pytest tests/ -v
```

### Migration Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Version updated | `jq '.aget_version' .aget/version.json` | `"3.15.0"` |
| Archetype set | `jq '.archetype' .aget/version.json` | Your archetype |
| Ontology exists | `ls ontology/ONTOLOGY_*.yaml` | 1 file |
| BC-001 clean | `grep -r "aget_agent_name" scripts/ .aget/` | No matches |
| Tests pass | `pytest tests/ -v` | All pass |

---

## Part 3: Fleet Adoption

### Minimum Viable Fleet (MVF)

Choose the fleet size that fits your situation:

| Level | Composition | Setup Time | When to Use |
|-------|-------------|:----------:|-------------|
| **MVF-0** | 1 agent, no supervisor | ~30 min | Solo practitioner, evaluating AGET |
| **MVF-1** | 1 supervisor + 1 worker | ~1 hr | Coordinated pair, getting started |
| **MVF-2** | 1 supervisor + 2-4 workers | ~2-3 hr | Small team, mixed archetypes |
| **MVF-3** | Full fleet with registry | Half day | Production fleet, organization-wide |

**Recommendation for new users**: Start at MVF-0 or MVF-1. The supervisor template includes `aget-create-aget` for spinning up new agents on demand.

### MVF-0: Solo Agent (30 minutes)

```bash
# 1. Clone any single template
gh repo clone aget-framework/template-worker-aget my-agent
cd my-agent

# 2. Configure identity
# Edit .aget/version.json: set agent_name, domain

# 3. Verify
python3 -m pytest tests/ -v

# 4. Start
# Open in Claude Code (or your CLI tool) and say: "wake up"
```

No supervisor needed. The agent accumulates knowledge independently across sessions.

### MVF-1: Supervisor + One Worker (1 hour)

```bash
# Step 1: Create supervisor first
gh repo clone aget-framework/template-supervisor-aget my-supervisor
cd my-supervisor
# Edit .aget/version.json: agent_name = "my-supervisor", domain = "coordination"

# Step 2: In your supervisor session, create a worker
# Tell your supervisor agent: "/aget-create-aget worker my-worker"
# The supervisor handles cloning, identity setup, and fleet registration

# Step 3: Verify fleet health
# Tell your supervisor: "health check"
```

### Fleet Structure

```
Fleet
├── my-supervisor (supervisor archetype)        ← creates and coordinates
│   ├── my-worker-1 (worker archetype)
│   ├── my-developer (developer archetype)
│   └── my-researcher (researcher archetype)
```

### Fleet Configuration

In each worker agent's `.aget/version.json`, the `managed_by` field identifies the supervisor:

```json
{
  "agent_name": "my-worker-aget",
  "instance_type": "aget",
  "archetype": "worker",
  "managed_by": "my-supervisor"
}
```

The supervisor sets `"managed_by": "none"` (top-level) or references its own parent supervisor.

### Fleet Coordination Patterns

| Pattern | Use Case | Supervisor Skill |
|---------|----------|------------------|
| Create agent | Spin up a new agent from template | `aget-create-aget` |
| Broadcast | Announce to all agents | `aget-broadcast-fleet` |
| Review agent | Assess agent work quality | `aget-review-agent` |
| Escalate issue | Elevate issues up the chain | `aget-escalate-issue` |
| Fleet health | Check all agents are healthy | `aget-check-fleet` |

### Fleet Repository Strategy

| Strategy | When to Use | Trade-off |
|----------|-------------|-----------|
| One repo per agent | Most fleets | Simple; each agent has full history |
| Monorepo | Tightly-coupled teams | Easy cross-agent search; harder isolation |
| Org account | Public or shared fleet | Visibility; requires GitHub org |
| Personal repos | Individual practitioner | Simple start; less visible |

---

## Part 4: Customization

### Extending Ontology

Add domain-specific concepts to `ontology/ONTOLOGY_{archetype}.yaml`:

```yaml
# Example: Adding research domain concepts to advisor ontology
concepts:
  - id: C100
    prefLabel: Research_Study
    definition: A research investigation being analyzed
    category: domain_extension

  - id: C101
    prefLabel: Finding
    definition: A specific conclusion supported by evidence
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

### v3.15.0 (2026-04-18)

- **Breaking: BC-001** — Backward-compatibility shim for legacy `aget_`-prefixed field names removed; see migration guide above
- **Breaking: BC-002** — See [docs/BREAKING_CHANGES_v3.15.md](docs/BREAKING_CHANGES_v3.15.md)
- **Universal Skills**: 32 skills per conformant template (up from 15)
- **Security Spec**: AGET_SECURITY_SPEC v0.2 (8 security capabilities)
- **Budget Grammar**: AGET_BUDGET_GRAMMAR_SPEC v0.2 (4 capabilities)
- **Fleet**: 34/34 agents confirmed at v3.15.0

### v3.14.0 (2026-03-xx)

- **Requirements Publication**: First public R-* requirements documents
- **Template**: 13th archetype added (document-processor)
- **Spec scoring**: averaged across 38+ specifications

### v3.13.0 (2026-03-xx)

- **Alias normalization**: Short-name identity layer (`aget_short_name` in version.json)
- **`aget_` prefix**: All version.json fields normalized (19 renames)
- **Triad pilot**: Release Builder/Auditor/Critic (SKILL-012/013/014) formal pilot

### v3.5.0 (2026-02-14)

- **Archetype Customization**: 12 archetype ontologies, 26 archetype skills
- **Skill Framework**: 44 total skills (15 universal + 29 archetype)
- **Ontology-Driven Creation**: Vocabulary → Specification → Instance pattern
- **SOP Updates**: SOP_aget_create v2.2.0, SOP_aget_migrate v1.2.0

---

*ADOPTION_GUIDE.md — External adoption guide for AGET v3.15.0*
