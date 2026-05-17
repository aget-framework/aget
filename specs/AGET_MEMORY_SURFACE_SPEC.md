# AGET_MEMORY_SURFACE_SPEC v0.2.0 — DRAFT

**Spec ID**: AGET_MEMORY_SURFACE_SPEC
**Version**: 0.2.0 (V-test wiring + EARS-formalization + Conformance Matrix + N=2 cross-references) — prior 0.1.0 (initial DRAFT 2026-05-15 AM)
**Status**: DRAFT (canonical; pending cross-fleet review)
**Created**: 2026-05-15 AM; v0.2 amendment 2026-05-15 PM; canonical promotion 2026-05-16 (v3.18 G1.T1.16)
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_MEMORY_SURFACE_SPEC.md`
**Governing**: L335 Memory Architecture Vision; L742 Two-Level Model
**Theoretical Basis**: Extended Mind (Clark/Chalmers), Transactive Memory (Wegner), Distributed Cognition (Hutchins) — per L331/L335
**Empirical Grounding**: 2 same-session L908 instances 2026-05-15 AM (memory-surface routing error + claim-scope under-application) + 1 N=2 cross-validation 2026-05-15 PM (gh#1378 surfaced canonical promotion path; gh#1384 surfaced in-repo vs harness boundary question)
**Tracking issue**: gmelli/aget-aget#1378 (canonical promotion path; closes L908 memory-surface gap)
**Paired item**: v3.18 T2.37 (V-test wiring + inbound cross-references; sequencing constraint T1.16-before-T2.37 per F-3)

## v0.2 Amendment Summary (2026-05-15 PM)

**Changes from v0.1**:
1. **EARS-formalized R-MS-001..007** (added EARS clause type [Ubiquitous / Event-Driven / Conditional / Optional] to each)
2. **V-MS-005 mechanical implementation** (replaces "manual audit suffices")
3. **3 NEW V-tests V-MS-006..008** covering today's surfaced cases
4. **Conformance Matrix added** (CAP-MS-001..003 + R-MS-001..007 + V-MS-001..008 wired)
5. **Cross-references updated** with this-batch evidence (gh#1374, gh#1378, gh#1379, gh#1384)
6. **T2.37 v3.18 candidacy formalized** in changelog

**Unchanged**: Vocabulary (5 SKOS-grounded terms), capabilities (3), theoretical basis, purpose.

---

## Purpose

This specification codifies the **memory-surface taxonomy** for AGETs — disambiguating two distinct memory surfaces (harness auto-memory vs KB substrate) and providing routing rules for content classes. Closes a structural gap surfaced 2026-05-15 wherein an AGET proposed a non-canonical surface for session-insight content due to absent boundary rules.

This spec addresses **L742 spec-fault**: the AGET behavioral spec did not previously define which memory surface applies to which content class, leaving boundary judgment to ad-hoc disposition.

---

## Vocabulary

| Term | Definition | SKOS |
|------|------------|------|
| **Harness Auto-Memory** | The system-prompt-managed memory directory at `~/.claude/projects/<encoded-path>/memory/` containing harness-specific topic files keyed by type (user, feedback, project, reference). Operated by the Claude CLI harness. Out-of-repo. Not git-tracked. Persists across conversations for a single AGENT instance. | C-MEM-HARNESS |
| **KB Substrate** | The in-repo Memory Architecture (L335) substrate spanning `.aget/evolution/L*.md` (L-docs), `docs/patterns/PATTERN_*.md`, `docs/` (memos/findings/briefs), `governance/*.md`, `planning/` (plans/proposals/initiatives), `sops/SOP_*.md`. In-repo. Git-tracked. Shared across agents and humans. | C-MEM-KB |
| **Content Class** | Categorical type of memory content: feedback / user / project / reference (harness) vs L-doc / pattern / spec / SOP / session-insight / finding / memo / brief / plan (KB). | C-MEM-CLASS |
| **Surface Routing** | The rule mapping a content class to its appropriate surface. | C-MEM-ROUTE |
| **Precedence Rule** | The disambiguation rule when harness instructions and AGENTS.md governance both apply: AGENTS.md OVERRIDES for content in the AGET's domain. | C-MEM-PRECED |

---

## Requirements (R-MS-NNN, EARS-formalized in v0.2)

### R-MS-001 — Two Memory Surfaces

**R-MS-001-01** (Ubiquitous): The AGET SHALL recognize two distinct memory surfaces with non-overlapping primary scope:

- **Harness auto-memory** at `~/.claude/projects/<encoded-path>/memory/` — managed by Claude CLI harness via system-prompt instructions
- **KB substrate** at in-repo paths governed by L335 — managed by AGET via SOPs and skills

### R-MS-002 — Harness Auto-Memory Content Scope

**R-MS-002-01** (Ubiquitous): Harness auto-memory SHALL contain ONLY:
- **user** entries (principal profile facts; cross-conversation continuity)
- **feedback** entries (corrections / confirmations / behavior rules learned from principal)
- **project** entries (lightweight, ephemeral session-state pointers; NOT canonical session insight)
- **reference** entries (pointers to external systems)
- An index file `MEMORY.md` cataloging the above

**R-MS-002-02** (Ubiquitous): Harness auto-memory SHALL NOT contain:
- Session insight intended for cross-agent sharing
- L-doc class structural findings
- Spec-class governance content
- Pattern documentation
- Any content that should appear in a future agent's `inherited/` directory

### R-MS-003 — KB Substrate Content Scope

**R-MS-003-01** (Ubiquitous): KB substrate SHALL contain:
- **L-doc** class artifacts (`.aget/evolution/L*.md`)
- **Pattern** class artifacts (`docs/patterns/PATTERN_*.md`)
- **Spec** class artifacts (`aget/specs/` canonical + `aget/specs/drafts/` pre-canonical)
- **SOP** class artifacts (`sops/SOP_*.md`)
- **Governance** class artifacts (`governance/*.md`)
- **Session-insight** docs (`docs/SESSION_PATTERN_*.md`, `docs/FINDING_*.md`, `docs/MEMO_*.md`, `docs/BRIEF_*.md`)
- **Planning** class artifacts (`planning/PROJECT_PLAN_*.md`, `planning/initiatives/INIT-*.md`, `planning/project-proposals/PROPOSAL_*.md`)
- **CANDIDATE** artifacts pre-promotion (`docs/CANDIDATE_LDOC_*.md`, `aget/specs/drafts/`)

### R-MS-004 — Precedence Rule (AGENTS.md OVERRIDES Harness)

**R-MS-004-01** (Event-Driven): WHEN the system-prompt's auto-memory instructions and the AGET's AGENTS.md governance both apply to a piece of content, the AGENT SHALL apply AGENTS.md governance.

This is critical for AGETs that subscribe to L335 Memory Architecture principle #4 ("Memory is shared human-AI artifact, not hidden AI state"). Routing session-insight to harness auto-memory hides it from the substrate the AGET is contractually obliged to maintain.

### R-MS-005 — Routing Rules per Content Class

**R-MS-005-01** (Ubiquitous): For session-generated content, the AGENT SHALL route per this table:

| Content Class | Surface | Path Template |
|---------------|---------|---------------|
| Principal-profile fact (user role/preference) | Harness | `~/.claude/.../memory/user_<slug>.md` |
| Principal feedback (correction / confirmation / behavior rule) | Harness | `~/.claude/.../memory/feedback_<slug>.md` |
| Session state pointer (NOT structural insight) | Harness (lightweight) | `~/.claude/.../memory/project_<slug>.md` |
| External-system reference | Harness | `~/.claude/.../memory/reference_<slug>.md` |
| Session structural insight (cross-agent value) | **KB** | `docs/SESSION_PATTERN_<topic>_<YYYY-MM-DD>.md` or `docs/FINDING_<topic>_<YYYY-MM-DD>.md` |
| Methodology generalization (cross-session value) | **KB** | `.aget/evolution/L<NNN>_<slug>.md` |
| Anti-pattern documentation | **KB** | `.aget/evolution/L<NNN>_<slug>.md` |
| Pattern documentation | **KB** | `docs/patterns/PATTERN_<slug>.md` |
| Spec class | **KB** | `aget/specs/drafts/<NAME>_v<N.M>.md` (pre-canonical) or `../aget/specs/<NAME>.md` (canonical) |

### R-MS-006 — Conflict Resolution

**R-MS-006-01** (Conditional): IF a content type appears in both surfaces' scope (e.g., a behavior rule that originated as principal-feedback AND has cross-agent generalization value), THEN the AGENT SHALL author in **BOTH** surfaces with cross-references — feedback memory cites L-doc; L-doc cites feedback memory.

**R-MS-006-02** (Conditional): IF authoring in both surfaces per R-MS-006-01, the AGENT SHALL use `[[name]]` syntax in harness memory and explicit-path citation (`docs/...md`, `.aget/evolution/L###_...md`) in KB.

### R-MS-007 — Self-Application Discipline

**R-MS-007-01** (Ubiquitous): The AGENT SHALL apply this spec's routing rules to ITS OWN writes — not exempting same-session in-repo writes from claim-verification discipline.

**R-MS-007-02** (Conditional): IF a write seems to fit BOTH surfaces and the AGENT is unsure, THEN it SHALL DEFAULT to KB substrate (per R-MS-004 precedence) AND raise the surface-routing question for principal Decide.

---

## Capabilities (CAP-MS-NNN)

### CAP-MS-001 — Surface Detection

The AGENT SHALL detect which surface a memory write should target by:
1. Classifying content per R-MS-005 table
2. Resolving conflicts per R-MS-006
3. Defaulting to KB substrate when ambiguous (per R-MS-004 precedence)

### CAP-MS-002 — Cross-Reference Discipline

When content appears in both surfaces (per R-MS-006), the AGENT SHALL author bidirectional cross-references using `[[name]]` syntax in harness memory and explicit-path citation in KB.

### CAP-MS-003 — Routing Audit

The AGENT SHOULD periodically (per scope-lock ceremony Gate 0 G0.5a freshness audit) audit harness ~/.claude/ memory for content that should have routed to KB. Findings → migration candidate list.

---

## V-tests

```bash
# V-MS-001: Routing rule reachability — for each content class, an example path exists
test -d ~/.claude/projects/-Users-gabormelli-github-aget-framework-private-aget-framework-AGET/memory/ \
  && echo "PASS: harness memory dir exists" || echo "FAIL: harness memory dir missing"

# V-MS-002: KB substrate paths reachable
for path in .aget/evolution docs/patterns docs governance planning sops aget/specs/drafts; do
  test -d "$path" || echo "MISSING: $path"
done

# V-MS-003: Cross-reference discipline — sample feedback memory cites L-doc (per R-MS-006)
ls ~/.claude/projects/-Users-gabormelli-github-aget-framework-private-aget-framework-AGET/memory/feedback_*.md 2>/dev/null \
  | head -3 | while read f; do
    grep -q "L[0-9]\{3\}\|\.aget/evolution\|docs/" "$f" \
      && echo "PASS: $(basename $f) cross-references KB" \
      || echo "WARN: $(basename $f) lacks KB cross-reference"
  done

# V-MS-004: KB substrate session-insight class exists (per R-MS-005)
ls docs/SESSION_PATTERN_*.md docs/FINDING_*.md docs/MEMO_*.md docs/BRIEF_*.md 2>/dev/null | wc -l
# expect >0 (session-insight class populated)

# V-MS-005: No L-doc class artifact MISSING from KB (negative test for harness-leak)
# v0.2 mechanical implementation: scan harness memory for content patterns that should be L-docs
ls ~/.claude/projects/-Users-gabormelli-github-aget-framework-private-aget-framework-AGET/memory/*.md 2>/dev/null \
  | while read f; do
    # L-doc patterns: structural finding (claim layer + evidence + generalization)
    grep -lE "^##.*(Pattern|Anti-pattern|Structural|L[0-9]{3}|Layer [0-9])" "$f" 2>/dev/null
  done | tee /tmp/v_ms_005_candidates.txt
test -s /tmp/v_ms_005_candidates.txt \
  && echo "WARN: harness memory contains L-doc-class candidates (should migrate to KB)" \
  || echo "PASS: no L-doc-class content in harness memory"

# V-MS-006 (NEW v0.2): R-MS-005 routing table is exhaustive against today's content classes
# Test: every committed artifact this cycle maps to a row in R-MS-005 table
git log --since="2026-05-15" --name-only --pretty=format: \
  | grep -E "^(docs/|planning/|aget/specs/drafts/|\.aget/evolution/|governance/|sessions/|sops/)" \
  | sort -u | head -30
# Manual audit: each path prefix appears in R-MS-005 routing table

# V-MS-007 (NEW v0.2): No bidirectional cross-reference orphans
# For every feedback_*.md citing L-doc, verify L-doc cites back (R-MS-006-01)
ls ~/.claude/projects/-Users-gabormelli-github-aget-framework-private-aget-framework-AGET/memory/feedback_*.md 2>/dev/null \
  | while read f; do
    LDOCS=$(grep -oE "L[0-9]{3}" "$f" | sort -u)
    SLUG=$(basename "$f" .md | sed 's/^feedback_//')
    for ldoc in $LDOCS; do
      LFILE=$(ls .aget/evolution/${ldoc}_*.md 2>/dev/null | head -1)
      [ -n "$LFILE" ] && grep -q "$SLUG\|feedback_" "$LFILE" \
        || echo "ORPHAN: $f cites $ldoc but $ldoc does not cite back"
    done
  done

# V-MS-008 (NEW v0.2): Self-application audit — recent in-repo writes verified against R-MS-007
# This V-test is qualitative: did the most-recent 5 commits respect surface routing?
git log --since="2026-05-15" --pretty=format:"%h %s" | head -5 \
  | grep -vE "^[a-f0-9]+ (specs|planning|docs|sessions|sops|governance|ontology|knowledge|handoffs|\.aget):" \
  && echo "WARN: commit subject suggests off-substrate write" \
  || echo "PASS: recent commits respect content-class prefixes"
```

---

## Conformance Status

**v0.2.0 DRAFT (canonical)** — per ADR-008 progression: spec → draft → adopted → canonical. Lives at canonical location; pending cross-fleet peer review for v1.0.0 promotion.

## Conformance Matrix (NEW v0.2)

| Element | Type | Status | Verification |
|---------|------|:------:|--------------|
| R-MS-001-01 | Requirement | DRAFTED | V-MS-001 (harness dir) + V-MS-002 (KB dirs) |
| R-MS-002-01..02 | Requirement | DRAFTED | V-MS-004 (KB session-insight present) + V-MS-005 (harness L-doc absence) |
| R-MS-003-01 | Requirement | DRAFTED | V-MS-002 (KB dirs reachable) + V-MS-006 (R-MS-005 table exhaustive against today's commits) |
| R-MS-004-01 | Requirement | DRAFTED | Qualitative — applied at every memory write Decide; this batch's #1378 surface-question audit = instance |
| R-MS-005-01 | Requirement | DRAFTED | V-MS-006 (table covers content-class universe) |
| R-MS-006-01..02 | Requirement | DRAFTED | V-MS-007 (no cross-reference orphans) |
| R-MS-007-01..02 | Requirement | DRAFTED | V-MS-008 (self-application audit) |
| CAP-MS-001 | Capability | DRAFTED | V-MS-006 (routing detection mechanism reachable) |
| CAP-MS-002 | Capability | DRAFTED | V-MS-007 (cross-reference discipline mechanism reachable) |
| CAP-MS-003 | Capability | DRAFTED | V-MS-005 (audit mechanism reachable; Gate 0 G0.5a freshness audit integration pending) |
| V-MS-001..008 | V-tests | 8 specified | All bash-executable (5 from v0.1 + 3 new v0.2) |

**Promotion criteria to v1.0.0 canonical**:
1. Empirical validation in ≥2 sessions (instance 1: 2026-05-15 AM L908 cluster; instance 2: 2026-05-15 PM this-batch cross-validation via gh#1378 + gh#1384 surfacing — **MET**)
2. Cross-fleet review (supervisor + ≥1 peer AGET) — **pending**
3. V-test automation (V-MS-005..008 wired bash-executable in v0.2) — **MET**
4. Canonical promotion to `aget/specs/AGET_MEMORY_SURFACE_SPEC.md` — **MET 2026-05-16 (v3.18 G1.T1.16)**

---

## Theoretical Grounding (L331/L335)

- **Extended Mind** (Clark/Chalmers) — both surfaces extend agent cognition, but DIFFERENT cognition layers: harness extends agent-instance continuity; KB extends fleet-wide cognition
- **Transactive Memory** (Wegner) — KB IS the shared "who knows what" across agents; harness memory is NOT (private to one agent's harness)
- **Distributed Cognition** (Hutchins) — KB substrate is the distributed cognition artifact; harness is per-instance and does not participate
- **Cybernetics** (Ashby) — both surfaces provide variety, but at different time scales (harness = within-conversation; KB = across releases)

---

## Cross-References (outbound only — inbound wiring deferred to v3.18 T2.37 per F-3 sequencing constraint)

| Anchor | Reference |
|--------|-----------|
| Tracking issue (canonical promotion path) | gmelli/aget-aget#1378 |
| Empirical evidence (1st L908 instance) | gmelli/aget-aget#1374 |
| Empirical evidence (2nd L908 instance — surfaces this spec) | 2026-05-15 session — proposed `~/.claude/` for AGET session-insight; principal "ouch" probe |
| Empirical evidence (N=2 cross-validation) | gmelli/aget-aget#1378 (canonical path) + gmelli/aget-aget#1384 (in-repo vs harness boundary) |
| L-doc anchor (apply-to-others-not-self) | L908 (private-aget-framework-AGET `.aget/evolution/L908_*.md`) |
| L-doc anchor (memory-entry-as-claim) | L960 (private-aget-framework-AGET `.aget/evolution/L960_*.md`) — downstream sibling |
| Sibling spec | L913 (Plan-Close → Plan-Create Handoff — closes adjacent surface-taxonomy gap at NBA-generation surface) |
| Sibling skill | `/aget-file-issue` (D71 STRUCTURAL — codifies destination routing rule, this spec codifies destination routing for memory) |
| Theoretical foundation | L331 (theoretical foundations), L335 (Memory Architecture Vision) |
| Two-Level Model | L742 (this spec is spec-side; the agent following memory-routing rules is implementation-side) |
| Paired item (v3.18) | T2.37 (V-test wiring + inbound cross-references; sequencing constraint T1.16-before-T2.37 per F-3) |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-05-15 AM | Initial DRAFT. Authored as Action B of /aget-propose-actions --budget=2h --batch --go (GO 2026-05-15) framework-remediation cycle. Empirical grounding: 2 same-session L908 instances at memory-surface + claim-scope. Spec-fault root cause per 5-Whys analysis. |
| 0.2.0 | 2026-05-15 PM | EARS-formalization of R-MS-001..007; V-MS-005 mechanical implementation; 3 NEW V-tests V-MS-006..008 (R-MS-005 exhaustiveness, R-MS-006 orphan audit, R-MS-007 self-application audit); Conformance Matrix added; N=2 empirical validation MET via this-batch evidence (gh#1378 + gh#1384). v3.18 T2.37 fold-in candidate per VERSION_SCOPE_v3.18.0 v0.2.0. Authored as Round 3 Action 3 of 6 of /aget-propose-actions --budget=4h --count=auto --batch --go 2026-05-15 PM. |
| 0.2.0 (canonical) | 2026-05-16 | **Canonical promotion** (v3.18 G1.T1.16; gh#1378 closure). Source: `private-aget-framework-AGET/aget/specs/drafts/AGET_MEMORY_SURFACE_SPEC_v0.1.md` (header internally already at v0.2.0). Destination: `aget/specs/AGET_MEMORY_SURFACE_SPEC.md` (bare canonical convention per AGET_INITIATIVE_SPEC precedent). Status field updated `DRAFT (pre-canonical; drafts/ location)` → `DRAFT (canonical; pending cross-fleet review)`. Promotion criterion #4 MET. PAIRED with T2.37 under F-3 sequencing constraint (T1.16-before-T2.37): outbound cross-references only this gate; inbound cross-references (other specs/L-docs citing AGET_MEMORY_SURFACE_SPEC) deferred to T2.37. Authorization: `/aget-go` bare 2026-05-16T19:22Z (svc-ed triad; c=UNMET acknowledged-with-defaults; default-(a) corrected at execution from `_v0.2.0_DRAFT.md` → bare canonical per AskUserQuestion disambiguation). Session record: `sessions/session_2026-05-16_1921.md`. |

---

*aget/specs/AGET_MEMORY_SURFACE_SPEC.md — canonical DRAFT pending cross-fleet review for v1.0.0 promotion.*
