# AGET Issue Governance Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Process (Issue Management)
**Format Version**: 1.3
**Created**: 2026-01-11
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_ISSUE_GOVERNANCE_SPEC.md`
**Change Origin**: PROJECT_PLAN_issue_governance_v1.0
**Related Specs**: AGET_RELEASE_SPEC, AGET_TEMPLATE_SPEC, AGET_ORGANIZATION_SPEC

---

## Abstract

This specification defines issue management governance for the AGET framework, including issue destination routing based on agent type, content sanitization requirements, and repository issue settings. It establishes controls to prevent private information leakage when filing issues from private fleet agents to public repositories.

## Motivation

Issue governance challenges observed in practice:

1. **Private info exposure**: Private agent filed issue containing internal agent names to public-facing repo
2. **Issue fragmentation**: Issues scattered across template repos instead of central tracker
3. **No destination governance**: No spec defining where issues should go based on agent type
4. **Repo settings drift**: Template repos had issues enabled by default

Evidence: Issue #4 in `aget-framework/template-supervisor-aget` contained private agent names (`vp_of_ai-aget`, `private-work-supervisor-AGET`), fleet size, and internal incident details.

## Scope

**Applies to**: All agents filing issues to aget-framework repositories.

**Defines**:
- Issue destination matrix (agent type → repository)
- Content sanitization requirements
- Repository issue settings requirements
- Validation and enforcement mechanisms

**Does not cover**:
- Issue triage and labeling (future spec)
- Pull request governance (see future PR_GOVERNANCE_SPEC)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "issue_governance"
    version: "1.0.0"
    inherits: "aget_core"

  routing:
    Issue_Destination:
      skos:prefLabel: "Issue_Destination"
      skos:definition: "Target repository for issue filing based on agent type"
      skos:narrower:
        - Private_Issue_Destination
        - Public_Issue_Destination
      aget:governed_by: "AGET_ISSUE_GOVERNANCE_SPEC"

    Private_Issue_Destination:
      skos:prefLabel: "Private_Issue_Destination"
      skos:definition: "Issue destination for private fleet agents"
      aget:value: "gmelli/aget-aget"
      skos:related: ["Private_Fleet_Agent", "R-ISSUE-001"]

    Public_Issue_Destination:
      skos:prefLabel: "Public_Issue_Destination"
      skos:definition: "Issue destination for public/remote agents"
      aget:value: "aget-framework/aget"
      skos:related: ["Public_Remote_Agent", "R-ISSUE-002"]

  agents:
    Private_Fleet_Agent:
      skos:prefLabel: "Private_Fleet_Agent"
      skos:definition: "Agent in gmelli's private fleet, may reference private details"
      aget:detection: ["path contains gmelli", "version.json has fleet:private"]
      skos:related: ["R-ISSUE-001", "R-ISSUE-003", "R-ISSUE-004"]

    Public_Remote_Agent:
      skos:prefLabel: "Public_Remote_Agent"
      skos:definition: "Agent not in private fleet, content must be sanitized for public"
      aget:detection: ["not Private_Fleet_Agent"]
      skos:related: ["R-ISSUE-002"]

  sanitization:
    Issue_Sanitization:
      skos:prefLabel: "Issue_Sanitization"
      skos:definition: "Process of removing private information from issue content before public filing"
      skos:related: ["R-ISSUE-003", "R-ISSUE-004", "Private_Pattern"]

    Private_Pattern:
      skos:prefLabel: "Private_Pattern"
      skos:definition: "Content pattern indicating private/internal information"
      skos:example: ["private-*-aget", "gmelli/*", "fleet size", "SESSION_*"]
      aget:detection_script: "sanitize_issue_content.py"

  anti_patterns:
    Cross_Boundary_Filing:
      skos:definition: "Private agent filing to public repo without sanitization"
      aget:anti_pattern: true
      aget:severity: "high"
      skos:related: ["R-ISSUE-001", "R-ISSUE-005"]

    Issue_Fragmentation:
      skos:definition: "Issues scattered across template repos instead of central tracker"
      aget:anti_pattern: true
      skos:related: ["R-ISSUE-007", "R-ISSUE-009"]
```

---

## Requirements

### CAP-ISSUE-001: Issue Destination Routing

**Statement**: The SYSTEM shall route issues to appropriate destination based on agent type.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-001 | conditional | IF Agent_Type is Private_Fleet_Agent THEN the SYSTEM shall file issues to `gmelli/aget-aget` |
| R-ISSUE-002 | conditional | IF Agent_Type is Public_Remote_Agent THEN the SYSTEM shall file issues to `aget-framework/aget` |

**Enforcement**: `validate_issue_destination.py`

---

### CAP-ISSUE-002: Content Sanitization

**Statement**: The SYSTEM shall prevent private information in public issue filings.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-003 | event-driven | WHEN filing to Public_Issue_Destination, the SYSTEM shall NOT include private agent names |
| R-ISSUE-004 | event-driven | WHEN filing to Public_Issue_Destination, the SYSTEM shall NOT include internal project details |

**Private Patterns to Detect**:
```python
PRIVATE_PATTERNS = [
    r'private-\w+-aget',           # Private agent names
    r'private-\w+-AGET',           # Private agent names (caps)
    r'gmelli/\w+',                 # Private repo references
    r'\d+ agents? (in|across) fleet', # Fleet size disclosure
    r'SESSION_\d{4}-\d{2}-\d{2}',  # Session file references
    r'vp_of_ai-aget',              # Known private agent
    r'law_insider-aget',           # Known private agent
]
```

**Enforcement**: `sanitize_issue_content.py`

---

### CAP-ISSUE-003: Issue Filing Verification

**Statement**: The SYSTEM shall verify destination and content before filing.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-005 | event-driven | WHEN filing issues, the SYSTEM shall verify agent type matches destination |
| R-ISSUE-006 | event-driven | WHEN filing to public destination, the SYSTEM shall validate content for private patterns |

**Enforcement**: `create_issue.py --governance-check`

---

### CAP-ISSUE-004: Repository Issue Settings

**Statement**: The SYSTEM shall maintain appropriate issue settings on repositories.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-007 | ubiquitous | Template repositories SHALL have GitHub issues DISABLED |
| R-ISSUE-008 | ubiquitous | Organization config repositories (.github) SHALL have issues DISABLED |
| R-ISSUE-009 | ubiquitous | Only `aget-framework/aget` SHALL accept public issues |
| R-ISSUE-010 | optional | WHERE GitHub supports organization issue types, the organization MAY define standard issue types |

**Enforcement**: `repo_settings_validator.py --check-issues`

---

## Repository Issue Matrix

| Repository | Issues | Visibility | Rationale |
|------------|--------|------------|-----------|
| `aget-framework/aget` | **enabled** | public | Central public issue tracker |
| `aget-framework/.github` | disabled | public | Org config only |
| `aget-framework/template-*` | disabled | public | Code templates, not issue targets |
| `gmelli/aget-aget` | enabled | private | Private fleet issue tracker |

---

## Agent Type Detection

### Algorithm

```python
def detect_agent_type(agent_root: Path) -> str:
    """Detect whether agent is private fleet or public/remote."""

    # Check 1: Path contains gmelli/gabormelli
    path_str = str(agent_root).lower()
    if 'gmelli' in path_str or 'gabormelli' in path_str:
        return 'private_fleet'

    # Check 2: version.json has fleet marker
    version_json = agent_root / '.aget' / 'version.json'
    if version_json.exists():
        data = json.loads(version_json.read_text())
        if data.get('fleet') == 'private':
            return 'private_fleet'

    # Check 3: Remote URL points to gmelli/*
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True, text=True, cwd=agent_root
        )
        if 'gmelli/' in result.stdout:
            return 'private_fleet'
    except:
        pass

    # Default: public/remote
    return 'public_remote'
```

---

## Validation

### Pre-Filing Validation

```bash
# Check destination before filing
python3 .aget/patterns/github/validate_issue_destination.py --check

# Check content for private patterns
echo "Issue body text" | python3 .aget/patterns/github/sanitize_issue_content.py --check

# File with governance checks (default)
python3 .aget/patterns/github/create_issue.py --title "..." --body "..."
```

### Repository Settings Validation

```bash
# Verify all repos have correct issue settings
python3 .aget/patterns/validation/repo_settings_validator.py --check-issues
```

### Expected Output

```
Issue Governance Check
======================
Agent Type: private_fleet
Correct Destination: gmelli/aget-aget
Content Check: PASS (no private patterns in public filing)
Repository Settings: 14/15 repos have issues disabled (expected)
```

---

## Red Flags

| Anti-Pattern | Detection | Consequence |
|--------------|-----------|-------------|
| Filing from private agent to `aget-framework/*` | Destination validator | Private info exposure |
| Issue body contains `private-*-aget` | Content sanitizer | Private agent name leaked |
| Issue body contains fleet size | Content sanitizer | Internal capacity exposed |
| Template repo has issues enabled | Repo settings validator | Issue fragmentation |

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Information Security (Principle of Least Privilege)"
  secondary:
    - "Defense in Depth"
    - "Separation of Concerns"
  reference: "L520 (Issue Governance Gap)"
```

**Rationale**: Private information should only flow through channels appropriate for its sensitivity level. Public repositories are not appropriate channels for private fleet details.

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L520"]
  pattern_origin: "Issue #4 incident (private info in public-facing repo)"
  rationale: "Formalize issue governance to prevent private information leakage"
  effective_date: "2026-01-11"
```

---

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Specification | Active | This document |
| Destination validator | Pending | `.aget/patterns/github/validate_issue_destination.py` |
| Content sanitizer | Pending | `.aget/patterns/github/sanitize_issue_content.py` |
| Integrated filing script | Pending | `.aget/patterns/github/create_issue.py` |
| Repo settings check | Pending | Add to `repo_settings_validator.py` |

---

## References

- L520: Issue Governance Gap
- PROJECT_PLAN_issue_governance_v1.0.md
- AGET_RELEASE_SPEC (R-REL requirements pattern)
- AGET_TEMPLATE_SPEC (template requirements)
- GitHub Issue Types Documentation
- GitHub Projects Best Practices

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification: routing, sanitization, repo settings |

---

*AGET_ISSUE_GOVERNANCE_SPEC v1.0.0*
*"Route issues by agent type. Sanitize content for public."*
