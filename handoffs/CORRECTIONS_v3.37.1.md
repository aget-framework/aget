# Corrections since tag — v3.37.1

**What this file is**: the one place where corrections and known defects for v3.37.1 are recorded after the tag. v3.37.0's known defects (`handoffs/CORRECTIONS_v3.37.0.md`, section 2) all still apply. Its disclosure row 2 (section 1, the release-age default) is fixed by this release.

**Tag**: v3.37.1 (`9b202ae3b09d390041203b6d2ab4c2b75e07923b`) · **Surface opened**: 2026-11-06 · **Rows are append-only**: a row is never edited or removed; when a fix lands, a new row in section 1 names the fix's commit and the known-defect row it resolves.

**How to read it**: section 1 holds disclosures and post-tag fixes; section 2 holds known defects that have no fix yet. Each row says what you can do.

## 1. Disclosures and post-tag fixes

| # | Commit | Date | Artifact(s) | What | Why the tag copy is not enough | What you can do |
|---|--------|------|-------------|------|--------------------------------|-----------------|
| 1 | tag `9b202ae3` (disclosure, no fix) | 2026-11-06 | Every dated release file: `handoffs/REMOTE_MIGRATION_MESSAGE_v3.37.1.md` (date header and step 4), `CHANGELOG.md`, `release-notes/v3.37.1.md`, `handoffs/RELEASE_HANDOFF_v3.37.1.md`, `DEPLOYMENT_SPEC_v3.37.1.yaml` (`created` and the `M-3.37.1-1` detection line), `docs/VERSION_HISTORY.md`, `codemeta.json`, `CITATION.cff`, `.aget/version.json`; the 13 templates' CHANGELOG and version history; the organization homepage; and the "Row 2 fixed in v3.37.1 (2026-11-04)" line in `handoffs/CORRECTIONS_v3.37.0.md` | The release files carry the record date 2026-11-04. The release was published on 2026-11-06 (US Pacific). The migration message's step 4 says to substitute `2026-11-04` for the publication date. | The kit's age check (`adoption_policy.py --check-age --published <date>`) counts days from the date you give it. With 2026-11-04 it counts two days that had not passed, so a wait you declared yourself ends two days early. The record date was kept on purpose; the publication date is a different fact. | Give the publication date in your own timezone. The Release was published 2026-11-06 18:45 US Pacific (2026-11-07 02:45 UTC): in the Americas pass `--published 2026-11-06`; in UTC−2 or further east pass `--published 2026-11-07`. With no declared wait (the default 0) the result is the same either way. |
| 2 | tag `9b202ae3` (disclosure, no fix) | 2026-11-06 | `DEPLOYMENT_SPEC_v3.37.1.yaml` (`status`, `publication_state_note`, `corrections`) | The tagged specification says `status: candidate` and "Candidate. Planned publication date 2026-11-04." v3.37.1 is published: the annotated tag `v3.37.1` and the GitHub Release object are the publication evidence, as the note itself says. Its `corrections` field names `handoffs/CORRECTIONS_v3.37.0.md`; this release's record is this file, and v3.37.0's record still applies. | The tagged specification is frozen; it was written before publication and not moved to `released` before the tag. | If a check of yours reads the specification's `status` to decide whether v3.37.1 is released, it will say it is not. Read publication from the tag and the Release instead (`git rev-parse v3.37.1^{commit}` gives `9b202ae3…`). Read corrections from both files. |

## 2. Known defects, no fix yet

None new in v3.37.1. See `handoffs/CORRECTIONS_v3.37.0.md` section 2.
