# AGET Requirements Format v1.1

**Version**: 1.1.0
**Date**: 2026-04-19
**Status**: Active
**Authority**: Active (normative, minor/patch allowed)
**Author**: private-aget-framework-AGET
**Parallel to**: AGET_SPEC_FORMAT.md v1.3.0 (specification-level meta-doc)
**Evidence**: L748, L749, ISO/IEC/IEEE 29148:2018, Volere, ISO/IEC 25010:2023, C298 (Software System Requirement, ISO/IEC/IEEE 29148:2018 — added FWRK-2026-004)
**Tracking**: #725
**v1.1 changes** (2026-04-19): (a) Added optional `constraints:` per-REQ field for ADRs/governance/meta-docs that bound the REQ but do not implement it; (b) Clarified acceptable `specifications:` types: CAP-*, R-*, SKILL-*, RUBRIC-* (rubrics-as-spec per L749 duality). Motivated by 2026-04-19 audit which found 35/64 `specifications:` citations were category errors (L-docs belong in `evidence:`; ADRs/governance/meta-docs belong in `constraints:`).

---

## Purpose

This document defines the canonical format for **AGET requirements** — human-readable, published capability descriptions that sit above formal specifications (EARS) but below raw observations (L-docs).

Requirements express **what the principal wants** (intent, capabilities, quality attributes). Specifications express **what the framework contracts** (EARS-formalized, testable, enforceable).

### Two-Level Model (L742)

| Level | Name | Audience | Owner | Format | Home |
|-------|------|----------|-------|--------|------|
| **Requirements** | Human level | Principal, stakeholders, community | Principal | This format | `aget/requirements/` |
| **Specifications** | Contract level | Framework, agents, validators | Framework | EARS (AGET_SPEC_FORMAT) | `aget/specs/` |

### Relationship to ISO/IEC/IEEE 29148:2018

| ISO 29148 Level | AGET Equivalent | Status |
|-----------------|-----------------|--------|
| 3. StRS (Stakeholder Requirements) | **This format** | Active |
| 4. SyRS (System Requirements) | `aget/specs/` (EARS) | Established |

---

## Requirement Document Structure

A requirements document covers a **capability area** (e.g., Session Management, Release Quality, Agent Governance). Structure:

```markdown
# REQ-{DOMAIN}: {Capability Area Title}

**Version**: X.Y.Z
**Date**: YYYY-MM-DD
**Status**: draft | proposed | validated | published
**Domain**: {DOMAIN code}
**Specifications**: [list of CAP-xxx specs this traces to]

---

## Overview

[1-3 paragraphs: what this capability area is, why it matters,
who benefits. Written for human stakeholders, not engineers.]

## Functional Requirements

[REQ-{DOMAIN}-F-{NNN} entries — see Per-Requirement Format below]

## Quality Requirements

[REQ-{DOMAIN}-Q-{NNN} entries — classified by ISO 25010:2023]

## Constraints

[Non-negotiable boundaries from ADRs, governance, scope]

## Traceability

[REQ → CAP/R-xxx mapping table]

## Evidence

[L-docs, operational data, and research that ground these requirements]
```

---

## Per-Requirement Format

Each requirement is a YAML+Markdown block. This is the atomic unit.

### Schema

```yaml
id: REQ-{DOMAIN}-{F|Q}-{NNN}
title: "{Human-readable title}"
type: functional | quality
category: "{ISO 25010:2023 category — quality type only}"
description: >
  {Human-readable requirement statement. Implementation-free.
   Describes WHAT the principal wants, not HOW to build it.
   Written in stakeholder language, not engineering language.}
rationale: >
  {WHY this requirement matters. Business/operational justification.
   Connects to principal goals and AGET mission.}
evidence:
  - "{L-doc or operational reference — L700 provenance}"
  - "{Additional evidence}"
fit_criterion: >
  {Volere Fit Criterion: a testable, measurable condition that
   determines whether this requirement is satisfied.
   This is the bridge to EARS specifications.
   Must be verifiable without reading the specification.}
priority: P0 | P1 | P2 | P3
specifications:
  - "{CAP-xxx, R-xxx, SKILL-xxx, or RUBRIC_xxx — forward traceability to contracts}"
constraints:                    # OPTIONAL (added v1.1)
  - "{ADR-xxx, governance/X.md, AGENTS.md section, or SOP_X — non-implementing boundaries that bound this REQ}"
status: draft | proposed | validated | published
originator: principal | operational-evidence | community
```

### Field Definitions

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique identifier. Format: `REQ-{DOMAIN}-{F\|Q}-{NNN}` |
| `title` | Yes | Human-readable, concise (< 80 chars) |
| `type` | Yes | `functional` (what it does) or `quality` (how well it does it) |
| `category` | Quality only | ISO 25010:2023 characteristic (see NFR Taxonomy) |
| `description` | Yes | Stakeholder-language requirement statement |
| `rationale` | Yes | Why this matters (connects to mission/goals) |
| `evidence` | Yes | L-docs, data, research grounding this requirement (L700). **NOT for ADRs/governance docs (those go in `constraints:`).** |
| `fit_criterion` | Yes | Testable condition — the bridge to EARS |
| `priority` | Yes | P0 (critical) through P3 (stretch) |
| `specifications` | No | Forward traceability to **contracts that implement this REQ**. Acceptable types: **CAP-xxx, R-xxx, SKILL-xxx, RUBRIC_xxx** (rubrics-as-spec per L749 duality). NOT for L-docs (use `evidence:`), ADRs (use `constraints:`), or meta-docs/SOPs (use `constraints:`). |
| `constraints` | **No (added v1.1)** | Non-implementing boundaries: ADR-xxx, governance/X.md, AGENTS.md sections, SOP_X procedures, DESIGN_DIRECTION_X docs. These bound the REQ but do not implement it. |
| `status` | Yes | Lifecycle state |
| `originator` | Yes | Source: principal directive, operational evidence, or community |

### Field Selection Decision Tree (added v1.1)

When citing an artifact, route it to the correct field:

```
Is the artifact a CAP-xxx, R-xxx, SKILL-xxx, or RUBRIC_xxx that
implements/contracts this REQ?
   YES → specifications:
   NO ↓

Is the artifact an L-doc, operational data, web research, or
prior incident that GROUNDED this REQ (bottom-up provenance)?
   YES → evidence:
   NO ↓

Is the artifact an ADR, governance doc, AGENTS.md section, SOP,
or DESIGN_DIRECTION that BOUNDS this REQ (non-implementing
boundary)?
   YES → constraints:
   NO ↓

Is it a META-DOC (REQUIREMENTS_FORMAT, AGET_SPEC_FORMAT) that
DEFINES the format of this REQ?
   YES → no per-REQ field (implicit; the doc-level header
         already references the format)

Is it a planning artifact (VERSION_SCOPE, PROJECT_PLAN)?
   YES → no per-REQ field (these are not requirement attributes)
```

### ID Convention

```
REQ-SESSION-F-001     # Session domain, functional, first requirement
REQ-SESSION-Q-001     # Session domain, quality, first requirement
REQ-REL-F-001         # Release domain, functional, first requirement
REQ-GOV-Q-001         # Governance domain, quality, first requirement
```

**Domain codes**: Reuse AGET specification domain codes (SESSION, REL, GOV, TPL, CORE, 5D, VOC, etc.)

---

## NFR Taxonomy: ISO/IEC 25010:2023

Quality requirements (`type: quality`) MUST use one of the 9 ISO 25010:2023 categories:

| Category | Description | AGET Examples |
|----------|-------------|---------------|
| **Functional Suitability** | Correctness, completeness, appropriateness | Spec coverage, validator accuracy |
| **Performance Efficiency** | Time behavior, resource utilization, capacity | Wake-up < 120s, context recovery |
| **Compatibility** | Co-existence, interoperability | Template compatibility, fleet interop |
| **Interaction Capability** | Usability, learnability, operability | Human-AI collaboration quality |
| **Reliability** | Maturity, availability, fault tolerance, recoverability | Session continuity, KB integrity |
| **Security** | Confidentiality, integrity, authenticity | Private-first routing, content sanitization |
| **Maintainability** | Modularity, reusability, analyzability, modifiability, testability | Spec format compliance, upgrade paths |
| **Flexibility** | Adaptability, scalability, installability, replaceability | Template portability, archetype system |
| **Safety** | Operational constraint, risk identification, fail-safe, warning capability | Agent governance, scope boundaries, escalation rules |

**Note**: EARS patterns (AGET_SPEC_FORMAT.md) are NOT suitable for quality requirements (per Mavin). Quality requirements use the fit criterion + ISO 25010 category instead.

---

## Maturity Progression (L682 Mapping)

Requirements mature through L682 content levels:

| L682 Level | Requirement State | Artifact |
|------------|-------------------|----------|
| C0 (Implicit) | Observation in L-doc | `.aget/evolution/L*.md` |
| C1 (Intent) | `status: draft` | `aget/requirements/REQ-*.md` |
| C2 (Structured) | `status: proposed` with fit criterion | `aget/requirements/REQ-*.md` |
| C3 (Grounded) | `status: validated` with evidence + specs | `aget/requirements/REQ-*.md` |
| C4 (Verified) | Specification has V-tests | `aget/specs/` |
| C5 (Wired) | Enforcement in place | Validator / hook |

**Graduation trigger** (L700, L436): 3+ operational occurrences, or principal directive.

---

## Traceability Chain

```
Evidence (L-doc)
    ↓ graduation (L436: 3+ occurrences or principal directive)
Requirement (REQ-xxx)     ← THIS FORMAT
    ↓ conversion (Fit Criterion → EARS)
Specification (CAP-xxx)   ← AGET_SPEC_FORMAT
    ↓ implementation
V-test (VT-xxx)
    ↓ enforcement
Validator / Hook
```

### Conversion Example

```
REQUIREMENT (human level):
  id: REQ-SESSION-F-001
  description: >
    An agent session should recover essential context within
    2 minutes of session start.
  fit_criterion: >
    Context recovery covers agent identity, active projects,
    and recent findings within 120 seconds.

SPECIFICATION (contract level):
  id: CAP-SESSION-001-03
  pattern: ubiquitous
  statement: >
    The SYSTEM shall recover Session_Context WITHIN 120 seconds
    of Session_Start, MAINTAINING coverage of Agent_Identity,
    Active_Projects, and Recent_Findings.
```

The fit criterion makes this conversion mechanical: description → fit criterion → EARS statement.

---

## Requirements-Rubric Duality (L749)

Requirements and rubrics form a **dual pair** — two views of the same quality concern:

| Artifact | Direction | Question | Audience |
|----------|-----------|----------|----------|
| **Requirement** | Prospective | "What does good look like?" | Builder |
| **Rubric** | Retrospective | "How good was this?" | Assessor |

**Design principle**: Requirements are created first (prospective), then rubrics derived from them (retrospective). Rubrics reference requirements via traceability tables; requirements do not embed rubrics.

**L671 test**: A requirement without a rubric assessment path = decorative requirement. A rubric dimension without a traceable requirement = assessing an unstated expectation.

---

## Directory Structure

```
aget/requirements/
├── INDEX.md                              # Registry (parallel to specs/INDEX.md)
├── REQUIREMENTS_FORMAT.md                # This document
├── REQ-REL_release_quality.md            # Release quality requirements
├── REQ-GOV_agent_governance.md           # Governance requirements
├── REQ-SESSION_session_management.md     # Session capability requirements
├── REQ-TPL_template_management.md        # Template management requirements
└── ...
```

**Naming convention**: `REQ-{DOMAIN}_{snake_case_title}.md`

**Versioning**: Independent from framework versions. Requirements version on their own lifecycle (ISO 29148: StRS is an independent document).

---

## Design Decisions

| Decision | Rationale | Alternative Considered |
|----------|-----------|----------------------|
| YAML+Markdown (not pure prose) | Machine-parseable, version-controllable, aligns with AGET patterns | Pure Markdown (rejected: not machine-parseable) |
| ISO 25010:2023 for NFR categories | Most current standard, adds Safety (agent governance) | FURPS+ (rejected: less comprehensive, no Safety) |
| Volere Fit Criterion | Makes requirements testable at human level, bridges to EARS | Gherkin Given-When-Then (rejected: too implementation-oriented) |
| `evidence:` field | Supports L700 bottom-up model | `stakeholders:` field (rejected: AGET is single-principal) |
| `specifications:` field (forward traceability) | Completes REQ → SPEC → V-test chain | No traceability (rejected: violates L352) |
| `originator: principal \| operational-evidence \| community` | Captures AGET's dual-source model (L700 + principal directives) | Single `author:` field (rejected: loses provenance) |
| Separate `functional` / `quality` types | EARS not suitable for NFRs (per Mavin) — different treatment needed | Single type (rejected: quality reqs need ISO 25010 category) |
| One file per capability area | Reduces file proliferation, keeps related reqs together | One file per REQ (rejected: hundreds of files) |
| Separate rubric files (L749) | Requirements = prospective, rubrics = retrospective. Distinct artifacts. | Embedded rubrics (rejected: conflates intent and assessment) |
| Community via issues (#539) | Same governance as spec proposals. Issue → approval → REQ entry. | Direct PRs (rejected: no write access initially) |
| Independent versioning | Requirements change less than specs. Coupling = artificial bumps. | Framework-coupled (rejected: ISO 29148 treats StRS independently) |
| Defer automation to post-v3.11 | L103: validate format manually before automating (ADR-008 progression) | Build /aget-file-requirement now (rejected: premature abstraction) |

---

## Sources

- **ISO/IEC/IEEE 29148:2018** — 5-level document hierarchy, StRS definition
- **Volere Requirements Template** (Robertson & Robertson) — Fit Criterion, Snow Card
- **ISO/IEC 25010:2023** — Quality Model, 9 characteristics (incl. Safety, Flexibility)
- **EARS** (Mavin, Rolls-Royce) — Confirms EARS not suitable for quality attributes
- **SAFe Capabilities** — Capability-oriented (vs feature-oriented) framing
- **Sphinx-Needs** — Docs-as-code requirements pattern
- **Scacchi (UCI)** — OSS requirements as decentralized informalisms

---

*AGET_REQUIREMENTS_FORMAT_v1.0.md*
*"Requirements = what the principal wants. Specifications = what the framework contracts."*
*Ready for publication to aget/requirements/ (Gate 1, #725)*
