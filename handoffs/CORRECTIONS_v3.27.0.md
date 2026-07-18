# Corrections since tag — v3.27.0

**Contract** (SOP_release_process v1.57 Phase 3.6 Rule 2; gh#1882): this file is the ONE
write target per post-tag fix. Guidance surfaces point here and never duplicate.
Consumers pulling AT THE TAG: apply every row below on top of the tag payload.

**Tag**: v3.27.0 · **Surface opened**: 2026-07-18 (same-day) · **Rows are append-only.**

| # | SHA | Date | Artifact(s) | What | Why tag copy insufficient | Consumer action |
|---|-----|------|-------------|------|---------------------------|-----------------|
| 1 | `49516a7` | 2026-07-18 | `DEPLOYMENT_SPEC_v3.27.0.yaml` + `handoffs/REMOTE_MIGRATION_MESSAGE_v3.27.0.md` | M-3.27-4 corrected to seat-conditional non-blocking (+ smoke probe 3 conditional) — check_config.py is a framework-seat tool, NOT template payload | tag copy's blocking detection FAILS at every template-derived seat | pull spec+message from `main`, or apply: treat M-3.27-4 as skip-if-absent |
| 2 | (per-repo) | 2026-07-18 | 12 template `README.md` | **Version** line corrected 3.24.0→3.27.0 (version_bump pattern missed this line shape) | cosmetic at tag; badge misreports version | none — informational (main carries fix) |
| 3 | `5de5a5d` | 2026-07-18 | `handoffs/REMOTE_MIGRATION_MESSAGE_v3.27.0.md` | probe-3 path-literal → instance-only annotation (citation resolution) | cosmetic; tag copy carries the pre-correction row-1 shape | none — informational |

---
*First binding use of the corrections single-surface (built this release, gh#1882). The release body points here and is not edited further.*
