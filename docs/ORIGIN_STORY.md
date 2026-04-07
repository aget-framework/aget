# AGET Origin Story

**Version**: 1.1.0
**Created**: 2026-04-07
**Updated**: 2026-04-07
**Sources**: template-worker-aget git history, CCB AGET_RELATIONSHIP.md and journal, supervisor DEC 2025-09-25, COGNITIVE_SPECTRUM.md, L35 (capability signaling)

## The Name

AGET originated as a shorthand for the first repository: `aget-cli-agent-template`, created on September 21, 2025. The initial expansion was **"Agent Template"** (commit `8e4c82c`, Sep 21 21:13). Hours later, during a late-night session migrating CCB (Co-Creating Beauty) to AGET patterns, the expansion grew to **"Agent Evolution Template"** (AGET_RELATIONSHIP.md, Sep 22 00:08) — reflecting the idea that agents evolve through accumulated knowledge, not just execute from static configuration.

Three days later (Sep 25), a naming convention decision formalized the ambiguity as intentional: AGET "simultaneously represents the philosophical framework, the implementation template, the cognitive agent experience, and specific instance deployments." The multi-faceted identity was a design choice, not an accident.

The later public description — "Agent without the 'n'" — is a mnemonic simplification, not the full origin.

## The Config File Problem

Every AI coding session required re-explaining project context. Every tool (Claude Code, Cursor, Aider, Windsurf) needed different config files with duplicate content.

The first commit (Sep 21, 16:19) created a `CLAUDE.md` file. Twenty-nine minutes later, it was renamed to `AGENT.md` for universal compatibility — the template should work with any CLI agent, not just Claude Code. Seventy-three minutes after that, it became `AGENTS.md` (plural) to align with the emerging industry standard. Three renames in two hours, all on day one. The core tension — platform-specific vs. universal — was resolved immediately in favor of universality.

## The Conversational Command Insight

The breakthrough insight (recorded in the CCB journal, Sep 24, 23:42): AI agents are excellent at following conversational commands. Instead of complex configuration files, give them natural language protocols. "Wake up" could initialize a session. "Wind down" could save work. "Tidy up" could clean temporary files.

These phrases were present in the very first commit — the insight preceded the formal articulation by three days. The journal entry captured why it worked: "not as static files but as living conversations, not as isolated tools but as community-driven evolution, not as theoretical design but as patterns proven through real usage."

## The Vision

COGNITIVE_SPECTRUM.md (Sep 25, 2025) described five modalities — from standalone data analysis to nested meta-governance — and framed each AGET instance as a "cognitive prosthetic adapted to its specific context and your relationship to that context." The `.aget/evolution/` directory (Sep 24, 2025) made this concrete: agents track decisions, discoveries, extractions, and learnings, accumulating domain expertise across sessions.

## Timeline

| Date | Milestone |
|------|-----------|
| 2024-09-20 | RKB content enhancer created (pre-AGET, later retrofitted) |
| 2025-06-14 | Earliest known CLAUDE.md in the org |
| 2025-07-09 | Claude Code installed |
| 2025-09-21 16:19 | First commit: "Initial CLI Agent Template repository" with CLAUDE.md |
| 2025-09-21 16:48 | CLAUDE.md renamed to AGENT.md (universal compatibility) |
| 2025-09-21 18:01 | AGENT.md renamed to AGENTS.md (industry standard, plural) |
| 2025-09-21 21:13 | "AGET (Agent Template)" formalized |
| 2025-09-22 00:08 | "Agent Evolution Template" — born in late-night conversation |
| 2025-09-24 14:13 | `.aget/evolution/` directory created (4 entry types) |
| 2025-09-24 23:42 | Origin narrative captured in CCB journal |
| 2025-09-25 | Naming convention DEC + COGNITIVE_SPECTRUM.md |
| 2025-09-27 | First fleet agent commit (`my-AGET-aget`) |
| 2025-10-03 | Case distinction (-AGET/-aget) formalized (L35) |
| 2025-10-13 | First batch deployment (6 agents) |

## Naming Conventions

Established Sep 25, 2025 — the naming hierarchy carries structural meaning:

| Pattern | Meaning |
|---------|---------|
| `aget` | The concept and philosophy |
| `-AGET` suffix | Action-taking agent (can modify data) |
| `-aget` suffix | Information-only agent (read-only) |
| `aget-aget` | Governance layer (self-referential: AGET managing AGET) |
| `X-aget` | Instance pattern (e.g., `healthcare-aget`) |

### Case Distinction Origin

The `-AGET` vs `-aget` capability signaling appeared in practice from the very first fleet commit (`my-AGET-aget`, Sep 27) but was formalized later. During v2.4 planning (Oct 3, L35), the founder asked: "How about if the -aget indicates? -AGET vs -aget?" Moving the capability signal from the domain name to the suffix resolved ambiguity — acronym domains (CCB, RKB) no longer conflicted with capability casing. The pattern: suffix position is always consistent, visually clear, and independent of domain naming.

## See Also

- `specs/AGET_IDENTITY_SPEC.yaml` — Canonical identity and definitions
- `specs/AGET_POSITIONING_SPEC.yaml` — Strategic positioning
- `docs/VERSION_HISTORY.md` — Release timeline
