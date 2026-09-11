# AGET CLI Support Matrix

**Version**: 1.1.0
**Date**: 2026-09-09 (v1.0.0 2026-01-16)
**Status**: ACTIVE
**Implements**: PROJECT_PLAN_cli_independence_validation_v1.0

---

## Overview

AGET is designed to be CLI-agnostic, working with multiple AI coding assistants. This document tracks validation status and support levels for each CLI.

**Validation Date**: 2026-01-16 for the Baseline/Compatible rows below; **2026-09-09** for the
three-level evidence section and the Antigravity row.
**AGET Version**: 3.4.0 at original validation. **The version-tested column is not re-measured here** —
only the rows this cycle touched carry a 2026-09-09 reading.

---

## Support Matrix

| CLI | Vendor | Version Tested | Support Level | Tests | Notes |
|-----|--------|----------------|---------------|-------|-------|
| **Claude Code** | Anthropic | 2.1.9 | **Baseline** | 24/24 | Primary development target |
| **Codex CLI** | OpenAI | 0.77.0 | Compatible | 26/26 | Native AGENTS.md support |
| **Gemini CLI** | Google | 0.23.0 | Compatible | 26/26 | Newest, expect changes — **see the 2026-09-09 re-scope below; individual free access is reported retired and a successor is named** |
| **Antigravity CLI** | Google | 1.107.0 (launcher) | **Experimental** | — | **Announced successor for individual accounts.** Declares a prompt-taking `chat` subcommand; whether it can be driven **non-interactively** is unproven — `chat`'s options are all desktop-window controls. Experimental on three grounds: launcher-only L1, unproven L2, no governed receipt. See the retraction below |
| Cursor | Cursor | - | Experimental | - | Not validated |
| Aider | Open Source | - | Experimental | - | Not validated |
| Windsurf | - | - | Experimental | - | Not validated |

---

## Runtime support evidence — three levels that must not be collapsed *(added 2026-09-09, C-34-18)*

The `Evidence Required` column below is graded by three questions that are answered separately.
Answering the cheap one is routinely mistaken for answering the expensive one, so each is reported
on its own evidence by `scripts/check_runtime_support_evidence.py`:

| Level | Question | What satisfies it | What does NOT |
|---|---|---|---|
| **L1 installed** | does an executable resolve and report a version? | `which` resolves and `--version` exits 0 **for something that is not a desktop launcher** — a path resolving into a macOS `.app` bundle reads `UNKNOWN`, because a launcher's version is not evidence about a terminal agent | Nothing about support. A version string is an observation about a binary on one machine |
| **L2 instructable** | is there a non-interactive instruction surface? | the documented subcommand or flag appears in `--help` | L1. A tool can be installed and offer no way to be driven |
| **L3 governed** | did a bounded governed invocation actually run? | a JSON receipt that **declares the invocation** — `runtime`, `invoked: true`, and a non-empty `outcome` | L2, and a receipt that merely NAMES the runtime. A file saying the runtime was *not* invoked names it too; so does this command's own output |

**L1 does not imply L2; L2 does not imply L3.** A level with no evidence is `UNKNOWN` — never `NO`,
and never promoted to a pass. **L3 is read from a receipt and never produced by the checker**: running
a runtime to make it prove itself is a state-changing act, outside the CAP-CCP read-only boundary.

### Re-scope of the portability target — 2026-09-09, measured at source

`findings/R9_v3.33.0_pre_release_research_2026-08-28.md` Part 3 tabulated *"the declared successor —
1.107.0"*. **That reading is corrected here.** `1.107.0` is the version of an Electron **desktop
launcher**: `agy` resolves through a symlink to
`/Applications/Antigravity.app/Contents/Resources/app/bin/antigravity`. It is not evidence about a
terminal agent.

Measured 2026-09-09 with the checker above:

| Runtime | L1 installed | L2 instructable | L3 governed | Reading |
|---|---|---|---|---|
| Antigravity CLI | **UNKNOWN** — resolves to a DESKTOP LAUNCHER (`1.107.0` is the launcher's version) | **UNKNOWN** — declares a prompt-taking `chat`, but nothing states it runs non-interactively, and `chat`'s options are all window controls | UNKNOWN | announced successor; **all three levels unproven** |
| Gemini CLI | YES 0.59.0 | YES | UNKNOWN | superseded for individual accounts, still instructable |
| Codex CLI | YES 0.153.4 | YES | UNKNOWN | unchanged |

**RETRACTION, 2026-09-09 — this table published a false claim and it is corrected here rather than
quietly edited.** Two successive readings of the Antigravity row were wrong, in opposite directions:

1. It first recorded **L1 = YES** for the launcher, reasoning that the executable resolves and reports
   a version. An independent review then drove a launcher all the way to `SUPPORTED-TARGET`, exit 0,
   through the tool built to stop it — the launcher flag was computed, printed, and never consulted.
   L1 now reads **UNKNOWN** and the flag drives the verdict.
2. It then recorded **L2 = NO**, *"no `exec`/`agent`/`--prompt` subcommand in `--help`"*, and published
   the readings **"not currently instructable at this seat"** and **"less instructable than the runtime
   it supersedes."** **Those statements were false.** `antigravity --help` declares a `Subcommands`
   block whose first entry is `chat — "Pass in a prompt to run in a chat session in the current working
   directory."` The token list was simply wrong, and the checker converted *"my declared tokens did not
   match"* into a **definite NO** about the runtime.

The second error is the instructive one, because it is this document's own thesis failing one level
down. The checker treats an *unlisted* runtime as UNKNOWN "because we have not been told what to look
for" — and then treated a runtime listed with the *wrong* tokens as a demonstrated absence. **An
unmatched token list is an unproven expectation, not evidence about the world.** The checker now parses
the `Subcommands`/`Commands` block the help actually declares, and where declared tokens fail to match
while the help does declare surfaces, it reports **UNKNOWN with those surfaces named** rather than NO.

**Corrected reading, second attempt — and the first correction was also wrong.**

The retraction above fixed a false **NO** and published a false **YES** in its place. Recorded
because the sequence is the finding:

| Reading | Claim | Verdict |
|---|---|---|
| 1st | L2 = NO, "not currently instructable" | **false** — `chat` is declared |
| 2nd | L2 = YES, "`chat` takes a prompt non-interactively" | **false** — declaration is not capability |
| 3rd | **L2 = UNKNOWN** — declared, non-interactivity unproven | holds on the evidence |

`antigravity chat --help` lists exactly six options: `--mode`, `--add-file`, `--maximize`
("Maximize the chat session **view**"), `--reuse-window`, `--new-window`, `--profile`. Every one
drives a desktop window. There is no headless, print, or non-interactive option. Its peers state
theirs outright — `codex exec  Run Codex **non-interactively**`, `gemini -p  Run in
**non-interactive (headless) mode**` — and both earn L2 = YES on that sentence.

**L2 means "exposes a non-interactive instruction surface."** The checker had only ever
established *declaration*, and inferred capability from it. That is `identity is not invocation`
one level further down, and it produced an error in each direction before the distinction was
drawn. The checker now requires an explicit vendor statement of non-interactive operation;
a declared surface without one reads **UNKNOWN with the surface named**.

One narrower correction inside this one: `stdin` was briefly accepted as that evidence, and it is
not. Antigravity's help says *"To read from stdin, append '-' (`ps aux | grep code | antigravity
-`)"* — piping content **into a GUI editor**, which still opens a window. A predicate whose
extension is wider than its subject produces exactly the false YES it was added to prevent.

**Bounded**: the reported retirement narrows to **individual accounts**; enterprise and API-key access
are reported unaffected. No installer, authentication flow, or configuration mutation was performed, and
no pilot is claimed. Re-targeting the portability initiative itself is a separate governed act and is
not performed here.

---

## Support Level Definitions

| Level | Meaning | Evidence Required |
|-------|---------|-------------------|
| **Baseline** | Reference implementation, fully validated | CI + live session + all tests pass |
| **Validated** | Manual validation, all tests pass | VALIDATION_REPORT + live session |
| **Compatible** | Infrastructure tests pass, live session pending | VALIDATION_REPORT (infra only) |
| **Experimental** | Untested, architecture should support | None |
| **Unsupported** | Known incompatibilities | GAP_ANALYSIS documenting blockers |

---

## Validated CLI Details

### Claude Code (Baseline)

| Attribute | Value |
|-----------|-------|
| Vendor | Anthropic |
| Version Tested | 2.1.9 |
| Minimum Supported | 2.0.0 |
| Settings File | CLAUDE.md (symlink to AGENTS.md) |
| Support Level | Baseline |
| Test Results | 24/24 pass |
| Live Session | Validated |

**Validation Report**: `docs/validation/VALIDATION_REPORT_claude_code_v2.1.9.md`

**Notes**:
- Primary development and testing target
- All AGET features designed against Claude Code first
- 200k token context window, handles large AGENTS.md
- Full tool support (Read, Write, Edit, Bash)

---

### Codex CLI (Compatible)

| Attribute | Value |
|-----------|-------|
| Vendor | OpenAI |
| Version Tested | 0.77.0 |
| Minimum Supported | 0.70.0 |
| Settings File | AGENTS.md (native) |
| Support Level | Compatible |
| Test Results | 26/26 pass |
| Live Session | Pending |

**Validation Report**: `docs/validation/VALIDATION_REPORT_codex_cli_v0.77.0.md`

**Notes**:
- Reads AGENTS.md natively (no symlink needed)
- `-y` flag available for automation
- Rapidly evolving (0.x series)
- Live session validation needed for full certification

**Known Gaps**:
- GAP-001: Live session validation pending

---

### Gemini CLI (Compatible)

| Attribute | Value |
|-----------|-------|
| Vendor | Google |
| Version Tested | 0.23.0 |
| Minimum Supported | 0.20.0 |
| Settings File | Unknown (needs validation) |
| Support Level | Compatible |
| Test Results | 26/26 pass |
| Live Session | Pending |

**Validation Report**: `docs/validation/VALIDATION_REPORT_gemini_cli_v0.23.0.md`

**Notes**:
- Newest of the three CLIs
- Uses `@filename` syntax for file references
- Settings file compatibility unknown
- Expect rapid changes in 0.x series

**Known Gaps**:
- GAP-001: Settings file compatibility unknown
- GAP-002: Live session validation pending
- GAP-003: File reference syntax differs

---

## Test Categories

All CLI validations cover these test categories:

| ID | Category | Description |
|----|----------|-------------|
| TC-001 | Settings Read | CLI reads AGENTS.md and follows instructions |
| TC-002 | Wake Protocol | wake_up.py executes correctly |
| TC-003 | Wind Protocol | wind_down.py executes correctly |
| TC-004 | Script Execution | .aget/patterns/ scripts work |
| TC-005 | L-doc Creation | Can create/update L-docs |
| TC-006 | File Operations | Read/write/edit per CLI tool model |

---

## Version Tracking

CLI agents evolve rapidly. AGET maintains version tracking in:
- `tests/cli_verification/cli_versions.json`

**Minimum Supported Versions**:

| CLI | Minimum Version | Rationale |
|-----|-----------------|-----------|
| Claude Code | 2.0.0 | Major version stability |
| Codex CLI | 0.70.0 | Feature completeness |
| Gemini CLI | 0.20.0 | Basic functionality |

**Re-validation Cadence**: Major version updates or quarterly review.

---

## Using AGET with Different CLIs

### Claude Code

```bash
# AGENTS.md is read via CLAUDE.md symlink
ln -s AGENTS.md CLAUDE.md  # If not already present

# Standard invocation
claude "wake up"
```

### Codex CLI

```bash
# AGENTS.md is read natively
codex "wake up"

# With automation flag
codex -y "wake up"
```

### Gemini CLI

```bash
# Settings file may need configuration
gemini "wake up"

# File references use @ syntax
gemini "read @AGENTS.md"
```

---

## Shell Orchestration

AGET provides shell integration for CLI-agnostic invocation (see L452):

```zsh
# ~/.aget/aget.zsh
export AGET_CLI=claude  # Default CLI

aget() {
    local dir="$1"; shift
    cd "$dir" || return 1
    $AGET_CLI "Wake up. $*"
}

# Override per-invocation
AGET_CLI=codex aget ~/my-agent "fix the bug"
```

---

## Contributing Validation

To validate a new CLI:

1. Create `test_<cli_name>.py` following existing patterns
2. Add CLI to `cli_versions.json`
3. Run validation tests
4. Generate VALIDATION_REPORT
5. Submit PR to update this matrix

---

## References

- PROJECT_PLAN_cli_independence_validation_v1.0
- L452: Shell Orchestration Pattern
- CLI_SETTINGS_STANDARD.md
- AGET_FRAMEWORK_SPEC.md

---

*AGET CLI Support Matrix - Prove before you claim*
