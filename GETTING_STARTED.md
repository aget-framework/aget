# Getting Started with AGET

**Version**: 3.15.0
**Last Updated**: 2026-04-26

---

## Overview

AGET is a configuration and lifecycle management framework for CLI-based human-AI collaborative work. This guide helps you choose the right template and get started quickly.

---

## Step 1: Choose Your Archetype

AGET provides **12 archetypes**, each with specialized skills and domain concepts.

### Archetype Selection Guide

| If you need to... | Choose | Key Skills | Evidence |
|-------------------|--------|------------|----------|
| Execute tasks, track progress | **worker** | execute-task, report-progress | Demonstrated |
| Coordinate multiple agents | **supervisor** | broadcast-fleet, review-agent, escalate-issue | Demonstrated |
| Write, test, review code | **developer** | run-tests, lint-code, review-pr | Demonstrated |
| Provide guidance with personas | **advisor** | assess-risk, recommend-action | Demonstrated |
| Run strategic engagements | **consultant** | assess-client, propose-engagement | Template |
| Analyze data, generate reports | **analyst** | analyze-data, generate-report | Template |
| Design systems, evaluate tradeoffs | **architect** | design-architecture, assess-tradeoffs | Template |
| Research topics, document findings | **researcher** | search-literature, document-finding | Demonstrated |
| Handle incidents, run playbooks | **operator** | handle-incident, run-playbook | Template |
| Make decisions, review budgets | **executive** | make-decision, review-budget | Template |
| Review artifacts, provide feedback | **reviewer** | review-artifact, provide-feedback | Template |
| Write specifications, validate requirements | **spec-engineer** | validate-spec, generate-requirement | Template |

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
  "aget_version": "3.15.0",
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
| `agent_name` | Your agent's name | `my-dev-assistant` |
| `instance_type` | `AGET` (action) or `aget` (advisory) | `AGET` |
| `archetype` | From Step 1 | `developer` |
| `domain` | Your work domain | `code_quality` |

---

## Step 4: Verify Setup

Run contract tests to verify your agent is correctly configured:

```bash
python3 -m pytest tests/ -v
```

All tests should pass before using your agent.

---

## Step 5: Terminal Emulator Considerations

Your terminal emulator choice affects your AI CLI tool experience. AGET is terminal-agnostic, but the CLI tools underneath are not.

| Feature | Why It Matters |
|---------|---------------|
| **GPU-accelerated rendering** | AI CLI tools generate high volumes of terminal output; non-GPU terminals may flicker or scroll uncontrollably |
| **24-bit truecolor** | Diffs, syntax highlighting, and status indicators require full color support |
| **Multi-line input (Shift+Enter)** | Essential for writing multi-line prompts; native in iTerm2, WezTerm, Ghostty, Kitty |

Terminals with known smooth AI CLI experiences: **iTerm2** (macOS), **Ghostty** (macOS/Linux), **Kitty** (macOS/Linux), **WezTerm** (cross-platform). Check your CLI tool's documentation for terminal-specific configuration (e.g., Claude Code's `/terminal-setup` command).

---

## Step 6: Start Using

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

### Universal Skills (32)

All templates include these skills:

**Session lifecycle**
- `aget-wake-up` — Session initialization
- `aget-open-session` — Context-aware session open with recovery
- `aget-wind-down` — Session closure
- `aget-close-session` — Close session with pre-close triage and handoff
- `aget-save-state` — State persistence checkpoint
- `aget-describe-session` — Session narrative summary

**Knowledge base**
- `aget-study-topic` — KB research on a topic
- `aget-record-lesson` — Capture learnings as L-docs
- `aget-record-observation` — Record research observations
- `aget-process-observation` — Classify and route observations
- `aget-check-kb` — KB health validation
- `aget-check-evolution` — Evolution directory health
- `aget-check-sessions` — Session directory health

**Ontology**
- `aget-analyze-ontology` — Ontology health and coverage analysis
- `aget-expand-ontology` — Expand vocabularies with web-researched concepts

**Specifications and quality**
- `aget-enhance-spec` — 7-phase specification enhancement lifecycle
- `aget-create-rubric` — Create scoring rubrics
- `aget-check-facts` — Stratified 3-pass fact verification
- `aget-check-initiative` — Initiative coherence check
- `aget-enhance-health` — Remediate health drift

**Project management**
- `aget-create-project` — Governed project scaffolding
- `aget-review-project` — Project assessment
- `aget-propose-actions` — Ranked next-best actions with evidence

**Governance**
- `aget-propose-skill` — Skill governance and proposal
- `aget-create-skill` — Skill creation with spec
- `aget-file-issue` — Issue filing with private-first routing
- `aget-promote-issue` — Issue promotion to public repos

**Release**
- `aget-release-build` — Release build execution
- `aget-release-audit-specs` — Release specification audit
- `aget-release-critique` — Release critique from reviewer perspective

**Communication**
- `aget-create-briefing` — Generate narrative briefing documents

**Health**
- `aget-check-health` — Agent health inspection

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

## Supervisor-First Workflow

The recommended path for new users is to start with the **supervisor template** — it can coordinate a fleet and spin up new agents on demand.

```bash
# 1. Clone the supervisor template
git clone https://github.com/aget-framework/template-supervisor-aget my-supervisor
cd my-supervisor

# 2. Configure identity
# Edit .aget/version.json: set agent_name and domain

# 3. Run tests
python3 -m pytest tests/ -v

# 4. Open in your CLI tool and start the first session
# Tell your agent: "wake up"
```

Once the supervisor is running, create additional agents on demand:

```
# In your supervisor session:
/aget-create-aget worker my-task-runner
/aget-create-aget developer my-dev-assistant
/aget-create-aget researcher my-research-agent
```

The supervisor handles identity configuration, fleet registry, and handoff coordination automatically.

**Solo practitioner?** Skip the supervisor and clone any single template directly (Step 2 above). The supervisor adds value when you coordinate multiple agents.

---

## Migration from v3.14.x

If upgrading from v3.14.x to v3.15.0:

```bash
# Check current version
cat .aget/version.json | jq '.aget_version'

# Update version number
# Edit .aget/version.json: set aget_version to "3.15.0"

# BREAKING CHANGE BC-001: Backward-compatibility shim removed
# Code that reads aget_-prefixed field names via the removed shim must be updated
# Verify: grep -r "aget_agent_name\|aget_instance_type" scripts/ .aget/patterns/

# BREAKING CHANGE BC-002: See ADOPTION_GUIDE.md for full details

# Verify universal skills (32 expected for conformant templates)
ls .claude/skills/ | wc -l

# Run validation
python3 -m pytest tests/ -v
```

See [ADOPTION_GUIDE.md](ADOPTION_GUIDE.md) for detailed migration instructions and breaking change remediation.

---

## Support

- **Issues**: [aget-framework/aget](https://github.com/aget-framework/aget/issues)
- **Documentation**: [README.md](README.md)
- **Specifications**: [specs/](specs/)

---

*GETTING_STARTED.md — Quick start guide for AGET v3.15.0*
