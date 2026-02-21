# SOP: Instance_Migration to v3.0

**Version**: 1.2.0
**Created**: 2025-12-27
**Updated**: 2026-02-14 (v3.5.0 ontology/skill migration steps)
**Owner**: aget-framework
**Implements**: CAP-MIG-001 (Instance_Migration), CAP-SOP-001 (SOP structure)
**Traces to**: AGET_MIGRATION_SPEC.md, AGET_INSTANCE_SPEC.md
**Related**: L395 (Instance v3.0 Migration Pattern), L400 (Conceptual vs Structural)
**Applies To**: All AGET instances migrating from v2.x to v3.0 (also applicable for v3.4->v3.5)

---

## Purpose

Standard operating procedure for Instance_Migration from v2.x to v3.0 5D Composition Architecture. This SOP prevents common misconceptions and ensures Structural_Validation compliance.

---

## Prerequisites

Before starting migration:

- [ ] Agent has `.aget/version.json` with `aget_version: "2.x"`
- [ ] Agent has `AGENTS.md` (or `CLAUDE.md` symlink)
- [ ] Git repository initialized and clean
- [ ] Access to aget-framework/aget validation tools

---

## Pre-Migration Checkpoint (CRITICAL)

**Stop and verify understanding before proceeding**:

| Statement | Confirm |
|-----------|---------|
| 5D creates DIRECTORIES in `.aget/`, not SECTIONS in AGENTS.md | [ ] |
| knowledge/ content STAYS AS-IS (organic naming preserved) | [ ] |
| identity.json is REQUIRED (separate from version.json) | [ ] |
| governance/, planning/, knowledge/ are REQUIRED visible directories | [ ] |
| PROJECT_PLANs belong in `planning/`, not `.aget/specs/` | [ ] |

**If any statement is unclear, read L395 and L400 before proceeding.**

---

## Common Misconceptions (L400)

| What You Might Think | Actual Requirement |
|---------------------|-------------------|
| "Add 5D sections to AGENTS.md" | Create `.aget/{persona,memory,reasoning,skills,context}/` directories |
| "Use 5d_status field" | Use `manifest_version: "3.0"` |
| "Rename FOUNDATIONAL_* to D3_REASONING_*" | Keep organic naming; 5D is config, not content |
| "Skip identity.json" | identity.json is required per CAP-INST-001 |
| "Skip governance/" | governance/ is required per CAP-INST-002 |

---

## Migration Steps

### Step 1: Create 5D Directories (~1 min)

```bash
cd /path/to/your/agent
mkdir -p .aget/{persona,memory,reasoning,skills,context}
```

**Verification**:
```bash
ls -d .aget/*/
# Should show: persona, memory, reasoning, skills, context
```

### Step 2: Create Visible Directories (~1 min)

```bash
# Core directories (all instances)
mkdir -p governance sessions planning knowledge

# Archetype-specific (if applicable)
# operator: mkdir -p operations
# supervisor: mkdir -p fleet
# developer: mkdir -p products
```

**Verification**:
```bash
ls -d */
# Should include: governance, sessions, planning, knowledge
```

### Step 2.5: Create Ontology Directory (v3.5.0+)

```bash
# Ontology directory for archetype concepts (CAP-INST-006)
mkdir -p ontology

# Copy archetype ontology from template
ARCHETYPE=$(jq -r '.archetype' .aget/version.json)
TEMPLATE_PATH="$HOME/github/aget-framework/template-${ARCHETYPE}-aget"

if [ -f "$TEMPLATE_PATH/ontology/ONTOLOGY_${ARCHETYPE}.yaml" ]; then
  cp "$TEMPLATE_PATH/ontology/ONTOLOGY_${ARCHETYPE}.yaml" ontology/
  echo "PASS Ontology copied from template"
else
  echo "WARN No archetype ontology found in template"
fi
```

**Verification**:
```bash
ls ontology/
# Should contain: ONTOLOGY_{archetype}.yaml
```

### Step 3: Move PROJECT_PLANs (~1 min)

If PROJECT_PLANs exist in `.aget/specs/`:

```bash
# Move to correct location
mv .aget/specs/PROJECT_PLAN_*.md planning/ 2>/dev/null || echo "No PROJECT_PLANs to move"
```

### Step 4: Create identity.json (~2 min)

```bash
cat > .aget/identity.json << 'EOF'
{
  "name": "your-agent-name",
  "north_star": "Your agent's guiding purpose",
  "created": "YYYY-MM-DD",
  "version": "1.0.0"
}
EOF
```

**Customize**:
- `name`: Match agent_name in version.json
- `north_star`: The agent's primary purpose/mission

### Step 5: Add 5D Config Files (~10 min)

#### D1: Persona

```bash
cat > .aget/persona/archetype.yaml << 'EOF'
archetype: advisor  # or worker, developer, supervisor, operator, etc.
specialization: your-specialization
governance:
  intensity: balanced  # minimal | balanced | rigorous
EOF

cat > .aget/persona/style.yaml << 'EOF'
communication:
  formality: professional
  verbosity: concise
modes:
  default: collaborative
EOF
```

#### D2: Memory

```bash
cat > .aget/memory/layer_config.yaml << 'EOF'
layers:
  operational: true
  semantic: true
  episodic: true
  procedural: true
  strategic: true
  meta: true
EOF
```

#### D3: Reasoning

```bash
cat > .aget/reasoning/decision_authority.yaml << 'EOF'
autonomous:
  - l_doc_creation
  - documentation
escalate:
  - major_version
  - breaking_changes
EOF
```

#### D4: Skills

```bash
cat > .aget/skills/capabilities.yaml << 'EOF'
capabilities:
  - session-protocols
  - evolution-tracking
  - domain-knowledge
EOF
```

### Step 5.5: Verify/Deploy Archetype Skills (v3.5.0+)

For v3.5.0+ migration, verify archetype-specific skills are deployed:

```bash
ARCHETYPE=$(jq -r '.archetype' .aget/version.json)
TEMPLATE_PATH="$HOME/github/aget-framework/template-${ARCHETYPE}-aget"

# Count existing skills
EXISTING_SKILLS=$(ls .claude/skills/aget-*/SKILL.md 2>/dev/null | wc -l)
echo "Current skill count: $EXISTING_SKILLS"

# Expected: 15-16 (13 universal + 2-3 archetype)
if [ "$EXISTING_SKILLS" -lt 15 ]; then
  echo "WARN Missing archetype skills. Copying from template..."

  # Copy archetype-specific skills from template
  for skill_dir in "$TEMPLATE_PATH"/.claude/skills/aget-*/; do
    skill_name=$(basename "$skill_dir")
    if [ ! -d ".claude/skills/$skill_name" ]; then
      cp -r "$skill_dir" ".claude/skills/"
      echo "  PASS Deployed: $skill_name"
    fi
  done
fi
```

**Expected archetype skills by type**:

| Archetype | Skills |
|-----------|--------|
| worker | execute-task, report-progress |
| supervisor | broadcast-fleet, review-agent, escalate-issue |
| developer | run-tests, lint-code, review-pr |
| consultant | assess-client, propose-engagement |
| advisor | assess-risk, recommend-action |
| analyst | analyze-data, generate-report |
| architect | design-architecture, assess-tradeoffs |
| researcher | search-literature, document-finding |
| operator | handle-incident, run-playbook |
| executive | make-decision, review-budget |
| reviewer | review-artifact, provide-feedback |
| spec-engineer | validate-spec, generate-requirement |

#### D5: Context

```bash
cat > .aget/context/relationships.yaml << 'EOF'
managed_by: {supervisor-agent}
portfolio: main  # or ccb, workco, etc.
peers: []
EOF
```

### Step 6: Create Governance Files (~3 min)

```bash
cat > governance/CHARTER.md << 'EOF'
# Agent Charter

## What This Agent IS
- [Purpose 1]
- [Purpose 2]

## What This Agent IS NOT
- [Anti-purpose 1]
- [Anti-purpose 2]

## Authority
- [Autonomous decisions]
- [Escalation triggers]
EOF

cat > governance/MISSION.md << 'EOF'
# Mission

## Purpose
[One sentence purpose]

## Goals
1. [Goal 1]
2. [Goal 2]

## Success Metrics
- [Metric 1]
- [Metric 2]
EOF

cat > governance/SCOPE_BOUNDARIES.md << 'EOF'
# Scope Boundaries

## In Scope
- [In scope 1]

## Out of Scope
- [Out of scope 1]

## Escalation Triggers
- [Trigger 1]
EOF
```

### Step 7: Update version.json (~2 min)

Edit `.aget/version.json`:

```json
{
  "aget_version": "3.0.0-beta.3",
  "manifest_version": "3.0",
  "instance_type": "aget",
  "agent_name": "your-agent-name",
  "archetype": "advisor",
  "specialization": "your-specialization",
  "portfolio": "main",
  "managed_by": "{supervisor-agent}",
  "migration_history": [
    "... existing entries ...",
    "v2.x -> v3.0.0-beta.3: YYYY-MM-DD (5D Composition Architecture)"
  ]
}
```

### Step 8: Generate L-doc Index (~1 min)

If agent has 50+ L-docs:

```bash
python3 /path/to/aget/scripts/generate_ldoc_index.py .
```

**Verification**:
```bash
cat .aget/evolution/index.json | head -20
```

### Step 9: Validate (~5 min)

**9.1: Structural Validation (24 checks)**
```bash
python3 ~/github/aget-framework/aget/validation/validate_template_instance.py .
# Expected: 24/24 PASS
```

**9.2: Naming Conventions (L377)**
```bash
python3 ~/github/aget-framework/aget/validation/validate_naming_conventions.py .
# Expected: PASS
```

**9.3: Version Consistency (L377)**
```bash
python3 ~/github/aget-framework/aget/validation/validate_version_consistency.py .
# Expected: PASS (requires commit a26cbe5 for pre-release support)
```

**9.4: Legacy File Audit (L376)**
```bash
# Check for stale version-bearing files
find .aget -name "agent_manifest.yaml" 2>/dev/null
# Expected: No output (no legacy files)
```

**9.5: Contract Tests (if available)**
```bash
# Only if tests/ directory exists
[ -d "tests" ] && python3 -m pytest tests/test_identity_contract.py -v
# Expected: All tests pass
```

**9.6: Archetype Skill Validation (v3.5.0+)**
```bash
ARCHETYPE=$(jq -r '.archetype' .aget/version.json)
SKILL_COUNT=$(ls .claude/skills/aget-*/SKILL.md 2>/dev/null | wc -l)

echo "Archetype: $ARCHETYPE"
echo "Skill count: $SKILL_COUNT"

# Expected: 15-16 skills (13 universal + 2-3 archetype)
[ "$SKILL_COUNT" -ge 15 ] && echo "PASS Skill count OK" || echo "FAIL Missing skills"

# Verify archetype-specific skills
case "$ARCHETYPE" in
  worker) EXPECTED="execute-task report-progress" ;;
  supervisor) EXPECTED="broadcast-fleet review-agent escalate-issue" ;;
  developer) EXPECTED="run-tests lint-code review-pr" ;;
  *) EXPECTED="" ;;
esac

for skill in $EXPECTED; do
  [ -f ".claude/skills/aget-$skill/SKILL.md" ] && \
    echo "PASS aget-$skill" || echo "FAIL aget-$skill missing"
done
```

**All checks must pass before committing migration.**

---

## Post-Migration Verification

### Structural Verification

```bash
# Check 5D directories exist
for d in persona memory reasoning skills context; do
  [ -d ".aget/$d" ] && echo "PASS .aget/$d" || echo "FAIL .aget/$d missing"
done

# Check visible directories exist
for d in governance sessions planning knowledge; do
  [ -d "$d" ] && echo "PASS $d" || echo "FAIL $d missing"
done

# Check identity.json exists
[ -f ".aget/identity.json" ] && echo "PASS identity.json" || echo "FAIL identity.json missing"
```

### Content Verification

```bash
# Verify version
cat .aget/version.json | grep aget_version
# Should show: "3.0.0-beta.3"

# Verify manifest_version
cat .aget/version.json | grep manifest_version
# Should show: "3.0"
```

---

## Migration_Rollback

If Instance_Migration fails:

```bash
# Revert to previous version
git checkout -- .aget/version.json

# Remove new directories (if empty)
rmdir .aget/{persona,memory,reasoning,skills,context} 2>/dev/null
rmdir governance planning knowledge 2>/dev/null
```

---

## Troubleshooting

### "identity.json not found"

Create it:
```bash
cat > .aget/identity.json << 'EOF'
{
  "name": "your-agent-name",
  "north_star": "Your agent's purpose"
}
EOF
```

### "governance/ not found"

Create it with required files:
```bash
mkdir -p governance
touch governance/{CHARTER,MISSION,SCOPE_BOUNDARIES}.md
```

### Validation fails with "instance_type mismatch"

Fix version.json:
```json
{
  "instance_type": "aget"  // not "AGET" or "template"
}
```

---

## Time Estimate

| Step | Time |
|------|------|
| 5D directories | 1 min |
| Visible directories | 1 min |
| Move PROJECT_PLANs | 1 min |
| identity.json | 2 min |
| 5D config files | 10 min |
| Governance files | 3 min |
| version.json | 2 min |
| L-doc index | 1 min |
| Validation (full suite) | 5 min |
| **Total** | **~27 min** |

**Or use migration script (~2 min + 5 min validation):**
```bash
python3 ~/github/aget-framework/aget/scripts/migrate_instance_to_v3.py . \
  --archetype <archetype> \
  --specialization <specialization> \
  --north-star "Agent purpose" \
  --execute
```

---

## References

- L395: Instance v3.0 Migration Pattern
- L400: Conceptual vs Structural Migration Understanding
- AGET_INSTANCE_SPEC v1.0.0
- AGET_TEMPLATE_SPEC v3.1.0
- AGET_5D_ARCHITECTURE_SPEC v1.2.0

---

*SOP: Instance_Migration to v3.0 -- Preventing conceptual/structural confusion*
*Created: 2025-12-27 based on Instance_Migration learnings*
*Updated: 2025-12-28 -- CAP-SOP-001 vocabulary compliance*
*Updated: 2026-02-14 -- v3.5.0 ontology/skill migration (Steps 2.5, 5.5, 9.6)*
