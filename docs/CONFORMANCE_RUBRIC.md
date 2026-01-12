# AGET v3.x Conformance Assessment Rubric

**Version**: 1.0.0
**Date**: 2026-01-11
**Status**: Active
**Implements**: L518 (Conformance Assessment Rubric Pattern)
**Validator**: `aget/validation/validate_conformance.py`

---

## Purpose

This rubric provides a standardized framework for assessing AGET agent conformance to v3.x 5D Composition Architecture standards. It supports:

- **Self-Assessment**: Agents can evaluate their own conformance
- **Fleet Governance**: Supervisors can systematically assess fleet health
- **Upgrade Validation**: Post-upgrade conformance verification
- **Gap Identification**: Actionable remediation guidance

---

## Quick Reference Card

### Minimum Viable Agent (L2 Compliant)

An agent needs these 10 items to achieve L2 Compliant status:

- [ ] `.aget/version.json` with aget_version, agent_name, archetype
- [ ] `.aget/identity.json` with north_star
- [ ] `AGENTS.md` with session protocols
- [ ] `CLAUDE.md` symlink to AGENTS.md
- [ ] `governance/CHARTER.md` with scope
- [ ] `.aget/evolution/` with 1+ L-docs
- [ ] `planning/` directory
- [ ] `manifest.yaml` with capabilities
- [ ] One governance capability declared
- [ ] 60%+ composite score

### Quick Assessment

```bash
# Run conformance assessment
python3 aget/validation/validate_conformance.py /path/to/agent

# Verbose output with all checks
python3 aget/validation/validate_conformance.py /path/to/agent --verbose

# JSON output for automation
python3 aget/validation/validate_conformance.py /path/to/agent --json
```

---

## Conformance Levels

| Level | Score Range | Description | Action |
|-------|-------------|-------------|--------|
| **L3 Exemplary** | 85-100% | Exceeds requirements, reference implementation | Share as model |
| **L2 Compliant** | 60-84% | Meets v3.x CAP requirements | Production ready |
| **L1 Baseline** | 40-59% | Meets structural minimums | Scheduled remediation |
| **L0 Non-Conformant** | <40% | Fails critical requirements | Immediate action |

### Critical Requirements

These failures cause immediate L0 classification regardless of score:

| Requirement | Check |
|-------------|-------|
| `.aget/version.json` exists | File present |
| `.aget/identity.json` exists | File present |
| `AGENTS.md` exists | File present |
| `governance/` exists | Directory present |
| `manifest.yaml` exists (templates) | File present for instance_type=template |
| AGENTS.md size | < 40,000 characters |

---

## Assessment Dimensions

### Dimension Weights

| Dimension | Weight | Focus |
|-----------|--------|-------|
| D1 PERSONA | 15% | Identity, governance, goals |
| D2 MEMORY | 25% | Learning, sessions, continuity |
| D3 REASONING | 25% | Planning, gates, decisions |
| D4 SKILLS | 20% | Capabilities, tools, tests |
| D5 CONTEXT | 15% | Relationships, scope, environment |

---

## D1: PERSONA (15%)

*WHO is this agent?*

### P1: Archetype Declaration

| Score | Criteria |
|-------|----------|
| 5 | Archetype in version.json + AGENTS.md + manifest.yaml |
| 4 | Archetype in version.json + AGENTS.md |
| 3 | Archetype in version.json |
| 2 | Template field only (no archetype) |
| 1 | Neither template nor archetype |
| 0 | version.json missing/unreadable |

### P2: Governance Intensity

| Score | Criteria |
|-------|----------|
| 5 | Governance capability + behavioral examples |
| 4 | Exactly one governance capability declared |
| 3 | Governance capability declared |
| 2 | Multiple governance capabilities (conflict) |
| 1 | No governance capability (defaults to balanced) |
| 0 | manifest.yaml missing |

**Valid governance capabilities**:
- `capability-governance-rigorous`
- `capability-governance-balanced`
- `capability-governance-exploratory`

### P3: Identity Artifacts

| Score | Criteria |
|-------|----------|
| 5 | All 5 files + rich content |
| 4 | All 5 files present |
| 3 | 3+ core files (identity.json, version.json, CHARTER.md) |
| 2 | 2 files only |
| 1 | 1 file only |
| 0 | No identity files |

**Required files**: `.aget/version.json`, `.aget/identity.json`, `governance/CHARTER.md`, `governance/MISSION.md`, `AGENTS.md`

### P4: Goal Orientation (North Star)

| Score | Criteria |
|-------|----------|
| 5 | North Star (object) + Mission + Objectives |
| 4 | North Star defined (object format with statement) |
| 3 | North Star defined (string format) |
| 2 | Purpose in AGENTS.md only |
| 1 | Vague purpose |
| 0 | No goal orientation |

### P5: Version Coherence (L444)

| Score | Criteria |
|-------|----------|
| 5 | Version matches in version.json AND AGENTS.md |
| 4 | Version coherent across sources |
| 3 | Single version source |
| 2 | Version mismatch detected |
| 1 | Partial version info |
| 0 | No version information |

---

## D2: MEMORY (25%)

*WHAT does this agent know?*

### M1: Memory Structure

| Score | Criteria |
|-------|----------|
| 5 | All 6 layers + documented boundaries |
| 4 | All 6 memory layers present |
| 3 | 4+ core layers |
| 2 | 2-3 layers |
| 1 | 1 layer |
| 0 | No memory structure |

**Memory layers**: `.aget/evolution/`, `.aget/patterns/`, `governance/`, `planning/`, `sessions/`, `inherited/`

### M2: Learning Capture

| Score | Criteria |
|-------|----------|
| 5 | 10+ L-docs |
| 4 | 5-9 L-docs |
| 3 | 1-4 L-docs |
| 2 | evolution/ exists but empty |
| 1 | No evolution/ directory |
| 0 | No learning mechanism |

### M3: Session Protocols

| Score | Criteria |
|-------|----------|
| 5 | Scripts exist + execute <1s + documented |
| 4 | wake_up.py + wind_down.py present and functional |
| 3 | Partial scripts (wake or wind) |
| 2 | Protocols documented in AGENTS.md only |
| 1 | Minimal protocol documentation |
| 0 | No session protocols |

### M4: Core Memory Directories

| Score | Criteria |
|-------|----------|
| 5 | All 4 + well-organized |
| 4 | All 4 core directories present |
| 3 | 3 directories |
| 2 | 2 directories |
| 1 | 1 directory |
| 0 | No directories |

**Core directories**: `governance/`, `planning/`, `sessions/`, `knowledge/`

### M5: CLAUDE.md Symlink

| Score | Criteria |
|-------|----------|
| 5 | CLAUDE.md symlink → AGENTS.md (correct) |
| 3 | CLAUDE.md symlink to different target |
| 2 | CLAUDE.md exists but not symlink |
| 0 | CLAUDE.md missing |

---

## D3: REASONING (25%)

*HOW does this agent think?*

### R1: Planning Patterns

| Score | Criteria |
|-------|----------|
| 5 | 5+ PROJECT_PLANs with retrospectives |
| 4 | 5+ PROJECT_PLANs |
| 3 | 2-4 PROJECT_PLANs |
| 2 | 1 PROJECT_PLAN |
| 1 | planning/ exists but empty |
| 0 | No planning/ directory |

### R2: Gate Discipline

| Score | Criteria |
|-------|----------|
| 5 | Perfect gate discipline + documented |
| 4 | 80%+ plans have gates |
| 3 | 50%+ plans have gates |
| 2 | Some gates |
| 1 | No gate structure |
| 0 | No plans to evaluate |

### R3: Decision Framework

| Score | Criteria |
|-------|----------|
| 5 | Authority matrix + precedent citation |
| 4 | Authority matrix documented |
| 3 | Decision authority documented |
| 2 | No explicit decision framework |
| 1 | Unclear decision authority |
| 0 | No guidance |

### R4: V-Tests in Plans

| Score | Criteria |
|-------|----------|
| 5 | V-tests in all plans + executable |
| 4 | V-tests in 80%+ plans |
| 3 | V-tests in 50%+ plans |
| 2 | V-tests in some plans |
| 1 | No V-tests |
| 0 | No plans to evaluate |

### R5: 5D Directories

| Score | Criteria |
|-------|----------|
| 5 | All 5 dimension directories |
| 4 | 4 directories |
| 3 | 3 directories |
| 2 | 1-2 directories |
| 1 | No 5D directories |
| 0 | No .aget/ directory |

**5D directories**: `.aget/persona/`, `.aget/memory/`, `.aget/reasoning/`, `.aget/skills/`, `.aget/context/`

---

## D4: SKILLS (20%)

*WHAT can this agent do?*

### S1: Capability Declaration

| Score | Criteria |
|-------|----------|
| 5 | manifest.yaml + comprehensive capabilities + validated |
| 4 | Capabilities in manifest.yaml |
| 3 | Capabilities in version.json or basic manifest |
| 2 | Capabilities documented in AGENTS.md only |
| 1 | Implicit capabilities |
| 0 | No capability declaration |

### S2: Tool Availability

| Score | Criteria |
|-------|----------|
| 5 | 10+ scripts/tools |
| 4 | 5-9 scripts/tools |
| 3 | 3-4 scripts/tools |
| 2 | 1-2 scripts |
| 1 | No scripts |
| 0 | No tools |

### S3: Contract Tests

| Score | Criteria |
|-------|----------|
| 5 | 5+ test files + passing |
| 4 | 3+ test files |
| 3 | 1-2 test files |
| 2 | tests/ exists but no test_*.py |
| 1 | No tests/ directory |
| 0 | No testing |

### S4: Shell Integration (v3.3)

| Score | Criteria |
|-------|----------|
| 5 | shell/ + profile + README + aget_info() |
| 4 | shell/ + profile + README |
| 3 | shell/ + profile |
| 2 | shell/ exists but incomplete |
| 1 | No shell/ directory |
| 0 | No shell integration |

### S5: Documentation

| Score | Criteria |
|-------|----------|
| 5 | README + CHANGELOG + usage guide |
| 4 | README.md + CHANGELOG.md |
| 3 | README.md |
| 2 | CHANGELOG.md only |
| 1 | No documentation |
| 0 | No docs |

---

## D5: CONTEXT (15%)

*WHERE/WHEN does this agent operate?*

### C1: Relationship Structure

| Score | Criteria |
|-------|----------|
| 5 | managed_by + peers + escalation paths |
| 4 | managed_by documented in CHARTER |
| 3 | managed_by in version.json |
| 2 | No managed_by field |
| 1 | Unclear relationships |
| 0 | No relationship documentation |

### C2: Scope Boundaries

| Score | Criteria |
|-------|----------|
| 5 | SCOPE_BOUNDARIES.md + examples |
| 4 | SCOPE_BOUNDARIES.md present |
| 3 | Scope in CHARTER.md |
| 2 | CHARTER.md exists (no explicit scope) |
| 1 | Vague scope |
| 0 | No scope documentation |

### C3: Environmental Awareness (L185)

| Score | Criteria |
|-------|----------|
| 5 | L185 referenced + protocol documented |
| 4 | Environmental grounding documented |
| 3 | Environmental awareness mentioned |
| 2 | Implicit awareness |
| 1 | Poor awareness |
| 0 | No environmental awareness |

### C4: Archetype Directories

| Score | Criteria |
|-------|----------|
| 5 | All archetype-specific directories present |
| 4 | Most archetype directories |
| 3 | No specific requirements for archetype |
| 2 | Missing some archetype directories |
| 1 | Missing most |
| 0 | No archetype directories |

**Archetype-specific directories**:
- supervisor: `fleet/`, `sops/`
- developer: `products/`, `workspace/`, `src/`
- advisor/consultant: `clients/`, `engagements/`
- analyst: `reports/`
- architect: `decisions/`
- researcher: `research/`
- operator: `operations/`
- spec-engineer: `specs/`

---

## Remediation Patterns

### Pattern 1: Missing Identity Artifacts (D1-P3)

**Symptoms**: identity.json or CHARTER.md missing (score 0-2)

**Steps**:
1. Create `.aget/identity.json`:
   ```json
   {
     "north_star": {
       "statement": "Your agent's purpose statement"
     },
     "created": "YYYY-MM-DD"
   }
   ```
2. Create `governance/CHARTER.md` from template
3. Create `governance/MISSION.md` with goals
4. Validate: `python3 validate_conformance.py . --verbose`

**Time**: 1-2 hours

---

### Pattern 2: No Learning Capture (D2-M2)

**Symptoms**: `.aget/evolution/` empty or no L-docs

**Steps**:
1. Create `.aget/evolution/` if missing
2. Review last 5 sessions for insights
3. Create 3-5 L-docs using format:
   ```markdown
   # LNNN: Title

   **Date**: YYYY-MM-DD
   **Type**: Pattern | Gap | Discovery
   **Context**: What led to this learning
   **Outcome**: What was learned
   ```
4. Document learning protocol in AGENTS.md

**Time**: 2-3 hours

---

### Pattern 3: Missing V-Tests (D3-R4)

**Symptoms**: PROJECT_PLANs lack verification tests

**Steps**:
1. Review existing PROJECT_PLANs
2. Add V-test sections:
   ```markdown
   **V-Tests**:

   | ID | Test | Result |
   |----|------|--------|
   | V-G1.1 | Specific testable condition | PASS/FAIL |
   ```
3. Create V-test template for future use
4. Add V-test requirement to AGENTS.md

**Time**: 1-2 hours

---

### Pattern 4: No Capability Declaration (D4-S1)

**Symptoms**: manifest.yaml missing

**Steps**:
1. Create `manifest.yaml`:
   ```yaml
   manifest_version: "3.0"

   template:
     name: "agent-name"
     archetype: "worker"
     version: "3.3.0"

   capabilities:
     - capability-governance-balanced
     - capability-session-protocols
   ```
2. Identify capabilities from current behavior
3. Validate: `python3 validate_composition.py .`

**Time**: 1 hour

---

### Pattern 5: Unclear Scope Boundaries (D5-C2)

**Symptoms**: CHARTER.md missing or vague

**Steps**:
1. Create `governance/CHARTER.md`:
   ```markdown
   # Agent Charter

   ## In Scope
   - What this agent DOES

   ## Out of Scope
   - What this agent does NOT do

   ## Escalation
   - When to escalate to supervisor
   ```
2. Define explicit boundaries
3. Document escalation paths
4. Link from AGENTS.md

**Time**: 1-2 hours

---

## Assessment Workflow

### Individual Assessment

1. **Run validator**:
   ```bash
   python3 aget/validation/validate_conformance.py /path/to/agent --verbose
   ```

2. **Review results**:
   - Check composite score and level
   - Review dimension breakdown
   - Note gaps requiring attention

3. **Plan remediation** (if needed):
   - Prioritize critical failures
   - Apply remediation patterns
   - Re-run validation

### Fleet Assessment

1. **Assess each agent**:
   ```bash
   for agent in /path/to/agents/*/; do
     python3 validate_conformance.py "$agent" --json >> fleet_report.json
   done
   ```

2. **Aggregate results**:
   - Calculate fleet average
   - Identify common gaps
   - Find reference implementations

3. **Create remediation plan**:
   - Prioritize by dimension weight
   - Address common gaps fleet-wide
   - Track progress

---

## Scoring Calculation

### Composite Score Formula

```
Composite = (D1 × 0.15) + (D2 × 0.25) + (D3 × 0.25) + (D4 × 0.20) + (D5 × 0.15)
```

### Dimension Score Formula

```
Dimension_Score = Average(Check_Scores) / 5.0 × 100%
```

### Level Classification

```
if critical_failures:
    level = L0_NON_CONFORMANT
elif composite >= 85%:
    level = L3_EXEMPLARY
elif composite >= 60%:
    level = L2_COMPLIANT
elif composite >= 40%:
    level = L1_BASELINE
else:
    level = L0_NON_CONFORMANT
```

---

## References

- **Validator**: `aget/validation/validate_conformance.py`
- **Pattern**: L518 (Conformance Assessment Rubric Pattern)
- **Specs**: AGET_5D_ARCHITECTURE_SPEC, AGET_TEMPLATE_SPEC, AGET_INSTANCE_SPEC
- **Version Coherence**: L444
- **Environmental Grounding**: L185

---

*CONFORMANCE_RUBRIC.md — AGET v3.x Conformance Assessment Guide*
*"Measure twice, remediate once."*
