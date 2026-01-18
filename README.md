# AGET Framework

> Configuration & lifecycle management for governed agentic work

## What is AGET?

AGET is a platform-agnostic governance framework for CLI-based human-AI
agentic work. It provides session continuity, shared memory architecture,
fleet coordination, and human-supervised autonomy patterns that work
across AI coding assistants including Claude Code, Cursor, Aider, and
Windsurf.

## Philosophy

**Human-AI collaboration quality over autonomous agent speed**

- **Governed Autonomy**: Agents act autonomously within explicit boundaries
- **Portable Memory**: Knowledge persists across sessions and platforms
- **Platform Agnostic**: Patterns work across CLI agent platforms
- **Human Oversight**: Humans remain decision authorities at key points
- **Evidence-First**: Design to reality, not theory

## What AGET is NOT

- **A specific AI model or runtime** — AGET is a governance layer that works with any LLM backend
- **A replacement for Claude Code, Cursor, or Aider** — AGET sits above these platforms as a governance substrate
- **An autonomous AI system** — AGET explicitly requires human supervision and gate discipline
- **A coding-only framework** — AGET supports advisory, consulting, supervision, and general knowledge work
- **A vendor lock-in solution** — Three-tier degradation ensures portability (gh → git → filesystem)

## Supported Platforms

AGET works across CLI agent platforms:

| Platform | Type | Integration |
|----------|------|-------------|
| Claude Code | CLI | `CLAUDE.md, .claude/` |
| Cursor | IDE | `.cursor/rules, .cursorrules` |
| Aider | CLI | `.aider.conf.yml, CONVENTIONS.md` |
| Windsurf | IDE | `TBD` |
| Codex CLI | CLI | `AGENTS.md, .codex/` |
| Gemini CLI | CLI | `Hooks (experimental)` |

## Key Features

- **Platform Portability**: Three-tier degradation ensures functionality across environments
- **Memory Architecture**: KB as shared collaboration substrate
- **Gate Discipline**: Explicit decision points with human approval
- **Fleet Patterns**: Multi-agent coordination with clear authority
- **Evidence-First Design**: Audit before architecture, validate before shipping
- **Theoretical Grounding**: Concepts mapped to established theory

## Strategic Context

| Era | Term | Scope |
|-----|------|-------|
| 2024 | **Coding Agent** | Domain-specific (code tasks) |
| 2025 | **CLI Agent** | Interface-specific (terminal-based) |
| 2026 | **Governed Agent** | Governance-centric (human-supervised autonomy) |

> The progression abstracts away from domain (coding) and interface (CLI)
to relationship (governed) and capability (autonomous work within bounds).

## Quick Start

1. Choose a template from [aget-framework](https://github.com/aget-framework)
2. Copy template to your project
3. Configure `AGENTS.md` or `CLAUDE.md` for your CLI agent
4. Start with `wake up` protocol

## Templates

| Template | Purpose |
|----------|---------|
| [template-worker-aget](https://github.com/aget-framework/template-worker-aget) | Foundation template |
| [template-advisor-aget](https://github.com/aget-framework/template-advisor-aget) | Advisory with personas |
| template-supervisor-aget *(private)* | Fleet coordination |
| [template-consultant-aget](https://github.com/aget-framework/template-consultant-aget) | Consulting engagements |
| [template-developer-aget](https://github.com/aget-framework/template-developer-aget) | Development workflows |
| [template-spec-engineer-aget](https://github.com/aget-framework/template-spec-engineer-aget) | Specification authoring |

## Session Protocols

| Command | Protocol | Purpose |
|---------|----------|---------|
| `wake up` | Wake_Protocol | Initialize session, load context |
| `study up [topic]` | Study_Up_Protocol | Deep dive on specific topic |
| `step back` | Step_Back_Protocol | Review KB before proposing |
| `sanity check` | Sanity_Check_Protocol | Verify agent health |
| `wind down` | Wind_Down_Protocol | End session, create handoff |

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 - See [LICENSE](LICENSE)

---

*Generated from specifications on 2026-01-16*
*See: [AGET_IDENTITY_SPEC.yaml](specs/AGET_IDENTITY_SPEC.yaml), [AGET_POSITIONING_SPEC.yaml](specs/AGET_POSITIONING_SPEC.yaml)*
