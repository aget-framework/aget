# Verification Inventory

**Owner**: private-aget-framework-AGET
**Updated**: 2026-02-15
**Reference**: L377 (Validation Suite Orchestration Gap)

---

## Purpose

This inventory lists all verification scripts in `aget/verification/` with their purpose, scope, and when to run them.

**Note**: As of v3.5.0, `validation/` was renamed to `verification/` for naming consistency. Both directories exist during transition; `validation/` will be removed in v3.6.0.

**Ownership Model** (per L377):
| Artifact | Owner |
|----------|-------|
| Individual validators | Framework-aget |
| Validation inventory | Framework-aget |
| Orchestration (run-all) | Supervisor |
| Pre-migration audit | Supervisor |

---

## Validator Categories

### Migration Validators (Pre/Post Migration)

| Validator | Purpose | When to Run | CAP Reference |
|-----------|---------|-------------|---------------|
| `validate_template_instance.py` | Structural v3.0 compliance (24 checks) | Post-migration | CAP-INST-002 |
| `validate_version_consistency.py` | version.json ↔ AGENTS.md sync | Post-migration | CAP-MIG-010 |
| `validate_naming_conventions.py` | File/directory naming compliance | Pre/Post-migration | — |
| `validate_5d_compliance.py` | 5D directory structure | Post-migration | CAP-COMP-001 |

### Specification Validators

| Validator | Purpose | When to Run | CAP Reference |
|-----------|---------|-------------|---------------|
| `validate_capability_spec.py` | Capability spec format | Spec creation | — |
| `validate_spec_format.py` | Spec format v1.2 compliance | Spec creation | — |
| `validate_process_spec.py` | Process spec format | Spec creation | — |
| `validate_change_proposal.py` | Change proposal format | Proposal creation | — |
| `validate_project_plan.py` | PROJECT_PLAN format | Plan creation | — |
| `validate_learning_doc.py` | L-doc format | L-doc creation | — |

### Composition Validators

| Validator | Purpose | When to Run | CAP Reference |
|-----------|---------|-------------|---------------|
| `validate_composition.py` | Composition architecture | Composition changes | CAP-COMP-* |
| `validate_composition_refs.py` | Cross-composition references | Composition changes | — |
| `validate_persona_compliance.py` | Persona config (D1) | Instance creation | CAP-COMP-001 |
| `validate_memory_compliance.py` | Memory config (D2) | Instance creation | CAP-COMP-002 |
| `validate_context_compliance.py` | Context config (D5) | Instance creation | CAP-COMP-005 |

### Knowledge Validators

| Validator | Purpose | When to Run | CAP Reference |
|-----------|---------|-------------|---------------|
| `validate_vocabulary.py` | SKOS vocabulary format | Vocabulary changes | — |
| `check_aget_vocabulary.py` | AGET vocabulary compliance | Any change | — |
| `analyze_knowledge_content.py` | Knowledge base analysis | Periodic audit | — |
| `validate_graduation_history.py` | Knowledge graduation tracking | Knowledge changes | — |

### Template Validators

| Validator | Purpose | When to Run | CAP Reference |
|-----------|---------|-------------|---------------|
| `validate_template_manifest.py` | Template manifest format | Template changes | — |
| `validate_cross_references.py` | Cross-reference integrity | Any change | — |
| `validate_script_registry.py` | Script registry format | Script changes | — |

### Utility Scripts (Not Validators)

| Script | Purpose |
|--------|---------|
| `project_skos_to_ears.py` | SKOS to EARS conversion |

---

## Migration Checklist

### Pre-Migration (Supervisor runs)

```bash
# Run on agent BEFORE migration
python3 validate_naming_conventions.py /path/to/agent
python3 validate_version_consistency.py /path/to/agent
```

### Post-Migration (Supervisor runs)

```bash
# Run on agent AFTER migration
python3 validate_template_instance.py /path/to/agent  # 24 checks
python3 validate_version_consistency.py /path/to/agent
python3 validate_5d_compliance.py /path/to/agent
python3 validate_naming_conventions.py /path/to/agent
```

### Contract Tests (Supervisor runs)

```bash
# Run after structural validation
cd /path/to/agent
python3 -m pytest tests/test_identity_contract.py -v
```

---

## Known Issues

| Validator | Issue | Status | Reference |
|-----------|-------|--------|-----------|
| `validate_version_consistency.py` | Regex didn't capture pre-release versions | ✅ FIXED 2025-12-28 | L377 |

---

## Adding New Validators

1. Create `validate_<name>.py` in `aget/validation/`
2. Add to this inventory with purpose and when to run
3. If migration-related, add CAP reference
4. Update supervisor's orchestration script

---

*Inventory created: 2025-12-28*
*Reference: L377 (Validation Suite Orchestration Gap)*
*Owner: private-aget-framework-AGET*
