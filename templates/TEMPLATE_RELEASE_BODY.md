# TEMPLATE: GitHub Release Body

<!--
TEMPLATE INSTRUCTIONS:
1. Copy this template; replace all {placeholders}
2. Remove [OPTIONAL] sections that don't apply
3. Delete this instruction block before publishing
4. Run `.aget/patterns/release/validate_release_body_conformance.py --tag vX.Y.Z`
   before `gh release create` or `gh release edit`
5. For retroactive scope decisions (does this template apply to pre-existing
   releases?), consult RUBRIC_retroactive_scope_content_quality_caps_v0.1
-->

**Theme**: {Theme name — Concise capability or discipline shipped this release}

## What's New

<!--
Bullet-form. Each bullet:
  1. Lead with plain-language outcome in **bold** (≤15 words)
  2. Follow with 1-2 sentences of context, technical detail, theoretical basis
  3. Optional trailing `*Traceability: T-IDs, gh#NNN*` line for internal references
Avoid em-dash compound constructions in lead sentences (REQ-HOM-Q-001).
Preserve internal-ID precision (T-IDs, CAP-NNN, gh#NNN) — principal register, not for sanitization.
-->

- **{Plain-language outcome 1}.** {Context, mechanism, theoretical basis or
  reference}.
  *Traceability: {T-IDs, gh#NNN, script paths}*

- **{Plain-language outcome 2}.** {Context}.
  *Traceability: {…}*

- {…repeat per delivered item}

## Sleeping-CAPs Disclosure [OPTIONAL — remove if no sleeping CAPs]

<!--
Required whenever the release ships SPEC-LANDED-IMPLEMENTATION-DEFERRED
contracts OR closes prior cycle's sleeping CAPs. Cite R-DEP-010/R-DEP-011
grace-period rationale per POL-DEP-001.
-->

{Newly sleeping CAPs at vX.Y.Z, with R-DEP-010 grace-period annotation.}
{Inherited sleeping CAPs from prior cycle, with current status (IMPLEMENTED /
GRACE-EXTENDED / WITHDRAWN).}
{Number of new sleeping CAPs at V-test layer — state ZERO explicitly when
none.}

## Compatibility

**{No breaking changes | Breaking changes — see Migration below}** in vX.Y.Z.
{One sentence on upgrade path: typically "Existing instances upgrade by
version-bump only." Note any spec-fault carries — gh#NNN OPEN per L708
annotation precedent — when applicable.}

See [CHANGELOG.md](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md)
for full Added/Changed sections + [AGET_DELTA_vX.Y.md](https://github.com/aget-framework/aget/blob/main/specs/deltas/AGET_DELTA_vX.Y.md).

## Migration [OPTIONAL — required if breaking changes declared above]

{Migration steps. Include executable commands when possible. Estimated time
per agent. Link to BREAKING_CHANGES_vX.Y.md for full guide.}

## What This Release Doesn't Change [OPTIONAL]

<!--
Honest gap recording per the framework's learning-project register.
List 1-3 known limitations, deferred questions, or post-release-identified
patterns. Each item: 1-2 sentences with anchor to L-doc or tracking artifact.
This section is the framework's structural defense against L92 (Premature
Victory) at the release-narrative layer.
-->

- {Known limitation or deferred question 1}. {Anchor: L###, gh#NNN, RUBRIC, or
  audit document.}
- {Known limitation 2}.
- {…}

---

## Template Provenance

| Aspect | Reference |
|--------|-----------|
| Effective version | v3.18+ (forward; v3.17.0 refreshed retroactively under principal override per L178) |
| Governing requirement | CAP-REL-006-02-NN (release-body structured-template) |
| Voice requirement | REQ-HOM-Q-001 (Principal's Voice — ≤15-word sentences majority; no em-dash compounds) |
| Validator | `validate_release_body_conformance.py` (private-aget-framework-AGET); promotion to canonical `aget/scripts/` is a v3.18 grooming candidate |
| Lessons that shaped this template | L941 (no observed peer for inline release history); L942 (triple-surface drift); L944 (retroactive scope question) |
| Retroactive-scope decision-support | `RUBRIC_retroactive_scope_content_quality_caps_v0.1.md` (private-aget-framework-AGET docs/) |
| First worked example | v3.17.0 refresh on 2026-05-10 (commit `473fbc7` in private-aget-framework-AGET) |

## Validation checklist

Before publishing a release body authored from this template:

- [ ] Theme line present and starts with `**Theme**:` (case-sensitive)
- [ ] What's New section has ≥1 bullet
- [ ] Compatibility section present
- [ ] If breaking changes declared, Migration section present
- [ ] If sleeping CAPs exist (newly added or inherited), Sleeping-CAPs Disclosure present
- [ ] Voice check: <20% sentences exceed 15 words; no em-dash compound clauses leading bullets
- [ ] Evidence check: each capability claim has artifact link OR `(experimental)`/`(planned)` qualifier
- [ ] Internal-link integrity: all hyperlinks resolve (run `post_release_validation.py` post-publish)
- [ ] Validator run: `python3 .aget/patterns/release/validate_release_body_conformance.py --tag vX.Y.Z` returns 0
