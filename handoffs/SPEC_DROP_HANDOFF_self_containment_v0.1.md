# Spec Drop Handoff: RELEASE_HANDOFF Self-Containment Specification v0.1

**Date**: 2026-05-03
**Type**: Pre-v3.17 Spec Drop (NOT a versioned release)
**From**: aget-framework manager
**For**: Remote fleet supervisors, contributors, integrators

---

## TL;DR

Two new public artifacts ship today, both pre-v3.17:

1. **`specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md` v0.1.0** (status: REVIEWED) — defines what "self-containment" means for `RELEASE_HANDOFF_v{X.Y.Z}.md` artifacts via 8 CAPs and 11 testable sub-requirements.

2. **`verification/validate_handoff_self_containment.py` v0.1.0** — runnable validator. You can invoke it on any RELEASE_HANDOFF (yours or ours).

**SOP wiring is deferred to v3.17.0 final** — the new spec defines a contract; no release process automatically enforces it yet. Validator is advisory at this drop.

**No breaking changes. No version bump. No fleet-wide migration required.**

---

## Why this drop exists (before full v3.17)

Three failure classes drove the spec, all observed during recent fleet migrations:

1. **Silent SOP staleness (L910)**: a remote consumer reading a canonical SOP at vN can be operating against a stale runbook while the publisher is on vN+10 internally. No signal that the runbook is stale.

2. **Recurring REMOTE_MIGRATION_MESSAGE confusion (L901, revised)**: 4 of 15 historical releases produced the supplemental file; 3 of 4 most recent did not. Variability framed as "orphan gap" but the absence wasn't the defect — the **missing definition of self-containment** was.

3. **Implicit cross-agent dependency**: handoff text occasionally uses dialog-implying phrases (referrals to the framework manager, references to private agents, contact-naming directives). Self-containment was presumed, not gated. The new spec lists exact prohibited phrasings; see CAP-RHSC-001 in the spec for the canonical list.

**Empirical evidence the property IS achievable**: v3.16 fleet upgrade reached 32/34 agents at v3.16.0 with 0 rollbacks using only `RELEASE_HANDOFF_v3.16.0.md` as the published artifact. The property exists; the spec just makes it testable.

---

## What's in the spec (one-paragraph view)

`AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC v0.1` declares: a `RELEASE_HANDOFF_v{X.Y.Z}.md` is *self-contained* if a remote supervisor can complete migration end-to-end using only (a) the published handoff, (b) public AGET repositories, and (c) their own local SOPs — **with no dialog dependency** on the framework manager. The 8 CAPs gate this property by checking: dialog-reference prohibition, sanitization invariants (4 sub-rules), SOP version parity with canonical, breaking-change detection commands, per-archetype branch explicitness, sleeping-requirement disclosure, measurement-substrate caveat, and deprecation replacement naming.

---

## How to consume (3 paths)

### Path 1: Read the spec for reference
```
https://github.com/aget-framework/aget/blob/main/specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md
```
Use as documented criterion when authoring or reviewing your own handoff text.

### Path 2: Run the validator on your own handoff(s)
```bash
git clone https://github.com/aget-framework/aget.git
cd aget
python3 verification/validate_handoff_self_containment.py \
  --handoff /path/to/your/RELEASE_HANDOFF_vX.Y.Z.md
```

Optional flags for fuller coverage:
```bash
python3 verification/validate_handoff_self_containment.py \
  --handoff /path/to/your/RELEASE_HANDOFF_vX.Y.Z.md \
  --release-manifest /path/to/your/DEPLOYMENT_SPEC_vX.Y.Z.yaml \
  --prior-version vX.Y-1.0 \
  --json
```

Output is per-V-test PASS/FAIL/UNKNOWN with file:line evidence.

### Path 3: Run it on our handoff (works as a worked example)
```bash
python3 verification/validate_handoff_self_containment.py \
  --handoff handoffs/RELEASE_HANDOFF_v3.16.0.md \
  --release-manifest DEPLOYMENT_SPEC_v3.16.0.yaml \
  --prior-version v3.15.0
```

You should see **10 PASS / 1 FAIL / 0 UNKNOWN** (exit code 1).

**IMPORTANT — read this before you panic about the FAIL**:

The single FAIL is **V-RHSC-008** (per-archetype enumeration) on the v3.16 handoff. This is **intentional falsifiability evidence**, not a sign that v3.16 was a bad migration or that the validator is broken:

- v3.16 reached 32/34 fleet PASS empirically — the migration WORKED
- v3.16 handoff doesn't enumerate per-archetype branches; it also doesn't include the explicit "no per-archetype variation" disclaimer the spec accepts as alternative
- This is the **inversion test working** — the spec exposes a documentation gap the empirical migration tolerated
- Per H-RHSC-001 PF-2 disposition: **pivot to G4 backfill audit, do NOT narrow spec**. The fix is at the handoff layer (add disclaimer or enumeration), not the spec layer.

If your own handoff PASSes V-RHSC-008 with archetype enumerations or a no-variation disclaimer, you're ahead of v3.16's documentation discipline.

### Bonus G4 finding (V-RHSC-010 detected on v3.16)

The v3.16 self-test surfaced that `validate_archetype_skills.py` was modified between v3.15..v3.16 (substrate-modification confirmed) AND the v3.16 handoff has no KR PASS/FAIL claims — vacuously passing CAP-RHSC-007 because there are no claims to caveat. This is itself a separate Loading Dock anti-pattern (L656) instance worth investigating at G4: KR claims should appear in any release handoff per AGET_RELEASE_SPEC. If your KR-reporting discipline is tighter than ours, V-RHSC-010 will validate it; if it's looser, the substrate-caveat rule applies once you start citing KRs.

---

## What's NOT in this drop (deferred to v3.17.0 final)

- **G3 SOP wiring** — `sops/SOP_release_process.md` Phase 6.3 will be amended to invoke the validator as a BLOCKING V-test. Until then, the spec is advisory and validator runs are opt-in. v3.17.0 final will close this.
- **G4 backfill audit** — v3.10..v3.16 handoffs scored against the new V-tests, surfacing per-handoff gap inventory.
- **G5 L901 closure** — re-grade L901 ("REMOTE_MIGRATION_MESSAGE recurring orphan gap") once G3 + G4 land.

These are tracked under H-RHSC-001 (`PROJECT_PLAN_release_handoff_self_containment_spec_v1.0.md` in the framework manager's planning surface).

---

## Compatibility statement

| Aspect | Status |
|--------|--------|
| Breaking changes | None |
| Required agent action | None (advisory at this drop) |
| Recommended agent action | Run validator on your own handoff before next release; surface gaps |
| Version bump required | None (spec is additive, no API contract change) |
| Migration required | None (no fleet-wide migration; spec drop only) |
| Backward compatibility | Full (existing handoffs continue to work; new spec defines a contract going forward) |

---

## For framework integrators (not fleet supervisors)

If you fork or integrate `aget-framework/aget`:

- The new spec lives at `specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md`. Status REVIEWED → ACTIVE transition happens at v3.17.0 final once G3 SOP wiring lands.
- The validator at `verification/validate_handoff_self_containment.py` is a standalone Python 3 script with stdlib-only dependencies. No new install steps.
- Tests against the validator itself are not yet shipped (planned for v3.17.0); current validation is via self-test against `handoffs/RELEASE_HANDOFF_v3.16.0.md` as documented above.

---

## Traceability

| Link | Reference |
|------|-----------|
| Spec | `specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md` v0.1.0 (REVIEWED) |
| Validator | `verification/validate_handoff_self_containment.py` v0.1.0 |
| Parent spec | `AGET_RELEASE_SPEC v1.17.0` CAP-REL-020 (R-REL-019) |
| Hypothesis | H-RHSC-001 (`PROJECT_PLAN_release_handoff_self_containment_spec_v1.0.md` in framework manager's planning surface) |
| Initiative | INIT-FRAMEWORK-TRANSPARENCY (Stream 1 extension — handoff layer) |
| L-docs (public-relevant) | L901 (revised by this spec); L910 (CAP-RHSC-003 closure); L916 (CAP-RHSC-006 closure); L917 (CAP-RHSC-007 motivation); L656 (Loading Dock anti-pattern — disclosed in this drop) |
| CHANGELOG | `CHANGELOG.md` `[3.17.0-unreleased]` section |
| Wiring SOP (deferred) | `sops/SOP_release_process.md` Phase 6.3 amendment, planned v3.17.0 final |

---

## Questions, issues, contributions

- For framework framework-side issues, file at `aget-framework/aget` (public).
- For your fleet-side adoption questions, follow your local agent communication conventions.

---

*SPEC_DROP_HANDOFF_self_containment_v0.1.md — pre-v3.17 spec drop authored 2026-05-03 by aget-framework manager*
*This is a SPEC DROP, not a versioned release. No tag, no version bump, no fleet-wide ceremony. Forwardable as-is.*
