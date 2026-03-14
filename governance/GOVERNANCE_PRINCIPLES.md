# Governance Principles: Meta-Principles

**Created**: 2026-03-04
**Updated**: 2026-03-04
**Last Reviewed**: 2026-03-04
**Status**: Active
**Type**: Meta-Governance
**Visibility**: Public (not a focal point of READMEs)
**Source**: L643 (Meta-Principle Taxonomy)

---

## Purpose

Meta-principles are governance constraints that govern how AGET creates, applies, and enforces its own governance artifacts. They answer: **"What rules govern the rules?"**

This document is the fourth principle category, alongside:

| Category | Document | Governs |
|----------|----------|---------|
| Design Principles | DESIGN_PHILOSOPHY.md | What AGET builds |
| Operating Principles | MISSION.md | How this agent executes |
| Positioning Principles | Homepage README.md | How AGET appears |
| **Meta-Principles** | **This document** | **How governance itself works** |

---

## Relationship to Governance Hierarchy

Meta-principles sit **above** the 5-layer governance hierarchy (Specs > Capabilities > Patterns > SOPs > Tools). They are not a 6th layer — they constrain how the hierarchy itself operates:

```
    Meta-Principles (this document)
           │
           ▼ constrain
    ┌─────────────────────────────┐
    │  5-Layer Governance         │
    │  Hierarchy                  │
    │                             │
    │  Specs                      │
    │    > Capabilities           │
    │      > Patterns             │
    │        > SOPs               │
    │          > Tools            │
    └─────────────────────────────┘
           │
           ▼ constrain
    Agent behavior + artifacts
           │
           ▼ produce evidence for
    L-docs + learnings
           │
           ▼ inform updates to
    Meta-Principles
```

The loop closes: meta-principles constrain governance, governance constrains agents, agents produce evidence, evidence informs meta-principles.

---

## Tier 1: Codified Meta-Principles

### 0. Established-Knowledge Grounding

**Principle**: Ground governance artifacts in well-established best-practice principles from recognized fields rather than reinventing through trial and error.

**Established Field(s)**:
- *Primary*: Knowledge management (Nonaka & Takeuchi 1995 — organizational knowledge creation)
- *Secondary*: Ontology engineering (Guarino 1998), competitive intelligence, "standing on shoulders" (Newton)

**Rationale**: Most governance challenges AGET faces have been solved in established fields — project management, software engineering, safety engineering, knowledge management. Reinventing these solutions through trial and error wastes effort and produces inferior results. Connecting to established knowledge provides validated patterns, shared vocabulary, and a research base. This meta-principle governs all other meta-principles: each must cite the established field(s) it connects to.

**In Practice**:
- L331-L332: Theoretical grounding protocol maps every new concept to established theory (BDI, Actor Model, Cybernetics, Extended Mind, CAS)
- L333: Pre-release governance grounding — consult governance specs before releasing
- POL-CI-001: Competitive intelligence policy — survey peer platforms before designing features
- SOP_pre_proposal_kb_audit: 3+ precedent citation rule — cite established precedents or note "novel"
- L346: Research-before-action discipline — follow existing research protocols, then expand
- L185: Environmental grounding — investigate actual state, not cached assumptions

**Anti-Pattern**: "NIH (Not Invented Here)" — reinventing solutions that established fields have already validated. Trial-and-error discovery of principles that knowledge management, organizational theory, or software engineering have long codified.
**AGET Pattern**: "6-level grounding stack" — framework (L331-L332), release (L333), proposal (SOP_pre_proposal_kb_audit), environment (L185), governance (CHARTER/MISSION/ADRs), memory (L335/KB).

**Learning References**: L331, L332, L333, L346, L185, POL-CI-001

---

### 1. Spec-First + Verification

**Principle**: Audit before architecture. Read the governing spec, score conformance, classify gaps — then fix.

**Established Field(s)**:
- *Primary*: Formal verification, design-by-contract (Meyer 1988)
- *Secondary*: V-model (systems engineering), test-driven development

**Rationale**: Governance artifacts exist within a specification hierarchy. Acting without reading the governing spec produces solutions that drift from requirements. The cost of a conformance audit is small compared to the cost of rework from misaligned implementation.

**In Practice**:
- Gate -1 pattern: deductive audit (read spec, score gaps) before inductive planning (look at peers)
- /aget-enhance-spec encodes this as Phase 0
- Every PROJECT_PLAN Phase -1 includes "Prior Work" and "L-doc Review" sections
- New agents run conformance checks before modifying governance artifacts

**Anti-Pattern**: "Fix-first" — jumping to implementation without reading the spec. Produces solutions that don't align with requirements.
**AGET Pattern**: "Audit-first" — read the governing spec, score conformance, classify gaps by severity, then fix in priority order.

**Learning References**: L289, L617, L616, ADR-008

---

### 2. Gate Execution Discipline

**Principle**: Execute only this gate. Stop at the boundary. Validate. Present. Wait for GO.

**Established Field(s)**:
- *Primary*: Stage-gate process (Cooper 1990)
- *Secondary*: Tollgate reviews (project management), phase-gate governance

**Rationale**: Without boundary discipline, work expands to fill available context. Each gate represents a decision point where the principal evaluates direction. Skipping decision points trades short-term speed for long-term misalignment.

**In Practice**:
- V-test at every gate boundary (executable verification)
- Mid-gate checkpoints at 50% for gates with 4+ deliverables (L002, 6-12x ROI)
- Red flags: "While we're at it...", "I also...", "Might as well..."
- Execution governance artifact required before work begins (L340)

**Anti-Pattern**: "While we're at it..." — scope expansion beyond gate boundary, bypassing decision points.
**AGET Pattern**: "Gate boundary protocol" — execute deliverables, run V-test, present completion summary, wait for explicit GO.

**Learning References**: L42, L001, L002, L340

---

### 3. Layered Propagation

**Principle**: Critical patterns need 5 discovery paths: session init, point-of-use, searchable index, proactive surfacing, automated validation.

**Established Field(s)**:
- *Primary*: Defense in depth (security engineering)
- *Secondary*: Swiss cheese model (Reason 1990), redundancy engineering

**Rationale**: A critical principle documented in only one place has probability < 1 of being discovered when needed. Single-point documentation creates "discovery lottery" — whether an agent follows a critical principle depends on whether they happen to find it.

**In Practice**:
- CLAUDE.md: Session init (Layer 1 — highest reliability for session-scoped principles)
- SOP trigger: Point-of-use (Layer 2 — activated when relevant action begins)
- KB index: Searchable (Layer 3 — discoverable via /aget-study-up)
- Wake-up: Proactive surfacing (Layer 4 — presented at session start)
- Validator: Automated (Layer 5 — highest reliability for testable rules)

**Anti-Pattern**: "Discovery lottery" — critical pattern lives in a single document. Agents who happen to find it follow it; those who don't, don't.
**AGET Pattern**: "5-layer propagation" — every critical principle deployed across multiple discovery channels with different reliability characteristics.

**Learning References**: L467, L616, L623

---

### 4. Exemplar Requirement

**Principle**: Governance agents must comply with the standards they enforce, before governing others.

**Established Field(s)**:
- *Primary*: Dogfooding (software engineering practice)
- *Secondary*: Leading by example (leadership theory), "Physician, heal thyself" (medical ethics)

**Rationale**: An agent that publishes standards it doesn't itself meet undermines the legitimacy of those standards. Compliance-first governance ensures that standards are tested against real usage before fleet deployment.

**In Practice**:
- private-aget-framework-AGET must pass the same conformance checks it requires of templates
- New skills proposed by this agent should be adopted here first (L636 — proposer-first principle)
- Template standards are validated against the framework agent's own structure before publishing

**Anti-Pattern**: "Delegation theater" (L284) — governing others while non-compliant yourself. Publishing template standards the framework agent doesn't meet.
**AGET Pattern**: "Compliance-first governance" — verify own compliance before publishing standards for others.

**Learning References**: L367, L636, L284

---

### 5. Infrastructure Over Memory

**Principle**: When a principle is critical, embed it structurally in workflow gates — not as a passive warning in a memory document.

**Established Field(s)**:
- *Primary*: Poka-yoke (Shingo — error-proofing in manufacturing)
- *Secondary*: Forcing functions (Norman 1988), guardrails (safety engineering)

**Rationale**: Memory-based governance depends on the agent remembering to check. Structural governance prevents the error from occurring. The progression from Advisory → Strict → Generator (ADR-008) moves principles from memory-dependent to infrastructure-enforced.

**In Practice**:
- /aget-create-project includes infrastructure spec-first check gate
- Conformance validators run automatically (not manually invoked)
- ADR-008 progression: Advisory (CLAUDE.md warning) → Strict (validator blocks) → Generator (tool produces compliant output)
- L616: Infrastructure gates caught spec-first violations that memory warnings missed

**Anti-Pattern**: "Memory-only governance" — critical rules exist only as advisory text in CLAUDE.md or MEMORY.md. Compliance depends on the agent remembering to check.
**AGET Pattern**: "Structural enforcement" — embed critical principles in workflow gates, validators, and generators.

**Learning References**: L616, L623, ADR-008

---

## Tier 2: Emerging Candidates

Tier 2 meta-principles are named and tracked but not yet fully codified. Each includes promotion criteria — the evidence threshold required to move to Tier 1.

### 6. Human Override Protocol (Tier 2)

**Draft Formulation**: When principal overrides governance: acknowledge, commit, execute. Make the exception visible.

**Evidence**: L178, L591
**Established Field**: Exception handling (software engineering), escalation protocols (ITIL)
**Promotion Criteria**: 3+ additional L-doc instances documenting override events with post-hoc analysis

---

### 7. Artifact Proximity (Tier 2)

**Draft Formulation**: The most proximate artifact governs behavior, not the most authoritative.

**Evidence**: L632
**Established Field**: Locality of reference (computer science), context-dependent governance
**Promotion Criteria**: 3+ instances of proximity overriding authority, with demonstrated behavioral impact

---

### 8. Memory as Substrate (Tier 2)

**Draft Formulation**: The KB is collaboration infrastructure, not documentation. Leave it better than you found it.

**Evidence**: L335, L330
**Established Field**: Transactive memory (Wegner 1987), stigmergy (Grasse 1959), organizational knowledge creation (Nonaka & Takeuchi)
**Promotion Criteria**: Consumption rate measurement — how often non-memory skills query KB to make decisions

---

### 9. Bidirectional Flow (Tier 2)

**Draft Formulation**: Governance flows down (specify > implement) AND up (feedback > learning > spec update).

**Evidence**: L604 (high citation count, but mostly documenting the gap rather than the practice)
**Established Field**: Double-loop learning (Argyris & Schon 1978), cybernetic feedback (Wiener 1948), OODA loop (Boyd)
**Promotion Criteria**: Documented instances of upward flow (L-doc causing spec update) as opposed to only documenting the absence

---

### 10. Scope Discipline (Tier 2)

**Draft Formulation**: Every action classifiable against session mandate. Expand scope only with explicit acknowledgment.

**Evidence**: L342, L591, L131
**Established Field**: Scope management (PMI/PMBOK), change control (configuration management)
**Promotion Criteria**: Validator that checks scope drift during session execution

---

## Established-Field Summary

| MP | Primary Field | Key Reference | Connection |
|----|--------------|---------------|------------|
| 0 | Knowledge management | Nonaka & Takeuchi 1995 | Organizational knowledge creation is a mature discipline |
| 1 | Formal verification | Meyer 1988 (Design by Contract) | Precondition checking is a 40-year practice |
| 2 | Stage-gate process | Cooper 1990 | Phase-gate governance is standard in product development |
| 3 | Defense in depth | Reason 1990 (Swiss Cheese Model) | Redundant safety layers is foundational in safety engineering |
| 4 | Dogfooding | Software engineering practice | "Eat your own dog food" is widely practiced |
| 5 | Poka-yoke | Shingo (Toyota Production System) | Error-proofing through design is a manufacturing standard |

Every Tier 1 meta-principle has a well-established analog in an existing field. AGET did not invent these principles — it discovered them through practice and is now naming them.

---

*Governance Principles v1.1.0*
*"What rules govern the rules?"*
