# CONVENTION: Terminal-State Vocabulary — representing "implemented, awaiting deployment evidence"

**Status**: v1.0 (2026-07-10, v3.26 C-26-14) — convention rung per ADR-008; the R-REL-022-01 enum extension is a registered spec-touch obligation (below), not silently performed here.
**Evidence**: gh#1856 (L656 as a *representable state*, not only a guard); F-REL326-G(-1)-1 (VERSION_SCOPE display-string "LOCKED — READY FOR BUILD" ∉ the R-REL-022-01 enum while its machine-readable `lock_event` conforms); L656 (Loading Dock — IMPLEMENTED ≠ deployed); v3.25 close ("SUP pilot pending" prose with no state to hold it).

## Problem

The lifecycle vocabularies have no state between "built" and "verified running downstream." Plans and VERSION_SCOPEs express that interval as prose caveats ("pilot pending", "awaiting deployment evidence") bolted onto a terminal-looking status — so state scans read done-ness that isn't, and L656 lives only as reviewer discipline instead of as data.

## Vocabulary

### Plan-level statuses (PROJECT_PLAN `Plan_Status` / gate rows)

| State | Meaning | Terminal? |
|-------|---------|-----------|
| `IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE` | artifact built + committed; ≥1 independent downstream confirmation NOT yet on record (L656 interval as data) | NO — a waiting state, scans as open |
| `PILOTED` | ≥1 non-author agent has applied/run it with evidence on record (L1113 satisfied); fleet propagation not yet done | NO |
| `STAGED` | committed locally / queued for a push window (L735); not yet public | NO |
| `COMPLETE` / `CLOSED (PARTIAL)` / `ABANDONED` / `SUPERSEDED` | per AGET_PROJECT_PLAN_SPEC — unchanged | YES |

Usage rule: these states are ONLY valid with a pointer to what would advance them (which pilot, which window, which evidence). A waiting state with no advancement pointer is the Loading Dock anti-pattern wearing a new label.

### VERSION_SCOPE statuses (R-REL-022-01 relationship)

Current enum: {PLANNING, SCOPE_LOCKED, READY FOR RELEASE, RELEASED, CANCELLED}.

- **Delta registered (NOT enacted here — L644)**: add `LOCKED — READY FOR BUILD` as the post-lock/pre-release display state (v3.25 + v3.26 both used it de facto; machine state carried by `lock_event`). Route: next AGET_RELEASE_SPEC `/aget-enhance-spec` pass; tracked as F-REL326-G(-1)-1 disposition.
- Until enacted, conformance is satisfied by the `lock_event: SCOPE_LOCKED …` field being grep-able in the Status line (V-REL-029-C form) — the convention v3.26 G(-1) verified.

## Self-application (L922)

The v3.26 cycle applies this vocabulary to itself: C-26-19's pattern is `IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE` → advances to `PILOTED` on supervisor-pilot evidence (#1698 Decision 2) → canonical/template promotion (L1113). The v3.26 release plan's template stagings are `STAGED` until the 2026-07-18 window.

## Traceability

gh#1856 · F-REL326-G(-1)-1 · L656 · L1113 · L735 · L922 · AGET_PROJECT_PLAN_SPEC (statuses extended, not replaced) · v3.26 C-26-14.
