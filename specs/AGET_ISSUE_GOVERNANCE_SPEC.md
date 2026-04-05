# AGET Issue Governance Specification

**Version**: 2.1.0
**Status**: Active
**Category**: Process (Issue Management)
**Format Version**: 1.3
**Created**: 2026-01-11
**Updated**: 2026-04-04
**Author**: aget-framework
**Location**: `aget/specs/AGET_ISSUE_GOVERNANCE_SPEC.md`
**Change Origin**: PROJECT_PLAN_issue_governance_v1.0, PROJECT_PLAN_issue_content_sanitization_v1.0, PROJECT_PLAN_public_issue_migration_v1.0, PROJECT_PLAN_issue_management_remediation_v3.11_v1.0
**Related Specs**: AGET_RELEASE_SPEC, AGET_TEMPLATE_SPEC, AGET_ORGANIZATION_SPEC, AGET_VOCABULARY_SPEC

---

## Abstract

This specification defines issue management governance for the AGET framework. All issues are filed to the private tracker (`{private-tracker}`) by default. Public issues on `aget-framework/aget` are created only via explicit promotion with principal approval. This private-first routing eliminates the need for content sanitization at filing time — sanitization applies only at the promotion boundary.

v2.1.0 adds triage, lifecycle management, and structured filing capabilities (CAP-ISSUE-006 through CAP-ISSUE-008) grounded in Kubernetes triage patterns, faceted classification, and GitHub Issue Forms.

## Motivation

Issue governance challenges observed in practice:

1. **Private info exposure**: Private agent filed issue containing internal agent names to public-facing repo (Issue #4 in `aget-framework/template-supervisor-aget`)
2. **Issue fragmentation**: Issues scattered across template repos instead of central tracker
3. **Pattern-based sanitization structurally insufficient**: Three rounds of remediation (L520, L583, L638) demonstrated that content diversity exceeds pattern coverage — 19 of 50 public issues (38%) still contained private information after two prior remediations
4. **Repo settings drift**: Template repos had issues enabled by default
5. **Filing without grooming** (v2.1.0): 100 open issues at v3.11 planning start — filing governed but no triage, lifecycle, or closing process existed (L750)
6. **Classification without consequence** (v2.1.0): Labels and categories applied without downstream behavioral triggers (L671)

**Root cause** (L638 5-Whys): The original architecture placed private content in a public context, then attempted to filter it. Filter-then-publish fails when content diversity is open-ended. Private-first routing is the structural fix.

**Root cause** (L750): Filing governance (CAP-ISSUE-001) was mature but lifecycle governance was absent. Issues accumulated monotonically because no SOP, skill, or scheduled trigger existed for triage or closing.

## Scope

**Applies to**: All agents filing issues related to the AGET framework.

**Defines**:
- Issue routing policy (private-first, promotion-based)
- Issue promotion requirements
- Content sanitization requirements (at promotion boundary only)
- Repository issue settings requirements
- Validation and enforcement mechanisms
- Issue triage and classification (v2.1.0)
- Issue lifecycle state machine (v2.1.0)
- Structured filing via Issue Forms (v2.1.0)

**Does not cover**:
- Pull request governance (see future PR_GOVERNANCE_SPEC)
- Automated issue triage bot implementation
- GitHub Projects V2 integration
- Cross-organization issue aggregation

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "issue_governance"
    version: "2.1.0"
    inherits: "aget_core"

  # --- v2.0.0 terms (retained unchanged) ---

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
      aget:value: "{private-tracker}"
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
      skos:related: ["R-ISSUE-011", "R-ISSUE-012", "R-ISSUE-013", "R-ISSUE-014", "Promotion_Workflow"]

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

  # --- v2.1.0 terms (new) ---

  triage:
    Issue_Triage:
      skos:prefLabel: "Issue_Triage"
      skos:definition: "Systematic process of reviewing, classifying, and prioritizing filed issues to determine their disposition for a release cycle"
      skos:narrower:
        - Triage_State
        - Triage_Priority
        - Triage_Classification
      skos:related: ["Issue_Lifecycle", "R-ISSUE-015", "R-ISSUE-016"]
      aget:governed_by: "AGET_ISSUE_GOVERNANCE_SPEC"
      aget:consequence: "Determines VERSION_SCOPE inclusion and release scheduling"

    Triage_State:
      skos:prefLabel: "Triage_State"
      skos:definition: "Current disposition of an issue within the triage process"
      skos:broader: "Issue_Triage"
      skos:narrower: ["Needs_Triage", "Triaged", "Accepted", "Declined"]
      aget:consequence: "Issues in Needs_Triage state are NOT eligible for VERSION_SCOPE inclusion"

    Needs_Triage:
      skos:prefLabel: "Needs_Triage"
      skos:definition: "Issue has been filed but not yet reviewed by the triage process"
      skos:broader: "Triage_State"
      aget:consequence: "Issue excluded from VERSION_SCOPE until triaged"
      aget:detection: "No triage classification label present"

    Triaged:
      skos:prefLabel: "Triaged"
      skos:definition: "Issue has been reviewed and assigned a triage classification"
      skos:broader: "Triage_State"
      aget:consequence: "Issue eligible for VERSION_SCOPE consideration"

    Accepted:
      skos:prefLabel: "Accepted"
      skos:definition: "Issue has been triaged and accepted into a VERSION_SCOPE"
      skos:broader: "Triage_State"
      aget:consequence: "Issue tracked in VERSION_SCOPE; PROJECT_PLAN may be required"

    Declined:
      skos:prefLabel: "Declined"
      skos:definition: "Issue has been triaged and determined to be out of scope, duplicate, or resolved"
      skos:broader: "Triage_State"
      aget:consequence: "Issue closed with rationale"

    Triage_Priority:
      skos:prefLabel: "Triage_Priority"
      skos:definition: "Relative urgency and importance of an issue, determining VERSION_SCOPE tier assignment"
      skos:broader: "Issue_Triage"
      skos:narrower: ["Priority_Critical", "Priority_High", "Priority_Medium", "Priority_Low", "Priority_Awaiting_Evidence"]
      aget:consequence: "Maps to VERSION_SCOPE tiers: P1/P2/P3"

    Priority_Critical:
      skos:prefLabel: "Priority_Critical"
      skos:definition: "Issue blocks release or causes governance violations"
      skos:broader: "Triage_Priority"
      aget:consequence: "VERSION_SCOPE P1. PROJECT_PLAN required. Blocks release gate."

    Priority_High:
      skos:prefLabel: "Priority_High"
      skos:definition: "Issue has significant value and evidence grounding"
      skos:broader: "Triage_Priority"
      aget:consequence: "VERSION_SCOPE P2. PROJECT_PLAN recommended."

    Priority_Medium:
      skos:prefLabel: "Priority_Medium"
      skos:definition: "Issue has value but may be deferred without blocking release quality"
      skos:broader: "Triage_Priority"
      aget:consequence: "VERSION_SCOPE P2 or P3. Defer-eligible."

    Priority_Low:
      skos:prefLabel: "Priority_Low"
      skos:definition: "Nice-to-have improvement; stretch goal"
      skos:broader: "Triage_Priority"
      aget:consequence: "VERSION_SCOPE P3 (stretch)."

    Priority_Awaiting_Evidence:
      skos:prefLabel: "Priority_Awaiting_Evidence"
      skos:definition: "Issue lacks sufficient evidence to determine priority"
      skos:broader: "Triage_Priority"
      aget:consequence: "Not VERSION_SCOPE eligible until evidence provided"

    Triage_Classification:
      skos:prefLabel: "Triage_Classification"
      skos:definition: "Owner-and-scope classification assigned during triage"
      skos:broader: "Issue_Triage"
      skos:narrower: ["Classification_Release_Scoped", "Classification_Supervisor_Owned", "Classification_External", "Classification_Deferred", "Classification_Closeable"]
      aget:consequence: "Determines routing and VERSION_SCOPE eligibility"

    Classification_Release_Scoped:
      skos:prefLabel: "Classification_Release_Scoped"
      skos:definition: "Issue is within framework scope and targeted for a specific release"
      skos:broader: "Triage_Classification"
      aget:consequence: "Added to VERSION_SCOPE at assigned priority tier"

    Classification_Supervisor_Owned:
      skos:prefLabel: "Classification_Supervisor_Owned"
      skos:definition: "Issue belongs to supervisor agent scope"
      skos:broader: "Triage_Classification"
      aget:consequence: "Left open. Not in framework VERSION_SCOPE."

    Classification_External:
      skos:prefLabel: "Classification_External"
      skos:definition: "Issue belongs to an external agent or portfolio scope"
      skos:broader: "Triage_Classification"
      aget:consequence: "Routed to appropriate owner."

    Classification_Deferred:
      skos:prefLabel: "Classification_Deferred"
      skos:definition: "Issue is valid but not targeted for the current release cycle"
      skos:broader: "Triage_Classification"
      aget:consequence: "Left open. Subject to staleness detection."

    Classification_Closeable:
      skos:prefLabel: "Classification_Closeable"
      skos:definition: "Issue is superseded, duplicate, or resolved"
      skos:broader: "Triage_Classification"
      aget:consequence: "Closed with rationale (requires principal approval)"

  lifecycle:
    Issue_Lifecycle:
      skos:prefLabel: "Issue_Lifecycle"
      skos:definition: "State machine governing an issue from filing through resolution"
      skos:narrower:
        - Issue_Lifecycle_State
        - Lifecycle_Transition
        - Staleness_Level
        - Stale_Threshold
      skos:related: ["Issue_Triage", "R-ISSUE-017", "R-ISSUE-018"]
      aget:consequence: "Defines valid state transitions; invalid transitions are governance violations"

    Issue_Lifecycle_State:
      skos:prefLabel: "Issue_Lifecycle_State"
      skos:definition: "Current state of an issue within the lifecycle state machine"
      skos:broader: "Issue_Lifecycle"
      skos:narrower: ["State_Open", "State_In_Progress", "State_Stale", "State_Frozen", "State_Closed"]

    State_Open:
      skos:prefLabel: "State_Open"
      skos:definition: "Issue is filed and active; awaiting triage or work"
      skos:broader: "Issue_Lifecycle_State"
      aget:github_native: true
      aget:consequence: "Visible in triage queue"

    State_In_Progress:
      skos:prefLabel: "State_In_Progress"
      skos:definition: "Issue accepted; work begun (PROJECT_PLAN created or deliverable in progress)"
      skos:broader: "Issue_Lifecycle_State"
      aget:github_native: false
      aget:detection: "Label 'status:in-progress' present"
      aget:consequence: "Tracked in active PROJECT_PLAN. Not subject to staleness."

    State_Stale:
      skos:prefLabel: "State_Stale"
      skos:definition: "Issue has had no activity for >= Stale_Threshold"
      skos:broader: "Issue_Lifecycle_State"
      aget:github_native: false
      aget:detection: "No activity for >= 90 days"
      aget:consequence: "Flagged in next triage. Must justify, reprioritize, or close."

    State_Frozen:
      skos:prefLabel: "State_Frozen"
      skos:definition: "Issue intentionally paused; blocked by external dependency"
      skos:broader: "Issue_Lifecycle_State"
      aget:github_native: false
      aget:detection: "Label 'status:frozen' present with blocking reference"
      aget:consequence: "Excluded from triage queue. Not counted as stale."

    State_Closed:
      skos:prefLabel: "State_Closed"
      skos:definition: "Issue resolved, superseded, or declined"
      skos:broader: "Issue_Lifecycle_State"
      aget:github_native: true
      aget:consequence: "Removed from triage queue. Closing rationale required."

    Lifecycle_Transition:
      skos:prefLabel: "Lifecycle_Transition"
      skos:definition: "Valid state change within the issue lifecycle with trigger condition"
      skos:broader: "Issue_Lifecycle"
      aget:consequence: "Only valid transitions are permitted"

    Stale_Threshold:
      skos:prefLabel: "Stale_Threshold"
      skos:definition: "Duration of inactivity after which an issue transitions to State_Stale"
      skos:broader: "Issue_Lifecycle"
      aget:value: "90 days"

    Staleness_Level:
      skos:prefLabel: "Staleness_Level"
      skos:definition: "Graduated staleness classification"
      skos:broader: "Issue_Lifecycle"
      skos:narrower: ["Staleness_Fresh", "Staleness_Aging", "Staleness_Stale", "Staleness_Ancient"]
      aget:consequence: "Higher levels require stronger justification to keep open"

    Staleness_Fresh:
      skos:prefLabel: "Staleness_Fresh"
      skos:definition: "Created within the current release cycle"
      skos:broader: "Staleness_Level"
      aget:consequence: "Normal triage"

    Staleness_Aging:
      skos:prefLabel: "Staleness_Aging"
      skos:definition: "Open for 1 release cycle"
      skos:broader: "Staleness_Level"
      aget:consequence: "Priority review at next triage"

    Staleness_Stale:
      skos:prefLabel: "Staleness_Stale"
      skos:definition: "Open for 2+ release cycles"
      skos:broader: "Staleness_Level"
      aget:consequence: "Must justify or close"

    Staleness_Ancient:
      skos:prefLabel: "Staleness_Ancient"
      skos:definition: "Open for 3+ release cycles"
      skos:broader: "Staleness_Level"
      aget:consequence: "Close unless actively referenced in PROJECT_PLAN"

  labeling:
    Issue_Label_Taxonomy:
      skos:prefLabel: "Issue_Label_Taxonomy"
      skos:definition: "Faceted labeling system for filtering, routing, and triage"
      skos:narrower: ["Label_Category", "Standard_Label_Set"]
      skos:related: ["Issue_Triage", "R-ISSUE-016"]
      aget:consequence: "Labels drive triage filtering and reporting"

    Label_Category:
      skos:prefLabel: "Label_Category"
      skos:definition: "A facet dimension; issues may have one label per category"
      skos:broader: "Issue_Label_Taxonomy"
      skos:narrower: ["Category_Type", "Category_Priority", "Category_Domain", "Category_Status", "Category_Owner"]

    Category_Type:
      skos:prefLabel: "Category_Type"
      skos:definition: "Classification by nature of work"
      skos:broader: "Label_Category"
      aget:labels: ["type:bug", "type:enhancement", "type:feature", "type:documentation", "type:governance", "type:deprecation"]

    Category_Priority:
      skos:prefLabel: "Category_Priority"
      skos:definition: "Release-relative priority"
      skos:broader: "Label_Category"
      aget:labels: ["priority:critical", "priority:high", "priority:medium", "priority:low", "priority:awaiting-evidence"]

    Category_Domain:
      skos:prefLabel: "Category_Domain"
      skos:definition: "Functional area of the framework"
      skos:broader: "Label_Category"
      aget:labels: ["domain:core", "domain:templates", "domain:governance", "domain:release-process", "domain:ontology", "domain:skills", "domain:session-protocol"]

    Category_Status:
      skos:prefLabel: "Category_Status"
      skos:definition: "Lifecycle status tracked via label"
      skos:broader: "Label_Category"
      aget:labels: ["status:needs-triage", "status:accepted", "status:in-progress", "status:stale", "status:frozen"]

    Category_Owner:
      skos:prefLabel: "Category_Owner"
      skos:definition: "Organizational owner"
      skos:broader: "Label_Category"
      aget:labels: ["owner:framework", "owner:supervisor", "owner:external"]

    Standard_Label_Set:
      skos:prefLabel: "Standard_Label_Set"
      skos:definition: "Complete governed label set for {private-tracker}"
      skos:broader: "Issue_Label_Taxonomy"
      aget:consequence: "Non-standard labels flagged during grooming"

  promotion_workflow:
    Promotion_Workflow:
      skos:prefLabel: "Promotion_Workflow"
      skos:definition: "End-to-end process for promoting private issue to public tracker"
      skos:narrower: ["Promotion_Request", "Promotion_Approval", "Promotion_Checklist", "Promoted_Issue", "Promotion_Status"]
      skos:related: ["Issue_Promotion", "CAP-ISSUE-005"]
      aget:consequence: "Only valid path from private to public"

    Promotion_Status:
      skos:prefLabel: "Promotion_Status"
      skos:definition: "Current state within the promotion workflow"
      skos:broader: "Promotion_Workflow"
      skos:narrower: ["Promotion_Not_Requested", "Promotion_Pending", "Promotion_Approved", "Promotion_Complete", "Promotion_Deferred"]

    Promotion_Not_Requested:
      skos:prefLabel: "Promotion_Not_Requested"
      skos:definition: "Default state — no promotion requested"
      skos:broader: "Promotion_Status"

    Promotion_Pending:
      skos:prefLabel: "Promotion_Pending"
      skos:definition: "Promotion requested, awaiting principal approval"
      skos:broader: "Promotion_Status"

    Promotion_Approved:
      skos:prefLabel: "Promotion_Approved"
      skos:definition: "Principal approved; agent may execute promotion"
      skos:broader: "Promotion_Status"

    Promotion_Complete:
      skos:prefLabel: "Promotion_Complete"
      skos:definition: "Issue filed on public tracker, cross-referenced"
      skos:broader: "Promotion_Status"

    Promotion_Deferred:
      skos:prefLabel: "Promotion_Deferred"
      skos:definition: "Promotion considered but intentionally deferred"
      skos:broader: "Promotion_Status"

    Promotion_Request:
      skos:prefLabel: "Promotion_Request"
      skos:definition: "Formal request to promote with sanitized content and rationale"
      skos:broader: "Promotion_Workflow"

    Promotion_Approval:
      skos:prefLabel: "Promotion_Approval"
      skos:definition: "Principal's explicit authorization to promote"
      skos:broader: "Promotion_Workflow"
      aget:authority: "principal"

    Promotion_Checklist:
      skos:prefLabel: "Promotion_Checklist"
      skos:definition: "Verification steps before promotion: approval, sanitization, traceability, content audit"
      skos:broader: "Promotion_Workflow"

    Promoted_Issue:
      skos:prefLabel: "Promoted_Issue"
      skos:definition: "Issue that completed promotion with back-reference to private source"
      skos:broader: "Promotion_Workflow"

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

    Filing_Without_Grooming:
      skos:definition: "Issues filed systematically but never reviewed, prioritized, or closed"
      aget:anti_pattern: true
      aget:severity: "high"
      skos:related: ["L750", "Issue_Triage"]
      aget:detection: "Issue count > 50 with no ISSUE_TRIAGE artifact"

    Grooming_Without_Closing:
      skos:definition: "Triage artifacts created but no issues actually closed"
      aget:anti_pattern: true
      aget:severity: "medium"
      skos:related: ["L671", "Classification_Closeable"]

    Decorative_Labeling:
      skos:definition: "Labels applied that do not drive any triage, routing, or lifecycle behavior"
      aget:anti_pattern: true
      aget:severity: "medium"
      skos:related: ["L671", "Issue_Label_Taxonomy"]
```

---

## Requirements

### CAP-ISSUE-001: Issue Destination Routing (Private-First)

**Statement**: The SYSTEM shall route all issues to the private tracker by default.

**Pattern**: ubiquitous

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-001 | ubiquitous | ALL agents SHALL file issues to `{private-tracker}` |
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
    r'vp_of_ai-aget',              # Known cross-fleet agent pattern
    r'law_insider-aget',           # Known private agent
    # Added per L583:
    r'[Ll]egal[Oo]n',              # Proprietary company name
    r'[Vv][Pp]-?of-?[Aa][Ii]',     # Cross-fleet agent reference
    r'[Ww]ork[Cc]o',               # Domain placeholder
    # Added per L638:
    r'FLEET-\w+-\d+',              # Internal project IDs
    r'\d+ agents?\s',              # Fleet size (broader)
    r'workforce-\w+-aget',        # Cross-fleet agent reference (sanitized form)
]
```

**Enforcement**: `sanitize_issue_content.py`

---

### CAP-ISSUE-003: Issue Filing Verification

**Statement**: The SYSTEM shall verify destination before filing.

**Pattern**: event-driven

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-005 | event-driven | WHEN filing issues, the SYSTEM shall verify destination is `{private-tracker}` |
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
| R-ISSUE-009 | ubiquitous | `aget-framework/aget` SHALL accept issues only via promotion from `{private-tracker}` |
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

**Enforcement**: `/aget-promote-issue` skill (proposed). Manual until skill implemented.

**Rationale**: Promotion is an explicit, reviewable action — not a passive filter. This is the architectural difference from the prior agent-type routing approach.

---

### CAP-ISSUE-006: Issue Triage (v2.1.0)

**Statement**: The SYSTEM shall provide a structured triage process for classifying and prioritizing filed issues.

**Pattern**: event-driven

**Theoretical Basis**: Kubernetes 5-step triage model (kubernetes.dev), Ranganathan faceted classification (1933), Ashby's requisite variety — triage categories must match issue variety.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-015 | event-driven | WHEN a new issue is filed to `{private-tracker}`, the SYSTEM shall assign Triage_State `Needs_Triage` by default |
| R-ISSUE-016 | event-driven | WHEN performing backlog grooming (SOP_backlog_grooming), the SYSTEM shall assign each issue exactly ONE Triage_Classification (Release_Scoped, Supervisor_Owned, External, Deferred, or Closeable) and ONE Triage_Priority (Critical, High, Medium, Low, or Awaiting_Evidence) for release-scoped issues |
| R-ISSUE-017 | conditional | IF an issue is classified as Classification_Closeable THEN the SYSTEM shall close it with a rationale comment and cross-reference, subject to principal approval for batch closes |

**Enforcement**: SOP_backlog_grooming.md (behavioral). Label audit during grooming (manual).

**Rationale** (L750): Filing governance was mature (CAP-ISSUE-001) but triage was absent. 100 open issues accumulated at v3.11 planning start. Issues without triage cannot be scoped effectively — scope decisions operate against stale data.

**Rationale** (L671): Every triage classification must have a documented consequence. Classifications without downstream behavior are decorative metadata. The consequence is: triage classification determines VERSION_SCOPE eligibility and tier assignment.

---

### CAP-ISSUE-007: Issue Lifecycle Management (v2.1.0)

**Statement**: The SYSTEM shall manage issue lifecycle through a governed state machine with staleness detection.

**Pattern**: state-driven

**Theoretical Basis**: Mealy/Moore state machine theory. L498 P2: domain-specific lifecycle extensions over minimal core. K8s stale/frozen pattern adapted for AGET release cadence.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-018 | ubiquitous | ALL issues SHALL follow the lifecycle state machine: Open -> {In_Progress, Stale, Frozen, Closed}; In_Progress -> {Closed, Frozen}; Stale -> {Open, Closed}; Frozen -> {Open, Closed} |
| R-ISSUE-019 | event-driven | WHEN an issue has had no activity (comments, label changes, or cross-references) for >= 90 days (Stale_Threshold), the SYSTEM shall flag it as State_Stale at the next triage cycle |
| R-ISSUE-020 | conditional | IF an issue is State_Stale AND classified as Staleness_Ancient (3+ release cycles), THEN the SYSTEM shall close it unless it is actively referenced in a current PROJECT_PLAN or VERSION_SCOPE |

**Lifecycle State Machine**:

```
                    ┌──────────────────┐
                    │    State_Open    │ (default at filing)
                    └──────┬───────────┘
                           │
              ┌────────────┼────────────┬──────────────┐
              ▼            ▼            ▼              ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │In_Progress│ │  Stale   │ │  Frozen  │ │  Closed  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘
             │             │            │
             ▼             ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Closed  │ │Open/Closed│ │Open/Closed│
        └──────────┘ └──────────┘ └──────────┘
```

**Valid Transitions**:

| From | To | Trigger | Evidence Required |
|------|-----|---------|-------------------|
| Open | In_Progress | Work begun | PROJECT_PLAN reference or label `status:in-progress` |
| Open | Stale | No activity >= 90 days | Staleness detection at triage |
| Open | Frozen | External dependency | Blocking issue/dependency documented in comment |
| Open | Closed | Declined/duplicate/resolved | Rationale in closing comment |
| In_Progress | Closed | Deliverable committed | Commit reference or PR merge |
| In_Progress | Frozen | Blocker discovered | Blocker documented |
| Stale | Open | Justified at triage | Reprioritization rationale |
| Stale | Closed | Not justified | Closing rationale |
| Frozen | Open | Dependency resolved | Resolution evidence |
| Frozen | Closed | Dependency unresolvable | Closing rationale |

**Enforcement**: Label-based tracking on `{private-tracker}`. SOP_backlog_grooming Phase 3 (staleness detection).

---

### CAP-ISSUE-008: Structured Filing via Issue Forms (v2.1.0)

**Statement**: The public issue tracker SHALL provide structured filing templates to ensure consistent issue quality.

**Pattern**: ubiquitous

**Theoretical Basis**: GitHub Issue Forms documentation. Structured inputs reduce filing friction and enable auto-labeling.

| ID | Pattern | Statement |
|----|---------|-----------|
| R-ISSUE-021 | ubiquitous | `aget-framework/aget` SHALL provide Issue Form templates (YAML) for at least: enhancement, bug report, and feature request |
| R-ISSUE-022 | ubiquitous | Each Issue Form SHALL include required fields: title, description, and issue type |
| R-ISSUE-023 | event-driven | WHEN a user submits an Issue Form, the SYSTEM shall auto-assign the corresponding `type:` label |

**Note**: Issue Forms apply to the public tracker (`aget-framework/aget`) only. The private tracker (`{private-tracker}`) uses agent-generated issues via `/aget-file-issue` which already has governed structure.

**Enforcement**: GitHub repository settings. Presence check: `.github/ISSUE_TEMPLATE/*.yml`

---

## Repository Issue Matrix

| Repository | Issues | Visibility | Rationale |
|------------|--------|------------|-----------|
| `{private-tracker}` | **enabled** | private | Default filing destination for all agents |
| `aget-framework/aget` | **enabled** | public | Promotion-only public issue tracker. Issue Forms deployed (v2.1.0). |
| `aget-framework/.github` | disabled | public | Org config only |
| `aget-framework/template-*` | disabled | public | Code templates, not issue targets |

---

## Agent Type Detection

### Algorithm

```python
def detect_agent_type(agent_root: Path) -> str:
    """Detect whether agent is private fleet or public/remote.

    Note: Under private-first routing (v2.0.0), agent type no longer
    determines filing destination — all agents file to {private-tracker}.
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

## Authority Model

```yaml
authority:
  applies_to: "issue_routing_sanitization_triage_lifecycle"

  governed_by:
    spec: "AGET_ISSUE_GOVERNANCE_SPEC"
    owner: "aget-framework"

  agent_authority:
    can_autonomously:
      - "File issues to {private-tracker} (private tracker)"
      - "Run content sanitization checks on issue content"
      - "Validate issue destination before filing"
      - "Verify repository issue settings"
      - "Detect private patterns in issue content"
      - "Assign triage labels during backlog grooming (v2.1.0)"
      - "Flag stale issues during triage (v2.1.0)"
    requires_approval:
      - action: "Promote issue from private to public tracker"
        approver: "principal"
      - action: "Enable issues on template repositories"
        approver: "principal"
      - action: "Modify private pattern detection rules"
        approver: "principal"
      - action: "Batch close issues (> 2 issues)"
        approver: "principal"

  conformance:
    validator: "spec_readiness_validator.py"
    method: "automated"
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-ISSUE-001 | CAP-ISSUE-001 | automated | Verify default issue destination resolves to {private-tracker} for all agents |
| V-ISSUE-002 | CAP-ISSUE-002 | automated | Verify promoted issue content does not match PRIVATE_PATTERNS |
| V-ISSUE-003 | CAP-ISSUE-003 | automated | Verify pre-filing validation confirms destination is {private-tracker} |
| V-ISSUE-004 | CAP-ISSUE-004 | automated | Verify template repositories have GitHub issues disabled |
| V-ISSUE-005 | CAP-ISSUE-005 | manual | Verify promoted issues have principal approval and reference private source |
| V-ISSUE-006 | CAP-ISSUE-002 | automated | Verify sanitize_issue_content.py detects all PRIVATE_PATTERNS at promotion boundary |
| V-ISSUE-007 | CAP-ISSUE-004 | automated | Verify organization config repository (.github) has issues disabled |
| V-ISSUE-008 | CAP-ISSUE-001 | inspection | Verify private-first routing eliminates content sanitization requirement at filing time |
| V-ISSUE-009 | CAP-ISSUE-006 | inspection | Verify ISSUE_TRIAGE artifact assigns Triage_Classification and Triage_Priority to all issues |
| V-ISSUE-010 | CAP-ISSUE-006 | automated | Verify `status:needs-triage` label exists on `{private-tracker}` label set |
| V-ISSUE-011 | CAP-ISSUE-007 | inspection | Verify lifecycle transitions follow valid state machine (no invalid transitions in issue history) |
| V-ISSUE-012 | CAP-ISSUE-007 | automated | Verify staleness detection flags issues with no activity >= 90 days |
| V-ISSUE-013 | CAP-ISSUE-008 | automated | Verify `aget-framework/aget` has Issue Form YAML files in `.github/ISSUE_TEMPLATE/` |
| V-ISSUE-014 | CAP-ISSUE-008 | automated | Verify each Issue Form includes required fields: title, description, type label |

### Validation Commands

```bash
# Check destination before filing (V-ISSUE-001, V-ISSUE-003)
python3 .aget/patterns/github/validate_issue_destination.py --check

# File with governance checks (V-ISSUE-001)
python3 .aget/patterns/github/create_issue.py --title "..." --body "..."

# Check content for private patterns at promotion boundary (V-ISSUE-002, V-ISSUE-006)
echo "Issue body text" | python3 .aget/patterns/github/sanitize_issue_content.py --check

# Verify all repos have correct issue settings (V-ISSUE-004, V-ISSUE-007)
python3 .aget/patterns/validation/repo_settings_validator.py --check-issues

# Verify Issue Forms exist on public tracker (V-ISSUE-013)
ls aget-framework/aget/.github/ISSUE_TEMPLATE/*.yml 2>/dev/null | wc -l  # expect >= 3

# Verify labels deployed (V-ISSUE-010)
gh label list --repo {private-tracker} --search "status:needs-triage" --json name | python3 -c "import json,sys; print('PASS' if json.load(sys.stdin) else 'FAIL')"
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
| Filing without grooming (v2.1.0) | Issue count > 50, no ISSUE_TRIAGE | Stale backlog (L750) |
| Grooming without closing (v2.1.0) | Triage artifact exists, no closes | Decorative triage (L671) |
| Labels without behavior (v2.1.0) | Label not in any query/SOP | Decorative labeling (L671) |

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Information Security (Principle of Least Privilege)"
  secondary:
    - "Defense in Depth"
    - "Separation of Concerns"
    - "Structural vs Behavioral Control"
    - "Faceted Classification (Ranganathan 1933)"
    - "State Machine Theory (Mealy/Moore)"
    - "Cybernetics — Requisite Variety (Ashby 1956)"
    - "Pragmatist Epistemology — Consequential Classification (Peirce 1878)"
  reference: "L520, L583, L638, L750, L671, L498, L535, L595"
  key_insight: "Filter-then-publish fails when content diversity exceeds pattern coverage. Publish-from-private succeeds because promotion is an explicit, reviewable action."
  v2_1_insight: "Filing without grooming creates a one-way accumulator. Every classification must have a behavioral consequence — otherwise it is decorative metadata."
```

---

## Graduation History

```yaml
graduation:
  source_learnings: ["L520", "L583", "L638", "L750", "L671"]
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
    - version: "2.1.0"
      date: "2026-04-04"
      approach: "Triage, lifecycle, structured filing"
      outcome: "Closes filing-grooming gap (L750); adds state machine, faceted labels, Issue Forms"
  effective_date: "2026-04-04"
```

---

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Specification | Draft (v2.1.0) | This document |
| Destination validator | Active | `.aget/patterns/github/validate_issue_destination.py` |
| Content sanitizer | Active (promotion use) | `.aget/patterns/github/sanitize_issue_content.py` |
| Integrated filing script | Active | `.aget/patterns/github/create_issue.py` |
| Repo settings check | Active | `repo_settings_validator.py` |
| Promotion tooling | Proposed (SP-004) | `/aget-promote-issue` skill |
| Triage SOP | Active | `sops/SOP_backlog_grooming.md` |
| Issue Forms | Draft | `planning/artifacts/issue_forms/*.yml` (Gate 3) |
| Standard label set | Draft | `planning/artifacts/issue_governance_vocabulary_v2.1.0_draft.md` |

---

## References

- L520: Issue Governance Gap
- L583: Issue Content Sanitization Gap
- L638: Private-First Issue Routing
- L750: Backlog Grooming Gap
- L671: Classification Without Consequence
- L498: Action Item Ontology Implications
- L535: Vocabulary Completeness Gap
- L595: Action Item Management Theoretical Grounding
- PROJECT_PLAN_issue_governance_v1.0.md
- PROJECT_PLAN_issue_content_sanitization_v1.0.md
- PROJECT_PLAN_public_issue_migration_v1.0.md
- PROJECT_PLAN_issue_management_remediation_v3.11_v1.0.md
- AGET_RELEASE_SPEC (R-REL requirements pattern)
- AGET_TEMPLATE_SPEC (template requirements)
- AGET_VOCABULARY_SPEC (vocabulary alignment)
- SOP_backlog_grooming.md (triage process)
- kubernetes.dev: Issue Triage Guidelines
- Ranganathan, S.R. (1933). Colon Classification
- GitHub Docs: Issue Forms

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification: routing, sanitization, repo settings |
| 1.1.0 | 2026-02-14 | Added WorkCo, VP-of-AI, WorkCo patterns per L583 |
| 2.0.0 | 2026-03-02 | **Private-first routing**: R-ISSUE-001 rewritten (all agents -> {private-tracker}), R-ISSUE-002 rewritten (promotion-only), R-ISSUE-009 revised (promotion target), CAP-ISSUE-005 added (R-ISSUE-011 through R-ISSUE-014: promotion requirements), vocabulary updated, Exhaustive_Pattern_List anti-pattern added. Per L638. |
| 2.1.0 | 2026-04-04 | **Triage, lifecycle, structured filing**: CAP-ISSUE-006 (Triage: R-ISSUE-015 through R-ISSUE-017), CAP-ISSUE-007 (Lifecycle: R-ISSUE-018 through R-ISSUE-020), CAP-ISSUE-008 (Issue Forms: R-ISSUE-021 through R-ISSUE-023). 54 new SKOS vocabulary terms across 4 concept groups (triage, lifecycle, labeling, promotion_workflow). 3 new anti-patterns. 6 new V-tests (V-ISSUE-009 through V-ISSUE-014). Per L750, L671, L498. |

---

*AGET_ISSUE_GOVERNANCE_SPEC v2.1.0*
*"File private-first. Triage with consequence. Promote explicitly."*
