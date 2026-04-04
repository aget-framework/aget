# REQ-HOM: Homepage Quality

**Version**: 1.0.0
**Date**: 2026-04-04
**Status**: proposed
**Domain**: HOM
**Specifications**: [R-HOM-001_homepage_messaging_quality.md](../specs/requirements/R-HOM-001_homepage_messaging_quality.md)
**Evidence**: L733 (Voice), L407 (Pain-Point Framing), L657 (Content Absorption), L289 (Evidence-First)

---

## Context

The AGET homepage (aget/README.md) is the primary first-impression artifact for developers discovering the framework. It must communicate what AGET is, what problems it solves, and how to start — in the principal's authentic voice.

---

## Functional Requirements

### REQ-HOM-F-001: Quick Start Above the Fold

The homepage SHALL present installation and first-use instructions within the first 35 lines, before any philosophy, architecture, or feature detail.

**Rationale**: Web research (LangChain 84-line exemplar, makeareadme.com, GitHub Docs) consistently shows Quick Start placement determines developer retention. Line 106 in the current README means most visitors never reach it.

**Traces to**: R-HOM-001-02 (audience targeting)

### REQ-HOM-F-002: Pain-Point Framing

The homepage SHALL lead with problems AGET solves ("lost context between sessions", "agents that can't learn from each other") rather than features or architecture.

**Rationale**: L407 — users search for problems, not product categories. Pain-point framing matches search intent and creates immediate relevance.

**Traces to**: R-HOM-001-04 (pain-point framing)

### REQ-HOM-F-003: Evidence-Based Claims Only

The homepage SHALL NOT claim capabilities that are not demonstrated by existing AGET artifacts. Each major claim SHALL include a proof link to a real AGET file or release.

**Rationale**: L289 (evidence-first), L92 (premature victory). Platform "validated" claims without evidence = L92.

**Traces to**: R-HOM-001-01 (evidence-based), R-HOM-001-05 (proof links)

### REQ-HOM-F-004: Honest Platform Status

The homepage SHALL clearly distinguish between platforms that are actively developed against (Baseline), platforms tested and compatible (Compatible — with last validation date), and platforms not yet tested (Experimental).

**Rationale**: R-HOM-001-03 (aspirational marking), R-HOM-001-07 (credibility indicators). Codex CLI and Gemini CLI were marked "validated" without documented validation dates.

**Traces to**: R-HOM-001-03, R-HOM-001-07

### REQ-HOM-F-005: Reference Content in docs/

Philosophy, strategic context, archetype ecosystem, and ontology design sections SHALL live in docs/ with links from the homepage, not inline in the README.

**Rationale**: L657 (content absorption risk during rewrites). A ~100-line README linking to docs/ is more maintainable than a 169-line document with inline reference material.

**Traces to**: R-HOM-001-02 (developer-first audience — developers want Quick Start, not philosophy essays)

### REQ-HOM-F-006: Content Preservation During Rewrites

Homepage rewrites SHALL preserve all prior release entries in the roadmap section and SHALL NOT absorb earlier release content into the current release entry.

**Rationale**: L657 — v3.7.0 disappeared entirely during v3.8.0 rewrite.

**Traces to**: SOP_release_process.md homepage update procedure

---

## Quality Requirements

### REQ-HOM-Q-001: Principal's Voice

The homepage SHALL be written in the principal's authentic voice: direct, conversational prose with short declarative sentences. It SHALL NOT use em-dash compound constructions or AI-generated marketing copy patterns.

**Rationale**: L733 (voice as composition driver). The principal identified em-dash-heavy compound sentences as the primary tell of AI-generated text. The homepage is the most visible artifact — voice authenticity is non-negotiable.

**Exemplar**: The org profile opening paragraph (2026-04-04 version) is the current voice reference.

### REQ-HOM-Q-002: Compact Size

The homepage SHALL be ≤120 lines. Reference material that pushes the README beyond this limit SHALL be relocated to docs/.

**Rationale**: Web research (LangChain 84 lines, Standard Readme Spec 70-230 range). Current: 169 lines.

### REQ-HOM-Q-003: Coherent First Impression

The homepage (README.md) and the organization profile (.github/profile/README.md) SHALL present a coherent first impression — consistent terminology, aligned claims, and complementary (not duplicative) content.

**Rationale**: Developers may land on either surface first. Contradictions between them undermine credibility.

---

## Traceability

```
REQ-HOM-F-001 → R-HOM-001-02 (audience)
REQ-HOM-F-002 → R-HOM-001-04 (pain-point framing)
REQ-HOM-F-003 → R-HOM-001-01, R-HOM-001-05 (evidence, proof links)
REQ-HOM-F-004 → R-HOM-001-03, R-HOM-001-07 (aspirational, credibility)
REQ-HOM-F-005 → R-HOM-001-02 (developer-first)
REQ-HOM-F-006 → L657 (content absorption)
REQ-HOM-Q-001 → L733 (voice composition)
REQ-HOM-Q-002 → Web research (README line count benchmarks)
REQ-HOM-Q-003 → REL-042 Gate 2 (coordinated first impression)
```

---

*REQ-HOM_homepage_quality.md v1.0.0*
*"Developer landing page, not reference document. In the principal's voice."*
