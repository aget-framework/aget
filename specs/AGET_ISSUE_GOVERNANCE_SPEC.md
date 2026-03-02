# AGET Issue Governance Specification

**Version**: 2.0.0
**Status**: Active
**Category**: Process (Issue Management)
**Format Version**: 1.3
**Created**: 2026-01-11
**Author**: aget-framework
**Location**: `aget/specs/AGET_ISSUE_GOVERNANCE_SPEC.md`
**Change Origin**: PROJECT_PLAN_issue_governance_v1.0, PROJECT_PLAN_issue_content_sanitization_v1.0, PROJECT_PLAN_public_issue_migration_v1.0
**Related Specs**: AGET_RELEASE_SPEC, AGET_TEMPLATE_SPEC, AGET_ORGANIZATION_SPEC, AGET_VOCABULARY_SPEC

---

## Abstract

This specification defines issue management governance for the AGET framework. All issues are filed to the private tracker (`gmelli/aget-aget`) by default. Public issues on `aget-framework/aget` are created only via explicit promotion with principal approval. This private-first routing eliminates the need for content sanitization at filing time — sanitization applies only at the promotion boundary.

## Motivation

Issue governance challenges observed in practice:

1. **Private info exposure**: Private agent filed issue containing internal agent names to public-facing repo (Issue #4 in `aget-framework/template-supervisor-aget`)
2. **Issue fragmentation**: Issues scattered across template repos instead of central tracker
3. **Pattern-based sanitization structurally insufficient**: Three rounds of remediation (L520, L583, L638) demonstrated that content diversity exceeds pattern coverage — 19 of 50 public issues (38%) still contained private information after two prior remediations
4. **Repo settings drift**: Template repos had issues enabled by default

**Root cause** (L638 5-Whys): The original architecture placed private content in a public context, then attempted to filter it. Filter-then-publish fails when content diversity is open-ended. Private-first routing is the structural fix.

## Scope

**Applies to**: All agents filing issues related to the AGET framework.

**Defines**:
- Issue routing policy (private-first, promotion-based)
- Issue promotion requirements
- Content sanitization requirements (at promotion boundary only)
- Repository issue settings requirements
- Validation and enforcement mechanisms

**Does not cover**:
- Issue triage and labeling (future spec)
- Pull request governance (see future PR_GOVERNANCE_SPEC)
- Promotion workflow tooling (spec defines requirements; tooling deferred)

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "issue_governance"
    version: "2.0.0"
    inherits: "aget_core"

  routing:
    Issue_Destination:
      skos:prefLabel: "Issue_Destination"
      skos:definition: "Target repository for issue filing"
      skos:narrower:
        - Private_Issue_Destination
        - Public_Issue_Destination
      aget:governed_by: "AGET_ISSUE_GOVERNANCE_SPEC"

    Private_Issue_Destination:
      skos:prefLabel: "Private_Issue_Destination"
      skos:definition: "Default issue destination for all agents"
      aget:value: "gmelli/aget-aget"
      skos:related: ["R-ISSUE-001"]

    Public_Issue_Destination:
      skos:prefLabel: "Public_Issue_Destination"
      skos:definition: "Promotion-only destination for principal-approved public issues"
      aget:value: "aget-framework/aget"
      skos:related: ["R-ISSUE-002", "R-ISSUE-011", "R-ISSUE-012", "R-ISSUE-013", "R-ISSUE-014"]

  promotion:
    Issue_Promotion:
      skos:prefLabel: "Issue_Promotion"
      skos:definition: "Explicit, reviewable action to publish a private issue to the public tracker"
      skos:related: ["R-ISSUE-011", "R-ISSUE-012", "R-ISSUE-013", "R-ISSUE-014"]

  agents:
    Private_Fleet_Agent:
      skos:prefLabel: "Private_Fleet_Agent"
      skos:definition: "Agent in gmelli's private fleet, may reference private details"
      aget:detection: ["path contains gmelli", "version.json has fleet:private"]
      skos:related: ["R-ISSUE-001"]

    Public_Remote_Agent:
      skos:prefLabel: "Public_Remote_Agent"
      skos:definition: "Agent not in private fleet"
      aget:detection: ["not Private_Fleet_Agent"]
      skos:related: ["R-ISSUE-001"]
      skos:note: "Under private-first routing, Public_Remote_Agent files to the same destination as Private_Fleet_Agent"

  sanitization:
    Issue_Sanitization:
      skos:prefLabel: "Issue_Sanitization"
      skos:definition: "Process of removing private information from issue content before promotion to public"
      skos:related: ["R-ISSUE-003", "R-ISSUE-004", "R-ISSUE-012", "R-ISSUE-014", "Private_Pattern"]
      skos:note: "Applies only at the promotion boundary, not at filing time"

    Private_Pattern:
      skos:prefLabel: "Private_Pattern"
      skos:definition: "Content pattern indicating private/internal information"
      skos:example: ["private-*-aget", "gmelli/*", "fleet size", "SESSION_*"]
      aget:detection_script: "sanitize_issue_content.py"

  anti_patterns:
    Cross_Boundary_Filing:
      skos:definition: "Any agent filing directly to public repo without promotion"
      aget:anti_pattern: true
      aget:severity: "high"
      skos:related: ["R-ISSUE-001", "R-ISSUE-002"]

    Issue_Fragmentation:
      skos:definition: "Issues scattered across template repos instead of central tracker"
      aget:anti_pattern: true
      skos:related: ["R-ISSUE-007", "R-ISSUE-009"]

    Exhaustive_Pattern_List:
      skos:definition: "Attempting to enumerate all private content patterns for sanitization at filing time"
      aget:anti_pattern: true
      aget:severity: "medium"
      skos:related: ["L520", "L583", "L638"]
      skos:note: "Content diversity exceeds pattern coverage. Private-first routing is the structural fix."
```

---

## Requirements

### CAP-ISSUE-001: Issue Destination Routing (Private-First)

**Statement**: The SYSTEM shall route all issues to the private tracker by default.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-001 | ubiquitous | ALL agents SHALL file issues to `gmelli/aget-aget` |
| R-ISSUE-002 | conditional | IF an issue is promoted to public THEN the SYSTEM shall file it to `aget-framework/aget` via the promotion process (CAP-ISSUE-005) |

**Enforcement**: `validate_issue_destination.py`

**Rationale** (L638): Three rounds of remediation (L520 routing, L583 content scrubbing, L638 structural fix) demonstrated that routing by agent type with sanitization fails when content diversity exceeds pattern coverage. Private-first routing eliminates the filtering problem.

---

### CAP-ISSUE-002: Content Sanitization (Promotion Boundary)

**Statement**: The SYSTEM shall prevent private information in promoted public issues.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-003 | event-driven | WHEN promoting to Public_Issue_Destination, the SYSTEM shall NOT include private agent names |
| R-ISSUE-004 | event-driven | WHEN promoting to Public_Issue_Destination, the SYSTEM shall NOT include internal project details |

**Note**: Under private-first routing, sanitization applies only at the promotion boundary (CAP-ISSUE-005), not at filing time. All issues filed via R-ISSUE-001 go to the private tracker where no sanitization is needed.

**Private Patterns to Detect** (at promotion boundary):
```python
PRIVATE_PATTERNS = [
    r'private-\w+-aget',           # Private agent names
    r'private-\w+-AGET',           # Private agent names (caps)
    r'gmelli/\w+',                 # Private repo references
    r'\d+ agents? (in|across) fleet', # Fleet size disclosure
    r'SESSION_\d{4}-\d{2}-\d{2}',  # Session file references
    r'vp_of_ai-aget',              # Known private agent
    r'law_insider-aget',           # Known private agent
    # Added per L583:
    r'[Ll]egal[Oo]n',              # Proprietary company name
    r'[Vv][Pp]-?of-?[Aa][Ii]',     # Cross-fleet agent reference
    r'[Ww]ork[Cc]o',               # Domain placeholder
    # Added per L638:
    r'FLEET-\w+-\d+',              # Internal project IDs
    r'\d+ agents?\s',              # Fleet size (broader)
    r'legalforce-\w+-aget',        # Cross-fleet agent reference (sanitized form)
]
```

**Enforcement**: `sanitize_issue_content.py`

---

### CAP-ISSUE-003: Issue Filing Verification

**Statement**: The SYSTEM shall verify destination before filing.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-005 | event-driven | WHEN filing issues, the SYSTEM shall verify destination is `gmelli/aget-aget` |
| R-ISSUE-006 | event-driven | WHEN promoting to public destination, the SYSTEM shall validate content for private patterns |

**Enforcement**: `create_issue.py --governance-check`

---

### CAP-ISSUE-004: Repository Issue Settings

**Statement**: The SYSTEM shall maintain appropriate issue settings on repositories.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-007 | ubiquitous | Template repositories SHALL have GitHub issues DISABLED |
| R-ISSUE-008 | ubiquitous | Organization config repositories (.github) SHALL have issues DISABLED |
| R-ISSUE-009 | ubiquitous | `aget-framework/aget` SHALL accept issues only via promotion from `gmelli/aget-aget` |
| R-ISSUE-010 | optional | WHERE GitHub supports organization issue types, the organization MAY define standard issue types |

**Enforcement**: `repo_settings_validator.py --check-issues`

---

### CAP-ISSUE-005: Issue Promotion

**Statement**: The SYSTEM shall enforce governance requirements when promoting issues from private to public.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-011 | event-driven | WHEN promoting an issue to `aget-framework/aget`, the SYSTEM shall require principal approval |
| R-ISSUE-012 | event-driven | WHEN promoting an issue, the promoted content SHALL pass content sanitization check (R-ISSUE-003, R-ISSUE-004) before filing |
| R-ISSUE-013 | event-driven | WHEN promoting an issue, the promoted issue SHALL reference the private source issue for traceability |
| R-ISSUE-014 | event-driven | WHEN promoting an issue, the promoted content SHALL NOT contain fleet sizes, internal project IDs, organizational names, or private agent identifiers |

**Enforcement**: Manual (principal-approved process). Tooling deferred to first use.

**Rationale**: Promotion is an explicit, reviewable action — not a passive filter. This is the architectural difference from the prior agent-type routing approach.

---

## Repository Issue Matrix

| Repository | Issues | Visibility | Rationale |
|------------|--------|------------|-----------|
| `gmelli/aget-aget` | **enabled** | private | Default filing destination for all agents |
| `aget-framework/aget` | **enabled** | public | Promotion-only public issue tracker |
| `aget-framework/.github` | disabled | public | Org config only |
| `aget-framework/template-*` | disabled | public | Code templates, not issue targets |

---

## Agent Type Detection

### Algorithm

```python
def detect_agent_type(agent_root: Path) -> str:
    """Detect whether agent is private fleet or public/remote.

    Note: Under private-first routing (v2.0.0), agent type no longer
    determines filing destination — all agents file to gmelli/aget-aget.
    This detection remains useful for other governance purposes.
    """

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
# Check destination before filing (should always return gmelli/aget-aget)
python3 .aget/patterns/github/validate_issue_destination.py --check

# File with governance checks (default — routes to gmelli/aget-aget)
python3 .aget/patterns/github/create_issue.py --title "..." --body "..."
```

### Promotion Validation

```bash
# Check content for private patterns (before promotion only)
echo "Issue body text" | python3 .aget/patterns/github/sanitize_issue_content.py --check
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
Destination: gmelli/aget-aget (private-first routing)
Repository Settings: 14/15 repos have issues disabled (expected)
```

---

## Red Flags

| Anti-Pattern | Detection | Consequence |
|--------------|-----------|-------------|
| Filing directly to `aget-framework/aget` (any agent) | Destination validator | Bypasses private-first routing |
| Issue body contains `private-*-aget` in promoted issue | Content sanitizer (at promotion) | Private agent name leaked |
| Issue body contains fleet size in promoted issue | Content sanitizer (at promotion) | Internal capacity exposed |
| Template repo has issues enabled | Repo settings validator | Issue fragmentation |
| Promoting without principal approval | Promotion checklist | Bypasses R-ISSUE-011 |

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Information Security (Principle of Least Privilege)"
  secondary:
    - "Defense in Depth"
    - "Separation of Concerns"
    - "Structural vs Behavioral Control"
  reference: "L520, L583, L638"
  key_insight: "Filter-then-publish fails when content diversity exceeds pattern coverage. Publish-from-private succeeds because promotion is an explicit, reviewable action."
```

**Rationale**: Private information should only flow through channels appropriate for its sensitivity level. Private-first routing is a structural control — it eliminates the content filtering problem rather than attempting to solve it with ever-growing pattern lists.

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L520", "L583", "L638"]
  pattern_origin: "Issue #4 incident (private info in public-facing repo)"
  evolution:
    - version: "1.0.0"
      date: "2026-01-11"
      approach: "Agent-type routing"
      outcome: "48 violations discovered Feb 14"
    - version: "1.1.0"
      date: "2026-02-14"
      approach: "Content pattern sanitization"
      outcome: "19 violations remained Mar 2"
    - version: "2.0.0"
      date: "2026-03-02"
      approach: "Private-first routing (structural fix)"
      outcome: "Eliminates content filtering at filing time"
  effective_date: "2026-03-02"
```

---

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Specification | Active (v2.0.0) | This document |
| Destination validator | Pending update | `.aget/patterns/github/validate_issue_destination.py` |
| Content sanitizer | Active (promotion use) | `.aget/patterns/github/sanitize_issue_content.py` |
| Integrated filing script | Pending update | `.aget/patterns/github/create_issue.py` |
| Repo settings check | Active | `repo_settings_validator.py` |
| Promotion tooling | Deferred | Spec defines requirements; tooling deferred to first use |

---

## References

- L520: Issue Governance Gap
- L583: Issue Content Sanitization Gap
- L638: Private-First Issue Routing
- PROJECT_PLAN_issue_governance_v1.0.md
- PROJECT_PLAN_issue_content_sanitization_v1.0.md
- PROJECT_PLAN_public_issue_migration_v1.0.md
- AGET_RELEASE_SPEC (R-REL requirements pattern)
- AGET_TEMPLATE_SPEC (template requirements)
- AGET_VOCABULARY_SPEC (vocabulary alignment)
- GitHub Issue Types Documentation
- GitHub Projects Best Practices

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification: routing, sanitization, repo settings |
| 1.1.0 | 2026-02-14 | Added LegalOn, VP-of-AI, WorkCo patterns per L583 |
| 2.0.0 | 2026-03-02 | **Private-first routing**: R-ISSUE-001 rewritten (all agents → gmelli/aget-aget), R-ISSUE-002 rewritten (promotion-only), R-ISSUE-009 revised (promotion target), CAP-ISSUE-005 added (R-ISSUE-011 through R-ISSUE-014: promotion requirements), vocabulary updated, Exhaustive_Pattern_List anti-pattern added. Per L638. |

---

*AGET_ISSUE_GOVERNANCE_SPEC v2.0.0*
*"File private-first. Promote explicitly."*
