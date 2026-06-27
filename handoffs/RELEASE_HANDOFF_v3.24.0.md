# RELEASE HANDOFF: v3.24.0 — "Reliance & Boundaries"

**Date**: 2026-06-27 (Saturday)
**From**: Framework Manager
**To**: Fleet Supervisor (fleet upgrade coordination — L511 ownership boundary)
**Release**: https://github.com/aget-framework/aget/releases/tag/v3.24.0 (live, `draft=false`)
**Canonical HEAD**: `cd260c2` · **Tag**: `v3.24.0`

---

## Summary

First public release since v3.22. Theme **Reliance & Boundaries** — advanced, not completed.

| Capability | What | Where |
|------------|------|-------|
| **R-BND-001 — Boundary & Reliance Requirements** | Cross-boundary reliance = principal-owned, single-source, version-pinned, verified meets-declared-minimum (not parity-to-template), drift-detectable | `specs/requirements/R-BND-001_boundary_reliance.md` |
| **Skill-reliance manifest framework feature** | `{S}`/`{O}`/`{D}` release-pinned reliance contract, declarable + self-checkable | `schemas/skill_reliance_manifest.schema.yaml` + `scripts/check_skill_reliance_manifest.py` |
| **AGET_HOST_RUNTIME_SPEC v1.0.0** | Host-runtime filesystem-layout standard (lifecycle-class separation, record/exhaust boundary, deployed-copy decoupling); conformance V-tests deploy-pending (ADR-007) | `specs/AGET_HOST_RUNTIME_SPEC.md` |

**Staged to a following cycle**: friction-handling triage (CAP-FRIC-006) — L1113-blocked pending a non-author forward-validation (request: `handoffs/SUPERVISOR_REQUEST_friction_forward_validation_v3.24.md`).

## Upgrade guide

- **No breaking changes** — additive (new requirement, new schema+validator, new standard). Existing agents continue unaffected.
- To adopt the reliance contract: author a `.aget/skill_reliance_manifest.yaml` against `schemas/skill_reliance_manifest.schema.yaml`; verify with `scripts/check_skill_reliance_manifest.py`.
- **Scope note (D-REL-3, core-first)**: this release landed `aget/` canonical only. The **13-template fan-out is a deliberate follow-up** (validator + starter manifest into each template) — not yet shipped.

## Pilot tracking (D-REL-2 deploy-verify bar = supervisor + self)

| Agent | Deployed v3.24.0 | Confirmed |
|-------|:----------------:|-----------|
| Framework Manager (self) | ✅ (AGENTS.md/CLAUDE.md/version.json @ 3.24.0) | 2026-06-27 |
| Fleet Supervisor | ⏳ pending | — |

## Deprecations

- None this release.

## Owed follow-ups

1. **13-template fan-out** of the reliance validator + starter manifest (D-REL-3 deferred tail).
2. **Supervisor deploy-verify** (D-REL-2 — second confirmed deployment; L656 loading-dock guard on next-cycle planning).
3. **Friction forward-validation** (v3.25; supervisor Stream B — unblocks CAP-FRIC-006).
4. **#1737 conformance** activates at first node deployment (operator lane, INIT-ALWAYS-ON-HOST).

---

*Release executed under `/loop` + principal GO, 2026-06-27. Two-pole flagship (path ii); G0.2c floor cleared at 75% landable-new functional. Pre-push content-sanitization caught + remediated a private-name leak before the public push.*
