# SOP: Scope-Lock Ceremony

**Version**: 1.7.1
**Status**: LANDED
**Created**: 2026-05-09
**Updated**: 2026-07-17 (v1.7.0 → v1.7.1 — **anti-pattern cluster currency fix**: the SOP carried "11 L-docs" at three sites while its own §table listed 12, and the v3.26 additions (L1155/L1158/L1160, recorded only in VERSION_SCOPE_v3.26.0 prereq #4) never propagated back — an L1188 instance (stored registry not read) inside the SOP that defines the cluster. True count 15, all members re-verified on disk 2026-07-17. Fix: §Anti-Pattern Cluster table becomes the single membership source of truth; prereq #4 and Gate 0 reference it instead of restating counts; L1155/L1158/L1160 rows added; v3.27 addition candidates L1168/L1187/L1188/L1190 staged pending Gate-0 stamp. See `planning/MEMO_v3.27_freshness_audit_2026-07-17.md`. Prior 2026-07-11 v1.6.0 → v1.7.0 — adds Gate 1 **G1.PORTFOLIO**: per-release initiative-portfolio grooming pass (agent-prepared close-candidate/re-authorize/suspend verdicts per ACTIVE, D-IG-3) + **prior-cycle VERSION_SCOPE §Deferred ingest** with PROCEED/RE-DEFER/DROP dispositions (gh#1536 deferral backpressure; L1002 cheapest non-recursive edge). Prior v1.5.0 → v1.6.0 — adds **G1.SELECT board design requirement 7**: predicted-value (V1) selection column, HYBRID threshold-gated per D-RP-13 / gmelli/aget-aget#1758 — value-contribution legible at the moment of selection, distinct-axis-never-summed; tooling column render OWED #1758/#1649. Prior v1.4.0 → v1.5.0 — adds Gate 1 **G1.VALUEGATE** blocking value-to-ship gate per POL-REL-001 v1.1.0 R-REL-CAD-008 / decision D-RP-4; the prework enforcement of substance-gated cadence — stops a v3.23.0-class dominated-thin lock at scope-lock, not post-ship). Prior: 2026-06-12 v1.3.0 → v1.4.0 — Gate 1 **G1.SELECT** principal scope-selection via cycle-current interactive control board; closes L824. v1.2.0 → v1.3.0 2026-05-23 — G1.AUDIT audit-after-synthesis pairing; L980 / gh#1476)
**Owner**: private-aget-framework-AGET (canonical-promoted to `aget-framework/aget/sops/SOP_scope_lock_ceremony.md` at v1.0.0; v1.1.0/v1.2.0/v1.3.0 canonical sync deferred to next public push window per L735 — `origin = aget-framework/*` applies)
**Implements**: R-REL-022-01 (Lock-Event Status Transition), CAP-REL-029 (Lock-Event Protocol)
**Governing**: PROJECT_PLAN scope-lock plans (v3.16, v3.17 cycles); VERSION_SCOPE_vX.Y.Z lifecycle state machine (L708)
**Source Evidence**: `planning/archive/PROJECT_PLAN_v3.16.0_scope_lock_v1.0.md` v1.1.2 (Complete); `planning/archive/PROJECT_PLAN_v3.17.0_scope_lock_v1.0.md` v1.1.2 (Complete); `MEMO_v3.17_release_patterns_research_2026_05_09.md`; `MEMO_v3.17_freshness_audit_2026_05_09.md`; v3.17.0 release plan v1.0.18 (lock event commit `e50a182` 2026-05-09T13:28:03-0700)
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
4. **Anti-pattern cluster identified** — membership is enumerated ONLY in §Anti-Pattern Cluster Self-Application Audit (single source of truth; do not restate counts here — the inline "11" this line carried went stale twice, v1.7.1 audit 2026-07-17). Update the §table if the cycle has identified new members; the cycle's VERSION_SCOPE prereq row cites the additions.
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

**Objective**: Apply the anti-pattern cluster (membership per §Anti-Pattern Cluster Self-Application Audit) to the lock-prep act itself (L908 self-application). Synthesize lock-prep inputs into a single readiness assessment. Produce VERSION_SCOPE annotation-only pass per L850.

**Deliverables**:
- [ ] G0.1: Push-window outcomes verified (no Mon-Fri pushes since prior release per L735)
- [ ] G0.2: Consolidation audit — no duplicate PROJECT_PLANs targeting this version (L465)
- [ ] G0.3: **Self-application audit** — broader release-patterns/misses survey via distributed Critic (general-purpose Agent-tool subagent with sealed prompt)
- [ ] G0.4: Canonical-vs-private comprehensive sweep — file L910 findings if marker count low
- [ ] G0.5: VERSION_SCOPE annotation-only pass per L850 — NO Tier movements; NO new-candidate promotions; absorbs status drifts + new items as annotations only
- [ ] **G0.5a: Freshness-audit cadence check (v1.1.0)** — confirm `MEMO_vX.Y.Z_freshness_audit_*.md` is ≤7 days old AND no >20-inbound-issue burst has occurred since it was authored; if either threshold exceeded, re-run audit before proceeding to Gate 1
- [ ] **G0.5b: Rubric currency check (v1.3.0 — added 2026-05-16 per B6/INIT-RELEASE-CYCLE-STEWARDSHIP CAP-RCS-004)** — inventory rubrics cited by VERSION_SCOPE_vX.Y.Z.md; for each rubric file in `rubrics/RUBRIC_*.md` cited by current cycle, check `**Last reviewed**:` header field. If > 1 cycle stale OR field absent, surface for review before Gate 1 entry. If `**Status**: Draft` and rubric has been used in ≥1 prior cycle, surface for promotion review. Route review decisions to owning initiative (per rubric's `**Initiative**:` header field). Closes orphan-rubric pattern surfaced 2026-05-16 (RUBRIC_scope_item_priority Draft for 6 cycles unreviewed).
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

# V-0.5a (v1.1.0): Freshness-audit cadence check
audit_age_days=$(( ($(date +%s) - $(stat -f %m docs/MEMO_vX.Y.Z_freshness_audit_*.md 2>/dev/null | sort -n | tail -1)) / 86400 ))
test "$audit_age_days" -le 7 || { echo "FAIL: freshness audit $audit_age_days days old (>7)"; exit 1; }
# Inbound-burst check: count issues since freshness-audit timestamp
since=$(stat -f %SmY-%Sm%d docs/MEMO_vX.Y.Z_freshness_audit_*.md 2>/dev/null | tail -1)
inbound_count=$(gh issue list --repo gmelli/aget-aget --state open --search "created:>=$since" --limit 100 --json number --jq 'length')
test "$inbound_count" -le 20 || { echo "FAIL: $inbound_count inbound issues since audit (>20)"; exit 1; }

# V-0.5b (v1.3.0): Rubric currency check — every rubric cited by VERSION_SCOPE has Last reviewed and Status fields, not stale beyond 1 cycle
for r in $(grep -oE 'rubrics/RUBRIC_[a-z_]+\.md' planning/VERSION_SCOPE_vX.Y.Z.md | sort -u); do
  test -f "$r" || { echo "MISSING: $r cited but not on disk"; continue; }
  reviewed=$(grep -E '^\*\*Last reviewed\*\*:' "$r" | head -1)
  status=$(grep -E '^\*\*Status\*\*:' "$r" | head -1)
  initiative=$(grep -E '^\*\*Initiative\*\*' "$r" | head -1)
  test -n "$reviewed" || echo "WARN: $r missing **Last reviewed** field"
  test -n "$initiative" || echo "WARN: $r missing **Initiative** field (owner unknown)"
  # surface for review if reviewed > 1 cycle (heuristic: ~30 days)
done

# V-0.6: Lock-readiness briefing exists
test -f planning/vX.Y.Z_lock_readiness_briefing.md && echo PASS
```

**Mid-gate checkpoint** (CAP-PP-019-03, 50% = after G0.3): If G0.3 surfaces ≥3 self-application findings, cap recursion at L131 (max 2 amendment passes) and route remaining to v3.YY+1 P2.

**Decision Point**: Proceed to Gate 1 if G0.3 self-application audit surfaces ≤2 material findings (or ≥3 with explicit deferral routing).

### Gate 1: WSJF Grooming + Theme Alignment + AM1 Distributed Critic + Decide-Packet Preparation + Pre-LOCK Inbound-Issue Review

**Objective**: Resolve all pending grooming dispositions with theme-coherence check. Convert candidate inventory + new items into Tier 1/2/3 placement. Verify each Tier 1/2 item against theme alignment or mark theme-orthogonal carry-forward.

**Deliverables** (representative):
- [ ] G1.1..G1.N: Capture each grooming-question disposition (Q1, Q2, ..., QN)
- [ ] G1.WSJF: WSJF Tier 1/2/3 placement — produce groomed VERSION_SCOPE vX.Y.Z (e.g., v0.6.4 → v0.7.0)
  - **AM2 quantitative demotion trigger**: if ΣSU(Tier 1) > cycle-cap (default 65 SU per L708), invoke principal-decide demotion rubric. Pre-list demotion candidates in grooming-decision-packet.
- [ ] **G1.SELECT: Principal scope selection via interactive control board (NEW v1.4.0 — MANDATORY)** — principal makes Tier/selection decisions through a **cycle-current** HTML control board generated from the VERSION_SCOPE candidate inventory; the board's exported `SCOPE_LOCK` block is captured verbatim as the selection record and persisted back into VERSION_SCOPE. The board surfaces each candidate's **predicted functional-value (V1)** beside WSJF as a binding selection input for flagship/Tier-1/≥8-SU items (NEW v1.6.0 — D-RP-13; see §Board design requirement 7). See §Principal Scope-Selection Step below.
- [ ] G1.THEME: Theme alignment check — every Tier 1/2 item tagged for theme-coherence OR explicitly tagged "theme-orthogonal" with rationale; demote any incoherent item to Tier 3
- [ ] **G1.VALUEGATE: Value-to-ship gate (NEW v1.5.0 — 2026-06-26; POL-REL-001 R-REL-CAD-008 / D-RP-4)** — evaluate the selected/groomed Tier-1 against `RUBRIC_release_value_cost` **CON-FLOOR** (≥1 item V1=L3 AND functional items V1≥L2 ΣSU ≥33%) **and CON-CAPABILITY-SHARE** (≥⅓ ΣSU capability-facing). **BLOCKING**: if either constraint is unmet, the lock HOLDS — the cycle does not proceed toward public release until the scope clears the bar OR the principal records an L178 override with reason. This is the *prework enforcement* of the substance-gated cadence (R-REL-CAD-007) — stop a v3.23.0-class dominated-thin lock at scope-lock, not post-ship (REQ-R). It pairs with G0.5b (rubric currency): G0.5b ensures the *rubric* is fresh; G1.VALUEGATE applies it as a *blocking constraint* on the selected scope. See §Value-to-Ship Gate Step below.
- [ ] G1.CRITIC: AM1 distributed Critic invocation with prompt_hash evidence (per Gate 0 pattern)
- [ ] **G1.DECIDE: Cross-cycle Decide-Packet preparation (NEW v1.1.0)** — consolidate accumulated initiative-portfolio Decide gates into a single principal-facing packet
- [ ] G1.INBOUND: **Pre-LOCK inbound-issue review** (NEW per T2.18 v0.7.5)
- [ ] **G1.AUTHORED: Pre-LOCK in-repo authored-substrate review (NEW v1.2.0)** — disposition PROPOSALs, initiative manifests, and L-doc candidates authored since the freshness-audit timestamp (closes gh#1374; sibling of G1.INBOUND, distinct concern: in-repo authored artifacts vs GitHub issues)
- [ ] **G1.AUDIT: Audit-after-synthesis pairing (NEW v1.3.0 — L980 / gh#1476 Healthy Friction codification, Channel 2 point-of-use)** — Gate 1 writes synthesis-class rows to governed artifacts (VERSION_SCOPE Tier placement, INDEX.md grooming dispositions, INBOUND/AUTHORED disposition tables). Before Gate 1 close, perform an audit-class action that **re-derives every count/ΣSU/roster claim from primary sources — NOT from the narrative just written**. See §Audit-After-Synthesis Pairing Step below.
- [ ] **G1.PORTFOLIO: Initiative-portfolio grooming pass + deferral ingest (NEW v1.7.0 — D-IG-3 + gh#1536)** — two halves, both MANDATORY at Gate 1:
  1. **Portfolio pass (D-IG-3)**: run `python3 scripts/check_initiatives.py`; for EVERY ACTIVE initiative, the agent pre-computes a verdict — **close-candidate** (Exit Conditions near-met → route to `/aget-close-initiative`), **re-authorize** (live work, window re-stamped with this ceremony as the recorded Decide), or **suspend** (→ DORMANT). The principal rules on exceptions only. Maintain-typed initiatives are judged against their `## Health Contract` (breach → dated Achieve recovery item), never against done-dates. Ratio/spine/aging signals from the rollup are the verdict inputs.
  2. **Deferral ingest (gh#1536)**: read cycle N-1's `VERSION_SCOPE §Deferred`; every deferred item receives an explicit disposition — **PROCEED** (into this cycle's scope) / **RE-DEFER** (rationale + new target) / **DROP** (rationale). An item with no disposition = Healthy Friction violation (L178 override available). This is the cheap non-recursive edge that breaks the L1002 bootstrap loop (the v3.19→v3.20 initiative-stream slip class).
  Requirements basis: D-IG-3 (INIT-INITIATIVE-MATURATION §F-2026-07-11-A); staged spec R-INIT-REVIEW-001; first executed manually as the 2026-07-11 G3 disposition packet (D-IG-5..9).

#### Cross-Cycle Decide-Packet Preparation Step (G1.DECIDE)

**Why mandatory** (v1.1.0 addition; closes scattered-Decide-gates structural gap):

Decide gates accumulate between releases — surfaced in BRIEF/MEMO/PROPOSAL/initiative-INDEX-Findings artifacts but NOT consolidated into a principal-facing packet. The v3.18 cycle empirically demonstrated this: 10 distinct pre-plan Decide gates were scattered across `docs/BRIEF_initiative_decide_gates_2026-05-14.md` (6 gates), `docs/MEMO_init_principled_execution_decide_2026-05-14.md` (3 gates), and `planning/VERSION_SCOPE_vX.Y.Z.md` (2 grooming preconditions) — requiring principal to reassemble 9 separate documents to act.

G1.INBOUND covers inbound *GitHub issues* (issue-class dispositions). G1.DECIDE covers cross-cycle *initiative-portfolio* gates (initiative-class, theme-class, fork-class, taxonomy-class) — distinct concern, distinct procedure.

**Procedure**:

1. **Survey Decide-class artifacts since prior release** — list all artifacts containing pending Decide gates:

   ```bash
   # Decide-bearing artifact patterns since prior version release
   prior_release_date="<YYYY-MM-DD of prior vX.Y-1.0 ship>"
   find docs/ -name "BRIEF_*.md" -o -name "MEMO_*decide*.md" -o -name "FINDING_*.md" \
       -newer <prior-release-anchor-file> 2>/dev/null
   grep -l "## Gate [0-9]\+" planning/initiatives/INDEX.md  # INDEX Findings as Decide gates
   ```

2. **Per-Decide-gate consolidation** — for each surfaced gate, classify and consolidate:

   | Class | Trigger | Action |
   |-------|---------|--------|
   | **Initiative-portfolio** | PROPOSED→ACTIVE / status transitions / scaffolding decisions | Surface in DECIDE_PACKET; agent recommends; principal decides |
   | **Theme/fork-class** | VERSION_SCOPE grooming preconditions (theme, fork) | Surface in DECIDE_PACKET; cite supporting memo if exists |
   | **Spec-priority** | Spec-fault prioritization (e.g., gh#NNNN spec-edit v3.X fold-in) | Surface in DECIDE_PACKET with effort estimate |
   | **Taxonomy/governance** | Vocabulary drifts, status-taxonomy conflicts | Surface in DECIDE_PACKET; cite finding doc |
   | **Already-Decided** | Decide gate exists but principal has resolved elsewhere | Annotate disposition + reference; do NOT re-surface |
   | **Out-of-scope** | Decides for next cycle or different agent | Annotate routing; do NOT surface |

3. **Author DECIDE_PACKET** at `docs/DECIDE_PACKET_vX.Y.Z_<YYYY-MM-DD>.md`:

   ```markdown
   # DECIDE PACKET: vX.Y.Z Pre-Plan — N Gates Consolidated

   **Author**: <agent name>
   **Source artifacts consolidated**: <list of BRIEF/MEMO/finding files>
   **Verified state**: <on-disk substrate pulls — manifest existence, file modtimes, etc.>

   ## TL;DR — N Gates, 1 Sequencing Recommendation
   | Gate | Topic | Recommendation | Principal Effort |
   ...

   ## D-1, D-2, ..., D-N (one section per gate)
   ## Sequencing rationale
   ## Cross-Reference Trail
   ```

4. **V-test verification** — DECIDE_PACKET exists + cites all source artifacts + each gate has recommendation:

   ```bash
   # V-1.DECIDE.1: Packet exists
   ls docs/DECIDE_PACKET_vX.Y.Z_*.md | head -1 | xargs test -f && echo PASS

   # V-1.DECIDE.2: All source artifacts cited
   pkt=$(ls docs/DECIDE_PACKET_vX.Y.Z_*.md | head -1)
   for src in $(find docs/ -name "BRIEF_*decide*.md" -o -name "MEMO_*decide*.md" -newer <prior-anchor>); do
     grep -q "$(basename $src)" "$pkt" || echo "MISSING-SRC: $src"
   done

   # V-1.DECIDE.3: Each gate has recommendation
   pkt=$(ls docs/DECIDE_PACKET_vX.Y.Z_*.md | head -1)
   gates=$(grep -cE "^## D-[0-9]+" "$pkt")
   recs=$(grep -cE "^\*\*Recommendation\*\*:" "$pkt")
   test "$gates" -eq "$recs" || echo "FAIL: $gates gates / $recs recommendations"
   ```

5. **Principal-time-efficiency target**: A well-consolidated DECIDE_PACKET should reduce principal Decide effort to ~5-10 min per gate (consolidated framing + agent recommendation + trade-off table) — vs ~15-30 min per gate if Decides are scattered (requires re-reading source memo each time).

**V-tests**:

```bash
# V-1.DECIDE.1..3 per procedure above

# V-1.DECIDE.4: Sequencing recommendation present
grep -cE "^\*\*Sequencing\*\*:|^## Sequencing" docs/DECIDE_PACKET_vX.Y.Z_*.md 2>/dev/null
# expect ≥1
```

**Decision Point**: Proceed to G1.INBOUND if DECIDE_PACKET authored AND principal has been briefed (Decides may resolve before or after Gate 1 close, but the packet's existence is a Gate 1 deliverable).



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

**Decision Point** (Gate 1 close): Proceed to G1.AUTHORED if all inbound issues dispositioned; G1.AUTHORED is the sibling pass for in-repo authored substrate.

#### Pre-LOCK Authored-Substrate Review Step (G1.AUTHORED)

**Why mandatory** (v1.2.0 addition; closes gh#1374; sibling of L913):

G1.INBOUND covers inbound *GitHub issues* filed since the freshness-audit timestamp. It does NOT cover **in-repo authored substrate** filed between the freshness audit and lock event:

- `planning/project-proposals/PROPOSAL_*.md` (PP-### proposals)
- `planning/initiatives/INIT-*.md` (initiative manifests)
- `docs/CANDIDATE_LDOC_*.md` (L-doc candidates pre-promotion)

These artifacts slip past G1.INBOUND as currently scoped. The v3.18 pre-plan cycle (2026-05-12 → 2026-05-14 burst) empirically surfaced 11 such artifacts: 5 new PROPOSALs (PP-027..PP-032), 2 new initiative manifests, 4 L-doc candidates (L945..L948) — all would be undispositioned at scope-lock Gate 1 under v1.1.0 scope.

**Sibling layer in handoff-discovery family**:

| Layer | L-doc | Coverage |
|-------|-------|----------|
| Release → Deployment handoff | L656 | ✓ Covered |
| Release → Fleet handoff | L511 | ✓ Covered |
| Plan-Close → Plan-Create handoff | L913 | ✓ Covered (via SKILL-024 v1.3.0 REQ-PA-005a) |
| Cycle-N substrate-authoring → Cycle-N scope-lock pre-LOCK review | **(this step)** | ✓ Covered v1.2.0 |

**Procedure**:

1. **Recency-aware survey** — list authored substrate filed since the freshness-audit timestamp (anchor = freshness-audit memo file):

   ```bash
   audit_anchor="docs/MEMO_vX.Y.Z_freshness_audit_<YYYY-MM-DD>.md"

   # PROPOSALs authored since audit
   find planning/project-proposals/ -name "PROPOSAL_*.md" -newer "$audit_anchor"

   # Initiative manifests created/modified since audit
   find planning/initiatives/ -name "INIT-*.md" -newer "$audit_anchor"

   # L-doc candidates authored since audit
   find docs/ -name "CANDIDATE_LDOC_*.md" -newer "$audit_anchor"
   ```

2. **Per-artifact disposition** — mirror the G1.INBOUND class table (ABSORB / VERIFY-COVERED / DEFER / RETIRE):

   | Disposition | Trigger | Action |
   |-------------|---------|--------|
   | **ABSORB** as new Tier-1/2 item | Artifact scope is in-cycle + theme-aligned | Add row to VERSION_SCOPE candidate table; cite artifact path |
   | **ABSORB in-place** to existing item | Artifact refines existing candidate | Edit existing row; cite artifact path in description |
   | **VERIFY COVERED** | Artifact is already addressed by sibling plan or existing item | Annotate verification in VERSION_SCOPE Version Log |
   | **DEFER to next cycle** | Out-of-cycle scope; non-critical | Add row to Tier 3 with deferral target version |
   | **RETIRE** | Artifact is admin-class or superseded | Annotate disposition + reference; do NOT surface as candidate |

3. **Carry-forward absorption table** — record dispositions in VERSION_SCOPE Version Log entry, mirroring G1.INBOUND format:

   ```markdown
   | <new-version> | <date> | **Pre-LOCK authored-substrate review pass (G1.AUTHORED)**. Reviewed in-repo substrate authored since <audit-anchor>: PP-NNN → ABSORB → T2.X (description); INIT-XXX → DEFER vNEXT; L###-candidate → VERIFY COVERED via <plan>. Tier 2 +X SU; Tier 1 unchanged. |
   ```

4. **Self-demonstrating closure**: like G1.INBOUND, this G1.AUTHORED step IS the procedure the SOP codifies; executing it produces evidence of the step's value.

**V-tests**:

```bash
# V-1.AUTHORED.1: All since-anchor PROPOSALs dispositioned
audit_anchor="docs/MEMO_vX.Y.Z_freshness_audit_<YYYY-MM-DD>.md"
for f in $(find planning/project-proposals/ -name "PROPOSAL_*.md" -newer "$audit_anchor"); do
  grep -q "$(basename $f)" planning/VERSION_SCOPE_vX.Y.Z.md \
    || echo "UNDISPOSITIONED: $f"
done
# expect no UNDISPOSITIONED output

# V-1.AUTHORED.2: All since-anchor initiative manifests dispositioned
for f in $(find planning/initiatives/ -name "INIT-*.md" -newer "$audit_anchor"); do
  grep -q "$(basename $f)" planning/VERSION_SCOPE_vX.Y.Z.md \
    || echo "UNDISPOSITIONED: $f"
done

# V-1.AUTHORED.3: All since-anchor L-doc candidates dispositioned
for f in $(find docs/ -name "CANDIDATE_LDOC_*.md" -newer "$audit_anchor"); do
  grep -q "$(basename $f)" planning/VERSION_SCOPE_vX.Y.Z.md \
    || echo "UNDISPOSITIONED: $f"
done
```

#### Value-to-Ship Gate Step (G1.VALUEGATE)

**Why mandatory** (v1.5.0 addition; POL-REL-001 v1.1.0 R-REL-CAD-008 / decision D-RP-4, 2026-06-26):

Scope-lock historically optimized for *process* (theme coherence, WSJF placement, cap discipline) but did not enforce *value* at the lock boundary. v3.23.0 cleared every process gate and shipped a near-zero-capability dominated fleet-upgrade (REQ-R). The principal's hard-value-gate decision (D-RP-4) makes the rubric's functional floor a **blocking** lock constraint — caught here, as prework, rather than as a post-ship recalibration datum.

**Procedure**:
1. **Score the selected Tier-1** on `RUBRIC_release_value_cost` primary axis (V1 functional value), from pre-lock primary sources only (L960/L850 confabulation guard — score predicted, not narrated).
2. **Evaluate CON-FLOOR**: does the locked Tier-1 contain ≥1 item at V1=L3 (high-leverage, directly principal-consumed) AND do functional items (V1≥L2) sum to ≥33% of Tier-1 ΣSU?
3. **Evaluate CON-CAPABILITY-SHARE**: is ≥⅓ of Tier-1 ΣSU owned by capability-facing initiatives (not governance initiatives)? (initiative-class tags supplied at G1.SELECT.)
4. **Disposition**:
   - **Both met** → value-gate PASS; proceed.
   - **Either unmet** → **HOLD**: the lock does not proceed toward public release. Surface to the principal. Either re-scope to clear the bar (promote a capability item, defer governance bulk) OR the principal records an explicit **L178 override with reason** (the override is logged; the default is HOLD).
5. **Record** the value-gate disposition in the VERSION_SCOPE Version Log entry (PASS / HOLD / L178-override-with-reason).

**Coherence**: G1.VALUEGATE governs *whether the scope is worth shipping*; G1.AUDIT (below) governs *whether the scope's counts are true*; G0.5b governs *whether the scoring rubric is fresh*. Three distinct pre-lock guards — value, integrity, instrument-currency.

#### Audit-After-Synthesis Pairing Step (G1.AUDIT)

**Why mandatory** (v1.3.0 addition; L980 / gh#1476 Healthy Friction codification — Channel 2 point-of-use per L467):

Gate 1 is the ceremony's heaviest **synthesis surface**: G1.WSJF writes Tier-placement rows to VERSION_SCOPE, the per-Q grooming dispositions amend `planning/initiatives/INDEX.md`, and G1.INBOUND/G1.AUTHORED write multi-row disposition tables. Synthesis under composition pressure flattens conditional caveats and produces narrative-closure claims ("ΣSU 8→7 hits the ceiling", "ACTIVE count N→M", "Tier 1 = K items") that *feel* coherent but are not re-derived from primary sources.

L980 (2026-05-21) recorded the **first in-flight self-catch** of a false synthesis-layer count claim — caught *because* a later audit-class action re-touched the same artifact (`INDEX.md`) within the session. The pairing is the L908+L939+L960 verification chain's structural firing surface. Without it, a false count commits to the locked artifact and propagates to next-session wake-up. The v3.19 cycle executed this ad hoc as `G1.AUDIT-COUNTS` (caught an "ACTIVE 8→7" near-miss + corrected AUTHORED "~30"→32); v1.3.0 promotes it to a standing step.

**Procedure**:

1. **Identify synthesis-class writes this gate** — every governed artifact (VERSION_SCOPE, INDEX.md, INIT-*.md) that received a multi-row or count-bearing write during Gate 1.
2. **Re-derive each quantity from primary sources — NOT from the row just written**: ΣSU(Tier 1) by re-summing per-item SU from the candidate inventory; ACTIVE/NASCENT roster by re-counting `planning/initiatives/INIT-*.md` headers; INBOUND/AUTHORED counts by re-running the since-anchor `find`/`gh` queries; Tier counts by re-listing tagged items.
3. **Reconcile** — if any re-derived quantity differs from the synthesized claim, correct the artifact (treat the written row as a claim under test, L960) and record the correction transparently as a Finding in the affected artifact (not buried in a commit message).
4. **Self-demonstrating closure**: like G1.INBOUND/G1.AUTHORED, executing G1.AUDIT on the cycle's own synthesis rows IS the procedure the SOP codifies.

**Trigger phrases** (yellow flags that mandate the pairing): "closes the gap" / "hits the ceiling" / "completes the cycle" / "N→M" count transitions / a "clean" or "tidy" feeling about a freshly-written row.

**V-tests**:

```bash
# V-1.AUDIT.1: ΣSU(Tier 1) re-derived from per-item SU equals the stated total
# (re-sum the candidate-inventory SU column; compare to VERSION_SCOPE Tier-1 ΣSU row)

# V-1.AUDIT.2: ACTIVE roster count re-derived from primary source
grep -lE "^\*\*Status\*\*: ACTIVE" planning/initiatives/INIT-*.md | wc -l
# compare to any "ACTIVE count = N" claim written this gate

# V-1.AUDIT.3: every count-bearing claim written this gate has a re-derivation note
# (manual: each synthesis row with a number cites its primary-source re-count)
```

#### Principal Scope-Selection Step (G1.SELECT)

**Why mandatory** (v1.4.0 addition; principal directive 2026-06-12 — "Enforce this step for future releases", issued with a worked Copy-to-Clipboard demonstration from `tools/scope_selector.html` v0.5.0):

Two prior generations of interactive scope-selection boards (`tools/scope_selector.html` v0.5.0, v3.13 cycle — registered IC-1 "in use"; `tools/scope_selector_v318.html` v0.9.2, v3.18 cycle) gave the principal a visual checkbox/WSJF interface for scope decisions, then **died after one cycle each** because: (a) WSJF scores and selections computed in the HTML were never persisted back into the governed VERSION_SCOPE (L824 finding 4); (b) each board was hand-authored against one cycle's data and went stale immediately. The v3.19–v3.21 ceremonies regressed to table-only selection. This step makes the interface mandatory AND closes both failure modes structurally.

**Procedure**:

1. **Tool-currency precondition (stale-board ban)**: before presenting, the control board MUST be generated or refreshed from the cycle's `VERSION_SCOPE_vX.Y.Z.md` candidate inventory **same-session**. Presenting a prior cycle's board (or any board whose item roster ≠ the current candidate inventory) is PROHIBITED — it would put stale state in front of the principal with interface-borrowed authority. Verify: board item IDs == VERSION_SCOPE candidate IDs (list-diff, both directions).
2. **Principal selection**: principal opens the board (`open tools/scope_selector_vXYZ.html`), makes Tier/selection/defer decisions, clicks **Copy to Clipboard**.
3. **Capture verbatim**: the exported `SCOPE_LOCK` markdown block is pasted into the session and the agent records it **verbatim** in the cycle lock plan (selection-record section) — this is the principal's selection evidence at Gate 1, sibling to (NOT a substitute for) the Gate 2 form-contract GO.
4. **Persist back (closes L824)**: the agent transcribes the selections — Tier placements, WSJF scores, defer list — into `VERSION_SCOPE_vX.Y.Z.md` Tier tables as the grooming version bump. **Render one way, persist the other**: the HTML is a view; the markdown stays the artifact of record.
5. **Reconcile**: G1.AUDIT re-derives the selected/deferred/total counts from the captured block vs the written Tier tables (equal sets).

**Board design requirements** (SHALL — from the 2026-06-12 principal directives; enforced by `scripts/generate_scope_board.py`):

1. **Local-date stamp + source provenance** — boards SHALL stamp the LOCAL ISO date (Gen-1 defect: emitted 2026-06-13 on 2026-06-12 via UTC) and the source VERSION_SCOPE version + generation date.
2. **Explicit select/de-select, tier-backed** — scope membership and tier placement are two facets of one state, and BOTH must be operable and legible: (a) an explicit **IN/OUT select control** (the membership gesture) so the principal never has to *infer* how to include/drop an item; (b) the **tier dropdown** (placement within scope). They are kept in sync — formally **selected ≝ tier ∈ {T1,T2,T3}**, **de-selected ≝ tier = DEFER**; checking IN promotes a DEFER item to its lean tier, un-checking sets DEFER. *(History: a Gen-3 iteration removed the checkbox as "redundant with tier" — correct on the data model, wrong on UX: principals could not find the select gesture. Membership ≠ placement; surface both.)*
3. **Visible / legible default (forcing-function principle; L466 cognate)** — every item SHALL open at a **visible** default value (the agent-lean tier from VERSION_SCOPE §WSJF Pre-Scores), NEVER a null `tier…` placeholder. A silent/null default lets an item enter or leave scope unconsidered; a visible default makes each item an explicit accept-or-override. The board SHALL **mark which items the principal actively ruled vs passively inherited** (e.g. a "lean" badge + a `°` marker in the export), so passive acceptance stays legible — the same provenance discipline as the `*` adjusted-score marker. Silence ≠ approval (L466).
4. **Column legibility** — every column and filter control SHALL carry a hover description (tooltip). Carried Gen-1 feature (v0.3.0 "all column header tooltips"), dropped in early Gen-3, restored as a requirement.
5. **Agent pre-scores live in VERSION_SCOPE** — the board renders the §WSJF Pre-Scores block (D1–D4 + lean tier + Top/Watch + tension); it does not invent scores client-side. Principal adjustments at the board are authoritative and exported with provenance markers.
6. **Per-cycle scope-lean parameters carry forward** — the principal MAY set, for an upcoming cycle, a target **candidate count** and **accept/reject (in-scope/DEFER) lean ratio** that the agent uses when seeding that cycle's lean tiers (e.g. v3.22 = ~33 / 80-20; v3.23 directive = ~43 / 70-30, tightening selectivity as backlog grows). These are agent-lean *defaults* the principal still adjusts at the board (requirement 3) — NOT a hard split to engineer (avoid scoring-to-a-ratio; set honest per-item tiers and report the resulting ratio). Record a set target in agent memory + the next cycle's pre-release-research notes so the seed starts from the principal's selectivity intent rather than re-deriving it.
7. **Predicted-value selection column (NEW v1.6.0 — D-RP-13; gmelli/aget-aget#1758)** — the board SHALL surface each candidate's **predicted functional-value score** (`RUBRIC_release_value_cost` predicted mode: V1 L0–L3, sourced from the P1.7 pre-release-research table) as a **column distinct from the WSJF chips** — the two axes are displayed **side-by-side, never summed** (rubric core principle: process/urgency and functional value are distinct). The column makes the include/exclude tradeoff value-legible at the moment of selection, closing the L1000 conflation at the selection-mechanism layer. **HYBRID enforcement (D-RP-13)**: for **flagship / Tier-1 candidates AND any candidate ≥ 8 SU** the predicted V1 is a **MANDATORY binding input** — a Tier-1 selection whose predicted V1 is absent or L0/L1 SHALL be flagged (board badge) for explicit principal ruling, not silently selected; for Tier-2/3 and sub-8-SU items it is **ADVISORY** (shown, non-binding). *(8-SU threshold = PROPOSED DEFAULT, principal-confirmable; per F-G1-2 anti-research-theater.)* **Data dependency**: per-item V1 must be carried in VERSION_SCOPE in a board-parseable location (today V1 lives in the SPINE/lock table, not the candidate-inventory rows the parser reads) — the schema + `scripts/generate_scope_board.py` column render are the OWED tooling realization tracked under #1758 (coupled to the Gen-3 board-generator work #1649). Until the column ships, P1.7's predicted-value table is presented alongside the board as the interim binding record.

**V-tests**:

```bash
# V-1.SELECT.1: Board is cycle-current — roster equality with VERSION_SCOPE
# (list-diff board item IDs vs candidate-inventory IDs; expect equal sets)

# V-1.SELECT.2: SCOPE_LOCK block captured verbatim in lock plan
grep -c "SCOPE_LOCK: v" planning/PROJECT_PLAN_vX.Y.Z_scope_lock_v1.0.md  # expect ≥1

# V-1.SELECT.3: Selections persisted — selected/deferred counts in VERSION_SCOPE
# Tier tables match the captured block's "Items: N selected / M total" line
```

**Decision Point** (Gate 1 close): Proceed to Gate 2 if Tier 1 SU ≤ cycle cap AND theme alignment confirmed AND principal selection captured + persisted (G1.SELECT) AND all inbound issues dispositioned (G1.INBOUND) AND all in-repo authored substrate dispositioned (G1.AUTHORED) AND every synthesis-class count claim re-derived from primary sources (G1.AUDIT) AND every ACTIVE initiative carries a G1.PORTFOLIO verdict AND every prior-cycle §Deferred item carries a disposition (G1.PORTFOLIO).

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

The cluster is the set of L-docs whose anti-patterns the lock-prep ceremony itself MUST NOT recur. **This table is the single source of truth for membership** — prereq #4 and Gate 0 reference it; no other site restates a count. Current cluster (15 L-docs; count re-derived 2026-07-17, all members verified on disk):

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
| L980 | Audit-After-Synthesis Pairing (in-flight self-catch) | **G1.AUDIT** — Gate 1 synthesis-class writes paired with audit-class re-derivation from primary sources (gh#1476 Healthy Friction codification, Channel 2) |
| L671 | Classification-Without-Consequence | All grace-extends have explicit V-tests verifying registry update |
| L869 | (cycle-specific) | Per cycle disposition |
| L894 | (cycle-specific) | Per cycle disposition |
| L1155 | Access-Asymmetry | Added v3.26 cycle (VERSION_SCOPE_v3.26.0 prereq #4) — verify claims only on surfaces this seat can actually read |
| L1158 | Co-Atomic Gate-Row Assertion | Added v3.26 cycle — gate rows asserted together must be verified together |
| L1160 | Corrections Are Claims-Under-Test | Added v3.26 cycle — a correction pass is itself re-verified at source before it stamps anything |

**v3.27-cycle addition candidates (pending Gate-0 confirmation stamp, per `planning/MEMO_v3.27_freshness_audit_2026-07-17.md`)**: L1168 (subagent-relay claims need primary-source re-verification), L1187 (promotion-to-canonical ≠ shipping), L1188 (stored registries don't get read — wrong denominators), L1190 (a named pointer is a claim, not a footnote). Noted-not-added: L1162, L1171. On confirmation, move into the table with a self-application line each.

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
| 1.1.0 | 2026-05-15 | **Minor enhancement** via /aget-propose-actions Action 5 of 5 (4h GO 2026-05-15). Adds 2 procedural steps surfacing methodology debt empirically observed in v3.18 pre-plan cycle: (a) **Gate 0 G0.5a Freshness-Audit Cadence Specification** — codifies "≤7 days OR ≤20 new inbound issues" threshold, preventing recurrence of the 3-day-old / 47-new-issue drift observed at v3.18 pre-plan 2026-05-15 (per `docs/MEMO_v3.18_freshness_audit_2026-05-15.md`); (b) **Gate 1 G1.DECIDE Cross-Cycle Decide-Packet Preparation** — codifies consolidation of accumulated initiative-portfolio Decide gates into single principal-facing packet, after empirical demonstration of 10-gates-across-9-documents scatter pattern at v3.18 pre-plan (per `docs/DECIDE_PACKET_v3.18_2026-05-15.md`). Both additions complement (do NOT replace) existing G0.5 annotation-only pass and G1.INBOUND inbound-issue review. Distinguishing concern: G1.INBOUND handles issue-class dispositions; G1.DECIDE handles initiative-portfolio-class Decides. Canonical sync to public deferred to next push window (L735). v1.1.0 source evidence: this NBA cycle's 4 sibling artifacts (commits `753bc68`, `1b8a75b`, `2e5ebc0`, `1fe51cb`). |
| 1.3.0 | 2026-05-23 | **Minor enhancement** (v3.19 release-build Gate 1 T1.4; principal GO "T1.4 is in scope"). Adds **Gate 1 G1.AUDIT Audit-After-Synthesis Pairing** step — codifies L980 / gh#1476 (Healthy Friction codification) as the SOP's **Channel 2 point-of-use** (L467): Gate 1 synthesis-class writes to governed artifacts (VERSION_SCOPE Tier placement, INDEX.md grooming dispositions, INBOUND/AUTHORED tables) SHALL be paired with an audit-class re-derivation of every count/ΣSU/roster claim from primary sources before Gate 1 close. Empirical grounding: v3.19 scope-lock cycle ran this ad hoc as `G1.AUDIT-COUNTS` (caught a false "ACTIVE 8→7" near-miss + corrected AUTHORED "~30"→32 from primary source). Layer 1 (AGENTS.md §Audit-After-Synthesis Pairing) + L-doc (L980) pre-existed; Layer 5 (`/aget-propose-actions` Step 2.7 structural) = release T1.1. No new L-doc authored (L980 is the anchor; avoiding L974 banner-inflation). Canonical sync to public deferred to next push window (L735; `origin = aget-framework/*`). |
| 1.2.0 | 2026-05-16 | **Minor enhancement** via /aget-propose-actions Action 3 (4h GO 2026-05-16). Adds **Gate 1 G1.AUTHORED Pre-LOCK Authored-Substrate Review** step closing gh#1374 (sibling of L913 handoff-discovery class). Surfaces in-repo authored substrate (PROPOSAL_*.md, INIT-*.md, CANDIDATE_LDOC_*.md) filed since the freshness-audit timestamp — a class undispositioned at scope-lock under G1.INBOUND alone. Empirical grounding: v3.18 pre-plan burst (2026-05-12 → 2026-05-14) authored 11 such artifacts (5 PROPOSALs + 2 initiative manifests + 4 L-doc candidates) all slipping past G1.INBOUND scope. Distinguishing concern: G1.INBOUND handles GitHub issue-class dispositions; G1.AUTHORED handles in-repo authored-artifact-class dispositions; both mandatory pre-Gate-2. VERSION_SCOPE_v3.18.0 T1.14 (Decide-independent; 3 SU). Canonical sync to public deferred to next public push window (L735). |
