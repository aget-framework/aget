# CLI Settings Hygiene Standard

**Version**: 1.0.0
**Status**: ACTIVE
**Implements**: #6 (CLI Settings Hygiene Standards)
**Patterns**: L038 (Agent-Agnostic)

---

## Purpose

Define consistent structure and hygiene standards for CLI settings files across supported AI coding assistants. Ensures agents work identically regardless of which CLI they're running on.

---

## Supported CLI Environments

| CLI | Settings File | Location |
|-----|---------------|----------|
| Claude Code | `CLAUDE.md` | Project root |
| Codex CLI | `AGENTS.md` | Project root |
| Cursor | `.cursorrules` | Project root |
| Aider | `.aider` | Project root |
| Windsurf | `.windsurfrules` | Project root |

---

## Standard Structure

### R-CLI-001: Universal Sections

All CLI settings MUST include these sections:

```markdown
# Agent Configuration

@aget-version: X.Y.Z

## North Star
> **Purpose**: [One-sentence agent purpose]

## Session Protocol
[Wake up and wind down instructions]

## Key Documents
[Reference table to important files]
```

### R-CLI-002: North Star Reference

**REQUIRED**: Reference to `.aget/identity.json` for authoritative purpose.

```markdown
## North Star
> **Purpose**: [Statement from identity.json north_star]

See: `.aget/identity.json` | `governance/MISSION.md`
```

### R-CLI-003: Version Tag

**REQUIRED**: Version tag at top of file.

```markdown
@aget-version: 3.1.0
```

This enables:
- Automated version checking
- Migration detection
- Compliance validation

### R-CLI-004: Session Protocol Section

**REQUIRED**: Define wake up and wind down behavior.

```markdown
## Session Protocol

### Wake Up Protocol
When user says "wake up":
1. Execute `python3 .aget/patterns/session/wake_up.py`
2. Display formatted output
3. Ready for work

### Wind Down Protocol
When user says "wind down":
1. Execute `python3 .aget/patterns/session/wind_down.py`
2. Note any pending work
3. Clean close
```

### R-CLI-005: Key Documents Table

**RECOMMENDED**: Reference table for navigation.

```markdown
## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| North Star | `.aget/identity.json` | Agent purpose |
| Mission | `governance/MISSION.md` | Goals and metrics |
| Charter | `governance/CHARTER.md` | What agent IS/IS NOT |
| Scope | `governance/SCOPE_BOUNDARIES.md` | Boundaries |
```

---

## CLI-Specific Adaptations

### Claude Code (CLAUDE.md)

Full markdown supported. Can include:
- Detailed instructions
- Code examples
- Multi-level headers
- Tables

```markdown
# Agent Configuration

@aget-version: 3.1.0

## North Star
> **Purpose**: Enable human-AI collaboration...

[Full content...]
```

### Codex CLI (AGENTS.md)

Similar to CLAUDE.md. Full markdown.

```markdown
# Agent: my-agent

@aget-version: 3.1.0

## Purpose
[Brief purpose statement]

## Instructions
[Codex-specific instructions]
```

### Cursor (.cursorrules)

More constrained format. Keep concise.

```
# Cursor Rules for my-agent

Version: 3.1.0
Purpose: [One line]

## Key Behaviors
- [Behavior 1]
- [Behavior 2]

## Session Commands
- "wake up" - Initialize session
- "wind down" - End session
```

### Aider (.aider)

Configuration format. Minimal markdown.

```
# Aider config for my-agent

model: claude-3-opus
edit-format: diff

# AGET Integration
# Version: 3.1.0
# Wake: python3 .aget/patterns/session/wake_up.py
```

---

## Validation Rules

### V-CLI-001: Version Tag Present

```bash
grep -E "^@aget-version:|^Version:" CLAUDE.md
# Expected: Match found
```

### V-CLI-002: North Star Section Exists

```bash
grep -c "North Star\|Purpose" CLAUDE.md
# Expected: >= 1
```

### V-CLI-003: Session Protocol Defined

```bash
grep -c "wake up\|Wind Down\|Session Protocol" CLAUDE.md
# Expected: >= 1
```

### V-CLI-004: No Hardcoded Paths

```bash
grep -c "/Users/\|/home/\|C:\\\\" CLAUDE.md
# Expected: 0 (no absolute paths)
```

### V-CLI-005: References .aget/

```bash
grep -c "\.aget/" CLAUDE.md
# Expected: >= 1
```

---

## Migration Between CLIs

### From Claude Code to Codex CLI

1. Copy `CLAUDE.md` to `AGENTS.md`
2. Adjust header format if needed
3. Verify session protocol works

### From Codex CLI to Cursor

1. Extract key sections from `AGENTS.md`
2. Condense to `.cursorrules` format
3. Keep under 2000 tokens recommended

### Universal Migration Script

```bash
python3 scripts/migrate_cli_settings.py \
  --from CLAUDE.md \
  --to .cursorrules \
  --format cursor
```

---

## Template Files

### CLAUDE.md Template

Location: `aget/templates/cli/CLAUDE.md.template`

### AGENTS.md Template

Location: `aget/templates/cli/AGENTS.md.template`

### .cursorrules Template

Location: `aget/templates/cli/.cursorrules.template`

---

## Hygiene Checklist

Before committing CLI settings:

- [ ] Version tag present and current
- [ ] North Star matches identity.json
- [ ] Session protocol complete
- [ ] No hardcoded absolute paths
- [ ] No secrets or credentials
- [ ] Key documents table accurate
- [ ] File size reasonable (<50KB)

---

## References

- L038: Agent-Agnostic Infrastructure Pattern
- Issue #6: CLI Settings Hygiene Standards
- `scripts/validate_cli_settings.py` - Validation tool

---

*CLI_SETTINGS_STANDARD.md - Cross-CLI settings hygiene*
