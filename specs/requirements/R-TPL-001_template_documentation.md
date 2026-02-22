# R-TPL-001: Template Documentation Requirements

**Version**: 1.0.0
**Status**: Active
**Category**: Requirements (Documentation Governance)
**Format Version**: 1.2
**Created**: 2025-12-29
**Updated**: 2025-12-29
**Author**: aget-framework
**Location**: `aget/specs/requirements/R-TPL-001_template_documentation.md`
**Change Origin**: Gap analysis - internal specs not visible in public READMEs
**Related Specs**: AGET_TEMPLATE_SPEC, WORKER_TEMPLATE_SPEC, R-PUB-001

---

## Abstract

This specification defines requirements for AGET template documentation. Template READMEs must provide visible traceability to governing specifications, enabling users to understand the formal backing behind template capabilities.

## Motivation

AGET maintains 32 comprehensive specifications in `aget/specs/`, but users visiting template READMEs on GitHub see no evidence of this rigor:

| Internal State | External State (Gap) |
|----------------|----------------------|
| AGET_TEMPLATE_SPEC v3.1 (783 lines) | No spec reference |
| WORKER_TEMPLATE_SPEC (35 CAP-* capabilities) | No capability IDs |
| Contract tests (7+ per template) | No test badge |
| EARS patterns throughout | Informal prose only |

**Root Cause**: No specification governed template documentation requirements. R-PUB-001 covers the organization homepage but not individual template READMEs.

**Solution**: This specification (R-TPL-001) establishes requirements for template README documentation, creating visible spec-to-README traceability.

## Scope

**Applies to**: All AGET template READMEs (`template-*/README.md`).

**Defines**:
- Required Specification section structure
- Version consistency requirements
- Spec link requirements
- Contract test disclosure
- Capability listing requirements

**Does NOT apply to**: Agent instance READMEs, organization homepage (covered by R-PUB-001).

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "template_documentation"
    version: "1.0.0"
    inherits: "aget_core"

  documentation:
    Template_README:
      skos:definition: "User-facing documentation file for AGET templates"
      aget:location: "template-*/README.md"
    Specification_Section:
      skos:definition: "README section providing spec traceability"
      skos:notation: "## Specification"
    Spec_Badge:
      skos:definition: "Structured table showing governing specs and attributes"
    Governed_By_Link:
      skos:definition: "Hyperlink to primary governing specification"
    Foundation_Link:
      skos:definition: "Hyperlink to foundation capability specification"

  traceability:
    Spec_README_Traceability:
      skos:definition: "Explicit connection from README to governing specs"
    Capability_Reference:
      skos:definition: "CAP-* ID reference in README"
    Version_Consistency:
      skos:definition: "README version matching manifest.yaml version"
```

---

## Requirements

### R-TPL-001-01: Specification Section Required

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-01 | ubiquitous | Template_README SHALL include Specification_Section |

**Enforcement**: `validate_readme_claims.py`

**Rationale**: Users must be able to find spec backing from the README.

---

### R-TPL-001-02: Governing Spec Reference

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-02 | ubiquitous | Specification_Section SHALL include Governed_By_Link to primary spec |

**Enforcement**: `validate_readme_claims.py` (link validation)

**Required Link Format**:
```markdown
| **Governed By** | [AGET_TEMPLATE_SPEC v3.1](https://github.com/aget-framework/aget/blob/main/specs/AGET_TEMPLATE_SPEC.md) |
```

---

### R-TPL-001-03: Archetype Declaration

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-03 | ubiquitous | Specification_Section SHALL declare Archetype matching manifest.yaml |

**Enforcement**: `validate_readme_claims.py` (archetype match)

**Rationale**: Users need to understand the template's role classification.

---

### R-TPL-001-04: Contract Test Disclosure

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-04 | ubiquitous | Specification_Section SHALL declare contract test counts |

**Enforcement**: `validate_readme_claims.py` (test count validation)

**Required Format**:
```markdown
| **Contract Tests** | {N} required, {M} recommended |
```

---

### R-TPL-001-05: Version Consistency

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-05 | ubiquitous | Template_README version SHALL match manifest.yaml template.version |

**Enforcement**: `validate_readme_claims.py` (version match)

**Rationale**: Prevents version drift between manifest and documentation.

---

### R-TPL-001-06: Capability References

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-06 | conditional | IF template has documented capabilities THEN Specification_Section SHALL list key CAP-* IDs |

**Enforcement**: Documentation review

**Minimum Capabilities to List**:
- CAP-001: Wake Protocol
- CAP-009: Wind Down Protocol
- CAP-020: Version Configuration
- At least 1 archetype-specific capability (if applicable)

---

### R-TPL-001-07: Spec Update Propagation

| ID | Pattern | Statement |
|----|---------|-----------|
| R-TPL-001-07 | event-driven | WHEN governing spec is updated, Template_README Specification_Section SHALL be updated |

**Enforcement**: Release checklist

**Rationale**: README must remain consistent with spec changes.

---

## Spec Badge Template

Templates SHALL use this structure for the Specification section:

```markdown
## Specification

| Attribute | Value |
|-----------|-------|
| **Governed By** | [AGET_TEMPLATE_SPEC v3.1](https://github.com/aget-framework/aget/blob/main/specs/AGET_TEMPLATE_SPEC.md) |
| **Foundation** | [WORKER_TEMPLATE_SPEC v1.0](https://github.com/aget-framework/aget/blob/main/specs/WORKER_TEMPLATE_SPEC_v1.0.yaml) |
| **Archetype** | {Worker|Advisor|Supervisor|Developer|Consultant|Spec_Engineer} |
| **Manifest Version** | 3.0 |
| **Contract Tests** | {N} required, {M} recommended |

### Key Capabilities

| ID | Capability | Pattern |
|----|------------|---------|
| CAP-001 | Wake Protocol | event-driven |
| CAP-009 | Wind Down Protocol | event-driven |
| CAP-020 | Version Configuration | ubiquitous |
| CAP-028 | Project Plan Pattern | event-driven |
| {archetype-specific} | {description} | {pattern} |

Validate compliance: `pytest tests/ -v`

See: [Full specification](https://github.com/aget-framework/aget/tree/main/specs)
```

---

## Authority Model

```yaml
authority:
  applies_to: "template_readmes"

  governed_by:
    spec: "R-TPL-001"
    owner: "aget-framework"

  enforcement:
    automated: "validate_readme_claims.py"
    manual: "Release checklist review"

  exceptions:
    - "Private templates may omit public links"
    - "Draft templates may have incomplete sections"
```

---

## Inviolables

```yaml
inviolables:
  - id: "INV-TPL-DOC-001"
    source: "R-TPL-001"
    statement: "Template_README SHALL NOT claim capabilities not in governing spec"
    rationale: "Documentation must be accurate"

  - id: "INV-TPL-DOC-002"
    source: "R-TPL-001"
    statement: "Template_README SHALL NOT omit Specification_Section in public releases"
    rationale: "Spec traceability is mandatory for public templates"
```

---

## Validation

```bash
# Validate single template README
python3 validation/validate_readme_claims.py /path/to/template-worker-aget

# Validate all templates
python3 validation/validate_readme_claims.py --all

# Expected output:
# ✅ Specification section exists
# ✅ Version matches manifest (3.0.0)
# ✅ Archetype matches manifest (Worker)
# ✅ Governed By link valid (200 OK)
# ✅ Contract test count accurate (7 required, 5 recommended)
# PASSED: template-worker-aget
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Documentation as Contract"
  secondary:
    - "Traceability (requirements engineering)"
    - "Single Source of Truth principle"
    - "Design by Contract (Meyer)"
  rationale: >
    Public documentation creates an implicit contract with users.
    R-TPL-001 ensures this contract is backed by formal specifications,
    enabling verification and maintaining consistency. The Spec Badge
    Pattern provides explicit traceability from user-facing docs to
    internal governance.
  references:
    - "L409_spec_readme_traceability_pattern.md"
    - "R-PUB-001 (analogous homepage requirements)"
```

---

## Graduation History

```yaml
graduation:
  source_analysis: "2025-12-29 gap analysis (internal specs vs public docs)"
  source_patterns:
    - "R-PUB-001 homepage requirements"
    - "L407 pain-point framing"
    - "L408 5D framework"
  trigger: "User question: how to formalize template specifications"
  rationale: "No spec governed template README requirements"
```

---

## References

- AGET_TEMPLATE_SPEC.md - Primary template architecture spec
- WORKER_TEMPLATE_SPEC_v1.0.yaml - Foundation capabilities
- R-PUB-001 - Public release completeness (homepage)
- AGET_SPEC_FORMAT_v1.2 - Specification format standard
- L409 - Spec-README Traceability Pattern

---

*R-TPL-001: Template Documentation Requirements v1.0.0*
*"Internal rigor deserves external visibility"*
*Created: 2025-12-29 | Format: AGET_SPEC_FORMAT v1.2*
