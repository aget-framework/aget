# AGET Framework

**Canonical specification and reference implementation for AGET (Agent) framework**

## What is AGET?

AGET is a configuration & lifecycle management system for CLI-based human-AI collaborative coding. It provides:
- Universal CLI compatibility (Claude Code, Cursor, Aider, Windsurf)
- Contract testing and version compliance
- Shared learning repository and evolutionary patterns
- Human-centric governance with evidence-based planning

## Origin

Created 2025-11-21 via [ADR-001](https://github.com/aget-framework/private-supervisor-AGET/.aget/decisions/ADR-001-aget-framework-repository.md) in private-supervisor-AGET.

## Current Version

**v2.11.0** (2025-12-24): Memory Architecture + L352 Traceability + Version Migration

Key features: 6-layer information model, five-tier requirement-to-test traceability, 80 contract tests passing, configurable wake-up output.

**Version History**: See [docs/VERSION_HISTORY.md](docs/VERSION_HISTORY.md) for complete version timeline and known gaps.

This repository contains:
- `specs/` - Framework specifications
- `templates/` - Standard templates (ADR format)
- `validation/` - Compliance checking tools
- `docs/` - Architecture and structure guides

## Repository Structure

```
aget/
├── specs/                          # Framework specifications
│   ├── AGET_SPEC_FORMAT_v1.1.md       # EARS-based spec format
│   ├── AGET_CONTROLLED_VOCABULARY.md  # Canonical vocabulary
│   ├── AGET_VERSIONING_CONVENTIONS.md # SemVer rules
│   └── WORKER_TEMPLATE_SPEC_v1.0.yaml # Foundation template spec
├── templates/                      # Standard templates
│   └── ADR_TEMPLATE.md               # Architectural Decision Record format
├── validation/                     # Compliance tools
│   └── check_aget_vocabulary.py      # Vocabulary compliance checker
└── docs/                           # Architecture guides
    ├── LAYER_ARCHITECTURE.md         # Template inheritance hierarchy
    └── TEMPLATE_STRUCTURE_GUIDE.md   # Standard directory structure
```

## Specifications

### Core Specifications

| Specification | Purpose | Status |
|--------------|---------|--------|
| AGET_SPEC_FORMAT_v1.1.md | EARS-based requirement format | Canonical |
| AGET_CONTROLLED_VOCABULARY.md | Standard terminology | Canonical |
| AGET_VERSIONING_CONVENTIONS.md | Version numbering rules | Canonical |
| WORKER_TEMPLATE_SPEC_v1.0.yaml | Foundation template (35 capabilities) | Canonical |

### Template Specifications

| Template | Specification | Status |
|----------|--------------|--------|
| template-worker-aget | WORKER_TEMPLATE_SPEC_v1.0.yaml | v1.0.0 |
| template-advisor-aget | ADVISOR_TEMPLATE_SPEC_v1.0.yaml | v2.0.0 |
| template-supervisor-aget | (pending) | Planned |

## For Template Developers

Import framework specifications:

```yaml
spec:
  inherits_from: SPEC-WORKER-TEMPLATE
  parent_version: "1.0.0"
```

Reference controlled vocabulary:
```
See: aget/specs/AGET_CONTROLLED_VOCABULARY.md
```

Use EARS patterns for capability statements:
```yaml
statement: "WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol"
```

## For Agent Creators

See templates in [aget-framework organization](https://github.com/aget-framework):
- template-worker-aget - Foundation template
- template-advisor-aget - Advisory with personas
- template-supervisor-aget - Fleet coordination
- template-consultant-aget - Consulting engagements
- template-developer-aget - Development workflows
- template-spec-engineer-aget - Specification authoring

## Roadmap

### v2.9.x (Current)
- [x] Core Template Specification (WORKER_TEMPLATE_SPEC)
- [x] Layer Architecture documentation
- [x] Template Structure Guide
- [ ] INSTANCE_CREATION_SPEC (Tier 3)
- [ ] Additional contract tests

### v3.0 (Future)
- Full Framework Conformance (comprehensive AGET_FRAMEWORK_SPEC)
- Complete capabilities (EARS-formatted)
- External interoperability and validation
- SUPERVISOR_TEMPLATE_SPEC

## Validation

Check vocabulary compliance:

```bash
cd aget/validation
python check_aget_vocabulary.py ../specs/
```

## Quick Reference

### Instance Types

| Type | Capabilities | Example |
|------|-------------|---------|
| `aget` | Read-only, analysis, advisory | private-impact-aget |
| `AGET` | Action-taking, file writes | private-supervisor-AGET |
| `template` | Reference implementation | template-worker-aget |
| `coordinator` | Fleet management | private-supervisor-AGET |

### Session Protocols

| Command | Protocol | Purpose |
|---------|----------|---------|
| `wake up` | Wake_Protocol | Initialize session |
| `study up` | Study_Up_Protocol | Load deep context |
| `wind down` | Wind_Down_Protocol | Finalize session |
| `sign off` | Sign_Off_Protocol | Complete closure |

### Key L-docs

| L-doc | Topic |
|-------|-------|
| L185 | Environmental grounding |
| L186 | TodoWrite vs PROJECT_PLAN |
| L187 | Wake protocol silent execution |
| L174 | Template specification debt |
| L171 | Instance creation gap |

## License

Apache License 2.0 - See LICENSE file

## Maintenance

Maintained by private-aget-framework-AGET (framework management role)
Governed by private-supervisor-AGET (fleet coordinator)

---

**Version**: 2.10.0
**Created**: 2025-11-21
**Updated**: 2025-12-13
**Status**: Capability Composition Architecture
