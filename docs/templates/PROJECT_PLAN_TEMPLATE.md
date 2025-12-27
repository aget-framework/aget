# PROJECT_PLAN: [Title]

**Part of**: [Parent version or initiative]
**Master Scope**: [VERSION_SCOPE_vX.Y.md reference]

**Version**: 1.0
**Date**: YYYY-MM-DD
**Owner**: [agent-name]
**Supervisor**: [supervisor-agent-name]
**Status**: DRAFT | READY FOR APPROVAL | IN PROGRESS | COMPLETED
**Trigger**: [What prompted this plan]
**Prerequisites**: [What must be complete before starting]
**Change Proposals**: [CP-NNN list]
**VERSION_SCOPE Reference**: planning/VERSION_SCOPE_vX.Y.md

---

## Executive Summary

**Objective**: [1-2 sentence description of what this plan accomplishes]

**Origin**: [How this plan came about - discovery, user request, etc.]

**Deliverables**:
1. [Primary deliverable]
2. [Secondary deliverable]
3. ...

**Estimated Effort**: [Total hours/sessions]
**Risk Level**: Low | Medium | High

---

## Part 0: Discovery & Scope Definition

### 0.1 Discovery Process

[Document how scope was determined - Q&A sessions, research, analysis]

### 0.2 Scope Definition

#### Change Proposals Included

| ID | Title | Type | Impact |
|----|-------|------|--------|
| CP-NNN | [Title] | New Spec / Enhancement / Process | MAJOR / MINOR / PATCH |

#### Version Impact Assessment

- **Breaking changes**: [Yes/No - describe if yes]
- **New specifications**: [Count]
- **Spec updates**: [List]
- **Template updates**: [Count]
- **Version type**: MAJOR | MINOR | PATCH

#### Deferred Items

| Item | Reason |
|------|--------|
| [Feature] | [Why deferred] |

---

## Part 1: Design Decisions Record

### Decision 1: [Topic]

**Context**: [Why this decision is needed]

**Options Considered**:
- A) [Option A description]
- B) [Option B description]
- C) [Option C description]

**Decision**: [Selected option]

**Rationale**: [Why this option was chosen]

[Repeat for each significant decision]

---

## Part 2: Objectives & Key Results

### Objective

[Primary objective statement]

### Key Results

**KR1: [Result Name]**
- Measurement: [How to measure]
- Deliverables: [What is produced]
- Success: [What success looks like]

[Repeat for each key result]

---

## Part 3: Gate Structure

```
G-0: [Gate Name] (XX min)
     │
     ▼ [GO/NOGO]
G-1: [Gate Name] (XX min)
     │
     ▼ [GO/NOGO]
G-2: [Gate Name] (XX min)
     │
     ▼ [GO/NOGO]
...
G-N: Validation & Release (XX min)
     │
     ▼ [COMPLETE]
```

**Total Estimated Effort**: [Sum of gate estimates]

---

## G-0: [Gate Name]

**Objective**: [What this gate accomplishes]

**Prerequisites**:
- [ ] [What must be true before starting]

**Deliverables**:

| # | Deliverable | Verification |
|---|-------------|--------------|
| 0.1 | [Artifact] | [How to verify] |
| 0.2 | [Artifact] | [How to verify] |

**Verification Tests** (L382 - MANDATORY):

```bash
# Test 0.1: [Description]
[executable command]
# Expected: [output pattern]

# Test 0.2: [Description]
[executable command]
# Expected: [output pattern]
```

**Success Criteria**:
- [ ] All verification tests pass
- [ ] [Additional criteria]

**Decision Point**:
- **GO**: [Conditions for proceeding]
- **NOGO**: [Conditions for stopping/revising]

---

## G-1: [Gate Name]

**Objective**: [What this gate accomplishes]

**Location**: `[path/to/artifact]`

**Deliverables**:

| # | Deliverable | Verification |
|---|-------------|--------------|
| 1.1 | [Artifact] | [How to verify] |

**Verification Tests** (L382 - MANDATORY):

```bash
# Test 1.1: [Description]
[executable command]
# Expected: [output pattern]
```

**Success Criteria**:
- [ ] All verification tests pass

**Decision Point**:
- **GO**: [Conditions]
- **NOGO**: [Conditions]

---

## G-N: Validation & Release

**Objective**: Validate all deliverables and release.

**Deliverables**:

| # | Deliverable | Verification |
|---|-------------|--------------|
| N.1 | Run all validators | All pass |
| N.2 | Cross-reference check | All refs valid |
| N.3 | Integration tests | Tests pass |
| N.4 | Git tag | Tagged |
| N.5 | Release notes | Created |

**Verification Tests** (L382 - MANDATORY):

```bash
# Test N.1: Validator suite
python3 validation/validate_[relevant].py [target]
# Expected: ✅ X/X valid

# Test N.2: Cross-references
python3 validation/validate_cross_references.py --dir [path]
# Expected: ✅ X/X files have valid references

# Test N.3: Integration tests
python3 -m pytest tests/ -v
# Expected: X passed

# Test N.4: Artifacts created
ls -la [expected artifacts]
# Expected: Files exist with correct content

# Test N.5: Tag verification
git tag -l 'vX.Y*'
# Expected: vX.Y.Z listed
```

**Success Criteria**:
- [ ] ALL verification tests pass (no exceptions)
- [ ] No FAIL or ERROR status
- [ ] Git clean, ready to push

**Decision Point**:
- **COMPLETE**: All tests pass
- **NOGO**: Fix issues, re-validate

---

## Part 4: Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | Low/Med/High | Low/Med/High | [How to mitigate] |

---

## Part 5: Dependencies

**Upstream** (blocks this):
- [Dependency]

**Downstream** (blocked by this):
- [What this enables]

---

## Part 6: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| [Metric] | [Target value] | [How measured] |

---

## Part 7: Rollback Procedures

### Per-Deliverable Rollback

```bash
# Rollback [artifact]
git checkout -- [path]
```

### Full Rollback

```bash
# Complete rollback
git reset --hard [commit-before-start]
```

---

## Part 8: Approval

**Plan Status**: [Current status]

**Approval Required**: [Who must approve]

**Next Step**: [What happens after approval]

---

## Appendix A: Verification Test Reference

Per PATTERN_gate_verification_tests.md (L382):

| Gate Creates | Validator to Use |
|--------------|------------------|
| Specification | validate_spec_format.py (if exists) |
| Process YAML | validate_process_spec.py |
| Change Proposal | validate_change_proposal.py |
| PROJECT_PLAN | validate_project_plan.py |
| L-doc | validate_learning_doc.py |
| Pattern | validate_graduation_history.py |
| Any markdown | validate_cross_references.py |
| Template changes | validate_template_manifest.py |
| Vocabulary | validate_vocabulary.py |

---

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | YYYY-MM-DD | Initial plan |

---

*PROJECT_PLAN Template v2.0*
*Enhanced with L382 Gate Verification Tests*
*See: docs/patterns/PATTERN_gate_verification_tests.md*
