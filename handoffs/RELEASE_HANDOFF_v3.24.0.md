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
- **Remote/external fleets**: see `handoffs/REMOTE_MIGRATION_MESSAGE_v3.24.0.md` — sanitized upgrade guide + an 8-point operational playbook from an executed v3.23.1→v3.24.0 fleet migration (triplet-vs-doublet, blocking-vs-additive layers, conformance-then-bump, verify-from-disk, pre-flight classification, one-owner).
- To adopt the reliance contract: author a `.aget/skill_reliance_manifest.yaml` against `schemas/skill_reliance_manifest.schema.yaml`; verify with `scripts/check_skill_reliance_manifest.py`.
- **Scope note (D-REL-3, core-first)**: this release landed `aget/` canonical at ship. The reliance **feature** (validator + schema) has since fanned out to **13/13 templates** (verified 2026-06-27). Still pending (EC-5): per-template version-label bump (13/13 at 3.23.1), the starter manifest (0/13), and the full v3.24 spec payload (R-BND-001 + AGET_HOST_RUNTIME_SPEC). Existing-agent point-upgrades are unaffected; clean NEW-agent template derivation awaits EC-5.

## Pilot tracking (D-REL-2 deploy-verify bar = supervisor + self)

| Agent | Deployed v3.24.0 | Confirmed |
|-------|:----------------:|-----------|
| Framework Manager (self) | ✅ (AGENTS.md/CLAUDE.md/version.json @ 3.24.0) | 2026-06-27 |
| Fleet Supervisor | ⏳ pending | — |

## Deprecations

- None this release.

## Owed follow-ups

1. **EC-5 template conformance** — validator + schema reached 13/13; remaining: per-template version bump (after full-payload conformance, not label-only), starter manifest (0/13), R-BND-001 + AGET_HOST_RUNTIME_SPEC into templates.
2. **Supervisor deploy-verify** (D-REL-2 — second confirmed deployment; L656 loading-dock guard on next-cycle planning).
3. **Friction forward-validation** (v3.25; supervisor Stream B — unblocks CAP-FRIC-006).
4. **#1737 conformance** activates at first node deployment (operator lane, INIT-ALWAYS-ON-HOST).

---

*Release executed under `/loop` + principal GO, 2026-06-27. Two-pole flagship (path ii); G0.2c floor cleared at 75% landable-new functional. Pre-push content-sanitization caught + remediated a private-name leak before the public push.*
