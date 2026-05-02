# RELEASE_BODY_TEMPLATE_core.md

**Purpose**: Standard structure for the **aget core** (`aget-framework/aget`) GitHub Release body.
**Audience**: framework adopters, contributors, consumers — the primary public-facing surface for the release.
**Used by**: SOP_release_process Phase 6.4.5.3 (`gh release create vX.Y.Z --notes-file <body-from-this-template>`).
**Companion**: `RELEASE_BODY_TEMPLATE_template.md` (for template-{archetype}-aget releases — different audience, different density).

---

## When to use

Use this template for the **aget core** release body. Each aget-framework/aget GitHub Release body SHALL follow this structure (per CAP-REL-032 R-REL-032-07a).

NOT for template-{archetype}-aget release bodies — those use `RELEASE_BODY_TEMPLATE_template.md` (alignment-driven, not depth-driven).

---

## Byte-norm calibration (per release type)

| Release type | Floor | Soft cap | Examples (historical) |
|--------------|------:|---------:|----------------------|
| Trivial-mechanical (version bump only) | ~500 | ~1000 | (avoid; usually has SOMETHING to highlight) |
| Non-breaking minor | ~1000 | ~3000 | v3.7.0 (1141), v3.8.0 (1403), v3.10.0 (1434) |
| Substantive minor (themed) | ~1500 | ~4000 | v3.14.0 (3000) |
| Breaking minor | ~1500 | ~3000 | v3.15.0 (1922) |
| Non-breaking minor with sleeping-CAPs disclosure | up to ~9000 | exception | v3.16.0 (8904) — disclosure depth justifies exceeding norm |

**Rule of thumb**: depth-driven by what shipped. Sleeping-CAPs / breaking-changes / theme depth justify more bytes; pure-mechanical releases stay near the floor.

---

## Required structure

```markdown
## What's New

- **{Headline change 1}** — {one-line description with version delta or capability summary}
- **{Headline change 2}** — {...}
- **{...}** — typically 5-10 bullets for non-breaking minor; up to 12 for substantive
- {Optional: SOP/spec amendments worth surfacing publicly}

## Sleeping-CAPs Disclosure (CONDITIONAL — include ONLY if release ships SPEC-LANDED-DEFERRED contracts)

{1-2 sentence summary of which CAPs are spec-only-deferred, R-DEP-010 grace cite, removal threshold, procedural enforcement note if applicable}

## Breaking Changes (CONDITIONAL — include ONLY if release ships breaking changes)

{Brief BC-NNN list with link to BREAKING_CHANGES_vX.Y.md}

## Compatibility

**{Breaking|Non-breaking}.** {1-2 sentence migration summary; link to CHANGELOG.md for full Added/Changed sections + migration notes}
```

---

## Example skeletons

### Skeleton 1: Non-breaking minor (norm)

```markdown
## What's New

- **{Capability A} v{N.M}**: {one-line summary}
- **{Spec amendment B}**: {one-line — what changed in spec layer}
- **{SOP update C}**: {one-line — what changed in process layer}
- **{Tooling D}**: {one-line — new script/skill}
- **{Doc/template E}**: {one-line — documentation surface improvement}

## Compatibility

**Non-breaking.** Instances upgrade by version-bump only. See [CHANGELOG.md](CHANGELOG.md) for full detail.
```

Target: ~1000-1500 bytes.

### Skeleton 2: Non-breaking minor with sleeping-CAPs disclosure (exception class)

Add this section between What's New and Compatibility:

```markdown
## Sleeping-CAPs Disclosure

CAP-{group}-{NNN..NNN} ship at `SPEC-LANDED; IMPLEMENTATION DEFERRED v{target-version}`. {1-sentence note on what's missing}. R-DEP-010 grace; v{removal-threshold} removal threshold. {Optional: procedural enforcement that compensates meanwhile}.
```

Target: up to ~9000 bytes acceptable (depth justified by disclosure honesty).

### Skeleton 3: Breaking minor

Replace Compatibility with Breaking Changes section:

```markdown
## Breaking Changes

v{X.Y} contains **{N} breaking change(s)**. See [BREAKING_CHANGES_v{X.Y}.md](docs/BREAKING_CHANGES_v{X.Y}.md) for migration guide.

- **BC-NNN**: {one-line summary}
- **BC-NNN**: {one-line summary}
```

Target: ~1500-3000 bytes.

---

## L909 sanitization (BLOCKING before commit)

Before committing release body, grep for:

```bash
for pat in 'private-[a-z]+-(aget|AGET)' 'gmelli/' '[0-9]+ agents( in| across)?' 'FLEET-[A-Z]+-[0-9]+' 'SESSION_2026-[0-9]' 'legalon'; do
  grep -qiE "$pat" <body-file> && { echo "❌ L909 FAIL: $pat"; exit 1; }
done
echo "✅ L909 PASS"
```

Reuse the same patterns CAP-SEC-006 enforces at CHANGELOG-write time — release body is the public-facing surface; same sanitization rules apply.

---

## Anti-patterns (DO NOT)

| Anti-pattern | Why wrong |
|--------------|-----------|
| `gh release create vX.Y.Z --notes "see CHANGELOG"` | L671 at GitHub-Release surface (decorative redirect with substantive content elsewhere). v3.16.0 cycle evidence: 14/14 repos shipped 138-byte minimal redirect bodies; defects audit identified the gap. |
| Pasting full CHANGELOG entry verbatim including all sub-bullets | Templates' release bodies should reference, not duplicate. CHANGELOG is the canonical detail surface; release body is the at-a-glance surface. |
| Including private agent names, gmelli/ paths, fleet size | L909 violation; promoted to public via release body. |
| Skipping sleeping-CAPs disclosure when applicable | Spec-truthfulness violation; sleeping-requirements MUST be visible at release-body level, not gated behind a click. |

---

## Traceability

| Link | Reference |
|------|-----------|
| Used by | SOP_release_process v1.32 Phase 6.4.5.3 |
| Required by | CAP-REL-032 R-REL-032-07a (aget core release body content requirement) |
| Companion | `RELEASE_BODY_TEMPLATE_template.md` (template release body — different audience) |
| L-docs | L671 (decorative-classification anti-pattern at release-body surface), L909 (sanitization gate) |
| Origin | v3.16.0 cycle defect surfaced by principal recalibration 2026-05-02 ("v3.16.0 is too verbose ... do we have requirements and templates for these two perspectives?") |

---

*RELEASE_BODY_TEMPLATE_core.md — authored 2026-05-02 to close the core-vs-template release-body distinction gap. v3.16.0 release body (8904 bytes) is the exception-class example justifying the sleeping-CAPs disclosure depth.*
