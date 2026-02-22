# Getting Started with AGET

**Version**: 3.5.0
**Last Updated**: 2026-02-14

---

## Overview

AGET is a configuration and lifecycle management framework for CLI-based human-AI collaborative work. This guide helps you choose the right template and get started quickly.

---

## Step 1: Choose Your Archetype

AGET provides **12 archetypes**, each with specialized skills and domain concepts.

### Archetype Selection Guide

| If you need to... | Choose | Key Skills |
|-------------------|--------|------------|
| Execute tasks, track progress | **worker** | execute-task, report-progress |
| Coordinate multiple agents | **supervisor** | broadcast-fleet, review-agent, escalate-issue |
| Write, test, review code | **developer** | run-tests, lint-code, review-pr |
| Provide guidance with personas | **advisor** | assess-risk, recommend-action |
| Run strategic engagements | **consultant** | assess-client, propose-engagement |
| Analyze data, generate reports | **analyst** | analyze-data, generate-report |
| Design systems, evaluate tradeoffs | **architect** | design-architecture, assess-tradeoffs |
| Research topics, document findings | **researcher** | search-literature, document-finding |
| Handle incidents, run playbooks | **operator** | handle-incident, run-playbook |
| Make decisions, review budgets | **executive** | make-decision, review-budget |
| Review artifacts, provide feedback | **reviewer** | review-artifact, provide-feedback |
| Write specifications, validate requirements | **spec-engineer** | validate-spec, generate-requirement |

### Decision Tree

```
Start Here
    │
    ├── Managing other agents? → supervisor
    │
    ├── Writing code? → developer
    │
    ├── Providing guidance?
    │   ├── With personas → advisor
    │   └── For clients → consultant
    │
    ├── Analyzing information?
    │   ├── Data-focused → analyst
    │   └── Research-focused → researcher
    │
    ├── Designing systems? → architect
    │
    ├── Operations/incidents? → operator
    │
    ├── Making executive decisions? → executive
    │
    ├── Reviewing work? → reviewer
    │
    ├── Writing specifications? → spec-engineer
    │
    └── General tasks? → worker
```

---

## Step 2: Clone Your Template

```bash
# Replace {archetype} with your choice from Step 1
gh repo clone aget-framework/template-{archetype}-aget my-agent-name
cd my-agent-name
```

### Examples

```bash
# For a development assistant
gh repo clone aget-framework/template-developer-aget my-dev-assistant

# For a research agent
gh repo clone aget-framework/template-researcher-aget my-research-agent

# For a task executor
gh repo clone aget-framework/template-worker-aget my-worker-agent
```

---

## Step 3: Configure Identity

Edit `.aget/version.json`:

```json
{
  "agent_name": "my-agent-name",
  "aget_version": "3.5.0",
  "instance_type": "AGET",
  "archetype": "developer",
  "domain": "your-domain-here",
  "template": "developer",
  "created": "2026-02-14"
}
```

### Key Fields

| Field | Description | Example |
|-------|-------------|---------|
| `agent_name` | Your agent's name | `my-legal-assistant` |
| `instance_type` | `AGET` (action) or `aget` (advisory) | `AGET` |
| `archetype` | From Step 1 | `developer` |
| `domain` | Your work domain | `legal_contract_analysis` |

---

## Step 4: Verify Setup

Run contract tests to verify your agent is correctly configured:

```bash
python3 -m pytest tests/ -v
```

All tests should pass before using your agent.

---

## Step 5: Start Using

### With Claude Code

```bash
cd my-agent-name
claude code .
```

### With Codex CLI

```bash
cd my-agent-name
codex
```

### With Gemini CLI

```bash
cd my-agent-name
gemini
```

### With Cursor (Experimental — not validated)

```bash
cd my-agent-name
cursor .
```

### With Aider (Experimental — not validated)

```bash
cd my-agent-name
aider
```

---

## Session Protocols

Once your agent is running, use these commands:

| Command | Purpose |
|---------|---------|
| `wake up` | Start session, load context |
| `study up [topic]` | Research a specific topic |
| `step back` | Review KB before proposing changes |
| `sanity check` | Verify agent health |
| `wind down` | End session, create handoff |

---

## What's Included

### Universal Skills (14)

All templates include these skills:
- `aget-wake-up` — Session initialization
- `aget-wind-down` — Session closure
- `aget-check-health` — Health inspection
- `aget-studyup` — KB research
- `aget-record-lesson` — Capture learnings
- `aget-create-project` — Project scaffolding
- `aget-review-project` — Project assessment
- `aget-save-state` — State persistence
- `aget-propose-skill` — Skill governance
- `aget-capture-observation` — Research capture
- `aget-check-sessions` — Session health
- `aget-check-evolution` — Evolution health
- `aget-check-kb` — KB health

### Archetype Skills (2-3 per archetype)

Each archetype includes specialized skills. See the [archetype capability matrix](README.md#templates) for details.

### Archetype Ontology

Each template includes `ontology/ONTOLOGY_{archetype}.yaml` with domain concepts specific to that archetype (5-10 concepts per archetype).

---

## Next Steps

1. **Customize ontology**: Add domain-specific concepts to `ontology/ONTOLOGY_{archetype}.yaml`
2. **Add skills**: Create custom skills in `.claude/skills/`
3. **Configure AGENTS.md**: Set up CLI agent integration
4. **Run first session**: Use `wake up` to start

---

## Migration from v3.4.x

If upgrading from v3.4.x:

```bash
# Check current version
cat .aget/version.json | jq '.aget_version'

# Update version
# Edit .aget/version.json: set aget_version to "3.5.0"

# Verify ontology exists
ls ontology/ONTOLOGY_*.yaml

# Verify archetype skills exist
ls .claude/skills/aget-*/SKILL.md | wc -l
# Should be 16-17 (14 universal + 2-3 archetype)

# Run validation
python3 -m pytest tests/ -v
```

See [ADOPTION_GUIDE.md](ADOPTION_GUIDE.md) for detailed migration instructions.

---

## Support

- **Issues**: [aget-framework/aget](https://github.com/aget-framework/aget/issues)
- **Documentation**: [README.md](README.md)
- **Specifications**: [specs/](specs/)

---

*GETTING_STARTED.md — Quick start guide for AGET v3.5.0*
