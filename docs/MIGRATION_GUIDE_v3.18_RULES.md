# v3.18 Migration Rules — Before You Start

**Audience**: Fleet supervisors about to attempt v3.18 migration for the first time.
**Source**: FLEET-UPG-016 (main fleet) + FU016R adoption-stream remediation + FU016F F-G2-1 finalization, executed 2026-05-17. Combined wall-clock: ~13.7h. **~50% of that time was retroactive remediation** that better up-front design would have prevented.

These 7 rules each prevent a specific failure mode observed in that cycle. Cross-references resolve at `gmelli/aget-aget` gh-issue family + public `aget-framework/aget` canonical paths.

---

## The 7 Rules

| # | Rule | This-cycle evidence | Cost if skipped | Cross-ref |
|---|------|---------------------|-----------------|-----------|
| **R0** | **Define KR1 substantively before cycle starts.** Specify what "agent at vX.Y.Z" means — version-stamp only, or full adoption-stream coverage? If your release has adoption streams (spec ref / skill deploy / governance amendment), the migration mechanic MUST cover ALL of them, not just the version line. | KR1 reported 55% (version-stamp) while effective adoption was 11% (substantive); the conflation surfaced at Gate 4 close, triggering retroactive remediation. | ~3h remediation cycle (FU016R) for 13 agents needing 4-of-5 adoption streams backfilled. | gh#1431 |
| **R1** | **Before designing cross-agent action as carve-out, test invocation modes first.** Framing as "R-CLI-004 carve-out shape" can anchor 3h of design work that headless invocation dissolves in 30 seconds. Ask "could each agent do this in own authority via `claude -p`?" before drafting carve-out audit phrasing. | FU016F G1 designed Path B-2 carve-out language extensively; principal asked "how about headless calls?" — entire framework collapsed cleanly. | ~25% of cycle wall-clock spent on framing that didn't match problem geometry. | gh#1430 (sibling pattern) |
| **R2** | **Status-stamp ≠ ceremony complete.** Stamping `Plan_Status: COMPLETE` is not the same as completing the close ceremony. At G4 entry, enumerate explicit ceremony items (retrospective + rubric + handoff + broadcast + ...) and mark each "this-session" or "next-session" BEFORE stamping. External-readable prose retrospective is the discipline test. | "Finalized" overclaimed 3 separate times in same cycle (each by supervisor after stamping with only mechanical close); each required principal correction. | 3 correction rounds + cycle-trust erosion + retroactive plan version bumps. | gh#1432 |
| **R3** | **Reuse the Generator, don't rebuild.** `fleet_remediation_v318.py` v1.0.0 is production-ready: semantic-not-byte-literal idempotency, 25-second batch for 13 agents, validated under production load. Re-running on already-completed agents = zero double-write. | FU016R Wave 1 + FU016F finalize mode both ran on same Generator without modification; idempotency held under repeated invocation. | ~2h rebuild + bug-debug per cycle (the cycle-1 bug was a `dry_run=False` hardcode discovered at G2 PILOT). | path below |
| **R4** | **Default to headless dispatch for cross-agent action.** Workers invoked via `claude -p "<task description>"` act in own authority — no supervisor cross-write, no R-CLI-004 carve-out, no scope-language tension. This is the cleaner mechanic. | 4 FU016F routine agents self-classified own commits + self-pushed in ~5 min total via headless dispatch loop. | Obsoletes the entire Path B-2 carve-out family + audit-phrasing ceremony overhead. | gh#1430 (sibling) |
| **R5** | **Worker discipline propagates via clear taxonomy + relay channel, not pre-training.** Workers absorb a classification taxonomy (e.g., "routine = session-narrative / labeled chore / supervisor-pre-authorized") + a paste-relay or headless prompt with that taxonomy, and self-arc from there. | 3 workers (impact-aget D2=a, ccb-AGET Path C full-arc, FU016F 4-agent headless cohort) self-arc'd without coaching cycle. Three workers HALT-refused non-routine commits cleanly. | Otherwise need explicit per-agent L100 coaching cycle (~30 min each) for what could be ~5 min relay. | supervisor retro path below |
| **R6** | **File framework-side findings DURING discovery, not at close.** When you discover a framework gap mid-cycle (wake_up.py rendering, harness-state behavior, skill-deployment mechanism), file as gh issue WHILE the evidence is fresh — not 6h later at close-ceremony. Findings filed at close lose specificity to cycle-narrative friction. | gh#1433 substrate (wake_up.py "clean" vs "fully-pushed" conflation) discovered 6h before filing; multiple workers misread "clean" as "ready-for-dispatch" before the gap was named. | Findings get bundled into retro as "we noticed X" rather than tracked as actionable issues; v3.19+ has to re-derive specificity. | gh#1433 |

---

## How to use this doc

- **Before plan scaffolding**: R0 (KR1 definition), R3 (plan to reuse Generator), R4 (headless first)
- **At gate execution**: R1 (when drafting carve-out language), R5 (when coordinating workers)
- **At gate close**: R2 (before declaring complete), R6 (file findings as you discover them, not at close)

---

## Substrate references (read for context)

| Substrate | Path |
|---|---|
| Reusable Generator | `~/github/private-supervisor-AGET/workspace/fleet_remediation_v318.py` v1.0.0 (private fleet; mirror to your own workspace per R3) |
| Cycle retrospective (substantive prose) | `~/github/private-supervisor-AGET/sessions/SESSION_2026-05-17_v318_migration_finalization.md` |
| gh issue family (v3.19 ADR substrate) | gh#1430 DIRTYTREE-classification, gh#1431 STRICT-propagation, gh#1432 cycle-retrospective, gh#1433 wake_up-reporting-gaps, gh#1434 v3.19-intake |
| Cycle plans | FLEET-UPG-016 v1.22 + FU016R v1.6 + FU016F v1.6 (private fleet) |

---

## Falsifier (how to measure these rules worked for you)

After your v3.18 migration cycle closes, check:

- [ ] KR1 defined substantively at plan scaffold (R0) — version-stamp + adoption-substance measured separately
- [ ] ≤1 hour spent on R-CLI-004 carve-out language vs headless mechanic discovery (R1 + R4)
- [ ] 0 "finalized" overclaims requiring principal correction (R2)
- [ ] Generator reused, not rebuilt (R3)
- [ ] ≥2 of 3 worker dispatches self-arc on first relay without coaching (R5)
- [ ] ≥80% of framework-side findings filed cycle-time, not at close (R6)

**If you hit ≥3 of these criteria failing**, these rules failed to prevent the main fleet's pattern at scale. File a follow-up at gh#1431 family. Hypothesis H-LEARN-001 (this doc's effectiveness) is then falsified for your cycle.

**If ≥5 pass**, the rules worked. Your retrospective should still capture cycle-specific findings — these 7 rules are the floor, not the ceiling.

---

*v3.18 Migration Rules v1.0.0 — authored 2026-05-17 by `private-aget-framework-AGET` at LEARN-001 Gate 1 BUILD-A.*
*Falsifier operational; cross-references resolve at gh issues + public canonical paths.*
*For v3.19+ migrations: underlying rules generalize (R1-R6 are mechanic-shaped, R0 is metric-shaped); consult v3.19 release docs for cycle-specific updates.*
