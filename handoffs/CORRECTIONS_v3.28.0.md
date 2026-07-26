# CORRECTIONS — v3.28.0

Post-tag corrections for v3.28.0. **This is the single surface** for fixes discovered after the tag; other
artifacts point here rather than being edited (gh#1834 rule 2).

Read from `origin/main`, not the tag.

---

## Row 1 — `DEPLOYMENT_SPEC_v3.28.0.yaml`: 5 of 6 M-row detections verify EXISTENCE, not behaviour

**Found**: 2026-07-26, post-tag, by this seat auditing its own release against the cycle's root-cause finding.

**What is wrong**: every mandatory M-row detection is a `test -f` / `grep -q` / `jq -e` string check. The
sharpest case is **`M-3.28-4`**, whose description reads *"Detection checks the guard **CAN** write it"*
while the detection is:

```
grep -q 'control_firings.jsonl' .claude/hooks/release_gate_firing_guard.sh
```

That greps a file for a **string**. It proves a filename appears in a script. It does **not** prove a single
byte is ever written — and this is the row carrying the entire evidence path for the delivery Goal's leg 3.

**A seat can pass every mandatory row of this spec while shipping a guard that never writes anything.**

**Impact on your migration**: low. The payload itself is correct — the guard *does* write the ledger, verified
at the producing seat and by the smoke probes in `REMOTE_MIGRATION_MESSAGE_v3.28.0.md` (probe 5 returns
`hook_event: PreToolUse`). What is wrong is the **detection**, which would not have caught it had it been
broken.

**What to do**: run **probe 5** rather than relying on `M-3.28-4`. The probe verifies behaviour; the M-row
verifies a string.

**Why this is disclosed rather than silently patched**: the spec is published. v3.27.0 shipped
*"tag-payload post-tag divergence undisclosed in the release body"* by its own quality score, and editing a
published artifact without a correction row is that same defect. A corrected spec ships in v3.29.

**Root**: this is the cycle's own root-cause finding — an edge checked by *name* is a node with extra steps
— reproduced in the release's own deployment contract, written four hours after the finding was recorded.

---

## Row 2 — GitHub release body was initially published in the wrong format

**Found**: 2026-07-26, principal-caught, within an hour of the tag.

The release body was first published as the full deep release notes rather than a conforming release body:
`release_body_gates` reported `conformant=False` (missing `What's New` and `Compatibility`) plus 2 voice
flags. **Corrected the same session**; the live body now passes structure, value and voice gates.

No action required. Recorded because the release body is a consumed surface and its history should be visible.
