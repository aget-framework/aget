# AGET Core Vocabulary

**Version**: 1.0.0
**Date**: 2025-12-26
**Source**: AGET_CONTROLLED_VOCABULARY.md (subset)
**Purpose**: Clone-ready vocabulary for AGET templates

---

## Purpose

This document provides the essential vocabulary terms that every AGET agent should understand. It is a subset of the full AGET_CONTROLLED_VOCABULARY.md, designed to be included in templates so vocabulary is available immediately after cloning.

---

## Artifact Types

| Term | Definition |
|------|------------|
| Learning_Document | L-series knowledge capture (e.g., L187) |
| Pattern | Reusable practice extracted from experience |
| Specification | Formal requirements document |
| SOP | Standard Operating Procedure |
| PROJECT_PLAN | Gated execution plan |
| VERSION_SCOPE | Version contents definition |
| Change_Proposal | Formal change request (CP) |
| ADR | Architecture Decision Record |
| Template | Reusable agent archetype |
| Validator | Automated compliance checker |
| Manifest | Agent composition definition (manifest.yaml) |
| Capability | Composable agent behavior module |
| CHANGELOG | Version change record |
| Release_Notes | Detailed version documentation |
| Contract_Test | Automated specification verification |

---

## Lifecycle States

| Term | Definition |
|------|------------|
| DRAFT | In preparation |
| SUBMITTED | Filed for review |
| UNDER_REVIEW | Being evaluated |
| ACCEPTED | Approved for implementation |
| REJECTED | Not approved |
| DEFERRED | Postponed to future |
| SCOPED | Assigned to version |
| IMPLEMENTING | In active development |
| RELEASED | Published |
| CLOSED | Complete |

---

## Process Terms

| Term | Definition |
|------|------------|
| Gate | Decision checkpoint in plan |
| Phase | Workflow stage |
| Decision_Point | Explicit GO/NOGO moment |
| Tier | Gate grouping by trigger |
| Deliverable | Gate output artifact |
| Validation | Compliance checking |
| Migration | Version upgrade process |
| Release | Version publication |
| Rollback | Revert to previous state |
| Escalation | Defer to higher authority |
| Approval | Explicit authorization |
| Checkpoint | Mid-gate verification |
| Intake | Initial receipt processing |
| Scoping | Version assignment |
| Closure | Final completion |

---

## Core Verbs

| Verb | Meaning |
|------|---------|
| READ | Access file contents |
| WRITE | Create or update file |
| CREATE | Make new artifact |
| DELETE | Remove artifact |
| VALIDATE | Check against rules |
| VERIFY | Confirm correctness |
| EXECUTE | Run protocol |
| DISPLAY | Output to user |
| REPORT | Generate formatted output |
| CHECK | Verify condition |
| TRACK | Maintain history |
| APPEND | Add to list |
| BEGIN | Start protocol |
| COMPLETE | Finish protocol |
| WARN | Alert without stopping |
| FAIL | Stop with error |
| PROMPT | Request input |
| REVIEW | Examine for quality |
| APPROVE | Grant authorization |
| ESCALATE | Defer to authority |

---

## Governance Terms

| Term | Definition |
|------|------------|
| Principal | Human operator with ultimate authority |
| Supervisor | Coordinating agent |
| Fleet | Collection of agents |
| Portfolio | Organizational grouping |
| North_Star | Agent purpose statement |
| Charter | Agent scope definition |
| Scope_Boundary | Operational limits |
| Authority_Matrix | Decision rights map |
| Substantial_Change | Change requiring planning |
| Breaking_Change | Change requiring migration |

---

## Usage

### In Specifications

```yaml
# Use Title_Case for domain objects
CAP-001:
  statement: "WHEN Wake_Command is received, the SYSTEM shall execute Wake_Protocol"
```

### In Documentation

Use vocabulary terms consistently:
- ✅ "Create a Learning_Document to capture this insight"
- ❌ "Write a learning doc about this"

---

## Extending Vocabulary

For domain-specific terms, create:
```
governance/vocabulary/DOMAIN_VOCABULARY.md
```

This allows agent-specific vocabulary while preserving core terminology.

---

## Reference

Full vocabulary: `aget/specs/AGET_CONTROLLED_VOCABULARY.md`

---

*AGET_CORE_VOCABULARY.md — Essential vocabulary for AGET agents*
*Clone-ready subset of AGET_CONTROLLED_VOCABULARY.md*
