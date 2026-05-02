# RELEASE_BODY_TEMPLATE_template.md

**Purpose**: Standard structure for **template-{archetype}-aget** GitHub Release bodies.
**Audience**: archetype-specific adopters; downstream consumers; less framework-context, more template-customization-context.
**Used by**: SOP_release_process Phase 6.4.5.3 (`gh release create vX.Y.Z --notes-file <body-from-this-template>`) for each of 13 templates.
**Companion**: `RELEASE_BODY_TEMPLATE_core.md` (for aget core release body — different audience, different density).

---

## When to use

Use this template for the **template-{archetype}-aget** release body. Each template's GitHub Release body SHALL follow this structure (per CAP-REL-032 R-REL-032-07b).

NOT for aget core release body — that uses `RELEASE_BODY_TEMPLATE_core.md` (depth-driven, not alignment-driven).

Template release bodies are downstream-of-aget-core: they primarily signal alignment + any archetype-specific delta. The substantive framework-level content lives in the aget core release body; template bodies should NOT duplicate it.

---

## Byte-norm calibration (per release type)

| Release type | Floor | Soft cap | Examples (historical) |
|--------------|------:|---------:|----------------------|
| Trivial alignment (version-bump only; no archetype-specific change) | ~200 | ~500 | supervisor/worker v3.16.0 (637-638) |
| Alignment with archetype-specific changes | ~400 | ~1000 | v3.16.0 archetype-templates (766 final, after 1155 over-correction was retightened per skeleton 2) |
| Alignment with breaking-change pass-through | ~500 | ~1200 | (no v3.16 example; v3.15.x templates) |

**Rule of thumb**: alignment-driven by delta-from-canonical. Templates that get NO archetype-specific change in a release should stay near the floor. Templates with archetype-specific deltas (e.g., the v3.16.0 release-triad revert applied to 10 archetype templates) get a few extra bullets but should still stay tight.

**Inverse-of-core principle**: aget core grows when content depth grows; templates stay tight regardless of core release size. A 9000-byte aget core release body should NOT pull templates to 9000 bytes — templates summarize the alignment, not duplicate the disclosure.

---

## Required structure

```markdown
## Aligned with framework v{X.Y.Z}

{Theme line cross-referencing aget core CHANGELOG entry, e.g.,
"Aligned with framework v3.16.0 (Framework-Discipline Closure + Wave-1A Spec Contracts + /aget-go Production)"}

## Changed (template-specific)

- Version bump: {X.Y.Z-prev} → {X.Y.Z} (framework alignment)
- `AGENTS.md` `@aget-version` updated to {X.Y.Z}
- {Optional: archetype-specific changes — e.g., "Universal-skills migration: 15 missing skills added from worker baseline"}
- {Optional: archetype-specific reverts — e.g., "Release-triad revert: 3 release-triad skills removed per CAP-TPL-016-07"}

## Compatibility

**{Breaking|Non-breaking}.** {1 line}. See [aget framework CHANGELOG](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) for full release detail.
```

---

## Example skeletons

### Skeleton 1: Trivial alignment (most common)

```markdown
## Aligned with framework v3.X.0

Aligned with framework v3.X.0 ({theme summary in 1 line}).

## Changed

- Version bump: 3.{X-1}.0 → 3.X.0 (framework alignment)
- `AGENTS.md` `@aget-version` updated to 3.X.0

## Compatibility

**Non-breaking.** Instances upgrade by version-bump only. See [aget framework CHANGELOG](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) for full release detail.
```

Target: ~250-400 bytes.

### Skeleton 2: Alignment with archetype-specific changes (e.g., v3.16.0 archetype-templates)

```markdown
## Aligned with framework v3.X.0

Aligned with framework v3.X.0 ({theme summary in 1 line}).

## Changed

- Version bump: 3.{X-1}.0 → 3.X.0
- `AGENTS.md` `@aget-version` updated to 3.X.0
- **{Archetype-specific change A}**: {one-line summary; e.g., "Universal-skills migration: 15 skills added from worker baseline"}
- **{Archetype-specific change B}**: {one-line summary; e.g., "Release-triad revert: aget-release-build/audit-specs/critique removed per CAP-TPL-016-07 — moved to release-execution archetype catalog"}

## Compatibility

**Non-breaking.** {Optional: brief migration note specific to archetype delta}. See [aget framework CHANGELOG](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) for full release detail.
```

Target: ~600-900 bytes.

### Skeleton 3: Release-execution archetype (worker, supervisor) — minimal delta

```markdown
## Aligned with framework v3.X.0

Aligned with framework v3.X.0 ({theme summary in 1 line}).

## Changed

- Version bump: 3.{X-1}.0 → 3.X.0
- `AGENTS.md` `@aget-version` updated to 3.X.0
- Release-triad skills retained (this template is in the release-execution archetype catalog per CAP-TPL-016-07).

## Compatibility

**Non-breaking.** See [aget framework CHANGELOG](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) for full release detail.
```

Target: ~400-500 bytes (v3.16.0 worker/supervisor were 637-638 bytes — slight over but within soft cap).

### Skeleton 4: Dormant template (e.g., document-processor)

```markdown
## Aligned with framework v3.X.0

Aligned with framework v3.X.0 ({theme summary}).

## Changed

- Version bump: 3.{X-1}.0 → 3.X.0
- {Note about dormant status if applicable; e.g., "No `.claude/skills/` baseline present (template lacks universal-skill deployment per L671 dormant classification)"}

## Compatibility

**Non-breaking.** See [aget framework CHANGELOG](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md) for full release detail.
```

Target: ~400-500 bytes.

---

## L909 sanitization (BLOCKING before commit)

Same patterns as RELEASE_BODY_TEMPLATE_core.md:

```bash
for pat in 'private-[a-z]+-(aget|AGET)' 'gmelli/' '[0-9]+ agents( in| across)?' 'FLEET-[A-Z]+-[0-9]+' 'SESSION_2026-[0-9]' 'legalon'; do
  grep -qiE "$pat" <body-file> && { echo "❌ L909 FAIL: $pat"; exit 1; }
done
echo "✅ L909 PASS"
```

---

## Anti-patterns (DO NOT)

| Anti-pattern | Why wrong |
|--------------|-----------|
| Pasting the full aget core CHANGELOG entry verbatim into the template release body | Duplicates content; inflates body to core-norm bytes when template-norm is appropriate. v3.16.0 archetype-templates first shipped 1155 bytes via this anti-pattern; retightened to 766 per skeleton 2 after principal "It is still verbose" correction. |
| Omitting the cross-reference link to aget core CHANGELOG | Adopters need a path to full framework-level detail; the template body is the at-a-glance entry, not the full story. |
| Reproducing sleeping-CAPs disclosure verbatim from aget core | Sleeping-CAPs are framework-level; templates should at most one-line acknowledge ("See aget core release notes for sleeping-CAPs disclosure"). Most templates don't need to mention. |
| Treating template release body as another core release body | Different audience, different density. Inverse-of-core: templates stay tight regardless of core release size. |

---

## Traceability

| Link | Reference |
|------|-----------|
| Used by | SOP_release_process v1.32 Phase 6.4.5.3 |
| Required by | CAP-REL-032 R-REL-032-07b (template release body content requirement) |
| Companion | `RELEASE_BODY_TEMPLATE_core.md` (aget core release body — different audience) |
| L-docs | L671 (decorative-classification at release-body surface), L909 (sanitization gate) |
| Origin | v3.16.0 cycle defect surfaced by principal recalibration 2026-05-02 ("do we have requirements and templates for these two perspectives?") |

---

*RELEASE_BODY_TEMPLATE_template.md — authored 2026-05-02 to close the core-vs-template release-body distinction gap. v3.16.0 archetype-templates calibration history: 138 (under-floor; original L671 anti-pattern) → 1155 (over-cap; verbatim CHANGELOG paste anti-pattern) → 766 (correct; skeleton 2 norm).*
