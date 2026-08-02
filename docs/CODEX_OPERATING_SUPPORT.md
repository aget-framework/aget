# Codex Operating Support — Private Framework Manager

**Status**: Local pilot guidance; not yet public payload or fleet convention
**Owner**: INIT-CROSS-CLI-PORTABILITY Streams 1–4
**Evidence**: `PROJECT_PLAN_codex_portability_pilot_v1.0.md` Gates 1C–1D

## Daily operating sequence

1. Run canonical wake-up and record Codex CLI/model plus an AGET episode identifier.
2. Resolve the governing `AGENTS.md`. When a repository AGET skill is not natively discoverable,
   label `explicit-source-fallback` and name the `SKILL.md`; preserve every gate in that source.
3. Capture principal authorization with its bounded scope. Never translate the scope into a blanket
   permission or a broader action batch.
4. Keep logical AGET episode identity separate from the Codex harness session identifier. If the harness
   identifier is unavailable, record PARTIAL/UNSCORABLE plus the limitation.
5. Before an exact-scope commit in a concurrently used repository, prefer a reviewed, digest-bound
   transaction request. The request has this closed schema (unknown keys fail):

   ```json
   {
     "schema": "aget.codex-git-transaction.v1",
     "repo": ".",
     "expected_head": "<observed-head>",
     "message": "<message>",
     "paths": ["<exact-path>"]
   }
   ```

   Compute its SHA-256, inspect it without mutation, then submit the same path and digest for the
   consequential operation:

   ```sh
   shasum -a 256 <request.json>
   python3 scripts/codex_git_guard.py \
     --request <request.json> \
     --request-sha256 <sha256> \
     --dry-run
   python3 scripts/codex_git_guard.py \
     --request <request.json> \
     --request-sha256 <sha256>
   ```

   A changed request fails its content-digest check. A stale HEAD fails both dry-run and execution.
   The explicit-argument form remains supported for small transactions:

   ```sh
   python3 scripts/codex_git_guard.py \
     --expected-head <observed-head> \
     --path <exact-path> \
     --message "<message>"
   ```

   The guard locks the real index, constructs an isolated candidate tree, runs local commit hooks, uses
   expected-old `git update-ref`, and restores the selected paths in the shared index while preserving
   unrelated staging. Stale HEAD, staged-path ambiguity, hook failure, or ref-CAS failure stops the commit.
   The history-mutation prompt remains structural-healthy. Approve it once for the reviewed request;
   do not retain a script-only `python3 scripts/codex_git_guard.py` permission, because future arguments
   can name a different HEAD, message, request, or path set.
6. Validate the operating receipt before reporting completion:

   ```sh
   python3 scripts/validate_codex_operating_receipt.py <receipt.json>
   ```

## Next-release sequence

Before scope lock, run:

```sh
python3 scripts/codex_release_rehearsal.py \
  --operator-packet planning/artifacts/CODEX_V329_RELEASE_SESSION_PACKET_2026-07-31.json \
  --check
```

The rehearsal is read-only. It checks governance bootstrap, canonical wake-up presence, the authoritative
release SOP, Codex initiative/plan surfaces, runtime identity, initiative health, goal coverage, rollback,
and dirty-state disclosure. A PASS means the private pre-lock surfaces resolve; it does not authorize or
execute a release and it does not prove interactive or remote portability.

For a future v3.29 release session, open `handoffs/CODEX_V329_RELEASE_OPERATOR_PACKET.md`. Its nine entry
gates remain `MUST_REDERIVE`; a packet-validation PASS is preparation evidence, not release readiness.
The future session must stop on any packet stop condition, present the current release summary, and obtain
a separate principal GO before release execution.

During a separately authorized release, Codex follows `sops/SOP_release_process.md` by reference with no
client-specific waiver. Every BLOCKING step needs direct output or a recorded L178 waiver. A second Codex
pass is common-mode review unless its independent axis is named.

## Evidence-state boundaries

| Claim | Minimum evidence |
|---|---|
| Dependable local operation | Valid operating receipt plus focused tests |
| Safe exact-scope commit | Guard PASS with expected HEAD and exact created-commit paths |
| Private pre-lock readiness | Rehearsal PASS with release/public mutation false |
| Native skill discovery | Source-owner interactive matrix PASS; explicit fallback is not native |
| Fleet parity | Local interactive and consumer-confirmed remote evidence PASS |
| Release success | Governing release SOP completion; rehearsal alone is insufficient |

## Native v3.29 support bundle and recovery

The v3.29 public payload exposes three low-risk, repository-local skills through Codex's native
`.agents/skills/` discovery surface:

1. `aget-wake-up` — establish governed session identity and readiness.
2. `aget-study-topic` — perform the pre-implementation KB review.
3. `aget-save-state` — checkpoint before interruption and resume from the recorded state.

If native discovery fails, report `explicit-source-fallback`, read the corresponding
`.claude/skills/<name>/SKILL.md`, and preserve its gates. That fallback is recovery, not native-discovery
PASS. `python3 scripts/validate_codex_skill_discovery.py --json` verifies the producer bundle; Gate 4
still requires cold-context discovery, invocation, and recovery on a downstream v3.29 seat.

## Current limits

- The operating support is validated only in this private manager repository on macOS with Codex 0.144.5.
- The Git guard is opt-in and uses POSIX `fcntl`; cross-platform behavior is not established.
- Request-file binding narrows and shortens the reviewed command surface; it does not replace the
  consequential Git authorization gate or make a broad persistent prefix safe.
- Mutation-producing release-observability, version-validator, and wind-down contract tests use
  temporary agent roots. They must not append test artifacts to tracked operational logs or create
  repository session notes.
- Remote-consumer confirmation and public/fleet adoption remain gated. Producer-native discovery passes
  only after the public `.agents/skills/` bundle is present; it does not substitute for Gate 4.
- No global Codex configuration, blanket approval, plugin, remote state, or public repository is changed.
