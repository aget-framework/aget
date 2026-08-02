# CORRECTIONS — v3.29.0

**Status**: ACTIVE

This is the single public disclosure surface for defects found after the immutable v3.29.0 tags were
published. Tags are not moved or replaced. The public `main` branch and mutable GitHub Release records
carry the fix-forwards below.

| # | Surface at `v3.29.0` | Correction on `main` / live service | Consumer action |
|---:|---|---|---|
| 1 | All 14 GitHub Release bodies reused the 62-line deep release notes and failed the canonical 3-section, 12–25-line body contract. | Bodies replaced with the validated `release-notes/v3.29.0_release_body.md` source; all 14 live validators PASS. | No tag change. Read the GitHub Release body for the concise overview and the tag-pinned release notes for depth. |
| 2 | `docs/VERSION_HISTORY.md` remained current only through v3.27.0. | Public-core `main` commit `53468ea` adds v3.28.0 and v3.29.0 current/timeline entries. | Use `main` for the current timeline; historical tag payload remains unchanged. |
| 3 | `handoffs/RELEASE_HANDOFF_v3.29.0.md` contained external migration content but omitted the required `Context for External Fleets` heading. | Public-core `main` adds the explicit section and points back to this corrections surface. | External fleets should read the corrected handoff on `main` before migration. |

These corrections do not establish downstream receipt or behavior. Gate 4 remains separately authorized
and must prove the receiving version plus cold-context Codex discovery, invocation, and recovery.
