# AGET Skills Index

**Version**: 1.2.0
**Updated**: 2026-02-14
**Total Skills**: 40 (14 universal + 26 archetype)
**Project**: ARC-001 (Archetype Customization v3.5)

---

## Universal Skills (14)

Deployed to all 12 templates.

| ID | Name | Category | Description |
|----|------|----------|-------------|
| SKILL-001 | aget-wake-up | Session | Initialize AGET session with status briefing |
| SKILL-002 | aget-wind-down | Session | End AGET session with state capture |
| SKILL-003 | aget-sanity-check | Health | Run AGET health inspection |
| SKILL-004 | aget-healthcheck-evolution | Health | Check evolution directory health |
| SKILL-005 | aget-healthcheck-sessions | Health | Check sessions directory health |
| SKILL-006 | aget-healthcheck-kb | Health | Validate Knowledge Base health |
| SKILL-007 | aget-record-lesson | Evolution | Record lessons learned as L-docs |
| SKILL-008 | aget-capture-observation | Evolution | Capture research observations |
| SKILL-009 | aget-propose-skill | Governance | Propose new skills with governance |
| SKILL-010 | aget-review-project | Project | Mid-flight review of project plans |
| SKILL-011 | aget-create-project | Project | Create research projects with scaffolding |
| SKILL-012 | aget-create-skill | Development | Create new skill with spec |
| SKILL-013 | aget-save-state | Session | Save workflow state for recovery |
| SKILL-040 | aget-file-issue | Governance | File issues with L520 governance compliance |

---

## Archetype Skills (26)

Deployed to specific archetypes only.

### Advisor (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-014 | aget-assess-risk | CAP-ADV-001 | Assess risks with likelihood, impact, mitigation |
| SKILL-015 | aget-recommend-action | CAP-ADV-002 | Provide recommendations with rationale |

### Analyst (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-016 | aget-analyze-data | CAP-ANL-001 | Perform analysis to discover patterns and insights |
| SKILL-017 | aget-generate-report | CAP-ANL-002 | Generate reports with metrics and findings |

### Architect (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-018 | aget-design-architecture | CAP-ARC-001 | Design system architecture with patterns |
| SKILL-019 | aget-assess-tradeoffs | CAP-ARC-002 | Analyze trade-offs between concerns |

### Consultant (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-020 | aget-assess-client | CAP-CON-001 | Assess client needs and constraints |
| SKILL-021 | aget-propose-engagement | CAP-CON-002 | Create engagement proposals |

### Developer (3 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-022 | aget-run-tests | CAP-DEV-001 | Execute test suite and report results |
| SKILL-023 | aget-lint-code | CAP-DEV-002 | Run code linting and formatting checks |
| SKILL-024 | aget-review-pr | CAP-DEV-003 | Review pull requests for quality |

### Executive (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-025 | aget-make-decision | CAP-EXE-001 | Make decisions with documented rationale |
| SKILL-026 | aget-review-budget | CAP-EXE-002 | Review budget allocation and ROI |

### Operator (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-027 | aget-handle-incident | CAP-OPS-001 | Handle incidents with diagnosis and mitigation |
| SKILL-028 | aget-run-playbook | CAP-OPS-002 | Execute runbooks for operations |

### Researcher (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-029 | aget-search-literature | CAP-RES-001 | Search and review literature |
| SKILL-030 | aget-document-finding | CAP-RES-002 | Document research findings with evidence |

### Reviewer (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-031 | aget-review-artifact | CAP-REV-001 | Review artifacts against criteria |
| SKILL-032 | aget-provide-feedback | CAP-REV-002 | Provide structured feedback |

### Spec-Engineer (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-033 | aget-validate-spec | CAP-SPE-001 | Validate specifications for completeness |
| SKILL-034 | aget-generate-requirement | CAP-SPE-002 | Generate EARS-compliant requirements |

### Supervisor (3 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-035 | aget-broadcast-fleet | CAP-SUP-001 | Send communications to fleet members |
| SKILL-036 | aget-review-agent | CAP-SUP-002 | Review agent health and conformance |
| SKILL-037 | aget-escalate-issue | CAP-SUP-003 | Escalate issues to higher authority |

### Worker (2 skills)

| ID | Name | Capability | Description |
|----|------|------------|-------------|
| SKILL-038 | aget-execute-task | CAP-WRK-001 | Execute tasks with progress tracking |
| SKILL-039 | aget-report-progress | CAP-WRK-002 | Report progress on current work |

---

## Skill Distribution by Archetype

| Archetype | Universal | Archetype-Specific | Total |
|-----------|:---------:|:------------------:|:-----:|
| advisor | 13 | 2 | 15 |
| analyst | 13 | 2 | 15 |
| architect | 13 | 2 | 15 |
| consultant | 13 | 2 | 15 |
| developer | 13 | 3 | 16 |
| executive | 13 | 2 | 15 |
| operator | 13 | 2 | 15 |
| researcher | 13 | 2 | 15 |
| reviewer | 13 | 2 | 15 |
| spec-engineer | 13 | 2 | 15 |
| supervisor | 13 | 3 | 16 |
| worker | 13 | 2 | 15 |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| SKILL_VOCABULARY.md | Skill terminology definitions |
| ARCHETYPE_SKILLS_INDEX.yaml | Archetype skills registry (aget/specs/) |
| AGET_SKILLS_SPEC.md | Skills specification (aget/specs/) |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-10 | Initial index with 13 universal skills |
| 1.1.0 | 2026-02-14 | Added 26 archetype skills (ARC-001) |

---

*INDEX.md - AGET Skills Index*
*Last Updated: 2026-02-14*
