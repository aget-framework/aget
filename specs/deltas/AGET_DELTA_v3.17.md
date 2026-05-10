# AGET Delta: v3.16 → v3.17

**From**: v3.16.0 (2026-05-02)
**To**: v3.17.0 (2026-05-09)
**Type**: Minor release
**Theme**: C3 — Canonical Coherence + Structural Self-Conformance

---

## Convention Status

The `specs/deltas/AGET_DELTA_v{X.Y}.md` convention was used at v2.11.0 and v3.0.0-alpha.1, then effectively abandoned in favor of:

- `CHANGELOG.md` — canonical change log per semver convention
- `release-notes/v{X.Y.Z}.md` — deep narrative release notes (in private framework-manager workspace)

The `tag_release.py:create_release()` template, however, has continued auto-linking to `AGET_DELTA_v{X.Y}.md` since v3.1, producing 17 cycles of broken links in GitHub Release bodies (v3.1.0 through v3.16.0). This v3.17.0 file closes the 404 for the current release and serves as a redirect; v3.18.0 will externalize the convention from the script template (per v3.17 retrospective candidate).

---

## See For Complete Changes

| Resource | Path |
|----------|------|
| **CHANGELOG entry (canonical)** | [`CHANGELOG.md`](../../CHANGELOG.md) — section `## [3.17.0] - 2026-05-09` |
| **Deep release notes** | Available in framework-manager private workspace; key content excerpted into the canonical CHANGELOG entry above |
| **GitHub Release** | [v3.17.0 release](https://github.com/aget-framework/aget/releases/tag/v3.17.0) |

---

## Summary

v3.17 ratifies Theme C3 (Canonical Coherence + Structural Self-Conformance) operationally. The framework was forced to pass its own audits at every gate boundary; the audits caught real drift that prior cycles had silently masked.

**Key deliverables** (full detail in CHANGELOG):

- **Tier 1 (Implementation)**: T1.7 framework-manager archetype coined (Q4=A.2; SKOS C610 grounding); T1.1+T1.2 CAP-REL-030+CAP-REL-031 implemented (closes v3.16 sleeping CAPs); T1.3+T1.4 CAP-REL-032+CAP-REL-033 grace-extended to v3.18.0 (Q1=B); T1.5+T1.6 H-RHSC-001 G3+G4 SOP wiring (SOP_release_process v1.32 → v1.45); T1.8 substance-aware health check (closes L656 gh#1211); T1.9 wake/wind shim Q9 grace extension.
- **Tier 2 (Specification Authoring)**: T2.18 SOP_scope_lock_ceremony LANDED v1.0.0 (codifies the 4-gate ceremony executed at v3.16+v3.17 lock events); T2.19 AGET_SKILL_LIFECYCLE_SPEC LANDED v1.0.0 with full V-test authoring (Q-G1.5-2=B; rejected v3.16 SPEC-LANDED-IMPL-DEFERRED precedent); T2.20 AGET_FLEET_UPGRADE_SPEC v0.1 DRAFT (calibrated demote per L103 Q-G1.5-1=A); T2.23 AGET_TASK_ROUTING_SPEC v0.1 DRAFT (calibrated demote).

**Theme C3 demonstrations** (3 in-cycle V-test recurrences + 2 post-publication recurrences):

1. T1.7 V-T1.7 v0 (4 declared sites) → V-T1.7-EXT (6 actual sites) — Critic-at-exit caught L908 self-application
2. Gate 2 V-2.1 declared 5 sites including AGENTS.md; aget/ canonical has 3 sites (no AGENTS.md) — V-test corrected at execution
3. Gate 4 V-1.5.2 narrow regex (`V-test (deferred to v0.2)`) vs broader `deferred to v0.2` — Auditor caught at gate-4 mid-cycle pulse
4. Org-profile README missed (single-cycle anomaly; v3.12-v3.16 all updated org-profile, v3.17 dropped via plan-driven execution)
5. AGET_DELTA chronic 17-cycle gap — script template references file convention abandoned post-v3.0-alpha.1; never V-tested

v3.17's empirical lesson: **V-test correctness has TWO axes** — assertion correctness (multi-condition equality; v3.16's #1 lesson) AND scope correctness (declared scope vs actual canonical-artifact universe; v3.17's ratification). v3.18 candidate adds a THIRD axis: publication-correctness (what does a public viewer see post-release?).

---

## Compatibility

**No breaking changes** in v3.17.0. Existing instances upgrade by version-bump only. The `framework-manager` archetype field addition is additive.

**Spec-fault carry**: gh#1179 + gh#1180 OPEN per v3.16 L708 annotation precedent (best-effort artifact, not blocking).

---

*This file closes the 404 for v3.17's GitHub Release body link. Full canonical content lives at `CHANGELOG.md`.*
