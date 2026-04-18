# Release Handoff: v3.14.0

**Date**: 2026-04-18
**Theme**: v3.13 Loop Closure + Scope-Lock Discipline
**From**: aget-framework manager
**To**: Fleet supervisors, remote fleets, aligned-peer adopters

---

## Release Summary

v3.14.0 is a **retrospectively dominant** release: the meaningful content is what the v3.13 cycle finally landed (pilot tracking closure, handoff artifact maturation, deployment baseline), not new v3.14 work. The v3.14 cycle scope-locked on release day with a committed item set that will execute across v3.14.x patches and into v3.15.

### Key Changes

- **CAP-REL-028 Upstream Deployment Feedback** spec added (REQ-REL-F-009) — formalizes fleet→framework feedback channel when deployment reveals gaps
- **DEPLOYMENT_SPEC_v3.13.0.yaml** — template baseline + reconciliation steps for fleet upgrade
- **AGET_TEMPLATE_SPEC** updated — universal skills 15→31, supervisor skills 18→37
- **SKILL_NAMING_CONVENTION_SPEC v1.4.0** (CAP-SNAME-001-06) — Single-Verb Exception Registry permits `aget-{verb}` form for approved self-contained verbs
- **`log_skill_invocation.py`** — skill telemetry logger
- **v3.13.0 handoff maturation** — self-contained for remote fleets (DEPLOYMENT_SPEC reference + skill deployment guide embedded)
- **Version bump** 3.13.0 → 3.14.0 across framework core + 13 templates (29 version-bearing files atomic update)

### Breaking Changes

**None.** All changes are backward-compatible.

### Deprecations

Per POL-DEP-001 (2-minor-version grace per R-DEP-011); v3.14 and v3.15 accept both old and new names; removal in v3.16.0:

| Artifact | Replacement | Removal |
|----------|-------------|:-------:|
| `scripts/wake_up.py` | `scripts/aget_open_session.py` | v3.16.0 |
| `scripts/wind_down.py` | `scripts/aget_close_session.py` | v3.16.0 |
| `scripts/wake_up_ext.py` | `scripts/aget_open_session_ext.py` | v3.16.0 |
| `scripts/wind_down_ext.py` | `scripts/aget_close_session_ext.py` | v3.16.0 |

---

## Upgrade Guide

### For Each Fleet Agent

| Step | Obligation | Action | V-Test Command | Expected |
|------|-----------|--------|---------------|----------|
| 1 | MUST | Update `.aget/version.json`: set `aget_version` to "3.14.0" | `jq -r .aget_version .aget/version.json` | `"3.14.0"` |
| 2 | MUST | Update `AGENTS.md` header: `@aget-version: 3.14.0` | `grep '@aget-version: 3.14.0' AGENTS.md` | Match |
| 3 | SHOULD | Sync skill directories from template (31 universal; supervisor: 37) | `ls .claude/skills/ \| wc -l` | ≥ 31 (or ≥ 37 for supervisor-class) |
| 4 | SHOULD | Run health check | `python3 scripts/health_check.py; echo $?` | `0` |
| 5 | SHOULD | Run contract tests | `python3 -m pytest tests/` | All green |

### Session-script migration (non-urgent)

Old names (`wake_up.py`, `wind_down.py`, and their `_ext.py` partners) continue to work through v3.15.0. Migrate at convenience:

```bash
# Rename in place (or use shims — see POL-DEP-001)
mv scripts/wake_up.py   scripts/aget_open_session.py
mv scripts/wind_down.py scripts/aget_close_session.py
mv scripts/wake_up_ext.py   scripts/aget_open_session_ext.py  # if present
mv scripts/wind_down_ext.py scripts/aget_close_session_ext.py # if present
```

If you maintain shell aliases or hooks that reference the old names, update those along with the rename.

---

## Known Issues

1. **GitHub release objects missing on some template repos at initial publish**: the tags were pushed but the release objects were not created for every template. Remediated post-release via the post-release remediation plan (PRR-044). If your fleet verifies "Latest" badges on template repos, re-verify after the remediation closes. Release objects attach to the same commits as the tags — no artifact drift.

2. **Template CHANGELOG gaps for v3.12.0 and v3.13.0**: prior releases did not maintain per-version entries in every template CHANGELOG; v3.14.0 entries acknowledge this in their Notes sections. Framework-level CHANGELOG in `aget-framework/aget` remains the canonical record for those versions.

3. **Historical content in `template-document-processor-AGET` [2.8.0] CHANGELOG entry** references an internal agent name. Already public (pre-existing). Not remediated in this release (would require rewriting published history); tracked for principal decision.

---

## Process Improvements Validated This Release

Signals useful to remote fleets and aligned peers:

- **Scope-lock as governance state-machine**: v3.14 scope transitioned `PLANNING → TRIAGED → SCOPE_LOCKED → EXECUTING → COMPLETE` during the release cycle. The SCOPE_LOCKED state denied mid-cycle additions without explicit override — a structural defense against scope drift.
- **Spec-first gate ordering**: every project plan this cycle included Gate -1 (Governing Spec Verification) before implementation gates, per MP-1. Prevents scaffolding errors from propagating through execution.
- **Batched multi-repo operations**: version bumps, CHANGELOG inserts, and commit+tag batches reduced per-operation friction and shrank the state-change attack surface.
- **Clarifying-question skill (`/aget-ask`) dogfooded**: first release-day invocation measured pre-ask confidence 0.55 → post-ask 0.92. Entropy-reduction as a measurable quality metric became operational.

---

## Looking Ahead (v3.15 candidates)

Post-release remediation (PRR-044) surfaced four structural enhancement candidates for v3.15 scope-triage:

- **NBA skill release-proximity classification** — gather state + interpret state
- **Release artifact sanitization generalization** — current scope (issues) extended to CHANGELOG, release-notes, handoff, governance docs, commit messages
- **Verification freshness guard** — point-in-time checks invalidated by state-changing operations; state-fingerprint persistence
- **Phase 7.5 scope-inheritance** — `gh release create` applied uniformly across every pushed repo in a release, not just framework core

Each is filed against the internal tracker; v3.15 scope-triage will evaluate.

---

## Traceability

| Link | Reference |
|------|-----------|
| CHANGELOG | [`aget-framework/aget/CHANGELOG.md`](../CHANGELOG.md) v3.14.0 section |
| GitHub release | [v3.14.0](https://github.com/aget-framework/aget/releases/tag/v3.14.0) |
| Governing SOP | [`sops/SOP_release_process.md`](../sops/SOP_release_process.md) (Phase 7+ post-release) |
| Governing specs | [`AGET_RELEASE_SPEC`](../specs/AGET_RELEASE_SPEC.md), [`AGET_PROJECT_PLAN_SPEC`](../specs/AGET_PROJECT_PLAN_SPEC.md), [`SKILL_NAMING_CONVENTION_SPEC`](../specs/SKILL_NAMING_CONVENTION_SPEC.md) v1.4.0 |
| Deprecation policy | [POL-DEP-001](../../) (registered in internal governance) |
| Prior release handoff | [`RELEASE_HANDOFF_v3.13.0.md`](RELEASE_HANDOFF_v3.13.0.md) |

---

*Handoff filed 2026-04-18. Post-release remediation (PRR-044) in progress; this document will be revised if remediation surfaces material changes.*
