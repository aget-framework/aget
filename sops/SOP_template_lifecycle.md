# SOP: Template Lifecycle Management

**Version**: 1.0.0
**Date**: 2026-01-11
**Status**: Active
**Owner**: aget-framework
**Implements**: L515 (Template Coherence Gap), #189 (Protocol Template Propagation)

---

## Purpose

Define the standard procedure for creating, updating, deprecating, and propagating AGET document templates. This SOP prevents template drift, ensures validator alignment, and maintains single-source-of-truth discipline.

---

## Scope

This SOP applies to:
- All document templates in `aget/templates/`
- Template updates and enhancements
- Template deprecation and removal
- Template propagation to downstream consumers

**Templates Covered**:

| Template | Location | Validator |
|----------|----------|-----------|
| PROJECT_PLAN_TEMPLATE.md | templates/ | validate_project_plan.py |
| ADR_TEMPLATE.md | templates/ | validate_adr.py |
| L_DOC_TEMPLATE.md | templates/ | — |
| SPEC_TEMPLATE.md | templates/ | validate_spec.py |
| VOCABULARY_TEMPLATE.md | templates/ | — |

---

## Prerequisites

- Template ownership (framework manager for public framework)
- Understanding of corresponding validator behavior
- Access to `aget/validation/` directory

---

## Procedure

### Phase 1: Template Creation

#### 1.1 Pre-Creation Checklist

| # | Check | Verification |
|---|-------|--------------|
| 1 | No existing template for this purpose | `ls templates/*{PURPOSE}*` returns empty |
| 2 | Clear use case documented | Enhancement request or L-doc exists |
| 3 | Validator exists or planned | `ls validation/validate_{type}.py` |

#### 1.2 Creation Process

1. **Create template in canonical location**: `aget/templates/{TYPE}_TEMPLATE.md`
2. **Include version header**:
   ```markdown
   <!-- Template Version: X.Y.Z (vAGET) -->
   ```
3. **Document required vs optional sections**
4. **Add validator alignment note** if validator exists
5. **Update CHANGELOG.md** with new template entry

#### 1.3 Validator Alignment (MANDATORY)

If a validator exists for this template type:

```bash
# Test: Template passes its own validator
python3 validation/validate_{type}.py templates/{TYPE}_TEMPLATE.md
# Expected: PASS (or clear indication this is a template file)
```

**Rule**: Templates MUST be valid instances of their own format, or validators MUST explicitly handle template files.

---

### Phase 2: Template Update

#### 2.1 Pre-Update Checklist

| # | Check | Verification |
|---|-------|--------------|
| 1 | Single canonical location exists | Only one template file |
| 2 | Change documented | Enhancement request or L-doc |
| 3 | Backward compatibility assessed | Existing documents won't fail validation |

#### 2.2 Update Process

1. **Edit canonical template only** (never create copies)
2. **Bump version in header**:
   - **Major**: Breaking format changes
   - **Minor**: New sections or features
   - **Patch**: Typo fixes, clarifications
3. **Update validator if format changed**
4. **Test validator alignment**:
   ```bash
   python3 validation/validate_{type}.py templates/{TYPE}_TEMPLATE.md
   ```
5. **Update CHANGELOG.md**

#### 2.3 Breaking Change Protocol

If update breaks existing documents:

1. Document migration path in template or separate guide
2. Consider validator `--lenient` mode for transition period
3. Notify downstream consumers via release notes
4. Set deprecation date for old format support

---

### Phase 3: Template Deprecation

#### 3.1 Deprecation Criteria

Deprecate a template when:
- Superseded by consolidated template
- Format no longer in use
- Duplicates canonical location

#### 3.2 Deprecation Process

1. **Verify no active references**:
   ```bash
   grep -r "{TEMPLATE_NAME}" aget/ --include="*.md" | grep -v CHANGELOG
   ```
2. **Update any references to point to canonical location**
3. **Remove deprecated file**:
   ```bash
   git rm templates/{DEPRECATED_TEMPLATE}.md
   # or
   git rm docs/templates/{DEPRECATED_TEMPLATE}.md
   ```
4. **Update CHANGELOG.md** with removal note
5. **Create L-doc if removal has learning value**

#### 3.3 Duplicate Prevention

**Rule**: Only ONE file with a given template purpose should exist.

**Allowed locations**:
- `aget/templates/` — canonical location for all document templates

**NOT allowed**:
- `aget/docs/templates/` — use templates/ instead
- Multiple files with same purpose in different locations

---

### Phase 4: Template Propagation (#189)

#### 4.1 Propagation Triggers

Propagate templates when:
- Major version release includes template changes
- Breaking format changes require fleet update
- Critical fix affects document validity

#### 4.2 Propagation Checklist

**Before Release**:

| # | Check | Verification |
|---|-------|--------------|
| 1 | Template version bumped | Header shows new version |
| 2 | Validator aligned | Template passes validation |
| 3 | CHANGELOG updated | Change documented |
| 4 | Release notes mention template | Deep release notes or CHANGELOG |

**After Release**:

| # | Check | Owner | Verification |
|---|-------|-------|--------------|
| 1 | Release handoff includes template changes | framework-aget | RELEASE_HANDOFF mentions templates |
| 2 | Fleet notified of template update | supervisor | Handoff delivered |
| 3 | Upgrade instructions provided | framework-aget | Migration guide if breaking |

#### 4.3 Downstream Communication

For significant template changes, include in release handoff:

```markdown
## Template Updates

| Template | Version | Change | Action Required |
|----------|---------|--------|-----------------|
| PROJECT_PLAN_TEMPLATE.md | 2.0.0 | Mandatory closure checklist | Update new plans to use |
```

---

## V-Tests Summary

| ID | Test | BLOCKING |
|----|------|----------|
| V-SOP-TL-01 | Single canonical location per template | YES |
| V-SOP-TL-02 | Template passes own validator | YES |
| V-SOP-TL-03 | Version header present | YES |
| V-SOP-TL-04 | CHANGELOG entry for changes | YES |
| V-SOP-TL-05 | No orphan references after deprecation | YES |

---

## Quick Reference

### Template Locations

```
aget/templates/           <- CANONICAL (all document templates here)
aget/validation/          <- Validators for templates
aget/docs/templates/      <- DEPRECATED (do not use)
```

### Validation Commands

```bash
# Validate PROJECT_PLAN template/instances
python3 aget/validation/validate_project_plan.py aget/templates/PROJECT_PLAN_TEMPLATE.md

# Validate ADR template/instances
python3 aget/validation/validate_adr.py aget/templates/ADR_TEMPLATE.md

# Validate SPEC template/instances
python3 aget/validation/validate_spec.py aget/templates/SPEC_TEMPLATE.md
```

### Version Bump Rules

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking format change | Major | 1.0 → 2.0 |
| New section/feature | Minor | 1.0 → 1.1 |
| Typo/clarification | Patch | 1.0.0 → 1.0.1 |

---

## Failure Handling

If template coherence check fails:

1. **Identify gap**: Which rule violated?
2. **Document in L-doc**: If pattern, create learning
3. **Remediate**: Follow this SOP to fix
4. **Update checklist**: If gap reveals missing check

---

## References

- L515: Template Coherence Gap
- L370: Template-First Development
- #189: Protocol Template Propagation Checklist
- SOP_template_validation.md
- RELEASE_VERIFICATION_CHECKLIST.md

---

*SOP_template_lifecycle.md v1.0.0 - Template lifecycle management procedure*
