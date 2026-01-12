# Validator Inventory

**Version**: 1.0.0
**Status**: Active
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Source**: L433 (Validator Enforcement Theater Gap)

---

## Purpose

This document tracks all validators referenced in AGET specifications, their implementation status, and enforcement accuracy. Per L433, specs must not reference non-existent validators without proper marking.

---

## Summary

| Category | Count |
|----------|-------|
| **Implemented** | 32 |
| **Planned** | 15 |
| **Deferred** | 2 |
| **Total Referenced** | 46 |
| **Theater Ratio** | 33% → target <10% by removing spec refs |

---

## Implemented Validators

These validators exist in `validation/` and are functional:

| Validator | Spec Reference | Status |
|-----------|----------------|--------|
| validate_5d_compliance.py | AGET_5D_ARCHITECTURE_SPEC | ✅ Implemented |
| validate_capability_spec.py | AGET_SKILLS_SPEC | ✅ Implemented |
| validate_change_proposal.py | AGET_CHANGE_PROPOSAL_SPEC | ✅ Implemented |
| validate_composition_refs.py | AGET_TEMPLATE_SPEC | ✅ Implemented |
| validate_composition.py | AGET_SKILLS_SPEC | ✅ Implemented |
| validate_context_compliance.py | AGET_CONTEXT_SPEC | ✅ Implemented |
| validate_cross_references.py | Internal | ✅ Implemented |
| validate_graduation_history.py | AGET_MEMORY_SPEC | ✅ Implemented |
| validate_learning_doc.py | AGET_MEMORY_SPEC | ✅ Implemented |
| validate_memory_compliance.py | AGET_MEMORY_SPEC | ✅ Implemented |
| validate_naming_conventions.py | AGET_SOP_SPEC | ✅ Implemented |
| validate_persona_compliance.py | AGET_PERSONA_SPEC | ✅ Implemented |
| validate_process_spec.py | AGET_FRAMEWORK_SPEC | ✅ Implemented |
| validate_project_plan.py | AGET_REASONING_SPEC | ✅ Implemented |
| validate_readme_claims.py | R-TPL-001 | ✅ Implemented |
| validate_script_registry.py | AGET_PYTHON_SCRIPT_SPEC | ✅ Implemented |
| validate_spec_format.py | AGET_VALIDATION_SPEC | ✅ Implemented |
| validate_template_instance.py | AGET_INSTANCE_SPEC | ✅ Implemented |
| validate_template_manifest.py | AGET_TEMPLATE_SPEC | ✅ Implemented |
| validate_version_consistency.py | AGET_FRAMEWORK_SPEC | ✅ Implemented |
| validate_vocabulary.py | AGET_GLOSSARY_STANDARD_SPEC | ✅ Implemented |
| validate_file_naming.py | AGET_FILE_NAMING_CONVENTIONS | ✅ Implemented (v3.2.0) |
| validate_spec_header.py | AGET_SPEC_FORMAT | ✅ Implemented (v3.2.0) |
| validate_spec_cross_refs.py | Internal | ✅ Implemented (v3.2.0) |
| validate_license_compliance.py | AGET_LICENSE_SPEC | ✅ Implemented (v3.2.0) |
| validate_agent_structure.py | AGET_TEMPLATE_SPEC | ✅ Implemented (v3.2.0) |
| validate_release_gate.py | AGET_RELEASE_SPEC (L440) | ✅ Implemented (v3.2.0) |
| validate_ldoc_index.py | AGET_MEMORY_SPEC | ✅ Implemented (v3.2.0) |
| validate_sop_compliance.py | AGET_SOP_SPEC | ✅ Implemented (v3.2.0) |
| validate_homepage_messaging.py | AGET_ORGANIZATION_SPEC | ✅ Implemented (v3.2.0) |
| analyze_knowledge_content.py | Internal | ✅ Implemented |
| check_aget_vocabulary.py | Internal | ✅ Implemented |
| project_skos_to_ears.py | Internal | ✅ Implemented |
| validate_artifact_size.py | AGET_SPEC_FORMAT, CAP-PP-012 (L502) | ✅ Implemented (v3.3.0) |
| validate_template_exemplar.py | CAP-TPL-014, SOP_template_validation | ✅ Implemented (v3.3.0) |

---

## Planned Validators

These validators are referenced in specs but not yet implemented. Specs should be updated to mark them as "(planned)":

| Validator | Spec Reference | Priority | Status |
|-----------|----------------|----------|--------|
| validate_portability_compliance.py | AGET_PORTABILITY_SPEC | P2 | Planned |
| validate_compatibility.py | AGET_COMPATIBILITY_SPEC | P2 | Planned |
| validate_script_compliance.py | AGET_PYTHON_SCRIPT_SPEC | P2 | Planned |
| validate_governance_traceability.py | AGET_GOVERNANCE_SPEC | P2 | Planned |
| validate_tool_alignment.py | AGET_TOOL_SPEC | P3 | Planned |
| validate_agents_md_size.py | AGET_MIGRATION_SPEC | P3 | Planned |
| validate_cli_settings.py | AGET_DOCUMENTATION_SPEC | P2 | Planned |
| validate_public_content.py | AGET_SECURITY_SPEC | P2 | Planned |
| validate_contract_tests.py | AGET_TESTING_SPEC | P2 | Planned |
| validate_test_naming.py | AGET_TESTING_SPEC | P3 | Planned |
| validate_changelog.py | AGET_RELEASE_SPEC | P2 | Planned |
| validate_fleet.py | AGET_RELEASE_SPEC | P3 | Planned |
| validate_artifact.py | Internal | P3 | Planned |
| validate_readme.py | Internal | P3 | Planned |
| validate_naming.py | Internal | P3 | Planned |

---

## Deferred Validators

These validators are referenced but explicitly deferred (with documented rationale):

| Validator | Spec Reference | Reason |
|-----------|----------------|--------|
| validate_supervisor_fleet_state.py | AGET_MIGRATION_SPEC | Advanced feature, fleet not yet scaled |
| validate_vocabulary_specificity.py | AGET_SOP_SPEC | Future enhancement, low priority |

---

## Spec Update Requirements

Per R-SPEC-010, specs referencing non-existent validators must be updated:

### Priority 1: High-Traffic Specs

| Spec | Validators to Mark | Action |
|------|-------------------|--------|
| AGET_LICENSE_SPEC | validate_license_compliance.py | Add "(planned)" |
| AGET_SOP_SPEC | validate_sop_compliance.py | Add "(planned)" |
| R-HOM-001 | validate_homepage_messaging.py | Add "(planned)" |

### Priority 2: Other Specs

All specs with "Enforcement:" sections referencing missing validators should be updated to use:
- `validator.py (planned)` - if validator will be created
- `Manual review per SOP_X` - if no automation planned

---

## Validation Command

Run this to check current theater ratio:

```bash
cd /Users/gabormelli/github/aget-framework/aget

# Count implemented
implemented=$(ls validation/validate_*.py 2>/dev/null | wc -l)

# Count referenced
referenced=$(grep -rh "validate_.*\.py" specs/ | grep -oE "validate_[a-z_]+\.py" | sort -u | wc -l)

# Calculate theater ratio
missing=$((referenced - implemented))
ratio=$((missing * 100 / referenced))

echo "Implemented: $implemented"
echo "Referenced: $referenced"
echo "Missing: $missing"
echo "Theater Ratio: ${ratio}%"
```

---

## Remediation Roadmap

### v3.2.0 Target (Issue #36)
**Theme**: Specification Architecture
**Goal**: Theater ratio < 10%

- [ ] validate_license_compliance.py (P0)
- [ ] validate_agent_structure.py (P1)
- [ ] validate_homepage_messaging.py (P1)
- [ ] validate_sop_compliance.py (P1)
- [ ] validate_spec_header.py (new, P1)
- [ ] validate_release_gate.py (new, P1) — L440 remediation
- [ ] Update all specs to mark "(planned)" accurately
- [ ] Add 7 new specs (TESTING, RELEASE, DOCUMENTATION, ORGANIZATION, ERROR, SECURITY, PROJECT_PLAN)

**V-Test (Gate 6.12)**:
```bash
# Theater ratio < 10%
missing=$(grep -rh "validate_.*\.py" specs/ | grep -oE "validate_[a-z_]+\.py" | sort -u | \
  while read v; do [ ! -f "validation/$v" ] && echo "$v"; done | wc -l)
total=$(grep -rh "validate_.*\.py" specs/ | grep -oE "validate_[a-z_]+\.py" | sort -u | wc -l)
ratio=$((missing * 100 / total))
[ $ratio -lt 10 ] && echo "PASS: ${ratio}%" || echo "FAIL: ${ratio}%"
```

### v3.3.0 Target
**Theme**: Fleet Communication Patterns

- [ ] validate_file_naming.py (P2)
- [ ] validate_portability_compliance.py (P2)
- [ ] validate_compatibility.py (P2)
- [ ] Theater ratio maintained < 10%

### v3.4.0 Target
- [ ] Remaining P2/P3 validators
- [ ] Full validator coverage for all specs

---

## References

- L433: Validator Enforcement Theater Gap
- R-SPEC-010: Validator Existence Gate
- ADR-007: No Test Theater
- SOP_release_process.md (Gate 9)
- RELEASE_VERIFICATION_CHECKLIST.md (Gate 9)

---

*VALIDATOR_INVENTORY.md - Enforcement accuracy tracking*
*"A spec that claims enforcement without implementation is governance theater."*
