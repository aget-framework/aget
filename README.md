# AGET Framework

[![Latest Release](https://img.shields.io/github/v/release/aget-framework/aget?style=flat-square)](https://github.com/aget-framework/aget/releases/latest)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=flat-square)](LICENSE)

> Persistent domain intelligence for governed agentic work

## The Problem

Your CLI agents lose context between sessions. Knowledge resets daily. Agents in the same fleet can't learn from each other. You have no confidence that what worked yesterday still works today.

AGET fixes this. It gives your agents persistent knowledge, shared memory, fleet coordination, and human-supervised governance. Your agents accumulate domain expertise that compounds across sessions.

## Quick Start

Start with the [Supervisor template](https://github.com/aget-framework/template-supervisor-aget). It coordinates your fleet and can create new agents.

```bash
# 1. Clone the supervisor template
git clone https://github.com/aget-framework/template-supervisor-aget my-supervisor

# 2. Open in your CLI agent (Claude Code, Codex CLI, or Gemini CLI)
cd my-supervisor

# 3. Start your first session
# Tell your agent: "wake up"

# 4. Create a new agent from a template
# Tell your agent: "/aget-create-aget worker my-first-worker"
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for the full supervisor-first workflow.

## Key Features

- **Persistent Knowledge**: Agents accumulate expertise across sessions ([L-docs](https://github.com/aget-framework/aget/tree/main/docs), [evolution/](https://github.com/aget-framework/aget/tree/main/.aget/evolution))
- **Shared Memory**: KB as collaboration substrate, not hidden AI state ([MEMORY_VISION](https://github.com/aget-framework/aget/blob/main/docs/MEMORY_VISION.md))
- **Requirements-Driven**: Human-level requirements ground testable specifications ([requirements/](https://github.com/aget-framework/aget/tree/main/requirements))
- **Gate Discipline**: Explicit decision points with human approval ([GOVERNANCE_PRINCIPLES](https://github.com/aget-framework/aget/blob/main/governance/GOVERNANCE_PRINCIPLES.md))
- **Fleet Coordination**: Multi-agent patterns with clear authority boundaries
- **Evidence-First**: Audit before architecture. Validate before shipping.

## Supported Platforms

| Platform | Status | Integration |
|----------|--------|-------------|
| **Claude Code** | Baseline | `CLAUDE.md`, `.claude/` |
| **Codex CLI** | Compatible | `AGENTS.md`, `.codex/` |
| **Gemini CLI** | Compatible | `AGENTS.md` |
| Cursor | Experimental | `.cursor/rules` |
| Aider | Experimental | `CONVENTIONS.md` |

See [CLI Support Matrix](docs/AGET_CLI_SUPPORT_MATRIX.md) for details.

## What AGET is NOT

- **Not an AI model or runtime.** AGET is a governance layer that works with any LLM backend.
- **Not a replacement for Claude Code or Codex CLI.** AGET sits above these platforms.
- **Not an autonomous system.** AGET requires human supervision and gate discipline.
- **Not coding-only.** AGET supports advisory, consulting, research, and general knowledge work.

## Templates

12 archetypes, each with specialized skills and formal ontology:

| Template | Use Case |
|----------|----------|
| [**template-supervisor-aget**](https://github.com/aget-framework/template-supervisor-aget) | Fleet coordination (**start here**) |
| [template-worker-aget](https://github.com/aget-framework/template-worker-aget) | Task execution |
| [template-developer-aget](https://github.com/aget-framework/template-developer-aget) | Development workflows |
| [template-advisor-aget](https://github.com/aget-framework/template-advisor-aget) | Advisory with personas |
| [template-analyst-aget](https://github.com/aget-framework/template-analyst-aget) | Data analysis |
| [template-architect-aget](https://github.com/aget-framework/template-architect-aget) | System design |
| [template-researcher-aget](https://github.com/aget-framework/template-researcher-aget) | Research workflows |
| [template-consultant-aget](https://github.com/aget-framework/template-consultant-aget) | Consulting engagements |
| [template-operator-aget](https://github.com/aget-framework/template-operator-aget) | Operations/DevOps |
| [template-executive-aget](https://github.com/aget-framework/template-executive-aget) | Executive advisory |
| [template-reviewer-aget](https://github.com/aget-framework/template-reviewer-aget) | Quality review |
| [template-spec-engineer-aget](https://github.com/aget-framework/template-spec-engineer-aget) | Specification authoring |

All templates include 15 universal skills. See [Archetype Ecosystem](docs/ARCHETYPE_ECOSYSTEM.md) for details.

## Session Protocols

| Command | What it does |
|---------|-------------|
| `wake up` | Initialize session, load context |
| `study up [topic]` | Research a topic across the KB |
| `health check` | Verify agent health |
| `wind down` | End session, create handoff |

## Learn More

- [Strategic Context](docs/STRATEGIC_CONTEXT.md): The governed agent paradigm
- [Ontology-Driven Design](docs/ONTOLOGY_DESIGN.md): Vocabulary-first agent customization
- [Philosophy](docs/COMPOSITION_GUIDE.md): Human-AI collaboration quality over autonomous speed

## Contributing

Contributions welcome. See the [Issues page](https://github.com/aget-framework/aget/issues) to report bugs or suggest features.

## License

Apache License 2.0. See [LICENSE](LICENSE).
