# SOP: Fleet Migration

**Version**: 1.9.0
**Status**: Active
**Created**: 2026-01-05
**Updated**: 2026-08-03
**Owner**: aget-framework
**Implements**: CAP-MIG-017 (Remote Supervisor Upgrade), SD-3 wave-sequencing (v1.6.0)
**Related**: L455 (AGENTS.md Invocation Verification), L457 (Cross-Machine Pre-Flight), AGET_RELEASE_SPEC, PROJECT_PLAN_fleet_v3.2_migration.md

---

## Purpose

Standard operating procedure for migrating fleet agents to new AGET framework versions. Ensures consistent deployment of version updates, session scripts, and validation across all active agents.

---

## Execution Model (Centralized by Default)

Fleet migration is **centralized by default**: the supervisor executes all agent upgrades in a single coordinated session. Distributed execution (each agent self-upgrades) is used only when agent count or machine topology makes centralized execution impractical, and requires principal approval.

| Model | When | Mechanism |
|-------|------|-----------|
| **Centralized** (default) | Fleet ≤ 40 agents, single supervisor machine | Supervisor iterates agents directly |
| **Distributed** | Fleet > 40, multi-machine, or principal directed | Each agent receives REMOTE_MIGRATION_MESSAGE; supervisor coordinates |

### Execution-model authorization receipt

Record the chosen model before dispatch: model, reason, authorizing event, executing identity, and the
permission surface that will actually be consulted. Distributed execution is not centralized execution
performed through more prompts: each receiving seat becomes an executor, so its write scope, command
allowlist, and refusal behavior become load-bearing. A blocked seat is evidence about the chosen model;
do not broaden that seat's permissions merely to make an unauthorized model work.

If distributed execution lacks its required principal approval, stop and use the centralized default or
obtain the approval. Do not describe a later reversion to the default as remediation of five individual
permission defects when the execution model was the shared cause.

---

## Wave Sequencing

Fleet migration proceeds in three sequential waves. Each wave SHALL complete before the next begins; wave-boundary V-tests are blocking gates.

| Wave | Scope | Purpose | Sequencing Rule |
|------|-------|---------|-----------------|
| **Wave 0** | Supervisor self-upgrade | Validate target version on the agent that will execute the rest of the migration | MUST land before any Wave 1 work; supervisor cannot orchestrate an upgrade it has not itself completed |
| **Wave 1** | Pilot agent(s) — typically 1-3 representative agents | Risk validation: surface BC-NNN violations, V-test gaps, or framework-defects before full-fleet exposure | MUST land + soak ≥ 1 session before Wave 2; rollback at this stage is bounded to the pilot set |
| **Wave 2** | Remainder of fleet (main + secondary portfolios) | Full-fleet propagation | Proceeds only after Wave 1 success; portfolio batches sequenced per Phase 2-3 |

### Wave-to-Phase Mapping

| Wave | Phases (this SOP) | Boundary V-test |
|------|-------------------|-----------------|
| Wave 0 | Phase 0.5 (Remote Supervisor Pre-Flight) + supervisor's own version-bump | V0.5.3 (Version Verification on supervisor) |
| Wave 1 | Phase 1 (Gate 1.1 → Gate 1.4) | Gate 1.4 (Pilot Commit) |
| Wave 2 | Phase 2 + Phase 3 + Phase 4 | Gate 4.2 (Version Consistency Check across remaining fleet) |

### Why Sequenced (Not Parallel)

- **Wave 0 before Wave 1**: A supervisor running v(N-1) cannot reliably orchestrate v(N) on its workers — it lacks the target version's specs, scripts, and V-tests. Self-upgrade first is the bootstrapping invariant.
- **Wave 1 before Wave 2**: Pilots surface release-defects at bounded blast radius (1-3 agents). Skipping Wave 1 trades observability for speed; the trade is rarely worth it once fleet > 5 agents. Past cycles show 60-80% of release-defects surface in Wave 1.
- **No Wave-skip without principal approval**: An "experienced" release where Wave 1 feels redundant is exactly when L92 (Premature Victory) is most likely. Document any wave-skip in the migration session log with explicit principal approval citation.

### Wave-Boundary Rollback

If a wave fails its boundary V-test:
- **Wave 0 fail**: Halt migration; supervisor cannot proceed. Triage on supervisor itself.
- **Wave 1 fail**: Rollback pilot(s) per Rollback Criteria (see below); file release-blocking issue; do NOT enter Wave 2.
- **Wave 2 fail (per-portfolio batch)**: Halt batch; complete in-flight agents; rollback failed agents; surface to principal for triage decision (continue with other batches vs. halt all of Wave 2).

---

## Mandatory vs Optional Change Classification

Not all upgrade changes carry the same obligation. This classification determines which steps are blocking and which are contextual.

| Class | Definition | V-test Requirement | Example |
|-------|-----------|-------------------|---------|
| **Mandatory** | Required for version compliance. Agent is non-compliant at target version without these changes. | BLOCKING — must PASS before declaring agent complete | `version.json` aget_version field, AGENTS.md @aget-version header, BC-NNN breaking change compliance |
| **Optional** | Capabilities each agent adopts based on context. Non-adoption does not affect version compliance. | Recommended — WARN if missing, not FAIL | New universal skills, new PATTERN_*.md files, new AGENTS.md sections |

**When a release includes breaking changes (BC-NNN)**: BC compliance is automatically Mandatory. Check DEPLOYMENT_SPEC_vX.Y.Z.yaml for the full classification table for each release.

---

## Scope

**Applies to**: Fleet-wide version migrations (minor and major releases)

**Covers**:
- Version.json updates across fleet
- AGENTS.md @aget-version updates
- Session script deployment (wake_up.py, wind_down.py, health_check.py)
- L455 AGENTS.md Invocation Verification
- Mandatory change compliance verification
- FLEET_STATE.yaml / FLEET_REGISTRY updates

**Does NOT cover**:
- Framework/template releases (see SOP_release_process.md)
- Single-agent migrations (use SOP_aget_migrate.md)
- Breaking changes requiring code modifications (see DEPLOYMENT_SPEC_vX.Y.Z.yaml BC-NNN)

---

## Prerequisites

Before starting Fleet_Migration:

1. **Framework release complete**: Target version released via SOP_release_process.md
2. **Scripts available**: Session scripts exist in framework at target version
3. **Fleet state known**: FLEET_STATE.yaml reflects current fleet
4. **Git access**: Push access to all fleet repositories
5. **gh CLI auth verified**: `gh auth status` returns exit 0 (not keyring error)

```bash
# Pre-flight auth smoke-test — catch keyring failures before migration starts
gh auth status && echo "PASS: gh auth" || echo "FAIL: gh auth — check keyring or re-authenticate (gh auth login)"
```

**Warning**: Cloud-hosted agents may return keyring errors on `gh auth status` even when auth is configured. If any agent shows a keyring error, resolve before migration (re-run `gh auth login` on that machine). Undetected auth failures cause silent gh CLI failures during migration.

---

## Dispatch Safety — field learnings, v3.28.0 cycle (2026-07-26)

**Read this before Phase 0.** Each item below cost a real incident or a wrong gate verdict during the
v3.28.0 fleet wave. They are procedure, not anecdote: every one changed how a gate closes.

### 1. A suite run during migration needs a TWO-CLAUSE behavioural gate

A migrating seat is told to run its contract suite (pre-migration baseline, then post-migration probe).
That suite can mutate the repository. Assert **both** clauses across the run:

```bash
git rev-list --count HEAD     # unchanged
git status --porcelain        # unchanged
```

**Why both.** The commit-count clause alone was adopted first and passed a run that wrote 18 files into
the live repo without committing them. Count-unchanged and tree-unchanged are different claims; a mutation
that stops short of a commit satisfies the first and violates the second.

**Why any clause at all.** A dispatched seat's suite committed to its own repository in a self-replicating
loop: the wind-down pattern ran `git add -A && git commit`, whose post-commit action re-invoked the suite.
**527 junk commits in 67 minutes, unattended.** The dispatch instruction to "run the contract suite" was
the ignition source.

> **Do not diagnose this by grepping for unguarded test call sites.** That hypothesis was filed, and both
> halves were falsified within hours: one seat carried the call sites and never detonated (not sufficient),
> another guarded every one and detonated anyway (not necessary). The mechanism was a `Path.cwd()` default
> in a vendored command module — a *product* path, not a test path. If a seat's suite mutates its repo,
> **bisect per file with the two-clause gate** rather than reasoning about which calls look unsafe.

**Run it, do not re-implement it — and do not rely on this paragraph.** `scripts/run_suite_gated.py`
enforces both clauses and bisects:

```bash
python3 scripts/run_suite_gated.py <seat-path>                      # gated run; exit 2 = mutated
python3 scripts/run_suite_gated.py <seat-path> --bisect             # every igniter, one file at a time
python3 scripts/run_suite_gated.py <seat-path> --allow-path .aget/logs/   # declare benign, still reported
```

Exit `2` means the run mutated the repository — **do not report it as a pass whatever the test result
was.** `--allow-path` declares append-only paths benign; exemptions are always printed, and the
**commit-count clause is never exemptible**. Self-test: `--self-test` (12/12).

**Why a script and not the paragraph above.** The prose was read, cited, and planned around by a
consuming supervisor seat on 2026-07-27 — which reached for grep first anyway, scoring **0-for-2 on its
hits and 0-for-3 on the real igniters**, then found all three by bisecting with the gate as oracle. Its
own retrospective: *"the upstream correction warned about precisely that and the warning didn't stop me;
the gate did."* A warning its most careful reader cites and then does not follow is decorative (L671).
That seat's incident was contained at **3 junk commits instead of 527** by the gate, not by the warning.

**One calibration from the instrument's first real run**: it fired on canonical `aget` itself, because
that suite appends to tracked logs under `.aget/logs/`. Real mutation, benign cause. Declare such paths
with `--allow-path` rather than lowering the gate — a gate that fires on every run gets disabled, and a
disabled gate protects nothing.
>
> When one file is the igniter: `--deselect` it, run the rest, and report the probe **PARTIAL, naming what
> was deselected**. Never as a clean pass.

### 2. Per-seat timeout SHALL scale with that seat's divergence count

Measured across five pilots on one release, wall-clock to completion:

| Seat divergence | Time |
|---|---|
| 0 diverged payload files | 177s · 282s · 296s |
| 2 diverged | timed out at 540s |
| 4 diverged | timed out at 540s |

Perfect separation. The cost driver is **diff-review-and-re-base** — the work the divergence-routing rules
require. A budget measured on the easy case and applied to the hard one times out precisely the seats
doing the most careful work, and a raised constant does not fix it: size the budget from the seat's
measured divergence, or dispatch outlier seats individually.

### 3. A timed-out dispatch can leave a seat WORSE than untouched

A timeout is not a no-op. One seat was killed mid-gate holding: `aget_version` pinned to the new release,
one payload file re-based, three untouched, **nothing committed**, dirty tree. It claimed a version it did
not carry, and the state was harder to see after a later commit made the tree clean.

**Therefore**: before dispatching, refuse any seat whose payload-relevant tree is already dirty — you may
be landing on top of a partial. After a timeout, **inspect the seat's tree before re-dispatching**, and
have it either complete-and-commit or roll back its own version pin. Do not clean it up from the
supervisor: that is the seat's repository.

### 4. Liveness needs TWO signals, and neither alone is safe

Dispatching into a live session races that session's writes — same tree, sequential writers, and git emits
no signal until one commits over the other.

**Both signals fail in BOTH directions.** The first published version of this table assigned one failure
direction to each signal — mtime over-reports, process under-reports. That is wrong, and the first field
use of the gate proved it wrong in under a day. Corrected 2026-07-27:

| Signal | Answers | Over-reports (false LIVE) | Under-reports (false CLEAR) |
|---|---|---|---|
| session-file mtime | "did something write here recently" | a session that just exited still reads LIVE — **2 of 4 readings**, cost a pilot slot | **a session file is written once at open, not continuously** — a long-running session that is reading and thinking goes stale and reads CLEAR. Measured: two live seats with session files **268 and 23 minutes old** under a 10-minute window. Also **blind** to a runaway writing only to `scripts/` and git |
| running process + cwd | "is a session here now" | a process parked at that cwd doing nothing else | misses a session open and thinking, having written nothing yet — and misses everything if it counts **its own ancestry** as foreign (below) |

**Gate**: refuse to dispatch if **either** fires. `CLEAR` means *no evidence of activity*, never *proved
idle*. The gate rule is unchanged by the correction above and held on first field use — it refused two
seats that an mtime-only gate would have dispatched into.

**Exclude your own ancestry, and do it by ancestry — not `getppid()`.** A liveness instrument run by the
supervisor finds the supervisor's own session at the supervisor's own repo and refuses Wave 0 forever.
The fix is not `os.getppid()`: the harness spawns a **fresh subshell per tool call**, so the parent PID
differs between calls inside one logical session. Walk the full ancestor chain and treat that set as
"us". Report the result as a distinct `SELF` state rather than silently downgrading to `CLEAR` — the
distinction is the evidence, and collapsing it is the same shape as recording a vacuous PASS as a PASS.

**Verify your matcher can match its subject.** Both defects above were found by a seat auditing its own
freshly-built instrument *before* trusting its verdict — it initially refused all seven seats. An
instrument's clean negative is only as good as its ability to match what it is looking for.

### 5. Verify the EXECUTED surface, not the delivered path

A payload file can land byte-exact at its delivered path and be invoked by nothing. Resolve what the
seat's own skills actually run — read its `SKILL.md`, do not assume `scripts/`.

**But do not infer a capability gap from a byte gap.** One seat's executed copy differed from the payload
and was declared non-green four times; measuring the release's actual delivery showed one of the two
changes already present there and the other structurally inapplicable. **Byte gap ⇒ executed-surface
differs** is sound; **⇒ capability absent** does not follow. Measure the delta, then rule.

### 6. Bound every diff read before you read it

Run `git diff --stat` (or `| wc -l`) **before** any `head -N`. A truncated diff has **no truncation
signal** — `head -30` renders identically on a 28-line delta and a 300-line one, and only one of those
conclusions is right. This decided a seat's gate status with two lines of margin nobody could see.

### 7. Report composition, not a single headline number

A migration tally of "N/M green" hides whether a seat is green by delivery, by declared-and-accepted
divergence, or by exemption. State the decomposition: *delivered X · re-based Y · exempt Z*. A single
number lets a definitional pass read as a capability claim.

---

## Migration Mechanism — plan once, re-derive at apply

The v3.29 receiving-seat experience exposed four ways a careful migration can still pass the wrong
predicate: a scalar count can hide substitution, a comparison against the incoming release can call
staleness a graft, a checker can pass only because the migration supplies its answer, and a target can
move after the operator reviewed it. The rules below make the migration a reviewable transaction rather
than a sequence of individually-approved verbs.

### M1. Plan the complete mutation set before the first write

Derive and display one manifest containing every intended mutation: seat, path, operation, source,
classification, expected hash or semantic result, and rollback. Hash the manifest. The review checkpoint
is the manifest, not each later `cp`, edit, or commit command.

At `--apply` time, re-derive the manifest from current source and target state. Refuse if its hash or any
listed precondition changed. A target `HEAD`, working tree, release correction, or source byte that moved
after review invalidates the approval; it does not become an implicit amendment.

```text
plan = derive(source, target, claimed_baseline)
display(plan, sha256(plan))
apply(expected_hash):
    current = derive(source, target, claimed_baseline)
    refuse unless sha256(current) == expected_hash
    apply current exactly
```

The manifest is an execution contract, not proof of completion. After application, verify received state
and behavior separately.

### M2. Classify at the baseline the seat claims

Compare a seat's current artifact first with the framework version recorded by that seat. If it is
byte-identical at the claimed baseline, content absent from the incoming release is staleness, not an
organic graft, and may be replaced under the migration contract. Only a difference from the claimed
baseline is evidence of local divergence requiring preserve/re-base review.

Classification order:

1. Read the seat's claimed framework version from its governed version surfaces.
2. Resolve the corresponding framework baseline.
3. Compare the live seat artifact with that baseline.
4. Classify `baseline-identical`, `local divergence`, `unreadable baseline`, or `not applicable`.
5. Only then compare with the incoming payload and select overwrite/re-base/exempt/refuse.

If the claimed baseline cannot be resolved or parsed, report `UNREADABLE`; silence is not a clean
classification.

### M3. Fix the expectation before migration

Run the incoming release's checker against the current seat before changing it. Record the check names,
applicability decisions, and results. This establishes what the incoming instrument can actually see and
the exact post-migration result expected after known payload changes.

An expectation such as "at least 15 checks" is insufficient. It can pass when a new framework check
arrives and a local check disappears. Record the ordered or normalized name set and compare sets after
application. A checker that cannot fail on a known-bad pre-migration fixture is not a conformance oracle;
route the detector defect and keep the affected result qualified.

### M4. Verify graft preservation by identity, never count

Before mutation, enumerate every accepted local graft by path and, where the artifact contains a registry
or check collection, by stable name. After mutation, require the same identities or an explicit reviewed
mapping. Count equality proves only cardinality:

```text
before = {local_check_a, local_check_b}
after  = {framework_check_c, local_check_b}
len(before) == len(after)  # true; local_check_a was still lost
```

Use name/path set difference as the V-test. A relocation is not an append: if the incoming release moves a
concept between semantic categories, preserve its meaning at the new category and reject a verbatim merge
that would make the artifact contradict itself.

### M5. Separate status predicates and name every denominator

Use these terms independently:

| Predicate | Minimum evidence |
|---|---|
| `current` | Governed version surfaces agree at the receiving seat. |
| `applicable-detection conformant` | Every applicable published detection passes, with disputed or non-discriminating detections named. |
| `received state` | Declared payload and persisted state are observed at the destination. |
| `behavioral evidence` | The selected workflow runs in the receiving environment through the documented discovery, invocation, and recovery path. |

Report composition alongside any fleet headline: delivered, re-based, exempt, disputed, and failed. State
the row-seat denominator and applicability basis. `current` does not imply conformance; conformance does
not imply received persistence; received state does not imply behavior.

### M6. A detector cannot borrow its answer from the payload without disclosure

When a detector claims a property of artifact A but concatenates or consults migration-delivered artifact
B, report both surfaces separately. A payload-engineered marker can turn every receiving seat green while
artifact A remains unchanged. At minimum emit `subject_only` and `subject_plus_payload` results and use
`subject_only` for a native-subject conformance claim.

This rule does not forbid a multi-artifact contract. It forbids naming the result as if one artifact were
measured when another supplied the passing evidence. The v3.29 M-3.29-1 marker finding is the calibration
case: correction #5 fixed distribution while making the marker half partly self-satisfying; the size half
remained discriminating.

### M7. Receiving-seat critique is an independent falsification channel

Invite the pilot seat to challenge the proposed merge, baseline, V-test, and expected result, and verify
its correction at source before accepting or disputing it. In the v3.29 Legalon migration, four receiving-
seat corrections were confirmed: relocation instead of append, name-list instead of count, incoming-
checker expectation capture, and claimed-version baseline classification.

This is a bounded observation, not an authority inversion or proof that peer critique is universally
superior to guards or self-review. The transferable rule is narrower: semantic review from the receiving
context is a distinct evidence channel, and a supervisor must not discard it merely because the dispatch
originated at the supervisor.

---

## Procedure

### Phase 0: Pre-Migration Verification

**Objective**: Confirm framework and fleet readiness

#### V0.0: Dispatch Names the Target — Wave-0 entry criterion

*Delivered by gh#1835 / v3.26 C-26-04. Provenance, not a live dependency — see §Citing issues below.*

The migration dispatch/handoff SHALL name the target version explicitly. A dispatch WITHOUT
a target version is answered with a V0.1 discovery result ("latest public release is vX.Y.Z —
confirm this is the target"), NOT with an inferred target: inference machinery defaults to
fleet-internal ground truth (peer/self versions), which cannot see the release channel and
structurally resolves to N-1 (field-evidenced 2026-07-05: verbatim dispatch "prepare fleet for
AGET migration" → v3.24.0 plan authored and validated one day after v3.25.0 shipped). The gap
is symmetric — dispatchers name the target; receivers refuse to infer it.

#### V0.1: Discover Latest Release
```bash
# Check latest release on GitHub (L723, L755)
gh release list --repo aget-framework/aget --limit 3
```
**Purpose**: Remote fleet supervisors should discover the target version from the release list, not from commit inference. Per L723: release discovery must be explicit, not inferred.

#### V0.2: Verify Framework Version
```bash
python3 -c "import json; print(json.load(open('~/github/aget-framework/aget/.aget/version.json'))['aget_version'])"
```
**Expected**: Target version matching the latest release from V0.1

#### V0.2: Verify Script Availability
```bash
ls ~/github/aget-framework/aget/scripts/{wake_up,wind_down,health_check}.py
```
**Expected**: All three scripts present

#### V0.3: Read Fleet State
```bash
python3 -c "import yaml; f=yaml.safe_load(open('~/.../FLEET_STATE.yaml')); print(f'Active: {f[\"metadata\"][\"active_agents\"]}')"
```
**Expected**: Known agent count

#### V0.4: Check for Late-Created Agents
```bash
# Identify agents created after last migration (may have missed version wave)
LAST_MIGRATION="YYYY-MM-DD"  # Date of previous fleet migration
# FLEET_GLOBS: your fleet's roots — see §Fleet-root parameterization (Phase 4); glob-miss = silent empty loop
FLEET_GLOBS=(~/github/private-*-aget ~/github/GM-*/private-*-aget)   # <— EDIT to your topology
for agent in "${FLEET_GLOBS[@]}"; do
  created=$(jq -r '.created // .discovered // "unknown"' $agent/.aget/version.json 2>/dev/null)
  if [[ "$created" > "$LAST_MIGRATION" ]]; then
    echo "LATE: $(basename $agent) created $created"
  fi
done
```
**Expected**: List of agents needing catch-up migration (may be empty)
**Action**: Include late-created agents in Phase 2 batches

**Decision_Point**: Framework ready? [GO/NOGO]

---

### Phase 0.5: Remote Supervisor Pre-Flight (CAP-MIG-017)

**When This Applies**: Migration executed on different machine from framework development.

**Objective**: Ensure local framework clone is synchronized before migration.

**Key Issue**: Your local framework clone may be stale, causing agents to incorrectly report "version X.X doesn't exist."

See: FLEET_MIGRATION_GUIDE_v3.md (Cross-Machine Pre-Flight section), L457

#### V0.5.1: Health Check (Remote Reachable)

```bash
# Find your framework clone (common locations below)
# Personal laptop: ~/github/aget-framework/aget/
# Work laptop: ~/code/aget-framework/aget/
# Server: /opt/aget/ or /srv/aget/
cd /path/to/your/aget-framework/aget

git ls-remote origin HEAD > /dev/null 2>&1 && echo "PASS: V0.5.1" || echo "FAIL: V0.5.1 - Remote unreachable"
```
**Expected**: PASS
**Fix (if FAIL)**: Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git`

#### V0.5.2: Framework Sync

```bash
cd /path/to/your/aget-framework/aget
git fetch origin && git pull origin main
```
**Expected**: Up-to-date or successful pull

#### V0.5.3: Version Verification

```bash
cat /path/to/your/aget-framework/aget/.aget/version.json | grep aget_version
```
**Expected**: Target version (e.g., "3.3.0")

#### V0.5.3b: SUBSTANCE Verification (version label ≠ payload present)

The version reading X.Y.Z confirms the *label* is set — NOT that the deployment contract is published or your source contains the release payload. A version bump does **not** copy new artifacts. Verify substance before migrating (FLEET-UPG-023 lessons):

```bash
FW=/path/to/your/aget-framework
# (a) Deployment contract published (read it — detection clauses + breaking_release):
test -f $FW/aget/DEPLOYMENT_SPEC_vX.Y.Z.yaml && echo "PASS: spec" || echo "FAIL: no DEPLOYMENT_SPEC_vX.Y.Z — STOP, do NOT relabel 'no spec' as version.json"
# (b) Your template source actually CONTAINS the release's new artifacts (list them per release notes):
#     for each new artifact: test -f $FW/template-{archetype}-aget/<path> || echo "FAIL: empty source pulls nothing — STOP"
```
**Expected**: PASS on both. **If FAIL**: STOP — migrating from an empty source, or relabeling a missing contract as a "deviation," are real observed failures (FLEET-UPG-023). Pull/escalate first.

Post-rollout, remember: **version-pass ≠ health-pass** — run the *full* `health_check`, expect pre-existing drift; and L444 coherence is **schema-aware** (manifests differ by archetype — worker top-level `version:` vs researcher `instance.version:`; a uniform grep false-flags).

#### V0.5.4: State Verification (Re-Study)

```
⚠️ If agent previously studied with stale framework:
   - Agent context is now INVALID
   - Agent may incorrectly report "version X.X doesn't exist"
   - Solution: Re-run study/research phase after git pull
   - Pattern: "study up, focus on: vX.Y upgrade"
```

**Decision_Point**: Remote environment ready? [GO/NOGO]

---

### Phase 1: Pilot Migration (Risk Validation)

**Objective**: Validate migration approach on representative agents

**Selection Criteria** (3 agents minimum, L583):
- 1 simple agent (structural validation — does the upgrade script work?)
- 1 high-value agent (signal validation — does it break what matters? e.g., professional-core, cli-aget)
- 1 high-complexity agent (divergence validation — does it handle organic customizations? e.g., supervisor-level skills)

**Anti-pattern**: Selecting only dormant/simple agents optimizes for procedural safety, not validation signal. Pilot evidence must be compelling enough for external fleet deployments.

#### Gate 1.1: Pilot Agent Migration

For each pilot agent:

```bash
AGENT_PATH=~/github/{agent-name}

# 1. Create scripts directory if needed
mkdir -p $AGENT_PATH/scripts

# 2. Deploy session scripts
cp ~/github/aget-framework/aget/scripts/wake_up.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/wind_down.py $AGENT_PATH/scripts/
cp ~/github/aget-framework/aget/scripts/health_check.py $AGENT_PATH/scripts/

# 3. Update version.json
sed -i '' 's/"aget_version": "[^"]*"/"aget_version": "X.Y.Z"/' $AGENT_PATH/.aget/version.json

# 4. Update AGENTS.md @aget-version
sed -i '' 's/@aget-version: .*/@aget-version: X.Y.Z/' $AGENT_PATH/AGENTS.md
```

#### Gate 1.2: Skill Content Sync (Conservative Protocol)

**Objective**: Sync framework skill updates to agent instances without destroying organic customizations.

**When this applies**: When the release includes skill SKILL.md changes (check RELEASE_HANDOFF for "skill updates" section).

**Why conservative**: Remote fleets have minimal visibility to outcomes. A blunt overwrite can destroy organic features (evidence-rich mode, custom project types, invocation recording, disable-model-invocation) that the agent developed through use. The classify-archive-diff-merge-verify protocol prevents silent regressions.

**Note**: ~50% of agents have `.claude/` in `.gitignore` (#317). Skill file commits require `git add -f` for these agents.

For each skill with framework updates:

```bash
AGENT_PATH=~/github/{agent-name}
TEMPLATE_PATH=~/github/aget-framework/template-{archetype}-aget
SKILL_NAME=aget-create-project  # Replace per skill

# Step 1: CLASSIFY — detect organic customizations
python3 .aget/patterns/upgrade/pre_sync_check.py \
  --baseline $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/ \
  --instance $AGENT_PATH/.claude/skills/$SKILL_NAME/

# If pre_sync_check unavailable or single-file, classify manually:
diff $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
     $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md | head -40

# Step 2: ARCHIVE — preserve current version before any changes
cp $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
   $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md.pre-vX.Y.Z

# Step 3: CLASSIFY result determines action:
```

| Classification | Organic Customizations? | Action |
|---------------|------------------------|--------|
| **Clean** (identical to prior template) | No | Safe to overwrite: `cp $TEMPLATE_PATH/...SKILL.md $AGENT_PATH/...SKILL.md` |
| **Extension** (template + additions) | Yes | **MERGE**: Add framework updates into agent's file, preserving organic sections |
| **Conflict** (incompatible changes) | Yes | **MANUAL**: Review diff, resolve conflicts, preserve organic intent |

```bash
# Step 4: For CLEAN agents — direct copy
cp $TEMPLATE_PATH/.claude/skills/$SKILL_NAME/SKILL.md \
   $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md

# Step 4: For EXTENSION/CONFLICT agents — manual merge
# Read both files, identify framework additions vs organic features
# Add framework steps into agent's file preserving organic content

# Step 5: VERIFY — confirm framework updates present AND organic features preserved
echo "=== Framework updates ==="
grep -c "Step 0\|Step 3.6\|Step 3.7\|Step 3.8\|Step 8" \
  $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md
# Expected: 5+ matches for D62

echo "=== Organic features ==="
# Check for agent-specific features (varies per agent)
grep -c "disable-model-invocation\|evidence-rich\|gap\|record_invocation" \
  $AGENT_PATH/.claude/skills/$SKILL_NAME/SKILL.md
# Expected: matches for any organic features the agent had

# Step 6: COMMIT (use -f if .claude/ is gitignored)
git -C $AGENT_PATH add -f .claude/skills/$SKILL_NAME/SKILL.md \
  .claude/skills/$SKILL_NAME/SKILL.md.pre-vX.Y.Z
```

**Decision_Point**: Skill sync verified for pilot agents? [GO/NOGO]

#### Gate 1.3: L455 Verification (V-MIG-AGENTS Tests)

```bash
# V-MIG-AGENTS.1: No stale patterns
! grep -q "sanity-check" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: L455 violation"

# V-MIG-AGENTS.2: v3.1+ flags documented
grep -q "\-\-json\|\-\-dir" $AGENT_PATH/AGENTS.md && echo "PASS" || echo "FAIL: Missing --json docs"

# V-MIG-AGENTS.3: Housekeeping script works
python3 $AGENT_PATH/scripts/health_check.py --json --dir $AGENT_PATH | jq -r '.status'
```
**Expected**: PASS, PASS, healthy/warning

#### Gate 1.4: Pilot Commit

```bash
git -C $AGENT_PATH add -A
git -C $AGENT_PATH commit -m "feat: Migrate to AGET vX.Y.Z

- Deploy session scripts (wake_up.py, wind_down.py, health_check.py)
- Update version.json to vX.Y.Z
- Update AGENTS.md @aget-version

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Decision_Point**: Pilot successful? [GO/NOGO]

---

### Phase 2: Main Portfolio Migration

**Objective**: Migrate Main portfolio agents (typically largest)

**Batching Strategy**: 3-4 agents per batch for manageable commits

#### Gate 2.N: Batch Migration

For each batch:
1. Deploy scripts to all batch agents
2. Update version.json for all
3. Update AGENTS.md for all
4. Run V-MIG-AGENTS tests for all
5. Fix any L455 violations
6. Commit batch

**Decision_Point**: Main portfolio complete? [GO/NOGO]

---

### Phase 3: Secondary Portfolio Migration

**Objective**: Migrate remaining portfolios (CCB, RKB, PREDICTIONWORKS, etc.)

#### Gate 3.1: Per-Portfolio Batches

Migrate each portfolio as a batch:
- CCB (sensitive): Extra verification
- RKB: Check for symlink edge cases
- PREDICTIONWORKS: Standard procedure

#### Gate 3.2: Archive/Deprecation Handling

If portfolio is deprecated:
```bash
# Option A: Mark delegated in FLEET_STATE
# Option B: Archive to ~/archive/
tar -czvf ~/archive/GM-{PORTFOLIO}-archived-$(date +%Y-%m-%d).tar.gz ~/github/GM-{PORTFOLIO}
rm -rf ~/github/GM-{PORTFOLIO}
```

Update FLEET_STATE.yaml:
```yaml
{portfolio}:
  status: archived
  archived_date: 'YYYY-MM-DD'
  archived_location: ~/archive/{filename}.tar.gz
```

**Decision_Point**: Secondary portfolios complete? [GO/NOGO]

---

### Phase 4: Fleet Validation

**Objective**: Verify fleet-wide consistency

#### Gate 4.0: Behavioral Verification — Rung 4 — BLOCKING at pilot, per-seat elsewhere

*Delivered by gh#1881 / L1165, SOP v1.7.0. Provenance, not a live dependency — see §Citing issues below.*

**"31/31 upgraded ≠ 31/31 unregressed"** (supervisor verdict, v3.26 sweep). The ladder
dispatch → receipt → state confirms LANDING; this rung confirms RUNNING. Per migrated seat:

1. **Behavioral smoke probes** (1–3 per payload feature, derived from DEPLOYMENT_SPEC M-rows;
   the dispatch's §Behavioral Smoke section names them): run each new signal once ON THE
   EXECUTED SURFACE ("after upgrade, wake-up prints the new line"), never a file-existence grep.
2. **Post-payload test suite**: `python3 -m pytest tests/ -q` at the seat — symbol moves strand
   local imports invisibly (it-consultant CI-red exhibit; absorbs their L239: BEFORE closing a
   symbol-move migration, grep the seat's own consumers for the moved symbols).
3. **Executed-surface parity**: for every dual-basename payload target (`scripts/<name>.py` vs
   `.aget/patterns/session/<name>.py`), verify the copy the config INVOKES carries the payload —
   version-says-current-behavior-is-old is the cli-aget C-26-01 dead-on-arrival class. Absorbs
   cli-aget L756 (sync-survival ext guard) as the standing seat-side pattern.
4. **Evidence bar (amends the L656 pilot row)**: a pilot confirmation SHALL include ≥1 recorded
   behavioral-probe RESULT — received-state disk verification alone no longer confirms.

#### Fleet-root parameterization (v1.7.1 — REQUIRED before running any Gate 4.x loop)

The agent-enumeration globs below are PARAMETERS, not portable defaults — the literal
`~/github/private-*-aget` pattern encodes ONE fleet's filesystem topology. On any other
machine (e.g. a remote fleet rooted at `~/code/<org>/`) the glob matches NOTHING and the
loop **silently passes an empty set** — a wave-boundary gate that green-lights zero agents
(same silent-skip class as the v1.45 template-glob fix in SOP_release_process). Set your
fleet's roots explicitly and VERIFY the count before trusting any Gate 4.x output:

```bash
FLEET_GLOBS=(~/github/private-*-aget ~/github/GM-*/private-*-aget)   # <— EDIT to your topology
ls -d "${FLEET_GLOBS[@]}" 2>/dev/null | wc -l   # MUST equal your known agent count; 0 or short = STOP
```

#### Gate 4.1: Batch Housekeeping Validation

```bash
for agent in "${FLEET_GLOBS[@]}"; do
  result=$(python3 $agent/scripts/health_check.py --json --dir $agent 2>&1)
  status=$(echo "$result" | jq -r '.status')
  echo "$(basename $agent): $status"
done
```
**Expected**: All healthy or warning (no errors)

#### Gate 4.2: Version Consistency Check

```bash
for agent in "${FLEET_GLOBS[@]}"; do
  ver=$(jq -r '.aget_version' $agent/.aget/version.json)
  echo "$(basename $agent): $ver"
done | grep -v "X.Y.Z" && echo "DRIFT DETECTED" || echo "ALL CONSISTENT"
```
**Expected**: All at target version

#### Gate 4.2.1: Migration History Check (V-MIG-HISTORY)

```bash
# Verify migration_history was updated per-agent
TARGET_VERSION="X.Y.Z"
for agent in "${FLEET_GLOBS[@]}"; do
  last_to=$(jq -r '.migration_history[-1].to_version // "none"' $agent/.aget/version.json 2>/dev/null)
  if [[ "$last_to" != "$TARGET_VERSION" ]]; then
    echo "MISSING: $(basename $agent) - last recorded: $last_to"
  fi
done
```
**Expected**: All agents show target version in migration_history
**Action**: If gaps found, update version.json migration_history arrays

#### Gate 4.3: FLEET_STATE Update

```bash
# Update all agent versions
sed -i '' 's/version: v.*/version: vX.Y.Z/g' ~/.../FLEET_STATE.yaml

# Update metadata
sed -i '' 's/v3_migration_status:.*/v3_migration_status: complete/' ~/.../FLEET_STATE.yaml
sed -i '' "s/last_updated:.*/last_updated: '$(date +%Y-%m-%d)'/" ~/.../FLEET_STATE.yaml
```

**Decision_Point**: Fleet validated? [GO/NOGO]

---

### Phase 5: Finalization

#### Gate 5.1: Commit FLEET_STATE

```bash
git -C ~/github/my-supervisor-agent add .aget/fleet/FLEET_STATE.yaml
git -C ~/github/my-supervisor-agent commit -m "feat: Complete Fleet vX.Y.Z Migration"
git -C ~/github/my-supervisor-agent push
```

#### Gate 5.2: Session Log

Create session log in `sessions/SESSION_YYYY-MM-DD_fleet_vX.Y.Z_migration.md`

#### Gate 5.3: PROJECT_PLAN Finalization (if applicable)

- Mark status: COMPLETE
- Add retrospective section
- Record KR achievement

#### Gate 5.4: FLEET_REGISTRY Update (BLOCKING Completion Criterion)

FLEET_REGISTRY must be updated before declaring migration complete. This is a **BLOCKING** gate — a migration without FLEET_REGISTRY update is considered incomplete even if all agents are at target version.

```bash
# Update FLEET_REGISTRY with migration record
# Location varies by supervisor; common paths:
# - .aget/fleet/FLEET_REGISTRY.yaml
# - .aget/fleet/FLEET_STATE.yaml (if consolidated)

python3 -c "
import json, yaml, datetime
registry = yaml.safe_load(open('.aget/fleet/FLEET_REGISTRY.yaml'))
registry['last_migration'] = {
  'version': 'X.Y.Z',
  'date': '$(date +%Y-%m-%d)',
  'agent_count': 0,  # fill actual count
  'method': 'centralized'
}
print(yaml.dump(registry))
"
```

**V5.4.1: FLEET_REGISTRY records target version**
```bash
grep "version: X.Y.Z" .aget/fleet/FLEET_REGISTRY.yaml && echo "PASS" || echo "FAIL"
```
**Expected**: PASS
**BLOCKING**: Do NOT mark migration COMPLETE if FAIL.

**Decision_Point**: Project complete? [COMPLETE]

---

## Rollback Criteria

Rollback is triggered when any of the following conditions occur and cannot be resolved within the session:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| V-MIG-AGENTS failures | >10% of fleet fails after remediation | Rollback affected agents to prior version |
| BC-NNN compliance failure | Any agent non-compliant after 2 remediation attempts | Escalate to framework; do not mark complete |
| Health check errors (not warnings) | >5% of fleet shows error | Rollback and investigate root cause |
| gh auth failure (cloud agents) | Any agent cannot authenticate | Pause migration; resolve auth before continuing |

**Rollback procedure** (per-agent):
```bash
AGENT_PATH=~/github/{agent-name}
PRIOR_VERSION="X.Y.Z-1"

# 1. Revert version.json
sed -i '' "s/\"aget_version\": \"[^\"]*\"/\"aget_version\": \"$PRIOR_VERSION\"/" $AGENT_PATH/.aget/version.json

# 2. Revert AGENTS.md
sed -i '' "s/@aget-version: .*/@aget-version: $PRIOR_VERSION/" $AGENT_PATH/AGENTS.md

# 3. Restore prior scripts (from framework git history)
FRAMEWORK_PATH=~/github/aget-framework/aget
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/wake_up.py" > $AGENT_PATH/scripts/wake_up.py
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/wind_down.py" > $AGENT_PATH/scripts/wind_down.py
git -C $FRAMEWORK_PATH show "v$PRIOR_VERSION:scripts/health_check.py" > $AGENT_PATH/scripts/health_check.py

# 4. Commit rollback
git -C $AGENT_PATH add .aget/version.json AGENTS.md scripts/
git -C $AGENT_PATH commit -m "rollback: Revert to AGET v$PRIOR_VERSION (migration issue)"
```

**Partial migration**: If > 50% of agents migrated successfully, do not roll back the successful cohort — document partial state in session log and continue remediation in next session.

---

## Troubleshooting

### L455 Violation (V-MIG-AGENTS.1 FAIL)

**Symptom**: Agent has stale `sanity-check` pattern in AGENTS.md

**Fix**:
1. Remove/replace stale invocations
2. Add Housekeeping Commands section with correct syntax:
```markdown
## Housekeeping Commands

### Sanity Check
When user says "sanity check":
- Run: `python3 scripts/health_check.py` (human-readable output)
- Or: `python3 scripts/health_check.py --json` (JSON output)
```

### Symlink Edge Case

**Symptom**: `mkdir: scripts: Not a directory`

**Fix**:
```bash
rm $AGENT_PATH/scripts  # Remove symlink
mkdir -p $AGENT_PATH/scripts  # Create real directory
```

### Shell Aliasing Issues

**Symptom**: `command not found: mkdir` or `rm` prompts

**Fix**: Use explicit paths:
```bash
/bin/mkdir -p $AGENT_PATH/scripts
/bin/rm -f $AGENT_PATH/scripts
```

### Remote Supervisor Pre-Flight Issues (CAP-MIG-017)

| Problem | Cause | Solution |
|---------|-------|----------|
| V0.5.1 FAIL: Remote unreachable | Network/SSH issue | Use HTTPS: `git remote set-url origin https://github.com/aget-framework/aget.git` |
| V0.5.2 FAIL: Pull failed | Merge conflicts, uncommitted changes | `git stash` or commit first, resolve conflicts |
| V0.5.3 FAIL: Framework stale | Pull failed silently | Check git status, try `git reset --hard origin/main` |
| Agent says "version doesn't exist" | Studied with stale framework | Re-study after pull: `"study up, focus on: vX.Y upgrade"` |
| V0.5.4: Context invalid | Proceeded without re-study | Session restart with fresh study phase |

See: FLEET_MIGRATION_GUIDE_v3.md (Cross-Machine Pre-Flight), L457

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Version homogeneity | 100% | All agents at target version |
| Validation passing | 100% | All housekeeping --json pass |
| L455 compliance | 100% | No stale invocation patterns |
| Zero regressions | 0 failures | No broken deployments |

---

## Post-Migration: Ongoing Health Monitoring

After fleet migration completes, supervisors are recommended to establish a weekly fleet health check routine. Two independent fleet supervisors converged on the same design independently (L831 cross-fleet spec signal), indicating this is a framework-level best practice.

**Recommended pattern**: Weekly RemoteTrigger agent running:
1. `health_check.py --json` against each agent
2. CORRECTION commit monitor (grep `\(CORRECTION\)` in recent git log)
3. Summary report to supervisor

See: `docs/patterns/PATTERN_weekly_fleet_health_monitor.md` (framework-recommended pattern)

**Prerequisites before deploying the routine**:
- Fix #1166: Remove `Write` tool from routine (not needed for read-only health checks)
- Validate CORRECTION grep pattern: `\(CORRECTION\)` (parenthesized form, not plain `CORRECTION`)
- Confirm auth smoke-test passes on target machine (keyring issue risk)

---

## Citing issues — provenance vs. live dependency

An issue reference in this document is one of two speech acts, and **consuming seats run automated
citation gates that cannot tell them apart from context**. Write the distinction explicitly:

| Intent | Form | What a gate should do |
|---|---|---|
| **Provenance** — the issue that *delivered* this rule; usually CLOSED, and correctly so | `Delivered by gh#N` · `Origin: gh#N` | ignore; a CLOSED state is expected |
| **Live dependency** — this rule is waiting on that issue | `Blocked on gh#N` · `Pending gh#N` | flag if the issue is CLOSED |

**Never put a bare `gh#N` in a heading**, and never place one in the same parenthetical as an
enforcement word (`BLOCKING`, `MANDATORY`). Adjacency is all an automated gate has.

**Why this section exists.** `Gate 4.0`'s heading read
`(v1.7.0, gh#1881/L1165 — BLOCKING at pilot, per-seat elsewhere)`. `gh#1881` is provenance — it is the
issue that *delivered* Rung 4, CLOSED 2026-07-18 — and `BLOCKING` describes the **gate's** enforcement
level, not the issue's state. On 2026-07-27 a consuming supervisor in another fleet adopted this file
verbatim and its citation gate blocked the commit as a stale-blocker citation. That seat's judgment was
correct in both directions: it verified `gh#1881` first-party, and it declined to edit adopted canonical
text to satisfy a local hook, because a hand-patched copy forks from canonical — a worse defect than the
citation. It committed with `--no-verify` and **disclosed that in the same turn**, in its plan's risk
table and its commit message.

The defect was ours. A reader can infer speech-act class from surrounding prose; an instrument cannot,
and every consuming seat runs one. Same failure class as quoting a `Last reviewed:` line to ground a
requirement — the right words in the wrong speech-act class — here at machine scale, at every seat, on
every adoption.

**Scope**: this file. Applying the convention across canonical `sops/` and `specs/`, and adding a
validator that flags a bare `gh#N` in a heading, is **owed, not done**.

---

## References

- AGET_RELEASE_SPEC.md (version types, deployment scope)
- SOP_release_process.md (framework releases - precedes fleet migration)
- DEPLOYMENT_SPEC_vX.Y.Z.yaml (mandatory/optional change classification per release)
- L455: AGENTS.md Invocation Verification
- L457: Cross-Machine Pre-Flight
- PATTERN_weekly_fleet_health_monitor.md (post-migration health routine)
- PROJECT_PLAN_fleet_v3.2_migration.md (graduation source)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.9.0 | 2026-08-03 | **Migration Mechanism + execution-model receipt** — canonicalizes the v3.29 receiving-seat corrections after source review: hash-bound plan/apply transaction with re-derivation and drift refusal; classification at the version the seat claims; incoming-checker expectation capture; graft identity/name-list verification instead of scalar count; separate current/conformant/received/behavior predicates and composition denominators; subject-only vs payload-supplied detector provenance; and receiving-seat critique as a bounded independent falsification channel, not an authority inversion. The execution-model section now requires a pre-dispatch authorization/permission receipt. Evidence: private-first `gh#2119`; marker-provenance calibration: private-first `gh#2103`. Prepared locally under v3.29 release-plan Gate 4R1; publication is separately governed by L735. |
| 1.8.2 | 2026-07-27 | **§Dispatch Safety item 1 gains a runnable instrument** — `scripts/run_suite_gated.py` (two-clause gate + per-file `--bisect` + `--allow-path` declared-benign exemptions that are always reported; commit-count clause never exemptible; `--self-test` 12/12). Reason: the item-1 prose was measured **ineffective on its most careful reader** — a consuming supervisor seat read it, cited it, built a plan around it, and reached for grep anyway (0-for-2 on hits, 0-for-3 on the real igniters), finding all three only by bisecting with the gate as oracle. Decorative-warning closure per L671. First real run of the instrument fired on canonical `aget` itself (suite appends to tracked `.aget/logs/`) — recorded as the calibration case for `--allow-path` rather than as a reason to weaken the gate. |
| 1.8.1 | 2026-07-27 | **Corrections from v1.8.0's first field use, all consumer-found.** (a) §Dispatch Safety item 4's failure-direction table was **wrong**: it assigned one direction per signal (mtime over-reports, process under-reports); both signals fail both ways. mtime **under**-reports because a session file is written once at open, not continuously — measured at two live seats with session files 268 and 23 minutes old under a 10-minute window, which an mtime-only gate would have dispatched into. The **gate rule is unchanged and held**; only its explanation was wrong. Item 4 also gains the own-ancestry exclusion (walk the ancestor chain — `getppid()` is insufficient because the harness spawns a fresh subshell per tool call) and the `SELF`-as-distinct-state rule. (b) New **§Citing issues** — provenance (`Delivered by gh#N`) vs. live dependency (`Blocked on gh#N`), no bare `gh#N` in headings, never beside an enforcement word. `Gate 4.0` and `V0.0` headings reformed accordingly. A consuming seat's citation gate blocked on `gh#1881` cited as provenance in Gate 4.0's heading beside the word `BLOCKING`; the defect was ours, not the gate's. Cross-`sops/`/`specs/` application and a heading validator are **owed, not done**. |
| 1.8.0 | 2026-07-26 | **§Dispatch Safety added** — seven field learnings from the v3.28.0 wave, each costing a real incident or a wrong gate verdict: two-clause behavioural gate for suite runs (a one-clause version passed a run that mutated the repo); per-seat timeout scaled to divergence count (0-diverged seats 177–296s, diverged seats both blew 540s — perfect separation); timed-out dispatch can leave a seat version-pinned with no payload and a dirty tree; two-signal liveness (mtime over-reports and is blind to non-session writes, process-check under-reports); executed-surface verification **with** the caution that a byte gap does not imply a capability gap; bounded diff reads (`--stat` before `head -N` — a truncated diff has no truncation signal); composition reporting instead of a single N/M headline. Also records that the "unguarded test call sites" hypothesis for the self-replicating commit loop was **falsified in both directions** and names the bisect method that found the real cause. |
| 1.7.1 | 2026-07-18 | FLEET_GLOBS parameterization; silent-empty-set gate fix. |
| 1.7.0 | 2026-07-18 | Rung-4 behavioural verification — M-row smoke probes, post-payload suite (`it-consultant:L239`), executed-surface/dual-basename parity (`cli-aget:L756`), L656 pilot evidence bar. |
| 1.6.0 | 2026-05-02 | Wave Sequencing (SD-3 residual). |

> Entries before 1.6.0 predate this table; see `git log -- sops/SOP_fleet_migration.md`.

| 1.7.1 | 2026-07-18 | **Fleet-root parameterization** — Gate 4.1/4.2/4.2.1 + V0.4 agent-enumeration globs converted from hardcoded `~/github/private-*-aget` literals to an explicit `FLEET_GLOBS` parameter with a MANDATORY count-verification pre-step. Root cause: the literals encode one fleet's filesystem topology; on any other machine the glob matches nothing and every Gate 4.x loop silently passes an empty set (v1.45 silent-skip class at the SOP layer). Field-evidenced 2026-07-18: a remote fleet rooted at `~/code/<org>/` ruled wholesale adoption of this SOP — as written, its wave-boundary gates would have green-lit zero agents. |
| 1.7.0 | 2026-07-18 | Gate 4.0 Behavioral Verification (Rung 4) — smoke probes from M-rows + post-payload test suite (absorbs it-consultant L239 consumer-grep) + executed-surface parity incl. dual-basename drift (absorbs cli-aget L756; C-26-01 exhibit) + L656 pilot evidence bar (≥1 behavioral result). gh#1881/L1165; built v3.27 G2.1. |

### v1.6.0 (2026-05-02)

- **Added**: Wave Sequencing section — Wave 0 (supervisor self) → Wave 1 (pilots) → Wave 2 (full fleet); wave-to-phase mapping; wave-boundary V-tests; wave-skip prohibition without principal approval; wave-boundary rollback procedure
- **Rationale**: Closes SD-3 wave-sequencing residual surfaced by Gate 1 entry-time scope re-check (F-AUDIT-REL-G1-001, plan v1.0.11). v1.5.0 covered 5/6 SD-3 required sections; wave sequencing was the absent 6th. Sequencing was implicit in Phase 0.5/Phase 1 ordering but not named or constraint-bound.
- **Sources**: VERSION_SCOPE_v3.16.0 row #2 SD-3, plan G1.1 deliverable (PROJECT_PLAN_v3.16.0_release_v1.0.md v1.0.11)

### v1.5.0 (2026-04-26)

- **Added**: Execution Model section — centralized by default (principal decision 2026-04-26); distributed requires explicit principal approval
- **Added**: Mandatory vs Optional Change Classification section — Mandatory (BLOCKING V-tests), Optional (WARN, not FAIL); references DEPLOYMENT_SPEC_vX.Y.Z.yaml
- **Added**: Prerequisites item 5 — gh auth smoke-test; addresses cloud-hosted keyring failure risk (FLEET-UPG-014 finding)
- **Added**: Gate 5.4: FLEET_REGISTRY Update as BLOCKING completion criterion (FLEET-UPG-014 D1 gap)
- **Added**: Rollback Criteria section — 4 triggers, per-agent rollback procedure, partial migration guidance
- **Added**: Post-Migration: Ongoing Health Monitoring section — weekly fleet health monitor recommendation (SD-6; L831 cross-fleet convergence, two independent supervisors)
- **Updated**: Scope section — added Mandatory change compliance and FLEET_REGISTRY to Covers; updated Does NOT cover
- **Updated**: References section — added DEPLOYMENT_SPEC and PATTERN_weekly_fleet_health_monitor
- Implements SD-3, SD-4 (VERSION_SCOPE_v3.16.0 directives 2026-04-26)

### v1.3.0 (2026-03-14)

- Added Gate 1.2: Skill Content Sync (Conservative Protocol)
- 6-step classify-archive-diff-merge-verify-commit protocol
- Clean/Extension/Conflict classification determines sync strategy
- Preserves organic customizations during framework skill updates
- Documents .claude/ gitignore workaround (git add -f, #317)
- Renumbered Gates 1.2→1.3, 1.3→1.4
- Implements #441 (SOP skill sync phase gap)
- Validated by: FLEET-UPG-006 supervisor D62 self-remediation (2026-03-14)

### v1.2.0 (2026-01-11)

- Added Phase 0.5: Remote Supervisor Pre-Flight (CAP-MIG-017)
- Added V0.5.1-V0.5.4: Health check, framework sync, version verification, state verification
- Added troubleshooting section for remote supervisor issues
- Cross-reference to FLEET_MIGRATION_GUIDE_v3.md Cross-Machine Pre-Flight section
- Implements CAP-MIG-017 (7 requirements)

### v1.1.0 (2026-01-07)

- Added V0.4: Late-created agent detection (Phase 0)
- Added Gate 4.2.1: V-MIG-HISTORY migration_history per-agent check
- Created L455, L457 learning documents in `docs/learnings/`
- Cross-supervisor feedback integration (multi-fleet validation)

### v1.0.0 (2026-01-05)

- Initial SOP graduated from PROJECT_PLAN_fleet_v3.2_migration.md
- Based on patterns from v2.12.0 LTS, v3.0.0, v3.2.1 migrations
- L455 V-MIG-AGENTS tests integrated
- Troubleshooting section from v3.2.1 learnings

---

## Graduation History

```yaml
graduation:
  source: "PROJECT_PLAN_fleet_v3.2_migration.md"
  pattern_executions:
    - v2.12.0_LTS_Convergence (2025-12-26)
    - v3.0.0_Migration (2025-12-27)
    - v3.2.1_Fleet_Migration (2026-01-05)
  trigger: "L436 - Pattern executed successfully 3 times"
  rationale: "Repeatable fleet migration procedure warranted formalization"
```

---

*SOP_fleet_migration.md — Fleet version migration procedure for AGET framework*
