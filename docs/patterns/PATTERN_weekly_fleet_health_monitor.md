# Pattern: Weekly Fleet Health Monitor

**Version**: 1.0.0
**Status**: Active
**Created**: 2026-04-26
**Source Learnings**: L822 (CI Infrastructure Decay), L831 (Cross-Agent Question Convergence = Spec Signal), L836 (Fleet CI Verification Gap)
**Evidence**: Two independent supervisors (main fleet + legalon fleet) designed identical weekly RemoteTrigger routines independently. Cross-fleet convergence without coordination is a strong signal this is a framework-level best practice (L831).

---

## Problem

Fleet health degrades silently between migrations. After a fleet upgrade completes, no mechanism prompts the supervisor to verify agents remain healthy. Issues accumulate:

- Agents accumulate CORRECTION commits (governance violations) undetected
- Session scripts silently fail after environment changes
- Version drift goes unnoticed between releases
- CI spec staleness is not caught until principal surfaces an external failure report

The feedback loop ends at delivery (upgrade complete) rather than at confirmation (agents healthy, running, no violations). The Loading Dock anti-pattern (L656) applies at the fleet level: UPGRADED ≠ HEALTHY.

---

## Pattern

A **weekly RemoteTrigger routine** runs automated fleet health verification on a regular cadence. The supervisor does not need to manually check — the routine surfaces anomalies proactively.

**Trigger**: Weekly scheduled agent invocation (e.g., RemoteTrigger, cron, CI workflow)

**Three checks**:

| Check | Command | Signal |
|-------|---------|--------|
| **Health status** | `health_check.py --json` per agent | Structural compliance |
| **CORRECTION monitor** | `git log --oneline --since="7 days ago"` with `\(CORRECTION\)` grep | Governance violations |
| **Version consistency** | `jq -r '.aget_version' .aget/version.json` per agent | Version drift |

**Output**: Structured report posted to supervisor (email, Slack, or session file) listing:
- Agent count by health status (healthy / warning / error)
- Agents with CORRECTION commits in the past 7 days
- Any agents off the fleet's canonical version

---

## Implementation

### Prerequisites

Before deploying this routine:

1. **Fix #1166 (three fixes required before production)**:
   - Remove `Write` tool from routine permissions (not needed for read-only health checks; Write is a blast-radius risk in an automated context)
   - Validate CORRECTION grep pattern uses parenthesized form: `\(CORRECTION\)` (not plain `CORRECTION` — plain form produces false positives on commit messages containing "correction" as a word)
   - Add auth smoke-test: `gh auth status` must exit 0 before any gh CLI operations (cloud-hosted agents may have keyring failures — see SOP_fleet_migration.md Prerequisites)

2. **gh auth verified** on execution machine (keyring issue risk for cloud agents)

### RemoteTrigger Configuration Template

```yaml
# .aget/routines/weekly_fleet_health.yaml
name: weekly_fleet_health_monitor
trigger:
  type: scheduled
  cadence: weekly
  day: monday
  time: "09:00"
permissions:
  - Bash(git:*)
  - Bash(python3:*)
  - Read
  # NOTE: Do NOT include Write — read-only routine

steps:
  - name: health_check
    for_each_agent: true
    command: "python3 {agent_path}/scripts/health_check.py --json"
    
  - name: correction_monitor
    for_each_agent: true
    command: "git -C {agent_path} log --oneline --since='7 days ago' | grep -c '\\(CORRECTION\\)'"
    
  - name: version_check
    for_each_agent: true
    command: "jq -r '.aget_version' {agent_path}/.aget/version.json"

report:
  format: summary
  destination: supervisor_session_file
  escalate_on:
    - health_status: error
    - correction_count: ">= 3"
    - version: "!= {fleet_canonical_version}"
```

### Minimal Bash Implementation

For supervisors not using a RemoteTrigger framework:

```bash
#!/bin/bash
# weekly_fleet_health.sh — run weekly, e.g., via cron
# 0 9 * * 1 /path/to/weekly_fleet_health.sh > /path/to/report.txt 2>&1

TARGET_VERSION=$(cat ~/github/aget-framework/aget/.aget/version.json | python3 -c "import json,sys; print(json.load(sys.stdin)['aget_version'])")
AGENTS=(~/github/private-*-aget ~/github/GM-*/private-*-aget)
CUTOFF=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)

echo "=== Weekly Fleet Health Report — $(date +%Y-%m-%d) ==="
echo ""

for agent in "${AGENTS[@]}"; do
  name=$(basename $agent)
  
  # Health check
  health=$(python3 $agent/scripts/health_check.py --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "error")
  
  # Version
  ver=$(python3 -c "import json; print(json.load(open('$agent/.aget/version.json')).get('aget_version','?'))" 2>/dev/null || echo "?")
  
  # CORRECTION commits
  corrections=$(git -C $agent log --oneline --since="$CUTOFF" 2>/dev/null | grep -c '(CORRECTION)' || echo 0)
  
  # Version drift flag
  drift=""
  [ "$ver" != "$TARGET_VERSION" ] && drift=" [VERSION DRIFT: $ver]"
  
  echo "$name: $health | corrections=$corrections$drift"
done
```

---

## Threshold Guidance

| Metric | Green | Amber | Red |
|--------|-------|-------|-----|
| Agents healthy | 100% | 90-99% | < 90% |
| CORRECTION commits/agent/week | 0 | 1-2 | ≥ 3 |
| Version drift | 0 agents | 1-2 agents | > 2 agents |

**Red = escalate to principal session** (do not defer to next routine cycle).

---

## Cross-Fleet Convergence Evidence

This pattern was independently designed by two separate fleet supervisors:

1. **Main fleet supervisor** (private-supervisor-AGET): designed weekly RemoteTrigger routine during FLEET-UPG-013 post-mortem analysis (2026-04-26)
2. **Legalon fleet supervisor**: independently designed identical routine design during FLEET-UPG-014 analysis (2026-04-26), including the same three checks and same cadence

Neither supervisor was aware of the other's design. Independent convergence to the same architecture is the L831 "Cross-Agent Question Convergence = Spec Signal" pattern — both agents hit the same gap (no post-migration health feedback loop) and produced the same solution independently. This confidence level is sufficient to promote from local pattern to framework recommendation.

---

## Related

- SOP_fleet_migration.md § Post-Migration: Ongoing Health Monitoring
- L822 (CI Infrastructure Decay — the same silent-decay problem at CI layer)
- L831 (Cross-Agent Question Convergence = Spec Signal)
- L836 (Fleet CI Verification Gap — convergent finding)
- L656 (Loading Dock Anti-Pattern — UPGRADED ≠ DEPLOYED/HEALTHY)
- #1166 (three fixes required before production deployment)

---

*PATTERN_weekly_fleet_health_monitor.md — Framework-recommended post-migration health routine*
*Promoted from: Main + Legalon supervisor convergent design (2026-04-26)*
