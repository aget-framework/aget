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
| 4 | `7dd4b61` (+per-template) | 2026-07-18 | `scripts/check_initiatives.py`, `scripts/close_gate_check.py`, `scripts/wind_down.py` (canonical + all 13 templates) | **BLOCKING** — M-3.27-3/-5 substance (CIS-010 + CIS-008 D-27-A; dual-status scanner) backfilled to canonical + templates; M-3.27-6 guard backfilled to templates (gmelli/aget-aget#1945: features were built on the framework seat, promotion step missed at release) | tag copies of all three scripts pre-date the payload — smoke probes 1/2/5 and dual-status blocking FAIL on tag-sourced pulls | pull the three scripts from `main` (canonical or your template's origin), or re-pull payload from main; then re-run §Behavioral Smoke |
| 5 | advisor `ffad95c`, consultant `3300d89` | 2026-07-18 | `AGENTS.md` + `docs/AGENTS_archive_v3.27.md` (template-advisor, template-consultant) | AGENTS.md over 40k hard limit (advisor 41,157 — CI red, gmelli/aget-aget#1941; consultant 44,743 — latent, size test never runs in CI): Internal State Management templates archived, pointer stub remains | tag copies exceed the 40k Claude Code limit — advisor-derived seats fail `test_configuration_size` | advisor/consultant-derived seats: pull `AGENTS.md` + `docs/AGENTS_archive_v3.27.md` from template `main` |

---
*First binding use of the corrections single-surface (built this release, gh#1882). The release body points here and is not edited further.*
