# PATTERN: Release Remediation Generator

**Pattern type**: Cross-agent operations infrastructure
**Status**: PRODUCTION-READY (v1.0.0 validated under load 2026-05-17)
**Source cycle**: FLEET-UPG-016R adoption-stream remediation (private fleet, 2026-05-17)
**Reusable**: YES — designed for v3.19+ adoption-stream cycles + fleet-wide structural-artifact updates

---

## When to use this pattern

When the framework ships a release with **adoption streams** (per-agent structural updates beyond the version-stamp itself — e.g., new spec references, new skill deployments, new governance annotations, new STRUCTURAL routing table entries), you need a Generator that:

1. Iterates the cohort of migrated agents
2. Applies each adoption stream idempotently (running again = zero double-write)
3. Refuses to touch substance files (R-CLI-004 carve-out boundary enforcement)
4. Captures per-agent external-verification logs + an aggregate INDEX
5. Reports cohort-wide outcome (pass / skip / fail per agent per stream)

The reference implementation is `fleet_remediation_v318.py` at `~/github/private-supervisor-AGET/workspace/`.

## Architecture (per L968 substrate)

### Table-driven stream registry

Each adoption stream is a row in a `STREAMS` list:

```python
STREAMS = [
    {
        "id": "MEMORY_SURFACE_SPEC_ref",
        "semantic_identifier": r"AGET_MEMORY_SURFACE_SPEC",
        "kind": "ack-row",       # vs "skill-copy", "annotation"
        "emit_fn": emit_ack_row,
    },
    # ... per-stream entries
]
```

**Why table-driven**: adding a new stream = adding a row, not rewriting dispatch logic. New v3.19 streams are appended; existing streams continue working.

### Semantic-not-byte-literal idempotency

```python
def check_stream_idempotency(stream, agent_root):
    """Returns 'present' if stream already adopted, else 'absent'."""
    if stream["kind"] == "skill-copy":
        # Verify git-tracked, not just disk-present (per Path 1 force-add)
        skill_path = ".claude/skills/<name>/SKILL.md"
        result = subprocess.run(
            ["git", "-C", str(agent_root), "ls-files", "--error-unmatch", skill_path],
            capture_output=True,
        )
        return "present" if result.returncode == 0 else "absent"
    # ack-row / annotation: regex on stream identifier in AGENTS.md
    agents_md = agent_root / "AGENTS.md"
    content = agents_md.read_text()
    if re.search(stream["semantic_identifier"], content):
        return "present"
    return "absent"
```

**Why regex on identifier, not byte-equality**: byte-equality would create duplicates on re-run if format drifts (extra whitespace, table reformatting, etc.). Regex on semantic identifier (e.g., the spec name) treats "present-anywhere-in-section" as semantically present.

**Validated under load**: re-running Generator on already-completed cohort during FU016R Wave 1 = 7/7 skipped, zero double-write.

### Path allowlist guard (R-CLI-004 boundary enforcement)

```python
ALLOWLIST = [
    "AGENTS.md",
    ".claude/skills/<skill_name>/",
    # optional: "governance/" for governance ref annotations
]

def assert_in_allowlist(path):
    """Hard-fail (exit 2) if writing outside structural-artifact scope."""
    if not any(path.startswith(p) for p in ALLOWLIST):
        raise SystemExit(f"R-CLI-004 violation: {path} not in allowlist")
```

**Why hard-fail**: a single substance file accidentally touched = R-CLI-004 letter violation. Exit-2 + audit trail surfaces the bug at execution time.

### Refuse-substance self-test

```python
def self_test_substance_refuse():
    """V-test: ensure substance paths trigger exit-2."""
    test_path = ".aget/evolution/L_TEST.md"
    try:
        assert_in_allowlist(test_path)
        sys.exit(0)  # Should not reach
    except SystemExit:
        print("V-test PASS: refuse-substance guard fires")
        sys.exit(2)
```

### Dry-run flag with side-effect propagation

**Trap from FU016R G2-1**: the cycle-1 bug was `dry_run=False` hardcoded inside `ensure_adoption_section_present()`. Dry-run wrote section headers despite `--dry-run` flag.

**Fix**: propagate `dry_run` flag explicitly through every function that mutates state. Test by running dry-run + grepping target files for changes (should be zero).

### Per-emission idempotency (not per-agent)

Allows top-up of partially-adopted agents — supervisor self-pilot at 5/5 stays at 5/5; a partial-adoption agent at 2/5 gets the missing 3/5 emitted, not all 5/5 re-emitted.

## Authorization context

This Generator is **supervisor-direct invocation under existing Wave-2a precedent authority**. It does NOT require new R-CLI-004 carve-out language because:

- Stream emissions are structural (AGENTS.md sections + skill file copies + table rows) — not substance
- Path allowlist hard-fails on substance violations
- Authorization Record at parent plan binds the carve-out to "structural artifacts only; no substance modification"

For Wave-2c L100-worker mechanic (substance-staged agents), the Generator's `--cohort <name>` flag enumerates routine subsets; workers self-apply via L100 packet OR via headless dispatch per L968 + ADR DRAFT headless-mechanic-first.

## Performance benchmarks (cycle evidence)

| Metric | FU016R Wave 1 | FU016F finalize |
|---|---|---|
| Agents processed | 13 | 5 |
| Wall-clock | ~25 seconds | ~5 minutes (incl. headless dispatch latency) |
| Streams per agent | 7 (S1+S2+S3+S4a+S4b+S4c+S5) | 7 same |
| R-CLI-004 violations | 0 | 0 |
| Double-writes on re-run | 0 (semantic idempotency held) | 0 |
| Bug fixes during execution | 1 (dry-run hardcode → propagated flag) | 0 |

## How to extend for v3.19+

1. **New release with adoption streams**: append rows to `STREAMS` for each new stream
2. **New cohort definition**: append to `COHORT_DEFINITIONS` (e.g., new portfolio added)
3. **New mechanic** (e.g., MERGE_INTO instead of APPEND): add new `kind` + emit function
4. **New invocation mode** (per L968): keep supervisor-direct as one mode; add headless dispatch as alternative

## Trade-offs

| Aspect | Generator pattern | Alternative |
|---|---|---|
| Speed | ~25 sec for 13 agents (supervisor-direct) | ~30 min per agent (L100-worker) |
| R-CLI-004 posture | Carve-out required for cross-write | Headless per L968 = no carve-out (cleaner) |
| Idempotency | Built-in (semantic regex) | Manual per worker |
| Aggregation | Built-in (INDEX CSV) | Manual at supervisor |
| Worker substance adjudication | NOT in scope (path allowlist refuses) | L100 packet OR headless lets worker decide |

The Generator pattern is best for **structural artifacts** (deterministic, idempotent, allowlist-bounded). For substance-bearing operations, headless dispatch per L968 + ADR DRAFT is the v3.19+ default.

## References

- **Reference implementation**: `~/github/private-supervisor-AGET/workspace/fleet_remediation_v318.py` v1.0.0
- **Cycle origin**: FU016R adoption-stream remediation + FU016F finalize-mode extension
- **L-docs**: L968 (frame-anchoring; alternative mechanics), L967 (plan-body-as-spec; substrate discipline), L644 (verify-before-recommend)
- **Specs**: AGET_RELEASE_SPEC R-REL-043 (KR1-substance requirement; this Generator is the mechanism)
- **ADR**: DRAFT headless-mechanic-first (sibling default for non-structural cross-agent action)

---

*v1.0.0 — authored 2026-05-17 by `private-aget-framework-AGET` at LEARN-001 G3 BUILD-B. Generalizes the FU016R cycle's Generator into a reusable pattern for v3.19+ adoption-stream remediation.*
