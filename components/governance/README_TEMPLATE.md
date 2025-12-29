# Governance Directory

This directory contains governance artifacts that define agent boundaries and authority.

## Required Files (CAP-INST-002)

| File | Purpose |
|------|---------|
| `CHARTER.md` | What this agent IS and IS NOT |
| `MISSION.md` | Goals and key results |
| `SCOPE_BOUNDARIES.md` | Authority limits and escalation paths |

## Optional Files

| File | Purpose |
|------|---------|
| `NAMING_CONVENTIONS.md` | Agent-specific naming rules |
| `DECISION_MATRIX.md` | Authority delegation rules |
| `MEMORY_VISION.md` | Memory architecture principles |

## Guidance

### What Goes Here

- **Operational boundaries** — not technical specifications
- **Authority definitions** — what decisions this agent can make autonomously
- **Escalation rules** — when to defer to supervisor or principal

### Maintenance

- Update `CHARTER.md` when scope changes
- Review `MISSION.md` quarterly for KR relevance
- Update `SCOPE_BOUNDARIES.md` when authority model changes

### Anti-Patterns

| Anti-Pattern | Why Bad | Instead |
|--------------|---------|---------|
| Technical specs in CHARTER | Conflates governance with implementation | Put specs in `.aget/specs/` |
| Vague MISSION goals | Not measurable | Use SMART criteria |
| Missing escalation paths | Agent operates beyond authority | Define explicit boundaries |

## Cross-References

| Document | Relationship |
|----------|--------------|
| `.aget/identity.json` | North Star alignment |
| `CLAUDE.md` | Operational instructions |
| `AGENTS.md` | Public-facing identity |

---

*Template version: 1.0.0 (L403 pattern)*
*Created by: private-aget-framework-AGET*
