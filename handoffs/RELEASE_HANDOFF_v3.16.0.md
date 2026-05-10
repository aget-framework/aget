# RELEASE_HANDOFF_v3.16.0

**Version**: 3.16.0 | **Released**: 2026-05-02 (Saturday) | **Breaking Changes**: NONE | **Framework Manager**: Framework Manager

---

## Context for External Fleets

Public-facing notification: AGET v3.16.0 is released. Non-breaking minor; instances upgrade by version-bump only.

---

## Release Summary

v3.16.0 closes the framework-discipline cluster opened in v3.15-retro. Key changes:

1. **4 NEW Wave-1A spec contracts** (CAP-REL-030/031/032/033) at honest **SPEC-LANDED; IMPLEMENTATION DEFERRED v3.17** (R-DEP-010 grace; v3.18 removal threshold)
2. **SKILL-048 `/aget-go`** promoted to production v1.0.0 — Healthy Friction primitive
3. **`.agetignore` skeleton + CAP-SEC-007** — knowledge-tier isolation contract (hook deferred)
4. **Universal-skill mandate 32 → 29** — release-triad moved to release-execution archetype catalog (CAP-TPL-016-07)
5. **`**Plan_Status**:` / `**Gate_Status:**` template schema** (backward-compatible)
6. **SOP_release_process v1.30 Phase 6.4.5** — tag-cut moved post-handoff (#1154 fix)
7. **SOP_fleet_migration v1.6.0** — Wave 0/1/2 sequencing

---

## Sleeping Requirements Disclosure

This release ships 4 spec contracts WITHOUT implementation. Consumers SHALL NOT treat them as runtime-binding until v3.17 implementation lands. The headline #1154 tag-resolvability invariant IS enforced procedurally at release time via SOP v1.30 Phase 6.4.5 inline V-test.

---

## Upgrade Guide

**Instance agents**: Bump `.aget/version.json` `aget_version` and `AGENTS.md` `@aget-version` to `3.16.0`. No breaking changes; existing artifacts continue to work.

**Archetype-template-based agents** (advisor / analyst / architect / consultant / developer / executive / operator / researcher / reviewer / spec-engineer): release-triad skills (`aget-release-build`, `aget-release-audit-specs`, `aget-release-critique`) **removed** from your archetype baseline (moved to release-execution archetype). Add back as archetype-specific only if your agent performs release execution (CAP-TPL-016-07).

**Worker / supervisor templates**: release-triad retained.

---

## Fleet Action Required

Supervisors SHALL: review this handoff; acknowledge receipt; broadcast v3.16 availability; initiate pilot upgrade tracking per local Wave 0/1/2 sequencing (supervisor self → 1-2 representative agents → remainder).

---

## Acknowledgment & References

Receiving supervisors acknowledge in this section once upgrade is initiated; pilot tracking per supervisor in their own scope.

### Acknowledgments

- ✅ Main supervisor: main fleet upgrade complete 2026-05-02; experience report filed (see issue tracker).
- ✅ External fleet supervisor: external fleet upgrade complete 2026-05-03; 7-agent fleet upgraded; Wave 0/1/2 sequencing applied (supervisor self → 2 representative pilots → 4 remainder); experience report filed (see issue tracker).

References: `aget/CHANGELOG.md` v3.16.0; `aget/sops/SOP_release_process.md` v1.30; `aget/sops/SOP_fleet_migration.md` v1.6.0; `https://github.com/aget-framework/aget/releases/tag/v3.16.0`.

*Public handoff per SOP v1.30 Phase 6.3.1. 2026-05-02; ack section updated 2026-05-03.*
