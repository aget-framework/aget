# AGET Identity JSON Schema Specification

**Version**: 1.1.0
**Created**: 2026-01-08
**Updated**: 2026-03-16
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
    "relationship_to_supervisor": "Child agent managed by my-supervisor-agent",
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
  "name": "my-supervisor-agent",
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

## Requirements

| ID | Pattern | Statement | V-Test |
|----|---------|-----------|--------|
| CAP-IDJSON-001 | ubiquitous | The SYSTEM shall store agent identity in a valid JSON file at `.aget/identity.json`. | V1 |
| CAP-IDJSON-002 | ubiquitous | The Identity_File shall contain a `name` field of type string. | V4 |
| CAP-IDJSON-003 | ubiquitous | The Identity_File shall contain a `north_star` field of type object. | V2 |
| CAP-IDJSON-004 | ubiquitous | The North_Star object shall contain a `type` field with value in: "purpose", "ambition", "curiosity", "wonder". | V3 |
| CAP-IDJSON-005 | ubiquitous | The North_Star object shall contain a `statement` field of type string with length greater than 10 characters. | V2 |
| CAP-IDJSON-006 | ubiquitous | The Identity_File shall contain a `created` field in ISO date format. | V5 |
| CAP-IDJSON-007 | prohibited | The `north_star` field shall NOT be a bare string. | V2 |
| CAP-IDJSON-008 | optional | WHERE Archetype_Specific_Fields are included, the Identity_File should include the `archetype` field. | — |

**Vocabulary**: Identity_File, North_Star, Archetype_Specific_Fields, Enforcement_Status

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-ID-001 | CAP-IDJSON-001 | automated | Validate that `.aget/identity.json` is valid JSON |
| V-ID-002 | CAP-IDJSON-002 | automated | Verify `name` field exists and is a string |
| V-ID-003 | CAP-IDJSON-003 | automated | Verify `north_star` field is an object (not a string) |
| V-ID-004 | CAP-IDJSON-004 | automated | Verify `north_star.type` is one of: purpose, ambition, curiosity, wonder |
| V-ID-005 | CAP-IDJSON-005 | automated | Verify `north_star.statement` exists and length > 10 characters |
| V-ID-006 | CAP-IDJSON-006 | automated | Verify `created` field exists in ISO date format |
| V-ID-007 | CAP-IDJSON-007 | automated | Verify `north_star` is NOT a bare string (prohibited pattern) |
| V-ID-008 | CAP-IDJSON-008 | inspection | Where archetype-specific fields are present, verify `archetype` field is included |

### Validation Commands

```bash
# Validate JSON syntax (V-ID-001)
cat .aget/identity.json | python3 -m json.tool > /dev/null
# Expected: Exit 0 (valid JSON)

# Verify north_star is object with statement (V-ID-003, V-ID-005, V-ID-007)
jq -e '.north_star.statement' .aget/identity.json > /dev/null
# Expected: Exit 0 (statement exists)

# Verify north_star.type is valid (V-ID-004)
jq -e '.north_star.type | . == "purpose" or . == "ambition" or . == "curiosity" or . == "wonder"' .aget/identity.json
# Expected: true

# Verify name field exists (V-ID-002)
jq -e '.name' .aget/identity.json > /dev/null
# Expected: Exit 0

# Verify created field exists (V-ID-006)
jq -e '.created' .aget/identity.json > /dev/null
# Expected: Exit 0

# Full validation script (all V-ID-* tests)
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

## Deprecation Schedule

### north_star String Format

| Phase | Version | Status | Behavior |
|-------|---------|--------|----------|
| De facto deprecated | v3.0.0 | **Current** | String format causes wake_up.py `AttributeError`. No formal deprecation notice. |
| Formal deprecation | v3.7.0 | Planned | `validate_identity_json.py` emits WARNING for string format. Migration guide referenced. |
| Hard removal | v4.0.0 | Planned | String format rejected by validation. Object format required. |

**Migration**: See [From String north_star to Object](#from-string-north_star-to-object) below.

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

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-03-16 | Added EARS-patterned requirements (CAP-IDJSON-001 through 008). Cross-referenced V-tests to CAP IDs. Per L682 maturity uplift L0→L1. |
| 1.0.0 | 2026-01-08 | Initial schema specification. |

---

**Schema Version**: 1.1.0
**Effective Date**: 2026-01-08
**Review Cycle**: On schema change or consumer update
