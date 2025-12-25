# Fleet Migration Guide

**Version**: 1.0.0
**Created**: 2025-12-25
**Purpose**: Guide practitioners in migrating agents to Capability Composition Architecture

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Single Agent Migration](#single-agent-migration)
4. [Validation Process](#validation-process)
5. [Rollback Procedures](#rollback-procedures)
6. [Fleet-Wide Migration](#fleet-wide-migration)
7. [Troubleshooting](#troubleshooting)
8. [Migration Checklist](#migration-checklist)

---

## Overview

### What is Migration?

Migration is the process of upgrading an existing AGET agent to use the Capability Composition Architecture introduced in v2.10+.

### Key Principle: Additive, Not Destructive

**Capability composition is additive**:
- Agents retain existing template inheritance
- `capabilities[]` array augments, doesn't replace
- No data migration required
- No directory deletion required
- Rollback is always possible

### Before and After

**Before (template-only)**:
```json
{
  "name": "my-agent",
  "template": "advisor",
  "version": "2.9.0"
}
```

**After (template + capabilities)**:
```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

composition:
  base_template: advisor
  capabilities:
    - name: memory-management
    - name: domain-knowledge
```

---

## Prerequisites

### Framework Prerequisites

Before migrating any agent:

| Prerequisite | Check | Location |
|--------------|-------|----------|
| AGET framework v2.11+ | `cat aget/.aget/version.json` | `aget/` |
| Capability specs exist | `ls specs/capabilities/` | `specs/capabilities/` |
| Validators available | `ls aget/validation/` | `aget/validation/` |

### Agent Prerequisites

For each agent to migrate:

| Prerequisite | Check | Notes |
|--------------|-------|-------|
| Working state | Agent is functional | Don't migrate broken agents |
| Git clean | `git status` shows clean | Commit changes first |
| Backup exists | Git history or backup | Rollback safety net |
| Template known | Check `.aget/identity.json` | Know the base template |

### Capability Prerequisites

Know which capabilities the agent needs:

1. Review capability specs in `specs/capabilities/`
2. Match agent's behaviors to capabilities
3. Check capability prerequisites (some require others)

---

## Single Agent Migration

### Step 1: Assess Current State

```bash
cd /path/to/agent

# Check current configuration
cat .aget/version.json
cat .aget/identity.json

# Check existing structure
ls -la
ls -la .aget/
ls governance/ planning/ docs/ 2>/dev/null || echo "Missing directories"
```

### Step 2: Identify Target Capabilities

Review the agent's current behaviors and map to capabilities:

| If agent does... | Add capability |
|------------------|----------------|
| KB management, context refresh | `memory-management` |
| Domain expertise | `domain-knowledge` |
| Formatted outputs (JSON, YAML, reports) | `structured-outputs` |
| Multi-agent coordination | `collaboration` |
| Organizational KB (5W+H) | `org-kb` |

### Step 3: Create Template Manifest

Create `manifest.yaml` in agent root:

```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: agent-name
  version: 1.0.0
  created: "YYYY-MM-DD"
  author: migrating-agent
  status: active

composition:
  base_template: advisor  # or worker, supervisor, etc.
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
  composition_rules:
    conflict_resolution: error
```

### Step 4: Ensure Required Structure

Each capability has contracts that require certain directories/files:

**memory-management requires**:
```bash
mkdir -p governance planning .aget/evolution docs/patterns sops
```

**domain-knowledge requires**:
```bash
mkdir -p docs
```

**structured-outputs requires**:
```bash
mkdir -p outputs templates
```

### Step 5: Update Version Information

**CRITICAL**: Update BOTH files (L366 - AGENTS.md is runtime source of truth):

#### 5a. Update `.aget/version.json`:

```json
{
  "name": "agent-name",
  "version": "1.0.0",
  "template": "advisor",
  "aget_version": "2.12.0",
  "capabilities": [
    "memory-management",
    "domain-knowledge"
  ],
  "migration_history": [
    "v2.x.0 -> v2.12.0: YYYY-MM-DD (Capability Composition Architecture)"
  ]
}
```

#### 5b. Update `AGENTS.md`:

```markdown
# Agent Configuration

@aget-version: 2.12.0   # <-- Must match version.json!

## Project Context
agent-name - Description - v2.12.0   # <-- Also update here
```

**Why both?** Claude Code reads `@aget-version` from AGENTS.md at runtime.
`version.json` is for validators and scripts. They must stay synchronized.

### Step 6: Add Pattern Documents

If missing, create pattern documents referenced by capabilities:

```bash
# For memory-management
touch docs/patterns/PATTERN_step_back_review_kb.md
touch sops/SESSION_HANDOFF_AGET.md
touch sops/SOP_pre_proposal_kb_audit.md
```

### Step 7: Validate Migration

```bash
# Validate manifest schema
python3 aget/validation/validate_template_manifest.py manifest.yaml

# Validate composition
python3 aget/validation/validate_composition.py manifest.yaml \
  --specs aget/specs/capabilities/

# Run contract tests
python3 -m pytest aget/tests/capability_architecture/test_capability_contracts.py -v
```

### Step 8: Test Agent Operation

```bash
# Wake up the agent
# Verify capabilities are recognized
# Test key behaviors (step back, etc.)
```

---

## Validation Process

### Level 1: Schema Validation

Validates manifest structure:

```bash
python3 aget/validation/validate_template_manifest.py manifest.yaml
```

**Pass criteria**:
- Valid apiVersion
- Valid kind
- Required fields present
- Valid composition structure

### Level 2: Composition Validation

Validates capability combination:

```bash
python3 aget/validation/validate_composition.py manifest.yaml \
  --specs specs/capabilities/ -v
```

**Pass criteria**:
- No duplicate capabilities
- Prerequisites satisfied
- No behavior conflicts
- Compatible with base template

### Level 3: Contract Validation

Validates capability requirements:

```python
from tests.capability_architecture.test_capability_contracts import ContractEvaluator

evaluator = ContractEvaluator('/path/to/agent')
contracts = [
    {'name': 'has_governance', 'assertion': 'directory_exists', 'path': 'governance/'},
    {'name': 'has_planning', 'assertion': 'directory_exists', 'path': 'planning/'},
    # ... more contracts from capability specs
]

for contract in contracts:
    result = evaluator.evaluate_contract(contract)
    print(f"{'PASS' if result.passed else 'FAIL'}: {result.name} - {result.message}")
```

### Level 4: Operational Validation

Manual verification:

- [ ] Agent wakes up successfully
- [ ] Capability behaviors trigger correctly
- [ ] No regressions in existing functionality
- [ ] Pattern documents are accessible

---

## Rollback Procedures

### Principle: Safe by Design

Capability composition is additive. Rolling back is straightforward.

### Quick Rollback

To immediately rollback a single agent:

```bash
cd /path/to/agent

# Option 1: Remove manifest
rm manifest.yaml

# Option 2: Remove capabilities from version.json
# Edit .aget/version.json, remove "capabilities" array
```

The agent continues working with base template only.

### Full Rollback

For complete removal:

```bash
# 1. Remove manifest
rm manifest.yaml

# 2. Revert version.json
git checkout -- .aget/version.json

# 3. Capability directories can remain (harmless)
# Or remove if clean slate desired
```

### Fleet Rollback

If systemic issues require fleet-wide rollback:

1. **Stop**: Halt all ongoing migrations
2. **Assess**: Identify affected agents
3. **Rollback**: Apply quick rollback to each
4. **Document**: Record issues for spec revision
5. **Resume**: Only after root cause resolved

---

## Fleet-Wide Migration

### Migration Phases

| Phase | Scope | Version | Goal |
|-------|-------|---------|------|
| Pilot | 6-8 agents | v2.11+ | Validate in practice |
| Wave 1 | Main portfolio | v2.12 | Core agents |
| Wave 2 | Other portfolios | v2.12+ | Full coverage |
| Wave 3 | Special handling | v2.13+ | CCB, federated |

### Pilot Selection Criteria

Choose pilot agents that are:
- Low risk (not critical infrastructure)
- Representative (different templates/capabilities)
- Accessible (can easily test and rollback)
- Willing (owner engagement)

### Migration Tracking

Track migration status:

```yaml
# Example: migration_status.yaml
agents:
  - name: pilot-agent-1
    status: migrated
    capabilities: [memory-management, domain-knowledge]
    migrated_date: "2025-01-15"
    validated: true

  - name: pilot-agent-2
    status: in_progress
    capabilities: [memory-management]
    started_date: "2025-01-20"

  - name: pending-agent
    status: pending
    target_capabilities: [memory-management, structured-outputs]
```

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Migration completion | 100% | Agents with capabilities[] |
| Validation pass rate | 100% | All three validation levels |
| Rollback rate | <5% | Agents requiring rollback |
| Capability reuse | 3+ agents | Per P0 capability |

---

## Troubleshooting

### Issue: Manifest Validation Fails

**Symptom**:
```
❌ manifest.yaml
   ❌ Missing required field: composition.base_template
```

**Solution**: Ensure all required fields are present:
```yaml
composition:
  base_template: advisor  # Required!
  capabilities: []
```

### Issue: Missing Prerequisite

**Symptom**:
```
CONFLICT [missing_prerequisite]: Capability 'collaboration' requires
'domain-knowledge' which is not in composition
```

**Solution**: Add the prerequisite capability:
```yaml
capabilities:
  - name: domain-knowledge  # Add this first
  - name: collaboration
```

### Issue: Contract Fails

**Symptom**:
```
FAIL: has_governance - Directory not found: governance/
```

**Solution**: Create required directory:
```bash
mkdir governance
```

### Issue: Behavior Conflict

**Symptom**:
```
CONFLICT [behavior_name_collision]: Behavior 'step_back' defined in
multiple capabilities
```

**Solution**: Configure conflict resolution:
```yaml
composition_rules:
  conflict_resolution: first-wins  # or last-wins, merge
```

### Issue: Unknown Capability

**Symptom**:
```
⚠️ Unknown capability 'my-custom-cap'
```

**Solution**: Either:
1. Create capability spec: `specs/capabilities/CAPABILITY_SPEC_my_custom_cap.yaml`
2. Or check spelling of capability name

### Issue: Version Mismatch

**Symptom**:
```
Agent version 2.9.0 < minimum required 2.11.0
```

**Solution**: Upgrade agent to v2.11+:
1. Update `.aget/version.json`
2. Apply any breaking changes from v2.10/v2.11

---

## Migration Checklist

### Pre-Migration

- [ ] Framework is v2.11+
- [ ] Agent is in working state
- [ ] Git working directory is clean
- [ ] Backup/commit point exists
- [ ] Target capabilities identified
- [ ] Prerequisites understood

### Migration

- [ ] Created manifest.yaml
- [ ] Created required directories
- [ ] Created required files
- [ ] Updated .aget/version.json (aget_version, capabilities[], migration_history)
- [ ] Updated AGENTS.md (@aget-version tag + project context) **[L366]**
- [ ] Verified CLAUDE.md symlink → AGENTS.md
- [ ] Added pattern documents

### Validation

- [ ] Schema validation passed
- [ ] Composition validation passed
- [ ] Contract validation passed
- [ ] Agent wakes up successfully
- [ ] Key behaviors work correctly
- [ ] No regressions observed

### Post-Migration

- [ ] Committed changes
- [ ] Updated migration tracking
- [ ] Documented any issues
- [ ] Reported success/failure

---

## Example: Complete Migration

### Agent: private-data-analyst-aget

**Before**:
```
private-data-analyst-aget/
├── .aget/
│   ├── version.json
│   └── identity.json
├── CLAUDE.md
└── docs/
```

**Step 1: Assess**
```bash
cat .aget/version.json
# { "version": "2.9.0", "template": "advisor" }
```

**Step 2: Identify Capabilities**
- Domain expertise in data science → `domain-knowledge`
- Outputs analysis reports → `structured-outputs`
- KB management → `memory-management`

**Step 3: Create Manifest**
```yaml
# manifest.yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: private-data-analyst-aget
  version: 1.0.0

composition:
  base_template: advisor
  capabilities:
    - name: memory-management
    - name: domain-knowledge
    - name: structured-outputs
```

**Step 4: Create Structure**
```bash
mkdir -p governance planning .aget/evolution
mkdir -p docs/patterns sops
mkdir -p outputs templates
```

**Step 5: Update Version**
```json
{
  "name": "private-data-analyst-aget",
  "version": "1.0.0",
  "template": "advisor",
  "framework_version": "2.12.0",
  "capabilities": [
    "memory-management",
    "domain-knowledge",
    "structured-outputs"
  ]
}
```

**Step 6: Add Patterns**
```bash
touch docs/patterns/PATTERN_step_back_review_kb.md
touch sops/SESSION_HANDOFF_AGET.md
```

**Step 7: Validate**
```bash
python3 aget/validation/validate_template_manifest.py manifest.yaml
# ✅ manifest.yaml

python3 aget/validation/validate_composition.py manifest.yaml --specs specs/capabilities/
# ✅ manifest.yaml
# 1/1 compositions valid
```

**After**:
```
private-data-analyst-aget/
├── .aget/
│   ├── version.json (updated)
│   ├── identity.json
│   └── evolution/
├── CLAUDE.md
├── manifest.yaml (new)
├── governance/
├── planning/
├── docs/
│   └── patterns/
│       └── PATTERN_step_back_review_kb.md
├── sops/
│   └── SESSION_HANDOFF_AGET.md
├── outputs/
└── templates/
```

---

## References

- Capability Author Guide: `docs/CAPABILITY_AUTHOR_GUIDE.md`
- Composition Guide: `docs/COMPOSITION_GUIDE.md`
- Fleet Migration Plan: `planning/FLEET_MIGRATION_PLAN_v2.10.md`
- Capability Specs: `specs/capabilities/`
- Validators: `validation/`
- Tests: `tests/capability_architecture/`

---

*Fleet Migration Guide v1.0.0*
*Part of AGET Capability Composition Architecture*
