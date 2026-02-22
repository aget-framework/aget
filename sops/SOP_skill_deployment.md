# SOP: Skill Deployment

**Version**: 1.0.0
**Status**: Active
**Created**: 2026-02-15
**Author**: aget-framework
**Category**: Skills
**Spec Reference**: SKILL_NAMING_CONVENTION_SPEC v1.1.0 (CAP-SKILL-DEP-001)

---

## Purpose

This SOP defines the deployment process for AGET skills, ensuring dependencies are validated before deployment per R-SKILL-DEP-001. Prevents the class of runtime failures documented in L586.

---

## Scope

**Applies to**: All skill deployments to `.claude/skills/`
**Audience**: AGET maintainers, template authors, fleet agents

---

## Pre-Requisites

- Skill SKILL.md file complete
- Skill tested in development
- All referenced dependencies created

---

## Deployment Process

### Phase 1: Pre-Deployment Validation

**Duration**: Before any file operations

#### V1.1: Naming Convention Check

```bash
# Verify skill name follows aget-{verb}-{noun} pattern
skill_name="aget-create-project"  # Replace with actual name

if [[ ! "$skill_name" =~ ^aget-[a-z]+-[a-z]+(-[a-z]+)?$ ]]; then
  echo "FAIL: Invalid skill name pattern"
  exit 1
fi
```

**Reference**: R-SKILL-NAME-001 through R-SKILL-NAME-005

#### V1.2: Dependency Validation (R-SKILL-DEP-001)

```bash
# Run dependency validator
python3 aget/validation/validate_skill_dependencies.py \
  --skill .claude/skills/aget-create-project/ \
  --check

# Expected: exit 0
# If exit 1: Do NOT proceed until dependencies created
```

**If validation fails**:
1. List missing dependencies from validator output
2. Create each missing dependency:
   - Templates: Create in `templates/{category}/`
   - Specs: Create stub in `specs/` (stub acceptable per R-SKILL-DEP-004)
   - Directories: Create with README
3. Re-run validation until PASS

#### V1.3: Spec Synchronization Check

```bash
# Verify spec filename matches skill name
spec_file="specs/skills/SKILL-NNN_${skill_name}.yaml"
skill_dir=".claude/skills/${skill_name}/"

if [[ -f "$spec_file" ]] && [[ -d "$skill_dir" ]]; then
  echo "PASS: Spec-skill synchronized"
else
  echo "WARN: Spec or skill directory missing"
fi
```

**Reference**: R-SKILL-NAME-020 through R-SKILL-NAME-022

---

### Phase 2: Deployment

**Duration**: After validation passes

#### D2.1: Copy Skill Directory

```bash
# Deploy skill to target
cp -r path/to/skill/ .claude/skills/aget-{verb}-{noun}/
```

#### D2.2: Verify Deployment

```bash
# Confirm skill directory exists
test -d ".claude/skills/aget-{verb}-{noun}/" && echo "PASS" || echo "FAIL"

# Confirm SKILL.md exists
test -f ".claude/skills/aget-{verb}-{noun}/SKILL.md" && echo "PASS" || echo "FAIL"
```

---

### Phase 3: Post-Deployment Validation

**Duration**: After deployment

#### P3.1: Re-run Dependency Check

```bash
# Confirm dependencies still valid from deployment location
python3 aget/validation/validate_skill_dependencies.py \
  --skill .claude/skills/aget-{verb}-{noun}/ \
  --check
```

#### P3.2: Functional Test

Invoke skill with minimal input to verify it works:

```
/aget-{verb}-{noun} --help
```

or equivalent minimal invocation.

---

## Decision Points

| Gate | Decision | If FAIL |
|------|----------|---------|
| V1.1 | Name valid? | Rename skill, restart |
| V1.2 | Dependencies exist? | Create dependencies, re-validate |
| V1.3 | Spec synchronized? | Rename spec to match |
| P3.1 | Post-deploy valid? | Investigate path resolution |
| P3.2 | Skill invokable? | Debug skill logic |

---

## Anti-Patterns

| Anti-Pattern | Detection | Consequence |
|--------------|-----------|-------------|
| Deploy without validation | Skip V1.2 | Runtime failures (L586) |
| Create stubs post-deploy | "We'll add templates later" | Skills fail silently |
| Force validation pass | `--force` flag abuse | Technical debt |

---

## Checklist

```markdown
## Skill Deployment: {skill-name}

### Pre-Deployment
- [ ] Skill name follows `aget-{verb}-{noun}` pattern
- [ ] `validate_skill_dependencies.py --check` passes
- [ ] Spec filename matches skill name

### Deployment
- [ ] Skill directory copied to `.claude/skills/`
- [ ] SKILL.md present

### Post-Deployment
- [ ] Dependency validation passes from deployment location
- [ ] Skill invokable with minimal input
```

---

## Traceability

| Link | Reference |
|------|-----------|
| Spec | SKILL_NAMING_CONVENTION_SPEC v1.1.0 |
| Requirements | CAP-SKILL-DEP-001 (R-SKILL-DEP-001 through R-SKILL-DEP-005) |
| Validator | validation/validate_skill_dependencies.py |
| Trigger | L586 (Skill Infrastructure Deployment Gap) |
| Related | L582 (Universal Skill Customization Preservation) |

---

*SOP_skill_deployment.md v1.0.0*
*"Validate before deploy, prevent runtime failures"*
