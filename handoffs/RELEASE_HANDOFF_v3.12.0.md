# RELEASE HANDOFF: v3.12.0

**Version**: 3.12.0
**Released**: 2026-04-04
**Type**: MINOR (Developer Surface & Governance Maturation)
**Prepared By**: private-aget-framework-AGET
**Tracking**: REL-042

---

## Summary

v3.12.0 is the largest-scope release since v3.3.0. It rewrites the developer-facing homepage, adds triage/lifecycle/Issue Forms capabilities to issue governance, introduces epistemic parameterization for study_topic, completes the first deprecation cycle in AGET history, and formalizes release state management.

---

## What Changed

### Issue Governance v2.1.0

- **3 new capabilities**: CAP-ISSUE-006 (Triage), CAP-ISSUE-007 (Lifecycle), CAP-ISSUE-008 (Issue Forms)
- **9 new EARS requirements**: R-ISSUE-015 through R-ISSUE-023
- **54 new SKOS vocabulary terms** across triage, lifecycle, labeling, promotion_workflow
- **3 Issue Form templates** deployed to aget/.github/ISSUE_TEMPLATE/
- **26 faceted labels** deployed to gmelli/aget-aget (type/priority/domain/status/owner)
- **ISSUE_FILING_GUIDE v2.1** with triage and lifecycle sections

### Homepage Rewrite

- README.md: 169 -> 104 lines
- Quick Start moved from line 106 to line 14
- R-HOM-001 conformance: 1/7 -> 6/7
- 3 reference sections relocated to docs/ (Strategic Context, Archetype Ecosystem, Ontology Design)
- REQ-HOM published (6F + 3Q requirements)

### Epistemic Parameterization (study_topic.py)

- `--purpose` flag: pre-implementation, pre-release, exploration, audit
- `--domain-keywords` flag: agent-domain relevance boosting
- Config-driven via `.aget/config.json` study_topic block
- CAP-SESSION-007-06/07 added to AGET_SESSION_SPEC
- Three-tier degradation: flags > config > default

### Release State Management (Gate 0)

- SOP_release_process v1.33 -> v1.37
- VERSION_SCOPE state machine formalized (L708)
- deployment_monitor --init as BLOCKING step
- post_release_validation structural invocation
- tag_release.py for 14-repo automated tagging

### Deprecation Cycle Complete

- `capture` verb removed (POL-DEP-001)
- `study-up` script references removed (SSNA rename)
- `record-nugget` skill directory removed

### Other

- SOP_fleet_migration v1.4: `gh release list` discovery step (L723)

---

## Upgrade Guide

### For Fleet Agents (Main + Remote)

1. Update `@aget-version: 3.12.0` in AGENTS.md/CLAUDE.md
2. Update `.aget/version.json` aget_version to "3.12.0"
3. Copy `scripts/study_topic.py` from aget/ core (new --purpose and --domain-keywords flags)
4. Optional: Add `study_topic` block to `.aget/config.json` for domain-aware search
5. Run `python3 -m pytest tests/ -v` to verify

### For Template Users

Templates are already at v3.12.0. Clone fresh or pull main.

---

## Pilot Tracking

| Agent/Fleet | Version | Confirmed | Date | Notes |
|-------------|---------|:---------:|------|-------|
| private-aget-framework-AGET | 3.12.0 | Yes | 2026-04-04 | Release agent |
| private-supervisor-AGET | — | — | — | Pending |
| Workco fleet (8) | — | — | — | Pending |

---

## Deprecations

None new in v3.12.0. First deprecation cycle CLOSED (3 items from v3.10.0 removed).

---

## Known Issues

- post_release_validation: 9/15 at release time (broken links fixed, org profile updated post-release)
- Org profile update required manual post-release edit
- Template propagation of study_topic.py epistemic params: version bump only, script propagated via core copy

---

## Deferred to v3.13

| Item | Reason |
|------|--------|
| /aget-enhance-config (#614) | Separate project |
| Ontology self-grounding (#576) | Research-intensive |
| L742 requirements grounding | Broad scope |
| L694 convergence refresh | Needs analysis + principal input |
| REQ-REL v1.2 | Depends on requirements grounding |
| /aget-promote-issue skill (SP-004) | Proposed, not implemented (#821) |

---

*RELEASE_HANDOFF_v3.12.0.md*
*"Developer Surface & Governance Maturation"*
