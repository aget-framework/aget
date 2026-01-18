# SOP: Artifact Deprecation

**Version**: 1.0.0
**Created**: 2026-01-12
**Owner**: private-aget-framework-AGET
**Related**: AGET_VOCABULARY_SPEC Part 7 (Authority Model)

---

## Purpose

This SOP defines the process for deprecating AGET framework artifacts (specifications, SOPs, templates, patterns) when they are superseded, obsolete, or no longer applicable. Proper deprecation ensures historical traceability while preventing confusion from outdated content.

## Scope

### When This SOP Applies

- An artifact is superseded by a newer version or consolidated spec
- An artifact is obsolete and no longer relevant
- An artifact contains incorrect guidance that should not be followed
- Framework evolution renders an artifact inapplicable

### When This SOP Does NOT Apply

- Artifact is still active and current
- Artifact is being updated (use versioning, not deprecation)
- Artifact is archived for historical reference but still valid

## Prerequisites

- [ ] Identified artifact to deprecate
- [ ] Confirmed superseding artifact exists (if applicable)
- [ ] Verified no active dependencies on deprecated artifact
- [ ] Approval from artifact owner or framework maintainer

## Procedure

### Step 1: Identify Deprecation Type

| Type | Description | Action |
|------|-------------|--------|
| **Superseded** | Replaced by newer artifact | Archive with reference |
| **Obsolete** | No longer relevant | Archive with explanation |
| **Incorrect** | Contains harmful guidance | Archive with warning |

### Step 2: Add Deprecation Notice

Add deprecation header at the top of the artifact:

**For Superseded Artifacts:**
```markdown
> **DEPRECATED** (YYYY-MM-DD): This artifact has been superseded by
> [{NEW_ARTIFACT}](path/to/NEW_ARTIFACT.md).
> This file is retained for historical reference only.
> Do not use this artifact for new work.
```

**For Obsolete Artifacts:**
```markdown
> **DEPRECATED** (YYYY-MM-DD): This artifact is obsolete.
> Reason: {Brief explanation of why it's obsolete}
> This file is retained for historical reference only.
```

**For Incorrect Artifacts:**
```markdown
> **DEPRECATED** (YYYY-MM-DD): This artifact contains incorrect guidance.
> **WARNING**: Do not follow procedures in this document.
> See: {Link to corrective L-doc or replacement}
```

### Step 3: Move to Archive

Move the artifact to the appropriate archive directory:

```bash
# For specifications
mv aget/specs/OLD_SPEC.md aget/specs/archive/

# For SOPs
mv aget/sops/SOP_old.md aget/sops/archive/

# For templates
mv aget/templates/OLD_TEMPLATE.md aget/templates/archive/

# For patterns
mv aget/docs/patterns/PATTERN_old.md aget/docs/patterns/archive/
```

### Step 4: Update Authority Status

If artifact is in AGET_VOCABULARY_SPEC as a Specification_Document instance, update its authority:

```yaml
OLD_SPEC:
  aget:authority: "Deprecated"  # Changed from "Active"
  aget:deprecated_date: "YYYY-MM-DD"
  aget:superseded_by: "NEW_SPEC"  # If applicable
```

### Step 5: Update INDEX.md

For specifications:

1. Move entry from active table to Archived Specs table
2. Add supersession information:
   ```markdown
   | OLD_SPEC | NEW_SPEC | YYYY-MM-DD |
   ```

### Step 6: Update References

1. Search for references to deprecated artifact:
   ```bash
   grep -r "OLD_ARTIFACT" aget/
   ```

2. For each reference:
   - If in active content: Update to point to replacement
   - If in historical content (L-docs, changelogs): Leave as-is with note

### Step 7: Document Deprecation

Create or update L-doc capturing:
- What was deprecated
- Why it was deprecated
- What replaces it (if applicable)
- Any migration guidance

## Verification

```bash
# V1: Deprecation notice exists
grep -q "DEPRECATED" aget/specs/archive/OLD_SPEC.md && echo "PASS"

# V2: File moved to archive
test -f aget/specs/archive/OLD_SPEC.md && echo "PASS"
test ! -f aget/specs/OLD_SPEC.md && echo "PASS"

# V3: INDEX.md updated (if spec)
grep "OLD_SPEC" aget/specs/INDEX.md | grep -q "Archived\|Superseded"

# V4: No dangling references in active content
grep -r "OLD_SPEC" aget/ | grep -v archive | grep -v CHANGELOG | wc -l
# Should be 0 or minimal (historical references only)
```

## Rollback

If deprecation was premature:

1. Move artifact back from archive to active directory
2. Remove deprecation header
3. Update INDEX.md status
4. Update AGET_VOCABULARY_SPEC authority (if applicable)
5. Document rollback decision in L-doc

## Authority Lifecycle

```
Draft → Active → Deprecated
         ↓
      CANONICAL (immutable, never deprecated)
```

**Note**: CANONICAL artifacts are never deprecated. They may only be versioned with major version bumps that create new CANONICAL artifacts.

## References

- AGET_VOCABULARY_SPEC Part 7: Authority Model
- SOP_specification_consolidation.md: For consolidation-triggered deprecation
- AGET_SPEC_FORMAT: Specification format requirements

---

*SOP_artifact_deprecation.md — Artifact deprecation process*
