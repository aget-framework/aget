# SOP: Scope-Lock Ceremony

**Version**: 1.0.0
**Status**: LANDED
**Created**: 2026-05-09
**Updated**: 2026-05-09 (DRAFT v0.1.0 → LANDED v1.0.0 via v3.17.0 release plan G1.5.1; T2.18 deliverable per VERSION_SCOPE_v3.17.0 Q-G1.5-2 disposition)
**Owner**: private-aget-framework-AGET (canonical-promoted to `aget-framework/aget/sops/SOP_scope_lock_ceremony.md`)
**Implements**: R-REL-022-01 (Lock-Event Status Transition), CAP-REL-029 (Lock-Event Protocol)
**Governing**: PROJECT_PLAN scope-lock plans (v3.16, v3.17 cycles); VERSION_SCOPE_vX.Y.Z lifecycle state machine (L708)
**Source Evidence**: `planning/PROJECT_PLAN_v3.16.0_scope_lock_v1.0.md` v1.1.2 (Complete); `planning/PROJECT_PLAN_v3.17.0_scope_lock_v1.0.md` v1.1.2 (Complete); `MEMO_v3.17_release_patterns_research_2026_05_09.md`; `MEMO_v3.17_freshness_audit_2026_05_09.md`; v3.17.0 release plan v1.0.18 (lock event commit `e50a182` 2026-05-09T13:28:03-0700)
**Empirical Grounding (LANDED rigor)**: SOP procedure empirically executed twice — at v3.16.0 scope-lock (commit `91c5871` 2026-05-02) and v3.17.0 scope-lock (commit `e50a182` 2026-05-09); both ceremonies generated the cycle outcomes the SOP predicts (PLANNING → READY FOR RELEASE state transition; principal-GO form contract recorded; cluster anti-pattern self-application audit clearance). Theme C3 self-conformance: this SOP codifies the very 4-gate ceremony that v3.17 has just executed.

---

## Purpose

Standard operating procedure for the scope-lock ceremony — the structured 4-gate ritual that transitions `VERSION_SCOPE_vX.Y.Z.md` from `PLANNING` to `READY FOR RELEASE` (canonical R-REL-022-01) / `SCOPE_LOCKED` (L708 vernacular). The ceremony bounds the cycle's scope under principal-GO authorization, captures grooming dispositions, applies the anti-pattern cluster discipline to its own act (L908 self-application), and produces a structurally-coherent lock-event commit.

This SOP closes the meta-gap: lock-prep had L-docs (L708, L656, L465, L617, L131) + lock plans (per-cycle PROJECT_PLAN scope-lock instances) + critic memos but no canonical SOP per L808 ADR-008 progression (L-doc → SOP → Spec → Skill).

---

## When this SOP applies

| Trigger | Apply |
|---------|:-----:|
| Cycle's VERSION_SCOPE_vX.Y.Z is at `PLANNING` and grooming is converging | YES |
| Theme has been disposed (or is co-disposed during Gate 1) | YES |
| L656 Loading Dock is cleared (prior version deployed to ≥1 downstream) | YES |
| Lock-event commit has NOT yet landed | YES |
| Cycle is in `SCOPE_LOCKED` or later state | NO — release-build SOP applies |
| L656 Loading Dock NOT cleared | NO — verify deployment first |

---

## Prerequisites

Before invoking this SOP:

1. **L656 Loading Dock cleared** — prior version deployed to ≥1 downstream agent confirmed via handoff pilot tracking table.
2. **VERSION_SCOPE_vX.Y.Z.md exists** at PLANNING status with candidate inventory.
3. **PROJECT_PLAN_vX.Y.Z_scope_lock_v1.0.md scaffolded** via `/aget-create-project` (STRUCTURAL — D71 Layer 1).
4. **Anti-pattern cluster identified** — current cluster is 11 L-docs (L908+L909+L910+L912+L913+L916+L922+L935 original 8; L671+L869+L894 added v1.1.0 of v3.17 lock plan). Update if cycle has identified new members.
5. **Spec-fault dispositions** known — any OPEN spec faults (e.g., #1179, #1180) noted; same disposition strategy as prior cycle unless amended.
6. **Tracking issue filed** in `gmelli/aget-aget` (per L638 private-first routing).

---

## The 4-Gate Ceremony

```
Gate -1: Governing Spec Verification + L656 + Structural Pulse
   ↓
Gate 0:  Lock-Prep Synthesis + Self-Application Audit + Freshness Pass
   ↓
Gate 1:  WSJF Grooming + Theme Alignment + AM1 Distributed Critic + Pre-LOCK Inbound-Issue Review
   ↓
Gate 2:  Lock Event + Canonical Status Write + Principal GO Capture + Final-Gate Critic
```

Each gate has: deliverables (checkbox list), V-tests (executable bash), Triad checkpoint (Builder + Auditor + Critic perspectives), and a Decision Point (proceed/halt).

### Gate -1: Governing Spec Verification + L656 + Structural Pulse

**Objective**: Verify governing specs read, deployment confirmed, structural artifacts exist.

**Deliverables**:
- [ ] G-1.1: Read `AGET_PROJECT_PLAN_SPEC` current version (verify CAP-PP-001..019 conformance)
- [ ] G-1.2: Read `AGET_RELEASE_SPEC`; record disposition for any OPEN spec faults
- [ ] G-1.3: L656 Loading Dock clearance — confirm prior-version deployment via handoff pilot tracking
- [ ] G-1.4: Structural pulse on `VERSION_SCOPE_vX.Y.Z.md` — every cited `planning/*.md` path exists
- [ ] G-1.5: Canonical-vs-private sweep — lock plan has ≥3 CANONICAL/PRIVATE markers (L910)
- [ ] G-1.6: Freshness-audit memo present (per cycle convention)
- [ ] G-1.7: AM3 — Predecessor deprecation-promise verification (grep last 2 cycles' RELEASE_HANDOFF; verify each promise landed or grace-extended)

**V-tests** (representative):

```bash
# V-1.1: Governing spec exists
test -f /path/to/aget/specs/AGET_PROJECT_PLAN_SPEC.md && echo PASS

# V-1.2: OPEN spec faults stable
gh issue view <fault-id> --json state -q .state  # expect known status

# V-1.3: L656 evidence
gh issue view <fleet-upg-id> --json title -q .title | grep -c "<expected fleet count>"

# V-1.4: Structural pulse
for path in $(grep -oE 'planning/[^ )]+\.md' planning/VERSION_SCOPE_vX.Y.Z.md); do
  test -f "$path" || echo "MISSING: $path"
done

# V-1.5: Canonical/private markers
grep -cE "(CANONICAL|PRIVATE)" planning/PROJECT_PLAN_vX.Y.Z_scope_lock_v1.0.md  # expect ≥3
```

**Triad checkpoint**: Builder executes V-tests + spec reads. Auditor validates marker count + structural pulse. Critic deferred to Gate 0 G0.3 distributed invocation per L131.

**Decision Point**: Proceed to Gate 0 if all V-tests PASS and ≤1 minor finding (route to v3.YY+1 P2).

### Gate 0: Lock-Prep Synthesis + Self-Application Audit + Freshness Pass

**Objective**: Apply the anti-pattern cluster (currently 11 L-docs) to the lock-prep act itself (L908 self-application). Synthesize lock-prep inputs into a single readiness assessment. Produce VERSION_SCOPE annotation-only pass per L850.

**Deliverables**:
- [ ] G0.1: Push-window outcomes verified (no Mon-Fri pushes since prior release per L735)
- [ ] G0.2: Consolidation audit — no duplicate PROJECT_PLANs targeting this version (L465)
- [ ] G0.3: **Self-application audit** — broader release-patterns/misses survey via distributed Critic (general-purpose Agent-tool subagent with sealed prompt)
- [ ] G0.4: Canonical-vs-private comprehensive sweep — file L910 findings if marker count low
- [ ] G0.5: VERSION_SCOPE annotation-only pass per L850 — NO Tier movements; NO new-candidate promotions; absorbs status drifts + new items as annotations only
- [ ] G0.6: Lock-readiness briefing authored at `planning/vX.Y.Z_lock_readiness_briefing.md`

**Distributed Critic invocation** (G0.3):

The Critic perspective MUST be invoked via the Agent tool with a sealed prompt and a prompt_hash recorded in `planning/triad_findings.jsonl`. Label-only verification is insufficient (per F-CRITIC-009 v3.16; AM1 v1.1.0 amendment of v3.17 lock plan). The prompt_hash is the structural proof that distributed Critic actually executed.

```bash
# Compute prompt_hash for the AM1 invocation
echo -n "v3YY-G0-AM1-distributed-critic-YYYY-MM-DD" | sha256sum | cut -c1-12
# Record in triad_findings.jsonl with key "prompt_hash"
```

**V-tests** (representative):

```bash
# V-0.3: Critic perspective with prompt_hash evidence
grep -c '"prompt_hash":' planning/triad_findings.jsonl  # expect ≥1

# V-0.5: Annotation pass landed
grep -c "v0.6.4" planning/VERSION_SCOPE_vX.Y.Z.md  # or current annotation version

# V-0.6: Lock-readiness briefing exists
test -f planning/vX.Y.Z_lock_readiness_briefing.md && echo PASS
```

**Mid-gate checkpoint** (CAP-PP-019-03, 50% = after G0.3): If G0.3 surfaces ≥3 self-application findings, cap recursion at L131 (max 2 amendment passes) and route remaining to v3.YY+1 P2.

**Decision Point**: Proceed to Gate 1 if G0.3 self-application audit surfaces ≤2 material findings (or ≥3 with explicit deferral routing).

### Gate 1: WSJF Grooming + Theme Alignment + AM1 Distributed Critic + Pre-LOCK Inbound-Issue Review

**Objective**: Resolve all pending grooming dispositions with theme-coherence check. Convert candidate inventory + new items into Tier 1/2/3 placement. Verify each Tier 1/2 item against theme alignment or mark theme-orthogonal carry-forward.

**Deliverables** (representative):
- [ ] G1.1..G1.N: Capture each grooming-question disposition (Q1, Q2, ..., QN)
- [ ] G1.WSJF: WSJF Tier 1/2/3 placement — produce groomed VERSION_SCOPE vX.Y.Z (e.g., v0.6.4 → v0.7.0)
  - **AM2 quantitative demotion trigger**: if ΣSU(Tier 1) > cycle-cap (default 65 SU per L708), invoke principal-decide demotion rubric. Pre-list demotion candidates in grooming-decision-packet.
- [ ] G1.THEME: Theme alignment check — every Tier 1/2 item tagged for theme-coherence OR explicitly tagged "theme-orthogonal" with rationale; demote any incoherent item to Tier 3
- [ ] G1.CRITIC: AM1 distributed Critic invocation with prompt_hash evidence (per Gate 0 pattern)
- [ ] G1.INBOUND: **Pre-LOCK inbound-issue review** (NEW per T2.18 v0.7.5)

#### Pre-LOCK Inbound-Issue Review Step (G1.INBOUND)

**Why mandatory** (closes F-V317-G1-009, L913 instance at inbound-issue surface):

The freshness-audit pass at Gate 0 captures inbound issues at *that* timestamp. Issues filed AFTER the freshness audit but BEFORE lock-event landing get missed unless explicitly re-checked. The v3.17 cycle empirically demonstrated this: 7-of-10 issues filed since the prior freshness audit were missed by the AM1 mid-gate Critic and surfaced only by post-Gate-1-closure principal directive.

**Procedure**:

1. **Recency-aware query** — list all issues filed in the tracking repo since the freshness-audit timestamp:

   ```bash
   # Replace <since-timestamp> with the freshness-audit memo's timestamp
   gh issue list --repo gmelli/aget-aget --state open --limit 30 \
       --json number,title,createdAt,labels \
       --jq 'sort_by(.createdAt) | reverse | .[] |
           select(.createdAt > "<since-timestamp>") |
           "\(.createdAt[:10]) #\(.number) \(.title)"'
   ```

2. **Per-issue disposition** — for each issue, decide:

   | Disposition | Trigger | Action |
   |-------------|---------|--------|
   | **ABSORB** as new Tier-1/2 item | Issue scope is in-cycle + theme-aligned | Add row to VERSION_SCOPE candidate table; cite issue # |
   | **ABSORB in-place** to existing item | Issue refines existing candidate | Edit existing row; cite issue # in the description |
   | **VERIFY COVERED** | Issue is already addressed by sibling plan or existing item | Annotate verification in VERSION_SCOPE Version Log |
   | **DEFER to next cycle** | Out-of-cycle scope; non-critical | Add row to Tier 3 with deferral target version |
   | **CLOSE** | Issue is admin-class (e.g., previously-completed plan tracking) | `gh issue close` with referencing commit |

3. **Carry-forward absorption table** — record dispositions in VERSION_SCOPE Version Log entry:

   ```markdown
   | <new-version> | <date> | **Pre-LOCK inbound-issue review pass**. Reviewed inbound queue since <since-timestamp>: gh#NNNN → ABSORB → T2.X (description); gh#MMMM → DEFER vNEXT; gh#KKKK → VERIFY COVERED via <plan>. Tier 2 +X SU; Tier 1 unchanged. svc-ed-d triad+diligence PASS. |
   ```

4. **Self-demonstrating closure**: this G1.INBOUND step IS the procedure the SOP codifies; executing it produces evidence of the SOP's value.

**V-tests**:

```bash
# V-1.INBOUND.1: All since-timestamp issues dispositioned
gh issue list --repo gmelli/aget-aget --state open --limit 30 \
    --jq '.[] | select(.createdAt > "<since-timestamp>") | .number' \
| while read num; do
    grep -q "gh#$num\|#$num" planning/VERSION_SCOPE_vX.Y.Z.md \
      || echo "UNDISPOSITIONED: #$num"
  done
# expect no UNDISPOSITIONED output
```

**Decision Point** (Gate 1 close): Proceed to Gate 2 if Tier 1 SU ≤ cycle cap AND theme alignment confirmed AND all inbound issues dispositioned.

### Gate 2: Lock Event + Canonical Status Write + Principal GO Capture + Final-Gate Critic

**Objective**: Execute the lock-event transition.

**Deliverables**:
- [ ] G2.1: Update `VERSION_SCOPE_vX.Y.Z.md` Status field to canonical `READY FOR RELEASE` + record `lock_event: SCOPE_LOCKED <ISO timestamp>` annotation
- [ ] G2.2: Capture explicit principal GO line in plan + session file: form contract = `"GO vX.YY scope-lock <ISO timestamp>"` (verbatim grep target)
- [ ] G2.3: Commit lock event with structured message: `vX.YY scope lock: VERSION_SCOPE v0.X.Y → v1.0.0 — theme <theme-name>; <N> dispositions captured; GO recorded <timestamp>`
- [ ] G2.4: Final-gate Critic invocation (REQUIRED per RUBRIC override at final gates)

**Principal-GO form contract**:

The principal MUST issue the GO in the verbatim form `GO vX.YY scope-lock <ISO timestamp>`. Free-text "yes" / "proceed" / "do it" is REJECTED at this gate (per L466 Question Is Not Approval; L854 Spec-First Selective Application). The form contract is the audit anchor.

**V-tests**:

```bash
# V-2.1: Canonical status written
grep -c "READY FOR RELEASE" planning/VERSION_SCOPE_vX.Y.Z.md  # expect ≥1

# V-2.2: L708 lock-event annotation
grep -cE "lock_event:.*SCOPE_LOCKED" planning/VERSION_SCOPE_vX.Y.Z.md  # expect ≥1

# V-2.3: Principal GO form contract
grep -cE "GO v[0-9]+\.[0-9]+ scope-lock [0-9]{4}-[0-9]{2}-[0-9]{2}" \
    planning/PROJECT_PLAN_vX.Y.Z_scope_lock_v1.0.md  # expect ≥1

# V-2.4: Lock-event commit landed
git log --oneline -1 | grep -c "scope lock"  # expect 1

# V-2.5: Locked version landed
grep -c "v1.0.0" planning/VERSION_SCOPE_vX.Y.Z.md  # expect ≥1
```

**Decision Point**: Lock complete. Plan transitions to `Plan_Status: Complete`. Downstream: scaffold `PROJECT_PLAN_vX.Y.Z_release_v1.0.md` (separate session, separate GO).

---

## Anti-Pattern Cluster Self-Application Audit

The cluster is the set of L-docs whose anti-patterns the lock-prep ceremony itself MUST NOT recur. Current cluster (11 L-docs):

| L-doc | Anti-Pattern | Self-Application |
|-------|--------------|------------------|
| L908 | Apply-to-Others-Not-Self | Cluster discipline applied to lock-prep act itself, not just routed as fixes for next cycle |
| L909 | Under-Sanitization at CHANGELOG Write Time | Reserve retrospective + finalization sections; populate at close |
| L910 | Canonical-vs-Private Artifact Relationship | All citations marked CANONICAL/PRIVATE explicitly |
| L912 | Container-Verb Anti-Pattern | State names use descriptive past-participle (RELEASED, SCOPE_LOCKED), not intransitive -ING |
| L913 | Plan-Close → Plan-Create Handoff Discovery Gap | Pre-LOCK inbound-issue review (G1.INBOUND) closes this |
| L916 | Spec-Claimed-Delegate-Without-Implementation | V-tests verify delegate execution, not just creation |
| L922 | Recursive Coverage Gap | Explicit theme-deliverable composition check at G1.THEME |
| L935 | Wired Validator Synecdoche | V-tests verify the requirement scope, not a strict subset |
| L671 | Classification-Without-Consequence | All grace-extends have explicit V-tests verifying registry update |
| L869 | (cycle-specific) | Per cycle disposition |
| L894 | (cycle-specific) | Per cycle disposition |

**Self-application discipline**: BEFORE Gate 2, verify NO cluster member's anti-pattern is recurring within the lock-prep plan or VERSION_SCOPE. If found, route to in-flight fix at amendment cap (L131: 2 passes max).

---

## Common Pitfalls / Red Flags

| Red Flag | Anti-Pattern | Response |
|----------|--------------|----------|
| Gate 1 deliverables `[x]` without VERSION_SCOPE evidence | L908 self-application discipline gap | Phase A audit pass; mark `[x]` with V-test result citation |
| Free-text "yes" / "proceed" treated as GO at Gate 2 | L466, L854 | REJECT; require form-contract verbatim |
| Annotation pass introduces new-candidate items | L850 violation | Convert to grooming-pass version (vX.Y+1 not vX.Y.Z+1) |
| Distributed Critic claimed but no prompt_hash | F-CRITIC-009 (v3.16); AM1 fix | Re-invoke Critic with sealed prompt + record hash |
| Lock event commits with cluster anti-pattern recurrence | L908 self-application falsified | Block; remediate at amendment cap |
| Inbound issues since freshness audit not reviewed | F-V317-G1-009 (L913 inbound-surface) | Execute G1.INBOUND before Gate 2 entry |

---

## Authorization & Push Window

**Authorization at lock event**: Principal `/aget-go` with form-contract verbatim. The lock event is a STRUCTURAL state transition; bare `/aget-go` is sufficient when scope is unambiguous (only one PROJECT_PLAN scope-lock in flight).

**Public push window** (L735): The lock event is a *commit*, not a *push*. Lock-event commits land at the time of the ceremony (any day). The cycle's release push (downstream of this SOP) honors the weekend-only public-push window.

---

## Related Artifacts

| Artifact | Relation |
|----------|----------|
| `PROJECT_PLAN_vX.Y.Z_scope_lock_v1.0.md` | Per-cycle instance of this SOP |
| `VERSION_SCOPE_vX.Y.Z.md` | Target artifact (state transition target) |
| `vX.Y.Z_lock_readiness_briefing.md` | Gate 0 G0.6 deliverable |
| `MEMO_vX.Y.Z_freshness_audit_*.md` | Gate 0 G0.5 input |
| `MEMO_vX.Y.Z_grooming_decision_packet_*.md` | Gate 1 input |
| `MEMO_vX.Y.Z_release_patterns_research_*.md` | Gate 0 G0.3 distributed-Critic output |
| `planning/triad_findings.jsonl` | Per-cycle Critic findings registry (with prompt_hash) |
| `handoffs/RELEASE_HANDOFF_vX.Y.Z.md` | Downstream artifact (post-release) |
| `governance/POLICY_deprecation.md` | R-DEP grace mechanism reference for sleeping-CAP dispositions |
| `sops/SOP_release_process.md` | Downstream SOP (release execution after lock) |

---

## V-test Roll-up

Single command to verify SOP conformance for a completed lock cycle:

```bash
# Run from cycle's PROJECT_PLAN directory
verify_scope_lock_ceremony() {
  local v="$1"  # e.g. "v3.17.0"
  local plan="planning/PROJECT_PLAN_${v}_scope_lock_v1.0.md"
  local scope="planning/VERSION_SCOPE_${v}.md"

  # Gate 2 essentials
  grep -q "READY FOR RELEASE" "$scope" || { echo "FAIL: Gate 2 status"; return 1; }
  grep -qE "lock_event:.*SCOPE_LOCKED" "$scope" || { echo "FAIL: L708 annotation"; return 1; }
  grep -qE "GO ${v%.0} scope-lock [0-9]{4}-[0-9]{2}-[0-9]{2}" "$plan" \
    || { echo "FAIL: principal-GO form contract"; return 1; }
  grep -q "v1.0.0" "$scope" || { echo "FAIL: locked version"; return 1; }

  # Distributed Critic evidence
  grep -q '"prompt_hash":' planning/triad_findings.jsonl \
    || { echo "FAIL: distributed Critic prompt_hash"; return 1; }

  # Cluster self-application — no [ ] deliverables in Complete gates
  awk '/^### Gate/{in_gate=1; gate=$0; next}
       /^\*\*Gate_Status\*\*: Complete/{complete=1; next}
       /^- \[ \]/{if(in_gate && complete) print "FAIL: unchecked deliverable in", gate; bad=1}
       /^---/{in_gate=0; complete=0}
       END{exit bad}' "$plan"

  echo "PASS: $v scope-lock ceremony verified"
}
```

---

## Traceability

| Link | Reference |
|------|-----------|
| L-docs | L708 (Scope-Lock state machine), L656 (Loading Dock), L465 (Scope Consolidation), L131 (amendment cap), L850 (annotation-only), L908 (Apply-to-Others-Not-Self), L913 (Plan-Close → Plan-Create handoff), L935 (Wired Validator Synecdoche), L671 (Classification w/o Consequence) |
| ADRs | ADR-005 (Gates as release points), ADR-008 (Advisory → Strict → Generator) |
| Specs | AGET_RELEASE_SPEC R-REL-022-01, CAP-REL-029; AGET_PROJECT_PLAN_SPEC v1.2.3 |
| Predecessors | `PROJECT_PLAN_v3.16.0_scope_lock_v1.0.md` v1.1.2; `PROJECT_PLAN_v3.17.0_scope_lock_v1.0.md` v1.1.1 |
| VERSION_SCOPE entries | T2.18 (this SOP), T2.19 (`AGET_SKILL_LIFECYCLE_SPEC`), T2.20 (`AGET_FLEET_UPGRADE_SPEC`), T2.23 (`AGET_TASK_ROUTING_SPEC`) — sibling spec-authoring cluster at canonical-coherence-at-governance-layer |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-05-09 | Initial draft — extracted from v3.16+v3.17 lock plan evidence; includes pre-LOCK inbound-issue review step (G1.INBOUND) per T2.18 v0.7.5 mandate; closes F-V317-G1-009 absorption-gap structural prevention path. Authored as Action 3 of /aget-propose-actions --budget=4h batch (auth /aget-go 2026-05-09T13:00 PT). |
| 1.0.0 | 2026-05-09 | **LANDED promotion** via v3.17.0 release plan G1.5.1 (T2.18 deliverable per VERSION_SCOPE_v3.17.0 Q-G1.5-2). Status: DRAFT → LANDED. Empirical grounding: SOP procedure was executed twice (v3.16 scope-lock 2026-05-02; v3.17 scope-lock 2026-05-09T13:28:03-0700) before LANDED rigor declared — both executions produced predicted outcomes. Canonical promotion: copied to `aget-framework/aget/sops/SOP_scope_lock_ceremony.md` per T2.16 Q7=β procedure. Cross-reference added to `aget-framework/aget/sops/SOP_release_process.md` Phase 1 (Scope-Lock entry point). Authored under /aget-go batch authorized 2026-05-09T~19:55 PDT (session_2026-05-09_1955 release record). Theme C3 self-conformance: this SOP codifies the very ceremony executed at v3.17 lock event. |
