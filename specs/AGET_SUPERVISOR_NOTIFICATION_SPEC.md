# AGET Supervisor Notification Specification

**Version**: 1.1.0
**Status**: Active
**Category**: Process (Release Communication)
**Format Version**: 1.3
**Created**: 2026-03-05
**Author**: aget-framework
**Location**: `aget/specs/AGET_SUPERVISOR_NOTIFICATION_SPEC.md`
**Change Origin**: PROJECT_PLAN_supervisor_notification_spec_v1.0 (G1)
**Related Specs**: AGET_RELEASE_SPEC (R-REL-019), AGET_ISSUE_GOVERNANCE_SPEC (sanitization model)

---

## Abstract

This specification defines content, structure, and sanitization requirements for supervisor notification artifacts. Notifications bridge release completion and fleet upgrade initiation — they are the trigger that tells a supervisor "a new version is available, here's what you need to know."

## Motivation

Notification challenges observed in practice:

1. **Content drift**: SOP §6.4 specifies 4 content items; actual notifications contain 7+ sections with 85+ lines (L631)
2. **Audience blindness**: Notifications written for internal supervisor contained private agent names, internal file paths, and fleet-specific observations — unusable by remote fleet supervisors (L631)
3. **Sanitization gap**: L520 governs issue sanitization, but notifications had no equivalent — 5 of 6 notifications contained L520 violations (L631 G0.3)
4. **No validation**: Post-release validation checks handoff artifacts but not notifications

Evidence: v3.7.0 notification required manual remediation after principal review revealed it would not serve a remote fleet supervisor.

## Scope

**Applies to**: Release notifications from framework manager to fleet supervisor(s).

**Defines**:
- Required and optional notification sections
- Audience-aware content rules (internal vs external)
- Sanitization requirements (extending L520 model)
- Response tracking structure

**Does not cover**:
- Push-based delivery mechanism (R-REL-019 delivery gap — separate remediation)
- Non-release notifications (incident, deprecation, survey — future scope)
- Handoff artifact content (see R-REL-019 in AGET_RELEASE_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "supervisor_notification"
    version: "1.0.0"
    inherits: "aget_core"

  notification:
    Supervisor_Notification:
      skos:prefLabel: "Supervisor_Notification"
      skos:definition: "Artifact that communicates release availability from framework manager to fleet supervisor"
      skos:narrower:
        - Release_Notification
      aget:governed_by: "AGET_SUPERVISOR_NOTIFICATION_SPEC"
      skos:related: ["Release_Handoff", "R-NOTIFY-001"]

    Release_Notification:
      skos:prefLabel: "Release_Notification"
      skos:definition: "Notification triggered by framework release completion"
      aget:trigger: "Release completion (post R-REL-019 handoff creation)"
      skos:related: ["R-NOTIFY-001", "R-NOTIFY-002"]

  audience:
    Internal_Audience:
      skos:prefLabel: "Internal_Audience"
      skos:definition: "Fleet supervisor with access to private repos and internal context"
      aget:access_level: "private"
      skos:related: ["R-NOTIFY-008"]

    External_Audience:
      skos:prefLabel: "External_Audience"
      skos:definition: "Fleet supervisor without access to private repos — receives only public artifacts"
      aget:access_level: "public"
      skos:related: ["R-NOTIFY-009", "R-NOTIFY-010"]

  anti_patterns:
    Private_Leak_In_Notification:
      skos:definition: "Notification to external audience containing private agent names, paths, or fleet details"
      aget:anti_pattern: true
      aget:severity: "medium"
      skos:related: ["R-NOTIFY-010", "R-ISSUE-003"]
```

---

## Requirements

### CAP-NOTIFY-001: Required Notification Sections

**Statement**: Release notifications SHALL contain a defined set of required sections.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-NOTIFY-001 | ubiquitous | Release notification SHALL contain an Executive Summary with version, theme, and handoff artifact link |
| R-NOTIFY-002 | ubiquitous | Release notification SHALL contain a Release Highlights section with numbered key changes |
| R-NOTIFY-003 | ubiquitous | Release notification SHALL contain a Breaking Changes section (even if "None") |
| R-NOTIFY-004 | ubiquitous | Release notification SHALL contain a Fleet Action Required section with numbered steps, where step 1 is governance setup (create PROJECT_PLAN per local upgrade SOP) |
| R-NOTIFY-005 | ubiquitous | Release notification SHALL contain a Post-Release Quality section with validation results table |
| R-NOTIFY-006 | ubiquitous | Release notification SHALL contain a Traceability section linking to handoff, changelog, release, and upgrade guide |
| R-NOTIFY-007 | ubiquitous | Release notification SHALL contain a Supervisor Response Log with acknowledgment checkboxes |

**V-Test**:
```bash
FILE="handoffs/SUPERVISOR_NOTIFICATION_YYYY-MM-DD.md"
for section in "Executive Summary" "Release Highlights" "Breaking Changes" "Fleet Action Required" "Post-Release Quality" "Traceability" "Supervisor Response Log"; do
  grep -q "## $section" "$FILE" && echo "PASS: $section" || echo "FAIL: $section"
done
```

---

### CAP-NOTIFY-002: Conditional Notification Sections

**Statement**: Release notifications SHALL include additional sections when specific conditions apply.

**Pattern**: conditional

| ID | Pattern | Statement |
|----|---------|-----------|
| R-NOTIFY-008 | conditional | IF upgrade carries risk of data loss or customization overwrite THEN notification SHALL contain an Upgrade Warnings section |
| R-NOTIFY-009 | conditional | IF known non-blocking issues exist THEN notification MAY contain a Known Items section |

**V-Test**:
```bash
# Check for upgrade warnings when skill renames present
if grep -q "rename" "$FILE"; then
  grep -q "## Upgrade Warnings" "$FILE" && echo "PASS" || echo "WARN: renames present but no warnings section"
fi
```

---

### CAP-NOTIFY-003: Audience-Aware Content

**Statement**: Notifications SHALL be written for the broadest intended audience.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-NOTIFY-010 | ubiquitous | Notification From/To fields SHALL use role names ("Framework Manager", "Fleet Supervisor"), not private agent names |
| R-NOTIFY-011 | ubiquitous | Traceability links SHALL use public URLs (https://github.com/aget-framework/...), not local file paths |
| R-NOTIFY-012 | conditional | IF fleet-specific observations are included THEN they SHALL be clearly labeled as "Internal Note" or removed for external variants |

**Rationale**: A single notification should serve both internal and external audiences without requiring a separate sanitized version. This is achieved by writing for the external audience by default.

---

### CAP-NOTIFY-004: Sanitization Requirements

**Statement**: Notifications SHALL NOT contain private information, extending L520 patterns.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-NOTIFY-013 | event-driven | WHEN creating a notification, the author SHALL NOT include private agent names (`private-*-aget`, `private-*-AGET`) |
| R-NOTIFY-014 | event-driven | WHEN creating a notification, the author SHALL NOT include private repository paths (`gmelli/*`, `~/github/private-*`) |
| R-NOTIFY-015 | event-driven | WHEN creating a notification, the author SHALL NOT include fleet size disclosures |
| R-NOTIFY-016 | event-driven | WHEN creating a notification, the author SHALL NOT include internal session references (`SESSION_*`, `session_*`) |

**Private Patterns** (extends L520):
```python
NOTIFICATION_PRIVATE_PATTERNS = [
    r'private-\w+-aget',           # Private agent names (lowercase)
    r'private-\w+-AGET',           # Private agent names (uppercase)
    r'gmelli/\w+',                 # Private repo references
    r'\d+ agents? (in|across) fleet', # Fleet size disclosure
    r'SESSION_\d{4}-\d{2}-\d{2}',  # Session file references
    r'session_\d{4}-\d{2}-\d{2}',  # Session file references (lowercase)
    r'~/github/private-',          # Local private paths
]
```

**V-Test**:
```bash
FILE="handoffs/SUPERVISOR_NOTIFICATION_YYYY-MM-DD.md"
grep -cE "private-\w+-[aA][gG][eE][tT]|gmelli/|~/github/private-" "$FILE" | grep -q "^0$" && echo "PASS" || echo "FAIL: contains private references"
```

---

### CAP-NOTIFY-005: Notification Artifact Naming

**Statement**: Notification artifacts SHALL follow a consistent naming convention.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-NOTIFY-017 | ubiquitous | Release notifications SHALL be named `SUPERVISOR_NOTIFICATION_YYYY-MM-DD.md` using the release date |
| R-NOTIFY-018 | ubiquitous | Release notifications SHALL be stored in `handoffs/` directory |

---

## Notification Section Reference

| Section | Required | Content | Source |
|---------|----------|---------|--------|
| Executive Summary | YES | Version, theme, handoff link | R-NOTIFY-001 |
| Release Highlights | YES | Numbered list of key changes (4-8 items) | R-NOTIFY-002 |
| Breaking Changes | YES | "None" or list with migration | R-NOTIFY-003 |
| Upgrade Warnings | CONDITIONAL | Risk advisories (L629, customization, etc.) | R-NOTIFY-008 |
| Fleet Action Required | YES | Numbered steps for supervisor (step 1 = governance setup) | R-NOTIFY-004 |
| Post-Release Quality | YES | Validation results table | R-NOTIFY-005 |
| Traceability | YES | Public links to handoff, changelog, release | R-NOTIFY-006 |
| Supervisor Response Log | YES | Checkboxes for acknowledgment tracking | R-NOTIFY-007 |
| Known Items | OPTIONAL | Non-blocking issues | R-NOTIFY-009 |

---

## Relationship to Other Artifacts

```
Release Complete
       │
       ├─→ RELEASE_HANDOFF_vX.Y.Z.md  (governed by R-REL-019)
       │     └─ Detailed upgrade guide, text replacements, V-tests
       │
       └─→ SUPERVISOR_NOTIFICATION_YYYY-MM-DD.md  (governed by this spec)
             └─ Summary trigger: "what changed, what to do, how it went"
```

**Distinction**: The handoff is the *how* (detailed upgrade guide). The notification is the *what* and *why* (summary trigger + quality evidence).

---

## Enforcement

### Current State

| Mechanism | Status |
|-----------|--------|
| Spec (this document) | v1.0.0 |
| SOP_release_process.md §6.4 | To be updated (G2) |
| Template | To be created (G2) |
| Automated validation | Not yet (future CAP) |

### Maturity Path (ADR-008)

| Stage | Status | Artifact |
|-------|--------|----------|
| Advisory | Active | This spec |
| Strict | Future | post_release_validation.py check |
| Generator | Future | Template-based notification generation |

---

## Changelog

### v1.1.0 (2026-03-05)

- R-NOTIFY-004 strengthened: step 1 must be governance setup, not content review (L632)
- Design principle added: "embed governance at the point of action, not in a separate preamble"

### v1.0.0 (2026-03-05)

- Initial specification (L631)
- 18 EARS requirements across 5 CAP groups
- Sanitization requirements extending L520 model
- Audience-aware content rules (R-NOTIFY-010 through R-NOTIFY-012)
- Section reference table (7 required, 1 conditional, 1 optional)

---

*AGET_SUPERVISOR_NOTIFICATION_SPEC v1.0.0*
