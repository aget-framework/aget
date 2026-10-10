# SOP: Fleet Migration

**Version**: 1.10.8
**Status**: Active
**Created**: 2026-01-05
**Updated**: 2026-10-06
**Owner**: aget-framework
**Implements**: CAP-MIG-017 (Remote Supervisor Upgrade), SD-3 wave-sequencing (v1.6.0)
**Related**: L455 (AGENTS.md Invocation Verification), L457 (Cross-Machine Pre-Flight), AGET_RELEASE_SPEC, prior internal authoring plan

---

## Purpose

Standard operating procedure for migrating fleet agents to new AGET framework versions. Ensures consistent deployment of version updates, session scripts, and validation across all active agents.

The migration kit's test-body witness requires Python 3.12+ (`sys.monitoring`); on Python 3.10/3.11 a run needing that witness returns INCONCLUSIVE by design (weekly-train:R15).

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
after review invalidates the approval; it does not become an implicit amendment. (In the kit, B7 compares each listed write's `pre` bytes, each `noop` file's `post` bytes and the member's HEAD with the list; held files and the rest of the working tree are not compared. B8's launcher also refuses a moved HEAD. Keeping the rest of the working tree unchanged at B7 remains an operator rule.)

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
its correction at source before accepting or disputing it. In the v3.29 a downstream fleet migration, four receiving-
seat corrections were confirmed: relocation instead of append, name-list instead of count, incoming-
checker expectation capture, and claimed-version baseline classification.

This is a bounded observation, not an authority inversion or proof that peer critique is universally
superior to guards or self-review. The transferable rule is narrower: semantic review from the receiving
context is a distinct evidence channel, and a supervisor must not discard it merely because the dispatch
originated at the supervisor.

---

## Kit Batch Procedure (the migration kit; since v1.10.0)

**What this is.** The procedure a supervisor runs, batch by batch, with the migration kit the release ships at
`scripts/migration_kit/` (tests at `tests/migration_kit/`). It carries the batch procedure one supervisor converged on
while migrating its own fleet to v3.35.0, made release-neutral. The phases below (pilot, main, secondary) still
decide **which** Agets go in which batch; this section decides **how** a batch runs. A batch is run from this section
alone: if you need another document to run one, record which one in B13, because that is a gap in this section.

**Which command-line tool.** (The released tools differ from the rehearsed ones by the eight behaviour fixes in history row 1.10.6 and the three fixes after the first outcome test; all are covered by tests.) The kit is built, tested and rehearsed with Claude Code only, for the supervisor's
session and for receivers' sessions. The typed-line check, the launcher and the receiver watcher read Claude Code's
session transcripts and launch settings. A session run with another tool is outside what this release has shown to
work: record it in B13 as a deviation, and do not read a refusal there as a defect of that tool.

Three further fixes made after the first outcome test are covered by failing-first tests: the launcher accepts the null apply receipt that B1 writes before apply, for packet reading and baseline launches, while a migration launch still needs a receipt; parallel members can create their shared contained environment without a directory-creation collision, and links or non-directories still refuse; and default packet and confirmation folders now sit beside the batch packet, under `<packet folder>/<release>/packets/` and `<packet folder>/<release>/runs/`, with the explicit environment overrides retained. The packet folder must lie outside every git repository, every member and the framework clones. The second outcome test ran on 2026-10-06: a fresh template-built supervisor took two worker members from 3.35.1 to v3.36.0 through apply, launch, push to local remotes and the ledger. Its result was FAIL: P3 exceeded the principal-line count and P6 exceeded the principal-wait time. The principal accepted that FAIL as named limits under weekly-train:R59, including F-3/F-5/F-6/F-8 and the hooks refusal; F-5 was subsequently fixed by the cache-free default. Supervisor-template members stay INCONCLUSIVE. This fixture run is not evidence of real-fleet deployment or GitHub continuous integration.

**Set up once per release** (from your supervisor repository's root):

| Setting | How | Why |
|---|---|---|
| Get the kit | copy `scripts/migration_kit/` from your framework clone, checked out at the release that ships the kit (the release you migrate *with*; the kit need not exist at the tag of the release you migrate *to*), into your supervisor repository at the same path, and commit it, naming the clone's commit in the message | The tools resolve your records, transcripts and identity from the repository they sit in |
| What the kit needs installed | `python3 -m pip install -r scripts/migration_kit/requirements.txt` (a YAML library; the supervisor template declares only the test runner) | Without it eight tools stop at import, even for `--help`: `fleet_ledger.py`, `census_fleet_ci.py`, `wave_readiness.py`, the three B1 prepare tools (`prepare_batch.py`, `prepare_launch.py`, `prepare_write_list.py`), `rehearse_batch2.py` and `rehearse_repair.py` |
| Your fleet register | `.aget/fleet/FLEET_STATE.yaml`, committed in your repository before anything else: a `fleet:` map whose groups list `agents`, each with `agent_name` and `location` | The ledger, `prepare_batch.py` and `prepare_launch.py` read it at the commit named by `register_pin`; the own runs of `census_fleet_ci.py`, of `wave_readiness.py` (which stops before reading it when a local script it needs is absent from `scripts/`) and of `verify_extension_survival.py` when run without `--location` read the working-tree file; a supervisor built from the template has no register until it writes one |
| Release target | `.aget/migration_target.json` with `from` and `to`, and for the fleet tools `register_pin` (the commit of *this* repository that holds the fleet register you migrate from) and `pinned_members` (the number of members that register lists, whatever the size of a batch). The `AGET_MIGRATION_*` variables override the file | The kit carries no default release; the prepare, plan, apply, packet-rehearsal, push, ledger and readiness tools (nine) stop without a target and say so; the others, among them `launch_batch.py`, `record_authority.py`, `rehearse_v37.py` and `suite_at_commit.py`, make no such check |
| The framework clones | one folder holding the core clone `aget/` and each `template-*-aget/` clone your fleet uses, every one with the source and the target release tags fetched. Name the folder as `framework_root` in `.aget/migration_target.json` (default `~/github/aget-framework`; `AGET_FRAMEWORK_ROOT` overrides) | The prepare tools read each release's bytes from these clones at their tags, so B0 and B1 cannot pass without them. Set it in the file: shell state does not persist between a session's commands, and an `export ...;` prefix stops the session rules from matching |
| Run root | choose and record an absolute sibling folder beside your supervisor repository, e.g. `<supervisor-repo>/../<supervisor-repo-name>-migration-runs/`, outside every git repository, every member and the framework root and clones. The supervisor creates it once with `mkdir -p <run-root>` before B0 | The supervisor session needs write permission for this named folder, including creating each batch folder and copying durable files at B13. `batch_rules.json` covers only three kit commands; it does not authorize `mkdir` or archive-copy commands, which use the session's normal permission checks |
| Your supervisor's name | read from your `.aget/version.json` `agent_name`; override with `AGET_MIGRATION_SUPERVISOR` | Receiver prompts name the supervisor that launched them |
| Your batch-line prefix | `GO supervisor - ` by default; set `AGET_MIGRATION_LINE_PREFIX` (e.g. `GO overseer - `) if your supervisor has another name | The typed-line check on a push, and on a launch without `--copy-root`, accepts only a line that starts with it |
| Where your transcripts are | derived from your repository path; set `AGET_MIGRATION_PROJECTS_DIR` if your session runs elsewhere | The typed-line check reads them |
| The batch session | from your supervisor root, start it with `claude --settings <framework clone>/scripts/migration_kit/batch_rules.json` (the rules name the kit by its path in your repository, so the file can be read from the clone before the kit is copied; see `BATCH_SESSION.md`) | Narrow allow rules for one session only: nothing persists and nothing needs removing. Each rule covers its command with any arguments. The tools they name call the typed-line check, except `launch_batch.py --launch --copy-root`, which makes none and instead refuses a folder that is not apart from the member's own folder, in which git would act on another working tree or git folder, that lacks the marker file `rehearse_v37.py` writes for this packet and member, has a git remote, or is not at the packet's HEAD (B3). B3's rehearsal uses that form. The marker is a plain file that anyone able to write it can forge, so using that form nowhere else stays an operator rule, enforced by the tool only as far as those tests go. A session cannot see its own launch settings, so confirm them: `ps -o args= -p $PPID`, run in the session, prints the session's own command line, which must show `--settings` |
| Records | `data/<slug>_ledger/records.json` (`<slug>` = `v` + the target's major and minor digits, e.g. `v336`) | Authority, receipts, overrides and deviations, each with its source. Create it once, containing `{}`: `record_authority.py` stops if it is missing. Commit it with the kit; at B13, commit the durable batch archive described below, while the live batch folder stays outside the repository |

Run the kit as `python3 scripts/migration_kit/<tool>.py ...` from the repository root. For the three tools the session
rules name (`launch_batch.py`, `push_batch.py`, `record_authority.py`) the command must **begin** with
`python3 scripts/migration_kit/`: anything in front of it (`cd <folder> &&`, `VAR=...;`, `env -u ...`, `export ...;`) stops the
rule from matching, and the permission checker decides in its place. The other tools may be chained. `launch_batch.py`,
`push_batch.py` and `suite_at_commit.py` remove the variables whose names end in `API_KEY` from the environment of the
sessions (launch and push) and the suite run (B8a) they start; two other runs keep them (see Network and cost).
Below, `<run-root>` is the sibling folder named in setup. Before B1, the supervisor creates the batch's own
folder `B` with `mkdir -p <run-root>/migration/<slug>/batchN`, outside every git repository, every member and the
framework root and clones. Use its absolute path for the `B/...` arguments below;
every `--evidence` is passed explicitly. B1 defaults to `B/<release>/packets/` for staged packets, and the launcher
defaults to `B/<release>/runs/` for confirmation clones. `AGET_MIGRATION_PACKET_BASE` and `AGET_MIGRATION_WORK`
remain explicit overrides; their folders must pass the same outside-repository and non-overlap checks.

**The migration's record.** Before B0, start one record of the migration in your repository (called "the plan" below):
any document your own governance accepts. It holds one entry per batch (B13) and, from the start, the close-out rows
of Gate 5.5 (its step 1). Nothing else in this section creates it.

**What the kit touches outside your repository.** It reads your session's transcripts under `~/.claude/projects/`; the
headless sessions of B3, B6, B8 and B10 (the push session) write their own transcripts there; B8a clones members under
`~/.cache/aget-suite-at-commit/`, and B2's reference run clones them under its `reference/` subfolder; and B2 and B3 copy
members into a fresh run folder under the `--scratch` work root you name, which the tools refuse inside any git repository and where it is, holds or lies inside a member, a declared sibling's source folder or the framework root; run folders are kept. B1 makes each packet's root under
`B/<release>/packets/`, and every result file gets a `runs.jsonl` beside it. It writes to a member at B7 and
through that member's own session. Its tools also write at the output paths you pass (`--out`,
`--evidence`, `--receipt-dir`, `--json`): keep those paths outside the members' repositories (operator rule, not
enforced by the tool). `--scratch` is a work root, refused as above; removing old run folders in it is yours.

### Part A — per-release inputs (change these; the procedure does not)

| Input | Where it comes from |
|---|---|
| Release payload per template, at its tag | the core and template clones at the release tag; the prepare tools read them |
| Protected paths (`.claude/`, `AGENTS.md`, `CLAUDE.md`) | the kit's protected-path list; written only by the reviewed apply step |
| Correction rows (a file taken from core instead of the template) | not a per-release input in this kit, and no tool reads a corrections handoff: a fixed two-path list, `CORRECTION_ROW_4` in `wave_readiness.py` (`scripts/close_authorization_guard.py` and `tests/test_close_authorization_guard.py`), the same whatever the release. `prepare_launch.py` takes core as the release source for those two paths, and the ledger's payload expectations and `wave_readiness.py`'s coverage paths include them |
| Version carriers each receiver bumps | `.aget/version.json`, `manifest.yaml`, plus any carrier a receiver's own hooks demand |
| Instruments the release names but does not ship | a principal ruling, quoted in the batch record |
| Template per Aget | the ledger's resolver; a disagreement needs a ruling recorded in `records.json` |
| Receiver write-scope overrides | `records.json` `scope_overrides`, each naming its batches. `record_authority.py` writes one only with a typed line whose prompt names the Aget; `prepare_write_list.py` reads whatever entry is there and does not check the line |
| The Claude Code version | `claude --version` at preparation; launch refuses a mismatch within a batch; record each batch's value |
| The reviewed apply script's digest | `sha256 scripts/migration_kit/apply_protected.py`; a changed script is a new review, never an edit inside a batch |

### Part B — the fixed procedure

Each step names its tool, its pass condition and who acts. **Stop at the first failure** and record it, naming the
step. INCONCLUSIVE is never PASS. Judge each step from the verdict it prints for each member, not from its exit
code: a live launch at B8 exits 0 whatever its after-run checks said, and a receiver that `push_batch.py`'s gate
refuses prints NOT PUSHED without changing the exit code.

| # | Step | Tool / act | Passes when | Who |
|---|---|---|---|---|
| B0 | **Membership** | `fleet_ledger.py --online --json <ledger>`; take its unmet rows. *(No membership tool ships yet: check each by hand. The ledger prints no template for a member not yet migrated; resolve it with `python3 -c "import sys; sys.path.insert(0, 'scripts/migration_kit'); import fleet_ledger as L; print(L.resolve_template('<member folder>', '<member name>'))"` (pass the member's name as the register lists it: a template ruling in `records.json` is looked up by that name, as the prepare tools do). For a live session, list the processes whose working folder is the member's (`lsof -a -d cwd`, filtered on its path). A batch may take any subset of the unmet rows: say which and why in B13. `wave_readiness.py`'s own run needs four instruments the kit does not ship, and says so before writing anything.)* | Template resolves without a new ruling; the Aget's HEAD equals its remote with no held commits (else drop it with the reason, or include held commits only under a push line that names them); tree clean, or dirty only on paths the migration does not write; no live session in that tree | supervisor |
| B1 | **Prepare** (the B1 tools read each member; they write the `--out` files, `B/WRITE_LIST_scope.json` beside the write list, and the packet root: a new folder beside the `--out` packet under `B/<release>/packets/` (or under `$AGET_MIGRATION_PACKET_BASE`), which must lie outside every repository and every member. It holds the `stage` folder, sealed (not writable, every file's digest in the packet) before the packet file is written, and one baseline folder per member, open until that member's launch at B8) | `prepare_batch.py --batch N --out B/PROTECTED_LIST.json NAMES`, then `prepare_launch.py --batch N --protected-list B/PROTECTED_LIST.json --placed-by-apply --out B/LAUNCH_PACKET.json NAMES`, then `prepare_write_list.py --protected B/PROTECTED_LIST.json --packet B/LAUNCH_PACKET.json --out B/WRITE_LIST.json`, then `plan_protected.py --list B/WRITE_LIST.json` (the trial run: it calls the apply script's own planning and contains no write) | Lists and packet written; receiver bounds (`check_batch_scope.py`) exit 0 or a recorded override (else the list marks the Aget `blocked`); trial run clean. No B1 tool prints a git-ignored warning, so a quiet run says nothing about ignored paths. Check by hand: an op with `"tracked": false` in `B/PROTECTED_LIST.json`, or a receiver's non-empty `untracked_protected` in `B/LAUNCH_PACKET.json`, names a protected path git does not track; for each, `git -C <member> check-ignore -v <path>` prints the rule that ignores it, or nothing when the path is only new. A member whose protected files are ignored needs a skill-tracking pass as its own earlier batch, or its push cannot carry them (B10 prints NOT PUSHED for it). Run each receiver's own lint config over the release bytes, which are in the packet's `stage` folder (for example `ruff check --config <member>/ruff.toml <stage>`). A *blocking gate* is a check that a hook, a workflow or the member's suite runs, so that a finding would stop its commit, push or CI: raise such a finding for a ruling before B2. A check nothing runs is disclosed in the B4 request, not a stop. A member dropped later is re-listed with `prepare_write_list.py ... --drop AGET=REASON`. That marks it `blocked` in the write list only, as the bounds check does. B7 skips a `blocked` member, but `launch_batch.py` and `push_batch.py` read the packet and never the list. So after any drop or `blocked` mark, either rebuild the packet without the member (re-run this step with the remaining names; the later steps then read the new packet and list), or pass `--only` with the remaining members at B6, B8 and B10. Otherwise the member is still launched: as a migrating member it gets a baseline session and a migration session that is told its files were already placed and to set the version and commit. Operator rule, not enforced by the tool. Two fixed values to know: unless `--route "<label>"` is passed to `prepare_launch.py`, a fixed route text written for an earlier batch is what a migrating member is told to record in its version history and receipt, and a repair member in its receipt only (a track-skills prompt carries no route); and each migrating and repair member is told to run three fixed validation commands written for the 3.35.0 features (a track-skills member is allowed them but not told to run them). F-5 is fixed: the default member suite command is `python3 -m pytest -q -p no:cacheprovider`, which avoids creating `.pytest_cache/.gitignore` in a fresh checkout; the baseline and rehearsals also disable the cache provider, and an explicit `--suite-cmd` still overrides the default. K-1 remains a named cost: templates declare no write scope and need the principal's recorded scope override. Named limit F-6: to tell the member not to substitute a targeted test for its declared suite, pass `--extra-step "AGET=For pytest, run only the declared step-5 suite command; do not run targeted test commands."`; replace `AGET` with the register name. The extra step is an instruction only, not enforcement; the other required validation commands still apply. | supervisor |
| B2 | **Packet rehearsal** — on copies, no model | `rehearse_batch2.py --packet B/LAUNCH_PACKET.json --list B/WRITE_LIST.json --scratch <dir> --out B/V36_RESULT.json [--sibling-read AGET=REL ...]` | Every member PASS: no new test failure against its own baseline. The tool rehearses every member even when one is refused, and writes a verdict for each; a member that reads `REFUSED: <why>` fails the step until it is dropped or resolved as the B2 route below says, and B2 is then re-run (after B1 when the packet changes); for a migrating member each listed write equals the digest the list gives it (`post`); blind spots recorded. Declare at B1 every folder outside an Aget that its tests read (`prepare_launch.py --sibling-read AGET=REL`): a copy without it fails for the wrong reason. The tool refuses, before it makes anything, a `--scratch` work root that lies inside any git repository, that is, holds or lies inside a member, a declared sibling's source folder or the framework root, or for which git cannot say whether it lies in a repository; each run copies into a fresh run folder made in it, removes nothing, and names that run folder in its result. Before it copies a member, it refuses a copy folder that would be the member's own folder, hold it or lie inside it, and it refuses a copy (of the member or of a declared sibling) in which git would act on another working tree or git folder: nothing is then run in the copy. So is a copy in which any symbolic link, a hook link included, leads outside the run's folder (the copy, or the folder that holds it and its declared siblings); a hook linked into the member's own tree is admitted. A copy of the member that has no `.git` of its own (a member inside a shared repository) is refused the same way. So is a copy whose git configuration (the member's own, global or system) holds an `includeIf` with an `onbranch:` or `hasconfig:` condition, or an include of a file inside the repository: an operator whose global or system git configuration uses such an include is refused until it is moved out of that file for the run or given a `gitdir:` condition (the refusal names the file and the entry). No kit route rehearses such a member, so drop it (B0: a batch may take any subset of the unmet rows; `prepare_write_list.py ... --drop AGET=REASON`, then rebuild the packet at B1) and record why in B13; and remote definitions under `.git/remotes/` or `.git/branches/` are deleted. Not closed, here and at B3, B8a and the after-run confirmation run: a sibling folder with no `.git` at its top is copied with only the link test, and git run in its copy acts on any repository that encloses it; a symbolic link that code in the copy makes after the link test; a repository nested deeper inside a copied sibling; a submodule; a branch whose remote is a path with no remote section; a remote added during the run; a push to an explicit URL or path; the object store's `alternates` file; hooks; what code does after it starts. A hook the member installed as a symbolic link that the copy's link test refuses makes that member's copy refused. There are two routes, and the one taken is recorded in B13. Either drop the member as above. Or, if the principal wants it in this batch: changing the hook is an act on that receiver's own check inputs, so it needs a line (Line-need test). It is the principal's line, submitted in that receiver's own session (Receiver sittings; `open_receiver.py`). It is never a write by the supervisor or by a kit tool into the member's `.git/hooks`. After it, re-run B1 and B2 for the batch. Before it writes in its copy, the rehearsal refuses a path that is or goes through a symbolic link. A member's copy loses its remotes; a sibling's copy keeps them with a push URL that cannot resolve. Named limit F-3: the supervisor template's `test_template_size_buffer` calls `pytest.skip()` at run time when `AGENTS.md` is at least 25,000 characters, which reads INCONCLUSIVE here. Drop that member from the batch and record the runtime-skip reason; do not count it as PASS. | supervisor |
| B3 | **Session rehearsal** — headless, on a copy: a baseline session, then the migration session, as at the real launch (a track-skills receiver gets no baseline session). `rehearse_v37.py` makes the copy, tests that git run in the copy acts on the copy, removes the copy's remotes and writes a marker file into the copy's `.git` folder (`aget_rehearsal_copy.json`, naming the SHA-256 of the packet file's bytes and the member); it is not on the session's allow list and asks for no typed line. Before it makes anything it refuses a `--scratch` work root that lies inside any git repository, that is, holds or lies inside a member, a declared sibling's source folder or the framework root, or for which git cannot say whether it lies in a repository; it then makes a fresh run folder in it for this run's copies, and `<scratch>/evidence` for the evidence. Before it copies a member it refuses a copy folder that is the member's own folder, holds it or lies inside it (reason `copy not made`). Nothing is removed to make room, and run folders are kept (removing old ones is yours). The rehearsal's result does not name its run folder (the packet and repair rehearsals' results do). Each declared sibling's copy must pass the same git test and keeps its remotes with a push URL that cannot resolve. It calls `launch_batch.py --launch --copy-root <copy>`, and that form of the launcher makes no authority check. The launcher refuses the folder (exit 2, reason printed) unless it is apart from the member's own folder (not the same folder, not inside it, not containing it, and not sharing its `.git` through a link), git run in it names the folder as its working tree and the folder's own `.git` as its git folder and common folder, it holds in its `.git` folder the marker file that `rehearse_v37.py` writes into each copy it makes, naming this packet file's digest and this member, has no git remote, and is at the packet's HEAD for that member. The git test asks git itself, with the environment the session gets: a copy whose `core.worktree` setting names the member (git commands in such a copy change the member's files), a linked worktree, a `commondir` file and a bare repository are refused, and so is an environment that holds `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` or `GIT_NAMESPACE`; the object store's `alternates` file and hooks are not read. The rehearsal makes the same git test on the copy before it runs any other git command there, applies the list or launches, and ends with the reason `copy not usable` when it fails. So a member whose `.git` is a file or a link, or whose config sets `core.worktree`, is not rehearsed by this tool: its remotes are not removed and nothing is applied. The tool refuses a `--scratch` inside any git repository, as above, and a member copy with no `.git` of its own. A packet file edited after the copy was made is refused for that copy: run `rehearse_v37.py` again. The marker is a plain file: anyone able to write it can forge it in another checkout that is apart from the member's folder, has no remote and is at the packet's HEAD, and the session rule covers `launch_batch.py` with any arguments. So do not run `launch_batch.py --copy-root` outside this step: operator rule, enforced by the tool only as far as the tests above go. The session rehearsal (B3) reports a verdict only from its own run: the after-run record and the launch record that an earlier rehearsal left in its evidence folder are removed before the session launch, and a session launch that does not exit 0 gives no verdict (`session launch failed`), and the rehearsal's first act, before it reads the packet or makes a folder, is to write its result file as not finished; a run that stops after that leaves no earlier PASS for the approval step (B4). Each run's first act, before it parses its arguments, records the run in `runs.jsonl` beside the result file; a later step counts a result only when it is the last run recorded for that file and that run finished with those bytes. If the run cannot be recorded or the result file cannot be written, the tool stops there (exit 2) and a file from an earlier run may still count, so read the tool's exit before B4. A run that dies before its first act (the interpreter or an import fails), or that cannot append to its run log, leaves no run record, and the earlier result for that output stays current. The packet rehearsal (B2) and the repair rehearsal write their result files the same way. A batch made only of members that this tool cannot rehearse (a `.git` file or link, a `core.worktree` setting) has no B3 result and cannot be approved at B4 with the kit: stop and take it to the principal. The rehearsal costs model calls and several minutes a member | `rehearse_v37.py --batch N --scratch <dir> --packet B/LAUNCH_PACKET.json --list B/WRITE_LIST.json --out B/V37_RESULT.json <the member with the most hooks among those B2 rehearsed to PASS>` | The copy's after-run check PASS, including F (no new failure in the session's own suite run); the packet root left as it was (a rehearsal's baseline is written inside its copy, and the launch replaces the packet's baseline path in the prompt with the copy's). Hooks-path limit: a member with `core.hooksPath=/dev/null` is refused because it does not name a hooks folder inside the run that the kit can judge. If no hooks are wanted, run `git config --local --unset-all core.hooksPath` in the member before the batch and check its result, then confirm that `git config --get-all core.hooksPath` prints nothing and exits 1. The first command clears all local values; if the effective setting still appears, stop and record it rather than treating the workaround as complete. With no effective setting, Git uses its default hooks location, so check that no hooks are installed there. | supervisor |
| B4 | **List approval** | `check_list_approvable.py --list B/WRITE_LIST.json --v36 B/V36_RESULT.json --v37 B/V37_RESULT.json` exit 0 (both results name this list's digest; the packet rehearsal's result carries a blind-spot report for each member that is not blocked and not track-skills, and no blind-spot test is matched by name to a file the batch writes for that member, unless it is passed as `--accept-blind TEST_ID`; the match is by name only, so a test that exercises a written file without naming it is not caught). After a `--drop` re-list the results name the rehearsed list, not the new one: copy the rehearsed list aside before re-listing (the re-list overwrites it) and add `--relisted-from <the rehearsed copy>`, which passes only when the two lists differ in nothing but newly blocked members (and `prepared_at`). It refuses a re-list in which a member the B3 result names is newly blocked. Each result must also be the current run at its output path (its run id is the last run started in `runs.jsonl` there, and that run finished with these bytes): a result file copied from another folder, or one a later run of the same output superseded, is refused even when it names this list's digest. The B3 result's digest is its recorded `list_sha256` only. A rebuilt packet is a new list: run B2 and B3 again. Then the principal types the batch line | The typed prompt that holds the line names the batch in its first batch list; `record_authority.py --key N --line "<line>" --session <id> [--packet ...]` records it, and checks the line's provenance, prefix, length and batch, and, for a scope override, that the member is a receiver in `--packet` and is named in the typed prompt; it does not check the scope text or other recorded values against the line, which are the operator's. A receiver write-scope override rides on the same record as `--scope-override AGET=SCOPE`; the member's short name (without `private-`/`public-` and `-aget`) must be a whole word of the newest prompt that holds the line, outside any pasted block that sits among other words, and the recorded line itself need not name it. A line passed as the session's launch argument is not typed authority (`check_principal_line.py` exit 5): the principal types it again in the open session | principal |
| B5 | **Launch confirmation** | the same or another typed line; a line typed in another window is a relay: decline it (operator rule, not enforced by the tool: the check reads the transcript `--session` names and does not compare that id with the session running the batch) | `check_principal_line.py --session <id> --contains "<line>"` exit 0 (typed) or 4 (a human-origin entry queued mid-turn, whose prompt source the tool does not read; accepted, and disclosed); exit 5 means the line is only the session's first prompt, which a launch argument also produces, and is refused | principal |
| B6 | **Baselines** (migrants) | `launch_batch.py --packet B/LAUNCH_PACKET.json --launch --baseline --evidence B/evidence`; after any drop or `blocked` mark, add `--only NAME [NAME ...]` naming each remaining member, because the launcher reads the packet and never the list | RECORDED for each; HEAD unmoved since B1. Refused (exit 6) unless a recorded line for this batch is found typed (B5's exit 0) or queued mid-turn (its exit 4). A launch line need not name the launch. In addition to the provenance, prefix, length and batch checks, the recorded line must not match the tool's recognized launch-exclusion pattern. Recording a line as launch authority only when the principal meant the launch is an operator rule, not enforced by the tool. For the launch, the check binds the batch's name, not the packet: the launch tool passes it the packet's `batch` value and nothing else of the packet, so another packet file with the same `batch` value passes the launch check on the same recorded line, whatever receivers it lists. Launching with the packet that was rehearsed (B2, B3) and whose list was approved (B4) for that batch is an operator rule, not enforced by the tool. The push line is bound to its packet (B9) | supervisor |
| B7 | **Apply** | `apply_protected.py --list B/WRITE_LIST.json --apply --receipt-dir B` | APPLIED, every digest verified; protected mode-only payload changes use the write route and carry release_mode; The after-run A check compares a mode-bearing protected receipt with the working-tree executable bit and, where tracked, the regular-file mode in HEAD; ignored/untracked protected files need no HEAD entry. Ordinary D payloads still require the release mode in HEAD, and unavailable Git readings remain INCONCLUSIVE. an incorrectly-modeled noop refuses as RELEASE MODE MISMATCH; the script's digest equals the list's. Each member's result is APPLIED, REFUSED, ROLLBACK-INCOMPLETE, SKIPPED or NOT-STARTED; an IN-PROGRESS entry means the run was killed partway through that member. Every guarantee of this step, and of every other step that writes into a member, holds only while nothing else changes that member's folder tree and its listed files for the whole step: no other process, not only no second kit run, may write, rename or move anything in it. A folder moved after the kit's last check is not seen, and the write can land in the moved folder (release note, stated limits). REFUSED means nothing listed was left changed: a refusal before the first write writes nothing, and a failure after it is rolled back and read back. ROLLBACK-INCOMPLETE means the member may hold some release bytes: the receipt names each path restored and not restored; repair it by hand and re-prepare the list (a re-run refuses it as STALE). The other members are applied either way. A listed path that is or goes through a symbolic link, is not a regular file, has a second name, or resolves outside the member refuses that member at the plan; the member's HEAD is compared with the list's, and a list without HEADs is refused (prepare it again). A member the list marks `blocked` reads SKIPPED: nothing is applied to it, and it must be kept out of B8 with `--only` or a rebuilt packet. Named limit F-8: this updates `@aget-version` in `AGENTS.md`, not its `@aget-canonical-specs .../v<from>/specs` reference. After the batch, update that reference by hand to the target version in the member's own session, or record it as stale in B13; no kit check reports it. | supervisor, under the principal's typed batch line of B4 |
| B8 | **Sessions + after-run check** | `launch_batch.py --packet B/LAUNCH_PACKET.json --launch --apply-receipt <receipt> --evidence B/evidence`; after any drop or `blocked` mark, add `--only NAME [NAME ...]` naming each remaining member: without it the launcher starts a migration session in every member the packet names, including one B7 skipped | The `--settings` file equals the packet digest; after-run check PASS, including F, read from the line printed for each member; the after-run check reads the receiver's own terminal from its receipt at HEAD, in the packet's attempt section (check H), and G reads, for links and second names, every path the transcript shows written, every path git shows changed or untracked, every path already changed before the run and every `.claude/` file whose bytes changed (ignored or not), and checks the sealed stage and baseline; a write to another path git ignores, with no edit-tool call naming it, is not read. The prompt gives each release file the session places as a command of the packet's sealed placer (`python3 <packet root>/stage/kit/place_file.py ...`), not `cp -f` and `mkdir -p`. The command exits 0 whatever the after-run checks said (FAIL and INCONCLUSIVE included), so exit 0 is not a pass. No kit step runs `verify_extension_survival.py --verify` after a migration: the after-run check reads a member's own extensions back only for payload items (KEEP unchanged, every line of a MERGE surviving). F-5 is fixed: the default declared member suite is `python3 -m pytest -q -p no:cacheprovider`, so a fresh checkout's default run does not create `.pytest_cache/.gitignore`; an explicit `--suite-cmd` still overrides it. Named limit F-6: a session's targeted one-file test command instead of its declared step-5 suite still reads INCONCLUSIVE. Supply the B1 `--extra-step` instruction to run only the declared step-5 pytest command; it does not enforce the instruction or remove the other required validation commands. | supervisor |
| B8a | **Suite at the exact commit to be pushed** | `suite_at_commit.py --packet B/LAUNCH_PACKET.json --aget A --evidence B/evidence [--sha SHA] [--allow-path PATH]...` | PASS naming that commit, in a clean clone with each declared sibling folder copied from the live folder to the same relative path and, where the copy has a `.git` at its top, checked out at its `origin/HEAD` (else `origin/main`) as last fetched there, with no fetch; a sibling without `.git` at its top, or with neither ref, stays as copied, branch and uncommitted changes included, and the record's `sibling_refs` says which. FAIL: stop and record it, as for every step (operator rule, not enforced by the tool: at B10 `push_batch.py` prints NOT PUSHED for that member, unless the ruling below is accepted, and goes on to the other members). B8a wants no failure in the tests it runs, whether or not it was in a baseline; it applies the CI exclusions it reads from the member's workflows and suite command and lists them in the record's `excluded`. PASS also needs no change that the tool reads in the clone: it reads the clone's HEAD and `git status --porcelain` before the suite, after it and after the pre-push hook, and with each status line the content of the paths it names (a file's bytes and permission bits, a link's target, the files under a folder git lists as one entry), and a snapshot of every file, link and folder of the working tree that git does not ignore. A moved HEAD, or outside the paths named with `--allow-path` a new status line, a status line that is gone, or any other change to a file, link or folder of the working tree that git does not ignore, tracked or not (a file's bytes or permission bits, a link's target, a folder's permission bits; for example a file in a sibling folder copied inside the clone, listed before the suite and rewritten by it, or a tracked file whose read and write bits changed), or a status or a working tree that could not be read, reads INCONCLUSIVE (exit 3). The ignore rules in `.git/info/exclude` and the value of the `core.excludesFile` setting are part of what is compared, so a suite that adds an ignore rule there, or points the setting elsewhere, and then writes files the rule hides reads INCONCLUSIVE. Git's whole ignore state is compared too (`copy_isolation.ignore_state()`, as the release note's B8a item lists): among it the bytes of the file `core.excludesFile` names or, unset, of git's default ignore file (`~/.config/git/ignore`, or under `$XDG_CONFIG_HOME`), the bytes of every configuration file git reads, and the index's skip-worktree and assume-unchanged flags; a rule a suite adds to any of them, or a part of that state that cannot be read, reads INCONCLUSIVE. The pre-push hook run here is the file `hooks/pre-push` in the member's git common folder: a hook that a `core.hooksPath` setting names is not run at this step, and where no file is at that place the record says `hook.present: false` and PASS needs only the suite (where one is there and `core.hooksPath` names another, the file at the default place is the one run). The hook is placed in the clone as a regular file before it runs, chosen by where its entry resolves with every link followed: a file in the member's git folder gives its bytes, and a file in the member's working tree gives the bytes of the same path in the clone, at the tested commit. An entry that resolves outside the member, or to a path the clone does not hold as a regular file, is not run, and the record reads INCONCLUSIVE with `hook.present` true, `hook.run` false and the reason in `hook.why`; a hook still running after 2400 seconds has its process group killed and reads INCONCLUSIVE. The push at B10 is a plain `git push`, which runs the hook git finds. Each copied sibling folder that is a git repository goes through the same isolation as the clone before it is checked out, cleaned or used: git run in it must act on the copy, and each of its remotes gets a push URL that cannot resolve. A sibling whose copy fails that test reads INCONCLUSIVE with nothing run. For a change in the clone the record keeps the first 40 lines of each reading with its full count, up to 40 of the lines that blocked and up to 40 of the lines that were allowed (a HEAD moved by the suite is recorded as `head_after`, with no status lines). `--allow-path` is given once for each path: an exact repository-relative path, or a folder prefix ending in `/` (plain text, no glob); it is read from the command line only, so repeat it on each run. Untracked files under `__pycache__` or `.pytest_cache` folders are left out, and not read as a change are a file git ignores, a change made and undone between two readings, an empty folder added or removed, times and owners, any other change inside a `.git` folder, a ref moved while HEAD and the status lines stay as they were, a write by a process that outlives the suite or the hook outside its process group, a change inside a copied sibling beside the clone, a push to an explicit URL or path, and anything written outside the clone. On that INCONCLUSIVE, read the lines its reason names; where they are paths the member's suite or hook is known to write, name them with `--allow-path` and run B8a again; otherwise stop and record it. At B10 `push_batch.py` prints NOT PUSHED for a member whose record reads INCONCLUSIVE, and the ruling below does not apply to it: a run that fails tests and also changes the clone outside the allowed paths reads INCONCLUSIVE, not FAIL. B2 looks instead for failures new against a baseline taken on the copy, as do B3 and B8 for a migrating member (B3 against one taken on the copy, B8 against the one B6 records), and B6 can read RECORDED with failures in it. So a test that failed at B6 and still fails in this run keeps the member from PASS. The principal may rule that failure baseline-equal for that commit, in a typed line of one fixed form, typed as a whole prompt of its own: the prefix, then `the failures at SHA are baseline-equal`, SHA being 7 to 40 characters the commit's id starts with (for example `GO supervisor - the failures at abc1234 are baseline-equal`; a ruling worded any other way, such as "same failures as before", is refused); record it with `record_authority.py --session <id> --baseline-equal AGET=<commit> --ruling-line "<line>" --evidence B/evidence` (never by hand: operator rule, not enforced by the tool, as the push reads the ruling file as found and does not check what wrote it). The push then accepts the FAIL only when its failure set equals the B6 baseline exactly and the ruling's line is found typed or queued mid-turn (B5's exit 0 or 4), the newest prompt holding it equals it once runs of whitespace are collapsed (a pasted block among other words is left out of the comparison), and the line has that fixed form and names this commit (a test of form, not a reading of meaning; the push makes the same tests of the line as the recorder) | supervisor |
| B9 | **Push approval** | the principal's typed line, in one fixed form: the prefix, then `push the commits of batch N`, optionally more batches (`batches 10t and 10`) and, for every non-batch commit the push would carry, ` with commit SHA` (or `commits SHA, SHA and SHA`, each 7 to 40 hexadecimal characters), and nothing else. With the default prefix: `GO supervisor - push the commits of batch 1`, or `GO supervisor - push the commits of batch 12 with commit abc1234`. The push line is typed as a whole prompt of its own. Record it on its own, whole as typed, for the packet it authorizes: `record_authority.py --key N --act push --line "<line>" --session <id> --packet B/LAUNCH_PACKET.json`. The recorder refuses `--act push` without `--packet` and keeps the packet file's digest with the line; at B10 a push from any other packet file is refused, even one with the same batch number. A push reads only that entry (key `N:push`): the batch's launch line is never push authority, whatever it says, so a batch line that said "launch and push" does not authorize the push. The recorder refuses, and at B10 the push tool refuses again, unless the line starts with the prefix, has at least 30 characters, has that form (runs of whitespace are not compared, and after the prefix letter case is not compared either; the prefix itself keeps its letter case), is found typed or queued mid-turn (B5's exit 0 or 4) in a prompt whose first batch list names the batch, and equals that whole prompt once runs of whitespace are collapsed. The prompt compared is the newest one that holds the line, so a line typed alone and later quoted inside a longer prompt is refused. Every line in another form is refused, and the reason states the form. So "the push is not approved yet", "hold the push until I review", "the push remains unapproved", "the push is prohibited", "the push is held" and "push tomorrow" are refused. This is a test of form, not a reading of meaning: an affirmative line worded another way ("batch 1, push the verified commits", "no problem, push it") is refused too, and the principal types the form. A commit the line names must be passed at B10 as `--extra-commit`, which must match it (the shorter id a prefix of the longer), when HEAD moved since the launch check, HEAD is compared with the longer id; with HEAD unchanged, a supplied extra commit does not change the checked commit the gate permits; a push whose line names a commit is refused without `--extra-commit` (B10). A pasted block that sits among the principal's other words is left out of the whole-prompt comparison, and a later prompt that withdraws the push without repeating the line is not read. So read the typed prompts yourself, pasted text included, and if the principal withholds or conditions the push there, record nothing and ask again: operator rule, not enforced by the tool. The push line binds the packet it was recorded for, not only the batch's name (the launch line binds the batch's name only, B6) | only PASS receivers | principal |
| B10 | **Push** | `push_batch.py --packet B/LAUNCH_PACKET.json --evidence B/evidence --apply-receipt <receipt>` (dry run), then `--push` | Fast-forward; HEAD equals the checked head (or, when HEAD moved since the launch check and `--extra-commit` is supplied, is the commit that option names, by 8 or more characters of its id, whose only parent is the checked head and which touches at least one path, only paths among the `--extra-paths`, and no path among the packet's items for that member); every path the batch wrote is in the pushed commit; the after-run verdict is the current run of the check for that member's verdict file and names that member and the session its launch record names; the receipt at the commit to be pushed ends the packet's attempt section with exactly `Terminal: ACCEPTED` or `Terminal: BEHAVIOUR_VERIFIED`; `ls-remote` reads the pushed SHA. Refused (exit 6) unless a push line recorded for this batch with `--act push` (B9) exists, was recorded for this packet file (`--packet`), and passes B9's tests again: the batch's launch line is never read for a push, so a batch with no recorded push line is refused whatever its own line says (B9 says what those tests do not catch). A receiver the gate refuses prints NOT PUSHED without changing the command's exit code, which can still be 0, so read each member's line. After any drop, pass `--only NAME [NAME ...]` naming each remaining member. `--extra-paths` and `--allow-dirty PATH=REASON` come from the command line alone and are compared with no typed line: using them only on the principal's word is an operator rule, not enforced by the tool. `--extra-commit` must be a commit the recorded push line names (` with commit SHA`, the shorter id a prefix of the longer), when HEAD moved since the launch check, HEAD is compared with the longer id; with HEAD unchanged, a supplied extra commit does not change the checked commit the gate permits. The one accepted push form has a place for commit ids and none for a path, so that word is a separate line of the principal's, quoted in the batch's record | supervisor |
| B11 | **Ingest** | per pushed receiver, add to `records.json`: `receipts[<aget>]` (terminal, `receipt_revision` = pushed SHA, `attempt` = the packet's attempt for that receiver, `receipt_path` = the receipt's path in the member, and `source`; the ledger reads the terminal from the file at that revision and attempt, and the recorded value is only a cross-check) and each merge as a deviation, `deviations[<aget>][<path>] = {"blob": <the path's blob id at the pushed revision, from `git -C <member> rev-parse <pushed SHA>:<path>`>, "why": ...}` (the ledger reports a deviation without a blob as unbound). *(No ingest tool ships yet: additions only, by hand; keep the file's two-space indent so the change reads as additions.)* | additions only | supervisor |
| B12 | **Ledger** | `fleet_ledger.py --online --json <ledger>` | Each pushed receiver reads VERIFIED (CI passed on that SHA) or PUBLISHED-NO-CI (no root workflow), and only when its receipt at its receipt_revision, read in the section for the attempt records.json names, ends with exactly one line `Terminal: ACCEPTED` or `Terminal: BEHAVIOUR_VERIFIED`. Any of the following reads RECEIPT-NOT-SUCCESS, which is not a terminal state: REJECTED, CANNOT-RUN, any other value, a second terminal line, no section for that attempt, a later attempt section, a records entry without `attempt` or `receipt_path`, or a recorded terminal the file does not hold. A failed CI query reads INCONCLUSIVE, never a state. A receiver with a root workflow that no earlier condition has settled also reads INCONCLUSIVE, with a reason saying so, when its workflow checks could not be compared with its pre-migration revision (that revision was not found, or a workflow tree could not be read at the pre-migration or the published revision) and no `workflows-not-compared` check-change ruling is recorded for it. INCONCLUSIVE is not a terminal state, so that member counts as unmet. The row passes this test when a later ledger run makes the comparison, or when a `workflows-not-compared` ruling by the principal is recorded for the member: `record_authority.py --session <id> --check-line "<line>" --check-change AGET:NAME=CHANGE` (the line is found typed or queued mid-turn, starts with the principal line prefix and has at least 30 characters; the prompt that holds it names the member's short name and NAME as whole words; CHANGE is written as given, compared with no typed line). With that matching ruling recorded the row is classified from its CI result (VERIFIED on a pass; any other CI result leaves it unmet), and its `checks_compared` in the `--json` output still reads false. The ruling must have the shape `record_authority.py` writes and name `workflows-not-compared` for an unmade comparison or `workflows-changed` for a changed tree. A ruling naming another comparison passes nothing. The ledger checks that shape and name, but does not authenticate the principal's line. A tightening review does not stand in for a comparison that was not made | supervisor |
| B13 | **Record** | copy the batch's durable files from live `B` (lists, results and their `runs.jsonl`, evidence to keep, and the B13 record) into `migration/<slug>/batchN/` in your supervisor repository, and commit that archive with the plan's batch entry. Never copy or commit the packet root, stage or confirmation clones. Continue using live `B` for kit steps; the copies are an archive | Members and drops with reasons; list digest; every clock read; the principal's time per act from transcript timestamps, never estimated (from the end of the turn that asked to the typed line's time, which `check_principal_line.py` prints); every refusal of an authorized step with its reason verbatim; each command the principal was asked to run by hand; every document consulted to run the batch | supervisor |

**Line-need test.** Before offering the principal any line, check that the act needs one: a push; a public,
cross-Aget or irreversible act; a check loosened; a change to the principal's configuration; or a choice that is
genuinely the principal's. Anything else is done, then reported. An act request ends at the principal's last
keystroke, and its completion is detected, not asked for.

**Requests to the principal.** Every request for a principal act ends the supervisor's turn. The line to type stands
alone on the last line, in a code span, and the sentence above it names the window it is typed in; a request buried in
prose is missed. Keep a line under about 150 characters so it does not wrap: detail belongs in the batch record the
line names. When you defer a choice to the principal, state your recommendation and why; a deferral without one leaves
the principal to decide with less than you know.

**Refusal of an authorized step.** A harness or classifier refusal of a step the principal authorized is a blocker,
reported with the step, the refusal's reason verbatim and the authorizing line. It is never retried in another form or
routed around. The principal decides the route. Asking the principal to run a command by hand is the last option, and
each such ask is counted in B13.

**Receiver sittings.** An act only a receiver can do (push its own commits, amend its receipt, change its own check
inputs) is the principal's line submitted in **that receiver's own session**. `open_receiver.py` opens a receiver's
window only on a typed `OPEN <key>` at a real terminal, or a pre-authorization file naming the window and the batch (the file's
origin is not checked and no session record is read). Give
each Aget of a shared repository root its own window (relative hook paths break in another Aget's folder). Give the
principal the short form, run from the supervisor root with relative paths:
`python3 scripts/migration_kit/open_receiver.py --receivers B/RECEIVERS.json <key>` (a command long enough to wrap breaks when
copied). A folder Claude Code has not opened before first shows its folder-trust prompt with "No, exit" selected: say
so in the request, because Enter alone closes the window. After handing an act to a receiver window, arm
`watch_receiver.py <receiver folder>` before you end your turn: it is read-only and exits on the receiver's turn end,
HEAD move or a move of `refs/heads/main` on its `origin` remote (pass `--ref refs/heads/<branch>` for a receiver on
another branch). It also exits with no event at its `--timeout` (3600 seconds by default, exit 3) or when a git probe
fails (exit 2). Each turn-end event names its session, and `--session <id>` narrows the turn-end watch to the transcripts
whose names start with that id: use it whenever the receiver's folder may hold another live session. HEAD and the remote
belong to the checkout, not to a session, so their moves end the watch whichever session caused them.
**Never end a turn on a receiver act without it armed**: a receiver that stops on a question to the
principal changes nothing on disk, so a watch on HEAD alone waits forever. Ask the receiver to end with one plain
table of choices, each row a typed line `GO <aget> - <phrase>`; never a question widget for an act (a checkbox answer
is not a typed line).

**Network and cost.** The headless sessions of B3, B6 and B8, the push session of B10, B8a's suite run and B2's
reference run start with every variable whose name ends in `API_KEY` removed. Two runs do not: B2's suite runs on the
copy (`rehearse_batch2.py`, before and after the apply), and the after-run check's re-run of new failures at B3 and
B8. Both inherit the batch session's environment, API keys included, so start the batch session from a shell where
those variables are unset (a prefix on a ruled command stops the session rule from matching). A member whose suite
makes live calls gets a suite command at B1 that excludes them, disclosed in the B4 request.
Before the after-run check's re-run starts any test, it gives every remote of its clone, and of each copied sibling
folder that is a git repository, a push URL that cannot resolve, so a push to one of those remotes by name from the
clone or from such a copy fails while that setting stands (a push from any other folder is not covered).
When that cannot be done, or a declared sibling's `.git` is a file or a link, the new failures are not re-run and
stay failures (the member's after-run check reads FAIL). A push to an explicit URL or path, and the environment the
re-run inherits, are as before.

**Boundaries the supervisor keeps at every step (operator rules; the tools enforce only the checks stated above)**: no receiver write except by B7's reviewed script or the receiver's own
session; no push without B9; no history rewrite; no Claude Code restart or update inside a batch; workflows and
subagents never approve, apply, launch, push or commit.

**Rehearsing the kit itself** is the release producer's obligation, not a batch step: before release, a supervisor
session working from the kit alone migrates a throwaway copy of a supervisor and a small throwaway fleet, with the
producer at most controlling or evaluating. A run driven by the kit's producer is a tool test, not that rehearsal.
B2 and B3 above rehearse one batch's packet; they do not rehearse the kit.

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
python3 -c "import json; from pathlib import Path; print(json.loads(Path('~/github/aget-framework/aget/.aget/version.json').expanduser().read_text())['aget_version'])"
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

The version reading X.Y.Z confirms the *label* is set — NOT that the deployment contract is published or your source contains the release payload. A version bump does **not** copy new artifacts. Verify substance before migrating (prior fleet upgrade case lessons):

```bash
FW=/path/to/your/aget-framework
# (a) Deployment contract published (read it — detection clauses + breaking_release):
test -f $FW/aget/DEPLOYMENT_SPEC_vX.Y.Z.yaml && echo "PASS: spec" || echo "FAIL: no DEPLOYMENT_SPEC_vX.Y.Z — STOP, do NOT relabel 'no spec' as version.json"
# (b) Your template source actually CONTAINS the release's new artifacts (list them per release notes):
#     for each new artifact: test -f $FW/template-{archetype}-aget/<path> || echo "FAIL: empty source pulls nothing — STOP"
```
**Expected**: PASS on both. **If FAIL**: STOP — migrating from an empty source, or relabeling a missing contract as a "deviation," are real observed failures (prior fleet upgrade case). Pull/escalate first.

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

#### Gate 5.5: Release Outcome Close-Out (BLOCKING, v1.10.0)

Required before the plan's terminal status, for every fleet migration (canon R-REL-024-03). In the v3.35.0 wave the
plan closed without any of it, because its checklist came from a template with no close-out rows and the close read
only the plan; it was the fourth recurrence.

1. **At plan creation**, copy the rows below into the plan's Closure Checklist. A close check that reads only the
   plan cannot fail on a row the plan never had.
2. **Release Outcome Report**: score the migration against `rubrics/RUBRIC_fleet_upgrade_outcome_v1.3.md` (minimum
   10/15; below 10, document the gap; below 6, rework). Name the score's subject: the exact close it scores. Write
   it before the close and **re-derive it at the closing commit**: status, gate verdicts and publication claims
   written earlier go stale the moment the close and its push land.
3. **Two distinct issues**: an outcome issue (coverage N/N, gates, pushes, residuals, the score) and an experience
   issue (transferable lessons). Filing one does not satisfy the other.
4. **Eligibility receipt** before the status change: the plan, rubric, close guard and authorization bound by digest
   at a nonterminal commit (rubric §C-C). Without it the close cannot be accepted.
5. Record the score and rubric in the release handoff's Completion Response.

**After a batch that leaves members unmet.** This gate is judged for the whole migration: N/N, the three-Aget sample
and the fleet version cannot pass while members remain. Record each row as met, not met or not exercised, with the
reason, and leave the plan open; the rubric has no level for partial coverage, so a partial score is provisional. No
instrument writes the eligibility receipt of step 4 yet: write it as a section of the outcome report. For the
stale-reference row, the scope is the member's live files (its instruction file, manifest and version carriers), not
its history, sessions or changelog.

**V-Tests**:
- [ ] All active Agets at the target version (N/N), from the ledger
- [ ] Fleet register updated (per-Aget carriers and the fleet version)
- [ ] Behavioural sample: 3+ Agets answer with the target version
- [ ] No stale version references, measured with both the prior and the target version (an empty scope is NOT MEASURED, never PASS)
- [ ] Release Outcome Report filed, its subject named, re-derived at the closing commit
- [ ] Outcome issue and experience issue filed, both numbers named in the plan
- [ ] Eligibility receipt present before the terminal status

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
- prior internal authoring plan (graduation source)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.10.8 | 2026-10-06 | Records the second outcome test (FAIL on P3/P6, R59 accepted limits); the post-10-02 null-receipt and parallel-environment fixes; packet-relative external run roots; the hooks workaround; V0.2 expands the home path; Round 2 release executable-bit placement and exact extra-step rendering/refusal. Round 2 code changes have unit-test coverage and have not had another outcome run. |
| 1.10.7 | 2026-10-02 | **Steps brought in line with the kit's design pass** (four rules applied at every site of their class: containment, result binding, instruction fidelity, all-or-nothing apply; unit-tested at preparation; the 2026-10-06 second outcome run later exercised the worker path and returned FAIL, accepted as R59 named limits): B1 names the packet root outside every repository, its sealed stage and the per-member baseline folders; B2 says every member is rehearsed even when one is refused, and routes a refused member to a drop or to the principal's line in that receiver's own session, never a hook installed by the kit; B3 names a member B2 rehearsed to PASS, the run record each result now carries, and the rehearsal's baseline inside its copy; B4 adds the current-run test and refuses a re-list that blocks a B3 member; B7 lists the result values, the rollback and the HEAD comparison; B8 names after-run checks H and G, and what G reads; B7 states the exclusive-mutation condition for every step that writes into a member; B2 refuses a copy in which a symbolic link leads outside the run's folder and admits a hook linked into the member's own tree; B10 the verdict binding and the receipt terminal; B11 `attempt` and `receipt_path`; B12 RECEIPT-NOT-SUCCESS. Also recorded under 1.10.7: the release note keeps the kit's stated limits in one section ("What the kit guarantees, and its stated limits"), which B7 cites and which ends with what reads INCONCLUSIVE because the kit cannot prove it; B8 says a member's session places its release files with the packet's sealed placer, never with `cp -f`; B2 refuses a copy whose git configuration holds an `onbranch:` or `hasconfig:` include, or an include of a file inside the repository; B2 and B3 say `--scratch` is a work root that the tools refuse inside any git repository and where it is, holds or lies inside a member, a declared sibling's source folder or the framework root, in which each run makes a fresh run folder and removes nothing; B6 says only the launch check binds the batch's name alone, and B9 and B10 that a push line is recorded with `--packet` for one packet file and that a commit it names must be passed as `--extra-commit`; B8a says the pre-push hook is placed in the clone as a regular file, that one resolving outside the member reads INCONCLUSIVE, and that the `core.excludesFile` file and git's default ignore file are compared. |
| 1.10.6 | 2026-10-02 | **Steps brought in line with eight tool fixes** (made after the independent reviews of the v3.36.0 candidate; the fixes were unit-tested at preparation; the later second outcome run exercised the worker path, returning FAIL accepted as R59 named limits): the setup table and B3 say what a `--copy-root` launch now refuses (a folder not apart from the member's own, in which git would act on another working tree or git folder, without the marker file `rehearse_v37.py` writes for the packet and member, with a git remote, or not at the packet's HEAD), what the rehearsal refuses before it removes, copies, applies or launches, that the marker can be forged, and that a packet edited after the copy needs the rehearsal run again; B8a shows `--allow-path` and says that a moved HEAD, or outside the allowed paths a new status line, a status line that is gone, or any other change to a path of the working tree that git does not ignore (untracked files under `__pycache__` or `.pytest_cache` folders are left out), reads INCONCLUSIVE, what is not read as a change, and what the operator then does; B8a, B9 and B10 state the tests the tools now make on a baseline-equal ruling line and on a push line (a push reads only a line recorded with `--act push`, never the batch's launch line; the line must equal the whole typed prompt it is found in, with whitespace runs collapsed and a pasted block among other words left out of the comparison, and must have one fixed form, as must the ruling line); B12 says a member with a root workflow whose workflow checks could not be compared with its pre-migration revision reads INCONCLUSIVE, where no earlier test has settled its row, unless a check-change ruling is recorded for it with `record_authority.py`; Network and cost says the after-run check's re-run gives every remote of its clone and of each copied sibling repository a push URL that cannot resolve before any test runs; B2, B3 and B8a say that every copy and clone the kit makes passes one isolation routine before anything runs in it, that B8a's copied siblings cannot push to a named remote and that a changed ignore rule reads INCONCLUSIVE; B3 says its verdict comes from its own run only; B10 says where the principal's word for the three extra push options is recorded; B12 says which shape of check-change ruling counts. Added the same day, after the third independent review: B2 and B3 refuse a member copy with no `.git` of its own, delete remote definitions under `.git/remotes/` and `.git/branches/`, and state what isolation does not close; `--scratch` stays outside any repository that holds a member; a protected file is replaced only when it is byte for byte an upstream version; B7 refuses a listed path through a symbolic link and compares bytes, not HEAD (M1's rule is an operator rule there); B8a states which pre-push hook it runs and which ignore files it does not compare. |
| 1.10.5 | 2026-10-01 | **Statements corrected to what the tools do** (independent review of the v3.36.0 candidate; no tool changed): the setup table and B3 no longer say each ruled tool checks the typed line (a launch with `--copy-root` checks none); B1, B6, B7, B8 and B10 say a dropped or blocked member stays in the packet and is launched unless the packet is rebuilt or `--only` names the remaining members; B6 says a launch line need not name the launch; B9 states what the push-exclusion check catches and the operator rule for a push line; B10 says the three extra options are compared with no typed line; Part B, B8 and B10 say exit code 0 is not a pass; B1 discloses the fixed route text and validation commands. A second pass of the same review corrected further statements, again with no tool's behaviour changed: the setup table says which tools read the register at `register_pin`; the paragraph after it says that the launch, push and B8a tools remove the variables whose names end in `API_KEY`; the paragraph on what the kit touches names B2's reference clones; Part A says the correction rows are a fixed list in the kit; B1 says what the prepare tools write; B2 names the digest its writes are compared with; B4 says what `--relisted-from` does not refuse and where a scope override's member must be named; B5 says a relayed line is declined by the operator, not the tool, and what exit 4 is; B8a says what its clone, its failure test and a FAIL do; Part B and B10 say a receiver the push gate refuses leaves the exit code unchanged; the receiver-sittings paragraph says which ref `watch_receiver.py` watches and when it exits with no event. The 1.10.0 row's "network-bounded suite runs" does not mean runs cut off from the network; Network and cost states which runs start without the variables whose names end in `API_KEY` and which two keep them. |
| 1.10.4 | 2026-10-01 | **Wording only**: the kit section's opening no longer states the size or batch count of the fleet the procedure was developed on. No step changed. |
| 1.10.3 | 2026-10-01 | **Setup for a supervisor built from the template alone** (a scratch investigation built one and ran the prepare steps): the kit's own requirements file and the row that installs it; the fleet register named as something the supervisor must have committed first. `verify_extension_survival.py` now looks for the register at the repository root. |
| 1.10.2 | 2026-10-01 | **Kit Batch Procedure corrected from its second rehearsal** (one member migrated from this section alone; its list named where the section did not suffice): which release the kit is copied from; the two fleet keys of the release target; committing the records file and batch folders; the migration's record, created before B0; what the kit touches outside the repository; the prefix rule stated positively for the three ruled tools; by-hand methods for B0 (template, live session, choosing members) and B1 (ignored paths, receiver lint and what a blocking gate is); the sibling-read flag; what B3 costs; who runs B7; B8a's stricter condition and the baseline-equal ruling, now recorded by `record_authority.py --baseline-equal` and checked as typed; the deviation record's shape; how the principal's time is read; the close-out gate after a partial batch. |
| 1.10.1 | 2026-10-01 | **Kit Batch Procedure corrected from its first rehearsal** (a supervisor session migrating a throwaway fleet from this section alone): the framework clones and `framework_root` in the target file; confirming a session's launch settings; creating the records file; `plan_protected.py` as B1's read-only trial run; B3 runs two sessions for a migration receiver; the scope-override syntax; a launch argument is not a typed line; the push needs a line that names it (`--act push`); how the supervisor presents its own requests; `watch_receiver.py` (events name their session; `--session` watches one) and the rule never to end a turn on a receiver act without it armed; the kit is shown to work with Claude Code only; the short receiver-window command and the folder-trust prompt. |
| 1.10.0 | 2026-09-30 | **Kit Batch Procedure + close-out gate** — carries one supervisor's v3.35.0 batch procedure (B0–B13) into canon as the instructions for the release's migration kit (`scripts/migration_kit/`), release-neutral: per-release inputs separated from the fixed steps; typed-authority gates on launch and push; one-session permission rules (`batch_rules.json`); receiver sittings in the receiver's own window; network-bounded suite runs. Steps whose tool the kit does not ship yet (membership, ingest) are written as manual criteria, never as a named instrument. **Gate 5.5** adds the release-outcome close-out: report re-derived at the closing commit with its subject named, two distinct issues, an eligibility receipt before the terminal status, and the rows copied into the plan at creation (the v3.35 close skipped all of them). |
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
- **Sources**: VERSION_SCOPE_v3.16.0 row #2 SD-3, plan G1.1 deliverable (prior internal authoring plan v1.0.11)

### v1.5.0 (2026-04-26)

- **Added**: Execution Model section — centralized by default (principal decision 2026-04-26); distributed requires explicit principal approval
- **Added**: Mandatory vs Optional Change Classification section — Mandatory (BLOCKING V-tests), Optional (WARN, not FAIL); references DEPLOYMENT_SPEC_vX.Y.Z.yaml
- **Added**: Prerequisites item 5 — gh auth smoke-test; addresses cloud-hosted keyring failure risk (prior fleet upgrade case finding)
- **Added**: Gate 5.4: FLEET_REGISTRY Update as BLOCKING completion criterion (prior fleet upgrade case D1 gap)
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
- Validated by: prior fleet upgrade case supervisor D62 self-remediation (2026-03-14)

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

- Initial SOP graduated from prior internal authoring plan
- Based on patterns from v2.12.0 LTS, v3.0.0, v3.2.1 migrations
- L455 V-MIG-AGENTS tests integrated
- Troubleshooting section from v3.2.1 learnings

---

## Graduation History

```yaml
graduation:
  source: "prior internal authoring plan"
  pattern_executions:
    - v2.12.0_LTS_Convergence (2025-12-26)
    - v3.0.0_Migration (2025-12-27)
    - v3.2.1_Fleet_Migration (2026-01-05)
  trigger: "L436 - Pattern executed successfully 3 times"
  rationale: "Repeatable fleet migration procedure warranted formalization"
```

---

*SOP_fleet_migration.md — Fleet version migration procedure for AGET framework*
