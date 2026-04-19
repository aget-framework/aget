# REQ-HOM: Homepage Quality

**Version**: 1.1.0
**Date**: 2026-04-19
**Status**: proposed
**Domain**: HOM
**Specifications**: [R-HOM-001_homepage_messaging_quality.md](../specs/requirements/R-HOM-001_homepage_messaging_quality.md), RUBRIC_voice_conformance_v1.0
**Format Version**: REQUIREMENTS_FORMAT v1.0 (refactored from inline-prose v1.0.0 for rubric scorability — 2026-04-19)

---

## Overview

The AGET homepage (`aget/README.md`) is the primary first-impression artifact for developers discovering the framework. It must communicate what AGET is, what problems it solves, and how to start — in the principal's authentic voice. This document specifies the human-level requirements for homepage quality; CAP-* and rubric artifacts implement enforcement at the contract level.

REQ-HOM is one of four published REQ-* domains in `aget/requirements/`, alongside REQ-CORE (cross-cutting foundations), REQ-GOV (governance), and REQ-REL (release quality).

---

## Functional Requirements

```yaml
id: REQ-HOM-F-001
title: "Quick Start Above the Fold"
type: functional
description: >
  The homepage shall present installation and first-use instructions
  within the first 35 lines, before any philosophy, architecture, or
  feature detail.
rationale: >
  Quick Start placement determines developer retention. Reference
  exemplars (LangChain 84-line README, makeareadme.com, GitHub Docs)
  consistently put installation early. The current README placement
  at line 106 means most visitors never reach it.
evidence:
  - "L407 (Pain-Point Framing)"
  - "Web research: LangChain README, makeareadme.com, GitHub Docs Quick Start placement patterns"
  - "Operational evidence: pre-refactor README placed install at line 106; bounce analytics indicate drop-off"
fit_criterion: >
  Installation command appears at or before line 35 of aget/README.md;
  first usage example appears at or before line 60.
priority: P1
specifications:
  - "R-HOM-001-02 (audience targeting)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-F-002
title: "Pain-Point Framing"
type: functional
description: >
  The homepage shall lead with problems AGET solves
  (e.g., "lost context between sessions", "agents that can't
  learn from each other") rather than features or architecture.
rationale: >
  Users search for problems, not product categories. Pain-point
  framing matches search intent and creates immediate relevance
  for visitors arriving from search.
evidence:
  - "L407 (Pain-Point Framing)"
fit_criterion: >
  First substantive paragraph (after title and badge row) names
  >=2 concrete user-language pain points; no architecture term or
  internal feature name appears before line 25.
priority: P1
specifications:
  - "R-HOM-001-04 (pain-point framing)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-F-003
title: "Evidence-Based Claims Only"
type: functional
description: >
  The homepage shall not claim capabilities that are not demonstrated
  by existing AGET artifacts. Each major claim shall include a proof
  link to a real AGET file or release.
rationale: >
  Platform "validated" claims without evidence are L92 instances
  (Premature Victory). The homepage carries the highest credibility
  cost when evidence-claim divergence is detected by visitors.
evidence:
  - "L289 (Evidence-First Design)"
  - "L92 (Premature Victory)"
  - "Operational incident: 'Codex CLI validated' / 'Gemini CLI validated' claims without documented validation dates"
fit_criterion: >
  Every capability claim has at least one of (a) a link to an AGET
  artifact, (b) a link to a release tag, (c) a qualifier
  "(experimental)" or "(planned)". 0 unsupported claims when
  homepage is grep'd for capability verbs.
priority: P0
specifications:
  - "R-HOM-001-01 (evidence-based)"
  - "R-HOM-001-05 (proof links)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-F-004
title: "Honest Platform Status"
type: functional
description: >
  The homepage shall clearly distinguish (a) platforms actively
  developed against (Baseline), (b) platforms tested and compatible
  with last-validation date (Compatible), and (c) platforms not yet
  tested (Experimental).
rationale: >
  Codex CLI and Gemini CLI were marked "validated" without
  documented validation dates — a specific incident motivating
  this requirement. Honest status preserves credibility when
  visitors verify claims independently.
evidence:
  - "L92 (Premature Victory)"
  - "Operational incident: Codex/Gemini undated 'validated' claims"
  - "R-HOM-001-03 (aspirational marking)"
  - "R-HOM-001-07 (credibility indicators)"
fit_criterion: >
  Every platform mentioned in any compatibility table has one of
  {Baseline, Compatible (YYYY-MM-DD), Experimental}; 0 platforms
  appear without a status tag.
priority: P1
specifications:
  - "R-HOM-001-03 (aspirational marking)"
  - "R-HOM-001-07 (credibility indicators)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-F-005
title: "Reference Content in docs/"
type: functional
description: >
  Philosophy, strategic context, archetype ecosystem, and ontology
  design sections shall live in docs/ with links from the homepage,
  not inline in the README.
rationale: >
  L657 (Content Absorption Risk During Rewrites) — a ~100-line
  README linking to docs/ is more maintainable than a 169-line
  document with inline reference material. Developers want Quick
  Start, not philosophy essays, on first contact.
evidence:
  - "L657 (Content Absorption Risk)"
  - "Operational evidence: pre-refactor README was 169 lines with inline philosophy section"
fit_criterion: >
  aget/README.md contains 0 H1/H2 sections titled Philosophy,
  Architecture, Ecosystem, or Ontology Design; each such topic
  is referenced by a link to docs/.
priority: P1
specifications:
  - "R-HOM-001-02 (developer-first audience)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-F-006
title: "Content Preservation During Rewrites"
type: functional
description: >
  Homepage rewrites shall preserve all prior release entries in the
  roadmap section and shall not absorb earlier release content into
  the current release entry.
rationale: >
  L657 — v3.7.0 disappeared entirely during v3.8.0 rewrite.
  Release history is institutional memory; absorption erases the
  framework's evolution narrative.
evidence:
  - "L657 (Content Absorption Risk)"
  - "Operational incident: v3.7.0 entry absorbed into v3.8.0 entry during 2025 rewrite"
fit_criterion: >
  After any homepage rewrite, every release entry present in
  CHANGELOG.md is present in the homepage roadmap section;
  pre-rewrite line count of the release section <= post-rewrite
  line count of the release section.
priority: P1
specifications:
  - "CAP-HOM-001 (PROPOSED — see PROPOSAL_cap_hom_preservation_during_rewrites.md; spec authoring deferred to v3.15)"
constraints:
  - "SOP_release_process.md homepage update procedure (the procedural wrapper around this REQ)"
status: proposed
originator: operational-evidence
```

---

## Quality Requirements

```yaml
id: REQ-HOM-Q-001
title: "Principal's Voice"
type: quality
category: "Interaction Capability"
description: >
  The homepage shall be written in the principal's authentic voice:
  direct, conversational prose with short declarative sentences. It
  shall not use em-dash compound constructions or AI-generated
  marketing copy patterns.
rationale: >
  Voice authenticity is non-negotiable for the most visible artifact.
  The principal has identified em-dash-heavy compound sentences as
  the primary tell of AI-generated text; the homepage is the worst
  place to fail this signal.
evidence:
  - "L733 (Voice as Composition Driver)"
  - "Exemplar: org profile opening paragraph (2026-04-04 version)"
  - "L800 (Voice Architecture 5-Layer Model)"
fit_criterion: >
  0 em-dash compound constructions in homepage prose; >=80% of
  sentences are <=15 words; voice-conformance score >=L2 when
  scored against RUBRIC_voice_conformance_v1.0.
priority: P0
specifications:
  - "RUBRIC_voice_conformance_v1.0 (rubric-as-spec)"
status: proposed
originator: principal
```

```yaml
id: REQ-HOM-Q-002
title: "Compact Size"
type: quality
category: "Maintainability"
description: >
  The homepage shall be <=120 lines. Reference material that
  pushes the README beyond this limit shall be relocated to docs/.
rationale: >
  Web research (LangChain 84 lines, Standard Readme Spec 70-230
  range) bounds the readable size. Pre-refactor was 169 lines with
  visible reader fatigue.
evidence:
  - "Web research: LangChain README line count, Standard Readme Spec"
  - "Operational evidence: 169-line pre-refactor baseline"
fit_criterion: >
  `wc -l aget/README.md` returns a value <=120.
priority: P2
specifications:
  - "R-HOM-001-02 (developer-first audience — implies brevity)"
status: proposed
originator: operational-evidence
```

```yaml
id: REQ-HOM-Q-003
title: "Coherent First Impression"
type: quality
category: "Functional Suitability"
description: >
  The homepage (README.md) and the organization profile
  (.github/profile/README.md) shall present a coherent first
  impression — consistent terminology, aligned claims, and
  complementary (not duplicative) content.
rationale: >
  Developers may land on either surface first. Contradictions
  between them undermine credibility before any technical
  evaluation begins.
evidence:
  - "REL-042 Gate 2 (coordinated first impression validation)"
  - "Operational evidence: principal-driven coordination during 2026-04-04 release"
fit_criterion: >
  Diff of major-claim sentences between aget/README.md and
  .github/profile/README.md shows 0 contradictions; key
  terminology (AGET, agent, fleet, principal) is used identically
  across both surfaces.
priority: P1
specifications:
  - "CAP-HOM-002 (PROPOSED — see PROPOSAL_cap_hom_coherence_first_impression.md; spec authoring deferred to v3.15)"
constraints:
  - "REL-042 Gate 2 procedure (operational instance demonstrating coordinated first impression validation)"
status: proposed
originator: operational-evidence
```

---

## Constraints

| Constraint | Source | Apply When |
|------------|--------|------------|
| Homepage is the most visible AGET artifact | governance/MISSION.md | Any homepage edit |
| Voice authenticity is non-negotiable | REQ-HOM-Q-001, L733 | Any homepage prose change |
| L735 push window discipline | governance/POLICY_push_window | Publishing homepage changes (Saturday only autonomous) |
| L656 Loading Dock | Post-publish verification | After any homepage push, verify rendered output on github.com |

---

## Traceability

| Requirement | Forward → Specification | Evidence Anchor |
|-------------|-------------------------|-----------------|
| REQ-HOM-F-001 | R-HOM-001-02 | L407 + web research |
| REQ-HOM-F-002 | R-HOM-001-04 | L407 |
| REQ-HOM-F-003 | R-HOM-001-01, R-HOM-001-05 | L289, L92 |
| REQ-HOM-F-004 | R-HOM-001-03, R-HOM-001-07 | L92 + Codex/Gemini incident |
| REQ-HOM-F-005 | R-HOM-001-02 | L657 |
| REQ-HOM-F-006 | CAP-HOM-001 (PROPOSED) | L657 + v3.7.0 absorption incident |
| REQ-HOM-Q-001 | RUBRIC_voice_conformance_v1.0 | L733, L800 |
| REQ-HOM-Q-002 | R-HOM-001-02 | LangChain/Standard Readme benchmarks |
| REQ-HOM-Q-003 | CAP-HOM-002 (PROPOSED) | REL-042 Gate 2 + coordinated first impression validation |

Forward traceability is mandatory (REQ-CORE-F-001). The table above shall remain synchronized with each REQ block's `specifications:` field.

---

## Evidence

This document grounds in:
- **L289** — Evidence-First Design (audit before architecture)
- **L407** — Pain-Point Framing (search-intent matching)
- **L657** — Content Absorption Risk During Rewrites (lossy refactors)
- **L733** — Voice as Composition Driver
- **L800** — Voice Architecture 5-Layer Model
- **L92** — Premature Victory (the anti-pattern REQ-HOM-F-003 defends against)
- **REL-042 Gate 2** — Coordinated first impression validation (operational instance)
- **C298** (Software System Requirement, ISO/IEC/IEEE 29148:2018 — added FWRK-2026-004 2026-04-19) — ontology grounding for all REQ-HOM-* artifacts

---

## Format Refactor Note (2026-04-19)

This document was refactored on 2026-04-19 from inline-prose format to YAML+Markdown REQ blocks per REQUIREMENTS_FORMAT.md v1.0. The refactor preserves all 9 original requirements with the same titles, rationales, and traceability. Added per-requirement: `evidence:`, `fit_criterion:`, `priority:`, `originator:`, and (for quality reqs) `category:`. Motivation: enable mechanical scoring against `RUBRIC_requirement_quality_v1.0.md`. Refactor surfaced as observation in scoring memo `docs/scoring/SCORING_2026-04-19_req_cap.md` (REQ-HOM was the one published REQ-* file unscorable in the original run).

---

*REQ-HOM_homepage_quality.md v1.1.0*
*"Developer landing page, not reference document. In the principal's voice."*
*Refactored to REQUIREMENTS_FORMAT v1.0 — 2026-04-19*
