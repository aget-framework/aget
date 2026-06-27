# AGET Host-Runtime Filesystem Layout Specification

**Spec ID**: AGET_HOST_RUNTIME_SPEC
**Status**: **Active** (v1.0.0, canonical — graduated 2026-06-27 in v3.24.0 via `/aget-enhance-spec`, #1737). The **standard** is producer-complete and governing; behavioral conformance V-tests (V-HFL-001..007) are **runtime-pending** — they activate at first node deployment (operator lane), per ADR-007 honest-testability (no test theater). v1.0.0 labels the *standard*, not deployment-proof; adoption is tracked separately (INIT-ALWAYS-ON-HOST). The runnable-now gate — the CAP↔V bijection (7↔7) — PASSES.
**Owner**: INIT-FRAMEWORK-COHERENCE Stream 7 (producer lane); deployed/operated by INIT-ALWAYS-ON-HOST Stream 1/3 (operator lane). Producer/Operator lane-split C1051.
**Governing decisions** (principal, 2026-06-22, requirements-level): **tiered** telemetry · **fleet-wide** standard · **decoupled-required** ownership.
**Theoretical basis**: lifecycle-class separation convergent across XDG Base Directory, systemd (`StateDirectory`/`LogsDirectory`/`RuntimeDirectory`/`CacheDirectory`/`ConfigurationDirectory`), macOS launchd / `~/Library`, and structured-logging bounded-growth practice (web study 2026-06-22).
**Ontology**: FWRK-2026-054 (C1045–C1054).

---

## 1. Scope

**Defines**: where an always-on AGET host's *runtime* artifacts live on disk — the per-node filesystem layout for daemon config, data, state, cache, logs, runtime, and telemetry — so location is derivable from rules (the spatial twin of naming predictability, C1050).

**Does NOT define**: repo-internal layout (`AGET_TEMPLATE_SPEC` CAP-TPL-001/002/010 governs that); repo deployment (`DEPLOYMENT_SPEC`); host *operations* (migration, scheduling — INIT-ALWAYS-ON-HOST operator lane); agent identity/roster (supervisor lane); host **enforcement** of AGET's mechanical governance (write-scope/budget/egress) — that is the **second Stream 7 dimension**, `AGET_HOST_ENFORCEMENT_CONTRACT_SPEC` (DRAFT, sibling). Fills the gap `AGET_UNATTENDED_AUTONOMY_SPEC:30` explicitly carves out ("does NOT define the host runtime itself").

**Applies to**: every always-on node (node-1 is the first instance and the conformance reference; the standard is fleet-wide per principal ruling — node-2..N inherit it).

## 2. Lifecycle classes (CAP-HFL-001)

Each runtime artifact belongs to exactly one lifecycle class; its location is determined by that class. AGET-native expression:

| Class | Lifecycle | AGET-native location | Persistence |
|-------|-----------|----------------------|-------------|
| config | durable, authored | repo `data/<node>/config/` (record) | persists, versioned |
| data — record | durable, app-maintained, low-volume | repo `data/<node>/...` (git-tracked) | persists, versioned |
| state/telemetry — exhaust | high-volume, raw | host tree `~/aof/state/` (gitignored) | persists on host, rotated, NOT versioned |
| cache | regenerable | host tree `~/aof/cache/` | disposable |
| logs | append-only | host `~/Library/Logs/aof-*.log` (macOS) | rotated, size+time capped |
| runtime | ephemeral (sockets/pids) | host `$TMPDIR`/`~/aof/run/` (0700) | removed on stop |

## 3. Requirements (EARS)

| ID | Pattern | Requirement | Concept |
|----|---------|-------------|---------|
| CAP-HFL-001 | ubiquitous | The SYSTEM shall place each runtime artifact under a directory determined by its lifecycle class. | C1046 |
| CAP-HFL-002 | ubiquitous | The SYSTEM shall maintain a layout manifest mapping each path (or pattern) to its owning writer and lifecycle class. | C1048 |
| CAP-HFL-003 | event-driven | WHEN a structured/append-only output exceeds its configured size or age cap, the SYSTEM shall rotate it and retain at most N rotated files. | C1047 |
| CAP-HFL-004 | unwanted | IF a runtime artifact appears outside its declared lifecycle-class path, THEN the SYSTEM shall report it as layout drift. | C1048, C1050 |
| CAP-HFL-005 | ubiquitous | The SYSTEM shall classify each runtime output as *record* (durable → git-tracked under `data/`) or *exhaust* (high-volume/ephemeral → host-anchored, gitignored, rotated), per §4 boundary; classification is per-output by default and MAY be **per-row** (manifest-declared record-predicate) where a stream mixes tiers. | C1045, C1053 |
| CAP-HFL-006 | unwanted | IF a region has no governing layout rule, THEN the SYSTEM shall NOT grade its disorder as a violation (absence ≠ drift). | C1052 |
| CAP-HFL-007 | unwanted | IF a daemon executes directly from an agent's repo checkout (run-from-repo), THEN the SYSTEM shall report it non-conformant; node daemons SHALL run from deployed copies owned by the operator agent. | C1051, C1054 |

## 4. Record / exhaust tier boundary (CAP-HFL-005 detail)

Principal ruling: telemetry is **tiered**. The boundary:

- **Record tier** (versioned, repo `data/`): low-volume, durable, semantically meaningful state and **summarized** telemetry — capability manifests (`data/aof/capability/*.manifest.json`, already conformant), attestations, rollups/digests, config.
- **Exhaust tier** (host-anchored, gitignored, rotated): high-volume raw append-only streams — heartbeat JSONL, git-sync JSONL, resident-audit JSONL, orphan-report JSONL. Never committed; rotated under CAP-HFL-003.

Default classification rule: an output is **exhaust** if it is append-per-tick and unbounded; **record** if bounded and human/audit-meaningful. The manifest (CAP-HFL-002) records each output's tier explicitly (per-output override of the default).

**Reference classification** (illustrative, from a first-node always-on deployment) — example outputs and their tiers:

| Output | Tier |
|--------|------|
| `data/aof/capability/*.manifest.json`, `aof_daily_digest/*.md` | record |
| `aof_heartbeat.jsonl`, `aof_git_sync.jsonl`, `aof_orphan_report.jsonl`, `aof_node_monitor.log/.err`, `aof_channel/topics/*.jsonl` | exhaust |
| `aof_dispatch/done/*` | record-leaning (completed dispatch+response = work record) |
| **`aof_resident_audit.jsonl`** | **boundary case** — compliance audit trail dominated by `idle-beat` "no action" rows |

**Granularity decision (the boundary case forces it):** classification is **per-output by default, but MAY be per-row** where one stream mixes tiers. The audit trail is the forcing example — proposed row-predicate: *an audit row is **record** iff `envelope_disposition != "n/a (no action)"`; idle-beats are **exhaust***. CAP-HFL-005 therefore admits a per-row record-predicate (declared in the manifest), not only per-file tiering. (Spec-design item resolved by operator data, not assumed.)

## 5. Deployed-copy decoupling (CAP-HFL-007 detail)

Principal ruling: node operation is **decoupled** from any single agent's existence. Node daemons run from **deployed copies** (e.g. `~/.local/bin/aof_*` or operator-owned deploy path), never from an agent's git checkout. Consequence: retiring an agent cannot break the node. Migration of any existing run-from-repo daemon to a deployed copy is a prerequisite for that agent's retirement (operator/supervisor lane executes; this spec only defines conformance).

**Reference example** (a first-node deployment): of seven node daemons, two ran from an operator agent's repo checkout (non-conformant — migration owed) and five already ran from a deployed path (`~/.local/bin/`, conformant). The conformance check is per-daemon; the standard defines the rule, not any one node's roster.

**Scope clarity:** CAP-HFL-007 is *correctly daemon-scoped*. A full agent-retirement migration is **broader** than this conformance check — it must also clear non-daemon couplings (on-demand tooling and rules-of-record artifacts). Those are out of CAP-HFL-007's scope by design (not daemons) but belong to the retirement manifest's scope. The standard must not be read as "the daemon set = the whole migration."

## 6. Layout manifest schema (CAP-HFL-002)

```yaml
# layout_manifest.yaml — path → owner → class → tier
paths:
  - pattern: "~/aof/state/heartbeat.jsonl"
    owner: aof-selfreport
    class: state
    tier: exhaust
    rotate: { max_size_mb: 50, max_age_days: 14, keep: 3 }
  - pattern: "data/aof/capability/*.manifest.json"
    owner: <operator-agent>
    class: data
    tier: record
```
The manifest is the conformance instrument — checkable by the node monitor so any path outside its declared class/tier registers as drift (CAP-HFL-004).

## 7. Verification (V-tests — runtime-pending; honest-testability ADR-007)

All behavioral V-tests are **runtime-pending** until the layout is deployed on a node; the runnable-now check is the CAP↔V coverage bijection (meta-test).

| V-test | Targets | Falsifier | State |
|--------|---------|-----------|-------|
| V-HFL-001 | CAP-HFL-001 | A runtime artifact whose location is not class-derivable | runtime-pending |
| V-HFL-002 | CAP-HFL-002 | A live path absent from the manifest | runtime-pending |
| V-HFL-003 | CAP-HFL-003 | An un-capped/un-rotated append-only output | runtime-pending |
| V-HFL-004 | CAP-HFL-004 | A misplaced artifact not flagged as drift | runtime-pending |
| V-HFL-005 | CAP-HFL-005 | A high-volume raw stream committed to git (exhaust mis-tiered as record) | runtime-pending |
| V-HFL-006 | CAP-HFL-006 | An ungoverned region's disorder graded as a violation (phantom rule) | runtime-pending |
| V-HFL-007 | CAP-HFL-007 | A node daemon running from an agent's repo checkout | runtime-pending |

## 8. Ontology bindings

`HostRuntimeFilesystemLayout` (C1045) · `LifecycleClassSeparation` (C1046) · `BoundedGrowthPolicy` (C1047) · `LayoutManifest` (C1048) · `CoherenceAsPredictability` (C1049) · `LayoutPredictabilityInvariant` (C1050) · `ProducerOperatorLaneSplit` (C1051) · `StandardAbsenceVsViolation` (C1052) · `RecordExhaustTierBoundary` (C1053) · `DeployedCopyDecoupling` (C1054). (DRAFT FWRK-2026-054, gated.)

## 9. Graduation path

1. `/aget-enhance-spec` lifecycle (Phases 0–6) → wire V-tests, ratify, promote to canonical `../aget/specs/AGET_HOST_RUNTIME_SPEC.md`.
2. Weekend release window to publish.
3. INIT-ALWAYS-ON-HOST consumes: deploys layout on node-1 (operator lane), runs conformance check via node monitor.

**Open items**: ~~confirm record/exhaust tiering (RELAY Q1)~~ **ANSWERED** 2026-06-22 (§4, verified at source); ~~confirm migration set (RELAY Q2)~~ **ANSWERED** 2026-06-22 (§5, 2 daemons + non-daemon caveat). Remaining: per-row vs per-file boundary granularity is now *admitted* (CAP-HFL-005) — finalize the manifest record-predicate schema at graduation; CAP↔V bijection meta-test (7↔7, PASS) = the runnable-now gate; graduation via `/aget-enhance-spec` + weekend release window is the only blocker to canonical.
