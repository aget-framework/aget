# SOP: Specification Consolidation

**Version**: 1.0.0
**Created**: 2026-01-12
**Owner**: aget-framework
**Related**: L434 (Spec Fragmentation), AGET_VOCABULARY_SPEC Part 7

---

## Purpose

This SOP defines the process for consolidating multiple specifications that have overlapping scope or redundant content into a unified specification. Consolidation reduces fragmentation, improves discoverability, and eliminates conflicting definitions.

## Scope

### When This SOP Applies

- Two or more specifications have >50% conceptual overlap
- Multiple specs define the same or similar terms
- Fragmented specifications create navigation burden
- Maintenance overhead exceeds value of separation

### When This SOP Does NOT Apply

- Specifications have distinct, non-overlapping domains
- Consolidation would exceed 800-line threshold (L502)
- Specifications serve different audiences with conflicting needs

## Prerequisites

- [ ] Identified candidate specs for consolidation
- [ ] Confirmed overlap ratio (>50% conceptual overlap)
- [ ] Verified consolidated spec will remain under 800 lines
- [ ] No active work in progress on candidate specs

## Procedure

### Step 1: Analysis

1. List all candidate specifications with their:
   - Line counts
   - Domain coverage
   - Key terms defined
   - Dependent specifications

2. Create overlap matrix showing shared concepts

3. Estimate consolidated spec size:
   ```
   Estimated size = Sum(unique content) + overhead
   ```

### Step 2: Create Consolidated Specification

1. Create new specification following AGET_SPEC_FORMAT:
   ```
   {DOMAIN}_CONSOLIDATED_SPEC.md  or  {DOMAIN}_SPEC.md
   ```

2. Include "Consolidates:" line in header:
   ```markdown
   **Consolidates**: SPEC_A.md, SPEC_B.md, SPEC_C.md
   ```

3. Merge content:
   - Deduplicate overlapping definitions
   - Preserve all unique requirements
   - Maintain requirement IDs from source specs
   - Add cross-references where concepts were unified

### Step 3: Archive Original Specifications

1. Move original specs to `specs/archive/`:
   ```bash
   mv aget/specs/SPEC_A.md aget/specs/archive/
   mv aget/specs/SPEC_B.md aget/specs/archive/
   ```

2. Add supersession header to archived specs:
   ```markdown
   > **ARCHIVED**: This specification has been superseded by
   > [{CONSOLIDATED_SPEC}](../CONSOLIDATED_SPEC.md) as of {YYYY-MM-DD}.
   > This file is retained for historical reference only.
   ```

### Step 4: Update INDEX.md

1. Add consolidated spec to Spec ID Registry
2. Move original specs to Archived Specs table
3. Add supersession date

### Step 5: Update References

1. Search for references to archived specs:
   ```bash
   grep -r "SPEC_A\|SPEC_B" aget/
   ```

2. Update all references to point to consolidated spec

### Step 6: Verify Consolidation

Run verification tests:

```bash
# V1: Archived specs have supersession header
grep -l "ARCHIVED" aget/specs/archive/SPEC_*.md

# V2: Consolidated spec exists
test -f aget/specs/CONSOLIDATED_SPEC.md

# V3: INDEX.md updated
grep "CONSOLIDATED_SPEC" aget/specs/INDEX.md

# V4: No dangling references
grep -r "SPEC_A\|SPEC_B" aget/ | grep -v archive | grep -v "Consolidates:"
```

## Rollback

If consolidation creates problems:

1. Restore original specs from archive
2. Remove consolidated spec
3. Revert INDEX.md changes
4. Document failure in L-doc

## Examples

### Successful Consolidations

| Original Specs | Consolidated To | Date |
|----------------|-----------------|------|
| AGET_GLOSSARY_STANDARD_SPEC, AGET_CONTROLLED_VOCABULARY | AGET_VOCABULARY_SPEC | 2026-01-04 |
| AGET_PERSONA_SPEC, AGET_MEMORY_SPEC, AGET_REASONING_SPEC, AGET_SKILLS_SPEC, AGET_CONTEXT_SPEC | AGET_5D_COMPONENTS_SPEC | 2026-01-04 |

## References

- L434: Specification Fragmentation Pattern
- L502: Artifact Comprehensibility Gap
- AGET_SPEC_FORMAT: Specification format requirements
- AGET_VOCABULARY_SPEC Part 7: Standards Document Ontology

---

*SOP_specification_consolidation.md — Specification consolidation process*
