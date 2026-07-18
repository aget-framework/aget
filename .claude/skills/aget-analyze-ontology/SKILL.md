---
name: aget-analyze-ontology
description: Analyze ontology health and coverage across controlled vocabularies. Reports completeness, consistency, coverage, and freshness with actionable insights.
version: 1.1.0
---

# /aget-analyze-ontology

Analyze the health and coverage of AGET ontology artifacts across all controlled vocabularies.

## Purpose

Provide deep analysis of ontology health for agents managing vocabularies and specifications. Goes beyond file counts to assess semantic completeness, cross-vocabulary consistency, and actual usage coverage.

**Verb convention** (`check-` vs `analyze-`):
- `check-*` = Lightweight monitoring. Threshold pass/fail, health status, ~5 seconds. (e.g., `aget-check-kb`, `aget-check-health`)
- `analyze-*` = Deep qualitative analysis. Cross-references, coverage percentages, recommendations, ~30 seconds. (e.g., `aget-analyze-kb`, `aget-analyze-ontology`)

KB has both: `aget-check-kb` (quick health) and `aget-analyze-kb` (deep quality). Ontology currently has only `analyze-`. If fleet ontology adoption grows beyond 2 operational agents, consider splitting:
- `aget-check-ontology` = Steps 7-8 only (tier compliance + ratio check)
- `aget-analyze-ontology` = Steps 1-8 (full vocabulary analysis)

## Execution

When invoked, perform these analyses:

### 1. Vocabulary Discovery

```bash
# Find all vocabulary files
VOCABS=(
  ".aget/specs/skills/SKILL_VOCABULARY.md"
  ".aget/specs/AGET_CONTROLLED_VOCABULARY.md"
  ".aget/evolution/CONTROLLED_VOCABULARY.md"
)

for vocab in "${VOCABS[@]}"; do
  test -f "$vocab" && echo "Found: $vocab" || echo "Missing: $vocab"
done
```

### 2. Term Extraction

Extract defined terms from each vocabulary:
- Parse markdown headers and definition tables
- Count terms per vocabulary
- Build unified term registry

### 3. Completeness Check

Scan specifications for term usage:

```bash
# Find terms used in specs
grep -oh '\b[A-Z][a-z]*_[A-Z][a-z]*\b' .aget/specs/skills/*.yaml | sort -u

# Compare against vocabulary definitions
# Report undefined terms
```

### 4. Consistency Check

Compare term definitions across vocabularies:
- Same term should have same definition
- Flag conflicts with both definitions
- Suggest canonical source

### 5. Coverage Analysis

Calculate what percentage of specification terms are vocabulary-defined:

```
Coverage = (defined_terms_used / total_terms_used) * 100
```

### 6. Freshness Check

Identify vocabulary terms with no recent usage:
- Scan spec modification dates
- Flag terms not referenced in 90+ days

### 7. Tier Assessment

Assess ontology operational depth per ONTOLOGY_TIER_SPEC_v1.0.yaml:

1. Read `ontology_tier` from `.aget/version.json` (default to `inherited` if absent)
2. Validate tier-specific requirements:
   - **Inherited**: `ontology/` exists AND at least one YAML file declares `extends:` → COMPLIANT
   - **Domain**: >=25 domain-specific SKOS terms AND zero collisions with framework vocabulary → COMPLIANT; else GAP
   - **Operational**: All Domain requirements met AND at least one skill in `.claude/skills/` references ontology content AND ontology status surfaced in lifecycle → COMPLIANT; else GAP
3. Check `extends:` resolution: If `extends:` value cannot be matched to a known canonical vocabulary (`aget_core.yaml`, `ONTOLOGY_personal_ai_systems_v1.0.yaml`), report WARN
4. Report tier, compliance status, and specific gaps

### 8. Concept-to-Requirement Ratio (OT-022)

For Domain and Operational tier agents, calculate vocabulary consumption balance:

1. Count concepts: `grep -c "prefLabel" ontology/*.yaml vocabulary/*.yaml 2>/dev/null`
2. Count EARS requirements: `grep -c "^  R-\|^R-" .aget/specs/*.yaml 2>/dev/null`
3. Calculate ratio: `concept_count / requirement_count`
4. Classify:

| Ratio | Status | Interpretation |
|-------|--------|---------------|
| < 1.0 | UNDER_SPECIFIED | More requirements than vocabulary to ground them |
| 1.0 - 3.0 | HEALTHY | Vocabulary supports specification work |
| > 3.0 | CONCEPT_SURPLUS | Vocabulary growing faster than consumption |
| > 10.0 | SELF_REFERENTIAL | Ontology may be its own domain, not supporting the agent's domain |

5. For Inherited tier agents: Skip ratio check (OT-021 exemption)
6. Report status with ratio value and recommendation

## Thresholds

| Metric | OK | WARN | CRITICAL |
|--------|-----|------|----------|
| Undefined terms | 0-3 | 4-10 | >10 |
| Inconsistencies | 0 | 1-5 | >5 |
| Coverage | >90% | 80-90% | <80% |
| Stale terms | <10 | 10-25 | >25 |

## Output Format

```
=== /aget-analyze-ontology ===

Vocabularies scanned: 3
Total terms: 158

Health Status: [OK | WARN | CRITICAL]

Completeness:
  Defined terms: 158
  Terms used in specs: 142
  Undefined terms: 4
    - Foo_Bar (SKILL-014)
    - Baz_Qux (SKILL-015)
    ...

Consistency:
  Cross-vocabulary conflicts: 1
    - "Session" differs between SKILL_VOCABULARY and CONTROLLED_VOCABULARY

Coverage:
  SKILL_VOCABULARY: 29 terms, 92% coverage
  AGET_CONTROLLED_VOCABULARY: 100 terms, 87% coverage
  CONTROLLED_VOCABULARY: 29 terms, 78% coverage

Freshness:
  Active terms (used in 30 days): 120
  Stale terms (90+ days no usage): 12

Tier Assessment:
  Tier: operational (from version.json)
  Status: COMPLIANT
  Domain terms: 8 (SKOS)
  Consuming skills: 2 (aget-analyze-ontology, aget-analyze-kb)
  Lifecycle: wake_up.py ontology line present

Concept-to-Requirement Ratio:
  Concepts: 12
  EARS Requirements: 14
  Ratio: 0.86:1
  Status: UNDER_SPECIFIED

Recommendations:
1. Add definitions for 4 undefined terms
2. Resolve "Session" definition conflict
3. Review 12 stale terms for deprecation
```

## Health Status Logic

```
IF undefined_terms > 10 OR inconsistencies > 5:
  CRITICAL
ELIF undefined_terms > 3 OR inconsistencies > 0 OR coverage < 80%:
  WARN
ELSE:
  OK
```

## Constraints

- **C1**: Read-only operation. Never modify vocabulary or spec files.
- **C2**: Scan all three vocabulary sources.
- **C3**: Report actionable recommendations.

## Invocation Recording

After completing this skill's primary actions, record the invocation:
```bash
python3 scripts/record_invocation.py aget-analyze-ontology
```
## Related Skills

- `/aget-healthcheck-kb` - Quick KB threshold check
- `/aget-analyze-kb` - Deep KB quality analysis
- `/aget-healthcheck-evolution` - Evolution directory health

## Traceability

| Link | Reference |
|------|-----------|
| Spec | SKILL-014_aget-analyze-ontology.yaml (AO-001 through AO-011) |
| Spec | ONTOLOGY_TIER_SPEC_v1.0.yaml (OT-010, OT-011, OT-022) |
| Proposal | PROPOSAL_aget-analyze-ontology.md |
| L-docs | L537 (Verb Taxonomy), L322 (Knowledge Taxonomy), L525 (Ontology-First), L564 (Demand-Side), L565 (Behavioral Gap), L566 (Value Attribution) |
| Project | v3.5.0 Ontology Research |

---

*aget-analyze-ontology v1.1.0*
*Category: Monitoring*
*SKILL-014*
