# Corrections since tag — v3.33.1

**Contract** (SOP_release_process v1.57 Phase 3.6 Rule 2; gh#1882): this file is the ONE
write target per post-tag fix. Guidance surfaces (release body, RELEASE_HANDOFF,
REMOTE_MIGRATION_MESSAGE, SUPERVISOR_PROMPT) point here and never duplicate the enumeration.
Consumers pulling AT THE TAG: apply every row below on top of the tag payload.

**Tag**: v3.33.1 (`8fe9c9884b597d7dfba86e754dc11f3dc052d8bb`) · **Surface opened**: 2026-09-05 · **Rows are append-only.**

> **Why this file opens with defects rather than fix SHAs.** Rows 1–3 were found by *receivers*
> mid-migration, not by a post-tag commit here. The tag is immutable and is not repaired in place, so
> the correction surface is where a consumer learns what the tag gets wrong before applying it. Fix SHAs
> land in the SHA column as they merge.

| # | SHA | Date | Artifact(s) | What | Why tag copy insufficient | Consumer action |
|---|-----|------|-------------|------|---------------------------|-----------------|
| 1 | *pending — PR #94* | 2026-09-05 | `scripts/**`, `verification/**`, `templates/**` | **188 `F541`** (f-string with no placeholder) at the tag; **68 in `scripts/`**, the surface a receiver installs. 152 are auto-fixable. | A receiver whose pre-commit lint set includes `F541` **refuses the payload**. One seat applied the tagged payload and fully reverted; its migration plan records the disposition as owner *"framework for a corrected release tag."* Fixing the single occurrence that seat reached first does not clear the class. | If your lint gate blocks on `F541`: run `ruff check --select F541 --fix` over the installed paths after applying, or install with lint suspended and sweep before your first commit. **Not informational** — this refuses migrations. |
| 2 | *pending* | 2026-09-05 | `DEPLOYMENT_SPEC_v3.33.1.yaml`, `handoffs/RELEASE_HANDOFF_v3.33.1.md`, `handoffs/REMOTE_MIGRATION_MESSAGE_v3.33.1.md` | **Two incompatible terminal enums ship at one tag.** `DEPLOYMENT_SPEC_v3.33.1.yaml` declares `receiver_acceptance.terminals: ["ACCEPTED","REJECTED","CANNOT-RUN"]`. Both handoff surfaces require the completion response to carry one of `ACQUIRED \| INTEGRITY_VERIFIED \| INSTALLED \| BEHAVIOUR_VERIFIED \| ACCEPTED \| HOLD \| ROLLED_BACK`. **Overlap is `ACCEPTED` and nothing else.** | A receiver that closes on `CANNOT-RUN` (the spec's terminal, and the correct one when template repos are absent) cannot express that in the completion response. A receiver that reports `HOLD` — the state 19 seats are actually in — is reporting something the governing spec does not define as a terminal. The two surfaces cannot both be satisfied. | **Close on the deployment spec's three terminals** (`receiver_acceptance.terminals` is the normative field). Treat the handoff's seven values as a **progress vocabulary**, not terminals, and say which you used. Reconciliation rides the next tag. |
| 3 | *pending* | 2026-09-05 | `DEPLOYMENT_SPEC_v3.33.1.yaml` | **All three `mandatory_changes` are producer-side.** `HANDOFF-3331-01` targets `handoffs/`, `HISTORY-3331-02` targets `docs/VERSION_HISTORY.md`, `DOCUMENT-TEMPLATE-3331-03` targets `../template-document-processor-AGET`. None names a receiver-instance path. | A receiver resolving `mandatory_changes` by running each row's `detection` clause passes **all three vacuously** — two by producing artifacts it does not own, one by a template repo it may not have on disk. A green mandatory-changes result therefore proves nothing about the receiver. | Resolve receiver obligations from **`receiver_acceptance`** (acquire / integrity / behavioral), never from `mandatory_changes`. If a `detection` clause passes because its subject is absent, record `CANNOT-RUN`, not `ACCEPTED`. |

---

## Provenance

Rows 1–3 were derived at the tag, not from working trees: `git archive v3.33.1` into a clean tree then
`ruff check --select F541` (row 1); `git show v3.33.1:<path>` across the three contract surfaces
(rows 2–3). Row 1's receiver evidence is the fleet v3.33.1 migration plan's Gate 4 disposition for the
seat that reverted.

Row 2 also explains a reporting artefact visible in that migration's outcome ledger: the split
*"8 accepted, 19 held at release, 4 held below release"* uses `HOLD`, which row 2 shows is not a terminal
in the specification that governs closure. The ledger is not wrong; the contract is under-specified.

*Surface opened 2026-09-05 after four releases without one — `CORRECTIONS_v3.30`, `v3.31`, `v3.32` and
`v3.33.0` were never created. The checker (`check_corrections_surface.py`) reports `PASS` when no
post-tag commit touches a coupled artifact, so a lapsed surface and a clean one are indistinguishable
in its output.*
