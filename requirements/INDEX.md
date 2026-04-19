# Requirements Index

**Format**: [REQUIREMENTS_FORMAT.md](REQUIREMENTS_FORMAT.md) v1.0
**Level**: Human (ISO 29148 StRS — Stakeholder Requirements Specification)
**Parallel to**: [specs/INDEX.md](../specs/INDEX.md) (Contract level)

---

## Registry

| Domain | File | Requirements | Status | Date |
|--------|------|:----------:|--------|------|
| **CORE** | [REQ-CORE_critical_foundations.md](REQ-CORE_critical_foundations.md) | 7F + 3Q | proposed | 2026-04-18 |
| GOV | [REQ-GOV_agent_governance.md](REQ-GOV_agent_governance.md) | 4F + 2Q | proposed | 2026-04-18 |
| REL | [REQ-REL_release_quality.md](REQ-REL_release_quality.md) | 6F + 3Q | proposed | 2026-03-28 |
| HOM | [REQ-HOM_homepage_quality.md](REQ-HOM_homepage_quality.md) | 6F + 3Q | proposed | 2026-04-04 |

**CORE** is the cross-cutting foundational domain — the ten requirements every other domain inherits from. Read first.

---

## Two-Level Model (L742)

| Level | Directory | Format | Owner |
|-------|-----------|--------|-------|
| **Requirements** (human) | `aget/requirements/` (this directory) | REQUIREMENTS_FORMAT v1.0 | Principal |
| **Specifications** (contract) | `aget/specs/` | AGET_SPEC_FORMAT v1.3 (EARS) | Framework |

---

## Traceability

Requirements trace forward to specifications:

```
REQ-REL-F-001 → R-REL-025, SOP Phase -1
REQ-REL-F-002 → R-REL-019, SOP Phase 5.3/6.3
REQ-REL-F-003 → SOP Phase 7.4
REQ-REL-F-004 → R-SYNC-002, SOP Phase -0.5
REQ-REL-F-005 → SOP Phase 4.3, R-REL-025-029
REQ-REL-F-006 → SOP Phase 0, VERSION_SCOPE
REQ-REL-Q-001 → RELEASE_BRIDGE velocity
REQ-REL-Q-002 → RUBRIC D4
REQ-REL-Q-003 → SOP Phase 7.4
```

---

*requirements/INDEX.md*
*"What the principal wants — published, traceable, assessable."*
