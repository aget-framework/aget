# AGET_CONTENT_INTEGRITY_SPEC v1.0.0

**Status**: Active
**Version**: 1.0.0
**Date**: 2026-02-28
**Domain**: CI (Content Integrity)
**Maturity**: minimal
**Governing Spec**: AGET_SPEC_FORMAT v1.3.0

---

## Abstract

Defines requirements for validating that prose claims in documentation match their source-of-truth documents. Covers 8 content integrity dimensions identified through systematic 5-Whys analysis of drift patterns observed across 3 consecutive releases (v3.4.0–v3.6.0).

---

## Motivation

Content claim drift occurs when documentation files make claims — platform support, skill counts, version numbers, SOP availability — that diverge from their source-of-truth specifications. Manual fixes fail because there is no enforcement mechanism, only documentation saying "remember to update" (L605). Validation tooling checks artifact-level properties (file exists, parses correctly) but not whether claims in prose match structured data sources (L608).

---

## Scope

### In Scope

1. Source-of-truth mappings for 8 content integrity dimensions (L608)
2. Validation requirements per dimension (EARS format)
3. Gate integration points for automated checking
4. Alignment with existing validators (test_version_enforcement.py, aget_conformance_report.py)

### Out of Scope

- Implementing validators (follow-on work after spec)
- Retroactive content audit (separate cleanup task)
- Modifying AGET_SPEC_FORMAT

---

## Vocabulary (SKOS)

```yaml
Content_Claim:
  skos:prefLabel: "Content_Claim"
  skos:definition: "Prose statement asserting a fact that has a source-of-truth"
  skos:example: ["'supports Cursor'", "'13 universal skills'", "'v3.5.0'"]
  aget:source: "L608"

Source_Of_Truth:
  skos:prefLabel: "Source_Of_Truth"
  skos:definition: "Authoritative file defining the canonical value for a claim type"
  skos:example: ["CLI_SUPPORT_MATRIX.md", "AGET_TEMPLATE_SPEC.md", "version.json"]
  aget:source: "L608"

Claim_Drift:
  skos:prefLabel: "Claim_Drift"
  skos:definition: "Divergence between a Content_Claim and its Source_Of_Truth value"
  skos:broader: "Quality_Defect"
  aget:source: "L608"

Content_Integrity_Dimension:
  skos:prefLabel: "Content_Integrity_Dimension"
  skos:definition: "One of 8 categories of claim-source validation"
  skos:note: "Dimensions 1-6 are pre-release audit scope; 7-8 are post-release"
  aget:source: "L608"

Claim_Source_Mapping:
  skos:prefLabel: "Claim_Source_Mapping"
  skos:definition: "Explicit association between a Content_Claim type and its Source_Of_Truth file"
  aget:source: "This spec"

Platform_Claim:
  skos:prefLabel: "Platform_Claim"
  skos:definition: "Content_Claim asserting support status for a specific CLI platform"
  skos:broader: "Content_Claim"
  aget:source: "L608 Dim 1"

Quantitative_Claim:
  skos:prefLabel: "Quantitative_Claim"
  skos:definition: "Content_Claim asserting a numeric value about framework capabilities"
  skos:broader: "Content_Claim"
  aget:source: "L608 Dim 2"

Private_Name_Leak:
  skos:prefLabel: "Private_Name_Leak"
  skos:definition: "Occurrence of private agent names in public-facing content"
  skos:broader: "Content_Claim"
  aget:source: "L520, L608 Dim 3"

Phantom_Reference:
  skos:prefLabel: "Phantom_Reference"
  skos:definition: "Reference to an artifact that does not exist on disk"
  skos:broader: "Claim_Drift"
  aget:source: "L608 Dim 6"

Version_Bearing_File:
  skos:prefLabel: "Version_Bearing_File"
  skos:definition: "File containing version strings that must match version.json"
  aget:source: "L608 Dim 7"

Version_Producing_Script:
  skos:prefLabel: "Version_Producing_Script"
  skos:definition: "Script that generates version-bearing output at runtime"
  skos:note: "Distinct from Version_Bearing_File — produces versioned content dynamically"
  aget:source: "L608 Dim 8"
```

---

## Source-of-Truth Mapping

| Dim | Name | Source_Of_Truth | Validation_Method |
|:---:|------|-----------------|-------------------|
| 1 | Platform support | `aget/docs/AGET_CLI_SUPPORT_MATRIX.md` | Platform claim validator |
| 2 | Skill counts | `aget/specs/AGET_TEMPLATE_SPEC.md` | Quantitative claim validator |
| 3 | Private names | Detection pattern (`private-*` grep) | Content security scanner |
| 4 | Template identity | `{template}/identity.json` | Identity consistency check |
| 5 | Dead links | Filesystem (target existence) | Link validator |
| 6 | Phantom SOPs | `sops/` directory listing | SOP reference validator |
| 7 | README versions | `.aget/version.json` | README version conformance |
| 8 | Executable versions | `.aget/version.json` | Executable version scanner |

---

## Requirements

### CAP-CI-001: Source-of-Truth Governance

The SYSTEM shall enforce source-of-truth mappings for content claims.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-001 | ubiquitous | The SYSTEM shall maintain a Claim_Source_Mapping for each Content_Integrity_Dimension |
| R-CI-002 | ubiquitous | Each Claim_Source_Mapping shall identify the Source_Of_Truth file path for the claim type |
| R-CI-003 | conditional | IF a Source_Of_Truth file is referenced in a Claim_Source_Mapping THEN the file shall exist on disk |

**Evidence**: L608 root cause — prose claims decoupled from structured source-of-truth documents.
**Enforcement**: Source-of-Truth Mapping table (this spec).

### CAP-CI-002: Platform Support Claims

The SYSTEM shall validate Platform_Claims against the CLI Support Matrix.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-004 | ubiquitous | The Source_Of_Truth for Platform_Claims shall be `aget/docs/AGET_CLI_SUPPORT_MATRIX.md` |
| R-CI-005 | conditional | IF a file contains a Platform_Claim THEN the claimed platform status shall match CLI_SUPPORT_MATRIX.md |
| R-CI-006 | prohibited | Content shall NOT assert platform support status that contradicts CLI_SUPPORT_MATRIX.md |

**Evidence**: L608 Dim 1 — 20+ files claimed "Claude Code, Cursor, Aider, Windsurf" as equivalent; Support Matrix defines tiered classification.
**Enforcement**: Platform claim validator (planned).

### CAP-CI-003: Quantitative Claims

The SYSTEM shall validate Quantitative_Claims against their Source_Of_Truth documents.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-007 | ubiquitous | The Source_Of_Truth for skill count claims shall be `aget/specs/AGET_TEMPLATE_SPEC.md` |
| R-CI-008 | conditional | IF a file contains a Quantitative_Claim about skill counts THEN the number shall match AGET_TEMPLATE_SPEC.md |
| R-CI-009 | conditional | IF a file contains a Quantitative_Claim about template counts THEN the number shall match the AGET_TEMPLATE_SPEC.md archetype table |

**Evidence**: L608 Dim 2 — 9 files claimed "13 universal skills" when actual count was 14.
**Enforcement**: Quantitative claim validator (planned).

### CAP-CI-004: Private Name Boundary

The SYSTEM shall prevent Private_Name_Leaks in public content.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-010 | prohibited | Public-facing content shall NOT contain private agent name patterns (`private-*-aget`, `private-*-AGET`) |
| R-CI-011 | prohibited | Public-facing content shall NOT contain private repository references |
| R-CI-012 | event-driven | WHEN content is prepared for public repositories THEN the SYSTEM shall scan for Private_Name_Leak patterns |

**Evidence**: L520 + L608 Dim 3 — 134 private name instances leaked to public content in v3.6.0.
**Enforcement**: Content security scanner (planned). See also: AGET_ISSUE_GOVERNANCE_SPEC.

### CAP-CI-005: Template Identity Consistency

The SYSTEM shall validate template identity claims against identity files.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-013 | ubiquitous | The Source_Of_Truth for template archetype claims shall be the template's `identity.json` |
| R-CI-014 | conditional | IF a template AGENTS.md contains archetype descriptions THEN the content shall match the `identity.json` archetype field |
| R-CI-015 | conditional | IF a template AGENTS.md exceeds 500 lines THEN the SYSTEM shall flag for identity verification |

**Evidence**: L608 Dim 4 — spec-engineer AGENTS.md contained 1,368 lines of advisor content (copy-paste error).
**Enforcement**: Identity consistency check (planned).

### CAP-CI-006: Reference Integrity

The SYSTEM shall validate that references resolve to existing artifacts.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-016 | conditional | IF a markdown file contains an internal link THEN the link target shall exist on disk |
| R-CI-017 | conditional | IF a file references an SOP by name (`SOP_*.md` pattern) THEN the referenced SOP shall exist in the `sops/` directory |
| R-CI-018 | ubiquitous | The Source_Of_Truth for SOP existence shall be the `sops/` directory listing |
| R-CI-019 | prohibited | Documentation shall NOT reference Phantom_References as normative guidance |

**Evidence**: L608 Dim 5+6 — 2 dead README links, 17 phantom SOP references. L607 — graph-based validation needed.
**Enforcement**: Link validator + SOP reference validator (planned).

### CAP-CI-007: Version String Consistency

The SYSTEM shall validate version strings in documentation against version.json.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-020 | ubiquitous | The Source_Of_Truth for version claims shall be `.aget/version.json` |
| R-CI-021 | conditional | IF a Version_Bearing_File contains a version string THEN the version shall match `.aget/version.json` |
| R-CI-022 | ubiquitous | The SYSTEM shall maintain an inventory of all Version_Bearing_Files |
| R-CI-023 | event-driven | WHEN a version bump occurs THEN all Version_Bearing_Files shall be updated |

**Evidence**: L608 Dim 7 — ~20 files with stale version strings post-release. Principal discovered v3.5.0 on GitHub after v3.6.0 release.
**Enforcement**: `aget_conformance_report.py` (check_readme_version, partial). Extend to full inventory.

### CAP-CI-008: Executable Version Strings

The SYSTEM shall validate version handling in Version_Producing_Scripts.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-024 | prohibited | Version_Producing_Scripts shall NOT hardcode version constants for runtime output |
| R-CI-025 | ubiquitous | Version_Producing_Scripts classified as Runtime_Fix shall read version from `.aget/version.json` |
| R-CI-026 | conditional | IF a Python script contains a version string pattern THEN the script shall be classified as Runtime_Fix, Intentional, or Stale per L608 taxonomy |
| R-CI-027 | event-driven | WHEN a new Python script is created that produces version-bearing output THEN the script shall read version from `.aget/version.json` |

**Evidence**: L608 Dim 8 — wind_down.py hardcoded "2.9.0" at v3.6.0. 5-Whys: scripts that produce version-bearing output are a hidden category.
**Enforcement**: `tests/test_version_enforcement.py` (active).

### CAP-CI-009: Gate Integration

The SYSTEM shall integrate content integrity validation at release gate boundaries.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-CI-028 | event-driven | WHEN a release gate boundary is reached THEN the SYSTEM shall execute content integrity validation |
| R-CI-029 | ubiquitous | Pre-release validation shall cover Content_Integrity_Dimensions 1 through 6 |
| R-CI-030 | ubiquitous | Post-release validation shall cover Content_Integrity_Dimension 7 (Version_Bearing_Files) |
| R-CI-031 | conditional | IF content integrity validation fails THEN the release shall NOT proceed past the current gate |

**Evidence**: L605 — fixes as documentation not enforcement. L608 — drift recurred 3 consecutive releases despite manual fix attempts.
**Enforcement**: Gate integration via SOP_release_process.md (planned).

---

## Existing Validator Alignment

| Validator | Location | Dimensions | Status |
|-----------|----------|:----------:|--------|
| Executable version scanner | `tests/test_version_enforcement.py` | 8 | Active |
| README version conformance | `.aget/patterns/conformance/aget_conformance_report.py` | 7 | Active (partial) |
| Version consistency | `.aget/patterns/sync/version_consistency.py` | 7 | Active (cross-template) |
| Template sync check | `.aget/patterns/sync/template_sync_check.py` | — | Active (structure only) |

---

## Graduation History

| Version | Source | Rationale |
|---------|--------|-----------|
| 1.0.0 | L608, L607, L606, L605, L520 | Content claim drift observed in 3 consecutive releases; 8 dimensions identified through systematic 5-Whys analysis |

---

## Theoretical Basis

| Theory | Application |
|--------|-------------|
| Cybernetics (Ashby) | Content claim drift = loss of requisite variety in feedback loop. Claim-source validation restores control system coverage. (L608) |
| Stigmergy (Grasse) | Source-of-truth documents are environmental markers for coordination. Prose bypassing markers breaks stigmergic synchronization. (L608) |
| Extended Mind (Clark/Chalmers) | Source-of-truth files extend cognitive state across sessions. Drift means the extended mind holds inconsistent beliefs. |

---

## References

- L608: Content Claim Drift (8 dimensions)
- L607: Referential Integrity Across Deployment Boundaries
- L606: Development Standard Enforcement Gap
- L605: Release Observability Enforcement Gap
- L520: Issue Governance Gap
- L611: Stale VERSION_SCOPE Classifications
- AGET_SPEC_FORMAT v1.3.0 (governing spec)
- AGET_TEMPLATE_SPEC.md (source-of-truth for Dim 2)
- AGET_CLI_SUPPORT_MATRIX.md (source-of-truth for Dim 1)
- AGET_ISSUE_GOVERNANCE_SPEC.md (related — Dim 3)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-28 | Initial specification — 8 content integrity dimensions, 31 EARS requirements, 9 CAP groups |

---

*AGET_CONTENT_INTEGRITY_SPEC v1.0.0 — Content Claim Validation*
*"Validate claims against sources, not just claim syntax." (L608)*
