# Corrections since tag — v3.37.0

**What this file is**: the one place where corrections and known defects for v3.37.0 are recorded after the tag. The release body, release handoff, remote migration message and supervisor prompt point here and do not repeat the list.

**Tag**: v3.37.0 (`357600117e7892985746658f61ac4bb083a051f0`) · **Surface opened**: 2026-10-17 · **Rows are append-only**: a row is never edited or removed; when a fix lands, a new row in section 1 names the fix's commit and the known-defect row it resolves.

**How to read it**: section 1 holds disclosures and post-tag fixes; section 2 holds known defects that have no fix yet. Each row says what you can do. Rows whose action says "informational" need no action.

## 1. Disclosures and post-tag fixes

| # | Commit | Date | Artifact(s) | What | Why the tag copy is not enough | What you can do |
|---|--------|------|-------------|------|--------------------------------|-----------------|
| 1 | tag `35760011` (disclosure, no fix) | 2026-10-17 | `DEPLOYMENT_SPEC_v3.37.0.yaml`, row `M-3.37-5` | The row declares `surfaces: [core, templates]` and lists both `scripts/wind_down.py` and `docs/protocols/WIND_DOWN_PROTOCOL.md` under `paths`. The protocol document ships in core only, as the row's `detection_scope` and the 13 template Release bodies say; `scripts/wind_down.py` is present at all 14 tags. A check that requires every listed path at every declared surface reports the protocol document absent at each of the 13 template tags. The template payloads are as intended; the row's path list is imprecise. | The tagged specification is frozen; its `paths` list does not say which path belongs to which surface. | If a check of yours reads `M-3.37-5.paths` against a template checkout, expect `docs/protocols/WIND_DOWN_PROTOCOL.md` to be absent there and read it from core at `v3.37.0` instead. Do not copy it into a template to satisfy the check. |

## 2. Known defects, no fix yet

| # | Area | What happens | What you can do now |
|---|------|--------------|---------------------|
| — | — | None recorded. | — |
