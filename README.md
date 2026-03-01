# AGET Framework

> Persistent domain intelligence for governed agentic work

## What is AGET?

AGET enables AI agents that build persistent domain knowledge serving
human decisions. It provides session continuity, shared memory architecture,
fleet coordination, and human-supervised autonomy patterns that work
across CLI agent platforms. Governance ensures knowledge accumulates
reliably. Validated platforms include Claude Code, Codex CLI, and Gemini CLI.

## Philosophy

**Human-AI collaboration quality over autonomous agent speed**

- **Domain Intelligence First**: Agent value is measured by domain knowledge that serves human decisions
- **Governed Autonomy**: Agents act autonomously within explicit boundaries
- **Portable Memory**: Knowledge persists across sessions and platforms
- **Platform Agnostic**: Patterns work across CLI agent platforms
- **Human Oversight**: Humans remain decision authorities at key points
- **Evidence-First**: Design to reality, not theory

## What AGET is NOT

- **A specific AI model or runtime** — AGET is a governance layer that works with any LLM backend
- **A replacement for Claude Code, Codex CLI, or Gemini CLI** — AGET sits above these platforms as a governance substrate
- **An autonomous AI system** — AGET explicitly requires human supervision and gate discipline
- **A coding-only framework** — AGET supports advisory, consulting, supervision, and general knowledge work
- **A vendor lock-in solution** — Three-tier degradation ensures portability (gh → git → filesystem)

## Supported Platforms

AGET is designed to be platform-agnostic. Validated platforms:

| Platform | Type | Integration | Status |
|----------|------|-------------|--------|
| **Claude Code** | CLI | `CLAUDE.md, .claude/` | **Baseline** — primary development target |
| **Codex CLI** | CLI | `AGENTS.md, .codex/` | **Compatible** — validated |
| **Gemini CLI** | CLI | `AGENTS.md` | **Compatible** — validated |
| Cursor | IDE | `.cursor/rules, .cursorrules` | Experimental — not validated |
| Aider | CLI | `.aider.conf.yml, CONVENTIONS.md` | Experimental — not validated |
| Windsurf | IDE | `TBD` | Experimental — not validated |

See [CLI Support Matrix](docs/AGET_CLI_SUPPORT_MATRIX.md) for detailed validation status.

## Key Features

- **Persistent Domain Knowledge**: Agents accumulate expertise that compounds across sessions
- **Memory Architecture**: KB as shared collaboration substrate
- **Platform Portability**: Three-tier degradation ensures functionality across environments
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

## Archetype Ecosystem

AGET provides **12 specialized archetypes**, each with purpose-built skills and formal ontology:

| Category | Archetypes | Focus |
|----------|------------|-------|
| **Execution** | Worker, Developer, Operator | Task completion, code, operations |
| **Analysis** | Analyst, Researcher, Reviewer | Data, literature, quality |
| **Design** | Architect, Spec-Engineer | Systems, requirements |
| **Advisory** | Advisor, Consultant, Executive | Guidance, engagements, decisions |
| **Coordination** | Supervisor | Fleet management |

Each archetype includes:
- **2-3 specialized skills** for archetype-specific workflows
- **15 universal skills** shared across all agents (session, health, learning, governance)
- **Formal ontology** defining domain vocabulary

See [GETTING_STARTED.md](GETTING_STARTED.md) for archetype selection guidance.

## Ontology-Driven Design

v3.5.0 introduces **ontology-driven agent customization**:

```
Vocabulary → Specification → Implementation
```

| Layer | Artifact | Purpose |
|-------|----------|---------|
| **Vocabulary** | `ontology/ONTOLOGY_{archetype}.yaml` | Domain concepts (SKOS-compliant) |
| **Specification** | `specs/SKILL_{name}_SPEC.md` | Formal requirements (EARS patterns) |
| **Implementation** | `.claude/skills/{name}/` | Skill execution |

**Benefits**:
- **Precision**: Formal vocabulary prevents ambiguity
- **Consistency**: Same concepts across all archetype instances
- **Extensibility**: Add domain-specific terms to ontology

## Quick Start

> **Recommended Starting Point**: Start with the [Supervisor template](https://github.com/aget-framework/template-supervisor-aget). It coordinates your agent fleet and can create new agents using `/aget-create-aget`. See [GETTING_STARTED.md](GETTING_STARTED.md) for the supervisor-first workflow.

1. Clone a template from [aget-framework](https://github.com/aget-framework)
2. Configure `.aget/version.json` and `AGENTS.md` for your agent
3. Run `python3 -m pytest tests/ -v` to verify setup
4. Start with `wake up` protocol

## Templates

**12 Archetypes** with specialized skills and ontologies (v3.5.0+):

| Template | Archetype | Key Skills | Use Case |
|----------|-----------|------------|----------|
| [**template-supervisor-aget**](https://github.com/aget-framework/template-supervisor-aget) | supervisor | broadcast-fleet, review-agent, escalate-issue, create-aget | Fleet coordination (**recommended start**) |
| [template-worker-aget](https://github.com/aget-framework/template-worker-aget) | worker | execute-task, report-progress | Task execution, foundation |
| [template-developer-aget](https://github.com/aget-framework/template-developer-aget) | developer | run-tests, lint-code, review-pr | Development workflows |
| [template-advisor-aget](https://github.com/aget-framework/template-advisor-aget) | advisor | assess-risk, recommend-action | Advisory with personas |
| [template-consultant-aget](https://github.com/aget-framework/template-consultant-aget) | consultant | assess-client, propose-engagement | Consulting engagements |
| [template-analyst-aget](https://github.com/aget-framework/template-analyst-aget) | analyst | analyze-data, generate-report | Data analysis |
| [template-architect-aget](https://github.com/aget-framework/template-architect-aget) | architect | design-architecture, assess-tradeoffs | System design |
| [template-researcher-aget](https://github.com/aget-framework/template-researcher-aget) | researcher | search-literature, document-finding | Research workflows |
| [template-operator-aget](https://github.com/aget-framework/template-operator-aget) | operator | handle-incident, run-playbook | Operations/DevOps |
| [template-executive-aget](https://github.com/aget-framework/template-executive-aget) | executive | make-decision, review-budget | Executive advisory |
| [template-reviewer-aget](https://github.com/aget-framework/template-reviewer-aget) | reviewer | review-artifact, provide-feedback | Quality review |
| [template-spec-engineer-aget](https://github.com/aget-framework/template-spec-engineer-aget) | spec-engineer | validate-spec, generate-requirement | Specification authoring |

**All templates include**: 15 universal skills + archetype-specific skills.
See [GETTING_STARTED.md](GETTING_STARTED.md) for archetype selection guidance.

## Session Protocols

| Command | Protocol | Purpose |
|---------|----------|---------|
| `wake up` | Wake_Protocol | Initialize session, load context |
| `study up [topic]` | Study_Up_Protocol | Deep dive on specific topic |
| `step back` | Step_Back_Protocol | Review KB before proposing |
| `sanity check` | Sanity_Check_Protocol | Verify agent health |
| `wind down` | Wind_Down_Protocol | End session, create handoff |

## Contributing

Contributions welcome! See the [Issues page](https://github.com/aget-framework/aget/issues) to report bugs or suggest features.

## License

Apache License 2.0 - See [LICENSE](LICENSE)

---

*Generated from specifications on 2026-02-22*
*See: [AGET_IDENTITY_SPEC.yaml](specs/AGET_IDENTITY_SPEC.yaml), [AGET_POSITIONING_SPEC.yaml](specs/AGET_POSITIONING_SPEC.yaml)*
