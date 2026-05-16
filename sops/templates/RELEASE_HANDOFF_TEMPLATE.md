# RELEASE_HANDOFF_vX.Y.Z.md

**Version**: X.Y.Z
**Released**: YYYY-MM-DD
**Breaking Changes**: Yes/No
**Framework Manager**: private-aget-framework-AGET

---

## Release Summary

**Theme**: [Brief theme/title, e.g., "Shell Integration + Executable Knowledge"]

### Key Changes

1. **[Major Change 1]**: [Brief description]
2. **[Major Change 2]**: [Brief description]
3. **[Major Change 3]**: [Brief description]

### New Specifications

- [List new specs, e.g., AGET_SPEC_NAME.md]
- [Or "None" if no new specs]

### New Validators

- [List new validators, e.g., validate_something.py]
- [Or "None" if no new validators]

### New L-docs

[Count and range, e.g., "18 L-docs: L451-L503, L505, L508-L511"]

---

## Upgrade Guide

### For Instances (AGETs)

1. Update `.aget/version.json`:
   ```json
   {
     "aget_version": "X.Y.Z",
     "migration_history": [
       "... existing ...",
       "vOLD -> vX.Y.Z: YYYY-MM-DD (Theme)"
     ]
   }
   ```

2. Update `AGENTS.md` header:
   ```markdown
   @aget-version: X.Y.Z
   ```

3. [Version-specific steps, if any]

4. **Run pytest**: should pass at your agent's pre-migration baseline + any newly-bundled framework tests. The N/N expected count varies by archetype role (e.g., framework-manager ~160, supervisor ~33, worker varies by domain). Treat the migration as PASS if pytest count matches your previous baseline plus any expected new tests, with no regressions — not by literal N/N match against the framework-manager number.

### DEPLOYMENT_SPEC Note (per release)

[Choose one — fill at handoff authoring time:]

- **Option A (default)**: `DEPLOYMENT_SPEC_vX.Y.Z.yaml` ships at canonical aget/ root. Fleet-upgrade tooling SHALL use this version's contract.
- **Option B (deployment-spec-optional, when applied)**: **No `DEPLOYMENT_SPEC_vX.Y.Z.yaml` ships** — explicit policy per principal Decide. vX.Y.Z inherits the prior available DEPLOYMENT_SPEC contract semantically (no breaking changes). Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z-prior}.yaml` as the contractual artifact set. **This is intentional, not oversight** — do not file `where-is-DEPLOYMENT_SPEC` issues. Cite full rationale in `aget/CHANGELOG.md` for this version.

### For Templates

[Template-specific guidance, or "Templates already updated. No action required if using vX.Y.Z templates."]

### Breaking Changes

[None, or list breaking changes with migration instructions]

---

## Fleet Action Required

### Supervisor Tasks

- [ ] Acknowledge receipt of this handoff
- [ ] Broadcast vX.Y.Z availability to fleet
- [ ] Prioritize pilot upgrades
- [ ] Track and report adoption status

### Pilot Upgrade Tracking

| Pilot | Portfolio | Status | Date | Migration PR | Notes |
|-------|-----------|--------|------|--------------|-------|
| private-supervisor-AGET | main | ⏳ Pending | | | Fleet coordinator |
| private-aget-framework-AGET | main | ✅ Complete | YYYY-MM-DD | | Self (framework manager) |
| private-impact-aget | main | ⏳ Pending | | | |
| private-workco-aget | workco | ⏳ Pending | | | |
| private-predictionworks-aget | predictionworks | ⏳ Pending | | | |
| [Add other pilots as needed] | | ⏳ Pending | | | |

**Migration PR column semantics** (added PP-035 / closes gh#1392 / L952):
- **Purpose**: Records the PR# that shipped the migration to this agent. Closes L952 deployment-evidence-channel traceability axis (PR# was previously unrecorded at migration moment).
- **Format (private/internal handoff)**: `gmelli/{repo}#NNN` for private agent migrations.
- **Format (promoted/public handoff per R-REL-019-07)**: `aget-framework/{repo}#NNN` only — `gmelli/*` refs are sanitized per R-RHSC-002-02 / L631.
- **`N/A (direct-commit)` permitted** when migration uses direct-commit path (no PR opened). Acceptable per current SOP_point_upgrade.md Phase 4.
- **Value is forward-looking**: column populates non-N/A once branched-PR "heavyweight" route per gh#1392 is adopted; current default = `N/A (direct-commit)` for direct-commit migrations.
- **V-test V-UPGRADE-004**: SOP_point_upgrade.md Phase 4 requires PR# recording or `N/A (direct-commit)` marking (procedural consequence: STOP if neither).

### Adoption Target

- **Priority 1**: Supervisor + main portfolio (by YYYY-MM-DD)
- **Priority 2**: Other portfolios (by YYYY-MM-DD)

### Self-Tick Prevention (L656 + L908)

**Receiving agents SHALL NOT mark their own row ✅ on self-deploy alone.** L656 requires cross-AGENT deployment evidence; self-confirmation instantiates the L908 self-application gap. Receiving agents update only their own *handoff-consumed* + *upgrade-guide-executed* status. Pilot-confirmed deployment status (`✅`) is set by the supervisor or framework-manager on cross-AGENT verification, not self-tick. v3.17.0 caught two paired same-week recurrences of this pattern (framework-manager D6 over-statement; sibling fleet agent everything-but-self-migrate) — see gh#1277 for grounding evidence and v3.18 retro candidate D0 for the structural L-doc.

**Cross-AGENT pair**: framework-manager + supervisor at vX.Y.Z constitutes the minimum L656 cross-AGENT evidence; subsequent fleet rows are confirmed via supervisor pilot pass.

---

## Release Artifacts

| Artifact | URL |
|----------|-----|
| aget/ release | https://github.com/aget-framework/aget/releases/tag/vX.Y.Z |
| CHANGELOG | https://github.com/aget-framework/aget/blob/main/CHANGELOG.md |
| VERSION_HISTORY | https://github.com/aget-framework/aget/blob/main/docs/VERSION_HISTORY.md |
| Homepage | https://github.com/aget-framework |

---

## Handoff Protocol

**From**: private-aget-framework-AGET (Framework Manager)
**To**: private-supervisor-AGET (Fleet Coordinator)
**Date**: YYYY-MM-DD
**Method**: This artifact + direct notification

### Acknowledgment

Supervisor: Please update this section upon receipt.

```
[ ] Acknowledged by: _______________
[ ] Date: _______________
[ ] Fleet broadcast sent: _______________
```

---

*RELEASE_HANDOFF_vX.Y.Z.md*
*Created: YYYY-MM-DD*
*Status: Awaiting supervisor acknowledgment*
