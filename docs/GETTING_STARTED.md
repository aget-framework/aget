# Getting Started with AGET

**Version**: v3.0.0
**Audience**: New users, developers wanting to create agents

---

## What is AGET?

AGET (Agent Configuration & Lifecycle Management) is a framework for human-AI collaborative coding. It provides:

- **Configuration as Code**: Agent identity, capabilities, and governance in YAML/JSON
- **5D Composition Architecture**: Persona, Memory, Reasoning, Skills, Context
- **12 Archetypes**: Pre-built templates for common agent roles
- **Session Protocols**: Wake-up, wind-down, and handoff patterns
- **Validation Tools**: Ensure agents comply with specifications

---

## Quick Start (5 Minutes)

### 1. Choose a Template

AGET provides 12 archetype templates:

| Template | Role | Key Capability |
|----------|------|----------------|
| `template-worker-aget` | Base agent | Task execution |
| `template-advisor-aget` | Read-only advisor | Recommendations without changes |
| `template-developer-aget` | Software developer | Code implementation |
| `template-architect-aget` | System designer | Architecture decisions |
| `template-supervisor-aget` | Team coordinator | Multi-agent oversight |
| `template-consultant-aget` | Domain expert | Specialized expertise |
| `template-spec-engineer-aget` | Specification author | EARS/SKOS authoring |
| `template-executive-aget` | Strategic leader | Portfolio oversight |
| `template-analyst-aget` | Data analyst | Insights and reports |
| `template-reviewer-aget` | Quality reviewer | Code and spec review |
| `template-operator-aget` | Operations | Deployment and monitoring |
| `template-researcher-aget` | Researcher | Investigation and discovery |

### 2. Instantiate Your Agent

```bash
# Clone the framework
git clone https://github.com/aget-framework/aget.git
cd aget-framework

# Create your agent from a template
python3 aget/scripts/instantiate_template.py \
  --template template-developer-aget \
  --name my-project-AGET \
  --persona "Project Developer for MyApp"

# Navigate to your agent
cd my-project-AGET
```

### 3. Customize Your Agent

Edit these files to personalize your agent:

```bash
# Update identity
nano .aget/identity.json

# Customize charter
nano governance/CHARTER.md

# Set mission and scope
nano governance/MISSION.md
nano governance/SCOPE_BOUNDARIES.md
```

### 4. Verify Setup

```bash
# Run validation
python3 -m pytest tests/ -v

# Or use template-aware validator
python3 ../aget/validation/validate_template_instance.py .
```

### 5. Start Using Your Agent

Create your first session:

```bash
mkdir -p sessions
echo "# Session $(date +%Y-%m-%d)" > sessions/session_$(date +%Y-%m-%d).md
```

---

## Understanding the Structure

### Agent Directory Layout

```
my-project-AGET/
├── .aget/                      # Agent configuration (hidden)
│   ├── version.json            # Agent version and type
│   ├── identity.json           # North Star and persona
│   ├── persona/                # D1: Communication style
│   ├── memory/                 # D2: Memory configuration
│   ├── reasoning/              # D3: Decision patterns
│   ├── skills/                 # D4: Capabilities
│   ├── context/                # D5: Environment awareness
│   └── evolution/              # L-docs (learnings)
├── governance/                 # Agent governance (visible)
│   ├── CHARTER.md              # What agent IS and IS NOT
│   ├── MISSION.md              # Goals and metrics
│   └── SCOPE_BOUNDARIES.md     # Operational limits
├── planning/                   # Active work (visible)
├── sessions/                   # Session notes (visible)
├── knowledge/                  # Domain knowledge (visible)
├── manifest.yaml               # Capability declarations
├── README.md                   # Agent documentation
└── tests/                      # Validation tests
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Template** | Canonical pattern, not for direct use |
| **Instance** | Deployed agent created from template |
| **L-doc** | Learning document (L001, L002, ...) |
| **North Star** | Agent's guiding purpose |
| **Archetype** | Agent category (advisor, developer, etc.) |
| **5D Composition** | Five dimensions that define an agent |

---

## Templates vs Instances

### Templates Are Patterns

Templates (`template-*-aget`) are **not meant for direct use**. They are:
- Canonical patterns for agent creation
- Maintained by the framework
- Updated with each release
- `instance_type: "template"` in version.json

### Instances Are Deployed Agents

Instances (`*-AGET`) are **working agents**. They are:
- Created from templates via `instantiate_template.py`
- Customized for specific purposes
- Accumulate learnings over time
- `instance_type: "aget"` in version.json

---

## The 5D Composition Architecture

Every AGET agent is composed of five dimensions:

### D1: PERSONA (Who)
- Identity and communication style
- Archetype (advisor, developer, etc.)
- Persona modes and intensity

### D2: MEMORY (What Knows)
- Six-layer memory model
- L-doc accumulation
- Knowledge inheritance

### D3: REASONING (How Thinks)
- Decision authority matrix
- Planning patterns
- Gate discipline

### D4: SKILLS (What Can Do)
- Capability declarations
- A-SDLC phase mapping
- Tool integrations

### D5: CONTEXT (Where Operates)
- Relationships with other agents
- Operational scope
- Environmental awareness

---

## Common Tasks

### Wake Up an Agent

```bash
# In agent directory
python3 .aget/patterns/session/wake_up.py

# Or manually
cat .aget/version.json
cat .aget/identity.json
git status
```

### Wind Down a Session

```bash
# Create session handoff
cat > sessions/handoff_$(date +%Y-%m-%d).md << 'EOF'
# Session Handoff

## What we set out to do
...

## What we actually did
...

## Next session should start with
...
EOF
```

### Capture a Learning

```bash
# Create L-doc
cat > .aget/evolution/L001_my_first_learning.md << 'EOF'
# L001: My First Learning

**Date**: $(date +%Y-%m-%d)
**Context**: ...

## Observation
...

## Insight
...

## Application
...
EOF
```

### Export Knowledge (Framework Ejection)

```bash
# Export portable content
python3 ../aget/scripts/export_agent_knowledge.py . --output ./export

# Check what would be exported
python3 ../aget/scripts/export_agent_knowledge.py . --check
```

---

## Validation Tools

### Template/Instance Validator

```bash
# Validates with type-appropriate checks
python3 aget/validation/validate_template_instance.py /path/to/agent

# Strict mode (warnings = failures)
python3 aget/validation/validate_template_instance.py /path/to/agent --strict
```

### L-doc Index Generator

```bash
# Generate index for 50+ L-docs
python3 aget/scripts/generate_ldoc_index.py /path/to/agent

# Check if index is needed
python3 aget/scripts/generate_ldoc_index.py /path/to/agent --check
```

### Template Compliance Analyzer

```bash
# Analyze template compliance
python3 aget/scripts/analyze_template_compliance.py /path/to/template
```

---

## Governance Levels

AGET supports three governance intensities:

| Level | When to Use | Gate Discipline |
|-------|-------------|-----------------|
| **Minimal** | Exploration, research | Flexible |
| **Balanced** | Most agents | Standard gates |
| **Rigorous** | Production, supervisors | Strict gates |

Set in `.aget/persona/archetype.yaml`:

```yaml
governance:
  intensity: "balanced"  # minimal | balanced | rigorous
```

---

## Session Protocol

### Wake-Up (Start of Session)

1. Load identity (version.json, identity.json)
2. Check git status
3. Review pending work
4. Display summary

### Mid-Session (Step Back)

1. "step back. review kb."
2. Check inherited/, planning/, evolution/
3. Cite precedents before proposing

### Wind-Down (End of Session)

1. Document decisions made
2. Capture learnings as L-docs
3. Create session handoff
4. Note pending work

---

## Next Steps

1. **Explore archetypes**: Review each template's CHARTER.md
2. **Read specifications**: `aget/specs/AGET_TEMPLATE_SPEC.md`
3. **Understand memory**: `aget/specs/AGET_MEMORY_SPEC.md`
4. **Check portability**: `aget/specs/AGET_PORTABILITY_SPEC.md`

---

## Getting Help

- **GitHub Issues**: https://github.com/aget-framework/aget/issues
- **Specifications**: `aget/specs/`
- **Patterns**: `aget/docs/patterns/`

---

*AGET Getting Started Guide v3.0.0*
*"AGET optimizes for human-AI collaboration quality, not autonomous agent speed."*
