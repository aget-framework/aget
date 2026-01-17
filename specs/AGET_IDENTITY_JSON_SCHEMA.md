# AGET Identity JSON Schema Specification

**Version**: 1.0.0
**Created**: 2026-01-08
**Status**: Active
**Implements**: AGET_INSTANCE_SPEC.md (identity.json requirements)
**Context**: Created following L488 (SOP Template vs Operational Reality Gap)

---

## Purpose

This specification defines the schema for `.aget/identity.json`, ensuring compatibility between identity files and session scripts (wake_up.py, wind_down.py).

**Critical**: Session scripts expect specific field structures. Schema compliance prevents runtime failures.

---

## Schema Definition

### Required Fields

| Field | Type | Description | Consumer |
|-------|------|-------------|----------|
| `name` | string | Agent name (must match directory name) | All scripts |
| `north_star` | **object** | Agent purpose and success criteria | wake_up.py |
| `created` | string (ISO date) | Creation date | Metadata |

### north_star Object (REQUIRED STRUCTURE)

```json
{
  "north_star": {
    "type": "purpose",
    "statement": "string - the agent's core mission",
    "success_looks_like": ["array of success indicators"],
    "failure_looks_like": ["array of failure indicators"]
  }
}
```

| Subfield | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | One of: "purpose", "ambition", "curiosity", "wonder" |
| `statement` | string | Yes | Core mission statement (>10 chars) |
| `success_looks_like` | array[string] | Recommended | Observable success indicators |
| `failure_looks_like` | array[string] | Recommended | Observable failure indicators |

**WARNING**: `north_star` as a bare string will cause wake_up.py to fail with AttributeError.

### Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `updated` | string (ISO date) | Last update date |
| `version` | string (semver) | Identity schema version (e.g., "1.4.0") |
| `identity_dimensions` | object | Role, scope, relationships |
| `operating_principles` | array[string] | Guiding principles |

### identity_dimensions Object (RECOMMENDED)

```json
{
  "identity_dimensions": {
    "role": "string - functional role description",
    "scope": "string - what the agent operates on",
    "relationship_to_supervisor": "string - hierarchy relationship",
    "relationship_to_framework": "string - (optional) framework relationship"
  }
}
```

### Archetype-Specific Fields (OPTIONAL)

Different archetypes may include additional fields:

#### Researcher/Research_Engineer

| Field | Type | Description |
|-------|------|-------------|
| `archetype` | string | "Researcher" or "Research_Engineer" |
| `specialization` | string | Research domain |
| `research_subjects` | array[string] | Subjects under study |
| `research_domains` | array[string] | Domain areas |
| `vocabulary_ref` | string | Path to vocabulary spec |
| `spec_ref` | string | Path to domain spec |
| `methodology_ref` | string | Path to methodology doc |
| `theoretical_basis` | array[string] | Foundational L-docs |

#### Worker/Operator

| Field | Type | Description |
|-------|------|-------------|
| `archetype` | string | "Worker" or "Operator" |
| `capabilities` | array[string] | Enabled capabilities |

#### Supervisor

| Field | Type | Description |
|-------|------|-------------|
| `archetype` | string | "Supervisor" |
| `fleet_scope` | string | Portfolios managed |
| `direct_reports` | array[string] | Managed agents |

---

## Complete Examples

### Minimal Valid Identity (Worker)

```json
{
  "name": "private-example-aget",
  "created": "2026-01-08",
  "north_star": {
    "type": "purpose",
    "statement": "Process incoming requests and maintain data quality",
    "success_looks_like": [
      "Zero data corruption incidents",
      "All requests processed within SLA"
    ],
    "failure_looks_like": [
      "Data quality degradation",
      "SLA breaches"
    ]
  }
}
```

### Full Research Agent Identity

```json
{
  "name": "private-cli-aget",
  "created": "2026-01-07",
  "updated": "2026-01-08",
  "version": "1.4.0",
  "north_star": {
    "type": "purpose",
    "statement": "Deep research on CLI agent subsystems to inform framework governance",
    "success_looks_like": [
      "Comprehensive L-docs covering each subsystem",
      "POC artifacts demonstrating patterns",
      "Framework recommendations grounded in evidence"
    ],
    "failure_looks_like": [
      "Research that doesn't generalize",
      "Theoretical analysis without validation",
      "Findings that never inform governance"
    ]
  },
  "identity_dimensions": {
    "role": "Research Engineer (action-taking for POCs)",
    "scope": "CLI agent subsystems across multiple CLI tools",
    "relationship_to_supervisor": "Child agent managed by private-supervisor-AGET",
    "relationship_to_framework": "Research arm informing aget-framework governance"
  },
  "operating_principles": [
    "Multi-CLI evidence over single-CLI assumptions",
    "POC validation before framework recommendations",
    "Vocabulary precision (L481/L482 grounding)"
  ],
  "archetype": "Research_Engineer",
  "specialization": "CLI Agent Subsystem Research",
  "research_subjects": ["Claude Code", "Codex CLI", "Gemini CLI"],
  "research_domains": ["Skills", "Hooks", "Context", "Permissions", "Sessions"],
  "vocabulary_ref": "specs/CLI_VOCABULARY.md",
  "spec_ref": "specs/CLI_SUBSYSTEM_SPEC.md",
  "theoretical_basis": [
    "L481: Ontology-Driven Agent Creation",
    "L482: Executable Ontology (SKOS+EARS)"
  ]
}
```

### Supervisor Identity

```json
{
  "name": "private-supervisor-AGET",
  "created": "2025-09-24",
  "updated": "2026-01-08",
  "version": "1.0.0",
  "north_star": {
    "type": "purpose",
    "statement": "Coordinate fleet operations and maintain framework governance standards",
    "success_looks_like": [
      "Fleet-wide version consistency",
      "Timely incident response",
      "Pattern propagation across all agents"
    ],
    "failure_looks_like": [
      "Version drift across fleet",
      "Unresolved incidents",
      "Isolated patterns that don't propagate"
    ]
  },
  "identity_dimensions": {
    "role": "Fleet Coordinator (action-taking)",
    "scope": "28 agents across 4 portfolios",
    "relationship_to_supervisor": "Self-managed (root of hierarchy)"
  },
  "operating_principles": [
    "Fleet health over individual agent optimization",
    "Evidence-based pattern deployment",
    "Cross-portfolio consistency"
  ],
  "archetype": "Supervisor",
  "fleet_scope": "main, ccb, predictionworks, rkb"
}
```

---

## Validation

### V-Tests

```bash
# V1: JSON is valid
cat .aget/identity.json | python3 -m json.tool > /dev/null
# Expected: Exit 0 (valid JSON)

# V2: north_star is object with statement (CRITICAL)
jq -e '.north_star.statement' .aget/identity.json > /dev/null
# Expected: Exit 0 (statement exists)

# V3: north_star.type is valid
jq -e '.north_star.type | . == "purpose" or . == "ambition" or . == "curiosity" or . == "wonder"' .aget/identity.json
# Expected: true

# V4: name field exists
jq -e '.name' .aget/identity.json > /dev/null
# Expected: Exit 0

# V5: created field exists
jq -e '.created' .aget/identity.json > /dev/null
# Expected: Exit 0

# Full validation script
python3 validation/validate_identity_json.py .aget/identity.json
# Expected: All checks pass
```

### Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'str' object has no attribute 'get'` | `north_star` is string, not object | Convert to object with `statement` field |
| `KeyError: 'statement'` | Missing statement in north_star | Add `statement` field |
| `jq: error: null` | Field doesn't exist | Add required field |

---

## Migration Guide

### From String north_star to Object

**Before (INVALID)**:
```json
{
  "north_star": "Research CLI agent subsystems"
}
```

**After (VALID)**:
```json
{
  "north_star": {
    "type": "purpose",
    "statement": "Research CLI agent subsystems",
    "success_looks_like": ["..."],
    "failure_looks_like": ["..."]
  }
}
```

### Migration Script

```bash
# Check if migration needed
if jq -e '.north_star | type == "string"' .aget/identity.json > /dev/null 2>&1; then
  echo "Migration needed: north_star is string"
  # Extract current string
  OLD_NS=$(jq -r '.north_star' .aget/identity.json)
  # Create new object structure
  jq --arg stmt "$OLD_NS" '.north_star = {type: "purpose", statement: $stmt, success_looks_like: [], failure_looks_like: []}' .aget/identity.json > .aget/identity.json.new
  mv .aget/identity.json.new .aget/identity.json
  echo "Migrated. Please add success/failure indicators."
else
  echo "No migration needed"
fi
```

---

## Compatibility Notes

### Session Script Requirements

| Script | Fields Used | Requirement |
|--------|-------------|-------------|
| wake_up.py | `north_star.type`, `north_star.statement` | north_star MUST be object |
| wind_down.py | `name`, `north_star.statement` | Same as wake_up.py |

### Backward Compatibility

Scripts SHOULD handle both formats gracefully:

```python
# Defensive handling pattern
ns = identity.get('north_star', {})
if isinstance(ns, str):
    # Legacy format
    ns_statement = ns
    ns_type = 'purpose'
else:
    # Current format
    ns_type = ns.get('type', 'purpose')
    ns_statement = ns.get('statement', '')
```

---

## Related Documents

- AGET_INSTANCE_SPEC.md - Parent specification
- SOP_aget_create.md - References this schema
- L488: SOP Template vs Operational Reality Gap
- L489: Validation-Operation Gap
- L490: Schema Shape V-Tests

---

**Schema Version**: 1.0.0
**Effective Date**: 2026-01-08
**Review Cycle**: On schema change or consumer update
